"""The figure for the post on three hypothesis tests on TU momentum, Example 1.1.

``blog/tu-hypothesis-tests-lessons.md`` teaches what Entry 37 of the
replication log found, and
[issue 480](https://github.com/l3a0/quantitative-trading/issues/480) chose one
figure for it. :func:`make_tu_hypothesis_tests_figure` draws three panels on
one horizontal axis of mean daily strategy return, with the observed mean
drawn as the same vertical line in each. Each panel holds one of the book's
tests beside the check, added after a trial run, that varies one input of it.

1. The Gaussian test's null, the density of the mean of 2,000 normal days
   with a mean of zero and the strategy's own spread, drawn as a dashed
   curve. Beside it, the means of the 10,000 type IV draws with their target
   mean removed.
2. The second test's 10,000 means on type IV draws, beside the means on
   normal draws with TU's mean and ``std`` taken from the same uniforms.
3. The corrected third test's 100,000 means on shuffled entry days.

Set side by side, panels 1 and 2 show what the drift does to the type IV
means: it moves their centre right and widens them. Panel 1 shows that the
drift-free draws nearly match the Gaussian null, and panel 3 how narrow the
shuffled means sit. The check that applies the observed positions to the
simulated returns is left out, because it answers where the script's comment
came from rather than what drives the count.

Every value comes from :func:`chan.tu_momentum.read_sources` and
:func:`chan.tu_hypothesis_tests.hypothesis_tests`, the run's own path, so the
scale-break guard runs here too. The run takes long enough that a caller
holding one can hand it in as ``result``, and the closes are still read for
the vintage the note names. Redraw it with::

    uv run python -m chan.tu_hypothesis_tests_figures
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter, MultipleLocator
from numpy.typing import NDArray
from scipy.special import ndtr
from scipy.stats import norm

from chan.coin_flip_figures import _plain_text, _save, _sci, _style, _title
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED, SURFACE
from chan.series import WindowCrossesScaleBreak
from chan.tu_hypothesis_tests import (
    RETURNS_SEED,
    TRADES_SEED,
    HypothesisTests,
    hypothesis_tests,
)
from chan.tu_momentum import HOLD_DAYS, LOOKBACK, PERIODS, read_sources
from chan.vintage import VintageEntry, VintageUnavailable

TU_HYPOTHESIS_TESTS_FIGURE = "tu_hypothesis_tests.png"

#: Bins across the shared axis. Every histogram uses the same edges, so the
#: panels compare bar for bar.
BINS = 150
#: Points the dashed Gaussian curve is drawn on.
CURVE_POINTS = 801
#: How far the shared axis reaches either side of the Gaussian null's centre,
#: in its spreads, unless a simulated mean lies further out.
NULL_REACH = 4.0
#: Padding beyond the widest value, as a share of the axis's span.
PAD = 0.03
#: How far each panel's top sits above its tallest value, so the legend clears the data.
HEADROOM = 1.55
#: The spacing of the axis's ticks, in mean daily return.
TICK = 5e-5


def gaussian_spread(result: HypothesisTests) -> float:
    """The Gaussian null's standard deviation of the mean, the daily ``std`` over √n."""
    return float(result.daily.std(ddof=1) / math.sqrt(len(result.daily)))


def panel_series(result: HypothesisTests) -> dict[str, NDArray[np.float64]]:
    """The simulated means each panel draws, keyed by the gid of the histogram drawing them."""
    return {
        "mean-zero": result.returns.mean_zero,
        "declared": result.returns.declared,
        "normal": result.returns.normal,
        "shuffled": result.trades,
    }


def axis_limits(result: HypothesisTests) -> tuple[float, float]:
    """One span for all three panels.

    It reaches the Gaussian null's ±4 spreads, every simulated mean and the
    observed mean, padded on both sides, so no draw falls outside a bin.
    """
    reach = NULL_REACH * gaussian_spread(result)
    values = np.concatenate([*panel_series(result).values(), [result.observed_mean]])
    low = min(-reach, float(values.min()))
    high = max(reach, float(values.max()))
    pad = PAD * (high - low)
    return low - pad, high + pad


def bin_edges(result: HypothesisTests) -> NDArray[np.float64]:
    """:data:`BINS` equal bins across :func:`axis_limits`."""
    return np.linspace(*axis_limits(result), BINS + 1)


def _ratio(x: float, _pos: object = None) -> str:
    """A tick in the post's e-notation with a true minus sign, and a bare zero."""
    if abs(x) < TICK / 1e6:
        return "0"
    return _sci(x, 0).replace("-", "−", 1) if x < 0 else _sci(x, 0)


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


def _draws(count: int, of: int) -> str:
    return f"{count:,} of {of:,} at or above"


@_plain_text
def make_tu_hypothesis_tests_figure(
    out: Path | None = None,
    result: HypothesisTests | None = None,
    sources: tuple[VintageEntry, pd.Series] | None = None,
) -> Figure:
    """The three tests' nulls, each beside the check that varies one input of it."""
    entry, closes = sources if sources is not None else read_sources()
    if result is None:
        result = hypothesis_tests(closes.to_numpy(dtype=float))
    series = panel_series(result)
    edges = bin_edges(result)
    observed = result.observed_mean
    spread = gaussian_spread(result)
    tail = float(ndtr(-result.statistic))

    fig = Figure(figsize=(10, 11), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    gaussian_ax, returns_ax, trades_ax = fig.subplots(3, 1, sharex=True)
    for ax in (gaussian_ax, returns_ax, trades_ax):
        _style(ax)
        ax.set_yticks([])
        ax.set_ylabel("share of draws, as a density", color=INK, fontsize=10)

    def histogram(ax, gid: str, label: str, color: str, filled: bool) -> None:
        values, _ = np.histogram(series[gid], bins=edges, density=True)
        if filled:
            ax.stairs(values, edges, fill=True, color=color, alpha=0.4, gid=gid, label=label)
        else:
            ax.stairs(values, edges, color=color, lw=1.6, gid=gid, label=label)

    def observed_line(ax) -> None:
        ax.axvline(observed, color=INK, lw=1.4, gid="observed", label="observed mean")

    x = np.linspace(edges[0], edges[-1], CURVE_POINTS)
    gaussian_ax.plot(
        x,
        norm.pdf(x, loc=0.0, scale=spread),
        color=ACCENT,
        lw=1.8,
        ls="--",
        gid="gaussian",
        label=f"Gaussian null of the mean, one-sided tail {tail:.6f}",
    )
    histogram(
        gaussian_ax,
        "mean-zero",
        f"type IV with the mean set to zero, added after a trial run: "
        f"{_draws(result.count(series['mean-zero']), len(series['mean-zero']))}",
        LOST,
        filled=False,
    )
    observed_line(gaussian_ax)
    _heading(
        gaussian_ax,
        f"The first test: the mean of {len(result.daily):,} normal days with a mean of zero "
        f"and the strategy's std,\nwhich spreads by {_sci(spread, 2)}. Removing TU's drift "
        "from the type IV draws gives nearly the same null.",
    )

    histogram(
        returns_ax,
        "declared",
        f"type IV with TU's four moments: "
        f"{_draws(result.count(series['declared']), len(series['declared']))}",
        ACCENT,
        filled=True,
    )
    histogram(
        returns_ax,
        "normal",
        f"normal with TU's mean and std, added after a trial run: "
        f"{_draws(result.count(series['normal']), len(series['normal']))}",
        GOOD,
        filled=False,
    )
    observed_line(returns_ax)
    _heading(
        returns_ax,
        "The second test: the rule rerun on simulated returns. Type IV and a normal draw "
        "share TU's mean\nand spread, and their means sit almost on top of each other, "
        "shifted right of the first panel's.",
    )

    histogram(
        trades_ax,
        "shuffled",
        f"shuffled entry days, corrected: "
        f"{_draws(result.count(series['shuffled']), len(series['shuffled']))}",
        ACCENT,
        filled=True,
    )
    observed_line(trades_ax)
    _heading(
        trades_ax,
        "The third test, corrected: the long and short entry days shuffled on TU's own "
        "returns.\nThe means sit in a narrow band, and none reaches the observed mean.",
    )

    for ax in (gaussian_ax, returns_ax, trades_ax):
        ax.set_ylim(0, HEADROOM * ax.get_ylim()[1])
        ax.legend(loc="upper left", frameon=False, fontsize=9, labelcolor=INK)
    trades_ax.set_xlim(edges[0], edges[-1])
    trades_ax.xaxis.set_major_locator(MultipleLocator(TICK))
    trades_ax.xaxis.set_major_formatter(FuncFormatter(_ratio))
    trades_ax.set_xlabel("mean daily strategy return", color=INK, fontsize=10)
    trades_ax.tick_params(axis="x", colors=MUTED)

    days = closes.index
    _title(
        fig,
        "Exploratory: three hypothesis tests on TU momentum, rerun on Chan's own file",
        f"Example 1.1 of Algorithmic Trading. TU from {entry.path}, saved {entry.obtained}, "
        f"{days[0].date()} to {days[-1].date()}.\nSeed {RETURNS_SEED} draws the simulated "
        f"returns and seed {TRADES_SEED} the shuffles.\nThe checks marked as added came after "
        f"a trial run on other seeds.\nThe {LOOKBACK}-day lookback and {HOLD_DAYS}-day hold were "
        f"picked from {len(PERIODS) ** 2} pairs on the same closes, and no p-value here is "
        "corrected for that.",
    )
    fig.tight_layout(rect=(0, 0.085, 1, 0.97))
    return _save(fig, out, TU_HYPOTHESIS_TESTS_FIGURE)


def main() -> None:
    try:
        make_tu_hypothesis_tests_figure()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day is worth nothing at
        # the bottom of a traceback, so it reaches the operator as one line, the
        # way chan.tu_hypothesis_tests.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / TU_HYPOTHESIS_TESTS_FIGURE}")


if __name__ == "__main__":
    main()
