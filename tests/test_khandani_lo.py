"""The pins for Khandani and Lo's linear reversal, Chan's Example 3.7.

This file is the single authority for every number any prose surface quotes
about the reversal, with one exception. ``blog/survivorship-and-transaction-costs.md``
also quotes where its running-profit figure ends, which
``tests/test_survivorship_and_costs_figures.py`` holds, and README lists what
the post says that nothing pins. ``docs/replication-log.md`` Entry 8 carries
the verdicts and points here row by row.

Every pin on the committed file reads one vintage and one specification, so
both are stated once here rather than in every docstring.

- **Vintage.** ``spx_20071123/``, the 500 stocks lifted from Chan's
  ``SPX_20071123.mat``, read as one frame through ``chan.series.load_panel``.
  Its identity is the ``SPX_20071123.mat`` row of ``LIFTED_SOURCES`` in
  ``tests/support/committed_vintages.py``, which ``TestTheVintage`` holds the
  members to rather than retyping it. The stocks are the index as it stood on
  2007-11-23, so every figure is a figure about survivors.
- **Specification.** ``example3_7.m`` at the mirror commit the module names.
  Returns, weights and profit are computed on the whole panel and cut to
  2006-01-01 to 2006-12-31, 251 trading days. The cost is 5 basis points on
  each side of a change in weight. The Sharpe ratio is ``√252 · mean / std``
  with no risk-free rate.

Each figure below names which of three specifications it is.

1. **Chan's rule before costs**, 0.2510, his ``sharpe``.
2. **Chan's rule after costs, both quirks kept**, −3.1884, his
   ``sharpeminustcost``. The first day's rebalance is not charged, so that day
   is NaN, and ``smartstd`` counts the NaN as 0 while ``smartmean`` skips it.
3. **Both quirks removed**, −3.2337. The first day is charged from the weights
   before the window, so nothing is NaN and nothing is zero-filled. Chan
   prints no figure for it.

Rows 1 and 2 are each held twice: at four decimals, at ``abs=5e-5``, which is
what lets the log quote them at four, and at the book's two decimals, which is
the pin ``docs/design.md``'s ``### What an experiment pins`` asks for. Dropping
the NaN the pandas way gives −3.1822, which misses −3.19 by one unit at the
book's precision. ``TestTheQuirksMoveTheFigure`` holds that, because it is the
mistake a port is most likely to make.

``TestWhatAnAverageDayCosts`` holds why the third figure lands where it does,
on the third specification: an average day earns 0.5276 basis points of the
position, pays 7.2525 in cost and swings by 33.3770, so the cost is 13.7453
days of profit.

Khandani and Lo's 4.47 is cited here as unpinned. It was computed on their own
universe, which this repo does not hold, and nothing below asserts it.

Exploratory. Reproducing Chan's figures spends the 2006 sample on a rule
somebody else chose. First run on 2026-10-02.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from chan import paths
from chan.khandani_lo import (
    BOOK_AFTER_COSTS,
    BOOK_BEFORE_COSTS,
    BOOK_KHANDANI_LO,
    ONE_WAY_COST,
    SOURCE_FILE,
    TRADING_DAYS,
    WINDOW_END,
    WINDOW_START,
    DailyBook,
    Reversal,
    chan_sharpe,
    daily_book,
    daily_pnl,
    daily_returns,
    main,
    plain_sharpe,
    reversal,
    reversal_weights,
    run,
    trading_cost,
)
from chan.series import WindowCrossesScaleBreak, load_panel, refuse_window_crossing_a_break
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import LIFTED_SOURCES

# --- the committed file --------------------------------------------------------


@pytest.fixture(scope="module")
def panel():
    return load_panel(SOURCE_FILE)


@pytest.fixture(scope="module")
def result(panel) -> Reversal:
    _, frame = panel
    return reversal(frame)


@pytest.fixture(scope="module")
def day(result) -> DailyBook:
    return daily_book(result)


class TestTheVintage:
    """The members are the ``LIFTED_SOURCES`` row, and the window is Chan's."""

    def test_the_members_are_the_pinned_source(self, panel) -> None:
        members, frame = panel
        vendor, basis, saved, folder, count = LIFTED_SOURCES[SOURCE_FILE]
        assert {(m.vendor, m.price_basis, m.obtained) for m in members} == {(vendor, basis, saved)}
        assert {m.path.split("/")[0] for m in members} == {folder}
        assert len(members) == count == frame.shape[1]

    def test_the_window_is_chans(self, result: Reversal) -> None:
        assert (WINDOW_START, WINDOW_END) == ("2006-01-01", "2006-12-31")
        assert len(result.days) == 251
        assert str(result.days[0].date()) == "2006-01-03"
        assert str(result.days[-1].date()) == "2006-12-29"

    def test_how_many_stocks_are_priced_at_each_end(self, panel) -> None:
        """491 on the first day and 495 on the last, because the panel is survivors."""
        _, frame = panel
        assert frame.loc["2006-01-03"].notna().sum() == 491
        assert frame.loc["2006-12-29"].notna().sum() == 495

    def test_no_stock_leaves_during_the_window_and_four_join(self, panel) -> None:
        """No stock priced on the first day is missing on the last, which a
        file of survivors guarantees. The four that join began trading during
        2006."""
        _, frame = panel
        first, last = frame.loc["2006-01-03"].notna(), frame.loc["2006-12-29"].notna()
        assert list(frame.columns[first & ~last]) == []
        assert sorted(frame.columns[last & ~first]) == ["EQ", "NYX", "WU", "WYN"]


class TestTheFigures:
    """Rows 1, 2 and 3 of the specifications in the module docstring."""

    def test_before_costs(self, result: Reversal) -> None:
        """Chan's ``sharpe``. He prints 0.25, at Kindle locations 2137 and 2233."""
        assert result.before_costs == pytest.approx(0.2510, abs=5e-5)
        assert round(result.before_costs, 2) == BOOK_BEFORE_COSTS == 0.25

    def test_after_costs_with_both_quirks(self, result: Reversal) -> None:
        """Chan's ``sharpeminustcost``. He prints −3.19, at location 2233."""
        assert result.after_costs == pytest.approx(-3.1884, abs=5e-5)
        assert round(result.after_costs, 2) == BOOK_AFTER_COSTS == -3.19

    def test_after_costs_with_both_quirks_removed(self, result: Reversal) -> None:
        """No figure in the book. A little below Chan's figure in row 2."""
        assert result.after_costs_charged == pytest.approx(-3.2337, abs=5e-5)

    def test_the_constants_are_the_scripts(self) -> None:
        """``onewaytcost`` and the annualisation, as ``example3_7.m`` sets them."""
        assert ONE_WAY_COST == 0.0005
        assert TRADING_DAYS == 252

    def test_khandani_and_los_figure_is_cited_and_not_computed(self) -> None:
        """4.47, location 2099. On their universe, so this is a citation only."""
        assert BOOK_KHANDANI_LO == 4.47


class TestWhatAnAverageDayCosts:
    """Why 0.2510 becomes about −3.2, as an average day of the charged specification.

    Every figure is a daily mean or deviation over the window's mean gross
    position, a constant, so each reads in basis points of the position held
    and neither Sharpe ratio moves. Dividing each day by its own position
    would be a different rule, and gives 1.4666 for the turnover rather than
    1.4505. ``blog/survivorship-and-transaction-costs.md`` quotes these.
    """

    def test_the_day_earns_half_a_basis_point_and_pays_seven(self, day: DailyBook) -> None:
        assert day.profit * 1e4 == pytest.approx(0.5276, abs=5e-5)
        assert day.cost * 1e4 == pytest.approx(7.2525, abs=5e-5)

    def test_the_cost_is_about_fourteen_days_of_profit(self, day: DailyBook) -> None:
        assert day.cost_per_profit == pytest.approx(13.7453, abs=5e-5)

    def test_the_rule_trades_about_one_and_a_half_books_a_day(self, day: DailyBook) -> None:
        """Five basis points on each unit traded is the whole cost."""
        assert day.turnover == pytest.approx(1.4505, abs=5e-5)
        assert day.cost == pytest.approx(day.turnover * ONE_WAY_COST, abs=1e-15)

    def test_dividing_each_day_by_its_own_position_reads_differently(
        self, result: Reversal
    ) -> None:
        """The figure the issue's plan measured, on the rule this class avoids."""
        assert (result.traded / result.held).mean() == pytest.approx(1.4666, abs=5e-5)

    def test_the_daily_swing_dwarfs_both(self, day: DailyBook) -> None:
        assert day.swing * 1e4 == pytest.approx(33.3770, abs=5e-5)
        assert day.swing_after * 1e4 == pytest.approx(33.0134, abs=5e-5)

    def test_the_sharpe_ratios_are_these_averages(self, day: DailyBook, result: Reversal) -> None:
        """√252 times the average day over its swing gives rows 1 and 3 exactly."""
        root = math.sqrt(TRADING_DAYS)
        assert root * day.profit / day.swing == pytest.approx(result.before_costs, abs=1e-12)
        assert root * (day.profit - day.cost) / day.swing_after == pytest.approx(
            result.after_costs_charged, abs=1e-12
        )

    def test_the_charged_series_is_the_profit_less_five_basis_points_a_unit(
        self, result: Reversal
    ) -> None:
        assert np.isfinite(result.pnl_charged).all()
        assert result.pnl_charged == pytest.approx(
            result.pnl - result.traded * ONE_WAY_COST, abs=1e-18
        )
        assert result.held.min() > 0


class TestTheQuirksMoveTheFigure:
    """What each quirk does to row 2, so a port that drops one fails here."""

    def test_the_after_cost_series_has_one_nan_on_the_first_day(self, result: Reversal) -> None:
        missing = np.flatnonzero(~np.isfinite(result.pnl_after_costs))
        assert missing.tolist() == [0]
        assert np.isfinite(result.pnl).all()

    def test_dropping_the_nan_misses_chans_second_digit(self, result: Reversal) -> None:
        """Skipping the NaN in the deviation as well as the mean, the pandas way."""
        kept = result.pnl_after_costs[np.isfinite(result.pnl_after_costs)]
        dropped = math.sqrt(TRADING_DAYS) * kept.mean() / kept.std(ddof=1)
        assert dropped == pytest.approx(-3.1822, abs=5e-5)
        assert round(dropped, 2) != BOOK_AFTER_COSTS

    def test_numpys_nan_functions_land_on_chans_digit_by_another_route(
        self, result: Reversal
    ) -> None:
        """``np.nanmean`` and ``np.nanstd`` also skip the NaN in both, but the
        deviation divides by n rather than n − 1, which lands on −3.19 with
        neither quirk. So the second digit turns on the divisor as well."""
        after = result.pnl_after_costs
        numpy_port = math.sqrt(TRADING_DAYS) * np.nanmean(after) / np.nanstd(after)
        assert numpy_port == pytest.approx(-3.1886, abs=5e-5)
        assert round(numpy_port, 2) == BOOK_AFTER_COSTS


class TestTheScaleBreakDecision:
    """Why the module does not call the single-series guard, run rather than asserted.

    The comment above ``FLAGGED_IN_CHANS_MAT_FILES`` in
    ``tests/test_scale_breaks.py`` leaves the decision to this run, and
    ``chan.khandani_lo``'s docstring makes it. These hold the two answers the guard gives, and
    that neither is about this run, because the rule never weights the day it
    would care about.
    """

    START, END = pd.Timestamp("2006-01-03"), pd.Timestamp("2006-12-29")

    def test_handed_the_panels_columns_it_refuses(self, panel) -> None:
        """It names the ten stocks with a NaN close in 2006 as unreadable, and no break."""
        members, frame = panel
        legs = [(m, frame[m.symbol]) for m in members]
        with pytest.raises(WindowCrossesScaleBreak) as refused:
            refuse_window_crossing_a_break(legs, start=self.START, end=self.END)
        said = str(refused.value)
        assert said.startswith(
            "the window 2006-01-03 to 2006-12-29 cannot be computed across: "
            "spx_20071123/cov.csv has no readable"
        )
        assert said.count("has no readable day-over-day move") == 10
        assert "changes scale" not in said

    def test_ten_stocks_have_a_missing_close_in_the_window(self, panel) -> None:
        _, frame = panel
        window = frame.loc[self.START : self.END]
        assert window.isna().any().sum() == 10

    def test_handed_each_members_own_rows_it_passes(self, panel) -> None:
        members, frame = panel
        legs = [(m, frame[m.symbol].dropna()) for m in members]
        refuse_window_crossing_a_break(legs, start=self.START, end=self.END)

    def test_wyns_restart_never_enters_a_weight(self, panel) -> None:
        """WYN's 2006-07-31 is NaN on the grid, so 2006-08-01 has no return and weight 0."""
        _, frame = panel
        closes = frame.to_numpy(dtype=float)
        column = frame.columns.get_loc("WYN")
        day = frame.index.get_loc(pd.Timestamp("2006-08-01"))
        assert np.isnan(closes[day - 1, column])
        assert np.isnan(daily_returns(closes)[day, column])
        assert reversal_weights(closes)[day, column] == 0.0


class TestTheReport:
    def test_it_prints_the_panel_the_window_and_each_figure(self, capsys) -> None:
        main()
        out = capsys.readouterr().out
        assert "500 members lifted from SPX_20071123.mat" in out
        assert "2006-01-03 to 2006-12-29, 251 trading days" in out
        assert "0.2510   0.25" in out
        assert "-3.1884  -3.19" in out
        assert "-3.2337   none" in out
        assert "Khandani and Lo report 4.47 for 2006" in out
        assert "survivors" in out

    def test_a_missing_vintage_reaches_the_reader_as_one_line(self, monkeypatch, tmp_path) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert "SPX_20071123.mat cannot be" in str(stopped.value)

    def test_run_reads_the_directory_it_is_given(self, tmp_path) -> None:
        with pytest.raises(VintageUnavailable, match="SPX_20071123.mat cannot be"):
            run(tmp_path)

    def test_any_other_failure_keeps_its_traceback(self, monkeypatch) -> None:
        """Only a refusal is turned into one line. A bug still surfaces as itself."""

        def broken(*_args, **_kwargs):
            raise RuntimeError("a bug, not a refusal")

        monkeypatch.setattr("chan.khandani_lo.load_panel", broken)
        with pytest.raises(RuntimeError, match="a bug, not a refusal"):
            main()


# --- a panel small enough to work by hand ------------------------------------------
#
# Three stocks over four days. C is first priced on day 1, so it counts in that
# day's n without having a return.
#
#   day   A      B       C
#   0     10     20      NaN
#   1     11     19      5       returns  +0.10  -0.05  NaN   market +0.025
#   2     11     19.95   5.5     returns   0     +0.05  +0.10 market +0.05
#   3     12.1   19.95   5.5     returns  +0.10   0      0    market +0.0333

HAND = np.array(
    [
        [10.0, 20.0, np.nan],
        [11.0, 19.0, 5.0],
        [11.0, 19.95, 5.5],
        [12.1, 19.95, 5.5],
    ]
)
HAND_DAYS = pd.to_datetime(["2005-12-29", "2005-12-30", "2006-01-03", "2006-01-04"])


class TestTheRuleByHand:
    def test_the_weights(self) -> None:
        """Day 1 divides by 3, the count of closes, not 2, the count of returns."""
        weights = reversal_weights(HAND)
        assert weights[0].tolist() == [0.0, 0.0, 0.0]
        assert weights[1] == pytest.approx([-0.025, 0.025, 0.0], abs=1e-12)
        assert weights[2] == pytest.approx([0.05 / 3, 0.0, -0.05 / 3], abs=1e-12)

    def test_the_weights_sum_to_zero_every_day(self) -> None:
        assert reversal_weights(HAND).sum(axis=1) == pytest.approx(0.0, abs=1e-15)

    def test_a_stock_priced_today_and_not_yesterday_has_weight_zero(self) -> None:
        assert reversal_weights(HAND)[1, 2] == 0.0

    def test_buy_the_loser_and_short_the_winner(self) -> None:
        """The sign. A stock that beat the market is shorted."""
        weights = reversal_weights(HAND)
        assert weights[1, 0] < 0 < weights[1, 1]

    def test_the_profit_uses_yesterdays_weights(self) -> None:
        pnl = daily_pnl(reversal_weights(HAND), daily_returns(HAND))
        assert np.isnan(pnl[0])
        assert pnl[1:] == pytest.approx([0.0, 0.025 * 0.05, 0.1 * 0.05 / 3], abs=1e-15)

    def test_the_cost_is_five_basis_points_on_each_side_of_a_change(self) -> None:
        cost = trading_cost(reversal_weights(HAND))
        assert np.isnan(cost[0])
        assert cost[1] == pytest.approx(0.05 * 0.0005, abs=1e-15)
        assert cost[2] == pytest.approx((0.025 + 0.05 / 3 + 0.025 + 0.05 / 3) * 0.0005, abs=1e-15)

    def test_a_window_starts_after_its_profit_is_computed(self) -> None:
        """The window's first profit uses the day before's weights, and its cost is NaN."""
        frame = pd.DataFrame(HAND, index=HAND_DAYS, columns=["A", "B", "C"])
        got = reversal(frame, start="2006-01-01", end="2006-12-31")
        assert got.pnl.tolist() == pytest.approx([0.025 * 0.05, 0.1 * 0.05 / 3], abs=1e-15)
        assert np.isnan(got.pnl_after_costs[0])
        assert np.isfinite(got.pnl_after_costs[1:]).all()

    def test_both_bounds_are_inclusive(self) -> None:
        """Chan's window drops a day only when it falls before the start or after the end."""
        frame = pd.DataFrame(HAND, index=HAND_DAYS, columns=["A", "B", "C"])
        got = reversal(frame, start="2006-01-03", end="2006-01-04")
        assert [str(day.date()) for day in got.days] == ["2006-01-03", "2006-01-04"]


class TestTheSharpeRatios:
    """Chan's mix of the two helpers, and the plain ratio the third figure uses.

    ``tests/test_matlab_helpers.py`` holds the helpers themselves.
    """

    def test_chans_sharpe_mixes_the_two(self) -> None:
        daily = np.array([np.nan, 1.0, 3.0])
        want = math.sqrt(252) * 2.0 / np.std([0.0, 1.0, 3.0], ddof=1)
        assert chan_sharpe(daily) == pytest.approx(want, abs=1e-12)

    def test_the_plain_sharpe_refuses_a_nan(self) -> None:
        with pytest.raises(ValueError, match="every day finite"):
            plain_sharpe(np.array([np.nan, 1.0, 3.0]))
