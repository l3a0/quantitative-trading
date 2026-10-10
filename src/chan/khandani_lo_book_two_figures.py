"""The figure for the post on the Khandani-Lo reversal on Chan's 2012 panel.

``blog/khandani-lo-reversal-lessons.md`` teaches what Entry 19 of the
replication log found. :func:`make_reversal_figure` draws two panels on one
date axis over the window's 1,260 days, in the order the post reads them.

1. Example 4.3's compounded cumulative return, the book's Figure 4.4. The two
   calendar years location 2110 names, 2008 and 2011, are shaded.
2. Example 4.4's compounded cumulative return, on its own axis. The book draws
   no figure for it, and its APR of 73 percent would flatten Example 4.3's
   curve on a shared axis.

Both of ``andrewlo_2007_2012.m``'s ``plot`` lines draw ``cumprod(1+dailyret)-1``
against the row number, so both panels compound and the redraw only dates the
axis. Each calendar year carries the APR the script's APR line gives it, so
the three years the book does not name are on the page beside the two it does.

Every value comes from :func:`chan.khandani_lo_book_two.close_to_close` and
:func:`chan.khandani_lo_book_two.open_to_close` on the committed panel, the
functions the pins call. That module computes across the scale breaks the
guard would refuse, as its docstring decides, so the figure does too::

    uv run python -m chan.khandani_lo_book_two_figures
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter, YearLocator
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.khandani_lo_book_two import (
    BOOK_43_APR_PERCENT,
    BOOK_43_SHARPE,
    BOOK_44_APR_PERCENT,
    BOOK_44_SHARPE,
    BOOK_YEAR_APR_PERCENT,
    SOURCE_FILE,
    WINDOW_END,
    WINDOW_START,
    Run,
    close_to_close,
    open_to_close,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, INK, MUTED, SURFACE
from chan.series import load_panel
from chan.vintage import VintageEntry, VintageUnavailable

REVERSAL_FIGURE = "khandani_lo_book_two.png"

#: The calendar years location 2110 names, shaded in the first panel.
NAMED_YEARS = tuple(BOOK_YEAR_APR_PERCENT)


def read_sources() -> tuple[list[VintageEntry], pd.DataFrame, pd.DataFrame]:
    """The panel's members, opens and closes, as ``chan.khandani_lo_book_two.run`` reads them."""
    members, closes = load_panel(SOURCE_FILE)
    _, opens = load_panel(SOURCE_FILE, field="Open")
    return members, opens, closes


def cumulative_return(run: Run) -> np.ndarray:
    """``cumprod(1 + dailyret) − 1``, the series each of the script's ``plot`` lines draws."""
    return np.cumprod(1 + run.daily) - 1


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


def _years(ax, run: Run, *, named_by_book: bool) -> None:
    """Each calendar year's APR above its span, with any year the book names shaded."""
    for year in sorted(set(run.days.year)):
        inside = run.days[run.days.year == year]
        named = named_by_book and year in NAMED_YEARS
        if named:
            ax.axvspan(inside[0], inside[-1], color=ACCENT, alpha=0.12, lw=0, gid=f"shade-{year}")
        ax.text(
            inside[0] + (inside[-1] - inside[0]) / 2,
            0.97,
            f"{year}\n{100 * run.year_apr(year):.2f}%".replace("-", "\N{MINUS SIGN}"),
            transform=ax.get_xaxis_transform(),
            ha="center",
            va="top",
            color=ACCENT if named else MUTED,
            fontsize=9.5,
            fontweight="bold" if named else "normal",
            linespacing=1.3,
            gid=f"year-{year}",
        )


def _panel(ax, run: Run, gid: str, heading: str) -> None:
    curve = cumulative_return(run)
    ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    ax.plot(
        run.days,
        curve,
        color=INK,
        lw=1.3,
        gid=gid,
        label=f"APR {run.apr:.6f}, Sharpe ratio {run.sharpe:.6f}",
    )
    # Room above the curve for the year labels, which sit in the top fifth.
    low, high = min(curve.min(), 0.0), curve.max()
    ax.set_ylim(low - 0.05 * (high - low), high + 0.3 * (high - low))
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.set_ylabel("cumulative return, compounded", color=INK, fontsize=10)
    ax.legend(loc="lower right", frameon=False, fontsize=9.5, labelcolor=INK)
    _heading(ax, heading)


@_plain_text
def make_reversal_figure(
    out: Path | None = None,
    sources: tuple[list[VintageEntry], pd.DataFrame, pd.DataFrame] | None = None,
) -> Figure:
    """Example 4.3's and Example 4.4's cumulative returns, each year's APR above them."""
    members, opens, closes = sources if sources is not None else read_sources()
    held = close_to_close(closes, start=WINDOW_START, end=WINDOW_END)
    intraday = open_to_close(opens, closes, start=WINDOW_START, end=WINDOW_END)
    days = held.days

    fig = Figure(figsize=(10, 9.5), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    held_ax, intraday_ax = fig.subplots(2, 1, sharex=True, gridspec_kw={"hspace": 0.45})
    for ax in (held_ax, intraday_ax):
        _style(ax)
        ax.tick_params(labelbottom=True)

    _panel(
        held_ax,
        held,
        "close-to-close",
        "Figure 4.4: Example 4.3, each day's weights held from one close to the next.\n"
        f"The book prints {BOOK_43_APR_PERCENT} percent and {BOOK_43_SHARPE}, and "
        f"{BOOK_YEAR_APR_PERCENT[2008]} percent in 2008 and {BOOK_YEAR_APR_PERCENT[2011]} "
        "percent in 2011, the two years shaded.",
    )
    _years(held_ax, held, named_by_book=True)
    _panel(
        intraday_ax,
        intraday,
        "open-to-close",
        "Example 4.4, weighted on the overnight move, entered at the open and closed at the "
        "same day's close.\n"
        f"The book prints {BOOK_44_APR_PERCENT} percent and {BOOK_44_SHARPE} and draws no "
        "figure, so this one has its own axis.",
    )
    _years(intraday_ax, intraday, named_by_book=False)

    intraday_ax.set_xlim(days[0], days[-1])
    intraday_ax.xaxis.set_major_locator(YearLocator())
    intraday_ax.xaxis.set_major_formatter(DateFormatter("%Y"))

    saved = sorted({m.obtained for m in members})
    _title(
        fig,
        "Exploratory: Khandani and Lo's reversal on Chan's 2012 panel of survivors",
        f"Algorithmic Trading, Examples 4.3 and 4.4, {days[0].date()} to {days[-1].date()}, "
        f"{len(days):,} trading days, as andrewlo_2007_2012.m runs them.\n"
        f"Prices from {SOURCE_FILE}, saved {', '.join(saved)}, for the {len(members)} stocks "
        "Chan held as the S&P 500 on 2012-04-24.\n"
        "Their prices are carried back, so every figure is about survivors. No cost is "
        "charged.",
    )
    fig.subplots_adjust(left=0.09, right=0.97, top=0.9, bottom=0.13)
    return _save(fig, out, REVERSAL_FIGURE)


def main() -> None:
    try:
        make_reversal_figure()
    except VintageUnavailable as refused:
        # A refusal that names the source is worth nothing at the bottom of a
        # traceback, so it reaches the operator as one line, the way
        # chan.khandani_lo_book_two.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / REVERSAL_FIGURE}")


if __name__ == "__main__":
    main()
