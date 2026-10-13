"""The charts for the post on USD.CAD's mean reversion, *Algorithmic Trading*'s Examples 2.1 to 2.5.

The post teaches what Entry 22 of the replication log found, and
[issue 459](https://github.com/l3a0/quantitative-trading/issues/459) chose one
figure for it. :func:`make_usdcad_figure` draws two panels that share the date
axis over the 1,216 closes ``stationarityTests.m`` reads.

1. The closes with their moving average over the run's lookback, the
   half-life rounded, which is the level Example 2.5 bets the close returns
   to. The average starts once its window has filled, and the rule holds
   nothing before then. The script draws the closes with ``plot(y)``.
2. The cumulative P&L, which the script draws with ``plot(cumsum(pnl))``, with
   the deepest fall below its running maximum shaded, so the "large drawdown"
   location 1225 names has a scale beside the total.

Lesson 4 of the post then reads the deepest fall day by day, and
:func:`make_usdcad_fall_figure` draws it as a second figure. Three panels share
one date axis from the fall's peak to its trough, and a thin vertical line
crosses all three on the day of the largest short.

1. The closes and their moving average, as in the first figure's top panel,
   with a band of one moving standard deviation either side of the average.
   The position counts the close's distance from the average in that unit, so
   the band shows why the largest short is not where the gap in price is
   widest.
2. The position the rule holds at each close, which is
   :func:`chan.usdcad_mean_reversion.market_value`, with the largest short and
   the position on the trough day marked. The script never plots it.
3. The cumulative P&L over the same days, with the peak and the trough marked.

The closes, the lookback, the P&L and the drawdown come from
:func:`chan.usdcad_mean_reversion.read_sources` and
:func:`chan.usdcad_mean_reversion.stationarity_tests`, the run's own path, so
the scale-break guard runs here too. The run keeps its moving average inside
:func:`chan.usdcad_mean_reversion.linear_mean_reversion` rather than returning
it, so the top panel draws it with the same ``movingAvg`` over the run's own
lookback. The second figure reads the position the same way, from
``market_value`` over the run's own lookback, and its band from ``movingStd``
over the same lookback. Every value and date either figure prints comes from
the run. Redraw both with::

    uv run python -m chan.usdcad_mean_reversion_figures
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from matplotlib.dates import DateFormatter, MonthLocator, YearLocator
from matplotlib.figure import Figure

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.matlab_helpers import moving_avg, moving_std
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED, SURFACE
from chan.series import WindowCrossesScaleBreak
from chan.usdcad_mean_reversion import (
    StationarityRun,
    market_value,
    read_sources,
    stationarity_tests,
)
from chan.vintage import VintageEntry, VintageUnavailable

USDCAD_FIGURE = "usdcad_mean_reversion.png"
USDCAD_FALL_FIGURE = "usdcad_fall_position.png"
#: Calendar days of empty axis either side of the fall, so the marks on its
#: first and last days sit clear of the frame.
FALL_MARGIN = pd.Timedelta(days=3)


def moving_average(run: StationarityRun) -> pd.Series:
    """``movingAvg(y, lookback)`` on the run's closes, NaN until the window fills."""
    return pd.Series(
        moving_avg(run.closes.to_numpy(dtype=float), run.lookback), index=run.closes.index
    )


def moving_deviation(run: StationarityRun) -> pd.Series:
    """``movingStd(y, lookback)`` on the run's closes, the unit the position counts in."""
    return pd.Series(
        moving_std(run.closes.to_numpy(dtype=float), run.lookback), index=run.closes.index
    )


def cumulative_pnl(run: StationarityRun) -> pd.Series:
    """``cumsum(pnl)``, the line the script's last ``plot`` draws."""
    return run.pnl.cumsum()


def position(run: StationarityRun) -> pd.Series:
    """``mktVal`` on each close, the position the rule holds, NaN until the window fills."""
    y = run.closes.to_numpy(dtype=float)
    return pd.Series(market_value(y, run.lookback), index=run.closes.index)


def fall_days(run: StationarityRun) -> pd.DatetimeIndex:
    """The closes from the drawdown's peak to its trough, both included."""
    days = run.closes.index
    return days[(days >= run.drawdown.peak) & (days <= run.drawdown.trough)]


def signed(value: float, places: int = 3) -> str:
    """``value`` to ``places`` decimals with a true minus sign, as the post prints it."""
    return f"{value:.{places}f}".replace("-", "−")


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


@_plain_text
def make_usdcad_figure(
    out: Path | None = None,
    sources: tuple[VintageEntry, pd.Series] | None = None,
) -> Figure:
    """The closes with their moving average, and the cumulative P&L with its drawdown."""
    entry, closes = sources if sources is not None else read_sources()
    run = stationarity_tests(entry, closes)
    days = run.closes.index
    average = moving_average(run)
    started = average.first_valid_index()
    cumulative = cumulative_pnl(run)
    drawdown = run.drawdown
    high, low = cumulative[drawdown.peak], cumulative[drawdown.trough]

    fig = Figure(figsize=(10, 9), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    close_ax, pnl_ax = fig.subplots(2, 1, sharex=True, gridspec_kw={"height_ratios": (1, 1)})
    for ax in (close_ax, pnl_ax):
        _style(ax)

    close_ax.plot(days, run.closes, color=INK, lw=0.8, gid="closes", label="close at 16:59")
    close_ax.plot(
        days,
        average,
        color=ACCENT,
        lw=1.6,
        gid="moving-average",
        label=f"{run.lookback}-day moving average",
    )
    close_ax.set_ylabel("Canadian dollars per US dollar", color=INK, fontsize=10)
    close_ax.legend(loc="upper right", frameon=False, fontsize=9.5, labelcolor=INK)
    _heading(
        close_ax,
        f"The {len(days):,} closes of USD.CAD and their {run.lookback}-day moving average, "
        f"the half-life of {run.half_life:.1f} days rounded.\nThe rule sells when the close "
        "is above the average and buys when it is below, sized by the distance in deviations.\n"
        f"The average starts on {started.date()}, once its window has filled.",
    )

    pnl_ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    pnl_ax.axvspan(drawdown.peak, drawdown.trough, color=LOST, alpha=0.12, lw=0, gid="drawdown")
    pnl_ax.plot(days, cumulative, color=GOOD, lw=1.2, gid="pnl")
    pnl_ax.plot([drawdown.peak], [high], "o", color=INK, ms=4.5, gid="peak")
    pnl_ax.plot([drawdown.trough], [low], "o", color=LOST, ms=4.5, gid="trough")
    pnl_ax.set_ylabel("cumulative P&L, summed", color=INK, fontsize=10)
    _heading(
        pnl_ax,
        f"The cumulative P&L, flat until {run.first_position.date()} and ending at "
        f"{signed(run.total_pnl)}. Unlevered and before costs.\nThe shaded fall runs from "
        f"{signed(high)} on {drawdown.peak.date()} to {signed(low)} on "
        f"{drawdown.trough.date()}, {signed(drawdown.depth)} deep.",
    )
    pnl_ax.set_xlim(days[0], days[-1])
    pnl_ax.xaxis.set_major_locator(YearLocator())
    pnl_ax.xaxis.set_major_formatter(DateFormatter("%Y"))

    _title(
        fig,
        "Exploratory: linear mean reversion redrawn on Chan's own USD.CAD closes",
        f"Examples 2.1 to 2.5 of Algorithmic Trading, {days[0].date()} to "
        f"{days[-1].date()}, the 16:59 bar of each day.\nCloses from {entry.path}, saved "
        f"{entry.obtained}.\nThe {run.lookback}-day lookback comes from the half-life of "
        "the same closes the rule trades, so every figure is in-sample.",
    )
    fig.tight_layout(rect=(0, 0.075, 1, 0.97))
    return _save(fig, out, USDCAD_FIGURE)


def _mark(ax, day, value, colour: str, gid: str) -> None:
    ax.plot([day], [value], "o", color=colour, ms=6, mec=SURFACE, mew=1.4, zorder=3, gid=gid)


def _label(
    ax, text: str, day, value, offset: tuple[float, float], ha: str, gid: str, va: str = "center"
) -> None:
    ax.annotate(
        text,
        (day, value),
        xytext=offset,
        textcoords="offset points",
        ha=ha,
        va=va,
        linespacing=1.3,
        color=INK,
        fontsize=9.5,
        gid=gid,
    )


@_plain_text
def make_usdcad_fall_figure(
    out: Path | None = None,
    sources: tuple[VintageEntry, pd.Series] | None = None,
) -> Figure:
    """The closes, the position held and the cumulative P&L from the fall's peak to its trough."""
    entry, closes = sources if sources is not None else read_sources()
    run = stationarity_tests(entry, closes)
    days = fall_days(run)
    peak, trough = run.drawdown.peak, run.drawdown.trough
    held = position(run)[days]
    average = moving_average(run)[days]
    deviation = moving_deviation(run)[days]
    cumulative = cumulative_pnl(run)[days]
    deepest = held.idxmin()
    rise = run.closes[trough] / run.closes[peak] - 1
    further = run.closes[trough] / run.closes[deepest] - 1
    gap = run.closes[days] - average
    gap_grew = gap[trough] / gap[deepest] - 1
    deviation_grew = deviation[trough] / deviation[deepest] - 1

    fig = Figure(figsize=(10, 10.5), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    close_ax, held_ax, pnl_ax = fig.subplots(3, 1, sharex=True)
    for ax in (close_ax, held_ax, pnl_ax):
        _style(ax)
        ax.axvline(deepest, color=MUTED, lw=0.9, ls=(0, (4, 3)), zorder=1, gid="guide")

    close_ax.plot(days, run.closes[days], color=INK, lw=1.2, gid="closes", label="close at 16:59")
    close_ax.plot(
        days,
        average,
        color=ACCENT,
        lw=1.6,
        gid="moving-average",
        label=f"{run.lookback}-day moving average",
    )
    close_ax.fill_between(
        days,
        average - deviation,
        average + deviation,
        color=ACCENT,
        alpha=0.16,
        lw=0,
        gid="deviation-band",
        label="average ± one moving deviation",
    )
    close_ax.set_ylabel("Canadian dollars per US dollar", color=INK, fontsize=10)
    close_ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK)
    _heading(
        close_ax,
        f"USD.CAD rose from {run.closes[peak]:.5f} on {peak.date()} to "
        f"{run.closes[trough]:.5f} on {trough.date()}, {100 * rise:.1f} percent.\n"
        f"It closed at {run.closes[deepest]:.5f} on {deepest.date()}, the dashed line, and "
        f"rose another {100 * further:.1f} percent after it.\nThe band is one moving "
        "standard deviation either side of the average, the unit the position counts in.",
    )

    held_ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    held_ax.fill_between(days, held, 0, where=held < 0, color=LOST, alpha=0.14, lw=0, gid="short")
    held_ax.plot(days, held, color=LOST, lw=1.4, gid="position")
    _mark(held_ax, deepest, held[deepest], LOST, "deepest")
    _mark(held_ax, trough, held[trough], INK, "trough-position")
    _label(
        held_ax,
        f"largest short {signed(held[deepest], 2)}, {deepest.date()}",
        deepest,
        held[deepest],
        (-9, -4),
        "right",
        "deepest-label",
    )
    _label(
        held_ax,
        f"{signed(held[trough], 2)}, {trough.date()}",
        trough,
        held[trough],
        (-4, -16),
        "right",
        "trough-position-label",
    )
    held_ax.set_ylabel("position, minus the z-score", color=INK, fontsize=10)
    _heading(
        held_ax,
        "The position held at each close, minus the close's distance from its average in "
        "moving deviations.\nIt is largest when the close stands furthest above the average "
        "in deviations, not in price.\n"
        f"From {deepest.date()} to {trough.date()} the gap in price grew "
        f"{100 * gap_grew:.0f} percent and the moving deviation {100 * deviation_grew:.0f} "
        "percent.",
    )

    pnl_ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    pnl_ax.plot(days, cumulative, color=GOOD, lw=1.4, gid="pnl")
    _mark(pnl_ax, peak, cumulative[peak], INK, "peak")
    _mark(pnl_ax, trough, cumulative[trough], LOST, "trough")
    _label(
        pnl_ax,
        f"high {signed(cumulative[peak], 4)}, {peak.date()}",
        peak,
        cumulative[peak],
        (9, 6),
        "left",
        "peak-label",
    )
    _label(
        pnl_ax,
        f"low {signed(cumulative[trough], 4)}\n{trough.date()}",
        trough,
        cumulative[trough],
        (-2, -7),
        "right",
        "trough-label",
        va="top",
    )
    pnl_ax.set_ylabel("cumulative P&L, summed", color=INK, fontsize=10)
    _heading(
        pnl_ax,
        f"The cumulative P&L falls {signed(run.drawdown.depth, 4)} over the same days. "
        "Unlevered and before costs.\nEach day earns the previous close's position times "
        "the day's return.",
    )
    for ax, (low, high) in (
        (held_ax, (held.min(), 0)),
        (pnl_ax, (cumulative.min(), cumulative.max())),
    ):
        # Room below the lowest mark for the label under it, and above the
        # highest for the label beside it.
        span = high - low
        ax.set_ylim(low - 0.24 * span, high + 0.16 * span)

    pnl_ax.set_xlim(days[0] - FALL_MARGIN, days[-1] + FALL_MARGIN)
    pnl_ax.xaxis.set_major_locator(MonthLocator())
    pnl_ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))

    _title(
        fig,
        "Exploratory: the position the linear rule held through its deepest fall",
        f"Example 2.5 of Algorithmic Trading on Chan's own USD.CAD closes, {peak.date()} to "
        f"{trough.date()}, the 16:59 bar of each day.\nCloses from {entry.path}, saved "
        f"{entry.obtained}.\nThe {run.lookback}-day lookback comes from the half-life of "
        "the same closes the rule trades, so every figure is in-sample.",
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.97))
    return _save(fig, out, USDCAD_FALL_FIGURE)


def main() -> None:
    try:
        make_usdcad_figure()
        make_usdcad_fall_figure()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day is worth nothing at
        # the bottom of a traceback, so it reaches the operator as one line, the
        # way chan.usdcad_mean_reversion.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / USDCAD_FIGURE}")
    print(f"wrote {FIGURES_DIR / USDCAD_FALL_FIGURE}")


if __name__ == "__main__":
    main()
