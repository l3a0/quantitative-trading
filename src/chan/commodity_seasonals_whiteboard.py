"""Whiteboard sketches for the commodity seasonals post, for Lessons 1, 2 and 4.

``blog/commodity-seasonals-lessons.md`` checks Chan's two commodity seasonal
trades against EIA's settlements. Eight of its passages turn on a picture a
sentence has to build in the reader's head: where a count of profitable years
starts, which edition each of gasoline's two claims was written for, what
three missing rows leave of a count, why a guessed price cannot stand in for a
missing one, what Chan's 19 needs of the missing years, how the second fill
carries June's move across a gap, how far a fill misses against each year's
move, and which numbered file holds the June contract on a given day. This
module draws those eight as scenes, and the post places each right after the
paragraph it draws.

1. Where the count starts decides where a streak ends: a year axis from 1994
   to the first losing year, a dot for each profitable year and a cross for
   the loss, a note naming the trade as natural gas's June contract, a dashed
   mark for the first edition's release in November 2008, brackets above the
   axis for the streaks of 13 and 14 counted from 1995 and brackets below for
   the same counts from 1994. It sits in Lesson 1, after the list of what the
   files rule out and cannot pick, which opens
   "1. **They rule out the revised edition.**".
2. Gasoline's two claims read as two editions: a year axis from 1995 to
   2015 with a dot for each profitable gasoline year, a cross for each loss,
   a span under the years with no row, a dashed mark for the first edition's
   release, a brown bracket from 1995 to 2008 for the sidebar's profit every
   year since 1995, and a black bracket from 1995 to 2015 for the main text's
   19 of 21. The sidebar's bracket ends before the first loss, and the main
   text's runs past both. It sits in Lesson 1 after the paragraph opening
   "Gasoline’s main text says 19 profitable years".
3. Three missing rows leave a range, not a count: gasoline's years from 1995
   to 2015 with a span under the years with no row, then a scale of counts on
   which the files allow 16 to 19 profitable years and Chan's 19 sits at the
   top. It sits in Lesson 2 after the paragraph opening "EIA’s New York
   Harbor file holds no row".
4. Interpolating turns a gap into a guess: the May gasoline contract's
   settlements around April 14, 1997, the entry day with no row, a straight
   line between the rows on either side and the guess it gives that day, and
   a band of one typical miss either side of the guess, split at the exit
   price into a part where the year is a loss and a part where it is a profit.
   It sits after the paragraph opening "Interpolating, which here means".
5. Chan's 19 needs all three gaps to be profits: Chan's 21 years as one bar
   of 19 profits and 2 losses, and the files' as 16 profits, 3 years with no
   row and the 2 losses of 2009 and 2012, so the missing years sit under the
   end of Chan's profits. It sits after the paragraph opening "The losses say
   more than the gaps."
6. Fill 2 carries June's move across the gap: May's and June's settlements
   around April 14, 1997, May as dots and June as rings, June's rise from the
   last day both files hold to the gap day, the same rise added to May's
   price there to give fill 2's guess, and a band of fill 2's typical miss
   either side, split at the exit price. It sits after the list opening
   "1. **Fill 1, a straight line**".
7. Each corrected move against fill 2's spread: for each missing year, the
   year's move with fill 2's guess corrected by its average miss, a bar of the
   spread of its misses either side, and each year's chance of a profit. The
   bars for 1997 and 1998 cross zero and 1999's stops short. It sits after
   the paragraph opening "So the chance that all three years were profits".
8. Which file holds the June contract: the March, April, May and June natural
   gas contracts as bars on a calendar from late February to the start of
   May, each ending at its last trading day, for one year in which March is
   still trading on the entry date and one in which it has expired. A dashed
   line at each entry and exit crosses the contracts still trading that day,
   and June's number is how many it crosses, which its closing label says. It
   sits in Lesson 4, after the paragraph opening "For gasoline the answer is
   simple."

All eight carry data, and none needs the owner's archive.
:meth:`StreakFigures.from_run` reads every natural gas trade from the
committed EIA files through :func:`chan.commodity_seasonals.natural_gas_trades`
and counts its streaks with :func:`chan.commodity_seasonals.runs_ending`.
:meth:`GasolineFigures.from_run` reads each gasoline year's result from
:func:`chan.commodity_seasonals.gasoline_trades`, which the edition, range and
Chan's-19 sketches all draw. :meth:`GuessFigures.from_run` reads 1997's
straight-line fill and its typical miss from
:func:`chan.commodity_seasonals.gap_fills`, and the settlements around it from
the contract-1 file. :meth:`FillTwoFigures.from_run` reads the same gap's
fill 2 and the contract-1 and contract-2 settlements around it. The fill-miss
sketch reads every gap's fill from :func:`chan.commodity_seasonals.gap_fills`
too.
:meth:`JuneYear.from_run` reads one year's entry and exit days and file
numbers from :func:`chan.commodity_seasonals.natural_gas_trade`, and each
contract's last trading day from :func:`chan.futures.ng_last_trade`. Three
figures are the book's rather than the run's: the counts 13 and 14 Chan
prints, which the streak sketch looks up in the run's streaks, gasoline's 19
profitable years of 21 as of 2015, which three sketches draw, and the first
edition's release in November 2008, which the post cites.

The calendar sketch draws 2008 and 2006. In 2008 the entry, February 25, comes
two days before March's last trading day, so June is contract 4. In 2006 the
entry moves to Monday, February 27, after March's last day on the 24th, so
June is contract 3. 2007 is left out because its entry falls on March's own
last day, the edge case the post's third check of the expiry rule covers.
Both years' calendars are drawn on one axis of month and day.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look, frame rate and colours.
Each sketch carries more than a reader takes in at that post's pace, so
all eight are in :data:`PACED`, and :func:`sketch_timeline` holds each of their
labels longer and their finished drawings for twelve seconds, as
:mod:`chan.equity_seasonals_whiteboard` does for its slow sketches. Only
the scenes, the pacing and the file names are this module's. Each GIF is
named :data:`GIF_PREFIX` plus the scene's slug, a prefix chosen so no GIF
name starts like the post's chart, ``commodity_seasonals_years.png``.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw all eight with::

    uv run python -m chan.commodity_seasonals_whiteboard
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import numpy as np

from chan import commodity_seasonals as seasonals
from chan.commodity_seasonals_figures import GASOLINE_BOOK_END
from chan.futures import ng_last_trade
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    Frame,
    Label,
    Scene,
    Stroke,
    _arrow,
    _box,
    _line,
    _span,
    _stroke,
    render,
    timeline,
)

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "commodity_sketch_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``commodity_sketch_june_file.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


def _cross(gid: str, x: float, y: float, color: str, r: float = 0.12) -> Stroke:
    """An x centred on (x, y), drawn as one stroke."""
    return _stroke(
        gid,
        _line([(x - r, y - r), (x + r, y + r), (x, y), (x - r, y + r), (x + r, y - r)], 20),
        color=color,
        width=2.6,
        frames=2,
    )


# --- Lesson 1: where the count starts ----------------------------------------

#: The counts of consecutive profitable years Chan prints, 13 in the main text
#: and 14 in the sidebar, both on p. 185 of the revised edition, each with the
#: words its bracket carries above the axis.
BOOK_COUNTS = ((13, "main text"), (14, "sidebar"))
#: The two start years the post compares: 1995, which Chan's gasoline sidebar
#: names, and 1994, the first year EIA's files hold a whole trade.
STARTS = (seasonals.RUN_START, seasonals.NG_YEARS[0])
#: The first edition's release, November 2008, which the post cites.
FIRST_EDITION = (2008, 11)
#: Which trade the dots are, since gasoline's sidebar supplies the 1995 start
#: and a reader meeting the sketch first could take it for gasoline's.
TRADE = "natural gas, June contract"


@dataclass(frozen=True)
class StreakFigures:
    """What the streak sketch draws, each field read from the natural gas run.

    ``years`` holds each year from the first year of the files to the first
    loss after it, with whether its trade was profitable. ``ends`` maps each
    start year to the year each of :data:`BOOK_COUNTS` ends in, counted from
    that start, in the order :data:`BOOK_COUNTS` lists them.
    """

    years: tuple[tuple[int, bool], ...]
    ends: dict[int, tuple[int, ...]]

    @property
    def loss(self) -> int:
        """The first losing year, where the axis ends."""
        return next(year for year, profitable in self.years if not profitable)

    @classmethod
    def from_run(cls) -> StreakFigures:
        gas = seasonals.natural_gas_trades(*seasonals.NG_YEARS)
        first_loss = next(t.year for t in gas if t.profitable is False)
        years = tuple((t.year, bool(t.profitable)) for t in gas if t.year <= first_loss)
        ends = {}
        for start in STARTS:
            runs = seasonals.runs_ending([t for t in gas if t.year >= start])
            ends[start] = tuple(
                min(year for year, run in runs.items() if run == count) for count, _ in BOOK_COUNTS
            )
        return cls(years=years, ends=ends)


#: Where the year axis runs on the board and its height. Each start year's two
#: brackets sit on its own side, 1995's above the axis and 1994's below, the
#: shorter streak nearer the axis.
STREAK_X = (0.5, 9.45)
STREAK_AXIS_Y = 2.4
BRACKET_YS = {STARTS[0]: (2.85, 3.45), STARTS[1]: (1.55, 0.95)}
#: How far a bracket's label sits from its bracket, up for the brackets above
#: the axis and down for those below.
BRACKET_LABEL_GAP = 0.3
#: How far below the axis each labelled year sits.
YEAR_LABEL_DROP = 0.42


def _streak_x(year: float, f: StreakFigures) -> float:
    """Where ``year`` sits on the axis, each year at the middle of its own slot."""
    first, last = f.years[0][0], f.loss
    return STREAK_X[0] + (year - first) * (STREAK_X[1] - STREAK_X[0]) / (last - first)


def _release_x(f: StreakFigures) -> float:
    """The first edition's release, at its month inside its year's slot.

    A year's mark sits at the middle of its slot, so January opens half a
    slot before it, and November 2008 sits ten and a half twelfths of a slot
    past that.
    """
    year, month = FIRST_EDITION
    return _streak_x(year - 0.5 + (month - 0.5) / 12, f)


def _streak_start(f: StreakFigures) -> Scene:
    """Lesson 1: the same files give streaks of 13 and 14 ending a year apart,
    depending on whether the count starts in 1995 or in 1994.

    Only the years a bracket starts or ends in, and the loss, carry a label,
    so the axis stays readable.
    """
    first, loss = f.years[0][0], f.loss
    x0, x1 = _streak_x(first, f), _streak_x(loss, f)
    y = STREAK_AXIS_Y
    won = [year for year, profitable in f.years if profitable]
    steps: list[Stroke | Label] = [
        _stroke("axis", _line([(x0 - 0.25, y), (x1 + 0.25, y)]), color=MUTED, frames=8),
        Stroke(
            "profitable",
            np.array([_streak_x(year, f) for year in won]),
            np.full(len(won), y),
            color=GOOD,
            frames=8,
            dots=7.0,
        ),
        _cross("loss", x1, y, LOST),
    ]
    ends = {year for years in f.ends.values() for year in years}
    for year in sorted({*STARTS, *ends, loss}):
        steps.append(
            Label(
                str(year),
                _streak_x(year, f),
                y - YEAR_LABEL_DROP,
                names="axis",
                color=MUTED,
                size=10,
                ha="center",
            )
        )
    steps.append(Label("loss", x1, y - 0.72, names="loss", color=LOST, size=11, ha="center"))
    steps.append(
        Label("dot: a profitable year", 0.3, 0.35, names="profitable", color=GOOD, size=11)
    )
    steps.append(Label(TRADE, 9.7, 0.35, names="profitable", color=MUTED, size=11, ha="right"))
    release = _release_x(f)
    steps += [
        _stroke(
            "release",
            _line([(release, y + 0.2), (release, 3.95)]),
            color=MUTED,
            dashed=True,
            frames=6,
        ),
        Label(
            "first edition, Nov 2008",
            release - 0.2,
            3.85,
            names="release",
            color=MUTED,
            size=11,
            ha="right",
        ),
    ]
    for start, color, side in ((STARTS[0], ACCENT, 1), (STARTS[1], INK, -1)):
        for (count, words), end, at in zip(
            BOOK_COUNTS, f.ends[start], BRACKET_YS[start], strict=True
        ):
            gid = f"from-{start}-{count}"
            left, right = _streak_x(start, f), _streak_x(end, f)
            steps.append(_stroke(gid, _span(left, right, at, tick=0.1), color=color, frames=8))
            text = f"{count} from {start}, {words}" if side > 0 else f"{count} from {start}"
            steps.append(
                Label(
                    text,
                    (left + right) / 2,
                    at + side * BRACKET_LABEL_GAP,
                    names=gid,
                    color=color,
                    size=11,
                    ha="center",
                )
            )
    return Scene("The start year decides where a streak ends", "streak_start", tuple(steps))


# --- Lesson 1: gasoline's two claims -----------------------------------------

#: Chan's gasoline main text: 19 profitable years of the last 21 "as of 2015"
#: (p. 183). The year is the chart's, where the book's gasoline years end.
GASOLINE_COUNT = (19, 21)
#: Which trade the dots are, the counterpart of :data:`TRADE`. Every gasoline
#: sketch whose title does not say gasoline carries it, so a reader landing on
#: one before its paragraph knows which commodity it draws.
GASOLINE_TRADE = "gasoline, May contract"
#: The editions sketch's note, which needs only the contract because its title
#: names gasoline.
GASOLINE_CONTRACT = "May contract"


@dataclass(frozen=True)
class GasolineFigures:
    """What the gasoline sketch draws, read from the gasoline run.

    ``years`` holds each year from :data:`chan.commodity_seasonals.RUN_START`,
    where the sidebar's count starts, to :data:`GASOLINE_BOOK_END`, with
    ``True`` for a profit, ``False`` for a loss and ``None`` for a year whose
    trade dates have no row in the file.
    """

    years: tuple[tuple[int, bool | None], ...]

    def _where(self, outcome: bool | None) -> list[int]:
        return [year for year, profitable in self.years if profitable is outcome]

    @property
    def won(self) -> list[int]:
        return self._where(True)

    @property
    def lost(self) -> list[int]:
        return self._where(False)

    @property
    def gaps(self) -> list[int]:
        return self._where(None)

    @classmethod
    def from_run(cls) -> GasolineFigures:
        trades = seasonals.gasoline_trades(seasonals.RUN_START, GASOLINE_BOOK_END)
        return cls(years=tuple((t.year, t.profitable) for t in trades))


#: Where the gasoline axis runs on the board and its height, and the heights of
#: the sidebar's bracket and the main text's above it.
GASOLINE_X = (0.55, 9.45)
GASOLINE_AXIS_Y = 2.0
SIDEBAR_Y, MAIN_TEXT_Y = 2.6, 3.35
#: How far below the axis the span under the missing years sits.
GAP_DROP = 0.8


def _gasoline_x(year: float, f: GasolineFigures) -> float:
    """Where ``year`` sits on the gasoline axis, each year at the middle of its slot."""
    first, last = f.years[0][0], f.years[-1][0]
    return GASOLINE_X[0] + (year - first) * (GASOLINE_X[1] - GASOLINE_X[0]) / (last - first)


def _consecutive(years: list[int]) -> list[list[int]]:
    """``years`` split into runs of consecutive years."""
    runs: list[list[int]] = []
    for year in years:
        if runs and year == runs[-1][-1] + 1:
            runs[-1].append(year)
        else:
            runs.append([year])
    return runs


def _and(years: list[int]) -> str:
    """The years as a sentence lists them, such as ``2009 and 2012``."""
    words = [str(year) for year in years]
    return words[0] if len(words) == 1 else f"{', '.join(words[:-1])} and {words[-1]}"


def _gasoline_editions(f: GasolineFigures) -> Scene:
    """Lesson 1: the sidebar's profit every year since 1995 holds to 2008, the
    first edition's years, and the main text's 19 of 21 runs to 2015, past
    both losses.
    """
    first, last = f.years[0][0], f.years[-1][0]
    edition, month = FIRST_EDITION
    release = _gasoline_x(edition - 0.5 + (month - 0.5) / 12, f)
    y = GASOLINE_AXIS_Y
    steps: list[Stroke | Label] = [
        _stroke(
            "axis",
            _line([(_gasoline_x(first, f) - 0.25, y), (_gasoline_x(last, f) + 0.25, y)]),
            color=MUTED,
            frames=8,
        ),
        Stroke(
            "profitable",
            np.array([_gasoline_x(year, f) for year in f.won]),
            np.full(len(f.won), y),
            color=GOOD,
            frames=8,
            dots=7.0,
        ),
    ]
    steps += [_cross(f"loss-{year}", _gasoline_x(year, f), y, LOST) for year in f.lost]
    for year in (first, edition, last):
        steps.append(
            Label(
                str(year),
                _gasoline_x(year, f),
                y - YEAR_LABEL_DROP,
                names="axis",
                color=MUTED,
                size=10,
                ha="center",
            )
        )
    for k, run in enumerate(_consecutive(f.gaps)):
        left, right = _gasoline_x(run[0], f), _gasoline_x(run[-1], f)
        steps.append(
            _stroke(f"gap-{k}", _span(left, right, y - GAP_DROP, tick=0.08), color=MUTED, frames=6)
        )
        steps.append(
            Label(
                "no row",
                (left + right) / 2,
                y - GAP_DROP - 0.4,
                names=f"gap-{k}",
                color=MUTED,
                size=11,
                ha="center",
            )
        )
    left = _gasoline_x(first, f)
    steps += [
        _stroke(
            "release",
            _line([(release, y + 0.2), (release, 3.95)]),
            color=MUTED,
            dashed=True,
            frames=6,
        ),
        Label(
            "first edition, Nov 2008",
            release + 0.25,
            2.8,
            names="release",
            color=MUTED,
            size=11,
        ),
        _stroke(
            "sidebar",
            _span(left, _gasoline_x(edition, f), SIDEBAR_Y, tick=0.1),
            color=ACCENT,
            frames=8,
        ),
        Label(
            f"sidebar: a profit every year since {first}",
            (left + _gasoline_x(edition, f)) / 2,
            SIDEBAR_Y + BRACKET_LABEL_GAP,
            names="sidebar",
            color=ACCENT,
            size=11,
            ha="center",
        ),
        _stroke("main-text", _span(left, _gasoline_x(last, f), MAIN_TEXT_Y, tick=0.1), frames=8),
        Label(
            f"main text: {GASOLINE_COUNT[0]} of {GASOLINE_COUNT[1]}, as of {last}",
            (left + release) / 2,
            MAIN_TEXT_Y + BRACKET_LABEL_GAP,
            names="main-text",
            color=INK,
            size=11,
            ha="center",
        ),
        Label("dot: a profitable year", 0.3, 0.35, names="profitable", color=GOOD, size=11),
        Label(
            f"x: a loss, {_and(f.lost)}",
            3.6,
            0.35,
            names=f"loss-{f.lost[0]}",
            color=LOST,
            size=11,
        ),
        Label(GASOLINE_CONTRACT, 9.7, 0.35, names="profitable", color=MUTED, size=11, ha="right"),
    ]
    return Scene("Gasoline’s two claims read as two editions", "gasoline_editions", tuple(steps))


# --- Lesson 2: what the missing rows leave -----------------------------------

#: The number words a title spells a small count in.
WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}

#: The range sketch's year axis and count scale, each with its height.
RANGE_YEAR_X = (0.55, 9.45)
RANGE_YEAR_Y = 3.0
RANGE_COUNT_X = (1.2, 8.8)
RANGE_COUNT_Y = 1.15


def _range_scale(f: GasolineFigures) -> tuple[int, int]:
    """The counts the scale runs between, one past each end of the range."""
    return len(f.won) - 1, len(f.won) + len(f.gaps) + 1


def _count_x(count: int, f: GasolineFigures) -> float:
    lo, hi = _range_scale(f)
    return RANGE_COUNT_X[0] + (count - lo) * (RANGE_COUNT_X[1] - RANGE_COUNT_X[0]) / (hi - lo)


def _range_year_x(year: int, f: GasolineFigures) -> float:
    first, last = f.years[0][0], f.years[-1][0]
    return RANGE_YEAR_X[0] + (year - first) * (RANGE_YEAR_X[1] - RANGE_YEAR_X[0]) / (last - first)


def _gap_range(f: GasolineFigures) -> Scene:
    """Lesson 2: the missing years count neither way, so the files allow a
    range of profitable years with Chan's count at its top."""
    first, last = f.years[0][0], f.years[-1][0]
    y, c = RANGE_YEAR_Y, RANGE_COUNT_Y
    low, high = len(f.won), len(f.won) + len(f.gaps)
    gaps = _consecutive(f.gaps)[0]
    steps: list[Stroke | Label] = [
        _stroke("axis", _line([(0.3, y), (9.7, y)]), color=MUTED, frames=8),
        Stroke(
            "profitable",
            np.array([_range_year_x(year, f) for year in f.won]),
            np.full(len(f.won), y),
            color=GOOD,
            frames=8,
            dots=7.0,
        ),
        *[_cross(f"loss-{year}", _range_year_x(year, f), y, LOST) for year in f.lost],
        *[
            Label(
                str(year),
                _range_year_x(year, f),
                y - YEAR_LABEL_DROP,
                names="axis",
                color=MUTED,
                size=10,
                ha="center",
            )
            for year in (first, last)
        ],
        _stroke(
            "gaps",
            _span(_range_year_x(gaps[0], f), _range_year_x(gaps[-1], f), y - 0.5, tick=0.08),
            color=MUTED,
            frames=6,
        ),
        Label(
            "no row: a profit or a loss?",
            _range_year_x(gaps[-1], f) + 0.3,
            y - 0.62,
            names="gaps",
            color=MUTED,
            size=11,
        ),
    ]
    lo, hi = _range_scale(f)
    steps += [
        _stroke(
            "scale", _line([(_count_x(lo, f), c), (_count_x(hi, f), c)]), color=MUTED, frames=6
        ),
        *[
            Label(
                str(n), _count_x(n, f), c - 0.42, names="scale", color=MUTED, size=10, ha="center"
            )
            for n in range(lo, hi + 1)
        ],
        _stroke(
            "range",
            _span(_count_x(low, f), _count_x(high, f), c + 0.35, tick=0.1),
            color=ACCENT,
            frames=8,
        ),
        Label(
            f"the files allow {low} to {high}",
            (_count_x(low, f) + _count_x(high, f)) / 2,
            c + 0.68,
            names="range",
            color=ACCENT,
            size=11,
            ha="center",
        ),
        _stroke(
            "chan",
            _line(
                [
                    (_count_x(GASOLINE_COUNT[0], f), c - 0.12),
                    (_count_x(GASOLINE_COUNT[0], f), c + 0.12),
                ],
                per_unit=20,
            ),
            color=INK,
            width=3.0,
            frames=2,
        ),
        Label(
            f"Chan: {GASOLINE_COUNT[0]}",
            _count_x(GASOLINE_COUNT[0], f) + 0.2,
            c - 0.42,
            names="chan",
            color=INK,
            size=11,
        ),
        Label(
            f"profitable years of {len(f.years)}",
            0.3,
            0.3,
            names="scale",
            color=MUTED,
            size=11,
        ),
    ]
    steps.append(Label(GASOLINE_TRADE, 9.7, 0.3, names="axis", color=MUTED, size=11, ha="right"))
    title = f"{WORDS[len(f.gaps)].capitalize()} missing rows leave a range, not a count"
    return Scene(title, "gap_range", tuple(steps))


# --- Lesson 2: interpolating turns a gap into a guess -------------------------


@dataclass(frozen=True)
class GuessFigures:
    """What the interpolation sketch draws, read from the gasoline run.

    ``prices`` holds the contract-1 settlements from a week before the
    missing day to the trade's exit. ``fill`` is the run's
    :class:`chan.commodity_seasonals.GapFill` for that day, which carries the
    straight-line guess, its typical miss, the rows around the gap and the
    exit price.
    """

    prices: tuple[tuple[date, Decimal], ...]
    fill: seasonals.GapFill

    @property
    def top(self) -> float:
        return self.fill.linear + self.fill.linear_error

    @property
    def bottom(self) -> float:
        return self.fill.linear - self.fill.linear_error

    @classmethod
    def from_run(cls) -> GuessFigures:
        fill = seasonals.gap_fills()[0]
        one = seasonals.settlements(seasonals.HARBOR_GASOLINE)[1]
        first = fill.day - timedelta(days=7)
        last = seasonals.gasoline_trade(fill.year).exit_day
        return cls(prices=tuple((d, one[d]) for d in sorted(one) if first <= d <= last), fill=fill)


#: Where the days run across the board, the price scale's height, and the
#: band's half width.
GUESS_X = (0.7, 9.3)
GUESS_Y = (0.85, 3.9)
BAND_HALF = 0.3
#: The gap between the strokes that fill the band.
BAND_STEP = 0.07


def _guess_x(day: date, f: GuessFigures) -> float:
    """Where ``day`` sits, one step per trading day, as the straight-line guess weights them.

    Spacing by calendar days would put the guess off the line it lies on,
    because a weekend counts there and not in the fill.
    """
    first, last = f.prices[0][0], f.prices[-1][0]
    span = seasonals._trading_days_between(first, last)
    step = seasonals._trading_days_between(first, day)
    return GUESS_X[0] + step * (GUESS_X[1] - GUESS_X[0]) / span


def _guess_scale(f: GuessFigures) -> tuple[float, float]:
    """The prices at the bottom and the top of the scale, a margin past the band and every price."""
    prices = [float(p) for _, p in f.prices]
    return min(*prices, f.bottom) - 0.007, max(*prices, f.top) + 0.005


def _guess_y(price: float, f: GuessFigures) -> float:
    lo, hi = _guess_scale(f)
    return GUESS_Y[0] + (float(price) - lo) * (GUESS_Y[1] - GUESS_Y[0]) / (hi - lo)


def _band(x0: float, y0: float, x1: float, y1: float) -> tuple:
    """A box filled with close horizontal strokes, drawn as one zigzag from the bottom up."""
    points, y, right = [(x0, y0)], y0, True
    while y < y1:
        points.append((x1 if right else x0, y))
        y = min(y + BAND_STEP, y1)
        points.append((x1 if right else x0, y))
        right = not right
    points.append((x1 if right else x0, y1))
    return _line(points, per_unit=4)


def _interpolation_guess(f: GuessFigures) -> Scene:
    """Lesson 2: the straight-line guess for the missing entry, and the band of
    one typical miss around it, which reaches past the exit price."""
    fill, one = f.fill, dict(f.prices)
    gx, exit_y = _guess_x(fill.day, f), _guess_y(fill.other, f)
    last = f.prices[-1][0]
    steps: list[Stroke | Label] = [
        _stroke("axis", _line([(0.4, 0.7), (9.6, 0.7)]), color=MUTED, frames=6),
        Stroke(
            "prices",
            np.array([_guess_x(d, f) for d, _ in f.prices]),
            np.array([_guess_y(p, f) for _, p in f.prices]),
            color=INK,
            frames=8,
            dots=6.0,
        ),
        Label(
            f"{GASOLINE_TRADE}, {fill.day:%B} {fill.year}",
            9.6,
            0.35,
            names="axis",
            color=MUTED,
            size=11,
            ha="right",
        ),
        Label(
            f"{fill.day:%b} {fill.day.day}, the {fill.leg}: no row",
            gx,
            0.35,
            names="axis",
            color=MUTED,
            size=11,
            ha="center",
        ),
        _stroke(
            "exit",
            _line([(gx - 0.6, exit_y), (_guess_x(last, f) + 0.25, exit_y)]),
            color=MUTED,
            dashed=True,
            frames=6,
        ),
        Label(
            f"exit price {fill.other}",
            gx - BAND_HALF - 0.45,
            exit_y - 0.3,
            names="exit",
            color=MUTED,
            size=11,
            ha="right",
        ),
        _stroke(
            "line",
            _line(
                [
                    (_guess_x(fill.before, f), _guess_y(one[fill.before], f)),
                    (_guess_x(fill.after, f), _guess_y(one[fill.after], f)),
                ]
            ),
            color=ACCENT,
            frames=6,
        ),
        Stroke(
            "guess",
            np.array([gx]),
            np.array([_guess_y(fill.linear, f)]),
            color=ACCENT,
            frames=1,
            dots=9.0,
        ),
        Label(
            f"straight-line guess {fill.linear:.3f}",
            gx + BAND_HALF + 1.0,
            1.15,
            names="guess",
            color=ACCENT,
            size=11,
        ),
        _stroke(
            "loss-zone",
            _band(gx - BAND_HALF, exit_y, gx + BAND_HALF, _guess_y(f.top, f)),
            color=LOST,
            width=1.2,
            frames=10,
        ),
        _stroke(
            "profit-zone",
            _band(gx - BAND_HALF, _guess_y(f.bottom, f), gx + BAND_HALF, exit_y),
            color=GOOD,
            width=1.2,
            frames=10,
        ),
        Label(
            f"{f.top:.3f}",
            gx + BAND_HALF + 0.2,
            _guess_y(f.top, f) - 0.05,
            names="loss-zone",
            color=MUTED,
            size=10,
        ),
        Label(
            f"{f.bottom:.3f}",
            gx + BAND_HALF + 0.2,
            _guess_y(f.bottom, f) - 0.05,
            names="profit-zone",
            color=MUTED,
            size=10,
        ),
        Label(
            "one typical miss either side",
            gx - BAND_HALF - 0.25,
            _guess_y(f.top, f) + 0.05,
            names="loss-zone",
            color=INK,
            size=11,
            ha="right",
        ),
        Label(
            "entry here: a loss",
            gx - BAND_HALF - 0.45,
            (_guess_y(f.top, f) + exit_y) / 2 - 0.05,
            names="loss-zone",
            color=LOST,
            size=11,
            ha="right",
        ),
        Label(
            "entry here: a profit",
            gx - BAND_HALF - 0.25,
            _guess_y(f.bottom, f) + 0.15,
            names="profit-zone",
            color=GOOD,
            size=11,
            ha="right",
        ),
    ]
    return Scene("Interpolating turns a gap into a guess", "interpolation_guess", tuple(steps))


# --- Lesson 2: what Chan's 19 needs ------------------------------------------

#: The two bars' left end, their heights and their half thickness.
BAR_X0, BAR_X1 = 1.2, 9.6
CHAN_Y, FILES_Y, BAR_HALF = 3.0, 1.8, 0.32


def _bar_x(count: float, f: GasolineFigures) -> float:
    """Where ``count`` years along a bar of all the years ends."""
    return BAR_X0 + count * (BAR_X1 - BAR_X0) / len(f.years)


def _chan_needs_gaps(f: GasolineFigures) -> Scene:
    """Lesson 2: Chan's 19 profits reach past the files' 16 by exactly the
    missing years, so each missing year must have been a profit."""
    won, total = GASOLINE_COUNT
    files_won, gaps = len(f.won), _consecutive(f.gaps)[0]
    ch, fi, h = CHAN_Y, FILES_Y, BAR_HALF
    g0, g1 = _bar_x(files_won, f), _bar_x(files_won + len(f.gaps), f)
    l0 = _bar_x(files_won + len(f.gaps), f)
    steps: list[Stroke | Label] = [
        _stroke(
            "chan-won", _box(_bar_x(0, f), ch - h, _bar_x(won, f), ch + h), color=GOOD, frames=8
        ),
        Label(
            f"{won} profits",
            (_bar_x(0, f) + _bar_x(won, f)) / 2,
            ch,
            names="chan-won",
            color=GOOD,
            size=11,
            ha="center",
        ),
        _stroke(
            "chan-lost",
            _box(_bar_x(won, f), ch - h, _bar_x(total, f), ch + h),
            color=LOST,
            frames=4,
        ),
        Label("Chan", 0.25, ch, names="chan-won", color=INK, size=12),
        _stroke(
            "files-won",
            _box(_bar_x(0, f), fi - h, _bar_x(files_won, f), fi + h),
            color=GOOD,
            frames=8,
        ),
        Label(
            f"{files_won} profits",
            (_bar_x(0, f) + _bar_x(files_won, f)) / 2,
            fi,
            names="files-won",
            color=GOOD,
            size=11,
            ha="center",
        ),
        _stroke("files-gap", _box(g0, fi - h, g1, fi + h), color=MUTED, dashed=True, frames=6),
        _stroke(
            "files-lost", _box(l0, fi - h, _bar_x(len(f.years), f), fi + h), color=LOST, frames=4
        ),
        Label("EIA", 0.3, fi, names="files-won", color=INK, size=12),
        Label(
            f"{total - won} losses",
            (_bar_x(won, f) + _bar_x(total, f)) / 2,
            ch + h + 0.3,
            names="chan-lost",
            color=LOST,
            size=11,
            ha="center",
        ),
        Label(
            ", ".join(str(year) for year in f.lost),
            (l0 + _bar_x(len(f.years), f)) / 2,
            fi - h - 0.3,
            names="files-lost",
            color=LOST,
            size=11,
            ha="center",
        ),
        Label("no row", (g0 + g1) / 2, fi, names="files-gap", color=MUTED, size=10, ha="center"),
        _stroke(
            "needs",
            _arrow((g0 + g1) / 2 - 1.2, fi - h - 0.75, (g0 + g1) / 2 - 0.05, fi - h - 0.08),
            color=ACCENT,
            frames=4,
        ),
        Label(
            f"{gaps[0]} to {gaps[-1]} must all be profits for Chan’s {won}",
            (g0 + g1) / 2 - 1.3,
            fi - h - 1.05,
            names="needs",
            color=ACCENT,
            size=11,
            ha="right",
        ),
    ]
    steps.append(
        Label(GASOLINE_TRADE, 9.7, 0.43, names="files-won", color=MUTED, size=11, ha="right")
    )
    title = f"Chan’s {won} needs all {WORDS[len(f.gaps)]} gaps to be profits"
    return Scene(title, "chan_needs_gaps", tuple(steps))


# --- Lesson 2: fill 2 carries June's move ------------------------------------


@dataclass(frozen=True)
class FillTwoFigures:
    """What the fill 2 sketch draws, read from the gasoline run.

    ``may`` and ``june`` hold the contract-1 and contract-2 settlements from
    the trading day before the June fill's base to three trading days after
    the gap. ``fill`` is the run's :class:`chan.commodity_seasonals.GapFill`
    for the gap.
    """

    may: tuple[tuple[date, Decimal], ...]
    june: tuple[tuple[date, Decimal], ...]
    fill: seasonals.GapFill

    @property
    def window(self) -> tuple[date, date]:
        return seasonals._step(self.fill.base, -1), seasonals._step(self.fill.day, 3)

    @property
    def top(self) -> float:
        return self.fill.june + self.fill.june_error

    @property
    def bottom(self) -> float:
        return self.fill.june - self.fill.june_error

    @classmethod
    def from_run(cls) -> FillTwoFigures:
        fill = seasonals.gap_fills()[0]
        first, last = seasonals._step(fill.base, -1), seasonals._step(fill.day, 3)
        one = seasonals.settlements(seasonals.HARBOR_GASOLINE)[1]
        two = seasonals.settlements(seasonals.HARBOR_GASOLINE_2)[1]
        return cls(
            may=tuple((d, one[d]) for d in sorted(one) if first <= d <= last),
            june=tuple((d, two[d]) for d in sorted(two) if first <= d <= last),
            fill=fill,
        )


#: Where the fill 2 sketch's days run, leaving room at the left for the two
#: series' names, and a June ring's radius.
FILL_TWO_X = (1.15, 9.25)
RING = 0.075


def _fill_two_x(day: date, f: FillTwoFigures) -> float:
    """Where ``day`` sits, one step per trading day."""
    first, last = f.window
    span = seasonals._trading_days_between(first, last)
    step = seasonals._trading_days_between(first, day)
    return FILL_TWO_X[0] + step * (FILL_TWO_X[1] - FILL_TWO_X[0]) / span


def _fill_two_y(price: float, f: FillTwoFigures) -> float:
    prices = [float(p) for _, p in f.may + f.june]
    lo, hi = min(*prices, f.bottom) - 0.004, max(*prices, f.top) + 0.004
    return GUESS_Y[0] + (float(price) - lo) * (GUESS_Y[1] - GUESS_Y[0]) / (hi - lo)


def _ring(gid: str, x: float, y: float) -> Stroke:
    """June's mark, a hollow circle drawn as one stroke, so it differs from
    May's dots by shape as well as by ink."""
    t = np.linspace(0, 2 * np.pi, 17)
    return Stroke(gid, x + RING * np.cos(t), y + RING * np.sin(t), color=MUTED, width=1.6, frames=2)


def _june_move_fill(f: FillTwoFigures) -> Scene:
    """Lesson 2: June's rise across the gap, added to May's last price, is fill
    2's guess, and fill 2's typical miss around it still reaches the exit."""
    fill, one, two = f.fill, dict(f.may), dict(f.june)
    x = lambda day: _fill_two_x(day, f)  # noqa: E731
    y = lambda price: _fill_two_y(price, f)  # noqa: E731
    gx, bx, exit_y = x(fill.day), x(fill.base), y(fill.other)
    rise = two[fill.day] - two[fill.base]
    steps: list[Stroke | Label] = [
        _stroke("axis", _line([(0.4, 0.7), (9.6, 0.7)]), color=MUTED, frames=6),
        Stroke(
            "may",
            np.array([x(d) for d, _ in f.may]),
            np.array([y(p) for _, p in f.may]),
            color=INK,
            frames=min(8, len(f.may) - 1),
            dots=6.0,
        ),
        *[_ring(f"june-{k}", x(d), y(p)) for k, (d, p) in enumerate(f.june)],
        Label(
            "May",
            x(f.may[0][0]) - 0.28,
            y(f.may[0][1]) + 0.05,
            names="may",
            color=INK,
            size=11,
            ha="right",
        ),
        Label(
            "June",
            x(f.june[0][0]) - 0.28,
            y(f.june[0][1]) - 0.22,
            names="june-0",
            color=MUTED,
            size=11,
            ha="right",
        ),
        Label("dot: May   ring: June", 0.3, 0.35, names="june-0", color=MUTED, size=11),
        Label("gasoline", 9.7, 0.35, names="may", color=MUTED, size=11, ha="right"),
        Label(
            f"{fill.day:%b} {fill.day.day}, the {fill.leg}: no May row",
            gx,
            0.35,
            names="axis",
            color=MUTED,
            size=11,
            ha="center",
        ),
        _stroke(
            "june-rise",
            _arrow(bx, y(two[fill.base]), gx - 0.12, y(two[fill.day])),
            color=MUTED,
            frames=6,
        ),
        Label(
            f"June rose {100 * float(rise):.1f}¢",
            3.8,
            1.25,
            names="june-rise",
            color=MUTED,
            size=11,
            ha="center",
        ),
        _stroke(
            "may-rise",
            _arrow(bx, y(one[fill.base]), gx - 0.12, y(fill.june)),
            color=ACCENT,
            frames=6,
        ),
        Stroke("guess", np.array([gx]), np.array([y(fill.june)]), color=ACCENT, frames=1, dots=9.0),
        Label(
            f"same rise on May: guess {fill.june:.3f}",
            3.3,
            (y(one[fill.base]) + y(fill.june)) / 2 + 0.55,
            names="may-rise",
            color=ACCENT,
            size=11,
            ha="center",
        ),
        _stroke(
            "exit", _line([(gx - 0.8, exit_y), (9.6, exit_y)]), color=MUTED, dashed=True, frames=6
        ),
        Label(
            f"exit price {fill.other}",
            9.6,
            exit_y - 0.3,
            names="exit",
            color=MUTED,
            size=11,
            ha="right",
        ),
        _stroke(
            "loss-zone",
            _band(gx - BAND_HALF, exit_y, gx + BAND_HALF, y(f.top)),
            color=LOST,
            width=1.2,
            frames=10,
        ),
        _stroke(
            "profit-zone",
            _band(gx - BAND_HALF, y(f.bottom), gx + BAND_HALF, exit_y),
            color=GOOD,
            width=1.2,
            frames=10,
        ),
        Label(
            f"{f.top:.3f}",
            gx - BAND_HALF - 0.2,
            y(f.top) - 0.05,
            names="loss-zone",
            color=MUTED,
            size=10,
            ha="right",
        ),
        Label(
            f"{f.bottom:.3f}",
            gx + BAND_HALF + 0.2,
            y(f.bottom) - 0.15,
            names="profit-zone",
            color=MUTED,
            size=10,
        ),
        Label(
            "fill 2’s typical miss either side",
            gx,
            y(f.top) + 0.35,
            names="loss-zone",
            color=INK,
            size=11,
            ha="center",
        ),
        Label(
            "entry here: a loss",
            gx + BAND_HALF + 0.2,
            exit_y + 0.3,
            names="loss-zone",
            color=LOST,
            size=11,
        ),
        Label(
            "entry here: a profit",
            gx + BAND_HALF + 0.2,
            2.3,
            names="profit-zone",
            color=GOOD,
            size=11,
        ),
    ]
    return Scene("Fill 2 carries June’s move across the gap", "june_move_fill", tuple(steps))


# --- Lesson 2: each fill's miss against each year's move ---------------------

#: Where zero cents sits, how wide a cent is, the scale's ends in cents, and
#: the first year's row with the step down to each next one.
MISS_ZERO_X, MISS_CENT = 5.2, 2.6
MISS_SCALE = (-1.5, 1.7)
MISS_TOP, MISS_STEP = 3.0, 0.85


def _cents_x(cents: float) -> float:
    return MISS_ZERO_X + cents * MISS_CENT


def _fill_misses(fills: tuple[seasonals.GapFill, ...]) -> Scene:
    """Lesson 2: for each missing year, the move fill 2's guess gives once
    corrected by its average miss, and the spread of its misses either side."""
    steps: list[Stroke | Label] = [
        _stroke(
            "zero",
            _line([(_cents_x(0), 0.75), (_cents_x(0), 3.85)]),
            color=MUTED,
            dashed=True,
            frames=6,
        ),
        Label("loss", _cents_x(0) - 0.25, 3.7, names="zero", color=LOST, size=11, ha="right"),
        Label("profit", _cents_x(0) + 0.25, 3.7, names="zero", color=GOOD, size=11),
    ]
    for k, fill in enumerate(fills):
        row = MISS_TOP - k * MISS_STEP
        move, miss = 100 * fill.move(fill.june_corrected), 100 * fill.june_spread
        steps += [
            _stroke(
                f"miss-{fill.year}",
                _span(_cents_x(move - miss), _cents_x(move + miss), row, tick=0.1),
                color=INK,
                frames=6,
            ),
            Stroke(
                f"move-{fill.year}",
                np.array([_cents_x(move)]),
                np.array([row]),
                color=ACCENT,
                frames=1,
                dots=8.0,
            ),
            Label(
                f"σ = {miss:.2f}",
                _cents_x(move + miss / 2),
                row + 0.31,
                names=f"miss-{fill.year}",
                color=INK,
                size=10,
                ha="center",
            ),
            Label(str(fill.year), 0.3, row, names=f"miss-{fill.year}", color=INK, size=12),
            Label(
                f"{100 * fill.june_chance:.0f}%",
                9.7,
                row,
                names=f"miss-{fill.year}",
                color=MUTED,
                size=11,
                ha="right",
            ),
        ]
    first = fills[0].year
    steps += [
        _stroke(
            "scale",
            _line([(_cents_x(MISS_SCALE[0]), 0.75), (_cents_x(MISS_SCALE[1]), 0.75)]),
            color=MUTED,
            frames=6,
        ),
        *[
            Label(f"{c:+d}", _cents_x(c), 0.33, names="scale", color=MUTED, size=10, ha="center")
            for c in (-1, 1)
        ],
        Label("cents a gallon", 0.3, 0.33, names="scale", color=MUTED, size=10),
        Label("chance of profit", 9.7, 3.7, names="zero", color=MUTED, size=11, ha="right"),
        Label(
            "dot: the corrected move",
            0.3,
            3.75,
            names=f"move-{first}",
            color=ACCENT,
            size=10,
        ),
        Label(
            "bar: σ, fill 2’s spread, either side",
            0.3,
            3.45,
            names=f"miss-{first}",
            color=INK,
            size=10,
        ),
    ]
    steps.append(
        Label(GASOLINE_TRADE, MISS_ZERO_X, 0.33, names="scale", color=MUTED, size=10, ha="center")
    )
    return Scene("Each corrected move against fill 2’s spread", "fill_misses", tuple(steps))


# --- Lesson 4: which numbered file holds June --------------------------------

#: The year whose entry comes before March's last trading day, and the year
#: whose entry comes after it, in the order the sketch draws them.
STILL_TRADING_YEAR, EXPIRED_YEAR = 2008, 2006
#: The contracts each year's bars draw, by delivery month, June last.
MONTHS = (3, 4, 5, 6)
MONTH_NAMES = {3: "March", 4: "April", 5: "May", 6: "June"}


@dataclass(frozen=True)
class JuneYear:
    """One year's natural gas trade as the calendar sketch draws it.

    ``last_trade`` holds the March, April, May and June contracts' last
    trading days, and ``entry_number`` and ``exit_number`` the numbered file
    that holds June on the entry and exit days.
    """

    year: int
    entry: date
    exit: date
    last_trade: tuple[date, ...]
    entry_number: int
    exit_number: int

    @property
    def march_trading(self) -> bool:
        """Whether March still trades at the entry's close, its own last day included."""
        return self.entry <= self.last_trade[0]

    @classmethod
    def from_run(cls, year: int) -> JuneYear:
        trade = seasonals.natural_gas_trade(year)
        return cls(
            year=year,
            entry=trade.entry_day,
            exit=trade.exit_day,
            last_trade=tuple(ng_last_trade(year, month) for month in MONTHS),
            entry_number=seasonals.june_contract_number(trade.entry_day),
            exit_number=seasonals.june_contract_number(trade.exit_day),
        )


#: The calendar the bars run on, by month and day. A leap year holds every
#: day either drawn year can, so February 29 has a place too.
CALENDAR = (date(2008, 2, 20), date(2008, 5, 1))
CALENDAR_X = (1.75, 9.4)
#: The gap between one year's rows, March at the top, and each year's top row.
ROW_GAP = 0.29
YEAR_TOPS = (3.75, 2.0)
#: Where the March note starts, clear of both years' entry lines.
MARCH_NOTE_X = 2.95
#: How far each month's name sits left of its bar, how far an entry or exit
#: line runs past the top and bottom bars, and how far below that line's foot
#: its count sits.
MONTH_LABEL_GAP = 0.2
LINE_PAST = 0.12
COUNT_DROP = 0.3


def _day_x(day: date) -> float:
    """Where ``day``'s month and day sit on :data:`CALENDAR`, whatever its year."""
    on = day.replace(year=CALENDAR[0].year)
    span = (CALENDAR[1] - CALENDAR[0]).days
    return CALENDAR_X[0] + (on - CALENDAR[0]).days * (CALENDAR_X[1] - CALENDAR_X[0]) / span


def _short_date(day: date) -> str:
    return f"{day:%b} {day.day}"


def _rows(top: float) -> tuple[float, ...]:
    return tuple(top - k * ROW_GAP for k in range(len(MONTHS)))


def _year_steps(f: JuneYear, top: float) -> list[Stroke | Label]:
    """One year's four bars, its March note, and a dashed line at its entry and
    exit, each with June's number and the date beneath it."""
    rows = _rows(top)
    tag = str(f.year)
    steps: list[Stroke | Label] = []
    for month, row, last in zip(MONTHS, rows, f.last_trade, strict=True):
        gid = f"{tag}-{MONTH_NAMES[month].lower()}"
        june = month == MONTHS[-1]
        if june:
            shape = _line(
                [
                    (CALENDAR_X[0], row),
                    (9.75, row),
                    (9.6, row + 0.08),
                    (9.75, row),
                    (9.6, row - 0.08),
                ]
            )
        else:
            end = _day_x(last)
            shape = _line([(CALENDAR_X[0], row), (end, row), (end, row + 0.09), (end, row - 0.09)])
        steps.append(
            _stroke(gid, shape, color=ACCENT if june else INK, width=3.0 if june else 2.2, frames=6)
        )
        steps.append(
            Label(
                MONTH_NAMES[month],
                CALENDAR_X[0] - MONTH_LABEL_GAP,
                row,
                names=gid,
                color=ACCENT if june else MUTED,
                size=10,
                ha="right",
            )
        )
    steps.append(Label(tag, 0.3, (rows[1] + rows[2]) / 2, names=f"{tag}-march", size=13))
    note = "March still trading" if f.march_trading else "March has expired"
    steps.append(Label(note, MARCH_NOTE_X, rows[0], names=f"{tag}-march", color=MUTED, size=10))
    for moment, day, number in (
        ("entry", f.entry, f.entry_number),
        ("exit", f.exit, f.exit_number),
    ):
        gid = f"{tag}-{moment}"
        x = _day_x(day)
        steps.append(
            _stroke(
                gid,
                _line([(x, rows[0] + LINE_PAST), (x, rows[-1] - LINE_PAST)], per_unit=10),
                color=MUTED,
                dashed=True,
                frames=4,
            )
        )
        words = "June is contract" if moment == "entry" else "contract"
        steps.append(
            Label(
                f"{words} {number} on {_short_date(day)}",
                x,
                rows[-1] - LINE_PAST - COUNT_DROP,
                names=gid,
                color=ACCENT,
                size=11,
                ha="center",
            )
        )
    return steps


def _june_file(still: JuneYear, expired: JuneYear) -> Scene:
    """Lesson 4: June's number is how many contracts are still trading that day."""
    steps = _year_steps(still, YEAR_TOPS[0]) + _year_steps(expired, YEAR_TOPS[1])
    steps.append(
        Label(
            "June’s number is how many bars each line crosses",
            9.6,
            0.22,
            names=f"{expired.year}-exit",
            color=INK,
            size=12,
            ha="right",
        )
    )
    return Scene("Which file holds the June contract", "june_file", tuple(steps))


#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = (
    "streak_start",
    "gasoline_editions",
    "gap_range",
    "interpolation_guess",
    "chan_needs_gaps",
    "june_move_fill",
    "fill_misses",
    "june_file",
)
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


def june_years() -> tuple[JuneYear, JuneYear]:
    """The two years the calendar sketch draws, read from the run."""
    return JuneYear.from_run(STILL_TRADING_YEAR), JuneYear.from_run(EXPIRED_YEAR)


def scenes(
    streaks: StreakFigures | None = None,
    years: tuple[JuneYear, JuneYear] | None = None,
    gasoline: GasolineFigures | None = None,
    guess: GuessFigures | None = None,
    fill_two: FillTwoFigures | None = None,
) -> tuple[Scene, ...]:
    """The eight scenes in the order the post reads them, Lessons 1, 2 and 4."""
    streaks = streaks if streaks is not None else StreakFigures.from_run()
    years = years if years is not None else june_years()
    gasoline = gasoline if gasoline is not None else GasolineFigures.from_run()
    guess = guess if guess is not None else GuessFigures.from_run()
    fill_two = fill_two if fill_two is not None else FillTwoFigures.from_run()
    return (
        _streak_start(streaks),
        _gasoline_editions(gasoline),
        _gap_range(gasoline),
        _interpolation_guess(guess),
        _chan_needs_gaps(gasoline),
        _june_move_fill(fill_two),
        _fill_misses(tuple(seasonals.gap_fills())),
        _june_file(*years),
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


def make_commodity_seasonals_whiteboards(
    out_dir: Path | None = None,
    streaks: StreakFigures | None = None,
    years: tuple[JuneYear, JuneYear] | None = None,
    gasoline: GasolineFigures | None = None,
    guess: GuessFigures | None = None,
    fill_two: FillTwoFigures | None = None,
) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes(streaks, years, gasoline, guess, fill_two)]


def main() -> None:
    for path in make_commodity_seasonals_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
