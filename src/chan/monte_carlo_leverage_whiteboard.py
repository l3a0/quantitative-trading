"""Whiteboard sketches for the Monte Carlo leverage post, one for Lesson 4 and one for Lesson 5.

``blog/monte-carlo-leverage-lessons.md`` makes two claims a sentence has to
build in the reader's head: the least of 100,000 draws sits deeper than Chan's
worst day because there are so many more draws, and Box 8.6's CPPI loop keeps
trading near its full leverage while the account falls through its floor. This
module draws the two as scenes, and the post places each right after the
paragraph it draws.

1. The least of many draws goes deeper: three rows of dots on one return
   scale, each dot a day below −0.012. The top row is Chan's 612 saved
   returns, whose least, −0.022031, a dashed brass line carries down through
   the rows below. The middle row is the first 612 of the declared seed's
   draws, whose least stops short of that line, and a label gives the chance
   of 0.091663 that the least of 612 draws from the fit reaches it. The
   bottom row is all 100,000 draws, about 163 times as many, whose least,
   −0.043071, is marked in red and is 1.9550 times as deep. It sits in
   Lesson 4, after the paragraph opening "The draws hold a worse day than the
   history".
2. Box 8.6's loop barely cuts its leverage: the leverage each form puts on
   its account, day by day, from the day after the account's high on day 169
   to day 303, the first day Box 8.6's loop is below −0.5. Both start at
   f·D = 10. The loop's red line stays near it and ends at 9.47, because it
   scales 10 by one plus the drawdown of the unlevered returns through day
   302, 0.946693, while its account's drawdown on day 303 is −0.504523. The
   scheme on p. 263 trades a slice of its high-water mark, so its green line
   falls as its account falls, to 3.46 with its account's drawdown at
   −0.407605. It sits in Lesson 5, after the paragraph opening "Box 8.6, the
   code printed beside that sentence".

Neither sketch is schematic. Every dot is a return or a draw, every point on
the two lines is one day's leverage, and each sits to scale.
:meth:`SketchFigures.from_run` reads all of them from
:mod:`chan.monte_carlo_leverage` on Chan's committed returns and the declared
seed, through the same :func:`~chan.monte_carlo_leverage.read_returns`,
:func:`~chan.monte_carlo_leverage.pearson_fit`,
:func:`~chan.monte_carlo_leverage.draws`,
:func:`~chan.monte_carlo_leverage.optimal_leverage`, the two CPPI forms,
:func:`~chan.monte_carlo_leverage.account_drawdowns` and
:func:`~chan.monte_carlo_leverage.minimum_below` the run uses, so a sketch
prints only what the run computes. The first sketch leaves out every value
above −0.012, which is most of them, so a row's density is that of its far
left tail only. That cutoff sits where the fit's tail turns thinner than
Chan's history's: the first 612 draws and his 612 returns each hold 3 values
below it, and only his reach past −0.015.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look, frame rate and colours. The
post's chart, :mod:`chan.monte_carlo_leverage_figures`, still draws in
:mod:`chan.regime_figure`'s shared colours, so the sketches do too, and the
loop is red and the scheme green in both. Each sketch carries more than a
reader takes in at that post's pace, so both are in :data:`PACED`, and
:func:`sketch_timeline` holds each of their labels longer and their finished
drawings for twelve seconds, as :mod:`chan.equity_seasonals_whiteboard` does
for its slow sketches. Each GIF is named :data:`GIF_PREFIX` plus the scene's
slug. The post's chart, ``monte_carlo_leverage.png``, does not start with that
prefix, so nothing that looks for the sketches by prefix finds the chart.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw both with::

    uv run python -m chan.monte_carlo_leverage_whiteboard
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import ArrayLike, NDArray

from chan.monte_carlo_leverage import (
    CAP,
    DRAWS,
    SEED,
    D,
    account_drawdowns,
    cppi_as_described,
    cppi_as_scripted,
    draws,
    minimum_below,
    optimal_leverage,
    pearson_fit,
    read_returns,
)
from chan.monte_carlo_leverage_figures import FLOOR, first_below
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    Frame,
    Label,
    Scene,
    Stroke,
    _dot,
    _line,
    _signed,
    _stroke,
    render,
    timeline,
)

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "monte_carlo_leverage_sketch_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``monte_carlo_leverage_sketch_least_draw.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


# --- The figures, read from the run ----------------------------------------------

#: The first sketch draws only the returns and draws below this, the left tail.
CUTOFF = -0.012


def leverage_on_account(account: ArrayLike, returns: ArrayLike) -> NDArray[np.float64]:
    """Each day's account return over the strategy's return that day, the leverage on the account.

    Both CPPI forms earn a multiple of the day's return ``R``, so this is that
    multiple. A day whose ``R`` is 0 has no such multiple, and this refuses it.
    """
    values = np.asarray(returns, dtype=float)
    if (values == 0).any():
        raise ValueError("a day whose return is 0 says nothing about the leverage on the account")
    return np.asarray(account, dtype=float) / values


def below(values: ArrayLike, cutoff: float = CUTOFF) -> tuple[float, ...]:
    """The values below ``cutoff``, shallowest first, the order the dots appear in."""
    found = np.asarray(values, dtype=float)
    return tuple(float(v) for v in np.sort(found[found < cutoff])[::-1])


@dataclass(frozen=True)
class LoopFigures:
    """What the loop sketch draws: each form's leverage on its account over one losing stretch.

    The stretch runs from the day after Box 8.6's account sets a high,
    ``high_day``, to ``floor_day``, the first day that account is below −0.5.
    ``loop`` and ``scheme`` hold one leverage for each day of it, and the two
    drawdowns are each account's on ``floor_day``. ``multiplier`` is the loop's
    one plus the unlevered drawdown on ``floor_day``, its leverage there over
    ``leverage·d``.
    """

    leverage: float
    d: float
    high_day: int
    floor_day: int
    loop: tuple[float, ...]
    scheme: tuple[float, ...]
    loop_drawdown: float
    scheme_drawdown: float
    multiplier: float

    @property
    def full(self) -> float:
        """``f·D``, the leverage on the whole account the loop scales down."""
        return self.leverage * self.d

    @property
    def days(self) -> range:
        return range(self.high_day + 1, self.floor_day + 1)


@dataclass(frozen=True)
class LeastFigures:
    """What the least-draw sketch draws: three rows of values below :data:`CUTOFF`.

    ``history`` is Chan's saved returns below it, ``few`` the first
    ``history_count`` draws of the declared seed and ``many`` all of them.
    ``chance`` is the exact chance that the least of ``history_count`` draws
    from the fit is at or below ``history_least``.
    """

    history: tuple[float, ...]
    history_count: int
    history_least: float
    few: tuple[float, ...]
    many: tuple[float, ...]
    many_count: int
    many_least: float
    chance: float

    @property
    def times_as_many(self) -> int:
        """How many times as many draws as returns, to the nearest whole number."""
        return round(self.many_count / self.history_count)

    @property
    def times_as_deep(self) -> float:
        return self.many_least / self.history_least


@dataclass(frozen=True)
class SketchFigures:
    """Both sketches' figures, computed once from the saved returns and the declared seed."""

    loop: LoopFigures
    least: LeastFigures

    @classmethod
    def from_run(cls, data_dir: Path | None = None) -> SketchFigures:
        """Read Chan's saved returns and compute each figure as the run does.

        The full run draws the declared seed and two ensembles of 200 more, and
        these figures need only the declared seed, so this computes it alone,
        through :mod:`chan.monte_carlo_leverage`'s own functions. ``f`` is the
        capped optimum on the draws, as in
        :func:`chan.monte_carlo_leverage.simulate`.
        """
        _, returns = read_returns(data_dir)
        _, params = pearson_fit(returns)
        sim = draws(params, SEED)
        f = optimal_leverage(sim, CAP)
        scripted = cppi_as_scripted(sim, f)
        described = cppi_as_described(sim, f)
        loop_drawdowns = account_drawdowns(scripted)
        floor_day = first_below(loop_drawdowns)
        if floor_day is None:
            raise ValueError("Box 8.6's account never falls below the floor on these draws")
        high_day = int(np.argmax(np.cumprod(1 + scripted)[:floor_day])) + 1
        stretch = slice(high_day, floor_day)
        loop = leverage_on_account(scripted[stretch], sim[stretch])
        scheme = leverage_on_account(described[stretch], sim[stretch])
        return cls(
            loop=LoopFigures(
                leverage=f,
                d=D,
                high_day=high_day,
                floor_day=floor_day,
                loop=tuple(float(v) for v in loop),
                scheme=tuple(float(v) for v in scheme),
                loop_drawdown=float(loop_drawdowns[floor_day - 1]),
                scheme_drawdown=float(account_drawdowns(described)[floor_day - 1]),
                multiplier=float(loop[-1] / (f * D)),
            ),
            least=LeastFigures(
                history=below(returns),
                history_count=len(returns),
                history_least=float(returns.min()),
                few=below(sim[: len(returns)]),
                many=below(sim),
                many_count=DRAWS,
                many_least=float(sim.min()),
                chance=minimum_below(params, float(returns.min()), len(returns)),
            ),
        )


def count(value: int) -> str:
    """A count in digits with thousands separators, as the post writes 100,000."""
    return f"{value:,}"


# --- Lesson 4: the least of many draws goes deeper --------------------------------

#: The return scale: the values from ``RETURN_RANGE[0]`` to ``RETURN_RANGE[1]``
#: run across the board from ``ROW_X[0]`` to ``ROW_X[1]``.
RETURN_RANGE = (-0.046, CUTOFF)
ROW_X = (0.5, 5.3)
#: The height of each row: Chan's returns, the first 612 draws, all the draws.
HISTORY_Y, FEW_Y, MANY_Y = 3.25, 2.25, 1.25
#: The size of each row's dots, in points.
DOT_SIZE = 5.0
#: How far above the top row and below the bottom row the dashed line at
#: Chan's worst day runs.
LINE_OVER = 0.3
#: How far above the dashed line's top its figure sits.
WORST_ABOVE = 0.34
#: Where the words beside the rows start across, and how far apart their lines sit.
WORDS_X, WORDS_STEP = 5.65, 0.36
#: How far below the bottom row the least draw's figure sits.
LEAST_BELOW = 0.4
#: The height of the closing note.
CLOSING_Y = 0.22


def return_x(value: float) -> float:
    """The board across of a return, on the scale every row shares."""
    low, high = RETURN_RANGE
    return ROW_X[0] + (ROW_X[1] - ROW_X[0]) * (value - low) / (high - low)


def _row(gid: str, values: tuple[float, ...], y: float, color: str, frames: int) -> Stroke:
    xs = np.array([return_x(v) for v in values])
    return Stroke(gid, xs, np.full(len(xs), y), color=color, dots=DOT_SIZE, frames=frames)


def _least_draw(figures: LeastFigures) -> Scene:
    """Lesson 4: the least of 100,000 draws reaches deeper than the least of 612 or Chan's worst."""
    steps: list[Stroke | Label] = []
    worst = return_x(figures.history_least)
    steps.append(_row("history", figures.history, HISTORY_Y, ACCENT, frames=2))
    steps.append(
        Label(
            f"Chan’s {count(figures.history_count)} returns",
            WORDS_X,
            HISTORY_Y,
            names="history",
            color=ACCENT,
            size=12,
        )
    )
    steps.append(
        _stroke(
            "worst",
            _line([(worst, HISTORY_Y + LINE_OVER), (worst, MANY_Y - LINE_OVER)], per_unit=4),
            color=ACCENT,
            width=1.6,
            dashed=True,
            frames=4,
        )
    )
    steps.append(
        Label(
            f"worst day {_signed(figures.history_least, 6)}",
            worst,
            HISTORY_Y + LINE_OVER + WORST_ABOVE,
            names="worst",
            color=ACCENT,
            size=12,
            ha="center",
        )
    )
    steps.append(_row("few", figures.few, FEW_Y, INK, frames=2))
    for k, text in enumerate(
        (
            f"{count(figures.history_count)} draws from the fit",
            f"reach it with chance {figures.chance:.6f}",
        )
    ):
        steps.append(
            Label(text, WORDS_X, FEW_Y + WORDS_STEP / 2 - k * WORDS_STEP, names="few", size=12)
        )
    steps.append(_row("many", figures.many, MANY_Y, INK, frames=8))
    steps.append(
        _dot("many-least", return_x(figures.many_least), MANY_Y, color=LOST),
    )
    steps.append(
        Label(
            _signed(figures.many_least, 6),
            return_x(figures.many_least),
            MANY_Y - LEAST_BELOW,
            names="many-least",
            color=LOST,
            size=12,
            ha="center",
        )
    )
    deeper = figures.many_least < figures.history_least
    for k, (text, color) in enumerate(
        (
            (f"{count(figures.many_count)} draws, about", INK),
            (f"{figures.times_as_many} times as many", INK),
            (
                f"least {figures.times_as_deep:.4f} times as deep",
                LOST if deeper else INK,
            ),
        )
    ):
        steps.append(
            Label(
                text,
                WORDS_X,
                MANY_Y + WORDS_STEP - k * WORDS_STEP,
                names="many-least",
                color=color,
                size=12,
            )
        )
    steps.append(
        Label(
            f"each dot a day below {_signed(CUTOFF, 3)}, to scale, draws from seed {SEED}",
            0.3,
            CLOSING_Y,
            names="many",
            color=MUTED,
            size=12,
        )
    )
    title = (
        "The least of many draws goes deeper"
        if deeper
        else "The least of many draws goes no deeper"
    )
    return Scene(title, "least_draw", tuple(steps))


# --- Lesson 5: Box 8.6's loop barely cuts its leverage ----------------------------

#: The chart's corner, where the first day meets a leverage of 0, and how far
#: across the last day sits.
AXIS_X, AXIS_Y, LAST_X = 1.6, 0.95, 5.3
#: How far up the board one unit of leverage runs, and how far above f·D the
#: axis reaches.
PER_LEVERAGE, AXIS_OVER = 0.25, 0.05
#: Where the words beside the two lines start across, and how far apart their lines sit.
LINE_WORDS_X, LINE_WORDS_STEP = 5.5, 0.36
#: How far left of the axis the two ticks' words end.
TICK_GAP = 0.22
#: How far below the axis the two days' words sit.
DAY_BELOW = 0.33
#: The height of the axis's caption.
CAPTION_Y = 3.88


def leverage_y(value: float) -> float:
    """The board height of a leverage on the account."""
    return AXIS_Y + PER_LEVERAGE * value


def stretch_x(figures: LoopFigures, day: int) -> float:
    """The board across of a day of the losing stretch."""
    first, last = figures.days[0], figures.days[-1]
    return AXIS_X + (LAST_X - AXIS_X) * (day - first) / (last - first)


def _path(gid: str, figures: LoopFigures, values: tuple[float, ...], color: str) -> Stroke:
    return Stroke(
        gid,
        np.array([stretch_x(figures, day) for day in figures.days]),
        np.array([leverage_y(v) for v in values]),
        color=color,
        width=2.0,
        frames=10,
    )


def _loop_leverage(figures: LoopFigures) -> Scene:
    """Lesson 5: Box 8.6's leverage on the account stays near f·D, the scheme's falls."""
    top = leverage_y(figures.full)
    steps: list[Stroke | Label] = [
        _stroke(
            "axes",
            _line([(AXIS_X, top + AXIS_OVER), (AXIS_X, AXIS_Y), (LAST_X, AXIS_Y)], per_unit=4),
            color=MUTED,
            width=1.6,
            frames=4,
        ),
        Label(
            f"leverage on the account, from its high on day {figures.high_day}",
            0.3,
            CAPTION_Y,
            names="axes",
            color=MUTED,
            size=12,
        ),
        Label(
            f"f·D = {figures.full:.0f}",
            AXIS_X - TICK_GAP,
            top,
            names="axes",
            color=MUTED,
            size=12,
            ha="right",
        ),
        Label("0", AXIS_X - TICK_GAP, AXIS_Y, names="axes", color=MUTED, size=12, ha="right"),
        Label(
            f"day {figures.days[0]}",
            AXIS_X,
            AXIS_Y - DAY_BELOW,
            names="axes",
            color=MUTED,
            size=12,
        ),
        Label(
            f"day {figures.floor_day}",
            LAST_X,
            AXIS_Y - DAY_BELOW,
            names="axes",
            color=MUTED,
            size=12,
            ha="right",
        ),
    ]
    floor = _signed(FLOOR, 1)
    steps.append(_path("loop", figures, figures.loop, LOST))
    loop_end = leverage_y(figures.loop[-1])
    for k, text in enumerate(
        (
            f"Box 8.6’s loop: {figures.loop[-1]:.2f}",
            f"drawdown {_signed(figures.loop_drawdown, 6)}, "
            + (f"past {floor}" if figures.loop_drawdown < FLOOR else f"above {floor}"),
        )
    ):
        steps.append(
            Label(
                text,
                LINE_WORDS_X,
                loop_end - k * LINE_WORDS_STEP,
                names="loop",
                color=LOST,
                size=12,
            )
        )
    steps.append(_path("scheme", figures, figures.scheme, GOOD))
    scheme_end = leverage_y(figures.scheme[-1])
    for k, text in enumerate(
        (
            f"the scheme on p. 263: {figures.scheme[-1]:.2f}",
            f"drawdown {_signed(figures.scheme_drawdown, 6)}, "
            + (f"past {floor}" if figures.scheme_drawdown < FLOOR else f"above {floor}"),
        )
    ):
        steps.append(
            Label(
                text,
                LINE_WORDS_X,
                scheme_end - k * LINE_WORDS_STEP,
                names="scheme",
                color=GOOD,
                size=12,
            )
        )
    steps.append(
        Label(
            f"the loop’s 1 + dd from the unlevered returns to day {figures.floor_day - 1}: "
            f"{figures.multiplier:.6f}",
            0.3,
            CLOSING_Y,
            names="loop",
            size=12,
        )
    )
    return Scene("Box 8.6’s loop barely cuts its leverage", "loop_leverage", tuple(steps))


# --- Drawing ------------------------------------------------------------------

#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("least_draw", "loop_leverage")
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


def scenes(figures: SketchFigures | None = None) -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them, Lesson 4's then Lesson 5's.

    ``figures`` defaults to :meth:`SketchFigures.from_run` on Chan's file.
    """
    found = figures if figures is not None else SketchFigures.from_run()
    return (_least_draw(found.least), _loop_leverage(found.loop))


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


def make_monte_carlo_leverage_whiteboards(out_dir: Path | None = None) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes()]


def main() -> None:
    for path in make_monte_carlo_leverage_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
