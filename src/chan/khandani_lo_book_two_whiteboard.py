"""Whiteboard sketches for the post on Khandani and Lo's reversal on Chan's 2012 panel.

``blog/khandani-lo-reversal-lessons.md`` makes two claims that a sentence has
to build in the reader's head: Chan's match needs one stock's odd prices, and
the first book's rule pays its costs on the panel because the profit grew
while the trading did not. This module draws the two as scenes, and the post
places each right after the paragraph it draws. Neither is schematic. Every
figure either prints, and every place it puts a mark, is read from a run on
the committed files.

1. The bounce the rule bought, in Lesson 2, after the paragraph opening "One
   of them is not.": CAH's closes on 2009-08-31, 2009-09-01 and 2009-09-02
   as three dots on a price axis, to one scale. A black arrow down carries
   the fall's ratio, which the scale-break guard lets through, and a red
   arrow up the rise's, which it flags. A green mark under the middle dot is
   the weight Example 4.3 bought at that close, a green bracket beside the
   rise measures it and gives what that weight earned the next day, and a
   closing line gives Example 4.3's APR and Sharpe ratio without CAH. Its
   figures come from :class:`Bounce`, which reads
   :func:`chan.khandani_lo_book_two.close_to_close` on the committed panel.
2. Same trading, twenty times the profit, in Lesson 4, after the paragraph
   opening "So over 2006 the cost was": the first book's rule's average day
   on its own 2006 file and on the panel, as two pairs of bars on one scale
   in basis points of the rule's average gross position. A red bar is the
   day's cost and a green bar its profit. On 2006 a red hatched stretch runs
   from the profit's end to the cost's end, and on the panel a brown bracket
   runs from the cost's end to the profit's end, the part kept. The title's
   count is the ratio of the two profits, rounded to a whole number and
   spelled in words. Its figures come from :class:`AverageDays`, which reads
   :func:`chan.khandani_lo.daily_book` on both files.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look, frame rate and colours.
Each sketch carries more than a reader takes in at that post's pace, so both
are in :data:`PACED`, and :func:`sketch_timeline` holds each of their labels
longer and their finished drawings for twelve seconds, as
:mod:`chan.equity_seasonals_whiteboard` does for its slow sketches. Each GIF
is named :data:`GIF_PREFIX` plus the scene's slug, a prefix chosen so no GIF
name starts like the post's chart, ``khandani_lo_book_two.png``, or the small
caps post's sketches.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw both with::

    uv run python -m chan.khandani_lo_book_two_whiteboard
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from chan import khandani_lo
from chan.khandani_lo import ONE_WAY_COST, daily_book, reversal
from chan.khandani_lo_book_two import (
    BOOK_43_APR_PERCENT,
    BOOK_43_SHARPE,
    SOURCE_FILE,
    WINDOW_END,
    WINDOW_START,
    close_to_close,
    matches,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.series import SCALE_BREAK_BOUND, load_panel, scale_breaks
from chan.usdcad_tests_whiteboard import (
    Frame,
    Label,
    Scene,
    Stroke,
    _arrow,
    _dot,
    _hatched,
    _line,
    _stroke,
    render,
    timeline,
)

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "khandani_lo_book_two_sketch_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``khandani_lo_book_two_sketch_cah_bounce.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


def _frames(data_dir: Path | None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """The panel's closes and the first book's closes, read the way the run reads them."""
    _, panel = load_panel(SOURCE_FILE, data_dir=data_dir)
    _, first_file = load_panel(khandani_lo.SOURCE_FILE, data_dir=data_dir)
    return panel, first_file


# --- Lesson 2: the bounce the rule bought ------------------------------------------

#: The stock and the three days the sketch draws.
SYMBOL = "CAH"
DAYS = ("2009-08-31", "2009-09-01", "2009-09-02")


@dataclass(frozen=True)
class Bounce:
    """CAH's three closes, what Example 4.3 bought at the middle one, and the run without CAH.

    ``weight`` is CAH's weight at the 2009-09-01 close, a fraction of that
    day's $1 of gross, and ``earned`` is what it earned over the next day,
    the same fraction of $1. ``apr_without`` and ``sharpe_without`` are
    Example 4.3's two figures with CAH dropped from the panel. ``bound`` is
    the largest day-over-day ratio the scale-break guard lets through.
    """

    closes: tuple[float, float, float]
    weight: float
    earned: float
    apr_without: float
    sharpe_without: float
    flagged: tuple[str, ...]
    bound: float = math.exp(SCALE_BREAK_BOUND)

    @property
    def fall(self) -> float:
        return self.closes[1] / self.closes[0]

    @property
    def rise(self) -> float:
        return self.closes[2] / self.closes[1]

    @classmethod
    def from_run(cls, data_dir: Path | None = None) -> Bounce:
        """Run Example 4.3 on the committed panel, with CAH and without it.

        It refuses unless the guard lets the fall through and flags the rise,
        the rule bought CAH at the middle close, and neither figure without
        CAH matches the book, since the sketch's words say each.
        """
        panel, _ = _frames(data_dir)
        return cls.from_panel(panel)

    @classmethod
    def from_panel(cls, panel: pd.DataFrame) -> Bounce:
        """:meth:`from_run` on a panel of closes already read."""
        run = close_to_close(panel, start=WINDOW_START, end=WINDOW_END)
        column = panel.columns.get_loc(SYMBOL)
        row = run.days.get_loc(pd.Timestamp(DAYS[1]))
        closes = panel[SYMBOL].loc[DAYS[0] : DAYS[2]]
        if [str(day.date()) for day in closes.index] != list(DAYS):
            raise ValueError(f"{SYMBOL}'s closes do not fall on {', '.join(DAYS)}")
        weight = float(run.weights[row, column])
        cut = panel.loc[run.days, SYMBOL]
        next_return = float(cut.iloc[row + 1] / cut.iloc[row] - 1)
        without = close_to_close(panel.drop(columns=[SYMBOL]), start=WINDOW_START, end=WINDOW_END)
        series = panel[SYMBOL].loc[DAYS[0] : DAYS[2]].dropna()
        found = cls(
            closes=tuple(float(c) for c in closes),
            weight=weight,
            earned=weight * next_return,
            apr_without=without.apr,
            sharpe_without=without.sharpe,
            flagged=tuple(str(day.date()) for day in scale_breaks(series)),
        )
        found.refuse_false_words()
        return found

    def refuse_false_words(self) -> None:
        """Raise when the figures would make a label false."""
        if abs(math.log(self.fall)) > math.log(self.bound) or self.flagged != (DAYS[2],):
            raise ValueError("the sketch says the guard lets the fall through and flags the rise")
        if not self.weight > 0:
            raise ValueError("the sketch says the rule bought CAH at the 2009-09-01 close")
        if matches(100 * self.apr_without, BOOK_43_APR_PERCENT) or matches(
            self.sharpe_without, BOOK_43_SHARPE
        ):
            raise ValueError("the sketch says neither figure without CAH matches the book")


def cents(fraction: float) -> str:
    """A fraction of $1 in cents, to two decimals."""
    return f"{100 * fraction:.2f}"


#: The price axis's foot and top, and the prices those heights stand for. A
#: close's height is one affine function of its price, so the three dots sit
#: to one scale.
PRICE_FOOT, PRICE_TOP = 1.1, 3.75
PRICE_LOW, PRICE_HIGH = 11.0, 24.0
PRICE_AXIS_X = 1.1
#: Where each day sits along the time axis.
DAY_X = (2.1, 4.3, 6.6)
#: Where the green bracket stands, and how far beneath the middle dot the
#: green mark sits.
RISE_X = 7.5
BOUGHT_BELOW = 0.22


def price_y(price: float) -> float:
    """The board height of a close, to one scale."""
    return PRICE_FOOT + (price - PRICE_LOW) / (PRICE_HIGH - PRICE_LOW) * (PRICE_TOP - PRICE_FOOT)


def _toward(x0: float, y0: float, x1: float, y1: float, trim: float = 0.2) -> tuple:
    """An arrow from one dot to another, stopping ``trim`` short of each."""
    length = math.hypot(x1 - x0, y1 - y0)
    dx, dy = (x1 - x0) / length * trim, (y1 - y0) / length * trim
    return _arrow(x0 + dx, y0 + dy, x1 - dx, y1 - dy)


def _bounce(bounce: Bounce) -> Scene:
    """Lesson 2: a fall the guard lets through, a rise it flags, and the stake bought between."""
    ys = [price_y(c) for c in bounce.closes]
    price_ticks: list[Stroke | Label] = []
    for k, (close, y) in enumerate(zip(bounce.closes, ys, strict=True)):
        gid = f"price-tick-{k}"
        price_ticks.append(
            _stroke(
                gid,
                _line([(PRICE_AXIS_X - 0.1, y), (PRICE_AXIS_X + 0.1, y)], per_unit=12),
                color=MUTED,
                frames=2,
            )
        )
        price_ticks.append(
            Label(
                f"{close:.2f}", PRICE_AXIS_X - 0.28, y, names=gid, color=MUTED, size=11, ha="right"
            )
        )
    price_ticks.append(
        _stroke(
            "price-tick-foot",
            _line([(PRICE_AXIS_X - 0.1, PRICE_FOOT), (PRICE_AXIS_X, PRICE_FOOT)], per_unit=12),
            color=MUTED,
            frames=2,
        )
    )
    price_ticks.append(
        Label(
            f"{PRICE_LOW:.2f}",
            PRICE_AXIS_X - 0.28,
            PRICE_FOOT,
            names="price-tick-foot",
            color=MUTED,
            size=11,
            ha="right",
        )
    )
    day_ticks: list[Stroke | Label] = []
    for k, (x, text) in enumerate(zip(DAY_X, (DAYS[0], DAYS[1][5:], DAYS[2][5:]), strict=True)):
        gid = f"day-tick-{k}"
        day_ticks.append(
            _stroke(
                gid,
                _line([(x, PRICE_FOOT - 0.1), (x, PRICE_FOOT + 0.1)], per_unit=12),
                color=MUTED,
                frames=2,
            )
        )
        day_ticks.append(
            Label(text, x, PRICE_FOOT - 0.42, names=gid, color=MUTED, size=11, ha="center")
        )
    (x0, x1, x2), (y0, y1, y2) = DAY_X, ys
    bound = f"{bounce.bound:g}"
    return Scene(
        "The bounce the rule bought",
        "cah_bounce",
        (
            _stroke(
                "price-axis",
                _line([(PRICE_AXIS_X, PRICE_FOOT), (PRICE_AXIS_X, PRICE_TOP)]),
                color=MUTED,
                frames=6,
            ),
            Label(
                f"{SYMBOL}’s close",
                PRICE_AXIS_X + 0.35,
                PRICE_TOP + 0.05,
                names="price-axis",
                color=MUTED,
                size=11,
            ),
            _stroke(
                "time-axis",
                _line([(PRICE_AXIS_X, PRICE_FOOT), (9.0, PRICE_FOOT)]),
                color=MUTED,
                frames=8,
            ),
            *day_ticks,
            *price_ticks,
            _dot("close-0", x0, y0, color=INK),
            _dot("close-1", x1, y1, color=INK),
            _dot("close-2", x2, y2, color=INK),
            _stroke("fall", _toward(x0, y0, x1, y1), color=INK, frames=6),
            Label(
                f"× {bounce.fall:.4f}: inside\nthe check’s bounds",
                1.45,
                1.66,
                names="fall",
                size=11,
            ),
            _stroke("rise", _toward(x1, y1, x2, y2), color=LOST, frames=6),
            Label(
                f"× {bounce.rise:.4f}:\npast {bound}, flagged",
                5.2,
                3.15,
                names="rise",
                color=LOST,
                size=11,
                ha="right",
            ),
            _stroke(
                "bought",
                _line(
                    [(x1 - 0.25, y1 - BOUGHT_BELOW), (x1 + 0.25, y1 - BOUGHT_BELOW)], per_unit=10
                ),
                color=GOOD,
                width=7.0,
                frames=3,
            ),
            Label(
                f"bought at the close:\n{cents(bounce.weight)} cents of the $1",
                x1 + 0.55,
                y1 - 0.17,
                names="bought",
                color=GOOD,
                size=11,
            ),
            _stroke(
                "earned",
                _line(
                    [
                        (RISE_X - 0.13, y1),
                        (RISE_X + 0.13, y1),
                        (RISE_X, y1),
                        (RISE_X, y2),
                        (RISE_X - 0.13, y2),
                        (RISE_X + 0.13, y2),
                    ],
                    per_unit=8,
                ),
                color=GOOD,
                frames=5,
            ),
            Label(
                f"up {100 * (bounce.rise - 1):.2f} percent:\n"
                f"{cents(bounce.earned)} cents earned\nthe next day",
                RISE_X + 0.22,
                (y1 + y2) / 2,
                names="earned",
                color=GOOD,
                size=11,
            ),
            Label(
                f"without {SYMBOL}: {100 * bounce.apr_without:.2f} percent and "
                f"{bounce.sharpe_without:.4f}, neither matches the book",
                5.0,
                0.25,
                names="time-axis",
                color=MUTED,
                size=11,
                ha="center",
            ),
        ),
    )


# --- Lesson 4: same trading, twenty times the profit --------------------------------


@dataclass(frozen=True)
class AverageDays:
    """The first book's rule's average day on 2006's file and on the panel.

    Profits and costs are in basis points of the rule's average gross
    position, and each turnover is that position's multiple traded a day, the
    figures :func:`chan.khandani_lo.daily_book` gives.
    """

    year_profit: float
    year_cost: float
    year_turnover: float
    panel_profit: float
    panel_cost: float
    panel_turnover: float

    @property
    def year_cost_per_profit(self) -> float:
        return self.year_cost / self.year_profit

    @property
    def panel_kept(self) -> float:
        return self.panel_profit - self.panel_cost

    @property
    def profit_ratio(self) -> float:
        return self.panel_profit / self.year_profit

    @classmethod
    def from_run(cls, data_dir: Path | None = None) -> AverageDays:
        """Run the first book's rule on its own 2006 file and on the panel's window.

        The panel's run is :class:`chan.khandani_lo_book_two.BookTwo`'s
        ``first_rule_on_panel``, the same call on the same window.
        """
        panel, first_file = _frames(data_dir)
        return cls.from_frames(panel, first_file)

    @classmethod
    def from_frames(cls, panel: pd.DataFrame, first_file: pd.DataFrame) -> AverageDays:
        """:meth:`from_run` on frames of closes already read."""
        year = daily_book(reversal(first_file))
        on_panel = daily_book(reversal(panel, start=WINDOW_START, end=WINDOW_END))
        found = cls(
            year_profit=1e4 * year.profit,
            year_cost=1e4 * year.cost,
            year_turnover=year.turnover,
            panel_profit=1e4 * on_panel.profit,
            panel_cost=1e4 * on_panel.cost,
            panel_turnover=on_panel.turnover,
        )
        found.refuse_false_words()
        return found

    def refuse_false_words(self) -> None:
        """Raise when the figures would make a label false.

        The hatch says the year's cost passes its profit, the bracket says the
        panel's profit passes its cost, and its words say the part kept is
        less than a third of the profit.
        """
        if not self.year_cost > self.year_profit > 0:
            raise ValueError("the sketch says 2006's cost passes its profit")
        if not 0 < self.panel_kept < self.panel_profit / 3:
            raise ValueError("the sketch says the panel keeps less than a third of its profit")


#: Whole numbers in words, as the post spells a count.
_ONES = (
    "no",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
)
_TENS = ("", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety")


def spelled(count: int) -> str:
    """``count`` in words below a hundred, and in digits from there."""
    if 0 <= count < 20:
        return _ONES[count]
    if 20 <= count < 100:
        tens, ones = divmod(count, 10)
        return _TENS[tens] + (f"-{_ONES[ones]}" if ones else "")
    return f"{count:,}"


def times_in_words(ratio: float) -> str:
    """A ratio rounded to the nearest whole number and spelled, such as ``twenty``."""
    return spelled(round(ratio))


#: Where zero basis points sits, and the board units per basis point.
ZERO_X, PER_POINT = 2.05, 0.53
#: The height of each bar, from the top: 2006's cost and profit, then the
#: panel's cost and profit. The scale's axis runs beneath them.
YEAR_COST_Y, YEAR_PROFIT_Y = 3.35, 2.95
PANEL_COST_Y, PANEL_PROFIT_Y = 2.05, 1.65
AXIS_Y = 1.3
BAR_WIDTH = 7.0
#: The half height of the hatched stretch, which matches a bar's thickness.
HATCH_HALF = 0.09
#: The scale's ticks, in basis points.
POINT_TICKS = (0, 5, 10)


def on_scale(points: float) -> float:
    """The board position of a figure in basis points, to one scale."""
    return ZERO_X + PER_POINT * points


def _bar(gid: str, points: float, y: float, color: str) -> Stroke:
    return _stroke(
        gid,
        _line([(ZERO_X, y), (on_scale(points), y)], per_unit=24),
        color=color,
        width=BAR_WIDTH,
        frames=5,
    )


def _bar_label(text: str, y: float, gid: str, color: str) -> Label:
    """A bar's name and figure, to the left of where every bar starts."""
    return Label(text, ZERO_X - 0.3, y, names=gid, color=color, size=11, ha="right")


def _average_day(days: AverageDays) -> Scene:
    """Lesson 4: the same trading costs about the same, and the profit is what moved."""
    year_end, panel_end = on_scale(days.year_cost), on_scale(days.panel_profit)
    scale_ticks: list[Stroke | Label] = []
    for points in POINT_TICKS:
        gid = f"tick-{points}"
        x = on_scale(points)
        scale_ticks.append(
            _stroke(
                gid,
                _line([(x, AXIS_Y - 0.1), (x, AXIS_Y + 0.1)], per_unit=12),
                color=MUTED,
                frames=2,
            )
        )
        scale_ticks.append(
            Label(f"{points}", x, AXIS_Y - 0.42, names=gid, color=MUTED, size=11, ha="center")
        )
    kept_share = "less than a third"
    return Scene(
        f"Same trading, {times_in_words(days.profit_ratio)} times the profit",
        "average_day",
        (
            _stroke(
                "axis",
                _line([(ZERO_X, AXIS_Y), (on_scale(11), AXIS_Y)]),
                color=MUTED,
                frames=8,
            ),
            *scale_ticks,
            Label(
                "basis points a day, of the average gross position",
                on_scale(5),
                0.55,
                names="axis",
                color=MUTED,
                size=11,
                ha="center",
            ),
            Label("2006, the first book’s file", 0.3, 3.75, names="axis", size=12),
            _bar("year-cost", days.year_cost, YEAR_COST_Y, LOST),
            _bar_label(f"cost {days.year_cost:.4f}", YEAR_COST_Y, "year-cost", LOST),
            _bar("year-profit", days.year_profit, YEAR_PROFIT_Y, GOOD),
            _bar_label(f"profit {days.year_profit:.4f}", YEAR_PROFIT_Y, "year-profit", GOOD),
            Label("2007 to 2011, the panel", 0.3, 2.45, names="axis", size=12),
            _bar("panel-cost", days.panel_cost, PANEL_COST_Y, LOST),
            _bar_label(f"cost {days.panel_cost:.4f}", PANEL_COST_Y, "panel-cost", LOST),
            _bar("panel-profit", days.panel_profit, PANEL_PROFIT_Y, GOOD),
            _bar_label(f"profit {days.panel_profit:.4f}", PANEL_PROFIT_Y, "panel-profit", GOOD),
            Label(
                f"trades {days.year_turnover:.4f} and {days.panel_turnover:.4f}"
                " times the position a day",
                9.75,
                3.75,
                names="panel-cost",
                color=MUTED,
                size=11,
                ha="right",
            ),
            _stroke(
                "short",
                _hatched(
                    on_scale(days.year_profit),
                    YEAR_PROFIT_Y - HATCH_HALF,
                    year_end,
                    YEAR_PROFIT_Y + HATCH_HALF,
                ),
                color=LOST,
                width=1.4,
                frames=10,
            ),
            Label(
                f"cost is {days.year_cost_per_profit:.4f} times the profit",
                year_end + 0.3,
                YEAR_PROFIT_Y,
                names="short",
                color=LOST,
                size=11,
            ),
            _stroke(
                "kept",
                _line(
                    [
                        (on_scale(days.panel_cost), PANEL_COST_Y + 0.13),
                        (on_scale(days.panel_cost), PANEL_COST_Y - 0.13),
                        (on_scale(days.panel_cost), PANEL_COST_Y),
                        (panel_end, PANEL_COST_Y),
                        (panel_end, PANEL_COST_Y + 0.13),
                        (panel_end, PANEL_COST_Y - 0.13),
                    ],
                    per_unit=8,
                ),
                color=ACCENT,
                frames=5,
            ),
            Label(
                f"kept: {days.panel_kept:.4f},\n{kept_share}",
                panel_end + 0.3,
                PANEL_COST_Y,
                names="kept",
                color=ACCENT,
                size=11,
            ),
            Label(
                f"first book’s rule, {ONE_WAY_COST * 1e4:g} basis points on every buy and sell, "
                "first day’s trades charged",
                on_scale(5),
                0.2,
                names="axis",
                color=MUTED,
                size=11,
                ha="center",
            ),
        ),
    )


# --- Drawing ------------------------------------------------------------------

#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("cah_bounce", "average_day")
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


def figures_from_run(data_dir: Path | None = None) -> tuple[Bounce, AverageDays]:
    """Both scenes' figures from one read of the committed files."""
    panel, first_file = _frames(data_dir)
    return Bounce.from_panel(panel), AverageDays.from_frames(panel, first_file)


def scenes(bounce: Bounce | None = None, days: AverageDays | None = None) -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them, Lesson 2's then Lesson 4's.

    Each figure set defaults to its run on the committed files.
    """
    if bounce is None or days is None:
        found_bounce, found_days = figures_from_run()
        bounce = bounce if bounce is not None else found_bounce
        days = days if days is not None else found_days
    return (_bounce(bounce), _average_day(days))


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


def make_khandani_lo_book_two_whiteboards(out_dir: Path | None = None) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes()]


def main() -> None:
    for path in make_khandani_lo_book_two_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
