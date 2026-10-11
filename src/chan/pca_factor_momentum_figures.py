"""The PCA factor momentum post's one figure, drawn from Chan's S&P 600 file.

``blog/pca-factor-momentum-lessons.md`` writes up Entry 42, which tests
whether the five factors Example 7.4 fits for itself have momentum.
[Issue 520](https://github.com/l3a0/quantitative-trading/issues/520) planned
the post and chose this figure, with two panels.

:func:`make_pca_factor_momentum_figure` draws them.

1. **The verdicts against the stocks.** The 579 stocks' statistics as their
   cumulative curve, drawn as a step, with the ±1.96/√752 band shaded, zero
   and the median stock. Each factor's statistic is a filled dot on the curve
   at its percentile among the stocks, so its height is that percentile. A
   hollow dot marks the same factor without PMC, at its percentile among the
   578 stocks left, and a thin line joins the two. No stock ties any factor,
   which ``TestWhatThePostMeasured`` pins, so the share at or below a factor
   is the share strictly below, which the percentile counts.
2. **Why each pair reads one day's vectors.** For each factor, four
   statistics side by side: on each day's own weights, with sign and rank
   matched, with tomorrow's weights fitted on the 251 days that leave today's
   return out, and the paired statistic the test reads. The third is a marker
   rather than a sentence because it is what closes the gap the first two
   leave.

The first panel draws the verdicts' figures, and the second figures measured
after the run, which decide nothing. Neither uses the green or the red other
figures here give a verdict, because no factor clears the noise. The title
calls the test exploratory and the note says the file holds only survivors.

Every value comes from one :class:`chan.pca_factor_momentum.Results` and one
:class:`chan.pca_factor_momentum.WeightStatistics`, so the figure can only be
wrong by drawing the wrong thing, which ``tests/test_pca_factor_momentum_figures.py``
checks. It reads the committed vintage, so it redraws anywhere the data is::

    uv run python -m chan.pca_factor_momentum_figures
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from matplotlib.figure import Figure

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.paths import FIGURES_DIR
from chan.pca_factor import SMALL_CAPS, SPLICED
from chan.pca_factor_momentum import (
    NAMES,
    Results,
    WeightStatistics,
    compute_both,
    daily_components,
    file_returns,
    weight_statistics,
)
from chan.regime_figure import ACCENT, INK, MUTED, RULE, SURFACE
from chan.series import load_panel
from chan.vintage import VintageUnavailable

PCA_FACTOR_MOMENTUM_FIGURE = "pca_factor_momentum.png"

#: Panel 2's four statistics, left to right within each factor: the field of
#: :class:`WeightStatistics` it reads, or ``"paired"`` for the test's own, and
#: its legend entry, colour, marker and whether the marker is filled.
WAYS = (
    ("own", "each day's own weights", MUTED, "o", False),
    ("matched", "sign and rank matched", MUTED, "s", True),
    ("left_out", "tomorrow's weights on 251 days without today", ACCENT, "D", True),
    ("paired", "both days on today's weights, as tested", INK, "o", True),
)

#: Where each factor's label starts in panel 1, in data units. The curve climbs
#: to the right, so the space below it on the right is empty. The labels run
#: down in the order of the dots' heights, PC2, PC5, PC1, PC4 and PC3, so no
#: two leader lines cross.
LABEL_SPOTS = {
    "PC2": (0.09, 0.68),
    "PC5": (0.09, 0.58),
    "PC1": (0.09, 0.48),
    "PC4": (0.09, 0.38),
    "PC3": (0.09, 0.28),
}

#: Panel 1's horizontal range, wide enough for every stock and the labels.
STATISTIC_RANGE = (-0.235, 0.16)


def _signed(x: float) -> str:
    """A figure at the four decimals the log quotes, with a typographic minus."""
    return format(x, ".4f").replace("-", "−")


def factor_label(name: str, spliced: float, unspliced: float) -> str:
    """One factor's statistic with PMC, then without it, as panel 1 prints them."""
    return f"{name} {_signed(spliced)} → {_signed(unspliced)}"


def _verdicts_panel(ax, results: Results) -> None:
    c, u = results.spliced.comparison, results.unspliced.comparison
    stocks = np.sort(c.stocks.to_numpy())
    count = len(stocks)
    heights = np.arange(1, count + 1) / count

    ax.axvspan(-c.band, c.band, color=RULE, alpha=0.45, lw=0, zorder=0, gid="band")
    ax.axvline(0, color=MUTED, lw=0.9, zorder=1, gid="zero")
    ax.axvline(c.median, color=MUTED, lw=1.1, ls=":", zorder=2, gid="median")
    ax.step(stocks, heights, where="post", color=INK, lw=1.4, zorder=3, gid="stocks")

    for k, name in enumerate(NAMES):
        tag = name.lower()
        at = (c.factors[k], c.percentile(c.factors[k]) / 100)
        without = (u.factors[k], u.percentile(u.factors[k]) / 100)
        ax.plot(
            [at[0], without[0]],
            [at[1], without[1]],
            color=ACCENT,
            lw=0.9,
            zorder=4,
            gid=f"{tag}-moves",
        )
        ax.plot(*at, "o", color=ACCENT, ms=6.5, zorder=6, gid=tag)
        ax.plot(
            *without,
            "o",
            mfc=SURFACE,
            mec=ACCENT,
            mew=1.4,
            ms=6.5,
            zorder=5,
            gid=f"{tag}-without",
        )
        ax.annotate(
            factor_label(name, c.factors[k], u.factors[k]),
            at,
            xytext=LABEL_SPOTS[name],
            textcoords="data",
            ha="left",
            va="center",
            color=INK,
            fontsize=9,
            arrowprops={
                "arrowstyle": "-",
                "color": RULE,
                "lw": 0.8,
                "shrinkB": 4,
                "relpos": (0, 0.5),
            },
            gid=f"label-{tag}",
        )

    ax.annotate(
        f"median stock {_signed(c.median)}",
        (c.median, 0.03),
        xytext=(-3, 0),
        textcoords="offset points",
        ha="right",
        va="bottom",
        rotation=90,
        color=MUTED,
        fontsize=9,
        gid="label-median",
    )
    ax.annotate(
        f"±{c.band:.4f}, where a series\nwith no persistence lands\n95 percent of the time",
        (c.band, 0.03),
        xytext=(6, 0),
        textcoords="offset points",
        ha="left",
        va="bottom",
        color=MUTED,
        fontsize=9,
        linespacing=1.35,
        gid="label-band",
    )
    ax.set_xlim(*STATISTIC_RANGE)
    ax.set_ylim(0, 1.02)
    ax.set_ylabel(f"share of the {count} stocks at or below", color=INK, fontsize=10)
    ax.set_xlabel(
        f"uncentred correlation of {c.pairs} pairs of one day's return and the next",
        color=INK,
        fontsize=10,
    )
    ax.grid(axis="x", color=RULE, lw=0.6, alpha=0.7)
    ax.set_title(
        f"The verdicts: each factor with {SPLICED}, filled, → without it, hollow",
        loc="left",
        color=INK,
        fontsize=11,
    )


def _ways_panel(ax, results: Results, weights: WeightStatistics) -> None:
    c = results.spliced.comparison
    ax.axhspan(-c.band, c.band, color=RULE, alpha=0.45, lw=0, zorder=0, gid="band")
    ax.axhline(0, color=MUTED, lw=0.9, zorder=1, gid="zero")
    centres = np.arange(len(NAMES))
    offsets = np.linspace(-0.27, 0.27, len(WAYS))
    for (field, label, colour, marker, filled), offset in zip(WAYS, offsets, strict=True):
        values = c.factors if field == "paired" else getattr(weights, field)
        ax.plot(
            centres + offset,
            values,
            marker,
            ls="none",
            ms=7,
            mec=colour,
            mfc=colour if filled else SURFACE,
            mew=1.4,
            zorder=3,
            label=label,
            gid=field,
        )
    ax.set_xticks(centres, NAMES)
    ax.set_xlim(-0.6, len(NAMES) - 0.4)
    ax.set_ylabel("uncentred correlation", color=INK, fontsize=10)
    ax.legend(
        loc="lower right",
        frameon=False,
        fontsize=9,
        labelcolor=INK,
        title="tomorrow's factor return read on",
        title_fontsize=9,
    )
    ax.set_title(
        "Why each pair reads one day's weights, measured after the run",
        loc="left",
        color=INK,
        fontsize=11,
    )


@_plain_text
def make_pca_factor_momentum_figure(
    results: Results, weights: WeightStatistics, out: Path | None = None
) -> Figure:
    """The verdicts against the stocks, and the four ways of reading tomorrow's factor return."""
    fig = Figure(figsize=(10, 11.5), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    verdicts_ax, ways_ax = fig.subplots(2, 1, gridspec_kw={"hspace": 0.32})
    for ax in (verdicts_ax, ways_ax):
        _style(ax)
    _verdicts_panel(verdicts_ax, results)
    _ways_panel(ways_ax, results, weights)

    count = len(results.spliced.comparison.stocks)
    _title(
        fig,
        "Example 7.4's own factors on Chan's S&P 600 file, an exploratory test",
        f"The {count} stocks are every stock in ijr_20080114/ priced on every day the pairs "
        "read. That file holds only the companies\nin the S&P 600 on 2008-01-14, so every "
        f"figure here is about survivors. A hollow dot sits at its percentile among the "
        f"{count - 1}\nstocks left without {SPLICED}. The shaded band is the same in both "
        "panels. Panel 2 was measured after the verdicts and decides nothing.",
    )
    fig.subplots_adjust(left=0.09, right=0.97, top=0.93, bottom=0.1)
    return _save(fig, out, PCA_FACTOR_MOMENTUM_FIGURE)


def main() -> None:
    try:
        _, closes = load_panel(SMALL_CAPS, field="Close")
    except VintageUnavailable as refused:
        # The refusal `chan.pca_factor_momentum.main` prints, for the same
        # reason: a sentence naming the missing member is worth nothing at the
        # bottom of a traceback.
        raise SystemExit(str(refused)) from refused
    returns = file_returns(closes)
    results = compute_both(closes)
    weights = weight_statistics(returns, daily_components(returns))
    make_pca_factor_momentum_figure(results, weights)
    print(f"wrote {FIGURES_DIR / PCA_FACTOR_MOMENTUM_FIGURE}")


if __name__ == "__main__":
    main()
