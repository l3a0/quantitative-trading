"""Whiteboard sketch for the build board post, in the section on the move.

``blog/build-board-on-github-lessons.md`` describes two ways of keeping the
build board current, and the second is easier to see beside the first than to
read after it. This module draws the two as one scene, and the post places it
right after the paragraph that says "A session no longer writes the board."

1. Before and after the move, as two rows of boxes read top to bottom. The top
   row, "before (by hand)", is the update a session or a sub-agent made: read
   the six sections and GitHub, edit, render and run the six checks, then
   write with the version pin. A vermilion arrow labelled "refused" runs from
   the write back to the read, for the pin refusing a write when a section it
   carries changed since the read. The bottom row, "after (from GitHub)", is a
   session setting a label, which is a GitHub event, which starts the Action that
   rebuilds the page. A berry arrow labelled "PR merges / CI finishes" enters
   the event from below with no session behind it, because GitHub records
   those events itself.

The sketch is schematic and carries no figures from any run. Its boxes stand
in the order the post gives the steps, and their sizes and spacing say
nothing about how long a step takes or what it costs. The bottom row shows a
label as the example of what a session sets, though a line in an issue body
or a comment starts a run the same way. A "blocked by" link starts no run, so
the box never says "link". The scheduled runs, the runs started by hand and
the events that start no run are left out.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so this GIF shares that post's look and frame rate. Its colours
are :mod:`chan.palette`'s, which a colour-blind reader can tell apart, so
:func:`render` maps each frame onto :data:`chan.palette.INKS`: vermilion for
the refusal and berry for the events GitHub records. Each coloured arrow also
carries its own words, so colour is never the only cue. The sketch carries
more than a reader takes in at that post's pace, so it is in :data:`PACED`,
and :func:`sketch_timeline` holds each label longer and the finished drawing
for twelve seconds, as :mod:`chan.equity_seasonals_whiteboard` does for its
slow sketches. Only the scene, the choice to pace it and the file name are
this module's. :func:`sketch_timeline` and the GIF writer are copied from
:mod:`chan.equity_seasonals_whiteboard`, with :data:`chan.palette.INKS` passed
to :func:`render`. The GIF is named :data:`GIF_PREFIX` plus the scene's slug.

The sketch is deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw it with::

    uv run python -m chan.build_board_whiteboard
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import numpy as np

from chan.palette import ACCENT, INKS, LOST
from chan.paths import FIGURES_DIR
from chan.regime_figure import MUTED
from chan.usdcad_tests_whiteboard import (
    Frame,
    Label,
    Scene,
    Stroke,
    _arrow,
    _box,
    _line,
    _stroke,
    render,
    timeline,
)

#: The scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "build_board_sketch_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, ``build_board_sketch_update_flow.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


#: Each row's steps in the order the post gives them, as (name, words, width).
#: A name keys the box's strokes, and the width is the box's in board units,
#: wide enough that its words clear its edges in either font.
BEFORE = (
    ("session", "session or\nsub-agent", 1.65),
    ("read", "read 6 sections\n+ GitHub", 2.3),
    ("edit", "edit", 0.9),
    ("render", "render,\n6 checks", 1.5),
    ("write", "write\n+ pin", 1.1),
)
AFTER = (
    ("session", "session", 1.3),
    ("label", "set label", 1.5),
    ("event", "GitHub\nevent", 1.25),
    ("action", "Action\nrebuilds", 1.45),
    ("page", "page", 1.0),
)

#: Each row's heading, and its boxes' bottom and top edges.
ROWS = {
    "before": ("before (by hand)", 2.6, 3.57),
    "after": ("after (from GitHub)", 0.8, 1.77),
}
#: How far above its boxes' top edge a row's heading sits.
HEADING_UP = 0.34
#: Where each row's first box starts, and the space between two boxes.
LEFT, GAP = 0.3, 0.45
#: How far an arrow stops short of the box it leaves or enters.
CLEAR = 0.07
#: The height of the refusal's return under the top row, and where the
#: berry arrow starts beneath the bottom row.
RETURN_Y = 1.96
EVENT_FROM_Y = 0.12

#: Box labels are drawn at this size, read on a phone at half the board's width.
BOX_SIZE = 12


def spans(row: Sequence[tuple[str, str, float]]) -> dict[str, tuple[float, float]]:
    """Each box's left and right edges, laid out from :data:`LEFT` with
    :data:`GAP` between neighbours."""
    found, x = {}, LEFT
    for name, _, width in row:
        found[name] = (x, x + width)
        x += width + GAP
    return found


def _row(tag: str, row: Sequence[tuple[str, str, float]]) -> list[Stroke | Label]:
    """One row: each box and its words, an arrow from the box before it, and
    the row's heading after its first box."""
    heading, bottom, top = ROWS[tag]
    edges, middle = spans(row), (bottom + top) / 2
    steps: list[Stroke | Label] = []
    previous = None
    for name, words, _ in row:
        x0, x1 = edges[name]
        if previous is not None:
            steps.append(
                _stroke(
                    f"{tag}-to-{name}",
                    _arrow(edges[previous][1] + CLEAR, middle, x0 - CLEAR, middle),
                    frames=3,
                )
            )
        steps.append(_stroke(f"{tag}-{name}", _box(x0, bottom, x1, top), frames=5))
        steps.append(
            Label(words, (x0 + x1) / 2, middle, names=f"{tag}-{name}", ha="center", size=BOX_SIZE)
        )
        if previous is None:
            steps.append(
                Label(heading, LEFT, top + HEADING_UP, names=f"{tag}-{name}", color=MUTED, size=12)
            )
        previous = name
    return steps


def _bent_arrow(points: Sequence[tuple[float, float]]) -> tuple:
    """A polyline through ``points`` whose last segment is drawn by
    :func:`chan.usdcad_tests_whiteboard._arrow`, so its head is that one."""
    body_x, body_y = _line(points[:-1])
    head_x, head_y = _arrow(*points[-2], *points[-1])
    return np.concatenate([body_x, head_x[1:]]), np.concatenate([body_y, head_y[1:]])


def _update_flow() -> Scene:
    """The update a session made by hand, above the one GitHub makes now."""
    before, after = spans(BEFORE), spans(AFTER)
    _, top_bottom, _ = ROWS["before"]
    _, low_bottom, _ = ROWS["after"]
    write, read = sum(before["write"]) / 2, sum(before["read"]) / 2
    event = sum(after["event"]) / 2
    steps: list[Stroke | Label] = _row("before", BEFORE)
    steps += [
        _stroke(
            "refused",
            _bent_arrow(
                [
                    (write, top_bottom - CLEAR),
                    (write, RETURN_Y),
                    (read, RETURN_Y),
                    (read, top_bottom - CLEAR),
                ]
            ),
            color=LOST,
            frames=8,
        ),
        Label(
            "refused",
            (write + read) / 2,
            (RETURN_Y + top_bottom) / 2,
            names="refused",
            color=LOST,
            ha="center",
            size=12,
        ),
    ]
    steps += _row("after", AFTER)
    steps += [
        _stroke(
            "github-records",
            _arrow(event, EVENT_FROM_Y, event, low_bottom - CLEAR),
            color=ACCENT,
            width=2.6,
            frames=5,
        ),
        Label(
            "PR merges / CI finishes",
            event + 0.32,
            EVENT_FROM_Y + 0.26,
            names="github-records",
            color=ACCENT,
            size=12,
        ),
    ]
    return Scene("The board before and after the move", "update_flow", tuple(steps))


# --- Drawing ------------------------------------------------------------------

#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("update_flow",)
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
    """The one scene the post embeds."""
    return (_update_flow(),)


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


def make_build_board_whiteboards(out_dir: Path | None = None) -> list[Path]:
    """Write one looping GIF for each scene and return their paths."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes()]


def main() -> None:
    for path in make_build_board_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
