"""Whiteboard sketches for the opening gap post, both in Lesson 1.

``blog/opening-gap-lessons.md`` makes two claims in Lesson 1 that a sentence
has to build in the reader's head: line 23's sign pays a long when the price
falls from the open, and Chan's Python port, which takes the text's sign,
never holds a long at all. This module draws the two as scenes, and the post
places each right after the paragraph it draws.

1. One day, two signs: the post's worked day. On the left, a long day, whose
   open of 100 sits above a dashed grey "yesterday's high", with an arrow
   down to a close of 90. On the right, a short day, whose open of 100 sits
   below a dashed grey "yesterday's low", with an arrow up to a close of 120.
   Under each, the literal reading's return in green and the momentum
   reading's in red, +10% and −10% for the long and +20% and −20% for the
   short, and a closing line that line 23 pays when the jump reverses. It
   sits after the paragraph opening "Take a long day."
2. Why Chan's Python port never holds a long: two columns of where the open
   can land, the script's and the port's, each crossed by the same two dashed
   levels, the previous high times one plus a tenth of the standard deviation
   σ and the previous low times one minus it, and a note under the script's
   column says what high, low and σ are. The script's column is long above
   the upper level, flat between and short below the lower. The port's long
   zone is drawn first, then its short zone from the lower level up past the
   top, then a note that the short is set after the long, and then the long
   zone redrawn as short. Its foot gives the port's days long and short and
   the upward jumps it sold. It sits after the paragraph opening "Chan's
   later Python port of the script".

The first sketch is schematic and carries no figure from the data. Its
prices are the post's worked day, and its returns come from
:func:`chan.opening_gap.daily_returns` on that day, the same synthetic day
``TestTheRules`` in ``tests/test_opening_gap.py`` holds. The open and the
close sit on one price scale shared by both panels, so the fall to 90 is half
as long as the rise to 120. The previous day's high and low sit a fixed
schematic distance from the open, since the worked day gives no price for
them. The second sketch's geometry is schematic too: its levels and zones
show only which side of each level the open falls on, not any price. Its
counts come from the run, through :class:`PortCounts`, which reads the
committed file through :func:`chan.opening_gap.read_sources` and runs
:func:`chan.opening_gap.python_port` on it.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look, frame rate and colours.
The post's chart has not moved to :mod:`chan.palette`, so both sketches draw
in the shared inks of :mod:`chan.regime_figure` and the post keeps one set of
colours. Each sketch carries more than a reader takes in at that post's
pace, so both are in :data:`PACED`, and :func:`sketch_timeline` holds each of
their labels longer and their finished drawings for twelve seconds, as
:mod:`chan.equity_seasonals_whiteboard` does for its slow sketches. Each GIF
is named :data:`GIF_PREFIX` plus the scene's slug. The post's chart,
``opening_gap.png``, does not start with that prefix, so nothing that looks
for the sketches by prefix finds the chart.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw both with::

    uv run python -m chan.opening_gap_whiteboard
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from chan import opening_gap as og
from chan.paths import FIGURES_DIR
from chan.regime_figure import GOOD, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    Frame,
    Label,
    Scene,
    Stroke,
    _arrow,
    _line,
    _stroke,
    render,
    timeline,
)

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "opening_gap_sketch_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``opening_gap_sketch_two_signs.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


def percent(value: float) -> str:
    """A return as a signed whole percent with a typographic minus, such as −10%."""
    return f"{value:+.0%}".replace("-", "−")


def count(value: int) -> str:
    """A count with a thousands comma, as the post writes 1,718."""
    return f"{value:,}"


# --- Lesson 1: one day, two signs ---------------------------------------------

#: The post's worked day: an open of 100, a long day's close of 90 and a short
#: day's close of 120.
OPEN, LONG_CLOSE, SHORT_CLOSE = 100.0, 90.0, 120.0


@dataclass(frozen=True)
class WorkedDay:
    """One side of the worked day and what each reading of line 23 pays on it.

    ``side`` is ``"long"`` or ``"short"``, and the two returns are
    :func:`chan.opening_gap.daily_returns`' on that position, open and close.
    """

    side: str
    open: float
    close: float

    @property
    def position(self) -> float:
        return og.SIDES[self.side]

    def earns(self, reading: str) -> float:
        """The day's return under one reading of line 23."""
        return float(
            og.daily_returns(
                np.array([self.position]),
                np.array([self.open]),
                np.array([self.close]),
                reading=reading,
            )[0]
        )


#: The board's height of the open, and how far one point of price runs up it.
#: Both panels share the scale, so each arrow is as long as its move.
OPEN_Y, PER_POINT = 2.3, 0.06
#: How far the previous day's high sits below the open, and its low above it.
#: Schematic: the worked day gives no price for either.
LEVEL_GAP = 0.3
#: The left edge of each panel, and how far right of it the arrow runs.
PANEL_XS, ARROW_DX = (0.3, 5.2), 2.9
#: Half the open tick's width, and how far each level runs left and right of
#: the arrow.
TICK_HALF, LEVEL_LEFT, LEVEL_RIGHT = 0.3, 0.75, 0.35
#: How far right of the arrow the open and close labels start.
PRICE_WORDS_DX = 0.5
#: The heights of the panel headings, the two readings' rows and the closing line.
HEADING_Y, ROW_YS, CLOSING_Y = 3.75, (1.2, 0.8), 0.35


def price_y(price: float, open_: float = OPEN) -> float:
    """The board's height of a price, on the scale both panels share."""
    return OPEN_Y + PER_POINT * (price - open_)


def worked_days(
    open_: float = OPEN, long_close: float = LONG_CLOSE, short_close: float = SHORT_CLOSE
) -> tuple[WorkedDay, WorkedDay]:
    """The long day and the short day, the post's by default."""
    return WorkedDay("long", open_, long_close), WorkedDay("short", open_, short_close)


def _price(value: float) -> str:
    return f"{value:g}"


def _two_signs(days: tuple[WorkedDay, WorkedDay]) -> Scene:
    """Lesson 1: the worked long day and short day, and what each reading pays on them."""
    steps: list[Stroke | Label] = []
    for day, x0 in zip(days, PANEL_XS, strict=True):
        side = day.side
        x = x0 + ARROW_DX
        open_y = price_y(day.open, day.open)
        close_y = price_y(day.close, day.open)
        level_y = open_y - LEVEL_GAP if side == "long" else open_y + LEVEL_GAP
        steps.append(
            _stroke(
                f"{side}-level",
                _line([(x - LEVEL_LEFT, level_y), (x + LEVEL_RIGHT, level_y)], per_unit=8),
                color=MUTED,
                dashed=True,
                width=1.5,
                frames=4,
            )
        )
        steps.append(Label(f"a {side} day", x0, HEADING_Y, names=f"{side}-level"))
        steps.append(
            Label(
                "yesterday’s high" if side == "long" else "yesterday’s low",
                x - LEVEL_LEFT - 0.2,
                level_y,
                names=f"{side}-level",
                color=MUTED,
                size=12,
                ha="right",
            )
        )
        steps.append(
            _stroke(
                f"{side}-open",
                _line([(x - TICK_HALF, open_y), (x + TICK_HALF, open_y)], per_unit=10),
                width=3.0,
                frames=3,
            )
        )
        steps.append(
            Label(f"open {_price(day.open)}", x + PRICE_WORDS_DX, open_y, names=f"{side}-open")
        )
        steps.append(_stroke(f"{side}-move", _arrow(x, open_y, x, close_y), frames=5))
        steps.append(
            Label(f"close {_price(day.close)}", x + PRICE_WORDS_DX, close_y, names=f"{side}-move")
        )
        for reading, y, color in zip(og.READINGS, ROW_YS, (GOOD, LOST), strict=True):
            steps.append(
                Label(
                    f"{reading}: {side} earns {percent(day.earns(reading))}",
                    x0,
                    y,
                    names=f"{side}-move",
                    color=color,
                    size=12,
                )
            )
    steps.append(
        Label(
            "line 23 pays when the jump reverses", 5.0, CLOSING_Y, names="short-move", ha="center"
        )
    )
    return Scene("One day, two signs", "two_signs", tuple(steps))


# --- Lesson 1: why the port never holds a long ---------------------------------


@dataclass(frozen=True)
class PortCounts:
    """What the port sketch prints: the port's days long and short, and the upward jumps.

    ``upward`` counts the days that pass the long test, which is the script's,
    and ``sold`` the ones of those the port is short on.
    """

    long: int
    short: int
    upward: int
    sold: int

    @classmethod
    def from_port(cls, port: og.PythonPort) -> PortCounts:
        held = port.positions
        return cls(
            long=int((held == 1).sum()),
            short=int((held == -1).sum()),
            upward=int(port.longs.sum()),
            sold=int((port.longs & (held == -1)).sum()),
        )

    @classmethod
    def from_run(cls, data_dir: Path | None = None) -> PortCounts:
        """Read the committed file through the replication's reader and run the port on it."""
        _, prices = og.read_sources(data_dir)
        return cls.from_port(og.python_port(prices))


#: Where each column runs across, the script's and the port's, and how far
#: right of the port's long zone its short zone runs.
SCRIPT_X, PORT_X, SHORT_DX = 2.85, 5.25, 0.28
#: The heights of the columns' foot, the lower level, the upper level, the top
#: of the zones and the tip of each arrow.
FOOT_Y, LOWER_Y, UPPER_Y, TOP_Y, TIP_Y = 1.0, 1.72, 2.5, 3.32, 3.5
#: Where the dashed levels start and end across.
LEVELS_X = (SCRIPT_X - 0.3, PORT_X + SHORT_DX + 0.25)
#: How wide a zone is drawn, in points, and how wide the redrawn long zone is,
#: so it covers the green beneath it.
ZONE_WIDTH, REDRAWN_WIDTH, SHORT_WIDTH = 8.0, 9.5, 6.0
#: How far right of each column its words start.
SCRIPT_WORDS_DX, PORT_WORDS_DX = 0.3, 0.8
#: The heights of the headings, of the port's two lines in its long zone, and
#: of the two lines at the foot.
HEADINGS_Y, PORT_LONG_YS, FOOT_YS = 3.87, (3.15, 2.76), (0.62, 0.25)

UPPER_WORDS = "high × (1 + 0.1σ)"
LOWER_WORDS = "low × (1 − 0.1σ)"


def _middle(y0: float, y1: float) -> float:
    return (y0 + y1) / 2


def _port_never_long(counts: PortCounts) -> Scene:
    """Lesson 1: the script's three zones beside the port's, whose short covers its long.

    The title holds only when the port is never long, so any other count is
    refused rather than drawn under a false title.
    """
    if counts.long != 0:
        raise ValueError(
            f"the port sketch draws a port that is never long, not long on {counts.long}"
        )
    steps: list[Stroke | Label] = []
    for name, x in (("script", SCRIPT_X), ("port", PORT_X)):
        steps.append(
            _stroke(f"{name}-axis", _arrow(x, FOOT_Y, x, TIP_Y), color=MUTED, width=1.5, frames=6)
        )
        steps.append(Label(f"the {name}", x, HEADINGS_Y, names=f"{name}-axis", ha="center"))
    steps.append(
        Label(
            "open price",
            (SCRIPT_X + PORT_X) / 2,
            TIP_Y,
            names="port-axis",
            color=MUTED,
            size=12,
            ha="center",
        )
    )
    for name, y, words in (("upper", UPPER_Y, UPPER_WORDS), ("lower", LOWER_Y, LOWER_WORDS)):
        steps.append(
            _stroke(
                f"{name}-level",
                _line([(LEVELS_X[0], y), (LEVELS_X[1], y)], per_unit=4),
                color=MUTED,
                dashed=True,
                width=1.5,
                frames=6,
            )
        )
        steps.append(
            Label(
                words, LEVELS_X[0] - 0.2, y, names=f"{name}-level", color=MUTED, size=12, ha="right"
            )
        )
    for text, y in zip(
        ("high, low: the previous day’s", "σ: the 90-day standard deviation"), FOOT_YS, strict=True
    ):
        steps.append(Label(text, 0.3, y, names="lower-level", color=MUTED, size=12))
    script_words = SCRIPT_X + SCRIPT_WORDS_DX
    steps.append(
        _stroke(
            "script-long",
            _line([(SCRIPT_X, UPPER_Y), (SCRIPT_X, TOP_Y)], per_unit=10),
            color=GOOD,
            width=ZONE_WIDTH,
            frames=4,
        )
    )
    steps.append(
        Label(
            "long", script_words, _middle(UPPER_Y, TOP_Y), names="script-long", color=GOOD, size=12
        )
    )
    steps.append(
        Label(
            "flat",
            script_words,
            _middle(LOWER_Y, UPPER_Y),
            names="script-axis",
            color=MUTED,
            size=12,
        )
    )
    steps.append(
        _stroke(
            "script-short",
            _line([(SCRIPT_X, LOWER_Y), (SCRIPT_X, FOOT_Y)], per_unit=10),
            color=LOST,
            width=ZONE_WIDTH,
            frames=4,
        )
    )
    steps.append(
        Label(
            "short",
            script_words,
            _middle(FOOT_Y, LOWER_Y),
            names="script-short",
            color=LOST,
            size=12,
        )
    )
    port_words = PORT_X + PORT_WORDS_DX
    steps.append(
        _stroke(
            "port-long",
            _line([(PORT_X, UPPER_Y), (PORT_X, TOP_Y)], per_unit=10),
            color=GOOD,
            width=ZONE_WIDTH,
            frames=4,
        )
    )
    steps.append(Label("long", port_words, PORT_LONG_YS[0], names="port-long", color=GOOD, size=12))
    short_x = PORT_X + SHORT_DX
    steps.append(
        _stroke(
            "port-short",
            _arrow(short_x, LOWER_Y, short_x, TIP_Y),
            color=LOST,
            width=SHORT_WIDTH,
            frames=6,
        )
    )
    steps.append(
        Label(
            "short: open ≥ low × (1 − 0.1σ)",
            port_words,
            _middle(LOWER_Y, UPPER_Y),
            names="port-short",
            color=LOST,
            size=12,
        )
    )
    steps.append(
        Label(
            "short set last, so it wins",
            port_words,
            PORT_LONG_YS[1],
            names="port-short",
            color=MUTED,
            size=12,
        )
    )
    steps.append(
        _stroke(
            "port-redrawn",
            _line([(PORT_X, UPPER_Y), (PORT_X, TOP_Y)], per_unit=10),
            color=LOST,
            width=REDRAWN_WIDTH,
            frames=4,
        )
    )
    steps.append(
        Label(
            "→ short", port_words + 0.65, PORT_LONG_YS[0], names="port-redrawn", color=LOST, size=12
        )
    )
    steps.append(
        Label("flat", port_words, _middle(FOOT_Y, LOWER_Y), names="port-axis", color=MUTED, size=12)
    )
    sold = (
        f"all {count(counts.upward)} upward jumps sold"
        if counts.sold == counts.upward
        else f"{count(counts.sold)} of {count(counts.upward)} upward jumps sold"
    )
    for text, y in zip(
        (f"long on {count(counts.long)} days, short on {count(counts.short)}", sold),
        FOOT_YS,
        strict=True,
    ):
        steps.append(Label(text, PORT_X - 0.2, y, names="port-redrawn", size=12))
    return Scene("Why Chan’s Python port never holds a long", "port_never_long", tuple(steps))


# --- Drawing ------------------------------------------------------------------

#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("two_signs", "port_never_long")
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


def scenes(counts: PortCounts | None = None) -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them, the worked day's then the port's.

    ``counts`` defaults to :meth:`PortCounts.from_run` on the committed file.
    """
    found = counts if counts is not None else PortCounts.from_run()
    return (_two_signs(worked_days()), _port_never_long(found))


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


def make_opening_gap_whiteboards(out_dir: Path | None = None) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes()]


def main() -> None:
    for path in make_opening_gap_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
