"""Whiteboard sketches for the equity-seasonals post: its opening and its two strategies.

``blog/equity-seasonals-lessons.md`` opens on why a strategy published as dead
is worth testing, which sources can say anything about that, and what two
later runs found. Its section "The two strategies" then describes Example 7.6
and Example 7.7. This module draws four scenes, and the post places each
right after the text it draws.

1. Which years each source reads: one axis from 1960 to 2030, with Heston and
   Sadka's sample ending at the start of 2002, where Chan says the effect
   disappeared, Chan's two short files, the book, and the two registered runs
   from 2009 on. Every bar is to scale, from :class:`Spans`.
2. Two verdicts: the January run's low and high means as one bracket that
   straddles zero, and the Heston and Sadka run's mean as a dot at zero with
   the returns its test could miss tinted up to X. Both lines are to scale,
   and the figures come from :class:`Verdicts`.
3. The January trade: a calendar year of returns, a ranking at the year's
   last close, the worst tenth bought and the best tenth shorted, held through
   January, with the losers pointed up and the winners down. That is Example
   7.6's bet that the extremes come back, a mean reversion trade.
4. The same-month trade: two monthly strips, last year above this year, with
   March of last year ranked and March of this year held, then April and on.
   The best tenth is bought and the worst shorted, with the winners pointed up
   again and the losers down. That is Example 7.7's bet that a month repeats,
   a seasonal momentum trade.

The two strategy scenes are schematic and carry no data. The ranked dots stand
for a cross-section of stocks sorted by the return each strategy ranks on, and
the two ringed at each end stand for a tenth. March is an example month, and
the scene says the trade moves on to the next one.

The two opening scenes carry data. :meth:`Verdicts.from_runs` reads the
registered runs on the owner's archive, about twenty seconds, and
:meth:`Spans.read` reads Chan's committed files and the runs' constants. The
start of Heston and Sadka's sample is drawn dashed, because nothing here has
checked where it starts. A run whose figures would make the verdicts scene's
words false is refused rather than drawn.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied: its strokes, labels, tints, timeline, renderer and palette, so
these GIFs share that post's look, frame rate, hold and colours. Only the
scenes and the file names are this module's. Each GIF is named
:data:`GIF_PREFIX` plus the scene's slug.

The sketch is deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw all four on a machine with the archive
with::

    uv run python -m chan.equity_seasonals_whiteboard
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from chan import equity_seasonals as seasonals
from chan.archive import ArchiveUnavailable
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.series import load_panel
from chan.usdcad_tests_whiteboard import (
    TINT,
    Fill,
    Label,
    Scene,
    Stroke,
    _arrow,
    _dot,
    _line,
    _span,
    _stroke,
    render,
    timeline,
)

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "equity_seasonals_"

#: How many stocks the ranked row draws, and how many of them stand for a tenth.
RANKED = 20
TENTH = 2


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``equity_seasonals_january_trade.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


def _ranked(x0: float, y0: float, x1: float, y1: float) -> tuple[np.ndarray, np.ndarray]:
    """:data:`RANKED` stocks sorted by return, lowest at the lower left."""
    t = np.linspace(0.0, 1.0, RANKED)
    return x0 + (x1 - x0) * t, y0 + (y1 - y0) * t


def _ring(x: np.ndarray, y: np.ndarray, pad: float = 0.22) -> tuple:
    """An ellipse round the points ``x``, ``y``, ``pad`` clear of them."""
    cx, cy = float(x.mean()), float(y.mean())
    rx = (float(x.max() - x.min())) / 2 + pad
    ry = (float(y.max() - y.min())) / 2 + pad
    angle = np.linspace(0.0, 2 * math.pi, 40)
    return cx + rx * np.cos(angle), cy + ry * np.sin(angle)


def _cells(x0: float, x1: float, y: float, months: int = 12, half: float = 0.2) -> tuple:
    """A strip of ``months`` cells from ``x0`` to ``x1`` centred on ``y``,
    drawn as one stroke: the outline, then each divider."""
    points = [(x0, y - half), (x1, y - half), (x1, y + half), (x0, y + half), (x0, y - half)]
    width = (x1 - x0) / months
    for k in range(1, months):
        x = x0 + k * width
        points += [(x, y - half), (x, y + half)] if k % 2 else [(x, y + half), (x, y - half)]
    return _line(points)


def _cell(x0: float, x1: float, y: float, month: int, months: int = 12, half: float = 0.2) -> tuple:
    """The outline of month ``month``'s cell, counting January as 0."""
    width = (x1 - x0) / months
    left = x0 + month * width
    return _line(
        [
            (left, y - half),
            (left + width, y - half),
            (left + width, y + half),
            (left, y + half),
            (left, y - half),
        ]
    )


#: Where the January trade's year runs, and where its January ends, one
#: twelfth of the year past the year's last close.
YEAR = (0.6, 6.0, 3.4)
JANUARY_END = YEAR[1] + (YEAR[1] - YEAR[0]) / 12
#: Where each scene's ranked row runs, from its lowest stock to its highest.
JANUARY_ROW = (0.8, 0.6, 5.6, 2.3)
SAME_MONTH_ROW = (0.8, 0.6, 5.6, 1.75)
#: Where each scene's two arrows stand, and the row of their labels.
ARROWS_X = 7.0


def _january_trade() -> Scene:
    """Example 7.6: rank on a calendar year, hold January, bet the extremes come back."""
    x0, x1, y = YEAR
    stocks = _ranked(*JANUARY_ROW)
    losers = (stocks[0][:TENTH], stocks[1][:TENTH])
    winners = (stocks[0][-TENTH:], stocks[1][-TENTH:])
    return Scene(
        "The January trade",
        "january_trade",
        (
            _stroke("year", _span(x0, x1, y), frames=10),
            Label("a year of returns", (x0 + x1) / 2 + 0.6, 3.85, names="year", ha="center"),
            _dot("close", x1, y),
            _stroke(
                "january", _line([(x1, y), (JANUARY_END, y)]), color=ACCENT, width=4.0, frames=3
            ),
            Label("hold January", JANUARY_END + 0.2, y, names="january", color=ACCENT),
            _stroke("to-rank", _arrow(x1 - 0.05, y - 0.25, x1 - 0.3, 2.7), color=MUTED, frames=4),
            Label("rank at the year’s last close", x1 + 0.2, 2.85, names="to-rank", size=12),
            Stroke("ranked", stocks[0], stocks[1], color=MUTED, frames=10, dots=6.0),
            _stroke("buy", _ring(*losers), color=GOOD, frames=6),
            Label("buy the worst tenth", 1.7, 0.3, names="buy", color=GOOD, size=12),
            _stroke("short", _ring(*winners), color=LOST, frames=6),
            Label(
                "short the best tenth", 4.75, 2.75, names="short", color=LOST, ha="right", size=12
            ),
            _stroke("losers-up", _arrow(ARROWS_X, 0.7, ARROWS_X, 1.2), color=GOOD, frames=4),
            Label("losers up", ARROWS_X + 0.3, 0.95, names="losers-up", color=GOOD, size=12),
            _stroke("winners-down", _arrow(ARROWS_X, 2.05, ARROWS_X, 1.5), color=LOST, frames=4),
            Label("winners down", ARROWS_X + 0.3, 1.75, names="winners-down", color=LOST, size=12),
            Label(
                "mean reversion", 9.6, 0.3, names="winners-down", color=ACCENT, ha="right", size=14
            ),
        ),
    )


#: The same-month trade's two strips, last year above this year, and the
#: example month it ranks and holds, counting January as 0.
STRIPS = (2.3, 8.3)
LAST_YEAR, THIS_YEAR = 3.25, 2.45
MARCH, APRIL = 2, 3


def _same_month_trade() -> Scene:
    """Example 7.7: rank on one month a year ago, hold that month, bet it repeats."""
    x0, x1 = STRIPS
    width = (x1 - x0) / 12
    march = x0 + (MARCH + 0.5) * width
    april = x0 + (APRIL + 0.5) * width
    stocks = _ranked(*SAME_MONTH_ROW)
    losers = (stocks[0][:TENTH], stocks[1][:TENTH])
    winners = (stocks[0][-TENTH:], stocks[1][-TENTH:])
    gap = (LAST_YEAR - 0.2, THIS_YEAR + 0.2)
    return Scene(
        "The same-month trade",
        "same_month_trade",
        (
            _stroke("last-year", _cells(x0, x1, LAST_YEAR), frames=10),
            Label("last year", x0 - 0.25, LAST_YEAR, names="last-year", ha="right", size=12),
            _stroke("this-year", _cells(x0, x1, THIS_YEAR), frames=10),
            Label("this year", x0 - 0.25, THIS_YEAR, names="this-year", ha="right", size=12),
            _stroke(
                "march-then", _cell(x0, x1, LAST_YEAR, MARCH), color=ACCENT, width=3.5, frames=4
            ),
            Label("March", march, 3.8, names="march-then", color=ACCENT, ha="center"),
            Label("rank on", x1 + 0.25, LAST_YEAR, names="march-then", color=ACCENT, size=12),
            _stroke(
                "repeat", _arrow(march, gap[0] - 0.02, march, gap[1] + 0.02), color=ACCENT, frames=3
            ),
            _stroke(
                "march-now", _cell(x0, x1, THIS_YEAR, MARCH), color=ACCENT, width=3.5, frames=4
            ),
            Label("hold", x1 + 0.25, THIS_YEAR, names="march-now", color=ACCENT, size=12),
            _stroke(
                "april-then", _cell(x0, x1, LAST_YEAR, APRIL), color=MUTED, width=3.0, frames=4
            ),
            _stroke("april-now", _cell(x0, x1, THIS_YEAR, APRIL), color=MUTED, width=3.0, frames=4),
            Label("then April, May, …", april + 0.45, 3.8, names="april-now", color=MUTED, size=12),
            Stroke("ranked", stocks[0], stocks[1], color=MUTED, frames=10, dots=6.0),
            _stroke("buy", _ring(*winners), color=GOOD, frames=6),
            Label("buy the best tenth", 4.55, 1.92, names="buy", color=GOOD, ha="right", size=12),
            _stroke("short", _ring(*losers), color=LOST, frames=6),
            Label("short the worst tenth", 1.55, 0.3, names="short", color=LOST, size=12),
            _stroke("winners-up", _arrow(ARROWS_X, 1.45, ARROWS_X, 2.0), color=GOOD, frames=4),
            Label("winners up", ARROWS_X + 0.3, 1.75, names="winners-up", color=GOOD, size=12),
            _stroke("losers-down", _arrow(ARROWS_X, 1.2, ARROWS_X, 0.7), color=LOST, frames=4),
            Label("losers down", ARROWS_X + 0.3, 0.95, names="losers-down", color=LOST, size=12),
            Label(
                "seasonal momentum",
                9.6,
                0.3,
                names="losers-down",
                color=ACCENT,
                ha="right",
                size=14,
            ),
        ),
    )


def scenes() -> tuple[Scene, ...]:
    """The two strategy scenes in the order the post reads them."""
    return (_january_trade(), _same_month_trade())


@dataclass(frozen=True)
class Verdicts:
    """The four figures the verdicts scene draws, each read from a registered run.

    ``january_low`` and ``january_high`` are the means of the low and high
    series of :func:`chan.equity_seasonals.run_point_in_time`, a return per
    January. ``monthly_mean`` is the mean held month of
    :func:`chan.equity_seasonals.run_monthly_point_in_time` under
    :data:`chan.equity_seasonals.REVISED_MATLAB`, and ``detectable`` is that
    run's X, the annual return its test detects with 80 percent probability.
    """

    january_low: float
    january_high: float
    monthly_mean: float
    detectable: float

    @classmethod
    def from_runs(
        cls, january: seasonals.PointInTimeRun, monthly: seasonals.MonthlyRun
    ) -> Verdicts:
        return cls(
            january_low=january.low.mean,
            january_high=january.high.mean,
            monthly_mean=monthly.matlab.test.mean,
            detectable=monthly.matlab.x,
        )


@dataclass(frozen=True)
class Spans:
    """The years the timeline scene draws, each read from the data or the runs.

    ``large_caps`` and ``small_caps`` are the first and last dates of Chan's
    two files as :func:`chan.series.load_panel` reads them. ``later`` runs
    from the first month either registered run holds to the last, January
    2009 to September 2026, from :data:`chan.equity_seasonals.FIRST_HELD` and
    :data:`chan.equity_seasonals.LAST_HELD`. ``split`` is
    :data:`chan.equity_seasonals.SPLIT`, the start of 2002.
    """

    large_caps: tuple[pd.Timestamp, pd.Timestamp]
    small_caps: tuple[pd.Timestamp, pd.Timestamp]
    later: tuple[pd.Timestamp, pd.Timestamp]
    split: pd.Timestamp

    @classmethod
    def read(cls) -> Spans:
        def span(name: str) -> tuple[pd.Timestamp, pd.Timestamp]:
            _, closes = load_panel(name)
            return closes.index[0], closes.index[-1]

        return cls(
            large_caps=span(seasonals.LARGE_CAPS),
            small_caps=span(seasonals.SMALL_CAPS),
            later=(
                seasonals.FIRST_HELD.to_timestamp(how="start"),
                seasonals.LAST_HELD.to_timestamp(how="end").normalize(),
            ),
            split=seasonals.SPLIT,
        )


def _signed(value: float, places: int) -> str:
    return f"{value:.{places}f}".replace("-", "−")


#: Each verdict's number line: the board's span, its height, and the values
#: at its ends. The January line reads a return per January, the Heston and
#: Sadka line a return per year.
VERDICT_X = (3.0, 9.6)
JANUARY_Y, MONTHLY_Y = 3.2, 1.3
JANUARY_RANGE = (-0.15, 0.15)
ANNUAL_RANGE = (-0.02, 0.08)


def _at(value: float, lo: float, hi: float) -> float:
    """Where ``value`` sits on a number line from ``lo`` to ``hi``."""
    if not lo <= value <= hi:
        raise ValueError(f"{value} lies outside the line from {lo} to {hi}")
    x0, x1 = VERDICT_X
    return x0 + (value - lo) / (hi - lo) * (x1 - x0)


def _two_verdicts(verdicts: Verdicts) -> Scene:
    """The two registered runs' verdicts, each on its own number line to scale.

    The January effect's line carries the low and high series' means as the
    two ends of one bracket that straddles zero, which is why free data cannot
    decide it. Heston and Sadka's line carries the run's mean, a year's worth
    of its mean month, as a dot at zero, and tints the returns from zero to X,
    the size its test could have missed. A run whose figures would make those
    words false is refused: a bracket that does not straddle zero, or a mean
    that is not inside the tinted gap's reach of zero.
    """
    low, high = verdicts.january_low, verdicts.january_high
    if not low < 0 < high:
        raise ValueError(f"the January bracket {low} to {high} does not straddle zero")
    annual = 12 * verdicts.monthly_mean
    if not abs(annual) < verdicts.detectable:
        raise ValueError(f"a mean of {annual} a year is not inside X = {verdicts.detectable}")
    x_low, x_high = _at(low, *JANUARY_RANGE), _at(high, *JANUARY_RANGE)
    zero_1, zero_2 = _at(0.0, *JANUARY_RANGE), _at(0.0, *ANNUAL_RANGE)
    x_detect, x_mean = _at(verdicts.detectable, *ANNUAL_RANGE), _at(annual, *ANNUAL_RANGE)
    x0, x1 = VERDICT_X
    bracket_y = JANUARY_Y + 0.35
    return Scene(
        "Two verdicts",
        "two_verdicts",
        (
            _stroke(
                "january-line", _line([(x0, JANUARY_Y), (x1, JANUARY_Y)]), color=MUTED, frames=6
            ),
            Label("January effect", 0.3, JANUARY_Y, names="january-line"),
            Label("per January", 0.3, JANUARY_Y - 0.38, names="january-line", color=MUTED, size=11),
            _stroke(
                "january-zero",
                _line([(zero_1, JANUARY_Y - 0.13), (zero_1, JANUARY_Y + 0.13)]),
                frames=2,
            ),
            Label("0", zero_1, JANUARY_Y - 0.46, names="january-zero", ha="center", size=12),
            _stroke("bracket", _span(x_low, x_high, bracket_y), color=ACCENT, width=3.0, frames=8),
            Label(
                _signed(low, 4),
                x_low,
                bracket_y + 0.47,
                names="bracket",
                color=ACCENT,
                ha="center",
                size=12,
            ),
            Label(
                _signed(high, 4),
                x_high,
                bracket_y + 0.47,
                names="bracket",
                color=ACCENT,
                ha="center",
                size=12,
            ),
            Label(
                "free data cannot decide",
                x1,
                JANUARY_Y - 0.46,
                names="bracket",
                color=ACCENT,
                ha="right",
                size=12,
            ),
            _stroke(
                "monthly-line", _line([(x0, MONTHLY_Y), (x1, MONTHLY_Y)]), color=MUTED, frames=6
            ),
            Label("Heston and Sadka", 0.3, MONTHLY_Y, names="monthly-line"),
            Label("per year", 0.3, MONTHLY_Y - 0.38, names="monthly-line", color=MUTED, size=11),
            _stroke(
                "monthly-zero",
                _line([(zero_2, MONTHLY_Y - 0.13), (zero_2, MONTHLY_Y + 0.13)]),
                frames=2,
            ),
            Label("0", zero_2, MONTHLY_Y - 0.46, names="monthly-zero", ha="center", size=12),
            Fill("unseen", zero_2, MONTHLY_Y + 0.04, x_detect, MONTHLY_Y + 0.34, TINT),
            _stroke(
                "detectable",
                _line([(x_detect, MONTHLY_Y - 0.13), (x_detect, MONTHLY_Y + 0.45)]),
                color=ACCENT,
                width=3.0,
                frames=3,
            ),
            Label(
                f"{100 * verdicts.detectable:.1f}% a year",
                x_detect,
                MONTHLY_Y + 0.8,
                names="detectable",
                color=ACCENT,
                ha="center",
                size=12,
            ),
            _dot("mean", x_mean, MONTHLY_Y, color=INK),
            Label("measured", x_mean - 0.3, MONTHLY_Y + 0.45, names="mean", ha="right", size=12),
            Label(
                "too small to detect",
                (zero_2 + x_detect) / 2,
                MONTHLY_Y - 0.46,
                names="detectable",
                color=GOOD,
                ha="center",
                size=12,
            ),
        ),
    )


#: The timeline's years, its board span, and the heights of its rows.
YEARS = (1960, 2030)
TIMELINE_X = (0.6, 9.6)
AXIS_Y = 0.75
#: Heston and Sadka's sample is drawn from this year, with a dashed lead-in
#: before it, because nothing here has checked where their sample starts.
SAMPLE_FROM = 1968


def _year(when: pd.Timestamp | float) -> float:
    """Where a date or a fractional year sits on the timeline."""
    year = when if isinstance(when, float | int) else when.year + (when.dayofyear - 1) / 365.25
    lo, hi = YEARS
    x0, x1 = TIMELINE_X
    return x0 + (year - lo) / (hi - lo) * (x1 - x0)


def _which_years(spans: Spans) -> Scene:
    """Which years each source reads, on one axis to scale.

    Heston and Sadka's sample ends at the start of 2002, where Chan says the
    effect disappeared. Chan's two files are short and end before the book.
    The two registered runs start where the book came out and run to 2026.
    """
    lo, hi = YEARS
    split = _year(spans.split)
    axis = [(_year(float(lo)), AXIS_Y), (_year(float(hi)), AXIS_Y)]
    ticks = []
    for decade in range(lo + 10, hi, 10):
        x = _year(float(decade))
        ticks += [(x, AXIS_Y), (x, AXIS_Y - 0.12), (x, AXIS_Y)]
    sample_y, files_y, later_y = 3.3, 2.45, 1.5
    large, small = spans.large_caps, spans.small_caps
    first, last = spans.later
    book = _year(first)
    steps: list = [
        _stroke("axis", _line(axis + ticks), color=MUTED, frames=8),
    ]
    for decade in range(lo + 10, hi, 10):
        steps.append(
            Label(
                str(decade),
                _year(float(decade)),
                AXIS_Y - 0.43,
                names="axis",
                color=MUTED,
                ha="center",
                size=11,
            )
        )
    steps += [
        _stroke(
            "sample-lead",
            _line([(_year(float(lo)) + 0.05, sample_y), (_year(float(SAMPLE_FROM)), sample_y)]),
            color=MUTED,
            dashed=True,
            frames=3,
        ),
        _stroke(
            "sample",
            _line([(_year(float(SAMPLE_FROM)), sample_y), (split, sample_y)]),
            width=5.0,
            frames=8,
        ),
        Label(
            "Heston and Sadka’s sample",
            _year(float(SAMPLE_FROM)),
            sample_y + 0.4,
            names="sample",
            size=12,
        ),
        _stroke(
            "split", _line([(split, 1.95), (split, 3.75)]), color=ACCENT, dashed=True, frames=5
        ),
        Label("“disappeared since then”", split + 0.15, 4.02, names="split", color=ACCENT, size=12),
        _stroke(
            "large-caps",
            _line([(_year(large[0]), files_y + 0.14), (_year(large[1]), files_y + 0.14)]),
            width=5.0,
            frames=4,
        ),
        _stroke(
            "small-caps",
            _line([(_year(small[0]), files_y - 0.14), (_year(small[1]), files_y - 0.14)]),
            width=5.0,
            frames=4,
        ),
        Label(
            "Chan’s files, survivors only",
            _year(large[0]) - 0.2,
            files_y,
            names="small-caps",
            ha="right",
            size=12,
        ),
        _dot("book", book, AXIS_Y, color=ACCENT),
        Label("the book", book, AXIS_Y + 0.38, names="book", color=ACCENT, ha="center", size=12),
        _stroke(
            "later",
            _line([(book, later_y), (_year(last), later_y)]),
            color=GOOD,
            width=5.0,
            frames=6,
        ),
        Label(
            "two later runs, index as it stood",
            book - 0.2,
            later_y,
            names="later",
            color=GOOD,
            ha="right",
            size=12,
        ),
    ]
    return Scene("Which years each source reads", "which_years", tuple(steps))


def opening_scenes(verdicts: Verdicts, spans: Spans) -> tuple[Scene, ...]:
    """The two scenes for the post's opening section, in the order it reads them."""
    return (_which_years(spans), _two_verdicts(verdicts))


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


def make_equity_seasonals_whiteboards(
    out_dir: Path | None = None,
    verdicts: Verdicts | None = None,
    spans: Spans | None = None,
) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, the
    opening's two first, then the two strategies'.

    ``verdicts`` is read from the two registered runs on the owner's archive
    when it is not handed in, which takes about twenty seconds, and ``spans``
    from Chan's two committed files.
    """
    folder = out_dir if out_dir is not None else FIGURES_DIR
    if verdicts is None:
        verdicts = Verdicts.from_runs(
            seasonals.run_point_in_time(), seasonals.run_monthly_point_in_time()
        )
    spans = spans if spans is not None else Spans.read()
    return [_write(scene, folder) for scene in (*opening_scenes(verdicts, spans), *scenes())]


def main() -> None:
    try:
        paths = make_equity_seasonals_whiteboards()
    except ArchiveUnavailable as absent:
        # The verdicts read the owner's archive, so a machine without it
        # gets one line naming what is missing rather than a traceback.
        raise SystemExit(str(absent)) from absent
    for path in paths:
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
