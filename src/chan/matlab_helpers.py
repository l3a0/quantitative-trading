"""Chan's MATLAB helper functions, computed the way his helpers compute them.

Chan's cross-sectional examples lean on a handful of small MATLAB functions he
wrote himself, and on two behaviours of MATLAB that numpy does not share. A
replication that swaps in the numpy default for any of them moves a printed
figure, so each one lives here once, with the case that separates it from the
default held by ``tests/test_matlab_helpers.py``.

The source is Chan's first-edition mirror,
[egorpe/EPChan-QuantitativeTrading](https://github.com/egorpe/EPChan-QuantitativeTrading)
at ``1a71950``, which ``data/README.md`` already names. That mirror's
``smartmean``, ``smartsum`` and ``smartstd`` each take a ``dim`` argument that
Example 7.7 leaves out, which stops MATLAB before it prints anything. The
printed figures match a ``dim`` of 1, so ``axis`` here defaults to 0, the same
reduction down each column. So the mirror's helpers cannot run that script as
shipped, and these are what its printout implies rather than what it executes.

What each one does:

- :func:`smartmean` takes the mean of the finite entries.
- :func:`smartsum` takes the sum of the finite entries, NaN where there are
  none.
- :func:`smartstd` replaces each non-finite entry with zero and then divides by
  n - 1 over every entry. That is not a NaN-skipping standard deviation. A
  month that held no position counts as a month that returned nothing.
- :func:`backshift`, :func:`lag1` and :func:`fwdshift` move rows down or up and
  pad with NaN.
- :func:`matlab_sort` orders a row ascending with NaN last and ties in column
  order.
- :func:`round_half_away` is MATLAB's ``round``. numpy's ``round`` sends a half
  to the even neighbour instead, which is what R's ``round`` does.

[Issue 17](https://github.com/l3a0/quantitative-trading/issues/17) reads the
same S&P 500 file with the same helpers, which is why they are a module of
their own rather than private to one replication.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray


def _finite(x: ArrayLike) -> tuple[NDArray[np.float64], NDArray[np.bool_]]:
    values = np.asarray(x, dtype=float)
    return values, np.isfinite(values)


def smartsum(x: ArrayLike, axis: int = 0) -> NDArray[np.float64] | np.float64:
    """The sum of the finite entries along ``axis``, NaN where none is finite."""
    values, has = _finite(x)
    total = np.where(has, values, 0.0).sum(axis=axis)
    return np.where(has.any(axis=axis), total, np.nan)[()]


def smartmean(x: ArrayLike, axis: int = 0) -> NDArray[np.float64] | np.float64:
    """The mean of the finite entries along ``axis``, NaN where none is finite."""
    values, has = _finite(x)
    count = has.sum(axis=axis)
    total = np.where(has, values, 0.0).sum(axis=axis)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(count > 0, total / count, np.nan)[()]


def smartstd(x: ArrayLike, axis: int = 0) -> NDArray[np.float64] | np.float64:
    """The standard deviation after replacing every non-finite entry with zero.

    It divides by n - 1, where n counts the replaced entries too, because
    Chan's helper zero-fills and then calls MATLAB's ``std``. It is NaN only
    where no entry is finite at all.
    """
    values, has = _finite(x)
    spread = np.where(has, values, 0.0).std(axis=axis, ddof=1)
    return np.where(has.any(axis=axis), spread, np.nan)[()]


def backshift(periods: int, x: ArrayLike) -> NDArray[np.float64]:
    """Each row moved ``periods`` rows later, with NaN in the rows it vacates."""
    if periods < 0:
        raise ValueError(
            f"backshift moves rows later, so periods must be at least 0, not {periods}"
        )
    values = np.asarray(x, dtype=float)
    shifted = np.full_like(values, np.nan)
    shifted[periods:] = values[: len(values) - periods]
    return shifted


def lag1(x: ArrayLike) -> NDArray[np.float64]:
    """Each row moved one row later, which is ``backshift(1, x)``."""
    return backshift(1, x)


def fwdshift(periods: int, x: ArrayLike) -> NDArray[np.float64]:
    """Each row moved ``periods`` rows earlier, with NaN in the rows it vacates."""
    if periods < 0:
        raise ValueError(
            f"fwdshift moves rows earlier, so periods must be at least 0, not {periods}"
        )
    values = np.asarray(x, dtype=float)
    shifted = np.full_like(values, np.nan)
    shifted[: len(values) - periods] = values[periods:]
    return shifted


def matlab_sort(x: ArrayLike) -> NDArray[np.intp]:
    """The order MATLAB's ``sort`` puts a row in: ascending, NaN last, ties kept in place.

    numpy already places NaN last. The stable kind is what keeps two equal
    values in the order their columns came in, which the default quicksort
    does not promise.
    """
    return np.argsort(np.asarray(x, dtype=float), kind="stable")


def round_half_away(x: ArrayLike) -> NDArray[np.float64] | np.float64:
    """MATLAB's ``round``, which sends a half away from zero rather than to the even neighbour."""
    values = np.asarray(x, dtype=float)
    return (np.sign(values) * np.floor(np.abs(values) + 0.5))[()]
