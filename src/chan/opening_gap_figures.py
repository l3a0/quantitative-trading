"""The figure for ``blog/opening-gap-lessons.md``, *Algorithmic Trading*'s Example 7.1.

That post is on the opening gap strategy on FSTX, the STOXX Europe 50 index
future. :mod:`chan.opening_gap` prints Entry 40's figures and draws nothing,
so this module draws what the run does not.
[issue 509](https://github.com/l3a0/quantitative-trading/issues/509) asked for
the post, and its plan set the two panels on one date axis.

1. **Figure 7.1 redrawn, with the sign the text describes beside it.** The
   literal reading's cumulative compounded return, ``cumprod(1 + ret) − 1``,
   the series the script's ``plot(cumret)`` draws, in ink. The momentum
   reading's, the sign location 2965 describes, in a second colour on the
   same axis, with a line at 0. The literal reading's deepest drawdown has
   its high and trough marked, and so does its longest run below a high.
2. **The literal reading by side.** The same returns kept on the long days
   only and on the short days only, from :func:`chan.opening_gap.by_side`,
   each compounded with nothing earned on the other days. The book prints
   only the whole curve, while the post's last lesson turns on the two sides.

Both panels shade the first 90 rows, which have no standard deviation and hold
nothing.
Nothing compares the redraw with the chart the book prints, so it is a redraw
of the script's plot rather than a checked copy.

Every value comes from :func:`chan.opening_gap.read_sources` and
:func:`~chan.opening_gap.opening_gap`, the run's own path, so the scale-break
guard runs here too::

    uv run python -m chan.opening_gap_figures
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter, YearLocator, date2num
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.matlab_helpers import drawdown_path
from chan.opening_gap import (
    BOOK_APR_PERCENT,
    BOOK_SHARPE,
    SOURCE_FILE,
    SPREAD_LOOKBACK,
    OpeningGap,
    by_side,
    opening_gap,
    read_sources,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, INK, LOST, MUTED, RULE, SURFACE
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageEntry, VintageUnavailable

FIGURE = "opening_gap.png"
#: The shading for the first rows, which have no standard deviation, in both panels.
NO_SPREAD_SHADE = (RULE, 0.45)
#: The first panel's vertical range, wide enough that the legend sits above
#: both curves in the upper left.
CURVE_LIMITS = (-0.85, 1.95)
#: The second panel's vertical range, for the same reason.
SIDE_LIMITS = (-0.25, 1.3)


def cumulative_return(daily: np.ndarray) -> np.ndarray:
    """``cumprod(1 + ret) − 1``, the series Figure 7.1 draws."""
    return np.cumprod(1 + np.asarray(daily, dtype=float)) - 1


def signed(value: float, places: int = 2) -> str:
    """``value`` to ``places`` decimals with a true minus sign, as the post prints it."""
    return f"{value:.{places}f}".replace("-", "−")


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


def _shade(ax, days: pd.DatetimeIndex) -> None:
    """The first rows, before the standard deviation exists, the same in both panels."""
    color, alpha = NO_SPREAD_SHADE
    ax.axvspan(
        date2num(days[0]),
        date2num(days[SPREAD_LOOKBACK - 1]),
        color=color,
        alpha=alpha,
        lw=0,
        gid="no-spread",
        label=f"the first {SPREAD_LOOKBACK} days, no standard deviation and nothing held",
    )


def _mark(ax, day: pd.Timestamp, value: float, gid: str, text: str, offset) -> None:
    ax.plot([day], [value], "o", color=ACCENT, ms=5, zorder=4, gid=gid)
    ax.annotate(
        f"{text}, {signed(value, 6)} on {day.date()}",
        (day, value),
        xytext=offset,
        textcoords="offset points",
        ha="right" if offset[0] < 0 else "left",
        color=ACCENT,
        fontsize=9,
        gid=f"{gid}-label",
    )


def _readings_panel(ax, result: OpeningGap) -> None:
    days = result.days
    literal = cumulative_return(result.literal)
    momentum = cumulative_return(result.momentum)
    _shade(ax, days)
    ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    ax.plot(
        days,
        momentum,
        color=LOST,
        lw=1.4,
        gid="momentum",
        label=f"the sign the text describes, ending at {signed(100 * momentum[-1])} percent",
    )
    ax.plot(
        days,
        literal,
        color=INK,
        lw=1.7,
        zorder=3,
        gid="literal",
        label=f"the script as written, ending at {signed(100 * literal[-1])} percent",
    )

    highs, drawdown, duration = drawdown_path(literal)
    trough = int(np.argmin(drawdown))
    high = int(np.argmax(literal[: trough + 1]))
    _mark(ax, days[high], literal[high], "drawdown-high", "high", (-10, 0))
    _mark(ax, days[trough], literal[trough], "drawdown-trough", "trough", (8, -12))
    last = int(np.argmax(duration))
    first = last - int(duration[last]) + 1
    ax.plot(
        [days[first], days[last]],
        [highs[last]] * 2,
        color=ACCENT,
        lw=1.0,
        ls=":",
        gid="longest-drawdown",
    )
    ax.annotate(
        f"{duration[last]} days below this high,\nto {days[last].date()}",
        (days[first] + (days[last] - days[first]) / 2, highs[last]),
        xytext=(0, 5),
        textcoords="offset points",
        ha="center",
        color=ACCENT,
        fontsize=9,
        gid="longest-drawdown-label",
    )

    ax.set_ylim(*CURVE_LIMITS)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.set_ylabel("cumulative return, compounded", color=INK, fontsize=10)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK)
    lit, mom = result.literal_figures, result.momentum_figures
    _heading(
        ax,
        f"Figure 7.1 redrawn: the script as written earns APR {lit.apr:.6f} and Sharpe ratio "
        f"{lit.sharpe:.6f},\nwhere the book prints {BOOK_APR_PERCENT} percent and "
        f"{BOOK_SHARPE}. The sign the text describes earns {signed(mom.apr, 6)} and "
        f"{signed(mom.sharpe, 6)}.",
    )


def _sides_panel(ax, result: OpeningGap) -> None:
    days = result.days
    sides = by_side(result)
    long = cumulative_return(sides["long"].daily)
    short = cumulative_return(sides["short"].daily)
    _shade(ax, days)
    ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    ax.plot(
        days,
        short,
        color=MUTED,
        lw=1.4,
        ls="--",
        gid="short",
        label=f"the {sides['short'].days} short days alone, ending at "
        f"{signed(100 * short[-1])} percent",
    )
    ax.plot(
        days,
        long,
        color=INK,
        lw=1.7,
        zorder=3,
        gid="long",
        label=f"the {sides['long'].days} long days alone, ending at "
        f"{signed(100 * long[-1])} percent",
    )
    low = int(np.argmin(short))
    _mark(ax, days[low], short[low], "short-low", "low", (8, -12))

    ax.set_ylim(*SIDE_LIMITS)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.set_ylabel("cumulative return, compounded", color=INK, fontsize=10)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK)
    _heading(
        ax,
        "The script as written, by side: each side's returns on its own days, and nothing on "
        "the others.\nIts long days earn a fall from the open after an upward jump, and its "
        "short days a rise after a downward one.",
    )


@_plain_text
def make_opening_gap_figure(
    out: Path | None = None,
    sources: tuple[VintageEntry, pd.DataFrame] | None = None,
) -> Figure:
    """Figure 7.1 with the momentum reading beside it, and the script's returns by side."""
    entry, prices = sources if sources is not None else read_sources()
    result = opening_gap(prices)

    fig = Figure(figsize=(10, 10.5), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    readings_ax, sides_ax = fig.subplots(
        2, 1, sharex=True, gridspec_kw={"hspace": 0.3, "height_ratios": (1.4, 1)}
    )
    for ax in (readings_ax, sides_ax):
        _style(ax)
    _readings_panel(readings_ax, result)
    _sides_panel(sides_ax, result)
    readings_ax.set_xlim(date2num(result.days[0]), date2num(result.days[-1]))
    sides_ax.xaxis.set_major_locator(YearLocator())
    sides_ax.xaxis.set_major_formatter(DateFormatter("%Y"))

    _title(
        fig,
        "Exploratory: the opening gap strategy on STOXX Europe 50 futures, both signs",
        f"Algorithmic Trading, Kindle edition, Example 7.1 and p. 229. FSTX from {SOURCE_FILE}, "
        "saved "
        f"{entry.obtained}.\n{len(result.days):,} days from {result.days[0].date()} to "
        f"{result.days[-1].date()}, each held from the open to the close, with no cost charged.",
    )
    fig.subplots_adjust(left=0.1, right=0.97, top=0.9, bottom=0.09)
    return _save(fig, out, FIGURE)


def main() -> None:
    try:
        make_opening_gap_figure()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day reaches the reader
        # as one line, the way chan.opening_gap.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / FIGURE}")


if __name__ == "__main__":
    main()
