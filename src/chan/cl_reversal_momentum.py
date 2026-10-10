"""Crude oil reversal joined to momentum, *Algorithmic Trading*'s rule at location 2701.

On one shared lookback, a mean-reverting rule and a momentum rule take
opposite sides every day, so joining them would cancel. Chan gives them
different lookbacks, 30 and 40 trading days, and trades only on the days the
two agree. His claim at
Kindle location 2701, in Chapter 6, is that the join can beat either: "the
combination of mean-reverting and momentum rules may work better than each
strategy by itself." The rule he gives is to "buy at the market close if the
price is lower than that of 30 days ago and is higher than that of 40 days
ago; vice versa for shorts. If neither the buy nor the sell condition is
satisfied, flatten any existing position. The APR is 12 percent, with a Sharpe
ratio of 1.1." The text names no window and no save, and prints no figure for
either rule alone.

**What ``CL_rev.m`` holds.** The script is git blob ``420d501`` under
``public/img/book2/`` in the mirror
[ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) at
``e4bc46f``, 78 lines of which 46 hold code. It loads
``inputDataOHLCDaily_20120504`` and keeps CL's column of ``cl``, 1,000 rows.
Then it runs four rules, each earning
``backshift(1, positions).*(cl-backshift(1, cl))./backshift(1, cl)`` with
``ret(isnan(ret))=0``.

1. **The combination**, the book's rule. ``longs = cl < backshift(30, cl) &
   cl > backshift(40, cl)``, shorts the mirror, and positions of +1, −1 or 0.
   It prints ``APR=%f Sharpe=%f`` as ``prod(1+ret).^(252/length(ret))-1`` and
   ``sqrt(252)*mean(ret)/std(ret)`` over all 1,000 rows, and the comment under
   it reads ``APR=0.117600 Sharpe=1.100368``.
2. **Momentum only**, long above the 40-day lag and short below it.
3. **Reversal only**, long below the 30-day lag and short above it.
4. **"ComboOR"**, a long wherever either of the combination's long conditions
   holds and a short wherever either short condition holds, summed.

Rules 2 to 4 are plotted beside rule 1 and print nothing. The commented-out
lines are variants on ``lag`` and ``movingAvg`` that do not run, and the plot
is out of scope here.

**Why ComboOR is the combination under another name.** Call the reversal
condition "below the 30-day lag" and the momentum condition "above the 40-day
lag". Where both hold, both rules go long. Where neither holds, the close is
above the first lag and below the second, and both rules go short. Where
exactly one holds, OR scores a long and a short at once, which sums to flat,
and the combination is flat too. So the two can differ only where a lag is
missing or a close ties its lag. No close ties either lag on this save, and
they differ on the 10 rows where the 30-day lag exists and the 40-day one does
not, where OR trades the reversal rule alone. The same argument says swapping
the two lookbacks turns every long into a short, so which lookback carries
which rule decides the sign of every position.

**The run.** :func:`read_cl` reads CL from :data:`SOURCE_FILE` through
:func:`chan.series.load_panel`, cut to ``["CL"].dropna()``, since each symbol
in a continuous save keeps its own calendar. :func:`combination_positions`
signals against :func:`chan.matlab_helpers.backshift`, and a comparison
against the NaN a missing lag leaves is false, so the first 40 rows are flat.
:func:`trade` earns the script's return line, and the APR and the Sharpe
ratio are :func:`chan.khandani_lo_book_two.compounded_apr` and
:func:`chan.khandani_lo.plain_sharpe` over every row, flat rows included, as
the script measures them. ``plain_sharpe`` divides by n − 1, which is MATLAB's
``std``.

**The saves.** The series is back-adjusted at each roll, which
[issue 313](https://github.com/l3a0/quantitative-trading/issues/313) found by
comparing it with the front contract's settlements. It closes at 175.48 on
2008-05-19, well above the traded price, and a percentage return divides by
that shifted price. That makes the save part of the
specification. Three saves are read.

1. :data:`SOURCE_FILE`, the one the script loads, for the specification and
   the three rows beside it.
2. :data:`LATER_SOURCE_FILE`, which sits 0.27 higher on every day of the
   book's window, for one row showing what a later download of the same
   series gives.
3. :data:`EARLIER_SOURCE_FILE`, whose CL closes equal the first save's on all
   1,000 of the book's days and whose earlier rows therefore extend the same
   series backward. Its 998 rows before the book's window test the book's
   sentence on data the book did not report. That segment is back-adjusted
   further still, closing at 119.12 on 2004-05-24 while WTI averaged about $41
   that year (EIA's annual spot average, not measured here), so it is evidence
   about the sentence rather than a clean backtest.

**The scale-break guard.** :func:`read_cl` calls
:func:`chan.series.refuse_window_crossing_a_break` on CL over each span it
reads, in each save. Nothing in CL flags in any of the four continuous saves,
so nothing is refused.

``tests/test_cl_reversal_momentum.py`` pins every figure. Every result here is
exploratory. Reproducing Chan's figures spends the 2008 to 2012 sample on a
rule he chose, and nothing shows the lookbacks were fixed before the window
they are reported on was seen. The earlier segment was not registered before
it was read, so it is not a holdout either.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from chan.khandani_lo import TRADING_DAYS, plain_sharpe
from chan.khandani_lo_book_two import compounded_apr, gap, matches
from chan.matlab_helpers import backshift
from chan.series import (
    WindowCrossesScaleBreak,
    load_panel,
    refuse_window_crossing_a_break,
    vintage_line,
)
from chan.vintage import VintageEntry, VintageUnavailable

#: The save ``CL_rev.m`` loads. A save is named by the date in its file name.
#: This one was downloaded on 2012-05-07, and "the 2012-05-07 save" means
#: :data:`EARLIER_SOURCE_FILE`, not this file.
SOURCE_FILE = "inputDataOHLCDaily_20120504.mat"
#: A save whose CL closes equal the first's on the book's window, and run back to 2004.
EARLIER_SOURCE_FILE = "inputDataOHLCDaily_20120507.mat"
#: A later save, 0.27 higher on every day of the book's window.
LATER_SOURCE_FILE = "inputDataOHLCDaily_20120511.mat"

CL = "CL"
#: ``backshift(30, cl)``, the lag the reversal condition compares against.
REVERSAL_LOOKBACK = 30
#: ``backshift(40, cl)``, the lag the momentum condition compares against.
MOMENTUM_LOOKBACK = 40

#: The first and last of the 1,000 rows :data:`SOURCE_FILE` holds for CL.
BOOK_START = pd.Timestamp("2008-05-19")
BOOK_END = pd.Timestamp("2012-05-04")

#: The comment under ``CL_rev.m``'s ``fprintf``.
SCRIPT_APR = "0.117600"
SCRIPT_SHARPE = "1.100368"
#: What location 2701 prints.
BOOK_APR_PERCENT = "12"
BOOK_SHARPE = "1.1"


@dataclass(frozen=True)
class Trades:
    """One rule's positions and the returns they earn, over every row of one series."""

    days: pd.DatetimeIndex
    positions: NDArray[np.float64]
    daily: NDArray[np.float64]

    @property
    def apr(self) -> float:
        return compounded_apr(self.daily)

    @property
    def sharpe(self) -> float:
        return plain_sharpe(self.daily)

    @property
    def changes(self) -> int:
        """How many rows hold a different position from the row before."""
        return int(np.count_nonzero(np.diff(self.positions)))


@dataclass(frozen=True)
class FourRules:
    """``CL_rev.m``'s four rules on one series."""

    combination: Trades
    momentum: Trades
    reversal: Trades
    either: Trades


def _lags(
    closes: pd.Series, *lookbacks: int
) -> tuple[NDArray[np.float64], list[NDArray[np.float64]]]:
    close = closes.to_numpy(dtype=float)
    return close, [backshift(lookback, close) for lookback in lookbacks]


def _signed(longs: NDArray[np.bool_], shorts: NDArray[np.bool_]) -> NDArray[np.float64]:
    """+1 on a long, −1 on a short, summed, so a row holding both is flat.

    ``CL_rev.m`` sums only for ComboOR. Its other three rules assign the short
    over the long, which agrees with a sum because no row of theirs can hold
    both.
    """
    return longs.astype(float) - shorts.astype(float)


def combination_positions(
    closes: pd.Series,
    *,
    reversal: int = REVERSAL_LOOKBACK,
    momentum: int = MOMENTUM_LOOKBACK,
) -> NDArray[np.float64]:
    """Long below the reversal lag and above the momentum lag, short on the mirror, else flat."""
    close, (rev, mom) = _lags(closes, reversal, momentum)
    return _signed((close < rev) & (close > mom), (close > rev) & (close < mom))


def momentum_positions(
    closes: pd.Series, *, lookback: int = MOMENTUM_LOOKBACK
) -> NDArray[np.float64]:
    """Long above the lag and short below it."""
    close, (lag,) = _lags(closes, lookback)
    return _signed(close > lag, close < lag)


def reversal_positions(
    closes: pd.Series, *, lookback: int = REVERSAL_LOOKBACK
) -> NDArray[np.float64]:
    """Long below the lag and short above it."""
    close, (lag,) = _lags(closes, lookback)
    return _signed(close < lag, close > lag)


def either_positions(
    closes: pd.Series,
    *,
    reversal: int = REVERSAL_LOOKBACK,
    momentum: int = MOMENTUM_LOOKBACK,
) -> NDArray[np.float64]:
    """``CL_rev.m``'s "ComboOR": long where either long condition holds, short likewise, summed."""
    close, (rev, mom) = _lags(closes, reversal, momentum)
    return _signed((close < rev) | (close > mom), (close > rev) | (close < mom))


def trade(closes: pd.Series, positions: NDArray[np.float64]) -> Trades:
    """Earn yesterday's position on today's percentage move, with NaN set to 0."""
    close = closes.to_numpy(dtype=float)
    previous = backshift(1, close)
    daily = backshift(1, positions) * (close - previous) / previous
    daily[np.isnan(daily)] = 0
    return Trades(days=closes.index, positions=positions, daily=daily)


def four_rules(closes: pd.Series) -> FourRules:
    """The combination, each rule alone, and ComboOR, on the same series."""
    return FourRules(
        combination=trade(closes, combination_positions(closes)),
        momentum=trade(closes, momentum_positions(closes)),
        reversal=trade(closes, reversal_positions(closes)),
        either=trade(closes, either_positions(closes)),
    )


def read_cl(
    source_file: str = SOURCE_FILE,
    *,
    start: pd.Timestamp | None = None,
    end: pd.Timestamp | None = None,
    data_dir: Path | None = None,
) -> tuple[VintageEntry, pd.Series]:
    """CL's own rows in one save, cut to ``start`` and ``end`` and guarded over that span.

    Either bound left out keeps the save's own first or last row.
    """
    members, closes = load_panel(source_file, data_dir=data_dir)
    (member,) = [m for m in members if m.symbol == CL]
    cl = closes[CL].dropna()
    cl = cl.loc[
        start if start is not None else cl.index[0] : end if end is not None else cl.index[-1]
    ]
    refuse_window_crossing_a_break([(member, cl)], start=cl.index[0], end=cl.index[-1])
    return member, cl


def _verdict(value: float, printed: str) -> str:
    return "reproduced" if matches(value, printed) else f"gap {gap(value, printed):+g}"


def _span(days: pd.DatetimeIndex) -> str:
    return f"{days[0].date()} to {days[-1].date()}, {len(days)} rows"


def _row(label: str, traded: Trades) -> str:
    return f"  {label:<44} {traded.apr:>10.6f} {traded.sharpe:>10.6f}"


def report(
    member: VintageEntry,
    book: FourRules,
    later: Trades,
    earlier_member: VintageEntry,
    before: FourRules,
) -> None:
    """Print the vintage, each printed figure beside the computed one, and the rows beside them."""
    spec = book.combination
    print("Crude oil reversal joined to momentum, Algorithmic Trading location 2701")
    print(f"  vintage   {vintage_line(member)}")
    print(f"  window    {_span(spec.days)}")
    print()
    print(f"  {'Figure':<14} {'Computed':>10}  {'Script':>9}  {'Verdict':<12} {'Book':>5}  Verdict")
    for label, value, script, printed, scale in (
        ("APR", spec.apr, SCRIPT_APR, BOOK_APR_PERCENT, 100),
        ("Sharpe ratio", spec.sharpe, SCRIPT_SHARPE, BOOK_SHARPE, 1),
    ):
        print(
            f"  {label:<14} {value:>10.6f}  {script:>9}  {_verdict(value, script):<12} "
            f"{printed:>5}  {_verdict(scale * value, printed)}"
        )
    long, short = int((spec.positions > 0).sum()), int((spec.positions < 0).sum())
    first = spec.days[int(np.argmax(spec.positions != 0))].date()
    print(
        f"  long {long} rows, short {short}, flat {len(spec.days) - long - short}, "
        f"{spec.changes} changes, first position {first}"
    )
    print()
    print("Rows beside it. None carries a verdict.")
    print(f"  {'Row':<44} {'APR':>10} {'Sharpe':>10}")
    print(_row("Momentum only", book.momentum))
    print(_row("Reversal only", book.reversal))
    print(_row("ComboOR", book.either))
    print(_row("The combination, the 2012-05-11 save", later))
    print()
    print(f"Before the book's window, {_span(before.combination.days)}")
    print(f"  vintage   {vintage_line(earlier_member)}")
    print(_row("The combination", before.combination))
    print(_row("Momentum only", before.momentum))
    print(_row("Reversal only", before.reversal))
    print()
    print(f"  Annualised over {TRADING_DAYS} days with no cost, flat rows included.")
    print("  Exploratory. docs/replication-log.md carries the verdicts.")


def run(data_dir: Path | None = None) -> FourRules:
    """Read the three saves, run each rule, and print the report."""
    member, cl = read_cl(data_dir=data_dir)
    book = four_rules(cl)
    _, later_cl = read_cl(LATER_SOURCE_FILE, start=BOOK_START, end=BOOK_END, data_dir=data_dir)
    earlier_member, before_cl = read_cl(
        EARLIER_SOURCE_FILE, end=BOOK_START - pd.Timedelta(days=1), data_dir=data_dir
    )
    report(
        member,
        book,
        trade(later_cl, combination_positions(later_cl)),
        earlier_member,
        four_rules(before_cl),
    )
    return book


def main() -> None:
    argparse.ArgumentParser(
        description="Crude oil reversal joined to momentum, Algorithmic Trading location 2701"
    ).parse_args()
    try:
        run()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day reaches the reader
        # as one line, the way chan.price_spread.main does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
