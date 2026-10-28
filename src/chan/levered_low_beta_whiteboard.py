"""Whiteboard sketches for the levered low-beta post, both for Lesson 3.

``blog/levered-low-beta-lessons.md`` makes two claims in Lesson 3 that a
sentence has to build in the reader's head: a higher leverage moves the ruin
line toward zero, so a smaller loss ruins, and June 2001's line was crossed by
an ordinary month rather than a rare one. This module draws the two as scenes,
and the post places each right after the paragraph it draws.

1. The ruin line: axes with the low fifth's monthly return across and the
   levered month's return up, at scales that differ by about a hundred, and a
   red floor at −1 where the whole capital is lost. Every levered line
   rf + k × (r_low − rf) passes through the point (rf, rf), drawn as a dot. A
   grey line at k = 23.2017, the smallest leverage that ruins June, meets the
   floor at June's own return of −0.0403. A black line at June's k of 58.0262
   meets it at −0.0144, June's ruin line. Dashed grey drops carry each meeting
   down to the axis, and a red dot on the black line marks June's month, a
   return of −0.0403 levered to −2.5053, below the floor. It sits in Lesson 3,
   after the paragraph that says "the line sat at −0.0144".
2. Thirteen of 83 months past June's line: a return axis, a bell curve with
   the low fifth's monthly mean of 0.0109 and standard deviation of 0.0292, a
   red line at June's line of −0.0144, and the curve's tail left of it shaded
   red, where the curve puts 0.1931 of its months. Under the axis the 83 low
   fifth months sit as a strip of dots in return order, the 13 at or below the
   line in red. Where two dots would overlap, the later one drops a row, so
   the strip piles up where months crowd together. It sits in Lesson 3, after
   the paragraph that says "13 fell at or below June".

Neither sketch is schematic. Every figure either sketch prints, and every
position it draws a line, a dot or the curve at, comes from :class:`RuinFigures`, which
:meth:`RuinFigures.from_run` reads through :func:`chan.low_beta_leverage.read_sources`
and :func:`chan.low_beta_leverage.build_portfolios`, the run's own path. The
ruin line and the leverage that ruins come from
:func:`chan.low_beta_leverage.ruin_line` and
:func:`chan.low_beta_leverage.ruinous_leverage`. The ruined month is the run's
first, from :func:`chan.low_beta_leverage.ruined_months`, rather than a date
typed here. The axes' tick values, 0, −1 and −2 up the first sketch, are
gridlines rather than figures. The bell curve is drawn to its own height, so
it shows shape and the shaded share rather than a count of months. The curve
would expect about 16 months at or below the line, a figure the post does not
state.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look, frame rate and colours.
This post's chart still draws in :mod:`chan.regime_figure`'s shared inks, so
the sketches do too. Each sketch carries more than a reader takes in at that
post's pace, so both are in :data:`PACED`, and :func:`sketch_timeline` holds
each of their labels longer and their finished drawings for twelve seconds,
as :mod:`chan.equity_seasonals_whiteboard` does for its slow sketches. Each GIF
is named :data:`GIF_PREFIX` plus the scene's slug. The post's chart,
``low_beta_leverage.png``, does not start with that prefix, so nothing that
looks for the sketches by prefix finds the chart.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw both with::

    uv run python -m chan.levered_low_beta_whiteboard
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from statistics import NormalDist

import numpy as np

from chan import low_beta_leverage as llb
from chan.paths import FIGURES_DIR
from chan.regime_figure import INK, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    Frame,
    Label,
    Scene,
    Stroke,
    _dot,
    _line,
    _stroke,
    render,
    timeline,
)

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "levered_low_beta_sketch_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``levered_low_beta_sketch_ruin_line.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


# --- The figures, read from the run ---------------------------------------------


@dataclass(frozen=True)
class RuinFigures:
    """What both sketches draw: the first ruined month, and every month's low fifth return.

    ``month`` is the ruined month's last day, the ``held_to`` of its
    formation. ``rf``, ``leverage``, ``line``, ``low`` and ``levered`` are that
    month's bill rate, k, ruin line, low fifth return and levered return.
    ``ruinous`` is the smallest leverage that would have ruined it. ``returns``
    holds the low fifth's return in every holding month, in date order.
    """

    month: str
    rf: float
    leverage: float
    line: float
    low: float
    levered: float
    ruinous: float
    returns: tuple[float, ...]

    @property
    def mean(self) -> float:
        return float(np.mean(self.returns))

    @property
    def sd(self) -> float:
        """The standard deviation with ddof 1, as the post's figure is."""
        return float(np.std(self.returns, ddof=1))

    @property
    def reached(self) -> int:
        """How many months' low fifth return sits at or below the ruin line."""
        return sum(r <= self.line for r in self.returns)

    @property
    def chance(self) -> float:
        """The share of a bell curve with :attr:`mean` and :attr:`sd` at or below the line."""
        return NormalDist(self.mean, self.sd).cdf(self.line)

    @classmethod
    def from_run(cls, data_dir: Path | None = None) -> RuinFigures:
        """Read the committed vintages through the run's own path."""
        _, closes, _, spy, _, bills = llb.read_sources(data_dir)
        return cls.from_portfolios(llb.build_portfolios(closes, spy, bills))

    @classmethod
    def from_portfolios(cls, p: llb.Portfolios) -> RuinFigures:
        """The figures for the first month the run's levered portfolio was ruined."""
        month = llb.ruined_months(p)[0].held_to
        return cls(
            month=str(month.date()),
            rf=float(p.rf.loc[month]),
            leverage=float(p.leverage.loc[month]),
            line=float(llb.ruin_line(p.rf, p.leverage).loc[month]),
            low=float(p.low.loc[month]),
            levered=float(p.levered.loc[month]),
            ruinous=float(llb.ruinous_leverage(p.low, p.rf).loc[month]),
            returns=tuple(float(r) for r in p.low),
        )

    @property
    def name(self) -> str:
        """The ruined month's name, such as ``June``."""
        return date.fromisoformat(self.month).strftime("%B")


def four(value: float) -> str:
    """``value`` to four decimals with a typographic minus, as the post prints it."""
    return f"{value:.4f}".replace("-", "−")


#: Counts in words for a title, up to twenty.
COUNT_WORDS = (
    "Zero One Two Three Four Five Six Seven Eight Nine Ten Eleven Twelve Thirteen"
    " Fourteen Fifteen Sixteen Seventeen Eighteen Nineteen Twenty"
).split()


def spelled(n: int) -> str:
    """``n`` in words up to twenty, as a title starts a count, and in digits past it."""
    return COUNT_WORDS[n] if n < len(COUNT_WORDS) else str(n)


# --- Lesson 3: the ruin line ------------------------------------------------------

#: The window the first sketch draws: the low fifth's return across and the
#: levered return up, and where each lands on the board.
RUIN_R, RUIN_X = (-0.065, 0.025), (1.3, 9.5)
LEVERED, RUIN_Y = (-2.85, 0.45), (0.72, 3.6)
#: Where the return axis runs, just under the window, and the levered return
#: of each tick up the other axis.
AXIS_Y = 0.62
Y_TICKS = (0.0, -1.0, -2.0)
TICK = 0.08


def r_x(r: float | np.ndarray) -> float | np.ndarray:
    """The board across of a low fifth return."""
    (r0, r1), (x0, x1) = RUIN_R, RUIN_X
    return x0 + (np.asarray(r) - r0) * (x1 - x0) / (r1 - r0)


def lev_y(v: float | np.ndarray) -> float | np.ndarray:
    """The board height of a levered return."""
    (v0, v1), (y0, y1) = LEVERED, RUIN_Y
    return y0 + (np.asarray(v) - v0) * (y1 - y0) / (v1 - v0)


def levered_line(f: RuinFigures, k: float) -> tuple[float, float]:
    """The low fifth returns where rf + k × (r − rf) leaves the window, left end first."""
    lo = max(RUIN_R[0], f.rf + (LEVERED[0] - f.rf) / k)
    hi = min(RUIN_R[1], f.rf + (LEVERED[1] - f.rf) / k)
    return lo, hi


def _levered_stroke(gid: str, f: RuinFigures, k: float, color: str) -> Stroke:
    lo, hi = levered_line(f, k)
    points = [(float(r_x(r)), float(lev_y(f.rf + k * (r - f.rf)))) for r in (lo, hi)]
    return _stroke(gid, _line(points), color=color, frames=8)


def _y_axis() -> tuple:
    """The levered return's axis, bottom to top, with a tick out and back at each
    of :data:`Y_TICKS`."""
    x = RUIN_X[0]
    points = [(x, AXIS_Y)]
    for v in sorted(Y_TICKS):
        y = float(lev_y(v))
        points += [(x, y), (x - TICK, y), (x, y)]
    points.append((x, RUIN_Y[1]))
    return _line(points)


def _x_axis(f: RuinFigures) -> tuple:
    """The low fifth return's axis, with a tick down at each line's meeting with the floor."""
    points = [(RUIN_X[0], AXIS_Y)]
    for r in sorted((f.low, f.line)):
        x = float(r_x(r))
        points += [(x, AXIS_Y), (x, AXIS_Y - TICK), (x, AXIS_Y)]
    points.append((RUIN_X[1], AXIS_Y))
    return _line(points)


def _ruin_line(f: RuinFigures) -> Scene:
    """Lesson 3: a steeper levered line meets −1 nearer zero, so a smaller loss ruins."""
    floor_y = float(lev_y(llb.RUIN))
    pivot = (float(r_x(f.rf)), float(lev_y(f.rf)))
    meets_low, meets_line = float(r_x(f.low)), float(r_x(f.line))
    dot_y = float(lev_y(f.levered))
    name = f.name
    steps: list[Stroke | Label] = [
        _stroke("y-axis", _y_axis(), color=MUTED, frames=6),
        Label("levered month", RUIN_X[0] + 0.2, 3.82, names="y-axis", color=MUTED, size=11),
        *(
            Label(
                f"{v:.0f}".replace("-", "−"),
                RUIN_X[0] - TICK - 0.2,
                float(lev_y(v)),
                names="y-axis",
                color=MUTED,
                size=10,
                ha="right",
            )
            for v in Y_TICKS
        ),
        _stroke("x-axis", _x_axis(f), color=MUTED, frames=8),
        Label(
            "low fifth’s month",
            RUIN_X[1],
            AXIS_Y - 0.38,
            names="x-axis",
            color=MUTED,
            size=11,
            ha="right",
        ),
        _stroke("floor", _line([(RUIN_X[0], floor_y), (RUIN_X[1], floor_y)]), color=LOST, frames=6),
        Label(
            "whole capital lost",
            RUIN_X[0] + 0.2,
            floor_y + 0.3,
            names="floor",
            color=LOST,
            size=11,
        ),
        _dot("pivot", *pivot, color=INK),
        Label(
            f"every line turns on rf = {four(f.rf)}",
            pivot[0] - 0.25,
            pivot[1] + 0.3,
            names="pivot",
            size=11,
            ha="right",
        ),
        _levered_stroke("ruinous", f, f.ruinous, MUTED),
        _stroke(
            "ruinous-drop",
            _line([(meets_low, floor_y), (meets_low, AXIS_Y)]),
            color=MUTED,
            dashed=True,
            width=1.5,
            frames=4,
        ),
        Label(four(f.low), meets_low, AXIS_Y - 0.38, names="ruinous-drop", size=10, ha="center"),
        Label(
            f"k = {four(f.ruinous)}, the least that ruins {name}",
            RUIN_X[0] + 0.2,
            3.15,
            names="ruinous",
            color=MUTED,
            size=11,
        ),
        _levered_stroke("asked", f, f.leverage, INK),
        _stroke(
            "asked-drop",
            _line([(meets_line, floor_y), (meets_line, AXIS_Y)]),
            color=MUTED,
            dashed=True,
            width=1.5,
            frames=4,
        ),
        Label(four(f.line), meets_line, AXIS_Y - 0.38, names="asked-drop", size=10, ha="center"),
        Label(
            f"{name}’s k = {four(f.leverage)}",
            meets_line + 0.25,
            1.95,
            names="asked",
            size=11,
        ),
        _dot("month", meets_low, dot_y, color=LOST),
        Label(
            f"{name}: {four(f.levered)}",
            meets_low - 0.25,
            dot_y + 0.2,
            names="month",
            color=LOST,
            size=11,
            ha="right",
        ),
        Label(
            "steeper line: smaller loss ruins",
            RUIN_X[1],
            1.25,
            names="asked",
            size=11,
            ha="right",
        ),
    ]
    return Scene("The ruin line", "ruin_line", tuple(steps))


# --- Lesson 3: how many months reach June's line ---------------------------------

#: The return axis across the second sketch, the board it spans, its height,
#: and the curve's height at its peak.
TAIL_R, TAIL_X = (-0.08, 0.115), (0.5, 9.5)
TAIL_AXIS_Y, CURVE_HEIGHT = 1.45, 1.9
#: The strip under the axis: its first row, how far each row sits below the
#: last, and how close two dots in one row may sit, in board units.
STRIP_TOP, ROW_STEP, DOT_APART = 1.15, 0.12, 0.1
DOT_SIZE = 4.5


def tail_x(r: float | np.ndarray) -> float | np.ndarray:
    """The board across of a monthly return."""
    (r0, r1), (x0, x1) = TAIL_R, TAIL_X
    return x0 + (np.asarray(r) - r0) * (x1 - x0) / (r1 - r0)


def curve_y(f: RuinFigures, r: float | np.ndarray) -> np.ndarray:
    """The board height of the bell curve at return ``r``, its peak :data:`CURVE_HEIGHT` up."""
    z = (np.asarray(r) - f.mean) / f.sd
    return TAIL_AXIS_Y + CURVE_HEIGHT * np.exp(-0.5 * z**2)


def strip_rows(xs: np.ndarray) -> np.ndarray:
    """A row for each dot: the first row, counting down, with no dot within :data:`DOT_APART`.

    Dots are placed left to right, so the strip stays in return order and a
    dot moves down only where its neighbours would hide it.
    """
    rows = np.zeros(len(xs), dtype=int)
    last: list[float] = []
    for k in np.argsort(xs, kind="stable"):
        row = next((n for n, x in enumerate(last) if xs[k] - x >= DOT_APART), len(last))
        if row == len(last):
            last.append(xs[k])
        else:
            last[row] = xs[k]
        rows[k] = row
    return rows


def _shade(xs: np.ndarray, base: float, tops: np.ndarray) -> tuple:
    """Upright strokes from ``base`` up to each of ``tops``, as one pen path."""
    points: list[tuple[float, float]] = []
    for k, (x, top) in enumerate(zip(xs, tops, strict=True)):
        points += [(x, base), (x, top)] if k % 2 == 0 else [(x, top), (x, base)]
    return _line(points, per_unit=8)


def _dots(gid: str, xs: np.ndarray, rows: np.ndarray, color: str) -> Stroke:
    order = np.argsort(xs, kind="stable")
    return Stroke(
        gid,
        xs[order],
        STRIP_TOP - ROW_STEP * rows[order],
        color=color,
        frames=6,
        dots=DOT_SIZE,
    )


def _months_past(f: RuinFigures) -> Scene:
    """Lesson 3: the low fifth's months against June's line, beside a bell curve's tail."""
    name = f.name
    line_x = float(tail_x(f.line))
    rs = np.linspace(*TAIL_R, 140)
    tail = np.linspace(TAIL_R[0] + 0.002, f.line - 0.0008, 18)
    returns = np.array(f.returns)
    xs = tail_x(returns)
    rows = strip_rows(xs)
    past = returns <= f.line
    steps: list[Stroke | Label] = [
        _stroke("axis", _line([(TAIL_X[0], TAIL_AXIS_Y), (TAIL_X[1], TAIL_AXIS_Y)]), color=MUTED),
        _stroke("curve", (tail_x(rs), curve_y(f, rs)), color=INK, frames=10),
        Label(
            f"bell curve: mean {four(f.mean)}, sd {four(f.sd)}",
            float(tail_x(f.mean)) + 0.95,
            TAIL_AXIS_Y + CURVE_HEIGHT - 0.05,
            names="curve",
            size=11,
        ),
        _stroke(
            "line",
            _line([(line_x, STRIP_TOP - ROW_STEP * (rows.max() + 0.5)), (line_x, 3.62)]),
            color=LOST,
            frames=6,
        ),
        Label(
            f"{name}’s line, {four(f.line)}",
            line_x - 0.2,
            3.85,
            names="line",
            color=LOST,
            size=11,
            ha="right",
        ),
        _stroke(
            "tail",
            _shade(tail_x(tail), TAIL_AXIS_Y, curve_y(f, tail)),
            color=LOST,
            width=1.0,
            frames=6,
        ),
        Label(
            f"{four(f.chance)} of the curve",
            TAIL_X[0] + 0.05,
            3.17,
            names="tail",
            color=LOST,
            size=11,
        ),
        Label(
            f"about one month in {spelled(round(1 / f.chance)).lower()}",
            TAIL_X[0] + 0.05,
            2.86,
            names="tail",
            color=LOST,
            size=11,
        ),
        _dots("months", xs[~past], rows[~past], INK),
        Label(
            f"the low fifth’s {len(returns)} monthly returns",
            TAIL_X[1],
            0.3,
            names="months",
            size=11,
            ha="right",
        ),
        _dots("past", xs[past], rows[past], LOST),
        Label(
            f"{f.reached} of {len(returns)} at or below",
            TAIL_X[0],
            0.3,
            names="past",
            color=LOST,
            size=11,
        ),
    ]
    title = f"{spelled(f.reached)} of {len(returns)} months past {name}’s line"
    return Scene(title, "months_past", tuple(steps))


# --- Drawing ------------------------------------------------------------------

#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("ruin_line", "months_past")
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


def scenes(figures: RuinFigures | None = None) -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them.

    ``figures`` defaults to :meth:`RuinFigures.from_run` on the committed vintages.
    """
    found = figures if figures is not None else RuinFigures.from_run()
    return (_ruin_line(found), _months_past(found))


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


def make_levered_low_beta_whiteboards(out_dir: Path | None = None) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes()]


def main() -> None:
    for path in make_levered_low_beta_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
