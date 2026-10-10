"""The figure for the post on spot and roll returns, *Algorithmic Trading*'s Example 5.3.

The post teaches what Entry 27 of the replication log found, and
[issue 458](https://github.com/l3a0/quantitative-trading/issues/458) chose one
figure for it. :func:`make_roll_returns_figure` draws two panels.

1. Each strip's spot return and both roll returns as bars, in percent: the
   script's γ, which regresses on contract columns and printed Table 5.1, and
   the γ regressed on months, the unit the book's text names. A tick over BR,
   C and TU marks twice the spot return, the threshold location 2399's claim
   was read against. Neither of Chan's figures shows this, because both draw CL,
   whose contracts are a month apart.
2. CL's γ on every day it is defined, the book's Figure 5.5, shaded above zero
   for backwardation and below for contango, with its mean drawn across it.

Figure 5.4 is not redrawn. The book names its contracts and not its day, so a
redraw would have to choose a day the book does not give.

Every value comes from :func:`chan.roll_returns.load_strip` and
:func:`chan.roll_returns.strip_returns`, the run's own path, so the
scale-break guard runs here too. Redraw it with::

    uv run python -m chan.roll_returns_figures
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from matplotlib.dates import DateFormatter, YearLocator
from matplotlib.figure import Figure

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED, SURFACE
from chan.roll_returns import ROOTS, StripReturns, load_strip, strip_returns
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable

ROLL_RETURNS_FIGURE = "roll_returns.png"
#: The strip whose γ Figure 5.5 plots.
FIGURE_5_5_ROOT = "CL"
#: The strips location 2399 says have a roll return much larger than their
#: spot return, read as at least twice.
MUCH_LARGER = ("BR", "C2", "TU")
#: How far either side of a group's centre its three bars sit.
BAR_WIDTH = 0.26


def book_label(root: str) -> str:
    """The symbol Table 5.1 prints. The C2 strip is the book's C."""
    return "C" if root == "C2" else root


def signed(value: float, places: int = 6) -> str:
    """``value`` to ``places`` decimals with a true minus sign, as the post prints it."""
    return f"{value:.{places}f}".replace("-", "−")


def read_results() -> dict[str, StripReturns]:
    """Each strip of Table 5.1 through the run's one read path, in the table's order."""
    return {root: strip_returns(load_strip(root)) for root in ROOTS}


def bar_heights(results: dict[str, StripReturns]) -> dict[str, list[float]]:
    """The three bars of each strip in percent: |α|, the script's |γ| and the month-spaced |γ|."""
    return {
        "alpha": [100 * abs(results[root].alpha) for root in ROOTS],
        "gamma-columns": [100 * abs(results[root].mean_gamma) for root in ROOTS],
        "gamma-months": [100 * abs(results[root].mean_gamma_in_months) for root in ROOTS],
    }


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


@_plain_text
def make_roll_returns_figure(
    out: Path | None = None,
    results: dict[str, StripReturns] | None = None,
) -> Figure:
    """The spot and roll returns of the five strips, and CL's roll return day by day."""
    results = results if results is not None else read_results()
    heights = bar_heights(results)
    cl = results[FIGURE_5_5_ROOT]
    gamma = cl.gamma.dropna()
    days = gamma.index
    contango, backwardation = int((gamma < 0).sum()), int((gamma > 0).sum())

    fig = Figure(figsize=(10, 9.5), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    bar_ax, gamma_ax = fig.subplots(2, 1, gridspec_kw={"height_ratios": (1, 1)})
    for ax in (bar_ax, gamma_ax):
        _style(ax)

    centres = np.arange(len(ROOTS), dtype=float)
    for offset, (gid, colour, label) in zip(
        (-BAR_WIDTH, 0.0, BAR_WIDTH),
        (
            ("alpha", MUTED, "spot return |α|"),
            ("gamma-columns", ACCENT, "roll return |γ|, the script's, on contract columns"),
            ("gamma-months", GOOD, "roll return |γ| with maturity in months, the text's unit"),
        ),
        strict=True,
    ):
        bars = bar_ax.bar(centres + offset, heights[gid], BAR_WIDTH, color=colour, label=label)
        for bar in bars:
            bar.set_gid(gid)
    for i, root in enumerate(ROOTS):
        if root in MUCH_LARGER:
            twice = 2 * heights["alpha"][i]
            bar_ax.plot(
                [centres[i] - 1.5 * BAR_WIDTH, centres[i] + 1.5 * BAR_WIDTH],
                [twice, twice],
                color=LOST,
                lw=1.4,
                ls=(0, (3, 2)),
                zorder=3,
                gid=f"twice-alpha-{book_label(root)}",
            )
    bar_ax.plot([], [], color=LOST, lw=1.4, ls=(0, (3, 2)), label="twice the spot return")
    bar_ax.set_xticks(centres, [book_label(root) for root in ROOTS])
    bar_ax.set_ylabel("annualized, percent", color=INK, fontsize=10)
    bar_ax.legend(loc="upper right", frameon=False, fontsize=9, labelcolor=INK)
    hg, c = results["HG"], results["C2"]
    _heading(
        bar_ax,
        "Table 5.1's spot and roll returns, and the roll return with maturity in months.\n"
        f"On months HG's roll return of {100 * hg.mean_gamma_in_months:.2f}% falls below its "
        f"spot return of {100 * hg.alpha:.2f}%,\nand C's is "
        f"{abs(c.mean_gamma_in_months) / abs(c.alpha):.2f} times its spot return, short of "
        "twice.",
    )

    gamma_ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    gamma_ax.fill_between(
        days, gamma, 0, where=gamma > 0, color=GOOD, alpha=0.35, lw=0, gid="backwardation"
    )
    gamma_ax.fill_between(
        days, gamma, 0, where=gamma < 0, color=LOST, alpha=0.25, lw=0, gid="contango"
    )
    gamma_ax.plot(days, gamma, color=INK, lw=0.6, gid="gamma")
    gamma_ax.axhline(
        cl.mean_gamma,
        color=ACCENT,
        lw=1.4,
        ls=(0, (5, 3)),
        gid="mean",
        label=f"mean {signed(cl.mean_gamma)}, Table 5.1's −7.1%",
    )
    gamma_ax.set_ylabel("roll return γ, annualized", color=INK, fontsize=10)
    gamma_ax.legend(loc="lower left", frameon=False, fontsize=9.5, labelcolor=INK)
    _heading(
        gamma_ax,
        f"Figure 5.5 redrawn: CL's roll return on its {len(days):,} days from "
        f"{days[0].date()} to {days[-1].date()}.\nBelow zero, contango, on "
        f"{contango:,} days and above zero, backwardation, on {backwardation:,}.",
    )
    gamma_ax.set_xlim(days[0], days[-1])
    gamma_ax.xaxis.set_major_locator(YearLocator())
    gamma_ax.xaxis.set_major_formatter(DateFormatter("%Y"))

    first = cl.strip.members[0]
    _title(
        fig,
        "Exploratory: spot and roll returns redrawn on Chan's own futures strips",
        f"Example 5.3 of Algorithmic Trading. Five strips saved {first.obtained}, one "
        "file per commodity holding its spot and every contract.\nα is 252 times the slope "
        "of the log spot on the day number. γ is −12 times the slope of the five nearest "
        "contracts'\nlog prices on their columns, or on their months. Every figure is "
        "in-sample on 1986 to 2012.",
    )
    fig.tight_layout(rect=(0, 0.075, 1, 0.97))
    return _save(fig, out, ROLL_RETURNS_FIGURE)


def main() -> None:
    try:
        make_roll_returns_figure()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day is worth nothing at
        # the bottom of a traceback, so it reaches the operator as one line, the
        # way chan.roll_returns.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / ROLL_RETURNS_FIGURE}")


if __name__ == "__main__":
    main()
