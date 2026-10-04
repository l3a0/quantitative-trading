"""Buy on gap and its short-on-gap mirror, *Algorithmic Trading*'s Example 4.1.

Daily closes of a stock follow something close to a random walk, but Chan
argues at Kindle location 1948 that the open can overshoot. On a morning when
index futures are down, some stocks open far below the previous day's low
under panic selling, and drift back up once it is over. So each day the rule
buys at the open the ten stocks that dropped furthest below their previous low,
by more than one 90-day standard deviation of their daily returns, provided the
open is still above the 20-day moving average of closes, and sells them at the
same day's close. At location 1974 Chan reports an APR of 8.7 percent and a
Sharpe ratio of 1.5 from 2006-05-11 to 2012-04-24, on an S&P 500 "that has
survivorship bias". At location 1993 he reports the mirror image, shorting
stocks that open a standard deviation above the previous day and are still
below their moving average, at an APR of 46 percent and a Sharpe ratio of
1.27, with a steeper drawdown.

**The transcription.** Every step of the buy side is Chan's ``bog.m`` and the
helpers it calls, read under ``archived/matlab/`` in the mirror
[ivanliu1989/algorithmic_trading](https://github.com/ivanliu1989/algorithmic_trading)
at ``45670240f1f3d4b5233a75f82fd18b742455b4bb``. The mirror
[ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) at
``e4bc46f`` holds the same ``bog.m`` under ``public/img/book2/``, the same git
blob. Where ``op``, ``lo`` and ``cl`` are the open, low and close:

1. ``stdretC2C90d`` is book two's ``smartMovingStd`` over 90 rows of
   ``calculateReturns(cl, 1)``, moved one row later, so day t reads the
   returns ending at t − 1.
2. ``buyPrice = backshift(1, lo) · (1 − stdretC2C90d)``, and the drop is
   ``(op − backshift(1, lo)) / backshift(1, lo)``.
3. ``ma`` is ``smartMovingAvg`` over 20 rows of ``cl``, moved one row later.
4. A stock qualifies when its drop is finite, ``op < buyPrice`` and
   ``op > ma``. The qualifiers are sorted by drop, deepest first, ties in
   column order, and the first ten get a position of 1. The comparison is made
   against ``buyPrice`` as the script writes it. On this file it selects the
   same 972 qualifiers as comparing the drop against the spread.
5. The day's return is the sum over stocks of position times
   ``(cl − op) / op``, skipping a product that is not finite, divided by 10,
   and a day that summed nothing is set to 0.

The divisor is 10 whatever the day's count, so a day with three qualifiers
holds three tenths of the book and leaves the rest idle. Example 7.2's fixed
30 is the same choice.

``bog.m`` prints two figures, and :class:`Side` carries both.

1. ``prod(1 + ret)^(252 / n) − 1`` over all 1,500 days, the compounded APR.
   The script labels it APR and its closing comment gives 8.7 percent.
2. ``mean(ret) · √252 / std(ret)``, the Sharpe ratio, with MATLAB's own
   ``std``, which divides by n − 1. That is
   :func:`chan.khandani_lo.plain_sharpe` exactly, so it is called rather than
   written a third time. It refuses a NaN, which holds the script's zero-fill
   in place.

Three more are reported beside them.

1. ``252 · mean(ret)``, the arithmetic annual return, because location 3509
   calls the same 8.7 percent an "annualized average return", which named the
   arithmetic figure in Example 7.2. Here it is 0.085279 and does not reach
   8.7, so the 8.7 is the compounded figure under a second name.
2. and 3. The deepest drawdown and its duration, from book two's
   ``calculateMaxDD``, for location 1993's steeper drawdown.

**The mirror has no script, and its rule was declared before any run.**
[Issue 295](https://github.com/l3a0/quantitative-trading/issues/295) read it
from location 1993's sentence and took ``bog.m``'s choice reversed wherever
the sentence is silent. The jump is measured from the previous day's high, and
a stock qualifies when ``op > backshift(1, hi) · (1 + stdretC2C90d)`` and
``op < ma``. The ten largest jumps are shorted, ties in column order, and
everything else is ``bog.m``. Two things in Chan's book-two code point at the
high.

1. ``bog.m`` loads ``hi`` and never reads it.
2. ``gapFutures_FSTX.m`` measures a jump up from ``backshift(1, hi)``.

Two other readings of the sentence were named on the issue and are not run.

1. A jump measured from the previous close.
2. Shorting the smallest qualifying jumps first.

The declared rule lands far from Chan's figures, and the issue's rule is that
no second reading is tried after a miss, because choosing a reading once its
number is seen is a search.

**The helper choice moves both printed figures.** ``smartMovingStd`` calls book
two's ``smartstd``, which skips a missing return and divides by n. With the
first edition's, which zero-fills and divides by n − 1, the APR becomes
0.083629 and the Sharpe ratio 1.6503, which round to 8.4 and 1.7 rather than
Chan's 8.7 and 1.5. ``tests/test_buy_on_gap.py`` pins both.

**A late listing can trade on a thin spread, and that is Chan's code.**
:func:`chan.matlab_helpers.smart_moving_std` gives a spread from whatever
returns a window holds, so a stock listed inside the window reaches the rule
before 90 returns stand behind it. Three positions on this file rest on fewer
than 90, CFN and MPC on the buy side and DPS on the short side, and none on a
spread of 0.

**The vintage.** ``inputdataohlcdaily_stocks_20120424/``, the 497 stocks of
Chan's ``inputDataOHLCDaily_stocks_20120424.mat``, read for the open, high,
low and close through :func:`chan.series.load_panel`, which hashes each member
against its manifest entry before parsing it. ``bog.m`` loads
``inputDataOHLCDaily_20120424``, with no ``_stocks``. EpchanPreview at
``e4bc46f`` ships a file of exactly that name, under
``public/img/book3/Chap3 Time Series/``, and it is the same git blob as the
``_stocks`` file, with the sha256 ``data/README.md`` records for it. Neither
public mirror holds another file of that name. That shows what the name
points at in the code Chan published, not that the file he ran in 2012 is the
one he later shipped under it.

**Every figure here is about survivors.** The price file is the S&P 500 as
Chan held it on 2012-04-24, carried backwards, and location 1974 says so.

**The scale-break guard is not called, and issue 295 decided that.**
:func:`chan.series.refuse_window_crossing_a_break` flags 30 days in 17 of this
file's stocks, every one between 2007 and 2009, and this window holds all 30,
so calling it the way :mod:`chan.pead` does would refuse the run. Issues 18,
21 and 22 each declined it because the job is to reproduce what Chan's script
computed on the prices as they stand, and that holds here. Issue 250 measured
that none of the 30 sits near a split, so they read as real moves. One
position lands on one, a short in MS on 2008-10-13.
``TestTheScaleBreakDecision`` runs the guard and holds both facts.

**What changed on the way over from** ``bog.m``. Four things, and none moves a
figure.

1. The file is read as committed vintages through
   :func:`chan.series.load_panel` rather than loaded from the ``.mat``.
2. ``plot(cumret)`` is not carried. The run prints and draws nothing.
3. The arithmetic return and the drawdown are computed beside the script's
   two figures.
4. The mirror runs beside it, under the rule the issue declared.

Every result here is exploratory. Reproducing Chan's figures spends the 2006
to 2012 sample on a rule he chose, so the run says whether his numbers
reproduce on his file and nothing about whether the rule pays today. The
mirror's rule was declared before its numbers were seen, but it is a reading
of one sentence rather than a hypothesis tested on held-out data, so it is
exploratory too.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from chan.khandani_lo import plain_sharpe
from chan.matlab_helpers import (
    backshift,
    calculate_max_dd,
    calculate_returns,
    matlab_sort,
    smart_moving_avg,
    smart_moving_std,
    smartsum,
)
from chan.series import load_panel, panel_line
from chan.vintage import VintageEntry, VintageUnavailable

PRICE_FILE = "inputDataOHLCDaily_stocks_20120424.mat"
#: The name ``bog.m`` loads, which is the same bytes as :data:`PRICE_FILE`.
SCRIPT_PRICE_FILE = "inputDataOHLCDaily_20120424"

#: ``topN`` in ``bog.m``: the most positions on one day, and the divisor on every day.
TOP_N = 10
#: ``entryZscore``: how many moving standard deviations the open must clear.
ENTRY_ZSCORE = 1
#: ``lookback``: the rows in the moving average of closes.
AVERAGE_LOOKBACK = 20
#: The rows in the moving standard deviation of close-to-close returns.
SPREAD_LOOKBACK = 90
#: The annualisation in both figures ``bog.m`` prints.
TRADING_DAYS = 252

#: What location 1974 and ``bog.m``'s closing comment print for buy on gap.
BOOK_APR_PERCENT = 8.7
BOOK_SHARPE = 1.5
SCRIPT_COMMENT = "APR=8.7%, Sharpe=1.5"
#: What ``bog.m`` prints for its window, ``tday(1)`` and ``tday(end)``.
SCRIPT_WINDOW = "20060511 - 20120424"
#: What location 1993 prints for the mirror, which has no script.
MIRROR_BOOK_APR_PERCENT = 46
MIRROR_BOOK_SHARPE = 1.27


@dataclass(frozen=True)
class Side:
    """One side of the strategy over the panel's days.

    ``positions`` is each stock's 1, −1 or 0 on each day and ``daily`` each
    day's return over :data:`TOP_N`, with a day that summed nothing set to 0
    as ``bog.m`` sets it. The first two figures are the two ``bog.m`` prints.
    The rest are reported beside them.
    """

    name: str
    days: pd.DatetimeIndex
    positions: np.ndarray
    daily: np.ndarray
    apr: float
    sharpe: float
    arithmetic_annual: float
    max_drawdown: float
    max_drawdown_days: int

    @property
    def trades(self) -> int:
        return int(np.count_nonzero(self.positions))

    @property
    def days_held(self) -> int:
        return int((np.count_nonzero(self.positions, axis=1) > 0).sum())

    @property
    def most_held(self) -> int:
        return int(np.count_nonzero(self.positions, axis=1).max())


def entry_spread(closes: np.ndarray) -> np.ndarray:
    """``stdretC2C90d``: the 90-row moving deviation of close-to-close returns, one row later.

    Day t reads the returns ending at t − 1, through book two's ``smartstd``,
    so a window with fewer finite returns than rows still gives a spread.
    """
    return backshift(1, smart_moving_std(calculate_returns(closes, 1), SPREAD_LOOKBACK))


def trailing_average(closes: np.ndarray) -> np.ndarray:
    """``ma``: the mean of the finite closes over the 20 rows ending at t − 1."""
    return backshift(1, smart_moving_avg(closes, AVERAGE_LOOKBACK))


def drop_qualifiers(
    opens: np.ndarray, lows: np.ndarray, spread: np.ndarray, average: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """``bog.m``'s ``hasData``: which stocks qualify each day, and each drop below the previous low.

    A stock qualifies when its drop is finite, its open is strictly below
    ``buyPrice`` and strictly above the moving average. The comparison is
    against ``buyPrice`` as ``bog.m`` writes it, not against the drop over the
    spread, which is the same in algebra and not always in floating point. A
    NaN on either side of a comparison qualifies nothing, as in MATLAB.
    """
    previous = backshift(1, lows)
    with np.errstate(invalid="ignore", divide="ignore"):
        buy_price = previous * (1 - ENTRY_ZSCORE * spread)
        drop = (opens - previous) / previous
        qualifies = np.isfinite(drop) & (opens < buy_price) & (opens > average)
    return qualifies, drop


def jump_qualifiers(
    opens: np.ndarray, highs: np.ndarray, spread: np.ndarray, average: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """The declared mirror: which stocks qualify each day, and each jump above the previous high.

    A stock qualifies when its jump is finite, its open is strictly above the
    previous high times one plus the spread, and strictly below the moving
    average.
    """
    previous = backshift(1, highs)
    with np.errstate(invalid="ignore", divide="ignore"):
        sell_price = previous * (1 + ENTRY_ZSCORE * spread)
        jump = (opens - previous) / previous
        qualifies = np.isfinite(jump) & (opens > sell_price) & (opens < average)
    return qualifies, jump


def gap_down_positions(
    opens: np.ndarray, lows: np.ndarray, spread: np.ndarray, average: np.ndarray
) -> np.ndarray:
    """``positionTable``: a 1 on each of the day's ten deepest qualifying drops, from row two."""
    qualifies, drop = drop_qualifiers(opens, lows, spread, average)
    return _ranked(qualifies, drop, 1.0)


def gap_up_positions(
    opens: np.ndarray, highs: np.ndarray, spread: np.ndarray, average: np.ndarray
) -> np.ndarray:
    """The mirror's selection: a −1 on each of the day's ten largest qualifying jumps.

    Ranking by the negated jump puts the largest first and keeps ties in
    column order.
    """
    qualifies, jump = jump_qualifiers(opens, highs, spread, average)
    return _ranked(qualifies, -jump, -1.0)


def _ranked(qualifies: np.ndarray, key: np.ndarray, sign: float) -> np.ndarray:
    """``bog.m``'s loop: from the second row, sort the qualifiers by ``key`` and keep ``topN``."""
    positions = np.zeros(qualifies.shape)
    for t in range(1, len(qualifies)):
        held = np.flatnonzero(qualifies[t])
        order = matlab_sort(key[t, held])
        positions[t, held[order[:TOP_N]]] = sign
    return positions


def daily_returns(positions: np.ndarray, opens: np.ndarray, closes: np.ndarray) -> np.ndarray:
    """``ret``: the day's open-to-close return on the positions, over ten, NaN set to 0."""
    with np.errstate(invalid="ignore", divide="ignore"):
        daily = smartsum(positions * (closes - opens) / opens, axis=1) / TOP_N
    return np.where(np.isnan(daily), 0.0, daily)


def figures(name: str, days: pd.DatetimeIndex, positions: np.ndarray, daily: np.ndarray) -> Side:
    """``bog.m``'s APR and Sharpe ratio, and the three figures reported beside them."""
    max_dd, max_ddd = calculate_max_dd(np.cumprod(1 + daily) - 1)
    return Side(
        name=name,
        days=days,
        positions=positions,
        daily=daily,
        apr=float(np.prod(1 + daily) ** (TRADING_DAYS / len(daily)) - 1),
        sharpe=plain_sharpe(daily),
        arithmetic_annual=float(TRADING_DAYS * daily.mean()),
        max_drawdown=max_dd,
        max_drawdown_days=max_ddd,
    )


def _arrays(*frames: pd.DataFrame) -> list[np.ndarray]:
    first = frames[0]
    if not all(f.index.equals(first.index) and f.columns.equals(first.columns) for f in frames):
        raise ValueError("the price frames must share one index and one column order")
    return [f.to_numpy(dtype=float) for f in frames]


def buy_on_gap(opens: pd.DataFrame, lows: pd.DataFrame, closes: pd.DataFrame) -> Side:
    """Run ``bog.m`` on three date-by-stock frames sharing one index and one column order."""
    op, lo, cl = _arrays(opens, lows, closes)
    positions = gap_down_positions(op, lo, entry_spread(cl), trailing_average(cl))
    return figures("buy on gap", opens.index, positions, daily_returns(positions, op, cl))


def short_on_gap(opens: pd.DataFrame, highs: pd.DataFrame, closes: pd.DataFrame) -> Side:
    """Run the mirror issue 295 declared on three frames sharing one index and column order."""
    op, hi, cl = _arrays(opens, highs, closes)
    positions = gap_up_positions(op, hi, entry_spread(cl), trailing_average(cl))
    return figures("short on gap", opens.index, positions, daily_returns(positions, op, cl))


def read_sources(
    data_dir: Path | None = None,
) -> tuple[list[VintageEntry], dict[str, pd.DataFrame]]:
    """The panel's members and its four price fields, each a date-by-symbol frame."""
    frames = {}
    for field in ("Open", "High", "Low", "Close"):
        members, frames[field] = load_panel(PRICE_FILE, field=field, data_dir=data_dir)
    return members, frames


def report(members: list[VintageEntry], long: Side, short: Side) -> None:
    """Print the source, the rules, and each figure beside what Chan printed."""
    print("Buy on gap and its mirror, Chan's Example 4.1 in Algorithmic Trading")
    print(f"  prices   {panel_line(members)}, the Open, High, Low and Close columns")
    print(
        f"  window   {long.days[0].strftime('%Y%m%d')} - {long.days[-1].strftime('%Y%m%d')}, "
        f"{len(long.days)} trading days, {long.positions.shape[1]} stocks"
    )
    print(
        f"  long     open below the previous low by more than {ENTRY_ZSCORE} {SPREAD_LOOKBACK}-day "
        f"std and above the {AVERAGE_LOOKBACK}-day average, the {TOP_N} deepest, out at the close"
    )
    print(
        f"  short    open above the previous high by more than {ENTRY_ZSCORE} "
        f"{SPREAD_LOOKBACK}-day std and below the {AVERAGE_LOOKBACK}-day average, "
        f"the {TOP_N} highest, out at the close."
    )
    print("           The book prints no script for it. Issue 295 declared it before any run.")
    for side in (long, short):
        print(
            f"  sizing   {side.name}: each day's sum over {TOP_N}. {side.trades} positions on "
            f"{side.days_held} days, at most {side.most_held} on one."
        )
    print()
    rows = [
        (
            "Buy on gap, APR",
            f"{long.apr:.6f}",
            f"{long.apr:10.4f}".strip(),
            "8.7%",
            f"{BOOK_APR_PERCENT} percent",
        ),
        (
            "Buy on gap, Sharpe ratio",
            f"{long.sharpe:.4f}",
            f"{long.sharpe:4.2f}",
            "1.5",
            f"{BOOK_SHARPE}",
        ),
        (
            "Buy on gap, 252 x mean",
            f"{long.arithmetic_annual:.6f}",
            "none",
            "none",
            f"{BOOK_APR_PERCENT} percent",
        ),
        (
            "Short on gap, APR",
            f"{short.apr:.6f}",
            f"{short.apr:10.4f}".strip(),
            "none",
            f"{MIRROR_BOOK_APR_PERCENT} percent",
        ),
        (
            "Short on gap, Sharpe ratio",
            f"{short.sharpe:.4f}",
            f"{short.sharpe:4.2f}",
            "none",
            f"{MIRROR_BOOK_SHARPE}",
        ),
        ("Short on gap, 252 x mean", f"{short.arithmetic_annual:.6f}", "none", "none", "none"),
        ("Buy on gap, maximum drawdown", f"{long.max_drawdown:.6f}", "none", "none", "none"),
        ("Short on gap, maximum drawdown", f"{short.max_drawdown:.6f}", "none", "none", "steeper"),
    ]
    print(f"  {'Figure':<32} {'Computed':>10} {'Prints as':>10} {'bog.m':>8} {'Book':>12}")
    for label, computed, printed, script, book in rows:
        print(f"  {label:<32} {computed:>10} {printed:>10} {script:>8} {book:>12}")
    print()
    print(
        "  The price file holds only the stocks in the index on 2012-04-24, "
        "so every figure above is about survivors."
    )
    print(
        "  Exploratory. Reproducing Chan's figures spends the 2006 to 2012 sample on a rule he "
        "chose, so this says whether"
    )
    print(
        "  his numbers reproduce on his file and nothing about whether the rule pays today. "
        "docs/replication-log.md Entry 17 carries the verdicts."
    )


def both_sides(data_dir: Path | None = None) -> tuple[list[VintageEntry], Side, Side]:
    """Read the panel and run both sides, printing nothing."""
    members, frames = read_sources(data_dir)
    long = buy_on_gap(frames["Open"], frames["Low"], frames["Close"])
    short = short_on_gap(frames["Open"], frames["High"], frames["Close"])
    return members, long, short


def run(data_dir: Path | None = None) -> tuple[Side, Side]:
    """Read the panel, run both sides and print the report."""
    members, long, short = both_sides(data_dir)
    report(members, long, short)
    return long, short


def main() -> None:
    argparse.ArgumentParser(
        description="Buy on gap and its mirror on Chan's own file, Example 4.1 of "
        "Algorithmic Trading"
    ).parse_args()
    try:
        run()
    except VintageUnavailable as refused:
        # A refusal that names the source is worth nothing at the bottom of a
        # traceback, so it reaches the reader as one line, the way
        # chan.pead.main does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
