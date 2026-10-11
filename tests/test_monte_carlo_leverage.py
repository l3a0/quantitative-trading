"""The pins for the Monte Carlo leverage, historical optimization and CPPI of Boxes 8.1 to 8.6.

This file is the single authority for every number a prose surface quotes
about *Algorithmic Trading*'s Chapter 8 leverage boxes and the rows beside
them. ``docs/replication-log.md`` Entry 40 carries the verdicts and points here
row by row.

Every pin reads one vintage and one specification, so both are stated once
here.

- **Vintage.** ``pythoncodesanddata/AUDCAD_unequal_ret.csv``, vendor
  ``chan-py``, symbol ``AUDCAD-UNEQUAL``, basis ``return``, saved 2018-12-26,
  the 612 test-set returns Example 5.1's ``AUDCAD_unequal.m`` saved, read
  through ``chan.series.load_returns``. Its identity is its row of
  ``PYTHON_PORT`` in ``tests/support/committed_vintages.py``.
- **Specification.** ``monteCarloOptimLeverage.m`` at EpchanPreview
  ``e4bc46f``, git blob ``fc32599``, as :mod:`chan.monte_carlo_leverage`
  transcribes it, under the declaration
  [issue 360](https://github.com/l3a0/quantitative-trading/issues/360) wrote
  before any draw on its seeds. The moments are the mean, the n − 1 ``std`` and
  the biased skewness and kurtosis. Seed s's draws are
  ``pearson_iv_draws(params, default_rng(s).random(100_000))`` through the type
  IV inverse CDF on a θ grid of 20,001 points. The growth rate is
  ``mean(log1p(f·R))``, its optimum is Brent's bounded search with
  ``xatol=1e-10`` over ``(0, min(20, ruin))`` for the capped optimum and
  ``(0, ruin)`` for the uncapped one, and every drawdown is ``calculateMaxDD``
  on ``cumprod(1 + a) − 1``. D is 0.5, and every leverage on the draws is a
  multiple of the capped optimum on the same draws. The declared seed is
  20261012 and the ensemble is the 200 seeds 20261013 to 20261212. A simulated
  figure lands inside the ensemble's 5th to 95th percentile.

A seeded figure is pinned at six decimals, or six significant figures where it
is smaller than 0.01, so a change to the draw method cannot move it inside the
book's rounding unnoticed. An optimum is pinned at 1e-6, because the search
stops within about 3e-7 of the true optimum at a leverage of 20, and the
uncapped ones are also held to the root of the growth rate's derivative.

Exploratory. Reproducing Chan's figures spends his 612 returns on a method he
chose. The boxes first ran on the declared seeds on 2026-10-10.
"""

from __future__ import annotations

import io
import math
from contextlib import redirect_stdout

import numpy as np
import pytest
from scipy import integrate, optimize

from chan import monte_carlo_leverage as module
from chan.aud_cad_johansen import SCRIPT_KELLY
from chan.khandani_lo_book_two import matches
from chan.monte_carlo_leverage import (
    BAND,
    BOOK_CPPI_GROWTH,
    BOOK_DRAWDOWN_HALF,
    BOOK_DRAWDOWN_OPTIMUM,
    BOOK_DRAWDOWN_SEVENTH,
    BOOK_FULL_DRAWDOWN,
    BOOK_FULL_GROWTH,
    BOOK_HISTORICAL,
    BOOK_KELLY,
    BOOK_MINIMUM,
    BOOK_OPTIMUM,
    BOOK_OPTIMUM_FMINBND,
    BOOK_RUIN,
    BOOK_SEVENTH_LEVERAGE,
    BOOK_TYPE,
    CAP,
    DRAWS,
    ENSEMBLE_SEEDS,
    EQUAL_WITHIN,
    SEED,
    SIMILAR_WITHIN,
    XATOL,
    Band,
    D,
    MonteCarloLeverage,
    cppi_as_described,
    cppi_as_described_loop,
    cppi_as_scripted,
    cppi_as_scripted_loop,
    draws,
    growth,
    implied_kelly,
    implied_kelly_band,
    lands_in_exact_distribution,
    lower_tail,
    max_drawdown,
    minimum_below,
    optimal_leverage,
    read_returns,
    rounding_band,
    rows,
    ruin_leverage,
    shifted_landings,
    shifted_parameters,
    simulated_verdict,
)
from chan.tu_hypothesis_tests import GRID_POINTS, pearson_iv_draws, script_moments
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import PYTHON_PORT
from tests.support.pearson_iv import closed_form_moments


@pytest.fixture(scope="module")
def saved():
    return read_returns()


@pytest.fixture(scope="module")
def returns(saved):
    return saved[1]


@pytest.fixture(scope="module")
def ran() -> tuple[MonteCarloLeverage, str]:
    """``run`` on the declared seed and both ensembles, with what it prints."""
    out = io.StringIO()
    with redirect_stdout(out):
        result = module.run()
    return result, out.getvalue()


@pytest.fixture(scope="module")
def result(ran) -> MonteCarloLeverage:
    return ran[0]


@pytest.fixture(scope="module")
def printed(ran) -> str:
    return ran[1]


@pytest.fixture(scope="module")
def verdicts(result) -> dict[tuple[str, str], str]:
    """Each row's verdict, keyed by its number and its published figure."""
    return {(row.number, row.published): row.verdict for row in rows(result)}


@pytest.fixture(scope="module")
def declared_draws(result):
    return draws(result.params, SEED)


@pytest.fixture
def no_arguments(monkeypatch):
    """``main`` parses ``sys.argv``, which under pytest holds pytest's own arguments."""
    monkeypatch.setattr("sys.argv", ["chan.monte_carlo_leverage"])


def _derivative_root(values: np.ndarray) -> float:
    """Where ``mean(R / (1 + f·R))``, the growth rate's derivative, is zero, to 1e-14."""
    return optimize.brentq(
        lambda f: float(np.mean(values / (1 + f * values))),
        1.0,
        ruin_leverage(values) - 1e-9,
        xtol=1e-14,
    )


class TestTheDeclaration:
    def test_the_seeds_and_the_sizes_are_the_issue_s(self) -> None:
        assert SEED == 20261012
        assert len(ENSEMBLE_SEEDS) == 200
        assert (ENSEMBLE_SEEDS[0], ENSEMBLE_SEEDS[-1]) == (20261013, 20261212)
        assert SEED not in ENSEMBLE_SEEDS
        assert (DRAWS, CAP, D, XATOL) == (100_000, 20.0, 0.5, 1e-10)

    def test_the_criteria(self) -> None:
        assert BAND == (5.0, 95.0)
        assert (EQUAL_WITHIN, SIMILAR_WITHIN) == (0.01, 0.02)

    def test_the_printed_figures(self) -> None:
        assert (BOOK_KELLY, BOOK_TYPE, BOOK_OPTIMUM_FMINBND, BOOK_MINIMUM, BOOK_RUIN) == (
            "18.4",
            4,
            "19",
            "-0.0331",
            "30.2",
        )
        assert BOOK_HISTORICAL == "18.4"
        assert (
            BOOK_OPTIMUM,
            BOOK_DRAWDOWN_OPTIMUM,
            BOOK_DRAWDOWN_HALF,
            BOOK_DRAWDOWN_SEVENTH,
            BOOK_SEVENTH_LEVERAGE,
        ) == ("19.2", "-0.999", "-0.963", "-0.5", "2.7")
        assert (BOOK_CPPI_GROWTH, BOOK_FULL_GROWTH, BOOK_FULL_DRAWDOWN) == (
            "0.002484",
            "0.002525",
            "-0.9",
        )

    def test_the_book_s_ruin_leverage_is_one_over_its_minimum(self) -> None:
        assert 1 / -float(BOOK_MINIMUM) == pytest.approx(30.21, abs=5e-3)
        assert matches(1 / -float(BOOK_MINIMUM), BOOK_RUIN)

    def test_the_draw_method_is_pinned(self, declared_draws) -> None:
        """The seed means these draws only under this method, so the first three are pinned."""
        assert GRID_POINTS == 20_001
        np.testing.assert_allclose(
            declared_draws[:3],
            [0.0012333806877945636, -0.0005516092461756489, 0.005235601065326979],
            rtol=1e-9,
        )

    def test_a_verdict_names_the_seed_only_inside_the_band(self) -> None:
        assert simulated_verdict(-0.991, "-0.999", True) == "reproduced with a gap, the seed"
        assert simulated_verdict(-0.871, "-0.9", True) == "reproduced"
        assert simulated_verdict(-0.871, "-0.963", False) == "did not reproduce"

    def test_a_band_includes_both_ends(self) -> None:
        found = Band(1.0, 2.0, 3.0)
        assert found.holds(1.0) and found.holds(3.0)
        assert not found.holds(0.999) and not found.holds(3.001)
        assert lands_in_exact_distribution(0.05) and lands_in_exact_distribution(0.95)
        assert not lands_in_exact_distribution(0.049) and not lands_in_exact_distribution(0.951)

    def test_the_bands_are_numpy_s_linear_percentiles(self, result) -> None:
        values = result.ensemble.values("uncapped")
        found = result.ensemble.band("uncapped")
        assert (found.low, found.median, found.high) == tuple(
            np.percentile(values, [5, 50, 95]).tolist()
        )


class TestTheVintage:
    def test_the_saved_returns_are_their_pinned_source(self, saved) -> None:
        entry, values = saved
        vendor, symbol, basis, saved_date, _, _ = PYTHON_PORT[entry.path]
        assert entry.path == "pythoncodesanddata/AUDCAD_unequal_ret.csv"
        assert (entry.vendor, entry.symbol, entry.price_basis, entry.obtained) == (
            vendor,
            symbol,
            basis,
            saved_date,
        )
        assert (vendor, symbol, basis, saved_date) == (
            "chan-py",
            "AUDCAD-UNEQUAL",
            "return",
            "2018-12-26",
        )
        assert len(values) == 612

    def test_the_run_reads_the_same_returns(self, result, returns) -> None:
        np.testing.assert_array_equal(result.returns, returns)
        assert result.entry == read_returns()[0]

    def test_main_turns_a_missing_vintage_into_one_line(self, monkeypatch, no_arguments) -> None:
        def missing(data_dir=None):
            raise VintageUnavailable("AUDCAD_unequal_ret.csv is not committed")

        monkeypatch.setattr(module, "read_returns", missing)
        with pytest.raises(SystemExit, match="AUDCAD_unequal_ret.csv is not committed"):
            module.main()


class TestTheSampler:
    def test_the_script_s_moments(self, result, returns) -> None:
        """MATLAB's n − 1 ``std``, and biased skewness and kurtosis not in excess form."""
        assert result.moments == script_moments(returns)
        assert result.moments.mean == pytest.approx(4.318452e-04, rel=5e-7)
        assert result.moments.std == pytest.approx(4.255615e-03, rel=5e-7)
        assert result.moments.skewness == pytest.approx(0.582712, abs=5e-7)
        assert result.moments.kurtosis == pytest.approx(7.821679, abs=5e-7)

    def test_the_parameters(self, result) -> None:
        p = result.params
        assert p.m == pytest.approx(3.254731, abs=5e-7)
        assert p.nu == pytest.approx(-0.897242, abs=5e-7)
        assert p.a == pytest.approx(7.819013e-03, rel=5e-7)
        assert p.lam == pytest.approx(-1.123894e-03, rel=5e-7)

    def test_moments_exist_only_below_order_5_51(self, result) -> None:
        """Type IV's moment of order n exists for n < 2m − 1, so skewness's variance does not."""
        assert 2 * result.params.m - 1 == pytest.approx(5.509462, abs=5e-7)
        assert 4 < 2 * result.params.m - 1 < 6

    def test_the_closed_form_moments_are_the_targets(self, result) -> None:
        p, m = result.params, result.moments
        found = closed_form_moments(p.m, p.nu, p.a, p.lam)
        np.testing.assert_allclose(found, (m.mean, m.std, m.skewness, m.kurtosis), rtol=1e-9)

    @pytest.mark.parametrize("where", ["book", 5, 10])
    def test_the_grid_s_tail_mass_matches_quadrature(self, result, where) -> None:
        """The grid's mass below the book's −0.0331, and below the mean less 5 and 10 std."""
        p, m = result.params, result.moments
        x = float(BOOK_MINIMUM) if where == "book" else m.mean - where * m.std

        def density(theta: float) -> float:
            return math.cos(theta) ** (2 * p.m - 2) * math.exp(-p.nu * theta)

        whole = integrate.quad(density, -math.pi / 2, math.pi / 2, limit=200)[0]
        upper = math.atan((x - p.lam) / p.a)
        exact = integrate.quad(density, -math.pi / 2, upper, limit=200)[0] / whole
        grid = optimize.brentq(
            lambda u: float(pearson_iv_draws(p, np.array([u]))[0]) - x, 1e-15, 0.5, xtol=1e-18
        )
        assert grid == pytest.approx(exact, rel=1e-3)
        assert lower_tail(p, x) == pytest.approx(exact, rel=1e-12)

    def test_the_declared_draws_have_the_target_mean_and_std(self, result, declared_draws) -> None:
        """Within four standard errors. The std's needs the fourth moment, which exists here."""
        m, n = result.moments, DRAWS
        assert abs(declared_draws.mean() - m.mean) < 4 * m.std / math.sqrt(n)
        se_std = m.std * math.sqrt((m.kurtosis - 1) / (4 * n))
        assert abs(declared_draws.std(ddof=1) - m.std) < 4 * se_std
        assert declared_draws.mean() == pytest.approx(4.180685e-04, rel=5e-7)
        assert declared_draws.std(ddof=1) == pytest.approx(4.280224e-03, rel=5e-7)

    def test_the_mean_moves_only_lambda(self, result) -> None:
        """Why row group 13 can shift the draws' mean without a second inversion."""
        shifted = result.shifted_params
        p = result.params
        assert (shifted.m, shifted.nu, shifted.a) == (p.m, p.nu, p.a)
        target = float(BOOK_KELLY) * result.moments.std**2
        assert shifted.lam - p.lam == pytest.approx(target - result.moments.mean, rel=1e-9)
        assert shifted == shifted_parameters(result.moments)


class TestRows1And2:
    def test_row_1_the_kelly_is_the_script_s(self, result, verdicts) -> None:
        assert result.kelly == pytest.approx(23.845328, abs=5e-7)
        assert matches(result.kelly, SCRIPT_KELLY)
        assert verdicts[("1", BOOK_KELLY)] == "did not reproduce, gap +5.4"

    def test_row_2_kappa_puts_the_moments_in_type_iv(self, result, verdicts) -> None:
        b1, b2 = result.moments.skewness**2, result.moments.kurtosis
        kappa = b1 * (b2 + 3) ** 2 / (4 * (4 * b2 - 3 * b1) * (2 * b2 - 3 * b1 - 6))
        assert result.kappa == pytest.approx(kappa, rel=1e-12)
        assert result.kappa == pytest.approx(0.038081, abs=5e-7)
        assert verdicts[("2", str(BOOK_TYPE))] == "reproduced"


class TestRows3And4TheSimulatedOptimum:
    def test_the_declared_seed_sits_on_the_cap(self, result) -> None:
        seeded = result.declared
        assert seeded.optimum == pytest.approx(20.0, abs=1e-6)
        assert seeded.optimum < CAP
        assert seeded.on_the_cap

    def test_the_declared_seed_s_uncapped_optimum(self, result, declared_draws) -> None:
        root = _derivative_root(declared_draws)
        assert root == pytest.approx(22.295382, abs=5e-7)
        assert result.declared.uncapped == pytest.approx(root, abs=1e-6)

    def test_the_uncapped_band(self, result) -> None:
        found = result.ensemble.band("uncapped")
        assert found.low == pytest.approx(16.622019, abs=1e-6)
        assert found.median == pytest.approx(23.319117, abs=1e-6)
        assert found.high == pytest.approx(24.865122, abs=1e-6)

    def test_158_of_200_seeds_sit_on_the_cap(self, result) -> None:
        assert sum(run.on_the_cap for run in result.ensemble.runs) == 158
        capped = result.ensemble.values("optimum")
        assert np.all(capped < CAP)
        assert np.count_nonzero(capped > CAP - 1e-6) == 158

    def test_row_3_both_figures_land_and_the_seed_explains_the_gap(self, verdicts) -> None:
        assert verdicts[("3", BOOK_OPTIMUM_FMINBND)] == "reproduced with a gap, the seed"
        assert verdicts[("3", BOOK_OPTIMUM)] == "reproduced with a gap, the seed"

    def test_the_capped_band_would_reach_the_book_only_through_clamped_seeds(self, result) -> None:
        """Why row 3 reads the uncapped band: below 19.2 every capped optimum was cut by ruin."""
        ens = result.ensemble
        capped, ruin = ens.values("optimum"), ens.values("ruin")
        below = capped < float(BOOK_OPTIMUM)
        assert np.all(ruin[below] < CAP)

    def test_row_4_the_kelly_lies_inside_the_uncapped_band(self, result, verdicts) -> None:
        assert result.ensemble.band("uncapped").holds(result.kelly)
        assert verdicts[("4", "a claim")] == "reproduced"


class TestRow5TheMinimumAndTheRuinLeverage:
    def test_the_declared_seed_s_minimum_and_ruin_leverage(self, result, declared_draws) -> None:
        assert result.declared.minimum == pytest.approx(-0.043071, abs=5e-7)
        assert result.declared.ruin == pytest.approx(23.217362, abs=5e-7)
        assert result.declared.ruin == pytest.approx(-1 / declared_draws.min(), rel=1e-15)

    def test_the_book_s_minimum_in_its_exact_distribution(self, result) -> None:
        """``1 − (1 − F(x))^100000``, the chance the least of 100,000 draws is at or below x."""
        assert lower_tail(result.params, float(BOOK_MINIMUM)) == pytest.approx(
            1.645480e-05, rel=5e-7
        )
        assert result.minimum_at_or_below_book == pytest.approx(0.807083, abs=5e-7)
        assert minimum_below(result.params, -1 / float(BOOK_RUIN)) == pytest.approx(
            0.806406, abs=5e-7
        )

    def test_row_5_lands_and_the_seed_explains_the_gap(self, verdicts) -> None:
        assert verdicts[("5", BOOK_MINIMUM)] == "reproduced with a gap, the seed"
        assert verdicts[("5", BOOK_RUIN)] == "reproduced with a gap, the seed"

    def test_growth_at_the_ruin_leverage_is_refused(self, declared_draws, result) -> None:
        with pytest.raises(ValueError, match="at or above the ruin leverage"):
            growth(result.declared.ruin, declared_draws)
        assert math.isfinite(growth(result.declared.ruin * (1 - 1e-9), declared_draws))

    def test_the_share_of_seeds_ruined_below_the_cap(self, result) -> None:
        """Exactly 0.149180. The ensemble's 42 of 200 is within four binomial standard errors."""
        p = result.ruin_below_cap_exact
        assert p == pytest.approx(0.149180, abs=5e-7)
        count = sum(run.ruin_below_cap for run in result.ensemble.runs)
        assert count == 42
        assert abs(count - 200 * p) < 4 * math.sqrt(200 * p * (1 - p))


class TestRows6And7TheHistoricalOptimum:
    def test_row_6_the_historical_optimum(self, result, returns, verdicts) -> None:
        root = _derivative_root(returns)
        assert root == pytest.approx(23.721773, abs=5e-7)
        assert result.historical == pytest.approx(root, abs=1e-6)
        assert verdicts[("6", BOOK_HISTORICAL)] == "did not reproduce, gap +5.3"

    def test_capped_at_20_it_returns_the_cap(self, result) -> None:
        assert result.historical_capped == pytest.approx(CAP, abs=1e-6)

    def test_row_7_the_historical_optimum_is_within_1_percent_of_the_kelly(
        self, result, verdicts
    ) -> None:
        assert result.historical / result.kelly - 1 == pytest.approx(-0.005182, abs=5e-7)
        assert verdicts[("7", "a claim")] == "reproduced"


class TestRows8To10TheDrawdowns:
    @pytest.mark.parametrize(
        ("name", "seeded", "low", "high"),
        [
            ("drawdown_optimum", -0.991276, -0.999256, -0.979930),
            ("drawdown_half", -0.871216, -0.922292, -0.763269),
            ("drawdown_seventh", -0.416419, -0.468433, -0.302281),
        ],
    )
    def test_seeded_and_banded(self, result, name, seeded, low, high) -> None:
        assert getattr(result.declared, name) == pytest.approx(seeded, abs=5e-7)
        found = result.ensemble.band(name)
        assert (found.low, found.high) == pytest.approx((low, high), abs=5e-7)

    def test_row_8_lands_and_the_seed_explains_the_gap(self, verdicts) -> None:
        assert verdicts[("8", BOOK_DRAWDOWN_OPTIMUM)] == "reproduced with a gap, the seed"

    def test_row_9_falls_outside_its_band(self, verdicts) -> None:
        assert verdicts[("9", BOOK_DRAWDOWN_HALF)] == "did not reproduce"

    def test_row_10_falls_outside_its_band(self, result, verdicts) -> None:
        assert verdicts[("10", BOOK_DRAWDOWN_SEVENTH)] == "did not reproduce"
        assert result.declared.optimum / 7 == pytest.approx(2.857143, abs=5e-7)

    def test_the_drawdowns_go_through_calculate_max_dd(self, result, declared_draws) -> None:
        f = result.declared.optimum
        assert result.declared.drawdown_half == max_drawdown(f / 2 * declared_draws)


class TestRow11TheGrowthRates:
    def test_seeded_and_banded(self, result) -> None:
        seeded, ens = result.declared, result.ensemble
        assert seeded.cppi_growth == pytest.approx(3.223851e-03, rel=5e-7)
        assert seeded.full_growth == pytest.approx(3.271182e-03, rel=5e-7)
        cppi, full = ens.band("cppi_growth"), ens.band("full_growth")
        assert (cppi.low, cppi.high) == pytest.approx((2.912517e-03, 3.576541e-03), rel=5e-7)
        assert (full.low, full.high) == pytest.approx((2.955473e-03, 3.623032e-03), rel=5e-7)

    def test_both_figures_fall_below_their_bands(self, verdicts) -> None:
        assert verdicts[("11", BOOK_CPPI_GROWTH)] == "did not reproduce"
        assert verdicts[("11", BOOK_FULL_GROWTH)] == "did not reproduce"

    def test_the_claim_holds_on_the_declared_seed_and_every_seed(self, result, verdicts) -> None:
        assert result.declared.growth_gap == pytest.approx(0.014469, abs=5e-7)
        assert verdicts[("11", "a claim")] == "reproduced"
        assert all(run.growth_gap < SIMILAR_WITHIN for run in result.ensemble.runs)

    def test_the_book_s_own_two_figures_differ_by_1_6_percent(self) -> None:
        book = 1 - float(BOOK_CPPI_GROWTH) / float(BOOK_FULL_GROWTH)
        assert book == pytest.approx(0.016238, abs=5e-7)

    def test_the_full_account_s_growth_is_the_script_s_minus_g_at_f_d(
        self, result, declared_draws
    ) -> None:
        f = result.declared.optimum
        assert result.declared.full_growth == pytest.approx(
            growth(f * D, declared_draws), rel=1e-14
        )


class TestRow12TheDrawdownCppiCaps:
    def test_the_full_account_lands_and_rounds_to_the_book(self, result, verdicts) -> None:
        assert result.declared.full_drawdown == pytest.approx(-0.871216, abs=5e-7)
        assert verdicts[("12", BOOK_FULL_DRAWDOWN)] == "reproduced"

    def test_at_d_one_half_row_12_s_full_account_is_row_9(self, result) -> None:
        """f·D is f / 2, so the book's −0.963 and its "painful 0.9" are one quantity."""
        for run in (result.declared, *result.ensemble.runs):
            assert run.full_drawdown == run.drawdown_half

    def test_cppi_as_scripted_breaks_the_floor_on_every_seed(self, result, verdicts) -> None:
        values = result.ensemble.values("cppi_drawdown")
        assert np.all(values < -D)
        assert result.declared.cppi_drawdown == pytest.approx(-0.848088, abs=5e-7)
        found = result.ensemble.band("cppi_drawdown")
        assert (found.low, found.high) == pytest.approx((-0.902235, -0.742510), abs=5e-7)
        claims = [row.verdict for row in rows(result) if row.number == "12" and "CPPI" in row.label]
        assert claims == ["did not reproduce", "reproduced"]

    def test_cppi_as_described_keeps_the_floor_on_every_seed(self, result) -> None:
        values = result.ensemble.values("described_drawdown")
        assert np.all(values > -D)
        assert result.declared.described_drawdown == pytest.approx(-0.495638, abs=5e-7)


class TestBesideTheReplication:
    def test_cppi_as_described_costs_about_a_quarter_of_the_growth(self, result) -> None:
        seeded = result.declared
        assert seeded.described_growth == pytest.approx(2.436097e-03, rel=5e-7)
        found = result.ensemble.band("described_growth")
        assert (found.low, found.high) == pytest.approx((2.320925e-03, 2.814401e-03), rel=5e-7)
        assert 1 - seeded.described_growth / seeded.full_growth == pytest.approx(0.255285, abs=5e-7)

    def test_the_script_s_historical_lines(self, result) -> None:
        """Read at the declared seed's capped optimum, with ``ret`` read for line 73's ``r``."""
        lines = result.lines
        assert lines.leverage == result.declared.optimum
        assert lines.full_growth == pytest.approx(3.421423e-03, rel=5e-7)
        assert lines.drawdown_over_1_4 == pytest.approx(-0.526211, abs=5e-7)
        assert lines.full_drawdown == pytest.approx(-0.396779, abs=5e-7)
        assert lines.cppi_growth == pytest.approx(3.368026e-03, rel=5e-7)
        assert lines.cppi_drawdown == pytest.approx(-0.391438, abs=5e-7)
        assert lines.described_growth == pytest.approx(2.673396e-03, rel=5e-7)
        assert lines.described_drawdown == pytest.approx(-0.332652, abs=5e-7)


class TestRowGroup13TheEighteenPointFourGap:
    def test_the_kelly_band_implied_by_example_5_1_s_figures(self) -> None:
        low, high = implied_kelly_band()
        assert (low, high) == pytest.approx((21.558894, 26.757652), abs=5e-7)
        assert not low <= float(BOOK_KELLY) <= high

    def test_the_bands_are_half_a_printed_unit_either_side(self) -> None:
        assert rounding_band("1.6") == pytest.approx((1.55, 1.65))
        assert rounding_band("11", scale=0.01) == pytest.approx((0.105, 0.115))

    def test_the_implied_kelly_inverts_its_own_formula(self) -> None:
        """A series made with a Sharpe ratio of 1.6 under the formula gives its Kelly back."""
        sigma = 0.0042
        m = 1.6 * sigma / math.sqrt(252)
        apr = math.exp(252 * (m - sigma**2 / 2)) - 1
        assert implied_kelly(1.6, apr) == pytest.approx(m / sigma**2, rel=1e-9)

    def test_the_kelly_rises_with_the_sharpe_ratio_and_falls_with_the_apr(self) -> None:
        assert implied_kelly(1.65, 0.11) > implied_kelly(1.6, 0.11) > implied_kelly(1.55, 0.11)
        assert implied_kelly(1.6, 0.105) > implied_kelly(1.6, 0.11) > implied_kelly(1.6, 0.115)

    def test_the_shifted_ensemble_s_median_optimum(self, result) -> None:
        assert result.shifted_params.lam == pytest.approx(-1.222510e-03, rel=5e-7)
        assert result.shifted.band("uncapped").median == pytest.approx(18.470198, abs=1e-6)
        assert sum(run.on_the_cap for run in result.shifted.runs) == 8

    def test_rows_3_8_10_and_11_land_under_it_and_row_9_does_not(self, result) -> None:
        landed = {
            (number, printed): lands for number, printed, _, lands in shifted_landings(result)
        }
        assert landed == {
            ("3", BOOK_OPTIMUM_FMINBND): True,
            ("3", BOOK_OPTIMUM): True,
            ("8", BOOK_DRAWDOWN_OPTIMUM): True,
            ("9", BOOK_DRAWDOWN_HALF): False,
            ("10", BOOK_DRAWDOWN_SEVENTH): True,
            ("11", BOOK_CPPI_GROWTH): True,
            ("11", BOOK_FULL_GROWTH): True,
        }
        half = result.shifted.band("drawdown_half")
        assert (half.low, half.high) == pytest.approx((-0.953551, -0.823942), abs=5e-7)

    def test_the_shifted_draws_are_the_declared_draws_moved(self, result) -> None:
        moved = draws(result.shifted_params, ENSEMBLE_SEEDS[0])
        original = draws(result.params, ENSEMBLE_SEEDS[0])
        np.testing.assert_allclose(
            moved - original, result.shifted_params.lam - result.params.lam, rtol=0, atol=1e-17
        )


class TestTheLoopTwins:
    @pytest.mark.parametrize("which", ["draws", "saved"])
    def test_cppi_as_scripted_is_its_loop(self, result, declared_draws, returns, which) -> None:
        values = declared_draws if which == "draws" else returns
        f = result.declared.optimum
        np.testing.assert_allclose(
            cppi_as_scripted(values, f), cppi_as_scripted_loop(values, f), rtol=0, atol=1e-13
        )

    @pytest.mark.parametrize("which", ["draws", "saved"])
    def test_cppi_as_described_is_its_loop(self, result, declared_draws, returns, which) -> None:
        values = declared_draws if which == "draws" else returns
        f = result.declared.optimum
        found, loop = cppi_as_described(values, f), cppi_as_described_loop(values, f)
        np.testing.assert_allclose(found, loop, rtol=0, atol=1e-12)
        assert max_drawdown(found) == pytest.approx(max_drawdown(loop), abs=1e-12)


class TestOnSyntheticReturns:
    def test_the_optimum_of_a_two_outcome_series_is_kelly_s(self) -> None:
        """Up 0.1 or down 0.05 with equal odds: g' = 0 at f = 0.5/0.05 − 0.5/0.1 = 5."""
        values = np.array([0.1, -0.05] * 50)
        assert ruin_leverage(values) == pytest.approx(20.0)
        assert optimal_leverage(values, CAP) == pytest.approx(5.0, abs=1e-6)
        assert optimal_leverage(values) == pytest.approx(5.0, abs=1e-6)

    def test_a_ruin_leverage_below_the_cap_bounds_the_search(self) -> None:
        """A loss of 0.2 ruins at 5, so the capped search never reaches 20 or evaluates 5."""
        values = np.array([0.3, -0.2, 0.25, 0.05] * 25)
        assert ruin_leverage(values) == pytest.approx(5.0)
        found = optimal_leverage(values, CAP)
        assert 0 < found < 5
        assert found == pytest.approx(_derivative_root(values), abs=1e-6)
        with pytest.raises(ValueError, match="ruin leverage"):
            growth(5.0, values)

    def test_a_series_with_no_negative_return_has_no_ruin_and_no_optimum(self) -> None:
        values = np.array([0.01, 0.02, 0.0, 0.03])
        assert math.isinf(ruin_leverage(values))
        assert optimal_leverage(values, CAP) == pytest.approx(CAP, abs=1e-6)
        with pytest.raises(ValueError, match="no negative return and no cap"):
            optimal_leverage(values)

    def test_a_cppi_path_that_sets_a_high_falls_and_recovers(self) -> None:
        """f = 2, D = 0.5, worked by hand.

        The path opens on a day that returns nothing, because ``calculateMaxDD``
        never counts its first row as a high. As described: the subaccount
        stays at 0.5, goes to 0.6 and resets to 0.55 at the high of 1.1, falls
        to 0.495 and 0.4455, rises to 0.6237 for a high of 1.1737 and resets to
        0.58685, then ends at 0.70422, so the account ends at 1.29107 and its
        deepest drawdown is 0.9955 / 1.1 − 1. As scripted: the unlevered
        drawdown goes 0, 0, 0, −0.05, −0.0975 and back to 0, so the account
        earns 0, 0.1, −0.05, −0.0475, 0.1805 and 0.1.
        """
        values = np.array([0.0, 0.1, -0.05, -0.05, 0.2, 0.1])
        described = cppi_as_described(values, 2.0)
        np.testing.assert_allclose(
            np.cumprod(1 + described), [1.0, 1.1, 1.045, 0.9955, 1.1737, 1.29107], rtol=1e-12
        )
        assert max_drawdown(described) == pytest.approx(0.9955 / 1.1 - 1, rel=1e-12)
        np.testing.assert_allclose(described, cppi_as_described_loop(values, 2.0), rtol=1e-12)
        scripted = cppi_as_scripted(values, 2.0)
        np.testing.assert_allclose(
            scripted, [0.0, 0.1, -0.05, -0.0475, 0.1805, 0.1], rtol=1e-12, atol=1e-15
        )
        np.testing.assert_allclose(scripted, cppi_as_scripted_loop(values, 2.0), rtol=1e-12)

    def test_with_no_drawdown_both_cppi_forms_are_the_full_account(self) -> None:
        """Location 3438: CPPI equals ``f·D`` on the whole account when every return is positive."""
        values = np.array([0.01, 0.02, 0.005, 0.03])
        full = 3.0 * D * values
        np.testing.assert_allclose(cppi_as_scripted(values, 3.0), full, rtol=1e-12)
        np.testing.assert_allclose(cppi_as_described(values, 3.0), full, rtol=1e-12)

    def test_cppi_as_described_refuses_a_leverage_that_empties_the_subaccount(self) -> None:
        with pytest.raises(ValueError, match="empties the subaccount"):
            cppi_as_described(np.array([0.1, -0.25]), 4.0)


class TestTheReport:
    def test_every_row_prints_its_verdict(self, result, printed) -> None:
        for row in rows(result):
            assert row.verdict in printed
            assert row.label in printed

    def test_it_names_the_vintage_the_seeds_and_the_label(self, printed) -> None:
        assert "pythoncodesanddata/AUDCAD_unequal_ret.csv" in printed
        assert "saved 2018-12-26" in printed
        assert "declared seed 20261012, ensemble 20261013 to 20261212" in printed
        assert "Exploratory." in printed

    def test_it_prints_row_group_13(self, printed) -> None:
        assert "21.56 to 26.76" in printed
        assert "median uncapped optimum 18.470198" in printed
        assert "does not land" in printed

    def test_it_names_how_many_seeds_the_ruin_leverage_cut(self, printed) -> None:
        assert "seeds on the cap 158 of 200" in printed
        assert "below 20: 42, against 29.8 expected exactly" in printed
