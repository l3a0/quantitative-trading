"""Whiteboard sketches for the low-beta holdout post, one for Lesson 1 and one for Lesson 5.

``blog/low-beta-holdout-lessons.md`` makes two claims that a sentence has to
build in the reader's head. Y and the one-sided upper bound are both built from
the same standard error, yet they answer different questions, because they are
measured from different starting points. And the earlier test's holding-month
rule looked ahead on a panel whose series can stop inside a month. This module
draws the two as scenes, and the post places each right after the paragraph it
draws.

1. Y and the upper bound: one axis of the yearly gap, levered low fifth minus
   unlevered high fifth. A red dot sits at the measured gap of −0.0590. A black
   bracket above the axis runs 1.645 standard errors of 0.1185 from that dot to
   the upper bound of 0.1360, and red hatching right of the bound marks the
   advantages the data reject. A brass bracket below the axis runs from 0 to Y,
   0.2948, which is 1.645 plus 0.8416 of the same standard errors. A short brass
   tick on it marks where its first 1.645 standard errors end, the same length
   as the black bracket. That point, 1.645 × 0.1185 or 0.1950, carries no label,
   because the post does not state it. It sits in Lesson 1, after the paragraph
   that ends "from a deficit of the same size."
2. What the formation cannot know: a time axis with a formation and the next
   month-end. Stock A trades past both. Stock B's series stops between them.
   A red arrow runs from the next month-end back to the formation, because the
   old rule, which asked every stock for a close at the next month-end, drops B
   only by reading that later date. A green line then carries B flat from its
   last close to the month-end, the new rule, which earns B's return to its last
   close and holds cash after it. It sits in Lesson 5, after the paragraph that
   opens "The holding month changed most." It draws no closing label saying the
   formation now sees only its own date, because the paragraph after it names
   two exclusions that still read the next month-end.

The first sketch is drawn to scale, and the second is schematic. Every figure
the first prints, and every position it draws a dot, a bracket, a tick or the
hatching at, comes from :class:`BoundFigures`, which
:meth:`BoundFigures.from_verdict` reads from the registered run's
:class:`chan.low_beta_leverage.Verdict`. Those figures need the owner's archive,
so ``tests/test_low_beta_holdout_whiteboard.py`` pins them as a frozen copy and
``tests/test_low_beta_holdout.py`` holds that the run gives that copy. The
second sketch carries no figures: its paths, its dates and where B stops are
shapes, not data.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look, frame rate and colours. This
post's chart draws in :mod:`chan.regime_figure`'s shared inks, so the sketches
do too. Both are in :data:`PACED`, and :func:`sketch_timeline` holds each of
their labels longer and their finished drawings for twelve seconds, as
:mod:`chan.equity_seasonals_whiteboard` does for its slow sketches. Each GIF is
named :data:`GIF_PREFIX` plus the scene's slug. The post's chart,
``low_beta_holdout.png``, does not start with that prefix, so nothing that
looks for the sketches by prefix finds the chart.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. The schematic is written first, so a redraw
without the archive leaves only the first sketch stale and says so. Redraw both
with::

    QT_ARCHIVE_DIR=/path/to/archive uv run python -m chan.low_beta_holdout_whiteboard
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from chan import low_beta_holdout
from chan.archive import ArchiveRefused, ArchiveUnavailable
from chan.equity_seasonals import MonthlyRunRefused
from chan.fund_panel import PanelRefused
from chan.low_beta_leverage import (
    CRITICAL,
    MONTHS,
    POWER,
    EmptyPortfolio,
    NonPositiveBeta,
    UnreadableStandardError,
    Verdict,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    Frame,
    Label,
    Scene,
    Stroke,
    _arrow,
    _dot,
    _hatched,
    _line,
    _stroke,
    render,
    timeline,
)
from chan.vintage import VintageUnavailable

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "low_beta_holdout_sketch_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``low_beta_holdout_sketch_bound_and_y.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


def four(value: float) -> str:
    """``value`` to four decimals with a typographic minus, as the post prints it."""
    return f"{value:.4f}".replace("-", "−")


# --- The figures, read from the run ----------------------------------------------


@dataclass(frozen=True)
class BoundFigures:
    """What the first sketch draws, all of it a year: the gap, its standard error and Y.

    ``gap`` is twelve times the mean of d, the levered low fifth's monthly log
    growth minus the unlevered high fifth's. ``error`` is twelve times the
    Newey-West standard error of that mean. ``detectable`` is Y, the run's own
    (1.645 + 0.8416) × ``error``. The bound is not stored, since it follows from
    the gap and the error the way the post's paragraph says.
    """

    gap: float
    error: float
    detectable: float

    @property
    def bound(self) -> float:
        """The one-sided 95 percent upper bound, the gap plus 1.645 standard errors."""
        return self.gap + CRITICAL * self.error

    @property
    def reach(self) -> float:
        """1.645 standard errors, the length of both brackets' first piece."""
        return CRITICAL * self.error

    @classmethod
    def from_verdict(cls, verdict: Verdict) -> BoundFigures:
        return cls(
            gap=verdict.gap,
            error=verdict.standard_error * MONTHS,
            detectable=verdict.detectable,
        )

    @classmethod
    def from_run(cls) -> BoundFigures:
        """Read the owner's archive through the run's own path, about a minute."""
        return cls.from_verdict(low_beta_holdout.read_holdout().verdict)


# --- Lesson 1: Y and the upper bound -----------------------------------------------

#: The gap a year the axis spans, and where it lands on the board.
GAPS, GAP_X = (-0.14, 0.31), (0.5, 9.5)
#: The axis's height, how far above it the black bracket runs and how far below
#: it the brass one runs, and the half height of the tick at the brass join.
AXIS_Y, ABOVE_Y, BELOW_Y = 2.3, 3.15, 1.25
JOIN_TICK = 0.13
#: The red hatching's bottom and top, above the axis and right of the bound.
HATCH = (2.42, 3.2)


def gap_x(value: float | np.ndarray) -> float | np.ndarray:
    """The board across of a gap a year."""
    (v0, v1), (x0, x1) = GAPS, GAP_X
    return x0 + (np.asarray(value) - v0) * (x1 - x0) / (v1 - v0)


def _at(value: float) -> float:
    return float(gap_x(value))


def _bracket(start: float, end: float, level: float) -> tuple:
    """A bracket whose legs stand on the axis at ``start`` and ``end``, its bar at ``level``."""
    return _line([(start, AXIS_Y), (start, level), (end, level), (end, AXIS_Y)], per_unit=4)


def _bound_and_y(f: BoundFigures) -> Scene:
    """Lesson 1: one standard error, measured from the gap to the bound and from 0 to Y."""
    marks = {"gap": f.gap, "bound": f.bound, "Y": f.detectable}
    outside = {name: value for name, value in marks.items() if not GAPS[0] < value < GAPS[1]}
    if outside or not f.gap < 0 < f.bound < f.detectable:
        raise ValueError(
            f"the sketch draws a negative gap, then 0, the bound and Y in that order inside "
            f"{GAPS}, and these figures give gap {f.gap}, bound {f.bound}, Y {f.detectable}"
        )
    zero, gap, bound = _at(0.0), _at(f.gap), _at(f.bound)
    join, y_end = _at(f.reach), _at(f.detectable)
    under = (AXIS_Y + BELOW_Y) / 2
    steps: list[Stroke | Label] = [
        _stroke(
            "axis",
            _line(
                [
                    (GAP_X[0], AXIS_Y),
                    (zero, AXIS_Y),
                    (zero, AXIS_Y - 0.1),
                    (zero, AXIS_Y),
                    (GAP_X[1], AXIS_Y),
                ]
            ),
            color=MUTED,
            frames=8,
        ),
        Label("gap a year", GAP_X[0], AXIS_Y + 0.32, names="axis", color=MUTED, size=11),
        Label("0", zero - 0.18, AXIS_Y - 0.3, names="axis", color=MUTED, size=11, ha="right"),
        _dot("gap", gap, AXIS_Y, color=LOST),
        # Two lines, because one would run off the board's left edge in the
        # wider fallback font.
        Label(
            "measured gap", gap - 0.15, AXIS_Y - 0.32, names="gap", color=LOST, size=11, ha="right"
        ),
        Label(four(f.gap), gap - 0.15, AXIS_Y - 0.65, names="gap", color=LOST, size=11, ha="right"),
        _stroke("bound", _bracket(gap, bound, ABOVE_Y), color=INK, frames=8),
        Label(
            f"{CRITICAL} × {four(f.error)}",
            (gap + bound) / 2,
            (AXIS_Y + ABOVE_Y) / 2,
            names="bound",
            color=MUTED,
            size=11,
            ha="center",
        ),
        Label(
            f"upper bound {four(f.bound)}",
            bound - 0.1,
            ABOVE_Y + 0.38,
            names="bound",
            size=11,
            ha="right",
        ),
        _stroke(
            "reject",
            _hatched(bound, HATCH[0], GAP_X[1], HATCH[1]),
            color=LOST,
            width=1.4,
            frames=10,
        ),
        Label(
            "advantages the data reject",
            (bound + GAP_X[1]) / 2,
            ABOVE_Y + 0.38,
            names="reject",
            color=LOST,
            size=11,
            ha="center",
        ),
        _stroke("y", _bracket(zero, y_end, BELOW_Y), color=ACCENT, frames=8),
        _stroke(
            "join",
            _line([(join, BELOW_Y - JOIN_TICK), (join, BELOW_Y + JOIN_TICK)], per_unit=10),
            color=ACCENT,
            frames=2,
        ),
        Label(
            "the gap found four times in five",
            zero + 0.2,
            under,
            names="y",
            color=ACCENT,
            size=11,
        ),
        Label(
            f"Y {four(f.detectable)}",
            y_end - 0.2,
            under,
            names="y",
            color=ACCENT,
            size=11,
            ha="right",
        ),
        # The two pieces are labelled under the bar rather than inside it,
        # since the second is too narrow to hold its label between the legs.
        Label(
            f"the same {CRITICAL} × {four(f.error)}",
            (zero + join) / 2,
            BELOW_Y - 0.42,
            names="join",
            color=MUTED,
            size=11,
            ha="center",
        ),
        Label(
            f"{POWER} × {four(f.error)}",
            (join + y_end) / 2,
            BELOW_Y - 0.42,
            names="join",
            color=MUTED,
            size=11,
            ha="center",
        ),
        Label(
            "same standard error, different starting points",
            GAP_X[0],
            0.38,
            names="y",
            size=11,
        ),
    ]
    return Scene("Y and the upper bound", "bound_and_y", tuple(steps))


# --- Lesson 5: what the formation cannot know --------------------------------------

#: Where the two dates sit across the board, and where the time axis runs.
FORMED_X, NEXT_X = 2.2, 8.2
TIME_Y, TIME_TOP = 0.62, 3.75
#: Where each stock's path starts and runs, where B's series stops, and the
#: height the old rule's arrow runs at.
PATH_START, A_Y, B_Y, B_STOPS = 0.95, 3.2, 2.25, 5.2
PATH_END = 9.4
OLD_Y = 1.32


def _wiggle(x: np.ndarray, phase: float) -> np.ndarray:
    """A schematic price path around zero, a few sines and no data."""
    return 0.12 * np.sin(2.1 * x + phase) + 0.06 * np.sin(5.3 * x + 2 * phase)


def _look_ahead() -> Scene:
    """Lesson 5: the old rule drops B by reading the next month-end, and the new one holds it."""
    a_x = np.linspace(PATH_START, PATH_END, 60)
    b_x = np.linspace(PATH_START, B_STOPS, 32)
    b_y = B_Y + _wiggle(b_x, 1.3)
    last = float(b_y[-1])
    steps: list[Stroke | Label] = [
        _stroke(
            "time",
            _line([(0.5, TIME_Y), (9.5, TIME_Y)]),
            color=MUTED,
            frames=8,
        ),
        _stroke(
            "formed",
            _line([(FORMED_X, TIME_Y), (FORMED_X, TIME_TOP)]),
            color=MUTED,
            dashed=True,
            width=1.5,
            frames=4,
        ),
        Label(
            "formation", FORMED_X, TIME_Y - 0.34, names="formed", color=MUTED, size=11, ha="center"
        ),
        _stroke(
            "next",
            _line([(NEXT_X, TIME_Y), (NEXT_X, TIME_TOP)]),
            color=MUTED,
            dashed=True,
            width=1.5,
            frames=4,
        ),
        Label(
            "next month-end", NEXT_X, TIME_Y - 0.34, names="next", color=MUTED, size=11, ha="center"
        ),
        _stroke("a", (a_x, A_Y + _wiggle(a_x, 0.0)), color=INK, frames=10),
        Label("stock A", 4.6, A_Y + 0.5, names="a", size=11, ha="center"),
        _stroke("b", (b_x, b_y), color=INK, frames=8),
        _dot("b-last", B_STOPS, last, color=INK),
        Label("stock B’s series stops", B_STOPS + 0.2, last + 0.42, names="b-last", size=11),
        _stroke("old", _arrow(NEXT_X, OLD_Y, FORMED_X, OLD_Y), color=LOST, frames=8),
        Label(
            "old rule: drop B, read from the future",
            (FORMED_X + NEXT_X) / 2,
            OLD_Y - 0.36,
            names="old",
            color=LOST,
            size=11,
            ha="center",
        ),
        _stroke("cash", _line([(B_STOPS, last), (NEXT_X, last)]), color=GOOD, frames=6),
        Label(
            "new rule: B’s return to its last close, then cash",
            NEXT_X - 0.2,
            last - 0.45,
            names="cash",
            color=GOOD,
            size=11,
            ha="right",
        ),
    ]
    return Scene("What the formation cannot know", "look_ahead", tuple(steps))


# --- Drawing ------------------------------------------------------------------

#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("bound_and_y", "look_ahead")
PACED_LABEL_MS, PACED_HOLD_MS = 900, 12000

#: The sketches whose figures come from the owner's archive, which a redraw
#: without it leaves stale.
ARCHIVE_SLUGS = ("bound_and_y",)

#: The refusals a redraw can meet in reading the archive, the ones
#: :func:`chan.low_beta_holdout.main` turns into one line.
REFUSALS = (
    ArchiveUnavailable,
    ArchiveRefused,
    PanelRefused,
    MonthlyRunRefused,
    VintageUnavailable,
    low_beta_holdout.HoldoutRefused,
    NonPositiveBeta,
    EmptyPortfolio,
    UnreadableStandardError,
)


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


def scenes(figures: BoundFigures) -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them."""
    return (_bound_and_y(figures), _look_ahead())


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


def make_low_beta_holdout_whiteboards(
    out_dir: Path | None = None, figures: BoundFigures | None = None
) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order.

    ``figures`` is read from the owner's archive when it is not handed in. The
    schematic needs no archive and is written before that read, so a refused or
    missing archive leaves it redrawn and raises from the read.
    """
    folder = out_dir if out_dir is not None else FIGURES_DIR
    look = _write(_look_ahead(), folder)
    found = figures if figures is not None else BoundFigures.from_run()
    return [_write(_bound_and_y(found), folder), look]


def main() -> None:
    try:
        paths = make_low_beta_holdout_whiteboards()
    except REFUSALS as refused:
        # The schematic's GIF is already written. The one left stale is named,
        # and the exit is non-zero, so a redraw on a machine without the
        # archive does not read as a full one.
        stale = ", ".join(f"{GIF_PREFIX}{slug}.gif" for slug in ARCHIVE_SLUGS)
        raise SystemExit(f"{stale} was not redrawn: {refused}") from refused
    for path in paths:
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
