"""The figure for the post on crude oil's calendar spread, *Algorithmic Trading*'s Example 5.4.

:mod:`chan.calendar_spread_reversion` prints Entry 34's figures and draws
nothing, so this module draws what the run does not.
[issue 463](https://github.com/l3a0/quantitative-trading/issues/463) asked for
the post, and its plan set the two panels.

1. **Figure 5.7 redrawn.** S's cumulative compounded return,
   ``cumprod(1 + ret) − 1``, from 2008-01-02 to 2012-08-13, which is the curve
   the book prints. The last 66 rows are shaded, because no pair is held after
   2012-05-08 and each of them returns exactly 0, so the curve's flat end is
   the schedule running out rather than a trade standing still. The last held
   day is marked. Beside it, dashed in a muted colour, is the same schedule
   with every position reversed, whose daily return is minus S's. That is the
   direction location 2471 describes for γ.
2. **The sign the trade rests on.** The held pair's log spread, far minus
   near, against forward-filled γ on each of S's held rows from 2008-01-02.
   Under Example 5.3's model the spread is γ(T1 − T2), so it falls as γ rises.
   Line 107 of the script reverses the long-far position wherever γ's z-score
   is above 0, so the downward slope here means its short sits where γ is
   high. On 841 of the 1,097 held days that is also where the spread sits
   below its own 36-day average, so the trade mostly sells the spread when it
   is low.

The upper panel is still the book's one-panel plot, and the lower one is
what the post adds. Every value comes from :func:`chan.roll_returns.load_strip`
and :func:`chan.calendar_spread_reversion.run_spread`, the run's own path, so
the scale-break guard runs here too::

    uv run python -m chan.calendar_spread_reversion_figures
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter, YearLocator
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter

from chan.calendar_spread_reversion import (
    BOOK_APR_PERCENT,
    BOOK_SHARPE,
    ROOT,
    START,
    CalendarSpreadRun,
    calendar_schedule,
    held_log_spread,
    run_spread,
)
from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, INK, MUTED, RULE, SURFACE
from chan.roll_returns import SOURCE_FILES, Strip, load_strip, roll_returns
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable

CALENDAR_SPREAD_REVERSION_FIGURE = "calendar_spread_reversion.png"


@dataclass(frozen=True)
class HeldRows:
    """S's held rows from its first day: the log spread and filled γ on each."""

    spread: pd.Series
    gamma: pd.Series

    @property
    def correlation(self) -> float:
        return float(np.corrcoef(self.spread, self.gamma)[0, 1])


def cumulative_return(returns: pd.Series) -> pd.Series:
    """``cumprod(1 + ret) − 1`` over the window, the series Figure 5.7 draws."""
    return pd.Series(np.cumprod(1 + returns.to_numpy()) - 1, index=returns.index)


def flat_tail(returns: pd.Series) -> pd.DatetimeIndex:
    """The window's last rows whose return is exactly 0, up to the first that is not."""
    earning = np.flatnonzero(returns.to_numpy() != 0)
    first_flat = int(earning[-1]) + 1 if len(earning) else 0
    return returns.index[first_flat:]


def held_rows(contracts: pd.DataFrame, gamma: pd.Series, start: pd.Timestamp) -> HeldRows:
    """The rows from ``start`` where the unflipped schedule holds a pair and filled γ is finite."""
    spread = held_log_spread(contracts, calendar_schedule(contracts))
    filled = gamma.astype(float).ffill()
    keep = spread.notna().to_numpy() & filled.notna().to_numpy() & (contracts.index >= start)
    return HeldRows(spread=spread[keep], gamma=filled[keep])


def signed(value: float, places: int = 2) -> str:
    """``value`` to ``places`` decimals with a true minus sign, as the post prints it."""
    return f"{value:.{places}f}".replace("-", "−")


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


def _returns_panel(ax, s: CalendarSpreadRun) -> None:
    cumret = cumulative_return(s.returns)
    reversed_ = cumulative_return(-s.returns)
    flat = flat_tail(s.returns)
    ax.axvspan(flat[0], flat[-1], color=RULE, alpha=0.45, lw=0, gid="flat")
    ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    ax.axvline(s.last_held, color=ACCENT, lw=1.0, ls="--", gid="last-held")
    ax.plot(
        cumret.index,
        cumret,
        color=INK,
        lw=1.8,
        zorder=3,
        gid="cumulative",
        label=f"the script's rule, ending at {signed(100 * cumret.iloc[-1])} percent",
    )
    ax.plot(
        reversed_.index,
        reversed_,
        color=MUTED,
        lw=1.4,
        ls="--",
        gid="reversed",
        label=f"every position reversed, ending at {signed(100 * reversed_.iloc[-1])} percent",
    )
    ax.annotate(
        f"last pair held on {s.last_held.date()}",
        (s.last_held, cumret.loc[s.last_held]),
        xytext=(-10, -34),
        textcoords="offset points",
        ha="right",
        color=ACCENT,
        fontsize=9.5,
        gid="last-held-label",
    )
    ax.set_xlim(cumret.index[0], cumret.index[-1])
    ax.xaxis.set_major_locator(YearLocator())
    ax.xaxis.set_major_formatter(DateFormatter("%Y"))
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.set_ylabel("cumulative return, compounded", color=INK, fontsize=10)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK)
    _heading(
        ax,
        f"Figure 5.7: the script's cumulative return, {cumret.index[0].date()} to "
        f"{cumret.index[-1].date()}. APR {s.apr:.6f} and Sharpe ratio {s.sharpe:.6f},\n"
        f"where the book prints {BOOK_APR_PERCENT} percent and {BOOK_SHARPE}. Shaded: the last "
        f"{len(flat)} days, {flat[0].date()} to {flat[-1].date()}, which earn nothing.",
    )


def _scatter_panel(ax, held: HeldRows) -> None:
    ax.scatter(
        held.gamma,
        held.spread,
        s=7,
        color=INK,
        alpha=0.55,
        lw=0,
        gid="held",
    )
    ax.axhline(0, color=RULE, lw=0.9, gid="zero")
    ax.axvline(0, color=RULE, lw=0.9, gid="gamma-zero")
    ax.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.set_xlabel("γ, the roll return a year", color=INK, fontsize=10)
    ax.set_ylabel("log(far) − log(near)", color=INK, fontsize=10)
    _heading(
        ax,
        f"The held pair's log spread against γ on the {len(held.spread):,} days a pair is held "
        f"from {held.spread.index[0].date()}, correlation {signed(held.correlation, 6)}.\n"
        "The spread falls as γ rises, so reversing where γ's z-score is above 0 mostly sells "
        "the spread when it is low.",
    )


@_plain_text
def make_calendar_spread_reversion_figure(
    out: Path | None = None,
    strip: Strip | None = None,
) -> Figure:
    """Figure 5.7 with its reversal beside it, and the held spread against γ."""
    strip = strip if strip is not None else load_strip(ROOT)
    gamma = roll_returns(strip.contracts)
    s = run_spread(strip.contracts, gamma, start=START)

    fig = Figure(figsize=(10, 11), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    returns_ax, scatter_ax = fig.subplots(2, 1, gridspec_kw={"hspace": 0.34})
    for ax in (returns_ax, scatter_ax):
        _style(ax)
    _returns_panel(returns_ax, s)
    _scatter_panel(scatter_ax, held_rows(strip.contracts, gamma, START))

    saved = sorted({m.obtained for m in strip.members})
    _title(
        fig,
        "Exploratory: Example 5.4's calendar spread on crude oil, and the direction it trades",
        f"Algorithmic Trading, locations 2461 and 2471. Contracts from {SOURCE_FILES[ROOT]}, "
        f"saved {', '.join(saved)}.\nThe 2008 to 2012 window is the one Chan chose, and no "
        "cost is charged.",
    )
    fig.subplots_adjust(left=0.1, right=0.97, top=0.9, bottom=0.09)
    return _save(fig, out, CALENDAR_SPREAD_REVERSION_FIGURE)


def main() -> None:
    try:
        make_calendar_spread_reversion_figure()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day reaches the reader
        # as one line, the way chan.calendar_spread_reversion.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / CALENDAR_SPREAD_REVERSION_FIGURE}")


if __name__ == "__main__":
    main()
