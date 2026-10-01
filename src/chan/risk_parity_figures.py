"""Two figures for the risk parity post, drawn from the committed SPY and AGG vintages.

1. :func:`make_risk_split_figure` draws Qian's premise, that 60/40 splits
   capital 60 to 40 and risk nowhere near it, on the full common span as four
   bars: 60/40's capital split, 60/40's risk split, risk parity's capital split
   and risk parity's risk split.
2. :func:`make_claim_figure` draws Lesson 1 of
   ``blog/risk-parity-against-60-40.md``. Risk parity's stock weight and
   leverage land close to Qian's, while the Sharpe ratio comparison he printed
   them to support does not. Its Sharpe panel has three rows: Qian's own pair,
   then this run's pair at the average bill rate and at the 4 percent rate the
   rest of the post uses.

Every number this run measured comes from :mod:`chan.risk_parity`, so a figure
can only be wrong by drawing the wrong thing, which
``tests/test_risk_parity_figures.py`` checks. Qian's numbers are the ones his
paper prints and are drawn as printed. Both figures read the committed vintages,
so they redraw anywhere the data is::

    uv run python -m chan.risk_parity_figures
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, PercentFormatter

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, MUTED, RULE, SURFACE
from chan.risk_parity import (
    BENCHMARK_WEIGHTS,
    BOND,
    BOOK_LEVERAGE,
    BOOK_WEIGHTS,
    RISK_FREE,
    STOCK,
    WINDOWS,
    Ranking,
    WindowResult,
    measure_window,
    rank_at_matched_volatility,
)
from chan.series import aligned_closes

SPLIT_FIGURE = "risk_parity_capital_and_risk.png"
CLAIM_FIGURE = "risk_parity_against_qian.png"

#: Qian's Sharpe ratios for 60/40 and for levered risk parity, Table 2 of
#: ``research/papers/qian-2005-risk-parity-portfolios.pdf``. Monthly returns on
#: the Russell 1000 and the Lehman Aggregate from 1983 to 2004, above the
#: Treasury-bill rate. Printed to two decimals, and drawn as printed.
QIAN_SHARPE_BENCHMARK = 0.67
QIAN_SHARPE_PARITY = 0.87

#: The average of the St. Louis Fed's three-month bill series, TB3MS, from
#: October 2003 to August 2026, the full calendar months inside the span. Read
#: off the Fed's site on 2026-09-30 and not stored here, which is why the
#: figure's note says so rather than presenting it as a measurement.
BILL_AVERAGE = 0.0174

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
        f"{STOCK} and {BOND}, {legs.start} to {legs.end}, 2026 downloads. A leg's share of risk "
        "is its share of the portfolio's variance.\n"
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
    at_bills = full_span_ranking(BILL_AVERAGE)
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
                f"{STOCK} and {BOND}, 2003 to 2026, cash at the {BILL_AVERAGE:.2%} bill average",
                at_bills.sharpe_benchmark,
                at_bills.sharpe_parity,
                at_bills.t_newey_west,
            ),
            SharpePair(
                f"{STOCK} and {BOND}, 2003 to 2026, cash at {RISK_FREE:.0%}",
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

    fig = Figure(figsize=(10, 6.2), dpi=130)
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
        "Risk parity's weight and leverage land close to Qian's, "
        "and its Sharpe ratio lead does not",
        "Qian (2005), Table 2: Russell 1000 and Lehman Aggregate, monthly, 1983 to 2004.\n"
        f"{STOCK} and {BOND}: {drawn.start} to {drawn.end}, daily, 2026 downloads. "
        f"{BILL_AVERAGE:.2%} is the St. Louis Fed's average three-month bill rate\n"
        "(TB3MS) from October 2003 to August 2026, read off the Fed's site and not stored here.\n"
        "t is the Newey-West t-statistic of risk parity minus 60/40. Beyond ±2, a gap that size "
        "arises by chance less than 5% of the time.",
    )
    fig.subplots_adjust(left=0.1, right=0.98, top=0.86, bottom=0.29)
    fig.claim = drawn
    return _save(fig, out, CLAIM_FIGURE)


def main() -> None:
    make_risk_split_figure()
    print(f"wrote {FIGURES_DIR / SPLIT_FIGURE}")
    make_claim_figure()
    print(f"wrote {FIGURES_DIR / CLAIM_FIGURE}")


if __name__ == "__main__":
    main()
