"""The figure for ``blog/monte-carlo-leverage-lessons.md``, *Algorithmic Trading*'s Chapter 8.

That post is on choosing a leverage for Example 5.1's AUD.CAD returns three
ways: by Monte Carlo, by the historical growth rate, and with constant
proportion portfolio insurance (CPPI). :mod:`chan.monte_carlo_leverage` prints
Entry 43's figures and draws nothing, so this module draws what the run does
not. [issue 515](https://github.com/l3a0/quantitative-trading/issues/515)
asked for the post, and its plan set the two panels. Both read the declared
seed's draws only.

1. **Figure 8.2 redrawn, with the evidence on 18.4.** The growth rate
   ``g(f)``, the mean of ``log(1 + f·R)``, against the leverage ``f`` from 0
   to 27, on the declared seed's 100,000 draws in ink and on the 612 saved
   returns, muted. The draws' curve stops at their ruin leverage, where one
   draw loses everything. Their uncapped optimum is marked, and so is the
   script's answer at its cap of 20. The saved returns' optimum and their
   Kelly leverage are marked, the Kelly range that Example 5.1's printed
   Sharpe ratio and APR allow is shaded, and the book's 18.4, 19 and 19.2
   stand on the axis.
2. **Two CPPI forms against the floor.** The account's drawdown over the
   100,000 draws, for Box 8.6's loop and for the scheme location 3426
   describes, beside the full account at ``f·D``, with a line at −0.5. A
   hundred thousand daily values are too dense to read as a line, so each
   step is the deepest drawdown in its 1,000 days. The deepest day, the first
   day below −0.5 and the days below it are read from the daily values and
   named in the legend.

No panel reads the 200 further seeds. Row 3's band rule was chosen after
those seeds were seen, and a picture built around one band would look like an
endorsement of that rule rather than show one of two.

Every value comes from :mod:`chan.monte_carlo_leverage`'s own functions,
:func:`~chan.monte_carlo_leverage.pearson_fit`,
:func:`~chan.monte_carlo_leverage.draws`,
:func:`~chan.monte_carlo_leverage.growth`,
:func:`~chan.monte_carlo_leverage.optimal_leverage`,
:func:`~chan.monte_carlo_leverage.kelly`,
:func:`~chan.monte_carlo_leverage.ruin_leverage`, the two CPPI forms and
:func:`~chan.monte_carlo_leverage.account_drawdowns`, so the figure and the
run read one computation::

    uv run python -m chan.monte_carlo_leverage_figures
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from numpy.typing import NDArray

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.monte_carlo_leverage import (
    BOOK_KELLY,
    BOOK_OPTIMUM,
    BOOK_OPTIMUM_FMINBND,
    CAP,
    DRAWS,
    SEED,
    D,
    account_drawdowns,
    cppi_as_described,
    cppi_as_scripted,
    draws,
    growth,
    implied_kelly_band,
    kelly,
    optimal_leverage,
    pearson_fit,
    read_returns,
    ruin_leverage,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED, SURFACE
from chan.vintage import VintageEntry, VintageUnavailable

FIGURE = "monte_carlo_leverage.png"
#: Figure 8.2 runs from f = 0 to 23. This runs to 27, so the Kelly range shows whole.
LEVERAGE_MAX = 27.0
#: Points on each growth curve.
CURVE_POINTS = 541
#: The drawdown floor location 3438 says CPPI keeps, −D.
FLOOR = -D
#: The shading for the Kelly range Example 5.1's printed figures allow.
KELLY_BAND_SHADE = (ACCENT, 0.14)
#: The first panel's vertical range, growth per day, with room above the curves for the legend.
GROWTH_LIMITS = (0.0, 0.0068)
#: The second panel draws the deepest drawdown in each run of this many days,
#: since 100,000 daily values are too dense to read as lines.
BLOCK = 1_000
#: The second panel's vertical range, with room below the curves for the legend.
DRAWDOWN_LIMITS = (-1.2, 0.03)
#: How far up the first panel the book's figures stand, as a share of its height.
BOOK_TICK = 0.16
#: How far up the first panel the cap and the ruin leverage reach, so they stop below the legend.
LINE_TOP = 0.8


@dataclass(frozen=True)
class Drawn:
    """What the figure draws, computed once from the saved returns and the declared seed."""

    entry: VintageEntry
    returns: NDArray[np.float64]
    sim: NDArray[np.float64]
    ruin: float
    uncapped: float
    capped: float
    historical: float
    kelly: float
    scripted: NDArray[np.float64]
    described: NDArray[np.float64]
    full: NDArray[np.float64]


def drawn(saved: tuple[VintageEntry, NDArray[np.float64]] | None = None) -> Drawn:
    """The declared seed's draws, both optima on each series, and the three accounts at ``f``.

    ``f`` is the capped optimum on the draws, the leverage the script's CPPI
    lines read, as in :func:`chan.monte_carlo_leverage.simulate`.
    """
    entry, returns = saved if saved is not None else read_returns()
    _, params = pearson_fit(returns)
    sim = draws(params, SEED)
    capped = optimal_leverage(sim, CAP)
    return Drawn(
        entry=entry,
        returns=returns,
        sim=sim,
        ruin=ruin_leverage(sim),
        uncapped=optimal_leverage(sim),
        capped=capped,
        historical=optimal_leverage(returns),
        kelly=kelly(returns),
        scripted=account_drawdowns(cppi_as_scripted(sim, capped)),
        described=account_drawdowns(cppi_as_described(sim, capped)),
        full=account_drawdowns(capped * D * sim),
    )


def growth_curve(returns: NDArray[np.float64], upper: float) -> tuple[np.ndarray, np.ndarray]:
    """``g(f)`` on :data:`CURVE_POINTS` leverages from 0 up to ``upper``, leaving out ``upper``.

    The draws' curve ends below their ruin leverage, where no real growth
    rate exists, so the end is left out for every curve alike.
    """
    leverages = np.linspace(0.0, upper, CURVE_POINTS, endpoint=False)
    return leverages, np.array([growth(f, returns) for f in leverages])


def first_below(drawdowns: NDArray[np.float64], floor: float = FLOOR) -> int | None:
    """The first day, counted from 1 at the first draw, whose drawdown is below ``floor``."""
    below = np.flatnonzero(drawdowns < floor)
    return int(below[0]) + 1 if below.size else None


def days_below(drawdowns: NDArray[np.float64], floor: float = FLOOR) -> int:
    """How many days the drawdown is strictly below ``floor``. A day exactly on it is not."""
    return int(np.count_nonzero(drawdowns < floor))


def deepest_day(drawdowns: NDArray[np.float64]) -> int:
    """The day, counted from 1, of the deepest drawdown, the first if several tie."""
    return int(np.argmin(drawdowns)) + 1


def signed(value: float, places: int = 6) -> str:
    """``value`` to ``places`` decimals with a true minus sign, as the post prints it."""
    return f"{value:.{places}f}".replace("-", "−")


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


def _thousands(x: float, _pos: object = None) -> str:
    return f"{x:,.0f}"


def _growth_panel(ax, d: Drawn) -> None:
    low, high = implied_kelly_band()
    color, alpha = KELLY_BAND_SHADE
    ax.axvspan(
        low,
        high,
        color=color,
        alpha=alpha,
        lw=0,
        gid="kelly-band",
        label=f"the Kelly range Example 5.1's printed figures allow, {low:.6f} to {high:.6f}",
    )
    x, y = growth_curve(d.returns, LEVERAGE_MAX)
    ax.plot(x, y, color=MUTED, lw=1.5, gid="saved", label=f"Chan's {len(d.returns)} saved returns")
    x, y = growth_curve(d.sim, d.ruin)
    ax.plot(
        x,
        y,
        color=INK,
        lw=1.8,
        zorder=3,
        gid="draws",
        label=f"{DRAWS:,} draws on seed {SEED}, ending at their ruin leverage of {d.ruin:.6f}",
    )
    ax.axvline(d.ruin, ymax=LINE_TOP, color=INK, lw=0.9, ls=":", gid="ruin")
    ax.axvline(
        CAP,
        ymax=LINE_TOP,
        color=MUTED,
        lw=1.1,
        ls="--",
        gid="cap",
        label=f"the script's cap, fminbnd(minusGsim, 0, {CAP:g})",
    )

    marks = (
        ("capped", d.capped, d.sim, "the script's answer on the draws", "s", ACCENT),
        ("uncapped", d.uncapped, d.sim, "the draws' optimum without the cap", "o", ACCENT),
        ("historical", d.historical, d.returns, "the saved returns' optimum", "D", MUTED),
        ("kelly", d.kelly, d.returns, "the saved returns' Kelly", "^", MUTED),
    )
    for gid, f, series, text, marker, color in marks:
        g = growth(f, series)
        ax.plot(
            [f],
            [g],
            marker,
            color=color,
            mec=SURFACE,
            ms=7,
            zorder=4,
            ls="none",
            gid=gid,
            label=f"{text}, {f:.6f}, growth {g:.6f}",
        )

    for gid, value in (
        ("book-kelly", BOOK_KELLY),
        ("book-fminbnd", BOOK_OPTIMUM_FMINBND),
        ("book-optimum", BOOK_OPTIMUM),
    ):
        ax.axvline(float(value), ymin=0, ymax=BOOK_TICK, color=LOST, lw=1.6, gid=gid)
    ax.text(
        float(BOOK_KELLY) - 0.2,
        0.05,
        f"{BOOK_KELLY}, the book's Kelly\nand historical optimum",
        transform=ax.get_xaxis_transform(),
        ha="right",
        color=LOST,
        fontsize=9,
        gid="book-kelly-label",
    )
    ax.text(
        float(BOOK_OPTIMUM) - 0.2,
        BOOK_TICK + 0.02,
        f"{BOOK_OPTIMUM_FMINBND} and {BOOK_OPTIMUM},\nthe book's simulated optimum",
        transform=ax.get_xaxis_transform(),
        ha="right",
        color=LOST,
        fontsize=9,
        gid="book-optimum-label",
    )

    ax.set_xlim(0.0, LEVERAGE_MAX)
    ax.set_ylim(*GROWTH_LIMITS)
    ax.set_xlabel("leverage f", color=INK, fontsize=10)
    ax.set_ylabel("growth rate g(f), per day", color=INK, fontsize=10)
    ax.legend(loc="upper left", frameon=False, fontsize=8.8, labelcolor=INK)
    _heading(
        ax,
        "Figure 8.2 redrawn: the growth rate g(f), the mean of log(1 + f·R), against the "
        "leverage f.\nThe book prints 18.4 for the Kelly and for the historical optimum. "
        "The saved returns give neither.",
    )


def block_minima(drawdowns: NDArray[np.float64], block: int = BLOCK) -> NDArray[np.float64]:
    """The deepest drawdown in each run of ``block`` days, the first block starting on day 1."""
    return drawdowns.reshape(-1, block).min(axis=1)


def _cppi_panel(ax, d: Drawn) -> None:
    edges = np.arange(0, len(d.sim) + 1, BLOCK)
    rows = (
        ("full", d.full, MUTED, f"the full account at f·D = {d.capped * D:.6f}"),
        ("scripted", d.scripted, LOST, "Box 8.6's loop"),
        ("described", d.described, GOOD, "the scheme on p. 263"),
    )
    for gid, series, color, name in rows:
        start = first_below(series)
        below = days_below(series)
        tail = (
            f"below {signed(FLOOR, 1)} on {below:,} days from day {start:,}"
            if start is not None
            else f"never below {signed(FLOOR, 1)}"
        )
        ax.stairs(
            block_minima(series),
            edges,
            color=color,
            lw=1.3,
            baseline=None,
            gid=gid,
            label=f"{name}: deepest {signed(float(series.min()))} on day "
            f"{deepest_day(series):,}, {tail}",
        )
        day = deepest_day(series)
        ax.plot(
            [day], [float(series[day - 1])], "o", color=color, ms=5, zorder=4, gid=f"{gid}-deepest"
        )
    ax.axhline(FLOOR, color=INK, lw=1.1, ls="--", gid="floor")

    ax.set_xlim(0, len(d.sim))
    ax.set_ylim(*DRAWDOWN_LIMITS)
    ax.xaxis.set_major_formatter(FuncFormatter(_thousands))
    ax.set_xlabel("day of the draws", color=INK, fontsize=10)
    ax.set_ylabel(f"deepest drawdown in each {BLOCK:,} days", color=INK, fontsize=10)
    ax.legend(loc="lower right", frameon=False, fontsize=8.8, labelcolor=INK)
    _heading(
        ax,
        f"Two CPPI forms on the same draws, at the script's f of {d.capped:.6f} and D = {D:g}."
        f"\nChan says on p. 264 that CPPI's drawdown is less than {-FLOOR:g} by design. The dashed "
        f"line is {signed(FLOOR, 1)}.",
    )


@_plain_text
def make_monte_carlo_leverage_figure(
    out: Path | None = None,
    saved: tuple[VintageEntry, NDArray[np.float64]] | None = None,
) -> Figure:
    """Figure 8.2 with the evidence on 18.4, and two CPPI forms against the floor."""
    d = drawn(saved)

    fig = Figure(figsize=(10, 11), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    growth_ax, cppi_ax = fig.subplots(2, 1, gridspec_kw={"hspace": 0.38})
    for ax in (growth_ax, cppi_ax):
        _style(ax)
    _growth_panel(growth_ax, d)
    _cppi_panel(cppi_ax, d)
    _title(
        fig,
        "Exploratory: Chapter 8's leverage on Example 5.1's returns, one declared seed",
        f"Algorithmic Trading, Kindle edition, Figure 8.2 and pp. 258 to 265. Returns from "
        f"{d.entry.path}, saved {d.entry.obtained}.\nDraws: {DRAWS:,} from the Pearson type "
        f"IV with the returns' four moments, on seed {SEED}. No further seed is drawn here.",
    )
    fig.subplots_adjust(left=0.1, right=0.97, top=0.9, bottom=0.1)
    return _save(fig, out, FIGURE)


def main() -> None:
    try:
        make_monte_carlo_leverage_figure()
    except VintageUnavailable as refused:
        # A refusal that names the file reaches the reader as one line, the way
        # chan.monte_carlo_leverage.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / FIGURE}")


if __name__ == "__main__":
    main()
