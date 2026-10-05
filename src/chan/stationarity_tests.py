"""The three toolbox tests *Algorithmic Trading*'s Chapter 2 calls, as Chan's scripts ran them.

Chan's ``stationarityTests.m`` tests USD.CAD for mean reversion with three
functions he did not write, and later scripts call the same three again:
``cointegrationTests.m``, ``example_2_6.m`` and ``calendarSpdsMeanReversion.m``
call ``adf``, and ``TU_mom.m`` calls ``genhurst`` and ``vratiotest``. Each is
transcribed here once so that every replication reads one copy.

1. :func:`jplv7_adf` is ``adf`` from James LeSage's jplv7 toolbox, with the
   critical values of its ``ztcrit``.
2. :func:`genhurst` is Tomaso Aste's generalized Hurst exponent from the
   MATLAB File Exchange.
3. :func:`vratiotest` is the Lo and MacKinlay variance ratio test as MATLAB's
   Econometrics Toolbox computes it.

What vouches for each transcription is that it lands the digits Chan printed
from it on his own closes. ``tests/test_usdcad_mean_reversion.py`` holds that,
and ``tests/test_stationarity_tests.py`` holds each function's rules on
synthetic series.

**Why jplv7's ADF is not** :func:`ithildincore.timeseries.adf_tstat`. That is
``statsmodels``' ``adfuller`` at a fixed lag, and jplv7's ``adf`` starts its
sample one row later. It trims the lagged changes and then trims the lagged
level once more, so at one lag it fits ``n - 3`` rows where ``adfuller`` fits
``n - 2``. Its statistic is otherwise the usual one: the level regressed on the
lagged level, the lagged changes and a constant, with ``beta - 1`` divided by
its standard error. On Chan's 1,216 USD.CAD closes the dropped row moves the
statistic from −1.8430 to the −1.840744 his script prints.

**Where each came from.**

- ``adf.m`` and ``ztcrit.m`` from burakbayramli/books at
  ``43c0bb4de514fc04db3dbad3bb7f09381b2f71a1``, under
  ``Algorithmic_Trading_Chan/jplv7/coint/``, git blobs ``8266d37`` and
  ``e62b32a``. Three other copies of the toolbox hold the same ``adf.m`` body:
  the same repository's ``Econometrics_Using_Matlab_LeSage/coint/``,
  r-forge/spdep2's ``SEtoolbox/coint/`` and
  jfhawkin/Spatial-Econometric-Software's ``coint/``. The toolbox carries no
  licence beyond LeSage's statement that it is free.
- ``genhurst.m`` from the same repository and commit, under
  ``Algorithmic_Trading_Chan/``, git blob ``0cbf9a8``, dated 2013-01-30 by its
  author. GitHub's code search finds 16 copies in 5 blobs, and they run one
  algorithm once comments, whitespace and plotting lines are set aside. The
  Sable/mcbench-benchmarks snapshot of the File Exchange holds the same code,
  so no earlier version survives.
- ``vratiotest`` is MathWorks' and is not copied. :func:`vratiotest` implements
  Lo and MacKinlay's (1988) heteroskedasticity-consistent statistic from the
  paper, with the three details MATLAB's implementation fixes: the returns are
  trimmed to a whole number of periods first, the one-period variance divides
  by ``N - 1``, and the overlapping one by ``q(N - q + 1)(1 - q/N)``. Those
  three were read from MATLAB's own ``vratiotest.m``, and the p-value Chan
  printed is what vouches for them.

The port landed here with the pull request for
[issue 338](https://github.com/l3a0/quantitative-trading/issues/338).

**What changed on the way over.** Five things, and none moves a figure Chan
printed.

1. ``adf`` takes only the trend order 0, a constant and no trend, and
   :data:`ZTCRIT_CONSTANT` holds only the ten rows of ``ztcrit``'s table for
   that order. Every script in the book passes 0. Another order is refused by
   name rather than read from rows that were never committed.
2. ``adf`` returns the statistic, the AR(1) estimate, the observation count and
   the 1, 5 and 10 percent critical values. ``ztcrit``'s 90, 95 and 99 percent
   columns, the upper tail, are not carried, because no script reads them.
3. ``genhurst`` takes one ``q`` rather than a vector of them, and returns H
   without its standard deviation. Its warning for a short series compares the
   length against ``(maxT*4 | 60)``, a logical or that is always 1, so it never
   fires on a series of two or more points and is not carried.
4. ``vratiotest`` refuses a missing value where MATLAB deletes it. A deleted
   row would join the two returns either side of it into one, which is a
   different series, so a caller has to say what it meant.
5. ``vratiotest`` takes one period at a time rather than a vector of them.

``genhurst.m`` is distributed under this licence, which its redistribution
requires be kept with the source:

    Copyright (c) 2011, Tomaso Aste
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are
    met:

        * Redistributions of source code must retain the above copyright
          notice, this list of conditions and the following disclaimer.
        * Redistributions in binary form must reproduce the above copyright
          notice, this list of conditions and the following disclaimer in
          the documentation and/or other materials provided with the
          distribution

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
    ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
    LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
    SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
    INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
    CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
    ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
    POSSIBILITY OF SUCH DAMAGE.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.stats import norm

from chan.matlab_helpers import round_half_away

#: ``ztcrit``'s 1, 5 and 10 percent critical values for trend order 0, one row
#: per bin of 50 observations. ``ztcrit`` reads row ``(i − 1)·7 + p + 2`` of its
#: 70-row table, so these are rows 2, 9, 16, ... 65.
ZTCRIT_CONSTANT: tuple[tuple[float, float, float], ...] = (
    (-3.63993, -2.94935, -2.61560),
    (-3.56634, -2.93701, -2.61518),
    (-3.43911, -2.91515, -2.58414),
    (-3.46419, -2.91242, -2.58837),
    (-3.49260, -2.87595, -2.56885),
    (-3.44558, -2.84182, -2.57313),
    (-3.44036, -2.86974, -2.58294),
    (-3.42692, -2.86280, -2.57220),
    (-3.38577, -2.86443, -2.57318),
    (-3.45830, -2.87104, -2.59369),
)


@dataclass(frozen=True)
class Jplv7Adf:
    """What jplv7's ``adf`` returns and ``prt`` prints.

    ``statistic`` is ``results.adf``, ``ar1`` is ``results.alpha``, the
    coefficient on the lagged level, and ``nobs`` the rows the regression fit.
    ``critical`` holds the 1, 5 and 10 percent values in that order.
    """

    statistic: float
    ar1: float
    nobs: int
    lags: int
    critical: tuple[float, float, float]


@dataclass(frozen=True)
class VarianceRatio:
    """What MATLAB's ``vratiotest`` returns for one period.

    ``rejects`` is ``h``, true when the random walk is rejected at ``alpha``.
    ``statistic`` is the standard normal z, and ``ratio`` the variance of the
    overlapping ``period``-step returns over ``period`` times the variance of
    the one-step returns.
    """

    rejects: bool
    p_value: float
    statistic: float
    ratio: float
    period: int
    nobs: int


def ztcrit(nobs: int, order: int = 0) -> tuple[float, float, float]:
    """``ztcrit``: the 1, 5 and 10 percent critical values for ``nobs`` observations.

    The bin is ``round(nobs / 50) + 1``, one less below 50 observations, and
    capped at 10, so every series of 425 observations or more reads the last
    row. ``round`` is MATLAB's, half away from zero, which puts 125
    observations in bin 4 where numpy's half-to-even would put them in bin 3.
    """
    if order != 0:
        raise ValueError(
            f"ztcrit holds only trend order 0, a constant and no trend, not {order}, because "
            "that is the order every script in the book passes"
        )
    if nobs < 25:
        raise ValueError(
            f"ztcrit has no bin for {nobs} observations, because MATLAB's own index would "
            "fall below the table's first row"
        )
    i = int(round_half_away(nobs / 50)) + 1
    if nobs < 50:
        i -= 1
    return ZTCRIT_CONSTANT[min(i, 10) - 1]


def _zero_lag(x: NDArray[np.float64], n: int) -> NDArray[np.float64]:
    """jplv7's ``lag(x, n)``: ``x`` moved ``n`` rows later, the first ``n`` filled with 0."""
    return np.r_[np.zeros(n), x[:-n]]


def jplv7_adf(x: ArrayLike, order: int = 0, lags: int = 1) -> Jplv7Adf:
    """jplv7's ``adf(x, order, lags)``: the augmented Dickey-Fuller test as Chan ran it.

    The level is regressed on the lagged level, ``lags`` lagged changes and a
    constant, and the statistic is the lagged level's coefficient less 1 over
    its standard error, with the residual variance over the rows less the
    regressor count. The rows are ``x``'s fourth onward at one lag, one fewer
    than ``adfuller`` fits, for the reason the module docstring gives.
    """
    values = np.asarray(x, dtype=float)
    if not np.all(np.isfinite(values)):
        raise ValueError("jplv7_adf takes a series with no missing value, as adf.m does")
    if lags < 1:
        raise ValueError(
            f"jplv7_adf takes at least 1 lag, not {lags}, because adf.m's trimr refuses to "
            "trim the empty matrix of lagged changes it builds at 0"
        )
    nobs = len(values)
    if nobs - 2 * lags + 1 < 1:
        raise ValueError(f"{lags} lags leave no degrees of freedom in {nobs} observations")
    critical = ztcrit(nobs, order)
    changes = np.diff(values)
    lagged = np.column_stack([_zero_lag(changes, k) for k in range(1, lags + 1)])[lags:]
    level = values[1:][lags:]
    regressors = np.column_stack([level[:-1], lagged[1:], np.ones(len(level) - 1)])
    target = level[1:]
    cross = regressors.T @ regressors
    beta = np.linalg.solve(cross, regressors.T @ target)
    resid = target - regressors @ beta
    variance = float(resid @ resid) / (len(target) - regressors.shape[1])
    se = math.sqrt(variance * np.linalg.inv(cross)[0, 0])
    return Jplv7Adf(
        statistic=float((beta[0] - 1) / se),
        ar1=float(beta[0]),
        nobs=len(target),
        lags=lags,
        critical=critical,
    )


def genhurst(series: ArrayLike, q: float = 1, max_t: int = 19) -> float:
    """``genhurst(S, q, maxT)``: Aste's generalized Hurst exponent H(q).

    For each window length ``Tmax`` from 5 to ``max_t``, and each step ``tt``
    from 1 to ``Tmax``, the series is sampled every ``tt`` points. The sampled
    points are fitted with a straight line, the slope is taken off their
    changes and the line off their levels, and the ``q``-th absolute moment of
    the changes is divided by that of the levels. The slope of the log of that
    ratio against the log of ``tt`` is one estimate of ``q·H``, and H is the
    mean of the estimates over every ``Tmax``, divided by ``q``.
    """
    s = np.asarray(series, dtype=float)
    if s.ndim != 1:
        raise ValueError("genhurst takes one series, as genhurst.m takes a 1xT vector")
    length = len(s)
    estimates = []
    for t_max in range(5, max_t + 1):
        steps = np.arange(1, t_max + 1)
        moments = np.empty(t_max)
        for tt in steps:
            # genhurst.m's S((tt+1):tt:L) - S(((tt+1):tt:L)-tt), in 0-based positions.
            ends = np.arange(tt, length, tt)
            changes = s[ends] - s[ends - tt]
            levels = s[np.arange(0, length, tt)]
            n = len(changes) + 1
            x = np.arange(1, n + 1, dtype=float)
            mean_x = x.sum() / n
            ss_xx = (x**2).sum() - n * mean_x**2
            mean_y = levels.sum() / n
            ss_xy = (x * levels).sum() - n * mean_x * mean_y
            slope = ss_xy / ss_xx
            intercept = mean_y - slope * mean_x
            detrended_changes = changes - slope
            detrended_levels = levels - slope * x - intercept
            moments[tt - 1] = np.mean(np.abs(detrended_changes) ** q) / np.mean(
                np.abs(detrended_levels) ** q
            )
        log_x = np.log10(steps)
        mean_log_x = log_x.mean()
        ss_xx = (log_x**2).sum() - t_max * mean_log_x**2
        log_m = np.log10(moments)
        ss_xy = (log_x * log_m).sum() - t_max * mean_log_x * log_m.mean()
        estimates.append(ss_xy / ss_xx)
    return float(np.mean(estimates) / q)


def vratiotest(
    y: ArrayLike, period: int = 2, *, iid: bool = False, alpha: float = 0.05
) -> VarianceRatio:
    """MATLAB's ``vratiotest(y)`` at one ``period``: Lo and MacKinlay's variance ratio test.

    ``y`` is a level, such as a log price, and its one-step changes are the
    returns. They are trimmed to the first ``N = floor((len(y) − 1) / period)
    · period``, and the drift is the mean change over those ``N``. The ratio is
    the overlapping ``period``-step variance, over
    ``period·(N − period + 1)·(1 − period/N)``, against the one-step variance
    over ``N − 1``. Under ``iid`` the ratio's variance is
    ``2(2q − 1)(q − 1)/(3q)``. Otherwise it is the heteroskedasticity-consistent
    ``4 Σ (1 − k/q)² δ(k)``, where ``δ(k)`` is ``N`` times the sum of products
    of squared demeaned returns ``k`` apart, over the squared sum of squares.
    The statistic is ``√N (ratio − 1)`` over the root of that variance, and the
    p-value is two-sided.
    """
    values = np.asarray(y, dtype=float)
    if not np.all(np.isfinite(values)):
        raise ValueError(
            "vratiotest takes a series with no missing value. MATLAB deletes one, which joins "
            "the returns either side of it, so say which series is meant"
        )
    num_obs = len(values)
    if period < 2:
        raise ValueError(f"vratiotest takes a period of at least 2, not {period}")
    if period >= num_obs / 2:
        raise ValueError(
            f"vratiotest needs more than twice the period, {period}, in observations, not {num_obs}"
        )
    returns = np.diff(values)
    n = ((num_obs - 1) // period) * period
    drift = (values[n] - values[0]) / n
    e1 = returns[:n] - drift
    sse1 = float(e1 @ e1)
    var1 = sse1 / (n - 1)
    e2 = values[period : n + 1] - values[: n - period + 1] - period * drift
    var2 = float(e2 @ e2) / (period * (n - period + 1) * (1 - period / n))
    ratio = var2 / var1
    if iid:
        ratio_var = 2 * (2 * period - 1) * (period - 1) / (3 * period)
    else:
        ratio_var = 4 * sum(
            (1 - k / period) ** 2 * n * float(e1[k:] ** 2 @ e1[: n - k] ** 2) / sse1**2
            for k in range(1, period)
        )
    statistic = math.sqrt(n) * (ratio - 1) / math.sqrt(ratio_var)
    p_value = float(2 * norm.cdf(-abs(statistic)))
    return VarianceRatio(
        rejects=p_value <= alpha,
        p_value=p_value,
        statistic=statistic,
        ratio=ratio,
        period=period,
        nobs=n,
    )
