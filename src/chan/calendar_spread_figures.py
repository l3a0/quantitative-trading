"""The calendar-spreads post's one figure, drawn from the committed EIA files.

``blog/calendar-spreads-lessons.md`` teaches in its Lesson 2 that the
simulated contracts a share is judged against have to move together as real
ones do. Issue 137 declared a null of independent walks, review found real
neighbouring contracts move almost as one, and the owner ruled on 2026-10-03 to
re-judge both commodities against walks correlated at the files' own median.
The correction moved RBOB's verdict and not natural gas's, so the figure draws
both nulls side by side for each commodity. Issue 314 planned its shape.

:func:`make_nulls_figure` draws two panels, natural gas above and RBOB
gasoline below.

1. **Two histograms of 1,000 null shares each**, the declared null of
   independent walks and the corrected null at the files' correlation. The
   axis counts pairs rather than shares, so it reads 57, 47 and 19 as the post
   does.
2. **Each null's bar as a dashed line**, the 975th of its 1,000 shares, in the
   null's own colour.
3. **The real count as a solid line** with a marker at its foot, and the
   count in the panel's title.

Nothing is drawn in the verdict colours, because the figure grades nothing.
The title says the result is exploratory. No pair and no window is drawn, so
the objection ``docs/design.md``'s register row "Figures for the stationary
candidates" records against reading one window as a finding does not reach
it.

Every value comes from :func:`chan.stationary_candidates.calendar_spread`, so
the figure can only be wrong by drawing the wrong thing, which
``tests/test_calendar_spread_figures.py`` checks. It reads the committed
vintages, so it redraws anywhere the data is::

    uv run python -m chan.calendar_spread_figures
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from matplotlib.figure import Figure
from numpy.typing import NDArray

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, INK, MUTED, SURFACE
from chan.stationary_candidates import SPREAD_PRODUCTS, CalendarSpread, calendar_spread
from chan.vintage import VintageUnavailable

NULLS_FIGURE = "calendar_spread_nulls.png"

#: The day all eight files the pairs read were downloaded, which
#: ``tests/test_calendar_spread_figures.py`` holds to each one's manifest line,
#: so the note cannot name a date the vintages do not carry.
DOWNLOADED = "2026-10-02"

#: One colour per null. Neither is a verdict colour.
DECLARED_COLOUR = MUTED
CORRECTED_COLOUR = ACCENT


def spreads() -> tuple[CalendarSpread, ...]:
    """Both commodities' batches, natural gas first, as the replication runs them."""
    return tuple(calendar_spread(product) for product in SPREAD_PRODUCTS)


def pairs_of(shares: NDArray[np.float64] | float, n: int) -> NDArray[np.int64]:
    """Shares of ``n`` pairs as the whole numbers of pairs they are."""
    return np.rint(np.asarray(shares) * n).astype(np.int64)


def real_count(spread: CalendarSpread) -> int:
    """How many of the commodity's pairs reject in both orientations."""
    return int(pairs_of(spread.share, len(spread.tests)))


def _panel(ax, spread: CalendarSpread, name: str) -> None:
    _style(ax)
    n = len(spread.tests)
    declared = pairs_of(spread.declared_null, n)
    corrected = pairs_of(spread.null, n)
    real = real_count(spread)
    # One bin per whole pair, centred on it, so a bar's height is how many of
    # the 1,000 sets gave exactly that count.
    top = max(int(declared.max()), int(corrected.max()), real) + 3
    edges = np.arange(-0.5, top + 1.5)
    for counts, colour, key in (
        (declared, DECLARED_COLOUR, "declared"),
        (corrected, CORRECTED_COLOUR, "corrected"),
    ):
        _, _, patches = ax.hist(counts, bins=edges, color=colour, alpha=0.55, zorder=3)
        for patch in patches:
            patch.set_gid(f"{name}-{key}-bin")
    tallest = ax.get_ylim()[1]
    # Both labels hang to the left of their lines, at two heights, because the
    # real count can sit one pair from the declared bar, as RBOB's 14 does
    # beside 13.
    for cut, colour, key, drop in (
        (spread.declared_cut, DECLARED_COLOUR, "declared", -6),
        (spread.cut, CORRECTED_COLOUR, "corrected", -24),
    ):
        bar = int(pairs_of(cut, n))
        ax.axvline(bar, color=colour, lw=1.6, ls="--", zorder=4, gid=f"{name}-{key}-bar")
        ax.annotate(
            f"{key} null's bar: {bar}",
            (bar, 1.0),
            xycoords=("data", "axes fraction"),
            xytext=(-5, drop),
            textcoords="offset points",
            ha="right",
            va="top",
            color=colour,
            fontsize=9.5,
            gid=f"{name}-{key}-label",
        )
    ax.axvline(real, color=INK, lw=1.4, zorder=4, gid=f"{name}-real-line")
    ax.plot(
        [real],
        [0],
        ls="none",
        marker="D",
        markersize=8,
        color=INK,
        clip_on=False,
        zorder=5,
        gid=f"{name}-real",
    )
    ax.set_xlim(-0.5, top + 0.5)
    ax.set_ylim(0, tallest * 1.35)
    ax.set_ylabel("null sets of 1,000", color=INK, fontsize=10)


@_plain_text
def make_nulls_figure(
    results: tuple[CalendarSpread, ...] | None = None, out: Path | None = None
) -> Figure:
    """Both nulls and the real count, one panel per commodity."""
    gas, rbob = results if results is not None else spreads()

    fig = Figure(figsize=(10, 8.4), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    top, bottom = fig.subplots(2, 1)
    _panel(top, gas, "gas")
    _panel(bottom, rbob, "rbob")
    top.set_title(
        f"Natural gas: {real_count(gas)} of {len(gas.tests)} pairs reject in both orientations",
        loc="left",
        color=INK,
        fontsize=11,
    )
    bottom.set_title(
        f"RBOB gasoline: {real_count(rbob)} of {len(rbob.tests)} pairs reject in both orientations",
        loc="left",
        color=INK,
        fontsize=11,
    )
    bottom.set_xlabel("pairs rejecting in both orientations at 10%", color=INK, fontsize=10)

    symbols = "\n".join(
        f"{spread.product.name}: {', '.join(spread.product.symbols)}" for spread in (gas, rbob)
    )
    _title(
        fig,
        "Chan's calendar spreads against two nulls, an exploratory result",
        f"EIA's NYMEX settlements, downloaded {DOWNLOADED}:\n{symbols}.\n"
        "Each histogram is 1,000 sets of simulated contracts that do not cointegrate, "
        "read on the days the real pairs keep.\nThe grey null makes every contract an "
        "independent walk, as declared before any statistic. The brass null\ncorrelates "
        "them at the files' own median, the correction made after the result was seen.",
    )
    fig.tight_layout(rect=(0, 0.14, 1, 0.96))
    return _save(fig, out, NULLS_FIGURE)


def main() -> None:
    try:
        results = spreads()
    except VintageUnavailable as refusal:
        # The refusal `chan.stationary_candidates.main` would end in, as one
        # line: a sentence naming the missing vintage is worth nothing at the
        # bottom of a traceback.
        raise SystemExit(str(refusal)) from refusal
    make_nulls_figure(results)
    print(f"wrote {FIGURES_DIR / NULLS_FIGURE}")


if __name__ == "__main__":
    main()
