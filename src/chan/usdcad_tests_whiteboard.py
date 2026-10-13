"""Whiteboard sketches of the tests, the rule and Lesson 1 in the USD.CAD post.

The post's section "The tests and the file" explains four ways of asking one
question, whether USD.CAD wanders like a random walk or is pulled back to a
mean, and then the linear rule that trades the answer. Each test is a short
paragraph of regression terms. A reader who has not met them gets more from a
picture of what each one looks for than from the terms, so this module draws
those as six scenes, and two more for the post's Lesson 1. Each scene is
sketched stroke by stroke as if on a whiteboard, and each is its own looping
GIF, so the post can place it right after the text it draws.

1. The question: a wiggly price around a dashed mean.
2. ADF: a high close followed by a fall, which is what a negative λ means.
3. Hurst: two pairs of curves spreading from one point, the narrower pair a
   reverting series whose variance grows like τ²ᴴ with H below 0.5.
4. Variance ratio: the 2-day variance shorter than twice the 1-day variance.
5. Half-life: the distance from the mean decaying, halved after −ln 2 / λ
   days, which the run measures at its lookback.
6. The linear rule: a z-score of +2 sold short and one of −1.5 bought, with a
   warning that the lookback was measured on every close the rule trades.
7. Chan's reading: the ADF statistic on a number line with the three critical
   values, right of the 10 percent value it would have to pass to reject a
   random walk.
8. The fingerprint: Chan's MATLAB file cannot be compared with the CSV here,
   so the CSV goes through the three calculations and each lands the values
   the script printed, which no change of units would alter.

The numbers above order this list and nothing else. A GIF stands alone, so its
title is the scene's name with no number, and its file is named for the scene,
such as ``usdcad_tests_hurst.gif``.

The first six scenes' shapes are schematic and carry no data. Two numbers in
them do: the lookback the half-life rounds to and the count of closes. Chan's
reading is drawn to scale, so the position of each tick and of the statistic's
dot is an affine function of its value, and it prints the three critical
values and the statistic. The fingerprint prints the count of closes, the ADF
statistic, the AR(1) estimate, the variance ratio's p-value and the half-life.
Every one of these comes from the
:class:`chan.usdcad_mean_reversion.StationarityRun` that
:func:`chan.usdcad_mean_reversion.stationarity_tests` returns, read through the
run's own path, so the scale-break guard runs here too. A change to the
vintage, to how the half-life rounds or to any of those figures moves the
labels with the run.

:func:`scenes` describes every stroke and label as data, :func:`timeline`
orders one scene's steps into frames, and :func:`render` draws them. A test
reads the first two without drawing anything. A label always appears after the
stroke it names, and each GIF holds on its finished drawing for
:data:`HOLD_MS` before it loops. :func:`clearances` measures how far each
label and title sits from the nearest stroke on the finished drawing, so a
test can hold that no label touches a line it does not name.

The sketch is deterministic. Matplotlib's path sketch adds the same wobble on
every draw, which two draws in separate processes confirmed byte for byte when
this module was written. The palette is fixed rather than fitted to each
frame, and nothing else here is random. So two draws on one machine give the
same bytes, and a redraw with no change is a no-op diff. Pillow writes the
GIFs, and it arrives as a dependency of matplotlib rather than as an entry of
its own in ``pyproject.toml``.
Another machine can differ, because the hand-drawn font is whichever of
:data:`HAND_FONTS` is installed, with matplotlib's own DejaVu Sans as the
fallback, and font rasterising varies across platforms. Redraw all eight with::

    uv run python -m chan.usdcad_tests_whiteboard
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
from PIL import Image

from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.series import WindowCrossesScaleBreak
from chan.usdcad_mean_reversion import StationarityRun, read_sources, stationarity_tests
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
#: A label pops in on one frame that lasts this long.
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

    A stroke of one point is a dot, drawn in a single frame.
    """

    gid: str
    x: np.ndarray
    y: np.ndarray
    color: str = INK
    width: float = 2.2
    dashed: bool = False
    frames: int = 8

    @property
    def points(self) -> int:
        return len(self.x)


@dataclass(frozen=True)
class Label:
    """Text that appears once the stroke it names, ``names``, is drawn."""

    text: str
    x: float
    y: float
    names: str
    color: str = INK
    ha: str = "left"
    va: str = "center"
    size: float = 13
    math: bool = False


@dataclass(frozen=True)
class Scene:
    """One scene: its title, the slug its GIF is named for, and its strokes
    and labels in drawing order."""

    title: str
    slug: str
    steps: tuple[Stroke | Label, ...]

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


def _arrow(x0: float, y0: float, x1: float, y1: float, head: float = 0.22) -> tuple:
    """A shaft from (x0, y0) to (x1, y1) with a two-stroke head at the end."""
    angle = math.atan2(y1 - y0, x1 - x0)
    left = (x1 - head * math.cos(angle - 0.5), y1 - head * math.sin(angle - 0.5))
    right = (x1 - head * math.cos(angle + 0.5), y1 - head * math.sin(angle + 0.5))
    return _line([(x0, y0), (x1, y1), left, (x1, y1), right])


def _stroke(gid: str, xy: tuple, **style) -> Stroke:
    return Stroke(gid, xy[0], xy[1], **style)


def _dot(gid: str, x: float, y: float, color: str = ACCENT) -> Stroke:
    return Stroke(gid, np.array([x]), np.array([y]), color=color, frames=1)


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
            # The time to half sits in the corner the dashed line closes,
            # below the curve, so it reads as the span along the axis.
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


def _check(x: float, y: float) -> tuple:
    """A check mark whose short stroke starts at (x, y)."""
    return _line([(x, y), (x + 0.1, y - 0.13), (x + 0.32, y + 0.2)], per_unit=10)


def _hatched(x0: float, y0: float, x1: float, y1: float, gap: float = 0.3) -> tuple:
    """A rectangle shaded with parallel diagonals, drawn as one stroke.

    After the outline, the pen climbs one diagonal, steps along the top edge,
    comes down the next diagonal parallel to the first, and steps along the
    bottom edge, so every move between diagonals retraces the outline.
    """
    rise = (y1 - y0) / 2
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
    """
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
            Label(_signed(value, 3), at(value), 1.35, names=gid, ha="center", size=12),
            Label(name, at(value), 0.9, names=gid, ha="center", color=MUTED, size=12),
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
    """
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


def scenes(run: StationarityRun) -> tuple[Scene, ...]:
    """The eight scenes in the order the post reads them, every number drawn
    read from ``run``.

    The first six sketch the section on the tests, and the last two Lesson 1.
    """
    return (
        _the_question(),
        _adf(),
        _hurst(),
        _variance_ratio(),
        _half_life(run.lookback),
        _linear_rule(run.lookback, len(run.closes)),
        _no_rejection(run.adf.statistic, run.adf.critical),
        _fingerprint(run),
    )


def timeline(scene: Scene) -> list[Frame]:
    """Every frame of one scene's GIF in order, with how long each one shows.

    The GIF opens on the scene's title alone. A stroke takes its ``frames``
    frames, each showing a longer prefix of its points, and a label takes one
    frame of :data:`LABEL_MS`. The last frame, the finished drawing, shows for
    :data:`HOLD_MS`, and then the GIF loops.
    """
    frames = [Frame(0, 0, TITLE_MS)]
    for done, step in enumerate(scene.steps):
        if isinstance(step, Label):
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


def palette() -> Image.Image:
    """The GIF's palette as an image Pillow can quantize against: white, then
    each ink at each blend with white."""
    board = np.array(matplotlib.colors.to_rgb(BOARD))
    colours = [board]
    for ink in INKS:
        rgb = np.array(matplotlib.colors.to_rgb(ink))
        colours += [blend * rgb + (1 - blend) * board for blend in BLENDS]
    flat = [round(255 * channel) for colour in colours for channel in colour]
    holder = Image.new("P", (1, 1))
    holder.putpalette(flat + flat[:3] * (256 - len(colours)))
    return holder


def _board(scene: Scene) -> tuple[FigureCanvasAgg, list]:
    """A canvas holding the scene's title, and one artist for each step, every
    stroke empty and every label hidden. The title is the last artist."""
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
            if step.points == 1:
                line.set_linestyle("none")
                line.set_marker("o")
                line.set_markersize(9)
            artists.append(line)
        else:
            text = ax.text(
                step.x,
                step.y,
                step.text,
                color=step.color,
                fontsize=step.size,
                ha=step.ha,
                va=step.va,
                parse_math=step.math,
                visible=False,
            )
            artists.append(text)
    title = ax.text(0.3, 4.3, scene.title, color=INK, fontsize=16, fontweight="bold", va="center")
    return canvas, artists + [title]


def _show(scene: Scene, artists: Sequence, frame: Frame) -> None:
    for index, (step, artist) in enumerate(zip(scene.steps, artists, strict=False)):
        if isinstance(step, Label):
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
    """How far each label, and the title, sits from the nearest stroke on the
    finished drawing, in pixels.

    A text's box is the one matplotlib lays it out in. A stroke is its points
    with each segment filled in every pixel or so, and the distance is measured
    to the edge of its ink, half its line width out from the line, or the
    dot's radius for a dot. The wobble the sketch adds is not in the points,
    so a label needs a few pixels to spare to stay clear of it on the board.
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
            if step.points > 1:
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
            found[text] = nearest
    return found


def make_usdcad_tests_whiteboards(
    out_dir: Path | None = None,
    sources: tuple[VintageEntry, pd.Series] | None = None,
) -> list[Path]:
    """Write one looping GIF for each of the eight scenes and return their
    paths, in the order the post reads them."""
    entry, closes = sources if sources is not None else read_sources()
    folder = out_dir if out_dir is not None else FIGURES_DIR
    paths = []
    for scene in scenes(stationarity_tests(entry, closes)):
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
