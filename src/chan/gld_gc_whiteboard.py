"""Whiteboard sketches for the long GLD, short gold futures post, one for its opening and one for Lesson 4.

``blog/gld-gc-lessons.md`` makes two claims a sentence has to build in the
reader's head: owning the metal and shorting its future cancels the spot
return and leaves the roll return with its sign flipped, and a difference in
when the two legs are recorded would put two moves of gold into each day's
change in their ratio. This module draws the two as scenes, and the post
places each right after the paragraph it draws.

1. Only the roll return is left, in "Why own the metal and short the future",
   after the paragraph opening "Ernest Chan’s *Algorithmic Trading* turns the
   split into a trade." A green arrow up owns the metal and earns the spot
   return. A red arrow down shorts the future and pays back the spot return
   and the roll return. A black line strikes out each spot return, a brown
   arrow points from the roll return to what is left, and a green check
   closes on why that is above 0 in contango. Its words name neither GLD nor
   GC, because the post names them only in the next paragraph.
2. Two moves in each day's change, in Lesson 4, after the paragraph opening
   "Of a 24-hour day, a share of 0.001775 is about 2.6 minutes". A wiggly
   brown gold price runs across yesterday and today. Each day carries a dashed
   grey tick where GC would be recorded if it were recorded at 1:30 p.m., and
   a solid black tick where GLD is recorded at 4 p.m. A brown brace under each
   day marks gold's move between the two ticks. Four lines of words under it
   say what each day's log(GC / GLD) carries, what its daily change carries,
   and what that does to the variance, and a green check closes on the run's
   bound.

The first sketch is schematic and carries no figures. Its arrows and
strikes draw the algebra of the post's sentence, which holds whatever the
returns are. The second is schematic apart from its last line. Its price,
its days and the width of the gap between its ticks are made up to show a
shape, and the gap is drawn far wider than 150 minutes of a day would be. Its
words are the supposition the post tests and rejects, which is why the GC
tick is dashed and its label opens on "if". Its last line reads the bound,
0.001775, from :attr:`chan.gld_gc.Identity.gap_share` on the committed files
through :class:`Bound`, and the minutes from that share of a 24-hour day.

The strikes are the one place a stroke here crosses a label. Every other
label clears every stroke, as the shared rules ask, and each strike crosses
only the spot return it strikes out, which the tests hold.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look and frame rate. They draw
in the shared colours of :mod:`chan.regime_figure`, as the post's chart does.
Each sketch carries more than a reader takes in at that post's pace, so both
are in :data:`PACED`, and :func:`sketch_timeline` holds each of their labels
longer and their finished drawings for twelve seconds, as
:mod:`chan.equity_seasonals_whiteboard` does for its slow sketches. Only the
scenes, the pacing and the file names are this module's. Each GIF is named
:data:`GIF_PREFIX` plus the scene's slug, a prefix chosen so no GIF name
starts like the post's chart, ``gld_gc.png``.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw both with::

    uv run python -m chan.gld_gc_whiteboard
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator

from chan import gld_gc
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    Frame,
    Label,
    Scene,
    Stroke,
    _arrow,
    _check,
    _line,
    _stroke,
    render,
    timeline,
)

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "gld_gc_sketch_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``gld_gc_sketch_roll_left.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


# --- Why own the metal and short the future: only the roll return is left ------

#: Each leg's row height, and the left edge of the words beside its arrow.
OWN_Y, SHORT_Y = 3.55, 2.75
LEG_X = 0.95
#: The arrows' column, and how far each reaches above and below its row.
ARROW_X, ARROW_REACH = 0.5, 0.27
#: Where each term starts along its row: the spot returns share a column, so
#: the two strikes sit one above the other.
SPOT_X, ROLL_X = 4.1, 6.55
#: Each strike is a slash, the way algebra cancels a term: it climbs from
#: just before its spot return's lower left to just past its upper right.
STRIKE_X, STRIKE_RISE = (SPOT_X - 0.1, SPOT_X + 1.85), 0.2
#: The height of the words left after the strikes, and of the closing line.
LEFT_Y, CLOSE_Y = 1.6, 0.62


def _roll_left() -> Scene:
    """The opening: own the metal, short the future, and the spot returns cancel."""
    roll_mid = ROLL_X + 0.95
    return Scene(
        "The spot returns cancel, and the roll return is left",
        "roll_left",
        (
            _stroke(
                "own",
                _arrow(ARROW_X, OWN_Y - ARROW_REACH, ARROW_X, OWN_Y + ARROW_REACH),
                color=GOOD,
                frames=5,
            ),
            Label("own the metal:", LEG_X, OWN_Y, names="own", color=GOOD, size=13),
            Label("+ spot return", SPOT_X, OWN_Y, names="own", color=GOOD, size=13),
            _stroke(
                "short",
                _arrow(ARROW_X, SHORT_Y + ARROW_REACH, ARROW_X, SHORT_Y - ARROW_REACH),
                color=LOST,
                frames=5,
            ),
            Label("short the future:", LEG_X, SHORT_Y, names="short", color=LOST, size=13),
            Label("− spot return", SPOT_X, SHORT_Y, names="short", color=LOST, size=13),
            Label("− roll return", ROLL_X, SHORT_Y, names="short", color=LOST, size=13),
            _stroke(
                "strike-own",
                _line(
                    [
                        (STRIKE_X[0], OWN_Y - STRIKE_RISE),
                        (STRIKE_X[1], OWN_Y + STRIKE_RISE),
                    ],
                    per_unit=4,
                ),
                color=INK,
                width=2.4,
                frames=4,
            ),
            _stroke(
                "strike-short",
                _line(
                    [
                        (STRIKE_X[0], SHORT_Y - STRIKE_RISE),
                        (STRIKE_X[1], SHORT_Y + STRIKE_RISE),
                    ],
                    per_unit=4,
                ),
                color=INK,
                width=2.4,
                frames=4,
            ),
            _stroke(
                "left",
                _arrow(roll_mid, SHORT_Y - 0.36, roll_mid, LEFT_Y + 0.32),
                color=ACCENT,
                frames=5,
            ),
            Label(
                "left: − roll return",
                roll_mid,
                LEFT_Y,
                names="left",
                color=ACCENT,
                size=13,
                ha="center",
            ),
            _stroke("check", _check(0.35, CLOSE_Y), color=GOOD, frames=4),
            Label(
                "in contango the roll return is below 0, so − roll return is above 0",
                0.85,
                CLOSE_Y,
                names="check",
                color=GOOD,
                size=11,
            ),
        ),
    )


# --- Lesson 4: a timing offset puts two moves in each day's change ------------


@dataclass(frozen=True)
class Bound:
    """What the Lesson 4 sketch reads off the run.

    ``gap_share`` is :attr:`chan.gld_gc.Identity.gap_share`, the most of GLD's
    daily variance an offset between the two closes can carry, which the post
    reads as a share of a 24-hour day. ``caveat_minutes`` is the offset the
    book's caveat describes, from 1:30 to 4:00 p.m.
    """

    gap_share: float
    caveat_minutes: int = (16 * 60) - (13 * 60 + 30)

    @property
    def minutes(self) -> float:
        """The share as minutes of a 24-hour day."""
        return self.gap_share * 24 * 60

    @classmethod
    def from_run(cls, data_dir: Path | None = None) -> Bound:
        """Read the bound from :func:`chan.gld_gc.identity` on the committed files."""
        sources = gld_gc.read_sources(data_dir)
        result = gld_gc.gld_gc(sources)
        return cls(gld_gc.identity(sources, result, data_dir).gap_share)


#: Where each day starts, how wide it is drawn, and where in it each tick sits.
DAY_X0 = (0.4, 5.0)
GC_AT, GLD_AT = 3.3, 4.3
#: The ticks' bottom and top, the brace's top and bottom under them, and the
#: height of the tick labels and of the day names.
TICK_Y = (2.2, 3.42)
BRACE_Y = (2.12, 1.92)
TICK_LABEL_Y, DAY_NAME_Y = 3.72, 2.0
#: The heights of the four lines of words under the drawing.
LINE_Y = (1.6, 1.28, 0.96, 0.4)
#: The gold price's knots, as (x, height). It wanders across both days and
#: moves up between the two ticks on each, and nothing in it jumps and comes
#: back.
PRICE_KNOTS = (
    (0.3, 2.85),
    (1.2, 3.05),
    (2.1, 2.62),
    (3.0, 2.78),
    (3.6, 2.55),
    (4.6, 3.05),
    (5.4, 2.9),
    (6.3, 3.12),
    (7.2, 2.7),
    (8.0, 2.95),
    (8.3, 2.62),
    (9.3, 2.98),
    (9.7, 2.86),
)


def day_x(day: int, at: float) -> float:
    """A place ``at`` units into day ``day``, 0 for yesterday and 1 for today."""
    return DAY_X0[day] + at


def price() -> tuple[np.ndarray, np.ndarray]:
    """The schematic gold price, sampled finely enough to draw a little at a time."""
    xs, ys = zip(*PRICE_KNOTS, strict=True)
    x = np.linspace(xs[0], xs[-1], 140)
    return x, PchipInterpolator(xs, ys)(x)


def _brace(x0: float, x1: float, top: float, bottom: float) -> tuple:
    """A brace opening upward, from ``x0`` to ``x1``, its point down at the middle,
    as :mod:`chan.aud_cad_rollover_whiteboard` draws one."""
    middle, centre = (top + bottom) / 2, (x0 + x1) / 2
    return _line(
        [
            (x0, top),
            (x0 + 0.12, middle),
            (centre - 0.12, middle),
            (centre, bottom),
            (centre + 0.12, middle),
            (x1 - 0.12, middle),
            (x1, top),
        ],
        per_unit=8,
    )


def _two_moves(bound: Bound) -> Scene:
    """Lesson 4: if GC were recorded before GLD, each change would carry two moves."""
    x, y = price()
    steps: list[Stroke | Label] = [Stroke("price", x, y, color=ACCENT, frames=12)]
    for day, name in ((0, "yesterday"), (1, "today")):
        gc_x, gld_x = day_x(day, GC_AT), day_x(day, GLD_AT)
        steps += [
            _stroke(
                f"gc-{day}",
                _line([(gc_x, TICK_Y[0]), (gc_x, TICK_Y[1])], per_unit=8),
                color=MUTED,
                width=1.8,
                dashed=True,
                frames=4,
            ),
            _stroke(
                f"gld-{day}",
                _line([(gld_x, TICK_Y[0]), (gld_x, TICK_Y[1])], per_unit=8),
                color=INK,
                width=1.8,
                frames=4,
            ),
        ]
        if day == 0:
            steps += [
                Label(
                    "if GC were recorded at 1:30 p.m.",
                    gc_x + 0.1,
                    TICK_LABEL_Y,
                    names="gc-0",
                    color=MUTED,
                    size=11,
                    ha="right",
                ),
                Label(
                    "GLD recorded at 4 p.m.",
                    gld_x - 0.1,
                    TICK_LABEL_Y,
                    names="gld-0",
                    color=INK,
                    size=11,
                ),
            ]
        steps.append(
            Label(name, DAY_X0[day] + 0.1, DAY_NAME_Y, names="price", color=MUTED, size=11)
        )
    for day in (0, 1):
        steps.append(
            _stroke(
                f"move-{day}",
                _brace(day_x(day, GC_AT), day_x(day, GLD_AT), *BRACE_Y),
                color=ACCENT,
                width=1.8,
                frames=4,
            )
        )
    steps += [
        Label(
            "each day’s log(GC / GLD) carries that day’s move over the gap",
            0.3,
            LINE_Y[0],
            names="move-1",
            color=INK,
            size=11,
        ),
        Label(
            "each change carries two: today’s, and yesterday’s with its sign flipped",
            0.3,
            LINE_Y[1],
            names="move-1",
            color=INK,
            size=11,
        ),
        Label(
            "each move carries the gap’s share of a day’s variance, so the change carries "
            "twice that",
            0.3,
            LINE_Y[2],
            names="move-1",
            color=INK,
            size=10,
        ),
        _stroke("check", _check(0.35, LINE_Y[3]), color=GOOD, frames=4),
        Label(
            f"at most {bound.gap_share:.6f} of a day, about {bound.minutes:.1f} minutes, "
            f"against {bound.caveat_minutes}",
            0.85,
            LINE_Y[3],
            names="check",
            color=GOOD,
            size=12,
        ),
    ]
    return Scene("An offset puts two moves in each day’s change", "two_moves", tuple(steps))


# --- Drawing ------------------------------------------------------------------

#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("roll_left", "two_moves")
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


def scenes(bound: Bound | None = None) -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them, the opening's then Lesson 4's."""
    return (_roll_left(), _two_moves(bound if bound is not None else Bound.from_run()))


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


def make_gld_gc_whiteboards(out_dir: Path | None = None, bound: Bound | None = None) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes(bound)]


def main() -> None:
    for path in make_gld_gc_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
