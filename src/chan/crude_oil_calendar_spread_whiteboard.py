"""Whiteboard sketches for the crude oil calendar spread post: its schedule, and Lesson 2.

``blog/crude-oil-calendar-spread-lessons.md`` makes two claims a sentence has
to build in the reader's head: the script holds one pair of contracts at a
time and skips a pair whose last day would come too soon after its first, and the script sells the
spread where the roll return is high, which is mostly where the spread is
low. This module draws the two as scenes, and the post places each right after
the passage it draws.

1. One pair at a time, a year apart, in "The spread, the signal and the file",
   after a short lead-in that follows the paragraph ending "When γ
   rises, the spread falls." It draws item 6 of that section's list on
   Chan's file: a trading-day axis from December 2007 to November 2008 with a
   grey tick at each near contract's last priced day, the pair short K2008
   and long K2009 as a black bar with a bracket over the 10 days before
   K2008's last priced day, the three windows from 2008-04-09 that are too
   short crossed in red, and the pair short U2008 and long U2009 as a second
   black bar. A closing note gives the rule that skips the three: a later pair
   is held only when its last day comes at least 63 trading days after its
   first. The sketch is not schematic. Every date and count on it comes from
   :class:`Schedule`, which reads
   :func:`chan.calendar_spread_reversion.calendar_schedule` on the committed
   CL strip, and every mark sits on the axis at its own trading day.
2. High roll return, low spread, and the script sells, in Lesson 2, after the
   paragraph opening "The script does the opposite.": the roll return in
   brass over the held spread in black, each with its dashed 36-day average,
   a tint over a stretch where the roll return's z-score is above 0 and the
   spread sits below its own average, a red arrow where the script sells the
   spread and a green one where a bet on reversion would buy it, and the
   spread falling on through the tint. A closing note gives two counts.

The Lesson 2 sketch is schematic apart from its closing note. Its curves are
made up to show the shape of the relation, a rough and noisy inverse rather
than a mirror, so no height or date on it is a value of γ or of the spread.
Its two counts, the 841 of 1,097 held days on which the two z-scores have
opposite signs and the 554 held days with the roll return's z-score above 0,
all of them held short the far contract, come from :class:`Signs`, which reads
:func:`chan.calendar_spread_reversion.held_spread_zscore` and the script's
own positions on the committed CL strip. It names γ in words, as the roll
return, because the hand font draws γ like a y.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look, frame rate and colours.
Each sketch carries more than a reader takes in at that post's pace, so both
are in :data:`PACED`, and :func:`sketch_timeline` holds each of their labels
longer and their finished drawings for twelve seconds, as
:mod:`chan.equity_seasonals_whiteboard` does for its slow sketches. Each GIF
is named :data:`GIF_PREFIX` plus the scene's slug, a prefix chosen so no GIF
name starts like the post's chart, ``calendar_spread_reversion.png``.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw both with::

    uv run python -m chan.crude_oil_calendar_spread_whiteboard
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from chan.calendar_spread_reversion import (
    HOLDDAYS,
    NUM_DAYS_END,
    ROOT,
    START,
    calendar_schedule,
    held_log_spread,
    held_spread_zscore,
    run_spread,
)
from chan.matlab_helpers import fwdshift
from chan.paths import FIGURES_DIR
from chan.price_spread import zscore
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.roll_returns import load_strip, roll_returns
from chan.usdcad_tests_whiteboard import (
    TINT,
    Fill,
    Frame,
    Label,
    Scene,
    Stroke,
    _arrow,
    _box,
    _line,
    _span,
    _stroke,
    render,
    timeline,
)

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "crude_oil_calendar_spread_"
#: The width of the green edge drawn round every pale tint that carries
#: meaning, as :mod:`chan.equity_seasonals_whiteboard` draws it.
TINT_EDGE = 1.2


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``crude_oil_calendar_spread_schedule.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


def _contract(symbol: str) -> str:
    """A contract's short name, ``K2008`` for ``CL-2008K``."""
    return f"{symbol[-1]}{symbol[-5:-1]}"


def _day(date: str) -> str:
    """A date's month and day, ``04-22`` for ``2008-04-22``."""
    return date[5:]


def _month(date: str) -> str:
    """A date's month and year, ``Dec 2007`` for ``2007-12-03``."""
    return pd.Timestamp(date).strftime("%b %Y")


def _thousands(count: int) -> str:
    return f"{count:,}"


# --- The schedule: one pair at a time, a year apart ----------------------------

#: The near contract of the first pair the sketch draws, and the trading days
#: its axis spans.
FIRST_NEAR = "CL-2008K"
AXIS_FROM, AXIS_TO = "2007-12-01", "2008-11-30"


@dataclass(frozen=True)
class Window:
    """A pair's window: contract c short against c + 12 long, from ``first`` to ``last``.

    ``apart`` is how many trading days the last day comes after the first,
    and ``days`` how many trading days the window holds, both ends included,
    so one more. A held window is one the schedule holds. A skipped one is
    the window a pair would have had, from the day after the previous pair
    ended to :data:`~chan.calendar_spread_reversion.NUM_DAYS_END` days before
    its near contract's last priced day.
    """

    near: str
    far: str
    first: str
    last: str
    apart: int
    held: bool

    @property
    def days(self) -> int:
        return self.apart + 1


@dataclass(frozen=True)
class Schedule:
    """What the schedule sketch reads off the run.

    ``days`` are the axis's trading days, ``before`` and ``after`` the pair
    held first and the next pair held, ``skipped`` the pairs between them,
    and ``expiries`` each near contract's last priced day from ``before``'s
    to ``after``'s.
    """

    days: tuple[str, ...]
    before: Window
    skipped: tuple[Window, ...]
    after: Window
    expiries: tuple[tuple[str, str], ...]
    holddays: int = HOLDDAYS
    days_to_expiry: int = NUM_DAYS_END

    @classmethod
    def from_run(cls, data_dir: Path | None = None) -> Schedule:
        """Read the schedule the script runs on the committed CL strip.

        It refuses unless every skipped window is shorter than the rule allows
        and the next held one is not, each held pair ends
        :data:`~chan.calendar_spread_reversion.NUM_DAYS_END` days before its
        near contract's last priced day, and the next starts the day after,
        since the sketch's words say each.
        """
        contracts = load_strip(ROOT, data_dir).contracts
        return cls.from_contracts(contracts)

    @classmethod
    def from_contracts(cls, contracts: pd.DataFrame) -> Schedule:
        schedule = calendar_schedule(contracts).to_numpy()
        prices = contracts.to_numpy(dtype=float)
        expired = np.isfinite(prices) & ~np.isfinite(fwdshift(1, prices))
        index, columns = contracts.index, list(contracts.columns)

        def iso(row: int) -> str:
            return str(index[row].date())

        def last_priced(column: int) -> int:
            return int(np.flatnonzero(expired[:, column])[-1])

        def held(column: int) -> Window:
            rows = np.flatnonzero(schedule[:, column] == -1)
            (far,) = np.flatnonzero(schedule[rows[0]] == 1)
            return Window(
                columns[column],
                columns[int(far)],
                iso(int(rows[0])),
                iso(int(rows[-1])),
                int(rows[-1] - rows[0]),
                held=True,
            )

        first = columns.index(FIRST_NEAR)
        held_columns = [c for c in range(len(columns)) if (schedule[:, c] == -1).any()]
        following = held_columns[held_columns.index(first) + 1]
        before, after = held(first), held(following)
        start = index.get_loc(pd.Timestamp(before.last)) + 1
        skipped = tuple(
            Window(
                columns[c],
                columns[c + 12],
                iso(start),
                iso(last_priced(c) - NUM_DAYS_END),
                last_priced(c) - NUM_DAYS_END - start,
                held=False,
            )
            for c in range(first + 1, following)
        )
        for near, window in ((first, before), (following, after)):
            if index.get_loc(pd.Timestamp(window.last)) != last_priced(near) - NUM_DAYS_END:
                raise ValueError(f"{window.near}'s pair does not end {NUM_DAYS_END} days early")
        if index.get_loc(pd.Timestamp(after.first)) != start:
            raise ValueError(f"{after.near}'s pair does not start the day after the last ended")
        if not all(w.apart < HOLDDAYS for w in skipped) or after.apart < HOLDDAYS:
            raise ValueError("the skipped windows are not exactly the ones under the rule's length")
        axis = index[(index >= AXIS_FROM) & (index <= AXIS_TO)]
        return cls(
            days=tuple(str(d.date()) for d in axis),
            before=before,
            skipped=skipped,
            after=after,
            expiries=tuple(
                (columns[c][-1], iso(last_priced(c))) for c in range(first, following + 1)
            ),
        )


#: The axis's height and ends, the heights of the rows above it, and how far
#: each expiry's tick reaches below the axis.
AXIS_Y, AXIS_X0, AXIS_X1 = 0.95, 0.4, 9.6
BEFORE_Y, AFTER_Y = 3.4, 1.65
SKIPPED_Y = (2.95, 2.57, 2.19)
TICK = 0.12
#: How far a cross reaches from its middle.
CROSS = 0.1


def day_x(run: Schedule, date: str) -> float:
    """A trading day's place on the axis, an affine function of its count from the first."""
    return AXIS_X0 + (AXIS_X1 - AXIS_X0) * run.days.index(date) / (len(run.days) - 1)


def _cross(x: float, y: float) -> tuple:
    """An X centred on (x, y), drawn as one stroke."""
    return _line(
        [
            (x - CROSS, y - CROSS),
            (x + CROSS, y + CROSS),
            (x, y),
            (x - CROSS, y + CROSS),
            (x + CROSS, y - CROSS),
        ],
        per_unit=12,
    )


def _schedule(run: Schedule) -> Scene:
    """Item 6: the first pair, the skipped windows after it, and the next pair held."""
    before, after = run.before, run.after
    b0, b1 = day_x(run, before.first), day_x(run, before.last)
    a0, a1 = day_x(run, after.first), day_x(run, after.last)
    expiry = day_x(run, dict(run.expiries)[before.near[-1]])
    steps: list[Stroke | Fill | Label] = [
        _stroke("axis", _line([(AXIS_X0, AXIS_Y), (AXIS_X1, AXIS_Y)]), color=MUTED, frames=8),
        Label(_month(run.days[0]), AXIS_X0, AXIS_Y - 0.4, names="axis", color=MUTED, size=11),
        Label(
            _month(run.days[-1]),
            AXIS_X1,
            AXIS_Y - 0.4,
            names="axis",
            color=MUTED,
            size=11,
            ha="right",
        ),
    ]
    for letter, date in run.expiries:
        x = day_x(run, date)
        steps += [
            _stroke(
                f"expiry-{letter}",
                _line([(x, AXIS_Y), (x, AXIS_Y - TICK)], per_unit=20),
                color=MUTED,
                width=1.6,
                frames=2,
            ),
            Label(
                letter,
                x,
                AXIS_Y + 0.3,
                names=f"expiry-{letter}",
                color=MUTED,
                size=11,
                ha="center",
            ),
            Label(
                _day(date),
                x,
                AXIS_Y - 0.4,
                names=f"expiry-{letter}",
                color=MUTED,
                size=10,
                ha="center",
            ),
        ]
    steps += [
        _stroke("before", _span(b0, b1, BEFORE_Y), color=INK, width=3.0, frames=8),
        Label(
            f"short {_contract(before.near)}, long {_contract(before.far)}: "
            f"{_day(before.first)} to {_day(before.last)}, {before.days} days",
            b0,
            BEFORE_Y + 0.47,
            names="before",
            color=INK,
            size=12,
        ),
        _stroke(
            "days-to-expiry",
            _span(b1, expiry, BEFORE_Y, tick=0.08),
            color=MUTED,
            width=1.6,
            frames=4,
        ),
        Label(
            f"{run.days_to_expiry} days to {_contract(before.near)}’s last priced day",
            expiry + 0.17,
            BEFORE_Y,
            names="days-to-expiry",
            color=MUTED,
            size=11,
        ),
    ]
    if not 0 < len(run.skipped) <= len(SKIPPED_Y):
        raise ValueError(f"the sketch has rows for 1 to {len(SKIPPED_Y)} skipped windows")
    rows = SKIPPED_Y[: len(run.skipped)]
    for k, (window, y) in enumerate(zip(run.skipped, rows, strict=True)):
        x0, x1 = day_x(run, window.first), day_x(run, window.last)
        steps += [
            _stroke(f"skipped-{k}", _span(x0, x1, y, tick=0.08), color=LOST, width=2.0, frames=5),
            _stroke(f"cross-{k}", _cross((x0 + x1) / 2, y), color=LOST, width=2.0, frames=3),
            Label(
                f"{_contract(window.near)} to {_day(window.last)}: {window.apart} days apart",
                x1 + 0.24,
                y,
                names=f"cross-{k}",
                color=LOST,
                size=11,
            ),
        ]
    steps += [
        Label(
            "skipped, too short",
            a0 - 0.25,
            float(np.mean(rows)),
            names=f"cross-{len(run.skipped) - 1}",
            color=LOST,
            size=12,
            ha="right",
        ),
        _stroke("after", _span(a0, a1, AFTER_Y), color=INK, width=3.0, frames=8),
        Label(
            f"short {_contract(after.near)}, long {_contract(after.far)}",
            a0 - 0.25,
            AFTER_Y,
            names="after",
            color=INK,
            size=12,
            ha="right",
        ),
        Label(
            f"{_day(after.first)} to {_day(after.last)}, {after.days} days",
            a1 + 0.2,
            AFTER_Y,
            names="after",
            color=INK,
            size=12,
        ),
        Label(
            f"a later pair is held only when its last day comes at least {run.holddays} "
            "trading days after its first",
            0.3,
            0.2,
            names="after",
            color=MUTED,
            size=11,
        ),
    ]
    return Scene("One pair at a time, a year apart", "schedule", tuple(steps))


# --- Lesson 2: high roll return, low spread, and the script sells ---------------


@dataclass(frozen=True)
class Signs:
    """The counts the Lesson 2 sketch prints, read off the run from :data:`START`.

    ``held`` is the window's held days, ``opposite`` those on which the held
    pair's own 36-day z-score has the opposite sign to the roll return's,
    ``high`` those with the roll return's z-score above 0, and ``short_far``
    those of ``high`` on which the script holds the far contract short.
    """

    held: int
    opposite: int
    high: int
    short_far: int
    start: str = str(START.date())

    @classmethod
    def from_run(cls, data_dir: Path | None = None) -> Signs:
        """Run the script on the committed CL strip and count its held days."""
        contracts = load_strip(ROOT, data_dir).contracts
        gamma = roll_returns(contracts)
        run = run_spread(contracts, gamma, start=START)
        schedule = calendar_schedule(contracts)
        filled = gamma.ffill()
        spread = held_log_spread(contracts, schedule)
        held = (spread.notna() & filled.notna()).to_numpy() & (contracts.index >= START)
        own = held_spread_zscore(contracts, schedule, run.lookback).to_numpy()[held]
        of_gamma = zscore(filled.to_numpy(), run.lookback)[held]
        far = (run.positions.to_numpy() * (schedule.to_numpy() == 1)).sum(axis=1)[held]
        high = of_gamma > 0
        return cls(
            held=int(held.sum()),
            opposite=int((np.sign(own) != np.sign(of_gamma)).sum()),
            high=int(high.sum()),
            short_far=int((far[high] == -1).sum()),
        )

    @property
    def all_short(self) -> bool:
        return self.short_far == self.high


#: The curves' ends, the bands each runs in, and the height of the day axis.
CURVE_X0, CURVE_X1 = 0.4, 5.9
GAMMA_BAND, SPREAD_BAND = (2.9, 3.62), (1.35, 2.3)
DAYS_Y = 1.08
#: The made-up curves' samples, how many lead in before the first drawn one
#: so the first average has a full window, and that window.
SAMPLES, LEAD, WINDOW = 120, 24, 24
#: Where the tint starts and the green arrow points, as fractions of the drawn
#: span. The red arrow points at the spread a little to the green one's left.
TINT_FROM, SPOT = 0.55, 0.66
#: The tint's top and bottom.
TINT_Y0, TINT_Y1 = 1.22, 3.85


def shapes() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """The made-up roll return and spread, their trailing averages, and the drawn t.

    The roll return wanders and then climbs, and the spread is minus the roll
    return plus noise of its own, so it mostly falls when the roll return
    rises and sometimes does not. Each average is the mean of the last
    :data:`WINDOW` samples, a stand-in for the 36-day average.
    """
    t = np.arange(-LEAD, SAMPLES) / (SAMPLES - 1)
    gamma = (
        0.12 * np.sin(2 * np.pi * 1.7 * t + 1.2)
        + 2.0 * np.clip(t - 0.42, 0, None) ** 1.2
        + 0.03 * np.sin(2 * np.pi * 5.3 * t)
    )
    spread = (
        -gamma + 0.08 * np.sin(2 * np.pi * 2.6 * t + 0.4) + 0.035 * np.sin(2 * np.pi * 6.7 * t + 1)
    )

    def trailing(v: np.ndarray) -> np.ndarray:
        return np.convolve(v, np.ones(WINDOW) / WINDOW, mode="full")[: len(v)]

    keep = slice(LEAD, None)
    return t[keep], gamma[keep], trailing(gamma)[keep], spread[keep], trailing(spread)[keep]


def tint_start() -> int:
    """The first sample at or after :data:`TINT_FROM`, where the tint starts.

    It refuses unless the roll return sits above its average and the spread
    below its own on every sample from there to the end, since the tint and
    its label say both.
    """
    t, gamma, gamma_avg, spread, spread_avg = shapes()
    start = int(np.flatnonzero(t >= TINT_FROM)[0])
    if not ((gamma > gamma_avg) & (spread < spread_avg))[start:].all():
        raise ValueError(
            "the made-up roll return is not above its average, with the spread below its "
            "own, on every sample of the tint"
        )
    return start


def _to_band(values: np.ndarray, together: np.ndarray, band: tuple[float, float]) -> np.ndarray:
    lo, hi = float(together.min()), float(together.max())
    return band[0] + (band[1] - band[0]) * (values - lo) / (hi - lo)


def board_curves() -> tuple[np.ndarray, ...]:
    """The made-up curves on the board: x, the roll return and its average, the spread and its."""
    t, gamma, gamma_avg, spread, spread_avg = shapes()
    x = CURVE_X0 + (CURVE_X1 - CURVE_X0) * t
    both_g, both_s = np.concatenate([gamma, gamma_avg]), np.concatenate([spread, spread_avg])
    return (
        x,
        _to_band(gamma, both_g, GAMMA_BAND),
        _to_band(gamma_avg, both_g, GAMMA_BAND),
        _to_band(spread, both_s, SPREAD_BAND),
        _to_band(spread_avg, both_s, SPREAD_BAND),
    )


def _script_sells(signs: Signs) -> Scene:
    """Lesson 2: high roll return, low spread, the script sells and reversion would buy."""
    if not signs.all_short:
        raise ValueError(
            f"the far leg is short on {signs.short_far} of the {signs.high} days with the "
            "roll return's z-score above 0, not on all of them"
        )
    x, gy, gay, sy, say = board_curves()
    tint_x0 = float(x[tint_start()])
    spot = int(np.argmin(np.abs(x - (CURVE_X0 + (CURVE_X1 - CURVE_X0) * SPOT))))
    sx, s_y = float(x[spot]), float(sy[spot])
    red = int(np.argmin(np.abs(x - (sx - 0.22))))
    rx, r_y = float(x[red]), float(sy[red])
    right = CURVE_X1 + 0.3
    steps: list[Stroke | Fill | Label] = [
        _stroke("days", _line([(CURVE_X0, DAYS_Y), (CURVE_X1, DAYS_Y)]), color=MUTED, frames=6),
        Label("trading days", right, DAYS_Y, names="days", color=MUTED, size=11),
        Stroke("gamma", x, gy, color=ACCENT, width=2.6, frames=10),
        Label("roll return", CURVE_X0, 3.62, names="gamma", color=ACCENT, size=12),
        Stroke("gamma-average", x, gay, color=ACCENT, width=1.5, dashed=True, frames=8),
        Stroke("spread", x, sy, color=INK, width=2.6, frames=10),
        Label("held spread", CURVE_X0, 2.62, names="spread", color=INK, size=12),
        Stroke("spread-average", x, say, color=INK, width=1.5, dashed=True, frames=8),
        Label(
            "dashed: 36-day averages",
            CURVE_X0,
            1.42,
            names="spread-average",
            color=MUTED,
            size=11,
        ),
        Fill("high", tint_x0, TINT_Y0, CURVE_X1, TINT_Y1, TINT),
        _stroke(
            "high-edge",
            _box(tint_x0, TINT_Y0, CURVE_X1, TINT_Y1),
            color=GOOD,
            width=TINT_EDGE,
            frames=4,
        ),
        Label(
            "roll return’s z-score above 0",
            right,
            3.7,
            names="high-edge",
            color=MUTED,
            size=11,
        ),
        _stroke("sell", _arrow(right - 0.22, 2.98, rx, r_y + 0.07), color=LOST, frames=6),
        Label("script: sell the spread,", right, 3.15, names="sell", color=LOST, size=12),
        Label("short far and long near", right, 2.8, names="sell", color=LOST, size=12),
        _stroke("buy", _arrow(right - 0.22, 2.3, sx + 0.16, s_y + 0.02), color=GOOD, frames=6),
        Label("reversion would buy it here", right, 2.3, names="buy", color=GOOD, size=12),
        Label("the bet pays if the", right, 1.86, names="spread", color=INK, size=12),
        Label("spread keeps falling", right, 1.52, names="spread", color=INK, size=12),
        Label(
            f"the two z-scores have opposite signs on {_thousands(signs.opposite)} "
            f"of {_thousands(signs.held)} held days from {signs.start}",
            0.3,
            0.62,
            names="days",
            color=MUTED,
            size=11,
        ),
        Label(
            f"short far on all {_thousands(signs.high)} held days with the roll return’s "
            "z-score above 0",
            0.3,
            0.27,
            names="days",
            color=MUTED,
            size=11,
        ),
    ]
    return Scene("High roll return, low spread, and the script sells", "script_sells", tuple(steps))


# --- Drawing ------------------------------------------------------------------

#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("schedule", "script_sells")
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


def scenes(schedule: Schedule | None = None, signs: Signs | None = None) -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them, the schedule's then Lesson 2's."""
    return (
        _schedule(schedule if schedule is not None else Schedule.from_run()),
        _script_sells(signs if signs is not None else Signs.from_run()),
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


def make_crude_oil_calendar_spread_whiteboards(out_dir: Path | None = None) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes()]


def main() -> None:
    for path in make_crude_oil_calendar_spread_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
