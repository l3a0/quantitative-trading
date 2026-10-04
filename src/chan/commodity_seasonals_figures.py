"""The commodity-seasonals post's one figure, drawn from the committed EIA files.

``blog/commodity-seasonals-lessons.md`` teaches in its Lesson 2 that a missing
row is not a losing year, and in its Lesson 3 that a trade chosen after looking
at the history is tested by the years after the book. Both lessons are about
single years, so the figure draws every year of both trades rather than the
counts. Issue 283 named it and planned its shape.

:func:`make_years_figure` draws two panels, gasoline from 1995 and natural gas
from 1994, both to 2023, the last year whose exit the files hold.

1. **One bar per year at the settlement change**, ``Trade.change``, in the
   file's own units, dollars a gallon for gasoline and dollars per million Btu
   for natural gas. A bar above zero is a profitable year under the rule issue
   19 pinned, one contract and no costs.
2. **An empty slot labelled "no row"** for each year whose trade date has no
   row in its file, never a bar of zero, because a missing year counts neither
   way. Only gasoline has them, in 1997, 1998 and 1999.
3. **A dashed divider where the book's years end**: after 2008 for natural gas,
   under the reading pinned on issue 19 that both of Chan's counts were written
   for the first edition, and after 2015 for gasoline, the year the revised
   edition's count runs to. Each side is labelled with its count.

Every bar takes one ink whatever its sign, and nothing is drawn in the verdict
colours, because the figure grades nothing. The title says the record is
exploratory, for the reason ``chan.commodity_seasonals`` gives: Chan chose both
trades after looking at the history the files hold.

Every value comes from :mod:`chan.commodity_seasonals`, so the figure can only
be wrong by drawing the wrong thing, which
``tests/test_commodity_seasonals_figures.py`` checks. It reads the committed
vintages, so it redraws anywhere the data is::

    uv run python -m chan.commodity_seasonals_figures
"""

from __future__ import annotations

from pathlib import Path

from matplotlib.figure import Figure

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.commodity_seasonals import (
    GASOLINE_YEARS,
    NG_YEARS,
    Trade,
    gasoline_trades,
    natural_gas_trades,
    profitable_count,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, INK, MUTED, SURFACE
from chan.vintage import VintageUnavailable

YEARS_FIGURE = "commodity_seasonals_years.png"

#: The last year of the book's record for each trade. Natural gas ends in 2008
#: under the reading issue 19 pinned, gasoline in 2015, where the revised
#: edition's 19 of 21 stops.
GASOLINE_BOOK_END = 2015
NG_BOOK_END = 2008

Trades = tuple[list[Trade], list[Trade]]

#: The day all five files the trades read were downloaded, which
#: ``tests/test_commodity_seasonals_figures.py`` holds to each one's manifest
#: line, so the note cannot name a date the vintages do not carry.
DOWNLOADED = "2026-10-02"


def year_trades() -> Trades:
    """Both trades over every year the files serve, gasoline first."""
    return gasoline_trades(*GASOLINE_YEARS), natural_gas_trades(*NG_YEARS)


def symbols_read(*trades: list[Trade]) -> str:
    """Every EIA symbol the trades read, in the order they first read it."""
    seen: dict[str, None] = {}
    for trade in (trade for group in trades for trade in group):
        seen.setdefault(trade.entry_symbol)
        seen.setdefault(trade.exit_symbol)
    return ", ".join(seen)


def side_label(trades: list[Trade]) -> str:
    """One side of a divider: its years, its profitable count, and any unreadable years."""
    first, last = trades[0].year, trades[-1].year
    missing = sum(1 for trade in trades if trade.profitable is None)
    label = f"{first} to {last}\n{profitable_count(trades)} of {len(trades)} profitable"
    return label + (f"\n{missing} with no row" if missing else "")


def _panel(ax, trades: list[Trade], book_end: int, name: str, units: str) -> None:
    _style(ax)
    ax.axhline(0, color=MUTED, lw=0.9, zorder=1, gid=f"{name}-zero")
    readable = [trade for trade in trades if trade.change is not None]
    bars = ax.bar(
        [trade.year for trade in readable],
        [float(trade.change) for trade in readable],
        width=0.72,
        color=ACCENT,
        zorder=3,
    )
    for bar, trade in zip(bars, readable, strict=True):
        bar.set_gid(f"{name}-bar-{trade.year}")
    # Natural gas's 2022 is near three dollars and its 2014 under a cent, so a
    # bar alone hides the sign of the small years. One mark per readable year
    # along the panel's foot says it whatever the size, pointing up for a
    # profit and down for a loss.
    for direction, marker in ((True, "^"), (False, "v")):
        years = [trade.year for trade in readable if trade.profitable is direction]
        ax.plot(
            years,
            [0.035] * len(years),
            ls="none",
            marker=marker,
            markersize=4.5,
            color=INK,
            transform=ax.get_xaxis_transform(),
            zorder=4,
            gid=f"{name}-{'profit' if direction else 'loss'}-marks",
        )
    for trade in trades:
        if trade.change is None:
            ax.annotate(
                "no row",
                (trade.year, 0),
                xytext=(0, 4),
                textcoords="offset points",
                rotation=90,
                ha="center",
                va="bottom",
                color=MUTED,
                fontsize=8.5,
                gid=f"{name}-missing-{trade.year}",
            )
    ax.axvline(book_end + 0.5, color=MUTED, lw=1.1, ls="--", zorder=2, gid=f"{name}-divider")
    before = [trade for trade in trades if trade.year <= book_end]
    after = [trade for trade in trades if trade.year > book_end]
    for text, x, ha, gid in (
        (side_label(before), -8, "right", f"{name}-label-before"),
        (side_label(after), 8, "left", f"{name}-label-after"),
    ):
        ax.annotate(
            text,
            (book_end + 0.5, 1.0),
            xycoords=("data", "axes fraction"),
            xytext=(x, -6),
            textcoords="offset points",
            ha=ha,
            va="top",
            color=INK,
            fontsize=9.5,
            linespacing=1.35,
            gid=gid,
        )
    low = min(0.0, *(float(trade.change) for trade in readable))
    high = max(0.0, *(float(trade.change) for trade in readable))
    pad = (high - low) * 0.08
    ax.set_ylim(low - 2 * pad, high + 6 * pad)
    ax.set_ylabel(units, color=INK, fontsize=10)


@_plain_text
def make_years_figure(trades: Trades | None = None, out: Path | None = None) -> Figure:
    """Every year of both trades as a bar, with the book's years divided from the rest."""
    gasoline, gas = trades if trades is not None else year_trades()

    fig = Figure(figsize=(10, 8.2), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    top, bottom = fig.subplots(2, 1, sharex=True)
    _panel(top, gasoline, GASOLINE_BOOK_END, "gasoline", "settlement change,\ndollars a gallon")
    _panel(bottom, gas, NG_BOOK_END, "gas", "settlement change,\ndollars per million Btu")
    top.set_title(
        "Gasoline: the May contract, close of April 13 to close of April 25",
        loc="left",
        color=INK,
        fontsize=11,
    )
    bottom.set_title(
        "Natural gas: the June contract, close of February 25 to close of April 15",
        loc="left",
        color=INK,
        fontsize=11,
    )
    first = min(gasoline[0].year, gas[0].year)
    last = max(gasoline[-1].year, gas[-1].year)
    bottom.set_xlim(first - 0.7, last + 0.7)
    bottom.set_xlabel("year of the trade", color=INK, fontsize=10)

    _title(
        fig,
        "Chan's two commodity seasonals, year by year, an exploratory record with no verdict",
        f"EIA's NYMEX settlements, downloaded {DOWNLOADED}: {symbols_read(gasoline, gas)}.\n"
        "One contract a year with no costs, so a bar above zero is a profitable year, and the "
        "marks along each foot\npoint up for a profit and down for a loss. Chan chose both "
        "trades after looking at this history.\nThe dashed line is where "
        "the book's years end: 2015 for gasoline, and 2008 for natural gas under\n"
        "the reading that both of its counts were written for the first edition.",
    )
    fig.tight_layout(rect=(0, 0.125, 1, 0.96))
    return _save(fig, out, YEARS_FIGURE)


def main() -> None:
    try:
        trades = year_trades()
    except VintageUnavailable as refusal:
        # The refusal `chan.commodity_seasonals.main` would end in, as one line:
        # a sentence naming the missing vintage is worth nothing at the bottom
        # of a traceback.
        raise SystemExit(str(refusal)) from refusal
    make_years_figure(trades)
    print(f"wrote {FIGURES_DIR / YEARS_FIGURE}")


if __name__ == "__main__":
    main()
