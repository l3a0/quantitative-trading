"""The S&P 600 year-end panel: IJR's members, Alpha Vantage's closes, and how much they cover.

[Issue 332](https://github.com/l3a0/quantitative-trading/issues/332) is the
scope. [Issue 329](https://github.com/l3a0/quantitative-trading/issues/329)
runs Example 7.6 on this panel, and needs to know which year-ends it covers
whole. Every step lives in :mod:`chan.fund_panel`, which the S&P 500 panel
shares. This module binds IJR, the ``sp600`` cross-section and the members file
at ``research/filings/ijr/members.csv``, and holds the command.

```bash
QT_ARCHIVE_DIR=/path/to/archive zsh -i -c 'uv run python -m chan.sp600_panel fetch'
QT_ARCHIVE_DIR=/path/to/archive uv run python -m chan.sp600_panel check
uv run python -m chan.sp600_panel report
```

1. ``fetch`` hands every mapped ticker to :func:`chan.fetch_alphavantage.fetch`,
   which records only the symbols with no line yet. It reads
   ``ALPHAVANTAGE_API_KEY`` from the environment, which the owner's
   ``~/.zshrc`` exports, hence the interactive shell.
2. ``check`` reads the archive and rewrites the members file's ``check``,
   ``gap`` and ``exit`` columns.
3. ``report`` reads only committed tables and prints each year-end's coverage
   and the missing members that threaten a tenth.

The calendar is the committed raw SPY vintage, so a price date is a day the
exchange traded rather than a day some series happens to carry.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Sequence
from pathlib import Path

import pandas as pd

from chan import fetch_alphavantage
from chan.archive import ArchiveRefused, ArchiveUnavailable, read_cross_section
from chan.fund_holdings import FILINGS_DIR, IJR
from chan.fund_panel import (
    Coverage,
    MemberRow,
    PanelRefused,
    check_members,
    coverage,
    members_path,
    read_members,
    serialize_members,
    threats,
    year_end_returns,
)
from chan.series import load_vintage

FUND = IJR
CROSS_SECTION = "sp600"
MEMBERS_PATH = members_path(FUND)


def calendar(data_dir: Path | None = None) -> pd.DatetimeIndex:
    """The trading days of the committed raw SPY vintage."""
    _, closes = load_vintage("SPY", unadjusted=True, data_dir=data_dir)
    return pd.DatetimeIndex(closes.index)


def tickers(rows: Sequence[MemberRow]) -> list[str]:
    """Every mapped ticker, once each, sorted."""
    return sorted({row.ticker for row in rows if row.ticker})


def check(path: Path = MEMBERS_PATH, *, directory: Path | None = None) -> list[MemberRow]:
    """The members file's rows with the check recomputed from the archive."""
    rows = read_members(path)
    wanted = tickers(rows)
    _, closes = read_cross_section(
        CROSS_SECTION, column="close", symbols=wanted, directory=directory
    )
    return check_members(FUND, rows, closes, calendar())


def threatening(rows: Sequence[MemberRow], report: Coverage) -> list[tuple[str, int]]:
    """The missing members at one year-end that could change a tenth.

    The tenth is sized on every member of the year-end, because which covered
    members rank needs prices and this reads only committed tables. Issue 329
    passes its own count of the ranked covered members plus the missing ones.
    """
    returns = year_end_returns(FUND, report.report_date)
    return threats(returns, report.missing, universe=report.members)


def report_lines(rows: Sequence[MemberRow]) -> list[str]:
    """One line per year-end, then one per missing member that threatens a tenth."""
    names = {
        (filing.report_date, row): holding.name
        for filing in FUND.filings
        for row, holding in _numbered(filing.report_date)
    }
    lines = []
    flagged_lines = []
    for year in coverage(FUND, rows):
        misses = ", ".join(f"{reason} {count}" for reason, count in sorted(year.misses.items()))
        flagged = threatening(rows, year)
        lines.append(
            f"{year.report_date}  members {year.members}  covered {year.covered}  "
            f"January stops {year.stops}  missing {year.members - year.covered}"
            + (f" ({misses})" if misses else "")
            + f"  threats {len(flagged)}"
            + ("  exact" if not flagged else "")
        )
        flagged_lines.extend(f"  {key[0]} row {key[1]}: {names[key]}" for key in flagged)
    return lines + (["threatening members:", *flagged_lines] if flagged_lines else [])


def _numbered(report_date: str):
    from chan.fund_panel import numbered_members

    return numbered_members(FUND, report_date)


def main(argv: Sequence[str] | None = None) -> None:
    """``python -m chan.sp600_panel {fetch,check,report}``."""
    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) != 1 or arguments[0] not in ("fetch", "check", "report"):
        raise SystemExit("usage: python -m chan.sp600_panel {fetch,check,report}")
    command = arguments[0]
    try:
        if command == "fetch":
            key = os.environ.get(fetch_alphavantage.KEY_ENV, "").strip()
            if not key:
                raise SystemExit(f"{fetch_alphavantage.KEY_ENV} is not set, so no request was made")
            tally = fetch_alphavantage.fetch(
                CROSS_SECTION, tickers(read_members(MEMBERS_PATH)), key=key
            )
            print(fetch_alphavantage._redact(tally.line(), key))
            if not tally.complete:
                raise SystemExit(1)
        elif command == "check":
            MEMBERS_PATH.write_bytes(serialize_members(check()))
            print(f"wrote {MEMBERS_PATH.relative_to(FILINGS_DIR.parent.parent)}")
        else:
            print("\n".join(report_lines(read_members(MEMBERS_PATH))))
    except (ArchiveUnavailable, ArchiveRefused, PanelRefused) as refusal:
        # One line rather than a traceback, the way chan.equity_seasonals
        # reports a vintage it could not read.
        raise SystemExit(str(refusal)) from refusal


if __name__ == "__main__":
    main()
