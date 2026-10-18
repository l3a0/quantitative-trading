"""Whiteboard sketches of the two strategies in the equity-seasonals post.

``blog/equity-seasonals-lessons.md`` describes Example 7.6 and Example 7.7 in
its section "The two strategies". What a reader has to build in their head
there is timing: what each strategy ranks on, when it ranks, how long it
holds, and which way it bets. A timeline shows that faster than a paragraph,
so this module draws one scene for each strategy, and the post places each
right after the paragraph it draws.

1. The January trade: a calendar year of returns, a ranking at the December
   31 close, the worst tenth bought and the best tenth shorted, held through
   January, with the losers pointed up and the winners down. That is Example
   7.6's bet that the extremes come back, a mean reversion trade.
2. The same-month trade: two monthly strips, last year above this year, with
   March of last year ranked and March of this year held, then April and on.
   The best tenth is bought and the worst shorted, with the winners pointed up
   again and the losers down. That is Example 7.7's bet that a month repeats,
   a seasonal momentum trade.

Both scenes are schematic and carry no data. The ranked dots stand for a
cross-section of stocks sorted by the return each strategy ranks on, and the
two ringed at each end stand for a tenth. No number is drawn, so no test here
reads a vintage. March is an example month, and the scene says the trade moves
on to the next one.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied: its strokes, labels, timeline, renderer and palette, so these
GIFs share that post's look, frame rate, hold and colours. Only the scenes
and the file names are this module's. Each GIF is named
:data:`GIF_PREFIX` plus the scene's slug.

The sketch is deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw both with::

    uv run python -m chan.equity_seasonals_whiteboard
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    Label,
    Scene,
    Stroke,
    _arrow,
    _dot,
    _line,
    _span,
    _stroke,
    render,
    timeline,
)

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "equity_seasonals_"

#: How many stocks the ranked row draws, and how many of them stand for a tenth.
RANKED = 20
TENTH = 2


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``equity_seasonals_january_trade.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


def _ranked(x0: float, y0: float, x1: float, y1: float) -> tuple[np.ndarray, np.ndarray]:
    """:data:`RANKED` stocks sorted by return, lowest at the lower left."""
    t = np.linspace(0.0, 1.0, RANKED)
    return x0 + (x1 - x0) * t, y0 + (y1 - y0) * t


def _ring(x: np.ndarray, y: np.ndarray, pad: float = 0.22) -> tuple:
    """An ellipse round the points ``x``, ``y``, ``pad`` clear of them."""
    cx, cy = float(x.mean()), float(y.mean())
    rx = (float(x.max() - x.min())) / 2 + pad
    ry = (float(y.max() - y.min())) / 2 + pad
    angle = np.linspace(0.0, 2 * math.pi, 40)
    return cx + rx * np.cos(angle), cy + ry * np.sin(angle)


def _cells(x0: float, x1: float, y: float, months: int = 12, half: float = 0.2) -> tuple:
    """A strip of ``months`` cells from ``x0`` to ``x1`` centred on ``y``,
    drawn as one stroke: the outline, then each divider."""
    points = [(x0, y - half), (x1, y - half), (x1, y + half), (x0, y + half), (x0, y - half)]
    width = (x1 - x0) / months
    for k in range(1, months):
        x = x0 + k * width
        points += [(x, y - half), (x, y + half)] if k % 2 else [(x, y + half), (x, y - half)]
    return _line(points)


def _cell(x0: float, x1: float, y: float, month: int, months: int = 12, half: float = 0.2) -> tuple:
    """The outline of month ``month``'s cell, counting January as 0."""
    width = (x1 - x0) / months
    left = x0 + month * width
    return _line(
        [
            (left, y - half),
            (left + width, y - half),
            (left + width, y + half),
            (left, y + half),
            (left, y - half),
        ]
    )


#: Where the January trade's year runs, and where its January ends, one
#: twelfth of the year past the December 31 close.
YEAR = (0.6, 6.0, 3.4)
JANUARY_END = YEAR[1] + (YEAR[1] - YEAR[0]) / 12
#: Where each scene's ranked row runs, from its lowest stock to its highest.
JANUARY_ROW = (0.8, 0.6, 5.6, 2.3)
SAME_MONTH_ROW = (0.8, 0.6, 5.6, 1.75)
#: Where each scene's two arrows stand, and the row of their labels.
ARROWS_X = 7.0


def _january_trade() -> Scene:
    """Example 7.6: rank on a calendar year, hold January, bet the extremes come back."""
    x0, x1, y = YEAR
    stocks = _ranked(*JANUARY_ROW)
    losers = (stocks[0][:TENTH], stocks[1][:TENTH])
    winners = (stocks[0][-TENTH:], stocks[1][-TENTH:])
    return Scene(
        "The January trade",
        "january_trade",
        (
            _stroke("year", _span(x0, x1, y), frames=10),
            Label("a year of returns", (x0 + x1) / 2 + 0.6, 3.85, names="year", ha="center"),
            _dot("close", x1, y),
            _stroke(
                "january", _line([(x1, y), (JANUARY_END, y)]), color=ACCENT, width=4.0, frames=3
            ),
            Label("hold January", JANUARY_END + 0.2, y, names="january", color=ACCENT),
            _stroke("to-rank", _arrow(x1 - 0.05, y - 0.25, x1 - 0.3, 2.7), color=MUTED, frames=4),
            Label("rank at the Dec 31 close", x1 + 0.2, 2.85, names="to-rank", size=12),
            Stroke("ranked", stocks[0], stocks[1], color=MUTED, frames=10, dots=6.0),
            _stroke("buy", _ring(*losers), color=GOOD, frames=6),
            Label("buy the worst tenth", 1.7, 0.3, names="buy", color=GOOD, size=12),
            _stroke("short", _ring(*winners), color=LOST, frames=6),
            Label(
                "short the best tenth", 4.75, 2.75, names="short", color=LOST, ha="right", size=12
            ),
            _stroke("losers-up", _arrow(ARROWS_X, 0.7, ARROWS_X, 1.2), color=GOOD, frames=4),
            Label("losers up", ARROWS_X + 0.3, 0.95, names="losers-up", color=GOOD, size=12),
            _stroke("winners-down", _arrow(ARROWS_X, 2.05, ARROWS_X, 1.5), color=LOST, frames=4),
            Label("winners down", ARROWS_X + 0.3, 1.75, names="winners-down", color=LOST, size=12),
            Label(
                "mean reversion", 9.6, 0.3, names="winners-down", color=ACCENT, ha="right", size=14
            ),
        ),
    )


#: The same-month trade's two strips, last year above this year, and the
#: example month it ranks and holds, counting January as 0.
STRIPS = (2.3, 8.3)
LAST_YEAR, THIS_YEAR = 3.25, 2.45
MARCH, APRIL = 2, 3


def _same_month_trade() -> Scene:
    """Example 7.7: rank on one month a year ago, hold that month, bet it repeats."""
    x0, x1 = STRIPS
    width = (x1 - x0) / 12
    march = x0 + (MARCH + 0.5) * width
    april = x0 + (APRIL + 0.5) * width
    stocks = _ranked(*SAME_MONTH_ROW)
    losers = (stocks[0][:TENTH], stocks[1][:TENTH])
    winners = (stocks[0][-TENTH:], stocks[1][-TENTH:])
    gap = (LAST_YEAR - 0.2, THIS_YEAR + 0.2)
    return Scene(
        "The same-month trade",
        "same_month_trade",
        (
            _stroke("last-year", _cells(x0, x1, LAST_YEAR), frames=10),
            Label("last year", x0 - 0.25, LAST_YEAR, names="last-year", ha="right", size=12),
            _stroke("this-year", _cells(x0, x1, THIS_YEAR), frames=10),
            Label("this year", x0 - 0.25, THIS_YEAR, names="this-year", ha="right", size=12),
            _stroke(
                "march-then", _cell(x0, x1, LAST_YEAR, MARCH), color=ACCENT, width=3.5, frames=4
            ),
            Label("March", march, 3.8, names="march-then", color=ACCENT, ha="center"),
            Label("rank", x1 + 0.25, LAST_YEAR, names="march-then", color=ACCENT, size=12),
            _stroke(
                "repeat", _arrow(march, gap[0] - 0.02, march, gap[1] + 0.02), color=ACCENT, frames=3
            ),
            _stroke(
                "march-now", _cell(x0, x1, THIS_YEAR, MARCH), color=ACCENT, width=3.5, frames=4
            ),
            Label("hold", x1 + 0.25, THIS_YEAR, names="march-now", color=ACCENT, size=12),
            _stroke(
                "april-then", _cell(x0, x1, LAST_YEAR, APRIL), color=MUTED, width=3.0, frames=4
            ),
            _stroke("april-now", _cell(x0, x1, THIS_YEAR, APRIL), color=MUTED, width=3.0, frames=4),
            Label("then April, May, …", april + 0.45, 3.8, names="april-now", color=MUTED, size=12),
            Stroke("ranked", stocks[0], stocks[1], color=MUTED, frames=10, dots=6.0),
            _stroke("buy", _ring(*winners), color=GOOD, frames=6),
            Label("buy the best tenth", 4.55, 1.92, names="buy", color=GOOD, ha="right", size=12),
            _stroke("short", _ring(*losers), color=LOST, frames=6),
            Label("short the worst tenth", 1.55, 0.3, names="short", color=LOST, size=12),
            _stroke("winners-up", _arrow(ARROWS_X, 1.45, ARROWS_X, 2.0), color=GOOD, frames=4),
            Label("winners up", ARROWS_X + 0.3, 1.75, names="winners-up", color=GOOD, size=12),
            _stroke("losers-down", _arrow(ARROWS_X, 1.2, ARROWS_X, 0.7), color=LOST, frames=4),
            Label("losers down", ARROWS_X + 0.3, 0.95, names="losers-down", color=LOST, size=12),
            Label(
                "seasonal momentum",
                9.6,
                0.3,
                names="losers-down",
                color=ACCENT,
                ha="right",
                size=14,
            ),
        ),
    )


def scenes() -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them."""
    return (_january_trade(), _same_month_trade())


def make_equity_seasonals_whiteboards(out_dir: Path | None = None) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the
    order the post reads them."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    paths = []
    for scene in scenes():
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
        paths.append(path)
    return paths


def main() -> None:
    for path in make_equity_seasonals_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
