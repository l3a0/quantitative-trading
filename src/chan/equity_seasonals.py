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
   [Issue 336](https://github.com/l3a0/quantitative-trading/issues/336) tests
   Example 7.7 after the book on the S&P 500 as it stood each month, which
   is the monthly run below, and
   [issue 196](https://github.com/l3a0/quantitative-trading/issues/196) keeps
   the years before 2002. The point-in-time run below is where Example 7.6 is
   tested on the rest.
2. The 2002 split of the revised Python is exploratory. It was computed before
   any criterion for "disappeared" was written down, so it carries no verdict.

P. 180's claim that the most recent five years do even worse is the one
verdict here on timing. Its criterion was written on
[issue 254](https://github.com/l3a0/quantitative-trading/issues/254) before
any five-year figure was computed, and :class:`FiveYearCheck` says what it
reads. The claim holds on this file, and the first limit above still applies
to it.

The scale-break guard is not applied. ``refuse_window_crossing_a_break`` serves
the pair readers and :func:`chan.series.load_panel` does not call it. The
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

**Example 7.7 on the S&P 500 as IVV held it each month.**
[Issue 336](https://github.com/l3a0/quantitative-trading/issues/336) runs
:data:`REVISED_MATLAB` unchanged and before costs over the 213 months from
January 2009 to September 2026, on the members IVV's quarter-end schedules
list, each carried forward to the next. It reads three sources.

1. The members file, ``research/filings/ivv/members.csv``, which
   :mod:`chan.sp500_panel` reads, with the holes file beside it.
   [Issue 373](https://github.com/l3a0/quantitative-trading/issues/373)
   built both.
2. The adjusted closes and volumes of the ``sp500`` lines those tickers name,
   with the bytes in the owner's archive.
3. The committed raw SPY vintage, as the calendar.

Each series stops at its last row that traded and moved, by
:func:`last_traded`. The members a month-end may rank are the ones
:func:`chan.sp500_panel.monthly_coverage` covers with those stops, passed to
:func:`monthly_returns` as ``members``, so the tenth is a tenth of the covered
members. The run tests whether the mean monthly return is above zero, and
:func:`monthly_verdict` words the outcome. :data:`PYTHON_HESTON_SADKA` runs
beside it with no verdict. The claim, the test and the wording were written
on the issue before any return was computed, so the result is labelled
registered.

``tests/test_equity_seasonals.py`` is the single authority for every number
any prose surface quotes about either example.

Usage:
    python -m chan.equity_seasonals
    python -m chan.equity_seasonals --survivors
    python -m chan.equity_seasonals --point-in-time

``--point-in-time`` runs Example 7.6 on the S&P 600 at each year-end, then
Example 7.7 on the S&P 500 each month.
"""

from __future__ import annotations

import argparse
import math
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from enum import Enum
from pathlib import Path

import numpy as np
import pandas as pd
from ithildincore.stats import NeweyWestSummary, newey_west_summary
from numpy.typing import NDArray
from scipy import optimize, stats

from chan import sp500_panel, sp600_panel
from chan.archive import ArchiveEntry, ArchiveRefused, ArchiveUnavailable, read_cross_section
from chan.fund_holdings import IJR, Filing, members
from chan.fund_panel import (
    SIDES,
    Coverage,
    Key,
    MemberRow,
    PanelRefused,
    coverage,
    exit_date,
    previous_rows,
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
from chan.sp500_panel import MonthCoverage
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


def _allowed(
    members: pd.DataFrame | None, ends: pd.DatetimeIndex, columns: pd.Index
) -> NDArray[np.bool_] | None:
    """Which stocks each month-end may rank, one row per month-end, in the panel's column order.

    ``None`` stays ``None``, which ranks every column. A month the frame does
    not hold ranks nobody. A month-end is matched to the frame by its calendar
    month, so a row labelled 2009-01-30 and one labelled 2009-01-31 both read
    January 2009.
    """
    if members is None:
        return None
    if members.columns.has_duplicates or set(members.columns) != set(columns):
        extra = sorted(set(members.columns) - set(columns))
        absent = sorted(set(columns) - set(members.columns))
        repeated = sorted(set(members.columns[members.columns.duplicated()]))
        raise ValueError(
            f"the members frame's columns differ from the panel's: {len(extra)} not in the "
            f"panel {extra[:5]}, {len(absent)} not in the frame {absent[:5]}, {len(repeated)} "
            f"repeated {repeated[:5]}"
        )
    if not isinstance(members.index, pd.PeriodIndex) or members.index.freqstr != "M":
        raise ValueError("the members frame must be indexed by calendar month, as monthly periods")
    if not all(pd.api.types.is_bool_dtype(dtype) for dtype in members.dtypes):
        raise ValueError("the members frame must hold only True and False")
    aligned = members.reindex(index=ends.to_period("M"), columns=columns, fill_value=False)
    return aligned.to_numpy(dtype=bool)


def positions(
    closes: pd.DataFrame, rules: HestonSadkaRules, *, members: pd.DataFrame | None = None
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """The position each month-end sets, and each stock's return over the month ending there.

    Both frames are indexed by month-end with the panel's columns. A position
    is 1 for the best tenth, held long, -1 for the worst, held short, and 0
    otherwise. It is set at its row's month-end and earns over the month
    after, which is the next row of the returns.

    ``members`` is :func:`monthly_returns`'s.
    """
    if rules.per_stock_period_ends:
        # The final month is dropped, because the file ends before it does.
        ends = closes.resample("ME").last().iloc[:-1]
    else:
        ends = closes.iloc[row_month_ends(closes.index)]
    level = ends.to_numpy()
    previous = lag1(level)
    ret = (level - previous) / previous
    allowed = _allowed(members, pd.DatetimeIndex(ends.index), closes.columns)

    held_at = np.zeros_like(ret)
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
        if allowed is not None:
            # ``kept`` is in sorted order, so the membership row is read in it
            # too. Read in column order, it would keep or drop a stock on
            # another stock's membership, the first edition's
            # sorted-against-columns defect in a new place.
            kept &= allowed[held][order]
        chosen = order[kept]
        top = int(rules.decile_size(len(chosen) / 10))
        if top:
            held_at[held, chosen[:top]] = -1
            held_at[held, chosen[len(chosen) - top :]] = 1
    return (
        pd.DataFrame(held_at, index=ends.index, columns=closes.columns),
        pd.DataFrame(ret, index=ends.index, columns=closes.columns),
    )


def monthly_returns(
    closes: pd.DataFrame, rules: HestonSadkaRules, *, members: pd.DataFrame | None = None
) -> pd.Series:
    """Each month's return, indexed by the month-end it is earned to.

    No month is dropped here. :func:`summarize` drops them.

    ``members`` says which stocks each month-end may rank: a boolean frame
    indexed by calendar month, as monthly periods, with the panel's columns.
    ``None``, the default, ranks every column with a return a year earlier,
    which is what every printout does. A month the frame does not hold ranks
    nobody, and a frame whose columns are not the panel's is a ``ValueError``
    naming the difference.
    """
    held_at, stock_returns = positions(closes, rules, members=members)
    ret = stock_returns.to_numpy()
    held_then = lag1(held_at.to_numpy())
    total = smartsum(held_then * ret, axis=1)
    if rules.per_position:
        count = np.where(np.isfinite(held_then), np.abs(held_then), 0.0).sum(axis=1)
        if rules.empty_month_is_nan:
            with np.errstate(invalid="ignore", divide="ignore"):
                total = total / count
        else:
            total = total / np.where(count == 0, 1.0, count)
    return pd.Series(total, index=held_at.index, name=rules.source)


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


def heston_sadka(
    closes: pd.DataFrame, rules: HestonSadkaRules, *, members: pd.DataFrame | None = None
) -> HestonSadka:
    """Example 7.7 under one printout's rules, on the frame :func:`load_panel` returns.

    ``members`` is :func:`monthly_returns`'s.
    """
    returns = monthly_returns(closes, rules, members=members)
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

    Each return is one holding, a January for Example 7.6 and a month for
    Example 7.7, so the returns do not overlap and need no correction for it.
    The count is the sequence's length.
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

    X is a mean per holding, as ``std`` is a deviation per holding, so a caller
    whose holding is a month multiplies by twelve for a year.
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
# Example 7.7 on the S&P 500 as IVV held it each month, registered
# --------------------------------------------------------------------------

#: The first and last days the S&P 500 run reads. December 2008's ranking
#: reads January 2008's return, which needs December 2007's month-end close,
#: and :func:`chan.series.row_month_ends` finds September 2026's month-end by
#: the October row after it.
MONTHLY_START = pd.Timestamp("2007-12-03")
MONTHLY_END = pd.Timestamp("2026-10-01")

#: The first and last months a position is held over, one month after the
#: first and last ranking months :mod:`chan.sp500_panel` covers.
FIRST_HELD = sp500_panel.FIRST_MONTH + 1
LAST_HELD = sp500_panel.LAST_MONTH + 1

#: January 2009 to September 2026, the count issue 336's ruling fixed.
HELD_MONTHS = 213

#: The last ranking month the departing-name comparison reads, the last whose
#: twelfth month a schedule sets.
DEPARTING_LAST = pd.Period("2025-08", "M")

#: Each month-end's three places in a tenth, as :func:`positions` sets them.
PLACES = ("long", "short", "neither")


class MonthlyRunRefused(Exception):
    """The S&P 500 run stopped rather than compute a month it cannot trust."""


def last_traded(adjusted: pd.DataFrame, volume: pd.DataFrame) -> pd.Series:
    """Each series' last row that traded and moved, by the rule issue 336 fixed before the run.

    Some acquired companies' files carry rows after the last trade, at an
    unchanged price with zero or token volume. Those rows would keep a company
    that is gone ranked at a zero return, and hide when it stopped. So, walking
    back from a series' last row, a row is dropped while its volume is zero or
    its adjusted close equals the row before it, and the series stops at the
    row that remains. The rule needs no threshold.

    A series' rows are the ones holding an adjusted close. A series with no
    row left stops at ``NaT``.
    """
    stops = {}
    for symbol in adjusted.columns:
        closes = adjusted[symbol].dropna()
        level = closes.to_numpy()
        traded = volume[symbol].reindex(closes.index).to_numpy()
        kept = len(level)
        while kept and (traded[kept - 1] == 0 or (kept > 1 and level[kept - 1] == level[kept - 2])):
            kept -= 1
        stops[symbol] = closes.index[kept - 1] if kept else pd.NaT
    return pd.Series(stops, index=adjusted.columns, dtype="datetime64[ns]")


def traded_spans(
    spans: Mapping[str, tuple[str, str]], stops: pd.Series
) -> dict[str, tuple[str, str]]:
    """The manifest's spans, with each stopped series' last date replaced by its stop.

    A series with no row that traded and moved is refused, because the
    coverage rule needs a last date for every series it reads.
    """
    empty = [symbol for symbol, stop in stops.items() if pd.isna(stop)]
    if empty:
        raise MonthlyRunRefused(
            f"{len(empty)} series hold no row that traded and moved, the first {empty[0]}"
        )
    traded = dict(spans)
    for symbol, stop in stops.items():
        traded[symbol] = (spans[symbol][0], str(stop.date()))
    return traded


def stopped_closes(
    closes: pd.DataFrame, stops: pd.Series, calendar: pd.DatetimeIndex
) -> pd.DataFrame:
    """Each series cut at its stop, with its last close carried to the next month-end row only.

    A held stock whose prices stop strictly between two month-ends earns its
    return to its last close and nothing after it, as issue 336's ruling sets
    out. The carried close gives the month-end row that return. Nothing is
    carried further, and :func:`members_mask` drops the stock at that
    month-end, because the carried close would otherwise make it rankable for
    the month after. A stop on a month-end needs nothing carried. A stop
    inside the frame's span on a day the frame holds no row for is refused,
    because its last close has no row to come from.
    """
    ends = calendar[row_month_ends(calendar)]
    cut = closes.copy()
    for symbol in cut.columns:
        stop = stops.get(symbol, pd.NaT)
        if pd.isna(stop) or stop >= cut.index[-1]:
            continue
        if stop >= cut.index[0] and stop not in cut.index:
            raise MonthlyRunRefused(f"{symbol} stops on {stop.date()}, a day the panel has no row")
        last = cut.at[stop, symbol] if stop in cut.index else np.nan
        cut.loc[cut.index > stop, symbol] = np.nan
        after = ends[ends > stop]
        if stop not in ends and len(after) and after[0] in cut.index:
            cut.at[after[0], symbol] = last
    return cut


def monthly_panel(
    adjusted: pd.DataFrame, stops: pd.Series, calendar: pd.DatetimeIndex
) -> tuple[pd.DataFrame, int]:
    """The closes the run ranks, and how many series rows fell on no calendar day.

    The frame runs from :data:`MONTHLY_START` to :data:`MONTHLY_END` on the
    calendar's days. A series row on a day the calendar lacks is dropped and
    counted, so one stray row cannot become a month-end, which
    :func:`refuse_off_calendar` refuses for Example 7.6 instead.
    """
    days = calendar[(calendar >= MONTHLY_START) & (calendar <= MONTHLY_END)]
    if len(days) == 0 or days[0] != MONTHLY_START or days[-1] != MONTHLY_END:
        raise MonthlyRunRefused(
            f"the calendar does not trade on both {MONTHLY_START.date()} and {MONTHLY_END.date()}"
        )
    sliced = adjusted.loc[(adjusted.index >= MONTHLY_START) & (adjusted.index <= MONTHLY_END)]
    off = sliced.loc[~sliced.index.isin(days)]
    dropped = int(off.notna().to_numpy().sum())
    return stopped_closes(sliced.reindex(days), stops, calendar), dropped


def members_mask(
    rows: Sequence[MemberRow], months: Sequence[MonthCoverage], columns: Sequence[str]
) -> pd.DataFrame:
    """Which stocks each ranking month may rank: the members its coverage counts as covered.

    The frame is indexed by calendar month, so a schedule for 2013-03-31
    applies at that month's last row, 2013-03-28, rather than after it.
    """
    by_schedule: dict[str, list[MemberRow]] = {}
    for row in rows:
        by_schedule.setdefault(row.report_date, []).append(row)
    index = pd.PeriodIndex([month.month for month in months], freq="M")
    mask = pd.DataFrame(False, index=index, columns=list(columns))
    for month, period in zip(months, index, strict=True):
        missing = set(month.missing)
        covered = [r.ticker for r in by_schedule[month.schedule] if r.key not in missing]
        absent = [ticker for ticker in covered if ticker not in mask.columns]
        if absent:
            raise MonthlyRunRefused(f"{month.month}: covered member {absent[0]} has no column")
        mask.loc[period, covered] = True
    return mask


def refuse_unranked(closes: pd.DataFrame, mask: pd.DataFrame) -> None:
    """Refuse a covered member that :data:`REVISED_MATLAB` could not rank.

    The coverage is computed from the committed holes file and the manifest's
    spans, and the panel from the bytes. A covered member needs a close at its
    month-end and at the two month-ends a year back, so a disagreement between
    the two would rank fewer stocks than the coverage reports.
    """
    days = pd.DatetimeIndex(closes.index[row_month_ends(closes.index)])
    level = closes.loc[days].set_axis(days.to_period("M"))
    for month in mask.index:
        covered = mask.columns[mask.loc[month].to_numpy()]
        for back in (0, sp500_panel.LOOKBACK - 1, sp500_panel.LOOKBACK):
            row = level.loc[month - back, covered]
            if row.isna().any():
                raise MonthlyRunRefused(
                    f"{month}: covered member {row.index[row.isna()][0]} has no close at the "
                    f"month-end of {month - back}"
                )


def held_months(returns: pd.Series) -> pd.Series:
    """The months from :data:`FIRST_HELD` to :data:`LAST_HELD`, selected by calendar month.

    Selecting by day would lose one, because :data:`REVISED_MATLAB` labels
    January 2009 by its last row, 2009-01-30, and :data:`PYTHON_HESTON_SADKA`
    by 2009-01-31. A NaN month is refused by name rather than dropped, since
    dropping it would shrink the count the ruling fixed.
    """
    months = returns.index.to_period("M")
    chosen = returns[(months >= FIRST_HELD) & (months <= LAST_HELD)]
    if len(chosen) != HELD_MONTHS:
        raise MonthlyRunRefused(
            f"{len(chosen)} months fall from {FIRST_HELD} to {LAST_HELD}, not {HELD_MONTHS}"
        )
    empty = chosen.index[chosen.isna().to_numpy()]
    if len(empty):
        raise MonthlyRunRefused(
            f"{empty[0].to_period('M')} holds no position, and {len(empty)} months in all"
        )
    return chosen


def monthly_verdict(test: OneSided, x: float) -> str:
    """The verdict issue 336 worded before any return was computed.

    ``x`` is the annual return the test detects with :data:`POWER`. The
    verdict never says the strategy is dead.
    """
    if test.rejects:
        return (
            f"a return above zero: a mean of {test.mean:.4f} a month, t {test.t:.2f}, "
            f"p {test.p:.3f}, over {test.n} months"
        )
    return f"no return detectable above about {x:.1%} a year"


@dataclass(frozen=True)
class MonthlyTest:
    """One rule's held months on the panel and mask, and the test of their mean."""

    rules: HestonSadkaRules
    returns: pd.Series
    test: OneSided
    newey_west: NeweyWestSummary
    #: X, the annual return the test detects with :data:`POWER`, twelve times the monthly mean.
    x: float

    @property
    def newey_west_se(self) -> float:
        """The Newey-West standard error of the mean, the mean over its t."""
        return self.test.mean / self.newey_west.t_newey_west


def monthly_test(
    closes: pd.DataFrame, rules: HestonSadkaRules, members: pd.DataFrame
) -> MonthlyTest:
    """One rule's held months, before costs, with the one-sided test and Newey-West beside it."""
    returns = held_months(monthly_returns(closes, rules, members=members))
    test = one_sided_t(returns.to_numpy())
    return MonthlyTest(
        rules=rules,
        returns=returns,
        test=test,
        newey_west=newey_west_summary(returns.to_numpy()),
        x=12 * detectable_mean(test.std, test.n),
    )


@dataclass(frozen=True)
class ScheduleChange:
    """The names that changed between two consecutive schedules, and the positions they took.

    The change fell somewhere between the two, so the ranking months after the
    earlier schedule's month and before the later's may be misdated for those
    names.
    """

    earlier: str
    later: str
    removed: tuple[Key, ...]
    added: tuple[Key, ...]
    months: tuple[pd.Period, ...]
    #: Positions the carry-forward run gave a removed name in those months.
    removed_positions: int = 0
    #: Positions the union run gave an added name in those months.
    added_positions: int = 0

    @property
    def misdated(self) -> int:
        return self.removed_positions + self.added_positions


def schedule_changes(
    rows: Sequence[MemberRow], previous: Mapping[Key, Key]
) -> tuple[ScheduleChange, ...]:
    """Each pair of consecutive schedules, with the names removed and added between them.

    Names are matched by issuer through :func:`chan.fund_panel.previous_rows`,
    so a ticker change is neither. A removed name is a row at the earlier
    schedule that no row at the later one links back to, and an added name is
    a row at the later schedule with no link back.
    """
    by_schedule: dict[str, list[Key]] = {}
    for row in rows:
        by_schedule.setdefault(row.report_date, []).append(row.key)
    schedules = sp500_panel.schedule_months()
    changes = []
    for (earlier, first), (later, second) in zip(schedules, schedules[1:], strict=False):
        linked = {previous[key] for key in by_schedule[later] if key in previous}
        months = tuple(
            month
            for month in pd.period_range(first + 1, second - 1, freq="M")
            if sp500_panel.FIRST_MONTH <= month <= sp500_panel.LAST_MONTH
        )
        changes.append(
            ScheduleChange(
                earlier=earlier,
                later=later,
                removed=tuple(key for key in by_schedule[earlier] if key not in linked),
                added=tuple(key for key in by_schedule[later] if key not in previous),
                months=months,
            )
        )
    return tuple(changes)


def bracketing_masks(
    mask: pd.DataFrame,
    rows: Sequence[MemberRow],
    changes: Sequence[ScheduleChange],
    covers: Callable[[MemberRow, pd.Period], str | None],
) -> tuple[pd.DataFrame, pd.DataFrame, set[tuple[pd.Period, str]]]:
    """The intersection and union masks, and the month and ticker pairs the union adds.

    At a misdated month the intersection keeps a covered member only if the
    later schedule links back to it. The union adds each added name that the
    coverage rule, ``covers``, covers when its later row is evaluated at that
    month. True membership lies between the two whenever a name changes at
    most once between schedules.
    """
    by_key = {row.key: row for row in rows}
    intersection, union = mask.copy(), mask.copy()
    added: set[tuple[pd.Period, str]] = set()
    for change in changes:
        for month in change.months:
            for key in change.removed:
                ticker = by_key[key].ticker
                if ticker:
                    intersection.loc[month, ticker] = False
            for key in change.added:
                row = by_key[key]
                if row.ticker and covers(row, month) is None and not mask.loc[month, row.ticker]:
                    union.loc[month, row.ticker] = True
                    added.add((month, row.ticker))
    return intersection, union, added


def count_misdated(
    changes: Sequence[ScheduleChange],
    rows: Sequence[MemberRow],
    carried: pd.DataFrame,
    unioned: pd.DataFrame,
    added: set[tuple[pd.Period, str]],
) -> tuple[ScheduleChange, ...]:
    """Each change with the positions its names took in its misdated months.

    ``carried`` and ``unioned`` are :func:`positions`' frames for the
    carry-forward and union runs. A removed name counts where the carry-forward
    run held it, and an added name where the union run, which alone ranks it
    there, held it.
    """
    by_key = {row.key: row for row in rows}
    carried = carried.set_axis(carried.index.to_period("M"))
    unioned = unioned.set_axis(unioned.index.to_period("M"))
    counted = []
    for change in changes:
        removed = sum(
            1
            for month in change.months
            for key in change.removed
            if by_key[key].ticker and carried.loc[month, by_key[key].ticker] != 0
        )
        new = sum(
            1
            for month in change.months
            for key in change.added
            if (month, by_key[key].ticker) in added and unioned.loc[month, by_key[key].ticker] != 0
        )
        counted.append(replace(change, removed_positions=removed, added_positions=new))
    return tuple(counted)


def stopped_positions(
    held_at: pd.DataFrame, stock_returns: pd.DataFrame, stops: pd.Series
) -> tuple[int, float]:
    """The held positions whose stock stopped inside the month held, and their returns summed.

    A position is stopped when its stock's stop falls strictly between the
    month-end it was set at and the next. Each return is signed by its side,
    so it is what the position earned. Only the months from
    :data:`FIRST_HELD` to :data:`LAST_HELD` are read.
    """
    days = pd.DatetimeIndex(held_at.index)
    stop = stops.reindex(held_at.columns).to_numpy(dtype="datetime64[ns]")
    count, total = 0, 0.0
    for at in range(1, len(days)):
        if not FIRST_HELD <= days[at].to_period("M") <= LAST_HELD:
            continue
        side = held_at.iloc[at - 1].to_numpy()
        with np.errstate(invalid="ignore"):
            inside = (stop > days[at - 1].to_datetime64()) & (stop < days[at].to_datetime64())
        hit = (side != 0) & inside
        count += int(hit.sum())
        total += float(np.nansum(side[hit] * stock_returns.iloc[at].to_numpy()[hit]))
    return count, total


@dataclass(frozen=True)
class Departures:
    """Covered member-months by whether the name leaves the index within a year, and by place.

    ``table`` holds the departing row, then the staying row, each counting
    the member-months :data:`REVISED_MATLAB` placed long, short and neither.
    ``p`` is the chi-square test's on that table. It is descriptive, since
    member-months repeat the same names, and decides nothing.
    """

    table: tuple[tuple[int, int, int], tuple[int, int, int]]
    p: float

    def shares(self, departing: bool) -> tuple[float, float, float]:
        """One row's member-months as shares of its total, long, short and neither."""
        long, short, neither = self.table[0 if departing else 1]
        total = long + short + neither
        return long / total, short / total, neither / total


def departures(
    rows: Sequence[MemberRow],
    months: Sequence[MonthCoverage],
    previous: Mapping[Key, Key],
    held_at: pd.DataFrame,
) -> Departures:
    """The departing-name comparison over ranking months 2008-12 to :data:`DEPARTING_LAST`.

    A departing name at a ranking month is a covered member with no chain of
    links to the schedule that sets the month twelve months later. Members
    with no checked price are dropped from the ranking, and the argument for
    that is that whether a name leaves the index has little to do with one
    month's return a year earlier. This table is that argument's test.
    """
    by_schedule: dict[str, list[MemberRow]] = {}
    for row in rows:
        by_schedule.setdefault(row.report_date, []).append(row)
    forward = {earlier: later for later, earlier in previous.items()}
    # Read as an array, because a label lookup per member-month takes most of a minute.
    placed = held_at.to_numpy()
    row_of = {month: at for at, month in enumerate(held_at.index.to_period("M"))}
    column_of = {ticker: at for at, ticker in enumerate(held_at.columns)}
    leaving, staying = [0, 0, 0], [0, 0, 0]
    for month in months:
        period = pd.Period(month.month, "M")
        if period > DEPARTING_LAST:
            continue
        target = sp500_panel.setter(period + sp500_panel.LOOKBACK)
        missing = set(month.missing)
        for row in by_schedule[month.schedule]:
            if row.key in missing:
                continue
            step: Key | None = row.key
            while step is not None and step[0] < target:
                step = forward.get(step)
            side = placed[row_of[period], column_of[row.ticker]]
            counts = leaving if step is None or step[0] != target else staying
            counts[0 if side > 0 else 1 if side < 0 else 2] += 1
    result = stats.chi2_contingency(np.array([leaving, staying]))
    return Departures(
        table=((leaving[0], leaving[1], leaving[2]), (staying[0], staying[1], staying[2])),
        p=float(result.pvalue),
    )


@dataclass(frozen=True)
class MonthlyRun:
    """Everything the S&P 500 run computes, and what it read to compute it."""

    #: The cross-section lines read, one per mapped ticker with a series.
    entries: tuple[ArchiveEntry, ...]
    calendar: VintageEntry
    #: Each series' last row that traded and moved.
    stops: pd.Series
    #: Series whose stop comes before their file's last row.
    moved: int
    #: Series rows inside the span on a day the calendar lacks, dropped.
    off_calendar: int
    coverage: tuple[MonthCoverage, ...]
    matlab: MonthlyTest
    python: MonthlyTest
    #: :data:`REVISED_MATLAB`'s mean over the held months on each bracketing mask.
    intersection_mean: float
    union_mean: float
    changes: tuple[ScheduleChange, ...]
    #: Positions whose stock stopped inside the month held, and their returns summed.
    stopped: int
    stopped_return: float
    departures: Departures

    @property
    def verdict(self) -> str:
        return monthly_verdict(self.matlab.test, self.matlab.x)

    @property
    def covered(self) -> int:
        return sum(month.covered for month in self.coverage)

    @property
    def members(self) -> int:
        return sum(month.members for month in self.coverage)

    @property
    def stops_inside(self) -> int:
        """Covered member-months whose series ends inside the month held."""
        return sum(month.stops for month in self.coverage)


def run_monthly_point_in_time(
    *, data_dir: Path | None = None, directory: Path | None = None
) -> MonthlyRun:
    """Read the members file, the closes, their volumes and the calendar, and run every month."""
    rows = sp500_panel.load()
    symbols = sp500_panel.tickers(rows)
    entries, adjusted = read_cross_section(
        sp500_panel.CROSS_SECTION,
        column="adjusted_close",
        symbols=symbols,
        data_dir=data_dir,
        directory=directory,
    )
    _, volume = read_cross_section(
        sp500_panel.CROSS_SECTION,
        column="volume",
        symbols=symbols,
        data_dir=data_dir,
        directory=directory,
    )
    calendar, spy = load_vintage("SPY", unadjusted=True, data_dir=data_dir)
    days = pd.DatetimeIndex(spy.index)
    stops = last_traded(adjusted, volume)
    manifest = sp500_panel.spans(data_dir)
    moved = sum(1 for symbol, stop in stops.items() if str(stop.date()) != manifest[symbol][1])
    spans = traded_spans(manifest, stops)
    holes = sp500_panel.read_holes()
    previous = previous_rows(sp500_panel.FUND)
    coverage = tuple(sp500_panel.monthly_coverage(rows, spans, holes, days, previous=previous))
    traded, off_calendar = monthly_panel(adjusted, stops, days)
    closes = traded.reindex(columns=symbols)
    refuse_nonpositive(closes)
    mask = members_mask(rows, coverage, symbols)
    refuse_unranked(closes, mask)

    matlab = monthly_test(closes, REVISED_MATLAB, mask)
    python = monthly_test(closes, PYTHON_HESTON_SADKA, mask)
    held_at, stock_returns = positions(closes, REVISED_MATLAB, members=mask)

    covers = sp500_panel.coverage_rule(rows, spans, holes, days, previous=previous)
    changes = schedule_changes(rows, previous)
    intersection, union, added = bracketing_masks(mask, rows, changes, covers)
    union_held, _ = positions(closes, REVISED_MATLAB, members=union)
    stopped, stopped_return = stopped_positions(held_at, stock_returns, stops)
    return MonthlyRun(
        entries=tuple(entries),
        calendar=calendar,
        stops=stops,
        moved=moved,
        off_calendar=off_calendar,
        coverage=coverage,
        matlab=matlab,
        python=python,
        intersection_mean=monthly_test(closes, REVISED_MATLAB, intersection).test.mean,
        union_mean=monthly_test(closes, REVISED_MATLAB, union).test.mean,
        changes=count_misdated(changes, rows, held_at, union_held, added),
        stopped=stopped,
        stopped_return=stopped_return,
        departures=departures(rows, coverage, previous, held_at),
    )


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


def _monthly_figures(result: MonthlyTest) -> str:
    test, nw = result.test, result.newey_west
    return (
        f"mean {test.mean:.4f} a month, standard deviation {test.std:.4f}, t {test.t:.2f}, "
        f"one-sided p {test.p:.3f}, over {test.n} months; Newey-West t "
        f"{nw.t_newey_west:.2f} at lag {nw.lag}, standard error {result.newey_west_se:.4f}; "
        f"detectable with {POWER:.0%} probability at {SIGNIFICANCE:.0%}: {result.x:.2%} a year"
    )


def report_monthly(result: MonthlyRun) -> None:
    downloads = sorted({entry.download_date for entry in result.entries})
    first, last = result.coverage[0].schedule, result.coverage[-1].schedule
    print("Example 7.7 on the S&P 500 as IVV held it each month, registered")
    print(
        f"  members: {sp500_panel.MEMBERS_PATH.relative_to(sp500_panel.FILINGS_DIR.parent.parent)}"
        f", IVV's quarter-end schedules, {first} to {last}, each carried forward to the next"
    )
    print(
        f"  closes: {len(result.entries)} series from the {sp500_panel.CROSS_SECTION} "
        f"cross-section, Alpha Vantage adjusted, downloaded {', '.join(downloads)}"
    )
    print(f"  calendar: {vintage_line(result.calendar)}")
    print(
        f"  the panel: {MONTHLY_START.date()} to {MONTHLY_END.date()}, {result.off_calendar} "
        f"series rows on no calendar day dropped; {result.moved} of {len(result.stops)} series "
        f"stop before their file's last row, at their last row that traded and moved"
    )
    shares = [month.covered / month.members for month in result.coverage]
    low = result.coverage[int(np.argmin(shares))]
    high = result.coverage[int(np.argmax(shares))]
    print(
        f"  coverage: {result.covered} of {result.members} member-months covered, ranking "
        f"{result.coverage[0].month} to {result.coverage[-1].month}, from {low.covered} of "
        f"{low.members} in {low.month} to {high.covered} of {high.members} in {high.month}; "
        f"{result.stops_inside} covered members stop inside the month held"
    )
    by_year: dict[str, list[str]] = {}
    for month in result.coverage:
        by_year.setdefault(month.month[:4], []).append(f"{month.covered}/{month.members}")
    for year, counts in by_year.items():
        print(f"    {year}: {' '.join(counts)}")
    print(
        f"  {REVISED_MATLAB.source}, the tenth taken of the covered members, before costs, "
        f"{FIRST_HELD} to {LAST_HELD}"
    )
    print(f"    {_monthly_figures(result.matlab)}")
    print(f"    verdict: {result.verdict}")
    print(f"  {PYTHON_HESTON_SADKA.source}, the same panel and members, no verdict")
    print(f"    {_monthly_figures(result.python)}")
    print(
        f"  {REVISED_MATLAB.source} on the two masks bracketing each name that changed, no "
        f"verdict: intersection mean {result.intersection_mean:.4f}, union mean "
        f"{result.union_mean:.4f} a month"
    )
    removed = sum(len(change.removed) for change in result.changes)
    added = sum(len(change.added) for change in result.changes)
    print(
        f"  names that changed between schedules: {removed} removed and {added} added; "
        f"positions in the months between that the carry-forward run gave a removed name "
        f"and the union run an added name: {sum(c.misdated for c in result.changes)}"
    )
    for change in result.changes:
        print(
            f"    {change.earlier} to {change.later}: {len(change.removed)} removed, "
            f"{len(change.added)} added, {len(change.months)} months between; positions "
            f"{change.removed_positions} on removed names and {change.added_positions} on "
            f"added names"
        )
    print(
        f"  positions whose stock stopped inside the month held: {result.stopped}, their "
        f"returns summed by side {result.stopped_return:.4f}"
    )
    table = result.departures
    print(
        f"  covered member-months by whether the name leaves the index within twelve months, "
        f"ranking {sp500_panel.FIRST_MONTH} to {DEPARTING_LAST}, described rather than tested"
    )
    for label, departing in (("departing", True), ("staying", False)):
        counts = table.table[0 if departing else 1]
        shares_of = table.shares(departing)
        print(
            f"    {label}: "
            + ", ".join(
                f"{place} {count} ({share:.1%})"
                for place, count, share in zip(PLACES, counts, shares_of, strict=True)
            )
        )
    print(f"    chi-square p {table.p:.3f}, descriptive only")


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
            "members at 2025-12-31 instead, and with --point-in-time, Example 7.6 on IJR's "
            "members at each year-end and Example 7.7 on IVV's each month. Both need the "
            "owner's data archive."
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
        help=(
            "run Example 7.6 from January 2009 on IJR's members at each year-end, then "
            "Example 7.7 from January 2009 on IVV's members each month"
        ),
    )
    args = parser.parse_args([] if argv is None else argv)
    try:
        if args.survivors:
            report_survivors(run_survivors())
        elif args.point_in_time:
            report_point_in_time(run_point_in_time(), run_survivors())
            print()
            report_monthly(run_monthly_point_in_time())
        else:
            run()
    except (
        VintageUnavailable,
        ArchiveUnavailable,
        ArchiveRefused,
        SurvivorRunRefused,
        PointInTimeRefused,
        MonthlyRunRefused,
        PanelRefused,
    ) as refusal:
        # A refusal naming which member is missing is worth nothing at the
        # bottom of a pandas traceback, which is the reason
        # `chan.stationary_candidates.main` gives for the same line.
        raise SystemExit(str(refusal)) from refusal


if __name__ == "__main__":
    main(sys.argv[1:])
