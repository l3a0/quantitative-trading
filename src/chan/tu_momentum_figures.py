"""The figure for the post on time-series momentum on TU, *Algorithmic Trading*'s Example 6.1.

The post is ``blog/tu-momentum-lessons.md``.

The post teaches what Entry 33 of the replication log found, and
[issue 453](https://github.com/l3a0/quantitative-trading/issues/453) chose one
figure for it. :func:`make_tu_figure` draws two panels that share the date axis
over the 2,000 closes ``TU_mom.m`` reads.

1. TU's closes, so a reader can see the price the rule was long on. The issue
   added this panel to the script's plot, because the post's point that the
   rule held its longs through a rising price cannot be read from the curve
   alone. The close's highest point is marked.
2. The cumulative return, which the script draws with
   ``plot(cumprod(1+ret)-1)``. The deepest drawdown ``calculateMaxDD`` finds is
   shaded, the curve's highest point is marked, and a vertical line marks
   2009-01-02, where the script's active line starts, so a reader sees how
   much of the gain came before the window that line reads.

The closes come from :func:`chan.tu_momentum.read_sources`, so the
scale-break guard runs here too, and the returns from the run's own
:func:`chan.tu_momentum.signals`, :func:`chan.tu_momentum.positions`,
:func:`chan.tu_momentum.market_returns` and
:func:`chan.tu_momentum.strategy_returns`. The drawdown is
:func:`chan.cross_sectional_momentum_figures.deepest_drawdown`, which reads the
loop ``calculateMaxDD`` runs. Redraw it with::

    uv run python -m chan.tu_momentum_figures
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter, YearLocator
from matplotlib.figure import Figure

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.cross_sectional_momentum_figures import deepest_drawdown
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED, SURFACE
from chan.series import WindowCrossesScaleBreak
from chan.tu_momentum import (
    ACTIVE_LINE_START,
    HOLD_DAYS,
    LOOKBACK,
    market_returns,
    positions,
    read_sources,
    signals,
    strategy_returns,
)
from chan.usdcad_mean_reversion_figures import signed
from chan.vintage import VintageEntry, VintageUnavailable

TU_FIGURE = "tu_momentum.png"


def daily_returns(closes: pd.Series) -> np.ndarray:
    """``ret``, the rule's daily return over every close, through the run's own four steps."""
    cl = closes.to_numpy(dtype=float)
    return strategy_returns(positions(*signals(cl)), market_returns(cl))


def cumulative_return(daily: np.ndarray) -> np.ndarray:
    """``cumprod(1+ret)-1``, the line the script's ``plot`` draws."""
    return np.cumprod(1 + daily) - 1


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


@_plain_text
def make_tu_figure(
    out: Path | None = None,
    sources: tuple[VintageEntry, pd.Series] | None = None,
) -> Figure:
    """TU's closes, and the cumulative return with its drawdown, its high and the active line."""
    entry, closes = sources if sources is not None else read_sources()
    days = closes.index
    daily = daily_returns(closes)
    cumulative = cumulative_return(daily)
    first = days[int(np.flatnonzero(daily)[0])]
    drawdown = deepest_drawdown(cumulative)
    top = int(np.argmax(cumulative))
    close_top = int(np.argmax(closes.to_numpy()))
    active = days.get_loc(ACTIVE_LINE_START)

    fig = Figure(figsize=(10, 9), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    close_ax, return_ax = fig.subplots(2, 1, sharex=True, gridspec_kw={"height_ratios": (1, 1)})
    for ax in (close_ax, return_ax):
        _style(ax)

    close_ax.plot(days, closes, color=INK, lw=0.8, gid="closes", label="TU's daily close")
    close_ax.plot(
        [days[close_top]],
        [closes.iloc[close_top]],
        "o",
        color=ACCENT,
        ms=5,
        gid="close-high",
        label=f"highest close, {closes.iloc[close_top]:.4f} on {days[close_top].date()}",
    )
    close_ax.set_ylabel("close, back-adjusted", color=INK, fontsize=10)
    close_ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK)
    _heading(
        close_ax,
        f"The {len(days):,} closes of TU, the two-year Treasury note future, from "
        f"{closes.iloc[0]:.4f} to {closes.iloc[-1]:.4f}.\nThe rule is long when the close is "
        f"above the close {LOOKBACK} days back and short when it is below.\nEach day's call "
        f"is held {HOLD_DAYS} days with 1/{HOLD_DAYS} of the capital.",
    )

    return_ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    return_ax.axvspan(
        days[drawdown.high],
        days[drawdown.trough],
        color=LOST,
        alpha=0.15,
        lw=0,
        gid="drawdown",
        label=f"deepest drawdown, {signed(drawdown.depth, 6)}",
    )
    return_ax.axvline(
        ACTIVE_LINE_START,
        color=MUTED,
        lw=1.1,
        ls="--",
        gid="active-line",
        label=f"{ACTIVE_LINE_START.date()}, where the script's active line starts",
    )
    return_ax.plot(
        days, cumulative, color=GOOD, lw=1.3, gid="cumulative", label="the rule's cumulative return"
    )
    return_ax.plot(
        [days[top]],
        [cumulative[top]],
        "o",
        color=ACCENT,
        ms=5,
        gid="high",
        label=f"highest point, {cumulative[top]:.6f} on {days[top].date()}",
    )
    return_ax.set_ylabel("cumulative return, compounded", color=INK, fontsize=10)
    return_ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK)
    _heading(
        return_ax,
        f"The cumulative return, flat until {first.date()} and ending at "
        f"{cumulative[-1]:.6f}. Unlevered and before costs.\nIt stands at "
        f"{cumulative[active]:.6f} on {ACTIVE_LINE_START.date()}. The shaded drawdown runs "
        f"from the high on {days[drawdown.high].date()}\nto the low on "
        f"{days[drawdown.trough].date()}, {signed(drawdown.depth, 6)} against the account's "
        "value at the high.",
    )
    return_ax.set_xlim(days[0], days[-1])
    return_ax.xaxis.set_major_locator(YearLocator())
    return_ax.xaxis.set_major_formatter(DateFormatter("%Y"))

    _title(
        fig,
        "Exploratory: time-series momentum redrawn on Chan's own TU closes",
        f"Example 6.1 of Algorithmic Trading, {days[0].date()} to {days[-1].date()}, "
        f"TU_mom.m with idx = 1.\nCloses from {entry.path}, {entry.obtained_verb} "
        f"{entry.obtained}.\n"
        f"The {LOOKBACK}-day lookback and {HOLD_DAYS}-day hold were chosen from a table of the "
        "same closes, so every figure is in-sample.",
    )
    fig.tight_layout(rect=(0, 0.075, 1, 0.97))
    return _save(fig, out, TU_FIGURE)


def main() -> None:
    try:
        make_tu_figure()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day is worth nothing at
        # the bottom of a traceback, so it reaches the operator as one line, the
        # way chan.tu_momentum.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / TU_FIGURE}")


if __name__ == "__main__":
    main()
