"""A whiteboard sketch for the price spread post: why the spread is mostly the fit's intercept.

``blog/price-spread-ratio-lessons.md`` says, in Lesson 4, that each 20-day
regression fits ``USO = c + h·GLD + e`` and the scripts trade ``USO − h·GLD``,
which is ``c + e``, and that ``c`` carries almost all of it. A reader can take
that as a fact about the run without seeing why it happens. The reason is
geometric. GLD traded near 90 dollars, so every 20-day cloud of points sits
about 90 dollars to the right of GLD = 0, where ``c`` is read. A small turn of
the fitted line about its cloud moves the place it meets GLD = 0 a long way,
by about the change in ``h`` times that distance, while the leftover ``e`` of
the last day stays a few dollars. This module draws that as one scene, and the
post places it right after the list that ends on the leftover earning nothing.

1. Why c carries the spread: two real 20-day windows one trading week apart,
   the second ending on the day the spread reaches its lowest value, which is
   also the day the hedge ratio reaches its highest. On the left, GLD and USO
   axes to scale, with GLD = 0 drawn as USO's axis, each window's fitted line
   extended dashed back to GLD = 0 and landing at its ``c``, and a bracket for
   how far ``c`` fell. On the right, the clouds magnified, where the second
   barely moves from the first while its line turns steeper, and the second
   window's ``e`` as a tick from its line to its last day's point, which a
   ring marks. It closes
   on the whole run's figures, the correlation of ``c`` with the spread and the
   two standard deviations, labelled as figures over every traded day rather
   than placed beside one window's points.

One window alone would show ``c`` sitting far below the cloud, which reads as
the reason when the claim is about how far ``c`` moves. So the scene always
draws two.

Every figure the scene prints and every point it places comes from
:class:`Lever`, which :meth:`Lever.from_run` reads from the committed vintage
through :func:`chan.price_spread.read_sources`, scale-break guard included, and
:func:`chan.price_spread.rolling_intercept`, the same intercept
``tests/test_price_spread.py`` reads. Which two windows are drawn is read from
the run too: the day of the spread's lowest value and the day
:data:`WEEK` rows before it. The left panel is to scale on both axes, each its
own affine map, so a line straight in dollars is straight on the board. The
right panel magnifies the clouds, each axis its own affine map again. Neither
axis is broken. The arithmetic label rounds ``h``'s change and the clouds'
mean GLD, and it leaves out two smaller terms that nearly cancel, the change
in mean USO and the mean ``h`` times the change in mean GLD, so it carries an
approximate sign.

Exploratory, like everything Example 3.1 runs here.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from chan.paths import FIGURES_DIR
from chan.price_spread import (
    LOOKBACK,
    X_SYMBOL,
    Y_SYMBOL,
    price_spread,
    read_sources,
    rolling_intercept,
)
from chan.regime_figure import ACCENT, INK, MUTED
from chan.series import WindowCrossesScaleBreak
from chan.usdcad_tests_whiteboard import (
    Frame,
    Label,
    Scene,
    Stroke,
    _box,
    _dot,
    _line,
    _span,
    _stroke,
    render,
    timeline,
)
from chan.vintage import VintageUnavailable

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "price_spread_"

#: How many rows before the spread's lowest day the first window ends, one
#: trading week.
WEEK = 5


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``price_spread_intercept_lever.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


@dataclass(frozen=True)
class Window:
    """One 20-day regression ``USO = c + h·GLD + e``, and the points it fits.

    ``gld`` and ``uso`` are the window's closes, oldest first, ``hedge`` is
    ``h``, ``intercept`` is ``c`` and ``leftover`` is ``e`` on the window's last
    day, the day the scripts trade on.
    """

    end: pd.Timestamp
    gld: np.ndarray
    uso: np.ndarray
    hedge: float
    intercept: float
    leftover: float

    @property
    def spread(self) -> float:
        """``USO − h·GLD`` on the last day, which is ``c + e``."""
        return float(self.uso[-1] - self.hedge * self.gld[-1])


@dataclass(frozen=True)
class Lever:
    """What the scene draws: two windows a week apart, and the whole run's figures.

    - ``before`` and ``after``: the two windows, ``after`` ending on the day of
      the spread's lowest value.
    - ``correlation``: the correlation of ``c`` with the spread over every
      traded day.
    - ``spread_sd`` and ``leftover_sd``: the standard deviations, in dollars,
      of the spread and of ``e`` over the same days, with MATLAB's n − 1.
    - ``days``: how many traded days those figures cover.
    """

    before: Window
    after: Window
    correlation: float
    spread_sd: float
    leftover_sd: float
    days: int

    @property
    def mean_gld(self) -> float:
        """The two windows' mean GLD, averaged: how far the clouds sit from GLD = 0."""
        return float((self.before.gld.mean() + self.after.gld.mean()) / 2)

    @classmethod
    def from_run(cls, closes: pd.DataFrame | None = None) -> Lever:
        """Read the figures from ``closes``, or from the committed vintage when none is given."""
        if closes is None:
            _, closes = read_sources()
        days = closes.index
        gld = closes[X_SYMBOL].to_numpy(dtype=float)
        uso = closes[Y_SYMBOL].to_numpy(dtype=float)
        signal = price_spread(days, gld, uso)
        intercept = rolling_intercept(uso, gld)[LOOKBACK:]
        leftover = signal.value - intercept
        lowest = int(np.argmin(signal.value))

        def window(kept: int) -> Window:
            row = kept + LOOKBACK
            span = slice(row - LOOKBACK + 1, row + 1)
            return Window(
                end=signal.days[kept],
                gld=gld[span],
                uso=uso[span],
                hedge=float(signal.hedge[kept]),
                intercept=float(intercept[kept]),
                leftover=float(leftover[kept]),
            )

        return cls(
            before=window(lowest - WEEK),
            after=window(lowest),
            correlation=float(np.corrcoef(signal.value, intercept)[0, 1]),
            spread_sd=float(signal.value.std(ddof=1)),
            leftover_sd=float(leftover.std(ddof=1)),
            days=len(signal.days),
        )


def _signed(value: float, places: int) -> str:
    """``value`` to ``places`` decimals with a typographic minus, as the post prints one."""
    return f"{value:.{places}f}".replace("-", "−")


def _day(day: pd.Timestamp) -> str:
    """A day as the post writes one, without its year, such as ``7 July``."""
    return f"{day.day} {day:%B}"


#: The left panel, to scale: GLD from 0 to :data:`GLD_TOP` dollars across
#: :data:`MAIN_X`, and USO over :data:`USO_SPAN` dollars up :data:`MAIN_Y`.
GLD_TOP = 95.0
MAIN_X = (2.1, 5.6)
USO_SPAN = (-175.0, 45.0)
MAIN_Y = (0.3, 3.9)
#: The right panel magnifies GLD over :data:`ZOOM_GLD` and USO over
#: :data:`ZOOM_USO` onto the board's :data:`ZOOM_X` by :data:`ZOOM_Y`.
ZOOM_GLD = (88.6, 94.4)
ZOOM_USO = (28.0, 43.0)
ZOOM_X = (6.15, 9.72)
ZOOM_Y = (1.5, 4.4)
#: Where each window's name sits in the right panel: the first's at its right,
#: below its flatter line, and the second's in its upper left, above its
#: steeper one. ``e``'s label runs along the panel's foot, below every point.
BEFORE_TAG_Y, AFTER_TAG_Y, LEFTOVER_Y = 2.45, 4.1, 1.8
#: The "GLD = 0" label sits below the origin, beside USO's axis and clear of the
#: span above the GLD axis, so it reads as naming the upright axis.
GLD_ZERO_Y = 2.8
#: The ring round the second window's last point, the one its ``e`` is
#: measured on. Two other points sit within a tenth of a dollar of GLD from it,
#: so the tick alone could end at any of three.
RING = 0.1
#: The rule under the right panel that the whole run's figures sit beneath.
RULE_X, RULE_Y = 5.65, 1.32


def _affine(value, source: tuple[float, float], board: tuple[float, float]):
    return board[0] + (np.asarray(value, dtype=float) - source[0]) / (source[1] - source[0]) * (
        board[1] - board[0]
    )


def _main(gld, uso) -> tuple[np.ndarray, np.ndarray]:
    """A point in dollars on the left panel."""
    return _affine(gld, (0.0, GLD_TOP), MAIN_X), _affine(uso, USO_SPAN, MAIN_Y)


def _zoom(gld, uso) -> tuple[np.ndarray, np.ndarray]:
    """A point in dollars on the right panel."""
    return _affine(gld, ZOOM_GLD, ZOOM_X), _affine(uso, ZOOM_USO, ZOOM_Y)


def _refuse_off_the_board(lever: Lever) -> None:
    """Refuse figures that would fall off either panel rather than draw them clipped."""
    for window in (lever.before, lever.after):
        fitted = window.intercept + window.hedge * window.gld
        inside = (
            ZOOM_GLD[0] <= window.gld.min()
            and window.gld.max() <= ZOOM_GLD[1]
            and ZOOM_USO[0] <= min(window.uso.min(), fitted.min())
            and max(window.uso.max(), fitted.max()) <= ZOOM_USO[1]
            and USO_SPAN[0] <= window.intercept
        )
        if not inside:
            raise ValueError(
                f"the window to {window.end.date()} falls outside the sketch's panels, GLD "
                f"{ZOOM_GLD} and USO {ZOOM_USO} magnified, and c above {USO_SPAN[0]}"
            )


def _fit(window: Window, place) -> tuple[np.ndarray, np.ndarray]:
    """The window's fitted line across its own GLD range, placed by ``place``."""
    ends = np.array([window.gld.min(), window.gld.max()])
    x, y = place(ends, window.intercept + window.hedge * ends)
    return _line(list(zip(x, y, strict=True)), per_unit=8)


def _reach(window: Window) -> tuple[np.ndarray, np.ndarray]:
    """The fitted line extended from the window's lowest GLD back to GLD = 0, on the left."""
    low = window.gld.min()
    x, y = _main(
        np.array([low, 0.0]), np.array([window.intercept + window.hedge * low, window.intercept])
    )
    return _line(list(zip(x, y, strict=True)), per_unit=4)


def _ring(x: float, y: float, radius: float = RING) -> tuple[np.ndarray, np.ndarray]:
    """A circle round (x, y) on the board, drawn from its right-hand point."""
    turn = np.linspace(0.0, 2 * np.pi, 25)
    return x + radius * np.cos(turn), y + radius * np.sin(turn)


def _points(gid: str, window: Window, color: str) -> Stroke:
    x, y = _zoom(window.gld, window.uso)
    return Stroke(gid, x, y, color=color, dots=4.5, frames=5)


def _lever(lever: Lever) -> Scene:
    """Two windows a week apart: a small turn of the fitted line moves ``c`` a long way."""
    _refuse_off_the_board(lever)
    before, after = lever.before, lever.after
    axis_x, zero_y = MAIN_X[0], float(_main(0.0, 0.0)[1])
    axis_end = float(_main(GLD_TOP, 0.0)[0]) + 0.15
    c_before, c_after = (float(_main(0.0, w.intercept)[1]) for w in (before, after))
    box_x, box_y = _main(np.array(ZOOM_GLD), np.array(ZOOM_USO))
    mean_x = float(_main(lever.mean_gld, 0.0)[0])
    tick_x, last_y = (float(v) for v in _zoom(after.gld[-1], after.uso[-1]))
    fitted_y = float(_zoom(after.gld[-1], after.intercept + after.hedge * after.gld[-1])[1])
    drop_x = axis_x - 0.15
    left = drop_x - 0.2
    middle = (c_before + c_after) / 2
    moved = "fell" if after.intercept < before.intercept else "rose"
    return Scene(
        "Why c carries the spread",
        "intercept_lever",
        (
            _stroke(
                "uso-axis",
                _line([(axis_x, MAIN_Y[0]), (axis_x, MAIN_Y[1])]),
                color=MUTED,
                width=1.6,
                frames=6,
            ),
            Label("USO", left, 3.8, names="uso-axis", color=MUTED, ha="right", size=12),
            Label("GLD = 0", left, GLD_ZERO_Y, names="uso-axis", color=MUTED, ha="right", size=12),
            _stroke(
                "gld-axis",
                _line([(axis_x, zero_y), (axis_end, zero_y)]),
                color=MUTED,
                width=1.6,
                frames=6,
            ),
            Label(
                "GLD",
                axis_end - 0.5,
                zero_y - 0.3,
                names="gld-axis",
                color=MUTED,
                ha="center",
                size=12,
            ),
            _stroke(
                "zoom",
                _box(box_x[0], box_y[0], box_x[1], box_y[1]),
                color=MUTED,
                width=1.2,
                frames=4,
            ),
            _stroke(
                "to-top",
                _line([(box_x[1], box_y[1]), (ZOOM_X[0], ZOOM_Y[1])]),
                color=MUTED,
                width=1.0,
                frames=4,
            ),
            _stroke(
                "to-bottom",
                _line([(box_x[1], box_y[0]), (ZOOM_X[0], ZOOM_Y[0])]),
                color=MUTED,
                width=1.0,
                frames=4,
            ),
            _stroke(
                "panel",
                _box(ZOOM_X[0], ZOOM_Y[0], ZOOM_X[1], ZOOM_Y[1]),
                color=MUTED,
                width=1.2,
                frames=6,
            ),
            _points("cloud-before", before, MUTED),
            _stroke("fit-before", _fit(before, _zoom), color=MUTED, frames=5),
            Label(
                f"{_day(before.end)}, h {before.hedge:.2f}",
                ZOOM_X[1] - 0.2,
                BEFORE_TAG_Y,
                names="fit-before",
                color=MUTED,
                ha="right",
                size=11,
            ),
            _stroke("reach-before", _reach(before), color=MUTED, dashed=True, frames=8),
            _dot("c-before", axis_x, c_before),
            Label(
                f"c {_signed(before.intercept, 2)}",
                left,
                c_before,
                names="c-before",
                color=ACCENT,
                ha="right",
                size=12,
            ),
            _points("cloud-after", after, INK),
            _stroke("fit-after", _fit(after, _zoom), color=INK, frames=5),
            Label(
                f"{_day(after.end)}, h {after.hedge:.2f}",
                ZOOM_X[0] + 0.2,
                AFTER_TAG_Y,
                names="fit-after",
                color=INK,
                size=11,
            ),
            _stroke("reach-after", _reach(after), color=INK, dashed=True, frames=8),
            _dot("c-after", axis_x, c_after),
            Label(
                f"c {_signed(after.intercept, 2)}",
                left,
                c_after,
                names="c-after",
                color=ACCENT,
                ha="right",
                size=12,
            ),
            _stroke(
                "drop",
                _line(
                    [
                        (drop_x + 0.1, c_before),
                        (drop_x, c_before),
                        (drop_x, c_after),
                        (drop_x + 0.1, c_after),
                    ]
                ),
                color=ACCENT,
                frames=6,
            ),
            Label(
                f"c {moved} {abs(after.intercept - before.intercept):.2f}",
                left,
                middle + 0.17,
                names="drop",
                color=ACCENT,
                ha="right",
                size=12,
            ),
            _stroke(
                "distance",
                _span(axis_x, mean_x, zero_y + 0.3, tick=0.08),
                color=MUTED,
                width=1.4,
                frames=6,
            ),
            Label(
                f"{lever.mean_gld:.1f} dollars",
                (axis_x + mean_x) / 2 - 0.4,
                zero_y + 0.6,
                names="distance",
                color=MUTED,
                ha="center",
                size=11,
            ),
            Label(
                f"≈ {abs(after.hedge - before.hedge):.2f} × {lever.mean_gld:.1f}",
                left,
                middle - 0.17,
                names="distance",
                color=ACCENT,
                ha="right",
                size=11,
            ),
            _stroke(
                "last-day",
                _ring(tick_x, last_y),
                color=INK,
                width=1.4,
                frames=4,
            ),
            _stroke(
                "leftover",
                _line([(tick_x, fitted_y), (tick_x, last_y)], per_unit=10),
                color=INK,
                width=2.6,
                frames=3,
            ),
            Label(
                f"e {_signed(after.leftover, 2)}, a week before {_signed(before.leftover, 2)}",
                ZOOM_X[0] + 0.2,
                LEFTOVER_Y,
                names="leftover",
                color=INK,
                size=10,
            ),
            _stroke(
                "rule",
                _line([(RULE_X, RULE_Y), (ZOOM_X[1], RULE_Y)]),
                color=MUTED,
                width=1.0,
                frames=4,
            ),
            Label(
                f"over all {lever.days:,} traded days",
                RULE_X,
                RULE_Y - 0.28,
                names="rule",
                color=MUTED,
                size=10,
            ),
            Label(
                f"correlation of c and the spread {lever.correlation:.4f}",
                RULE_X,
                RULE_Y - 0.58,
                names="rule",
                color=INK,
                size=10,
            ),
            Label(
                f"SD of the spread {lever.spread_sd:.2f} dollars, of e {lever.leftover_sd:.2f}",
                RULE_X,
                RULE_Y - 0.88,
                names="rule",
                color=INK,
                size=10,
            ),
        ),
    )


def scenes(lever: Lever) -> tuple[Scene, ...]:
    """The post's one sketch, in a tuple like every other post's module returns."""
    return (_lever(lever),)


def draft() -> tuple[Scene, ...]:
    """The scene on the committed vintage, for the sketch-notes draft script."""
    return scenes(Lever.from_run())


#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
PACED = ("intercept_lever",)
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


def make_price_spread_whiteboards(
    out_dir: Path | None = None, lever: Lever | None = None
) -> list[Path]:
    """Write the post's GIF and return its path in a list.

    ``lever`` is read from the committed vintage when it is not handed in.
    """
    folder = out_dir if out_dir is not None else FIGURES_DIR
    lever = lever if lever is not None else Lever.from_run()
    return [_write(scene, folder) for scene in scenes(lever)]


def main() -> None:
    try:
        paths = make_price_spread_whiteboards()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # As in chan.price_spread.main, a refusal that names the source or the
        # flagged day reaches the operator as one line.
        raise SystemExit(str(refused)) from refused
    for path in paths:
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
