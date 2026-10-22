"""The pins for EWA, EWC and IGE, *Algorithmic Trading*'s Examples 2.6 to 2.8.

This file is the single authority for every number a prose surface quotes
about these three examples and the rows beside them, with one exception. The
intercept of the regression the hedge ratio comes from, 6.4113, is pinned in
``tests/test_etf_cointegration_figures.py``, since the figure in
``blog/johansen-etf-lessons.md`` draws it as the residual's mean. That post's
Lesson 2 quotes it beside the whole-file slope, 0.9624, which is pinned here,
and ``blog/kalman-hedge-lessons.md`` quotes the same two, so a change to either
moves that post too. ``blog/usdcad-stationarity-lessons.md`` quotes the book's
23-day half-life, so a change to that pin moves it too. README lists what each
post says that nothing here asserts.
``docs/replication-log.md`` Entry 23 carries the verdicts and points here row
by row.

``TestWhatThePostQuotes`` reads ``blog/johansen-etf-lessons.md`` itself. It
rebuilds each figure the post quotes from the run, at the post's precision,
and fails when the post no longer says it. So a re-pin that leaves that post
behind fails here rather than going stale. The Kalman and USD.CAD posts get no
such check.

Every pin on the committed file reads one vintage and one specification, so
both are stated once here.

- **Vintage.** ``inputdata_etf/ewa.csv``, ``ewc.csv`` and ``ige.csv``, lifted
  from Chan's ``inputData_ETF.mat``, chan-mat, adjusted by subtracting each
  dividend in dollars, saved 2012-04-10, 1,500 trading days from 2006-04-26 to
  2012-04-09, read for the close through ``chan.series.load_panel``. Its
  identity is that file's row of ``LIFTED_SOURCES`` in
  ``tests/support/committed_vintages.py``.
- **Specification.** ``cointegrationTests.m`` at EpchanPreview ``e4bc46f``,
  as :mod:`chan.etf_cointegration` transcribes it. ``cadf(EWC, EWA, 0, 1)``,
  which is ``lesage_cadf`` with one lag. ``johansen(·, 0, 1)``, a constant and
  one lagged difference, on columns EWC, EWA and then IGE. The portfolio is
  the triplet's first eigenvector, its half-life comes from a regression with
  an intercept, and the strategy's lookback is that half-life rounded half
  away from zero. Returns are annualised over 252 days with no risk-free rate
  and no cost, and the deviation divides by n − 1.

Each published figure is held twice: at the computed value's own precision,
which is what lets the log quote it, and at the precision Chan printed,
through ``matches``.

Exploratory. Reproducing Chan's figures spends the 2006 to 2012 sample on a
portfolio he chose, fitted on the days it trades. All three examples first ran
on 2026-10-05.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from ithildincore.timeseries import ADF_CRIT_CONST, EG_CRIT_N2, ols

from chan import etf_cointegration as module
from chan import paths
from chan.etf_cointegration import (
    BOOK_APR_PERCENT,
    BOOK_CADF_T,
    BOOK_HALF_LIFE_DAYS,
    BOOK_SHARPE,
    PAIR,
    SCRIPT_APR,
    SCRIPT_CADF_AR1,
    SCRIPT_CADF_CRITICAL,
    SCRIPT_CADF_T,
    SCRIPT_EIGENVALUES,
    SCRIPT_EIGENVECTORS,
    SCRIPT_HALF_LIFE,
    SCRIPT_PAIR_EIGEN,
    SCRIPT_PAIR_EIGEN_CRITICAL,
    SCRIPT_PAIR_TRACE,
    SCRIPT_PAIR_TRACE_CRITICAL,
    SCRIPT_SHARPE,
    SCRIPT_TRIPLET_EIGEN,
    SCRIPT_TRIPLET_EIGEN_CRITICAL,
    SCRIPT_TRIPLET_TRACE,
    SCRIPT_TRIPLET_TRACE_CRITICAL,
    SOURCE_FILE,
    TRIPLET,
    EtfCointegration,
    etf_cointegration,
    linear_mean_reversion,
    main,
    portfolio_value,
    read_sources,
    run,
    strategy,
)
from chan.johansen import johansen
from chan.khandani_lo_book_two import matches
from chan.matlab_helpers import calculate_max_dd, drawdown_path, moving_avg, moving_std
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import LIFTED_SOURCES

#: The module docstring's vintage and specification in one line, which
#: ``tests/test_etf_cointegration_figures.py`` carries in its failure messages.
SPEC = (
    "inputdata_etf/ EWA, EWC and IGE closes over 1,500 days, cadf(EWC, EWA, 0, 1), "
    "johansen(., 0, 1) on EWC, EWA, IGE, the first eigenvector traded with a 23-row "
    "lookback, profit over gross dollars, compounded APR, n - 1 Sharpe ratio, no cost"
)


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def result(sources) -> EtfCointegration:
    return etf_cointegration(sources[1])


@pytest.fixture(scope="module")
def triplet(sources) -> np.ndarray:
    return sources[1][list(TRIPLET)].to_numpy(dtype=float)


@pytest.fixture
def no_arguments(monkeypatch):
    """``main`` parses ``sys.argv``, which under pytest holds pytest's own arguments."""
    monkeypatch.setattr("sys.argv", ["chan.etf_cointegration"])


def _printed(rows) -> np.ndarray:
    return np.array([[float(cell) for cell in row] for row in rows])


class TestTheVintage:
    def test_the_three_members_are_the_pinned_source(self, sources) -> None:
        members, closes = sources
        vendor, basis, saved, folder, _ = LIFTED_SOURCES[SOURCE_FILE]
        assert {(m.vendor, m.price_basis, m.obtained) for m in members} == {(vendor, basis, saved)}
        assert sorted(m.path for m in members) == [
            f"{folder}/ewa.csv",
            f"{folder}/ewc.csv",
            f"{folder}/ige.csv",
        ]
        assert list(closes.columns) == ["EWA", "EWC", "IGE"]

    def test_the_window_is_the_whole_file_with_no_price_missing(self, sources) -> None:
        closes = sources[1]
        assert len(closes) == 1500
        assert str(closes.index[0].date()) == "2006-04-26"
        assert str(closes.index[-1].date()) == "2012-04-09"
        assert np.isfinite(closes.to_numpy()).all()

    def test_the_script_orders_the_columns_ewc_ewa_ige(self) -> None:
        """``y2 = [y, x]``, so every eigenvector row follows this order, not the title's."""
        assert PAIR == ("EWC", "EWA")
        assert TRIPLET == ("EWC", "EWA", "IGE")


class TestExample26TheCadfTest:
    """Rows 1 to 3: ``cadf(EWC, EWA, 0, 1)`` and the claim location 1292 makes."""

    def test_row_1_the_t_statistic(self, result) -> None:
        assert result.cadf.t == pytest.approx(-3.6434663489, abs=1e-10)
        assert matches(result.cadf.t, SCRIPT_CADF_T)
        assert matches(result.cadf.t, BOOK_CADF_T)

    def test_row_2_the_ar1_estimate_and_the_observations(self, result) -> None:
        assert result.cadf.ar1 == pytest.approx(-0.0204108120, abs=1e-10)
        assert matches(result.cadf.ar1, SCRIPT_CADF_AR1)
        assert result.cadf.nobs == 1498

    def test_row_3_the_pair_cointegrates_at_95_percent(self, result) -> None:
        """Past jplv7's −3.359, which is quoted, and not past its −3.880 at 99."""
        one, five, ten = (float(v) for v in SCRIPT_CADF_CRITICAL)
        assert (one, five, ten) == (-3.880, -3.359, -3.038)
        assert one < result.cadf.t < five
        assert result.cadf.t < EG_CRIT_N2["5%"] == -3.34


class TestExample27TheJohansenTest:
    """Rows 4 to 11, with each critical value the script prints."""

    def test_row_4_the_pair_trace_statistics(self, result) -> None:
        np.testing.assert_allclose(result.pair.trace, [19.983219, 3.982761], atol=1e-6)
        assert all(map(matches, result.pair.trace, SCRIPT_PAIR_TRACE))

    def test_row_5_the_pair_eigen_statistics(self, result) -> None:
        np.testing.assert_allclose(result.pair.eigen, [16.000457, 3.982761], atol=1e-6)
        assert all(map(matches, result.pair.eigen, SCRIPT_PAIR_EIGEN))

    def test_row_7_the_triplet_trace_statistics(self, result) -> None:
        np.testing.assert_allclose(
            result.triplet.trace, [34.428620, 17.531719, 4.471021], atol=1e-6
        )
        assert all(map(matches, result.triplet.trace, SCRIPT_TRIPLET_TRACE))

    def test_row_8_the_triplet_eigen_statistics(self, result) -> None:
        np.testing.assert_allclose(
            result.triplet.eigen, [16.896901, 13.060698, 4.471021], atol=1e-6
        )
        assert all(map(matches, result.triplet.eigen, SCRIPT_TRIPLET_EIGEN))

    @pytest.mark.parametrize(
        ("which", "statistic", "printed"),
        [
            ("pair", "trace", SCRIPT_PAIR_TRACE_CRITICAL),
            ("pair", "eigen", SCRIPT_PAIR_EIGEN_CRITICAL),
            ("triplet", "trace", SCRIPT_TRIPLET_TRACE_CRITICAL),
            ("triplet", "eigen", SCRIPT_TRIPLET_EIGEN_CRITICAL),
        ],
    )
    def test_every_critical_value_is_the_one_printed(self, result, which, statistic, printed):
        computed = getattr(getattr(result, which), f"{statistic}_critical")
        assert computed.shape == (len(printed), 3)
        # LeSage's tables hold four decimals, such as 2.7055, and prt printed
        # three. Formatting reproduces the printout. round() on a numpy float
        # scales and rounds half to even, which gives 2.706 instead.
        for row, row_printed in zip(computed, printed, strict=True):
            assert [f"{value:.3f}" for value in row] == list(row_printed)

    def test_row_10_the_triplet_eigenvalues(self, result) -> None:
        np.testing.assert_allclose(
            result.triplet.eigenvalues, [0.01121626, 0.00868086, 0.00298021], atol=1e-8
        )
        assert all(map(matches, result.triplet.eigenvalues, SCRIPT_EIGENVALUES))

    def test_row_11_the_eigenvectors_are_chans_with_every_sign_flipped(self, result) -> None:
        """statsmodels makes the top-left element positive, and MATLAB gave −1.0460 there."""
        printed = _printed(SCRIPT_EIGENVECTORS)
        np.testing.assert_allclose(result.triplet.eigenvectors, -printed, atol=5e-5)
        assert not np.allclose(result.triplet.eigenvectors, printed, atol=5e-5)
        assert result.triplet.eigenvectors[0, 0] == pytest.approx(1.04602749, abs=1e-8)

    def test_row_12_the_half_life(self, result) -> None:
        assert result.strategy.half_life == pytest.approx(22.6625778505, abs=1e-9)
        assert matches(result.strategy.half_life, SCRIPT_HALF_LIFE)
        assert matches(result.strategy.half_life, BOOK_HALF_LIFE_DAYS)


class TestTheClaims:
    """Rows 3, 6 and 9 read each test's relations through its critical values."""

    def test_row_6_both_tests_find_two_relations_for_the_pair_at_95(self, result) -> None:
        assert result.pair.relations("trace", 95) == 2
        assert result.pair.relations("eigen", 95) == 2

    def test_row_6_the_trace_rejects_r_le_0_at_99_and_the_eigen_does_not(self, result) -> None:
        """Location 1324 says the trace's r = 0 falls at 99 and the eigen's at 95."""
        assert result.pair.trace[0] > result.pair.trace_critical[0, 2]
        assert result.pair.eigen[0] < result.pair.eigen_critical[0, 2]
        assert result.pair.relations("trace", 99) == 1

    def test_row_6_the_pairs_second_relation_clears_its_bar_by_0_141(self, result) -> None:
        margin = result.pair.trace[1] - result.pair.trace_critical[1, 1]
        assert margin == pytest.approx(0.141261, abs=1e-6)

    def test_row_9_the_trace_test_finds_three_relations_at_95(self, result) -> None:
        assert result.triplet.relations("trace", 95) == 3

    def test_row_9_the_eigen_test_finds_none_even_at_90(self, result) -> None:
        """16.897 is short of 18.893, so location 1337's "Both" does not survive."""
        assert result.triplet.eigen[0] < result.triplet.eigen_critical[0, 0]
        assert [result.triplet.relations("eigen", level) for level in (90, 95, 99)] == [0, 0, 0]

    def test_row_9_the_trace_test_finds_none_at_99(self, result) -> None:
        """34.429 clears 29.796 at 95 and falls short of 35.463 at 99.

        So at 99 percent the count stops at the first null, and neither test
        finds a relation among the three.
        """
        assert result.triplet.trace_critical[0, 1] < result.triplet.trace[0]
        assert result.triplet.trace[0] < result.triplet.trace_critical[0, 2]
        assert [result.triplet.relations("trace", level) for level in (90, 95, 99)] == [3, 3, 0]


class TestExample28TheStrategy:
    """Rows 13 and 14, and how the strategy gets there."""

    def test_row_13_the_apr(self, result) -> None:
        assert result.strategy.apr == pytest.approx(0.1257386810, abs=1e-10)
        assert matches(result.strategy.apr, SCRIPT_APR)
        assert matches(100 * result.strategy.apr, BOOK_APR_PERCENT)

    def test_row_14_the_sharpe_ratio(self, result) -> None:
        assert result.strategy.sharpe == pytest.approx(1.3913100883, abs=1e-10)
        assert matches(result.strategy.sharpe, SCRIPT_SHARPE)
        assert matches(result.strategy.sharpe, BOOK_SHARPE)

    def test_the_lookback_is_the_half_life_rounded(self, result) -> None:
        assert result.strategy.lookback == 23

    def test_the_weights_are_the_first_eigenvector(self, result) -> None:
        np.testing.assert_array_equal(result.strategy.weights, result.triplet.eigenvectors[:, 0])

    def test_the_first_return_is_on_row_23_and_every_later_day_has_one(self, result) -> None:
        """The moving deviation fills on row 22 and positions earn from the next row."""
        nonzero = np.flatnonzero(result.strategy.daily)
        assert nonzero[0] == 23
        assert str(result.days[23].date()) == "2006-05-30"
        assert len(nonzero) == 1477 == 1500 - 23
        assert len(result.strategy.daily) == 1500

    def test_negating_the_eigenvector_moves_nothing(self, triplet, result) -> None:
        """Chan's sign gives the same half-life, lookback and every day's return."""
        flipped = strategy(triplet, -result.strategy.weights)
        assert flipped.half_life == pytest.approx(result.strategy.half_life, abs=1e-9)
        assert flipped.lookback == result.strategy.lookback
        np.testing.assert_allclose(flipped.daily, result.strategy.daily, atol=1e-15)

    def test_zero_padding_the_lag_as_lesage_does_gives_the_same_series(self, triplet, result):
        """The first row divides by a zero price, so it is not a number and becomes 0."""
        weights = result.strategy.weights
        value = portfolio_value(triplet, weights)
        lookback = result.strategy.lookback
        with np.errstate(invalid="ignore", divide="ignore"):
            units = -(value - moving_avg(value, lookback)) / moving_std(value, lookback)
            positions = units[:, None] * weights[None, :] * triplet
            held = np.vstack([np.zeros((1, 3)), positions[:-1]])
            before = np.vstack([np.zeros((1, 3)), triplet[:-1]])
            pnl = np.sum(held * (triplet - before) / before, axis=1)
            daily = pnl / np.sum(np.abs(held), axis=1)
        assert np.isnan(daily[0])
        np.testing.assert_array_equal(np.where(np.isnan(daily), 0.0, daily), result.strategy.daily)


class TestTheRule:
    """The strategy's lines on series built by hand."""

    def test_a_portfolio_is_each_price_times_its_weight_summed(self) -> None:
        prices = np.array([[10.0, 20.0], [11.0, 19.0]])
        np.testing.assert_array_equal(portfolio_value(prices, np.array([1.0, -0.5])), [0.0, 1.5])

    def test_the_rows_before_the_window_fills_earn_nothing(self) -> None:
        prices = np.column_stack([np.linspace(10, 20, 12), np.linspace(20, 10, 12) + [0, 1] * 6])
        daily = linear_mean_reversion(prices, np.array([1.0, 1.0]), 4)
        assert (daily[:4] == 0).all()
        assert (daily[4:] != 0).any()

    def test_a_portfolio_above_its_average_is_sold(self) -> None:
        """The last price jumps, so the units go negative and the next rise loses."""
        one = np.r_[np.full(5, 10.0) + [0, 0.1, -0.1, 0.1, -0.1], 12.0, 13.0]
        prices = np.column_stack([one, np.full(7, 5.0)])
        daily = linear_mean_reversion(prices, np.array([1.0, 0.0]), 3)
        assert daily[6] < 0

    def test_a_portfolio_that_does_not_revert_is_refused_by_name(self) -> None:
        """``ou_half_life`` gives infinity here, which ``int`` would refuse with no reason."""
        trend = np.column_stack([np.exp(np.linspace(0, 1, 50)), np.ones(50)])
        with pytest.raises(ValueError, match="does not revert"):
            strategy(trend, np.array([1.0, 0.0]))

    def test_a_missing_price_makes_its_day_zero_as_matlabs_sum_does(self) -> None:
        """``np.nansum`` would skip the missing leg and earn on the other."""
        rng = np.random.default_rng(5)
        prices = 10 + np.cumsum(rng.normal(scale=0.1, size=(30, 2)), axis=0)
        prices[20, 1] = np.nan
        daily = linear_mean_reversion(prices, np.array([1.0, -1.0]), 5)
        assert daily[20] == 0
        assert daily[19] != 0

    def test_the_lookback_rounds_a_half_away_from_zero(self, monkeypatch, triplet, result):
        """``np.round`` would give 22, since it sends a half to the even neighbour."""
        monkeypatch.setattr(module, "ou_half_life", lambda _: 22.5)
        assert strategy(triplet, result.strategy.weights).lookback == 23

    def test_a_day_with_no_gross_is_zero_rather_than_nan(self) -> None:
        """A weight of 0 everywhere leaves the gross at 0 and 0 / 0 at NaN, set to 0."""
        prices = np.column_stack([np.linspace(1, 2, 8), np.linspace(2, 3, 8)])
        assert (linear_mean_reversion(prices, np.zeros(2), 3) == 0).all()


class TestBesideTheReplication:
    """No book prints these, so none carries a verdict."""

    def test_the_hedge_ratio_feeds_only_the_figure(self, result) -> None:
        assert result.hedge_ratio == pytest.approx(0.9624293987, abs=1e-10)

    def test_reversing_the_legs_moves_the_statistic_and_not_the_verdict(self, result) -> None:
        """Location 1282 says the result differs. It does, by 0.0029, past −3.359 both ways."""
        assert result.reversed_cadf.t == pytest.approx(-3.6405421403, abs=1e-10)
        assert result.reversed_cadf.t - result.cadf.t == pytest.approx(0.002924, abs=1e-6)
        assert result.reversed_cadf.t < float(SCRIPT_CADF_CRITICAL[1])

    def test_reordering_the_columns_leaves_every_statistic(self, result) -> None:
        """Location 1324 says the Johansen test does not depend on the order."""
        for statistic in ("trace", "eigen", "eigenvalues"):
            np.testing.assert_allclose(
                getattr(result.reordered_triplet, statistic),
                getattr(result.triplet, statistic),
                atol=1e-11,
            )

    def test_reordering_permutes_the_vectors_rows_up_to_sign(self, result) -> None:
        reordered = result.reordered_triplet.eigenvectors[[1, 0, 2]]
        signs = np.sign(reordered[0] / result.triplet.eigenvectors[0])
        np.testing.assert_allclose(reordered * signs, result.triplet.eigenvectors, atol=1e-10)
        assert list(signs) == [-1, -1, 1]

    def test_the_first_eigenvector_reverts_fastest(self, result) -> None:
        """Location 1340 expects the half-lives to rise as the eigenvalues fall."""
        np.testing.assert_allclose(
            result.eigenvector_half_lives, [22.662578, 43.731678, 151.546826], atol=1e-6
        )
        assert list(result.eigenvector_half_lives) == sorted(result.eigenvector_half_lives)

    def test_no_etf_alone_rejects_a_unit_root_even_at_90(self, result) -> None:
        """A plain ADF with a constant and one lag, against MacKinnon's −2.57.

        The pair's Johansen rank of 2 says each series is stationary around a
        constant. These three say none is, which is what makes row 6's reading
        fragile rather than wrong.
        """
        assert result.adf == pytest.approx(
            {"EWA": -1.863334, "EWC": -1.901877, "IGE": -2.078705}, abs=1e-6
        )
        assert all(t > -2.57 for t in result.adf.values())

    @pytest.mark.parametrize("which", ["pair", "triplet"])
    def test_each_trace_statistic_sums_the_eigen_statistics_from_its_row_down(
        self, result, which: str
    ) -> None:
        """The trace for r ≤ i adds the eigen statistics for r ≤ i and every row after it.

        For the triplet that is 34.428620 = 16.896901 + 13.060698 + 4.471021,
        then 17.531719 = 13.060698 + 4.471021, and 4.471021 alone.
        """
        tested = getattr(result, which)
        np.testing.assert_allclose(
            np.cumsum(tested.eigen[::-1])[::-1], tested.trace, rtol=0, atol=1e-9
        )
        assert tested.trace[-1] == tested.eigen[-1]

    def test_the_first_eigenvector_holds_one_fund_long_against_two_short(
        self, sources, result
    ) -> None:
        """Each ETF's dollars per unit on 2012-04-09, the weight times the last close.

        The weights are 1.04602749, −0.7599635 and −0.22330592 shares, rows
        EWC, EWA and IGE, at closes of 27.46, 22.93 and 38.00.
        """
        closes = sources[1][list(TRIPLET)]
        assert str(closes.index[-1].date()) == "2012-04-09"
        dollars = result.strategy.weights * closes.iloc[-1].to_numpy(dtype=float)
        np.testing.assert_allclose(
            dollars, [28.72391494, -17.42596314, -8.48562509], rtol=0, atol=1e-8
        )
        assert list(np.sign(dollars)) == [1, -1, -1]

    def test_the_deepest_drawdown_and_the_longest_spell_below_a_high(self, result) -> None:
        """``calculateMaxDD`` on ``cumprod(1 + ret) − 1``, with where each one falls.

        The deepest drawdown bottoms on 2010-08-16. The longest spell below a
        high runs 598 rows, from the day after the 2009-04-01 high to
        2011-08-15, so the trough sits inside it.
        """
        cumret = np.cumprod(1 + result.strategy.daily) - 1
        deepest, longest = calculate_max_dd(cumret)
        assert deepest == pytest.approx(-0.10124855881644923, abs=1e-10)
        assert longest == 598
        _, drawdown, duration = drawdown_path(cumret)
        trough = int(np.argmin(drawdown))
        assert drawdown[trough] == deepest
        assert str(result.days[trough].date()) == "2010-08-16"
        last = int(np.argmax(duration))
        first = last - longest + 1
        assert duration[last] == longest
        assert drawdown[first - 1] == 0 and drawdown[first] < 0
        assert [str(result.days[row].date()) for row in (first - 1, first, last)] == [
            "2009-04-01",
            "2009-04-02",
            "2011-08-15",
        ]
        assert first <= trough <= last

    def test_the_pair_is_tested_as_ewc_then_ewa(self, sources, result) -> None:
        """The statistics do not depend on the order, so the eigenvector rows are what show it."""
        closes = sources[1]
        script_order = johansen(closes[["EWC", "EWA"]].to_numpy(dtype=float))
        np.testing.assert_allclose(script_order.eigenvectors, result.pair.eigenvectors, atol=1e-10)
        swapped = johansen(closes[["EWA", "EWC"]].to_numpy(dtype=float))
        assert not np.allclose(np.abs(swapped.eigenvectors), np.abs(result.pair.eigenvectors))


class TestTheGuardAndTheReads:
    def test_read_sources_runs_the_guard_on_the_three_over_the_whole_file(
        self, monkeypatch
    ) -> None:
        seen = []

        def record(legs, *, start, end):
            seen.append(([entry.symbol for entry, _ in legs], start, end))

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", record)
        read_sources()
        assert seen == [
            (["EWA", "EWC", "IGE"], pd.Timestamp("2006-04-26"), pd.Timestamp("2012-04-09"))
        ]

    def test_a_refusal_from_the_guard_reaches_the_caller(self, monkeypatch) -> None:
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("flagged")

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(WindowCrossesScaleBreak, match="flagged"):
            run()

    def test_main_turns_a_guard_refusal_into_one_line(self, monkeypatch, no_arguments):
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("inputdata_etf/ewa.csv changes scale on 2008-01-02")

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(SystemExit, match="ewa.csv changes scale on 2008-01-02"):
            main()

    def test_run_reads_the_directory_it_is_given(self, tmp_path) -> None:
        with pytest.raises(VintageUnavailable, match="inputData_ETF.mat"):
            run(tmp_path)

    def test_main_turns_a_missing_vintage_into_one_line(
        self, monkeypatch, tmp_path, no_arguments
    ) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit, match="inputData_ETF.mat"):
            main()

    def test_a_miss_is_reported_as_one(self) -> None:
        assert module._verdict(0.0, "1.0") == "did not reproduce, gap -1"
        assert module._verdict(1.04, "1.0") == "reproduced"

    def test_the_report_marks_every_printed_figure_reproduced(self, capsys, no_arguments):
        main()
        out = capsys.readouterr().out
        figures = [line for line in out.splitlines() if line.startswith("  2.")]
        assert len(figures) == 18
        assert all(line.endswith("reproduced") for line in figures)
        assert "did not reproduce" not in out
        assert "triplet eigen  0 at 90%, 0 at 95%, 0 at 99%" in out
        assert "Exploratory." in out


#: The post whose quoted figures ``TestWhatThePostQuotes`` rebuilds from the run.
POST = paths.REPO_ROOT / "blog" / "johansen-etf-lessons.md"

#: How the post spells a count of relations or nulls.
_WORDS = {0: "no", 1: "one", 2: "two", 3: "three"}


def _minus(x: float, places: int) -> str:
    """A figure at the post's precision, with the post's minus sign, U+2212."""
    return f"{x:.{places}f}".replace("-", "−")


def _dollars(x: float) -> str:
    """Dollars to the cent, the sign ahead of the dollar sign, as the post writes them."""
    return f"{'−' if x < 0 else ''}${abs(x):.2f}"


def _table(rows: list[str]) -> str:
    """A LaTeX array's rows as the post writes them, through its closing line."""
    return " \\\\\n".join(rows) + "\n\\end{array}"


@pytest.fixture(scope="module")
def post() -> str:
    return POST.read_text(encoding="utf-8")


class TestWhatThePostQuotes:
    """One copy of each figure ``blog/johansen-etf-lessons.md`` quotes, rebuilt from the run.

    Each fragment is formatted from the computed value at the precision the
    post prints, with the words around it, so it also says which copy it holds
    where the post quotes a figure more than once. Each table is rebuilt whole,
    so a digit added to a cell fails as well as a digit changed. The script's
    printout and the book's figures come from the module's constants, which
    the classes above already compare with the run. Chan's words, the Kindle
    locations and the shapes the alt text describes are not rebuilt, since
    README lists them as not pinned. A re-pin that leaves the post behind
    fails here, and so does an edit to the post that leaves the run behind.
    """

    @staticmethod
    def _holds(post: str, *fragments: str) -> None:
        missing = [f for f in fragments if f not in post]
        assert not missing, f"{SPEC}: the post does not say {missing}"

    def test_the_opening_and_the_file(self, sources, post, result) -> None:
        members, closes = sources
        s, days = result.strategy, result.days
        folder = LIFTED_SOURCES[SOURCE_FILE][3]
        etfs = len(list((paths.DATA_DIR / folder).glob("*.csv")))
        (saved,) = {m.obtained for m in members}
        assert np.isfinite(closes.to_numpy()).all(), SPEC
        self._holds(
            post,
            f"The CADF statistic is {_minus(result.cadf.t, 8)}. The portfolio Chan builds "
            f"from the three ETFs takes {s.half_life:.6f} days to close half its distance",
            f"an annual percentage rate, or APR, of {s.apr:.6f} with a Sharpe ratio of "
            f"{s.sharpe:.6f}, the book’s {BOOK_APR_PERCENT} percent and {BOOK_SHARPE}",
            f"saved on {saved}. It holds {etfs} ETFs over {len(days):,} trading days, from "
            f"{days[0].date()} to {days[-1].date()}, and EWA, EWC and IGE each have a close "
            "on every one of those days.",
        )

    def test_lesson_1_s_tables(self, post, result) -> None:
        p, t, s, cadf = result.pair, result.triplet, result.strategy, result.cadf
        header = r" & \text{Computed} & \text{Printed} \\ \hline" + "\n"
        first = rf"\text{{Figure}}{header}" + _table(
            [
                rf"\text{{CADF statistic}} & {cadf.t:.10f} & {SCRIPT_CADF_T}",
                rf"\text{{CADF }} \lambda & {cadf.ar1:.10f} & {SCRIPT_CADF_AR1}",
                rf"\text{{Half-life, days}} & {s.half_life:.10f} & {SCRIPT_HALF_LIFE}",
                rf"\text{{APR}} & {s.apr:.10f} & {SCRIPT_APR}",
                rf"\text{{Sharpe ratio}} & {s.sharpe:.10f} & {SCRIPT_SHARPE}",
            ]
        )
        johansen_rows = []
        for name, tested, printed in (
            ("Pair", p, (SCRIPT_PAIR_TRACE, SCRIPT_PAIR_EIGEN)),
            ("Triplet", t, (SCRIPT_TRIPLET_TRACE, SCRIPT_TRIPLET_EIGEN)),
        ):
            for statistic, shown in zip(("trace", "eigen"), printed, strict=True):
                for i, (value, cell) in enumerate(
                    zip(getattr(tested, statistic), shown, strict=True)
                ):
                    johansen_rows.append(
                        rf"\text{{{name} {statistic}, }} r \le {i} & {value:.6f} & {cell}"
                    )
        for i, (value, cell) in enumerate(zip(t.eigenvalues, SCRIPT_EIGENVALUES, strict=True)):
            johansen_rows.append(rf"\text{{Triplet eigenvalue {i + 1}}} & {value:.8f} & {cell}")
        for symbol, value, row in zip(
            TRIPLET, t.eigenvectors[:, 0], SCRIPT_EIGENVECTORS, strict=True
        ):
            johansen_rows.append(rf"\text{{First eigenvector, {symbol}}} & {value:.4f} & {row[0]}")
        self._holds(
            post,
            first,
            rf"\text{{Johansen figure}}{header}" + _table(johansen_rows),
            f"1. A CADF statistic of about {BOOK_CADF_T.replace('-', '−')}.\n"
            f"2. A half-life of {BOOK_HALF_LIFE_DAYS} days.\n"
            f"3. An APR of {BOOK_APR_PERCENT} percent.\n"
            f"4. A Sharpe ratio of {BOOK_SHARPE}.",
        )

    def test_lesson_1_s_cadf_bars_and_the_sign(self, post, result) -> None:
        one, five = (float(v) for v in SCRIPT_CADF_CRITICAL[:2])
        assert one < result.cadf.t < five, SPEC
        self._holds(
            post,
            f"{_minus(one, 3)} at 99 percent and {_minus(five, 3)} at 95. The computed "
            f"{_minus(result.cadf.t, 4)} is below {_minus(five, 3)} but above {_minus(one, 3)}, "
            "and a CADF statistic clears its bar by falling below it. So the pair "
            "cointegrates at 95 percent",
            "and not at 99, which he does not claim",
            f"MATLAB gave {SCRIPT_EIGENVECTORS[0][0].replace('-', '−')} there",
        )

    def test_the_figure_s_alt_text(self, sources, post, result) -> None:
        closes, days = sources[1], result.days
        cumret = np.cumprod(1 + result.strategy.daily) - 1
        deepest, longest = calculate_max_dd(cumret)
        _, drawdown, duration = drawdown_path(cumret)
        trough = str(days[int(np.argmin(drawdown))].date())
        last = int(np.argmax(duration))
        high, first, end = (
            str(days[row].date()) for row in (last - longest, last - longest + 1, last)
        )
        mean = float(np.mean(closes["EWC"] - result.hedge_ratio * closes["EWA"]))
        t, s = result.triplet, result.strategy
        five = float(SCRIPT_CADF_CRITICAL[1])
        assert (t.trace > t.trace_critical[:, 1]).all(), SPEC
        assert (t.trace < t.trace_critical[:, 2]).all(), SPEC
        assert t.eigen[0] < t.eigen_critical[0, 0], SPEC
        self._holds(
            post,
            f"three of them over the file’s {len(days):,} trading days, from "
            f"{days[0]:%B %Y} to {days[-1]:%B %Y}",
            f"the residual EWC − {result.hedge_ratio:.4f}·EWA, which crosses a dashed line "
            f"at its mean of {mean:.2f}, the regression’s intercept",
            f"the CADF statistic of {_minus(result.cadf.t, 4)} against the 95 percent bar "
            f"of {_minus(five, 3)}",
            f"Every trace column, {t.trace[0]:.3f}, {t.trace[1]:.3f} and {t.trace[2]:.3f}, "
            "rises above its 95 percent line and stops below its 99 percent line.",
            f"The first eigen column, {t.eigen[0]:.3f}, stops below even its 90 percent line, "
            f"and a note reads {t.eigen[0]:.3f}, short of {t.eigen_critical[0, 0]:.3f}, its "
            "90 percent bar.",
            f"climbs from 0 to a high on {high}, sits below that high in a shaded band "
            f"labelled {longest} days, from {first} to {end}, with its deepest drawdown of "
            f"{_minus(deepest, 6)} marked on {trough}, and ends near "
            f"{round(100 * cumret[-1])} percent.",
            f"an APR of {s.apr:.6f} and a Sharpe ratio of {s.sharpe:.4f} against the book’s "
            f"{BOOK_APR_PERCENT} percent and {BOOK_SHARPE}.",
        )

    def test_lesson_2(self, sources, post, result) -> None:
        closes = sources[1]
        x, y = closes["EWA"].to_numpy(dtype=float), closes["EWC"].to_numpy(dtype=float)
        slope, intercept = ols(y, np.column_stack([x, np.ones(len(x))])).beta
        assert slope == pytest.approx(result.hedge_ratio, abs=1e-12), SPEC
        five = float(SCRIPT_CADF_CRITICAL[1])
        assert max(result.cadf.t, result.reversed_cadf.t) < five, SPEC
        gap = max(
            np.max(np.abs(getattr(result.reordered_triplet, k) - getattr(result.triplet, k)))
            for k in ("trace", "eigen", "eigenvalues")
        )
        assert gap < 1e-11, SPEC
        reordered = result.reordered_triplet.eigenvectors[[1, 0, 2]]
        negated = int(np.sum(np.sign(reordered[0] / result.triplet.eigenvectors[0]) < 0))
        self._holds(
            post,
            f"With EWA on the left, the statistic is {_minus(result.reversed_cadf.t, 4)} "
            f"against {_minus(result.cadf.t, 4)}, and both are past the 95 percent bar of "
            f"{_minus(five, 3)}.",
            f"over all {len(result.days):,} days and holds it fixed. With EWC on the left, "
            f"it finds a slope of {slope:.4f}, which is the hedge ratio, and an intercept of "
            f"{intercept:.4f}, the constant the regression adds.",
            "within 10⁻¹¹ of the first run",
            f"and {_WORDS[negated]} of the three come back negated",
        )

    def test_lesson_3(self, post, result) -> None:
        t = result.triplet
        levels = (90, 95, 99)

        def block(name: str, values: np.ndarray, critical: np.ndarray) -> list[str]:
            return [rf"\text{{{name}}} & " + " & ".join(f"{v:.3f}" for v in values)] + [
                rf"\text{{Bar, {level} percent}} & "
                + " & ".join(f"{v:.3f}" for v in critical[:, j])
                for j, level in enumerate(levels)
            ]

        table = (
            r"\text{Null} & "
            + " & ".join(rf"r \le {i}" for i in range(len(t.trace)))
            + " \\\\ \\hline\n"
            + " \\\\\n".join(block("Trace", t.trace, t.trace_critical))
            + " \\\\ \\hline\n"
            + _table(block("Eigen", t.eigen, t.eigen_critical))
        )
        assert [t.relations("eigen", level) for level in levels] == [0, 0, 0], SPEC
        assert t.eigen[2] > t.eigen_critical[2, 1], SPEC
        assert t.relations("trace", 99) == 0, SPEC
        self._holds(
            post,
            f"so the triplet’s {t.trace[0]:.3f} is {t.eigen[0]:.3f} plus {t.eigen[1]:.3f} "
            f"plus {t.eigen[2]:.3f}",
            table,
            f"The trace test rejects all {_WORDS[len(t.trace)]} nulls at 95 percent, so it "
            f"counts {_WORDS[t.relations('trace', 95)]} relations.",
            f"Its {t.eigen[0]:.3f} falls short of even the 90 percent bar of "
            f"{t.eigen_critical[0, 0]:.3f}, so it rejects nothing and counts no relations at "
            "any of the three levels.",
            f"as {t.eigen[2]:.3f} clears {t.eigen_critical[2, 1]:.3f}",
            f"At 99 percent the trace test falls short too, since {t.trace[0]:.3f} is below "
            f"{t.trace_critical[0, 2]:.3f}, so at that level neither test finds a relation.",
        )

    def test_lesson_4(self, post, result) -> None:
        p, adf, t = result.pair, result.adf, result.triplet
        margin = p.trace[1] - p.trace_critical[1, 1]
        assert p.eigen[1] == pytest.approx(p.trace[1], abs=1e-12), SPEC
        assert p.eigen_critical[1, 1] == p.trace_critical[1, 1], SPEC
        assert p.relations("trace", 95) == p.relations("eigen", 95), SPEC
        assert p.relations("trace", 99) != p.relations("eigen", 99), SPEC
        self._holds(
            post,
            "On the pair, both tests agree at 95 percent. "
            f"The trace test rejects r ≤ 0 with {p.trace[0]:.3f}, past even its 99 percent "
            f"bar of {p.trace_critical[0, 2]:.3f}, and the eigen test rejects it with "
            f"{p.eigen[0]:.3f} against {p.eigen_critical[0, 1]:.3f} at 95. Both then reject "
            f"r ≤ 1 with {p.trace[1]:.3f} against {p.trace_critical[1, 1]:.3f}. So both "
            f"count {_WORDS[p.relations('trace', 95)]} relations between EWA and EWC.",
            f"gives {_minus(adf['EWA'], 2)} for EWA, {_minus(adf['EWC'], 2)} for EWC and "
            f"{_minus(adf['IGE'], 2)} for IGE. All three fall short of "
            f"{_minus(ADF_CRIT_CONST['10%'], 2)}, the bar for rejecting a unit root at even "
            "90 percent confidence",
            f"rests on {p.trace[1]:.3f} against a bar of {p.trace_critical[1, 1]:.3f}. It "
            f"clears its bar by only {margin:.3f}. At 99 percent the bar is "
            f"{p.trace_critical[1, 2]:.3f}, and the trace test counts "
            f"{_WORDS[p.relations('trace', 99)]} relation rather than "
            f"{_WORDS[p.relations('trace', 95)]}.",
            f"The triplet’s trace count of {_WORDS[t.relations('trace', 95)]} says the same of "
            f"all {_WORDS[len(t.trace)]}.",
        )

    def test_lesson_5(self, sources, post, result) -> None:
        s = result.strategy
        w = s.weights
        closes = sources[1][list(TRIPLET)]
        dollars = w * closes.iloc[-1].to_numpy(dtype=float)
        lives = result.eigenvector_half_lives
        first = int(np.flatnonzero(s.daily)[0])
        self._holds(
            post,
            f"in shares: {w[0]:.4f} of EWC, {_minus(w[1], 4)} of EWA and {_minus(w[2], 4)} of IGE",
            f"On the file’s last day, {closes.index[-1].date()}, one unit of it holds "
            f"{_dollars(dollars[0])} of EWC against {_dollars(dollars[1])} of EWA and "
            f"{_dollars(dollars[2])} of IGE",
            f"Its half-life is {lives[0]:.1f} days, against {lives[1]:.1f} for the second "
            f"eigenvector’s portfolio and {lives[2]:.1f} for the third’s",
            f"The rule rounds {s.half_life:.1f} to a lookback of {s.lookback} days. Its first "
            f"return comes on {result.days[first].date()}, the trading day after the "
            f"{s.lookback}-day moving standard deviation first has {s.lookback} days to use, "
            f"and it earns a return on every one of the {np.count_nonzero(s.daily):,} days "
            "from there on.",
        )

    def test_lesson_6_and_what_the_run_cannot_say(self, post, result) -> None:
        t, p = result.triplet, result.pair
        cumret = np.cumprod(1 + result.strategy.daily) - 1
        deepest, longest = calculate_max_dd(cumret)
        _, drawdown, duration = drawdown_path(cumret)
        trough = str(result.days[int(np.argmin(drawdown))].date())
        last = int(np.argmax(duration))
        first, end = (str(result.days[row].date()) for row in (last - longest + 1, last))
        margin = p.trace[1] - p.trace_critical[1, 1]
        assert t.relations("eigen", 95) == 0, SPEC
        self._holds(
            post,
            f"the same {len(result.days):,} days the rule then trades",
            f"and it leaves the {BOOK_APR_PERCENT} percent in-sample",
            f"the deepest drawdown is {_minus(deepest, 6)}, with its trough on {trough}. Its "
            f"longest spell below a high runs {longest} trading days, from {first} to {end}",
            f"and the pair’s full rank clears its bar by only {margin:.3f}.",
            f"here one counts {_WORDS[t.relations('trace', 95)]} relations where the other "
            "counts none",
        )
