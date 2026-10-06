"""A Kalman filter hedge ratio on EWA and EWC, *Algorithmic Trading*'s ``KF_beta_EWA_EWC.m``.

Example 3.2 hedges one ETF with another through a slope refitted over a
rolling window. Chan's next step replaces that window with a Kalman filter,
which re-estimates the slope and intercept of EWC on EWA every day from the
day before's estimate and the new pair of closes. The filter's one-day
forecast error then becomes the trading signal, and its forecast variance sets
the band. Kindle locations 1633 to 1726 describe it, and location 1726 reports
"a reasonable APR of 26.2 percent and a Sharpe ratio of 2.4". The script
closes on the comment ``APR=0.262252 Sharpe=2.361162``, so the book's figures
are the script's rounded.

The same location makes two claims about the filter's state: the slope
"oscillates around 1" and the intercept "increases monotonically with time".
The owner ruled on
[issue 342](https://github.com/l3a0/quantitative-trading/issues/342) on
2026-10-06 that both are carried as findings with no verdict, because the only
criteria available for them were written after a run. :func:`slope_findings`
and :func:`intercept_findings` measure what the issue quotes.

**What ``KF_beta_EWA_EWC.m`` holds.** The script is git blob ``e2f8a62`` under
``public/img/book2/`` in
[ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) at
``e4bc46f``, and the same blob under ``archived/matlab/`` in
ivanliu1989/algorithmic_trading at ``4567024``. Its ``fillMissingData.m`` is
blob ``88632fc`` in both. Box 3.1, which carries the equations, is not among
the highlights, and the script labels its lines with equations 3.7 to 3.12, so
the script is the specification. ``x`` is EWA's close with a column of ones
beside it, and ``y`` is EWC's close.

1. **Start.** The state ``beta``, a slope and an intercept, starts at 0, and
   the covariances ``R`` and ``P`` start as 2 × 2 zeros. Row 1 skips the
   prediction step, so its forecast variance is :data:`VE`, its gain is 0, and
   ``beta`` stays 0 after the update.
2. **Predict, from row 2.** ``beta`` is yesterday's and ``R = P + Vw``, with
   ``Vw = delta / (1 − delta)`` on the diagonal, equations 3.7 and 3.8.
3. **Forecast.** ``yhat = x·beta`` and ``Q = x·R·x' + Ve``, equations 3.9 and
   3.10, and the error ``e`` is ``y − yhat``.
4. **Update.** The gain ``K = R·x' / Q``, then ``beta + K·e`` and
   ``P = R − K·x·R``, equations 3.11 and 3.12. Everything downstream reads
   ``beta`` after this update.
5. **Trade** with :func:`chan.bollinger.band_units`. A long enters at
   ``e < −sqrt(Q)`` and exits at ``e > −sqrt(Q)``. A short enters at
   ``e > sqrt(Q)`` and exits at ``e < sqrt(Q)``. Each exit sits on its own
   entry band, where ``bollinger.m`` exits at the mean. The error is compared
   with ``±sqrt(Q)`` directly rather than divided into a z-score, for the
   reason :mod:`chan.bollinger` gives.
6. **Earn** each day's return as :func:`chan.price_spread.daily_returns` gives
   it, on positions of ``units · [−slope, 1] · [EWA, EWC]``.
7. **Measure** the APR, compounded at 252 a year, and the Sharpe ratio with
   the n − 1 deviation, over all 1,500 rows. Unlike ``bollinger.m``, the
   script drops no row.

**The script trades on the file's first day.** On row 1 the state is still 0,
so the forecast is 0 and the error is EWC's whole close, far above
``sqrt(Q)``. The script enters a short on 2006-04-26 that holds EWC alone,
with no EWA leg. :attr:`KalmanHedge.quiet_start` withholds the signal on rows 1
and 2, which the script's own plot of ``e`` leaves out, and the APR and Sharpe
ratio then round to 26.1 percent and 2.3 rather than the book's 26.2 and 2.4.

**What changed on the way over.** Three things, and none moves a figure.

1. The two ETFs are read as committed vintages through
   :func:`chan.series.load_panel` rather than loaded from the ``.mat``.
2. The script's four plots, Figures 3.5 to 3.8, are not drawn. The run prints.
3. The filter is the script's loop written out, rather than statsmodels'
   state-space models, because the script's start, a zero state with zero
   covariance, is part of the specification.

**The scale-break guard.** :func:`read_sources` calls
:func:`chan.series.refuse_window_crossing_a_break` on both legs over the whole
file, as :mod:`chan.price_spread` does. Neither ETF carries a flagged day, so
nothing is refused. The guard also refuses a close that is not a finite
number, so the filter carries no refusal of its own.

Every result here is exploratory. Reproducing Chan's figures spends the 2006 to
2012 sample on a rule and two constants he chose, and the script's comment
invites tuning ``delta``, which this module does not do.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from chan.bollinger import band_units
from chan.khandani_lo import TRADING_DAYS, plain_sharpe
from chan.khandani_lo_book_two import compounded_apr, gap, matches
from chan.price_spread import daily_returns
from chan.series import (
    WindowCrossesScaleBreak,
    load_panel,
    panel_line,
    refuse_window_crossing_a_break,
)
from chan.vintage import VintageEntry, VintageUnavailable

#: The file ``KF_beta_EWA_EWC.m`` loads, git blob ``261718b``.
SOURCE_FILE = "inputData_ETF.mat"
#: ``x`` in the script.
X = "EWA"
#: ``y`` in the script.
Y = "EWC"

#: ``delta=0.0001``, which sets the state's drift ``Vw = delta/(1-delta)``.
DELTA = 0.0001
#: ``Ve=0.001``, the variance of the measurement error.
VE = 0.001

#: The comment the script closes on.
SCRIPT_APR = "0.262252"
SCRIPT_SHARPE = "2.361162"
#: What location 1726 prints.
BOOK_APR_PERCENT = "26.2"
BOOK_SHARPE = "2.4"

TITLE = "A Kalman filter hedge ratio on EWA and EWC, Algorithmic Trading's KF_beta_EWA_EWC.m"

#: Rows 1 and 2, which :attr:`KalmanHedge.quiet_start` gives no signal.
QUIET_ROWS = 2
#: The window of the rolling mean :func:`intercept_findings` reads.
ROLLING_DAYS = 250


@dataclass(frozen=True)
class Filter:
    """The filter's state after each row's update, and the forecast that row made.

    ``slope`` and ``intercept`` are ``beta(1,:)`` and ``beta(2,:)``. ``error``
    is ``e``, and ``variance`` is ``Q``.
    """

    days: pd.DatetimeIndex
    slope: NDArray[np.float64]
    intercept: NDArray[np.float64]
    error: NDArray[np.float64]
    variance: NDArray[np.float64]


@dataclass(frozen=True)
class Trade:
    """``numUnits`` on every row and the daily return it earned."""

    units: NDArray[np.float64]
    daily: NDArray[np.float64]

    @property
    def apr(self) -> float:
        return compounded_apr(self.daily)

    @property
    def sharpe(self) -> float:
        return plain_sharpe(self.daily)


@dataclass(frozen=True)
class KalmanHedge:
    """The script on EWA and EWC, and the same run with no signal on rows 1 and 2."""

    filter: Filter
    trade: Trade
    quiet_start: Trade


@dataclass(frozen=True)
class SlopeFindings:
    """What location 1726's "oscillates around 1" can be read against.

    ``crossings`` counts the rows on which the slope sits on the other side of
    1 from the row before, so the first counts the step up from the zero start.
    """

    median: float
    mean: float
    rows_above_one: int
    rows: int
    crossings: int


@dataclass(frozen=True)
class Falls:
    """How many steps of one series fall, out of how many steps it takes."""

    falls: int
    steps: int


@dataclass(frozen=True)
class InterceptFindings:
    """What location 1726's "increases monotonically with time" can be read against.

    ``yearly`` holds each calendar year's mean intercept. Each ``Falls`` counts
    the steps of one grain that go down. ``peak`` is the intercept's highest
    value and its day, and ``last`` is its value on the file's last row.
    """

    yearly: pd.Series
    by_year: Falls
    by_quarter: Falls
    by_month: Falls
    by_day: Falls
    rolling: Falls
    peak_day: pd.Timestamp
    peak: float
    last: float


def kalman_filter(days: pd.DatetimeIndex, x: NDArray, y: NDArray) -> Filter:
    """Run ``KF_beta_EWA_EWC.m``'s loop over every row of ``x`` and ``y``."""
    n = len(x)
    observation = np.column_stack([x, np.ones(n)])
    drift = DELTA / (1 - DELTA) * np.eye(2)
    beta = np.zeros((2, n))
    error = np.full(n, np.nan)
    variance = np.full(n, np.nan)
    state_cov = np.zeros((2, 2))
    predicted_cov = np.zeros((2, 2))
    for t in range(n):
        row = observation[t]
        if t > 0:
            beta[:, t] = beta[:, t - 1]
            predicted_cov = state_cov + drift
        variance[t] = row @ predicted_cov @ row + VE
        error[t] = y[t] - row @ beta[:, t]
        gain = predicted_cov @ row / variance[t]
        beta[:, t] = beta[:, t] + gain * error[t]
        state_cov = predicted_cov - np.outer(gain, row) @ predicted_cov
    return Filter(days=days, slope=beta[0], intercept=beta[1], error=error, variance=variance)


def band_signals(
    error: NDArray, variance: NDArray, *, quiet_rows: int = 0
) -> tuple[NDArray, NDArray, NDArray, NDArray]:
    """The four arrays the script sets, each exit on its own entry band.

    ``quiet_rows`` sets all four false on that many leading rows.
    """
    band = np.sqrt(variance)
    signals = (error < -band, error > -band, error > band, error < band)
    for each in signals:
        each[:quiet_rows] = False
    return signals


def trade(prices: NDArray, filtered: Filter, *, quiet_rows: int = 0) -> Trade:
    """Hold the units the band sets in ``[−slope, 1]`` of EWA and EWC, and earn each day."""
    units = band_units(*band_signals(filtered.error, filtered.variance, quiet_rows=quiet_rows))
    positions = units[:, None] * np.column_stack([-filtered.slope, np.ones(len(units))]) * prices
    return Trade(units=units, daily=daily_returns(positions, prices))


def kalman_hedge(closes: pd.DataFrame) -> KalmanHedge:
    """The script and the quiet-start run on a frame holding EWA and EWC."""
    prices = closes[[X, Y]].to_numpy(dtype=float)
    filtered = kalman_filter(closes.index, prices[:, 0], prices[:, 1])
    return KalmanHedge(
        filter=filtered,
        trade=trade(prices, filtered),
        quiet_start=trade(prices, filtered, quiet_rows=QUIET_ROWS),
    )


def slope_findings(slope: NDArray) -> SlopeFindings:
    """The slope's median, mean, rows above 1, and crossings of 1."""
    above = slope > 1
    return SlopeFindings(
        median=float(np.median(slope)),
        mean=float(np.mean(slope)),
        rows_above_one=int(above.sum()),
        rows=len(slope),
        crossings=int((above[1:] != above[:-1]).sum()),
    )


def _falls(series: pd.Series) -> Falls:
    steps = series.diff().dropna()
    return Falls(falls=int((steps < 0).sum()), steps=len(steps))


def intercept_findings(days: pd.DatetimeIndex, intercept: NDArray) -> InterceptFindings:
    """The intercept's means by year, quarter and month, its daily and rolling steps, its peak."""
    series = pd.Series(intercept, index=days)
    yearly = series.groupby(series.index.year).mean()
    return InterceptFindings(
        yearly=yearly,
        by_year=_falls(yearly),
        by_quarter=_falls(series.groupby(series.index.to_period("Q")).mean()),
        by_month=_falls(series.groupby(series.index.to_period("M")).mean()),
        by_day=_falls(series),
        rolling=_falls(series.rolling(ROLLING_DAYS).mean().dropna()),
        peak_day=series.idxmax(),
        peak=float(series.max()),
        last=float(series.iloc[-1]),
    )


def read_sources(data_dir: Path | None = None) -> tuple[list[VintageEntry], pd.DataFrame]:
    """EWA's and EWC's closes, refused if either spans a scale break over the file."""
    members, closes = load_panel(SOURCE_FILE, data_dir=data_dir)
    read = [m for m in members if m.symbol in (X, Y)]
    frame = closes[[X, Y]]
    refuse_window_crossing_a_break(
        [(m, frame[m.symbol]) for m in read], start=frame.index[0], end=frame.index[-1]
    )
    return read, frame


def _verdict(value: float, printed: str) -> str:
    if matches(value, printed):
        return "reproduced"
    return f"did not reproduce, gap {gap(value, printed):+g}"


def report(members: list[VintageEntry], result: KalmanHedge) -> None:
    """Print the vintage, each printed figure beside the computed one, and the findings."""
    f, t = result.filter, result.trade
    print(TITLE)
    print(f"  vintage   {panel_line(members)}: {', '.join(m.symbol for m in members)}")
    print(f"  rows      {f.days[0].date()} to {f.days[-1].date()}, {len(f.days)} days")
    print(f"  filter    delta {DELTA:g}, Ve {VE:g}, state and covariance starting at 0")
    print()
    print(f"  {'Figure':<14} {'Computed':>12}  {'Script':>9}  {'Book':>5}  Verdict")
    for label, value, script, book, book_value in (
        ("APR", t.apr, SCRIPT_APR, BOOK_APR_PERCENT, 100 * t.apr),
        ("Sharpe ratio", t.sharpe, SCRIPT_SHARPE, BOOK_SHARPE, t.sharpe),
    ):
        verdicts = {_verdict(value, script), _verdict(book_value, book)}
        verdict = "reproduced" if verdicts == {"reproduced"} else ", ".join(sorted(verdicts))
        print(f"  {label:<14} {value:>12.8f}  {script:>9}  {book:>5}  {verdict}")
    print()
    first = np.flatnonzero(t.daily)[0]
    print(
        f"  first units {t.units[0]:+.0f} on {f.days[0].date()} with the slope at "
        f"{f.slope[0]:g}, first return on {f.days[first].date()}"
    )
    q = result.quiet_start
    print(
        f"  no signal on rows 1 and 2, all {len(q.daily)} rows annualised: "
        f"APR {q.apr:.8f}, Sharpe ratio {q.sharpe:.8f}"
    )
    print()
    print("Location 1726's two claims, carried as findings with no verdict.")
    s = slope_findings(f.slope)
    print(
        f"  slope      median {s.median:.6f}, mean {s.mean:.6f}, above 1 on "
        f"{s.rows_above_one} of {s.rows} rows ({100 * s.rows_above_one / s.rows:.1f} percent), "
        f"{s.crossings} crossings of 1"
    )
    i = intercept_findings(f.days, f.intercept)
    yearly = ", ".join(f"{year} {mean:.4f}" for year, mean in i.yearly.items())
    print(f"  intercept  yearly means {yearly}")
    for label, falls in (
        ("yearly", i.by_year),
        ("quarterly", i.by_quarter),
        ("monthly", i.by_month),
        (f"{ROLLING_DAYS}-day rolling", i.rolling),
        ("daily", i.by_day),
    ):
        print(f"             {label} steps falling: {falls.falls} of {falls.steps}")
    print(f"             peak {i.peak:.6f} on {i.peak_day.date()}, last {i.last:.6f}")
    print()
    print(
        f"  Annualised over {TRADING_DAYS} days with no cost. Exploratory. "
        "docs/replication-log.md carries the verdicts."
    )


def run(data_dir: Path | None = None) -> KalmanHedge:
    """Read EWA and EWC, run the script, and print the report."""
    members, closes = read_sources(data_dir)
    result = kalman_hedge(closes)
    report(members, result)
    return result


def main() -> None:
    argparse.ArgumentParser(description=TITLE).parse_args()
    try:
        run()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day reaches the reader
        # as one line, the way chan.vx_es.main does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
