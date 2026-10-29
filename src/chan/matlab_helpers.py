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
Trading*'s. Choosing it over the first edition's moves figures in several
examples. One is Example 7.2's, which ``tests/test_pead.py`` pins, and another
is the revised Example 7.7 Sharpe ratio above. The revised edition's Example 7.4
prints a Sharpe ratio that :func:`smartstd_book_two` lands and the first
edition's misses, and the repost of its code named below carries book two's
file, so :mod:`chan.pca_factor` calls :func:`smartstd_book_two`.
``tests/test_pca_factor.py`` pins the figure the first edition's would give.

The rest are Chan's helpers as his scripts call them. A change to one reaches
every module here that imports it, such as
:mod:`chan.cross_sectional_momentum`, which transcribes *Algorithmic Trading*'s
Example 6.2. Its tests pin figures that a helper change can move, so a change
here can fail a replication's own tests as well as
``tests/test_matlab_helpers.py``.

Reversing the tie order in :func:`matlab_sort` moves no printed figure on the
two files Examples 7.6 and 7.7 read. On the 2012 stock file Example 4.1 reads, no
two stocks qualifying on one day tie at all, on either side, so it moves
nothing there either.

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
  pad with NaN. :func:`fwdshift` is carried because Chan's ``example7_6.m``
  calls it, though Example 7.6 here finds month-ends by comparing each row with
  the next instead.
- :func:`matlab_sort` orders a row ascending with NaN last and ties in column
  order.
- :func:`round_half_away` is MATLAB's ``round``. numpy's ``round`` sends a half
  to the even neighbour instead, which is what R's ``round`` does.

They are a module of their own rather than private to one replication,
because Examples 3.7 and 3.8 call the same helpers on the same file.

Six of them live in the shared ``ithildincore`` package rather than in this
file: :func:`smartsum`, :func:`smartmean`, :func:`backshift` and :func:`lag1`,
and the private ``_finite`` and ``_within`` that two helpers here still call.
They moved to ``ithildincore.reversal`` for
[issue 19 there](https://github.com/l3a0/ithildin-core/issues/19), because
ithildin-runtime runs the reversal weights that call them. This module imports
them under the same names, so no module that imports them from here changed,
and their bodies are the ones that were here at ``0237abf2``. A change to one
of them is now a release of that package and a re-pin here.

**Book two's helpers.** Seven come from Chan's *Algorithmic Trading* code
rather than his first edition's. The revised edition of
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
  :func:`drawdown_path` is the calculation inside it, returning each day's
  high, drawdown and duration, so a caller that needs to know where the longest run or the
  deepest drawdown falls reads the same calculation rather than a second copy
  of it.
- :func:`calculate_returns` is ``calculateReturns``, each row's simple return
  over the row ``lag`` rows before it.
- :func:`smart_moving_avg` is ``smartMovingAvg``, the mean of the finite
  entries over a trailing window of rows, NaN until the window first fills.
- :func:`moving_avg` and :func:`moving_std` are ``movingAvg`` and
  ``movingStd``, the plain mean and MATLAB's n − 1 standard deviation over a
  trailing window of rows. Unlike the ``smart`` pair, a NaN anywhere in a
  window makes that row NaN.

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

``movingAvg.m`` and ``movingStd.m`` came for Example 3.1's ``PriceSpread.m``,
``LogPriceSpread.m`` and ``Ratio.m``. Example 3.2's ``bollinger.m`` calls them
too, and so does Example 2.5's ``stationarityTests.m``. They are git blobs
``5b9f933`` and ``2f5f858`` under ``public/img/book2/`` in EpchanPreview at
``e4bc46f`` and under ``archived/matlab/`` in ivanliu1989/algorithmic_trading
at ``4567024``. They landed here for
[issue 340](https://github.com/l3a0/quantitative-trading/issues/340). Other
scripts of Chan's call them as well, such as Example 4.2's ``indexArb.m``,
which [issue 343](https://github.com/l3a0/quantitative-trading/issues/343)
transcribes. Three things changed on the way over.

1. ``movingStd``'s optional third argument, which samples every ``period``
   rows, is not carried, because no script transcribed here passes it.
2. ``movingAvg``'s ``assert(T>0)`` becomes a refusal that names the window,
   and ``movingStd`` refuses a window of one row for the reason
   :func:`smart_moving_std` does.
3. ``movingAvg`` adds the window's rows oldest first, the reverse of
   ``smartMovingAvg``, and :func:`moving_avg` keeps that order.
   :func:`moving_std` takes numpy's ``std``, whose sum can differ from
   MATLAB's in the last bit.

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

# Six of these helpers live in ithildincore, because ithildin-runtime runs the
# reversal weights that call them too. Importing them here keeps every module
# that imports them from chan.matlab_helpers unchanged. smartsum and lag1 are
# only re-exported, which is what the noqa is for. _finite and _within are
# private there and still called by smartstd_first_edition and fwdshift here.
from ithildincore.reversal import (  # noqa: F401
    _finite,
    _within,
    backshift,
    lag1,
    smartmean,
    smartsum,
)
from numpy.typing import ArrayLike, NDArray


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


def moving_avg(x: ArrayLike, lookback: int) -> NDArray[np.float64]:
    """``movingAvg``: the plain mean of each trailing ``lookback`` rows.

    Row t holds the mean of rows t − lookback + 1 through t, column by column,
    and the first ``lookback − 1`` rows are NaN. A NaN in a window makes that
    row NaN, where :func:`smart_moving_avg` would skip it. The sum is taken in
    the ``.m`` file's order, the oldest row first.
    """
    values = np.asarray(x, dtype=float)
    if lookback < 1:
        raise ValueError(f"moving_avg takes a window of at least 1 row, not {lookback}")
    mean = np.full_like(values, np.nan)
    if len(values) < lookback:
        return mean
    total = np.zeros_like(values[lookback - 1 :])
    for i in range(lookback):
        total = total + values[i : len(values) - lookback + 1 + i]
    mean[lookback - 1 :] = total / lookback
    return mean


def moving_std(x: ArrayLike, lookback: int) -> NDArray[np.float64]:
    """``movingStd``: MATLAB's ``std`` of each trailing ``lookback`` rows, which divides by n − 1.

    Row t holds the spread of rows t − lookback + 1 through t, column by column,
    and the first ``lookback − 1`` rows are NaN. A NaN in a window makes that
    row NaN, where :func:`smart_moving_std` would skip it and divide by n.
    """
    values = np.asarray(x, dtype=float)
    if lookback < 2:
        raise ValueError(
            f"moving_std takes a window of at least 2 rows, not {lookback}, because "
            "MATLAB reduces a one-row window across its columns"
        )
    spread = np.full_like(values, np.nan)
    for t in range(lookback - 1, len(values)):
        spread[t] = np.std(values[t - lookback + 1 : t + 1], axis=0, ddof=1)
    return spread


def drawdown_path(
    cumret: ArrayLike,
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.int_]]:
    """``calculateMaxDD``'s loop: each day's high, drawdown and duration below the high.

    :func:`calculate_max_dd` takes the minimum drawdown and the maximum
    duration of these, and its docstring states the rules and the two quirks.

    Chan's ``calculateMaxDD.m`` is a loop over the rows, and this computes the
    same three arrays without one, because a Monte Carlo ensemble in
    :mod:`chan.monte_carlo_leverage` calls it on about 2,000 paths of 100,000
    rows. ``tests/test_matlab_helpers.py`` keeps the loop as the reference and
    holds the two equal bit for bit, NaN rows included.

    1. The high is a running maximum over a leading 0 and rows 2 onward, taken
       with ``np.fmax`` so that a NaN row leaves the high standing, as the
       loop's ``max`` does.
    2. Each drawdown is the loop's own expression on the same two operands, so
       it is the same double.
    3. A day's duration is its distance from the last row whose drawdown is
       exactly 0. The first row's drawdown is 0, so that row always exists,
       and a NaN drawdown is not 0, so it counts as a day below the high.
    """
    values = np.asarray(cumret, dtype=float)
    high = np.zeros_like(values)
    drawdown = np.zeros_like(values)
    duration = np.zeros(len(values), dtype=int)
    if len(values) < 2:
        return high, drawdown, duration
    high[1:] = np.fmax.accumulate(np.concatenate([[0.0], values[1:]]))[1:]
    drawdown[1:] = (1 + values[1:]) / (1 + high[1:]) - 1
    rows = np.arange(len(values))
    last_zero = np.maximum.accumulate(np.where(drawdown == 0, rows, 0))
    duration[:] = rows - last_zero
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
