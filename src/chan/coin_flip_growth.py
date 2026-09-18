"""Chan's coin-flip gamble, Example 6.1, where expectation and growth disagree.

Chan borrows Kahneman's gamble and rescales it for a trading account. A fair
coin pays $110 on heads and costs $100 on tails against $1,000 of capital. The
expected value is positive and most people still decline it, which behavioural
finance reads as loss aversion and a bias. His point is that declining it can
be correct, because what matters to someone dealt one coin at a time is the
compound growth rate of capital rather than the expected gain per round.

Two averages, and the argument is the difference between them. Chan names both
at Kindle location 3166: the **ensemble average** across different traders, and
the **time series average** over one trader's horizon. Here they have opposite
signs. The ensemble side gains 0.005 per round and the time average loses
0.0005125, so the layman refusing the gamble is right.

The name is a revised-edition label. ``docs/design.md`` declares that every
citation of a chapter, a page or a MATLAB filename in this repo means the 2009
first edition unless it says otherwise. This one does not: it comes from the
revised edition's own prose at location 3186, "As Example 6.1 shows". The
first-edition code mirror this repo cites elsewhere carries ``example6_2.xls``
and ``example6_3.m`` and no ``example6_1`` in any form, so there is no
companion file to check the arithmetic against. The printed prose is the whole
source.

**This experiment reads no vintage.** Every other replication here commits the
series it ran on, because a vendor restates an adjusted price without
announcing it. A gamble has no vendor and no download date, so there is
nothing to restate and nothing to commit. That is why it could be built before
the vintage recorder exists.

**The pins are closed form, and the simulation cannot carry them.** Every
figure the book prints follows from the payoffs alone. The per-flip standard
deviation of the log return is 0.10486, so the standard error of a simulated
growth rate falls as ``0.10486 / sqrt(flips)``. Pinning −0.0005 down to an
absolute 1e-5 takes about 110 million flips and to 1e-6 about 11 billion, while
Chan prints seven decimals. So :func:`gamble_moments` is what the book's figures are pinned
against, and :func:`simulate` is the demonstration a reader looks at.

Three choices in :func:`gamble_moments` are load-bearing, because the book
prints no formula and the near misses do not look wrong on the page.

1. The standard deviation is the population form over the two outcomes. The
   sample form divides by ``n - 1``, gives 0.14849 rather than 0.105, and
   turns the growth rate into −0.006025, out by a factor of 11.8.
2. ``growth_continuous`` is ``m - s**2 / 2``, the continuous approximation the
   book names, and it reproduces −0.0005125 exactly.
3. ``growth_exact`` is the discrete rate, ``0.5 * ln(1.11) + 0.5 * ln(0.90)``.
   It is the right answer to a question the book did not ask, and it differs
   at the fourth significant digit, so it is reported beside the book's figure
   rather than in place of it.

**The rescaling is the trap.** At location 3186 Chan adjusts the payoff as
capital changes, so a doubled account of $2,000 wins $220 or loses $200. Each
round therefore multiplies capital by 1.11 or 0.90, and the stake is exactly a
tenth rather than roughly one. An implementation that adds $110 or subtracts
$100 against a changing balance has no constant growth rate to report at all.

**The rates do not diverge. The capital does.** Both rates are constants in
the number of rounds, so a report showing two rates at one horizon shows a
disagreement in sign and never a divergence. What accumulates is the capital
they imply, since the ensemble mean compounds up while the time-average path
compounds down. :func:`capital_horizon` is that comparison, and the ratio grows
as ``exp(0.005488 * n)``.

``tests/test_coin_flip_growth.py`` is the single authority for every number
quoted about this experiment, and ``docs/replication-log.md`` Entry 2 carries
the verdict.

Usage::

    python -m chan.coin_flip_growth            # Chan's Example 6.1, the pinned run
    python -m chan.coin_flip_growth --rounds 100 --paths 200
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

# Chan's gamble as the book states it, at Kindle locations 3176 and 3186.
WIN = 110.0
LOSS = 100.0
START_CAPITAL = 1000.0
BOOK_REF = (
    "Example 6.1 (rev. ed., locations 3176 and 3186): win $110 or lose $100 "
    "on $1,000, expected return 0.005, return sd 0.105, growth -0.0005125"
)

# The size the pinned run uses. Chosen from measurement rather than taste: at
# 100 rounds by 200 paths the time average came out positive on 56 of the
# first 200 seeds, so more than a quarter of seeds show no divergence at all.
# At this size none of those 200 seeds does, and the sweep costs about a
# second. tests/test_coin_flip_growth.py pins both halves of that.
BOOK_ROUNDS = 1000
BOOK_PATHS = 1000
BOOK_SEED = 42

# How many standard errors from zero an estimate needs before the report is
# willing to call its sign. Two is the usual convention and the number matters
# less than saying it out loud: without a rule the report prints a positive
# time average at a small size and nothing raises, because nothing failed.
SIGN_SIGMAS = 2.0


@dataclass(frozen=True)
class Moments:
    """The closed-form description of one round, which is what the book prints.

    ``expected_gain`` is in dollars and holds only at ``START_CAPITAL``, which
    is the sense of Chan's "$5 gain per round" at location 3186: what a player
    with infinite capital collects, where the stake never rescales. Everything
    else is per round and independent of the capital level, because the payoff
    is rescaled to it.

    ``ensemble_log_growth`` is ``ln(1 + m)``. It exists so the two averages can
    be printed in one unit. The book's own two figures are not: 0.005 is an
    arithmetic mean of a simple return and −0.0005125 is a log growth rate, so
    printing them side by side compares a return against a growth rate.
    """

    expected_gain: float
    expected_return: float
    return_sd: float
    ensemble_log_growth: float
    growth_continuous: float
    growth_exact: float
    stake_fraction: float
    breakeven_stake: float


@dataclass(frozen=True)
class Simulation:
    """One seeded run, and what it is entitled to claim.

    ``standard_error`` is the closed-form ``sd_log / sqrt(rounds * paths)``
    rather than the scatter of the sample, so it is known before the run and
    can be compared against the estimate. Checked against 200 seeds at the
    pinned size, where it predicts 1.0486e-4 and the observed spread is
    9.96e-5, which is inside the sampling error of a spread measured on 200
    draws.

    ``resolves_sign`` is that comparison. False means the run is too small to
    say which side of zero the time average sits on, whatever number it
    happened to produce.
    """

    rounds: int
    paths: int
    seed: int
    ensemble_log_growth: float
    time_average_growth: float
    standard_error: float

    @property
    def resolves_sign(self) -> bool:
        """Whether the time average is far enough from zero to be believed."""
        return abs(self.time_average_growth) > SIGN_SIGMAS * self.standard_error


@dataclass(frozen=True)
class Horizon:
    """Capital after ``rounds``, on both averages, and the gap between them.

    ``time_average_capital`` is ``exp(g * rounds)``, the path the time-average
    rate describes. It equals the median path at even ``rounds`` and not at odd
    ones, where the head count cannot split, so it is named for the rate it
    comes from rather than called typical.
    """

    rounds: int
    ensemble_capital: float
    time_average_capital: float
    ratio: float


def gamble_moments(
    win: float = WIN,
    loss: float = LOSS,
    capital: float = START_CAPITAL,
) -> Moments:
    """Everything Example 6.1 prints, from the payoffs alone. No random draws.

    The two outcomes are equally likely, so every moment below is an average
    over exactly two numbers and the whole calculation is exact.
    """
    up = win / capital
    down = -loss / capital
    mean = 0.5 * (up + down)
    # The population variance over the two outcomes. Dividing by n-1 instead
    # gives 0.14849 and a growth rate out by a factor of 11.8.
    variance = 0.5 * (up - mean) ** 2 + 0.5 * (down - mean) ** 2
    stake = loss / capital
    return Moments(
        expected_gain=0.5 * win - 0.5 * loss,
        expected_return=mean,
        return_sd=math.sqrt(variance),
        ensemble_log_growth=math.log1p(mean),
        growth_continuous=mean - variance / 2.0,
        growth_exact=0.5 * math.log1p(up) + 0.5 * math.log1p(down),
        stake_fraction=stake,
        # Growth is zero where (1 + up)(1 + down) == 1. With a win leg paying
        # b times the stake that solves to f = (b - 1) / b, which is 1/11 here
        # and is why the gamble sits a hair below break-even rather than far
        # from it. Chan's f of 1/10 is just past the line.
        breakeven_stake=(win / loss - 1.0) / (win / loss),
    )


def log_return_sd(win: float = WIN, loss: float = LOSS, capital: float = START_CAPITAL) -> float:
    """Per-flip standard deviation of the log return, which sets what a run can see.

    A simulated growth rate is a mean of ``rounds * paths`` draws from this
    spread, so its standard error is this divided by the square root of that
    count. It is 0.10486 for Chan's payoffs.
    """
    up = math.log1p(win / capital)
    down = math.log1p(-loss / capital)
    return abs(up - down) / 2.0


def _flip_log_returns(
    rounds: int,
    paths: int,
    seed: int,
    win: float,
    loss: float,
    capital: float,
) -> NDArray[np.float64]:
    """Log returns for one seeded block of coin flips.

    ``rng.integers`` rather than a distribution method, on purpose. A seed
    alone does not pin a run: on seed 7, ``integers``, ``random``, ``binomial``
    and ``standard_normal`` give four different flip sequences. Bounded
    integers come straight off the bit stream, which is the narrowest surface
    available, and `pyproject.toml` declares `numpy>=2` with no ceiling.
    """
    rng = np.random.default_rng(seed)
    heads = rng.integers(0, 2, size=(paths, rounds), dtype=np.int8) == 1
    return np.where(heads, math.log1p(win / capital), math.log1p(-loss / capital))


def simulate(
    rounds: int = BOOK_ROUNDS,
    paths: int = BOOK_PATHS,
    seed: int = BOOK_SEED,
    win: float = WIN,
    loss: float = LOSS,
    capital: float = START_CAPITAL,
) -> Simulation:
    """Play the gamble ``paths`` times for ``rounds`` rounds and average two ways.

    The ensemble side is the mean simple return per flip, converted to log
    units. The other candidate, the log of the mean terminal wealth, estimates
    the same quantity and collapses as rounds grow, because a sample mean
    misses more of the lognormal tail the longer the paths run. At 5,000 rounds
    by 1,000 paths this estimator holds ``ln(1.005)`` to within 1e-4 on every
    one of the first 20 seeds, while that one sits below 0.0038 on every one of
    them, over exactly the range where the divergence should become clearer.
    ``test_only_one_ensemble_estimator_survives_more_rounds`` pins both.
    """
    logs = _flip_log_returns(rounds, paths, seed, win, loss, capital)
    return Simulation(
        rounds=rounds,
        paths=paths,
        seed=seed,
        ensemble_log_growth=math.log1p(float(np.expm1(logs).mean())),
        time_average_growth=float(logs.mean()),
        standard_error=log_return_sd(win, loss, capital) / math.sqrt(rounds * paths),
    )


def seeds_with_positive_time_average(
    rounds: int = BOOK_ROUNDS,
    paths: int = BOOK_PATHS,
    seeds: int = 200,
) -> int:
    """How many of the first ``seeds`` seeds fail to show the losing side.

    This is what makes the size defensible rather than lucky. A test that pins
    one seed's number passes at a size where the demonstration is fragile, and
    three seeds would pass too. At 100 rounds by 200 paths this returns 56 out
    of 200. At the pinned size it returns 0.
    """
    return sum(
        1 for seed in range(seeds) if simulate(rounds, paths, seed).time_average_growth > 0.0
    )


def capital_horizon(
    rounds: int,
    moments: Moments,
    capital: float = START_CAPITAL,
) -> Horizon:
    """Capital after ``rounds``, on the ensemble average and on the time average.

    This is the divergence. Both rates are constants, so only the capital they
    compound into pulls apart, and the ratio grows as ``exp((e - g) * rounds)``
    where the exponent is 0.005488 per round for Chan's payoffs.
    """
    ensemble = capital * math.exp(moments.ensemble_log_growth * rounds)
    time_average = capital * math.exp(moments.growth_exact * rounds)
    return Horizon(
        rounds=rounds,
        ensemble_capital=ensemble,
        time_average_capital=time_average,
        ratio=ensemble / time_average,
    )


def report(run: Simulation, horizons: tuple[int, ...] = (10, 100, 250, 1000)) -> None:
    """Print the closed-form figures, the seeded run, and the capital gap."""
    m = gamble_moments()
    print("Chan's coin-flip gamble, Example 6.1 (revised edition, location 3186)")
    print(f"  {BOOK_REF}")
    print("  vintage: none, synthetic. This experiment reads no series.")
    print()
    print("Closed form, which is what the book's figures are pinned against:")
    print(f"  expected gain per round   = ${m.expected_gain:.2f}  at ${START_CAPITAL:,.0f}")
    print(f"  expected return per round = {m.expected_return:+.4f}")
    print(f"  standard deviation        = {m.return_sd:.4f}   (population, over two outcomes)")
    print(
        f"  stake fraction            = {m.stake_fraction:.4f}   (break-even at "
        f"{m.breakeven_stake:.4f})"
    )
    print()
    print("The two averages, in one unit, per round:")
    print(f"  ensemble average (across traders) = {m.ensemble_log_growth:+.7f}")
    print("    closed form ln(1 + m). The run below estimates it as the mean")
    print("    simple return per flip, not as the log of mean terminal wealth,")
    print("    which collapses as rounds grow.")
    print(
        f"  time average     (one trader)     = {m.growth_continuous:+.7f}  "
        "<- the book's continuous approximation"
    )
    print(
        f"  time average, exact discrete      = {m.growth_exact:+.7f}  "
        "<- not a figure the book prints"
    )
    print("  They disagree in sign, which is the whole argument.")
    print()
    print(
        f"Seeded run: {run.paths:,} paths x {run.rounds:,} rounds, seed {run.seed}, "
        "drawn with rng.integers"
    )
    print(f"  ensemble average = {run.ensemble_log_growth:+.7f}")
    print(
        f"  time average     = {run.time_average_growth:+.7f}  "
        f"+/- {run.standard_error:.2e} (1 s.e.)"
    )
    if run.resolves_sign:
        sigmas = abs(run.time_average_growth) / run.standard_error
        print(f"  The time average is {sigmas:.1f} standard errors below zero, so its sign holds.")
    else:
        print(f"  TOO SMALL. The time average is inside {SIGN_SIGMAS:.0f} standard errors of")
        print("  zero, so this run cannot say which side of it the truth sits on. Raise")
        print(f"  --rounds or --paths. The pinned size is {BOOK_PATHS:,} x {BOOK_ROUNDS:,}.")
    print()
    print("The rates are constants. What accumulates is the capital they compound into:")
    print(f"  {'rounds':>8}  {'ensemble mean':>16}  {'time-average path':>19}  {'ratio':>10}")
    for n in horizons:
        h = capital_horizon(n, m)
        print(
            f"  {h.rounds:>8,}  {'$' + format(h.ensemble_capital, ',.0f'):>16}"
            f"  {'$' + format(h.time_average_capital, ',.0f'):>19}  {h.ratio:>10,.2f}"
        )
    print()
    print("A replication is exploratory when a sample was spent looking. This one")
    print("spends none, so neither that label nor its opposite reaches it.")
    print("docs/replication-log.md Entry 2 carries the verdict.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Chan's coin-flip gamble, Example 6.1: expectation against growth"
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=BOOK_ROUNDS,
        help=f"rounds per path (default: {BOOK_ROUNDS}, the pinned size)",
    )
    parser.add_argument(
        "--paths",
        type=int,
        default=BOOK_PATHS,
        help=f"independent players (default: {BOOK_PATHS}, the pinned size)",
    )
    parser.add_argument(
        "--seed", type=int, default=BOOK_SEED, help=f"draw seed (default: {BOOK_SEED})"
    )
    args = parser.parse_args()
    if args.rounds < 1 or args.paths < 1:
        parser.error("--rounds and --paths must both be at least 1")
    report(simulate(rounds=args.rounds, paths=args.paths, seed=args.seed))


if __name__ == "__main__":
    main()
