"""VX against ES on VX's roll return, *Algorithmic Trading*'s trade after Simon and Campasano.

A VX future converges on the VIX index as it nears settlement, so when the
front contract sits well above VIX it tends to fall toward it, and when it
sits well below it tends to rise. That convergence is VX's roll return.
Volatility rises when the stock market falls, so an E-mini S&P 500 future,
ES, held the same way as the VX leg hedges most of the market's move. Every
location below is in ``research/book-notes/algorithmic-trading.md``.

1. **Location 2747** says no ETF holds VIX, because a basket of options
   replicating it is too expensive to keep, and that ES, whose roll return is
   about 1 percent a year, can stand in for a series that moves against it.
2. **Location 2754** gives the rule, after Simon and Campasano (2012). If the
   front VX contract is above VIX by 0.1 point times the trading days left to
   settlement, "short 0.3906 front contracts of VX and short 1 front contract
   of ES. Hold for one day." If it is below by that much, buy both. "The
   settlement is the day after the contracts expire." It then gives the
   result. "The APR for July 29, 2010, to May 7, 2012 (this period was not
   used for hedge ratio determination) is 6.9 percent, with a Sharpe ratio of
   1." Figure 6.4 draws its cumulative return.

**What ``VX_ES_rollreturn.m`` holds.** The script is git blob ``849e0ac``
under ``public/img/book2/`` in the mirror
[ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) at
``e4bc46f``, and the line numbers below are that blob's. It carries two
position rules, and its closing comment prints four figures for each.

1. **Hedge 0.3906**, lines 47 and 55, commented out. Its comment, lines 81 to
   82, prints an APR of 0.069065, a Sharpe ratio of 1.002020, a maximum
   drawdown of −0.075683 and a longest drawdown of 259 days. The book's 6.9
   percent and Sharpe ratio of 1 come from this rule.
2. **Hedge [1, 1]**, lines 48 to 49 and 56 to 57, the live lines. One VX
   contract per ES contract. Its comment, lines 86 to 88, prints 0.293906,
   3.263952, −0.035798 and 59.

The run takes both, with the hedge as the one argument that differs. It
trades the printed 0.3906 rather than the hedge :mod:`chan.vx_es` fits,
0.390594, because the fitted hedge misses the script's sixth decimal on
both the APR and the Sharpe ratio, which :func:`run` prints beside the rest.

**The transcription.** Six steps, each mapped to the function that runs it.

1. The script loads the VX strip, then ``VIX.csv``'s last column, then ES
   from ``inputDataOHLCDaily_20120507``. :func:`read_sources` does it through
   the guarded read paths below.
2. ``intersect`` keeps VIX's days that the strip holds, then the ones ES
   holds too. :func:`common_days` does it in that order.
3. A contract's expiry is its last priced row on that calendar, and each
   contract is the front from 40 to 10 rows before it, starting no earlier
   than the row after the previous front ended. This is the loop
   ``XLE_CL_rollReturn.m`` runs, and
   :func:`chan.xle_uso_roll_return.front_windows` carries it for both.
4. On each front row, line 46 divides ``VX − VIX`` by
   ``expireIdx − idx + 1``, the trading days to settlement. Above
   :data:`ENTRY_THRESHOLD` the position is short the front VX and short ES,
   below its negative it is long both, and otherwise it is flat. The VX leg
   holds ``hedge`` contracts and the ES leg one. :func:`positions` sets them.
5. Line 68 earns each day's dollar profit on yesterday's positions over
   yesterday's gross market value, on ``y = [1000·VX, 50·ES]``, less
   :data:`ONE_WAY_COST` of the day's change in market value over the same
   gross, with NaN set to 0. :func:`daily_returns` earns it, with
   :func:`chan.matlab_helpers.backshift` for ``lag`` and
   :func:`chan.matlab_helpers.smartsum` for ``smartsum``.
6. The figures are taken over rows 501 onward of the days on or after
   :data:`chan.vx_es.ANCHOR`, the test, 2010-07-29 to 2012-05-07. The APR is
   :func:`chan.khandani_lo_book_two.compounded_apr`. Line 77's
   ``sqrt(252)*mean(r)/std(r)`` divides by n − 1, which is
   :func:`chan.khandani_lo.plain_sharpe` exactly. The drawdowns are
   :func:`chan.matlab_helpers.calculate_max_dd` on ``cumprod(1 + r) − 1``.

**Two quirks the run keeps.** Both are measured on these files, and the
transcription names them rather than copying them silently.

1. **An entry from flat is free.** On the day a position opens from nothing,
   yesterday's gross is 0, so the day's return is NaN and set to 0, and line
   68 never charges the entry's cost. It charges a held day on its
   mark-to-market move as well as on any trade, because it takes the change
   in ``positions·y`` rather than in ``positions``. The test holds 32 entries
   from flat.
2. **The file's last day reads as an expiry.** Eight contracts are priced on
   2012-05-07, the strip's last row, so each reads as expiring there.
   VX-2012K's window ends on 2012-04-23, its days to settlement count to
   2012-05-07 rather than to its real expiry, and the test's last 10 rows
   hold nothing. The loop stops one short of the last contract, VX-2012Z, so
   it reads 71 of the 72. The six between VX-2012K and VX-2012Z get windows
   that hold no row, so 65 of the 71 hold a row.

**The data.** Four committed vintages. The trade reads the first three, and
the fitted hedge beside it reads the fourth.

1. **The VX strip** from ``inputDataDaily_VX_20120507.mat``, vendor
   chan-mat, basis ``raw``, saved 2012-05-08, 72 contracts from VX-2007F
   over 1,543 days from 2006-03-23 to 2012-05-07, with no spot column.
2. **VIX** from ``VIX.csv``, vendor chan-csv, basis ``raw``, saved
   2012-05-09, 5,635 rows from 1990-01-02 to 2012-05-08. The script reads its
   last column, ``Adj Close``, which equals ``Close`` on every row, and the
   reader refuses a file where the two differ.
3. **ES** from ``inputDataOHLCDaily_20120507.mat``, vendor chan-mat, basis
   ``adjusted``, saved 2012-05-09, 2,000 rows from 2004-06-02 to 2012-05-08.
   ES was rewritten between saves, so this save is part of the
   specification.
4. **VX's continuous close** from the same 2012-05-07 save as ES, vendor
   chan-mat, basis ``adjusted``, saved 2012-05-09, 2,000 rows from 2004-06-01
   to 2012-05-08. :func:`fitted_hedge` reads it with ES through
   :func:`chan.vx_es.read_legs` to fit the hedge the log's row 11 trades in
   place of 0.3906. No figure under 0.3906 or [1, 1] reads it.

The trade's three calendars share all 1,543 of the strip's days, so every expiry is
the strip's own. 2008-08-04 is the first of 948 days from the anchor.

**The scale-break guard.** The strip is read through
:func:`chan.roll_returns.load_strip`, which guards every contract over its
own rows. The run guards ES over its own span in the 2012-05-07 save, as
:func:`chan.vx_es.read_legs` does, and guards VIX from the anchor to the last
common day, 2008-08-04 to 2012-05-07, the span the script's ``idx`` measures
from. VIX flags 2007-02-27, a real move from 11.15 to 18.31, so a guard over
the whole common span would refuse. That day sets a long position, but no
figure reads it. A position reads only its own day's VIX, and the first test
return earns the position held at the close of 2010-07-28. Nothing flags
over the guarded spans, so nothing is refused. :func:`chan.vx_es.read_legs`
guards VX's continuous close and ES over their whole spans for the fitted
hedge, and :func:`run` fits that hedge before it prints, so a break in either
refuses the whole run. Neither flags a day.

**What the post reads.** :func:`front_roll` is line 46's roll on its own,
and :func:`positions` signs the rule from it, so the figure that
:mod:`chan.vx_es_roll_return_figures` draws and the rule read one
computation. :func:`leg_returns` splits each day's return into the VX legs'
profit, ES's profit and the cost, each over the same gross, for the post's
fifth lesson. Neither changes a figure the run prints.

``tests/test_vx_es_roll_return.py`` pins every figure. Every result here is
exploratory. Reproducing Chan's figures spends his 2008 to 2012 sample on a
rule Simon and Campasano proposed and a hedge he chose, so the run says
whether his numbers reproduce on his files and nothing about whether the
trade pays out of sample.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray

from chan.khandani_lo import TRADING_DAYS, plain_sharpe
from chan.khandani_lo_book_two import compounded_apr, gap, matches
from chan.matlab_helpers import backshift, calculate_max_dd, smartsum
from chan.roll_returns import Strip, load_strip
from chan.series import (
    WindowCrossesScaleBreak,
    load_panel,
    panel_line,
    refuse_window_crossing_a_break,
    vintage_line,
)
from chan.vintage import VintageEntry, VintageUnavailable
from chan.vx_es import (
    ANCHOR,
    BOOK_HEDGE,
    ES,
    ES_POINT_VALUE,
    SOURCE_FILE,
    TRAINING_DAYS,
    VX,
    VX_POINT_VALUE,
    anchored,
    fit_hedge,
    read_legs,
)
from chan.xle_uso_roll_return import front_windows

#: The strip the script's first load line reads.
ROOT = "VX"
#: The index file line 7 reads.
VIX_FILE = "VIX.csv"
VIX = "VIX"

#: ``entryThreshold``, in VIX points per trading day to settlement.
ENTRY_THRESHOLD = 0.1
#: ``onewaytcost``, one basis point of each day's change in market value.
ONE_WAY_COST = 1 / 10000

#: The VX contracts per ES contract of lines 47 and 55, the book's 0.3906.
HEDGE = float(BOOK_HEDGE)
#: The live lines, 48 to 49 and 56 to 57, one VX contract per ES contract.
SHIPPED_HEDGE = 1.0


@dataclass(frozen=True)
class Printed:
    """The four figures one of the script's comment blocks prints, as printed."""

    apr: str
    sharpe: str
    max_drawdown: str
    max_drawdown_days: str


#: Lines 81 to 82, the 0.3906 rule.
HEDGED_COMMENT = Printed("0.069065", "1.002020", "-0.075683", "259")
#: Lines 86 to 88, the [1, 1] rule.
SHIPPED_COMMENT = Printed("0.293906", "3.263952", "-0.035798", "59")
#: What location 2754 prints, "6.9 percent" and "a Sharpe ratio of 1".
BOOK_APR_PERCENT = "6.9"
BOOK_SHARPE = "1"


@dataclass(frozen=True)
class Sources:
    """The trade's three reads, each a vintage and its series.

    The fitted hedge's read of VX's continuous close is the fourth, and
    :func:`fitted_hedge` takes it.
    """

    strip: Strip
    vix_member: VintageEntry
    vix: pd.Series
    es_member: VintageEntry
    es: pd.Series


@dataclass(frozen=True)
class RollReturnTrade:
    """One position rule over every common day, and its figures over the test.

    ``positions`` holds one column per contract in the strip's order and ES's
    last, as the script's ``positions`` does. ``daily`` holds every common
    day's return, and ``test`` the rows the figures read.
    """

    hedge: float
    days: pd.DatetimeIndex
    positions: NDArray[np.float64]
    daily: NDArray[np.float64]
    test: NDArray[np.intp]

    @property
    def test_days(self) -> pd.DatetimeIndex:
        return self.days[self.test]

    @property
    def test_daily(self) -> NDArray[np.float64]:
        return self.daily[self.test]

    @property
    def apr(self) -> float:
        return compounded_apr(self.test_daily)

    @property
    def sharpe(self) -> float:
        return plain_sharpe(self.test_daily)

    @property
    def max_drawdown(self) -> float:
        return calculate_max_dd(np.cumprod(1 + self.test_daily) - 1)[0]

    @property
    def max_drawdown_days(self) -> int:
        return calculate_max_dd(np.cumprod(1 + self.test_daily) - 1)[1]

    @property
    def es_leg(self) -> NDArray[np.float64]:
        """The ES column, −1 short, +1 long and 0 flat, which signs every held row."""
        return self.positions[:, -1]

    @property
    def entries_from_flat(self) -> NDArray[np.bool_]:
        """The rows holding something after a row that held nothing."""
        held = (self.positions != 0).any(axis=1)
        return held & ~np.append(False, held[:-1])


def common_days(contracts: pd.DataFrame, vix: pd.Series, es: pd.Series) -> pd.DatetimeIndex:
    """VIX's days the strip holds, then the ones ES holds too, in the script's order."""
    days = vix.index.intersection(contracts.index)
    return days.intersection(es.index).sort_values()


def front_roll(contracts: pd.DataFrame, vix: ArrayLike) -> pd.Series:
    """Line 46's roll, ``(VX − VIX) / (expiry − row + 1)``, on each front row and NaN elsewhere.

    ``contracts`` and ``vix`` run over the same days. The front rows are the
    ones :func:`chan.xle_uso_roll_return.front_windows` gives, and the divisor
    is the trading days to settlement, counting the expiry row itself.
    :func:`positions` signs the rule from this series, and
    :mod:`chan.vx_es_roll_return_figures` draws it, so the two share one
    computation.
    """
    prices = contracts.to_numpy(dtype=float)
    vix = np.asarray(vix, dtype=float)
    roll = np.full(len(prices), np.nan)
    for window in front_windows(contracts):
        rows = window.rows
        roll[rows] = (prices[rows, window.column] - vix[rows]) / (window.expiry - rows + 1)
    return pd.Series(roll, index=contracts.index, name="front_roll")


def positions(
    contracts: pd.DataFrame, vix: NDArray[np.float64], hedge: float
) -> NDArray[np.float64]:
    """Steps 3 and 4: one row per day, a column per contract and ES's last.

    ``contracts`` and ``vix`` run over the same days. On each front row the
    roll is :func:`front_roll`'s. Above :data:`ENTRY_THRESHOLD` the front
    holds ``−hedge`` and ES −1, below its negative ``hedge`` and +1, and
    otherwise nothing. A NaN roll holds nothing.
    """
    roll = front_roll(contracts, vix).to_numpy()
    held = np.zeros((len(roll), contracts.shape[1] + 1))
    for window in front_windows(contracts):
        rows = window.rows
        with np.errstate(invalid="ignore"):
            short = rows[roll[rows] > ENTRY_THRESHOLD]
            long = rows[roll[rows] < -ENTRY_THRESHOLD]
        held[short, window.column] = -hedge
        held[short, -1] = -1
        held[long, window.column] = hedge
        held[long, -1] = 1
    return held


def market_values(contracts: pd.DataFrame, es: NDArray[np.float64]) -> NDArray[np.float64]:
    """``y = [VX·1000 ES·50]``, one contract of each in dollars, in :func:`positions`' columns."""
    return np.column_stack(
        [VX_POINT_VALUE * contracts.to_numpy(dtype=float), ES_POINT_VALUE * np.asarray(es, float)]
    )


def daily_returns(held: NDArray[np.float64], values: NDArray[np.float64]) -> NDArray[np.float64]:
    """Step 5: yesterday's dollar profit over yesterday's gross, less the cost, NaN set to 0.

    The cost is :data:`ONE_WAY_COST` of the day's change in ``held·values``
    summed over the columns, over the same gross. A row after a flat row
    divides by a gross of 0, so it is NaN and earns 0, cost and all.
    """
    value = held * values
    yesterday = backshift(1, value)
    gross = smartsum(np.abs(yesterday), axis=1)
    profit = smartsum(backshift(1, held) * (values - backshift(1, values)), axis=1)
    traded = smartsum(np.abs(value - yesterday), axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        ret = profit / gross - ONE_WAY_COST * traded / gross
    return np.where(np.isnan(ret), 0.0, ret)


@dataclass(frozen=True)
class LegReturns:
    """Each row's return split three ways, each over yesterday's gross market value.

    ``vx`` is the dollar profit of every VX column, ``es`` that of the ES
    column, and ``cost`` the :data:`ONE_WAY_COST` :func:`daily_returns`
    subtracts. All three are 0 on a row whose yesterday held nothing, so
    ``vx + es − cost`` is :func:`daily_returns` on every row.
    """

    vx: NDArray[np.float64]
    es: NDArray[np.float64]
    cost: NDArray[np.float64]


def leg_returns(held: NDArray[np.float64], values: NDArray[np.float64]) -> LegReturns:
    """:func:`daily_returns` split into the VX legs' profit, ES's profit and the cost.

    Each part divides by the same gross :func:`daily_returns` does, with
    ``smartsum`` skipping a NaN the same way, and is 0 where that gross is 0.
    """
    yesterday = backshift(1, held * values)
    gross = smartsum(np.abs(yesterday), axis=1)
    pnl = backshift(1, held) * (values - backshift(1, values))
    traded = smartsum(np.abs(held * values - yesterday), axis=1)

    def over_gross(dollars: NDArray[np.float64]) -> NDArray[np.float64]:
        # A gross of 0 gives NaN on the legs and +inf on an entry's cost.
        # Both earn 0, as daily_returns' NaN does.
        with np.errstate(invalid="ignore", divide="ignore"):
            share = dollars / gross
        return np.where(np.isfinite(share), share, 0.0)

    return LegReturns(
        vx=over_gross(smartsum(pnl[:, :-1], axis=1)),
        es=over_gross(smartsum(pnl[:, -1:], axis=1)),
        cost=over_gross(ONE_WAY_COST * traded),
    )


def measured_rows(days: pd.DatetimeIndex) -> NDArray[np.intp]:
    """``idx(501:end)`` with ``idx=find(tday >= 20080804)``: the rows after the 500 that trained."""
    return np.flatnonzero(days >= ANCHOR)[TRAINING_DAYS:]


def roll_return_trade(sources: Sources, hedge: float) -> RollReturnTrade:
    """Steps 2 to 6 for one hedge."""
    days = common_days(sources.strip.contracts, sources.vix, sources.es)
    contracts = sources.strip.contracts.loc[days]
    held = positions(contracts, sources.vix.loc[days].to_numpy(dtype=float), hedge)
    values = market_values(contracts, sources.es.loc[days].to_numpy(dtype=float))
    return RollReturnTrade(
        hedge=hedge,
        days=days,
        positions=held,
        daily=daily_returns(held, values),
        test=measured_rows(days),
    )


def read_sources(data_dir: Path | None = None) -> Sources:
    """The strip, VIX and ES, each through the guard the module docstring names."""
    strip = load_strip(ROOT, data_dir)
    vix_members, vix_panel = load_panel(VIX_FILE, data_dir=data_dir)
    vix_member = next(m for m in vix_members if m.symbol == VIX)
    vix = vix_panel[VIX]
    es_members, es_panel = load_panel(SOURCE_FILE, data_dir=data_dir)
    es_member = next(m for m in es_members if m.symbol == ES)
    es = es_panel[ES].dropna()
    refuse_window_crossing_a_break([(es_member, es)], start=es.index[0], end=es.index[-1])
    days = common_days(strip.contracts, vix, es)
    refuse_window_crossing_a_break([(vix_member, vix)], start=ANCHOR, end=days[-1])
    return Sources(strip=strip, vix_member=vix_member, vix=vix, es_member=es_member, es=es)


def fitted_hedge(data_dir: Path | None = None) -> tuple[VintageEntry, float]:
    """:mod:`chan.vx_es`'s hedge on the same 500 rows from the anchor, for the row beside.

    It returns VX's continuous close's vintage with the hedge.
    :func:`chan.vx_es.read_legs` guards that series and ES over their whole
    spans, so a break in either refuses here.
    """
    members, legs = read_legs(SOURCE_FILE, data_dir)
    vx_member = next(m for m in members if m.symbol == VX)
    return vx_member, fit_hedge(anchored(legs).iloc[:TRAINING_DAYS]).hedge


def _verdict(value: float, printed: str) -> str:
    return "reproduced" if matches(value, printed) else f"gap {gap(value, printed):+g}"


def _figures(trade: RollReturnTrade) -> tuple[float, float, float, int]:
    return trade.apr, trade.sharpe, trade.max_drawdown, trade.max_drawdown_days


def report(
    sources: Sources,
    hedged: RollReturnTrade,
    shipped: RollReturnTrade,
    fitted: RollReturnTrade,
    fitted_member: VintageEntry,
) -> None:
    """Print the vintages, both rules beside their comments, the text's two, and the counts.

    ``fitted_member`` is the vintage of VX's continuous close, which only the
    fitted hedge reads.
    """
    days, test = hedged.days, hedged.test_days
    print("VX against ES on VX's roll return, Algorithmic Trading location 2754")
    print(f"  strip     {panel_line(sources.strip.members)}")
    print(f"  vintage   {vintage_line(sources.vix_member)}")
    print(f"  vintage   {vintage_line(sources.es_member)}")
    print(f"  vintage   {vintage_line(fitted_member)}, for the fitted hedge alone")
    print(f"  calendar  {days[0].date()} to {days[-1].date()}, {len(days)} days all three hold")
    print(f"  test      {test[0].date()} to {test[-1].date()}, {len(test)} days")
    print(
        f"  rule      (VX − VIX) over the days to settlement on the front, above "
        f"{ENTRY_THRESHOLD} short both legs,"
    )
    print(f"            below −{ENTRY_THRESHOLD} long both, one basis point a side.")
    print()
    print(f"  {'Figure':<24} {'Computed':>10}  {'Script':>9}  Verdict")
    for label, trade, printed in (
        (f"Hedge {BOOK_HEDGE}, lines 81 to 82", hedged, HEDGED_COMMENT),
        ("Hedge [1, 1], lines 86 to 88", shipped, SHIPPED_COMMENT),
    ):
        print(f"  {label}")
        apr, sharpe, drawdown, drawdown_days = _figures(trade)
        for name, value, string in (
            ("APR", apr, printed.apr),
            ("Sharpe ratio", sharpe, printed.sharpe),
            ("Maximum drawdown", drawdown, printed.max_drawdown),
        ):
            print(f"    {name:<22} {value:>10.6f}  {string:>9}  {_verdict(value, string)}")
        print(
            f"    {'Longest drawdown, days':<22} {drawdown_days:>10d}  "
            f"{printed.max_drawdown_days:>9}  {_verdict(drawdown_days, printed.max_drawdown_days)}"
        )
    print()
    print(f"  {'Book, location 2754':<24} {'Computed':>10}  {'Book':>9}  Verdict")
    for label, value, printed in (
        ("APR, percent", 100 * hedged.apr, BOOK_APR_PERCENT),
        ("Sharpe ratio", hedged.sharpe, BOOK_SHARPE),
    ):
        print(f"    {label:<22} {value:>10.6f}  {printed:>9}  {_verdict(value, printed)}")
    print()
    print("Beside the replication, with no verdict.")
    print(
        f"  The fitted hedge {fitted.hedge:.6f}: APR {fitted.apr:.6f} against "
        f"{HEDGED_COMMENT.apr}, Sharpe ratio {fitted.sharpe:.6f} against {HEDGED_COMMENT.sharpe}"
    )
    print()
    leg = hedged.es_leg[hedged.test]
    entries = int(hedged.entries_from_flat[hedged.test].sum())
    print(
        f"  test      held on {int((leg != 0).sum())} days, short on {int((leg < 0).sum())}, "
        f"long on {int((leg > 0).sum())}, {entries} entries from flat, each free"
    )
    print(
        f"  Annualised over {TRADING_DAYS} days. The Sharpe ratio divides by n − 1, "
        "with no risk-free rate."
    )
    print("  Exploratory. docs/replication-log.md carries the verdicts.")


def run(data_dir: Path | None = None) -> tuple[RollReturnTrade, RollReturnTrade]:
    """Read the trade's three vintages and the fitted hedge's fourth, run both rules, and print."""
    sources = read_sources(data_dir)
    hedged = roll_return_trade(sources, HEDGE)
    shipped = roll_return_trade(sources, SHIPPED_HEDGE)
    fitted_member, hedge = fitted_hedge(data_dir)
    fitted = roll_return_trade(sources, hedge)
    report(sources, hedged, shipped, fitted, fitted_member)
    return hedged, shipped


def main() -> None:
    argparse.ArgumentParser(
        description="VX against ES on VX's roll return, Algorithmic Trading location 2754"
    ).parse_args()
    try:
        run()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day reaches the reader
        # as one line, the way chan.price_spread.main does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
