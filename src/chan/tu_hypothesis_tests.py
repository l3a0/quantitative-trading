"""Three hypothesis tests on TU momentum, *Algorithmic Trading*'s Example 1.1.

A backtest's average return means little until it is set against what chance
alone would give. Example 1.1, at Kindle locations 606 to 674, asks that of
Example 6.1's TU momentum strategy three ways, and the three answers differ by
two orders of magnitude. The first test reads the strategy's daily returns as
Gaussian. The second reruns the strategy on simulated market returns that
share TU's first four moments, 10,000 times, and "1,166 have average strategy
return greater than or equal to the observed average return" (location 665).
The third shuffles the strategy's entry days 100,000 times and finds "not a
single sample" that does as well (location 672). Location 674 reads the second
test as showing that "any random returns distribution with high kurtosis can
be favorable to momentum strategies", and location 2923 repeats its count as
12 percent.

**The transcription.** Every step is Chan's ``TU_mom_hypothesisTest.m``, read
under ``public/img/book2/`` in the mirror
[ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) at
``e4bc46f``, git blob ``c0dda16``, and landed here for
[issue 352](https://github.com/l3a0/quantitative-trading/issues/352). Line
numbers below are that blob's. The strategy itself is Example 6.1's, imported
unchanged from :mod:`chan.tu_momentum`: :func:`~chan.tu_momentum.read_sources`,
:func:`~chan.tu_momentum.signals`, :func:`~chan.tu_momentum.positions`,
:func:`~chan.tu_momentum.market_returns`,
:func:`~chan.tu_momentum.strategy_returns` and
:func:`~chan.tu_momentum.gaussian_statistic`. Every call passes
:data:`~chan.tu_momentum.HOLD_DAYS` to both functions that take it.

1. **The Gaussian test**, L39. ``mean(ret)/std(ret)·√n`` over all 2,000
   returns with MATLAB's n − 1 ``std``. L40's comment prints 2.93.
2. **The randomized-returns test**, L43 to L77. L43 takes the mean, ``std``,
   ``skewness`` and ``kurtosis`` of ``marketRet``. MATLAB's ``std`` divides by
   n − 1, and its ``skewness`` and ``kurtosis`` default to the biased forms,
   with kurtosis not in excess form. L46 draws 2,000 returns from
   ``pearsrnd`` with those moments, L47 builds ``cl_sim = cumprod(1 +
   marketRet_sim) − 1``, and L49 to L65 rebuild the signals and positions
   from ``cl_sim``. L68 and L69 take ``ret_sim`` from the simulated returns
   themselves, never from ``cl_sim``'s own returns, and L71 counts the draws
   whose mean is at or above the observed mean. L77's comment prints a p-value
   of 0.027500, which disagrees with the book's 1,166 of 10,000.
3. **The randomized-trades test**, L82 to L113. L84 to L86 apply one
   ``randperm(2000)`` to both ``longs`` and ``shorts``, which keeps 1,274 long
   days and 474 short days. L103 takes ``ret_sim`` from the observed market
   returns, and L108 counts as L71 does. The script prints no figure for it.

**The third test cannot fail as written.** L88 sets ``pos_sim`` to zeros, and
L99 and L100 then add the shuffled tranches to ``pos``, the observed
positions, rather than to ``pos_sim``. So ``ret_sim`` at L103 is zero on every
draw. The observed mean is positive, so the count is 0 whatever the data.
:func:`randomized_trades_as_written` runs that loop for a few draws, and
:func:`randomized_trades` runs the corrected test, which builds each draw's
positions from its shuffled signals.

**The second test's generator is Pearson type IV, which is an inference.**
``pearsrnd`` picks a member of the Pearson family from the four moments.
MathWorks' page names the types without stating its criterion. The standard
criterion, as Heinrich (2004) gives it, puts TU's moments in type IV, so
:func:`pearson_iv_parameters` and :func:`pearson_iv_draws` draw from type IV.
If ``pearsrnd`` chose the same type, they reproduce the script's null in
distribution, though not draw for draw. The parameters follow Heinrich's
"A guide to the Pearson type IV distribution", CDF/MEMO/STATISTICS/PUBLIC/6820.

**The declaration.** Issue 352 fixed every choice below before any draw on
the two seeds, after scratch runs on other seeds had seen results.

1. ``RETURNS_SEED = 20261010`` for the second test and ``TRADES_SEED =
   20261011`` for the third, each through :func:`numpy.random.default_rng`.
   The draw method is part of what a seed means, so each is stated here.
2. Series i of the second test's 10,000 is row i of ``rng.random((10_000,
   2_000))``, mapped through the type IV inverse CDF. Calls of fewer rows taken
   in order give the same array, so the draws are computed in batches.
3. Draw d of the corrected third test applies one ``rng.permutation(2_000)``
   to both signal arrays, taken in order, so batching changes nothing.
4. A count lands when it lies within two binomial standard errors of the
   printed figure, using the printed proportion and the test's own N, which
   :func:`landing_band` computes. That gives 1,102 to 1,230 for the book's
   1,166, 243 to 307 for the script's 0.027500 at N = 10,000, and only 0 for
   the book's 0 of 100,000.
5. This is Chan's own saved file, so the vintage explanation is spent and a
   count outside its band did not reproduce. The as-written third test cannot
   fail, so it carries no verdict.

**Three rows beside the replication were added after the scratch run saw
results.** Each varies one input to test a reason the book gives, and each
runs on ``RETURNS_SEED``'s uniforms, so it differs from the declared test in
that input alone.

1. The observed positions applied to the simulated returns, which is the test
   the scratch run found to match the script's 0.027500. Nothing in the
   script does this, and the file has one commit, so the match is numerical
   rather than recovered history.
2. A normal draw with TU's mean and ``std``, which removes the skewness and
   kurtosis location 674 credits.
3. The declared draws less their target mean, which removes the drift. Only
   λ depends on the mean, so this is type IV with a mean of zero and costs no
   second inversion.

**The draws run in two dimensions here.** :func:`chan.tu_momentum.positions`
refuses input that is not one-dimensional, and one draw through it takes about
2 ms, so 100,000 would take minutes. :func:`simulated_strategy_returns`,
:func:`fixed_position_returns` and :func:`permuted_strategy_returns` compute a
batch of draws at once with the same arithmetic in the same order, and
``tests/test_tu_hypothesis_tests.py`` holds them equal to the one-dimensional
functions draw by draw. Widening :func:`chan.tu_momentum.positions` was the
alternative, and it would change a contract Example 6.1 shipped.

No sibling code was ported. The sibling repository holds no moment-matched
simulation, and its count-preserving label shuffles share the third test's
idea and none of its code.

Every result here is exploratory. The three tests are Chan's, chosen for a
strategy whose lookback and hold he picked from a table computed on the same
closes. The rows beside them were chosen after the scratch run, so they can
motivate a registered test of the book's reading and cannot confirm or refute
it.
"""

from __future__ import annotations

import argparse
import math
from collections.abc import Iterator
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.special import ndtr, ndtri
from scipy.stats import kurtosis, skew

from chan.khandani_lo_book_two import gap, matches
from chan.series import WindowCrossesScaleBreak, vintage_line
from chan.tu_momentum import (
    HOLD_DAYS,
    LOOKBACK,
    SCRIPT_GAUSSIAN_STATISTIC,
    gaussian_statistic,
    market_returns,
    positions,
    read_sources,
    signals,
    strategy_returns,
)
from chan.vintage import VintageEntry, VintageUnavailable

#: The declared seeds, each through ``np.random.default_rng``.
RETURNS_SEED = 20261010
TRADES_SEED = 20261011
#: L45's 10,000 simulated return series and L83's 100,000 shuffles.
RETURNS_DRAWS = 10_000
TRADES_DRAWS = 100_000
#: How many draws of the as-written third test run. Its count is 0 by construction.
AS_WRITTEN_DRAWS = 10
#: Draws computed at once. Batching changes no figure, which a test holds.
RETURNS_BATCH = 1_000
TRADES_BATCH = 2_000
#: Points of the θ grid the type IV inverse CDF interpolates on.
GRID_POINTS = 20_001

#: Location 665 and L77, as printed, without the thousands comma.
BOOK_RANDOMIZED_RETURNS_COUNT = "1166"
SCRIPT_RANDOMIZED_RETURNS_P_VALUE = "0.027500"
#: Location 672, "not a single sample out of 100,000".
BOOK_RANDOMIZED_TRADES_COUNT = "0"
#: The N each printed count is out of.
BOOK_RETURNS_DRAWS = 10_000
BOOK_TRADES_DRAWS = 100_000


@dataclass(frozen=True)
class Moments:
    """L43's four moments: the mean, the n − 1 ``std``, and biased skewness and kurtosis."""

    mean: float
    std: float
    skewness: float
    kurtosis: float


def script_moments(market: ArrayLike) -> Moments:
    """``{mean, std, skewness, kurtosis}`` of ``market`` under MATLAB's defaults."""
    x = np.asarray(market, dtype=float)
    return Moments(
        mean=float(x.mean()),
        std=float(x.std(ddof=1)),
        skewness=float(skew(x, bias=True)),
        kurtosis=float(kurtosis(x, fisher=False, bias=True)),
    )


@dataclass(frozen=True)
class PearsonIV:
    """Heinrich's parameters, the density ``[1 + ((x − λ)/a)²]^(−m)·exp(−ν·atan((x − λ)/a))``."""

    m: float
    nu: float
    a: float
    lam: float


def _kappa(skewness: float, kurtosis: float) -> float:
    """Pearson's κ from β₁ = skewness² and β₂ = kurtosis. Type IV is 0 < κ < 1."""
    b1, b2 = skewness * skewness, kurtosis
    return b1 * (b2 + 3) ** 2 / (4 * (4 * b2 - 3 * b1) * (2 * b2 - 3 * b1 - 6))


def pearson_iv_parameters(mean: float, std: float, skewness: float, kurtosis: float) -> PearsonIV:
    """The type IV distribution with these four moments, refusing moments of another type.

    Kurtosis is not in excess form, so a normal distribution's is 3.
    """
    b1, b2 = skewness * skewness, kurtosis
    denominator = 2 * b2 - 3 * b1 - 6
    kappa = _kappa(skewness, kurtosis) if denominator and 4 * b2 != 3 * b1 else math.nan
    if not 0 < kappa < 1:
        raise ValueError(
            f"a skewness of {skewness:g} and a kurtosis of {kurtosis:g} give a Pearson κ of "
            f"{kappa:g}, outside type IV's 0 < κ < 1, and no other type is drawn here"
        )
    r = 6 * (b2 - b1 - 1) / denominator
    root = math.sqrt(16 * (r - 1) - b1 * (r - 2) ** 2)
    return PearsonIV(
        m=(r + 2) / 2,
        nu=-r * (r - 2) * skewness / root,
        a=std * root / 4,
        lam=mean - (r - 2) * skewness * std / 4,
    )


@lru_cache(maxsize=4)
def _theta_cdf(m: float, nu: float) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """The CDF of θ = atan((x − λ)/a), whose density is ``cos(θ)^(2m − 2)·exp(−νθ)``.

    That density is bounded and smooth on (−π/2, π/2) for m > 1, so a
    trapezoid rule on an even grid integrates it accurately.
    """
    theta = np.linspace(-math.pi / 2, math.pi / 2, GRID_POINTS)
    with np.errstate(divide="ignore"):
        log_density = (2 * m - 2) * np.log(np.cos(theta)) - nu * theta
    density = np.exp(log_density - log_density[np.isfinite(log_density)].max())
    density[0] = density[-1] = 0.0
    cdf = np.concatenate([[0.0], np.cumsum((density[1:] + density[:-1]) / 2)])
    return cdf / cdf[-1], theta


def pearson_iv_draws(params: PearsonIV, uniforms: ArrayLike) -> NDArray[np.float64]:
    """Map uniforms through the type IV inverse CDF, interpolated in θ."""
    cdf, theta = _theta_cdf(params.m, params.nu)
    return params.lam + params.a * np.tan(np.interp(np.asarray(uniforms, dtype=float), cdf, theta))


def _daily(
    longs: NDArray[np.bool_],
    shorts: NDArray[np.bool_],
    market: NDArray[np.float64],
    hold_days: int,
) -> NDArray[np.float64]:
    """:func:`~chan.tu_momentum.positions`, then ``strategy_returns``, on every row at once.

    Row t of the positions adds the signals of rows t − hold_days + 1 to t,
    which is a running sum less the sum ``hold_days`` rows back. The return is
    yesterday's position times today's market return, divided by
    ``hold_days``, in that order, with the first row 0.
    """
    signal = longs.astype(np.int64) - shorts.astype(np.int64)
    running = np.cumsum(signal, axis=-1)
    held = running.copy()
    held[..., hold_days:] -= running[..., :-hold_days]
    rows = np.broadcast_shapes(held.shape, market.shape)
    daily = np.zeros(rows)
    daily[..., 1:] = held[..., :-1].astype(float) * market[..., 1:] / hold_days
    return daily


def simulated_strategy_returns(
    simulated: ArrayLike, lookback: int = LOOKBACK, hold_days: int = HOLD_DAYS
) -> NDArray[np.float64]:
    """L47 to L69 for each row of ``simulated``: the strategy rerun on ``cl_sim``.

    ``cl_sim = cumprod(1 + r) − 1``, its signals compare each row with the one
    ``lookback`` back, and the return earns the simulated returns themselves.
    """
    sim = np.asarray(simulated, dtype=float)
    cl_sim = np.cumprod(1 + sim, axis=-1) - 1
    longs = np.zeros(sim.shape, dtype=bool)
    shorts = np.zeros(sim.shape, dtype=bool)
    longs[..., lookback:] = cl_sim[..., lookback:] > cl_sim[..., :-lookback]
    shorts[..., lookback:] = cl_sim[..., lookback:] < cl_sim[..., :-lookback]
    return _daily(longs, shorts, sim, hold_days)


def fixed_position_returns(
    held: ArrayLike, simulated: ArrayLike, hold_days: int = HOLD_DAYS
) -> NDArray[np.float64]:
    """The first row beside the replication: the observed positions on each simulated row."""
    sim = np.asarray(simulated, dtype=float)
    daily = np.zeros(sim.shape)
    daily[..., 1:] = np.asarray(held, dtype=float)[:-1] * sim[..., 1:] / hold_days
    return daily


def permuted_strategy_returns(
    longs: ArrayLike,
    shorts: ArrayLike,
    permutations: ArrayLike,
    market: ArrayLike,
    hold_days: int = HOLD_DAYS,
) -> NDArray[np.float64]:
    """The corrected third test for each row of ``permutations``, earning the observed returns."""
    order = np.asarray(permutations)
    return _daily(
        np.asarray(longs, dtype=bool)[order],
        np.asarray(shorts, dtype=bool)[order],
        np.asarray(market, dtype=float),
        hold_days,
    )


def _batches(total: int, batch: int) -> Iterator[int]:
    if batch < 1:
        raise ValueError(f"a batch holds at least 1 draw, not {batch}")
    for start in range(0, total, batch):
        yield min(batch, total - start)


@dataclass(frozen=True)
class RandomizedReturns:
    """The second test and the three rows beside it, as each draw's mean strategy return.

    ``draw_mean`` and ``draw_std`` are the pooled sample moments of every
    declared draw, the check the sampler gets on its mean and ``std``.
    """

    declared: NDArray[np.float64]
    observed_positions: NDArray[np.float64]
    normal: NDArray[np.float64]
    mean_zero: NDArray[np.float64]
    draw_mean: float
    draw_std: float


def randomized_returns(
    moments: Moments,
    held: ArrayLike,
    draws: int = RETURNS_DRAWS,
    seed: int = RETURNS_SEED,
    batch: int = RETURNS_BATCH,
    length: int = 2_000,
) -> RandomizedReturns:
    """Draw ``draws`` series of ``length`` uniforms in order and run all four rows on them."""
    params = pearson_iv_parameters(moments.mean, moments.std, moments.skewness, moments.kurtosis)
    rng = np.random.default_rng(seed)
    out: dict[str, list[NDArray[np.float64]]] = {
        "declared": [],
        "observed_positions": [],
        "normal": [],
        "mean_zero": [],
    }
    total = total_squares = 0.0
    for rows in _batches(draws, batch):
        uniforms = rng.random((rows, length))
        simulated = pearson_iv_draws(params, uniforms)
        total += float(simulated.sum())
        total_squares += float(np.square(simulated).sum())
        out["declared"].append(simulated_strategy_returns(simulated).mean(axis=1))
        out["observed_positions"].append(fixed_position_returns(held, simulated).mean(axis=1))
        normal = moments.mean + moments.std * ndtri(uniforms)
        out["normal"].append(simulated_strategy_returns(normal).mean(axis=1))
        out["mean_zero"].append(simulated_strategy_returns(simulated - moments.mean).mean(axis=1))
    count = draws * length
    draw_mean = total / count
    return RandomizedReturns(
        **{name: np.concatenate(means) for name, means in out.items()},
        draw_mean=draw_mean,
        draw_std=math.sqrt((total_squares - count * draw_mean**2) / (count - 1)),
    )


def randomized_trades(
    longs: ArrayLike,
    shorts: ArrayLike,
    market: ArrayLike,
    draws: int = TRADES_DRAWS,
    seed: int = TRADES_SEED,
    batch: int = TRADES_BATCH,
) -> NDArray[np.float64]:
    """The corrected third test: each draw's mean return, one permutation per draw in order."""
    rng = np.random.default_rng(seed)
    n = len(np.asarray(longs))
    means = []
    for rows in _batches(draws, batch):
        order = np.stack([rng.permutation(n) for _ in range(rows)])
        means.append(permuted_strategy_returns(longs, shorts, order, market).mean(axis=1))
    return np.concatenate(means)


@dataclass(frozen=True)
class AsWritten:
    """L82 to L113 as the script writes them, for a few draws.

    ``largest_return`` is the largest ``|ret_sim|`` over every draw, and
    ``positions_after`` is ``pos`` once the loop has added every draw's
    shuffled tranches to it.
    """

    means: NDArray[np.float64]
    largest_return: float
    positions_after: NDArray[np.float64]


def randomized_trades_as_written(
    longs: ArrayLike,
    shorts: ArrayLike,
    held: ArrayLike,
    market: ArrayLike,
    draws: int = AS_WRITTEN_DRAWS,
    seed: int = TRADES_SEED,
) -> AsWritten:
    """The third test's loop line for line, through :mod:`chan.tu_momentum`'s functions."""
    rng = np.random.default_rng(seed)
    long_signal = np.asarray(longs, dtype=bool)
    short_signal = np.asarray(shorts, dtype=bool)
    pos = np.array(held, dtype=float)
    means, largest = [], 0.0
    for _ in range(draws):
        order = rng.permutation(len(long_signal))  # L84
        longs_sim, shorts_sim = long_signal[order], short_signal[order]  # L85, L86
        pos_sim = np.zeros(len(long_signal))  # L88
        pos += positions(longs_sim, shorts_sim, HOLD_DAYS)  # L90 to L101 add to pos
        ret_sim = strategy_returns(pos_sim, market, HOLD_DAYS)  # L103 to L105
        means.append(float(ret_sim.mean()))
        largest = max(largest, float(np.abs(ret_sim).max()))
    return AsWritten(np.array(means), largest, pos)


def landing_band(printed_proportion: float, draws: int) -> tuple[int, int]:
    """The counts within two binomial standard errors of ``printed_proportion · draws``."""
    centre = printed_proportion * draws
    spread = 2 * math.sqrt(draws * printed_proportion * (1 - printed_proportion))
    return math.ceil(centre - spread), math.floor(centre + spread)


#: The declaration's three bands, for rows 2, 3 and 4.
BOOK_RETURNS_BAND = landing_band(
    int(BOOK_RANDOMIZED_RETURNS_COUNT) / BOOK_RETURNS_DRAWS, RETURNS_DRAWS
)
SCRIPT_RETURNS_BAND = landing_band(float(SCRIPT_RANDOMIZED_RETURNS_P_VALUE), RETURNS_DRAWS)
BOOK_TRADES_BAND = landing_band(int(BOOK_RANDOMIZED_TRADES_COUNT) / BOOK_TRADES_DRAWS, TRADES_DRAWS)


def count_at_or_above(means: ArrayLike, observed: float) -> int:
    """L71 and L108: how many simulated means are at or above the observed mean."""
    return int(np.count_nonzero(np.asarray(means) >= observed))


def band_verdict(count: int, band: tuple[int, int]) -> str:
    """Declaration 5: inside the band reproduced, outside it did not."""
    low, high = band
    return "reproduced" if low <= count <= high else "did not reproduce"


@dataclass(frozen=True)
class HypothesisTests:
    """Every row of the run on one series of TU's closes."""

    daily: NDArray[np.float64]
    moments: Moments
    statistic: float
    returns: RandomizedReturns
    trades: NDArray[np.float64]
    as_written: AsWritten

    @property
    def observed_mean(self) -> float:
        return float(self.daily.mean())

    def count(self, means: ArrayLike) -> int:
        return count_at_or_above(means, self.observed_mean)


def hypothesis_tests(closes: ArrayLike) -> HypothesisTests:
    """Run the three tests and the rows beside them on TU's closes."""
    cl = np.asarray(closes, dtype=float)
    market = market_returns(cl)
    longs, shorts = signals(cl, LOOKBACK)
    held = positions(longs, shorts, HOLD_DAYS)
    daily = strategy_returns(held, market, HOLD_DAYS)
    moments = script_moments(market)
    return HypothesisTests(
        daily=daily,
        moments=moments,
        statistic=gaussian_statistic(daily),
        returns=randomized_returns(moments, held, length=len(cl)),
        trades=randomized_trades(longs, shorts, market),
        as_written=randomized_trades_as_written(longs, shorts, held, market),
    )


def report(entry: VintageEntry, result: HypothesisTests) -> None:
    """Print the vintage, the five rows with their verdicts, and the three rows beside them."""
    returns_count = result.count(result.returns.declared)
    trades_count = result.count(result.trades)
    as_written_count = result.count(result.as_written.means)
    print("Three hypothesis tests on TU momentum, Algorithmic Trading's Example 1.1")
    print(f"  vintage  {vintage_line(entry)}")
    print(
        f"  rule     Example 6.1's, {LOOKBACK} days back and {HOLD_DAYS} held, observed mean "
        f"daily return {result.observed_mean:.6e}"
    )
    print(
        f"  seeds    {RETURNS_SEED} for the randomized returns, {TRADES_SEED} for the "
        "randomized trades"
    )
    print()
    print(f"  {'Row':<46} {'Computed':>14}  {'Chan':>9}  {'Lands on':>14}  Verdict")
    statistic_verdict = (
        "reproduced"
        if matches(result.statistic, SCRIPT_GAUSSIAN_STATISTIC)
        else f"did not reproduce, gap {gap(result.statistic, SCRIPT_GAUSSIAN_STATISTIC):+g}"
    )
    print(
        f"  {'1 Gaussian statistic, mean/std*sqrt(n)':<46} {result.statistic:>14.6f}  "
        f"{SCRIPT_GAUSSIAN_STATISTIC:>9}  {'2.93 printed':>14}  {statistic_verdict}"
    )
    rows = [
        (
            f"2 Randomized returns, count of {RETURNS_DRAWS}",
            f"{returns_count}",
            BOOK_RANDOMIZED_RETURNS_COUNT,
            BOOK_RETURNS_BAND,
            returns_count,
        ),
        (
            "3 Randomized returns, p-value",
            f"{returns_count / RETURNS_DRAWS:.6f}",
            SCRIPT_RANDOMIZED_RETURNS_P_VALUE,
            SCRIPT_RETURNS_BAND,
            returns_count,
        ),
        (
            f"4 Randomized trades, corrected, of {TRADES_DRAWS}",
            f"{trades_count}",
            BOOK_RANDOMIZED_TRADES_COUNT,
            BOOK_TRADES_BAND,
            trades_count,
        ),
    ]
    for label, computed, printed, (low, high), count in rows:
        print(
            f"  {label:<46} {computed:>14}  {printed:>9}  {f'{low} to {high}':>14}  "
            f"{band_verdict(count, (low, high))}"
        )
    print(
        f"  {f'5 Randomized trades, as written, of {AS_WRITTEN_DRAWS}':<46} "
        f"{as_written_count:>14}  {BOOK_RANDOMIZED_TRADES_COUNT:>9}  {'n/a':>14}  "
        f"none, a finding: ret_sim is 0 on every draw, largest |ret_sim| "
        f"{result.as_written.largest_return:g}"
    )
    print()
    print(f"  The one-sided normal tail of row 1's statistic is {ndtr(-result.statistic):.6f}.")
    print(
        f"  The declared draws have a pooled mean of {result.returns.draw_mean:.6e} and a std of "
        f"{result.returns.draw_std:.6e}, against {result.moments.mean:.6e} and "
        f"{result.moments.std:.6e}."
    )
    print()
    print(
        "Beside the replication, added after the scratch run saw results. Each varies one input on"
    )
    print(f"  seed {RETURNS_SEED}'s uniforms, and none carries a verdict.")
    low, high = SCRIPT_RETURNS_BAND
    for label, means in (
        ("the observed positions on the simulated returns", result.returns.observed_positions),
        ("a normal draw with TU's mean and std", result.returns.normal),
        ("Pearson type IV with the mean set to zero", result.returns.mean_zero),
    ):
        found = result.count(means)
        inside = "inside" if low <= found <= high else "outside"
        print(
            f"  {label:<48} {found:>6} of {RETURNS_DRAWS}, {found / RETURNS_DRAWS:.6f}, "
            f"{inside} the script's {low} to {high}"
        )
    print()
    print("  Exploratory. docs/replication-log.md Entry 37 carries the verdicts.")


def run(data_dir: Path | None = None) -> HypothesisTests:
    """Read TU, guard it, run every row, and print the report."""
    entry, closes = read_sources(data_dir)
    result = hypothesis_tests(closes.to_numpy(dtype=float))
    report(entry, result)
    return result


def main() -> None:
    argparse.ArgumentParser(
        description="Three hypothesis tests on TU momentum, Example 1.1 of Algorithmic Trading"
    ).parse_args()
    try:
        run()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day reaches the reader
        # as one line, the way chan.tu_momentum.main does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
