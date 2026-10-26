"""Whiteboard sketches for the post-earnings drift post, one for its strategy and one for Lesson 4.

``blog/post-earnings-drift-lessons.md`` makes two claims a sentence has to
build in the reader's head: the gap is what the rule reads and never what it
earns, and swapping one ``smartstd`` helper for the other flips one position.
This module draws the two as scenes, and the post places each right after
the text it draws.

1. One trade, two days: a time axis across the day before and the trading
   day, with one stock's price. A brass bracket over the night from the
   4:00 p.m. close to the 9:30 a.m. open marks where an announcement counts,
   the jump from that close to the open is the gap the rule reads, and a
   green bar from the open to the close is what the position holds. A red
   mark in the day before's session has its news in that close already, so
   the gap misses it, and a red mark after today's open comes too late for a
   trade opened at the open. It sits in "The strategy and the two files",
   after the list item opening "4. **The sizing.**". This sketch is
   schematic and carries no figures from the run. Its price path, the size
   of its gap and the exact times of its red marks inside their sessions
   are made up to show the order of events in one trading day. A schematic
   caption under it in the post says so.
2. One position the helper flips: a number line around 0.42 percent with
   PNW's gap on 2012-02-24 as a black dot, half the 90-day deviation that
   *Algorithmic Trading*'s ``smartstd`` gives as a green tick marked "long",
   and half the one the first edition of *Quantitative Trading* gives as a
   red tick marked "no trade", all to one scale. A closing line gives the
   day's loss on that long and the arithmetic annual return with and without
   it. It sits in Lesson 4, after the paragraph opening "The one position
   that changes is PNW". This sketch is not schematic. Every figure it prints
   and every place it puts a mark comes from :class:`HelperFlip`, which reads
   :func:`chan.pead.pead` on the committed files with each helper.

The drawing machinery is :mod:`chan.usdcad_tests_whiteboard`'s, reused rather
than copied, so these GIFs share that post's look, frame rate and colours.
Each sketch carries more than a reader takes in at that post's pace, so both
are in :data:`PACED`, and :func:`sketch_timeline` holds each of their labels
longer and their finished drawings for twelve seconds, as
:mod:`chan.equity_seasonals_whiteboard` does for its slow sketches. Each GIF
is named :data:`GIF_PREFIX` plus the scene's slug, a prefix chosen so no GIF
name starts like the post's chart, ``pead_cumulative_return.png``, or the
follow-up post's, ``pead_edgar_rerun.png``.

The sketches are deterministic for the reason that module gives, so a redraw
with no change is a no-op diff. Redraw both with::

    uv run python -m chan.pead_whiteboard
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from chan import pead
from chan.matlab_helpers import smart_moving_std, smartmean, smartstd_first_edition
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    Frame,
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
GIF_PREFIX = "pead_sketch_"


def gif_name(scene: Scene) -> str:
    """The scene's file name, such as ``pead_sketch_one_trade.gif``."""
    return f"{GIF_PREFIX}{scene.slug}.gif"


# --- The strategy: one trade, two days ------------------------------------------

#: The axis's height, and where its three ticks sit: the day before's close,
#: today's open and today's close. The night between the first two is drawn
#: narrower than the sessions, since nothing trades in it.
AXIS_Y = 0.8
PREVIOUS_CLOSE, OPEN, CLOSE = 3.4, 6.0, 9.2
#: Where the day before's session starts on the board.
SESSION_START = 0.4
#: The price at the day before's close and at today's open, in board units.
CLOSE_LEVEL, OPEN_LEVEL = 1.75, 2.75
#: The heights of the bracket over the night and the bar under today's session.
BRACKET_Y, HELD_Y = 3.35, 1.3
#: Where the two red marks sit: one inside the day before's session and one
#: inside today's, after the open.
NEWS_IN_CLOSE_X, TOO_LATE_X = 1.6, 7.4


def _session(x0: float, x1: float, start: float, end: float, seed: float) -> tuple:
    """A made-up price through one session, from ``start`` at ``x0`` to ``end`` at ``x1``."""
    x = np.linspace(x0, x1, int(round((x1 - x0) * 10)) + 1)
    t = (x - x0) / (x1 - x0)
    wiggle = 0.11 * np.sin(2.6 * np.pi * t + seed) + 0.05 * np.sin(7.1 * np.pi * t + 2 * seed)
    return x, start + (end - start) * t + wiggle * np.sin(np.pi * t)


def price_at(x: float) -> float:
    """The made-up price at ``x`` inside either session."""
    for x0, x1, start, end, seed in SESSIONS:
        if x0 <= x <= x1:
            px, py = _session(x0, x1, start, end, seed)
            return float(np.interp(x, px, py))
    raise ValueError(f"{x} falls in no session")


#: Each session's span, its price at each end and its wiggle's phase.
SESSIONS = (
    (SESSION_START, PREVIOUS_CLOSE, 1.95, CLOSE_LEVEL, 0.4),
    (OPEN, CLOSE, OPEN_LEVEL, 3.0, 1.3),
)


def _red_mark(gid: str, x: float) -> Stroke:
    """A short red upright through the price at ``x``."""
    y = price_at(x)
    return _stroke(gid, _line([(x, y - 0.3), (x, y + 0.3)], per_unit=10), color=LOST, frames=4)


def _one_trade() -> Scene:
    """The strategy: the gap is read overnight, and only the open to the close is held."""
    ticks: list[Stroke | Label] = []
    for gid, x, text in (
        ("tick-previous-close", PREVIOUS_CLOSE, "close 4:00 p.m."),
        ("tick-open", OPEN, "open 9:30 a.m."),
        ("tick-close", CLOSE, "close"),
    ):
        ticks.append(
            _stroke(
                gid,
                _line([(x, AXIS_Y - 0.12), (x, AXIS_Y + 0.12)], per_unit=12),
                color=MUTED,
                frames=2,
            )
        )
        ticks.append(Label(text, x, AXIS_Y - 0.45, names=gid, color=MUTED, size=11, ha="center"))
    before, today = SESSIONS
    night = (PREVIOUS_CLOSE + OPEN) / 2
    return Scene(
        "One trade, two days",
        "one_trade",
        (
            _stroke("axis", _line([(0.25, AXIS_Y), (9.75, AXIS_Y)]), color=MUTED, frames=8),
            *ticks,
            Label(
                "the day before",
                1.3,
                AXIS_Y - 0.45,
                names="axis",
                color=MUTED,
                size=11,
                ha="center",
            ),
            Label(
                "today",
                (OPEN + CLOSE) / 2,
                AXIS_Y - 0.45,
                names="axis",
                color=MUTED,
                size=11,
                ha="center",
            ),
            Stroke("price-before", *_session(*before), color=INK, frames=8),
            _stroke("bracket", _span(PREVIOUS_CLOSE, OPEN, BRACKET_Y), color=ACCENT, frames=5),
            Label(
                "announced here: counts",
                night,
                BRACKET_Y + 0.45,
                names="bracket",
                color=ACCENT,
                size=12,
                ha="center",
            ),
            _stroke(
                "close-level",
                _line([(PREVIOUS_CLOSE, CLOSE_LEVEL), (OPEN, CLOSE_LEVEL)]),
                color=MUTED,
                dashed=True,
                width=1.5,
                frames=4,
            ),
            _stroke(
                "gap",
                _arrow(OPEN, CLOSE_LEVEL, OPEN, OPEN_LEVEL),
                color=INK,
                frames=4,
            ),
            Label(
                "the gap: the signal",
                OPEN - 0.25,
                (CLOSE_LEVEL + OPEN_LEVEL) / 2,
                names="gap",
                size=12,
                ha="right",
            ),
            Stroke("price-today", *_session(*today), color=INK, frames=8),
            _stroke(
                "held",
                _line([(OPEN, HELD_Y), (CLOSE, HELD_Y)], per_unit=10),
                color=GOOD,
                width=7.0,
                frames=5,
            ),
            Label(
                "held: the return earned",
                7.75,
                HELD_Y + 0.45,
                names="held",
                color=GOOD,
                size=12,
                ha="center",
            ),
            Label(
                "nothing held\novernight",
                night,
                HELD_Y - 0.03,
                names="close-level",
                color=MUTED,
                size=11,
                ha="center",
            ),
            _red_mark("news-in-close", NEWS_IN_CLOSE_X),
            Label(
                "news already in the close,\nso the gap misses it",
                0.3,
                price_at(NEWS_IN_CLOSE_X) + 0.95,
                names="news-in-close",
                color=LOST,
                size=11,
            ),
            _red_mark("too-late", TOO_LATE_X),
            Label(
                "too late: the trade\nopened at 9:30",
                8.3,
                3.75,
                names="too-late",
                color=LOST,
                size=11,
                ha="center",
            ),
        ),
    )


# --- Lesson 4: one position the helper flips ------------------------------------


@dataclass(frozen=True)
class HelperFlip:
    """The one position that differs between the two ``smartstd`` helpers.

    ``gap`` is the stock's close-to-open return that day, and each ``half_*``
    is half its 90-day moving deviation under that helper, all as fractions.
    ``day_return`` is the stock's open-to-close return that day, which the
    position earns. ``arithmetic_*`` is ``pead.m``'s arithmetic annual return
    under each helper.
    """

    symbol: str
    day: str
    gap: float
    half_book_two: float
    half_first_edition: float
    day_return: float
    arithmetic_book_two: float
    arithmetic_first_edition: float

    @classmethod
    def from_run(cls, data_dir: Path | None = None) -> HelperFlip:
        """Run :func:`chan.pead.pead` on the committed files with each helper.

        It reads the files and runs the scale-break guard the way
        :func:`chan.pead.guarded_drift` does, so it is not a second read path
        that skips the guard. Book two's run is :func:`chan.pead.pead` itself.
        The first edition's runs the same steps with
        :func:`chan.matlab_helpers.smartstd_first_edition` in the moving
        deviation. It refuses unless exactly one position differs and book
        two's helper is the one that holds it.
        """
        prices, _, opens, closes, flags = pead.read_sources(data_dir)
        drift = pead.pead(opens, closes, flags)
        pead.refuse_scale_breaks(prices, opens, closes, drift.days)
        op = opens.loc[drift.days].to_numpy(dtype=float)
        cl = closes.loc[drift.days].to_numpy(dtype=float)
        announced = flags.loc[drift.days].to_numpy(dtype=float)
        gaps = pead.close_to_open(op, cl)
        book_two = smart_moving_std(gaps, pead.LOOKBACK)
        first = np.full_like(gaps, np.nan)
        for t in range(pead.LOOKBACK - 1, len(gaps)):
            first[t] = smartstd_first_edition(gaps[t - pead.LOOKBACK + 1 : t + 1], axis=0)
        held_first = pead.drift_positions(gaps, first, announced)
        differ = np.argwhere(drift.positions != held_first)
        if len(differ) != 1:
            raise ValueError(f"{len(differ)} positions differ between the helpers, not one")
        ((row, column),) = differ
        if (drift.positions[row, column], held_first[row, column]) != (1.0, 0.0):
            raise ValueError("the sketch draws a long that only book two's helper takes")
        daily_first = pead.daily_returns(held_first, op, cl)
        return cls(
            symbol=str(opens.columns[column]),
            day=str(drift.days[row].date()),
            gap=float(gaps[row, column]),
            half_book_two=float(pead.ENTRY * book_two[row, column]),
            half_first_edition=float(pead.ENTRY * first[row, column]),
            day_return=float((cl[row, column] - op[row, column]) / op[row, column]),
            arithmetic_book_two=drift.arithmetic_annual,
            arithmetic_first_edition=float(pead.TRADING_DAYS * smartmean(daily_first)),
        )


def percent(value: float) -> str:
    """A fraction as a percentage to four decimals, the precision the post gives."""
    return f"{100 * value:.4f}"


def printed(value: float) -> str:
    """An annual return as ``pead.m``'s ``fprintf`` prints it, four decimals."""
    return f"{value:7.4f}".strip()


#: Where the number line runs, its height, and where the two ticks sit. The
#: green tick is at half book two's deviation and the red at half the first
#: edition's, and every value between maps to the board by one affine scale.
LINE_X = (0.4, 9.6)
LINE_Y = 2.2
LONG_X, NO_TRADE_X = 1.0, 9.0
#: Each tick's top. The red one reaches higher, so its label sits above the
#: black dot's.
LONG_TOP, NO_TRADE_TOP = 2.65, 3.1
TICK_FOOT = 1.75


def on_line(flip: HelperFlip, value: float) -> float:
    """The board position of a fraction on the number line, to one scale."""
    span = flip.half_first_edition - flip.half_book_two
    return LONG_X + (value - flip.half_book_two) / span * (NO_TRADE_X - LONG_X)


def _helper_flip(flip: HelperFlip) -> Scene:
    """Lesson 4: one gap that clears half one helper's deviation and misses the other's."""
    lost = flip.day_return < 0
    return Scene(
        "One position the helper flips",
        "helper_flip",
        (
            _stroke(
                "line", _line([(LINE_X[0], LINE_Y), (LINE_X[1], LINE_Y)]), color=MUTED, frames=8
            ),
            _stroke(
                "long-tick",
                _line([(LONG_X, TICK_FOOT), (LONG_X, LONG_TOP)], per_unit=10),
                color=GOOD,
                frames=4,
            ),
            Label(
                f"half the Algorithmic Trading helper’s deviation: {percent(flip.half_book_two)}%",
                LONG_X + 0.2,
                LONG_TOP + 0.3,
                names="long-tick",
                color=GOOD,
                size=12,
            ),
            Label(
                "long",
                LONG_X,
                TICK_FOOT - 0.35,
                names="long-tick",
                color=GOOD,
                size=12,
                ha="center",
            ),
            _stroke(
                "no-trade-tick",
                _line([(NO_TRADE_X, TICK_FOOT), (NO_TRADE_X, NO_TRADE_TOP)], per_unit=10),
                color=LOST,
                frames=4,
            ),
            Label(
                f"half the first edition’s deviation: {percent(flip.half_first_edition)}%",
                NO_TRADE_X + 0.3,
                NO_TRADE_TOP + 0.36,
                names="no-trade-tick",
                color=LOST,
                size=12,
                ha="right",
            ),
            Label(
                "no trade",
                NO_TRADE_X,
                TICK_FOOT - 0.35,
                names="no-trade-tick",
                color=LOST,
                size=12,
                ha="center",
            ),
            _dot("gap-dot", on_line(flip, flip.gap), LINE_Y, color=INK),
            Label(
                f"{flip.symbol}’s gap on {flip.day}: {percent(flip.gap)}%",
                on_line(flip, flip.gap) - 0.3,
                LINE_Y - 0.42,
                names="gap-dot",
                size=12,
                ha="right",
            ),
            Label(
                f"the long {'lost' if lost else 'made'} {100 * abs(flip.day_return):.2f}%: "
                f"annual return {printed(flip.arithmetic_book_two)} with it, "
                f"{printed(flip.arithmetic_first_edition)} without",
                5.0,
                0.6,
                names="gap-dot",
                size=12,
                ha="center",
            ),
        ),
    )


# --- Drawing ------------------------------------------------------------------

#: The scenes that build slowly, because each carries more than a reader takes
#: in at the usual pace: a label shows on its own for :data:`PACED_LABEL_MS`
#: and the finished drawing holds for :data:`PACED_HOLD_MS` before the loop.
#: Both match :mod:`chan.equity_seasonals_whiteboard`'s, which the tests check.
PACED = ("one_trade", "helper_flip")
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


def scenes(flip: HelperFlip | None = None) -> tuple[Scene, ...]:
    """The two scenes in the order the post reads them, the strategy's then Lesson 4's.

    ``flip`` defaults to :meth:`HelperFlip.from_run` on the committed files.
    """
    return (_one_trade(), _helper_flip(flip if flip is not None else HelperFlip.from_run()))


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


def make_pead_whiteboards(out_dir: Path | None = None) -> list[Path]:
    """Write one looping GIF for each scene and return their paths, in the post's order."""
    folder = out_dir if out_dir is not None else FIGURES_DIR
    return [_write(scene, folder) for scene in scenes()]


def main() -> None:
    for path in make_pead_whiteboards():
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
