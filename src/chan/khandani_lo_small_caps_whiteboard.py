"""Whiteboard sketches for the post on Khandani and Lo's reversal on Chan's S&P 600 file.

``blog/khandani-lo-small-caps-lessons.md`` compares the reversal's Sharpe
ratio on Chan's S&P 600 file with his S&P 500 file, and its Lesson 6 adds the
S&P 400 from a later run. This module draws two scenes, and the post places
each right after the paragraph it draws. Neither is schematic. Every figure
either prints is read from a run.

1. The correlation narrows the standard error, in Lesson 3: the closes' gap
   of +3.1576 on one axis of the gap in Sharpe ratio, against a band two
   standard errors each way round 0 for the two books treated as unrelated
   and another for their measured correlation. The first band ends just short
   of the gap and the second well short of it. Its figures come from
   :class:`Narrowing`, which reads :func:`chan.khandani_lo_small_caps.compare`
   on the two committed files.
2. The size order at the closes and the opens, in Lesson 6: the three
   indexes from the largest companies to the smallest, with each price's
   Sharpe ratios before costs joined by a line, to one scale. A falling step
   breaks the order Chan's explanation predicts and is red, a rising step
   beyond one year's noise is green and prints its standard errors, and a
   rising step inside the noise stays black. The title gives the reading
   written down before the S&P 400 run. The S&P 500 and S&P 600 figures come
   from :func:`chan.khandani_lo_small_caps.compare`, and the S&P 400's from
   :class:`MidCaps`, read from :mod:`chan.khandani_lo_mid_caps` on the owner's
   archive.

Both build slowly, as :data:`PACED` lists.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, and the
pacing and GIF writer follow :mod:`chan.equity_seasonals_whiteboard`.
``tests/test_khandani_lo_small_caps_whiteboard.py`` pins what each scene draws.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from chan import khandani_lo_mid_caps as mid_caps
from chan import khandani_lo_small_caps as small_caps
from chan.archive import ArchiveRefused, ArchiveUnavailable
from chan.fund_panel import PanelRefused
from chan.khandani_lo import TRADING_DAYS
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    TINT,
    Fill,
    Frame,
    Label,
    Scene,
    Stroke,
    _arrow,
    _box,
    _dot,
    _line,
    _stroke,
    render,
    timeline,
)
from chan.vintage import VintageUnavailable

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "khandani_lo_small_caps_"

#: The width of the green edge drawn round every pale tint that carries
#: meaning, as :mod:`chan.equity_seasonals_whiteboard` draws it.
TINT_EDGE = 1.2


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``khandani_lo_small_caps_size_order.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


def _tinted(gid: str, x0: float, y0: float, x1: float, y1: float) -> tuple[Fill, Stroke]:
    """A pale tint and a thin green edge round it, so the region it marks
    reads at WCAG's 3 to 1 for graphical objects. The edge is ``gid`` plus
    ``-edge``."""
    return Fill(gid, x0, y0, x1, y1, TINT), _stroke(
        f"{gid}-edge", _box(x0, y0, x1, y1), color=GOOD, width=TINT_EDGE, frames=4
    )


def _signed(value: float, places: int) -> str:
    """``value`` to ``places`` decimals with its sign, and a typographic minus."""
    return f"{value:+.{places}f}".replace("-", "−")


# --- Lesson 3: the correlation narrows the standard error -----------------------


@dataclass(frozen=True)
class Narrowing:
    """What the narrowing scene draws, from the closes' gap before costs.

    - ``gap``: the S&P 600's Sharpe ratio less the S&P 500's.
    - ``correlation``: the two books' daily profits' correlation.
    - ``standard_error``: the gap's standard error at that correlation.
    - ``unrelated_error``: the same standard error with the correlation set to
      0, from :func:`chan.khandani_lo_small_caps.memmel_variance`, as
      ``test_without_the_correlation_the_closes_standard_error_would_be_1_4252``
      in ``tests/test_khandani_lo_small_caps.py`` computes it.
    - ``days``: the days both books trade.
    """

    gap: float
    correlation: float
    standard_error: float
    unrelated_error: float
    days: int

    @property
    def z(self) -> float:
        return self.gap / self.standard_error

    @property
    def unrelated_z(self) -> float:
        return self.gap / self.unrelated_error

    @classmethod
    def from_comparison(cls, result: small_caps.Comparison) -> Narrowing:
        a, b = result.small_closes.pnl, result.large_closes.pnl
        gap = result.closes_gap
        daily = [float(s.mean() / s.std(ddof=1)) for s in (a, b)]
        variance = small_caps.memmel_variance(daily[0], daily[1], 0, gap.days)
        return cls(
            gap=gap.gap,
            correlation=gap.correlation,
            standard_error=gap.standard_error,
            unrelated_error=math.sqrt(TRADING_DAYS * variance),
            days=gap.days,
        )


#: The narrowing scene's axis runs over these gaps in Sharpe ratio, from
#: :data:`NARROW_X`'s left end to its right.
NARROW_RANGE = (-3.0, 3.5)
NARROW_X = (0.5, 6.5)
NARROW_TICKS = (-1.0, 0.0, 1.0)
#: The axis's height, and each row's band, from its bottom to its top.
NARROW_AXIS_Y = 1.25
UNRELATED_ROW = (3.2, 3.6)
MEASURED_ROW = (1.75, 2.15)


def _on_gap(value: float) -> float:
    """Where a gap in Sharpe ratio sits on the narrowing scene's axis."""
    (x0, x1), (lo, hi) = NARROW_X, NARROW_RANGE
    return x0 + (x1 - x0) * (value - lo) / (hi - lo)


def _correlation_narrows(n: Narrowing) -> Scene:
    """The closes' gap against two standard errors each way, unrelated and measured."""
    m = small_caps.NOISE_MULTIPLE
    if not 0 < n.standard_error < n.unrelated_error:
        raise ValueError(
            f"the scene says the correlation narrows the standard error, and the "
            f"measured {n.standard_error} is not inside the unrelated {n.unrelated_error}"
        )
    # A narrower measured error puts the measured z further out than the
    # unrelated one, so a gap past the line unrelated is past it measured too.
    if not m < n.unrelated_z < m + 0.5:
        raise ValueError(
            f"the scene says the gap is barely past {m:g} with the books unrelated, "
            f"and there its z is {n.unrelated_z}"
        )
    if not (NARROW_RANGE[0] < -m * n.unrelated_error and n.gap < NARROW_RANGE[1]):
        raise ValueError(f"a gap of {n.gap} or its band runs off the axis")
    ticks = []
    for value in NARROW_TICKS:
        x = _on_gap(value)
        ticks += [(x, NARROW_AXIS_Y), (x, NARROW_AXIS_Y - 0.12), (x, NARROW_AXIS_Y)]
    gap_x = _on_gap(n.gap)
    rows = (
        ("unrelated", UNRELATED_ROW, n.unrelated_error, n.unrelated_z),
        ("measured", MEASURED_ROW, n.standard_error, n.z),
    )
    steps: list[Stroke | Fill | Label] = [
        _stroke(
            "axis",
            _line([(NARROW_X[0], NARROW_AXIS_Y), (NARROW_X[1], NARROW_AXIS_Y)] + ticks),
            color=MUTED,
            frames=12,
        ),
        *[
            Label(
                _signed(value, 0) if value else "0",
                _on_gap(value),
                NARROW_AXIS_Y - 0.42,
                names="axis",
                color=MUTED,
                ha="center",
                size=10,
            )
            for value in NARROW_TICKS
        ],
        Label(
            "gap in Sharpe ratio",
            NARROW_X[1] + 0.25,
            NARROW_AXIS_Y,
            names="axis",
            color=MUTED,
            size=10,
        ),
    ]
    words = (
        f"unrelated, ρ = 0: standard error {n.unrelated_error:.4f}",
        f"measured ρ = {n.correlation:.4f}: standard error {n.standard_error:.4f}",
    )
    for (gid, (y0, y1), error, _), text in zip(rows, words, strict=True):
        steps += [
            *_tinted(gid, _on_gap(-m * error), y0, _on_gap(m * error), y1),
            Label(text, NARROW_X[0], y1 + 0.3, names=gid, size=11),
        ]
        if gid == "unrelated":
            steps.append(
                Label(
                    f"{m:g} standard errors each way",
                    _on_gap(0.0),
                    y0 - 0.32,
                    names=gid,
                    color=GOOD,
                    ha="center",
                    size=11,
                )
            )
    steps += [
        _stroke(
            "gap",
            _line([(gap_x, NARROW_AXIS_Y), (gap_x, UNRELATED_ROW[1] + 0.15)], per_unit=4),
            color=ACCENT,
            width=2.6,
            frames=9,
        ),
        Label(
            f"gap {_signed(n.gap, 4)}",
            gap_x,
            NARROW_AXIS_Y - 0.42,
            names="gap",
            color=ACCENT,
            ha="center",
            size=11,
        ),
    ]
    for gid, (y0, y1), _, z in rows:
        text = f"z {_signed(z, 4)}, barely past {m:g}" if gid == "unrelated" else f"z {_signed(z, 4)}"
        steps.append(Label(text, gap_x + 0.22, (y0 + y1) / 2, names="gap", size=11))
    steps.append(
        Label(
            f"closes, before costs, {n.days} days",
            0.3,
            0.25,
            names="gap",
            color=MUTED,
            size=10,
        )
    )
    return Scene("The correlation narrows the standard error", "correlation_narrows", tuple(steps))


# --- Lesson 6: the size order at the closes and the opens -----------------------


@dataclass(frozen=True)
class MidCaps:
    """The S&P 400's figures the size-order scene draws, from Entry 50's run.

    The run is :func:`chan.khandani_lo_mid_caps.comparison` on the owner's
    archive, so these are read once and pinned rather than read on every draw.
    ``tests/test_khandani_lo_small_caps_whiteboard.py`` pins them as
    ``PINNED_MID``, and ``test_the_whiteboard_draws_this_runs_figures`` in
    ``tests/test_khandani_lo_mid_caps.py`` holds that the run gives them.

    - ``closes`` and ``opens``: the S&P 400's Sharpe ratio before costs.
    - ``closes_up_z`` and ``opens_up_z``: the step from the S&P 500 to the
      S&P 400 in standard errors, the S&P 400 less the S&P 500.
    - ``closes_down_z`` and ``opens_down_z``: the step from the S&P 400 to the
      S&P 600 in standard errors, the S&P 600 less the S&P 400.
    """

    closes: float
    opens: float
    closes_up_z: float
    closes_down_z: float
    opens_up_z: float
    opens_down_z: float

    @classmethod
    def from_run(cls, result: mid_caps.MidCapComparison) -> MidCaps:
        return cls(
            closes=result.closes.mid.before_costs,
            opens=result.opens.mid.before_costs,
            closes_up_z=result.closes.mid_gap.z,
            closes_down_z=result.closes.small_gap.z,
            opens_up_z=result.opens.mid_gap.z,
            opens_down_z=result.opens.small_gap.z,
        )


@dataclass(frozen=True)
class SizeOrder:
    """Each price's three Sharpe ratios before costs, largest companies first,
    and each step's standard errors, smaller index less larger."""

    closes: tuple[float, float, float]
    opens: tuple[float, float, float]
    closes_z: tuple[float, float]
    opens_z: tuple[float, float]

    @classmethod
    def from_runs(cls, result: small_caps.Comparison, mid: MidCaps) -> SizeOrder:
        return cls(
            closes=(
                result.large_closes.before_costs,
                mid.closes,
                result.small_closes.before_costs,
            ),
            opens=(result.large_opens.before_costs, mid.opens, result.small_opens.before_costs),
            closes_z=(mid.closes_up_z, mid.closes_down_z),
            opens_z=(mid.opens_up_z, mid.opens_down_z),
        )

    @property
    def reading(self) -> str:
        return mid_caps.reading(self.closes, self.opens)


#: The three indexes from the largest companies to the smallest, and where
#: each stands across the board.
INDEXES = ("S&P 500", "S&P 400", "S&P 600")
INDEX_X = (1.9, 4.9, 7.9)
#: A Sharpe ratio ``v`` stands at ``SIZE_Y[0] + SIZE_Y[1] · v``, from 0 to
#: :data:`SIZE_TOP`, the highest the board holds.
SIZE_Y = (1.25, 0.5)
SIZE_TOP = 5.6
SIZE_AXIS_Y = 0.95

#: Where each figure's value sits beside its dot, as an offset across and up
#: and the side it is aligned on, one for each index on each price.
CLOSES_VALUES = ((-0.25, 0.0, "right"), (0.18, -0.32, "left"), (-0.3, 0.3, "right"))
OPENS_VALUES = ((-0.25, 0.0, "right"), (0.0, 0.45, "center"), (0.0, 0.38, "center"))

#: How a falling step's standard errors read in words, rounded.
STEP_WORDS = {1: "one standard error", 2: "two standard errors"}


def _size_y(value: float) -> float:
    """Where a Sharpe ratio stands on the size-order scene."""
    return SIZE_Y[0] + SIZE_Y[1] * value


def _step(gid: str, x0: float, y0: float, x1: float, y1: float, z: float) -> tuple:
    """One step of a price's line, coloured and labelled by what it says.

    A step that falls breaks the predicted order and is red, a step that rises
    beyond one year's noise is green, and one that rises inside it stays black.
    Only the first two carry words, since the post prints no figure for the
    third.
    """
    beyond = abs(z) > small_caps.NOISE_MULTIPLE
    rises = y1 > y0
    if not rises and beyond:
        raise ValueError(f"{gid} falls beyond one year's noise, which the scene has no words for")
    if not rises and round(abs(z)) not in STEP_WORDS:
        raise ValueError(f"{gid} falls by {abs(z):.4f} standard errors, which reads as none")
    if rises != (z > 0):
        raise ValueError(f"{gid}'s standard errors, {z}, do not share its direction")
    color = LOST if not rises else GOOD if beyond else INK
    stroke = _stroke(gid, _line([(x0, y0), (x1, y1)], per_unit=4), color=color, frames=10)
    middle_x, middle_y = (x0 + x1) / 2, (y0 + y1) / 2
    if not rises:
        words = f"breaks the order, about {STEP_WORDS[round(abs(z))]}"
        return stroke, Label(
            words, middle_x + 0.6, max(y0, y1) + 0.4, names=gid, color=LOST, ha="center", size=11
        )
    if beyond:
        return stroke, Label(
            f"{z:.4f} standard errors",
            middle_x - 0.5,
            middle_y + 0.62,
            names=gid,
            color=GOOD,
            ha="center",
            size=11,
        )
    return (stroke,)


def _size_order(order: SizeOrder) -> Scene:
    """The three indexes' Sharpe ratios at both prices, against the predicted rise."""
    for figure in order.closes + order.opens:
        if not 0 <= figure <= SIZE_TOP:
            raise ValueError(f"a Sharpe ratio of {figure} runs off the board")
    ticks = []
    for x in INDEX_X:
        ticks += [(x, SIZE_AXIS_Y), (x, SIZE_AXIS_Y - 0.1), (x, SIZE_AXIS_Y)]
    steps: list[Stroke | Fill | Label] = [
        _stroke(
            "axis",
            _line([(INDEX_X[0] - 0.7, SIZE_AXIS_Y), (INDEX_X[-1] + 0.7, SIZE_AXIS_Y)] + ticks),
            color=MUTED,
            frames=12,
        ),
        *[
            Label(name, x, SIZE_AXIS_Y - 0.4, names="axis", color=MUTED, ha="center", size=11)
            for name, x in zip(INDEXES, INDEX_X, strict=True)
        ],
        _stroke("predicted", _arrow(3.95, 1.15, 4.45, 1.55), color=MUTED, frames=6),
        Label(
            "predicted: rises as the companies get smaller",
            4.65,
            1.3,
            names="predicted",
            color=MUTED,
            size=10,
        ),
        Label(
            "Sharpe ratios before costs",
            INDEX_X[-1] + 0.7,
            0.22,
            names="axis",
            color=MUTED,
            ha="right",
            size=10,
        ),
    ]
    for price, figures, zs, values in (
        ("closes", order.closes, order.closes_z, CLOSES_VALUES),
        ("opens", order.opens, order.opens_z, OPENS_VALUES),
    ):
        ys = [_size_y(f) for f in figures]
        for k, (x, y, figure, (dx, dy, ha)) in enumerate(
            zip(INDEX_X, ys, figures, values, strict=True)
        ):
            gid = f"{price}-{k}"
            if k:
                steps += _step(f"{price}-step-{k}", INDEX_X[k - 1], ys[k - 1], x, y, zs[k - 1])
            steps += [
                _dot(gid, x, y, color=INK),
                Label(f"{figure:.4f}", x + dx, y + dy, names=gid, ha=ha, size=11),
            ]
        steps.append(Label(price, INDEX_X[-1] + 0.27, ys[-1], names=f"{price}-2", size=11))
    steps.append(
        Label(
            "S&P 400: Alpha Vantage files downloaded in 2026",
            0.3,
            0.22,
            names="opens-1",
            color=MUTED,
            size=10,
        )
    )
    return Scene(f"The size order: {order.reading}", "size_order", tuple(steps))


# --- Every scene, paced and written ---------------------------------------------

#: The scenes that build slowly: a label shows on its own for
#: :data:`PACED_LABEL_MS` and the finished drawing holds for
#: :data:`PACED_HOLD_MS`, as :mod:`chan.equity_seasonals_whiteboard` paces its
#: sketches with as many labels.
PACED = ("correlation_narrows", "size_order")
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


def make_khandani_lo_small_caps_whiteboards(
    out_dir: Path | None = None,
    comparison: small_caps.Comparison | None = None,
    mid: MidCaps | None = None,
) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the
    order the post places them: Lesson 3's, then Lesson 6's.

    ``comparison`` is read from the two committed files when it is not handed
    in, and ``mid`` from the S&P 400 run on the owner's archive, about a
    minute. Lesson 3's GIF needs no archive and is written before that read,
    so a refused or missing archive leaves it redrawn and raises from the read.
    """
    folder = out_dir if out_dir is not None else FIGURES_DIR
    comparison = comparison if comparison is not None else small_caps.compare()
    paths = [_write(_correlation_narrows(Narrowing.from_comparison(comparison)), folder)]
    if mid is None:
        mid = MidCaps.from_run(mid_caps.comparison(mid_caps.read()[2]))
    paths.append(_write(_size_order(SizeOrder.from_runs(comparison, mid)), folder))
    return paths


#: The sketches whose figures come from the owner's archive, which a redraw
#: without it leaves stale.
ARCHIVE_SLUGS = ("size_order",)

#: The refusals a redraw can meet in reading the archive, the ones
#: :func:`chan.khandani_lo_mid_caps.main` turns into one line.
REFUSALS = (VintageUnavailable, ArchiveUnavailable, ArchiveRefused, PanelRefused)


def main() -> None:
    try:
        paths = make_khandani_lo_small_caps_whiteboards()
    except REFUSALS as refused:
        # Lesson 3's GIF is already written. The one left stale is named, and
        # the exit is non-zero, so a redraw on a machine without the archive
        # does not read as a full one.
        stale = ", ".join(f"{GIF_PREFIX}{slug}.gif" for slug in ARCHIVE_SLUGS)
        raise SystemExit(f"{stale} was not redrawn: {refused}") from refused
    for path in paths:
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
