"""Whiteboard sketches for the AUD.CAD rollover post, one for Lesson 2 and one for Lesson 3.

``blog/aud-cad-rollover-lessons.md`` explains in Lesson 2 why annualising the
average daily rollover interest over 365 days overstates the year, and in
Lesson 3 why a strategy that is long and short in turns earns rollover
interest only on its net position. This module draws two scenes, and the post
places each right after the text it draws.

1. Five trading days pay for seven, after Lesson 2's list of the two readings
   that land inside the pass mark. Two rows of five weekdays, AUD above CAD,
   each day holding the days of interest it pays: one, except AUD's Wednesday
   and CAD's Thursday, which pay three. A brace under each row says the five
   trading days pay seven days of interest. A green branch multiplies the
   average by 252 trading days and ends at 3.26 percent, and a red one
   multiplies it by 365 and ends at 4.73 percent, which counts every weekend
   again. The rows are schematic, a week at a constant rate, but each day's
   count is read from :func:`chan.aud_cad_rollover.daily_rates` on that rate,
   so the tripling the script applies is what the rows draw. The two
   percentages and the ratio 365 / 252 are the run's.
2. Long and short days cancel, after Lesson 3's paragraph opening "Net
   position explains the cost." One bar of the 1,217 days the rule holds a
   position, to scale, green for the 510 days long and red for the 707 short.
   A grey bracket pairs the 510 long days with 510 of the short ones, and a
   thinner grey line laid over those days says they cancel. A red bracket
   marks the 197 short days left over, 16.2 percent of the days held. That
   share times the 3.26 percent a year gives −0.528 percent, beside the
   −0.522 percent that rollover interest added to the returns. The bar groups
   the days by side rather than by date, since the rule changes sides
   throughout the sample. That grouping is the one schematic part.

Every figure comes from :class:`RunFigures`, which
:meth:`RunFigures.from_run` reads from :func:`chan.aud_cad_rollover.aud_cad_rollover`
on Chan's committed files. ``tests/test_aud_cad_rollover_whiteboard.py`` reads
the same run, so no figure is typed into a scene.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look, frame rate and colours. The
second sketch carries seven figures, so it is in :data:`PACED`: each label
shows 900 ms rather than 350, and the finished drawing holds 12 seconds rather
than 4, as :func:`sketch_timeline` sets. Each GIF is named :data:`GIF_PREFIX`
plus the scene's slug, and a redraw with no change is a no-op diff. Redraw
both with::

    uv run python -m chan.aud_cad_rollover_whiteboard
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from chan.aud_cad_rollover import (
    AUD_TRIPLE_WEEKDAY,
    CAD_TRIPLE_WEEKDAY,
    DAYS_IN_YEAR,
    SCRIPT_LOOKBACK,
    Rollover,
    aud_cad_rollover,
    daily_rates,
    read_sources,
)
from chan.khandani_lo import TRADING_DAYS
from chan.matlab_helpers import lag1
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    Frame,
    Label,
    Scene,
    Stroke,
    _arrow,
    _check,
    _line,
    _span,
    _stroke,
    render,
    timeline,
)

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "aud_cad_rollover_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``aud_cad_rollover_long_short_cancel.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


def _signed(value: float, places: int) -> str:
    """``value`` to ``places`` decimals with a typographic minus, as the post prints it."""
    return f"{value:.{places}f}".replace("-", "−")


@dataclass(frozen=True)
class RunFigures:
    """The figures the two sketches print, all from the run on Chan's files.

    ``long_days`` and ``short_days`` count the days the lagged position is
    long and short, over the days after the first ``SCRIPT_LOOKBACK``, which
    is the position each day's return carries. The unlagged position gives a
    different count, because it is one day earlier. ``long_rate`` and
    ``short_rate`` are the rollover interest annualised over 252 days and
    averaged over the days held long and the days held short.
    """

    long_days: int
    short_days: int
    rollover: float
    over_365_days: float
    rollover_drag: float
    long_rate: float
    short_rate: float

    @classmethod
    def from_run(cls, result: Rollover) -> RunFigures:
        held = lag1(result.position)[SCRIPT_LOOKBACK:]
        term = lag1(np.log(1 + result.aud) - np.log(1 + result.cad))[SCRIPT_LOOKBACK:]
        return cls(
            long_days=int((held > 0).sum()),
            short_days=int((held < 0).sum()),
            rollover=result.rollover,
            over_365_days=result.over_365_days,
            rollover_drag=result.rollover_drag,
            long_rate=float(TRADING_DAYS * term[held > 0].mean()),
            short_rate=float(TRADING_DAYS * term[held < 0].mean()),
        )

    @property
    def held_days(self) -> int:
        return self.long_days + self.short_days

    @property
    def net_share(self) -> float:
        """The net position as a share of the days held, negative when net short."""
        return (self.long_days - self.short_days) / self.held_days

    @property
    def predicted(self) -> float:
        """The net share times the annualised rollover interest."""
        return self.net_share * self.rollover


def read_figures() -> RunFigures:
    """The run on Chan's committed files, without the report ``run`` prints."""
    sources = read_sources()
    return RunFigures.from_run(aud_cad_rollover(sources.closes[1], sources.aud[1], sources.cad[1]))


# --- Lesson 2: five trading days pay for seven -------------------------------

#: The week the rows draw, Monday 2007-07-23 to Friday 2007-07-27, the first
#: week of Chan's closes, at a constant 3.65 percent a year, which is 0.0001 a
#: day as the post's three ideas say. Any constant rate gives the same counts.
WEEK = pd.bdate_range("2007-07-23", periods=5)
CONSTANT_RATE = 3.65

#: The rows' cells, from left to right, and each row's height.
CELLS_X = (1.1, 4.6)
CELL_HALF = 0.34
AUD_Y, CAD_Y = 3.25, 1.62
#: How far below a row's cells its brace starts and ends, and where its words sit.
BRACE_DROP = (0.12, 0.28)
BRACE_LABEL_DROP = 0.6

#: Where the two branches and the note sit, on the right of the rows.
BRANCH_X = (5.3, 7.3)
GREEN_Y, RED_Y = 3.15, 1.9


NUMBER_WORDS = {5: "five", 7: "seven"}


def _word(n: int) -> str:
    """A small count spelt as the title spells it, or its digits for any other."""
    return NUMBER_WORDS.get(n, str(n))


def week_days_paid(triple_weekday: int) -> tuple[int, ...]:
    """The days of interest each weekday of :data:`WEEK` pays, read from the script's rule.

    Each is the day's rate from :func:`daily_rates` divided by one calendar
    day's rate, on a constant rate, so a change to the tripling rule moves it.
    """
    monthly = pd.Series([CONSTANT_RATE], index=pd.DatetimeIndex(["2007-07-01"]))
    one_day = CONSTANT_RATE / DAYS_IN_YEAR / 100
    paid = daily_rates(monthly, WEEK, triple_weekday) / one_day
    return tuple(int(round(days)) for days in paid)


def _cell_x(k: int) -> tuple[float, float]:
    width = (CELLS_X[1] - CELLS_X[0]) / len(WEEK)
    return CELLS_X[0] + k * width, CELLS_X[0] + (k + 1) * width


def _row(y: float) -> tuple:
    """Five cells in a strip, outlined, then each divider drawn down and back up."""
    x0, x1 = CELLS_X
    low, high = y - CELL_HALF, y + CELL_HALF
    points = [(x0, low), (x1, low), (x1, high), (x0, high), (x0, low)]
    for k in range(1, len(WEEK)):
        x = _cell_x(k)[0]
        points += [(x, low), (x, high)] if k % 2 else [(x, high), (x, low)]
    return _line(points)


def _cell(k: int, y: float) -> tuple:
    """One cell's outline, drawn over the strip to mark it."""
    x0, x1 = _cell_x(k)
    low, high = y - CELL_HALF, y + CELL_HALF
    return _line([(x0, low), (x1, low), (x1, high), (x0, high), (x0, low)])


def _brace(x0: float, x1: float, top: float, bottom: float) -> tuple:
    """A brace opening upward, from ``x0`` to ``x1``, its point down at the middle."""
    middle = (top + bottom) / 2
    centre = (x0 + x1) / 2
    return _line(
        [
            (x0, top),
            (x0 + 0.12, middle),
            (centre - 0.12, middle),
            (centre, bottom),
            (centre + 0.12, middle),
            (x1 - 0.12, middle),
            (x1, top),
        ],
        per_unit=8,
    )


def _week_row(name: str, y: float, paid: tuple[int, ...]) -> list:
    """One currency's row, its days of interest in each cell, and its brace."""
    gid = name.lower()
    steps: list = [
        _stroke(f"{gid}-row", _row(y), frames=8),
        Label(name, 0.3, y, names=f"{gid}-row", size=14),
    ]
    for k, days in enumerate(paid):
        centre = sum(_cell_x(k)) / 2
        if days == 1:
            # An ordinary day pays its own day's interest, in the row's ink.
            steps.append(Label("1", centre, y, names=f"{gid}-row", ha="center"))
            continue
        steps += [
            _stroke(f"{gid}-tripled", _cell(k, y), color=ACCENT, width=3.0, frames=4),
            Label(str(days), centre, y, names=f"{gid}-tripled", color=ACCENT, ha="center"),
        ]
    top, bottom = y - CELL_HALF - BRACE_DROP[0], y - CELL_HALF - BRACE_DROP[1]
    steps += [
        _stroke(f"{gid}-brace", _brace(*CELLS_X, top, bottom), color=MUTED, frames=5),
        Label(
            f"{len(paid)} trading days pay {sum(paid)} days of interest",
            sum(CELLS_X) / 2,
            y - CELL_HALF - BRACE_LABEL_DROP,
            names=f"{gid}-brace",
            color=MUTED,
            ha="center",
            size=12,
        ),
    ]
    return steps


def _five_pay_seven(f: RunFigures) -> Scene:
    """Lesson 2: the tripled day pays for the weekend, so 252 annualises and 365 overstates."""
    aud = week_days_paid(AUD_TRIPLE_WEEKDAY)
    cad = week_days_paid(CAD_TRIPLE_WEEKDAY)
    if sum(aud) != sum(cad):
        raise ValueError(f"the two rows pay {sum(aud)} and {sum(cad)} days, and the title says one")
    ratio = DAYS_IN_YEAR / TRADING_DAYS
    x0, x1 = BRANCH_X
    headers = [
        Label(
            day.strftime("%a"),
            sum(_cell_x(k)) / 2,
            AUD_Y + CELL_HALF + 0.3,
            names="aud-row",
            ha="center",
            size=11,
        )
        for k, day in enumerate(WEEK)
    ]
    aud_row = _week_row("AUD", AUD_Y, aud)
    return Scene(
        f"{_word(len(WEEK)).capitalize()} trading days pay for {_word(sum(aud))}",
        "five_pay_seven",
        (
            *aud_row[:2],
            *headers,
            *aud_row[2:],
            *_week_row("CAD", CAD_Y, cad),
            _stroke("by-252", _arrow(x0, GREEN_Y, x1, GREEN_Y), color=GOOD, frames=5),
            Label(
                f"average × {TRADING_DAYS} trading days",
                x0,
                GREEN_Y + 0.45,
                names="by-252",
                color=GOOD,
                size=12,
            ),
            Label(
                f"{100 * f.rollover:.2f} percent",
                x1 + 0.2,
                GREEN_Y,
                names="by-252",
                color=GOOD,
                size=14,
            ),
            _stroke("by-365", _arrow(x0, RED_Y, x1, RED_Y), color=LOST, frames=5),
            Label(
                f"average × {DAYS_IN_YEAR} counts",
                x0,
                RED_Y + 0.82,
                names="by-365",
                color=LOST,
                size=12,
            ),
            Label("every weekend again", x0, RED_Y + 0.46, names="by-365", color=LOST, size=12),
            Label(
                f"{100 * f.over_365_days:.2f} percent",
                x1 + 0.2,
                RED_Y,
                names="by-365",
                color=LOST,
                size=14,
            ),
            Label(
                f"{100 * f.over_365_days:.2f} = {100 * f.rollover:.2f} × {DAYS_IN_YEAR} / "
                f"{TRADING_DAYS}, about {ratio:.2f} times",
                9.7,
                1.35,
                names="by-365",
                color=MUTED,
                ha="right",
                size=11,
            ),
            Label(
                "the tripled day already paid for the weekend",
                9.7,
                0.26,
                names="by-365",
                color=ACCENT,
                ha="right",
                size=14,
            ),
        ),
    )


# --- Lesson 3: long and short days cancel ------------------------------------

#: The bar of held days, to scale from its left end to its right.
BAR_X = (0.5, 9.5)
BAR_Y = 3.3
BAR_WIDTH = 14.0
BRACKET_Y = 2.85
#: The row that multiplies the net share by the rate, and the row that checks it.
PRODUCT_Y, ADDED_Y = 1.75, 1.2
PRODUCT_ARROW = (6.6, 7.35)
#: Where the two results end, so their figures sit one above the other.
RESULTS_RIGHT = 9.6
CHECK_X = 4.85
#: The grey line laid over the paired days, thinner than the bar, so the
#: colours of the days it pairs still show either side of it.
PAIRED_WIDTH = 5.0


def _day_x(days: float, f: RunFigures) -> float:
    """Where a count of held days ends along the bar, to scale."""
    return BAR_X[0] + (BAR_X[1] - BAR_X[0]) * days / f.held_days


def _bracket(x0: float, middle: float, x1: float, y: float, tick: float = 0.13) -> tuple:
    """A span from ``x0`` to ``x1`` with an upright tick at each end and at ``middle``."""
    return _line(
        [
            (x0, y + tick),
            (x0, y - tick),
            (x0, y),
            (middle, y),
            (middle, y + tick),
            (middle, y - tick),
            (middle, y),
            (x1, y),
            (x1, y + tick),
            (x1, y - tick),
        ]
    )


def _long_short_cancel(f: RunFigures) -> Scene:
    """Lesson 3: the long days and as many short days cancel, and the net short is left."""
    if f.short_days <= f.long_days:
        raise ValueError(
            f"{f.short_days} short days against {f.long_days} long ones, "
            "and the sketch says more days are short"
        )
    left, right = BAR_X
    long_end = _day_x(f.long_days, f)
    paired_end = _day_x(2 * f.long_days, f)
    a0, a1 = PRODUCT_ARROW
    return Scene(
        "Long and short days cancel",
        "long_short_cancel",
        (
            _stroke(
                "long",
                _line([(left, BAR_Y), (long_end, BAR_Y)]),
                color=GOOD,
                width=BAR_WIDTH,
                frames=6,
            ),
            Label(
                f"{f.long_days:,} days long: earn the rollover",
                left,
                BAR_Y + 0.45,
                names="long",
                color=GOOD,
                size=12,
            ),
            _stroke(
                "short",
                _line([(long_end, BAR_Y), (right, BAR_Y)]),
                color=LOST,
                width=BAR_WIDTH,
                frames=6,
            ),
            Label(
                f"{f.short_days:,} days short: pay it",
                right,
                BAR_Y + 0.45,
                names="short",
                color=LOST,
                ha="right",
                size=12,
            ),
            _stroke(
                "cancel", _bracket(left, long_end, paired_end, BRACKET_Y), color=MUTED, frames=6
            ),
            _stroke(
                "paired",
                _line([(left, BAR_Y), (paired_end, BAR_Y)]),
                color=MUTED,
                width=PAIRED_WIDTH,
                frames=6,
            ),
            Label("cancel", (left + long_end) / 2, BRACKET_Y - 0.45, names="cancel", color=MUTED),
            _stroke("leftover", _span(paired_end, right, BRACKET_Y), color=LOST, frames=4),
            Label(
                f"{f.short_days - f.long_days:,} more days short: "
                f"{_signed(100 * f.net_share, 1)} percent of days held",
                right,
                BRACKET_Y - 0.45,
                names="leftover",
                color=LOST,
                ha="right",
                size=12,
            ),
            _stroke("times-rate", _arrow(a0, PRODUCT_Y, a1, PRODUCT_Y), color=INK, frames=4),
            Label(
                f"× {100 * f.rollover:.2f} percent a year",
                a0 - 0.2,
                PRODUCT_Y,
                names="times-rate",
                ha="right",
                size=12,
            ),
            Label(
                f"{_signed(100 * f.predicted, 3)} percent",
                RESULTS_RIGHT,
                PRODUCT_Y,
                names="times-rate",
                ha="right",
                size=13,
            ),
            _stroke("checks-out", _check(CHECK_X, ADDED_Y - 0.02), color=GOOD, frames=4),
            Label(
                f"rollover added: {_signed(100 * f.rollover_drag, 3)} percent",
                RESULTS_RIGHT,
                ADDED_Y,
                ha="right",
                names="checks-out",
                color=GOOD,
                size=13,
            ),
            Label(
                f"they cancel because long days see {100 * f.long_rate:.3f} "
                f"and short days {100 * f.short_rate:.3f} percent a year",
                0.4,
                0.7,
                names="checks-out",
                color=MUTED,
                size=11,
            ),
            Label(
                "what is left is the net position",
                9.7,
                0.3,
                names="checks-out",
                color=ACCENT,
                ha="right",
                size=14,
            ),
        ),
    )


def scenes(figures: RunFigures | None = None) -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them, on the run's figures by default."""
    f = read_figures() if figures is None else figures
    return (_five_pay_seven(f), _long_short_cancel(f))


#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
PACED = ("long_short_cancel",)
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


def make_aud_cad_rollover_whiteboards(
    out_dir: Path | None = None, figures: RunFigures | None = None
) -> list[Path]:
    """Write both GIFs into ``out_dir``, ``docs/figures`` by default, and return their paths."""
    folder = FIGURES_DIR if out_dir is None else out_dir
    folder.mkdir(parents=True, exist_ok=True)
    return [_write(scene, folder) for scene in scenes(figures)]


def main() -> None:
    for path in make_aud_cad_rollover_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
