"""Whiteboard sketches for the TU hypothesis tests post, one for Lesson 4 and one for Lesson 5.

``blog/tu-hypothesis-tests-lessons.md`` makes two claims a sentence has to
build in the reader's head: the script's third test adds its shuffled trades
to the wrong array, so it cannot fail, and a drifting series keeps the rule
long on most days, so the rule collects the drift. This module draws the two
as scenes, and the post places each right after the paragraph it draws.

1. The shuffled trades land in the wrong place: five boxes joined by arrows,
   the script's third test as written. The shuffled trades go into ``pos``,
   the real positions, along an arrow labelled "added here", while a dashed
   arrow toward ``pos_sim``, which starts as zeros, is labelled "never
   reached". ``pos_sim`` then feeds the box for ``ret_sim``, built from a
   ``pos_sim`` of 0, which feeds the box for every simulated mean, 0, set
   against the observed mean above 0. A closing line gives the number of
   draws the run executes as written and what they return. It sits in
   Lesson 4, after the paragraph opening "The script writes the third test
   so that it returns 0 whatever the data."
2. Drift makes the rule mostly long: two noisy price lines, one with TU's
   drift above one with the same noise and no drift. Under each, ten
   brackets 250 days long end in an arrow, up in green where the price ends
   the 250 days higher, which makes the rule long, and down in red where it
   ends lower, which makes it short. Eight of the ten point up on the
   drifting line and five on the flat one. Labels give the share of its days
   with a long or short signal on which the rule is long, averaged over the
   first 1,000 of the second test's simulated series, with and without the
   mean. The upper line's label calls it schematic, a grey note says the
   shares come from those series, and a closing line says the rule collects
   the drift. It sits in Lesson 5, after the paragraph opening "**The
   mechanism is the rule itself.**"

The second sketch's lines are schematic. Both are random walks drawn from
:data:`WALK_SEED` with TU's daily standard deviation, and the upper one adds
TU's daily mean. That keeps the drift at its real size against the noise over
250 days, about 0.87 of one standard deviation. Neither line is TU's own
closes, on which the rule is long on a different share of days, and neither
is one of the second test's series.

The second sketch's two shares and the first sketch's observed mean, draw
count and simulated means are not schematic. :meth:`SketchFigures.from_run`
reads each of them from :mod:`chan.tu_hypothesis_tests` on Chan's committed
file, so a sketch prints only what the run computes.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look, frame rate and colours. The
post's chart still draws in :mod:`chan.regime_figure`'s shared colours, so the
sketches do too. Each sketch carries more than a reader takes in at that
post's pace, so both are in :data:`PACED`, and :func:`sketch_timeline` holds
each of their labels longer and their finished drawings for twelve seconds, as
:mod:`chan.equity_seasonals_whiteboard` does for its slow sketches. Each GIF
is named :data:`GIF_PREFIX` plus the scene's slug. The post's chart,
``tu_hypothesis_tests.png``, does not start with that prefix, so nothing that
looks for the sketches by prefix finds the chart.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw both with::

    uv run python -m chan.tu_hypothesis_tests_whiteboard
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import ArrayLike, NDArray

from chan import tu_hypothesis_tests as tests
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.tu_momentum import (
    HOLD_DAYS,
    LOOKBACK,
    market_returns,
    positions,
    read_sources,
    signals,
    strategy_returns,
)
from chan.usdcad_tests_whiteboard import (
    Frame,
    Label,
    Scene,
    Stroke,
    _arrow,
    _box,
    _line,
    _stroke,
    render,
    timeline,
)

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "tu_hypothesis_tests_sketch_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``tu_hypothesis_tests_sketch_wrong_array.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


# --- The figures, read from the run ----------------------------------------------

#: How many of the second test's simulated series the long shares average over,
#: the first of its 10,000.
SHARE_SERIES = 1_000


def long_share(simulated: ArrayLike, lookback: int = LOOKBACK) -> float:
    """The average over the rows of ``simulated`` of long days over long and short days.

    Each row is one series of daily returns. The rule's signal compares
    ``cumprod(1 + r) − 1`` with its value ``lookback`` rows back, as
    :func:`chan.tu_hypothesis_tests.simulated_strategy_returns` does, so a day
    is long when the price is higher than ``lookback`` days before and short
    when it is lower.
    """
    sim = np.atleast_2d(np.asarray(simulated, dtype=float))
    cl_sim = np.cumprod(1 + sim, axis=1) - 1
    longs = (cl_sim[:, lookback:] > cl_sim[:, :-lookback]).sum(axis=1)
    shorts = (cl_sim[:, lookback:] < cl_sim[:, :-lookback]).sum(axis=1)
    return float((longs / (longs + shorts)).mean())


@dataclass(frozen=True)
class SketchFigures:
    """What both sketches print, and the drift and noise the schematic lines are drawn with.

    ``drifting_share`` and ``flat_share`` are :func:`long_share` on the first
    :data:`SHARE_SERIES` of the second test's series, as drawn and with TU's
    mean removed. ``as_written_means`` is each draw's mean return from the
    third test run as written, and ``largest_return`` the largest ``|ret_sim|``
    over all of them.
    """

    drifting_share: float
    flat_share: float
    observed_mean: float
    as_written_means: tuple[float, ...]
    largest_return: float
    daily_mean: float
    daily_std: float
    lookback: int = LOOKBACK

    @property
    def as_written_draws(self) -> int:
        return len(self.as_written_means)

    @classmethod
    def from_run(cls, data_dir: Path | None = None) -> SketchFigures:
        """Read Chan's file and compute each figure as :mod:`chan.tu_hypothesis_tests` does.

        The full run draws 110,000 series and shuffles, and these figures need
        only the strategy on TU's closes, the third test's ten as-written
        draws and the first :data:`SHARE_SERIES` of the second test's series,
        so this computes those alone, through the run's own functions.
        """
        _, closes = read_sources(data_dir)
        cl = closes.to_numpy(dtype=float)
        market = market_returns(cl)
        longs, shorts = signals(cl, LOOKBACK)
        held = positions(longs, shorts, HOLD_DAYS)
        daily = strategy_returns(held, market, HOLD_DAYS)
        moments = tests.script_moments(market)
        params = tests.pearson_iv_parameters(
            moments.mean, moments.std, moments.skewness, moments.kurtosis
        )
        uniforms = np.random.default_rng(tests.RETURNS_SEED).random((SHARE_SERIES, len(cl)))
        simulated = tests.pearson_iv_draws(params, uniforms)
        written = tests.randomized_trades_as_written(longs, shorts, held, market)
        return cls(
            drifting_share=long_share(simulated),
            flat_share=long_share(simulated - moments.mean),
            observed_mean=float(daily.mean()),
            as_written_means=tuple(float(m) for m in written.means),
            largest_return=written.largest_return,
            daily_mean=moments.mean,
            daily_std=moments.std,
        )


def share(value: float) -> str:
    """A share of days to six decimals, the precision the post prints."""
    return f"{value:.6f}"


def mean(value: float) -> str:
    """A mean daily return in the post's form, such as ``6.626644e-05``."""
    return f"{value:.6e}"


def count(value: int) -> str:
    """A count in digits, as the post writes the 10 draws."""
    return f"{value:,}"


# --- Lesson 4: the shuffled trades land in the wrong place ------------------------

#: The boxes, each as (x0, y0, x1, y1) on the board.
TRADES_BOX = (0.3, 3.25, 2.8, 3.95)
POS_BOX = (5.3, 3.25, 9.0, 3.95)
POS_SIM_BOX = (0.3, 1.7, 2.8, 2.4)
RET_SIM_BOX = (3.9, 1.7, 9.0, 2.4)
MEANS_BOX = (5.3, 0.5, 9.0, 1.2)
#: The height of the closing line.
CLOSING_Y = 0.22
#: How far each arrow stops short of the boxes it joins.
ARROW_GAP = 0.1
#: Where the dashed arrow toward ``pos_sim`` stops, short of that box's top.
NEVER_STOP = 0.3


def _middle(box: tuple[float, float, float, float]) -> tuple[float, float]:
    x0, y0, x1, y1 = box
    return (x0 + x1) / 2, (y0 + y1) / 2


def _wrong_array(figures: SketchFigures) -> Scene:
    """Lesson 4: the shuffled trades reach ``pos`` and never ``pos_sim``, so every mean is 0."""
    steps: list[Stroke | Label] = []

    def boxed(gid: str, box: tuple[float, float, float, float], text: str, color: str) -> None:
        steps.append(_stroke(gid, _box(*box), color=color, frames=4))
        x, y = _middle(box)
        steps.append(Label(text, x, y, names=gid, color=color, size=12, ha="center"))

    boxed("trades", TRADES_BOX, "shuffled trades", ACCENT)
    boxed("pos", POS_BOX, "pos, the real positions", INK)
    row = _middle(TRADES_BOX)[1]
    steps.append(
        _stroke(
            "added",
            _arrow(TRADES_BOX[2] + ARROW_GAP, row, POS_BOX[0] - ARROW_GAP, row),
            color=INK,
            frames=4,
        )
    )
    steps.append(
        Label(
            "added here",
            (TRADES_BOX[2] + POS_BOX[0]) / 2,
            row - 0.34,
            names="added",
            size=12,
            ha="center",
        )
    )
    boxed("pos-sim", POS_SIM_BOX, "pos_sim = zeros", MUTED)
    down = _middle(TRADES_BOX)[0]
    steps.append(
        _stroke(
            "never",
            _arrow(down, TRADES_BOX[1] - ARROW_GAP, down, POS_SIM_BOX[3] + NEVER_STOP),
            color=LOST,
            dashed=True,
            frames=4,
        )
    )
    steps.append(
        Label(
            "never reached",
            down + 0.35,
            (TRADES_BOX[1] + POS_SIM_BOX[3]) / 2,
            names="never",
            color=LOST,
            size=12,
        )
    )
    row = _middle(POS_SIM_BOX)[1]
    steps.append(
        _stroke(
            "feeds",
            _arrow(POS_SIM_BOX[2] + ARROW_GAP, row, RET_SIM_BOX[0] - ARROW_GAP, row),
            color=MUTED,
            frames=3,
        )
    )
    built = "0" if figures.largest_return == 0 else "not 0"
    boxed("ret-sim", RET_SIM_BOX, f"ret_sim built from pos_sim = {built}", MUTED)
    across = _middle(MEANS_BOX)[0]
    steps.append(
        _stroke(
            "averaged",
            _arrow(across, RET_SIM_BOX[1] - ARROW_GAP, across, MEANS_BOX[3] + ARROW_GAP),
            color=MUTED,
            frames=3,
        )
    )
    zero = all(m == 0 for m in figures.as_written_means)
    boxed(
        "means",
        MEANS_BOX,
        "every simulated mean: 0" if zero else "not every simulated mean is 0",
        LOST,
    )
    sign = ">" if figures.observed_mean > 0 else "≤"
    steps.append(
        Label(
            f"observed mean {mean(figures.observed_mean)} {sign} 0",
            0.3,
            _middle(MEANS_BOX)[1],
            names="means",
            color=GOOD,
            size=12,
        )
    )
    returns = (
        "every return 0"
        if figures.largest_return == 0
        else f"largest return {mean(figures.largest_return)}"
    )
    steps.append(
        Label(
            f"{count(figures.as_written_draws)} draws run as written: {returns}",
            0.3,
            CLOSING_Y,
            names="means",
            size=12,
        )
    )
    return Scene("The shuffled trades land in the wrong place", "wrong_array", tuple(steps))


# --- Lesson 5: drift makes the rule mostly long -----------------------------------

#: The seed of the schematic noise both lines share. Its first 2,500 normal
#: draws put eight of the ten windows up with the drift and five without it.
WALK_SEED = 156
#: How many 250-day windows each line runs.
WINDOWS = 10
#: Where each line runs across, and how far below it each row of brackets sits.
LINE_X = (0.3, 5.7)
#: The height of each line's start, and of its brackets.
DRIFTING_START, DRIFTING_BRACKETS = 3.15, 2.7
FLAT_START, FLAT_BRACKETS = 1.75, 1.0
#: How far up the board one unit of cumulative return runs, the same on both lines.
PER_RETURN = 5.0
#: How far each bracket's arrow runs up or down, and how high its left tick stands.
ARROW_RISE, BRACKET_TICK = 0.28, 0.08
#: How far each bracket stops short of the next one's tick.
BRACKET_GAP = 0.05
#: Every how many days the drawn line takes a point.
EVERY = 5
#: Where the labels beside the lines start across, how far right of the first
#: word of the arrows' key the second starts, and the heights of the three lines
#: of words beside each line.
WORDS_X, LEGEND_STEP = 6.15, 1.3
DRIFTING_WORDS_YS = (3.85, 3.4, 3.05)
FLAT_WORDS_YS = (2.0, 1.55, 1.2)
#: Where the note naming the shares' source ends across, on the closing line's height.
SOURCE_X = 9.85


def walk(figures: SketchFigures, drift: bool) -> NDArray[np.float64]:
    """The schematic line's cumulative return on each day, day 0 first at 0.

    Daily returns are ``daily_mean + daily_std · z`` with the drift, and
    ``daily_std · z`` without it, for the same normal draws ``z``.
    """
    days = figures.lookback * WINDOWS
    z = np.random.default_rng(WALK_SEED).standard_normal(days)
    step = figures.daily_std * z + (figures.daily_mean if drift else 0.0)
    return np.concatenate([[0.0], np.cumsum(step)])


def window_changes(figures: SketchFigures, drift: bool) -> NDArray[np.float64]:
    """Each window's change in the line, from the price 250 days back to today's."""
    return np.diff(walk(figures, drift)[:: figures.lookback])


def day_x(figures: SketchFigures, day: float) -> float:
    """The board across of a day of the schematic lines."""
    return LINE_X[0] + (LINE_X[1] - LINE_X[0]) * day / (figures.lookback * WINDOWS)


def _row(figures: SketchFigures, drift: bool) -> list[Stroke]:
    """One line, then its brackets, each ending in an arrow up in green or down in red."""
    name = "drifting" if drift else "flat"
    start, brackets = (DRIFTING_START, DRIFTING_BRACKETS) if drift else (FLAT_START, FLAT_BRACKETS)
    level = walk(figures, drift)
    days = np.arange(0, len(level), EVERY)
    line = _stroke(
        f"{name}-line",
        (
            np.array([day_x(figures, d) for d in days]),
            start + PER_RETURN * level[days],
        ),
        color=ACCENT if drift else INK,
        width=1.6,
        frames=12,
    )
    strokes = [line]
    for k, change in enumerate(window_changes(figures, drift)):
        x0 = day_x(figures, k * figures.lookback) + BRACKET_GAP
        x1 = day_x(figures, (k + 1) * figures.lookback) - BRACKET_GAP
        tip = brackets + (ARROW_RISE if change > 0 else -ARROW_RISE)
        head = _arrow(x1, brackets, x1, tip)
        body = _line(
            [
                (x0, brackets + BRACKET_TICK),
                (x0, brackets - BRACKET_TICK),
                (x0, brackets),
                (x1, brackets),
            ],
            per_unit=10,
        )
        strokes.append(
            _stroke(
                f"{name}-window-{k + 1}",
                (np.concatenate([body[0], head[0]]), np.concatenate([body[1], head[1]])),
                color=GOOD if change > 0 else LOST,
                width=2.0,
                frames=2,
            )
        )
    return strokes


def _mostly_long(figures: SketchFigures) -> Scene:
    """Lesson 5: with the drift most windows end higher, so the rule is mostly long."""
    steps: list[Stroke | Label] = []
    drifting = _row(figures, drift=True)
    steps.append(drifting[0])
    steps.append(
        Label(
            "schematic, with TU’s drift",
            WORDS_X,
            DRIFTING_WORDS_YS[0],
            names="drifting-line",
            color=ACCENT,
            size=12,
        )
    )
    steps.extend(drifting[1:])
    last = drifting[-1].gid
    steps.append(Label("up: long", WORDS_X, DRIFTING_BRACKETS, names=last, color=GOOD, size=12))
    steps.append(
        Label(
            "down: short", WORDS_X + LEGEND_STEP, DRIFTING_BRACKETS, names=last, color=LOST, size=12
        )
    )
    for text, y in zip(
        (f"long on {share(figures.drifting_share)}", "of the days it trades"),
        DRIFTING_WORDS_YS[1:],
        strict=True,
    ):
        steps.append(Label(text, WORDS_X, y, names=last, color=ACCENT, size=12))
    flat = _row(figures, drift=False)
    steps.append(flat[0])
    steps.append(
        Label("same noise, no drift", WORDS_X, FLAT_WORDS_YS[0], names="flat-line", size=12)
    )
    steps.extend(flat[1:])
    for text, y in zip(
        (f"long on {share(figures.flat_share)}", "once the mean is removed"),
        FLAT_WORDS_YS[1:],
        strict=True,
    ):
        steps.append(Label(text, WORDS_X, y, names=flat[-1].gid, size=12))
    steps.append(
        Label(
            f"shares from {count(SHARE_SERIES)} simulated series",
            SOURCE_X,
            CLOSING_Y,
            names=flat[-1].gid,
            color=MUTED,
            size=12,
            ha="right",
        )
    )
    mostly = figures.drifting_share > 0.5
    steps.append(
        Label(
            "long most days, so it collects the drift"
            if mostly
            else "not long most days, so it misses the drift",
            LINE_X[0],
            CLOSING_Y,
            names=flat[-1].gid,
            size=12,
        )
    )
    title = (
        "Drift makes the rule mostly long" if mostly else "Drift does not make the rule mostly long"
    )
    return Scene(title, "mostly_long", tuple(steps))


# --- Drawing ------------------------------------------------------------------

#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("wrong_array", "mostly_long")
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
    return (_wrong_array(found), _mostly_long(found))


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


def make_tu_hypothesis_tests_whiteboards(out_dir: Path | None = None) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes()]


def main() -> None:
    for path in make_tu_hypothesis_tests_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
