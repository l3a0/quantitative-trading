"""Qian's risk parity against the classic 60/40, on SPY and AGG.

Chan reports Edward Qian's argument that a 60/40 split between stocks and
bonds is not the balanced portfolio its labels suggest. Capital is split 60 to
40, and risk is not, because the equity leg is several times as volatile as
the bond leg. Weighting the legs so each contributes the same share of risk
moves the capital split a long way toward bonds, and levering the result back
to 60/40's volatility is what makes the two comparable. Location 4684 prints
one clause, quoted here as the committed highlight carries it: "to achieve a
higher Sharpe ratio while maintaining the same risk level as the 60–40
portfolio, Dr. Qian recommended a 23–77 allocation while leveraging the entire
portfolio by 1.8". Three things in it are chased below, the allocation, the
leverage and the Sharpe ranking, and the fourth is the matching condition the
leverage exists to meet.

So the claim is a Sharpe ranking at matched risk, and the reproducible parts
are the allocation, the leverage, the risk decomposition and the ranking. The
book prints no returns and no volatilities, so pinning a return against it
would invent a precision the source does not carry.
``docs/replication-log.md`` Entry 4 carries this run's verdicts row by row, and
``tests/test_risk_parity.py`` is the single authority for every number any
prose surface quotes about it.

## Risk contribution, and why two legs make the specification arithmetic

A leg's **risk contribution** is its share of the portfolio's variance,
``w_i * (Sigma w)_i / (w' Sigma w)``, where ``Sigma`` is the covariance matrix
of the legs' returns. The shares sum to 1 by construction. **Risk parity** is
the allocation that makes them equal.

Two live specifications compute that. Equal risk contribution splits the shares
evenly using the whole covariance matrix. Inverse-volatility weighting sets
``w_i`` proportional to ``1 / sigma_i`` and never looks at the correlation.
They part company in general and they do not part company on two assets.
Setting the two contributions equal gives
``w_1^2 s_1^2 + rho w_1 w_2 s_1 s_2 = w_2^2 s_2^2 + rho w_1 w_2 s_1 s_2``, and
the correlation term is identical on both sides. It cancels, leaving
``w_1 s_1 = w_2 s_2`` for positive weights.

Both are still named in every pin, because the two stop agreeing the moment a
third leg is added. :func:`risk_parity_weights` computes the inverse-volatility
form and :func:`risk_shares` is what checks it equalised the contributions.

## Qian's two figures are one figure and a correlation

His 23-77 is a statement about volatilities rather than about a solver.
``0.23 * s_stock = 0.77 * s_bond``, so his equity leg is about
:data:`BOOK_VOL_RATIO` times as volatile as his bond leg. Two significant
figures is all the source carries, so weights that round to 23 and 77 put the
ratio anywhere in :data:`BOOK_RATIO_BAND` and a third digit would be invented.

His 1.8 is not independent of that. Given 23-77 weights, the leverage that
matches 60/40's volatility is fixed by the correlation alone, because the leg
volatilities cancel out of the ratio once their ratio is pinned by the weights.
:func:`leverage_from_correlation` is that map and
:func:`correlation_from_leverage` runs it backwards. Read forwards it is
useful, since the leverage this run derives moves visibly with the measured
correlation. Read backwards it is weak. 1.8 solves to a correlation near 0.16
on his printed weights, and letting both of his roundings vary at once opens
that to roughly −0.01 through +0.37, which is most of the range a stock-bond
correlation occupies. So the report states what the derived leverage implies
and does not claim to have recovered the correlation Qian measured.

## The bond leg is an aggregate bond fund, committed before anything was read

Qian's bond leg is an aggregate bond exposure, and AGG is that fund. The owner
ruled on 2026-09-18, under the rule that a proxy matches what the source
describes, in writing, before anything is downloaded, and is never chosen
because it makes a number come out. TLT was the earlier answer and it is
withdrawn: a twenty-plus-year Treasury fund's volatility sits far closer to
equities' than an aggregate index's does, so the derived weights could not land
near 23-77 and the cause would be the instrument rather than the method. A
verdict reached that way is about the proxy rather than about the claim.

That the ratio is reachable under AGG is a consequence of matching the source
rather than the reason for choosing it. The measured ratio is reported beside
:data:`BOOK_VOL_RATIO` and its band whatever it comes out at, so a ratio inside
the band is not called a miss and one far outside reads as the gap it is.

## The price basis is adjusted, which runs against this repo's default

``docs/design.md`` prefers raw as-traded closes, because they cannot be
restated. A bond fund's return is mostly its distributions, so a raw AGG series
strips out most of what the leg earns and makes every return, Sharpe and
ranking figure here wrong. Both legs read the adjusted close, which
``chan.series.close_identity`` spells ``(yfinance, adjusted)``. The basis moves
the returns and barely moves the risk decomposition, since a price return and a
total return have close volatilities, so the report names the basis beside
every figure and says which ones it could move.

## Constant weights, rebalanced daily

"60/40" is a rebalancing rule rather than a holding. Buy and hold drifts to
whatever the market makes of it, and the risk decomposition assumes the weights
it is handed. This run holds constant weights and rebalances every trading day,
which is what makes the reported weights the weights the portfolio carried.

## The units are declared, because mixing them has already cost this repo once

Three declarations, because Sharpe ratios, volatilities and a comparison of
what two portfolios did to capital are three quantities in two units.

1. **The moments are computed on simple daily returns**, which is the basis a
   Sharpe ratio is conventionally quoted on. The annual risk-free rate comes
   down to a daily one by simple division, ``r / 252``, rather than by the
   compounded ``(1 + r) ** (1 / 252) - 1``. The two differ by about 2 percent
   of the rate, which is small and is still a choice.
2. **Annualisation is 252 trading days**, the mean scaled by 252 and the
   volatility by the square root of 252. Nothing in ``src/chan`` annualised
   anything before ``chan.kelly_leverage``, and this follows it, which is what
   stops the next experiment picking 260.
3. **No transaction costs and no financing spread are charged**, because the
   book charges none and a replication reproduces the source's calculation.
   The omission is not neutral and it points one way: a daily rebalance has
   turnover, the levered portfolio has more of it plus a borrowing cost, so
   charging nothing favours the portfolio the book is arguing for.

## A Sharpe ratio needs a rate, and no risk-free series is committed

So the run assumes a constant annual rate and declares it as a specification.
Chan's own 4 percent at location 2858 is the rate ``chan.kelly_leverage``
pins, and taking it keeps one number across two replications rather than
inventing a second.

Under costless financing on excess returns a Sharpe ratio does not move with
leverage, so the ranking's sign is settled before the portfolio is levered.
:func:`rank_at_matched_volatility` computes the leverage inside the window it
ranks, and what that costs is worth stating exactly rather than waving away.

``sharpe_difference`` is invariant to the leverage, so the point estimate
carries no look-ahead at all and ``tests/test_risk_parity.py`` holds that at
three leverages. The error bar is a different matter. ``newey_west_summary``
reads ``leverage * parity - bench``, so ``mean_difference_annual`` and
``t_newey_west`` are both functions of a leverage estimated inside the window
they describe. On the rising-rates window the robust t runs from −2.20 at the
in-window leverage to −1.64 at the falling window's, which crosses the
threshold this module reports against. The in-window leverage is the right
choice, because it is the one that makes the matched-volatility identity below
exact and so the one the error bar is attached to, but it is a choice the
sample informed and the suite pins the spread rather than hiding it.

The leverage still earns its place beyond the distance from 1.8. Once the two
portfolios are matched on volatility, their Sharpe difference is exactly their
mean excess-return difference divided by that common volatility, so the ranking
becomes the mean of one daily series rather than a bare sign.

## The ranking gets an error bar, because a short window cannot resolve one

The rising-rates window below is a few years rather than two decades.
``ithildincore.stats.newey_west_summary`` takes the daily difference of the two
portfolios' excess returns and reports its mean, both t-statistics and the lag
it used, with the robust one correcting for the autocorrelation daily portfolio
returns carry. So each window says whether it resolves the ranking, in a line a
reader sees rather than as an exception, because a window that cannot resolve a
sign has not failed at anything.

The ranking is therefore pinned as the measured difference and its robust t
rather than as the comparison's result. An assertion that one Sharpe exceeds
another survives any mutation that leaves the sign alone, which includes
getting the magnitude wrong by any amount.

## The three windows were declared on the issue before any number existed

A window chosen after the ranking is seen is a window chosen to produce a
ranking, so the boundary is a dated external event rather than anything read
from the series under test. The Federal Reserve raised its target range on
:data:`TIGHTENING_START`, the first increase of that tightening cycle, which is
the public fact the regime question is about. The three windows are
:data:`WINDOWS`, the report runs all three every time, and moving the boundary
means editing
[issue 15](https://github.com/l3a0/quantitative-trading/issues/15) first.

## Refitting the weights inside a sub-window would flatter risk parity

60/40 is fixed by definition and never sees the data. Weights refitted inside a
window have seen every day they are then judged on, so a ranking built that way
compares a fixed allocation against one fitted to the sample. The two questions
are therefore separated.

1. **The decomposition is in-window.** The risk contributions and the weights
   are recomputed inside each window and reported there, because what they
   answer is what balanced risk looked like in that regime. They carry no
   ranking.
2. **The ranking uses weights that did not see the window.** The rising-rates
   window is ranked on weights derived from the falling-rates window, which is
   strictly earlier data and available at the boundary. The full span and the
   falling-rates window have nothing before them, so their rankings are
   in-sample and every surface says so.

## Risk parity may invert the book's correction

The weights follow the volatilities, and bonds were not quiet after 2022. As
the bond leg's volatility approaches the equity leg's in a window, the
risk-parity weights move toward stocks, and far enough past 60/40's own split
risk parity puts more weight on stocks than 60/40 does. The correction the book
argues for then points the other way in that window. That is a result rather
than a bug, so the report states the direction it found rather than describing
the weights as a move toward bonds.

Usage::

    python -m chan.risk_parity                            # the three declared windows
    python -m chan.risk_parity --start 2010-01-01 --end 2019-12-31
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from ithildincore.stats import newey_west_summary

from chan.series import WindowCrossesScaleBreak, aligned_closes, load_close, vintage_line
from chan.vintage import VintageUnavailable

#: The two legs, stocks first. Chan names no instruments, so both are this
#: repo's choice, fixed in writing on issue 15 before anything was downloaded.
#:
#: Qian's own paper does name them, which Chan's "not publicly distributed"
#: obscured and a search found on PanAgora's own site. He worked the Russell
#: 1000 Index against the Lehman Aggregate Bond Index from 1983 to 2004. AGG
#: tracks that bond index under its later names, so the bond leg is his in
#: substance and cannot reach his span, since the fund opened five days before
#: his sample ends. SPY is the S&P 500 rather than the Russell 1000, and IWB is
#: the fund that tracks his index. Swapping the equity leg for it is
#: [issue 160](https://github.com/l3a0/quantitative-trading/issues/160), which
#: runs on free data, and reaching his 1983 to 2004 sample is
#: [issue 161](https://github.com/l3a0/quantitative-trading/issues/161), which
#: does not.
STOCK = "SPY"
BOND = "AGG"

#: 60/40, stocks then bonds. Fixed by definition and never fitted to anything.
BENCHMARK_WEIGHTS = (0.60, 0.40)

#: Qian's allocation at location 4684, stocks then bonds.
BOOK_WEIGHTS = (0.23, 0.77)

#: The leverage at location 4684, on the whole risk-parity portfolio.
BOOK_LEVERAGE = 1.8

#: The volatility ratio :data:`BOOK_WEIGHTS` implies, ``0.77 / 0.23``.
#:
#: Under inverse-volatility weighting ``w_stock * s_stock = w_bond * s_bond``,
#: so the printed weights are a statement about volatilities. Quoted at two
#: significant figures everywhere a report prints it, because that is what the
#: source carries.
BOOK_VOL_RATIO = BOOK_WEIGHTS[1] / BOOK_WEIGHTS[0]

#: The ratios weights rounding to 23 and 77 admit, ``0.765/0.235`` to
#: ``0.775/0.225``.
#:
#: A measured ratio inside this band is consistent with what Qian printed. One
#: outside it is the gap it looks like. The band exists so a third digit is
#: never read off a two-digit source.
BOOK_RATIO_BAND = (0.765 / 0.235, 0.775 / 0.225)

#: The first increase of the 2022 tightening cycle, which cuts the sub-windows.
#:
#: A dated external event rather than anything read from the series under test.
#: A cut placed at the bond leg's own worst stretch would be the result
#: deciding the test.
TIGHTENING_START = "2022-03-16"

#: The three declared windows, each ``(label, start, end)`` with ``None`` open.
#:
#: Declared on issue 15 before any number existed. The report runs all three
#: every time, so a window cannot be reported alone.
WINDOWS = (
    ("full span", None, None),
    ("falling rates", None, "2022-03-15"),
    ("rising rates", TIGHTENING_START, None),
)

#: Chan's constant at location 2858, the rate ``chan.kelly_leverage`` also
#: reads. No risk-free series is committed, so this is a declared
#: specification rather than a rate anyone paid.
RISK_FREE = 0.04

#: Trading days in a year, the annualisation ``chan.kelly_leverage`` set.
TRADING_DAYS = 252

#: A window shorter than this stops the run, the floor
#: ``chan.pair_cointegration.run`` and ``chan.kelly_leverage.run`` already use.
#: A volatility estimated from a handful of days is a number the report would
#: print without a caveat.
MIN_TRADING_DAYS = 30

BOOK_REF = (
    "Qian's risk parity as Chan reports it (rev. ed., Kindle location 4684): a 23-77 "
    "allocation between stocks and bonds, levered 1.8 times to hold 60/40's risk level, "
    "for a higher Sharpe ratio"
)


@dataclass(frozen=True)
class Legs:
    """Both legs' annualised moments over one window, and nothing about weights.

    ``vol_ratio`` is the equity leg's volatility over the bond leg's, which is
    the quantity :data:`BOOK_VOL_RATIO` is a claim about. ``correlation`` is
    the measured one, which the report keeps apart from the correlation a
    leverage implies: the two agree only when the measured weights are the
    printed ones.
    """

    start: str
    end: str
    days: int
    stock_vol: float
    bond_vol: float
    vol_ratio: float
    correlation: float
    stock_mean: float
    bond_mean: float

    @property
    def ratio_inside_the_band(self) -> bool:
        """Whether the measured ratio is one weights rounding to 23-77 admit."""
        low, high = BOOK_RATIO_BAND
        return low <= self.vol_ratio <= high


@dataclass(frozen=True)
class Allocation:
    """One set of weights and what it did over one window.

    ``stock_risk_share`` and ``bond_risk_share`` are the risk contributions,
    which sum to 1. They are what says how far from balanced an allocation is,
    and they are the argument the weights rest on.

    ``volatility`` and ``mean_excess`` are annualised, and ``sharpe`` is their
    ratio. None of the three is levered, because leverage moves the first two
    together and leaves the third alone.
    """

    label: str
    stock_weight: float
    bond_weight: float
    stock_risk_share: float
    bond_risk_share: float
    volatility: float
    mean_excess: float
    sharpe: float


@dataclass(frozen=True)
class Ranking:
    """Two portfolios matched on volatility, and whether the window resolves them.

    ``leverage`` is what it takes to lift the risk-parity portfolio to the
    benchmark's volatility. ``implied_correlation`` reads that leverage back
    through :func:`correlation_from_leverage` on Qian's printed weights, so
    this run's leverage and his 1.8 are comparable in one unit. It is ``None``
    where the leverage solves to nothing a correlation can be, which the report
    prints as a refusal rather than as a number.

    ``sharpe_difference`` is risk parity less the benchmark, so a positive
    value is the direction the book argues for. ``t_newey_west`` is the robust
    t-statistic on ``mean_difference_daily``, which is the daily series whose
    mean the whole ranking is.

    ``in_sample`` says whether the weights saw this window. ``weight_source``
    names the window they came from, so a row can never be read without it.
    """

    label: str
    weight_source: str
    in_sample: bool
    leverage: float
    implied_correlation: float | None
    matched_volatility: float
    sharpe_benchmark: float
    sharpe_parity: float
    sharpe_difference: float
    mean_difference_annual: float
    days: int
    t_naive: float
    t_newey_west: float
    lag: int

    @property
    def rate_sensitivity(self) -> float:
        """How far the Sharpe difference moves per unit of assumed risk-free rate.

        ``1 / vol(60/40)`` less ``1 / vol(risk parity, unlevered)``, which is
        the derivative of the difference with respect to the rate. Levering to
        match puts the unlevered risk-parity volatility at
        ``matched_volatility / leverage``, so the whole thing collapses to
        ``(1 - leverage) / matched_volatility`` and is negative exactly when
        the leverage exceeds 1. That is the same condition as risk parity
        being the quieter portfolio before it is levered.

        It is computed rather than asserted because the rate was declared with
        the windows, so scanning it would spend the sample on a search nothing
        recorded. The derivative says which way a different rate would push
        without computing a second ranking.
        """
        return (1.0 - self.leverage) / self.matched_volatility

    @property
    def resolved(self) -> bool:
        """Whether the robust t clears 2, the usual two-sided 5 percent rule.

        Reported rather than enforced. A window that does not resolve the
        ranking has not failed at anything, and the line saying so is what
        stops a verdict being read off a sign the sample cannot support.
        """
        return abs(self.t_newey_west) >= 2.0


def simple_returns(closes: pd.DataFrame) -> pd.DataFrame:
    """One-period simple returns for both legs, with non-finite rows dropped.

    The same rule ``chan.kelly_leverage.simple_returns`` applies to one leg. A
    zero close divides to an infinity rather than raising, and a portfolio
    volatility computed from one is ``nan``, which prints and compares without
    stopping anything.
    """
    returns = closes.pct_change().dropna()
    return returns[np.isfinite(returns).all(axis=1)]


def annualised_covariance(returns: pd.DataFrame) -> np.ndarray:
    """The legs' covariance matrix, scaled to a year by :data:`TRADING_DAYS`.

    The sample form, dividing by ``n - 1``, which is what ``chan.kelly_leverage``
    reads for the same reason: it is what MATLAB's ``cov`` does and what Chan's
    own scripts therefore computed.
    """
    return returns.cov(ddof=1).to_numpy() * TRADING_DAYS


def measure_legs(returns: pd.DataFrame) -> Legs:
    """Each leg's annualised volatility and mean, their ratio and their correlation."""
    covariance = annualised_covariance(returns)
    stock_vol, bond_vol = math.sqrt(covariance[0, 0]), math.sqrt(covariance[1, 1])
    return Legs(
        start=str(returns.index[0].date()),
        end=str(returns.index[-1].date()),
        days=len(returns),
        stock_vol=stock_vol,
        bond_vol=bond_vol,
        vol_ratio=stock_vol / bond_vol,
        correlation=covariance[0, 1] / (stock_vol * bond_vol),
        stock_mean=float(returns.iloc[:, 0].mean()) * TRADING_DAYS,
        bond_mean=float(returns.iloc[:, 1].mean()) * TRADING_DAYS,
    )


def risk_shares(weights: tuple[float, float], covariance: np.ndarray) -> tuple[float, float]:
    """Each leg's share of the portfolio's variance, which sums to 1.

    ``w_i * (Sigma w)_i / (w' Sigma w)``. This is the quantity Qian's argument
    is about: 60/40 splits capital 60 to 40 and splits this far more unevenly,
    because the equity leg is several times as volatile.
    """
    w = np.asarray(weights, dtype=float)
    marginal = w * (covariance @ w)
    total = float(w @ covariance @ w)
    return float(marginal[0] / total), float(marginal[1] / total)


def risk_parity_weights(legs: Legs) -> tuple[float, float]:
    """Inverse-volatility weights, which equalise the risk contributions on two legs.

    The correlation cancels out of the two-leg equal-contribution equation, so
    this is the equal-risk-contribution answer as well as the
    inverse-volatility one. The module docstring carries the cancellation, and
    ``tests/test_risk_parity.py`` checks it numerically at three correlations
    rather than trusting the algebra.
    """
    stock = (1.0 / legs.stock_vol) / (1.0 / legs.stock_vol + 1.0 / legs.bond_vol)
    return stock, 1.0 - stock


def portfolio_excess_returns(
    returns: pd.DataFrame, weights: tuple[float, float], *, risk_free: float = RISK_FREE
) -> pd.Series:
    """A constant-weight portfolio's daily excess return, rebalanced every day.

    Constant weights make the daily portfolio return the weighted sum of the
    legs' returns, which is what a daily rebalance buys and what a buy-and-hold
    does not. The rate is subtracted per day as ``risk_free / 252``, the simple
    division declared in the module docstring.
    """
    return returns @ np.asarray(weights, dtype=float) - risk_free / TRADING_DAYS


def decompose(
    label: str,
    returns: pd.DataFrame,
    weights: tuple[float, float],
    *,
    risk_free: float = RISK_FREE,
) -> Allocation:
    """One allocation's risk split, volatility, mean excess return and Sharpe ratio."""
    covariance = annualised_covariance(returns)
    stock_share, bond_share = risk_shares(weights, covariance)
    excess = portfolio_excess_returns(returns, weights, risk_free=risk_free)
    volatility = float(excess.std(ddof=1)) * math.sqrt(TRADING_DAYS)
    mean_excess = float(excess.mean()) * TRADING_DAYS
    return Allocation(
        label=label,
        stock_weight=weights[0],
        bond_weight=weights[1],
        stock_risk_share=stock_share,
        bond_risk_share=bond_share,
        volatility=volatility,
        mean_excess=mean_excess,
        sharpe=mean_excess / volatility,
    )


def leverage_from_correlation(
    correlation: float,
    *,
    weights: tuple[float, float] = BOOK_WEIGHTS,
    benchmark: tuple[float, float] = BENCHMARK_WEIGHTS,
) -> float:
    """The leverage that matches the benchmark's volatility, at a given correlation.

    Under inverse-volatility weighting the weights fix the volatility ratio, at
    ``weights[1] / weights[0]``, and the leg volatilities then cancel out of
    the ratio of the two portfolio volatilities. So on fixed weights the
    leverage reads the correlation and nothing else, which is what makes Qian's
    1.8 a statement about the stock-bond correlation.

    Defaults to Qian's printed weights, because that is the map his 1.8 has to
    be read through.
    """
    ratio = weights[1] / weights[0]
    return math.sqrt(
        _variance(benchmark, ratio, correlation) / _variance(weights, ratio, correlation)
    )


def correlation_from_leverage(
    leverage: float,
    *,
    weights: tuple[float, float] = BOOK_WEIGHTS,
    benchmark: tuple[float, float] = BENCHMARK_WEIGHTS,
) -> float | None:
    """:func:`leverage_from_correlation` run backwards, or ``None`` where it does not.

    The map is monotone and invertible over the correlations a pair of traded
    instruments reaches, and it is still a ratio of two quadratics. A leverage
    far enough outside the reachable range solves either to nothing at all,
    when the denominator vanishes, or to a number outside ``[-1, 1]``, which no
    correlation is. Both come back as ``None``, and the report prints that as
    a refusal rather than as a number, because a correlation of 1.4 read as a
    figure is worse than no figure.
    """
    if leverage <= 0.0:
        # The inversion squares its input, so without this a leverage of -5
        # comes back as a perfectly ordinary-looking correlation. Nothing
        # reaches here with one, because `matching_leverage` is a ratio of two
        # standard deviations, and a guard whose cost is one comparison is
        # cheaper than the reader who has to work out why the sign vanished.
        return None
    ratio = weights[1] / weights[0]
    squared = leverage**2
    # Both variances are affine in the correlation, so the equation is linear.
    bench_const, bench_slope = _affine(benchmark, ratio)
    parity_const, parity_slope = _affine(weights, ratio)
    denominator = squared * parity_slope - bench_slope
    if denominator == 0.0:
        return None
    correlation = (bench_const - squared * parity_const) / denominator
    return correlation if -1.0 <= correlation <= 1.0 else None


def _affine(weights: tuple[float, float], ratio: float) -> tuple[float, float]:
    """A portfolio's variance as ``constant + slope * correlation``, at unit bond volatility.

    The bond leg's volatility is set to 1 and the stock leg's to ``ratio``,
    which is the scaling that cancels in :func:`leverage_from_correlation`.
    """
    stock, bond = weights
    return stock**2 * ratio**2 + bond**2, 2.0 * stock * bond * ratio


def _variance(weights: tuple[float, float], ratio: float, correlation: float) -> float:
    constant, slope = _affine(weights, ratio)
    return constant + slope * correlation


def matching_leverage(
    returns: pd.DataFrame,
    parity_weights: tuple[float, float],
    *,
    benchmark: tuple[float, float] = BENCHMARK_WEIGHTS,
    risk_free: float = RISK_FREE,
) -> float:
    """The multiple that lifts the risk-parity portfolio to the benchmark's volatility.

    Measured on the window's own returns rather than derived from
    :func:`leverage_from_correlation`, because the weights handed in are not
    always the ones that fix the volatility ratio: an out-of-sample ranking
    carries in weights from an earlier window.
    """
    parity = portfolio_excess_returns(returns, parity_weights, risk_free=risk_free)
    bench = portfolio_excess_returns(returns, benchmark, risk_free=risk_free)
    return float(bench.std(ddof=1)) / float(parity.std(ddof=1))


def rank_at_matched_volatility(
    label: str,
    returns: pd.DataFrame,
    parity_weights: tuple[float, float],
    *,
    weight_source: str,
    in_sample: bool,
    benchmark: tuple[float, float] = BENCHMARK_WEIGHTS,
    risk_free: float = RISK_FREE,
) -> Ranking:
    """The Sharpe ranking as one daily series' mean, with a robust error bar.

    Levering the risk-parity portfolio to the benchmark's volatility makes the
    two Sharpe ratios differ by exactly the mean of ``leverage * parity excess
    less benchmark excess``, divided by the common volatility. So the ranking
    is the mean of one series and :func:`newey_west_summary` is what says
    whether the window resolves it.

    The leverage is measured inside this window and that is not look-ahead. A
    Sharpe ratio does not move with leverage under costless financing on excess
    returns, so ``sharpe_difference`` is invariant to it and only the weights
    carry information from outside.
    """
    parity = portfolio_excess_returns(returns, parity_weights, risk_free=risk_free)
    bench = portfolio_excess_returns(returns, benchmark, risk_free=risk_free)
    leverage = float(bench.std(ddof=1)) / float(parity.std(ddof=1))
    difference = leverage * parity - bench
    summary = newey_west_summary(difference.to_numpy())
    volatility = float(bench.std(ddof=1)) * math.sqrt(TRADING_DAYS)
    sharpe_bench = float(bench.mean()) * TRADING_DAYS / volatility
    sharpe_parity = (
        float(parity.mean()) * TRADING_DAYS / (float(parity.std(ddof=1)) * math.sqrt(TRADING_DAYS))
    )
    return Ranking(
        label=label,
        weight_source=weight_source,
        in_sample=in_sample,
        leverage=leverage,
        implied_correlation=correlation_from_leverage(leverage),
        matched_volatility=volatility,
        sharpe_benchmark=sharpe_bench,
        sharpe_parity=sharpe_parity,
        sharpe_difference=sharpe_parity - sharpe_bench,
        mean_difference_annual=summary.mean * TRADING_DAYS,
        days=summary.n,
        t_naive=summary.t_naive,
        t_newey_west=summary.t_newey_west,
        lag=summary.lag,
    )


@dataclass(frozen=True)
class WindowResult:
    """One window's decomposition, which is in-window and carries no ranking.

    The ranking is a separate object, because the weights it uses are not
    always the weights measured here. Keeping them apart is what stops a
    reader taking a fitted allocation's ranking for an out-of-sample one.
    """

    label: str
    legs: Legs
    benchmark: Allocation
    parity: Allocation

    @property
    def parity_tilts_toward_stocks(self) -> bool:
        """Whether risk parity put more weight on stocks than 60/40 does.

        The state the module docstring names as reachable rather than
        impossible. It inverts the correction the book is arguing for, and it
        is a result rather than a bug.
        """
        return self.parity.stock_weight > BENCHMARK_WEIGHTS[0]


class WindowTooShort(Exception):
    """A declared window holds too few common trading days to estimate a volatility.

    Separate from ``chan.vintage.VintageUnavailable``, which says a run could
    not read a vintage, and from ``chan.series.WindowCrossesScaleBreak``, which
    says a window spans a day a series changed scale. This one says both
    vintages read, verified and joined, and the window came back too thin to
    compute a moment on. ``main`` turns all three into a line naming which one
    fired.
    """


def clip(joined: pd.DataFrame, start: str | None, end: str | None) -> pd.DataFrame:
    """The joined frame over one inclusive window, both bounds optional."""
    if start is not None:
        joined = joined.loc[joined.index >= pd.Timestamp(start)]
    if end is not None:
        joined = joined.loc[joined.index <= pd.Timestamp(end)]
    return joined


def measure_window(
    label: str,
    joined: pd.DataFrame,
    start: str | None,
    end: str | None,
    *,
    risk_free: float = RISK_FREE,
) -> tuple[WindowResult, pd.DataFrame]:
    """One window's decomposition, and the returns it was computed from.

    The returns come back because the ranking needs them and recomputing them
    would be a second answer to one question.
    """
    window = clip(joined, start, end)
    if len(window) < MIN_TRADING_DAYS:
        raise WindowTooShort(
            f"the {label} window holds {len(window)} common trading days, and a volatility "
            f"needs at least {MIN_TRADING_DAYS} -- the joined span is "
            f"{joined.index[0].date()}..{joined.index[-1].date()}"
        )
    returns = simple_returns(window)
    legs = measure_legs(returns)
    parity_weights = risk_parity_weights(legs)
    return (
        WindowResult(
            label=label,
            legs=legs,
            benchmark=decompose("60/40", returns, BENCHMARK_WEIGHTS, risk_free=risk_free),
            parity=decompose("risk parity", returns, parity_weights, risk_free=risk_free),
        ),
        returns,
    )


def rank_the_windows(
    measured: dict[str, tuple[WindowResult, pd.DataFrame]],
    *,
    risk_free: float = RISK_FREE,
) -> dict[str, Ranking]:
    """Each declared window's ranking, with the rising one ranked out of sample.

    The rising-rates window takes the falling-rates window's weights, which is
    strictly earlier data and available at the boundary. The other two have
    nothing before them, so their weights are their own and every surface says
    in sample.
    """
    earlier = measured["falling rates"][0].parity
    earlier_weights = (earlier.stock_weight, earlier.bond_weight)
    rankings = {}
    for label, (result, returns) in measured.items():
        out_of_sample = label == "rising rates"
        weights = (
            earlier_weights
            if out_of_sample
            else (result.parity.stock_weight, result.parity.bond_weight)
        )
        rankings[label] = rank_at_matched_volatility(
            label,
            returns,
            weights,
            weight_source="falling rates" if out_of_sample else label,
            in_sample=not out_of_sample,
            risk_free=risk_free,
        )
    return rankings


def _header(joined: pd.DataFrame, legs: dict[str, pd.Series], risk_free: float) -> None:
    """The vintages, the join and the specification, before any number is printed."""
    stock_entry, bond_entry = joined.attrs["vintages"]
    print("Risk parity against 60/40 on SPY and AGG, as Chan reports Edward Qian's argument")
    print(f"  {BOOK_REF}")
    print(f"  {STOCK} vintage: {vintage_line(stock_entry)}")
    print(f"  {BOND} vintage: {vintage_line(bond_entry)}")
    first, last = joined.index[0], joined.index[-1]
    print(f"  joined:      {first.date()} .. {last.date()}   ({len(joined):,} common days)")
    # An inner join drops days one leg traded and the other did not, silently.
    # Printing what each leg brought to the span is what turns a truncated
    # vintage or a calendar that is not the calendar into a number rather than
    # a shorter window nobody questioned.
    for entry in (stock_entry, bond_entry):
        own = legs[entry.symbol]
        inside = int(((own.index >= first) & (own.index <= last)).sum())
        print(
            f"    {entry.symbol} recorded {entry.first_date}..{entry.last_date}, "
            f"{entry.row_count:,} rows, {inside:,} of them inside the joined span, "
            f"of which the join dropped {inside - len(joined):,}"
        )
    print("  spec:        adjusted closes on both legs, constant weights rebalanced every")
    print(f"               trading day, simple daily returns, mean x {TRADING_DAYS}, sample sd")
    print(
        f"               (n-1) x sqrt({TRADING_DAYS}), risk-free {risk_free:.0%} subtracted as "
        f"{risk_free}/{TRADING_DAYS}"
    )
    print("               per day, no transaction costs and no financing spread")
    print()


def _decomposition(result: WindowResult, *, against_the_book: bool) -> None:
    """One window's leg moments, its 60/40 risk split and its risk-parity weights."""
    legs = result.legs
    print(f"--- {result.label}: {legs.start} .. {legs.end}   ({legs.days:,} daily returns) ---")
    print()
    print(
        f"  leg volatility, annualised      {STOCK} {legs.stock_vol:>8.2%}   "
        f"{BOND} {legs.bond_vol:>8.2%}"
    )
    inside = "inside" if legs.ratio_inside_the_band else "outside"
    low, high = BOOK_RATIO_BAND
    # Four decimals rather than two. The band's low end is 3.2553, which prints
    # as 3.26 and would make a measured 3.2554 read as "inside the 3.26 band",
    # so a reader checking the flag against the printed bound would find it
    # false. Nothing measured lands there and the line is what a reader checks.
    print(
        f"  volatility ratio {STOCK}/{BOND}       {legs.vol_ratio:>8.4f}   "
        f"{inside} the {low:.4f} to {high:.4f} band Qian's 23-77 admits"
    )
    print(f"  measured correlation            {legs.correlation:>+8.4f}")
    print(
        f"  leg mean return, annualised     {STOCK} {legs.stock_mean:>8.2%}   "
        f"{BOND} {legs.bond_mean:>8.2%}"
    )
    print()
    bench, parity = result.benchmark, result.parity
    print(f"  {'':<32}{STOCK:>10}{BOND:>10}")
    print(f"  {'60/40 capital weights':<32}{bench.stock_weight:>10.2%}{bench.bond_weight:>10.2%}")
    print(
        f"  {'60/40 risk contributions':<32}{bench.stock_risk_share:>10.2%}"
        f"{bench.bond_risk_share:>10.2%}"
    )
    print(
        f"  {'risk-parity capital weights':<32}{parity.stock_weight:>10.2%}"
        f"{parity.bond_weight:>10.2%}"
    )
    print(
        f"  {'its risk contributions':<32}{parity.stock_risk_share:>10.2%}"
        f"{parity.bond_risk_share:>10.2%}"
    )
    if against_the_book:
        # Both gaps are stated at the precision Qian's own figures carry, which
        # is whole percentage points on the weights and one decimal on the
        # ratio, and both are rounded from the full computed value rather than
        # from the rounded one printed above.
        print(
            f"  {'Qian prints':<32}{BOOK_WEIGHTS[0]:>10.0%}{BOOK_WEIGHTS[1]:>10.0%}   "
            f"gaps {(parity.stock_weight - BOOK_WEIGHTS[0]) * 100:+.0f} and "
            f"{(parity.bond_weight - BOOK_WEIGHTS[1]) * 100:+.0f} percentage points"
        )
        print(
            f"  {'his weights imply a ratio of':<32}{BOOK_VOL_RATIO:>10.1f}"
            f"{'':>10}   gap {legs.vol_ratio - BOOK_VOL_RATIO:+.1f}"
        )
    if result.parity_tilts_toward_stocks:
        print()
        print("  Risk parity puts MORE weight on stocks here than 60/40 does, so the")
        print("  correction the book argues for points the other way in this window.")
        print("  That is a result rather than a bug: the weights follow the volatilities,")
        print("  and the bond leg was not quiet enough here to pull them toward bonds.")
    print()


def _ranking(ranking: Ranking, *, against_the_book: bool) -> None:
    """The matched-volatility comparison, its leverage, and whether it resolved."""
    print("  the ranking, with both portfolios matched on volatility")
    sample = "in sample" if ranking.in_sample else "out of sample"
    print(f"    {'weights come from':<30}{ranking.weight_source} ({sample})")
    if not ranking.in_sample:
        print("      so the Sharpe ratio below is on those weights and not on the ones")
        print("      printed above, which were measured inside this window and rank nothing")
    leverage = f"{ranking.leverage:.4f}"
    if against_the_book:
        print(
            f"    {'leverage that matches 60/40':<30}{leverage:>10}   "
            f"the book prints {BOOK_LEVERAGE:g}, gap {ranking.leverage - BOOK_LEVERAGE:+.1f}"
        )
    else:
        print(f"    {'leverage that matches 60/40':<30}{leverage:>10}")
    implied = ranking.implied_correlation
    shown = f"{implied:+.4f}" if implied is not None else "no correlation solves it"
    his = correlation_from_leverage(BOOK_LEVERAGE)
    print(
        f"    {'read back on his 23-77 weights':<30}{shown:>10}   "
        f"where his {BOOK_LEVERAGE:g} implies {his:+.4f}"
    )
    print(f"    {'the volatility both carry':<30}{ranking.matched_volatility:>10.2%}")
    print(f"    {'Sharpe, 60/40':<30}{ranking.sharpe_benchmark:>10.4f}")
    print(f"    {'Sharpe, risk parity':<30}{ranking.sharpe_parity:>10.4f}")
    ranks = "risk parity ranks higher" if ranking.sharpe_difference > 0 else "60/40 ranks higher"
    print(f"    {'difference, parity less 60/40':<30}{ranking.sharpe_difference:>+10.4f}   {ranks}")
    print(
        f"    {'mean excess-return difference':<30}"
        f"{ranking.mean_difference_annual:>+10.2%}   a year, on {ranking.days:,} daily differences"
    )
    print(
        f"    {'robust t on that mean':<30}{ranking.t_newey_west:>+10.4f}   "
        f"Newey-West at lag {ranking.lag}, against a naive {ranking.t_naive:+.4f}"
    )
    print(
        f"    {'per unit of assumed rate':<30}{ranking.rate_sensitivity:>+10.4f}   "
        f"(1 - leverage) / volatility, so a higher rate costs risk parity"
    )
    if ranking.resolved:
        print("    This window resolves the ranking: the robust t clears 2.")
    else:
        print("    This window does NOT resolve the ranking. The robust t is under 2, so the")
        print("    sign above is not something this sample can support. Nothing has failed.")
    print()


def report(
    joined: pd.DataFrame,
    legs: dict[str, pd.Series],
    *,
    risk_free: float = RISK_FREE,
    extra: tuple[str, str | None, str | None] | None = None,
) -> None:
    """Print the three declared windows together, then any window a reader asked for."""
    _header(joined, legs, risk_free)
    measured = {
        label: measure_window(label, joined, start, end, risk_free=risk_free)
        for label, start, end in WINDOWS
    }
    rankings = rank_the_windows(measured, risk_free=risk_free)
    print("The three windows below were declared on issue 15 before any number existed, and")
    print(f"the boundary is the Federal Reserve's first increase of the cycle, {TIGHTENING_START}.")
    print("All three print every run, so no window here was chosen after its ranking was seen.")
    print()
    print(f"One return falls in neither sub-window, the one dated {TIGHTENING_START} itself, which")
    print("is why the two sub-windows hold one day fewer between them than the full span.")
    print("A return spans two closes, so that one straddles the cut and belongs to neither")
    print("side of it. It is the decision day, and it is the largest single day in the")
    print("neighbourhood, so it is named here rather than left for a reader to subtract.")
    print()
    for label, _, _ in WINDOWS:
        _decomposition(measured[label][0], against_the_book=True)
        _ranking(rankings[label], against_the_book=True)

    if extra is not None:
        label, start, end = extra
        result, returns = measure_window(label, joined, start, end, risk_free=risk_free)
        weights = (result.parity.stock_weight, result.parity.bond_weight)
        print("This window is not one of the three declared above, so it is off the")
        print("reproduction. Nothing below carries a published counterpart, and its weights")
        print("were fitted inside the window they are judged on.")
        print()
        _decomposition(result, against_the_book=False)
        _ranking(
            rank_at_matched_volatility(
                label,
                returns,
                weights,
                weight_source=label,
                in_sample=True,
                risk_free=risk_free,
            ),
            against_the_book=False,
        )

    print("A replication against data is exploratory by construction. The sample was spent")
    print("on a hypothesis Qian chose and Chan reported, so this run says whether his")
    print("figures reproduce and nothing about whether either allocation is a good idea.")
    print(f"The {risk_free:.0%} is Chan's constant applied to whatever window was read, not a rate")
    print("anyone paid, and no transaction cost or financing spread is charged, which")
    print("favours the levered portfolio the book argues for.")
    print()
    print("The assumed rate is not neutral to the ranking, which is why every window above")
    print("reports what it costs. The Sharpe difference changes with the rate by")
    print("1/vol(60/40) less 1/vol(risk parity, unlevered), and levering to match collapses")
    print("that to (1 - leverage) / volatility. So a higher assumed rate penalises risk")
    print("parity whenever the leverage is above 1. --risk-free moves the rate, and a run")
    print("that does is off the reproduction, because the rate was declared with the")
    print("windows.")
    print("docs/replication-log.md Entry 4 carries the verdict.")


def run(
    *,
    start: str | None = None,
    end: str | None = None,
    risk_free: float = RISK_FREE,
    data_dir: Path | None = None,
) -> None:
    """Read both vintages, join them, and print the report.

    Each leg is loaded on its own as well as through the join, so the report
    can say how many days the inner join dropped. The join is what verifies the
    bytes and what refuses a window spanning a scale break, and the two extra
    reads answer a question the joined frame no longer holds.
    """
    joined = aligned_closes(STOCK, BOND, data_dir=data_dir)
    legs = {
        STOCK: load_close(STOCK, data_dir=data_dir),
        BOND: load_close(BOND, data_dir=data_dir),
    }
    extra = None if start is None and end is None else ("the window you asked for", start, end)
    report(joined, legs, risk_free=risk_free, extra=extra)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Qian's risk parity against 60/40, on committed SPY and AGG vintages"
    )
    parser.add_argument(
        "--start",
        default=None,
        help="start of an extra window, inclusive, reported as off the reproduction",
    )
    parser.add_argument(
        "--end",
        default=None,
        help="end of an extra window, inclusive, reported as off the reproduction",
    )
    parser.add_argument(
        "--risk-free",
        type=float,
        default=RISK_FREE,
        help=f"annual risk-free rate (default: {RISK_FREE}, Chan's constant at location 2858)",
    )
    args = parser.parse_args()
    try:
        run(start=args.start, end=args.end, risk_free=args.risk_free)
    except (VintageUnavailable, WindowCrossesScaleBreak, WindowTooShort) as stopped:
        # A refusal naming which vintage or which window is worth nothing at the
        # bottom of a twenty-line pandas traceback. All three reach the operator
        # as a line, the way `chan.pair_cointegration.main` and
        # `chan.regime_figure.main` already exit. The scale-break refusal is
        # raised inside `aligned_closes` rather than here, so a module that
        # reads a pair and does not name it lets it through as a traceback.
        raise SystemExit(str(stopped)) from stopped


if __name__ == "__main__":
    main()
