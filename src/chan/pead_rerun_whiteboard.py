"""Whiteboard sketches for the post-earnings drift rerun post, one each for Lessons 1 and 2.

``blog/pead-edgar-rerun-lessons.md`` makes two claims that a sentence has to
build in the reader's head. The 56 stocks outside U fall into three groups,
depending on which of two checks each passes. And a time read 4 hours late
hurts a morning filer, leaves an evening filer alone and gives a filer
during the session a wrong flag. This module draws the two as scenes, and the
post places each right after the list it draws.

1. Where the 56 go: a box for ALL's 497 stocks holding two overlapping
   circles, CAL's 488 whose filer passed its check and PX's 446 whose price
   series passed its check, which overlap in U's 441. The 47 in CAL alone are
   outlined and labelled in brass, the ink of the brass line that draws the
   same 47 in the post's chart, and split into the 4 reused tickers and the
   43 without prices for the whole window. The 5 in PX alone and the 4
   outside both circles sit under one brace as the 9 that fail the filer
   check, all in red, the ink of the chart's red line for the same 9. A
   closing line adds 47, 5 and 4 to 56. It sits in Lesson 1,
   after the list whose last item opens "**Forty-three lack the prices to
   check.**". This sketch is not drawn to scale. The circles show which
   checks a group passes, not how many stocks it holds, since circles sized
   to 488 and 446 would leave the 5 and the 47 too thin to label. Every count
   it prints comes from :class:`Universes`, which
   :meth:`Universes.from_sources` reads from the committed ticker table
   through :func:`chan.pead_rerun.read_committed`.
2. Four hours late: a clock from 6 a.m. to 10 p.m. Eastern with the session
   from 9:30 a.m. to 4:00 p.m. tinted red, because R1 flags nothing for a
   filing accepted in it. Three rows each move a span of acceptance times 4
   hours later, the shift a time read late takes under daylight saving time.
   The first moves the 1,460 filings accepted before the open, from the
   earliest at 06:00:43, into the session. The second moves Apple's releases
   from about 4:30 p.m. to about 8:30 p.m., both after the close. The third
   moves noon to the close, inside the session, to past the close, where R1
   flags the next day, whose gap opens after the news is out. A late copy
   is red where it changes R1's flag and green where it keeps it. It sits in
   Lesson 2, after the list whose last item opens "**A filer that files
   during the session gains a wrong flag.**". It is drawn to one scale of the clock.
   The earliest time, the two counts and Apple's times come from
   :class:`FilingTimes`, which :meth:`FilingTimes.from_index` reads from the
   committed index of filings. The 4 hours, and the 5 a winter time takes,
   are what the Internet Archive's copies of the submissions file saved on
   2026-10-07 show, and a check of 248 filings made while planning the rerun
   found shifts of 4 or 5 hours. The repository does not hold that sample
   or those copies, so :data:`LATE_HOURS` and
   :data:`WINTER_HOURS` are constants here rather than figures read from a
   file. Noon is the close less those 4 hours. Nothing counts how many of
   the 1,460 come from filers whose time reads late, so the sketch draws
   none, and it prints no count for the span from noon on, which nothing
   pins either.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look, frame rate and colours.
This post's chart draws in :mod:`chan.regime_figure`'s shared inks, so the
sketches do too. Both are in :data:`PACED`, and :func:`sketch_timeline`
holds each of their labels and tints longer and their finished drawings for
twelve seconds, as :mod:`chan.equity_seasonals_whiteboard` does for its slow
sketches. Each GIF is named :data:`GIF_PREFIX` plus the scene's slug. The
post's chart, ``pead_edgar_rerun.png``, and the drift post's sketches, which
start ``pead_sketch_``, do not start with that prefix, so nothing that looks
for these sketches by prefix finds them.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Both read only committed files, and the
second also draws the two constants from the uncommitted copies. Redraw both
with::

    uv run python -m chan.pead_rerun_whiteboard
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import time
from pathlib import Path

import numpy as np

from chan import pead_rerun
from chan.earnings_filings import Release
from chan.paths import FIGURES_DIR
from chan.pead_rerun import SESSION_CLOSE, SESSION_OPEN
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    REJECT_TINT,
    Fill,
    Frame,
    Label,
    Scene,
    Stroke,
    _arrow,
    _box,
    _dot,
    _line,
    _span,
    _stroke,
    render,
    timeline,
)

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "pead_rerun_sketch_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``pead_rerun_sketch_four_hours_late.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


#: How wide the edge round a tint is drawn, as the equity seasonals module's.
TINT_EDGE = 1.2


# --- Lesson 1: where the 56 go ---------------------------------------------------


@dataclass(frozen=True)
class Universes:
    """The four universes' sizes, and how the stocks outside U split.

    ``cal_only`` passes the filer check and not the series check, ``px_only``
    the series check and not the filer check, and ``neither`` passes neither.
    ``reused`` and ``unpriced`` split ``cal_only`` by why its series failed:
    a series holding another company's returns, or one lacking prices for the
    whole window or never proposed.
    """

    all: int
    cal: int
    px: int
    u: int
    cal_only: int
    px_only: int
    neither: int
    reused: int
    unpriced: int

    @property
    def outside(self) -> int:
        """The stocks outside U."""
        return self.all - self.u

    @property
    def no_filer(self) -> int:
        """The stocks that fail the filer check, PX's alone and those outside both."""
        return self.px_only + self.neither

    @classmethod
    def from_sources(cls, sources: pead_rerun.Sources) -> Universes:
        """Count each universe and region from the ticker table the runs read."""
        rows = {row.ticker: row for row in sources.table}
        every, cal, px, u = (set(sources.universe(n)) for n in pead_rerun.UNIVERSES)
        cal_only = cal - px
        return cls(
            all=len(every),
            cal=len(cal),
            px=len(px),
            u=len(u),
            cal_only=len(cal_only),
            px_only=len(px - cal),
            neither=len(every - cal - px),
            reused=sum(rows[s].archive_check == "returns" for s in cal_only),
            unpriced=sum(rows[s].archive_check in ("missing", "none") for s in cal_only),
        )


#: The box ALL's stocks sit in, and the two circles' centres and radius.
BOX = (0.3, 0.65, 4.55, 3.85)
CAL_CENTRE, PX_CENTRE, RADIUS = (1.85, 2.25), (2.85, 2.25), 1.05
#: Where the text beside the box starts, and the brace's ends and height.
TEXT_X = 4.8
BRACE = (4.8, 9.55, 2.35)


def _circle(centre: tuple[float, float], start: float = 0.0) -> tuple:
    """A circle drawn from the angle ``start``, counterclockwise."""
    t = start + np.linspace(0.0, 2 * np.pi, 73)
    return centre[0] + RADIUS * np.cos(t), centre[1] + RADIUS * np.sin(t)


def _crescent() -> tuple:
    """The outline of the part of CAL's circle that lies outside PX's.

    The two circles cross where their centres' midline meets them. The outline
    runs CAL's arc from the upper crossing round the left to the lower, then
    PX's arc back up through the overlap's left edge.
    """
    half = (PX_CENTRE[0] - CAL_CENTRE[0]) / 2
    reach = float(np.arccos(half / RADIUS))
    outer = np.linspace(reach, 2 * np.pi - reach, 60)
    inner = np.linspace(np.pi + reach, np.pi - reach, 24)
    x = np.concatenate(
        [CAL_CENTRE[0] + RADIUS * np.cos(outer), PX_CENTRE[0] + RADIUS * np.cos(inner)]
    )
    y = np.concatenate(
        [CAL_CENTRE[1] + RADIUS * np.sin(outer), PX_CENTRE[1] + RADIUS * np.sin(inner)]
    )
    return x, y


def _brace(x0: float, x1: float, y: float) -> tuple:
    """A brace from ``x0`` to ``x1`` at height ``y``, its ends down and its point up."""
    mid, rise = (x0 + x1) / 2, 0.12
    return _line(
        [
            (x0, y - rise),
            (x0 + 0.12, y),
            (mid - 0.12, y),
            (mid, y + rise),
            (mid + 0.12, y),
            (x1 - 0.12, y),
            (x1, y - rise),
        ],
        per_unit=4,
    )


def _where_the_56_go(f: Universes) -> Scene:
    """Lesson 1: which check each of the stocks outside U fails."""
    if (
        f.u + f.cal_only != f.cal
        or f.u + f.px_only != f.px
        or f.cal_only + f.px_only + f.neither != f.outside
        or f.reused + f.unpriced != f.cal_only
        or min(f.cal_only, f.px_only, f.neither) <= 0
    ):
        raise ValueError(
            f"the sketch draws U inside CAL and PX, and CAL alone, PX alone and neither as the "
            f"stocks outside U, and these counts disagree: {f}"
        )
    x0, y0, x1, y1 = BOX
    lens = (CAL_CENTRE[0] + PX_CENTRE[0]) / 2
    cal_alone = CAL_CENTRE[0] - RADIUS / 2 - 0.05
    px_alone = PX_CENTRE[0] + RADIUS / 2 + 0.05
    b0, b1, by = BRACE
    steps: list[Stroke | Label] = [
        _stroke("box", _box(x0, y0, x1, y1), color=MUTED, frames=8),
        Label(f"ALL {f.all}", x0 + 0.22, y0 + 0.33, names="box", color=MUTED, size=11),
        _stroke("cal", _circle(CAL_CENTRE, np.pi / 2), color=INK, frames=8),
        Label(f"CAL {f.cal}", x0 + 0.22, y1 - 0.3, names="cal", size=11),
        _stroke("px", _circle(PX_CENTRE, np.pi / 2), color=INK, frames=8),
        Label(f"PX {f.px}", x1 - 0.22, y1 - 0.3, names="px", size=11, ha="right"),
        Label(f"U {f.u}", lens, CAL_CENTRE[1], names="px", size=11, ha="center"),
        _stroke("cal-only", _crescent(), color=ACCENT, width=3.0, frames=8),
        Label(
            f"{f.cal_only}",
            cal_alone,
            CAL_CENTRE[1],
            names="cal-only",
            color=ACCENT,
            size=13,
            ha="center",
        ),
        Label(
            f"{f.cal_only}: the filer passes, the series does not:\n"
            f"{f.reused} reused tickers hold another company’s series\n"
            f"and {f.unpriced} lack prices for the whole window",
            TEXT_X,
            3.45,
            names="cal-only",
            color=ACCENT,
            size=10,
        ),
        # The 9 that fail the filer check are red, as the chart's line for them is.
        Label(f"{f.px_only}", px_alone, PX_CENTRE[1], names="px", color=LOST, size=13, ha="center"),
        Label(f"{f.neither}", x1 - 0.35, y0 + 0.42, names="box", color=LOST, size=13, ha="center"),
        Label(
            f"{f.px_only}: the series passes,\nthe filer does not",
            TEXT_X,
            1.77,
            names="px",
            color=LOST,
            size=10,
        ),
        Label(f"{f.neither}: neither passes", 7.6, 1.92, names="box", color=LOST, size=10),
        _stroke("brace", _brace(b0, b1, by), color=LOST, frames=6),
        Label(
            f"the {f.no_filer} that fail the filer check",
            (b0 + b1) / 2,
            by + 0.42,
            names="brace",
            color=LOST,
            size=10,
            ha="center",
        ),
        Label(
            f"{f.cal_only} + {f.px_only} + {f.neither} = {f.outside} outside U",
            TEXT_X,
            0.95,
            names="brace",
            size=11,
        ),
    ]
    return Scene(f"Where the {f.outside} go", "where_the_56_go", tuple(steps))


# --- Lesson 2: four hours late ---------------------------------------------------

#: How many hours late a late time reads under daylight saving time, and in
#: winter. Both are what the Internet Archive's copies of 2026-10-07 show,
#: which the repository does not hold, so nothing here pins them.
LATE_HOURS, WINTER_HOURS = 4, 5


def _hours(clock: time) -> float:
    """A time of day as hours after midnight."""
    return clock.hour + clock.minute / 60 + clock.second / 3600


def clock_text(hours: float, minutes: bool = True) -> str:
    """Hours after midnight as the post writes a time, such as ``4:30 p.m.``.

    With ``minutes`` false a time on the hour drops them, such as ``6 a.m.``.
    """
    whole = round(hours * 60)
    hour, minute = divmod(whole, 60)
    noon = "a.m." if hour < 12 else "p.m."
    shown = hour % 12 or 12
    if minute == 0 and not minutes:
        return f"{shown} {noon}"
    return f"{shown}:{minute:02d} {noon}"


@dataclass(frozen=True)
class FilingTimes:
    """When the index's filings were accepted, Eastern time.

    ``earliest`` is the earliest time of day any filing was accepted, as
    ``HH:MM:SS``. ``before_open`` counts those accepted before 9:30 a.m. and
    ``in_session`` those from then to before 4:00 p.m., on any day.
    ``apple`` is each of Apple's acceptance times, in the index's order.
    """

    earliest: str
    before_open: int
    in_session: int
    apple: tuple[str, ...]

    @property
    def earliest_hours(self) -> float:
        return _hours(time.fromisoformat(self.earliest))

    @property
    def apple_hours(self) -> float:
        """Apple's typical time of day, the mean of its times to the nearest five minutes."""
        mean = np.mean([_hours(time.fromisoformat(stamp[11:])) for stamp in self.apple])
        return round(float(mean) * 12) / 12

    @classmethod
    def from_index(cls, index: Sequence[Release]) -> FilingTimes:
        times = sorted(release.accepted[11:] for release in index)
        opens, closes = SESSION_OPEN.isoformat(), SESSION_CLOSE.isoformat()
        return cls(
            earliest=times[0],
            before_open=sum(t < opens for t in times),
            in_session=sum(opens <= t < closes for t in times),
            apple=tuple(release.accepted for release in index if release.ticker == "AAPL"),
        )


#: The clock's hours and where they land across the board, and the heights of
#: the clock, the session tint's top and the three rows.
HOURS, HOUR_X = (6.0, 22.0), (0.4, 9.6)
CLOCK_Y, TINT_TOP = 0.5, 3.56
ROWS_Y = (3.15, 2.95, 1.51)
#: How far above its row each shift's arrow runs, and how far short of the
#: next mark an arrow between two dots stops.
ARROW_RISE, DOT_GAP = 0.27, 0.17
#: Where the labels right of the session start, a little past its edge.
RIGHT_X = 6.36


def hour_x(hours: float | np.ndarray) -> float | np.ndarray:
    """The board across of a time of day, in hours after midnight."""
    (h0, h1), (x0, x1) = HOURS, HOUR_X
    return x0 + (np.asarray(hours) - h0) * (x1 - x0) / (h1 - h0)


def _at(hours: float) -> float:
    return float(hour_x(hours))


def _four_hours_late(f: FilingTimes) -> Scene:
    """Lesson 2: a late time loses a morning filing, keeps an evening one, moves a session one."""
    opens, closes = _hours(SESSION_OPEN), _hours(SESSION_CLOSE)
    noon = closes - LATE_HOURS
    early, apple = f.earliest_hours, f.apple_hours
    # The open shifted by the late hours staying before the close is the same
    # claim as noon, the close less them, falling after the open.
    claims = (
        HOURS[0] <= early < opens,
        all(opens <= early + late and opens + late < closes for late in (LATE_HOURS, WINTER_HOURS)),
        closes <= apple and apple + WINTER_HOURS <= HOURS[1],
        f.before_open > 0 and f.in_session > 0,
    )
    if not all(claims):
        raise ValueError(
            f"the sketch draws every filing before the open moving inside the session and "
            f"Apple's staying after the close, and these times do not: {f}"
        )
    row1, row2, row3 = ROWS_Y
    left, right = _at(opens), _at(closes)

    def shift(gid: str, start: float, end: float, y: float) -> Stroke:
        """The arrow above a row, from the middle of its span to the middle of the late copy."""
        middle = (start + end) / 2
        return _stroke(
            gid,
            _arrow(_at(middle), y + ARROW_RISE, _at(middle + LATE_HOURS), y + ARROW_RISE),
            color=INK,
            frames=6,
        )

    clock = _line(
        [(HOUR_X[0], CLOCK_Y), (HOUR_X[1], CLOCK_Y)],
        per_unit=4,
    )
    steps: list[Stroke | Fill | Label] = [
        _stroke("clock", clock, color=MUTED, frames=8),
        Label(
            f"under daylight saving time, {WINTER_HOURS} hours in winter",
            9.65,
            4.3,
            names="clock",
            color=MUTED,
            size=10,
            ha="right",
        ),
        Label(
            clock_text(HOURS[0], minutes=False),
            HOUR_X[0],
            CLOCK_Y - 0.29,
            names="clock",
            color=MUTED,
            size=10,
        ),
        Label(
            clock_text(opens),
            left,
            CLOCK_Y - 0.29,
            names="clock",
            color=MUTED,
            size=10,
            ha="center",
        ),
        Label(
            clock_text(closes),
            right,
            CLOCK_Y - 0.29,
            names="clock",
            color=MUTED,
            size=10,
            ha="center",
        ),
        Label(
            clock_text(HOURS[1], minutes=False),
            HOUR_X[1],
            CLOCK_Y - 0.29,
            names="clock",
            color=MUTED,
            size=10,
            ha="right",
        ),
        Fill("session", left, CLOCK_Y, right, TINT_TOP, REJECT_TINT),
        _stroke(
            "session-edge",
            _box(left, CLOCK_Y, right, TINT_TOP),
            color=LOST,
            width=TINT_EDGE,
            frames=4,
        ),
        Label(
            f"{f.in_session} accepted during the session, where R1 flags nothing",
            (left + right) / 2,
            3.88,
            names="session",
            color=LOST,
            size=10,
            ha="center",
        ),
        # Row 1: every filing before the open reads inside the session.
        _stroke("morning", _span(_at(early), left, row1), color=INK, frames=6),
        Label(
            f"{f.before_open:,} filings\naccepted before\nthe open",
            HOUR_X[0],
            row1 - 0.72,
            names="morning",
            size=10,
        ),
        shift("morning-shift", early, opens, row1),
        _stroke(
            "morning-late",
            _span(_at(early + LATE_HOURS), _at(opens + LATE_HOURS), row1),
            color=LOST,
            frames=6,
        ),
        Label(
            "read late: inside the session",
            RIGHT_X,
            row1 + 0.25,
            names="morning-late",
            color=LOST,
            size=10,
        ),
        Label(
            f"nothing counts\nhow many of the\n{f.before_open:,} read late",
            HOUR_X[0],
            row1 - 1.65,
            names="morning-late",
            color=MUTED,
            size=10,
        ),
        # Row 2: Apple's evening releases stay after the close.
        _dot("apple", _at(apple), row2, color=INK),
        Label(f"Apple, about {clock_text(apple)}", RIGHT_X, row2 - 0.4, names="apple", size=10),
        _stroke(
            "apple-shift",
            _arrow(_at(apple) + DOT_GAP, row2, _at(apple + LATE_HOURS) - DOT_GAP, row2),
            color=INK,
            frames=5,
        ),
        _dot("apple-late", _at(apple + LATE_HOURS), row2, color=GOOD),
        Label(
            "same flag, the next morning",
            RIGHT_X,
            row2 - 0.7,
            names="apple-late",
            color=GOOD,
            size=10,
        ),
        # Row 3: noon to the close moves past the close.
        _stroke("afternoon", _span(_at(noon), right, row3), color=INK, frames=6),
        shift("afternoon-shift", noon, closes, row3),
        _stroke(
            "afternoon-late",
            _span(right, _at(closes + LATE_HOURS), row3),
            color=LOST,
            frames=6,
        ),
        Label(
            "flags the next day, whose gap\nopens after its news is out",
            RIGHT_X,
            row3 - 0.58,
            names="afternoon-late",
            color=LOST,
            size=10,
        ),
    ]
    return Scene(f"{_word(LATE_HOURS).capitalize()} hours late", "four_hours_late", tuple(steps))


def _word(count: int) -> str:
    return ("zero", "one", "two", "three", "four", "five", "six")[count]


# --- Drawing ------------------------------------------------------------------

#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label or tint shows on its own for
#: :data:`PACED_LABEL_MS` and the finished drawing holds for
#: :data:`PACED_HOLD_MS` before the loop. Both match
#: :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("where_the_56_go", "four_hours_late")
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


def read_figures(data_dir: Path | None = None) -> tuple[Universes, FilingTimes]:
    """Read the committed files once, through :func:`chan.pead_rerun.read_committed`."""
    sources = pead_rerun.read_committed(data_dir)
    return Universes.from_sources(sources), FilingTimes.from_index(sources.releases)


def scenes(
    universes: Universes | None = None, times: FilingTimes | None = None
) -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them, Lesson 1's then Lesson 2's.

    Both sets of figures default to :func:`read_figures` on the committed files.
    """
    if universes is None or times is None:
        read_universes, read_times = read_figures()
        universes = universes if universes is not None else read_universes
        times = times if times is not None else read_times
    return (_where_the_56_go(universes), _four_hours_late(times))


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


def make_pead_rerun_whiteboards(out_dir: Path | None = None) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes()]


def main() -> None:
    for path in make_pead_rerun_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
