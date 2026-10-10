"""The figure for the post on Bollinger bands on GLD and USO, *Algorithmic Trading*'s Example 3.2.

``blog/bollinger-band-lessons.md`` teaches what Entry 26 of the replication log
found, and [issue 430](https://github.com/l3a0/quantitative-trading/issues/430)
chose one figure for it. :func:`make_bollinger_figure` draws three panels that
share the date axis over the 1,480 rows ``bollinger.m`` trades.

1. The price spread's 20-day z-score, with lines at −1, 0 and 1. A long enters
   below −1 and a short above 1, and each exits when the z-score crosses 0.
2. The units held, which are only ever −1, 0 or 1.
3. The band's compounded cumulative return, which ``bollinger.m`` plots and
   the book prints as Figure 3.3 at location 1559, beside Example 3.1's linear
   rule on the same spread. The band with the moving deviation divided by n
   rather than n − 1 is drawn dashed, because it is a diagnostic rather than
   Chan's run.

The band, the linear rule and the spread come from
:func:`chan.price_spread.read_sources` and
:func:`chan.bollinger.example_three_two`, the run's own path, so the
scale-break guard runs here too. The dashed line comes from
:func:`divided_by_n` instead. It reuses that run's spread and recomputes the
z-score with ``smartMovingStd`` in place of ``movingStd``, and
``tests/test_bollinger_figures.py`` holds it equal to the patched run that
``tests/test_bollinger.py`` builds. Redraw it with::

    uv run python -m chan.bollinger_figures
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter, YearLocator
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter

from chan.bollinger import ENTRY_ZSCORE, EXIT_ZSCORE, band_units, example_three_two
from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.matlab_helpers import moving_avg, smart_moving_std
from chan.paths import FIGURES_DIR
from chan.price_spread import LOOKBACK, SOURCE_FILE, Run, daily_returns, read_sources
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED, SURFACE
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageEntry, VintageUnavailable

BOLLINGER_FIGURE = "bollinger_band.png"

#: Each run's line on the bottom panel: its gid, label, colour, dash and width.
RUNS = (
    ("bollinger", "the band, bollinger.m", GOOD, "-", 1.7),
    ("linear", "the linear rule, Example 3.1", ACCENT, "-", 1.2),
    ("by_n", "the band, deviation divided by n, a diagnostic", GOOD, "--", 1.1),
)

#: The z-score panel's three lines: the level, its gid and its colour.
BANDS = (
    (-ENTRY_ZSCORE, "long-entry", LOST),
    (EXIT_ZSCORE, "exit", MUTED),
    (ENTRY_ZSCORE, "short-entry", LOST),
)


def cumulative_return(run: Run) -> np.ndarray:
    """``cumprod(1 + ret) − 1``, the line ``bollinger.m``'s last ``plot`` draws."""
    return np.cumprod(1 + run.daily) - 1


def divided_by_n(run: Run, lookback: int = LOOKBACK) -> Run:
    """The band on ``run``'s spread with ``smartMovingStd``, which divides by n.

    Everything else is :func:`chan.bollinger.bollinger_band`'s: the same
    ``movingAvg``, the same thresholds and the same returns.
    """
    signal = run.signal
    with np.errstate(invalid="ignore", divide="ignore"):
        z = (signal.value - moving_avg(signal.value, lookback)) / smart_moving_std(
            signal.value, lookback
        )
        units = band_units(z < -ENTRY_ZSCORE, z > -EXIT_ZSCORE, z > ENTRY_ZSCORE, z < EXIT_ZSCORE)
    positions = units[:, None] * signal.unit_dollars
    return Run(signal, units, positions, daily_returns(positions, signal.prices))


def legend_label(run: Run, label: str) -> str:
    """A run's label with the two figures its script prints."""
    return f"{label}: APR {run.apr:.6f}, Sharpe ratio {run.sharpe:.6f}"


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


@_plain_text
def make_bollinger_figure(
    out: Path | None = None,
    sources: tuple[list[VintageEntry], pd.DataFrame] | None = None,
) -> Figure:
    """The z-score with its band, the units held, and each run's cumulative return."""
    members, closes = sources if sources is not None else read_sources()
    result = example_three_two(closes)
    band = result.bollinger
    days = band.signal.days
    runs = {"bollinger": band, "linear": result.linear, "by_n": divided_by_n(band)}

    fig = Figure(figsize=(10, 11.5), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    z_ax, units_ax, return_ax = fig.subplots(
        3, 1, sharex=True, gridspec_kw={"height_ratios": (1.1, 0.6, 1.35)}
    )
    for ax in (z_ax, units_ax, return_ax):
        _style(ax)

    for level, gid, colour in BANDS:
        z_ax.axhline(level, color=colour, lw=1.0, ls="--" if level else "-", gid=gid)
    z_ax.plot(days, result.zscore, color=INK, lw=0.8, gid="zscore")
    reach = np.nanmax(np.abs(result.zscore))
    z_ax.set_ylim(-1.08 * reach, 1.08 * reach)
    z_ax.set_ylabel("z-score", color=INK, fontsize=10)
    _heading(
        z_ax,
        f"The {LOOKBACK}-day z-score of the price spread USO − h·GLD.\n"
        f"A long enters below −{ENTRY_ZSCORE} and a short above {ENTRY_ZSCORE}, "
        f"and each exits when the z-score crosses {EXIT_ZSCORE}.",
    )

    units = band.units
    values, counts = np.unique(units, return_counts=True)
    held = dict(zip(values.tolist(), counts.tolist(), strict=True))
    changes = int(np.count_nonzero(np.diff(units)))
    linear_changes = int(np.count_nonzero(np.diff(result.linear.units[LOOKBACK - 1 :])))
    units_ax.plot(days, units, color=INK, lw=0.9, drawstyle="steps-post", gid="units")
    units_ax.set_yticks([-1, 0, 1], ["short −1", "flat 0", "long 1"])
    units_ax.set_ylim(-1.35, 1.35)
    units_ax.set_ylabel("units held", color=INK, fontsize=10)
    _heading(
        units_ax,
        f"The units held: short on {held[-1.0]:,} days, flat on {held[0.0]:,} and long on "
        f"{held[1.0]:,}.\nThey change on {changes:,} days, where the linear rule's change on "
        f"{linear_changes:,}.",
    )

    return_ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    for gid, label, colour, dash, width in RUNS:
        run = runs[gid]
        return_ax.plot(
            days,
            cumulative_return(run),
            color=colour,
            ls=dash,
            lw=width,
            gid=gid,
            label=legend_label(run, label),
        )
    # The legend takes the band above the highest line, where it covers nothing.
    lines = [cumulative_return(run) for run in runs.values()]
    low, high = min(line.min() for line in lines), max(line.max() for line in lines)
    return_ax.set_ylim(low - 0.08 * (high - low), high + 0.4 * (high - low))
    return_ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    return_ax.set_ylabel("cumulative return, compounded", color=INK, fontsize=10)
    return_ax.legend(loc="upper left", frameon=False, fontsize=9, labelcolor=INK)
    _heading(
        return_ax,
        "Figure 3.3: the band's compounded return, beside the linear rule's on the same "
        "spread.\nUnlevered and before costs. The dashed line is a diagnostic, not Chan's run.",
    )
    return_ax.set_xlim(days[0], days[-1])
    return_ax.xaxis.set_major_locator(YearLocator())
    return_ax.xaxis.set_major_formatter(DateFormatter("%Y"))

    saved = sorted({m.obtained for m in members})
    _title(
        fig,
        "Exploratory: Example 3.2 redrawn on Chan's own GLD and USO closes",
        f"Example 3.2 of Algorithmic Trading, {days[0].date()} to {days[-1].date()}, the "
        f"{len(days):,} days left once the first {LOOKBACK} are dropped.\n"
        f"Prices from {SOURCE_FILE}, saved {', '.join(saved)}. Chan's {LOOKBACK}-day lookback "
        "was chosen with hindsight, so every figure is in-sample.",
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.975))
    return _save(fig, out, BOLLINGER_FIGURE)


def main() -> None:
    try:
        make_bollinger_figure()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day is worth nothing at
        # the bottom of a traceback, so it reaches the operator as one line, the
        # way chan.bollinger.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / BOLLINGER_FIGURE}")


if __name__ == "__main__":
    main()
