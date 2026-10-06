"""The figure for the post on GLD, GDX and USO around July 2008, location 1922.

``blog/gold-miners-oil-lessons.md`` teaches what Entry 29 of the replication
log found. :func:`make_break_figure` draws two panels that share the date axis
over the 1,481 days all three ETFs are priced, with the day Chan splits at
marked on both.

1. The three closes in dollars, because the split is the day USO closes
   highest on the file, and that is the fact Chan's oil story starts from.
2. GLD and GDX held in the weights the first window's Johansen test finds,
   in standard deviations from that portfolio's first-window mean. The
   weights are fitted on the first window only, so everything right of the
   split shows those weights on days they never saw. The second window's own
   test fits fresh weights and still finds no relation, which this panel
   cannot show and the post says.

Every value comes from :func:`chan.gold_miners_oil.read_sources` and
:func:`chan.gold_miners_oil.gold_miners_oil`, the run's own path, so the
scale-break guard runs here too::

    uv run python -m chan.gold_miners_oil_figures
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from matplotlib.dates import DateFormatter, YearLocator
from matplotlib.figure import Figure

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.gold_miners_oil import (
    AFTER,
    BEFORE,
    GDX,
    GLD,
    PAIR,
    SOURCE_FILE,
    TRIPLET,
    USO,
    GoldMinersOil,
    gold_miners_oil,
    read_sources,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED, SURFACE
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable

BREAK_FIGURE = "gold_miners_oil_break.png"

#: Each close's line on the top panel: its colour.
COLOURS = {GLD: GOOD, GDX: ACCENT, USO: LOST}


@dataclass(frozen=True)
class FirstWindowPortfolio:
    """GLD and GDX held in the first window's Johansen weights, over every day.

    ``weights`` are shares of GLD and GDX, the first column of the first
    window's eigenvectors with statsmodels' sign. ``z`` is the portfolio's
    value in standard deviations from its first-window mean, the deviation
    taken with ``n − 1``, pandas' default.
    """

    weights: tuple[float, float]
    value: pd.Series
    z: pd.Series


def first_window_portfolio(closes: pd.DataFrame, result: GoldMinersOil) -> FirstWindowPortfolio:
    """The first window's Johansen weights on GLD and GDX, carried across the split."""
    weights = result.before.eigenvectors[:, 0]
    value = closes[list(PAIR)] @ weights
    first = value.loc[BEFORE[0] : BEFORE[1]]
    return FirstWindowPortfolio(
        weights=(float(weights[0]), float(weights[1])),
        value=value,
        z=(value - first.mean()) / first.std(),
    )


def signed(value: float, places: int = 2) -> str:
    """``value`` to ``places`` decimals with a true minus sign, as the post prints it."""
    return f"{value:.{places}f}".replace("-", "\u2212")


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


@_plain_text
def make_break_figure(out: Path | None = None, closes: pd.DataFrame | None = None) -> Figure:
    """The three closes and the first window's GLD and GDX portfolio, split marked."""
    if closes is None:
        closes = read_sources()[1]
    result = gold_miners_oil(closes)
    portfolio = first_window_portfolio(closes, result)
    days = closes.index
    split = pd.Timestamp(BEFORE[1])
    peak = closes[USO].idxmax()
    before, after = portfolio.z.loc[: BEFORE[1]], portfolio.z.loc[AFTER[0] :]

    fig = Figure(figsize=(10, 9), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    price_ax, z_ax = fig.subplots(2, 1, sharex=True, gridspec_kw={"height_ratios": (1, 1)})
    for ax in (price_ax, z_ax):
        _style(ax)
        ax.axvline(split, color=MUTED, lw=1.0, ls="--", gid="split")

    for symbol in TRIPLET:
        price_ax.plot(days, closes[symbol], color=COLOURS[symbol], lw=1.2, gid=symbol, label=symbol)
    price_ax.plot([peak], [closes[USO].max()], "o", color=LOST, ms=5, gid="peak")
    price_ax.set_ylabel("close, dollars", color=INK, fontsize=10)
    price_ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK)
    _heading(
        price_ax,
        f"The three closes on Chan's file. USO's highest, {closes[USO].max():.2f}, "
        f"is on {peak.date()},\nthe last day of Chan's first window, marked dashed.",
    )

    z_ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    z_ax.plot(before.index, before, color=GOOD, lw=1.1, gid="before")
    z_ax.plot(after.index, after, color=LOST, lw=1.1, gid="after")
    z_ax.set_ylabel("deviations from first-window mean", color=INK, fontsize=10)
    w_gld, w_gdx = (signed(w, 3) for w in portfolio.weights)
    _heading(
        z_ax,
        f"GLD and GDX in the first window's Johansen weights, {w_gld} and {w_gdx} shares.\n"
        f"From {signed(before.min())} to {signed(before.max())} in the {len(before)} days "
        f"before the split. From {signed(after.min())} to {signed(after.max())} in the "
        f"{len(after)} after it,\nwhere it never comes back to the first window's mean.",
    )
    z_ax.set_xlim(days[0], days[-1])
    z_ax.xaxis.set_major_locator(YearLocator())
    z_ax.xaxis.set_major_formatter(DateFormatter("%Y"))

    _title(
        fig,
        "Exploratory: GLD and GDX either side of July 14, 2008, on Chan's own closes",
        f"Algorithmic Trading, location 1922, {days[0].date()} to {days[-1].date()}, the "
        f"{len(days):,} days GDX is priced.\nPrices from {SOURCE_FILE}, saved 2012-04-10. "
        "The split date was chosen after the break was seen,\nso a test that splits there "
        "is favoured by construction.",
    )
    fig.tight_layout(rect=(0, 0.08, 1, 0.97))
    return _save(fig, out, BREAK_FIGURE)


def main() -> None:
    try:
        make_break_figure()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source is worth nothing at the bottom of a
        # traceback, so it reaches the operator as one line, the way
        # chan.gold_miners_oil.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / BREAK_FIGURE}")


if __name__ == "__main__":
    main()
