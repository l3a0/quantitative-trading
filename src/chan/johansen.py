"""The Johansen cointegration test, as LeSage's ``johansen.m`` computes it.

The Engle-Granger and CADF tests in :mod:`chan.pair_cointegration` take two
series and one regression, so they find at most one hedge ratio, and which leg
is the dependent one changes the answer. The Johansen test takes any number of
series at once and counts how many independent stationary combinations they
hold. Each combination is an eigenvector of one matrix, and the eigenvector is
the hedge ratio, one weight per series. Chan's *Algorithmic Trading* uses it
from Example 2.7 onward, always through ``johansen(y, 0, 1)`` from James
LeSage's jplv7 toolbox.

**What runs.** :func:`johansen` calls
``statsmodels.tsa.vector_ar.vecm.coint_johansen``. Its critical-value tables,
``c_sja`` and ``c_sjt``, are LeSage's, and statsmodels' ``coint_tables`` module
carries his MATLAB header verbatim. Its detrending and lag matrix are not
checked line by line against his ``johansen.m``. What vouches for them is
that they land every statistic, critical value and eigenvalue
``cointegrationTests.m`` prints for EWA, EWC and IGE, which
``tests/test_etf_cointegration.py`` pins. They also land every statistic,
critical value and eigenvector ``indexArb.m`` prints for its basket of stocks
against SPY, in log prices, which ``tests/test_index_arbitrage.py`` pins.
Nothing is ported. ``p`` is the
deterministic term, as LeSage names it: −1 for none, 0 for a constant, 1 for a
constant and a trend. ``k`` is the number of lagged differences. Chan's
printouts check ``p = 0`` and ``k = 1`` only, the values every book-two script
passes, so a ``p`` of −1 or 1 or another ``k`` has nothing here vouching for
it.

Three things the wrapper adds, each because statsmodels' own answer would
reach a caller in a worse form.

1. **The figures come back real.** statsmodels takes the eigenvalues from
   ``np.linalg.eig`` on a non-symmetric matrix. From numpy 2.5, which
   ``uv.lock`` pins, that hands back a complex array even when every
   eigenvalue is real, so statsmodels' eigenvalues and eigenvectors carry a
   ``+0j`` and its statistics warn. numpy 2.4 and earlier hand back reals there.
   The wrapper refuses any non-zero imaginary part by message and returns real
   arrays under either.
2. **A price that is not a finite number is refused by name.** statsmodels
   raises ``LinAlgError: SVD did not converge`` on a single NaN, which names
   neither the column nor the row. A panel read by
   :func:`chan.series.load_panel` holds NaN wherever a member was not yet
   listed, so the refusal names the column and the first row.
3. **``p`` and the series count must have critical values.** statsmodels
   warns and carries on outside −1, 0 and 1, and past twelve series, and
   hands back NaN critical values, every one for a ``p`` of 2 and the first
   row for thirteen series. A NaN bar fails every comparison silently, so the
   wrapper refuses both.

**The sign of an eigenvector is statsmodels', not MATLAB's.** statsmodels
multiplies the whole eigenvector matrix by the sign of its top-left element
(statsmodels issue 5517), so that element always comes back positive. MATLAB's
``eig`` makes no such promise, and on Chan's triplet it gave −1.0460 there, so
every vector of his printout comes back here with its sign flipped. On
``indexArb.m``'s basket it gave 1.0939, already positive, so those come back
with his signs. A stationary
combination is still stationary when negated, and the half-life and the
strategy Chan runs on it do not move, which the tests hold.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray
from statsmodels.tsa.vector_ar.vecm import coint_johansen

#: The columns of each critical-value array, in statsmodels' and LeSage's order.
LEVELS = (90, 95, 99)

#: LeSage's tables stop at twelve series.
MOST_SERIES = 12


@dataclass(frozen=True)
class Johansen:
    """One Johansen test, row i of each statistic testing the null r ≤ i.

    ``trace_critical`` and ``eigen_critical`` hold one row per null and one
    column per entry of :data:`LEVELS`. ``eigenvectors`` holds one vector per
    column, ordered by decreasing eigenvalue. Chan expects column 0 to revert
    fastest, and on his ETFs it does, but a larger eigenvalue does not
    guarantee a shorter half-life, so a caller that needs the fastest measures
    it.
    """

    trace: NDArray[np.float64]
    trace_critical: NDArray[np.float64]
    eigen: NDArray[np.float64]
    eigen_critical: NDArray[np.float64]
    eigenvalues: NDArray[np.float64]
    eigenvectors: NDArray[np.float64]

    def relations(self, statistic: str, level: int) -> int:
        """How many cointegrating relations one statistic finds at one level.

        The nulls r ≤ 0, r ≤ 1, and so on are tested in order, and the count is
        how many are rejected before the first that is not. A null rejected
        after one that was not adds nothing, because the test stops at the
        first rank it cannot rule out.
        """
        if statistic not in ("trace", "eigen"):
            raise ValueError(f"the statistic is 'trace' or 'eigen', not {statistic!r}")
        if level not in LEVELS:
            raise ValueError(f"the level is one of {LEVELS}, not {level}")
        values = self.trace if statistic == "trace" else self.eigen
        critical = (self.trace_critical if statistic == "trace" else self.eigen_critical)[
            :, LEVELS.index(level)
        ]
        count = 0
        for value, bar in zip(values, critical, strict=True):
            if not value > bar:
                break
            count += 1
        return count


def _real(values: NDArray, what: str) -> NDArray[np.float64]:
    if np.iscomplexobj(values):
        if np.any(values.imag != 0):
            raise ValueError(
                f"the Johansen {what} came back complex, so the matrix has no real "
                "eigen-decomposition and no hedge ratio to read"
            )
        return values.real.copy()
    return np.asarray(values, dtype=float)


def johansen(prices: ArrayLike, p: int = 0, k: int = 1) -> Johansen:
    """LeSage's ``johansen(prices, p, k)``, one series per column of ``prices``."""
    values = np.asarray(prices, dtype=float)
    if values.ndim != 2 or values.shape[1] < 2:
        raise ValueError(
            f"the Johansen test takes a matrix of at least two series as columns, "
            f"not shape {values.shape}"
        )
    if values.shape[1] > MOST_SERIES:
        raise ValueError(
            f"LeSage's critical values stop at {MOST_SERIES} series, and this matrix "
            f"holds {values.shape[1]}"
        )
    if p not in (-1, 0, 1):
        raise ValueError(f"p is -1, 0 or 1, the terms LeSage's tables cover, not {p}")
    if k < 0:
        raise ValueError(f"k counts lagged differences, so it cannot be {k}")
    finite = np.isfinite(values)
    if not finite.all():
        row, column = np.argwhere(~finite)[0]
        raise ValueError(
            f"the Johansen test needs every price finite, and column {column} is "
            f"{values[row, column]} on row {row}"
        )
    with warnings.catch_warnings():
        # statsmodels writes complex eigenvalues into real arrays for the two
        # statistics, and _real below refuses the case where that loses anything.
        warnings.simplefilter("ignore", np.exceptions.ComplexWarning)
        result = coint_johansen(values, p, k)
    return Johansen(
        trace=np.asarray(result.lr1, dtype=float),
        trace_critical=np.asarray(result.cvt, dtype=float),
        eigen=np.asarray(result.lr2, dtype=float),
        eigen_critical=np.asarray(result.cvm, dtype=float),
        eigenvalues=_real(result.eig, "eigenvalues"),
        eigenvectors=_real(result.evec, "eigenvectors"),
    )
