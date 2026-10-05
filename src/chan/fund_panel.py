"""A fund's year-end members, mapped to Alpha Vantage tickers and checked against its filings.

Example 7.6 ranks an index as it stood at each year-end, which needs a price
series for companies that later left it. :mod:`chan.fund_holdings` reads which
companies a fund held from its SEC filings. This module joins those members to
Alpha Vantage's daily closes in the owner's archive, and says how many of them
a panel built that way covers.
[Issue 332](https://github.com/l3a0/quantitative-trading/issues/332) is the
scope, for IJR and the S&P 600, and
[issue 373](https://github.com/l3a0/quantitative-trading/issues/373) reuses
every function here for IVV, so each takes the fund, its members file and its
cross-section as arguments. :mod:`chan.sp600_panel` binds IJR's.

The record is one members file per fund, beside the holdings files, with the
columns :data:`COLUMNS`, one row per member and report date.

1. ``report_date`` and ``row`` name the holding: ``row`` is its position among
   the holdings file's data rows, counting from 1, so a row the committed list
   of non-stock rows drops keeps its number.
2. ``ticker``, ``source`` and ``note`` are the mapping. ``source`` says which of
   :data:`SOURCES` answered, and ``note`` names a hand row's evidence.
3. ``check``, ``gap`` and ``exit`` are what :func:`check_members` computes from
   the archive. ``gap`` is the price miss in cents on a ``price`` row. ``exit``
   says whether a passing series holds the close on the last trading day of
   the following January.

The mapping is research rather than code. Its lookups ran through a connector
in the session that built the file, so they cannot be rerun here. What holds a
ticker is the check, which compares the series' raw close times the filing's
share count with the filing's value. :func:`carry_back` is the one mapping step
that is code: a company is resolved at the latest year-end it is a member,
because Alpha Vantage files a company under its last ticker, and the ticker is
carried back along :func:`chan.fund_holdings.link`.

The report reads only committed tables, so it runs anywhere. The check needs
the archive.
"""

from __future__ import annotations

import csv
import io
from collections import Counter
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from decimal import Decimal
from pathlib import Path

import pandas as pd

from chan.fund_holdings import (
    FILINGS_DIR,
    Filing,
    Fund,
    Holding,
    holdings_path,
    link,
    members,
    place,
    read_holdings,
)
from chan.matlab_helpers import round_half_away
from chan.vintage import SYMBOL_PATTERN

#: The members file's name inside a fund's directory of holdings files.
MEMBERS_NAME = "members.csv"

#: The members file's columns, in order.
COLUMNS = ("report_date", "row", "ticker", "source", "note", "check", "gap", "exit")

#: Where a ticker came from, then ``none`` where nothing resolved it. Issue
#: 332 ordered them as written. Its build tried Alpha Vantage's listings,
#: recorded as ``filing`` or ``name``, before the CUSIP lookup, because the
#: lookup's connector answered about five requests a minute.
SOURCES = ("cusip", "filing", "link", "name", "hand", "none")

#: What the check says about one member at one year-end.
CHECKS = ("pass", "price", "no-row", "no-series", "unmapped")

#: Whether a passing series holds its January exit close. Empty on any other row.
EXITS = ("close", "stop", "")

#: The forms that print a schedule in HTML, with whole dollars and whole
#: shares: the N-Q, the two shareholder reports, and IVV's one standalone
#: NPORT-EX for 2019-06-30.
WHOLE_UNIT_FORMS = ("N-Q", "N-CSR", "N-CSRS", "NPORT-EX")

#: The forms that print N-PORT's XML, with cents and shares to eight decimals.
CENT_FORMS = ("NPORT-P", "NPORT-P/A")

#: Half the unit each form reports a value in. An HTML schedule prints whole
#: dollars and N-PORT prints cents.
HALF_UNIT = {
    **{form: Decimal("0.5") for form in WHOLE_UNIT_FORMS},
    **{form: Decimal("0.005") for form in CENT_FORMS},
}

#: Half the unit each form reports a share count in. An HTML schedule prints whole shares,
#: so a value computed on a fractional holding can sit up to half a share's
#: price from the close times the printed count. Measured on 2010-12-31, Maidenform
#: Brands prints 325,785 shares valued at $7,743,910, and 325,785 at the
#: $23.77 close is $7,743,909.45. N-PORT prints the balance to eight decimals,
#: so nothing is added there.
HALF_SHARE = {
    **{form: Decimal("0.5") for form in WHOLE_UNIT_FORMS},
    **{form: Decimal(0) for form in CENT_FORMS},
}


class PanelRefused(Exception):
    """The members file or the check stopped rather than produce a panel nobody can trust.

    The message is one line, because a command prints it as the whole report.
    """


@dataclass(frozen=True)
class MemberRow:
    """One line of a members file."""

    report_date: str
    row: int
    ticker: str
    source: str
    note: str = ""
    check: str = ""
    gap: str = ""
    exit: str = ""

    @property
    def key(self) -> tuple[str, int]:
        return self.report_date, self.row


Key = tuple[str, int]


# --- The record --------------------------------------------------------------


def members_path(fund: Fund, filings_dir: Path | None = None) -> Path:
    """Where a fund's members file sits, beside its holdings files."""
    directory = FILINGS_DIR if filings_dir is None else filings_dir
    return directory / fund.symbol.lower() / MEMBERS_NAME


def read_members(path: Path) -> tuple[MemberRow, ...]:
    """A members file's rows, refusing a column, source, check or exit it does not allow."""
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != COLUMNS:
            raise PanelRefused(f"{path} has columns {reader.fieldnames}, not {list(COLUMNS)}")
        rows = []
        for number, line in enumerate(reader, start=2):
            if not line["row"].isdigit():
                raise PanelRefused(f"{path} line {number}: row {line['row']!r} is not a number")
            row = MemberRow(**{**line, "row": int(line["row"])})
            problem = _malformed(row)
            if problem:
                raise PanelRefused(f"{path} line {number}: {problem}")
            rows.append(row)
    # Counted once rather than with list.count per row, which took five
    # seconds on IJR's 11,334 rows.
    repeated = sorted(key for key, seen in Counter(row.key for row in rows).items() if seen > 1)
    if repeated:
        raise PanelRefused(f"{path} names {repeated[0]} more than once")
    return tuple(rows)


def _malformed(row: MemberRow) -> str | None:
    if row.source not in SOURCES:
        return f"source {row.source!r} is not one of {', '.join(SOURCES)}"
    if (row.source == "none") != (row.ticker == ""):
        return "a ticker is empty exactly when the source is none"
    if row.ticker and not SYMBOL_PATTERN.fullmatch(row.ticker):
        return f"ticker {row.ticker!r} is not a symbol as chan.vintage.SYMBOL_PATTERN writes one"
    if row.check and row.check not in CHECKS:
        return f"check {row.check!r} is not one of {', '.join(CHECKS)}"
    if row.exit not in EXITS or (row.exit != "") != (row.check == "pass"):
        return "exit is close or stop on a pass row and empty on any other"
    if (row.gap != "") != (row.check == "price"):
        return "gap is given on a price row and nowhere else"
    return None


def require_panel(
    fund: Fund,
    rows: Sequence[MemberRow],
    filings_dir: Path | None = None,
    *,
    whole_first: bool = False,
) -> None:
    """A :class:`PanelRefused` unless the rows name every row of the panel and nothing else.

    A file missing a member would report a smaller year-end without saying so,
    and one naming a row no filing holds would fail later as a ``KeyError``.
    ``whole_first`` is :func:`panel_keys`'s.
    """
    wanted = set(panel_keys(fund, filings_dir, whole_first=whole_first))
    held = {row.key for row in rows}
    if held != wanted:
        stray, absent = sorted(held - wanted), sorted(wanted - held)
        raise PanelRefused(
            f"the members file names {len(stray)} rows the filings do not hold and lacks "
            f"{len(absent)} they do, the first {(stray or absent)[0]}"
        )


def serialize_members(rows: Iterable[MemberRow]) -> bytes:
    """A members file's bytes, sorted by report date then row, LF endings."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(COLUMNS)
    for row in sorted(rows, key=lambda row: row.key):
        writer.writerow([getattr(row, column) for column in COLUMNS])
    return buffer.getvalue().encode("utf-8")


def alpha_vantage_symbol(ticker: str) -> str:
    """A ticker as Alpha Vantage writes it: a share class after a hyphen.

    The filing writes Moog's class A as ``MOG/A`` and Massive as ``MOG.A``, and
    Alpha Vantage files it as ``MOG-A``.
    """
    return ticker.strip().upper().replace("/", "-").replace(".", "-")


# --- Members and the links between filings -----------------------------------


def listed(fund: Fund) -> tuple[Filing, ...]:
    """The fund's filings that hold a full schedule, in order.

    A filing the list skips has no holdings file. IVV's 2013-09-30 shareholder
    report prints only a summary, so every step here passes over it, and the
    filing before it links straight to the filing after.
    """
    return tuple(filing for filing in fund.filings if not filing.skipped)


def numbered_members(
    fund: Fund, report_date: str, filings_dir: Path | None = None
) -> list[tuple[int, Holding]]:
    """One filing's members, each with its row number in the holdings file."""
    filing = next(filing for filing in fund.filings if filing.report_date == report_date)
    every = read_holdings(holdings_path(fund, filing, filings_dir))
    kept = members(fund, filing, filings_dir)
    numbered = []
    at = 0
    for holding in kept:
        while every[at] != holding:
            at += 1
        numbered.append((at + 1, holding))
        at += 1
    return numbered


def previous_rows(fund: Fund, filings_dir: Path | None = None) -> dict[Key, Key]:
    """Each member linked to the filing before, mapped to the row it links to."""
    dates = [filing.report_date for filing in listed(fund)]
    numbered = {date: numbered_members(fund, date, filings_dir) for date in dates}
    links: dict[Key, Key] = {}
    for earlier, later in zip(dates, dates[1:], strict=False):
        before = numbered[earlier]
        position = {id(holding): row for row, holding in before}
        pairs = link([holding for _, holding in numbered[later]], [h for _, h in before])
        for (row, _), (paired, _) in zip(numbered[later], pairs, strict=True):
            if paired is not None:
                links[(later, row)] = (earlier, position[id(paired)])
    return links


def panel_keys(
    fund: Fund, filings_dir: Path | None = None, *, whole_first: bool = False
) -> list[Key]:
    """Every row a members file holds.

    Each member of every filing after the first, and each member of the first
    that links to one in the second, since its close is what ranks that member
    at the second year-end. A panel whose first filing also sets months it
    trades in passes ``whole_first``, and then every member of the first is a
    row too. IVV's 2008-12-31 schedule sets December 2008 to February 2009.
    """
    dates = [filing.report_date for filing in listed(fund)]
    linked_into = set(previous_rows(fund, filings_dir).values())
    keys = [
        (dates[0], row)
        for row, _ in numbered_members(fund, dates[0], filings_dir)
        if whole_first or (dates[0], row) in linked_into
    ]
    for date in dates[1:]:
        keys.extend((date, row) for row, _ in numbered_members(fund, date, filings_dir))
    return keys


def carry_back(
    fund: Fund,
    resolved: Mapping[Key, MemberRow],
    filings_dir: Path | None = None,
    *,
    whole_first: bool = False,
) -> list[MemberRow]:
    """Every row of the panel, each resolved row as given and the rest carried along links.

    A row with no resolution of its own takes the ticker of the row in the
    next filing that links to it, with source ``link``, walking forward until
    a resolved row is met. A row reaching no resolution is unmapped. A
    resolution for a row outside the panel is refused, because it would be a
    mapping nothing reads. ``whole_first`` is :func:`panel_keys`'s.
    """
    keys = panel_keys(fund, filings_dir, whole_first=whole_first)
    outside = sorted(set(resolved) - set(keys))
    if outside:
        raise PanelRefused(f"a resolution names {outside[0]}, which is not a row of the panel")
    forward = {before: after for after, before in previous_rows(fund, filings_dir).items()}
    rows = []
    for key in keys:
        if key in resolved:
            rows.append(resolved[key])
            continue
        step = forward.get(key)
        while step is not None and step not in resolved:
            step = forward.get(step)
        if step is None or resolved[step].source == "none":
            rows.append(MemberRow(key[0], key[1], "", "none"))
        else:
            rows.append(MemberRow(key[0], key[1], resolved[step].ticker, "link"))
    return rows


# --- The calendar ------------------------------------------------------------


def price_date(calendar: pd.DatetimeIndex, report_date: str) -> pd.Timestamp:
    """The last trading day on or before a report date."""
    on_or_before = calendar[calendar <= pd.Timestamp(report_date)]
    if len(on_or_before) == 0:
        raise PanelRefused(f"the calendar holds no trading day on or before {report_date}")
    return on_or_before[-1]


def exit_date(calendar: pd.DatetimeIndex, report_date: str) -> pd.Timestamp:
    """The last trading day of the January after a report date's year."""
    year = pd.Timestamp(report_date).year + 1
    january = calendar[(calendar.year == year) & (calendar.month == 1)]
    if len(january) == 0 or calendar[-1] < pd.Timestamp(f"{year}-02-01"):
        raise PanelRefused(f"the calendar does not reach the end of January {year}")
    return january[-1]


# --- The check ---------------------------------------------------------------


def check_members(
    fund: Fund,
    rows: Sequence[MemberRow],
    closes: pd.DataFrame,
    calendar: pd.DatetimeIndex,
    filings_dir: Path | None = None,
    *,
    exit_on: Callable[[pd.DatetimeIndex, str], pd.Timestamp] = exit_date,
) -> list[MemberRow]:
    """Each row with its check, gap and exit computed from raw closes.

    ``closes`` is a date-by-symbol frame of raw closes, holding a column for
    every ticker the archive records and none for one it does not. A row
    passes when its close on the price date times the filing's shares is
    within half the filing's value unit of the filing's value, plus half a
    share at that close where the form prints whole shares.

    ``exit_on`` gives the day whose close a passing row's ``exit`` asks about,
    from the calendar and the report date. It defaults to :func:`exit_date`,
    the January a year-end panel sells in. A panel that holds for a month
    passes its own.

    Two members passing on one ticker at one year-end is refused, naming both,
    because one series cannot be two companies' prices. Two failing on one
    ticker stand, since that is a reused ticker caught by the check.
    """
    holdings = {
        filing.report_date: dict(numbered_members(fund, filing.report_date, filings_dir))
        for filing in listed(fund)
    }
    forms = {filing.report_date: filing.form for filing in listed(fund)}
    checked = []
    for row in rows:
        holding = holdings[row.report_date][row.row]
        checked.append(_check_one(row, holding, forms[row.report_date], closes, calendar, exit_on))
    passing: dict[tuple[str, str], MemberRow] = {}
    for row in checked:
        if row.check != "pass":
            continue
        twin = passing.setdefault((row.report_date, row.ticker), row)
        if twin is not row:
            raise PanelRefused(
                f"{row.report_date}: rows {twin.row} and {row.row} both pass on {row.ticker}, "
                f"so one of them is mapped to another company's series"
            )
    return checked


def _check_one(
    row: MemberRow,
    holding: Holding,
    form: str,
    closes: pd.DataFrame,
    calendar: pd.DatetimeIndex,
    exit_on: Callable[[pd.DatetimeIndex, str], pd.Timestamp],
) -> MemberRow:
    blank = replace(row, check="", gap="", exit="")
    if not row.ticker:
        return replace(blank, check="unmapped")
    if row.ticker not in closes.columns:
        return replace(blank, check="no-series")
    series = closes[row.ticker]
    on = price_date(calendar, row.report_date)
    close = series.get(on)
    if close is None or pd.isna(close):
        return replace(blank, check="no-row")
    price = Decimal(repr(float(close)))
    shares, value = Decimal(holding.shares), Decimal(holding.value)
    if shares <= 0 or value <= 0:
        # Any close times no shares is no value, so the check would pass every
        # ticker. No committed member holds none.
        raise PanelRefused(
            f"{row.report_date} row {row.row} holds {holding.shares} shares valued at "
            f"{holding.value}, so no close can be checked against it"
        )
    if abs(price * shares - value) > HALF_UNIT[form] + price * HALF_SHARE[form]:
        gap = ((price - value / shares) * 100).quantize(Decimal("0.01"))
        return replace(blank, check="price", gap=str(gap))
    after = series.get(exit_on(calendar, row.report_date))
    held = after is not None and not pd.isna(after)
    return replace(blank, check="pass", exit="close" if held else "stop")


# --- Coverage and the threat rule ---------------------------------------------


@dataclass(frozen=True)
class Coverage:
    """What one year-end's members file says about the panel there.

    ``misses`` counts the members not covered by reason: a check other than
    ``pass``, or ``rank`` for a linked member whose previous row did not pass,
    since its rank close is unverified. ``stops`` counts covered members whose
    series ends inside the following January, which the run keeps.
    ``within_a_cent`` counts the ``price`` misses whose close is a cent or less
    from the filing's price, which says how many misses are a disagreement
    about the close rather than a different company.
    """

    report_date: str
    members: int
    covered: int
    misses: dict[str, int]
    stops: int
    missing: tuple[Key, ...]
    within_a_cent: int = 0


def coverage(
    fund: Fund, rows: Sequence[MemberRow], filings_dir: Path | None = None
) -> list[Coverage]:
    """Each year-end after the first, with its covered count, misses and January stops.

    A member is covered when its own row passes and, where it links to the
    filing before, that row passed too.
    """
    by_key = {row.key: row for row in rows}
    previous = previous_rows(fund, filings_dir)
    report = []
    for filing in listed(fund)[1:]:
        date = filing.report_date
        mine = [row for row in rows if row.report_date == date]
        misses: Counter[str] = Counter()
        missing = []
        stops = 0
        near = 0
        for row in mine:
            if not row.check:
                raise PanelRefused(f"{date} row {row.row} has not been checked")
            reason = row.check if row.check != "pass" else None
            near += row.check == "price" and abs(Decimal(row.gap)) <= 1
            before = previous.get(row.key)
            if reason is None and before is not None and by_key[before].check != "pass":
                reason = "rank"
            if reason is None:
                stops += row.exit == "stop"
                continue
            misses[reason] += 1
            missing.append(row.key)
        report.append(
            Coverage(
                date,
                len(mine),
                len(mine) - len(missing),
                dict(misses),
                stops,
                tuple(missing),
                near,
            )
        )
    return report


def threats(
    returns: Mapping[Key, Decimal | None], missing: Iterable[Key], universe: int
) -> list[Key]:
    """The missing members that could change a tenth, by issue 329's rule.

    ``returns`` holds every member's rough calendar-year return, ``None`` where
    it cannot be placed. The tenth is MATLAB's rounding of a tenth of
    ``universe``. A missing member threatens when it cannot be placed, or when
    its return is no further in than the member twice a tenth in from either
    end of the placed returns. Ties at that boundary threaten, so the rule
    errs toward flagging.
    """
    tenth = int(round_half_away(universe / 10))
    margin = 2 * tenth
    placed = sorted(value for value in returns.values() if value is not None)
    if not placed or margin == 0:
        return [key for key in missing if returns.get(key) is None]
    low = placed[min(margin, len(placed)) - 1]
    high = placed[-min(margin, len(placed))]
    flagged = []
    for key in missing:
        value = returns.get(key)
        if value is None or value <= low or value >= high:
            flagged.append(key)
    return flagged


def year_end_returns(
    fund: Fund, report_date: str, filings_dir: Path | None = None
) -> dict[Key, Decimal | None]:
    """Each member's rough calendar-year return from :func:`chan.fund_holdings.place`, by row."""
    numbered = numbered_members(fund, report_date, filings_dir)
    placements = place(fund, report_date, filings_dir)
    return {
        (report_date, row): placement.calendar_return
        for (row, _), placement in zip(numbered, placements, strict=True)
    }
