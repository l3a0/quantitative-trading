"""The figure for the post on SPY against its component stocks, Example 4.2.

``blog/index-arbitrage-lessons.md`` teaches what Entry 24 of the replication
log found. :func:`make_index_arbitrage_figure` draws two panels.

1. The book's Figure 4.3, the compounded cumulative return over the 1,076
   test days. ``indexArb.m`` plots it against the row number, and this panel
   plots it against the date.
2. The share of series the screen passes over 2007, for the stocks in Chan's
   file and for random walks unrelated to SPY, with the 90 percent bar's
   nominal 10 percent drawn as a line. The walks are
   :func:`chan.index_arbitrage.walks_unrelated_to` with the seed
   ``tests/test_index_arbitrage.py`` pins, so the panel and that pin read the
   same walks.

Every value comes from :func:`chan.index_arbitrage.read_sources` and
:func:`chan.index_arbitrage.index_arbitrage`, the run's own path, so the
scale-break guard on SPY runs here too::

    uv run python -m chan.index_arbitrage_figures
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter, YearLocator
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.index_arbitrage import (
    BOOK_APR_PERCENT,
    BOOK_SHARPE,
    ETF_FILE,
    SCREEN_LEVEL,
    STOCK_FILE,
    IndexArbitrage,
    index_arbitrage,
    read_sources,
    screen,
    walks_unrelated_to,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, GROUND, INK, MUTED, SURFACE
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable

FIGURE = "index_arbitrage.png"

#: The random walks ``tests/test_index_arbitrage.py`` screens, and their seed.
WALKS = 2000
WALK_SEED = 343


@dataclass(frozen=True)
class ScreenRates:
    """How many of each kind of series the screen tested over 2007, and passed."""

    stocks_tested: int
    stocks_passed: int
    walks_tested: int
    walks_passed: int


def screen_rates(index: pd.Series, result: IndexArbitrage) -> ScreenRates:
    """The run's own screen beside the same screen on random walks unrelated to SPY."""
    spy = index.loc[result.train_days]
    walks = screen(walks_unrelated_to(spy, WALKS, WALK_SEED), spy)
    return ScreenRates(
        stocks_tested=len(result.screen.tested),
        stocks_passed=len(result.screen.passed),
        walks_tested=len(walks.tested),
        walks_passed=len(walks.passed),
    )


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


@_plain_text
def make_index_arbitrage_figure(
    out: Path | None = None,
    sources: tuple | None = None,
    rates: ScreenRates | None = None,
) -> Figure:
    """Figure 4.3 against the date, and the screen's pass rate beside chance's."""
    if sources is None:
        sources = read_sources()
    stock_members, spy_member, stocks, index = sources
    result = index_arbitrage(stocks, index)
    if rates is None:
        rates = screen_rates(index, result)
    days = result.test_days
    cumulative = np.cumprod(1 + result.daily) - 1
    first = days[int(np.flatnonzero(result.daily)[0])]

    fig = Figure(figsize=(10, 9), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    curve_ax, rate_ax = fig.subplots(2, 1, gridspec_kw={"height_ratios": (1.5, 1)})
    for ax in (curve_ax, rate_ax):
        _style(ax)

    curve_ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    curve_ax.plot(days, cumulative, color=GOOD, lw=1.4, gid="cumulative")
    curve_ax.set_xlim(days[0], days[-1])
    curve_ax.xaxis.set_major_locator(YearLocator())
    curve_ax.xaxis.set_major_formatter(DateFormatter("%Y"))
    curve_ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    curve_ax.set_ylabel("cumulative return", color=INK, fontsize=10)
    _heading(
        curve_ax,
        f"Figure 4.3 against the date: the compounded cumulative return over the "
        f"{len(days):,} test days.\nAPR {result.apr:.6f} and Sharpe ratio {result.sharpe:.6f}, "
        f"which the book prints as {BOOK_APR_PERCENT} percent and {BOOK_SHARPE}.\n"
        f"Zero until the first return on {first.date()}, and {cumulative[-1]:.6f} on the "
        f"last day, unlevered and before costs.",
    )

    labels = (
        f"{rates.stocks_passed} of {rates.stocks_tested} stocks in Chan's file",
        f"{rates.walks_passed} of {rates.walks_tested:,} random walks unrelated to SPY",
    )
    shares = (
        rates.stocks_passed / rates.stocks_tested,
        rates.walks_passed / rates.walks_tested,
    )
    bars = rate_ax.barh((1, 0), shares, height=0.45, color=(GOOD, ACCENT), gid="shares")
    for bar, share, label in zip(bars, shares, labels, strict=True):
        middle = bar.get_y() + bar.get_height() / 2
        # The ground behind each label hides the nominal line where it crosses.
        rate_ax.text(
            0,
            middle + 0.36,
            label,
            va="center",
            color=INK,
            fontsize=10,
            gid="label",
            bbox={"facecolor": GROUND, "edgecolor": "none", "pad": 1.5},
        )
        rate_ax.text(
            share + 0.004, middle, f"{100 * share:.1f}%", va="center", color=INK, fontsize=10
        )
    nominal = 1 - SCREEN_LEVEL / 100
    rate_ax.axvline(nominal, color=MUTED, lw=1.1, ls="--", gid="nominal")
    rate_ax.text(
        nominal + 0.004,
        1.75,
        f"nominal {100 * nominal:.0f} percent at the {SCREEN_LEVEL} percent bar",
        va="center",
        color=MUTED,
        fontsize=9.5,
    )
    rate_ax.set_yticks(())
    rate_ax.set_ylim(-0.4, 1.95)
    rate_ax.set_xlim(0, 0.35)
    rate_ax.xaxis.set_major_formatter(PercentFormatter(1.0))
    rate_ax.set_xlabel("share passing the screen over 2007", color=INK, fontsize=10)
    _heading(
        rate_ax,
        "The screen tests each series against SPY's 2007 closes at the trace test's 90 percent\n"
        "bar. Random walks with no drift, which are not stocks, pass more often than the stocks\n"
        "do, so the count of stocks passing is no evidence that any of them cointegrates with SPY.",
    )

    _title(
        fig,
        "Exploratory and survivor-only: SPY against the stocks that pass Chan's screen",
        f"Algorithmic Trading, Example 4.2, location 2035. Stocks from {STOCK_FILE}, saved "
        f"{stock_members[0].obtained},\nand SPY from {ETF_FILE}, saved {spy_member.obtained}. "
        "The stocks and the weights are fitted on 2007 and traded from 2008,\nbut the lookback "
        "of 5 was chosen with hindsight, and every stock in the file survived to 2012.",
    )
    fig.tight_layout(rect=(0, 0.08, 1, 0.97))
    return _save(fig, out, FIGURE)


def main() -> None:
    try:
        make_index_arbitrage_figure()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day is worth nothing at
        # the bottom of a traceback, so it reaches the operator as one line, the
        # way chan.index_arbitrage.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / FIGURE}")


if __name__ == "__main__":
    main()
