"""A whiteboard sketch for the gold miners and oil post, of how the Johansen test reaches its count.

``blog/gold-miners-oil-lessons.md`` says the test reaches its count in steps
and stops at the first hypothesis it cannot reject. Lesson 1 then reports the
three funds' count as exactly one. This module draws that count as one scene,
and the post places it in Lesson 1, right after the list item opening
"3. **The three funds, exactly one.**".

1. Counting stops at the first no. A grey floor carries three slots, labelled
   "r ≤ 0", "r ≤ 1" and "r ≤ 2", one for each hypothesis the test can try on
   three series. Over the first slot a black column stands at the triplet's
   first trace statistic, crossed by a dashed line at its 99 percent bar. A
   green check and the words "rejected: go on" follow. A grey arrow leads to
   the second slot, where a black column stands at the second trace
   statistic, under a dashed line at its own 99 percent bar. Red words say
   "not rejected: stop", and a red note says the statistic falls short even
   of the 90 percent bar. The third slot gets a grey dotted outline labelled
   "not read: the count stopped", and the closing words give the count.

This sketch is not schematic. The two columns and the two dashed lines stand
on one floor at one affine function of their values, and every figure it
prints comes from :class:`CountingStop`, which reads the trace test of
GLD, GDX and USO over the whole span in :mod:`chan.gold_miners_oil` on the
committed vintage. The dotted outline over the third slot is the one mark
whose height is not a figure. The test does compute a third trace statistic,
which :class:`CountingStop` holds as ``unread``, but the count never reads it,
so the sketch draws the slot empty rather than at that value. The 90 percent
bar is named in the red note and not drawn. Figures that would make the
sketch's words false are refused rather than drawn, as
:mod:`chan.etf_cointegration_whiteboard` refuses its own.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so this GIF shares that post's look, frame rate and colours. The
sketch carries more than a reader takes in at that post's pace, so it is in
:data:`PACED`, and :func:`sketch_timeline` holds each label longer and the
finished drawing for twelve seconds, as :mod:`chan.equity_seasonals_whiteboard`
does for its slow sketches. The GIF is named :data:`GIF_PREFIX` plus the
scene's slug, a prefix chosen so no GIF name starts like the post's chart,
``gold_miners_oil_break.png``.

The sketch is deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw it with::

    uv run python -m chan.gold_miners_oil_whiteboard
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from chan.gold_miners_oil import LEVEL, GoldMinersOil, gold_miners_oil, read_sources
from chan.johansen import LEVELS
from chan.paths import FIGURES_DIR
from chan.regime_figure import GOOD, INK, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    Frame,
    Label,
    Scene,
    Stroke,
    _arrow,
    _box,
    _check,
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


#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("counting",)
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


def scenes(stop: CountingStop | None = None) -> tuple[Scene, ...]:
    """The one scene, in a tuple like every other post's sketch module returns.

    ``stop`` defaults to :meth:`CountingStop.read` on the committed vintage.
    """
    return (_counting(stop if stop is not None else CountingStop.read()),)


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
    out_dir: Path | None = None, stop: CountingStop | None = None
) -> list[Path]:
    """Write one looping GIF for each scene and return their paths. ``stop`` is
    read from the committed vintage when it is not handed in."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes(stop)]


def main() -> None:
    for path in make_gold_miners_oil_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
