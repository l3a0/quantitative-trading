"""A figure for the stationary-candidates post, drawn from the committed vintages.

``blog/stationary-candidates-lessons.md`` teaches that one series and a fitted
pair are read against different bars. The owner chose on 2026-10-02 to give
the post one figure, and :func:`make_bars_figure` draws that lesson as two
number lines of t-statistics.

1. **One series.** The bars of the ADF with a constant, ``ADF_CRIT_CONST``,
   with the CAD/AUD rate's statistic at one lag and at the first lag count
   whose residuals pass.
2. **A fitted pair.** Engle-Granger's bars, ``EG_CRIT_N2``, with TLT and IEF's
   statistic in each orientation, and the rate's two statistics drawn again as
   hollow marks, read against the pair's bars.

Every statistic comes from :func:`chan.stationary_candidates.cross_rate` and
:func:`chan.stationary_candidates.fixed_income`, so the figure can only be
wrong by drawing the wrong thing, which
``tests/test_stationary_candidates_figures.py`` checks. It draws no rolling
scan. Issue 16 ruled out a figure for these candidates because a picture of a
scan invites reading one window as a finding, and the register row in
``docs/design.md`` records why this one is different. It reads the committed
vintages, so it redraws anywhere the data is::

    uv run python -m chan.stationary_candidates_figures
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ithildincore.timeseries import ADF_CRIT_CONST, EG_CRIT_N2
from matplotlib.figure import Figure

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.paths import FIGURES_DIR
from chan.regime_figure import GOOD, INK, LOST, MUTED, RULE, SURFACE
from chan.stationary_candidates import (
    INTERMEDIATE,
    LONG,
    TEST_START,
    CrossRate,
    Orientation,
    cross_rate,
    fixed_income,
)

BARS_FIGURE = "stationary_candidates_bars.png"

#: The t-statistics the axis spans. The pair's 1% bar, -3.90, is the most
#: negative thing drawn and IEF on TLT, -2.3168, the least.
X_RANGE = (-4.1, -2.0)

#: Where each number line sits, the one series above the pair.
ONE_SERIES_Y, PAIR_Y = 1.0, 0.0

#: The order the bars are drawn and labelled in, most negative first.
LEVELS = ("1%", "5%", "10%")


@dataclass(frozen=True)
class Mark:
    """One statistic drawn on one number line."""

    gid: str
    x: float
    y: float
    colour: str
    hollow: bool
    label: str
    offset: tuple[float, float]


def _t(x: float, places: int = 4) -> str:
    """A t-statistic with a typographic minus, as the post prints it."""
    return f"{x:.{places}f}".replace("-", "−")


def marks(rate: CrossRate, orientations: tuple[Orientation, ...]) -> list[Mark]:
    """The six statistics the figure draws, in the order it draws them."""
    by = {o.dependent: o for o in orientations}
    one, passing = rate.adf_stat, rate.passing.adf_stat
    return [
        Mark("cadaud-1", one, ONE_SERIES_Y, GOOD, False, f"CAD/AUD, 1 lag\n{_t(one)}", (-12, -40)),
        Mark(
            "cadaud-passing",
            passing,
            ONE_SERIES_Y,
            GOOD,
            False,
            f"CAD/AUD, {rate.passing.lags} lags\n{_t(passing)}",
            (8, -40),
        ),
        Mark(
            "tlt-on-ief",
            by[LONG].fit.adf_stat,
            PAIR_Y,
            LOST,
            False,
            f"{LONG} on {INTERMEDIATE}\n{_t(by[LONG].fit.adf_stat)}",
            (-58, -40),
        ),
        Mark(
            "ief-on-tlt",
            by[INTERMEDIATE].fit.adf_stat,
            PAIR_Y,
            LOST,
            False,
            f"{INTERMEDIATE} on {LONG}\n{_t(by[INTERMEDIATE].fit.adf_stat)}",
            (6, -40),
        ),
        Mark("cadaud-1-as-pair", one, PAIR_Y, GOOD, True, "", (0, 0)),
        Mark(
            "cadaud-passing-as-pair",
            passing,
            PAIR_Y,
            GOOD,
            True,
            "CAD/AUD's two,\nread as a pair",
            (-86, -40),
        ),
    ]


def _line(ax, y: float, bars: dict[str, float], name: str) -> None:
    """One number line: the axis, the 5% region shaded, and three bars."""
    ax.plot(
        X_RANGE, (y, y), color=RULE, lw=1.4, solid_capstyle="butt", zorder=1, gid=f"axis-{name}"
    )
    ax.fill_between(
        (X_RANGE[0], bars["5%"]),
        y - 0.13,
        y + 0.13,
        color=GOOD,
        alpha=0.12,
        lw=0,
        gid=f"shade-{name}",
    )
    for level in LEVELS:
        x = bars[level]
        ax.plot(
            (x, x), (y - 0.16, y + 0.16), color=MUTED, lw=1.4, zorder=2, gid=f"bar-{name}-{level}"
        )
        ax.annotate(
            f"{level}\n{_t(x, 2)}",
            (x, y + 0.16),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            color=MUTED,
            fontsize=9.5,
        )


@_plain_text
def make_bars_figure(
    out: Path | None = None,
    rate: CrossRate | None = None,
    orientations: tuple[Orientation, ...] | None = None,
) -> Figure:
    """Both tables of bars, with the four headline statistics on them."""
    rate = rate if rate is not None else cross_rate()
    orientations = orientations if orientations is not None else fixed_income()[1]
    drawn = marks(rate, orientations)

    fig = Figure(figsize=(10, 5.6), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.subplots()
    _style(ax)
    ax.grid(False)
    ax.spines["left"].set_visible(False)

    _line(ax, ONE_SERIES_Y, ADF_CRIT_CONST, "adf")
    _line(ax, PAIR_Y, EG_CRIT_N2, "eg")

    for m in drawn:
        ax.plot(
            [m.x],
            [m.y],
            "o",
            ms=9,
            color=m.colour,
            mfc="none" if m.hollow else m.colour,
            mec=m.colour if m.hollow else SURFACE,
            mew=2,
            zorder=3,
            gid=f"mark-{m.gid}",
        )
        if m.label:
            ax.annotate(
                m.label,
                (m.x, m.y),
                xytext=m.offset,
                textcoords="offset points",
                color=INK,
                fontsize=9.5,
                linespacing=1.3,
            )

    ax.set_xlim(*X_RANGE)
    ax.set_ylim(PAIR_Y - 0.62, ONE_SERIES_Y + 0.55)
    ax.set_yticks(
        [ONE_SERIES_Y, PAIR_Y],
        ["one series,\nADF with a constant", "a fitted pair,\nEngle-Granger"],
    )
    ax.tick_params(axis="y", length=0, labelsize=10.5, labelcolor=INK)
    ax.set_xlabel(
        "t-statistic, where further left is stronger evidence of a stationary series or spread",
        color=INK,
        fontsize=10.5,
    )
    _title(
        fig,
        "CAD/AUD clears the bar for one series and would miss the bar for a fitted pair",
        f"CADAUD=X, log of the rate, {TEST_START} to 2026-09-30. TLT and IEF raw closes, "
        "2002-07-30 to 2026-10-01. All downloaded 2026-10-02.\n"
        "Shaded: past the 5% bar. Hollow: CAD/AUD's two statistics read against the "
        "pair's bars, which pay for a fitted hedge ratio.",
    )
    fig.tight_layout(rect=(0, 0.08, 1, 0.95))
    fig.marks = drawn
    return _save(fig, out, BARS_FIGURE)


def main() -> None:
    make_bars_figure()
    print(f"wrote {FIGURES_DIR / BARS_FIGURE}")


if __name__ == "__main__":
    main()
