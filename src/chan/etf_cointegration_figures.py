"""The figure for the post on EWA, EWC and IGE, *Algorithmic Trading*'s Examples 2.6 to 2.8.

The post teaches what Entry 23 of the replication log found, and
[issue 402](https://github.com/l3a0/quantitative-trading/issues/402) asked for
it. :func:`make_cointegration_figure` draws four panels, in the order the
post reads them.

1. The closes of EWA and EWC over the whole file, which the book prints as
   Figure 2.4.
2. The residual ``EWC − h·EWA``, which ``cointegrationTests.m`` plots as
   ``y - hedgeRatio*x`` and the book prints as Figure 2.6. The hedge ratio
   comes from a regression with an intercept, and the plot leaves the
   intercept in, so the residual wanders around it rather than around zero.
   A dashed line marks it, since the residual's mean equals it.
3. The triplet's trace and eigen statistics, one pair of bars per null
   r ≤ 0, r ≤ 1 and r ≤ 2, each crossed by its 90, 95 and 99 percent critical
   values. The trace test clears its 95 percent bar on every null, while the
   eigen test's first statistic falls short of even its 90 percent bar.
   The book prints no figure for this.
4. The compounded cumulative return of the linear rule on the first
   eigenvector, which the book prints as Figure 2.7. The longest spell below
   the high is shaded and the deepest drawdown is marked, as
   :mod:`chan.buy_on_gap_figures` does. ``calculateMaxDD`` returns the two
   separately, and here the trough happens to sit inside the spell, which
   ``tests/test_etf_cointegration_figures.py`` holds.

Every value comes from :func:`chan.etf_cointegration.read_sources` and
:func:`chan.etf_cointegration.etf_cointegration`, the run's own path, so the
scale-break guard runs here too::

    uv run python -m chan.etf_cointegration_figures
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter, YearLocator
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import PercentFormatter

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.etf_cointegration import (
    BOOK_APR_PERCENT,
    BOOK_SHARPE,
    SOURCE_FILE,
    TRIPLET,
    EtfCointegration,
    X,
    Y,
    etf_cointegration,
    read_sources,
)
from chan.matlab_helpers import calculate_max_dd, drawdown_path
from chan.paths import FIGURES_DIR
from chan.pead_figures import _signed, longest_spell
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED, RULE, SURFACE
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageEntry, VintageUnavailable

COINTEGRATION_FIGURE = "etf_cointegration.png"

#: The critical values' levels, in the order the columns of ``trace_critical`` hold them,
#: with the dash each is drawn in.
LEVELS = ((90, ":"), (95, "-"), (99, "--"))
#: Each statistic's bars: its name, its fill, and how far its bar sits from the group's centre.
STATISTICS = (("trace", ACCENT, -0.19), ("eigen", GOOD, 0.19))
BAR_WIDTH = 0.34


def cumulative_return(result: EtfCointegration) -> np.ndarray:
    """``cumprod(1 + ret) − 1``, the series the script's last ``plot`` draws."""
    return np.cumprod(1 + result.strategy.daily) - 1


def residual(closes: pd.DataFrame, result: EtfCointegration) -> np.ndarray:
    """``y - hedgeRatio*x``, EWC less the hedge ratio times EWA, with no intercept taken out."""
    return closes[Y].to_numpy(dtype=float) - result.hedge_ratio * closes[X].to_numpy(dtype=float)


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


def _closes_panel(ax, closes: pd.DataFrame) -> None:
    for symbol, colour in ((X, ACCENT), (Y, INK)):
        ax.plot(closes.index, closes[symbol], color=colour, lw=1.1, gid=symbol, label=symbol)
    ax.set_ylabel("adjusted close, dollars", color=INK, fontsize=10)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK)
    _heading(ax, f"Figure 2.4: the closes of {X} and {Y} over the whole file.")


def _residual_panel(ax, closes: pd.DataFrame, result: EtfCointegration) -> None:
    values = residual(closes, result)
    ax.plot(closes.index, values, color=INK, lw=1.0, gid="residual", label="the residual")
    ax.axhline(
        values.mean(),
        color=MUTED,
        lw=1.0,
        ls="--",
        gid="mean",
        label=f"its mean, {values.mean():.2f}, which is the regression's intercept",
    )
    # The legend takes a band above the residual's highest point, so it covers nothing.
    span = values.max() - values.min()
    ax.set_ylim(values.min() - 0.08 * span, values.max() + 0.32 * span)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK, ncols=2)
    ax.set_ylabel("dollars", color=INK, fontsize=10)
    _heading(
        ax,
        f"Figure 2.6: the residual {Y} − {result.hedge_ratio:.4f}·{X}, the hedge ratio from "
        f"{Y} on {X} with an intercept.\n"
        f"Its CADF statistic is {_signed_short(result.cadf.t)}, past the 95 percent bar "
        "of −3.359.",
    )


def _signed_short(x: float) -> str:
    return f"{x:.4f}".replace("-", "−")


def _statistics_panel(ax, result: EtfCointegration) -> None:
    tested = result.triplet
    nulls = range(len(tested.trace))
    for name, colour, offset in STATISTICS:
        values = getattr(tested, name)
        critical = getattr(tested, f"{name}_critical")
        for i in nulls:
            x = i + offset
            ax.bar(x, values[i], BAR_WIDTH, color=colour, alpha=0.85, lw=0, gid=f"{name}-{i}")
            for column, (level, dash) in enumerate(LEVELS):
                ax.plot(
                    [x - BAR_WIDTH / 2 - 0.03, x + BAR_WIDTH / 2 + 0.03],
                    [critical[i, column]] * 2,
                    color=INK,
                    ls=dash,
                    lw=1.4,
                    gid=f"{name}-{i}-{level}",
                )
    ax.set_xticks(
        [i + offset for i in nulls for _, _, offset in STATISTICS],
        [f"{name}\n{getattr(tested, name)[i]:.3f}" for i in nulls for name, _, _ in STATISTICS],
    )
    for i in nulls:
        ax.text(
            i,
            -0.25,
            f"null r ≤ {i}",
            transform=ax.get_xaxis_transform(),
            ha="center",
            va="top",
            color=INK,
            fontsize=10,
            fontweight="bold",
            gid=f"null-{i}",
        )
    ax.set_xlim(-0.6, len(tested.trace) - 0.4)
    top = max(tested.trace.max(), tested.trace_critical.max())
    ax.set_ylim(0, 1.18 * top)
    ax.set_ylabel("statistic", color=INK, fontsize=10)

    short, bar = tested.eigen[0], tested.eigen_critical[0, 0]
    ax.annotate(
        f"{short:.3f}, short of {bar:.3f},\nits 90 percent bar",
        (STATISTICS[1][2], short),
        xytext=(0.42, 0.78),
        textcoords=ax.transAxes,
        ha="left",
        va="center",
        color=LOST,
        fontsize=9.5,
        fontweight="bold",
        arrowprops={"arrowstyle": "-", "color": LOST, "lw": 1.0},
        gid="eigen-short-label",
    )
    handles = [
        Patch(color=colour, alpha=0.85, lw=0, label=f"{name} statistic")
        for name, colour, _ in STATISTICS
    ] + [
        Line2D([], [], color=INK, ls=dash, lw=1.4, label=f"{level} percent critical value")
        for level, dash in LEVELS
    ]
    ax.legend(handles=handles, loc="upper right", frameon=False, fontsize=9, labelcolor=INK)
    trace_found = tested.relations("trace", 95)
    eigen_found = tested.relations("eigen", 90)
    _heading(
        ax,
        f"The Johansen test on {', '.join(TRIPLET[:-1])} and {TRIPLET[-1]}: each statistic "
        "beside its 90, 95 and 99 percent critical values.\n"
        f"The trace test finds {trace_found} relations at 95 percent. "
        f"The eigen test finds {eigen_found}, even at 90.",
    )


def _returns_panel(ax, days: pd.DatetimeIndex, result: EtfCointegration) -> None:
    cumret = cumulative_return(result)
    spell = longest_spell(cumret)
    depth, _ = calculate_max_dd(cumret)
    _, drawdown, _ = drawdown_path(cumret)
    trough = int(np.argmin(drawdown))

    ax.axvspan(days[spell.first], days[spell.last], color=LOST, alpha=0.12, lw=0, gid="spell")
    ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    ax.plot(days, cumret, color=INK, lw=1.6, gid="cumulative")
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
    for gid, row, colour in (("high", spell.high, INK), ("trough", trough, LOST)):
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
        f"deepest drawdown {_signed(depth)},\n{days[trough].date()}",
        (days[trough], cumret[trough]),
        xytext=(-4, -34),
        textcoords="offset points",
        ha="left",
        color=LOST,
        fontsize=9.5,
        fontweight="bold",
        gid="trough-label",
    )
    span = cumret.max() - cumret.min()
    ax.set_ylim(cumret.min() - 0.12 * span, cumret.max() + 0.24 * span)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.set_ylabel("cumulative return, compounded", color=INK, fontsize=10)
    s = result.strategy
    _heading(
        ax,
        f"Figure 2.7: the first eigenvector traded by the linear rule, over a "
        f"{s.lookback}-day lookback.\n"
        f"APR {s.apr:.6f} and Sharpe ratio {s.sharpe:.4f}, where the book prints "
        f"{BOOK_APR_PERCENT} percent and {BOOK_SHARPE}. Unlevered and before costs.",
    )
    ax.cumret = cumret
    ax.spell = spell
    ax.trough = trough


@_plain_text
def make_cointegration_figure(
    out: Path | None = None,
    sources: tuple[list[VintageEntry], pd.DataFrame] | None = None,
) -> Figure:
    """The two closes, the residual, the triplet's statistics and the strategy's return."""
    members, closes = sources if sources is not None else read_sources()
    result = etf_cointegration(closes)
    days = result.days

    fig = Figure(figsize=(10, 15), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    closes_ax, residual_ax, statistics_ax, returns_ax = fig.subplots(
        4, 1, gridspec_kw={"height_ratios": (1, 1, 1.15, 1.3), "hspace": 0.62}
    )
    for ax in (residual_ax, returns_ax):
        ax.sharex(closes_ax)
    for ax in (closes_ax, residual_ax, statistics_ax, returns_ax):
        _style(ax)

    _closes_panel(closes_ax, closes)
    _residual_panel(residual_ax, closes, result)
    _statistics_panel(statistics_ax, result)
    _returns_panel(returns_ax, days, result)

    closes_ax.set_xlim(days[0], days[-1])
    for ax in (closes_ax, residual_ax, returns_ax):
        ax.xaxis.set_major_locator(YearLocator())
        ax.xaxis.set_major_formatter(DateFormatter("%Y"))
    statistics_ax.tick_params(axis="x", colors=INK)
    statistics_ax.spines["bottom"].set_color(RULE)

    saved = sorted({m.obtained for m in members})
    _title(
        fig,
        "Exploratory: Examples 2.6 to 2.8 redrawn on Chan's own EWA, EWC and IGE closes",
        f"Examples 2.6 to 2.8 of Algorithmic Trading, {days[0].date()} to {days[-1].date()}, "
        f"{len(days):,} trading days, as cointegrationTests.m runs them.\n"
        f"Prices from {SOURCE_FILE}, saved {', '.join(saved)}. The eigenvector is fitted on "
        "the days the strategy trades, so every figure is in-sample.",
    )
    fig.subplots_adjust(left=0.09, right=0.97, top=0.935, bottom=0.07)
    return _save(fig, out, COINTEGRATION_FIGURE)


def main() -> None:
    try:
        make_cointegration_figure()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day is worth nothing at
        # the bottom of a traceback, so it reaches the operator as one line, the
        # way chan.etf_cointegration.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / COINTEGRATION_FIGURE}")


if __name__ == "__main__":
    main()
