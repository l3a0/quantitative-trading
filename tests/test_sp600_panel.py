"""The pins for the S&P 600 year-end panel: IJR's members, their tickers, and their coverage.

This file is the single authority for every number any prose surface quotes
about ``research/filings/ijr/members.csv``.
[Issue 332](https://github.com/l3a0/quantitative-trading/issues/332) built it.

**The specification.** A member is a row :func:`chan.fund_holdings.members`
keeps. Its ticker is the one the members file maps it to. Its check compares
Alpha Vantage's raw ``close`` on the price date, times the filing's share
count, with the filing's value, within half the filing's value unit, plus
half a share at the close on an N-Q, which prints whole shares. The price
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
import json
from collections import Counter
from decimal import Decimal

import pandas as pd
import pytest

from chan import archive, fetch_alphavantage, sp600_panel
from chan.archive import ArchiveUnavailable, read_cross_section
from chan.fund_holdings import IJR
from chan.fund_panel import (
    HALF_SHARE,
    HALF_UNIT,
    PanelRefused,
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


#: Per year-end: members, covered, misses by reason, price misses within a
#: cent, January stops, and missing members that threaten a tenth.
YEAR_ENDS = (
    ("2008-12-31", 600, 439, {"no-row": 69, "no-series": 80, "price": 10, "rank": 2}, 0, 0, 89),
    ("2009-12-31", 600, 426, {"no-row": 60, "no-series": 68, "price": 46}, 20, 0, 89),
    ("2010-12-31", 600, 425, {"no-row": 57, "no-series": 58, "price": 29, "rank": 31}, 4, 0, 97),
    ("2011-12-31", 600, 481, {"no-row": 57, "no-series": 36, "price": 7, "rank": 19}, 0, 0, 67),
    ("2012-12-31", 601, 457, {"no-row": 53, "no-series": 25, "price": 66}, 27, 0, 76),
    ("2013-12-31", 601, 443, {"no-row": 47, "no-series": 18, "price": 42, "rank": 51}, 12, 0, 87),
    ("2014-12-31", 601, 506, {"no-row": 45, "no-series": 14, "price": 6, "rank": 30}, 0, 1, 49),
    ("2015-12-31", 601, 541, {"no-row": 42, "no-series": 10, "price": 8}, 0, 1, 34),
    ("2016-12-31", 602, 552, {"no-row": 26, "no-series": 11, "price": 9, "rank": 4}, 0, 0, 30),
    ("2017-12-31", 602, 556, {"no-row": 24, "no-series": 9, "price": 12, "rank": 1}, 5, 1, 30),
    ("2018-12-31", 603, 559, {"no-row": 23, "no-series": 9, "price": 7, "rank": 5}, 0, 2, 28),
    ("2019-12-31", 603, 563, {"no-row": 22, "no-series": 4, "price": 13, "rank": 1}, 6, 4, 22),
    ("2020-12-31", 601, 573, {"no-row": 12, "no-series": 4, "price": 7, "rank": 5}, 0, 1, 14),
    ("2021-12-31", 602, 588, {"no-row": 9, "no-series": 1, "price": 4}, 0, 1, 9),
    ("2022-12-30", 601, 590, {"no-row": 6, "no-series": 1, "price": 4}, 0, 0, 7),
    ("2023-12-31", 602, 593, {"no-row": 6, "price": 3}, 0, 3, 7),
    ("2024-12-31", 602, 594, {"no-row": 7, "price": 1}, 0, 3, 5),
    ("2025-12-31", 603, 601, {"no-row": 2}, 0, 1, 1),
)

#: How many rows each source answered, and how many each check gave.
SOURCES = {"cusip": 40, "filing": 791, "hand": 356, "link": 9538, "name": 609}
CHECKS = {"no-row": 632, "no-series": 414, "pass": 10004, "price": 284}

#: The report's whole output on the pinned members file, by sha256.
REPORT_SHA256 = "3a4a3e23b9dbbcae8059bdc0a40dbb85897d7e1a1526bf8bda7d88343aa5d9e7"

#: The members file this module pins, by sha256.
MEMBERS_SHA256 = "c92cc2512ded3a054c861b48e17572c9ff708a4dcfb548e9e226901c14adda9b"


class TestTheCoverage:
    def test_the_file_is_the_one_these_pins_were_measured_on(self) -> None:
        digest = hashlib.sha256(sp600_panel.MEMBERS_PATH.read_bytes()).hexdigest()
        assert digest == MEMBERS_SHA256

    @pytest.mark.parametrize("pin", YEAR_ENDS, ids=lambda pin: pin[0])
    def test_each_year_end_covers_its_pinned_members(self, pin: tuple) -> None:
        report_date, members, covered, misses, near, stops, threats = pin
        year = COVERAGE[report_date]
        assert (year.members, year.covered, year.misses) == (members, covered, misses)
        assert (year.within_a_cent, year.stops) == (near, stops)
        assert len(sp600_panel.threatening(ROWS, year)) == threats

    def test_every_year_end_after_2007_is_reported(self) -> None:
        assert [pin[0] for pin in YEAR_ENDS] == [f.report_date for f in IJR.filings[1:]]

    def test_no_year_end_is_exact(self) -> None:
        """Every year-end has a missing member that could change a tenth.

        So issue 329 bounds every January rather than reading any as exact.
        """
        assert all(pin[6] > 0 for pin in YEAR_ENDS)

    def test_the_sources_and_checks(self) -> None:
        assert dict(sorted(Counter(row.source for row in ROWS).items())) == SOURCES
        assert dict(sorted(Counter(row.check for row in ROWS).items())) == CHECKS


class TestTheManifestLines:
    """The ``sp600`` lines this panel recorded, beside issue 333's for the 2025-12-31 members."""

    def _lines(self) -> tuple[list[bytes], list[bytes]]:
        current = {row.ticker for row in ROWS if row.report_date == "2025-12-31"}
        lines = [
            line
            for line in (archive._manifest_path(None)).read_bytes().split(b"\n")
            if b'"cross_section"' in line
        ]
        theirs = [line for line in lines if json.loads(line)["symbol"] in current]
        mine = [line for line in lines if json.loads(line)["symbol"] not in current]
        return theirs, mine

    def test_the_2025_members_read_issue_333s_lines_and_nothing_else(self) -> None:
        theirs, _ = self._lines()
        current = {row.ticker for row in ROWS if row.report_date == "2025-12-31"}
        assert len(theirs) == len(current) == 603
        assert {json.loads(line)["symbol"] for line in theirs} == current

    def test_this_panel_recorded_896_lines_on_one_download_date(self) -> None:
        _, mine = self._lines()
        entries = [json.loads(line) for line in mine]
        assert len(mine) == 896
        assert sum(len(line) + 1 for line in mine) == 347_681
        assert sum(entry["row_count"] for entry in entries) == 3_653_318
        assert {entry["download_date"] for entry in entries} == {"2026-10-05"}
        digest = hashlib.sha256(b"".join(sorted(line + b"\n" for line in mine))).hexdigest()
        assert digest == "afcc113f0b023b1f7afe166e859402bf937e56af1ab7e65ec98e8304f8ebd5c3"

    def test_twelve_lines_hold_a_ticker_tried_and_then_replaced(self) -> None:
        _, mine = self._lines()
        mapped = {row.ticker for row in ROWS if row.ticker}
        unread = sorted(json.loads(line)["symbol"] for line in mine)
        assert [symbol for symbol in unread if symbol not in mapped] == [
            "ACI", "AMEH", "BELFA", "CBB-P-B", "CONN", "FRANQ",
            "GCI", "IACVV", "NYMTZ", "RJET", "SPW", "ZYXI",
        ]  # fmt: skip


class TestTheNqAllowance:
    def test_five_nq_passes_cannot_resolve_a_cent(self) -> None:
        """Half a dollar and half a share at the close exceeds a cent of price on few rows.

        The allowance resolves a cent only above 50 + 50 times the close shares.
        Biglari's three passes hold under 20,000 shares at over $300, and
        Cousins and Lumentum are one-share lots, which pass on almost any close.
        """
        forms = {filing.report_date: filing.form for filing in IJR.filings}
        loose = []
        for row in ROWS:
            if row.check != "pass" or forms[row.report_date] != "N-Q":
                continue
            holding = dict(numbered_members(IJR, row.report_date))[row.row]
            shares = Decimal(holding.shares)
            price = Decimal(holding.value) / shares
            if (HALF_UNIT["N-Q"] + price * HALF_SHARE["N-Q"]) / shares > Decimal("0.01"):
                loose.append((row.report_date, row.ticker, holding.shares))
        assert loose == [
            ("2009-12-31", "BH", "16102"),
            ("2010-12-31", "BH", "19996"),
            ("2012-12-31", "BH", "18993"),
            ("2016-12-31", "CUZ", "1"),
            ("2018-12-31", "LITE", "1"),
        ]


class TestTheCases:
    def test_a_reused_ticker_passes_laclede_and_fails_standard_register(self) -> None:
        laclede, standard = BY_KEY[("2009-12-31", 254)], BY_KEY[("2009-12-31", 317)]
        assert _name("2009-12-31", 254) == "Laclede Group Inc. (The)"
        assert _name("2009-12-31", 317) == "Standard Register Co. (The)"
        assert (laclede.ticker, laclede.check) == ("SR", "pass")
        assert (standard.ticker, standard.check, standard.gap) == ("SR", "price", "2867.00")

    def test_deckers_passes_on_its_as_traded_close_before_a_split(self) -> None:
        """Deckers split 3 for 1 on 2010-07-06. 169,442 shares at the 101.72 raw close is
        $17,235,640.24, the filing's $17,235,640, where the adjusted 5.65 would not be."""
        deckers = BY_KEY[("2009-12-31", 18)]
        assert _name("2009-12-31", 18) == "Deckers Outdoor Corp."
        assert (deckers.ticker, deckers.check) == ("DECK", "pass")


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

    def test_the_close_column_is_as_traded_across_deckers_split(self) -> None:
        store = _store()
        entries, closes = read_cross_section(
            "sp600", column="close", symbols=["DECK"], directory=store
        )
        _, adjusted = read_cross_section(
            "sp600", column="adjusted_close", symbols=["DECK"], directory=store
        )
        assert [entry.download_date for entry in entries] == ["2026-10-05"]
        assert closes.loc["2009-12-31", "DECK"] == 101.72
        assert adjusted.loc["2009-12-31", "DECK"] < 101.72 / 3


class TestTheCommand:
    def test_report_prints_one_line_per_year_end_then_every_missing_member(self, capsys) -> None:
        sp600_panel.main(["report"])
        out = capsys.readouterr().out
        lines = out.splitlines()
        assert [line.split()[0] for line in lines[:18]] == [pin[0] for pin in YEAR_ENDS]
        assert lines[17] == (
            "2025-12-31  members 603  covered 601  January stops 1  missing 2 (no-row 2)  "
            "price within a cent 0  threats 1"
        )
        assert lines[18] == "missing members:"
        assert len(lines) == 19 + sum(pin[1] - pin[2] for pin in YEAR_ENDS)
        assert (
            "  2009-12-31 row 317 SR: Standard Register Co. (The), price, threatens a tenth"
            in lines
        )
        assert sum(line.endswith(", threatens a tenth") for line in lines) == sum(
            pin[6] for pin in YEAR_ENDS
        )
        assert hashlib.sha256(out.encode()).hexdigest() == REPORT_SHA256

    def test_a_year_end_with_no_threat_is_marked_exact(self, monkeypatch) -> None:
        monkeypatch.setattr(sp600_panel, "threatening", lambda rows, year: [])
        lines = sp600_panel.report_lines(ROWS)
        assert lines[0].endswith("  threats 0  exact")
        assert not any(line.endswith("threatens a tenth") for line in lines)

    def test_fetch_hands_on_every_ticker_and_redacts_the_key(self, monkeypatch, capsys) -> None:
        handed = {}

        def fake_fetch(cross_section, symbols, *, key):
            handed.update(cross_section=cross_section, symbols=list(symbols), key=key)
            return fetch_alphavantage.Tally(recorded=["AAA"], failed=[f"X{key}"])

        monkeypatch.setenv("ALPHAVANTAGE_API_KEY", "SECRETKEY")
        monkeypatch.setattr(fetch_alphavantage, "fetch", fake_fetch)
        with pytest.raises(SystemExit) as stopped:
            sp600_panel.main(["fetch"])
        assert stopped.value.code == 1
        assert handed["cross_section"] == "sp600"
        assert handed["symbols"] == sp600_panel.tickers(ROWS)
        assert "" not in handed["symbols"]
        out = capsys.readouterr().out
        assert "SECRETKEY" not in out
        assert "X<key>" in out

    def test_a_complete_fetch_exits_cleanly(self, monkeypatch, capsys) -> None:
        monkeypatch.setenv("ALPHAVANTAGE_API_KEY", "SECRETKEY")
        monkeypatch.setattr(
            fetch_alphavantage, "fetch", lambda *a, **k: fetch_alphavantage.Tally(already=["A"])
        )
        sp600_panel.main(["fetch"])
        assert capsys.readouterr().out.startswith("recorded 0, already recorded 1")

    @pytest.mark.parametrize("refusal", [PanelRefused, archive.ArchiveRefused])
    def test_a_refusal_is_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*args, **kwargs):
            raise refusal("the one line")

        monkeypatch.setattr(sp600_panel, "load", refuse)
        with pytest.raises(SystemExit, match="^the one line$"):
            sp600_panel.main(["report"])

    def test_check_with_no_archive_prints_one_line(self, monkeypatch, tmp_path) -> None:
        monkeypatch.delenv("QT_ARCHIVE_DIR", raising=False)
        monkeypatch.setattr(archive, "ARCHIVE_DIR_CONFIG", tmp_path / "absent")
        with pytest.raises(SystemExit) as stopped:
            sp600_panel.main(["check"])
        assert str(stopped.value).startswith("no data archive is configured")

    def test_fetch_with_no_key_makes_no_request(self, monkeypatch) -> None:
        monkeypatch.delenv("ALPHAVANTAGE_API_KEY", raising=False)
        with pytest.raises(SystemExit, match="ALPHAVANTAGE_API_KEY is not set"):
            sp600_panel.main(["fetch"])

    def test_an_unknown_command_prints_the_usage(self) -> None:
        with pytest.raises(SystemExit, match="usage"):
            sp600_panel.main(["fetch", "now"])
