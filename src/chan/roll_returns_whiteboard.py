"""Whiteboard sketches for the spot and roll returns post, one for its model and one for Lesson 2.

``blog/roll-returns-lessons.md`` makes two claims a sentence has to build in
the reader's head: one line for a futures price gives two returns, depending
on whether a reader holds one contract or one day, and a fit that counts
contracts where it should count months triples the roll return of quarterly
contracts. This module draws the two as scenes, and the post places each
right after the passage it draws.

1. One line, read two ways: a spot line rising at α, three contracts below it
   by γ times their time to expiry, each rising at α + γ to end on the spot
   line at its own expiry, one of them retraced as the contract a holder
   keeps, and a dashed line on one day crossing all of them, where each later
   expiry sits lower. It sits in "The model and the files", after the
   numbered list under "Two readings of that one line give the two returns."
2. Same five prices, three times the slope: the five prices of a planted
   quarterly curve, March to the next March, at their months with the fit
   in months through them, then the same prices slid one column apart with
   the script's fit through them, three times steeper. It sits in Lesson 2, after
   the paragraph opening "A planted example shows how large the difference
   is."

The model sketch is schematic and carries no figures from the run. Its slopes
and expiries are made up to show the shape of the model, so no position or
slope on it is a value of α or γ. What it draws is the algebra of the model,
ln F(t, T) = c + αt − γ(T − t), with the spot line c + αt sharing its c, so
each contract meets the spot at its own expiry, and that holds whatever the
numbers. Its labels name the two returns in words rather than as α and γ,
because the hand font draws α like a and γ like y.

The Lesson 2 sketch reads none of Chan's five files. It draws the planted
example the post describes, built the way
``test_quarterly_contracts_triple_the_column_gamma_and_not_the_month_gamma``
in ``tests/test_roll_returns.py`` builds it, and its two figures, 0.03 and
0.09, are read from :func:`chan.roll_returns.roll_returns_in_months` and
:func:`chan.roll_returns.roll_returns` on that frame rather than typed. Its
month names are read off the planted contracts' symbols. The five prices fall
from 50.00 to 48.52, which would draw as a flat row, so the drop is drawn
larger than it is. No price axis is drawn, so no height carries a number. The
heights keep their order and their even spacing, which is what the two fits
read.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look, frame rate and colours.
The model sketch carries more than a reader takes in at that post's pace, so
it is in :data:`PACED`, and :func:`sketch_timeline` holds each of its labels
longer and its finished drawing for twelve seconds, as
:mod:`chan.equity_seasonals_whiteboard` does for its slow sketches. Only the
scenes, the pacing and the file names are this module's. Each GIF is named
:data:`GIF_PREFIX` plus the scene's slug, a prefix chosen so no GIF name
starts like the post's chart, ``roll_returns.png``.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw both with::

    uv run python -m chan.roll_returns_whiteboard
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.roll_returns import (
    MONTH_LETTERS,
    MONTHS_PER_YEAR,
    NEAREST,
    contract_month,
    roll_returns,
    roll_returns_in_months,
)
from chan.usdcad_tests_whiteboard import (
    Frame,
    Label,
    Scene,
    Stroke,
    _arrow,
    _dot,
    _line,
    _stroke,
    render,
    timeline,
)

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "roll_returns_sketch_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``roll_returns_sketch_one_line.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


# --- The model: one line, read two ways ----------------------------------------

#: Where the axes meet, and how far each runs.
MODEL_ORIGIN = (0.8, 0.35)
MODEL_X_END, MODEL_Y_END = 9.6, 3.6
#: The model's constant, spot return and roll return, in board units per unit
#: of date. Made up: γ is positive, which is backwardation, and α is smaller.
C, ALPHA, GAMMA = 2.62, 0.08, 0.25
#: The dates each line starts and the spot line ends, the three contracts'
#: expiries, and the one day the dashed line reads.
T_START, T_END = 0.9, 9.4
EXPIRIES = (3.6, 6.2, 8.8)
T0 = 2.4
#: How far the dashed line runs above the spot line.
DAY_ABOVE = 0.25


def spot_line(t: float | np.ndarray) -> float | np.ndarray:
    """The log spot price on the board, c + αt."""
    return C + ALPHA * np.asarray(t)


def contract_line(t: float | np.ndarray, expiry: float) -> float | np.ndarray:
    """The log price of the contract expiring at ``expiry``, c + αt − γ(T − t)."""
    t = np.asarray(t)
    return C + ALPHA * t - GAMMA * (expiry - t)


def _one_line() -> Scene:
    """The model: a contract held rises α + γ, and one day's contracts fall γ per year to expiry."""
    ox, oy = MODEL_ORIGIN
    held = EXPIRIES[-1]
    steps: list[Stroke | Label] = [
        _stroke("x-axis", _line([(ox, oy), (MODEL_X_END, oy)]), color=MUTED, frames=8),
        Label(
            "date t", MODEL_X_END - 0.1, oy + 0.32, names="x-axis", color=MUTED, size=12, ha="right"
        ),
        _stroke("y-axis", _line([(ox, oy), (ox, MODEL_Y_END)]), color=MUTED, frames=5),
        Label("log price", ox + 0.2, MODEL_Y_END, names="y-axis", color=MUTED, size=12),
        _stroke(
            "spot",
            _line([(T_START, float(spot_line(T_START))), (T_END, float(spot_line(T_END)))]),
            color=INK,
            frames=8,
        ),
        Label(
            "spot: rises at the spot return",
            9.55,
            3.95,
            names="spot",
            color=INK,
            size=12,
            ha="right",
        ),
    ]
    for expiry in EXPIRIES:
        gid = f"contract-{expiry}"
        start = (T_START, float(contract_line(T_START, expiry)))
        end = (expiry, float(spot_line(expiry)))
        steps.append(_stroke(gid, _line([start, end]), color=MUTED, frames=6))
        steps.append(_dot(f"{gid}-end", *end, color=MUTED))
    steps.append(
        Label(
            "each contract ends at the spot",
            2.9,
            3.52,
            names=f"contract-{held}-end",
            color=MUTED,
            size=12,
        )
    )
    steps.append(
        _stroke(
            "held",
            _arrow(T_START, float(contract_line(T_START, held)), held, float(spot_line(held))),
            color=ACCENT,
            width=3.0,
            frames=8,
        )
    )
    steps.append(
        Label(
            "hold one contract: spot return + roll return",
            4.6,
            1.55,
            names="held",
            color=ACCENT,
            size=12,
        )
    )
    steps.append(
        _stroke(
            "day",
            _line([(T0, oy), (T0, float(spot_line(T0)) + DAY_ABOVE)], per_unit=8),
            color=INK,
            dashed=True,
            width=1.5,
            frames=5,
        )
    )
    steps.append(_dot("day-spot", T0, float(spot_line(T0)), color=INK))
    for expiry in EXPIRIES:
        steps.append(_dot(f"day-{expiry}", T0, float(contract_line(T0, expiry)), color=INK))
    steps.append(
        Label(
            "hold one day: each year to expiry sits one roll return lower",
            2.9,
            1.05,
            names="day",
            color=GOOD,
            size=11,
        )
    )
    steps.append(
        Label("roll return above 0: backwardation", 2.9, 0.68, names="day", color=GOOD, size=12)
    )
    return Scene("One line, read two ways", "one_line", tuple(steps))


# --- Lesson 2: same five prices, three times the slope -------------------------

#: The planted example: quarterly contracts, March 2020 to June 2021, on four
#: days, priced on a forward curve with a roll return of 0.03 a year from a
#: price of 50. ``tests/test_roll_returns.py`` builds the same frame.
PLANTED_GAMMA = 0.03
PLANTED_SPOT = 50.0
PLANTED_DAYS = pd.bdate_range("2020-01-01", periods=4)
QUARTERLY = ("X-2020H", "X-2020M", "X-2020U", "X-2020Z", "X-2021H", "X-2021M")


@dataclass(frozen=True)
class Planted:
    """What the sketch reads off the planted frame: the five nearest contracts'
    months from the nearest, their month names, their log prices, and γ from
    each fit."""

    months: tuple[int, ...]
    names: tuple[str, ...]
    log_prices: tuple[float, ...]
    month_gamma: float
    column_gamma: float

    @property
    def times(self) -> int:
        """How many times the script's fit's γ is the fit in months', as a whole number."""
        ratio = self.column_gamma / self.month_gamma
        times = round(ratio)
        if not np.isclose(ratio, times, rtol=1e-9):
            raise ValueError(
                f"the script's fit is {ratio} times the fit in months, not a whole number"
            )
        return times


def planted_frame(gamma: float = PLANTED_GAMMA) -> pd.DataFrame:
    """The quarterly contracts on a forward curve with roll return ``gamma``,
    maturity in months, the same on every day."""
    months = np.array([contract_month(s) for s in QUARTERLY], dtype=float)
    months -= months[0]
    prices = np.tile(
        PLANTED_SPOT * np.exp(-gamma / MONTHS_PER_YEAR * months), (len(PLANTED_DAYS), 1)
    )
    return pd.DataFrame(prices, index=PLANTED_DAYS, columns=list(QUARTERLY))


def _one_value(gamma: pd.Series) -> float:
    """The γ every day of the planted frame shares."""
    values = gamma.to_numpy(dtype=float)
    if not (np.isfinite(values).all() and np.allclose(values, values[0], rtol=1e-12)):
        raise ValueError(f"the planted frame should give one γ on every day, not {values}")
    return float(values[0])


def planted(gamma: float = PLANTED_GAMMA) -> Planted:
    """Run both fits on the planted frame and read what the sketch draws."""
    frame = planted_frame(gamma)
    symbols = list(frame.columns[:NEAREST])
    months = [contract_month(s) - contract_month(symbols[0]) for s in symbols]
    names = tuple(calendar.month_abbr[MONTH_LETTERS.index(s[-1]) + 1] for s in symbols)
    return Planted(
        months=tuple(months),
        names=names,
        log_prices=tuple(float(v) for v in np.log(frame.iloc[0, :NEAREST].to_numpy(dtype=float))),
        month_gamma=_one_value(roll_returns_in_months(frame)),
        column_gamma=_one_value(roll_returns(frame)),
    )


#: Number words for the title and the closing label.
TIMES_WORDS = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}
#: Where the month axis sits, its first tick, and how far apart a month is.
MONTH_AXIS_Y, MONTH_X0, PER_MONTH = 0.85, 1.0, 0.62
#: The height of the first price, and how far the five fall on the board. The
#: true fall is a few percent, so the drop is drawn larger than it is.
FIRST_Y, DRAWN_DROP = 3.4, 1.2
#: How far short of a dot each sliding arrow stops, so the dot keeps its head clear.
ARROW_SHORT = 0.16


def month_x(month: float | np.ndarray) -> float | np.ndarray:
    """The board position of a maturity, in months from the nearest contract."""
    return MONTH_X0 + PER_MONTH * np.asarray(month, dtype=float)


def price_y(run: Planted) -> np.ndarray:
    """The five prices' board heights: the first at :data:`FIRST_Y`, the last
    :data:`DRAWN_DROP` below it, and the rest in proportion to their log prices."""
    logs = np.asarray(run.log_prices)
    return FIRST_Y - DRAWN_DROP * (logs[0] - logs) / (logs[0] - logs[-1])


def _fit(x: np.ndarray, y: np.ndarray) -> tuple:
    """The least-squares line through the dots, from the first dot to the last."""
    slope, intercept = np.polyfit(x, y, 1)
    x0, x1 = float(x.min()), float(x.max())
    return _line([(x0, intercept + slope * x0), (x1, intercept + slope * x1)])


def _same_five_prices(run: Planted) -> Scene:
    """Lesson 2: the planted prices at their months, then one column apart."""
    word = TIMES_WORDS[run.times]
    months = np.asarray(run.months, dtype=float)
    columns = np.arange(len(months), dtype=float)
    heights = price_y(run)
    by_month, by_column = month_x(months), month_x(columns)
    last = float(months[-1])
    ticks: list[tuple[float, float]] = [(float(month_x(0)) - 0.1, MONTH_AXIS_Y)]
    for m in range(int(last) + 1):
        x = float(month_x(m))
        ticks += [(x, MONTH_AXIS_Y), (x, MONTH_AXIS_Y - 0.09), (x, MONTH_AXIS_Y)]
    ticks.append((float(month_x(last)) + 0.5, MONTH_AXIS_Y))
    steps: list[Stroke | Label] = [
        _stroke("axis", _line(ticks, per_unit=4), color=MUTED, frames=8),
    ]
    for name, m in zip(run.names, months, strict=True):
        steps.append(
            Label(
                name,
                float(month_x(m)),
                MONTH_AXIS_Y - 0.43,
                names="axis",
                color=MUTED,
                size=11,
                ha="center",
            )
        )
    steps.append(
        Label(
            "months from the nearest contract",
            float(month_x(last)) + 0.5,
            1.2,
            names="axis",
            color=MUTED,
            size=12,
            ha="right",
        )
    )
    steps += [
        Stroke("prices", by_month, heights, color=INK, frames=4, dots=7.0),
        _stroke("months-fit", _fit(by_month, heights), color=GOOD, frames=6),
        Label(
            f"fit in months: {run.month_gamma:.2f} a year",
            6.4,
            3.2,
            names="months-fit",
            color=GOOD,
            size=12,
        ),
    ]
    for k in range(1, len(months)):
        steps.append(
            _stroke(
                f"slide-{k}",
                _arrow(
                    float(by_month[k]) - 0.12,
                    float(heights[k]),
                    float(by_column[k]) + ARROW_SHORT,
                    float(heights[k]),
                ),
                color=MUTED,
                width=1.5,
                frames=4,
            )
        )
    steps += [
        Label(
            "same prices, one column apart",
            5.8,
            1.8,
            names=f"slide-{len(months) - 1}",
            color=MUTED,
            size=12,
        ),
        Stroke("columns", by_column, heights, color=LOST, frames=4, dots=7.0),
        _stroke("script-fit", _fit(by_column, heights), color=LOST, frames=6),
        Label(
            f"script’s fit: {run.column_gamma:.2f} a year, {word} times",
            0.9,
            1.55,
            names="script-fit",
            color=LOST,
            size=12,
        ),
    ]
    return Scene(f"Same five prices, {word} times the slope", "same_five_prices", tuple(steps))


# --- Drawing ------------------------------------------------------------------

#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("one_line",)
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


def scenes(run: Planted | None = None) -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them, the model's then Lesson 2's."""
    return (_one_line(), _same_five_prices(run if run is not None else planted()))


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


def make_roll_returns_whiteboards(out_dir: Path | None = None) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes()]


def main() -> None:
    for path in make_roll_returns_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
