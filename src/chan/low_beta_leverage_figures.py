"""The figure for ``blog/levered-low-beta-lessons.md``, *Quantitative Trading* at location 4709.

That post is on Chan's rule that a levered low-beta portfolio out-compounds an
unlevered high-beta one. :mod:`chan.low_beta_leverage` prints Entry 45's
verdict and draws nothing, so this module draws what the run does not.
[Issue 528](https://github.com/l3a0/quantitative-trading/issues/528) asked for
the post, and its plan set the three panels. All three share one axis of
holding months, so each value sits at the month it applied to. The leverage
formed 2001-04-30, for example, sits at 2001-05-31.

1. **Each fifth's mean beta at formation**, the low fifth in ink and the high
   fifth muted, with the low fifth's lowest marked.
2. **k on a log axis**, with its highest marked, each ruined month marked
   with its k and levered return, and a dashed line at the low fifth's
   full-sample Kelly leverage, which looks ahead.
3. **The low fifth's monthly return against its ruin line**,
   :func:`chan.low_beta_leverage.ruin_line`, with the months at or below it
   marked. The y-axis stops at :data:`RETURN_LIMITS`, so the line leaves the
   panel once it falls below the lower limit.

The ruined months carry the verdict, registered under an amendment the owner
made after June 2001 was seen. Every path drawn is exploratory, and the ruin
line and the Kelly line were added after the run.

Every value comes from :func:`chan.low_beta_leverage.read_sources` and
:func:`chan.low_beta_leverage.build_portfolios`, the run's own path::

    uv run python -m chan.low_beta_leverage_figures
"""

from __future__ import annotations

import pandas as pd
from matplotlib.dates import DateFormatter, YearLocator
from matplotlib.figure import Figure
from matplotlib.ticker import FixedLocator, MultipleLocator, NullLocator, ScalarFormatter

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.low_beta_leverage import (
    SOURCE_FILE,
    Portfolios,
    build_portfolios,
    kelly,
    read_sources,
    ruin_line,
    ruined_months,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import INK, LOST, MUTED, SURFACE
from chan.vintage import VintageUnavailable

LOW_BETA_LEVERAGE_FIGURE = "low_beta_leverage.png"

#: The third panel's y-axis, wide enough for every month the low fifth held
#: and narrow enough that the months near the ruin line can be read.
RETURN_LIMITS = (-0.10, 0.12)

#: The leverages the log axis labels.
LEVERAGE_TICKS = (2, 5, 10, 20, 50, 100)

#: Where each marked point's label sits, in data coordinates, chosen by eye on
#: the committed vintages so that no label crosses a line. A rule joins each
#: label to its point.
LABEL_AT = {
    "lowest": (pd.Timestamp("2002-10-01"), 0.10),
    "highest": (pd.Timestamp("2001-09-15"), 92.0),
    "ruined-0": (pd.Timestamp("2002-01-01"), 45.0),
    "ruined-1": (pd.Timestamp("2002-01-01"), 24.0),
    "below-0": (pd.Timestamp("2003-04-01"), -0.085),
    "below-1": (pd.Timestamp("2003-04-01"), -0.055),
}
ARROW = {"arrowstyle": "-", "color": LOST, "lw": 0.8}


def signed(value: float, places: int = 4) -> str:
    """``value`` to ``places`` decimals with a true minus sign, as the post prints it."""
    return f"{value:.{places}f}".replace("-", "−")


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


def _dates(ax, months: pd.DatetimeIndex) -> None:
    ax.set_xlim(months[0], months[-1])
    ax.xaxis.set_major_locator(YearLocator())
    ax.xaxis.set_major_formatter(DateFormatter("%Y"))


def _beta_panel(ax, p: Portfolios) -> None:
    months = p.low_beta.index
    ax.plot(months, p.high_beta, color=MUTED, lw=1.4, gid="high", label="highest fifth")
    ax.plot(months, p.low_beta, color=INK, lw=1.8, zorder=3, gid="low", label="lowest fifth")
    lowest = p.low_beta.idxmin()
    formed = p.formed[months.get_loc(lowest)]
    ax.plot([lowest], [p.low_beta.loc[lowest]], "o", color=LOST, ms=5, zorder=4, gid="lowest")
    ax.annotate(
        f"{p.low_beta.loc[lowest]:.4f}, formed {formed.date()}",
        (lowest, p.low_beta.loc[lowest]),
        xytext=LABEL_AT["lowest"],
        textcoords="data",
        ha="left",
        va="center",
        color=LOST,
        fontsize=9,
        arrowprops=ARROW,
        gid="lowest-label",
    )
    _dates(ax, months)
    ax.set_ylim(0, 2.2)
    ax.set_ylabel("mean beta at formation", color=INK, fontsize=10)
    ax.legend(loc="center right", frameon=False, fontsize=9.5, labelcolor=INK)
    _heading(
        ax,
        "Each fifth's mean beta at formation, at the month it was held. The low fifth's fell "
        f"to {p.low_beta.min():.4f},\nwhile the high fifth's stayed between "
        f"{p.high_beta.min():.4f} and {p.high_beta.max():.4f}.",
    )


def _leverage_panel(ax, p: Portfolios) -> None:
    months = p.leverage.index
    reading = kelly(p)
    ax.axhline(
        reading.leverage,
        color=MUTED,
        lw=1.1,
        ls="--",
        gid="kelly",
        label=f"full-sample Kelly, look-ahead, {reading.leverage:.4f}",
    )
    ax.plot(months, p.leverage, color=INK, lw=1.8, zorder=3, gid="k", label="k, high beta over low")
    highest = p.leverage.idxmax()
    ax.annotate(
        f"highest, {p.leverage.loc[highest]:.4f}",
        (highest, p.leverage.loc[highest]),
        xytext=LABEL_AT["highest"],
        textcoords="data",
        ha="left",
        va="center",
        color=INK,
        fontsize=9,
        arrowprops={**ARROW, "color": INK},
        gid="highest-label",
    )
    ruined = ruined_months(p)
    ax.plot(
        [r.held_to for r in ruined],
        [r.leverage for r in ruined],
        "o",
        color=LOST,
        ms=6,
        zorder=4,
        gid="ruined",
    )
    for n, r in enumerate(ruined):
        ax.annotate(
            f"ruined {r.held_to.date()}: k {r.leverage:.4f},\nlevered return {signed(r.levered)}",
            (r.held_to, r.leverage),
            xytext=LABEL_AT[f"ruined-{n}"],
            textcoords="data",
            ha="left",
            va="center",
            color=LOST,
            fontsize=9,
            arrowprops=ARROW,
            gid=f"ruined-label-{n}",
        )
    ax.set_yscale("log")
    ax.yaxis.set_major_locator(FixedLocator(LEVERAGE_TICKS))
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.yaxis.set_minor_locator(NullLocator())
    ax.set_ylim(1.5, 120)
    _dates(ax, months)
    ax.set_ylabel("leverage, log scale", color=INK, fontsize=10)
    ax.legend(loc="upper right", frameon=False, fontsize=9.5, labelcolor=INK)
    _heading(
        ax,
        f"k, the leverage that matches the high fifth's beta, mean {p.leverage.mean():.4f}. "
        f"{len(ruined)} months lost more\nthan the capital, and the Kelly line, added after "
        "the run, looks ahead and decides nothing.",
    )


def _ruin_panel(ax, p: Portfolios) -> None:
    months = p.low.index
    line = ruin_line(p.rf, p.leverage)
    ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    ax.plot(
        months,
        line,
        color=LOST,
        lw=1.4,
        ls="--",
        gid="ruin-line",
        label="ruin line, rf − (1 + rf) / k",
    )
    ax.plot(
        months, p.low, color=INK, lw=1.3, zorder=3, gid="low", label="low fifth's monthly return"
    )
    below = p.low[p.low <= line]
    ax.plot(below.index, below, "o", color=LOST, ms=6, zorder=4, gid="below")
    for n, held_to in enumerate(below.index):
        ax.annotate(
            f"{held_to.date()}: {signed(p.low.loc[held_to])}\nagainst a line at "
            f"{signed(line.loc[held_to])}",
            (held_to, p.low.loc[held_to]),
            xytext=LABEL_AT[f"below-{n}"],
            textcoords="data",
            ha="left",
            va="center",
            color=LOST,
            fontsize=9,
            arrowprops=ARROW,
            gid=f"below-label-{n}",
        )
    _dates(ax, months)
    ax.set_ylim(*RETURN_LIMITS)
    ax.yaxis.set_major_locator(MultipleLocator(0.04))
    ax.yaxis.set_major_formatter(lambda y, _pos: signed(y, 2))
    ax.set_ylabel("monthly return", color=INK, fontsize=10)
    ax.legend(loc="upper right", frameon=False, fontsize=9.5, labelcolor=INK)
    gone = line[line < RETURN_LIMITS[0]].index[0]
    _heading(
        ax,
        "The low fifth's monthly return against the return that would ruin the levered month. "
        f"The line\nleaves the panel from {gone.date()} on, and {len(below)} months fall at or "
        "below it.",
    )


@_plain_text
def make_low_beta_leverage_figure(
    out=None, portfolios: Portfolios | None = None, sources=None
) -> Figure:
    """Each fifth's beta, the leverage path, and the low fifth's return against its ruin line."""
    sources = sources if sources is not None else read_sources()
    members, closes, spy_entry, spy, bill_entry, bills = sources
    p = portfolios if portfolios is not None else build_portfolios(closes, spy, bills)

    fig = Figure(figsize=(10, 13), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    beta_ax, leverage_ax, ruin_ax = fig.subplots(3, 1, gridspec_kw={"hspace": 0.42})
    for ax in (beta_ax, leverage_ax, ruin_ax):
        _style(ax)
    _beta_panel(beta_ax, p)
    _leverage_panel(leverage_ax, p)
    _ruin_panel(ruin_ax, p)

    _title(
        fig,
        "Registered verdict, exploratory path: Chan's low-beta fifth levered to the high "
        "fifth's beta",
        f"Quantitative Trading, Kindle edition, pp. 189 to 191. Stocks from {SOURCE_FILE}, saved "
        f"{members[0].obtained}, survivors only.\nSPY from {spy_entry.path}, saved "
        f"{spy_entry.obtained}, and FRED's TB3MS, downloaded {bill_entry.obtained}. "
        "Not a holdout.\nThe ruined months carry the verdict, registered under an amendment "
        "made after June 2001 was seen.\nThe paths are exploratory, and the ruin and Kelly "
        "lines were added after the run.",
    )
    fig.subplots_adjust(left=0.1, right=0.97, top=0.93, bottom=0.11)
    return _save(fig, out, LOW_BETA_LEVERAGE_FIGURE)


def main() -> None:
    try:
        make_low_beta_leverage_figure()
    except VintageUnavailable as refused:
        # A refusal that names the source reaches the reader as one line, the
        # way chan.low_beta_leverage.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / LOW_BETA_LEVERAGE_FIGURE}")


if __name__ == "__main__":
    main()
