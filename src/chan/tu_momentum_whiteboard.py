"""Whiteboard sketches for the TU momentum post, one for its correlation table and one for Lesson 1.

``blog/tu-momentum-lessons.md`` makes two claims a sentence has to build in
the reader's head: keeping every 25th day stops the future returns from
overlapping while the past returns still overlap, and a later save of the same
closes keeps a different set of 69 days. This module draws the two as scenes,
and the post places each right after the paragraph it draws.

1. Future returns end to end, past returns overlap: the first three days the 250/25 cell keeps on
   the 2012-05-11 save, each drawn to scale on one grey day axis as a brass
   past bar 250 days long ending on the kept day and a black future bar 25
   days long starting there. The shared style draws round caps, so each bar's
   line stops the cap's reach inside its days and its ink covers exactly them.
   Each future bar starts where the one before ends, which a dashed grey join
   marks, each past bar lies over all but 25 days of the one before, and a
   bracket names the 225 of 250 days the first two pasts share. A row of dots,
   one for each of the 69 kept days and spaced evenly rather than to scale,
   closes it. It sits in "The correlation table", after
   the paragraph opening "Neighbouring days share almost all of their
   windows." It holds only for a hold shorter than the lookback, where the
   step is the hold, so any other cell is refused.
2. Same closes, no kept day shared: two lines of ticks, the days the 250/25 cell
   keeps on the 2012-05-11 save above the days it keeps on the 2012-05-17
   save, which starts four trading days later. Only the first four kept days
   of each are drawn, to scale, and a dashed grey link joins each upper tick
   to the lower one four days after it. Labels give the 1,996 closes the saves share,
   all equal, the 69 kept days in each with none shared, and the correlation
   each save gives, 0.2719 and 0.2870, which print as 0.27 and 0.29 at the
   book's two decimals. It sits in Lesson 1, after the paragraph that says
   "that shift alone moves the 250/25 correlation".

Neither sketch is schematic. Every day, count and correlation they print comes
from :class:`SaveFigures`, which :meth:`SaveFigures.from_run` reads from both
saves through :func:`chan.tu_momentum.read_sources` and
:func:`chan.tu_momentum.read_later_save`, so the same scale-break guard runs
as in the replication. The bars and ticks are to scale in trading days. Only
the first sketch's row of dots is not, since 69 days 25 apart would run far
past the board, and its label says so.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look, frame rate and colours.
Each sketch carries more than a reader takes in at that post's pace, so both
are in :data:`PACED`, and :func:`sketch_timeline` holds each of their labels
longer and their finished drawings for twelve seconds, as
:mod:`chan.equity_seasonals_whiteboard` does for its slow sketches. Each GIF
is named :data:`GIF_PREFIX` plus the scene's slug. The post's chart,
``tu_momentum.png``, does not start with that prefix, so nothing that looks
for the sketches by prefix finds the chart.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw both with::

    uv run python -m chan.tu_momentum_whiteboard
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray

from chan import tu_momentum as tu
from chan.matlab_helpers import backshift, fwdshift
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, INK, MUTED
from chan.usdcad_tests_whiteboard import (
    DPI,
    WIDTH,
    XLIM,
    Frame,
    Label,
    Scene,
    Stroke,
    _line,
    _stroke,
    render,
    timeline,
)

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "tu_momentum_sketch_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``tu_momentum_sketch_futures_tile.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


# --- The figures, read from the run ----------------------------------------------


def kept_rows(closes: ArrayLike, lookback: int, hold: int) -> NDArray[np.int64]:
    """The rows :func:`chan.tu_momentum.correlation` keeps for one cell, as positions in ``closes``.

    The rows that have both a past and a future return, then the first of
    them and every ``min(lookback, hold)``-th after it, the selection the
    correlation runs on.
    """
    cl = np.asarray(closes, dtype=float)
    with np.errstate(invalid="ignore", divide="ignore"):
        before = backshift(lookback, cl)
        past = (cl - before) / before
        future = (fwdshift(hold, cl) - cl) / cl
    both = np.flatnonzero(~(np.isnan(past) | np.isnan(future)))
    return both[:: min(lookback, hold)]


@dataclass(frozen=True)
class KeptDays:
    """The days one save's 250/25 cell keeps, and the correlation it gives on them.

    ``rows`` are positions in the save's own closes, and ``days`` their dates.
    """

    save: str
    rows: tuple[int, ...]
    days: tuple[str, ...]
    coefficient: float


@dataclass(frozen=True)
class SaveFigures:
    """What both sketches print: the cell, the kept days on each save, and how the saves line up.

    ``offset`` is how many trading days of the earlier save come before the
    later save's first day. ``shared`` counts the days the saves have in
    common and ``equal`` the ones of those whose closes are equal.
    """

    lookback: int
    hold: int
    earlier: KeptDays
    later: KeptDays
    offset: int
    shared: int
    equal: int

    @property
    def step(self) -> int:
        """How many rows apart the kept days sit, ``min(lookback, hold)``."""
        return min(self.lookback, self.hold)

    @property
    def overlap(self) -> int:
        """How many days of one kept past window the next kept past window covers."""
        return self.lookback - self.step

    @property
    def shared_kept(self) -> int:
        """How many kept days the two saves have in common."""
        return len(set(self.earlier.days) & set(self.later.days))

    @classmethod
    def from_run(cls, data_dir: Path | None = None) -> SaveFigures:
        """Read both saves through the replication's own readers and its scale-break guard."""
        _, earlier = tu.read_sources(data_dir)
        _, later = tu.read_later_save(data_dir)
        return cls.from_closes(earlier, later)

    @classmethod
    def from_closes(
        cls,
        earlier: pd.Series,
        later: pd.Series,
        lookback: int = tu.LOOKBACK,
        hold: int = tu.HOLD_DAYS,
    ) -> SaveFigures:
        """The figures for two saves of one future's closes, the earlier save first."""

        def kept(closes: pd.Series, save: str) -> KeptDays:
            rows = kept_rows(closes.to_numpy(dtype=float), lookback, hold)
            return KeptDays(
                save=save,
                rows=tuple(int(row) for row in rows),
                days=tuple(str(day.date()) for day in closes.index[rows]),
                coefficient=tu.correlation(
                    closes.to_numpy(dtype=float), lookback, hold
                ).coefficient,
            )

        common = earlier.index.intersection(later.index)
        return cls(
            lookback=lookback,
            hold=hold,
            earlier=kept(earlier, str(earlier.index[-1].date())),
            later=kept(later, str(later.index[-1].date())),
            offset=int(earlier.index.get_loc(later.index[0])),
            shared=len(common),
            equal=int((earlier[common] == later[common]).sum()),
        )


def count(value: int) -> str:
    """A count with a thousands comma, as the post writes 1,996."""
    return f"{value:,}"


def four(value: float) -> str:
    """A correlation to four decimals, the precision of the post's table."""
    return f"{value:.4f}"


def book(value: float) -> str:
    """A correlation to two decimals, the precision the book prints."""
    return f"{value:.2f}"


# --- The correlation table: future returns end to end, past returns overlap ------

#: The board across of day 0, the first day of the first kept past window, and
#: how far across one trading day runs.
DAY_X0, PER_DAY = 0.45, 0.0165
#: The heights of the three kept pairs, from the first down.
PAIR_YS = (3.45, 2.65, 2.05)
#: The height of the words above the first pair, and of the bracket between
#: the first and second pasts.
PAIR_WORDS_Y, BRACKET_Y = 3.85, 3.05
#: The height of the grey day axis, of the row of dots, and of the words under it.
AXIS_Y, DOTS_Y, DOTS_WORDS_Y, CLOSING_Y = 1.55, 1.05, 0.68, 0.27
#: Where every pair's date sits across, right of the last future bar.
DATES_X = 6.1
#: Where the row of dots runs across. The dots are evenly spaced, not to scale.
DOTS_X = (0.45, 9.55)
#: How wide the past and future bars are, in points, and how far the bracket's
#: halves stop short of its words on each side.
BAR_WIDTH, BRACKET_GAP = 5.0, 1.5
#: How far a bar's round cap reaches past the end of its line, in board units.
#: The shared style draws every line with round caps, so each bar's line stops
#: this far inside its days and its ink, cap included, covers exactly them.
CAP = BAR_WIDTH / 2 * DPI / 72 / (WIDTH / (XLIM[1] - XLIM[0]))
#: How far each dashed join stops short of the bars it joins.
JOIN_PAST = 0.1
#: How many kept pairs the sketch draws.
PAIRS = 3


def day_x(day: float) -> float:
    """The board across of a trading day, counted from the first kept past window's first day."""
    return DAY_X0 + PER_DAY * day


def _bar(start: float, end: float, y: float, per_unit: float) -> tuple:
    """A bar whose ink, round caps included, covers days ``start`` to ``end`` at height ``y``."""
    return _line([(day_x(start) + CAP, y), (day_x(end) - CAP, y)], per_unit=per_unit)


#: How many holds after the first kept day each later pair starts, in words,
#: one for each of the :data:`PAIRS` after the first.
HOLDS_LATER = ("one hold later", "two holds later")


def _futures_tile(figures: SaveFigures) -> Scene:
    """The correlation table: three kept pairs to scale, futures end to end and pasts piled up.

    The title and the closing lines hold only when the hold is shorter than
    the lookback, so the step is the hold. Then the futures lie end to end and the pasts
    overlap. The other way round the pasts would tile and the futures overlap,
    so any other cell is refused rather than drawn under a false title.
    """
    if not figures.hold < figures.lookback:
        raise ValueError(
            f"the tile sketch draws a hold shorter than the lookback, not "
            f"{figures.lookback}/{figures.hold}"
        )
    kept = figures.earlier
    first = kept.rows[0] - figures.lookback
    steps: list[Stroke | Label] = []
    last_day = kept.rows[PAIRS - 1] - first + figures.hold
    steps.append(
        _stroke(
            "axis", _line([(day_x(0), AXIS_Y), (day_x(last_day), AXIS_Y)]), color=MUTED, frames=6
        )
    )
    steps.append(
        Label("trading days, to scale", DATES_X, AXIS_Y, names="axis", color=MUTED, size=12)
    )
    for k in range(PAIRS):
        day = kept.rows[k] - first
        y = PAIR_YS[k]
        past = f"past-{k + 1}"
        future = f"future-{k + 1}"
        steps.append(
            _stroke(
                past,
                _bar(day - figures.lookback, day, y, per_unit=4),
                color=ACCENT,
                width=BAR_WIDTH,
                frames=6,
            )
        )
        if k == 0:
            steps.append(
                Label(
                    f"past {figures.lookback} days",
                    day_x(day - figures.lookback / 2),
                    PAIR_WORDS_Y,
                    names=past,
                    color=ACCENT,
                    size=12,
                    ha="center",
                )
            )
        steps.append(
            _stroke(
                future,
                _bar(day, day + figures.hold, y, per_unit=10),
                color=INK,
                width=BAR_WIDTH,
                frames=3,
            )
        )
        if k == 0:
            steps.append(
                Label(
                    f"future {figures.hold} days",
                    day_x(day + figures.hold / 2),
                    PAIR_WORDS_Y,
                    names=future,
                    size=12,
                    ha="center",
                )
            )
        if k > 0:
            # A dashed grey join from the end of the future before to the
            # start of this one, the same day, so the two tile end to end.
            steps.append(
                _stroke(
                    f"join-{k}",
                    _line(
                        [(day_x(day), PAIR_YS[k - 1] - JOIN_PAST), (day_x(day), y + JOIN_PAST)],
                        per_unit=10,
                    ),
                    color=MUTED,
                    dashed=True,
                    width=1.5,
                    frames=3,
                )
            )
        when = (
            f"first kept day, {kept.days[k]}" if k == 0 else f"{kept.days[k]}, {HOLDS_LATER[k - 1]}"
        )
        steps.append(Label(when, DATES_X, y, names=future, size=12))
        if k == 1:
            start, end = day_x(day - figures.lookback), day_x(day - figures.step)
            middle = (start + end) / 2
            steps.append(
                _stroke(
                    "bracket-left",
                    _line(
                        [
                            (start, BRACKET_Y + 0.12),
                            (start, BRACKET_Y - 0.12),
                            (start, BRACKET_Y),
                            (middle - BRACKET_GAP, BRACKET_Y),
                        ]
                    ),
                    color=MUTED,
                    width=1.5,
                    frames=4,
                )
            )
            steps.append(
                _stroke(
                    "bracket-right",
                    _line(
                        [
                            (middle + BRACKET_GAP, BRACKET_Y),
                            (end, BRACKET_Y),
                            (end, BRACKET_Y + 0.12),
                            (end, BRACKET_Y - 0.12),
                        ]
                    ),
                    color=MUTED,
                    width=1.5,
                    frames=4,
                )
            )
            steps.append(
                Label(
                    f"{figures.overlap} of {figures.lookback} days shared",
                    middle,
                    BRACKET_Y,
                    names="bracket-right",
                    color=MUTED,
                    size=11,
                    ha="center",
                )
            )
    days = len(kept.rows)
    steps.append(
        Stroke(
            "kept-days",
            np.linspace(*DOTS_X, days),
            np.full(days, DOTS_Y),
            color=INK,
            frames=8,
            dots=4.0,
        )
    )
    steps.append(
        Label(
            f"{days} kept days, every {figures.step}th, dots not to scale",
            (DOTS_X[0] + DOTS_X[1]) / 2,
            DOTS_WORDS_Y,
            names="kept-days",
            size=12,
            ha="center",
        )
    )
    steps.append(
        Label("future returns: no overlap", DOTS_X[0], CLOSING_Y, names="kept-days", size=12)
    )
    steps.append(
        Label(
            "past returns: still overlap",
            DOTS_X[1],
            CLOSING_Y,
            names="kept-days",
            color=ACCENT,
            size=12,
            ha="right",
        )
    )
    return Scene("Future returns end to end, past returns overlap", "futures_tile", tuple(steps))


# --- Lesson 1: same closes, no kept day shared ----------------------------------

#: How many kept days of each save the sketch draws.
SHOWN = 4
#: Where the first upper tick and the last lower tick sit across.
TICKS_X = (0.75, 6.25)
#: The centre height of each row of ticks, the earlier save's on top, and how
#: far each tick reaches up and down from it.
UPPER_Y, LOWER_Y, TICK_HALF = 3.2, 2.4, 0.2
#: Where each row's name sits across, and the height of each first day's date.
ROW_NAMES_X, UPPER_DATE_Y, LOWER_DATE_Y = 6.75, 3.72, 1.88
#: The heights of the four lines of words under the rows.
WORDS_YS = (1.45, 1.05, 0.65, 0.25)


def tick_scale(figures: SaveFigures) -> tuple[float, float]:
    """The board across of the earlier save's row 0, and how far across one trading day runs.

    The first upper tick sits at the left of :data:`TICKS_X` and the last lower
    tick drawn at its right, each at its row in the earlier save's days.
    """
    first = figures.earlier.rows[0]
    last = figures.later.rows[SHOWN - 1] + figures.offset
    per_day = (TICKS_X[1] - TICKS_X[0]) / (last - first)
    return TICKS_X[0] - per_day * first, per_day


def _no_shared_day(figures: SaveFigures) -> Scene:
    """Lesson 1: the two saves' kept days, each lower one four days after an upper one."""
    origin, per_day = tick_scale(figures)

    def across(row: int) -> float:
        return origin + per_day * row

    upper = [across(row) for row in figures.earlier.rows[:SHOWN]]
    lower = [across(row + figures.offset) for row in figures.later.rows[:SHOWN]]
    steps: list[Stroke | Label] = []
    for name, xs, y, color in (
        ("upper", upper, UPPER_Y, INK),
        ("lower", lower, LOWER_Y, ACCENT),
    ):
        points: list[tuple[float, float]] = []
        for x in xs:
            points += [(x, y), (x, y + TICK_HALF), (x, y - TICK_HALF), (x, y)]
        steps.append(
            _stroke(f"{name}-ticks", _line(points, per_unit=12), color=color, width=3.0, frames=8)
        )
        save = figures.earlier if name == "upper" else figures.later
        steps.append(
            Label(
                f"file ending {save.save}",
                ROW_NAMES_X,
                y,
                names=f"{name}-ticks",
                color=color,
                size=12,
            )
        )
        steps.append(
            Label(
                save.days[0],
                xs[0] - 0.12,
                UPPER_DATE_Y if name == "upper" else LOWER_DATE_Y,
                names=f"{name}-ticks",
                color=color,
                size=12,
            )
        )
    for k, (top, bottom) in enumerate(zip(upper, lower, strict=True)):
        steps.append(
            _stroke(
                f"link-{k + 1}",
                _line(
                    [(top, UPPER_Y - TICK_HALF - 0.06), (bottom, LOWER_Y + TICK_HALF + 0.06)],
                    per_unit=12,
                ),
                color=MUTED,
                dashed=True,
                width=1.5,
                frames=3,
            )
        )
    steps.append(
        Label(
            f"each {figures.offset} trading days later",
            ROW_NAMES_X,
            (UPPER_Y + LOWER_Y) / 2,
            names=f"link-{SHOWN}",
            color=MUTED,
            size=12,
        )
    )
    none = "none" if figures.shared_kept == 0 else count(figures.shared_kept)
    every = (
        "every one equal" if figures.equal == figures.shared else f"{count(figures.equal)} equal"
    )
    later_count = len(figures.later.rows)
    earlier_count = len(figures.earlier.rows)
    kept_words = (
        f"{earlier_count} kept days in each, {none} shared"
        if earlier_count == later_count
        else f"{earlier_count} and {later_count} kept days, {none} shared"
    )
    steps.append(
        Label(
            f"first {SHOWN} kept days of each",
            ROW_NAMES_X,
            UPPER_DATE_Y,
            names="lower-ticks",
            color=MUTED,
            size=12,
        )
    )
    cell = f"{figures.lookback}/{figures.hold}"
    lines = (
        f"{count(figures.shared)} closes in both files, {every}",
        kept_words,
        f"{cell} correlation: {four(figures.earlier.coefficient)} on the earlier, "
        f"{four(figures.later.coefficient)} on the later",
        f"at the book’s two decimals: {book(figures.earlier.coefficient)} against "
        f"{book(figures.later.coefficient)}",
    )
    for text, y in zip(lines, WORDS_YS, strict=True):
        steps.append(Label(text, 0.45, y, names="lower-ticks", size=12))
    closes = "Same closes" if figures.equal == figures.shared else "Some closes differ"
    days = "day" if figures.shared_kept == 1 else "days"
    kept = (
        "no kept day shared"
        if figures.shared_kept == 0
        else f"{count(figures.shared_kept)} kept {days} shared"
    )
    return Scene(f"{closes}, {kept}", "no_shared_day", tuple(steps))


# --- Drawing ------------------------------------------------------------------

#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("futures_tile", "no_shared_day")
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


def scenes(figures: SaveFigures | None = None) -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them, the correlation table's then Lesson 1's.

    ``figures`` defaults to :meth:`SaveFigures.from_run` on the committed saves.
    """
    found = figures if figures is not None else SaveFigures.from_run()
    return (_futures_tile(found), _no_shared_day(found))


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


def make_tu_momentum_whiteboards(out_dir: Path | None = None) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes()]


def main() -> None:
    for path in make_tu_momentum_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
