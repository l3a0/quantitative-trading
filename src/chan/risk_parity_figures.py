"""A figure for the risk parity post, drawn from the committed SPY and AGG vintages.

``blog/risk-parity-against-60-40.md`` starts from Qian's premise, that 60/40
splits capital 60 to 40 and risk nowhere near it. :func:`make_risk_split_figure`
draws that premise on the full common span, as four bars.

1. 60/40's capital split.
2. 60/40's risk split, where the equity leg carries nearly all of it.
3. Risk parity's capital split, which moves most of the capital into bonds.
4. Risk parity's risk split, which is even.

The shares come from :func:`chan.risk_parity.measure_window`, so the figure can
only be wrong by drawing the wrong thing, which
``tests/test_risk_parity_figures.py`` checks. It reads the committed vintages,
so it redraws anywhere the data is::

    uv run python -m chan.risk_parity_figures
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from matplotlib.figure import Figure
from matplotlib.patches import Patch
from matplotlib.ticker import PercentFormatter

from chan.coin_flip_figures import _plain_text, _save, _style, _title
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, RULE, SURFACE
from chan.risk_parity import BOND, STOCK, WINDOWS, WindowResult, measure_window
from chan.series import aligned_closes

SPLIT_FIGURE = "risk_parity_capital_and_risk.png"

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
        "60/40 puts 60% of the capital and 97% of the risk in stocks",
        f"{STOCK} and {BOND}, {legs.start} to {legs.end}, 2026 downloads. A leg's share of risk "
        "is its share of the portfolio's variance.\n"
        f"Risk parity weights each leg by the inverse of its volatility, {legs.stock_vol:.2%} "
        f"for {STOCK} and {legs.bond_vol:.2%} for {BOND}, which splits the risk evenly.",
    )
    fig.tight_layout(rect=(0, 0.08, 1, 0.95))
    fig.bars = bars
    return _save(fig, out, SPLIT_FIGURE)


def main() -> None:
    make_risk_split_figure()
    print(f"wrote {FIGURES_DIR / SPLIT_FIGURE}")


if __name__ == "__main__":
    main()
