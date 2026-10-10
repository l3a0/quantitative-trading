"""The figure for the post on USD.CAD's mean reversion, *Algorithmic Trading*'s Examples 2.1 to 2.5.

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

The closes, the lookback, the P&L and the drawdown come from
:func:`chan.usdcad_mean_reversion.read_sources` and
:func:`chan.usdcad_mean_reversion.stationarity_tests`, the run's own path, so
the scale-break guard runs here too. The run keeps its moving average inside
:func:`chan.usdcad_mean_reversion.linear_mean_reversion` rather than returning
it, so the top panel draws it with the same ``movingAvg`` over the run's own
lookback. Redraw it with::

    uv run python -m chan.usdcad_mean_reversion_figures
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from matplotlib.dates import DateFormatter, YearLocator
from matplotlib.figure import Figure

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.matlab_helpers import moving_avg
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED, SURFACE
from chan.series import WindowCrossesScaleBreak
from chan.usdcad_mean_reversion import (
    StationarityRun,
    read_sources,
    stationarity_tests,
)
from chan.vintage import VintageEntry, VintageUnavailable

USDCAD_FIGURE = "usdcad_mean_reversion.png"


def moving_average(run: StationarityRun) -> pd.Series:
    """``movingAvg(y, lookback)`` on the run's closes, NaN until the window fills."""
    return pd.Series(
        moving_avg(run.closes.to_numpy(dtype=float), run.lookback), index=run.closes.index
    )


def cumulative_pnl(run: StationarityRun) -> pd.Series:
    """``cumsum(pnl)``, the line the script's last ``plot`` draws."""
    return run.pnl.cumsum()


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


def main() -> None:
    try:
        make_usdcad_figure()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day is worth nothing at
        # the bottom of a traceback, so it reaches the operator as one line, the
        # way chan.usdcad_mean_reversion.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / USDCAD_FIGURE}")


if __name__ == "__main__":
    main()
