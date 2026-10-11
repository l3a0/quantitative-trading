"""Chan's constant leverage and capped Kelly allocation, Examples 8.1 and 8.2.

Both examples sit in *Algorithmic Trading*'s risk chapter, and both are
arithmetic on inputs the book states. Example 8.1 shows what keeping a leverage
constant asks of a trader after a loss and after a gain. Example 8.2 shows that
when a broker caps leverage below what Kelly asks for, scaling every Kelly
leverage down by the same factor is not the allocation that grows fastest.

Location numbers are Kindle locations in *Algorithmic Trading* (Wiley, 2013),
in ``research/book-notes/algorithmic-trading.md``. Neither example has a script
in Chan's public code mirrors, so the printed prose is the whole source.

**These examples read no vintage.** Like ``coin_flip_growth``, every input is a
number the book states, so there is no vendor to restate it and no download
date to name. The run says ``vintage: none, synthetic``. Nothing can move an
arithmetic result, so every verdict was known before this module was written,
and neither epistemic label reaches it: exploratory means a sample was spent
looking, registered means a hypothesis was written before a number was seen,
and this spends no sample.

## Example 8.1 runs through ``kelly_leverage.rebalance``

Location 3216 starts with $100K of equity at leverage 5, takes a $10K loss and
then a $20K gain, and resizes to leverage 5 after each. That is the operation
``chan.kelly_leverage.rebalance`` already performs for *Quantitative Trading*'s
Example 6.2, so :func:`constant_leverage_chain` calls it rather than holding a
second copy that could drift. The price is a conversion. ``rebalance`` takes a
fractional ``shock`` on the position and the book states dollars, so each step
passes ``-pnl / position``, and the trade is ``resized - shocked_portfolio``, a
quantity ``Rebalance`` does not carry. A gain is a negative shock.

## Example 8.2: the proportional scaling is the book's counter-example

Two uncorrelated strategies with annualised mean excess returns of 30 and 60
percent and volatilities of 26 and 35 percent have Kelly leverages
``F = C^-1 M`` of 4.4 and 4.9. A broker allows a gross leverage of 2. Location
3268 calls scaling both by ``2 / 9.3`` "the usual recommendation", which gives
0.95 and 1.05, and Example 8.2 exists to show it is not the best allocation.
The growth rate is ``g = r + F'M - F'CF / 2`` at ``r = 0``, and on the line
``F1 = 2 - F2`` it rises over the whole range from 0 to 2, so it peaks with
everything on strategy 2.

Three things about that peak are easy to get wrong, and each is pinned.

1. **0.955 is a tie.** The peak is exactly 191/200. Chan prints 0.96, the tie
   rounded up, which half-up and half-to-even rounding both give, so the
   printed digit cannot say which he used. In float, 0.955 sits just below the
   tie, so a report
   formatting it at two decimals prints 0.95 beside the book's 0.96 and reads
   as a miss. :func:`report` prints three decimals.
2. **The line has a higher point outside the cap.** Solved without bounding F2,
   the line's stationary point is F2 = 2.289321 with a growth rate of
   0.962956, reached by shorting strategy 1. Its gross leverage is 2.578643,
   over the cap, and location 3268 is explicit that the cap is on gross
   leverage. :func:`best_allocation_at_cap` clamps F2 to ``[0, Fmax]``.
3. **The corner is not always the answer.** Everything on strategy 2 stays best
   only while the cap is below :func:`corner_threshold`, 2.448980 here. That is
   the measured form of Chan's "when Fmax is much smaller than" the total
   Kelly leverage.

The constrained search is long-only and two-strategy on purpose. Long-only is
the range Chan plots in Figure 8.1, and two strategies are what the book works.
With a strong positive correlation, a short hedge inside the gross cap can beat
every long-only allocation, so the restriction is a stated limit rather than a
theorem. ``tests/test_kelly_allocation.py`` holds a case where it binds.
``docs/design.md`` records why a general allocator for n strategies was cut.

## What Entry 3 shares with this, and what it does not

``chan.kelly_leverage`` builds its leverage from a return series, and Example
8.2 starts from stated moments, so no function there applies. The formula is
the same continuous Gaussian form, ``f = m / s^2``, and Entry 3's
``levered_growth = r + S^2 / 2`` is the one-strategy case of Equation 8.3. The
sibling repo's ``kelly_fraction`` is a different object, the discrete form over
a bag of trade outcomes, as issue 14 ruled.

``tests/test_kelly_allocation.py`` is the single authority for every number
quoted about these examples, and ``docs/replication-log.md`` Entry 20 carries
the verdicts.

:mod:`chan.kelly_allocation_figures` draws the curve the run prints along
``F1 = 2 - F2``, the book's Figure 8.1, for
``blog/capped-kelly-allocation-lessons.md``. It continues the line past the
cap, dashed, to the unbounded peak, and calls these functions rather than
holding its own copy of the growth rate.

Usage::

    python -m chan.kelly_allocation
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from chan.kelly_leverage import rebalance

# Example 8.1 as location 3216 states it.
EX81_LEVERAGE = 5.0
EX81_EQUITY = 100_000.0
EX81_PNLS = (-10_000.0, 20_000.0)

# Example 8.2 as location 3287 states it: annualised mean excess returns and
# volatilities, zero correlation, a risk-free rate of 0, and a cap of 2.
MEANS = (0.30, 0.60)
VOLS = (0.26, 0.35)
CORRELATION = 0.0
RISK_FREE = 0.0
MAX_LEVERAGE = 2.0

BOOK_REF = (
    "Examples 8.1 and 8.2 (Algorithmic Trading, locations 3216 and 3287): "
    "leverage 5 on $100K sells $40K after a $10K loss and buys $80K after a $20K "
    "gain. Kelly leverages 4.4 and 4.9, total 9.3. Capped at 2, the proportional "
    "0.95 and 1.05 grow at 0.82 and everything on strategy 2 grows at 0.96"
)

# How finely the report samples the growth rate along F1 = Fmax - F2, which is
# the curve Figure 8.1 draws.
CURVE_STEPS = 8


@dataclass(frozen=True)
class Step:
    """One day of Example 8.1: the move, then the resize back to the leverage.

    ``trade`` is positive for a purchase and negative for a sale, so the book's
    "liquidate a further $40K" is ``trade == -40_000``.
    """

    equity_before: float
    position_before: float
    pnl: float
    position_after_move: float
    equity_after: float
    target: float
    trade: float


@dataclass(frozen=True)
class Allocation:
    """A leverage per strategy and the growth rate it earns."""

    leverages: tuple[float, ...]
    growth: float

    @property
    def gross(self) -> float:
        """The absolute sum of the leverages, which is what a broker caps."""
        return float(sum(abs(f) for f in self.leverages))


def constant_leverage_chain(
    leverage: float = EX81_LEVERAGE,
    equity: float = EX81_EQUITY,
    pnls: Sequence[float] = EX81_PNLS,
) -> tuple[Step, ...]:
    """Hold ``leverage`` through a run of dollar P&Ls, resizing after each.

    Each step is one call to :func:`chan.kelly_leverage.rebalance`, which
    starts from a position of ``leverage * equity``. That holds at every step
    after the first because the previous step resized to exactly it.
    """
    if leverage <= 0.0:
        raise ValueError(f"a leverage of {leverage} holds no position to resize")
    if equity <= 0.0:
        raise ValueError(f"equity of {equity:,.2f} leaves nothing to hold at any leverage")
    steps = []
    for pnl in pnls:
        position = leverage * equity
        moved = rebalance(leverage, equity=equity, shock=-pnl / position)
        # Checked after the move rather than before the next one, so the last
        # P&L in a run is held to it too. A resize against equity at or below
        # zero would report a short target at the same leverage.
        if moved.shocked_equity <= 0.0:
            raise ValueError(
                f"equity is {moved.shocked_equity:,.2f} after a P&L of {pnl:,.2f}, so there "
                "is nothing left to hold at any leverage"
            )
        steps.append(
            Step(
                equity_before=equity,
                position_before=moved.portfolio,
                pnl=pnl,
                position_after_move=moved.shocked_portfolio,
                equity_after=moved.shocked_equity,
                target=moved.resized,
                trade=moved.resized - moved.shocked_portfolio,
            )
        )
        equity = moved.shocked_equity
    return tuple(steps)


def covariance(vols: Sequence[float], correlation: float = 0.0) -> NDArray[np.float64]:
    """The covariance matrix of strategies sharing one pairwise correlation."""
    s = np.asarray(vols, dtype=float)
    corr = np.full((len(s), len(s)), float(correlation))
    np.fill_diagonal(corr, 1.0)
    return corr * np.outer(s, s)


def kelly_leverages(means: Sequence[float], cov: NDArray[np.float64]) -> NDArray[np.float64]:
    """Equation 8.2, ``F = C^-1 M``, solved rather than inverted."""
    return np.linalg.solve(np.asarray(cov, dtype=float), np.asarray(means, dtype=float))


def growth_rate(
    leverages: Sequence[float],
    means: Sequence[float],
    cov: NDArray[np.float64],
    risk_free: float = RISK_FREE,
) -> float:
    """``g = r + F'M - F'CF / 2``, the Gaussian growth rate at any leverages.

    At the Kelly leverages this is Equation 8.3, and at any other it is the
    form Equation 8.4 evaluates. Location 3319 gives the one-strategy case as
    ``f m - f^2 s^2 / 2``. Its recovered text reads ``m2`` where ``s2`` belongs,
    and the arithmetic settles which: with ``m^2`` the proportional allocation
    grows at 0.676, which matches nothing the book prints.
    """
    f = np.asarray(leverages, dtype=float)
    m = np.asarray(means, dtype=float)
    c = np.asarray(cov, dtype=float)
    return float(risk_free + f @ m - f @ c @ f / 2.0)


def proportional_cap(leverages: Sequence[float], max_leverage: float) -> NDArray[np.float64]:
    """Scale every leverage by ``Fmax / sum|Fi|``, the usual recommendation.

    Leverages already inside the cap come back unchanged, because the rule
    location 3268 states applies only when the cap is below the gross.
    """
    _check_cap(max_leverage)
    f = np.asarray(leverages, dtype=float)
    gross = float(np.abs(f).sum())
    if gross <= max_leverage:
        return f.copy()
    return f * (max_leverage / gross)


def _two(
    means: Sequence[float], cov: NDArray[np.float64]
) -> tuple[float, float, float, float, float]:
    m = np.asarray(means, dtype=float)
    c = np.asarray(cov, dtype=float)
    if m.shape != (2,) or c.shape != (2, 2):
        raise ValueError(
            f"the capped search works two strategies, as Example 8.2 does, and was given "
            f"means of shape {m.shape} and a covariance of shape {c.shape}"
        )
    return float(m[0]), float(m[1]), float(c[0, 0]), float(c[1, 1]), float(c[0, 1])


def _check_cap(max_leverage: float) -> None:
    if max_leverage < 0.0:
        raise ValueError(
            f"a cap of {max_leverage} is below zero, and a cap on gross leverage cannot be"
        )


def segment_stationary_point(
    means: Sequence[float], cov: NDArray[np.float64], max_leverage: float
) -> float:
    """Where the growth rate is flat on the line ``F1 = Fmax - F2``, unbounded.

    ``F2* = (m2 - m1 + Fmax (c11 - c12)) / (c11 + c22 - 2 c12)``. Nothing keeps
    it inside ``[0, Fmax]``, so it can name a short position whose gross
    leverage breaks the cap. :func:`best_allocation_at_cap` is the bounded one.
    """
    _check_cap(max_leverage)
    m1, m2, c11, c22, c12 = _two(means, cov)
    spread_variance = c11 + c22 - 2.0 * c12
    if spread_variance <= 0.0:
        raise ValueError(
            "the two strategies' difference has no variance, so every split of the cap "
            "grows at the same rate and no point on the line is the best"
        )
    return (m2 - m1 + max_leverage * (c11 - c12)) / spread_variance


def best_allocation_at_cap(
    means: Sequence[float],
    cov: NDArray[np.float64],
    max_leverage: float = MAX_LEVERAGE,
) -> Allocation:
    """The long-only split of a two-strategy cap that grows fastest.

    It spends the whole cap, ``F1 + F2 = Fmax`` with both at least zero, which
    is the range Figure 8.1 plots. That is the constrained optimum when the cap
    binds, meaning the uncapped Kelly pair is long-only and its gross is at
    least ``Fmax``. A short hedge is outside this search, and the module
    docstring says when that matters.
    """
    raw = segment_stationary_point(means, cov, max_leverage)
    f2 = min(max(raw, 0.0), max_leverage)
    leverages = (max_leverage - f2, f2)
    return Allocation(leverages, growth_rate(leverages, means, cov))


def corner_threshold(means: Sequence[float], cov: NDArray[np.float64]) -> float:
    """The largest cap at which putting everything on strategy 2 is still best.

    At the corner the slope along the line is ``(m2 - m1) - Fmax (c22 - c12)``,
    which stays positive while ``Fmax < (m2 - m1) / (c22 - c12)``. That is a
    largest cap only when strategy 2 has the higher mean and a variance above
    its covariance with strategy 1, which is Example 8.2's case. With the
    lower mean the corner is never best at a small cap, and with a variance at
    or below the covariance the slope rises with the cap rather than falling,
    so the same formula would name a smallest cap or nothing. Both refuse.
    """
    m1, m2, _, c22, c12 = _two(means, cov)
    if m2 <= m1:
        raise ValueError(
            f"strategy 2's mean of {m2} is not above strategy 1's {m1}, so no cap is small "
            "enough for everything on strategy 2 to be best"
        )
    if c22 <= c12:
        raise ValueError(
            "strategy 2's variance does not exceed its covariance with strategy 1, so the "
            "slope at the corner never falls with the cap and there is no largest cap"
        )
    return (m2 - m1) / (c22 - c12)


def report() -> None:
    """Print both examples, each figure beside the book's."""
    print("Chan's Examples 8.1 and 8.2, Algorithmic Trading (locations 3216 and 3287)")
    print(f"  {BOOK_REF}")
    print("  vintage: none, synthetic. These examples read no series.")
    print()

    print(f"Example 8.1, leverage {EX81_LEVERAGE:g} held on ${EX81_EQUITY:,.0f} of equity:")
    print(f"  {'P&L':>10}  {'equity':>10}  {'position after':>15}  {'target':>10}  {'trade':>10}")
    for step in constant_leverage_chain():
        print(
            f"  {step.pnl:>+10,.0f}  {step.equity_after:>10,.0f}"
            f"  {step.position_after_move:>15,.0f}  {step.target:>10,.0f}  {step.trade:>+10,.0f}"
        )
    print("  The book prints $490K and $450K, a sale of $40K, then $470K and $550K, a")
    print("  purchase of $80K. Each resize runs through chan.kelly_leverage.rebalance.")
    print()

    cov = covariance(VOLS, CORRELATION)
    kelly = kelly_leverages(MEANS, cov)
    capped = proportional_cap(kelly, MAX_LEVERAGE)
    best = best_allocation_at_cap(MEANS, cov, MAX_LEVERAGE)
    print(
        f"Example 8.2, two strategies, correlation {CORRELATION:g}, risk-free rate "
        f"{RISK_FREE:g}, cap {MAX_LEVERAGE:g}:"
    )
    print(f"  {'':<44}{'computed':>12}  book")
    rows = (
        ("Kelly leverage, strategy 1", f"{kelly[0]:.6f}", "4.4"),
        ("Kelly leverage, strategy 2", f"{kelly[1]:.6f}", "4.9"),
        ("total gross leverage", f"{np.abs(kelly).sum():.6f}", "9.3"),
        (
            "growth rate at Kelly, Equation 8.3",
            f"{growth_rate(kelly, MEANS, cov):.6f}",
            "not in the highlights",
        ),
        ("scaling factor, cap over gross", f"{MAX_LEVERAGE / np.abs(kelly).sum():.6f}", "none"),
        ("capped leverage, strategy 1", f"{capped[0]:.6f}", "0.95"),
        ("capped leverage, strategy 2", f"{capped[1]:.6f}", "1.05"),
        (
            "growth rate, proportional, Equation 8.4",
            f"{growth_rate(capped, MEANS, cov):.6f}",
            "0.82",
        ),
        ("growth rate, everything on strategy 2", f"{best.growth:.3f}", "0.96"),
    )
    for label, value, book in rows:
        print(f"  {label:<44}{value:>12}  {book}")
    print("  0.955 is exactly 191/200, a tie at two decimals, and 0.96 is that tie")
    print("  rounded up. It is printed at three decimals because a float 0.955 sits just")
    print("  below the tie and prints as 0.95 at two.")
    print()

    print(f"Growth rate along F1 = {MAX_LEVERAGE:g} - F2, the curve Figure 8.1 plots:")
    for k in range(CURVE_STEPS + 1):
        f2 = MAX_LEVERAGE * k / CURVE_STEPS
        g = growth_rate((MAX_LEVERAGE - f2, f2), MEANS, cov)
        print(f"  F2 = {f2:5.3f}   g = {g:.6f}")
    print(f"  The proportional allocation sits at F2 = {capped[1]:.6f}. The growth rate")
    print(f"  rises the whole way and peaks at F2 = {best.leverages[1]:g}.")
    print()

    raw = segment_stationary_point(MEANS, cov, MAX_LEVERAGE)
    line = (MAX_LEVERAGE - raw, raw)
    print("Two things the book's figures do not show:")
    print(
        f"  Unbounded, the line peaks at F2 = {raw:.6f} with g = "
        f"{growth_rate(line, MEANS, cov):.6f}, by holding F1 = {line[0]:.6f}."
    )
    print(
        f"  Its gross leverage is {abs(line[0]) + abs(line[1]):.6f}, over the cap of "
        f"{MAX_LEVERAGE:g}, so it is not allowed."
    )
    print(
        f"  Everything on strategy 2 stays best only while the cap is below "
        f"{corner_threshold(MEANS, cov):.6f}."
    )
    print()
    print("A replication is exploratory when a sample was spent looking. This one")
    print("spends none, so neither that label nor its opposite reaches it.")
    print("docs/replication-log.md Entry 20 carries the verdicts.")


def main() -> None:
    argparse.ArgumentParser(
        description=(
            "Chan's Examples 8.1 and 8.2: constant leverage and capped Kelly allocation. "
            "Takes no options, because the book fixes every input."
        )
    ).parse_args()
    report()


if __name__ == "__main__":
    main()
