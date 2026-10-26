"""Whiteboard sketches for the calendar spreads post.

``blog/calendar-spreads-lessons.md`` tests Chan's claim that calendar spreads
cointegrate on every pair of neighbouring natural gas and RBOB gasoline
contracts in EIA's settlements. This module draws two scenes, and the post
places each right after the text it draws.

1. What requiring both orientations removes, in Lesson 2 after the figure's
   caption. Two panels of two circles, one circle for the natural gas pairs
   that reject with the near month as the dependent leg and one for the far
   month, each circle's area to scale with its count, and the two overlapping
   by the count that rejects both ways. Against independent walks each
   orientation alone rejects in a median of 38 null pairs, and only 12 both
   ways. Against walks correlated as the files are, each alone still rejects
   in 38, and 35 both ways. So correlating the walks leaves each orientation
   where it was, and the whole rise in the null's count is the requirement
   for both losing its effect. It closes on the real files' counts. Its
   figures are :class:`BothOrientations`, which
   ``tests/test_stationary_candidates.py`` holds the run gives.
2. One window, four expiries, in Lesson 4 after the list under "The six days
   each window drops". The June 2018 natural gas pair on a time axis of
   trading days from late February to late May 2018: the four expiries it
   rests on, its window, which numbered file each leg is read from on each
   day, the days it keeps as grey dots, and the six it drops as vermilion
   crosses. Its figures are :class:`OneWindow`, read from the calendar and the
   committed files through the functions the run uses. Under protanopia the
   vermilion sits 7.5 from the grey, short of the 8 a reader can rely on, so a
   dropped day is told from a kept one by its cross as well as its colour.

Neither scene is schematic. Every count and date a label prints, and every
size and position the counts and dates set, comes from those two classes. The
June 2018 pair is the one ``tests/test_stationary_candidates.py`` already pins
the window and the dropped days of.

Both scenes carry more than the usual pace lets a reader take in, so
:func:`sketch_timeline` shows each of their labels on its own for 900 ms
rather than 350 and holds their finished drawings for twelve seconds rather
than four, as :data:`PACED` lists. That is the pace
:mod:`chan.equity_seasonals_whiteboard` gives its slower sketches.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look and frame rate. Their
colours are :mod:`chan.palette`'s, which a colour-blind reader can tell apart,
so :func:`render` gets :data:`chan.palette.INKS` and maps every frame onto them.
Only the scenes, their pace, their colours and the file names are this
module's. Each GIF is named :data:`GIF_PREFIX` plus the scene's slug. The
sketches are deterministic for the reason that module gives, so a redraw with
no change is a no-op diff.
Redraw both with::

    uv run python -m chan.calendar_spreads_whiteboard

It reads the committed EIA files and runs the natural gas batch and its two
nulls once more in each orientation, so it takes about half a minute.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from chan import stationary_candidates as sc
from chan.futures import (
    NATURAL_GAS_CONTRACTS,
    Product,
    contract_number,
    month_step,
    next_trading_day,
    previous_trading_day,
    trading_days,
)
from chan.paths import FIGURES_DIR
from chan.palette import ACCENT, INKS, LOST
from chan.regime_figure import MUTED
from chan.usdcad_tests_whiteboard import (
    Frame,
    Label,
    Scene,
    Stroke,
    _line,
    _stroke,
    render,
    timeline,
)

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "calendar_spreads_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``calendar_spreads_one_window.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


def _pairs(share: float, pairs: int) -> float:
    """A share of ``pairs`` as the count of pairs it is, a median possibly a half."""
    return round(share * pairs * 2) / 2


def _count(value: float) -> str:
    """A count of pairs as the post prints it: whole, or with one decimal for a half."""
    return f"{value:.0f}" if value == int(value) else f"{value:.1f}"


# --- Sketch 1: what requiring both orientations removes ---------------------


@dataclass(frozen=True)
class BothOrientations:
    """The natural gas counts the both-orientations sketch draws.

    Each null count is the median, over ``sets`` simulated sets, of how many
    of the commodity's ``pairs`` reject at 10% under one reject rule: near on
    far alone, far on near alone, or both. ``independent_*`` reads the null
    of independent walks and ``correlated_*`` the null at the files' own
    correlation, both with seed 20261003. ``files_*`` are the real counts.
    """

    pairs: int
    sets: int
    independent_near: float
    independent_far: float
    independent_both: float
    correlated_near: float
    correlated_far: float
    correlated_both: float
    files_near: int
    files_far: int
    files_both: int

    @classmethod
    def from_nulls(
        cls,
        spread: sc.CalendarSpread,
        independent_near: NDArray[np.float64],
        independent_far: NDArray[np.float64],
        correlated_near: NDArray[np.float64],
        correlated_far: NDArray[np.float64],
    ) -> BothOrientations:
        """The figures from one commodity's batch and its four single-orientation nulls."""
        n = len(spread.tests)

        def median(shares: NDArray[np.float64]) -> float:
            return _pairs(float(np.median(shares)), n)

        return cls(
            pairs=n,
            sets=len(spread.null),
            independent_near=median(independent_near),
            independent_far=median(independent_far),
            independent_both=median(spread.declared_null),
            correlated_near=median(correlated_near),
            correlated_far=median(correlated_far),
            correlated_both=median(spread.null),
            files_near=round(spread.near_on_far_share * n),
            files_far=round(spread.far_on_near_share * n),
            files_both=round(spread.share * n),
        )

    @classmethod
    def read(cls, product: Product = NATURAL_GAS_CONTRACTS) -> BothOrientations:
        """Run the batch, then each null once more in each single orientation."""
        spread = sc.calendar_spread(product)
        pairs = tuple(t.pair for t in spread.tests)

        def alone(correlation: float, orientation: str) -> NDArray[np.float64]:
            return sc.null_shares(pairs, correlation=correlation, orientation=orientation)

        return cls.from_nulls(
            spread,
            alone(0.0, "near"),
            alone(0.0, "far"),
            alone(spread.correlation, "near"),
            alone(spread.correlation, "far"),
        )


#: The area of the board one pair's circle area stands for, so a circle's
#: area is to scale with its count in both panels.
AREA_PER_PAIR = 0.05
#: Where each panel's circles centre across the board, and the height of the
#: point midway between the two centres. The near-on-far circle sits above.
PANEL_X = (2.9, 7.65)
CIRCLES_Y = 2.28
#: How far each label sits clear of the circle it names.
LABEL_GAP = 0.32


def radius(count: float) -> float:
    """The radius of the circle whose area stands for ``count`` pairs."""
    return math.sqrt(count * AREA_PER_PAIR / math.pi)


def lens_area(r1: float, r2: float, d: float) -> float:
    """The area two circles of radii ``r1`` and ``r2``, ``d`` apart, share."""
    if d >= r1 + r2:
        return 0.0
    if d <= abs(r1 - r2):
        return math.pi * min(r1, r2) ** 2
    a1 = r1 * r1 * math.acos((d * d + r1 * r1 - r2 * r2) / (2 * d * r1))
    a2 = r2 * r2 * math.acos((d * d + r2 * r2 - r1 * r1) / (2 * d * r2))
    kite = 0.5 * math.sqrt((-d + r1 + r2) * (d + r1 - r2) * (d - r1 + r2) * (d + r1 + r2))
    return a1 + a2 - kite


def apart(near: float, far: float, both: float) -> float:
    """How far apart the two circles' centres sit so they share ``both`` pairs' area.

    Found by bisection, since the shared area falls as the centres move apart.
    """
    r1, r2 = radius(near), radius(far)
    want = both * AREA_PER_PAIR
    low, high = abs(r1 - r2), r1 + r2
    for _ in range(80):
        mid = (low + high) / 2
        if lens_area(r1, r2, mid) > want:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def _circle(cx: float, cy: float, r: float, start: float) -> tuple:
    """A circle drawn from angle ``start``, counterclockwise, closed."""
    angle = start + np.linspace(0.0, 2 * math.pi, 72)
    return cx + r * np.cos(angle), cy + r * np.sin(angle)


def _lens(x: float, y1: float, r1: float, y2: float, r2: float) -> tuple:
    """The outline of what two circles centred at (x, y1) and (x, y2) share,
    the first above the second, as one closed stroke: the upper circle's arc
    inside the lower one, then back along the lower circle's arc inside the
    upper one."""
    d = y1 - y2
    a = (d * d + r1 * r1 - r2 * r2) / (2 * d)
    h = math.sqrt(max(r1 * r1 - a * a, 0.0))
    # Each angle is measured from the line between the centres, so each arc
    # runs across the overlap from one crossing point to the other.
    t1, t2 = math.atan2(h, a), math.atan2(h, d - a)
    upper = np.linspace(-t1, t1, 30)
    lower = np.linspace(t2, -t2, 30)
    xs = np.concatenate([x + r1 * np.sin(upper), x + r2 * np.sin(lower)])
    ys = np.concatenate([y1 - r1 * np.cos(upper), y2 + r2 * np.cos(lower)])
    return np.append(xs, xs[0]), np.append(ys, ys[0])


def _panel(
    key: str, heading: str, middle: float, near: float, far: float, both: float
) -> list[Stroke | Label]:
    """One panel: the near-on-far circle above, the far-on-near one below, and
    what they share, labelled beside it at the circles' waist."""
    d = apart(near, far, both)
    r1, r2 = radius(near), radius(far)
    y1, y2 = CIRCLES_Y + d / 2, CIRCLES_Y - d / 2
    side = math.sqrt(0.5)
    return [
        _stroke(f"{key}-near", _circle(middle, y1, r1, math.pi / 2), frames=8),
        Label(heading, middle, 3.85, names=f"{key}-near", ha="center"),
        Label(f"near on far: {_count(near)}", middle - r1 * side - LABEL_GAP, y1 + r1 * side,
              names=f"{key}-near", size=12, ha="right"),
        _stroke(f"{key}-far", _circle(middle, y2, r2, -math.pi / 2), frames=8),
        Label(f"far on near: {_count(far)}", middle - r2 * side - LABEL_GAP, y2 - r2 * side,
              names=f"{key}-far", size=12, ha="right"),
        _stroke(f"{key}-both", _lens(middle, y1, r1, y2, r2), color=ACCENT, width=3.2,
                frames=6),
        Label(f"both: {_count(both)}", middle + max(r1, r2) + LABEL_GAP, CIRCLES_Y,
              names=f"{key}-both", color=ACCENT, size=12),
    ]  # fmt: skip


def _both_orientations(f: BothOrientations) -> Scene:
    """Correlating the walks leaves each orientation alone where it was."""
    left = _panel(
        "independent",
        "independent walks",
        PANEL_X[0],
        f.independent_near,
        f.independent_far,
        f.independent_both,
    )
    right = _panel(
        "correlated",
        "walks correlated as the files are",
        PANEL_X[1],
        f.correlated_near,
        f.correlated_far,
        f.correlated_both,
    )
    return Scene(
        "What requiring both orientations removes",
        "both_orientations",
        (
            *left,
            *right,
            Label(
                f"medians of {f.sets:,} null sets of {f.pairs} natural gas pairs",
                5.0,
                0.6,
                names="correlated-both",
                color=MUTED,
                size=11,
                ha="center",
            ),
            Label(
                f"the files: {f.files_near} and {f.files_far} alone, {f.files_both} both",
                5.0,
                0.27,
                names="correlated-both",
                color=ACCENT,
                size=13,
                ha="center",
            ),
        ),
    )


# --- Sketch 2: one window, four expiries ------------------------------------


#: The pair the window sketch draws, the near month June 2018, whose window
#: and dropped days ``tests/test_stationary_candidates.py`` already pins.
EXAMPLE_NEAR = (2018, 6)


@dataclass(frozen=True)
class Stretch:
    """Consecutive window days on which each leg reads the same numbered file."""

    first: date
    last: date
    near_file: int
    far_file: int


@dataclass(frozen=True)
class OneWindow:
    """One pair's window as the run reads it.

    ``expiries`` are the last trading days of the contracts three months
    before the near one through the near one itself, as ``(delivery month,
    last day)``. ``stretches`` split the window where either leg moves to
    another numbered file. ``kept`` and ``dropped`` are the days the pair
    keeps and the six :func:`chan.stationary_candidates.guard_band` drops.
    """

    near: tuple[int, int]
    window: tuple[date, ...]
    expiries: tuple[tuple[tuple[int, int], date], ...]
    stretches: tuple[Stretch, ...]
    kept: tuple[date, ...]
    dropped: tuple[date, ...]

    @property
    def far(self) -> tuple[int, int]:
        return month_step(*self.near, 1)

    @classmethod
    def read(
        cls, product: Product = NATURAL_GAS_CONTRACTS, near: tuple[int, int] = EXAMPLE_NEAR
    ) -> OneWindow:
        """Read the pair at ``near`` through the run's own calendar and files."""
        window = sc.spread_window(product, near)
        far = month_step(*near, 1)
        months = [month_step(*near, k) for k in (-3, -2, -1, 0)]
        stretches: list[Stretch] = []
        for day in window:
            files = (
                contract_number(day, *near, product.last_trade),
                contract_number(day, *far, product.last_trade),
            )
            if stretches and (stretches[-1].near_file, stretches[-1].far_file) == files:
                stretches[-1] = Stretch(stretches[-1].first, day, *files)
            else:
                stretches.append(Stretch(day, day, *files))
        return cls(
            near=near,
            window=window,
            expiries=tuple((m, product.last_trade(*m)) for m in months),
            stretches=tuple(stretches),
            kept=sc.spread_pair(product, near).kept,
            dropped=tuple(sorted(sc.guard_band(product, near))),
        )


#: Where the window sketch's day axis runs across the board, and the height
#: of each of its rows.
DAYS_X = (2.0, 8.85)
WINDOW_Y = 3.6
NEAR_Y, FAR_Y = 2.95, 2.3
KEPT_Y = 1.82
AXIS_Y = 1.32
TICK = 0.15
CROSS = 0.045


def _axis_days(w: OneWindow) -> tuple[date, ...]:
    """The trading days the axis spans: one before the first expiry, through
    one after the window's last day."""
    first = previous_trading_day(w.expiries[0][1])
    return trading_days(first, next_trading_day(w.window[-1]))


def day_x(w: OneWindow, day: date) -> float:
    """Where ``day`` sits on the axis, one equal step per trading day."""
    days = _axis_days(w)
    step = (DAYS_X[1] - DAYS_X[0]) / (len(days) - 1)
    return DAYS_X[0] + days.index(day) * step


def _month_name(month: tuple[int, int], form: str) -> str:
    return date(month[0], month[1], 1).strftime(form)


def _day(day: date) -> str:
    return f"{day.day} {day:%b}"


def _cross(gid: str, x: float, y: float) -> Stroke:
    r = CROSS
    xy = _line([(x - r, y - r), (x + r, y + r), (x, y), (x - r, y + r), (x + r, y - r)], 40)
    return _stroke(gid, xy, color=LOST, width=2.0, frames=2)


def _one_window(w: OneWindow) -> Scene:
    """The June 2018 pair's window: its expiries, its files, and the days it drops."""
    x = {day: day_x(w, day) for day in _axis_days(w)}
    first, last = w.window[0], w.window[-1]
    steps: list[Stroke | Label] = [
        _stroke("axis", _line([(DAYS_X[0], AXIS_Y), (DAYS_X[1], AXIS_Y)]), color=MUTED, frames=6),
    ]
    for k, (month, day) in enumerate(w.expiries):
        gid = f"expiry-{k}"
        steps += [
            _stroke(gid, _line([(x[day], AXIS_Y), (x[day], AXIS_Y + TICK)], 30), color=MUTED,
                    frames=2),
            _stroke(f"{gid}-guide", _line([(x[day], AXIS_Y + TICK), (x[day], WINDOW_Y)], 10),
                    color=MUTED, width=1.2, dashed=True, frames=4),
            Label(f"{_month_name(month, '%b')} expires {_day(day)}", x[day], AXIS_Y - 0.33,
                  names=gid, color=MUTED, size=10, ha="center"),
        ]  # fmt: skip
    window = _line(
        [
            (x[first], WINDOW_Y + TICK),
            (x[first], WINDOW_Y),
            (x[last], WINDOW_Y),
            (x[last], WINDOW_Y + TICK),
        ]
    )
    steps += [
        _stroke("window", window, frames=8),
        Label(f"the window: {len(w.window)} trading days", x[last], WINDOW_Y + 0.47,
              names="window", ha="right", size=12),
    ]  # fmt: skip
    for leg, y, month in (("near", NEAR_Y, w.near), ("far", FAR_Y, w.far)):
        steps.append(
            Label(f"{_month_name(month, '%B')}, {leg}", DAYS_X[0] - 0.2, y, names="window",
                  ha="right", size=12)
        )  # fmt: skip
        for k, stretch in enumerate(w.stretches):
            gid = f"{leg}-{k}"
            number = stretch.near_file if leg == "near" else stretch.far_file
            steps += [
                _stroke(gid, _line([(x[stretch.first], y), (x[stretch.last], y)]), width=4.0,
                        frames=4),
                Label(f"file {number}", (x[stretch.first] + x[stretch.last]) / 2, y + 0.32,
                      names=gid, size=11, ha="center"),
            ]  # fmt: skip
    steps += [
        Stroke(
            "kept",
            np.array([x[day] for day in w.kept]),
            np.full(len(w.kept), KEPT_Y),
            color=MUTED,
            frames=8,
            dots=3.0,
        ),
        Label(f"{len(w.kept)} kept", DAYS_X[0] - 0.2, KEPT_Y, names="kept", color=MUTED, size=12,
              ha="right"),
    ]  # fmt: skip
    steps += [_cross(f"dropped-{k}", x[day], KEPT_Y) for k, day in enumerate(w.dropped)]
    steps.append(
        Label(
            "a rule a day off misreads only the crossed days",
            5.0,
            0.4,
            names=f"dropped-{len(w.dropped) - 1}",
            color=ACCENT,
            ha="center",
        )
    )
    return Scene("One window, four expiries", "one_window", tuple(steps))


def scenes(orientations: BothOrientations, window: OneWindow) -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them."""
    return (_both_orientations(orientations), _one_window(window))


#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
PACED = ("both_orientations", "one_window")
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


def _write(scene: Scene, folder: Path) -> Path:
    frames = sketch_timeline(scene)
    first, *rest = render(scene, frames, INKS)
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


def make_calendar_spreads_whiteboards(
    out_dir: Path | None = None,
    orientations: BothOrientations | None = None,
    window: OneWindow | None = None,
) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the
    order the post reads them. Each figure class is read from the committed
    files when it is not handed in."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    orientations = orientations if orientations is not None else BothOrientations.read()
    window = window if window is not None else OneWindow.read()
    return [_write(scene, folder) for scene in scenes(orientations, window)]


def main() -> None:
    for path in make_calendar_spreads_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
