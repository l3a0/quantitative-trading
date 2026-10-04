"""Khandani and Lo's linear reversal on Chan's S&P 500 file, Examples 3.7 and 3.8.

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

**The transcription.** Every step of Example 3.7, and of Example 3.8's rule B
below, is Chan's ``example3_7.m`` and the four helpers it calls, read in the mirror
[egorpe/EPChan-QuantitativeTrading](https://github.com/egorpe/EPChan-QuantitativeTrading)
at ``1a7195003cf3e85a806e18867e0af547d17ad5c4``. The four helpers come from
:mod:`chan.matlab_helpers`, under their MATLAB names, which
[issue 18](https://github.com/l3a0/quantitative-trading/issues/18) built for
Examples 7.6 and 7.7 on the same file. This module passes them a column with
``axis=0`` or a panel with ``axis=1``, which are the shapes on which they
match the ``.m`` files.

On the full panel, before any window is cut, where ``cl`` is the close and
Example 3.8 puts the open in its place:

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
printed rather than argued. :func:`daily_book` states the third figure's
average day as a share of the position held, which is how
``blog/survivorship-and-transaction-costs.md`` explains it.

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

**Example 3.8 updates the positions at the open instead of the close.** It is
a revised-edition label, on p. 78, and the first-edition mirror has no file for
it. The book prints no figure, only that the Sharpe ratios before and after
costs are "both very positive". Chan's ``example3_8.ipynb`` prints two, and
[issue 206](https://github.com/l3a0/quantitative-trading/issues/206) carries
the reasoning behind running two rules on the opens.

1. **Rule B is the rule above with the open in place of the close**, which is
   :func:`reversal` handed the open frame. Chan's sentence calls Example 3.8
   the strategy that printed 0.25 and −3.19 with one change, so rule B carries
   his claim. It holds when both figures are at least 1.0, unrounded, his own
   line for a strategy worth trading on its own, on p. 23.
2. **Rule A is the notebook as written**, :func:`notebook_reversal`. It printed
   the published figures, 2.3818 and 1.3997 at four decimals, and its Example
   3.7 twin printed 0.9578 and −2.1617 rather than the book's 0.25 and −3.19.
   Its six departures from rule B are listed on the function.

Rule A forward-fills before taking returns, carrying each stock's last price
into a gap, so it reads WYN's gap between two companies as one day's move: a
return of 121.5 on the closes and 127.65 on the opens. That is the
transcription rather than a defect, and the report prints rule A without the
forward-fill and without WYN beside it, so a reader sees how much of Chan's
figure that gap carries.

Every result here is exploratory. Reproducing Chan's figures spends the 2006
sample on a rule somebody else chose, so the run says whether his numbers
reproduce on his file and nothing about whether the rule pays today.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from chan.matlab_helpers import lag1, smartmean, smartstd_first_edition, smartsum
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

#: Where Example 3.8's notebook was read. The book points to
#: ``example3_8.ipynb``, and six public reposts of it agree, five byte for byte.
NOTEBOOK_SOURCE = (
    "example3_8.ipynb, as reposted at pinhaocheng/epchan-quant_trading_Python_codes 5fcab61"
)
#: What Chan's notebooks print, at full precision. Example 3.7's twin first,
#: which is rule A's control on the closes, then Example 3.8.
NOTEBOOK_37_BEFORE = 0.957785681010386
NOTEBOOK_37_AFTER = -2.1617433718962276
NOTEBOOK_38_BEFORE = 2.381759409645483
NOTEBOOK_38_AFTER = 1.3996944546182997
#: How many decimals a reproduction of a notebook figure must match, the four
#: every reversal pin carries.
NOTEBOOK_DECIMALS = 4

#: The book's words for Example 3.8's two figures, p. 78.
BOOK_OPEN_CLAIM = "very positive"
#: What "very positive" must clear, both figures and unrounded. Chan's own line
#: for a strategy worth trading on its own, p. 23. The owner confirmed it on
#: issue 206 on 2026-10-02, before any figure on the opens was computed.
VERY_POSITIVE = 1.0

#: Chan's minimum-backtest estimate on p. 61: a Sharpe ratio of 1 over 681 daily
#: points gives 95 percent confidence that the true one is at least 0.
BAR_SHARPE = 1.0
BAR_POINTS = 681
#: That bar scaled to the window's 251 days, with the bar falling as one over
#: the square root of the sample. Reported, and it decides nothing.
ONE_YEAR_BAR = BAR_SHARPE * math.sqrt(BAR_POINTS / 251)

#: The symbol that holds two companies across a gap ending inside 2006, on
#: 2006-08-01. DFS holds two as well, but its gap ends in 2007.
SPLICED_SYMBOL = "WYN"


def daily_returns(prices: np.ndarray) -> np.ndarray:
    """Step 1: each stock's return on each day, NaN where either price is missing."""
    previous = lag1(prices)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (prices - previous) / previous


def reversal_weights(prices: np.ndarray) -> np.ndarray:
    """Steps 2 to 4: minus each stock's return against the market, over the priced count.

    ``n`` counts a stock priced today and not yesterday, which has no return
    and so takes no part in the market's mean, and its own weight is then set
    to 0. That is ``example3_7.m`` exactly, and it makes the weights a little
    smaller on a day a stock enters than a count of returns would.
    """
    returns = daily_returns(prices)
    market = smartmean(returns, axis=1)
    priced = smartsum(np.isfinite(prices).astype(float), axis=1)
    weights = -(returns - market[:, None]) / priced[:, None]
    weights[~np.isfinite(prices) | ~np.isfinite(lag1(prices))] = 0.0
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
    return float(
        np.sqrt(TRADING_DAYS)
        * smartmean(column, axis=0)[0]
        / smartstd_first_edition(column, axis=0)[0]
    )


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
    """Run Example 3.7's rule on a date-by-stock frame of prices, over ``start`` to ``end``.

    Handed the closes it is Example 3.7, and handed the opens it is Example
    3.8's rule B. Everything up to the profit is computed on the whole frame
    and only then cut, so the window's first profit uses the weights from the
    day before it. The weights are cut before they are differenced for Chan's
    cost, which is the first quirk. The charged figure differences them before
    the cut.
    """
    prices = frame.to_numpy(dtype=float)
    returns = daily_returns(prices)
    weights = reversal_weights(prices)
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
    were, which is why the profit and the swings divide by the window's mean
    rather than each day's own position: dividing each day by its own would be
    the different rule the module docstring describes, and would move both
    figures. The turnover takes the same divisor so that it times
    ``ONE_WAY_COST`` is exactly the cost.

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


@dataclass(frozen=True)
class NotebookReversal:
    """What one window of rule A gives, Chan's ``example3_8.ipynb`` as written.

    ``pnl`` is the profit before costs and ``pnl_after_costs`` the profit after
    them. Neither holds a NaN, because the notebook sums with ``np.nansum``.
    Rule A has no figure with a quirk removed, so this is not a
    :class:`Reversal`.
    """

    days: pd.DatetimeIndex
    pnl: np.ndarray
    pnl_after_costs: np.ndarray
    before_costs: float
    after_costs: float


def notebook_reversal(
    frame: pd.DataFrame, *, start: str = WINDOW_START, end: str = WINDOW_END, fill: bool = True
) -> NotebookReversal:
    """Rule A: the reversal as Chan's Python notebooks compute it.

    Each line transcribes a cell of ``example3_8.ipynb``, which is
    ``example3_7.ipynb`` reading the opens. Six things differ from
    :func:`reversal`, and each moves the figure.

    1. **Returns are taken after a forward-fill.** The notebook's
       ``df.pct_change()`` ran under pandas 0.24, which filled each gap with
       the last price first. A stock missing for a day earns 0 that day, and a
       gap of any length is read as one day's move. pandas 3 no longer fills
       by default, so the fill is written out. ``fill=False`` leaves it out,
       which is the variant the report prints beside it.
    2. **Each day's weights are scaled to a gross exposure of 1**, divided by
       the sum of their absolute values rather than by the count of stocks
       priced.
    3. **No stock is zeroed for a missing price.** After the fill a stock has a
       NaN return only before its first price and on that first day, and
       ``np.nansum`` skips its products. A day whose weights are all 0 stays
       at 0.
    4. **The deviation divides by n**, because the notebook calls ``np.std``.
    5. **The first day's cost is 0 rather than NaN**, because ``np.nansum`` of
       a row of NaN is 0. So neither of Example 3.7's two quirks applies.
    6. **No change in weight beside a NaN weight is charged**, because
       ``abs(w - NaN)`` is NaN and ``np.nansum`` skips it. :func:`reversal`
       holds 0 in those cells and charges the move to or from it. With the
       fill this skips the entry cost of a stock first priced inside 2006, and
       without it the cost at every gap.
    """
    prices = frame.ffill() if fill else frame
    returns_frame = prices.pct_change(fill_method=None)
    returns = returns_frame.to_numpy(dtype=float)
    market = returns_frame.mean(axis=1).to_numpy(dtype=float)
    weights = -(returns - market[:, None])
    gross = np.nansum(np.abs(weights), axis=1)
    weights[gross == 0] = 0.0
    gross[gross == 0] = 1.0
    weights = weights / gross[:, None]
    pnl = np.nansum(lag1(weights) * returns, axis=1)

    inside = (frame.index >= pd.Timestamp(start)) & (frame.index <= pd.Timestamp(end))
    pnl = pnl[inside]
    held = weights[inside]
    after_costs = pnl - np.nansum(np.abs(held - lag1(held)), axis=1) * ONE_WAY_COST
    return NotebookReversal(
        days=frame.index[inside],
        pnl=pnl,
        pnl_after_costs=after_costs,
        before_costs=_numpy_sharpe(pnl),
        after_costs=_numpy_sharpe(after_costs),
    )


def _numpy_sharpe(daily: np.ndarray) -> float:
    """``np.sqrt(252)*np.mean(x)/np.std(x)``, the notebook's ratio, dividing by n."""
    return float(np.sqrt(TRADING_DAYS) * daily.mean() / daily.std())


def matches_notebook(result: NotebookReversal, before: float, after: float) -> bool:
    """Whether both figures round to the notebook's at :data:`NOTEBOOK_DECIMALS`."""
    return round(result.before_costs, NOTEBOOK_DECIMALS) == round(
        before, NOTEBOOK_DECIMALS
    ) and round(result.after_costs, NOTEBOOK_DECIMALS) == round(after, NOTEBOOK_DECIMALS)


def claim_holds(result: Reversal) -> bool:
    """Whether "both very positive" holds: both of Chan's figures at least 1.0, unrounded."""
    return result.before_costs >= VERY_POSITIVE and result.after_costs >= VERY_POSITIVE


@dataclass(frozen=True)
class OpenVariation:
    """Example 3.8 on the opens: rule B, rule A, and rule A's two variants.

    ``rule_b`` is :func:`reversal` on the opens and carries the claim.
    ``notebook`` is :func:`notebook_reversal` and carries the published
    figures. ``unfilled`` drops the forward-fill and ``without_splice`` drops
    WYN, and neither decides anything.
    """

    rule_b: Reversal
    notebook: NotebookReversal
    unfilled: NotebookReversal
    without_splice: NotebookReversal

    @property
    def figures_reproduced(self) -> bool:
        return matches_notebook(self.notebook, NOTEBOOK_38_BEFORE, NOTEBOOK_38_AFTER)

    @property
    def claim_holds(self) -> bool:
        return claim_holds(self.rule_b)


def open_variation(frame: pd.DataFrame) -> OpenVariation:
    """Run both rules of Example 3.8 on a date-by-stock frame of opens."""
    return OpenVariation(
        rule_b=reversal(frame),
        notebook=notebook_reversal(frame),
        unfilled=notebook_reversal(frame, fill=False),
        without_splice=notebook_reversal(frame.drop(columns=[SPLICED_SYMBOL])),
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


def report_at_open(members, variation: OpenVariation) -> None:
    """Print Example 3.8: both rules, the notebook's figures, both verdicts and the bar.

    It is a report of its own rather than a branch inside :func:`report`, so
    Example 3.7's printed lines stay exactly as they were, the way
    ``chan.stationary_candidates`` gives each claim-route verdict its own report.
    """
    a, b = variation.notebook, variation.rule_b
    cost = f"{ONE_WAY_COST * 1e4:.0f} bp a side"
    print("Khandani and Lo's linear reversal at the open, Chan's Example 3.8 (revised edition)")
    print(f"  vintage  {panel_line(members)}, the Open column")
    print(
        f"  window   {b.days[0].date()} to {b.days[-1].date()}, "
        f"{len(b.days)} trading days, positions updated at the open"
    )
    print(f"  Sharpe   sqrt({TRADING_DAYS}) * mean / std, no risk-free rate")
    print()
    print(f"Rule A, Chan's notebook as written: {NOTEBOOK_SOURCE}")
    print("  returns after a forward-fill, weights scaled to a gross exposure of 1, std over n")
    print(f"  {'Specification':<62} {'Sharpe':>8}  {'Notebook':>8}")
    rows_a = [
        ("Before costs", a.before_costs, f"{NOTEBOOK_38_BEFORE:.4f}"),
        (f"After {cost}", a.after_costs, f"{NOTEBOOK_38_AFTER:.4f}"),
        ("Before costs, no forward-fill", variation.unfilled.before_costs, "none"),
        (f"After {cost}, no forward-fill", variation.unfilled.after_costs, "none"),
        (f"Before costs, without {SPLICED_SYMBOL}", variation.without_splice.before_costs, "none"),
        (f"After {cost}, without {SPLICED_SYMBOL}", variation.without_splice.after_costs, "none"),
    ]
    for label, value, book in rows_a:
        print(f"  {label:<62} {value:>8.4f}  {book:>8}")
    word = "REPRODUCED" if variation.figures_reproduced else "DID NOT REPRODUCE"
    print(
        f"  Verdict: {word}. Both figures must round to the notebook's at "
        f"{NOTEBOOK_DECIMALS} decimals."
    )
    print(
        f"  The four rows without a notebook figure show what the forward-fill and "
        f"{SPLICED_SYMBOL}'s gap between two companies carry, and decide nothing."
    )
    print()
    print("Rule B, Example 3.7's MATLAB with the open in place of the close")
    print(f"  {'Specification':<62} {'Sharpe':>8}  {'Book':>13}")
    rows_b = [
        ("Before costs, Chan's rule", b.before_costs, BOOK_OPEN_CLAIM),
        (f"After {cost}, first day uncharged, NaN zero-filled", b.after_costs, BOOK_OPEN_CLAIM),
        (f"After {cost}, first day charged, nothing zero-filled", b.after_costs_charged, "none"),
    ]
    for label, value, book in rows_b:
        print(f"  {label:<62} {value:>8.4f}  {book:>13}")
    halves = (("Before costs", b.before_costs), ("After costs", b.after_costs))
    cleared = [half for half, value in halves if value >= VERY_POSITIVE]
    line = f"{VERY_POSITIVE:.1f}"
    if variation.claim_holds:
        verdict = "HOLDS"
    elif cleared:
        verdict = f"DOES NOT HOLD. {cleared[0]} clears {line} and the other half does not"
    else:
        verdict = f"DOES NOT HOLD. Neither half clears {line}"
    print(
        f'  Claim, "both {BOOK_OPEN_CLAIM}": {verdict}. Both figures must be at least '
        f"{VERY_POSITIVE:.1f}, unrounded, declared before any figure on the opens was computed."
    )
    print()
    figures = {
        "rule A before costs": a.before_costs,
        "rule A after costs": a.after_costs,
        "rule B before costs": b.before_costs,
        "rule B after costs": b.after_costs,
    }
    clearing = [name for name, value in figures.items() if value >= ONE_YEAR_BAR]
    print(
        f"  One-year bar {ONE_YEAR_BAR:.4f}, Chan's {BAR_SHARPE:.0f} over {BAR_POINTS} days "
        f"scaled to {len(b.days)}. Decides nothing. Clearing it: {', '.join(clearing) or 'none'}."
    )
    print(
        "  The panel holds only the stocks still in the index on 2007-11-23, "
        "so every figure above is about survivors."
    )
    print(
        "  Exploratory. Reproducing Chan's figures spends the 2006 sample on a rule somebody "
        "else chose, so this says whether"
    )
    print(
        "  his numbers reproduce on his file and nothing about whether trading at the open "
        "pays. docs/replication-log.md Entry 10 carries the verdicts."
    )


def run(data_dir: Path | None = None, *, at_open: bool = False) -> Reversal | OpenVariation:
    """Read the panel, run Chan's window, and print the report.

    ``at_open`` reads the opens and runs Example 3.8. A boolean rather than a
    field name, because ``load_panel`` accepts any of five fields and only the
    close and the open have an example behind them.
    """
    if at_open:
        members, frame = load_panel(SOURCE_FILE, field="Open", data_dir=data_dir)
        variation = open_variation(frame)
        report_at_open(members, variation)
        return variation
    members, frame = load_panel(SOURCE_FILE, data_dir=data_dir)
    result = reversal(frame)
    report(members, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Khandani and Lo's linear reversal on Chan's S&P 500 file, Example 3.7, "
        "or Example 3.8 at the open"
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="update the positions at the open, Example 3.8 in the revised edition",
    )
    args = parser.parse_args()
    try:
        run(at_open=args.open)
    except VintageUnavailable as unavailable:
        # A refusal that names the source is worth nothing at the bottom of a
        # pandas traceback, so it reaches the reader as one line, the way
        # chan.kelly_leverage.main does it.
        raise SystemExit(str(unavailable)) from unavailable


if __name__ == "__main__":
    main()
