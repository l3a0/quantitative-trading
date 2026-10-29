"""The whiteboard sketch for the capped low-beta post, in Lesson 5.

``blog/capped-low-beta-lessons.md`` makes a claim in Lesson 5 that a sentence
has to build in the reader's head: the larger lead, at a ceiling of 5, breaks
even at the smaller borrowing spread, because it borrows more for each unit of
capital. This module draws that as one scene, and the post places it right
after the paragraph that begins "The run searched for the spread at which the
gap's point estimate falls to zero".

1. Who breaks even first: grey axes with the yearly borrowing spread across
   and the gap a year up, and a grey line at a gap of 0. A black line falls
   from the gap of 0.0934 at a ceiling of 2 to 0 at a spread of 0.0946, and
   its label says it borrows 1 per unit of capital. A brass line starts higher,
   at 0.1659 at a ceiling of 5, falls about 2.5 times as steeply, and reaches 0
   first, at 0.0661, and its label says it borrows 2.5134. Dashed grey drops
   carry each break-even down to the spread axis. The brass line passes under
   the black one before either reaches 0, and that crossing is left unlabelled,
   since the post does not state it. The last label reads "steeper line:
   smaller spread erases it", echoing the levered low-beta post's "steeper
   line: smaller loss ruins".

The sketch is not schematic. Every figure it prints, and every position it
draws a line at, comes from :class:`BreakEvenFigures`, which
:meth:`BreakEvenFigures.from_run` reads through
:func:`chan.low_beta_leverage.read_sources` and
:func:`chan.low_beta_leverage.build_portfolios`, the run's own path. Each
gap is :attr:`chan.low_beta_capped.Capped.gap`, each break-even spread is
:func:`chan.low_beta_capped.break_even_spread` on
:func:`chan.low_beta_capped.cap`'s portfolios, and each line's borrowing is
the mean of that capped leverage less 1. Like every figure Entry 48 reports,
they are exploratory point estimates about survivors only, and a spread below
a break-even does not make a gap real, which the post's next paragraph says.

Each line is drawn straight between the run's two endpoints, its gap at no
spread and 0 at its break-even spread. The charged gap,
:func:`chan.low_beta_capped.charged_gap`, is not exactly straight in the
spread, because each month's log growth bends as the charge rises. Over the
span drawn it departs from the straight line by at most about 0.00034 a year,
at a ceiling of 5 near the middle of its span, which is under half a pixel on
this board. So the straight lines are faithful to the run, and the test
module checks that midpoint against the run's own ``charged_gap``.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so this GIF shares that post's look, frame rate and colours. This
post's chart still draws in :mod:`chan.regime_figure`'s shared inks, so the
sketch does too. It carries more than a reader takes in at that post's pace,
so it is in :data:`PACED`, and :func:`sketch_timeline` holds each of its
labels longer and its finished drawing for twelve seconds, as
:mod:`chan.levered_low_beta_whiteboard` does for both of its sketches. The GIF
is named :data:`GIF_PREFIX` plus the scene's slug. The post's chart,
``low_beta_capped.png``, does not start with that prefix, so nothing that
looks for the sketch by prefix finds the chart.

The sketch is deterministic for the reason :mod:`chan.usdcad_tests_whiteboard`
gives, so a redraw with no change is a no-op diff. Redraw it with::

    uv run python -m chan.capped_low_beta_whiteboard
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from chan import low_beta_capped as lbc
from chan import low_beta_leverage as llb
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, INK, MUTED
from chan.usdcad_tests_whiteboard import (
    Frame,
    Label,
    Scene,
    Stroke,
    _line,
    _stroke,
    render,
    timeline,
)

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "capped_low_beta_sketch_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``capped_low_beta_sketch_break_even.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


# --- The figures, read from the run ---------------------------------------------


@dataclass(frozen=True)
class CeilingLine:
    """One ceiling's line: its gap at no spread, its break-even spread, and what it borrows.

    ``gap`` is twelve times the mean of d at the bill rate, ``spread`` the
    yearly spread at which that gap reaches 0, and ``borrowed`` the mean
    leverage less 1, what the capped portfolio borrows for each unit of
    capital.
    """

    ceiling: float
    gap: float
    spread: float
    borrowed: float

    @property
    def slope(self) -> float:
        """How fast the gap falls as the spread rises, the gap over the break-even spread."""
        return self.gap / self.spread

    @classmethod
    def from_portfolios(cls, p: llb.Portfolios, ceiling: float) -> CeilingLine:
        capped = lbc.cap(p, ceiling)
        spread = lbc.break_even_spread(capped)
        if spread is None:
            raise ValueError(f"at a ceiling of {ceiling:g} the gap is 0 or below with no spread")
        return cls(
            ceiling=ceiling,
            gap=lbc.capped(p, ceiling).gap,
            spread=spread,
            borrowed=float(capped.leverage.mean()) - 1,
        )


@dataclass(frozen=True)
class BreakEvenFigures:
    """What the sketch draws: the line at each of the run's two ceilings, 2 then 5."""

    low: CeilingLine
    high: CeilingLine

    @classmethod
    def from_run(cls, data_dir: Path | None = None) -> BreakEvenFigures:
        """Read the committed vintages through the run's own path."""
        _, closes, _, spy, _, bills = llb.read_sources(data_dir)
        return cls.from_portfolios(llb.build_portfolios(closes, spy, bills))

    @classmethod
    def from_portfolios(cls, p: llb.Portfolios) -> BreakEvenFigures:
        low, high = (CeilingLine.from_portfolios(p, c) for c in lbc.CEILINGS)
        return cls(low=low, high=high)


def four(value: float) -> str:
    """``value`` to four decimals, as the post prints it."""
    return f"{value:.4f}"


def amount(value: float) -> str:
    """A whole number as a digit, such as ``1``, and anything else to four decimals."""
    return f"{value:.0f}" if value == round(value) else four(value)


# --- Lesson 5: who breaks even first ---------------------------------------------

#: The window the sketch draws: the yearly spread across and the yearly gap up,
#: and where each lands on the board. The spread axis runs along the bottom, a
#: little below a gap of 0, so the line at 0 sits clear of it.
SPREAD, SPREAD_X = (0.0, 0.11), (2.3, 9.5)
GAP, GAP_Y = (-0.035, 0.175), (0.75, 3.55)
TICK = 0.08
#: How far under the spread axis its labels sit.
UNDER = 0.38


def s_x(s: float | np.ndarray) -> float | np.ndarray:
    """The board across of a yearly spread."""
    (s0, s1), (x0, x1) = SPREAD, SPREAD_X
    return x0 + (np.asarray(s) - s0) * (x1 - x0) / (s1 - s0)


def g_y(g: float | np.ndarray) -> float | np.ndarray:
    """The board height of a yearly gap."""
    (g0, g1), (y0, y1) = GAP, GAP_Y
    return y0 + (np.asarray(g) - g0) * (y1 - y0) / (g1 - g0)


def _ceiling_stroke(gid: str, line: CeilingLine, color: str) -> Stroke:
    """The line from the gap at no spread down to 0 at the break-even spread."""
    points = [(float(s_x(0.0)), float(g_y(line.gap))), (float(s_x(line.spread)), float(g_y(0.0)))]
    return _stroke(gid, _line(points), color=color, frames=8)


def _drop(gid: str, line: CeilingLine) -> Stroke:
    x = float(s_x(line.spread))
    return _stroke(
        gid,
        _line([(x, float(g_y(0.0))), (x, GAP_Y[0])], per_unit=16),
        color=MUTED,
        dashed=True,
        width=1.5,
        frames=4,
    )


def _spread_axis(f: BreakEvenFigures) -> tuple:
    """The spread axis, with a tick down at each break-even spread."""
    y = GAP_Y[0]
    points = [(SPREAD_X[0], y)]
    for s in sorted((f.low.spread, f.high.spread)):
        x = float(s_x(s))
        points += [(x, y), (x, y - TICK), (x, y)]
    points.append((SPREAD_X[1], y))
    return _line(points)


def _break_even(f: BreakEvenFigures) -> Scene:
    """Lesson 5: the steeper line reaches a gap of 0 first, so a smaller spread erases it."""
    left = SPREAD_X[0]
    zero_y = float(g_y(0.0))
    low_y, high_y = float(g_y(f.low.gap)), float(g_y(f.high.gap))
    low_x, high_x = float(s_x(f.low.spread)), float(s_x(f.high.spread))
    steps: list[Stroke | Label] = [
        _stroke("gap-axis", _line([(left, GAP_Y[0]), (left, GAP_Y[1])]), color=MUTED, frames=6),
        Label("gap a year", left + 0.2, 3.82, names="gap-axis", color=MUTED, size=11),
        _stroke("spread-axis", _spread_axis(f), color=MUTED, frames=8),
        Label(
            "yearly borrowing spread",
            left,
            GAP_Y[0] - UNDER,
            names="spread-axis",
            color=MUTED,
            size=11,
        ),
        _stroke("zero", _line([(left, zero_y), (SPREAD_X[1], zero_y)]), color=MUTED, frames=6),
        Label("0", left - 0.2, zero_y, names="zero", color=MUTED, size=10, ha="right"),
        _ceiling_stroke("low", f.low, INK),
        Label(
            f"ceiling {f.low.ceiling:g}: {four(f.low.gap)}",
            left - 0.2,
            low_y,
            names="low",
            size=11,
            ha="right",
        ),
        Label(
            f"borrows {amount(f.low.borrowed)} per unit of capital",
            6.3,
            2.05,
            names="low",
            size=11,
        ),
        _drop("low-drop", f.low),
        Label(four(f.low.spread), low_x, GAP_Y[0] - UNDER, names="low-drop", size=10, ha="center"),
        _ceiling_stroke("high", f.high, ACCENT),
        Label(
            f"ceiling {f.high.ceiling:g}: {four(f.high.gap)}",
            left - 0.2,
            high_y,
            names="high",
            color=ACCENT,
            size=11,
            ha="right",
        ),
        Label(
            f"borrows {amount(f.high.borrowed)}",
            3.75,
            3.1,
            names="high",
            color=ACCENT,
            size=11,
        ),
        _drop("high-drop", f.high),
        Label(
            four(f.high.spread),
            high_x,
            GAP_Y[0] - UNDER,
            names="high-drop",
            color=ACCENT,
            size=10,
            ha="center",
        ),
        Label(
            "steeper line: smaller spread erases it",
            SPREAD_X[1],
            2.75,
            names="high",
            color=ACCENT,
            size=11,
            ha="right",
        ),
    ]
    return Scene("Who breaks even first", "break_even", tuple(steps))


# --- Drawing ------------------------------------------------------------------

#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("break_even",)
PACED_LABEL_MS, PACED_HOLD_MS = 900, 12000


def sketch_timeline(scene: Scene) -> list[Frame]:
    """:func:`timeline`'s frames, slowed for the scenes in :data:`PACED`."""
    frames = timeline(scene)
    if scene.slug not in PACED:
        return frames
    paced = [
        Frame(f.done, f.partial, PACED_LABEL_MS)
        if f.partial == 0 and f.done and not isinstance(scene.steps[f.done - 1], Stroke)
        else f
        for f in frames
    ]
    last = paced[-1]
    paced[-1] = Frame(last.done, last.partial, PACED_HOLD_MS)
    return paced


def scenes(figures: BreakEvenFigures | None = None) -> tuple[Scene, ...]:
    """The one scene, as a tuple so the post's sketches read like every other post's.

    ``figures`` defaults to :meth:`BreakEvenFigures.from_run` on the committed vintages.
    """
    found = figures if figures is not None else BreakEvenFigures.from_run()
    return (_break_even(found),)


def _write(scene: Scene, folder: Path) -> Path:
    frames = sketch_timeline(scene)
    first, *rest = render(scene, frames)
    path = folder / gif_name(scene)
    first.save(
        path,
        save_all=True,
        append_images=rest,
        duration=[frame.ms for frame in frames],
        loop=0,
        optimize=False,
    )
    return path


def make_capped_low_beta_whiteboards(out_dir: Path | None = None) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes()]


def main() -> None:
    for path in make_capped_low_beta_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
