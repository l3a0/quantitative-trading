"""Chan's two equity seasonals, Examples 7.6 and 7.7, on his files and on IJR's members.

Chan publishes both strategies as already dead. At Kindle location 4425 he says
the Heston and Sadka strategy returned more than 13 percent a year before 2002
and "has disappeared since then". Example 7.6 trades the January effect, and
location 766 says a reader's backtest of it failed and Chan's own confirmed the
failure. So reproducing these checks whether a documented disappearance is
visible in data a reader can get, rather than whether a published edge
survives.

**Example 7.6, the January effect.** At each December year-end, rank the
S&P 600 small caps on their calendar-year return. Buy the worst tenth and short
the best tenth at that close, and close both at the last close of January. The
return is half the losers' mean January return less half the winners', less
two one-way costs of 5 basis points.

**Example 7.7, Heston and Sadka.** At each S&P 500 month-end, rank the stocks on
their return in the month that comes a year before the month about to be
held. Buy the best tenth and short the worst tenth for that month.

The book prints each example in up to three languages, and the editions differ.
:data:`JANUARY_RULES` and :data:`HESTON_SADKA_RULES` hold one entry per
printout, each naming what that printout's script does. A builder who writes
the strategy from its description will not land on them, and
[issue 18](https://github.com/l3a0/quantitative-trading/issues/18) records the
second figure each rule produces when it is changed.

Four sources, all of them Chan's.

1. The first edition's MATLAB, from the mirror at
   [egorpe/EPChan-QuantitativeTrading](https://github.com/egorpe/EPChan-QuantitativeTrading)
   at ``1a71950``: ``example7_6.m`` and ``example7_7.m``.
2. The revised edition's Python, from
   [liujiantong/epchan_books](https://github.com/liujiantong/epchan_books) at
   ``653cf92``: ``example7_6.py`` and ``example7_7.py``. The owner checked
   their printed figures against the revised Kindle edition on 2026-10-02 and
   all five match.
3. The revised edition's MATLAB, printed on p. 179 of the revised Kindle
   edition. The owner read its figures on 2026-10-02 and its code on
   2026-10-03, and
   [issue 226](https://github.com/l3a0/quantitative-trading/issues/226) quotes
   the expressions that decide each rule. :data:`REVISED_MATLAB` is that code
   with one repair, which its comment names. The revised edition's code as
   reposted at pinhaocheng/epchan-quant_trading_MATLAB_codes ``7430b84``
   already carries the repair, in ``example7_7.m``, and ships book two's
   ``smartstd.m``.
4. The revised edition's R, printed on p. 181 and read the same way.
   :data:`R_HESTON_SADKA` follows it with no change.

Both editions' MATLAB and the revised R print the same three Example 7.6
returns, so the rules for those are the first edition's, with R's rounding
taken from its Example 7.7 code.

Example 7.6 reads ``IJR_20080131.mat``, the file Chan's script loads. The
mirror does not hold it, so it comes from the revised edition's code as
reposted at pinhaocheng/epchan-quant_trading_MATLAB_codes ``7430b84``, and
``data/README.md`` says why that copy is trusted. Its last row is 2008-02-01,
and that row is what makes 2008-01-31 a January month-end under every
printout's rules, so the third holding needs it.
[Issue 225](https://github.com/l3a0/quantitative-trading/issues/225) committed
it, and the earlier save, ``IJR_20080114.mat``, gives the first two holdings
to the same digits.

Two limits, each stated where it applies.

1. Both files hold only the companies in their index on the day Chan saved
   them, carried backwards. Whatever these files show about a disappearance,
   they show it about survivors.
   [Issue 196](https://github.com/l3a0/quantitative-trading/issues/196) is
   where Example 7.7 is tested on the rest, and the point-in-time run below
   is where Example 7.6 is.
2. The 2002 split of the revised Python is exploratory. It was computed before
   any criterion for "disappeared" was written down, so it carries no verdict.

P. 180's claim that the most recent five years do even worse is the one
verdict here on timing. Its criterion was written on
[issue 254](https://github.com/l3a0/quantitative-trading/issues/254) before
any five-year figure was computed, and :class:`FiveYearCheck` says what it
reads. The claim holds on this file, and the first limit above still applies
to it.

The scale-break guard is not applied. :func:`chan.series.load_panel` does not
call ``refuse_window_crossing_a_break``, so a run reading a panel applies the
guard only by calling it itself. The
comment above ``FLAGGED_IN_CHANS_MAT_FILES`` in ``tests/test_scale_breaks.py``
says why for these files.

**Example 7.6 on IJR's members at 2025-12-31.**
[Issue 333](https://github.com/l3a0/quantitative-trading/issues/333) runs
:data:`MATLAB_JANUARY` unchanged over January 2009 to January 2026, on the 603
companies IJR held at 2025-12-31, carried back to 2007. It reads two more
sources than the replications do.

1. The member list, ``research/filings/ijr/2025-12-31.csv``, which
   :mod:`chan.fund_holdings` reads from IJR's Form N-PORT, accession
   ``0000940400-26-007526``, through its member rule.
   :data:`ALPHAVANTAGE_SYMBOLS` takes eleven of its tickers to the symbols
   Alpha Vantage files them under.
2. Alpha Vantage's adjusted daily closes for those symbols, recorded as the
   ``sp600`` cross-section in ``data/archive_vintages.jsonl``, with the bytes
   in the owner's archive. :func:`chan.archive.read_cross_section` reads them.

The committed raw SPY vintage downloaded on 2026-10-03 is the run's calendar.

That run is survivor-only, and it is read in one direction only. Companies
that left the index before 2025-12-31 are missing, and on this strategy both
legs gain from their absence, so the data lean toward finding a January
effect. A January mean not detectably above zero bounds the effect even so,
at the mean the test detects with 80% probability. One that is above zero
gives no verdict, because the bias alone could produce it. The rule was
written on the issue before any return was computed, and
:func:`survivor_reading` words it.

**Example 7.6 on the S&P 600 as it stood at each year-end.**
[Issue 329](https://github.com/l3a0/quantitative-trading/issues/329) runs the
same Januaries on the members IJR held at each year-end from 2008 to 2025, so
the companies that left the index are in it. It reads two sources.

1. The members file, ``research/filings/ijr/members.csv``, which
   :mod:`chan.sp600_panel` reads. For each member of each year-end filing it
   names an Alpha Vantage ticker and whether the series' raw close agrees with
   the filing.
   [Issue 332](https://github.com/l3a0/quantitative-trading/issues/332) built
   it, and :func:`chan.fund_panel.coverage` says which members it covers.
2. The adjusted closes of the ``sp600`` lines those tickers name, with the
   bytes in the owner's archive, and the same SPY calendar as the survivor
   run.

Each year-end ranks only its covered members, one year-end at a time, because
:func:`january_effect` reads no membership. The tenth is taken of the ranked
covered members plus every missing member, through ``universe``. A missing
member that could change a tenth is flagged from the filings alone by
:func:`chan.fund_panel.threat_sides`, and a January with any flag is bounded
by :func:`bounded_january`. Each series takes the one-sided test, and
:func:`point_in_time_verdict` words the outcome. The claim, the test, the bound
and the wording were written on the issue before any return was computed, so
the result is labelled registered.

``tests/test_equity_seasonals.py`` is the single authority for every number
any prose surface quotes about either example.

Usage:
    python -m chan.equity_seasonals
    python -m chan.equity_seasonals --survivors
    python -m chan.equity_seasonals --point-in-time
"""

from __future__ import annotations

import argparse
import math
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from scipy import optimize, stats

from chan import sp600_panel
from chan.archive import ArchiveEntry, ArchiveRefused, ArchiveUnavailable, read_cross_section
from chan.fund_holdings import IJR, Filing, members
from chan.fund_panel import (
    SIDES,
    Coverage,
    MemberRow,
    PanelRefused,
    coverage,
    exit_date,
    price_date,
    threat_sides,
    year_end_returns,
)
from chan.matlab_helpers import (
    lag1,
    matlab_sort,
    round_half_away,
    smartmean,
    smartstd_book_two,
    smartstd_first_edition,
    smartsum,
)
from chan.series import load_panel, load_vintage, panel_line, row_month_ends, vintage_line
from chan.vintage import VintageEntry, VintageUnavailable

#: The S&P 600 small-cap file Example 7.6 reads, the one Chan's script loads.
SMALL_CAPS = "IJR_20080131.mat"

#: The S&P 500 file Example 7.7 reads.
LARGE_CAPS = "SPX_20071123.mat"

#: Example 7.6's one-way transaction cost, 5 basis points, paid twice per trade.
ONE_WAY_COST = 0.0005

#: The date location 4425 splits the Heston and Sadka record on.
SPLIT = pd.Timestamp("2002-01-01")


# --------------------------------------------------------------------------
# Example 7.6, the January effect
# --------------------------------------------------------------------------


class Winners(Enum):
    """Which of the best performers the short side holds."""

    #: The whole top decile, as the MATLAB and R scripts take it.
    DECILE = "decile"
    #: ``np.arange(-topN+1, -1)``, which is the revised Python's slice. It takes
    #: ``topN - 2`` stocks and leaves out the single best performer.
    PYTHON_SLICE = "python-slice"


@dataclass(frozen=True)
class JanuaryRules:
    """What one printout of Example 7.6 does."""

    source: str
    #: True when each stock's last priced day in the period counts, as pandas
    #: resampling takes it. False when one shared row is the period's end.
    per_stock_period_ends: bool
    decile_size: Callable[[float], float]
    winners: Winners
    #: Forward-fill the year-end closes before ranking, as pandas' old default did.
    pads_year_ends: bool
    #: How the source prints a figure, as a format spec. MATLAB's ``%7.4f``
    #: is ``.4f``, the Python's ``%f`` is ``.6f``, and R's default print
    #: keeps seven significant digits, which is ``.7g``.
    printed: str


@dataclass(frozen=True)
class JanuaryTrade:
    """One holding, from a December year-end close to the last close of the next January."""

    entered: pd.Timestamp
    exited: pd.Timestamp
    ranked: int
    #: The losers held long, which is the decile size.
    longs: int
    #: The winners held short. The revised Python's slice holds two fewer.
    shorts: int
    ret: float


@dataclass(frozen=True)
class JanuaryEffect:
    """Every holding the file reaches, and the year-ends it does not."""

    trades: tuple[JanuaryTrade, ...]
    #: December year-ends that were ranked but whose January the file ends before.
    unreached: tuple[pd.Timestamp, ...]
    file_end: pd.Timestamp


def _rank_and_trade(
    annual: NDArray[np.float64],
    january: NDArray[np.float64],
    rules: JanuaryRules,
    universe: int | None = None,
) -> tuple[int, int, int, float]:
    has = np.flatnonzero(np.isfinite(annual))
    order = has[matlab_sort(annual[has])]
    top = int(rules.decile_size(_universe(len(order), universe) / 10))
    losers = order[:top]
    if rules.winners is Winners.DECILE:
        winners = order[len(order) - top :]
    else:
        winners = order[np.arange(-top + 1, -1)]
    ret = (smartmean(january[losers]) - smartmean(january[winners])) / 2 - 2 * ONE_WAY_COST
    return len(order), len(losers), len(winners), float(ret)


def _universe(ranked: int, universe: int | None) -> int:
    """The count a tenth is taken of: ``universe``, or the ranked count when it is None."""
    if universe is None:
        return ranked
    if universe < ranked:
        raise ValueError(f"a universe of {universe} is smaller than the {ranked} stocks ranked")
    return universe


def january_effect(
    closes: pd.DataFrame, rules: JanuaryRules, *, universe: int | None = None
) -> JanuaryEffect:
    """Example 7.6 under one printout's rules, on the frame :func:`load_panel` returns.

    ``universe`` is the count each tenth is taken of. Every printout takes it
    of the stocks it ranked, which is the default. On a panel with members
    missing, that is a tenth of the covered stocks rather than of the index, so
    the point-in-time run passes the whole index's count. It applies to every
    year-end the frame holds, so that run passes one year-end at a time.
    """
    days = closes.index
    if rules.per_stock_period_ends:
        # The final year and the final January are dropped, as the script drops
        # them, because neither is a real period end.
        year_ends = closes.resample("YE").last().iloc[:-1]
        januaries = closes.resample("BYE-JAN").last().iloc[:-1]
        year_end_days = list(year_ends.index)
        jan_by_year = {
            day.year: row for day, row in zip(januaries.index, januaries.to_numpy(), strict=True)
        }
        year_end_rows = year_ends.to_numpy()
        # The script's ``pct_change()`` names no fill method, and every pandas
        # before 3.0 then forward-fills. So a stock with no close in a year is
        # ranked on its last close before it: a return of 0 for a year with no
        # close, and a return across the gap for the year its closes resume.
        # PMC is that case in 2007. The January return reads the unfilled
        # year-end, as the script's ``eoyPrice.values`` does.
        ranked_rows = year_ends.ffill().to_numpy() if rules.pads_year_ends else year_end_rows
        exit_day = {day.year: day for day in januaries.index}
    else:
        ends = row_month_ends(days)
        decembers = [row for row in ends if days[row].month == 12]
        jan_rows = [row for row in ends if days[row].month == 1]
        year_end_days = [days[row] for row in decembers]
        year_end_rows = closes.to_numpy()[decembers]
        ranked_rows = year_end_rows
        jan_by_year = {days[row].year: closes.to_numpy()[row] for row in jan_rows}
        exit_day = {days[row].year: days[row] for row in jan_rows}

    trades, unreached = [], []
    for y in range(1, len(year_end_days)):
        entered = year_end_days[y]
        before, now = ranked_rows[y - 1], ranked_rows[y]
        annual = (now - before) / before
        at = year_end_rows[y]
        if entered.year + 1 not in jan_by_year:
            unreached.append(entered)
            continue
        january = (jan_by_year[entered.year + 1] - at) / at
        ranked, longs, shorts, ret = _rank_and_trade(annual, january, rules, universe)
        trades.append(
            JanuaryTrade(
                entered=entered,
                exited=exit_day[entered.year + 1],
                ranked=ranked,
                longs=longs,
                shorts=shorts,
                ret=ret,
            )
        )
    return JanuaryEffect(trades=tuple(trades), unreached=tuple(unreached), file_end=days[-1])


#: Example 7.6 as both editions' MATLAB print it. The owner read the revised
#: edition on 2026-10-02, and its MATLAB prints the same three returns, labelled
#: with the January exit day rather than the December entry day.
MATLAB_JANUARY = JanuaryRules(
    source="example7_6.m, first and revised editions",
    per_stock_period_ends=False,
    decile_size=round_half_away,
    winners=Winners.DECILE,
    pads_year_ends=False,
    printed=".4f",
)

#: R's ``round`` sends a half to the even neighbour, which is what numpy's
#: does. The owner read that rule in R's Example 7.7, and it is assumed here.
#: No decile on this file lands on a half, so it gives MATLAB's figures either way.
R_JANUARY = JanuaryRules(
    source="Example 7.6 in R, revised edition",
    per_stock_period_ends=False,
    decile_size=np.round,
    winners=Winners.DECILE,
    pads_year_ends=False,
    printed=".4f",
)

PYTHON_JANUARY = JanuaryRules(
    source="example7_6.py, revised edition",
    per_stock_period_ends=True,
    decile_size=np.round,
    winners=Winners.PYTHON_SLICE,
    pads_year_ends=True,
    printed=".6f",
)

JANUARY_RULES = (MATLAB_JANUARY, PYTHON_JANUARY, R_JANUARY)


# --------------------------------------------------------------------------
# Example 7.7, Heston and Sadka
# --------------------------------------------------------------------------


class Mask(Enum):
    """Which stocks a month's ranking keeps, beyond having a return a year earlier."""

    #: The first edition's ``hasReturns``. It ANDs a row in sorted order with
    #: ``isfinite(cl(monthEnds(m-1), :))``, which is in column order, so a stock
    #: is kept or dropped on another stock's close.
    SORTED_AGAINST_COLUMNS = "sorted-against-columns"
    #: Each stock on its own close at the month-end the position is set.
    OWN_CLOSE = "own-close"
    #: Each stock on its own return over the month ending the day the position is set.
    OWN_RETURN = "own-return"


class Statistic(Enum):
    """How the monthly returns become a mean and a standard deviation."""

    #: ``smartmean`` skips a NaN month and the first edition's ``smartstd`` counts it as
    #: zero, dividing by n - 1.
    SMART = "smart"
    #: ``smartmean`` and *Algorithmic Trading*'s ``smartstd``, which skips a NaN month and
    #: divides by n. That is what ``NUMPY`` computes on anything but an infinite entry,
    #: and the member is kept to say which of Chan's helpers the code calls.
    SMART_BOOK_TWO = "smart-book-two"
    #: ``np.nanmean`` and ``np.nanstd``, which divides by n.
    NUMPY = "numpy"
    #: R's ``mean`` and ``sd``, which divides by n - 1, on months with no NaN left.
    R = "r"


@dataclass(frozen=True)
class HestonSadkaRules:
    """What one printout of Example 7.7 does."""

    source: str
    per_stock_period_ends: bool
    mask: Mask
    decile_size: Callable[[float], float]
    #: Divide each month's summed return by the number of positions held. False
    #: leaves it a sum, in units of summed positions rather than of capital.
    per_position: bool
    #: Where ``per_position`` is set, what a month holding nothing returns:
    #: NaN, as MATLAB's and R's 0/0 gives, or 0, as the Python's capital of 1 gives.
    empty_month_is_nan: bool
    #: How many leading months are dropped before the statistics.
    dropped: int
    statistic: Statistic
    #: How the source prints a figure, as a format spec. MATLAB's ``%7.4f``
    #: is ``.4f``, the Python's ``%f`` is ``.6f``, and R's default print
    #: keeps seven significant digits, which is ``.7g``.
    printed: str


@dataclass(frozen=True)
class HestonSadka:
    """The monthly returns one printout's rules produce, and their two summaries."""

    returns: pd.Series
    annual_return: float
    sharpe: float


def monthly_returns(closes: pd.DataFrame, rules: HestonSadkaRules) -> pd.Series:
    """Each month's return, indexed by the month-end it is earned to.

    No month is dropped here. :func:`summarize` drops them.
    """
    if rules.per_stock_period_ends:
        # The final month is dropped, because the file ends before it does.
        ends = closes.resample("ME").last().iloc[:-1]
    else:
        ends = closes.iloc[row_month_ends(closes.index)]
    level = ends.to_numpy()
    previous = lag1(level)
    ret = (level - previous) / previous

    positions = np.zeros_like(ret)
    for held in range(11, len(ret) - 1):
        # The position is set at month-end ``held`` and earns over the month
        # after it, so it ranks on the month a year before that one.
        year_earlier = ret[held - 11]
        order = matlab_sort(year_earlier)
        kept = np.isfinite(year_earlier[order])
        if rules.mask is Mask.SORTED_AGAINST_COLUMNS:
            kept &= np.isfinite(level[held])
        elif rules.mask is Mask.OWN_CLOSE:
            kept &= np.isfinite(level[held][order])
        else:
            kept &= np.isfinite(ret[held][order])
        chosen = order[kept]
        top = int(rules.decile_size(len(chosen) / 10))
        if top:
            positions[held, chosen[:top]] = -1
            positions[held, chosen[len(chosen) - top :]] = 1

    held_then = lag1(positions)
    total = smartsum(held_then * ret, axis=1)
    if rules.per_position:
        count = np.where(np.isfinite(held_then), np.abs(held_then), 0.0).sum(axis=1)
        if rules.empty_month_is_nan:
            with np.errstate(invalid="ignore", divide="ignore"):
                total = total / count
        else:
            total = total / np.where(count == 0, 1.0, count)
    return pd.Series(total, index=ends.index, name=rules.source)


def summarize(returns: pd.Series, rules: HestonSadkaRules) -> tuple[float, float]:
    """The annualised mean and Sharpe ratio, on twelve months a year and no risk-free rate."""
    kept = returns.to_numpy()[rules.dropped :]
    if rules.statistic is Statistic.SMART:
        mean, std = smartmean(kept), smartstd_first_edition(kept)
    elif rules.statistic is Statistic.SMART_BOOK_TWO:
        mean, std = smartmean(kept), smartstd_book_two(kept)
    elif rules.statistic is Statistic.NUMPY:
        mean, std = np.nanmean(kept), np.nanstd(kept)
    else:
        mean, std = np.nanmean(kept), np.nanstd(kept, ddof=1)
    return float(12 * mean), float(math.sqrt(12) * mean / std)


def heston_sadka(closes: pd.DataFrame, rules: HestonSadkaRules) -> HestonSadka:
    """Example 7.7 under one printout's rules, on the frame :func:`load_panel` returns."""
    returns = monthly_returns(closes, rules)
    annual, sharpe = summarize(returns, rules)
    return HestonSadka(returns=returns, annual_return=annual, sharpe=sharpe)


#: The first edition's ``example7_7.m``. The monthly return is a sum over every
#: position held, never divided by their number, so -0.9167 is in units of summed
#: positions. The mean runs over 95 months, counting 12 with no position as 0.
FIRST_EDITION_MATLAB = HestonSadkaRules(
    source="example7_7.m, first edition",
    per_stock_period_ends=False,
    mask=Mask.SORTED_AGAINST_COLUMNS,
    decile_size=np.floor,
    per_position=False,
    empty_month_is_nan=False,
    dropped=0,
    statistic=Statistic.SMART,
    printed=".4f",
)

#: The revised edition's MATLAB as printed on p. 179, with one repair. The
#: listing cuts ``cl`` to its month-end rows and then masks on
#: ``cl(monthEnds(m-1), :)``, which asks a 96-row array for a daily row number
#: and stops on the first pass. The repair reads ``cl(m-1, :)``, the month-end
#: row the cut array holds. The mask removes the stocks it finds by column,
#: through ``setdiff(sortIndex, badData, 'stable')``, so the repair keeps each
#: stock on its own close rather than bringing back the first edition's
#: sorted-against-columns rule.
#:
#: The rest is as printed. The decile takes the floor, each month is divided by
#: the number of positions, so a month with none is MATLAB's 0/0, and
#: ``ret(1:13)=[]`` drops 13 months before ``smartmean`` and ``smartstd``.
#: Pp. 179 to 181 do not print ``smartstd`` itself. Book two's, which skips a
#: NaN month and divides by n, prints Chan's -0.1243, and the first edition's
#: prints -0.1236.
#:
#: The revised edition's code as reposted at
#: pinhaocheng/epchan-quant_trading_MATLAB_codes ``7430b84`` settles both choices the page
#: leaves open. Its ``example7_7.m`` masks on ``cl(m-1, :)``, which is the
#: repair above, and matches this rule everywhere else, down to the -0.0129 and
#: -0.1243 in its closing comment. Its ``smartstd.m`` normalises by N, which is
#: book two's.
REVISED_MATLAB = HestonSadkaRules(
    source="Example 7.7 in MATLAB, revised edition",
    per_stock_period_ends=False,
    mask=Mask.OWN_CLOSE,
    decile_size=np.floor,
    per_position=True,
    empty_month_is_nan=True,
    dropped=13,
    statistic=Statistic.SMART_BOOK_TWO,
    printed=".4f",
)

PYTHON_HESTON_SADKA = HestonSadkaRules(
    source="example7_7.py, revised edition",
    per_stock_period_ends=True,
    mask=Mask.OWN_RETURN,
    decile_size=np.floor,
    per_position=True,
    empty_month_is_nan=False,
    dropped=13,
    statistic=Statistic.NUMPY,
    printed=".6f",
)

#: The revised edition's R as printed on p. 181, with no change. It drops a
#: stock with no return a year earlier through ``order(..., na.last = NA)``,
#: masks each stock on its own close at the month-end, and rounds the decile
#: with R's ``round``, which sends a half to the even neighbour. Each month is
#: divided by its positions, so a month with none is R's 0/0. ``ret[-(1:13)]``
#: drops 13 months before ``mean`` and ``sd`` with ``na.rm=TRUE``.
R_HESTON_SADKA = HestonSadkaRules(
    source="Example 7.7 in R, revised edition",
    per_stock_period_ends=False,
    mask=Mask.OWN_CLOSE,
    decile_size=np.round,
    per_position=True,
    empty_month_is_nan=True,
    dropped=13,
    statistic=Statistic.R,
    printed=".7g",
)

HESTON_SADKA_RULES = (FIRST_EDITION_MATLAB, REVISED_MATLAB, PYTHON_HESTON_SADKA, R_HESTON_SADKA)


def split_at(
    result: HestonSadka, rules: HestonSadkaRules, when: pd.Timestamp = SPLIT
) -> tuple[tuple[int, float, float], tuple[int, float, float]]:
    """The kept months before ``when`` and from it.

    Each half comes back as a count, an annual return and a Sharpe ratio.

    Exploratory, and it carries no verdict. The module docstring says why.
    """
    kept = result.returns.iloc[rules.dropped :]
    halves = []
    for part in (kept[kept.index < when], kept[kept.index >= when]):
        annual, sharpe = summarize(part, _undropped(rules))
        halves.append((len(part), annual, sharpe))
    return halves[0], halves[1]


def _undropped(rules: HestonSadkaRules) -> HestonSadkaRules:
    return HestonSadkaRules(**{**rules.__dict__, "dropped": 0})


#: Where the revised edition makes the claim, directly after the MATLAB listing.
FIVE_YEAR_PAGE = 180

#: What p. 180 suggests the program be run on.
FIVE_YEAR_CLAIM = "the most recent five years instead of the entire data period"

#: How many of the full run's last kept months the second reading of p. 180 averages.
TAIL_MONTHS = 60


def five_year_cutoff(closes: pd.DataFrame) -> pd.Timestamp:
    """The day five calendar years before the file's last row."""
    return closes.index[-1] - pd.DateOffset(years=5)


def most_recent_five_years(closes: pd.DataFrame) -> pd.DataFrame:
    """The rows dated after :func:`five_year_cutoff`."""
    return closes.loc[closes.index > five_year_cutoff(closes)]


@dataclass(frozen=True)
class FiveYearCheck:
    """P. 180's claim that the most recent five years do even worse, under one printout's rules.

    The criterion was written on
    [issue 254](https://github.com/l3a0/quantitative-trading/issues/254) before
    any five-year figure was computed. Reading 1 reruns the program unchanged on
    the last five years of its input, which is what the sentence tells a reader
    to do, and carries the verdict under :data:`REVISED_MATLAB`. Reading 2
    averages the full run's last :data:`TAIL_MONTHS` kept months, and carries no
    verdict, because it adds a rule the book does not print.
    """

    whole: HestonSadka
    rerun: HestonSadka
    #: Reading 1's monthly returns after the program's own drop.
    rerun_kept: pd.Series
    #: Reading 2, as a count, an annual return and a Sharpe ratio.
    tail: tuple[int, float, float]

    @property
    def worse(self) -> bool:
        """Whether reading 1's annual return is below the whole period's, at full precision."""
        return self.rerun.annual_return < self.whole.annual_return


def five_year_check(closes: pd.DataFrame, rules: HestonSadkaRules) -> FiveYearCheck:
    """Both readings of p. 180 beside the whole period, on the frame :func:`load_panel` returns."""
    whole = heston_sadka(closes, rules)
    rerun = heston_sadka(most_recent_five_years(closes), rules)
    last = whole.returns.iloc[rules.dropped :].iloc[-TAIL_MONTHS:]
    annual, sharpe = summarize(last, _undropped(rules))
    return FiveYearCheck(
        whole=whole,
        rerun=rerun,
        rerun_kept=rerun.returns.iloc[rules.dropped :],
        tail=(len(last), annual, sharpe),
    )


# --------------------------------------------------------------------------
# Example 7.6 on IJR's members at 2025-12-31, survivor-only
# --------------------------------------------------------------------------

#: The IJR year-end whose members the survivor run ranks over every January.
SURVIVOR_REPORT_DATE = "2025-12-31"

#: The archive cross-section holding the members' daily closes.
SURVIVOR_CROSS_SECTION = "sp600"

#: Each filing ticker Alpha Vantage files under another symbol, measured on
#: 2026-10-04 against its active and delisted listings with the owner's key.
#: Nine companies were renamed after the filing, and Alpha Vantage keeps a
#: company's whole history under its newest ticker, so fetching the old one
#: returns nothing or another company. Two are share classes, which the filing
#: writes with a slash and Alpha Vantage with a dash. Every other member is
#: fetched under the filing's ticker, the ones delisted in 2026 included.
#: Two of those, NVRI and GTES, came back holding nothing before 2026, which
#: :func:`no_close_at_filing` reports rather than this map hiding.
ALPHAVANTAGE_SYMBOLS: Mapping[str, str] = {
    "AHH": "AHRT",
    "ATGE": "CVSA",
    "AXL": "DCH",
    "EXPI": "AGNT",
    "FDP": "DMC",
    "IAC": "PPLI",
    "MODG": "CALY",
    "MPW": "MPT",
    "VSCO": "VSXY",
    "CWEN/A": "CWEN-A",
    "MOG/A": "MOG-A",
}

#: The first row the run reads. The 2008-12-31 ranking needs a December 2007
#: row, because :func:`january_effect` ranks each year-end against the one
#: before it, so a slice starting in 2008 yields one January fewer.
SURVIVOR_SLICE_START = pd.Timestamp("2007-12-01")

#: January 2009 to January 2026, as the issue declares.
SURVIVOR_JANUARIES = 18

#: The download date naming the committed raw SPY vintage the run takes its
#: trading days from, so a later SPY download does not change the calendar.
CALENDAR_DOWNLOAD = "2026-10-03"

#: The one-sided test's size.
SIGNIFICANCE = 0.05

#: The probability with which :func:`detectable_mean` asks the test to reject.
POWER = 0.8


class SurvivorRunRefused(Exception):
    """The survivor run stopped rather than compute a January from data it cannot trust.

    One class for the four refusals the run makes itself, so :func:`main`
    catches it by name. Catching ``ValueError`` instead would also turn a bug
    into a one-line message.
    """


@dataclass(frozen=True)
class OneSided:
    """A one-sided t-test that a mean is above zero.

    ``std`` removes one degree of freedom, and ``p`` reads the t distribution
    at ``n - 1`` degrees of freedom.
    """

    n: int
    mean: float
    std: float
    t: float
    p: float

    @property
    def rejects(self) -> bool:
        """Whether the mean is detectably above zero at :data:`SIGNIFICANCE`."""
        return self.p < SIGNIFICANCE


def one_sided_t(returns: Sequence[float]) -> OneSided:
    """Test whether the mean of ``returns`` is above zero, one-sided.

    Each January is one trade, so the returns do not overlap and need no
    correction for it.
    """
    values = np.asarray(returns, dtype=float)
    n = len(values)
    mean = float(values.mean())
    std = float(values.std(ddof=1))
    t = mean / (std / math.sqrt(n))
    return OneSided(n=n, mean=mean, std=std, t=t, p=float(stats.t.sf(t, n - 1)))


def detectable_mean(
    std: float, n: int, *, significance: float = SIGNIFICANCE, power: float = POWER
) -> float:
    """The smallest true mean the one-sided test detects with probability ``power``.

    Under a true mean X, the statistic follows a noncentral t at ``n - 1``
    degrees of freedom with noncentrality X √n over ``std``. X is the mean at
    which that distribution exceeds the test's critical value with probability
    ``power``. The normal approximation gives a smaller X, because it ignores
    the uncertainty in ``std``.
    """
    df = n - 1
    critical = stats.t.isf(significance, df)
    noncentrality = optimize.brentq(
        lambda shift: stats.nct.sf(critical, df, shift) - power, 0.0, 50.0, xtol=1e-12
    )
    return float(noncentrality * std / math.sqrt(n))


def survivor_filing() -> Filing:
    """IJR's filing for :data:`SURVIVOR_REPORT_DATE`."""
    (filing,) = (filing for filing in IJR.filings if filing.report_date == SURVIVOR_REPORT_DATE)
    return filing


def survivor_members(filings_dir: Path | None = None) -> tuple[tuple[str, str], ...]:
    """Each member as its filing ticker and the symbol Alpha Vantage files it under.

    A ``ValueError`` if a member has no ticker or two members share a symbol,
    because either would rank one company's series as another's.
    """
    rows = members(IJR, survivor_filing(), filings_dir)
    pairs = tuple((row.ticker, ALPHAVANTAGE_SYMBOLS.get(row.ticker, row.ticker)) for row in rows)
    blank = [row.name for row in rows if not row.ticker]
    if blank:
        raise ValueError(f"{len(blank)} members carry no ticker, the first {blank[0]!r}")
    symbols = [symbol for _, symbol in pairs]
    shared = sorted({symbol for symbol in symbols if symbols.count(symbol) > 1})
    if shared:
        raise ValueError(f"two members map to {', '.join(shared)}")
    return pairs


def survivor_calendar(data_dir: Path | None = None) -> tuple[VintageEntry, pd.Series]:
    """The committed raw SPY vintage the run takes its trading days from."""
    return load_vintage("SPY", unadjusted=True, dated=CALENDAR_DOWNLOAD, data_dir=data_dir)


def missing_members(pairs: Sequence[tuple[str, str]], recorded: set[str]) -> tuple[str, ...]:
    """Members whose symbol has no line, as ``TICKER``, or ``TICKER as SYMBOL`` when mapped."""
    return tuple(
        ticker if ticker == symbol else f"{ticker} as {symbol}"
        for ticker, symbol in pairs
        if symbol not in recorded
    )


def survivor_slice(closes: pd.DataFrame) -> pd.DataFrame:
    """The rows from :data:`SURVIVOR_SLICE_START` to the last row the fetch holds."""
    return closes.loc[closes.index >= SURVIVOR_SLICE_START]


def refuse_off_calendar(closes: pd.DataFrame, calendar: pd.DatetimeIndex) -> None:
    """Refuse a row on a day the calendar holds no row for.

    :func:`row_month_ends` reads the union of every member's dates. One series
    with a row on a day the market was shut adds a row on which almost every
    member is missing, and if that row ends a month it becomes the year-end.
    """
    off = closes.index.difference(calendar)
    if len(off):
        day = off[0]
        symbol = closes.loc[day].first_valid_index()
        named = "a row with no close" if symbol is None else f"{symbol} has a row"
        raise SurvivorRunRefused(
            f"{named} on {day.date()}, which the SPY calendar does not hold, "
            f"and {len(off)} such days in all"
        )


def refuse_nonpositive(closes: pd.DataFrame) -> None:
    """Refuse a close of zero or below, naming the earliest.

    :func:`chan.matlab_helpers.smartmean` skips only a value that is not
    finite. A zero on a January exit row would read as a −100% return and be
    averaged in. A zero at a year-end would rank the stock as a −100% loser
    and leave its January return undefined, so it would take a long slot and
    add nothing. A missing close stays NaN and is not refused.
    """
    with np.errstate(invalid="ignore"):
        bad = closes.to_numpy() <= 0
    if bad.any():
        row, column = np.argwhere(bad)[0]
        raise SurvivorRunRefused(
            f"{closes.columns[column]} closes at {closes.iat[row, column]} on "
            f"{closes.index[row].date()}, and a close of zero or below has no return"
        )


def survivor_effect(closes: pd.DataFrame, calendar: pd.DatetimeIndex) -> JanuaryEffect:
    """:data:`MATLAB_JANUARY` on the slice, in one call, refusing what it cannot read.

    Membership is fixed, so the whole slice goes into one call. A member ranks
    at a year-end only where it has a close there and at the year-end before,
    so one listed after 2008 enters the ranking at its second year-end.
    """
    sliced = survivor_slice(closes)
    refuse_off_calendar(sliced, calendar)
    refuse_nonpositive(sliced)
    effect = january_effect(sliced, MATLAB_JANUARY)
    if effect.unreached:
        raise SurvivorRunRefused(
            f"the closes end {effect.file_end.date()}, before the January after "
            f"{effect.unreached[0].date()}, so that year-end has no exit"
        )
    if len(effect.trades) != SURVIVOR_JANUARIES:
        raise SurvivorRunRefused(
            f"the slice yields {len(effect.trades)} Januaries, not {SURVIVOR_JANUARIES}"
        )
    days = calendar[(calendar >= sliced.index[0]) & (calendar <= sliced.index[-1])]
    for trade in effect.trades:
        december = days[(days.year == trade.entered.year) & (days.month == 12)][-1]
        january = days[(days.year == trade.entered.year + 1) & (days.month == 1)][-1]
        if (trade.entered, trade.exited) != (december, january):
            raise SurvivorRunRefused(
                f"the trade entered {trade.entered.date()} and exited {trade.exited.date()}, "
                f"where the calendar's last December and January days are {december.date()} "
                f"and {january.date()}"
            )
    return effect


def before_costs(effect: JanuaryEffect) -> tuple[float, ...]:
    """Each January's return before costs.

    :func:`_rank_and_trade` charges :data:`ONE_WAY_COST` twice on every trade,
    one constant, so adding it back recovers each return to floating-point
    rounding.
    """
    return tuple(trade.ret + 2 * ONE_WAY_COST for trade in effect.trades)


def ranked_without_exit(closes: pd.DataFrame) -> tuple[int, ...]:
    """For each January, how many ranked members have no close on its exit row.

    A member that stops trading inside January, by a takeover or a delisting,
    has a NaN January return, which :func:`chan.matlab_helpers.smartmean`
    skips. This count is what says how often that happened.
    """
    sliced = survivor_slice(closes)
    days = sliced.index
    ends = row_month_ends(days)
    level = sliced.to_numpy()
    decembers = [row for row in ends if days[row].month == 12]
    exits = {days[row].year: row for row in ends if days[row].month == 1}
    counts = []
    for before, now in zip(decembers, decembers[1:], strict=False):
        exit_row = exits.get(days[now].year + 1)
        if exit_row is None:
            continue
        with np.errstate(invalid="ignore", divide="ignore"):
            ranked = np.isfinite((level[now] - level[before]) / level[before])
        counts.append(int((ranked & ~np.isfinite(level[exit_row])).sum()))
    return tuple(counts)


def year_ends_missed(closes: pd.DataFrame) -> dict[str, tuple[pd.Timestamp, ...]]:
    """Each member with no close on one or more December year-end rows, and which."""
    sliced = survivor_slice(closes)
    decembers = [row for row in row_month_ends(sliced.index) if sliced.index[row].month == 12]
    at = sliced.iloc[decembers]
    return {
        symbol: tuple(at.index[at[symbol].isna()])
        for symbol in sliced.columns
        if at[symbol].isna().any()
    }


def no_close_at_filing(closes: pd.DataFrame) -> tuple[str, ...]:
    """Members with no close on :data:`SURVIVOR_REPORT_DATE`, the day the filing lists them.

    The fund held every member that day, so a series without a close there is
    missing the member's own history rather than starting late. Such a member
    is never ranked at the last year-end, and usually at none.
    """
    day = pd.Timestamp(SURVIVOR_REPORT_DATE)
    if day not in closes.index:
        return tuple(closes.columns)
    return tuple(closes.columns[closes.loc[day].isna()])


def survivor_reading(test: OneSided, detectable: float) -> str:
    """The reading the issue declared before any return was computed.

    Failing to reject gives the owner's wording, with X at the measured
    standard deviation. Rejecting gives no verdict, because the survivor bias
    alone could produce a mean above zero.
    """
    if test.rejects:
        return (
            f"above zero on survivors, no verdict: a mean of {test.mean:.4f} a January, "
            f"t {test.t:.2f}, p {test.p:.3f}, over {test.n} Januaries. The survivor bias "
            f"alone could produce it"
        )
    return (
        f"no January effect detectable above about {detectable:.1%} a January, on members "
        f"that favour the effect"
    )


@dataclass(frozen=True)
class SurvivorRun:
    """Everything the survivor run computes, and what it read to compute it."""

    #: Each member as its filing ticker and its Alpha Vantage symbol.
    members: tuple[tuple[str, str], ...]
    #: The cross-section lines read, one per member with a series.
    entries: tuple[ArchiveEntry, ...]
    #: Members whose symbol has no line, as ``TICKER`` or ``TICKER as SYMBOL``.
    missing: tuple[str, ...]
    calendar: VintageEntry
    effect: JanuaryEffect
    before: tuple[float, ...]
    test: OneSided
    #: X, the mean the test detects with :data:`POWER`, at the measured deviation.
    detectable: float
    after_mean: float
    no_exit: tuple[int, ...]
    missed: dict[str, tuple[pd.Timestamp, ...]]
    #: Members whose series holds no close on the filing's own date.
    no_close: tuple[str, ...]

    @property
    def reading(self) -> str:
        return survivor_reading(self.test, self.detectable)


def run_survivors(
    *,
    data_dir: Path | None = None,
    directory: Path | None = None,
    filings_dir: Path | None = None,
) -> SurvivorRun:
    """Read the members, their closes and the calendar, and run Example 7.6 on them."""
    pairs = survivor_members(filings_dir)
    entries, closes = read_cross_section(
        SURVIVOR_CROSS_SECTION,
        column="adjusted_close",
        symbols=[symbol for _, symbol in pairs],
        data_dir=data_dir,
        directory=directory,
    )
    missing = missing_members(pairs, {entry.symbol for entry in entries})
    calendar, spy = survivor_calendar(data_dir)
    effect = survivor_effect(closes, pd.DatetimeIndex(spy.index))
    before = before_costs(effect)
    test = one_sided_t(before)
    return SurvivorRun(
        members=pairs,
        entries=tuple(entries),
        missing=missing,
        calendar=calendar,
        effect=effect,
        before=before,
        test=test,
        detectable=detectable_mean(test.std, test.n),
        after_mean=float(np.mean([trade.ret for trade in effect.trades])),
        no_exit=ranked_without_exit(closes),
        missed=year_ends_missed(closes),
        no_close=no_close_at_filing(closes),
    )


# --------------------------------------------------------------------------
# Example 7.6 on the S&P 600 as it stood at each year-end, registered
# --------------------------------------------------------------------------

#: The percentiles of one January's covered returns that a member with no
#: checked price is given when it is inserted into a tenth, the worse for the
#: strategy first. Issue 329's owner ruling of 2026-10-04 names both.
BOUND_PERCENTILES = (1.0, 99.0)


class PointInTimeRefused(Exception):
    """The point-in-time run stopped rather than compute a January it cannot trust.

    The two refusals it shares with the survivor run raise
    :class:`SurvivorRunRefused`, and :func:`main` catches both.
    """


@dataclass(frozen=True)
class YearEnd:
    """One year-end of the point-in-time run: who it ranks, who it misses, and its January.

    ``trade`` is :data:`MATLAB_JANUARY` on the covered members alone, with the
    tenth taken of ``universe``, after costs as every trade is. ``low`` and
    ``high`` are before costs. They are equal, and equal to ``trade``'s return
    with its costs added back, exactly when no missing member threatens a
    tenth.
    """

    report_date: str
    trade: JanuaryTrade
    members: int
    covered: int
    #: The missing members, each of which counts toward the tenth.
    missing: int
    #: The ranked covered members plus every missing member.
    universe: int
    #: Each missing member that could change a tenth, mapped to the tenth it
    #: threatens, as :func:`chan.fund_panel.threat_sides` names it.
    sides: Mapping[tuple[str, int], str]
    #: Ranked covered members with no close on the January exit row.
    no_exit: int
    low: float
    high: float

    @property
    def exact(self) -> bool:
        """Whether no missing member could change a tenth, so the January is the full panel's."""
        return not self.sides

    def threatening(self, side: str) -> int:
        """How many missing members threaten ``side``, one of :data:`chan.fund_panel.SIDES`."""
        return sum(1 for value in self.sides.values() if value == side)


def year_end_slice(
    closes: pd.DataFrame, calendar: pd.DatetimeIndex, report_date: str
) -> pd.DataFrame:
    """A year-end's rows, from the first trading day of the December before to February's first.

    That is the span :func:`january_effect` needs for exactly one trade: two
    December year-ends to rank between, and a February row that makes the
    last January row a month-end.
    """
    year = pd.Timestamp(report_date).year
    first = calendar[(calendar.year == year - 1) & (calendar.month == 12)]
    last = calendar[(calendar.year == year + 1) & (calendar.month == 2)]
    if len(first) == 0 or len(last) == 0:
        raise PointInTimeRefused(
            f"{report_date}: the calendar does not run from December {year - 1} "
            f"to February {year + 1}"
        )
    return closes.loc[(closes.index >= first[0]) & (closes.index <= last[0])]


def slice_returns(
    sliced: pd.DataFrame,
) -> tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp, NDArray[np.float64], NDArray[np.float64]]:
    """The rank day, the entry day, the exit day, and each column's annual and January return.

    The days and returns are the ones :data:`MATLAB_JANUARY` reads: month-ends
    by row, ranking each December year-end against the one before it, and
    holding to the last row of the January after.
    """
    days = sliced.index
    ends = row_month_ends(days)
    decembers = [row for row in ends if days[row].month == 12]
    januaries = [row for row in ends if days[row].month == 1]
    if len(decembers) != 2 or days[januaries[-1]].year != days[decembers[1]].year + 1:
        raise PointInTimeRefused(
            f"the slice from {days[0].date()} to {days[-1].date()} does not hold two "
            f"December year-ends and the January after the second"
        )
    level = sliced.to_numpy()
    before, now, after = level[decembers[0]], level[decembers[1]], level[januaries[-1]]
    return (
        days[decembers[0]],
        days[decembers[1]],
        days[januaries[-1]],
        (now - before) / before,
        (after - now) / now,
    )


def bounded_january(
    annual: NDArray[np.float64],
    january: NDArray[np.float64],
    tenth: int,
    *,
    long: int = 0,
    short: int = 0,
    unplaced: int = 0,
) -> tuple[float, float]:
    """One January's low and high return before costs, by the owner's ruling on issue 329.

    Each member that threatens a tenth is inserted into it and displaces the
    least extreme covered member there. A tenth with more threats than places
    holds threats only. An inserted member's January return is a percentile of
    the covered members' January returns, set per leg so that each series is
    a bound. The low series gives an inserted loser, held long, the 1st
    percentile, and an inserted winner, held short, the 99th. The high series
    does the reverse. Every unplaced member takes the same return within a
    series, so only how many of them go long matters. Every split is tried,
    and the low series keeps the lowest return and the high series the highest.

    With nothing to insert, both are the covered members' return, which is
    :func:`_rank_and_trade`'s with its costs added back.
    """
    has = np.flatnonzero(np.isfinite(annual))
    order = has[matlab_sort(annual[has])]
    held = january[has]
    held = held[np.isfinite(held)]
    worst, best = np.percentile(held, BOUND_PERCENTILES)
    bounds = []
    for long_value, short_value, pick in ((worst, best, min), (best, worst, max)):
        returns = []
        for going_long in range(unplaced + 1):
            in_long = min(tenth, long + going_long)
            in_short = min(tenth, short + unplaced - going_long)
            losers = np.concatenate(
                [january[order[: tenth - in_long]], np.full(in_long, long_value)]
            )
            winners = np.concatenate(
                [january[order[len(order) - (tenth - in_short) :]], np.full(in_short, short_value)]
            )
            returns.append(float((smartmean(losers) - smartmean(winners)) / 2))
        bounds.append(pick(returns))
    return bounds[0], bounds[1]


def point_in_time_year(
    rows: Sequence[MemberRow],
    year: Coverage,
    closes: pd.DataFrame,
    calendar: pd.DatetimeIndex,
    filings_dir: Path | None = None,
) -> YearEnd:
    """One year-end's January, exact or bounded, refusing what it cannot read.

    The covered members' closes are sliced to this year-end alone, because
    :func:`january_effect` reads no membership and would rank every column
    with an annual return. The missing members are placed and flagged from the
    filings, with the tenth sized on the ranked covered members plus every
    missing member.
    """
    date = year.report_date
    missing = set(year.missing)
    tickers = [row.ticker for row in rows if row.report_date == date and row.key not in missing]
    absent = [ticker for ticker in tickers if ticker not in closes.columns]
    if absent:
        raise PointInTimeRefused(
            f"{date}: {len(absent)} covered members have no series in the closes read, "
            f"the first {absent[0]}"
        )
    sliced = year_end_slice(closes[tickers], calendar, date)
    refuse_off_calendar(sliced, calendar)
    refuse_nonpositive(sliced)
    ranked_on, entered, exited, annual, january = slice_returns(sliced)
    expected = (price_date(calendar, date), exit_date(calendar, date))
    if (entered, exited) != expected:
        raise PointInTimeRefused(
            f"{date}: the slice enters {entered.date()} and exits {exited.date()}, where the "
            f"filing's price date is {expected[0].date()} and January's last trading day "
            f"is {expected[1].date()}"
        )
    before = pd.Timestamp(date).year - 1
    rank_day = calendar[(calendar.year == before) & (calendar.month == 12)][-1]
    if ranked_on != rank_day:
        raise PointInTimeRefused(
            f"{date}: the slice ranks against {ranked_on.date()}, where the calendar's last "
            f"trading day of December {before} is {rank_day.date()}"
        )
    ranked = int(np.isfinite(annual).sum())
    universe = ranked + len(year.missing)
    effect = january_effect(sliced, MATLAB_JANUARY, universe=universe)
    if len(effect.trades) != 1:
        raise PointInTimeRefused(f"{date}: the slice yields {len(effect.trades)} trades, not one")
    (trade,) = effect.trades
    if (trade.entered, trade.exited, trade.ranked) != (entered, exited, ranked):
        raise PointInTimeRefused(
            f"{date}: january_effect entered {trade.entered.date()} and ranked "
            f"{trade.ranked}, where the slice gives {entered.date()} and {ranked}"
        )
    sides = threat_sides(year_end_returns(IJR, date, filings_dir), year.missing, universe)
    counts = {side: sum(1 for value in sides.values() if value == side) for side in SIDES}
    low, high = bounded_january(annual, january, trade.longs, **counts)
    unbounded, _ = bounded_january(annual, january, trade.longs)
    if not math.isclose(unbounded, trade.ret + 2 * ONE_WAY_COST, abs_tol=1e-12):
        raise PointInTimeRefused(
            f"{date}: the covered members' return is {unbounded} before costs where "
            f"january_effect gives {trade.ret + 2 * ONE_WAY_COST}"
        )
    return YearEnd(
        report_date=date,
        trade=trade,
        members=year.members,
        covered=year.covered,
        missing=len(year.missing),
        universe=universe,
        sides=sides,
        no_exit=int((np.isfinite(annual) & ~np.isfinite(january)).sum()),
        low=low,
        high=high,
    )


def _span(low: float, high: float, spec: str) -> str:
    """One figure where both series print the same, otherwise both, low first."""
    first, second = format(low, spec), format(high, spec)
    return first if first == second else f"{first} to {second}"


def point_in_time_verdict(low: OneSided, high: OneSided, x_low: float, x_high: float) -> str:
    """The verdict issue 329 worded before any return was computed.

    Each series is tested on its own. If both fail to reject, the verdict is
    the owner's wording with the larger X, since that is the size neither
    series can rule out. If both reject, it names the effect with its mean, t,
    p and count. If they differ, the free sources cannot decide it.
    """
    if low.rejects and high.rejects:
        return (
            f"a January effect above zero: a mean of {_span(low.mean, high.mean, '.4f')} a "
            f"January, t {_span(low.t, high.t, '.2f')}, p {_span(low.p, high.p, '.3f')}, "
            f"over {low.n} Januaries"
        )
    if not low.rejects and not high.rejects:
        return f"no January effect detectable above about {max(x_low, x_high):.1%} a January"
    return (
        f"the free sources cannot decide it: the low series gives p {low.p:.3f} and the high "
        f"series p {high.p:.3f}, so the next step is buying prices for the members that "
        f"threaten a tenth"
    )


@dataclass(frozen=True)
class PointInTimeRun:
    """Everything the point-in-time run computes, and what it read to compute it."""

    #: The cross-section lines read, one per mapped ticker with a series.
    entries: tuple[ArchiveEntry, ...]
    calendar: VintageEntry
    year_ends: tuple[YearEnd, ...]
    low: OneSided
    high: OneSided
    #: X for each series, the mean its test detects with :data:`POWER`.
    x_low: float
    x_high: float

    @property
    def verdict(self) -> str:
        return point_in_time_verdict(self.low, self.high, self.x_low, self.x_high)

    @property
    def after_costs(self) -> tuple[float, float]:
        """Each series' mean less the two one-way costs every trade pays."""
        return self.low.mean - 2 * ONE_WAY_COST, self.high.mean - 2 * ONE_WAY_COST


def run_point_in_time(
    *,
    data_dir: Path | None = None,
    directory: Path | None = None,
    filings_dir: Path | None = None,
) -> PointInTimeRun:
    """Read the members file, the closes and the calendar, and run every year-end."""
    rows = sp600_panel.load()
    entries, closes = read_cross_section(
        sp600_panel.CROSS_SECTION,
        column="adjusted_close",
        symbols=sp600_panel.tickers(rows),
        data_dir=data_dir,
        directory=directory,
    )
    calendar, spy = survivor_calendar(data_dir)
    days = pd.DatetimeIndex(spy.index)
    year_ends = tuple(
        point_in_time_year(rows, year, closes, days, filings_dir)
        for year in coverage(IJR, rows, filings_dir)
    )
    if len(year_ends) != SURVIVOR_JANUARIES:
        raise PointInTimeRefused(
            f"the members file reaches {len(year_ends)} year-ends, not {SURVIVOR_JANUARIES}"
        )
    low = one_sided_t([year.low for year in year_ends])
    high = one_sided_t([year.high for year in year_ends])
    return PointInTimeRun(
        entries=tuple(entries),
        calendar=calendar,
        year_ends=year_ends,
        low=low,
        high=high,
        x_low=detectable_mean(low.std, low.n),
        x_high=detectable_mean(high.std, high.n),
    )


def survivorship_gap(
    run: PointInTimeRun, survivors: SurvivorRun
) -> tuple[tuple[tuple[float, float], ...], tuple[float, float]]:
    """The survivor run's January less this run's, per January and in the mean, low then high.

    Issue 329 asks for the gap described rather than tested. Both runs read one
    cross-section, so it measures membership rather than two download dates.
    """
    exits = [trade.exited for trade in survivors.effect.trades]
    if exits != [year.trade.exited for year in run.year_ends]:
        raise PointInTimeRefused("the survivor run's Januaries are not this run's, so no gap")
    per = tuple(
        (before - year.low, before - year.high)
        for before, year in zip(survivors.before, run.year_ends, strict=True)
    )
    return per, (survivors.test.mean - run.low.mean, survivors.test.mean - run.high.mean)


# --------------------------------------------------------------------------
# The report
# --------------------------------------------------------------------------


def _figure(value: float, printed: str) -> str:
    return format(value, printed)


def report_january(members, closes: pd.DataFrame) -> None:
    print("Example 7.6, the January effect")
    print(f"  {panel_line(members)}")
    for rules in JANUARY_RULES:
        result = january_effect(closes, rules)
        print(f"  {rules.source}")
        for trade in result.trades:
            print(
                f"    entered {trade.entered.date()} exited {trade.exited.date()}: "
                f"{_figure(trade.ret, rules.printed)}   "
                f"({trade.longs} long and {trade.shorts} short of {trade.ranked} ranked)"
            )
        for entered in result.unreached:
            print(
                f"    entered {entered.date()}: not computable, the file ends "
                f"{result.file_end.date()} before the January it holds through"
            )


def report_heston_sadka(members, closes: pd.DataFrame) -> None:
    print("Example 7.7, Heston and Sadka")
    print(f"  {panel_line(members)}")
    for rules in HESTON_SADKA_RULES:
        result = heston_sadka(closes, rules)
        print(
            f"  {rules.source}: average annual return "
            f"{_figure(result.annual_return, rules.printed)}, Sharpe ratio "
            f"{_figure(result.sharpe, rules.printed)}"
        )
    result = heston_sadka(closes, PYTHON_HESTON_SADKA)
    before, after = split_at(result, PYTHON_HESTON_SADKA)
    print(f"  Exploratory, no verdict: {PYTHON_HESTON_SADKA.source} split at {SPLIT.date()}")
    for label, (months, annual, sharpe) in (("before", before), ("from", after)):
        print(
            f"    {label} {SPLIT.date()}, {months} months: {annual:.6f} a year, "
            f"Sharpe ratio {sharpe:.6f}"
        )
    print(
        f"  The most recent five years of p. {FIVE_YEAR_PAGE}, "
        f"rows after {five_year_cutoff(closes):%Y-%m-%d}"
    )
    for rules in (REVISED_MATLAB, PYTHON_HESTON_SADKA):
        check = five_year_check(closes, rules)
        if rules is REVISED_MATLAB:
            verdict = "reproduced" if check.worse else "not reproduced"
        else:
            verdict = "no verdict"
        months, annual, sharpe = check.tail
        print(
            f"    {rules.source}, {verdict}: rerun on {len(check.rerun_kept)} months "
            f"{_figure(check.rerun.annual_return, rules.printed)} a year against the whole "
            f"period's {_figure(check.whole.annual_return, rules.printed)}. Its Sharpe ratio "
            f"{_figure(check.rerun.sharpe, rules.printed)}, no verdict. The last {months} months "
            f"{_figure(annual, rules.printed)} a year, Sharpe ratio "
            f"{_figure(sharpe, rules.printed)}, no verdict"
        )


def _years(days: Sequence[pd.Timestamp]) -> str:
    years = [day.year for day in days]
    if years == list(range(years[0], years[-1] + 1)) and len(years) > 2:
        return f"{years[0]} to {years[-1]}"
    return ", ".join(str(year) for year in years)


def report_survivors(result: SurvivorRun) -> None:
    filing = survivor_filing()
    downloads = sorted({entry.download_date for entry in result.entries})
    print("Example 7.6 on IJR's members at 2025-12-31, survivor-only and exploratory")
    print(
        f"  members: {len(result.members)} from IJR's {filing.form} for {filing.report_date}, "
        f"accession {filing.accession}"
    )
    print(
        f"  closes: {len(result.entries)} series from the {SURVIVOR_CROSS_SECTION} "
        f"cross-section, Alpha Vantage adjusted, downloaded {', '.join(downloads)}"
    )
    print(f"  calendar: {vintage_line(result.calendar)}")
    print(f"  members with no series: {len(result.missing)}")
    for name in result.missing:
        print(f"    {name}")
    print(
        f"  members whose series has no close on {SURVIVOR_REPORT_DATE}, the filing's own "
        f"date: {len(result.no_close)}"
    )
    for symbol in result.no_close:
        entry = next(entry for entry in result.entries if entry.symbol == symbol)
        print(f"    {symbol}: its series runs {entry.first_date} to {entry.last_date}")
    print(f"  members missing a year-end close: {len(result.missed)}")
    for symbol, days in sorted(result.missed.items()):
        print(f"    {symbol}: {_years(days)}")
    print(f"  {MATLAB_JANUARY.source}, returns before costs")
    for trade, before, no_exit in zip(
        result.effect.trades, result.before, result.no_exit, strict=True
    ):
        print(
            f"    entered {trade.entered.date()} exited {trade.exited.date()}: {before:.4f}   "
            f"({trade.longs} long and {trade.shorts} short of {trade.ranked} ranked, "
            f"{no_exit} ranked with no exit close)"
        )
    test = result.test
    print(
        f"  before costs: mean {test.mean:.4f}, standard deviation {test.std:.4f}, "
        f"t {test.t:.2f}, one-sided p {test.p:.3f}, over {test.n} Januaries"
    )
    print(
        f"  detectable with {POWER:.0%} probability at {SIGNIFICANCE:.0%}: "
        f"{result.detectable:.4f} a January"
    )
    print(f"  after costs: mean {result.after_mean:.4f}")
    print(f"  reading: {result.reading}")
    print(
        "  Read one way only: the companies that left the index are missing, and both "
        "legs gain from their absence"
    )


def report_point_in_time(result: PointInTimeRun, survivors: SurvivorRun | None = None) -> None:
    downloads = sorted({entry.download_date for entry in result.entries})
    print("Example 7.6 on the S&P 600 as it stood at each year-end, registered")
    print(
        f"  members: {sp600_panel.MEMBERS_PATH.relative_to(sp600_panel.FILINGS_DIR.parent.parent)}"
        f", IJR's year-end filings, 2007 to 2025"
    )
    print(
        f"  closes: {len(result.entries)} series from the {sp600_panel.CROSS_SECTION} "
        f"cross-section, Alpha Vantage adjusted, downloaded {', '.join(downloads)}"
    )
    print(f"  calendar: {vintage_line(result.calendar)}")
    print(f"  {MATLAB_JANUARY.source}, the tenth taken of the whole index, before costs")
    for year in result.year_ends:
        trade = year.trade
        held = f"{year.low:.4f}" if year.exact else f"{year.low:.4f} to {year.high:.4f}"
        print(
            f"    {year.report_date}: entered {trade.entered.date()} exited "
            f"{trade.exited.date()}: {held}   ({'exact' if year.exact else 'bounded'}; "
            f"{trade.longs} long and {trade.shorts} short of {trade.ranked} ranked, a tenth of "
            f"{year.universe}; {year.missing} of {year.members} members missing, "
            f"{year.threatening('long')} threatening the losers, "
            f"{year.threatening('short')} the winners, {year.threatening('unplaced')} "
            f"unplaced; {year.no_exit} ranked with no exit close)"
        )
    for name, test, x, after in (
        ("low", result.low, result.x_low, result.after_costs[0]),
        ("high", result.high, result.x_high, result.after_costs[1]),
    ):
        print(
            f"  the {name} series: mean {test.mean:.4f}, standard deviation {test.std:.4f}, "
            f"t {test.t:.2f}, one-sided p {test.p:.3f}, over {test.n} Januaries; detectable "
            f"with {POWER:.0%} probability at {SIGNIFICANCE:.0%}: {x:.4f} a January; after "
            f"costs: mean {after:.4f}"
        )
    print(f"  verdict: {result.verdict}")
    if survivors is not None:
        per, means = survivorship_gap(result, survivors)
        print(
            "  the survivor-only run less this one's low and high series, described rather "
            "than tested"
        )
        for year, (low, high) in zip(result.year_ends, per, strict=True):
            print(f"    {year.trade.exited.year} January: {low:.4f} and {high:.4f}")
        print(f"    the mean: {means[0]:.4f} and {means[1]:.4f}")


def run(*, data_dir: Path | None = None) -> None:
    """Read both files and print every figure beside the panel it came from."""
    small = load_panel(SMALL_CAPS, data_dir=data_dir)
    report_january(*small)
    print()
    large = load_panel(LARGE_CAPS, data_dir=data_dir)
    report_heston_sadka(*large)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="python -m chan.equity_seasonals",
        description=(
            "Examples 7.6 and 7.7 on Chan's files. With --survivors, Example 7.6 on IJR's "
            "members at 2025-12-31 instead, and with --point-in-time, on IJR's members at "
            "each year-end. Both need the owner's data archive."
        ),
    )
    which = parser.add_mutually_exclusive_group()
    which.add_argument(
        "--survivors",
        action="store_true",
        help="run Example 7.6 from January 2009 on IJR's 2025-12-31 members",
    )
    which.add_argument(
        "--point-in-time",
        action="store_true",
        help="run Example 7.6 from January 2009 on IJR's members at each year-end",
    )
    args = parser.parse_args([] if argv is None else argv)
    try:
        if args.survivors:
            report_survivors(run_survivors())
        elif args.point_in_time:
            report_point_in_time(run_point_in_time(), run_survivors())
        else:
            run()
    except (
        VintageUnavailable,
        ArchiveUnavailable,
        ArchiveRefused,
        SurvivorRunRefused,
        PointInTimeRefused,
        PanelRefused,
    ) as refusal:
        # A refusal naming which member is missing is worth nothing at the
        # bottom of a pandas traceback, which is the reason
        # `chan.stationary_candidates.main` gives for the same line.
        raise SystemExit(str(refusal)) from refusal


if __name__ == "__main__":
    main(sys.argv[1:])
