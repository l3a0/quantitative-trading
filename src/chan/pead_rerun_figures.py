"""The figure for the post on Example 7.2 rerun on EDGAR's calendar and the archive's prices.

``blog/pead-edgar-rerun-lessons.md`` teaches what Entry 46 of the replication
log found, and [issue 530](https://github.com/l3a0/quantitative-trading/issues/530)
set the figure: one figure, two panels, drawn from committed files only. CI
has no archive, so a panel drawn from the archive's prices would be one no
test there could hold and no reader could redraw. C, D, E1 and E5 are left
out, and the note under the figure says so.

1. **Where the universe effect comes from.** Run A's arithmetic annual return
   built up over the 330 days, split among three groups of its 497 stocks:
   the 441 of U, the 47 of CAL with no checked archive series, and the 9 with
   no checked CIK. Each line is the cumulative sum of its group's daily
   return times 252 over 330, so the three end on A's figure together. Each
   stock trades on its own gap and deviation, so the U line is A_U's run
   exactly, and the other two add up to the universe effect. 2011-08-04, the
   day the stocks outside U add most, is marked.
2. **Trades times their mean.** Each committed run's trades against its mean
   return per trade, with dashed curves of equal arithmetic annual return
   through A and A_CAL. The rule divides each day by a fixed 30, so the return
   is the trades times their mean times 252, over 30 and over the 330 days,
   and a curve of equal return is that identity solved for the mean. Arrows
   run from A to A_U, the universe, and from A_CAL to B1 and B5, the two
   calendars.

Every value comes from :func:`chan.pead_rerun.read_committed` and
:func:`chan.pead_rerun.committed_runs`, the run's own path, so the scale-break
guard runs here too::

    uv run python -m chan.pead_rerun_figures
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter, MonthLocator
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter, PercentFormatter

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.paths import FIGURES_DIR
from chan.pead import DENOMINATOR, FLAG_FILE, PRICE_FILE, TRADING_DAYS, Drift
from chan.pead_rerun import (
    ARCHIVE_RUNS,
    SPECS,
    Sources,
    committed_runs,
    per_trade,
    read_committed,
    trade_returns,
)
from chan.regime_figure import ACCENT, INK, LOST, MUTED, RULE, SURFACE
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable

RERUN_FIGURE = "pead_edgar_rerun.png"

#: The three groups of A's stocks, in the order the first panel draws them.
GROUPS = ("U", "CAL, no checked series", "no checked CIK")
#: How each group is drawn: its colour and what the legend calls it.
GROUP_STYLE = {
    "U": (INK, "the {n} stocks of U, with a checked filer and a checked series"),
    "CAL, no checked series": (ACCENT, "the {n} with a checked filer and no checked series"),
    "no checked CIK": (LOST, "the {n} with no checked filer"),
}

#: The day the stocks outside U add most to A, which the first panel marks.
MARKED_DAY = pd.Timestamp("2011-08-04")

#: The runs the second panel draws, every one that reads only committed files.
POINTS = tuple(spec.name for spec in SPECS if spec.name not in ARCHIVE_RUNS)
#: The runs a curve of equal return passes through.
CURVES = ("A", "A_CAL")
#: Each arrow's start, end and label.
ARROWS = (
    ("A", "A_U", "the universe"),
    ("A_CAL", "B1", "R1"),
    ("A_CAL", "B5", "R5"),
)
#: Where each arrow's label sits: the share of the way along the arrow, the
#: offset in points and the alignment.
ARROW_LABEL_AT = {
    "the universe": (0.85, (10, -8), "left"),
    "R1": (0.5, (0, 7), "center"),
    "R5": (0.5, (0, -14), "center"),
}
#: The span of trades the curves are drawn over.
TRADE_SPAN = (880, 1520)


def group_stocks(sources: Sources) -> dict[str, list[str]]:
    """A's 497 stocks split three ways, each in the order of Chan's files."""
    u, cal = set(sources.universe("U")), set(sources.universe("CAL"))
    stocks = sources.universe("ALL")
    return {
        "U": [s for s in stocks if s in u],
        "CAL, no checked series": [s for s in stocks if s in cal and s not in u],
        "no checked CIK": [s for s in stocks if s not in cal],
    }


def contributions(sources: Sources, drift: Drift) -> dict[str, pd.Series]:
    """Each group's running contribution to ``drift``'s arithmetic annual return.

    The arithmetic annual return is 252 times the mean daily return, so a
    day's return adds itself times 252 over the number of days. A day's
    return is its summed trades over 30, so a group's share of it is its own
    trades over 30.
    """
    stocks = sources.universe("ALL")
    returns = trade_returns(drift, sources.opens[stocks], sources.closes[stocks])
    scale = TRADING_DAYS / (DENOMINATOR * len(drift.days))
    return {
        group: returns[columns].sum(axis=1).cumsum() * scale
        for group, columns in group_stocks(sources).items()
    }


def equal_return(annual: float, trades: np.ndarray, days: int) -> np.ndarray:
    """The mean return per trade that gives ``annual`` at each count of ``trades``."""
    return annual * DENOMINATOR * days / (TRADING_DAYS * np.asarray(trades, dtype=float))


def signed(value: float, places: int = 6) -> str:
    """``value`` to ``places`` decimals with a true minus sign."""
    return f"{value:.{places}f}".replace("-", "−")


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


def _contribution_panel(ax, sources: Sources, drift: Drift) -> None:
    lines = contributions(sources, drift)
    groups = group_stocks(sources)
    days = drift.days
    ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    ax.axvline(MARKED_DAY, color=RULE, lw=1.2, ls="--", zorder=1, gid="marked-day")
    for group in GROUPS:
        color, name = GROUP_STYLE[group]
        line = lines[group]
        ax.plot(
            days,
            line,
            color=color,
            lw=2.0 if group == "U" else 1.6,
            zorder=3,
            gid=group,
            label=f"{name.format(n=len(groups[group]))}, ending at {signed(line.iloc[-1])}",
        )
    i = days.get_loc(MARKED_DAY)
    step = sum(float(lines[g].iloc[i] - lines[g].iloc[i - 1]) for g in GROUPS[1:])
    ax.annotate(
        f"{MARKED_DAY.date()}: the stocks outside U\nadd {signed(step)} on one day",
        (MARKED_DAY, lines["no checked CIK"].iloc[i]),
        xytext=(-12, 34),
        textcoords="offset points",
        ha="right",
        color=LOST,
        fontsize=9,
        arrowprops={"arrowstyle": "-", "color": LOST, "lw": 0.8},
        gid="marked-day-label",
    )
    ax.set_xlim(days[0], days[-1])
    ax.xaxis.set_major_locator(MonthLocator(bymonth=(1, 4, 7, 10)))
    ax.xaxis.set_major_formatter(DateFormatter("%b %Y"))
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.set_ylabel("contribution to the arithmetic annual return", color=INK, fontsize=10)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK)
    outside = sum(float(lines[g].iloc[-1]) for g in GROUPS[1:])
    _heading(
        ax,
        f"Run A's arithmetic annual return, {signed(drift.arithmetic_annual)}, built up over "
        f"its {len(days)} days from three groups of its {len(sources.universe('ALL'))} "
        f"stocks.\nThe {len(groups['CAL, no checked series']) + len(groups['no checked CIK'])} "
        f"stocks outside U add {signed(outside)}, and the U line is run A_U exactly.",
    )


def _per_trade_panel(ax, runs: dict[str, Drift]) -> None:
    days = len(runs["A"].days)
    span = np.linspace(*TRADE_SPAN, 200)
    for name in CURVES:
        annual = runs[name].arithmetic_annual
        curve = equal_return(annual, span, days)
        ax.plot(span, curve, color=MUTED, lw=1.0, ls="--", zorder=1, gid=f"equal-{name}")
        ax.annotate(
            f"{name}'s return, held fixed",
            (span[0], curve[0]),
            xytext=(6, 6),
            textcoords="offset points",
            ha="left",
            color=MUTED,
            fontsize=9,
            gid=f"equal-{name}-label",
        )
    for start, end, label in ARROWS:
        a, b = runs[start], runs[end]
        ax.annotate(
            "",
            (b.trades, per_trade(b)),
            xytext=(a.trades, per_trade(a)),
            arrowprops={
                "arrowstyle": "-|>",
                "color": ACCENT,
                "lw": 1.3,
                "shrinkA": 6,
                "shrinkB": 6,
            },
            gid=f"arrow-{start}-{end}",
        )
        along, offset, align = ARROW_LABEL_AT[label]
        ax.annotate(
            label,
            (
                a.trades + along * (b.trades - a.trades),
                per_trade(a) + along * (per_trade(b) - per_trade(a)),
            ),
            xytext=offset,
            textcoords="offset points",
            ha=align,
            color=ACCENT,
            fontsize=9,
            fontweight="bold",
            gid=f"arrow-{start}-{end}-label",
        )
    offsets = {
        "A": (8, 4, "left"),
        "A_CAL": (-8, -12, "right"),
        "A_PX": (-8, -4, "right"),
        "A_U": (0, -16, "center"),
        "B1": (8, 4, "left"),
        "B5": (-8, -14, "right"),
    }
    for name in POINTS:
        drift = runs[name]
        ax.plot(
            [drift.trades],
            [per_trade(drift)],
            "o",
            ms=7,
            color=INK,
            mec=SURFACE,
            mew=1.5,
            zorder=4,
            gid=f"point-{name}",
        )
        dx, dy, ha = offsets[name]
        ax.annotate(
            f"{name}, {signed(drift.arithmetic_annual)}",
            (drift.trades, per_trade(drift)),
            xytext=(dx, dy),
            textcoords="offset points",
            ha=ha,
            color=INK,
            fontsize=9.5,
            gid=f"point-{name}-label",
        )
    ax.set_xlim(*TRADE_SPAN)
    ax.set_ylim(0.0013, 0.0031)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _pos: f"{x:,.0f}"))
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=2))
    ax.set_xlabel("trades taken over the 330 days", color=INK, fontsize=10)
    ax.set_ylabel("mean return per trade, open to close", color=INK, fontsize=10)
    _heading(
        ax,
        "Each committed run's trades against its mean return per trade, labelled with its "
        "arithmetic annual return.\nEach day is divided by a fixed "
        f"{DENOMINATOR}, so along a dashed curve more trades at a lower mean earn the same.",
    )


@_plain_text
def make_rerun_figure(out: Path | None = None, sources: Sources | None = None) -> Figure:
    """Where A's return comes from, and each committed run's trades against their mean."""
    sources = sources if sources is not None else read_committed()
    runs = committed_runs(sources)

    fig = Figure(figsize=(10, 11), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    contribution_ax, per_trade_ax = fig.subplots(2, 1, gridspec_kw={"hspace": 0.36})
    for ax in (contribution_ax, per_trade_ax):
        _style(ax)
    _contribution_panel(contribution_ax, sources, runs["A"])
    _per_trade_panel(per_trade_ax, runs)

    window = sources.window
    _title(
        fig,
        "Exploratory: post-earnings drift on EDGAR's calendar, the runs on committed files",
        f"Algorithmic Trading, Example 7.2, {window[0].date()} to {window[-1].date()}, on "
        f"{PRICE_FILE} and {FLAG_FILE},\nand Item 2.02 8-Ks as research/filings/earnings/ "
        "recorded them from EDGAR on 2026-10-10. No cost is charged.\n"
        f"{', '.join(ARCHIVE_RUNS[:-1])} and {ARCHIVE_RUNS[-1]} read the owner's archive of "
        "Alpha Vantage prices, so no reader can rerun them, and they are left out.",
    )
    fig.subplots_adjust(left=0.1, right=0.97, top=0.9, bottom=0.12)
    return _save(fig, out, RERUN_FIGURE)


def main() -> None:
    try:
        make_rerun_figure()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source reaches the operator as one line,
        # the way chan.pead_rerun.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / RERUN_FIGURE}")


if __name__ == "__main__":
    main()
