"""The figure for ``blog/low-beta-holdout-lessons.md``, Chan's low-beta rule after the book.

That post is on Entry 49 of ``docs/replication-log.md``, which runs the rule
at location 4709 of *Quantitative Trading* on IVV's S&P 500 members from
2008-12. :mod:`chan.low_beta_holdout` prints the verdict and draws nothing, so
this module draws what the post's second lesson compares: the same beta match
on Chan's own file, where it ruined the levered portfolio, and on the later
panel, where it did not. The planning pass on the post's issue set a grid of
two rows and two columns.

1. **The left column** is Chan's file, holding months December 2000 to
   October 2007, read from the committed files through
   :func:`chan.low_beta_leverage.read_sources`, as
   :mod:`chan.low_beta_leverage_figures` reads them.
2. **The right column** is IVV's members, holding months January 2009 to
   April 2026, from :func:`chan.low_beta_holdout.read_holdout`, which needs
   the owner's archive of Alpha Vantage prices.
3. **The top row** is each fifth's mean beta at formation, with the low
   fifth's lowest marked and every formation the skip amendment left out
   plotted at its negative low beta. A muted line marks zero, below which no
   leverage matches the high fifth's beta.
4. **The bottom row** is k on one log axis shared by both columns, with its
   highest marked, each ruined month marked, the worst levered month marked
   where no month is ruined, and the skipped months shaded.

Every value sits at the month it applied to, so a beta or a leverage formed
at t sits at t + 1. Each column's verdict is registered under its amendments,
and every path drawn is exploratory.

:func:`make_low_beta_holdout_figure` takes both columns' ``Portfolios``, so
``tests/test_low_beta_holdout_figures.py`` draws a synthetic right column on
every clone. Only the real right column needs the archive, so the committed
PNG redraws only where the archive is::

    QT_ARCHIVE_DIR=/path/to/archive uv run python -m chan.low_beta_holdout_figures

The price is that CI never sees the real right column drawn, and a reader
cannot redraw it.
"""

from __future__ import annotations

import pandas as pd
from matplotlib.dates import DateFormatter, YearLocator
from matplotlib.figure import Figure
from matplotlib.ticker import FixedLocator, NullLocator, ScalarFormatter

from chan import sp500_panel
from chan.archive import ArchiveRefused, ArchiveUnavailable, read_archive_manifest
from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.equity_seasonals import MonthlyRunRefused
from chan.fund_panel import PanelRefused
from chan.low_beta_holdout import MARKET, HoldoutRefused, read_holdout
from chan.low_beta_leverage import (
    SOURCE_FILE,
    EmptyPortfolio,
    NonPositiveBeta,
    Portfolios,
    UnreadableStandardError,
    build_portfolios,
    read_sources,
    ruined_months,
)
from chan.low_beta_leverage_figures import signed
from chan.paths import FIGURES_DIR
from chan.regime_figure import INK, LOST, MUTED, RULE, SURFACE
from chan.vintage import VintageUnavailable

LOW_BETA_HOLDOUT_FIGURE = "low_beta_holdout.png"

#: The top row's y-axis, shared by both columns. It reaches below the most
#: negative low beta a skipped formation had and above the highest high beta.
BETA_LIMITS = (-0.4, 2.6)

#: The bottom row's log axis, shared by both columns.
LEVERAGE_LIMITS = (1.5, 120.0)
LEVERAGE_TICKS = (2, 5, 10, 20, 50, 100)

#: Where each label's text sits, as a fraction of its panel, chosen by eye on
#: the committed files and the archive run so that no label crosses a line. A
#: rule joins each label to its point.
LABEL_AT = {
    ("chan", "lowest"): (0.22, 0.07),
    ("chan", "highest"): (0.36, 0.95),
    ("chan", "ruined-0"): (0.36, 0.80),
    ("chan", "ruined-1"): (0.36, 0.66),
    ("ivv", "lowest"): (0.42, 0.42),
    ("ivv", "skipped"): (0.12, 0.06),
    ("ivv", "highest"): (0.36, 0.95),
    ("ivv", "worst"): (0.36, 0.80),
    # The real holdout ruins no month, so these two are placed only to be clear
    # of the highest k's label should a redraw ever ruin one.
    ("ivv", "ruined-0"): (0.36, 0.80),
    ("ivv", "ruined-1"): (0.36, 0.66),
}
ARROW = {"arrowstyle": "-", "color": LOST, "lw": 0.8}

#: Each column's heading names its panel, and the year ticks are thinned on
#: the longer span so their labels do not collide.
YEARS = {"chan": 1, "ivv": 2}
NAMES = {"chan": "Chan's file", "ivv": "IVV's members"}


def count(n: int, noun: str) -> str:
    """``n`` and ``noun``, with an s unless ``n`` is 1."""
    return f"{n} {noun}{'' if n == 1 else 's'}"


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


def span(p: Portfolios) -> tuple[pd.Timestamp, pd.Timestamp]:
    """The first and last holding month a column draws, skipped months included."""
    last = max([p.held_to[-1], *(skip.held_to for skip in p.skipped)])
    return p.held_to[0], last


def _dates(ax, p: Portfolios, side: str) -> None:
    ax.set_xlim(*span(p))
    ax.xaxis.set_major_locator(YearLocator(YEARS[side]))
    ax.xaxis.set_major_formatter(DateFormatter("%Y"))


def _shade_skipped(ax, p: Portfolios) -> None:
    """Shade from the first skipped formation to the last skipped holding month."""
    if p.skipped:
        ax.axvspan(
            p.skipped[0].formed,
            p.skipped[-1].held_to,
            color=LOST,
            alpha=0.10,
            lw=0,
            gid="skipped-span",
            label="months skipped, low beta at or below zero",
        )


def _label(ax, side: str, key: str, text: str, xy, color: str, gid: str) -> None:
    ax.annotate(
        text,
        xy,
        xytext=LABEL_AT[(side, key)],
        textcoords="axes fraction",
        ha="left",
        va="center",
        color=color,
        fontsize=9,
        arrowprops={**ARROW, "color": color},
        gid=gid,
    )


def _beta_panel(ax, p: Portfolios, side: str) -> None:
    months = p.low_beta.index
    ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    _shade_skipped(ax, p)
    ax.plot(months, p.high_beta, color=MUTED, lw=1.3, gid="high", label="highest fifth")
    ax.plot(months, p.low_beta, color=INK, lw=1.6, zorder=3, gid="low", label="lowest fifth")
    lowest = p.low_beta.idxmin()
    formed = p.formed[months.get_loc(lowest)]
    ax.plot([lowest], [p.low_beta.loc[lowest]], "o", color=LOST, ms=5, zorder=4, gid="lowest")
    _label(
        ax,
        side,
        "lowest",
        f"lowest kept, {p.low_beta.loc[lowest]:.4f}, formed {formed.date()}",
        (lowest, p.low_beta.loc[lowest]),
        LOST,
        "lowest-label",
    )
    if p.skipped:
        ax.plot(
            [skip.held_to for skip in p.skipped],
            [skip.low_beta for skip in p.skipped],
            "o",
            mfc="none",
            mec=LOST,
            mew=1.3,
            ms=5,
            zorder=4,
            clip_on=False,
            gid="skipped",
        )
        first, last = p.skipped[0], p.skipped[-1]
        _label(
            ax,
            side,
            "skipped",
            f"{len(p.skipped)} skipped, formed {first.formed.date()} to {last.formed.date()}, "
            f"low fifth's beta {signed(first.low_beta)} to {signed(last.low_beta)}",
            (last.held_to, last.low_beta),
            LOST,
            "skipped-label",
        )
    _dates(ax, p, side)
    ax.set_ylim(*BETA_LIMITS)
    n = len(p.skipped)
    skipped = f", and {count(n, 'formation')} at or below zero {'is' if n == 1 else 'are'} skipped"
    skipped = skipped if n else ""
    _heading(
        ax,
        f"{NAMES[side]}: each fifth's mean beta at formation.\nThe low fifth's fell to "
        f"{p.low_beta.min():.4f}{skipped}.",
    )


def _leverage_panel(ax, p: Portfolios, side: str) -> None:
    months = p.leverage.index
    _shade_skipped(ax, p)
    ax.plot(months, p.leverage, color=INK, lw=1.6, zorder=3, gid="k", label="k, high beta over low")
    highest = p.leverage.idxmax()
    formed = p.formed[months.get_loc(highest)]
    ax.plot([highest], [p.leverage.loc[highest]], "o", color=INK, ms=5, zorder=4, gid="highest")
    _label(
        ax,
        side,
        "highest",
        f"highest, {p.leverage.loc[highest]:.4f}, formed {formed.date()}",
        (highest, p.leverage.loc[highest]),
        INK,
        "highest-label",
    )
    ruined = ruined_months(p)
    if ruined:
        ax.plot(
            [r.held_to for r in ruined],
            [r.leverage for r in ruined],
            "o",
            color=LOST,
            ms=6,
            zorder=4,
            gid="ruined",
        )
        for n, r in enumerate(ruined[:2]):
            _label(
                ax,
                side,
                f"ruined-{n}",
                f"ruined {r.held_to.date()}: k {r.leverage:.4f}",
                (r.held_to, r.leverage),
                LOST,
                f"ruined-label-{n}",
            )
        heading = f"{count(len(ruined), 'month')} lost more than the capital."
    else:
        worst = p.levered.idxmin()
        k = p.leverage.loc[worst]
        levered = signed(p.levered.loc[worst])
        ax.plot([worst], [k], "o", color=LOST, ms=6, zorder=4, gid="worst")
        _label(
            ax,
            side,
            "worst",
            f"worst month {worst.date()}: k {k:.4f},\nlevered return {levered}",
            (worst, k),
            LOST,
            "worst-label",
        )
        heading = "No month lost the capital."
    ax.set_yscale("log")
    ax.yaxis.set_major_locator(FixedLocator(LEVERAGE_TICKS))
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.yaxis.set_minor_locator(NullLocator())
    ax.set_ylim(*LEVERAGE_LIMITS)
    _dates(ax, p, side)
    if p.skipped:
        ax.legend(loc="center left", frameon=False, fontsize=9, labelcolor=INK)
    _heading(
        ax,
        f"{NAMES[side]}: k, the leverage that matches the high fifth's beta,\nmean "
        f"{p.leverage.mean():.4f}. {heading}",
    )


def _ivv_note() -> str:
    """The right column's vintages, from the committed manifest, which needs no archive."""
    lines = [e for e in read_archive_manifest() if e.cross_section == sp500_panel.CROSS_SECTION]
    members = sorted({e.download_date for e in lines if e.symbol != MARKET})
    (market,) = [e for e in lines if e.symbol == MARKET]
    return (
        f"Right: IVV's members at each month-end, Alpha Vantage adjusted closes downloaded "
        f"{', '.join(members)}, and SPY's downloaded {market.download_date}, in a private "
        "archive. A holdout."
    )


@_plain_text
def make_low_beta_holdout_figure(
    out=None,
    chan: Portfolios | None = None,
    ivv: Portfolios | None = None,
    sources=None,
) -> Figure:
    """Each fifth's beta and the leverage path, on Chan's file and on IVV's members."""
    sources = sources if sources is not None else read_sources()
    members, closes, spy_entry, spy, bill_entry, bills = sources
    chan = chan if chan is not None else build_portfolios(closes, spy, bills)
    ivv = ivv if ivv is not None else read_holdout().portfolios

    fig = Figure(figsize=(13, 9.6), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    axes = fig.subplots(
        2,
        2,
        sharey="row",
        gridspec_kw={"hspace": 0.42, "wspace": 0.08, "width_ratios": (1, 1.6)},
    )
    for ax in axes.flat:
        _style(ax)
    for column, (side, p) in enumerate((("chan", chan), ("ivv", ivv))):
        _beta_panel(axes[0, column], p, side)
        _leverage_panel(axes[1, column], p, side)
    axes[0, 0].set_ylabel("mean beta at formation", color=INK, fontsize=10)
    axes[1, 0].set_ylabel("leverage, log scale", color=INK, fontsize=10)
    axes[0, 0].legend(loc="center right", frameon=False, fontsize=9, labelcolor=INK)
    for ax in axes[:, 1]:
        ax.tick_params(axis="y", labelleft=False)
        ax.spines["left"].set_color(RULE)

    _title(
        fig,
        "Registered verdicts, exploratory paths: the beta match on Chan's file and after the book",
        f"Quantitative Trading, locations 4684 and 4709. Left: stocks from {SOURCE_FILE}, saved "
        f"{members[0].obtained}, survivors only, and SPY from {spy_entry.path}. Not a holdout.\n"
        f"{_ivv_note()}\nBoth borrow at FRED's TB3MS, downloaded {bill_entry.obtained}. Each "
        "value sits at the month it applied to.\nEach verdict is registered under its "
        "amendments, and every path drawn is exploratory.",
    )
    fig.subplots_adjust(left=0.07, right=0.98, top=0.9, bottom=0.14)
    return _save(fig, out, LOW_BETA_HOLDOUT_FIGURE)


def main() -> None:
    try:
        make_low_beta_holdout_figure()
    except (
        ArchiveUnavailable,
        ArchiveRefused,
        PanelRefused,
        MonthlyRunRefused,
        VintageUnavailable,
        HoldoutRefused,
        NonPositiveBeta,
        EmptyPortfolio,
        UnreadableStandardError,
    ) as refused:
        # A refusal reaches the reader as one line, the way
        # chan.low_beta_holdout.main prints one.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / LOW_BETA_HOLDOUT_FIGURE}")


if __name__ == "__main__":
    main()
