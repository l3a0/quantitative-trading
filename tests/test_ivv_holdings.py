"""The pins for IVV's quarter-end holdings, read from its SEC filings.

[Issue 372](https://github.com/l3a0/quantitative-trading/issues/372) is the
scope. IVV is iShares' S&P 500 fund, and this record is what
[issue 373](https://github.com/l3a0/quantitative-trading/issues/373) builds the
S&P 500 panel from. This file is the single authority for every number any
prose surface quotes about ``research/filings/ivv/``. It needs no network.
Every pin reads the committed record, and every parser test reads a few rows
cut from the real document, under ``tests/fixtures/filings/``.

**What pins a number here is the accession rather than a vintage**, for the
reason ``tests/test_fund_holdings.py`` gives. The record was written on
2026-10-05 from the documents downloaded from EDGAR that day.

**The specification.** A row is a row under common stocks: an HTML schedule's
rows from IVV's "Common Stocks" line to its "Total Common Stocks" line, and an
N-PORT's ``invstOrSec`` rows whose ``assetCat`` is ``EC``. A member is a row
not on :data:`chan.fund_holdings.IVV`'s list of non-stock rows. A member is
linked when :func:`chan.fund_holdings.link` pairs it with a member of the
recorded schedule before it, which for 2013-12-31 is 2013-06-30's, because
2013-09-30 has no full schedule.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from chan import fund_holdings
from chan.fund_holdings import (
    IJR,
    IVV,
    FilingRefused,
    Holding,
    link,
    members,
    parse,
    parse_nport,
    parse_nq,
    place,
    read_holdings,
    read_index,
    record,
)

FIXTURES = Path(__file__).parent / "fixtures" / "filings"

#: Per quarter-end with a full schedule: report date, form, accession, rows
#: under common stocks, members, members linked to the schedule before,
#: members left unlinked, and the "Total Common Stocks" an HTML schedule
#: prints. The first schedule has nothing before it, so it links nobody.
QUARTER_ENDS = (
    ("2008-12-31", "N-Q", "0001193125-09-040696", 500, 500, None, None, 15_609_267_288),
    ("2009-03-31", "N-CSR", "0001193125-09-126206", 500, 500, 488, 12, 14_709_010_567),
    ("2009-06-30", "N-Q", "0001193125-09-183934", 502, 502, 496, 6, 18_329_902_038),
    ("2009-09-30", "N-CSRS", "0001193125-09-248357", 500, 500, 496, 4, 20_453_650_777),
    ("2009-12-31", "N-Q", "0001193125-10-044578", 500, 500, 491, 9, 21_781_415_066),
    ("2010-03-31", "N-CSR", "0001193125-10-133919", 500, 500, 492, 8, 22_748_508_357),
    ("2010-06-30", "N-Q", "0001193125-10-199353", 500, 500, 496, 4, 20_504_439_353),
    ("2010-09-30", "N-CSRS", "0001193125-10-277292", 500, 500, 495, 5, 22_642_774_716),
    ("2010-12-31", "N-Q", "0001193125-11-052046", 500, 500, 495, 5, 25_726_771_938),
    ("2011-03-31", "N-CSR", "0001193125-11-162711", 501, 501, 495, 6, 26_990_122_663),
    ("2011-06-30", "N-Q", "0001193125-11-235651", 499, 499, 495, 4, 27_572_962_353),
    ("2011-09-30", "N-CSRS", "0001193125-11-336349", 500, 500, 495, 5, 23_819_500_558),
    ("2011-12-31", "N-Q", "0001193125-12-088646", 500, 500, 488, 12, 26_168_508_403),
    ("2012-03-31", "N-CSR", "0001193125-12-264907", 500, 500, 497, 3, 29_955_490_375),
    ("2012-06-30", "N-Q", "0001193125-12-373715", 501, 501, 491, 10, 29_751_845_287),
    ("2012-09-30", "N-CSRS", "0001193125-12-494940", 501, 501, 498, 3, 31_702_434_377),
    ("2012-12-31", "N-Q", "0001193125-13-086998", 500, 500, 491, 9, 34_986_901_401),
    ("2013-03-31", "N-CSR", "0001193125-13-251330", 500, 500, 496, 4, 40_910_716_871),
    ("2013-06-30", "N-Q", "0001193125-13-351768", 500, 500, 493, 7, 42_845_287_874),
    ("2013-12-31", "N-Q", "0001193125-14-076476", 500, 500, 482, 18, 53_614_771_251),
    ("2014-03-31", "N-CSR", "0001193125-14-230537", 500, 500, 498, 2, 54_249_541_318),
    ("2014-06-30", "N-Q", "0001193125-14-327134", 502, 502, 491, 11, 57_750_612_466),
    ("2014-09-30", "N-CSRS", "0001193125-14-434445", 502, 502, 495, 7, 60_968_227_775),
    ("2014-12-31", "N-Q", "0001193125-15-065725", 502, 502, 496, 6, 70_654_668_853),
    ("2015-03-31", "N-CSR", "0001193125-15-216083", 502, 502, 487, 15, 68_604_526_051),
    ("2015-06-30", "N-Q", "0001193125-15-306363", 502, 502, 494, 8, 67_659_229_676),
    ("2015-09-30", "N-CSRS", "0001193125-15-396474", 505, 505, 488, 17, 63_672_220_307),
    ("2015-12-31", "N-Q", "0001193125-16-480933", 504, 504, 497, 7, 70_149_235_344),
    ("2016-03-31", "N-CSR", "0001193125-16-613829", 504, 504, 492, 12, 70_976_021_930),
    ("2016-06-30", "N-Q", "0001193125-16-695276", 507, 507, 492, 15, 73_038_716_739),
    ("2016-09-30", "N-CSRS", "0001193125-16-788378", 505, 505, 497, 8, 79_438_644_848),
    ("2016-12-31", "N-Q", "0001193125-17-065125", 505, 505, 500, 5, 90_349_833_188),
    ("2017-03-31", "N-CSR", "0001193125-17-194722", 505, 505, 494, 11, 101_590_682_821),
    ("2017-06-30", "N-Q", "0001193125-17-271743", 505, 505, 496, 9, 115_574_753_071),
    ("2017-09-30", "N-CSRS", "0001193125-17-359934", 505, 505, 493, 12, 126_632_851_799),
    ("2017-12-31", "N-Q", "0001193125-18-063612", 504, 504, 499, 5, 141_075_921_279),
    ("2018-03-31", "N-CSR", "0001193125-18-186572", 505, 505, 497, 8, 140_073_478_583),
    ("2018-06-30", "N-Q", "0001193125-18-261300", 505, 505, 493, 12, 148_253_964_464),
    ("2018-09-30", "N-CSRS", "0001193125-18-344229", 506, 506, 503, 3, 164_845_892_126),
    ("2018-12-31", "N-Q", "0001193125-19-059323", 506, 506, 495, 11, 149_219_092_430),
    ("2019-03-31", "N-CSR", "0001193125-19-167652", 505, 505, 499, 6, 168_918_569_125),
    ("2019-06-30", "NPORT-EX", "0001752724-19-108752", 505, 505, 498, 7, 176_338_648_537),
    ("2019-09-30", "NPORT-P", "0001752724-19-177847", 505, 505, 487, 18, None),
    ("2019-12-31", "NPORT-P", "0001752724-20-038725", 505, 505, 494, 11, None),
    ("2020-03-31", "NPORT-P", "0001752724-20-112027", 505, 505, 502, 3, None),
    ("2020-06-30", "NPORT-P", "0001752724-20-176909", 505, 505, 494, 11, None),
    ("2020-09-30", "NPORT-P", "0001752724-20-247818", 505, 505, 501, 4, None),
    ("2020-12-31", "NPORT-P", "0001752724-21-040719", 505, 505, 501, 4, None),
    ("2021-03-31", "NPORT-P", "0001752724-21-116363", 505, 505, 495, 10, None),
    ("2021-06-30", "NPORT-P", "0001752724-21-186201", 505, 505, 501, 4, None),
    ("2021-09-30", "NPORT-P", "0001752724-21-255857", 505, 505, 498, 7, None),
    ("2021-12-31", "NPORT-P", "0001752724-22-046281", 505, 505, 501, 4, None),
    ("2022-03-31", "NPORT-P", "0001752724-22-122805", 505, 505, 501, 4, None),
    ("2022-06-30", "NPORT-P", "0001752724-22-193652", 505, 504, 498, 6, None),
    ("2022-09-30", "NPORT-P", "0001752724-22-268673", 503, 503, 500, 3, None),
    ("2022-12-31", "NPORT-P", "0001752724-23-039243", 503, 503, 497, 6, None),
    ("2023-03-31", "NPORT-P", "0001752724-23-123220", 503, 503, 499, 4, None),
    ("2023-06-30", "NPORT-P", "0001752724-23-191503", 503, 503, 501, 2, None),
    ("2023-09-30", "NPORT-P", "0001752724-23-264277", 503, 503, 499, 4, None),
    ("2023-12-31", "NPORT-P", "0001752724-24-043113", 503, 503, 496, 7, None),
    ("2024-03-31", "NPORT-P", "0001752724-24-123331", 503, 503, 499, 4, None),
    ("2024-06-30", "NPORT-P", "0001752724-24-194289", 503, 503, 496, 7, None),
    ("2024-09-30", "NPORT-P", "0001752724-24-269943", 504, 504, 498, 6, None),
    ("2024-12-31", "NPORT-P", "0001752724-25-043800", 503, 503, 495, 8, None),
    ("2025-03-31", "NPORT-P", "0001752724-25-119791", 504, 504, 499, 5, None),
    ("2025-06-30", "NPORT-P", "0001752724-25-210389", 504, 504, 502, 2, None),
    ("2025-09-30", "NPORT-P/A", "0002071691-26-015790", 503, 503, 495, 8, None),
    ("2025-12-31", "NPORT-P", "0002071691-26-004238", 503, 503, 497, 6, None),
    ("2026-03-31", "NPORT-P", "0002071691-26-012459", 503, 503, 498, 5, None),
    ("2026-06-30", "NPORT-P", "0002071691-26-019760", 503, 503, 494, 9, None),
)

HTML_FORMS = ("N-Q", "N-CSR", "N-CSRS", "NPORT-EX")

#: The one date on the list with no holdings file.
SKIPPED = "2013-09-30"


def _filing(report_date: str) -> fund_holdings.Filing:
    return next(filing for filing in IVV.filings if filing.report_date == report_date)


def _held(report_date: str) -> tuple[Holding, ...]:
    return read_holdings(fund_holdings.holdings_path(IVV, _filing(report_date)))


def _entry(report_date: str) -> fund_holdings.IndexEntry:
    return next(e for e in read_index() if e.fund == "IVV" and e.report_date == report_date)


def _fixture(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


def _quarter_ends(first: str, last: str) -> list[str]:
    ends = ("03-31", "06-30", "09-30", "12-31")
    year, dates = int(first[:4]), []
    while not dates or dates[-1] != last:
        dates += [f"{year}-{end}" for end in ends if first <= f"{year}-{end}" <= last]
        year += 1
    return dates


# --- The committed list ------------------------------------------------------


class TestTheList:
    def test_every_quarter_end_from_2008_to_2026_is_listed_once(self) -> None:
        listed = [filing.report_date for filing in IVV.filings]
        assert listed == _quarter_ends("2008-12-31", "2026-06-30")
        assert len(listed) == 71

    def test_the_seventy_recorded_dates_are_the_pinned_ones(self) -> None:
        recorded = [(f.report_date, f.form, f.accession) for f in IVV.filings if not f.skipped]
        assert recorded == [row[:3] for row in QUARTER_ENDS]
        assert len(recorded) == 70

    def test_the_form_follows_the_fiscal_year_ending_march_31(self) -> None:
        for filing in IVV.filings:
            date, month = filing.report_date, filing.report_date[5:]
            if date == "2019-06-30":
                expected = "NPORT-EX"
            elif date == "2025-09-30":
                expected = "NPORT-P/A"
            elif date >= "2019-09-30":
                expected = "NPORT-P"
            else:
                expected = {"03-31": "N-CSR", "09-30": "N-CSRS"}.get(month, "N-Q")
            assert filing.form == expected, date

    def test_each_december_nq_is_the_accession_ijrs_list_names(self) -> None:
        # One N-Q holds every fund in the trust, so the index tells the two
        # funds' lines apart by fund as well as by accession.
        ijr = {f.report_date: f.accession for f in IJR.filings}
        shared = [f for f in IVV.filings if f.form == "N-Q" and f.report_date.endswith("12-31")]
        assert len(shared) == 11
        assert all(ijr[f.report_date] == f.accession for f in shared)


class TestTheSkippedDate:
    def test_2013_09_30_is_skipped_because_its_schedule_is_a_summary(self) -> None:
        skipped = [filing for filing in IVV.filings if filing.skipped]
        assert [f.report_date for f in skipped] == [SKIPPED]
        assert skipped[0].form == "N-CSRS"
        assert skipped[0].accession == "0001193125-13-466531"
        assert "summary schedule of 55 holdings" in skipped[0].skipped

    def test_nothing_is_written_for_it(self) -> None:
        assert not fund_holdings.holdings_path(IVV, _filing(SKIPPED)).exists()
        assert SKIPPED not in {e.report_date for e in read_index() if e.fund == "IVV"}

    def test_reading_its_members_names_the_reason(self) -> None:
        with pytest.raises(ValueError, match="no holdings file: the N-CSRS prints a summary"):
            members(IVV, _filing(SKIPPED))

    def test_the_writer_refuses_it(self, tmp_path: Path) -> None:
        with pytest.raises(FilingRefused, match="2013-09-30 is skipped: the N-CSRS"):
            record(IVV, _filing(SKIPPED), b"", tmp_path)
        assert not any(tmp_path.iterdir())

    def test_the_fetch_never_downloads_it(self, tmp_path: Path, monkeypatch) -> None:
        asked = []
        monkeypatch.setattr(fund_holdings, "record", lambda *arguments: None)
        fund = fund_holdings.Fund("IVV", IVV.series_id, (), IVV.filings[18:21], ())
        fund_holdings.fetch(
            fund,
            filings_dir=tmp_path,
            contact="n@example.com",
            download=lambda url, contact: asked.append(url) or b"",
            pause=lambda seconds: None,
        )
        assert [f.report_date for f in fund.filings] == ["2013-06-30", SKIPPED, "2013-12-31"]
        assert asked == [fund_holdings.document_url(f) for f in fund.filings if not f.skipped]

    def test_a_placement_reaching_back_to_it_names_the_reason(self) -> None:
        with pytest.raises(ValueError, match="2013-09-30 has no holdings file"):
            place(IVV, "2013-12-31")


# --- The committed record ----------------------------------------------------


class TestTheCommittedRecord:
    def test_the_index_holds_one_line_per_recorded_filing(self) -> None:
        lines = [e for e in read_index() if e.fund == "IVV"]
        assert [(e.report_date, e.form, e.accession) for e in lines] == [
            row[:3] for row in QUARTER_ENDS
        ]
        recorded = [filing for filing in IVV.filings if not filing.skipped]
        for entry, filing in zip(lines, recorded, strict=True):
            assert entry.series_id == "S000004310"
            assert entry.filing_date == filing.filing_date
            assert entry.document == filing.document
            assert entry.path == f"ivv/{filing.report_date}.csv"

    @pytest.mark.parametrize("row", QUARTER_ENDS, ids=lambda row: row[0])
    def test_each_quarter_end_holds_its_rows_and_members(self, row: tuple) -> None:
        report_date, _, _, rows, member_count, *_ = row
        assert len(_held(report_date)) == _entry(report_date).row_count == rows
        assert len(members(IVV, _filing(report_date))) == member_count

    @pytest.mark.parametrize(
        "row", [row for row in QUARTER_ENDS if row[1] in HTML_FORMS], ids=lambda row: row[0]
    )
    def test_each_html_schedule_sums_to_the_total_it_prints(self, row: tuple) -> None:
        report_date, *_, printed = row
        assert _entry(report_date).printed_total == printed
        assert sum(int(holding.value) for holding in _held(report_date)) == printed

    def test_forty_two_schedules_are_html_and_twenty_eight_are_nport(self) -> None:
        forms = [row[1] for row in QUARTER_ENDS]
        assert sum(form in HTML_FORMS for form in forms) == 42
        assert [e.printed_total for e in read_index() if e.fund == "IVV"][42:] == [None] * 28

    def test_html_rows_carry_no_identifiers_and_nport_rows_carry_an_isin(self) -> None:
        for report_date, form, *_ in QUARTER_ENDS:
            held = _held(report_date)
            if form in HTML_FORMS:
                assert all(not (h.cusip or h.isin or h.ticker) for h in held)
            else:
                assert all(h.isin for h in held)

    def test_ivvs_nport_rows_carry_no_ticker(self) -> None:
        # IJR's N-PORT rows print a ticker from 2022. IVV's never do, so a
        # ticker for an IVV member has to come from somewhere else.
        for report_date, form, *_ in QUARTER_ENDS:
            if form.startswith("NPORT-P"):
                assert not any(holding.ticker for holding in _held(report_date))

    def test_the_schedules_keep_the_companies_that_later_left(self) -> None:
        departed = {
            "2008-12-31": ("Centex Corp.", "Schering-Plough Corp."),
            "2020-09-30": ("Tiffany & Co", "Noble Energy Inc"),
            "2024-12-31": ("Hess Corp.", "Discover Financial Services"),
        }
        for report_date, names in departed.items():
            assert set(names) <= {holding.name for holding in _held(report_date)}

    def test_lines_sharing_an_accession_name_one_document(self) -> None:
        by_accession: dict[str, set[str]] = {}
        for entry in read_index():
            by_accession.setdefault(entry.accession, set()).add(entry.document_sha256)
        assert all(len(hashes) == 1 for hashes in by_accession.values())
        shared = [
            e
            for e in read_index()
            if e.fund == "IVV" and e.accession in {f.accession for f in IJR.filings}
        ]
        assert len(shared) == 11

    def test_the_amendment_is_what_2025_09_30_reads(self) -> None:
        entry = _entry("2025-09-30")
        assert (entry.form, entry.accession, entry.filing_date) == (
            "NPORT-P/A",
            "0002071691-26-015790",
            "2026-07-13",
        )


class TestTheMemberRule:
    def test_the_one_non_stock_row_is_a_zero_share_line(self) -> None:
        assert [(e.report_date, e.name, e.cusip) for e in IVV.not_stocks] == [
            ("2022-06-30", "Under Armour Inc", "904311206")
        ]
        (line,) = [h for h in _held("2022-06-30") if h.cusip == "904311206"]
        assert Decimal(line.shares) == Decimal(line.value) == 0
        assert line not in members(IVV, _filing("2022-06-30"))

    def test_no_other_row_holds_zero_shares(self) -> None:
        for report_date, *_ in QUARTER_ENDS:
            zero = [h for h in _held(report_date) if not Decimal(h.shares)]
            assert len(zero) == (1 if report_date == "2022-06-30" else 0), report_date

    def test_a_right_filed_outside_ec_is_not_a_row(self) -> None:
        # The 2026-06-30 N-PORT holds a Hologic CVR and no Hologic stock.
        assert not any("Hologic" in holding.name for holding in _held("2026-06-30"))
        t_mobile = [h for h in _held("2020-06-30") if h.name.startswith("T-Mobile")]
        assert [h.cusip for h in t_mobile] == ["872590104"]

    def test_a_second_share_class_is_its_own_member(self) -> None:
        for report_date in ("2016-12-31", "2024-12-31"):
            alphabet = [h for h in members(IVV, _filing(report_date)) if "Alphabet" in h.name]
            assert len(alphabet) == 2
            assert len({h.name for h in alphabet}) == 2


RECORDED = [filing for filing in IVV.filings if not filing.skipped]


class TestLinks:
    @pytest.mark.parametrize("at", range(1, len(RECORDED)), ids=lambda at: RECORDED[at].report_date)
    def test_each_schedule_links_its_pinned_count_to_the_one_recorded_before(self, at: int) -> None:
        # The schedule before is the one before in the list that has a file,
        # so 2013-12-31 is linked to 2013-06-30 across the skipped date.
        current = members(IVV, RECORDED[at])
        previous = members(IVV, RECORDED[at - 1])
        pairs = link(current, previous)
        linked = sum(1 for row, _ in pairs if row is not None)
        pinned = next(row for row in QUARTER_ENDS if row[0] == RECORDED[at].report_date)
        assert (linked, len(current) - linked) == pinned[5:7]


# --- Parsing the traps the survey met, one fixture each -----------------------


def _html(name: str) -> fund_holdings.Schedule:
    return parse_nq(_fixture(name), IVV.schedule_names)


class TestParseHtml:
    def test_the_summary_schedule_before_the_full_one_is_skipped(self) -> None:
        schedule = _html("ncsr-2009-summary-first.htm")
        assert schedule.holdings == (
            Holding("Interpublic Group of Companies Inc. (The)", "1018705", "4197065"),
            Holding("Omnicom Group Inc.", "660047", "15445100"),
        )
        assert schedule.printed_total == 14_709_010_567
        assert b"Other securities" in _fixture("ncsr-2009-summary-first.htm")

    def test_the_heading_names_the_index_fund_and_later_the_core_etf(self) -> None:
        assert b"S&amp;P 500 INDEX FUND" in _fixture("ncsr-2009-summary-first.htm")
        schedule = _html("ncsrs-2012-core-heading.htm")
        assert [h.name for h in schedule.holdings] == ["Interpublic Group of Companies Inc. (The)"]
        assert schedule.printed_total == 31_702_434_377
        with pytest.raises(ValueError, match="no schedule heading"):
            parse_nq(_fixture("ncsrs-2012-core-heading.htm"), ("S&P 500 INDEX FUND",))

    def test_the_2018_06_name_above_schedule_of_investments_opens_the_section(self) -> None:
        schedule = _html("nq-2018-06-name-before-heading.htm")
        assert [h.name for h in schedule.holdings] == ["Arconic Inc.", "Monster Beverage Corp."]
        assert schedule.printed_total == 148_253_964_464

    def test_the_2014_06_total_split_by_a_space_is_read_whole(self) -> None:
        schedule = _html("nq-2014-06-split-total.htm")
        assert schedule.printed_total == 57_750_612_466
        assert b"57,750, 612,466" in _fixture("nq-2014-06-split-total.htm")

    @pytest.mark.parametrize(
        ("name", "mark"),
        [
            ("nq-2014-06-split-total.htm", b">a,b</SUP>"),
            ("nq-2018-06-name-before-heading.htm", b">(a)(c)</SUP>"),
        ],
    )
    def test_both_styles_of_footnote_mark_are_dropped(self, name: str, mark: bytes) -> None:
        assert mark in _fixture(name)
        assert "Monster Beverage Corp." in [h.name for h in _html(name).holdings]

    def test_the_page_footer_inside_a_schedule_is_not_a_row(self) -> None:
        schedule = _html("ncsrs-2010-footer-and-wrapped-names.htm")
        assert len(schedule.holdings) == 3
        assert b"S<SMALL>CHEDULES</SMALL>" in _fixture("ncsrs-2010-footer-and-wrapped-names.htm")

    def test_the_letter_spaced_page_footer_of_2019_is_not_a_row(self) -> None:
        schedule = _html("ncsr-2019-spaced-footer.htm")
        assert schedule.holdings == (Holding("Arconic Inc.", "3015637", "57628823"),)
        assert schedule.printed_total == 168_918_569_125

    def test_a_name_wrapped_across_two_rows_is_read_whole(self) -> None:
        schedule = _html("ncsrs-2010-footer-and-wrapped-names.htm")
        assert [h.name for h in schedule.holdings] == [
            "Interpublic Group of Companies Inc. (The)",
            "E.I. du Pont de Nemours and Co.",
            "Discovery Communications Inc. Series A",
        ]
        assert {"E.I. du Pont de Nemours and Co.", "Discovery Communications Inc. Series A"} <= {
            holding.name for holding in _held("2010-09-30")
        }

    def test_a_heading_carried_onto_a_new_page_is_not_part_of_a_name(self) -> None:
        names = [h.name for h in _html("nport-ex-2019-06-standalone.htm").holdings]
        assert names == ["Arconic Inc.", "Coca-Cola Co. (The)"]

    def test_the_standalone_nport_ex_is_read_as_html(self) -> None:
        schedule = parse(_fixture("nport-ex-2019-06-standalone.htm"), IVV, _filing("2019-06-30"))
        assert schedule.holdings[0] == Holding("Arconic Inc.", "2880822", "74382824")
        assert schedule.printed_total == 176_338_648_537


#: One fixture per form IVV's list reads, with the filing it is parsed as.
#: 2025-09-30's amendment is read as the 2020-06-30 N-PORT, since both are XML
#: for IVV's series.
ROUTES = {
    "N-Q": ("nq-2014-06-split-total.htm", "2014-06-30", "Boeing Co. (The)"),
    "N-CSR": (
        "ncsr-2009-summary-first.htm",
        "2009-03-31",
        "Interpublic Group of Companies Inc. (The)",
    ),
    "N-CSRS": (
        "ncsrs-2010-footer-and-wrapped-names.htm",
        "2010-09-30",
        "Interpublic Group of Companies Inc. (The)",
    ),
    "NPORT-EX": ("nport-ex-2019-06-standalone.htm", "2019-06-30", "Arconic Inc."),
    "NPORT-P": ("nport-2020-06-right.xml", "2020-06-30", "T-Mobile US Inc"),
    "NPORT-P/A": ("nport-2020-06-right.xml", "2025-09-30", "T-Mobile US Inc"),
}


class TestParseRoutes:
    def test_every_form_on_the_list_has_a_route_here(self) -> None:
        assert set(ROUTES) == {filing.form for filing in IVV.filings}

    @pytest.mark.parametrize("form", sorted(ROUTES))
    def test_each_form_reaches_the_parser_that_reads_it(self, form: str) -> None:
        name, report_date, first = ROUTES[form]
        filing = _filing(report_date)
        assert filing.form == form
        assert parse(_fixture(name), IVV, filing).holdings[0].name == first

    def test_a_form_no_parser_reads_is_refused(self) -> None:
        with pytest.raises(ValueError, match="no parser reads form N-CSR/A"):
            parse(b"", IVV, replace(_filing("2009-03-31"), form="N-CSR/A"))

    def test_the_symbol_fetch_takes_is_the_fund(self) -> None:
        assert fund_holdings.FUNDS["IVV"] is IVV
        assert IVV.symbol == "IVV"


def _rows(*rows: tuple[str, ...]) -> bytes:
    """A schedule built by hand, for the name rule's cases no filing prints."""
    cells = "".join("<TR>" + "".join(f"<TD>{c}</TD>" for c in row) + "</TR>" for row in rows)
    return (
        "<P>Schedule of Investments</P><P>iShares Core S&amp;P 500 ETF</P>"
        f"<TABLE><TR><TD>COMMON STOCKS</TD></TR>{cells}"
        "<TR><TD>TOTAL COMMON STOCKS</TD><TD>30</TD></TR></TABLE>"
    ).encode()


def _names(*rows: tuple[str, ...]) -> list[str]:
    return [h.name for h in parse_nq(_rows(*rows), IVV.schedule_names).holdings]


class TestTheNameRule:
    def test_a_joined_start_is_not_carried_to_the_next_holding(self) -> None:
        assert _names(
            ("Discovery",), ("Communications Inc.", "1", "10"), ("Acme Inc.", "1", "20")
        ) == [
            "Discovery Communications Inc.",
            "Acme Inc.",
        ]

    def test_a_start_is_held_across_both_page_footers(self) -> None:
        names = _names(
            ("E.I. du Pont de Nemours",),
            ("SCHEDULES OF INVESTMENTS", "7"),
            ("8", "2010 iSHARES SEMI-ANNUAL REPORT TO SHAREHOLDERS"),
            ("and Co.", "1", "30"),
        )
        assert names == ["E.I. du Pont de Nemours and Co."]

    @pytest.mark.parametrize(
        "line",
        [
            "Media — 2.0%",
            "AEROSPACE & DEFENSE",
            "Chemicals (continued)",
            "Chemicals (Continued)",
            "Chemicals—continued",
            "(a) Non-income earning security.",
            "7585,592,127",
        ],
    )
    def test_a_line_that_is_not_a_name_start_is_not_joined(self, line: str) -> None:
        assert _names((line,), ("Acme Inc.", "1", "30")) == ["Acme Inc."]

    def test_a_heading_after_a_start_clears_it(self) -> None:
        assert _names(("Discovery",), ("Media — 2.0%",), ("Acme Inc.", "1", "30")) == ["Acme Inc."]

    def test_a_row_of_a_name_and_one_number_is_refused(self) -> None:
        with pytest.raises(ValueError, match="a shape no year printed"):
            parse_nq(_rows(("Acme Inc.", "10")), IVV.schedule_names)


class TestParseNport:
    def test_a_right_filed_outside_ec_is_left_out(self) -> None:
        document = _fixture("nport-2020-06-right.xml")
        assert document.count(b"<title>T-Mobile US Inc</title>") == 2
        schedule = parse_nport(document, "S000004310")
        assert [(h.name, h.cusip) for h in schedule.holdings] == [("T-Mobile US Inc", "872590104")]
