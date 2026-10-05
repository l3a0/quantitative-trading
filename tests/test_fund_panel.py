"""The rules of a fund's members panel, on small synthetic funds that run in CI.

:mod:`chan.fund_panel` maps a fund's members to tickers, checks each against
the filing, and reports coverage. These tests hold each rule on a fund of a few
rows written to a temporary directory, so none of them reads the archive or the
committed record. ``tests/test_sp600_panel.py`` pins what the rules give on
IJR's record.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest

from chan import fund_holdings
from chan.fund_holdings import Filing, Fund, Holding, NotStock
from chan.fund_panel import (
    COLUMNS,
    MemberRow,
    PanelRefused,
    alpha_vantage_symbol,
    carry_back,
    check_members,
    coverage,
    exit_date,
    numbered_members,
    panel_keys,
    previous_rows,
    price_date,
    read_members,
    require_panel,
    serialize_members,
    threats,
)

FIRST = Filing("2008-12-31", "N-Q", "a-1", "2009-02-27", "dnq.htm")
SECOND = Filing("2009-12-31", "N-Q", "a-2", "2010-02-26", "dnq.htm")
THIRD = Filing("2010-12-31", "NPORT-P", "a-3", "2011-02-25", "primary_doc.xml")

#: Weekdays from December 2008 to February 2011, standing in for an exchange
#: calendar. 2010-12-31 is a Friday and 2011-01-31 a Monday.
CALENDAR = pd.bdate_range("2008-12-01", "2011-02-28")


def _fund(tmp_path: Path, rows: dict[Filing, list[Holding]], not_stocks=()) -> Fund:
    fund = Fund("XYZ", "S0", (), tuple(rows), tuple(not_stocks))
    for filing, held in rows.items():
        path = fund_holdings.holdings_path(fund, filing, tmp_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(fund_holdings.serialize(held))
    return fund


@pytest.fixture
def three_years(tmp_path: Path) -> Fund:
    """Alpha in all three years, Beta from the second, Gone only in the first.

    Gone left before the second year-end, so it is outside the panel.
    """
    return _fund(
        tmp_path,
        {
            FIRST: [Holding("Alpha Inc", "100", "1000"), Holding("Gone Corp", "10", "50")],
            SECOND: [Holding("Alpha Inc", "100", "1200"), Holding("Beta Co", "200", "2000")],
            THIRD: [
                Holding("Alpha Inc", "100", "1500.00"),
                Holding("Beta Co", "200", "2500.00"),
            ],
        },
    )


class TestSymbol:
    @pytest.mark.parametrize("ticker", ["MOG/A", "MOG.A", "mog-a", " MOG/A "])
    def test_a_share_class_takes_alpha_vantages_hyphen(self, ticker: str) -> None:
        assert alpha_vantage_symbol(ticker) == "MOG-A"

    def test_a_plain_ticker_is_upper_cased_and_kept(self) -> None:
        assert alpha_vantage_symbol("kate") == "KATE"


class TestRows:
    def test_a_dropped_non_stock_row_keeps_the_numbers_after_it(self, tmp_path: Path) -> None:
        fund = _fund(
            tmp_path,
            {
                FIRST: [
                    Holding("Alpha Inc", "1", "1"),
                    Holding("Escrow Interest", "1", "0"),
                    Holding("Beta Co", "1", "1"),
                ]
            },
            [NotStock(FIRST.report_date, "Escrow Interest", "", "an escrow")],
        )
        numbered = numbered_members(fund, FIRST.report_date, tmp_path)
        assert [(row, holding.name) for row, holding in numbered] == [
            (1, "Alpha Inc"),
            (3, "Beta Co"),
        ]

    def test_links_name_the_row_in_the_filing_before(self, three_years: Fund, tmp_path) -> None:
        assert previous_rows(three_years, tmp_path) == {
            ("2009-12-31", 1): ("2008-12-31", 1),
            ("2010-12-31", 1): ("2009-12-31", 1),
            ("2010-12-31", 2): ("2009-12-31", 2),
        }

    def test_the_first_filing_holds_only_members_linked_into_the_second(
        self, three_years: Fund, tmp_path: Path
    ) -> None:
        assert panel_keys(three_years, tmp_path) == [
            ("2008-12-31", 1),
            ("2009-12-31", 1),
            ("2009-12-31", 2),
            ("2010-12-31", 1),
            ("2010-12-31", 2),
        ]


class TestCarryBack:
    def test_a_ticker_resolved_at_the_latest_year_end_reaches_back_along_links(
        self, three_years: Fund, tmp_path: Path
    ) -> None:
        resolved = {
            ("2010-12-31", 1): MemberRow("2010-12-31", 1, "ALP", "cusip"),
            ("2010-12-31", 2): MemberRow("2010-12-31", 2, "BET", "filing"),
        }
        rows = {row.key: row for row in carry_back(three_years, resolved, tmp_path)}
        assert rows[("2008-12-31", 1)] == MemberRow("2008-12-31", 1, "ALP", "link")
        assert rows[("2009-12-31", 1)] == MemberRow("2009-12-31", 1, "ALP", "link")
        assert rows[("2009-12-31", 2)] == MemberRow("2009-12-31", 2, "BET", "link")
        assert rows[("2010-12-31", 2)].source == "filing"

    def test_an_earlier_resolution_stands_over_a_later_one(
        self, three_years: Fund, tmp_path: Path
    ) -> None:
        resolved = {
            ("2010-12-31", 1): MemberRow("2010-12-31", 1, "ALP", "cusip"),
            ("2009-12-31", 1): MemberRow("2009-12-31", 1, "OLD", "hand", "a filing"),
        }
        rows = {row.key: row for row in carry_back(three_years, resolved, tmp_path)}
        assert rows[("2008-12-31", 1)].ticker == "OLD"

    def test_a_row_reaching_no_resolution_is_unmapped(
        self, three_years: Fund, tmp_path: Path
    ) -> None:
        rows = {row.key: row for row in carry_back(three_years, {}, tmp_path)}
        assert rows[("2009-12-31", 2)] == MemberRow("2009-12-31", 2, "", "none")

    def test_a_later_row_resolved_as_none_leaves_the_rows_behind_it_unmapped(
        self, three_years: Fund, tmp_path: Path
    ) -> None:
        resolved = {("2010-12-31", 1): MemberRow("2010-12-31", 1, "", "none")}
        rows = {row.key: row for row in carry_back(three_years, resolved, tmp_path)}
        assert rows[("2008-12-31", 1)] == MemberRow("2008-12-31", 1, "", "none")

    def test_a_resolution_outside_the_panel_is_refused(
        self, three_years: Fund, tmp_path: Path
    ) -> None:
        gone = {("2008-12-31", 2): MemberRow("2008-12-31", 2, "GON", "hand")}
        with pytest.raises(PanelRefused, match="not a row of the panel"):
            carry_back(three_years, gone, tmp_path)


class TestCalendar:
    def test_a_weekend_report_date_takes_the_friday_before(self) -> None:
        days = pd.DatetimeIndex(["2011-12-29", "2011-12-30", "2012-01-03"])
        assert price_date(days, "2011-12-31") == pd.Timestamp("2011-12-30")

    def test_the_exit_is_the_last_trading_day_of_the_next_january(self) -> None:
        assert exit_date(CALENDAR, "2009-12-31") == pd.Timestamp("2010-01-29")

    def test_a_calendar_starting_after_the_report_date_is_refused(self) -> None:
        with pytest.raises(PanelRefused, match="on or before 2000-12-31"):
            price_date(CALENDAR, "2000-12-31")

    def test_a_calendar_ending_on_the_last_friday_of_january_is_refused(self) -> None:
        # 2011-01-31 is a Monday, so a calendar ending on the 28th lacks it.
        short = CALENDAR[CALENDAR <= pd.Timestamp("2011-01-28")]
        with pytest.raises(PanelRefused, match="end of January 2011"):
            exit_date(short, "2010-12-31")

    def test_a_calendar_ending_inside_january_is_refused(self) -> None:
        short = CALENDAR[CALENDAR <= pd.Timestamp("2011-01-20")]
        with pytest.raises(PanelRefused, match="end of January 2011"):
            exit_date(short, "2010-12-31")


def _closes(**series: dict[str, float]) -> pd.DataFrame:
    frame = pd.DataFrame(
        {
            name: pd.Series({pd.Timestamp(day): close for day, close in days.items()})
            for name, days in series.items()
        }
    )
    return frame.sort_index()


def _one(fund: Fund, tmp_path: Path, row: MemberRow, closes: pd.DataFrame) -> MemberRow:
    return check_members(fund, [row], closes, CALENDAR, tmp_path)[0]


class TestCheck:
    def test_an_nq_value_within_half_a_dollar_and_half_a_share_passes(self, tmp_path: Path) -> None:
        # 100,000 shares at 10.00 is 1,000,000. The allowance is $0.50 for the
        # printed value and $5.00 for half a share, so 1,000,005.49 passes.
        fund = _fund(tmp_path, {FIRST: [Holding("Alpha Inc", "100000", "1000000")]})
        row = MemberRow("2008-12-31", 1, "ALP", "hand")
        closes = _closes(ALP={"2008-12-31": 10.0000549, "2009-01-30": 9.0})
        assert _one(fund, tmp_path, row, closes) == MemberRow(
            "2008-12-31", 1, "ALP", "hand", check="pass", exit="close"
        )

    def test_the_whole_share_rounding_of_an_nq_count_passes(self, tmp_path: Path) -> None:
        # Maidenform Brands on 2010-12-31: 325,785 shares at 23.77 is
        # 7,743,909.45, and the N-Q prints 7,743,910.
        fund = _fund(tmp_path, {FIRST: [Holding("Maidenform Brands Inc.", "325785", "7743910")]})
        row = MemberRow("2008-12-31", 1, "MFB", "link")
        assert _one(fund, tmp_path, row, _closes(MFB={"2008-12-31": 23.77})).check == "pass"

    def test_an_nq_close_a_cent_away_fails_with_its_gap_in_cents(self, tmp_path: Path) -> None:
        fund = _fund(tmp_path, {FIRST: [Holding("Alpha Inc", "100000", "1000000")]})
        row = MemberRow("2008-12-31", 1, "ALP", "hand")
        checked = _one(fund, tmp_path, row, _closes(ALP={"2008-12-31": 10.01}))
        assert (checked.check, checked.gap, checked.exit) == ("price", "1.00", "")

    def test_an_nq_value_just_past_the_allowance_fails(self, tmp_path: Path) -> None:
        fund = _fund(tmp_path, {FIRST: [Holding("Alpha Inc", "100000", "1000000")]})
        row = MemberRow("2008-12-31", 1, "ALP", "hand")
        assert _one(fund, tmp_path, row, _closes(ALP={"2008-12-31": 10.000056})).check == "price"

    def test_an_nport_value_must_land_within_half_a_cent(self, tmp_path: Path) -> None:
        fund = _fund(tmp_path, {THIRD: [Holding("Alpha Inc", "100", "1000.00")]})
        row = MemberRow("2010-12-31", 1, "ALP", "cusip")
        assert _one(fund, tmp_path, row, _closes(ALP={"2010-12-31": 10.0})).check == "pass"
        assert _one(fund, tmp_path, row, _closes(ALP={"2010-12-31": 10.0001})).check == "price"

    def test_an_nport_miss_of_exactly_half_a_cent_passes_and_more_fails(
        self, tmp_path: Path
    ) -> None:
        # 100 shares at 20.00005 is 2000.005, half a cent from the filed
        # 2000.00. Read through its repr the close is exact, so the miss sits on
        # the boundary rather than a binary fraction past it.
        fund = _fund(tmp_path, {THIRD: [Holding("Alpha Inc", "100", "2000.00")]})
        row = MemberRow("2010-12-31", 1, "ALP", "cusip")
        assert _one(fund, tmp_path, row, _closes(ALP={"2010-12-31": 20.00005})).check == "pass"
        assert _one(fund, tmp_path, row, _closes(ALP={"2010-12-31": 20.00006})).check == "price"
        assert _one(fund, tmp_path, row, _closes(ALP={"2010-12-31": 20.00004})).check == "pass"

    @pytest.mark.parametrize(
        ("close", "gap"), [(10.0123, "1.23"), (10.01235, "1.24"), (9.98, "-2.00")]
    )
    def test_the_gap_is_the_close_less_the_filed_price_in_cents_to_the_cent(
        self, tmp_path: Path, close: float, gap: str
    ) -> None:
        fund = _fund(tmp_path, {FIRST: [Holding("Alpha Inc", "100000", "1000000")]})
        row = MemberRow("2008-12-31", 1, "ALP", "hand")
        assert _one(fund, tmp_path, row, _closes(ALP={"2008-12-31": close})).gap == gap

    def test_a_missing_close_beside_another_series_is_no_row_and_a_missing_exit_a_stop(
        self, tmp_path: Path
    ) -> None:
        fund = _fund(tmp_path, {FIRST: [Holding("Alpha Inc", "100", "1000")]})
        closes = _closes(
            ALP={"2008-12-30": 10.0, "2009-01-29": 9.0},
            BET={"2008-12-31": 5.0, "2009-01-30": 5.0},
        )
        row = MemberRow("2008-12-31", 1, "ALP", "hand")
        assert _one(fund, tmp_path, row, closes).check == "no-row"
        closes.loc[pd.Timestamp("2008-12-31"), "ALP"] = 10.0
        assert _one(fund, tmp_path, row, closes).exit == "stop"

    def test_a_holding_of_nothing_is_refused(self, tmp_path: Path) -> None:
        fund = _fund(tmp_path, {FIRST: [Holding("Empty Inc", "0", "0")]})
        row = MemberRow("2008-12-31", 1, "EMP", "hand")
        with pytest.raises(PanelRefused, match="holds 0 shares"):
            _one(fund, tmp_path, row, _closes(EMP={"2008-12-31": 10.0}))

    def test_a_half_cent_close_passes_on_nport_cents(self, tmp_path: Path) -> None:
        fund = _fund(tmp_path, {THIRD: [Holding("Half Inc", "1000", "35135.00")]})
        row = MemberRow("2010-12-31", 1, "HLF", "filing")
        assert _one(fund, tmp_path, row, _closes(HLF={"2010-12-31": 35.135})).check == "pass"

    def test_a_series_ending_inside_january_passes_as_a_stop(self, tmp_path: Path) -> None:
        fund = _fund(tmp_path, {FIRST: [Holding("Alpha Inc", "100", "1000")]})
        row = MemberRow("2008-12-31", 1, "ALP", "hand")
        closes = _closes(ALP={"2008-12-31": 10.0, "2009-01-15": 11.0})
        assert _one(fund, tmp_path, row, closes).exit == "stop"

    def test_the_three_ways_to_have_no_close(self, tmp_path: Path) -> None:
        fund = _fund(tmp_path, {FIRST: [Holding("Alpha Inc", "100", "1000")]})
        closes = _closes(ALP={"2008-12-30": 10.0})
        assert _one(fund, tmp_path, MemberRow("2008-12-31", 1, "ALP", "hand"), closes).check == (
            "no-row"
        )
        assert _one(fund, tmp_path, MemberRow("2008-12-31", 1, "XXX", "hand"), closes).check == (
            "no-series"
        )
        assert _one(fund, tmp_path, MemberRow("2008-12-31", 1, "", "none"), closes).check == (
            "unmapped"
        )

    def test_a_reused_ticker_passes_one_member_and_fails_the_other(self, tmp_path: Path) -> None:
        # Laclede and Standard Register, both 2009 members, both under SR.
        fund = _fund(
            tmp_path,
            {
                FIRST: [
                    Holding("Laclede Group Inc. (The)", "291724", "9851519"),
                    Holding("Standard Register Co. (The)", "167339", "853429"),
                ]
            },
        )
        rows = [MemberRow("2008-12-31", 1, "SR", "hand"), MemberRow("2008-12-31", 2, "SR", "hand")]
        checked = check_members(fund, rows, _closes(SR={"2008-12-31": 33.77}), CALENDAR, tmp_path)
        assert [row.check for row in checked] == ["pass", "price"]

    def test_two_members_passing_on_one_ticker_is_refused(self, tmp_path: Path) -> None:
        fund = _fund(
            tmp_path,
            {FIRST: [Holding("Alpha Inc", "100", "1000"), Holding("Alpha Twin", "10", "100")]},
        )
        rows = [
            MemberRow("2008-12-31", 1, "ALP", "hand"),
            MemberRow("2008-12-31", 2, "ALP", "hand"),
        ]
        with pytest.raises(PanelRefused, match="rows 1 and 2 both pass on ALP"):
            check_members(fund, rows, _closes(ALP={"2008-12-31": 10.0}), CALENDAR, tmp_path)

    def test_one_ticker_passing_at_two_year_ends_stands(self, three_years, tmp_path) -> None:
        rows = [
            MemberRow("2008-12-31", 1, "ALP", "link"),
            MemberRow("2009-12-31", 1, "ALP", "link"),
        ]
        closes = _closes(ALP={"2008-12-31": 10.0, "2009-12-31": 12.0})
        checked = check_members(three_years, rows, closes, CALENDAR, tmp_path)
        assert [row.check for row in checked] == ["pass", "pass"]

    def test_a_rerun_replaces_the_previous_result(self, tmp_path: Path) -> None:
        fund = _fund(tmp_path, {FIRST: [Holding("Alpha Inc", "100", "1000")]})
        stale = MemberRow("2008-12-31", 1, "ALP", "hand", check="price", gap="3.00")
        assert _one(fund, tmp_path, stale, _closes(ALP={"2008-12-31": 10.0})).gap == ""


class TestCoverage:
    def _rows(self, alpha_2009: str) -> list[MemberRow]:
        return [
            MemberRow("2008-12-31", 1, "ALP", "link", check="pass", exit="close"),
            MemberRow("2009-12-31", 1, "ALP", "link", **_checked(alpha_2009)),
            MemberRow("2009-12-31", 2, "BET", "link", check="pass", exit="stop"),
            MemberRow("2010-12-31", 1, "ALP", "cusip", check="pass", exit="close"),
            MemberRow("2010-12-31", 2, "", "none", check="unmapped"),
        ]

    def test_a_member_whose_previous_row_failed_misses_for_its_rank_close(
        self, three_years: Fund, tmp_path: Path
    ) -> None:
        second, third = coverage(three_years, self._rows("price"), tmp_path)
        assert (second.members, second.covered, second.misses) == (2, 1, {"price": 1})
        assert second.stops == 1
        assert (third.covered, third.misses) == (0, {"rank": 1, "unmapped": 1})
        assert third.missing == (("2010-12-31", 1), ("2010-12-31", 2))

    def test_an_unchecked_row_is_refused(self, three_years: Fund, tmp_path: Path) -> None:
        rows = [replace(row, check="", exit="") for row in self._rows("pass")]
        with pytest.raises(PanelRefused, match="has not been checked"):
            coverage(three_years, rows, tmp_path)

    def test_a_price_miss_within_a_cent_is_counted_apart(
        self, three_years: Fund, tmp_path: Path
    ) -> None:
        rows = self._rows("price")
        second, _ = coverage(three_years, rows, tmp_path)
        assert second.within_a_cent == 1
        wide = [replace(row, gap="1.01") if row.check == "price" else row for row in rows]
        second, _ = coverage(three_years, wide, tmp_path)
        assert second.within_a_cent == 0

    def test_a_member_new_to_the_index_needs_only_its_own_row(
        self, three_years: Fund, tmp_path: Path
    ) -> None:
        second, _ = coverage(three_years, self._rows("pass"), tmp_path)
        assert (second.covered, second.misses, second.missing) == (2, {}, ())


def _checked(check: str) -> dict[str, str]:
    if check == "pass":
        return {"check": "pass", "exit": "close"}
    return {"check": check, "gap": "1.00" if check == "price" else ""}


class TestThreats:
    def _returns(self) -> dict[tuple[str, int], Decimal | None]:
        values = {("d", n): Decimal(n) for n in range(1, 21)}
        values[("d", 99)] = None
        return values

    def test_the_margin_is_twice_a_tenth_of_the_universe_from_each_end(self) -> None:
        # A tenth of 20 is 2, so the margin is 4 from each end: 1 to 4 and 17 to 20.
        returns = self._returns()
        missing = [("d", n) for n in (4, 5, 16, 17)]
        assert threats(returns, missing, universe=20) == [("d", 4), ("d", 17)]

    def test_a_member_that_cannot_be_placed_always_threatens(self) -> None:
        assert threats(self._returns(), [("d", 99), ("d", 10)], universe=20) == [("d", 99)]

    def test_the_tenth_rounds_half_away_from_zero(self) -> None:
        # A tenth of 25 is 2.5, which MATLAB rounds to 3, so the margin is 6.
        returns = self._returns()
        assert threats(returns, [("d", 6), ("d", 7)], universe=25) == [("d", 6)]

    def test_a_universe_too_small_for_a_tenth_flags_only_the_unplaced(self) -> None:
        returns = {("d", 1): None, ("d", 2): Decimal(1)}
        assert threats(returns, [("d", 1), ("d", 2)], universe=4) == [("d", 1)]

    def test_fewer_placed_members_than_the_margin_all_threaten(self) -> None:
        returns = {("d", n): Decimal(n) for n in (1, 2, 3)}
        assert threats(returns, [("d", 2)], universe=20) == [("d", 2)]

    def test_a_tie_at_the_boundary_threatens(self) -> None:
        # A tenth of 5 rounds to 1, so the margin is 2, and the third of three
        # members tied at the lowest return sits third yet still threatens.
        returns = {("d", n): Decimal(1) for n in (1, 2, 3)}
        returns.update({("d", n): Decimal(n) for n in range(4, 11)})
        assert threats(returns, [("d", 3), ("d", 4)], universe=5) == [("d", 3)]


class TestTheRecord:
    def test_a_file_round_trips(self, tmp_path: Path) -> None:
        rows = [
            MemberRow(
                "2009-12-31", 2, "SR", "hand", "Standard Register's 10-K", "price", "-2867.00"
            ),
            MemberRow("2009-12-31", 1, "SR", "hand", "", "pass", "", "close"),
        ]
        path = tmp_path / "members.csv"
        path.write_bytes(serialize_members(rows))
        assert path.read_text().splitlines()[0] == ",".join(COLUMNS)
        assert read_members(path) == (rows[1], rows[0])

    @pytest.mark.parametrize(
        ("line", "problem"),
        [
            ("2009-12-31,1,SR,guess,,,,", "source 'guess'"),
            ("2009-12-31,1,,hand,,,,", "empty exactly when the source is none"),
            ("2009-12-31,1,SR,hand,,price,,", "gap is given on a price row"),
            ("2009-12-31,1,SR,hand,,no-row,,stop", "exit is close or stop on a pass row"),
            ("2009-12-31,1,SR,hand,,pass,,", "exit is close or stop on a pass row"),
            ("2009-12-31,1,sr,hand,,,,", "SYMBOL_PATTERN"),
            ("2009-12-31,1,SR,hand,,maybe,,", "check 'maybe'"),
            ("2009-12-31,1,SR,none,,,,", "empty exactly when the source is none"),
            ("2009-12-31,1,SR,hand,,no-row,1.00,", "gap is given on a price row"),
            ("2009-12-31,1,SR,hand,,pass,,maybe", "exit is close or stop on a pass row"),
            ("2009-12-31,x,SR,hand,,,,", "row 'x' is not a number"),
        ],
    )
    def test_a_malformed_line_is_refused_by_number(
        self, tmp_path: Path, line: str, problem: str
    ) -> None:
        path = tmp_path / "members.csv"
        path.write_text(",".join(COLUMNS) + "\n" + line + "\n")
        with pytest.raises(PanelRefused, match=f"line 2: .*{problem}"):
            read_members(path)

    def test_a_header_in_another_order_is_refused(self, tmp_path: Path) -> None:
        path = tmp_path / "members.csv"
        path.write_text(",".join(reversed(COLUMNS)) + "\n")
        with pytest.raises(PanelRefused, match="has columns"):
            read_members(path)

    def test_a_file_that_is_not_the_panel_is_refused(self, three_years: Fund, tmp_path) -> None:
        rows = carry_back(three_years, {}, tmp_path)
        require_panel(three_years, rows, tmp_path)
        with pytest.raises(PanelRefused, match="lacks 1 they do, the first"):
            require_panel(three_years, rows[1:], tmp_path)
        stray = [*rows, MemberRow("2009-12-31", 9, "", "none")]
        with pytest.raises(PanelRefused, match="names 1 rows the filings do not hold"):
            require_panel(three_years, stray, tmp_path)

    def test_a_key_given_twice_is_refused(self, tmp_path: Path) -> None:
        path = tmp_path / "members.csv"
        line = "2009-12-31,1,SR,hand,,,,"
        path.write_text(",".join(COLUMNS) + "\n" + line + "\n" + line + "\n")
        with pytest.raises(PanelRefused, match="more than once"):
            read_members(path)
