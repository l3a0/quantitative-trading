"""A whiteboard sketch of the four tests and the rule in the USD.CAD post.

The post's section "The tests and the file" explains four ways of asking one
question, whether USD.CAD wanders like a random walk or is pulled back to a
mean, and then the linear rule that trades the answer. Each test is a short
paragraph of regression terms. A reader who has not met them gets more from a
picture of what each one looks for than from the terms, so this module draws
the section as an animated GIF in six scenes, each sketched stroke by stroke as
if on a whiteboard.

1. The question: a wiggly price around a dashed mean.
2. ADF: a high close followed by a fall, which is what a negative λ means.
3. Hurst: two pairs of curves spreading from one point, the narrower pair a
   reverting series whose variance grows like τ²ᴴ with H below 0.5.
4. Variance ratio: the 2-day variance shorter than twice the 1-day variance.
5. Half-life: the distance from the mean decaying, halved after −ln 2 / λ
   days, which the run measures at its lookback.
6. The linear rule: a z-score of +2 sold short and one of −1.5 bought, with a
   warning that the lookback was measured on every close the rule trades.

The shapes are schematic and carry no data. Two numbers do: the lookback the
half-life rounds to and the count of closes. Both come from the
:class:`chan.usdcad_mean_reversion.StationarityRun` that
:func:`chan.usdcad_mean_reversion.stationarity_tests` returns, read through the
run's own path, so the scale-break guard runs here too. A change to the
vintage or to how the half-life rounds moves the labels with the run.

:func:`scenes` describes every stroke and label as data, :func:`timeline`
orders them into frames, and :func:`render` draws them. A test reads the first
two without drawing anything. A label always appears after the stroke it
names, and each scene holds on its last frame before the next one starts.

The sketch is deterministic. Matplotlib's path sketch adds the same wobble on
every draw, which two draws in separate processes confirmed byte for byte when
this module was written. The palette is fixed rather than fitted to each
frame, and nothing else here is random. So two draws on one machine give the
same bytes, and a redraw with no change is a no-op diff. Pillow writes the
GIF, and it arrives as a dependency of matplotlib rather than as an entry of
its own in ``pyproject.toml``.
Another machine can differ, because the hand-drawn font is whichever of
:data:`HAND_FONTS` is installed, with matplotlib's own DejaVu Sans as the
fallback, and font rasterising varies across platforms. Redraw it with::

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

WHITEBOARD_GIF = "usdcad_tests_whiteboard.gif"

#: The frame in pixels, and the figure size and dpi that give it.
WIDTH, HEIGHT = 680, 320
DPI = 100

#: One drawing frame lasts this long, so strokes are drawn at 10 frames a second.
FRAME_MS = 100
#: A scene's title shows alone for this long before its first stroke.
TITLE_MS = 400
#: A label pops in on one frame that lasts this long.
LABEL_MS = 350
#: The last frame of each scene holds this much longer.
HOLD_MS = 1400

BOARD = "#FFFFFF"
#: The inks every stroke and label is drawn in. Each frame is mapped onto
#: these and their blends with the white board, so the GIF carries one
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
    """One scene: its title and its strokes and labels in drawing order."""

    title: str
    steps: tuple[Stroke | Label, ...]

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

    scene: int
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
        "1  The question",
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
        "2  ADF",
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
        "3  Hurst",
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
            Label(r"variance $\sim \tau^{2H}$", 6.6, 1.0, names="narrow-down", size=15, math=True),
        ),
    )


def _variance_ratio() -> Scene:
    def bar(left: float, top: float) -> tuple:
        right = left + 1.5
        return _line([(left, 0.7), (left, top), (right, top), (right, 0.7)])

    return Scene(
        "4  Variance ratio",
        (
            _stroke("floor", _line([(1.4, 0.7), (8.6, 0.7)]), color=MUTED, frames=5),
            _stroke("two-day", bar(2.4, 2.2), color=GOOD, frames=8),
            Label("2-day variance", 3.15, 0.38, names="two-day", ha="center", color=GOOD),
            _stroke("one-day", bar(5.6, 3.1), color=INK, frames=8),
            Label("2 × 1-day variance", 6.35, 0.38, names="one-day", ha="center"),
            _stroke("gap", _line([(2.4, 3.1), (5.6, 3.1)]), color=MUTED, dashed=True, frames=5),
            Label("ratio < 1 → pulled back", 5.0, 3.62, names="gap", ha="center", color=ACCENT),
        ),
    )


def _half_life(lookback: int) -> Scene:
    halving = 2.2
    t = np.linspace(0.0, 8.0, 90)
    distance = 0.5 + 3.0 * np.exp(-math.log(2) * t / halving)
    corner = 1.0 + halving
    return Scene(
        "5  Half-life",
        (
            _stroke("axes", _line([(1.0, 3.75), (1.0, 0.5), (9.3, 0.5)]), color=MUTED, frames=6),
            Label("distance from the mean", 1.2, 3.8, names="axes", color=MUTED, size=12),
            _stroke("decay", _curve(1.0 + t, distance), frames=12),
            _stroke(
                "half",
                _line([(1.0, 2.0), (corner, 2.0), (corner, 0.5)]),
                color=ACCENT,
                dashed=True,
                frames=6,
            ),
            Label("half", 0.88, 2.0, names="half", ha="right", color=ACCENT, size=12),
            Label(f"≈ {lookback} days", corner, 0.22, names="half", ha="center", color=ACCENT),
            Label("−ln 2 / λ", corner + 0.3, 2.4, names="half", size=15),
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
    warning = _line([(0.55, 0.25), (1.05, 0.25), (0.8, 0.7), (0.55, 0.25)], per_unit=10)
    return Scene(
        "6  The linear rule",
        (
            _stroke("mean", _line([(0.4, 2.0), (9.6, 2.0)]), color=MUTED, dashed=True, frames=6),
            _stroke("price", _curve(x, 2.0 + sigma * z), frames=12),
            _dot("above", 2.5, 2.0 + 2.0 * sigma, color=LOST),
            Label("z = +2 → short 2", 2.8, 3.45, names="above", color=LOST),
            _dot("below", 5.5, 2.0 - 1.5 * sigma, color=GOOD),
            Label("z = −1.5 → long 1.5", 5.85, 1.0, names="below", color=GOOD),
            _stroke("warning", warning, color=LOST, width=2.4, frames=5),
            Label("!", 0.8, 0.43, names="warning", ha="center", color=LOST, size=12),
            Label(
                f"{lookback} days measured on all {closes:,} closes",
                1.3,
                0.45,
                names="warning",
                color=LOST,
            ),
        ),
    )


def scenes(run: StationarityRun) -> tuple[Scene, ...]:
    """The six scenes, with the lookback and the count of closes from ``run``."""
    return (
        _the_question(),
        _adf(),
        _hurst(),
        _variance_ratio(),
        _half_life(run.lookback),
        _linear_rule(run.lookback, len(run.closes)),
    )


def timeline(drawn: Sequence[Scene]) -> list[Frame]:
    """Every frame in order, with how long each one shows.

    A scene opens on its title alone. A stroke takes its ``frames`` frames,
    each showing a longer prefix of its points, and a label takes one frame of
    :data:`LABEL_MS`. The scene's last frame holds :data:`HOLD_MS` longer.
    """
    frames: list[Frame] = []
    for index, scene in enumerate(drawn):
        frames.append(Frame(index, 0, 0, TITLE_MS))
        for done, step in enumerate(scene.steps):
            if isinstance(step, Label):
                frames.append(Frame(index, done + 1, 0, LABEL_MS))
                continue
            for k in range(1, step.frames + 1):
                shown = math.ceil(step.points * k / step.frames)
                if shown == step.points:
                    frames.append(Frame(index, done + 1, 0, FRAME_MS))
                else:
                    frames.append(Frame(index, done, max(shown, 2), FRAME_MS))
        last = frames[-1]
        frames[-1] = Frame(last.scene, last.done, last.partial, last.ms + HOLD_MS)
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


def _draw_scene(scene: Scene, frames: Sequence[Frame], colours: Image.Image) -> list[Image.Image]:
    fig = Figure(figsize=(WIDTH / DPI, HEIGHT / DPI), dpi=DPI)
    fig.patch.set_facecolor(BOARD)
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(*XLIM)
    ax.set_ylim(*YLIM)
    ax.set_axis_off()
    ax.text(0.3, 4.3, scene.title, color=INK, fontsize=16, fontweight="bold", va="center")
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

    images = []
    for frame in frames:
        for index, (step, artist) in enumerate(zip(scene.steps, artists, strict=True)):
            if isinstance(step, Label):
                artist.set_visible(index < frame.done)
                continue
            shown = step.points if index < frame.done else 0
            if index == frame.done:
                shown = frame.partial
            artist.set_data(step.x[:shown], step.y[:shown])
        canvas.draw()
        rgb = Image.fromarray(np.asarray(canvas.buffer_rgba())[..., :3])
        images.append(rgb.quantize(palette=colours, dither=Image.Dither.NONE))
    return images


def render(drawn: Sequence[Scene], frames: Sequence[Frame]) -> list[Image.Image]:
    """Draw every frame, each mapped onto :func:`palette`."""
    colours = palette()
    images: list[Image.Image] = []
    with matplotlib.rc_context(_style()):
        for index, scene in enumerate(drawn):
            images += _draw_scene(scene, [f for f in frames if f.scene == index], colours)
    return images


def make_usdcad_tests_whiteboard(
    out: Path | None = None,
    sources: tuple[VintageEntry, pd.Series] | None = None,
) -> Path:
    """Write the looping GIF of the six scenes and return its path."""
    entry, closes = sources if sources is not None else read_sources()
    drawn = scenes(stationarity_tests(entry, closes))
    frames = timeline(drawn)
    first, *rest = render(drawn, frames)
    path = out if out is not None else FIGURES_DIR / WHITEBOARD_GIF
    first.save(
        path,
        save_all=True,
        append_images=rest,
        duration=[frame.ms for frame in frames],
        loop=0,
        optimize=False,
    )
    return path


def main() -> None:
    try:
        path = make_usdcad_tests_whiteboard()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # As in chan.usdcad_mean_reversion_figures.main, a refusal that names
        # the source or the flagged day reaches the operator as one line.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
