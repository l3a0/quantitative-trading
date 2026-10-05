"""The figure for the post on cross-sectional momentum, *Algorithmic Trading*'s Example 6.2.

``blog/cross-sectional-momentum-lessons.md`` teaches what Entry 17 of the
replication log found, and
[issue 317](https://github.com/l3a0/quantitative-trading/issues/317) chose one
figure for it. ``kentdaniel.m`` closes on ``plot(cumret)``, where ``cumret``
compounds the active window's days from zero, and the script carries three
windows switched by which pair of lines is commented out. So
:func:`make_cumulative_figure` draws three panels side by side, one per
window, sharing the y-axis, with widths in proportion to the 160, 505 and 582
days each holds. That redraws what the script draws once per run, three times,
and each panel ends at the compounded figure the run prints for its window.

Each panel marks three things.

1. Its deepest drawdown, the high it fell from and the trough, labelled with
   ``calculateMaxDD``'s depth. :func:`deepest_drawdown` locates it.
2. On the 2008 and 2009 panel only, the longest spell below the high, shaded
   and labelled as still running when the window ends, because it runs to the
   window's last day.
3. A heading naming the window, the compounded and arithmetic returns and the
   Sharpe ratio, beside the book's figure where it prints one.

The drawdown is marked rather than :func:`chan.pead_figures.longest_spell`'s
trough because the two differ in two of the three windows. In 2007 and in 2010
to 2012 the deepest drawdown sits outside the longest spell, so the spell's
trough would label a number the post does not quote.
``tests/test_cross_sectional_momentum_figures.py`` holds that.

Every value comes from :func:`chan.cross_sectional_momentum.script_as_printed`
over :func:`chan.cross_sectional_momentum.read_closes`, the run's own path, and
each window is sliced by
:func:`chan.cross_sectional_momentum.window_returns`, the rule the printed
figures use. The run calls no scale-break guard, by
[issue 297](https://github.com/l3a0/quantitative-trading/issues/297)'s
decision, so the figure has no guard to skip::

    uv run python -m chan.cross_sectional_momentum_figures
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter, MonthLocator, YearLocator
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.cross_sectional_momentum import (
    BOOK_APR_PERCENT,
    BOOK_CRISIS_APR_PERCENT,
    BOOK_SHARPE,
    HOLD_DAYS,
    PRICE_FILE,
    TOP_N,
    WINDOWS,
    Figures,
    read_closes,
    script_as_printed,
    window_figures,
    window_returns,
)
from chan.matlab_helpers import drawdown_path
from chan.paths import FIGURES_DIR
from chan.pead_figures import _signed, longest_spell
from chan.regime_figure import INK, LOST, MUTED, SURFACE
from chan.vintage import VintageUnavailable

CUMULATIVE_FIGURE = "cross_sectional_momentum_cumulative_returns.png"


def _signed_percent(x: int) -> str:
    """A whole percent with a true minus sign, as the post prints it."""
    return f"{x}".replace("-", "−")


#: The one window whose longest spell below the high is shaded, because it is
#: the one the post quotes a duration for.
SPELL_WINDOW = "2008-2009"

#: What the book prints for each window at location 2800, over two lines
#: because the 2007 panel is the narrowest. The third prints no figure, only a
#: claim.
BOOK_LINES = {
    "2007": f"The book prints\n{BOOK_APR_PERCENT} percent and {BOOK_SHARPE}.",
    "2008-2009": f"The book prints\n{_signed_percent(BOOK_CRISIS_APR_PERCENT)} percent.",
    "2010-2012": 'The book says it\n"did stabilize".',
}

#: Where each trough's label sits from its point, in points. The 2007 trough
#: sits just above the zero line, so its label drops further to clear the line.
TROUGH_OFFSETS = {"2007": (-8, -74), "2008-2009": (-8, -46), "2010-2012": (-8, -46)}


@dataclass(frozen=True)
class Drawdown:
    """The deepest drawdown, as rows of one window.

    ``high`` is the row the high was set on and ``trough`` the deepest row,
    where the drawdown is ``depth``.
    """

    high: int
    trough: int
    depth: float


@dataclass(frozen=True)
class Panel:
    """One window's days, its compounded cumulative return and its printed figures."""

    window: str
    days: pd.DatetimeIndex
    cumret: np.ndarray
    figures: Figures


def deepest_drawdown(cumret: np.ndarray) -> Drawdown:
    """Where ``calculateMaxDD``'s deepest drawdown falls, under its own rules.

    It reads :func:`chan.matlab_helpers.drawdown_path`, the loop
    :func:`chan.matlab_helpers.calculate_max_dd` runs, so the depth is that
    function's. The high is the trough's row less its duration below the high,
    which is the last row the drawdown was 0. Where two rows tie, the first is
    taken.
    """
    _, drawdown, duration = drawdown_path(cumret)
    trough = int(np.argmin(drawdown))
    return Drawdown(
        high=trough - int(duration[trough]), trough=trough, depth=float(drawdown[trough])
    )


def panels(closes: pd.DataFrame) -> list[Panel]:
    """The script as printed over each of :data:`WINDOWS`, in the script's order."""
    daily = script_as_printed(closes.to_numpy(dtype=float))
    days = pd.DatetimeIndex(closes.index)
    drawn = []
    for window in WINDOWS:
        inside, r = window_returns(daily, days, window)
        drawn.append(
            Panel(
                window=window,
                days=inside,
                cumret=np.cumprod(1 + r) - 1,
                figures=window_figures(daily, days, window),
            )
        )
    return drawn


def panel_heading(panel: Panel) -> str:
    """The window, its three figures, and what the book prints beside them."""
    start, end = WINDOWS[panel.window]
    f = panel.figures
    sharpe = f"{f.sharpe:.4f}".replace("-", "−")
    return (
        f"{start} to\n{end}\n"
        f"compounded {_signed(f.compounded_apr)}\n"
        f"arithmetic {_signed(f.arithmetic_annual)}\n"
        f"Sharpe ratio {sharpe}\n" + BOOK_LINES[panel.window]
    )


def _draw(ax, panel: Panel) -> None:
    days, cumret = panel.days, panel.cumret
    deepest = deepest_drawdown(cumret)
    _style(ax)

    if panel.window == SPELL_WINDOW:
        spell = longest_spell(cumret)
        ax.axvspan(days[spell.first], days[spell.last], color=LOST, alpha=0.12, lw=0, gid="spell")
        ax.text(
            days[(spell.first + spell.last) // 2],
            0.97,
            f"{spell.rows} days below the high,\n{days[spell.first].date()} to "
            f"{days[spell.last].date()},\nstill running when the window ends",
            transform=ax.get_xaxis_transform(),
            ha="center",
            va="top",
            color=LOST,
            fontsize=9.5,
            fontweight="bold",
            gid="spell-label",
        )
        ax.spell = spell

    ax.axhline(0, color=MUTED, lw=0.9)
    ax.plot(days, cumret, color=INK, lw=1.6, gid="cumulative")
    for gid, row, colour in (("high", deepest.high, INK), ("trough", deepest.trough, LOST)):
        ax.plot(
            [days[row]],
            [cumret[row]],
            "o",
            ms=6,
            color=colour,
            mec=SURFACE,
            mew=1.6,
            zorder=3,
            gid=gid,
        )
    ax.annotate(
        f"high,\n{days[deepest.high].date()}",
        (days[deepest.high], cumret[deepest.high]),
        xytext=(-6, 6),
        textcoords="offset points",
        ha="right",
        color=INK,
        fontsize=9,
        gid="high-label",
    )
    ax.annotate(
        f"deepest drawdown\n{_signed(deepest.depth)},\n{days[deepest.trough].date()}",
        (days[deepest.trough], cumret[deepest.trough]),
        xytext=TROUGH_OFFSETS[panel.window],
        textcoords="offset points",
        ha="right",
        color=LOST,
        fontsize=9,
        fontweight="bold",
        gid="trough-label",
    )
    ax.set_title(panel_heading(panel), loc="left", color=INK, fontsize=9.5, linespacing=1.3)
    ax.set_xlim(days[0], days[-1])
    ax.cumret = cumret
    ax.deepest = deepest


@_plain_text
def make_cumulative_figure(out: Path | None = None, closes: pd.DataFrame | None = None) -> Figure:
    """Each window's compounded cumulative return, its deepest drawdown marked."""
    closes = closes if closes is not None else read_closes()[1]
    drawn = panels(closes)

    fig = Figure(figsize=(14, 7.8), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    axes = fig.subplots(
        1, 3, sharey=True, gridspec_kw={"width_ratios": [len(p.days) for p in drawn]}
    )
    for ax, panel in zip(axes, drawn, strict=True):
        _draw(ax, panel)

    low = min(p.cumret.min() for p in drawn)
    high = max(p.cumret.max() for p in drawn)
    span = high - low
    axes[0].set_ylim(low - 0.22 * span, high + 0.22 * span)
    axes[0].yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    axes[0].set_ylabel("cumulative return, compounded from each window's start", color=INK)
    # The 2007 panel spans seven months, so it ticks by month. The other two
    # span two years or more and tick by year.
    axes[0].xaxis.set_major_locator(MonthLocator(bymonth=(6, 9, 12)))
    axes[0].xaxis.set_major_formatter(DateFormatter("%b"))
    for ax in axes[1:]:
        ax.xaxis.set_major_locator(YearLocator())
        ax.xaxis.set_major_formatter(DateFormatter("%Y"))

    _title(
        fig,
        "Exploratory: kentdaniel.m's cumulative return redrawn on Chan's own file, "
        "one run per window",
        f"Example 6.2 of Algorithmic Trading, the {TOP_N} highest and {TOP_N} lowest 252-day "
        f"returns long and short, each day's picks held {HOLD_DAYS} days, unlevered and before "
        "costs.\n"
        f"Prices from {PRICE_FILE}. Each panel restarts at zero on its window's first day, "
        "as the script does.\n"
        "The file holds the S&P 500 as Chan held it on 2012-04-24, so every stock is a survivor.",
    )
    fig.tight_layout(rect=(0, 0.09, 1, 0.97))
    return _save(fig, out, CUMULATIVE_FIGURE)


def main() -> None:
    try:
        make_cumulative_figure()
    except VintageUnavailable as refused:
        # A refusal that names the source is worth nothing at the bottom of a
        # traceback, so it reaches the operator as one line, the way
        # chan.cross_sectional_momentum.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / CUMULATIVE_FIGURE}")


if __name__ == "__main__":
    main()
