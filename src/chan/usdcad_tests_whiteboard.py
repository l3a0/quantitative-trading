"""Whiteboard sketches of the tests, the rule and the lessons in the USD.CAD post.

The post's section "The tests and the file" explains four ways of asking one
question, whether USD.CAD wanders like a random walk or is pulled back to a
mean, and then the linear rule that trades the answer. Each test is a short
paragraph of regression terms. A reader who has not met them gets more from a
picture of what each one looks for than from the terms, so this module draws
those as six scenes. One more comes before them, for the post's opening
section, two after them for its Lesson 1, one for Lesson 2, two for Lesson 3
and two for Lesson 5. Each scene is sketched stroke by stroke as if on a
whiteboard, and each is its own looping GIF, so the post can place it right
after the text it draws.

1. Every day or a few round trips: a dot on every point of a price path, and
   the same path with a few round trips under it, because a test reads every
   close and a backtest sees only the round trips its rule made.
2. The question: a wiggly price around a dashed mean.
3. ADF: a high close followed by a fall, which is what a negative λ means.
4. Hurst: two pairs of curves spreading from one point, the narrower pair a
   reverting series whose variance grows like τ²ᴴ with H below 0.5.
5. Variance ratio: the 2-day variance shorter than twice the 1-day variance.
6. Half-life: the distance from the mean decaying, halved after −ln 2 / λ
   days, which the run measures at its lookback.
7. The linear rule: a z-score of +2 sold short and one of −1.5 bought, with a
   warning that the lookback was measured on every close the rule trades.
8. Chan's reading: the ADF statistic on a number line with the three critical
   values, right of the 10 percent value it would have to pass to reject a
   random walk.
9. The fingerprint: Chan's MATLAB file cannot be compared with the CSV here,
   so the CSV goes through the three calculations and each lands the values
   the script printed, which no change of units would alter.
10. One row apart: ``adfuller`` fits the closes from day 3 to the last, and
    jplv7's ``adf`` from day 4, so the script's statistic rests on one row
    fewer.
11. Chance and the start day: a histogram of ``genhurst``'s H on random walks
    of the same length, with its ±1 SD band, lines at 0.5, the run's H and the
    book's 0.49, and a dot for each of the eleven start days.
12. Leaning, not crossing: three gauges, the ADF statistic against its 10
    percent critical value, H against the random walks' ±1 SD band, and the
    variance ratio's statistic against its test's critical value, each on the
    reverting side of a random walk and none past the line that would reject.
13. The look-ahead: the half-life measured on every close, and the rule
    trading from its first position inside that window, above a schematic of
    measuring on earlier days and trading after.
14. Ten half-lives: the closes on a line with a tick every lookback, and the
    count of half-lives they span.

The numbers above order this list and nothing else. A GIF stands alone, so its
title is the scene's name with no number, and its file is named for the scene,
such as ``usdcad_tests_hurst.gif``. The last scene's title counts its ticks,
and that count is read from the run, so it is spelled out rather than written.

The first seven scenes' shapes are schematic and carry no data. Two numbers in
them do: the lookback the half-life rounds to and the count of closes. The
opening scene's round trips stand for a generic rule that enters and exits,
not the post's linear rule, which holds a position on every day once its
lookback fills, and changes its size and its side as the close moves. Chan's
reading is drawn to scale, so the position of each tick and of the statistic's
dot is an affine function of its value, and it prints the three critical
values and the statistic. The fingerprint prints the count of closes, the ADF
statistic, the AR(1) estimate, the variance ratio's p-value and the half-life.
One row apart prints the count of closes, each toolbox's row count and
statistic, and places each bar's start at the cell of the first day its
regression fits. Chance and the start day is drawn to scale along its axis,
with its bins, its band and its dots from :mod:`chan.usdcad_hurst_noise`
through :func:`spread`. Leaning, not crossing draws each of its three gauges
to its own scale, and prints the ADF statistic and its 10 percent critical
value, H, and the variance ratio's statistic and critical value. Its band is
the same measurement's mean and SD, and the variance ratio's critical value is
derived from :data:`chan.stationarity_tests.VRATIO_ALPHA`, the level the test
reports at. The look-ahead places its bars to scale by date and
prints the first close, the first position, the last close, the count of
closes and the lookback. Ten half-lives prints the dates of the first and last
close, the lookback, and the closes over the unrounded half-life. Every number
but the book's 0.49, a random walk's 0.5 and the gauges' 0 comes from the
:class:`chan.usdcad_mean_reversion.StationarityRun` that
:func:`chan.usdcad_mean_reversion.stationarity_tests` returns, read through the
run's own path, so the scale-break guard runs here too, or from the
measurement. A change to the vintage, to how the half-life rounds or to any of
those figures moves the labels with the run, except where the words would turn
false. Four scenes refuse such a run rather than draw it.

1. Chan's reading, whose arrow says the statistic sits right of the 10 percent
   value.
2. The fingerprint, whose check marks say each value is the one the script
   printed.
3. One row apart, whose title says the two regressions start one day apart.
4. Leaning, not crossing, whose title says each statistic sits on the
   reverting side of a random walk short of the line that would reject.

:func:`scenes` describes every stroke, tint and label as data,
:func:`timeline` orders one scene's steps into frames, and :func:`render`
draws them. A test reads the first two without drawing anything. A tint is a
flat rectangle drawn beneath every stroke, and only Lesson 3's two scenes have
any: the ±1 SD band in both, and the gauges' reject zones. A
label always appears after the stroke or tint it names, and each GIF holds on
its finished drawing for :data:`HOLD_MS` before it loops. :func:`clearances`
measures how far each label and title sits from the nearest stroke or tint on
the finished drawing, so a test can hold that no label touches a line it does
not name and none sits on a tint.

The sketch is deterministic. Matplotlib's path sketch adds the same wobble on
every draw, which two draws in separate processes confirmed byte for byte when
this module was written. The palette is fixed rather than fitted to each
frame, and nothing else here is random. So two draws on one machine give the
same bytes, and a redraw with no change is a no-op diff. Pillow writes the
GIFs, and it arrives as a dependency of matplotlib rather than as an entry of
its own in ``pyproject.toml``.
Another machine can differ, because the hand-drawn font is whichever of
:data:`HAND_FONTS` is installed, with matplotlib's own DejaVu Sans as the
fallback, and font rasterising varies across platforms. Redraw all fourteen with::

    uv run python -m chan.usdcad_tests_whiteboard

:mod:`chan.equity_seasonals_whiteboard` draws its thirty-two sketches with this
module's strokes, timeline and renderer, so an edit to those changes its GIFs
too. Redraw both sets after one. The second command needs the owner's archive
for nine of its thirty-two GIFs, and says so when it is missing::

    uv run python -m chan.usdcad_tests_whiteboard
    uv run python -m chan.equity_seasonals_whiteboard
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties, findfont
from matplotlib.patches import Rectangle
from PIL import Image
from scipy.stats import norm

from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.series import WindowCrossesScaleBreak
from chan.stationarity_tests import VRATIO_ALPHA
from chan.usdcad_hurst_noise import (
    PATHS,
    SEED,
    StartOffset,
    random_walk_genhurst,
    start_offset_hurst,
)
from chan.usdcad_mean_reversion import (
    BOOK_HURST,
    SCRIPT_ADF,
    SCRIPT_AR1,
    SCRIPT_HALF_LIFE,
    SCRIPT_VRATIO_P,
    StationarityRun,
    read_sources,
    stationarity_tests,
)
from chan.vintage import VintageEntry, VintageUnavailable

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "usdcad_tests_"

#: The frame in pixels, and the figure size and dpi that give it.
WIDTH, HEIGHT = 680, 320
DPI = 100

#: One drawing frame lasts this long, so strokes are drawn at 10 frames a second.
FRAME_MS = 100
#: A scene's title shows alone for this long before its first stroke.
TITLE_MS = 400
#: A label, or a tint, pops in on one frame that lasts this long.
LABEL_MS = 350
#: The finished drawing shows this long before the GIF loops back to its title.
HOLD_MS = 4000

BOARD = "#FFFFFF"
#: The inks every stroke and label is drawn in. Each frame is mapped onto
#: these and their blends with the white board, so every GIF carries one
#: palette rather than one fitted to every frame.
INKS = (INK, MUTED, ACCENT, GOOD, LOST)
BLENDS = (1.0, 0.8, 0.6, 0.4, 0.2)

#: Hand-drawn fonts in order of preference. None is downloaded, so the first
#: one installed is used, and matplotlib's own DejaVu Sans when none is.
HAND_FONTS = ("Humor Sans", "Comic Neue", "Comic Sans MS")
FALLBACK_FONT = "DejaVu Sans"

#: The board's coordinates. Ten units across and 4.7 up keep a unit about as
#: tall as it is wide at 680 by 320 pixels.
XLIM, YLIM = (0.0, 10.0), (0.0, 4.7)


@dataclass(frozen=True)
class Stroke:
    """A line drawn from its first point to its last over ``frames`` frames.

    A stroke of one point is a dot, drawn in a single frame when ``frames`` is
    1, as :func:`_dot` sets it. A stroke with a
    ``dots`` size is a row of dots of that size in points, one on each of its
    points and no line between them, revealed a few more on each frame.
    """

    gid: str
    x: np.ndarray
    y: np.ndarray
    color: str = INK
    width: float = 2.2
    dashed: bool = False
    frames: int = 8
    dots: float = 0.0

    @property
    def points(self) -> int:
        return len(self.x)


@dataclass(frozen=True)
class Fill:
    """A flat rectangle of ``color`` from (x0, y0) to (x1, y1), a tint that
    shades a region rather than a line that draws one.

    It appears whole on one frame, like a label, and it sits beneath every
    stroke, so a line drawn across it stays on top.
    """

    gid: str
    x0: float
    y0: float
    x1: float
    y1: float
    color: str


@dataclass(frozen=True)
class Label:
    """Text that appears at its own place in the scene's steps. ``names`` is the
    stroke or tint before it that it labels, which the tests hold is drawn first."""

    text: str
    x: float
    y: float
    names: str
    color: str = INK
    ha: str = "left"
    size: float = 13
    math: bool = False


@dataclass(frozen=True)
class Scene:
    """One scene: its title, the slug its GIF is named for, and its strokes,
    tints and labels in drawing order."""

    title: str
    slug: str
    steps: tuple[Stroke | Fill | Label, ...]

    @property
    def gif(self) -> str:
        """The GIF's file name, such as ``usdcad_tests_hurst.gif``."""
        return f"{GIF_PREFIX}{self.slug}.gif"

    @property
    def labels(self) -> list[str]:
        return [step.text for step in self.steps if isinstance(step, Label)]

    @property
    def strokes(self) -> list[Stroke]:
        return [step for step in self.steps if isinstance(step, Stroke)]

    @property
    def fills(self) -> list[Fill]:
        return [step for step in self.steps if isinstance(step, Fill)]


@dataclass(frozen=True)
class Frame:
    """One GIF frame: the steps ``scene.steps[:done]`` are complete, and when
    ``partial`` is above zero the stroke at ``done`` shows that many points."""

    done: int
    partial: int
    ms: int


def _line(points: Sequence[tuple[float, float]], per_unit: float = 6.0) -> tuple:
    """The polyline through ``points``, with points added along each segment
    so it can be revealed a little at a time. A segment gets points in
    proportion to its length, and each corner is kept exactly."""
    xs, ys = [points[0][0]], [points[0][1]]
    for (x0, y0), (x1, y1) in zip(points, points[1:], strict=False):
        steps = max(1, math.ceil(math.hypot(x1 - x0, y1 - y0) * per_unit))
        t = np.arange(1, steps + 1) / steps
        xs.extend(x0 + (x1 - x0) * t)
        ys.extend(y0 + (y1 - y0) * t)
    return np.array(xs), np.array(ys)


def _curve(x: np.ndarray, y: np.ndarray) -> tuple:
    return np.asarray(x, dtype=float), np.asarray(y, dtype=float)


def _arrow(x0: float, y0: float, x1: float, y1: float) -> tuple:
    """A shaft from (x0, y0) to (x1, y1) with a two-stroke head at the end."""
    angle, head = math.atan2(y1 - y0, x1 - x0), 0.22
    left = (x1 - head * math.cos(angle - 0.5), y1 - head * math.sin(angle - 0.5))
    right = (x1 - head * math.cos(angle + 0.5), y1 - head * math.sin(angle + 0.5))
    return _line([(x0, y0), (x1, y1), left, (x1, y1), right])


def _stroke(gid: str, xy: tuple, **style) -> Stroke:
    return Stroke(gid, xy[0], xy[1], **style)


def _dot(gid: str, x: float, y: float, color: str = ACCENT) -> Stroke:
    return Stroke(gid, np.array([x]), np.array([y]), color=color, frames=1)


def _path(x: np.ndarray) -> np.ndarray:
    """The schematic price the opening scene draws twice, around zero."""
    return 0.32 * np.sin(1.5 * x) + 0.14 * np.sin(3.9 * x + 1) + 0.06 * np.sin(8.3 * x)


#: Where the opening scene's two copies of the path sit, and its round trips
#: on the lower copy, each from entry to exit along the board.
TOP, BOTTOM = 3.15, 1.4
ROUND_TRIPS = ((1.0, 2.4), (4.3, 5.6), (7.3, 8.8))


def _every_day(closes: int) -> Scene:
    """The opening section's point: a test reads every close, a backtest its round trips.

    One schematic path is drawn twice. On the upper copy a dot lands on every
    point, and the label prints the run's count of closes. The lower copy is
    the same path in a fainter ink, with a bracket under each of a few round
    trips from entry to exit. The round trips stand for a generic rule that
    enters and exits. They are not the post's linear rule, which holds a
    position on every day once its lookback fills, and changes its size and
    its side as the close moves.
    """
    x = np.linspace(0.5, 9.5, 180)
    marks = np.linspace(0.5, 9.5, 46)
    steps: list[Stroke | Label] = [
        _stroke("top-path", _curve(x, TOP + _path(x)), frames=12),
        Stroke("closes", marks, TOP + _path(marks), color=ACCENT, frames=12, dots=5.0),
        Label(
            f"a test reads all {closes:,} closes",
            9.6,
            3.95,
            names="closes",
            ha="right",
            color=ACCENT,
            size=12,
        ),
        _stroke("bottom-path", _curve(x, BOTTOM + _path(x)), color=MUTED, frames=10),
    ]
    for k, (entry, exit_) in enumerate(ROUND_TRIPS, start=1):
        level = 0.72
        bracket = _line(
            [
                (entry, BOTTOM + float(_path(np.array([entry]))[0]) - 0.14),
                (entry, level),
                (exit_, level),
                (exit_, BOTTOM + float(_path(np.array([exit_]))[0]) - 0.14),
            ]
        )
        steps += [
            _stroke(f"trip-{k}", bracket, color=ACCENT, frames=5),
            Label(
                "round trip",
                (entry + exit_) / 2,
                0.36,
                names=f"trip-{k}",
                ha="center",
                color=ACCENT,
                size=12,
            ),
        ]
    steps.append(
        Label(
            "a backtest sees only its round trips",
            9.6,
            2.2,
            names=f"trip-{len(ROUND_TRIPS)}",
            ha="right",
            size=12,
        )
    )
    return Scene("Every day or a few round trips", "every_day", tuple(steps))


def _the_question() -> Scene:
    x = np.linspace(0.4, 9.6, 140)
    price = 2.0 + 0.55 * np.sin(1.7 * x) + 0.3 * np.sin(4.3 * x + 1) + 0.12 * np.sin(9.1 * x)
    return Scene(
        "The question",
        "question",
        (
            _stroke("mean", _line([(0.4, 2.0), (9.6, 2.0)]), color=MUTED, dashed=True, frames=6),
            _stroke("price", _curve(x, price), frames=14),
            Label("Random walk?", 0.6, 3.55, names="price"),
            _stroke("pull", _arrow(6.9, 3.35, 6.9, 2.15), color=ACCENT, frames=6),
            Label("Pulled back?", 7.15, 3.55, names="pull", color=ACCENT),
        ),
    )


def _adf() -> Scene:
    before = np.linspace(0.4, 5.5, 70)
    wiggle = 0.12 * np.sin(5.0 * before)
    rise = 1.4 + wiggle + 2.0 * np.exp(-(((before - 5.5) / 0.55) ** 2))
    after = np.linspace(5.5, 9.6, 60)
    fall = 1.4 + 2.0 * np.exp(-(after - 5.5) / 1.1) + 0.1 * np.sin(5.0 * (after - 5.5))
    peak = float(rise[-1])
    return Scene(
        "ADF",
        "adf",
        (
            _stroke("mean", _line([(0.4, 1.4), (9.6, 1.4)]), color=MUTED, dashed=True, frames=6),
            _stroke("rise", _curve(before, rise), frames=10),
            _dot("high", 5.5, peak),
            Label("high close…", 5.75, peak + 0.15, names="high", color=ACCENT),
            _stroke("fall", _curve(after, fall), frames=10),
            Label("…then a fall", 7.0, 2.35, names="fall"),
            Label("λ < 0", 8.3, 0.6, names="fall", color=ACCENT, size=16),
        ),
    )


def _hurst() -> Scene:
    t = np.linspace(0.0, 5.6, 60)
    x = 0.8 + t
    wide, narrow = 0.62 * np.sqrt(t), 0.5 * t**0.25
    return Scene(
        "Hurst",
        "hurst",
        (
            _dot("start", 0.8, 2.0, color=INK),
            _stroke("wide-up", _curve(x, 2.0 + wide), color=INK, frames=6),
            _stroke("wide-down", _curve(x, 2.0 - wide), color=INK, frames=6),
            Label("random walk, H = 0.5", 6.6, 3.47, names="wide-down"),
            _stroke("narrow-up", _curve(x, 2.0 + narrow), color=GOOD, frames=6),
            _stroke("narrow-down", _curve(x, 2.0 - narrow), color=GOOD, frames=6),
            Label("reverting, H < 0.5", 6.6, 2.77, names="narrow-down", color=GOOD),
            # The tilde goes through mathtext as \sim, because the words
            # outside the dollar signs are set in the hand font, which lacks ∼.
            # It sits under the starting point, apart from every curve, because
            # it describes both pairs. Beside a curve's end it read as that
            # curve's label.
            Label(r"variance $\sim \tau^{2H}$", 0.4, 0.45, names="narrow-down", size=15, math=True),
        ),
    )


def _variance_ratio() -> Scene:
    def bar(left: float, top: float) -> tuple:
        right = left + 1.5
        return _line([(left, 0.7), (left, top), (right, top), (right, 0.7)])

    return Scene(
        "Variance ratio",
        "variance_ratio",
        (
            _stroke("floor", _line([(1.4, 0.7), (8.6, 0.7)]), color=MUTED, frames=5),
            _stroke("two-day", bar(2.4, 2.2), color=GOOD, frames=8),
            Label("2-day variance", 3.15, 0.32, names="two-day", ha="center", color=GOOD),
            _stroke("one-day", bar(5.6, 3.1), color=INK, frames=8),
            Label("2 × 1-day variance", 6.35, 0.32, names="one-day", ha="center"),
            _stroke("gap", _line([(2.4, 3.1), (5.6, 3.1)]), color=MUTED, dashed=True, frames=5),
            Label("ratio < 1 → pulled back", 5.0, 3.62, names="gap", ha="center", color=ACCENT),
        ),
    )


def _half_life(lookback: int) -> Scene:
    halving = 2.2
    t = np.linspace(0.0, 8.0, 90)
    floor, start = 0.65, 2.9
    distance = floor + start * np.exp(-math.log(2) * t / halving)
    half = floor + start / 2
    corner = 1.0 + halving
    return Scene(
        "Half-life",
        "half_life",
        (
            _stroke(
                "axes", _line([(1.0, 3.75), (1.0, floor), (9.3, floor)]), color=MUTED, frames=6
            ),
            Label("distance from the mean", 1.2, 3.8, names="axes", color=MUTED, size=12),
            _stroke("decay", _curve(1.0 + t, distance), frames=12),
            _stroke(
                "half",
                _line([(1.0, half), (corner, half), (corner, floor)]),
                color=ACCENT,
                dashed=True,
                frames=6,
            ),
            Label("half", 0.8, half, names="half", ha="right", color=ACCENT, size=12),
            Label(f"≈ {lookback} days", corner, 0.3, names="half", ha="center", color=ACCENT),
            # The time to half sits just right of the vertical dashed line,
            # under the curve, so it reads as the span along the axis.
            Label("−ln 2 / λ", corner + 0.25, 1.1, names="half", size=15),
        ),
    )


def _linear_rule(lookback: int, closes: int) -> Scene:
    sigma = 0.55
    x = np.linspace(0.4, 9.6, 150)
    z = (
        2.0 * np.exp(-(((x - 2.5) / 0.9) ** 2))
        - 1.5 * np.exp(-(((x - 5.5) / 0.9) ** 2))
        + 0.3 * np.sin(np.pi * (x - 2.5) / 1.5)
    )
    warning = _line([(0.5, 0.2), (1.1, 0.2), (0.8, 0.75), (0.5, 0.2)], per_unit=10)
    return Scene(
        "The linear rule",
        "linear_rule",
        (
            _stroke("mean", _line([(0.4, 2.0), (9.6, 2.0)]), color=MUTED, dashed=True, frames=6),
            _stroke("price", _curve(x, 2.0 + sigma * z), frames=12),
            _dot("above", 2.5, 2.0 + 2.0 * sigma, color=LOST),
            Label("z = +2 → short 2", 2.8, 3.45, names="above", color=LOST),
            _dot("below", 5.5, 2.0 - 1.5 * sigma, color=GOOD),
            Label("z = −1.5 → long 1.5", 5.85, 1.0, names="below", color=GOOD),
            _stroke("warning", warning, color=LOST, width=2.4, frames=5),
            # The sign's "!" is drawn as two strokes rather than set as text,
            # because it sits inside the triangle, where a label would touch it.
            _stroke("bang", _line([(0.8, 0.6), (0.8, 0.4)], per_unit=10), color=LOST, frames=2),
            _stroke("bang-dot", _line([(0.8, 0.3), (0.8, 0.28)]), color=LOST, width=3.0, frames=1),
            Label(
                f"{lookback} days measured on all {closes:,} closes",
                1.35,
                0.45,
                names="warning",
                color=LOST,
            ),
        ),
    )


def _box(x0: float, y0: float, x1: float, y1: float) -> tuple:
    """A rectangle drawn from its lower left corner, counterclockwise."""
    return _line([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)])


def _span(x0: float, x1: float, y: float, tick: float = 0.13) -> tuple:
    """A bar from ``x0`` to ``x1`` at height ``y``, with an upright tick at each end."""
    return _line([(x0, y + tick), (x0, y - tick), (x0, y), (x1, y), (x1, y + tick), (x1, y - tick)])


def _check(x: float, y: float) -> tuple:
    """A check mark whose short stroke starts at (x, y)."""
    return _line([(x, y), (x + 0.1, y - 0.13), (x + 0.32, y + 0.2)], per_unit=10)


def _hatched(x0: float, y0: float, x1: float, y1: float) -> tuple:
    """A rectangle shaded with parallel diagonals, drawn as one stroke.

    After the outline, the pen climbs one diagonal, steps along the top edge,
    comes down the next diagonal parallel to the first, and steps along the
    bottom edge, so every move between diagonals retraces the outline.
    """
    rise, gap = (y1 - y0) / 2, 0.3
    points = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    feet = np.arange(x0 + gap, x1 - rise, gap)
    for k, foot in enumerate(feet):
        diagonal = [(foot, y0), (foot + rise, y1)]
        points += diagonal if k % 2 == 0 else diagonal[::-1]
    return _line(points)


def _signed(value: float, places: int) -> str:
    """``value`` to ``places`` decimals with a typographic minus, as the post
    prints a negative number."""
    return f"{value:.{places}f}".replace("-", "−")


def _no_rejection(statistic: float, critical: Sequence[float]) -> Scene:
    """Chan's first reading: the statistic sits right of the 10 percent value.

    Unlike the six scenes of the section on the tests, this one is drawn to
    scale. The line maps the span from the lowest of the four values to the
    highest, with a quarter of that span added at each end, onto the board, so
    every position on it is an affine function of the value it marks.

    The arrow and its words say the statistic must move left to reject, so a
    statistic at or left of the 10 percent value is refused rather than drawn
    under words it contradicts.
    """
    if statistic <= critical[2]:
        raise ValueError(
            f"Chan's reading draws the ADF statistic right of its 10 percent critical value of "
            f"{_signed(critical[2], 3)}, and this run's is {_signed(statistic, 6)}"
        )
    marks = [*critical, statistic]
    span = max(marks) - min(marks)
    low, high = min(marks) - span / 4, max(marks) + span / 4
    left, right, level = 0.9, 9.2, 1.9

    def at(value: float) -> float:
        return left + (value - low) / (high - low) * (right - left)

    ticks: list[Stroke | Label] = []
    levels = zip(("tick-1", "tick-5", "tick-10"), critical, ("1%", "5%", "10%"), strict=True)
    for gid, value, name in levels:
        top = 2.95 if gid == "tick-10" else level + 0.18
        ticks += [
            _stroke(gid, _line([(at(value), level - 0.18), (at(value), top)]), frames=3),
            # The 5 and 10 percent values sit close on this run. At 11 points
            # their labels stay apart in the wider DejaVu Sans too.
            Label(_signed(value, 3), at(value), 1.35, names=gid, ha="center", size=11),
            Label(name, at(value), 0.9, names=gid, ha="center", color=MUTED, size=11),
        ]
    edge = at(critical[2])
    dot = at(statistic)
    return Scene(
        "Chan’s reading",
        "no_rejection",
        (
            _stroke("line", _line([(0.5, level), (9.6, level)]), frames=8),
            *ticks,
            _stroke("zone", _hatched(0.5, 2.15, edge, 2.85), color=LOST, width=1.4, frames=10),
            Label(
                "reject a random walk", (0.5 + edge) / 2, 3.3, names="zone", ha="center", color=LOST
            ),
            _dot("statistic", dot, level),
            Label(_signed(statistic, 2), dot, 1.35, names="statistic", ha="center", color=ACCENT),
            Label("ADF statistic", dot, 0.9, names="statistic", ha="center", color=ACCENT, size=12),
            _stroke("needs", _arrow(dot - 0.25, 2.5, edge + 0.2, 2.5), color=ACCENT, frames=5),
            Label("must sit left of 10% to reject", edge + 0.3, 3.0, names="needs", color=ACCENT),
        ),
    )


def _fingerprint(run: StationarityRun) -> Scene:
    """Lesson 1's argument: four values from three calculations all match.

    Chan's MATLAB file is not public, so the closes here are compared with his
    only through what the script printed. Each calculation leads to the values it
    gives, at the six decimals the script prints, each with a check mark.

    A check mark says the value matches the script's, so a run any of whose
    four values prints otherwise at six decimals is refused rather than
    checked off.
    """
    printed = (
        ("an ADF statistic", run.adf.statistic, SCRIPT_ADF),
        ("an AR(1) estimate", run.adf.ar1, SCRIPT_AR1),
        ("a variance ratio p-value", run.vratio.p_value, SCRIPT_VRATIO_P),
        ("a half-life", run.half_life, SCRIPT_HALF_LIFE),
    )
    for name, value, script in printed:
        if f"{value:.6f}" != f"{script:.6f}":
            raise ValueError(
                f"Lesson 1's scene checks each value off as the one the script printed, and "
                f"this run gives {name} of {_signed(value, 6)} where the script printed "
                f"{_signed(script, 6)}"
            )
    calculations = (
        ("adf", "ADF regression", 3.4, (run.adf.statistic, run.adf.ar1)),
        ("vratio", "variance ratio", 2.3, (run.vratio.p_value,)),
        ("half-life", "half-life", 1.2, (run.half_life,)),
    )
    steps: list[Stroke | Label] = [
        _stroke("matlab", _box(0.2, 2.75, 2.95, 3.85), frames=5),
        Label("Chan’s MATLAB file", 1.575, 3.5, names="matlab", ha="center", size=12),
        Label("not public", 1.575, 3.1, names="matlab", ha="center", color=LOST, size=12),
        _stroke("csv", _box(0.2, 0.75, 2.95, 1.85), frames=5),
        Label("the CSV here", 1.575, 1.5, names="csv", ha="center", size=12),
        Label(f"{len(run.closes):,} closes", 1.575, 1.1, names="csv", ha="center", size=12),
        _stroke("link", _line([(0.6, 2.75), (0.6, 1.85)]), color=LOST, dashed=True, frames=4),
        _stroke("cross-a", _line([(0.42, 2.48), (0.78, 2.12)]), color=LOST, frames=2),
        _stroke("cross-b", _line([(0.42, 2.12), (0.78, 2.48)]), color=LOST, frames=2),
        Label("can’t compare", 1.02, 2.3, names="cross-b", color=LOST, size=12),
    ]
    for gid, name, middle, values in calculations:
        rows = [middle] if len(values) == 1 else [middle + 0.25, middle - 0.25]
        steps += [
            _stroke(f"to-{gid}", _arrow(3.05, 1.3, 3.8, middle), color=MUTED, frames=3),
            _stroke(gid, _box(3.9, middle - 0.35, 6.2, middle + 0.35), frames=5),
            Label(name, 5.05, middle, names=gid, ha="center", size=12),
            _stroke(f"{gid}-out", _arrow(6.3, middle, 6.85, middle), color=MUTED, frames=3),
        ]
        for k, (row, value) in enumerate(zip(rows, values, strict=True)):
            steps += [
                Label(_signed(value, 6), 7.05, row, names=f"{gid}-out"),
                _stroke(f"check-{gid}-{k}", _check(8.95, row - 0.02), color=GOOD, frames=3),
            ]
    steps.append(
        Label(
            "closes × a constant would match too",
            9.85,
            0.28,
            names="check-half-life-0",
            ha="right",
            color=MUTED,
            size=12,
        )
    )
    return Scene("The fingerprint", "fingerprint", tuple(steps))


#: The days the row of cells in Lesson 2's scene shows before its ellipsis.
SHOWN_DAYS = 6


def _one_row(run: StationarityRun) -> Scene:
    """Lesson 2's point: jplv7's ``adf`` fits one row fewer than ``adfuller``.

    A row of cells stands for the closes, days 1 to :data:`SHOWN_DAYS`, an
    ellipsis and the last day. The days before ``adfuller``'s first row are
    shaded, because no regression on one lagged change can use them. Under the
    row, one bar for each toolbox runs from the cell of its first day to the
    last cell, so the jplv7 bar starts one cell to the right, and the cell
    between them is marked as the one row.

    The title and the note say one row, so a run whose two regressions start
    other than one day apart, or after the days the row shows, is refused
    rather than drawn under words it contradicts.
    """
    early, late = run.adfuller_first_day, run.adf_first_day
    if late - early != 1 or not 1 < early < late <= SHOWN_DAYS:
        raise ValueError(
            f"Lesson 2's scene draws adfuller starting on a day from 2 to {SHOWN_DAYS - 1} and "
            f"jplv7 one day later, and this run starts them on days {early} and {late}"
        )
    width, left, bottom, top = 0.9, 0.3, 2.85, 3.4

    def at(day: int) -> float:
        """The left edge of the cell of ``day``, from 1 to :data:`SHOWN_DAYS`."""
        return left + (day - 1) * width

    right = at(SHOWN_DAYS + 1)
    last = (right + 0.7, right + 1.7)
    row = [(left, bottom), (right, bottom), (right, top), (left, top), (left, bottom)]
    for k in range(1, SHOWN_DAYS):
        edge = at(k + 1)
        row += [(edge, bottom), (edge, top)] if k % 2 else [(edge, top), (edge, bottom)]
    numbers = [
        Label(str(day), at(day) + width / 2, 3.8, names="days", ha="center", size=12)
        for day in range(1, SHOWN_DAYS + 1)
    ]

    middle = (at(early) + last[1]) / 2
    end = last[1] + 0.25
    return Scene(
        "One row apart",
        "one_row",
        (
            _stroke("days", _line(row), frames=10),
            *numbers,
            _stroke("last", _box(last[0], bottom, last[1], top), frames=4),
            Label("…", right + 0.35, (bottom + top) / 2, names="last", ha="center"),
            Label(f"{len(run.closes):,}", sum(last) / 2, 3.8, names="last", ha="center", size=12),
            _stroke("grey", _hatched(left, bottom, at(early), top), color=MUTED, width=1.4),
            Label(
                "no earlier\nchange\nto lag",
                (left + at(early)) / 2,
                2.2,
                names="grey",
                ha="center",
                color=MUTED,
                size=11,
            ),
            _stroke("adfuller", _span(at(early), last[1], 2.15), width=3.0, frames=8),
            Label(
                f"adfuller, {run.adfuller_nobs:,} rows",
                middle,
                1.65,
                names="adfuller",
                ha="center",
                size=12,
            ),
            Label(_signed(run.adfuller_statistic, 6), end, 2.15, names="adfuller"),
            _stroke("jplv7", _span(at(late), last[1], 1.1), color=GOOD, width=3.0, frames=8),
            Label(
                f"jplv7 adf, {run.adf.nobs:,} rows",
                (at(late) + last[1]) / 2,
                0.68,
                names="jplv7",
                ha="center",
                color=GOOD,
                size=12,
            ),
            Label(_signed(run.adf.statistic, 6), end, 1.1, names="jplv7", color=GOOD),
            Label("the script’s figure", end, 0.68, names="jplv7", color=GOOD, size=12),
            _stroke(
                "one-row", _box(at(early), bottom, at(late), top), color=ACCENT, width=3.2, frames=4
            ),
            Label(
                "the one row",
                (at(early) + at(late)) / 2,
                1.65,
                names="one-row",
                ha="center",
                color=ACCENT,
                size=12,
            ),
        ),
    )


#: The theoretical H of a random walk, which Lesson 3's scene marks with a
#: dashed line. It is a property of the model rather than a figure of the run.
RANDOM_WALK_H = 0.5
#: Lesson 3's histogram spans this many SDs of the random walks' H either side
#: of their mean, in bins a third of an SD wide, so the ±1 SD band starts and
#: ends on a bin edge.
SPREAD_SDS, BINS_PER_SD = 3, 3

#: Counts spelled out, as the post spells them, for the words that print one.
WORDS = (
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
)


def _word(count: int) -> str:
    """``count`` in words up to twelve, and in digits past it."""
    return WORDS[count] if 0 <= count < len(WORDS) else f"{count:,}"


@dataclass(frozen=True)
class Spread:
    """What Lesson 3's scene reads from :mod:`chan.usdcad_hurst_noise`.

    ``walks`` holds ``genhurst``'s H on each seeded random walk of ``length``
    log prices, and ``offsets`` the start-day sweep on the closes, its first
    row being the closes from their first day.
    """

    walks: np.ndarray
    length: int
    offsets: tuple[StartOffset, ...]


def spread(closes: pd.Series, paths: int = PATHS, seed: int = SEED) -> Spread:
    """The random walks and the start days of :func:`chan.usdcad_hurst_noise.measure`.

    The walks are :func:`chan.usdcad_hurst_noise.random_walk_genhurst`, the
    same walks and the same values as the measurement's ``genhurst``, without
    the port's estimator, which the scene does not draw. ``paths`` and
    ``seed`` default to the measurement's own.
    """
    return Spread(
        walks=random_walk_genhurst(len(closes), paths=paths, seed=seed),
        length=len(closes),
        offsets=tuple(start_offset_hurst(closes)),
    )


def _levels(xs: Sequence[float], apart: float) -> list[int]:
    """A row for each dot at ``xs``, the lowest whose dots all sit ``apart`` or
    more from it. The dots are placed in order of ``x``, so they stack like a
    swarm rather than in the order they are drawn."""
    rows: list[list[float]] = []
    level = [0] * len(xs)
    for k in sorted(range(len(xs)), key=lambda k: xs[k]):
        free = [r for r, row in enumerate(rows) if all(abs(xs[k] - x) >= apart for x in row)]
        if not free:
            rows.append([])
            free = [len(rows) - 1]
        rows[free[0]].append(xs[k])
        level[k] = free[0]
    return level


def _noise_band(run: StationarityRun, measured: Spread) -> Scene:
    """Lesson 3's point: H misses 0.49 by less than chance moves it.

    The scene is drawn to scale along its axis, which maps the random walks'
    mean less and plus :data:`SPREAD_SDS` SDs onto the board. Each bar of the
    histogram is a real bin of ``genhurst``'s values on the walks, a third of
    an SD wide, and its height is in proportion to its count. The walks beyond
    the axis are left out rather than piled into the end bins. The run's H,
    the book's 0.49 and 0.5 are lines at their values, and each start day's
    ``genhurst`` is a dot at its value under the axis, stacked where two would
    touch. The dots that print as the book's 0.49 at two decimals are drawn in
    the book's colour.

    A spread measured on walks of another length, or on closes starting on
    another day, is refused rather than drawn beside a run it does not
    describe.
    """
    first_day = measured.offsets[0].first_day
    if measured.length != len(run.closes) or first_day != run.closes.index[0]:
        raise ValueError(
            f"Lesson 3's scene needs walks as long as the run's {len(run.closes):,} closes and "
            f"start days counted from {run.closes.index[0].date()}, and these walks are "
            f"{measured.length:,} long with start days counted from {first_day.date()}"
        )
    mean, sd = float(measured.walks.mean()), float(measured.walks.std(ddof=1))
    reach = SPREAD_SDS * BINS_PER_SD
    edges = mean + sd * np.arange(-reach, reach + 1) / BINS_PER_SD
    counts, _ = np.histogram(measured.walks, bins=edges)
    left, right, base, tall = 0.6, 9.4, 2.55, 1.3

    def at(value: float) -> float:
        return left + (value - edges[0]) / (edges[-1] - edges[0]) * (right - left)

    def top(count: float) -> float:
        return base + count / counts.max() * tall

    outline = [(at(edges[0]), base)]
    for k, count in enumerate(counts):
        outline += [(at(edges[k]), top(count)), (at(edges[k + 1]), top(count))]
    outline.append((at(edges[-1]), base))

    # The band is a flat tint behind the outline and the lines, from the axis
    # to the tallest bar, so it reads as a shaded region rather than as more
    # data drawn over the bins.
    low, high = mean - sd, mean + sd
    band = Fill("band", at(low), base, at(high), top(counts.max()), color=TINT)

    xs = [at(row.genhurst) for row in measured.offsets]
    levels = _levels(xs, 0.2)
    dots = [
        _dot(f"start-{row.offset}", x, 0.7 + 0.19 * level, LOST if row.prints_as_book else ACCENT)
        for row, x, level in zip(measured.offsets, xs, levels, strict=True)
    ]
    hits = sum(row.prints_as_book for row in measured.offsets)
    # Under its number, the run's name ends and the book's begins, so the two
    # names read apart rather than as one phrase.
    marks = (
        ("half", RANDOM_WALK_H, MUTED, f"{RANDOM_WALK_H:.1f}", None, "center"),
        ("run", run.hurst, ACCENT, f"{run.hurst:.4f}", "this run", "right"),
        ("book", BOOK_HURST, LOST, f"{BOOK_HURST:.2f}", "the book", "left"),
    )
    lines: list[Stroke | Label] = []
    for gid, value, color, number, words, ha in marks:
        line = _line([(at(value), base), (at(value), 3.9)])
        lines += [
            _stroke(gid, line, color=color, dashed=gid == "half", frames=4),
            Label(number, at(value), 2.15, names=gid, ha="center", color=color, size=12),
        ]
        if words:
            shift = {"right": 0.3, "left": -0.3}[ha]
            lines.append(
                Label(words, at(value) + shift, 1.8, names=gid, ha=ha, color=color, size=12)
            )
    last = dots[-1].gid
    return Scene(
        "Chance and the start day",
        "noise_band",
        (
            _stroke("axis", _line([(left, base), (right, base)]), color=MUTED, frames=5),
            _stroke("walks", _line(outline, per_unit=10), frames=14),
            Label(f"{len(measured.walks):,} random walks", left, 3.62, names="walks", size=12),
            band,
            Label("±1 SD", at(high) + 0.4, 3.62, names="band", color=GOOD, size=12),
            *lines,
            *dots,
            Label(
                f"{_word(len(dots))} start days",
                min(xs) - 0.35,
                0.7,
                names=last,
                ha="right",
                color=ACCENT,
                size=12,
            ),
            Label(
                f"{_word(hits)} print as {BOOK_HURST:.2f}",
                max(xs) + 0.35,
                0.7,
                names=last,
                color=LOST,
                size=12,
            ),
        ),
    )


#: Where Lesson 3's three gauges run on the board, and how far above and below
#: a gauge its labels sit. Each gauge's own values are mapped onto this span.
GAUGE_LEFT, GAUGE_RIGHT = 2.5, 9.2
#: The share of a gauge's span added past its most reverting mark, so its
#: reject zone or band does not start on the line's end. H's line also runs
#: past its band by :data:`H_PAST`, because its band reaches above 0.5.
LEAN_PAST, H_PAST = 0.4, 0.25
#: The ADF's critical values are the 1, 5 and 10 percent ones in that order,
#: and the gauge reads the 10 percent one, the level the post and Chan cite.
ADF_LEVEL = "10%"


def _vratio_critical() -> float:
    """The negative critical value of ``vratiotest``'s two-sided test at
    :data:`chan.stationarity_tests.VRATIO_ALPHA`, the level its ``h`` reports
    a rejection at. The p-value is twice the normal tail beyond the statistic,
    so the test rejects below the normal quantile of half that level."""
    return float(norm.ppf(VRATIO_ALPHA / 2))


def _gauge_map(values: Sequence[float], past_high: float = 0.0):
    """The affine map from a gauge's values onto the board, spanning every
    value in ``values`` with :data:`LEAN_PAST` of their span added below the
    lowest and ``past_high`` of it above the highest."""
    span = max(values) - min(values)
    low, high = min(values) - LEAN_PAST * span, max(values) + past_high * span

    def at(value: float) -> float:
        return GAUGE_LEFT + (value - low) / (high - low) * (GAUGE_RIGHT - GAUGE_LEFT)

    return at


def _tick(gid: str, x: float, y: float, color: str = INK) -> Stroke:
    return _stroke(gid, _line([(x, y - 0.1), (x, y + 0.1)], per_unit=10), color=color, frames=2)


def _lean_not_cross(run: StationarityRun, measured: Spread) -> Scene:
    """Lesson 3's close: the three tests all lean toward reversion and none crosses.

    Three horizontal gauges, drawn one at a time, each with its random-walk
    value toward the right and more reverting values to the left. Each gauge
    is drawn to its own scale, since their units differ, so along one gauge a
    position is an affine function of the value it marks. The statistic's dot
    comes last on each.

    1. The ADF statistic, against the 10 percent critical value with its
       reject zone left of it. The line ends at 0.
    2. ``genhurst``'s H, against the band one SD either side of the random
       walks' mean from :func:`spread`, the measurement Lesson 3's histogram
       draws. A tick marks 0.5. H is an estimate rather than a test, so it has
       no critical value and the gauge draws none.
    3. The variance ratio's statistic, against the critical value of
       ``vratiotest``'s own two-sided test at its fixed level, with the reject
       zone below the negative one. The test also rejects above the positive
       one, which lies on the side a trending series gives, beyond the
       random-walk end this gauge stops at.

    The title says each statistic leans toward reversion without crossing, so
    a run whose ADF or variance ratio statistic sits at or past its critical
    value, or at or right of 0, or whose H sits at or above 0.5, is refused
    rather than drawn under words it contradicts.
    """
    mean, sd = float(measured.walks.mean()), float(measured.walks.std(ddof=1))
    adf_critical, vr_critical = run.adf.critical[2], _vratio_critical()
    adf, vr = run.adf.statistic, run.vratio.statistic
    for name, value, critical in (
        ("ADF statistic", adf, adf_critical),
        ("variance ratio's statistic", vr, vr_critical),
    ):
        if not critical < value < 0:
            raise ValueError(
                f"Lesson 3's gauges draw the {name} between its critical value of "
                f"{_signed(critical, 3)} and 0, and this run's is {_signed(value, 6)}"
            )
    if not run.hurst < RANDOM_WALK_H:
        raise ValueError(
            f"Lesson 3's gauges draw H below a random walk's {RANDOM_WALK_H}, and this run's "
            f"is {run.hurst:.6f}"
        )
    at_adf = _gauge_map((0.0, adf_critical, adf))
    at_h = _gauge_map((RANDOM_WALK_H, mean - sd, mean + sd, run.hurst), past_high=H_PAST)
    at_vr = _gauge_map((0.0, vr_critical, vr))
    rows = {"adf": 3.3, "h": 2.0, "vr": 0.7}
    above, below, zone = 0.45, -0.45, 0.08

    def line(gid: str) -> Stroke:
        y = rows[gid]
        return _stroke(f"{gid}-line", _line([(GAUGE_LEFT, y), (GAUGE_RIGHT, y)]), frames=6)

    def reject(gid: str, at, critical: float, words: str) -> list[Stroke | Fill | Label]:
        """The reject zone left of ``critical``, then its tick and its words."""
        y, edge = rows[gid], at(critical)
        return [
            Fill(f"{gid}-zone", GAUGE_LEFT, y - zone, edge, y + zone, color=REJECT_TINT),
            Label("reject", edge - 0.12, y + above, names=f"{gid}-zone", ha="right", color=LOST),
            _tick(f"{gid}-critical", edge, y, color=LOST),
            Label(words, edge + 0.12, y + above, names=f"{gid}-critical", color=LOST),
        ]

    def zero(gid: str, at) -> list[Stroke | Label]:
        y = rows[gid]
        return [
            _tick(f"{gid}-zero", at(0.0), y, color=MUTED),
            Label("0", at(0.0), y + below, names=f"{gid}-zero", ha="center", color=MUTED),
        ]

    def dot(gid: str, x: float, number: str) -> list[Stroke | Label]:
        y = rows[gid]
        return [
            _dot(f"{gid}-dot", x, y),
            Label(number, x, y + below, names=f"{gid}-dot", ha="center", color=ACCENT),
        ]

    h = rows["h"]
    return Scene(
        "Leaning, not crossing",
        "lean_not_cross",
        (
            line("adf"),
            Label("← more reverting", 4.6, 4.3, names="adf-line", color=MUTED, size=12),
            Label("random walk →", 9.7, 4.3, names="adf-line", ha="right", color=MUTED, size=12),
            Label("ADF statistic", 0.3, rows["adf"], names="adf-line", size=12),
            *zero("adf", at_adf),
            *reject("adf", at_adf, adf_critical, f"{_signed(adf_critical, 3)} at {ADF_LEVEL}"),
            *dot("adf", at_adf(adf), _signed(adf, 2)),
            line("h"),
            Label("H", 0.3, h + 0.25, names="h-line", size=12),
            Label(
                "no test:\nH is an estimate", 0.3, h - 0.25, names="h-line", color=MUTED, size=11
            ),
            _tick("h-half", at_h(RANDOM_WALK_H), h, color=MUTED),
            Label(
                f"{RANDOM_WALK_H:.1f}",
                at_h(RANDOM_WALK_H),
                h + below,
                names="h-half",
                ha="center",
                color=MUTED,
            ),
            Fill("h-band", at_h(mean - sd), h - zone, at_h(mean + sd), h + zone, color=TINT),
            Label(
                "±1 SD of a random walk",
                (at_h(mean - sd) + at_h(mean + sd)) / 2,
                h + above,
                names="h-band",
                ha="center",
                color=GOOD,
                size=12,
            ),
            *dot("h", at_h(run.hurst), f"{run.hurst:.4f}"),
            line("vr"),
            Label("variance ratio\nstatistic", 0.3, rows["vr"], names="vr-line", size=12),
            *zero("vr", at_vr),
            *reject(
                "vr",
                at_vr,
                vr_critical,
                f"{_signed(vr_critical, 2)} at {VRATIO_ALPHA:.0%}, two-sided",
            ),
            *dot("vr", at_vr(vr), _signed(vr, 2)),
        ),
    )


def _look_ahead(run: StationarityRun) -> Scene:
    """Lesson 5's look-ahead: the half-life is measured on every close the rule trades.

    The top three rows are the run, drawn to scale by date. The timeline runs
    from the first close to the last, the measuring bar spans all of it, and
    the trading bar starts on the run's first position. The bottom pair is a
    schematic of what avoiding the look-ahead needs, drawn dashed, because it
    is not this run's dates. :mod:`chan.usdcad_holdout` runs that fix on the
    closes after Chan's, with the lookback measured on his. So the pair carries
    no dates and no numbers, and where it splits the sample means nothing.
    """
    first, last, start = run.closes.index[0], run.closes.index[-1], run.first_position
    left, right = 1.95, 8.05
    middle = (left + right) / 2
    # The schematic pair middles the sample a little right of the middle, so
    # the label under the measuring bar clears the trading bar's first tick.
    cut = left + 0.6 * (right - left)

    def at(day: pd.Timestamp) -> float:
        return left + (day - first) / (last - first) * (right - left)

    return Scene(
        "The look-ahead",
        "look_ahead",
        (
            _stroke("timeline", _span(left, right, 3.7, tick=0.1), color=MUTED, frames=6),
            Label(
                str(first.date()),
                left - 0.22,
                3.7,
                names="timeline",
                ha="right",
                color=MUTED,
                size=12,
            ),
            Label(str(last.date()), right + 0.22, 3.7, names="timeline", color=MUTED, size=12),
            _stroke("measure", _span(left, right, 3.2), color=ACCENT, width=3.0, frames=8),
            Label(
                f"measure the half-life: all {len(run.closes):,} closes",
                middle,
                2.84,
                names="measure",
                ha="center",
                color=ACCENT,
                size=12,
            ),
            _stroke("trade", _span(at(start), right, 2.45), width=3.0, frames=8),
            Label(str(start.date()), at(start) - 0.22, 2.45, names="trade", ha="right", size=12),
            Label(
                f"trade with a {run.lookback}-day lookback",
                (at(start) + right) / 2,
                2.09,
                names="trade",
                ha="center",
                size=12,
            ),
            Label(
                "every day traded sits inside the days measured",
                middle,
                1.72,
                names="trade",
                ha="center",
                color=LOST,
                size=12,
            ),
            _stroke(
                "earlier", _span(left, cut, 1.2), color=ACCENT, width=3.0, dashed=True, frames=6
            ),
            Label(
                "measure on earlier days",
                (left + cut) / 2,
                0.8,
                names="earlier",
                ha="center",
                color=ACCENT,
                size=12,
            ),
            _stroke("after", _span(cut, right, 0.6), width=3.0, dashed=True, frames=6),
            Label("trade only after", (cut + right) / 2, 0.24, names="after", ha="center", size=12),
            Label(
                "a sketch of the fix, not a run",
                cut + 0.3,
                1.2,
                names="after",
                color=MUTED,
                size=12,
            ),
        ),
    )


def _half_lives(run: StationarityRun) -> Scene:
    """Lesson 5's other limit: the sample spans few half-lives.

    The line stands for the closes, drawn to scale by count rather than by
    date, because the half-life counts closes. A tick falls every
    ``run.lookback`` closes, the half-life rounded, and the title counts the
    ticks, the stretches long enough for a distance from the mean to halve.
    The larger label divides the count of closes by the unrounded half-life,
    the figure the post prints.
    """
    closes, lookback = len(run.closes), run.lookback
    left, right, level = 0.8, 9.2, 2.4

    def at(close: int) -> float:
        return left + close / closes * (right - left)

    ticks = [
        _stroke(
            f"tick-{k}",
            _line([(at(k * lookback), level - 0.15), (at(k * lookback), level + 0.15)]),
            color=ACCENT,
            frames=2,
        )
        for k in range(1, closes // lookback + 1)
    ]
    whole = len(ticks)
    title = f"{_word(whole).capitalize()} half-li{'fe' if whole == 1 else 'ves'}"
    return Scene(
        title,
        "half_lives",
        (
            _stroke("sample", _span(left, right, level, tick=0.15), frames=8),
            Label(str(run.closes.index[0].date()), left, 1.9, names="sample", color=MUTED, size=12),
            Label(
                str(run.closes.index[-1].date()),
                right,
                1.9,
                names="sample",
                ha="right",
                color=MUTED,
                size=12,
            ),
            ticks[0],
            Label(
                f"{lookback} days",
                (left + at(lookback)) / 2,
                2.95,
                names=ticks[0].gid,
                ha="center",
                color=ACCENT,
                size=12,
            ),
            *ticks[1:],
            Label(
                f"{closes / run.half_life:.1f} half-lives",
                (left + right) / 2,
                3.45,
                names=ticks[-1].gid,
                ha="center",
                size=15,
            ),
            Label(
                "only a few stretches for a distance from the mean to halve",
                (left + right) / 2,
                1.3,
                names=ticks[-1].gid,
                ha="center",
                color=MUTED,
                size=12,
            ),
        ),
    )


def scenes(run: StationarityRun, measured: Spread) -> tuple[Scene, ...]:
    """The fourteen scenes in the order the post reads them, every number drawn
    read from ``run`` or, for Lesson 3's, from ``measured``.

    The first sketches the post's opening section, the next six the section on
    the tests, two Lesson 1, one Lesson 2, two Lesson 3, and the last two
    Lesson 5.
    """
    return (
        _every_day(len(run.closes)),
        _the_question(),
        _adf(),
        _hurst(),
        _variance_ratio(),
        _half_life(run.lookback),
        _linear_rule(run.lookback, len(run.closes)),
        _no_rejection(run.adf.statistic, run.adf.critical),
        _fingerprint(run),
        _one_row(run),
        _noise_band(run, measured),
        _lean_not_cross(run, measured),
        _look_ahead(run),
        _half_lives(run),
    )


def timeline(scene: Scene) -> list[Frame]:
    """Every frame of one scene's GIF in order, with how long each one shows.

    The GIF opens on the scene's title alone. A stroke takes its ``frames``
    frames, each showing a longer prefix of its points, and a tint or a label
    takes one frame of :data:`LABEL_MS`. The last frame, the finished drawing,
    shows for :data:`HOLD_MS`, and then the GIF loops.
    """
    frames = [Frame(0, 0, TITLE_MS)]
    for done, step in enumerate(scene.steps):
        if not isinstance(step, Stroke):
            frames.append(Frame(done + 1, 0, LABEL_MS))
            continue
        for k in range(1, step.frames + 1):
            shown = math.ceil(step.points * k / step.frames)
            if shown == step.points:
                frames.append(Frame(done + 1, 0, FRAME_MS))
            else:
                frames.append(Frame(done, max(shown, 2), FRAME_MS))
    last = frames[-1]
    frames[-1] = Frame(last.done, last.partial, HOLD_MS)
    return frames


def hand_font() -> str:
    """The first of :data:`HAND_FONTS` installed here, or DejaVu Sans."""
    for family in HAND_FONTS:
        try:
            findfont(FontProperties(family=family), fallback_to_default=False)
        except ValueError:
            continue
        return family
    return FALLBACK_FONT


def _style() -> dict:
    """Matplotlib settings for the hand-drawn look, ``plt.xkcd`` without pyplot.

    The sketch wobbles every path. DejaVu Sans follows the hand font in the
    family list, so a glyph the hand font lacks, such as λ, falls back to it
    rather than to an empty box.
    """
    font = hand_font()
    return {
        "path.sketch": (1.0, 100.0, 2.0),
        "font.family": [font] if font == FALLBACK_FONT else [font, FALLBACK_FONT],
        "lines.solid_capstyle": "round",
        "lines.solid_joinstyle": "round",
        "lines.dash_capstyle": "round",
        "text.parse_math": False,
    }


def _blend(ink: str, blend: float) -> np.ndarray:
    """``ink`` laid on the white board at ``blend``, as RGB from 0 to 1."""
    board = np.array(matplotlib.colors.to_rgb(BOARD))
    return blend * np.array(matplotlib.colors.to_rgb(ink)) + (1 - blend) * board


def palette() -> Image.Image:
    """The GIF's palette as an image Pillow can quantize against: white, then
    each ink at each blend with white."""
    colours = [np.array(matplotlib.colors.to_rgb(BOARD))]
    for ink in INKS:
        colours += [_blend(ink, blend) for blend in BLENDS]
    flat = [round(255 * channel) for colour in colours for channel in colour]
    holder = Image.new("P", (1, 1))
    holder.putpalette(flat + flat[:3] * (256 - len(colours)))
    return holder


#: Lesson 3's ±1 SD tint: the band's green at the palette's lightest blend
#: with the board. Being a colour the palette already holds, it adds none, so
#: the other GIFs' palettes, and their bytes, stay as they were.
TINT = matplotlib.colors.to_hex(_blend(GOOD, BLENDS[-1]))
#: The reject zones' tint in the gauges that close Lesson 3: the red of a
#: critical value at the same blend, so it adds no colour to the palette either.
REJECT_TINT = matplotlib.colors.to_hex(_blend(LOST, BLENDS[-1]))


def _board(scene: Scene) -> tuple[FigureCanvasAgg, list]:
    """A canvas holding the scene's title, and one artist for each step, every
    stroke empty and every tint and label hidden. The title is the last artist.

    A tint is a rectangle at zorder 1, beneath the strokes' 2, so it is drawn
    first whatever order the steps come in.
    """
    fig = Figure(figsize=(WIDTH / DPI, HEIGHT / DPI), dpi=DPI)
    fig.patch.set_facecolor(BOARD)
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(*XLIM)
    ax.set_ylim(*YLIM)
    ax.set_axis_off()
    artists = []
    for step in scene.steps:
        if isinstance(step, Stroke):
            (line,) = ax.plot([], [], color=step.color, lw=step.width, gid=step.gid)
            if step.dashed:
                line.set_linestyle((0, (4, 3)))
            if step.points == 1 or step.dots:
                line.set_linestyle("none")
                line.set_marker("o")
                line.set_markersize(step.dots or 9)
            artists.append(line)
        elif isinstance(step, Fill):
            artists.append(
                ax.add_patch(
                    Rectangle(
                        (step.x0, step.y0),
                        step.x1 - step.x0,
                        step.y1 - step.y0,
                        facecolor=step.color,
                        edgecolor="none",
                        zorder=1,
                        gid=step.gid,
                        visible=False,
                    )
                )
            )
        else:
            text = ax.text(
                step.x,
                step.y,
                step.text,
                color=step.color,
                fontsize=step.size,
                ha=step.ha,
                va="center",
                parse_math=step.math,
                visible=False,
            )
            artists.append(text)
    title = ax.text(0.3, 4.3, scene.title, color=INK, fontsize=16, fontweight="bold", va="center")
    return canvas, artists + [title]


def _show(scene: Scene, artists: Sequence, frame: Frame) -> None:
    for index, (step, artist) in enumerate(zip(scene.steps, artists, strict=False)):
        if not isinstance(step, Stroke):
            artist.set_visible(index < frame.done)
            continue
        shown = step.points if index < frame.done else 0
        if index == frame.done:
            shown = frame.partial
        artist.set_data(step.x[:shown], step.y[:shown])


def render(scene: Scene, frames: Sequence[Frame]) -> list[Image.Image]:
    """Draw every frame of one scene, each mapped onto :func:`palette`."""
    colours = palette()
    images = []
    with matplotlib.rc_context(_style()):
        canvas, artists = _board(scene)
        for frame in frames:
            _show(scene, artists, frame)
            canvas.draw()
            rgb = Image.fromarray(np.asarray(canvas.buffer_rgba())[..., :3])
            images.append(rgb.quantize(palette=colours, dither=Image.Dither.NONE))
    return images


def clearances(scene: Scene) -> dict[str, float]:
    """How far each label, and the title, sits from the nearest stroke or
    tint on the finished drawing, in pixels. A text that appears more than
    once, such as each "round trip" of the opening scene, reports its nearest
    copy.

    A text's box is the one matplotlib lays it out in. A stroke is its points
    with each segment filled in every pixel or so, and the distance is measured
    to the edge of its ink, half its line width out from the line, or the
    dot's radius for a dot. The wobble the sketch adds is not in the points,
    so a label needs a few pixels to spare to stay clear of it on the board.

    A tint counts the same as a stroke, measured to its rectangle's edge, and
    a label over it reads zero. A label could stay readable over a pale tint,
    but this keeps every label off it, so the tint never has to be checked
    against the text it would sit behind.
    """
    with matplotlib.rc_context(_style()):
        canvas, artists = _board(scene)
        _show(scene, artists, Frame(len(scene.steps), 0, 0))
        canvas.draw()
        renderer = canvas.get_renderer()
        to_pixels = artists[0].axes.transData
        inks = []
        for step in scene.strokes:
            xy = to_pixels.transform(np.column_stack([step.x, step.y]))
            if step.dots:
                reach = step.dots * DPI / 72 / 2
            elif step.points > 1:
                gaps = np.hypot(*np.diff(xy, axis=0).T)
                xy = np.vstack(
                    [
                        np.linspace(a, b, max(2, math.ceil(gap)), endpoint=False)
                        for a, b, gap in zip(xy[:-1], xy[1:], gaps, strict=True)
                    ]
                    + [xy[-1:]]
                )
                reach = step.width * DPI / 72 / 2
            else:
                reach = 9 * DPI / 72 / 2
            inks.append((xy, reach))
        tints = [
            to_pixels.transform([(fill.x0, fill.y0), (fill.x1, fill.y1)]) for fill in scene.fills
        ]
        texts = [
            (step.text, artist)
            for step, artist in zip(scene.steps, artists, strict=False)
            if isinstance(step, Label)
        ] + [(scene.title, artists[-1])]
        found = {}
        for text, artist in texts:
            box = artist.get_window_extent(renderer)
            nearest = math.inf
            for xy, reach in inks:
                dx = np.maximum.reduce([box.x0 - xy[:, 0], xy[:, 0] - box.x1, np.zeros(len(xy))])
                dy = np.maximum.reduce([box.y0 - xy[:, 1], xy[:, 1] - box.y1, np.zeros(len(xy))])
                nearest = min(nearest, float(np.hypot(dx, dy).min()) - reach)
            for (x0, y0), (x1, y1) in tints:
                dx = max(box.x0 - x1, x0 - box.x1, 0.0)
                dy = max(box.y0 - y1, y0 - box.y1, 0.0)
                nearest = min(nearest, math.hypot(dx, dy))
            found[text] = min(nearest, found.get(text, math.inf))
    return found


def make_usdcad_tests_whiteboards(
    out_dir: Path | None = None,
    sources: tuple[VintageEntry, pd.Series] | None = None,
    measured: Spread | None = None,
) -> list[Path]:
    """Write one looping GIF for each of the fourteen scenes and return their
    paths, in the order the post reads them.

    ``measured`` is the :func:`spread` of the closes, measured from them when
    it is not handed in. The run comes first, so its scale-break guard refuses
    a flagged window before the walks are drawn.
    """
    entry, closes = sources if sources is not None else read_sources()
    folder = out_dir if out_dir is not None else FIGURES_DIR
    run = stationarity_tests(entry, closes)
    paths = []
    for scene in scenes(run, measured if measured is not None else spread(closes)):
        frames = timeline(scene)
        first, *rest = render(scene, frames)
        path = folder / scene.gif
        first.save(
            path,
            save_all=True,
            append_images=rest,
            duration=[frame.ms for frame in frames],
            loop=0,
            optimize=False,
        )
        paths.append(path)
    return paths


def main() -> None:
    try:
        paths = make_usdcad_tests_whiteboards()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # As in chan.usdcad_mean_reversion_figures.main, a refusal that names
        # the source or the flagged day reaches the operator as one line.
        raise SystemExit(str(refused)) from refused
    for path in paths:
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
