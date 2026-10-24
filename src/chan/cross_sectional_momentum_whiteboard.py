"""Whiteboard sketches for the cross-sectional momentum post, for its strategy and its Lesson 1.

``blog/cross-sectional-momentum-lessons.md`` asks a reader to hold two pictures
that its sentences only describe. One is how 25 overlapping cohorts of picks
add up to one unit of capital. The other is how one window's daily returns
give two different annual returns, depending on whether they are added or
multiplied. This module draws the two as scenes, sketched stroke by stroke as
if on a whiteboard, and the post places each right after the passage it draws.

1. Twenty-five cohorts make one portfolio: a grey day axis, one cohort of picks
   held for 25 days as a green bar for its 50 longs over a red bar for its 50
   shorts, then the next 24 cohorts, each starting one day later and one row
   lower, then a brass dashed line on the one day that cuts all 25 bars, the
   arithmetic that makes 2,500 picks one unit of capital, and last a red
   stretch of the axis under the 2007 window's first 24 days, which hold fewer
   than 25 cohorts. It sits in the post's section on the strategy, after the
   list that ends on the sizing.
2. Add, or multiply: the 2007 window's daily returns as a row of small grey
   bars, then two paths from them. The black one adds the returns and scales
   the sum by 252 over the window's days, which the script prints as
   ``Avg Ann Ret``. The brass one multiplies the 1 + r and raises the product
   to 252 over the window's days, less 1, which the script prints as ``APR``.
   It sits in Lesson 1, after the paragraph opening "None of the five prints
   what the comment says".

Every number either sketch prints is read from the run on the committed
vintage, through :func:`chan.cross_sectional_momentum.read_closes`, rather than
written into the scene. :func:`cohort_figures` measures the cohorts from the
script's own formations and :func:`chan.cross_sectional_momentum.cohorts_held`,
and :func:`return_figures` reads the script as printed over the 2007 window.
The cohorts sketch is drawn to its
count rather than to its dates: each bar is one cohort and each step along the
axis is one trading day, so the brass line falls where the first cohort's last
day is the last cohort's first. The bars in the returns sketch are the
window's daily returns, each drawn at a height in proportion to its value. A
run whose figures would make the drawing false is refused rather than drawn,
such as a window that opens on more than one cohort.

The book's 37 percent is not on the returns sketch. The post holds the book's
figures back until Lesson 2, because the rule written before the run read the
book's APR as the arithmetic figure, and the compounded match was seen only
afterwards.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look, frame rate and colours. Each
sketch carries more than a reader takes in at that post's pace, so both are in
:data:`PACED`, and :func:`sketch_timeline` holds each of their labels longer
and their finished drawings for twelve seconds, as
:mod:`chan.equity_seasonals_whiteboard` does for its slow sketches. Each GIF is
named :data:`GIF_PREFIX` plus the scene's slug. The post's chart,
``cross_sectional_momentum_cumulative_returns.png``, starts with the same
prefix, and it is a PNG, so no check that globs for GIFs reads it.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw both with::

    uv run python -m chan.cross_sectional_momentum_whiteboard
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from chan import cross_sectional_momentum as momentum
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    Frame,
    Label,
    Scene,
    Stroke,
    _arrow,
    _line,
    _stroke,
    render,
    timeline,
)
from chan.vintage import VintageUnavailable

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "cross_sectional_momentum_"

#: The window both sketches read, the one the book reports.
WINDOW = "2007"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``cross_sectional_momentum_two_returns.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


# --- The figures, read from the run --------------------------------------------


@dataclass(frozen=True)
class Cohorts:
    """What the cohorts sketch counts, measured on the run.

    ``hold_days`` is the most cohorts any day holds, and ``picks`` the longs
    plus the shorts each formation row marks, ``longs`` of them long. On a day
    holding every cohort, ``picks_held`` is the marks summed over the cohorts
    held, and ``divisor`` what the script divides each day's return by. The
    window opens on ``opens``, holding ``held_at_open`` cohorts, and holds
    fewer than ``hold_days`` on its first ``short_days`` days.
    """

    hold_days: int
    longs: int
    picks: int
    picks_held: int
    divisor: int
    opens: pd.Timestamp
    held_at_open: int
    short_days: int


@dataclass(frozen=True)
class Returns:
    """What the returns sketch prints, over the script's 2007 window.

    ``daily`` is each day's return from the script as printed, ``total`` their
    sum and ``growth`` the product of each 1 + r. ``arithmetic`` and
    ``compounded`` are the two annual figures
    :func:`chan.cross_sectional_momentum.window_figures` gives.
    """

    daily: tuple[float, ...]
    total: float
    growth: float
    arithmetic: float
    compounded: float
    trading_days: int

    @property
    def days(self) -> int:
        return len(self.daily)


def cohort_figures(closes: pd.DataFrame) -> Cohorts:
    """The cohorts sketch's counts, from the script's formations and the cohorts it holds."""
    values = closes.to_numpy(dtype=float)
    days = pd.DatetimeIndex(closes.index)
    longs, shorts = momentum.formations(momentum.ranking_returns(values))
    formed = longs.any(axis=1)
    per_row = {int(n) for n in (longs.sum(axis=1) + shorts.sum(axis=1))[formed]}
    long_rows = {int(n) for n in longs.sum(axis=1)[formed]}
    if len(per_row) != 1 or len(long_rows) != 1:
        raise ValueError(
            f"The cohorts sketch draws one size of cohort, and this run's are {per_row}"
        )
    held = momentum.cohorts_held(len(values))
    hold_days = int(held.max())
    full = np.flatnonzero(held == hold_days)
    marks = (longs | shorts).sum(axis=1)
    picks_held = {int(marks[t - hold_days : t].sum()) for t in full}
    if len(picks_held) != 1:
        raise ValueError(f"The cohorts sketch draws one full book, and this run's are {picks_held}")
    window, _ = momentum.window_returns(np.zeros(len(values)), days, WINDOW)
    inside = held[(days >= window[0]) & (days <= window[-1])]
    return Cohorts(
        hold_days=hold_days,
        longs=long_rows.pop(),
        picks=per_row.pop(),
        picks_held=picks_held.pop(),
        divisor=2 * momentum.TOP_N * momentum.HOLD_DAYS,
        opens=window[0],
        held_at_open=int(inside[0]),
        short_days=int((inside < hold_days).sum()),
    )


def return_figures(closes: pd.DataFrame) -> Returns:
    """The returns sketch's figures, from the script as printed over :data:`WINDOW`."""
    values = closes.to_numpy(dtype=float)
    days = pd.DatetimeIndex(closes.index)
    daily = momentum.script_as_printed(values)
    _, r = momentum.window_returns(daily, days, WINDOW)
    figures = momentum.window_figures(daily, days, WINDOW)
    return Returns(
        daily=tuple(float(each) for each in r),
        total=float(r.sum()),
        growth=float(np.prod(1 + r)),
        arithmetic=figures.arithmetic_annual,
        compounded=figures.compounded_apr,
        trading_days=momentum.TRADING_DAYS,
    )


# --- The cohorts sketch --------------------------------------------------------

#: Where the first cohort's first day starts, and the board width of one day.
X0, DX = 1.7, 0.085
#: The height of the first cohort, and how far each later one sits below it.
Y_TOP, PITCH = 3.4, 0.1
#: How far the green and red halves of a bar sit above and below its middle.
HALF = 0.035
#: The day axis's height.
AXIS_Y = 0.75
#: Where the arithmetic's labels start across the board.
SUMS_X = 5.9

#: Counts in words for a title, from one to ninety-nine.
UNITS = ("", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
TEENS = (
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
TENS = ("", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety")


def spelled(count: int) -> str:
    """``count`` in words, such as ``twenty-five``, for counts from 1 to 99."""
    if not 1 <= count <= 99:
        raise ValueError(f"spelled counts from 1 to 99, not {count}")
    if count < 10:
        return UNITS[count]
    if count < 20:
        return TEENS[count - 10]
    tens, units = divmod(count, 10)
    return TENS[tens] + (f"-{UNITS[units]}" if units else "")


def day_x(day: float) -> float:
    """The board position of the start of trading day ``day``, counted from 0 at
    the first cohort's first day."""
    return X0 + DX * day


def cohort_y(k: int) -> float:
    """The height of the middle of cohort ``k``'s bar, counted from 0."""
    return Y_TOP - PITCH * k


def _cohorts(figures: Cohorts) -> Scene:
    """The strategy section: 25 cohorts, each held 25 days, are one unit of capital."""
    n = figures.hold_days
    if figures.held_at_open != 1 or figures.short_days != n - 1:
        raise ValueError(
            f"The cohorts sketch opens the window on the first cohort's first day and fills "
            f"it a day at a time, and this run opens on {figures.held_at_open} cohorts with "
            f"{figures.short_days} days short of {n}"
        )
    if figures.picks_held != n * figures.picks or figures.divisor != figures.picks_held:
        raise ValueError(
            f"The cohorts sketch says {n} cohorts of {figures.picks} picks are "
            f"{figures.picks_held} and that the script divides by that, and it divides by "
            f"{figures.divisor}"
        )
    shorts = figures.picks - figures.longs
    if shorts != figures.longs:
        raise ValueError(
            f"The cohorts sketch divides by 2 · {figures.longs} · {n}, which needs as many "
            f"shorts as longs, and this run's cohorts hold {figures.longs} long and {shorts} short"
        )
    # Where the one day that every cohort holds is: cohort 0's last day, and
    # cohort n − 1's first. The line runs down its middle.
    held_x = day_x(n - 0.5)
    steps: list[Stroke | Label] = [
        _stroke(
            "axis",
            _line([(X0 - 0.3, AXIS_Y), (day_x(2 * n - 1) + 1.0, AXIS_Y)], per_unit=4),
            color=MUTED,
            frames=8,
        ),
        Label(
            "trading days",
            day_x(2 * n - 1) + 1.0,
            AXIS_Y - 0.32,
            names="axis",
            color=MUTED,
            size=11,
            ha="right",
        ),
    ]
    for k in range(n):
        y = cohort_y(k)
        frames = 4 if k == 0 else 1
        for side, ink, dy in (("long", GOOD, HALF), ("short", LOST, -HALF)):
            steps.append(
                _stroke(
                    f"cohort-{k}-{side}",
                    _line([(day_x(k), y + dy), (day_x(k + n), y + dy)], per_unit=8),
                    color=ink,
                    width=2.4,
                    frames=frames,
                )
            )
        if k == 0:
            steps += [
                Label(
                    f"{figures.longs} long",
                    X0 - 0.25,
                    y + 0.2,
                    names="cohort-0-long",
                    color=GOOD,
                    size=12,
                    ha="right",
                ),
                Label(
                    f"{shorts} short",
                    X0 - 0.25,
                    y - 0.2,
                    names="cohort-0-short",
                    color=LOST,
                    size=12,
                    ha="right",
                ),
                Label(
                    f"one cohort: one day’s {figures.picks} picks",
                    day_x(n) + 0.2,
                    y + 0.25,
                    names="cohort-0-short",
                    size=12,
                ),
            ]
    steps += [
        _stroke(
            "held",
            _line([(held_x, Y_TOP + 0.12), (held_x, AXIS_Y - 0.15)], per_unit=8),
            color=ACCENT,
            dashed=True,
            width=2.0,
            frames=6,
        ),
        Label(
            f"{n} cohorts held",
            held_x,
            AXIS_Y - 0.5,
            names="held",
            color=ACCENT,
            size=12,
            ha="center",
        ),
        Label(f"{n} cohorts × {figures.picks} picks", SUMS_X, 2.95, names="held", size=12),
        Label(f"= {figures.picks_held:,} picks held", SUMS_X, 2.61, names="held", size=12),
        Label(
            f"divide by 2 · {figures.longs} · {n} = {figures.divisor:,}",
            SUMS_X,
            2.1,
            names="held",
            size=12,
        ),
        Label("one unit of capital", SUMS_X, 1.76, names="held", size=12),
        _stroke(
            "ramp",
            _line([(day_x(0), AXIS_Y), (day_x(figures.short_days), AXIS_Y)], per_unit=8),
            color=LOST,
            width=4.0,
            frames=5,
        ),
        Label(
            f"first {figures.short_days} days of {figures.opens.year}:",
            0.15,
            1.62,
            names="ramp",
            color=LOST,
            size=12,
        ),
        Label(f"fewer than {n}", 0.15, 1.28, names="ramp", color=LOST, size=12),
    ]
    return Scene(f"{spelled(n).capitalize()} cohorts make one portfolio", "cohorts", tuple(steps))


# --- The returns sketch --------------------------------------------------------

#: Where the row of daily bars runs across the board, its baseline's height,
#: and the board height of the largest return in the window.
DAILY_X = (0.5, 7.0)
DAILY_Y, DAILY_TALLEST = 3.3, 0.4
#: The heights of the two paths, the black one added and the brass multiplied.
ADD_Y, MULTIPLY_Y = 2.05, 0.95
#: Where each path's arrow runs across the board, and where its result starts.
ARROW_X = (4.25, 6.0)
RESULT_X = 6.3


def bar_heights(returns: Returns) -> np.ndarray:
    """Each daily bar's height above the baseline, in proportion to its return."""
    daily = np.asarray(returns.daily)
    return DAILY_TALLEST * daily / np.abs(daily).max()


def bar_xs(returns: Returns) -> np.ndarray:
    """Where each daily bar stands, evenly spaced along :data:`DAILY_X`."""
    return np.linspace(*DAILY_X, returns.days)


def _daily_bars(returns: Returns) -> tuple:
    """One stroke that walks the baseline and rises to each day's return and back."""
    xs, ys = [], []
    for x, h in zip(bar_xs(returns), bar_heights(returns), strict=True):
        xs += [x, x, x]
        ys += [DAILY_Y, DAILY_Y + h, DAILY_Y]
    return np.array(xs), np.array(ys)


def _two_returns(returns: Returns) -> Scene:
    """Lesson 1: the script's two annual returns, one added and one multiplied."""
    n, year = returns.days, returns.trading_days
    if not returns.total > 0 or not returns.growth > 1:
        raise ValueError(
            f"The returns sketch draws a window that gained, and this run's sum is "
            f"{returns.total:.6f} and its growth {returns.growth:.6f}"
        )
    steps: list[Stroke | Label] = [
        _stroke("daily", _daily_bars(returns), color=MUTED, width=1.2, frames=10),
        Label(
            f"{WINDOW}: {n} days", DAILY_X[1] + 0.3, DAILY_Y, names="daily", color=MUTED, size=12
        ),
    ]
    for gid, ink, y, first, operation, result in (
        (
            "add",
            INK,
            ADD_Y,
            f"add the {n} returns: {returns.total:.4f}",
            f"× {year}/{n}",
            f"{returns.arithmetic:.4f}, Avg Ann Ret",
        ),
        (
            "multiply",
            ACCENT,
            MULTIPLY_Y,
            f"multiply the 1 + r: {returns.growth:.4f}",
            f"^({year}/{n}), less 1",
            f"{returns.compounded:.4f}, APR",
        ),
    ):
        steps += [
            Label(first, 0.3, y, names="daily", color=ink, size=12),
            _stroke(gid, _arrow(ARROW_X[0], y, ARROW_X[1], y), color=ink, frames=5),
            Label(
                operation, sum(ARROW_X) / 2, y + 0.42, names=gid, color=ink, size=12, ha="center"
            ),
            Label(result, RESULT_X, y, names=gid, color=ink, size=12),
        ]
    return Scene("Add, or multiply: two annual returns, one window", "two_returns", tuple(steps))


# --- Drawing ------------------------------------------------------------------

#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("cohorts", "two_returns")
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


def scenes(cohorts: Cohorts, returns: Returns) -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them, the strategy's then Lesson 1's."""
    return (_cohorts(cohorts), _two_returns(returns))


def read_figures(data_dir: Path | None = None) -> tuple[Cohorts, Returns]:
    """Both sketches' figures, read from the committed closes."""
    _, closes = momentum.read_closes(data_dir)
    return cohort_figures(closes), return_figures(closes)


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


def make_cross_sectional_momentum_whiteboards(
    out_dir: Path | None = None, figures: tuple[Cohorts, Returns] | None = None
) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order.

    ``figures`` is read from the committed closes through :func:`read_figures`
    when it is not handed in.
    """
    cohorts, returns = figures if figures is not None else read_figures()
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes(cohorts, returns)]


def main() -> None:
    try:
        paths = make_cross_sectional_momentum_whiteboards()
    except VintageUnavailable as refused:
        # As in chan.cross_sectional_momentum.main, a refusal that names the
        # source reaches the reader as one line.
        raise SystemExit(str(refused)) from refused
    for path in paths:
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
