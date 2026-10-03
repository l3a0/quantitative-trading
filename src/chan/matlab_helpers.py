"""Chan's MATLAB helper functions, computed the way his helpers compute them.

Chan's cross-sectional examples lean on a handful of small MATLAB functions he
wrote himself, and on two behaviours of MATLAB that numpy does not share. Each
lives here once, with the case that separates it from the numpy default held by
``tests/test_matlab_helpers.py``.

Two of them move a figure Examples 7.6 and 7.7 print, and
``tests/test_equity_seasonals.py`` pins what each move gives.

1. :func:`smartstd`'s zero-fill moves the first edition's 7.7 Sharpe ratio.
2. :func:`round_half_away` moves the first edition's January 2006 return,
   against the floor.

The rest are Chan's helpers as his scripts call them. :func:`smartmean`,
:func:`smartsum`, :func:`lag1` and :func:`matlab_sort` run in Example 7.7,
and the first three run in Examples 3.7 and 3.8 in :mod:`chan.khandani_lo` too.
:func:`backshift` runs through :func:`lag1`. :func:`fwdshift` has no caller
yet. It is carried because Chan's ``example7_6.m`` calls it, and the build here
finds month-ends by comparing each row with the next instead. Reversing the
tie order in :func:`matlab_sort` moves no printed figure on these files.

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

They are a module of their own rather than private to one replication,
because Examples 3.7 and 3.8 call the same helpers on the same file.
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
    filled = np.where(has, values, 0.0)
    if filled.shape[axis] == 1:
        # MATLAB's ``std`` of one value is 0, where numpy's n - 1 divides by zero.
        spread = np.zeros_like(filled.sum(axis=axis))
    else:
        spread = filled.std(axis=axis, ddof=1)
    return np.where(has.any(axis=axis), spread, np.nan)[()]


def _within(periods: int, x: ArrayLike, name: str) -> NDArray[np.float64]:
    values = np.asarray(x, dtype=float)
    if periods > len(values):
        # MATLAB would hand back more rows than it was given, and nothing here
        # shifts that far, so this refuses rather than copying that.
        raise ValueError(f"{name} by {periods} rows is longer than the {len(values)} given")
    return values


def backshift(periods: int, x: ArrayLike) -> NDArray[np.float64]:
    """Each row moved ``periods`` rows later, with NaN in the rows it vacates."""
    if periods < 0:
        raise ValueError(
            f"backshift moves rows later, so periods must be at least 0, not {periods}"
        )
    values = _within(periods, x, "backshift")
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
    values = _within(periods, x, "fwdshift")
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
    # Adding 0.5 and taking the floor misrounds 0.49999999999999994 to 1, so
    # the fraction is compared against a half instead.
    whole = np.trunc(values)
    return (whole + np.sign(values) * (np.abs(values - whole) >= 0.5))[()]
