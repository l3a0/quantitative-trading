"""Khandani and Lo's reversal on Chan's 2012 panel, *Algorithmic Trading*'s Examples 4.3 and 4.4.

The rule weights every stock in the index by minus its return against the
equal-weighted market, so it buys what fell most against its peers and shorts
what rose most. *Algorithmic Trading*'s Example 4.3 holds those weights from
one close to the next. At Kindle location 2110 Chan reports "an APR of 13.7
percent and Sharpe ratio of 1.3 from January 2, 2007, to December 30, 2011",
and an APR "of 30 percent in 2008" and "11 percent in 2011". Example 4.4 takes
its signal from the gap between yesterday's close and today's open, enters at
the open and exits at the same day's close, and location 2135 reports "73
percent and 4.7".

**The transcription.** Every step is Chan's ``andrewlo_2007_2012.m`` and the
helpers beside it, read in the mirror
[ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) at
``e4bc46f`` under ``public/img/book2/``. The mirror
[ivanliu1989/algorithmic_trading](https://github.com/ivanliu1989/algorithmic_trading)
at ``45670240f1f3d4b5233a75f82fd18b742455b4bb`` holds the same file under
``archived/matlab/``, byte for byte, with sha256
``673b1cfd2bfeac676ff8f01550d13551c564670d79b976c49311188c1a5c7be9``. It
landed here under [issue 296](https://github.com/l3a0/quantitative-trading/issues/296).
Both examples run on the closes and opens cut to 2007-01-03 through
2011-12-30 before any return is taken, which is 1,260 rows. The book's
January 2 was a market holiday, so no row carries it.

Example 4.3:

1. ``ret = (cl − lag(cl)) / lag(cl)``, which is
   :func:`chan.khandani_lo.daily_returns`.
2. The market's return each day is the mean of the finite returns.
3. ``w = −(ret − market)``, each row divided by the sum of its finite
   ``|w|``, so every day with a return holds a gross position of exactly 1.
   A stock with no return keeps a NaN weight, which the sums skip.
4. The day's profit is yesterday's weights times today's returns, summed over
   the finite products, and a day with none is 0.

Example 4.4 weights the gap from yesterday's close to today's open, which is
:func:`chan.pead.close_to_open`, the same way, and its day's profit is those
weights times the same day's open-to-close return. Its figures divide that sum
by the gross a second time, as the script does, which moves nothing but a day
with no weight at all.

Both examples print ``prod(1 + r)^(252 / n) − 1`` as the APR and
``√252 · mean / std`` as the Sharpe ratio, with MATLAB's own ``mean`` and
``std`` over all 1,260 rows, the zeros included, so the deviation divides by
n − 1. That is :func:`chan.khandani_lo.plain_sharpe` on a series with nothing
left to skip.

**The first days earn nothing, because the cut comes first.** 2007-01-03 has
no return. 2007-01-04 holds 2007-01-03's weights, which are all NaN, so
Example 4.3's first two days are 0 and Example 4.4's first day is. Neither
mirror holds the ``lag.m`` the script calls. A lag padded with NaN and one
padded with zeros, as LeSage's toolbox pads, both leave the first row's return
non-finite, and both helpers skip a non-finite value, so the series is the same
either way. ``tests/test_khandani_lo_book_two.py`` holds that.

**The script's file name.** It loads ``inputDataOHLCDaily_20120424``, without
``_stocks``. ``data/README.md`` records the copy under that name as the same
bytes as the committed panel, so this module reads the panel by its committed
name.

**What changed on the way over.** Five things, and none moves a figure.

1. The panel is read as a committed vintage through
   :func:`chan.series.load_panel`, and the window is cut by date rather than by
   ``find`` on ``tday``.
2. Each example's window is an argument, so the first bridge below can hand
   Example 4.3 the first book's file and year.
3. The two ``plot`` lines are not carried. The run prints and draws nothing.
4. The commented-out cost and Kelly lines print nothing and are not carried.
   One of them still reads "Sharpe ratio should be about 0.25", which is
   ``example3_7.m``'s comment, so the script began as a copy of the first
   book's.
5. The yearly APRs have no line in the script. Each applies the script's APR
   line to one calendar year of the full run's series, rather than rerunning
   the year on its own, which would zero its first two days.

**How this differs from the first book's rule.** :mod:`chan.khandani_lo`
transcribes ``example3_7.m``, which divides each day's weights by the count of
stocks priced, sets a missing price's weight to 0, charges 5 basis points a
side, takes returns on the whole file and cuts the profit afterwards, and mixes
``smartmean`` with the first edition's ``smartstd``. So its
``reversal_weights``, ``reversal`` and ``chan_sharpe`` are a different rule and
are not called for either example. Example 4.4 is neither of Example 3.8's
rules, which signal and hold from one open to the next.

Two bridge rows set the books side by side. Book two's rule on the first
book's file and year, and the first book's rule on this panel and window. No
book prints either, so neither carries a verdict.

**The scale-break guard is not called, and that was decided here.**
:func:`chan.series.refuse_window_crossing_a_break` refuses this window, on 17
stocks' closes and 14 stocks' opens read from each stock's own rows. On the
close they are the 30 days ``tests/test_scale_breaks.py`` pins, all in 2007 to
2009. Chan's script computes across them, and his figures reproduce only with
them in, so refusing the window would refuse the computation being reproduced.

Most of the flags read as the 2008 crisis, the moves a reversal rule is meant
to see, which is [issue 22](https://github.com/l3a0/quantitative-trading/issues/22)'s
reasoning for momentum. Not all of them do. CAH's close falls from 19.96 to
14.50 on 2009-09-01 and rises to 23.57 the next day, which reads as a data
error or a corporate action rather than a crash, and without CAH Example 4.3
gives 13.26 percent and 1.2267, so neither of Chan's figures reproduces. The
opens' flags were counted rather than read, and three of their stocks, HBAN,
SLM and ZION, are flagged on the open only. The decision is about reproducing
this script, and it is not a ruling for any other rule on this panel.

**Every figure here is about survivors.** The panel is the S&P 500 as Chan
held it on 2012-04-24, carried backwards. Chan calls the years from 2008 "a
true out-of-sample test" because the strategy was published in 2007. They are
out of sample in time, but the stocks were chosen with 2012's membership.
[Issue 252](https://github.com/l3a0/quantitative-trading/issues/252) prices
survivorship on this file for Example 7.2 over 2011 and 2012, and nothing yet
prices it for this rule over 2007 to 2011.

Every result here is exploratory. Reproducing Chan's figures spends the 2007
to 2011 sample on a rule somebody else chose, so the run says whether his
numbers reproduce on his file and nothing about whether the rule pays today.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from chan import khandani_lo
from chan.khandani_lo import TRADING_DAYS, Reversal, daily_returns, plain_sharpe, reversal
from chan.matlab_helpers import backshift, smartmean, smartsum
from chan.pead import close_to_open
from chan.series import load_panel, panel_line
from chan.vintage import VintageUnavailable

SOURCE_FILE = "inputDataOHLCDaily_stocks_20120424.mat"

#: ``find(tday==20070103)`` and ``find(tday==20111230)``, inclusive.
WINDOW_START = "2007-01-03"
WINDOW_END = "2011-12-30"

#: Example 4.3's figures, location 2110. Percentages as the book prints them.
BOOK_43_APR_PERCENT = "13.7"
BOOK_43_SHARPE = "1.3"
#: The two calendar years location 2110 names, with the APR it gives each.
BOOK_YEAR_APR_PERCENT = {2008: "30", 2011: "11"}
#: Example 4.4's figures, location 2135. Location 2890 repeats the 4.7.
BOOK_44_APR_PERCENT = "73"
BOOK_44_SHARPE = "4.7"
#: Example 4.4's figures as the script's ``fprintf`` printed them.
SCRIPT_44_APR = "0.731553"
SCRIPT_44_SHARPE = "4.713284"


def window(frame: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    """The rows from ``start`` to ``end``, both inclusive, cut before any return is taken."""
    inside = (frame.index >= pd.Timestamp(start)) & (frame.index <= pd.Timestamp(end))
    return frame.loc[inside]


def gross_weights(signal: np.ndarray) -> np.ndarray:
    """``−(signal − market)``, each row divided by the sum of its finite ``|w|``.

    The market is the mean of the finite signals that day. A stock whose
    signal is not finite keeps a NaN weight, which is how the script leaves
    it, and every later sum skips it.
    """
    market = smartmean(signal, axis=1)
    weights = -(signal - market[:, None])
    with np.errstate(invalid="ignore", divide="ignore"):
        return weights / smartsum(np.abs(weights), axis=1)[:, None]


def _zero_filled(daily: np.ndarray) -> np.ndarray:
    """``dailyret(isnan(dailyret))=0``: a day with nothing to sum earns 0."""
    return np.where(np.isnan(daily), 0.0, daily)


def held_overnight(weights: np.ndarray, returns: np.ndarray) -> np.ndarray:
    """Example 4.3's day: yesterday's weights times today's returns, summed."""
    return _zero_filled(smartsum(backshift(1, weights) * returns, axis=1))


def held_intraday(weights: np.ndarray, opens: np.ndarray, closes: np.ndarray) -> np.ndarray:
    """Example 4.4's day: today's weights times today's open-to-close return, over the gross."""
    with np.errstate(invalid="ignore", divide="ignore"):
        day = smartsum(weights * (closes - opens) / opens, axis=1)
        return _zero_filled(day / smartsum(np.abs(weights), axis=1))


def compounded_apr(daily: np.ndarray) -> float:
    """``prod(1 + r)^(252 / n) − 1`` over every row handed in."""
    return float(np.prod(1 + daily) ** (TRADING_DAYS / len(daily)) - 1)


@dataclass(frozen=True)
class Run:
    """One example's daily profit over its window and the two figures the script prints."""

    days: pd.DatetimeIndex
    daily: np.ndarray
    weights: np.ndarray

    @property
    def apr(self) -> float:
        return compounded_apr(self.daily)

    @property
    def sharpe(self) -> float:
        return plain_sharpe(self.daily)

    def year_apr(self, year: int) -> float:
        """The script's APR line on one calendar year of this run's series."""
        return compounded_apr(self.daily[self.days.year == year])


def close_to_close(closes: pd.DataFrame, *, start: str, end: str) -> Run:
    """Example 4.3 on a date-by-stock frame of closes, cut to ``start`` and ``end`` first."""
    cut = window(closes, start, end)
    returns = daily_returns(cut.to_numpy(dtype=float))
    weights = gross_weights(returns)
    return Run(days=cut.index, daily=held_overnight(weights, returns), weights=weights)


def open_to_close(opens: pd.DataFrame, closes: pd.DataFrame, *, start: str, end: str) -> Run:
    """Example 4.4 on frames of opens and closes holding the same days and stocks."""
    if not (opens.index.equals(closes.index) and opens.columns.equals(closes.columns)):
        raise ValueError("the opens and the closes must hold the same days and stocks in one order")
    op = window(opens, start, end)
    cl = window(closes, start, end).to_numpy(dtype=float)
    weights = gross_weights(close_to_open(op.to_numpy(dtype=float), cl))
    return Run(
        days=op.index,
        daily=held_intraday(weights, op.to_numpy(dtype=float), cl),
        weights=weights,
    )


def matches(value: float, printed: str) -> bool:
    """Whether ``value`` rounds to ``printed`` at the decimals ``printed`` carries."""
    decimals = len(printed.partition(".")[2])
    return round(value, decimals) == round(float(printed), decimals)


def gap(value: float, printed: str) -> float:
    """Computed minus published, at the published figure's precision."""
    decimals = len(printed.partition(".")[2])
    return round(value - float(printed), decimals)


@dataclass(frozen=True)
class BookTwo:
    """Both examples on the 2012 panel, and the two bridge rows beside the first book.

    ``rule_on_first_file`` is Example 4.3's rule on ``SPX_20071123.mat``'s
    closes over the first book's year. ``first_rule_on_panel`` is
    :func:`chan.khandani_lo.reversal` on this panel's closes over this window.
    """

    close_to_close: Run
    open_to_close: Run
    rule_on_first_file: Run
    first_rule_on_panel: Reversal


def book_two(opens: pd.DataFrame, closes: pd.DataFrame, first_file_closes: pd.DataFrame) -> BookTwo:
    """Run both examples and both bridge rows on frames already read."""
    return BookTwo(
        close_to_close=close_to_close(closes, start=WINDOW_START, end=WINDOW_END),
        open_to_close=open_to_close(opens, closes, start=WINDOW_START, end=WINDOW_END),
        rule_on_first_file=close_to_close(
            first_file_closes, start=khandani_lo.WINDOW_START, end=khandani_lo.WINDOW_END
        ),
        # reversal defaults to the first book's 2006, and this panel starts on
        # 2006-05-11. Left out, the window opens on a day with no earlier
        # weights, and plain_sharpe refuses that day's NaN cost with a message
        # that says nothing about the window.
        first_rule_on_panel=reversal(closes, start=WINDOW_START, end=WINDOW_END),
    )


def _verdict(value: float, printed: str) -> str:
    return (
        "reproduced"
        if matches(value, printed)
        else f"did not reproduce, gap {gap(value, printed):+g}"
    )


def report(members, result: BookTwo) -> None:
    """Print the panel, the window, each figure beside the book's, and the two bridge rows."""
    a, b = result.close_to_close, result.open_to_close
    print(
        "Khandani and Lo's linear reversal on Chan's 2012 panel, "
        "Algorithmic Trading's Examples 4.3 and 4.4"
    )
    print(f"  vintage  {panel_line(members)}")
    print(
        f"  window   {a.days[0].date()} to {a.days[-1].date()}, {len(a.days)} trading days, "
        "cut before any return"
    )
    print("  rule     weight = -(signal - equal-weighted market), scaled to a gross of 1 each day")
    print(
        f"  figures  APR = prod(1 + r)^({TRADING_DAYS} / n) - 1, "
        f"Sharpe = sqrt({TRADING_DAYS}) * mean / std, no cost"
    )
    print()
    rows = [
        ("4.3 close to close, APR percent", 100 * a.apr, BOOK_43_APR_PERCENT),
        ("4.3 close to close, Sharpe", a.sharpe, BOOK_43_SHARPE),
        *(
            (f"4.3 close to close, APR percent in {year}", 100 * a.year_apr(year), printed)
            for year, printed in BOOK_YEAR_APR_PERCENT.items()
        ),
        ("4.4 open to close, APR percent", 100 * b.apr, BOOK_44_APR_PERCENT),
        ("4.4 open to close, Sharpe", b.sharpe, BOOK_44_SHARPE),
        ("4.4 open to close, APR as the script prints it", b.apr, SCRIPT_44_APR),
        ("4.4 open to close, Sharpe as the script prints it", b.sharpe, SCRIPT_44_SHARPE),
    ]
    print(f"  {'Figure':<50} {'Computed':>10}  {'Chan':>9}  Verdict")
    for label, value, printed in rows:
        print(f"  {label:<50} {value:>10.6f}  {printed:>9}  {_verdict(value, printed)}")
    print()
    first = result.first_rule_on_panel
    cost = f"{khandani_lo.ONE_WAY_COST * 1e4:.0f} bp a side"
    print("Beside the first book. No book prints these, so neither carries a verdict.")
    print(
        f"  Book two's rule on {khandani_lo.SOURCE_FILE} over 2006, Sharpe "
        f"{result.rule_on_first_file.sharpe:.4f}, where Example 3.7 printed "
        f"{khandani_lo.BOOK_BEFORE_COSTS:.2f}"
    )
    print(
        f"  Example 3.7's rule on this panel and window, Sharpe {first.before_costs:.4f} "
        f"before costs and {first.after_costs_charged:.4f} after {cost}"
    )
    print()
    print(
        "  The panel holds only the stocks still in the index on 2012-04-24, "
        "so every figure is about survivors."
    )
    print("  Exploratory. docs/replication-log.md carries the verdicts.")


def run(data_dir: Path | None = None) -> BookTwo:
    """Read the panel's opens and closes and the first book's closes, run, and print."""
    members, closes = load_panel(SOURCE_FILE, data_dir=data_dir)
    _, opens = load_panel(SOURCE_FILE, field="Open", data_dir=data_dir)
    _, first_file = load_panel(khandani_lo.SOURCE_FILE, data_dir=data_dir)
    result = book_two(opens, closes, first_file)
    report(members, result)
    return result


def main() -> None:
    argparse.ArgumentParser(
        description="Khandani and Lo's linear reversal on Chan's 2012 panel, "
        "Algorithmic Trading's Examples 4.3 and 4.4"
    ).parse_args()
    try:
        run()
    except VintageUnavailable as unavailable:
        # A refusal that names the source is worth nothing at the bottom of a
        # pandas traceback, so it reaches the reader as one line, the way
        # chan.khandani_lo.main does it.
        raise SystemExit(str(unavailable)) from unavailable


if __name__ == "__main__":
    main()
