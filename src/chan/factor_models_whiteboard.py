"""Whiteboard sketches for the factor models post, one for Lesson 2 and one for Lesson 3.

``blog/factor-models-lessons.md`` makes two claims a sentence has to build in
the reader's head: a least-squares fit with an intercept leaves residuals that
cancel, so the revised Python ranks on each stock's own returns, and a sign flip
in a day's weights changes both members of a pair together, so it moves no
product. This module draws the two as scenes, and the post places each right
after the paragraph it draws.

1. The residuals cancel: a grey day axis for one stock's year with a dozen
   daily returns as black bars, the fitted value beside each bar as a brass
   dot, and the gap between them as a short tick, green where the return is
   above the fit and red where it is below. With an intercept the gaps sum to
   0, so two totals beside it, Σ returns and Σ fitted, stand at the same
   height, and a ranked column of four stocks closes it: ranking on Σ fitted
   is ranking on Σ returns, which is momentum with no factors needed. It sits
   in Lesson 2, after the display equation under the paragraph opening "The
   revised Python regresses each stock’s returns".
2. A sign flip changes both members of a pair: day t's weights as a row of
   arrows over six stocks, applied to day t's returns and to day t+1's to give
   the pair f and g, whose product is positive. Day t+1's fresh analysis
   returns the same arrows reversed, so a series built from each day's fresh
   weights reads f and then −g, and the flip reads as a reversal. In the pair,
   a flip reverses both members, (−f)(−g) = fg, so the product stays. It sits
   in Lesson 3, after the paragraph opening "Each day’s principal component
   analysis gives each factor".

Both sketches are schematic and carry no figures from the run. The returns,
the five factor series, the weights and the four ranked stocks are made up to
show a shape, so no bar, dot or arrow on them is a value from Chan's file.
What each draws is a fact about the arithmetic that holds whatever the data.
The first sketch's dots are the least-squares fit of its bars on an intercept
and five made-up factor series, so its gaps do sum to 0, as
``chan.pca_factor.python_expected`` and ``summed_returns`` give on the file.
Its sums are sums of daily returns, the ``window.sum(axis=1)`` the Python
ranks on, not a compounded year's return. The second sketch's f and g are its
weights applied to two made-up days of returns, and flipping the weights flips
both, which ``test_a_flipped_vector_moves_no_product_and_no_statistic`` in
``tests/test_pca_factor_momentum.py`` pins on the run.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look, frame rate and colours. The
sign flip sketch carries more steps than a reader takes in at that post's
pace, so it is in :data:`PACED`, and :func:`sketch_timeline` holds each of its
labels longer and its finished drawing for twelve seconds, as
:mod:`chan.equity_seasonals_whiteboard` does for its slow sketches. Only the
scenes, the pacing and the file names are this module's. Each GIF is named
:data:`GIF_PREFIX` plus the scene's slug, a prefix no chart in
``docs/figures`` starts with.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw both with::

    uv run python -m chan.factor_models_whiteboard
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    Frame,
    Label,
    Scene,
    Stroke,
    _arrow,
    _check,
    _line,
    _span,
    _stroke,
    render,
    timeline,
)

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "factor_models_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``factor_models_sign_flip.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


# --- Lesson 2: the residuals cancel -------------------------------------------

#: One stock's daily returns over a made-up year of a dozen days, in board
#: units above or below the day axis before :data:`RETURN_SCALE`.
RETURNS = np.array([-0.68, 0.27, -0.37, -0.5, 0.43, -0.7, 0.74, 0.16, 0.58, 0.78, 0.46, 0.25])
#: Five made-up factor series over the same dozen days. The fit regresses the
#: returns on an intercept and these, as the Python does on its five.
FACTOR_SERIES = np.array(
    [
        [-0.1, 0.0, -0.9, 1.0, 0.1, 0.2, 1.0, 1.0, 0.4, 0.7, 0.4, 0.2],
        [-0.2, -0.4, 0.1, -0.4, 0.9, -0.4, 0.4, 0.5, -0.6, 0.0, 0.7, 0.4],
        [-0.2, -0.8, 0.9, 0.7, -0.6, -0.9, -0.9, -0.9, 0.1, 0.2, -0.6, -0.3],
        [-1.0, -0.5, 0.8, -0.1, 0.5, -0.3, 0.7, 1.0, 0.4, 0.1, 0.5, 0.8],
        [0.1, -0.3, 0.0, -0.1, 0.4, 0.6, -0.1, -0.5, 0.4, -0.8, 0.4, -0.9],
    ]
)
#: The day axis's height, the board height of a return of 1, and each day's
#: place across.
AXIS_Y, RETURN_SCALE = 2.0, 1.2
AXIS_X = (0.4, 5.6)
FIRST_DAY_X, DAY_STEP = 0.75, 0.42
#: How far right of its bar each fitted dot and its gap's tick sit.
DOT_OFFSET = 0.14
BAR_WIDTH, DOT_SIZE, TICK_WIDTH = 5.0, 6.0, 2.5
#: The two totals: where each bar stands, its base, and the board height of a
#: summed return of 1.
TOTALS_X = {"returns": 6.2, "fitted": 7.4}
TOTALS_BASE, TOTAL_SCALE = 1.6, 0.9
#: Four made-up stocks' summed returns, ranked from the top, each drawn as a
#: bar across from :data:`RANKED_X` with its summed fitted value as a dot
#: beside the bar's end.
RANKED = (1.25, 0.95, 0.65, 0.35)
RANKED_X, RANKED_TOP, RANKED_STEP = 8.1, 3.05, 0.35


def fitted(returns: np.ndarray = RETURNS, factors: np.ndarray = FACTOR_SERIES) -> np.ndarray:
    """The least-squares fitted values of the returns on an intercept and the factor series."""
    design = np.column_stack([np.ones(len(returns)), factors.T])
    coefficients = np.linalg.lstsq(design, returns, rcond=None)[0]
    return design @ coefficients


def day_x(day: int) -> float:
    """Where a day's bar stands across the board."""
    return FIRST_DAY_X + DAY_STEP * day


def _bar(gid: str, x: float, y0: float, y1: float, color: str, width: float) -> Stroke:
    return _stroke(gid, _line([(x, y0), (x, y1)], per_unit=10), color=color, width=width, frames=1)


def _residuals_cancel() -> Scene:
    """Lesson 2: the fit's gaps sum to 0, so its sum is the returns' sum."""
    fit = fitted()
    days = np.arange(len(RETURNS))
    steps: list[Stroke | Label] = [
        _stroke("axis", _line([(AXIS_X[0], AXIS_Y), (AXIS_X[1], AXIS_Y)]), color=MUTED, frames=6),
        Label("one stock’s year (schematic)", 0.4, 0.32, names="axis", color=MUTED, size=11),
    ]
    for day in days:
        top = AXIS_Y + RETURN_SCALE * RETURNS[day]
        steps.append(_bar(f"return-{day}", day_x(day), AXIS_Y, top, INK, BAR_WIDTH))
    steps.append(Label("daily returns", 0.4, 3.65, names=f"return-{days[-1]}", size=12))
    steps.append(
        Stroke(
            "fitted",
            np.array([day_x(day) + DOT_OFFSET for day in days]),
            AXIS_Y + RETURN_SCALE * fit,
            color=ACCENT,
            frames=6,
            dots=DOT_SIZE,
        )
    )
    steps.append(Label("fitted values", 2.1, 3.65, names="fitted", color=ACCENT, size=12))
    for day in days:
        above = RETURNS[day] > fit[day]
        steps.append(
            _bar(
                f"gap-{day}",
                day_x(day) + DOT_OFFSET,
                AXIS_Y + RETURN_SCALE * fit[day],
                AXIS_Y + RETURN_SCALE * RETURNS[day],
                GOOD if above else LOST,
                TICK_WIDTH,
            )
        )
    first_above = next(day for day in days if RETURNS[day] > fit[day])
    first_below = next(day for day in days if RETURNS[day] < fit[day])
    steps += [
        Label("+ return above the fit", 0.4, 3.28, names=f"gap-{first_above}", color=GOOD, size=11),
        Label(
            "− return below the fit", 2.95, 3.28, names=f"gap-{first_below}", color=LOST, size=11
        ),
        Label(
            "with an intercept, the residuals sum to 0", 0.4, 0.68, names=f"gap-{days[-1]}", size=11
        ),
    ]
    total = float(RETURNS.sum())
    for name, color in (("returns", INK), ("fitted", ACCENT)):
        value = total if name == "returns" else float(fit.sum())
        x = TOTALS_X[name]
        steps.append(
            _bar(
                f"total-{name}",
                x,
                TOTALS_BASE,
                TOTALS_BASE + TOTAL_SCALE * value,
                color,
                BAR_WIDTH * 1.6,
            )
        )
        steps.append(
            Label(f"Σ {name}", x, 1.2, names=f"total-{name}", color=color, size=12, ha="center")
        )
    middle = (TOTALS_X["returns"] + TOTALS_X["fitted"]) / 2
    height = TOTALS_BASE + TOTAL_SCALE * total / 2
    steps.append(Label("=", middle, height, names="total-fitted", size=16, ha="center"))
    for rank, length in enumerate(RANKED):
        y = RANKED_TOP - RANKED_STEP * rank
        steps.append(_bar_across(f"ranked-{rank}", y, length))
        steps.append(
            Stroke(
                f"ranked-fit-{rank}",
                np.array([RANKED_X + length + DOT_OFFSET]),
                np.array([y]),
                color=ACCENT,
                frames=1,
                dots=DOT_SIZE,
            )
        )
    last = f"ranked-fit-{len(RANKED) - 1}"
    steps += [
        Label("four stocks, ranked", 7.75, 3.65, names=last, size=11),
        Label("rank on Σ fitted = rank on Σ returns", 5.9, 0.75, names=last, size=11),
        Label("momentum, no factors needed", 5.9, 0.4, names=last, size=11),
    ]
    return Scene("The residuals cancel, so the sums match", "residuals_cancel", tuple(steps))


def _bar_across(gid: str, y: float, length: float) -> Stroke:
    return _stroke(
        gid,
        _line([(RANKED_X, y), (RANKED_X + length, y)], per_unit=10),
        color=INK,
        width=BAR_WIDTH,
        frames=2,
    )


# --- Lesson 3: a sign flip changes both members of a pair ----------------------

#: Day t's weights on six made-up stocks, drawn as arrows up or down from
#: :data:`ARROW_Y`, and the six stocks' returns on day t and on day t+1.
WEIGHTS = np.array([0.45, -0.3, 0.2, 0.5, -0.4, 0.25])
DAY_T = np.array([0.6, -0.2, 0.3, 0.4, -0.5, 0.1])
DAY_AFTER = np.array([0.3, 0.1, -0.2, 0.5, -0.1, 0.2])
#: Where each of the three panels starts across, the height the arrows rise or
#: fall from, and the height the values stand on.
PANELS = (0.35, 3.55, 6.75)
ARROW_Y, ARROW_STEP = 3.25, 0.42
VALUE_BASE = 1.5
#: The board height of a factor return of 1 and of a product of 1.
VALUE_SCALE, PRODUCT_SCALE = 0.55, 1.2
#: Where each value's bar and the product's bar stand inside a panel.
FIRST_AT, SECOND_AT, PRODUCT_AT = 0.5, 1.1, 2.2
#: How far a value's letter sits beyond the base, on the side its bar is not.
LETTER_GAP = 0.42


def pair() -> tuple[float, float]:
    """Day t's weights applied to day t's returns and to day t+1's, as ``(f, g)``."""
    return float(WEIGHTS @ DAY_T), float(WEIGHTS @ DAY_AFTER)


def _arrows(panel: float, sign: float, color: str, tag: str) -> list[Stroke]:
    strokes = []
    for k, weight in enumerate(WEIGHTS):
        x = panel + 0.25 + ARROW_STEP * k
        strokes.append(
            _stroke(
                f"{tag}-{k}", _arrow(x, ARROW_Y, x, ARROW_Y + sign * weight), color=color, frames=2
            )
        )
    return strokes


def _value(
    gid: str, x: float, value: float, scale: float, color: str, width: float = 6.0
) -> Stroke:
    return _bar(gid, x, VALUE_BASE, VALUE_BASE + scale * value, color, width)


def _letter(text: str, x: float, value: float, names: str, color: str, size: float = 12) -> Label:
    """A value's name on the far side of the base from its bar."""
    y = VALUE_BASE - LETTER_GAP if value > 0 else VALUE_BASE + LETTER_GAP + 0.02
    return Label(text, x, y, names=names, color=color, size=size, ha="center")


def _base(gid: str, panel: float) -> Stroke:
    return _stroke(
        gid,
        _line([(panel + 0.1, VALUE_BASE), (panel + 2.9, VALUE_BASE)]),
        color=MUTED,
        width=1.5,
        frames=3,
    )


def _sign_flip() -> Scene:
    """Lesson 3: a flip in one day's weights reverses both members of the pair."""
    f, g = pair()
    one, two, three = PANELS
    steps: list[Stroke | Label] = []
    # Panel 1: day t's weights give the pair (f, g), and its product is positive.
    steps += _arrows(one, 1.0, INK, "weights")
    steps.append(Label("day t’s weights", one + 0.1, 2.45, names="weights-5", size=11))
    steps.append(_base("base-pair", one))
    steps.append(_value("pair-f", one + FIRST_AT, f, VALUE_SCALE, INK))
    steps.append(_letter("f", one + FIRST_AT, f, "pair-f", INK))
    steps.append(_value("pair-g", one + SECOND_AT, g, VALUE_SCALE, INK))
    steps.append(_letter("g", one + SECOND_AT, g, "pair-g", INK))
    steps.append(
        _stroke(
            "pair-bracket",
            _span(one + FIRST_AT - 0.15, one + SECOND_AT + 0.15, 0.7, tick=0.08),
            color=INK,
            frames=3,
        )
    )
    steps.append(Label("one pair: day t, day t+1", one + 0.1, 0.3, names="pair-bracket", size=11))
    steps.append(_value("pair-product", one + PRODUCT_AT, f * g, PRODUCT_SCALE, GOOD))
    steps.append(_letter("f·g", one + PRODUCT_AT, f * g, "pair-product", INK, size=11))
    steps.append(
        Label(
            "+",
            one + PRODUCT_AT + 0.35,
            VALUE_BASE + 0.32,
            names="pair-product",
            color=GOOD,
            size=14,
        )
    )
    # Panel 2: day t+1's fresh weights come out flipped, and a series built from
    # each day's fresh weights reads f and then −g, so its product turns negative.
    steps += _arrows(two, -1.0, LOST, "fresh")
    steps.append(
        Label("day t+1’s weights, flipped", two + 0.1, 2.45, names="fresh-5", color=LOST, size=11)
    )
    steps.append(_base("base-naive", two))
    steps.append(_value("naive-f", two + FIRST_AT, f, VALUE_SCALE, INK))
    steps.append(_letter("f", two + FIRST_AT, f, "naive-f", INK))
    steps.append(_value("naive-g", two + SECOND_AT, -g, VALUE_SCALE, LOST))
    steps.append(_letter("−g", two + SECOND_AT, -g, "naive-g", LOST))
    steps.append(_value("naive-product", two + PRODUCT_AT, -f * g, PRODUCT_SCALE, LOST))
    steps.append(_letter("f·(−g)", two + PRODUCT_AT, -f * g, "naive-product", INK, size=11))
    steps.append(
        Label(
            "−",
            two + PRODUCT_AT + 0.35,
            VALUE_BASE - 0.32,
            names="naive-product",
            color=LOST,
            size=14,
        )
    )
    steps.append(Label("fresh weights each day:", two + 0.1, 0.72, names="naive-product", size=10))
    steps.append(
        Label("the flip reads as a reversal", two + 0.1, 0.4, names="naive-product", size=10)
    )
    # Panel 3: a flip in day t's weights reverses both members of the pair.
    steps.append(_base("base-flipped", three))
    steps.append(_value("flipped-f", three + FIRST_AT, -f, VALUE_SCALE, LOST))
    steps.append(_letter("−f", three + FIRST_AT, -f, "flipped-f", LOST))
    steps.append(_value("flipped-g", three + SECOND_AT, -g, VALUE_SCALE, LOST))
    steps.append(_letter("−g", three + SECOND_AT, -g, "flipped-g", LOST))
    steps.append(_value("flipped-product", three + PRODUCT_AT, f * g, PRODUCT_SCALE, GOOD))
    steps.append(
        Label(
            "+",
            three + PRODUCT_AT + 0.35,
            VALUE_BASE + 0.32,
            names="flipped-product",
            color=GOOD,
            size=14,
        )
    )
    steps.append(Label("(−f)(−g) = fg", three + 0.1, ARROW_Y, names="flipped-product", size=14))
    steps.append(_stroke("check", _check(three + 2.35, ARROW_Y - 0.05), color=GOOD, frames=3))
    steps.append(Label("day t’s flip changes both,", three + 0.02, 0.72, names="check", size=10))
    steps.append(Label("so the product stays", three + 0.02, 0.4, names="check", size=10))
    return Scene("A sign flip changes both members of a pair", "sign_flip", tuple(steps))


# --- Drawing ------------------------------------------------------------------

#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("sign_flip",)
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


def scenes() -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them, Lesson 2's then Lesson 3's."""
    return (_residuals_cancel(), _sign_flip())


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


def make_factor_models_whiteboards(out_dir: Path | None = None) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes()]


def main() -> None:
    for path in make_factor_models_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
