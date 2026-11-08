"""Whiteboard sketches for the roll-return momentum post, one for Lesson 2 and one for Lesson 3.

``blog/roll-momentum-lessons.md`` makes two claims a sentence has to build in
the reader's head: the declared rule earns about what holding TU earns while
swinging less, because the days it sits out went nowhere, and the rebuilt
front contract and Chan's continuous close switch contracts one trading day
apart, which is where every change that differs between them by more than
rounding falls. This
module draws the two as scenes, and the post places each right after the text
it draws.

1. Nearly the same return, less swing, in Lesson 2, after the paragraph opening "What
   differs is the risk." A brown row of TU's daily returns as ticks, for
   Example 6.1's rule holding TU every day, and below it the same row in
   green with grey stretches where the ticks flatten to zero, for the
   declared rule flat on 341 days. Grey brackets under the flat stretches
   give TU's compounded return on those days, −0.001244, and green brackets
   under the rest give the 572 long days' 0.050629. Two fractions close it,
   each rule's average annual return over its annual volatility: 0.013661 /
   0.007575 = 1.80 for the declared rule and 0.013351 / 0.011156 = 1.20 for
   Example 6.1's.
2. Chan's continuous close switches a day early, in Lesson 3, after
   the two-item list whose first item opens "The returns agree." On a
   trading-day axis from 9 trading days before the March 2012 contract's last
   price to that last price, grey lines for the March and June contracts, a
   thick black rebuild on March through 2012-03-21 and on June from
   2012-03-22, and a brown line for Chan's continuous close between them. A
   dashed grey guide ties its 2012-03-20 point to March, as March's close
   less 0.1407, and another ties its 2012-03-21 point to June, whose close it
   equals there. Its change on 2012-03-21, +0.0625, matches neither March's
   own +0.0547 nor June's own +0.0546. A closing note gives the 30 of 1,999
   changes that differ beyond rounding, all at 7 trading days to a last price.

The first sketch is schematic in its ticks and figured in its words. The tick
heights and the number and places of the stretches are made up, though the
share of ticks drawn flat is the nearest :data:`TICKS` allow to the share of
window days the rule sits flat, and every number it prints is read from the
run. The second is not schematic in its
days or its numbers: each mark sits at its own trading day on the axis, and
every date, price change and count is read from the run. Its rows are not
prices to scale. They say which contract each series reads, since to scale
the shifted close would sit within 0.008 of June's on 2012-03-20.

Every figure comes from :class:`Swing` and :class:`Switch`, which read
:func:`chan.roll_returns.load_strip` on the committed TU strip and
:func:`chan.tu_momentum.read_sources` for the 2012-05-11 save, through
:func:`chan.roll_momentum.roll_momentum`, :func:`chan.roll_momentum.held_contracts`
and :func:`chan.roll_momentum.check_against_save`. So the scale-break guard
runs here as it does in the replication.

The drawing machinery is :mod:`ithildincore.whiteboard`'s, the machinery every
post's sketches share, so these GIFs share their look and frame rate. They draw
in the shared colours of :mod:`chan.regime_figure`, as the post's chart does,
and keep its meanings: brown for Example 6.1's rule and green for the
declared rule. In the second sketch brown marks Chan's continuous close, the
series Example 6.1 trades and the one the sketch points at. Each sketch
carries more than a reader takes in at that post's pace, so both are in
:data:`PACED`, and :func:`sketch_timeline` holds each of their labels longer
and their finished drawings for twelve seconds, as
:mod:`chan.equity_seasonals_whiteboard` does for its slow sketches. Each GIF
is named :data:`GIF_PREFIX` plus the scene's slug, a prefix chosen so no GIF
name starts like the post's chart, ``roll_momentum.png``.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw both with::

    uv run python -m chan.roll_momentum_whiteboard
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

# Re-exported, because each post's tests read the pace from its module.
from ithildincore.whiteboard import PACED_HOLD_MS as PACED_HOLD_MS
from ithildincore.whiteboard import PACED_LABEL_MS as PACED_LABEL_MS
from ithildincore.whiteboard import (
    Frame,
    Label,
    Scene,
    Stroke,
    paced_timeline,
    timeline,
    write_gif,
)
from ithildincore.whiteboard import line as _line
from ithildincore.whiteboard import span as _span
from ithildincore.whiteboard import stroke as _stroke

from chan import roll_momentum as run
from chan.matlab_helpers import backshift
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, MUTED
from chan.roll_returns import MONTH_LETTERS, load_strip
from chan.tu_momentum import HOLD_DAYS, read_sources
from chan.usdcad_tests_whiteboard import _signed

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "roll_momentum_sketch_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``roll_momentum_sketch_less_swing.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


def _day(date: str) -> str:
    """A date's month and day, ``03-21`` for ``2012-03-21``."""
    return date[5:]


def _delivery(symbol: str) -> str:
    """A contract's delivery month, ``March 2012`` for ``TU-2012H``."""
    month = MONTH_LETTERS.index(symbol[-1]) + 1
    return pd.Timestamp(year=int(symbol[-5:-1]), month=month, day=1).strftime("%B %Y")


def _change(value: float) -> str:
    """A price change to the files' four decimals, signed, as ``+0.0625``."""
    return ("+" if value >= 0 else "") + _signed(value, 4)


# --- Lesson 2: nearly the same return, less swing -----------------------------


@dataclass(frozen=True)
class Swing:
    """What the Lesson 2 sketch reads off the run, over the window's rows.

    ``flat_days`` and ``long_days`` count the rows the declared rule earns
    flat and long on, and ``flat_return`` and ``long_return`` compound the
    rebuilt series' return over each. Each rule's average annual return,
    annual volatility and Sharpe ratio are :class:`chan.tu_momentum.Figures`'
    own, so the volatility is a population standard deviation scaled by √252.
    """

    flat_days: int
    long_days: int
    flat_return: float
    long_return: float
    declared_average: float
    declared_volatility: float
    declared_sharpe: float
    example_average: float
    example_volatility: float
    example_sharpe: float

    @classmethod
    def from_run(cls, data_dir: Path | None = None) -> Swing:
        return cls.from_result(run.roll_momentum(load_strip(run.ROOT, data_dir)))

    @classmethod
    def from_result(cls, result: run.RollMomentum) -> Swing:
        """Read the counts and figures from one run of both rules.

        It refuses unless Example 6.1's rule holds every tranche long on every
        window row and the declared rule is never short, since the sketch's
        words say both.
        """
        tranches = backshift(1, result.example_positions)[result.window]
        if not np.all(tranches == HOLD_DAYS):
            raise ValueError("Example 6.1's rule is not fully long on every window row")
        held = result.held_position
        if np.any(held < 0):
            raise ValueError("the declared rule is short on some window row")
        market = result.market[result.window]
        flat = held == 0
        declared, example = result.figures, result.example_figures
        return cls(
            flat_days=int(flat.sum()),
            long_days=int((~flat).sum()),
            flat_return=float(np.prod(1 + market[flat]) - 1),
            long_return=float(np.prod(1 + market[~flat]) - 1),
            declared_average=declared.average_annual_return,
            declared_volatility=declared.annual_volatility,
            declared_sharpe=declared.sharpe,
            example_average=example.average_annual_return,
            example_volatility=example.annual_volatility,
            example_sharpe=example.sharpe,
        )

    @property
    def days(self) -> int:
        return self.flat_days + self.long_days


#: How many ticks each row draws, and how far across they run.
TICKS = 48
ROW_X = (0.4, 5.95)
#: The heights of the brown row and the green row, and how far a tick reaches.
EXAMPLE_Y, DECLARED_Y, TICK_REACH = 3.5, 2.55, 0.26
#: The heights of the grey brackets under the flat stretches and the green ones
#: under the long stretches, and where the words beside the rows start across.
FLAT_BRACKET_Y, LONG_BRACKET_Y, WORDS_X = 1.95, 1.5, 6.25
#: How far each bracket stops short of its stretch's ends.
BRACKET_GAP = 0.05
#: The heights of the fractions' caption and the two fractions.
CAPTION_Y, DECLARED_FRACTION_Y, EXAMPLE_FRACTION_Y = 1.0, 0.64, 0.3
#: How many stretches of each kind the green row draws, flat first, as the
#: window opens flat. Their places are schematic.
STRETCHES = 3


def flat_ticks(swing: Swing) -> int:
    """How many of :data:`TICKS` are drawn flat, the flat days' share of the window."""
    return round(TICKS * swing.flat_days / swing.days)


def tick_heights() -> np.ndarray:
    """The schematic daily returns, one tick each, deterministic and within the reach."""
    k = np.arange(TICKS)
    shape = np.sin(1.7 * k + 0.4) * (0.55 + 0.45 * np.abs(np.sin(0.63 * k + 1.1)))
    return TICK_REACH * shape


def tick_x(k: int) -> float:
    """The board across of tick ``k``, each in the middle of its own slot."""
    return ROW_X[0] + (k + 0.5) * (ROW_X[1] - ROW_X[0]) / TICKS


def slot_edges(k: int) -> tuple[float, float]:
    """The left and right edge of tick ``k``'s slot."""
    width = (ROW_X[1] - ROW_X[0]) / TICKS
    return ROW_X[0] + k * width, ROW_X[0] + (k + 1) * width


def stretches(swing: Swing) -> list[tuple[str, int, int]]:
    """The green row's stretches as ``(kind, first tick, end tick)``, flat first, alternating."""
    flat = np.array_split(np.arange(flat_ticks(swing)), STRETCHES)
    long = np.array_split(np.arange(TICKS - flat_ticks(swing)), STRETCHES)
    found, at = [], 0
    for kind, sizes in zip(
        ("flat", "long") * STRETCHES,
        [x for p in zip(flat, long, strict=True) for x in p],
        strict=True,
    ):
        found.append((kind, at, at + len(sizes)))
        at += len(sizes)
    return found


def _ticks(first: int, end: int, y: float, heights: np.ndarray) -> tuple:
    """The ticks from ``first`` up to ``end``, joined along the baseline from slot edge to edge."""
    points = [(slot_edges(first)[0], y)]
    for k in range(first, end):
        x = tick_x(k)
        points += [(x, y), (x, y + heights[k]), (x, y)]
    points.append((slot_edges(end - 1)[1], y))
    return _line(points, per_unit=10)


def _less_swing(swing: Swing) -> Scene:
    """Lesson 2: the declared rule is holding TU with its flat days taken out."""
    heights = tick_heights()
    steps: list[Stroke | Label] = [
        _stroke("example", _ticks(0, TICKS, EXAMPLE_Y, heights), color=ACCENT, frames=12),
        Label(
            "Example 6.1’s rule", WORDS_X, EXAMPLE_Y + 0.17, names="example", color=ACCENT, size=12
        ),
        Label(
            "holds TU every day", WORDS_X, EXAMPLE_Y - 0.19, names="example", color=ACCENT, size=12
        ),
    ]
    parts = stretches(swing)
    for n, (kind, first, end) in enumerate(parts):
        if kind == "flat":
            left, right = slot_edges(first)[0], slot_edges(end - 1)[1]
            xy = _line([(left, DECLARED_Y), (right, DECLARED_Y)], per_unit=10)
            steps.append(_stroke(f"flat-{n // 2 + 1}", xy, color=MUTED, width=3.0, frames=4))
        else:
            xy = _ticks(first, end, DECLARED_Y, heights)
            steps.append(_stroke(f"long-{n // 2 + 1}", xy, color=GOOD, frames=4))
    steps += [
        Label("the declared rule", WORDS_X, DECLARED_Y + 0.17, names="long-1", color=GOOD, size=12),
        Label(
            f"flat on {swing.flat_days:,} days",
            WORDS_X,
            DECLARED_Y - 0.19,
            names=f"flat-{STRETCHES}",
            color=MUTED,
            size=12,
        ),
    ]
    for kind, y, color in (("flat", FLAT_BRACKET_Y, MUTED), ("long", LONG_BRACKET_Y, GOOD)):
        n = 0
        for part, first, end in parts:
            if part != kind:
                continue
            n += 1
            left, right = slot_edges(first)[0], slot_edges(end - 1)[1]
            xy = _span(left + BRACKET_GAP, right - BRACKET_GAP, y, tick=0.1)
            steps.append(_stroke(f"{kind}-bracket-{n}", xy, color=color, width=1.8, frames=3))
        days = swing.flat_days if kind == "flat" else swing.long_days
        value = swing.flat_return if kind == "flat" else swing.long_return
        steps.append(
            Label(
                f"TU on {days:,} {kind} days: {_signed(value, 6)}",
                WORDS_X,
                y,
                names=f"{kind}-bracket-{n}",
                color=color,
                size=11,
            )
        )
    steps += [
        Label(
            "average annual return / annual volatility",
            ROW_X[0],
            CAPTION_Y,
            names="long-bracket-1",
            color=MUTED,
            size=12,
        ),
        Label(
            f"declared: {swing.declared_average:.6f} / {swing.declared_volatility:.6f} = "
            f"{swing.declared_sharpe:.2f}",
            ROW_X[0],
            DECLARED_FRACTION_Y,
            names="long-1",
            color=GOOD,
            size=12,
        ),
        Label(
            f"Example 6.1: {swing.example_average:.6f} / {swing.example_volatility:.6f} = "
            f"{swing.example_sharpe:.2f}",
            ROW_X[0],
            EXAMPLE_FRACTION_Y,
            names="example",
            color=ACCENT,
            size=12,
        ),
        Label(
            "nearly the same return,",
            9.6,
            DECLARED_FRACTION_Y,
            names="example",
            ha="right",
            size=12,
        ),
        Label("a smaller swing", 9.6, EXAMPLE_FRACTION_Y, names="example", ha="right", size=12),
    ]
    return Scene("Nearly the same return, less swing", "less_swing", tuple(steps))


# --- Lesson 3: Chan's continuous close switches a day early -------------------

#: The contract whose roll the sketch draws, the one the post names.
OLD = "TU-2012H"
#: How many trading days before the old contract's last price the axis starts.
AXIS_DAYS = 9


@dataclass(frozen=True)
class Switch:
    """What the Lesson 3 sketch reads off the run, around one roll.

    ``days`` are the axis's trading days on the strip's calendar, from
    :data:`AXIS_DAYS` before the old contract's last priced day, ``last``, to
    it. ``before``, ``switch`` and ``after`` are the 8th, 7th and 6th trading
    days before ``last``. ``rebuild_switch`` and ``rebuild_after`` name the
    contract the rebuild earns on ``switch`` and ``after``. ``shift`` is the
    old contract's close less the save's on ``before``, and ``save_change``,
    ``old_change`` and ``new_change`` are the save's and each contract's own
    change on ``switch``. The counts are :func:`chan.roll_momentum.check_against_save`'s.
    """

    old: str
    new: str
    days: tuple[str, ...]
    before: str
    switch: str
    after: str
    last: str
    rebuild_switch: str
    rebuild_after: str
    shift: float
    save_change: float
    old_change: float
    new_change: float
    changes: int
    differ: int
    on_roll_row: int

    @classmethod
    def from_run(cls, data_dir: Path | None = None) -> Switch:
        strip = load_strip(run.ROOT, data_dir)
        _, save = read_sources(data_dir)
        result = run.roll_momentum(strip)
        return cls.from_data(strip.contracts, save, run.check_against_save(strip, result, save))

    @classmethod
    def from_data(
        cls, contracts: pd.DataFrame, save: pd.Series, check: run.SaveCheck, old: str = OLD
    ) -> Switch:
        """Read the roll of ``old`` from the strip's contracts and the save's close.

        It refuses unless the rebuild earns ``old`` on the switch day and the
        next contract the day after, and unless the save equals that next
        contract's close on the switch day, since the sketch's words say each.
        """
        index = contracts.index
        last = int(np.flatnonzero(contracts[old].notna())[-1])
        held = run.held_contracts(contracts)
        roll = run.ROLL_ROWS
        before, switch, after = last - roll - 1, last - roll, last - roll + 1
        new = held.iloc[after]
        if held.iloc[switch] != old or new is None or new == old:
            raise ValueError(
                f"the rebuild does not roll from {old} between the switch day and after"
            )
        day = lambda row: index[row]  # noqa: E731
        if save[day(switch)] != contracts[new].iloc[switch]:
            raise ValueError(f"the save does not equal {new}'s close on {day(switch).date()}")
        return cls(
            old=old,
            new=str(new),
            days=tuple(str(d.date()) for d in index[last - AXIS_DAYS : last + 1]),
            before=str(day(before).date()),
            switch=str(day(switch).date()),
            after=str(day(after).date()),
            last=str(day(last).date()),
            rebuild_switch=str(held.iloc[switch]),
            rebuild_after=str(held.iloc[after]),
            shift=float(contracts[old].iloc[before] - save[day(before)]),
            save_change=float(save[day(switch)] - save[day(before)]),
            old_change=float(contracts[old].iloc[switch] - contracts[old].iloc[before]),
            new_change=float(contracts[new].iloc[switch] - contracts[new].iloc[before]),
            changes=check.changes,
            differ=check.beyond_rounding,
            on_roll_row=check.beyond_rounding_on_jump_row,
        )

    def before_last(self, date: str) -> int:
        """How many trading days ``date`` comes before the old contract's last price."""
        return self.days.index(self.last) - self.days.index(date)


#: The axis's height and ends, and the rows of the old contract, Chan's
#: continuous close and the new contract, top to bottom.
AXIS_Y, AXIS_X0, AXIS_X1 = 1.32, 3.25, 9.5
OLD_Y, SAVE_Y, NEW_Y = 3.58, 2.56, 1.88
#: The heights of the axis's dates, of the counts under them, and of the closing note.
DATES_Y, COUNTS_Y, CLOSING_Y = 1.02, 0.7, 0.3
#: Where each row's name starts across, and the widths of the contract lines,
#: the rebuild and the switching change, in points.
NAMES_X = 0.3
CONTRACT_WIDTH, REBUILD_WIDTH, SWITCH_WIDTH = 1.6, 4.5, 4.5
#: How far a guide stops short of the rows it joins.
GUIDE_GAP = 0.12
#: The heights of the two lines of words on the switching change.
SWITCH_WORDS_Y = (3.2, 2.88)


def switch_x(run_: Switch, date: str) -> float:
    """A trading day's place on the axis, an affine function of its count from the first."""
    return AXIS_X0 + (AXIS_X1 - AXIS_X0) * run_.days.index(date) / (len(run_.days) - 1)


def _switch_day(s: Switch) -> Scene:
    """Lesson 3: the rebuild switches a day after Chan's continuous close does."""
    x = lambda date: switch_x(s, date)  # noqa: E731
    first, last = x(s.days[0]), x(s.last)
    shown = (s.before, s.switch, s.after, s.last)
    axis = [(first, AXIS_Y)]
    for date in s.days:
        axis += [(x(date), AXIS_Y), (x(date), AXIS_Y + 0.08), (x(date), AXIS_Y)]
    old_month, new_month = _delivery(s.old), _delivery(s.new)
    old_name = old_month.split()[0]
    new_name = new_month.split()[0]
    steps: list[Stroke | Label] = [
        _stroke("axis", _line(axis, per_unit=6), color=MUTED, frames=8),
        *[
            Label(_day(date), x(date), DATES_Y, names="axis", color=MUTED, size=10, ha="center")
            for date in shown
        ],
        Label("days to last price", NAMES_X, COUNTS_Y, names="axis", color=MUTED, size=11),
        *[
            Label(
                str(s.before_last(date)),
                x(date),
                COUNTS_Y,
                names="axis",
                color=MUTED,
                size=11,
                ha="center",
            )
            for date in shown
        ],
        _stroke(
            "old",
            _line(
                [(first, OLD_Y), (last, OLD_Y), (last, OLD_Y + 0.1), (last, OLD_Y - 0.1)],
                per_unit=4,
            ),
            color=MUTED,
            width=CONTRACT_WIDTH,
            frames=8,
        ),
        Label(f"{old_month} contract", NAMES_X, OLD_Y, names="old", color=MUTED, size=11),
        _stroke(
            "new",
            _line([(first, NEW_Y), (last, NEW_Y)], per_unit=4),
            color=MUTED,
            width=CONTRACT_WIDTH,
            frames=8,
        ),
        Label(f"{new_month} contract", NAMES_X, NEW_Y, names="new", color=MUTED, size=11),
        _stroke(
            "rebuild-old",
            _line([(first, OLD_Y), (x(s.switch), OLD_Y)], per_unit=8),
            color=INK,
            width=REBUILD_WIDTH,
            frames=5,
        ),
        _stroke(
            "rebuild-new",
            _line([(x(s.after), NEW_Y), (last, NEW_Y)], per_unit=4),
            color=INK,
            width=REBUILD_WIDTH,
            frames=8,
        ),
        Label(
            f"rebuild: {old_name} through {_day(s.switch)}, {new_name} from {_day(s.after)}",
            last - 0.25,
            OLD_Y + 0.34,
            names="rebuild-new",
            color=INK,
            size=11,
            ha="right",
        ),
        _stroke(
            "save-before",
            _line([(first, SAVE_Y), (x(s.before), SAVE_Y)], per_unit=8),
            color=ACCENT,
            frames=4,
        ),
        Label(
            "Chan’s continuous close", NAMES_X, SAVE_Y, names="save-before", color=ACCENT, size=11
        ),
        _stroke(
            "guide-before",
            _line(
                [(x(s.before), SAVE_Y + GUIDE_GAP), (x(s.before), OLD_Y - GUIDE_GAP)], per_unit=10
            ),
            color=MUTED,
            dashed=True,
            width=1.5,
            frames=3,
        ),
        Label(
            f"{old_name}’s close less {s.shift:.4f}",
            x(s.before) - 0.2,
            (OLD_Y + SAVE_Y) / 2,
            names="guide-before",
            color=ACCENT,
            size=11,
            ha="right",
        ),
        _stroke(
            "save-switch",
            _line([(x(s.before), SAVE_Y), (x(s.switch), SAVE_Y)], per_unit=10),
            color=ACCENT,
            width=SWITCH_WIDTH,
            frames=4,
        ),
        _stroke(
            "guide-switch",
            _line(
                [(x(s.switch), SAVE_Y - GUIDE_GAP), (x(s.switch), NEW_Y + GUIDE_GAP)], per_unit=10
            ),
            color=MUTED,
            dashed=True,
            width=1.5,
            frames=3,
        ),
        Label(
            f"{_day(s.switch)}: switches to {new_name}’s close, {_change(s.save_change)}",
            x(s.switch) + 0.2,
            SWITCH_WORDS_Y[0],
            names="save-switch",
            color=ACCENT,
            size=11,
        ),
        Label(
            f"neither {old_name}’s {_change(s.old_change)} nor {new_name}’s "
            f"{_change(s.new_change)}",
            x(s.switch) + 0.2,
            SWITCH_WORDS_Y[1],
            names="save-switch",
            color=INK,
            size=11,
        ),
        _stroke(
            "save-after",
            _line([(x(s.switch), SAVE_Y), (last, SAVE_Y)], per_unit=4),
            color=ACCENT,
            frames=8,
        ),
        Label(
            f"{s.differ:,} of {s.changes:,} changes differ beyond rounding, all at "
            f"{run.ROLL_ROWS} days to last price"
            if s.on_roll_row == s.differ
            else f"{s.differ:,} of {s.changes:,} changes differ beyond rounding, "
            f"{s.on_roll_row:,} at {run.ROLL_ROWS} days to last price",
            NAMES_X,
            CLOSING_Y,
            names="save-after",
            color=INK,
            size=12,
        ),
    ]
    return Scene("Chan’s continuous close switches a day early", "switch_day", tuple(steps))


# --- Drawing ------------------------------------------------------------------

#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("less_swing", "switch_day")


def sketch_timeline(scene: Scene) -> list[Frame]:
    """:func:`timeline`'s frames, slowed for the scenes in :data:`PACED`."""
    return paced_timeline(scene) if scene.slug in PACED else timeline(scene)


def scenes(swing: Swing | None = None, switch: Switch | None = None) -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them, Lesson 2's then Lesson 3's."""
    return (
        _less_swing(swing if swing is not None else Swing.from_run()),
        _switch_day(switch if switch is not None else Switch.from_run()),
    )


def _write(scene: Scene, folder: Path) -> Path:
    frames = sketch_timeline(scene)
    path = write_gif(scene, frames, folder / gif_name(scene))
    return path


def make_roll_momentum_whiteboards(
    out_dir: Path | None = None, swing: Swing | None = None, switch: Switch | None = None
) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes(swing, switch)]


def main() -> None:
    for path in make_roll_momentum_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
