"""The regression and unit-root primitives every replication here builds on.

A replication that rolls its own least squares is a second implementation of
the calculation, and two implementations drift without either one looking
wrong. So the estimators live here once and the replications call them:

- ``ols``, ordinary least squares returning coefficients, their standard
  errors, and residuals, via ``statsmodels.api.OLS``.
- ``adf_tstat``, the Augmented Dickey-Fuller unit-root t-statistic, via
  ``statsmodels.tsa.stattools.adfuller`` at a fixed lag.
- ``ou_half_life``, the Ornstein-Uhlenbeck mean-reversion half-life, which is
  an AR(1) regression through the same ``ols``.
- ``ADF_CRIT_CONST`` and ``EG_CRIT_N2``, MacKinnon (2010) asymptotic critical
  values for the plain ADF test and for the Engle-Granger residual test on two
  series.

The fixed lag in ``adf_tstat`` is the load-bearing choice, not a default worth
copying past. Chan reports that Python disagreed with MATLAB and R on the
GLD/GDX verdict and concludes Python's statistics packages cannot be trusted.
The disagreement is real and it is a setting. ``statsmodels`` defaults to
``autolag='aic'``, which reads the lag count off the data and picked six on
the short window, while MATLAB and R fix it at one. Each extra lag pulls the
statistic toward zero, and six was enough to flip the verdict. Pin the lag and
all three agree.

This module imports nothing else in ``chan``, so any replication can build on
it without a dependency running backwards.
"""

from __future__ import annotations

import math
import warnings
from dataclasses import dataclass

import numpy as np
import statsmodels.api as sm
from numpy.typing import NDArray
from statsmodels.tsa.stattools import adfuller

# MacKinnon (2010) asymptotic critical values.
#
# Standard ADF unit-root test on a single series, constant, no trend.
ADF_CRIT_CONST: dict[str, float] = {"1%": -3.43, "5%": -2.86, "10%": -2.57}
# Engle-Granger residual-based test: N=2 I(1) variables, a constant in the
# cointegrating regression, no trend. More demanding than the plain ADF values
# because the spread was itself estimated. A fitted hedge ratio mechanically
# makes residuals look more stationary.
EG_CRIT_N2: dict[str, float] = {"1%": -3.90, "5%": -3.34, "10%": -3.04}


@dataclass(frozen=True)
class OLSFit:
    """Coefficients, their standard errors, and residuals from one OLS fit."""

    beta: NDArray[np.float64]
    se: NDArray[np.float64]
    resid: NDArray[np.float64]


def ols(y: NDArray[np.float64], x: NDArray[np.float64]) -> OLSFit:
    """Ordinary least squares of ``y`` on the columns of ``x``.

    There is no implicit intercept. Add a column of ones when one is wanted,
    which is what makes the two GLD/GDX specifications distinguishable at the
    call site rather than hidden in a flag.
    """
    res = sm.OLS(np.asarray(y, dtype=float), np.asarray(x, dtype=float)).fit()
    return OLSFit(
        beta=np.asarray(res.params, dtype=float),
        se=np.asarray(res.bse, dtype=float),
        resid=np.asarray(res.resid, dtype=float),
    )


def adf_tstat(
    series: NDArray[np.float64], lags: int = 1, *, constant: bool = True
) -> tuple[float, int]:
    """Augmented Dickey-Fuller t-statistic on the lagged-level coefficient.

    Runs ``statsmodels.tsa.stattools.adfuller`` at a fixed lag (``maxlag=lags,
    autolag=None``), for the reason the module docstring gives.

    Returns ``(tstat, nobs)``. A large negative ``tstat`` is evidence against a
    unit root, which is to say evidence for mean reversion. Pass
    ``constant=False`` for regression residuals, which are mean-zero by
    construction and so take no deterministic term.
    """
    with warnings.catch_warnings():
        # adfuller warns that its return type will change in a future release.
        # Only the tuple's stat and nobs are read here, so silence it.
        warnings.simplefilter("ignore", FutureWarning)
        result = adfuller(
            np.asarray(series, dtype=float),
            maxlag=lags,
            autolag=None,  # type: ignore[arg-type]  # the stub over-narrows autolag to str
            regression="c" if constant else "n",
        )
    return float(result[0]), int(result[3])  # type: ignore[arg-type]  # adfuller's tuple is untyped


def ou_half_life(spread: NDArray[np.float64]) -> float:
    """Ornstein-Uhlenbeck mean-reversion half-life, in the series' own steps.

    Trading days, for everything here. Regress the change ``d_z_t`` on the
    lagged level ``z_{t-1}``; the slope is ``-theta`` and the half-life is
    ``ln(2)/theta``. Returns ``+inf`` when the spread does not mean-revert,
    meaning a non-negative slope.
    """
    z = np.asarray(spread, dtype=float)
    dz = np.diff(z)
    zlag = z[:-1]
    design = np.column_stack([zlag, np.ones(len(zlag))])
    fit = ols(dz, design)
    slope = float(fit.beta[0])  # == -theta
    if slope >= 0:
        return math.inf
    return math.log(2.0) / (-slope)
