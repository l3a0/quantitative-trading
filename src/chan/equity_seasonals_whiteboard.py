"""Whiteboard sketches for the equity-seasonals post: its opening, its two strategies and its rules.

``blog/equity-seasonals-lessons.md`` opens on why a strategy published as dead
is worth testing, which sources can say anything about that, and what two
later runs found. Its section "The two strategies" then describes Example 7.6
and Example 7.7, and its first lesson lists the rules behind each printout.
This module draws twelve scenes, and the post places each right after the
text it draws. The first four are these.

1. Which years each source reads: one axis from 1960 to 2030, with the years
   behind Heston and Sadka's 13 percent ending at the start of 2002, where
   Chan says the effect disappeared, Chan's two short files, the book's first
   edition, and the two registered runs from 2009 on. Every bar is to scale,
   from :class:`Spans`.
2. Two verdicts: the January run's low and high means as one bracket that
   straddles zero, and the Heston and Sadka run's mean as a dot at zero with
   the returns its test could miss tinted up to the return it detects 80
   percent of the time. Each line has its own scale, and the figures come
   from :class:`Verdicts`.
3. The January trade: a calendar year of returns, a ranking at the year's
   last close, the worst tenth bought and the best tenth shorted, held through
   January, with the losers pointed up and the winners down. That is Example
   7.6's bet that the extremes come back, a mean reversion trade.
4. The same-month trade: two monthly strips, last year above this year, with
   March of last year ranked and March of this year held, then April and on.
   The best tenth is bought and the worst shorted, with the winners pointed up
   again and the losers down. That is Example 7.7's bet that a month repeats,
   a seasonal momentum trade.

The other seven each draw one rule, in the order the post lists them:

1. Example 7.6's rule 2, the revised Python's winners sliced two short of a
   tenth, as two bars to scale.
2. Example 7.6's rule 3, PMC's last close carried across its gap to the end
   of 2006 and read as a gain for 2007.
3. Example 7.7's rule 1, one month's positions added up against averaged.
4. Example 7.7's rule 2, each stock in the sorted row checked against the
   close in the same column of the unsorted one.
5. Example 7.7's rule 3, the 96 months as dots, with the 95 and the 83 each
   mean divides by.
6. Example 7.7's rule 5, a shared month-end row against each stock's own last
   priced day.
7. Example 7.7's rule 8, the first pass asking the month-end rows for a daily
   row past their end, and the row the repair reads.

Their figures come from :class:`RuleFigures`, which
``tests/test_equity_seasonals.py`` derives from Chan's two files. The scenes
for rules 1, 2 and 5 of Example 7.7 are schematic and carry no figure.

The twelfth sits in Lesson 2, after the paragraph on the split's years. It
draws the two halves' annual returns beside the sums of 2002 and 2006, to
one scale, with a bracket for each pair's gap. Its figures come from
:class:`SplitFigures`, which ``TestTheYearsInsideTheSplit`` derives.

The two strategy scenes are schematic and carry no data. The ranked dots stand
for a cross-section of stocks sorted by the return each strategy ranks on, and
the two ringed at each end stand for a tenth. March is an example month, and
the scene says the trade moves on to the next one.

The two opening scenes carry data. :meth:`Verdicts.from_runs` reads the
registered runs on the owner's archive, about twenty seconds, and
:meth:`Spans.read` reads Chan's committed files and the runs' constants. The
bar for Heston and Sadka's 13 percent ends at Chan's 2002 split rather than at
any date read from their paper, and its start is drawn dashed, because nothing
here has checked where their sample starts or ends. A run whose verdicts
differ from the ones the scene's words state is refused rather than drawn.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied: its strokes, labels, tints, timeline, renderer and palette, so
these GIFs share that post's look, frame rate, hold and colours. Only the
scenes and the file names are this module's. Each GIF is named
:data:`GIF_PREFIX` plus the scene's slug.

The sketch is deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw all twelve with the command below.
Only the verdicts sketch reads the archive, so on a machine without it the
command redraws the other eleven and exits non-zero naming the one it left::

    uv run python -m chan.equity_seasonals_whiteboard
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from chan import equity_seasonals as seasonals
from chan.archive import ArchiveRefused, ArchiveUnavailable
from chan.fund_panel import PanelRefused
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
from chan.vintage import VintageUnavailable

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
class RuleFigures:
    """The figures four of the seven rule sketches print, all from Chan's two files.

    ``tests/test_equity_seasonals.py`` derives each one from the files in
    ``TestTheRuleSketchesFigures``, so a default here that drifts from the
    data fails there rather than reaching a GIF.
    """

    #: January 2006 under the revised Python: stocks ranked, losers bought
    #: and winners shorted, the winners sliced as ``topN - 2``.
    ranked_2006: int = 579
    longs_2006: int = 58
    shorts_2006: int = 56
    #: PMC in the S&P 600 file: its last close before its gap, the trading
    #: days the gap runs, its close at the end of 2007, the gain the fill
    #: reads for 2007, where that gain ranks and of how many.
    pmc_last_close: float = 6.02
    pmc_gap_days: int = 851
    pmc_2007_close: float = 13.88
    pmc_gain: float = 1.3056478405315617
    pmc_rank: int = 4
    ranked_2007: int = 595
    #: Example 7.7's months in the S&P 500 file: the first with no return,
    #: then the months with no position and the months that hold positions.
    empty_months: int = 12
    held_months: int = 83
    #: The revised MATLAB's month-end rows, and the daily row its first pass,
    #: m = 14, asks for, ``monthEnds(13)``, where the repair reads row 13.
    month_end_rows: int = 96
    first_pass_row: int = 258
    repaired_row: int = 13

    @property
    def first_edition_months(self) -> int:
        """The months the first edition's mean runs over, every one with a return."""
        return self.empty_months + self.held_months


def _cross(x: float, y: float, r: float = 0.14) -> tuple:
    """An X centred on (x, y), drawn as one stroke."""
    return _line(
        [(x - r, y - r), (x + r, y + r), (x, y), (x - r, y + r), (x + r, y - r)], per_unit=10
    )


def _circle(x: float, y: float, r: float) -> tuple:
    angle = np.linspace(0.0, 2 * math.pi, 30)
    return x + r * np.cos(angle), y + r * np.sin(angle)


def _ordinal(n: int) -> str:
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


#: The short-side scene's bars: where both start, and the width of one stock.
SIDES_X, STOCK_WIDTH = 0.9, 0.11
LONG_Y, SHORT_Y = 3.0, 2.0


def _short_side(f: RuleFigures) -> Scene:
    """Example 7.6's rule 2: the winners sliced two short of a tenth."""
    long_end = SIDES_X + f.longs_2006 * STOCK_WIDTH
    short_end = SIDES_X + f.shorts_2006 * STOCK_WIDTH
    return Scene(
        "Two fewer winners shorted",
        "rule_short_side",
        (
            _stroke("long", _span(SIDES_X, long_end, LONG_Y), color=GOOD, width=4.0, frames=8),
            Label(f"buy the {f.longs_2006} worst", SIDES_X, 3.5, names="long", color=GOOD, size=12),
            _stroke("short", _span(SIDES_X, short_end, SHORT_Y), color=LOST, width=4.0, frames=8),
            Label(
                f"short {f.shorts_2006} of the {f.longs_2006} best",
                SIDES_X,
                2.5,
                names="short",
                color=LOST,
                size=12,
            ),
            _stroke(
                "tenth",
                _line([(long_end, 3.35), (long_end, 1.8)]),
                color=ACCENT,
                dashed=True,
                frames=4,
            ),
            Label(
                f"a tenth: {f.longs_2006}",
                long_end + 0.22,
                3.5,
                names="tenth",
                color=ACCENT,
                size=12,
            ),
            _stroke(
                "missing",
                _line([(short_end, SHORT_Y), (long_end, SHORT_Y)]),
                color=MUTED,
                dashed=True,
                frames=2,
            ),
            Label(
                f"{f.longs_2006 - f.shorts_2006} left out: "
                f"the best and the {_ordinal(f.longs_2006)}",
                long_end + 0.1,
                1.45,
                names="missing",
                color=MUTED,
                ha="right",
                size=12,
            ),
            Label("the winners are sliced as topN − 2", SIDES_X, 1.0, names="missing", size=13),
            Label(
                f"January 2006, {f.ranked_2006} stocks ranked",
                SIDES_X,
                0.45,
                names="missing",
                color=MUTED,
                size=11,
            ),
        ),
    )


#: The filled-close scene's years along the board, and its price scale.
PMC_X = (0.8, 8.4)
PMC_YEARS = (2004.0, 2008.1)
PMC_AXIS_Y = 0.65
PMC_PRICE = (6.0, 1.5, 0.22)


def _pmc_x(year: float) -> float:
    (x0, x1), (first, last) = PMC_X, PMC_YEARS
    return x0 + (x1 - x0) * (year - first) / (last - first)


def _pmc_y(price: float) -> float:
    base, y0, per = PMC_PRICE
    return y0 + (price - base) * per


def _filled_close(f: RuleFigures) -> Scene:
    """Example 7.6's rule 3: PMC's last close carried across its gap to 2006's year-end.

    The two short stretches of price either side of the gap are schematic. The
    carried close, the close at the end of 2007 and the years are PMC's.
    """
    ticks = []
    for year in range(2004, 2009):
        ticks += [(_pmc_x(year), PMC_AXIS_Y), (_pmc_x(year), PMC_AXIS_Y - 0.1)]
        ticks.append((_pmc_x(year), PMC_AXIS_Y))
    early_t = np.linspace(2004.04, 2004.2, 12)
    early = f.pmc_last_close + 0.25 * np.sin(np.linspace(0, 5, 12)) * np.linspace(1, 0, 12)
    late_t = np.linspace(2007.58, 2008.08, 20)
    late = f.pmc_2007_close + 0.7 + 0.5 * np.sin(np.linspace(0, 7, 20))
    late[-6] = f.pmc_2007_close
    end_2006, end_2007 = _pmc_x(2007.0), _pmc_x(late_t[-6])
    carried, closed = _pmc_y(f.pmc_last_close), _pmc_y(f.pmc_2007_close)
    axis = [(_pmc_x(PMC_YEARS[0]), PMC_AXIS_Y), (_pmc_x(PMC_YEARS[1]), PMC_AXIS_Y)]
    return Scene(
        "PMC’s filled close",
        "rule_filled_close",
        (
            _stroke("axis", _line(axis + ticks), color=MUTED, frames=6),
            *[
                Label(
                    str(year), _pmc_x(year), 0.22, names="axis", color=MUTED, ha="center", size=11
                )
                for year in range(2004, 2009)
            ],
            Stroke("before", np.array([_pmc_x(t) for t in early_t]), _pmc_y(early), frames=4),
            Label("PMC", _pmc_x(2004.0), 1.12, names="before", size=12),
            _stroke(
                "carried",
                _line([(_pmc_x(2004.2), carried), (end_2006, carried)]),
                color=MUTED,
                dashed=True,
                frames=8,
            ),
            Label(
                f"last close {f.pmc_last_close:.2f}, "
                f"then {f.pmc_gap_days} trading days with no price",
                0.4,
                2.0,
                names="carried",
                color=MUTED,
                size=10.5,
            ),
            _dot("end-2006", end_2006, carried),
            Label(
                "end of 2006",
                end_2006 - 0.25,
                1.12,
                names="end-2006",
                color=ACCENT,
                ha="right",
                size=11,
            ),
            Stroke("after", np.array([_pmc_x(t) for t in late_t]), _pmc_y(late), frames=5),
            _dot("end-2007", end_2007, closed),
            Label(
                f"{f.pmc_2007_close:.2f}",
                end_2007 + 0.25,
                closed - 0.27,
                names="end-2007",
                color=ACCENT,
                size=11,
            ),
            _stroke(
                "gain",
                _arrow(end_2006 + 0.1, carried + 0.1, end_2007 - 0.12, closed - 0.08),
                color=LOST,
                frames=5,
            ),
            Label(
                f"+{f.pmc_gain:.2%} read as 2007’s gain",
                3.0,
                3.35,
                names="gain",
                color=LOST,
                size=12,
            ),
            Label(
                f"{_ordinal(f.pmc_rank)} best of {f.ranked_2007}: shorted",
                3.0,
                2.85,
                names="gain",
                color=LOST,
                size=12,
            ),
        ),
    )


#: One schematic month's returns on its positions, and the line they hang from.
POSITION_RETURNS = (0.35, -0.45, 0.1, -0.5, 0.25, -0.4, -0.2, -0.35)
SUM_BASE = 2.5
SUM_X, MEAN_X = 6.1, 8.6


def _bars(x0: float, step: float) -> tuple:
    """Each return as a bar from :data:`SUM_BASE`, joined along it, as one stroke."""
    points = []
    for k, r in enumerate(POSITION_RETURNS):
        x = x0 + k * step
        points += [(x, SUM_BASE), (x, SUM_BASE + r), (x, SUM_BASE)]
        if k + 1 < len(POSITION_RETURNS):
            points.append((x + step, SUM_BASE))
    return _line(points, per_unit=10)


def _sum_or_mean() -> Scene:
    """Example 7.7's rule 1: one month's positions added up, or averaged."""
    total = sum(POSITION_RETURNS)
    mean = total / len(POSITION_RETURNS)
    return Scene(
        "Add up, or average",
        "rule_sum_or_mean",
        (
            _stroke("bars", _bars(0.8, 0.33), frames=10, width=3.0),
            Label("one month’s N positions", 0.6, 3.35, names="bars", size=12),
            _stroke("to-sum", _arrow(3.4, SUM_BASE, 5.5, SUM_BASE), color=MUTED, frames=4),
            Label("first edition: add them up", SUM_X, 3.35, names="to-sum", ha="center", size=12),
            _stroke(
                "sum", _line([(SUM_X, SUM_BASE), (SUM_X, SUM_BASE + total)]), width=8.0, frames=5
            ),
            Label("summed positions", SUM_X, 0.85, names="sum", ha="center", size=12),
            _stroke(
                "mean",
                _line([(MEAN_X, SUM_BASE), (MEAN_X, SUM_BASE + mean)]),
                color=ACCENT,
                width=8.0,
                frames=1,
            ),
            Label("revised: ÷ N", MEAN_X, 3.35, names="mean", color=ACCENT, ha="center", size=12),
            Label("capital", MEAN_X, 0.85, names="mean", color=ACCENT, ha="center", size=12),
            _stroke(
                "zero",
                _line([(SUM_X - 0.4, SUM_BASE), (MEAN_X + 0.4, SUM_BASE)]),
                color=MUTED,
                frames=3,
            ),
            Label("each month is N times too big", 5.0, 0.35, names="zero", color=MUTED, size=11),
        ),
    )


#: The wrong-close scene's two rows of five stocks: the first sorted by
#: return, the second in column order, with C the stock that has no close.
CARDS = (2.4, 6.4)
SORTED_Y, COLUMNS_Y = 3.1, 1.6
SORTED, COLUMNS = "DBEAC", "ABCDE"
NO_CLOSE = "C"


def _card(k: int) -> float:
    return CARDS[0] + (k + 0.5) * (CARDS[1] - CARDS[0]) / len(COLUMNS)


def _wrong_close() -> Scene:
    """Example 7.7's rule 2: each sorted position checked against the close in its column."""
    hole = COLUMNS.index(NO_CLOSE)
    pairs = [
        _stroke(
            f"pair-{k}",
            _arrow(_card(k), SORTED_Y - 0.42, _card(k), COLUMNS_Y + 0.42),
            color=MUTED,
            frames=2,
        )
        for k in range(len(COLUMNS))
        if k != hole
    ]
    one = np.array([SORTED_Y])
    return Scene(
        "Checking the wrong stock’s close",
        "rule_wrong_close",
        (
            _stroke("sorted", _cells(*CARDS, SORTED_Y, months=5, half=0.36), frames=8),
            Label(
                "sorted by return", CARDS[0] - 0.2, SORTED_Y, names="sorted", ha="right", size=12
            ),
            *[
                Label(s, _card(k), SORTED_Y, names="sorted", ha="center", size=14)
                for k, s in enumerate(SORTED)
            ],
            _stroke("columns", _cells(*CARDS, COLUMNS_Y, months=5, half=0.36), frames=8),
            Label("column order", CARDS[0] - 0.2, COLUMNS_Y, names="columns", ha="right", size=12),
            *[
                Label(s, _card(k), COLUMNS_Y, names="columns", ha="center", size=14)
                for k, s in enumerate(COLUMNS)
            ],
            _stroke(
                "no-close",
                _cross(_card(hole), COLUMNS_Y - 0.66, r=0.1),
                color=LOST,
                frames=2,
            ),
            Label(
                "no close",
                _card(hole) + 0.3,
                COLUMNS_Y - 0.66,
                names="no-close",
                color=LOST,
                size=11,
            ),
            *pairs,
            _stroke(
                f"pair-{hole}",
                _arrow(_card(hole), COLUMNS_Y + 0.42, _card(hole), SORTED_Y - 0.42),
                color=LOST,
                frames=3,
            ),
            _stroke("dropped", _ring(np.array([_card(hole)]), one, pad=0.4), color=LOST, frames=4),
            Label(
                f"{SORTED[hole]} dropped: {NO_CLOSE} has no close",
                CARDS[1] + 0.3,
                3.1,
                names="dropped",
                color=LOST,
                size=12,
            ),
            _stroke(
                "kept",
                _ring(np.array([_card(SORTED.index(NO_CLOSE))]), one, pad=0.4),
                color=ACCENT,
                frames=4,
            ),
            Label(
                f"{NO_CLOSE} ranked anyway",
                CARDS[1] + 0.3,
                2.6,
                names="kept",
                color=ACCENT,
                size=12,
            ),
            Label(
                "each check reads the column, not the stock",
                CARDS[0],
                0.3,
                names="kept",
                color=MUTED,
                size=11,
            ),
        ),
    )


#: The empty-months scene's strip of months, from the first to the last.
MONTHS_X = (0.7, 9.3)
MONTHS_Y = 2.75


def _month(k: int, months: int) -> float:
    """Month ``k`` of ``months``, counting from 1, along the strip."""
    return MONTHS_X[0] + (MONTHS_X[1] - MONTHS_X[0]) * (k - 1) / (months - 1)


def _empty_months(f: RuleFigures) -> Scene:
    """Example 7.7's rule 3: the months each mean divides by."""
    months = 1 + f.empty_months + f.held_months
    first_held = 2 + f.empty_months
    empty = np.array([_month(k, months) for k in range(2, first_held)])
    held = np.array([_month(k, months) for k in range(first_held, months + 1)])
    return Scene(
        "Which months the mean counts",
        "rule_empty_months",
        (
            _stroke("missing", _circle(_month(1, months), MONTHS_Y, 0.06), color=MUTED, width=1.4),
            Label("month 1: no return", 0.6, 2.38, names="missing", color=MUTED, size=10),
            Stroke("empty", empty, np.full(len(empty), MONTHS_Y), color=MUTED, frames=4, dots=4.0),
            Label(
                f"{f.empty_months} months with no position, each a 0",
                0.6,
                3.35,
                names="empty",
                color=MUTED,
                size=11,
            ),
            Stroke("held", held, np.full(len(held), MONTHS_Y), frames=10, dots=4.0),
            Label(
                f"{f.held_months} months that hold positions",
                MONTHS_X[1],
                3.35,
                names="held",
                ha="right",
                size=11,
            ),
            _stroke("first", _span(_month(2, months), _month(months, months), 1.9), frames=8),
            Label(
                f"first edition: sum ÷ {f.first_edition_months}",
                5.0,
                1.5,
                names="first",
                ha="center",
                size=12,
            ),
            _stroke(
                "revised",
                _span(_month(first_held, months), _month(months, months), 0.9),
                color=ACCENT,
                frames=8,
            ),
            Label(
                f"revised: sum ÷ {f.held_months}",
                5.6,
                0.5,
                names="revised",
                color=ACCENT,
                ha="center",
                size=12,
            ),
        ),
    )


#: The own-month-end scene's last five trading days, and its two stocks' rows.
DAYS_X = (2.4, 3.5, 4.6, 5.7, 6.8)
A_Y, B_Y = 2.75, 1.75
#: How many of those days stock B has a price on.
B_PRICED = 3


def _own_month_end() -> Scene:
    """Example 7.7's rule 5: the shared month-end row against each stock's own last day."""
    last = DAYS_X[-1]
    own = DAYS_X[B_PRICED - 1]
    return Scene(
        "Where a month ends",
        "rule_own_month_end",
        (
            Fill("shared", last - 0.3, 1.25, last + 0.3, 3.2, TINT),
            Label("shared month-end row", last, 3.6, names="shared", ha="center", size=12),
            Stroke("a", np.array(DAYS_X), np.full(len(DAYS_X), A_Y), frames=4, dots=8.0),
            Label("stock A", DAYS_X[0] - 0.4, A_Y, names="a", ha="right", size=12),
            Stroke("b", np.array(DAYS_X[:B_PRICED]), np.full(B_PRICED, B_Y), frames=2, dots=8.0),
            Label("stock B", DAYS_X[0] - 0.4, B_Y, names="b", ha="right", size=12),
            _stroke("b-missing", _cross(last, B_Y), color=LOST, frames=2),
            Label("missing", last + 0.45, B_Y, names="b-missing", color=LOST, size=12),
            _stroke(
                "b-own", _ring(np.array([own]), np.array([B_Y]), pad=0.25), color=GOOD, frames=4
            ),
            Label(
                "B’s own last priced day, which the revised Python reads",
                DAYS_X[0] - 1.5,
                0.85,
                names="b-own",
                color=GOOD,
                size=12,
            ),
            Label(
                "the month’s last five trading days",
                DAYS_X[0] - 1.5,
                0.35,
                names="b-own",
                color=MUTED,
                size=11,
            ),
        ),
    )


#: The lookup scene's strip, which stands for the month-end rows, and its cells.
ROWS = (0.8, 6.2, 2.7)
ROW_CELLS = 16
ASKED_X = 8.6


def _month_end_lookup(f: RuleFigures) -> Scene:
    """Example 7.7's rule 8: the first pass asks the month-end rows for a daily row."""
    x0, x1, y = ROWS
    repaired = x0 + (f.repaired_row - 0.5) * (x1 - x0) / f.month_end_rows
    return Scene(
        "A lookup past the end",
        "rule_month_end_lookup",
        (
            _stroke("rows", _cells(x0, x1, y, months=ROW_CELLS, half=0.22), frames=8),
            Label(
                f"{f.month_end_rows} month-end rows",
                (x0 + x1) / 2,
                3.3,
                names="rows",
                ha="center",
                size=12,
            ),
            Label("row 1", x0, y - 0.56, names="rows", color=MUTED, ha="center", size=11),
            Label(
                f"row {f.month_end_rows}",
                x1,
                y - 0.56,
                names="rows",
                color=MUTED,
                ha="center",
                size=11,
            ),
            _stroke("past", _line([(x1, y), (ASKED_X, y)]), color=MUTED, dashed=True, frames=5),
            _stroke("asks", _cross(ASKED_X, y), color=LOST, frames=2),
            Label(
                f"row {f.first_pass_row}",
                ASKED_X,
                3.3,
                names="asks",
                color=LOST,
                ha="center",
                size=12,
            ),
            Label(
                "the first pass asks for it and stops",
                9.6,
                1.75,
                names="asks",
                color=LOST,
                ha="right",
                size=12,
            ),
            _stroke("repair", _arrow(repaired, 1.05, repaired, y - 0.3), color=GOOD, frames=4),
            Label(
                f"the repair reads row m − 1, here {f.repaired_row}",
                repaired + 0.2,
                0.75,
                names="repair",
                color=GOOD,
                size=12,
            ),
        ),
    )


def rule_scenes(figures: RuleFigures | None = None) -> tuple[Scene, ...]:
    """The seven rule scenes in the order the post reads them: Example 7.6's
    rules 2 and 3, then Example 7.7's rules 1, 2, 3, 5 and 8."""
    f = figures if figures is not None else RuleFigures()
    return (
        _short_side(f),
        _filled_close(f),
        _sum_or_mean(),
        _wrong_close(),
        _empty_months(f),
        _own_month_end(),
        _month_end_lookup(f),
    )


@dataclass(frozen=True)
class SplitFigures:
    """The figures the split-swing sketch draws, from Chan's S&P 500 file.

    Each is the revised Python's: the annual return of its 13 months before
    2002 and of its 70 from 2002, and the sum of its months in 2002 and in
    2006. A year's sum is twelve times its mean, so it is in the same units
    as a half's annual return. ``TestTheYearsInsideTheSplit`` in
    ``tests/test_equity_seasonals.py`` derives each one from the file.
    """

    before_2002: float = -0.14538748140058178
    from_2002: float = 0.011966696363436455
    year_2002: float = 0.22273245297832958
    year_2006: float = -0.13191102457761186


#: The split-swing scene's zero line, its scale in board units per unit of
#: return, and where each group's two bars and its bracket stand.
SWING_ZERO, SWING_PER = 2.1, 5.0
HALVES_X, YEARS_X = (1.75, 3.0), (6.1, 7.5)
HALVES_GAP_X, YEARS_GAP_X = 3.75, 8.0


def _swing_y(r: float) -> float:
    return SWING_ZERO + r * SWING_PER


def _bar(x: float, r: float) -> tuple:
    return _line([(x, SWING_ZERO), (x, _swing_y(r))])


def _bracket(x: float, low: float, high: float) -> tuple:
    """An upright bracket at ``x`` from return ``low`` to ``high``, opening left."""
    return _line(
        [
            (x - 0.1, _swing_y(low)),
            (x, _swing_y(low)),
            (x, _swing_y(high)),
            (x - 0.1, _swing_y(high)),
        ]
    )


def _with_sign(value: float, places: int) -> str:
    """The value with its sign always shown, and a true minus."""
    return f"{value:+.{places}f}".replace("-", "−")


def _sign_color(r: float) -> str:
    return GOOD if r > 0 else LOST


def _split_swing(f: SplitFigures) -> Scene:
    """Lesson 2's split: the two halves' annual returns against two single years.

    The bars and brackets are to one scale, so the years' bracket is as much
    longer than the halves' as their gap is wider.
    """
    (before_x, after_x), (y2002_x, y2006_x) = HALVES_X, YEARS_X
    halves_gap = abs(f.from_2002 - f.before_2002)
    years_gap = abs(f.year_2002 - f.year_2006)
    return Scene(
        "One year swings more than the split",
        "split_swing",
        (
            _stroke("zero", _line([(1.1, SWING_ZERO), (3.35, SWING_ZERO)]), color=MUTED, frames=3),
            Label(
                "the two halves, per year",
                sum(HALVES_X) / 2,
                3.65,
                names="zero",
                ha="center",
                size=12,
            ),
            _stroke(
                "before",
                _bar(before_x, f.before_2002),
                color=_sign_color(f.before_2002),
                width=9.0,
                frames=3,
            ),
            Label(
                "before 2002",
                before_x,
                min(_swing_y(f.before_2002), SWING_ZERO) - 0.38,
                names="before",
                ha="center",
                size=11,
            ),
            Label(
                _with_sign(f.before_2002, 6),
                before_x - 0.25,
                (_swing_y(f.before_2002) + SWING_ZERO) / 2,
                names="before",
                color=_sign_color(f.before_2002),
                ha="right",
                size=10,
            ),
            _stroke(
                "after",
                _bar(after_x, f.from_2002),
                color=_sign_color(f.from_2002),
                width=9.0,
                frames=1,
            ),
            Label(
                "from 2002", after_x - 0.15, SWING_ZERO - 0.42, names="after", ha="center", size=11
            ),
            Label(
                _with_sign(f.from_2002, 6),
                after_x,
                max(_swing_y(f.from_2002), SWING_ZERO) + 0.38,
                names="after",
                color=_sign_color(f.from_2002),
                ha="center",
                size=10,
            ),
            _stroke(
                "halves-gap",
                _bracket(HALVES_GAP_X, f.before_2002, f.from_2002),
                color=ACCENT,
                frames=4,
            ),
            Label(
                f"{halves_gap:.4f} apart",
                HALVES_GAP_X + 0.25,
                _swing_y((f.before_2002 + f.from_2002) / 2),
                names="halves-gap",
                color=ACCENT,
                size=11,
            ),
            _stroke(
                "zero-years", _line([(5.5, SWING_ZERO), (7.85, SWING_ZERO)]), color=MUTED, frames=3
            ),
            Label(
                "two single years", sum(YEARS_X) / 2, 3.65, names="zero-years", ha="center", size=12
            ),
            _stroke(
                "y2002",
                _bar(y2002_x, f.year_2002),
                color=_sign_color(f.year_2002),
                width=9.0,
                frames=4,
            ),
            Label("2002", y2002_x, SWING_ZERO - 0.38, names="y2002", ha="center", size=11),
            Label(
                _with_sign(f.year_2002, 4),
                y2002_x - 0.25,
                (_swing_y(f.year_2002) + SWING_ZERO) / 2,
                names="y2002",
                color=_sign_color(f.year_2002),
                ha="right",
                size=10,
            ),
            _stroke(
                "y2006",
                _bar(y2006_x, f.year_2006),
                color=_sign_color(f.year_2006),
                width=9.0,
                frames=3,
            ),
            Label("2006", y2006_x, SWING_ZERO + 0.38, names="y2006", ha="center", size=11),
            Label(
                _with_sign(f.year_2006, 4),
                y2006_x,
                _swing_y(f.year_2006) - 0.36,
                names="y2006",
                color=_sign_color(f.year_2006),
                ha="center",
                size=10,
            ),
            _stroke(
                "years-gap",
                _bracket(YEARS_GAP_X, f.year_2006, f.year_2002),
                color=ACCENT,
                frames=5,
            ),
            Label(
                f"{years_gap:.4f} apart",
                YEARS_GAP_X + 0.25,
                _swing_y((f.year_2006 + f.year_2002) / 2),
                names="years-gap",
                color=ACCENT,
                size=11,
            ),
            Label(
                "each bar adds up a year of monthly returns, the halves’ on average, before costs",
                0.6,
                0.35,
                names="years-gap",
                color=MUTED,
                size=11,
            ),
        ),
    )


def split_scenes(figures: SplitFigures | None = None) -> tuple[Scene, ...]:
    """The one scene for Lesson 2's split."""
    return (_split_swing(figures if figures is not None else SplitFigures()),)


@dataclass(frozen=True)
class Verdicts:
    """What the verdicts scene draws, each field read from a registered run.

    The January run is :func:`chan.equity_seasonals.run_point_in_time`, and
    the monthly run :func:`chan.equity_seasonals.run_monthly_point_in_time`
    under :data:`chan.equity_seasonals.REVISED_MATLAB`.

    - ``january_low`` and ``january_high``: the low and high series' mean
      return per January.
    - ``monthly_mean``: the monthly run's mean held month.
    - ``detectable``: the monthly run's X, the annual return its test detects
      with 80 percent probability.
    - ``january_low_rejects``, ``january_high_rejects`` and
      ``monthly_rejects``: whether each series' one-sided test rejects a mean
      of zero, which is what each registered verdict turns on.
    """

    january_low: float
    january_high: float
    monthly_mean: float
    detectable: float
    january_low_rejects: bool
    january_high_rejects: bool
    monthly_rejects: bool

    @classmethod
    def from_runs(
        cls, january: seasonals.PointInTimeRun, monthly: seasonals.MonthlyRun
    ) -> Verdicts:
        return cls(
            january_low=january.low.mean,
            january_high=january.high.mean,
            monthly_mean=monthly.matlab.test.mean,
            detectable=monthly.matlab.x,
            january_low_rejects=january.low.rejects,
            january_high_rejects=january.high.rejects,
            monthly_rejects=monthly.matlab.test.rejects,
        )


@dataclass(frozen=True)
class Spans:
    """The years the timeline scene draws, each read from the data or the runs.

    ``large_caps`` and ``small_caps`` are the first and last dates of Chan's
    two files as :func:`chan.series.load_panel` reads them. ``later`` runs
    over the monthly run's held months, January 2009 to September 2026, from
    :data:`chan.equity_seasonals.FIRST_HELD` and
    :data:`chan.equity_seasonals.LAST_HELD`, which hold the January run's
    eighteen Januaries from 2009 to 2026 too. ``split`` is
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
    two ends of one bracket that straddles zero. Heston and Sadka's line
    carries the run's mean, a year's worth of its mean month, as a dot at
    zero, and tints the returns from zero to X, which a true return of that
    size could pass unseen. Each line has its own scale.

    The words are the registered verdicts, so a run whose verdicts differ is
    refused rather than drawn.

    1. "free data cannot decide" needs the high series to reject zero and the
       low series not to, and the bracket to straddle zero.
    2. "could pass unseen" needs the monthly run not to reject zero, and its
       mean to sit nearer zero than X on either side.
    """
    low, high = verdicts.january_low, verdicts.january_high
    if not low < 0 < high:
        raise ValueError(f"the January bracket {low} to {high} does not straddle zero")
    if verdicts.january_low_rejects or not verdicts.january_high_rejects:
        raise ValueError("free data decides the January verdict, so the words would be false")
    if verdicts.monthly_rejects:
        raise ValueError("the monthly run rejects zero, so a return was detected")
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
            Label("per January", 0.3, JANUARY_Y - 0.38, names="january-line", size=11),
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
            Label("per year", 0.3, MONTHLY_Y - 0.38, names="monthly-line", size=11),
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
                f"about {100 * verdicts.detectable:.1f}% a year",
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
                "could pass unseen",
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
#: The bar for Heston and Sadka's 13 percent is drawn solid from this year,
#: with a dashed lead-in before it, because nothing here has checked where
#: their sample starts.
SAMPLE_FROM = 1968
#: The book's first edition, which the post cites as Chan (2009).
BOOK_YEAR = 2009


def _year(when: pd.Timestamp | float) -> float:
    """Where a date or a fractional year sits on the timeline."""
    year = when if isinstance(when, float | int) else when.year + (when.dayofyear - 1) / 365.25
    lo, hi = YEARS
    x0, x1 = TIMELINE_X
    return x0 + (year - lo) / (hi - lo) * (x1 - x0)


def _which_years(spans: Spans) -> Scene:
    """Which years each source reads, on one axis to scale.

    The years behind Heston and Sadka's 13 percent end at the start of 2002,
    where Chan says the effect disappeared. That end is Chan's split, not a
    date read from their paper. Chan's two files are short and end before the
    book's first edition. The two registered runs start that year and run to
    2026.
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
    book = _year(float(BOOK_YEAR))
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
            "Heston and Sadka’s 13%, before 2002",
            _year(float(lo)) + 0.05,
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
            _line([(_year(first), later_y), (_year(last), later_y)]),
            color=GOOD,
            width=5.0,
            frames=6,
        ),
        Label(
            "two later runs, index as it stood",
            _year(first) - 0.2,
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
    opening's two first, then the two strategies', then the seven rules',
    then the split's.

    ``spans`` is read from Chan's two committed files when it is not handed
    in. ``verdicts`` is read from the two registered runs on the owner's
    archive, about twenty seconds. Every GIF but the verdicts sketch is
    written before that read, so a refused or missing archive leaves the
    other eleven redrawn and raises from the read.
    """
    folder = out_dir if out_dir is not None else FIGURES_DIR
    spans = spans if spans is not None else Spans.read()
    paths = [_write(_which_years(spans), folder)]
    strategies = [_write(scene, folder) for scene in scenes()]
    rules = [_write(scene, folder) for scene in rule_scenes()]
    split = [_write(scene, folder) for scene in split_scenes()]
    if verdicts is None:
        verdicts = Verdicts.from_runs(
            seasonals.run_point_in_time(), seasonals.run_monthly_point_in_time()
        )
    paths.append(_write(_two_verdicts(verdicts), folder))
    return paths + strategies + rules + split


#: The refusals a redraw can meet in reading the archive, the ones
#: :func:`chan.equity_seasonals.main` turns into one line.
REFUSALS = (
    VintageUnavailable,
    ArchiveUnavailable,
    ArchiveRefused,
    seasonals.PointInTimeRefused,
    seasonals.MonthlyRunRefused,
    PanelRefused,
)


def main() -> None:
    try:
        paths = make_equity_seasonals_whiteboards()
    except REFUSALS as refused:
        # The other eleven GIFs are already written. The one left stale is
        # named, and the exit is non-zero, so a redraw on a machine without
        # the archive does not read as a full one.
        raise SystemExit(f"{GIF_PREFIX}two_verdicts.gif was not redrawn: {refused}") from refused
    for path in paths:
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
