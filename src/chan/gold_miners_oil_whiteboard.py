"""Whiteboard sketches for the gold miners and oil post: the Johansen count, and what it cannot say.

``blog/gold-miners-oil-lessons.md`` says the test reaches its count in steps
and stops at the first hypothesis it cannot reject, reports the three funds'
count as exactly one, and then asks in Lesson 3 which funds that one relation
needs. This module draws two scenes, and the post places each right after the
text it draws.

1. Counting stops at the first no, in Lesson 1 after the list item opening
   "3. **The three funds, exactly one.**". A grey floor carries three slots,
   labelled "r ≤ 0", "r ≤ 1" and "r ≤ 2", one for each hypothesis the test
   can try on three series. Over the first slot a black column stands at the
   triplet's first trace statistic, crossed by a dashed line at its 99
   percent bar. A green check and the words "rejected: go on" follow. A grey
   arrow leads to the second slot, where a black column stands at the second
   trace statistic, under a dashed line at its own 99 percent bar. Red words
   say "not rejected: stop", and a red note says the statistic falls short
   even of the 90 percent bar. The third slot gets a grey dotted outline
   labelled "not read: the count stopped", and the closing words give the
   count.
2. One relation, three pairs, in Lesson 3 after the paragraph opening "Gold
   and oil alone find nothing". Three black dots in a triangle stand for GLD,
   GDX and USO, with grey words inside saying the three funds hold one
   relation. Each edge is one pair tested alone over the same days and
   carries that pair's first trace statistic. GLD and GDX, then GLD and USO,
   are red dashed edges marked "none", and GDX and USO is a green solid edge
   marked "one at 99%". A grey note gives the pairs' shared 99 percent bar,
   and brown words say a count of one cannot say which pair the relation is.
   The last two notes are the zero-weight tests on the triplet's relation:
   GLD's weight set to zero is rejected, in green, and USO's is not, in red.

Neither sketch is schematic. In the first, the two columns and the two dashed
lines stand on one floor at one affine function of their values, and every
figure it prints comes from :class:`CountingStop`, which reads the trace test
of GLD, GDX and USO over the whole span in :mod:`chan.gold_miners_oil` on the
committed vintage. The dotted outline over the third slot is the one mark
whose height is not a figure. The test does compute a third trace statistic, which
:class:`CountingStop` holds as ``unread``, but the count never reads it, so
the sketch draws the slot empty rather than at that value. The 90 percent bar
is named in the red note and not drawn. In the second, every figure it prints
comes from :class:`PairsAndWeights`, read from the same run's control, its two
pairs with USO and its zero-weight tests. Its triangle's shape and the
lengths of its edges carry no figure. Figures that would make either sketch's
words false are refused rather than drawn, as
:mod:`chan.etf_cointegration_whiteboard` refuses its own.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look, frame rate and colours.
Each sketch carries more than a reader takes in at that post's pace, so both
are in :data:`PACED`, and :func:`sketch_timeline` holds each label longer and
the finished drawing for twelve seconds, as
:mod:`chan.equity_seasonals_whiteboard` does for its slow sketches. Each GIF
is named :data:`GIF_PREFIX` plus the scene's slug, a prefix chosen so no GIF
name starts like the post's chart, ``gold_miners_oil_break.png``.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw both with::

    uv run python -m chan.gold_miners_oil_whiteboard
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from chan.gold_miners_oil import (
    CHI2_1,
    GDX,
    GLD,
    LEVEL,
    USO,
    GoldMinersOil,
    gold_miners_oil,
    read_sources,
)
from chan.johansen import LEVELS
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    Frame,
    Label,
    Scene,
    Stroke,
    _arrow,
    _box,
    _check,
    _dot,
    _line,
    _stroke,
    render,
    timeline,
)

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "gold_miners_oil_sketch_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``gold_miners_oil_sketch_counting.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


class CountRefused(ValueError):
    """Figures that would make the counting sketch's words false."""


@dataclass(frozen=True)
class CountingStop:
    """What the counting sketch draws, each field read from the triplet's trace test.

    - ``first`` and ``second``: the trace statistics for r ≤ 0 and r ≤ 1.
    - ``first_bar`` and ``second_bar``: their critical values at the 99
      percent level the claim names.
    - ``second_bar_90``: the critical value for r ≤ 1 at 90 percent, the
      lowest level the test reports.
    - ``unread``: the trace statistic for r ≤ 2, which the test computes and
      the count never reads.
    - ``count``: the relations the trace test finds at 99 percent.

    The sketch says the first statistic is rejected, the second is not, the
    second falls short even of its 90 percent bar, and the count is one.
    Figures for which any of those is false are refused.
    """

    first: float
    second: float
    first_bar: float
    second_bar: float
    second_bar_90: float
    unread: float
    count: int

    def __post_init__(self) -> None:
        if not self.first > self.first_bar:
            raise CountRefused(f"the first statistic {self.first} does not clear {self.first_bar}")
        if self.second > self.second_bar:
            raise CountRefused(f"the second statistic {self.second} clears {self.second_bar}")
        if self.second > self.second_bar_90:
            raise CountRefused(
                f"the second statistic {self.second} clears its 90% bar {self.second_bar_90}"
            )
        if self.count != 1:
            raise CountRefused(f"the count is {self.count}, and the sketch stops after one")

    @classmethod
    def from_run(cls, result: GoldMinersOil) -> CountingStop:
        """GLD, GDX and USO over the whole span, on the trace statistic."""
        triplet = result.triplet
        at = LEVELS.index(LEVEL)
        return cls(
            first=float(triplet.trace[0]),
            second=float(triplet.trace[1]),
            first_bar=float(triplet.trace_critical[0, at]),
            second_bar=float(triplet.trace_critical[1, at]),
            second_bar_90=float(triplet.trace_critical[1, LEVELS.index(90)]),
            unread=float(triplet.trace[2]),
            count=triplet.relations("trace", LEVEL),
        )

    @classmethod
    def read(cls, data_dir: Path | None = None) -> CountingStop:
        """Read the committed vintage the way ``python -m chan.gold_miners_oil``
        does, scale-break guard included, without printing its report."""
        _, closes = read_sources(data_dir)
        return cls.from_run(gold_miners_oil(closes))


#: Where the floor sits, and board units per unit of statistic.
FLOOR = 0.8
SCALE = 0.065
#: Each slot's centre, and half a column's width.
SLOTS = (1.3, 4.4, 8.6)
HALF = 0.65
#: The height of the dotted outline over the third slot, which is not a figure.
OUTLINE_TOP = 1.5


def up(value: float) -> float:
    """The height a statistic of ``value`` reaches above the floor."""
    return FLOOR + SCALE * value


def _relations(count: int) -> str:
    return f"count: {count} relation{'' if count == 1 else 's'}"


def _counting(f: CountingStop) -> Scene:
    """The trace test's count on three funds: one rejection, then a stop."""
    s1, s2, s3 = SLOTS
    bar1, bar2 = up(f.first_bar), up(f.second_bar)
    slots: list[Stroke | Label] = [
        Label(text, x, FLOOR - 0.38, names="floor", color=MUTED, size=12, ha="center")
        for text, x in zip(("r ≤ 0", "r ≤ 1", "r ≤ 2"), SLOTS, strict=True)
    ]
    return Scene(
        "Counting stops at the first no",
        "counting",
        (
            _stroke("floor", _line([(0.4, FLOOR), (9.6, FLOOR)]), color=MUTED, frames=6),
            *slots,
            _stroke("column-1", _box(s1 - HALF, FLOOR, s1 + HALF, up(f.first)), color=INK),
            Label(f"{f.first:.3f}", s1, up(f.first / 2), names="column-1", size=12, ha="center"),
            _stroke(
                "bar-1",
                _line([(s1 - HALF - 0.2, bar1), (s1 + HALF + 0.2, bar1)]),
                color=INK,
                dashed=True,
                width=2.6,
                frames=4,
            ),
            Label(f"99% bar, {f.first_bar:.3f}", s1 + HALF + 0.4, bar1, names="bar-1", size=11),
            _stroke("check", _check(s1 + HALF + 0.4, bar1 - 0.55), color=GOOD, frames=4),
            Label(
                "rejected: go on",
                s1 + HALF + 0.95,
                bar1 - 0.5,
                names="check",
                color=GOOD,
                size=12,
            ),
            _stroke(
                "on",
                _arrow(s1 + HALF + 0.2, 1.25, s2 - HALF - 0.2, 1.25),
                color=MUTED,
                frames=6,
            ),
            _stroke(
                "column-2",
                _box(s2 - HALF, FLOOR, s2 + HALF, up(f.second)),
                color=INK,
                frames=6,
            ),
            Label(
                f"{f.second:.3f}", s2, up(f.second) + 0.35, names="column-2", size=12, ha="center"
            ),
            _stroke(
                "bar-2",
                _line([(s2 - HALF - 0.2, bar2), (s2 + HALF + 0.2, bar2)]),
                color=INK,
                dashed=True,
                width=2.6,
                frames=4,
            ),
            Label(f"99% bar, {f.second_bar:.3f}", s2 + HALF + 0.4, bar2, names="bar-2", size=11),
            Label(
                "not rejected: stop",
                s2 + HALF + 0.4,
                bar2 + 0.5,
                names="column-2",
                color=LOST,
                size=12,
            ),
            Label(
                f"short even of the\n90% bar, {f.second_bar_90:.3f}",
                s2 + HALF + 0.4,
                1.45,
                names="bar-2",
                color=LOST,
                size=11,
            ),
            Stroke(
                "unread",
                *_box(s3 - HALF, FLOOR, s3 + HALF, OUTLINE_TOP)[:2],
                color=MUTED,
                frames=6,
                dots=2.5,
            ),
            Label(
                "not read:\nthe count stopped",
                s3,
                OUTLINE_TOP + 0.5,
                names="unread",
                color=MUTED,
                size=11,
                ha="center",
            ),
            Label(_relations(f.count), 9.7, 4.3, names="unread", size=14, ha="right"),
        ),
    )


# --- Lesson 3: one relation, three pairs ----------------------------------------


class PairsRefused(ValueError):
    """Figures that would make the three-pairs sketch's words false."""


@dataclass(frozen=True)
class PairsAndWeights:
    """What the three-pairs sketch draws, each field read from one run.

    - ``gld_gdx``, ``gld_uso`` and ``gdx_uso``: each pair's first trace
      statistic over the triplet's days, the first being the control.
    - ``counts``: the relations each pair's trace test finds at 90 and at 99
      percent, in that order, keyed like the three statistics.
    - ``pair_bar``: the trace test's 99 percent bar for r ≤ 0 on two series,
      which every pair shares.
    - ``triplet_count``: the relations the triplet's trace test finds at 99
      percent.
    - ``gld_weight`` and ``uso_weight``: the zero-weight test's statistics for
      GLD and for USO in the triplet's relation.
    - ``weight_bar`` and ``weight_bar_90``: that test's bars at 95 and at 90
      percent, chi-squared with one degree of freedom.

    The sketch says the triplet holds one relation, that GLD and GDX and GLD
    and USO find none at any level the test reports, that GDX and USO find one
    at 99 percent, that GLD's zero weight is rejected, and that USO's is not
    rejected at any level. Figures for which any of those is false are
    refused.
    """

    gld_gdx: float
    gld_uso: float
    gdx_uso: float
    counts: dict[str, tuple[int, int]]
    pair_bar: float
    triplet_count: int
    gld_weight: float
    uso_weight: float
    weight_bar: float
    weight_bar_90: float

    def __post_init__(self) -> None:
        if self.triplet_count != 1:
            raise PairsRefused(f"the triplet finds {self.triplet_count} relations, not one")
        for pair in ("gld_gdx", "gld_uso"):
            if self.counts[pair] != (0, 0):
                raise PairsRefused(f"{pair} finds {self.counts[pair]} relations at 90 and 99%")
        if self.counts["gdx_uso"][1] != 1:
            raise PairsRefused(f"gdx_uso finds {self.counts['gdx_uso'][1]} relations at 99%")
        if not self.gld_weight > self.weight_bar:
            raise PairsRefused(f"GLD's weight {self.gld_weight} does not clear {self.weight_bar}")
        if not self.uso_weight < self.weight_bar_90:
            raise PairsRefused(f"USO's weight {self.uso_weight} clears {self.weight_bar_90}")

    @classmethod
    def from_run(cls, result: GoldMinersOil) -> PairsAndWeights:
        """The control, the two pairs with USO and the triplet's zero-weight tests."""
        tests = {
            "gld_gdx": result.control,
            "gld_uso": result.with_oil[GLD],
            "gdx_uso": result.with_oil[GDX],
        }
        at = LEVELS.index(LEVEL)
        bars = {float(test.trace_critical[0, at]) for test in tests.values()}
        if len(bars) != 1:
            raise PairsRefused(f"the pairs' 99% bars differ: {sorted(bars)}")
        return cls(
            gld_gdx=float(tests["gld_gdx"].trace[0]),
            gld_uso=float(tests["gld_uso"].trace[0]),
            gdx_uso=float(tests["gdx_uso"].trace[0]),
            counts={
                name: (test.relations("trace", 90), test.relations("trace", LEVEL))
                for name, test in tests.items()
            },
            pair_bar=bars.pop(),
            triplet_count=result.triplet.relations("trace", LEVEL),
            gld_weight=float(result.zero_weight[GLD]),
            uso_weight=float(result.zero_weight[USO]),
            weight_bar=CHI2_1[95],
            weight_bar_90=CHI2_1[90],
        )

    @classmethod
    def read(cls, data_dir: Path | None = None) -> PairsAndWeights:
        """Read the committed vintage the way ``python -m chan.gold_miners_oil``
        does, scale-break guard included, without printing its report."""
        _, closes = read_sources(data_dir)
        return cls.from_run(gold_miners_oil(closes))


#: Where each fund's dot sits. The triangle's shape carries no figure.
FUNDS = {"gld": (3.4, 3.35), "gdx": (1.0, 0.95), "uso": (5.8, 0.95)}
#: How far each edge stops short of the dots at its ends.
TRIM = 0.25
#: Where the notes on the right start.
NOTES_X = 6.6


def _edge(gid: str, one: str, other: str, color: str, dashed: bool) -> Stroke:
    """A line from one fund's dot to another's, stopping :data:`TRIM` short of both."""
    (x0, y0), (x1, y1) = FUNDS[one], FUNDS[other]
    length = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
    dx, dy = (x1 - x0) / length * TRIM, (y1 - y0) / length * TRIM
    return _stroke(
        gid,
        _line([(x0 + dx, y0 + dy), (x1 - dx, y1 - dy)], per_unit=8),
        color=color,
        dashed=dashed,
        width=2.6,
        frames=6,
    )


def _three_pairs(f: PairsAndWeights) -> Scene:
    """Lesson 3: the triplet's one relation, each pair alone, and the weights."""
    (gx, gy), (dx, dy), (ux, uy) = FUNDS["gld"], FUNDS["gdx"], FUNDS["uso"]
    return Scene(
        "One relation, three pairs",
        "three_pairs",
        (
            _dot("gld", gx, gy, color=INK),
            Label("GLD", gx, gy + 0.42, names="gld", size=13, ha="center"),
            _dot("gdx", dx, dy, color=INK),
            Label("GDX", dx, dy - 0.4, names="gdx", size=13, ha="center"),
            _dot("uso", ux, uy, color=INK),
            Label("USO", ux, uy - 0.4, names="uso", size=13, ha="center"),
            Label(
                "three funds,\none relation",
                gx,
                1.6,
                names="uso",
                color=MUTED,
                size=11,
                ha="center",
            ),
            _edge("gld-gdx", "gld", "gdx", LOST, dashed=True),
            Label(
                f"{f.gld_gdx:.3f}: none",
                (gx + dx) / 2 - 0.35,
                (gy + dy) / 2 + 0.15,
                names="gld-gdx",
                color=LOST,
                size=12,
                ha="right",
            ),
            _edge("gld-uso", "gld", "uso", LOST, dashed=True),
            Label(
                f"{f.gld_uso:.3f}: none",
                (gx + ux) / 2 + 0.35,
                (gy + uy) / 2 + 0.15,
                names="gld-uso",
                color=LOST,
                size=12,
            ),
            _edge("gdx-uso", "gdx", "uso", GOOD, dashed=False),
            Label(
                f"{f.gdx_uso:.3f}: one at 99%",
                gx,
                dy - 0.4,
                names="gdx-uso",
                color=GOOD,
                size=12,
                ha="center",
            ),
            Label(
                f"pair bar at 99%: {f.pair_bar:.3f}",
                NOTES_X,
                3.6,
                names="gdx-uso",
                color=MUTED,
                size=11,
            ),
            Label(
                "a count of one cannot\nsay which pair it is",
                NOTES_X,
                2.85,
                names="gdx-uso",
                color=ACCENT,
                size=12,
            ),
            Label(
                f"GLD’s weight 0?\n{f.gld_weight:.3f}: rejected",
                NOTES_X,
                1.95,
                names="gld",
                color=GOOD,
                size=11,
            ),
            Label(
                f"USO’s weight 0?\n{f.uso_weight:.3f}: not rejected",
                NOTES_X,
                1.05,
                names="uso",
                color=LOST,
                size=11,
            ),
        ),
    )


#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("counting", "three_pairs")
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


def scenes(
    stop: CountingStop | None = None, pairs: PairsAndWeights | None = None
) -> tuple[Scene, ...]:
    """Both scenes, in the order the post reads them, Lesson 1's then Lesson 3's.

    ``stop`` and ``pairs`` default to their ``read`` on the committed vintage.
    """
    return (
        _counting(stop if stop is not None else CountingStop.read()),
        _three_pairs(pairs if pairs is not None else PairsAndWeights.read()),
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


def make_gold_miners_oil_whiteboards(
    out_dir: Path | None = None,
    stop: CountingStop | None = None,
    pairs: PairsAndWeights | None = None,
) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the
    post's order. ``stop`` and ``pairs`` are read from the committed vintage
    when they are not handed in."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes(stop, pairs)]


def main() -> None:
    for path in make_gold_miners_oil_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
