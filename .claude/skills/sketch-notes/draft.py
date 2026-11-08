"""Draw a whiteboard sketch into a scratch folder and check it, before it is shown.

Usage, from the repo root:

    uv run python .claude/skills/sketch-notes/draft.py MODULE:CALLABLE --out DIR [--paced]

``CALLABLE`` is a function in ``MODULE`` that takes no arguments and returns a
``Scene``, or a tuple of them. A scene that needs a run's figures gets a small
function in a scratch file that builds them and calls the scene, with that
file's folder on ``PYTHONPATH``.

For each scene it writes the GIF and its last frame as a PNG into ``DIR``, which
must lie outside ``docs/figures``, and prints every rule the scene breaks. The
checks are :func:`ithildincore.whiteboard.draft`'s, the same functions the
sketch tests and every other repository's call, so a rule changes in one place.
The layout rules run in the hand font and again in the fallback font.

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
6. A scene draws in one palette. Its strokes, labels and tints use either the
   brass, green and red of :mod:`chan.regime_figure` and their tints, or the
   berry, blue, vermilion and tints of :mod:`chan.palette`, never both. The ink
   and the grey belong to both. A helper whose colour defaults to the brass,
   such as ``_dot``, leaves a mark of the old palette in a scene that has
   moved, and the renderer maps it onto the nearest new ink, which is the grey.

What stays here is what belongs to this repository: the refusal to draft into
``docs/figures``, and the reading of whether a post has moved to the new
colours. A post has moved when ``MODULE`` holds :data:`chan.palette.INKS`, which
is :data:`ithildincore.palette.INKS`, or the :mod:`chan.palette` module itself,
when
``--palette`` says so, or when a scene uses any of :mod:`chan.palette`'s own
colours. The GIF is drawn the way the post's module draws its committed GIFs:
on :data:`chan.palette.INKS` for a post that has moved, and on the brass inks
otherwise. In a post that has moved, any brass colour breaks rule 6, even in a
scene with no other colour. Pass ``--palette`` when ``MODULE`` is a scratch file
that builds a moved post's scene, since such a file need not import
:mod:`chan.palette`. ``--paced`` draws on
:func:`ithildincore.whiteboard.paced_timeline`, which every post module's
``sketch_timeline`` uses for its ``PACED`` scenes.

A scene that breaks none prints ``ok``. The script exits 1 when any scene
breaks a rule, so a caller can act on the result.
"""

from __future__ import annotations

import argparse
import importlib
import os
import sys
from pathlib import Path

from ithildincore.whiteboard import draft

from chan import palette
from chan.paths import FIGURES_DIR


def has_moved(module: object) -> bool:
    """Whether ``module`` draws in :mod:`chan.palette`, read from what it imports."""
    return any(value is palette or value is palette.INKS for value in vars(module).values())


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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("target", help="MODULE:CALLABLE returning a Scene or a tuple of them")
    parser.add_argument("--out", required=True, type=Path, help="a scratch folder")
    parser.add_argument("--paced", action="store_true", help="900 ms labels and a 12 s hold")
    parser.add_argument("--palette", action="store_true", help="the post has moved to chan.palette")
    args = parser.parse_args(argv)
    if inside_figures(args.out):
        sys.exit("draft into a scratch folder, not docs/figures")
    module, _, name = args.target.partition(":")
    loaded = importlib.import_module(module)
    moved = args.palette or has_moved(loaded)
    made = getattr(loaded, name)()
    scenes = made if isinstance(made, tuple) else (made,)
    args.out.mkdir(parents=True, exist_ok=True)
    broken = False
    for scene in scenes:
        found = draft(scene, args.out, args.paced, moved)
        broken = broken or bool(found)
        print(f"{args.out / (scene.slug + '.gif')}: {'see below' if found else 'ok'}")
        for line in found:
            print(f"  {line}")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
