"""The figure for the post on Conditional Parameter Optimization, Example 7.1.

``blog/conditional-parameter-optimization-lessons.md`` teaches what Entry 16 of
the replication log found, and
[issue 316](https://github.com/l3a0/quantitative-trading/issues/316) planned
one figure for its fourth lesson. :func:`make_cells_figure` draws the 400 cells
of the parameter grid, each at its round trips a day on the test days, on a log
axis, against its test Sharpe ratio before costs.

1. **A horizontal line at Chan's 1.947**, his unconditional Sharpe ratio.
2. **Three labelled cells**, each found from the run rather than named here:
   the cell the train years chose, the cell with the highest test Sharpe ratio,
   and the cell nearest 1.947.

The scatter shows what no table in the post shows: the selection rule picks
turnover, and Chan's figure sits among the cells that trade about once a day.
Entry 16's row 10, which the figure draws, was added after the result was
seen, so the title says so beside the exploratory label. The note names both
vintages by hash prefix and says nothing is charged for costs. Every point is
a test-day figure, and the test days end on 2020-12-31, so the figure draws
nothing past the date ``docs/design.md``'s register row on the daily study
protects.

:func:`make_cells_figure` takes a :class:`chan.cpo.Result` rather than calling
:func:`chan.cpo.run`, so ``tests/test_cpo_figures.py`` draws a synthetic one on
every clone. Only the real run needs the owner's archive of minute bars, so
the committed PNG redraws only where that archive is, in about five minutes::

    QT_ARCHIVE_DIR=/path/to/archive uv run python -m chan.cpo_figures
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

from chan import cpo
from chan.archive import ArchiveRefused, ArchiveUnavailable
from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GROUND, INK, LOST, MUTED, SURFACE

CELLS_FIGURE = "cpo_cells.png"

#: Chan's unconditional Sharpe ratio, the line the figure draws.
BOOK_SHARPE = cpo.BOOK_UNCONDITIONAL["sharpe"]


def labelled_cells(result: cpo.Result) -> dict[str, int]:
    """The three cells the figure names, as positions in grid order.

    ``chosen`` is the cell the train years chose, ``highest`` the cell with the
    highest test Sharpe ratio, and ``nearest`` the cell whose test Sharpe ratio
    sits closest to Chan's 1.947.
    """
    sharpes = result.cell_sharpes
    return {
        "chosen": cpo.cells().index(result.unconditional),
        "highest": int(np.argmax(sharpes)),
        "nearest": int(np.argmin(np.abs(sharpes - BOOK_SHARPE))),
    }


#: What each label says before the cell's own spelling, and where it sits
#: against its point, in points. On the real run the chosen and the highest
#: cells trade the same 46.7 round trips a day and sit one above the other at
#: the top right of the cloud, so the higher one's label hangs above it and the
#: lower one's below, both to the left.
LABELS = {
    "chosen": ("chosen on the train years", (-12, -20), "right", LOST),
    "highest": ("highest test Sharpe ratio", (-12, 16), "right", INK),
    "nearest": ("nearest Chan's 1.947", (10, -24), "left", ACCENT),
}


def _trips(x: float, _pos: object = None) -> str:
    """A tick on the round-trip axis, whole above one and one decimal below."""
    return f"{x:g}"


@_plain_text
def make_cells_figure(result: cpo.Result, out: Path | None = None) -> Figure:
    """The 400 cells' test Sharpe ratios against their round trips a day."""
    trips = result.cell_trips
    sharpes = result.cell_sharpes
    grid = cpo.cells()
    marked = labelled_cells(result)

    fig = Figure(figsize=(10, 6.6), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.subplots()
    _style(ax)
    ax.set_xscale("log")

    ax.scatter(trips, sharpes, s=18, color=MUTED, alpha=0.55, linewidths=0, zorder=3, gid="cells")
    ax.axhline(BOOK_SHARPE, color=ACCENT, lw=1.4, ls="--", zorder=2, gid="book-line")
    ax.annotate(
        f"Chan's Sharpe ratio, {BOOK_SHARPE}",
        (1.0, BOOK_SHARPE),
        xycoords=("axes fraction", "data"),
        xytext=(-4, 5),
        textcoords="offset points",
        ha="right",
        va="bottom",
        color=ACCENT,
        fontsize=9.5,
        gid="book-label",
    )
    for key, at in marked.items():
        words, offset, align, colour = LABELS[key]
        ax.plot(
            [trips[at]],
            [sharpes[at]],
            "o",
            ms=7,
            color=colour,
            mec=SURFACE,
            mew=1.4,
            zorder=4,
            gid=key,
        )
        ax.annotate(
            f"{grid[at].label}, {words}\n{trips[at]:.3g} round trips a day, "
            f"Sharpe ratio {sharpes[at]:.3f}",
            (trips[at], sharpes[at]),
            xytext=offset,
            textcoords="offset points",
            ha=align,
            va="center",
            color=colour,
            fontsize=9.5,
            # The chosen cell's label lands on the cloud, so every label sits
            # on a patch of the axes ground that hides the points behind it.
            bbox={"boxstyle": "round,pad=0.25", "fc": GROUND, "ec": "none", "alpha": 0.9},
            zorder=5,
            gid=f"{key}-label",
        )

    ax.xaxis.set_major_formatter(FuncFormatter(_trips))
    ax.set_xlabel("round trips a day on the test days, log scale", color=INK, fontsize=10)
    ax.set_ylabel("test Sharpe ratio, before costs", color=INK, fontsize=10)
    low, high = float(sharpes.min()), float(sharpes.max())
    ax.set_ylim(min(low, BOOK_SHARPE) - 0.5, high + 0.6)

    days = result.test_days
    vintages = "\n".join(
        f"{entry.symbol}: {entry.path}, sha256 {entry.sha256[:8]}…, "
        f"downloaded {entry.download_date}"
        for entry in result.vintages
    )
    _title(
        fig,
        "Exploratory, added after the result was seen: the selection picks turnover",
        f"Example 7.1's {len(sharpes)} cells, weight_lookback_entry, on the "
        f"{len(days)} test days from {days[0].date()} to {days[-1].date()}.\n"
        "Nothing is charged for costs. Alpha Vantage one-minute bars, as traded:\n"
        f"{vintages}",
    )
    fig.tight_layout(rect=(0, 0.15, 1, 0.96))
    return _save(fig, out, CELLS_FIGURE)


def main() -> None:
    try:
        result = cpo.run()
    except (ArchiveUnavailable, ArchiveRefused) as refused:
        # A sentence naming what is missing is worth nothing at the bottom of a
        # traceback, so it reaches the operator as one line, the way
        # chan.buy_on_gap_figures.main does it.
        raise SystemExit(str(refused)) from refused
    make_cells_figure(result)
    print(f"wrote {FIGURES_DIR / CELLS_FIGURE}")


if __name__ == "__main__":
    main()
