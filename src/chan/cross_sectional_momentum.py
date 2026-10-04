"""Cross-sectional momentum on Chan's 2012 S&P 500 file, *Algorithmic Trading*'s Example 6.2.

Stocks that rose most over the past year tend to keep rising for a while, and
those that fell most tend to keep falling. Chan trades that by buying the
strongest stocks and shorting the weakest. At Kindle location 2800 he reports
an APR of 37 percent and a Sharpe ratio of 4.1 from 2007-05-15 to 2007-12-31,
and −30 percent from 2008-01-02 to 2009-12-31. The script the example names,
``kentdaniel.m``, prints a Sharpe ratio of 0.40 over the same 2007 window, a
tenth of the book's. This module reproduces the script and then runs four
readings, declared on
[issue 297](https://github.com/l3a0/quantitative-trading/issues/297) before any
of them was computed, that could explain the gap.

**The transcription.** Every step is Chan's ``kentdaniel.m`` and the helpers
it calls, read under ``archived/matlab/`` in the mirror
[ivanliu1989/algorithmic_trading](https://github.com/ivanliu1989/algorithmic_trading)
at ``45670240f1f3d4b5233a75f82fd18b742455b4bb``. The mirror
[ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) at
``e4bc46f`` holds the same file under ``public/img/book2/``, byte for byte.
Where ``cl`` is the close and t counts rows from 0:

1. ``ret = cl(t) / cl(t − 252) − 1``, each stock's return over 252 rows. The
   script's comment on that line calls it a daily return, which it is not.
2. On every row from 252 on, the 50 stocks with the highest finite ``ret`` are
   marked long and the 50 lowest short, in the order MATLAB's ``sort`` gives.
3. Each row's marks are held for 25 rows, so a stock's position is the number
   of the last 25 rows that marked it long less the number that marked it
   short, between −25 and +25.
4. The day's return is the sum over stocks of yesterday's position times
   today's close-to-close return, skipping a product that is not finite,
   divided by 2 · 50 and by 25, with a NaN day set to 0.
5. Over a window's rows, ``kentdaniel.m`` prints ``252 · smartmean``,
   ``√252 · smartmean / smartstd``, ``prod(1 + r)^(252/n) − 1``, and book two's
   ``calculateMaxDD`` on ``cumprod(1 + r) − 1``.

The 2007 window, rows 253 to 412, opens the day after the first row any stock
is marked, so its first 24 days hold fewer than 25 cohorts while the script
still divides by 25.

**The book's APR is the arithmetic figure.** Entry 12 found that Example 7.2's
"APR of 6.7 percent" is ``pead.m``'s ``252 · smartmean``, not its compounded
figure, so the book's 37 and −30 percent are set against the arithmetic
return here, and the compounded one is reported beside them.

**The readings.** :data:`READINGS` holds the script as printed and four
variants, each changing one thing, and the report always runs all five. The
rule's numbers are module constants and no argument varies them, so trying a
sixth reading is an edit that shows in a diff.

- R0 is the script as printed.
- R1 holds one portfolio at a time, formed on row 252 and every 25th row
  after, divided by 2 · 50.
- R2 ranks on ``cl(t − 21) / cl(t − 252) − 1``, skipping the latest 21 rows.
- R3 drops the one-row lag on the daily return, so a cohort earns the day it
  was formed on. It looks ahead.
- R4 divides each day by 2 · 50 times the cohorts actually held, rather than
  by 2 · 50 · 25.

A reading lands the book when its 2007 arithmetic return rounds to 37 percent
and its 2007 Sharpe ratio rounds to 4.1, both rounded half away from zero as
MATLAB rounds. :func:`lands_the_book` is that test.

**What changed on the way over from** ``kentdaniel.m``. Five things, and none
moves a figure.

1. The closes are read as committed vintages through
   :func:`chan.series.load_panel` rather than loaded from the ``.mat`` file.
2. ``longs`` is preallocated. The script's line that would preallocate it was
   swallowed by the comment on the line before, so MATLAB grows it row by row.
   It still ends with every row, so its logical indexing lands on the same
   cells.
3. ``lag(cl)`` is :func:`chan.matlab_helpers.lag1`. Neither mirror ships a
   ``lag.m``. The first edition's ``lag1.m`` defines ``lag`` as a one-row
   shift padded with NaN, and the printed figures reproducing confirms it.
4. A row with fewer than 50 returns that are not NaN is refused, where MATLAB
   would stop on an index below 1. No row of Chan's file comes near that.
5. ``plot(cumret)`` is not carried. The run prints and draws nothing.

**The scale-break guard is not called.** The 30 days the guard flags in this
file all fall in 2007 to 2009. ETFC's 2007-11-12 is inside the 2007 window and
the other 29 inside 2008 and 2009, so the guard :mod:`chan.pead` calls would
refuse both. The script ran on these closes as they stand, and a momentum
ranking is meant to see a real collapse, which is the decision
:mod:`chan.momentum_factor` recorded. The comment above
``FLAGGED_IN_CHANS_MAT_FILES`` in ``tests/test_scale_breaks.py`` records it.

**Every figure here is about survivors.** The file is the S&P 500 as Chan held
it on 2012-04-24, carried backwards, so every stock in it survived 2008 and
2009. That reaches the two legs in opposite directions. The short leg lacks
stocks that fell and then left the index, which pushes the strategy down, and
the long leg lacks past winners that later collapsed out of it, which pushes
it up. Which dominates is not measured here.

Every result here is exploratory. Reproducing Chan's figures spends the 2007
to 2012 sample on a rule he chose, and a reading that lands is an explanation
found by a search over four, so the run says whether his numbers reproduce on
his file and nothing about whether momentum pays today.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from chan.matlab_helpers import (
    backshift,
    calculate_max_dd,
    lag1,
    matlab_sort,
    round_half_away,
    smartmean,
    smartstd_book_two,
    smartsum,
)
from chan.series import load_panel, panel_line
from chan.vintage import VintageEntry, VintageUnavailable

PRICE_FILE = "inputDataOHLCDaily_stocks_20120424.mat"

#: ``lookback`` in ``kentdaniel.m``, the rows each ranking return spans.
LOOKBACK = 252
#: ``holddays``, the rows each day's marks are held.
HOLD_DAYS = 25
#: ``topN``, the stocks marked long and the stocks marked short each day.
TOP_N = 50
#: R2's skip, one month of rows, so the ranking return ends a month back.
SKIP = 21
#: The annualisation in every figure ``kentdaniel.m`` prints.
TRADING_DAYS = 252

#: The script's three windows, lines 11 and 12 active and the other two
#: commented out. Each is named by the book figure it carries.
WINDOWS = {
    "2007": ("2007-05-15", "2007-12-31"),
    "2008-2009": ("2008-01-02", "2009-12-31"),
    "2010-2012": ("2010-01-04", "2012-04-24"),
}

#: What the book prints at location 2800. Each APR is the arithmetic figure.
BOOK_APR_PERCENT = 37
BOOK_SHARPE = 4.1
BOOK_CRISIS_APR_PERCENT = -30

#: What ``kentdaniel.m`` prints for the 2007 window, in its comment lines, at
#: the precision its ``fprintf`` formats give each figure.
SCRIPT_ARITHMETIC = "0.0315"
SCRIPT_SHARPE = "0.40"
SCRIPT_APR = "0.0288"
SCRIPT_MAX_DD = "-0.066923"
SCRIPT_MAX_DDD = 182


@dataclass(frozen=True)
class Figures:
    """The five figures ``kentdaniel.m`` prints, over one window's ``days``."""

    days: pd.DatetimeIndex
    arithmetic_annual: float
    sharpe: float
    compounded_apr: float
    max_drawdown: float
    max_drawdown_days: int


def ranking_returns(closes: np.ndarray) -> np.ndarray:
    """Line 21: each stock's return over :data:`LOOKBACK` rows."""
    return _ranking(closes, skip=0)


def lagged_ranking_returns(closes: np.ndarray) -> np.ndarray:
    """R2: the return from :data:`LOOKBACK` rows back to :data:`SKIP` rows back."""
    return _ranking(closes, skip=SKIP)


def _ranking(closes: np.ndarray, skip: int) -> np.ndarray:
    then = backshift(LOOKBACK, closes)
    with np.errstate(invalid="ignore", divide="ignore"):
        return backshift(skip, closes) / then - 1


def formations(ranking: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Lines 25 to 31: each row's :data:`TOP_N` highest returns long and lowest short.

    Rows before :data:`LOOKBACK` mark nothing. A NaN return is dropped from the
    order rather than ranked, so a stock with no return on a row is never
    marked on it.
    """
    longs = np.zeros(ranking.shape, dtype=bool)
    shorts = np.zeros(ranking.shape, dtype=bool)
    for t in range(LOOKBACK, len(ranking)):
        order = matlab_sort(ranking[t])
        order = order[~np.isnan(ranking[t, order])]
        if len(order) < TOP_N:
            raise ValueError(
                f"row {t} holds {len(order)} returns that are not NaN, fewer than the {TOP_N} "
                "kentdaniel.m marks on each side"
            )
        longs[t, order[-TOP_N:]] = True
        shorts[t, order[:TOP_N]] = True
    return longs, shorts


def overlapping_positions(longs: np.ndarray, shorts: np.ndarray) -> np.ndarray:
    """Lines 33 to 44: each stock's marks summed over the last :data:`HOLD_DAYS` rows."""
    marks = longs.astype(float) - shorts.astype(float)
    positions = np.zeros_like(marks)
    for held in range(HOLD_DAYS):
        positions += np.nan_to_num(backshift(held, marks))
    return positions


def one_cohort_positions(longs: np.ndarray, shorts: np.ndarray) -> np.ndarray:
    """R1: the marks of the latest formation row, formed every :data:`HOLD_DAYS` rows.

    The first formation is row :data:`LOOKBACK`, the first row marked, so no
    phase is chosen.
    """
    marks = longs.astype(float) - shorts.astype(float)
    positions = np.zeros_like(marks)
    for formed in range(LOOKBACK, len(marks), HOLD_DAYS):
        positions[formed : formed + HOLD_DAYS] = marks[formed]
    return positions


def cohorts_held(rows: int) -> np.ndarray:
    """How many cohorts line 46's lagged positions hold on each row, at most :data:`HOLD_DAYS`."""
    return np.clip(np.arange(rows) - LOOKBACK, 0, HOLD_DAYS)


def daily_returns(
    positions: np.ndarray, closes: np.ndarray, divisor: float | np.ndarray, lag: int = 1
) -> np.ndarray:
    """Lines 46 and 48: positions ``lag`` rows back times today's return, summed, over ``divisor``.

    A row with nothing finite to sum, or a divisor of 0, returns 0, which is
    what line 48 makes of a NaN.
    """
    previous = lag1(closes)
    with np.errstate(invalid="ignore", divide="ignore"):
        daily = smartsum(backshift(lag, positions) * (closes - previous) / previous, axis=1)
        daily = daily / divisor
    return np.where(np.isfinite(daily), daily, 0.0)


def script_as_printed(closes: np.ndarray) -> np.ndarray:
    """R0, ``kentdaniel.m`` as printed."""
    longs, shorts = formations(ranking_returns(closes))
    return daily_returns(overlapping_positions(longs, shorts), closes, 2 * TOP_N * HOLD_DAYS)


def one_portfolio_at_a_time(closes: np.ndarray) -> np.ndarray:
    """R1, one cohort held at a time rather than 25 overlapping."""
    longs, shorts = formations(ranking_returns(closes))
    return daily_returns(one_cohort_positions(longs, shorts), closes, 2 * TOP_N)


def lagged_lookback(closes: np.ndarray) -> np.ndarray:
    """R2, the ranking return ending :data:`SKIP` rows back."""
    longs, shorts = formations(lagged_ranking_returns(closes))
    return daily_returns(overlapping_positions(longs, shorts), closes, 2 * TOP_N * HOLD_DAYS)


def same_day_alignment(closes: np.ndarray) -> np.ndarray:
    """R3, today's positions earning today's return, which looks ahead."""
    longs, shorts = formations(ranking_returns(closes))
    positions = overlapping_positions(longs, shorts)
    return daily_returns(positions, closes, 2 * TOP_N * HOLD_DAYS, lag=0)


def divided_by_cohorts_held(closes: np.ndarray) -> np.ndarray:
    """R4, each day over the cohorts it actually holds rather than over 25."""
    longs, shorts = formations(ranking_returns(closes))
    divisor = 2 * TOP_N * cohorts_held(len(closes))
    return daily_returns(overlapping_positions(longs, shorts), closes, divisor)


#: The closed set the report runs, in the order issue 297 declared them.
READINGS: dict[str, tuple[str, Callable[[np.ndarray], np.ndarray]]] = {
    "R0": ("the script as printed", script_as_printed),
    "R1": ("one portfolio at a time", one_portfolio_at_a_time),
    "R2": ("a lookback skipping 21 rows", lagged_lookback),
    "R3": ("same-day alignment", same_day_alignment),
    "R4": ("divided by the cohorts held", divided_by_cohorts_held),
}


def window_figures(
    daily: np.ndarray,
    days: pd.DatetimeIndex,
    window: str,
    smartstd: Callable[[np.ndarray], float] = smartstd_book_two,
) -> Figures:
    """Lines 50 to 58: the five figures over one of :data:`WINDOWS`.

    ``smartstd`` is book two's, which ``kentdaniel.m`` calls. The tests swap in
    the first edition's to show what that would move.
    """
    start, end = (pd.Timestamp(each) for each in WINDOWS[window])
    inside = (days >= start) & (days <= end)
    r = daily[inside]
    mean = float(smartmean(r))
    max_dd, max_ddd = calculate_max_dd(np.cumprod(1 + r) - 1)
    return Figures(
        days=days[inside],
        arithmetic_annual=TRADING_DAYS * mean,
        sharpe=float(np.sqrt(TRADING_DAYS) * mean / smartstd(r)),
        compounded_apr=float(np.prod(1 + r) ** (TRADING_DAYS / len(r)) - 1),
        max_drawdown=max_dd,
        max_drawdown_days=max_ddd,
    )


def lands_the_book(figures: Figures) -> bool:
    """Whether a 2007 window's figures round to the book's 37 percent and 4.1."""
    return bool(
        round_half_away(100 * figures.arithmetic_annual) == BOOK_APR_PERCENT
        and round_half_away(10 * figures.sharpe) == round(10 * BOOK_SHARPE)
    )


def lands_the_crisis(figures: Figures) -> bool:
    """Whether a 2008 and 2009 window's arithmetic return rounds to the book's −30 percent."""
    return bool(round_half_away(100 * figures.arithmetic_annual) == BOOK_CRISIS_APR_PERCENT)


def stabilised(later: Figures, first: Figures) -> bool:
    """Location 2800's claim that the return after 2009 "did stabilize, though it
    hasn't returned to its former high level yet".

    It holds when the later window's arithmetic return is at least 0 and below
    the first window's, both from the same reading.
    """
    return 0 <= later.arithmetic_annual < first.arithmetic_annual


def read_closes(data_dir: Path | None = None) -> tuple[list[VintageEntry], pd.DataFrame]:
    """The committed closes of Chan's 2012 file, one column per stock."""
    return load_panel(PRICE_FILE, field="Close", data_dir=data_dir)


def momentum(closes: pd.DataFrame) -> dict[str, dict[str, Figures]]:
    """Every reading over every window, keyed by reading and then by window."""
    values = closes.to_numpy(dtype=float)
    days = pd.DatetimeIndex(closes.index)
    results = {}
    for name, (_, rule) in READINGS.items():
        daily = rule(values)
        results[name] = {window: window_figures(daily, days, window) for window in WINDOWS}
    return results


def report(members: list[VintageEntry], results: dict[str, dict[str, Figures]]) -> None:
    """Print the source, the script's five figures beside Chan's, then every reading."""
    script = results["R0"]["2007"]
    print("Cross-sectional momentum, Chan's Example 6.2 in Algorithmic Trading")
    print(f"  closes   {panel_line(members)}, the Close column")
    print(
        f"  rule     the {TOP_N} highest and {TOP_N} lowest {LOOKBACK}-day returns, long and "
        f"short, each day's marks held {HOLD_DAYS} days"
    )
    for window, (start, end) in WINDOWS.items():
        days = results["R0"][window].days
        print(f"  window   {window:<10} {start} to {end}, {len(days)} trading days")
    print()
    print("The script as printed, over 2007")
    rows = [
        (
            "Arithmetic annual return, 252 x mean",
            f"{script.arithmetic_annual:.6f}",
            f"{script.arithmetic_annual:7.4f}".strip(),
            SCRIPT_ARITHMETIC,
            f"{BOOK_APR_PERCENT} percent",
        ),
        (
            "Sharpe ratio, sqrt(252) x mean / std",
            f"{script.sharpe:.4f}",
            f"{script.sharpe:4.2f}",
            SCRIPT_SHARPE,
            f"{BOOK_SHARPE}",
        ),
        (
            "Compounded APR",
            f"{script.compounded_apr:.6f}",
            f"{script.compounded_apr:10.4f}".strip(),
            SCRIPT_APR,
            "none",
        ),
        (
            "Maximum drawdown",
            f"{script.max_drawdown:.6f}",
            f"{script.max_drawdown:f}",
            SCRIPT_MAX_DD,
            "none",
        ),
        (
            "Maximum drawdown duration, days",
            f"{script.max_drawdown_days}",
            f"{script.max_drawdown_days}",
            f"{SCRIPT_MAX_DDD}",
            "none",
        ),
    ]
    print(f"  {'Figure':<38} {'Computed':>10} {'Prints as':>10} {'script':>10} {'Book':>12}")
    for label, computed, printed, line, book in rows:
        print(f"  {label:<38} {computed:>10} {printed:>10} {line:>10} {book:>12}")
    print()
    print(
        f"The readings, arithmetic annual return and Sharpe ratio. The book prints "
        f"{BOOK_APR_PERCENT} percent and {BOOK_SHARPE} for 2007, and "
        f"{BOOK_CRISIS_APR_PERCENT} percent for 2008 and 2009."
    )
    print(f"  {'Reading':<34} " + " ".join(f"{window:>19}" for window in WINDOWS) + "  lands")
    for name, (label, _) in READINGS.items():
        cells = " ".join(
            f"{results[name][window].arithmetic_annual:>10.4f}{results[name][window].sharpe:>9.4f}"
            for window in WINDOWS
        )
        landed = "yes" if lands_the_book(results[name]["2007"]) else "no"
        print(f"  {name} {label:<31} {cells}  {landed}")
    print()
    landed = [name for name in READINGS if lands_the_book(results[name]["2007"])]
    print(f"  Readings landing 37 percent and 4.1 together: {', '.join(landed) or 'none'}.")
    crisis = results["R0"]["2008-2009"]
    print(
        f"  The script's 2008 and 2009 arithmetic return rounds to -30 percent: "
        f"{'yes' if lands_the_crisis(crisis) else 'no'}."
    )
    print(
        "  The return after 2009 stabilised below its 2007 level: "
        f"{'yes' if stabilised(results['R0']['2010-2012'], script) else 'no'}."
    )
    print()
    print(
        "  The file holds only the stocks in the index on 2012-04-24, "
        "so every figure above is about survivors."
    )
    print(
        "  Exploratory. Reproducing Chan's figures spends the 2007 to 2012 sample on a rule he "
        "chose, so this says whether"
    )
    print(
        "  his numbers reproduce on his file and nothing about whether momentum pays today. "
        "docs/replication-log.md carries the verdicts."
    )


def run(data_dir: Path | None = None) -> dict[str, dict[str, Figures]]:
    """Read the closes, run every reading over every window, and print the report."""
    members, closes = read_closes(data_dir)
    results = momentum(closes)
    report(members, results)
    return results


def main() -> None:
    argparse.ArgumentParser(
        description="Cross-sectional momentum on Chan's own file, Example 6.2 of "
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
