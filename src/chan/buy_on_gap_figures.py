"""The figure for the post on buy on gap, *Algorithmic Trading*'s Example 4.1.

``blog/buy-on-gap-lessons.md`` teaches what Entry 18 of the replication log
found, and [issue 309](https://github.com/l3a0/quantitative-trading/issues/309)
chose one figure for it. :func:`make_cumulative_figure` draws two panels that
share both axes.

1. The top panel redraws what ``bog.m``'s closing ``plot(cumret)`` draws,
   which the book prints as Figure 4.1 at location 1974: the compounded
   cumulative return over the file's 1,500 days, at one tenth of capital a
   position, unlevered and before costs.
2. The bottom panel draws the same series for the short-on-gap mirror, where
   the book prints Figure 4.2 at location 1993. Chan published no script for
   it, so this is the rule
   [issue 295](https://github.com/l3a0/quantitative-trading/issues/295)
   declared before any run, not his.

On shared axes, the mirror's steeper drawdown, which reproduces, and its
return, which does not, read on one scale. The figure
serves the post's first lesson, that both printed figures reproduce, and its
fourth, on the mirror.

Two stretches are shaded on each panel.

1. The first 90 rows, which hold no position because the 90-row moving
   spread does not exist until 2006-09-19.
2. The longest spell below the high, which ``calculateMaxDD`` measures
   without saying where it falls. :func:`chan.pead_figures.longest_spell`
   finds it under the same rules, and on both sides the deepest drawdown
   happens to sit inside it. Nothing in ``calculateMaxDD`` makes that so,
   which is why ``tests/test_buy_on_gap_figures.py`` holds it.

Every value comes from :func:`chan.buy_on_gap.both_sides`, the run's own read
of the committed file. The run calls no scale-break guard, by
[issue 295](https://github.com/l3a0/quantitative-trading/issues/295)'s
decision, so the figure has no guard to skip::

    uv run python -m chan.buy_on_gap_figures
"""

from __future__ import annotations

from pathlib import Path

from matplotlib.dates import DateFormatter, YearLocator
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter

from chan.buy_on_gap import (
    BOOK_APR_PERCENT,
    BOOK_SHARPE,
    MIRROR_BOOK_APR_PERCENT,
    MIRROR_BOOK_SHARPE,
    PRICE_FILE,
    SCRIPT_PRICE_FILE,
    SPREAD_LOOKBACK,
    TOP_N,
    Side,
    both_sides,
)
from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.paths import FIGURES_DIR
from chan.pead_figures import _signed, cumulative_return, longest_spell
from chan.regime_figure import INK, LOST, MUTED, RULE, SURFACE
from chan.vintage import VintageUnavailable

CUMULATIVE_FIGURE = "buy_on_gap_cumulative_returns.png"


def panel_heading(side: Side, *, mirror: bool) -> str:
    """What a panel draws, its two figures, and what the book prints beside them."""
    if mirror:
        lead = "Where Figure 4.2 stands: short on gap, the mirror as declared here"
        book = f"{MIRROR_BOOK_APR_PERCENT} percent and {MIRROR_BOOK_SHARPE}"
    else:
        lead = "Figure 4.1: buy on gap, as bog.m runs it"
        book = f"{BOOK_APR_PERCENT} percent and {BOOK_SHARPE}"
    return (
        f"{lead}.\nAPR {side.apr:.6f} and Sharpe ratio {side.sharpe:.4f}, "
        f"where the book prints {book}."
    )


def _panel(ax, side: Side, *, mirror: bool) -> None:
    days = side.days
    cumret = cumulative_return(side)
    spell = longest_spell(cumret)
    _style(ax)

    ax.axvspan(days[0], days[SPREAD_LOOKBACK - 1], color=RULE, alpha=0.45, lw=0, gid="unfilled")
    ax.axvspan(days[spell.first], days[spell.last], color=LOST, alpha=0.12, lw=0, gid="spell")
    ax.axhline(0, color=MUTED, lw=0.9)
    ax.plot(days, cumret, color=INK, lw=1.6, gid="cumulative")

    # The spell's label sits at the top of its band rather than on the line,
    # because the line climbs past the high within days of the spell ending.
    ax.text(
        days[(spell.first + spell.last) // 2],
        0.95,
        f"{spell.rows} days below the high,\n{days[spell.first].date()} to "
        f"{days[spell.last].date()}",
        transform=ax.get_xaxis_transform(),
        ha="center",
        va="top",
        color=LOST,
        fontsize=9.5,
        fontweight="bold",
        gid="spell-label",
    )
    for gid, row, colour in (("high", spell.high, INK), ("trough", spell.trough, LOST)):
        ax.plot(
            [days[row]],
            [cumret[row]],
            "o",
            ms=6,
            color=colour,
            mec=SURFACE,
            mew=1.6,
            zorder=3,
            gid=gid,
        )
    ax.annotate(
        f"high, {days[spell.high].date()}",
        (days[spell.high], cumret[spell.high]),
        xytext=(-8, 6),
        textcoords="offset points",
        ha="right",
        color=INK,
        fontsize=9.5,
        gid="high-label",
    )
    ax.annotate(
        f"deepest drawdown {_signed(spell.depth)},\n{days[spell.trough].date()}",
        (days[spell.trough], cumret[spell.trough]),
        xytext=(-4, -34),
        textcoords="offset points",
        ha="left",
        color=LOST,
        fontsize=9.5,
        fontweight="bold",
        gid="trough-label",
    )
    ax.set_title(
        panel_heading(side, mirror=mirror), loc="left", color=INK, fontsize=10.5, linespacing=1.4
    )
    ax.cumret = cumret
    ax.spell = spell


@_plain_text
def make_cumulative_figure(
    out: Path | None = None, sides: tuple[Side, Side] | None = None
) -> Figure:
    """Both sides' compounded cumulative return, the idle start and each longest spell shaded."""
    long, short = sides if sides is not None else both_sides()[1:]

    fig = Figure(figsize=(10, 8.8), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    top, bottom = fig.subplots(2, 1, sharex=True, sharey=True)
    _panel(top, long, mirror=False)
    _panel(bottom, short, mirror=True)

    # The idle label sits at the top left, where the line has not yet climbed,
    # because below the zero line it would run off the axes.
    top.text(
        long.days[SPREAD_LOOKBACK - 1],
        0.95,
        f" no position in the first {SPREAD_LOOKBACK} days,\n before the "
        f"{SPREAD_LOOKBACK}-day\n standard deviation exists",
        transform=top.get_xaxis_transform(),
        ha="left",
        va="top",
        color=MUTED,
        fontsize=9.5,
        gid="unfilled-label",
    )

    days = long.days
    low = min(top.cumret.min(), bottom.cumret.min())
    high = max(top.cumret.max(), bottom.cumret.max())
    span = high - low
    bottom.set_xlim(days[0], days[-1])
    bottom.set_ylim(low - 0.18 * span, high + 0.16 * span)
    bottom.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    bottom.xaxis.set_major_locator(YearLocator())
    bottom.xaxis.set_major_formatter(DateFormatter("%Y"))
    for ax in (top, bottom):
        ax.set_ylabel("cumulative return, compounded", color=INK, fontsize=10)
    _title(
        fig,
        "Exploratory: buy on gap redrawn on Chan's own file, the declared mirror below",
        f"Example 4.1 of Algorithmic Trading, {days[0].date()} to {days[-1].date()}, each day's "
        f"summed return over {TOP_N}, unlevered and before costs.\n"
        f"Prices from {PRICE_FILE}, the file bog.m loads as {SCRIPT_PRICE_FILE}.\n"
        "The file holds the S&P 500 as Chan held it on 2012-04-24, "
        "so every stock is a survivor.",
    )
    fig.tight_layout(rect=(0, 0.08, 1, 0.97))
    return _save(fig, out, CUMULATIVE_FIGURE)


def main() -> None:
    try:
        make_cumulative_figure()
    except VintageUnavailable as refused:
        # A refusal that names the source is worth nothing at the bottom of a
        # traceback, so it reaches the operator as one line, the way
        # chan.buy_on_gap.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / CUMULATIVE_FIGURE}")


if __name__ == "__main__":
    main()
