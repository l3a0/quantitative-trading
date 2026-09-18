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

import dataclasses
import math
import re

import numpy as np
import pytest

from chan.coin_flip_growth import (
    BOOK_PATHS,
    BOOK_REF,
    BOOK_ROUNDS,
    BOOK_SEED,
    LOSS,
    SIGN_SIGMAS,
    START_CAPITAL,
    WIN,
    Moments,
    capital_horizon,
    gamble_moments,
    log_return_sd,
    main,
    report,
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


def _terminal_wealth_estimator(rounds: int, paths: int, seed: int) -> float:
    """The ensemble estimator the module rejects, computed here because the
    module does not implement it. Log of the mean terminal wealth, per round."""
    rng = np.random.default_rng(seed)
    heads = rng.integers(0, 2, size=(paths, rounds), dtype=np.int8) == 1
    logs = np.where(heads, math.log1p(0.11), math.log1p(-0.10))
    return math.log(np.exp(logs.sum(axis=1)).mean()) / rounds


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
        assert (log_return_sd() / 1e-6) ** 2 == pytest.approx(1.10e10, rel=0.01)

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

        The two margins are asserted rather than the booleans alone. Comparing
        ``resolves_sign`` against its own definition holds nothing about the
        threshold, and would pass for any value between 0.28 and 4.95.
        """
        small, pinned = simulate(100, 200, 0), simulate()
        assert SIGN_SIGMAS == 2.0
        assert abs(small.time_average_growth) / small.standard_error == pytest.approx(
            0.279, abs=5e-4
        )
        assert abs(pinned.time_average_growth) / pinned.standard_error == pytest.approx(
            4.955, abs=5e-4
        )
        assert not small.resolves_sign
        assert pinned.resolves_sign

    def test_the_standard_error_divides_by_every_flip(self) -> None:
        """Held at an unequal size, where rounds*paths, rounds^2 and paths^2
        differ. At the pinned size all three coincide, so the size that proves
        the book's figures unreachable cannot also hold this."""
        assert simulate(100, 200, 0).standard_error == pytest.approx(
            0.10486027 / math.sqrt(20_000), rel=1e-6
        )

    def test_a_run_records_the_size_it_ran(self) -> None:
        """Read back by the report's header and its too-small branch. Pinned at
        an unequal size, because a swap is invisible at the pinned one."""
        run = simulate(100, 200, 0)
        assert (run.rounds, run.paths, run.seed) == (100, 200, 0)
        assert capital_horizon(250, gamble_moments()).rounds == 250

    def test_the_result_objects_are_frozen(self) -> None:
        """A replication's own outputs do not get edited after the fact."""
        for frozen in (
            gamble_moments(),
            simulate(10, 10, 0),
            capital_horizon(10, gamble_moments()),
        ):
            with pytest.raises(dataclasses.FrozenInstanceError):
                frozen.rounds = 0  # type: ignore[misc]

    def test_only_one_ensemble_estimator_survives_more_rounds(self) -> None:
        """Why the module averages simple returns per flip rather than taking
        the log of mean terminal wealth.

        Both estimate ln(1.005). At 5,000 rounds the second has lost most of it,
        because a sample mean misses more of the lognormal tail the longer the
        paths run, so adding rounds shrinks the very divergence the report
        exists to show.
        """
        target, rounds, paths = math.log(1.005), 5_000, 1_000
        for seed in range(20):
            run = simulate(rounds, paths, seed)
            assert run.ensemble_log_growth == pytest.approx(target, abs=1e-4)
            logs = _terminal_wealth_estimator(rounds, paths, seed)
            assert logs < 0.0038


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


# ============================================================
# The report and the CLI, which are the only surfaces a reader meets
# ============================================================


class TestTheReportSaysWhatItComputed:
    """Nothing else in this file executes ``report`` or ``main``.

    The repo already learned this once. ``TestReportNamesItsBasis`` in
    ``tests/test_pair_cointegration.py`` exists because a ported report
    announced the wrong price basis while reading a different file, and nothing
    noticed, because nothing covered the report at all. A report that names the
    wrong quantity is worse than one that names none.
    """

    def test_the_report_runs_and_prints_the_figures_it_labels(self, moments, capsys) -> None:
        """Every labelled rate carries the value its label claims."""
        run = simulate(100, 200, 0)
        report(run, horizons=(10, 1000))
        out = capsys.readouterr().out
        assert f"{moments.ensemble_log_growth:+.7f}" in out
        assert f"{moments.growth_continuous:+.7f}" in out
        assert f"{moments.growth_exact:+.7f}" in out
        assert f"{run.ensemble_log_growth:+.7f}" in out
        assert f"{run.time_average_growth:+.7f}" in out
        assert "population, over two outcomes" in out
        assert "rng.integers" in out
        assert "none, synthetic" in out

    def test_the_report_names_which_ensemble_estimator_the_run_used(self, capsys) -> None:
        """Requirement 2. Two estimators of the ensemble side exist and only one
        survives more rounds, so the report says which one produced its number
        rather than leaving it in a docstring."""
        report(simulate(100, 200, 0), horizons=(10,))
        out = capsys.readouterr().out
        assert "mean" in out and "simple return per flip" in out
        assert "log of mean terminal wealth" in out

    def test_the_report_draws_four_horizons_by_default(self, capsys) -> None:
        """The default is what `python -m chan.coin_flip_growth` prints, and a
        divergence needs more than one row to be visible as a widening one."""
        report(simulate(10, 10, 0))
        row = re.compile(r"^\s+[\d,]+\s+\$[\d,]+\s+\$[\d,]+\s+[\d,.]+$")
        assert len([x for x in capsys.readouterr().out.splitlines() if row.match(x)]) == 4

    def test_the_report_draws_every_horizon_it_is_given(self, capsys) -> None:
        """The divergence is visible in the capital and nowhere else, so a
        report that silently drew one row would show a gap and not a widening
        one."""
        report(simulate(10, 10, 0), horizons=(10, 100, 250, 1000))
        row = re.compile(r"^\s+[\d,]+\s+\$[\d,]+\s+\$[\d,]+\s+[\d,.]+$")
        rows = [line for line in capsys.readouterr().out.splitlines() if row.match(line)]
        assert len(rows) == 4
        assert "241.72" in rows[-1]

    def test_a_run_that_cannot_resolve_the_sign_says_so_in_the_report(self, capsys) -> None:
        """The too-small branch, which is the visible half of requirement 5.
        Nothing raises, because nothing failed, so the only thing standing
        between a reader and a wrong-signed number is this line."""
        report(simulate(100, 200, 0), horizons=(10,))
        assert "TOO SMALL" in capsys.readouterr().out
        report(simulate(), horizons=(10,))
        assert "TOO SMALL" not in capsys.readouterr().out

    def test_the_book_reference_quotes_the_figures_the_suite_pins(self, moments) -> None:
        """``BOOK_REF`` is the second line the report prints and it restates
        three pinned figures, which makes it a second implementation unless a
        re-pin has to move it too."""
        assert f"{moments.expected_return:.3f}" in BOOK_REF
        assert f"{moments.return_sd:.3f}" in BOOK_REF
        assert f"{moments.growth_continuous:.7f}" in BOOK_REF

    def test_the_cli_refuses_a_size_it_cannot_run(self, monkeypatch) -> None:
        """Zero rounds divides by zero in the standard error. argparse exits
        rather than letting the report print nan."""
        for bad in (["--rounds", "0"], ["--paths", "0"], ["--rounds", "-1"]):
            monkeypatch.setattr("sys.argv", ["chan.coin_flip_growth", *bad])
            with pytest.raises(SystemExit):
                main()

    def test_the_cli_passes_every_argument_through(self, monkeypatch, capsys) -> None:
        """A dropped argument leaves the report describing a run nobody asked
        for, and the header is where that shows."""
        monkeypatch.setattr(
            "sys.argv", ["chan.coin_flip_growth", "--rounds", "50", "--paths", "30", "--seed", "9"]
        )
        main()
        out = capsys.readouterr().out
        assert "30 paths x 50 rounds, seed 9" in out
        assert f"{simulate(50, 30, 9).time_average_growth:+.7f}" in out


class TestTheGambleIsParameterised:
    """The payoff arguments carry a general claim, so a second gamble holds it.

    ``breakeven_stake`` is ``(b - 1) / b`` for a win leg paying ``b`` times the
    stake, and one payoff cannot tell that formula apart from the constant
    1/11. These cases are the only ones in the file that leave Chan's numbers.
    """

    # Win 300, lose 200, on 2,000 of capital. All three differ from the
    # defaults, and each differs in a way that separates it from the constant
    # it would collapse to: the stake is 200/2,000 = 0.1, against 0.05 if the
    # loss leg were read from LOSS and 0.2 if the capital were read from
    # START_CAPITAL. A payoff sharing any value with the defaults leaves the
    # corresponding argument free.
    OTHER = {"win": 300.0, "loss": 200.0, "capital": 2000.0}

    def test_a_second_payoff_moves_the_break_even_stake(self) -> None:
        """b = 1.5 here, so break-even is 1/3 rather than 1/11, and the gamble
        is on the winning side of it."""
        other = gamble_moments(**self.OTHER)
        assert other.breakeven_stake == pytest.approx(1.0 / 3.0, abs=5e-12)
        assert other.stake_fraction == pytest.approx(0.1, abs=5e-12)
        assert other.expected_return == pytest.approx(0.025, abs=5e-12)
        assert other.return_sd == pytest.approx(0.125, abs=5e-12)
        assert other.expected_gain == pytest.approx(50.0, abs=5e-9)
        assert other.growth_continuous == pytest.approx(0.0171875, abs=5e-12)
        assert other.stake_fraction < other.breakeven_stake

    def test_a_second_payoff_reaches_the_simulation_too(self) -> None:
        """The payoff arguments are plumbed through ``log_return_sd`` and
        ``_flip_log_returns``, so the run's own standard error moves with them
        and a winning gamble comes out positive on both averages."""
        assert log_return_sd(**self.OTHER) == pytest.approx(0.12256123, abs=5e-8)
        run = simulate(1000, 200, 0, **self.OTHER)
        assert run.standard_error == pytest.approx(0.12256123 / math.sqrt(200_000), rel=1e-6)
        assert run.time_average_growth > 0.0
        assert run.ensemble_log_growth > 0.0

    def test_the_horizon_scales_with_the_capital_it_is_given(self, moments) -> None:
        """``capital`` is a real argument, not a constant read from the module."""
        base = capital_horizon(100, moments)
        doubled = capital_horizon(100, moments, capital=2 * START_CAPITAL)
        assert doubled.ensemble_capital == pytest.approx(2 * base.ensemble_capital, rel=1e-12)
        assert doubled.ratio == pytest.approx(base.ratio, rel=1e-12)

    def test_the_horizon_reads_the_moments_it_is_given(self) -> None:
        """A deliberately altered ``Moments`` moves the result, so the argument
        is read rather than recomputed from the defaults."""
        altered = dataclasses.replace(gamble_moments(), growth_exact=0.0)
        assert capital_horizon(100, altered).time_average_capital == pytest.approx(
            START_CAPITAL, rel=1e-12
        )

    def test_the_seed_sweep_defaults_to_the_count_the_pins_use(self) -> None:
        """Both call sites pass ``SEEDS`` explicitly, so the default is free
        unless something holds it. Three seeds would pass at a fragile size,
        which is the argument the function's own docstring makes."""
        assert seeds_with_positive_time_average(100, 200) == seeds_with_positive_time_average(
            100, 200, SEEDS
        )


def test_the_moments_type_is_what_the_horizon_takes() -> None:
    """``capital_horizon`` requires its moments rather than defaulting them, so
    a caller cannot silently compare two different gambles in one report."""
    assert isinstance(gamble_moments(), Moments)
    with pytest.raises(TypeError):
        capital_horizon(100)  # type: ignore[call-arg]
