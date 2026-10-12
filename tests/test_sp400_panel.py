"""The pins for issue 303's S&P 400 panel and its S&P 600 control.

This file is the single authority for every number any prose surface quotes
about ``research/filings/ijh/members.csv`` and
``research/filings/ijr/members_2007-12-31.csv``.
[Issue 303](https://github.com/l3a0/quantitative-trading/issues/303) built
them.

**The specification.** A member is a row of the fund's 2007-12-31 schedule in
iShares Trust's N-Q, accession ``0001193125-08-043324``: IJH's 401 for the
S&P 400 and IJR's 602 for the control. Its ticker is the one the members file
maps it to. Its check is :func:`chan.fund_panel.check_members`'s: Alpha
Vantage's raw ``close`` on 2007-12-31 times the filing's share count, against
the filing's value, within half a dollar plus half a share at that close. The
calendar is the committed raw SPY vintage,
``yfinance_spy_raw_1993-01-29_2026-10-02_dl2026-10-03.csv``. A passing
member's 2006 history is :func:`chan.sp400_panel.history`'s, over the window
2006-01-03 to 2006-12-29 and the day before it, on the adjusted close and the
raw open. A flagged day is one :func:`chan.series.scale_breaks` reports on a
held member's own rows from 2005-12-01 to 2006-12-31, on the adjusted close
and on the adjusted open, which is the raw open times that day's adjusted
close over its raw close.

**The vintage.** IJH's closes are the ``sp400`` cross-section in
``data/archive_vintages.jsonl``, every line downloaded from Alpha Vantage with
``TIME_SERIES_DAILY_ADJUSTED`` on 2026-10-11. The control's are the ``sp600``
cross-section: its 509 rows shared with IJR's members file read the lines
issue 332 downloaded on 2026-10-05, and its 93 others read lines from either
date. The coverage pins read only the members files, whose sha256 they name,
so they run in CI. The pins that recompute the check or read 2006 read the
archive, and skip with the archive's own reason where there is none.

No pin here is a return, a profit or a Sharpe ratio. Issue 303 declares how
its run reads these panels before any such figure is computed.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter

import pandas as pd
import pytest

from chan import archive, fetch_alphavantage, fund_holdings, sp400_panel
from chan.archive import ArchiveUnavailable
from chan.fund_holdings import IJH, IJR, read_holdings, read_index
from chan.fund_panel import (
    MemberRow,
    PanelRefused,
    members_path,
    numbered_members,
    panel_keys,
    read_members,
    serialize_members,
)
from chan.series import load_panel, scale_breaks
from chan.sp400_panel import CONTROL, IJH_PANEL, History, history
from chan.vintage import SYMBOL_PATTERN

IJH_ROWS = read_members(IJH_PANEL.path)
CONTROL_ROWS = read_members(CONTROL.path)
ROWS = {"ijh": IJH_ROWS, "control": CONTROL_ROWS}

#: Each members file this module pins, by sha256.
MEMBERS_SHA256 = {
    "ijh": "ec0883763a2cc86304551517c3c725c489be220b376cad2d875732fe746f6f61",
    "control": "5bdb2d9238800ff5335fe88ecc9dab73d02e67de7a30e901759b1945fef1eb2b",
}

#: Per panel, each check's members and the filing's value they hold, in dollars.
VERDICTS = {
    "ijh": {
        "pass": (298, 3_792_198_350),
        "price": (7, 93_771_322),
        "no-row": (62, 650_209_215),
        "no-series": (34, 343_993_040),
        "unmapped": (0, 0),
    },
    "control": {
        "pass": (406, 3_145_789_754),
        "price": (13, 107_509_005),
        "no-row": (86, 486_873_085),
        "no-series": (97, 647_474_072),
        "unmapped": (0, 0),
    },
}

#: Per panel, the filing's value of every member, which the verdicts sum to.
TOTALS = {"ijh": 4_880_171_927, "control": 4_387_645_916}

#: Per panel, how many rows each mapping source answered.
SOURCES = {"ijh": {"hand": 100, "name": 301}, "control": {"hand": 55, "link": 509, "name": 38}}

#: Per panel, the report's whole output, by sha256.
REPORT_SHA256 = {
    "ijh": "5159dc834719e2e3b7dc28412b94e1baa86fe149d0da190de653628d46d1ce22",
    "control": "97f98fb6e9be3644f55740301079a94bf03991cac738448f1439d26b23e2aa7d",
}


class TestIjhsFiling:
    """IJH's schedule in the 2007-12-31 N-Q, recorded by chan.fund_holdings."""

    def test_the_list_holds_the_one_filing_ijr_reads_from_the_same_n_q(self) -> None:
        assert [(f.report_date, f.accession, f.document) for f in IJH.filings] == [
            ("2007-12-31", "0001193125-08-043324", "dnq.htm")
        ]
        assert IJH.filings[0].accession == IJR.filings[0].accession
        assert IJH.series_id == "S000004307"
        assert IJH.schedule_names == ("S&P MIDCAP 400 INDEX FUND",)

    def test_401_holdings_sum_to_the_total_the_schedule_prints(self) -> None:
        entry = next(e for e in read_index() if e.fund == "IJH")
        held = read_holdings(fund_holdings.FILINGS_DIR / entry.path)
        assert (entry.row_count, len(held)) == (401, 401)
        assert entry.printed_total == sum(int(h.value) for h in held) == 4_880_171_927

    def test_its_document_is_the_one_ijrs_line_pins(self) -> None:
        lines = {e.fund: e for e in read_index() if e.accession == "0001193125-08-043324"}
        assert lines["IJH"].document_sha256 == lines["IJR"].document_sha256

    def test_the_panel_is_the_whole_filing(self) -> None:
        """A fund read from one filing yields no rows from panel_keys without whole_first."""
        assert sp400_panel.keys(IJH_PANEL) == panel_keys(IJH, whole_first=True)
        assert panel_keys(IJH) == []


class TestTheRuling:
    def test_sp400_is_ruled_into_the_archive_and_is_the_panels_cross_section(self) -> None:
        assert "sp400" in archive.CROSS_SECTIONS
        archive.require_ruled("sp400")
        assert (IJH_PANEL.cross_section, CONTROL.cross_section) == ("sp400", "sp600")


@pytest.mark.parametrize("name", ["ijh", "control"])
class TestTheMembersFiles:
    def test_the_file_is_the_one_these_pins_were_measured_on(self, name: str) -> None:
        path = sp400_panel.PANELS[name].path
        assert hashlib.sha256(path.read_bytes()).hexdigest() == MEMBERS_SHA256[name]

    def test_it_holds_every_member_of_the_filing_once_in_order(self, name: str) -> None:
        panel = sp400_panel.PANELS[name]
        assert [row.key for row in ROWS[name]] == sp400_panel.keys(panel)
        assert sp400_panel.load(panel) == ROWS[name]

    def test_it_is_what_the_writer_writes(self, name: str) -> None:
        assert serialize_members(ROWS[name]) == sp400_panel.PANELS[name].path.read_bytes()

    def test_every_ticker_is_a_symbol_and_every_lookup_names_its_evidence(self, name: str) -> None:
        rows = ROWS[name]
        assert all(SYMBOL_PATTERN.fullmatch(row.ticker) for row in rows if row.ticker)
        assert all(row.note for row in rows if row.source in ("hand", "name"))

    def test_every_row_is_checked_and_no_two_pass_on_one_ticker(self, name: str) -> None:
        rows = ROWS[name]
        assert all(row.check for row in rows)
        passing = [row.ticker for row in rows if row.check == "pass"]
        assert len(passing) == len(set(passing))

    def test_each_check_holds_its_pinned_members_and_value(self, name: str) -> None:
        panel = sp400_panel.PANELS[name]
        verdicts = sp400_panel.verdicts(panel, ROWS[name])
        assert {v.check: (v.members, v.value) for v in verdicts} == VERDICTS[name]
        filed = sum(int(h.value) for _, h in numbered_members(panel.fund, "2007-12-31"))
        assert sum(v.value for v in verdicts) == filed == TOTALS[name]

    def test_the_sources(self, name: str) -> None:
        assert dict(sorted(Counter(row.source for row in ROWS[name]).items())) == SOURCES[name]

    def test_the_report_is_pinned(self, name: str, capsys) -> None:
        sp400_panel.main(["report", name])
        out = capsys.readouterr().out
        assert hashlib.sha256(out.encode()).hexdigest() == REPORT_SHA256[name]
        assert sum(line.startswith("  row ") for line in out.splitlines()) == sum(
            row.check != "pass" for row in ROWS[name]
        )


class TestTheControl:
    def test_its_509_shared_rows_are_ijrs_members_file_as_it_stands(self) -> None:
        shared = {row.key: row for row in read_members(members_path(IJR))}
        mine = [row for row in CONTROL_ROWS if row.key in shared]
        assert len(mine) == 509
        assert all(row == shared[row.key] for row in mine)

    def test_the_93_others_are_what_ijrs_file_leaves_out(self) -> None:
        shared = {row.key for row in read_members(members_path(IJR))}
        others = [row for row in CONTROL_ROWS if row.key not in shared]
        assert len(others) == 93
        assert Counter(row.check for row in others) == Counter(
            {"pass": 38, "no-series": 31, "no-row": 21, "price": 3}
        )

    def test_its_fetch_asks_only_for_the_tickers_of_the_93(self) -> None:
        shared = {row.key for row in read_members(members_path(IJR))}
        others = {row.ticker for row in CONTROL_ROWS if row.key not in shared and row.ticker}
        assert sp400_panel.fetch_symbols(CONTROL, CONTROL_ROWS) == sorted(others)
        assert sp400_panel.fetch_symbols(IJH_PANEL, IJH_ROWS) == sp400_panel.tickers(IJH_ROWS)


def _lines(cross_section: str, download_date: str) -> list[bytes]:
    return [
        line
        for line in archive._manifest_path(None).read_bytes().split(b"\n")
        if line.strip()
        and json.loads(line).get("cross_section") == cross_section
        and json.loads(line)["download_date"] == download_date
    ]


class TestTheManifestLines:
    """The lines issue 303 recorded on 2026-10-11, in sp400 and in sp600 for the control."""

    @pytest.mark.parametrize(
        ("cross_section", "count", "size", "rows", "digest"),
        [
            (
                "sp400", 367, 142_162, 1_865_549,
                "2188e6d1eddfe7a6cf97ab5da199e3c932a80badf8f6d917f3a0a2b7f6c136db",
            ),
            (
                "sp600", 44, 17_064, 158_240,
                "2132821cd03f1b4c5bb4df721095b597cbdeb5f1ea5ef747a827e519257d9d19",
            ),
        ],
    )  # fmt: skip
    def test_the_lines_by_count_bytes_rows_and_sha256(
        self, cross_section: str, count: int, size: int, rows: int, digest: str
    ) -> None:
        lines = _lines(cross_section, "2026-10-11")
        entries = [json.loads(line) for line in lines]
        assert len(lines) == count
        assert sum(len(line) + 1 for line in lines) == size
        assert sum(entry["row_count"] for entry in entries) == rows
        assert min(entry["first_date"] for entry in entries) == "1999-11-01"
        assert max(entry["last_date"] for entry in entries) == "2026-10-09"
        joined = b"".join(sorted(line + b"\n" for line in lines))
        assert hashlib.sha256(joined).hexdigest() == digest

    def test_sp400_holds_every_ijh_ticker_but_those_alpha_vantage_has_no_series_for(
        self,
    ) -> None:
        recorded = {json.loads(line)["symbol"] for line in _lines("sp400", "2026-10-11")}
        mapped = set(sp400_panel.tickers(IJH_ROWS))
        assert recorded <= mapped
        assert mapped - recorded == {row.ticker for row in IJH_ROWS if row.check == "no-series"}
        assert len(mapped - recorded) == 34

    def test_every_ijh_series_with_no_row_on_2007_12_31_starts_after_it(self) -> None:
        """So each of the 62 is a later series under the ticker, not a gap in an older one.

        Read from the ``sp400`` lines of 2026-10-11 alone, with no archive.
        DRS and LEA are the two examples Entry 50 names.
        """
        first = {
            json.loads(line)["symbol"]: json.loads(line)["first_date"]
            for line in _lines("sp400", "2026-10-11")
        }
        no_row = [row.ticker for row in IJH_ROWS if row.check == "no-row"]
        assert len(no_row) == 62
        assert all(first[ticker] > sp400_panel.REPORT_DATE for ticker in no_row)
        assert (first["DRS"], first["LEA"]) == ("2022-11-29", "2009-11-09")

    def test_sp600_gained_lines_only_for_tickers_the_controls_93_rows_map(self) -> None:
        recorded = {json.loads(line)["symbol"] for line in _lines("sp600", "2026-10-11")}
        assert recorded <= set(sp400_panel.fetch_symbols(CONTROL, CONTROL_ROWS))


class TestHistory:
    """The 2006 history rule on a calendar of the day before the window and four days."""

    DAYS = pd.DatetimeIndex(
        [
            "2005-12-29",
            "2005-12-30",
            "2006-01-03",
            "2006-06-01",
            "2006-12-28",
            "2006-12-29",
            "2007-01-03",
        ]
    )
    NAN = float("nan")

    def _kind(self, closes: list[float], opens: list[float] | None = None) -> str:
        row = MemberRow("2007-12-31", 1, "AAA", "hand", "x", "pass", "", "close")
        frame = pd.DataFrame({"AAA": closes}, index=self.DAYS)
        opened = pd.DataFrame({"AAA": closes if opens is None else opens}, index=self.DAYS)
        return history([row], frame, opened, self.DAYS)[0].kind

    def test_every_day_with_a_close_and_an_open_is_full(self) -> None:
        assert self._kind([1.0] * 7) == "full"

    def test_a_missing_open_inside_the_window_is_partial(self) -> None:
        assert self._kind([1.0] * 7, [1, 1, 1, self.NAN, 1, 1, 1]) == "partial"

    def test_a_missing_close_on_the_day_before_the_window_is_partial(self) -> None:
        assert self._kind([1, self.NAN, 1, 1, 1, 1, 1]) == "partial"

    def test_a_first_row_inside_the_window_is_listed(self) -> None:
        assert self._kind([self.NAN] * 3 + [1.0] * 4) == "listed"

    def test_a_first_row_on_the_vendors_start_is_cut(self) -> None:
        assert self._kind([self.NAN] * 4 + [1.0] * 3) == "cut"

    def test_a_first_row_after_the_vendors_start_is_cut_rather_than_listed(self) -> None:
        """A series the vendor starts on 2006-12-29 is cut too, not a listing."""
        assert self._kind([self.NAN] * 5 + [1.0] * 2) == "cut"

    def test_no_row_inside_the_window_is_absent(self) -> None:
        assert self._kind([self.NAN] * 6 + [1.0]) == "absent"

    def test_a_row_that_did_not_pass_has_no_history(self) -> None:
        row = MemberRow("2007-12-31", 1, "AAA", "hand", "x", "no-row")
        frame = pd.DataFrame({"AAA": [1.0] * 7}, index=self.DAYS)
        assert history([row], frame, frame, self.DAYS) == []

    def test_a_run_holds_full_partial_and_listed(self) -> None:
        entries = [
            History(("2007-12-31", n), "A", pd.Timestamp("2001-01-02"), 1, 1, kind)
            for n, kind in enumerate(sp400_panel.HISTORIES, start=1)
        ]
        assert sp400_panel.panel_keys(entries) == [("2007-12-31", n) for n in (1, 2, 3)]


class TestTheVendorsStart:
    """Why a series starting on 2006-12-28 is read as the vendor's cut-off.

    The vintage is ``data/archive_vintages.jsonl``'s ``sp600`` lines that
    issue 332 downloaded from Alpha Vantage with ``TIME_SERIES_DAILY_ADJUSTED``
    on 2026-10-05, and Chan's ``IJR_20080114.mat`` as committed under
    ``data/ijr_20080114/``. The specification is a line whose ``first_date``
    is :data:`chan.sp400_panel.VENDOR_START`, and a close in Chan's file on
    every one of 2006's 251 trading days. Neither needs the archive.
    """

    def test_fifteen_sp600_series_recorded_on_2026_10_05_begin_on_it(self) -> None:
        symbols = sorted(
            json.loads(line)["symbol"]
            for line in _lines("sp600", "2026-10-05")
            if json.loads(line)["first_date"] == sp400_panel.VENDOR_START
        )
        assert symbols == [
            "AGP", "CGX", "CHB", "HOTT", "JAS", "JDAS", "MFB", "OMX",
            "PEET", "PLFE", "PMTI", "PRX", "TGX", "TWB", "WBSN",
        ]  # fmt: skip

    def test_chans_file_prices_13_of_them_on_every_day_of_2006(self) -> None:
        symbols = {
            json.loads(line)["symbol"]
            for line in _lines("sp600", "2026-10-05")
            if json.loads(line)["first_date"] == sp400_panel.VENDOR_START
        }
        _, chan = load_panel("IJR_20080114.mat")
        year = chan.loc["2006-01-01":"2006-12-31"]
        assert len(year) == 251
        whole = sorted(s for s in symbols if s in year and year[s].notna().all())
        assert len(whole) == 13
        assert sorted(symbols - set(whole)) == ["OMX", "PRX"]


class TestTheBindings:
    def test_load_refuses_a_file_missing_a_member(self, tmp_path) -> None:
        short = tmp_path / "members.csv"
        short.write_bytes(serialize_members(IJH_ROWS[1:]))
        with pytest.raises(PanelRefused, match="lacks 1 it does"):
            sp400_panel.load(IJH_PANEL, short)

    def test_an_unchecked_row_is_refused_by_the_verdicts(self) -> None:
        rows = [MemberRow("2007-12-31", 1, "GYI", "hand", "x")]
        with pytest.raises(PanelRefused, match="row 1 has not been checked"):
            sp400_panel.verdicts(IJH_PANEL, rows)

    def test_fetch_hands_on_the_panels_tickers_and_redacts_the_key(
        self, monkeypatch, capsys
    ) -> None:
        handed = {}

        def fake_fetch(cross_section, symbols, *, key):
            handed.update(cross_section=cross_section, symbols=list(symbols))
            return fetch_alphavantage.Tally(recorded=["AAA"], failed=[f"X{key}"])

        monkeypatch.setenv("ALPHAVANTAGE_API_KEY", "SECRETKEY")
        monkeypatch.setattr(fetch_alphavantage, "fetch", fake_fetch)
        with pytest.raises(SystemExit) as stopped:
            sp400_panel.main(["fetch", "ijh"])
        assert stopped.value.code == 1
        assert handed == {"cross_section": "sp400", "symbols": sp400_panel.tickers(IJH_ROWS)}
        out = capsys.readouterr().out
        assert "SECRETKEY" not in out and "X<key>" in out

    def test_fetch_with_no_key_makes_no_request(self, monkeypatch) -> None:
        monkeypatch.delenv("ALPHAVANTAGE_API_KEY", raising=False)
        with pytest.raises(SystemExit, match="ALPHAVANTAGE_API_KEY is not set"):
            sp400_panel.main(["fetch", "control"])

    def test_check_with_no_archive_prints_one_line(self, monkeypatch, tmp_path) -> None:
        monkeypatch.delenv("QT_ARCHIVE_DIR", raising=False)
        monkeypatch.setattr(archive, "ARCHIVE_DIR_CONFIG", tmp_path / "absent")
        with pytest.raises(SystemExit) as stopped:
            sp400_panel.main(["check", "ijh"])
        assert str(stopped.value).startswith("no data archive is configured")

    @pytest.mark.parametrize("argv", [["report"], ["report", "sp400"], ["run", "ijh"]])
    def test_an_unknown_command_or_panel_prints_the_usage(self, argv) -> None:
        with pytest.raises(SystemExit, match="usage"):
            sp400_panel.main(argv)


def _store():
    try:
        return archive.archive_dir()
    except ArchiveUnavailable as absent:
        pytest.skip(str(absent))


#: Per panel, the passing members by 2006 history, and how many a run holds.
HISTORY_COUNTS = {
    "ijh": ({"full": 272, "partial": 10, "listed": 3, "cut": 10, "absent": 3}, 285),
    "control": ({"full": 370, "partial": 14, "listed": 1, "cut": 17, "absent": 4}, 385),
}

#: Per panel, every passing member a run leaves out, as ticker and first row,
#: by history: ``cut`` on the vendor's start and ``absent`` with no 2006 row.
LEFT_OUT = {
    "ijh": {
        "cut": dict.fromkeys("TBL VCI JEF-1 MFE BLC PXP NTY PRX NDN SKS".split(), "2006-12-28"),
        "absent": {"PALM": "2007-10-25", "EXH": "2007-08-21", "BR": "2007-04-02"},
    },
    "control": {
        "cut": dict.fromkeys(
            "MFB PEET CGX SHAW RAH PMTI AGP CHB MNC PLFE WBSN TGX HOTT JAS TWB JDAS DITC".split(),
            "2006-12-28",
        ),
        "absent": {
            "ZEP": "2007-11-01",
            "SUG": "2007-09-26",
            "CENTA": "2007-02-06",
            "FOR": "2007-12-13",
        },
    },
}

#: Per panel, the members listed during 2006, which a run holds.
LISTED = {"ijh": ["CMG", "HBI", "KBR"], "control": ["CROX"]}

#: Per panel, the fewest and most of the window's 251 days a partial member
#: holds, on the close and on the open alike.
PARTIAL_DAYS = {"ijh": (244, 250), "control": (247, 250)}

#: Per panel, every flagged day, as ticker and day, the same on both prices.
FLAGGED = {
    "ijh": [("KCI", "2006-08-04")],
    "control": [
        ("CORSQ", "2006-05-19"),
        ("MAG", "2006-01-10"),
        ("MAG", "2006-01-11"),
        ("ZD", "2006-05-25"),
    ],
}


@pytest.mark.parametrize("name", ["ijh", "control"])
class TestTheArchive:
    """Runs only where an archive is configured. No figure here is a return."""

    def _read(self, name: str):
        store = _store()
        try:
            adjusted, opens, adjusted_opens = sp400_panel.frames(
                sp400_panel.PANELS[name], ROWS[name], directory=store
            )
        except ArchiveUnavailable as absent:
            pytest.skip(str(absent))
        entries = history(ROWS[name], adjusted, opens, sp400_panel.calendar())
        return adjusted, adjusted_opens, entries

    def test_the_committed_check_is_what_the_archive_gives(self, name: str) -> None:
        store = _store()
        try:
            recomputed = sp400_panel.check(sp400_panel.PANELS[name], directory=store)
        except ArchiveUnavailable as absent:
            pytest.skip(str(absent))
        assert tuple(recomputed) == ROWS[name]

    def test_the_2006_histories(self, name: str) -> None:
        _, _, entries = self._read(name)
        kinds, held = HISTORY_COUNTS[name]
        assert Counter(entry.kind for entry in entries) == Counter(kinds)
        assert len(sp400_panel.panel_keys(entries)) == held

    def test_the_passing_members_a_run_leaves_out(self, name: str) -> None:
        """The tickers and first rows ``history`` prints, on the vintage above."""
        _, _, entries = self._read(name)
        for kind, wanted in LEFT_OUT[name].items():
            found = {e.ticker: e.first.date().isoformat() for e in entries if e.kind == kind}
            assert found == wanted, kind

    def test_the_members_listed_during_2006(self, name: str) -> None:
        _, _, entries = self._read(name)
        assert sorted(e.ticker for e in entries if e.kind == "listed") == LISTED[name]

    def test_the_partial_members_fewest_and_most_days(self, name: str) -> None:
        """Out of the window's 251, so IJH's partial members miss 1 to 7 days."""
        _, _, entries = self._read(name)
        partial = [e for e in entries if e.kind == "partial"]
        assert all(e.closes == e.opens for e in partial)
        assert (min(e.closes for e in partial), max(e.closes for e in partial)) == (
            PARTIAL_DAYS[name]
        )

    def test_the_flagged_days_on_both_prices(self, name: str) -> None:
        adjusted, adjusted_opens, entries = self._read(name)
        held = sorted({entry.ticker for entry in entries if entry.kind in sp400_panel.HELD})
        for frame in (adjusted, adjusted_opens):
            found = []
            for ticker in held:
                own = frame[ticker].dropna().loc["2005-12-01":"2006-12-31"]
                found += [(ticker, day.date().isoformat()) for day in scale_breaks(own)]
            assert found == FLAGGED[name]

    def test_the_2006_days_are_chans_two_files_days_on_both_prices(self, name: str) -> None:
        """So chan.khandani_lo_small_caps.same_days holds as written for these runs."""
        adjusted, adjusted_opens, entries = self._read(name)
        held = sorted({entry.ticker for entry in entries if entry.kind in sp400_panel.HELD})
        mine = adjusted[held].loc["2006-01-01":"2006-12-31"].index
        assert len(mine) == 251
        assert adjusted_opens[held].loc["2006-01-01":"2006-12-31"].index.equals(mine)
        for source in ("SPX_20071123.mat", "IJR_20080114.mat"):
            for field in ("Close", "Open"):
                _, chan = load_panel(source, field=field)
                assert chan.loc["2006-01-01":"2006-12-31"].index.equals(mine), (source, field)
