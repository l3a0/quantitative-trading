"""The figure for ``blog/vix-filter-lessons.md``, *Algorithmic Trading*'s location 3509.

That post is on the VIX filter, which keeps only the days after VIX closed
above 35 and reruns buy on gap and the opening gap rule on FSTX on them.
:mod:`chan.vix_filter` prints Entry 47's figures and draws nothing, so this
module draws what the run does not.
[issue 537](https://github.com/l3a0/quantitative-trading/issues/537) asked for
the post, and its plan set two panels on one date axis, from FSTX's first
joined day, 2004-07-16, to VIX's last close, 2012-05-08.

1. **VIX and the threshold.** VIX's close on its own calendar, a dashed line
   at 35, the closes above it marked, and the first, highest and last close
   above 35 inside the window labelled.
2. **What each rule earned on its kept days.** Each rule's daily returns
   summed over its kept days, with nothing earned on the other days, which is
   :attr:`chan.vix_filter.Filtered.summed`. Buy on gap, FSTX under the
   script's sign, and FSTX under the sign the text describes. A sum rather
   than a compounded curve, because location 3509's filtered figures are
   arithmetic means, so each curve ends at its 252 · mean times kept / 252.

Both panels shade the span from the first kept day to the last, which holds
every kept day of both rules.

Every value comes from :func:`chan.vix_filter.read_sources` and
:func:`~chan.vix_filter.vix_filters`, the run's own path, so the scale-break
guard runs here too::

    uv run python -m chan.vix_filter_figures
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter, YearLocator, date2num
from matplotlib.figure import Figure

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.opening_gap_figures import signed
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, INK, LOST, MUTED, RULE, SURFACE
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable
from chan.vix_filter import (
    BOOK_BUY_ON_GAP_PERCENT,
    BOOK_BUY_ON_GAP_SHARPE,
    BOOK_FSTX_PERCENT,
    BOOK_FSTX_SHARPE,
    THRESHOLD,
    Filtered,
    Sources,
    VixFilter,
    read_sources,
    runs,
    vix_filters,
)

FIGURE = "vix_filter.png"
#: The shading for the span that holds every kept day, in both panels.
KEPT_SHADE = (RULE, 0.45)
#: The first panel's vertical range, which leaves room above VIX's highest close for its label.
VIX_LIMITS = (0.0, 92.0)
#: The second panel's vertical range, wide enough that the legend sits above every curve.
EARNED_LIMITS = (-0.12, 0.3)


def vix_window(result: VixFilter, vix: pd.Series) -> pd.Series:
    """VIX's closes from FSTX's first joined day to its last, the figure's date axis."""
    days = result.literal.days
    return vix.loc[days[0] : days[-1]]


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


def _shade(ax, kept: pd.DatetimeIndex) -> None:
    """The span from the first kept day to the last, the same in both panels."""
    color, alpha = KEPT_SHADE
    ax.axvspan(
        date2num(kept[0]),
        date2num(kept[-1]),
        color=color,
        alpha=alpha,
        lw=0,
        gid="kept-span",
        label=f"every kept day falls from {kept[0].date()} to {kept[-1].date()}",
    )


def _label(ax, day: pd.Timestamp, value: float, gid: str, text: str, offset) -> None:
    ax.plot([day], [value], "o", color=ACCENT, ms=6, zorder=5, gid=gid)
    ax.annotate(
        f"{text}, {value:.2f} on {day.date()}",
        (day, value),
        xytext=offset,
        textcoords="offset points",
        ha="right" if offset[0] < 0 else "left",
        va="center",
        color=ACCENT,
        fontsize=9,
        arrowprops={"arrowstyle": "-", "color": ACCENT, "lw": 0.8},
        gid=f"{gid}-label",
    )


def _vix_panel(ax, result: VixFilter, vix: pd.Series) -> None:
    window = vix_window(result, vix)
    above = window > THRESHOLD
    _shade(ax, result.buy_on_gap.kept_days)
    ax.plot(window.index, window.to_numpy(), color=INK, lw=1.0, gid="vix", label="VIX's close")
    ax.axhline(
        THRESHOLD,
        color=LOST,
        lw=1.1,
        ls="--",
        gid="threshold",
        label=f"the threshold, {THRESHOLD:g}",
    )
    ax.plot(
        window.index[above],
        window[above].to_numpy(),
        "o",
        color=ACCENT,
        ms=2.2,
        gid="above",
        label=f"a close above {THRESHOLD:g}, on {int(above.sum())} days in "
        f"{len(runs(above.to_numpy()))} runs",
    )
    closes = window[above]
    _label(
        ax, closes.index[0], closes.iloc[0], "first", "first above 35 inside the window", (-12, 26)
    )
    _label(ax, window.idxmax(), window.max(), "highest", "highest", (12, 0))
    _label(ax, closes.index[-1], closes.iloc[-1], "last", "last above 35", (-12, 40))

    ax.set_ylim(*VIX_LIMITS)
    ax.set_ylabel("VIX close", color=INK, fontsize=10)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK)
    _heading(
        ax,
        f"Inside the window, VIX closed above {THRESHOLD:g} only from {closes.index[0].year} to "
        f"{closes.index[-1].year}. A day is kept "
        "when the previous\njoined day closed above the dashed line, so the kept days follow "
        "the marked closes.",
    )


def _curve(ax, filtered: Filtered, gid: str, text: str, **style) -> None:
    summed = filtered.summed
    ax.plot(
        filtered.days,
        summed,
        gid=gid,
        label=f"{text}, {filtered.kept} kept days, ending at {signed(summed[-1], 6)}",
        **style,
    )


def _earned_panel(ax, result: VixFilter) -> None:
    _shade(ax, result.buy_on_gap.kept_days)
    ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    _curve(ax, result.momentum, "momentum", "FSTX, the sign the text describes", color=LOST, lw=1.4)
    _curve(
        ax, result.literal, "literal", "FSTX, the script as written", color=MUTED, lw=1.4, ls="--"
    )
    _curve(ax, result.buy_on_gap, "buy-on-gap", "buy on gap", color=INK, lw=1.7, zorder=3)
    long = result.buy_on_gap
    best = int(np.flatnonzero(long.qualifies)[np.argmax(long.filtered)])
    ax.plot([long.days[best]], [long.summed[best]], "o", color=ACCENT, ms=6, zorder=5, gid="best")
    ax.annotate(
        f"{long.days[best].date()} alone adds {long.daily[best]:.6f}",
        (long.days[best], long.summed[best]),
        xytext=(14, 14),
        textcoords="offset points",
        ha="left",
        va="center",
        color=ACCENT,
        fontsize=9,
        arrowprops={"arrowstyle": "-", "color": ACCENT, "lw": 0.8},
        gid="best-label",
    )

    ax.set_ylim(*EARNED_LIMITS)
    ax.set_ylabel("daily returns summed", color=INK, fontsize=10)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK)
    literal = result.literal
    _heading(
        ax,
        f"What each rule earned on its kept days, summed, and nothing on the others. Buy on gap's "
        f"252 · mean\nis {long.average_annual_return:.6f} and its Sharpe ratio "
        f"{long.sharpe:.6f}, where the book prints {BOOK_BUY_ON_GAP_PERCENT} percent and "
        f"{BOOK_BUY_ON_GAP_SHARPE}. FSTX's are {literal.average_annual_return:.6f}\nand "
        f"{literal.sharpe:.6f}, where it prints {BOOK_FSTX_PERCENT} percent and "
        f"{BOOK_FSTX_SHARPE}. The other sign gives both negated.",
    )


@_plain_text
def make_vix_filter_figure(out: Path | None = None, sources: Sources | None = None) -> Figure:
    """VIX against its threshold, and each rule's returns summed over its kept days."""
    sources = sources if sources is not None else read_sources()
    result = vix_filters(sources)

    fig = Figure(figsize=(10, 10.5), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    vix_ax, earned_ax = fig.subplots(2, 1, sharex=True, gridspec_kw={"hspace": 0.32})
    for ax in (vix_ax, earned_ax):
        _style(ax)
    _vix_panel(vix_ax, result, sources.vix)
    _earned_panel(earned_ax, result)
    days, kept = result.literal.days, result.buy_on_gap.kept_days
    vix_ax.set_xlim(date2num(days[0]), date2num(days[-1]))
    earned_ax.xaxis.set_major_locator(YearLocator())
    earned_ax.xaxis.set_major_formatter(DateFormatter("%Y"))

    _title(
        fig,
        "Exploratory: the VIX filter on buy on gap and on FSTX's opening gap rule",
        f"Algorithmic Trading, Kindle edition, p. 269. VIX saved {sources.vix_member.obtained}, "
        "the stocks "
        f"saved {sources.stock_members[0].obtained}, FSTX saved {sources.fstx_member.obtained}. "
        "No cost charged.\nThe FSTX alignment was chosen after its figures were seen, and "
        f"every kept day falls from {kept[0].year} to {kept[-1].year}.",
    )
    fig.subplots_adjust(left=0.09, right=0.97, top=0.88, bottom=0.09)
    return _save(fig, out, FIGURE)


def main() -> None:
    try:
        make_vix_filter_figure()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day reaches the reader
        # as one line, the way chan.vix_filter.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / FIGURE}")


if __name__ == "__main__":
    main()
