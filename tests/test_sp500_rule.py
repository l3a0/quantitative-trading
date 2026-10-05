"""The month-by-month coverage rule of the S&P 500 panel, on synthetic series that run in CI.

:mod:`chan.sp500_panel` says which of IVV's members Example 7.7 can rank at a
month-end. These tests hold each part of that rule on made-up spans, holes and
links, against IVV's own list of schedules, so none of them reads the archive
or the members file. ``tests/test_sp500_panel.py`` pins what the rule gives on
the committed record.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from chan import sp500_panel
from chan.fund_panel import MemberRow, PanelRefused
from chan.sp500_panel import (
    _Closes,
    _reason,
    exit_close,
    find_holes,
    last_month_set,
    month_end,
    months,
    read_holes,
    serialize_holes,
    setter,
)

#: Weekdays from November 2007 to October 2026, standing in for an exchange
#: calendar. 2026-09-30 is a Wednesday.
CALENDAR = pd.bdate_range("2007-11-01", "2026-10-15")

FIRST_SCHEDULE = pd.Period("2008-12", "M")


def _month(text: str) -> pd.Period:
    return pd.Period(text, "M")


def _closes(spans: dict[str, tuple[str, str]], holes=()) -> _Closes:
    return _Closes(spans, frozenset(holes), CALENDAR)


def _row(report_date: str, row: int = 1, ticker: str = "ALP", check: str = "pass") -> MemberRow:
    if check == "pass":
        return MemberRow(report_date, row, ticker, "hand", check="pass", exit="close")
    return MemberRow(report_date, row, ticker, "hand", check=check)


#: A series running across the whole span.
WHOLE = {"ALP": ("2000-01-03", "2026-10-15")}


class TestTheSchedules:
    def test_a_schedule_sets_its_own_month_and_the_two_after(self) -> None:
        assert [setter(_month(m)) for m in ("2009-02", "2009-03", "2009-05", "2009-06")] == [
            "2008-12-31",
            "2009-03-31",
            "2009-03-31",
            "2009-06-30",
        ]

    def test_2013_06_30_sets_six_months_because_2013_09_30_is_skipped(self) -> None:
        assert setter(_month("2013-11")) == "2013-06-30"
        assert setter(_month("2013-12")) == "2013-12-31"
        assert last_month_set("2013-06-30") == _month("2013-11")

    def test_no_schedule_sets_a_month_before_the_first(self) -> None:
        assert setter(_month("2008-11")) is None

    def test_the_last_schedule_sets_through_august_2026(self) -> None:
        assert last_month_set("2026-06-30") == _month("2026-08")

    def test_the_span_is_213_month_ends(self) -> None:
        span = months()
        assert (len(span), str(span[0]), str(span[-1])) == (213, "2008-12", "2026-08")


class TestTheCalendar:
    def test_a_month_end_is_the_last_trading_day_in_the_month(self) -> None:
        assert month_end(CALENDAR, _month("2013-03")) == pd.Timestamp("2013-03-29")

    def test_a_calendar_ending_inside_the_month_is_refused(self) -> None:
        short = CALENDAR[CALENDAR <= pd.Timestamp("2026-09-30")]
        with pytest.raises(PanelRefused, match="does not run past 2026-09"):
            month_end(short, _month("2026-09"))

    @pytest.mark.parametrize(
        ("report_date", "day"),
        [
            ("2009-03-31", "2009-06-30"),
            ("2013-06-30", "2013-12-31"),
            ("2026-06-30", "2026-09-30"),
        ],
    )
    def test_the_exit_is_the_month_end_after_the_last_month_a_schedule_sets(
        self, report_date: str, day: str
    ) -> None:
        assert exit_close(CALENDAR, report_date) == pd.Timestamp(day)


class TestTheReasons:
    """Each reason, on a member of the 2010-03-31 schedule ranked at March 2010."""

    MARCH = _month("2010-03")

    def _reason(self, row: MemberRow, spans=WHOLE, holes=(), previous=None, rows=()) -> str | None:
        by_key = {item.key: item for item in (row, *rows)}
        return _reason(
            row, self.MARCH, _closes(spans, holes), by_key, previous or {}, FIRST_SCHEDULE
        )

    def test_a_whole_series_new_to_the_index_is_covered(self) -> None:
        assert self._reason(_row("2010-03-31")) is None

    @pytest.mark.parametrize("check", ["price", "no-row", "no-series", "unmapped"])
    def test_a_failed_check_misses_with_its_outcome(self, check: str) -> None:
        assert self._reason(_row("2010-03-31", check=check)) == check

    def test_a_series_that_ended_before_the_month_end_has_stopped(self) -> None:
        spans = {"ALP": ("2000-01-03", "2010-03-15")}
        assert self._reason(_row("2010-03-31"), spans) == "stopped"

    def test_a_series_running_past_a_month_end_with_no_row_on_it_misses_its_close(self) -> None:
        assert self._reason(_row("2010-03-31"), holes=[("ALP", "2010-03")]) == "close"

    @pytest.mark.parametrize("back", ["2009-03", "2009-04"])
    def test_a_missing_year_earlier_close_misses_its_rank(self, back: str) -> None:
        assert self._reason(_row("2010-03-31"), holes=[("ALP", back)]) == "rank"

    def test_a_series_starting_after_the_year_earlier_month_misses_its_rank(self) -> None:
        spans = {"ALP": ("2009-04-01", "2026-10-15")}
        assert self._reason(_row("2010-03-31"), spans) == "rank"

    def test_a_year_earlier_close_rests_on_the_row_it_links_back_to(self) -> None:
        """March 2009 and April 2009 are both set by 2009-03-31, three links back."""
        chain = {
            ("2010-03-31", 1): ("2009-12-31", 4),
            ("2009-12-31", 4): ("2009-09-30", 7),
            ("2009-09-30", 7): ("2009-06-30", 2),
            ("2009-06-30", 2): ("2009-03-31", 9),
        }
        between = [_row("2009-12-31", 4), _row("2009-09-30", 7), _row("2009-06-30", 2)]
        passed = [*between, _row("2009-03-31", 9)]
        assert self._reason(_row("2010-03-31"), previous=chain, rows=passed) is None
        failed = [*between, _row("2009-03-31", 9, check="price")]
        assert self._reason(_row("2010-03-31"), previous=chain, rows=failed) == "rank"
        elsewhere = [*between, _row("2009-03-31", 9, ticker="OTHER")]
        assert self._reason(_row("2010-03-31"), previous=chain, rows=elsewhere) == "rank"

    def test_a_chain_that_breaks_before_the_year_earlier_month_ranks_on_the_series(self) -> None:
        chain = {("2010-03-31", 1): ("2009-12-31", 4)}
        rows = [_row("2009-12-31", 4)]
        assert self._reason(_row("2010-03-31"), previous=chain, rows=rows) is None

    def test_a_hole_at_the_next_month_end_misses_and_an_end_inside_the_month_stops(
        self,
    ) -> None:
        assert self._reason(_row("2010-03-31"), holes=[("ALP", "2010-04")]) == "next"
        ends = {"ALP": ("2000-01-03", "2010-04-14")}
        assert self._reason(_row("2010-03-31"), ends) is None

    def test_a_month_before_the_first_schedule_ranks_on_the_series_alone(self) -> None:
        """December 2008 reads December 2007 and January 2008, which no schedule sets."""
        row = _row("2008-12-31")
        by_key = {row.key: row}
        closes = _closes(WHOLE)
        assert _reason(row, _month("2008-12"), closes, by_key, {}, FIRST_SCHEDULE) is None
        holed = _closes(WHOLE, [("ALP", "2007-12")])
        assert _reason(row, _month("2008-12"), holed, by_key, {}, FIRST_SCHEDULE) == "rank"


class TestTheHoles:
    def test_a_missing_month_end_inside_a_span_is_a_hole_and_outside_is_not(self) -> None:
        days = CALENDAR[(CALENDAR >= "2007-11-01") & (CALENDAR <= "2026-10-15")]
        series = pd.Series(1.0, index=days)
        series[pd.Timestamp("2015-06-30")] = float("nan")
        frame = pd.DataFrame({"ALP": series, "BET": series.where(days <= "2012-01-10")})
        spans = {"ALP": ("2007-11-01", "2026-10-15"), "BET": ("2007-11-01", "2012-01-10")}
        assert find_holes(frame, spans, CALENDAR) == {("ALP", "2015-06")}

    def test_the_file_round_trips_sorted(self, tmp_path: Path) -> None:
        path = tmp_path / "holes.csv"
        path.write_bytes(serialize_holes([("BET", "2010-01"), ("ALP", "2015-06")]))
        assert path.read_text() == "ticker,month\nALP,2015-06\nBET,2010-01\n"
        assert read_holes(path) == {("ALP", "2015-06"), ("BET", "2010-01")}

    def test_a_file_with_other_columns_is_refused(self, tmp_path: Path) -> None:
        path = tmp_path / "holes.csv"
        path.write_text("symbol,month\n")
        with pytest.raises(PanelRefused, match="has columns"):
            read_holes(path)


class TestTheCrossSection:
    def test_the_panel_writes_to_the_sp500_cross_section_the_owner_ruled_in(self) -> None:
        from chan.archive import CROSS_SECTIONS

        assert sp500_panel.CROSS_SECTION == "sp500"
        assert CROSS_SECTIONS == ("sp600", "sp500")
