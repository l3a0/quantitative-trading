"""The GLD/GDX regime map, the one figure the write-up carries.

Section 6 of [blog/gld-gdx-cointegration-lessons.md](../../blog/gld-gdx-cointegration-lessons.md)
makes the claim that cointegration is a property of a window rather than of a
pair, and this is that claim as a picture. A rolling one-year CADF scan over
the full as-traded history, stepped monthly, with each window's t-statistic
drawn as a time series. Where the statistic dips below the 10% critical value
the pair cointegrates in that window. The lower panel tracks Chan's
through-origin hedge, which climbs from his 1.64 to well past 4 as the miners
detach from gold.

It reads the committed vintages through the same engine the replication uses,
so it fetches nothing and runs wherever the tests run. ``TestRollingRegime`` in
``tests/test_pair_cointegration.py`` pins the scan, and
``tests/test_regime_figure.py`` pins that this module draws that scan rather
than something else. A re-download that shifts the vintage moves the figure and
both sets of pins together.

Regenerate after any such change::

    uv run python -m chan.regime_figure

The committed PNG was drawn in the sibling repository the essay came from, and
this module is the port of the code that drew it. Redrawing it here produces a
visually identical figure and a different file, because a PNG carries the
matplotlib version that rendered it. So the test asserts the data behind the
picture rather than the bytes of it: a byte comparison would fail on a
matplotlib upgrade that changed nothing a reader can see.

Colours match the essay's palette, so the picture reads as part of it.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
from ithildincore.timeseries import EG_CRIT_N2
from matplotlib.figure import Figure

from chan.pair_cointegration import aligned_closes, rolling_cointegration
from chan.paths import FIGURES_DIR

# Essay palette, from the :root tokens in docs/gld-gdx-cointegration-lessons.html.
SURFACE = "#FEFDFA"  # figure ground
GROUND = "#F7F5EF"  # axes ground
INK = "#23201A"
MUTED = "#6B6353"
RULE = "#CFC8B4"
ACCENT = "#8B651A"  # brass -- the hedge line (WCAG-AA against the cream ground)
GOOD = "#4A7C59"  # green -- cointegrating windows
LOST = "#A24C3C"  # red -- critical lines / breakdown

REPRO_HEDGE = 1.6379  # the reproduced Chan through-origin hedge the essay quotes


def _style(ax) -> None:
    ax.set_facecolor(GROUND)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(RULE)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(True, color=RULE, lw=0.5, alpha=0.5)
    ax.set_axisbelow(True)


def make_regime_figure(out: Path | None = None) -> Figure:
    """Draw the two-panel GLD/GDX regime map and write it to ``out``.

    ``out`` defaults to the committed figure. A caller that passes a path
    elsewhere gets the same figure without touching it, which is what lets a
    test run the real drawing code.
    """
    df = aligned_closes("GLD", "GDX", unadjusted=True)
    a = df["GLD"].to_numpy(float)
    b = df["GDX"].to_numpy(float)
    scan = rolling_cointegration(a, b, window=252, step=21, lags=1)
    x = df.index[scan.end_idx]
    adf = scan.adf_stat
    hedge = scan.origin_hedge

    crit10 = EG_CRIT_N2["10%"]  # -3.04
    crit5 = EG_CRIT_N2["5%"]  # -3.34

    fig = Figure(figsize=(11, 7), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    gs = fig.add_gridspec(2, 1, height_ratios=[2.3, 1.0], hspace=0.18)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    _style(ax1)
    _style(ax2)

    # --- Panel A: rolling CADF t-statistic ---
    coint = adf < crit10
    labelled = False
    i = 0
    while i < len(coint):
        if coint[i]:
            j = i
            while j + 1 < len(coint) and coint[j + 1]:
                j += 1
            ax1.axvspan(
                x[i],
                x[min(j + 1, len(x) - 1)],
                color=GOOD,
                alpha=0.16,
                label="cointegrates (10%)" if not labelled else None,
            )
            labelled = True
            i = j + 1
        else:
            i += 1

    ax1.plot(x, adf, color=INK, lw=1.6, zorder=5)
    ax1.axhline(crit10, color=LOST, lw=1.1, ls="--", zorder=4)
    ax1.axhline(crit5, color=LOST, lw=1.1, ls=":", zorder=4)
    # Critical-line labels out in the right margin, at each line's level, so
    # they never cross the data.
    yt = ax1.get_yaxis_transform()
    ax1.text(
        1.012,
        crit10 + 0.04,
        "10% critical  −3.04",
        color=LOST,
        transform=yt,
        fontsize=8.5,
        va="bottom",
        ha="left",
    )
    ax1.text(
        1.012,
        crit5 - 0.04,
        "5% critical  −3.34",
        color=LOST,
        transform=yt,
        fontsize=8.5,
        va="top",
        ha="left",
    )
    ax1.tick_params(labelbottom=False)  # shared x-axis -- labels on the lower panel
    ax1.annotate(
        "Chan's 2006–07 window\n(t ≈ −3.18)",
        xy=(x[0], adf[0]),
        xytext=(x[6], -4.15),
        color=INK,
        fontsize=8.5,
        ha="left",
        va="center",
        arrowprops={"arrowstyle": "-", "color": MUTED, "lw": 0.8},
    )
    ax1.set_ylabel("rolling CADF t-statistic\n(1-year window)", color=INK, fontsize=10)
    ax1.set_title(
        "GLD / GDX cointegration is a property of the window, not the pair",
        color=INK,
        fontsize=13.5,
        loc="left",
        pad=12,
        fontweight="bold",
    )
    # Legend out in the right margin so it never sits over the data.
    ax1.legend(
        loc="upper left", bbox_to_anchor=(1.008, 1.0), frameon=False, fontsize=9, labelcolor=INK
    )

    # --- Panel B: the through-origin hedge drift ---
    ax2.plot(x, hedge, color=ACCENT, lw=1.6)
    ax2.axhline(REPRO_HEDGE, color=MUTED, lw=1.0, ls=":")
    ax2.text(
        x[-1],
        REPRO_HEDGE,
        "  reproduced Chan hedge 1.64",
        color=MUTED,
        fontsize=8.5,
        va="center",
        ha="left",
    )
    ax2.set_ylabel("through-origin\nhedge ratio", color=INK, fontsize=10)
    ax2.set_xlabel("window-end date", color=INK, fontsize=10)

    ax2.xaxis.set_major_locator(mdates.YearLocator(2))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax1.margins(x=0.01)

    path = out if out is not None else FIGURES_DIR / "reproduction_regime_map.png"
    fig.savefig(path, facecolor=SURFACE, bbox_inches="tight")
    return fig


def main() -> None:
    make_regime_figure()
    print(f"wrote {FIGURES_DIR / 'reproduction_regime_map.png'}")


if __name__ == "__main__":
    main()
