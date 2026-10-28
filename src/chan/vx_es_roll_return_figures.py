"""The figure for ``blog/vx-es-roll-return-lessons.md``, *Algorithmic Trading* at location 2754.

That post is on VX against ES on VX's roll return, after Simon and Campasano.
:mod:`chan.vx_es_roll_return` prints Entry 41's figures and draws nothing, so
this module draws what the run does not. The name ``vx_es_figures`` belongs to
Entry 28's figure, so this one carries the trade's own name. Two panels share
one date axis over the 448 test days, 2010-07-29 to 2012-05-07.

1. **Figure 6.4 redrawn.** ``cumprod(1 + r) − 1`` under both of the script's
   position rules. The book's rule, 0.3906 VX contracts per ES contract, is in
   ink, and the script's live lines, one VX contract per ES contract, are
   muted. The script's plot line draws whichever rule is live, while the
   book's text quotes 0.3906's figures, and nothing committed shows which
   curve the printed figure carries. Drawing both lets a reader holding the
   book match its figure to one of them. The deepest drawdown under 0.3906 is
   marked at its high and its trough, and so is its longest run below a high.
2. **The signal.** :func:`chan.vx_es_roll_return.front_roll`, the front
   contract's distance above VIX over the trading days to settlement, with
   dashed lines at the two thresholds. The book prints only the curve, while
   the post's lessons turn on what the rule reads each day. The last 10 days
   carry no front, so the line stops there.

Both panels shade the days the rule holds short in one tint and the days it
holds long in another. The two rules hold the same days with the same signs,
so one set of shading serves both curves.

Every value comes from :func:`chan.vx_es_roll_return.read_sources`,
:func:`~chan.vx_es_roll_return.roll_return_trade` and
:func:`~chan.vx_es_roll_return.front_roll`, the run's own path, so the
scale-break guard runs here too. Loading ES checks every member of its save
against its checksum, VX's continuous close among them, so a changed or
missing copy of that file refuses the figure as it refuses the run. The figure
never computes the fitted hedge, the only computation that uses VX's continuous
close as data::

    uv run python -m chan.vx_es_roll_return_figures
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter, MonthLocator, date2num
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.matlab_helpers import drawdown_path
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, GROUND, INK, MUTED, SURFACE
from chan.roll_momentum_figures import flat_spans
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable
from chan.vx_es_roll_return import (
    BOOK_APR_PERCENT,
    BOOK_SHARPE,
    ENTRY_THRESHOLD,
    HEDGE,
    SHIPPED_HEDGE,
    RollReturnTrade,
    Sources,
    front_roll,
    read_sources,
    roll_return_trade,
)
from chan.xle_uso_roll_return import FRONT_END, FRONT_START

FIGURE = "vx_es_roll_return.png"
#: The shading for the days held short both legs, in both panels.
SHORT_SHADE = (ACCENT, 0.16)
#: The shading for the days held long both legs, in both panels.
LONG_SHADE = (GOOD, 0.22)
#: The first panel's vertical range, with room for the legend above both curves.
CURVE_LIMITS = (-0.1, 0.75)
#: The second panel's vertical range, with room for the high's label above the signal.
ROLL_LIMITS = (-0.65, 0.42)
#: The ground behind every label, so a gridline or a shaded day never runs through its text.
LABEL_BOX = {"facecolor": GROUND, "edgecolor": "none", "pad": 1.5}
#: The thin line from a label set away from its marker back to the marker.
LEADER = {
    "arrowstyle": "-",
    "color": ACCENT,
    "lw": 0.8,
    "relpos": (0.02, 1.0),
    "shrinkA": 0,
    "shrinkB": 3,
}


def cumulative_return(daily: np.ndarray) -> np.ndarray:
    """``cumprod(1 + r) − 1``, the series line 74 computes and Figure 6.4 draws."""
    return np.cumprod(1 + np.asarray(daily, dtype=float)) - 1


def held_runs(
    days: pd.DatetimeIndex, held: np.ndarray
) -> list[tuple[pd.Timestamp, pd.Timestamp, int]]:
    """Each run of consecutive ``held`` rows as its first day, its last day and its length.

    The figure shades with :func:`chan.roll_momentum_figures.flat_spans` and
    never calls this. The tests call it to name the stretches the post
    quotes, and hold it equal to the spans read off the drawn patches.
    """
    edges = np.flatnonzero(np.diff(np.concatenate([[0], held.astype(int), [0]])))
    return [
        (days[start], days[end - 1], int(end - start))
        for start, end in zip(edges[::2], edges[1::2], strict=True)
    ]


def signed(value: float, places: int = 2) -> str:
    """``value`` to ``places`` decimals with a true minus sign, as the post prints it."""
    return f"{value:.{places}f}".replace("-", "−")


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


def _shade(ax, trade: RollReturnTrade) -> None:
    """The days held short and the days held long, the same in both panels."""
    days = trade.test_days
    leg = trade.es_leg[trade.test]
    for held, (color, alpha), gid, label in (
        (leg < 0, SHORT_SHADE, "short", "held short VX and short ES"),
        (leg > 0, LONG_SHADE, "long", "held long VX and long ES"),
    ):
        for k, (left, right) in enumerate(flat_spans(days, held)):
            ax.axvspan(
                left,
                right,
                color=color,
                alpha=alpha,
                lw=0,
                gid=gid,
                label=label if k == 0 else None,
            )


def _curve_panel(ax, hedged: RollReturnTrade, shipped: RollReturnTrade) -> None:
    days = hedged.test_days
    book = cumulative_return(hedged.test_daily)
    live = cumulative_return(shipped.test_daily)
    _shade(ax, hedged)
    ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    ax.plot(
        days,
        live,
        color=MUTED,
        lw=1.2,
        ls="--",
        gid="shipped",
        label=(
            f"{SHIPPED_HEDGE:g} VX contract per ES contract, the script's live lines, "
            f"ending at {signed(100 * live[-1])} percent"
        ),
    )
    ax.plot(
        days,
        book,
        color=INK,
        lw=1.7,
        zorder=3,
        gid="hedged",
        label=(
            f"{HEDGE} VX contracts per ES contract, the book's rule, "
            f"ending at {signed(100 * book[-1])} percent"
        ),
    )

    highs, drawdown, duration = drawdown_path(book)
    trough = int(np.argmin(drawdown))
    high = int(np.argmax(book[: trough + 1]))
    # The live lines' curve runs just above the high, so its label sits below
    # the zero line, where no curve runs, with a line back to the marker.
    for row, gid, text, offset, leader in (
        (high, "drawdown-high", "high", (0, -34), LEADER),
        (trough, "drawdown-trough", "trough", (8, -12), None),
    ):
        ax.plot([days[row]], [book[row]], "o", color=ACCENT, ms=5, zorder=4, gid=gid)
        ax.annotate(
            f"{text}, {signed(book[row], 6)} on {days[row].date()}",
            (days[row], book[row]),
            xytext=offset,
            textcoords="offset points",
            ha="right" if offset[0] < 0 else "left",
            color=ACCENT,
            fontsize=9,
            gid=f"{gid}-label",
            bbox=LABEL_BOX,
            arrowprops=leader,
        )
    last = int(np.argmax(duration))
    first = last - int(duration[last]) + 1
    ax.plot(
        [days[first], days[last]],
        [highs[last]] * 2,
        color=ACCENT,
        lw=1.0,
        ls=":",
        gid="longest-drawdown",
    )
    ax.annotate(
        f"{duration[last]} days below this high, to {days[last].date()}",
        (days[first] + (days[last] - days[first]) / 2, highs[last]),
        xytext=(0, 19),
        textcoords="offset points",
        ha="center",
        color=ACCENT,
        fontsize=9,
        gid="longest-drawdown-label",
        bbox=LABEL_BOX,
    )

    ax.set_ylim(*CURVE_LIMITS)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.set_ylabel("cumulative return, compounded", color=INK, fontsize=10)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK)
    _heading(
        ax,
        f"Figure 6.4: cumulative return over the test, {days[0].date()} to {days[-1].date()}."
        f"\nUnder {HEDGE}, APR {hedged.apr:.6f} and Sharpe ratio {hedged.sharpe:.6f}, where the "
        f"book prints {BOOK_APR_PERCENT} percent and {BOOK_SHARPE}.\nThe deepest drawdown is "
        f"{signed(hedged.max_drawdown, 6)}.",
    )


def _roll_panel(ax, hedged: RollReturnTrade, roll: pd.Series) -> None:
    days = hedged.test_days
    _shade(ax, hedged)
    ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    for level, gid in ((ENTRY_THRESHOLD, "short-line"), (-ENTRY_THRESHOLD, "long-line")):
        ax.axhline(level, color=MUTED, lw=1.0, ls="--", gid=gid)
    ax.plot(days, roll.to_numpy(), color=INK, lw=1.0, gid="roll")
    # The signal's December 2011 spike nearly reaches the high, so the high's
    # label sits above the marker rather than level with it.
    for day, gid, text, offset in (
        (roll.idxmin(), "roll-low", "low", (8, -4)),
        (roll.idxmax(), "roll-high", "high", (-6, 7)),
    ):
        ax.plot([day], [roll.loc[day]], "o", color=ACCENT, ms=5, zorder=4, gid=gid)
        ax.annotate(
            f"{text}, {signed(roll.loc[day], 6)} on {day.date()}",
            (day, roll.loc[day]),
            xytext=offset,
            textcoords="offset points",
            ha="right" if offset[0] < 0 else "left",
            color=ACCENT,
            fontsize=9,
            gid=f"{gid}-label",
            bbox=LABEL_BOX,
        )
    ax.set_ylim(*ROLL_LIMITS)
    ax.set_ylabel("VIX points a day to settlement", color=INK, fontsize=10)
    _heading(
        ax,
        "The signal: the front VX contract less VIX, over the trading days to settlement, each "
        f"contract the front\nfrom {FRONT_START} to {FRONT_END} rows before its last price. Above "
        f"{ENTRY_THRESHOLD} the rule is short both legs, below {signed(-ENTRY_THRESHOLD, 1)} long "
        "both.\nThe last 10 days have no front, and the rule holds nothing on them.",
    )


@_plain_text
def make_vx_es_roll_return_figure(
    out: Path | None = None, sources: Sources | None = None
) -> Figure:
    """Figure 6.4 under both rules, and the roll that signs them."""
    sources = sources if sources is not None else read_sources()
    hedged = roll_return_trade(sources, HEDGE)
    shipped = roll_return_trade(sources, SHIPPED_HEDGE)
    contracts = sources.strip.contracts.loc[hedged.days]
    roll = front_roll(contracts, sources.vix.loc[hedged.days]).iloc[hedged.test]

    fig = Figure(figsize=(10, 10.5), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    curve_ax, roll_ax = fig.subplots(
        2, 1, sharex=True, gridspec_kw={"hspace": 0.3, "height_ratios": (1.4, 1)}
    )
    for ax in (curve_ax, roll_ax):
        _style(ax)
    _curve_panel(curve_ax, hedged, shipped)
    _roll_panel(roll_ax, hedged, roll)
    days = hedged.test_days
    curve_ax.set_xlim(date2num(days[0]), date2num(days[-1]))
    roll_ax.xaxis.set_major_locator(MonthLocator(bymonth=(1, 4, 7, 10)))
    roll_ax.xaxis.set_major_formatter(DateFormatter("%Y-%m"))

    strip_saved = sorted({m.obtained for m in sources.strip.members})
    _title(
        fig,
        "Exploratory: VX against ES on VX's roll return",
        "Algorithmic Trading, Kindle edition, pp. 211 to 213. VX contracts from "
        "inputDataDaily_VX_20120507.mat, "
        f"saved {', '.join(strip_saved)}.\nVIX from VIX.csv, saved {sources.vix_member.obtained}. "
        f"ES from inputDataOHLCDaily_20120507.mat, saved {sources.es_member.obtained}.\nOne "
        "basis point of each day's change in market value is charged, and nothing on an entry "
        "from flat.",
    )
    fig.subplots_adjust(left=0.1, right=0.97, top=0.88, bottom=0.1)
    return _save(fig, out, FIGURE)


def main() -> None:
    try:
        make_vx_es_roll_return_figure()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day reaches the reader
        # as one line, the way chan.vx_es_roll_return.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / FIGURE}")


if __name__ == "__main__":
    main()
