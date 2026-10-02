"""Chan's two equity seasonals, Examples 7.6 and 7.7, on the files he ran them on.

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
printout, each naming the rules that make its figures land. A builder who writes
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
3. The revised edition's MATLAB, whose figures the owner read from the revised
   Kindle edition on 2026-10-02. Its code was not transcribed into this repo,
   so the rules :data:`REVISED_MATLAB` applies are a reading that reproduces
   the printed figures rather than a copy of the printed code.
4. The revised edition's R, read the same way. Its 7.7 figures are printed to
   seven significant digits, which pins its rules more tightly than any other
   printout. The revised MATLAB's four decimals are reached by masking each
   stock on its own close or on its own return, and R's seven digits are
   reached only by the close, which is also what the owner read the MATLAB
   indexing.

Three limits, each stated where it applies.

1. Both files hold only the companies in their index on the day Chan saved
   them, carried backwards. A verdict of "disappeared" here is a verdict on
   survivors.
   [Issue 196](https://github.com/l3a0/quantitative-trading/issues/196) is
   where the effect is tested on the rest.
2. ``IJR_20080114.mat`` ends on 2008-01-14. Chan's third January return,
   0.0881, holds through 2008-01-31, so it cannot be computed from the
   committed file under any edition's rules.
3. The 2002 split of the revised Python is exploratory. It was computed before
   any criterion for "disappeared" was written down, so it carries no verdict.

The scale-break guard is not applied. ``refuse_window_crossing_a_break`` serves
the pair readers and :func:`chan.series.load_panel` does not call it. The
comment above ``FLAGGED_IN_CHANS_MAT_FILES`` in ``tests/test_scale_breaks.py``
says why for these files.

``tests/test_equity_seasonals.py`` is the single authority for every number
any prose surface quotes about either example.

Usage:
    python -m chan.equity_seasonals
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from chan.matlab_helpers import lag1, matlab_sort, round_half_away, smartmean, smartstd
from chan.series import load_panel, panel_line
from chan.vintage import VintageUnavailable

#: The S&P 600 small-cap file Example 7.6 reads. Chan's script loads
#: ``IJR_20080131``, which the mirror does not hold.
SMALL_CAPS = "IJR_20080114.mat"

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
    decile: int
    ret: float


@dataclass(frozen=True)
class JanuaryEffect:
    """Every holding the file reaches, and the year-ends it does not."""

    trades: tuple[JanuaryTrade, ...]
    #: December year-ends that were ranked but whose January the file ends before.
    unreached: tuple[pd.Timestamp, ...]
    file_end: pd.Timestamp


def _row_month_ends(days: pd.DatetimeIndex) -> NDArray[np.intp]:
    """The rows whose next row falls in another month.

    The final row is never one, because the next row does not exist. That is
    how Chan's scripts find a month-end, by row rather than by calendar.
    """
    months = days.month.to_numpy()
    return np.flatnonzero(months[:-1] != months[1:])


def _rank_and_trade(
    annual: NDArray[np.float64],
    january: NDArray[np.float64],
    rules: JanuaryRules,
) -> tuple[int, int, float]:
    has = np.flatnonzero(np.isfinite(annual))
    order = has[matlab_sort(annual[has])]
    top = int(rules.decile_size(len(order) / 10))
    losers = order[:top]
    if rules.winners is Winners.DECILE:
        winners = order[len(order) - top :]
    else:
        winners = order[np.arange(-top + 1, -1)]
    ret = (smartmean(january[losers]) - smartmean(january[winners])) / 2 - 2 * ONE_WAY_COST
    return len(order), top, float(ret)


def january_effect(closes: pd.DataFrame, rules: JanuaryRules) -> JanuaryEffect:
    """Example 7.6 under one printout's rules, on the frame :func:`load_panel` returns."""
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
        exit_day = {day.year: day for day in januaries.index}
    else:
        ends = _row_month_ends(days)
        decembers = [row for row in ends if days[row].month == 12]
        jan_rows = [row for row in ends if days[row].month == 1]
        year_end_days = [days[row] for row in decembers]
        year_end_rows = closes.to_numpy()[decembers]
        jan_by_year = {days[row].year: closes.to_numpy()[row] for row in jan_rows}
        exit_day = {days[row].year: days[row] for row in jan_rows}

    trades, unreached = [], []
    for y in range(1, len(year_end_days)):
        entered = year_end_days[y]
        before, at = year_end_rows[y - 1], year_end_rows[y]
        annual = (at - before) / before
        if entered.year + 1 not in jan_by_year:
            unreached.append(entered)
            continue
        january = (jan_by_year[entered.year + 1] - at) / at
        ranked, decile, ret = _rank_and_trade(annual, january, rules)
        trades.append(
            JanuaryTrade(
                entered=entered,
                exited=exit_day[entered.year + 1],
                ranked=ranked,
                decile=decile,
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
    printed=".4f",
)

#: R's ``round`` sends a half to the even neighbour, which is what numpy's
#: does. No decile on this file lands on a half, so it gives MATLAB's figures.
R_JANUARY = JanuaryRules(
    source="Example 7.6 in R, revised edition",
    per_stock_period_ends=False,
    decile_size=np.round,
    winners=Winners.DECILE,
    printed=".4f",
)

PYTHON_JANUARY = JanuaryRules(
    source="example7_6.py, revised edition",
    per_stock_period_ends=True,
    decile_size=np.round,
    winners=Winners.PYTHON_SLICE,
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

    #: ``smartmean`` skips a NaN month and ``smartstd`` counts it as zero, dividing by n - 1.
    SMART = "smart"
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
    #: NaN, as MATLAB's 0/0 gives, or 0, as the Python's capital of 1 gives.
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
        ends = closes.iloc[_row_month_ends(closes.index)]
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
    earned = held_then * ret
    finite = np.isfinite(earned)
    total = np.where(finite, earned, 0.0).sum(axis=1)
    total[~finite.any(axis=1)] = np.nan
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
        mean, std = smartmean(kept), smartstd(kept)
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

#: A reading of the revised edition's MATLAB that reproduces both its printed
#: figures. Its code was not transcribed into this repo. The owner read that it
#: divides by the number of positions and masks on ``cl(monthEnds(m-1), :)``
#: after ``cl`` has been cut to its month-end rows, which cannot run as printed.
#: This reading keeps Chan's helpers, lets MATLAB's 0/0 make a month with no
#: position NaN, and starts the statistics at the thirteenth month.
REVISED_MATLAB = HestonSadkaRules(
    source="Example 7.7 in MATLAB, revised edition",
    per_stock_period_ends=False,
    mask=Mask.OWN_CLOSE,
    decile_size=np.floor,
    per_position=True,
    empty_month_is_nan=True,
    dropped=12,
    statistic=Statistic.SMART,
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

#: A reading of the revised edition's R that reproduces both its printed
#: figures to every digit printed. The owner read that it rounds the decile
#: size where MATLAB and Python take the floor, and that it uses R's ``sd``.
R_HESTON_SADKA = HestonSadkaRules(
    source="Example 7.7 in R, revised edition",
    per_stock_period_ends=False,
    mask=Mask.OWN_CLOSE,
    decile_size=np.round,
    per_position=True,
    empty_month_is_nan=False,
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
                f"({trade.decile} of {trade.ranked} each side)"
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


def run(*, data_dir: Path | None = None) -> None:
    """Read both files and print every figure beside the panel it came from."""
    small = load_panel(SMALL_CAPS, data_dir=data_dir)
    report_january(*small)
    print()
    large = load_panel(LARGE_CAPS, data_dir=data_dir)
    report_heston_sadka(*large)


def main() -> None:
    try:
        run()
    except VintageUnavailable as refusal:
        # A refusal naming which member is missing is worth nothing at the
        # bottom of a pandas traceback, which is the reason
        # `chan.stationary_candidates.main` gives for the same line.
        raise SystemExit(str(refusal)) from refusal


if __name__ == "__main__":
    main()
