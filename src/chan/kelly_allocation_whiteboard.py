"""Whiteboard sketches for the capped Kelly allocation post, one for Lesson 2 and one for Lesson 4.

``blog/capped-kelly-allocation-lessons.md`` makes two claims a sentence has to
build in the reader's head: under the cap, the corner's extra return outweighs
its extra drag, and the line ``F1 + F2 = 2`` fixes the gross leverage only
between its two corners. This module draws the two as scenes, and the post
places each right after the paragraph it draws.

1. Return against drag, in Lesson 2, after the paragraph opening "So the
   proportional split saves 0.147014 of drag". Two columns stand on a grey
   baseline, the proportional split and the corner. Each has a green bar up
   for its return, 0.914785 and 1.2, a red segment down from the bar's top
   for its drag, 0.097986 and 0.245, and a black tick at what remains, the
   growth rate, 0.816798 and 0.955. A dashed grey guide carries the split's
   top across to the corner, where a green bracket spans the 0.285215 of
   return the split gives up. A red bracket beside the top of the corner's
   red segment spans the 0.147014 of drag the split saves, the part of the
   corner's drag beyond the split's. A closing line gives the corner's lead
   in growth rate, 0.138202.
2. Gross against net, in Lesson 4, after the paragraph opening "The
   allocation is not allowed. F1 is negative". F1 runs across and F2 up, in
   equal units. The upper half of the gross cap's diamond, the triangle with
   corners (−2, 0), (2, 0) and (0, 2), is tinted with a green edge, where the
   gross leverage is at most 2. The black line ``F1 + F2 = 2`` runs from
   (2, 0) up past (0, 2). Its stretch from (2, 0) to (0, 2) is redrawn green,
   where the net leverage equals the gross. A green dot marks the corner at
   (0, 2), and the stretch past it is redrawn red, up to a hollow red circle
   at the unbounded peak, whose gross leverage is outside the cap.

Neither sketch is schematic. Every bar, tick, bracket, line and dot sits to
scale at its figure, and :meth:`SketchFigures.from_run` reads each figure from
:mod:`chan.kelly_allocation` through the same
:func:`~chan.kelly_allocation.kelly_leverages`,
:func:`~chan.kelly_allocation.proportional_cap`,
:func:`~chan.kelly_allocation.best_allocation_at_cap`,
:func:`~chan.kelly_allocation.unbounded_allocation_at_cap`,
:func:`~chan.kelly_allocation.growth_terms` and
:func:`~chan.kelly_allocation.growth_rate` the run uses, so a sketch prints
only what the run computes. The return is ``F'M`` and the drag ``F'CF / 2``,
the two terms :func:`~chan.kelly_allocation.growth_terms` returns and
:func:`~chan.kelly_allocation.growth_rate` subtracts. The axes' reach, the
line's end at (−0.5, 2.5) and the board's layout are drawing choices and carry
no figure.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look and frame rate. The post's
chart, :mod:`chan.kelly_allocation_figures`, still draws in
:mod:`chan.regime_figure`'s shared colours, so the sketches do too. The corner
is green and the unbounded peak red in both, and the proportional split's name
is brass, as its marker is in the chart. The post's alt texts call that colour
brown, as the ``sketch-notes`` skill's table of inks says posts do. The
machinery's tints are rectangles, so the triangle's tint is a stroke instead:
rows of the pale green, close enough to overlap, kept inside the triangle's
edge. Each sketch carries more than a reader takes in at that post's pace, so
both are in :data:`PACED`, and :func:`sketch_timeline` holds each of their
labels longer and their finished drawings for twelve seconds, as
:mod:`chan.equity_seasonals_whiteboard` does for its slow sketches. Each GIF is
named :data:`GIF_PREFIX` plus the scene's slug. The post's chart,
``kelly_allocation.png``, does not start with that prefix, so nothing that
looks for the sketches by prefix finds the chart.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw both with::

    uv run python -m chan.kelly_allocation_whiteboard
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from chan.kelly_allocation import (
    CORRELATION,
    MAX_LEVERAGE,
    MEANS,
    VOLS,
    Allocation,
    best_allocation_at_cap,
    covariance,
    growth_rate,
    growth_terms,
    kelly_leverages,
    proportional_cap,
    unbounded_allocation_at_cap,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    DPI,
    REJECT_TINT,
    TINT,
    Fill,
    Frame,
    Label,
    Scene,
    Stroke,
    _arrow,
    _box,
    _dot,
    _line,
    _stroke,
    render,
    timeline,
)

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "kelly_allocation_sketch_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``kelly_allocation_sketch_gross_against_net.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


def figure(value: float) -> str:
    """``value`` at six decimals with trailing zeros dropped, as the post
    writes 0.914785, 1.2 and 0.245, and with a typographic minus."""
    return f"{value:.6f}".rstrip("0").rstrip(".").replace("-", "−")


# --- The figures, read from the run ----------------------------------------------


@dataclass(frozen=True)
class Terms:
    """One allocation's growth rate and its two terms, the return and the drag."""

    leverages: tuple[float, float]
    ret: float
    drag: float
    growth: float

    @classmethod
    def at(cls, leverages, means, cov) -> Terms:
        """:func:`~chan.kelly_allocation.growth_terms` and
        :func:`~chan.kelly_allocation.growth_rate` at ``leverages``, so the
        sketch holds no copy of the formula."""
        ret, drag = growth_terms(leverages, means, cov)
        return cls(
            (float(leverages[0]), float(leverages[1])),
            ret,
            drag,
            growth_rate(leverages, means, cov),
        )


@dataclass(frozen=True)
class SketchFigures:
    """Both sketches' figures: the cap, the proportional split, the corner and
    the line's unbounded peak."""

    cap: float
    split: Terms
    corner: Terms
    corner_growth: float
    peak: Allocation

    @property
    def given_up(self) -> float:
        """The return the proportional split gives up against the corner."""
        return self.corner.ret - self.split.ret

    @property
    def saved(self) -> float:
        """The drag the proportional split saves against the corner."""
        return self.corner.drag - self.split.drag

    @property
    def faster(self) -> float:
        """How much faster the corner grows than the proportional split."""
        return self.corner.growth - self.split.growth

    @property
    def peak_outside(self) -> bool:
        return self.peak.gross > self.cap

    @classmethod
    def from_run(cls) -> SketchFigures:
        """Compute every figure as ``python -m chan.kelly_allocation`` does."""
        cov = covariance(VOLS, CORRELATION)
        capped = proportional_cap(kelly_leverages(MEANS, cov), MAX_LEVERAGE)
        best = best_allocation_at_cap(MEANS, cov, MAX_LEVERAGE)
        return cls(
            cap=MAX_LEVERAGE,
            split=Terms.at(capped, MEANS, cov),
            corner=Terms.at(best.leverages, MEANS, cov),
            corner_growth=best.growth,
            peak=unbounded_allocation_at_cap(MEANS, cov, MAX_LEVERAGE),
        )


# --- Lesson 2: return against drag ------------------------------------------------

#: The baseline's height and the board height of a return of 1.
BASE_Y, PER_UNIT = 0.95, 2.15
#: Each column's left and right edge across the board.
SPLIT_X, CORNER_X = (2.45, 3.25), (5.65, 6.45)
#: How far the baseline runs past the columns, and how far each growth tick
#: reaches past its column's sides.
BASE_OVER, TICK_OVER = 0.4, 0.15
#: Where the split's words end, left of its column, and the corner's start,
#: right of it, and how far apart their lines sit.
SPLIT_WORDS_X, CORNER_WORDS_X, WORDS_STEP = 2.1, 6.95, 0.32
#: How far left of the corner's column the return bracket stands, how far
#: right of it the drag bracket stands, and the length of each bracket's ends.
RETURN_BRACKET_GAP, DRAG_BRACKET_GAP, BRACKET_END = 0.25, 0.25, 0.12
#: Where the return bracket's words end, how far above the guide the lower
#: of its two lines sits, and the height of the column names and closing line.
GIVEN_UP_X, GIVEN_UP_ABOVE = 5.2, 0.3
NAMES_Y, CLOSING_Y = 0.6, 0.22
#: How far above its column the corner's return sits.
RETURN_ABOVE = 0.31
#: How far below the corner's top the drag bracket's words sit, high enough to
#: stay clear of the corner's drag below them.
SAVED_BELOW_TOP = 0.08
#: The edge round each bar's tint.
EDGE = 1.2


def value_y(value: float) -> float:
    """The board height of a return, a drag or a growth rate, from the baseline."""
    return BASE_Y + PER_UNIT * value


def _bar(gid: str, x: tuple[float, float], y0: float, y1: float, tint: str, ink: str):
    """A tinted rectangle with an edge of ``ink`` round it, the edge ``gid`` plus ``-edge``."""
    return Fill(gid, x[0], y0, x[1], y1, tint), _stroke(
        f"{gid}-edge", _box(x[0], y0, x[1], y1), color=ink, width=EDGE, frames=4
    )


def _column(name: str, x: tuple[float, float], terms: Terms) -> list[Stroke | Fill]:
    top, rest = value_y(terms.ret), value_y(terms.growth)
    return [
        *_bar(f"{name}-return", x, BASE_Y, top, TINT, GOOD),
        *_bar(f"{name}-drag", x, rest, top, REJECT_TINT, LOST),
        _stroke(
            f"{name}-growth",
            _line([(x[0] - TICK_OVER, rest), (x[1] + TICK_OVER, rest)], per_unit=8),
            color=INK,
            width=2.6,
            frames=3,
        ),
    ]


def _bracket(gid: str, x: float, y0: float, y1: float, toward: float, color: str) -> Stroke:
    """A square bracket at ``x`` from ``y0`` to ``y1``, its ends pointing ``toward``
    the side its sign gives, +1 for right and −1 for left."""
    end = x + toward * BRACKET_END
    return _stroke(
        gid,
        _line([(end, y0), (x, y0), (x, y1), (end, y1)], per_unit=16),
        color=color,
        width=1.8,
        frames=4,
    )


def _return_against_drag(figures: SketchFigures) -> Scene:
    """Lesson 2: the corner earns more return than it pays in extra drag."""
    split, corner = figures.split, figures.corner
    steps: list[Stroke | Fill | Label] = [
        _stroke(
            "baseline",
            _line([(SPLIT_X[0] - BASE_OVER, BASE_Y), (CORNER_X[1] + BASE_OVER, BASE_Y)]),
            color=MUTED,
            width=1.6,
            frames=4,
        ),
        Label(
            "proportional split",
            sum(SPLIT_X) / 2,
            NAMES_Y,
            names="baseline",
            color=ACCENT,
            size=12,
            ha="center",
        ),
        Label(
            "corner", sum(CORNER_X) / 2, NAMES_Y, names="baseline", color=GOOD, size=12, ha="center"
        ),
    ]
    # The split's three figures stack left of its column, centred on its red
    # segment. The corner's return sits above its column, because its right
    # side holds the drag bracket's words, and its drag and growth sit right
    # of it, beside the red segment's foot and below the tick.
    middle = (value_y(split.ret) + value_y(split.growth)) / 2
    places = {
        "split": [
            (SPLIT_WORDS_X, middle + WORDS_STEP, "right"),
            (SPLIT_WORDS_X, middle, "right"),
            (SPLIT_WORDS_X, middle - WORDS_STEP, "right"),
        ],
        "corner": [
            (sum(CORNER_X) / 2, value_y(corner.ret) + RETURN_ABOVE, "center"),
            (CORNER_WORDS_X, value_y(corner.growth) + 0.08, "left"),
            (CORNER_WORDS_X, value_y(corner.growth) - 0.25, "left"),
        ],
    }
    for name, x, numbers in (("split", SPLIT_X, split), ("corner", CORNER_X, corner)):
        bar, bar_edge, drag, drag_edge, tick = _column(name, x, numbers)
        words = (
            (f"return {figure(numbers.ret)}", bar.gid, GOOD),
            (f"drag {figure(numbers.drag)}", drag.gid, LOST),
            (f"growth {figure(numbers.growth)}", tick.gid, INK),
        )
        marks = ((bar, bar_edge), (drag, drag_edge), (tick,))
        for drawn, (text, gid, color), (words_x, y, ha) in zip(
            marks, words, places[name], strict=True
        ):
            steps += [
                *drawn,
                Label(text, words_x, y, names=gid, color=color, size=11, ha=ha),
            ]
    split_top, corner_top = value_y(split.ret), value_y(corner.ret)
    bracket_x = CORNER_X[0] - RETURN_BRACKET_GAP
    steps += [
        _stroke(
            "guide",
            _line([(SPLIT_X[1], split_top), (bracket_x, split_top)], per_unit=6),
            color=MUTED,
            width=1.4,
            dashed=True,
            frames=4,
        ),
        _bracket("given-up", bracket_x, split_top, corner_top, +1, GOOD),
        Label(
            f"gives up {figure(figures.given_up)}",
            GIVEN_UP_X,
            split_top + GIVEN_UP_ABOVE + WORDS_STEP,
            names="given-up",
            color=GOOD,
            size=11,
            ha="right",
        ),
        Label(
            "of return",
            GIVEN_UP_X,
            split_top + GIVEN_UP_ABOVE,
            names="given-up",
            color=GOOD,
            size=11,
            ha="right",
        ),
    ]
    saved_low = value_y(corner.ret - figures.saved)
    steps += [
        _bracket("saved", CORNER_X[1] + DRAG_BRACKET_GAP, saved_low, corner_top, -1, LOST),
        Label(
            f"saves {figure(figures.saved)} of drag",
            CORNER_WORDS_X,
            corner_top - SAVED_BELOW_TOP,
            names="saved",
            color=LOST,
            size=11,
        ),
    ]
    corner_wins = figures.faster > 0
    steps.append(
        Label(
            (
                f"corner grows faster by {figure(figures.faster)}"
                if corner_wins
                else f"proportional split grows faster by {figure(-figures.faster)}"
            ),
            0.3,
            CLOSING_Y,
            names="corner-growth",
            color=GOOD if corner_wins else ACCENT,
            size=12,
        )
    )
    title = (
        "The split saves less drag than it gives up in return"
        if figures.saved < figures.given_up
        else "The split saves more drag than it gives up in return"
    )
    return Scene(title, "return_against_drag", tuple(steps))


# --- Lesson 4: gross against net ------------------------------------------------

#: Where F1 = 0 and F2 = 0 sit on the board, and the board units for one unit
#: of leverage, the same across and up.
ORIGIN_X, ORIGIN_Y, PER_LEVERAGE = 4.6, 0.64, 1.2
#: How far each axis reaches, in leverage: F1 either side of 0, F2 up from it.
F1_REACH, F2_REACH = 2.2, 2.6
#: How far below the F1 axis its two tick figures sit.
TICK_BELOW = 0.41
#: Where the line ``F1 + F2 = cap`` stops, past the corner, as its F1.
LINE_END_F1 = -0.5
#: The tint's rows: how far apart they sit and how wide each is drawn, in
#: pixels, and how far inside the triangle's edge each stays.
TINT_ROW_PX, TINT_WIDTH_PT, TINT_INSET_PX = 3.0, 4.5, 1.0
#: The hollow circle's radius on the board.
RING = 0.09
#: The board's pixels per unit, the same across and up to within a pixel.
PIXELS_PER_UNIT = 68.0


def at(f1: float, f2: float) -> tuple[float, float]:
    """The board point of the allocation (F1, F2)."""
    return ORIGIN_X + PER_LEVERAGE * f1, ORIGIN_Y + PER_LEVERAGE * f2


def tint_rows(cap: float) -> tuple[np.ndarray, np.ndarray]:
    """Rows of pale green filling the triangle |F1| + F2 ≤ cap, F2 ≥ 0.

    One zigzag through every row, each row inset from the two slanted sides,
    and the zigzag's turns run parallel to them, so no part of the pen leaves
    the triangle. The rows sit closer than the pen is wide, so they overlap and
    read as one tint.
    """
    pen = TINT_WIDTH_PT * DPI / 72 / PIXELS_PER_UNIT / PER_LEVERAGE
    inset = (TINT_INSET_PX / PIXELS_PER_UNIT) / PER_LEVERAGE + pen / 2
    step = TINT_ROW_PX / PIXELS_PER_UNIT / PER_LEVERAGE
    points: list[tuple[float, float]] = []
    f2 = inset
    k = 0
    while True:
        half = cap - f2 - inset * math.sqrt(2)
        if half <= 0:
            break
        row = [(-half, f2), (half, f2)]
        points += row if k % 2 == 0 else row[::-1]
        f2 += step
        k += 1
    return _line([at(*p) for p in points], per_unit=1.5)


def _ring(gid: str, x: float, y: float, color: str) -> Stroke:
    t = np.linspace(0.0, 2 * math.pi, 25)
    return Stroke(gid, x + RING * np.cos(t), y + RING * np.sin(t), color=color, width=2.0, frames=3)


def _gross_against_net(figures: SketchFigures) -> Scene:
    """Lesson 4: the line F1 + F2 = cap fixes the gross only between its corners."""
    cap = figures.cap
    corner_f1, corner_f2 = figures.corner.leverages
    peak_f1, peak_f2 = figures.peak.leverages
    cap_text = figure(cap)
    # The F2 axis comes after the tint, so it is drawn over it rather than
    # showing through its rows as a dotted line.
    steps: list[Stroke | Fill | Label] = [
        _stroke(
            "f1-axis",
            _arrow(*at(-F1_REACH, 0.0), *at(F1_REACH, 0.0)),
            color=MUTED,
            width=1.6,
            frames=4,
        ),
        Label("F1", at(F1_REACH, 0.0)[0] + 0.2, ORIGIN_Y, names="f1-axis", color=MUTED, size=12),
        Label(
            f"−{cap_text}",
            at(-cap, 0.0)[0],
            ORIGIN_Y - TICK_BELOW,
            names="f1-axis",
            color=MUTED,
            size=11,
            ha="center",
        ),
        Label(
            cap_text,
            at(cap, 0.0)[0],
            ORIGIN_Y - TICK_BELOW,
            names="f1-axis",
            color=MUTED,
            size=11,
            ha="center",
        ),
        _stroke(
            "allowed",
            tint_rows(cap),
            color=TINT,
            width=TINT_WIDTH_PT,
            frames=8,
        ),
        _stroke(
            "allowed-edge",
            _line([at(-cap, 0.0), at(0.0, cap), at(cap, 0.0), at(-cap, 0.0)], per_unit=4),
            color=GOOD,
            width=EDGE,
            frames=4,
        ),
        Label(
            f"gross ≤ {cap_text}, allowed",
            ORIGIN_X,
            ORIGIN_Y - 0.32,
            names="allowed-edge",
            color=GOOD,
            size=12,
            ha="center",
        ),
        _stroke(
            "f2-axis",
            _arrow(*at(0.0, 0.0), *at(0.0, F2_REACH)),
            color=MUTED,
            width=1.6,
            frames=4,
        ),
        Label("F2", ORIGIN_X + 0.3, at(0.0, F2_REACH)[1], names="f2-axis", color=MUTED, size=12),
        _stroke(
            "net",
            _line([at(cap, 0.0), at(LINE_END_F1, cap - LINE_END_F1)], per_unit=6),
            color=INK,
            width=2.2,
            frames=8,
        ),
        Label(
            f"net = {cap_text}",
            at(LINE_END_F1, 0.0)[0] - 0.25,
            at(0.0, cap - LINE_END_F1)[1] + 0.12,
            names="net",
            color=INK,
            size=12,
            ha="right",
        ),
        _stroke(
            "equal",
            _line([at(cap, 0.0), at(corner_f1, corner_f2)], per_unit=6),
            color=GOOD,
            width=3.4,
            frames=6,
        ),
        Label(
            "here net = gross",
            at(cap / 2, 0.0)[0] + 0.45,
            at(0.0, cap / 2)[1] + 0.3,
            names="equal",
            color=GOOD,
            size=12,
        ),
        _dot("corner", *at(corner_f1, corner_f2), color=GOOD),
        Label(
            f"corner, g = {figure(figures.corner_growth)}",
            at(corner_f1, 0.0)[0] + 0.4,
            at(0.0, corner_f2)[1] + 0.12,
            names="corner",
            color=GOOD,
            size=12,
        ),
    ]
    outside = figures.peak_outside
    peak_ink = LOST if outside else GOOD
    steps += [
        _stroke(
            "past",
            _line([at(corner_f1, corner_f2), at(LINE_END_F1, cap - LINE_END_F1)], per_unit=6),
            color=LOST,
            width=3.4,
            frames=3,
        ),
        _ring("peak", *at(peak_f1, peak_f2), color=peak_ink),
        Label(
            f"unbounded peak, g = {figure(figures.peak.growth)}",
            at(peak_f1, 0.0)[0] - 0.4,
            at(0.0, peak_f2)[1],
            names="peak",
            color=peak_ink,
            size=11,
            ha="right",
        ),
        Label(
            f"gross {figure(figures.peak.gross)}, " + ("outside" if outside else "inside"),
            at(peak_f1, 0.0)[0] - 0.4,
            at(0.0, peak_f2)[1] - 0.32,
            names="peak",
            color=peak_ink,
            size=11,
            ha="right",
        ),
    ]
    return Scene(
        f"F1 + F2 = {cap_text} leaves the gross cap past the corner",
        "gross_against_net",
        tuple(steps),
    )


# --- Drawing ------------------------------------------------------------------

#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("return_against_drag", "gross_against_net")
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


def scenes(figures: SketchFigures | None = None) -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them, Lesson 2's then Lesson 4's."""
    found = figures if figures is not None else SketchFigures.from_run()
    return (_return_against_drag(found), _gross_against_net(found))


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


def make_kelly_allocation_whiteboards(
    out_dir: Path | None = None, figures: SketchFigures | None = None
) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes(figures)]


def main() -> None:
    for path in make_kelly_allocation_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
