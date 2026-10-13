"""The figure for ``blog/usdcad-holdout-lessons.md``, Example 2.5 on USD/CAD after 2012.

The post teaches what Entry 51 of the replication log found, and
[issue 609](https://github.com/l3a0/quantitative-trading/issues/609) chose one
figure for it, laid out like the old post's chart so its reader knows it.
:func:`make_usdcad_holdout_figure` draws two panels that share the date axis
over the 115 warm-up closes and the 3,791 traded days.

1. The closes with their moving average over the frozen lookback of 115 days,
   and a line on the first traded day. The average fills on the last warm-up
   close, so it covers every traded day.
2. The cumulative P&L of the traded days, with the deepest fall below its
   running maximum shaded, so the claim's one registered number, the final
   sum, sits beside a drawdown that decides nothing.

Everything comes from :func:`chan.usdcad_holdout.read_holdout`, the run's own
path, so its refusals and the scale-break guard run here too. The run keeps
its moving average inside
:func:`chan.usdcad_mean_reversion.linear_mean_reversion`, so the top panel
draws it with the same ``movingAvg`` over the run's lookback. Redraw it with::

    uv run python -m chan.usdcad_holdout_figures
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from matplotlib.dates import DateFormatter, YearLocator
from matplotlib.figure import Figure

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.matlab_helpers import moving_avg
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED, SURFACE
from chan.series import WindowCrossesScaleBreak
from chan.usdcad_holdout import Holdout, HoldoutRefused, read_holdout
from chan.vintage import VintageUnavailable

USDCAD_HOLDOUT_FIGURE = "usdcad_holdout.png"


def moving_average(holdout: Holdout) -> pd.Series:
    """``movingAvg(closes, lookback)`` over the warm-up and the holdout, NaN until it fills."""
    return pd.Series(
        moving_avg(holdout.closes.to_numpy(dtype=float), holdout.lookback),
        index=holdout.closes.index,
    )


def cumulative_pnl(holdout: Holdout) -> pd.Series:
    """The traded days' P&L summed, the series H1 reads at its last day."""
    return holdout.traded.cumsum()


def signed(value: float, places: int = 4) -> str:
    """``value`` to ``places`` decimals with a true minus sign, as the post prints it."""
    return f"{value:.{places}f}".replace("-", "−")


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


@_plain_text
def make_usdcad_holdout_figure(out: Path | None = None, holdout: Holdout | None = None) -> Figure:
    """The closes with their moving average, and the traded days' cumulative P&L."""
    holdout = holdout if holdout is not None else read_holdout()
    days = holdout.closes.index
    first = holdout.tested.index[0]
    average = moving_average(holdout)
    cumulative = cumulative_pnl(holdout)
    drawdown = holdout.drawdown
    high, low = cumulative[drawdown.peak], cumulative[drawdown.trough]

    fig = Figure(figsize=(10, 9), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    close_ax, pnl_ax = fig.subplots(2, 1, sharex=True, gridspec_kw={"height_ratios": (1, 1)})
    for ax in (close_ax, pnl_ax):
        _style(ax)
        ax.axvline(first, color=MUTED, lw=0.9, ls="--", gid="first-traded-day")

    close_ax.plot(days, holdout.closes, color=INK, lw=0.7, gid="closes", label="daily close")
    close_ax.plot(
        days,
        average,
        color=ACCENT,
        lw=1.6,
        gid="moving-average",
        label=f"{holdout.lookback}-day moving average",
    )
    close_ax.set_ylabel("Canadian dollars per US dollar", color=INK, fontsize=10)
    close_ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK)
    _heading(
        close_ax,
        f"The closes of USD.CAD and their {holdout.lookback}-day moving average, the lookback "
        "frozen from Chan's 2007 to 2012 closes.\nThe dashed line is the first traded day, "
        f"{first.date()}. The {len(holdout.warm_up)} closes before it only fill the window.\n"
        f"The half-life of the traded days' closes is {holdout.half_life:.1f} days.",
    )

    pnl_ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    pnl_ax.axvspan(drawdown.peak, drawdown.trough, color=LOST, alpha=0.12, lw=0, gid="drawdown")
    pnl_ax.plot(cumulative.index, cumulative, color=GOOD, lw=1.2, gid="pnl")
    pnl_ax.plot([drawdown.peak], [high], "o", color=INK, ms=4.5, gid="peak")
    pnl_ax.plot([drawdown.trough], [low], "o", color=LOST, ms=4.5, gid="trough")
    pnl_ax.set_ylabel("cumulative P&L, summed", color=INK, fontsize=10)
    _heading(
        pnl_ax,
        f"The cumulative P&L over {len(holdout.traded):,} traded days, ending at "
        f"{signed(holdout.total_pnl)}. Unlevered and before costs.\nThe shaded fall runs from "
        f"{signed(high)} on {drawdown.peak.date()} to {signed(low)} on "
        f"{drawdown.trough.date()}, {signed(drawdown.depth)} deep.",
    )
    pnl_ax.set_xlim(days[0], days[-1])
    pnl_ax.xaxis.set_major_locator(YearLocator(2))
    pnl_ax.xaxis.set_major_formatter(DateFormatter("%Y"))

    _title(
        fig,
        "Registered: Example 2.5's linear rule on USD.CAD after Chan's sample",
        f"Alpha Vantage FX_DAILY closes, {days[0].date()} to {days[-1].date()}, from "
        f"{holdout.entry.path}.\nThe registered claim is the sign of the final P&L, "
        "predicted before any of these closes was read.\nThe curve, the fall and the "
        "half-life are exploratory.",
    )
    fig.tight_layout(rect=(0, 0.075, 1, 0.97))
    return _save(fig, out, USDCAD_HOLDOUT_FIGURE)


def main() -> None:
    try:
        make_usdcad_holdout_figure()
    except (VintageUnavailable, HoldoutRefused, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day is worth nothing at
        # the bottom of a traceback, so it reaches the operator as one line, the
        # way chan.usdcad_mean_reversion_figures.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / USDCAD_HOLDOUT_FIGURE}")


if __name__ == "__main__":
    main()
