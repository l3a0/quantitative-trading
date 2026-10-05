"""The pins for the S&P 600 year-end panel: IJR's members, their tickers, and their coverage.

This file is the single authority for every number any prose surface quotes
about ``research/filings/ijr/members.csv``.
[Issue 332](https://github.com/l3a0/quantitative-trading/issues/332) built it.

**The specification.** A member is a row :func:`chan.fund_holdings.members`
keeps. Its ticker is the one the members file maps it to. Its check compares
Alpha Vantage's raw ``close`` on the price date, times the filing's share
count, with the filing's value, within half the filing's value unit. The price
date is the last trading day on or before the report date in the committed raw
SPY vintage, ``yfinance_spy_raw_1993-01-29_2026-10-02_dl2026-10-03.csv``. A
member is covered at a year-end when its row passes and, where
:func:`chan.fund_holdings.link` links it to the filing before, that row passed
too. The threat rule is issue 329's, with the tenth sized on every member of
the year-end.

**The vintage.** The closes are the ``sp600`` cross-section in
``data/archive_vintages.jsonl``, downloaded from Alpha Vantage with
``TIME_SERIES_DAILY_ADJUSTED`` on the dates its lines record. The committed
coverage pins read only the members file, whose sha256 they name, so they run
in CI. The pins that recompute the check read the archive, and skip with the
archive's own reason where there is none.
"""

from __future__ import annotations

import hashlib

import pandas as pd
import pytest

from chan import archive, sp600_panel
from chan.archive import ArchiveUnavailable
from chan.fund_holdings import IJR
from chan.fund_panel import (
    coverage,
    numbered_members,
    panel_keys,
    previous_rows,
    price_date,
    read_members,
)
from chan.vintage import SYMBOL_PATTERN

ROWS = read_members(sp600_panel.MEMBERS_PATH)
BY_KEY = {row.key: row for row in ROWS}
COVERAGE = {year.report_date: year for year in coverage(IJR, ROWS)}


def _name(report_date: str, row: int) -> str:
    return dict(numbered_members(IJR, report_date))[row].name


class TestTheMembersFile:
    def test_it_holds_every_row_of_the_panel_once_in_order(self) -> None:
        assert [row.key for row in ROWS] == sorted(panel_keys(IJR))

    def test_it_is_what_the_writer_writes(self) -> None:
        from chan.fund_panel import serialize_members

        assert serialize_members(ROWS) == sp600_panel.MEMBERS_PATH.read_bytes()

    def test_a_link_row_takes_the_ticker_of_the_row_that_links_to_it(self) -> None:
        forward = {before: after for after, before in previous_rows(IJR).items()}
        for row in ROWS:
            if row.source == "link":
                assert BY_KEY[forward[row.key]].ticker == row.ticker, row.key

    def test_every_ticker_is_a_symbol_the_archive_records_as_written(self) -> None:
        assert all(SYMBOL_PATTERN.fullmatch(row.ticker) for row in ROWS if row.ticker)

    def test_every_hand_row_names_its_evidence(self) -> None:
        assert all(row.note for row in ROWS if row.source == "hand")

    def test_every_row_carries_a_check(self) -> None:
        assert all(row.check for row in ROWS)

    def test_no_two_members_of_one_year_end_pass_on_one_ticker(self) -> None:
        passing = [(row.report_date, row.ticker) for row in ROWS if row.check == "pass"]
        assert len(passing) == len(set(passing))


class TestThePriceDates:
    @pytest.mark.parametrize(
        ("report_date", "day"),
        [
            ("2011-12-31", "2011-12-30"),
            ("2016-12-31", "2016-12-30"),
            ("2017-12-31", "2017-12-29"),
            ("2022-12-30", "2022-12-30"),
            ("2023-12-31", "2023-12-29"),
        ],
    )
    def test_a_weekend_year_end_takes_the_last_trading_day_before_it(
        self, report_date: str, day: str
    ) -> None:
        assert price_date(sp600_panel.calendar(), report_date) == pd.Timestamp(day)


def _store():
    try:
        return archive.archive_dir()
    except ArchiveUnavailable as absent:
        pytest.skip(str(absent))


class TestTheArchive:
    """Runs only where an archive is configured."""

    def test_the_committed_check_is_what_the_archive_gives(self) -> None:
        store = _store()
        try:
            recomputed = sp600_panel.check(directory=store)
        except ArchiveUnavailable as absent:
            pytest.skip(str(absent))
        assert tuple(recomputed) == ROWS


def test_the_members_file_hash() -> None:
    digest = hashlib.sha256(sp600_panel.MEMBERS_PATH.read_bytes()).hexdigest()
    assert digest == MEMBERS_SHA256


MEMBERS_SHA256 = ""
