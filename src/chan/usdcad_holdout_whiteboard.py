"""The whiteboard sketch in the post on USD.CAD's holdout after Chan's sample.

``blog/usdcad-holdout-lessons.md`` opens its Lesson 1 on a claim that passes
on the sign of a sum and on nothing stronger. The P&L summed over the traded
days is above 0, which is the registered pass mark, while the Newey-West t of
the mean daily P&L sits far below the 1.645 a one-sided test at 5 percent
needs. A reader who has not met a t-statistic gets more from a picture of the
two side by side than from the terms, so this module draws one scene, sketched
stroke by stroke as if on a whiteboard, as a looping GIF the post places right
after the paragraph that opens "The t is 0.2670, far below 1.645".

1. The sign and the t: the sum above 0 with a green check mark, then a t
   gauge with a mark at 0, a red hatched zone right of 1.645 where the mean
   would beat chance, and a brown dot for the run's t far left of that zone.

The gauge is drawn to scale, as Chan's reading is in
:mod:`chan.usdcad_tests_whiteboard`, whose layout it copies. The line maps the
span from 0 to the critical value, with a quarter of that span added at each
end, onto the board, so every position on it is an
affine function of the value it marks. Every number it prints is read rather
than written in. The sum is :attr:`chan.usdcad_holdout.Holdout.total_pnl`, the
t is the run's Newey-West t, the critical value is
:data:`chan.usdcad_holdout.NEWEY_WEST_CRITICAL`, and the zone's 5 percent is
the normal tail beyond that value. The 0 is the pass mark itself. A run whose
figures would make the words false is refused rather than drawn: a sum at or
below 0 would turn the check mark false, a t at or below 0 would put the dot
left of the 0 tick that a positive sum implies it sits right of, and a t at or
past the critical value would leave the dot inside the zone the sketch says it
falls short of.

The strokes, the timeline and the renderer are
:mod:`chan.usdcad_tests_whiteboard`'s, so an edit there changes this GIF too,
and that module's docstring explains why two draws on one machine give the
same bytes. Redraw it with::

    uv run python -m chan.usdcad_holdout_whiteboard
"""

from __future__ import annotations

from pathlib import Path

from scipy.stats import norm

from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, LOST
from chan.series import WindowCrossesScaleBreak
from chan.usdcad_holdout import NEWEY_WEST_CRITICAL, Holdout, HoldoutRefused, read_holdout
from chan.usdcad_tests_whiteboard import (
    Label,
    Scene,
    Stroke,
    _check,
    _dot,
    _hatched,
    _line,
    _stroke,
    render,
    timeline,
)
from chan.vintage import VintageUnavailable

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "usdcad_holdout_"

#: The height of the line the sum sits on with its check mark.
SUM_Y = 3.5
#: The gauge's height on the board, and where its line starts and ends.
LEVEL = 1.4
LINE_X = (0.5, 9.6)
#: The board span the marks are mapped onto, inside the line's ends.
SCALE_X = (0.9, 9.2)


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``usdcad_holdout_sign_and_t.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


def _level(critical: float) -> str:
    """The one-sided level a critical value of the normal rejects at, such as ``5%``."""
    return f"{norm.sf(critical):.0%}"


def _sign_and_t(total_pnl: float, t: float, critical: float = NEWEY_WEST_CRITICAL) -> Scene:
    """Lesson 1's verdict: the sum passes its mark of 0, and the t falls short of its own.

    A check mark says the sum is above 0, and the dot's place says the t is
    above 0 and short of the zone, so a run that breaks any of those is refused.
    """
    if total_pnl <= 0:
        raise ValueError(
            f"The sign and the t checks the sum off as above 0, and this run's is {total_pnl:.6f}"
        )
    if t <= 0:
        raise ValueError(
            f"The sign and the t draws the t right of 0, as a positive sum implies, "
            f"and this run's is {t:.6f}"
        )
    if t >= critical:
        raise ValueError(
            f"The sign and the t draws the t short of its critical value of {critical:.3f}, "
            f"and this run's is {t:.6f}"
        )
    marks = [0.0, t, critical]
    span = max(marks) - min(marks)
    low, high = min(marks) - span / 4, max(marks) + span / 4
    left, right = SCALE_X

    def at(value: float) -> float:
        return left + (value - low) / (high - low) * (right - left)

    zero, edge, dot = at(0.0), at(critical), at(t)
    below, zone = LEVEL - 0.55, (LEVEL + 0.25, LEVEL + 0.95)
    steps: tuple[Stroke | Label, ...] = (
        _stroke("check", _check(3.05, SUM_Y), color=GOOD, frames=3),
        Label(f"sum {total_pnl:.4f} > 0", 2.85, SUM_Y, names="check", ha="right", color=GOOD),
        _stroke("line", _line([(LINE_X[0], LEVEL), (LINE_X[1], LEVEL)]), frames=8),
        _stroke("tick-zero", _line([(zero, LEVEL - 0.18), (zero, LEVEL + 0.18)]), frames=3),
        Label("0", zero, below, names="tick-zero", ha="center"),
        _stroke("tick-critical", _line([(edge, LEVEL - 0.18), (edge, zone[1] + 0.1)]), frames=3),
        Label(f"{critical:.3f}", edge, below, names="tick-critical", ha="center"),
        _stroke(
            "zone", _hatched(edge, zone[0], LINE_X[1], zone[1]), color=LOST, width=1.4, frames=10
        ),
        Label(
            f"beats chance, one-sided {_level(critical)}",
            LINE_X[1],
            zone[1] + 0.45,
            names="zone",
            ha="right",
            color=LOST,
        ),
        _dot("t", dot, LEVEL),
        Label(f"t = {t:.4f}", dot, LEVEL + 0.45, names="t", ha="center", color=ACCENT),
        Label("mean daily P&L", dot, LEVEL + 0.9, names="t", ha="center", color=ACCENT, size=12),
    )
    return Scene("The sign and the t", "sign_and_t", steps)


def scenes(holdout: Holdout) -> tuple[Scene, ...]:
    """The post's one scene, its numbers read from ``holdout``."""
    return (_sign_and_t(holdout.total_pnl, holdout.newey_west.t_newey_west),)


def make_usdcad_holdout_whiteboards(
    out_dir: Path | None = None, holdout: Holdout | None = None
) -> list[Path]:
    """Write one looping GIF for each scene and return their paths.

    ``holdout`` is read from the committed vintage through
    :func:`chan.usdcad_holdout.read_holdout` when it is not handed in, so its
    refusals and scale-break guard run here too.
    """
    holdout = holdout if holdout is not None else read_holdout()
    folder = out_dir if out_dir is not None else FIGURES_DIR
    paths = []
    for scene in scenes(holdout):
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
        paths.append(path)
    return paths


def main() -> None:
    try:
        paths = make_usdcad_holdout_whiteboards()
    except (VintageUnavailable, HoldoutRefused, WindowCrossesScaleBreak) as refused:
        # As in chan.usdcad_holdout_figures.main, a refusal that names the
        # source or the flagged day reaches the operator as one line.
        raise SystemExit(str(refused)) from refused
    for path in paths:
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
