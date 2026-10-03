"""Khandani and Lo's linear reversal on Chan's S&P 500 file, Example 3.7.

The rule buys the stocks that fell most against the market yesterday and
shorts the ones that rose most. Khandani and Lo report a Sharpe ratio of 4.47
for 2006, at Kindle location 2099. Chan reruns it on the S&P 500 and gets
0.25, at location 2137, then charges 5 basis points a trade and gets −3.19, at
location 2233. The lesson is the collapse. A cost a large-cap trader pays every
day turns a small edge into a large loss, and Chan's explanation at location
2137 is that most of Khandani and Lo's returns came from small and microcap
stocks.

Nothing here reproduces 4.47. It was computed on a universe this repo does not
hold, so it is printed as the paper's figure and asserted nowhere.

**The transcription.** Every step is Chan's ``example3_7.m`` and the four
helpers it calls, read in the mirror
[egorpe/EPChan-QuantitativeTrading](https://github.com/egorpe/EPChan-QuantitativeTrading)
at ``1a7195003cf3e85a806e18867e0af547d17ad5c4``. The four helpers come from
:mod:`chan.matlab_helpers`, under their MATLAB names, which
[issue 18](https://github.com/l3a0/quantitative-trading/issues/18) built for
Examples 7.6 and 7.7 on the same file. This module passes them a column with
``axis=0`` or a panel with ``axis=1``, which are the shapes on which they
match the ``.m`` files.

On the full panel, before any window is cut:

1. ``ret = (cl − lag1(cl)) / lag1(cl)``.
2. The market's return each day is the mean of the finite returns that day.
3. ``w = −(ret − market) / n``, where ``n`` counts the stocks with a finite
   close that day, not the ones with a finite return.
4. ``w`` is 0 wherever today's close or yesterday's is not finite.
5. The day's profit is the sum over stocks of yesterday's weight times today's
   return, skipping a product that is not finite.

The weights sum to zero across stocks every day and are not scaled to a unit of
gross exposure. Multiplying every weight by one constant leaves both Sharpe
ratios unchanged, because the profit and the cost scale together. Scaling each
day to a unit of gross exposure is a different rule, because the factor then
changes from day to day, and it moves both figures. The cost is 5 basis points on each side of
a change in weight, ``0.0005 · Σ|w[t] − w[t−1]|``, which is location 998's
convention that a round trip is two transactions. The Sharpe ratio is
``√252 · mean / std`` with no risk-free rate subtracted.

**Two quirks are kept, because they move the printed figure.**

1. **The first day's rebalance is never charged.** Chan cuts the weights to
   2006 before differencing them, so the first row of the difference is NaN,
   ``smartsum`` of an all-NaN row is NaN, and the after-cost series carries one
   NaN, on 2006-01-03.
2. **``smartstd`` zero-fills that NaN where ``smartmean`` skips it.** The
   deviation is taken over all 251 rows with a 0 in the first, while the mean
   is taken over the other 250.

A port that skips the NaN in both, the way pandas does, lands on −3.1822 and
misses Chan's −3.19 at the two decimals he printed. ``tests/test_khandani_lo.py`` pins what each
specification gives, and :func:`reversal` returns both Chan's figures and the
after-cost figure with both quirks removed, so the distance between them is
printed rather than argued.

**The vintage.** ``spx_20071123/``, the 500 stocks of Chan's
``SPX_20071123.mat``, read as one frame through
:func:`chan.series.load_panel`. It is the S&P 500 as it stood on 2007-11-23,
carried backwards, so a company that left the index before then is absent and
every figure here is a figure about survivors.
[Issue 198](https://github.com/l3a0/quantitative-trading/issues/198) and
[issue 213](https://github.com/l3a0/quantitative-trading/issues/213) are where
survivorship is priced.

**The scale-break guard is not called, and that was decided here.**
:func:`chan.series.refuse_window_crossing_a_break` reads single series, and
neither answer it gives on this panel is about a scale break this run computes
across. Given the panel's columns it refuses, because ten stocks have a NaN
close inside 2006 and it cannot read the days beside one. Given each member's
own rows it passes, because WYN, which holds two companies under one symbol,
has no row in 2006 before its 2006-08-01 restart. Chan's rule
already puts a weight of 0 on every return that is not finite. WYN's
2006-07-31 is NaN on the panel's grid, so its 2006-08-01 return is NaN and
never enters a weight. That is why returns are computed on the panel rather
than on one member's rows, as ``load_panel`` says.

The variation that trades at the open is Example 3.8, and
[issue 206](https://github.com/l3a0/quantitative-trading/issues/206) carries
it. Every result here is exploratory. Reproducing Chan's figures spends the
2006 sample on a rule somebody else chose, so the run says whether his numbers
reproduce on his file and nothing about whether the rule pays today.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from chan.matlab_helpers import lag1, smartmean, smartstd, smartsum
from chan.series import load_panel, panel_line
from chan.vintage import VintageUnavailable

SOURCE_FILE = "SPX_20071123.mat"

#: ``startDate`` and ``endDate`` in ``example3_7.m``, inclusive.
WINDOW_START = "2006-01-01"
WINDOW_END = "2006-12-31"

#: ``onewaytcost``, 5 basis points on each side of a change in weight.
ONE_WAY_COST = 0.0005

#: The annualisation in both of Chan's Sharpe ratios.
TRADING_DAYS = 252

#: Khandani and Lo's 2006 Sharpe ratio, Kindle location 2099. On their own
#: universe, which this repo does not hold, so nothing here computes it.
BOOK_KHANDANI_LO = 4.47
#: Chan's figure before costs, location 2137 and again at 2233.
BOOK_BEFORE_COSTS = 0.25
#: Chan's figure after 5 basis points a trade, location 2233.
BOOK_AFTER_COSTS = -3.19


def daily_returns(closes: np.ndarray) -> np.ndarray:
    """Step 1: each stock's return on each day, NaN where either close is missing."""
    previous = lag1(closes)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (closes - previous) / previous


def reversal_weights(closes: np.ndarray) -> np.ndarray:
    """Steps 2 to 4: minus each stock's return against the market, over the priced count.

    ``n`` counts a stock priced today and not yesterday, which has no return
    and so takes no part in the market's mean, and its own weight is then set
    to 0. That is ``example3_7.m`` exactly, and it makes the weights a little
    smaller on a day a stock enters than a count of returns would.
    """
    returns = daily_returns(closes)
    market = smartmean(returns, axis=1)
    priced = smartsum(np.isfinite(closes).astype(float), axis=1)
    weights = -(returns - market[:, None]) / priced[:, None]
    weights[~np.isfinite(closes) | ~np.isfinite(lag1(closes))] = 0.0
    return weights


def daily_pnl(weights: np.ndarray, returns: np.ndarray) -> np.ndarray:
    """Step 5: yesterday's weights times today's returns, summed over stocks."""
    return smartsum(lag1(weights) * returns, axis=1)


def turnover(weights: np.ndarray) -> np.ndarray:
    """Each day's total change in weight, ``Σ|w[t] − w[t−1]|``, NaN on the first row."""
    return smartsum(np.abs(weights - lag1(weights)), axis=1)


def trading_cost(weights: np.ndarray) -> np.ndarray:
    """The cost of each day's change in weight, NaN on the array's first row."""
    return turnover(weights) * ONE_WAY_COST


def gross_held(weights: np.ndarray) -> np.ndarray:
    """The gross position each day's profit is earned on, ``Σ|w[t−1]|``."""
    return smartsum(np.abs(lag1(weights)), axis=1)


def chan_sharpe(daily: np.ndarray) -> float:
    """``sqrt(252)*smartmean(x,1)/smartstd(x,1)``, both quirks included."""
    column = daily[:, None]
    return float(np.sqrt(TRADING_DAYS) * smartmean(column, axis=0)[0] / smartstd(column, axis=0)[0])


def plain_sharpe(daily: np.ndarray) -> float:
    """``√252 · mean / std`` on a series that must hold no NaN.

    It refuses one rather than skipping it, because the figure it serves is
    the one with nothing left to skip.
    """
    if not np.isfinite(daily).all():
        raise ValueError("plain_sharpe takes a series with every day finite")
    return float(np.sqrt(TRADING_DAYS) * daily.mean() / daily.std(ddof=1))


@dataclass(frozen=True)
class Reversal:
    """What one window of the rule gives.

    ``days`` is the window's trading days. ``pnl`` is the profit before costs
    and ``pnl_after_costs`` is Chan's after-cost series, with its one NaN on
    the first day. The three figures are those the issue pins.

    1. ``before_costs``, Chan's ``sharpe``.
    2. ``after_costs``, Chan's ``sharpeminustcost``, with both quirks.
    3. ``after_costs_charged``, the same cost with the first day's rebalance
       charged from the weights before the window, so no day is NaN and
       nothing is zero-filled. Chan prints no such figure.

    The third figure's series is ``pnl_charged``. ``traded`` is each day's
    total change in weight and ``held`` the gross position the day's profit
    was earned on, both on that same specification, so the day's cost is
    ``traded · ONE_WAY_COST`` and :func:`daily_book` can set it beside the
    day's profit.
    """

    days: pd.DatetimeIndex
    pnl: np.ndarray
    pnl_after_costs: np.ndarray
    before_costs: float
    after_costs: float
    after_costs_charged: float
    pnl_charged: np.ndarray
    traded: np.ndarray
    held: np.ndarray


def reversal(frame: pd.DataFrame, *, start: str = WINDOW_START, end: str = WINDOW_END) -> Reversal:
    """Run Example 3.7 on a date-by-stock frame of closes, over ``start`` to ``end``.

    Everything up to the profit is computed on the whole frame and only then
    cut, so the window's first profit uses the weights from the day before it.
    The weights are cut before they are differenced for Chan's cost, which is
    the first quirk. The charged figure differences them before the cut.
    """
    closes = frame.to_numpy(dtype=float)
    returns = daily_returns(closes)
    weights = reversal_weights(closes)
    pnl = daily_pnl(weights, returns)

    inside = (frame.index >= pd.Timestamp(start)) & (frame.index <= pd.Timestamp(end))
    pnl = pnl[inside]
    after_costs = pnl - trading_cost(weights[inside])
    charged = pnl - trading_cost(weights)[inside]
    return Reversal(
        days=frame.index[inside],
        pnl=pnl,
        pnl_after_costs=after_costs,
        before_costs=chan_sharpe(pnl),
        after_costs=chan_sharpe(after_costs),
        after_costs_charged=plain_sharpe(charged),
        pnl_charged=charged,
        traded=turnover(weights)[inside],
        held=gross_held(weights)[inside],
    )


@dataclass(frozen=True)
class DailyBook:
    """An average day of the charged specification, per unit of the average book.

    ``book`` is the mean gross position over the window, in the units of
    Chan's weights, which he never scales. Every other field is a daily mean
    or deviation divided by that one constant, so each reads as a fraction of
    the position held. A constant divisor leaves both Sharpe ratios where they
    were, which is why it is the window's mean rather than each day's own
    position: dividing each day by its own would be the different rule the
    module docstring describes, and would move both figures.

    1. ``profit``, the mean daily profit before costs.
    2. ``cost``, the mean daily cost, first day charged.
    3. ``turnover``, the mean daily change in weight.
    4. ``swing`` and ``swing_after``, the daily standard deviation of profit
       before and after costs, dividing by n − 1 as ``plain_sharpe`` does.
    """

    book: float
    profit: float
    cost: float
    turnover: float
    swing: float
    swing_after: float

    @property
    def cost_per_profit(self) -> float:
        """How many days of average profit one day of average cost eats."""
        return self.cost / self.profit


def daily_book(result: Reversal) -> DailyBook:
    """The average day behind ``result``'s first and third figures."""
    book = float(result.held.mean())
    return DailyBook(
        book=book,
        profit=float(result.pnl.mean()) / book,
        cost=float(result.traded.mean()) * ONE_WAY_COST / book,
        turnover=float(result.traded.mean()) / book,
        swing=float(result.pnl.std(ddof=1)) / book,
        swing_after=float(result.pnl_charged.std(ddof=1)) / book,
    )


def report(members, result: Reversal) -> None:
    """Print the panel, the window, and each figure beside the book's."""
    print("Khandani and Lo's linear reversal, Chan's Example 3.7")
    print(f"  vintage  {panel_line(members)}")
    print(
        f"  window   {result.days[0].date()} to {result.days[-1].date()}, "
        f"{len(result.days)} trading days"
    )
    print(
        "  rule     weight = -(return - equal-weighted market) / stocks priced today, held one day"
    )
    print(f"  Sharpe   sqrt({TRADING_DAYS}) * mean / std, no risk-free rate")
    print()
    rows = [
        ("Before costs, Chan's rule", result.before_costs, f"{BOOK_BEFORE_COSTS:.2f}"),
        (
            f"After {ONE_WAY_COST * 1e4:.0f} bp a side, first day uncharged, NaN zero-filled",
            result.after_costs,
            f"{BOOK_AFTER_COSTS:.2f}",
        ),
        (
            f"After {ONE_WAY_COST * 1e4:.0f} bp a side, first day charged, nothing zero-filled",
            result.after_costs_charged,
            "none",
        ),
    ]
    print(f"  {'Specification':<70} {'Sharpe':>8}  {'Book':>5}")
    for label, value, book in rows:
        print(f"  {label:<70} {value:>8.4f}  {book:>5}")
    print()
    print(
        f"  Khandani and Lo report {BOOK_KHANDANI_LO:.2f} for 2006 on their own universe, "
        "which this repo does not hold."
    )
    print(
        "  The panel holds only the stocks still in the index on 2007-11-23, "
        "so every figure above is about survivors."
    )


def run(data_dir: Path | None = None) -> Reversal:
    """Read the panel, run the rule on Chan's window, and print the report."""
    members, frame = load_panel(SOURCE_FILE, data_dir=data_dir)
    result = reversal(frame)
    report(members, result)
    return result


def main() -> None:
    try:
        run()
    except VintageUnavailable as unavailable:
        # A refusal that names the source is worth nothing at the bottom of a
        # pandas traceback, so it reaches the reader as one line, the way
        # chan.kelly_leverage.main does it.
        raise SystemExit(str(unavailable)) from unavailable


if __name__ == "__main__":
    main()
