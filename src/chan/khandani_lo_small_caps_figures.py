"""The figure for ``blog/khandani-lo-small-caps-lessons.md``, *Quantitative Trading* location 2137.

That post is on Khandani and Lo's reversal run on Chan's S&P 600 file beside
his S&P 500 file. :mod:`chan.khandani_lo_small_caps` prints Entry 44's figures
and draws nothing, so this module draws what the run does not.
[issue 525](https://github.com/l3a0/quantitative-trading/issues/525) asked for
the post, and its plan set the figure.

Two panels, the closes above the opens. Each draws four running totals over
2006: the S&P 600 and the S&P 500, each before costs and after 5 basis points
a side with the first day charged. Each total is
:func:`chan.survivorship_and_costs_figures.cumulative`, each day's profit
summed through the window over that book's own mean gross position, so a line
reads as a share of the position held and no Sharpe ratio moves. A running
total cannot carry the NaN on the first day of Chan's own after-cost series,
which is why the cost lines charge the first day, as the published post's
figure does. Each panel heading states the before-cost Sharpe ratio gap, its
standard error and its z, because the totals alone do not say how much of the
distance between two lines one year's noise could make.

Every value comes from :func:`chan.khandani_lo_small_caps.compare`, the run's
own path. That module does not call the scale-break guard, and its docstring
says why, so neither does this one::

    uv run python -m chan.khandani_lo_small_caps_figures
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from matplotlib.dates import DateFormatter, MonthLocator
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.khandani_lo import ONE_WAY_COST
from chan.khandani_lo_small_caps import (
    LARGE_CAP_FILE,
    NOISE_MULTIPLE,
    SOURCE_FILE,
    Comparison,
    SharpeGap,
    compare,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, INK, MUTED, SURFACE
from chan.survivorship_and_costs_figures import cumulative
from chan.vintage import VintageUnavailable, read_manifest

KHANDANI_LO_SMALL_CAPS_FIGURE = "khandani_lo_small_caps.png"

#: The two panels, top to bottom.
PRICES = ("closes", "opens")
#: The lines each panel draws, in the order the legend lists them.
LINES = ("small-before", "small-after", "large-before", "large-after")
#: Each universe's colour and name, and which file it is read from.
UNIVERSE_STYLE = {
    "small": (ACCENT, "S&P 600", SOURCE_FILE),
    "large": (INK, "S&P 500", LARGE_CAP_FILE),
}
#: Each cost treatment's style, width and name.
COST_STYLE = {
    "before": ("-", 1.9, "before costs"),
    "after": ("--", 1.5, f"after {ONE_WAY_COST * 1e4:.0f} bp a side"),
}


def running_totals(result: Comparison, price: str) -> dict[str, np.ndarray]:
    """The four running totals one panel draws, keyed as :data:`LINES` names them."""
    totals = {
        universe: cumulative(getattr(result, f"{universe}_{price}")) for universe in UNIVERSE_STYLE
    }
    return {
        f"{universe}-{cost}": getattr(totals[universe], cost)
        for universe in UNIVERSE_STYLE
        for cost in COST_STYLE
    }


def saved(source_file: str, data_dir: Path | None = None) -> str:
    """The day Chan saved ``source_file``, read from the manifest rather than retyped.

    Every member of one lifted file shares a saved date, which
    :func:`chan.series.load_panel` checks, so one date comes back.
    """
    dates = {e.obtained for e in read_manifest(data_dir) if e.source_workbook == source_file}
    if len(dates) != 1:
        raise VintageUnavailable(
            f"{source_file} has {len(dates)} saved dates in the manifest, and the figure names one"
        )
    return dates.pop()


def signed(value: float, places: int = 4) -> str:
    """``value`` with its sign always shown and a true minus sign, as the post prints it."""
    return f"{value:+.{places}f}".replace("-", "−")


def percent(value: float) -> str:
    """A running total as a signed percent to one decimal, as the post prints it."""
    return f"{value:+.1%}".replace("-", "−")


def heading(price: str, gap: SharpeGap) -> str:
    """One panel's heading: both Sharpe ratios, the gap, its standard error and its z."""
    word = "beyond" if gap.beyond_noise else "within"
    return (
        f"On the {price}, the S&P 600's Sharpe ratio before costs is {gap.a_sharpe:.4f} against "
        f"the S&P 500's {gap.b_sharpe:.4f}.\nThe gap is {signed(gap.gap)}, its standard error "
        f"{gap.standard_error:.4f}, so z is {signed(gap.z)}, {word} the line of "
        f"{NOISE_MULTIPLE:g} standard errors."
    )


def _panel(ax, result: Comparison, price: str) -> None:
    totals = running_totals(result, price)
    days = getattr(result, f"small_{price}").days
    ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    for key in LINES:
        universe, cost = key.split("-")
        colour, name, _ = UNIVERSE_STYLE[universe]
        style, width, treatment = COST_STYLE[cost]
        line = totals[key]
        ax.plot(
            days,
            line,
            color=colour,
            ls=style,
            lw=width,
            gid=key,
            label=f"{name}, {treatment}, ending at {percent(line[-1])}",
        )
    ax.set_xlim(days[0], days[-1])
    ax.xaxis.set_major_locator(MonthLocator())
    ax.xaxis.set_major_formatter(DateFormatter("%b"))
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.set_ylabel("profit so far, share of the mean position", color=INK, fontsize=10)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK)
    gap = result.closes_gap if price == "closes" else result.opens_gap
    ax.set_title(heading(price, gap), loc="left", color=INK, fontsize=10.5, linespacing=1.4)


@_plain_text
def make_khandani_lo_small_caps_figure(
    out: Path | None = None, result: Comparison | None = None
) -> Figure:
    """The year's running profit on both files, before and after costs, at the close and open."""
    result = result if result is not None else compare()
    days = result.small_closes.days

    fig = Figure(figsize=(10, 11), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    axes = fig.subplots(2, 1, sharey=True, gridspec_kw={"hspace": 0.34})
    for ax, price in zip(axes, PRICES, strict=True):
        _style(ax)
        _panel(ax, result, price)

    _title(
        fig,
        "Exploratory: Khandani and Lo's reversal on Chan's S&P 600 and S&P 500 files",
        f"Quantitative Trading, locations 2137 and 2236, over {days[0].date()} to "
        f"{days[-1].date()}. The S&P 600 from {SOURCE_FILE},\nsaved {saved(SOURCE_FILE)}, and "
        f"the S&P 500 from {LARGE_CAP_FILE}, saved {saved(LARGE_CAP_FILE)}. Each line sums the "
        "day's profit over\nits own book's mean gross position for the year. The cost lines "
        "charge the first day too, which Chan's code does not.\nBoth files hold only survivors, "
        "and the S&P 600 holds no microcaps.",
    )
    fig.subplots_adjust(left=0.1, right=0.97, top=0.9, bottom=0.125)
    return _save(fig, out, KHANDANI_LO_SMALL_CAPS_FIGURE)


def main() -> None:
    try:
        make_khandani_lo_small_caps_figure()
    except VintageUnavailable as unavailable:
        # A refusal that names the source reaches the reader as one line, the
        # way chan.khandani_lo_small_caps.main does it. The run calls no
        # scale-break guard, so no other refusal can reach here.
        raise SystemExit(str(unavailable)) from unavailable
    print(f"wrote {FIGURES_DIR / KHANDANI_LO_SMALL_CAPS_FIGURE}")


if __name__ == "__main__":
    main()
