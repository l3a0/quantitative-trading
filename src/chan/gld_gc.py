"""Long GLD and short gold futures, *Algorithmic Trading*'s trade on gold's roll return.

A future's total return is its spot return plus its roll return, the part
that comes from converging on the spot as it nears expiry. Gold futures carry
a negative roll return, so holding the metal and shorting the future should
collect it. GLD owns physical gold, which makes it the long leg. At Kindle
location 2718 Chan reports that "holding a long position in GLD and a short
position in GC yields an annualized return of 1.9 percent and a maximum
drawdown of 0.8 percent from August 3, 2007, to August 2, 2010". He then
spends the result: GLD's financing cost "is not very different from 1.9
percent over the backtest period", so "the excess return of this strategy is
close to zero". Location 2730 adds that GC settles at 1:30 p.m. ET while GLD
closes at 4:00 p.m. ET, and says that does not matter here. It landed here
for [issue 355](https://github.com/l3a0/quantitative-trading/issues/355).

**The transcription.** Every step is Chan's ``GLD_GC.m``, read in the mirror
[ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) at
``e4bc46f`` under ``public/img/book2/``. Nothing is ported, because the
sibling search on the issue found no code for this trade.

1. Load GC's closes from ``inputData_GC_1600_20100802`` and GLD's from
   ``inputData_ETF``.
2. Keep the days both hold, sorted, which is what MATLAB's ``intersect``
   returns. :func:`common_days` does it.
3. ``ret`` is GLD's daily return minus GC's, each taken across the kept rows,
   so a return can span a day one leg did not trade. :func:`daily_returns`
   does it.
4. ``ret(isnan(ret)) = 0``, which zeroes the first row.
5. Hold that every day with no signal, and print five figures through
   :func:`figures`: ``252 · smartmean(ret)``, the Sharpe ratio
   ``√252 · smartmean(ret − rf) / smartstd(ret − rf)`` with ``rf = 0.02 / 252``,
   the APR ``prod(1 + ret)^(252 / n) − 1``, and ``calculateMaxDD`` on
   ``cumprod(1 + ret) − 1`` for the deepest drawdown and its duration.

``smartstd`` is book two's, which divides by the count of finite entries, so
:func:`chan.matlab_helpers.smartstd_book_two` computes it. Neither mirror
holds the ``lag.m`` the script calls. A lag padded with NaN leaves the first
row's return NaN, and one padded with zeros, as LeSage's toolbox pads, gives
infinity minus infinity on that row, which is NaN too. Either way step 4
zeroes it, and ``tests/test_gld_gc.py`` holds both.

**The specification S, declared before any figure.** S is ``GLD_GC.m`` as
shipped, on the two vintages below. Issue 355 declared it on 2026-10-10 at
``a331fea``, before any of the five figures was computed, along with the
criterion. S reproduces the book where each printed figure matches under
:func:`chan.khandani_lo_book_two.matches`, which rounds the computed value to
the printed decimals, and where the duration equals 91 exactly. The text's 1.9
and 0.8 percent are checked the same way at one decimal. The text says
"annualized return" and the script prints two, the average and the
compounded APR, so the 1.9 is checked against both. A miss is reported with
its size through :func:`chan.khandani_lo_book_two.gap`.

**One row beside S.** B1 is the financing cost, the three-month bill rate
averaged over August 2007 to August 2010 through :func:`chan.bill_rates.average`,
set against S's average annual return. The book gives no bound for "not very
different", so B1 carries no verdict. The bill rate is a floor on what
financing GLD costs, because a trader borrows above it.

**The series is GC sampled at 16:00, not the 1:30 p.m. settlement.**
:func:`identity` measures what says so.

1. GC holds 9 rows GLD lacks, and every one is a US exchange holiday, which
   :data:`GC_ONLY_HOLIDAYS` names. A settlement series has no row on a day the
   exchange is shut.
2. The GC close of ``inputDataOHLCDaily_20120507``, a continuous series
   shifted at each roll, never equals this one on the 752 days they share,
   and their daily returns correlate well below 1.
3. The daily change in log(GC / GLD) moves far less on this series than on
   that one.

So the file is a continuous series read at GLD's own close, and location
2730's caveat does not reach the series the script reads.

**The vintages.** ``inputdata_gc_1600_20100802/gc.csv``, chan-mat, raw, saved
2012-05-07, 761 rows from 2007-08-03 to 2010-08-02, and
``inputdata_etf/gld.csv``, chan-mat, adjusted, saved 2012-04-10. GLD pays no
dividend, so its adjusted close is its close. The 2012-05-07 OHLC save's GC,
chan-mat, adjusted, saved 2012-05-09, is read for the identity alone. Each is
guarded by :func:`chan.series.refuse_window_crossing_a_break` over the
window, on its own calendar.

Every result here is exploratory. The window was the book's, so reproducing
its figures spends no fresh sample, and nothing here tests the trade on later
data.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray

from chan import bill_rates
from chan.khandani_lo_book_two import compounded_apr, gap, matches
from chan.matlab_helpers import calculate_max_dd, lag1, smartmean, smartstd_book_two
from chan.series import (
    WindowCrossesScaleBreak,
    load_panel,
    refuse_window_crossing_a_break,
    vintage_line,
)
from chan.vintage import VintageEntry, VintageUnavailable

GC_SOURCE_FILE = "inputData_GC_1600_20100802.mat"
GLD_SOURCE_FILE = "inputData_ETF.mat"
#: The OHLC save whose continuous GC series :func:`identity` sets beside the 16:00 one.
OHLC_SOURCE_FILE = "inputDataOHLCDaily_20120507.mat"
GC, GLD = "GC", "GLD"
#: Location 2718's window, which is also the GC file's first and last day.
WINDOW_START = pd.Timestamp("2007-08-03")
WINDOW_END = pd.Timestamp("2010-08-02")
TRADING_DAYS = 252
#: ``riskFreeRate=0.02/252``, the script's daily risk-free rate for the Sharpe ratio.
RISK_FREE_RATE = 0.02 / TRADING_DAYS
#: B1's months, both ends included, as :func:`chan.bill_rates.average` names them.
FINANCING_MONTHS = ("2007-08", "2010-08")
#: The rows GC holds and GLD lacks, each named for the US exchange holiday it falls on.
GC_ONLY_HOLIDAYS = {
    "2007-11-22": "Thanksgiving",
    "2008-01-21": "Martin Luther King Jr. Day",
    "2008-02-18": "Presidents' Day",
    "2008-05-26": "Memorial Day",
    "2008-07-04": "Independence Day",
    "2008-09-01": "Labor Day",
    "2008-11-27": "Thanksgiving",
    "2009-01-19": "Martin Luther King Jr. Day",
    "2009-02-16": "Presidents' Day",
}
#: A daily change in log(GC / GLD) past this is counted as a step by :func:`identity`.
STEP = 0.02

#: The script's closing comment, at the precision it prints.
BOOK_AVERAGE_ANNUAL_RETURN = "0.0190"
BOOK_SHARPE = "-0.07"
BOOK_APR = "0.0191"
BOOK_MAX_DRAWDOWN = "-0.008247"
BOOK_MAX_DRAWDOWN_DAYS = 91
#: Location 2718's text, in percent.
BOOK_TEXT_RETURN_PERCENT = "1.9"
BOOK_TEXT_MAX_DRAWDOWN_PERCENT = "0.8"


@dataclass(frozen=True)
class Sources:
    """Both legs as the script loads them, each with the entry that names its vintage."""

    gc_entry: VintageEntry
    gc: pd.Series
    gld_entry: VintageEntry
    gld: pd.Series


def _column(source_file: str, symbol: str, data_dir: Path | None) -> tuple[VintageEntry, pd.Series]:
    """One symbol's closes from one lifted file, guarded over the window on its own calendar."""
    members, closes = load_panel(source_file, data_dir=data_dir)
    (entry,) = [member for member in members if member.symbol == symbol]
    series = closes[symbol].dropna()
    refuse_window_crossing_a_break([(entry, series)], start=WINDOW_START, end=WINDOW_END)
    return entry, series


def read_sources(data_dir: Path | None = None) -> Sources:
    """GC from the 16:00 file and GLD from the ETF file, each guarded over the window."""
    gc_entry, gc = _column(GC_SOURCE_FILE, GC, data_dir)
    gld_entry, gld = _column(GLD_SOURCE_FILE, GLD, data_dir)
    return Sources(gc_entry=gc_entry, gc=gc, gld_entry=gld_entry, gld=gld)


def common_days(gc: pd.Series, gld: pd.Series) -> pd.DatetimeIndex:
    """``intersect(gc.tday, gld.tday)``: the days both hold, sorted ascending."""
    return gc.index.intersection(gld.index).sort_values()


def _simple_returns(closes: NDArray[np.float64]) -> NDArray[np.float64]:
    before = lag1(closes)
    return (closes - before) / before


def daily_returns(gld: ArrayLike, gc: ArrayLike) -> NDArray[np.float64]:
    """GLD's return minus GC's on paired rows, with every NaN set to 0 as the script sets it."""
    long_leg = np.asarray(gld, dtype=float)
    short_leg = np.asarray(gc, dtype=float)
    if long_leg.shape != short_leg.shape:
        raise ValueError(
            f"daily_returns pairs the two legs row by row, so they need one shape, not "
            f"{long_leg.shape} and {short_leg.shape}"
        )
    with np.errstate(invalid="ignore", divide="ignore"):
        ret = _simple_returns(long_leg) - _simple_returns(short_leg)
    return np.where(np.isnan(ret), 0.0, ret)


@dataclass(frozen=True)
class Figures:
    """The five figures ``GLD_GC.m`` prints, each from the line that prints it."""

    average_annual_return: float
    sharpe: float
    apr: float
    max_drawdown: float
    max_drawdown_days: int


def figures(daily: ArrayLike, risk_free: float = RISK_FREE_RATE) -> Figures:
    """The script's three printing lines on ``daily``."""
    ret = np.asarray(daily, dtype=float)
    excess = ret - risk_free
    max_drawdown, max_drawdown_days = calculate_max_dd(np.cumprod(1 + ret) - 1)
    return Figures(
        average_annual_return=TRADING_DAYS * float(smartmean(ret)),
        sharpe=math.sqrt(TRADING_DAYS)
        * float(smartmean(excess))
        / float(smartstd_book_two(excess)),
        apr=compounded_apr(ret),
        max_drawdown=max_drawdown,
        max_drawdown_days=max_drawdown_days,
    )


@dataclass(frozen=True)
class GldGc:
    """S on the kept days: the paired closes, the daily return and its figures."""

    days: pd.DatetimeIndex
    gc: NDArray[np.float64]
    gld: NDArray[np.float64]
    daily: NDArray[np.float64]

    @property
    def figures(self) -> Figures:
        return figures(self.daily)


def gld_gc(sources: Sources) -> GldGc:
    """Run ``GLD_GC.m`` on the two legs."""
    days = common_days(sources.gc, sources.gld)
    gc = sources.gc.loc[days].to_numpy(dtype=float)
    gld = sources.gld.loc[days].to_numpy(dtype=float)
    return GldGc(days=days, gc=gc, gld=gld, daily=daily_returns(gld, gc))


@dataclass(frozen=True)
class Financing:
    """B1: the bill rate over the window and what is left of S's return above it."""

    bill_rate: float
    months: int
    average_annual_return: float

    @property
    def excess(self) -> float:
        return self.average_annual_return - self.bill_rate


def financing(result: GldGc, data_dir: Path | None = None) -> Financing:
    """B1 on the committed TB3MS vintage over :data:`FINANCING_MONTHS`."""
    first, last = FINANCING_MONTHS
    return Financing(
        bill_rate=bill_rates.average(first, last, data_dir=data_dir),
        months=bill_rates.months_in(first, last, data_dir=data_dir),
        average_annual_return=result.figures.average_annual_return,
    )


@dataclass(frozen=True)
class RatioSteps:
    """The daily change in log(GC / GLD) on the kept days, for one GC series."""

    days: int
    spread: float
    largest: float
    steps: int


def ratio_steps(gc: pd.Series, gld: pd.Series, days: pd.DatetimeIndex) -> RatioSteps:
    """Measure the daily change in log(GC / GLD) from one of ``days`` to the next.

    ``spread`` is its standard deviation over n, ``largest`` its biggest move
    in size, and ``steps`` counts the moves larger than :data:`STEP`.
    """
    ratio = gc.loc[days].to_numpy(dtype=float) / gld.loc[days].to_numpy(dtype=float)
    change = np.diff(np.log(ratio))
    return RatioSteps(
        days=len(days),
        spread=float(np.std(change)),
        largest=float(np.abs(change).max()),
        steps=int((np.abs(change) > STEP).sum()),
    )


@dataclass(frozen=True)
class Identity:
    """What says the GC file is sampled at 16:00, beside the OHLC save's GC."""

    gc_only: list[pd.Timestamp]
    gld_only: list[pd.Timestamp]
    shared_with_ohlc: int
    equal_to_ohlc: int
    smallest_difference: float
    return_correlation: float
    first_ratio: float
    last_ratio: float
    sampled_at_1600: RatioSteps
    ohlc: RatioSteps
    ohlc_entry: VintageEntry


def identity(sources: Sources, result: GldGc, data_dir: Path | None = None) -> Identity:
    """Set the 16:00 GC series beside GLD's calendar and beside the OHLC save's GC."""
    ohlc_entry, ohlc = _column(OHLC_SOURCE_FILE, GC, data_dir)
    gld_window = sources.gld.loc[WINDOW_START:WINDOW_END]
    shared = result.days.intersection(ohlc.index)
    ours = sources.gc.loc[shared].to_numpy(dtype=float)
    theirs = ohlc.loc[shared].to_numpy(dtype=float)
    ratio = result.gc / result.gld
    return Identity(
        gc_only=list(sources.gc.index.difference(sources.gld.index)),
        gld_only=list(gld_window.index.difference(sources.gc.index)),
        shared_with_ohlc=len(shared),
        equal_to_ohlc=int((ours == theirs).sum()),
        smallest_difference=float(np.abs(ours - theirs).min()),
        return_correlation=float(
            np.corrcoef(_simple_returns(ours)[1:], _simple_returns(theirs)[1:])[0, 1]
        ),
        first_ratio=float(ratio[0]),
        last_ratio=float(ratio[-1]),
        sampled_at_1600=ratio_steps(sources.gc, sources.gld, result.days),
        ohlc=ratio_steps(ohlc, sources.gld, shared),
        ohlc_entry=ohlc_entry,
    )


def _verdict(value: float, printed: str) -> str:
    return (
        "reproduced"
        if matches(value, printed)
        else f"did not reproduce, gap {gap(value, printed):+g}"
    )


def _days_verdict(value: int, printed: int) -> str:
    return "reproduced" if value == printed else f"did not reproduce, gap {value - printed:+d}"


def _dates(days: list[pd.Timestamp]) -> str:
    return ", ".join(str(day.date()) for day in days)


def report(sources: Sources, result: GldGc, b1: Financing, found: Identity) -> None:
    """Print the vintages, the seven printed figures with their verdicts, B1 and the identity."""
    s = result.figures
    print("Long GLD and short gold futures, Algorithmic Trading's locations 2718 and 2730")
    print(f"  vintage  {vintage_line(sources.gc_entry)}")
    print(f"  vintage  {vintage_line(sources.gld_entry)}")
    print(
        f"  window   {result.days[0].date()} to {result.days[-1].date()}, {len(result.days)} "
        f"days both legs hold, of GC's {len(sources.gc)}"
    )
    print("  rule     GLD_GC.m as shipped, long GLD and short GC every day")
    print()
    rows = [
        ("Average annual return", s.average_annual_return, BOOK_AVERAGE_ANNUAL_RETURN),
        ("Sharpe ratio", s.sharpe, BOOK_SHARPE),
        ("APR", s.apr, BOOK_APR),
        ("Maximum drawdown", s.max_drawdown, BOOK_MAX_DRAWDOWN),
        ("Text return percent, average", 100 * s.average_annual_return, BOOK_TEXT_RETURN_PERCENT),
        ("Text return percent, APR", 100 * s.apr, BOOK_TEXT_RETURN_PERCENT),
        ("Text maximum drawdown percent", -100 * s.max_drawdown, BOOK_TEXT_MAX_DRAWDOWN_PERCENT),
    ]
    print(f"  {'Figure':<32} {'Computed':>12}  {'Chan':>9}  Verdict")
    for label, value, printed in rows:
        print(f"  {label:<32} {value:>12.6f}  {printed:>9}  {_verdict(value, printed)}")
    days_verdict = _days_verdict(s.max_drawdown_days, BOOK_MAX_DRAWDOWN_DAYS)
    print(
        f"  {'Maximum drawdown days':<32} {s.max_drawdown_days:>12d}  "
        f"{BOOK_MAX_DRAWDOWN_DAYS:>9d}  {days_verdict}"
    )
    print()
    print("Beside S. No book prints these, so none carries a verdict.")
    print(
        f"  B1  the three-month bill rate over {FINANCING_MONTHS[0]} to {FINANCING_MONTHS[1]}, "
        f"{b1.months} months, {b1.bill_rate:.6f}"
    )
    print(
        f"      S's average annual return {b1.average_annual_return:.6f} less it "
        f"{b1.excess:+.6f}, a floor on financing, so an upper bound on the excess"
    )
    print(f"  GC rows GLD lacks, {len(found.gc_only)}: {_dates(found.gc_only)}")
    print(f"  GLD rows in the window GC lacks, {len(found.gld_only)}: {_dates(found.gld_only)}")
    print(f"  the OHLC save, {vintage_line(found.ohlc_entry)}")
    print(
        f"    equal to the 16:00 close on {found.equal_to_ohlc} of "
        f"{found.shared_with_ohlc} shared days, the nearest {found.smallest_difference:.2f} "
        f"apart, daily return correlation {found.return_correlation:.6f}"
    )
    print(
        f"  GC / GLD on the first and last day {found.first_ratio:.3f} and {found.last_ratio:.3f}"
    )
    for label, steps in (("16:00 GC", found.sampled_at_1600), ("OHLC save GC", found.ohlc)):
        print(
            f"  daily change in log(GC / GLD), {label}, over {steps.days} days: standard "
            f"deviation {steps.spread:.6f}, largest {steps.largest:.6f}, "
            f"{steps.steps} moves past {STEP:g}"
        )
    print()
    print("  Annualised over 252 days, with no cost and no financing beyond B1.")
    print("  Exploratory. docs/replication-log.md Entry 38 carries the verdicts.")


def run(data_dir: Path | None = None) -> tuple[GldGc, Financing, Identity]:
    """Read both legs, guard them, run S, B1 and the identity, and print the report."""
    sources = read_sources(data_dir)
    result = gld_gc(sources)
    b1 = financing(result, data_dir)
    found = identity(sources, result, data_dir)
    report(sources, result, b1, found)
    return result, b1, found


def main() -> None:
    argparse.ArgumentParser(
        description="Long GLD and short gold futures, locations 2718 and 2730 of Algorithmic "
        "Trading"
    ).parse_args()
    try:
        run()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day reaches the reader
        # as one line, the way chan.roll_momentum.main does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
