"""The figure for the post on VX against ES, *Algorithmic Trading*'s hedge from August 2008.

``blog/vx-es-lessons.md`` teaches what Entry 28 of the replication log found,
and [issue 431](https://github.com/l3a0/quantitative-trading/issues/431) asked
for it. :func:`make_vx_es_figure` draws three panels after the book's Figures
5.10 to 5.12, in the order the post reads them.

1. ``50·ES`` against ``1000·VX`` over the 2012-05-07 save's 1,999 common
   days, as ``VX_ES.m``'s ``scatter`` draws them for Figure 5.10, coloured by
   the two regimes location 2552 names, 2004 to May 2008 and August 2008 to
   2012. The book's text ignores the days between them, and so does the fit.
   The fitted line is drawn over the training days' range of VX.
2. The z-score from the anchor, 2008-08-04, with the band at ±1 and the last
   training day marked. Each run of days the band holds one position is
   shaded, green long and red short. Figure 5.11 draws the portfolio in
   dollars, and this panel draws it in training deviations so the band shows.
3. The test set's compounded cumulative return, which the book prints as
   Figure 5.12, with the three changes of position and 2011-08-05 marked.
   Standard and Poor's announced its downgrade of the U.S. credit rating after
   that day's close, and location 2559 says the trade "was particularly
   profitable" from around then.

Every value comes from :func:`chan.vx_es.read_legs` and
:func:`chan.vx_es.vx_es`, the run's own path, so the scale-break guard runs
here too::

    uv run python -m chan.vx_es_figures
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter, YearLocator
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter, PercentFormatter

from chan.coin_flip_figures import _dollars, _plain_text, _save, _style, _title
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED, RULE, SURFACE
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageEntry, VintageUnavailable
from chan.vx_es import (
    BAND,
    BOOK_APR_PERCENT,
    BOOK_SHARPE,
    ES,
    ES_POINT_VALUE,
    SOURCE_FILE,
    VX,
    VX_POINT_VALUE,
    Trade,
    VxEs,
    position_changes,
    read_legs,
    vx_es,
)

VX_ES_FIGURE = "vx_es.png"

#: The last day of location 2552's first regime, "2004 to May 2008".
FIRST_REGIME_END = pd.Timestamp("2008-05-31")
#: The first day of its second, "August 2008 to 2012".
SECOND_REGIME_START = pd.Timestamp("2008-08-01")
#: Standard and Poor's announced the downgrade after this day's close.
DOWNGRADE = pd.Timestamp("2011-08-05")

#: Each group of days on the scatter: its gid, its colour and its legend label.
REGIMES = (
    ("first", ACCENT, "2004 to May 2008"),
    ("between", RULE, "June and July 2008, between the regimes"),
    ("second", INK, "August 2008 to May 2012"),
)


@dataclass(frozen=True)
class Holding:
    """A run of consecutive days on which the band holds one position, ``units``."""

    first: pd.Timestamp
    last: pd.Timestamp
    units: float


def regime_masks(days: pd.DatetimeIndex) -> dict[str, np.ndarray]:
    """Which days fall in each of location 2552's regimes, and which fall between them."""
    first = days <= FIRST_REGIME_END
    second = days >= SECOND_REGIME_START
    return {"first": first, "between": ~first & ~second, "second": second}


def holdings(traded: Trade) -> list[Holding]:
    """Each run of days the band's units stay the same, from the anchor to the last test day.

    A position taken at a day's close is the units of that day, so a run's
    first day is the day the band entered it.
    """
    units = traded.units
    runs, start = [], 0
    for i in range(1, len(units) + 1):
        if i == len(units) or units[i] != units[start]:
            runs.append(Holding(traded.days[start], traded.days[i - 1], float(units[start])))
            start = i
    return runs


def cumulative_return(traded: Trade) -> pd.Series:
    """``cumprod(1 + ret) − 1`` over the test days, the series Figure 5.12 draws."""
    return pd.Series(np.cumprod(1 + traded.daily) - 1, index=traded.test_days)


def signed(value: float, places: int = 2) -> str:
    """``value`` to ``places`` decimals with a true minus sign, as the post prints it."""
    return f"{value:.{places}f}".replace("-", "−")


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


def _scatter_panel(ax, legs: pd.DataFrame, result: VxEs) -> None:
    vx = VX_POINT_VALUE * legs[VX].to_numpy(dtype=float)
    es = ES_POINT_VALUE * legs[ES].to_numpy(dtype=float)
    masks = regime_masks(legs.index)
    for gid, colour, label in REGIMES:
        mask = masks[gid]
        ax.scatter(
            vx[mask],
            es[mask],
            s=6,
            color=colour,
            alpha=0.75,
            lw=0,
            gid=gid,
            label=f"{label}, {int(mask.sum()):,} days",
        )
    h = result.hedge
    training = VX_POINT_VALUE * legs.loc[h.days, VX].to_numpy(dtype=float)
    x = np.array([training.min(), training.max()])
    ax.plot(
        x,
        h.intercept - h.hedge * x,
        color=LOST,
        lw=2.0,
        gid="fit",
        label=f"the fit on the {len(h.days)} training days",
    )
    ax.xaxis.set_major_formatter(FuncFormatter(_dollars))
    ax.yaxis.set_major_formatter(FuncFormatter(_dollars))
    ax.set_xlabel("1000·VX, dollars per contract", color=INK, fontsize=10)
    ax.set_ylabel("50·ES, dollars per contract", color=INK, fontsize=10)
    ax.legend(loc="upper right", frameon=False, fontsize=9.5, labelcolor=INK, markerscale=3)
    _heading(
        ax,
        f"Figure 5.10: 50·ES against 1000·VX on each of the {len(legs):,} days both traded.\n"
        f"The fit on {h.days[0].date()} to {h.days[-1].date()} is long {h.hedge:.4f} VX "
        f"contracts against one ES,\nwith a residual deviation of ${h.residual_std:,.2f}.",
    )


def _zscore_panel(ax, result: VxEs) -> None:
    t = result.trade
    runs = holdings(t)
    # Each shade runs to the day the next position is taken, so no day is left unshaded.
    ends = [after.first for after in runs[1:]] + [runs[-1].last]
    for held, end in zip(runs, ends, strict=True):
        if held.units:
            ax.axvspan(
                held.first,
                end,
                color=GOOD if held.units > 0 else LOST,
                alpha=0.13,
                lw=0,
                gid="long" if held.units > 0 else "short",
            )
    for gid, level in (("upper", BAND), ("lower", -BAND)):
        ax.axhline(level, color=MUTED, lw=1.0, ls=":", gid=gid)
    ax.axhline(0, color=RULE, lw=0.9, gid="zero")
    ax.axvline(result.hedge.days[-1], color=MUTED, lw=1.0, ls="--", gid="split")
    ax.plot(t.days, t.zscore, color=INK, lw=1.0, gid="zscore")
    low = int(np.argmin(t.zscore))
    ax.set_xlim(t.days[0], t.days[-1])
    ax.xaxis.set_major_locator(YearLocator())
    ax.xaxis.set_major_formatter(DateFormatter("%Y"))
    ax.set_ylabel("training deviations", color=INK, fontsize=10)
    _heading(
        ax,
        f"The z-score from {t.days[0].date()}, with the band at ±{BAND}. Shaded green while "
        "long and red while short.\n"
        f"Dashed: the last training day, {result.hedge.days[-1].date()}. "
        f"The lowest, {signed(t.zscore[low])}, is on {t.days[low].date()}.",
    )


def _returns_panel(ax, result: VxEs) -> None:
    t = result.trade
    cumret = cumulative_return(t)
    changes = [day for day, _ in position_changes(t)]
    ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    ax.axvline(DOWNGRADE, color=LOST, lw=1.0, ls="--", gid="downgrade")
    ax.plot(cumret.index, cumret, color=INK, lw=1.6, gid="cumulative")
    ax.plot(
        changes,
        cumret.loc[changes],
        "o",
        ms=6,
        color=ACCENT,
        mec=SURFACE,
        mew=1.6,
        zorder=3,
        gid="changes",
    )
    at_downgrade = cumret.loc[DOWNGRADE]
    ax.annotate(
        f"{signed(100 * at_downgrade)} percent at the close of {DOWNGRADE.date()}",
        (DOWNGRADE, at_downgrade),
        xytext=(-150, 70),
        textcoords="offset points",
        ha="left",
        color=LOST,
        arrowprops={"arrowstyle": "-", "color": LOST, "lw": 1.0},
        fontsize=9.5,
        fontweight="bold",
        gid="downgrade-label",
    )
    ax.set_xlim(cumret.index[0], cumret.index[-1])
    ax.xaxis.set_major_formatter(DateFormatter("%b %Y"))
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.set_ylabel("cumulative return, compounded", color=INK, fontsize=10)
    _heading(
        ax,
        f"Figure 5.12: the test set, {cumret.index[0].date()} to {cumret.index[-1].date()}, "
        f"ending at {100 * cumret.iloc[-1]:.2f} percent. Dots: the three changes of position.\n"
        f"APR {t.apr:.6f} and Sharpe ratio {t.sharpe:.6f}, where the book prints "
        f"{BOOK_APR_PERCENT} percent and {BOOK_SHARPE}. No cost is charged.",
    )


@_plain_text
def make_vx_es_figure(
    out: Path | None = None,
    sources: tuple[list[VintageEntry], pd.DataFrame] | None = None,
) -> Figure:
    """The regimes, the z-score with its band, and the test set's cumulative return."""
    members, legs = sources if sources is not None else read_legs()
    result = vx_es(legs)

    fig = Figure(figsize=(10, 14), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    scatter_ax, z_ax, returns_ax = fig.subplots(
        3, 1, gridspec_kw={"height_ratios": (1.3, 1, 1), "hspace": 0.5}
    )
    for ax in (scatter_ax, z_ax, returns_ax):
        _style(ax)
    _scatter_panel(scatter_ax, legs, result)
    _zscore_panel(z_ax, result)
    _returns_panel(returns_ax, result)

    saved = sorted({m.obtained for m in members})
    _title(
        fig,
        "Exploratory: VX against ES from August 2008, on Chan's 2012-05-07 save",
        f"Algorithmic Trading, locations 2546 to 2559. Closes from {SOURCE_FILE}, saved "
        f"{', '.join(saved)}.\nThe save and the exit were chosen because they land the printed "
        "figures, so the match is partly built in.",
    )
    fig.subplots_adjust(left=0.1, right=0.97, top=0.915, bottom=0.07)
    return _save(fig, out, VX_ES_FIGURE)


def main() -> None:
    try:
        make_vx_es_figure()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day is worth nothing at
        # the bottom of a traceback, so it reaches the operator as one line, the
        # way chan.vx_es.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / VX_ES_FIGURE}")


if __name__ == "__main__":
    main()
