"""The whiteboard sketch in the post on Chan's buy on gap.

``blog/buy-on-gap-lessons.md`` states the strategy's rules in words, and the
first two of them set two levels the open has to land between. It must fall
more than one 90-day standard deviation below the previous day's low, and it
must stay above the 20-day moving average of closes. A reader gets more from
a picture of the two levels than from the sentence, so this module draws one
scene, sketched stroke by stroke as if on a whiteboard, as a looping GIF the
post places right after the paragraph that opens "Chan gives a reason for rule
2".

1. Where the open has to land: a price axis with three levels across it, the
   previous day's low, a dashed line at that low times one less the standard
   deviation, and the 20-day average lower still. A green band between the
   dashed line and the average is where an open qualifies, and a brown dot
   for the day's open lands in it. Rule 3 then buys the ten deepest drops
   among the day's qualifiers, so an open in the band is not always bought,
   which is why the band says it qualifies rather than that it is bought. A
   red hatched zone below the average carries Chan's reason for the second
   rule, and a brown arrow from the open to the close says the position is
   sold at the close.

The sketch is not schematic. It draws one real stock on one real day to
scale, so every level stands at an affine function of its price. That day is
PCS on 2011-01-06, named by :data:`EXAMPLE_SYMBOL` and :data:`EXAMPLE_DAY`
rather than searched for, and the post's review chose it for three reasons.

1. PCS is the only stock the run bought that day, so the one open drawn is
   the whole of that day's book.
2. Its four levels stand far enough apart for each to carry its own label at
   a scale the board can hold.
3. Its close gains on the open but stays under both the dashed line and the
   previous low, so the sketch shows that the trade earns on any rise from the
   open and needs no return to where the stock traded the day before.

Every figure the sketch prints is read rather than written in.
:func:`read_gap_day` reads the committed file through
:func:`chan.buy_on_gap.read_sources`, and takes the spread, the entry price,
the average and the day's positions from :mod:`chan.buy_on_gap`'s own
functions, so the dashed line is the same ``buyPrice`` the run compares the
open against. A day whose figures would make the words false is refused rather
than drawn. The open has to sit strictly between the dashed line and the
average, as ``bog.m``'s comparisons require, so an open exactly on either line
is refused. The dashed line has to sit below the previous low, the close has
to sit above the open and below the dashed line, and the stock has to be the
only one bought that day.

The strokes, the timeline and the renderer are
:mod:`chan.usdcad_tests_whiteboard`'s, so an edit there changes this GIF too,
and that module's docstring explains why two draws on one machine give the
same bytes. Redraw it with::

    uv run python -m chan.buy_on_gap_whiteboard
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from chan.buy_on_gap import (
    buy_on_gap,
    entry_price,
    entry_spread,
    read_sources,
    trailing_average,
)
from chan.matlab_helpers import backshift
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    TINT,
    Fill,
    Label,
    Scene,
    Stroke,
    _arrow,
    _box,
    _dot,
    _hatched,
    _line,
    _stroke,
    render,
    timeline,
)
from chan.vintage import VintageUnavailable

#: Each scene's GIF is this prefix, the scene's slug, and ``.gif``.
GIF_PREFIX = "buy_on_gap_"

#: The stock and the day the sketch draws, chosen for the reasons the module
#: docstring gives.
EXAMPLE_SYMBOL = "PCS"
EXAMPLE_DAY = pd.Timestamp("2011-01-06")

#: Where the price axis stands, and where the levels across it end.
AXIS_X = 2.4
LINES_END = 5.2
#: Where the labels to the right of the levels start, and where those to the
#: left of the axis end.
RIGHT_X = 5.4
LEFT_X = 2.2
#: The heights the 20-day average and the previous low are drawn at. Every
#: other price stands at the affine function of its value these two fix.
AVERAGE_Y = 1.3
LOW_Y = 3.5
#: The bottom of the red zone below the average, which marks a region rather
#: than a price.
ZONE_BOTTOM = 0.3
#: How far the band and the zone stand inside the lines that bound them, so
#: their edges do not draw over those lines.
INSET = 0.08
#: Where the open's dot stands, and where the arrow to the close ends.
OPEN_X = 3.1
CLOSE_X = 4.7
#: The least height between two labels to the right of the levels.
LABEL_APART = 0.36
#: The width of the green edge round the pale tint, as
#: :mod:`chan.equity_seasonals_whiteboard` draws it.
TINT_EDGE = 1.2


@dataclass(frozen=True)
class GapDay:
    """One stock on one day, at the levels buy on gap compares its open with.

    - ``previous_low``: the stock's low on the day before.
    - ``spread``: the 90-day standard deviation of its daily returns, from
      :func:`chan.buy_on_gap.entry_spread`.
    - ``entry``: ``buyPrice``, the previous low times one less the spread,
      from :func:`chan.buy_on_gap.entry_price`.
    - ``average``: the 20-day moving average of its closes, from
      :func:`chan.buy_on_gap.trailing_average`.
    - ``bought``: every stock the run bought that day.
    """

    symbol: str
    day: pd.Timestamp
    previous_low: float
    spread: float
    entry: float
    open: float
    average: float
    close: float
    bought: tuple[str, ...]

    @property
    def open_to_close(self) -> float:
        """The day's return on the stock, from the open it is bought at to the close."""
        return (self.close - self.open) / self.open


def read_gap_day(
    symbol: str = EXAMPLE_SYMBOL, day: pd.Timestamp = EXAMPLE_DAY, data_dir: Path | None = None
) -> GapDay:
    """Read ``symbol`` on ``day`` from the committed file, through :mod:`chan.buy_on_gap`."""
    _, frames = read_sources(data_dir)
    opens, lows, closes = frames["Open"], frames["Low"], frames["Close"]
    op, lo, cl = (f.to_numpy(dtype=float) for f in (opens, lows, closes))
    spread = entry_spread(cl)
    t, j = opens.index.get_loc(day), opens.columns.get_loc(symbol)
    positions = buy_on_gap(opens, lows, closes).positions
    return GapDay(
        symbol=symbol,
        day=day,
        previous_low=float(backshift(1, lo)[t, j]),
        spread=float(spread[t, j]),
        entry=float(entry_price(lo, spread)[t, j]),
        open=float(op[t, j]),
        average=float(trailing_average(cl)[t, j]),
        close=float(cl[t, j]),
        bought=tuple(str(s) for s in opens.columns[positions[t] != 0]),
    )


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``buy_on_gap_where_the_open_lands.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


def _tinted(gid: str, x0: float, y0: float, x1: float, y1: float) -> tuple[Fill, Stroke]:
    """A pale tint and a thin green edge round it, so the region it marks
    reads at WCAG's 3 to 1 for graphical objects. The edge is ``gid`` plus
    ``-edge``."""
    return Fill(gid, x0, y0, x1, y1, TINT), _stroke(
        f"{gid}-edge", _box(x0, y0, x1, y1), color=GOOD, width=TINT_EDGE, frames=4
    )


def _apart(heights: list[float], apart: float) -> list[float]:
    """Each label's height, moved down where needed so it stands at least
    ``apart`` below the one above it. ``heights`` runs from the top label down."""
    placed: list[float] = []
    for height in heights:
        placed.append(height if not placed else min(height, placed[-1] - apart))
    return placed


def _refuse(day: GapDay) -> None:
    """Raise when ``day``'s figures would make the sketch's words false."""
    where = f"{day.symbol} on {day.day.date()}"
    if day.bought != (day.symbol,):
        raise ValueError(
            f"Where the open has to land draws the one stock bought that day, "
            f"and the run bought {list(day.bought)} on {day.day.date()}"
        )
    if not day.entry < day.previous_low:
        raise ValueError(
            f"Where the open has to land draws the dashed line below the previous low, "
            f"and {where} has it at {day.entry:.4f} against a low of {day.previous_low:.4f}"
        )
    if not day.average < day.open < day.entry:
        raise ValueError(
            f"Where the open has to land draws the open strictly between the dashed line "
            f"at {day.entry:.4f} and the average at {day.average:.4f}, "
            f"and {where} opened at {day.open:.4f}"
        )
    if not day.open < day.close < day.entry:
        raise ValueError(
            f"Where the open has to land draws the close above the open and under the dashed "
            f"line at {day.entry:.4f}, and {where} closed at {day.close:.4f}"
        )


def _where_the_open_lands(day: GapDay) -> Scene:
    """Rules 1 and 2 on one real day: the open lands between the dashed line and
    the average, and is sold at the close."""
    _refuse(day)

    def at(price: float) -> float:
        return AVERAGE_Y + (price - day.average) / (day.previous_low - day.average) * (
            LOW_Y - AVERAGE_Y
        )

    low, entry, opened, average, closed = (
        at(p) for p in (day.previous_low, day.entry, day.open, day.average, day.close)
    )
    band = (AXIS_X + INSET, average + INSET, LINES_END, entry - INSET)
    zone = (AXIS_X + INSET, ZONE_BOTTOM, LINES_END, average - INSET)
    low_at, entry_at, close_at = _apart([low, entry, closed], LABEL_APART)
    reason = (ZONE_BOTTOM + average) / 2
    steps: tuple[Stroke | Fill | Label, ...] = (
        _stroke("axis", _arrow(AXIS_X, ZONE_BOTTOM, AXIS_X, 3.95), color=MUTED, frames=6),
        Label("price", AXIS_X - 0.3, 3.75, names="axis", ha="right", color=MUTED, size=12),
        Label(
            f"{day.symbol} on {day.day.date()}, the only stock bought",
            9.7,
            3.95,
            names="axis",
            ha="right",
            color=MUTED,
            size=12,
        ),
        _stroke("low", _line([(AXIS_X, low), (LINES_END, low)]), frames=6),
        Label(f"yesterday’s low {day.previous_low:.2f}", RIGHT_X, low_at, names="low"),
        _stroke("entry", _line([(AXIS_X, entry), (LINES_END, entry)]), dashed=True, frames=6),
        Label(f"low × (1 − σ) {day.entry:.2f}", RIGHT_X, entry_at, names="entry"),
        _stroke("average", _line([(AXIS_X, average), (LINES_END, average)]), frames=6),
        Label(f"20-day average {day.average:.2f}", RIGHT_X, average, names="average"),
        *_tinted("band", *band),
        Label(
            "an open in this band qualifies",
            RIGHT_X,
            (band[1] + band[3]) / 2,
            names="band",
            color=GOOD,
        ),
        _dot("open", OPEN_X, opened),
        Label(f"open {day.open:.2f}", LEFT_X, opened, names="open", ha="right", color=ACCENT),
        _stroke("zone", _hatched(*zone), color=LOST, width=1.4, frames=10),
        Label("not bought", LEFT_X, reason, names="zone", ha="right", color=LOST),
        Label(
            "a large drop often carries bad news",
            RIGHT_X,
            average - 0.42,
            names="zone",
            color=LOST,
            size=12,
        ),
        Label(
            "and is less likely to revert",
            RIGHT_X,
            average - 0.76,
            names="zone",
            color=LOST,
            size=12,
        ),
        _stroke("sell", _arrow(OPEN_X + 0.2, opened + 0.06, CLOSE_X, closed), color=ACCENT),
        Label(
            f"sell at the close {day.close:.2f}",
            RIGHT_X,
            close_at,
            names="sell",
            color=ACCENT,
        ),
    )
    return Scene("Where the open has to land", "where_the_open_lands", steps)


def scenes(day: GapDay) -> tuple[Scene, ...]:
    """The post's one scene, its figures read from ``day``."""
    return (_where_the_open_lands(day),)


def make_buy_on_gap_whiteboards(
    out_dir: Path | None = None, day: GapDay | None = None
) -> list[Path]:
    """Write one looping GIF for each scene and return their paths.

    ``day`` is read from the committed file through :func:`read_gap_day` when
    it is not handed in.
    """
    day = day if day is not None else read_gap_day()
    folder = out_dir if out_dir is not None else FIGURES_DIR
    paths = []
    for scene in scenes(day):
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
        paths = make_buy_on_gap_whiteboards()
    except VintageUnavailable as refused:
        # As in chan.buy_on_gap.main, a refusal that names the source reaches
        # the operator as one line.
        raise SystemExit(str(refused)) from refused
    for path in paths:
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
