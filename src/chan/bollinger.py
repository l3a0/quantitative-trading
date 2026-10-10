"""Bollinger bands on GLD and USO, *Algorithmic Trading*'s Example 3.2.

Example 3.1 holds a position in proportion to how far the spread sits from its
average, so it is always in the market and always rebalancing. Chan's Example
3.2, at Kindle location 1559, trades the same GLD and USO price spread with a
Bollinger band instead. It enters one unit when the spread's z-score passes
one standard deviation and holds it until the spread crosses back through its
moving average, where the z-score is 0. The book reports "APR = 17.8 percent, and Sharpe ratio of
0.96, quite an improvement from the linear mean reversal strategy".

**The transcription.** Chan's ``bollinger.m`` is git blob ``6d80817`` under
``public/img/book2/`` in the mirror
[ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) at
``e4bc46f``, and under ``archived/matlab/`` in
[ivanliu1989/algorithmic_trading](https://github.com/ivanliu1989/algorithmic_trading)
at ``4567024``. ``fillMissingData.m`` is blob ``88632fc`` in both. Against
``PriceSpread.m``, the script changes only how ``numUnits`` is set, so
everything before and after it is :mod:`chan.price_spread`'s.

1. :func:`chan.price_spread.price_spread` builds ``yport = USO − h·GLD`` on
   the 1,480 rows left once the first 20 are dropped, with ``h`` refitted over
   the last 20 rows.
2. :func:`chan.price_spread.zscore` is ``(yport − movingAvg(yport, 20)) ./
   movingStd(yport, 20)``.
3. A long enters at ``zScore < −entryZscore`` and exits at ``zScore >
   −exitZscore``. A short enters at ``zScore > entryZscore`` and exits at
   ``zScore < exitZscore``. With :data:`ENTRY_ZSCORE` at 1 and
   :data:`EXIT_ZSCORE` at 0, that is ``< −1``, ``> 0``, ``> 1`` and ``< 0``. A
   NaN z-score compares false on all four, which covers the first 19 kept rows.
4. :func:`band_units` turns the four arrays into ``numUnits``. A long side
   starts at 0 on row 1, takes 1 on an entry and 0 on an exit, and carries its
   last value over every other row. The short side is the mirror with −1, and
   ``numUnits`` is their sum.
5. The positions, the return on yesterday's dollars over the gross dollars
   held, and the APR and Sharpe ratio are :func:`chan.price_spread.daily_returns`
   and :class:`chan.price_spread.Run`, as in Example 3.1.

:func:`band_units` takes the four boolean arrays rather than a z-score and two
thresholds because the Kalman filter example's ``KF_beta_EWA_EWC.m`` compares
the filter's error with ``±sqrt(Q)`` directly, and its exits sit on the entry band.
Dividing that error by ``sqrt(Q)`` to make a z-score would be a different
floating-point comparison from Chan's, so :mod:`chan.kalman_hedge` builds its
own four arrays and calls the same function, under
[issue 342](https://github.com/l3a0/quantitative-trading/issues/342).
:mod:`chan.vx_es` calls it too, for VX against ES under
[issue 350](https://github.com/l3a0/quantitative-trading/issues/350), with each
exit on the opposite entry band.

**The divisor moves both figures here.** Example 3.1's return is profit over
gross dollars, so a constant on every unit cancels and ``movingStd``'s n − 1
gives the same figures as ``smartMovingStd``, which divides by n.
This rule compares the z-score with a fixed threshold, so a different scale
changes which days trade. ``bollinger.m`` calls ``movingStd``, so n − 1 is the
transcription, and ``tests/test_bollinger.py`` holds the n reading beside it as
a diagnostic.

**Chan's Python port is not carried.** ``bollinger.py`` in
``PythonCodesAndData.zip`` exits a long at ``zScore > −entryZscore`` where the
MATLAB reads ``−exitZscore``, and keeps the first 20 rows. The MATLAB script
lands both of its comment's figures, so the port explains no miss.

**What changed on the way over.** Three things, and none moves a figure.

1. The file is read as committed vintages through
   :func:`chan.price_spread.read_sources` rather than loaded from the ``.mat``.
2. The plot of cumulative returns, Figure 3.3, is not carried. The run prints
   and draws nothing, and :mod:`chan.bollinger_figures` draws it for the post.
3. ``fillMissingData`` is written inside :func:`band_units` rather than as a
   helper, because nothing else here forward-fills an array of units.

The vintage and the scale-break guard are Example 3.1's, and
:mod:`chan.price_spread` describes both.

Every result here is exploratory. Reproducing Chan's figures spends the 2006
to 2012 sample on a rule he chose, with a lookback he tuned on that sample,
so the run says whether his numbers reproduce on his file and nothing about
whether the rule pays today.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from chan.price_spread import (
    BOOK_PRICE_SPREAD,
    LOOKBACK,
    SCRIPT_PRICE_SPREAD,
    X_SYMBOL,
    Y_SYMBOL,
    Run,
    Signal,
    daily_returns,
    linear_mean_reversion,
    price_spread,
    read_sources,
    zscore,
)
from chan.series import WindowCrossesScaleBreak, vintage_line
from chan.vintage import VintageEntry, VintageUnavailable

#: ``entryZscore`` and ``exitZscore`` in ``bollinger.m``.
ENTRY_ZSCORE = 1
EXIT_ZSCORE = 0

#: What ``bollinger.m``'s closing comment prints, ``APR=%f Sharpe=%f``.
SCRIPT_BOLLINGER = ("0.178249", "0.964673")
#: What location 1559 prints: "APR = 17.8 percent, and Sharpe ratio of 0.96".
BOOK_BOLLINGER = (17.8, 0.96)


@dataclass(frozen=True)
class ExampleThreeTwo:
    """The Bollinger band on the price spread, the z-score it traded on, and Example 3.1's
    linear rule on the same spread for the book's comparison."""

    bollinger: Run
    zscore: np.ndarray
    linear: Run


def band_units(
    longs_entry: np.ndarray,
    longs_exit: np.ndarray,
    shorts_entry: np.ndarray,
    shorts_exit: np.ndarray,
) -> np.ndarray:
    """``numUnits`` from four boolean arrays of entries and exits, as ``bollinger.m`` sets it.

    Each side starts as NaN with row 1 set to 0, takes its entry value on an
    entry row and 0 on an exit row, in that order, so an exit wins a row that
    holds both. ``fillMissingData`` then carries the last value forward over
    every row still NaN. The long side enters at 1 and the short side at −1,
    and the units are their sum, so a long and a short held together net to 0.
    """
    arrays = [np.asarray(each) for each in (longs_entry, longs_exit, shorts_entry, shorts_exit)]
    if any(each.dtype != bool for each in arrays):
        raise ValueError("band_units takes four boolean arrays")
    if len({each.shape for each in arrays}) != 1 or arrays[0].ndim != 1:
        raise ValueError("band_units takes four one-dimensional arrays of one length")
    longs_entry, longs_exit, shorts_entry, shorts_exit = arrays

    def one_side(entry: np.ndarray, exit_: np.ndarray, held: float) -> np.ndarray:
        units = np.full(len(entry), np.nan)
        units[0] = 0.0
        units[entry] = held
        units[exit_] = 0.0
        # fillMissingData: from the second row, a cell that is not finite takes
        # the previous row's value.
        for t in range(1, len(units)):
            if not np.isfinite(units[t]):
                units[t] = units[t - 1]
        return units

    return one_side(longs_entry, longs_exit, 1.0) + one_side(shorts_entry, shorts_exit, -1.0)


def bollinger_band(
    signal: Signal,
    lookback: int = LOOKBACK,
    entry: float = ENTRY_ZSCORE,
    exit_: float = EXIT_ZSCORE,
) -> tuple[Run, np.ndarray]:
    """Hold one unit of ``signal``'s portfolio between a band's entry and its exit.

    Returns the run and the z-score it traded on.
    """
    z = zscore(signal.value, lookback)
    with np.errstate(invalid="ignore"):
        units = band_units(z < -entry, z > -exit_, z > entry, z < exit_)
    positions = units[:, None] * signal.unit_dollars
    return Run(signal, units, positions, daily_returns(positions, signal.prices)), z


def example_three_two(closes: pd.DataFrame, lookback: int = LOOKBACK) -> ExampleThreeTwo:
    """Run ``bollinger.m`` on a frame holding GLD and USO, and ``PriceSpread.m`` beside it."""
    x = closes[X_SYMBOL].to_numpy(dtype=float)
    y = closes[Y_SYMBOL].to_numpy(dtype=float)
    signal = price_spread(closes.index, x, y, lookback)
    run_, z = bollinger_band(signal, lookback)
    return ExampleThreeTwo(bollinger=run_, zscore=z, linear=linear_mean_reversion(signal, lookback))


def report(members: list[VintageEntry], result: ExampleThreeTwo) -> None:
    """Print the source, the rule, and each figure beside what Chan printed."""
    days = result.bollinger.signal.days
    print(
        "Bollinger bands on the GLD and USO price spread, Chan's Example 3.2 in Algorithmic Trading"
    )
    for entry in members:
        print(f"  {entry.symbol:<8} {vintage_line(entry)}, lifted from {entry.source_workbook}")
    print(
        f"  window   {days[0].date()} to {days[-1].date()}, {len(days)} trading days after "
        f"the first {LOOKBACK} are dropped"
    )
    print(
        f"  rule     one unit of USO minus h GLD, entered at a {LOOKBACK}-day z-score beyond "
        f"{ENTRY_ZSCORE} and exited at {EXIT_ZSCORE}"
    )
    print()
    rows = [
        ("Bollinger band", result.bollinger, SCRIPT_BOLLINGER, BOOK_BOLLINGER),
        ("Linear rule, Example 3.1", result.linear, SCRIPT_PRICE_SPREAD, BOOK_PRICE_SPREAD),
    ]
    print(f"  {'Figure':<40} {'Computed':>10} {'Script':>10} {'Book':>10}")
    for label, each, script, book in rows:
        print(f"  {label + ', APR':<40} {each.apr:>10.6f} {script[0]:>10} {str(book[0]) + '%':>10}")
        print(
            f"  {label + ', Sharpe ratio':<40} {each.sharpe:>10.6f} {script[1]:>10} {book[1]!s:>10}"
        )
    print()
    print(
        "  Exploratory. Reproducing Chan's figures spends the 2006 to 2012 sample on a rule he "
        "chose, so this says whether"
    )
    print(
        "  his numbers reproduce on his file and nothing about whether the rule pays today. "
        "docs/replication-log.md carries the verdicts."
    )


def run(data_dir: Path | None = None) -> ExampleThreeTwo:
    """Read the two ETFs, run ``bollinger.m`` and print the report."""
    members, closes = read_sources(data_dir)
    result = example_three_two(closes)
    report(members, result)
    return result


def main() -> None:
    argparse.ArgumentParser(
        description="Bollinger bands on GLD and USO, Example 3.2 of Algorithmic Trading"
    ).parse_args()
    try:
        run()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source is worth nothing at the bottom of a
        # traceback, so it reaches the reader as one line, the way
        # chan.price_spread.main does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
