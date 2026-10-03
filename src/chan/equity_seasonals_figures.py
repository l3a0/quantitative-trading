"""The equity-seasonals post's one figure, drawn from the committed S&P 500 file.

``blog/equity-seasonals-lessons.md`` teaches in its Lesson 3 that reproducing a
strategy published as dead checks its printed figures and not its death. The
exploratory split at 2002 is where that lesson reaches the data, and the owner
chose on 2026-10-02 to give it a figure, the one issue 240 named.

:func:`make_split_figure` draws the 83 months Example 7.7 keeps under the
revised edition's Python, :data:`chan.equity_seasonals.PYTHON_HESTON_SADKA`,
from 2000-12-31 to 2007-10-31.

1. **A running sum rather than a compounded path.**
   :func:`chan.equity_seasonals.summarize` annualises the arithmetic mean as 12
   times it, so each half's slope is its annual return over 12 and the line
   agrees with the figures the post quotes. A compounded path would end on a
   number nothing quotes.
2. **A vertical line at** :data:`chan.equity_seasonals.SPLIT`, with each half
   labelled by its month count, annual return and Sharpe ratio from
   :func:`chan.equity_seasonals.split_at`.
3. **A y-axis in fractions of capital**, the units
   ``HestonSadkaRules.per_position`` names, so nobody reads the line against
   the first edition's −0.9167, which is in units of summed positions.

A single window invites reading as a finding, which is the objection the
register row on the stationary candidates' figures in ``docs/design.md``
records. This figure answers it in words, as that post's window figure does.
The title says the split is exploratory and carries no verdict, and the note
says the file holds only survivors and that one year moves a running sum
through 83 months a long way. Nothing is drawn in the verdict colours.

Every value comes from :func:`chan.equity_seasonals.heston_sadka` and
:func:`chan.equity_seasonals.split_at`, so the figure can only be wrong by
drawing the wrong thing, which ``tests/test_equity_seasonals_figures.py``
checks. It reads the committed vintage, so it redraws anywhere the data is::

    uv run python -m chan.equity_seasonals_figures
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import pandas as pd
from matplotlib.figure import Figure

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.equity_seasonals import (
    LARGE_CAPS,
    PYTHON_HESTON_SADKA,
    SPLIT,
    heston_sadka,
    split_at,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import INK, MUTED, RULE, SURFACE
from chan.series import load_panel, panel_line
from chan.vintage import VintageUnavailable

SPLIT_FIGURE = "equity_seasonals_split.png"


def running_sum(closes: pd.DataFrame) -> pd.Series:
    """The kept months' returns under the revised Python's rules, summed as they go."""
    rules = PYTHON_HESTON_SADKA
    return heston_sadka(closes, rules).returns.iloc[rules.dropped :].cumsum()


def _signed(x: float) -> str:
    """A figure at the revised Python's printed precision, with a typographic minus."""
    return format(x, PYTHON_HESTON_SADKA.printed).replace("-", "−")


def half_label(when: str, half: tuple[int, float, float]) -> str:
    """One half's month count, annual return and Sharpe ratio, as the figure prints them."""
    months, annual, sharpe = half
    return f"{months} months {when} 2002\n{_signed(annual)} a year\nSharpe ratio {_signed(sharpe)}"


@_plain_text
def make_split_figure(
    panel: tuple[object, pd.DataFrame] | None = None, out: Path | None = None
) -> Figure:
    """The running sum through 83 months, split at 2002 and labelled by half."""
    members, closes = panel if panel is not None else load_panel(LARGE_CAPS)
    line = running_sum(closes)
    before, after = split_at(heston_sadka(closes, PYTHON_HESTON_SADKA), PYTHON_HESTON_SADKA)

    fig = Figure(figsize=(10, 5.8), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.subplots()
    _style(ax)

    ax.axhline(0, color=MUTED, lw=0.9, zorder=1, gid="zero")
    ax.plot(line.index, line.to_numpy(), color=INK, lw=1.8, zorder=3, gid="running-sum")
    ax.axvline(SPLIT, color=MUTED, lw=1.1, ls="--", zorder=2, gid="split")

    for text, x, ha, gid in (
        (half_label("before", before), -8, "right", "label-before"),
        (half_label("from", after), 8, "left", "label-after"),
    ):
        ax.annotate(
            text,
            (SPLIT, 1.0),
            xycoords=("data", "axes fraction"),
            xytext=(x, -8),
            textcoords="offset points",
            ha=ha,
            va="top",
            color=INK,
            fontsize=9.5,
            linespacing=1.35,
            gid=gid,
        )

    low, high = float(line.min()), float(line.max())
    pad = (high - low) * 0.1
    ax.set_ylim(low - pad, high + 3.2 * pad)
    ax.set_ylabel(
        "running sum of monthly returns,\nas a fraction of capital", color=INK, fontsize=10
    )
    ax.set_xlabel("month-end the return is earned to", color=INK, fontsize=10)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(axis="x", color=RULE, lw=0.6, alpha=0.7)

    first, last = line.index[0].date(), line.index[-1].date()
    _title(
        fig,
        "Example 7.7 split at 2002, an exploratory cut with no verdict",
        f"{' '.join(panel_line(members).split())}, which holds only the\n"
        "companies in the S&P 500 the day Chan saved it. The revised edition's Python rules, "
        f"{len(line)} months from {first} to {last},\n"
        "each month's return divided by the positions held. "
        f"A running sum through {len(line)} months shows how far a single year moves it.",
    )
    fig.tight_layout(rect=(0, 0.14, 1, 0.95))
    return _save(fig, out, SPLIT_FIGURE)


def main() -> None:
    try:
        panel = load_panel(LARGE_CAPS)
    except VintageUnavailable as refusal:
        # The refusal `chan.equity_seasonals.main` prints, for the same reason:
        # a sentence naming the missing member is worth nothing at the bottom
        # of a traceback.
        raise SystemExit(str(refusal)) from refusal
    make_split_figure(panel)
    print(f"wrote {FIGURES_DIR / SPLIT_FIGURE}")


if __name__ == "__main__":
    main()
