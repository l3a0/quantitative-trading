"""The figure for ``blog/capped-low-beta-lessons.md``, *Quantitative Trading* at location 4709.

That post is on Chan's rule that a levered low-beta portfolio out-compounds an
unlevered high-beta one, tested at the two ceilings on leverage that
locations 814 and 2836 give. :mod:`chan.low_beta_capped` prints each ceiling's
outcome and draws nothing, so this module draws what the run does not.
[Issue 545](https://github.com/l3a0/quantitative-trading/issues/545) asked for
the post, and its plan set the figure. It teaches the post's third lesson,
that a large point estimate can still be noise.

One panel per ceiling, on one shared axis of the yearly gap in compounded
growth, so the reader sees the line move right as the leverage rises.

1. **The sampling curve if the true gap were 0**, a normal with the yearly
   Newey-West standard error, :func:`chan.low_beta_capped.yearly_standard_error`.
2. **The one-sided 5 percent line**, 1.645 standard errors to the right of 0,
   :func:`chan.low_beta_capped.five_percent_line`.
3. **The sampling curve if the true gap were Y**, the same normal centred on
   Y, with the part past the line shaded. Y is (1.645 + 0.8416) standard
   errors, so that part is four fifths of the curve.
4. **The point estimate**, marked on the baseline with its t.

Every figure drawn is exploratory. The ceilings were chosen after Entry 45's
figures had been seen, and the standard error and the line were added after
the run, so they decide nothing.

Every value comes from :func:`chan.low_beta_leverage.read_sources`,
:func:`chan.low_beta_leverage.build_portfolios` and
:func:`chan.low_beta_capped.assess`, the run's own path::

    uv run python -m chan.low_beta_capped_figures
"""

from __future__ import annotations

import math

import numpy as np
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator, NullLocator

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.low_beta_capped import (
    Outcome,
    assess,
    five_percent_line,
    yearly_standard_error,
)
from chan.low_beta_leverage import (
    SOURCE_FILE,
    Portfolios,
    build_portfolios,
    read_sources,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import GOOD, INK, LOST, MUTED, SURFACE
from chan.vintage import VintageUnavailable

LOW_BETA_CAPPED_FIGURE = "low_beta_capped.png"

#: The shared x-axis, wide enough for three standard errors either side of 0
#: and of Y at a ceiling of 5, the wider of the two.
GAP_LIMITS = (-0.45, 0.85)

#: How many points each curve is drawn through.
POINTS = 1301

#: The share of the curve centred on Y that lies past the 5 percent line.
SHADED = 0.80

#: Where each label sits, as a share of the panel's height and as an offset
#: in yearly gap from the point it names, chosen by eye on the committed
#: vintages so that no label crosses a line.
LINE_LABEL = (0.012, 0.93)
Y_LABEL = (1.35, 0.80)
ESTIMATE_LABEL = (GAP_LIMITS[0] + 0.015, 0.42)
ARROW = {"arrowstyle": "-", "color": INK, "lw": 0.8}


def signed(value: float, places: int = 4) -> str:
    """``value`` to ``places`` decimals with a true minus sign, as the post prints it."""
    return f"{value:.{places}f}".replace("-", "−")


def normal_density(x: np.ndarray, centre: float, scale: float) -> np.ndarray:
    """The normal density with mean ``centre`` and standard deviation ``scale`` at each ``x``."""
    z = (np.asarray(x, dtype=float) - centre) / scale
    return np.exp(-0.5 * z * z) / (scale * math.sqrt(2 * math.pi))


def _heading(ax, text: str) -> None:
    ax.set_title(text, loc="left", color=INK, fontsize=10.5, linespacing=1.4)


def _panel(ax, outcome: Outcome) -> None:
    c = outcome.capped
    se = yearly_standard_error(c)
    line = five_percent_line(c)
    y = c.detectable
    gap = c.gap
    xs = np.linspace(*GAP_LIMITS, POINTS)
    null = normal_density(xs, 0.0, se)
    alternative = normal_density(xs, y, se)
    top = float(null.max()) * 1.32

    # The shading starts exactly at the line rather than at the first grid
    # point past it, so its area is the share the post quotes.
    past = np.concatenate([[line], xs[xs > line]])
    ax.fill_between(
        past,
        normal_density(past, y, se),
        0,
        color=GOOD,
        alpha=0.22,
        lw=0,
        gid="shaded",
        label=f"{round(SHADED * 100)} percent of that curve, past the line",
    )
    ax.plot(xs, null, color=MUTED, lw=1.6, gid="null", label="if the true gap were 0")
    ax.plot(
        xs,
        alternative,
        color=INK,
        lw=1.8,
        zorder=3,
        gid="alternative",
        label="if the true gap were Y",
    )
    ax.axvline(line, color=LOST, lw=1.3, ls="--", gid="line")
    ax.axhline(0, color=MUTED, lw=0.9, gid="zero")
    ax.plot([gap], [0], "D", color=LOST, ms=8, zorder=5, clip_on=False, gid="estimate")

    ax.annotate(
        f"5 percent line, {line:.4f}",
        (line, top * LINE_LABEL[1]),
        xytext=(line + LINE_LABEL[0], top * LINE_LABEL[1]),
        textcoords="data",
        ha="left",
        va="center",
        color=LOST,
        fontsize=9.5,
        gid="line-label",
    )
    peak = float(alternative.max())
    ax.annotate(
        f"Y, {y:.4f}, the gap a\n5 percent test finds\nfour times in five",
        (y, peak),
        xytext=(y + Y_LABEL[0] * se, top * Y_LABEL[1]),
        textcoords="data",
        ha="left",
        va="center",
        color=INK,
        fontsize=9.5,
        arrowprops=ARROW,
        gid="y-label",
    )
    ax.annotate(
        f"point estimate {gap:.4f},\nNewey-West t {c.t:.4f}",
        (gap, 0),
        xytext=(ESTIMATE_LABEL[0], top * ESTIMATE_LABEL[1]),
        textcoords="data",
        ha="left",
        va="center",
        color=LOST,
        fontsize=9.5,
        arrowprops={**ARROW, "color": LOST},
        gid="estimate-label",
    )

    ax.set_xlim(*GAP_LIMITS)
    ax.set_ylim(0, top)
    ax.xaxis.set_major_locator(MultipleLocator(0.1))
    ax.xaxis.set_major_formatter(lambda x, _pos: "0" if abs(x) < 1e-12 else signed(x, 1))
    ax.tick_params(axis="x", labelbottom=True)
    ax.yaxis.set_major_locator(NullLocator())
    ax.set_ylabel("density", color=INK, fontsize=10)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=INK)
    leverage = (
        f"a constant leverage of {c.ceiling:g}"
        if c.binds == c.months
        else f"a mean leverage of {c.mean_leverage:.4f}, capped in {c.binds} of {c.months} months"
    )
    _heading(
        ax,
        f"Ceiling {c.ceiling:g}, {leverage}. Standard error {se:.4f} a year.\n"
        f"The point estimate, {gap:.4f}, falls short of the 5 percent line at {line:.4f}.",
    )


@_plain_text
def make_low_beta_capped_figure(
    out=None, portfolios: Portfolios | None = None, sources=None
) -> Figure:
    """One panel per ceiling: the curves at 0 and at Y, the 5 percent line and the estimate."""
    sources = sources if sources is not None else read_sources()
    members, closes, spy_entry, spy, bill_entry, bills = sources
    p = portfolios if portfolios is not None else build_portfolios(closes, spy, bills)
    outcomes = assess(p)

    fig = Figure(figsize=(10, 10), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    axes = fig.subplots(len(outcomes), 1, sharex=True, gridspec_kw={"hspace": 0.42})
    for ax, outcome in zip(axes, outcomes, strict=True):
        _style(ax)
        _panel(ax, outcome)
    axes[-1].set_xlabel(
        "gap in compounded growth a year, capped low fifth less unlevered high fifth",
        color=INK,
        fontsize=10,
    )

    _title(
        fig,
        "Exploratory: neither capped gap reaches the line a 5 percent test draws",
        "Quantitative Trading, Kindle edition, p. 191, ceilings from pp. 16 and 112. "
        f"Stocks from {SOURCE_FILE}, saved "
        f"{members[0].obtained}, survivors only.\nSPY from {spy_entry.path}, saved "
        f"{spy_entry.obtained}, and FRED's TB3MS, downloaded {bill_entry.obtained}. "
        "Not a holdout.\nThe ceilings were chosen after Entry 45's figures were seen, and "
        "the standard error and the 5 percent line were drawn\nafter the run, so nothing here "
        "decides anything.",
    )
    fig.subplots_adjust(left=0.07, right=0.97, top=0.89, bottom=0.17)
    return _save(fig, out, LOW_BETA_CAPPED_FIGURE)


def main() -> None:
    try:
        make_low_beta_capped_figure()
    except VintageUnavailable as refused:
        # A refusal that names the source reaches the reader as one line, the
        # way chan.low_beta_capped.main does it.
        raise SystemExit(str(refused)) from refused
    print(f"wrote {FIGURES_DIR / LOW_BETA_CAPPED_FIGURE}")


if __name__ == "__main__":
    main()
