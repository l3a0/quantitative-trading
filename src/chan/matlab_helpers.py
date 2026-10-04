"""Chan's MATLAB helper functions, computed the way his helpers compute them.

Chan's cross-sectional examples lean on a handful of small MATLAB functions he
wrote himself, and on two behaviours of MATLAB that numpy does not share. Each
lives here once, with the case that separates it from the numpy default held by
``tests/test_matlab_helpers.py``.

Three of them move a figure Examples 7.6 and 7.7 print, and
``tests/test_equity_seasonals.py`` pins what each move gives.

1. :func:`smartstd_first_edition`'s zero-fill moves the first edition's 7.7
   Sharpe ratio.
2. :func:`smartstd_book_two` moves the revised edition's 7.7 Sharpe ratio,
   against :func:`smartstd_first_edition`.
3. :func:`round_half_away` moves the first edition's January 2006 return,
   against the floor.

Chan's two books ship two different ``smartstd`` files under one name, and
each is what its own printouts imply, so both live here under names that say
which book each belongs to. :func:`smartstd_first_edition` is the first
edition of *Quantitative Trading*'s. :func:`smartstd_book_two` is *Algorithmic
Trading*'s, and choosing it over the first edition's moves a figure Example 7.2
prints, which ``tests/test_pead.py`` pins, both figures Example 4.1 prints,
which ``tests/test_buy_on_gap.py`` pins, and the revised Example 7.7 Sharpe
ratio above. The revised edition's Example 7.4
prints a Sharpe ratio that :func:`smartstd_book_two` lands and the first
edition's misses, and the repost of its code named below carries book two's
file, so :mod:`chan.pca_factor` calls :func:`smartstd_book_two`.
``tests/test_pca_factor.py`` pins the figure the first edition's would give.

The rest are Chan's helpers as his scripts call them. :func:`smartmean`,
:func:`smartsum`, :func:`lag1` and :func:`matlab_sort` run in Example 7.7,
and the first three run in Examples 3.7 and 3.8 in :mod:`chan.khandani_lo` too.
:func:`backshift` runs through :func:`lag1` there, and :mod:`chan.pead` calls
it, :func:`smartmean` and :func:`smartsum` directly for *Algorithmic
Trading*'s Example 7.2. :mod:`chan.pca_factor` calls :func:`backshift`,
:func:`smartmean`, :func:`smartsum` and :func:`matlab_sort` for Example 7.4.
:mod:`chan.cross_sectional_momentum` calls :func:`backshift`, :func:`lag1`,
:func:`smartmean`, :func:`smartsum`, :func:`matlab_sort` and
:func:`round_half_away` for *Algorithmic Trading*'s Example 6.2.
:mod:`chan.buy_on_gap` calls :func:`backshift`, :func:`smartsum` and
:func:`matlab_sort` for *Algorithmic Trading*'s Example 4.1.
:mod:`chan.khandani_lo_book_two` calls :func:`backshift`, :func:`smartmean`
and :func:`smartsum` for *Algorithmic Trading*'s Examples 4.3 and 4.4.
:func:`fwdshift` has no caller
yet. It is carried because Chan's ``example7_6.m`` calls it, and the build here
finds month-ends by comparing each row with the next instead. Reversing the
tie order in :func:`matlab_sort` moves no printed figure on these files. On
the 2012 S&P 500 file Example 4.1 reads, no two stocks qualifying on one day
tie at all, on either side, so it moves nothing there either.

The source is Chan's first-edition mirror,
[egorpe/EPChan-QuantitativeTrading](https://github.com/egorpe/EPChan-QuantitativeTrading)
at ``1a71950``, which ``data/README.md`` already names. That mirror's
``smartmean``, ``smartsum`` and ``smartstd`` each take a ``dim`` argument that
Example 7.7 leaves out, which stops MATLAB before it prints anything. Example
7.4's ``smartmean(ret)`` leaves it out the same way. The
printed figures match a ``dim`` of 1, so ``axis`` here defaults to 0, the same
reduction down each column. So the mirror's helpers cannot run either script as
shipped, and these are what its printout implies rather than what it executes.

What each one does:

- :func:`smartmean` takes the mean of the finite entries.
- :func:`smartsum` takes the sum of the finite entries, NaN where there are
  none.
- :func:`smartstd_first_edition` replaces each non-finite entry with zero and
  then divides by n - 1 over every entry. That is not a NaN-skipping standard
  deviation. A month that held no position counts as a month that returned
  nothing.
- :func:`backshift`, :func:`lag1` and :func:`fwdshift` move rows down or up and
  pad with NaN.
- :func:`matlab_sort` orders a row ascending with NaN last and ties in column
  order.
- :func:`round_half_away` is MATLAB's ``round``. numpy's ``round`` sends a half
  to the even neighbour instead, which is what R's ``round`` does.

They are a module of their own rather than private to one replication,
because Examples 3.7 and 3.8 call the same helpers on the same file.

**Book two's helpers.** Five come from Chan's *Algorithmic Trading* code
rather than his first edition's. :mod:`chan.pead` calls the first three,
:mod:`chan.buy_on_gap` calls all but :func:`smartstd_book_two` directly and
runs it through :func:`smart_moving_std`,
:mod:`chan.cross_sectional_momentum` calls :func:`smartstd_book_two` and
:func:`calculate_max_dd`, and :mod:`chan.pca_factor` and
:mod:`chan.equity_seasonals` call :func:`smartstd_book_two`, the second for
the revised edition's Example 7.7.
The revised edition of
*Quantitative Trading* reposted at pinhaocheng/epchan-quant_trading_MATLAB_codes
``7430b84`` carries ``smartstd.m``, ``smartmean.m``, ``smartsum.m``,
``backshift.m`` and ``fillMissingData.m`` identical to book two's once line
endings are stripped, measured on
[issue 21](https://github.com/l3a0/quantitative-trading/issues/21).

- :func:`smartstd_book_two` skips each non-finite entry and divides by n, the
  count of finite entries, rather than n - 1.
- :func:`smart_moving_std` is ``smartMovingStd``, book two's standard deviation
  over a trailing window of rows, NaN until the window first fills.
- :func:`calculate_max_dd` is ``calculateMaxDD``, the deepest drawdown of a
  compounded cumulative return and the longest run of days spent below a high.
  :func:`drawdown_path` is its loop, returning each day's high, drawdown and
  duration, so a caller that needs to know where the longest run falls reads
  the same calculation rather than a second copy of it.
- :func:`calculate_returns` is ``calculateReturns``, each row's simple return
  over the row ``lag`` rows before it.
- :func:`smart_moving_avg` is ``smartMovingAvg``, the mean of the finite
  entries over a trailing window of rows, NaN until the window first fills.

Book two's ``smartmean``, ``smartsum`` and ``backshift`` compute what the first
edition's do, so they are not carried twice.

They are ported from ``smartstd.m``, ``smartMovingStd.m`` and
``calculateMaxDD.m`` under ``archived/matlab/`` in the mirror
[ivanliu1989/algorithmic_trading](https://github.com/ivanliu1989/algorithmic_trading)
at ``45670240f1f3d4b5233a75f82fd18b742455b4bb``. The mirror
[ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) at
``e4bc46f`` holds the same three files under ``public/img/book2/``, identical
once line endings are stripped. ``data/README.md`` names both mirrors for the
data files. The port landed here with
[PR #263](https://github.com/l3a0/quantitative-trading/pull/263). Four things
changed on the way over.

1. ``smartstd``'s ``dim`` becomes ``axis``, with 0 as the default, as the
   first edition's helpers here already do. MATLAB's default is the first
   dimension longer than one, which is the same reduction on every shape
   Examples 7.2 and 4.1 pass.
2. ``smartMovingStd``'s optional third argument, which samples every
   ``period`` rows, is not carried, because neither ``pead.m`` nor ``bog.m``
   passes it.
3. ``smartMovingStd`` refuses a window of one row. MATLAB would hand that
   one-row slice to ``smartstd`` with no ``dim``, which then reduces across the
   columns rather than down them, a different calculation that nothing calls.
4. ``calculateMaxDD`` hands its duration back as a whole number of days
   rather than as a double, which is the value ``pead.m`` prints after its
   ``round``.

``calculateReturns.m`` and ``smartMovingAvg.m`` came later, from the same
directory of the same mirror at the same commit, for Example 4.1's ``bog.m``.
EpchanPreview holds both under ``public/img/book2/`` and again under
``public/img/book2/Utilities/``, all three copies identical once line endings
are stripped. They landed here with
[PR #307](https://github.com/l3a0/quantitative-trading/pull/307), for
[issue 295](https://github.com/l3a0/quantitative-trading/issues/295). Three
things changed on the way over.

1. ``smartMovingAvg``'s optional third argument, which samples every
   ``period`` rows, is not carried, because ``bog.m`` never passes it.
2. ``smartMovingAvg``'s ``assert(T>0)`` becomes a refusal that names the
   window.
3. ``calculateReturns``' commented-out log return is not carried.

``smartMovingAvg`` adds the window's rows one at a time, the current row first,
and :func:`smart_moving_avg` adds them in the same order, so each mean is the
same double rather than numpy's pairwise sum.

``calculateMaxDD``'s two quirks are kept, because they are what Chan's code
does. Its high-water mark starts at zero rather than at the first day's
return, and its loop starts on the second row, so the first day can never be
in a drawdown. Neither moves a figure ``pead.m`` prints, because its first
day returns nothing, so ``tests/test_matlab_helpers.py`` holds both on inputs
where they do.

One behaviour of MATLAB is carried rather than numpy's. MATLAB's ``min``
skips a NaN, so a day whose cumulative return is NaN leaves the deepest
drawdown standing, where numpy's ``min`` would return NaN.
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


def smartstd_first_edition(x: ArrayLike, axis: int = 0) -> NDArray[np.float64] | np.float64:
    """*Quantitative Trading*'s ``smartstd``: zero-fill every non-finite entry, then take ``std``.

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


def smartstd_book_two(x: ArrayLike, axis: int = 0) -> NDArray[np.float64] | np.float64:
    """*Algorithmic Trading*'s ``smartstd``: the spread of the finite entries, over n.

    n counts the finite entries only, so a non-finite entry is skipped rather
    than read as zero, and the result is not the n - 1 estimate that
    :func:`smartstd_first_edition` gives. It is computed the way the ``.m``
    file computes it, as the mean of the squared deviations from the mean, both
    means taken by :func:`smartmean`. It is NaN where no entry is finite.
    """
    values = np.asarray(x, dtype=float)
    centred = values - np.expand_dims(smartmean(values, axis=axis), axis)
    return np.sqrt(smartmean(centred * centred, axis=axis))[()]


def smart_moving_std(x: ArrayLike, lookback: int) -> NDArray[np.float64]:
    """``smartMovingStd``: :func:`smartstd_book_two` over each trailing window of ``lookback`` rows.

    Row t holds the spread of rows t - lookback + 1 through t, column by column,
    and the first ``lookback - 1`` rows are NaN because no window has filled.
    A window that holds fewer than ``lookback`` finite entries still gives a
    spread, because ``smartstd`` skips what is not finite rather than refusing.
    """
    values = np.asarray(x, dtype=float)
    if lookback < 2:
        raise ValueError(
            f"smart_moving_std takes a window of at least 2 rows, not {lookback}, because "
            "MATLAB reduces a one-row window across its columns"
        )
    spread = np.full_like(values, np.nan)
    for t in range(lookback - 1, len(values)):
        spread[t] = smartstd_book_two(values[t - lookback + 1 : t + 1], axis=0)
    return spread


def calculate_returns(prices: ArrayLike, lag: int) -> NDArray[np.float64]:
    """``calculateReturns``: each row's simple return over the row ``lag`` rows before it.

    ``(p − backshift(lag, p)) / backshift(lag, p)``, so the first ``lag`` rows
    are NaN, and so is any row whose price or earlier price is missing.
    """
    values = np.asarray(prices, dtype=float)
    previous = backshift(lag, values)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (values - previous) / previous


def smart_moving_avg(x: ArrayLike, lookback: int) -> NDArray[np.float64]:
    """``smartMovingAvg``: the mean of the finite entries in each trailing ``lookback`` rows.

    Row t holds the mean of whichever of rows t − lookback + 1 through t are
    finite, column by column, and NaN where none is. The first
    ``lookback − 1`` rows are NaN whatever they hold, because the ``.m`` file
    adds a NaN-padded shift of each earlier row and that padding survives the
    division. The sum is taken in the ``.m`` file's order, row t first and then
    each earlier row, so a mean here is the same double MATLAB's is rather than
    numpy's pairwise sum, which can differ in the last bit.
    """
    values = np.asarray(x, dtype=float)
    if lookback < 1:
        raise ValueError(f"smart_moving_avg takes a window of at least 1 row, not {lookback}")
    filled = np.where(np.isfinite(values), values, 0.0)
    total = np.zeros_like(values)
    count = np.zeros_like(values)
    for i in range(lookback):
        total = total + backshift(i, filled)
        count = count + np.isfinite(backshift(i, values))
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(count > 0, total / count, np.nan)


def drawdown_path(
    cumret: ArrayLike,
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.int_]]:
    """``calculateMaxDD``'s loop: each day's high, drawdown and duration below the high.

    :func:`calculate_max_dd` takes the minimum drawdown and the maximum
    duration of these, and its docstring states the rules and the two quirks.
    """
    values = np.asarray(cumret, dtype=float)
    high = np.zeros_like(values)
    drawdown = np.zeros_like(values)
    duration = np.zeros(len(values), dtype=int)
    for t in range(1, len(values)):
        high[t] = max(high[t - 1], values[t])
        drawdown[t] = (1 + values[t]) / (1 + high[t]) - 1
        duration[t] = 0 if drawdown[t] == 0 else duration[t - 1] + 1
    return high, drawdown, duration


def calculate_max_dd(cumret: ArrayLike) -> tuple[float, int]:
    """``calculateMaxDD``: the deepest drawdown and the longest stretch below a high.

    ``cumret`` is a compounded cumulative return, ``cumprod(1 + ret) - 1``. A
    day's drawdown is ``(1 + cumret) / (1 + high) - 1``, where the high is the
    largest ``cumret`` so far, and its duration counts the consecutive days
    that drawdown has been below zero. The deepest drawdown is a fraction no
    greater than zero and the duration is in rows.

    Two quirks of Chan's loop are kept. The high starts at zero rather than at
    the first day's ``cumret``, and the loop starts on the second row, so the
    first day's drawdown and duration are both 0 whatever it returned.
    """
    _, drawdown, duration = drawdown_path(cumret)
    # MATLAB's min skips NaN. The first row is always 0, so the minimum exists.
    return float(np.nanmin(drawdown)), int(duration.max())
