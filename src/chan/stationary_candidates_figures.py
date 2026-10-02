"""The stationary-candidates post's three figures, drawn from the committed vintages.

``blog/stationary-candidates-lessons.md`` teaches that one series and a fitted
pair are read against different bars, that checking a fit for leftover
autocorrelation moves its statistic, and that how often one-year windows
reject says little about the whole test period. The owner chose on 2026-10-02
to give each of those three lessons a figure.

:func:`make_bars_figure` draws the first as two number lines of t-statistics.

1. **One series.** The bars of the ADF with a constant, ``ADF_CRIT_CONST``,
   with the CAD/AUD rate's statistic at one lag and at the first lag count
   whose residuals pass.
2. **A fitted pair.** Engle-Granger's bars, ``EG_CRIT_N2``, with TLT and IEF's
   statistic in each orientation, and the rate's two statistics drawn again as
   hollow marks, read against the pair's bars.

:func:`make_lags_figure` draws the second as the statistic at every lag count
up to Schwert's ceiling, filled where the fit's residuals pass the check and
hollow where they fail, for the rate and for both orientations of the pair.

:func:`make_windows_figure` draws the third as the rolling scans the two
candidates already run: the rate's one-year windows against the bars for one
series, and both orientations of the pair against Engle-Granger's, with a dot
on each window that clears 10% and the result over the whole test period in
each panel's title. Issue 16 ruled out a picture of these scans because it
invites reading one window as a finding. The owner reversed that on
2026-10-02, after choosing the first figure. The figure's title, panel titles
and note say what the windows are not, which is the part of the objection it
can answer. The register row in ``docs/design.md`` records the ruling and both
reversals.

Every statistic comes from :func:`chan.stationary_candidates.cross_rate` and
:func:`chan.stationary_candidates.fixed_income`, so a figure can only be wrong
by drawing the wrong thing, which ``tests/test_stationary_candidates_figures.py``
checks. All three read the committed vintages, so they redraw anywhere the
data is::

    uv run python -m chan.stationary_candidates_figures
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.dates as mdates
import pandas as pd
from ithildincore.timeseries import ADF_CRIT_CONST, EG_CRIT_N2
from matplotlib.figure import Figure

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.pair_cointegration import ResidualCheck, residual_check
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED, RULE, SURFACE
from chan.series import WindowCrossesScaleBreak
from chan.stationary_candidates import (
    INTERMEDIATE,
    LONG,
    TEST_START,
    CrossRate,
    Orientation,
    cross_rate,
    fixed_income,
    residuals_pass,
)
from chan.vintage import VintageUnavailable

BARS_FIGURE = "stationary_candidates_bars.png"
WINDOWS_FIGURE = "stationary_candidates_windows.png"
LAGS_FIGURE = "stationary_candidates_lags.png"

#: The t-statistics the axis spans. The pair's 1% bar, -3.90, is the most
#: negative thing drawn and IEF on TLT, -2.3168, the least.
X_RANGE = (-4.1, -2.0)

#: Where each number line sits, the one series above the pair.
ONE_SERIES_Y, PAIR_Y = 1.0, 0.0

#: The order the bars are drawn and labelled in, most negative first.
LEVELS = ("1%", "5%", "10%")


@dataclass(frozen=True)
class Mark:
    """One statistic drawn on one number line."""

    gid: str
    x: float
    y: float
    colour: str
    hollow: bool
    label: str
    offset: tuple[float, float]


def _t(x: float, places: int = 4) -> str:
    """A t-statistic with a typographic minus, as the post prints it."""
    return f"{x:.{places}f}".replace("-", "−")


def marks(rate: CrossRate, orientations: tuple[Orientation, ...]) -> list[Mark]:
    """The six statistics the figure draws, in the order it draws them."""
    by = {o.dependent: o for o in orientations}
    one, passing = rate.adf_stat, rate.passing.adf_stat
    return [
        Mark("cadaud-1", one, ONE_SERIES_Y, GOOD, False, f"CAD/AUD, 1 lag\n{_t(one)}", (-12, -40)),
        Mark(
            "cadaud-passing",
            passing,
            ONE_SERIES_Y,
            GOOD,
            False,
            f"CAD/AUD, {rate.passing.lags} lags\n{_t(passing)}",
            (8, -40),
        ),
        Mark(
            "tlt-on-ief",
            by[LONG].fit.adf_stat,
            PAIR_Y,
            LOST,
            False,
            f"{LONG} on {INTERMEDIATE}\n{_t(by[LONG].fit.adf_stat)}",
            (-58, -40),
        ),
        Mark(
            "ief-on-tlt",
            by[INTERMEDIATE].fit.adf_stat,
            PAIR_Y,
            LOST,
            False,
            f"{INTERMEDIATE} on {LONG}\n{_t(by[INTERMEDIATE].fit.adf_stat)}",
            (6, -40),
        ),
        Mark("cadaud-1-as-pair", one, PAIR_Y, GOOD, True, "", (0, 0)),
        Mark(
            "cadaud-passing-as-pair",
            passing,
            PAIR_Y,
            GOOD,
            True,
            "CAD/AUD's two, read\nagainst these bars",
            (-86, -40),
        ),
    ]


def _line(ax, y: float, bars: dict[str, float], name: str) -> None:
    """One number line: the axis, the 5% region shaded, and three bars."""
    ax.plot(
        X_RANGE, (y, y), color=RULE, lw=1.4, solid_capstyle="butt", zorder=1, gid=f"axis-{name}"
    )
    ax.fill_between(
        (X_RANGE[0], bars["5%"]),
        y - 0.13,
        y + 0.13,
        color=GOOD,
        alpha=0.12,
        lw=0,
        gid=f"shade-{name}",
    )
    for level in LEVELS:
        x = bars[level]
        ax.plot(
            (x, x), (y - 0.16, y + 0.16), color=MUTED, lw=1.4, zorder=2, gid=f"bar-{name}-{level}"
        )
        ax.annotate(
            f"{level}\n{_t(x, 2)}",
            (x, y + 0.16),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            color=MUTED,
            fontsize=9.5,
        )


@_plain_text
def make_bars_figure(
    out: Path | None = None,
    rate: CrossRate | None = None,
    orientations: tuple[Orientation, ...] | None = None,
) -> Figure:
    """Both tables of bars, with the four headline statistics on them."""
    rate = rate if rate is not None else cross_rate()
    orientations = orientations if orientations is not None else fixed_income()[1]
    drawn = marks(rate, orientations)

    fig = Figure(figsize=(10, 5.6), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.subplots()
    _style(ax)
    ax.grid(False)
    ax.spines["left"].set_visible(False)

    _line(ax, ONE_SERIES_Y, ADF_CRIT_CONST, "adf")
    _line(ax, PAIR_Y, EG_CRIT_N2, "eg")

    for m in drawn:
        ax.plot(
            [m.x],
            [m.y],
            "o",
            ms=9,
            color=m.colour,
            mfc="none" if m.hollow else m.colour,
            mec=m.colour if m.hollow else SURFACE,
            mew=2,
            zorder=3,
            gid=f"mark-{m.gid}",
        )
        if m.label:
            ax.annotate(
                m.label,
                (m.x, m.y),
                xytext=m.offset,
                textcoords="offset points",
                color=INK,
                fontsize=9.5,
                linespacing=1.3,
            )

    ax.set_xlim(*X_RANGE)
    ax.set_ylim(PAIR_Y - 0.62, ONE_SERIES_Y + 0.55)
    ax.set_yticks(
        [ONE_SERIES_Y, PAIR_Y],
        ["one series,\nADF with a constant", "a fitted pair,\nEngle-Granger"],
    )
    ax.tick_params(axis="y", length=0, labelsize=10.5, labelcolor=INK)
    ax.set_xlabel(
        "t-statistic, where further left is stronger evidence of a stationary series or spread",
        color=INK,
        fontsize=10.5,
    )
    _title(
        fig,
        "CAD/AUD clears the one-series bar at 5%, and the same statistics fall short of the pair's",
        f"CADAUD=X, log of the rate, {TEST_START} to 2026-09-30. TLT and IEF raw closes, "
        "2002-07-30 to 2026-10-01. All downloaded 2026-10-02.\n"
        "Shaded: past the 5% bar. Hollow: CAD/AUD's two statistics read against the "
        "pair's bars, which pay for a fitted hedge ratio.",
    )
    fig.tight_layout(rect=(0, 0.08, 1, 0.95))
    fig.marks = drawn
    return _save(fig, out, BARS_FIGURE)


def _bar_lines(ax, table: dict[str, float], name: str) -> None:
    """The 10% and 5% bars as horizontal lines, labelled in the right margin."""
    # Above the 10% line and below the 5% one, so the two labels part even
    # where the lines sit close, the way the GLD/GDX regime map places them.
    for level, style, va in (("10%", "--", "bottom"), ("5%", ":", "top")):
        y = table[level]
        ax.axhline(y, color=LOST, lw=1.1, ls=style, zorder=4, gid=f"bar-{name}-{level}")
        ax.text(
            1.012,
            y,
            f"{level}  {_t(y, 2)}",
            color=LOST,
            transform=ax.get_yaxis_transform(),
            fontsize=8.5,
            va=va,
            ha="left",
        )


def _scan(ax, dates, stats, bar: float, colour: str, label: str, gid: str) -> None:
    """One rolling scan as a line, with a dot on each window past ``bar``.

    The dots take the line's own colour. The GLD/GDX regime map paints its
    rejecting windows green for "cointegrates", and a window past a bar here is
    exactly what the note says is not a finding, so the dots mark it without
    praising it."""
    ax.plot(dates, stats, color=colour, lw=1.4, zorder=5, label=label, gid=f"scan-{gid}")
    past = stats < bar
    ax.plot(
        dates[past],
        stats[past],
        "o",
        ms=4.5,
        color=colour,
        mec=SURFACE,
        mew=0.6,
        zorder=6,
        gid=f"clears-{gid}",
    )


@_plain_text
def make_windows_figure(
    out: Path | None = None,
    rate: CrossRate | None = None,
    fixed: tuple[pd.DataFrame, tuple[Orientation, ...]] | None = None,
) -> Figure:
    """The two candidates' rolling scans, one panel each, on one date axis."""
    rate = rate if rate is not None else cross_rate()
    closes, orientations = fixed if fixed is not None else fixed_income()
    by = {o.dependent: o for o in orientations}

    fig = Figure(figsize=(11, 7.4), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    top, bottom = fig.subplots(2, 1, sharex=True)
    for ax in (top, bottom):
        _style(ax)

    rate_dates = rate.log_rate.index[rate.scan.end_idx]
    _scan(top, rate_dates, rate.scan.adf_stat, ADF_CRIT_CONST["10%"], INK, "CAD/AUD", "cadaud")
    _bar_lines(top, ADF_CRIT_CONST, "adf")
    top.set_title(
        "CAD/AUD, one series. Over the whole test period the test rejects at 5%, "
        f"with t = {_t(rate.adf_stat)}.",
        color=INK,
        fontsize=11,
        loc="left",
    )

    pair_dates = closes.index[by[LONG].scan.end_idx]
    for leg, colour in ((LONG, INK), (INTERMEDIATE, ACCENT)):
        o = by[leg]
        _scan(
            bottom,
            pair_dates,
            o.scan.adf_stat,
            EG_CRIT_N2["10%"],
            colour,
            f"{o.dependent} on {o.independent}",
            f"{o.dependent.lower()}-on-{o.independent.lower()}",
        )
    _bar_lines(bottom, EG_CRIT_N2, "eg")
    bottom.set_title(
        "TLT and IEF, a fitted pair. Over the whole period it does not reject even at "
        f"10%: {_t(by[LONG].fit.adf_stat)} for TLT on IEF, "
        f"{_t(by[INTERMEDIATE].fit.adf_stat)} for IEF on TLT.",
        color=INK,
        fontsize=11,
        loc="left",
    )
    bottom.legend(
        loc="upper left", bbox_to_anchor=(1.008, 0.7), frameon=False, fontsize=9, labelcolor=INK
    )
    for ax in (top, bottom):
        ax.set_ylabel("one-year t-statistic", color=INK, fontsize=10)
    bottom.set_xlabel("date the one-year window ends", color=INK, fontsize=10)
    bottom.xaxis.set_major_locator(mdates.YearLocator(2))
    bottom.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    _title(
        fig,
        "How often one-year windows reject says little about the whole test period",
        "Windows of 252 trading days stepped by 21, one lag. Dots mark windows past the "
        f"10% bar.\nCADAUD=X, log of the rate, from {TEST_START}. TLT and IEF raw closes "
        "from 2002-07-30. All downloaded 2026-10-02.\nA window that clears a bar is one "
        "look at the data among many, not a finding about the candidate.",
    )
    fig.tight_layout(rect=(0, 0.09, 0.9, 0.95))
    return _save(fig, out, WINDOWS_FIGURE)


def lag_sweep(series, ceiling: int, regression: str) -> list[ResidualCheck]:
    """The fit and its residual check at every lag count from 0 to ``ceiling``.

    The same search :func:`chan.stationary_candidates.first_passing` runs, kept
    whole rather than stopped at the first pass, so the figure can show what
    the search walked past.
    """
    return [residual_check(series, lags, regression=regression) for lags in range(ceiling + 1)]


def _sweep(ax, checks: list[ResidualCheck], colour: str, label: str, gid: str) -> None:
    """One sweep as a line, with each lag count filled if it passes."""
    lags = [c.lags for c in checks]
    stats = [c.adf_stat for c in checks]
    ax.plot(lags, stats, color=colour, lw=1.1, zorder=4, label=label, gid=f"sweep-{gid}")
    for passed, face, name in ((True, colour, "pass"), (False, "none", "fail")):
        picked = [c for c in checks if residuals_pass(c) is passed]
        ax.plot(
            [c.lags for c in picked],
            [c.adf_stat for c in picked],
            "o",
            ms=5.5,
            color=colour,
            mfc=face,
            mec=colour,
            mew=1.2,
            zorder=5,
            gid=f"{name}-{gid}",
        )


def _first_pass(ax, checks: list[ResidualCheck], text: str, offset: tuple[float, float]) -> None:
    first = next(c for c in checks if residuals_pass(c))
    ax.annotate(
        text.format(lags=first.lags, t=_t(first.adf_stat)),
        (first.lags, first.adf_stat),
        xytext=offset,
        textcoords="offset points",
        color=INK,
        fontsize=9.5,
        arrowprops={"arrowstyle": "-", "color": MUTED, "lw": 0.8},
    )


@_plain_text
def make_lags_figure(
    out: Path | None = None,
    rate: CrossRate | None = None,
    orientations: tuple[Orientation, ...] | None = None,
) -> Figure:
    """The statistic at every lag count, filled where the residuals pass."""
    rate = rate if rate is not None else cross_rate()
    orientations = orientations if orientations is not None else fixed_income()[1]
    by = {o.dependent: o for o in orientations}
    rate_checks = lag_sweep(rate.log_rate.to_numpy(float), rate.ceiling, "c")
    pair_checks = {leg: lag_sweep(by[leg].fit.spread, by[leg].ceiling, "n") for leg in by}

    fig = Figure(figsize=(11, 7.4), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    top, bottom = fig.subplots(2, 1, sharex=True)
    for ax in (top, bottom):
        _style(ax)

    _sweep(top, rate_checks, INK, "CAD/AUD", "cadaud")
    _bar_lines(top, ADF_CRIT_CONST, "adf")
    _first_pass(top, rate_checks, "first count that passes: {lags} lags, {t}", (30, 48))
    top.set_title(
        f"CAD/AUD. The check shrinks the margin: every count up to {rate.ceiling} still "
        "rejects at 5%.",
        color=INK,
        fontsize=11,
        loc="left",
    )

    for leg, colour, offset in ((LONG, INK, (-250, -78)), (INTERMEDIATE, ACCENT, (-250, -98))):
        o = by[leg]
        name = f"{o.dependent} on {o.independent}"
        _sweep(
            bottom,
            pair_checks[leg],
            colour,
            name,
            f"{o.dependent.lower()}-on-{o.independent.lower()}",
        )
        _first_pass(bottom, pair_checks[leg], name + ", first passes at {lags} lags, {t}", offset)
    _bar_lines(bottom, EG_CRIT_N2, "eg")
    bottom.set_title(
        "TLT and IEF. The check strengthens the finding: the first fits that pass sit "
        "further from the bar.",
        color=INK,
        fontsize=11,
        loc="left",
    )
    bottom.legend(
        loc="upper left", bbox_to_anchor=(1.008, 0.55), frameon=False, fontsize=9, labelcolor=INK
    )
    for ax in (top, bottom):
        ax.set_ylabel("t-statistic", color=INK, fontsize=10)
    bottom.set_xlabel(
        "lag count, the number of earlier changes the ADF includes", color=INK, fontsize=10
    )

    _title(
        fig,
        "Checking each fit for leftover autocorrelation moves the statistic",
        "Each dot is one ADF fit over the whole test period. Filled: its residuals pass "
        "both halves of the check, a Breusch-Godfrey p-value above 0.10\n"
        "and all ten autocorrelations inside ±1.96/√n. Hollow: they fail. "
        "The search stops at Schwert's ceiling, rounded up as statsmodels rounds it.",
    )
    fig.tight_layout(rect=(0, 0.07, 0.9, 0.95))
    return _save(fig, out, LAGS_FIGURE)


def main() -> None:
    try:
        rate, fixed = cross_rate(), fixed_income()
        make_bars_figure(rate=rate, orientations=fixed[1])
        make_windows_figure(rate=rate, fixed=fixed)
        make_lags_figure(rate=rate, orientations=fixed[1])
    except (VintageUnavailable, WindowCrossesScaleBreak) as refusal:
        # The two refusals `chan.stationary_candidates.main` prints. This module
        # reads the same three vintages through the same two calls, so it
        # catches them the same way rather than ending in a traceback.
        raise SystemExit(str(refusal)) from refusal
    print(f"wrote {FIGURES_DIR / BARS_FIGURE}")
    print(f"wrote {FIGURES_DIR / WINDOWS_FIGURE}")
    print(f"wrote {FIGURES_DIR / LAGS_FIGURE}")


if __name__ == "__main__":
    main()
