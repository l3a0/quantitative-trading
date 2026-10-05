"""The S&P 500 monthly panel: IVV's members, Alpha Vantage's closes, and how much they cover.

[Issue 373](https://github.com/l3a0/quantitative-trading/issues/373) is the
scope. [Issue 336](https://github.com/l3a0/quantitative-trading/issues/336)
runs Example 7.7 on this panel, ranking at every month-end from December 2008
to August 2026, and needs to know which members it can rank there. The mapping
and the check live in :mod:`chan.fund_panel`, which the S&P 600 panel shares.
This module binds IVV, the ``sp500`` cross-section and the members file at
``research/filings/ivv/members.csv``, and holds the month-by-month coverage
rule, which only Example 7.7 reads.

```bash
QT_ARCHIVE_DIR=/path/to/archive zsh -i -c 'uv run python -m chan.sp500_panel fetch'
QT_ARCHIVE_DIR=/path/to/archive uv run python -m chan.sp500_panel check
uv run python -m chan.sp500_panel report
```

1. ``fetch`` hands every mapped ticker, and IVV itself, to
   :func:`chan.fetch_alphavantage.fetch`, which records only the symbols with
   no line yet. It reads ``ALPHAVANTAGE_API_KEY`` from the environment, which
   the owner's ``~/.zshrc`` exports, hence the interactive shell.
2. ``check`` reads the archive, rewrites the members file's ``check``, ``gap``
   and ``exit`` columns, and rewrites the holes file.
3. ``report`` reads only committed tables and prints each month-end's
   coverage, then every missing member with its reason.

**Which months a schedule sets.** IVV files a schedule at each quarter-end, and
issue 336 carries each one's members forward to the next. So a schedule sets
the month of its own report date and every month before the next listed
schedule's, which is three months, or six for 2013-06-30, because 2013-09-30
prints only a summary. A passing row's ``exit`` asks whether the series holds
the close at which the last position its schedule sets is closed, the
month-end after the last month it sets.

**What a covered member needs at a month-end.** Example 7.7 ranks on the return
of the month a year before the month it holds, so the series must hold three
things.

1. The close at the month-end, trusted when the member's row passed the check
   at the schedule that sets that month.
2. The closes at the month-ends twelve and eleven months back. Where the
   member was in the index then, by :func:`chan.fund_panel.previous_rows`, each
   is trusted when the row it links back to passed on the same ticker at the
   schedule that sets that month. A member new to the index is ranked on its
   series alone, and so is every member for a month before the first schedule.
3. A close at the next month-end, unless the series ends inside that month.
   A series that ends there is covered, because issue 336 gives the position
   its return to the last close, and it is counted as a stop.

A member that misses carries one reason, checked in this order: its check
outcome when it did not pass, ``stopped`` when its series ended before the
month-end, ``close`` when the series runs past the month-end with no row on
it, ``rank`` when a year-earlier close is missing or untrusted, and ``next``
when the series continues past the next month-end with no row on it.

**Why a second committed table.** The report runs in CI, where no archive is,
and it reads month-ends the check never looked at. The manifest's
``first_date`` and ``last_date`` give each series' span. The holes file,
``research/filings/ivv/holes.csv``, names every month-end inside a span where
the series holds no row, so the two together say which month-end closes exist
without committing a price.

The calendar is the committed raw SPY vintage, as the S&P 600 panel's is, so a
month-end is a day the exchange traded rather than a day some series happens to
carry. Issue 336 takes IVV's own trading days, and
``tests/test_sp500_panel.py`` holds that the two agree at every month-end.
"""

from __future__ import annotations

import csv
import io
import os
import sys
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from functools import cache
from pathlib import Path

import pandas as pd

from chan import fetch_alphavantage
from chan.archive import (
    ArchiveRefused,
    ArchiveUnavailable,
    read_archive_manifest,
    read_cross_section,
)
from chan.fund_holdings import FILINGS_DIR, IVV
from chan.fund_panel import (
    Key,
    MemberRow,
    PanelRefused,
    check_members,
    listed,
    members_path,
    numbered_members,
    previous_rows,
    read_members,
    require_panel,
    serialize_members,
)
from chan.series import load_vintage

FUND = IVV
CROSS_SECTION = "sp500"
MEMBERS_PATH = members_path(FUND)
HOLES_PATH = MEMBERS_PATH.with_name("holes.csv")

#: The first and last month-ends Example 7.7 ranks at, so the first position is
#: held over January 2009 and the last over September 2026, as issue 336 ruled.
FIRST_MONTH = pd.Period("2008-12", "M")
LAST_MONTH = pd.Period("2026-08", "M")

#: How far back a ranking reads: the month twelve months before a month-end.
LOOKBACK = 12

#: The holes file's columns.
HOLE_COLUMNS = ("ticker", "month")

#: The reasons a member that passed its check can still miss, in the order
#: they are tested. A member that failed its check misses with its outcome.
MISSES = ("stopped", "close", "rank", "next")


def calendar(data_dir: Path | None = None) -> pd.DatetimeIndex:
    """The trading days of the committed raw SPY vintage."""
    _, closes = load_vintage("SPY", unadjusted=True, data_dir=data_dir)
    return pd.DatetimeIndex(closes.index)


def month_end(calendar: pd.DatetimeIndex, month: pd.Period) -> pd.Timestamp:
    """The last trading day of a month, refused unless the calendar runs past the month."""
    if calendar[-1] <= month.end_time:
        raise PanelRefused(f"the calendar does not run past {month}")
    inside = calendar[(calendar >= month.start_time) & (calendar <= month.end_time)]
    if len(inside) == 0:
        raise PanelRefused(f"the calendar holds no trading day in {month}")
    return inside[-1]


@cache
def schedule_months() -> tuple[tuple[str, pd.Period], ...]:
    """Each listed schedule's report date and the month it sets first, in order."""
    return tuple(
        (filing.report_date, pd.Period(filing.report_date, "M")) for filing in listed(FUND)
    )


@cache
def setter(month: pd.Period) -> str | None:
    """The report date of the schedule that sets a month, or ``None`` before the first."""
    found = None
    for report_date, first in schedule_months():
        if first <= month:
            found = report_date
    return found


def last_month_set(report_date: str) -> pd.Period:
    """The last month a schedule sets: the month before the next listed one, or the span's end."""
    order = schedule_months()
    at = [date for date, _ in order].index(report_date)
    if at + 1 < len(order):
        return order[at + 1][1] - 1
    return LAST_MONTH


def exit_close(calendar: pd.DatetimeIndex, report_date: str) -> pd.Timestamp:
    """The day the last position a schedule sets is closed, which a passing exit asks about."""
    return month_end(calendar, last_month_set(report_date) + 1)


def months() -> list[pd.Period]:
    """Every month-end Example 7.7 ranks at, from :data:`FIRST_MONTH` to :data:`LAST_MONTH`."""
    return list(pd.period_range(FIRST_MONTH, LAST_MONTH, freq="M"))


def tickers(rows: Sequence[MemberRow]) -> list[str]:
    """Every mapped ticker, once each, sorted."""
    return sorted({row.ticker for row in rows if row.ticker})


def load(path: Path = MEMBERS_PATH) -> tuple[MemberRow, ...]:
    """The members file, refused unless it names exactly the panel's rows."""
    rows = read_members(path)
    require_panel(FUND, rows, whole_first=True)
    return rows


# --- The holes file ----------------------------------------------------------


def read_holes(path: Path = HOLES_PATH) -> frozenset[tuple[str, str]]:
    """The holes file's ticker and month pairs, refusing a column it does not allow."""
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != HOLE_COLUMNS:
            raise PanelRefused(f"{path} has columns {reader.fieldnames}, not {list(HOLE_COLUMNS)}")
        return frozenset((line["ticker"], line["month"]) for line in reader)


def serialize_holes(holes: Iterable[tuple[str, str]]) -> bytes:
    """A holes file's bytes, sorted by ticker then month, LF endings."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(HOLE_COLUMNS)
    writer.writerows(sorted(set(holes)))
    return buffer.getvalue().encode("utf-8")


def find_holes(
    closes: pd.DataFrame, spans: Mapping[str, tuple[str, str]], calendar: pd.DatetimeIndex
) -> set[tuple[str, str]]:
    """Every month-end the coverage reads that falls inside a series' span with no row on it."""
    read = pd.period_range(FIRST_MONTH - LOOKBACK, LAST_MONTH + 1, freq="M")
    days = {str(month): month_end(calendar, month) for month in read}
    holes = set()
    for ticker in closes.columns:
        first, last = (pd.Timestamp(day) for day in spans[ticker])
        series = closes[ticker]
        for month, day in days.items():
            if first <= day <= last and pd.isna(series.get(day)):
                holes.add((ticker, month))
    return holes


def spans(data_dir: Path | None = None) -> dict[str, tuple[str, str]]:
    """Each ``sp500`` symbol's first and last date, as its manifest line records them."""
    return {
        entry.symbol: (entry.first_date, entry.last_date)
        for entry in read_archive_manifest(data_dir)
        if entry.cross_section == CROSS_SECTION
    }


# --- The check -----------------------------------------------------------------


def check(
    path: Path = MEMBERS_PATH, *, directory: Path | None = None
) -> tuple[list[MemberRow], set[tuple[str, str]]]:
    """The members file's rows with the check recomputed from the archive, and the holes."""
    rows = load(path)
    _, closes = read_cross_section(
        CROSS_SECTION, column="close", symbols=tickers(rows), directory=directory
    )
    days = calendar()
    checked = check_members(FUND, rows, closes, days, exit_on=exit_close)
    return checked, find_holes(closes, spans(), days)


# --- Coverage, month by month --------------------------------------------------


@dataclass(frozen=True)
class MonthCoverage:
    """What the panel covers at one month-end.

    ``schedule`` is the report date of the schedule that sets the month.
    ``misses`` counts the members not covered by reason, and ``stops`` counts
    covered members whose series ends inside the next month.
    """

    month: str
    schedule: str
    members: int
    covered: int
    misses: dict[str, int]
    stops: int
    missing: tuple[Key, ...]
    reasons: tuple[str, ...]


class _Closes:
    """Whether a ticker's series holds a close at a month-end, from committed tables only."""

    def __init__(
        self,
        spans: Mapping[str, tuple[str, str]],
        holes: frozenset[tuple[str, str]],
        calendar: pd.DatetimeIndex,
    ) -> None:
        self._spans = {
            ticker: (pd.Timestamp(first), pd.Timestamp(last))
            for ticker, (first, last) in spans.items()
        }
        self._holes = holes
        self._calendar = calendar
        self._days: dict[pd.Period, pd.Timestamp] = {}

    def day(self, month: pd.Period) -> pd.Timestamp:
        if month not in self._days:
            self._days[month] = month_end(self._calendar, month)
        return self._days[month]

    def last(self, ticker: str) -> pd.Timestamp:
        return self._spans[ticker][1]

    def has(self, ticker: str, month: pd.Period) -> bool:
        if ticker not in self._spans:
            return False
        first, last = self._spans[ticker]
        day = self.day(month)
        return first <= day <= last and (ticker, str(month)) not in self._holes


def _reason(
    row: MemberRow,
    month: pd.Period,
    closes: _Closes,
    by_key: Mapping[Key, MemberRow],
    previous: Mapping[Key, Key],
    first_schedule: pd.Period,
) -> str | None:
    """Why a member misses at a month-end, or ``None`` when it is covered."""
    if row.check != "pass":
        return row.check
    ticker = row.ticker
    if not closes.has(ticker, month):
        return "stopped" if closes.last(ticker) < closes.day(month) else "close"
    for back in (month - LOOKBACK, month - LOOKBACK + 1):
        if not closes.has(ticker, back):
            return "rank"
        if back < first_schedule:
            continue
        wanted = setter(back)
        key: Key | None = row.key
        while key is not None and key[0] > wanted:
            key = previous.get(key)
        if key is None:
            continue
        before = by_key[key]
        if before.check != "pass" or before.ticker != ticker:
            return "rank"
    after = month + 1
    if not closes.has(ticker, after) and closes.last(ticker) >= closes.day(after):
        return "next"
    return None


def monthly_coverage(
    rows: Sequence[MemberRow],
    spans: Mapping[str, tuple[str, str]],
    holes: frozenset[tuple[str, str]],
    calendar: pd.DatetimeIndex,
) -> list[MonthCoverage]:
    """Each month-end from :data:`FIRST_MONTH` to :data:`LAST_MONTH`, with its coverage."""
    by_key = {row.key: row for row in rows}
    previous = previous_rows(FUND)
    closes = _Closes(spans, holes, calendar)
    first_schedule = schedule_months()[0][1]
    by_schedule: dict[str, list[MemberRow]] = {}
    for row in rows:
        by_schedule.setdefault(row.report_date, []).append(row)
    report = []
    for month in months():
        schedule = setter(month)
        if schedule is None:
            raise PanelRefused(f"no listed schedule sets {month}")
        mine = by_schedule[schedule]
        misses: Counter[str] = Counter()
        missing, reasons = [], []
        stops = 0
        for row in mine:
            if not row.check:
                raise PanelRefused(f"{row.report_date} row {row.row} has not been checked")
            reason = _reason(row, month, closes, by_key, previous, first_schedule)
            if reason is None:
                stops += closes.last(row.ticker) < closes.day(month + 1)
                continue
            misses[reason] += 1
            missing.append(row.key)
            reasons.append(reason)
        report.append(
            MonthCoverage(
                str(month),
                schedule,
                len(mine),
                len(mine) - len(missing),
                dict(misses),
                stops,
                tuple(missing),
                tuple(reasons),
            )
        )
    return report


def coverage_from_committed(rows: Sequence[MemberRow]) -> list[MonthCoverage]:
    """:func:`monthly_coverage` on the committed holes file, manifest and calendar."""
    return monthly_coverage(rows, spans(), read_holes(), calendar())


def report_lines(rows: Sequence[MemberRow]) -> list[str]:
    """One line per month-end, then one per missing member with its reason."""
    lines = []
    missing_lines = []
    names: dict[str, dict[int, str]] = {}
    by_key = {row.key: row for row in rows}
    for month in coverage_from_committed(rows):
        misses = ", ".join(f"{reason} {count}" for reason, count in sorted(month.misses.items()))
        lines.append(
            f"{month.month}  schedule {month.schedule}  members {month.members}  "
            f"covered {month.covered}  stops {month.stops}  "
            f"missing {month.members - month.covered}" + (f" ({misses})" if misses else "")
        )
        if month.schedule not in names:
            names[month.schedule] = {
                row: holding.name for row, holding in numbered_members(FUND, month.schedule)
            }
        for key, reason in zip(month.missing, month.reasons, strict=True):
            ticker = by_key[key].ticker or "-"
            missing_lines.append(
                f"  {month.month} row {key[1]} {ticker}: {names[month.schedule][key[1]]}, {reason}"
            )
    return lines + (["missing members:", *missing_lines] if missing_lines else [])


def main(argv: Sequence[str] | None = None) -> None:
    """``python -m chan.sp500_panel {fetch,check,report}``."""
    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) != 1 or arguments[0] not in ("fetch", "check", "report"):
        raise SystemExit("usage: python -m chan.sp500_panel {fetch,check,report}")
    command = arguments[0]
    try:
        if command == "fetch":
            key = os.environ.get(fetch_alphavantage.KEY_ENV, "").strip()
            if not key:
                raise SystemExit(f"{fetch_alphavantage.KEY_ENV} is not set, so no request was made")
            # IVV's own series is fetched too, because issue 336 takes its
            # trading days as the run's calendar.
            symbols = [FUND.symbol, *tickers(load())]
            tally = fetch_alphavantage.fetch(CROSS_SECTION, symbols, key=key)
            # The tally names each failed symbol, so it passes through the
            # fetch's own redaction in case a failure ever quotes the key.
            print(tally.line().replace(key, "<key>"))
            if not tally.complete:
                raise SystemExit(1)
        elif command == "check":
            rows, holes = check()
            MEMBERS_PATH.write_bytes(serialize_members(rows))
            HOLES_PATH.write_bytes(serialize_holes(holes))
            root = FILINGS_DIR.parent.parent
            print(f"wrote {MEMBERS_PATH.relative_to(root)} and {HOLES_PATH.relative_to(root)}")
        else:
            print("\n".join(report_lines(load())))
    except (ArchiveUnavailable, ArchiveRefused, PanelRefused) as refusal:
        # One line rather than a traceback, the way chan.sp600_panel reports
        # a refusal.
        raise SystemExit(str(refusal)) from refusal


if __name__ == "__main__":
    main()
