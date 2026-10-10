"""The figure for the post on the Kalman filter hedge ratio on EWA and EWC.

``blog/kalman-hedge-lessons.md`` teaches what Entry 32 of the replication log
found. :func:`make_kalman_figure` draws four panels on one date axis over the
file's 1,500 days, after the book's Figures 3.5 to 3.8, in the order the post
reads them.

1. The slope after each day's update, over every row as the script plots it,
   so the zero start on the file's first day shows. A dashed line marks 1,
   the level location 1726 says the slope oscillates around.
2. The intercept after each day's update, with each calendar year's mean
   drawn as a flat step over that year and the intercept's highest value
   marked. The steps are the yearly grain, at which every mean is above the
   one before, and the line beneath them is the daily grain, at which it
   falls on many steps.
3. The forecast error and the band of plus and minus one forecast standard
   deviation, from row 3, as the script plots them. Rows 1 and 2 sit far off
   that axis, and a note names their values, because the script trades on
   both.
4. The compounded cumulative return of the script, and dashed, of the same
   run with no signal on rows 1 and 2.

Every value comes from :func:`chan.kalman_hedge.read_sources` and
:func:`chan.kalman_hedge.kalman_hedge`, the run's own path, so the
scale-break guard runs here too::

    uv run python -m chan.kalman_hedge_figures
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter, YearLocator
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.kalman_hedge import (
    BOOK_APR_PERCENT,
    BOOK_SHARPE,
    DELTA,
    QUIET_ROWS,
    SOURCE_FILE,
    VE,
    KalmanHedge,
    Trade,
    X,
    Y,
    intercept_findings,
    kalman_hedge,
    read_sources,
    slope_findings,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED, SURFACE
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageEntry, VintageUnavailable

KALMAN_FIGURE = "kalman_hedge.png"

#: The colour of each line that a legend or a heading names.
COLOURS = {
    "slope": INK,
    "start": LOST,
    "intercept": INK,
    "yearly": ACCENT,
    "peak": LOST,
    "error": INK,
    "band": ACCENT,
    "script": INK,
    "quiet-start": GOOD,
}


def cumulative_return(run: Trade) -> np.ndarray:
    """``cumprod(1 + ret) − 1``, the series the script's last ``plot`` draws."""
    return np.cumprod(1 + run.daily) - 1


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


def _slope_panel(ax, result: KalmanHedge) -> None:
    f = result.filter
    found = slope_findings(f.slope)
    ax.axhline(1, color=MUTED, lw=1.0, ls="--", gid="one")
    ax.plot(f.days, f.slope, color=COLOURS["slope"], lw=1.1, gid="slope")
    ax.plot(
        [f.days[0]],
        [f.slope[0]],
        "o",
        ms=6,
        color=COLOURS["start"],
        mec=SURFACE,
        mew=1.4,
        zorder=3,
        clip_on=False,
        gid="start",
    )
    ax.annotate(
        f"{f.slope[0]:g} on {f.days[0].date()}, where the filter starts",
        (f.days[0], f.slope[0]),
        xytext=(10, 0),
        textcoords="offset points",
        ha="left",
        va="center",
        color=COLOURS["start"],
        fontsize=9.5,
        fontweight="bold",
        gid="start-label",
    )
    ax.set_ylabel(f"shares of {X} per {Y}", color=INK, fontsize=10)
    _heading(
        ax,
        f"Figure 3.5: the slope, shares of {X} held against one share of {Y}, after each "
        "day's update.\n"
        f"Median {found.median:.6f}, "
        f"mean {found.mean:.6f}, above the dashed line at 1 on {found.rows_above_one} "
        f"of {found.rows:,} days.",
    )


def _intercept_panel(ax, result: KalmanHedge) -> None:
    f = result.filter
    found = intercept_findings(f.days, f.intercept)
    years = f.days.year
    ax.plot(f.days, f.intercept, color=COLOURS["intercept"], lw=1.1, gid="intercept")
    for year, mean in found.yearly.items():
        inside = f.days[years == year]
        ax.plot(
            [inside[0], inside[-1]],
            [mean, mean],
            color=COLOURS["yearly"],
            lw=2.4,
            solid_capstyle="butt",
            gid=f"year-{year}",
        )
    ax.plot(
        [found.peak_day],
        [found.peak],
        "o",
        ms=6,
        color=COLOURS["peak"],
        mec=SURFACE,
        mew=1.4,
        zorder=3,
        gid="peak",
    )
    ax.annotate(
        f"highest, {found.peak:.6f} on {found.peak_day.date()}",
        (found.peak_day, found.peak),
        xytext=(-8, 8),
        textcoords="offset points",
        ha="right",
        color=COLOURS["peak"],
        fontsize=9.5,
        fontweight="bold",
        gid="peak-label",
    )
    span = f.intercept.max() - f.intercept.min()
    ax.set_ylim(f.intercept.min() - 0.06 * span, f.intercept.max() + 0.2 * span)
    ax.set_ylabel("dollars", color=INK, fontsize=10)
    _heading(
        ax,
        "Figure 3.6: the intercept after each day's update, and each year's mean drawn "
        "flat over its year.\n"
        f"The yearly mean falls on {found.by_year.falls} of {found.by_year.steps} steps. "
        f"Day to day, the intercept falls on {found.by_day.falls} of "
        f"{found.by_day.steps:,} steps.",
    )


def _error_panel(ax, result: KalmanHedge) -> None:
    f = result.filter
    shown = slice(QUIET_ROWS, None)
    band = np.sqrt(f.variance)
    ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    ax.plot(
        f.days[shown],
        f.error[shown],
        color=COLOURS["error"],
        lw=0.8,
        gid="error",
        label="forecast error",
    )
    ax.plot(
        f.days[shown],
        band[shown],
        color=COLOURS["band"],
        lw=1.4,
        gid="upper",
        label="plus and minus one forecast standard deviation",
    )
    ax.plot(f.days[shown], -band[shown], color=COLOURS["band"], lw=1.4, gid="lower")
    low, high = f.error[shown].min(), f.error[shown].max()
    span = high - low
    ax.set_ylim(low - 0.3 * span, high + 0.3 * span)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK)
    first, second = (f"{f.days[t].date()}" for t in range(QUIET_ROWS))
    ax.text(
        0.99,
        0.04,
        f"Off this axis: {first} at {f.error[0]:.2f}, {Y}'s whole close,\n"
        f"and {second} at {f.error[1]:.2f}. The script trades on both.",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        color=LOST,
        fontsize=9.5,
        fontweight="bold",
        gid="off-axis",
    )
    ax.set_ylabel("dollars", color=INK, fontsize=10)
    _heading(
        ax,
        "Figure 3.7: the forecast error and the band, from row 3, as the script plots them.\n"
        "A short enters above the upper band and a long below the lower, and each exits "
        "back across its own band.",
    )


def _returns_panel(ax, result: KalmanHedge) -> None:
    days = result.filter.days
    ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    for gid, run, dash, label in (
        ("script", result.trade, "-", "the script"),
        ("quiet-start", result.quiet_start, "--", "no signal on rows 1 and 2"),
    ):
        ax.plot(
            days,
            cumulative_return(run),
            color=COLOURS[gid],
            lw=1.5,
            ls=dash,
            gid=gid,
            label=f"{label}, APR {run.apr:.6f}, Sharpe ratio {run.sharpe:.6f}",
        )
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.set_ylabel("cumulative return, compounded", color=INK, fontsize=10)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK)
    _heading(
        ax,
        "Figure 3.8: the cumulative return, unlevered and before costs.\n"
        f"The book prints {BOOK_APR_PERCENT} percent and {BOOK_SHARPE}, the script's "
        "figures rounded.",
    )


@_plain_text
def make_kalman_figure(
    out: Path | None = None,
    sources: tuple[list[VintageEntry], pd.DataFrame] | None = None,
) -> Figure:
    """The slope, the intercept, the forecast error and band, and the return."""
    members, closes = sources if sources is not None else read_sources()
    result = kalman_hedge(closes)
    days = result.filter.days

    fig = Figure(figsize=(10, 15), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    slope_ax, intercept_ax, error_ax, returns_ax = fig.subplots(
        4, 1, sharex=True, gridspec_kw={"hspace": 0.5}
    )
    for ax in (slope_ax, intercept_ax, error_ax, returns_ax):
        _style(ax)
        ax.tick_params(labelbottom=True)

    _slope_panel(slope_ax, result)
    _intercept_panel(intercept_ax, result)
    _error_panel(error_ax, result)
    _returns_panel(returns_ax, result)

    returns_ax.set_xlim(days[0], days[-1])
    returns_ax.xaxis.set_major_locator(YearLocator())
    returns_ax.xaxis.set_major_formatter(DateFormatter("%Y"))

    saved = sorted({m.obtained for m in members})
    _title(
        fig,
        f"Exploratory: the Kalman filter hedge on Chan's own {X} and {Y} closes",
        f"Algorithmic Trading, locations 1633 to 1726, {days[0].date()} to "
        f"{days[-1].date()}, {len(days):,} trading days, as KF_beta_EWA_EWC.m runs them.\n"
        f"Prices from {SOURCE_FILE}, saved {', '.join(saved)}. delta {DELTA:g} and Ve "
        f"{VE:g} are Chan's, and every figure is in-sample.",
    )
    fig.subplots_adjust(left=0.09, right=0.97, top=0.935, bottom=0.07)
    return _save(fig, out, KALMAN_FIGURE)


def main() -> None:
    try:
        make_kalman_figure()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day is worth nothing at
        # the bottom of a traceback, so it reaches the operator as one line, the
        # way chan.kalman_hedge.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / KALMAN_FIGURE}")


if __name__ == "__main__":
    main()
