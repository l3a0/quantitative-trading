"""The pins for the three hypothesis tests on TU momentum, *Algorithmic Trading*'s Example 1.1.

This file is the single authority for every number a prose surface quotes
about this example and the rows beside it. One surface also quotes numbers
held elsewhere. ``blog/tu-hypothesis-tests-lessons.md`` takes the 49 pairs
behind the rule from ``tests/test_tu_momentum.py``, its figure's labels from
``tests/test_tu_hypothesis_tests_figures.py``, its sketches' labels from
``tests/test_tu_hypothesis_tests_whiteboard.py``, and the index arbitrage
post's 480 stocks from ``tests/test_index_arbitrage.py``.
README lists what the post says that nothing asserts. ``docs/replication-log.md``
Entry 37 carries the verdicts and points here row by row. The run itself comes
from ``tu_hypothesis_run`` in ``tests/conftest.py``, which the figure's pins
share.

Every pin reads one vintage and one specification, so both are stated once
here.

- **Vintage.** ``inputdataohlcdaily_20120511/tu.csv``, chan-mat, adjusted,
  saved 2012-05-12, lifted from ``inputDataOHLCDaily_20120511.mat``. TU's own
  column holds 2,000 days from 2004-06-01 to 2012-05-11, read through
  ``chan.tu_momentum.read_sources``, which runs the scale-break guard over the
  whole span. Its identity is its row of ``LIFTED_SOURCES`` in
  ``tests/support/committed_vintages.py``.
- **Specification.** ``TU_mom_hypothesisTest.m`` at EpchanPreview
  ``e4bc46f``, git blob ``c0dda16``, with a lookback of 250 and a hold of 25,
  under the declaration
  [issue 352](https://github.com/l3a0/quantitative-trading/issues/352) wrote
  before any draw on either seed. The second test draws series i of 10,000 from
  row i of ``default_rng(20261010).random((10_000, 2_000))`` through the
  Pearson type IV inverse CDF on a θ grid of 20,001 points, and reruns the
  strategy on ``cumprod(1 + r) − 1``. The corrected third test applies draw d
  of 100,000 ``default_rng(20261011).permutation(2_000)`` calls to both signal
  arrays and earns the observed market returns. A count lands within two
  binomial standard errors of the printed proportion at the test's own N.

Each computed count is pinned exactly at its seed, and each proportion at six
decimals, so a change to the draw method cannot move a count inside its band
unnoticed. ``TestTheRowsBesideAddedAfterTheScratchRun`` holds the three rows
the issue added after a scratch run on other seeds had seen results.

Exploratory. The three tests are Chan's, on a strategy whose lookback and hold
he chose from a table computed on the same closes. The example first ran on
the declared seeds on 2026-10-10.
"""

from __future__ import annotations

import dataclasses
import io
import math
from contextlib import redirect_stdout

import numpy as np
import pytest
from scipy import integrate, optimize
from scipy.special import ndtr, ndtri

from chan import paths, tu_momentum
from chan.khandani_lo_book_two import gap, matches
from chan.series import WindowCrossesScaleBreak
from chan.tu_hypothesis_tests import (
    AS_WRITTEN_DRAWS,
    BOOK_RANDOMIZED_RETURNS_COUNT,
    BOOK_RANDOMIZED_TRADES_COUNT,
    BOOK_RETURNS_BAND,
    BOOK_RETURNS_DRAWS,
    BOOK_TRADES_BAND,
    BOOK_TRADES_DRAWS,
    GRID_POINTS,
    RETURNS_DRAWS,
    RETURNS_SEED,
    SCRIPT_RANDOMIZED_RETURNS_P_VALUE,
    SCRIPT_RETURNS_BAND,
    TRADES_DRAWS,
    TRADES_SEED,
    HypothesisTests,
    band_verdict,
    count_at_or_above,
    fixed_position_returns,
    landing_band,
    main,
    pearson_iv_draws,
    pearson_iv_parameters,
    pearson_kappa,
    permuted_strategy_returns,
    randomized_returns,
    randomized_trades,
    report,
    script_moments,
    simulated_strategy_returns,
)
from chan.tu_momentum import (
    HOLD_DAYS,
    LOOKBACK,
    SCRIPT_GAUSSIAN_STATISTIC,
    SOURCE_FILE,
    market_returns,
    positions,
    read_sources,
    signals,
    strategy_returns,
)
from tests.support.committed_vintages import LIFTED_SOURCES
from tests.support.pearson_iv import closed_form_moments

#: The draws the vectorized form is held to the one-dimensional functions on.
EQUALITY_DRAWS = 200

#: The shuffles the net-position pin reads, the first of the third test's draws.
NET_POSITION_DRAWS = 500

#: The simulated series the long-share pin reads, the first of the second test's.
LONG_SHARE_DRAWS = 1_000


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def strategy(sources):
    """Example 6.1 on TU, through ``chan.tu_momentum``'s exported functions."""
    cl = sources[1].to_numpy(dtype=float)
    market = market_returns(cl)
    longs, shorts = signals(cl)
    held = positions(longs, shorts, HOLD_DAYS)
    return {
        "market": market,
        "longs": longs,
        "shorts": shorts,
        "held": held,
        "daily": strategy_returns(held, market, HOLD_DAYS),
    }


@pytest.fixture(scope="module")
def moments(strategy):
    return script_moments(strategy["market"])


@pytest.fixture(scope="module")
def params(moments):
    return pearson_iv_parameters(moments.mean, moments.std, moments.skewness, moments.kurtosis)


@pytest.fixture(scope="module")
def ran(tu_hypothesis_run) -> tuple[HypothesisTests, str]:
    """``run`` on the declared seeds, with what it prints, shared with the figure's pins."""
    return tu_hypothesis_run


@pytest.fixture(scope="module")
def result(ran) -> HypothesisTests:
    return ran[0]


@pytest.fixture(scope="module")
def printed(ran) -> str:
    return ran[1]


@pytest.fixture(scope="module")
def net_positions(strategy):
    """The net position of each of the first 500 shuffles on seed 20261011, one row per draw.

    Draw d here is the d-th ``default_rng(20261011).permutation(2_000)``
    call, the same permutation the corrected third test applies as its draw
    d. Module-scoped, so its pin and the post's reading share one computation.
    """
    longs, shorts = strategy["longs"], strategy["shorts"]
    rng = np.random.default_rng(TRADES_SEED)
    return np.stack(
        [
            positions(longs[order], shorts[order], HOLD_DAYS)
            for order in (rng.permutation(len(longs)) for _ in range(NET_POSITION_DRAWS))
        ]
    )


@pytest.fixture(scope="module")
def long_shares(params, moments) -> tuple[float, float]:
    """The long share of entry days on the first 1,000 series, with the drift and without it.

    Module-scoped, so its pin and the post's reading share one computation.
    """
    uniforms = np.random.default_rng(RETURNS_SEED).random((LONG_SHARE_DRAWS, 2_000))
    simulated = pearson_iv_draws(params, uniforms)
    shares = []
    for draws in (simulated, simulated - moments.mean):
        cl_sim = np.cumprod(1 + draws, axis=1) - 1
        longs = cl_sim[:, LOOKBACK:] > cl_sim[:, :-LOOKBACK]
        shorts = cl_sim[:, LOOKBACK:] < cl_sim[:, :-LOOKBACK]
        shares.append(float((longs.sum(axis=1) / (longs.sum(axis=1) + shorts.sum(axis=1))).mean()))
    return shares[0], shares[1]


@pytest.fixture
def no_arguments(monkeypatch):
    """``main`` parses ``sys.argv``, which under pytest holds pytest's own arguments."""
    monkeypatch.setattr("sys.argv", ["chan.tu_hypothesis_tests"])


class TestTheDeclaration:
    def test_the_seeds_and_the_draw_counts_are_the_issue_s(self) -> None:
        assert (RETURNS_SEED, TRADES_SEED) == (20261010, 20261011)
        assert (RETURNS_DRAWS, TRADES_DRAWS) == (10_000, 100_000)
        assert AS_WRITTEN_DRAWS == 10
        assert (LOOKBACK, HOLD_DAYS) == (250, 25)

    def test_the_printed_figures(self) -> None:
        assert (
            SCRIPT_GAUSSIAN_STATISTIC,
            BOOK_RANDOMIZED_RETURNS_COUNT,
            SCRIPT_RANDOMIZED_RETURNS_P_VALUE,
            BOOK_RANDOMIZED_TRADES_COUNT,
        ) == ("2.93", "1166", "0.027500", "0")

    def test_the_landing_bands(self) -> None:
        """Two binomial standard errors of the printed proportion at the test's own N."""
        assert BOOK_RETURNS_BAND == (1102, 1230)
        assert SCRIPT_RETURNS_BAND == (243, 307)
        assert BOOK_TRADES_BAND == (0, 0)
        assert math.sqrt(10_000 * 0.1166 * 0.8834) == pytest.approx(32.1, abs=0.05)
        assert math.sqrt(10_000 * 0.0275 * 0.9725) == pytest.approx(16.4, abs=0.05)

    def test_a_band_includes_both_ends(self) -> None:
        assert landing_band(0.5, 100) == (40, 60)
        assert band_verdict(1102, BOOK_RETURNS_BAND) == "reproduced"
        assert band_verdict(1230, BOOK_RETURNS_BAND) == "reproduced"
        assert band_verdict(1101, BOOK_RETURNS_BAND) == "did not reproduce"
        assert band_verdict(1231, BOOK_RETURNS_BAND) == "did not reproduce"
        assert band_verdict(0, BOOK_TRADES_BAND) == "reproduced"
        assert band_verdict(1, BOOK_TRADES_BAND) == "did not reproduce"

    def test_a_count_includes_a_tie(self) -> None:
        """L71 and L108 count ``mean(ret_sim) >= mean(ret)``."""
        assert count_at_or_above([0.1, 0.2, 0.3], 0.2) == 2

    def test_the_draw_method_is_pinned(self, params) -> None:
        """The seed means these draws only under this method, so the first of each is pinned."""
        assert GRID_POINTS == 20_001
        uniforms = np.random.default_rng(RETURNS_SEED).random((1, 2_000))
        first = pearson_iv_draws(params, uniforms)[0, :3]
        np.testing.assert_allclose(
            first,
            [0.0011298316172907972, -0.0020176764443526132, -0.0020462351456987],
            rtol=1e-9,
        )
        order = np.random.default_rng(TRADES_SEED).permutation(2_000)
        assert order[:5].tolist() == [270, 460, 1503, 1169, 315]

    def test_uniforms_in_batches_are_one_call(self) -> None:
        whole = np.random.default_rng(RETURNS_SEED).random((1_000, 2_000))
        rng = np.random.default_rng(RETURNS_SEED)
        parts = np.concatenate([rng.random((rows, 2_000)) for rows in (1, 499, 500)])
        np.testing.assert_array_equal(whole, parts)


class TestTheVintage:
    def test_tu_is_its_pinned_source(self, sources) -> None:
        entry, closes = sources
        vendor, basis, saved, folder, _ = LIFTED_SOURCES[SOURCE_FILE]
        assert (entry.vendor, entry.price_basis, entry.obtained) == (vendor, basis, saved)
        assert saved == "2012-05-12"
        assert entry.path == f"{folder}/tu.csv" == "inputdataohlcdaily_20120511/tu.csv"
        assert len(closes) == 2000
        assert str(closes.index[0].date()) == "2004-06-01"
        assert str(closes.index[-1].date()) == "2012-05-11"

    def test_the_run_reads_the_strategy_s_own_returns(self, strategy, result) -> None:
        np.testing.assert_array_equal(result.daily, strategy["daily"])
        assert result.observed_mean == pytest.approx(6.626644e-05, rel=5e-7)
        assert result.observed_mean > 0

    def test_the_signals_hold_1274_long_and_474_short_days(self, strategy) -> None:
        """One permutation applied to both keeps these counts, which location 669 asks for."""
        assert int(strategy["longs"].sum()) == 1274
        assert int(strategy["shorts"].sum()) == 474
        assert not (strategy["longs"] & strategy["shorts"]).any()


class TestThePearsonIV:
    def test_the_script_s_moments_of_tu(self, moments, result) -> None:
        """MATLAB's n − 1 ``std``, and biased skewness and kurtosis not in excess form."""
        assert moments == result.moments
        assert moments.mean == pytest.approx(5.999783e-05, rel=5e-7)
        assert moments.std == pytest.approx(1.095464e-03, rel=5e-7)
        assert moments.skewness == pytest.approx(-0.265892, abs=5e-7)
        assert moments.kurtosis == pytest.approx(12.115073, abs=5e-7)

    def test_the_moments_put_tu_in_type_iv(self, moments) -> None:
        b1, b2 = moments.skewness**2, moments.kurtosis
        kappa = b1 * (b2 + 3) ** 2 / (4 * (4 * b2 - 3 * b1) * (2 * b2 - 3 * b1 - 6))
        assert b1 == pytest.approx(0.070699, abs=5e-7)
        assert kappa == pytest.approx(0.004645, abs=5e-7)
        assert 0 < kappa < 1

    def test_the_parameters(self, params) -> None:
        assert params.m == pytest.approx(2.838885, abs=5e-7)
        assert params.nu == pytest.approx(0.251239, abs=5e-7)
        assert params.a == pytest.approx(1.788437e-03, rel=5e-7)
        assert params.lam == pytest.approx(1.821709e-04, rel=5e-7)

    def test_the_closed_form_moments_are_the_targets(self, moments, params) -> None:
        found = closed_form_moments(params.m, params.nu, params.a, params.lam)
        targets = (moments.mean, moments.std, moments.skewness, moments.kurtosis)
        np.testing.assert_allclose(found, targets, rtol=1e-12, atol=0)

    def test_a_case_worked_by_hand(self) -> None:
        """A skewness of 1 and a kurtosis of 5 give r = 18, so m = 10, ν = −72, a = 1, λ = −4."""
        found = pearson_iv_parameters(0.0, 1.0, 1.0, 5.0)
        assert (found.m, found.nu, found.a, found.lam) == pytest.approx((10, -72, 1, -4))
        np.testing.assert_allclose(
            closed_form_moments(found.m, found.nu, found.a, found.lam), (0, 1, 1, 5), atol=1e-12
        )

    @pytest.mark.parametrize(
        ("skewness", "kurtosis", "family"),
        [
            (0.0, 3.0, "normal"),
            (0.0, 12.0, "type VII"),
            (1.0, 3.0, "type I"),
            (1.5, 7.0, "type VI"),
            (2.0, 9.0, "type III, on the boundary"),
        ],
    )
    def test_moments_outside_type_iv_are_refused(self, skewness, kurtosis, family) -> None:
        with pytest.raises(ValueError, match="outside type IV"):
            pearson_iv_parameters(0.0, 1.0, skewness, kurtosis)

    def test_type_vi_just_past_type_iv_is_refused_on_the_module_s_own_kappa(self) -> None:
        """A skewness of 1.5 and a kurtosis of 7.5 give κ = 1.185, type VI.

        ``test_the_moments_put_tu_in_type_iv`` recomputes κ rather than reading
        the module's, and the refusals above still refuse with the sign inside
        ``4·β₂ − 3·β₁`` flipped. These moments do not. The flipped sign gives
        them 0.75, so they pass as type IV and then fail on a negative square
        root, whose message does not name the type.
        """
        with pytest.raises(ValueError, match=r"Pearson κ of 1\.18548, outside type IV"):
            pearson_iv_parameters(0.0, 1.0, 1.5, 7.5)

    def test_moments_that_zero_kappa_s_denominator_are_refused_by_type(self) -> None:
        """A skewness of 2 and a kurtosis of 3 make 4·β₂ equal 3·β₁.

        No distribution has them, since kurtosis is at least skewness² + 1.
        κ's denominator is zero there, so the refusal has to come before κ is
        computed, or the caller meets a ``ZeroDivisionError`` instead.
        """
        with pytest.raises(ValueError, match="outside type IV"):
            pearson_iv_parameters(0.0, 1.0, 2.0, 3.0)

    def test_the_mean_moves_only_lambda(self, moments, params) -> None:
        """Why the mean-zero row is the declared draws less their target mean."""
        centred = pearson_iv_parameters(0.0, moments.std, moments.skewness, moments.kurtosis)
        assert (centred.m, centred.nu, centred.a) == (params.m, params.nu, params.a)
        assert centred.lam == pytest.approx(params.lam - moments.mean, abs=1e-18)
        uniforms = np.random.default_rng(5).random(1_000)
        np.testing.assert_allclose(
            pearson_iv_draws(centred, uniforms),
            pearson_iv_draws(params, uniforms) - moments.mean,
            rtol=0,
            atol=1e-17,
        )

    def test_the_draws_rise_with_the_uniform(self, params) -> None:
        draws = pearson_iv_draws(params, np.linspace(0, 1, 100_001)[1:-1])
        assert (np.diff(draws) > 0).all()

    @pytest.mark.parametrize("sds", [5, 10])
    def test_the_tail_mass_matches_quadrature(self, moments, params, sds) -> None:
        """The grid's mass beyond the mean ± sds·std, against the density integrated in θ."""

        def density(theta: float) -> float:
            return math.cos(theta) ** (2 * params.m - 2) * math.exp(-params.nu * theta)

        def theta_of(x: float) -> float:
            return math.atan((x - params.lam) / params.a)

        whole = integrate.quad(density, -math.pi / 2, math.pi / 2, limit=200)[0]
        upper, lower = moments.mean + sds * moments.std, moments.mean - sds * moments.std
        upper_tail = integrate.quad(density, theta_of(upper), math.pi / 2, limit=200)[0] / whole
        lower_tail = integrate.quad(density, -math.pi / 2, theta_of(lower), limit=200)[0] / whole

        def at(u: float) -> float:
            return float(pearson_iv_draws(params, np.array([u]))[0])

        grid_upper = 1 - optimize.brentq(lambda u: at(u) - upper, 0.5, 1 - 1e-15, xtol=1e-18)
        grid_lower = optimize.brentq(lambda u: at(u) - lower, 1e-15, 0.5, xtol=1e-18)
        assert grid_upper == pytest.approx(upper_tail, rel=1e-3)
        assert grid_lower == pytest.approx(lower_tail, rel=1e-3)

    def test_the_declared_draws_have_the_target_mean_and_std(self, moments, result) -> None:
        """Within four standard errors over all 20 million draws.

        The standard error of the std uses the target kurtosis, which exists
        because this type IV has moments below order 4.68. Skewness and
        kurtosis get no sample check, because their sampling error needs
        moments from 6 up, and the closed form above is their check.
        """
        n = RETURNS_DRAWS * 2_000
        found = result.returns
        assert found.draw_mean == pytest.approx(6.014505e-05, rel=5e-7)
        assert found.draw_std == pytest.approx(1.095392e-03, rel=5e-7)
        mean_error = moments.std / math.sqrt(n)
        std_error = moments.std * math.sqrt((moments.kurtosis - 1) / (4 * n))
        assert abs(found.draw_mean - moments.mean) < 4 * mean_error
        assert abs(found.draw_std - moments.std) < 4 * std_error


class TestTheVectorizedForm:
    """The two-dimensional form equals ``chan.tu_momentum``'s functions, draw by draw."""

    def test_the_second_test_on_the_first_200_draws(self, params, moments, strategy, result):
        uniforms = np.random.default_rng(RETURNS_SEED).random((EQUALITY_DRAWS, 2_000))
        simulated = pearson_iv_draws(params, uniforms)
        normal = moments.mean + moments.std * ndtri(uniforms)
        for draws, means in (
            (simulated, result.returns.declared),
            (normal, result.returns.normal),
            (simulated - moments.mean, result.returns.mean_zero),
        ):
            expected = np.stack(
                [
                    strategy_returns(
                        positions(*signals(np.cumprod(1 + row) - 1, LOOKBACK), HOLD_DAYS),
                        row,
                        HOLD_DAYS,
                    )
                    for row in draws
                ]
            )
            found = simulated_strategy_returns(draws)
            np.testing.assert_allclose(found, expected, rtol=0, atol=1e-15)
            np.testing.assert_allclose(
                means[:EQUALITY_DRAWS], expected.mean(axis=1), rtol=0, atol=1e-15
            )

    def test_the_observed_positions_on_the_first_200_draws(self, params, strategy, result):
        uniforms = np.random.default_rng(RETURNS_SEED).random((EQUALITY_DRAWS, 2_000))
        simulated = pearson_iv_draws(params, uniforms)
        expected = np.stack([strategy_returns(strategy["held"], row) for row in simulated])
        np.testing.assert_allclose(
            fixed_position_returns(strategy["held"], simulated), expected, rtol=0, atol=1e-15
        )
        np.testing.assert_allclose(
            result.returns.observed_positions[:EQUALITY_DRAWS],
            expected.mean(axis=1),
            rtol=0,
            atol=1e-15,
        )

    def test_the_third_test_on_the_first_200_draws(self, strategy, result) -> None:
        rng = np.random.default_rng(TRADES_SEED)
        orders = np.stack([rng.permutation(2_000) for _ in range(EQUALITY_DRAWS)])
        longs, shorts, market = strategy["longs"], strategy["shorts"], strategy["market"]
        expected = np.stack(
            [
                strategy_returns(positions(longs[order], shorts[order], HOLD_DAYS), market)
                for order in orders
            ]
        )
        found = permuted_strategy_returns(longs, shorts, orders, market)
        np.testing.assert_allclose(found, expected, rtol=0, atol=1e-15)
        np.testing.assert_allclose(
            result.trades[:EQUALITY_DRAWS], expected.mean(axis=1), rtol=0, atol=1e-15
        )

    def test_the_second_test_does_not_depend_on_the_batch(self, moments, strategy, result):
        for batch in (300, 128):
            found = randomized_returns(moments, strategy["held"], draws=300, batch=batch)
            for name in ("declared", "observed_positions", "normal", "mean_zero"):
                np.testing.assert_array_equal(
                    getattr(found, name), getattr(result.returns, name)[:300]
                )

    def test_the_third_test_does_not_depend_on_the_batch(self, strategy, result) -> None:
        for batch in (2_500, 700):
            found = randomized_trades(
                strategy["longs"], strategy["shorts"], strategy["market"], draws=2_500, batch=batch
            )
            np.testing.assert_array_equal(found, result.trades[:2_500])

    def test_a_last_batch_of_one_draw_is_kept(self, strategy, result) -> None:
        """701 draws in batches of 700 leave one draw for a second batch.

        The batch sizes in the two tests above leave a last batch of 44 or 400
        draws, or none, so a loop that stops one draw short of the total still
        reaches every batch there.
        """
        found = randomized_trades(
            strategy["longs"], strategy["shorts"], strategy["market"], draws=701, batch=700
        )
        assert len(found) == 701
        np.testing.assert_array_equal(found, result.trades[:701])

    def test_the_second_test_earns_the_simulated_returns_not_cl_sim_s(self) -> None:
        """L68 multiplies by ``marketRet_sim``. ``cl_sim``'s own returns would differ."""
        simulated = np.array([[0.0, 0.5, -0.5, 0.25, 0.1, -0.2]])
        found = simulated_strategy_returns(simulated, lookback=1, hold_days=1)
        cl_sim = np.cumprod(1 + simulated[0]) - 1
        held = positions(*signals(cl_sim, 1), 1)
        np.testing.assert_allclose(found[0], strategy_returns(held, simulated[0], 1))
        assert not np.allclose(found[0], strategy_returns(held, market_returns(cl_sim), 1))

    def test_a_batch_of_zero_draws_is_refused(self, moments, strategy) -> None:
        with pytest.raises(ValueError, match="at least 1 draw"):
            randomized_returns(moments, strategy["held"], draws=10, batch=0)


class TestRow1TheGaussianStatistic:
    def test_it_lands_the_script_s_2_93(self, result) -> None:
        assert result.statistic == pytest.approx(2.933253, abs=5e-7)
        assert matches(result.statistic, SCRIPT_GAUSSIAN_STATISTIC)
        assert gap(result.statistic, SCRIPT_GAUSSIAN_STATISTIC) == 0.0

    def test_its_one_sided_normal_tail(self, result) -> None:
        """The p-value location 606's Gaussian null gives, which the mean-zero row lands near."""
        assert float(ndtr(-result.statistic)) == pytest.approx(0.001677, abs=5e-7)

    def test_the_null_s_spread_of_the_mean(self, result) -> None:
        """The strategy's daily ``std`` over √2,000, in closed form, with no seed.

        The figure draws the Gaussian null with this spread, and the post sets
        the mean-zero row's spread beside it. The statistic is the observed
        mean over this spread, so each pin checks the other.
        """
        std = float(result.daily.std(ddof=1))
        assert std == pytest.approx(1.010320e-03, rel=5e-7)
        spread = std / math.sqrt(len(result.daily))
        assert spread == pytest.approx(2.259145e-05, rel=5e-7)
        assert result.observed_mean / spread == pytest.approx(result.statistic, rel=1e-12)


class TestRows2And3TheRandomizedReturns:
    """One computed count, judged against the book's 1,166 and the script's 0.027500."""

    def test_the_count(self, result) -> None:
        assert result.count(result.returns.declared) == 1221
        assert len(result.returns.declared) == RETURNS_DRAWS

    def test_row_2_lands_the_book_s_1166(self, result) -> None:
        count = result.count(result.returns.declared)
        assert band_verdict(count, BOOK_RETURNS_BAND) == "reproduced"
        assert gap(count, BOOK_RANDOMIZED_RETURNS_COUNT) == 55
        assert BOOK_RETURNS_BAND[1] - count == 9

    def test_row_3_misses_the_script_s_0_027500(self, result) -> None:
        proportion = result.count(result.returns.declared) / RETURNS_DRAWS
        assert proportion == pytest.approx(0.122100, abs=5e-7)
        assert band_verdict(round(proportion * RETURNS_DRAWS), SCRIPT_RETURNS_BAND) == (
            "did not reproduce"
        )
        assert gap(proportion, SCRIPT_RANDOMIZED_RETURNS_P_VALUE) == pytest.approx(0.0946)

    def test_the_mean_simulated_return(self, result) -> None:
        assert float(result.returns.declared.mean()) == pytest.approx(3.220302e-05, rel=5e-7)
        assert float(result.returns.declared.max()) == pytest.approx(1.423978e-04, rel=5e-7)

    def test_the_spread_of_the_simulated_means(self, result) -> None:
        """The n − 1 ``std`` of the 10,000 means on seed 20261010's type IV draws."""
        assert float(result.returns.declared.std(ddof=1)) == pytest.approx(2.819219e-05, rel=5e-7)


class TestRow4TheCorrectedTrades:
    def test_no_draw_reaches_the_observed_mean(self, result) -> None:
        assert len(result.trades) == TRADES_DRAWS
        assert result.count(result.trades) == 0
        assert band_verdict(0, BOOK_TRADES_BAND) == "reproduced"
        assert gap(0, BOOK_RANDOMIZED_TRADES_COUNT) == 0

    def test_how_far_the_observed_mean_sits_above_them(self, result) -> None:
        """The rule-of-three bound then puts p below 3e-05 at 95 percent."""
        trades = result.trades
        assert float(trades.max()) == pytest.approx(3.973594e-05, rel=5e-7)
        assert float(trades.mean()) == pytest.approx(2.409664e-05, rel=5e-7)
        z = (result.observed_mean - trades.mean()) / trades.std(ddof=1)
        assert z == pytest.approx(11.131886, abs=5e-7)
        assert 3 / TRADES_DRAWS == 3e-05

    def test_the_shuffled_means_spread_far_less_than_the_simulated_ones(self, result) -> None:
        """The n − 1 ``std`` of seed 20261011's 100,000 means, against seed 20261010's 10,000.

        Shuffling scatters the long and short entry days across the sample,
        so the trades open on any day mostly cancel into a net long position
        of about the same size on every shuffle. A position nearly the same on
        every shuffle earns nearly the same mean on the same returns, so the
        shuffled means vary far less than means on new returns do, which is why
        the figure's third panel is narrow. The test below pins the
        cancellation.
        """
        shuffled = float(result.trades.std(ddof=1))
        assert shuffled == pytest.approx(3.788199e-06, rel=5e-7)
        assert shuffled < float(result.returns.declared.std(ddof=1)) / 7

    def test_shuffled_entry_days_cancel_into_a_steady_net_long_position(
        self, strategy, net_positions
    ) -> None:
        """The net position of the first 500 shuffles on seed 20261011, against the real rule's.

        Draw d here is the d-th ``default_rng(20261011).permutation(2_000)``
        call, the same permutation the corrected third test applies as its
        draw d, read on this file's vintage. Over those 500 draws the
        shuffled net position averages 9.975403 units in absolute size and is
        long on 0.983958 of days. The real rule averages 20.58 and is long on
        0.638 of its 2,000 days, both exact since positions are whole units.
        Each shuffle's average position sits within one percent of the
        average across shuffles, which is what "about the same size on every
        shuffle" means. 500 draws keep the test to about two seconds.
        """
        held = strategy["held"]
        assert float(np.abs(held).mean()) == pytest.approx(20.58, rel=5e-7)
        assert float((held > 0).mean()) == pytest.approx(0.638, rel=5e-7)

        shuffled = net_positions
        assert len(shuffled) == NET_POSITION_DRAWS
        assert float(np.abs(shuffled).mean()) == pytest.approx(9.975403, rel=5e-7)
        assert float((shuffled > 0).mean()) == pytest.approx(0.983958, rel=5e-7)
        per_shuffle = shuffled.mean(axis=1)
        assert float(per_shuffle.std(ddof=1)) < 0.01 * float(per_shuffle.mean())


class TestRow5TheAsWrittenTrades:
    """L99 and L100 add the shuffled tranches to ``pos``, so ``pos_sim`` stays zero."""

    def test_ret_sim_is_zero_on_every_draw(self, result) -> None:
        written = result.as_written
        assert len(written.means) == AS_WRITTEN_DRAWS
        assert written.largest_return == 0.0
        assert (written.means == 0).all()
        assert result.count(written.means) == 0

    def test_the_tranches_land_in_pos(self, strategy, result) -> None:
        added = result.as_written.positions_after - strategy["held"]
        assert np.abs(added).max() > 0
        rng = np.random.default_rng(TRADES_SEED)
        expected = sum(
            positions(strategy["longs"][order], strategy["shorts"][order], HOLD_DAYS)
            for order in (rng.permutation(2_000) for _ in range(AS_WRITTEN_DRAWS))
        )
        np.testing.assert_array_equal(added, expected)


class TestTheRowsBesideAddedAfterTheScratchRun:
    """Three rows the issue added after a scratch run on other seeds had seen results."""

    def test_the_observed_positions_on_the_simulated_returns(self, result) -> None:
        count = result.count(result.returns.observed_positions)
        assert count == 277
        assert count / RETURNS_DRAWS == pytest.approx(0.027700, abs=5e-7)
        low, high = SCRIPT_RETURNS_BAND
        assert low <= count <= high

    def test_a_normal_draw_with_tu_s_mean_and_std(self, result) -> None:
        count = result.count(result.returns.normal)
        assert count == 1165
        assert count / RETURNS_DRAWS == pytest.approx(0.116500, abs=5e-7)
        low, high = BOOK_RETURNS_BAND
        assert low <= count <= high

    def test_type_iv_with_the_mean_set_to_zero(self, result) -> None:
        count = result.count(result.returns.mean_zero)
        assert count == 19
        assert count / RETURNS_DRAWS == pytest.approx(0.001900, abs=5e-7)

    def test_the_drift_is_what_the_strategy_earns_on_simulated_returns(self, result) -> None:
        """The average simulated mean falls from row 2's 3.2e-05 to 3.6e-07 when the drift goes."""
        found = result.returns
        assert float(found.declared.mean()) == pytest.approx(3.220302e-05, rel=5e-7)
        assert float(found.mean_zero.mean()) == pytest.approx(3.604899e-07, rel=5e-7)
        assert float(found.observed_positions.mean()) == pytest.approx(2.394932e-05, rel=5e-7)

    def test_the_spreads_of_the_normal_and_mean_zero_means(self, result) -> None:
        """The n − 1 ``std`` of each row's 10,000 means on seed 20261010's uniforms.

        The normal row's spread sits near row 2's 2.819219e-05, and the
        mean-zero row's near the Gaussian null's 2.259145e-05.
        """
        found = result.returns
        assert float(found.normal.std(ddof=1)) == pytest.approx(2.806502e-05, rel=5e-7)
        assert float(found.mean_zero.std(ddof=1)) == pytest.approx(2.127120e-05, rel=5e-7)

    def test_a_drifting_series_is_long_on_most_signal_days(self, long_shares) -> None:
        """Why the drift pays: the rule goes long on most signal days of a drifting series."""
        assert long_shares == pytest.approx((0.804654, 0.502401), abs=5e-7)


class TestTheReport:
    def test_it_prints_the_five_rows_with_their_verdicts(self, printed) -> None:
        for label, figures in (
            ("1 Gaussian", ["2.933253", "2.93", "reproduced"]),
            ("2 Randomized returns, count", ["1221", "1166", "1102", "1230", "reproduced"]),
            ("3 Randomized returns, p-value", ["0.122100", "0.027500", "did", "not"]),
            ("4 Randomized trades, corrected", ["0", "reproduced"]),
            ("5 Randomized trades, as written", ["0", "none,", "finding:"]),
        ):
            row = next(r for r in printed.splitlines() if r.strip().startswith(label))
            assert all(f in row.split() for f in figures), row
        row_3 = next(r for r in printed.splitlines() if r.strip().startswith("3 Randomized"))
        assert "gap +0.0946" in row_3

    def test_it_prints_the_rows_beside_and_says_when_they_were_added(self, printed) -> None:
        assert "added after the scratch run saw results" in printed
        assert "277 of 10000, 0.027700, inside" in printed
        assert "1165 of 10000, 0.116500" in printed
        assert "19 of 10000, 0.001900" in printed
        assert "inputdataohlcdaily_20120511/tu.csv" in printed
        assert "Exploratory." in printed
        assert "Entry 37" in printed

    def test_rows_1_and_4_say_when_their_figures_miss(self, sources, result) -> None:
        """On the declared seeds both rows reproduce, and row 4's count equals row 5's.

        So the real printout cannot tell a verdict that reads its own figure
        from one that is always "reproduced" or reads row 5's count. This
        report gets a statistic of 3.5, which misses the script's 2.93, and
        three trade means above the observed mean.
        """
        trades = result.trades.copy()
        trades[:3] = 2 * result.observed_mean
        missed = dataclasses.replace(result, statistic=3.5, trades=trades)
        out = io.StringIO()
        with redirect_stdout(out):
            report(sources[0], missed)
        lines = out.getvalue().splitlines()
        row_1 = next(r for r in lines if r.strip().startswith("1 Gaussian"))
        assert "did not reproduce, gap +0.57" in row_1, row_1
        row_4 = next(r for r in lines if r.strip().startswith("4 Randomized trades"))
        assert row_4.split()[6:11] == ["3", "0", "0", "to", "0"], row_4
        assert row_4.endswith("did not reproduce, gap +3"), row_4

    def test_it_prints_the_normal_tail_and_the_pooled_std(self, printed) -> None:
        lines = printed.splitlines()
        tail = next(r for r in lines if "one-sided normal tail" in r)
        assert "is 0.001677." in tail, tail
        pooled = next(r for r in lines if "pooled mean" in r)
        assert "a std of 1.095392e-03, against" in pooled, pooled

    def test_each_row_beside_prints_its_own_count_and_side_of_the_band(self, printed) -> None:
        """1,165 lies above the script's 243 to 307 and 19 below it, so both are outside."""
        lines = printed.splitlines()
        for label, figures in (
            ("a normal draw with TU's mean and std", "1165 of 10000, 0.116500, outside"),
            ("Pearson type IV with the mean set to zero", "19 of 10000, 0.001900, outside"),
        ):
            row = next(r for r in lines if label in r)
            assert figures in row, row

    def test_main_turns_a_guard_refusal_into_one_line(self, monkeypatch, no_arguments) -> None:
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("inputdataohlcdaily_20120511/tu.csv changes scale")

        monkeypatch.setattr(tu_momentum, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(SystemExit, match="tu.csv changes scale"):
            main()

    def test_main_turns_a_missing_vintage_into_one_line(
        self, monkeypatch, tmp_path, no_arguments
    ) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit, match="inputDataOHLCDaily_20120511.mat"):
            main()


POST = paths.REPO_ROOT / "blog" / "tu-hypothesis-tests-lessons.md"

#: The counts the post spells out in words.
SPELLED = {4: "four", 7: "seven", 9: "nine"}


def _times_ten(value: float) -> str:
    """``value`` at six decimals in the post's LaTeX, as in ``6.626644\\times10^{-5}``."""
    mantissa, exponent = f"{value:.6e}".split("e")
    return rf"{mantissa}\times10^{{{int(exponent)}}}"


class TestWhatThePostQuotes:
    """Each run figure ``blog/tu-hypothesis-tests-lessons.md`` quotes, read there against the run.

    The classes above pin each figure once, and the post copies it by hand.
    Here each figure is built from the run at the precision the post prints
    it, and looked for in the post inside a fragment holding the number and
    the words that place it. A typo in that copy, or a re-pin that leaves the
    post behind, fails here. Lesson 1's two worked equations are rebuilt line
    by line in the post's LaTeX.

    Chan's printed figures are read through the module constants that hold
    them, so the book's 1,166 and the 0.1166 it divides to, the script's
    0.027500, and its 2.93 move with those constants. The comparisons the
    post's words draw are asserted on the run where each is one line, such as
    a count inside or outside its band, nine counts below the top, the
    sampler within four standard errors of its targets, κ between 0 and 1,
    and every as-written return being zero.

    One copy of each figure is read, the one in the passage that explains
    it, because the post states most figures more than once and a fragment
    per copy costs more than the copies are worth. Every other copy can carry
    a typo that passes. Those copies sit in the subtitle, the opening's
    list of findings, the closing list of habits, the section on what the
    replication cannot say and the figure's alt text, none of which is read
    here. A restatement inside a lesson, such as Lesson 4's second 1,274 and
    474, is read only where it shares a fragment with a figure the passage
    explains. The figure's own labels are read by
    ``tests/test_tu_hypothesis_tests_figures.py``.

    Also unread are Chan's words and the Kindle locations, the book's chapter
    and example numbers, location 2923's 12 percent, TU's two-year term, the
    first section's eight years, the replication log's entry number, the
    post's counts of its own results, lessons, tests,
    assumptions, moments and questions, the normal distribution's kurtosis of
    3, the two standard errors of the band rule and its 95 percent, the rule
    of three's 3/N and its 95 percent, the 2004 to 2012 of the exploratory
    note, the other post's 480 stocks, and the references.
    """

    @pytest.fixture(scope="class")
    @classmethod
    def text(cls) -> str:
        return POST.read_text(encoding="utf-8")

    @staticmethod
    def missing(text: str, fragments: list[str]) -> list[str]:
        return [fragment for fragment in fragments if fragment not in text]

    def test_the_rule_the_file_and_the_three_tests(self, sources, strategy, result, text):
        entry, closes = sources
        longs, shorts = int(strategy["longs"].sum()), int(strategy["shorts"].sum())
        first_entry = int(np.flatnonzero(strategy["longs"] | strategy["shorts"])[0])
        assert first_entry == LOOKBACK
        periods = len(tu_momentum.PERIODS)
        fragments = [
            f"The code counts 12 months as {LOOKBACK} trading days and a month as {HOLD_DAYS}. "
            f"From the {first_entry + 1}st day on,",
            f"holds it {HOLD_DAYS} days, so up to {HOLD_DAYS} trades are open at once.",
            f"times today’s return on TU, divided by {HOLD_DAYS}.",
            f"Chan’s own MATLAB file `{SOURCE_FILE}`, saved on {entry.obtained}, holds TU’s "
            f"closes for {len(closes):,} trading days from {closes.index[0].date()} to "
            f"{closes.index[-1].date()}. The rule’s **observed mean**, its average daily return "
            f"over those days, is {result.observed_mean:.6e}.",
            f"{SPELLED[periods]} lookbacks against {SPELLED[periods]} holds, "
            f"{periods * periods} pairs in all.",
            f"The script draws {len(closes):,} daily returns for TU",
            f"It repeats this {RETURNS_DRAWS:,} times.",
            f"which keeps the rule’s {longs:,} long entry days and {shorts} short entry days "
            f"and never makes a day both long and short. It repeats this {TRADES_DRAWS:,} times.",
        ]
        assert not (strategy["longs"] & strategy["shorts"]).any()
        assert self.missing(text, fragments) == []

    def test_chan_s_printed_figures(self, text) -> None:
        book = int(BOOK_RANDOMIZED_RETURNS_COUNT)
        fragments = [
            f"finds chance matching the strategy in {book:,} of {BOOK_RETURNS_DRAWS:,} tries. "
            f"Another finds it in none of {BOOK_TRADES_DRAWS:,}.",
            f"so his p-value is {book:,} / {BOOK_RETURNS_DRAWS:,}, or "
            f"{book / BOOK_RETURNS_DRAWS:.4f}.",
            f"**The Gaussian test lands the script’s {SCRIPT_GAUSSIAN_STATISTIC}.**",
        ]
        assert int(BOOK_RANDOMIZED_TRADES_COUNT) == 0, "the post spells the book's 0 as none"
        assert self.missing(text, fragments) == []

    def test_the_moments_and_the_pearson_type(self, moments, strategy, text) -> None:
        kappa = pearson_kappa(moments.skewness, moments.kurtosis)
        assert 0 < kappa < 1
        market = strategy["market"]
        assert market[0] == 0
        fragments = [
            f"of the {len(market):,} daily returns the script computes for TU. The first of those "
            f"returns is {market[0]:g}, because day one has no close before it.",
            f"A normal distribution’s kurtosis is 3, and TU’s is {moments.kurtosis:.6f}. So the "
            f"null keeps TU’s **drift**, its average daily return of {moments.mean:.6e},",
            f"TU’s κ is {kappa:.6f}, between 0 and 1, which puts it in type IV.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_1_the_gaussian_test(self, result, text) -> None:
        n = len(result.daily)
        s = float(result.daily.std(ddof=1))
        spread = s / math.sqrt(n)
        tail = float(ndtr(-result.statistic))
        assert matches(result.statistic, SCRIPT_GAUSSIAN_STATISTIC)
        fragments = [
            f"The script’s comment prints {SCRIPT_GAUSSIAN_STATISTIC} for the Gaussian "
            f"statistic. The run here gives {result.statistic:.6f}, which rounds to it.",
            rf"&= \frac{{{_times_ten(result.observed_mean)}}}{{{_times_ten(s)}}}\,"
            rf"\sqrt{{{n}}} \\" + f"\n&= {result.statistic:.6f}\n",
            rf"&= \frac{{{_times_ten(s)}}}{{\sqrt{{{n}}}}} \\" + f"\n&= {_times_ten(spread)}\n",
            f"The chance of a mean at or above {result.observed_mean:.6e} is the one-sided tail "
            f"beyond {result.statistic:.6f} standard errors, {tail:.6f}.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_2_the_bands_and_the_second_test(self, moments, result, text) -> None:
        book = int(BOOK_RANDOMIZED_RETURNS_COUNT)
        script = float(SCRIPT_RANDOMIZED_RETURNS_P_VALUE)
        book_p = book / BOOK_RETURNS_DRAWS
        book_se = math.sqrt(RETURNS_DRAWS * book_p * (1 - book_p))
        script_se = math.sqrt(RETURNS_DRAWS * script * (1 - script))
        trades_p = int(BOOK_RANDOMIZED_TRADES_COUNT) / BOOK_TRADES_DRAWS
        trades_se = math.sqrt(TRADES_DRAWS * trades_p * (1 - trades_p))
        (book_low, book_high), (script_low, script_high) = BOOK_RETURNS_BAND, SCRIPT_RETURNS_BAND
        assert BOOK_TRADES_BAND[0] == BOOK_TRADES_BAND[1]

        count = result.count(result.returns.declared)
        proportion = count / RETURNS_DRAWS
        assert band_verdict(count, BOOK_RETURNS_BAND) == "reproduced"
        assert band_verdict(count, SCRIPT_RETURNS_BAND) == "did not reproduce"

        n = RETURNS_DRAWS * len(result.daily)
        mean_error = moments.std / math.sqrt(n)
        std_error = moments.std * math.sqrt((moments.kurtosis - 1) / (4 * n))
        returns = result.returns
        assert abs(returns.draw_mean - moments.mean) < 4 * mean_error
        assert abs(returns.draw_std - moments.std) < 4 * std_error
        assert n % 1_000_000 == 0
        fragments = [
            f"1. **The book’s {book:,} of {BOOK_RETURNS_DRAWS:,}.** The standard error is "
            f"{book_se:.1f}, so the band runs from {book_low:,} to {book_high:,}.",
            f"2. **The script’s {SCRIPT_RANDOMIZED_RETURNS_P_VALUE}.** At N = {RETURNS_DRAWS:,} "
            f"the standard error is {script_se:.1f}, so the band runs from {script_low} to "
            f"{script_high}.",
            f"3. **The book’s {BOOK_RANDOMIZED_TRADES_COUNT} of {BOOK_TRADES_DRAWS:,}.** A printed "
            f"proportion of {trades_p:g} has a standard error of {trades_se:g}, so only "
            f"{BOOK_TRADES_BAND[0]} lands.",
            f"the seeds, {RETURNS_SEED} for the second test and {TRADES_SEED} for the third,",
            f"**The result.** On seed {RETURNS_SEED} the second test gives {count:,} of "
            f"{RETURNS_DRAWS:,}. That is inside {book_low:,} to {book_high:,}, "
            f"{SPELLED[book_high - count]} counts below the top, so the book’s {book:,} "
            f"**reproduced**, with a gap of {gap(count, BOOK_RANDOMIZED_RETURNS_COUNT):+.0f}. The "
            f"same count, {count:,}, is far outside the script’s {script_low} to {script_high}, "
            f"so the script’s {SCRIPT_RANDOMIZED_RETURNS_P_VALUE} **did not reproduce**. As a "
            f"p-value the count is {proportion:.6f}, a gap of "
            f"{gap(proportion, SCRIPT_RANDOMIZED_RETURNS_P_VALUE):+.6f} from the script’s.",
            f"Over all {n // 1_000_000} million simulated daily returns, the average is "
            f"{returns.draw_mean:.6e} against TU’s mean daily return of {moments.mean:.6e}, and "
            f"the standard deviation is {returns.draw_std:.6e} against TU’s {moments.std:.6e}. "
            f"Both sit within {SPELLED[4]} standard errors of their targets.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_3_the_observed_positions(self, result, text) -> None:
        count = result.count(result.returns.observed_positions)
        low, high = SCRIPT_RETURNS_BAND
        assert low <= count <= high
        fragments = [
            f"That gives {count} of {RETURNS_DRAWS:,}, or {count / RETURNS_DRAWS:.6f}, inside "
            f"the script’s {low} to {high}.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_4_the_third_test(self, strategy, result, net_positions, text) -> None:
        written = result.as_written
        assert (written.means == 0).all() and written.largest_return == 0.0
        trades = result.trades
        count = result.count(trades)
        assert band_verdict(count, BOOK_TRADES_BAND) == "reproduced"
        z = (result.observed_mean - trades.mean()) / trades.std(ddof=1)
        held = strategy["held"]
        fragments = [
            f"The run here executes that loop as written for {AS_WRITTEN_DRAWS} draws, and every "
            "simulated return is zero.",
            "**Corrected.** Building each draw’s positions from its own shuffled entry days gives "
            f"{count} of {TRADES_DRAWS:,} on seed {TRADES_SEED}.",
            f"so here below {3 / TRADES_DRAWS:.0e}.",
            f"The largest shuffled mean is {trades.max():.6e} and their average is "
            f"{trades.mean():.6e}. The observed mean sits {z:.6f} standard deviations of the "
            "shuffled means above that average.",
            f"Over the first {len(net_positions)} of those shuffles the net position averages "
            f"{np.abs(net_positions).mean():.6f} units in absolute size and is long on "
            f"{(net_positions > 0).mean():.6f} of the {len(held):,} days, against "
            f"{np.abs(held).mean():.2f} units and {(held > 0).mean():.3f} for the real rule.",
            f"The shuffled means’ standard deviation is {trades.std(ddof=1):.6e}, against "
            f"{result.returns.declared.std(ddof=1):.6e} for the second test’s means on new "
            "returns.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_5_drift_and_kurtosis(self, moments, result, long_shares, text) -> None:
        returns = result.returns
        normal, mean_zero = result.count(returns.normal), result.count(returns.mean_zero)
        declared = result.count(returns.declared)
        spread = float(result.daily.std(ddof=1)) / math.sqrt(len(result.daily))
        with_drift, without = long_shares
        fragments = [
            f"has no skewness and a kurtosis of 3, against TU’s {moments.kurtosis:.6f}. It gives "
            f"{normal:,} of {RETURNS_DRAWS:,}, against {declared:,} for type IV.",
            f"Type IV with TU’s mean set to zero gives {mean_zero} of {RETURNS_DRAWS:,}, or "
            f"{mean_zero / RETURNS_DRAWS:.6f}, close to the Gaussian test’s one-sided "
            f"{float(ndtr(-result.statistic)):.6f}. The average simulated mean falls from "
            f"{returns.declared.mean():.6e} to {returns.mean_zero.mean():.6e}.",
            f"Those {RETURNS_DRAWS:,} means spread with a standard deviation of "
            f"{returns.mean_zero.std(ddof=1):.6e}, close to the Gaussian null’s standard error of "
            f"{spread:.6e}",
            f"from {returns.mean_zero.std(ddof=1):.6e} to {returns.declared.std(ddof=1):.6e}.",
            f"On the first {LONG_SHARE_DRAWS:,} simulated series, long entry days make up on "
            f"average {with_drift:.6f} of all entry days, and {without:.6f} once the mean is "
            "removed.",
            f"TU did drift upward, at a mean daily return of {moments.mean:.6e}.",
        ]
        assert self.missing(text, fragments) == []
