"""What each ADF lag count leaves in the residuals, on Chan's Chapter 3 window.

The augmented Dickey-Fuller test adds lagged differences of the spread so that
what is left over has no autocorrelation. Its critical values assume exactly
that, so a lag count that leaves autocorrelation behind reads its statistic
against a table that does not apply, and the test's real rejection rate is not
the one it states. ``TestLagSettingDetour`` in
``tests/test_pair_cointegration.py`` pins the statistic at every lag count from
0 to 16 and shows that the lag count decides the verdict. This figure asks
which of those lag counts the test is entitled to.

Each panel is one fixed-lag ADF fit on the Chapter 3 residual spread, checked
by :func:`chan.pair_cointegration.residual_check`. The bars are the
autocorrelations of that fit's residuals at lags 1 to
:data:`~chan.pair_cointegration.RESIDUAL_LAGS`, the shaded band is
``±1.96/√n`` around zero, and a bar outside it is drawn in the breakdown colour
with its value printed. Each panel's title carries the ADF statistic and the
p-value of a Breusch-Godfrey test on the same residuals.

The picture shows which lag is missing, which a p-value cannot. A single
autocorrelation at lag 6 survives every fit short of six lags, and the fit at
one lag, which is the lag Chan passed to ``cadf`` and the book's
specification, fails the Breusch-Godfrey test at 10%. This is exploratory: the
sample was spent looking, the band is pointwise, and a lag-6 autocorrelation
that sits just outside it on 250 observations is what a different vintage
could move inside.

It reads the committed vintages through the same code the replication uses, so
it fetches nothing. ``TestResidualCheck`` in
``tests/test_pair_cointegration.py`` pins what the check computes, and
``tests/test_lag_residual_figure.py`` pins that this module draws it.
Regenerate after any change that moves either::

    uv run python -m chan.lag_residual_figure

This module is not a port. The sibling ``trading-strategies`` repo draws a
similar bar chart, ``fig11_excess_acf`` in ``engine/make_figures.py`` at
``7a26498``, but over option P&L read out of that repo's own summary record.
The idea is the same and none of the code carries over.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from ithildincore.timeseries import EG_CRIT_N2
from matplotlib.figure import Figure

from chan.pair_cointegration import (
    BOOK_START,
    BOOK_TRAIN_END,
    RESIDUAL_LAGS,
    engle_granger,
    residual_check,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import GROUND, INK, LOST, MUTED, RULE, SURFACE
from chan.series import WindowCrossesScaleBreak, aligned_closes, vintage_line
from chan.vintage import VintageUnavailable

FIGURE_NAME = "adf_residual_autocorrelation.png"

#: The lag counts drawn, one panel each. 0 and 1 are the two that reject, 2
#: and 3 are the two nearest that do not, and 6 is the first whose residuals
#: pass, which is also the count ``autolag='aic'`` picks.
LAG_COUNTS = (0, 1, 2, 3, 6)


def _signed(x: float, places: int) -> str:
    """A number with a typographic minus, the way the essay prints one."""
    return f"{x:+.{places}f}".replace("-", "−")


def make_lag_residual_figure(out: Path | None = None, data_dir: Path | None = None) -> Figure:
    """Draw one residual panel per entry of :data:`LAG_COUNTS` and write it to ``out``.

    ``out`` defaults to the committed figure and ``data_dir`` to
    :data:`chan.paths.DATA_DIR`, for the reasons
    :func:`chan.regime_figure.make_regime_figure` gives. The returned figure
    carries the two resolved entries on ``vintages`` and the checks it drew on
    ``checks``.
    """
    df = aligned_closes(
        "GLD", "GDX", start=BOOK_START, end=BOOK_TRAIN_END, unadjusted=True, data_dir=data_dir
    )
    a = df["GLD"].to_numpy(float)
    b = df["GDX"].to_numpy(float)
    spread = engle_granger(a, b, lags=1).spread
    checks = tuple(residual_check(spread, k) for k in LAG_COUNTS)
    crit10 = EG_CRIT_N2["10%"]

    fig = Figure(figsize=(15, 4.9), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    axes = fig.subplots(1, len(checks), sharey=True)
    residual_lags = np.arange(1, RESIDUAL_LAGS + 1)

    for ax, check in zip(axes, checks, strict=True):
        ax.set_facecolor(GROUND)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(RULE)
        ax.tick_params(colors=MUTED, labelsize=9)

        ax.axhspan(-check.band, check.band, color=RULE, alpha=0.45, lw=0, zorder=0)
        ax.axhline(0, color=MUTED, lw=0.9, zorder=1)
        outside = np.abs(check.autocorrelation) > check.band
        ax.bar(
            residual_lags,
            check.autocorrelation,
            width=0.5,
            color=[LOST if o else MUTED for o in outside],
            zorder=2,
        )
        for lag, r in zip(residual_lags[outside], check.autocorrelation[outside], strict=True):
            ax.annotate(
                _signed(r, 2),
                (lag, r),
                xytext=(0, 4 if r > 0 else -4),
                textcoords="offset points",
                ha="center",
                va="bottom" if r > 0 else "top",
                fontsize=9,
                color=INK,
                fontweight="bold",
            )

        verdict = "rejects at 10%" if check.adf_stat < crit10 else "does not reject"
        noun = "lag" if check.lags == 1 else "lags"
        ax.set_title(
            f"{check.lags} {noun}\n"
            f"ADF t {_signed(check.adf_stat, 2)}, {verdict}\n"
            f"Breusch-Godfrey p = {check.breusch_godfrey_p:.3f}",
            color=INK,
            fontsize=10,
            loc="left",
        )
        ax.set_xticks(residual_lags)
        ax.set_xlabel("residual lag", color=INK, fontsize=9.5)
        ax.set_ylim(-0.22, 0.26)

    axes[0].set_ylabel("autocorrelation of the ADF residuals", color=INK, fontsize=10)
    fig.suptitle(
        "A lag-6 autocorrelation survives every fit until the ADF regression includes a sixth lag",
        x=0.01,
        ha="left",
        color=INK,
        fontsize=13.5,
        fontweight="bold",
    )
    fig.text(
        0.01,
        0.01,
        "Exploratory. GLD/GDX raw closes, 2006-05-23 to 2007-05-23, with-intercept Engle-Granger "
        "spread, ADF at a fixed lag count with no deterministic term. Shaded band: ±1.96/√n. "
        "Red bars fall outside it.",
        color=MUTED,
        fontsize=8.5,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))

    path = out if out is not None else FIGURES_DIR / FIGURE_NAME
    fig.savefig(path, facecolor=SURFACE)
    fig.vintages = df.attrs["vintages"]
    fig.checks = checks
    return fig


def main() -> None:
    try:
        figure = make_lag_residual_figure()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refusal:
        # The same two refusals every other command that reads the pair turns
        # into a line.
        raise SystemExit(str(refusal)) from refusal
    for entry in figure.vintages:
        print(f"{entry.symbol} vintage: {vintage_line(entry)}")
    print(f"wrote {FIGURES_DIR / FIGURE_NAME}")


if __name__ == "__main__":
    main()
