"""The whiteboard sketch in the post on Chan's SPY index arbitrage.

``blog/index-arbitrage-lessons.md`` says in one paragraph what one unit of the
combination holds: the same dollar weight on each of 98 stocks, their total on
the long side, SPY's weight on the short side, and how little the two sides
differ. A reader gets more from a picture of the two sides at one scale than
from the three figures, so this module draws one scene, sketched stroke by
stroke as if on a whiteboard, as a looping GIF the post places right after
the paragraph that opens "So one unit of the combination is long $1.09386 of
each stock", in "What one unit holds, and when it first earns".

1. What one unit holds: the 98 stocks as a grid of green dots, one for each,
   labelled with their count and the dollars each one holds. A green arrow
   gathers them into one green column labelled long and the stocks' total,
   and a red column beside it, on the same baseline and at the same scale, is
   labelled short SPY and SPY's dollars. The two tops differ by 1.5 percent
   of the columns' height, about 3 pixels, so no bracket between them could
   be read. A callout above the columns names the difference instead, with
   an arrow down to each top, and a closing label says the rule scales the
   whole unit by minus the z-score. Colour is never the only cue, since the words
   long and short sit inside the columns.

The sketch is not schematic. It draws both columns to one scale, so each
column's height is an affine function of its dollars, and nothing in it is
magnified. Every figure it prints, and the count of dots, is read from the
run rather than written in. :meth:`OneUnit.from_run` reads both committed
files through :func:`chan.index_arbitrage.read_sources`, scale-break guard
included, and takes the weights from :func:`chan.index_arbitrage.index_arbitrage`,
the same path ``python -m chan.index_arbitrage`` runs. A run whose figures
would make the words false is refused rather than drawn: one whose stocks do
not all carry one weight, whose stocks' weight is not long, or whose SPY
weight is not short.

The strokes, the timeline and the renderer are
:mod:`chan.usdcad_tests_whiteboard`'s, so an edit there changes this GIF too,
and that module's docstring explains why two draws on one machine give the
same bytes. The GIF is named :data:`GIF_PREFIX` plus the scene's slug, a
prefix chosen so no GIF name starts like the post's chart,
``index_arbitrage.png``. Redraw it with::

    uv run python -m chan.index_arbitrage_whiteboard
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from chan import index_arbitrage as run
from chan.paths import FIGURES_DIR
from chan.regime_figure import GOOD, INK, LOST, MUTED
from chan.series import WindowCrossesScaleBreak
from chan.usdcad_tests_whiteboard import (
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
from chan.vintage import VintageUnavailable

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "index_arbitrage_sketch_"


@dataclass(frozen=True)
class OneUnit:
    """What one unit of the combination holds, in dollars.

    ``stocks`` is how many stocks the basket holds, ``each`` the dollars on
    each, ``long`` their total, which the run sums over its weights rather
    than multiplying, and ``short`` the dollars short of SPY, a positive
    number.
    """

    stocks: int
    each: float
    long: float
    short: float

    @property
    def apart(self) -> float:
        """How many more dollars the long side holds than the short side."""
        return self.long - self.short

    @classmethod
    def from_run(cls, data_dir: Path | None = None) -> OneUnit:
        """Read the committed files and take one unit's dollars from the run's weights."""
        _, _, stocks, index = run.read_sources(data_dir)
        weights = run.index_arbitrage(stocks, index).weights
        basket, spy = weights[:-1], float(weights[-1])
        if not (basket == basket[0]).all():
            raise ValueError("What one unit holds draws one weight on every stock")
        if not basket[0] > 0:
            raise ValueError(f"What one unit holds draws the stocks long, at {basket[0]:.4f}")
        if not spy < 0:
            raise ValueError(f"What one unit holds draws SPY short, at {spy:.4f}")
        return cls(stocks=len(basket), each=float(basket[0]), long=float(basket.sum()), short=-spy)


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``index_arbitrage_sketch_one_unit.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


#: The grid of dots, one for each stock: its columns, the spacing between
#: dots, where its top left dot sits, and each dot's size in points.
GRID_COLUMNS = 14
GRID_STEP = 0.17
GRID_X, GRID_TOP = 0.8, 2.95
DOT = 4.5
#: The baseline both columns stand on, the height the taller one reaches,
#: and each column's left and right edges.
BASE = 0.55
TOP = 3.55
LONG_X = (4.9, 6.5)
SHORT_X = (6.8, 8.4)
#: The height of the callout naming the difference, above both tops, with an
#: arrow from it down to each top.
CALLOUT_Y = 4.3


def grid(count: int) -> tuple[np.ndarray, np.ndarray]:
    """``count`` dots, :data:`GRID_COLUMNS` to a row, filled from the top left."""
    k = np.arange(count)
    return GRID_X + (k % GRID_COLUMNS) * GRID_STEP, GRID_TOP - (k // GRID_COLUMNS) * GRID_STEP


def height(unit: OneUnit, dollars: float) -> float:
    """Where a column holding ``dollars`` reaches, one scale for both columns."""
    return BASE + dollars * (TOP - BASE) / max(unit.long, unit.short)


def _one_unit(unit: OneUnit) -> Scene:
    """The paragraph on one unit: 98 equal longs gathered into one column, beside SPY's short."""
    xs, ys = grid(unit.stocks)
    rows = math.ceil(unit.stocks / GRID_COLUMNS)
    middle = GRID_X + (GRID_COLUMNS - 1) * GRID_STEP / 2
    bottom = GRID_TOP - (rows - 1) * GRID_STEP
    gathered = (GRID_TOP + bottom) / 2
    right_of_grid = GRID_X + GRID_COLUMNS * GRID_STEP + 0.15
    long_top, short_top = height(unit, unit.long), height(unit, unit.short)
    inside = (BASE + min(long_top, short_top)) / 2
    apart_x = (LONG_X[1] + SHORT_X[0]) / 2
    return Scene(
        "What one unit holds",
        "one_unit",
        (
            Stroke("stocks", xs, ys, color=GOOD, frames=14, dots=DOT),
            Label(
                f"{unit.stocks} stocks",
                middle,
                GRID_TOP + 0.4,
                names="stocks",
                color=GOOD,
                size=12,
                ha="center",
            ),
            Label(
                f"${unit.each:.5f} each",
                middle,
                bottom - 0.4,
                names="stocks",
                color=GOOD,
                size=12,
                ha="center",
            ),
            _stroke(
                "gather",
                _arrow(right_of_grid, gathered, LONG_X[0] - 0.2, gathered),
                color=GOOD,
                frames=5,
            ),
            _stroke(
                "base",
                _line([(LONG_X[0] - 0.15, BASE), (SHORT_X[1] + 0.15, BASE)]),
                color=MUTED,
                frames=4,
            ),
            _stroke("long", _box(LONG_X[0], BASE, LONG_X[1], long_top), color=GOOD, frames=8),
            Label(
                f"long\n${unit.long:.3f}",
                sum(LONG_X) / 2,
                inside,
                names="long",
                color=GOOD,
                size=12,
                ha="center",
            ),
            _stroke("short", _box(SHORT_X[0], BASE, SHORT_X[1], short_top), color=LOST, frames=8),
            Label(
                f"short SPY\n${unit.short:.3f}",
                sum(SHORT_X) / 2,
                inside,
                names="short",
                color=LOST,
                size=12,
                ha="center",
            ),
            _stroke(
                "callout-long",
                _arrow(apart_x - 0.4, CALLOUT_Y - 0.33, sum(LONG_X) / 2, long_top + 0.1),
                color=INK,
                frames=4,
            ),
            _stroke(
                "callout-short",
                _arrow(apart_x + 0.4, CALLOUT_Y - 0.33, sum(SHORT_X) / 2, short_top + 0.1),
                color=INK,
                frames=4,
            ),
            Label(
                f"${unit.apart:.3f} apart",
                apart_x,
                CALLOUT_Y,
                names="callout-short",
                size=12,
                ha="center",
            ),
            Label(
                "the rule scales the whole unit\nby minus the z-score",
                0.4,
                0.75,
                names="short",
                color=MUTED,
                size=12,
            ),
        ),
    )


def scenes(unit: OneUnit | None = None) -> tuple[Scene, ...]:
    """The post's one scene. ``unit`` defaults to :meth:`OneUnit.from_run`."""
    return (_one_unit(unit if unit is not None else OneUnit.from_run()),)


def _write(scene: Scene, folder: Path) -> Path:
    frames = timeline(scene)
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


def make_index_arbitrage_whiteboards(
    out_dir: Path | None = None, unit: OneUnit | None = None
) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes(unit)]


def main() -> None:
    try:
        paths = make_index_arbitrage_whiteboards()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # As in chan.index_arbitrage.main, a refusal that names the source or
        # the flagged day reaches the reader as one line.
        raise SystemExit(str(refused)) from refused
    for path in paths:
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
