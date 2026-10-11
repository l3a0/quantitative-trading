"""The pins for the VIX filter at location 3509 of *Algorithmic Trading*.

This file is the single authority for every number a prose surface quotes
about this replication, apart from Example 7.1's full-calendar figures, which
``tests/test_opening_gap.py`` holds. ``docs/replication-log.md`` Entry 47
carries the verdicts and points here row by row.

Every pin on the committed files reads three vintages and one specification
unless it names another, so they are stated once here.

- **VIX.** ``vix/vix.csv``, lifted from Chan's ``VIX.csv``, chan-csv,
  ``raw``, saved 2012-05-09, 5,635 rows from 1990-01-02 to 2012-05-08, read
  through ``chan.series.load_panel`` as the column ``VIX``.
- **The stocks.** ``inputdataohlcdaily_stocks_20120424/``, the 497 stocks of
  ``inputDataOHLCDaily_stocks_20120424.mat``, chan-mat, adjusted, saved
  2012-04-25, 1,500 days from 2006-05-11 to 2012-04-24, run through
  ``chan.buy_on_gap`` unchanged. Every figure on it is about survivors.
- **FSTX.** ``inputdataohlcdaily_20120517/fstx.csv``, chan-mat, adjusted,
  saved 2012-05-18, 2,000 days from 2004-07-16 to 2012-05-17, run through
  ``chan.opening_gap`` unchanged under both readings of its return line.
- **Specification.** Each rule runs on its full calendar, and its daily
  returns are taken on the days its calendar shares with VIX's, MATLAB's
  ``intersect``. A day is kept when ``backshift(1, vix) > 35`` on that joined
  calendar, strictly above and with NaN keeping nothing. The return figure is
  ``252 · mean`` over the kept days and the Sharpe ratio
  ``√252 · mean / std`` over them, with the std dividing by n − 1, no
  risk-free rate and no cost.

No script ships for location 3509. The FSTX alignment was chosen after six
alignments and two averages were tried, and ``TestTheReadingsThatMiss`` pins
all five alignments and the average that were set aside, each with its
reason. Two of the alignments read VIX on the trade's own date, which looks
ahead, and ``TestTheRules`` holds which close each alignment reads.

Each computed figure is held at six decimals, and each published figure at
the precision Chan printed it, through ``matches``.

Exploratory. Reproducing Chan's figures spends his samples on his rules and
his threshold. The run first ran here on 2026-10-11.
"""

from __future__ import annotations

import io
import math
from contextlib import redirect_stdout

import numpy as np
import pandas as pd
import pytest

from chan import buy_on_gap, opening_gap, paths
from chan import vix_filter as module
from chan.khandani_lo_book_two import gap, matches
from chan.matlab_helpers import backshift
from chan.series import (
    SCALE_BREAK_BOUND,
    WindowCrossesScaleBreak,
    refuse_window_crossing_a_break,
    scale_breaks,
)
from chan.vintage import VintageUnavailable
from chan.vix_filter import (
    BEFORE_FLAG,
    BOOK_BUY_ON_GAP_PERCENT,
    BOOK_BUY_ON_GAP_SHARPE,
    BOOK_FSTX_PERCENT,
    BOOK_FSTX_SHARPE,
    FLAGGED_DAY,
    THRESHOLD,
    VIX_FILE,
    Filtered,
    VixFilter,
    as_of_reading,
    common_days,
    forward_filled_reading,
    guarded_spans,
    latest_close_before,
    main,
    own_calendar_reading,
    qualifies,
    read_sources,
    reading,
    run,
    same_day_reading,
    vix_filter,
    vix_filters,
)
from tests.support.committed_vintages import LIFTED_SOURCES

#: Six decimals, the precision every computed pin is held at.
SIX = 1e-6

day = pd.Timestamp

#: VIX's last close, and the last day the buy-on-gap panel holds.
VIX_LAST = day("2012-05-08")
STOCKS_LAST = day("2012-04-24")


@pytest.fixture(scope="module")
def sources() -> module.Sources:
    return read_sources()


@pytest.fixture(scope="module")
def result(sources) -> VixFilter:
    return vix_filters(sources)


@pytest.fixture(scope="module")
def fstx_rule(sources) -> opening_gap.OpeningGap:
    return opening_gap.opening_gap(sources.fstx)


@pytest.fixture(scope="module")
def printed() -> str:
    """What ``run`` prints, captured once for the tests that read it."""
    out = io.StringIO()
    with redirect_stdout(out):
        run()
    return out.getvalue()


@pytest.fixture
def no_arguments(monkeypatch):
    """``main`` parses ``sys.argv``, which under pytest holds pytest's own arguments."""
    monkeypatch.setattr("sys.argv", ["chan.vix_filter"])


class TestTheVintages:
    def test_vix_is_its_pinned_source(self, sources) -> None:
        vendor, basis, saved, folder, _ = LIFTED_SOURCES[VIX_FILE]
        assert (vendor, basis, saved, folder) == ("chan-csv", "raw", "2012-05-09", "vix")
        member = sources.vix_member
        assert member.symbol == "VIX"
        assert (member.vendor, member.price_basis, member.obtained) == (vendor, basis, saved)
        assert member.path == "vix/vix.csv"

    def test_vix_holds_5635_closes(self, sources) -> None:
        assert len(sources.vix) == 5635
        assert sources.vix.notna().all()
        assert (sources.vix.index[0], sources.vix.index[-1]) == (day("1990-01-02"), VIX_LAST)

    def test_the_stocks_are_buy_on_gap_s_panel(self, sources) -> None:
        vendor, basis, saved, folder, _ = LIFTED_SOURCES[buy_on_gap.PRICE_FILE]
        assert len(sources.stock_members) == 497
        assert {(m.vendor, m.price_basis, m.obtained) for m in sources.stock_members} == {
            (vendor, basis, saved)
        }
        assert saved == "2012-04-25"
        assert {m.path.split("/")[0] for m in sources.stock_members} == {folder}
        days = sources.stocks["Close"].index
        assert (len(days), days[0], days[-1]) == (1500, day("2006-05-11"), STOCKS_LAST)

    def test_fstx_is_the_opening_gap_s_save(self, sources) -> None:
        vendor, basis, saved, folder, _ = LIFTED_SOURCES[opening_gap.SOURCE_FILE]
        member = sources.fstx_member
        assert (member.vendor, member.price_basis, member.obtained) == (vendor, basis, saved)
        assert saved == "2012-05-18"
        assert member.path == f"{folder}/fstx.csv"
        assert (len(sources.fstx), sources.fstx.index[0], sources.fstx.index[-1]) == (
            2000,
            day("2004-07-16"),
            day("2012-05-17"),
        )


class TestTheJoin:
    """Row 13: the calendar each rule keeps once it is joined to VIX's."""

    def test_buy_on_gap_keeps_all_1500_days(self, result) -> None:
        long = result.buy_on_gap
        assert (len(long.days), long.calendar_days) == (1500, 1500)

    def test_buy_on_gap_s_calendar_is_vix_s_over_its_span(self, sources) -> None:
        """So an alignment that reads the previous day changes only the first day's close.

        The join reads NaN on 2006-05-11 and the latest close before it reads
        11.78, and neither keeps the day.
        """
        days, vix = sources.stocks["Close"].index, sources.vix
        assert vix.loc[days[0] : days[-1]].index.equals(days)
        joined = backshift(1, vix.reindex(days).to_numpy(dtype=float))
        latest = latest_close_before(days, vix)
        assert (joined[1:] == latest[1:]).all()
        assert days[0] == day("2006-05-11")
        assert np.isnan(joined[0])
        assert latest[0] == 11.78 < THRESHOLD

    def test_fstx_keeps_1945_of_its_2000_days(self, result) -> None:
        literal = result.literal
        assert (len(literal.days), literal.calendar_days) == (1945, 2000)
        assert (literal.days[0], literal.days[-1]) == (day("2004-07-16"), VIX_LAST)
        assert result.momentum.days.equals(literal.days)

    def test_fstx_loses_7_days_after_vix_ends_and_48_the_cboe_did_not_trade(self, sources) -> None:
        lost = sources.fstx.index.difference(sources.vix.index)
        assert len(lost) == 55
        after = lost[lost > VIX_LAST]
        assert list(after) == list(pd.bdate_range("2012-05-09", "2012-05-17"))
        before = lost[lost <= VIX_LAST]
        assert len(before) == 48
        # US market holidays such as Independence Day and Thanksgiving.
        assert {day("2005-07-04"), day("2008-11-27"), day("2012-02-20")} <= set(before)

    def test_vix_holds_24_days_in_fstx_s_window_that_fstx_does_not(self, sources) -> None:
        fstx = sources.fstx.index
        extra = sources.vix.loc[fstx[0] : fstx[-1]].index.difference(fstx)
        assert len(extra) == 24

    def test_the_join_takes_each_rule_s_own_returns_on_the_shared_days(
        self, result, fstx_rule
    ) -> None:
        rows = fstx_rule.days.get_indexer(result.literal.days)
        assert (result.literal.daily == fstx_rule.literal[rows]).all()
        assert (result.momentum.daily == fstx_rule.momentum[rows]).all()
        assert (result.literal.held == (fstx_rule.positions[rows] != 0)).all()


class TestTheSpecification:
    """Rows 1 to 4: both rules on the days after a VIX close above 35."""

    def test_the_threshold_is_35(self) -> None:
        assert THRESHOLD == 35

    def test_buy_on_gap_keeps_190_days(self, result) -> None:
        assert result.buy_on_gap.kept == 190

    def test_buy_on_gap_s_return_is_chans_17_2_percent(self, result) -> None:
        long = result.buy_on_gap
        assert long.average_annual_return == pytest.approx(0.171924, abs=SIX)
        assert BOOK_BUY_ON_GAP_PERCENT == "17.2"
        assert matches(100 * long.average_annual_return, BOOK_BUY_ON_GAP_PERCENT)

    def test_buy_on_gap_s_sharpe_ratio_is_chans_1_4(self, result) -> None:
        long = result.buy_on_gap
        assert long.sharpe == pytest.approx(1.417425, abs=SIX)
        assert BOOK_BUY_ON_GAP_SHARPE == "1.4"
        assert matches(long.sharpe, BOOK_BUY_ON_GAP_SHARPE)

    def test_fstx_keeps_185_days(self, result) -> None:
        assert result.literal.kept == result.momentum.kept == 185

    def test_fstx_s_return_is_chans_2_6_percent_under_the_script_s_sign(self, result) -> None:
        literal = result.literal
        assert literal.average_annual_return == pytest.approx(0.025730, abs=SIX)
        assert BOOK_FSTX_PERCENT == "2.6"
        assert matches(100 * literal.average_annual_return, BOOK_FSTX_PERCENT)

    def test_fstx_s_sharpe_ratio_is_chans_0_16_under_the_script_s_sign(self, result) -> None:
        literal = result.literal
        assert literal.sharpe == pytest.approx(0.164869, abs=SIX)
        assert BOOK_FSTX_SHARPE == "0.16"
        assert matches(literal.sharpe, BOOK_FSTX_SHARPE)

    def test_every_gap_is_zero_with_the_sign_the_log_prints(self, result) -> None:
        """The replication log's verdict table, computed minus printed at the printed precision."""
        long, literal = result.buy_on_gap, result.literal
        gaps = [
            gap(100 * long.average_annual_return, BOOK_BUY_ON_GAP_PERCENT),
            gap(long.sharpe, BOOK_BUY_ON_GAP_SHARPE),
            gap(100 * literal.average_annual_return, BOOK_FSTX_PERCENT),
            gap(literal.sharpe, BOOK_FSTX_SHARPE),
        ]
        assert gaps == [0.0] * 4
        assert [math.copysign(1, g) for g in gaps] == [-1, 1, -1, 1]

    @pytest.mark.parametrize("rule", ["buy_on_gap", "literal"])
    def test_the_figures_are_252_times_the_mean_and_the_n_minus_1_sharpe_on_the_kept_days(
        self, result, rule
    ) -> None:
        filtered = getattr(result, rule)
        kept = filtered.daily[filtered.qualifies]
        assert filtered.average_annual_return == pytest.approx(252 * kept.mean(), abs=1e-15)
        assert filtered.sharpe == pytest.approx(
            math.sqrt(252) * kept.mean() / kept.std(ddof=1), abs=1e-12
        )

    def test_a_kept_day_follows_a_joined_day_closing_above_35(self, sources, result) -> None:
        for filtered in (result.buy_on_gap, result.literal):
            closes = sources.vix.reindex(filtered.days).to_numpy()
            rows = np.flatnonzero(filtered.qualifies)
            assert rows.min() > 0
            assert (closes[rows - 1] > 35).all()
            assert (closes[np.flatnonzero(~filtered.qualifies[1:])] <= 35).all()

    def test_the_rule_run_after_the_join_keeps_the_same_fstx_returns(
        self, sources, result, fstx_rule
    ) -> None:
        """Eleven joined days move and none of the 185 kept days does.

        Ten of the eleven are the first joined day after one of the 48 days
        the CBOE did not trade, where the open is set against the high or low
        of two sessions back. Holding the full calendar's spread, that alone
        moves those ten. The eleventh, 2005-09-20, moves through the 90-day
        spread alone. The 7 days after 2012-05-08 follow every joined day, so
        dropping them moves nothing.
        """
        literal = result.literal
        joined = literal.days
        frame = sources.fstx.loc[joined]
        after = opening_gap.opening_gap(frame)
        assert (after.literal[literal.qualifies] == literal.filtered).all()
        assert (after.momentum[literal.qualifies] == result.momentum.filtered).all()
        moved = after.literal != literal.daily
        assert int(moved.sum()) == 11
        assert not moved[literal.qualifies].any()
        lost = sources.fstx.index.difference(sources.vix.index)
        full = fstx_rule.days
        after_a_lost_day = np.array([full[full.get_loc(d) - 1] in lost for d in joined])
        assert int((moved & after_a_lost_day).sum()) == 10
        assert list(joined[moved & ~after_a_lost_day]) == [day("2005-09-20")]
        rows = full.get_indexer(joined)
        op, hi, lo = (frame[f].to_numpy(dtype=float) for f in ("Open", "High", "Low"))
        bar_only = opening_gap.positions(op, hi, lo, fstx_rule.spread[rows])
        assert list(joined[bar_only != fstx_rule.positions[rows]]) == list(
            joined[moved & after_a_lost_day]
        )
        assert int((lost > joined[-1]).sum()) == 7


class TestTheClaim:
    """Row 5: the momentum sign location 2965 describes does not earn location 3509's figures."""

    def test_the_momentum_sign_s_figures(self, result) -> None:
        momentum = result.momentum
        assert momentum.average_annual_return == pytest.approx(-0.025730, abs=SIX)
        assert momentum.sharpe == pytest.approx(-0.164869, abs=SIX)

    def test_neither_lands_the_book(self, result) -> None:
        momentum = result.momentum
        assert not matches(100 * momentum.average_annual_return, BOOK_FSTX_PERCENT)
        assert not matches(momentum.sharpe, BOOK_FSTX_SHARPE)
        assert gap(100 * momentum.average_annual_return, BOOK_FSTX_PERCENT) == -5.2
        assert gap(momentum.sharpe, BOOK_FSTX_SHARPE) == -0.32

    def test_the_momentum_returns_are_the_literal_ones_negated(self, result) -> None:
        assert (result.momentum.daily == -result.literal.daily).all()

    def test_the_momentum_sign_loses_on_the_joined_calendar(self, result) -> None:
        """252 times the mean over all 1,945 joined days, beside the kept days' −0.025730."""
        joined = result.momentum.unfiltered
        assert joined.kept == 1945
        assert joined.average_annual_return == pytest.approx(-0.139950, abs=SIX)


class TestTheReadingsThatMiss:
    """Rows 6 to 12: each reading set aside, and why."""

    def test_the_compounded_apr_prints_17_9_not_17_2(self, result) -> None:
        """Row 6. So location 3509's filtered figure is 252 times the mean.

        Entry 18 found the same sentence's unfiltered 8.7 percent to be the
        compounded APR, so the phrase names both formulas.
        """
        long = result.buy_on_gap
        assert long.apr == pytest.approx(0.179297, abs=SIX)
        assert not matches(100 * long.apr, BOOK_BUY_ON_GAP_PERCENT)
        assert matches(100 * long.apr, "17.9")
        assert gap(100 * long.apr, BOOK_BUY_ON_GAP_PERCENT) == 0.7
        assert result.literal.apr == pytest.approx(0.013762, abs=SIX)

    def test_zeroing_the_other_days_lands_neither_rule(self, result) -> None:
        """Row 7. So the average is taken over the kept days alone."""
        long, literal = result.buy_on_gap.zeroed, result.literal.zeroed
        assert long.kept == 1500
        assert long.average_annual_return == pytest.approx(0.021777, abs=SIX)
        assert long.sharpe == pytest.approx(0.503869, abs=SIX)
        assert matches(100 * long.average_annual_return, "2.2")
        assert gap(100 * long.average_annual_return, BOOK_BUY_ON_GAP_PERCENT) == -15.0
        assert gap(long.sharpe, BOOK_BUY_ON_GAP_SHARPE) == -0.9
        assert literal.kept == 1945
        assert literal.average_annual_return == pytest.approx(0.002447, abs=SIX)
        assert literal.sharpe == pytest.approx(0.050969, abs=SIX)
        assert not matches(100 * literal.average_annual_return, BOOK_FSTX_PERCENT)
        assert not matches(literal.sharpe, BOOK_FSTX_SHARPE)
        assert gap(100 * literal.average_annual_return, BOOK_FSTX_PERCENT) == -2.4
        assert gap(literal.sharpe, BOOK_FSTX_SHARPE) == -0.11

    def test_the_latest_close_before_each_day_prints_2_5(self, result) -> None:
        """Row 8. The Sharpe ratio lands and the return misses, so the join is the reading."""
        as_of = result.as_of
        assert as_of.kept == 188
        assert as_of.average_annual_return == pytest.approx(0.025319, abs=SIX)
        assert as_of.sharpe == pytest.approx(0.163555, abs=SIX)
        assert not matches(100 * as_of.average_annual_return, BOOK_FSTX_PERCENT)
        assert matches(100 * as_of.average_annual_return, "2.5")
        assert gap(100 * as_of.average_annual_return, BOOK_FSTX_PERCENT) == -0.1
        assert matches(as_of.sharpe, BOOK_FSTX_SHARPE)
        sharpe_gap = gap(as_of.sharpe, BOOK_FSTX_SHARPE)
        assert sharpe_gap == 0.0
        assert math.copysign(1, sharpe_gap) == 1

    def test_the_latest_close_reading_adds_three_us_holidays(
        self, sources, result, fstx_rule
    ) -> None:
        """Eurex traded on them and the CBOE did not, so the join drops them."""
        with np.errstate(invalid="ignore"):
            keep = latest_close_before(fstx_rule.days, sources.vix) > THRESHOLD
        extra = fstx_rule.days[keep].difference(result.literal.kept_days)
        assert list(extra) == [day("2008-11-27"), day("2009-01-19"), day("2009-02-16")]
        assert result.literal.kept_days.difference(fstx_rule.days[keep]).empty

    def test_vix_forward_filled_one_row_back_keeps_the_latest_close_s_days(
        self, sources, result, fstx_rule
    ) -> None:
        """Row 10. The second alignment set aside gives the first one's figures, day for day."""
        days = fstx_rule.days
        filled = qualifies(sources.vix.reindex(days, method="ffill").to_numpy())
        with np.errstate(invalid="ignore"):
            latest = latest_close_before(days, sources.vix) > THRESHOLD
        assert (filled == latest).all()
        assert result.forward_filled == result.as_of
        assert result.forward_filled.kept == 188

    def test_the_forward_fill_and_the_latest_close_read_different_closes_on_23_days(
        self, sources, fstx_rule
    ) -> None:
        """FSTX's first day, and 22 days after one the CBOE traded and Eurex did not.

        None of them moves a close across 35. The nearest is 2009-05-04, which
        reads 35.30 as the latest close and 36.50 forward-filled, both above.
        """
        days, vix = fstx_rule.days, sources.vix
        filled = backshift(1, vix.reindex(days, method="ffill").to_numpy(dtype=float))
        latest = latest_close_before(days, vix)
        differ = np.flatnonzero(~((filled == latest) | (np.isnan(filled) & np.isnan(latest))))
        assert len(differ) == 23
        assert differ[0] == 0
        assert np.isnan(filled[0])
        assert latest[0] == vix.loc[day("2004-07-15")] < THRESHOLD
        only_vix = vix.index.difference(days)
        for row in differ[1:]:
            assert ((only_vix > days[row - 1]) & (only_vix < days[row])).any()
            assert (filled[row] > THRESHOLD) == (latest[row] > THRESHOLD)
        nearest = days.get_loc(day("2009-05-04"))
        assert (latest[nearest], filled[nearest]) == (35.30, 36.50)

    def test_the_own_calendar_reading_swaps_the_day_after_each_holiday_for_the_holiday(
        self, sources, result, fstx_rule
    ) -> None:
        keep = qualifies(sources.vix.reindex(fstx_rule.days).to_numpy())
        own = fstx_rule.days[keep]
        joined = result.literal.kept_days
        assert list(own.difference(joined)) == [
            day("2008-11-27"),
            day("2009-01-19"),
            day("2009-02-16"),
        ]
        assert list(joined.difference(own)) == [
            day("2008-11-28"),
            day("2009-01-20"),
            day("2009-02-17"),
        ]

    def test_one_row_back_on_fstx_s_own_calendar_lands_neither(self, result) -> None:
        """Row 9. A day after a US holiday reads the holiday's missing close."""
        own = result.own_calendar
        assert own.kept == 185
        assert own.average_annual_return == pytest.approx(0.045238, abs=SIX)
        assert own.sharpe == pytest.approx(0.291589, abs=SIX)
        assert gap(100 * own.average_annual_return, BOOK_FSTX_PERCENT) == 1.9
        assert gap(own.sharpe, BOOK_FSTX_SHARPE) == 0.13

    def test_same_day_vix_with_nan_on_holidays_is_negative(self, result) -> None:
        """Row 11. The fourth alignment set aside, which looks ahead before any figure is read."""
        same = result.same_day
        assert same.kept == 185
        assert same.average_annual_return == pytest.approx(-0.047063, abs=SIX)
        assert same.sharpe == pytest.approx(-0.297416, abs=SIX)
        assert gap(100 * same.average_annual_return, BOOK_FSTX_PERCENT) == -7.3
        assert gap(same.sharpe, BOOK_FSTX_SHARPE) == -0.46

    def test_same_day_vix_forward_filled_is_negative(self, result) -> None:
        """Row 12. The fifth alignment set aside, which looks ahead before any figure is read."""
        same = result.same_day_filled
        assert same.kept == 188
        assert same.average_annual_return == pytest.approx(-0.046312, abs=SIX)
        assert same.sharpe == pytest.approx(-0.295046, abs=SIX)
        assert gap(100 * same.average_annual_return, BOOK_FSTX_PERCENT) == -7.2
        assert gap(same.sharpe, BOOK_FSTX_SHARPE) == -0.46

    def test_the_same_day_readings_read_vix_on_the_trade_s_own_date(
        self, sources, result, fstx_rule
    ) -> None:
        """Each day kept is one VIX closed above 35 on, a joined day before one the join keeps.

        VIX closes at 16:15 New York time, after FSTX's open on that date, so
        a position held from the open could not have read it.
        """
        days, vix, joined = fstx_rule.days, sources.vix, result.literal
        with np.errstate(invalid="ignore"):
            same = vix.reindex(days).to_numpy(dtype=float) > THRESHOLD
            filled = vix.reindex(days, method="ffill").to_numpy(dtype=float) > THRESHOLD
        assert list(days[same]) == list(joined.days[np.flatnonzero(joined.qualifies) - 1])
        assert reading(fstx_rule.literal, same) == result.same_day
        assert list(days[filled & ~same]) == [
            day("2008-11-27"),
            day("2009-01-19"),
            day("2009-02-16"),
        ]
        assert reading(fstx_rule.literal, filled) == result.same_day_filled

    def test_buy_on_gap_gives_the_same_figures_under_every_previous_day_alignment(
        self, sources
    ) -> None:
        stocks = sources.stocks
        long = buy_on_gap.buy_on_gap(stocks["Open"], stocks["Low"], stocks["Close"])
        joined = vix_filter("Buy on gap", long.days, long.daily, long.daily != 0, sources.vix)
        for other in (
            as_of_reading(long.days, long.daily, sources.vix),
            forward_filled_reading(long.days, long.daily, sources.vix),
            own_calendar_reading(long.days, long.daily, sources.vix),
        ):
            assert other.kept == joined.kept == 190
            assert other.average_annual_return == joined.average_annual_return
            assert other.sharpe == joined.sharpe

    def test_the_seven_days_after_vix_ends_could_not_qualify_either_way(
        self, sources, fstx_rule
    ) -> None:
        after = fstx_rule.days[fstx_rule.days > VIX_LAST]
        assert len(after) == 7
        before = latest_close_before(after, sources.vix)
        assert (before == 19.05).all()
        assert sources.vix.loc[VIX_LAST] == 19.05 < THRESHOLD


class TestBesideTheReplication:
    """Rows 14, 15 and 18, which no source prints."""

    def test_both_rules_keep_the_days_from_2008_09_18_to_2011_11_10(self, result) -> None:
        for filtered in (result.buy_on_gap, result.literal):
            kept = filtered.kept_days
            assert (kept[0], kept[-1]) == (day("2008-09-18"), day("2011-11-10"))

    def test_vix_first_closes_above_35_inside_either_window_on_2008_09_17(self, sources) -> None:
        above = sources.vix.loc[day("2004-07-15") :]
        above = above[above > THRESHOLD]
        assert above.index[0] == day("2008-09-17")
        assert above.iloc[0] == 36.22
        assert above.index[-1] == day("2011-11-09")

    def test_no_vix_close_sits_exactly_on_35(self, sources) -> None:
        """So the strict test decides no day here, and ``TestTheRules`` holds it."""
        assert not (sources.vix == THRESHOLD).any()
        assert sources.vix[sources.vix > THRESHOLD].min() == 35.02
        assert sources.vix[sources.vix <= THRESHOLD].max() == 34.95

    def test_buy_on_gap_held_a_position_on_20_of_its_190_kept_days(self, result) -> None:
        long = result.buy_on_gap
        assert long.held_days == 20
        assert long.kept - long.held_days == 170
        assert (long.filtered[~long.held[long.qualifies]] == 0).all()

    def test_fstx_held_a_position_on_43_of_its_185_kept_days(self, result, fstx_rule) -> None:
        literal = result.literal
        assert literal.held_days == result.momentum.held_days == 43
        rows = fstx_rule.days.get_indexer(literal.days)[literal.qualifies]
        assert (fstx_rule.positions[rows] == 1).sum() == 21
        assert (fstx_rule.positions[rows] == -1).sum() == 22

    def test_buy_on_gap_unfiltered_is_entry_18_s_because_the_calendar_is_unchanged(
        self, result
    ) -> None:
        f = result.buy_on_gap.unfiltered
        assert f.kept == 1500
        assert f.average_annual_return == pytest.approx(0.085279, abs=SIX)
        assert f.sharpe == pytest.approx(1.537063, abs=SIX)

    def test_the_join_moves_fstx_s_unfiltered_figures(self, result) -> None:
        """Location 3509's "around 13 percent and 1.4" is Example 7.1's full calendar."""
        joined = result.literal.unfiltered
        assert joined.kept == 1945
        assert joined.average_annual_return == pytest.approx(0.139950, abs=SIX)
        assert joined.sharpe == pytest.approx(1.589197, abs=SIX)
        assert not matches(100 * joined.average_annual_return, "13")
        assert not matches(joined.sharpe, "1.4")
        assert matches(100 * joined.average_annual_return, "14")
        assert matches(joined.sharpe, "1.6")
        full = result.fstx_full
        assert full.average_annual_return == pytest.approx(0.128622, abs=SIX)
        assert full.sharpe == pytest.approx(1.441620, abs=SIX)

    def test_neither_rule_s_kept_days_differ_from_its_other_days_beyond_noise(self, result) -> None:
        """Row 18. Welch's t on mean daily return, kept days against the other joined days.

        The test treats each day as independent of the others. Neither p is
        below 0.4, so neither sign's figures say which way the filter points.
        """
        long_t, long_p = result.buy_on_gap.welch
        assert long_t == pytest.approx(0.705402, abs=SIX)
        assert long_p == pytest.approx(0.481405, abs=SIX)
        fade_t, fade_p = result.literal.welch
        assert fade_t == pytest.approx(-0.684181, abs=SIX)
        assert fade_p == pytest.approx(0.494679, abs=SIX)
        momentum_t, momentum_p = result.momentum.welch
        assert momentum_t == pytest.approx(-fade_t, abs=1e-12)
        assert momentum_p == pytest.approx(fade_p, abs=1e-12)
        assert min(long_p, fade_p) > 0.4

    def test_welch_s_t_compares_the_kept_days_with_the_rest_unpooled(self) -> None:
        daily = np.array([0.0, 0.01, 0.03, -0.01, 0.05, 0.02])
        keep = np.array([False, True, True, False, True, False])
        filtered = Filtered(
            name="rule",
            days=pd.bdate_range("2020-01-06", periods=6),
            daily=daily,
            held=keep,
            qualifies=keep,
            calendar_days=6,
        )
        a, b = daily[keep], daily[~keep]
        se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
        t, p = filtered.welch
        assert t == pytest.approx((a.mean() - b.mean()) / se, abs=1e-12)
        assert 0 < p < 1


class TestTheGuard:
    """Row 16: VIX's flagged day, the spans guarded either side of it, and what the guard misses.

    The guard flags a day-over-day move of 1.6 times or more, so a rescale
    smaller than that passes it on any span. VIX's largest close before the
    flag sits where such a rescale could carry it past 35.
    """

    def test_vix_flags_2007_02_27_alone(self, sources) -> None:
        vix = sources.vix
        assert scale_breaks(vix) == [FLAGGED_DAY]
        assert vix.index[vix.index.get_loc(FLAGGED_DAY) - 1] == BEFORE_FLAG
        assert (vix.loc[BEFORE_FLAG], vix.loc[FLAGGED_DAY]) == (11.15, 18.31)
        # A wrong print could move a figure only if the true close were above 35.
        assert THRESHOLD / vix.loc[BEFORE_FLAG] > 3

    def test_vix_s_largest_close_before_the_flag_sits_inside_the_guard_s_blind_band(
        self, sources
    ) -> None:
        """23.81 on 2006-06-13, which a rescale of 1.47 times, too small to flag, lifts past 35."""
        before = sources.vix.loc[day("2004-07-16") : BEFORE_FLAG]
        assert before.max() == 23.81
        assert before.idxmax() == day("2006-06-13")
        assert math.exp(SCALE_BREAK_BOUND) == pytest.approx(1.6, abs=1e-15)
        assert 23.81 * 1.47 > THRESHOLD
        assert 1.47 < math.exp(SCALE_BREAK_BOUND)

    def test_vix_is_guarded_on_both_sides_of_its_flagged_day_in_each_window(
        self, monkeypatch
    ) -> None:
        seen = []

        def record(legs, *, start, end):
            seen.append(([entry.path for entry, _ in legs], start, end))

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", record)
        read_sources()
        assert seen == [
            (["vix/vix.csv"], day("2006-05-11"), BEFORE_FLAG),
            (["vix/vix.csv"], FLAGGED_DAY, STOCKS_LAST),
            (["vix/vix.csv"], day("2004-07-16"), BEFORE_FLAG),
            (["vix/vix.csv"], FLAGGED_DAY, VIX_LAST),
        ]

    @pytest.mark.parametrize("rule", ["buy_on_gap", "literal"])
    def test_the_two_spans_leave_out_only_the_flagged_move(self, sources, result, rule) -> None:
        """Every day-over-day pair of VIX closes the window reads is guarded, but one."""
        vix, days = sources.vix, getattr(result, rule).days

        def pairs(start, end):
            inside = vix.loc[start:end].index
            return set(zip(inside[:-1], inside[1:], strict=True))

        spans = guarded_spans(days, vix)
        guarded = set().union(*(pairs(start, end) for start, end in spans))
        assert pairs(days[0], days[-1]) - guarded == {(BEFORE_FLAG, FLAGGED_DAY)}
        for start, end in spans:
            assert scale_breaks(vix.loc[start:end]) == []

    @pytest.mark.parametrize("start", ["2004-07-16", "2006-05-11"])
    def test_a_guard_from_either_window_s_start_refuses_on_2007_02_27(self, sources, start) -> None:
        with pytest.raises(
            WindowCrossesScaleBreak, match="vix/vix.csv changes scale on 2007-02-27"
        ):
            refuse_window_crossing_a_break(
                [(sources.vix_member, sources.vix)], start=day(start), end=STOCKS_LAST
            )

    @pytest.mark.parametrize("when", ["2004-08-02", "2006-06-13", "2007-02-26"])
    def test_a_doubling_of_vix_before_its_flagged_day_is_refused(self, when, monkeypatch) -> None:
        """2004-08-02 lies inside FSTX's window alone, and 2007-02-26 ends the first span."""
        real = module.load_panel

        def broken(name, **kwargs):
            members, frame = real(name, **kwargs)
            if name == VIX_FILE:
                frame = frame.copy()
                frame.loc[day(when) :, "VIX"] *= 2
            return members, frame

        monkeypatch.setattr(module, "load_panel", broken)
        with pytest.raises(WindowCrossesScaleBreak, match=f"vix.csv changes scale on {when}"):
            read_sources()

    def test_a_rescale_under_1_6_times_passes_the_guard_and_moves_a_figure(
        self, sources, result
    ) -> None:
        """Closes to 2006-11-30 raised 1.48 times pass both spans, and buy on gap keeps 191 days."""
        vix = sources.vix.copy()
        vix.loc[: day("2006-11-30")] *= 1.48
        for days in (sources.stocks["Close"].index, sources.fstx.index):
            for start, end in guarded_spans(days, vix):
                refuse_window_crossing_a_break([(sources.vix_member, vix)], start=start, end=end)
        long = result.buy_on_gap
        moved = vix_filter("Buy on gap", long.days, long.daily, long.held, vix)
        assert moved.kept == 191

    @pytest.mark.parametrize("when", ["2008-01-02", "2010-06-01", "2012-04-24"])
    def test_a_scale_change_in_vix_after_its_flagged_day_is_refused(
        self, when, monkeypatch
    ) -> None:
        real = module.load_panel

        def broken(name, **kwargs):
            members, frame = real(name, **kwargs)
            if name == VIX_FILE:
                frame = frame.copy()
                frame.loc[day(when) :, "VIX"] *= 10
            return members, frame

        monkeypatch.setattr(module, "load_panel", broken)
        with pytest.raises(WindowCrossesScaleBreak, match="vix.csv changes scale"):
            read_sources()

    def test_a_scale_change_after_the_stocks_end_is_refused_by_fstx_s_span(
        self, monkeypatch
    ) -> None:
        """2012-05-08 lies past buy on gap's window and inside FSTX's."""
        real = module.load_panel

        def broken(name, **kwargs):
            members, frame = real(name, **kwargs)
            if name == VIX_FILE:
                frame = frame.copy()
                frame.loc[VIX_LAST:, "VIX"] *= 10
            return members, frame

        monkeypatch.setattr(module, "load_panel", broken)
        with pytest.raises(WindowCrossesScaleBreak, match="vix.csv changes scale on 2012-05-08"):
            read_sources()

    def test_fstx_is_guarded_by_the_opening_gap_s_own_read(self, monkeypatch) -> None:
        def refuse(data_dir=None, *, source_file=opening_gap.SOURCE_FILE):
            raise WindowCrossesScaleBreak("inputdataohlcdaily_20120517/fstx.csv changes scale")

        monkeypatch.setattr(module.opening_gap, "read_sources", refuse)
        with pytest.raises(WindowCrossesScaleBreak, match="fstx.csv"):
            read_sources()

    def test_the_stocks_are_read_unguarded_as_buy_on_gap_decides(self, sources) -> None:
        """``test_buy_on_gap.py``'s ``TestTheScaleBreakDecision`` holds the 30 flagged days."""
        _, frames = buy_on_gap.read_sources()
        assert frames["Close"].equals(sources.stocks["Close"])

    def test_read_sources_hands_its_directory_to_every_read(self, monkeypatch) -> None:
        seen = []
        real_panel = module.load_panel
        real_stocks = module.buy_on_gap.read_sources
        real_fstx = module.opening_gap.read_sources

        def panel(name, **kwargs):
            seen.append(("panel", kwargs.get("data_dir")))
            return real_panel(name, **kwargs)

        def stocks(data_dir=None):
            seen.append(("stocks", data_dir))
            return real_stocks(data_dir)

        def fstx(data_dir=None, **kwargs):
            seen.append(("fstx", data_dir))
            return real_fstx(data_dir, **kwargs)

        monkeypatch.setattr(module, "load_panel", panel)
        monkeypatch.setattr(module.buy_on_gap, "read_sources", stocks)
        monkeypatch.setattr(module.opening_gap, "read_sources", fstx)
        read_sources(paths.DATA_DIR)
        assert seen == [
            ("panel", paths.DATA_DIR),
            ("stocks", paths.DATA_DIR),
            ("fstx", paths.DATA_DIR),
        ]


class TestTheRules:
    """Each step on series built so the answer is known."""

    def test_a_close_exactly_on_35_keeps_nothing(self) -> None:
        assert qualifies([35.0, 35.0]).tolist() == [False, False]
        assert qualifies([np.nextafter(35.0, 36), 0.0]).tolist() == [False, True]

    def test_the_test_is_strictly_above_35_not_above_34(self) -> None:
        assert qualifies([34.5, 0.0, 35.5, 0.0]).tolist() == [False, False, False, True]

    def test_the_close_read_is_the_previous_row_s(self) -> None:
        """A close above 35 keeps the next row, not its own."""
        assert qualifies([40.0, 10.0, 10.0]).tolist() == [False, True, False]

    def test_a_nan_keeps_nothing_and_the_first_row_never_qualifies(self) -> None:
        assert qualifies([np.nan, 40.0, np.nan]).tolist() == [False, False, True]
        assert qualifies([40.0]).tolist() == [False]

    def test_the_join_keeps_the_days_both_trade_in_order(self) -> None:
        days = pd.DatetimeIndex(["2020-01-02", "2020-01-03", "2020-01-06", "2020-01-07"])
        vix = pd.Series(1.0, index=pd.DatetimeIndex(["2020-01-01", "2020-01-03", "2020-01-07"]))
        assert list(common_days(days, vix)) == [day("2020-01-03"), day("2020-01-07")]

    @staticmethod
    def _week():
        """Six rule days, VIX missing on the third and above 35 on the second and fifth."""
        days = pd.bdate_range("2020-01-06", periods=6)
        vix = pd.Series([20.0, 40.0, 20.0, 40.0, 20.0], index=days.delete(2))
        daily = np.array([0.01, 0.02, 0.03, 0.04, 0.05, 0.06])
        return days, vix, daily

    def test_the_filter_reads_the_previous_joined_day_across_a_missing_close(self) -> None:
        """The day after a missing VIX close reads the close before the gap."""
        days, vix, daily = self._week()
        filtered = vix_filter("rule", days, daily, daily > 0.03, vix)
        assert list(filtered.days) == list(days.delete(2))
        assert filtered.qualifies.tolist() == [False, False, True, False, True]
        assert filtered.filtered.tolist() == [0.04, 0.06]
        assert filtered.held_days == 2
        assert filtered.calendar_days == 6

    def test_the_own_calendar_reading_reads_the_missing_close_as_nan(self) -> None:
        days, vix, daily = self._week()
        own = own_calendar_reading(days, daily, vix)
        # Row 2 reads row 1's 40 and keeps 0.03, row 3 reads row 2's NaN, and row 5
        # reads row 4's 40 and keeps 0.06.
        assert own.kept == 2
        assert own.average_annual_return == pytest.approx(252 * 0.045)

    def test_the_as_of_reading_reads_the_latest_close_before_each_day(self) -> None:
        days, vix, daily = self._week()
        found = latest_close_before(days, vix)
        assert np.isnan(found[0])
        assert found[1:].tolist() == [20.0, 40.0, 40.0, 20.0, 40.0]
        as_of = as_of_reading(days, daily, vix)
        assert as_of.kept == 3
        assert as_of.average_annual_return == pytest.approx(252 * (0.03 + 0.04 + 0.06) / 3)

    def test_the_forward_fill_reads_the_rule_s_previous_day_not_a_later_vix_close(self) -> None:
        """A close on a day only VIX traded is what the latest close reads, and not the fill."""
        days = pd.DatetimeIndex(["2020-01-06", "2020-01-07", "2020-01-09", "2020-01-10"])
        vix = pd.Series(
            [40.0, 20.0, 40.0, 40.0],
            index=pd.DatetimeIndex(["2020-01-06", "2020-01-07", "2020-01-08", "2020-01-09"]),
        )
        daily = np.array([0.01, 0.02, 0.03, 0.04])
        # Thursday reads Wednesday's 40 as the latest close and Tuesday's 20 through the fill.
        filled = forward_filled_reading(days, daily, vix)
        assert filled.kept == 2
        assert filled.average_annual_return == pytest.approx(252 * (0.02 + 0.04) / 2)
        latest = as_of_reading(days, daily, vix)
        assert latest.kept == 3
        assert latest.average_annual_return == pytest.approx(252 * (0.02 + 0.03 + 0.04) / 3)

    def test_the_same_day_readings_keep_the_day_whose_own_close_is_above_35(self) -> None:
        """A close above 35 keeps its own row, where every other reading keeps the next."""
        days, vix, daily = self._week()
        same = same_day_reading(days, daily, vix, forward_fill=False)
        assert same.kept == 2
        assert same.average_annual_return == pytest.approx(252 * (0.02 + 0.05) / 2)
        # The fill gives the missing third row the second row's 40, so it keeps 0.03 too.
        filled = same_day_reading(days, daily, vix, forward_fill=True)
        assert filled.kept == 3
        assert filled.average_annual_return == pytest.approx(252 * (0.02 + 0.03 + 0.05) / 3)

    def test_a_day_before_vix_s_first_close_reads_nan(self) -> None:
        vix = pd.Series([40.0], index=pd.DatetimeIndex(["2020-01-07"]))
        days = pd.DatetimeIndex(["2020-01-06", "2020-01-07", "2020-01-08"])
        found = latest_close_before(days, vix)
        assert np.isnan(found[:2]).all()
        assert found[2] == 40.0

    def test_the_figures_on_a_known_series(self) -> None:
        daily = np.array([0.0, 0.02, -0.01, 0.03])
        keep = np.array([False, True, True, True])
        filtered = Filtered(
            name="rule",
            days=pd.bdate_range("2020-01-06", periods=4),
            daily=daily,
            held=np.array([False, True, True, False]),
            qualifies=keep,
            calendar_days=4,
        )
        kept = daily[keep]
        assert filtered.kept == 3
        assert filtered.average_annual_return == pytest.approx(252 * kept.mean())
        assert filtered.sharpe == pytest.approx(math.sqrt(252) * kept.mean() / kept.std(ddof=1))
        assert filtered.apr == pytest.approx((1.02 * 0.99 * 1.03) ** (252 / 3) - 1)
        assert filtered.held_days == 2
        assert filtered.zeroed.average_annual_return == pytest.approx(252 * daily.mean())
        assert filtered.zeroed.kept == 4
        assert filtered.unfiltered.average_annual_return == pytest.approx(252 * daily.mean())
        assert reading(daily, keep).sharpe == filtered.sharpe


class TestTheReport:
    @staticmethod
    def _row(out: str, label: str) -> list[str]:
        return next(r for r in out.splitlines() if r.strip().startswith(label)).split()

    def test_it_prints_both_rules_beside_the_book(self, printed) -> None:
        assert self._row(printed, "Buy on gap   ")[-7:] == [
            "190",
            "0.171924",
            "17.2",
            "reproduced",
            "1.417425",
            "1.4",
            "reproduced",
        ]
        assert self._row(printed, "FSTX, literal   ")[-7:] == [
            "185",
            "0.025730",
            "2.6",
            "reproduced",
            "0.164869",
            "0.16",
            "reproduced",
        ]
        assert self._row(printed, "FSTX, momentum")[-9:] == [
            "185",
            "-0.025730",
            "2.6",
            "gap",
            "-5.2",
            "-0.164869",
            "0.16",
            "gap",
            "-0.32",
        ]

    def test_it_prints_the_readings_that_miss(self, printed) -> None:
        assert self._row(printed, "Buy on gap, compounded APR")[-5:] == [
            "190",
            "0.179297",
            "17.2",
            "gap",
            "+0.7",
        ]
        assert self._row(printed, "FSTX, literal, latest VIX close before")[-8:] == [
            "188",
            "0.025319",
            "2.6",
            "gap",
            "-0.1",
            "0.163555",
            "0.16",
            "reproduced",
        ]
        assert self._row(printed, "FSTX, literal, one row back")[-9:] == [
            "185",
            "0.045238",
            "2.6",
            "gap",
            "+1.9",
            "0.291589",
            "0.16",
            "gap",
            "+0.13",
        ]
        assert self._row(printed, "FSTX, literal, forward-filled, one row back")[-8:] == [
            "188",
            "0.025319",
            "2.6",
            "gap",
            "-0.1",
            "0.163555",
            "0.16",
            "reproduced",
        ]
        assert self._row(printed, "FSTX, literal, same-day VIX, NaN on holidays")[-9:] == [
            "185",
            "-0.047063",
            "2.6",
            "gap",
            "-7.3",
            "-0.297416",
            "0.16",
            "gap",
            "-0.46",
        ]
        assert self._row(printed, "FSTX, literal, same-day VIX, forward-filled")[-9:] == [
            "188",
            "-0.046312",
            "2.6",
            "gap",
            "-7.2",
            "-0.295046",
            "0.16",
            "gap",
            "-0.46",
        ]
        assert "The same-day rows look ahead." in printed
        assert self._row(printed, "FSTX, literal, other days zeroed")[-9:] == [
            "1945",
            "0.002447",
            "2.6",
            "gap",
            "-2.4",
            "0.050969",
            "0.16",
            "gap",
            "-0.11",
        ]
        assert self._row(printed, "Buy on gap, other days zeroed")[-9:] == [
            "1500",
            "0.021777",
            "17.2",
            "gap",
            "-15",
            "0.503869",
            "1.4",
            "gap",
            "-0.9",
        ]

    def test_it_prints_the_vintages_the_join_and_the_counts(self, printed) -> None:
        assert printed.startswith(
            "The VIX filter on buy on gap and the STOXX Europe 50 gap rule, "
            "Algorithmic Trading location 3509"
        )
        assert "vix/vix.csv   chan-csv raw, saved 2012-05-09" in printed
        assert "inputdataohlcdaily_stocks_20120424/" in printed
        assert "inputdataohlcdaily_20120517/fstx.csv" in printed
        assert (
            "join      Buy on gap keeps 1500 of its 1500 days, 2006-05-11 to 2012-04-24" in printed
        )
        assert "join      FSTX keeps 1945 of its 2000 days, 2004-07-16 to 2012-05-08" in printed
        assert "a day is kept when VIX closed above 35 on the previous joined day" in printed
        assert "guard     VIX over each window but its flagged move, 2007-02-26 to 2007-02-27" in (
            printed
        )
        assert (
            "kept days      2008-09-18 to 2011-11-10 for buy on gap, "
            "2008-09-18 to 2011-11-10 for FSTX" in printed
        )
        assert (
            "held           buy on gap on 20 of its 190 kept days, FSTX on 43 of its 185" in printed
        )
        for line in (
            "Buy on gap, all 1500 joined days: 252 x mean 0.085279, Sharpe ratio 1.537063",
            "FSTX, literal, all 1945 joined days: 252 x mean 0.139950, Sharpe ratio 1.589197",
            "all 2000 days of Example 7.1: 252 x mean 0.128622, Sharpe ratio 1.441620",
            "Buy on gap, kept days against the other joined days: t 0.705402, p 0.481405",
            "FSTX, literal, kept days against the other joined days: t -0.684181, p 0.494679",
        ):
            assert line in printed
        assert (
            "No script ships for location 3509. The FSTX alignment was chosen after six were "
            "tried, and the five set aside are above." in printed
        )
        assert "Exploratory." in printed

    def test_a_miss_is_reported_as_one(self) -> None:
        assert module._verdict(2.5730, BOOK_FSTX_PERCENT) == "reproduced"
        assert module._verdict(2.5319, BOOK_FSTX_PERCENT) == "gap -0.1"
        assert module._verdict(17.9297, BOOK_BUY_ON_GAP_PERCENT) == "gap +0.7"

    def test_run_returns_the_specification(self) -> None:
        with redirect_stdout(io.StringIO()):
            found = run()
        assert found.literal.average_annual_return == pytest.approx(0.025730, abs=SIX)

    def test_run_reads_the_directory_it_is_given(self, tmp_path) -> None:
        with pytest.raises(VintageUnavailable, match="VIX.csv"):
            run(tmp_path)

    def test_main_turns_a_guard_refusal_into_one_line(self, monkeypatch, no_arguments) -> None:
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("vix/vix.csv changes scale")

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(SystemExit, match="vix.csv changes scale") as stopped:
            main()
        assert str(stopped.value) == "vix/vix.csv changes scale"

    def test_main_turns_a_missing_vintage_into_one_line(
        self, monkeypatch, tmp_path, no_arguments
    ) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit, match="VIX.csv"):
            main()

    def test_main_lets_any_other_error_through(self, monkeypatch, no_arguments) -> None:
        def broken(*_a, **_k):
            raise ValueError("a programming error keeps its traceback")

        monkeypatch.setattr(module, "run", broken)
        with pytest.raises(ValueError, match="keeps its traceback"):
            main()

    def test_main_refuses_an_argument(self, monkeypatch) -> None:
        monkeypatch.setattr("sys.argv", ["chan.vix_filter", "--bogus"])
        with pytest.raises(SystemExit) as refused:
            main()
        assert refused.value.code == 2
