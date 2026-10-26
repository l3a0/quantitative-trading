"""Whiteboard sketches for the post on Chan's Bollinger band on GLD and USO.

``blog/bollinger-band-lessons.md`` makes two claims a reader has to picture
from sentences: a held long can turn into a short on one close, and dividing
the moving deviation by n rather than n − 1 can push a z-score across the
band and open a position the script never opens. This module draws each as a
scene, sketched stroke by stroke as if on a whiteboard, as a looping GIF the
post places right after the text it draws.

1. Sixteen days of the band: the 16 traded days from 2006-07-27 to
   2006-08-17, the z-score as black dots against red dashed lines at −1 and
   +1 and a grey line at 0, above a strip of the units held. The strip turns
   green and long where the z-score enters below −1 and stays long while
   three dots sit back inside the band, two just above −1, which a note
   names, and one just below 0. It turns red and short on the one close
   that a ring marks, where the z-score jumps from below 0 to above 1. It
   goes flat and then long again at the end. It sits after the paragraph
   opening "At these thresholds", in "The rule and the file".
2. One close, two divisors: the 11 traded days from 2007-05-24 to
   2007-06-08, each day's z-score twice, black on the left with the n − 1
   divisor ``bollinger.m`` uses and brown on the right with n, which is the
   black one times √(20/19). A ring marks 2007-05-29, where the black dot sits
   just under +1 and the brown just over it. Two strips show the units: the
   n − 1 run flat throughout, the n run short from that day until it exits on
   2007-06-07. It sits after Lesson 3's list, after the item opening "**The
   Sharpe ratio** becomes 0.984872".

The sketches are not schematic. Each dot sits at its day's z-score on one
scale, and every figure and count the labels print is read from the run.
:meth:`BandRun.from_run` reads the committed file through
:func:`chan.price_spread.read_sources`, scale-break guard included, and runs
:func:`chan.bollinger.example_three_two`, the path ``python -m chan.bollinger``
runs. The n divisor's z-score comes from
:func:`chan.bollinger_figures.zscore_divided_by_n` and its units from
:func:`chan.bollinger_figures.divided_by_n`, the calculation behind the
figure's dashed line. A run whose days would make the words false is refused
rather than drawn. The two windows' dates are this module's choice, in
:data:`TURN_DAYS` and :data:`DIVISOR_DAYS`.

The strokes, the timeline and the renderer are
:mod:`chan.usdcad_tests_whiteboard`'s, so an edit there changes these GIFs too,
and that module's docstring explains why two draws on one machine give the
same bytes. Each sketch carries more than a reader takes in at that post's
pace, so both are in :data:`PACED`. Each GIF is named :data:`GIF_PREFIX` plus
the scene's slug, a prefix chosen so no GIF name starts like the post's chart,
``bollinger_band.png``. Redraw both with::

    uv run python -m chan.bollinger_whiteboard
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from chan.bollinger import ENTRY_ZSCORE, EXIT_ZSCORE, example_three_two
from chan.bollinger_figures import divided_by_n, zscore_divided_by_n
from chan.paths import FIGURES_DIR
from chan.price_spread import LOOKBACK, read_sources
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.series import WindowCrossesScaleBreak
from chan.usdcad_tests_whiteboard import (
    Frame,
    Label,
    Scene,
    Stroke,
    _line,
    _stroke,
    render,
    timeline,
)
from chan.vintage import VintageUnavailable

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "bollinger_sketch_"

#: The first and last day each scene draws.
TURN_DAYS = ("2006-07-27", "2006-08-17")
DIVISOR_DAYS = ("2007-05-24", "2007-06-08")


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``bollinger_sketch_one_close.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


@dataclass(frozen=True)
class Stretch:
    """Consecutive traded days of the band, under both divisors.

    ``zscore`` and ``units`` are ``bollinger.m``'s, with the n − 1 divisor.
    ``zscore_n`` and ``units_n`` are the same days with n.
    """

    days: tuple[pd.Timestamp, ...]
    zscore: np.ndarray
    units: np.ndarray
    zscore_n: np.ndarray
    units_n: np.ndarray


@dataclass(frozen=True)
class BandRun:
    """What both scenes draw: two stretches of the run, and three counts over all of it.

    ``differ`` counts the days on which the two divisors' units differ, and
    ``exits`` and ``exits_n`` count the days a unit goes flat under n − 1 and
    under n.
    """

    turn: Stretch
    divisors: Stretch
    differ: int
    exits: int
    exits_n: int

    @classmethod
    def from_run(cls, closes: pd.DataFrame | None = None) -> BandRun:
        """Read the figures from ``closes``, or from the committed file when none is given."""
        if closes is None:
            _, closes = read_sources()
        result = example_three_two(closes)
        band = result.bollinger
        days = band.signal.days
        zscore_n = zscore_divided_by_n(band.signal)
        units_n = divided_by_n(band.signal).units

        def stretch(first: str, last: str) -> Stretch:
            kept = (days >= pd.Timestamp(first)) & (days <= pd.Timestamp(last))
            return Stretch(
                days=tuple(days[kept]),
                zscore=result.zscore[kept],
                units=band.units[kept],
                zscore_n=zscore_n[kept],
                units_n=units_n[kept],
            )

        return cls(
            turn=stretch(*TURN_DAYS),
            divisors=stretch(*DIVISOR_DAYS),
            differ=int(np.count_nonzero(band.units != units_n)),
            exits=exits(band.units),
            exits_n=exits(units_n),
        )


def exits(units: np.ndarray) -> int:
    """How many days a held unit goes flat."""
    return int(np.count_nonzero((units[:-1] != 0) & (units[1:] == 0)))


def runs(units: np.ndarray) -> list[tuple[int, int, float]]:
    """Each stretch of equal units as ``(first row, last row, units)``, in order."""
    found, start = [], 0
    for row in range(1, len(units) + 1):
        if row == len(units) or units[row] != units[start]:
            found.append((start, row - 1, float(units[start])))
            start = row
    return found


#: Numbers in words for a title that counts its days.
NUMBER_WORDS = {
    11: "eleven",
    12: "twelve",
    13: "thirteen",
    14: "fourteen",
    15: "fifteen",
    16: "sixteen",
    17: "seventeen",
    18: "eighteen",
    19: "nineteen",
    20: "twenty",
}


def _ordinal(count: int) -> str:
    """``77th``, ``1st``, ``12th``."""
    tail = "th" if 10 <= count % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(count % 10, "th")
    return f"{count}{tail}"


def _article(count: int) -> str:
    """``an`` before an ordinal said with a vowel first, such as 8th, 11th, 18th or 80th."""
    digits = str(count)
    spoken_eight = digits.startswith("8") or (digits[:2] in ("11", "18") and len(digits) % 3 == 2)
    return "an" if spoken_eight else "a"


def _ring(x: float, y: float, radius: float) -> tuple[np.ndarray, np.ndarray]:
    """A circle round (x, y) on the board, drawn from its right-hand point."""
    turn = np.linspace(0.0, 2 * np.pi, 25)
    return x + radius * np.cos(turn), y + radius * np.sin(turn)


#: The word under each kind of stretch, and its ink. A held unit is a thick
#: bar and a flat one a thin grey line, so the width is a second cue.
WORD = {1.0: "long", -1.0: "short", 0.0: "flat"}
WORD_INK = {"long": GOOD, "short": LOST, "flat": MUTED}
BAR_WIDTH, FLAT_WIDTH = 7.0, 2.2
#: How far a stretch's word sits above or below its strip.
WORDS_APART = 0.36
#: How big a z-score dot is, in points.
DOT = 6.0
#: How far a level's or a strip's name sits left of where its line starts.
NAME_GAP = 0.2
#: The date range's place, at the right of the title's row.
DATES_X, DATES_Y = 9.6, 4.3


def _strip(
    prefix: str,
    units: np.ndarray,
    x: np.ndarray,
    y: float,
    words_y: float,
    after: dict[int, list[Stroke | Label]] | None = None,
) -> list[Stroke | Label]:
    """A bar along the days for each stretch of equal units, each with its word.

    A stretch runs from half a day before its first day to half a day after
    its last, so each day's units sit under its dot. ``after`` holds steps
    drawn right after the stretch that starts on a given row.
    """
    step = float(x[1] - x[0])
    steps: list[Stroke | Label] = []
    for first, last, held in runs(units):
        word = WORD[held]
        gid = f"{prefix}-{first}"
        x0, x1 = float(x[first]) - step / 2, float(x[last]) + step / 2
        steps.append(
            _stroke(
                gid,
                _line([(x0, y), (x1, y)], per_unit=10),
                color=WORD_INK[word],
                width=FLAT_WIDTH if word == "flat" else BAR_WIDTH,
                frames=3,
            )
        )
        steps.append(
            Label(
                word, (x0 + x1) / 2, words_y, names=gid, color=WORD_INK[word], size=11, ha="center"
            )
        )
        steps += (after or {}).get(first, [])
    return steps


def _level(gid: str, z: float, name: str, ink: str, x0: float, x1: float, z_y) -> list:
    """A level across the days at z-score ``z``, dashed unless it is 0, with its name at left."""
    y = float(z_y(z))
    return [
        _stroke(gid, _line([(x0, y), (x1, y)]), color=ink, dashed=bool(z), width=1.5, frames=4),
        Label(name, x0 - NAME_GAP, y, names=gid, color=ink, size=11, ha="right"),
    ]


def _dates(stretch: Stretch, names: str) -> Label:
    first, last = stretch.days[0].date(), stretch.days[-1].date()
    return Label(
        f"{first} to {last}", DATES_X, DATES_Y, names=names, color=MUTED, size=11, ha="right"
    )


# --- Sixteen days of the band ----------------------------------------------------

#: Where the first and last day sit across the board, the height of a z-score
#: of zero, and the height of one deviation.
TURN_X = (1.75, 9.45)
TURN_ZERO, TURN_PER_Z = 2.85, 0.65
#: The strip of units, and the row of notes between it and the dots.
TURN_STRIP, TURN_NOTES = 1.0, 1.45
#: How far the entry's note runs past its day, so it ends just past the dot
#: and leaves the row to its right for the note on the days back inside.
ENTRY_NOTE_PAST = 0.35
#: The ring round the turning day's dot.
TURN_RING = 0.15


def turn_x(stretch: Stretch) -> np.ndarray:
    """Each day's place across the board, evenly spaced."""
    return np.linspace(*TURN_X, len(stretch.days))


def turn_y(z):
    """The board height of a z-score in the first scene."""
    return TURN_ZERO + TURN_PER_Z * np.asarray(z)


@dataclass(frozen=True)
class TurnDays:
    """The rows of the first scene's three notes: the long's entry, the first
    stretch of days back inside the band while long, and the turn."""

    entry: int
    inside: tuple[int, ...]
    turn: int


def turn_days(stretch: Stretch) -> TurnDays:
    """Find the days the notes point at, and refuse a stretch that would make them false."""
    z, units = stretch.zscore, stretch.units
    turns = [t for t in range(1, len(units)) if units[t - 1] == 1 and units[t] == -1]
    if len(turns) != 1:
        raise ValueError(
            f"Sixteen days of the band draws one turn from long to short, not {len(turns)}"
        )
    (turn,) = turns
    if not (z[turn - 1] < EXIT_ZSCORE and z[turn] > ENTRY_ZSCORE):
        raise ValueError("the turn's note says one close passes the exit at 0 and the entry at 1")
    entries = [t for t in range(1, turn) if units[t - 1] == 0 and units[t] == 1]
    if not entries or not z[entries[0]] < -ENTRY_ZSCORE:
        raise ValueError("Sixteen days of the band draws a long entered below −1 before the turn")
    entry = entries[0]
    inside = [t for t in range(entry, turn) if -ENTRY_ZSCORE < z[t] < EXIT_ZSCORE]
    if not inside:
        raise ValueError(
            "Sixteen days of the band draws a long held with the z-score inside the band"
        )
    first = [inside[0]]
    for t in inside[1:]:
        if t != first[-1] + 1:
            break
        first.append(t)
    return TurnDays(entry=entry, inside=tuple(first), turn=turn)


def _one_close(stretch: Stretch) -> Scene:
    """The paragraph opening "At these thresholds": a long held, then turned short on one close."""
    count = len(stretch.days)
    if count not in NUMBER_WORDS:
        raise ValueError(f"the title spells its count of days, and has no word for {count}")
    x, y = turn_x(stretch), turn_y(stretch.zscore)
    marks = turn_days(stretch)
    step = float(x[1] - x[0])
    left, right = TURN_X[0] - step / 2, TURN_X[1] + step / 2
    ring_x, ring_y = float(x[marks.turn]), float(y[marks.turn])
    inside_x = float(np.mean(x[list(marks.inside)]))
    after = {
        marks.entry: [
            Label(
                "enters below −1",
                float(x[marks.entry]) + ENTRY_NOTE_PAST,
                TURN_NOTES,
                names=f"units-{marks.entry}",
                color=GOOD,
                size=12,
                ha="right",
            ),
            Label(
                "back inside the band, still long",
                inside_x,
                TURN_NOTES,
                names=f"units-{marks.entry}",
                color=MUTED,
                size=12,
                ha="center",
            ),
            _stroke("turn", _ring(ring_x, ring_y, TURN_RING), color=ACCENT, frames=4),
            Label(
                "one close: exit at 0 and short above 1",
                ring_x - TURN_RING - 0.17,
                ring_y + 0.2,
                names="turn",
                color=ACCENT,
                size=12,
                ha="right",
            ),
        ]
    }
    steps: list[Stroke | Label] = [
        *_level("short-entry", ENTRY_ZSCORE, "+1", LOST, left, right, turn_y),
        *_level("exit", EXIT_ZSCORE, "0", MUTED, left, right, turn_y),
        *_level("long-entry", -ENTRY_ZSCORE, "−1", LOST, left, right, turn_y),
        Stroke("zscore", x, y, color=INK, frames=8, dots=DOT),
        _dates(stretch, "zscore"),
    ]
    strip = _strip("units", stretch.units, x, TURN_STRIP, TURN_STRIP - WORDS_APART, after)
    steps += strip[:1]
    steps.append(
        Label("units held", left - NAME_GAP, TURN_STRIP, names=strip[0].gid, size=11, ha="right")
    )
    steps += strip[1:]
    return Scene(f"{NUMBER_WORDS[count].capitalize()} days of the band", "one_close", tuple(steps))


# --- One close, two divisors ----------------------------------------------------

DIVISOR_X = (2.75, 9.35)
DIVISOR_ZERO, DIVISOR_PER_Z = 2.7, 0.85
#: How far each divisor's dot sits from its day, left for n − 1 and right for
#: n. The two z-scores differ by under 3 percent, a pixel or two at this
#: scale, so side by side is the only way both show.
BESIDE = 0.11
#: The two strips, n − 1 above n, and where their names end.
STRIP_N1, STRIP_N = 1.45, 0.95
STRIP_NAMES_X = 2.25
#: The ring round the pair of dots on the day the n run enters.
PAIR_RING = 0.25
#: The legend's two halves on one row under the zero line, and the closing
#: note's row.
LEGEND_X, LEGEND_Y = (DIVISOR_X[0], 5.6), 2.3
#: How far the short entry's name sits under its line, at the right end,
#: where the z-score has fallen away from it.
SHORT_NAME_BELOW = 0.31
NOTE_Y = 0.25


def divisor_x(stretch: Stretch) -> np.ndarray:
    """Each day's place across the board, evenly spaced."""
    return np.linspace(*DIVISOR_X, len(stretch.days))


def divisor_y(z):
    """The board height of a z-score in the second scene."""
    return DIVISOR_ZERO + DIVISOR_PER_Z * np.asarray(z)


def factor(lookback: int = LOOKBACK) -> float:
    """√(n / (n − 1)), what dividing by n rather than n − 1 multiplies a z-score by."""
    return math.sqrt(lookback / (lookback - 1))


@dataclass(frozen=True)
class DivisorDays:
    """The rows of the second scene's marks: the n run's entry and its exit."""

    entry: int
    exit: int


def divisor_days(run: BandRun) -> DivisorDays:
    """Find the n run's entry and exit, and refuse a stretch that would make the words false."""
    stretch = run.divisors
    z, zn = stretch.zscore, stretch.zscore_n
    if np.any(stretch.units != 0):
        raise ValueError("One close, two divisors draws the n − 1 run flat throughout")
    entries = [
        t for t in range(1, len(zn)) if stretch.units_n[t - 1] == 0 and stretch.units_n[t] == -1
    ]
    if len(entries) != 1:
        raise ValueError(
            f"One close, two divisors draws one short entered under n, not {len(entries)}"
        )
    (entry,) = entries
    if not (z[entry] < ENTRY_ZSCORE < zn[entry]):
        raise ValueError("the ring says the n − 1 z-score sits under 1 and the n z-score over it")
    flats = [
        t
        for t in range(entry + 1, len(zn))
        if stretch.units_n[t - 1] == -1 and stretch.units_n[t] == 0
    ]
    if len(flats) != 1:
        raise ValueError(f"One close, two divisors draws one exit under n, not {len(flats)}")
    if run.exits_n != run.exits + 1:
        raise ValueError(f"the exit's label says n has one more exit than n − 1's {run.exits}")
    return DivisorDays(entry=entry, exit=flats[0])


def _two_divisors(run: BandRun) -> Scene:
    """Lesson 3's list: one z-score just under 1 crosses it under n and opens a short."""
    stretch = run.divisors
    marks = divisor_days(run)
    x = divisor_x(stretch)
    step = float(x[1] - x[0])
    left, right = DIVISOR_X[0] - step / 2, DIVISOR_X[1] + step / 2
    y, yn = divisor_y(stretch.zscore), divisor_y(stretch.zscore_n)
    ring_x = float(x[marks.entry])
    ring_y = float((y[marks.entry] + yn[marks.entry]) / 2)
    differ_here = int(np.count_nonzero(stretch.units != stretch.units_n))
    exit_x = float(x[marks.exit]) - step / 2
    n_strip = _strip(
        "n",
        stretch.units_n,
        x,
        STRIP_N,
        STRIP_N - WORDS_APART,
        {
            marks.exit: [
                Label(
                    f"{_article(run.exits_n)} {_ordinal(run.exits_n)} exit, "
                    f"on {stretch.days[marks.exit].date()}",
                    exit_x,
                    NOTE_Y,
                    names=f"n-{marks.exit}",
                    color=ACCENT,
                    size=11,
                    ha="center",
                )
            ]
        },
    )
    n1_strip = _strip("n1", stretch.units, x, STRIP_N1, STRIP_N1 + WORDS_APART)
    n1_strip[1] = Label(
        "flat throughout",
        n1_strip[1].x,
        n1_strip[1].y,
        names=n1_strip[1].names,
        color=MUTED,
        size=11,
        ha="center",
    )
    steps: list[Stroke | Label] = [
        *_level("short-entry", ENTRY_ZSCORE, "+1", LOST, left, right, divisor_y),
        Label(
            "short above +1",
            right,
            float(divisor_y(ENTRY_ZSCORE)) - SHORT_NAME_BELOW,
            names="short-entry",
            color=LOST,
            size=11,
            ha="right",
        ),
        *_level("exit", EXIT_ZSCORE, "0", MUTED, left, right, divisor_y),
        Stroke("zscore", x - BESIDE, y, color=INK, frames=6, dots=DOT),
        Label("left dots: divide by n − 1", LEGEND_X[0], LEGEND_Y, names="zscore", size=11),
        _dates(stretch, "zscore"),
        Stroke("zscore-n", x + BESIDE, yn, color=ACCENT, frames=6, dots=DOT),
        Label(
            "right dots: divide by n",
            LEGEND_X[1],
            LEGEND_Y,
            names="zscore-n",
            color=ACCENT,
            size=11,
        ),
        _stroke("entry", _ring(ring_x, ring_y, PAIR_RING), color=ACCENT, frames=4),
        Label(
            f"{stretch.zscore[marks.entry]:.4f} × {factor():.4f} = "
            f"{stretch.zscore_n[marks.entry]:.4f}",
            ring_x + PAIR_RING + 0.18,
            ring_y + 0.4,
            names="entry",
            color=ACCENT,
            size=12,
        ),
        n1_strip[0],
        Label(
            "n − 1 (bollinger.m)",
            STRIP_NAMES_X,
            STRIP_N1,
            names=n1_strip[0].gid,
            size=11,
            ha="right",
        ),
        *n1_strip[1:],
        n_strip[0],
        Label("n", STRIP_NAMES_X, STRIP_N, names=n_strip[0].gid, color=ACCENT, size=11, ha="right"),
        *n_strip[1:],
        Label(
            f"the units differ on {differ_here} days here and {run.differ} in all",
            0.25,
            NOTE_Y,
            names=n_strip[0].gid,
            color=MUTED,
            size=11,
        ),
    ]
    return Scene("One close, two divisors", "two_divisors", tuple(steps))


# --- Drawing ------------------------------------------------------------------

#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("one_close", "two_divisors")
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


def scenes(run: BandRun | None = None) -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them. ``run`` defaults to the committed file's."""
    run = run if run is not None else BandRun.from_run()
    return (_one_close(run.turn), _two_divisors(run))


def draft() -> tuple[Scene, ...]:
    """Both scenes on the committed file, for the sketch-notes draft script."""
    return scenes()


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


def make_bollinger_whiteboards(
    out_dir: Path | None = None, run: BandRun | None = None
) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes(run)]


def main() -> None:
    try:
        paths = make_bollinger_whiteboards()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # As in chan.bollinger.main, a refusal that names the source or the
        # flagged day reaches the operator as one line.
        raise SystemExit(str(refused)) from refused
    for path in paths:
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
