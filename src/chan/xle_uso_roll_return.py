"""XLE against USO signed by crude oil's contango, *Algorithmic Trading*'s trade at location 2734.

No ETF holds physical crude oil, so no ETF pair can collect crude's roll
return the way GLD against a gold future can. Chan's Chapter 6 offers a looser
version. A fund of oil producers tracks the spot price, and a fund of oil
futures earns the roll return on top of the spot, so holding one against the
other in the direction the roll return favours should collect it. Every
location below is in ``research/book-notes/algorithmic-trading.md``.

1. **Location 1939.** USO "doesn't actually own oil. It invests in oil
   futures contracts", so XLE need not track it the way it tracks the spot.
2. **Location 2385.** A producer ETF such as XLE "usually cointegrates with
   the spot price", and the roll return can break its tie to the futures.
3. **Location 2718** defines contango as a negative roll return, with the far
   contract priced above the near one.
4. **Location 2734** gives the trade. "Short USO and long XLE whenever CL is
   in contango. Long USO and short XLE whenever CL is in backwardation. The
   APR is a very respectable 16 percent from April 26, 2006, to April 9, 2012,
   with a Sharpe ratio of about 1." Figure 6.3 draws its cumulative return.

**What ``XLE_CL_rollReturn.m`` holds.** The script is git blob ``e9b8981``
under ``public/img/book2/`` in the mirror
[ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) at
``e4bc46f``. It reads USO and XLE from ``inputData_ETF`` and the CL strip from
``inputDataDaily_CL_20120502``, and its closing comment prints five figures:
an average annual return of 0.1592, a Sharpe ratio of 1.05, an APR of 0.1591,
a maximum drawdown of −0.192321 and a longest drawdown of 487 days. The text
gives no rule for deciding contango beyond location 2718's definition, so the
rule here comes from the script alone. It fits no hedge ratio, no z-score and
no band, and the two legs are equal and fixed.

**The transcription.** Seven steps, each mapped to the function that runs it.

1. The script loads USO's and XLE's closes, then the strip's contracts, which
   :func:`read_sources` does through the two guarded read paths below.
2. ``ratioMatrix=(fwdshift(1, cl')./cl')'`` divides each contract by the one
   before it in the strip on the same day, the back over the front.
   :func:`front_ratio` computes it.
3. A contract's expiry is its last priced row,
   ``isfinite(cl) & ~isfinite(fwdshift(1, cl))``. Each contract is the front
   from :data:`FRONT_START` to :data:`FRONT_END` rows before its expiry, and a
   later contract starts no earlier than the row after the previous one ends,
   ``max(endIdx+1, expireIdx-40)``. The ratio is the front's on its rows and
   NaN on every other row. :func:`front_ratio` runs that loop too.
4. ``intersect`` keeps the days both calendars hold, which :func:`arbitrage`
   does with :meth:`pandas.Index.intersection`.
5. A ratio above 1 is contango, and the position is short USO and long XLE.
   Below 1 is backwardation, long USO and short XLE. A NaN ratio, and a ratio
   of exactly 1, hold nothing. :func:`positions` sets them.
6. ``ret=smartsum(lag(positions,1).*pctchange,2)/2`` with NaN set to 0, so
   each leg carries half the capital. :func:`daily_returns` earns it, with
   :func:`chan.matlab_helpers.backshift` for ``lag``.
7. The figures are ``252*smartmean(ret)``, ``sqrt(252)*smartmean/smartstd``,
   ``prod(1+ret)^(252/n)-1`` and ``calculateMaxDD(cumprod(1+ret)-1)``, which
   is :func:`chan.tu_momentum.figures` exactly, with
   :func:`chan.matlab_helpers.smartstd_book_two` dividing by n.

**Why the calendar spread's schedule is not reused.**
:func:`chan.calendar_spread_reversion.calendar_schedule` with
``spread_month=1`` and ``holddays=0``, read through
:func:`chan.vx_calendar_spread.held_pair_ratio`, gives the same ratio on every
row both define. It differs in three ways.

1. It starts the first pair ``holddays + 10`` rows before expiry, not 40.
2. It drops a pair with fewer than ``holddays`` rows.
3. ``held_pair_ratio`` fills forward across unheld rows, where this script
   leaves NaN.

The first difference leaves CL-2007F's 31 front rows, 2006-10-20 to
2006-12-05, unheld, and those sit inside the window. Bending the schedule to
this script would add a fourth branch to code written for Example 5.4, so
:func:`front_ratio` carries its own loop.

**Two quirks of the loop that do not fire on this strip.** The transcription
names them rather than copying them silently.

1. **A contract with no expiry, or with two.** In MATLAB, a contract with no
   priced row makes ``endIdx`` empty, and the next contract's
   ``max(endIdx+1, ...)`` is then empty too, so it assigns nothing. A
   contract whose prices stop and restart marks two expiries, and MATLAB's
   colon reads the first. No contract in this strip is all NaN or carries two
   marks, so :func:`front_ratio` refuses either rather than guess at which
   reading Chan's run would have taken. The function is read on this strip
   alone, and other committed strips carry contracts it would refuse.
2. **The contracts still trading on the file's last day.** 24 contracts are
   priced on 2012-05-02, the strip's last row, so each reads as expiring
   there. The front from 2012-04-09 is CL-2012M, the first of them. Its
   window starts on the row after CL-2012K's ends, so its own 40-row start
   does not bind, and its window stops at 2012-04-18. The last 10 rows get no
   ratio, all after the trade's last day of 2012-04-09.

**The data.** Two committed vintages, both chan-mat.

1. **USO and XLE** from ``inputData_ETF.mat``, basis ``adjusted``, saved
   2012-04-10, 1,500 rows from 2006-04-26 to 2012-04-09 with no missing close.
   [Issue 299](https://github.com/l3a0/quantitative-trading/issues/299) found
   that this file subtracts each dividend in dollars from every earlier close.
   That leaves the replication untouched, because Chan's script read the same
   bytes. It does change what a holder of XLE earned, and no second XLE
   series over this window is committed to measure by how much.
2. **The CL strip** from ``inputDataDaily_CL_20120502.mat``, basis ``raw``,
   saved 2012-05-03, 89 contracts from CL-2007F to CL-2014K over 2,867 days
   from 2000-11-20, with no spot column.

The two calendars share 1,498 days. The ETF file holds 2006-07-03 and
2006-11-24, which the strip lacks. The first front window opens on 2006-10-20,
so the window's first 123 shared days carry a NaN ratio and hold nothing.

**The scale-break guard.** :func:`read_sources` reads the strip through
:func:`chan.roll_returns.load_strip`, which guards every contract over its own
rows. It calls :func:`chan.series.refuse_window_crossing_a_break` on XLE and
USO over the ETF file's whole span, 2006-04-26 to 2012-04-09, as
:mod:`chan.kalman_hedge` does for EWA and EWC. Nothing flags in either read,
so nothing is refused.

``tests/test_xle_uso_roll_return.py`` pins every figure. Every result here is
exploratory. Reproducing Chan's figures spends his 2006 to 2012 sample on a
rule he chose, so the run says whether his numbers reproduce on his files and
nothing about whether the trade pays out of sample.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from chan.khandani_lo_book_two import gap, matches
from chan.matlab_helpers import backshift, fwdshift, smartsum
from chan.roll_returns import Strip, load_strip
from chan.series import (
    WindowCrossesScaleBreak,
    load_panel,
    panel_line,
    refuse_window_crossing_a_break,
    vintage_line,
)
from chan.tu_momentum import Figures, figures
from chan.vintage import VintageEntry, VintageUnavailable

#: The ETF file the script's first load line reads.
ETF_FILE = "inputData_ETF.mat"
#: The strip the script's second load line reads.
STRIP_FILE = "inputDataDaily_CL_20120502.mat"
ROOT = "CL"
USO = "USO"
XLE = "XLE"
#: The order of the script's ``[uso xle]``, and so of a row of positions.
LEGS = (USO, XLE)

#: ``numDaysStart``, the rows before expiry a contract becomes the front.
FRONT_START = 40
#: ``numDaysEnd``, the rows before expiry a contract stops being the front.
FRONT_END = 10

#: Short USO and long XLE, in :data:`LEGS` order.
CONTANGO = (-1.0, 1.0)
#: Long USO and short XLE.
BACKWARDATION = (1.0, -1.0)

#: The ETF file's first and last day, the span location 2734 names.
WINDOW_START = pd.Timestamp("2006-04-26")
WINDOW_END = pd.Timestamp("2012-04-09")

#: The script's closing comment.
SCRIPT_AVERAGE_ANNUAL_RETURN = "0.1592"
SCRIPT_SHARPE = "1.05"
SCRIPT_APR = "0.1591"
SCRIPT_MAX_DRAWDOWN = "-0.192321"
SCRIPT_MAX_DRAWDOWN_DAYS = "487"
#: What location 2734 prints, "16 percent" and "about 1".
BOOK_APR_PERCENT = "16"
BOOK_SHARPE = "1"


@dataclass(frozen=True)
class Arbitrage:
    """The trade on the days both calendars hold, row for row."""

    days: pd.DatetimeIndex
    ratio: NDArray[np.float64]
    positions: NDArray[np.float64]
    daily: NDArray[np.float64]

    @property
    def figures(self) -> Figures:
        return figures(self.daily)

    @property
    def flat(self) -> int:
        """How many rows hold nothing, a NaN ratio or a ratio of exactly 1."""
        return int((self.positions == 0).all(axis=1).sum())


def _expiry(priced: NDArray[np.bool_], column: str) -> int:
    """The one row on which ``column`` is priced and the next row is not."""
    marks = np.flatnonzero(priced & ~np.append(priced[1:], False))
    if len(marks) != 1:
        raise ValueError(
            f"{column} marks {len(marks)} expiries, and the script's loop is read here "
            "only for a contract with exactly one"
        )
    return int(marks[0])


def front_ratio(contracts: pd.DataFrame) -> pd.Series:
    """The back contract over the front on each front row, NaN on every other row.

    ``contracts`` holds the strip's contracts in delivery order. Each contract
    but the last is the front from :data:`FRONT_START` to :data:`FRONT_END`
    rows before its last priced row, starting no earlier than the row after
    the previous front ended. A contract marking no expiry or two is refused,
    for the reason the module docstring gives, and so is a first front window
    that would start before the strip's first row.
    """
    prices = contracts.to_numpy(dtype=float)
    back_over_front = fwdshift(1, prices.T).T / prices
    priced = np.isfinite(prices)
    ratio = np.full(len(prices), np.nan)
    end = None
    for c, column in enumerate(contracts.columns[:-1]):
        expiry = _expiry(priced[:, c], column)
        if end is None:
            start = expiry - FRONT_START
            if start < 0:
                raise ValueError(
                    f"{column}'s front window would start before the strip's first row, "
                    f"at row {start}"
                )
        else:
            start = max(end + 1, expiry - FRONT_START)
        end = expiry - FRONT_END
        ratio[start : end + 1] = back_over_front[start : end + 1, c]
    return pd.Series(ratio, index=contracts.index, name="front_ratio")


def positions(ratio: NDArray[np.float64]) -> NDArray[np.float64]:
    """One row per day in :data:`LEGS` order: contango above 1, backwardation below, else flat."""
    ratio = np.asarray(ratio, dtype=float)
    held = np.zeros((len(ratio), len(LEGS)))
    with np.errstate(invalid="ignore"):
        held[ratio > 1] = CONTANGO
        held[ratio < 1] = BACKWARDATION
    return held


def daily_returns(closes: pd.DataFrame, held: NDArray[np.float64]) -> NDArray[np.float64]:
    """Yesterday's positions on today's moves, summed over the legs and halved, NaN set to 0."""
    prices = closes[list(LEGS)].to_numpy(dtype=float)
    previous = backshift(1, prices)
    ret = smartsum(backshift(1, held) * (prices - previous) / previous, axis=1) / 2
    return np.where(np.isnan(ret), 0.0, ret)


def arbitrage(closes: pd.DataFrame, ratio: pd.Series) -> Arbitrage:
    """Steps 4 to 6 on the ETF closes and the strip's front ratio."""
    days = closes.index.intersection(ratio.index).sort_values()
    on_days = ratio.loc[days].to_numpy(dtype=float)
    held = positions(on_days)
    return Arbitrage(
        days=days, ratio=on_days, positions=held, daily=daily_returns(closes.loc[days], held)
    )


def read_sources(
    data_dir: Path | None = None,
) -> tuple[list[VintageEntry], pd.DataFrame, Strip]:
    """USO and XLE guarded over the ETF file's span, and the strip through its guarded reader."""
    members, closes = load_panel(ETF_FILE, data_dir=data_dir)
    read = [next(m for m in members if m.symbol == symbol) for symbol in LEGS]
    frame = closes[list(LEGS)]
    refuse_window_crossing_a_break(
        [(m, frame[m.symbol]) for m in read], start=frame.index[0], end=frame.index[-1]
    )
    strip = load_strip(ROOT, data_dir, source_file=STRIP_FILE)
    return read, frame, strip


def _verdict(value: float, printed: str) -> str:
    return "reproduced" if matches(value, printed) else f"gap {gap(value, printed):+g}"


def report(etf: list[VintageEntry], strip: Strip, result: Arbitrage) -> None:
    """Print the vintages, each printed figure beside the computed one, and the counts."""
    f = result.figures
    print("XLE against USO signed by crude oil's contango, Algorithmic Trading location 2734")
    for member in etf:
        print(f"  vintage   {vintage_line(member)}")
    print(f"  strip     {panel_line(strip.members)}")
    print(
        f"  window    {result.days[0].date()} to {result.days[-1].date()}, "
        f"{len(result.days)} days both calendars hold"
    )
    print(
        f"  rule      the back contract over the front, the front from {FRONT_START} to "
        f"{FRONT_END} rows before its last price."
    )
    print("            Above 1 short USO and long XLE, below 1 the reverse, half the capital each.")
    print()
    print(f"  {'Figure':<24} {'Computed':>10}  {'Script':>9}  {'Verdict':<12} {'Book':>5}  Verdict")
    for label, value, script, book in (
        ("Average annual return", f.average_annual_return, SCRIPT_AVERAGE_ANNUAL_RETURN, None),
        ("Sharpe ratio", f.sharpe, SCRIPT_SHARPE, (f.sharpe, BOOK_SHARPE)),
        ("APR", f.apr, SCRIPT_APR, (100 * f.apr, BOOK_APR_PERCENT)),
        ("Maximum drawdown", f.max_drawdown, SCRIPT_MAX_DRAWDOWN, None),
    ):
        line = f"  {label:<24} {value:>10.6f}  {script:>9}  {_verdict(value, script):<12}"
        if book is not None:
            line += f" {book[1]:>5}  {_verdict(*book)}"
        print(line.rstrip())
    days = f.max_drawdown_days
    print(
        f"  {'Longest drawdown, days':<24} {days:>10d}  {SCRIPT_MAX_DRAWDOWN_DAYS:>9}  "
        f"{_verdict(days, SCRIPT_MAX_DRAWDOWN_DAYS)}"
    )
    print()
    contango = int((result.ratio > 1).sum())
    backwardation = int((result.ratio < 1).sum())
    unset = int(np.isnan(result.ratio).sum())
    first = result.days[int(np.argmax(np.isfinite(result.ratio)))].date()
    print(
        f"  contango on {contango} days, backwardation on {backwardation}, "
        f"no ratio on {unset}, a ratio of exactly 1 on {result.flat - unset}"
    )
    print(f"  first front ratio {first}")
    print()
    print("  Annualised over 252 days with no cost. The ETF closes subtract dividends in dollars.")
    print("  Exploratory. docs/replication-log.md carries the verdicts.")


def run(data_dir: Path | None = None) -> Arbitrage:
    """Read both vintages, run the trade, and print the report."""
    etf, closes, strip = read_sources(data_dir)
    result = arbitrage(closes, front_ratio(strip.contracts))
    report(etf, strip, result)
    return result


def main() -> None:
    argparse.ArgumentParser(
        description="XLE against USO signed by crude oil's contango, Algorithmic Trading 2734"
    ).parse_args()
    try:
        run()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day reaches the reader
        # as one line, the way chan.price_spread.main does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
