"""Draw a whiteboard sketch into a scratch folder and check it, before it is shown.

Usage, from the repo root:

    uv run python .claude/skills/sketch-notes/draft.py MODULE:CALLABLE --out DIR [--paced]

``CALLABLE`` is a function in ``MODULE`` that takes no arguments and returns a
``Scene``, or a tuple of them. A scene that needs a run's figures gets a small
function in a scratch file that builds them and calls the scene, with that
file's folder on ``PYTHONPATH``.

For each scene it writes the GIF and its last frame as a PNG into ``DIR``, which
must lie outside ``docs/figures``, and prints every rule the scene breaks. The
layout rules run in the hand font and again in the fallback font, and they are
the ones the sketch tests hold.

1. A label or the title sits at least 10 pixels from every stroke and tint.
2. A label or the title sits at least 5 pixels inside the board.
3. No two labels come within 4 pixels of each other.
4. Every label names a stroke or tint that comes before it in the steps.
5. The GIF holds as many frames as the timeline. When two frames show the same
   picture the GIF writer merges them, and the GIF's timing no longer matches
   the timeline the tests compare it with. A stroke drawn over more than one
   frame needs more points than frames to avoid that, and a one-point dot
   needs ``frames=1``. This is stricter than the tests' own check, which
   allows as many points as frames.

A scene that breaks none prints ``ok``. The script exits 1 when any scene
breaks a rule, so a caller can act on the result.
"""

from __future__ import annotations

import argparse
import importlib
import math
import os
import sys
from pathlib import Path

import matplotlib
from PIL import Image

from chan import usdcad_tests_whiteboard as wb
from chan.paths import FIGURES_DIR
from chan.usdcad_tests_whiteboard import (
    HEIGHT,
    WIDTH,
    Fill,
    Frame,
    Label,
    Scene,
    Stroke,
    clearances,
    render,
)

CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4
#: The slower pacing for a sketch a reader finds too fast: each label or tint
#: shows 900 ms instead of 350, and the finished drawing holds 12 seconds
#: instead of 4. ``chan.equity_seasonals_whiteboard`` paces its ``PACED`` list
#: the same way.
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


def inside_figures(out: Path) -> bool:
    """Whether ``out`` is ``docs/figures`` or a folder in it, however it is spelt.

    The folder and each parent that exists are compared with ``samefile``, so a
    relative path, a symlink, or another case on a disk that ignores case all
    count, and so does a folder in it that does not exist yet.
    """
    target = Path(os.path.realpath(out))
    return any(
        place.exists() and os.path.samefile(place, FIGURES_DIR)
        for place in (target, *target.parents)
    )


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


def layout_problems(scene: Scene) -> list[str]:
    """Rules 1 to 4, each layout rule checked in every font the board can fall back to."""
    found = []
    seen: set[str] = set()
    for step in scene.steps:
        if isinstance(step, Label) and step.names not in seen:
            found.append(f"label {step.text!r} names {step.names!r}, which is not drawn before it")
        if isinstance(step, (Stroke, Fill)):
            seen.add(step.gid)
    original = wb.hand_font
    fonts = [original()]
    if fonts[0] != wb.FALLBACK_FONT:
        fonts.append(wb.FALLBACK_FONT)
    try:
        for font in fonts:
            wb.hand_font = (lambda: wb.FALLBACK_FONT) if font == wb.FALLBACK_FONT else original
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


def frame_problems(scene: Scene, timeline_frames: int, gif: Path) -> list[str]:
    """Rule 5: the strokes that will merge frames, and whether the written GIF lost any."""
    found = [
        f"stroke {step.gid}: {step.frames} frames for {step.points} points"
        for step in scene.strokes
        if step.frames > 1 and step.frames >= step.points
    ]
    with Image.open(gif) as image:
        written = image.n_frames
    if written != timeline_frames:
        found.append(f"the GIF holds {written} frames where the timeline has {timeline_frames}")
    return found


def draft(scene: Scene, out: Path, paced: bool) -> list[str]:
    """Write one scene's GIF and last frame into ``out``, and return the rules it breaks."""
    frames = frames_for(scene, paced)
    images = render(scene, frames)
    gif = out / f"{scene.slug}.gif"
    images[0].save(
        gif,
        save_all=True,
        append_images=images[1:],
        duration=[f.ms for f in frames],
        loop=0,
        optimize=False,
    )
    images[-1].convert("RGB").save(out / f"{scene.slug}_last.png")
    return frame_problems(scene, len(frames), gif) + layout_problems(scene)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("target", help="MODULE:CALLABLE returning a Scene or a tuple of them")
    parser.add_argument("--out", required=True, type=Path, help="a scratch folder")
    parser.add_argument("--paced", action="store_true", help="900 ms labels and a 12 s hold")
    args = parser.parse_args(argv)
    if inside_figures(args.out):
        sys.exit("draft into a scratch folder, not docs/figures")
    module, _, name = args.target.partition(":")
    made = getattr(importlib.import_module(module), name)()
    scenes = made if isinstance(made, tuple) else (made,)
    args.out.mkdir(parents=True, exist_ok=True)
    broken = False
    for scene in scenes:
        found = draft(scene, args.out, args.paced)
        broken = broken or bool(found)
        print(f"{args.out / (scene.slug + '.gif')}: {'see below' if found else 'ok'}")
        for line in found:
            print(f"  {line}")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
