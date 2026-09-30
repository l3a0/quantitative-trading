"""A figure for the Kelly post, drawn from the committed SPY vintage.

``blog/kelly-leverage-on-spy.md`` derives the Kelly leverage from one growth
formula, ``g(f) = r + f*m - f**2 * s**2 / 2``, and the owner asked on
2026-09-30 for a picture of it. :func:`make_growth_figure` draws that curve on
Chan's window and marks four leverages.

1. Unlevered SPY, at a leverage of 1.
2. Half-Kelly, which keeps three-quarters of the growth above the risk-free
   rate.
3. Full Kelly, where the curve peaks.
4. Twice Kelly, where growth falls back to the risk-free rate.

The moments come from :func:`chan.kelly_leverage.annualised_moments`, so the
figure can only be wrong by drawing the wrong thing, which
``tests/test_kelly_figures.py`` checks. It reads the committed vintage, so it
redraws anywhere the data is::

    uv run python -m chan.kelly_figures
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.kelly_leverage import (
    BOOK_END,
    BOOK_START,
    VINTAGE_DATE,
    Moments,
    annualised_moments,
    simple_returns,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED, SURFACE
from chan.series import load_vintage

GROWTH_FIGURE = "kelly_growth_by_leverage.png"

#: The widest leverage the curve draws. Twice Kelly on Chan's window is 5.10,
#: so this leaves room past the last mark for its label.
MAX_LEVERAGE = 5.6


@dataclass(frozen=True)
class GrowthCurve:
    leverages: np.ndarray
    growth: np.ndarray


def chan_window_moments(data_dir: Path | None = None) -> Moments:
    """The moments of the committed SPY vintage over Chan's own window."""
    _, close = load_vintage("SPY", dated=VINTAGE_DATE, data_dir=data_dir)
    window = close[
        (close.index >= pd.Timestamp(BOOK_START)) & (close.index <= pd.Timestamp(BOOK_END))
    ]
    return annualised_moments(simple_returns(window))


def growth(moments: Moments, leverage: float | np.ndarray) -> float | np.ndarray:
    """``g(f) = r + f*m - f**2 * s**2 / 2``, the post's one growth formula."""
    m, s2 = moments.excess_annual, moments.sd_annual**2
    return moments.risk_free + leverage * m - leverage**2 * s2 / 2.0


def growth_curve(moments: Moments, points: int = 561) -> GrowthCurve:
    """Growth at each leverage from 0 to :data:`MAX_LEVERAGE`."""
    leverages = np.linspace(0.0, MAX_LEVERAGE, points)
    return GrowthCurve(leverages=leverages, growth=growth(moments, leverages))


@_plain_text
def make_growth_figure(out: Path | None = None, moments: Moments | None = None) -> Figure:
    """Growth against leverage on Chan's window, with four leverages marked."""
    moments = moments if moments is not None else chan_window_moments()
    curve = growth_curve(moments)
    kelly = moments.leverage
    r = moments.risk_free

    fig = Figure(figsize=(10, 5.6), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.subplots()
    _style(ax)

    ax.axhline(r, color=MUTED, lw=1, ls=(0, (5, 3)))
    ax.plot(curve.leverages, curve.growth, color=INK, lw=2)

    marks = [
        (1.0, MUTED, f"unlevered SPY, 1\n{growth(moments, 1.0):.2%} a year", (12, -34)),
        (
            kelly / 2,
            ACCENT,
            f"half-Kelly, {kelly / 2:.2f}\n{growth(moments, kelly / 2):.2%} a year",
            (-40, 22),
        ),
        (kelly, GOOD, f"Kelly, {kelly:.3f}\n{growth(moments, kelly):.2%} a year", (-40, 18)),
        (
            2 * kelly,
            LOST,
            f"twice Kelly, {2 * kelly:.2f}\n{growth(moments, 2 * kelly):.0%}, the cash rate",
            (-150, 22),
        ),
    ]
    for x, colour, label, offset in marks:
        y = growth(moments, x)
        ax.plot([x], [y], "o", ms=8, color=colour, mec=SURFACE, mew=2, zorder=3)
        ax.annotate(
            label,
            (x, y),
            xytext=offset,
            textcoords="offset points",
            color=INK,
            fontsize=10,
            arrowprops={"arrowstyle": "-", "color": MUTED, "lw": 0.8},
        )

    ax.set_xlim(0, MAX_LEVERAGE)
    ax.set_ylim(-0.005, 0.16)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.set_xlabel("leverage, the position divided by equity", color=INK, fontsize=10.5)
    ax.set_ylabel("compound growth per year", color=INK, fontsize=10.5)
    _title(
        fig,
        "Growth on SPY peaks at the Kelly leverage and falls back to cash at twice it",
        f"SPY, {BOOK_START} to {BOOK_END}, 2026 download. g(f) = r + f·m − f²s²/2, "
        f"with m = {moments.excess_annual:.5f}, s = {moments.sd_annual:.4f} and r = {r:.2f}.\n"
        "The dashed line is the risk-free rate. Half-Kelly keeps three-quarters of "
        "the growth above it at half the leverage.",
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.96))
    fig.curve = curve
    return _save(fig, out, GROWTH_FIGURE)


def main() -> None:
    make_growth_figure()
    print(f"wrote {FIGURES_DIR / GROWTH_FIGURE}")


if __name__ == "__main__":
    main()
