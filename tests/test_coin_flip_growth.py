"""Pins for Chan's coin-flip gamble, Example 6.1.

This file is the single authority for every number any prose surface quotes
about this experiment. ``docs/replication-log.md`` Entry 2 states those numbers
and derives none of them, and ``src/chan/coin_flip_growth.py`` carries the
reasoning.

Two kinds of assertion live here and they are not interchangeable.

1. **Closed-form pins**, which chase the figures the book prints. They involve
   no random draw, so they hold exactly and are quoted at the seven decimals
   Chan uses.
2. **Simulation pins**, which hold what a seeded run is entitled to claim. They
   never chase a book figure, because the standard error of a growth rate
   estimated from a million flips is 1.05e-4 against a quantity of 5e-4, so no
   run this suite could afford resolves the book's precision.

Every simulation pin here names its draw method. A seed alone does not
determine a run: ``rng.integers``, ``rng.random``, ``rng.binomial`` and
``rng.standard_normal`` give four different flip sequences from one seed, and
``test_the_draw_method_is_part_of_the_pin`` is what stops that being forgotten.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from chan.coin_flip_growth import (
    BOOK_PATHS,
    BOOK_ROUNDS,
    BOOK_SEED,
    LOSS,
    SIGN_SIGMAS,
    START_CAPITAL,
    WIN,
    capital_horizon,
    gamble_moments,
    log_return_sd,
    seeds_with_positive_time_average,
    simulate,
)

# The number of seeds every robustness pin below sweeps. Named once because
# the count is part of what those pins claim: three seeds would pass at a size
# where the demonstration is fragile.
SEEDS = 200


@pytest.fixture(scope="module")
def moments():
    return gamble_moments()


# ============================================================
# The closed form, which is what the book's figures are pinned against
# ============================================================


class TestBookFigures:
    """Every figure Example 6.1 prints, at the precision it prints it.

    Chan gives four numbers at locations 3176 and 3186 and no formula, so the
    formula is what these assertions really hold. Only one choice reproduces
    all four at once, and ``TestTheNearMisses`` is the other half of that
    claim.
    """

    def test_expected_gain_is_five_dollars(self, moments) -> None:
        """Location 3176 and again at 3186. It holds at the starting capital
        only, which is the sense of Chan's infinite-capital player."""
        assert moments.expected_gain == pytest.approx(5.0, abs=5e-9)

    def test_expected_return_and_standard_deviation(self, moments) -> None:
        """Location 3186, quoted there at three decimals."""
        assert moments.expected_return == pytest.approx(0.005, abs=5e-7)
        assert moments.return_sd == pytest.approx(0.105, abs=5e-7)

    def test_the_growth_rate_reproduces_to_the_digit(self, moments) -> None:
        """Chan's −0.0005125, at the seven decimals he prints.

        This is the whole replication. The tolerance is tight on purpose: at
        1e-5 the sample-standard-deviation error in ``TestTheNearMisses`` would
        still fail, but so would nothing else, and the point of the pin is that
        the formula is exactly right rather than nearly right.
        """
        assert moments.growth_continuous == pytest.approx(-0.0005125, abs=5e-11)

    def test_the_two_averages_disagree_in_sign(self, moments) -> None:
        """The argument, and the reason the layman is right to refuse.

        Both sides in log units per round, which the book's own two figures are
        not: 0.005 is an arithmetic mean simple return and −0.0005125 is a log
        growth rate.
        """
        assert moments.ensemble_log_growth == pytest.approx(0.0049875, abs=5e-8)
        assert moments.ensemble_log_growth > 0.0
        assert moments.growth_continuous < 0.0
        assert moments.growth_exact < 0.0

    def test_the_stake_is_exactly_a_tenth(self, moments) -> None:
        """The book says the payoff is adjusted as capital changes, so the
        stake is a fixed fraction. It is $100 against $1,000, and "roughly"
        does no work."""
        assert moments.stake_fraction == pytest.approx(0.1, abs=5e-12)

    def test_the_gamble_sits_just_past_break_even(self, moments) -> None:
        """Growth crosses zero at 1/11, so Chan's 1/10 is barely the losing
        side of the line. That is why the result is a sign rather than a
        magnitude, and it is what makes the thin margin worth stating."""
        assert moments.breakeven_stake == pytest.approx(1.0 / 11.0, abs=5e-12)
        assert moments.stake_fraction > moments.breakeven_stake


class TestTheNearMisses:
    """Two other formulas a reader could reasonably pick, and what they give.

    Without these the growth-rate pin holds a number rather than a choice. Each
    case below is computed here rather than imported, because the module does
    not implement the wrong ones.
    """

    def test_the_sample_standard_deviation_misses_by_a_factor_of_twelve(self) -> None:
        """Dividing by n-1 over two outcomes gives 0.14849, not 0.105.

        pandas' ``.std()`` defaults to that convention while numpy's does not,
        and both are declared dependencies here. The resulting growth rate is
        −0.006025, which is out by 11.8 times and still prints as a small
        negative number, so nothing about it looks wrong on the page.
        """
        up, down, mean = WIN / START_CAPITAL, -LOSS / START_CAPITAL, 0.005
        sample_sd = math.sqrt(((up - mean) ** 2 + (down - mean) ** 2) / 1)
        assert sample_sd == pytest.approx(0.14849, abs=5e-6)
        wrong = mean - sample_sd**2 / 2
        assert wrong == pytest.approx(-0.006025, abs=5e-7)
        assert wrong / -0.0005125 == pytest.approx(11.8, abs=0.05)

    def test_the_exact_discrete_rate_is_a_different_number(self, moments) -> None:
        """0.5*ln(1.11) + 0.5*ln(0.90) = −0.00050025.

        It is the right answer to a question the book did not ask, and it
        differs at the fourth significant digit, so it fails the book's pin. It
        is reported beside Chan's figure rather than in place of it, and
        ``docs/replication-log.md`` gives it its own row with no published
        counterpart.
        """
        assert moments.growth_exact == pytest.approx(-0.00050025, abs=5e-9)
        assert moments.growth_exact != pytest.approx(-0.0005125, abs=5e-8)
        assert moments.growth_exact - (-0.0005125) == pytest.approx(1.225e-5, abs=5e-9)


# ============================================================
# What a seeded run can and cannot carry
# ============================================================


class TestWhatTheSimulationCanClaim:
    """The simulation demonstrates the argument. It never pins a book figure."""

    def test_the_per_flip_spread_sets_what_a_run_can_see(self) -> None:
        """0.10486 per flip, which is what makes the book's precision
        unreachable. A standard error of 1e-5 needs about 110 million flips
        and 1e-6 needs about 11 billion."""
        assert log_return_sd() == pytest.approx(0.10486, abs=5e-6)
        assert (log_return_sd() / 1e-5) ** 2 == pytest.approx(1.10e8, rel=0.01)

    def test_the_run_reproduces_itself(self) -> None:
        """Same seed, same numbers. Determinism is what makes the report
        worth quoting at all."""
        first, second = simulate(200, 200, 7), simulate(200, 200, 7)
        assert first == second

    def test_the_draw_method_is_part_of_the_pin(self) -> None:
        """A seed alone does not determine the run, so the module names its
        draw method and this is why.

        Four ways to flip a fair coin from seed 7 give four different
        sequences. ``docs/replication-log.md`` row 11 records the same shape,
        where a conclusion about a library turned out to be a conclusion about
        an ``autolag`` default. ``rng.integers`` is chosen because bounded
        integers come straight off the bit stream.
        """
        n = 16
        sequences = {
            tuple(np.random.default_rng(7).integers(0, 2, n).tolist()),
            tuple((np.random.default_rng(7).random(n) < 0.5).astype(int).tolist()),
            tuple(np.random.default_rng(7).binomial(1, 0.5, n).tolist()),
            tuple((np.random.default_rng(7).standard_normal(n) > 0).astype(int).tolist()),
        }
        assert len(sequences) == 4

    def test_the_standard_error_predicts_the_observed_spread(self) -> None:
        """The report prints a closed-form error beside the estimate, so the
        formula has to be right rather than plausible.

        Predicted 1.0486e-4 at the pinned size against an observed 9.96e-5 over
        200 seeds. The band is wide because a spread measured on 200 draws
        carries about 5% sampling error of its own.
        """
        run = simulate()
        assert run.standard_error == pytest.approx(1.0486e-4, abs=5e-8)
        observed = np.std(
            [simulate(BOOK_ROUNDS, BOOK_PATHS, seed).time_average_growth for seed in range(SEEDS)]
        )
        assert observed == pytest.approx(9.96e-5, abs=5e-7)
        assert observed == pytest.approx(run.standard_error, rel=0.15)

    def test_the_pinned_run_lands_where_it_should(self, moments) -> None:
        """Seed 42 at the pinned size. Held loosely against the closed form on
        purpose, at one part in ten, because tightening it past what the
        standard error supports would pin the seed rather than the gamble."""
        run = simulate()
        assert run.seed == BOOK_SEED
        assert run.time_average_growth == pytest.approx(moments.growth_exact, rel=0.10)
        assert run.ensemble_log_growth == pytest.approx(moments.ensemble_log_growth, rel=0.10)
        assert run.time_average_growth < 0.0 < run.ensemble_log_growth


class TestTheSizeIsMeasuredRatherThanChosen:
    """Why the pinned size is what it is, held so a smaller one cannot pass.

    A test pinning one seed's number passes at a size where the demonstration
    is fragile, and so would three seeds. These two sweep 200.
    """

    def test_the_sign_holds_across_every_seed_at_the_pinned_size(self) -> None:
        """Zero of the first 200 seeds show a positive time average at 1,000
        paths by 1,000 rounds. This is the assertion the report's claim rests
        on, and it costs about a second."""
        assert seeds_with_positive_time_average(BOOK_ROUNDS, BOOK_PATHS, SEEDS) == 0

    def test_a_smaller_size_fails_on_more_than_a_quarter_of_seeds(self) -> None:
        """56 of the first 200 seeds at 100 rounds by 200 paths.

        This is the measurement that makes the size above defensible rather
        than lucky. Without it, nothing in the suite would notice a builder
        dropping the size to something that happens to work on seed 42.
        """
        assert seeds_with_positive_time_average(100, 200, SEEDS) == 56

    def test_a_run_too_small_to_resolve_the_sign_says_so(self) -> None:
        """The failure this guards is a report, not an exception.

        At 100 rounds by 200 paths the estimate sits inside two standard errors
        of zero, so the run cannot say which side of it the truth is on. The
        report prints that rather than raising, because nothing failed.
        """
        small = simulate(100, 200, 0)
        assert not small.resolves_sign
        assert abs(small.time_average_growth) <= SIGN_SIGMAS * small.standard_error
        assert simulate().resolves_sign


# ============================================================
# What actually diverges
# ============================================================


class TestTheCapitalDiverges:
    """The rates are constants. Only the capital they compound into pulls apart."""

    def test_the_rates_do_not_move_with_the_horizon(self, moments) -> None:
        """The reason the report shows capital at several horizons and the two
        rates once. A report showing two rates at one horizon shows a
        disagreement in sign and never a divergence."""
        for rounds in (10, 1000, 100_000):
            horizon = capital_horizon(rounds, moments)
            implied = math.log(horizon.ensemble_capital / START_CAPITAL) / rounds
            assert implied == pytest.approx(moments.ensemble_log_growth, abs=5e-12)

    def test_the_gap_widens_with_every_round(self, moments) -> None:
        """Ratios of 1.06, 1.73, 3.94 and 241.72 at 10, 100, 250 and 1,000
        rounds, which is what ``docs/replication-log.md`` Entry 2 quotes."""
        ratios = [capital_horizon(n, moments).ratio for n in (10, 100, 250, 1000)]
        assert ratios == [
            pytest.approx(1.06, abs=5e-3),
            pytest.approx(1.73, abs=5e-3),
            pytest.approx(3.94, abs=5e-3),
            pytest.approx(241.72, abs=5e-3),
        ]
        assert ratios == sorted(ratios)

    def test_the_ratio_grows_at_the_difference_between_the_rates(self, moments) -> None:
        """exp(0.005488 * n), that exponent being one rate minus the other."""
        exponent = moments.ensemble_log_growth - moments.growth_exact
        assert exponent == pytest.approx(0.005488, abs=5e-7)
        assert capital_horizon(1000, moments).ratio == pytest.approx(
            math.exp(exponent * 1000), rel=1e-9
        )

    def test_the_capital_a_reader_sees_at_a_thousand_rounds(self, moments) -> None:
        """$146,576 against $606, from $1,000. The ensemble player is rich and
        the trader who actually played is down 39%."""
        horizon = capital_horizon(1000, moments)
        assert horizon.ensemble_capital == pytest.approx(146_576, abs=0.5)
        assert horizon.time_average_capital == pytest.approx(606, abs=0.5)
