"""The pins for Khandani and Lo's linear reversal, Chan's Examples 3.7 and 3.8.

This file is the single authority for every number any prose surface quotes
about the reversal. ``docs/replication-log.md`` Entry 8 carries Example 3.7's
verdicts and Entry 10 carries Example 3.8's, and each points here row by row.
Example 3.8's pins are under ``the open-price variation`` below, and that
section states its own rules.

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

Khandani and Lo's 4.47 is cited here as unpinned. It was computed on their own
universe, which this repo does not hold, and nothing below asserts it.

Exploratory. Reproducing Chan's figures spends the 2006 sample on a rule
somebody else chose. Example 3.7 first ran on 2026-10-02, and Example 3.8 on
2026-10-03.
"""

from __future__ import annotations

import dataclasses
import math

import numpy as np
import pandas as pd
import pytest

from chan import paths
from chan.khandani_lo import (
    BAR_POINTS,
    BAR_SHARPE,
    BOOK_AFTER_COSTS,
    BOOK_BEFORE_COSTS,
    BOOK_KHANDANI_LO,
    BOOK_OPEN_CLAIM,
    NOTEBOOK_37_AFTER,
    NOTEBOOK_37_BEFORE,
    NOTEBOOK_38_AFTER,
    NOTEBOOK_38_BEFORE,
    NOTEBOOK_DECIMALS,
    ONE_WAY_COST,
    ONE_YEAR_BAR,
    SOURCE_FILE,
    SPLICED_SYMBOL,
    TRADING_DAYS,
    VERY_POSITIVE,
    WINDOW_END,
    WINDOW_START,
    NotebookReversal,
    OpenVariation,
    Reversal,
    chan_sharpe,
    claim_holds,
    daily_pnl,
    daily_returns,
    main,
    matches_notebook,
    notebook_reversal,
    open_variation,
    plain_sharpe,
    report_at_open,
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
def open_panel():
    return load_panel(SOURCE_FILE, field="Open")


@pytest.fixture(scope="module")
def variation(open_panel) -> OpenVariation:
    _, frame = open_panel
    return open_variation(frame)


@pytest.fixture
def no_arguments(monkeypatch):
    """``main`` parses ``sys.argv``, which under pytest holds pytest's own arguments."""
    monkeypatch.setattr("sys.argv", ["chan.khandani_lo"])


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


class TestTheScaleBreakDecision:
    """Why the module does not call the single-series guard, run rather than asserted.

    The comment above ``FLAGGED_IN_CHANS_MAT_FILES`` in
    ``tests/test_scale_breaks.py`` leaves the decision to this run, and
    ``chan.khandani_lo``'s docstring makes it. These hold the two answers the guard gives, and
    that neither is about this run, because the rule never weights the day it
    would care about. Each runs on the closes and on the opens, because Example
    3.8's rule B inherits the decision and the two fields share one NaN mask.
    Rule A reads WYN's gap as a return on purpose, which
    ``TestRuleAOnTheCloses`` pins.
    """

    START, END = pd.Timestamp("2006-01-03"), pd.Timestamp("2006-12-29")

    @pytest.fixture(params=["Close", "Open"])
    def either_panel(self, request):
        return request.getfixturevalue("panel" if request.param == "Close" else "open_panel")

    def test_handed_the_panels_columns_it_refuses(self, either_panel) -> None:
        """It names the ten stocks with a NaN price in 2006 as unreadable, and no break."""
        members, frame = either_panel
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

    def test_ten_stocks_have_a_missing_price_in_the_window(self, either_panel) -> None:
        _, frame = either_panel
        window = frame.loc[self.START : self.END]
        assert window.isna().any().sum() == 10

    def test_handed_each_members_own_rows_it_passes(self, either_panel) -> None:
        members, frame = either_panel
        legs = [(m, frame[m.symbol].dropna()) for m in members]
        refuse_window_crossing_a_break(legs, start=self.START, end=self.END)

    def test_wyns_restart_never_enters_a_weight(self, either_panel) -> None:
        """WYN's 2006-07-31 is NaN on the grid, so 2006-08-01 has no return and weight 0."""
        _, frame = either_panel
        prices = frame.to_numpy(dtype=float)
        column = frame.columns.get_loc("WYN")
        day = frame.index.get_loc(pd.Timestamp("2006-08-01"))
        assert np.isnan(prices[day - 1, column])
        assert np.isnan(daily_returns(prices)[day, column])
        assert reversal_weights(prices)[day, column] == 0.0


class TestTheReport:
    def test_it_prints_the_panel_the_window_and_each_figure(self, capsys, no_arguments) -> None:
        main()
        out = capsys.readouterr().out
        assert "500 members lifted from SPX_20071123.mat" in out
        assert "2006-01-03 to 2006-12-29, 251 trading days" in out
        assert "0.2510   0.25" in out
        assert "-3.1884  -3.19" in out
        assert "-3.2337   none" in out
        assert "Khandani and Lo report 4.47 for 2006" in out
        assert "survivors" in out

    def test_a_missing_vintage_reaches_the_reader_as_one_line(
        self, monkeypatch, tmp_path, no_arguments
    ) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert "SPX_20071123.mat cannot be" in str(stopped.value)

    def test_run_reads_the_directory_it_is_given(self, tmp_path) -> None:
        with pytest.raises(VintageUnavailable, match="SPX_20071123.mat cannot be"):
            run(tmp_path)

    def test_any_other_failure_keeps_its_traceback(self, monkeypatch, no_arguments) -> None:
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


# --- the open-price variation, Example 3.8 ---------------------------------------
#
# Example 3.8 is a revised-edition label, p. 78. Every pin below reads the same
# vintage as Example 3.7's, through ``load_panel(SOURCE_FILE, field="Open")``
# where it says the opens, over the same window, cost and annualisation. Each
# names which of two rules it is.
#
# - **Rule B** is ``example3_7.m`` with the open in place of the close, which is
#   ``reversal`` handed the open frame. It carries the book's claim, "both very
#   positive", read as both figures at least 1.0 and unrounded. The owner
#   confirmed that threshold on issue 206 before any figure on the opens was
#   computed.
# - **Rule A** is Chan's ``example3_8.ipynb`` as written, ``notebook_reversal``.
#   It printed the published figures. Its control is the notebook's Example 3.7
#   twin, run on the closes.
#
# Chan's notebooks read ``SPX_20071123.txt`` and ``SPX_op_20071123.txt``, which
# are not committed. Measured on issue 206 at ``7150afb``, they match the two
# panels cell for cell, NaN for NaN, to a largest relative difference of
# 2.0e-16, and nothing here can re-measure that.


class TestTheOpens:
    """The open panel has the close panel's shape exactly."""

    def test_the_same_days_stocks_and_missing_cells(self, panel, open_panel) -> None:
        _, closes = panel
        members, opens = open_panel
        assert len(members) == 500
        assert opens.index.equals(closes.index)
        assert list(opens.columns) == list(closes.columns)
        assert (opens.isna() == closes.isna()).all().all()

    def test_how_many_stocks_are_priced_at_each_end(self, open_panel) -> None:
        _, opens = open_panel
        assert opens.loc["2006-01-03"].notna().sum() == 491
        assert opens.loc["2006-12-29"].notna().sum() == 495

    def test_no_open_is_zero_or_negative(self, open_panel) -> None:
        _, opens = open_panel
        assert np.nanmin(opens.to_numpy(dtype=float)) > 0


class TestRuleAOnTheCloses:
    """Rule A's control: the notebook's Example 3.7 twin, which printed 0.9578 and −2.1617."""

    @pytest.fixture
    def closes(self, panel) -> pd.DataFrame:
        return panel[1]

    def test_it_reproduces_the_notebooks_example_37(self, closes) -> None:
        got = notebook_reversal(closes)
        assert got.before_costs == pytest.approx(0.9578, abs=5e-5)
        assert got.after_costs == pytest.approx(-2.1617, abs=5e-5)
        assert matches_notebook(got, NOTEBOOK_37_BEFORE, NOTEBOOK_37_AFTER)

    def test_without_the_forward_fill_it_does_not(self, closes) -> None:
        """The fill pandas 0.24 applied by default and pandas 3 does not."""
        got = notebook_reversal(closes, fill=False)
        assert got.before_costs == pytest.approx(0.4179, abs=5e-5)
        assert got.after_costs == pytest.approx(-3.3760, abs=5e-5)
        assert not matches_notebook(got, NOTEBOOK_37_BEFORE, NOTEBOOK_37_AFTER)

    def test_without_wyn_it_lands_near_the_unfilled_figure(self, closes) -> None:
        got = notebook_reversal(closes.drop(columns=[SPLICED_SYMBOL]))
        assert got.before_costs == pytest.approx(0.4268, abs=5e-5)
        assert got.after_costs == pytest.approx(-3.3643, abs=5e-5)

    def test_the_fill_reads_wyns_gap_as_one_days_move(self, closes) -> None:
        """0.26 before the gap and 31.85 after it, a return of 121.5 on 2006-08-01."""
        filled = closes.ffill().pct_change(fill_method=None)
        assert filled.loc["2006-08-01", SPLICED_SYMBOL] == pytest.approx(121.5, abs=5e-5)
        unfilled = closes.pct_change(fill_method=None)
        assert np.isnan(unfilled.loc["2006-08-01", SPLICED_SYMBOL])


class TestRuleAOnTheOpens:
    """The published figures, 2.3818 before costs and 1.3997 after."""

    def test_the_figures(self, variation: OpenVariation) -> None:
        assert variation.notebook.before_costs == pytest.approx(2.3818, abs=5e-5)
        assert variation.notebook.after_costs == pytest.approx(1.3997, abs=5e-5)

    def test_without_the_forward_fill(self, variation: OpenVariation) -> None:
        assert variation.unfilled.before_costs == pytest.approx(4.8606, abs=5e-5)
        assert variation.unfilled.after_costs == pytest.approx(1.0335, abs=5e-5)

    def test_without_wyn(self, variation: OpenVariation) -> None:
        """On the opens the splice lowers both figures, where on the closes it raises them."""
        assert variation.without_splice.before_costs == pytest.approx(4.8508, abs=5e-5)
        assert variation.without_splice.after_costs == pytest.approx(1.0357, abs=5e-5)

    def test_no_day_is_nan(self, variation: OpenVariation) -> None:
        assert np.isfinite(variation.notebook.pnl_after_costs).all()
        assert len(variation.notebook.days) == 251


class TestRuleBOnTheOpens:
    """Example 3.7's rule with the open in place of the close."""

    def test_before_costs(self, variation: OpenVariation) -> None:
        assert variation.rule_b.before_costs == pytest.approx(4.4202, abs=5e-5)

    def test_after_costs_with_both_quirks(self, variation: OpenVariation) -> None:
        assert variation.rule_b.after_costs == pytest.approx(0.7834, abs=5e-5)

    def test_after_costs_with_both_quirks_removed(self, variation: OpenVariation) -> None:
        assert variation.rule_b.after_costs_charged == pytest.approx(0.8293, abs=5e-5)

    def test_the_first_quirk_carries_over(self, variation: OpenVariation) -> None:
        missing = np.flatnonzero(~np.isfinite(variation.rule_b.pnl_after_costs))
        assert missing.tolist() == [0]

    def test_what_trading_at_the_open_recovered(self, variation, result) -> None:
        """Rule B's after-cost figure less Example 3.7's −3.1884."""
        recovered = variation.rule_b.after_costs - result.after_costs
        assert recovered == pytest.approx(3.9718, abs=5e-5)


class TestTheVerdicts:
    def test_the_published_figures_reproduce(self, variation: OpenVariation) -> None:
        assert variation.figures_reproduced

    def test_the_claim_does_not_hold_because_after_costs_misses(
        self, variation: OpenVariation
    ) -> None:
        assert not variation.claim_holds
        assert variation.rule_b.before_costs >= VERY_POSITIVE
        assert variation.rule_b.after_costs < VERY_POSITIVE

    def test_which_figures_clear_the_one_year_bar(self, variation: OpenVariation) -> None:
        a, b = variation.notebook, variation.rule_b
        assert a.before_costs >= ONE_YEAR_BAR and b.before_costs >= ONE_YEAR_BAR
        assert a.after_costs < ONE_YEAR_BAR and b.after_costs < ONE_YEAR_BAR

    def test_the_bar_is_chans_estimate_scaled_to_the_window(self) -> None:
        assert (BAR_SHARPE, BAR_POINTS) == (1.0, 681)
        assert ONE_YEAR_BAR == pytest.approx(1.6472, abs=5e-5)

    def test_the_constants(self) -> None:
        """The notebook's printouts at full precision, and the declared threshold."""
        assert (NOTEBOOK_37_BEFORE, NOTEBOOK_37_AFTER) == (0.957785681010386, -2.1617433718962276)
        assert (NOTEBOOK_38_BEFORE, NOTEBOOK_38_AFTER) == (2.381759409645483, 1.3996944546182997)
        assert NOTEBOOK_DECIMALS == 4
        assert VERY_POSITIVE == 1.0
        assert BOOK_OPEN_CLAIM == "very positive"


def _with_rule_b(variation: OpenVariation, before: float, after: float) -> OpenVariation:
    return dataclasses.replace(
        variation,
        rule_b=dataclasses.replace(variation.rule_b, before_costs=before, after_costs=after),
    )


class TestTheClaimRule:
    """The threshold is inclusive and reads the unrounded figure."""

    @pytest.mark.parametrize(
        ("before", "after", "holds"),
        [(1.0, 1.0, True), (4.0, 0.996, False), (0.999, 3.0, False), (0.5, -1.0, False)],
    )
    def test_both_halves_must_reach_one(self, variation, before, after, holds) -> None:
        assert claim_holds(_with_rule_b(variation, before, after).rule_b) is holds

    def test_matching_rounds_both_figures_at_four_decimals(self) -> None:
        days = pd.DatetimeIndex([])
        near = NotebookReversal(days, np.array([]), np.array([]), 2.38176, 1.39965)
        assert matches_notebook(near, NOTEBOOK_38_BEFORE, NOTEBOOK_38_AFTER)
        off = NotebookReversal(days, np.array([]), np.array([]), 2.38176, 1.39975)
        assert not matches_notebook(off, NOTEBOOK_38_BEFORE, NOTEBOOK_38_AFTER)


class TestTheOpenReport:
    def test_main_with_open_prints_both_rules_and_both_verdicts(self, capsys, monkeypatch) -> None:
        monkeypatch.setattr("sys.argv", ["chan.khandani_lo", "--open"])
        main()
        out = capsys.readouterr().out
        assert "Chan's Example 3.8 (revised edition)" in out
        assert "500 members lifted from SPX_20071123.mat, the Open column" in out
        assert "2.3818    2.3818" in out
        assert "1.3997    1.3997" in out
        assert "4.8606      none" in out
        assert "Verdict: REPRODUCED." in out
        assert "4.4202  very positive" in out
        assert "0.7834  very positive" in out
        assert "0.8293           none" in out
        assert "DOES NOT HOLD. Before costs clears it and the other half does not" in out
        assert "One-year bar 1.6472" in out
        assert "Clearing it: rule A before costs, rule B before costs." in out
        assert "survivors" in out
        assert "Exploratory." in out

    def test_run_asks_for_the_opens(self, monkeypatch, open_panel) -> None:
        asked = []

        def recording(source, *, field="Close", data_dir=None):
            asked.append(field)
            return open_panel

        monkeypatch.setattr("chan.khandani_lo.load_panel", recording)
        monkeypatch.setattr("chan.khandani_lo.report_at_open", lambda *_: None)
        got = run(at_open=True)
        assert asked == ["Open"]
        assert isinstance(got, OpenVariation)

    @pytest.mark.parametrize(
        ("before", "after", "said"),
        [
            (1.2, 1.1, "HOLDS."),
            (0.4, 1.1, "DOES NOT HOLD. After costs clears it and the other half does not"),
            (0.4, 0.3, "DOES NOT HOLD. Neither half clears it"),
        ],
    )
    def test_each_claim_verdict_is_said(
        self, capsys, variation, open_panel, before, after, said
    ) -> None:
        report_at_open(open_panel[0], _with_rule_b(variation, before, after))
        assert said in capsys.readouterr().out

    def test_a_missing_vintage_reaches_the_reader_as_one_line(self, monkeypatch, tmp_path) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        monkeypatch.setattr("sys.argv", ["chan.khandani_lo", "--open"])
        with pytest.raises(SystemExit) as stopped:
            main()
        assert "SPX_20071123.mat cannot be" in str(stopped.value)


# --- rule A on a panel small enough to work by hand --------------------------------
#
# Three stocks over five days. B is missing on day 2, so under the forward-fill
# it earns 0 that day and its day-3 return spans the gap.
#
#   day   A      B      C
#   0     10     20     5
#   1     11     19     5
#   2     11     NaN    5.5
#   3     12.1   22.8   5.5


HAND_A = pd.DataFrame(
    {"A": [10.0, 11.0, 11.0, 12.1], "B": [20.0, 19.0, np.nan, 22.8], "C": [5.0, 5.0, 5.5, 5.5]},
    index=pd.to_datetime(["2005-12-29", "2005-12-30", "2006-01-03", "2006-01-04"]),
)


class TestRuleAByHand:
    def test_the_fill_gives_a_missing_day_a_return_of_zero(self) -> None:
        returns = HAND_A.ffill().pct_change(fill_method=None)
        assert returns.loc["2006-01-03", "B"] == 0.0
        assert returns.loc["2006-01-04", "B"] == pytest.approx(22.8 / 19.0 - 1, abs=1e-15)

    def test_weights_have_a_gross_of_one_and_the_profit_lags_them(self) -> None:
        got = notebook_reversal(HAND_A, start="2005-12-30", end="2006-01-04")
        frame = HAND_A.ffill().pct_change(fill_method=None)
        returns = frame.to_numpy()
        raw = -(returns - frame.mean(axis=1).to_numpy()[:, None])
        weights = raw / np.nansum(np.abs(raw), axis=1)[:, None]
        assert np.nansum(np.abs(weights[1:]), axis=1) == pytest.approx([1.0, 1.0, 1.0])
        want = [np.nansum(weights[i - 1] * returns[i]) for i in (2, 3)]
        assert got.pnl[1:] == pytest.approx(want, abs=1e-15)
        assert got.pnl[0] == 0.0

    def test_the_first_days_cost_is_zero_and_the_deviation_divides_by_n(self) -> None:
        got = notebook_reversal(HAND_A, start="2005-12-30", end="2006-01-04")
        assert got.pnl_after_costs[0] == got.pnl[0]
        want = math.sqrt(252) * got.pnl_after_costs.mean() / got.pnl_after_costs.std(ddof=0)
        assert got.after_costs == pytest.approx(want, abs=1e-12)
