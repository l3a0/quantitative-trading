"""Time-series momentum on two-year Treasury note futures, *Algorithmic Trading*'s Example 6.1.

A trend follower bets that a price which rose over some past window keeps
rising over the next one. Example 6.1, at Kindle locations 2623 to 2668, tests
that bet on TU, the two-year Treasury note future, before trading it. It
correlates TU's past return over a lookback with its future return over a
holding period, for every pair of 1, 5, 10, 25, 60, 120 and 250 days, and
reports that the 250-day lookback and 25-day hold "have a correlation
coefficient of 0.27 with a p-value of 0.02". It adds that "the Hurst exponent
is 0.44, while the Variance Ratio test failed to reject the hypothesis that
this is a random walk". Then it trades the pair: buy when the 250-day return is
positive, sell when it is negative, and decide every day with a twenty-fifth
of the capital. "From June 1, 2004, to May 11, 2012, the Sharpe ratio is a
respectable 1", with an APR of 1.7 percent and a maximum drawdown of 2.5
percent.

**The transcription.** Every step is Chan's ``TU_mom.m``, read under
``public/img/book2/`` in the mirror
[ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) at
``e4bc46f``, git blob ``f7935c7``, and landed here for
[issue 351](https://github.com/l3a0/quantitative-trading/issues/351). It loads
``inputDataOHLCDaily_20120511`` and keeps TU's column of ``tday`` and ``cl``.

1. **The correlation table**, :func:`correlation`. For each lookback and hold,
   ``ret_lag = (cl − backshift(lookback, cl)) / backshift(lookback, cl)`` and
   ``ret_fut = (fwdshift(holddays, cl) − cl) / cl``. Rows where either is NaN
   are deleted, and every ``min(lookback, holddays)``-th row of what is left
   is kept, starting at the first, so overlapping windows do not count the
   same move twice. ``corrcoef``'s coefficient and p-value are
   :func:`scipy.stats.pearsonr`'s, the same two-sided t-test on n − 2 degrees
   of freedom.
2. **The two tests.** ``genhurst(log(cl), 2)`` at its default ``maxT`` of 19
   and ``vratiotest(log(cl))`` at its default period of 2, which are
   :func:`chan.stationarity_tests.genhurst` and
   :func:`chan.stationarity_tests.vratiotest`.
3. **The signals**, :func:`signals`. ``longs = cl > backshift(250, cl)`` and
   ``shorts = cl < backshift(250, cl)``. A comparison with NaN is false, so
   the first 250 rows are neither.
4. **The positions**, :func:`positions`. For ``h`` from 0 to 24, add 1 where
   ``backshift(h, longs)`` is true and subtract 1 where ``backshift(h,
   shorts)`` is true, NaN read as false. Each day's signal opens a tranche held
   for 25 days, so the position runs from −25 to 25.
5. **The return**, :func:`strategy_returns`. Yesterday's position times
   today's return, divided by 25, with NaN set to 0. Dividing by the tranche
   count rather than by the gross position is what makes each tranche a
   twenty-fifth of the capital.
6. **The figures**, :func:`figures`. ``252·smartmean(ret)``,
   ``√252·smartstd(ret)``, ``√252·smartmean(ret)/smartstd(ret)``, the
   compounded APR, ``calculateMaxDD(cumprod(1 + ret) − 1)``, and the Kelly f
   ``mean(ret)/std(ret)²``. ``smartstd`` is book two's, which divides by n,
   and the Kelly f's ``std`` is MATLAB's, which divides by n − 1.

**The book's figures come from the full window, not the script's active
line.** The script picks its window with ``idx = find(tday == 20090102)`` and
leaves ``% idx=1;`` commented out under it. All six figures in its closing
comment land on ``idx = 1``, the 2,000 rows from 2004-06-01 that the book's
sentence names, and none lands on 2009-01-02. The comment also prints no
annual volatility although the format string asks for one, so it was pasted
from an earlier version of the printing line. The specification is therefore
``TU_mom.m`` with ``idx = 1``, and :func:`tu_momentum` carries the 2009-01-02
window beside it as a row with no published figure.

**The save is the 2012-05-11 one.** ``correlationTest.m``, git blob
``3be3d50``, runs step 1 alone on the 2012-05-17 save, which shifts TU's
2,000 rows four trading days later. On it the 250/25 correlation rounds to
0.29 rather than 0.27, and the Kelly f misses the script's printed digits.
:func:`run` reads that save for one row beside the replication.

**The Hurst exponent misses.** H on TU is 0.43 at two decimals, against the
book's 0.44. Example 2.2's H on USD.CAD misses the same way through the same
:func:`chan.stationarity_tests.genhurst`, and raising ``maxT`` moves TU
towards 0.44 while it moves USD.CAD further from 0.49, so no single ``maxT``
lands both. ``tests/test_tu_momentum.py`` pins every one of those numbers.

**Chan's Python port is a different strategy.** ``TU_mom.py`` in the 2018
``PythonCodesAndData.zip`` loops ``h`` over 0 to 23 rather than 24 and divides
the day's profit by the gross position rather than by 25. It prints no figure,
so it is not a source of pins.

**What Example 1.1 imports.** ``TU_mom_hypothesisTest.m``, git blob
``c0dda16``, runs these positions on simulated prices and on shuffled signals,
which :mod:`chan.tu_hypothesis_tests` transcribes.
So :data:`SOURCE_FILE`, :data:`SYMBOL`, :data:`LOOKBACK`, :data:`HOLD_DAYS`,
:data:`SCRIPT_GAUSSIAN_STATISTIC`, :func:`read_sources`, :func:`signals`,
:func:`positions`, :func:`market_returns`, :func:`strategy_returns` and
:func:`gaussian_statistic` are public, and
:func:`positions` takes the two signal arrays rather than prices, because the
third test shuffles them first. ``hold_days`` appears in both
:func:`positions` and :func:`strategy_returns`, and the two must agree,
because the divisor is the tranche count. :func:`strategy_returns` refuses a
position larger in magnitude than its ``hold_days``. That catches a mismatch
which would overstate the return only when some position grows past the
divisor. Shuffled signals that cancel can stay inside it, so a caller passes
both functions the same ``hold_days`` rather than relying on the refusal.

**The vintage.** ``inputdataohlcdaily_20120511/tu.csv``, one column of Chan's
``inputDataOHLCDaily_20120511.mat``, read through
:func:`chan.series.load_panel` as ``closes["TU"].dropna()``. It is chan-mat,
adjusted, saved 2012-05-12, and holds 2,000 days from 2004-06-01 to
2012-05-11, exactly the book's window.

**The scale-break guard runs and refuses nothing.**
:func:`chan.series.refuse_window_crossing_a_break` flags only ZB and ZF in
Chan's continuous futures saves, so :func:`read_sources` calls it on TU over
its whole span and a bad print would stop the run.

**What changed on the way over.** Four things, and none moves a figure.

1. TU is read as a committed vintage through :func:`chan.series.load_panel`
   rather than loaded from the ``.mat``.
2. The ``plot`` of the cumulative return is not carried. The run draws
   nothing.
3. The positions and the return are split into the four functions Example 1.1
   imports, and the return multiplies yesterday's position by a market return
   computed once, as ``TU_mom_hypothesisTest.m`` writes it.
   ``tests/test_tu_momentum.py`` holds the returns identical whether or not
   the market return's leading NaN is first set to 0.
4. The run calls the scale-break guard, which the script has no counterpart
   for.

Every result here is exploratory. Reproducing Chan's figures spends the 2004
to 2012 sample on a lookback and a hold he chose from the same table, so the
run says whether his numbers reproduce on his file and nothing about whether
the rule pays today.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray
from scipy.stats import pearsonr

from chan.kelly_leverage import annualised_moments
from chan.khandani_lo import TRADING_DAYS
from chan.khandani_lo_book_two import compounded_apr, gap, matches
from chan.matlab_helpers import (
    backshift,
    calculate_max_dd,
    fwdshift,
    smartmean,
    smartstd_book_two,
)
from chan.series import (
    WindowCrossesScaleBreak,
    load_panel,
    refuse_window_crossing_a_break,
    vintage_line,
)
from chan.stationarity_tests import VarianceRatio, genhurst, vratiotest
from chan.vintage import VintageEntry, VintageUnavailable

SOURCE_FILE = "inputDataOHLCDaily_20120511.mat"
#: The save ``correlationTest.m`` loads, read for one row beside the replication.
LATER_SOURCE_FILE = "inputDataOHLCDaily_20120517.mat"
SYMBOL = "TU"
#: ``lookback`` and ``holddays`` of the traded rule.
LOOKBACK = 250
HOLD_DAYS = 25
#: The lookbacks and holds of the correlation table, in the script's order.
PERIODS = (1, 5, 10, 25, 60, 120, 250)
#: Location 2646's "best compromises", as ``(lookback, hold)``.
COMPROMISES = ((60, 10), (60, 25), (250, 10), (250, 25), (250, 60), (250, 120))
#: ``genhurst(log(cl), 2)``.
HURST_Q = 2
#: The ``maxT`` the diagnostic beside the Hurst row reads, where H on TU first rounds to 0.44.
HURST_DIAGNOSTIC_MAX_T = 24
#: The script's active line, ``idx = find(tday == 20090102)``.
ACTIVE_LINE_START = pd.Timestamp("2009-01-02")

#: ``TU_mom.m``'s closing comment.
SCRIPT_AVERAGE_ANNUAL_RETURN = "0.0167"
SCRIPT_SHARPE = "1.04"
SCRIPT_APR = "0.0167"
SCRIPT_MAX_DRAWDOWN = "-0.024847"
SCRIPT_MAX_DRAWDOWN_DAYS = 343
SCRIPT_KELLY = "64.919535"
#: ``TU_mom_hypothesisTest.m``'s first printed figure, ``mean/std·√n``.
SCRIPT_GAUSSIAN_STATISTIC = "2.93"
#: Locations 2646, 2659 and 2668.
BOOK_CORRELATION = "0.27"
BOOK_P_VALUE = "0.02"
BOOK_HURST = "0.44"
BOOK_SHARPE = "1"
BOOK_APR_PERCENT = "1.7"
BOOK_MAX_DRAWDOWN_PERCENT = "2.5"
BOOK_FIRST_DAY = pd.Timestamp("2004-06-01")
BOOK_LAST_DAY = pd.Timestamp("2012-05-11")


@dataclass(frozen=True)
class Correlation:
    """One cell of the table: the coefficient, its two-sided p-value and the rows it used."""

    coefficient: float
    p_value: float
    rows: int


def correlation(closes: ArrayLike, lookback: int, hold: int) -> Correlation:
    """Step 1 for one pair: past against future returns, every ``min(lookback, hold)``-th row."""
    cl = np.asarray(closes, dtype=float)
    with np.errstate(invalid="ignore", divide="ignore"):
        before = backshift(lookback, cl)
        past = (cl - before) / before
        future = (fwdshift(hold, cl) - cl) / cl
    kept = ~(np.isnan(past) | np.isnan(future))
    step = min(lookback, hold)
    past, future = past[kept][::step], future[kept][::step]
    coefficient, p_value = pearsonr(past, future)
    return Correlation(float(coefficient), float(p_value), len(past))


def correlation_table(closes: ArrayLike) -> dict[tuple[int, int], Correlation]:
    """Step 1: every lookback against every hold in :data:`PERIODS`, keyed ``(lookback, hold)``."""
    return {
        (lookback, hold): correlation(closes, lookback, hold)
        for lookback in PERIODS
        for hold in PERIODS
    }


def signals(
    closes: ArrayLike, lookback: int = LOOKBACK
) -> tuple[NDArray[np.bool_], NDArray[np.bool_]]:
    """Step 3: ``longs`` where the close is above the one ``lookback`` rows back, ``shorts`` below.

    A comparison with the NaN padding is false, so the first ``lookback`` rows
    are neither.
    """
    cl = np.asarray(closes, dtype=float)
    before = backshift(lookback, cl)
    return cl > before, cl < before


def positions(
    longs: ArrayLike, shorts: ArrayLike, hold_days: int = HOLD_DAYS
) -> NDArray[np.float64]:
    """Step 4: the open tranches, +1 for each long and −1 for each short of the last ``hold_days``.

    Row t adds up the signals of rows t − hold_days + 1 through t, so a
    position runs from ``−hold_days`` to ``hold_days``. A row before the first
    signal counts as no signal, which is the script's NaN read as false. A NaN
    in a float signal reads as false too, where a plain cast to bool would open
    a tranche.
    """
    long_signal = np.nan_to_num(np.asarray(longs, dtype=float), nan=0.0) != 0
    short_signal = np.nan_to_num(np.asarray(shorts, dtype=float), nan=0.0) != 0
    if long_signal.shape != short_signal.shape or long_signal.ndim != 1:
        raise ValueError("positions takes a longs and a shorts of one length")
    if hold_days < 1:
        raise ValueError(f"positions holds each tranche for at least 1 day, not {hold_days}")
    held = np.zeros(len(long_signal))
    for h in range(hold_days):
        held += np.nan_to_num(backshift(h, long_signal), nan=0.0) == 1
        held -= np.nan_to_num(backshift(h, short_signal), nan=0.0) == 1
    return held


def market_returns(closes: ArrayLike) -> NDArray[np.float64]:
    """``(cl − backshift(1, cl)) / backshift(1, cl)`` with a value that is not finite set to 0.

    That is ``TU_mom_hypothesisTest.m``'s ``marketRet``, so the first row is 0.
    """
    cl = np.asarray(closes, dtype=float)
    before = backshift(1, cl)
    with np.errstate(invalid="ignore", divide="ignore"):
        market = (cl - before) / before
    return np.where(np.isfinite(market), market, 0.0)


def strategy_returns(
    positions: ArrayLike, market: ArrayLike, hold_days: int = HOLD_DAYS
) -> NDArray[np.float64]:
    """Step 5: ``backshift(1, pos)·market / hold_days``, with NaN set to 0.

    The multiplication comes before the division, the script's order. A
    position larger in magnitude than ``hold_days`` is refused, because it
    means the positions were built with more tranches than this divides by,
    which would overstate the return. Positions built with more tranches whose
    longs and shorts cancel can stay inside the bound, and those pass.
    """
    held = np.asarray(positions, dtype=float)
    returns = np.asarray(market, dtype=float)
    if held.shape != returns.shape:
        raise ValueError(
            f"strategy_returns takes positions and market returns of one shape, not "
            f"{held.shape} and {returns.shape}"
        )
    largest = np.nanmax(np.abs(held), initial=0.0)
    if largest > hold_days:
        raise ValueError(
            f"a position of {largest:g} tranches cannot be held a {hold_days}th of the capital "
            f"at a time. Build the positions and the returns with the same hold_days"
        )
    with np.errstate(invalid="ignore"):
        daily = backshift(1, held) * returns / hold_days
    return np.where(np.isnan(daily), 0.0, daily)


@dataclass(frozen=True)
class Figures:
    """Step 6 over one window of daily returns, every figure the script's printing lines give."""

    average_annual_return: float
    annual_volatility: float
    sharpe: float
    apr: float
    max_drawdown: float
    max_drawdown_days: int
    kelly: float


def figures(daily: ArrayLike) -> Figures:
    """The printing lines of ``TU_mom.m`` on ``daily``, each through the helper that computes it."""
    ret = np.asarray(daily, dtype=float)
    mean = float(smartmean(ret))
    spread = float(smartstd_book_two(ret))
    max_drawdown, max_drawdown_days = calculate_max_dd(np.cumprod(1 + ret) - 1)
    return Figures(
        average_annual_return=TRADING_DAYS * mean,
        annual_volatility=math.sqrt(TRADING_DAYS) * spread,
        sharpe=math.sqrt(TRADING_DAYS) * mean / spread,
        apr=compounded_apr(ret),
        max_drawdown=max_drawdown,
        max_drawdown_days=max_drawdown_days,
        kelly=annualised_moments(pd.Series(ret), risk_free=0.0).period_leverage,
    )


def hurst_at(closes: ArrayLike, max_t: int = HURST_DIAGNOSTIC_MAX_T) -> float:
    """``genhurst(log(cl), 2, maxT)``, the diagnostic beside the Hurst row."""
    return genhurst(np.log(np.asarray(closes, dtype=float)), q=HURST_Q, max_t=max_t)


def gaussian_statistic(daily: ArrayLike) -> float:
    """``mean(ret)/std(ret)·√n`` with the n − 1 ``std``, ``TU_mom_hypothesisTest.m``'s first."""
    ret = np.asarray(daily, dtype=float)
    return float(ret.mean() / ret.std(ddof=1) * math.sqrt(len(ret)))


@dataclass(frozen=True)
class TuMomentum:
    """``TU_mom.m`` on one save of TU's closes.

    ``positions`` and ``daily`` hold a row for every day. ``figures`` reads
    every row, which is ``idx = 1``, and ``active_line_figures`` the rows from
    2009-01-02 on, which is the script's active line.
    """

    days: pd.DatetimeIndex
    closes: NDArray[np.float64]
    correlations: dict[tuple[int, int], Correlation]
    hurst: float
    variance_ratio: VarianceRatio
    positions: NDArray[np.float64]
    daily: NDArray[np.float64]

    @property
    def figures(self) -> Figures:
        return figures(self.daily)

    @property
    def active_line_days(self) -> pd.DatetimeIndex:
        return self.days[self.days.get_loc(ACTIVE_LINE_START) :]

    @property
    def active_line_figures(self) -> Figures:
        return figures(self.daily[self.days.get_loc(ACTIVE_LINE_START) :])

    @property
    def traded(self) -> Correlation:
        return self.correlations[(LOOKBACK, HOLD_DAYS)]


def tu_momentum(closes: pd.Series) -> TuMomentum:
    """Run steps 1 to 5 of ``TU_mom.m`` on one series of TU's closes."""
    cl = closes.to_numpy(dtype=float)
    held = positions(*signals(cl))
    return TuMomentum(
        days=closes.index,
        closes=cl,
        correlations=correlation_table(cl),
        hurst=genhurst(np.log(cl), q=HURST_Q),
        variance_ratio=vratiotest(np.log(cl)),
        positions=held,
        daily=strategy_returns(held, market_returns(cl)),
    )


def _read(source_file: str, data_dir: Path | None) -> tuple[VintageEntry, pd.Series]:
    members, closes = load_panel(source_file, data_dir=data_dir)
    (entry,) = [member for member in members if member.symbol == SYMBOL]
    tu = closes[SYMBOL].dropna()
    refuse_window_crossing_a_break([(entry, tu)], start=tu.index[0], end=tu.index[-1])
    return entry, tu


def read_sources(data_dir: Path | None = None) -> tuple[VintageEntry, pd.Series]:
    """TU's entry and its 2,000 closes from the 2012-05-11 save, after the scale-break guard."""
    return _read(SOURCE_FILE, data_dir)


def read_later_save(data_dir: Path | None = None) -> tuple[VintageEntry, pd.Series]:
    """TU's entry and closes from the 2012-05-17 save ``correlationTest.m`` loads, guarded."""
    return _read(LATER_SOURCE_FILE, data_dir)


def _verdict(value: float, printed: str) -> str:
    return (
        "reproduced"
        if matches(value, printed)
        else f"did not reproduce, gap {gap(value, printed):+g}"
    )


def report(
    entry: VintageEntry, result: TuMomentum, later_entry: VintageEntry, later: TuMomentum
) -> None:
    """Print the vintage, the table, each printed figure beside the computed one, and the rest."""
    found = result.figures
    print(
        "Time-series momentum on two-year Treasury note futures, Algorithmic Trading's Example 6.1"
    )
    print(f"  vintage  {vintage_line(entry)}")
    print(
        f"  window   {result.days[0].date()} to {result.days[-1].date()}, {len(result.days)} "
        "trading days, TU_mom.m with idx = 1"
    )
    print(
        f"  rule     long when the {LOOKBACK}-day return is positive, short when negative, "
        f"each day's call held {HOLD_DAYS} days with 1/{HOLD_DAYS} of the capital"
    )
    print()
    print("  Correlation of past and future returns, coefficient (p-value)")
    print("  " + "lookback\\hold".ljust(14) + "".join(f"{hold:>17}" for hold in PERIODS))
    for lookback in PERIODS:
        cells = "".join(
            f"{cell.coefficient:>8.4f} ({cell.p_value:6.4f})"
            for cell in (result.correlations[(lookback, hold)] for hold in PERIODS)
        )
        print(f"  {lookback:<14}{cells}")
    print()
    vr = result.variance_ratio
    rows = [
        ("250/25 correlation", result.traded.coefficient, BOOK_CORRELATION),
        ("250/25 p-value", result.traded.p_value, BOOK_P_VALUE),
        ("Hurst exponent", result.hurst, BOOK_HURST),
        ("Average annual return", found.average_annual_return, SCRIPT_AVERAGE_ANNUAL_RETURN),
        ("Sharpe ratio", found.sharpe, SCRIPT_SHARPE),
        ("Sharpe ratio, book", found.sharpe, BOOK_SHARPE),
        ("APR", found.apr, SCRIPT_APR),
        ("APR percent, book", 100 * found.apr, BOOK_APR_PERCENT),
        ("Maximum drawdown", found.max_drawdown, SCRIPT_MAX_DRAWDOWN),
        ("Maximum drawdown percent, book", -100 * found.max_drawdown, BOOK_MAX_DRAWDOWN_PERCENT),
        ("Kelly f", found.kelly, SCRIPT_KELLY),
    ]
    print(f"  {'Figure':<32} {'Computed':>12}  {'Chan':>10}  Verdict")
    for label, value, printed in rows:
        print(f"  {label:<32} {value:>12.6f}  {printed:>10}  {_verdict(value, printed)}")
    longest = found.max_drawdown_days
    print(
        f"  {'Longest drawdown, days':<32} {longest:>12}  {SCRIPT_MAX_DRAWDOWN_DAYS:>10}  "
        f"{_verdict(longest, str(SCRIPT_MAX_DRAWDOWN_DAYS))}"
    )
    print(
        f"  {'Variance ratio test rejects':<32} {'yes' if vr.rejects else 'no':>12}  {'no':>10}  "
        f"{'did not reproduce' if vr.rejects else 'reproduced'}, p = {vr.p_value:.6f}"
    )
    print()
    print("Beside the replication. No book prints these, so none carries a verdict.")
    print("  The six pairs location 2646 calls the best compromises")
    for lookback, hold in COMPROMISES:
        cell = result.correlations[(lookback, hold)]
        print(
            f"    {lookback:>3}/{hold:<3}  {cell.coefficient:.4f}, p {cell.p_value:.4f}, "
            f"{cell.rows} rows"
        )
    print(f"  annual volatility, idx = 1           {found.annual_volatility:.6f}")
    print(f"  Gaussian statistic, mean/std*sqrt(n)  {gaussian_statistic(result.daily):.4f}")
    print(
        f"  Hurst exponent at maxT = {HURST_DIAGNOSTIC_MAX_T}         {hurst_at(result.closes):.6f}"
    )
    days = result.active_line_days
    active = result.active_line_figures
    print(f"  the script's active line, {days[0].date()} to {days[-1].date()}, {len(days)} days")
    print(
        f"    average annual return {active.average_annual_return:.6f}, Sharpe ratio "
        f"{active.sharpe:.6f}, APR {active.apr:.6f}"
    )
    print(
        f"    maximum drawdown {active.max_drawdown:.6f} over {active.max_drawdown_days} days, "
        f"Kelly f {active.kelly:.6f}"
    )
    print(f"  the 2012-05-17 save, {vintage_line(later_entry)}")
    print(
        f"    {later.days[0].date()} to {later.days[-1].date()}, 250/25 correlation "
        f"{later.traded.coefficient:.4f}, p {later.traded.p_value:.4f}, Hurst {later.hurst:.6f}, "
        f"Kelly f {later.figures.kelly:.6f}"
    )
    print()
    print(
        f"  Annualised over {TRADING_DAYS} days with no risk-free rate and no cost, on "
        "back-adjusted closes."
    )
    print("  Exploratory. docs/replication-log.md Entry 33 carries the verdicts.")


def run(data_dir: Path | None = None) -> tuple[TuMomentum, TuMomentum]:
    """Read both saves, guard them, run the script on each, and print the report."""
    entry, closes = read_sources(data_dir)
    later_entry, later_closes = read_later_save(data_dir)
    result = tu_momentum(closes)
    later = tu_momentum(later_closes)
    report(entry, result, later_entry, later)
    return result, later


def main() -> None:
    argparse.ArgumentParser(
        description="Time-series momentum on two-year Treasury note futures, Example 6.1 of "
        "Algorithmic Trading"
    ).parse_args()
    try:
        run()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day reaches the reader
        # as one line, the way chan.price_spread.main does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
