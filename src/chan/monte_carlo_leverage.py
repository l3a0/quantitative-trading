"""Monte Carlo leverage, historical optimization and CPPI, *Algorithmic Trading*'s Boxes 8.1 to 8.6.

A leverage that maximizes growth can still bring a drawdown near total loss.
Chapter 8, at Kindle locations 3319 to 3438, makes that case on Example 5.1's
AUD.CAD returns three ways. It fits a Pearson distribution to their first four
moments, draws 100,000 returns from it and finds the leverage that maximizes
the simulated growth rate. It finds the same leverage on the historical
returns. And it shows that constant proportion portfolio insurance (CPPI),
which trades only a slice of the account and refills that slice at each new
high, keeps the drawdown above a set floor at almost no cost in growth.

**The transcription.** ``monteCarloOptimLeverage.m`` was read in the mirror
[ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) at
``e4bc46f``, under ``public/img/book2/``, git blob ``fc32599``, and landed here
for [issue 360](https://github.com/l3a0/quantitative-trading/issues/360). Line
numbers are the script's.

1. Line 3 loads ``ret`` from ``AUDCAD_unequal_ret`` with no slicing. That is
   Example 5.1's 612 saved returns, read here through
   :func:`chan.series.load_returns`.
2. Lines 5 and 6 take ``{mean, std, skewness, kurtosis}`` on MATLAB's
   defaults, which :func:`chan.tu_hypothesis_tests.script_moments` computes,
   and call ``pearsrnd(..., 100000, 1)``.
3. Line 8's growth rate is ``sum(log(1+f*R))/length(R)``, which is
   :func:`growth`. Line 22 searches it with ``fminbnd(minusGsim, 0, 20)``, so
   the simulated optimum is capped at 20.
4. Lines 28 to 38 print ``calculateMaxDD(cumprod(1+k*R)-1)`` at the optimum,
   half of it and a seventh of it on the draws, and at the optimum over 1.4 on
   the historical returns.
5. Lines 41 to 66 set D = 0.5 and print the growth and drawdown of the whole
   account at ``f·D`` and Box 8.6's CPPI loop, on the draws and on the
   historical returns.

**Three things the script does not do.**

1. It never computes the Kelly leverage. ``AUDCAD_unequal.m`` does, as
   ``mean / std²``, and :mod:`chan.aud_cad_johansen` pins its 23.845328.
2. It never runs Box 8.4's historical optimization. ``minusG`` is defined on
   line 19 and only evaluated at ``optimalF·D``. :func:`optimal_leverage` on
   the saved returns is that box.
3. Its second CPPI loop, on the historical returns, reads ``r(t)`` on line 73,
   which nothing defines. The script opens with ``clear``, so MATLAB stops
   there. The book quotes no figure from it, and :class:`Historical` reads
   ``ret`` for ``r``, which is what line 75 of the same loop reads.

**The draws.** ``pearsrnd`` picks a Pearson type from the four moments.
Location 3342 says the type is 4, and Pearson's κ on these moments is inside
type IV's 0 < κ < 1, so :func:`chan.tu_hypothesis_tests.pearson_iv_draws` draws
from type IV, as it does for Example 1.1. Seed s's draws are
``pearson_iv_draws(params, default_rng(s).random(100_000))``. The draw method
is part of what a seed means, so it is stated here. The fitted type IV has
m = 3.2547, so its moments exist only below order 5.51. A draw's sample
skewness then has infinite variance, so the tests check the fitted density's
tail and the draws' mean and std rather than a draw's third and fourth moments.

**The search.** :func:`optimal_leverage` runs ``scipy.optimize.minimize_scalar``
with the bounded method, which is Brent's method as ``fminbnd`` runs it, over
``(0, min(20, ruin))``. The ruin leverage is one over the size of the most
negative return. At or above it some day loses everything, MATLAB would take
the real part of a complex logarithm, and :func:`growth` refuses instead. So a
seed whose ruin leverage is below 20 is searched only up to it, and the report
counts how many seeds that touches.

**The declaration.** Issue 360 fixed these before any draw on its seeds.
Scratch runs on other seeds had seen results.

1. The declared seed is :data:`SEED`, 20261012, and every seeded figure is
   computed on its draws.
2. The ensemble is the 200 seeds :data:`ENSEMBLE_SEEDS`, 20261013 to 20261212.
3. A simulated figure lands when the book's value lies within the ensemble's
   5th to 95th percentile of the same quantity, numpy's default linear
   interpolation. Row 5 uses the exact distribution of the minimum instead,
   :func:`minimum_below`.
4. A claim row is judged by the criterion written in its row. One that names
   no seed is judged on the declared seed, and the report gives the share of
   seeds on which it holds.
5. A simulated figure outside its band did not reproduce. One inside its band
   whose seeded value differs is reproduced with a gap, and the gap's cause is
   the seed, since location 3399 says the draws are not reproducible.

**Row 3's rule changed after the ensemble was seen.** The declaration judged
row 3 against the uncapped optimum's band across all 200 seeds. Chan's 19.2
sits below his cap of 20, so his uncapped optimum was 19.2 as well, and the
declaration set the capped band aside because its lower tail is made of seeds
whose low ruin leverage holds the optimum down. The uncapped band shares those
seeds. A seed whose most negative draw is deep has a low ruin leverage, and
the growth rate falls to minus infinity at the ruin leverage, so the uncapped
optimum sits below it too. The two bands' 5th percentiles are the same seed's
optimum. So the declared rule applies the clamping objection to one band and
not the other. Row 3 is now judged against :func:`optimum_band`, the uncapped
optimum across the seeds whose ruin leverage is above the book's 30.2, which
are the seeds whose most negative draw is no deeper than Chan's. The report
prints the declared band and its verdict beside it, and the change is
exploratory like everything else here.

**Two CPPI forms run, because the script's loop is not the prose's scheme.**
Location 3426 sets aside D of the account, trades that subaccount at leverage
f, and refills it to D of the account at each new high, so the account can
never fall more than D below its high. Box 8.6's loop, lines 46 to 59, scales
``D·f`` by ``1 + dd``, where ``dd`` is the drawdown of the unlevered returns
rather than of the account. Location 3438 says CPPI's drawdown is "by design"
less than 0.5, and only the prose's form guarantees that.
:func:`cppi_as_scripted` and :func:`cppi_as_described` compute each without a
loop, because each reduces to a random walk reflected at zero, and
:func:`cppi_as_scripted_loop` and :func:`cppi_as_described_loop` are the loops
the tests hold them to. All four refuse a NaN return. The scripted pair also
refuses a return at or below −1, and the described pair a leverage that turns
the worst return into a loss of the whole subaccount. Past those points
neither form computes an account, and the scripted loop and its twin give
different answers.

**The 18.4 gap.** Location 3342 gives a Kelly leverage of 18.4 for these
returns and location 3379 the same historical optimum. On Chan's own saved
returns the Kelly is 23.845328 and the historical optimum 23.721773, so the
vintage explanation is spent and both rows did not reproduce. Row group 13
holds the evidence for where 18.4 came from.

1. :func:`implied_kelly_band` puts the Kelly of any daily series matching
   Example 5.1's printed Sharpe ratio of 1.6 and APR of 11 percent, across
   their rounding, between 21.56 and 26.76, when the APR compounds the log
   growth ``m − σ²/2``. Compounding ``1 + m`` exactly moves the lower edge to
   22.07, and the simple ``252·m`` moves it to 20.89, so the edge depends on
   how the book annualized. None of the three reaches 18.4.
2. The ensemble rerun with the draws' mean moved so that the Kelly is 18.4,
   which moves only λ, puts the median uncapped optimum at 18.470198 and
   lands four of the five simulated rows it reruns, row 3 under both its
   declared band and :func:`optimum_band`. Only the drawdown at half the
   optimum still misses.

The evidence favors Chapter 8 having run on an older ``ret`` whose Kelly was
near 18.4, which neither mirror holds and which disagrees with Example 5.1's
printed figures. That is an inference, not a held vintage.

No sibling code was ported. The sibling's ``kelly_fraction`` searches the same
growth rate on a grid too coarse to pin an optimum, and the sampler and the
drawdown come from this repo's own modules.

Every result here is exploratory. Reproducing Chan's figures spends his 612
returns on a method he chose. The run says whether his numbers reproduce on his
file, and nothing about whether any leverage is safe to trade.

:mod:`chan.monte_carlo_leverage_figures` draws the figure for the post on this
entry. It reads the fit through :func:`pearson_fit` and each day's drawdown
through :func:`account_drawdowns`, the same functions the run uses, so the
figure and the run cannot drift apart.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy import integrate
from scipy.optimize import minimize_scalar

from chan.aud_cad_johansen import BOOK_APR_PERCENT, BOOK_SHARPE, SAVED_RETURNS
from chan.khandani_lo import TRADING_DAYS
from chan.khandani_lo_book_two import gap, matches
from chan.matlab_helpers import calculate_max_dd, drawdown_path
from chan.series import load_returns, vintage_line
from chan.tu_hypothesis_tests import (
    Moments,
    PearsonIV,
    pearson_iv_draws,
    pearson_iv_parameters,
    pearson_kappa,
    script_moments,
)
from chan.vintage import VintageEntry, VintageUnavailable

#: The declared seed and the ensemble, each through ``np.random.default_rng(s).random(DRAWS)``.
SEED = 20261012
ENSEMBLE_SEEDS = tuple(range(20261013, 20261213))
#: ``pearsrnd(..., 100000, 1)``, script line 6.
DRAWS = 100_000
#: ``fminbnd(minusGsim, 0, 20)``, script line 22.
CAP = 20.0
#: ``D=0.5``, script line 41, and location 3438's maximum drawdown allowed.
D = 0.5
#: The tolerance handed to the bounded search.
XATOL = 1e-10
#: A simulated figure lands inside this percentile band of the ensemble.
BAND = (5.0, 95.0)
#: Row 7's criterion: the historical optimum and the Kelly within 1 percent.
EQUAL_WITHIN = 0.01
#: Row 11's criterion: the two growth rates within 2 percent on the declared seed.
SIMILAR_WITHIN = 0.02

#: Location 3342.
BOOK_KELLY = "18.4"
BOOK_TYPE = 4
BOOK_OPTIMUM_FMINBND = "19"
BOOK_MINIMUM = "-0.0331"
BOOK_RUIN = "30.2"
#: Location 3379.
BOOK_HISTORICAL = "18.4"
#: Location 3399.
BOOK_OPTIMUM = "19.2"
BOOK_DRAWDOWN_OPTIMUM = "-0.999"
BOOK_DRAWDOWN_HALF = "-0.963"
BOOK_DRAWDOWN_SEVENTH = "-0.5"
BOOK_SEVENTH_LEVERAGE = "2.7"
#: Location 3438.
BOOK_CPPI_GROWTH = "0.002484"
BOOK_FULL_GROWTH = "0.002525"
BOOK_FULL_DRAWDOWN = "-0.9"


def rounding_band(printed: str, scale: float = 1.0) -> tuple[float, float]:
    """Half a unit of ``printed``'s last digit either side of it, times ``scale``."""
    half = 0.5 * 10.0 ** -len(printed.partition(".")[2])
    return (float(printed) - half) * scale, (float(printed) + half) * scale


#: The rounding bands of Example 5.1's printed Sharpe ratio and APR in percent, location 2237.
SHARPE_BAND = rounding_band(BOOK_SHARPE)
APR_BAND = rounding_band(BOOK_APR_PERCENT, scale=0.01)


def ruin_leverage(returns: ArrayLike) -> float:
    """One over the size of the most negative return, which loses everything on that day.

    A series with no negative return has no ruin leverage, and this is infinite.
    """
    lowest = float(np.min(returns))
    return math.inf if lowest >= 0 else -1 / lowest


def growth(leverage: float, returns: ArrayLike) -> float:
    """Box 8.2's ``g``: the mean of ``log(1 + f·R)``, the growth per bar at leverage ``f``.

    At or above the ruin leverage one day's ``1 + f·R`` is zero or negative, so
    there is no real growth rate, and this refuses rather than return MATLAB's
    real part of a complex logarithm.
    """
    values = np.asarray(returns, dtype=float)
    ruin = ruin_leverage(values)
    if leverage >= ruin:
        raise ValueError(
            f"a leverage of {leverage:g} is at or above the ruin leverage {ruin:g}, "
            "so some day loses everything and the growth rate is not a real number"
        )
    return float(np.mean(np.log1p(leverage * values)))


def optimal_leverage(returns: ArrayLike, cap: float = math.inf) -> float:
    """The leverage that maximizes :func:`growth`, by Brent's bounded search as ``fminbnd`` runs it.

    The search runs over ``(0, min(cap, ruin))``. The script's cap is 20. A
    search capped below the optimum returns the cap, within the search's
    tolerance. With no cap and no negative return the growth rate rises
    without limit, so there is no optimum and this refuses.
    """
    values = np.asarray(returns, dtype=float)
    upper = min(cap, ruin_leverage(values))
    if math.isinf(upper):
        raise ValueError("with no negative return and no cap, growth rises with leverage forever")
    found = minimize_scalar(
        lambda f: -growth(f, values),
        bounds=(0.0, upper),
        method="bounded",
        options={"xatol": XATOL},
    )
    return float(found.x)


def max_drawdown(account: ArrayLike) -> float:
    """The deepest drawdown ``calculateMaxDD(cumprod(1 + a) − 1)`` gives for daily returns ``a``."""
    return calculate_max_dd(np.cumprod(1 + np.asarray(account, dtype=float)) - 1)[0]


def account_drawdowns(account: ArrayLike) -> NDArray[np.float64]:
    """Each day's drawdown of ``cumprod(1 + a) − 1``, through ``calculateMaxDD``'s loop.

    :func:`max_drawdown` is the least of these. The first day's drawdown is 0
    whatever it returned, a quirk of Chan's loop that
    :func:`chan.matlab_helpers.drawdown_path` keeps.
    """
    return drawdown_path(np.cumprod(1 + np.asarray(account, dtype=float)) - 1)[1]


def _cppi_returns(returns: ArrayLike, scale: float, empties: str) -> NDArray[np.float64]:
    """The returns as floats, refused when one is NaN or when ``scale·R`` reaches −1 on some day."""
    values = np.asarray(returns, dtype=float)
    if np.isnan(values).any():
        raise ValueError("a NaN return leaves the CPPI account undefined from that day on")
    if values.size and scale * float(np.min(values)) <= -1:
        raise ValueError(empties)
    return values


def _scripted_returns(returns: ArrayLike) -> NDArray[np.float64]:
    return _cppi_returns(
        returns, 1.0, "a return at or below -1 empties the unlevered drawdown Box 8.6 tracks"
    )


def _described_returns(returns: ArrayLike, leverage: float) -> NDArray[np.float64]:
    return _cppi_returns(
        returns, leverage, f"a leverage of {leverage:g} empties the subaccount on its worst day"
    )


def cppi_as_scripted(returns: ArrayLike, leverage: float, d: float = D) -> NDArray[np.float64]:
    """Box 8.6's loop, as the account's daily returns, computed without the loop.

    Day ``t`` earns ``R(t)·D·f·(1 + dd)``, where ``dd`` is the drawdown of the
    unlevered returns through the day before, ``min(0, (1 + dd)·(1 + R) − 1)``.
    ``log(1 + dd)`` is the running sum of ``log(1 + R)`` less its running
    maximum, floored at zero, which is a random walk reflected at zero, so the
    loop needs no loop. :func:`cppi_as_scripted_loop` is the loop it is held to.

    A NaN return, or one at or below −1, is refused. Past −1 the logarithm has
    no real value while the loop carries a drawdown below −1, so the two would
    disagree.
    """
    values = _scripted_returns(returns)
    walk = np.cumsum(np.log1p(values))
    level = walk - np.maximum.accumulate(np.maximum(walk, 0.0))
    before = np.concatenate([[0.0], level[:-1]])
    return values * d * leverage * np.exp(before)


def cppi_as_scripted_loop(returns: ArrayLike, leverage: float, d: float = D) -> NDArray[np.float64]:
    """Box 8.6's loop as the script writes it, lines 46 to 59, one day at a time.

    It refuses what :func:`cppi_as_scripted` refuses.
    """
    values = _scripted_returns(returns)
    account = np.empty_like(values)
    drawdown = 0.0
    for t, r in enumerate(values):
        account[t] = r * d * leverage * (1 + drawdown)
        drawdown = min(0.0, (1 + drawdown) * (1 + r) - 1)
    return account


def cppi_as_described(returns: ArrayLike, leverage: float, d: float = D) -> NDArray[np.float64]:
    """Location 3426's CPPI, as the account's daily returns, computed without a loop.

    The account starts at 1 with ``D`` in a trading subaccount and ``1 − D`` in
    cash. The subaccount earns ``f·R`` each day. When the account reaches a new
    high, the subaccount is reset to ``D`` of it, so the cash is always ``1 − D``
    of the last high. Between highs the subaccount over ``D`` times the high is
    a running product of ``1 + f·R``, reset to 1 at each new high, so its
    logarithm is a random walk reflected at zero, as in
    :func:`cppi_as_scripted`. The account is then ``high·(1 − D + D·y)``, and a
    new high multiplies the high by ``1 − D + D·y`` with ``y`` above 1.
    :func:`cppi_as_described_loop` is the loop it is held to.

    While ``f·min R > −1`` the subaccount never reaches zero, so the account's
    drawdown stays above ``−D``. At or past that this refuses, and so it does
    on a NaN return.
    """
    values = _described_returns(returns, leverage)
    walk = np.cumsum(np.log1p(leverage * values))
    peak_before = np.maximum.accumulate(np.concatenate([[0.0], walk]))[:-1]
    excess = walk - peak_before
    with np.errstate(over="ignore"):
        raised = np.where(excess > 0, np.log((1 - d) + d * np.exp(np.maximum(excess, 0.0))), 0.0)
    log_equity = np.cumsum(raised) + np.log((1 - d) + d * np.exp(np.minimum(excess, 0.0)))
    return np.expm1(np.diff(np.concatenate([[0.0], log_equity])))


def cppi_as_described_loop(
    returns: ArrayLike, leverage: float, d: float = D
) -> NDArray[np.float64]:
    """Location 3426's CPPI one day at a time: cash, a subaccount, and a reset at each new high.

    It refuses what :func:`cppi_as_described` refuses.
    """
    values = _described_returns(returns, leverage)
    account = np.empty_like(values)
    equity = high = 1.0
    sub = d * equity
    for t, r in enumerate(values):
        before = equity
        sub = sub * (1 + leverage * r)
        equity = (1 - d) * high + sub
        if equity > high:
            high = equity
            sub = d * equity
        account[t] = equity / before - 1
    return account


def account_growth(account: ArrayLike) -> float:
    """The growth per bar of an account's daily returns, ``mean(log(1 + a))``."""
    return float(np.mean(np.log1p(np.asarray(account, dtype=float))))


def implied_kelly(sharpe: float, apr: float, days: int = TRADING_DAYS) -> float:
    """The Kelly leverage ``m / σ²`` of a daily series with this Sharpe ratio and compounded APR.

    The Sharpe ratio fixes ``m = S·σ / √days``, and the APR is taken as
    ``exp(days·(m − σ²/2)) − 1``, the compounded growth of a series with these
    moments. Together they give a quadratic in σ, whose smaller root is the
    daily σ of a strategy like Example 5.1's, and the Kelly is then ``S / (√days·σ)``.

    The compounding is a choice the book does not state, and it moves the
    result. Compounding ``1 + m`` exactly, or taking the simple ``days·m``,
    gives the Kelly ``S² / (days·m)`` with a different ``m``, and the tests
    measure how far each moves :func:`implied_kelly_band`.
    """
    per_bar = sharpe / math.sqrt(days)
    log_growth = math.log1p(apr) / days
    sigma = per_bar - math.sqrt(per_bar * per_bar - 2 * log_growth)
    return per_bar / sigma


def implied_kelly_band(
    sharpe: tuple[float, float] = SHARPE_BAND, apr: tuple[float, float] = APR_BAND
) -> tuple[float, float]:
    """The lowest and highest :func:`implied_kelly` over the corners of the two rounding bands.

    The Kelly rises with the Sharpe ratio and falls with the APR inside these
    bands, so the corners are its extremes.
    """
    corners = [implied_kelly(s, a) for s in sharpe for a in apr]
    return min(corners), max(corners)


def lower_tail(params: PearsonIV, x: float) -> float:
    """``F(x)``, the type IV density integrated in θ up to ``x``, by ``scipy.integrate.quad``."""

    def density(theta: float) -> float:
        return math.cos(theta) ** (2 * params.m - 2) * math.exp(-params.nu * theta)

    whole = integrate.quad(density, -math.pi / 2, math.pi / 2, limit=200)[0]
    upper = math.atan((x - params.lam) / params.a)
    return integrate.quad(density, -math.pi / 2, upper, limit=200)[0] / whole


def minimum_below(params: PearsonIV, x: float, draws: int = DRAWS) -> float:
    """The probability that the least of ``draws`` independent draws is at or below ``x``.

    The least exceeds ``x`` only when every draw does, which has probability
    ``(1 − F(x))^draws``.
    """
    return -math.expm1(draws * math.log1p(-lower_tail(params, x)))


@dataclass(frozen=True)
class Simulated:
    """One seed's draws through every simulated row.

    ``optimum`` is capped at :data:`CAP`, as the script's ``fminbnd`` is, and
    every leverage below is a multiple of it. ``uncapped`` searches up to the
    ruin leverage.
    """

    seed: int
    minimum: float
    ruin: float
    optimum: float
    uncapped: float
    drawdown_optimum: float
    drawdown_half: float
    drawdown_seventh: float
    full_growth: float
    full_drawdown: float
    cppi_growth: float
    cppi_drawdown: float
    described_growth: float
    described_drawdown: float

    @property
    def on_the_cap(self) -> bool:
        """Whether the capped search returned the cap because the optimum lies past it."""
        return self.uncapped >= CAP

    @property
    def ruin_below_cap(self) -> bool:
        """Whether the ruin leverage, not the cap, bounded the capped search."""
        return self.ruin < CAP

    @property
    def growth_gap(self) -> float:
        """The full account's growth at ``f·D`` less scripted CPPI's, over the full account's."""
        return (self.full_growth - self.cppi_growth) / self.full_growth


def pearson_fit(returns: ArrayLike) -> tuple[Moments, PearsonIV]:
    """Script lines 5 and 6: the returns' four moments, and the type IV that has them.

    The moments are MATLAB's defaults, through
    :func:`chan.tu_hypothesis_tests.script_moments`, and the parameters come
    from :func:`chan.tu_hypothesis_tests.pearson_iv_parameters`.
    """
    moments = script_moments(np.asarray(returns, dtype=float))
    params = pearson_iv_parameters(moments.mean, moments.std, moments.skewness, moments.kurtosis)
    return moments, params


def draws(params: PearsonIV, seed: int, count: int = DRAWS) -> NDArray[np.float64]:
    """Seed ``s``'s draws: ``pearson_iv_draws(params, default_rng(s).random(count))``."""
    return pearson_iv_draws(params, np.random.default_rng(seed).random(count))


def simulate(params: PearsonIV, seed: int, d: float = D) -> Simulated:
    """Run every simulated row on one seed's draws."""
    sim = draws(params, seed)
    optimum = optimal_leverage(sim, CAP)
    full = optimum * d * sim
    scripted = cppi_as_scripted(sim, optimum, d)
    described = cppi_as_described(sim, optimum, d)
    return Simulated(
        seed=seed,
        minimum=float(sim.min()),
        ruin=ruin_leverage(sim),
        optimum=optimum,
        uncapped=optimal_leverage(sim),
        drawdown_optimum=max_drawdown(optimum * sim),
        drawdown_half=max_drawdown(optimum / 2 * sim),
        drawdown_seventh=max_drawdown(optimum / 7 * sim),
        full_growth=account_growth(full),
        full_drawdown=max_drawdown(full),
        cppi_growth=account_growth(scripted),
        cppi_drawdown=max_drawdown(scripted),
        described_growth=account_growth(described),
        described_drawdown=max_drawdown(described),
    )


@dataclass(frozen=True)
class Band:
    """The ensemble's 5th percentile, median and 95th percentile of one quantity."""

    low: float
    median: float
    high: float

    def holds(self, value: float) -> bool:
        return self.low <= value <= self.high


def band(values: ArrayLike) -> Band:
    """numpy's default linear-interpolation percentiles at :data:`BAND` and the median."""
    low, median, high = np.percentile(np.asarray(values, dtype=float), [BAND[0], 50.0, BAND[1]])
    return Band(float(low), float(median), float(high))


@dataclass(frozen=True)
class Ensemble:
    """Every seed of an ensemble, and each quantity's band across them."""

    runs: tuple[Simulated, ...]

    def values(self, name: str) -> NDArray[np.float64]:
        return np.array([getattr(run, name) for run in self.runs], dtype=float)

    def band(self, name: str) -> Band:
        return band(self.values(name))

    def ruin_above(self, threshold: float) -> Ensemble:
        """The seeds whose ruin leverage is above ``threshold``."""
        return Ensemble(tuple(run for run in self.runs if run.ruin > threshold))


def ensemble(params: PearsonIV, seeds: tuple[int, ...] = ENSEMBLE_SEEDS) -> Ensemble:
    return Ensemble(tuple(simulate(params, seed) for seed in seeds))


def optimum_band(found: Ensemble) -> Band:
    """Row 3's band: the uncapped optimum across the seeds whose ruin leverage is above the book's.

    Chan's run printed a ruin leverage of 30.2, so no draw of his was deeper
    than −0.0331 and nothing held his optimum down. A seed with a deeper draw
    has a lower ruin leverage, and its optimum sits below that, so these are
    the seeds whose optimum the same can be said of.
    """
    return found.ruin_above(float(BOOK_RUIN)).band("uncapped")


@dataclass(frozen=True)
class Historical:
    """The script's lines on the saved returns, with ``f`` the declared seed's capped optimum.

    Line 73 reads ``r(t)``, which nothing defines, and these read ``ret`` for
    it, as the loop's next line does.
    """

    leverage: float
    full_growth: float
    drawdown_over_1_4: float
    full_drawdown: float
    cppi_growth: float
    cppi_drawdown: float
    described_growth: float
    described_drawdown: float


def historical_lines(returns: NDArray[np.float64], leverage: float, d: float = D) -> Historical:
    full = leverage * d * returns
    scripted = cppi_as_scripted(returns, leverage, d)
    described = cppi_as_described(returns, leverage, d)
    return Historical(
        leverage=leverage,
        full_growth=account_growth(full),
        drawdown_over_1_4=max_drawdown(leverage / 1.4 * returns),
        full_drawdown=max_drawdown(full),
        cppi_growth=account_growth(scripted),
        cppi_drawdown=max_drawdown(scripted),
        described_growth=account_growth(described),
        described_drawdown=max_drawdown(described),
    )


def shifted_parameters(moments: Moments, kelly: float = float(BOOK_KELLY)) -> PearsonIV:
    """The type IV with the returns' std, skewness and kurtosis and a mean whose Kelly is ``kelly``.

    The Kelly is ``mean / std²``, so the mean becomes ``kelly·std²``, and only
    λ depends on the mean.
    """
    return pearson_iv_parameters(
        kelly * moments.std**2, moments.std, moments.skewness, moments.kurtosis
    )


@dataclass(frozen=True)
class MonteCarloLeverage:
    """Every row of the replication and every row beside it."""

    entry: VintageEntry
    returns: NDArray[np.float64]
    moments: Moments
    params: PearsonIV
    kappa: float
    kelly: float
    historical: float
    historical_capped: float
    declared: Simulated
    ensemble: Ensemble
    lines: Historical
    minimum_at_or_below_book: float
    ruin_below_cap_exact: float
    kelly_band: tuple[float, float]
    shifted_params: PearsonIV
    shifted: Ensemble


def monte_carlo_leverage(entry: VintageEntry, returns: NDArray[np.float64]) -> MonteCarloLeverage:
    """Run the specification on the saved returns, the declared seed and both ensembles."""
    moments, params = pearson_fit(returns)
    declared = simulate(params, SEED)
    shifted = shifted_parameters(moments)
    return MonteCarloLeverage(
        entry=entry,
        returns=returns,
        moments=moments,
        params=params,
        kappa=pearson_kappa(moments.skewness, moments.kurtosis),
        kelly=float(np.mean(returns) / np.var(returns, ddof=1)),
        historical=optimal_leverage(returns),
        historical_capped=optimal_leverage(returns, CAP),
        declared=declared,
        ensemble=ensemble(params),
        lines=historical_lines(returns, declared.optimum),
        minimum_at_or_below_book=minimum_below(params, float(BOOK_MINIMUM)),
        ruin_below_cap_exact=minimum_below(params, -1 / CAP),
        kelly_band=implied_kelly_band(),
        shifted_params=shifted,
        shifted=ensemble(shifted),
    )


def simulated_verdict(seeded: float, printed: str, landing: bool) -> str:
    """Declaration 5: outside the band did not reproduce, and inside it the seed explains a gap."""
    if not landing:
        return "did not reproduce"
    return "reproduced" if matches(seeded, printed) else "reproduced with a gap, the seed"


def exact_verdict(value: float, printed: str) -> str:
    """A deterministic row: reproduced when ``value`` rounds to ``printed``."""
    if matches(value, printed):
        return "reproduced"
    return f"did not reproduce, gap {gap(value, printed):+g}"


def claim_verdict(holds: bool) -> str:
    """A claim row: reproduced when its criterion holds."""
    return "reproduced" if holds else "did not reproduce"


def lands_in_exact_distribution(probability: float) -> bool:
    """Row 5: a printed minimum lands when its exact percentile is inside :data:`BAND`."""
    return BAND[0] / 100 <= probability <= BAND[1] / 100


@dataclass(frozen=True)
class Row:
    """One printed line: its row number, what it is, both figures, and the verdict."""

    number: str
    label: str
    computed: str
    published: str
    verdict: str


def _band_text(found: Band) -> str:
    return f"band {found.low:.6f} to {found.high:.6f}"


#: Rows 8 to 12's simulated figures: the row, the field of :class:`Simulated`, and the book's.
SIMULATED_ROWS = (
    ("8", "drawdown_optimum", "max drawdown at f", BOOK_DRAWDOWN_OPTIMUM),
    ("9", "drawdown_half", "max drawdown at f / 2", BOOK_DRAWDOWN_HALF),
    ("10", "drawdown_seventh", "max drawdown at f / 7", BOOK_DRAWDOWN_SEVENTH),
    ("11", "cppi_growth", "growth, CPPI as scripted", BOOK_CPPI_GROWTH),
    ("11", "full_growth", "growth, full account at f * D", BOOK_FULL_GROWTH),
    ("12", "full_drawdown", "max drawdown, full account at f * D", BOOK_FULL_DRAWDOWN),
)


def rows(result: MonteCarloLeverage) -> list[Row]:
    """Rows 1 to 12 as the report prints them, each with its verdict."""
    seeded, ens = result.declared, result.ensemble
    optimum = optimum_band(ens)
    conditioned = len(ens.ruin_above(float(BOOK_RUIN)).runs)
    out = [
        Row(
            "1",
            "Kelly leverage, mean / std^2",
            f"{result.kelly:.6f}",
            BOOK_KELLY,
            exact_verdict(result.kelly, BOOK_KELLY),
        ),
        Row(
            "2",
            "Pearson type, a kappa inside (0, 1) is type IV",
            f"{result.kappa:.6f}",
            str(BOOK_TYPE),
            claim_verdict(0 < result.kappa < 1),
        ),
    ]
    for printed in (BOOK_OPTIMUM_FMINBND, BOOK_OPTIMUM):
        out.append(
            Row(
                "3",
                f"uncapped optimum, ruin > {BOOK_RUIN} on {conditioned} seeds, "
                f"{_band_text(optimum)}",
                f"{seeded.uncapped:.6f}",
                printed,
                simulated_verdict(seeded.uncapped, printed, optimum.holds(float(printed))),
            )
        )
    out.append(
        Row(
            "4",
            "the Kelly lies inside row 3's band",
            f"{result.kelly:.6f}",
            "a claim",
            claim_verdict(optimum.holds(result.kelly)),
        )
    )
    ruin_book = minimum_below(result.params, -1 / float(BOOK_RUIN))
    out += [
        Row(
            "5",
            f"most negative draw, P(min <= {BOOK_MINIMUM}) {result.minimum_at_or_below_book:.6f}",
            f"{seeded.minimum:.6f}",
            BOOK_MINIMUM,
            simulated_verdict(
                seeded.minimum,
                BOOK_MINIMUM,
                lands_in_exact_distribution(result.minimum_at_or_below_book),
            ),
        ),
        Row(
            "5",
            f"ruin leverage, P(ruin <= {BOOK_RUIN}) {ruin_book:.6f}",
            f"{seeded.ruin:.6f}",
            BOOK_RUIN,
            simulated_verdict(seeded.ruin, BOOK_RUIN, lands_in_exact_distribution(ruin_book)),
        ),
        Row(
            "6",
            "historical optimum, uncapped",
            f"{result.historical:.6f}",
            BOOK_HISTORICAL,
            exact_verdict(result.historical, BOOK_HISTORICAL),
        ),
        Row(
            "7",
            "historical optimum over the Kelly, less 1, within 1%",
            f"{result.historical / result.kelly - 1:+.6f}",
            "a claim",
            claim_verdict(abs(result.historical / result.kelly - 1) < EQUAL_WITHIN),
        ),
    ]
    for number, name, label, printed in SIMULATED_ROWS:
        found = ens.band(name)
        value = getattr(seeded, name)
        out.append(
            Row(
                number,
                f"{label}, {_band_text(found)}",
                f"{value:.6f}",
                printed,
                simulated_verdict(value, printed, found.holds(float(printed))),
            )
        )
        if name == "drawdown_seventh":
            out.append(
                Row(
                    "10",
                    "the leverage f / 7",
                    f"{seeded.optimum / 7:.6f}",
                    BOOK_SEVENTH_LEVERAGE,
                    "none, it is row 3 over 7",
                )
            )
        if name == "full_growth":
            similar = np.array([run.growth_gap < SIMILAR_WITHIN for run in ens.runs])
            out.append(
                Row(
                    "11",
                    f"within 2% on the declared seed, and on {similar.sum()} of "
                    f"{len(similar)} seeds",
                    f"{seeded.growth_gap:.6f}",
                    "a claim",
                    claim_verdict(seeded.growth_gap < SIMILAR_WITHIN),
                )
            )
    for name, label in (("cppi_drawdown", "as scripted"), ("described_drawdown", "as described")):
        above = ens.values(name) > -D
        out.append(
            Row(
                "12",
                f"CPPI {label} stays above -{D:g}, on {above.sum()} of {len(above)} seeds",
                f"{getattr(seeded, name):.6f}",
                "a claim",
                claim_verdict(bool(above.all())),
            )
        )
    return out


#: Row group 13 reruns these rows under the ensemble whose Kelly is 18.4, after row 3.
SHIFTED_ROWS = (
    ("8", "drawdown_optimum", BOOK_DRAWDOWN_OPTIMUM),
    ("9", "drawdown_half", BOOK_DRAWDOWN_HALF),
    ("10", "drawdown_seventh", BOOK_DRAWDOWN_SEVENTH),
    ("11", "cppi_growth", BOOK_CPPI_GROWTH),
    ("11", "full_growth", BOOK_FULL_GROWTH),
)


def shifted_landings(result: MonteCarloLeverage) -> list[tuple[str, str, Band, bool]]:
    """Row group 13: each row's band under the shifted ensemble, and whether the book's lands.

    Row 3 reads :func:`optimum_band`, as it does in :func:`rows`.
    """
    optimum = optimum_band(result.shifted)
    out = [
        ("3", printed, optimum, optimum.holds(float(printed)))
        for printed in (BOOK_OPTIMUM_FMINBND, BOOK_OPTIMUM)
    ]
    for number, name, printed in SHIFTED_ROWS:
        found = result.shifted.band(name)
        out.append((number, printed, found, found.holds(float(printed))))
    return out


def report(result: MonteCarloLeverage) -> None:
    """Print the vintage, the specification, every row beside the book's figure, and the rest."""
    seeded, ens = result.declared, result.ensemble
    print(
        "Monte Carlo leverage, historical optimization and CPPI on Example 5.1's returns, "
        "Algorithmic Trading's Boxes 8.1 to 8.6"
    )
    print(f"  vintage  {vintage_line(result.entry)}, {len(result.returns)} returns")
    print(
        f"  draws    {DRAWS:,} a seed through the Pearson type IV inverse CDF, declared seed "
        f"{SEED}, ensemble {ENSEMBLE_SEEDS[0]} to {ENSEMBLE_SEEDS[-1]}"
    )
    print(
        f"  search   Brent's bounded search, xatol {XATOL:g}, capped at {CAP:g} as the script "
        f"is, D = {D:g}, bands at the {BAND[0]:g}th and {BAND[1]:g}th percentiles"
    )
    print()
    print(f"  {'Row':<4} {'Figure':<66} {'Computed':>12}  {'Chan':>8}  Verdict")
    for row in rows(result):
        print(
            f"  {row.number:<4} {row.label:<66} {row.computed:>12}  {row.published:>8}  "
            f"{row.verdict}"
        )
    print()
    print("Beside the replication. No book prints these, so none carries a verdict.")
    p = result.params
    print(
        f"  type IV  m {p.m:.6f}, nu {p.nu:.6f}, a {p.a:.6e}, lambda {p.lam:.6e}, "
        f"moments exist below order {2 * p.m - 1:.2f}"
    )
    print(
        f"  optimum capped at {CAP:g} as the script searches, declared seed "
        f"{seeded.optimum:.6f}, {_band_text(ens.band('optimum'))}"
    )
    declared_band = ens.band("uncapped")
    declared_lands = [declared_band.holds(float(p)) for p in (BOOK_OPTIMUM_FMINBND, BOOK_OPTIMUM)]
    print(
        f"  row 3 under the declared rule, every seed's uncapped optimum, "
        f"{_band_text(declared_band)}: {BOOK_OPTIMUM_FMINBND} and {BOOK_OPTIMUM} "
        f"{'land' if all(declared_lands) else 'do not both land'}"
    )
    on_cap = sum(run.on_the_cap for run in ens.runs)
    below = sum(run.ruin_below_cap for run in ens.runs)
    print(
        f"  seeds on the cap {on_cap} of {len(ens.runs)}. Seeds whose ruin leverage is "
        f"below {CAP:g}: {below}, against {result.ruin_below_cap_exact * len(ens.runs):.1f} "
        "expected exactly"
    )
    for name, label in (
        ("described_growth", "growth, CPPI as described"),
        ("described_drawdown", "max drawdown, CPPI as described"),
        ("cppi_drawdown", "max drawdown, CPPI as scripted"),
    ):
        print(f"  {label:<33} {getattr(seeded, name):.6f}, {_band_text(ens.band(name))}")
    lines = result.lines
    print(
        f"  on the saved returns at the declared seed's f of {lines.leverage:.6f}, reading ret "
        "for the script's r"
    )
    print(f"    growth, full account at f * D   {lines.full_growth:.6f}")
    print(f"    max drawdown at f / 1.4         {lines.drawdown_over_1_4:.6f}")
    print(f"    max drawdown at f * D           {lines.full_drawdown:.6f}")
    print(
        f"    CPPI as scripted                growth {lines.cppi_growth:.6f}, "
        f"max drawdown {lines.cppi_drawdown:.6f}"
    )
    print(
        f"    CPPI as described               growth {lines.described_growth:.6f}, "
        f"max drawdown {lines.described_drawdown:.6f}"
    )
    print(f"  historical optimum capped at {CAP:g}   {result.historical_capped:.6f}, the cap")
    print()
    low, high = result.kelly_band
    print(f"Row group 13, the evidence on the book's {BOOK_KELLY}")
    print(
        f"  Kelly implied by a Sharpe ratio of {SHARPE_BAND[0]:.2f} to {SHARPE_BAND[1]:.2f} and "
        f"an APR of {APR_BAND[0]:.3f} to {APR_BAND[1]:.3f}: {low:.2f} to {high:.2f}"
    )
    print(
        f"  draws shifted so the Kelly is {BOOK_KELLY}, lambda {result.shifted_params.lam:.6e}, "
        f"median uncapped optimum {result.shifted.band('uncapped').median:.6f}"
    )
    for number, printed, found, lands in shifted_landings(result):
        print(
            f"    row {number:<3} {printed:>9}  {_band_text(found)}  "
            f"{'lands' if lands else 'does not land'}"
        )
    print()
    print("  Exploratory. docs/replication-log.md carries the verdicts.")


def read_returns(data_dir: Path | None = None) -> tuple[VintageEntry, NDArray[np.float64]]:
    """Chan's saved Example 5.1 returns, through :func:`chan.series.load_returns`."""
    return load_returns(SAVED_RETURNS, data_dir=data_dir)


def run(data_dir: Path | None = None) -> MonteCarloLeverage:
    """Read the saved returns, run the specification on every seed, and print the report."""
    entry, returns = read_returns(data_dir)
    result = monte_carlo_leverage(entry, returns)
    report(result)
    return result


def main() -> None:
    argparse.ArgumentParser(
        description="Monte Carlo leverage, historical optimization and CPPI on Example 5.1's "
        "returns, Algorithmic Trading's Boxes 8.1 to 8.6"
    ).parse_args()
    try:
        run()
    except VintageUnavailable as refused:
        # A refusal that names the file reaches the reader as one line, the way
        # chan.aud_cad_johansen.main does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
