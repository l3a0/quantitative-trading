"""Four tests for mean reversion on USD.CAD and the trade they set, Examples 2.1 to 2.5.

The examples are *Algorithmic Trading*'s, in Chapter 2.

Chan's ``stationarityTests.m`` takes USD.CAD's close at 16:59 New York time on
each day of his minute file and runs, in order:

1. Example 2.1, jplv7's augmented Dickey-Fuller test at a constant and 1 lag,
   whose comment prints a statistic of −1.840744 against a 10 percent critical
   value of −2.594.
2. Example 2.2, ``genhurst(log(y), 2)``, which location 1119 reports as an H of
   0.49.
3. Example 2.3, ``vratiotest(log(y))``, whose comment prints ``h=0`` and a
   p-value of 0.367281.
4. Example 2.4, the half-life ``−log(2)/λ``, where λ is the slope of the daily
   change on the previous close with a constant, printed as 115.209794 days.
5. Example 2.5, a position of minus the close's distance from its moving
   average in moving standard deviations, with a lookback of the half-life
   rounded, plotted as cumulative P&L.

:mod:`chan.stationarity_tests` holds the three toolbox functions, and this
module runs them on the committed closes. The half-life is
:func:`ithildincore.timeseries.ou_half_life`, which is already the script's
regression. The moving average and deviation are Chan's ``movingAvg`` and
``movingStd`` in :mod:`chan.matlab_helpers`.

**The source.** ``stationarityTests.m`` in
[ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) at
``e4bc46f`` under ``public/img/book2/``, git blob ``b7bc6a1``, the same blob as
``archived/matlab/`` in ivanliu1989/algorithmic_trading at ``4567024``.

**The closes.** The script loads ``inputData_USDCAD.mat``, which neither
mirror holds. Chan's 2018 Python port ships the same bars as
``inputData_USDCAD.csv``, committed under issue 301, and
:func:`chan.series.load_minute_close` keeps the 16:59 bar as the script's
``cl(hhmm==1659)`` does. That the two files hold the same closes cannot be read
directly, so the evidence is the run: the ADF statistic, its AR(1) estimate,
the variance ratio's p-value and the half-life all land every digit Chan's
comments print.

**The Example 2.5 claim was declared before its P&L was computed.** Location
1225 says the cumulative P&L "manages to be positive, albeit with a large
drawdown". Issue 338 wrote down that the claim holds when the sum of the daily
P&L over all 1,216 rows is greater than 0, and that the drawdown is reported
beside it and decides nothing, since "large" carries no scale.
:func:`pnl_drawdown` measures it as the deepest fall of the cumulative P&L
below its running maximum, in the P&L's own units.
:func:`chan.matlab_helpers.calculate_max_dd` is not used, because it divides by
one plus the high and so reads a compounded return, which a sum of P&L is not.

**The scale-break guard runs** over the one series and its whole span, and
flags nothing.

**What changed on the way over from** ``stationarityTests.m``. Five things,
and none moves a figure. The transcription landed here with
[PR #387](https://github.com/l3a0/quantitative-trading/pull/387), for
[issue 338](https://github.com/l3a0/quantitative-trading/issues/338).

1. The closes are read from the committed minute file through the vintage
   manifest rather than loaded from the ``.mat``.
2. ``plot(y)`` and ``plot(cumsum(pnl))`` are not carried. The run prints and
   draws nothing, and :mod:`chan.usdcad_mean_reversion_figures` draws both.
3. ``prt(results)`` becomes the report's ADF rows.
4. Rows the script does not compute are reported beside it: the ADF statistic
   ``adfuller`` gives at the same lag, the H that Chan's 2018 Python port of
   ``genhurst`` gives, and the Example 2.5 drawdown.
5. jplv7's ``lag``, which fills its first row with 0, becomes
   :func:`chan.matlab_helpers.lag1`, which fills it with NaN. Example 2.5's
   first row is NaN either way, 0 times an infinity or NaN times a number, and
   the script sets every NaN to 0.

**The Python port's** ``genhurst`` is ``PythonCodesAndData/genhurst.py`` in
Chan's ``PythonCodesAndData.zip``, the zip ``data/README.md`` names with
sha256 ``91e3d0d534f465feae31da3f6a19db03e32b190cf70a2470f03cde60617f8317``,
in EpchanPreview at ``e4bc46f``. It is not committed, and
:func:`python_port_hurst` carries its arithmetic.

Exploratory. Reproducing Chan's figures spends the 2007 to 2012 sample on
tests he chose, so the run says whether his numbers reproduce on his closes and
nothing about whether USD.CAD reverts today. Location 1225 names a look-ahead
in Example 2.5 itself: its lookback comes from the half-life of the same
closes it trades.
"""

from __future__ import annotations

import argparse
import math
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from ithildincore.timeseries import ols, ou_half_life
from statsmodels.tsa.stattools import adfuller

from chan.matlab_helpers import lag1, moving_avg, moving_std, round_half_away
from chan.series import load_minute_close, refuse_window_crossing_a_break, vintage_line
from chan.stationarity_tests import Jplv7Adf, VarianceRatio, genhurst, jplv7_adf, vratiotest
from chan.vintage import VintageEntry, VintageUnavailable

SYMBOL = "USDCAD"
#: The saved date that picks the minute file out of USD.CAD's two vintages.
MINUTES_DATED = "2018-10-13"
#: ``adf(y, 0, 1)``: trend order 0, a constant, and 1 lagged change.
ADF_ORDER = 0
ADF_LAGS = 1
#: ``genhurst(log(y), 2)``.
HURST_Q = 2

#: What the script's comments print.
SCRIPT_ADF = -1.840744
SCRIPT_AR1 = 0.994120
SCRIPT_CRITICAL = (-3.458, -2.871, -2.594)
SCRIPT_VRATIO_H = 0
SCRIPT_VRATIO_P = 0.367281
SCRIPT_HALF_LIFE = 115.209794
#: What the book prints where the script prints nothing, or rounds what it does.
BOOK_ADF = -1.84
BOOK_HURST = 0.49
BOOK_HALF_LIFE_DAYS = 115


@dataclass(frozen=True)
class Drawdown:
    """The deepest fall of a cumulative P&L below its running maximum.

    ``depth`` is in the P&L's own units and is zero or positive. ``peak`` and
    ``trough`` are the dates of the high it fell from and of the low.
    """

    depth: float
    peak: pd.Timestamp
    trough: pd.Timestamp


@dataclass(frozen=True)
class StationarityRun:
    """Everything ``stationarityTests.m`` computes, and the rows reported beside it."""

    closes: pd.Series
    adf: Jplv7Adf
    hurst: float
    vratio: VarianceRatio
    half_life: float
    lookback: int
    pnl: pd.Series
    drawdown: Drawdown
    adfuller_statistic: float
    adfuller_ar1: float
    python_port_hurst: float

    @property
    def total_pnl(self) -> float:
        """The last point of ``cumsum(pnl)``, which the declared claim reads."""
        return float(self.pnl.sum())

    @property
    def first_position(self) -> pd.Timestamp:
        """The first day whose P&L is not zero."""
        return self.pnl.index[int(np.flatnonzero(self.pnl.to_numpy())[0])]


def linear_mean_reversion(closes: np.ndarray, lookback: int) -> np.ndarray:
    """Example 2.5's daily P&L, lines 55 to 57 of ``stationarityTests.m``.

    ``mktVal`` is minus the close's distance from its ``lookback``-row moving
    average, in ``lookback``-row moving standard deviations. Each day's P&L is
    the previous day's ``mktVal`` times the day's return, and a NaN is set to
    0. The first row has no previous day, and the rows before the window fills
    multiply by NaN, so all of them are 0.
    """
    previous = lag1(closes)
    with np.errstate(invalid="ignore", divide="ignore"):
        market_value = -(closes - moving_avg(closes, lookback)) / moving_std(closes, lookback)
        pnl = lag1(market_value) * (closes - previous) / previous
    return np.where(np.isnan(pnl), 0.0, pnl)


def pnl_drawdown(pnl: pd.Series) -> Drawdown:
    """The deepest fall of ``cumsum(pnl)`` below its running maximum, with its dates.

    The running maximum starts at the first day's cumulative P&L. The trough is
    the first day the deepest fall is reached, and the peak the last day before
    it that held the maximum.
    """
    cumulative = pnl.cumsum().to_numpy()
    high = np.maximum.accumulate(cumulative)
    fall = high - cumulative
    trough = int(np.argmax(fall))
    peak = int(np.flatnonzero(cumulative[: trough + 1] == high[trough])[-1])
    return Drawdown(depth=float(fall[trough]), peak=pnl.index[peak], trough=pnl.index[trough])


def adfuller_at_one_lag(closes: np.ndarray) -> tuple[float, float]:
    """``adfuller(y, maxlag=1, regression='c', autolag=None)``: its statistic and AR(1) estimate.

    It is the line in Chan's 2018 Python port and what
    :func:`ithildincore.timeseries.adf_tstat` runs. The AR(1) estimate is its
    slope on the lagged level plus 1, the form jplv7 prints.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        result = adfuller(closes, maxlag=ADF_LAGS, regression="c", autolag=None, regresults=True)
    return float(result[0]), float(result[3].resols.params[0]) + 1


def python_port_hurst(log_closes: np.ndarray) -> float:
    """H from ``genhurst.py`` in Chan's 2018 Python port, which is not ``genhurst.m``.

    The log variance of the τ-row differences, population variance, is fitted
    on log τ for τ from 1 to ``np.round(len / 10) − 1``, with a constant, and H
    is half the slope. τ = 0 is in the port's range and drops out, because its
    variance is zero and its log is not finite. The port assigns a one-column
    frame's ``var``, a one-element series, into one slot of a numpy array,
    which numpy 2 refuses, so it no longer runs as shipped. This is its
    arithmetic.
    """
    z = pd.Series(log_closes)
    taus = np.arange(int(np.round(len(z) / 10)))
    with np.errstate(divide="ignore"):
        log_var = np.array([np.log(z.diff(tau).var(ddof=0)) for tau in taus])
        log_tau = np.log(taus.astype(float))
    kept = np.isfinite(log_var)
    design = np.column_stack([log_tau[kept], np.ones(int(kept.sum()))])
    return float(ols(log_var[kept], design).beta[0]) / 2


def read_sources(data_dir: Path | None = None) -> tuple[VintageEntry, pd.Series]:
    """The minute file's manifest entry and its 1,216 closes at 16:59."""
    return load_minute_close(SYMBOL, dated=MINUTES_DATED, data_dir=data_dir)


def stationarity_tests(entry: VintageEntry, closes: pd.Series) -> StationarityRun:
    """Run ``stationarityTests.m`` on ``closes``, after the scale-break guard."""
    refuse_window_crossing_a_break([(entry, closes)], start=closes.index[0], end=closes.index[-1])
    y = closes.to_numpy(dtype=float)
    half_life = ou_half_life(y)
    if not math.isfinite(half_life):
        raise ValueError("the closes do not revert, so Example 2.5 has no lookback to use")
    lookback = int(round_half_away(half_life))
    pnl = pd.Series(linear_mean_reversion(y, lookback), index=closes.index)
    statistic, ar1 = adfuller_at_one_lag(y)
    return StationarityRun(
        closes=closes,
        adf=jplv7_adf(y, ADF_ORDER, ADF_LAGS),
        hurst=genhurst(np.log(y), HURST_Q),
        vratio=vratiotest(np.log(y)),
        half_life=half_life,
        lookback=lookback,
        pnl=pnl,
        drawdown=pnl_drawdown(pnl),
        adfuller_statistic=statistic,
        adfuller_ar1=ar1,
        python_port_hurst=python_port_hurst(np.log(y)),
    )


def report(entry: VintageEntry, run: StationarityRun) -> None:
    """Print the source, each test beside what Chan printed, and the Example 2.5 claim."""
    closes = run.closes
    print("Stationarity tests and linear mean reversion on USD.CAD, Examples 2.1 to 2.5")
    print(f"  closes   {vintage_line(entry)}, the 16:59 bar of each day")
    print(f"           {len(closes)} closes, {closes.index[0].date()} to {closes.index[-1].date()}")
    print()
    a, v = run.adf, run.vratio
    rows = [
        ("2.1 ADF statistic, 1 lag", f"{a.statistic:.6f}", f"{SCRIPT_ADF:.6f}", f"{BOOK_ADF}"),
        ("2.1 AR(1) estimate", f"{a.ar1:.6f}", f"{SCRIPT_AR1:.6f}", "none"),
        (
            "2.1 critical values 1/5/10%",
            "/".join(f"{c:.3f}" for c in a.critical),
            "/".join(f"{c:.3f}" for c in SCRIPT_CRITICAL),
            f"{SCRIPT_CRITICAL[2]} at 10%",
        ),
        ("2.2 Hurst exponent, q = 2", f"{run.hurst:.6f}", "none", f"{BOOK_HURST}"),
        ("2.3 variance ratio h", f"{int(v.rejects)}", f"{SCRIPT_VRATIO_H}", "none"),
        ("2.3 variance ratio p-value", f"{v.p_value:.6f}", f"{SCRIPT_VRATIO_P:.6f}", "none"),
        (
            "2.4 half-life, days",
            f"{run.half_life:.6f}",
            f"{SCRIPT_HALF_LIFE:.6f}",
            f"{BOOK_HALF_LIFE_DAYS}",
        ),
    ]
    print(f"  {'Figure':<30} {'Computed':>20} {'Script':>20} {'Book':>12}")
    for label, computed, script, book in rows:
        print(f"  {label:<30} {computed:>20} {script:>20} {book:>12}")
    print()
    print(
        f"  2.5 lookback {run.lookback} days, the half-life rounded. First position on "
        f"{run.first_position.date()}."
    )
    print(
        f"      cumulative P&L {run.total_pnl:.6f}. The claim declared on issue 338, "
        f"positive, {'holds' if run.total_pnl > 0 else 'fails'}."
    )
    d = run.drawdown
    print(
        f"      deepest drawdown {d.depth:.6f}, from {d.peak.date()} to {d.trough.date()}, "
        "reported beside the claim and deciding nothing."
    )
    print()
    print("  Beside the script, with no published figure:")
    print(
        f"    adfuller at 1 lag, Chan's Python port's line: statistic "
        f"{run.adfuller_statistic:.6f}, AR(1) {run.adfuller_ar1:.6f}"
    )
    print(f"    H from the Python port's own genhurst: {run.python_port_hurst:.6f}")
    print()
    print(
        "  Exploratory. Reproducing Chan's figures spends the 2007 to 2012 sample on tests he "
        "chose, and Example 2.5's lookback"
    )
    print(
        "  comes from the closes it trades. docs/replication-log.md Entry 22 carries the verdicts."
    )


def run(data_dir: Path | None = None) -> StationarityRun:
    """Read the closes, run every test and the trade, and print the report."""
    entry, closes = read_sources(data_dir)
    result = stationarity_tests(entry, closes)
    report(entry, result)
    return result


def main() -> None:
    argparse.ArgumentParser(
        description="Examples 2.1 to 2.5 of Algorithmic Trading on Chan's own USD.CAD closes"
    ).parse_args()
    try:
        run()
    except VintageUnavailable as refused:
        # A refusal that names the source is worth nothing at the bottom of a
        # traceback, so it reaches the reader as one line, the way
        # chan.buy_on_gap.main does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
