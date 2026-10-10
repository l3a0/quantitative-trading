"""The figure for the post on AUD.CAD with rollover interest, Example 5.2.

``blog/aud-cad-rollover-lessons.md`` teaches what Entry 30 of the replication
log found. The book prints no chart for this example, so no panel redraws one
of Chan's. :func:`make_rollover_figure` draws three panels that share the date
axis from July 2007, the month of the first close, to 2012-04-26, the last.

1. The AUD and CAD monthly rates in percent a year, as the two files hold
   them. A month a file lacks is drawn as a hollow marker at zero, because
   the script reads it as zero rather than carrying the last month forward.
   CAD lacks January to April 2012 and AUD lacks April 2012.
2. The AUD.CAD close, shaded by the position each day holds. A day's
   position is the one yesterday's z-score set, ``lag1(position)``, since
   that is the position that earns the day's return. Each held day is shaded
   from the previous close to its own, so the shading covers the stretch the
   position was held over. The first 20 days hold nothing.
3. The cumulative return with and without rollover interest, compounded as
   the script compounds it, ``cumprod(1 + returns) − 1``. Each line ends at
   ``(1 + apr) ** (1237 / 252) − 1`` for its own APR.

Every value comes from :func:`chan.aud_cad_rollover.read_sources` and
:func:`chan.aud_cad_rollover.aud_cad_rollover`, the run's own path, so the
scale-break guard runs here too::

    uv run python -m chan.aud_cad_rollover_figures
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter, YearLocator
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter
from numpy.typing import NDArray

from chan.aud_cad_rollover import (
    SCRIPT_LOOKBACK,
    Rollover,
    Sources,
    aud_cad_rollover,
    read_sources,
)
from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.matlab_helpers import lag1
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED, RULE, SURFACE
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable

ROLLOVER_FIGURE = "aud_cad_rollover.png"

#: Each currency's rate line on the top panel, and its hollow zero markers.
RATE_COLOURS = {"AUD": ACCENT, "CAD": INK}
#: The shading on the middle panel. A long position earns the rate
#: difference and a short one pays it.
HELD_COLOURS = {"long": GOOD, "short": LOST}
#: The two cumulative returns on the bottom panel.
CUMULATIVE_COLOURS = {"with": INK, "without": MUTED}
#: Both files lack April 2012, so AUD's ring is drawn around CAD's.
MISSING_MARKER_SIZES = {"AUD": 9, "CAD": 5}


def missing_months(monthly: pd.Series, days: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """The first day of each month the closes span that ``monthly`` holds no rate for."""
    spanned = pd.period_range(days[0].to_period("M"), days[-1].to_period("M"), freq="M")
    held = monthly.index.to_period("M")
    return spanned.difference(held).to_timestamp()


def held_position(result: Rollover) -> NDArray[np.float64]:
    """The position each day's return is earned on, yesterday's ``−sign(z)``.

    The first :data:`SCRIPT_LOOKBACK` rows are not a number, because no
    z-score had filled by the day before them.
    """
    return lag1(result.position)


@dataclass(frozen=True)
class Spell:
    """A run of consecutive days held the same way, as row positions in the closes.

    ``first`` and ``last`` are the first and last day held. The spell is
    shaded from the close before ``first`` to the close on ``last``.
    """

    side: str
    first: int
    last: int


def spells(held: NDArray[np.float64]) -> list[Spell]:
    """The maximal runs of days held long or held short, in order."""
    found: list[Spell] = []
    for day, position in enumerate(held):
        if np.isnan(position) or position == 0:
            continue
        side = "long" if position > 0 else "short"
        if found and found[-1].side == side and found[-1].last == day - 1:
            found[-1] = Spell(side, found[-1].first, day)
        else:
            found.append(Spell(side, day, day))
    return found


def cumulative(returns: NDArray[np.float64]) -> NDArray[np.float64]:
    """Line 49's compounding, kept day by day: ``cumprod(1 + returns) − 1``."""
    return np.cumprod(1 + returns) - 1


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


def _month(day: pd.Timestamp) -> str:
    return day.strftime("%B %Y")


def _extremes(series: pd.Series) -> str:
    """Where a rate series peaks and bottoms, each at its first month."""
    return (
        f"peaks at {series.max():.2f} in {_month(series.idxmax())} and bottoms at "
        f"{series.min():.2f} in {_month(series.idxmin())}"
    )


@_plain_text
def make_rollover_figure(out: Path | None = None, sources: Sources | None = None) -> Figure:
    """The two rates, the close shaded by the held position, and the two cumulative returns."""
    if sources is None:
        sources = read_sources()
    closes = sources.closes[1]
    result = aud_cad_rollover(closes, sources.aud[1], sources.cad[1])
    days = result.days
    start = days[0].to_period("M").to_timestamp()
    held = held_position(result)

    fig = Figure(figsize=(10, 12), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    rate_ax, close_ax, cum_ax = fig.subplots(3, 1, sharex=True)
    for ax in (rate_ax, close_ax, cum_ax):
        _style(ax)

    shown = {}
    for name, (_, monthly) in (("AUD", sources.aud), ("CAD", sources.cad)):
        rates = monthly.loc[start:]
        shown[name] = rates
        colour = RATE_COLOURS[name]
        rate_ax.plot(
            rates.index, rates, color=colour, lw=1.4, marker="o", ms=2.5, gid=name, label=name
        )
        missing = missing_months(monthly, days)
        rate_ax.plot(
            [rates.index[-1], *missing],
            [rates.iloc[-1], *np.zeros(len(missing))],
            color=colour,
            lw=1.2,
            ls=":",
            gid=f"{name}-drop",
        )
        rate_ax.plot(
            missing,
            np.zeros(len(missing)),
            ls="none",
            marker="o",
            ms=MISSING_MARKER_SIZES[name],
            mfc="none",
            mec=colour,
            mew=1.4,
            gid=f"{name}-missing",
            label=f"{name}, month missing from the file, read as 0",
        )
    rate_ax.set_ylabel("rate, percent a year", color=INK, fontsize=10)
    rate_ax.set_ylim(bottom=-0.4)
    rate_ax.legend(loc="upper right", frameon=False, fontsize=9, labelcolor=INK)
    _heading(
        rate_ax,
        f"The monthly rates from {_month(start)}. AUD {_extremes(shown['AUD'])}.\n"
        f"CAD {_extremes(shown['CAD'])}.\nThe script reads a month a file lacks as 0, "
        "drawn dotted to a hollow ring.",
    )

    close_ax.plot(days, closes, color=INK, lw=1.0, gid="close")
    close_ax.axvspan(
        days[0], days[SCRIPT_LOOKBACK - 1], color=RULE, alpha=0.45, lw=0, gid="unfilled"
    )
    for spell in spells(held):
        close_ax.axvspan(
            days[spell.first - 1],
            days[spell.last],
            color=HELD_COLOURS[spell.side],
            alpha=0.22,
            lw=0,
            gid=spell.side,
        )
    close_ax.set_ylabel("AUD.CAD close, CAD per AUD", color=INK, fontsize=10)
    long_days = int(np.count_nonzero(held > 0))
    short_days = int(np.count_nonzero(held < 0))
    _heading(
        close_ax,
        f"The AUD.CAD close, from {closes.min():.5f} on {closes.idxmin().date()} to "
        f"{closes.max():.5f} on {closes.idxmax().date()}.\nShaded green on the {long_days} "
        f"days held long and red on the {short_days} held short. The first "
        f"{SCRIPT_LOOKBACK} days hold nothing.",
    )

    with_rollover, without_rollover = cumulative(result.returns), cumulative(result.without)
    cum_ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    cum_ax.plot(
        days,
        with_rollover,
        color=CUMULATIVE_COLOURS["with"],
        lw=1.4,
        gid="with",
        label="with rollover interest",
    )
    cum_ax.plot(
        days,
        without_rollover,
        color=CUMULATIVE_COLOURS["without"],
        lw=1.2,
        ls="--",
        gid="without",
        label="without",
    )
    cum_ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    cum_ax.set_ylabel("cumulative return", color=INK, fontsize=10)
    cum_ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK)
    _heading(
        cum_ax,
        "Each day's log return compounded as if it were simple, as the script does.\n"
        f"With rollover interest it ends at {100 * with_rollover[-1]:.2f} percent, and "
        f"without it at {100 * without_rollover[-1]:.2f} percent.",
    )
    cum_ax.set_xlim(start, days[-1])
    cum_ax.xaxis.set_major_locator(YearLocator())
    cum_ax.xaxis.set_major_formatter(DateFormatter("%Y"))

    names = [Path(entry.path).name for entry in sources.entries]
    saved = sorted({entry.saved_date for entry in sources.entries})
    _title(
        fig,
        "Exploratory: AUD.CAD with and without rollover interest, on Chan's own files",
        f"Algorithmic Trading, Example 5.2, {days[0].date()} to {days[-1].date()}, "
        f"{len(days):,} days. Closes from {names[0]},\nrates from {names[1]} and "
        f"{names[2]}, Chan's Python port, saved {', '.join(saved)}.\nChan chose the rule "
        "and the sample, and no cost is charged.",
    )
    fig.tight_layout(rect=(0, 0.06, 1, 0.975))
    return _save(fig, out, ROLLOVER_FIGURE)


def main() -> None:
    try:
        make_rollover_figure()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source is worth nothing at the bottom of a
        # traceback, so it reaches the operator as one line, the way
        # chan.aud_cad_rollover.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / ROLLOVER_FIGURE}")


if __name__ == "__main__":
    main()
