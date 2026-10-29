"""The pins for the Monte Carlo leverage, historical optimization and CPPI of Boxes 8.1 to 8.6.

This file is the single authority for every number a prose surface quotes
about *Algorithmic Trading*'s Chapter 8 leverage boxes and the rows beside
them. ``docs/replication-log.md`` Entry 43 carries the verdicts and points here
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
  figure lands inside the ensemble's 5th to 95th percentile. Row 3 reads that
  band on the seeds whose ruin leverage is above the book's 30.2, a rule
  chosen after the ensemble was seen, and the declared band across all 200 is
  pinned beside it.

A seeded figure is pinned at six decimals, or six significant figures where it
is smaller than 0.01, so a change to the draw method cannot move it inside the
book's rounding unnoticed. An optimum is pinned at 1e-6, because the search
stops within about 3e-7 of the true optimum at a leverage of 20, and the
uncapped ones are also held to the root of the growth rate's derivative.

``blog/monte-carlo-leverage-lessons.md`` quotes most of these figures, so a
change to any of them moves that post too. ``TestWhatThePostMeasured`` holds
the numbers the post added, all measured after the run.
``TestWhatThePostSays`` reads one copy of each figure from the post itself
and checks it against the run, so a typo in the post fails a test.
``TestThePostsHelpers`` holds the helpers the post's figure shares with the
run. ``tests/test_monte_carlo_leverage_figures.py`` holds what the figure
draws, including the growth rates and the drawdown days the post quotes.
``tests/test_monte_carlo_leverage_whiteboard.py`` holds what the two sketches draw,
with the figures they read from the run.

Exploratory. Reproducing Chan's figures spends his 612 returns on a method he
chose. The boxes first ran on the declared seeds on 2026-10-10.
"""

from __future__ import annotations

import io
import math
import re
from contextlib import redirect_stdout
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
from scipy import integrate, optimize, stats

from chan import monte_carlo_leverage as module
from chan.aud_cad_johansen import SCRIPT_KELLY
from chan.khandani_lo_book_two import gap, matches
from chan.monte_carlo_leverage import (
    APR_BAND,
    BAND,
    BOOK_APR_PERCENT,
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
    BOOK_SHARPE,
    BOOK_TYPE,
    CAP,
    DRAWS,
    ENSEMBLE_SEEDS,
    EQUAL_WITHIN,
    SEED,
    SHARPE_BAND,
    SIMILAR_WITHIN,
    XATOL,
    Band,
    D,
    Ensemble,
    MonteCarloLeverage,
    account_drawdowns,
    cppi_as_described,
    cppi_as_described_loop,
    cppi_as_scripted,
    cppi_as_scripted_loop,
    draws,
    growth,
    implied_kelly,
    implied_kelly_band,
    kelly,
    lands_in_exact_distribution,
    lower_tail,
    max_drawdown,
    minimum_below,
    optimal_leverage,
    optimum_band,
    pearson_fit,
    read_returns,
    rounding_band,
    rows,
    ruin_leverage,
    shifted_landings,
    shifted_parameters,
    simulated_verdict,
)
from chan.monte_carlo_leverage_figures import days_below, deepest_day, first_below, signed
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

    def test_the_declared_band_shares_the_capped_band_s_lower_tail(self, result) -> None:
        """Why row 3's rule changed: both bands share their 5th percentile.

        numpy's linear percentile puts it between the 10th and 11th sorted
        optima, and both of those seeds' ruin leverages are below 20, so a seed
        held down by its ruin leverage sets both bands' low end.
        """
        ens = result.ensemble
        uncapped, capped = ens.band("uncapped"), ens.band("optimum")
        assert uncapped.low == capped.low
        assert uncapped.low == pytest.approx(16.622019, abs=1e-6)
        ruin = ens.values("ruin")
        assert np.all(ruin[ens.values("uncapped") <= uncapped.low] < CAP)
        order = np.argsort(ens.values("uncapped"))
        tenth, eleventh = ens.values("uncapped")[order[9:11]]
        assert tenth == pytest.approx(16.453115, abs=1e-6)
        assert eleventh == pytest.approx(16.630909, abs=1e-6)
        assert tenth < uncapped.low < eleventh
        assert np.all(ruin[order[9:11]] < CAP)

    def test_under_the_declared_band_both_figures_land(self, result) -> None:
        """The declared rule's verdict, kept beside the one row 3 now reads."""
        found = result.ensemble.band("uncapped")
        assert found.holds(float(BOOK_OPTIMUM_FMINBND)) and found.holds(float(BOOK_OPTIMUM))

    def test_the_band_row_3_reads(self, result) -> None:
        """The uncapped optimum on the seeds whose ruin leverage is above the book's 30.2.

        Their count is within four binomial standard errors of the exact chance
        that the least of 100,000 draws is above −1 / 30.2.
        """
        kept = result.ensemble.ruin_above(float(BOOK_RUIN))
        assert len(kept.runs) == 40
        p = 1 - minimum_below(result.params, -1 / float(BOOK_RUIN))
        assert abs(40 - 200 * p) < 4 * math.sqrt(200 * p * (1 - p))
        found = optimum_band(result.ensemble)
        assert found == kept.band("uncapped")
        assert found.low == pytest.approx(22.969856, abs=1e-6)
        assert found.median == pytest.approx(24.024213, abs=1e-6)
        assert found.high == pytest.approx(25.374220, abs=1e-6)

    def test_row_3_reads_the_declared_seed_s_uncapped_optimum(self, result) -> None:
        """The gap and the verdict read the same quantity, so the gap is to 22.295382, not 20."""
        printed = [row.computed for row in rows(result) if row.number == "3"]
        assert printed == ["22.295382", "22.295382"]
        assert gap(result.declared.uncapped, BOOK_OPTIMUM_FMINBND) == 3.0
        assert gap(result.declared.uncapped, BOOK_OPTIMUM) == pytest.approx(3.1, abs=1e-12)

    def test_row_3_neither_figure_lands(self, verdicts) -> None:
        assert verdicts[("3", BOOK_OPTIMUM_FMINBND)] == "did not reproduce"
        assert verdicts[("3", BOOK_OPTIMUM)] == "did not reproduce"

    def test_row_3_follows_only_the_conditioned_band(self, result) -> None:
        """Every other seed moved to 18 lands the book under the other bands and changes nothing.

        Moving the conditioned seeds instead, to straddle 19 and 19.2, lands both.
        """
        moved = tuple(
            run if run.ruin > float(BOOK_RUIN) else replace(run, uncapped=18.0, optimum=18.0)
            for run in result.ensemble.runs
        )
        other = replace(result, ensemble=Ensemble(moved))
        assert other.ensemble.band("uncapped").holds(float(BOOK_OPTIMUM_FMINBND))
        assert other.ensemble.band("optimum").holds(float(BOOK_OPTIMUM))
        assert {(r.number, r.verdict) for r in rows(other) if r.number in ("3", "4")} == {
            ("3", "did not reproduce"),
            ("4", "reproduced"),
        }
        spread = iter(np.linspace(18.5, 19.5, 40))
        straddled = tuple(
            replace(run, uncapped=next(spread)) if run.ruin > float(BOOK_RUIN) else run
            for run in result.ensemble.runs
        )
        landed = replace(result, ensemble=Ensemble(straddled))
        assert [r.verdict for r in rows(landed) if r.number == "3"] == [
            "reproduced with a gap, the seed"
        ] * 2

    def test_row_4_the_kelly_lies_inside_row_3_s_band(self, result, verdicts) -> None:
        assert optimum_band(result.ensemble).holds(result.kelly)
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
        """Exactly 0.149180, so about 29.8 of 200. The ensemble's 42 is 2.4 standard errors above.

        ``TestWhatThePostMeasured`` pins how far above and the chance of 42 or more.
        """
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
        found = result.ensemble.band("described_drawdown")
        assert (found.low, found.high) == pytest.approx((-0.499628, -0.489965), abs=5e-7)

    def test_one_seed_below_the_floor_fails_each_claim(self, result) -> None:
        """A claim on every seed fails when one seed breaks the floor."""
        first, *rest = result.ensemble.runs
        broken = replace(first, described_drawdown=-0.6, cppi_drawdown=-0.6)
        other = replace(result, ensemble=Ensemble((broken, *rest)))
        claims = [row.verdict for row in rows(other) if row.number == "12" and "CPPI" in row.label]
        assert claims == ["did not reproduce", "did not reproduce"]


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

    @pytest.mark.parametrize(
        ("compounding", "low", "high"),
        [("exact", 22.065999, 27.261771), ("simple", 20.891304, 25.928571)],
    )
    def test_other_compoundings_move_the_edge_but_not_to_18_4(self, compounding, low, high) -> None:
        """``(1 + m)^252 − 1`` or ``252·m`` for the log growth, each giving ``S² / (252·m)``."""

        def kelly(sharpe: float, apr: float) -> float:
            m = math.expm1(math.log1p(apr) / 252) if compounding == "exact" else apr / 252
            return sharpe * sharpe / (252 * m)

        corners = [kelly(s, a) for s in SHARPE_BAND for a in APR_BAND]
        assert (min(corners), max(corners)) == pytest.approx((low, high), abs=5e-7)
        assert min(corners) > float(BOOK_KELLY)

    def test_the_apr_a_kelly_of_18_4_needs_at_a_sharpe_ratio_of_1_6(self) -> None:
        """13.9 percent taken simply, 14.5 under the log growth, 14.9 compounded exactly."""
        sharpe, kelly = 1.6, float(BOOK_KELLY)
        m = sharpe * sharpe / (252 * kelly)
        sigma = sharpe / (math.sqrt(252) * kelly)
        assert 252 * m == pytest.approx(0.139130, abs=5e-7)
        assert math.expm1(252 * (m - sigma**2 / 2)) == pytest.approx(0.144937, abs=5e-7)
        assert math.expm1(252 * math.log1p(m)) == pytest.approx(0.149230, abs=5e-7)
        assert implied_kelly(sharpe, math.expm1(252 * (m - sigma**2 / 2))) == pytest.approx(kelly)

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
        row_3 = [found for number, _, found, _ in shifted_landings(result) if number == "3"]
        assert row_3 == [optimum_band(result.shifted)] * 2

    def test_row_3_s_band_under_it(self, result) -> None:
        """The rule row 3 reads, on the 39 shifted seeds whose ruin leverage is above 30.2."""
        assert len(result.shifted.ruin_above(float(BOOK_RUIN)).runs) == 39
        found = optimum_band(result.shifted)
        assert (found.low, found.high) == pytest.approx((17.514982, 20.017014), abs=1e-6)
        declared = result.shifted.band("uncapped")
        assert (declared.low, declared.high) == pytest.approx((16.339353, 19.905622), abs=1e-6)
        for printed in (BOOK_OPTIMUM_FMINBND, BOOK_OPTIMUM):
            assert found.holds(float(printed)) and declared.holds(float(printed))

    def test_the_shifted_draws_are_the_declared_draws_moved(self, result) -> None:
        moved = draws(result.shifted_params, ENSEMBLE_SEEDS[0])
        original = draws(result.params, ENSEMBLE_SEEDS[0])
        np.testing.assert_allclose(
            moved - original, result.shifted_params.lam - result.params.lam, rtol=0, atol=1e-17
        )


class TestWhatThePostMeasured:
    """What ``blog/monte-carlo-leverage-lessons.md`` quotes that the rows above do not pin.

    The write-up measured each of these after the run had been seen, so they
    are exploratory like everything here and carry no verdict. Each reads the
    vintage and the specification the module docstring states:
    ``pythoncodesanddata/AUDCAD_unequal_ret.csv``, chan-py, ``AUDCAD-UNEQUAL``,
    basis ``return``, saved 2018-12-26, 612 returns, on the declared seed
    20261012 and the 200 seeds 20261013 to 20261212. A drawdown or a leverage
    is pinned at six decimals.
    """

    def test_the_saved_returns_least_day_and_ruin_leverage(self, returns, result) -> None:
        """Lesson 4: the declared seed's least draw is nearly twice as deep as Chan's worst day."""
        assert returns.min() == pytest.approx(-0.022031, abs=5e-7)
        assert ruin_leverage(returns) == pytest.approx(45.390502, abs=5e-7)
        assert result.declared.minimum / returns.min() == pytest.approx(1.9550, abs=5e-5)

    def test_the_script_s_apr_is_closest_to_the_log_growth_compounding(self, returns) -> None:
        """Lesson 2: ``AUDCAD_unequal.m`` compounds the daily returns themselves.

        On the saved file that APR is 0.112410, and compounding the log growth
        ``m − σ²/2``, with σ divided by n − 1, gives 0.112426. The other two
        compoundings land further off.
        """
        days = module.TRADING_DAYS
        script = float(np.prod(1 + returns) ** (days / len(returns)) - 1)
        m, var = float(returns.mean()), float(returns.var(ddof=1))
        log_growth = math.exp(days * (m - var / 2)) - 1
        assert script == pytest.approx(0.112410, abs=5e-7)
        assert log_growth == pytest.approx(0.112426, abs=5e-7)
        others = ((1 + m) ** days - 1, days * m)
        assert all(abs(o - script) > abs(log_growth - script) for o in others)

    def test_the_log_growth_apr_allows_a_second_sigma_near_0_2(self) -> None:
        """Lesson 2: the quadratic in σ has a second root, a daily swing near 20 percent.

        At every corner of the printed figures' rounding the smaller root is
        under 10 percent a day, and the larger sits near 0.2 with a Kelly
        near 0.5, so the smaller is the one :func:`implied_kelly` keeps.
        """
        days = module.TRADING_DAYS
        for sharpe in (1.55, 1.65):
            for apr in (0.105, 0.115):
                per_bar = sharpe / math.sqrt(days)
                spread = math.sqrt(per_bar * per_bar - 2 * math.log1p(apr) / days)
                small, large = per_bar - spread, per_bar + spread
                assert small < 0.1
                assert sharpe / (math.sqrt(days) * small) == pytest.approx(
                    implied_kelly(sharpe, apr), rel=1e-12
                )
                assert 0.19 < large < 0.21
                assert 0.50 < sharpe / (math.sqrt(days) * large) < 0.52

    def test_612_draws_from_the_fit_rarely_reach_the_saved_returns_least_day(
        self, result, returns
    ) -> None:
        """Lesson 4: the fit's left tail is thinner than the history's, so the depth is the count.

        The exact distribution of the least of 612 draws, the backtest's length,
        puts the chance of one at or below −0.022031 at 0.091663. The least of
        100,000 draws reaches deeper because there are 163 times as many.
        """
        p = minimum_below(result.params, float(returns.min()), len(returns))
        assert p == pytest.approx(0.091663, abs=5e-7)
        assert DRAWS / len(returns) == pytest.approx(163.4, abs=0.05)

    def test_42_seeds_ruined_below_the_cap_sit_2_4_standard_errors_above_the_exact_chance(
        self, result
    ) -> None:
        """Lesson 4: 42 of 200 against 200 × 0.149180, and the exact chance of 42 or more."""
        p = result.ruin_below_cap_exact
        count = sum(run.ruin_below_cap for run in result.ensemble.runs)
        z = (count - 200 * p) / math.sqrt(200 * p * (1 - p))
        assert z == pytest.approx(2.414274, abs=5e-7)
        assert stats.binom.sf(count - 1, 200, p) == pytest.approx(0.012871, abs=5e-7)

    def test_the_seeds_at_or_below_the_book_s_optima_are_all_held_down_by_ruin(
        self, result
    ) -> None:
        """Lesson 3: every seed whose uncapped optimum is at or below 19 or 19.2 ruins below 20."""
        uncapped, ruin = result.ensemble.values("uncapped"), result.ensemble.values("ruin")
        low = uncapped <= float(BOOK_OPTIMUM)
        assert (int(low.sum()), int(np.count_nonzero(uncapped <= float(BOOK_OPTIMUM_FMINBND)))) == (
            30,
            28,
        )
        assert np.all(ruin[low] < CAP)
        assert ruin[low].max() == pytest.approx(19.147175, abs=5e-7)

    def test_a_seed_is_on_the_cap_exactly_when_its_ruin_leverage_is_20_or_more(
        self, result
    ) -> None:
        """The claim compares the uncapped optimum with the ruin leverage, read directly.

        Reading it through ``on_the_cap`` alone would let a property redefined
        as ``ruin >= CAP`` compare the ruin leverage with itself and pass.
        """
        runs = result.ensemble.runs
        assert [run.uncapped >= CAP for run in runs] == [run.ruin >= CAP for run in runs]
        assert [run.on_the_cap for run in runs] == [run.uncapped >= CAP for run in runs]
        free = result.ensemble.values("uncapped")[result.ensemble.values("ruin") >= CAP]
        assert len(free) == 158
        assert free.min() == pytest.approx(20.075698, abs=1e-6)

    def test_on_the_cap_reads_the_uncapped_optimum_not_the_ruin_leverage(self, result) -> None:
        """On these 200 seeds the two agree, so only a hand-built run tells them apart.

        An optimum of 19.5 with ruin at 21 is a seed the capped search would
        answer below the cap, so it is not on the cap.
        """
        run = replace(result.declared, uncapped=19.5, ruin=21.0)
        assert not run.on_the_cap
        assert replace(run, uncapped=20.5).on_the_cap

    def test_the_kelly_is_at_or_past_ruin_on_78_seeds_and_the_declared_one(self, result) -> None:
        """Lesson 4: at the Kelly some draw loses everything on these seeds."""
        assert result.kelly == pytest.approx(23.845328, abs=5e-7)
        assert int(np.count_nonzero(result.ensemble.values("ruin") <= result.kelly)) == 78
        assert result.declared.ruin <= result.kelly

    def test_the_saved_returns_drawdowns_at_the_optimum_and_the_kelly(
        self, result, returns
    ) -> None:
        """Lesson 6: ``calculateMaxDD`` on the 612 days, far from the draws' −0.99."""
        assert max_drawdown(result.historical * returns) == pytest.approx(-0.737560, abs=5e-7)
        assert max_drawdown(result.kelly * returns) == pytest.approx(-0.739733, abs=5e-7)


POST = Path(__file__).resolve().parents[1] / "blog" / "monte-carlo-leverage-lessons.md"


def _cell(latex: str) -> str:
    """A table cell as the reader sees it, so ``\\text{to } 24.8`` is ``to 24.8``.

    ``5{,}681`` reads ``5,681`` and ``{+5.4}`` reads ``+5.4``.
    """
    text = re.sub(r"\\text\{([^}]*)\}", r"\1", latex).replace("{,}", ",")
    return " ".join(text.replace("{", "").replace("}", "").split())


def _table(text: str, header: str) -> dict[str, list[list[str]]]:
    """The one ``array`` block holding ``header``, its rows keyed by their first cell.

    A row whose first cell is empty continues the labelled row above it, as
    Lesson 3's table writes each band on three lines, so each label maps to
    its rows in order, the label left out. The header rows sit under ``""``.
    """
    bodies = re.findall(r"\\begin\{array\}\{[^}]*\}(.*?)\\end\{array\}", text, re.S)
    (body,) = [found for found in bodies if header in found]
    table: dict[str, list[list[str]]] = {}
    label = ""
    for line in body.split("\\\\"):
        cells = [_cell(cell) for cell in line.replace("\\hline", "").split("&")]
        label = cells[0] or label
        table.setdefault(label, []).append(cells[1:])
    return table


def _fixed(value: float, places: int = 6) -> str:
    """``value`` as a table prints it, with an ASCII minus."""
    return f"{value:.{places}f}"


# A search stops within about 3e-7 of an optimum, so a figure that rests on one
# can print a different sixth decimal on another machine. CI's runner printed
# the Lesson 3 band's 22.969856 as 22.969857. An optimum, a band of optima and
# a table cell computed at an optimum are compared as numbers within this
# tolerance instead of as printed digits.
NEAR = 1.5e-6


def _near(cells: list[str], values, prefix: str = "") -> bool:
    """Whether each cell, less ``prefix``, is within ``NEAR`` of its value."""
    return len(cells) == len(values) and all(
        cell.startswith(prefix) and abs(float(cell.removeprefix(prefix)) - value) <= NEAR
        for cell, value in zip(cells, values, strict=True)
    )


def _says(text: str, before: str, value: float, after: str = "") -> bool:
    """Whether ``text`` holds ``before``, a number within ``NEAR`` of ``value``, then ``after``."""
    pattern = re.escape(before) + r"(−?\d+\.\d+)" + re.escape(after)
    return any(
        abs(float(found.replace("−", "-")) - value) <= NEAR for found in re.findall(pattern, text)
    )


def _lowest_kelly(compounding: str) -> float:
    """The least Kelly over the corners of Example 5.1's rounding, under one compounding."""

    def one(sharpe: float, apr: float) -> float:
        if compounding == "log":
            return implied_kelly(sharpe, apr)
        days = module.TRADING_DAYS
        m = math.expm1(math.log1p(apr) / days) if compounding == "exact" else apr / days
        return sharpe * sharpe / (days * m)

    return min(one(sharpe, apr) for sharpe in SHARPE_BAND for apr in APR_BAND)


class TestWhatThePostSays:
    """One copy of each figure ``blog/monte-carlo-leverage-lessons.md`` quotes, read from the post.

    Other copies of the same figure elsewhere in the post are not always read.
    Each expected value comes from the run, or from the book's printed figures
    the module holds as constants, and is compared at the precision the post
    prints it. Two kinds are compared within ``NEAR`` instead: an optimum or a
    band of optima, and a table cell computed at an optimum. A figure derived
    from an optimum in a sentence, such as a growth gap, is still compared at
    its printed digits. A table is read by its row labels, and a sentence by
    the words around its number.

    The prose states these numbers and the tests above derive them, so before
    this class a typo in the post passed every test. Round 1 of the post's
    review changed 62 single digits across its prose, tables and alt text, and
    none failed a test.
    """

    text = POST.read_text("utf-8")

    def test_lesson_1_s_table_and_the_two_methods_agreement(self, result) -> None:
        table = _table(self.text, "\\text{Historical}")
        assert table["Computed"][0][0] == _fixed(result.kelly)
        assert _near(table["Computed"][0][1:], [result.historical])
        assert table["Book"] == [[BOOK_KELLY, BOOK_HISTORICAL]]
        gaps = (gap(result.kelly, BOOK_KELLY), gap(result.historical, BOOK_HISTORICAL))
        assert table["Gap"] == [[f"{value:+.1f}" for value in gaps]]
        below = 1 - result.historical / result.kelly
        assert (
            f"The historical optimum sits {below:.6f} below the Kelly in relative terms, "
            f"or {100 * below:.2f} percent, inside the {100 * EQUAL_WITHIN:.0f} percent"
        ) in self.text

    def test_the_fit_s_kappa_kurtosis_and_moment_order(self, result, returns) -> None:
        words = {5: "five", 6: "sixth"}
        order = 2 * result.params.m - 1
        assert f"Here κ is {result.kappa:.6f}, which puts the returns in type IV" in self.text
        assert BOOK_TYPE == 4
        assert f"The kurtosis is {result.moments.kurtosis:.6f}, where a bell curve’s is 3" in (
            self.text
        )
        assert (
            f"finite moments only below order {order:.2f}, so its first "
            f"{words[math.floor(order)]} moments exist and its {words[math.ceil(order)]} does not"
        ) in self.text
        assert f"draws {DRAWS:,} returns from it" in self.text
        assert f"His script saved its {len(returns)} daily returns" in self.text

    def test_lesson_2_s_kelly_range_and_its_three_compoundings(self, result, returns) -> None:
        low, high = result.kelly_band
        assert (
            f"a Sharpe ratio from {SHARPE_BAND[0]:.2f} to {SHARPE_BAND[1]:.2f} and an APR from "
            f"{100 * APR_BAND[0]:.1f} to {100 * APR_BAND[1]:.1f} percent, the Kelly runs from "
            f"{low:.6f} to {high:.6f} under that compounding"
        ) in self.text
        lowest = {name: _lowest_kelly(name) for name in ("log", "exact", "simple")}
        assert lowest["log"] == low
        assert (
            f"**Compounding the log growth**, as above, puts the lowest Kelly at "
            f"{lowest['log']:.6f}."
        ) in self.text
        assert f"**Compounding 1 + m exactly** each day puts it at {lowest['exact']:.6f}." in (
            self.text
        )
        assert f"with no compounding, puts it at {lowest['simple']:.6f}." in self.text
        assert min(lowest.values()) > float(BOOK_KELLY)
        assert f"None reaches {BOOK_KELLY}." in self.text

        days = module.TRADING_DAYS
        script = float(np.prod(1 + returns) ** (days / len(returns)) - 1)
        m, var = float(returns.mean()), float(returns.var(ddof=1))
        log_growth = math.exp(days * (m - var / 2)) - 1
        assert f"compounded over {days} days, which on the saved file is {script:.6f}." in self.text
        assert (
            f"puts the APR at {log_growth:.6f}. So compounding the log growth, the first of the "
            "three ways below, is the closest"
        ) in self.text

        sharpe, kelly_ = float(BOOK_SHARPE), float(BOOK_KELLY)
        needed = sharpe * sharpe / (days * kelly_)
        simple, exact = days * needed, math.expm1(days * math.log1p(needed))
        assert (
            f"At a Sharpe ratio of {BOOK_SHARPE}, a Kelly of {BOOK_KELLY} needs an APR of "
            f"{100 * simple:.1f} to {100 * exact:.1f} percent across the three, well above the "
            f"printed {BOOK_APR_PERCENT}."
        ) in self.text

        per_bar = sharpe / math.sqrt(days)
        spread = math.sqrt(per_bar * per_bar - 2 * math.log1p(float(BOOK_APR_PERCENT) / 100) / days)
        large = per_bar + spread
        assert (
            f"The larger is near {large:.1f}, a daily swing of about {100 * large:.0f} percent "
            f"with a Kelly near {per_bar / large:.1f}, so the smaller is the one used."
        ) in self.text
        swing = 0.1
        for s in SHARPE_BAND:
            for a in APR_BAND:
                b = s / math.sqrt(days)
                r = math.sqrt(b * b - 2 * math.log1p(a) / days)
                assert b - r < swing < b + r
        assert (
            f"Example 5.1’s own printed figures rule {BOOK_KELLY} out.** Any series with that "
            f"example’s Sharpe ratio and APR, and a daily swing under {100 * swing:.0f} percent, "
            f"has a Kelly of at least {min(lowest.values()):.6f}"
        ) in self.text

    def test_the_declared_seed_and_the_further_seeds(self) -> None:
        assert (
            f"Each simulated figure here comes from one seed, {SEED}, named in writing before "
            f"the run and called the declared seed. It is judged against {len(ENSEMBLE_SEEDS)} "
            f"further seeds, {ENSEMBLE_SEEDS[0]} to {ENSEMBLE_SEEDS[-1]}."
        ) in self.text

    def test_lesson_2_s_shifted_draws(self, result) -> None:
        median = result.shifted.band("uncapped").median
        half = result.shifted.band("drawdown_half")
        assert _says(self.text, "the median uncapped optimum becomes ", median, ", close")
        assert float(BOOK_DRAWDOWN_HALF) < half.low
        assert (
            f"Its {signed(float(BOOK_DRAWDOWN_HALF), 3)} sits just past a band that runs to "
            f"{signed(half.low)}."
        ) in self.text

    def test_lesson_3_s_cap_and_the_seeds_held_down_by_ruin(self, result) -> None:
        words = {30: "Thirty", 40: "Forty"}
        runs = result.ensemble.runs
        on_cap = sum(run.on_the_cap for run in runs)
        assert (
            f"On the declared seed the script returns its cap of {CAP:g}, the most it can "
            f"return, and so it does on {on_cap} of the {len(runs)} further seeds."
        ) in self.text
        assert result.declared.on_the_cap
        assert _says(
            self.text,
            "Searched without the cap, the declared seed’s optimum is ",
            result.declared.uncapped,
            f".\n\nThe {on_cap} seeds split cleanly from the rest.",
        )
        free = result.ensemble.values("uncapped")[result.ensemble.values("ruin") >= CAP]
        assert _says(self.text, "has an uncapped optimum above 20, the lowest at ", free.min(), ".")

        declared = result.ensemble.band("uncapped")
        assert _says(self.text, "Its band runs from ", declared.low, " to ")
        assert _says(
            self.text,
            " to ",
            declared.high,
            f", and both {BOOK_OPTIMUM_FMINBND} and {BOOK_OPTIMUM} land inside it.",
        )
        uncapped, ruin = result.ensemble.values("uncapped"), result.ensemble.values("ruin")
        low = uncapped <= float(BOOK_OPTIMUM)
        at_19 = int(np.count_nonzero(uncapped <= float(BOOK_OPTIMUM_FMINBND)))
        assert np.all(ruin[low] < CAP)
        assert (
            f"{words[int(low.sum())]} seeds have an uncapped optimum at or below {BOOK_OPTIMUM}, "
            f"and {at_19} at or below {BOOK_OPTIMUM_FMINBND}. All {int(low.sum())} have a ruin "
            f"leverage below 20, the largest {ruin[low].max():.6f}."
        ) in self.text
        assert _says(
            self.text,
            "The capped band’s 5th percentile is the same ",
            result.ensemble.band("optimum").low,
            f", a point between the optima of two of those {int(low.sum())} seeds",
        )
        kept = len(result.ensemble.ruin_above(float(BOOK_RUIN)).runs)
        assert (
            f"seeds whose ruin leverage is above {BOOK_RUIN}, the ruin leverage the book prints "
            f"from its least draw of {signed(float(BOOK_MINIMUM), 4)}."
        ) in self.text
        assert f"{words[kept]} seeds qualify." in self.text

        middle = f"{BAND[1] - BAND[0]:.0f}"
        runs = len(result.ensemble.runs)
        assert f"both of the book’s fall inside the middle {middle} percent of them" in self.text
        assert f"fall outside the middle {middle} percent of what {runs} reruns give" in self.text
        assert (
            f"between the {BAND[0]:.0f}th and {BAND[1]:.0f}th percentiles of the same quantity"
        ) in self.text

    def test_lesson_3_s_table_of_bands(self, result) -> None:
        def verdict(found: Band) -> str:
            lands = [found.holds(float(p)) for p in (BOOK_OPTIMUM_FMINBND, BOOK_OPTIMUM)]
            return {(True, True): "both land", (False, False): "neither lands"}[tuple(lands)]

        table = _table(self.text, "\\text{As fitted}")
        assert table[""] == [["As fitted", f"Moved to {BOOK_KELLY}"]]
        runs = len(result.ensemble.runs)
        declared = (result.ensemble.band("uncapped"), result.shifted.band("uncapped"))
        chosen = (optimum_band(result.ensemble), optimum_band(result.shifted))
        assert _near(table["Declared rule"][0], [found.low for found in declared])
        upper, verdicts = table[f"all {runs} seeds"]
        assert _near(upper, [found.high for found in declared], prefix="to ")
        assert verdicts == [verdict(found) for found in declared]
        assert _near(table["Rule chosen after"][0], [found.low for found in chosen])
        kept = [len(e.ruin_above(float(BOOK_RUIN)).runs) for e in (result.ensemble, result.shifted)]
        upper, counts, verdicts = table[f"ruin above {BOOK_RUIN}"]
        assert _near(upper, [found.high for found in chosen], prefix="to ")
        assert counts == [f"{count} seeds" for count in kept]
        assert verdicts == [verdict(found) for found in chosen]
        assert all(found.holds(result.kelly) for found in (declared[0], chosen[0]))
        assert f"The Kelly of {result.kelly:.6f} lies inside both bands" in self.text

    def test_lesson_4_s_least_draw_and_ruin_leverage(self, result, returns) -> None:
        seeded = result.declared
        assert (
            f"draws hold a worse day than Chan’s backtest because there are about "
            f"{round(DRAWS / len(returns))} times as many"
        ) in self.text
        assert (
            f"At {signed(float(BOOK_MINIMUM), 4)} that chance is "
            f"{result.minimum_at_or_below_book:.6f}, inside the 5 to 95 percent range"
        ) in self.text
        ruin_chance = minimum_below(result.params, -1 / float(BOOK_RUIN))
        assert (
            f"the chance of a ruin leverage at or below {BOOK_RUIN} is {ruin_chance:.6f}."
        ) in self.text
        assert (
            f"The declared seed’s least draw is {signed(seeded.minimum)}, a gap of "
            f"{signed(gap(seeded.minimum, BOOK_MINIMUM), 4)}, so both reproduced with a gap"
        ) in self.text
        worst = float(returns.min())
        assert 1.9 < seeded.minimum / worst < 2
        assert (
            f"The worst of Chan’s {len(returns)} backtest returns is {signed(worst)}, a ruin "
            f"leverage of {ruin_leverage(returns):.6f}. The declared seed’s least draw is "
            f"{seeded.minimum / worst:.4f} times as deep, nearly twice, and its ruin leverage "
            f"is {seeded.ruin:.6f}."
        ) in self.text
        short = minimum_below(result.params, worst, len(returns))
        assert (
            f"With {len(returns)} draws in place of {DRAWS:,}, the same formula gives a chance "
            f"of {short:.6f}, about {100 * short:.1f} percent, that the least is at or below "
            f"{signed(worst)}."
        ) in self.text

    def test_lesson_4_s_seeds_ruined_at_the_kelly_and_below_the_cap(self, result) -> None:
        runs = result.ensemble.runs
        at_kelly = int(np.count_nonzero(result.ensemble.values("ruin") <= result.kelly))
        assert result.declared.ruin <= result.kelly
        assert f"The same holds on {at_kelly} of the {len(runs)} further seeds." in self.text
        below = sum(run.ruin_below_cap for run in runs)
        assert below == len(runs) - sum(run.on_the_cap for run in runs)
        assert (
            f"Across the {len(runs)} seeds, {below} have a ruin leverage below the script’s cap "
            f"of {CAP:g}, which means a least draw deeper than {signed(-1 / CAP, 2)}. They are the "
            f"{below} seeds of Lesson 3 that do not sit on the cap."
        ) in self.text
        p = result.ruin_below_cap_exact
        z = (below - len(runs) * p) / math.sqrt(len(runs) * p * (1 - p))
        tail = stats.binom.sf(below - 1, len(runs), p)
        assert (
            f"The formula above gives a chance of {p:.6f} that a seed has such a draw, or about "
            f"{len(runs) * p:.1f} seeds of {len(runs)}. So {below} is more than the fit "
            f"predicts, by {z:.1f} standard deviations of a binomial count, and the chance of "
            f"{below} or more is about {100 * tail:.1f} percent."
        ) in self.text

    def test_lesson_5_s_table(self, result, declared_draws) -> None:
        f = result.declared.optimum
        accounts = (
            account_drawdowns(cppi_as_scripted(declared_draws, f)),
            account_drawdowns(cppi_as_described(declared_draws, f)),
            account_drawdowns(f * D * declared_draws),
        )
        names = ("cppi_drawdown", "described_drawdown", "full_drawdown")
        bands = [result.ensemble.band(name) for name in names]
        table = _table(self.text, "\\text{Box 8.6's}")
        assert _near(table["Deepest"][0], [getattr(result.declared, n) for n in names])
        assert _near(table["5th"][0], [found.low for found in bands])
        assert _near(table["95th"][0], [found.high for found in bands])
        assert table["Days"] == [[f"{days_below(account):,}" for account in accounts]]

    def test_lesson_5_s_days_and_growth(self, result, declared_draws) -> None:
        f = result.declared.optimum
        scripted = account_drawdowns(cppi_as_scripted(declared_draws, f))
        described = account_drawdowns(cppi_as_described(declared_draws, f))
        full = account_drawdowns(f * D * declared_draws)
        assert deepest_day(scripted) == deepest_day(full)
        assert (
            f"The loop first falls below −0.5 on day {first_below(scripted)} and reaches its "
            f"deepest on day {deepest_day(scripted):,}, the same day as the full account."
        ) in self.text
        runs = result.ensemble.runs
        assert all(run.cppi_drawdown < -D for run in runs)
        assert all(run.described_drawdown > -D for run in runs)
        assert f"It breaks the floor on all {len(runs)} further seeds." in self.text
        assert (
            f"The scheme’s deepest is on day {deepest_day(described):,}, and it stays above "
            f"−0.5 on all {len(runs)}."
        ) in self.text
        assert f"At the script’s f of {CAP:g}, f·D is {D * CAP:g}" in self.text

        seeded = result.declared
        quarter = 1 - seeded.described_growth / seeded.full_growth
        assert round(4 * quarter) == 1
        assert (
            f"the loop’s growth falls short by {seeded.growth_gap:.6f}, or "
            f"{100 * seeded.growth_gap:.1f} percent"
        ) in self.text
        assert (f"The scheme’s falls short by {quarter:.6f}, about a quarter.") in self.text
        book = 1 - float(BOOK_CPPI_GROWTH) / float(BOOK_FULL_GROWTH)
        assert (
            f"The book’s two growth rates on p. 264, {BOOK_CPPI_GROWTH} for the loop and "
            f"{BOOK_FULL_GROWTH} for the full account, differ by about {100 * book:.1f} percent"
        ) in self.text

    def test_lesson_6_s_drawdown_table(self, result) -> None:
        names = ("drawdown_optimum", "drawdown_half", "drawdown_seventh")
        bands = [result.ensemble.band(name) for name in names]
        table = _table(self.text, "f/7")
        assert table["Book"] == [
            [BOOK_DRAWDOWN_OPTIMUM, BOOK_DRAWDOWN_HALF, f"about {BOOK_DRAWDOWN_SEVENTH}"]
        ]
        assert _near(table["Seed"][0], [getattr(result.declared, n) for n in names])
        assert _near(table["5th"][0], [found.low for found in bands])
        assert _near(table["95th"][0], [found.high for found in bands])

    def test_lesson_6_s_growth_table(self, result) -> None:
        names = ("cppi_growth", "full_growth", "full_drawdown")
        bands = [result.ensemble.band(name) for name in names]
        table = _table(self.text, "\\text{Growth,}")
        assert table["Book"] == [[BOOK_CPPI_GROWTH, BOOK_FULL_GROWTH, BOOK_FULL_DRAWDOWN]]
        assert _near(table["Seed"][0], [getattr(result.declared, n) for n in names])
        assert _near(table["5th"][0], [found.low for found in bands])
        assert _near(table["95th"][0], [found.high for found in bands])

    def test_lesson_6_s_seventh_and_the_saved_returns_drawdowns(self, result, returns) -> None:
        assert (
            f"The declared seed’s f / 7 is {result.declared.optimum / 7:.6f}, since its f is the "
            "cap."
        ) in self.text
        assert f"{float(BOOK_OPTIMUM) / 7:.1f}" == BOOK_SEVENTH_LEVERAGE
        assert (
            f"The book’s leverage at a seventh, {BOOK_SEVENTH_LEVERAGE}, is {BOOK_OPTIMUM} over 7."
        ) in self.text
        assert (
            f"At the historical optimum the deepest is "
            f"{signed(max_drawdown(result.historical * returns))}, and at the Kelly "
            f"{signed(max_drawdown(result.kelly * returns))}."
        ) in self.text
        lines = result.lines
        assert lines.leverage == pytest.approx(CAP, abs=1e-6)
        assert (
            f"with f its capped optimum of {CAP:g}, and there the deepest is "
            f"{signed(lines.drawdown_over_1_4)}. The draws at the optimum reach "
            f"{signed(result.declared.drawdown_optimum)}."
        ) in self.text
        assert all(run.growth_gap < SIMILAR_WITHIN for run in result.ensemble.runs)
        assert (
            f"The loop’s shortfall stays under {100 * SIMILAR_WITHIN:.0f} percent on all "
            f"{len(result.ensemble.runs)} seeds."
        ) in self.text


class TestThePostsHelpers:
    """The functions the figure shares with the run, so neither drifts from the other.

    The figure reads the fit through ``pearson_fit`` and the Kelly through
    ``kelly``, as the run does. It reads each day's drawdown through
    ``account_drawdowns``, which shares ``drawdown_path`` with the run's
    ``max_drawdown``, and a test here holds its least value equal to
    ``max_drawdown``'s.
    """

    def test_kelly_is_the_run_s_and_the_script_s(self, result, returns) -> None:
        assert kelly(returns) == result.kelly
        assert matches(kelly(returns), SCRIPT_KELLY)

    def test_kelly_on_returns_worked_by_hand(self) -> None:
        """Mean 0.01 and n − 1 variance 0.0004 over 0.01, 0.03 and −0.01, so 25."""
        assert kelly([0.01, 0.03, -0.01]) == pytest.approx(25.0, rel=1e-12)

    def test_pearson_fit_is_the_run_s_moments_and_parameters(self, result, returns) -> None:
        moments, params = pearson_fit(returns)
        assert moments == result.moments
        assert params == result.params

    @pytest.mark.parametrize("form", ["scripted", "described", "full"])
    def test_account_drawdowns_reach_max_drawdown(self, result, declared_draws, form) -> None:
        f = result.declared.optimum
        account = {
            "scripted": cppi_as_scripted(declared_draws, f),
            "described": cppi_as_described(declared_draws, f),
            "full": f * D * declared_draws,
        }[form]
        found = account_drawdowns(account)
        assert found.shape == account.shape
        assert found.min() == max_drawdown(account)

    def test_account_drawdowns_on_a_path_worked_by_hand(self) -> None:
        """Down 50 percent, up 120, down 20 and up 25: the account goes 0.5, 1.1, 0.88, 1.1.

        Chan's loop starts its high at 0 and on the second row, so the first
        day's loss counts for nothing and the drawdowns are 0, 0, −0.2 and 0.
        """
        found = account_drawdowns(np.array([-0.5, 1.2, -0.2, 0.25]))
        np.testing.assert_allclose(found, [0.0, 0.0, -0.2, 0.0], atol=1e-15)


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
        for form in (cppi_as_described, cppi_as_described_loop):
            with pytest.raises(ValueError, match="empties the subaccount"):
                form(np.array([0.1, -0.25]), 4.0)

    def test_cppi_as_scripted_is_its_loop_on_a_path_that_opens_on_a_loss(self) -> None:
        """The unlevered drawdown is floored at the opening level of 0, not the first day's."""
        values = np.array([-0.1, 0.05, 0.02, -0.03, 0.04])
        found = cppi_as_scripted(values, 2.0)
        np.testing.assert_allclose(found, cppi_as_scripted_loop(values, 2.0), rtol=1e-12)
        assert found[1] == pytest.approx(0.05 * D * 2.0 * 0.9, rel=1e-12)

    @pytest.mark.parametrize("bad", [math.nan, -1.0, -1.5])
    def test_cppi_as_scripted_refuses_a_nan_or_a_total_loss(self, bad) -> None:
        """Past −1 the vectorised form takes the log of a negative, and the loop carries on."""
        values = np.array([0.01, bad, 0.02])
        for form in (cppi_as_scripted, cppi_as_scripted_loop):
            with pytest.raises(ValueError, match="NaN return|at or below -1"):
                form(values, 2.0)

    def test_cppi_as_described_refuses_a_nan(self) -> None:
        for form in (cppi_as_described, cppi_as_described_loop):
            with pytest.raises(ValueError, match="NaN return"):
                form(np.array([0.01, math.nan, 0.02]), 2.0)


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

    def test_it_counts_the_seeds_row_11_s_claim_holds_on(self, printed) -> None:
        assert "within 2% on the declared seed, and on 200 of 200 seeds" in printed

    def test_it_keeps_row_3_s_declared_band_beside_the_new_one(self, printed) -> None:
        """Each band's ends at the 1e-6 the optima are pinned to, since a sixth decimal can flip.

        The search stops within about 3e-7 of an optimum, and 25.374220 sits
        less than 1e-7 from a rounding boundary, so the printed digits are
        parsed rather than matched.
        """
        number = r"(-?\d+\.\d{6})"
        found = re.search(
            rf"uncapped optimum, ruin > 30\.2 on 40 seeds, band {number} to {number}", printed
        )
        assert found is not None
        assert tuple(map(float, found.groups())) == pytest.approx(
            (22.969856, 25.374220), abs=1.5e-6
        )
        found = re.search(
            r"row 3 under the declared rule, every seed's uncapped optimum, "
            rf"band {number} to {number}: 19 and 19\.2 land",
            printed,
        )
        assert found is not None
        assert tuple(map(float, found.groups())) == pytest.approx(
            (16.622019, 24.865122), abs=1.5e-6
        )

    @pytest.mark.parametrize(
        ("name", "printed", "expected"),
        [
            ("minimum", BOOK_MINIMUM, -0.01),
            ("ruin", BOOK_RUIN, -7.0),
            ("drawdown_optimum", BOOK_DRAWDOWN_OPTIMUM, 0.008),
            ("drawdown_half", BOOK_DRAWDOWN_HALF, 0.092),
            ("drawdown_seventh", BOOK_DRAWDOWN_SEVENTH, 0.1),
            ("cppi_growth", BOOK_CPPI_GROWTH, 0.00074),
            ("full_growth", BOOK_FULL_GROWTH, 0.000746),
            ("full_drawdown", BOOK_FULL_DRAWDOWN, 0.0),
        ],
    )
    def test_each_seeded_row_s_gap(self, result, name, printed, expected) -> None:
        """The gaps Entry 43's verdict table prints, at the book's precision."""
        assert gap(getattr(result.declared, name), printed) == pytest.approx(expected, abs=1e-12)
