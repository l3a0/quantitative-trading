"""Whiteboard sketches for the XLE against USO post, one for Lesson 1 and one for Lesson 5.

``blog/xle-uso-roll-return-lessons.md`` makes two claims a sentence has to
build in the reader's head: the script's front moves to the next contract while
the old one is still priced, so "front month" means the contract the script
reads, and the roll return the ratio implies comes close to USO's fall on the
contango days and is a small part of its rise on the backwardation days. This module
draws the two as scenes, and the post places each right after the list it
draws.

1. The front moves on before the last price, in Lesson 1, after the two-item
   list whose first item opens "XLE stands in for crude’s spot price." On a
   trading-day axis from October 2006 to January 2007, a thin grey bar runs to
   CL-2007F's last price, a thick black bar marks CL-2007F's front window, and
   a second thick black bar marks CL-2007G's, starting on the row after,
   with grey words naming it the February 2007 contract, since the post names
   only CL-2007F by its month.
   A brown brace over the rows where the two overlap says CL-2007F is still
   priced there, so the front is the second-nearest contract. A closing note
   gives how often the front is the nearest contract the file prices and how
   often the second-nearest.
2. USO's log move against the roll return the ratio implies, in Lesson 5,
   after the two-item list whose first item opens "On the contango days, the
   implied roll return comes close to USO’s fall." Two groups of two bars
   meet a zero line: on the contango days a black bar down for USO's log
   move beside a brown bar nearly as long for the roll return, with the
   word "close" beside it, and on the backwardation days a black bar up for USO's log move
   beside a short brown bar for the roll return, with a black brace on the
   gap. A closing note says how the roll return is summed.

Neither sketch is schematic. Every date, count and value on them comes from
:class:`Handover` and :class:`Split`, which read
:func:`chan.xle_uso_roll_return.front_windows` and
:func:`chan.xle_uso_roll_return.by_view` on the committed files. Every bar
in the first sits on the axis at its own trading days, and every bar in the
second ends at an affine function of its value. Both values in each group are
log quantities, so every bar is drawn to one scale.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look and frame rate. They draw
in the shared colours of :mod:`chan.regime_figure`, as the post's chart does.
Each sketch carries more than a reader takes in at that post's pace, so both
are in :data:`PACED`, and :func:`sketch_timeline` holds each of their labels
longer and their finished drawings for twelve seconds, as
:mod:`chan.equity_seasonals_whiteboard` does for its slow sketches. Each GIF
is named :data:`GIF_PREFIX` plus the scene's slug, a prefix chosen so no GIF
name starts like the post's chart, ``xle_uso_roll_return.png``.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw both with::

    uv run python -m chan.xle_uso_roll_return_whiteboard
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from chan import xle_uso_roll_return as trade
from chan.matlab_helpers import fwdshift
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, INK, MUTED
from chan.usdcad_tests_whiteboard import (
    Frame,
    Label,
    Scene,
    Stroke,
    _box,
    _line,
    _signed,
    _stroke,
    render,
    timeline,
)

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "xle_uso_roll_return_sketch_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``xle_uso_roll_return_sketch_roll_vs_uso.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


def _day(date: str) -> str:
    """A date's month and day, ``12-06`` for ``2006-12-06``."""
    return date[5:]


#: CL's month codes, January to December, as each contract's last letter.
MONTH_CODES = "FGHJKMNQUVXZ"


def _delivery(symbol: str) -> str:
    """A contract's delivery month, ``February 2007`` for ``CL-2007G``."""
    month = MONTH_CODES.index(symbol[-1]) + 1
    return pd.Timestamp(year=int(symbol[-5:-1]), month=month, day=1).strftime("%B %Y")


def _month(date: str) -> str:
    """A date's month and year, ``Oct 2006`` for ``2006-10-16``."""
    return pd.Timestamp(date).strftime("%b %Y")


# --- Lesson 1: the front moves on before the last price -----------------------

#: The trading days the handover sketch's axis spans, on the strip's calendar.
AXIS_FROM, AXIS_TO = "2006-10-16", "2007-01-12"


@dataclass(frozen=True)
class Handover:
    """What the Lesson 1 sketch reads off the run.

    ``days`` are the axis's trading days on the CL strip's calendar. ``old``
    and ``new`` name the first two contracts the script reads as the front,
    ``old_first`` to ``old_last`` and ``new_first`` to ``new_last`` their
    front windows, with ``old_rows`` and ``new_rows`` the rows each holds, and
    ``old_expiry`` the old contract's last priced day. ``overlap`` counts the
    new contract's front rows on which the old one is still priced.
    ``with_ratio`` counts the trade's days with a ratio, ``nearest`` those on
    which the front is the nearest contract the file prices that day, and
    ``second`` those on which it is the second-nearest.
    """

    days: tuple[str, ...]
    old: str
    new: str
    old_first: str
    old_last: str
    old_rows: int
    old_expiry: str
    new_first: str
    new_last: str
    new_rows: int
    overlap: int
    with_ratio: int
    nearest: int
    second: int

    @classmethod
    def from_run(cls, data_dir: Path | None = None) -> Handover:
        """Read the first two front windows and the counts on the committed files."""
        _, closes, strip = trade.read_sources(data_dir)
        return cls.from_contracts(closes, strip.contracts)

    @classmethod
    def from_contracts(cls, closes: pd.DataFrame, contracts: pd.DataFrame) -> Handover:
        """Read them from the ETF closes and the strip's contracts.

        The counts come from the front windows: on each of the trade's days
        with a finite ratio, how many contracts the file prices that day
        expire before the front does. It refuses unless that is 0 or 1 on every day,
        since the closing note names only those two.
        """
        windows = trade.front_windows(contracts)
        index = contracts.index
        old, new = windows[0], windows[1]
        prices = contracts.to_numpy(dtype=float)
        priced = np.isfinite(prices)
        with np.errstate(invalid="ignore", divide="ignore"):
            finite = np.isfinite(fwdshift(1, prices.T).T / prices)

        def iso(row: int) -> str:
            return str(index[row].date())

        days = set(closes.index.intersection(index))
        earlier = []
        for window in windows:
            for row in window.rows:
                if index[row] in days and finite[row, window.column]:
                    earlier.append(int(priced[row, : window.column].sum()))
        if set(earlier) - {0, 1}:
            raise ValueError("the front is past the second-nearest contract on some day")
        axis = index[(index >= AXIS_FROM) & (index <= AXIS_TO)]
        return cls(
            days=tuple(str(d.date()) for d in axis),
            old=str(contracts.columns[old.column]),
            new=str(contracts.columns[new.column]),
            old_first=iso(old.first),
            old_last=iso(old.last),
            old_rows=len(old.rows),
            old_expiry=iso(old.expiry),
            new_first=iso(new.first),
            new_last=iso(new.last),
            new_rows=len(new.rows),
            overlap=int(priced[new.rows, old.column].sum()),
            with_ratio=len(earlier),
            nearest=earlier.count(0),
            second=earlier.count(1),
        )

    @property
    def overlap_last(self) -> str:
        """The last of the new contract's front rows on which the old is priced."""
        return self.days[self.days.index(self.new_first) + self.overlap - 1]


#: The axis's height and ends, the two contracts' rows above it, and the
#: brace's ends and point between them.
AXIS_Y, AXIS_X0, AXIS_X1 = 1.28, 0.4, 9.6
#: The heights of the closing note's two lines, under the axis's month names.
COUNT_Y = (0.56, 0.24)
OLD_Y, NEW_Y = 3.35, 1.95
BRACE_ENDS, BRACE_TIP = 2.95, 2.72
#: The thick front bars' and the thin priced bar's widths, in points.
FRONT_WIDTH, PRICED_WIDTH = 4.0, 1.6


def day_x(run: Handover, date: str) -> float:
    """A trading day's place on the axis, an affine function of its count from the first."""
    return AXIS_X0 + (AXIS_X1 - AXIS_X0) * run.days.index(date) / (len(run.days) - 1)


def _brace_down(x0: float, x1: float, ends: float, tip: float) -> tuple:
    """A brace from ``x0`` to ``x1`` with its ends at ``ends`` and its point at
    ``tip`` in the middle, shaped like the brace :mod:`chan.gld_gc_whiteboard` draws."""
    middle, centre = (ends + tip) / 2, (x0 + x1) / 2
    return _line(
        [
            (x0, ends),
            (x0 + 0.1, middle),
            (centre - 0.1, middle),
            (centre, tip),
            (centre + 0.1, middle),
            (x1 - 0.1, middle),
            (x1, ends),
        ],
        per_unit=8,
    )


def _handover(run: Handover) -> Scene:
    """Lesson 1: the old contract's front ends 10 rows before its last price."""
    old0, old1 = day_x(run, run.old_first), day_x(run, run.old_last)
    new0, new1 = day_x(run, run.new_first), day_x(run, run.new_last)
    expiry = day_x(run, run.old_expiry)
    steps: list[Stroke | Label] = [
        _stroke("axis", _line([(AXIS_X0, AXIS_Y), (AXIS_X1, AXIS_Y)]), color=MUTED, frames=8),
        Label(_month(run.days[0]), AXIS_X0, AXIS_Y - 0.35, names="axis", color=MUTED, size=11),
        Label(
            _month(run.days[-1]),
            AXIS_X1,
            AXIS_Y - 0.35,
            names="axis",
            color=MUTED,
            size=11,
            ha="right",
        ),
        _stroke(
            "old-priced",
            _line([(AXIS_X0, OLD_Y), (expiry, OLD_Y)], per_unit=4),
            color=MUTED,
            width=PRICED_WIDTH,
            frames=8,
        ),
        Label(
            f"last price {_day(run.old_expiry)}",
            expiry + 0.2,
            OLD_Y,
            names="old-priced",
            color=MUTED,
            size=11,
        ),
        _stroke(
            "old-front",
            _line([(old0, OLD_Y), (old1, OLD_Y)], per_unit=4),
            color=INK,
            width=FRONT_WIDTH,
            frames=8,
        ),
        Label(
            f"{run.old} front, {_day(run.old_first)} to {_day(run.old_last)}: {run.old_rows} rows",
            old0,
            OLD_Y + 0.42,
            names="old-front",
            color=INK,
            size=12,
        ),
        _stroke(
            "new-front",
            _line([(new0, NEW_Y), (new1, NEW_Y)], per_unit=4),
            color=INK,
            width=FRONT_WIDTH,
            frames=8,
        ),
        Label(
            f"{run.new} front, {_day(run.new_first)} to {_day(run.new_last)}: {run.new_rows} rows",
            new0 - 0.25,
            NEW_Y,
            names="new-front",
            color=INK,
            size=12,
            ha="right",
        ),
        Label(
            f"the {_delivery(run.new)} contract",
            new0 - 0.25,
            NEW_Y - 0.33,
            names="new-front",
            color=MUTED,
            size=11,
            ha="right",
        ),
        _stroke(
            "overlap",
            _brace_down(new0, day_x(run, run.overlap_last), BRACE_ENDS, BRACE_TIP),
            color=ACCENT,
            width=1.8,
            frames=5,
        ),
        Label(
            f"{run.old} still priced: {run.overlap} rows",
            new0 - 0.25,
            BRACE_ENDS,
            names="overlap",
            color=ACCENT,
            size=12,
            ha="right",
        ),
        Label(
            "so the front is the second-nearest",
            new0 - 0.25,
            BRACE_ENDS - 0.36,
            names="overlap",
            color=ACCENT,
            size=12,
            ha="right",
        ),
        Label(
            f"of the {run.with_ratio:,} days with a ratio, the front is the nearest contract "
            "the file prices",
            0.3,
            COUNT_Y[0],
            names="overlap",
            color=INK,
            size=11,
        ),
        Label(
            f"on {run.nearest:,} and the second-nearest on {run.second:,}",
            0.3,
            COUNT_Y[1],
            names="overlap",
            color=INK,
            size=11,
        ),
    ]
    return Scene("The front moves on before the last price", "front_handover", tuple(steps))


# --- Lesson 5: USO's log move against the roll return the ratio implies -------


@dataclass(frozen=True)
class Split:
    """What the Lesson 5 sketch reads off the run, from :func:`chan.xle_uso_roll_return.by_view`.

    For each view, the days earning on it, USO's log move over those days,
    ``ln(1 + uso)`` of its compounded return, and the roll return the ratio
    implies, summed over the same days. Both are log quantities.
    """

    contango_days: int
    contango_uso: float
    contango_roll: float
    backwardation_days: int
    backwardation_uso: float
    backwardation_roll: float

    @classmethod
    def from_run(cls, data_dir: Path | None = None) -> Split:
        _, closes, strip = trade.read_sources(data_dir)
        result = trade.arbitrage(closes, trade.front_ratio(strip.contracts))
        views = trade.by_view(closes, result)
        contango, backwardation = views["contango"], views["backwardation"]
        return cls(
            contango_days=contango.days,
            contango_uso=math.log1p(contango.uso),
            contango_roll=contango.roll,
            backwardation_days=backwardation.days,
            backwardation_uso=math.log1p(backwardation.uso),
            backwardation_roll=backwardation.roll,
        )


#: The zero line's height, and board units per unit of log return.
ZERO_Y, PER_LOG = 2.6, 1.7
#: Each bar's half width, and the bars' centres: USO's then the roll return's,
#: contango's group then backwardation's.
HALF = 0.3
CONTANGO_X = (1.2, 2.5)
BACKWARDATION_X = (5.35, 6.5)
#: How far a value's words sit below a bar that hangs down and above one that
#: stands up, and the heights of the closing note's two lines.
VALUE_OFF = (0.32, 0.36)
NOTE_Y = (0.55, 0.2)
#: The brace on the backwardation gap, and where its point reaches.
GAP_X, GAP_TIP = 7.2, 7.42


def bar_y(value: float) -> float:
    """A bar's far end, an affine function of its value."""
    return ZERO_Y + PER_LOG * value


def _bar(gid: str, x: float, value: float, color: str) -> Stroke:
    return _stroke(
        gid, _box(x - HALF, ZERO_Y, x + HALF, bar_y(value)), color=color, width=2.4, frames=6
    )


def _brace_right(x: float, y0: float, y1: float, tip: float) -> tuple:
    """An upright brace at ``x`` from ``y0`` to ``y1``, its point out to ``tip``."""
    middle, centre = (x + tip) / 2, (y0 + y1) / 2
    return _line(
        [
            (x, y0),
            (middle, y0 + 0.08),
            (middle, centre - 0.08),
            (tip, centre),
            (middle, centre + 0.08),
            (middle, y1 - 0.08),
            (x, y1),
        ],
        per_unit=10,
    )


def _roll_vs_uso(split: Split) -> Scene:
    """Lesson 5: close on the contango days, far apart on the backwardation days."""
    c_uso, c_roll = CONTANGO_X
    b_uso, b_roll = BACKWARDATION_X
    c_uso_end, c_roll_end = bar_y(split.contango_uso), bar_y(split.contango_roll)
    b_uso_end, b_roll_end = bar_y(split.backwardation_uso), bar_y(split.backwardation_roll)
    names_up, names_down = ZERO_Y + 0.3, ZERO_Y - 0.3
    steps: list[Stroke | Label] = [
        _stroke("zero", _line([(0.3, ZERO_Y), (9.7, ZERO_Y)], per_unit=3), color=MUTED, frames=8),
        Label(
            f"{split.contango_days:,} days earning on contango",
            0.4,
            ZERO_Y + 0.85,
            names="zero",
            color=INK,
            size=12,
        ),
        _bar("contango-uso", c_uso, split.contango_uso, INK),
        Label("USO", c_uso, names_up, names="contango-uso", color=INK, size=11, ha="center"),
        Label(
            _signed(split.contango_uso, 4),
            c_uso,
            c_uso_end - VALUE_OFF[0],
            names="contango-uso",
            color=INK,
            size=11,
            ha="center",
        ),
        _bar("contango-roll", c_roll, split.contango_roll, ACCENT),
        Label(
            "roll return",
            c_roll,
            names_up,
            names="contango-roll",
            color=ACCENT,
            size=11,
            ha="center",
        ),
        Label(
            _signed(split.contango_roll, 6),
            c_roll,
            c_roll_end - VALUE_OFF[0],
            names="contango-roll",
            color=ACCENT,
            size=11,
            ha="center",
        ),
        Label("close", 3.1, c_roll_end + 0.08, names="contango-roll", color=INK, size=12),
        Label(
            f"{split.backwardation_days:,} days earning on backwardation",
            5.0,
            ZERO_Y - 0.85,
            names="zero",
            color=INK,
            size=12,
        ),
        _bar("backwardation-uso", b_uso, split.backwardation_uso, INK),
        Label("USO", b_uso, names_down, names="backwardation-uso", color=INK, size=11, ha="center"),
        Label(
            _signed(split.backwardation_uso, 4),
            b_uso,
            b_uso_end + VALUE_OFF[1],
            names="backwardation-uso",
            color=INK,
            size=11,
            ha="center",
        ),
        _bar("backwardation-roll", b_roll, split.backwardation_roll, ACCENT),
        Label(
            "roll return",
            b_roll,
            names_down,
            names="backwardation-roll",
            color=ACCENT,
            size=11,
            ha="center",
        ),
        Label(
            _signed(split.backwardation_roll, 6),
            b_roll,
            b_roll_end + VALUE_OFF[1],
            names="backwardation-roll",
            color=ACCENT,
            size=11,
            ha="center",
        ),
        _stroke(
            "level",
            _line([(b_uso + HALF + 0.12, b_uso_end), (GAP_X, b_uso_end)], per_unit=6),
            color=MUTED,
            width=1.4,
            dashed=True,
            frames=4,
        ),
        _stroke("gap", _brace_right(GAP_X, b_roll_end, b_uso_end, GAP_TIP), color=INK, frames=5),
        Label(
            "USO’s move beyond",
            GAP_TIP + 0.22,
            (b_roll_end + b_uso_end) / 2 + 0.17,
            names="gap",
            color=INK,
            size=11,
        ),
        Label(
            "the roll return",
            GAP_TIP + 0.22,
            (b_roll_end + b_uso_end) / 2 - 0.17,
            names="gap",
            color=INK,
            size=11,
        ),
        Label(
            "roll return: 12 · ln(front / back) / 252, each group’s days summed,",
            0.3,
            NOTE_Y[0],
            names="gap",
            color=MUTED,
            size=11,
        ),
        Label(
            "on the ratio that set the view",
            0.3,
            NOTE_Y[1],
            names="gap",
            color=MUTED,
            size=11,
        ),
    ]
    return Scene("USO’s log move against the implied roll return", "roll_vs_uso", tuple(steps))


# --- Drawing ------------------------------------------------------------------

#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("front_handover", "roll_vs_uso")
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


def scenes(handover: Handover | None = None, split: Split | None = None) -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them, Lesson 1's then Lesson 5's."""
    return (
        _handover(handover if handover is not None else Handover.from_run()),
        _roll_vs_uso(split if split is not None else Split.from_run()),
    )


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


def make_xle_uso_roll_return_whiteboards(
    out_dir: Path | None = None, handover: Handover | None = None, split: Split | None = None
) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes(handover, split)]


def main() -> None:
    for path in make_xle_uso_roll_return_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
