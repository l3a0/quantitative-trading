"""Whiteboard sketches for the VX against ES post, one for Lesson 2 and one for Lesson 3.

``blog/vx-es-lessons.md`` makes two claims a sentence has to build in the
reader's head: a history shifted by one amount keeps the hedge while uneven
shifts change it, and the exit a rule uses decides when it holds a position.
This module draws the two as scenes, and the post places each right after the
paragraph it draws.

1. One shift slides, it does not tilt: falling dots for one save's days with
   their fit, the same dots shifted right by one amount with a parallel fit,
   and the same dots shifted by uneven amounts with a fit whose slope differs
   by about a quarter, exaggerated so the eye can see it. It sits in Lesson
   2, after the paragraph opening "[The post on GLD and GDX]".
2. Two ways to close a position: a z-score path against the band at −1, 0
   and +1, above two strips that show what each exit holds along it. Holding
   until the opposite band stays long from the dip below −1 to the rise above
   +1, then short until the next dip. Closing at the mean, as ``bollinger.m``
   does, closes each position where the path crosses zero and waits flat for
   the next band. It sits in Lesson 3, after the paragraph opening "Chan’s
   script for Example 3.2, `bollinger.m`, closes each position".

Both sketches are schematic and carry no figures from the run. The dots, the
shifts and the path are made up to show a shape, so no position, slope or
date on them is a value of the hedge, the deviation or the z-score. What
the shift sketch draws is a fact about the arithmetic that holds whatever the
data. Adding one constant to every VX close moves only the intercept of a
regression on it, so the hedge, the deviation and the z-score are unchanged.
What the exits sketch draws holds along the drawn path. There, closing at the
mean opens the same positions at the same crossings as holding until the
opposite band, and stays flat from each zero crossing to the next band. On
other data the mean exit can also open a second long, or a second short,
where the opposite-band rule already holds one. The flat stretches are drawn
short beside the held ones, since in the run the mean exit starts fewer than
one test day in five with no position. After each dip below −1 the drawn path
next reaches +1, and after +1 it next reaches −1, so the strips alternate
here, which the rule does not promise.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look and frame rate. Their
colours are :mod:`chan.palette`'s, which a colour-blind reader can tell apart,
so :func:`render` maps each frame onto :data:`chan.palette.INKS`: berry for
the copy shifted by one amount, blue for a long, and vermilion for the uneven
copy and a short. The grey of a flat stretch sits only 7.5 from the vermilion
under protanopia. Each stretch already carries its word, and a flat one is
drawn thinner than a long or a short, so the two still read apart.
Each sketch carries more than a reader takes in at that post's pace, so both
are in :data:`PACED`, and :func:`sketch_timeline` holds each of their labels
longer and their finished drawings for twelve seconds, as
:mod:`chan.equity_seasonals_whiteboard` does for its slow sketches. Only the
scenes, the pacing and the file names are this module's. Each GIF is named
:data:`GIF_PREFIX` plus the scene's slug, a prefix chosen so no GIF name
starts like the post's chart, ``vx_es.png``, or like a name the sibling post
on the roll return, ``vx_es_roll_return``, would take.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw both with::

    uv run python -m chan.vx_es_whiteboard
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator

from chan.palette import ACCENT, GOOD, INKS, LOST
from chan.paths import FIGURES_DIR
from chan.regime_figure import INK, MUTED
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
GIF_PREFIX = "vx_es_sketch_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``vx_es_sketch_two_exits.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


# --- Lesson 2: one shift slides, it does not tilt ------------------------------

#: Where the axes meet, and how far each runs.
ORIGIN = (0.8, 0.55)
X_END, Y_END = 9.6, 3.75
#: One save's days, made up: 1000·VX across and 50·ES up, falling as VX rises.
SAVE_X = np.array([1.3, 1.6, 1.85, 2.2, 2.45, 2.75, 3.05, 3.35, 3.7])
SAVE_Y = np.array([3.3, 3.12, 2.78, 2.86, 2.5, 2.28, 2.34, 1.98, 1.82])
#: The one amount every close moves by, in board units.
SAME = 2.6
#: The uneven amounts, one for each day. They wobble and grow along the row,
#: so the copy stretches and its fit tilts by about a quarter, enough to see.
#: The run's own change, 3.6 percent, would draw as one degree.
UNEVEN = np.array([5.02, 5.20, 5.18, 5.40, 5.38, 5.56, 5.54, 5.72, 5.74])
#: How far each fit runs past its first and last dot.
FIT_PAST = 0.15


def fit(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """The least-squares line through the dots, as ``(intercept, slope)``."""
    slope, intercept = np.polyfit(x, y, 1)
    return float(intercept), float(slope)


def _fit_line(x: np.ndarray, y: np.ndarray) -> tuple:
    """The fit through the dots, from just before the first to just past the last."""
    intercept, slope = fit(x, y)
    x0, x1 = float(x.min()) - FIT_PAST, float(x.max()) + FIT_PAST
    return _line([(x0, intercept + slope * x0), (x1, intercept + slope * x1)])


def _one_shift() -> Scene:
    """Lesson 2: one amount added to every close moves the fit sideways and keeps its slope."""
    ox, oy = ORIGIN
    same_x, uneven_x = SAVE_X + SAME, SAVE_X + UNEVEN
    return Scene(
        "One shift slides, it does not tilt",
        "one_shift",
        (
            _stroke("x-axis", _line([(ox, oy), (X_END, oy)]), color=MUTED, frames=8),
            Label("1000·VX", X_END, oy - 0.33, names="x-axis", color=MUTED, size=12, ha="right"),
            _stroke("y-axis", _line([(ox, oy), (ox, Y_END)]), color=MUTED, frames=5),
            Label("50·ES", ox + 0.2, Y_END, names="y-axis", color=MUTED, size=12),
            Stroke("save", SAVE_X, SAVE_Y, color=INK, frames=6, dots=6.0),
            _stroke("save-fit", _fit_line(SAVE_X, SAVE_Y), color=INK, frames=6),
            Label("one save", 1.05, 1.3, names="save-fit", color=INK, size=12),
            Stroke("same", same_x, SAVE_Y, color=ACCENT, frames=6, dots=6.0),
            _stroke("same-fit", _fit_line(same_x, SAVE_Y), color=ACCENT, frames=6),
            Label(
                "every close + the same amount: same slope",
                3.0,
                0.95,
                names="same-fit",
                color=ACCENT,
                size=12,
            ),
            Stroke("uneven", uneven_x, SAVE_Y, color=LOST, frames=6, dots=6.0),
            _stroke("uneven-fit", _fit_line(uneven_x, SAVE_Y), color=LOST, frames=6),
            Label(
                "uneven shifts: a different slope",
                9.6,
                1.3,
                names="uneven-fit",
                color=LOST,
                size=12,
                ha="right",
            ),
        ),
    )


# --- Lesson 3: two ways to close a position -----------------------------------

#: Where the path runs across the board, and the board height of a z-score of
#: zero and of one deviation.
PATH_X = (0.9, 9.4)
ZERO_Y, PER_Z = 3.25, 0.42
#: Where the path crosses a band: A below −1, B up through 0, C above +1, D
#: down through 0 and E below −1 again.
CROSSINGS = {"A": 1.6, "B": 4.0, "C": 4.5, "D": 7.2, "E": 7.7}
#: The path's knots as (x, z-score). Each crossing is a knot, and the path is
#: monotone between knots, so it crosses each level exactly at its knot.
KNOTS = (
    (PATH_X[0], 0.3),
    (CROSSINGS["A"], -1.0),
    (2.3, -1.55),
    (3.3, -0.9),
    (CROSSINGS["B"], 0.0),
    (CROSSINGS["C"], 1.0),
    (5.2, 1.5),
    (6.3, 0.9),
    (CROSSINGS["D"], 0.0),
    (CROSSINGS["E"], -1.0),
    (8.4, -1.5),
    (PATH_X[1], -0.9),
)
#: Each strip's rule, the height of its bar and of its rule's name above it,
#: and the height of the words beneath it.
STRIPS = (
    ("opposite", "hold until the opposite band (this run)", 1.92),
    ("mean", "close at the mean (bollinger.m)", 0.86),
)
NAME_ABOVE, WORDS_BELOW = 0.36, 0.36
BAR_WIDTH, FLAT_WIDTH = 7.0, 2.2
#: How far each band's name sits left of where its line starts.
LEVEL_NAME_X = 0.65


def z_y(z: float | np.ndarray) -> float | np.ndarray:
    """The board height of a z-score."""
    return ZERO_Y + PER_Z * np.asarray(z)


def path() -> tuple[np.ndarray, np.ndarray]:
    """The schematic z-score path, sampled along each segment between knots.

    Every knot is a sample, so each crossing in :data:`CROSSINGS` is a point
    of the stroke and the path reaches each band exactly there.
    """
    xs, zs = zip(*KNOTS, strict=True)
    curve = PchipInterpolator(xs, zs)
    grid = [np.array([xs[0]])]
    for x0, x1 in zip(xs, xs[1:], strict=False):
        grid.append(np.linspace(x0, x1, max(2, int(np.ceil((x1 - x0) * 8))) + 1)[1:])
    x = np.concatenate(grid)
    return x, curve(x)


#: Each strip's stretches, in drawing order, as (gid suffix, word, from, to).
#: Holding until the opposite band changes side only at a band. Closing at
#: the mean closes at each zero crossing and opens again at the next band.
HELD = {
    "opposite": (
        ("long-1", "long", "A", "C"),
        ("short", "short", "C", "E"),
        ("long-2", "long", "E", None),
    ),
    "mean": (
        ("long-1", "long", "A", "B"),
        ("flat-1", "flat", "B", "C"),
        ("short", "short", "C", "D"),
        ("flat-2", "flat", "D", "E"),
        ("long-2", "long", "E", None),
    ),
}
WORD_INK = {"long": GOOD, "short": LOST, "flat": MUTED}


def _strip(rule: str, name: str, y: float) -> list[Stroke | Label]:
    """One rule's bar along the path: a thick blue stretch while long, a thick
    vermilion one while short and a thin grey one while flat, each with its word."""
    steps: list[Stroke | Label] = []
    for k, (suffix, word, start, end) in enumerate(HELD[rule]):
        x0 = CROSSINGS[start]
        x1 = CROSSINGS[end] if end else PATH_X[1]
        gid = f"{rule}-{suffix}"
        width = FLAT_WIDTH if word == "flat" else BAR_WIDTH
        steps.append(
            _stroke(
                gid,
                _line([(x0, y), (x1, y)], per_unit=10),
                color=WORD_INK[word],
                width=width,
                frames=4,
            )
        )
        if k == 0:
            steps.append(Label(name, PATH_X[0], y + NAME_ABOVE, names=gid, size=12))
        steps.append(
            Label(
                word,
                (x0 + x1) / 2,
                y - WORDS_BELOW,
                names=gid,
                color=WORD_INK[word],
                size=11,
                ha="center",
            )
        )
    return steps


def _two_exits() -> Scene:
    """Lesson 3: the same path held to the opposite band, and closed at the mean."""
    steps: list[Stroke | Label] = []
    for z, name in ((1, "+1"), (0, "0"), (-1, "−1")):
        gid = f"level-{name}"
        y = float(z_y(z))
        steps.append(
            _stroke(
                gid,
                _line([(PATH_X[0] - 0.05, y), (PATH_X[1] + 0.15, y)]),
                color=MUTED,
                dashed=True,
                width=1.5,
                frames=4,
            )
        )
        steps.append(Label(name, LEVEL_NAME_X, y, names=gid, color=MUTED, size=11, ha="right"))
    x, z = path()
    steps.append(Stroke("path", x, z_y(z), color=INK, frames=12))
    for rule, name, y in STRIPS:
        steps += _strip(rule, name, y)
    return Scene("Two ways to close a position", "two_exits", tuple(steps))


# --- Drawing ------------------------------------------------------------------

#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("one_shift", "two_exits")
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


def scenes() -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them, Lesson 2's then Lesson 3's."""
    return (_one_shift(), _two_exits())


def _write(scene: Scene, folder: Path) -> Path:
    frames = sketch_timeline(scene)
    first, *rest = render(scene, frames, INKS)
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


def make_vx_es_whiteboards(out_dir: Path | None = None) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes()]


def main() -> None:
    for path in make_vx_es_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
