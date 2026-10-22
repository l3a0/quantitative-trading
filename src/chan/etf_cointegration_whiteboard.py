"""Whiteboard sketches for the post on Chan's Johansen test on three ETFs.

``blog/johansen-etf-lessons.md`` explains the Johansen test on EWA, EWC and
IGE, and two of its lessons turn on an idea a picture shows faster than the
words. This module draws two scenes, and the post places each right after the
paragraph it draws.

1. Weak pieces add up, in Lesson 3 after the paragraph that opens
   "The first eigenvalue alone is not strong enough". Two columns stand on one
   floor, to one scale. The left is the eigen test for r ≤ 0: one block of
   16.897 that stops short of its 90 percent bar at 18.893. The right is the
   trace test for r ≤ 0: the same block with 13.061 and 4.471 stacked on it,
   for 34.429, which clears its 95 percent bar at 29.796. Each bar is labelled
   with its level, because the two columns compare different confidence
   levels. The 99 percent bars are left out. Every figure comes from
   :class:`TraceStack`, read from the triplet's Johansen test in
   :mod:`chan.etf_cointegration` on the committed vintage. Figures that would
   make its words false are refused rather than drawn.
2. The test's two relations span every portfolio, in Lesson 4 after the
   paragraph that opens "Chan reads the two relations as two hedge ratios". It
   is schematic and carries none of the run's figures. A plane of shares of
   EWA across and shares of EWC up holds two arrows for the pair's two
   relations, pointing different ways, and a dashed parallelogram builds EWA
   held alone from the two. Its closing words state the test's claim
   as a condition, "if both relations revert, so does EWA alone", because the
   post calls the claim a tension the run does not settle: a plain ADF test on
   EWA alone does not reject a unit root. Each arrow falls in the quadrant of
   the run's eigenvector, up to its sign: relation 1 is long one ETF and short
   the other, and relation 2 is long both. Their lengths and angles are
   schematic.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied: its strokes, labels, timeline, renderer and palette, so these
GIFs share that post's look, frame rate, pace and colours. Only the scenes and
the file names are this module's. Each GIF is named :data:`GIF_PREFIX` plus
the scene's slug.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw both with::

    uv run python -m chan.etf_cointegration_whiteboard
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from chan.etf_cointegration import EtfCointegration, etf_cointegration, read_sources
from chan.johansen import LEVELS
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    Label,
    Scene,
    _arrow,
    _box,
    _line,
    _stroke,
    render,
    timeline,
)

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "etf_cointegration_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``etf_cointegration_trace_stack.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


class StackRefused(ValueError):
    """Figures that would make the trace-stack sketch's words false."""


@dataclass(frozen=True)
class TraceStack:
    """What the trace-stack sketch draws, each field read from one Johansen test.

    - ``pieces``: the eigen statistics for r ≤ 0, r ≤ 1 and r ≤ 2, which the
      trace statistic for r ≤ 0 adds up.
    - ``trace``: the trace statistic for r ≤ 0.
    - ``eigen_bar``: the eigen test's 90 percent critical value for r ≤ 0.
    - ``trace_bar``: the trace test's 95 percent critical value for r ≤ 0.

    The sketch says the first piece falls short of its bar and the stack
    clears its own, and draws the stack's top at ``trace``. Figures for which
    any of the three is false are refused.
    """

    pieces: tuple[float, float, float]
    trace: float
    eigen_bar: float
    trace_bar: float

    def __post_init__(self) -> None:
        if abs(sum(self.pieces) - self.trace) > 1e-9 * max(1.0, abs(self.trace)):
            raise StackRefused(f"the pieces {self.pieces} do not add up to the trace {self.trace}")
        if not self.pieces[0] < self.eigen_bar:
            raise StackRefused(f"the first piece {self.pieces[0]} clears its bar {self.eigen_bar}")
        if not self.trace > self.trace_bar:
            raise StackRefused(f"the stack {self.trace} does not clear its bar {self.trace_bar}")

    @classmethod
    def from_run(cls, result: EtfCointegration) -> TraceStack:
        """The triplet's test, EWC, EWA and IGE, at the levels the sketch names."""
        triplet = result.triplet
        return cls(
            pieces=tuple(float(v) for v in triplet.eigen[:3]),
            trace=float(triplet.trace[0]),
            eigen_bar=float(triplet.eigen_critical[0, LEVELS.index(90)]),
            trace_bar=float(triplet.trace_critical[0, LEVELS.index(95)]),
        )

    @classmethod
    def read(cls, data_dir: Path | None = None) -> TraceStack:
        """Read the committed vintage the way ``python -m chan.etf_cointegration``
        does, scale-break guard included, without printing its report."""
        _, closes = read_sources(data_dir)
        return cls.from_run(etf_cointegration(closes))


#: Where the stack sketch's floor sits, and board units per unit of statistic.
FLOOR = 0.75
SCALE = 0.095
#: Each column's left and right edges.
EIGEN_X = (0.75, 2.35)
TRACE_X = (5.95, 7.55)


def _up(value: float) -> float:
    """The height a statistic of ``value`` reaches above the floor."""
    return FLOOR + SCALE * value


def _trace_stack(f: TraceStack) -> Scene:
    """The eigen test's one piece against the trace test's stack of three."""
    first, second, third = f.pieces
    e0, e1 = EIGEN_X
    t0, t1 = TRACE_X
    mid_e, mid_t = (e0 + e1) / 2, (t0 + t1) / 2
    eigen_bar, trace_bar = _up(f.eigen_bar), _up(f.trace_bar)
    return Scene(
        "Weak pieces add up",
        "trace_stack",
        (
            _stroke("floor", _line([(0.5, FLOOR), (9.5, FLOOR)]), color=MUTED, frames=6),
            _stroke("eigen-1", _box(e0, FLOOR, e1, _up(first)), frames=8),
            Label(f"{first:.3f}", mid_e, _up(first / 2), names="eigen-1", ha="center", size=12),
            Label("eigen test, r ≤ 0", mid_e, 0.4, names="eigen-1", ha="center", size=12),
            _stroke(
                "eigen-bar",
                _line([(0.7, eigen_bar), (e1 + 0.3, eigen_bar)]),
                dashed=True,
                width=2.6,
                frames=4,
            ),
            Label(
                f"90% eigen bar, {f.eigen_bar:.3f}",
                e1 + 0.5,
                eigen_bar,
                names="eigen-bar",
                size=11,
            ),
            Label("falls short", e1 + 0.5, eigen_bar - 0.45, names="eigen-bar", color=LOST),
            _stroke(
                "same", _arrow(e1 + 0.15, _up(first / 2), t0 - 0.15, _up(first / 2)), color=MUTED
            ),
            Label(
                "the same piece",
                (e1 + t0) / 2,
                _up(first / 2) - 0.33,
                names="same",
                color=MUTED,
                ha="center",
                size=11,
            ),
            _stroke("trace-1", _box(t0, FLOOR, t1, _up(first)), frames=8),
            Label(f"{first:.3f}", mid_t, _up(first / 2), names="trace-1", ha="center", size=12),
            Label("trace test, r ≤ 0", mid_t, 0.4, names="trace-1", ha="center", size=12),
            _stroke(
                "trace-2", _box(t0, _up(first), t1, _up(first + second)), color=ACCENT, frames=8
            ),
            Label(
                f"+ {second:.3f}",
                mid_t,
                _up(first + second / 2),
                names="trace-2",
                color=ACCENT,
                ha="center",
                size=12,
            ),
            _stroke(
                "trace-3",
                _box(t0, _up(first + second), t1, _up(first + second + third)),
                color=ACCENT,
                frames=6,
            ),
            Label(
                f"+ {third:.3f}",
                t1 + 0.2,
                _up(first + second + third / 2),
                names="trace-3",
                color=ACCENT,
                size=12,
            ),
            _stroke(
                "trace-bar",
                _line([(t0 - 0.6, trace_bar), (t1, trace_bar)]),
                dashed=True,
                width=2.6,
                frames=4,
            ),
            Label(
                f"95% trace bar, {f.trace_bar:.3f}",
                t0 - 0.8,
                trace_bar,
                names="trace-bar",
                ha="right",
                size=11,
            ),
            Label(
                f"{f.trace:.3f} clears it",
                t1 + 0.2,
                _up(f.trace) + 0.25,
                names="trace-bar",
                color=GOOD,
            ),
        ),
    )


#: The plane's origin, and where each arrow of the two-relations sketch ends.
#: The two relations point different ways, and EWA alone is their sum, the
#: far corner of the parallelogram they make. Relation 1, the pair's first
#: eigenvector, is long one ETF and short the other, so it points down and to
#: the right. Relation 2 is long both, so it points up and to the right. The
#: lengths and angles are schematic.
ORIGIN = (1.4, 2.2)
RELATION_1 = (3.2, 1.0)
RELATION_2 = (3.6, 3.4)
EWA_ALONE = (
    RELATION_1[0] + RELATION_2[0] - ORIGIN[0],
    RELATION_1[1] + RELATION_2[1] - ORIGIN[1],
)


def _two_relations() -> Scene:
    """EWA held alone, built from the pair's two relations."""
    ox, oy = ORIGIN
    (ax, ay), (bx, by), (tx, ty) = RELATION_1, RELATION_2, EWA_ALONE
    return Scene(
        "The test’s two relations span every portfolio",
        "two_relations",
        (
            _stroke("ewa-axis", _line([(0.6, oy), (7.4, oy)]), color=MUTED, frames=6),
            Label("shares of EWA", 7.6, oy, names="ewa-axis", color=MUTED, size=12),
            _stroke("ewc-axis", _line([(ox, 0.3), (ox, 3.9)]), color=MUTED, frames=6),
            Label("shares of EWC", ox + 0.2, 3.85, names="ewc-axis", color=MUTED, size=12),
            _stroke("relation-1", _arrow(ox, oy, ax, ay), width=2.6, frames=6),
            Label("relation 1", ax, ay - 0.35, names="relation-1", ha="center", size=12),
            _stroke("relation-2", _arrow(ox, oy, bx, by), width=2.6, frames=6),
            Label("relation 2", bx + 0.1, by + 0.3, names="relation-2", size=12),
            _stroke(
                "mix", _line([(ax, ay), (tx, ty), (bx, by)]), color=MUTED, dashed=True, frames=8
            ),
            Label(
                "a mix of relations 1 and 2",
                (ax + tx) / 2 + 0.35,
                (ay + ty) / 2 - 0.3,
                names="mix",
                color=MUTED,
                size=12,
            ),
            _stroke("ewa", _arrow(ox, oy, tx, ty), color=ACCENT, width=3.5, frames=6),
            Label("EWA alone", tx + 0.2, ty + 0.35, names="ewa", color=ACCENT, size=12),
            Label(
                "if both relations revert, so does EWA alone",
                9.7,
                0.4,
                names="ewa",
                ha="right",
            ),
        ),
    )


def scenes(stack: TraceStack) -> tuple[Scene, ...]:
    """Both scenes, in the order the post reads them."""
    return _trace_stack(stack), _two_relations()


def _write(scene: Scene, folder: Path) -> Path:
    frames = timeline(scene)
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


def make_etf_cointegration_whiteboards(
    out_dir: Path | None = None, stack: TraceStack | None = None
) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the
    order the post reads them. ``stack`` is read from the committed vintage
    when it is not handed in."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    stack = stack if stack is not None else TraceStack.read()
    return [_write(scene, folder) for scene in scenes(stack)]


def main() -> None:
    for path in make_etf_cointegration_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
