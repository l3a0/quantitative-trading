"""The figure for the post on the price spread, log price spread and ratio, Example 3.1.

``blog/price-spread-ratio-lessons.md`` teaches what Entry 21 of the replication
log found, and
[issue 392](https://github.com/l3a0/quantitative-trading/issues/392) chose one
figure for it. :func:`make_signals_figure` draws four panels that share the date
axis over the 1,480 rows the three scripts trade.

1. The 20-day hedge ratio, with zero marked, because the ratio crosses it and on
   those days one unit holds both ETFs long.
2. The price spread ``USO − h·GLD``, which ``PriceSpread.m`` plots and the book
   prints as Figure 3.1 at location 1505.
3. The ratio USO/GLD, which ``Ratio.m`` plots and the book prints as Figure 3.2.
4. The compounded cumulative return of every run, which each script plots
   last. The ratio with GLD and USO swapped is drawn dashed, because it was a
   reading tried after the published script missed.

Every value comes from :func:`chan.price_spread.read_sources` and
:func:`chan.price_spread.example_three_one`, the run's own path, so the
scale-break guard runs here too::

    uv run python -m chan.price_spread_figures
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from matplotlib.dates import DateFormatter, YearLocator
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.paths import FIGURES_DIR
from chan.price_spread import (
    LOOKBACK,
    SOURCE_FILE,
    ExampleThreeOne,
    Run,
    example_three_one,
    read_sources,
)
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED, SURFACE
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable

SIGNALS_FIGURE = "price_spread_signals.png"

#: Each run's line on the bottom panel: its label, colour and dash.
RUNS = (
    ("price_spread", "price spread", INK, "-"),
    ("log_price_spread", "log price spread", ACCENT, "-"),
    ("ratio", "ratio, as Ratio.m publishes it", LOST, "-"),
    ("swapped_ratio", "ratio, GLD and USO swapped, tried after the miss", LOST, "--"),
)


def cumulative_return(run: Run) -> np.ndarray:
    """``cumprod(1 + ret) − 1``, the line each script's last ``plot`` draws."""
    return np.cumprod(1 + run.daily) - 1


def legend_label(run: Run, label: str) -> str:
    """A run's label with the two figures its script prints."""
    return f"{label}: APR {run.apr:.6f}, Sharpe ratio {run.sharpe:.6f}"


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


@_plain_text
def make_signals_figure(out: Path | None = None, result: ExampleThreeOne | None = None) -> Figure:
    """The hedge ratio, the spread, the ratio and every run's cumulative return."""
    if result is None:
        result = example_three_one(read_sources()[1])
    days = result.price_spread.signal.days
    hedge = result.price_spread.signal.hedge
    negative = int((hedge < 0).sum())

    fig = Figure(figsize=(10, 13), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    hedge_ax, spread_ax, ratio_ax, return_ax = fig.subplots(
        4, 1, sharex=True, gridspec_kw={"height_ratios": (1, 1, 1, 1.35)}
    )
    for ax in (hedge_ax, spread_ax, ratio_ax, return_ax):
        _style(ax)

    hedge_ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    hedge_ax.fill_between(
        days, hedge, 0, where=hedge < 0, color=LOST, alpha=0.25, lw=0, gid="negative"
    )
    hedge_ax.plot(days, hedge, color=ACCENT, lw=1.1, gid="hedge")
    hedge_ax.set_ylabel("GLD shares per USO share", color=INK, fontsize=10)
    _heading(
        hedge_ax,
        f"The hedge ratio h, refitted on the last {LOOKBACK} days.\n"
        f"Below zero on {negative} of {len(days):,} days, when one unit holds both ETFs long.",
    )

    spread_ax.axhline(0, color=MUTED, lw=0.9)
    spread_ax.plot(days, result.price_spread.signal.value, color=INK, lw=1.0, gid="spread")
    spread_ax.set_ylabel("dollars", color=INK, fontsize=10)
    _heading(spread_ax, "Figure 3.1: the price spread USO − h·GLD.")

    ratio_ax.plot(days, result.ratio.signal.value, color=LOST, lw=1.1, gid="ratio")
    ratio_ax.set_ylabel("USO / GLD", color=INK, fontsize=10)
    _heading(ratio_ax, "Figure 3.2: the ratio USO/GLD.")

    return_ax.axhline(0, color=MUTED, lw=0.9)
    for attribute, label, colour, dash in RUNS:
        run = getattr(result, attribute)
        return_ax.plot(
            days,
            cumulative_return(run),
            color=GOOD if attribute == "price_spread" else colour,
            ls=dash,
            lw=1.6 if attribute == "price_spread" else 1.2,
            gid=attribute,
            label=legend_label(run, label),
        )
    # The legend takes the band above the highest line, where it covers nothing.
    lines = [cumulative_return(getattr(result, attribute)) for attribute, *_ in RUNS]
    low, high = min(line.min() for line in lines), max(line.max() for line in lines)
    return_ax.set_ylim(low - 0.08 * (high - low), high + 0.45 * (high - low))
    return_ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    return_ax.set_ylabel("cumulative return, compounded", color=INK, fontsize=10)
    return_ax.legend(loc="upper left", frameon=False, fontsize=9, labelcolor=INK)
    _heading(return_ax, "Each run's compounded return, unlevered and before costs.")
    return_ax.set_xlim(days[0], days[-1])
    return_ax.xaxis.set_major_locator(YearLocator())
    return_ax.xaxis.set_major_formatter(DateFormatter("%Y"))

    _title(
        fig,
        "Exploratory: Example 3.1 redrawn on Chan's own GLD and USO closes",
        f"Example 3.1 of Algorithmic Trading, {days[0].date()} to {days[-1].date()}, the "
        f"{len(days):,} days left once the first {LOOKBACK} are dropped.\n"
        f"Prices from {SOURCE_FILE}, saved 2012-04-10. Chan's {LOOKBACK}-day lookback was "
        "chosen with hindsight, so every figure is in-sample.",
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.975))
    return _save(fig, out, SIGNALS_FIGURE)


def main() -> None:
    try:
        make_signals_figure()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source is worth nothing at the bottom of a
        # traceback, so it reaches the operator as one line, the way
        # chan.price_spread.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / SIGNALS_FIGURE}")


if __name__ == "__main__":
    main()
