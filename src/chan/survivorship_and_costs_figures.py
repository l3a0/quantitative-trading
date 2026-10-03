"""Two figures for the post on Chapter 3's two warnings, costs and survivors.

``blog/survivorship-and-transaction-costs.md`` teaches what Entries 8 and 9 of
the replication log found, and
[issue 239](https://github.com/l3a0/quantitative-trading/issues/239) chose one
figure for each.

1. :func:`make_cumulative_figure`, for the cost lesson. Khandani and Lo's
   reversal on Chan's S&P 500 file over 2006, its profit summed day by day
   before costs and after 5 basis points a side. Each day is divided by the
   window's mean gross position, one constant for the whole year, which
   :class:`chan.khandani_lo.DailyBook` says is why neither Sharpe ratio moves.
   The after-cost line is the specification with the first day charged,
   Entry 8's row 3, because a running total cannot carry the NaN Chan's own
   series has on its first day.
2. :func:`make_toy_figure`, for the survivorship lessons. The return of
   Chan's two printed tables of picks, and of the survivor-only table with
   NEOF on one share basis, each split into NEOF's share and the other nine's.

Every value comes from :mod:`chan.khandani_lo` and
:mod:`chan.survivorship_bias`, so a figure can only be wrong by drawing the
wrong thing, which ``tests/test_survivorship_and_costs_figures.py`` checks.
The toy's figure reads no vintage, so it is drawn first, and a missing S&P 500
file stops only the second::

    uv run python -m chan.survivorship_and_costs_figures
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter, MonthLocator
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.khandani_lo import ONE_WAY_COST, SOURCE_FILE, Reversal, daily_book, reversal
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED, RULE, SURFACE
from chan.series import load_panel
from chan.survivorship_bias import (
    END_DATE,
    NEOF_REVERSE_SPLIT,
    START_DATE,
    SURVIVOR_PICKS,
    UNBIASED_PICKS,
    contributions,
    equal_capital_return,
    one_share_basis,
)
from chan.vintage import VintageUnavailable

CUMULATIVE_FIGURE = "khandani_lo_cumulative_profit.png"
TOY_FIGURE = "survivorship_toy_returns.png"


def _pct(x: float, places: int) -> str:
    """A signed percent with a true minus sign, as the post prints one."""
    return f"{x:+.{places}%}".replace("-", "−")


def _signed(x: float) -> str:
    """A Sharpe ratio at four places, with a true minus sign where it is negative."""
    return f"{x:.4f}".replace("-", "−")


@dataclass(frozen=True)
class Cumulative:
    """The two running totals the cost figure draws, per unit of the mean book."""

    days: pd.DatetimeIndex
    before: np.ndarray
    after: np.ndarray


def cumulative(result: Reversal) -> Cumulative:
    """Each day's profit summed through the window, over the window's mean book."""
    book = daily_book(result).book
    return Cumulative(
        days=result.days,
        before=np.cumsum(result.pnl) / book,
        after=np.cumsum(result.pnl_charged) / book,
    )


def chan_window_result(data_dir: Path | None = None) -> Reversal:
    """The reversal on Chan's file and window, read without printing the report."""
    _, frame = load_panel(SOURCE_FILE, data_dir=data_dir)
    return reversal(frame)


@_plain_text
def make_cumulative_figure(out: Path | None = None, result: Reversal | None = None) -> Figure:
    """The year's running profit before and after 5 basis points a side."""
    result = result if result is not None else chan_window_result()
    totals = cumulative(result)
    bp = ONE_WAY_COST * 1e4

    fig = Figure(figsize=(10, 5.6), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.subplots()
    _style(ax)

    ax.axhline(0, color=MUTED, lw=0.9)
    ax.plot(totals.days, totals.before, color=GOOD, lw=2, gid="before")
    ax.plot(totals.days, totals.after, color=LOST, lw=2, gid="after")
    ends = [
        (totals.before[-1], GOOD, f"before costs, {_pct(totals.before[-1], 1)}", (-150, 12)),
        (
            totals.after[-1],
            LOST,
            f"after {bp:.0f} bp a side, {_pct(totals.after[-1], 1)}",
            (-205, -6),
        ),
    ]
    for y, colour, label, offset in ends:
        ax.plot([totals.days[-1]], [y], "o", ms=7, color=colour, mec=SURFACE, mew=2, zorder=3)
        ax.annotate(
            label,
            (totals.days[-1], y),
            xytext=offset,
            textcoords="offset points",
            color=colour,
            fontsize=10.5,
            fontweight="bold",
        )

    ax.set_xlim(totals.days[0], totals.days[-1] + pd.Timedelta(days=6))
    ax.set_ylim(-0.19, 0.04)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.xaxis.set_major_locator(MonthLocator())
    ax.xaxis.set_major_formatter(DateFormatter("%b"))
    ax.set_ylabel("profit so far, as a share of the average position", color=INK, fontsize=10.5)
    _title(
        fig,
        f"Five basis points a side turn a {_pct(totals.before[-1], 1)} year into a "
        f"{_pct(totals.after[-1], 1)} one",
        f"Khandani and Lo's reversal on Chan's S&P 500 file, {result.days[0].date()} to "
        f"{result.days[-1].date()}, each day's profit over the year's mean gross position.\n"
        f"The cost line charges the first day's rebalance too. Sharpe ratio "
        f"{_signed(result.before_costs)} before costs and "
        f"{_signed(result.after_costs_charged)} after.",
    )
    fig.tight_layout(rect=(0, 0.08, 1, 0.95))
    fig.totals = totals
    return _save(fig, out, CUMULATIVE_FIGURE)


@dataclass(frozen=True)
class ToyBar:
    """One portfolio's equal-capital return, and NEOF's share of it."""

    label: str
    total: float
    neof: float

    @property
    def others(self) -> float:
        return self.total - self.neof


def toy_bars() -> list[ToyBar]:
    """The three portfolios the figure draws, top to bottom."""
    adjusted = one_share_basis(SURVIVOR_PICKS)
    return [
        ToyBar(
            "survivorship-free picks,\nwhat a trader got",
            equal_capital_return(UNBIASED_PICKS),
            0.0,
        ),
        ToyBar(
            "survivor-only picks,\nas the book prints them",
            equal_capital_return(SURVIVOR_PICKS),
            contributions(SURVIVOR_PICKS)["NEOF"],
        ),
        ToyBar(
            "survivor-only picks,\nNEOF on one share basis",
            equal_capital_return(adjusted),
            contributions(adjusted)["NEOF"],
        ),
    ]


@_plain_text
def make_toy_figure(out: Path | None = None) -> Figure:
    """The two tables' returns, and the second with NEOF on one share basis."""
    bars = toy_bars()

    fig = Figure(figsize=(10, 5.2), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.subplots()
    _style(ax)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=RULE, lw=0.6, alpha=0.7)

    rows = np.arange(len(bars))[::-1]
    for y, bar in zip(rows, bars, strict=True):
        if bar.total < 0:
            ax.barh(y, bar.total, height=0.55, color=LOST, gid="loss")
        else:
            ax.barh(y, bar.others, height=0.55, color=GOOD, gid="others")
            ax.barh(y, bar.neof, left=bar.others, height=0.55, color=ACCENT, gid="neof")
            ax.annotate(
                "the other nine",
                (bar.others / 2, y),
                ha="center",
                va="center",
                color=SURFACE,
                fontsize=9.5,
                fontweight="bold",
            )
            # NEOF's segment holds its own label where it is wide enough to.
            # On one share basis it is not, so the label follows the total.
            if bar.neof > 0.5:
                where, offset, align, colour = (
                    (bar.others + bar.neof / 2, y),
                    (0, 0),
                    "center",
                    SURFACE,
                )
            else:
                where, offset, align, colour = (bar.total, y), (78, 0), "left", ACCENT
            ax.annotate(
                f"NEOF {bar.neof * 100:.2f} points",
                where,
                xytext=offset,
                textcoords="offset points",
                ha=align,
                va="center",
                color=colour,
                fontsize=9.5,
                fontweight="bold",
            )
        x = max(bar.total, 0.0)
        ax.annotate(
            _pct(bar.total, 2),
            (x, y),
            xytext=(8, 0),
            textcoords="offset points",
            va="center",
            color=INK,
            fontsize=11,
            fontweight="bold",
        )

    ax.axvline(0, color=MUTED, lw=0.9)
    ax.set_yticks(rows, [bar.label for bar in bars])
    ax.set_xlim(-0.6, 4.7)
    ax.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.set_xlabel(
        "return over the year, equal capital in each of ten stocks", color=INK, fontsize=10.5
    )
    _title(
        fig,
        f"A database of survivors turns a {-bars[0].total:.0%} loss into a "
        f"{bars[1].total:.0%} gain, most of it from one row",
        f"Chan's Example 3.3, revised edition: the ten cheapest of the 1,000 largest stocks, "
        f"{START_DATE} to {END_DATE}, from the book's two printed tables.\n"
        f"NEOF's start price predates a 1-for-{NEOF_REVERSE_SPLIT} reverse split and its end "
        f"price follows it. The bottom bar multiplies its start price by {NEOF_REVERSE_SPLIT}.",
    )
    fig.tight_layout(rect=(0, 0.09, 1, 0.95))
    fig.bars = bars
    return _save(fig, out, TOY_FIGURE)


def main() -> None:
    make_toy_figure()
    print(f"wrote {FIGURES_DIR / TOY_FIGURE}")
    try:
        result = chan_window_result()
    except VintageUnavailable as unavailable:
        # Caught the way chan.khandani_lo.main catches it. The toy's figure
        # reads no file and is already drawn, so a missing S&P 500 file costs
        # one line of output rather than a traceback.
        raise SystemExit(str(unavailable)) from unavailable
    make_cumulative_figure(result=result)
    print(f"wrote {FIGURES_DIR / CUMULATIVE_FIGURE}")


if __name__ == "__main__":
    main()
