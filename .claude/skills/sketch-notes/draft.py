"""Draw a sketch note into a scratch folder and check its layout, before it is shown.

Usage, from the repo root:

    uv run python .claude/skills/sketch-notes/draft.py MODULE:CALLABLE --out DIR [--paced]

``CALLABLE`` is a function in ``MODULE`` that takes no arguments and returns a
``Scene``, or a tuple of them. A scene that needs a run's figures gets a small
function in a scratch file that builds them and calls the scene, with that
file's folder on ``PYTHONPATH``.

For each scene it writes the GIF and its last frame as a PNG into ``DIR``,
never into ``docs/figures``, and prints every layout rule the scene breaks, in
the hand font and in the fallback font. The rules are the ones the sketch tests
hold.

1. A label or the title sits at least 10 pixels from every stroke and tint.
2. A label or the title sits at least 5 pixels inside the board.
3. No two labels come within 4 pixels of each other.
4. A stroke of more than one point has more points than frames. Otherwise two
   frames show the same picture, the GIF writer merges them, and the GIF's
   timing no longer matches the timeline the tests compare it with.

A scene that breaks none prints ``ok``.
"""

from __future__ import annotations

import argparse
import importlib
import math
import sys
from pathlib import Path

import matplotlib

from chan import usdcad_tests_whiteboard as wb
from chan.usdcad_tests_whiteboard import HEIGHT, WIDTH, Frame, Scene, Stroke, clearances, render

CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4
#: The slower pacing for a sketch a reader finds too fast: each label shows
#: 900 ms instead of 350, and the finished drawing holds 12 seconds instead of 4.
PACED_LABEL_MS, PACED_HOLD_MS = 900, 12000


def frames_for(scene: Scene, paced: bool) -> list[Frame]:
    frames = wb.timeline(scene)
    if not paced:
        return frames
    frames = [
        Frame(f.done, f.partial, PACED_LABEL_MS)
        if f.partial == 0 and f.done and not isinstance(scene.steps[f.done - 1], Stroke)
        else f
        for f in frames
    ]
    last = frames[-1]
    frames[-1] = Frame(last.done, last.partial, PACED_HOLD_MS)
    return frames


def boxes(scene: Scene) -> list:
    """Each visible text on the finished drawing with its box in pixels."""
    with matplotlib.rc_context(wb._style()):
        canvas, artists = wb._board(scene)
        wb._show(scene, artists, Frame(len(scene.steps), 0, 0))
        canvas.draw()
        renderer = canvas.get_renderer()
        return [
            (artist.get_text(), artist.get_window_extent(renderer))
            for artist in artists
            if hasattr(artist, "get_text") and artist.get_visible()
        ]


def problems(scene: Scene) -> list[str]:
    found = [
        f"stroke {step.gid}: {step.frames} frames for {step.points} points"
        for step in scene.strokes
        if step.points > 1 and step.frames >= step.points
    ]
    original = wb.hand_font
    try:
        for fallback in (False, True):
            font = wb.FALLBACK_FONT if fallback else original()
            wb.hand_font = (lambda: wb.FALLBACK_FONT) if fallback else original
            for text, gap in clearances(scene).items():
                if gap < CLEAR_PX:
                    found.append(f"{font}: {text!r} is {gap:.1f} px from a stroke")
            laid = boxes(scene)
            for text, box in laid:
                inside = min(box.x0, box.y0, WIDTH - box.x1, HEIGHT - box.y1)
                if inside < INSIDE_PX:
                    found.append(f"{font}: {text!r} is {inside:.1f} px inside the board")
            for k, (one, a) in enumerate(laid):
                for other, b in laid[k + 1 :]:
                    gap = math.hypot(
                        max(a.x0 - b.x1, b.x0 - a.x1, 0.0), max(a.y0 - b.y1, b.y0 - a.y1, 0.0)
                    )
                    if gap < APART_LABELS_PX:
                        found.append(f"{font}: {one!r} and {other!r} are {gap:.1f} px apart")
    finally:
        wb.hand_font = original
    return found


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("target", help="MODULE:CALLABLE returning a Scene or a tuple of them")
    parser.add_argument("--out", required=True, type=Path, help="a scratch folder")
    parser.add_argument("--paced", action="store_true", help="900 ms labels and a 12 s hold")
    args = parser.parse_args(argv)
    if args.out.resolve() == Path("docs/figures").resolve():
        sys.exit("draft into a scratch folder, not docs/figures")
    module, _, name = args.target.partition(":")
    made = getattr(importlib.import_module(module), name)()
    scenes = made if isinstance(made, tuple) else (made,)
    args.out.mkdir(parents=True, exist_ok=True)
    for scene in scenes:
        frames = frames_for(scene, args.paced)
        images = render(scene, frames)
        gif = args.out / f"{scene.slug}.gif"
        images[0].save(
            gif,
            save_all=True,
            append_images=images[1:],
            duration=[f.ms for f in frames],
            loop=0,
            optimize=False,
        )
        images[-1].convert("RGB").save(args.out / f"{scene.slug}_last.png")
        found = problems(scene)
        verdict = "ok" if not found else "see below"
        print(f"{gif}: {len(frames)} frames, {gif.stat().st_size:,} bytes, {verdict}")
        for line in found:
            print(f"  {line}")


if __name__ == "__main__":
    main()
