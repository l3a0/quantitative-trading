"""Price spread, log price spread and ratio on GLD and USO, *Algorithmic Trading*'s Example 3.1.

A pair trade needs a signal that reverts, and there is more than one way to
build it from two prices. Chan's Example 3.1, at Kindle location 1505, runs one
linear mean-reversion rule on the gold ETF GLD and the oil ETF USO three ways,
to show the choice matters. He notes that the two are not cointegrated, and
asks whether there is enough short-term reversion to trade anyway.

1. **The price spread**, ``USO − h·GLD``, with the hedge ratio ``h`` refitted
   every day over the last 20 days. Location 1505 reports "about 10.9 percent
   and Sharpe ratio of about 0.59". The script's own comment prints 0.108335,
   which rounds to 10.8, so the book's 10.9 is not its script's figure
   rounded.
2. **The log price spread**, ``log USO − h·log GLD``, with ``h`` refitted the
   same way on log prices. "The APR of 9 percent and Sharpe ratio of 0.5 are
   actually lower than the ones using the price spread strategy."
3. **The ratio**, ``USO / GLD``, with equal dollars on each side. Chan
   expects it to "perform poorly, with a negative APR".

**The transcription.** Every step is Chan's ``PriceSpread.m``,
``LogPriceSpread.m`` and ``Ratio.m``, read under ``public/img/book2/`` in the
mirror [ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview)
at ``e4bc46f``, git blobs ``522871f``, ``e7706d2`` and ``37565cd``. The mirror
[ivanliu1989/algorithmic_trading](https://github.com/ivanliu1989/algorithmic_trading)
at ``4567024`` holds the same three blobs under ``archived/matlab/``. ``x`` is
GLD's close, ``y`` is USO's and the lookback is 20 rows.

1. :func:`rolling_hedge_ratio` is the slope of ``ols(y, [x ones])`` over the
   20 rows ending at row t, first defined on row 20. ``ols`` is
   :func:`ithildincore.timeseries.ols`, the regression
   :func:`chan.pair_cointegration.engle_granger` fits, which takes the
   intercept column explicitly as Chan's call does.
2. The scripts delete the first 20 rows of every array, so all three run on
   the same 1,480 rows. ``Ratio.m``'s comment says the drop is there "to have
   same test set as price spread and log price spread strategies".
3. ``numUnits = −(signal − movingAvg(signal, 20)) / movingStd(signal, 20)``,
   which is :func:`linear_units`. ``movingAvg`` and ``movingStd`` are
   :func:`chan.matlab_helpers.moving_avg` and
   :func:`chan.matlab_helpers.moving_std`, the plain mean and MATLAB's n − 1
   ``std``, rather than the ``smart`` helpers that skip a NaN.
4. One unit of the portfolio holds ``[−h·x, y]`` dollars for the price spread,
   ``[−h, 1]`` for the log price spread and ``[−1, 1]`` for the ratio, and the
   positions are ``numUnits`` times that. :class:`Signal` carries it as
   ``unit_dollars``.
5. :func:`daily_returns` is ``sum(lag(pos)·(p − lag(p))/lag(p))`` over
   ``sum(|lag(pos)|)``, the profit over the gross dollars held, with a NaN day
   set to 0.

Each script prints two figures with ``%f``, and :class:`Run` carries both.

1. ``prod(1 + ret)^(252 / n) − 1`` over all 1,480 rows, which is
   :func:`chan.khandani_lo_book_two.compounded_apr`.
2. ``√252 · mean(ret) / std(ret)``, with MATLAB's n − 1 ``std``, which is
   :func:`chan.khandani_lo.plain_sharpe`. It refuses a NaN, which holds the
   zero-fill in place.

Neither mirror holds ``lag.m``. Whether it pads its first row with 0 or with
NaN moves nothing, because each script's first held position is NaN either
way, and ``tests/test_price_spread.py`` runs both. :func:`chan.matlab_helpers.lag1`
pads with NaN.

**The ratio's printed figures come from swapped legs.** The price spread and
the log price spread land all four printed figures to six digits. ``Ratio.m``
as published gives −0.134608 and −0.702522 against its closing comment's
−0.141522 and −0.746663. The same script with GLD and USO swapped, so the
signal is GLD/USO and a positive ``numUnits`` buys GLD, lands both to all six
digits. The book captions its Figure 3.2 "Ratio = USO/GLD" and the published
script computes USO/GLD, so the evidence favours the comment coming from a
run with the legs swapped. The swap was the third reading tried, after the
miss was seen, and
[issue 340](https://github.com/l3a0/quantitative-trading/issues/340) names
all three. :func:`example_three_one` runs it beside the published script as a
diagnostic, and Chan's own sentence, a negative APR, holds under both.

**The vintage.** ``inputdata_etf/gld.csv`` and ``inputdata_etf/uso.csv``, two
of the 67 ETFs of Chan's ``inputData_ETF.mat``, read through
:func:`chan.series.load_panel`, which hashes each member against its manifest
entry before parsing it. The file was saved on 2012-04-10 and holds 1,500
days from 2006-04-26 to 2012-04-09. It folds dividends in by subtracting them
in dollars rather than by rescaling, and GLD pays none.

**The scale-break guard runs and refuses nothing.**
:func:`chan.series.refuse_window_crossing_a_break` flags 58 days in eight of
the file's ETFs, every one a leveraged or inverse fund, and neither GLD nor
USO is among them. So :func:`read_sources` calls it on both legs over the
whole span, as :mod:`chan.pead` does, and a bad print in either would stop
the run.

**Example 3.2 builds on this.** Its ``bollinger.m`` computes the same hedge
ratio, the same 20-row drop and the same price spread, and differs only in
how it sets ``numUnits``. So :func:`price_spread`, :func:`zscore` and
:func:`daily_returns` are public, and
[issue 341](https://github.com/l3a0/quantitative-trading/issues/341) calls
them rather than a second copy.

**What changed on the way over.** Four things, and none moves a figure.

1. The file is read as committed vintages through
   :func:`chan.series.load_panel` rather than loaded from the ``.mat``.
2. The plots are not carried. The run prints and draws nothing.
3. The three scripts share one code path, so the 20-row drop, the units and
   the return are written once rather than three times.
4. The ratio runs a second time with the legs swapped, as a diagnostic.

Every result here is exploratory. Reproducing Chan's figures spends the 2006
to 2012 sample on a rule he chose, with a lookback he calls "near-optimal 20
trading days with the benefit of hindsight", so the run says whether his
numbers reproduce on his file and nothing about whether the rule pays today.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from ithildincore.timeseries import ols

from chan.khandani_lo import plain_sharpe
from chan.khandani_lo_book_two import compounded_apr
from chan.matlab_helpers import lag1, moving_avg, moving_std
from chan.series import (
    WindowCrossesScaleBreak,
    load_panel,
    refuse_window_crossing_a_break,
    vintage_line,
)
from chan.vintage import VintageEntry, VintageUnavailable

SOURCE_FILE = "inputData_ETF.mat"
#: ``x`` and ``y`` in all three scripts.
X_SYMBOL = "GLD"
Y_SYMBOL = "USO"
#: ``lookback``: the rows in the hedge ratio's regression, the average and the deviation.
LOOKBACK = 20

#: What each script's closing comment prints, ``APR=%f Sharpe=%f``.
SCRIPT_PRICE_SPREAD = ("0.108335", "0.589651")
SCRIPT_LOG_PRICE_SPREAD = ("0.088863", "0.504153")
SCRIPT_RATIO = ("-0.141522", "-0.746663")
#: What location 1505 prints for the price spread and the log price spread.
BOOK_PRICE_SPREAD = (10.9, 0.59)
BOOK_LOG_PRICE_SPREAD = (9, 0.5)


@dataclass(frozen=True)
class Signal:
    """One script's signal over the rows it keeps, and the dollars one unit holds.

    ``prices`` holds ``[x, y]`` on each kept row and ``unit_dollars`` the
    dollars one unit of the portfolio holds in each, in the same order.
    ``hedge`` is the rolling hedge ratio on the kept rows, and ``None`` for the
    ratio, which has none.
    """

    name: str
    days: pd.DatetimeIndex
    prices: np.ndarray
    hedge: np.ndarray | None
    value: np.ndarray
    unit_dollars: np.ndarray


@dataclass(frozen=True)
class Run:
    """One signal traded by the linear rule, and the two figures its script prints."""

    signal: Signal
    units: np.ndarray
    positions: np.ndarray
    daily: np.ndarray

    @property
    def apr(self) -> float:
        return compounded_apr(self.daily)

    @property
    def sharpe(self) -> float:
        return plain_sharpe(self.daily)


@dataclass(frozen=True)
class ExampleThreeOne:
    """The three scripts on GLD and USO, and the ratio again with the legs swapped."""

    price_spread: Run
    log_price_spread: Run
    ratio: Run
    swapped_ratio: Run


def rolling_hedge_ratio(
    dependent: np.ndarray, independent: np.ndarray, lookback: int = LOOKBACK
) -> np.ndarray:
    """The slope of ``ols(dependent, [independent ones])`` over each trailing ``lookback`` rows.

    Row t reads rows t − lookback + 1 through t, so the slope is first defined
    on row ``lookback − 1`` and the rows before it are NaN.
    """
    dependent = np.asarray(dependent, dtype=float)
    independent = np.asarray(independent, dtype=float)
    if dependent.shape != independent.shape or dependent.ndim != 1:
        raise ValueError("rolling_hedge_ratio takes two series of one shape")
    hedge = np.full(len(dependent), np.nan)
    ones = np.ones(lookback)
    for t in range(lookback - 1, len(dependent)):
        window = slice(t - lookback + 1, t + 1)
        hedge[t] = ols(dependent[window], np.column_stack([independent[window], ones])).beta[0]
    return hedge


def _kept(days: pd.DatetimeIndex, lookback: int) -> pd.DatetimeIndex:
    """The rows every script keeps once it deletes its first ``lookback``."""
    return days[lookback:]


def price_spread(
    days: pd.DatetimeIndex, x: np.ndarray, y: np.ndarray, lookback: int = LOOKBACK
) -> Signal:
    """``PriceSpread.m``'s ``yport = y − h·x``, with ``h`` refitted over the last ``lookback``."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    hedge = rolling_hedge_ratio(y, x, lookback)[lookback:]
    x, y = x[lookback:], y[lookback:]
    return Signal(
        name="price spread",
        days=_kept(days, lookback),
        prices=np.column_stack([x, y]),
        hedge=hedge,
        value=y - hedge * x,
        unit_dollars=np.column_stack([-hedge * x, y]),
    )


def log_price_spread(
    days: pd.DatetimeIndex, x: np.ndarray, y: np.ndarray, lookback: int = LOOKBACK
) -> Signal:
    """``LogPriceSpread.m``'s ``log y − h·log x``, with ``h`` refitted on log prices."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    hedge = rolling_hedge_ratio(np.log(y), np.log(x), lookback)[lookback:]
    x, y = x[lookback:], y[lookback:]
    return Signal(
        name="log price spread",
        days=_kept(days, lookback),
        prices=np.column_stack([x, y]),
        hedge=hedge,
        value=np.log(y) - hedge * np.log(x),
        unit_dollars=np.column_stack([-hedge, np.ones(len(hedge))]),
    )


def ratio(
    days: pd.DatetimeIndex,
    x: np.ndarray,
    y: np.ndarray,
    lookback: int = LOOKBACK,
    *,
    name: str = "ratio",
) -> Signal:
    """``Ratio.m``'s ``y / x``, with one dollar short ``x`` and one long ``y`` per unit."""
    x, y = np.asarray(x, dtype=float)[lookback:], np.asarray(y, dtype=float)[lookback:]
    ones = np.ones(len(x))
    return Signal(
        name=name,
        days=_kept(days, lookback),
        prices=np.column_stack([x, y]),
        hedge=None,
        value=y / x,
        unit_dollars=np.column_stack([-ones, ones]),
    )


def zscore(value: np.ndarray, lookback: int = LOOKBACK) -> np.ndarray:
    """How many moving standard deviations ``value`` sits from its moving average.

    Both are taken over the trailing ``lookback`` rows with ``movingAvg`` and
    ``movingStd``, so the first ``lookback − 1`` rows are NaN.
    """
    with np.errstate(invalid="ignore", divide="ignore"):
        return (value - moving_avg(value, lookback)) / moving_std(value, lookback)


def linear_units(value: np.ndarray, lookback: int = LOOKBACK) -> np.ndarray:
    """``numUnits``: the negative z-score, so the portfolio is bought in proportion as it falls."""
    return -zscore(value, lookback)


def daily_returns(positions: np.ndarray, prices: np.ndarray) -> np.ndarray:
    """Each row's profit on yesterday's dollar positions over the gross dollars they held.

    ``sum(lag(pos)·(p − lag(p))/lag(p))`` over ``sum(|lag(pos)|)``, summed
    across the legs without skipping a NaN, as MATLAB's ``sum`` does. A row
    that comes out NaN, the first and every row before a position exists, is
    set to 0.
    """
    held = lag1(positions)
    before = lag1(prices)
    with np.errstate(invalid="ignore", divide="ignore"):
        profit = (held * (prices - before) / before).sum(axis=1)
        daily = profit / np.abs(held).sum(axis=1)
    return np.where(np.isnan(daily), 0.0, daily)


def linear_mean_reversion(signal: Signal, lookback: int = LOOKBACK) -> Run:
    """Hold ``numUnits`` units of ``signal``'s portfolio each day and return the run."""
    units = linear_units(signal.value, lookback)
    positions = units[:, None] * signal.unit_dollars
    return Run(signal, units, positions, daily_returns(positions, signal.prices))


def example_three_one(closes: pd.DataFrame, lookback: int = LOOKBACK) -> ExampleThreeOne:
    """Run the three scripts on a frame holding GLD and USO, and the ratio with the legs swapped."""
    days = closes.index
    x = closes[X_SYMBOL].to_numpy(dtype=float)
    y = closes[Y_SYMBOL].to_numpy(dtype=float)
    return ExampleThreeOne(
        price_spread=linear_mean_reversion(price_spread(days, x, y, lookback), lookback),
        log_price_spread=linear_mean_reversion(log_price_spread(days, x, y, lookback), lookback),
        ratio=linear_mean_reversion(ratio(days, x, y, lookback), lookback),
        swapped_ratio=linear_mean_reversion(
            ratio(days, y, x, lookback, name="ratio, GLD and USO swapped"), lookback
        ),
    )


def read_sources(data_dir: Path | None = None) -> tuple[list[VintageEntry], pd.DataFrame]:
    """GLD's and USO's entries and a frame of their closes, after the scale-break guard."""
    members, closes = load_panel(SOURCE_FILE, data_dir=data_dir)
    legs = [entry for entry in members if entry.symbol in (X_SYMBOL, Y_SYMBOL)]
    pair = closes[[X_SYMBOL, Y_SYMBOL]]
    refuse_window_crossing_a_break(
        [(entry, pair[entry.symbol]) for entry in legs], start=pair.index[0], end=pair.index[-1]
    )
    return legs, pair


def report(members: list[VintageEntry], result: ExampleThreeOne) -> None:
    """Print the source, the rule, and each figure beside what Chan printed."""
    days = result.price_spread.signal.days
    print("Price spread, log price spread and ratio, Chan's Example 3.1 in Algorithmic Trading")
    for entry in members:
        print(f"  {entry.symbol:<8} {vintage_line(entry)}, lifted from {entry.source_workbook}")
    print(
        f"  window   {days[0].date()} to {days[-1].date()}, {len(days)} trading days after "
        f"the first {LOOKBACK} are dropped"
    )
    print(
        f"  rule     hold minus the {LOOKBACK}-day z-score of the signal in units of the "
        f"portfolio, the hedge ratio refitted on the last {LOOKBACK} days"
    )
    print()
    rows = [
        ("Price spread", result.price_spread, SCRIPT_PRICE_SPREAD, BOOK_PRICE_SPREAD),
        (
            "Log price spread",
            result.log_price_spread,
            SCRIPT_LOG_PRICE_SPREAD,
            BOOK_LOG_PRICE_SPREAD,
        ),
        ("Ratio, USO/GLD", result.ratio, SCRIPT_RATIO, ("negative", "none")),
        ("Ratio, legs swapped", result.swapped_ratio, ("none", "none"), ("none", "none")),
    ]
    print(f"  {'Figure':<32} {'Computed':>10} {'Script':>10} {'Book':>10}")
    for label, run, script, book in rows:
        apr_book = book[0] if isinstance(book[0], str) else f"{book[0]}%"
        print(f"  {label + ', APR':<32} {run.apr:>10.6f} {script[0]:>10} {apr_book:>10}")
        print(
            f"  {label + ', Sharpe ratio':<32} {run.sharpe:>10.6f} {script[1]:>10} {book[1]!s:>10}"
        )
    print()
    print(
        "  Ratio.m's comment matches the run with GLD and USO swapped, not the script as "
        "published. The swap was tried after the miss."
    )
    print(
        "  Exploratory. Reproducing Chan's figures spends the 2006 to 2012 sample on a rule he "
        "chose, so this says whether"
    )
    print(
        "  his numbers reproduce on his file and nothing about whether the rule pays today. "
        "docs/replication-log.md Entry 21 carries the verdicts."
    )


def run(data_dir: Path | None = None) -> ExampleThreeOne:
    """Read the two ETFs, run the three scripts and the swap, and print the report."""
    members, closes = read_sources(data_dir)
    result = example_three_one(closes)
    report(members, result)
    return result


def main() -> None:
    argparse.ArgumentParser(
        description="Price spread, log price spread and ratio on GLD and USO, Example 3.1 of "
        "Algorithmic Trading"
    ).parse_args()
    try:
        run()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source is worth nothing at the bottom of a
        # traceback, so it reaches the reader as one line, the way
        # chan.pead.main does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
