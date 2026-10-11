"""The figure for ``blog/gld-gc-lessons.md``, *Algorithmic Trading* at locations 2718 and 2730.

That post is on holding GLD long and gold futures short. :mod:`chan.gld_gc`
prints Entry 38's figures and draws nothing, so this module draws what the run
does not. [issue 493](https://github.com/l3a0/quantitative-trading/issues/493)
asked for the post, and its plan set the two panels.

1. **The return beside its financing.** Three cumulative curves over the 752
   kept days, each 0 on 2007-08-03: S's ``cumprod(1 + ret) − 1``, three-month
   bills accrued at each month's TB3MS over 252 through
   :func:`chan.gld_gc.bill_accrual`, and the script's 2 percent a year,
   compounded. The longest stretch below a high, the 91 days, is shaded, and
   the deepest drawdown's trough is marked.
2. **The daily change in log(GC / GLD) on both GC series.** The 16:00 series
   the script reads, over the OHLC save's continuous GC, with dashed lines at
   plus and minus :data:`chan.gld_gc.STEP`. Both come through
   :func:`chan.gld_gc.log_ratio_changes`, the computation
   :func:`chan.gld_gc.ratio_steps` summarises.

Every value comes from :func:`chan.gld_gc.read_sources`,
:func:`chan.gld_gc.gld_gc` and :func:`chan.gld_gc.identity`, the run's own
path, so the scale-break guard runs here too::

    uv run python -m chan.gld_gc_figures
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter, YearLocator
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter

from chan import bill_rates
from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.gld_gc import (
    GC_SOURCE_FILE,
    GLD_SOURCE_FILE,
    RISK_FREE_RATE,
    STEP,
    GldGc,
    Sources,
    bill_accrual,
    gld_gc,
    identity,
    log_ratio_changes,
    read_ohlc_gc,
    read_sources,
)
from chan.matlab_helpers import drawdown_path
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, INK, LOST, MUTED, RULE, SURFACE
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable

GLD_GC_FIGURE = "gld_gc.png"

#: The curves the first panel draws, in the order the legend lists them.
CURVES = ("S", "bills", "2 percent")
#: How each curve is drawn: colour, width, style, and what the legend calls it.
CURVE_STYLE = {
    "S": (INK, 1.8, "-", "S, long GLD and short GC"),
    "bills": (ACCENT, 1.4, "-", "three-month bills, each month's TB3MS over 252 a day"),
    "2 percent": (MUTED, 1.2, "--", "the script's 2 percent a year, compounded"),
}


def cumulative_return(daily: pd.Series) -> pd.Series:
    """``cumprod(1 + ret) − 1``, the series ``calculateMaxDD`` reads."""
    return pd.Series(np.cumprod(1 + daily.to_numpy()) - 1, index=daily.index)


def financing_curves(result: GldGc, data_dir: Path | None = None) -> dict[str, pd.Series]:
    """S and the two financing rates, each compounded from 0 on the first kept day.

    The bills earn each month's TB3MS over 252 a day, and the script's rate
    earns :data:`chan.gld_gc.RISK_FREE_RATE`. Both start from a first row of
    0, as S's return does, so all three curves begin at 0 together.
    """
    two_percent = np.full(len(result.days), RISK_FREE_RATE)
    two_percent[:1] = 0.0
    daily = {
        "S": pd.Series(result.daily, index=result.days),
        "bills": bill_accrual(result.days, data_dir=data_dir),
        "2 percent": pd.Series(two_percent, index=result.days),
    }
    return {key: cumulative_return(daily[key]) for key in CURVES}


def longest_stretch(cumret: pd.Series) -> tuple[pd.Timestamp, pd.Timestamp]:
    """The first and last day of the longest stretch below a high, counted as ``calculateMaxDD``."""
    _, _, duration = drawdown_path(cumret.to_numpy())
    last = int(np.argmax(duration))
    first = last - int(duration[last]) + 1
    return cumret.index[first], cumret.index[last]


def deepest_trough(cumret: pd.Series) -> tuple[pd.Timestamp, float]:
    """The day of the deepest drawdown and that drawdown, a fraction below zero."""
    _, drawdown, _ = drawdown_path(cumret.to_numpy())
    trough = int(np.argmin(drawdown))
    return cumret.index[trough], float(drawdown[trough])


def signed(value: float, places: int = 2) -> str:
    """``value`` to ``places`` decimals with a true minus sign, as the post prints it."""
    return f"{value:.{places}f}".replace("-", "−")


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


def _dates(ax, days: pd.DatetimeIndex) -> None:
    ax.set_xlim(days[0], days[-1])
    ax.xaxis.set_major_locator(YearLocator())
    ax.xaxis.set_major_formatter(DateFormatter("%Y"))


def _financing_panel(ax, result: GldGc, curves: dict[str, pd.Series]) -> None:
    s = curves["S"]
    first, last = longest_stretch(s)
    trough, depth = deepest_trough(s)
    _, drawdown, _ = drawdown_path(s.to_numpy())
    stretch_low = float(drawdown[s.index.get_loc(first) : s.index.get_loc(last) + 1].min())
    ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    ax.axvspan(first, last, color=RULE, alpha=0.45, lw=0, gid="longest-stretch")
    ax.annotate(
        f"{len(s.loc[first:last])} days below a high,\n{first.date()} to {last.date()},\n"
        f"at worst {signed(100 * stretch_low)} percent",
        (last, 0.012),
        xytext=(-6, 0),
        textcoords="offset points",
        ha="right",
        color=MUTED,
        fontsize=9,
        gid="longest-stretch-label",
    )
    for key in CURVES:
        color, width, style, name = CURVE_STYLE[key]
        curve = curves[key]
        ax.plot(
            curve.index,
            curve,
            color=color,
            lw=width,
            ls=style,
            zorder=3 if key == "S" else 2,
            gid=key,
            label=f"{name}, ending at {signed(100 * curve.iloc[-1])} percent",
        )
    ax.plot([trough], [s.loc[trough]], "o", color=LOST, ms=5, zorder=4, gid="trough")
    ax.annotate(
        f"the deepest drawdown, {signed(100 * depth)} percent, on {trough.date()}",
        (trough, s.loc[trough]),
        xytext=(8, -10),
        textcoords="offset points",
        ha="left",
        color=LOST,
        fontsize=9,
        gid="trough-label",
    )
    _dates(ax, result.days)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.set_ylabel("cumulative return, compounded", color=INK, fontsize=10)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK)
    above = s.index[(s > curves["2 percent"]).to_numpy()]
    _heading(
        ax,
        f"S's cumulative return beside two rates of financing, {result.days[0].date()} to "
        f"{result.days[-1].date()}.\nS last stands above the script's 2 percent a year on "
        f"{above[-1].date()}, and ends above the bills.",
    )


def _ratio_panel(ax, sources: Sources, result: GldGc, ohlc: pd.Series) -> None:
    at_1600 = log_ratio_changes(sources.gc, sources.gld, result.days)
    shifted = log_ratio_changes(ohlc, sources.gld, result.days)
    found = identity(sources, result)
    ax.plot(
        shifted.index,
        shifted,
        color=MUTED,
        lw=0.8,
        alpha=0.8,
        zorder=2,
        gid="ohlc",
        label=f"the OHLC save's GC, shifted at each roll, {found.ohlc.steps} moves past ±{STEP:g}",
    )
    ax.plot(
        at_1600.index,
        at_1600,
        color=INK,
        lw=0.9,
        zorder=3,
        gid="1600",
        label=f"the 16:00 series the script reads, {found.sampled_at_1600.steps} moves past "
        f"±{STEP:g}",
    )
    for sign, gid in ((1, "step-up"), (-1, "step-down")):
        ax.axhline(sign * STEP, color=ACCENT, lw=1.0, ls="--", gid=gid)
    largest = at_1600.abs().idxmax()
    ax.annotate(
        f"the 16:00 series' largest move, {at_1600.loc[largest]:.6f}, on {largest.date()}",
        (largest, at_1600.loc[largest]),
        xytext=(10, 34),
        textcoords="offset points",
        ha="left",
        color=INK,
        fontsize=9,
        arrowprops={"arrowstyle": "-", "color": INK, "lw": 0.8},
        gid="largest-label",
    )
    _dates(ax, result.days)
    ax.set_ylabel("daily change in log(GC / GLD)", color=INK, fontsize=10)
    ax.legend(loc="upper right", frameon=False, fontsize=9.5, labelcolor=INK)
    _heading(
        ax,
        f"The daily change in log(GC / GLD) over {len(at_1600)} days on each GC series. Its "
        f"standard deviation is {found.sampled_at_1600.spread:.6f}\non the 16:00 series and "
        f"{found.ohlc.spread:.6f} on the OHLC save's, whose largest move, "
        f"{found.ohlc.largest:.6f}, falls on {shifted.abs().idxmax().date()}.",
    )


@_plain_text
def make_gld_gc_figure(out: Path | None = None, sources: Sources | None = None) -> Figure:
    """The return beside its financing, and the daily change in log(GC / GLD) on both series."""
    sources = sources if sources is not None else read_sources()
    result = gld_gc(sources)
    _, ohlc = read_ohlc_gc()

    fig = Figure(figsize=(10, 11), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    financing_ax, ratio_ax = fig.subplots(2, 1, gridspec_kw={"hspace": 0.34})
    for ax in (financing_ax, ratio_ax):
        _style(ax)
    _financing_panel(financing_ax, result, financing_curves(result))
    _ratio_panel(ratio_ax, sources, result, ohlc)

    _title(
        fig,
        "Exploratory: long GLD and short gold futures",
        f"Algorithmic Trading, locations 2718 and 2730. GC from {GC_SOURCE_FILE}, saved "
        f"{sources.gc_entry.obtained},\nGLD from {GLD_SOURCE_FILE}, saved "
        f"{sources.gld_entry.obtained}, and FRED's TB3MS, downloaded "
        f"{bill_rates.bill_vintage().obtained}.\nMeasured after the run on the book's window, "
        "with no cost charged.",
    )
    fig.subplots_adjust(left=0.1, right=0.97, top=0.9, bottom=0.11)
    return _save(fig, out, GLD_GC_FIGURE)


def main() -> None:
    try:
        make_gld_gc_figure()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day reaches the reader
        # as one line, the way chan.gld_gc.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / GLD_GC_FIGURE}")


if __name__ == "__main__":
    main()
