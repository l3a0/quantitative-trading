"""Whiteboard sketches for the commodity seasonals post, for Lessons 1, 2, 4 and 5.

``blog/commodity-seasonals-lessons.md`` checks Chan's two commodity seasonal
trades against EIA's settlements. Seventeen of its passages turn on a picture a
sentence has to build in the reader's head: where a count of profitable years
starts, which edition each of gasoline's two claims was written for, what
three missing rows leave of a count, why a guessed price cannot stand in for a
missing one, what Chan's 19 needs of the missing years, how the second fill
carries June's move across a gap, which April days can test a fill, how its
misses lean and spread, how the lean looks April by April, why a miss
subtracts at an entry and adds at an exit, how far a fill misses against each
year's move, how far a Sharpe ratio from so few years can stray, why fewer
results widen a range, where natural gas's ±12% comes from, which later range
holds its earlier mean, how one year moves natural gas's mean but not its
ranks, and which numbered file holds the
June contract on a given day. This module draws those seventeen as scenes,
and the post places each right after the paragraph it draws.

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
   release, a purple bracket from 1995 to 2008 for the sidebar's profit every
   year since 1995, and a black bracket from 1995 to 2015 for the main text's
   19 of 21. The sidebar's bracket ends before the first loss, and the main
   text's runs past both. It sits in Lesson 1 after the paragraph opening
   "Gasoline’s main text says 19 profitable years".
3. Three missing rows leave a range, not a count: gasoline's years from 1995
   to 2015 with a span under the years with no row, then a scale of counts on
   which the files allow 16 to 19 profitable years and Chan's 19 sits at the
   top. It sits in Lesson 2 after the paragraph opening "EIA’s New York
   Harbor file holds no row".
4. Chan's 19 needs all three gaps to be profits: Chan's 21 years as one bar
   of 19 profits and 2 losses, and the files' as 16 profits, 3 years with no
   row and the 2 losses of 2009 and 2012, so the missing years sit under the
   end of Chan's profits. It sits after the paragraph opening "The losses say
   more than the gaps."
5. Interpolating turns a gap into a guess: the May gasoline contract's
   settlements around April 14, 1997, the entry day with no row, a straight
   line between the rows on either side and the guess it gives that day, and
   a band of one typical miss either side of the guess, split at the exit
   price into a part where the year is a loss and a part where it is a profit.
   It sits in the fill section, after the sentence opening "Fill 1 draws a
   straight line".
6. Fill 2 carries June's move across the gap: May's and June's settlements
   around April 14, 1997, May as dots and June as rings, June's rise from the
   last day both files hold to the gap day, the same rise added to May's
   price there to give fill 2's guess, and a band of fill 2's typical miss
   either side, split at the exit price. It sits after the sentence opening
   "Fill 2 takes May’s last known price".
7. Which April days can test a fill: four bars, the April trading days from
   1994 to 2005 narrowing to 1997's test days as each check removes days,
   with how many each check removes. It sits after the sentence opening "A
   pattern that reaches back fewer days".
8. One set of misses, three numbers: fill 2's misses on every test day of
   1997's pattern, stacked as dots on a scale in cents, with the average miss
   and a bar of the spread around it, and a bar of the typical miss around
   zero. It sits after the paragraph opening "Fill 2’s misses also lean one
   way."
9. Twelve Aprils lean low: each April's average miss from 1994 to 2005 as a
   bar from zero, with the number of test days that April. It sits after the
   paragraph opening "The test days overlap".
10. A miss at the entry subtracts, at the exit it adds: two panels, 1997's
   missing entry and 1998's missing exit, each with the known price, fill 2's
   guess, the guess lifted by fill 2's average miss, and brackets for the move
   with the guess and the move with the lifted guess, shorter for the entry
   and longer for the exit. It sits after the exit's derivation, which opens
   "```math".
11. Each corrected move against fill 2's spread: for each missing year, the
   year's move with fill 2's guess corrected by its average miss, a bar of the
   spread of its misses either side, and each year's chance of a profit. The
   bars for 1997 and 1998 cross zero and 1999's stops short. It sits after
   the paragraph opening "So the chance that all three years were profits".
12. How far each Sharpe ratio can stray: the four periods of the post's
   returns table, each trade before and after the book, as a dot at its
   Sharpe ratio and a bar 1.96 standard errors either side, against a dashed
   zero line. Both periods after the book reach across zero. It sits in
   Lesson 4, after the paragraph opening "For the four Sharpe ratios".
13. Fewer results, a wider range: Student's t's 95% multiplier as a bar for
   the post's 8 and 15 later years, for 30 results and for very many, against
   a dashed line at the normal curve's 1.96. It sits after the general range
   formula, which opens "```math".
14. Where ±12% comes from: natural gas's spread after 2008, divided by the
   root of its 15 years, times its multiplier, as three bars from one edge,
   against a dashed line at the gap to its earlier mean. It sits after that
   trade's worked range, which opens "```math".
15. One range holds the earlier mean, one does not: each period's mean and
   95% range, with each trade's earlier mean carried down as a dashed line
   past its later bar. It sits after the paragraph opening "That range,
   −6% to +2%, leaves out".
16. One year moves the mean, not the ranks: natural gas's returns from 2009
   to 2023 as dots on a percentage axis, with ticks at their mean and at
   their mean without the best year, 2022, and below them all 30 years from
   1994 to 2023 ranked worst to best, the earlier ones above a line and the
   later ones below it. A note names the two gains too close to zero for
   their side to show. It sits in Lesson 4, after the paragraph opening
   "Gasoline’s fall shows on both."
17. Which file holds the June contract: the March, April, May and June natural
   gas contracts as bars on a calendar from late February to the start of
   May, each ending at its last trading day, for one year in which March is
   still trading on the entry date and one in which it has expired. A dashed
   line at each entry and exit crosses the contracts still trading that day,
   and June's number is how many it crosses, which its closing label says. It
   sits in Lesson 5, after the paragraph opening "For gasoline the answer is
   simple."

All seventeen carry data, and none needs the owner's archive.
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
:func:`sharpe_rows` reads each period's Sharpe ratio and standard error from
:func:`chan.commodity_seasonals.sharpe_ratio` and
:func:`chan.commodity_seasonals.sharpe_standard_error`, and
:func:`mean_rows` reads each period's mean, spread, count and 95% range from
:func:`chan.commodity_seasonals.mean_interval`, and
:meth:`OneYearFigures.from_run` reads natural gas's yearly returns from
:func:`chan.commodity_seasonals.natural_gas_trades`.
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
than copied, so these GIFs share that post's look and frame rate. Their
colours are this post's own, from :mod:`chan.commodity_seasonals_figures`.
Each sketch carries more than a reader takes in at that post's pace, so
all seventeen are in :data:`PACED`, and :func:`sketch_timeline` holds each of their
labels longer and their finished drawings for twelve seconds, as
:mod:`chan.equity_seasonals_whiteboard` does for its slow sketches. Only
the scenes, the pacing and the file names are this module's. Each GIF is
named :data:`GIF_PREFIX` plus the scene's slug, a prefix chosen so no GIF
name starts like the post's chart, ``commodity_seasonals_years.png``.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw all seventeen with::

    uv run python -m chan.commodity_seasonals_whiteboard
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import numpy as np
from scipy import stats

from chan import commodity_seasonals as seasonals
from chan.commodity_seasonals_figures import ACCENT, GASOLINE_BOOK_END, GOOD, LOST
from chan.futures import ng_last_trade
from chan.paths import FIGURES_DIR
from chan.regime_figure import INK, MUTED
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

#: The inks every frame is mapped onto: the shared ink and grey, and this
#: post's own three colours in place of the shared ones.
INKS = (INK, MUTED, ACCENT, GOOD, LOST)

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
WORDS = {
    0: "none",
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
    11: "eleven",
    12: "twelve",
}

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
            f"exit price {_cents(fill.other)}",
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
            f"straight-line guess {_cents(fill.linear)}",
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
            f"{_cents(f.top)}",
            gx + BAND_HALF + 0.2,
            _guess_y(f.top, f) - 0.05,
            names="loss-zone",
            color=MUTED,
            size=10,
        ),
        Label(
            f"{_cents(f.bottom)}",
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
            f"same rise on May: guess {_cents(fill.june)}",
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
            f"exit price {_cents(fill.other)}",
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
            f"{_cents(f.top)}",
            gx - BAND_HALF - 0.2,
            y(f.top) - 0.05,
            names="loss-zone",
            color=MUTED,
            size=10,
            ha="right",
        ),
        Label(
            f"{_cents(f.bottom)}",
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


# --- Lesson 2: which April days can test a fill ------------------------------


@dataclass(frozen=True)
class NarrowingFigures:
    """What the test-day sketch draws: 1997's gap and how the April trading
    days narrow to its test days, as
    :func:`chan.commodity_seasonals.count_test_days` counts them."""

    fill: seasonals.GapFill
    counts: tuple[int, int, int, int]

    @classmethod
    def from_run(cls) -> NarrowingFigures:
        fill = seasonals.gap_fills()[0]
        return cls(fill=fill, counts=seasonals.count_test_days(fill))


#: The test-day sketch's bars: where each starts, how long the first one is,
#: each bar's height, and what each one keeps and what each drop loses.
NARROW_X0, NARROW_LONGEST = 0.5, 6.6
NARROW_ROWS = (3.4, 2.55, 1.7, 0.85)
NARROW_KEPT = (
    "April trading days, 1994 to 2005",
    "the pattern fits inside April",
    "May has all four prices",
    "June has both of fill 2’s prices",
)
NARROW_LOST = ("fall outside April", "lack a May price", "lack a June price")


def _narrow_end(count: int, f: NarrowingFigures) -> float:
    return NARROW_X0 + count * NARROW_LONGEST / f.counts[0]


def _test_days(f: NarrowingFigures) -> Scene:
    """Lesson 2: the April trading days of the test years, narrowed by each
    check a day must pass to test a fill in 1997's pattern."""
    steps: list[Stroke | Label] = []
    for k, (count, y, kept) in enumerate(zip(f.counts, NARROW_ROWS, NARROW_KEPT, strict=True)):
        ink = ACCENT if k == len(f.counts) - 1 else INK
        steps += [
            _stroke(
                f"stage-{k}",
                _line([(NARROW_X0, y), (_narrow_end(count, f), y)], per_unit=10),
                color=ink,
                width=9.0,
                frames=4,
            ),
            Label(kept, NARROW_X0, y + 0.4, names=f"stage-{k}", color=INK, size=11),
            Label(
                str(count),
                _narrow_end(count, f) + 0.3,
                y - 0.07,
                names=f"stage-{k}",
                color=ink,
                size=12,
            ),
        ]
        if k:
            steps.append(
                Label(
                    f"−{f.counts[k - 1] - count}: {NARROW_LOST[k - 1]}",
                    9.7,
                    y - 0.07,
                    names=f"stage-{k}",
                    color=LOST,
                    size=10,
                    ha="right",
                )
            )
    back, ahead, start = f.fill.steps
    steps += [
        Label(
            f"{f.fill.year}’s gap: rows {back} days back and {ahead} ahead, "
            f"fill 2 starts {start} back",
            0.3,
            0.25,
            names="stage-0",
            color=MUTED,
            size=10,
        ),
        Label(GASOLINE_TRADE, 9.7, 0.25, names="stage-0", color=MUTED, size=10, ha="right"),
    ]
    return Scene("Which April days can test a fill", "test_days", tuple(steps))


# --- Lesson 2: how fill 2's misses lean and spread ---------------------------


@dataclass(frozen=True)
class MissFigures:
    """What the two miss sketches draw, read from the gasoline run.

    ``misses`` holds fill 2's miss on every test day of ``fill``'s pattern, as
    :func:`chan.commodity_seasonals.fill_two_misses` gives them: the day, the
    base the guess starts from, and the true price minus the guess in dollars
    a gallon.
    """

    fill: seasonals.GapFill
    misses: tuple[tuple[date, date, float], ...]

    @property
    def cents(self) -> list[float]:
        return [100 * miss for *_, miss in self.misses]

    @property
    def by_april(self) -> dict[int, list[float]]:
        found: dict[int, list[float]] = {}
        for day, _, miss in self.misses:
            found.setdefault(day.year, []).append(100 * miss)
        return found

    @classmethod
    def from_run(cls) -> MissFigures:
        fill = seasonals.gap_fills()[0]
        return cls(fill=fill, misses=tuple(seasonals.fill_two_misses(fill)))


#: The three-numbers sketch's scale: where zero sits and how wide a cent is,
#: the width of a stack of dots, and the height of the lowest dot and each
#: next one up.
MISS_DOT_ZERO_X, MISS_DOT_CENT = 3.6, 1.6
MISS_DOT_BIN = 0.2
MISS_DOT_BASE, MISS_DOT_STEP = 1.25, 0.17
MISS_SPREAD_Y, MISS_TYPICAL_Y = 3.75, 3.35


def _miss_x(cents: float) -> float:
    return MISS_DOT_ZERO_X + cents * MISS_DOT_CENT


def _miss_stacks(cents: list[float]) -> tuple[list[float], list[float]]:
    """Each miss's place: its bin of :data:`MISS_DOT_BIN` cents across, and
    its height in that bin's stack, smallest misses first."""
    counts: dict[float, int] = {}
    xs, ys = [], []
    for miss in sorted(cents):
        stack = round(miss / MISS_DOT_BIN) * MISS_DOT_BIN
        height = counts.get(stack, 0)
        counts[stack] = height + 1
        xs.append(_miss_x(stack))
        ys.append(MISS_DOT_BASE + height * MISS_DOT_STEP)
    return xs, ys


def _three_numbers(f: MissFigures) -> Scene:
    """Lesson 2: fill 2's misses on its test days, with their average and the
    spread around it, and the typical miss around zero."""
    cents = f.cents
    mean, spread = statistics.fmean(cents), statistics.stdev(cents)
    typical = math.sqrt(statistics.fmean(c * c for c in cents))
    xs, ys = _miss_stacks(cents)
    steps: list[Stroke | Label] = [
        _stroke(
            "zero",
            _line([(_miss_x(0), 1.15), (_miss_x(0), 3.95)]),
            color=MUTED,
            dashed=True,
            frames=6,
        ),
        Stroke("misses", np.array(xs), np.array(ys), color=INK, frames=8, dots=4.0),
        _stroke("scale", _line([(_miss_x(-2), 1.05), (_miss_x(3.4), 1.05)]), color=MUTED, frames=6),
        *[
            Label(
                f"{c:+d}" if c else "0",
                _miss_x(c),
                0.7,
                names="scale",
                color=MUTED,
                size=10,
                ha="center",
            )
            for c in (-2, -1, 0, 1, 2)
        ],
        Label("cents a gallon", 9.7, 0.7, names="scale", color=MUTED, size=10, ha="right"),
        Label(
            f"dot: one test day’s miss, {len(cents)} days",
            0.3,
            0.3,
            names="misses",
            color=INK,
            size=10,
        ),
        _stroke(
            "typical",
            _span(_miss_x(-typical), _miss_x(typical), MISS_TYPICAL_Y, tick=0.1),
            color=MUTED,
            frames=6,
        ),
        Label(
            f"typical miss ±{typical:.2f}, around zero",
            _miss_x(typical) + 0.2,
            MISS_TYPICAL_Y - 0.05,
            names="typical",
            color=MUTED,
            size=11,
        ),
        _stroke(
            "spread",
            _span(_miss_x(mean - spread), _miss_x(mean + spread), MISS_SPREAD_Y, tick=0.1),
            color=INK,
            frames=6,
        ),
        Stroke(
            "average",
            np.array([_miss_x(mean)]),
            np.array([MISS_SPREAD_Y]),
            color=ACCENT,
            frames=1,
            dots=9.0,
        ),
        Label(
            f"average {mean:+.2f}, spread ±{spread:.2f}",
            _miss_x(mean + spread) + 0.2,
            MISS_SPREAD_Y - 0.05,
            names="spread",
            color=ACCENT,
            size=11,
        ),
        Label(GASOLINE_TRADE, 9.7, 0.3, names="scale", color=MUTED, size=10, ha="right"),
    ]
    return Scene("One set of misses, three numbers", "three_numbers", tuple(steps))


#: The Aprils sketch's scale: where zero sits, how wide a cent is, and the
#: height of the first April's row and the step down to each next one.
APRIL_ZERO_X, APRIL_CENT = 3.0, 3.0
APRIL_TOP, APRIL_STEP = 3.78, 0.285


def _april_x(cents: float) -> float:
    return APRIL_ZERO_X + cents * APRIL_CENT


def _april_leans(f: MissFigures) -> Scene:
    """Lesson 2: each April's average miss, which leans low in most years and
    takes most of its size from a few."""
    by = f.by_april
    means = {year: statistics.fmean(cents) for year, cents in sorted(by.items())}
    high = sum(1 for mean in means.values() if mean > 0)
    steps: list[Stroke | Label] = [
        _stroke(
            "zero",
            _line([(_april_x(0), 0.55), (_april_x(0), 3.95)]),
            color=MUTED,
            dashed=True,
            frames=6,
        )
    ]
    for k, (year, mean) in enumerate(means.items()):
        row = APRIL_TOP - k * APRIL_STEP
        ink = ACCENT if mean > 0 else MUTED
        bar = (
            _stroke(
                f"april-{year}",
                _line([(_april_x(0), row), (_april_x(mean), row)], per_unit=40),
                color=ink,
                width=3.0,
                frames=1,
            )
            if abs(_april_x(mean) - _april_x(0)) > 0.05
            else Stroke(
                f"april-{year}",
                np.array([_april_x(mean)]),
                np.array([row]),
                color=ink,
                frames=1,
                dots=5.0,
            )
        )
        steps += [
            bar,
            Label(
                f"{year} ({len(by[year])})",
                0.3,
                row - 0.05,
                names=f"april-{year}",
                color=INK,
                size=9,
            ),
        ]
    steps += [
        Label(
            "left: May guessed too high", 9.7, 1.75, names="zero", color=MUTED, size=10, ha="right"
        ),
        Label("right: too low", 9.7, 1.45, names="zero", color=ACCENT, size=10, ha="right"),
        Label(
            "(n): test days that April", 9.7, 1.15, names="zero", color=MUTED, size=10, ha="right"
        ),
        Label(
            f"{high} of {len(means)} Aprils lean low",
            9.7,
            0.75,
            names="zero",
            color=INK,
            size=11,
            ha="right",
        ),
        Label(GASOLINE_TRADE, 9.7, 0.3, names="zero", color=MUTED, size=10, ha="right"),
    ]
    title = f"{WORDS[len(means)].capitalize()} Aprils, {WORDS[high]} lean low"
    return Scene(title, "april_leans", tuple(steps))


# --- Lesson 2: a miss at the entry subtracts, at the exit it adds -----------

#: Board units per cent on the miss-sign sketch's price scale, and the height
#: of each panel's lowest price.
SIGN_CENT, SIGN_BASE_Y = 3.0, 1.15
#: Where each panel starts, the entry gap's on the left and the exit gap's on
#: the right of the divider.
SIGN_PANELS = (0.45, 5.05)
SIGN_DIVIDER = 5.0


def _sign_y(price: float, f: seasonals.GapFill) -> float:
    """Where ``price`` sits in ``f``'s panel, the lowest of its three prices at the base."""
    lo = min(float(f.other), f.june, f.june + f.june_bias)
    return SIGN_BASE_Y + (price - lo) * 100 * SIGN_CENT


def _vspan(x: float, y0: float, y1: float, tick: float = 0.1) -> tuple:
    """An upright bracket from ``y0`` to ``y1`` with a tick at each end."""
    return _line(
        [(x - tick, y0), (x + tick, y0), (x, y0), (x, y1), (x - tick, y1), (x + tick, y1)],
        per_unit=10,
    )


def _cents(price: float) -> str:
    """A price in dollars a gallon, written in cents as the post's tables give it.

    The files spell a price to a tenth of a cent, so one decimal place keeps
    every digit and invents none.
    """
    return f"{100 * float(price):.1f}¢"


def _price_dot(gid: str, x: float, y: float, color: str) -> Stroke:
    return Stroke(gid, np.array([x]), np.array([y]), color=color, frames=1, dots=8.0)


def _sign_panel(f: seasonals.GapFill, x0: float, tag: str) -> list[Stroke | Label]:
    """One gap: the known price, the guess, the guess lifted by fill 2's average
    miss with that miss's size beside the arrow, and the move with each,
    measured on dashed guides."""
    entry_missing = f.leg == "entry"
    known, guess, lifted = float(f.other), f.june, f.june + f.june_bias
    y = lambda price: _sign_y(price, f)  # noqa: E731
    entry_x, exit_x = x0 + 1.4, x0 + 2.5
    gap_x, known_x = (entry_x, exit_x) if entry_missing else (exit_x, entry_x)
    m_x, c_x = x0 + 2.95, x0 + 3.65
    m_ends = (guess, known) if entry_missing else (known, guess)
    c_ends = (lifted, known) if entry_missing else (known, lifted)
    top = known == max(known, guess, lifted)
    return [
        _price_dot(f"{tag}-known", known_x, y(known), INK),
        Label(
            f"{f.year}: the {f.leg} is missing",
            x0 + 2.2,
            3.75,
            names=f"{tag}-known",
            color=INK,
            size=12,
            ha="center",
        ),
        Label(
            f"{'exit' if entry_missing else 'entry'} {_cents(f.other)}",
            known_x,
            y(known) + (0.36 if top else -0.4),
            names=f"{tag}-known",
            color=INK,
            size=11,
            ha="center",
        ),
        _price_dot(f"{tag}-guess", gap_x, y(guess), ACCENT),
        Label(
            f"guess {_cents(guess)}",
            gap_x - 0.3,
            y(guess) - 0.05,
            names=f"{tag}-guess",
            color=ACCENT,
            size=11,
            ha="right",
        ),
        _ring(f"{tag}-lifted", gap_x, y(lifted)),
        _stroke(
            f"{tag}-e",
            _arrow(gap_x, y(guess) + 0.12, gap_x, y(lifted) - 0.1),
            color=MUTED,
            frames=3,
        ),
        Label(
            f"e = {100 * f.june_bias:.2f}¢",
            gap_x - 0.3,
            (y(guess) + y(lifted)) / 2,
            names=f"{tag}-e",
            color=MUTED,
            size=11,
            ha="right",
        ),
        Label(
            "guess + e",
            gap_x - 0.3,
            y(lifted) + 0.05,
            names=f"{tag}-lifted",
            color=MUTED,
            size=11,
            ha="right",
        ),
        *[
            _stroke(
                f"{tag}-guide-{k}",
                _line([(x + 0.15, y(price)), (c_x + 0.1, y(price))]),
                color=MUTED,
                dashed=True,
                width=1.0,
                frames=3,
            )
            for k, (x, price) in enumerate(((known_x, known), (gap_x, guess), (gap_x, lifted)))
        ],
        _stroke(f"{tag}-m", _vspan(m_x, y(m_ends[0]), y(m_ends[1])), color=ACCENT, frames=4),
        Label("m", m_x, y(m_ends[0]) - 0.38, names=f"{tag}-m", color=ACCENT, size=12, ha="center"),
        _stroke(f"{tag}-c", _vspan(c_x, y(c_ends[0]), y(c_ends[1])), color=INK, frames=4),
        Label(
            "m − e" if entry_missing else "m + e",
            c_x,
            y(c_ends[0]) - 0.38,
            names=f"{tag}-c",
            color=INK,
            size=12,
            ha="center",
        ),
    ]


def _miss_sign(entry: seasonals.GapFill, exit_: seasonals.GapFill) -> Scene:
    """Lesson 2: the same upward miss shortens the move when the entry is
    missing and lengthens it when the exit is, drawn at fill 2's average miss."""
    steps: list[Stroke | Label] = [
        _stroke(
            "divider",
            _line([(SIGN_DIVIDER, 0.55), (SIGN_DIVIDER, 3.95)]),
            color=MUTED,
            dashed=True,
            frames=6,
        )
    ]
    steps += _sign_panel(entry, SIGN_PANELS[0], "entry")
    steps += _sign_panel(exit_, SIGN_PANELS[1], "exit")
    steps += [
        Label("e drawn at fill 2’s average miss", 0.3, 0.3, names="entry-e", color=MUTED, size=10),
        Label(GASOLINE_TRADE, 9.7, 0.3, names="divider", color=MUTED, size=10, ha="right"),
    ]
    return Scene("A miss at the entry subtracts, at the exit it adds", "miss_sign", tuple(steps))


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


# --- Lesson 4: how far each Sharpe ratio can stray -------------------------

#: The returns table's four periods, each trade before and after the book.
PERIODS = (
    ("natural gas", 1994, 2008),
    ("natural gas", 2009, 2023),
    ("gasoline", 1995, 2015),
    ("gasoline", 2016, 2023),
)


def _period_trades(trade: str, first: int, last: int) -> list[seasonals.Trade]:
    if trade == "natural gas":
        return seasonals.natural_gas_trades(first, last)
    return seasonals.gasoline_trades(first, last)


@dataclass(frozen=True)
class SharpeRow:
    """One period's Sharpe ratio and its standard error, from the run."""

    trade: str
    first: int
    last: int
    ratio: float
    error: float

    @property
    def low(self) -> float:
        return self.ratio - 1.96 * self.error

    @property
    def high(self) -> float:
        return self.ratio + 1.96 * self.error


def sharpe_rows() -> tuple[SharpeRow, ...]:
    rows = []
    for trade, first, last in PERIODS:
        trades = _period_trades(trade, first, last)
        rows.append(
            SharpeRow(
                trade,
                first,
                last,
                seasonals.sharpe_ratio(trades),
                seasonals.sharpe_standard_error(trades),
            )
        )
    return tuple(rows)


#: Where a Sharpe ratio of zero sits, how wide a unit is, the scale's ends,
#: and the first row with the step down to each next one.
SHARPE_ZERO_X, SHARPE_UNIT = 5.9, 1.75
SHARPE_SCALE = (-1.5, 2.0)
SHARPE_TOP, SHARPE_STEP = 3.05, 0.62
SHARPE_AXIS_Y = 0.75


def _one_place(value: float) -> str:
    """``value`` to one place, with no sign on a value that rounds to zero."""
    text = f"{value:.1f}"
    return "0.0" if text == "-0.0" else text


def _sharpe_x(ratio: float) -> float:
    return SHARPE_ZERO_X + ratio * SHARPE_UNIT


def _sharpe_ranges(rows: tuple[SharpeRow, ...]) -> Scene:
    """Lesson 4: each period's Sharpe ratio with 1.96 standard errors either side."""
    steps: list[Stroke | Label] = [
        _stroke(
            "zero",
            _line([(_sharpe_x(0), SHARPE_AXIS_Y), (_sharpe_x(0), 3.85)]),
            color=MUTED,
            dashed=True,
            frames=6,
        ),
        Label("loses", _sharpe_x(0) - 0.25, 3.7, names="zero", color=LOST, size=11, ha="right"),
        Label("earns", _sharpe_x(0) + 0.25, 3.7, names="zero", color=GOOD, size=11),
    ]
    for k, row in enumerate(rows):
        y, tag = SHARPE_TOP - k * SHARPE_STEP, f"{row.trade}-{row.first}"
        steps += [
            Label(
                f"{row.trade}, {row.first} to {row.last}", 0.3, y, names="zero", color=INK, size=11
            ),
            _stroke(
                f"range-{tag}",
                _span(_sharpe_x(row.low), _sharpe_x(row.high), y, tick=0.1),
                color=INK,
                frames=6,
            ),
            Stroke(
                f"ratio-{tag}",
                np.array([_sharpe_x(row.ratio)]),
                np.array([y]),
                color=ACCENT,
                frames=1,
                dots=8.0,
            ),
            Label(
                _one_place(row.ratio),
                _sharpe_x(row.ratio) + (0.2 if row.ratio >= 0 else -0.2),
                y + 0.3,
                names=f"ratio-{tag}",
                color=ACCENT,
                size=10,
                ha="left" if row.ratio >= 0 else "right",
            ),
        ]
    first = f"{rows[0].trade}-{rows[0].first}"
    steps += [
        _stroke(
            "scale",
            _line(
                [
                    (_sharpe_x(SHARPE_SCALE[0]), SHARPE_AXIS_Y),
                    (_sharpe_x(SHARPE_SCALE[1]), SHARPE_AXIS_Y),
                ]
            ),
            color=MUTED,
            frames=6,
        ),
        *[
            Label(f"{v:+d}", _sharpe_x(v), 0.4, names="scale", color=MUTED, size=10, ha="center")
            for v in (-1, 1, 2)
        ],
        Label("Sharpe ratio", 0.3, 0.4, names="scale", color=MUTED, size=10),
        Label("dot: the Sharpe ratio", 0.3, 3.75, names=f"ratio-{first}", color=ACCENT, size=10),
        Label(
            "bar: 1.96 standard errors either side",
            0.3,
            3.45,
            names=f"range-{first}",
            color=INK,
            size=10,
        ),
    ]
    return Scene("How far each Sharpe ratio can stray", "sharpe_ranges", tuple(steps))


# --- Lesson 4: whether the mean return changed -------------------------------


@dataclass(frozen=True)
class MeanRow:
    """One period's yearly returns in percent: their mean, spread, count and 95% range."""

    trade: str
    first: int
    last: int
    mean: float
    spread: float
    count: int
    low: float
    high: float


def mean_rows() -> tuple[MeanRow, ...]:
    rows = []
    for trade, first, last in PERIODS:
        trades = _period_trades(trade, first, last)
        returns = [t.relative_change for t in trades if t.change is not None]
        low, high = seasonals.mean_interval(trades)
        rows.append(
            MeanRow(
                trade,
                first,
                last,
                100 * statistics.mean(returns),
                100 * statistics.stdev(returns),
                len(returns),
                float(100 * low),
                float(100 * high),
            )
        )
    return tuple(rows)


#: The percent axis: where 0% sits, how wide a point is, and the scale's ends.
MEAN_ZERO_X, MEAN_POINT = 5.75, 0.16
MEAN_SCALE = (-15.0, 20.0)


def _mean_x(pct: float) -> float:
    return MEAN_ZERO_X + pct * MEAN_POINT


def _mean_ranges(rows: tuple[MeanRow, ...]) -> Scene:
    """Lesson 4: each period's mean with its 95% range, and each trade's earlier
    mean carried down to see whether its later range holds it."""
    steps: list[Stroke | Label] = [
        _stroke(
            "zero",
            _line([(_mean_x(0), SHARPE_AXIS_Y), (_mean_x(0), 3.85)]),
            color=MUTED,
            dashed=True,
            frames=6,
        ),
        Label("0%", _mean_x(0) + 0.22, 3.75, names="zero", color=MUTED, size=10),
    ]
    for k, row in enumerate(rows):
        y, tag = SHARPE_TOP - k * SHARPE_STEP, f"{row.trade}-{row.first}"
        steps += [
            Label(
                f"{row.trade}, {row.first} to {row.last}", 0.3, y, names="zero", color=INK, size=11
            ),
            _stroke(
                f"range-{tag}",
                _span(_mean_x(row.low), _mean_x(row.high), y, tick=0.1),
                color=INK,
                frames=6,
            ),
            Stroke(
                f"mean-{tag}",
                np.array([_mean_x(row.mean)]),
                np.array([y]),
                color=ACCENT,
                frames=1,
                dots=8.0,
            ),
            Label(
                f"{row.mean:+.1f}%",
                9.7,
                y,
                names=f"mean-{tag}",
                color=ACCENT,
                size=11,
                ha="right",
            ),
        ]
    for before in (rows[0], rows[2]):
        k = rows.index(before)
        top, bottom = SHARPE_TOP - k * SHARPE_STEP, SHARPE_TOP - (k + 1) * SHARPE_STEP
        x, tag = _mean_x(before.mean), f"carry-{before.trade}"
        steps.append(
            _stroke(
                tag, _line([(x, top - 0.15), (x, bottom - 0.2)]), color=MUTED, dashed=True, frames=3
            )
        )
    steps += [
        _stroke(
            "scale",
            _line(
                [(_mean_x(MEAN_SCALE[0]), SHARPE_AXIS_Y), (_mean_x(MEAN_SCALE[1]), SHARPE_AXIS_Y)]
            ),
            color=MUTED,
            frames=6,
        ),
        *[
            Label(f"{v:+d}%", _mean_x(v), 0.4, names="scale", color=MUTED, size=10, ha="center")
            for v in (-10, 10, 20)
        ],
        Label("mean yearly return", 0.3, 0.4, names="scale", color=MUTED, size=10),
        Label(
            "dot: the mean",
            0.3,
            3.75,
            names=f"mean-{rows[0].trade}-{rows[0].first}",
            color=ACCENT,
            size=10,
        ),
        Label(
            "bar: 95% range   dashed: the earlier mean",
            0.3,
            3.45,
            names="carry-natural gas",
            color=INK,
            size=10,
        ),
    ]
    return Scene("One range holds the earlier mean, one does not", "mean_ranges", tuple(steps))


#: The multiplier chart: the bars' left edges, width and base, how tall a unit
#: is, and the count of results it sets beside the post's own for comparison.
T_BARS_X, T_BAR_WIDTH = (2.4, 4.2, 6.0, 7.8), 0.9
T_BASE, T_UNIT = 0.85, 0.92
T_COMPARE = 30


def _t_multiplier(counts: tuple[int, int]) -> Scene:
    """Lesson 4: the 95% multiplier Student's t gives for the post's two counts
    of later years, for :data:`T_COMPARE` results and for very many, against
    the normal curve's 1.96."""
    many = 1000
    normal = stats.norm.ppf(0.975)
    steps: list[Stroke | Label] = [
        _stroke("base", _line([(1.9, T_BASE), (9.2, T_BASE)]), color=MUTED, frames=6),
    ]
    sizes = (*counts, T_COMPARE, many)
    for x, n in zip(T_BARS_X, sizes, strict=True):
        t = stats.t.ppf(0.975, n - 1)
        top = T_BASE + t * T_UNIT
        ours = n in counts
        steps += [
            _stroke(
                f"bar-{n}",
                _box(x, T_BASE, x + T_BAR_WIDTH, top),
                color=ACCENT if ours else INK,
                frames=6,
            ),
            Label(
                f"{t:.2f}",
                x + T_BAR_WIDTH / 2,
                top + 0.3,
                names=f"bar-{n}",
                color=ACCENT if ours else INK,
                size=11,
                ha="center",
            ),
            Label(
                "many" if n == many else f"{n} results",
                x + T_BAR_WIDTH / 2,
                T_BASE - 0.33,
                names=f"bar-{n}",
                color=MUTED,
                size=10,
                ha="center",
            ),
        ]
    y = T_BASE + normal * T_UNIT
    steps += [
        _stroke("normal", _line([(2.25, y), (9.2, y)]), color=MUTED, dashed=True, frames=6),
        Label(f"normal, {normal:.2f}", 2.0, y, names="normal", color=MUTED, size=10, ha="right"),
        Label("95% multiplier from Student’s t", 0.3, 3.75, names="base", color=INK, size=10),
        Label(
            f"purple: the later periods’ {counts[0]} and {counts[1]} years",
            9.7,
            3.75,
            names="base",
            color=ACCENT,
            size=10,
            ha="right",
        ),
    ]
    return Scene("Fewer results, a wider range", "t_multiplier", tuple(steps))


#: The half-width build: where each bar starts, how wide a point is, and the rows.
HALF_X, HALF_POINT = 3.3, 0.27
HALF_ROWS = (3.2, 2.35, 1.5)


def _half_width(row: MeanRow, earlier: MeanRow) -> Scene:
    """Lesson 4: natural gas's half-width after 2008, built from its spread,
    against the gap to its earlier mean."""
    t = stats.t.ppf(0.975, row.count - 1)
    shrunk = row.spread / math.sqrt(row.count)
    half = t * shrunk
    gap = earlier.mean - row.mean
    widths = (row.spread, shrunk, half)
    texts = (
        f"spread s = {row.spread:.1f}%",
        f"s / √{row.count} = {shrunk:.1f}%",
        f"× {t:.2f} = {half:.1f}%",
    )
    steps: list[Stroke | Label] = []
    for k, (y, width, text) in enumerate(zip(HALF_ROWS, widths, texts, strict=True)):
        steps += [
            _stroke(
                f"half-{k}",
                _span(HALF_X, HALF_X + width * HALF_POINT, y, tick=0.1),
                color=ACCENT if k == 2 else INK,
                frames=6,
            ),
            Label(
                text,
                HALF_X - 0.25,
                y,
                names=f"half-{k}",
                color=ACCENT if k == 2 else INK,
                size=11,
                ha="right",
            ),
        ]
    x = HALF_X + gap * HALF_POINT
    steps += [
        Label(
            f"start: the later mean, {row.mean:+.1f}%",
            HALF_X,
            0.4,
            names="half-0",
            color=MUTED,
            size=10,
            ha="center",
        ),
        _stroke(
            "gap",
            _line([(x, HALF_ROWS[2] - 0.35), (x, HALF_ROWS[2] + 0.35)]),
            color=MUTED,
            dashed=True,
            frames=3,
        ),
        Label(
            f"the earlier mean, {gap:.1f} points higher",
            x,
            0.75,
            names="gap",
            color=MUTED,
            size=10,
            ha="center",
        ),
        Label(
            "natural gas, June contract, 2009 to 2023",
            9.7,
            3.85,
            names="half-0",
            color=MUTED,
            size=10,
            ha="right",
        ),
    ]
    return Scene(f"Where ±{half:.0f}% comes from", "half_width", tuple(steps))


def _mean_scenes(rows: tuple[MeanRow, ...]) -> tuple[Scene, Scene, Scene]:
    """The three sketches of whether the mean return changed, in the post's order."""
    gas_after, ng_before, ng_after = rows[3], rows[0], rows[1]
    return (
        _t_multiplier((gas_after.count, ng_after.count)),
        _half_width(ng_after, ng_before),
        _mean_ranges(rows),
    )


# --- Lesson 4: one year moves the mean, not the ranks -----------------------


@dataclass(frozen=True)
class OneYearFigures:
    """Natural gas's yearly returns in percent, before 2009 and after 2008, by year."""

    before: tuple[tuple[int, float], ...]
    after: tuple[tuple[int, float], ...]

    @property
    def best(self) -> tuple[int, float]:
        return max(self.after, key=lambda pair: pair[1])

    @property
    def mean_after(self) -> float:
        return statistics.mean(r for _, r in self.after)

    @property
    def mean_without_best(self) -> float:
        return statistics.mean(r for year, r in self.after if year != self.best[0])

    @classmethod
    def from_run(cls) -> OneYearFigures:
        def returns(first: int, last: int) -> tuple[tuple[int, float], ...]:
            trades = seasonals.natural_gas_trades(first, last)
            return tuple((t.year, 100 * t.relative_change) for t in trades if t.change is not None)

        return cls(before=returns(1994, 2008), after=returns(2009, 2023))


#: The return axis: where 0% sits, how wide a percentage point is, its ends,
#: how close two dots may sit on one level before the later one stacks above,
#: and the axis, dot and mean heights. Each dot sits at its true return, so
#: none lands on the wrong side of zero or of either mean tick.
YEAR_ZERO_X, YEAR_POINT = 3.52, 0.084
YEAR_SCALE = (-30.0, 70.0)
YEAR_DOT_GAP = 0.14
#: A gain this small, in points, sits too close to the zero line for its side to
#: show, so a label names it rather than leaving colour as the only cue.
YEAR_NEAR_ZERO = 1.0
YEAR_AXIS_Y, YEAR_DOT_BASE, YEAR_DOT_STEP = 2.6, 2.8, 0.17
YEAR_MEAN = (2.35, 2.6)
#: The ranks strip: its ends, and the before and after rows.
RANK_X = (1.9, 9.4)
RANK_BEFORE_Y, RANK_AFTER_Y = 1.3, 0.9


def _year_x(pct: float) -> float:
    return YEAR_ZERO_X + pct * YEAR_POINT


def _one_year(f: OneYearFigures) -> Scene:
    """Lesson 4: 2022 alone moves natural gas's mean after 2008, and moves its ranks by none."""
    best_year, best = f.best
    steps: list[Stroke | Label] = [
        _stroke(
            "axis",
            _line([(_year_x(YEAR_SCALE[0]), YEAR_AXIS_Y), (_year_x(YEAR_SCALE[1]), YEAR_AXIS_Y)]),
            color=MUTED,
            frames=6,
        ),
        _stroke(
            "zero",
            _line([(_year_x(0), YEAR_AXIS_Y - 0.1), (_year_x(0), 3.25)]),
            color=MUTED,
            dashed=True,
            frames=3,
        ),
        Label("0%", _year_x(0), 3.56, names="zero", color=MUTED, size=10, ha="center"),
        Label("returns, 2009 to 2023", 0.3, 3.75, names="axis", color=MUTED, size=10),
    ]
    placed: list[tuple[float, int]] = []
    for year, pct in sorted(f.after, key=lambda pair: pair[1]):
        x, level = _year_x(pct), 0
        while any(abs(x - px) < YEAR_DOT_GAP and pl == level for px, pl in placed):
            level += 1
        placed.append((x, level))
        steps.append(
            Stroke(
                f"year-{year}",
                np.array([x]),
                np.array([YEAR_DOT_BASE + level * YEAR_DOT_STEP]),
                color=GOOD if pct > 0 else LOST,
                frames=1,
                dots=8.0,
            )
        )
    near = sorted(year for year, pct in f.after if 0 < pct < YEAR_NEAR_ZERO)
    if near:
        steps.append(
            Label(
                " and ".join(str(year) for year in near) + ": just above 0%",
                _year_x(0) + 0.3,
                3.34,
                names=f"year-{near[-1]}",
                color=GOOD,
                size=10,
            )
        )
    steps += [
        Label(
            f"{best_year}: {best:+.0f}%",
            _year_x(best),
            3.16,
            names=f"year-{best_year}",
            color=GOOD,
            size=10,
            ha="center",
        ),
        _stroke(
            "mean",
            _line([(_year_x(f.mean_after), YEAR_MEAN[0]), (_year_x(f.mean_after), YEAR_MEAN[1])]),
            color=INK,
            frames=2,
        ),
        Label(
            f"mean {f.mean_after:+.1f}%",
            _year_x(f.mean_after) + 0.1,
            2.08,
            names="mean",
            color=INK,
            size=10,
        ),
        _stroke(
            "mean-without",
            _line(
                [
                    (_year_x(f.mean_without_best), YEAR_MEAN[0]),
                    (_year_x(f.mean_without_best), YEAR_MEAN[1]),
                ]
            ),
            color=ACCENT,
            frames=2,
        ),
        Label(
            f"without {best_year}: {f.mean_without_best:+.1f}%",
            _year_x(f.mean_without_best) - 0.1,
            2.08,
            names="mean-without",
            color=ACCENT,
            size=10,
            ha="right",
        ),
    ]
    ranked = sorted([(r, "before", y) for y, r in f.before] + [(r, "after", y) for y, r in f.after])
    step = (RANK_X[1] - RANK_X[0]) / (len(ranked) - 1)
    steps += [
        _stroke(
            "ranks",
            _line(
                [
                    (RANK_X[0], (RANK_BEFORE_Y + RANK_AFTER_Y) / 2),
                    (RANK_X[1], (RANK_BEFORE_Y + RANK_AFTER_Y) / 2),
                ]
            ),
            color=MUTED,
            frames=6,
        ),
        Label(
            "1994 to 2008",
            RANK_X[0] - 0.35,
            RANK_BEFORE_Y,
            names="ranks",
            color=INK,
            size=10,
            ha="right",
        ),
        Label(
            "2009 to 2023",
            RANK_X[0] - 0.35,
            RANK_AFTER_Y,
            names="ranks",
            color=ACCENT,
            size=10,
            ha="right",
        ),
    ]
    for k, (_, period, year) in enumerate(ranked):
        steps.append(
            Stroke(
                f"rank-{year}",
                np.array([RANK_X[0] + k * step]),
                np.array([RANK_BEFORE_Y if period == "before" else RANK_AFTER_Y]),
                color=INK if period == "before" else ACCENT,
                frames=1,
                dots=7.0,
            )
        )
    steps += [
        Label("worst", RANK_X[0], 0.5, names="ranks", color=MUTED, size=10, ha="center"),
        Label(
            f"best: {best_year}",
            RANK_X[1],
            0.5,
            names=f"rank-{best_year}",
            color=MUTED,
            size=10,
            ha="right",
        ),
        Label(
            f"ranked worst to best, {best_year} is the top rank however large its gain",
            0.3,
            1.75,
            names=f"rank-{best_year}",
            color=MUTED,
            size=10,
        ),
        Label(
            "natural gas, June contract", 9.7, 3.75, names="axis", color=MUTED, size=10, ha="right"
        ),
    ]
    return Scene("One year moves the mean, not the ranks", "one_year", tuple(steps))


# --- Lesson 5: which numbered file holds June --------------------------------

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
    """Lesson 5: June's number is how many contracts are still trading that day."""
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
    "chan_needs_gaps",
    "interpolation_guess",
    "june_move_fill",
    "test_days",
    "three_numbers",
    "april_leans",
    "miss_sign",
    "fill_misses",
    "sharpe_ranges",
    "mean_ranges",
    "t_multiplier",
    "half_width",
    "one_year",
    "june_file",
)
PACED_LABEL_MS, PACED_HOLD_MS = 900, 12000
#: Paced scenes the owner still found too fast, with each one's stroke frame
#: and label hold in milliseconds. Each has few steps, so the usual pace
#: finished it before a reader had followed it.
SLOWER = {"half_width": (250, 1800)}


def sketch_timeline(scene: Scene) -> list[Frame]:
    """:func:`timeline`'s frames, slowed for the scenes in :data:`PACED`, and
    slower still for those in :data:`SLOWER`."""
    frames = timeline(scene)
    if scene.slug not in PACED:
        return frames
    stroke_ms, label_ms = SLOWER.get(scene.slug, (None, PACED_LABEL_MS))

    def slowed(f: Frame) -> Frame:
        if f.partial == 0 and f.done and not isinstance(scene.steps[f.done - 1], Stroke):
            return Frame(f.done, f.partial, label_ms)
        if stroke_ms is not None and f.done + f.partial and f is not frames[0]:
            return Frame(f.done, f.partial, stroke_ms)
        return f

    paced = [slowed(f) for f in frames]
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
    misses: MissFigures | None = None,
    narrowing: NarrowingFigures | None = None,
) -> tuple[Scene, ...]:
    """The seventeen scenes in the order the post reads them, Lessons 1, 2, 4 and 5."""
    streaks = streaks if streaks is not None else StreakFigures.from_run()
    years = years if years is not None else june_years()
    gasoline = gasoline if gasoline is not None else GasolineFigures.from_run()
    guess = guess if guess is not None else GuessFigures.from_run()
    fill_two = fill_two if fill_two is not None else FillTwoFigures.from_run()
    misses = misses if misses is not None else MissFigures.from_run()
    narrowing = narrowing if narrowing is not None else NarrowingFigures.from_run()
    return (
        _streak_start(streaks),
        _gasoline_editions(gasoline),
        _gap_range(gasoline),
        _chan_needs_gaps(gasoline),
        _interpolation_guess(guess),
        _june_move_fill(fill_two),
        _test_days(narrowing),
        _three_numbers(misses),
        _april_leans(misses),
        _miss_sign(*seasonals.gap_fills()[:2]),
        _fill_misses(tuple(seasonals.gap_fills())),
        _sharpe_ranges(sharpe_rows()),
        *_mean_scenes(mean_rows()),
        _one_year(OneYearFigures.from_run()),
        _june_file(*years),
    )


def _write(scene: Scene, folder: Path) -> Path:
    frames = sketch_timeline(scene)
    first, *rest = render(scene, frames, INKS)
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
    misses: MissFigures | None = None,
    narrowing: NarrowingFigures | None = None,
) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [
        _write(scene, folder)
        for scene in scenes(streaks, years, gasoline, guess, fill_two, misses, narrowing)
    ]


def main() -> None:
    for path in make_commodity_seasonals_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
