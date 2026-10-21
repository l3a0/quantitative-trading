"""Whiteboard sketches for the commodity seasonals post, one for Lesson 1 and one for Lesson 4.

``blog/commodity-seasonals-lessons.md`` checks Chan's two commodity seasonal
trades against EIA's settlements. Two of its passages turn on a picture a
sentence has to build in the reader's head: where a count of profitable years
starts, and which numbered file holds the June contract on a given day. This
module draws those two as scenes, and the post places each right after the
paragraph it draws.

1. Where the count starts decides where a streak ends: a year axis from 1994
   to the first losing year, a dot for each profitable year and a cross for
   the loss, a dashed mark for the first edition's release in November 2008,
   brackets above the axis for the streaks of 13 and 14 counted from 1995 and
   brackets below for the same counts from 1994. It sits in Lesson 1, after
   the list of what the files rule out and cannot pick, which opens
   "1. **They rule out a count written for the revised edition.**".
2. Which file holds the June contract: the March, April, May and June natural
   gas contracts as bars on a calendar from late February to the start of
   May, each ending at its last trading day, for one year in which March is
   still trading on the entry date and one in which it has expired. A dashed
   line at each entry and exit crosses the contracts still trading that day,
   and June's number is how many it crosses, which its closing label says. It
   sits in Lesson 4, after the
   paragraph opening "For gasoline the answer is simple."

Both carry data, and neither needs the owner's archive.
:meth:`StreakFigures.from_run` reads every natural gas trade from the
committed EIA files through :func:`chan.commodity_seasonals.natural_gas_trades`
and counts its streaks with :func:`chan.commodity_seasonals.runs_ending`.
:meth:`JuneYear.from_run` reads one year's entry and exit days and file
numbers from :func:`chan.commodity_seasonals.natural_gas_trade`, and each
contract's last trading day from :func:`chan.futures.ng_last_trade`. Two
figures are the book's rather than the run's: the counts 13 and 14 Chan
prints, which the streak sketch looks up in the run's streaks, and the first
edition's release in November 2008, which the post cites.

The calendar sketch draws 2008 and 2006. In 2008 the entry, February 25, comes
two days before March's last trading day, so June is contract 4. In 2006 the
entry moves to Monday, February 27, after March's last day on the 24th, so
June is contract 3. 2007 is left out because its entry falls on March's own
last day, the edge case the post's third check of the expiry rule covers.
Both years' calendars are drawn on one axis of month and day.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look, frame rate, colours, pace
and hold. Only the scenes and the file names are this module's. Each GIF is
named :data:`GIF_PREFIX` plus the scene's slug, a prefix chosen so no GIF
name starts like the post's chart, ``commodity_seasonals_years.png``.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw both with::

    uv run python -m chan.commodity_seasonals_whiteboard
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import numpy as np

from chan import commodity_seasonals as seasonals
from chan.futures import ng_last_trade
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    Label,
    Scene,
    Stroke,
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


def june_years() -> tuple[JuneYear, JuneYear]:
    """The two years the calendar sketch draws, read from the run."""
    return JuneYear.from_run(STILL_TRADING_YEAR), JuneYear.from_run(EXPIRED_YEAR)


def scenes(
    streaks: StreakFigures | None = None, years: tuple[JuneYear, JuneYear] | None = None
) -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them, Lesson 1's then Lesson 4's."""
    streaks = streaks if streaks is not None else StreakFigures.from_run()
    years = years if years is not None else june_years()
    return (_streak_start(streaks), _june_file(*years))


def _write(scene: Scene, folder: Path) -> Path:
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
    return path


def make_commodity_seasonals_whiteboards(
    out_dir: Path | None = None,
    streaks: StreakFigures | None = None,
    years: tuple[JuneYear, JuneYear] | None = None,
) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes(streaks, years)]


def main() -> None:
    for path in make_commodity_seasonals_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
