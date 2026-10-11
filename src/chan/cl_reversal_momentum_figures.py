"""The figure for the post on the crude oil reversal joined to momentum, location 2701.

``blog/crude-oil-reversal-momentum-lessons.md`` teaches what Entry 31 of the
replication log found. :func:`make_join_figure` redraws three of the four
cumulative return curves ``CL_rev.m`` plots: the join Chan prints figures for,
momentum alone and reversal alone. ComboOR, the fourth, is left out because it
is the join outside 10 warm-up rows. It draws two panels, one per segment, and
they cover different years, so they do not share a date axis.

1. The book's window, the 1,000 rows of the 2012-05-04 save, where the join
   beats each rule alone on both of the script's figures.
2. The 998 rows before it on the 2012-05-07 save, whose closes equal the
   first save's on all 1,000 of the book's days, where momentum alone beats
   the join.

Each curve compounds the rule's daily returns, ``prod(1 + ret) − 1`` to each
day, so it ends at ``(1 + apr) ** (n / 252) − 1`` for that rule's APR over
``n`` rows. Every value comes from :func:`chan.cl_reversal_momentum.read_cl`
and :func:`chan.cl_reversal_momentum.four_rules`, the run's own path, so the
scale-break guard runs here too::

    uv run python -m chan.cl_reversal_momentum_figures
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter, YearLocator
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter

from chan.cl_reversal_momentum import (
    BOOK_START,
    EARLIER_SOURCE_FILE,
    SOURCE_FILE,
    FourRules,
    Trades,
    four_rules,
    read_cl,
)
from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, INK, LOST, MUTED, SURFACE
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable

JOIN_FIGURE = "cl_reversal_momentum.png"

#: Each rule's line: its legend label and its colour, in drawing order.
RULES = (
    ("combination", "the join", INK),
    ("momentum", "momentum alone", ACCENT),
    ("reversal", "reversal alone", LOST),
)


def cumulative(traded: Trades) -> pd.Series:
    """The compounded return to each day, ``prod(1 + ret) − 1``, as ``CL_rev.m`` plots it."""
    return pd.Series(np.cumprod(1 + traded.daily) - 1, index=traded.days)


def percent(value: float) -> str:
    """``value`` as a percentage to one decimal, with a true minus sign."""
    return f"{100 * value:.1f}%".replace("-", "−")


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


def _panel(ax, rules: FourRules, legend: str) -> dict[str, pd.Series]:
    curves = {}
    for name, label, colour in RULES:
        curve = cumulative(getattr(rules, name))
        curves[name] = curve
        width = 1.8 if name == "combination" else 1.1
        ax.plot(curve.index, curve, color=colour, lw=width, gid=name, label=label)
    days = rules.combination.days
    ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    ax.set_xlim(days[0], days[-1])
    ax.xaxis.set_major_locator(YearLocator())
    ax.xaxis.set_major_formatter(DateFormatter("%Y"))
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))
    ax.set_ylabel("cumulative return", color=INK, fontsize=10)
    ax.legend(loc=legend, frameon=False, fontsize=9.5, labelcolor=INK)
    return curves


def _span(days: pd.DatetimeIndex) -> str:
    return f"{days[0].date()} to {days[-1].date()}"


@_plain_text
def make_join_figure(
    out: Path | None = None,
    book_closes: pd.Series | None = None,
    before_closes: pd.Series | None = None,
) -> Figure:
    """The three rules compounded over the book's window and over the four years before it."""
    if book_closes is None:
        book_closes = read_cl()[1]
    if before_closes is None:
        before_closes = read_cl(EARLIER_SOURCE_FILE, end=BOOK_START - pd.Timedelta(days=1))[1]
    book, before = four_rules(book_closes), four_rules(before_closes)

    fig = Figure(figsize=(10, 9), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    book_ax, before_ax = fig.subplots(2, 1)
    for ax in (book_ax, before_ax):
        _style(ax)

    curves = _panel(book_ax, book, "lower right")
    momentum, reversal = curves["momentum"], curves["reversal"]
    _heading(
        book_ax,
        f"The book's window, {_span(book_closes.index)}, {len(book_closes):,} rows. "
        f"The join ends at {percent(curves['combination'].iloc[-1])}.\n"
        f"Momentum alone peaks at {percent(momentum.max())} on {momentum.idxmax().date()} "
        f"and ends at {percent(momentum.iloc[-1])}. Reversal alone falls to "
        f"{percent(reversal.min())}\non {reversal.idxmin().date()} and ends at "
        f"{percent(reversal.iloc[-1])}.",
    )

    curves = _panel(before_ax, before, "upper left")
    _heading(
        before_ax,
        f"The {len(before_closes):,} rows before it, {_span(before_closes.index)}. "
        f"The join ends at {percent(curves['combination'].iloc[-1])},\n"
        f"momentum alone at {percent(curves['momentum'].iloc[-1])} and reversal alone at "
        f"{percent(curves['reversal'].iloc[-1])}.",
    )

    _title(
        fig,
        "Exploratory: Chan's crude oil join against each of the two rules it joins",
        "Algorithmic Trading, location 2701. CL_rev.m's rules compounded daily on Chan's "
        "back-adjusted CL, with no cost.\n"
        f"The book's window reads {SOURCE_FILE}, the save the script loads, and the rows "
        f"before it\nread {EARLIER_SOURCE_FILE}. Those closes sit far above the traded "
        "price, so the lower panel is the rule\non Chan's series rather than a trader's "
        "return.",
    )
    fig.tight_layout(rect=(0, 0.09, 1, 0.97))
    return _save(fig, out, JOIN_FIGURE)


def main() -> None:
    try:
        make_join_figure()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source is worth nothing at the bottom of a
        # traceback, so it reaches the operator as one line, the way
        # chan.cl_reversal_momentum.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / JOIN_FIGURE}")


if __name__ == "__main__":
    main()
