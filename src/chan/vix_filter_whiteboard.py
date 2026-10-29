"""Whiteboard sketches for the VIX filter post, one in Lesson 3 and one in Lesson 4.

``blog/vix-filter-lessons.md`` makes two claims that a sentence has to build
in the reader's head: one US holiday is read four different ways on FSTX's
calendar, and buy on gap's kept days earn their sum on a handful of traded
days, one above all. This module draws the two as scenes, and the post places
each right after the paragraph it draws.

1. One US holiday, four readings: three columns, Wednesday 2008-11-26,
   Thursday 2008-11-27 and Friday 2008-11-28, with VIX's close on each, none
   on the Thursday, and a check for each day FSTX traded. Under them, one row
   for each of the four of the post's six readings that read the previous
   day: the join, the latest close, filled forward and a row back. The two
   that read the same day's close are left out, since Lesson 3 rules them out
   before any figure. In each row an arrow runs from each trade day the
   reading holds back to the column whose close that day reads, and a word
   says whether the day is kept or dropped. The join's row says the Thursday
   is not on its calendar at all. The Friday's own close is grey, with a note
   naming the next trade day, which reads it, since no day drawn does. It
   sits after the paragraph opening "The join lands 2.6 percent and 0.16."
2. What buy on gap's kept days earned: a row of one tick per kept day in date
   order, the ticks of the days that held nothing redrawn grey and a dot over
   each day that held a position, then those days as bars on a zero line, in
   date order and to one scale, gains above it and losses below. Each bar is
   an outline, so a return near zero still shows as a short dash on the line.
   The tallest is in brass, labelled with its date and return, and then
   struck out, and the last two lines give its share of the sum and what the
   other kept days give without it. It sits after the paragraph opening "A
   kept day is not a day traded."

Every figure either sketch prints, and every bar's height, is read from the
committed files through :func:`chan.vix_filter.read_sources`. The kept days
come from :func:`chan.vix_filter.vix_filters` into :class:`KeptDays`. The
holiday's reads come into :class:`HolidayWeek` from the functions the run's
readings are built on, :func:`~chan.vix_filter.common_days`,
:func:`~chan.vix_filter.latest_close_before` and
:func:`~chan.vix_filter.qualifies`, because the run keeps only each reading's
totals and not which close each day read. Each scene refuses figures that would make its words
false rather than drawing them. Two parts of the layout are schematic.

1. The first sketch's columns stand evenly apart, and its arrows show only
   which column's close each day reads.
2. The second sketch's ticks stand evenly apart in date order, with no date
   axis, and its bars stand evenly apart rather than at their dates. Their
   heights stand to one scale.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look, frame rate and colours.
The post's chart has not moved to :mod:`chan.palette`, so both sketches draw
in the shared inks of :mod:`chan.regime_figure` and the post keeps one set of
colours. Each sketch carries more than a reader takes in at that post's pace,
so both are in :data:`PACED`, and :func:`sketch_timeline` holds each of their
labels longer and their finished drawings for twelve seconds, as
:mod:`chan.equity_seasonals_whiteboard` does for its slow sketches. Each GIF
is named :data:`GIF_PREFIX` plus the scene's slug. The post's chart,
``vix_filter.png``, does not start with that prefix, so nothing that looks
for the sketches by prefix finds the chart.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw both with::

    uv run python -m chan.vix_filter_whiteboard
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from chan import vix_filter as vf
from chan.matlab_helpers import backshift
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    Frame,
    Label,
    Scene,
    Stroke,
    _arrow,
    _box,
    _check,
    _line,
    _stroke,
    render,
    timeline,
)

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "vix_filter_sketch_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``vix_filter_sketch_one_holiday.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


def six(value: float) -> str:
    """A figure at six decimals with a typographic minus, as the post prints it."""
    return f"{value:.6f}".replace("-", "−")


# --- Lesson 3: one US holiday, four readings ----------------------------------

#: The three days the sketch draws: the day before the holiday, the holiday,
#: and the day after.
WEEK = (pd.Timestamp("2008-11-26"), pd.Timestamp("2008-11-27"), pd.Timestamp("2008-11-28"))
#: The four of the post's six readings that read the previous day, in its
#: order, each as its row's label. The two same-day readings look ahead.
READINGS = ("Join", "Latest close", "Filled forward", "Row back")


@dataclass(frozen=True)
class HolidayRead:
    """Which close one trade day reads under one reading, and whether it is kept.

    ``source`` is the day whose close is read, and ``close`` that close, NaN
    where that day has none. ``source`` and ``kept`` are ``None`` when the
    reading's calendar holds no such trade day at all, which is the join on a
    US holiday.
    """

    reading: str
    day: pd.Timestamp
    source: pd.Timestamp | None
    close: float
    kept: bool | None


@dataclass(frozen=True)
class HolidayWeek:
    """What the holiday sketch prints: three days, VIX's close on each, and each reading.

    ``closes`` holds NaN where VIX has no close, ``traded`` whether FSTX
    traded that day, ``reads`` one :class:`HolidayRead` for each reading and
    each of the last two days, and ``next_day`` the FSTX day after the last.
    """

    days: tuple[pd.Timestamp, ...]
    closes: tuple[float, ...]
    traded: tuple[bool, ...]
    reads: tuple[HolidayRead, ...]
    next_day: pd.Timestamp

    def read(self, reading: str, day: pd.Timestamp) -> HolidayRead:
        return next(r for r in self.reads if r.reading == reading and r.day == day)

    @classmethod
    def from_sources(
        cls, sources: vf.Sources, days: tuple[pd.Timestamp, ...] = WEEK
    ) -> HolidayWeek:
        """Each reading's close and verdict on ``days``, from :mod:`chan.vix_filter`'s own steps.

        The join keeps a day when :func:`chan.vix_filter.qualifies` passes on
        the calendar :func:`chan.vix_filter.common_days` gives. The latest
        close reads :func:`chan.vix_filter.latest_close_before`. Filled
        forward and a row back run :func:`chan.vix_filter.qualifies` on VIX
        placed on FSTX's own calendar, filled forward or left NaN.
        """
        vix, fstx_days = sources.vix, sources.fstx.index
        joined = vf.common_days(fstx_days, vix)
        filled_from = pd.Series(vix.index, index=vix.index).reindex(fstx_days, method="ffill")
        latest = vf.latest_close_before(fstx_days, vix)
        latest_rows = vix.index.searchsorted(fstx_days, side="left") - 1
        with np.errstate(invalid="ignore"):
            latest_kept = latest > vf.THRESHOLD
        lookups = {
            "Join": _previous(joined, vix.reindex(joined), list(joined)),
            "Latest close": {
                pd.Timestamp(day): (
                    pd.Timestamp(vix.index[row]) if row >= 0 else None,
                    float(close),
                    bool(kept),
                )
                for day, row, close, kept in zip(
                    fstx_days, latest_rows, latest, latest_kept, strict=True
                )
            },
            "Filled forward": _previous(
                fstx_days,
                vix.reindex(fstx_days, method="ffill"),
                [None if pd.isna(d) else pd.Timestamp(d) for d in filled_from],
            ),
            "Row back": _previous(fstx_days, vix.reindex(fstx_days), list(fstx_days)),
        }
        reads = [
            HolidayRead(reading, day, *lookups[reading].get(day, (None, math.nan, None)))
            for reading in READINGS
            for day in days[1:]
        ]
        return cls(
            days=tuple(days),
            closes=tuple(float(vix.get(day, math.nan)) for day in days),
            traded=tuple(bool(day in fstx_days) for day in days),
            reads=tuple(reads),
            next_day=pd.Timestamp(fstx_days[fstx_days > days[-1]][0]),
        )


def _previous(
    calendar: pd.DatetimeIndex, closes: pd.Series, sources: list
) -> dict[pd.Timestamp, tuple[pd.Timestamp | None, float, bool]]:
    """One row back on ``calendar``: the day each day reads, its close, and whether it is kept.

    ``closes`` is VIX placed on ``calendar``, and ``sources`` the day each of
    its values came from. Whether a day is kept is
    :func:`chan.vix_filter.qualifies`, the run's own test.
    """
    values = closes.to_numpy(dtype=float)
    kept = vf.qualifies(values)
    read = backshift(1, values)
    before = [None, *sources[:-1]]
    return {
        pd.Timestamp(day): (before[k], float(read[k]), bool(kept[k]))
        for k, day in enumerate(calendar)
    }


#: Where each day's column stands across, and where the row names start.
COLUMN_XS = (3.2, 5.2, 7.2)
NAMES_X = 0.3
#: Where the rule under the day headings ends across.
RULE_END = 9.7
#: The heights of the day headings, the rule under them, the VIX row and the
#: FSTX row.
DAYS_Y, TOP_RULE_Y, VIX_Y, FSTX_Y = 3.92, 3.61, 3.29, 2.85
#: The height of each reading's row, and how far above and below it the
#: Thursday's and the Friday's arrows run.
ROW_YS, LANE = (2.19, 1.58, 0.97, 0.36), 0.15
#: How far right of an arrow's tail its kept or dropped word starts.
VERDICT_DX = 0.4
#: How far right of the last column the note on its close starts.
NOTE_DX = 0.55


def _close(value: float) -> str:
    return f"{value:.2f}"


def _weekday(day: pd.Timestamp) -> str:
    """A day as its weekday and month-day, such as ``Thu 11-27``."""
    return day.strftime("%a %m-%d")


def _one_holiday(week: HolidayWeek) -> Scene:
    """Lesson 3: one US holiday on FSTX's calendar, read four ways.

    The sketch draws a middle day FSTX traded and VIX did not, so any other
    week is refused, and so is a read of a day the sketch does not draw,
    since its arrow would have nowhere to point.
    """
    if not (math.isnan(week.closes[1]) and all(week.traded)):
        raise ValueError("the holiday sketch draws a middle day FSTX traded and VIX did not")
    columns = dict(zip(week.days, COLUMN_XS, strict=True))
    steps: list[Stroke | Label] = [
        _stroke(
            "top-rule",
            _line([(NAMES_X, TOP_RULE_Y), (RULE_END, TOP_RULE_Y)], per_unit=4),
            color=MUTED,
            width=1.5,
            frames=4,
        )
    ]
    for day, x in columns.items():
        steps.append(Label(_weekday(day), x, DAYS_Y, names="top-rule", size=12, ha="center"))
    steps.append(Label("VIX closed", NAMES_X, VIX_Y, names="top-rule", size=12))
    last = len(week.days) - 1
    for k, x in enumerate(COLUMN_XS):
        close = week.closes[k]
        if math.isnan(close):
            steps.append(
                Label("none: US holiday", x, VIX_Y, names="top-rule", size=12, ha="center")
            )
            continue
        # No day drawn reads the last day's close, so it is grey.
        color = MUTED if k == last else INK
        steps.append(
            Label(_close(close), x, VIX_Y, names="top-rule", color=color, size=12, ha="center")
        )
    steps.append(
        Label(
            f"read by {week.next_day.strftime('%m-%d')}",
            COLUMN_XS[-1] + NOTE_DX,
            VIX_Y,
            names="top-rule",
            color=MUTED,
            size=11,
        )
    )
    for day, x in columns.items():
        steps.append(_stroke(f"traded-{day.date()}", _check(x - 0.16, FSTX_Y - 0.08), frames=3))
    steps.append(
        Label("FSTX traded", NAMES_X, FSTX_Y, names=f"traded-{week.days[0].date()}", size=12)
    )
    for reading, y in zip(READINGS, ROW_YS, strict=True):
        steps.append(Label(reading, NAMES_X, y, names="top-rule"))
        for day, lane in zip(week.days[1:], (y + LANE, y - LANE), strict=True):
            read = week.read(reading, day)
            x = columns[day]
            if read.source is None:
                steps.append(
                    Label(
                        "not on the joined calendar",
                        x,
                        lane,
                        names="top-rule",
                        color=MUTED,
                        size=11,
                        ha="center",
                    )
                )
                continue
            if read.source not in columns or read.source >= day:
                raise ValueError(f"{reading} on {day.date()} reads {read.source.date()}, not drawn")
            gid = f"{reading}-{day.date()}"
            steps.append(_stroke(gid, _arrow(x, lane, columns[read.source], lane), frames=5))
            word, color = ("kept", GOOD) if read.kept else ("dropped", LOST)
            steps.append(Label(word, x + VERDICT_DX, lane, names=gid, color=color, size=11))
    return Scene("One US holiday, four readings", "one_holiday", tuple(steps))


# --- Lesson 4: what buy on gap's kept days earned ------------------------------


@dataclass(frozen=True)
class KeptDays:
    """What the kept-days sketch prints, for one rule's kept days.

    - ``kept``: how many days the filter kept.
    - ``places``, ``held_days`` and ``held``: the kept days the rule held a
      position on, in date order, as each one's place among the kept days,
      its date and its return.
    - ``total``: the kept days' returns summed, every day without a position
      adding 0.
    - ``rest_return`` and ``rest_sharpe``: 252 times the mean and the Sharpe
      ratio over the kept days without the largest held day, from
      :func:`chan.vix_filter.reading`.
    """

    kept: int
    places: tuple[int, ...]
    held_days: tuple[pd.Timestamp, ...]
    held: tuple[float, ...]
    total: float
    rest_return: float
    rest_sharpe: float

    @property
    def unheld(self) -> int:
        return self.kept - len(self.held)

    @property
    def gained(self) -> int:
        return sum(value > 0 for value in self.held)

    @property
    def lost(self) -> int:
        return sum(value < 0 for value in self.held)

    @property
    def top(self) -> int:
        """Where the largest held day stands among the held days."""
        return int(np.argmax(self.held))

    @property
    def share(self) -> float:
        """The largest held day's return as a share of :attr:`total`."""
        return self.held[self.top] / self.total

    @classmethod
    def from_filtered(cls, filtered: vf.Filtered) -> KeptDays:
        """Read one rule's kept days from :class:`chan.vix_filter.Filtered`.

        The sketch says a kept day with no position earns 0, so a rule whose
        such days earn anything is refused rather than drawn.
        """
        held = filtered.held[filtered.qualifies]
        returns = filtered.filtered
        if np.any(returns[~held] != 0):
            raise ValueError("a kept day with no position earned something")
        best = int(np.argmax(returns))
        rest = vf.reading(np.delete(returns, best), np.ones(len(returns) - 1, dtype=bool))
        return cls(
            kept=filtered.kept,
            places=tuple(int(k) for k in np.flatnonzero(held)),
            held_days=tuple(pd.Timestamp(d) for d in filtered.kept_days[held]),
            held=tuple(float(v) for v in returns[held]),
            total=float(returns.sum()),
            rest_return=rest.average_annual_return,
            rest_sharpe=rest.sharpe,
        )


#: The row of ticks: where it runs across, its foot and how tall each tick is.
TICKS_X, TICKS_Y, TICK_HIGH = (0.4, 9.6), 3.5, 0.22
#: How far above the row's ticks the held days' dots stand, and their size in points.
HELD_DOT_DY, HELD_DOT_SIZE = 0.12, 4.0
#: The height of the three labels under the row, and where the second and
#: third start.
TICK_WORDS_Y, UNHELD_X, HELD_X = 3.18, 2.5, 6.95
#: The zero line: its height, and where it runs across.
ZERO_Y, ZERO_XS = 1.38, (0.75, 6.65)
#: Where the first bar stands, how far apart the bars stand, and how tall the
#: largest is drawn. Every other bar stands at the same scale.
FIRST_BAR_X, BAR_STEP, TALLEST = 0.98, 0.29, 1.32
#: Half a bar's width, and the width of its outline in points. A bar is an
#: outline rather than one thick line, so a bar for a return near zero still
#: draws as a short dash on the zero line, and no round end stands past its
#: value.
BAR_HALF, BAR_LINE = 0.035, 3.0
#: Where the words on the right start across, and their heights.
RIGHT_X, GAINED_Y, LOST_Y = 6.95, 1.95, 1.12
#: Where the top bar's words start right of it, and how high they stand.
TOP_WORDS_DX, TOP_WORDS_Y = 0.28, 2.66
#: The strike across the top bar: how far it runs either side of the bar, and its ends' heights.
STRIKE_DX, STRIKE_YS = 0.22, (1.72, 2.26)
#: The heights of the two closing lines.
SHARE_Y, REST_Y = 0.72, 0.32


def tick_xs(kept: int) -> np.ndarray:
    """Where each kept day's tick stands across, in date order."""
    return np.linspace(*TICKS_X, kept)


def bar_x(k: int) -> float:
    """Where the ``k``-th held day's bar stands across."""
    return FIRST_BAR_X + k * BAR_STEP


def bar_scale(days: KeptDays) -> float:
    """Board units per unit of return, so the largest bar either way is :data:`TALLEST`."""
    return TALLEST / max(abs(v) for v in days.held)


def _comb(xs: np.ndarray, y: float, high: float) -> tuple:
    """One tick up from ``y`` at each of ``xs``, joined along the foot."""
    points = [(x, level) for x in xs for level in (y, y + high, y)]
    return np.array([p[0] for p in points]), np.array([p[1] for p in points])


def _kept_days(days: KeptDays) -> Scene:
    """Lesson 4: the kept days, the few held, and the one that earns most of the sum.

    The struck-out bar has to have gained, since the words give its share of
    the sum, so a rule whose largest held day lost is refused.
    """
    if not days.held or days.held[days.top] <= 0:
        raise ValueError("the kept-days sketch draws at least one held day that gained")
    xs = tick_xs(days.kept)
    unheld = np.ones(days.kept, dtype=bool)
    unheld[list(days.places)] = False
    steps: list[Stroke | Label] = [
        _stroke("kept", _comb(xs, TICKS_Y, TICK_HIGH), width=1.0, frames=8),
        Label(f"{days.kept} kept days", TICKS_X[0], TICK_WORDS_Y, names="kept", size=12),
        _stroke("unheld", _comb(xs[unheld], TICKS_Y, TICK_HIGH), color=MUTED, width=1.2, frames=6),
        Label(
            f"{days.unheld} held nothing: each earns 0",
            UNHELD_X,
            TICK_WORDS_Y,
            names="unheld",
            color=MUTED,
            size=12,
        ),
        Stroke(
            "held",
            xs[list(days.places)],
            np.full(len(days.places), TICKS_Y + TICK_HIGH + HELD_DOT_DY),
            frames=4,
            dots=HELD_DOT_SIZE,
        ),
        Label(f"{len(days.held)} held a position", HELD_X, TICK_WORDS_Y, names="held", size=12),
        _stroke(
            "zero",
            _line([(ZERO_XS[0], ZERO_Y), (ZERO_XS[1], ZERO_Y)], per_unit=4),
            color=MUTED,
            width=1.5,
            frames=4,
        ),
        Label("0", ZERO_XS[0] - 0.2, ZERO_Y, names="zero", color=MUTED, size=12, ha="right"),
    ]
    scale = bar_scale(days)
    for k, (day, value) in enumerate(zip(days.held_days, days.held, strict=True)):
        color = ACCENT if k == days.top else GOOD if value > 0 else LOST
        x, end = bar_x(k), ZERO_Y + scale * value
        steps.append(
            _stroke(
                f"bar-{day.date()}",
                _box(x - BAR_HALF, min(ZERO_Y, end), x + BAR_HALF, max(ZERO_Y, end)),
                color=color,
                width=BAR_LINE,
                frames=1,
            )
        )
    pairs = list(zip(days.held_days, days.held, strict=True))
    first_gain = next(d for d, v in pairs if v > 0)
    first_loss = next((d for d, v in pairs if v < 0), days.held_days[-1])
    top_day, top = days.held_days[days.top], days.held[days.top]
    top_x = bar_x(days.top)
    steps += [
        Label(
            f"{days.gained} gained, above 0",
            RIGHT_X,
            GAINED_Y,
            names=f"bar-{first_gain.date()}",
            color=GOOD,
            size=12,
        ),
        Label(
            f"{days.lost} lost, below 0",
            RIGHT_X,
            LOST_Y,
            names=f"bar-{first_loss.date()}",
            color=LOST,
            size=12,
        ),
        Label(
            f"{top_day.date()}: {six(top)}",
            top_x + TOP_WORDS_DX,
            TOP_WORDS_Y,
            names=f"bar-{top_day.date()}",
            color=ACCENT,
            size=12,
        ),
        Label(
            f"that day is {six(days.share)} of the {six(days.total)} the kept days sum to",
            TICKS_X[0],
            SHARE_Y,
            names=f"bar-{top_day.date()}",
            color=ACCENT,
            size=12,
        ),
        _stroke(
            "strike",
            _line(
                [(top_x - STRIKE_DX, STRIKE_YS[0]), (top_x + STRIKE_DX, STRIKE_YS[1])],
                per_unit=10,
            ),
            frames=4,
        ),
        Label(
            f"the other {days.kept - 1}: 252 × mean {six(days.rest_return)}, "
            f"Sharpe {six(days.rest_sharpe)}",
            TICKS_X[0],
            REST_Y,
            names="strike",
            size=12,
        ),
    ]
    return Scene("What buy on gap’s kept days earned", "kept_days", tuple(steps))


# --- Drawing ------------------------------------------------------------------

#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("one_holiday", "kept_days")
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


def figures(data_dir: Path | None = None) -> tuple[HolidayWeek, KeptDays]:
    """Both sketches' figures from one read of the committed vintages, through the run's path."""
    sources = vf.read_sources(data_dir)
    result = vf.vix_filters(sources)
    return HolidayWeek.from_sources(sources), KeptDays.from_filtered(result.buy_on_gap)


def scenes(week: HolidayWeek | None = None, kept: KeptDays | None = None) -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them, the holiday's then the kept days'.

    Either set of figures left out is read by :func:`figures` from the committed files.
    """
    if week is None or kept is None:
        found_week, found_kept = figures()
        week = week if week is not None else found_week
        kept = kept if kept is not None else found_kept
    return (_one_holiday(week), _kept_days(kept))


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


def make_vix_filter_whiteboards(out_dir: Path | None = None) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes()]


def main() -> None:
    for path in make_vix_filter_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
