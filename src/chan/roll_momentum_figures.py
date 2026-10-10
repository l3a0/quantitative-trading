"""The figure for the post on TU momentum traded on the lagged roll return.

``blog/roll-momentum-lessons.md`` teaches what Entry 36 of the replication log
found. The book prints no chart for location 2690, so this figure is the
repo's own. :func:`make_roll_momentum_figure` draws two panels over the
window's 913 rows, from 2009-01-02 to 2012-08-13.

1. The compounded cumulative return of the declared rule and of Example 6.1's
   rule on the same rebuilt series, with the rows the declared rule is flat
   shaded. Example 6.1's rule is long on every window row, so its line is the
   return of holding TU.
2. γ, the roll return in the script's column units, against the thresholds at
   3 percent and −3 percent, with the same rows shaded. γ never reaches the
   lower threshold in the window, so the rule is never short.

Every value comes from :func:`chan.roll_returns.load_strip` and
:func:`chan.roll_momentum.roll_momentum`, the run's own path, so the
scale-break guard on each contract runs here too::

    uv run python -m chan.roll_momentum_figures
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from matplotlib.dates import DateFormatter, YearLocator, date2num
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, MUTED, SURFACE
from chan.roll_momentum import (
    BOOK_APR_PERCENT,
    BOOK_SHARPE,
    ROLL_ROWS,
    ROOT,
    THRESHOLD,
    roll_momentum,
)
from chan.roll_returns import Strip, load_strip
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable

FIGURE = "roll_momentum.png"


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


def flat_spans(days: np.ndarray, flat: np.ndarray) -> list[tuple[float, float]]:
    """Each run of flat rows as a span of date numbers, from midway to the row before to midway
    to the row after, clamped to the first and last day.

    A run of one row still gets a width, and the dates inside the spans are
    exactly the flat rows.
    """
    x = date2num(days)
    edges = np.flatnonzero(np.diff(np.concatenate([[0], flat.astype(int), [0]])))
    spans = []
    for start, end in zip(edges[::2], edges[1::2], strict=True):
        left = x[0] if start == 0 else (x[start - 1] + x[start]) / 2
        right = x[-1] if end == len(x) else (x[end - 1] + x[end]) / 2
        spans.append((float(left), float(right)))
    return spans


def _shade(ax, spans: list[tuple[float, float]]) -> None:
    for left, right in spans:
        ax.axvspan(left, right, color=MUTED, alpha=0.13, lw=0, gid="flat")


@_plain_text
def make_roll_momentum_figure(out: Path | None = None, strip: Strip | None = None) -> Figure:
    """Both rules' cumulative return over the window, and γ against the thresholds."""
    if strip is None:
        strip = load_strip(ROOT)
    result = roll_momentum(strip)
    days = result.window_days
    declared = np.cumprod(1 + result.daily[result.window]) - 1
    example = np.cumprod(1 + result.example_daily[result.window]) - 1
    held = result.held_position
    flat = held == 0
    spans = flat_spans(days, flat)
    gamma = result.gamma[result.window]
    peak = int(np.nanargmax(gamma))
    found, against = result.figures, result.example_figures
    tranches = result.example_positions[result.window]

    fig = Figure(figsize=(10, 9.4), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    curve_ax, gamma_ax = fig.subplots(2, 1, sharex=True, gridspec_kw={"height_ratios": (1.3, 1)})
    for ax in (curve_ax, gamma_ax):
        _style(ax)

    curve_ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    curve_ax.plot(
        days,
        example,
        color=ACCENT,
        lw=1.3,
        gid="example",
        label="Example 6.1's rule, on the 250-day return",
    )
    curve_ax.plot(
        days,
        declared,
        color=GOOD,
        lw=1.5,
        gid="declared",
        label="the declared rule, on the lagged roll return",
    )
    _shade(curve_ax, spans)
    curve_ax.set_xlim(date2num(days[0]), date2num(days[-1]))
    curve_ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    curve_ax.set_ylabel("cumulative return", color=INK, fontsize=10)
    curve_ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK)
    _heading(
        curve_ax,
        f"The compounded cumulative return over the {len(days)} window rows, shaded where the "
        f"declared rule is flat.\nThe declared rule: APR {found.apr:.6f} and Sharpe ratio "
        f"{found.sharpe:.6f}, which the book prints as {BOOK_APR_PERCENT} percent and "
        f"{BOOK_SHARPE}.\nExample 6.1's rule: APR {against.apr:.6f} and Sharpe ratio "
        f"{against.sharpe:.6f}. It holds all {tranches.min():.0f} tranches long on every\n"
        f"window row, so its line is holding TU. They end at {declared[-1]:.6f} and "
        f"{example[-1]:.6f}, before costs.",
    )

    gamma_ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    for sign, gid in ((1, "long above"), (-1, "short below")):
        gamma_ax.axhline(sign * THRESHOLD, color=MUTED, lw=1.1, ls="--", gid=gid)
    gamma_ax.plot(days, gamma, color=INK, lw=1.0, gid="gamma")
    _shade(gamma_ax, spans)
    gamma_ax.set_ylim(-0.045, 0.085)
    gamma_ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    gamma_ax.set_ylabel("roll return, column units", color=INK, fontsize=10)
    gamma_ax.xaxis.set_major_locator(YearLocator())
    gamma_ax.xaxis.set_major_formatter(DateFormatter("%Y"))
    _heading(
        gamma_ax,
        f"The rule goes long when γ is above {100 * THRESHOLD:.0f} percent and short below "
        f"−{100 * THRESHOLD:.0f} percent, on the next row.\nγ peaks at {gamma[peak]:.6f} on "
        f"{days[peak].date()} and never falls below −{100 * THRESHOLD:.0f} percent in the "
        f"window,\nso the rule is long on {int((held > 0).sum())} rows, short on "
        f"{int((held < 0).sum()) or 'none'} and flat on the {int(flat.sum())} shaded rows.",
    )

    vintage = Path(strip.members[0].path).parent
    _title(
        fig,
        "Exploratory: TU momentum traded on the lagged roll return, against Example 6.1",
        f"Algorithmic Trading, location 2690. TU contracts from {vintage}/, saved "
        f"{strip.members[0].obtained}.\nThe series is the front contract rebuilt from the "
        f"strip, rolling {ROLL_ROWS} rows before its last price.\nThe rule was declared after "
        "about 90 scratch readings, so this is no registered test, and no cost is taken.",
    )
    fig.tight_layout(rect=(0, 0.075, 1, 0.97))
    return _save(fig, out, FIGURE)


def main() -> None:
    try:
        make_roll_momentum_figure()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day is worth nothing at
        # the bottom of a traceback, so it reaches the operator as one line, the
        # way chan.roll_momentum.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / FIGURE}")


if __name__ == "__main__":
    main()
