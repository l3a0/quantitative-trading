"""Whiteboard sketches for the Kalman filter hedge post, one of a filter day and one for Lesson 2.

``blog/kalman-hedge-lessons.md`` makes two claims a sentence has to build in
the reader's head: each day the filter runs four steps that end with its guess
moved toward the close it just saw, and on the file's first two rows the
filter forecasts EWC at 0, so its error is EWC's whole close and the rule
shorts EWC with no hedge. This module draws the two as scenes, and the post
places each right after the passage it draws.

1. One day of the filter, under "The filter and the file", after the
   paragraph opening "After the first day, the filter never becomes
   confident". It draws 2007-05-15 on axes of EWA's close across and EWC's
   close up, zoomed around that day. A black line is yesterday's slope and
   intercept, a grey tick on it at today's EWA is the forecast, two brass
   hairlines are the band of plus and minus one forecast standard deviation,
   a black dot is EWC's close, and a red bar from the forecast to the close is
   the forecast error. A green line is the slope and intercept after the
   update. A closing line of words splits the update's lift at today's EWA
   into the slope's part, its rise times today's EWA, and the intercept's
   rise, and gives the share of the miss the lift closed. A numbered list of
   the post's four steps runs down the left side, each step appearing with its
   mark and in its mark's colour.
2. Two rows on a forecast of 0, in Lesson 2, after the paragraph opening
   "**What that trade earns.**". Three columns on one dollar scale draw rows
   1 to 3, 2006-04-26 to 2006-04-28. In each, a grey dot is the forecast, a
   black dot EWC's close, a red bar the forecast error between them, and two
   brass hairlines the band around the forecast, drawn to the same scale, so
   on rows 1 and 2 they all but vanish beside an error the size of the close.
   Words under the columns say what the rule held: a short in EWC alone on
   row 1, which earns the first nonzero return on 2006-04-27, a slope that
   moves off 0 only after row 2's forecast, and row 3's forecast made with
   that slope, the one row 2's update left.

Neither sketch is schematic. Every figure either one draws is read from
:func:`chan.kalman_hedge.kalman_hedge` on the committed file through
:func:`chan.kalman_hedge.read_sources`, the run's own path, through
:class:`OneDay` and :class:`ZeroStart`, and every mark sits at its figure on
the sketch's own scale. The first sketch's two axes are zoomed around the day,
each to its own scale, so the forecast, the close and the two lines can be
told apart.

Row 2's short is not EWC alone. Positions use the slope after each row's
update, and row 2's update moves the slope to 1.366666 before the position is
set, so no word under the second column says the short is unhedged. Only row
1's position, which earns 2006-04-27's return, holds 0 EWA shares.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look and frame rate. They draw in
the shared colours of :mod:`chan.regime_figure`, as the post's chart does.
Each sketch carries more than a reader takes in at that post's pace, so both
are in :data:`PACED`, and :func:`sketch_timeline` holds each of their labels
longer and their finished drawings for twelve seconds, as
:mod:`chan.equity_seasonals_whiteboard` does for its slow sketches. Each GIF
is named :data:`GIF_PREFIX` plus the scene's slug, a prefix chosen so no GIF
name starts like the post's chart, ``kalman_hedge.png``.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw both with::

    uv run python -m chan.kalman_hedge_whiteboard
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from chan import kalman_hedge
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
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
GIF_PREFIX = "kalman_hedge_sketch_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``kalman_hedge_sketch_one_day.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


def _run(data_dir: Path | None = None) -> tuple[np.ndarray, np.ndarray, kalman_hedge.KalmanHedge]:
    """EWA's and EWC's closes and the run, read as ``python -m chan.kalman_hedge`` reads them."""
    _, closes = kalman_hedge.read_sources(data_dir)
    result = kalman_hedge.kalman_hedge(closes)
    return (
        closes[kalman_hedge.X].to_numpy(dtype=float),
        closes[kalman_hedge.Y].to_numpy(dtype=float),
        result,
    )


def _dollars(value: float) -> str:
    """A price or a forecast at the file's two decimals, and a forecast of exactly 0 as 0."""
    return "0" if value == 0 else f"{value:.2f}"


# --- The filter and the file: one day of the filter --------------------------


@dataclass(frozen=True)
class OneDay:
    """What the one-day sketch reads off the run, all on one row.

    ``slope_before`` and ``intercept_before`` are the state after the row
    before's update, which this row's forecast uses. ``forecast`` is EWC's
    forecast from them at today's EWA, ``error`` is EWC's close minus it, and
    ``sd`` is the square root of the forecast variance, the band's half-width.
    ``slope_after`` and ``intercept_after`` are the state after this row's
    update.
    """

    day: str
    ewa: float
    close: float
    slope_before: float
    intercept_before: float
    forecast: float
    error: float
    sd: float
    slope_after: float
    intercept_after: float

    @property
    def moved(self) -> float:
        """The updated slope and intercept's forecast at today's EWA."""
        return self.slope_after * self.ewa + self.intercept_after

    @property
    def slope_lift(self) -> float:
        """How far the slope's rise alone lifts the line at today's EWA."""
        return (self.slope_after - self.slope_before) * self.ewa

    @property
    def intercept_lift(self) -> float:
        """How far the intercept's rise lifts the line, the same at every EWA."""
        return self.intercept_after - self.intercept_before

    @property
    def closed(self) -> float:
        """The share of the forecast error the update closes at today's EWA."""
        return (self.moved - self.forecast) / self.error

    def before(self, ewa: float) -> float:
        """Yesterday's line at ``ewa``."""
        return self.slope_before * ewa + self.intercept_before

    def after(self, ewa: float) -> float:
        """The updated line at ``ewa``."""
        return self.slope_after * ewa + self.intercept_after

    @classmethod
    def from_run(cls, day: str = "2007-05-15", data_dir: Path | None = None) -> OneDay:
        """Read ``day``'s row from the run on the committed file.

        The file's first row has no row before it, so it has no state for its
        forecast to use, and reading one would wrap round to the last row's.
        """
        x, y, result = _run(data_dir)
        f = result.filter
        (t,) = np.flatnonzero(f.days == day)
        if t == 0:
            raise ValueError(
                f"{day} is the file's first row, so no row before it holds the slope and "
                "intercept its forecast uses"
            )
        return cls(
            day=day,
            ewa=float(x[t]),
            close=float(y[t]),
            slope_before=float(f.slope[t - 1]),
            intercept_before=float(f.intercept[t - 1]),
            forecast=float(y[t] - f.error[t]),
            error=float(f.error[t]),
            sd=float(np.sqrt(f.variance[t])),
            slope_after=float(f.slope[t]),
            intercept_after=float(f.intercept[t]),
        )


#: The plot's corners on the board, and the axes' corner just outside them.
#: The lines stop at the plot's right edge, and their labels sit past it.
PLOT_X, PLOT_Y = (1.95, 6.7), (1.05, 3.85)
AXIS_X, AXIS_Y = 1.75, 0.92
#: How far the zoomed axes reach either side of the day, in dollars: EWA's
#: close across, and EWC's close up from under the band to over the close.
EWA_REACH = 0.2
EWC_BELOW, EWC_ABOVE = 0.12, 0.31
#: Half the width of the forecast tick and of the band's hairlines.
TICK_HALF, HAIR_HALF = 0.18, 0.3
#: The post's four steps, as the numbered list down the left side names them.
STEPS = ("hold", "forecast", "miss", "update")
#: The list's left edge and its four rows' heights, top to bottom.
GUTTER_X, GUTTER_Y = 0.25, (3.2, 2.65, 2.1, 1.55)
#: Where the labels past the lines' right ends start, and the closing line's height.
ENDS_X, CLOSING_Y = 6.9, 0.2


@dataclass(frozen=True)
class Scale:
    """An affine map from (EWA, EWC) in dollars to the board, each axis its own."""

    ewa: tuple[float, float]
    ewc: tuple[float, float]

    def x(self, ewa: float) -> float:
        lo, hi = self.ewa
        return PLOT_X[0] + (ewa - lo) / (hi - lo) * (PLOT_X[1] - PLOT_X[0])

    def y(self, ewc: float) -> float:
        lo, hi = self.ewc
        return PLOT_Y[0] + (ewc - lo) / (hi - lo) * (PLOT_Y[1] - PLOT_Y[0])

    def ewa_at(self, x: float) -> float:
        lo, hi = self.ewa
        return lo + (x - PLOT_X[0]) / (PLOT_X[1] - PLOT_X[0]) * (hi - lo)


def scale(day: OneDay) -> Scale:
    """The zoom around ``day``: EWA either side of today's, EWC from under the
    band's lower edge to over the close."""
    return Scale(
        ewa=(day.ewa - EWA_REACH, day.ewa + EWA_REACH),
        ewc=(day.forecast - day.sd - EWC_BELOW, day.close + EWC_ABOVE),
    )


def _across(s: Scale, line, gid: str, color: str) -> Stroke:
    """``line`` across the plot from its left edge to its right."""
    xs = np.linspace(PLOT_X[0], PLOT_X[1], 90)
    ys = np.array([s.y(line(s.ewa_at(x))) for x in xs])
    return Stroke(gid, xs, ys, color=color, frames=10)


def _gutter(k: int, names: str, color: str) -> Label:
    """Step ``k + 1`` of :data:`STEPS` down the left side, in the colour of the mark it makes."""
    return Label(f"{k + 1} {STEPS[k]}", GUTTER_X, GUTTER_Y[k], names=names, color=color, size=12)


def _one_day(day: OneDay) -> Scene:
    """The four steps of one day, drawn to scale on axes zoomed around it."""
    s = scale(day)
    today = s.x(day.ewa)
    f, c = s.y(day.forecast), s.y(day.close)
    low, high = s.y(day.forecast - day.sd), s.y(day.forecast + day.sd)
    old_end, new_end = s.y(day.before(s.ewa[1])), s.y(day.after(s.ewa[1]))
    ds, di = day.slope_after - day.slope_before, day.intercept_lift
    steps: list[Stroke | Label] = [
        _stroke("ewa-axis", _arrow(AXIS_X, AXIS_Y, PLOT_X[1] + 0.1, AXIS_Y), color=MUTED, frames=6),
        _stroke(
            "ewc-axis", _arrow(AXIS_X, AXIS_Y, AXIS_X, PLOT_Y[1] + 0.05), color=MUTED, frames=6
        ),
        Label(
            "EWA close",
            PLOT_X[1] + 0.1,
            AXIS_Y - 0.4,
            names="ewa-axis",
            color=MUTED,
            size=11,
            ha="right",
        ),
        Label("EWC close", GUTTER_X, PLOT_Y[1] - 0.05, names="ewc-axis", color=MUTED, size=11),
        _across(s, day.before, "yesterday", INK),
        _gutter(0, "yesterday", INK),
        Label(
            f"yesterday: slope {day.slope_before:.6f},",
            ENDS_X,
            old_end + 0.15,
            names="yesterday",
            color=INK,
            size=10,
        ),
        Label(
            f"intercept {day.intercept_before:.6f}",
            ENDS_X,
            old_end - 0.15,
            names="yesterday",
            color=INK,
            size=10,
        ),
        _stroke(
            "today",
            _line([(today, AXIS_Y - 0.1), (today, AXIS_Y + 0.1)], per_unit=12),
            color=MUTED,
            frames=2,
        ),
        Label(
            f"EWA {day.ewa:.2f}",
            today,
            AXIS_Y - 0.4,
            names="today",
            color=MUTED,
            size=11,
            ha="center",
        ),
        _stroke(
            "forecast",
            _line([(today - TICK_HALF, f), (today + TICK_HALF, f)], per_unit=12),
            color=MUTED,
            width=3,
            frames=2,
        ),
        _gutter(1, "forecast", MUTED),
        Label(
            f"forecast {_dollars(day.forecast)}",
            today + 0.3,
            f - 0.32,
            names="forecast",
            color=MUTED,
            size=11,
        ),
        _stroke(
            "band-high",
            _line([(today - HAIR_HALF, high), (today + HAIR_HALF, high)], per_unit=12),
            color=ACCENT,
            width=1.2,
            frames=3,
        ),
        _stroke(
            "band-low",
            _line([(today - HAIR_HALF, low), (today + HAIR_HALF, low)], per_unit=12),
            color=ACCENT,
            width=1.2,
            frames=3,
        ),
        Label(
            f"band ±{day.sd:.2f}",
            today + HAIR_HALF + 0.17,
            low,
            names="band-low",
            color=ACCENT,
            size=11,
        ),
        _dot("close", today, c, color=INK),
        Label(
            f"close {_dollars(day.close)}",
            today - 0.2,
            c + 0.32,
            names="close",
            color=INK,
            size=11,
            ha="right",
        ),
        _stroke(
            "error", _line([(today, f), (today, c)], per_unit=12), color=LOST, width=2.6, frames=5
        ),
        _gutter(2, "error", LOST),
        Label(
            f"error {day.error:.2f}",
            today - HAIR_HALF - 0.15,
            (f + c) / 2 - 0.24,
            names="error",
            color=LOST,
            size=11,
            ha="right",
        ),
        _across(s, day.after, "updated", GOOD),
        _gutter(3, "updated", GOOD),
        Label(
            f"updated: slope {day.slope_after:.6f},",
            ENDS_X,
            new_end + 0.15,
            names="updated",
            color=GOOD,
            size=10,
        ),
        Label(
            f"intercept {day.intercept_after:.6f}",
            ENDS_X,
            new_end - 0.15,
            names="updated",
            color=GOOD,
            size=10,
        ),
        Label(
            f"slope {ds:+.6f} × EWA {day.ewa:.2f} = {day.slope_lift:+.2f}, "
            f"intercept {di:+.6f}: line to {_dollars(day.moved)}, {day.closed:.0%} of the miss",
            GUTTER_X,
            CLOSING_Y,
            names="updated",
            color=GOOD,
            size=10,
        ),
    ]
    return Scene("One day of the filter", "one_day", tuple(steps))


# --- Lesson 2: two rows on a forecast of 0 ------------------------------------


@dataclass(frozen=True)
class Row:
    """One row's forecast, close, error and band, and the slope after its update."""

    day: str
    forecast: float
    close: float
    error: float
    band: float
    slope: float


@dataclass(frozen=True)
class ZeroStart:
    """What the Lesson 2 sketch reads off the run: the file's first three rows,
    the units the script holds on row 1, and the first nonzero return, which
    row 1's position earns on the day after."""

    rows: tuple[Row, Row, Row]
    units: float
    first_return: float
    first_return_day: str

    @classmethod
    def from_run(cls, data_dir: Path | None = None) -> ZeroStart:
        """Read rows 1 to 3 and the first return from the run on the committed file."""
        _, y, result = _run(data_dir)
        f, t = result.filter, result.trade
        rows = tuple(
            Row(
                day=str(f.days[k].date()),
                forecast=float(y[k] - f.error[k]),
                close=float(y[k]),
                error=float(f.error[k]),
                band=float(np.sqrt(f.variance[k])),
                slope=float(f.slope[k]),
            )
            for k in range(3)
        )
        first = int(np.flatnonzero(t.daily)[0])
        return cls(
            rows=rows,
            units=float(t.units[0]),
            first_return=float(t.daily[first]),
            first_return_day=str(f.days[first].date()),
        )


#: Each column's red bar, left to right.
COLUMN_X = (0.75, 4.45, 7.42)
#: The board height of a dollar of 0 and the dollars per board unit up.
FLOOR_Y, PER_DOLLAR = 1.72, 0.088
#: How far each column's dots sit beside its bar, the forecast's to the left
#: and the close's to the right, so a short bar is not hidden under a dot.
DOT_OFFSET = 0.25
#: The heights of the date line and the two lines of words under the columns.
DATE_Y, WORDS_Y = (1.2, (0.84, 0.5))


def dollar_y(value: float) -> float:
    """A dollar value's height on the Lesson 2 sketch's one scale."""
    return FLOOR_Y + value * PER_DOLLAR


#: A bar taller than this, in board units, has room for its error label
#: beside it. A shorter one stacks all four labels beside its close.
LONG_BAR = 1.0


def label_places(k: int, row: Row) -> dict[str, tuple[float, float]]:
    """Where each of row ``k + 1``'s four labels sits, by what it names.

    Beside a long bar the close's label sits at the close, the error's at the
    bar's middle, and the band's and the forecast's just above and below the
    forecast. Beside a short bar, where all four marks crowd one height, they
    stack downward from the close in that order.
    """
    x = COLUMN_X[k]
    f, c = dollar_y(row.forecast), dollar_y(row.close)
    words_x = x + DOT_OFFSET + 0.25
    if abs(c - f) > LONG_BAR:
        return {
            "close": (words_x, c),
            "error": (x + 0.2, (f + c) / 2),
            "band": (words_x - 0.1, f + 0.16),
            "forecast": (words_x - 0.1, f - 0.16),
        }
    return {
        "close": (words_x, c + 0.05),
        "error": (words_x, c - 0.29),
        "band": (words_x, c - 0.63),
        "forecast": (words_x, c - 0.97),
    }


def _column(k: int, row: Row) -> list[Stroke | Label]:
    """Row ``k + 1``'s forecast, close, error and band, each with its label, and its date.

    Beside a short bar the labels appear in the order :func:`label_places`
    stacks them, close to forecast, rather than the forecast's first.
    """
    x = COLUMN_X[k]
    f, c = dollar_y(row.forecast), dollar_y(row.close)
    low, high = dollar_y(row.forecast - row.band), dollar_y(row.forecast + row.band)
    bar = _line([(x, f), (x, c)], per_unit=40)
    at = label_places(k, row)
    forecast = Label(
        f"forecast {_dollars(row.forecast)}",
        *at["forecast"],
        names=f"forecast-{k}",
        color=MUTED,
        size=11,
    )
    # Beside a short bar the forecast's label sits last in the stack, so it
    # appears after the band's rather than alone, far below its dot.
    short = abs(c - f) <= LONG_BAR
    return [
        _dot(f"forecast-{k}", x - DOT_OFFSET, f, color=MUTED),
        *([] if short else [forecast]),
        _dot(f"close-{k}", x + DOT_OFFSET, c, color=INK),
        Label(f"close {_dollars(row.close)}", *at["close"], names=f"close-{k}", color=INK, size=11),
        _stroke(f"error-{k}", bar, color=LOST, width=2.6, frames=min(5, len(bar[0]) - 1)),
        Label(f"error {row.error:.2f}", *at["error"], names=f"error-{k}", color=LOST, size=11),
        _stroke(
            f"band-high-{k}",
            _line([(x - 0.12, high), (x + 0.12, high)], per_unit=25),
            color=ACCENT,
            width=1.0,
            frames=2,
        ),
        _stroke(
            f"band-low-{k}",
            _line([(x - 0.12, low), (x + 0.12, low)], per_unit=25),
            color=ACCENT,
            width=1.0,
            frames=2,
        ),
        Label(f"band ±{row.band:.6f}", *at["band"], names=f"band-low-{k}", color=ACCENT, size=11),
        *([forecast] if short else []),
        Label(f"row {k + 1}, {row.day}", x - 0.3, DATE_Y, names=f"error-{k}", color=MUTED, size=11),
    ]


def _zero_start(zero: ZeroStart) -> Scene:
    """Lesson 2: rows 1 and 2 forecast 0, so the error is the whole close."""
    one, two, _ = zero.rows
    side = "short" if zero.units < 0 else "long"
    steps: list[Stroke | Label] = _column(0, one) + [
        Label(
            f"{side} EWC alone, {one.slope:g} EWA shares",
            COLUMN_X[0] - 0.3,
            WORDS_Y[0],
            names="error-0",
            color=LOST if zero.units < 0 else GOOD,
            size=11,
        ),
    ]
    steps += _column(1, two) + [
        Label(
            f"slope {one.slope:g} → {two.slope:.6f},",
            COLUMN_X[1] - 0.3,
            WORDS_Y[0],
            names="error-1",
            color=INK,
            size=11,
        ),
        Label(
            "after the forecast", COLUMN_X[1] - 0.3, WORDS_Y[1], names="error-1", color=INK, size=11
        ),
        Label(
            f"{zero.first_return:+.2%} on {zero.first_return_day}",
            COLUMN_X[0] - 0.3,
            WORDS_Y[1],
            names="close-1",
            color=GOOD if zero.first_return > 0 else LOST,
            size=11,
        ),
    ]
    steps += _column(2, zero.rows[2]) + [
        Label("forecast uses", COLUMN_X[2] - 0.3, WORDS_Y[0], names="error-2", color=INK, size=11),
        Label(
            f"slope {two.slope:.6f}",
            COLUMN_X[2] - 0.3,
            WORDS_Y[1],
            names="error-2",
            color=INK,
            size=11,
        ),
    ]
    return Scene("Two rows on a forecast of 0", "zero_start", tuple(steps))


# --- Drawing ------------------------------------------------------------------

#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("one_day", "zero_start")
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


def scenes(day: OneDay | None = None, zero: ZeroStart | None = None) -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them, the filter's day's then Lesson 2's."""
    return (
        _one_day(day if day is not None else OneDay.from_run()),
        _zero_start(zero if zero is not None else ZeroStart.from_run()),
    )


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


def make_kalman_hedge_whiteboards(
    out_dir: Path | None = None, day: OneDay | None = None, zero: ZeroStart | None = None
) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes(day, zero)]


def main() -> None:
    for path in make_kalman_hedge_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
