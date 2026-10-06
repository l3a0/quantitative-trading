"""The pins for IJR's year-end holdings, read from its SEC filings.

This file is the single authority for every number any prose surface quotes
about IJR's files under ``research/filings/``, and about the record as a
whole, such as its size. ``tests/test_ivv_holdings.py`` holds IVV's. It needs
no network. Every pin reads the committed record, and every parser test reads a
few rows cut from the real document, under ``tests/fixtures/filings/``.

**What pins a number here is the accession rather than a vintage.** An SEC
filing is never restated, so the accession names fixed bytes, and the index's
``document_sha256`` says which bytes were parsed. The record was written on
2026-10-04 from the documents the survey on
[issue 361](https://github.com/l3a0/quantitative-trading/issues/361)
downloaded that day.

**The specification.** A row is a row under common stocks: an N-Q's rows from
IJR's "COMMON STOCKS" line to its "Total Common Stocks" line, and an N-PORT's
``invstOrSec`` rows whose ``assetCat`` is ``EC``. A member is a row not on
:data:`chan.fund_holdings.IJR`'s list of non-stock rows. A member is placed
when :func:`chan.fund_holdings.link` pairs it with a row in the filing before,
by CUSIP where both carry one, and otherwise by name, first with the
share-class suffix and then without it.
"""

from __future__ import annotations

import http.client
import json
import urllib.error
from decimal import Decimal
from pathlib import Path

import pytest

from chan import fund_holdings
from chan.fund_holdings import (
    IJR,
    Filing,
    FilingRefused,
    Fund,
    Holding,
    link,
    members,
    parse_nport,
    parse_nq,
    place,
    read_holdings,
    read_index,
    record,
)

FIXTURES = Path(__file__).parent / "fixtures" / "filings"

#: Per year-end: report date, form, accession, rows under common stocks,
#: members, members placed, members not placed, and an N-Q's printed
#: "Total Common Stocks". The first filing has nothing before it, so it places
#: nobody and is not asked to.
YEAR_ENDS = (
    ("2007-12-31", "N-Q", "0001193125-08-043324", 602, 602, None, None, 4_387_645_916),
    ("2008-12-31", "N-Q", "0001193125-09-040696", 600, 600, 509, 91, 3_739_702_606),
    ("2009-12-31", "N-Q", "0001193125-10-044578", 600, 600, 543, 57, 5_291_542_066),
    ("2010-12-31", "N-Q", "0001193125-11-052046", 600, 600, 543, 57, 6_744_797_324),
    ("2011-12-31", "N-Q", "0001193125-12-088646", 601, 600, 530, 70, 6_907_921_868),
    ("2012-12-31", "N-Q", "0001193125-13-086998", 602, 601, 551, 50, 8_067_128_852),
    ("2013-12-31", "N-Q", "0001193125-14-076476", 602, 601, 549, 52, 14_298_541_057),
    ("2014-12-31", "N-Q", "0001193125-15-065725", 602, 601, 535, 66, 14_759_607_541),
    ("2015-12-31", "N-Q", "0001193125-16-480933", 602, 601, 525, 76, 16_970_976_697),
    ("2016-12-31", "N-Q", "0001193125-17-065125", 603, 602, 516, 86, 26_388_125_504),
    ("2017-12-31", "N-Q", "0001193125-18-063612", 603, 602, 527, 75, 35_999_526_395),
    ("2018-12-31", "N-Q", "0001193125-19-059323", 604, 603, 530, 73, 37_293_884_055),
    ("2019-12-31", "NPORT-P", "0001752724-20-038667", 604, 603, 522, 81, None),
    ("2020-12-31", "NPORT-P", "0001752724-21-040685", 601, 601, 528, 73, None),
    ("2021-12-31", "NPORT-P", "0001752724-22-046380", 602, 602, 537, 65, None),
    ("2022-12-30", "NPORT-P", "0001752724-23-037514", 603, 601, 536, 65, None),
    ("2023-12-31", "NPORT-P", "0001752724-24-038606", 604, 602, 503, 99, None),
    ("2024-12-31", "NPORT-P", "0001752724-25-041377", 604, 602, 522, 80, None),
    ("2025-12-31", "NPORT-P", "0000940400-26-007526", 605, 603, 532, 71, None),
)

PLACED_YEARS = [row for row in YEAR_ENDS if row[5] is not None]


def _filing(report_date: str) -> Filing:
    return next(filing for filing in IJR.filings if filing.report_date == report_date)


def _fixture(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


# --- The committed record ----------------------------------------------------


class TestTheCommittedRecord:
    def test_the_list_names_each_year_end_once_with_its_accession(self) -> None:
        listed = [(f.report_date, f.form, f.accession) for f in IJR.filings]
        assert listed == [row[:3] for row in YEAR_ENDS]

    def test_the_index_holds_one_line_per_filing_in_the_list(self) -> None:
        index = [entry for entry in read_index() if entry.fund == "IJR"]
        assert [(e.report_date, e.form, e.accession) for e in index] == [
            row[:3] for row in YEAR_ENDS
        ]
        for entry, filing in zip(index, IJR.filings, strict=True):
            assert entry.fund == "IJR"
            assert entry.series_id == "S000004313"
            assert entry.filing_date == filing.filing_date
            assert entry.document == filing.document
            assert entry.path == f"ijr/{filing.report_date}.csv"

    def test_the_directory_holds_no_file_the_index_does_not_name(self) -> None:
        # A fund's members file sits beside its holdings files and is not a
        # filing, so the index does not name it. Issue 332 records it. IVV's
        # holes file sits there too, and issue 373 records it.
        named = {entry.path for entry in read_index()}
        panel_files = {f"{symbol.lower()}/members.csv" for symbol in fund_holdings.FUNDS}
        panel_files.add("ivv/holes.csv")
        on_disk = {
            path.relative_to(fund_holdings.FILINGS_DIR).as_posix()
            for path in fund_holdings.FILINGS_DIR.rglob("*.csv")
        } - panel_files
        assert on_disk == named

    @pytest.mark.parametrize("entry", read_index(), ids=lambda entry: entry.path)
    def test_each_file_is_what_the_writer_writes_from_its_rows(
        self, entry: fund_holdings.IndexEntry
    ) -> None:
        content = (fund_holdings.FILINGS_DIR / entry.path).read_bytes()
        assert b"\r" not in content
        rows = read_holdings(fund_holdings.FILINGS_DIR / entry.path)
        assert fund_holdings.serialize(rows) == content

    @pytest.mark.parametrize("entry", read_index(), ids=lambda entry: entry.path)
    def test_each_file_hashes_to_its_index_line(self, entry: fund_holdings.IndexEntry) -> None:
        content = (fund_holdings.FILINGS_DIR / entry.path).read_bytes()
        assert fund_holdings._sha256(content) == entry.sha256
        assert len(entry.document_sha256) == 64

    @pytest.mark.parametrize("row", YEAR_ENDS, ids=lambda row: row[0])
    def test_each_year_end_holds_its_rows_and_members(self, row: tuple) -> None:
        report_date, _, _, rows, member_count, *_ = row
        filing = _filing(report_date)
        held = read_holdings(fund_holdings.holdings_path(IJR, filing))
        entry = next(e for e in read_index() if e.report_date == report_date)
        assert len(held) == entry.row_count == rows
        assert len(members(IJR, filing)) == member_count

    @pytest.mark.parametrize("row", YEAR_ENDS[:12], ids=lambda row: row[0])
    def test_each_nq_year_sums_to_the_total_it_prints(self, row: tuple) -> None:
        report_date, *_, printed = row
        filing = _filing(report_date)
        held = read_holdings(fund_holdings.holdings_path(IJR, filing))
        entry = next(e for e in read_index() if e.report_date == report_date)
        assert entry.printed_total == printed
        assert sum(int(holding.value) for holding in held) == printed

    def test_the_record_takes_the_bytes_the_design_doc_quotes(self) -> None:
        files = [fund_holdings.FILINGS_DIR / fund_holdings.INDEX_NAME]
        files += [fund_holdings.FILINGS_DIR / entry.path for entry in read_index()]
        assert sum(path.stat().st_size for path in files) == 2_672_010

    def test_nport_years_print_no_total(self) -> None:
        nport = [e.printed_total for e in read_index() if e.fund == "IJR" and e.form != "N-Q"]
        assert nport == [None] * 7

    def test_the_2009_anchor(self) -> None:
        held = read_holdings(fund_holdings.holdings_path(IJR, _filing("2009-12-31")))
        k_swiss = [holding for holding in held if holding.name.startswith("K-Swiss")]
        assert k_swiss == [Holding("K-Swiss Inc. Class A", "351129", "3490222")]

    def test_nq_rows_carry_no_identifiers_and_nport_rows_carry_an_isin(self) -> None:
        for filing in IJR.filings:
            held = read_holdings(fund_holdings.holdings_path(IJR, filing))
            if filing.form == "N-Q":
                assert all(not (h.cusip or h.isin or h.ticker) for h in held)
            else:
                assert all(h.isin for h in held)

    def test_tickers_appear_from_2022_as_the_filing_prints_them(self) -> None:
        for filing in IJR.filings[12:]:
            held = read_holdings(fund_holdings.holdings_path(IJR, filing))
            with_ticker = sum(1 for holding in held if holding.ticker)
            assert (with_ticker == len(held)) == (filing.report_date >= "2022")
        last = read_holdings(fund_holdings.holdings_path(IJR, IJR.filings[-1]))
        assert {"CWEN/A", "MOG/A"} <= {holding.ticker for holding in last}


class TestTheMemberRule:
    def test_every_non_stock_entry_names_exactly_one_row(self) -> None:
        for entry in IJR.not_stocks:
            held = read_holdings(fund_holdings.holdings_path(IJR, _filing(entry.report_date)))
            matches = [h for h in held if (h.name, h.cusip) == (entry.name, entry.cusip)]
            assert len(matches) == 1, entry

    def test_the_three_kinds_the_survey_found(self) -> None:
        kinds = {}
        for entry in IJR.not_stocks:
            kinds.setdefault(entry.name.split()[0].lower(), []).append(entry.report_date)
        assert kinds["gerber"] == [f"{year}-12-31" for year in range(2011, 2018)]
        assert kinds["a"] + kinds["schulman"] == ["2018-12-31", "2019-12-31"]
        assert sorted(kinds["omniab"] + kinds["omniab,"]) == sorted(
            [date for date in ("2022-12-30", "2023-12-31", "2024-12-31", "2025-12-31")] * 2
        )

    def test_a_second_share_class_is_its_own_member(self) -> None:
        held = members(IJR, _filing("2015-12-31"))
        central = [h.name for h in held if h.name.startswith("Central Garden")]
        assert central == ["Central Garden & Pet Co.", "Central Garden & Pet Co. Class A"]


class TestPlacement:
    @pytest.mark.parametrize("row", PLACED_YEARS, ids=lambda row: row[0])
    def test_each_year_end_places_and_leaves_its_pinned_counts(self, row: tuple) -> None:
        report_date, *_, placed, unplaced, _ = row
        placements = place(IJR, report_date)
        assert sum(1 for p in placements if p.calendar_return is not None) == placed
        assert sum(1 for p in placements if p.calendar_return is None) == unplaced

    def test_an_unlinked_member_carries_nothing_a_reader_could_mistake_for_a_return(self) -> None:
        for placement in place(IJR, "2019-12-31"):
            linked = placement.previous is not None
            assert linked == (placement.linked_by is not None)
            assert linked == (placement.calendar_return is not None)

    def test_a_reverse_split_that_changed_the_isin_is_left_unpaired(self) -> None:
        # Nabors's Bermuda shares carry no CUSIP, and the 1-for-50 reverse split
        # between the two filings gave them a new ISIN. Paired by name they read
        # as a gain of about nineteen times.
        nabors = [p for p in place(IJR, "2020-12-31") if p.holding.name.startswith("Nabors")]
        assert len(nabors) == 1
        assert nabors[0].previous is None

    def test_a_restyled_name_still_pairs(self) -> None:
        placement = next(
            p for p in place(IJR, "2015-12-31") if p.holding.name == "UniFirst Corp./MA"
        )
        assert placement.previous.name == "UniFirst Corp."
        assert placement.linked_by == "name"

    def test_the_return_is_the_change_in_value_over_shares(self) -> None:
        placement = next(
            p for p in place(IJR, "2010-12-31") if p.holding.name == "K-Swiss Inc. Class A"
        )
        assert placement.previous == Holding("K-Swiss Inc. Class A", "351129", "3490222")
        assert placement.calendar_return == (
            Decimal(placement.holding.value)
            / Decimal(placement.holding.shares)
            / (Decimal("3490222") / Decimal("351129"))
            - 1
        )

    def test_the_format_change_is_crossed_by_name(self) -> None:
        how = {p.linked_by for p in place(IJR, "2019-12-31")}
        assert how == {"name", "name without class", None}

    def test_a_change_in_share_count_reads_as_a_return(self) -> None:
        # The rough return reads value over shares, so a member whose share
        # count fell about twentyfold between two filings reads as a gain of
        # more than fifty times. Pinned so the limit is stated where it bites.
        placement = next(
            p for p in place(IJR, "2009-12-31") if p.holding.name.startswith("Steak n Shake")
        )
        assert int(placement.previous.shares) / int(placement.holding.shares) > 20
        assert placement.calendar_return > 50

    def test_a_zero_share_count_leaves_one_member_unplaced_and_the_rest_placed(
        self, tmp_path: Path
    ) -> None:
        first = Filing("2023-12-31", "NPORT-P", "a-1", "2024-01-01", "primary_doc.xml")
        second = Filing("2024-12-31", "NPORT-P", "a-2", "2025-01-01", "primary_doc.xml")
        fund = Fund("XYZ", "S0", (), (first, second), ())
        rows = {
            first: [Holding("Zero Inc", "0", "0", "111111111"), Holding("Two Inc", "1", "2", "2")],
            second: [Holding("Zero Inc", "5", "5", "111111111"), Holding("Two Inc", "1", "3", "2")],
        }
        for filing, held in rows.items():
            path = fund_holdings.holdings_path(fund, filing, tmp_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(fund_holdings.serialize(held))
        zero, two = place(fund, "2024-12-31", tmp_path)
        assert (zero.linked_by, zero.calendar_return) == ("cusip", None)
        assert two.calendar_return == Decimal("0.5")

    def test_the_first_filing_cannot_be_placed(self) -> None:
        with pytest.raises(ValueError, match="first filing"):
            place(IJR, "2007-12-31")


# --- Linking -----------------------------------------------------------------


class TestLink:
    def test_a_cusip_both_rows_carry_decides(self) -> None:
        current = [Holding("New Name Inc", "1", "1", cusip="123456789")]
        previous = [
            Holding("Old Name Inc", "1", "1", cusip="123456789"),
            Holding("New Name Inc", "1", "1", cusip="999999999"),
        ]
        assert link(current, previous) == [(previous[0], "cusip")]

    def test_two_cusips_that_disagree_are_never_paired_by_name(self) -> None:
        current = [Holding("Same Inc", "1", "1", cusip="123456789")]
        previous = [Holding("Same Inc", "1", "1", cusip="987654321")]
        assert link(current, previous) == [(None, None)]

    def test_names_pair_across_punctuation_case_and_a_curly_apostrophe(self) -> None:
        current = [Holding("US Physical Therapy Inc", "1", "1", cusip="90337L108")]
        previous = [
            Holding("U.S. Physical Therapy Inc.", "1", "1"),
            Holding("BJ’s Restaurants Inc.", "1", "1"),
        ]
        assert link(current, previous)[0] == (previous[0], "name")
        assert link([Holding("BJ's Restaurants Inc", "1", "1")], previous) == [
            (previous[1], "name")
        ]

    def test_the_share_class_keeps_two_lines_of_one_company_apart(self) -> None:
        current = [
            Holding("Central Garden & Pet Co.", "1", "1"),
            Holding("Central Garden & Pet Co. Class A", "1", "1"),
        ]
        previous = list(reversed(current))
        assert link(current, previous) == [(previous[1], "name"), (previous[0], "name")]

    def test_the_suffix_is_dropped_only_for_a_company_held_on_one_line(self) -> None:
        current = [Holding("Lithia Motors Inc", "1", "1", cusip="536797103")]
        previous = [Holding("Lithia Motors Inc., Class A", "1", "1")]
        assert link(current, previous) == [(previous[0], "name without class")]

    def test_two_lines_one_title_on_the_other_side_stay_unpaired(self) -> None:
        # 2019's N-PORT titles Central Garden's two classes the same.
        current = [
            Holding("Central Garden & Pet Co", "1", "1", cusip="153527106"),
            Holding("Central Garden & Pet Co", "1", "1", cusip="153527205"),
        ]
        previous = [
            Holding("Central Garden & Pet Co.", "1", "1"),
            Holding("Central Garden & Pet Co., Class A, NVS", "1", "1"),
        ]
        assert link(current, previous) == [(None, None), (None, None)]

    def test_a_previous_row_two_members_reach_is_given_to_neither(self) -> None:
        current = [Holding("Acme Inc", "1", "1"), Holding("Acme Inc.", "1", "1")]
        previous = [Holding("ACME INC", "1", "1")]
        assert link(current, previous) == [(None, None), (None, None)]

    def test_a_key_two_previous_rows_share_pairs_with_neither(self) -> None:
        current = [Holding("Acme Inc", "1", "1")]
        previous = [Holding("Acme Inc Class A", "1", "1"), Holding("Acme Inc Class B", "1", "1")]
        assert link(current, previous) == [(None, None)]

    def test_a_row_the_first_pass_took_is_not_offered_again(self) -> None:
        current = [Holding("Acme Inc", "1", "1"), Holding("Acme Inc Class B", "1", "1")]
        previous = [Holding("Acme Inc.", "1", "1")]
        assert link(current, previous) == [(previous[0], "name"), (None, None)]

    def test_two_different_class_letters_are_never_paired(self) -> None:
        current = [Holding("Acme Corp., Class B", "1", "1")]
        previous = [Holding("Acme Corp. Class A", "1", "1")]
        assert link(current, previous) == [(None, None)]

    def test_class_and_series_with_one_letter_agree(self) -> None:
        current = [Holding("Phibro Animal Health Corp., Class A", "1", "1")]
        previous = [Holding("Phibro Animal Health Corp. Series A", "1", "1")]
        assert link(current, previous) == [(previous[0], "name without class")]

    def test_two_isins_that_disagree_without_cusips_are_never_paired(self) -> None:
        current = [Holding("Nabors Industries Ltd", "1", "1", isin="BMG6359F1370")]
        previous = [Holding("Nabors Industries Ltd", "1", "1", isin="BMG6359F1032")]
        assert link(current, previous) == [(None, None)]

    def test_an_isin_is_not_compared_where_one_row_has_a_cusip(self) -> None:
        current = [Holding("Penguin Solutions Inc", "1", "1", "706915105", "US7069151055")]
        previous = [Holding("Penguin Solutions Inc", "1", "1", "", "KYG8232Y1017")]
        assert link(current, previous) == [(previous[0], "name")]

    def test_the_cusip_match_is_not_taken_by_a_namesake_without_one(self) -> None:
        current = [
            Holding("Acme Inc", "1", "1", cusip="123456789"),
            Holding("Acme Inc", "1", "1"),
        ]
        previous = [Holding("Acme Inc", "1", "1", cusip="123456789")]
        assert link(current, previous) == [(previous[0], "cusip"), (None, None)]

    @pytest.mark.parametrize(
        ("one", "other"),
        [
            ("Marcus Corp. (The)", "Marcus Corp."),
            ("UniFirst Corp./MA", "UniFirst Corp."),
            ("Kulicke & Soffa Industries Inc.", "Kulicke and Soffa Industries Inc."),
            ("Haverty Furniture Cos Inc", "Haverty Furniture Companies Inc."),
            ("Cato Corp/The", "Cato Corp. (The)"),
        ],
    )
    def test_the_restylings_between_years_normalise_alike(self, one: str, other: str) -> None:
        assert fund_holdings.normalised_name(one) == fund_holdings.normalised_name(other)

    def test_a_slash_inside_a_name_is_not_a_state(self) -> None:
        assert fund_holdings.normalised_name("RE/MAX Holdings Inc") == "re max holdings inc"


# --- Parsing an N-Q, one trap at a time ---------------------------------------


def _nq(name: str) -> fund_holdings.Schedule:
    return parse_nq(_fixture(name), IJR.schedule_names)


class TestParseNq:
    def test_every_fixture_names_the_accession_it_was_cut_from(self) -> None:
        accessions = {
            filing.accession: filing.document
            for fund in fund_holdings.FUNDS.values()
            for filing in fund.filings
        }
        for path in sorted(FIXTURES.iterdir()):
            first = path.read_text(encoding="utf-8").splitlines()[0]
            if first.startswith("<?xml"):
                first = first[first.index("?>") + 2 :]
            named = [a for a in accessions if f"accession {a}, document {accessions[a]}" in first]
            assert len(named) == 1, path.name

    def test_inline_footnotes_before_2012_are_dropped(self) -> None:
        schedule = _nq("nq-2009-inline-footnotes.htm")
        assert [h.name for h in schedule.holdings] == [
            "Andersons Inc. (The)",
            "K-Swiss Inc. Class A",
            "Liz Claiborne Inc.",
        ]
        assert schedule.printed_total == 5_291_542_066

    def test_sup_footnotes_from_2012_are_dropped(self) -> None:
        schedule = _nq("nq-2015-sup-footnotes.htm")
        assert schedule.holdings == (
            Holding("BJ’s Restaurants Inc.", "561542", "24410231"),
            Holding("Central Garden & Pet Co.", "269811", "3647845"),
            Holding("Central Garden & Pet Co. Class A", "892874", "12143086"),
        )

    def test_the_page_heading_repeated_from_2010_does_not_end_the_section(self) -> None:
        schedule = _nq("nq-2010-page-headings.htm")
        assert [h.name for h in schedule.holdings] == [
            "City Holding Co.",
            "Columbia Banking System Inc.",
            "Community Bank System Inc.",
            "First BanCorp (Puerto Rico)",
            "First Commonwealth Financial Corp.",
        ]
        assert schedule.printed_total == 6_744_797_324

    def test_the_column_header_repeated_from_2012_is_not_a_row(self) -> None:
        schedule = _nq("nq-2013-page-headings.htm")
        names = [h.name for h in schedule.holdings]
        assert len(names) == 40
        assert names[0] == "First Financial Bancorp"
        assert names[-1] == "Bel Fuse Inc. Class B"
        assert not any(name.startswith("Security") for name in names)
        assert schedule.printed_total == 14_298_541_057

    def test_a_line_break_inside_a_cell_is_a_space(self) -> None:
        schedule = _nq("nq-2016-line-break.htm")
        assert [h.name for h in schedule.holdings] == [
            "American Axle & Manufacturing Holdings Inc.",
            "Consolidated Communications Holdings Inc.",
        ]

    def test_the_2018_value_split_by_a_space_is_read_whole(self) -> None:
        schedule = _nq("nq-2018-split-number.htm")
        assert schedule.holdings == (Holding("Westamerica Bancorp.", "1501724", "83615992"),)
        assert schedule.printed_total == 37_293_884_055

    def test_the_space_is_closed_only_inside_a_correctly_grouped_number(self) -> None:
        assert fund_holdings._number("83,6 15,992") == "83615992"
        assert fund_holdings._number("83,6 1,5992") is None
        assert fund_holdings._number("$ 8,337,590") == "8337590"
        assert fund_holdings._number("(1,919") is None

    def test_the_2012_short_after_total_investments_is_not_read(self) -> None:
        schedule = _nq("nq-2012-short-positions.htm")
        assert schedule.holdings == (Holding("American States Water Co.", "299545", "14372169"),)
        assert schedule.printed_total == 8_067_128_852
        assert b"NCI Inc." in _fixture("nq-2012-short-positions.htm")

    def test_another_funds_heading_before_the_total_is_refused(self) -> None:
        with pytest.raises(ValueError, match="before the next fund's heading"):
            _nq("nq-2009-next-fund.htm")

    def test_a_document_without_the_fund_is_refused(self) -> None:
        with pytest.raises(ValueError, match="no schedule heading"):
            parse_nq(_fixture("nq-2009-inline-footnotes.htm"), ("S&P 500 INDEX FUND",))

    def test_a_heading_loses_the_trademark_sign_and_the_percentages_note(self) -> None:
        heading = "iShares® Core S&P Small-Cap ETF (Percentages shown are based on Net Assets)"
        assert fund_holdings._schedule_name(heading) == "CORE S&P SMALL-CAP ETF"


class TestParseNport:
    def test_the_title_the_isin_and_an_absent_cusip(self) -> None:
        schedule = parse_nport(_fixture("nport-2022-title-and-cusip.xml"), "S000004313")
        assert schedule.printed_total is None
        assert schedule.holdings == (
            Holding(
                "Moog Inc",
                "2146735.00000000",
                "188397463.60000000",
                "615394202",
                "US6153942023",
                "MOG/A",
            ),
            Holding(
                "Alpha & Omega Semiconductor Ltd",
                "1653335.00000000",
                "47235780.95000000",
                "",
                "BMG6331P1041",
                "AOSL",
            ),
        )

    def test_the_name_is_the_one_cut_at_thirty_characters(self) -> None:
        assert b"<name>Alpha &amp; Omega Semiconductor Lt</name>" in _fixture(
            "nport-2022-title-and-cusip.xml"
        )

    def test_a_document_for_another_series_is_refused(self) -> None:
        with pytest.raises(ValueError, match="not S000004314"):
            parse_nport(_fixture("nport-2022-title-and-cusip.xml"), "S000004314")


# --- Writing, refusing and fetching ------------------------------------------

_NPORT_FILING = Filing(
    "2022-12-30", "NPORT-P", "0001752724-23-037514", "2023-02-24", "primary_doc.xml"
)
_NQ_FILING = Filing("2018-12-31", "N-Q", "0001193125-19-059323", "2019-03-01", "d655820dnq.htm")
_FUND = Fund("IJR", "S000004313", IJR.schedule_names, (_NPORT_FILING,), ())


class TestRecord:
    def test_a_parse_writes_its_file_and_index_line(self, tmp_path: Path) -> None:
        document = _fixture("nport-2022-title-and-cusip.xml")
        entry = record(_FUND, _NPORT_FILING, document, tmp_path)
        written = (tmp_path / "ijr" / "2022-12-30.csv").read_bytes()
        assert written.splitlines()[0] == b"name,shares,value,cusip,isin,ticker"
        assert entry.row_count == 2
        assert entry.sha256 == fund_holdings._sha256(written)
        assert entry.document_sha256 == fund_holdings._sha256(document)
        line = json.loads((tmp_path / "index.jsonl").read_text(encoding="utf-8"))
        assert line["accession"] == "0001752724-23-037514"
        assert line["printed_total"] is None

    def test_a_rerun_writing_the_same_bytes_changes_nothing(self, tmp_path: Path) -> None:
        document = _fixture("nport-2022-title-and-cusip.xml")
        record(_FUND, _NPORT_FILING, document, tmp_path)
        before = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
        record(_FUND, _NPORT_FILING, document, tmp_path)
        assert {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()} == before

    def test_a_rerun_writing_different_bytes_refuses_and_names_both(self, tmp_path: Path) -> None:
        document = _fixture("nport-2022-title-and-cusip.xml")
        entry = record(_FUND, _NPORT_FILING, document, tmp_path)
        target = tmp_path / "ijr" / "2022-12-30.csv"
        target.write_bytes(target.read_bytes() + b"Extra,1,1,,,\n")
        altered = fund_holdings._sha256(target.read_bytes())
        with pytest.raises(FilingRefused) as refusal:
            record(_FUND, _NPORT_FILING, document, tmp_path)
        assert altered in str(refusal.value) and entry.sha256 in str(refusal.value)
        assert target.read_bytes().endswith(b"Extra,1,1,,,\n")

    def test_a_different_index_line_for_a_held_accession_is_refused(self, tmp_path: Path) -> None:
        document = _fixture("nport-2022-title-and-cusip.xml")
        record(_FUND, _NPORT_FILING, document, tmp_path)
        (tmp_path / "ijr" / "2022-12-30.csv").unlink()
        index = tmp_path / "index.jsonl"
        index.write_text(index.read_text().replace('"document_sha256": "', '"document_sha256": "0'))
        with pytest.raises(FilingRefused, match="already records IJR 0001752724-23-037514"):
            record(_FUND, _NPORT_FILING, document, tmp_path)
        assert not (tmp_path / "ijr" / "2022-12-30.csv").exists()

    def test_two_funds_reading_one_accession_each_keep_their_line(self, tmp_path: Path) -> None:
        # One N-Q holds every fund in the trust, so IJR's and IVV's December
        # N-Q are the same accession. A line is found by fund and accession.
        document = _fixture("nport-2022-title-and-cusip.xml")
        other = Fund("IVV", "S000004313", (), (_NPORT_FILING,), ())
        record(_FUND, _NPORT_FILING, document, tmp_path)
        record(other, _NPORT_FILING, document, tmp_path)
        record(other, _NPORT_FILING, document, tmp_path)
        lines = read_index(tmp_path)
        assert [(e.fund, e.accession) for e in lines] == [
            ("IJR", "0001752724-23-037514"),
            ("IVV", "0001752724-23-037514"),
        ]
        assert (tmp_path / "ivv" / "2022-12-30.csv").read_bytes() == (
            tmp_path / "ijr" / "2022-12-30.csv"
        ).read_bytes()

    def test_a_second_funds_line_from_other_bytes_is_refused(self, tmp_path: Path) -> None:
        document = _fixture("nport-2022-title-and-cusip.xml")
        record(_FUND, _NPORT_FILING, document, tmp_path)
        other = Fund("IVV", "S000004313", (), (_NPORT_FILING,), ())
        with pytest.raises(FilingRefused, match="for IJR from document sha256"):
            record(other, _NPORT_FILING, document.replace(b"Moog Inc", b"Moog Inc "), tmp_path)
        assert [e.fund for e in read_index(tmp_path)] == ["IJR"]
        assert not (tmp_path / "ivv").exists()

    def test_a_total_missed_by_one_dollar_is_refused(self, tmp_path: Path, monkeypatch) -> None:
        schedule = fund_holdings.Schedule((Holding("Acme Inc.", "10", "100"),), 101)
        monkeypatch.setattr(fund_holdings, "parse", lambda *arguments: schedule)
        with pytest.raises(FilingRefused, match="the rows sum to 100, and the filing prints 101"):
            record(_FUND, _NQ_FILING, b"", tmp_path)

    def test_an_nq_whose_rows_miss_its_printed_total_is_refused(self, tmp_path: Path) -> None:
        with pytest.raises(FilingRefused, match="the filing prints 37,293,884,055"):
            record(_FUND, _NQ_FILING, _fixture("nq-2018-split-number.htm"), tmp_path)
        assert not any(tmp_path.iterdir())


class TestFetch:
    def test_the_contact_comes_from_the_environment_before_the_config(self, tmp_path: Path) -> None:
        config = tmp_path / "sec_user_agent"
        config.write_text("From Config c@example.com\n")
        assert fund_holdings.user_agent({}, config) == "From Config c@example.com"
        environ = {"QT_SEC_USER_AGENT": "From Env e@example.com"}
        assert fund_holdings.user_agent(environ, config) == "From Env e@example.com"

    def test_a_missing_contact_names_both_places(self, tmp_path: Path) -> None:
        with pytest.raises(FilingRefused) as refusal:
            fund_holdings.user_agent({}, tmp_path / "absent")
        assert "QT_SEC_USER_AGENT" in str(refusal.value)
        assert "sec_user_agent" in str(refusal.value)

    def test_the_document_url(self) -> None:
        assert fund_holdings.document_url(_filing("2018-12-31")) == (
            "https://www.sec.gov/Archives/edgar/data/1100663/000119312519059323/d655820dnq.htm"
        )

    def test_a_fetch_downloads_records_and_paces(self, tmp_path: Path) -> None:
        second = Filing(
            "2023-12-31", "NPORT-P", "0001752724-24-038606", "2024-02-26", "primary_doc.xml"
        )
        fund = Fund("IJR", "S000004313", (), (_NPORT_FILING, second), ())
        asked, pauses = [], []

        def download(url: str, contact: str) -> bytes:
            asked.append((url, contact))
            return _fixture("nport-2022-title-and-cusip.xml")

        entries = fund_holdings.fetch(
            fund,
            filings_dir=tmp_path,
            contact="Name n@example.com",
            download=download,
            pause=pauses.append,
        )
        assert [e.report_date for e in entries] == ["2022-12-30", "2023-12-31"]
        assert [contact for _, contact in asked] == ["Name n@example.com"] * 2
        assert pauses == [fund_holdings.REQUEST_SPACING_SECONDS]
        assert fund_holdings.REQUEST_SPACING_SECONDS > 0.1

    @pytest.mark.parametrize(
        "failure",
        [
            ConnectionResetError("reset by peer"),
            TimeoutError("timed out"),
            urllib.error.URLError("no route"),
            http.client.IncompleteRead(b"partial"),
        ],
        ids=lambda failure: type(failure).__name__,
    )
    def test_a_failed_request_becomes_a_refusal(self, monkeypatch, failure: Exception) -> None:
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *details):
                return False

            def read(self):
                raise failure

        monkeypatch.setattr(fund_holdings.urllib.request, "urlopen", lambda *a, **k: Response())
        with pytest.raises(FilingRefused, match="could not be read"):
            fund_holdings._download("https://www.sec.gov/x", "n@example.com")

    def test_a_download_the_index_does_not_recognise_is_refused(self, tmp_path: Path) -> None:
        document = _fixture("nport-2022-title-and-cusip.xml")
        record(_FUND, _NPORT_FILING, document, tmp_path)
        with pytest.raises(FilingRefused, match="the index records"):
            fund_holdings.fetch(
                _FUND,
                filings_dir=tmp_path,
                contact="n@example.com",
                download=lambda url, contact: document + b"\n",
                pause=lambda s: None,
            )

    def test_a_download_is_checked_against_another_funds_line(self, tmp_path: Path) -> None:
        # One N-Q is one set of bytes for every fund in it, so IVV's download
        # of an accession IJR's line names must be the bytes IJR's line hashed.
        document = _fixture("nport-2022-title-and-cusip.xml")
        record(_FUND, _NPORT_FILING, document, tmp_path)
        other = Fund("IVV", "S000004313", (), (_NPORT_FILING,), ())
        with pytest.raises(FilingRefused, match="downloaded with sha256"):
            fund_holdings.fetch(
                other,
                filings_dir=tmp_path,
                contact="n@example.com",
                download=lambda url, contact: document + b"\n",
                pause=lambda s: None,
            )
        assert not (tmp_path / "ivv").exists()

    def test_the_downloads_are_deleted(self, tmp_path: Path, monkeypatch) -> None:
        scratch = tmp_path / "scratch"
        scratch.mkdir()
        monkeypatch.setattr(fund_holdings.tempfile, "tempdir", str(scratch))
        fund_holdings.fetch(
            _FUND,
            filings_dir=tmp_path / "record",
            contact="n@example.com",
            download=lambda url, contact: _fixture("nport-2022-title-and-cusip.xml"),
            pause=lambda s: None,
        )
        assert list(scratch.iterdir()) == []

    def test_a_refusal_reaches_the_command_line_as_one_line(self, monkeypatch) -> None:
        monkeypatch.delenv("QT_SEC_USER_AGENT", raising=False)
        monkeypatch.setattr(fund_holdings, "USER_AGENT_CONFIG", Path("/nonexistent/agent"))
        with pytest.raises(SystemExit) as stop:
            fund_holdings.main(["fetch", "IJR"])
        assert "\n" not in str(stop.value.code)
        assert str(stop.value.code).startswith("SEC asks every request to name a contact")

    def test_an_unknown_fund_prints_the_usage(self) -> None:
        with pytest.raises(SystemExit, match="usage"):
            fund_holdings.main(["fetch", "SPY"])
