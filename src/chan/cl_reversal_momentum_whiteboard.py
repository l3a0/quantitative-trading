"""Whiteboard sketches for the crude oil reversal and momentum post, for its rule and Lesson 2.

``blog/crude-oil-reversal-momentum-lessons.md`` makes two claims a sentence
has to build in the reader's head: the join buys a dip inside a rise and
shorts a bounce inside a fall, and half a position in each rule adds up to
the join's position. This module draws the two as scenes, and the post places
each right after the text it draws.

1. A dip inside a rise, a bounce inside a fall: two panels side by side, each
   three closes joined by a black line, 40 days ago, 30 days ago and today,
   with a grey dashed level from each lag across to today. Under each panel
   two lines say what reversal alone and momentum alone do, and a closing
   line in green or red says the join goes long or short, beside an arrow at
   today's close that points the same way. It sits in "The rule and the
   file", after the paragraph that ends "and holds nothing on any other day."
   This sketch is schematic. Its dates are the join's first long and its
   first short on the 2012-05-04 save, read from :class:`Lags`. Each panel
   keeps the order of that day's three closes but not their spacing, since
   the short's close sits only 0.50 above its 30-day lag, and its spacing
   across does not follow the 10 and 30 days between the closes. A
   caption under it in the post gives the three closes of each day, which the
   tests read from the run.
2. Half of each rule is the join: a 2×2 grid whose columns are reversal's
   position and whose rows are momentum's. Each cell holds a half-size arrow
   from each rule, green up for a long and red down for a short, and the sum
   they make. The two cells where the rules agree print their counts, and one
   grey label points at both cells where they disagree with the two counts'
   sum, since the post gives only that sum. A closing line says the join holds
   the average of the two rules' positions on those days. It sits in Lesson 2,
   after the paragraph opening "The two rules mostly disagree." This sketch is
   not schematic. Every count it prints comes from :class:`Agreement`, which
   reads :func:`chan.cl_reversal_momentum.four_rules` on the 2012-05-04 save.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look, frame rate and colours.
Each sketch carries more than a reader takes in at that post's pace, so both
are in :data:`PACED`, and :func:`sketch_timeline` holds each of their labels
longer and their finished drawings for twelve seconds, as
:mod:`chan.equity_seasonals_whiteboard` does for its slow sketches. Each GIF
is named :data:`GIF_PREFIX` plus the scene's slug, a prefix chosen so no GIF
name starts like the post's chart, ``cl_reversal_momentum.png``.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw both with::

    uv run python -m chan.cl_reversal_momentum_whiteboard
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from chan import cl_reversal_momentum as crude
from chan.matlab_helpers import backshift
from chan.paths import FIGURES_DIR
from chan.regime_figure import GOOD, INK, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
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
GIF_PREFIX = "cl_reversal_momentum_sketch_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``cl_reversal_momentum_sketch_dip_and_bounce.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


# --- The figures, read from the run ----------------------------------------------


@dataclass(frozen=True)
class Lags:
    """One day's close and the two lags the join compares it with."""

    day: str
    close: float
    reversal_lag: float
    momentum_lag: float

    @property
    def position(self) -> int:
        """The join's position: long below the reversal lag and above the momentum lag."""
        if self.momentum_lag < self.close < self.reversal_lag:
            return 1
        if self.reversal_lag < self.close < self.momentum_lag:
            return -1
        return 0


@dataclass(frozen=True)
class Agreement:
    """How the two rules' positions pair up on the rows where both lags exist.

    Each field counts the rows where reversal alone holds the first position
    named and momentum alone the second.
    """

    long_long: int
    long_short: int
    short_long: int
    short_short: int

    @property
    def rows(self) -> int:
        return self.long_long + self.long_short + self.short_long + self.short_short

    @property
    def disagree(self) -> int:
        return self.long_short + self.short_long


@dataclass(frozen=True)
class JoinFigures:
    """The join's first long and first short, and how the two rules pair up."""

    first_long: Lags
    first_short: Lags
    agreement: Agreement

    @classmethod
    def from_run(cls, data_dir: Path | None = None) -> JoinFigures:
        """Read the 2012-05-04 save through :func:`chan.cl_reversal_momentum.read_cl`.

        It runs :func:`chan.cl_reversal_momentum.four_rules`, so the save goes
        through the same scale-break guard as the replication. It refuses
        unless every row where both lags exist has each rule long or short,
        since the grid has no row or column for a flat rule, and unless the
        join's position on each of those rows is half of each rule's, added,
        which is what the grid's closing line says.
        """
        _, cl = crude.read_cl(data_dir=data_dir)
        rules = crude.four_rules(cl)
        close = cl.to_numpy(dtype=float)
        reversal_lag = backshift(crude.REVERSAL_LOOKBACK, close)
        momentum_lag = backshift(crude.MOMENTUM_LOOKBACK, close)
        both = ~np.isnan(reversal_lag) & ~np.isnan(momentum_lag)
        reversal, momentum = rules.reversal.positions[both], rules.momentum.positions[both]
        if not (np.isin(reversal, (-1.0, 1.0)).all() and np.isin(momentum, (-1.0, 1.0)).all()):
            raise ValueError("a rule is flat on a row where both lags exist")
        join = rules.combination.positions[both]
        if not np.array_equal(join, (reversal + momentum) / 2):
            raise ValueError("the join is not half of each rule on every row with both lags")

        def lags(row: int) -> Lags:
            return Lags(
                day=str(cl.index[row].date()),
                close=float(close[row]),
                reversal_lag=float(reversal_lag[row]),
                momentum_lag=float(momentum_lag[row]),
            )

        positions = rules.combination.positions

        def count(rev: float, mom: float) -> int:
            return int(((reversal == rev) & (momentum == mom)).sum())

        return cls(
            first_long=lags(int(np.argmax(positions > 0))),
            first_short=lags(int(np.argmax(positions < 0))),
            agreement=Agreement(
                long_long=count(1.0, 1.0),
                long_short=count(1.0, -1.0),
                short_long=count(-1.0, 1.0),
                short_short=count(-1.0, -1.0),
            ),
        )


def price(value: float) -> str:
    """A close to two decimals, the precision the save holds."""
    return f"{value:.2f}"


# --- The rule and the file: a dip inside a rise, a bounce inside a fall -----------

#: Where each panel starts across the board, the long's on the left.
LONG_PANEL, SHORT_PANEL = 0.0, 5.0
#: Inside a panel, where the three closes sit across it, in the order they
#: happened, and where the arrow beside today's close stands.
MOMENTUM_X, REVERSAL_X, TODAY_X, ARROW_X = 0.8, 2.3, 3.6, 4.1
#: The schematic heights: the higher lag, the lower lag and today's close,
#: which sits between them. Each panel keeps the order of its three closes,
#: not their spacing.
HIGH, LOW, BETWEEN = 3.35, 2.1, 2.55
#: How far past today's close each dashed level runs, so the dot sits
#: visibly between them.
LEVEL_PAST = 0.2
#: The height of the line over each panel that names its day, the baseline
#: under it that names each close, then the three lines that read the rule,
#: and the closing line's height.
DAY_Y = 3.8
NAMES_Y = 1.68
RULE_YS = (1.3, 0.96, 0.62)
FLAT_Y = 0.24


def _height(day: Lags, value: float) -> float:
    """A close's schematic height: the higher of the day's two lags, the lower, or between."""
    if value == day.close:
        return BETWEEN
    return HIGH if value == max(day.reversal_lag, day.momentum_lag) else LOW


def _panel(day: Lags, x0: float, side: str) -> list[Stroke | Label]:
    """One day's three closes, its two levels, what each rule says and what the join takes."""
    long = day.position > 0
    if day.position == 0:
        raise ValueError(f"the join holds nothing on {day.day}")
    ink = GOOD if long else LOST
    mom = (x0 + MOMENTUM_X, _height(day, day.momentum_lag))
    rev = (x0 + REVERSAL_X, _height(day, day.reversal_lag))
    today = (x0 + TODAY_X, _height(day, day.close))
    end = x0 + TODAY_X + LEVEL_PAST
    arrow_x = x0 + ARROW_X
    tip, tail = (BETWEEN + 0.38, BETWEEN - 0.38) if long else (BETWEEN - 0.38, BETWEEN + 0.38)
    if long:
        rules = ("below the 30-day lag: reversal buys", "above the 40-day lag: momentum buys")
        verdict = "both buy: long"
    else:
        rules = ("above the 30-day lag: reversal shorts", "below the 40-day lag: momentum shorts")
        verdict = "both short: short"
    return [
        _stroke(f"{side}-path", _line([mom, rev, today], per_unit=8), color=INK, frames=8),
        _dot(f"{side}-momentum-lag", *mom, color=INK),
        Label("40 days ago", mom[0], NAMES_Y, names=f"{side}-momentum-lag", size=11, ha="center"),
        _dot(f"{side}-reversal-lag", *rev, color=INK),
        Label("30 days ago", rev[0], NAMES_Y, names=f"{side}-reversal-lag", size=11, ha="center"),
        _dot(f"{side}-today", *today, color=INK),
        Label("today", today[0], NAMES_Y, names=f"{side}-today", size=11, ha="center"),
        Label(
            f"the join’s first {side}, {day.day}",
            x0 + 2.25,
            DAY_Y,
            names=f"{side}-today",
            size=12,
            ha="center",
        ),
        _stroke(
            f"{side}-reversal-level",
            _line([rev, (end, rev[1])], per_unit=10),
            color=MUTED,
            dashed=True,
            width=1.5,
            frames=4,
        ),
        Label(rules[0], x0 + 0.3, RULE_YS[0], names=f"{side}-reversal-level", size=11),
        _stroke(
            f"{side}-momentum-level",
            _line([mom, (end, mom[1])], per_unit=10),
            color=MUTED,
            dashed=True,
            width=1.5,
            frames=4,
        ),
        Label(rules[1], x0 + 0.3, RULE_YS[1], names=f"{side}-momentum-level", size=11),
        _stroke(f"{side}-position", _arrow(arrow_x, tail, arrow_x, tip), color=ink, frames=4),
        Label(verdict, x0 + 0.3, RULE_YS[2], names=f"{side}-position", color=ink, size=12),
    ]


def _dip_and_bounce(figures: JoinFigures) -> Scene:
    """The rule: the join's first long and first short, each between its two lags."""
    return Scene(
        "A dip inside a rise, a bounce inside a fall",
        "dip_and_bounce",
        (
            *_panel(figures.first_long, LONG_PANEL, "long"),
            *_panel(figures.first_short, SHORT_PANEL, "short"),
            _stroke(
                "flat", _line([(3.2, FLAT_Y), (4.0, FLAT_Y)], per_unit=10), color=MUTED, frames=4
            ),
            Label("any other day: flat", 4.2, FLAT_Y, names="flat", color=MUTED, size=12),
        ),
    )


# --- Lesson 2: half of each rule is the join -------------------------------------

#: The grid's two columns, reversal long then reversal short, and its two
#: rows, momentum long on top. A wide gutter between the columns holds the
#: label for both cells where the rules disagree.
COLUMNS = ((1.75, 4.86), (6.49, 9.6))
ROWS = ((2.17, 3.47), (0.72, 2.02))
HEADER_Y = 3.8
ROW_HEADER_X = 1.55
#: Inside a cell: where each rule's arrow stands, reversal's then momentum's,
#: the height the arrows span, and where the sum and the count sit.
ARROW_XS = (0.35, 1.25)
ARROW_SPAN = (0.74, 1.14)
HALF_PAST = 0.36
SUM_Y = 0.38
COUNT_X = 1.95
CLOSING_Y = 0.3
#: Each rule's position, long then short, as the sign of its half.
SIDES = ((1, "long"), (-1, "short"))


def _half(sign: int, first: bool) -> str:
    """One term of a cell's sum, such as ``½`` or ``− ½``."""
    if first:
        return "½" if sign > 0 else "−½"
    return "+ ½" if sign > 0 else "− ½"


def _cell(rev: int, mom: int, x0: float, y0: float, count: int | None) -> list[Stroke | Label]:
    """One cell: a half arrow from each rule, their sum, and its count where the rules agree."""
    name = f"{'long' if rev > 0 else 'short'}-{'long' if mom > 0 else 'short'}"
    steps: list[Stroke | Label] = []
    for rule, sign, dx in (("reversal", rev, ARROW_XS[0]), ("momentum", mom, ARROW_XS[1])):
        low, high = y0 + ARROW_SPAN[0], y0 + ARROW_SPAN[1]
        tail, tip = (low, high) if sign > 0 else (high, low)
        ink = GOOD if sign > 0 else LOST
        gid = f"{name}-{rule}"
        steps.append(_stroke(gid, _arrow(x0 + dx, tail, x0 + dx, tip), color=ink, frames=3))
        steps.append(
            Label("½", x0 + dx + HALF_PAST, (low + high) / 2, names=gid, color=ink, size=12)
        )
    total = rev + mom
    word = "long" if total > 0 else "short" if total < 0 else "flat"
    ink = GOOD if total > 0 else LOST if total < 0 else MUTED
    steps.append(
        Label(
            f"{_half(rev, True)} {_half(mom, False)} = {word}",
            x0 + 0.2,
            y0 + SUM_Y,
            names=f"{name}-momentum",
            color=ink,
            size=12,
        )
    )
    if count is not None:
        steps.append(
            Label(
                f"{count} days",
                x0 + COUNT_X,
                y0 + (ARROW_SPAN[0] + ARROW_SPAN[1]) / 2,
                names=f"{name}-momentum",
                color=ink,
                size=12,
            )
        )
    return steps


def _half_of_each(figures: JoinFigures) -> Scene:
    """Lesson 2: each cell's two half positions add to the join's, long, short or flat."""
    agree = figures.agreement
    counts = {(1, 1): agree.long_long, (-1, -1): agree.short_short}
    boxes: list[Stroke | Label] = []
    for (mom, _), (y0, y1) in zip(SIDES, ROWS, strict=True):
        for (rev, _), (x0, x1) in zip(SIDES, COLUMNS, strict=True):
            gid = f"box-{'long' if rev > 0 else 'short'}-{'long' if mom > 0 else 'short'}"
            boxes.append(_stroke(gid, _box(x0, y0, x1, y1), color=MUTED, width=1.5, frames=4))
    headers: list[Label] = [
        Label(
            f"reversal: {word}",
            (x0 + x1) / 2,
            HEADER_Y,
            names=f"box-{word}-long",
            size=12,
            ha="center",
        )
        for (_, word), (x0, x1) in zip(SIDES, COLUMNS, strict=True)
    ] + [
        Label(
            f"momentum:\n{word}",
            ROW_HEADER_X,
            (y0 + y1) / 2,
            names=f"box-long-{word}",
            size=11,
            ha="right",
        )
        for (_, word), (y0, y1) in zip(SIDES, ROWS, strict=True)
    ]
    cells: list[Stroke | Label] = []
    for (mom, _), (y0, _y1) in zip(SIDES, ROWS, strict=True):
        for (rev, _), (x0, _x1) in zip(SIDES, COLUMNS, strict=True):
            cells += _cell(rev, mom, x0, y0, counts.get((rev, mom)))
    gutter = (COLUMNS[0][1] + COLUMNS[1][0]) / 2
    middle = (ROWS[0][0] + ROWS[1][1]) / 2
    return Scene(
        "Half of each rule is the join",
        "half_of_each",
        (
            *boxes,
            *headers,
            *cells,
            _stroke(
                "to-short-long",
                _arrow(gutter + 0.45, middle + 0.6, COLUMNS[1][0] - 0.1, middle + 0.9),
                color=MUTED,
                frames=3,
            ),
            _stroke(
                "to-long-short",
                _arrow(gutter - 0.45, middle - 0.6, COLUMNS[0][1] + 0.1, middle - 0.9),
                color=MUTED,
                frames=3,
            ),
            Label(
                f"{agree.disagree} days:\nflat",
                gutter,
                middle,
                names="to-long-short",
                color=MUTED,
                size=12,
                ha="center",
            ),
            Label(
                f"on these {agree.rows} days, the join holds the average of the two rules’ "
                "positions",
                5.0,
                CLOSING_Y,
                names="box-short-short",
                size=12,
                ha="center",
            ),
        ),
    )


# --- Drawing ------------------------------------------------------------------

#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("dip_and_bounce", "half_of_each")
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


def scenes(figures: JoinFigures | None = None) -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them, the rule's then Lesson 2's.

    ``figures`` defaults to :meth:`JoinFigures.from_run` on the committed save.
    """
    found = figures if figures is not None else JoinFigures.from_run()
    return (_dip_and_bounce(found), _half_of_each(found))


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


def make_cl_reversal_momentum_whiteboards(out_dir: Path | None = None) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes()]


def main() -> None:
    for path in make_cl_reversal_momentum_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
