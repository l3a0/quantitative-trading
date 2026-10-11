"""The figure for ``blog/xle-uso-roll-return-lessons.md``, *Algorithmic Trading* at location 2734.

That post is on XLE held against USO in whichever direction crude oil's roll
return favours. :mod:`chan.xle_uso_roll_return` prints Entry 39's figures and
draws nothing, so this module draws what the run does not.
[issue 498](https://github.com/l3a0/quantitative-trading/issues/498) asked for
the post, and its plan set the two panels on one date axis.

1. **Figure 6.3 redrawn.** The trade's cumulative compounded return,
   ``cumprod(1 + ret) − 1``, from 2006-04-26 to 2012-04-09, the series the
   script plots, in ink. Beside it, muted, the same days holding contango's
   position wherever the trade holds anything, from
   :func:`chan.xle_uso_roll_return.fixed_view`. The deepest drawdown's high
   and trough are marked, and so is the longest run below a high.
2. **The signal.** The back contract over the front on each day it is
   defined, with a line at 1. The book prints only the curve, while the
   post's lessons turn on where the ratio sits against 1. The script's own
   last lines, commented out, overlay the contango flag on its plot, so
   drawing the view beside the curve follows the author.

Both panels shade the days the trade holds backwardation's position, long USO
and short XLE, and mark the window's first days, which carry no ratio and
hold nothing.

Every value comes from :func:`chan.xle_uso_roll_return.read_sources`,
:func:`~chan.xle_uso_roll_return.front_ratio` and
:func:`~chan.xle_uso_roll_return.arbitrage`, the run's own path, so the
scale-break guard runs here too::

    uv run python -m chan.xle_uso_roll_return_figures
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
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, INK, MUTED, RULE, SURFACE
from chan.roll_momentum_figures import flat_spans
from chan.roll_returns import Strip
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageEntry, VintageUnavailable
from chan.xle_uso_roll_return import (
    BACKWARDATION,
    BOOK_APR_PERCENT,
    BOOK_SHARPE,
    ETF_FILE,
    FRONT_END,
    FRONT_START,
    STRIP_FILE,
    Arbitrage,
    arbitrage,
    fixed_view,
    front_ratio,
    read_sources,
)

FIGURE = "xle_uso_roll_return.png"
#: The shading for the days held in backwardation, in both panels.
BACKWARDATION_SHADE = (ACCENT, 0.16)
#: The hatching for the window's first days, which carry no ratio, so they
#: read apart from the shaded backwardation days.
NO_RATIO_HATCH = RULE
#: The first panel's vertical range, low enough that the legend sits under
#: both curves in the lower right.
CURVE_LIMITS = (-0.6, 1.65)


def cumulative_return(daily: np.ndarray) -> np.ndarray:
    """``cumprod(1 + ret) − 1``, the series Figure 6.3 draws."""
    return np.cumprod(1 + np.asarray(daily, dtype=float)) - 1


def held_runs(
    days: pd.DatetimeIndex, held: np.ndarray
) -> list[tuple[pd.Timestamp, pd.Timestamp, int]]:
    """Each run of consecutive ``held`` rows as its first day, its last day and its length.

    The figure shades with :func:`chan.roll_momentum_figures.flat_spans` and
    never calls this. The tests call it to name the backwardation spans the
    post quotes, and hold it equal to the spans read off the drawn patches,
    so the 108-day and 20-day pins read the drawing directly.
    """
    edges = np.flatnonzero(np.diff(np.concatenate([[0], held.astype(int), [0]])))
    return [
        (days[start], days[end - 1], int(end - start))
        for start, end in zip(edges[::2], edges[1::2], strict=True)
    ]


def signed(value: float, places: int = 2) -> str:
    """``value`` to ``places`` decimals with a true minus sign, as the post prints it."""
    return f"{value:.{places}f}".replace("-", "−")


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


def _shade(ax, days: pd.DatetimeIndex, result: Arbitrage) -> None:
    """The backwardation days and the days with no ratio, the same in both panels."""
    color, alpha = BACKWARDATION_SHADE
    held = (result.positions == BACKWARDATION).all(axis=1)
    for k, (left, right) in enumerate(flat_spans(days, held)):
        ax.axvspan(
            left,
            right,
            color=color,
            alpha=alpha,
            lw=0,
            gid="backwardation",
            label="held long USO and short XLE, backwardation" if k == 0 else None,
        )
    for left, right in flat_spans(days, np.isnan(result.ratio)):
        ax.axvspan(
            left,
            right,
            facecolor="none",
            edgecolor=NO_RATIO_HATCH,
            hatch="///",
            lw=0,
            gid="no-ratio",
            label="no ratio, nothing held",
        )


def _curve_panel(ax, closes: pd.DataFrame, result: Arbitrage) -> None:
    days = result.days
    trade = cumulative_return(result.daily)
    fixed = cumulative_return(fixed_view(closes, result))
    _shade(ax, days, result)
    ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    ax.plot(
        days,
        fixed,
        color=MUTED,
        lw=1.2,
        ls="--",
        gid="fixed",
        label=f"contango's position on every held day, ending at {signed(100 * fixed[-1])} percent",
    )
    ax.plot(
        days,
        trade,
        color=INK,
        lw=1.7,
        zorder=3,
        gid="trade",
        label=f"the trade, ending at {signed(100 * trade[-1])} percent",
    )

    highs, drawdown, duration = drawdown_path(trade)
    trough = int(np.argmin(drawdown))
    high = int(np.argmax(trade[: trough + 1]))
    for row, gid, text, offset in (
        (high, "drawdown-high", "high", (-8, -3)),
        (trough, "drawdown-trough", "trough", (8, -12)),
    ):
        ax.plot([days[row]], [trade[row]], "o", color=ACCENT, ms=5, zorder=4, gid=gid)
        ax.annotate(
            f"{text}, {trade[row]:.6f} on {days[row].date()}",
            (days[row], trade[row]),
            xytext=offset,
            textcoords="offset points",
            ha="right" if offset[0] < 0 else "left",
            color=ACCENT,
            fontsize=9,
            gid=f"{gid}-label",
        )
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
        f"{duration[last]} days below this high, to {days[last].date()}",
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
    ax.legend(loc="lower right", frameon=False, fontsize=9.5, labelcolor=INK)
    f = result.figures
    _heading(
        ax,
        f"Figure 6.3: the trade's cumulative return, {days[0].date()} to {days[-1].date()}. "
        f"APR {f.apr:.6f} and Sharpe ratio {f.sharpe:.6f},\nwhere the book prints "
        f"{BOOK_APR_PERCENT} percent and about {BOOK_SHARPE}. The deepest drawdown is "
        f"{signed(f.max_drawdown, 6)}.",
    )


def _ratio_panel(ax, result: Arbitrage) -> None:
    days = result.days
    _shade(ax, days, result)
    ax.axhline(1, color=MUTED, lw=1.0, gid="one")
    defined = np.isfinite(result.ratio)
    ax.plot(days[defined], result.ratio[defined], color=INK, lw=1.0, gid="ratio")
    ratio = pd.Series(result.ratio, index=days)
    for day, gid, text, offset in (
        (ratio.idxmin(), "ratio-low", "low", (8, -4)),
        (ratio.idxmax(), "ratio-high", "high", (8, -4)),
    ):
        ax.plot([day], [ratio.loc[day]], "o", color=ACCENT, ms=5, zorder=4, gid=gid)
        ax.annotate(
            f"{text}, {ratio.loc[day]:.6f} on {day.date()}",
            (day, ratio.loc[day]),
            xytext=offset,
            textcoords="offset points",
            ha="left",
            color=ACCENT,
            fontsize=9,
            gid=f"{gid}-label",
        )
    ax.set_ylabel("back contract over front", color=INK, fontsize=10)
    _heading(
        ax,
        f"The signal: the back contract over the front, each contract the front from "
        f"{FRONT_START} to {FRONT_END} rows before its last price.\nAbove 1 is contango, "
        "short USO and long XLE. Below 1 is backwardation, long USO and short XLE.",
    )


@_plain_text
def make_xle_uso_roll_return_figure(
    out: Path | None = None,
    sources: tuple[list[VintageEntry], pd.DataFrame, Strip] | None = None,
) -> Figure:
    """Figure 6.3 with the fixed view beside it, and the ratio that signs the trade."""
    etf, closes, strip = sources if sources is not None else read_sources()
    result = arbitrage(closes, front_ratio(strip.contracts))

    fig = Figure(figsize=(10, 10.5), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    curve_ax, ratio_ax = fig.subplots(
        2, 1, sharex=True, gridspec_kw={"hspace": 0.3, "height_ratios": (1.4, 1)}
    )
    for ax in (curve_ax, ratio_ax):
        _style(ax)
    _curve_panel(curve_ax, closes, result)
    _ratio_panel(ratio_ax, result)
    curve_ax.set_xlim(date2num(result.days[0]), date2num(result.days[-1]))
    ratio_ax.xaxis.set_major_locator(YearLocator())
    ratio_ax.xaxis.set_major_formatter(DateFormatter("%Y"))

    etf_saved = sorted({m.obtained for m in etf})
    strip_saved = sorted({m.obtained for m in strip.members})
    _title(
        fig,
        "Exploratory: XLE against USO signed by crude oil's contango",
        f"Algorithmic Trading, location 2734. USO and XLE from {ETF_FILE}, saved "
        f"{', '.join(etf_saved)}, which subtracts dividends in dollars.\nContracts from "
        f"{STRIP_FILE}, saved {', '.join(strip_saved)}. No cost is charged.",
    )
    fig.subplots_adjust(left=0.1, right=0.97, top=0.9, bottom=0.09)
    return _save(fig, out, FIGURE)


def main() -> None:
    try:
        make_xle_uso_roll_return_figure()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day reaches the reader
        # as one line, the way chan.xle_uso_roll_return.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / FIGURE}")


if __name__ == "__main__":
    main()
