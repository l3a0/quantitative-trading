"""The S&P 400 panel for issue 303, and the S&P 600 control built the same way.

[Issue 303](https://github.com/l3a0/quantitative-trading/issues/303) runs
Example 3.8's reversal on the S&P 400, the mid-cap half of the exercise Chan
leaves, beside his S&P 500 and S&P 600 files. Chan saved no mid-cap file, so
the universe is IJH's schedule in iShares Trust's N-Q for 2007-12-31, which
:data:`chan.fund_holdings.IJH` records, priced from Alpha Vantage's daily bars
in the ``sp400`` cross-section of the owner's archive.

Those prices come from another vendor and another download decade than Chan's
two files, so the issue adds a control: the S&P 600, built from IJR's schedule
in the same N-Q exactly the way the S&P 400 panel is built, and priced from the
``sp600`` cross-section. A gap between the control and Chan's S&P 600 file
measures what building a panel this way does to the figure.

Two panels, each one filing's every member, mapped and checked by
:mod:`chan.fund_panel`.

1. :data:`IJH_PANEL`, IJH's 401 holdings, in ``research/filings/ijh/members.csv``.
2. :data:`CONTROL`, IJR's 602 holdings, in
   ``research/filings/ijr/members_2007-12-31.csv``. IJR's own members file
   holds only the 509 holdings of 2007-12-31 that link into the 2008-12-31
   schedule, because those are what IJR's year-end panel ranks. A control
   read from it would hold only members that were still in the index a year
   later, while the S&P 400 panel holds every holding. So the control file
   holds all 602, and its 509 shared rows are exactly IJR's members file's.

The ``exit`` column is :func:`chan.fund_panel.check_members`'s default, the
close at the end of January 2008. The 2006 run does not read it. It is kept so
the control's 509 shared rows stay byte for byte what IJR's file holds.

**Which passing members a run holds.** A run over 2006 needs the series to
trade in 2006, so :func:`history` sorts each passing member by its 2006 rows
into one of :data:`HISTORIES`.

1. ``full``: an adjusted close and an open on the day before the window and on
   every trading day inside it.
2. ``partial``: a first row on or before the day before the window, with a
   close or an open missing on some day.
3. ``listed``: a first row inside the window, before :data:`VENDOR_START`.
4. ``cut``: a first row on or after :data:`VENDOR_START`, which inside the
   window means 2006-12-28 or 2006-12-29. Fifteen of the series issue 332 recorded into
   the ``sp600`` cross-section on 2026-10-05 begin on 2006-12-28, and Chan's
   ``IJR_20080114.mat`` holds a close for 13 of those 15 on every trading day
   of 2006, so the date is the vendor's cut-off rather than a listing.
5. ``absent``: no row inside the window.

A run holds ``full``, ``partial`` and ``listed`` members, which is
:func:`panel_keys`.

```bash
QT_ARCHIVE_DIR=/path/to/archive uv run python -m chan.sp400_panel fetch ijh
QT_ARCHIVE_DIR=/path/to/archive uv run python -m chan.sp400_panel check ijh
uv run python -m chan.sp400_panel report ijh
QT_ARCHIVE_DIR=/path/to/archive uv run python -m chan.sp400_panel history ijh
```

Each takes ``ijh`` or ``control``. ``fetch`` reads ``ALPHAVANTAGE_API_KEY``
from the environment. ``report`` reads only committed tables, and ``history``
reads the archive.
"""

from __future__ import annotations

import os
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from chan import fetch_alphavantage
from chan.archive import ArchiveRefused, ArchiveUnavailable, read_cross_section
from chan.fund_holdings import FILINGS_DIR, IJH, IJR, Fund
from chan.fund_panel import (
    CHECKS,
    Key,
    MemberRow,
    PanelRefused,
    check_members,
    members_path,
    numbered_members,
    read_members,
    serialize_members,
)
from chan.sp600_panel import calendar

#: The date both panels are read at.
REPORT_DATE = "2007-12-31"

#: The run's window, Example 3.8's 2006, as its first and last trading days.
WINDOW_START = "2006-01-03"
WINDOW_END = "2006-12-29"

#: The trading day before the window, whose close the window's first return needs.
BEFORE_WINDOW = "2005-12-30"

#: The first day of Alpha Vantage's history for series it holds no earlier rows of.
VENDOR_START = "2006-12-28"

#: How a passing member's series covers 2006, in the order :func:`history` tests.
HISTORIES = ("full", "partial", "listed", "cut", "absent")

#: The histories a run over 2006 holds.
HELD = ("full", "partial", "listed")


@dataclass(frozen=True)
class Panel:
    """One fund's members at one filing, the cross-section pricing them, and its file."""

    name: str
    fund: Fund
    cross_section: str
    path: Path


IJH_PANEL = Panel("ijh", IJH, "sp400", members_path(IJH))
CONTROL = Panel("control", IJR, "sp600", FILINGS_DIR / "ijr" / f"members_{REPORT_DATE}.csv")
PANELS: Mapping[str, Panel] = {panel.name: panel for panel in (IJH_PANEL, CONTROL)}


def keys(panel: Panel) -> list[Key]:
    """Every member of the panel's filing, in the filing's order."""
    return [(REPORT_DATE, row) for row, _ in numbered_members(panel.fund, REPORT_DATE)]


def load(panel: Panel, path: Path | None = None) -> tuple[MemberRow, ...]:
    """The panel's members file, refused unless it names every member of the filing once."""
    rows = read_members(panel.path if path is None else path)
    wanted, held = keys(panel), [row.key for row in rows]
    if held != wanted:
        stray, absent = sorted(set(held) - set(wanted)), sorted(set(wanted) - set(held))
        raise PanelRefused(
            f"the members file names {len(stray)} rows the filing does not hold and lacks "
            f"{len(absent)} it does"
        )
    return rows


def tickers(rows: Sequence[MemberRow]) -> list[str]:
    """Every mapped ticker, once each, sorted."""
    return sorted({row.ticker for row in rows if row.ticker})


def fetch_symbols(panel: Panel, rows: Sequence[MemberRow]) -> list[str]:
    """The tickers a fetch asks for: every mapped ticker, less what IJR's own panel fetches.

    The control's 509 shared rows are IJR's members file's, whose tickers that
    panel's fetch already asked for. Asking again would record a ticker
    Alpha Vantage has started to serve since, which changes a check IJR's
    file pins, so the control asks only for the tickers its other rows map.
    """
    if panel is not CONTROL:
        return tickers(rows)
    shared = {row.key for row in read_members(members_path(IJR))}
    return tickers([row for row in rows if row.key not in shared])


def check(panel: Panel, *, directory: Path | None = None) -> list[MemberRow]:
    """The members file's rows with the check recomputed from the panel's cross-section."""
    rows = load(panel)
    _, closes = read_cross_section(
        panel.cross_section, column="close", symbols=tickers(rows), directory=directory
    )
    return check_members(panel.fund, rows, closes, calendar())


# --- Coverage by check, from committed tables ---------------------------------


@dataclass(frozen=True)
class Verdict:
    """How many members one check gave, and the filing's value they hold, in dollars."""

    check: str
    members: int
    value: int


def verdicts(panel: Panel, rows: Sequence[MemberRow]) -> list[Verdict]:
    """Each check's members and value, in :data:`chan.fund_panel.CHECKS` order, none omitted."""
    holdings = dict(numbered_members(panel.fund, REPORT_DATE))
    members: Counter[str] = Counter()
    value: Counter[str] = Counter()
    for row in rows:
        if not row.check:
            raise PanelRefused(f"row {row.row} has not been checked")
        members[row.check] += 1
        value[row.check] += int(holdings[row.row].value)
    return [Verdict(check, members[check], value[check]) for check in CHECKS]


def report_lines(panel: Panel, rows: Sequence[MemberRow]) -> list[str]:
    """One line per check with its count and value, then every member that did not pass."""
    holdings = dict(numbered_members(panel.fund, REPORT_DATE))
    total = sum(int(holding.value) for holding in holdings.values())
    lines = [f"{panel.name}: {len(rows)} members on {REPORT_DATE}, value {total:,}"]
    for verdict in verdicts(panel, rows):
        lines.append(
            f"  {verdict.check:9} {verdict.members:4}  "
            f"{verdict.members / len(rows):6.1%} by count  "
            f"{verdict.value / total:6.1%} by value"
        )
    lines.append("members that did not pass:")
    for row in rows:
        if row.check != "pass":
            lines.append(
                f"  row {row.row} {row.ticker or '-'}: {holdings[row.row].name}, {row.check}"
            )
    return lines


# --- 2006 history, from the archive -------------------------------------------


@dataclass(frozen=True)
class History:
    """One passing member's 2006 rows: how many days hold a close and an open, and its kind."""

    key: Key
    ticker: str
    first: pd.Timestamp
    closes: int
    opens: int
    kind: str


def window_days(days: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """The trading days inside the window."""
    return days[(days >= pd.Timestamp(WINDOW_START)) & (days <= pd.Timestamp(WINDOW_END))]


def history(
    rows: Sequence[MemberRow],
    adjusted: pd.DataFrame,
    opens: pd.DataFrame,
    days: pd.DatetimeIndex,
) -> list[History]:
    """Each passing member's 2006 history, sorted into :data:`HISTORIES`.

    ``adjusted`` and ``opens`` are date-by-ticker frames of the adjusted close
    and the raw open, and ``days`` is the calendar. A day counts for a member
    when its frame holds a number there, so a missing open makes the history
    ``partial`` even where the close is whole. A series with a row inside the
    window whose first row falls on or after :data:`VENDOR_START` is ``cut``,
    so a series the vendor starts a day late is not taken for a listing.
    """
    inside = window_days(days)
    wanted = pd.DatetimeIndex([pd.Timestamp(BEFORE_WINDOW), *inside])
    found = []
    for row in rows:
        if row.check != "pass":
            continue
        close = adjusted[row.ticker].dropna()
        opened = opens[row.ticker].dropna()
        first = close.index[0]
        on_close = close.index.intersection(inside)
        on_open = opened.index.intersection(inside)
        if len(on_close) == 0:
            kind = "absent"
        elif first >= pd.Timestamp(VENDOR_START):
            kind = "cut"
        elif first > pd.Timestamp(BEFORE_WINDOW):
            kind = "listed"
        elif wanted.isin(close.index).all() and wanted.isin(opened.index).all():
            kind = "full"
        else:
            kind = "partial"
        found.append(History(row.key, row.ticker, first, len(on_close), len(on_open), kind))
    return found


def panel_keys(histories: Sequence[History]) -> list[Key]:
    """The members a run over 2006 holds: those whose history is in :data:`HELD`."""
    return [entry.key for entry in histories if entry.kind in HELD]


def frames(
    panel: Panel, rows: Sequence[MemberRow], *, directory: Path | None = None
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """The adjusted closes, raw opens and adjusted opens of every passing member.

    The vendor adjusts only the close, so the adjusted open is the raw open
    times that day's adjusted close over its raw close, which issue 303
    declares.
    """
    symbols = sorted({row.ticker for row in rows if row.check == "pass"})
    read = {
        column: read_cross_section(
            panel.cross_section, column=column, symbols=symbols, directory=directory
        )[1]
        for column in ("adjusted_close", "close", "open")
    }
    adjusted_opens = read["open"] * read["adjusted_close"] / read["close"]
    return read["adjusted_close"], read["open"], adjusted_opens


def history_lines(panel: Panel, *, directory: Path | None = None) -> list[str]:
    """Each history's count and value, then every passing member a run leaves out."""
    rows = load(panel)
    adjusted, opens, _ = frames(panel, rows, directory=directory)
    entries = history(rows, adjusted, opens, calendar())
    holdings = dict(numbered_members(panel.fund, REPORT_DATE))
    total = sum(int(holding.value) for holding in holdings.values())
    counts = Counter(entry.kind for entry in entries)
    held = set(panel_keys(entries))
    held_value = sum(int(holdings[row].value) for _, row in held)
    lines = [f"{panel.name}: {len(entries)} passing members by 2006 history"]
    lines += [f"  {kind:8} {counts[kind]:4}" for kind in HISTORIES]
    lines.append(
        f"held by a run: {len(held)} of {len(rows)}, {len(held) / len(rows):.1%} by count, "
        f"{held_value / total:.1%} by value"
    )
    lines.append("passing members a run leaves out:")
    for entry in entries:
        if entry.kind not in HELD:
            name = holdings[entry.key[1]].name
            lines.append(
                f"  row {entry.key[1]} {entry.ticker}: {name}, {entry.kind}, "
                f"first row {entry.first.date()}"
            )
    return lines


# --- The command ---------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> None:
    """``python -m chan.sp400_panel {fetch,check,report,history} {ijh,control}``."""
    arguments = list(sys.argv[1:] if argv is None else argv)
    commands = ("fetch", "check", "report", "history")
    if len(arguments) != 2 or arguments[0] not in commands or arguments[1] not in PANELS:
        raise SystemExit(
            f"usage: python -m chan.sp400_panel {{{','.join(commands)}}} {{{','.join(PANELS)}}}"
        )
    command, panel = arguments[0], PANELS[arguments[1]]
    try:
        if command == "fetch":
            key = os.environ.get(fetch_alphavantage.KEY_ENV, "").strip()
            if not key:
                raise SystemExit(f"{fetch_alphavantage.KEY_ENV} is not set, so no request was made")
            symbols = fetch_symbols(panel, load(panel))
            tally = fetch_alphavantage.fetch(panel.cross_section, symbols, key=key)
            # The tally names each failed symbol, so it passes through the
            # fetch's own redaction in case a failure ever quotes the key.
            print(tally.line().replace(key, "<key>"))
            if not tally.complete:
                raise SystemExit(1)
        elif command == "check":
            panel.path.write_bytes(serialize_members(check(panel)))
            print(f"wrote {panel.path.relative_to(FILINGS_DIR.parent.parent)}")
        elif command == "report":
            print("\n".join(report_lines(panel, load(panel))))
        else:
            print("\n".join(history_lines(panel)))
    except (ArchiveUnavailable, ArchiveRefused, PanelRefused) as refusal:
        # One line rather than a traceback, the way chan.sp600_panel reports
        # a refusal.
        raise SystemExit(str(refusal)) from refusal


if __name__ == "__main__":
    main()
