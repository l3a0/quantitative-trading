"""The figure for ``blog/aud-cad-johansen-lessons.md``, *Algorithmic Trading*'s Example 5.1.

The post teaches what Entry 25 of the replication log found, and
[issue 452](https://github.com/l3a0/quantitative-trading/issues/452) chose one
figure for it. :func:`make_aud_cad_figure` draws two panels that share the date
axis over the 612 test days ``AUDCAD_unequal.m`` reports on.

1. Each day's hedge as a dollar split, CAD.USD's signed share of the gross with
   AUD.USD held long, from :attr:`chan.aud_cad_johansen.AudCad.dollar_split`.
   The days it held both legs the same way are shaded, and the windows where
   the trace test found a relation at 95 percent are marked on the line, with
   windows finding one relation drawn differently from those finding two. The
   script draws none of this. Location 2186 says the eigenvector is a capital
   weight, and this panel shows what that weight did.
2. The cumulative compounded return, which line 57 of the script draws with
   ``plot(cumprod(1+ret(trainlen+1:end))-1)`` against the row number. It is
   the book's Figure 5.1, drawn here against the date.

Every value comes from :func:`chan.aud_cad_johansen.read_sources` and
:func:`chan.aud_cad_johansen.aud_cad`, the run's own path, so the scale-break
guard runs here too. Redraw it with::

    uv run python -m chan.aud_cad_johansen_figures
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter, YearLocator
from matplotlib.figure import Figure
from numpy.typing import NDArray

from chan.aud_cad_johansen import (
    RELATION_LEVEL,
    SCRIPT_LOOKBACK,
    AudCad,
    Sources,
    aud_cad,
    cross_rates,
    read_sources,
)
from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED, RULE, SURFACE
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable

AUD_CAD_FIGURE = "aud_cad_johansen.png"


def cumulative_return(result: AudCad) -> pd.Series:
    """``cumprod(1 + ret) − 1`` over the test days, the line the script's ``plot`` draws."""
    return pd.Series(np.cumprod(1.0 + result.test) - 1.0, index=result.test_days)


def spells(mask: NDArray[np.bool_]) -> list[tuple[int, int]]:
    """The first and last index of each run of consecutive ``True`` in ``mask``."""
    edges = np.diff(np.concatenate(([0], mask.astype(int), [0])))
    return list(zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1) - 1, strict=True))


def signed(value: float, places: int = 3) -> str:
    """``value`` to ``places`` decimals with a true minus sign, as the post prints it."""
    return f"{value:.{places}f}".replace("-", "−")


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


@_plain_text
def make_aud_cad_figure(out: Path | None = None, sources: Sources | None = None) -> Figure:
    """The hedge as a dollar split with the trace test's windows, and the cumulative return."""
    sources = sources if sources is not None else read_sources()
    result = aud_cad(cross_rates(sources.audusd[1], sources.usdcad[1]))
    days = result.test_days
    split = result.dollar_split
    same_way = split > 0
    relations = result.trace_relations
    cumulative = cumulative_return(result)
    apr = result.figures.apr

    fig = Figure(figsize=(10, 9.5), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    split_ax, return_ax = fig.subplots(2, 1, sharex=True, gridspec_kw={"height_ratios": (1, 1)})
    for ax in (split_ax, return_ax):
        _style(ax)

    # Each band runs to the next test day, so a spell of one day still shows.
    for first, last in spells(same_way):
        end = days[min(last + 1, len(days) - 1)]
        split_ax.axvspan(
            days[first], end, color=LOST, alpha=0.12, lw=0, gid=f"same-way-{days[first].date()}"
        )
    split_ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    split_ax.axhline(-0.5, color=RULE, lw=1.2, ls="--", gid="equal-dollars")
    split_ax.plot(days, split, color=ACCENT, lw=1.1, gid="split", label="CAD.USD's share")
    for count, gid, colour, fill in (
        (1, "one-relation", INK, "none"),
        (2, "two-relations", LOST, LOST),
    ):
        found = relations == count
        split_ax.plot(
            days[found],
            split[found],
            "o",
            ms=5,
            color=colour,
            mfc=fill,
            ls="none",
            gid=gid,
            label=f"trace test finds {count} relation{'s' if count > 1 else ''}",
        )
    split_ax.set_ylim(-1.05, 1.05)
    split_ax.set_ylabel("CAD.USD's share of the gross, AUD.USD long", color=INK, fontsize=10)
    split_ax.legend(loc="upper center", frameon=False, fontsize=9.5, labelcolor=INK)
    _heading(
        split_ax,
        f"Each day's hedge in dollars. At −0.5 the two legs hold equal dollars against each "
        f"other,\nand above 0 they are held the same way, which the shaded "
        f"{int(same_way.sum())} days did.\nThe dots are the {int(np.count_nonzero(relations))} "
        f"of {len(days)} windows where the trace test found a relation at {RELATION_LEVEL} "
        f"percent,\n{int(np.count_nonzero(relations == 2))} of them two. The last day split "
        f"1 to {signed(split[-1] / (1 - abs(split[-1])), 4)}, long AUD.USD.",
    )

    return_ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    return_ax.plot(days, cumulative, color=GOOD, lw=1.2, gid="cumulative")
    return_ax.set_ylabel("cumulative return, compounded", color=INK, fontsize=10)
    _heading(
        return_ax,
        f"The cumulative return over the {len(days)} test days, ending at "
        f"{signed(cumulative.iloc[-1], 4)}, an APR of {signed(apr, 4)}.\nUnlevered, before costs "
        "and without rollover interest.",
    )
    return_ax.set_xlim(days[0], days[-1])
    return_ax.xaxis.set_major_locator(YearLocator())
    return_ax.xaxis.set_major_formatter(DateFormatter("%Y"))

    _title(
        fig,
        "Exploratory: AUD.USD against CAD.USD redrawn on Chan's own daily closes",
        f"Example 5.1 of Algorithmic Trading, {days[0].date()} to {days[-1].date()}, after "
        f"{result.training} days of training.\nCloses from {sources.audusd[0].path} and\n"
        f"{sources.usdcad[0].path}, saved {sources.audusd[0].obtained}.\nEach day's hedge "
        f"is fitted on the {result.training} days before it and held in units of minus a "
        f"{SCRIPT_LOOKBACK}-day z-score.",
    )
    fig.tight_layout(rect=(0, 0.1, 1, 0.97))
    return _save(fig, out, AUD_CAD_FIGURE)


def main() -> None:
    try:
        make_aud_cad_figure()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day is worth nothing at
        # the bottom of a traceback, so it reaches the operator as one line, the
        # way chan.aud_cad_johansen.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / AUD_CAD_FIGURE}")


if __name__ == "__main__":
    main()
