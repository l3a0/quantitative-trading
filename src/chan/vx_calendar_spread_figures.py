"""The figure for ``blog/vx-calendar-spread-lessons.md``, *Algorithmic Trading* at location 2502.

That post is on VIX futures calendar spreads. :mod:`chan.vx_calendar_spread`
prints Entry 35's figures and draws nothing, so this module draws what the run
does not.
[issue 465](https://github.com/l3a0/quantitative-trading/issues/465) asked for
the post, and its plan set the two panels.

1. **Figure 5.8 redrawn.** The cumulative compounded return,
   ``cumprod(1 + ret) − 1``, of S and of B1 to B3, from 2008-10-27 to the
   file's last row, 2012-05-07. The book prints one curve. Drawing the four
   rows that end on the file's last row shows the search that found B3, which
   is drawn in ink. B4 is S cut at 2012-04-23, so its curve would lie on S's
   and is left out. The book's end date is marked.
2. **The book's third claim.** Each of S and B1 to B3's APR before October
   2008, from the first row its flipped positions hold anything to
   2008-10-24, beside its APR from 2008-10-27. The book says its rule
   "performed much more poorly prior to October 2008", and only B3's bar
   falls.

Every value comes from :func:`chan.roll_returns.load_strip` and
:func:`chan.vx_calendar_spread.vx_calendar_spread`, the run's own path, so
the scale-break guard runs here too::

    uv run python -m chan.vx_calendar_spread_figures
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter, YearLocator
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, INK, MUTED, RULE, SURFACE
from chan.roll_returns import SOURCE_FILES, Strip, load_strip
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable
from chan.vx_calendar_spread import (
    BOOK_APR_PERCENT,
    BOOK_END,
    BOOK_SHARPE,
    ROOT,
    ROWS_BEFORE,
    VxCalendarSpread,
    vx_calendar_spread,
)

VX_CALENDAR_SPREAD_FIGURE = "vx_calendar_spread.png"

#: The rows the first panel draws, in the order the legend lists them.
CURVES = ("B3", "S", "B1", "B2")
#: How each curve is drawn: colour, width, style, and what the legend calls it.
CURVE_STYLE = {
    "B3": (INK, 1.8, "-", "B3, the held pair's ratio, each pair held in turn"),
    "S": (ACCENT, 1.4, "-", "S, the specification, the front pair's ratio"),
    "B1": (MUTED, 1.2, "--", "B1, the held pair's ratio"),
    "B2": (MUTED, 1.2, ":", "B2, the front pair's ratio, each pair held in turn"),
}
#: The width of each bar in the second panel, in row slots.
BAR_WIDTH = 0.38


def cumulative_return(returns: pd.Series) -> pd.Series:
    """``cumprod(1 + ret) − 1`` over the window, the series Figure 5.8 draws."""
    return pd.Series(np.cumprod(1 + returns.to_numpy()) - 1, index=returns.index)


def signed(value: float, places: int = 2) -> str:
    """``value`` to ``places`` decimals with a true minus sign, as the post prints it."""
    return f"{value:.{places}f}".replace("-", "−")


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


def _returns_panel(ax, result: VxCalendarSpread) -> None:
    ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    ax.axvline(BOOK_END, color=ACCENT, lw=1.0, ls="--", gid="book-end")
    for key in CURVES:
        color, width, style, name = CURVE_STYLE[key]
        cumret = cumulative_return(result.rows[key].returns)
        ax.plot(
            cumret.index,
            cumret,
            color=color,
            lw=width,
            ls=style,
            zorder=3 if key == "B3" else 2,
            gid=key,
            label=f"{name}, ending at {signed(100 * cumret.iloc[-1])} percent",
        )
    days = result.rows["S"].returns.index
    ax.annotate(
        f"the book's end, {BOOK_END.date()}",
        (BOOK_END, 0.35),
        xytext=(-6, 0),
        textcoords="offset points",
        ha="right",
        color=ACCENT,
        fontsize=9.5,
        gid="book-end-label",
    )
    ax.set_xlim(days[0], days[-1])
    ax.xaxis.set_major_locator(YearLocator())
    ax.xaxis.set_major_formatter(DateFormatter("%Y"))
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.set_ylabel("cumulative return, compounded", color=INK, fontsize=10)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK)
    b3 = result.b3_book_window
    _heading(
        ax,
        f"Figure 5.8: each row's cumulative return, {days[0].date()} to {days[-1].date()}. "
        f"On the book's window to {BOOK_END.date()},\nB3's APR is {b3.apr:.6f} and its Sharpe "
        f"ratio {b3.sharpe:.6f}, where the book prints {BOOK_APR_PERCENT} percent and "
        f"{BOOK_SHARPE}.",
    )


def _before_panel(ax, result: VxCalendarSpread) -> None:
    slots = np.arange(len(ROWS_BEFORE))
    before = [result.before[key].apr for key in ROWS_BEFORE]
    after = [result.rows[key].apr for key in ROWS_BEFORE]
    for offset, values, color, when, name in (
        (-BAR_WIDTH / 2, before, MUTED, "before", "before October 2008"),
        (BAR_WIDTH / 2, after, INK, "after", "from 2008-10-27"),
    ):
        bars = ax.bar(slots + offset, values, BAR_WIDTH, color=color, label=name, gid=when)
        for bar, value in zip(bars, values, strict=True):
            ax.annotate(
                signed(100 * value, 1),
                (bar.get_x() + bar.get_width() / 2, value),
                xytext=(0, 4 if value >= 0 else -4),
                textcoords="offset points",
                ha="center",
                va="bottom" if value >= 0 else "top",
                color=INK,
                fontsize=9,
            )
    ax.axhline(0, color=RULE, lw=0.9, gid="zero")
    ax.set_xticks(slots, ROWS_BEFORE)
    ax.margins(y=0.15)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.set_ylabel("APR, compounded", color=INK, fontsize=10)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK)
    first = min(result.before[key].returns.index[0] for key in ROWS_BEFORE)
    _heading(
        ax,
        f"Each row's APR before October 2008, from its first held row ({first.date()} at the "
        "earliest) to 2008-10-24,\nbeside its APR from 2008-10-27. Only B3 does worse before, "
        "as the book says of its rule.",
    )


@_plain_text
def make_vx_calendar_spread_figure(
    out: Path | None = None,
    strip: Strip | None = None,
) -> Figure:
    """Figure 5.8 with the rows declared beside S, and each row before October 2008."""
    strip = strip if strip is not None else load_strip(ROOT)
    result = vx_calendar_spread(strip.contracts)

    fig = Figure(figsize=(10, 11), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    returns_ax, before_ax = fig.subplots(2, 1, gridspec_kw={"hspace": 0.34})
    for ax in (returns_ax, before_ax):
        _style(ax)
    _returns_panel(returns_ax, result)
    _before_panel(before_ax, result)

    saved = sorted({m.obtained for m in strip.members})
    _title(
        fig,
        "Exploratory: VIX futures calendar spreads on the ratio of back to front",
        f"Algorithmic Trading, location 2502. Contracts from {SOURCE_FILES[ROOT]}, saved "
        f"{', '.join(saved)}.\nB3 was picked out after the run among five rows, and no cost "
        "is charged.",
    )
    fig.subplots_adjust(left=0.1, right=0.97, top=0.9, bottom=0.09)
    return _save(fig, out, VX_CALENDAR_SPREAD_FIGURE)


def main() -> None:
    try:
        make_vx_calendar_spread_figure()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day reaches the reader
        # as one line, the way chan.vx_calendar_spread.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / VX_CALENDAR_SPREAD_FIGURE}")


if __name__ == "__main__":
    main()
