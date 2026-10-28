"""Whiteboard sketches for the PCA factor momentum post, one for Lesson 1 and one for Lesson 5.

``blog/pca-factor-momentum-lessons.md`` makes two claims a sentence has to
build in the reader's head: tomorrow's weights are fitted on a window that
already holds today's return, and PMC's one large return takes the first
factor's place, so the factor that is usually first lands second. This module
draws the two as scenes, and the post places each right after the paragraph
it draws.

1. Tomorrow's own weights have already seen today's return, in Lesson 1: a day
   axis from t − 252 to t + 1 with today's and tomorrow's returns as dots, and
   three brackets over it. Day t's weights, black, cover the 252 days to
   t − 1. Day t+1's weights, red, cover the 252 days to t, so their right end
   sits on today's return. Tomorrow's weights fitted on 251 days that leave
   today out, brass, run from the red bracket's left end to the black
   bracket's right end. Its foot prints PC2's statistic on tomorrow's own
   weights, matched, on the weights that leave today out, and the pair the
   test reads, and in grey on the 251 days that still hold today. It sits
   after the paragraph opening "The window closes that gap."
2. PMC takes PC1, so the usual PC1 lands in PC2, in Lesson 5: three slots
   for PC1, PC2 and PC3, with the usual PC1 in the first slot without PMC.
   With PMC, a box that is mostly PMC takes the first slot on the days
   PMC carries PC1, and an arrow carries the usual PC1 down into the second.
   Beside the slots, PC2's squared products on 2007-08-09 and 2007-08-10
   stand as two red bars beside one grey bar for the other days together, all
   to one scale. Its foot gives the two days' share of PC1's squared products
   without PMC, and PC2's statistic with PMC and without. It sits after the
   paragraph opening "A return of 186.54 percent dominates any window that
   holds it."

Neither is schematic in its figures. Every number either prints is read from
the run, through :class:`Window` and :class:`RankShift`, and the rank shift's
bars stand at each day's share of PC2's squared products. The window
sketch's axis is not to scale, since it skips from t − 251 to t − 1, and the
slots carry no figure of their own. ``tests/test_pca_factor_momentum_whiteboard.py``
pins what each draws, and ``test_the_whiteboard_draws_this_runs_figures`` in
``tests/test_pca_factor_momentum.py`` holds that the run gives the figures it
pins.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look and frame rate. They draw
in the shared inks, as the post's chart does. Each sketch carries more than a
reader takes in at that post's pace, so both are in :data:`PACED`, and
:func:`sketch_timeline` holds each of their labels longer and their finished
drawings for twelve seconds, as :mod:`chan.equity_seasonals_whiteboard` does
for its slow sketches. Each GIF is named :data:`GIF_PREFIX` plus the scene's
slug, a prefix no other file in ``docs/figures`` starts with.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. A redraw runs the decompositions the post's
figures come from, about a minute::

    uv run python -m chan.pca_factor_momentum_whiteboard
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from chan.paths import FIGURES_DIR
from chan.pca_factor import LOOKBACK, SMALL_CAPS, SPLICED
from chan.pca_factor_momentum import (
    NAMES,
    Decomposition,
    Results,
    WeightStatistics,
    compute_both,
    daily_components,
    file_returns,
    largest_loading,
    share_of_largest,
    weight_statistics,
    windows_holding,
)
from chan.regime_figure import ACCENT, INK, LOST, MUTED
from chan.series import load_panel
from chan.usdcad_tests_whiteboard import (
    Frame,
    Label,
    Scene,
    Stroke,
    _arrow,
    _box,
    _dot,
    _line,
    _span,
    _stroke,
    render,
    timeline,
)

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "pca_factor_momentum_sketch_"

#: The factor both sketches print, which is PC2.
FACTOR = NAMES.index("PC2")


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``pca_factor_momentum_sketch_window.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


def _signed(value: float) -> str:
    """``value`` to four decimals with a typographic minus, as the post prints it."""
    return f"{value:.4f}".replace("-", "−")


# --- Lesson 1: tomorrow's own weights have already seen today's return ---------


@dataclass(frozen=True)
class Window:
    """PC2's statistic as the window sketch prints it, each pairing today's
    factor return on today's weights with tomorrow's return read another way.

    - ``matched``: on tomorrow's own weights, fitted on the 252 days ending
      today, with sign and rank matched to today's.
    - ``left_out``: on tomorrow's weights fitted on the 251 days before today,
      which leave today's return out, then matched.
    - ``shortened``: on tomorrow's weights fitted on the 251 days ending
      today, which still hold today's return, then matched.
    - ``paired``: on today's weights, the pair the test reads.
    """

    matched: float
    left_out: float
    shortened: float
    paired: float

    @classmethod
    def from_run(cls, results: Results, weights: WeightStatistics) -> Window:
        return cls(
            matched=float(weights.matched[FACTOR]),
            left_out=float(weights.left_out[FACTOR]),
            shortened=float(weights.shortened[FACTOR]),
            paired=float(results.spliced.comparison.factors[FACTOR]),
        )


#: Each bracket's window as the rows it covers, counted from day t, first and
#: last. :func:`chan.pca_factor_momentum.decompose` fits day t's weights on the
#: ``LOOKBACK`` rows before row t, so day t+1's own weights cover the rows to
#: t, and ``weight_statistics`` fits the weights that leave today out on the
#: ``LOOKBACK - 1`` rows before row t.
BRACKETS = {
    "today": (-LOOKBACK, -1),
    "tomorrow": (-(LOOKBACK - 1), 0),
    "left-out": (-(LOOKBACK - 1), -1),
}
#: Where each day the axis marks sits across the board, counted from day t.
#: The axis skips the days between t − 251 and t − 1, so it is not to scale.
DAY_X = {-LOOKBACK: 0.9, -(LOOKBACK - 1): 1.9, -1: 6.3, 0: 7.3, 1: 8.3}
#: Where the axis's skipped days are marked, between t − 251 and t − 1.
SKIP_X = 4.1
#: The axis's height, and each bracket's, top to bottom.
DAY_AXIS_Y = 1.6
#: How far below the axis each day's name sits, and how far above it the two
#: returns' names sit.
TICK_WORDS_BELOW, DOT_WORDS_ABOVE = 0.42, 0.4
BRACKET_Y = {"today": 3.55, "tomorrow": 2.79, "left-out": 2.03}
#: How far above its bracket a bracket's words sit, and how tall its end ticks are.
WORDS_ABOVE, BRACKET_TICK = 0.38, 0.08
#: How close the left-out figure must come to the pair's for the sketch to
#: print "≈" between them. The post calls the largest gap on that row, 0.0039,
#: close.
CLOSE = 0.005
#: Where the foot's two columns start, and the heights of its two rows.
WINDOW_FOOT_X, WINDOW_FOOT_Y = (0.3, 6.0), (0.85, 0.45)


def _day(offset: int) -> str:
    """A day's name on the axis, such as "t − 252", "t" or "t + 1"."""
    if offset == 0:
        return "t"
    return f"t {'+' if offset > 0 else '−'} {abs(offset)}"


def _window(w: Window) -> Scene:
    """Lesson 1: three windows over one day axis, and PC2 read on each."""
    if not abs(w.left_out - w.paired) < CLOSE:
        raise ValueError(
            f"the sketch prints the left-out figure {w.left_out} as close to the pair's "
            f"{w.paired}, and they are {abs(w.left_out - w.paired)} apart"
        )
    ticks = []
    for offset in sorted(DAY_X):
        x = DAY_X[offset]
        ticks += [(x, DAY_AXIS_Y), (x, DAY_AXIS_Y - 0.12), (x, DAY_AXIS_Y)]
    left, right = min(DAY_X.values()) - 0.4, max(DAY_X.values()) + 0.5
    steps: list[Stroke | Label] = [
        _stroke(
            "axis",
            _line([(left, DAY_AXIS_Y)] + ticks + [(right, DAY_AXIS_Y)]),
            color=MUTED,
            frames=10,
        ),
        *[
            Label(
                _day(offset),
                DAY_X[offset],
                DAY_AXIS_Y - TICK_WORDS_BELOW,
                names="axis",
                color=MUTED,
                size=10,
                ha="center",
            )
            for offset in sorted(DAY_X)
        ],
        Label(
            "…",
            SKIP_X,
            DAY_AXIS_Y - TICK_WORDS_BELOW,
            names="axis",
            color=MUTED,
            size=10,
            ha="center",
        ),
        _dot("today-return", DAY_X[0], DAY_AXIS_Y, color=INK),
        Label(
            "today",
            DAY_X[0],
            DAY_AXIS_Y + DOT_WORDS_ABOVE,
            names="today-return",
            size=11,
            ha="center",
        ),
        _dot("tomorrow-return", DAY_X[1], DAY_AXIS_Y, color=INK),
        Label(
            "tomorrow",
            DAY_X[1],
            DAY_AXIS_Y + DOT_WORDS_ABOVE,
            names="tomorrow-return",
            size=11,
            ha="center",
        ),
    ]
    words = {
        "today": (f"day t’s weights: {LOOKBACK} days to t − 1", INK),
        "tomorrow": (f"day t+1’s weights: {LOOKBACK} days to t", LOST),
        "left-out": (f"tomorrow’s weights, {LOOKBACK - 1} days, today left out", ACCENT),
    }
    for gid, (first, last) in BRACKETS.items():
        text, color = words[gid]
        x0, x1, y = DAY_X[first], DAY_X[last], BRACKET_Y[gid]
        steps += [
            _stroke(gid, _span(x0, x1, y, tick=BRACKET_TICK), color=color, frames=8),
            Label(text, x0, y + WORDS_ABOVE, names=gid, color=color, size=11),
        ]
        if gid == "tomorrow":
            steps += [
                Label("already holds", x1 + 0.2, y + 0.15, names=gid, color=color, size=10),
                Label("today’s return", x1 + 0.2, y - 0.15, names=gid, color=color, size=10),
            ]
    steps += [
        Label(
            f"PC2: tomorrow’s own weights, matched {_signed(w.matched)}",
            WINDOW_FOOT_X[0],
            WINDOW_FOOT_Y[0],
            names="tomorrow",
            color=LOST,
            size=11,
        ),
        Label(
            f"→ today left out {_signed(w.left_out)}",
            WINDOW_FOOT_X[1],
            WINDOW_FOOT_Y[0],
            names="left-out",
            color=ACCENT,
            size=11,
        ),
        Label(
            f"≈ the pair {_signed(w.paired)}",
            WINDOW_FOOT_X[1],
            WINDOW_FOOT_Y[1],
            names="today",
            size=11,
        ),
        Label(
            f"{LOOKBACK - 1} days that hold today: {_signed(w.shortened)}",
            WINDOW_FOOT_X[0],
            WINDOW_FOOT_Y[1],
            names="tomorrow",
            color=MUTED,
            size=10,
        ),
    ]
    return Scene("Tomorrow’s own weights have seen today’s return", "window", tuple(steps))


# --- Lesson 5: PMC takes PC1, so the usual PC1 lands in PC2 --------------------


@dataclass(frozen=True)
class RankShift:
    """What the rank shift sketch prints, from the run with PMC and without.

    - ``weights``: the smallest and largest weight PC1 puts on PMC on the days
      PMC carries PC1.
    - ``span``: the first and last of those days.
    - ``days``: the two days that carry PC2's statistic.
    - ``shares``: each of those days' share of the sum of PC2's squared
      products, in the order of ``days``.
    - ``others``: how many pair days there are besides those two.
    - ``without_share``: the same two days' share of PC1's squared products
      without PMC.
    - ``paired`` and ``without``: PC2's statistic with PMC and without.
    """

    weights: tuple[float, float]
    span: tuple[str, str]
    days: tuple[str, str]
    shares: tuple[float, float]
    others: int
    without_share: float
    paired: float
    without: float

    @property
    def share(self) -> float:
        """The two days' share of PC2's squared products together."""
        return sum(self.shares)

    @classmethod
    def from_run(
        cls, closes: pd.DataFrame, components: list[Decomposition], results: Results
    ) -> RankShift:
        """Read from the file's closes, every fitting day's decomposition and both runs.

        PMC's one large return is its largest, and the days PMC carries PC1
        are the pair days whose window holds that return and whose largest
        weight on PMC is PC1's. They are the first days in a row, so the span
        is their first and last.
        """
        returns = file_returns(closes)
        column = closes.columns.get_loc(SPLICED)
        row = int(np.nanargmax(returns[:, column]))
        holding = windows_holding(components[:-1], row)
        largest = [largest_loading(d, column) for d in holding]
        carriers = [k for _, k in largest]
        first = next((i for i, k in enumerate(carriers) if k != 0), len(carriers))
        if not first or 0 in carriers[first:]:
            raise ValueError("the sketch draws PMC on PC1 on the first days that hold its return")
        sizes = [size for size, _ in largest[:first]]
        names = [str(closes.index[d.end].date()) for d in holding[:first]]

        def products(result, factor: int) -> np.ndarray:
            pairs = result.pairs
            return pairs.today[:, factor] * pairs.tomorrow[:, factor]

        pairs = results.spliced.pairs
        spliced = products(results.spliced, FACTOR)
        share, at = share_of_largest(spliced, 2)
        squares = spliced**2
        without_share, without_at = share_of_largest(products(results.unspliced, 0), 2)
        days = tuple(str(pairs.days[i].date()) for i in at)
        without_days = tuple(str(results.unspliced.pairs.days[i].date()) for i in without_at)
        if without_days != days:
            raise ValueError(
                f"the sketch says the same two days carry PC1 without PMC, and they are "
                f"{without_days} rather than {days}"
            )
        return cls(
            weights=(float(min(sizes)), float(max(sizes))),
            span=(names[0], names[-1]),
            days=days,
            shares=tuple(float(squares[i] / squares.sum()) for i in at),
            others=len(pairs.days) - len(at),
            without_share=float(without_share),
            paired=float(results.spliced.comparison.factors[FACTOR]),
            without=float(results.unspliced.comparison.factors[FACTOR]),
        )


#: Each slot's height, PC1 to PC3, and the height of the shelf under it. PC3
#: holds no box, so its slot is shallower.
SLOT_Y = (3.08, 2.03, 1.25)
SHELF_Y = (2.55, 1.5, 0.98)
#: The two columns of slots, without PMC and with it, from left to right, and
#: the height of the words over each.
WITHOUT_X, WITH_X = (1.0, 2.8), (3.1, 6.1)
HEADER_Y = 3.88
#: How far a box reaches above and below its slot's height, and how far above
#: and below it the PMC box's two lines sit.
BOX_HALF, PMC_LINES = 0.48, (0.16, -0.17)
#: The bars' baseline, the board height of a share of 1, and where each bar
#: stands: the other days together, then the two days in the order of
#: :attr:`RankShift.days`. Each bar's name sits under the baseline.
BARS_BASE, SHARE_SCALE = 1.5, 2.4
BAR_X = (7.15, 8.4, 9.3)
BAR_WIDTH, NAMES_BELOW = 9.0, 0.36
#: Where the share's two lines start, and their heights.
SHARE_X, SHARE_Y = 6.55, (3.3, 2.98)
#: The heights of the sketch's two closing lines.
SHIFT_FOOT_Y = (0.62, 0.27)


def _percent(share: float) -> str:
    return f"{100 * share:.2f}%"


def _month_day(day: str) -> str:
    """A date's month and day, such as "08-10" for "2007-08-10"."""
    return day[5:]


def _rank_shift(r: RankShift) -> Scene:
    """Lesson 5: PMC takes the first slot and the usual PC1 moves to the second."""
    if not all(r.span[0] <= day <= r.span[1] for day in r.days):
        raise ValueError(
            f"the sketch says PMC carries PC1 on {r.days}, and it carries it {r.span[0]} "
            f"to {r.span[1]}"
        )
    years = {day[:4] for day in (*r.span, *r.days)}
    if len(years) != 1:
        raise ValueError(f"the sketch writes every day after the first without its year {years}")
    steps: list[Stroke | Label] = []
    for k, (y, shelf) in enumerate(zip(SLOT_Y, SHELF_Y, strict=True)):
        gid = f"shelf-{k}"
        steps += [
            _stroke(
                gid,
                _line([(WITHOUT_X[0] - 0.05, shelf), (WITH_X[1] + 0.05, shelf)]),
                color=MUTED,
                width=1.5,
                frames=4,
            ),
            Label(NAMES[k], 0.3, y, names=gid, size=12),
        ]
    middle_a, middle_b = sum(WITHOUT_X) / 2, sum(WITH_X) / 2
    steps += [
        _stroke(
            "usual-without",
            _box(WITHOUT_X[0], SLOT_Y[0] - BOX_HALF, WITHOUT_X[1], SLOT_Y[0] + BOX_HALF),
            color=INK,
            frames=6,
        ),
        Label("usual PC1", middle_a, SLOT_Y[0], names="usual-without", size=11, ha="center"),
        Label(
            "without PMC",
            middle_a,
            HEADER_Y,
            names="usual-without",
            color=MUTED,
            size=11,
            ha="center",
        ),
    ]
    lo, hi = r.weights
    steps += [
        _stroke(
            "pmc",
            _box(WITH_X[0], SLOT_Y[0] - BOX_HALF, WITH_X[1], SLOT_Y[0] + BOX_HALF),
            color=ACCENT,
            frames=6,
        ),
        Label(
            "mostly PMC",
            middle_b,
            SLOT_Y[0] + PMC_LINES[0],
            names="pmc",
            color=ACCENT,
            size=11,
            ha="center",
        ),
        Label(
            f"weight {lo:.4f} to {hi:.4f}",
            middle_b,
            SLOT_Y[0] + PMC_LINES[1],
            names="pmc",
            color=ACCENT,
            size=10,
            ha="center",
        ),
        Label(
            f"with PMC: days {r.span[0]} to {_month_day(r.span[1])}",
            WITH_X[0],
            HEADER_Y,
            names="pmc",
            size=11,
        ),
    ]
    usual_b = (WITH_X[0], WITH_X[0] + WITHOUT_X[1] - WITHOUT_X[0])
    steps += [
        _stroke(
            "push",
            _arrow(
                WITHOUT_X[1] + 0.05,
                SLOT_Y[0] - BOX_HALF - 0.05,
                WITH_X[0] - 0.05,
                SLOT_Y[1] + 0.1,
            ),
            color=INK,
            frames=5,
        ),
        _stroke(
            "usual-with",
            _box(usual_b[0], SLOT_Y[1] - BOX_HALF, usual_b[1], SLOT_Y[1] + BOX_HALF),
            color=INK,
            frames=6,
        ),
        Label("usual PC1", sum(usual_b) / 2, SLOT_Y[1], names="usual-with", size=11, ha="center"),
        _stroke(
            "baseline",
            _line([(BAR_X[0] - 0.45, BARS_BASE), (BAR_X[-1] + 0.4, BARS_BASE)]),
            color=MUTED,
            width=1.5,
            frames=4,
        ),
    ]
    heights = (1 - r.share, *r.shares)
    colors = (MUTED, LOST, LOST)
    for k, (x, height, color) in enumerate(zip(BAR_X, heights, colors, strict=True)):
        steps.append(
            _stroke(
                f"bar-{k}",
                _line([(x, BARS_BASE), (x, BARS_BASE + SHARE_SCALE * height)], per_unit=40),
                color=color,
                width=BAR_WIDTH,
                frames=3,
            )
        )
    under = BARS_BASE - NAMES_BELOW
    steps += [
        Label(
            f"{r.others} other days",
            BAR_X[0],
            under,
            names="bar-0",
            color=MUTED,
            size=10,
            ha="center",
        ),
        *[
            Label(
                _month_day(day),
                BAR_X[k + 1],
                under,
                names=f"bar-{k + 1}",
                color=LOST,
                size=10,
                ha="center",
            )
            for k, day in enumerate(r.days)
        ],
        Label(
            f"{_percent(r.share)} of PC2’s", SHARE_X, SHARE_Y[0], names="bar-2", color=LOST, size=11
        ),
        Label("squared products", SHARE_X, SHARE_Y[1], names="bar-2", color=LOST, size=11),
        Label(
            f"without PMC: the same two days, {_percent(r.without_share)} of PC1’s",
            0.3,
            SHIFT_FOOT_Y[0],
            names="bar-2",
            color=MUTED,
            size=10,
        ),
        Label(
            f"PC2: {_signed(r.paired)} with PMC → {_signed(r.without)} without",
            0.3,
            SHIFT_FOOT_Y[1],
            names="bar-2",
            size=11,
        ),
    ]
    return Scene("PMC takes PC1, so the usual PC1 lands in PC2", "rank_shift", tuple(steps))


# --- Drawing ------------------------------------------------------------------

#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("window", "rank_shift")
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


def scenes(window: Window, rank_shift: RankShift) -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them, Lesson 1's then Lesson 5's."""
    return (_window(window), _rank_shift(rank_shift))


def run_figures() -> tuple[Window, RankShift]:
    """Both sketches' figures, from the run on Chan's S&P 600 file, about a minute."""
    _, closes = load_panel(SMALL_CAPS, field="Close")
    returns = file_returns(closes)
    components = daily_components(returns)
    results = compute_both(closes)
    weights = weight_statistics(returns, components)
    return Window.from_run(results, weights), RankShift.from_run(closes, components, results)


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


def make_pca_factor_momentum_whiteboards(
    out_dir: Path | None = None, figures: tuple[Window, RankShift] | None = None
) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order.

    ``figures`` is read from the run by :func:`run_figures` when it is not
    handed in.
    """
    folder = out_dir if out_dir is not None else FIGURES_DIR
    window, rank_shift = figures if figures is not None else run_figures()
    return [_write(scene, folder) for scene in scenes(window, rank_shift)]


def main() -> None:
    for path in make_pca_factor_momentum_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
