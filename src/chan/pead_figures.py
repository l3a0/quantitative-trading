"""The figure for the post on post-earnings drift, *Algorithmic Trading*'s Example 7.2.

``blog/post-earnings-drift-lessons.md`` teaches what Entry 12 of the
replication log found, and
[issue 284](https://github.com/l3a0/quantitative-trading/issues/284) chose one
figure for it. :func:`make_cumulative_figure` redraws what ``pead.m``'s closing
``plot(cumret)`` draws, which the book prints as Figure 7.2 at location 3024:
the compounded cumulative return over the flag file's 330 days, at one
thirtieth of capital a position, unlevered and before costs. It serves the
post's first lesson, that every printed figure reproduces, and the spell it
marks serves the third, that most days hold nothing.

Two stretches are shaded.

1. The first 89 days, which hold no position because the 90-day moving
   deviation has not filled.
2. The longest spell below the high, which ``calculateMaxDD`` measures as 109
   days without saying where it falls. :func:`longest_spell` finds it under the
   same rules, and the deepest drawdown happens to sit inside it. Nothing in
   ``calculateMaxDD`` makes that so, which is why
   ``tests/test_pead_figures.py`` holds it.

Every value comes from :mod:`chan.pead`, read through
:func:`chan.pead.guarded_drift`, so the figure reads the committed files the
way the run does, scale-break guard included::

    uv run python -m chan.pead_figures
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from matplotlib.dates import DateFormatter, MonthLocator
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.paths import FIGURES_DIR
from chan.pead import (
    DENOMINATOR,
    FLAG_FILE,
    LOOKBACK,
    PRICE_FILE,
    Drift,
    guarded_drift,
)
from chan.regime_figure import INK, LOST, MUTED, RULE, SURFACE
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable

CUMULATIVE_FIGURE = "pead_cumulative_return.png"


def _signed(x: float) -> str:
    """A drawdown as ``pead.m`` prints it, with a true minus sign."""
    return f"{x:f}".replace("-", "−")


def cumulative_return(drift: Drift) -> np.ndarray:
    """``cumprod(1 + ret) − 1``, the series ``pead.m`` plots."""
    return np.cumprod(1 + drift.daily) - 1


@dataclass(frozen=True)
class Spell:
    """The longest stretch below the high, as rows of the 330 days.

    ``high`` is the row the high was set on, ``first`` and ``last`` bound the
    spell, and ``trough`` is its deepest row, where the drawdown is ``depth``.
    """

    high: int
    first: int
    last: int
    trough: int
    depth: float

    @property
    def rows(self) -> int:
        return self.last - self.first + 1


def longest_spell(cumret: np.ndarray) -> Spell:
    """Where ``calculateMaxDD``'s longest duration falls, under its own rules.

    The high starts at zero and the loop on the second row, as
    :func:`chan.matlab_helpers.calculate_max_dd` keeps them, so the spell's
    length is that function's duration. Where two spells tie, the first is
    taken.
    """
    values = np.asarray(cumret, dtype=float)
    high = np.zeros_like(values)
    drawdown = np.zeros_like(values)
    duration = np.zeros(len(values), dtype=int)
    for t in range(1, len(values)):
        high[t] = max(high[t - 1], values[t])
        drawdown[t] = (1 + values[t]) / (1 + high[t]) - 1
        duration[t] = 0 if drawdown[t] == 0 else duration[t - 1] + 1
    last = int(np.argmax(duration))
    first = last - int(duration[last]) + 1
    trough = first + int(np.argmin(drawdown[first : last + 1]))
    return Spell(
        high=first - 1, first=first, last=last, trough=trough, depth=float(drawdown[trough])
    )


@_plain_text
def make_cumulative_figure(out: Path | None = None, drift: Drift | None = None) -> Figure:
    """The 330 days' compounded cumulative return, with the idle start and the spell shaded."""
    drift = drift if drift is not None else guarded_drift()[2]
    days = drift.days
    cumret = cumulative_return(drift)
    spell = longest_spell(cumret)

    fig = Figure(figsize=(10, 5.6), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.subplots()
    _style(ax)

    idle = LOOKBACK - 1
    ax.axvspan(days[0], days[idle - 1], color=RULE, alpha=0.45, lw=0, gid="unfilled")
    ax.axvspan(days[spell.first], days[spell.last], color=LOST, alpha=0.12, lw=0, gid="spell")
    ax.axhline(0, color=MUTED, lw=0.9)
    ax.plot(days, cumret, color=INK, lw=2, gid="cumulative")

    ax.annotate(
        f"no position in the first {idle} days,\nbefore the {LOOKBACK}-day deviation fills",
        (days[idle // 2], 0.0),
        xytext=(0, 14),
        textcoords="offset points",
        ha="center",
        color=MUTED,
        fontsize=9.5,
        gid="unfilled-label",
    )
    ax.annotate(
        f"{spell.rows} days below the high,\n{days[spell.first].date()} to "
        f"{days[spell.last].date()}",
        (days[(spell.first + spell.last) // 2], cumret[spell.high]),
        xytext=(0, 12),
        textcoords="offset points",
        ha="center",
        color=LOST,
        fontsize=9.5,
        fontweight="bold",
        gid="spell-label",
    )
    ax.plot(
        [days[spell.high]],
        [cumret[spell.high]],
        "o",
        ms=7,
        color=INK,
        mec=SURFACE,
        mew=2,
        zorder=3,
        gid="high",
    )
    ax.annotate(
        f"high, {days[spell.high].date()}",
        (days[spell.high], cumret[spell.high]),
        xytext=(-10, 4),
        textcoords="offset points",
        ha="right",
        color=INK,
        fontsize=9.5,
        gid="high-label",
    )
    ax.plot(
        [days[spell.trough]],
        [cumret[spell.trough]],
        "o",
        ms=7,
        color=LOST,
        mec=SURFACE,
        mew=2,
        zorder=3,
        gid="trough",
    )
    ax.annotate(
        f"deepest drawdown {_signed(spell.depth)},\n{days[spell.trough].date()}",
        (days[spell.trough], cumret[spell.trough]),
        xytext=(0, -30),
        textcoords="offset points",
        ha="center",
        color=LOST,
        fontsize=9.5,
        fontweight="bold",
        gid="trough-label",
    )

    ax.set_xlim(days[0], days[-1])
    span = cumret.max() - cumret.min()
    ax.set_ylim(cumret.min() - 0.25 * span, cumret.max() + 0.12 * span)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.xaxis.set_major_locator(MonthLocator(bymonth=(1, 4, 7, 10)))
    ax.xaxis.set_major_formatter(DateFormatter("%b %Y"))
    ax.set_ylabel("cumulative return, compounded", color=INK, fontsize=10.5)
    _title(
        fig,
        "Exploratory: pead.m's cumulative return on Chan's own files, redrawn",
        f"Example 7.2 of Algorithmic Trading, {days[0].date()} to {days[-1].date()}, each day's "
        f"summed return over {DENOMINATOR}, unlevered and before costs.\n"
        f"Prices from {PRICE_FILE} and flags from {FLAG_FILE}.\n"
        "The price file holds only the S&P 500 as it stood on 2012-04-24, "
        "so every stock is a survivor.",
    )
    fig.tight_layout(rect=(0, 0.11, 1, 0.96))
    fig.cumret = cumret
    fig.spell = spell
    return _save(fig, out, CUMULATIVE_FIGURE)


def main() -> None:
    try:
        make_cumulative_figure()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source is worth nothing at the bottom of a
        # traceback, so it reaches the operator as one line, the way
        # chan.pead.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / CUMULATIVE_FIGURE}")


if __name__ == "__main__":
    main()
