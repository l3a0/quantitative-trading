"""Whiteboard sketches for the VX calendar spread post, one for Lesson 2 and one for Lesson 4.

``blog/vx-calendar-spread-lessons.md`` makes two claims a sentence has to
build in the reader's head: the specification S holds one pair of contracts
while its signal reads whichever two contracts are nearest expiry, and the
script as shipped, pairing contracts 12 months apart, leaves the far leg
without a price. This module draws the two as scenes, and the post places each
right after the paragraph it draws.

1. One hold of S, in Lesson 2, after the paragraph opening "The script holds
   each pair for at least 63 days". A grey trading-day axis from February to
   May 2009 carries a tick at each front contract's last priced day, which the
   script takes as its expiry. A thick black bar is S's hold of the pair near
   VX-2009K and far VX-2009M, with a grey bracket over the 10 days from its
   end to VX-2009K's last priced day. Under the bar a row gives the near leg's
   place among the contracts priced that day, 4th, 3rd, 2nd and then front,
   and its last stretch is tinted and labelled as the stretch where the signal
   reads the pair S holds. Under that, the front pair the signal reads steps
   from VX-2009G and VX-2009H to VX-2009K and VX-2009M, each ending at its
   front contract's tick. The bar carries no side, because the script reverses
   both legs whenever the z-score is above 0.
2. Twelve months apart, in Lesson 4, after the paragraph opening "Run on VX
   with Chan’s 12-month spacing, its schedule holds a pair on 1,284 days". One day,
   2010-01-04: a box for each contract from VX-2010F to VX-2011J, inked for
   the 8 priced that day and dashed for the rest, the near leg VX-2010J
   circled, and an arrow 12 months on to the dashed VX-2011J box, which has no
   price. A closing note says the script adds up the legs that have a price,
   so on that day it holds VX-2010J alone, and counts the held days on which
   the near leg is alone.

Neither sketch is schematic. Every date, count and place on the first comes
from :class:`Hold`, which reads
:func:`chan.calendar_spread_reversion.calendar_schedule` with S's
``spread_month`` of 1 and :func:`chan.vx_calendar_spread.near_leg_rank` on
the committed VX strip, and every mark sits on the axis at its own trading
day. Every contract, place and count on the second comes from
:class:`Shipped`, which reads the same schedule with the shipped
``spread_month`` of 12.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look and frame rate. They draw
in the shared colours of :mod:`chan.regime_figure`, as the post's chart does.
Each sketch carries more than a reader takes in at that post's pace, so both
are in :data:`PACED`, and :func:`sketch_timeline` holds each of their labels
longer and their finished drawings for twelve seconds, as
:mod:`chan.equity_seasonals_whiteboard` does for its slow sketches. The one
exception is a box's one-letter label in the Lesson 4 sketch, which keeps the
usual pace so the 16 letters do not hold back the ring and arrow they lead to. Each GIF
is named :data:`GIF_PREFIX` plus the scene's slug, a prefix chosen so no GIF
name starts like the post's chart, ``vx_calendar_spread.png``.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw both with::

    uv run python -m chan.vx_calendar_spread_whiteboard
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from chan.calendar_spread_reversion import NUM_DAYS_END, calendar_schedule
from chan.calendar_spread_reversion import SPREAD_MONTH as SHIPPED_SPREAD_MONTH
from chan.matlab_helpers import fwdshift
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.roll_returns import MONTH_LETTERS, load_strip
from chan.usdcad_tests_whiteboard import (
    TINT,
    Fill,
    Frame,
    Label,
    Scene,
    Stroke,
    _box,
    _line,
    _span,
    _stroke,
    render,
    timeline,
)
from chan.vx_calendar_spread import ROOT, SPREAD_MONTH, near_leg_rank

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "vx_calendar_spread_sketch_"
#: The width of the green edge drawn round every pale tint that carries
#: meaning, as :mod:`chan.equity_seasonals_whiteboard` draws it.
TINT_EDGE = 1.2

_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
_WORDS = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
_PLACES = {1: "front", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th"}


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``vx_calendar_spread_sketch_one_hold.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


def _letter(symbol: str) -> str:
    """A contract's month letter, ``K`` for ``VX-2009K``."""
    return symbol[-1]


def _month(symbol: str) -> str:
    """A contract's month, ``May`` for ``VX-2009K``."""
    return _MONTHS[MONTH_LETTERS.index(_letter(symbol))]


def _day(date: str) -> str:
    """A date's month and day, ``05-06`` for ``2009-05-06``."""
    return date[5:]


def _last_priced(contracts: pd.DataFrame) -> dict[str, str]:
    """Each contract's last priced day, which the script takes as its expiry."""
    prices = contracts.to_numpy(dtype=float)
    expired = np.isfinite(prices) & ~np.isfinite(fwdshift(1, prices))
    return {
        name: str(contracts.index[int(np.flatnonzero(expired[:, c])[-1])].date())
        for c, name in enumerate(contracts.columns)
        if expired[:, c].any()
    }


# --- Lesson 2: one hold of S, and the front pair under it ----------------------

#: The near leg of the pair the sketch draws, and the trading days its axis spans.
NEAR = "VX-2009K"
AXIS_FROM, AXIS_TO = "2009-02-01", "2009-05-31"


@dataclass(frozen=True)
class Stretch:
    """Days of one hold on which the signal reads one front pair.

    ``first`` to ``last`` are the stretch's days, ``days`` how many, both ends
    included, and ``place`` the held pair's near leg's place among the
    contracts priced on them, 1 for the front. ``front`` and ``back`` are the
    two nearest priced contracts, whose ratio the signal reads, and
    ``front_ends`` is the front contract's last priced day.
    """

    first: str
    last: str
    days: int
    place: int
    front: str
    back: str
    front_ends: str


@dataclass(frozen=True)
class Hold:
    """What the Lesson 2 sketch reads off S's schedule.

    ``days`` are the axis's trading days, ``near`` and ``far`` the pair held
    from ``first`` to ``last`` on ``held`` days, ``expiry`` the near leg's
    last priced day, and ``stretches`` the hold split where the front pair
    the signal reads changes.
    """

    days: tuple[str, ...]
    near: str
    far: str
    first: str
    last: str
    held: int
    expiry: str
    stretches: tuple[Stretch, ...]
    days_to_expiry: int = NUM_DAYS_END

    @classmethod
    def from_run(cls, data_dir: Path | None = None) -> Hold:
        """Read S's schedule on the committed VX strip."""
        return cls.from_contracts(load_strip(ROOT, data_dir).contracts)

    @classmethod
    def from_contracts(cls, contracts: pd.DataFrame) -> Hold:
        """Read the hold of :data:`NEAR` and the stretches under it.

        It refuses unless the hold ends :data:`NUM_DAYS_END` days before the
        near leg's last priced day, every stretch but the last ends on its
        front contract's last priced day, each front pair is two adjacent
        contracts, and in the last stretch the front pair is the pair held,
        since the sketch's marks and words say each.
        """
        schedule = calendar_schedule(contracts, spread_month=SPREAD_MONTH)
        rank = near_leg_rank(contracts, schedule).to_numpy()
        priced = np.isfinite(contracts.to_numpy(dtype=float))
        index, columns = contracts.index, list(contracts.columns)
        last_priced = _last_priced(contracts)

        rows = np.flatnonzero(schedule[NEAR].to_numpy() == -1)
        (far,) = np.flatnonzero(schedule.iloc[rows[0]].to_numpy() == 1)
        expiry = index.get_loc(pd.Timestamp(last_priced[NEAR]))
        if expiry - rows[-1] != NUM_DAYS_END:
            raise ValueError(f"{NEAR}'s pair does not end {NUM_DAYS_END} days early")

        def front_pair(row: int) -> tuple[int, int]:
            front, back = np.flatnonzero(priced[row])[:2]
            return int(front), int(back)

        keys = [(int(rank[row]), front_pair(row)) for row in rows]
        stretches: list[Stretch] = []
        start = 0
        for k in range(1, len(rows) + 1):
            if k == len(rows) or keys[k] != keys[start]:
                place, (front, back) = keys[start]
                if back != front + 1:
                    raise ValueError(f"{columns[front]} and {columns[back]} are not adjacent")
                stretches.append(
                    Stretch(
                        str(index[rows[start]].date()),
                        str(index[rows[k - 1]].date()),
                        k - start,
                        place,
                        columns[front],
                        columns[back],
                        last_priced[columns[front]],
                    )
                )
                start = k
        for stretch in stretches[:-1]:
            if stretch.last != stretch.front_ends:
                raise ValueError(f"the stretch reading {stretch.front} ends before its tick")
        final = stretches[-1]
        if (final.front, final.back, final.place) != (NEAR, columns[int(far)], 1):
            raise ValueError("the last stretch does not read the pair held")
        axis = index[(index >= AXIS_FROM) & (index <= AXIS_TO)]
        return cls(
            days=tuple(str(d.date()) for d in axis),
            near=NEAR,
            far=columns[int(far)],
            first=str(index[rows[0]].date()),
            last=str(index[rows[-1]].date()),
            held=len(rows),
            expiry=last_priced[NEAR],
            stretches=tuple(stretches),
        )


#: The axis's height and ends, and the heights of the rows above it.
AXIS_Y, AXIS_X0, AXIS_X1 = 1.2, 2.2, 8.2
BAR_Y, PLACE_Y, FRONT_Y = 3.5, 2.72, 1.66
#: How far each expiry's tick reaches below the axis, and how far the tint
#: reaches above and below the near leg's row.
TICK, TINT_PAD = 0.12, 0.13


def day_x(hold: Hold, date: str) -> float:
    """A trading day's place on the axis, an affine function of its count from the first."""
    return AXIS_X0 + (AXIS_X1 - AXIS_X0) * hold.days.index(date) / (len(hold.days) - 1)


def _one_hold(hold: Hold) -> Scene:
    """Lesson 2: S holds one pair while the front pair its signal reads steps on."""
    if len(hold.stretches) >= len(_WORDS):
        raise ValueError(f"the title spells the count in words up to {_WORDS[-1]}")
    b0, b1 = day_x(hold, hold.first), day_x(hold, hold.last)
    k_x = day_x(hold, hold.expiry)
    head = AXIS_X0 - 0.2
    steps: list[Stroke | Fill | Label] = [
        _stroke("axis", _line([(AXIS_X0, AXIS_Y), (AXIS_X1, AXIS_Y)]), color=MUTED, frames=8),
    ]
    for stretch in hold.stretches:
        x = day_x(hold, stretch.front_ends)
        gid = f"expiry-{_letter(stretch.front)}"
        steps += [
            _stroke(
                gid,
                _line([(x, AXIS_Y), (x, AXIS_Y - TICK)], per_unit=20),
                color=MUTED,
                width=1.6,
                frames=2,
            ),
            Label(stretch.front, x, 0.8, names=gid, color=MUTED, size=10, ha="center"),
            Label(
                f"{_month(stretch.front)}, {_day(stretch.front_ends)}",
                x,
                0.51,
                names=gid,
                color=MUTED,
                size=10,
                ha="center",
            ),
        ]
    steps += [
        Label(
            "each tick: a contract’s last priced day, which the script takes as its expiry",
            0.3,
            0.2,
            names="axis",
            color=MUTED,
            size=10,
        ),
        _stroke("hold", _span(b0, b1, BAR_Y, tick=0.08), color=INK, width=3.0, frames=8),
        Label("S holds", head, BAR_Y, names="hold", color=INK, size=12, ha="right"),
        Label(
            f"near {hold.near}, far {hold.far}: {_day(hold.first)} to {_day(hold.last)}, "
            f"{hold.held} days",
            b0,
            3.88,
            names="hold",
            color=INK,
            size=11,
        ),
        _stroke(
            "days-to-expiry",
            _span(b1, k_x, BAR_Y, tick=0.08),
            color=MUTED,
            width=1.6,
            frames=4,
        ),
        Label(
            f"{hold.days_to_expiry} days to its",
            k_x + 0.17,
            3.55,
            names="days-to-expiry",
            color=MUTED,
            size=11,
        ),
        Label("last priced day", k_x + 0.17, 3.22, names="days-to-expiry", color=MUTED, size=11),
    ]
    final = len(hold.stretches) - 1
    for k, stretch in enumerate(hold.stretches):
        x0, x1 = day_x(hold, stretch.first), day_x(hold, stretch.last)
        gid = f"place-{k}"
        steps += [
            _stroke(gid, _span(x0, x1, PLACE_Y, tick=0.07), color=INK, width=1.6, frames=3),
            Label(
                _PLACES[stretch.place],
                (x0 + x1) / 2,
                3.15,
                names=gid,
                color=INK,
                size=11,
                ha="center",
            ),
        ]
        if k == 0:
            steps.append(
                Label("near leg’s place", head, PLACE_Y, names=gid, color=INK, size=11, ha="right")
            )
        if k < final:
            steps.append(
                Label(
                    f"{stretch.days} days",
                    (x0 + x1) / 2,
                    2.35,
                    names=gid,
                    color=INK,
                    size=10,
                    ha="center",
                )
            )
    last = hold.stretches[-1]
    t0, t1 = day_x(hold, last.first), day_x(hold, last.last)
    steps += [
        Fill("same", t0, PLACE_Y - TINT_PAD, t1, PLACE_Y + TINT_PAD, TINT),
        _stroke(
            "same-edge",
            _box(t0, PLACE_Y - TINT_PAD, t1, PLACE_Y + TINT_PAD),
            color=GOOD,
            width=TINT_EDGE,
            frames=4,
        ),
        Label(
            f"same pair: {last.days} days",
            t1 + 0.17,
            PLACE_Y,
            names="same-edge",
            color=GOOD,
            size=11,
        ),
    ]
    for k, stretch in enumerate(hold.stretches):
        x0, x1 = day_x(hold, stretch.first), day_x(hold, stretch.front_ends)
        gid = f"front-{k}"
        steps += [
            _stroke(gid, _span(x0, x1, FRONT_Y, tick=0.07), color=ACCENT, width=2.0, frames=3),
            Label(
                f"{_letter(stretch.front)} and {_letter(stretch.back)}",
                (x0 + x1) / 2,
                2.03,
                names=gid,
                color=ACCENT,
                size=10,
                ha="center",
            ),
        ]
        if k == 0:
            steps.append(
                Label("signal reads", head, FRONT_Y, names=gid, color=ACCENT, size=11, ha="right")
            )
    title = f"S holds one pair while its signal reads {_WORDS[len(hold.stretches)]}"
    return Scene(title, "one_hold", tuple(steps))


# --- Lesson 4: twelve months apart leaves one leg alone ------------------------

#: The day the Lesson 4 sketch draws.
DAY = "2010-01-04"


@dataclass(frozen=True)
class Shipped:
    """What the Lesson 4 sketch reads off the script as shipped.

    On :data:`DAY` the schedule holds ``near`` against ``far``,
    ``spread_month`` contracts on, and ``row`` runs from the front contract to
    ``far``, of which ``priced`` have a price that day. ``held`` counts the
    days the schedule holds a pair, ``both`` those with both legs priced,
    ``near_alone`` those with only the near leg priced, and ``neither`` those
    with no leg priced.
    """

    day: str
    row: tuple[str, ...]
    priced: tuple[str, ...]
    near: str
    far: str
    held: int
    both: int
    near_alone: int
    neither: int
    spread_month: int = SHIPPED_SPREAD_MONTH

    @classmethod
    def from_run(cls, data_dir: Path | None = None) -> Shipped:
        """Read the shipped schedule on the committed VX strip."""
        return cls.from_contracts(load_strip(ROOT, data_dir).contracts)

    @classmethod
    def from_contracts(cls, contracts: pd.DataFrame) -> Shipped:
        """Read the day and the counts.

        It refuses unless the priced contracts that day are the first ones in
        the row with no gap, the near leg is among them and the far leg is
        not, since the sketch draws each.
        """
        schedule = calendar_schedule(contracts).to_numpy()
        priced = np.isfinite(contracts.to_numpy(dtype=float))
        columns = list(contracts.columns)
        row = contracts.index.get_loc(pd.Timestamp(DAY))
        (near,) = np.flatnonzero(schedule[row] == -1)
        (far,) = np.flatnonzero(schedule[row] == 1)
        on = np.flatnonzero(priced[row])
        front = int(on[0])
        if not (on == np.arange(front, front + len(on))).all():
            raise ValueError(f"the contracts priced on {DAY} have a gap")
        if not priced[row, near] or priced[row, far]:
            raise ValueError(f"on {DAY} the near leg is not priced alone")
        held = (schedule != 0).any(axis=1)
        has_near = ((schedule == -1) & priced).any(axis=1)
        has_far = ((schedule == 1) & priced).any(axis=1)
        return cls(
            day=DAY,
            row=tuple(columns[front : int(far) + 1]),
            priced=tuple(columns[c] for c in on),
            near=columns[int(near)],
            far=columns[int(far)],
            held=int(held.sum()),
            both=int((held & has_near & has_far).sum()),
            near_alone=int((held & has_near & ~has_far).sum()),
            neither=int((held & ~has_near & ~has_far).sum()),
        )


#: The boxes' left edge, width and pitch, and their bottom and top.
BOX_X0, BOX_W, BOX_PITCH = 0.55, 0.52, 0.58
BOX_Y0, BOX_Y1 = 2.35, 2.95
#: The circle's half-width and half-height, the arc's peak, and the bracket's height.
RING_RX, RING_RY = 0.33, 0.5
ARC_PEAK, BRACKET_Y = 3.9, 1.5


def box_x(k: int) -> float:
    """The middle of the k-th box from the left, an affine function of k."""
    return BOX_X0 + k * BOX_PITCH + BOX_W / 2


def _ring(x: float, y: float) -> tuple:
    """An ellipse round (x, y), drawn from its top, clockwise, as one stroke."""
    t = np.linspace(0, 2 * np.pi, 49)
    return x + RING_RX * np.sin(t), y + RING_RY * np.cos(t)


def _arc_arrow(x0: float, y0: float, x1: float, y1: float) -> tuple:
    """A curve from (x0, y0) over :data:`ARC_PEAK` to (x1, y1), with a head at the end."""
    t = np.linspace(0, 1, 40)
    mid = 2 * ARC_PEAK - (y0 + y1) / 2
    x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * (x0 + x1) / 2 + t**2 * x1
    y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * mid + t**2 * y1
    angle, head = np.arctan2(y[-1] - y[-2], x[-1] - x[-2]), 0.2
    left = (x1 - head * np.cos(angle - 0.5), y1 - head * np.sin(angle - 0.5))
    right = (x1 - head * np.cos(angle + 0.5), y1 - head * np.sin(angle + 0.5))
    hx, hy = _line([(x1, y1), left, (x1, y1), right], per_unit=12)
    return np.concatenate([x, hx[1:]]), np.concatenate([y, hy[1:]])


def _twelve_apart(shipped: Shipped) -> Scene:
    """Lesson 4: on one day the far leg, 12 months out, has no price."""
    middle = (BOX_Y0 + BOX_Y1) / 2
    near_k, far_k = shipped.row.index(shipped.near), shipped.row.index(shipped.far)
    steps: list[Stroke | Fill | Label] = []
    for k, symbol in enumerate(shipped.row):
        x, priced = box_x(k), symbol in shipped.priced
        gid = f"box-{k}"
        steps += [
            _stroke(
                gid,
                _box(x - BOX_W / 2, BOX_Y0, x + BOX_W / 2, BOX_Y1),
                color=INK if priced else MUTED,
                width=2.0 if priced else 1.4,
                dashed=not priced,
                frames=2,
            ),
            Label(
                _letter(symbol),
                x,
                middle,
                names=gid,
                color=INK if priced else MUTED,
                size=10,
                ha="center",
            ),
        ]
    first_x = box_x(0) - BOX_W / 2
    last_x = box_x(len(shipped.priced) - 1) + BOX_W / 2
    near_x, far_x = box_x(near_k), box_x(far_k)
    first = shipped.row[0]
    year, later = first[-5:-1], shipped.far[-5:-1]
    steps += [
        # The key to the month letters comes right after the last box, so the
        # repeated letters have it for the rest of the drawing.
        Label(
            f"letters are months: {_letter(first)} to {MONTH_LETTERS[-1]} run {_month(first)} "
            f"to {_MONTHS[-1]} {year}, then {MONTH_LETTERS[0]} to {_letter(shipped.far)} run "
            f"{_MONTHS[0]} to {_month(shipped.far)} {later}",
            0.3,
            0.88,
            names=f"box-{len(shipped.row) - 1}",
            color=MUTED,
            size=10,
        ),
        _stroke("priced", _span(first_x, last_x, BRACKET_Y, tick=0.08), color=MUTED, frames=6),
        Label(
            f"priced that day: {len(shipped.priced)} contracts",
            (first_x + last_x) / 2,
            1.19,
            names="priced",
            color=MUTED,
            size=11,
            ha="center",
        ),
        _stroke("near", _ring(near_x, middle), color=ACCENT, width=2.0, frames=6),
        Label(
            f"near: {shipped.near}",
            near_x,
            1.83,
            names="near",
            color=ACCENT,
            size=11,
            ha="center",
        ),
        _stroke(
            "later",
            _arc_arrow(near_x, middle + RING_RY + 0.02, far_x, BOX_Y1 + 0.05),
            color=ACCENT,
            width=2.0,
            frames=8,
        ),
        Label(
            f"+{shipped.spread_month} months",
            (near_x + far_x) / 2,
            3.45,
            names="later",
            color=ACCENT,
            size=12,
            ha="center",
        ),
        Label(
            f"far: {shipped.far}, no price",
            far_x + BOX_W / 2,
            1.83,
            names="later",
            color=LOST,
            size=11,
            ha="right",
        ),
        Label(
            f"the script adds up the legs that have a price, so it holds {shipped.near} alone",
            0.3,
            0.575,
            names="later",
            color=MUTED,
            size=11,
        ),
        Label(
            f"near leg alone on {shipped.near_alone:,} of {shipped.held:,} held days",
            0.3,
            0.25,
            names="later",
            color=MUTED,
            size=11,
        ),
    ]
    title = f"On {shipped.day} the far leg has no price"
    return Scene(title, "twelve_apart", tuple(steps))


# --- Drawing ------------------------------------------------------------------

#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label longer than one letter shows on its own for
#: :data:`PACED_LABEL_MS` and the finished drawing holds for
#: :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("one_hold", "twelve_apart")
PACED_LABEL_MS, PACED_HOLD_MS = 900, 12000


def sketch_timeline(scene: Scene) -> list[Frame]:
    """:func:`timeline`'s frames, slowed for the scenes in :data:`PACED`."""
    frames = timeline(scene)
    if scene.slug not in PACED:
        return frames
    paced = []
    for f in frames:
        step = scene.steps[f.done - 1] if f.partial == 0 and f.done else None
        # A box's one-letter label reads at a glance, and 16 of them at the slow
        # pace would hold back the Lesson 4 sketch's point by about nine seconds.
        letter = isinstance(step, Label) and len(step.text) == 1
        slow = step is not None and not isinstance(step, Stroke) and not letter
        paced.append(Frame(f.done, f.partial, PACED_LABEL_MS) if slow else f)
    last = paced[-1]
    paced[-1] = Frame(last.done, last.partial, PACED_HOLD_MS)
    return paced


def scenes(hold: Hold | None = None, shipped: Shipped | None = None) -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them, Lesson 2's then Lesson 4's."""
    if hold is None or shipped is None:
        contracts = load_strip(ROOT).contracts
        hold = hold if hold is not None else Hold.from_contracts(contracts)
        shipped = shipped if shipped is not None else Shipped.from_contracts(contracts)
    return (_one_hold(hold), _twelve_apart(shipped))


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


def make_vx_calendar_spread_whiteboards(out_dir: Path | None = None) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes()]


def main() -> None:
    for path in make_vx_calendar_spread_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
