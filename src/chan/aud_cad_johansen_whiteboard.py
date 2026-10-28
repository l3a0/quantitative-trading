"""Whiteboard sketches for the AUD.USD against CAD.USD post, one for Lesson 2 and one for Lesson 4.

``blog/aud-cad-johansen-lessons.md`` says in Lesson 2 that a constant scale on
either currency's closes cannot reach the returns, and in Lesson 4 what the
top panel of its chart plots. This module draws two scenes, and the post places
each right after the text it draws.

1. Doubling a price changes no return, after Lesson 2's paragraph opening
   "Multiplying every close of one currency by the same constant."
   Yesterday's and today's AUD.USD closes as two bars, an arrow times 2, and
   the same two bars doubled. Then three checked
   steps: today over yesterday is the same percent change; the weight w
   halves, so w times the close equals w over 2 times twice the close, the
   same dollars held; and so every return is identical. A closing line says
   the run with AUD.USD times 2 and CAD.USD times 0.37 still matches all 612 of
   Chan's returns. The sketch is schematic: the bars' heights stand for no
   close in the files. Its only figures are the two scales, read from
   :data:`chan.aud_cad_johansen.SCALE_CHECK`, the constant
   ``tests/test_aud_cad_johansen.py`` runs, and the count of test returns, read
   from the run.
2. What the top panel's share means, after Lesson 4's paragraph opening "That
   day's hedge is one of 612." The last day first: 1 unit of AUD.USD held long
   and −0.7797 units of CAD.USD held short, each times its close, as two bars
   in dollars to scale, which the words call 1 to −0.7622 on 2012-04-26.
   CAD.USD's signed share of the dollars, −0.4325, is a dot on a line from −1
   to 1. Then a dashed mark at −0.5, with two equal bars standing on it,
   AUD.USD long above and CAD.USD short below, where the legs hold equal
   dollars against each other, which is a spread. Then a red band on the line
   from 0 to 1, where both legs are held the same way, and above it a tall
   CAD.USD bar and a short AUD.USD bar side by side on one baseline, both
   long. Every pair draws the line's own convention, AUD.USD held long, which
   flips a day's whole hedge when AUD.USD's position is short. So the words
   say long both, or short both, a bet on the US dollar: the 90 days the hedge
   held both legs the same way were long both on 28 and short both on 62. The
   last day's bars, its dot and its four figures are the run's, from
   :attr:`chan.aud_cad_johansen.AudCad.dollar_split` and
   :attr:`chan.aud_cad_johansen.AudCad.last_hedge`, and the sketch refuses a
   run whose last day was not long AUD.USD and short CAD.USD, which its words
   say. The equal bars and the band's bars are schematic: their heights stand
   for no day's hedge, and the band's pair stands at no particular share.
   Each bar's ends are pulled in by its round cap, so its ink runs exactly
   from end to end and two bars meeting at one base show equal lengths.

Every figure comes from :class:`RunFigures`, which :meth:`RunFigures.from_run`
reads from :func:`chan.aud_cad_johansen.aud_cad` on Chan's committed files.
``tests/test_aud_cad_johansen_whiteboard.py`` reads the same run, so no figure
is typed into a scene.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look and frame rate. Their
colours are :mod:`chan.regime_figure`'s inks, the ones this post's chart,
:mod:`chan.aud_cad_johansen_figures`, still draws in, because the post has not
moved to :mod:`chan.palette`. The band's tint is
:data:`chan.usdcad_tests_whiteboard.REJECT_TINT`, the shared red at the
renderer's lightest blend, for the same reason, and :func:`_write` passes no
inks to :func:`render`, so it draws on the shared ones. The band carries a red
edge, because the tint alone is too pale to read against the white board.
The share sketch prints four of the run's figures and draws three ideas, so
it is in :data:`PACED`: each label shows 900 ms rather than 350, and the
finished drawing holds 12 seconds rather than 4, as :func:`sketch_timeline`
sets. Each GIF is named :data:`GIF_PREFIX` plus the scene's slug, and a redraw
with no change is a no-op diff. Redraw both with::

    uv run python -m chan.aud_cad_johansen_whiteboard
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from chan.aud_cad_johansen import SCALE_CHECK, AudCad, aud_cad, cross_rates, read_sources
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    DPI,
    HEIGHT,
    REJECT_TINT,
    WIDTH,
    XLIM,
    YLIM,
    Fill,
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
GIF_PREFIX = "aud_cad_johansen_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``aud_cad_johansen_share.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


def _signed(value: float, places: int) -> str:
    """``value`` to ``places`` decimals with a typographic minus, as the post prints it."""
    return f"{value:.{places}f}".replace("-", "−")


def _scale(value: float) -> str:
    """A scale as the post writes it, ``2`` rather than ``2.0`` and ``0.37`` as it is."""
    return f"{value:g}"


@dataclass(frozen=True)
class RunFigures:
    """The figures the two sketches print, all from the run on Chan's files.

    ``cad_units`` is the last day's CAD.USD weight with AUD.USD's scaled to 1,
    ``cad_dollars`` the same hedge in dollars at that day's closes, and
    ``share`` CAD.USD's signed share of the dollars with AUD.USD held long.
    ``scales`` is the constant scale Lesson 2 puts on AUD.USD and on CAD.USD.
    ``sides`` is the sign of each leg's position on the last day, AUD.USD then
    CAD.USD, which the words beside the last day's bars name as long or short.
    """

    last_day: pd.Timestamp
    cad_units: float
    cad_dollars: float
    share: float
    test_days: int
    scales: tuple[float, float]
    sides: tuple[int, int] = (1, -1)

    @classmethod
    def from_run(cls, result: AudCad, scales: tuple[float, float] = SCALE_CHECK) -> RunFigures:
        dollars = result.positions[-1] / result.positions[-1, 0]
        return cls(
            last_day=result.test_days[-1],
            cad_units=float(result.last_hedge[1]),
            cad_dollars=float(dollars[1]),
            share=float(result.dollar_split[-1]),
            test_days=len(result.test),
            scales=scales,
            sides=(int(np.sign(result.positions[-1, 0])), int(np.sign(result.positions[-1, 1]))),
        )


def read_figures() -> RunFigures:
    """The run on Chan's committed files, without the report ``run`` prints."""
    sources = read_sources()
    return RunFigures.from_run(aud_cad(cross_rates(sources.audusd[1], sources.usdcad[1])))


#: A bar's line width in points, and the band's edge, thinner than a stroke.
BAR_WIDTH = 9.0
TINT_EDGE = 1.2


def cap(width: float, across: bool) -> float:
    """How far a line's round cap reaches past its end, in board units.

    The cap is half the line's width, in points, out from the end. ``across``
    measures it along the board's width and otherwise along its height. A bar
    drawn from its true ends would reach this far past each, so two bars
    meeting at one base would overlap and look unequal, and a bar's ink would
    not be to scale. :func:`_bar` and :func:`_horizontal` pull each end in by it.
    """
    pixels = width * DPI / 72 / 2
    if across:
        return pixels * (XLIM[1] - XLIM[0]) / WIDTH
    return pixels * (YLIM[1] - YLIM[0]) / HEIGHT


def _bar(gid: str, x: float, base: float, top: float, color: str) -> Stroke:
    """An upright bar whose ink, caps included, runs from ``base`` to ``top``,
    drawn from the base outward."""
    reach = cap(BAR_WIDTH, across=False) * np.sign(top - base)
    xy = _line([(x, base + reach), (x, top - reach)], per_unit=40)
    return _stroke(gid, xy, color=color, width=BAR_WIDTH, frames=4)


# --- Lesson 2: doubling a price changes no return -----------------------------

#: The two closes the bars stand for, in board units, and the bars' baseline.
#: Schematic: any two closes say the same, and today's is drawn a little higher.
YESTERDAY, TODAY = 0.55, 0.68
CLOSES_BASE = 1.3
#: Where the plain pair and the doubled pair stand, yesterday then today.
PLAIN_X = (0.75, 1.7)
DOUBLED_X = (3.05, 4.0)
#: The arrow from the plain pair to the doubled one, and its height.
TIMES_X, TIMES_Y = (2.05, 2.75), 2.0
#: Where the three steps on the right start, and each step's height.
STEPS_X = 5.4
CHANGE_Y, DOLLARS_Y, SAME_Y = 3.6, 2.63, 1.72


def _closes(gid: str, xs: tuple[float, float], scale: float, words: str) -> list:
    """Yesterday's and today's close as two bars, ``scale`` times the plain ones."""
    steps: list = []
    for x, height, day in zip(xs, (YESTERDAY, TODAY), ("yesterday", "today"), strict=True):
        steps += [
            _bar(f"{gid}-{day}", x, CLOSES_BASE, CLOSES_BASE + scale * height, INK),
            Label(
                day, x, CLOSES_BASE - 0.38, names=f"{gid}-{day}", color=MUTED, ha="center", size=10
            ),
        ]
    steps.append(
        Label(
            words, xs[0] - 0.15, CLOSES_BASE + scale * TODAY + 0.38, names=f"{gid}-today", size=12
        )
    )
    return steps


def _no_return_moves(f: RunFigures) -> Scene:
    """Lesson 2: a constant scale on one leg's closes leaves every return as it was."""
    aud_scale, cad_scale = f.scales
    if aud_scale != 2:
        raise ValueError(f"AUD.USD is scaled by {aud_scale}, and the title says it doubles")
    check_x = STEPS_X - 0.5
    times = _scale(aud_scale)
    return Scene(
        "Doubling a price changes no return",
        "no_return_moves",
        (
            *_closes("plain", PLAIN_X, 1.0, "AUD.USD"),
            _stroke(
                "times", _arrow(TIMES_X[0], TIMES_Y, TIMES_X[1], TIMES_Y), color=ACCENT, frames=4
            ),
            Label(
                f"× {times}",
                sum(TIMES_X) / 2,
                TIMES_Y + 0.42,
                names="times",
                color=ACCENT,
                ha="center",
                size=12,
            ),
            *_closes("doubled", DOUBLED_X, aud_scale, f"AUD.USD × {times}"),
            _stroke("same-change", _check(check_x, CHANGE_Y - 0.05), color=GOOD, frames=4),
            Label("today ÷ yesterday:", STEPS_X, CHANGE_Y + 0.17, names="same-change", size=12),
            Label(
                "the same percent change",
                STEPS_X,
                CHANGE_Y - 0.17,
                names="same-change",
                color=GOOD,
                size=12,
            ),
            _stroke("same-dollars", _check(check_x, DOLLARS_Y - 0.05), color=GOOD, frames=4),
            Label("the weight w halves:", STEPS_X, DOLLARS_Y + 0.36, names="same-dollars", size=12),
            Label(
                f"w × close = (w ÷ {times}) × ({times} × close),",
                STEPS_X,
                DOLLARS_Y,
                names="same-dollars",
                size=12,
            ),
            Label(
                "the same dollars held",
                STEPS_X,
                DOLLARS_Y - 0.36,
                names="same-dollars",
                color=GOOD,
                size=12,
            ),
            _stroke("same-return", _check(check_x, SAME_Y - 0.05), color=GOOD, frames=4),
            Label(
                "every return identical",
                STEPS_X,
                SAME_Y,
                names="same-return",
                color=GOOD,
                size=12,
            ),
            Label(
                f"AUD.USD × {times}, CAD.USD × {_scale(cad_scale)}: all {f.test_days} still match",
                9.7,
                0.35,
                names="same-return",
                color=ACCENT,
                ha="right",
                size=14,
            ),
        ),
    )


# --- Lesson 4: what the top panel's share means -------------------------------

#: The share line, from −1 to 1, its height, and how far below it its words sit.
SHARE_X = (0.5, 9.5)
AXIS_Y = 0.8
UNDER = 0.4
#: The last day's two bars in dollars, from their left end, and AUD.USD's length.
DOLLARS_X, DOLLARS_LENGTH = 0.35, 1.25
AUD_Y, CAD_Y, LAST_Y = 3.7, 3.3, 2.9
#: Where the words beside the last day's bars start.
DOLLARS_WORDS_X = 1.9
#: The equal pair stands on the dashed mark at −0.5, from this baseline.
SPREAD_BASE, SPREAD_HALF = 1.75, 0.45
#: The band above 0, and the pair held the same way, standing side by side on
#: one baseline above it, CAD.USD then AUD.USD, at no particular share.
BAND_TOP = 1.3
SAME_BASE = 1.6
SAME_X = (7.55, 7.95)
SAME_HEIGHT = (0.8, 0.3)


def share_x(share: float) -> float:
    """Where a share sits along the line, to scale."""
    left, right = SHARE_X
    return (left + right) / 2 + (right - left) / 2 * share


def _horizontal(gid: str, y: float, length: float, color: str) -> Stroke:
    """A bar whose ink, caps included, lies from :data:`DOLLARS_X` to ``length`` past it."""
    reach = cap(BAR_WIDTH, across=True)
    xy = _line([(DOLLARS_X + reach, y), (DOLLARS_X + length - reach, y)], per_unit=10)
    return _stroke(gid, xy, color=color, width=BAR_WIDTH, frames=4)


def _share(f: RunFigures) -> Scene:
    """Lesson 4: the last day's hedge as a share, a spread at −0.5, and the band above 0."""
    if not -1 < f.share < 0:
        raise ValueError(f"the last day's share is {f.share}, and the sketch draws it below 0")
    if f.sides != (1, -1):
        raise ValueError(
            f"the last day's sides are {f.sides}, and the sketch says long AUD.USD, short CAD.USD"
        )
    left, right = SHARE_X
    zero, equal = share_x(0.0), share_x(-0.5)
    words_x = equal + 0.25
    cad_x, aud_x = SAME_X
    return Scene(
        "What the top panel’s share means",
        "share",
        (
            # The last day: two bars in dollars, to scale, and its share as a dot.
            _horizontal("aud-dollars", AUD_Y, DOLLARS_LENGTH, GOOD),
            Label(
                "AUD.USD: 1 unit × its close, long",
                DOLLARS_WORDS_X,
                AUD_Y,
                names="aud-dollars",
                color=GOOD,
                size=11,
            ),
            _horizontal("cad-dollars", CAD_Y, DOLLARS_LENGTH * -f.cad_dollars, LOST),
            Label(
                f"CAD.USD: {_signed(f.cad_units, 4)} units × its close, short",
                DOLLARS_WORDS_X,
                CAD_Y,
                names="cad-dollars",
                color=LOST,
                size=11,
            ),
            Label(
                f"the last day, {f.last_day.date()}: 1 to {_signed(f.cad_dollars, 4)} in dollars",
                DOLLARS_X,
                LAST_Y,
                names="cad-dollars",
                color=ACCENT,
                size=11,
            ),
            _stroke("axis", _line([(left, AXIS_Y), (right, AXIS_Y)]), color=MUTED, frames=6),
            *(
                Label(text, x, AXIS_Y - UNDER, names="axis", color=MUTED, ha="center", size=11)
                for text, x in (("−1", left), ("0", zero), ("1", right))
            ),
            _dot("last-day", share_x(f.share), AXIS_Y, color=ACCENT),
            Label(
                f"CAD.USD’s share, {_signed(f.share, 4)}",
                share_x(f.share),
                AXIS_Y - UNDER,
                names="last-day",
                color=ACCENT,
                ha="center",
                size=11,
            ),
            # −0.5: equal dollars against each other.
            Stroke(
                "equal",
                np.array([equal, equal]),
                np.array([AXIS_Y, SPREAD_BASE - SPREAD_HALF - 0.1]),
                color=MUTED,
                dashed=True,
                frames=1,
            ),
            _bar("spread-aud", equal, SPREAD_BASE, SPREAD_BASE + SPREAD_HALF, GOOD),
            Label(
                "AUD.USD long",
                equal - 0.32,
                SPREAD_BASE + SPREAD_HALF / 2,
                names="spread-aud",
                color=GOOD,
                ha="right",
                size=11,
            ),
            _bar("spread-cad", equal, SPREAD_BASE, SPREAD_BASE - SPREAD_HALF, LOST),
            Label(
                "CAD.USD short",
                equal - 0.32,
                SPREAD_BASE - SPREAD_HALF / 2,
                names="spread-cad",
                color=LOST,
                ha="right",
                size=11,
            ),
            Label("at −0.5, equal dollars", words_x, 2.15, names="equal", size=10),
            Label("against each other:", words_x, 1.85, names="equal", size=10),
            Label("a spread", words_x, 1.55, names="equal", size=10),
            # Above 0: both legs held the same way.
            Fill("same-way", zero, AXIS_Y, right, BAND_TOP, REJECT_TINT),
            _stroke(
                "same-way-edge",
                _box(zero, AXIS_Y, right, BAND_TOP),
                color=LOST,
                width=TINT_EDGE,
                frames=4,
            ),
            Label(
                "held the same way",
                (zero + right) / 2,
                AXIS_Y - UNDER,
                names="same-way",
                color=LOST,
                ha="center",
                size=11,
            ),
            _stroke(
                "same-base",
                _line([(cad_x - 0.2, SAME_BASE), (aud_x + 0.2, SAME_BASE)]),
                color=MUTED,
                frames=3,
            ),
            _bar("same-cad", cad_x, SAME_BASE, SAME_BASE + SAME_HEIGHT[0], GOOD),
            Label(
                "CAD.USD long",
                cad_x - 0.25,
                SAME_BASE + SAME_HEIGHT[0] - 0.15,
                names="same-cad",
                color=GOOD,
                ha="right",
                size=11,
            ),
            _bar("same-aud", aud_x, SAME_BASE, SAME_BASE + SAME_HEIGHT[1], GOOD),
            Label(
                "AUD.USD long",
                aud_x + 0.35,
                SAME_BASE + SAME_HEIGHT[1] / 2 + 0.1,
                names="same-aud",
                color=GOOD,
                size=11,
            ),
            Label(
                "long both, or short both:",
                9.65,
                3.05,
                names="same-way",
                color=LOST,
                ha="right",
                size=11,
            ),
            Label(
                "a bet on the US dollar",
                9.65,
                2.72,
                names="same-way",
                color=LOST,
                ha="right",
                size=11,
            ),
        ),
    )


def scenes(figures: RunFigures | None = None) -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them, on the run's figures by default."""
    f = read_figures() if figures is None else figures
    return (_no_return_moves(f), _share(f))


#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
PACED = ("share",)
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


def make_aud_cad_johansen_whiteboards(
    out_dir: Path | None = None, figures: RunFigures | None = None
) -> list[Path]:
    """Write both GIFs into ``out_dir``, ``docs/figures`` by default, and return their paths."""
    folder = FIGURES_DIR if out_dir is None else out_dir
    folder.mkdir(parents=True, exist_ok=True)
    return [_write(scene, folder) for scene in scenes(figures)]


def main() -> None:
    for path in make_aud_cad_johansen_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
