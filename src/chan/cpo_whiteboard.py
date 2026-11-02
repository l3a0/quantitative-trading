"""Whiteboard sketches for the Conditional Parameter Optimization post's rule and its Lesson 2.

``blog/conditional-parameter-optimization-lessons.md`` makes two claims a
reader has to picture from sentences: the strategy enters past the entry
threshold and exits before the z-score gets back to 0, and Chan's annual
returns cannot reach his cumulative ones whichever way an annual return is
read. This module draws the two as scenes, and the post places each right
after the passage it draws.

1. The entry and exit rule, under "The strategy, the grid and the bars", after
   the numbered list that ends on the bars and before the paragraph opening
   "The book does not say how to line up the two funds’ bars". A z-score path
   runs against dashed lines at +entry and −entry, dashed brass lines at +0.6
   and −0.6 times the entry, and a grey line at 0. It falls below −entry and
   the rule buys GLD, rises back above −0.6 times the entry and the rule exits the long, rises above
   +entry and the rule shorts GLD, and falls back below +0.6 times the entry
   and the rule exits the short. A dot on the path marks each of the four
   events, and a grey guide drops from each to a strip of the position held,
   long, flat or short. A line at the top says each exit comes before the
   z-score reaches 0, and the last line, under the title, gives the grid's
   lowest entry and the lines it puts the rule at.
2. Chan's annual returns against his cumulative ones, in Lesson 2, after the
   paragraph opening "The other common definition of an annual return is
   arithmetic". For the fixed arm, a black staircase compounds one dollar at
   17.29% a year to 61.4% over three years, a step at each year's end, marked
   year 1 to year 3. A dashed brass ceiling at 68.0% is
   the most three years of daily returns averaging an arithmetic 17.29% a year
   can compound to. A red mark at the book's printed 73% sits above both, and
   a red bracket from the ceiling to it says how far the ceiling falls short,
   as "68.0% still short of 73%". A grey note gives
   the re-chosen arm's three figures.

The first sketch is schematic and carries no figures from the run. Its path is
a made-up curve at an entry of 1, and its thresholds come from constants a
clone checks: :data:`chan.cpo.EXIT_FRACTION` sets the exit lines, and the
position strip is :func:`chan.cpo.positions` run on the drawn path, so the
strip changes exactly where the code's rule says. Its last line reads the
grid's lowest entry from :data:`chan.cpo.ENTRY_THRESHOLDS`. It draws no round
trip count and says nothing about why the chosen cell trades as often as it
does.

The second sketch is not schematic, and it needs no bars. Every figure it
prints is computed here from Chan's printed figures in
:data:`chan.cpo.BOOK_UNCONDITIONAL` and :data:`chan.cpo.BOOK_CONDITIONAL`, the
compounded figure by :func:`compounded` and the ceiling by
:func:`arithmetic_ceiling`, and each height on it is an affine function of a
dollar's value. ``tests/test_cpo.py`` pins the same figures in
``test_chan_s_annual_returns_do_not_compound_to_his_cumulative_ones`` and
``test_chan_s_annual_returns_read_as_arithmetic_cannot_reach_them_either``.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look and frame rate. They draw in
the shared colours of :mod:`chan.regime_figure`, as the post's chart does.
Each sketch carries more than a reader takes in at that post's pace, so both
are in :data:`PACED`, and :func:`sketch_timeline` holds each of their labels
longer and their finished drawings for twelve seconds, as
:mod:`chan.equity_seasonals_whiteboard` does for its slow sketches. Each GIF
is named :data:`GIF_PREFIX` plus the scene's slug, a prefix chosen so no GIF
name starts like the post's chart, ``cpo_cells.png``.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw both with::

    uv run python -m chan.cpo_whiteboard
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator

from chan import cpo
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    Frame,
    Label,
    Scene,
    Stroke,
    _dot,
    _line,
    _stroke,
    render,
    timeline,
)

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "cpo_sketch_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``cpo_sketch_rule.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


# --- The strategy, the grid and the bars: the entry and exit rule -------------

#: The schematic entry threshold the first sketch draws its lines at. Any
#: positive entry gives the same picture in units of the entry.
ENTRY = 1.0
#: The height of a z-score of 0, and the board units per unit of z-score.
ZERO_Y, PER_Z = 2.55, 1.0
#: Where the level lines start and end, and where their names end at left.
LEVEL_X = (2.45, 9.0)
NAMES_X = 2.25
#: The made-up path's knots, as (board x, z-score in units of the entry). It
#: dips below −entry, climbs past +entry, and settles between 0 and +0.6 times
#: the entry, so it crosses each of the four lines in the order the rule needs.
KNOTS = (
    (2.5, 0.25),
    (3.25, -0.6),
    (3.95, -1.3),
    (5.35, 0.0),
    (6.75, 1.15),
    (7.75, 0.7),
    (8.8, 0.3),
)
#: How many points the path is drawn and run through the rule with.
SAMPLES = 400
#: The position strip's height, its words' height, and the rows its event
#: words sit on: under −entry for the long's events, over +entry for the short's.
STRIP_Y, STRIP_WORDS_Y = 0.68, 0.3
LONG_WORDS_Y, SHORT_WORDS_Y = 1.08, 4.03
#: How far an event's words sit to one side of its guide.
WORDS_OFF = 0.2
#: Where the line saying each exit comes before 0 sits, ending at the board's
#: right, and where the grid's closing line sits, under the title.
BEFORE_X, BEFORE_Y = 9.7, 4.47
GRID_X, GRID_Y = 0.3, 3.88
#: The word for each position and its ink. A held position is a thick bar and
#: a flat one a thin grey line, so the width is a second cue beside the colour.
WORD = {1: "long", -1: "short", 0: "flat"}
WORD_INK = {"long": GOOD, "short": LOST, "flat": MUTED}
BAR_WIDTH, FLAT_WIDTH = 7.0, 2.2


def z_y(z: float) -> float:
    """A z-score's height on the first sketch, in units of the entry."""
    return ZERO_Y + z * PER_Z


def z_path() -> tuple[np.ndarray, np.ndarray]:
    """The schematic z-score path, as board x and z-score in units of the entry."""
    xs, zs = zip(*KNOTS, strict=True)
    x = np.linspace(xs[0], xs[-1], SAMPLES)
    return x, PchipInterpolator(xs, zs)(x)


def held(z: np.ndarray) -> np.ndarray:
    """The position :func:`chan.cpo.positions` holds after each point of ``z``,
    as one day that starts flat."""
    first = np.zeros(len(z), dtype=bool)
    first[0] = True
    return cpo.positions(z * ENTRY, ENTRY, first)


@dataclass(frozen=True)
class Event:
    """A point where the rule changes the position: its index on the path, and
    the position before and after it."""

    at: int
    before: int
    after: int

    @property
    def name(self) -> str:
        if self.after == 1:
            return "buy GLD"
        if self.after == -1:
            return "short GLD"
        return f"exit {WORD[self.before]}"

    @property
    def ink(self) -> str:
        return {1: GOOD, -1: LOST}.get(self.after, ACCENT)


def events(position: np.ndarray) -> list[Event]:
    """Every point where ``position`` changes, in order."""
    changes = np.flatnonzero(np.diff(position)) + 1
    return [Event(int(k), int(position[k - 1]), int(position[k])) for k in changes]


def _level(gid: str, z: float, name: str, ink: str) -> list[Stroke | Label]:
    """A line across the plot at z-score ``z``, dashed unless it is 0, with its name at left."""
    y = z_y(z)
    return [
        _stroke(
            gid,
            _line([(LEVEL_X[0], y), (LEVEL_X[1], y)]),
            color=ink,
            dashed=bool(z),
            width=1.5,
            frames=4,
        ),
        Label(name, NAMES_X, y, names=gid, color=ink, size=11, ha="right"),
    ]


def _stretch(k: int, x0: float, x1: float, word: str) -> list[Stroke | Label]:
    """One stretch of the position strip, a bar from ``x0`` to ``x1``, and its word."""
    gid = f"held-{k}"
    return [
        _stroke(
            gid,
            _line([(x0, STRIP_Y), (x1, STRIP_Y)], per_unit=10),
            color=WORD_INK[word],
            width=FLAT_WIDTH if word == "flat" else BAR_WIDTH,
            frames=3,
        ),
        Label(
            word,
            (x0 + x1) / 2,
            STRIP_WORDS_Y,
            names=gid,
            color=WORD_INK[word],
            size=11,
            ha="center",
        ),
    ]


def _event(k: int, event: Event, x: np.ndarray, z: np.ndarray) -> list[Stroke | Label]:
    """An event's dot on the path, its grey guide down to the strip, and its words.

    The long's words sit under −entry, the long's entry before its guide so
    they miss the dip beyond it. The short's sit over +entry, after their
    guides, where the peak stays low enough to clear them.
    """
    ex, ey = float(x[event.at]), z_y(float(z[event.at]))
    words_y = LONG_WORDS_Y if 1 in (event.before, event.after) else SHORT_WORDS_Y
    before = event.after == 1
    return [
        _dot(f"event-{k}", ex, ey, color=event.ink),
        _stroke(
            f"guide-{k}",
            _line([(ex, ey), (ex, STRIP_Y + 0.12)], per_unit=10),
            color=MUTED,
            dashed=True,
            width=1.0,
            frames=3,
        ),
        Label(
            event.name,
            ex - WORDS_OFF if before else ex + WORDS_OFF,
            words_y,
            names=f"event-{k}",
            color=event.ink,
            size=11,
            ha="right" if before else "left",
        ),
    ]


def _rule() -> Scene:
    """The strategy's rule on a made-up z-score path, with the position it holds."""
    x, z = z_path()
    position = held(z)
    found = events(position)
    inner = f"{-cpo.EXIT_FRACTION:g} × entry"
    steps: list[Stroke | Label] = [
        *_level("zero", 0.0, "0", MUTED),
        *_level("entry-high", 1.0, "+entry", INK),
        *_level("entry-low", -1.0, "−entry", INK),
        *_level("exit-high", -cpo.EXIT_FRACTION, f"+{inner}", ACCENT),
        *_level("exit-low", cpo.EXIT_FRACTION, f"−{inner}", ACCENT),
        _stroke("z", (x, ZERO_Y + z * PER_Z), color=INK, width=2.4, frames=16),
        Label("z-score", x[-1] + 0.25, z_y(float(z[-1])), names="z", color=INK, size=11),
    ]
    starts = [0, *(e.at for e in found)]
    ends = [*(e.at for e in found), len(x) - 1]
    for k, (a, b) in enumerate(zip(starts, ends, strict=True)):
        if k:
            steps += _event(k - 1, found[k - 1], x, z)
        steps += _stretch(k, float(x[a]), float(x[b]), WORD[int(position[a])])
        if k == 0:
            steps.append(
                Label(
                    "position", NAMES_X, STRIP_Y, names="held-0", color=MUTED, size=11, ha="right"
                )
            )
    lowest = min(cpo.ENTRY_THRESHOLDS)
    steps += [
        Label(
            "each exit comes before the z-score reaches 0",
            BEFORE_X,
            BEFORE_Y,
            names=f"event-{len(found) - 1}",
            color=ACCENT,
            size=11,
            ha="right",
        ),
        Label(
            f"lowest entry {lowest:g}: lines at ±{lowest:g}, ±{-cpo.EXIT_FRACTION * lowest:g}",
            GRID_X,
            GRID_Y,
            names="exit-high",
            color=MUTED,
            size=11,
        ),
    ]
    return Scene("The entry and exit rule", "rule", tuple(steps))


# --- Lesson 2: the annual returns against the cumulative ones -----------------

#: The test years Chan prints both figures over.
YEARS = 3


def compounded(annual: float, years: int = YEARS) -> float:
    """What ``annual`` compounds to over ``years``, less the dollar."""
    return (1 + annual) ** years - 1


def arithmetic_ceiling(annual: float, years: int = YEARS) -> float:
    """The most ``years`` of daily returns averaging an arithmetic ``annual``
    a year can compound to, less the dollar.

    Each day's growth factor ``1 + r`` is at most ``exp(r)``, so the product
    over the days is at most the exponential of their sum, ``years · annual``.
    """
    return math.exp(years * annual) - 1


@dataclass(frozen=True)
class Arm:
    """One of Chan's two columns: his printed annual and cumulative returns."""

    annual: float
    printed: float

    @property
    def compounded(self) -> float:
        return compounded(self.annual)

    @property
    def ceiling(self) -> float:
        return arithmetic_ceiling(self.annual)

    @classmethod
    def from_book(cls, figures: dict[str, float]) -> Arm:
        return cls(annual=figures["annual"], printed=figures["cumulative"])


def fixed_arm() -> Arm:
    return Arm.from_book(cpo.BOOK_UNCONDITIONAL)


def rechosen_arm() -> Arm:
    return Arm.from_book(cpo.BOOK_CONDITIONAL)


#: The height of one dollar and the board units per dollar of growth. A value
#: of one dollar plus ``g`` sits at ``DOLLAR_Y + g * PER_DOLLAR``.
DOLLAR_Y, PER_DOLLAR = 0.5, 4.6
#: Where year 0 sits across the board and how wide one year is, and where the
#: lines at the top of the staircase end.
YEAR0_X, YEAR_W = 1.0, 1.5
TOP_END_X = 6.0
#: The red mark's left end, the bracket's place, and where the right-hand
#: words start.
PRINTED_X0, BRACKET_X, WORDS_X = 4.7, 6.15, 6.35
#: How far the printed figure's words sit above its mark.
PRINTED_RISE = 0.25
#: The height of the year marks under the staircase's steps.
YEARS_Y = 0.2
#: The grey note's three lines, under the staircase's upper steps.
NOTE_X, NOTE_Y = 4.35, (1.55, 1.2, 0.85)


def growth_y(growth: float) -> float:
    """A cumulative return's height on the second sketch, one dollar at :data:`DOLLAR_Y`."""
    return DOLLAR_Y + growth * PER_DOLLAR


def year_x(year: float) -> float:
    return YEAR0_X + year * YEAR_W


def staircase(arm: Arm) -> tuple[np.ndarray, np.ndarray]:
    """One dollar compounding at ``arm.annual`` a year, a step at each year's end,
    then flat to :data:`TOP_END_X`."""
    corners = []
    for year in range(YEARS):
        level = growth_y(compounded(arm.annual, year))
        corners += [(year_x(year), level), (year_x(year + 1), level)]
    corners.append((year_x(YEARS), growth_y(arm.compounded)))
    corners.append((TOP_END_X, growth_y(arm.compounded)))
    return _line(corners, per_unit=8)


def _pct(value: float, places: int) -> str:
    return f"{value:.{places}%}"


def _annual_returns(fixed: Arm, rechosen: Arm) -> Scene:
    """Lesson 2: the fixed arm's 17.29% a year falls short of 73% under either reading."""
    rate = _pct(fixed.annual, 2)
    top, ceiling, printed = (
        growth_y(fixed.compounded),
        growth_y(fixed.ceiling),
        growth_y(fixed.printed),
    )
    steps: list[Stroke | Label] = [
        _stroke("stairs", staircase(fixed), color=INK, width=2.4, frames=14),
        Label("$1", YEAR0_X - 0.25, DOLLAR_Y, names="stairs", color=INK, size=11, ha="right"),
        *(
            Label(
                f"year {year}",
                year_x(year),
                YEARS_Y,
                names="stairs",
                color=MUTED,
                size=11,
                ha="center",
            )
            for year in range(1, YEARS + 1)
        ),
        Label(
            f"{_pct(fixed.compounded, 1)}: {rate} compounded",
            WORDS_X,
            top,
            names="stairs",
            color=INK,
            size=11,
        ),
        _stroke(
            "ceiling",
            _line([(YEAR0_X, ceiling), (TOP_END_X, ceiling)]),
            color=ACCENT,
            dashed=True,
            width=1.8,
            frames=6,
        ),
        Label(
            f"at most {_pct(fixed.ceiling, 1)}: {rate} arithmetic",
            YEAR0_X,
            ceiling - 0.3,
            names="ceiling",
            color=ACCENT,
            size=11,
        ),
        _stroke(
            "printed",
            _line([(PRINTED_X0, printed), (TOP_END_X, printed)], per_unit=10),
            color=LOST,
            width=3.0,
            frames=4,
        ),
        Label(
            f"{_pct(fixed.printed, 0)} printed",
            WORDS_X,
            printed + PRINTED_RISE,
            names="printed",
            color=LOST,
            size=11,
        ),
        _stroke(
            "short",
            _line([(BRACKET_X, ceiling), (BRACKET_X, printed)], per_unit=30),
            color=LOST,
            width=1.8,
            frames=3,
        ),
        Label(
            f"{_pct(fixed.ceiling, 1)} still short of {_pct(fixed.printed, 0)}",
            WORDS_X,
            (ceiling + printed) / 2 + 0.03,
            names="short",
            color=LOST,
            size=11,
        ),
        Label(
            f"re-chosen arm, {_pct(rechosen.annual, 2)} a year:",
            NOTE_X,
            NOTE_Y[0],
            names="stairs",
            color=MUTED,
            size=11,
        ),
        Label(
            f"{_pct(rechosen.compounded, 1)} compounded, at most "
            f"{_pct(rechosen.ceiling, 1)} arithmetic,",
            NOTE_X,
            NOTE_Y[1],
            names="stairs",
            color=MUTED,
            size=11,
        ),
        Label(
            f"{_pct(rechosen.printed, 0)} printed",
            NOTE_X,
            NOTE_Y[2],
            names="stairs",
            color=MUTED,
            size=11,
        ),
    ]
    return Scene(f"Fixed arm at {rate} a year", "annual_returns", tuple(steps))


# --- Drawing ------------------------------------------------------------------

#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("rule", "annual_returns")
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


def scenes(fixed: Arm | None = None, rechosen: Arm | None = None) -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them, the rule's then Lesson 2's."""
    return (
        _rule(),
        _annual_returns(
            fixed if fixed is not None else fixed_arm(),
            rechosen if rechosen is not None else rechosen_arm(),
        ),
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


def make_cpo_whiteboards(
    out_dir: Path | None = None, fixed: Arm | None = None, rechosen: Arm | None = None
) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes(fixed, rechosen)]


def main() -> None:
    for path in make_cpo_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
