"""The factor models post's one figure, drawn from the committed S&P 500 file.

``blog/factor-models-lessons.md`` teaches in its Lesson 4 that a verdict can
follow the declared criterion and still rest on almost nothing. Entry 14's two
autocorrelations are where that lesson reaches the data, and the owner chose on
2026-10-03 to give the post this one figure, the one
[issue 282](https://github.com/l3a0/quantitative-trading/issues/282) plans.

:func:`make_autocorrelation_figure` draws the 446 stocks' lag-1
autocorrelations from :func:`chan.momentum_factor.autocorrelations` as their
cumulative curve, with MKT, WML, the median stock, zero and the band on it.

1. **A cumulative curve rather than a histogram.** The x-axis is the
   autocorrelation and the y-axis the share of the 446 stocks at or below it,
   drawn as a step. A histogram's bars depend on a bin width nothing pins,
   while every step here is one stock's pinned value.
2. **A vertical line for each factor.** Where it meets the curve is the
   factor's percentile among the stocks, so the picture carries Lesson 3's
   two percentiles as well as Lesson 4's band. No stock's autocorrelation
   equals either factor's, so the share at or below and the share strictly
   below, which :meth:`chan.momentum_factor.Comparison.percentile` counts,
   agree.
3. **The band shaded**, ±1.96/√83, where a series with no autocorrelation
   lands about 95 percent of the time. Both factors sit inside it.

Nothing is drawn in the verdict colours, because Lesson 4 says neither verdict
is distinguishable from noise. The title says the test is exploratory, and the
note says ``spx_20071123/`` holds only survivors while SPY does not.

Every value comes from one :class:`chan.momentum_factor.Comparison`, so the
figure can only be wrong by drawing the wrong thing, which
``tests/test_momentum_factor_figures.py`` checks. It reads the committed
vintages, so it redraws anywhere the data is::

    uv run python -m chan.momentum_factor_figures
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from matplotlib.figure import Figure

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.momentum_factor import (
    Comparison,
    EmptyLeg,
    autocorrelations,
    build_factors,
    read_sources,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, INK, MUTED, RULE, SURFACE
from chan.vintage import VintageUnavailable

AUTOCORRELATION_FIGURE = "factor_momentum_autocorrelations.png"


def _signed(x: float) -> str:
    """A figure at the four decimals the log quotes, with a typographic minus."""
    return format(x, ".4f").replace("-", "−")


def factor_label(name: str, value: float, comparison: Comparison) -> str:
    """One factor's autocorrelation and percentile among the stocks, as the figure prints them."""
    return f"{name} {_signed(value)}\n{comparison.percentile(value):.4f}th percentile"


@_plain_text
def make_autocorrelation_figure(comparison: Comparison, out: Path | None = None) -> Figure:
    """The stocks' cumulative curve, with both factors, the median, zero and the band."""
    stocks = np.sort(comparison.stocks.to_numpy())
    count = len(stocks)
    heights = np.arange(1, count + 1) / count
    band = comparison.band

    fig = Figure(figsize=(10, 6.2), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.subplots()
    _style(ax)

    ax.axvspan(-band, band, color=RULE, alpha=0.45, lw=0, zorder=0, gid="band")
    ax.axvline(0, color=MUTED, lw=0.9, zorder=1, gid="zero")
    ax.axvline(comparison.median, color=MUTED, lw=1.1, ls=":", zorder=2, gid="median")
    ax.step(stocks, heights, where="post", color=INK, lw=1.6, zorder=3, gid="stocks")

    # The curve climbs to the right, so the space below and right of MKT's
    # point is empty, and so is the space above and left of WML's.
    for name, value, colour, style, ha, va, offset in (
        ("MKT", comparison.mkt, ACCENT, "-", "left", "top", (8, -14)),
        ("WML", comparison.wml, INK, "--", "right", "bottom", (-8, 14)),
    ):
        tag = name.lower()
        meets = comparison.percentile(value) / 100
        ax.axvline(value, color=colour, lw=1.6, ls=style, zorder=4, gid=tag)
        ax.plot([value], [meets], "o", color=colour, ms=6, zorder=5, gid=f"{tag}-meets")
        ax.annotate(
            factor_label(name, value, comparison),
            (value, meets),
            xytext=offset,
            textcoords="offset points",
            ha=ha,
            va=va,
            color=INK,
            fontsize=9.5,
            linespacing=1.35,
            gid=f"label-{tag}",
        )

    # Upright, beside its own line, because the gap between the median and
    # WML is too narrow for the label to lie flat without crossing WML's line.
    ax.annotate(
        f"median stock {_signed(comparison.median)}",
        (comparison.median, 0.03),
        xytext=(3, 0),
        textcoords="offset points",
        ha="left",
        va="bottom",
        rotation=90,
        color=MUTED,
        fontsize=9,
        gid="label-median",
    )
    ax.annotate(
        f"±{band:.4f}, where a series with no\nautocorrelation lands 95 percent of the time",
        (band, 0.03),
        xytext=(-6, 0),
        textcoords="offset points",
        ha="right",
        va="bottom",
        color=MUTED,
        fontsize=9,
        linespacing=1.35,
        gid="label-band",
    )

    ax.set_ylim(0, 1.02)
    ax.set_ylabel(f"share of the {count} stocks at or below", color=INK, fontsize=10)
    ax.set_xlabel(
        f"lag-1 autocorrelation of {comparison.months} monthly returns", color=INK, fontsize=10
    )
    ax.grid(axis="x", color=RULE, lw=0.6, alpha=0.7)

    _title(
        fig,
        "Factor momentum on Chan's S&P 500 file, an exploratory test",
        f"The {count} stocks are every stock in spx_20071123/ priced in all {comparison.months} "
        "holding months. That file holds only the companies\n"
        "in the S&P 500 the day Chan saved it, so WML and every stock here are survivors. "
        "MKT reads SPY, which held the index\n"
        "as it stood each day, so it is not. A factor's line meets the curve at its "
        "percentile among the stocks.",
    )
    fig.tight_layout(rect=(0, 0.12, 1, 0.95))
    return _save(fig, out, AUTOCORRELATION_FIGURE)


def main() -> None:
    try:
        _, closes, _, spy, _, bills = read_sources()
        comparison = autocorrelations(build_factors(closes, spy, bills))
    except (VintageUnavailable, EmptyLeg) as refused:
        # The refusals `chan.momentum_factor.main` prints, for the same reason:
        # a sentence naming the source or the month is worth nothing at the
        # bottom of a traceback.
        raise SystemExit(str(refused)) from refused
    make_autocorrelation_figure(comparison)
    print(f"wrote {FIGURES_DIR / AUTOCORRELATION_FIGURE}")


if __name__ == "__main__":
    main()
