"""The figure for the post on capped Kelly allocation, Example 8.2.

``blog/capped-kelly-allocation-lessons.md`` teaches what Entry 20 of the
replication log found. :func:`make_allocation_figure` redraws the book's
Figure 8.1, "Constrained Growth Rate g as Function of F2" at location 3287:
the growth rate along the line ``F1 = 2 - F2``, where the whole cap of 2 on
gross leverage is spent, against the leverage on strategy 2.

1. The solid curve runs from F2 = 0 to the cap, the range the book plots. It
   rises the whole way, from everything on strategy 1 to everything on
   strategy 2.
2. The dashed curve continues the same line past the cap to F2 = 2.6, over a
   shaded region labelled as over the gross cap. Past F2 = 2 the line holds a
   short in strategy 1, so its gross leverage exceeds 2. The book does not
   draw this part. It is here so the unbounded peak the post's fourth lesson
   is about can be seen, and seen to be out of bounds.
3. Three markers: the proportional split the book refutes, the corner with
   everything on strategy 2, and a hollow marker at the unbounded peak.

Every value comes from :mod:`chan.kelly_allocation`'s own functions, the ones
``python -m chan.kelly_allocation`` prints from, so the figure can only be
wrong by drawing the wrong thing, which
``tests/test_kelly_allocation_figures.py`` checks. The example reads no
vintage, so there is no refusal to turn into one line, and the command draws
and saves::

    uv run python -m chan.kelly_allocation_figures
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from matplotlib.figure import Figure

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.kelly_allocation import (
    CORRELATION,
    MAX_LEVERAGE,
    MEANS,
    VOLS,
    best_allocation_at_cap,
    covariance,
    growth_rate,
    kelly_leverages,
    proportional_cap,
    segment_stationary_point,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED, SURFACE

ALLOCATION_FIGURE = "kelly_allocation.png"

#: How far past the cap the dashed curve runs. The unbounded peak is at
#: F2 = 2.289321, so this leaves room on its far side for the curve to turn
#: over visibly.
BEYOND_CAP = 2.6

#: Points on the solid curve, one every 0.001 of F2.
CURVE_POINTS = 2001

#: Points on the dashed curve, one every 0.001 of F2.
BEYOND_POINTS = 601


@dataclass(frozen=True)
class Line:
    """The growth rate at each F2 along ``F1 = cap - F2``."""

    f2: np.ndarray
    growth: np.ndarray


@dataclass(frozen=True)
class Point:
    """One allocation on the line, by its leverage on strategy 2."""

    f2: float
    growth: float


@dataclass(frozen=True)
class AllocationCurve:
    """Everything the figure draws, computed once from the book's inputs."""

    inside: Line
    beyond: Line
    proportional: Point
    corner: Point
    peak: Point


def _line(f2: np.ndarray, cov: np.ndarray) -> Line:
    growth = np.array([growth_rate((MAX_LEVERAGE - x, x), MEANS, cov) for x in f2])
    return Line(f2=f2, growth=growth)


def allocation_curve() -> AllocationCurve:
    """The line inside the cap and past it, with its three marked allocations."""
    cov = covariance(VOLS, CORRELATION)
    kelly = kelly_leverages(MEANS, cov)
    capped = proportional_cap(kelly, MAX_LEVERAGE)
    best = best_allocation_at_cap(MEANS, cov, MAX_LEVERAGE)
    raw = segment_stationary_point(MEANS, cov, MAX_LEVERAGE)
    return AllocationCurve(
        inside=_line(np.linspace(0.0, MAX_LEVERAGE, CURVE_POINTS), cov),
        beyond=_line(np.linspace(MAX_LEVERAGE, BEYOND_CAP, BEYOND_POINTS), cov),
        proportional=Point(float(capped[1]), growth_rate(capped, MEANS, cov)),
        corner=Point(best.leverages[1], best.growth),
        peak=Point(raw, growth_rate((MAX_LEVERAGE - raw, raw), MEANS, cov)),
    )


@_plain_text
def make_allocation_figure(out: Path | None = None) -> Figure:
    """The growth rate along ``F1 = 2 - F2``, inside the cap and past it."""
    curve = allocation_curve()

    fig = Figure(figsize=(10, 5.8), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.subplots()
    _style(ax)

    ax.axvspan(MAX_LEVERAGE, BEYOND_CAP, color=LOST, alpha=0.08, lw=0, gid="over_cap")
    ax.text(
        (MAX_LEVERAGE + BEYOND_CAP) / 2,
        0.50,
        f"over the gross cap of {MAX_LEVERAGE:g}:\nstrategy 1 is held short",
        ha="center",
        va="bottom",
        color=LOST,
        fontsize=9.5,
        gid="over_cap_label",
    )
    ax.plot(curve.inside.f2, curve.inside.growth, color=INK, lw=2, gid="inside")
    ax.plot(curve.beyond.f2, curve.beyond.growth, color=INK, lw=1.6, ls="--", gid="beyond")

    marks = [
        (
            "proportional",
            curve.proportional,
            ACCENT,
            ACCENT,
            f"proportional split, F2 = {curve.proportional.f2:.6f}\n"
            f"g = {curve.proportional.growth:.6f}",
            (-120, -105),
            "left",
        ),
        (
            "corner",
            curve.corner,
            GOOD,
            GOOD,
            f"everything on strategy 2, F2 = {curve.corner.f2:g}\ng = {curve.corner.growth:.3f}",
            (-20, -95),
            "right",
        ),
        (
            "peak",
            curve.peak,
            LOST,
            "none",
            f"unbounded peak, F2 = {curve.peak.f2:.6f}\ng = {curve.peak.growth:.6f}, not allowed",
            (-150, 30),
            "left",
        ),
    ]
    for gid, point, edge, face, label, offset, align in marks:
        ax.plot(
            [point.f2],
            [point.growth],
            "o",
            ms=8,
            mec=edge,
            mfc=face,
            mew=2,
            zorder=3,
            gid=gid,
        )
        ax.annotate(
            label,
            (point.f2, point.growth),
            xytext=offset,
            textcoords="offset points",
            ha=align,
            color=INK,
            fontsize=9.5,
            arrowprops={"arrowstyle": "-", "color": MUTED, "lw": 0.8},
        )

    ax.set_xlim(0.0, BEYOND_CAP)
    ax.set_ylim(0.45, 1.02)
    ax.set_xlabel(
        f"F2, the leverage on strategy 2, with F1 = {MAX_LEVERAGE:g} − F2 on strategy 1",
        color=INK,
        fontsize=10.5,
    )
    ax.set_ylabel("growth rate g", color=INK, fontsize=10.5)
    _title(
        fig,
        "Under a cap of 2, the growth rate rises all the way to everything on strategy 2",
        "Algorithmic Trading, Example 8.2, location 3287. Means 0.30 and 0.60, volatilities "
        "0.26 and 0.35, no correlation, risk-free rate 0.\n"
        "g = F′M − F′CF / 2 along F1 + F2 = 2. The solid curve redraws the book's Figure 8.1. "
        "The dashed part past the cap is added.",
    )
    fig.tight_layout(rect=(0, 0.08, 1, 0.96))
    return _save(fig, out, ALLOCATION_FIGURE)


def main() -> None:
    make_allocation_figure()
    print(f"wrote {FIGURES_DIR / ALLOCATION_FIGURE}")


if __name__ == "__main__":
    main()
