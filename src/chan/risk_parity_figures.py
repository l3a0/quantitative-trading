"""Seven figures for the risk parity post, drawn from the committed SPY and AGG vintages.

1. :func:`make_risk_split_figure` draws Qian's premise, that 60/40 splits
   capital 60 to 40 and risk nowhere near it, on the full common span. It has
   four bars.

   1. 60/40's capital split.
   2. 60/40's risk split, where the equity leg carries nearly all of it.
   3. Risk parity's capital split, which moves most of the capital into bonds.
   4. Risk parity's risk split, which is even.

2. :func:`make_claim_figure` draws Lesson 1 of
   ``blog/risk-parity-against-60-40.md``. Risk parity's stock weight and
   leverage land close to Qian's, while the Sharpe ratio comparison he printed
   them to support does not. Its Sharpe panel has three rows: Qian's own pair,
   then this run's pair at the average bill rate and at the 4 percent rate the
   rest of the post assumes.
3. :func:`make_hurdle_figure` draws Lesson 2. Risk parity leads exactly when
   bonds' Sharpe ratio, as a multiple of stocks', clears a hurdle that
   :func:`chan.risk_parity.bond_sharpe_hurdle` computes from the two
   volatilities and the correlation. It draws the same three rows as the
   second figure, each with its hurdle and where bonds landed.
4. :func:`make_decode_figure` draws Lesson 3. Qian's 23-77 stands for a
   volatility ratio and his 1.8 for a correlation. One panel sets the ratios
   his rounded weights allow beside the ratio from his paper and SPY and
   AGG's over the whole period and on each side of 2022. The other draws the
   leverage that matches 60/40 against the correlation, with the band of
   correlations his rounding allows.
5. :func:`make_rate_figure` draws Lesson 4. Risk parity's Sharpe ratio less
   60/40's, against the assumed cash rate, with the tie, the rates at which
   the data can tell the two apart, and three marked rates: zero, the bill
   average and the 4 percent the post assumes.
6. :func:`make_window_figure` draws Lesson 5. The Sharpe ratios of 60/40 and
   levered risk parity over the whole period, before the 2022 rise and after
   it, as :func:`chan.risk_parity.rank_the_windows` ranks them, with the later
   period also on weights fitted to it with hindsight. The later period's row
   gives the t-statistic at its own leverage and at the earlier period's.

7. :func:`make_correlation_figure` draws Lesson 6. After the 2022 rise, the
   hurdle bonds' Sharpe ratio had to clear, drawn against the stock-bond
   correlation for weights fitted to the period and for the weights carried
   from before, beside AGG's actual ratio to SPY's. It meets the first curve
   only near a correlation of −0.96 and never meets the second.

Every number this run measured comes from :mod:`chan.risk_parity`, so a figure
can only be wrong by drawing the wrong thing, which
``tests/test_risk_parity_figures.py`` checks. Qian's numbers are the ones his
paper prints and are drawn as printed. All seven read the committed vintages,
so they redraw anywhere the data is::

    uv run python -m chan.risk_parity_figures
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import pandas as pd
from ithildincore.stats import newey_west_summary
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from matplotlib.ticker import FuncFormatter, PercentFormatter

from chan.bill_rates import average as bill_average
from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, MUTED, RULE, SURFACE
from chan.risk_parity import (
    BENCHMARK_WEIGHTS,
    BOND,
    BOOK_LEVERAGE,
    BOOK_LEVERAGE_ROUNDING,
    BOOK_RATIO_BAND,
    BOOK_WEIGHT_ROUNDING,
    BOOK_WEIGHTS,
    RISK_FREE,
    STOCK,
    WINDOWS,
    Ranking,
    WindowResult,
    bond_sharpe_hurdle,
    book_correlation_band,
    correlation_from_leverage,
    hurdle_for_weights,
    hurdle_rate,
    leg_sharpes,
    leverage_from_correlation,
    measure_window,
    portfolio_excess_returns,
    rank_at_matched_volatility,
    rank_the_windows,
)
from chan.series import aligned_closes

SPLIT_FIGURE = "risk_parity_capital_and_risk.png"
CLAIM_FIGURE = "risk_parity_against_qian.png"
HURDLE_FIGURE = "risk_parity_bond_hurdle.png"
DECODE_FIGURE = "risk_parity_ratio_and_correlation.png"
RATE_FIGURE = "risk_parity_cash_rate.png"
WINDOW_FIGURE = "risk_parity_by_window.png"
CORRELATION_FIGURE = "risk_parity_hurdle_by_correlation.png"

#: Qian's Sharpe ratios for 60/40 and for levered risk parity, Table 2 of
#: ``research/papers/qian-2005-risk-parity-portfolios.pdf``. Monthly returns on
#: the Russell 1000 and the Lehman Aggregate from 1983 to 2004, above the
#: Treasury-bill rate. Printed to two decimals, and drawn as printed.
QIAN_SHARPE_BENCHMARK = 0.67
QIAN_SHARPE_PARITY = 0.87

#: Qian's two legs over the same sample, from the same paper. The volatilities
#: and the correlation are on page 1, and the volatilities again in Table 2's
#: standard deviation row. The two Sharpe
#: ratios are Table 2's Russell 1000 and Lehman Aggregate columns.
QIAN_STOCK_VOL = 0.151
QIAN_BOND_VOL = 0.046
QIAN_CORRELATION = 0.2
QIAN_SHARPE_STOCK = 0.55
QIAN_SHARPE_BOND = 0.80

#: The calendar months wholly inside the run's span, 2003-09-30 to 2026-09-17,
#: which is the window the bill average covers. A test holds them to the span.
BILL_MONTHS = ("2003-10", "2026-08")


def bill_average_rate() -> float:
    """The St. Louis Fed's three-month bill average over :data:`BILL_MONTHS`.

    Read from the committed TB3MS vintage through :mod:`chan.bill_rates` each
    time it is asked for, rather than bound at import, so a redirected
    ``chan.paths.DATA_DIR`` reaches it the way it reaches every other read.
    It is 1.744 percent, which the post quotes as 1.74.
    """
    return bill_average(*BILL_MONTHS)


#: A Sharpe ratio gap smaller than this draws no arrow, because the two dots
#: already touch and an arrowhead would have no room.
MIN_ARROW = 0.05

#: Where 60/40 sits in the weight and leverage panels, for reference.
BENCHMARK_STOCK_WEIGHT = BENCHMARK_WEIGHTS[0]
UNLEVERED = 1.0

#: A segment narrower than this carries its label outside the bar, because the
#: text does not fit inside it.
INSIDE_LABEL_MIN = 0.12


@dataclass(frozen=True)
class Bar:
    label: str
    stock: float
    bond: float


def full_span() -> WindowResult:
    """The decomposition on the full common span of the two vintages."""
    label, start, end = WINDOWS[0]
    result, _ = measure_window(label, aligned_closes(STOCK, BOND), start, end)
    return result


def split_bars(result: WindowResult) -> tuple[Bar, ...]:
    """The four bars, top to bottom: each portfolio's capital, then its risk."""
    bench, parity = result.benchmark, result.parity
    return (
        Bar("60/40, capital", bench.stock_weight, bench.bond_weight),
        Bar("60/40, risk", bench.stock_risk_share, bench.bond_risk_share),
        Bar("risk parity, capital", parity.stock_weight, parity.bond_weight),
        Bar("risk parity, risk", parity.stock_risk_share, parity.bond_risk_share),
    )


def _share(x: float) -> str:
    """A share to one decimal, or a whole number when the decimal is zero."""
    text = f"{x:.1%}"
    return text.replace(".0%", "%")


@_plain_text
def make_risk_split_figure(out: Path | None = None, result: WindowResult | None = None) -> Figure:
    """Capital and risk shares for 60/40 and risk parity, on the full span."""
    result = result if result is not None else full_span()
    bars = split_bars(result)
    # A gap between the two portfolios, so each pair reads as one group.
    rows = [4.0, 3.0, 1.4, 0.4]

    fig = Figure(figsize=(10, 5.2), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.subplots()
    _style(ax)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=RULE, lw=0.6, alpha=0.7)

    for y, bar in zip(rows, bars, strict=True):
        for left, width, colour, symbol in (
            (0.0, bar.stock, ACCENT, STOCK),
            (bar.stock, bar.bond, GOOD, BOND),
        ):
            ax.barh(y, width, left=left, height=0.72, color=colour, edgecolor=SURFACE, lw=2)
            text = f"{symbol} {_share(width)}"
            if width >= INSIDE_LABEL_MIN:
                ax.text(
                    left + width / 2,
                    y,
                    text,
                    ha="center",
                    va="center",
                    color=SURFACE,
                    fontsize=10.5,
                    fontweight="bold",
                )
            else:
                ax.annotate(
                    text,
                    (left + width, y),
                    xytext=(6, 0),
                    textcoords="offset points",
                    ha="left",
                    va="center",
                    color=INK,
                    fontsize=10.5,
                )

    ax.set_yticks(rows, [bar.label for bar in bars])
    ax.tick_params(axis="y", colors=INK, labelsize=10.5, length=0)
    ax.set_xlim(0, 1.09)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.legend(
        handles=[
            Patch(color=ACCENT, label=f"stocks, {STOCK}"),
            Patch(color=GOOD, label=f"bonds, {BOND}"),
        ],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.1),
        ncol=2,
        frameon=False,
        fontsize=10,
        labelcolor=INK,
    )
    legs = result.legs
    _title(
        fig,
        f"60/40 puts {_share(result.benchmark.stock_weight)} of the capital and "
        f"{_share(result.benchmark.stock_risk_share)} of the risk in stocks",
        f"{STOCK} and {BOND}, {legs.start} to {legs.end}, downloaded in 2026. A leg's share of "
        "risk is its share of the portfolio's variance.\n"
        f"Risk parity weights each leg by the inverse of its volatility, {legs.stock_vol:.2%} "
        f"for {STOCK} and {legs.bond_vol:.2%} for {BOND}, which splits the risk evenly.",
    )
    fig.tight_layout(rect=(0, 0.08, 1, 0.95))
    fig.bars = bars
    return _save(fig, out, SPLIT_FIGURE)


@dataclass(frozen=True)
class SharpePair:
    """One row of the Sharpe panel: 60/40's ratio, risk parity's, and the t."""

    label: str
    benchmark: float
    parity: float
    t: float | None

    @property
    def gap(self) -> float:
        return self.parity - self.benchmark


@dataclass(frozen=True)
class Claim:
    """What the claim figure draws, so a test can read it without the axes."""

    stock_weight: float
    leverage: float
    start: str
    end: str
    pairs: tuple[SharpePair, ...]


def full_span_ranking(risk_free: float) -> Ranking:
    """The full span ranked at matched volatility, on its own weights, at one rate."""
    label, start, end = WINDOWS[0]
    result, returns = measure_window(
        label, aligned_closes(STOCK, BOND), start, end, risk_free=risk_free
    )
    weights = (result.parity.stock_weight, result.parity.bond_weight)
    return rank_at_matched_volatility(
        label, returns, weights, weight_source=label, in_sample=True, risk_free=risk_free
    )


def claim(result: WindowResult | None = None) -> Claim:
    """Qian's printed figures beside this run's, on the full span."""
    result = result if result is not None else full_span()
    at_bills = full_span_ranking(bill_average_rate())
    at_rate = full_span_ranking(RISK_FREE)
    return Claim(
        stock_weight=result.parity.stock_weight,
        leverage=at_rate.leverage,
        start=result.legs.start,
        end=result.legs.end,
        pairs=(
            SharpePair(
                "Qian, 1983 to 2004, cash at each month's bill rate",
                QIAN_SHARPE_BENCHMARK,
                QIAN_SHARPE_PARITY,
                None,
            ),
            SharpePair(
                f"{STOCK} and {BOND}, 2003 to 2026, cash at the {bill_average_rate():.2%} "
                "bill average",
                at_bills.sharpe_benchmark,
                at_bills.sharpe_parity,
                at_bills.t_newey_west,
            ),
            SharpePair(
                f"{STOCK} and {BOND}, 2003 to 2026, cash at an assumed {RISK_FREE:.0%}",
                at_rate.sharpe_benchmark,
                at_rate.sharpe_parity,
                at_rate.t_newey_west,
            ),
        ),
    )


def _signed(x: float, digits: int = 2) -> str:
    """A number with a typographic minus, so the label matches the post."""
    return f"{x:.{digits}f}".replace("-", "−")


def gap_text(pair: SharpePair) -> str:
    """Which portfolio leads and by how much, with the t where one was measured."""
    leader = "risk parity" if pair.gap > 0 else "60/40"
    text = f"{leader} ahead by {abs(pair.gap):.2f}"
    if pair.t is not None:
        text += f", t = {_signed(pair.t)}"
    return text


def _side_label(ax, x: float, y: float, text: str, *, right: bool) -> None:
    ax.annotate(
        text,
        (x, y),
        xytext=(9 if right else -9, 0),
        textcoords="offset points",
        ha="left" if right else "right",
        va="center",
        color=INK,
        fontsize=10,
    )


def _reference(ax, x: float, text: str) -> None:
    """A dashed line marking where 60/40 sits, labelled at the top."""
    ax.axvline(x, color=MUTED, lw=1, ls="--", zorder=1)
    ax.annotate(
        text,
        (x, 1.0),
        xycoords=("data", "axes fraction"),
        xytext=(5, -2),
        textcoords="offset points",
        ha="left",
        va="top",
        color=MUTED,
        fontsize=9,
    )


def _dot_panel(ax, values: tuple[str, str], positions: tuple[float, float], title: str) -> None:
    """Risk parity's value for Qian and for this run, one dot each."""
    _style(ax)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=RULE, lw=0.6, alpha=0.7)
    rows = (1.0, 0.0)
    for y, x, text in zip(rows, positions, values, strict=True):
        ax.plot([x], [y], "o", ms=9, color=ACCENT, zorder=3)
        _side_label(ax, x, y, text, right=True)
    ax.set_yticks(rows, ["Qian", f"{STOCK} and {BOND}"])
    ax.tick_params(axis="y", colors=INK, labelsize=10, length=0)
    ax.set_ylim(-0.6, 1.9)
    ax.set_title(title, loc="left", color=INK, fontsize=10.5, fontweight="bold")


@_plain_text
def make_claim_figure(out: Path | None = None, result: WindowResult | None = None) -> Figure:
    """Weight and leverage beside Qian's, then the Sharpe ratios they were meant to win."""
    drawn = claim(result)

    fig = Figure(figsize=(10, 6.7), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    grid = fig.add_gridspec(2, 2, width_ratios=(1, 1.45), hspace=0.75, wspace=0.12)
    weight_ax = fig.add_subplot(grid[0, 0])
    leverage_ax = fig.add_subplot(grid[1, 0])
    sharpe_ax = fig.add_subplot(grid[:, 1])

    _dot_panel(
        weight_ax,
        (_share(BOOK_WEIGHTS[0]), _share(drawn.stock_weight)),
        (BOOK_WEIGHTS[0], drawn.stock_weight),
        "Risk parity's stock weight",
    )
    weight_ax.set_xlim(0, 1)
    weight_ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    weight_ax.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    _reference(weight_ax, BENCHMARK_STOCK_WEIGHT, f"60/40 holds {_share(BENCHMARK_STOCK_WEIGHT)}")

    _dot_panel(
        leverage_ax,
        (f"{BOOK_LEVERAGE:g}", f"{drawn.leverage:.2f}"),
        (BOOK_LEVERAGE, drawn.leverage),
        "Leverage to match 60/40's volatility",
    )
    leverage_ax.set_xlim(0, 2.5)
    leverage_ax.set_xticks([0, 0.5, 1.0, 1.5, 2.0, 2.5])
    leverage_ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _pos: f"{x:g}×"))
    _reference(leverage_ax, UNLEVERED, "60/40 is unlevered")

    _style(sharpe_ax)
    sharpe_ax.grid(axis="y", visible=False)
    sharpe_ax.grid(axis="x", color=RULE, lw=0.6, alpha=0.7)
    rows = [float(len(drawn.pairs) - 1 - i) for i in range(len(drawn.pairs))]
    for y, pair in zip(rows, drawn.pairs, strict=True):
        if abs(pair.gap) >= MIN_ARROW:
            sharpe_ax.annotate(
                "",
                xy=(pair.parity, y),
                xytext=(pair.benchmark, y),
                arrowprops={
                    "arrowstyle": "-|>",
                    "color": INK,
                    "lw": 1.6,
                    "shrinkA": 5,
                    "shrinkB": 5,
                    "mutation_scale": 13,
                },
                zorder=2,
            )
        sharpe_ax.plot([pair.parity], [y], "o", ms=9, color=ACCENT, zorder=3)
        sharpe_ax.plot([pair.benchmark], [y], "o", ms=9, mfc="none", mec=INK, mew=1.6, zorder=4)
        parity_right = pair.parity > pair.benchmark
        _side_label(sharpe_ax, pair.parity, y, f"{pair.parity:.2f}", right=parity_right)
        _side_label(sharpe_ax, pair.benchmark, y, f"{pair.benchmark:.2f}", right=not parity_right)
        sharpe_ax.text(0.0, y + 0.27, pair.label, ha="left", va="center", color=INK, fontsize=10)
        sharpe_ax.text(
            0.0, y - 0.25, gap_text(pair), ha="left", va="center", color=MUTED, fontsize=9.5
        )
    sharpe_ax.set_yticks([])
    sharpe_ax.set_ylim(-0.65, len(drawn.pairs) - 0.35)
    sharpe_ax.set_xlim(0, 1.0)
    sharpe_ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    sharpe_ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _pos: f"{x:.1f}"))
    sharpe_ax.set_title(
        "Sharpe ratio, from 60/40 to levered risk parity",
        loc="left",
        color=INK,
        fontsize=10.5,
        fontweight="bold",
    )
    sharpe_ax.legend(
        handles=[
            Line2D(
                [], [], ls="none", marker="o", ms=9, mfc="none", mec=INK, mew=1.6, label="60/40"
            ),
            Line2D([], [], ls="none", marker="o", ms=9, color=ACCENT, label="risk parity"),
        ],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.07),
        ncol=2,
        frameon=False,
        fontsize=10,
        labelcolor=INK,
    )

    _title(
        fig,
        "Risk parity's weight and leverage land close to Qian's, and its Sharpe ratio lead is gone",
        "Qian (2005), Table 2: Russell 1000 and Lehman Aggregate, monthly, 1983 to 2004.\n"
        f"{STOCK} and {BOND}: {drawn.start} to {drawn.end}, daily, downloaded in 2026. "
        f"{bill_average_rate():.2%} is the St. Louis Fed's average three-month bill rate\n"
        "(TB3MS) from October 2003 to August 2026, from the series committed with the "
        "replication's data.\n"
        f"{RISK_FREE:.0%} is the cash rate Chan assumes elsewhere in the book, above what bills "
        "paid on average.\n"
        "t is the t-statistic of risk parity minus 60/40, corrected for day-to-day dependence "
        "(Newey-West).\nBeyond ±2, a gap that size arises by chance less than 5% of the time.",
    )
    fig.subplots_adjust(left=0.1, right=0.98, top=0.87, bottom=0.32)
    fig.claim = drawn
    return _save(fig, out, CLAIM_FIGURE)


@dataclass(frozen=True)
class HurdleRow:
    """One row of the hurdle figure: each leg's Sharpe ratio and the hurdle."""

    label: str
    stock_sharpe: float
    bond_sharpe: float
    hurdle: float
    #: Whether the inputs are a source's rounded figures, so the hurdle and the
    #: multiple carry less precision than the arithmetic prints.
    approximate: bool = False

    @property
    def ratio(self) -> float:
        """Bonds' Sharpe ratio as a multiple of stocks'."""
        return self.bond_sharpe / self.stock_sharpe

    @property
    def clears(self) -> bool:
        return self.ratio > self.hurdle

    @property
    def hurdle_text(self) -> str:
        if self.approximate:
            return f"hurdle about {Fraction(self.hurdle).limit_denominator(3)}"
        return f"hurdle {self.hurdle:.2f}"

    @property
    def ratio_text(self) -> str:
        return f"about {self.ratio:.2f}" if self.approximate else _signed(self.ratio)


def hurdle_rows(result: WindowResult | None = None) -> tuple[HurdleRow, ...]:
    """Qian's legs as printed, then this run's at the bill average and at 4%."""
    result = result if result is not None else full_span()
    legs = result.legs
    hurdle = bond_sharpe_hurdle(legs.stock_vol, legs.bond_vol, legs.correlation)
    rows = [
        HurdleRow(
            "Qian, 1983 to 2004, cash at each month's bill rate",
            QIAN_SHARPE_STOCK,
            QIAN_SHARPE_BOND,
            bond_sharpe_hurdle(QIAN_STOCK_VOL, QIAN_BOND_VOL, QIAN_CORRELATION),
            approximate=True,
        )
    ]
    for label, rate in (
        (f"cash at the {bill_average_rate():.2%} bill average", bill_average_rate()),
        (f"cash at an assumed {RISK_FREE:.0%}", RISK_FREE),
    ):
        stock, bond = leg_sharpes(legs, risk_free=rate)
        rows.append(HurdleRow(f"{STOCK} and {BOND}, 2003 to 2026, {label}", stock, bond, hurdle))
    return tuple(rows)


#: The hurdle figure's horizontal range, in multiples of stocks' Sharpe ratio.
HURDLE_XLIM = (-0.6, 1.7)


@_plain_text
def make_hurdle_figure(out: Path | None = None, result: WindowResult | None = None) -> Figure:
    """Where bonds' Sharpe ratio landed against the hurdle risk parity needs."""
    result = result if result is not None else full_span()
    rows = hurdle_rows(result)
    legs = result.legs

    fig = Figure(figsize=(10, 7.3), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.subplots()
    _style(ax)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=RULE, lw=0.6, alpha=0.7)

    left, right = HURDLE_XLIM
    ys = [float(len(rows) - 1 - i) for i in range(len(rows))]
    for y, row in zip(ys, rows, strict=True):
        ax.add_patch(
            Rectangle(
                (row.hurdle, y - 0.17), right - row.hurdle, 0.34, color=GOOD, alpha=0.16, lw=0
            )
        )
        ax.plot([row.hurdle, row.hurdle], [y - 0.24, y + 0.24], color=INK, lw=2.2, zorder=3)
        ax.annotate(
            row.hurdle_text,
            (row.hurdle, y - 0.24),
            xytext=(0, -3),
            textcoords="offset points",
            ha="center",
            va="top",
            color=INK,
            fontsize=9.5,
        )
        ax.plot([row.ratio], [y], "o", ms=10, color=ACCENT, zorder=4)
        _side_label(ax, row.ratio, y, row.ratio_text, right=row.ratio >= row.hurdle)
        ax.text(left + 0.02, y + 0.47, row.label, ha="left", va="center", color=INK, fontsize=10)
        ax.text(
            left + 0.02,
            y + 0.29,
            f"bonds {_signed(row.bond_sharpe)}, stocks {_signed(row.stock_sharpe)}",
            ha="left",
            va="center",
            color=MUTED,
            fontsize=9.5,
        )

    ax.axvline(1.0, color=MUTED, lw=1, ls="--", zorder=1)
    ax.annotate(
        "equal Sharpe ratios",
        (1.0, 1.0),
        xycoords=("data", "axes fraction"),
        xytext=(5, -2),
        textcoords="offset points",
        ha="left",
        va="top",
        color=MUTED,
        fontsize=9,
    )
    ax.axvline(0.0, color=RULE, lw=1.2, zorder=1)
    ax.set_xlim(left, right)
    ax.set_xticks([-0.5, 0.0, 0.5, 1.0, 1.5])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _pos: _signed(x, 1)))
    ax.set_xlabel("bonds' Sharpe ratio as a multiple of stocks'", color=INK, fontsize=10)
    ax.set_yticks([])
    ax.set_ylim(-0.6, len(rows) - 0.3)
    ax.legend(
        handles=[
            Line2D([], [], ls="none", marker="o", ms=10, color=ACCENT, label="where bonds landed"),
            Line2D([], [], color=INK, lw=2.2, label="hurdle"),
            Patch(color=GOOD, alpha=0.16, label="risk parity leads"),
        ],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.14),
        ncol=3,
        frameon=False,
        fontsize=10,
        labelcolor=INK,
    )

    _title(
        fig,
        "Qian's bonds cleared the hurdle, and AGG's fell short, narrowly at the bill average",
        "The hurdle is the multiple of stocks' Sharpe ratio at which levered risk parity and 60/40 "
        "earn the same\nSharpe ratio at the same volatility. It depends on the two volatilities "
        "and their correlation, not on the cash rate.\n"
        f"Qian's is computed here from his rounded inputs: stocks {QIAN_STOCK_VOL:.1%}, bonds "
        f"{QIAN_BOND_VOL:.1%}, correlation {QIAN_CORRELATION:g} (Qian, 2005).\n"
        f"{STOCK} and {BOND}: {legs.stock_vol:.2%} and {legs.bond_vol:.2%}, correlation "
        f"{_signed(legs.correlation, 4)}, {legs.start} to {legs.end}, downloaded in 2026. "
        "Each multiple\ndivides unrounded Sharpe ratios. AGG's multiple meets the hurdle with "
        f"cash at {hurdle_rate(legs):.2%}, the rate where the two Sharpe ratios tie.\n"
        f"{bill_average_rate():.2%} is the St. Louis Fed's average three-month bill rate, "
        "committed with the replication's data.\n"
        f"{RISK_FREE:.0%} is the rate Chan assumes when levering SPY, borrowed here.",
    )
    fig.subplots_adjust(left=0.03, right=0.98, top=0.9, bottom=0.41)
    fig.rows = rows
    return _save(fig, out, HURDLE_FIGURE)


@dataclass(frozen=True)
class RatioMark:
    """One row of the ratio panel: a source and the volatility ratio it gives."""

    label: str
    ratio: float
    #: The ratios a source's rounded volatilities allow, drawn as a bar in
    #: place of a dot, or ``None`` where the volatilities were measured here.
    span: tuple[float, float] | None = None

    @property
    def text(self) -> str:
        return f"about {self.ratio:.1f}" if self.span is not None else f"{self.ratio:.2f}"


@dataclass(frozen=True)
class LeveragePoint:
    """A point on a leverage curve: whose weights, the correlation and the leverage."""

    label: str
    stock_weight: float
    correlation: float
    leverage: float


@dataclass(frozen=True)
class Decoding:
    """What the decode figure draws, so a test can read it without the axes."""

    ratio_band: tuple[float, float]
    ratios: tuple[RatioMark, ...]
    qian: LeveragePoint
    run: LeveragePoint
    qian_printed_correlation: float
    correlation_band: tuple[float, float]
    #: The stock weights at the two ends of 23-77's rounding, and the two ends
    #: of 1.8's. The correlation band's edges are where those curves cross
    #: those leverages.
    rounding_weights: tuple[float, float]
    rounding_leverages: tuple[float, float]
    start: str
    end: str


#: Half the last printed digit of Qian's volatilities, 15.1% and 4.6%.
QIAN_VOL_ROUNDING = 0.0005


def qian_ratio_span() -> tuple[float, float]:
    """The volatility ratios Qian's rounded 15.1% and 4.6% allow."""
    return (
        (QIAN_STOCK_VOL - QIAN_VOL_ROUNDING) / (QIAN_BOND_VOL + QIAN_VOL_ROUNDING),
        (QIAN_STOCK_VOL + QIAN_VOL_ROUNDING) / (QIAN_BOND_VOL - QIAN_VOL_ROUNDING),
    )


def decoding(result: WindowResult | None = None) -> Decoding:
    """Qian's two printed figures read as the market properties they encode."""
    result = result if result is not None else full_span()
    joined = aligned_closes(STOCK, BOND)
    windows = {
        label: measure_window(label, joined, start, end)[0].legs for label, start, end in WINDOWS
    }
    implied = correlation_from_leverage(BOOK_LEVERAGE)
    if implied is None:
        raise ValueError("Qian's 1.8 solves to no correlation on his weights")
    legs = result.legs
    return Decoding(
        ratio_band=BOOK_RATIO_BAND,
        ratios=(
            RatioMark("Qian, 1983 to 2004", QIAN_STOCK_VOL / QIAN_BOND_VOL, span=qian_ratio_span()),
            RatioMark(f"{STOCK} and {BOND}, 2003 to 2026", legs.vol_ratio),
            RatioMark(f"{STOCK} and {BOND}, to March 2022", windows["falling rates"].vol_ratio),
            RatioMark(f"{STOCK} and {BOND}, from March 2022", windows["rising rates"].vol_ratio),
        ),
        qian=LeveragePoint("Qian's 23-77", BOOK_WEIGHTS[0], implied, BOOK_LEVERAGE),
        run=LeveragePoint(
            f"{STOCK} and {BOND}'s {_share(result.parity.stock_weight)}",
            result.parity.stock_weight,
            legs.correlation,
            full_span_ranking(RISK_FREE).leverage,
        ),
        qian_printed_correlation=QIAN_CORRELATION,
        correlation_band=book_correlation_band(),
        rounding_weights=(
            BOOK_WEIGHTS[0] - BOOK_WEIGHT_ROUNDING,
            BOOK_WEIGHTS[0] + BOOK_WEIGHT_ROUNDING,
        ),
        rounding_leverages=(
            BOOK_LEVERAGE - BOOK_LEVERAGE_ROUNDING,
            BOOK_LEVERAGE + BOOK_LEVERAGE_ROUNDING,
        ),
        start=legs.start,
        end=legs.end,
    )


#: The correlation range the leverage panel draws, and how finely.
DECODE_CORRELATIONS = (-0.4, 0.6)
CURVE_STEPS = 200


@_plain_text
def make_decode_figure(out: Path | None = None, result: WindowResult | None = None) -> Figure:
    """Qian's weights as a volatility ratio and his leverage as a correlation."""
    drawn = decoding(result)

    fig = Figure(figsize=(10, 6.6), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    grid = fig.add_gridspec(1, 2, width_ratios=(1, 1.1), wspace=0.28)
    ratio_ax = fig.add_subplot(grid[0, 0])
    curve_ax = fig.add_subplot(grid[0, 1])

    _style(ratio_ax)
    ratio_ax.grid(axis="y", visible=False)
    ratio_ax.grid(axis="x", color=RULE, lw=0.6, alpha=0.7)
    low, high = drawn.ratio_band
    span_low, span_high = drawn.ratios[0].span
    ratio_ax.axvspan(low, high, color=GOOD, alpha=0.16, lw=0)
    ratio_ax.annotate(
        "what 23-77 allows",
        ((low + high) / 2, 1.0),
        xycoords=("data", "axes fraction"),
        xytext=(0, -3),
        textcoords="offset points",
        ha="center",
        va="top",
        color=MUTED,
        fontsize=9,
    )
    rows = [float(len(drawn.ratios) - 1 - i) for i in range(len(drawn.ratios))]
    for y, mark in zip(rows, drawn.ratios, strict=True):
        if mark.span is None:
            ratio_ax.plot([mark.ratio], [y], "o", ms=9, color=ACCENT, zorder=3)
            _side_label(ratio_ax, mark.ratio, y, mark.text, right=True)
        else:
            ratio_ax.plot(
                list(mark.span), [y, y], color=ACCENT, lw=7, solid_capstyle="butt", zorder=3
            )
            _side_label(ratio_ax, mark.span[1], y, mark.text, right=True)
    ratio_ax.set_yticks(rows, [mark.label for mark in drawn.ratios])
    ratio_ax.tick_params(axis="y", colors=INK, labelsize=10, length=0)
    ratio_ax.set_ylim(-0.6, len(drawn.ratios) - 0.2)
    ratio_ax.set_xlim(2.5, 4.25)
    ratio_ax.set_xticks([2.5, 3.0, 3.5, 4.0])
    ratio_ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _pos: f"{x:g}×"))
    ratio_ax.set_title(
        "Weights: stocks' volatility over bonds'",
        loc="left",
        color=INK,
        fontsize=10.5,
        fontweight="bold",
    )

    _style(curve_ax)
    curve_ax.grid(axis="x", color=RULE, lw=0.6, alpha=0.7)
    band_low, band_high = drawn.correlation_band
    curve_ax.axvspan(band_low, band_high, color=GOOD, alpha=0.16, lw=0)
    curve_ax.annotate(
        "what 23-77 and 1.8 allow",
        ((band_low + band_high) / 2, 1.0),
        xycoords=("data", "axes fraction"),
        xytext=(0, -3),
        textcoords="offset points",
        ha="center",
        va="top",
        color=MUTED,
        fontsize=9,
    )
    left, right = DECODE_CORRELATIONS
    grid_points = [left + (right - left) * i / CURVE_STEPS for i in range(CURVE_STEPS + 1)]
    lev_low, lev_high = drawn.rounding_leverages
    curve_ax.axhspan(lev_low, lev_high, color=RULE, alpha=0.35, lw=0, zorder=0)
    curve_ax.annotate(
        "1.8's rounding",
        (left, (lev_low + lev_high) / 2),
        xytext=(5, 0),
        textcoords="offset points",
        ha="left",
        va="center",
        color=MUTED,
        fontsize=9,
    )
    for i, weight in enumerate(drawn.rounding_weights):
        curve_ax.plot(
            grid_points,
            [leverage_from_correlation(c, weights=(weight, 1.0 - weight)) for c in grid_points],
            color=INK,
            alpha=0.35,
            lw=0.9,
            zorder=1,
            label="ends of 23-77's rounding" if i == 0 else None,
        )
    for point, colour, style, value, offset in (
        (drawn.qian, INK, "-", f"{BOOK_LEVERAGE:g} at {_signed(drawn.qian.correlation)}", -1),
        (
            drawn.run,
            MUTED,
            "--",
            f"{drawn.run.leverage:.2f} at {_signed(drawn.run.correlation, 4)}",
            1,
        ),
    ):
        weights = (point.stock_weight, 1.0 - point.stock_weight)
        curve = [leverage_from_correlation(c, weights=weights) for c in grid_points]
        curve_ax.plot(
            grid_points,
            curve,
            color=colour,
            ls=style,
            lw=1.6,
            zorder=2,
            label=f"{point.label} weights",
        )
        curve_ax.plot([point.correlation], [point.leverage], "o", ms=9, color=ACCENT, zorder=4)
        curve_ax.annotate(
            value,
            (point.correlation, point.leverage),
            xytext=(9 * offset, 6 * offset),
            textcoords="offset points",
            ha="left" if offset > 0 else "right",
            va="bottom" if offset > 0 else "top",
            color=INK,
            fontsize=10,
        )
    curve_ax.axvline(drawn.qian_printed_correlation, color=MUTED, lw=1, ls=":", zorder=1)
    curve_ax.annotate(
        f"his paper prints {drawn.qian_printed_correlation:g}",
        (drawn.qian_printed_correlation, 0.85),
        xycoords=("data", "axes fraction"),
        xytext=(5, 0),
        textcoords="offset points",
        ha="left",
        va="center",
        color=MUTED,
        fontsize=9,
    )
    curve_ax.legend(loc="lower left", frameon=False, fontsize=9.5, labelcolor=INK)
    curve_ax.set_xlim(left, right)
    curve_ax.set_xticks([-0.4, -0.2, 0.0, 0.2, 0.4, 0.6])
    curve_ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _pos: _signed(x, 1)))
    curve_ax.set_ylim(1.5, 2.4)
    curve_ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _pos: f"{x:.1f}×"))
    curve_ax.set_xlabel("stock-bond correlation", color=INK, fontsize=10)
    curve_ax.set_title(
        "Leverage to match 60/40, by correlation",
        loc="left",
        color=INK,
        fontsize=10.5,
        fontweight="bold",
    )
    _title(
        fig,
        "Qian's weights stand for a volatility ratio, and his leverage for a correlation",
        "Risk parity sets each weight times its volatility equal, so 23-77 says stocks were "
        "77/23 times as volatile as bonds.\nWeights that round to 23 and 77 allow "
        f"{low:.2f} to {high:.2f}. Qian's (2005) {QIAN_STOCK_VOL:.1%} and "
        f"{QIAN_BOND_VOL:.1%} allow {span_low:.2f} to {span_high:.2f} once rounded.\n"
        "Given the weights, the leverage that matches 60/40 depends only on the correlation. "
        "The band's edges, "
        f"{_signed(band_low, 2)} and +{band_high:.2f},\nare where the faint curves cross the "
        "ends of 1.8's rounding. "
        "The split is the Federal Reserve's first rate rise of 2022, on 16 March.\n"
        f"{STOCK} and {BOND}: {drawn.start} to {drawn.end}, downloaded in 2026.",
    )
    fig.subplots_adjust(left=0.235, right=0.98, top=0.87, bottom=0.29)
    fig.decoding = drawn
    return _save(fig, out, DECODE_FIGURE)


@dataclass(frozen=True)
class RatePoint:
    """The comparison at one assumed cash rate."""

    rate: float
    gap: float
    t: float


@dataclass(frozen=True)
class RateLine:
    """What the rate figure draws, so a test can read it without the axes."""

    line: tuple[RatePoint, ...]
    marks: tuple[RatePoint, ...]
    tie: float
    settles_above: float
    start: str
    end: str


#: The cash rates the line runs across, and how finely.
RATE_RANGE = (0.0, 0.05)
RATE_STEPS = 50

#: Room left of a zero rate, so the dot marking it is not cut by the axis.
RATE_MARGIN = 0.0015

#: The t-statistic beyond which the data can tell the two portfolios apart.
T_BAR = 2.0


def _at(rate: float) -> RatePoint:
    ranking = full_span_ranking(rate)
    return RatePoint(rate, ranking.sharpe_difference, ranking.t_newey_west)


def rate_line(result: WindowResult | None = None) -> RateLine:
    """The whole period's comparison across assumed cash rates.

    Both the gap and its t-statistic move in a straight line with the rate,
    so the tie and the rate at which the t reaches the bar are each the root
    of a line through two of the computed points.
    """
    result = result if result is not None else full_span()
    low, high = RATE_RANGE
    line = tuple(_at(low + (high - low) * i / RATE_STEPS) for i in range(RATE_STEPS + 1))
    first, last = line[0], line[-1]
    gap_slope = (last.gap - first.gap) / (last.rate - first.rate)
    t_slope = (last.t - first.t) / (last.rate - first.rate)
    return RateLine(
        line=line,
        marks=(_at(0.0), _at(bill_average_rate()), _at(RISK_FREE)),
        tie=first.rate - first.gap / gap_slope,
        settles_above=first.rate + (-T_BAR - first.t) / t_slope,
        start=result.legs.start,
        end=result.legs.end,
    )


def rate_mark_text(point: RatePoint) -> str:
    """Which portfolio leads at a marked rate, by how much, and the t."""
    if point.rate == bill_average_rate():
        name = f"{point.rate:.2%} bill average"
    else:
        name = f"cash at {point.rate:.0%}"
    leader = "risk parity" if point.gap > 0 else "60/40"
    return f"{name}\n{leader} ahead by {abs(point.gap):.2f}, t = {point.t:+.2f}".replace("-", "−")


def _percent(x: float, _pos: object = None) -> str:
    return f"{x:.0%}"


@_plain_text
def make_rate_figure(out: Path | None = None, result: WindowResult | None = None) -> Figure:
    """The Sharpe ratio gap against the assumed cash rate, over the whole period."""
    drawn = rate_line(result)

    fig = Figure(figsize=(10, 6.0), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.subplots()
    _style(ax)
    ax.grid(axis="x", color=RULE, lw=0.6, alpha=0.7)

    low, high = RATE_RANGE
    ax.axvspan(drawn.settles_above, high, ymin=0.0, ymax=1.0, color=MUTED, alpha=0.12, lw=0)
    ax.annotate(
        f"the data names 60/40 the winner\nabove {drawn.settles_above:.2%}",
        (high, 1.0),
        xycoords=("data", "axes fraction"),
        xytext=(-6, -6),
        textcoords="offset points",
        ha="right",
        va="top",
        color=MUTED,
        fontsize=9.5,
    )
    ax.axhline(0.0, color=INK, lw=1, zorder=1)
    ax.text(low + 0.0008, 0.012, "risk parity leads", color=MUTED, fontsize=9.5, va="bottom")
    ax.text(low + 0.0008, -0.012, "60/40 leads", color=MUTED, fontsize=9.5, va="top")
    ax.plot(
        [p.rate for p in drawn.line], [p.gap for p in drawn.line], color=ACCENT, lw=2.2, zorder=2
    )
    ax.plot([drawn.tie], [0.0], "o", ms=9, mfc=SURFACE, mec=INK, mew=1.6, zorder=4)
    ax.annotate(
        f"tie at {drawn.tie:.2%}",
        (drawn.tie, 0.0),
        xytext=(8, 8),
        textcoords="offset points",
        ha="left",
        va="bottom",
        color=INK,
        fontsize=10,
    )
    placements = ((10, 6, "left", "bottom"), (-30, -42, "right", "top"), (-10, -8, "right", "top"))
    for point, (dx, dy, ha, va) in zip(drawn.marks, placements, strict=True):
        ax.plot([point.rate], [point.gap], "o", ms=9, color=ACCENT, zorder=4)
        ax.annotate(
            rate_mark_text(point),
            (point.rate, point.gap),
            xytext=(dx, dy),
            textcoords="offset points",
            ha=ha,
            va=va,
            color=INK,
            fontsize=10,
            linespacing=1.35,
            arrowprops={"arrowstyle": "-", "color": MUTED, "lw": 0.8, "shrinkB": 6}
            if point.rate == bill_average_rate()
            else None,
        )
    ax.set_xlim(low - RATE_MARGIN, high)
    ax.set_xticks([0.0, 0.01, 0.02, 0.03, 0.04, 0.05])
    ax.xaxis.set_major_formatter(FuncFormatter(_percent))
    ax.set_ylim(-0.33, 0.2)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _pos: _signed(y, 1)))
    ax.set_xlabel("assumed cash rate", color=INK, fontsize=10)
    ax.set_ylabel("risk parity's Sharpe ratio minus 60/40's", color=INK, fontsize=10)

    _title(
        fig,
        "The assumed cash rate decides which portfolio leads, and t passes "
        f"−{T_BAR:g} only above {drawn.settles_above:.2%}",
        f"{STOCK} and {BOND}, {drawn.start} to {drawn.end}, downloaded in 2026, both portfolios at "
        "the same volatility. The gap and its t-statistic\nmove in a straight line with the "
        "rate. The shading is where the t-statistic, corrected for day-to-day dependence, is "
        f"beyond −{T_BAR:g}.\n{bill_average_rate():.2%} is the St. Louis Fed's average three-month "
        "bill rate, committed with the replication's data.\n"
        f"{RISK_FREE:.0%} is the rate Chan assumes when levering SPY, borrowed here.",
    )
    fig.subplots_adjust(left=0.1, right=0.97, top=0.9, bottom=0.27)
    fig.rate_line = drawn
    return _save(fig, out, RATE_FIGURE)


@dataclass(frozen=True)
class WindowRow:
    """One row of the window figure: which weights, both Sharpe ratios, each t."""

    label: str
    stock_weight: float
    benchmark: float
    parity: float
    #: Each t-statistic beside the leverage it was measured at, the leverage
    #: that matches 60/40 inside the row's own years first. Empty where the
    #: post quotes no t.
    tests: tuple[tuple[float, float], ...]

    @property
    def gap(self) -> float:
        return self.parity - self.benchmark


@dataclass(frozen=True)
class WindowComparison:
    """What the window figure draws, so a test can read it without the axes.

    The rows run top to bottom: the whole period and the years before the rise,
    each on weights fitted to the same years, then the years after the rise on
    the earlier weights and on weights fitted to those years with hindsight.
    """

    rows: tuple[WindowRow, ...]
    start: str
    before_end: str
    after_start: str
    end: str

    @property
    def carried(self) -> WindowRow:
        return self.rows[2]

    @property
    def hindsight(self) -> WindowRow:
        return self.rows[3]

    @property
    def closed(self) -> float:
        """How much of the later gap fitting the weights with hindsight closes."""
        return self.hindsight.gap - self.carried.gap

    @property
    def closed_share(self) -> float:
        return self.closed / abs(self.carried.gap)


def measure_the_windows() -> dict[str, tuple[WindowResult, pd.DataFrame]]:
    """Every declared window's decomposition and returns, at the post's rate."""
    joined = aligned_closes(STOCK, BOND)
    return {label: measure_window(label, joined, start, end) for label, start, end in WINDOWS}


def _t_at_leverage(returns: pd.DataFrame, weights: tuple[float, float], leverage: float) -> float:
    """The robust t on the daily difference at a leverage the caller supplies.

    The same arithmetic as :func:`chan.risk_parity.rank_at_matched_volatility`
    with the leverage it measures inside the window swapped out, which is how
    ``tests/test_risk_parity.py`` reaches the post's −1.64. The only leverage
    passed here is the one the earlier years measured, so nothing is fitted.
    """
    parity = portfolio_excess_returns(returns, weights)
    bench = portfolio_excess_returns(returns, BENCHMARK_WEIGHTS)
    return newey_west_summary((leverage * parity - bench).to_numpy()).t_newey_west


def window_comparison(
    measured: dict[str, tuple[WindowResult, pd.DataFrame]] | None = None,
) -> WindowComparison:
    """The three declared windows as ranked, and the later one refitted with hindsight."""
    measured = measured if measured is not None else measure_the_windows()
    rankings = rank_the_windows(measured)
    earlier = rankings["falling rates"]
    whole, before, after = (measured[label][0] for label, _, _ in WINDOWS)
    _, after_returns = measured["rising rates"]
    carried = (before.parity.stock_weight, before.parity.bond_weight)
    own = (after.parity.stock_weight, after.parity.bond_weight)
    refitted = rank_at_matched_volatility(
        "rising rates", after_returns, own, weight_source="rising rates", in_sample=True
    )

    def ranked(label: str, weight: float, ranking: Ranking, extra=()) -> WindowRow:
        return WindowRow(
            label,
            weight,
            ranking.sharpe_benchmark,
            ranking.sharpe_parity,
            ((ranking.leverage, ranking.t_newey_west), *extra),
        )

    def stocks(weight: float) -> str:
        return f"{_share(weight)} stocks"

    rows = (
        ranked(
            "Whole period, 2003 to 2026, on weights fitted to the same years "
            f"({stocks(whole.parity.stock_weight)})",
            whole.parity.stock_weight,
            rankings["full span"],
        ),
        ranked(
            "Earlier period, 2003 to March 2022, on weights fitted to the same years "
            f"({stocks(before.parity.stock_weight)}, leverage {earlier.leverage:.2f})",
            before.parity.stock_weight,
            earlier,
        ),
        ranked(
            "Later period, March 2022 to 2026, on the weights carried from the earlier period "
            f"({stocks(carried[0])})",
            carried[0],
            rankings["rising rates"],
            extra=(
                (
                    earlier.leverage,
                    _t_at_leverage(after_returns, carried, earlier.leverage),
                ),
            ),
        ),
        WindowRow(
            "Later period, March 2022 to 2026, with hindsight, on weights fitted to the same "
            f"years ({stocks(own[0])})",
            own[0],
            refitted.sharpe_benchmark,
            refitted.sharpe_parity,
            (),
        ),
    )
    return WindowComparison(
        rows=rows,
        start=whole.legs.start,
        before_end=before.legs.end,
        after_start=after.legs.start,
        end=after.legs.end,
    )


#: The words for the share of the later gap hindsight closes, in quarters.
QUARTERS = {1: "a quarter", 2: "half", 3: "three-quarters"}


def quarter_words(share: float) -> str:
    """A share between an eighth and seven-eighths, to the nearest quarter."""
    quarters = round(share * 4)
    if quarters not in QUARTERS:
        raise ValueError(f"{share:.2f} rounds to no quarter the title can name")
    return QUARTERS[quarters]


def window_row_text(drawn: WindowComparison, row: WindowRow) -> str:
    """Which portfolio leads and by how much, with each t and its leverage."""
    leader = "risk parity" if row.gap > 0 else "60/40"
    text = f"{leader} ahead by {abs(row.gap):.2f}"
    if len(row.tests) == 1:
        text += f", t = {_signed(row.tests[0][1])}"
    elif row.tests:
        (own_leverage, own_t), (held, held_t) = row.tests
        text += (
            f", t = {_signed(own_t)} at leverage {own_leverage:.2f}, "
            f"and {_signed(held_t)} at {held:.2f}, carried from the earlier period"
        )
    if row is drawn.hindsight:
        text += f", so hindsight closes {drawn.closed:.2f} of the {abs(drawn.carried.gap):.2f}"
    return text


#: The window figure's horizontal range. It starts below zero so the label of
#: a Sharpe ratio near zero has room on its outer side.
WINDOW_XLIM = (-0.15, 0.7)


@_plain_text
def make_window_figure(
    out: Path | None = None,
    measured: dict[str, tuple[WindowResult, pd.DataFrame]] | None = None,
) -> Figure:
    """The Sharpe ratios on each side of March 2022, on carried and on hindsight weights."""
    drawn = window_comparison(measured)

    fig = Figure(figsize=(10, 7.4), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.subplots()
    _style(ax)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=RULE, lw=0.6, alpha=0.7)

    left, right = WINDOW_XLIM
    ys = [float(len(drawn.rows) - 1 - i) for i in range(len(drawn.rows))]
    for y, row in zip(ys, drawn.rows, strict=True):
        if abs(row.gap) >= MIN_ARROW:
            ax.annotate(
                "",
                xy=(row.parity, y),
                xytext=(row.benchmark, y),
                arrowprops={
                    "arrowstyle": "-|>",
                    "color": INK,
                    "lw": 1.6,
                    "shrinkA": 5,
                    "shrinkB": 5,
                    "mutation_scale": 13,
                },
                zorder=2,
            )
        ax.plot([row.parity], [y], "o", ms=9, color=ACCENT, zorder=3)
        ax.plot([row.benchmark], [y], "o", ms=9, mfc="none", mec=INK, mew=1.6, zorder=4)
        parity_right = row.parity > row.benchmark
        _side_label(ax, row.parity, y, f"{row.parity:.2f}", right=parity_right)
        _side_label(ax, row.benchmark, y, f"{row.benchmark:.2f}", right=not parity_right)
        ax.text(left + 0.005, y + 0.27, row.label, ha="left", va="center", color=INK, fontsize=10)
        ax.text(
            left + 0.005,
            y - 0.25,
            window_row_text(drawn, row),
            ha="left",
            va="center",
            color=MUTED,
            fontsize=9.5,
        )
    ax.set_yticks([])
    ax.set_ylim(-0.65, len(drawn.rows) - 0.35)
    ax.set_xlim(left, right)
    ax.set_xticks([0.0, 0.2, 0.4, 0.6])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _pos: f"{x:.1f}"))
    ax.set_xlabel("Sharpe ratio, from 60/40 to levered risk parity", color=INK, fontsize=10)
    ax.legend(
        handles=[
            Line2D(
                [], [], ls="none", marker="o", ms=9, mfc="none", mec=INK, mew=1.6, label="60/40"
            ),
            Line2D([], [], ls="none", marker="o", ms=9, color=ACCENT, label="risk parity"),
        ],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.1),
        ncol=2,
        frameon=False,
        fontsize=10,
        labelcolor=INK,
    )

    carried_leverage, _ = drawn.carried.tests[0]
    held_leverage, _ = drawn.carried.tests[1]
    _title(
        fig,
        "Risk parity trails most in the later period, and hindsight weights close only "
        f"about {quarter_words(drawn.closed_share)} of it",
        f"{STOCK} and {BOND}, {drawn.start} to {drawn.end}, daily, downloaded in 2026. The split "
        "is the Federal Reserve's first rate rise of 2022,\non 16 March, so the earlier period "
        f"runs to {drawn.before_end} and the later from {drawn.after_start}.\n"
        "Risk parity is levered to match 60/40's volatility. "
        f"In the later period, {carried_leverage:.2f} does that. "
        f"{held_leverage:.2f} matched the earlier period,\nand a trader on the day held it, "
        "carrying more risk.\n"
        "t is the Newey-West t-statistic of risk parity minus 60/40, corrected for day-to-day "
        f"dependence. Beyond ±{T_BAR:g}, a gap that size\narises by chance less than 5% of the "
        "time. Gaps are computed before rounding. "
        f"{RISK_FREE:.0%} is the cash rate throughout, the rate Chan\nassumes when levering SPY, "
        "borrowed here.",
    )
    fig.subplots_adjust(left=0.03, right=0.98, top=0.9, bottom=0.34)
    fig.comparison = drawn
    return _save(fig, out, WINDOW_FIGURE)


@dataclass(frozen=True)
class CorrelationCurves:
    """What the correlation figure draws, so a test can read it without the axes."""

    correlations: tuple[float, ...]
    fitted: tuple[float, ...]
    carried: tuple[float, ...]
    fitted_stock_weight: float
    carried_stock_weight: float
    agg_ratio: float
    measured: tuple[tuple[str, float], ...]
    fitted_at_measured: float
    carried_at_measured: float
    turns_negative: float
    meets_agg: float
    carried_floor: float
    stock_vol: float
    bond_vol: float
    start: str
    end: str


#: The correlations the curves run across. The curve on weights fitted to the
#: period divides by zero at exactly −1, where its volatility vanishes, so the
#: range stops just short of it.
CORRELATION_RANGE = (-0.995, 0.5)
CORRELATION_STEPS = 300


def _root(f, low: float, high: float) -> float:
    """Where ``f`` crosses zero between two correlations it brackets."""
    for _ in range(200):
        mid = (low + high) / 2
        if (f(low) < 0) == (f(mid) < 0):
            low = mid
        else:
            high = mid
    return (low + high) / 2


def correlation_curves() -> CorrelationCurves:
    """The later period's hurdle across correlations, on both sets of weights."""
    joined = aligned_closes(STOCK, BOND)
    measured_windows = {
        label: measure_window(label, joined, start, end)[0] for label, start, end in WINDOWS
    }
    late = measured_windows["rising rates"]
    legs = late.legs
    fitted_w = (late.parity.stock_weight, late.parity.bond_weight)
    early = measured_windows["falling rates"].parity
    carried_w = (early.stock_weight, early.bond_weight)

    def fitted(rho: float) -> float:
        return hurdle_for_weights(fitted_w, legs.stock_vol, legs.bond_vol, rho)

    def carried(rho: float) -> float:
        return hurdle_for_weights(carried_w, legs.stock_vol, legs.bond_vol, rho)

    stock, bond = leg_sharpes(legs)
    agg = bond / stock
    low, high = CORRELATION_RANGE
    grid = tuple(low + (high - low) * i / CORRELATION_STEPS for i in range(CORRELATION_STEPS + 1))
    return CorrelationCurves(
        correlations=grid,
        fitted=tuple(fitted(rho) for rho in grid),
        carried=tuple(carried(rho) for rho in grid),
        fitted_stock_weight=fitted_w[0],
        carried_stock_weight=carried_w[0],
        agg_ratio=agg,
        measured=(
            ("earlier period", measured_windows["falling rates"].legs.correlation),
            ("whole period", measured_windows["full span"].legs.correlation),
            ("later period", legs.correlation),
        ),
        fitted_at_measured=fitted(legs.correlation),
        carried_at_measured=carried(legs.correlation),
        turns_negative=_root(fitted, low, high),
        meets_agg=_root(lambda rho: fitted(rho) - agg, low, high),
        carried_floor=carried(-1.0),
        stock_vol=legs.stock_vol,
        bond_vol=legs.bond_vol,
        start=legs.start,
        end=legs.end,
    )


def _correlation(rho: float) -> str:
    """A correlation with its sign, to four places where two would round it to zero."""
    places = 2 if abs(rho) >= 0.005 else 4
    return f"{rho:+.{places}f}".replace("-", "−")


@_plain_text
def make_correlation_figure(out: Path | None = None) -> Figure:
    """The later period's hurdle against the correlation, beside AGG's ratio."""
    drawn = correlation_curves()

    fig = Figure(figsize=(10, 7.0), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.subplots()
    _style(ax)
    ax.grid(axis="x", color=RULE, lw=0.6, alpha=0.7)

    low, high = CORRELATION_RANGE
    ax.axvspan(low, drawn.meets_agg, color=GOOD, alpha=0.16, lw=0)
    ax.axhline(0.0, color=RULE, lw=1.2, zorder=1)
    ax.plot(
        drawn.correlations,
        drawn.fitted,
        color=INK,
        lw=2,
        zorder=3,
        label=(
            "weights fitted to the later period with hindsight "
            f"({_share(drawn.fitted_stock_weight)} stocks)"
        ),
    )
    ax.plot(
        drawn.correlations,
        drawn.carried,
        color=MUTED,
        lw=2,
        ls="--",
        zorder=3,
        label=(
            f"weights carried from the earlier period ({_share(drawn.carried_stock_weight)} stocks)"
        ),
    )
    ax.axhline(drawn.agg_ratio, color=ACCENT, lw=2, zorder=2)
    ax.annotate(
        f"AGG's Sharpe ratio, {_signed(drawn.agg_ratio)} times SPY's",
        (high, drawn.agg_ratio),
        xytext=(-6, -6),
        textcoords="offset points",
        ha="right",
        va="top",
        color=INK,
        fontsize=10,
    )
    placements = {
        "earlier period": (-4, -0.86, "right"),
        "whole period": (-4, -0.97, "right"),
        "later period": (4, -0.86, "left"),
    }
    for name, rho in drawn.measured:
        ax.axvline(rho, color=MUTED, lw=0.9, ls=":", zorder=1)
        dx, y, ha = placements[name]
        ax.annotate(
            f"{name}, {_correlation(rho)}",
            (rho, y),
            xytext=(dx, 0),
            textcoords="offset points",
            ha=ha,
            va="center",
            color=MUTED,
            fontsize=9,
        )
    after = drawn.measured[-1][1]
    for value in (drawn.fitted_at_measured, drawn.carried_at_measured):
        ax.plot([after], [value], "o", ms=8, color=ACCENT, zorder=5)
    ax.annotate(
        f"{_signed(drawn.fitted_at_measured)} and {_signed(drawn.carried_at_measured)}\n"
        f"at {_correlation(after)}",
        (after, drawn.fitted_at_measured),
        xytext=(10, -14),
        textcoords="offset points",
        ha="left",
        va="top",
        color=INK,
        fontsize=10,
        linespacing=1.35,
    )
    ax.plot(
        [drawn.meets_agg], [drawn.agg_ratio], "o", ms=9, mfc=SURFACE, mec=INK, mew=1.6, zorder=5
    )
    ax.annotate(
        f"meets AGG only at\ncorrelations below {_signed(drawn.meets_agg)}",
        (drawn.meets_agg, drawn.agg_ratio),
        xytext=(12, -10),
        textcoords="offset points",
        ha="left",
        va="top",
        color=INK,
        fontsize=10,
        linespacing=1.35,
    )
    ax.annotate(
        "on hindsight weights,\nrisk parity would lead",
        (low, 1.0),
        xycoords=("data", "axes fraction"),
        xytext=(4, -6),
        textcoords="offset points",
        ha="left",
        va="top",
        color=MUTED,
        fontsize=9,
        linespacing=1.3,
    )
    ax.set_xlim(low, high)
    ax.set_xticks([-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _pos: _signed(x, 2)))
    ax.set_ylim(-1.05, 1.05)
    ax.set_yticks([-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _pos: _signed(y, 2)))
    ax.set_xlabel("stock-bond correlation", color=INK, fontsize=10)
    ax.set_ylabel("hurdle, as a multiple of stocks' Sharpe ratio", color=INK, fontsize=10)
    ax.legend(
        loc="lower right", bbox_to_anchor=(1.0, 0.16), frameon=False, fontsize=9.5, labelcolor=INK
    )

    _title(
        fig,
        "After March 2022, AGG fell short of the hurdle at every correlation these funds showed",
        f"{STOCK} and {BOND} after the Federal Reserve's 16 March 2022 rate rise, {drawn.start} to "
        f"{drawn.end}, downloaded in 2026, at the {RISK_FREE:.0%} cash rate.\n"
        "The hurdle is the multiple of stocks' Sharpe ratio bonds need for levered risk parity to "
        "match 60/40 at the same volatility.\n"
        "Only the correlation varies. Both curves keep the later period's volatilities, "
        f"{drawn.stock_vol:.2%} for SPY and {drawn.bond_vol:.2%} for AGG,\nand AGG's line is "
        "its measured ratio. The solid curve turns negative at correlations below "
        f"{_signed(drawn.turns_negative)}. The dashed\ncurve, for the weights the post scores, "
        f"never falls below {_signed(drawn.carried_floor)} times stocks' Sharpe ratio, reached "
        "at −1.\n"
        f"{RISK_FREE:.0%} is the rate Chan assumes when levering SPY, borrowed here.",
    )
    fig.subplots_adjust(left=0.09, right=0.98, top=0.9, bottom=0.3)
    fig.curves = drawn
    return _save(fig, out, CORRELATION_FIGURE)


def main() -> None:
    make_risk_split_figure()
    print(f"wrote {FIGURES_DIR / SPLIT_FIGURE}")
    make_claim_figure()
    print(f"wrote {FIGURES_DIR / CLAIM_FIGURE}")
    make_hurdle_figure()
    print(f"wrote {FIGURES_DIR / HURDLE_FIGURE}")
    make_decode_figure()
    print(f"wrote {FIGURES_DIR / DECODE_FIGURE}")
    make_rate_figure()
    print(f"wrote {FIGURES_DIR / RATE_FIGURE}")
    make_window_figure()
    print(f"wrote {FIGURES_DIR / WINDOW_FIGURE}")
    make_correlation_figure()
    print(f"wrote {FIGURES_DIR / CORRELATION_FIGURE}")


if __name__ == "__main__":
    main()
