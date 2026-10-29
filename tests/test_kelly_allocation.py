"""Pins for Chan's Examples 8.1 and 8.2, constant leverage and capped Kelly allocation.

This file is the single authority for every number a prose surface quotes
about these examples. The one exception is
``blog/capped-kelly-allocation-lessons.md``:
``tests/test_kelly_allocation_figures.py`` holds the numbers its figure draws,
and README lists what it says that nothing asserts. Every other figure the post
quotes is pinned here. :class:`TestTheCorner`, :class:`TestBesideTheClaim`,
:class:`TestWhereTheCornerStopsWinning` and :class:`TestTheLongOnlyLimit` hold
the ones the entry's thirteen rows do not, the slope and the corner's margin
over the proportional split among them. :class:`TestWhatThePostSays` reads
one copy of each from the post itself. ``docs/replication-log.md`` Entry 20
states its numbers and derives none of them, and
``src/chan/kelly_allocation.py`` carries the reasoning.

Every pin names its specification, because a number alone does not say which
of several plausible formulas produced it. Unless a class says otherwise, that
is the book's own: the inputs location 3287 states, zero correlation, a
risk-free rate of 0, annualised moments, and the continuous Gaussian growth
rate ``g = r + F'M - F'CF / 2``. The vintage is ``none, synthetic`` throughout,
since nothing here reads a series.

The six-decimal pins hold the computed value. The book's own figures are held
separately, at the precision the book prints them, so a reader can see which
assertion carries the replication and which carries the specification.
"""

from __future__ import annotations

import dataclasses
import math
import re
from decimal import ROUND_HALF_DOWN, ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal
from fractions import Fraction

import numpy as np
import pytest

from chan import kelly_allocation
from chan.kelly_allocation import (
    CORRELATION,
    EX81_EQUITY,
    EX81_LEVERAGE,
    MAX_LEVERAGE,
    MEANS,
    VOLS,
    Allocation,
    Step,
    best_allocation_at_cap,
    constant_leverage_chain,
    corner_threshold,
    covariance,
    growth_rate,
    growth_terms,
    kelly_leverages,
    main,
    proportional_cap,
    report,
    segment_stationary_point,
    unbounded_allocation_at_cap,
)
from chan.kelly_allocation_figures import BEYOND_CAP
from chan.paths import REPO_ROOT


@pytest.fixture(scope="module")
def cov():
    return covariance(VOLS, CORRELATION)


@pytest.fixture(scope="module")
def kelly(cov):
    return kelly_leverages(MEANS, cov)


def _book(value: float, places: int) -> str:
    """Round half up from the true value. No value this file passes in sits on
    a tie, so half to even would give the same digits. Row 10's tie is held in
    :class:`TestTheCorner`."""
    quantum = Decimal(1).scaleb(-places)
    return str(Decimal(repr(float(value))).quantize(quantum, rounding=ROUND_HALF_UP))


def _segment_grid(means, cov, cap: float, points: int = 20_001) -> tuple[float, float]:
    """The best growth rate on ``F1 = cap - F2``, F2 in ``[0, cap]``, and where."""
    best = max(
        (growth_rate((cap - f2, f2), means, cov), f2) for f2 in np.linspace(0.0, cap, points)
    )
    return best


def _gross_boundary_grid(
    means, cov, cap: float, points: int = 20_001
) -> tuple[float, float, float]:
    """The best growth rate anywhere on ``|F1| + |F2| = cap``, short positions included."""
    best = (-np.inf, 0.0, 0.0)
    for f1 in np.linspace(-cap, cap, points):
        for sign in (1.0, -1.0):
            f2 = sign * (cap - abs(f1))
            g = growth_rate((f1, f2), means, cov)
            if g > best[0]:
                best = (g, float(f1), float(f2))
    return best


# ============================================================
# Example 8.1, location 3216
# ============================================================


class TestConstantLeverage:
    """Every dollar figure Example 8.1 prints, from leverage 5 on $100K."""

    def test_the_loss_day_sells_forty_thousand(self) -> None:
        loss, _ = constant_leverage_chain()
        assert loss.position_before == pytest.approx(500_000.0, abs=1e-6)
        assert loss.equity_after == pytest.approx(90_000.0, abs=1e-6)
        assert loss.position_after_move == pytest.approx(490_000.0, abs=1e-6)
        assert loss.target == pytest.approx(450_000.0, abs=1e-6)
        assert loss.trade == pytest.approx(-40_000.0, abs=1e-6)

    def test_the_gain_day_buys_eighty_thousand(self) -> None:
        _, gain = constant_leverage_chain()
        assert gain.position_before == pytest.approx(450_000.0, abs=1e-6)
        assert gain.equity_after == pytest.approx(110_000.0, abs=1e-6)
        assert gain.position_after_move == pytest.approx(470_000.0, abs=1e-6)
        assert gain.target == pytest.approx(550_000.0, abs=1e-6)
        assert gain.trade == pytest.approx(80_000.0, abs=1e-6)

    def test_the_leverage_is_back_at_five_after_every_resize(self) -> None:
        for step in constant_leverage_chain():
            assert step.target / step.equity_after == pytest.approx(EX81_LEVERAGE, abs=1e-12)

    def test_the_trade_takes_the_sign_of_the_pnl(self) -> None:
        """Selling into a loss and buying into a gain is the whole point of the
        example, so the sign is pinned on its own and not only through a value."""
        for step in constant_leverage_chain(3.0, 50_000.0, (-1_000.0, 2_500.0, -700.0)):
            assert np.sign(step.trade) == np.sign(step.pnl)
            assert step.trade == pytest.approx((3.0 - 1.0) * step.pnl, abs=1e-9)

    def test_each_day_starts_where_the_last_resize_ended(self) -> None:
        loss, gain = constant_leverage_chain()
        assert gain.equity_before == loss.equity_after
        assert gain.position_before == pytest.approx(loss.target, abs=1e-9)

    def test_the_chain_runs_through_kelly_leverage_rebalance(self, monkeypatch) -> None:
        """Issue 298 asks for a call, not a copy, so a second implementation of
        the rebalance cannot drift from Entry 3's. Replacing the function the
        module imported must change what the chain returns."""
        calls = []
        real = kelly_allocation.rebalance

        def spy(*args, **kwargs):
            calls.append(kwargs["shock"])
            return real(*args, **kwargs)

        monkeypatch.setattr(kelly_allocation, "rebalance", spy)
        constant_leverage_chain()
        assert calls == [pytest.approx(0.02), pytest.approx(-20_000.0 / 450_000.0)]

    def test_a_chain_refuses_once_equity_is_gone(self) -> None:
        """At leverage 5 a 20 percent fall in the position is all the equity."""
        with pytest.raises(ValueError, match="nothing left to hold"):
            constant_leverage_chain(5.0, 100_000.0, (-100_000.0, 1_000.0))

    def test_the_last_move_is_held_to_the_same_check(self) -> None:
        """A loss past the equity on the final day would otherwise come back as a
        short target of -250,000 at "leverage 5" on equity of -50,000."""
        with pytest.raises(ValueError, match="nothing left to hold"):
            constant_leverage_chain(5.0, 100_000.0, (-150_000.0,))

    def test_a_chain_refuses_to_start_with_no_equity(self) -> None:
        with pytest.raises(ValueError, match="nothing to hold"):
            constant_leverage_chain(5.0, 0.0, (1_000.0,))

    def test_a_chain_refuses_a_leverage_that_holds_nothing(self) -> None:
        for leverage in (0.0, -1.0):
            with pytest.raises(ValueError, match="holds no position"):
                constant_leverage_chain(leverage, EX81_EQUITY, (1.0,))

    def test_the_results_are_frozen(self) -> None:
        step = constant_leverage_chain()[0]
        with pytest.raises(dataclasses.FrozenInstanceError):
            step.trade = 0.0  # type: ignore[misc]
        assert isinstance(step, Step)


# ============================================================
# Example 8.2, location 3287
# ============================================================


class TestKellyLeverages:
    """Equation 8.2 on the book's two uncorrelated strategies."""

    def test_the_computed_leverages(self, kelly) -> None:
        assert kelly[0] == pytest.approx(4.437870, abs=5e-7)
        assert kelly[1] == pytest.approx(4.897959, abs=5e-7)
        assert np.abs(kelly).sum() == pytest.approx(9.335829, abs=5e-7)

    def test_the_book_figures_at_the_book_precision(self, kelly) -> None:
        assert _book(kelly[0], 1) == "4.4"
        assert _book(kelly[1], 1) == "4.9"
        assert _book(float(np.abs(kelly).sum()), 1) == "9.3"

    def test_zero_correlation_reduces_to_mean_over_variance(self, kelly) -> None:
        """Equation 8.1 per strategy, which is what the book's 4.4 and 4.9 are."""
        for f, m, s in zip(kelly, MEANS, VOLS, strict=True):
            assert f == pytest.approx(m / s**2, abs=1e-12)


class TestTheProportionalScaling:
    """The usual recommendation location 3268 names, and Equation 8.4's 0.82."""

    def test_the_scaling_factor(self, kelly) -> None:
        assert MAX_LEVERAGE / np.abs(kelly).sum() == pytest.approx(0.214228, abs=5e-7)

    def test_the_capped_leverages(self, kelly) -> None:
        capped = proportional_cap(kelly, MAX_LEVERAGE)
        assert capped[0] == pytest.approx(0.950718, abs=5e-7)
        assert capped[1] == pytest.approx(1.049282, abs=5e-7)
        assert _book(capped[0], 2) == "0.95"
        assert _book(capped[1], 2) == "1.05"
        assert np.abs(capped).sum() == pytest.approx(MAX_LEVERAGE, abs=1e-12)

    def test_the_growth_rate_at_the_capped_leverages(self, cov, kelly) -> None:
        g = growth_rate(proportional_cap(kelly, MAX_LEVERAGE), MEANS, cov)
        assert g == pytest.approx(0.816798, abs=5e-7)
        assert _book(g, 2) == "0.82"

    def test_leverages_inside_the_cap_come_back_unchanged(self) -> None:
        """As a copy, so a caller editing the result does not edit its input."""
        inside = np.array([0.5, 0.7])
        result = proportional_cap(inside, MAX_LEVERAGE)
        assert np.array_equal(result, inside)
        assert result is not inside

    def test_the_cap_is_on_gross_leverage(self) -> None:
        """A short leg counts toward the cap at its absolute size."""
        capped = proportional_cap(np.array([-3.0, 1.0]), MAX_LEVERAGE)
        assert np.abs(capped).sum() == pytest.approx(MAX_LEVERAGE, abs=1e-12)
        assert capped[0] == pytest.approx(-1.5, abs=1e-12)


class TestTheCorner:
    """Everything on strategy 2, and the 0.96 that lands only by rounding a tie."""

    def test_the_best_allocation_spends_the_cap_on_strategy_two(self, cov) -> None:
        best = best_allocation_at_cap(MEANS, cov, MAX_LEVERAGE)
        assert best.leverages == (0.0, MAX_LEVERAGE)
        assert best.gross == MAX_LEVERAGE

    def test_a_grid_along_the_line_agrees(self, cov) -> None:
        g, f2 = _segment_grid(MEANS, cov, MAX_LEVERAGE)
        assert f2 == MAX_LEVERAGE
        assert g == pytest.approx(best_allocation_at_cap(MEANS, cov).growth, abs=1e-12)

    def test_a_grid_over_the_whole_gross_boundary_agrees(self, cov) -> None:
        """Short positions included. On Chan's inputs the long-only corner is
        also the best allocation anywhere the gross cap allows."""
        g, f1, f2 = _gross_boundary_grid(MEANS, cov, MAX_LEVERAGE)
        assert (f1, f2) == pytest.approx((0.0, MAX_LEVERAGE), abs=1e-9)
        assert g == pytest.approx(0.955, abs=1e-12)

    @pytest.mark.parametrize("correlation", (-1.0, -0.5, 0.0, 0.5, 0.95, 1.0))
    def test_no_correlation_makes_a_short_pay_at_a_cap_of_two(self, correlation) -> None:
        """Chan's means and volatilities at his cap of 2, with the correlation
        varied. A short never beats the best long-only split, so the hedge in
        :class:`TestTheLongOnlyLimit` needs its other inputs too, not only the
        correlation of 0.95."""
        varied = covariance(VOLS, correlation)
        g, f1, f2 = _gross_boundary_grid(MEANS, varied, MAX_LEVERAGE, points=4_001)
        assert f1 >= 0.0 and f2 >= 0.0
        assert g == pytest.approx(
            best_allocation_at_cap(MEANS, varied, MAX_LEVERAGE).growth, abs=1e-5
        )

    def test_the_slope_along_the_line_is_positive_up_to_the_cap(self, cov) -> None:
        """Along ``F1 = 2 - F2`` the growth rate is a parabola, so its slope is a
        line in F2: 0.4352 at F2 = 0, falling by 0.1901 per unit. It is still
        positive at F2 = 2, which is why the peak is the corner.

        ``blog/capped-kelly-allocation-lessons.md`` names the parts. The 0.4352
        is strategy 2's extra mean of 0.30 plus the drag shed off strategy 1,
        0.1352, its variance of 0.0676 times its leverage of 2. The 0.1901 is
        the two variances, 0.0676 and 0.1225, added together."""

        def slope(f2: float, h: float = 1e-6) -> float:
            up = growth_rate((MAX_LEVERAGE - f2 - h, f2 + h), MEANS, cov)
            down = growth_rate((MAX_LEVERAGE - f2 + h, f2 - h), MEANS, cov)
            return (up - down) / (2 * h)

        assert slope(0.0) == pytest.approx(0.4352, abs=1e-8)
        assert slope(1.0) - slope(0.0) == pytest.approx(-0.1901, abs=1e-8)
        assert slope(MAX_LEVERAGE) == pytest.approx(0.0550, abs=1e-8)
        c11, c22 = cov[0, 0], cov[1, 1]
        assert round(MEANS[1] - MEANS[0], 6) == 0.30
        assert (round(c11, 6), round(c22, 6)) == (0.0676, 0.1225)
        assert round(c11 * MAX_LEVERAGE, 6) == 0.1352
        assert slope(0.0) == pytest.approx(MEANS[1] - MEANS[0] + c11 * MAX_LEVERAGE, abs=1e-8)
        assert slope(1.0) - slope(0.0) == pytest.approx(-(c11 + c22), abs=1e-8)

    def test_the_growth_rate_is_exactly_a_tie(self, cov) -> None:
        g = best_allocation_at_cap(MEANS, cov).growth
        assert g == pytest.approx(0.955, abs=1e-15)
        m, s = Fraction(60, 100), Fraction(35, 100)
        assert 2 * m - 4 * s**2 / 2 == Fraction(191, 200)

    def test_the_book_rounds_the_tie_up(self) -> None:
        """Half up and half to even both give 0.96, so the printed digit cannot
        say which rule Chan used. Only half down gives 0.95."""
        tie, cent = Decimal("0.955"), Decimal("0.01")
        assert tie.quantize(cent, rounding=ROUND_HALF_UP) == Decimal("0.96")
        assert tie.quantize(cent, rounding=ROUND_HALF_EVEN) == Decimal("0.96")
        assert tie.quantize(cent, rounding=ROUND_HALF_DOWN) == Decimal("0.95")

    def test_float_formatting_at_two_decimals_prints_a_miss(self, cov) -> None:
        """Why the report prints three decimals. A float 0.955 sits just below
        the tie, so the obvious format puts 0.95 beside the book's 0.96."""
        g = best_allocation_at_cap(MEANS, cov).growth
        assert f"{g:.2f}" == "0.95"
        assert round(g, 2) == 0.95
        assert f"{g:.3f}" == "0.955"

    def test_the_corner_beats_the_proportional_allocation(self, cov, kelly) -> None:
        """Chan's claim, which is what row 10's verdict rests on."""
        corner = best_allocation_at_cap(MEANS, cov).growth
        proportional = growth_rate(proportional_cap(kelly, MAX_LEVERAGE), MEANS, cov)
        assert corner - proportional == pytest.approx(0.138202, abs=5e-7)


class TestTheNearMisses:
    """Formulas that look right on the page and give a different number."""

    def test_the_unbounded_line_peaks_outside_the_cap(self, cov) -> None:
        """Substituting ``F1 = Fmax - F2`` without bounding F2 finds a higher
        growth rate by shorting strategy 1, which the gross cap forbids."""
        f2 = segment_stationary_point(MEANS, cov, MAX_LEVERAGE)
        line = (MAX_LEVERAGE - f2, f2)
        assert f2 == pytest.approx(2.289321, abs=5e-7)
        assert line[0] == pytest.approx(-0.289321, abs=5e-7)
        assert growth_rate(line, MEANS, cov) == pytest.approx(0.962956, abs=5e-7)
        assert abs(line[0]) + abs(line[1]) == pytest.approx(2.578643, abs=5e-7)
        assert growth_rate(line, MEANS, cov) > best_allocation_at_cap(MEANS, cov).growth
        peak = unbounded_allocation_at_cap(MEANS, cov, MAX_LEVERAGE)
        assert peak.leverages == line
        assert peak.growth == growth_rate(line, MEANS, cov)
        assert peak.gross == pytest.approx(2.578643, abs=5e-7)

    def test_reading_location_3319_literally_gives_0_676(self, kelly) -> None:
        """The recovered text reads ``f2m2/2``. With the mean in place of the
        volatility, the proportional allocation grows at 0.676, which matches
        nothing the book prints, so the variance is what belongs there."""
        capped = proportional_cap(kelly, MAX_LEVERAGE)
        literal = sum(f * m - f**2 * m**2 / 2 for f, m in zip(capped, MEANS, strict=True))
        assert literal == pytest.approx(0.675932, abs=5e-7)


class TestWhereTheCornerStopsWinning:
    """Where everything on strategy 2 stops being best.

    That is where the "all" in location 3268's "most or all" ends. It is not
    where "much smaller than" ends, because on these inputs strategy 2 keeps
    most of the cap at every cap up to the total Kelly leverage.
    """

    def test_the_threshold(self, cov) -> None:
        assert corner_threshold(MEANS, cov) == pytest.approx(2.448980, abs=5e-7)

    def test_below_the_threshold_everything_goes_on_strategy_two(self, cov) -> None:
        cap = corner_threshold(MEANS, cov) - 1e-3
        assert best_allocation_at_cap(MEANS, cov, cap).leverages == (0.0, cap)

    def test_with_the_means_swapped_everything_goes_on_strategy_one(self, cov) -> None:
        """The lower bound of the clamp. Swapped, the line's stationary point
        sits at F2 = -0.866912, a short in strategy 2 that breaks the cap."""
        swapped = (MEANS[1], MEANS[0])
        assert segment_stationary_point(swapped, cov, MAX_LEVERAGE) == pytest.approx(
            -0.866912, abs=5e-7
        )
        best = best_allocation_at_cap(swapped, cov, MAX_LEVERAGE)
        assert best.leverages == (MAX_LEVERAGE, 0.0)
        assert best.growth == pytest.approx(1.0648, abs=1e-12)
        g, grid_f2 = _segment_grid(swapped, cov, MAX_LEVERAGE)
        assert grid_f2 == 0.0 and g == pytest.approx(best.growth, abs=1e-12)

    def test_above_the_threshold_the_optimum_mixes(self, cov) -> None:
        cap = corner_threshold(MEANS, cov) + 0.5
        f1, f2 = best_allocation_at_cap(MEANS, cov, cap).leverages
        assert f1 > 0.0 and f2 > 0.0
        g, grid_f2 = _segment_grid(MEANS, cov, cap)
        assert f2 == pytest.approx(grid_f2, abs=cap / 20_000)

    def test_at_the_kelly_gross_the_optimum_is_the_kelly_pair(self, cov, kelly) -> None:
        best = best_allocation_at_cap(MEANS, cov, float(np.abs(kelly).sum()))
        assert best.leverages == pytest.approx(tuple(kelly), abs=1e-12)

    def test_strategy_two_keeps_most_of_the_cap_up_to_the_kelly_gross(self, cov, kelly) -> None:
        """Location 3268's "most" holds at every cap here, and only "all" ends at
        the threshold. The shares are held at the three decimals the post prints."""
        total = float(np.abs(kelly).sum())

        def share(cap: float) -> float:
            return best_allocation_at_cap(MEANS, cov, cap).leverages[1] / cap

        assert share(corner_threshold(MEANS, cov)) == 1.0
        assert _book(share(3.0), 3) == "0.882"
        assert _book(share(4.0), 3) == "0.750"
        assert _book(share(total), 3) == "0.525"
        assert all(share(cap) > 0.5 for cap in np.linspace(0.01, total, 1_000))


class TestTheKellyGrowthRate:
    """Equation 8.3, whose printed value the highlights did not capture."""

    def test_the_growth_rate_at_kelly(self, cov, kelly) -> None:
        assert growth_rate(kelly, MEANS, cov) == pytest.approx(2.135068, abs=5e-7)

    def test_it_is_half_the_sum_of_squared_sharpe_ratios(self, cov, kelly) -> None:
        sharpes = [m / s for m, s in zip(MEANS, VOLS, strict=True)]
        assert growth_rate(kelly, MEANS, cov) == pytest.approx(
            sum(x**2 for x in sharpes) / 2.0, abs=1e-12
        )

    def test_one_strategy_matches_entry_three(self) -> None:
        """Entry 3's ``levered_growth`` is ``r + S^2 / 2`` at the Kelly leverage,
        and this growth function gives the same at ``r = 0`` and at Chan's 4 percent."""
        m, s = 0.0723, 0.1691
        cov1 = np.array([[s**2]])
        f = kelly_leverages([m], cov1)
        for r in (0.0, 0.04):
            assert growth_rate(f, [m], cov1, r) == pytest.approx(r + (m / s) ** 2 / 2, abs=1e-12)

    def test_the_kelly_leverages_maximise_the_growth_rate(self, cov, kelly) -> None:
        g = growth_rate(kelly, MEANS, cov)
        for nudge in ((0.01, 0.0), (0.0, -0.01), (0.01, 0.01)):
            assert growth_rate(kelly + np.array(nudge), MEANS, cov) < g


class TestCorrelatedStrategies:
    """Chan's covariance is diagonal, so his figures cannot hold the off-diagonal
    term. Without these, dropping ``c12`` from any formula passes every pin."""

    MEANS = (0.30, 0.60)
    COV = covariance((0.26, 0.35), 0.5)

    def test_the_kelly_pair_matches_the_two_by_two_inverse(self) -> None:
        (c11, c12), (_, c22) = self.COV
        det = c11 * c22 - c12**2
        expected = ((c22 * 0.30 - c12 * 0.60) / det, (c11 * 0.60 - c12 * 0.30) / det)
        assert tuple(kelly_leverages(self.MEANS, self.COV)) == pytest.approx(expected, abs=1e-12)

    def test_the_two_terms_are_the_return_and_half_the_variance(self) -> None:
        """:func:`growth_terms` is the one place the formula is written, so it is
        held here to the arithmetic by hand, cross term included, and
        :func:`growth_rate` to the risk-free rate plus their difference."""
        (c11, c12), (_, c22) = self.COV
        f1, f2 = 0.7, 1.3
        ret, drag = growth_terms((f1, f2), self.MEANS, self.COV)
        assert ret == pytest.approx(f1 * 0.30 + f2 * 0.60, abs=1e-15)
        assert drag == pytest.approx(
            (f1 * f1 * c11 + 2 * f1 * f2 * c12 + f2 * f2 * c22) / 2, abs=1e-15
        )
        for r in (0.0, 0.04):
            assert growth_rate((f1, f2), self.MEANS, self.COV, r) == pytest.approx(
                r + ret - drag, abs=1e-15
            )

    def test_the_growth_rate_carries_the_cross_term(self) -> None:
        f = (1.0, 1.0)
        diagonal = covariance((0.26, 0.35), 0.0)
        assert growth_rate(f, self.MEANS, diagonal) - growth_rate(
            f, self.MEANS, self.COV
        ) == pytest.approx(self.COV[0, 1], abs=1e-15)

    def test_the_constrained_optimum_matches_a_grid(self) -> None:
        cap = 5.0
        f1, f2 = best_allocation_at_cap(self.MEANS, self.COV, cap).leverages
        assert 0.0 < f2 < cap
        g, grid_f2 = _segment_grid(self.MEANS, self.COV, cap)
        assert f2 == pytest.approx(grid_f2, abs=cap / 20_000)

    def test_the_threshold_carries_the_cross_term(self) -> None:
        (_, c12), (_, c22) = self.COV
        assert corner_threshold(self.MEANS, self.COV) == pytest.approx(
            0.30 / (c22 - c12), abs=1e-12
        )
        assert corner_threshold(self.MEANS, self.COV) == pytest.approx(3.896104, abs=5e-7)


class TestTheLongOnlyLimit:
    """The capped search is long-only, and here is a case where that costs growth.

    Two strategies with means of 0.05 and 0.30, a volatility of 0.30 each and a
    correlation of 0.95, under a cap of 4. The cap is a maximum, so the best
    long-only allocation holds strategy 2 alone at its own Kelly leverage of
    10/3, inside the cap, and grows at exactly 0.5. Spending the whole cap on
    strategy 2, which is what :func:`best_allocation_at_cap` searches, grows at
    0.48. A short hedge in strategy 1 inside the same gross cap grows faster than
    both, so the module's restriction is a limit and not a theorem.
    """

    MEANS = (0.05, 0.30)
    COV = covariance((0.30, 0.30), 0.95)
    CAP = 4.0

    def _hedge(self) -> tuple[float, float]:
        """The best split with strategy 1 short and the gross cap spent.

        With ``F1 = F2 - cap`` the short's size and strategy 2's long sum to the
        cap. Flipping strategy 1's sign turns that into the line
        :func:`segment_stationary_point` solves, with strategy 1's mean and the
        covariance negated.
        """
        flipped_means = (-self.MEANS[0], self.MEANS[1])
        flipped_cov = self.COV * np.array([[1.0, -1.0], [-1.0, 1.0]])
        f2 = segment_stationary_point(flipped_means, flipped_cov, self.CAP)
        return (f2 - self.CAP, f2)

    def _return(self, leverages) -> float:
        return growth_terms(leverages, self.MEANS, self.COV)[0]

    def _drag(self, leverages) -> float:
        return growth_terms(leverages, self.MEANS, self.COV)[1]

    def test_the_whole_cap_on_strategy_two(self) -> None:
        best = best_allocation_at_cap(self.MEANS, self.COV, self.CAP)
        assert best.leverages == (0.0, self.CAP)
        assert best.growth == pytest.approx(0.48, abs=1e-12)

    def test_the_best_long_only_allocation_is_strategy_two_alone_inside_the_cap(self) -> None:
        """Strategy 2 at ``m2 / c22`` grows at ``m2^2 / (2 c22)``, exactly 1/2,
        and no long-only allocation with a gross at or below the cap does better."""
        f2 = self.MEANS[1] / self.COV[1, 1]
        assert f2 == pytest.approx(3.333333, abs=5e-7)
        assert f2 < self.CAP
        g = growth_rate((0.0, f2), self.MEANS, self.COV)
        assert g == pytest.approx(0.5, abs=1e-12)
        m, c = Fraction(30, 100), Fraction(30, 100) ** 2
        assert m**2 / (2 * c) == Fraction(1, 2)
        assert g > best_allocation_at_cap(self.MEANS, self.COV, self.CAP).growth
        grid = np.linspace(0.0, self.CAP, 161)
        best = max(
            (growth_rate((a, b), self.MEANS, self.COV), a, b)
            for a in grid
            for b in grid
            if a + b <= self.CAP + 1e-12
        )
        assert best[0] <= g
        assert (best[1], best[2]) == pytest.approx((0.0, f2), abs=self.CAP / 160)

    def test_a_short_hedge_inside_the_cap_beats_it(self) -> None:
        g, f1, f2 = _gross_boundary_grid(self.MEANS, self.COV, self.CAP)
        assert f1 == pytest.approx(-1.002849, abs=1e-3)
        assert f2 == pytest.approx(2.997151, abs=1e-3)
        assert g == pytest.approx(0.656501, abs=1e-6)
        assert abs(f1) + abs(f2) == pytest.approx(self.CAP, abs=1e-9)

    def test_the_hedge_in_closed_form(self) -> None:
        f1, f2 = self._hedge()
        assert f1 == pytest.approx(-1.002849, abs=5e-7)
        assert f2 == pytest.approx(2.997151, abs=5e-7)
        assert abs(f1) + abs(f2) == pytest.approx(self.CAP, abs=1e-12)
        assert growth_rate((f1, f2), self.MEANS, self.COV) == pytest.approx(0.656501, abs=5e-7)
        g, *_ = _gross_boundary_grid(self.MEANS, self.COV, self.CAP)
        assert growth_rate((f1, f2), self.MEANS, self.COV) >= g

    def test_the_hedge_saves_more_drag_than_it_gives_up_in_return(self) -> None:
        """Set against the whole cap on strategy 2. The return given up is the
        short's own mean plus strategy 2's mean on the leverage the short
        displaces under the gross cap."""
        hedge, corner = self._hedge(), (0.0, self.CAP)
        for leverages in (hedge, corner):
            assert self._return(leverages) - self._drag(leverages) == pytest.approx(
                growth_rate(leverages, self.MEANS, self.COV), abs=1e-15
            )
        assert self._return(corner) == pytest.approx(1.2, abs=1e-12)
        assert self._drag(corner) == pytest.approx(0.72, abs=1e-12)
        assert self._return(hedge) == pytest.approx(0.849003, abs=5e-7)
        assert self._drag(hedge) == pytest.approx(0.192501, abs=5e-7)
        saved = self._drag(corner) - self._drag(hedge)
        given_up = self._return(corner) - self._return(hedge)
        on_the_short = -hedge[0] * self.MEANS[0]
        displaced = (self.CAP - hedge[1]) * self.MEANS[1]
        assert saved == pytest.approx(0.527499, abs=5e-7)
        assert given_up == pytest.approx(0.350997, abs=5e-7)
        assert on_the_short == pytest.approx(0.050142, abs=5e-7)
        assert displaced == pytest.approx(0.300855, abs=5e-7)
        assert on_the_short + displaced == pytest.approx(given_up, abs=1e-12)
        assert saved > given_up


class TestTheInputsAreChecked:
    def test_the_capped_search_takes_two_strategies(self) -> None:
        """Each half of the shape check on its own, so neither can be dropped."""
        with pytest.raises(ValueError, match="two strategies"):
            best_allocation_at_cap((0.1, 0.2, 0.3), covariance((0.1, 0.2, 0.3)), 2.0)
        with pytest.raises(ValueError, match="two strategies"):
            best_allocation_at_cap((0.1, 0.2), covariance((0.1, 0.2, 0.3)), 2.0)
        with pytest.raises(ValueError, match="two strategies"):
            best_allocation_at_cap((0.1, 0.2, 0.3), covariance((0.1, 0.2)), 2.0)

    def test_identical_strategies_have_no_best_split(self) -> None:
        with pytest.raises(ValueError, match="no variance"):
            segment_stationary_point((0.3, 0.3), covariance((0.2, 0.2), 1.0), 2.0)

    def test_a_threshold_needs_strategy_two_to_carry_its_own_risk(self) -> None:
        with pytest.raises(ValueError, match="no largest cap"):
            corner_threshold((0.3, 0.6), covariance((0.2, 0.2), 1.0))
        with pytest.raises(ValueError, match="no largest cap"):
            corner_threshold((0.3, 0.6), covariance((0.4, 0.2), 0.9))

    def test_a_threshold_needs_strategy_two_to_have_the_higher_mean(self) -> None:
        """With the means swapped the formula gives -2.448980, a cap nothing can be.
        With them equal it gives 0, which is no cap either."""
        with pytest.raises(ValueError, match="not above"):
            corner_threshold((0.60, 0.30), covariance(VOLS))
        with pytest.raises(ValueError, match="not above"):
            corner_threshold((0.30, 0.30), covariance(VOLS))

    def test_a_cap_below_zero_is_refused(self) -> None:
        with pytest.raises(ValueError, match="below zero"):
            best_allocation_at_cap(MEANS, covariance(VOLS), -1.0)
        with pytest.raises(ValueError, match="below zero"):
            proportional_cap((4.4, 4.9), -1.0)

    def test_an_allocation_reports_its_gross_leverage(self) -> None:
        assert Allocation((-1.5, 0.5), 0.0).gross == 2.0


class TestBesideTheClaim:
    """Figures the blog post quotes that the entry's thirteen rows do not hold.

    ``blog/capped-kelly-allocation-lessons.md`` splits the growth rate into
    its two terms, the return ``F'M`` and the drag ``F'CF / 2``, to say why
    the corner beats the proportional split. Each term comes from
    :func:`growth_terms` at the run's own leverages and covariance, and each
    pair is held to :func:`growth_rate`, so a split that stopped adding up
    fails too.
    """

    @staticmethod
    def _return(leverages) -> float:
        return growth_terms(leverages, MEANS, covariance(VOLS, CORRELATION))[0]

    @staticmethod
    def _drag(leverages, cov) -> float:
        return growth_terms(leverages, MEANS, cov)[1]

    def _split(self, leverages, cov) -> tuple[float, float]:
        ret, drag = self._return(leverages), self._drag(leverages, cov)
        assert ret - drag == pytest.approx(growth_rate(leverages, MEANS, cov), abs=1e-15)
        return ret, drag

    def test_the_sharpe_ratios(self, cov, kelly) -> None:
        """Half the sum of their squares is the growth rate at Kelly, 2.135068."""
        sharpes = [m / s for m, s in zip(MEANS, VOLS, strict=True)]
        assert sharpes == pytest.approx([1.153846, 1.714286], abs=5e-7)
        assert sum(x**2 for x in sharpes) / 2 == pytest.approx(
            growth_rate(kelly, MEANS, cov), abs=1e-12
        )

    def test_at_kelly_the_drag_is_exactly_half_the_return(self, cov, kelly) -> None:
        ret, drag = self._split(kelly, cov)
        assert ret == pytest.approx(4.270136, abs=5e-7)
        assert drag == pytest.approx(2.135068, abs=5e-7)
        assert drag == pytest.approx(ret / 2, abs=1e-12)

    def test_the_proportional_splits_return_and_drag(self, cov, kelly) -> None:
        ret, drag = self._split(proportional_cap(kelly, MAX_LEVERAGE), cov)
        assert ret == pytest.approx(0.914785, abs=5e-7)
        assert drag == pytest.approx(0.097986, abs=5e-7)

    def test_the_corners_return_and_drag(self, cov) -> None:
        ret, drag = self._split(best_allocation_at_cap(MEANS, cov).leverages, cov)
        assert ret == pytest.approx(1.2, abs=1e-12)
        assert drag == pytest.approx(0.245, abs=1e-12)

    def test_the_proportional_split_saves_less_drag_than_it_gives_up_in_return(
        self, cov, kelly
    ) -> None:
        proportional = proportional_cap(kelly, MAX_LEVERAGE)
        corner = best_allocation_at_cap(MEANS, cov).leverages
        saved = self._drag(corner, cov) - self._drag(proportional, cov)
        given_up = self._return(corner) - self._return(proportional)
        assert saved == pytest.approx(0.147014, abs=5e-7)
        assert given_up == pytest.approx(0.285215, abs=5e-7)

    def test_the_corner_grows_1_169199_times_as_fast(self, cov, kelly) -> None:
        corner = best_allocation_at_cap(MEANS, cov).growth
        proportional = growth_rate(proportional_cap(kelly, MAX_LEVERAGE), MEANS, cov)
        assert corner / proportional == pytest.approx(1.169199, abs=5e-7)

    def test_everything_on_strategy_one_grows_at_0_4648(self, cov) -> None:
        """The other end of the curve Figure 8.1 plots, F2 = 0."""
        assert growth_rate((MAX_LEVERAGE, 0.0), MEANS, cov) == pytest.approx(0.4648, abs=1e-12)

    def test_the_share_of_the_uncapped_kelly_growth_each_keeps(self, cov, kelly) -> None:
        at_kelly = growth_rate(kelly, MEANS, cov)
        proportional = growth_rate(proportional_cap(kelly, MAX_LEVERAGE), MEANS, cov)
        corner = best_allocation_at_cap(MEANS, cov).growth
        assert proportional / at_kelly == pytest.approx(0.382563, abs=5e-7)
        assert corner / at_kelly == pytest.approx(0.447292, abs=5e-7)

    def test_the_threshold_is_about_a_quarter_of_the_kelly_gross(self, cov, kelly) -> None:
        """Where the "all" ends, as a share of the Kelly gross on Chan's inputs."""
        ratio = corner_threshold(MEANS, cov) / float(np.abs(kelly).sum())
        assert ratio == pytest.approx(0.262321, abs=5e-7)


# ============================================================
# The report, which nothing above executes
# ============================================================


class TestTheReportSaysWhatItComputed:
    def test_the_report_prints_every_figure_beside_the_book(self, cov, kelly, capsys) -> None:
        report()
        out = capsys.readouterr().out
        assert "vintage: none, synthetic" in out
        for value in ("4.437870", "4.897959", "9.335829", "0.950718", "1.049282", "0.816798"):
            assert value in out
        assert "-40,000" in out and "+80,000" in out
        assert "2.289321" in out and "0.962956" in out and "2.578643" in out
        assert "2.448980" in out

    def test_each_labelled_row_carries_its_own_value(self, capsys) -> None:
        """The test above finds each value somewhere in the output, so it passes
        with two rows swapped or a label on the wrong number. These read the line
        each label sits on."""
        report()
        lines = capsys.readouterr().out.splitlines()

        def row(label: str) -> str:
            return next(line for line in lines if label in line)

        assert "2.135068" in row("growth rate at Kelly, Equation 8.3")
        assert "0.214228" in row("scaling factor, cap over gross")
        assert "0.816798" in row("growth rate, proportional, Equation 8.4")
        assert "correlation 0," in row("Example 8.2, two strategies")
        assert "F1 = -0.289321" in row("Unbounded, the line peaks")
        assert "sits at F2 = 1.049282" in row("The proportional allocation sits")
        assert "peaks at F2 = 2." in row("rises the whole way")
        loss = [cell for cell in lines if "-10,000" in cell][0].split()
        gain = [cell for cell in lines if "+20,000" in cell][0].split()
        assert loss == ["-10,000", "90,000", "490,000", "450,000", "-40,000"]
        assert gain == ["+20,000", "110,000", "470,000", "550,000", "+80,000"]

    def test_the_corner_line_prints_three_decimals(self, capsys) -> None:
        report()
        line = next(
            row
            for row in capsys.readouterr().out.splitlines()
            if "growth rate, everything on strategy 2" in row
        )
        assert line.split()[-2:] == ["0.955", "0.96"]

    def test_the_curve_rises_to_the_corner(self, capsys) -> None:
        report()
        growths = [
            float(row.split("g = ")[1])
            for row in capsys.readouterr().out.splitlines()
            if row.strip().startswith("F2 =")
        ]
        assert len(growths) == 9
        assert kelly_allocation.CURVE_STEPS == 8
        assert growths == sorted(growths)
        assert growths[-1] == pytest.approx(0.955, abs=5e-7)

    def test_the_cli_takes_no_options_and_runs(self, monkeypatch, capsys) -> None:
        monkeypatch.setattr("sys.argv", ["kelly_allocation"])
        main()
        assert "Example 8.2" in capsys.readouterr().out
        monkeypatch.setattr("sys.argv", ["kelly_allocation", "--cap", "3"])
        with pytest.raises(SystemExit):
            main()


# ============================================================
# The post, read against the run
# ============================================================

POST = REPO_ROOT / "blog" / "capped-kelly-allocation-lessons.md"


def _cell(latex: str) -> str:
    """A table cell as the reader sees it, so ``\\text{sell } 40\\text{K}`` is
    ``sell 40K`` and ``490{,}000`` is ``490,000``."""
    text = re.sub(r"\\text\{([^}]*)\}", r"\1", latex).replace("{,}", ",")
    return " ".join(text.replace("{", "").replace("}", "").split())


def _table(text: str, header: str) -> dict[str, list[list[str]]]:
    """The one ``array`` block holding ``header``, its rows keyed by their first
    cell. A label used twice, as Example 8.1's "Trade back to 5" is, maps to
    each of its rows in order."""
    bodies = re.findall(r"\\begin\{array\}\{[^}]*\}(.*?)\\end\{array\}", text, re.S)
    (body,) = [found for found in bodies if header in found]
    table: dict[str, list[list[str]]] = {}
    for line in body.split("\\\\"):
        cells = [_cell(cell) for cell in line.replace("\\hline", "").split("&")]
        table.setdefault(cells[0], []).append(cells[1:])
    return table


def _six(value: float) -> str:
    """``value`` at the six decimals the post prints, with a typographic minus."""
    return f"{value:.6f}".replace("-", "−")


def _short(value: float) -> str:
    """An exact figure as the post writes it, with no trailing zeros, such as 1.2."""
    return f"{value:.6f}".rstrip("0").rstrip(".")


def _dollars(value: float) -> str:
    """A dollar figure as the post's prose writes it, ``\\$40,000``."""
    return f"\\${abs(value):,.0f}"


def _thousands(value: float) -> str:
    """A dollar figure as the book prints it, ``40K``."""
    return f"{abs(value) / 1000:.0f}K"


class TestWhatThePostSays:
    """One copy of each figure the capped Kelly allocation post quotes, read from the post.

    The post is ``blog/capped-kelly-allocation-lessons.md``. Other copies of
    the same figure elsewhere in the post are not always read, and the figures
    the two whiteboard sketches print are read from their alt texts by
    ``tests/test_kelly_allocation_whiteboard.py``. Each expected value comes
    from the run, through the functions the pins above hold, and is compared at
    the precision the post prints it. The book's figures in Lesson 1's tables
    are compared with the run's at the book's precision. A table is read by its
    row labels, and a sentence by the words around its number.

    The prose states these numbers and the tests above derive them, so before
    this class a typo in the post passed every test. Round 1 of the post's
    review changed 34 single numbers across its prose, tables and alt text,
    and none failed a test.
    """

    text = POST.read_text("utf-8")

    def _has(self, *sentences: str) -> None:
        for sentence in sentences:
            assert sentence in self.text, sentence

    def test_lesson_1_s_table_for_example_8_1(self) -> None:
        loss, gain = constant_leverage_chain()
        assert _table(self.text, "Example 8.1") == {
            "Example 8.1": [["Computed", "Book"]],
            "Position after loss": [
                [f"{loss.position_after_move:,.0f}", _thousands(loss.position_after_move)]
            ],
            "Trade back to 5": [
                [f"{loss.trade:+,.0f}", f"sell {_thousands(loss.trade)}"],
                [f"{gain.trade:+,.0f}", f"buy {_thousands(gain.trade)}"],
            ],
            "Position after gain": [
                [f"{gain.position_after_move:,.0f}", _thousands(gain.position_after_move)]
            ],
        }

    def test_lesson_1_s_table_for_example_8_2(self, cov, kelly) -> None:
        capped = proportional_cap(kelly, MAX_LEVERAGE)
        total = float(np.abs(kelly).sum())
        scaled = growth_rate(capped, MEANS, cov)
        corner = best_allocation_at_cap(MEANS, cov).growth
        printed = Decimal(f"{corner:.3f}")
        assert _table(self.text, "Example 8.2") == {
            "Example 8.2": [["Computed", "Book"]],
            "Kelly F_1": [[_six(kelly[0]), _book(kelly[0], 1)]],
            "Kelly F_2": [[_six(kelly[1]), _book(kelly[1], 1)]],
            "Kelly F_1 + F_2": [[_six(total), _book(total, 1)]],
            "Scaled F_1": [[_six(capped[0]), _book(capped[0], 2)]],
            "Scaled F_2": [[_six(capped[1]), _book(capped[1], 2)]],
            "g at scaled F": [[_six(scaled), _book(scaled, 2)]],
            "g , all on F_2": [
                [str(printed), str(printed.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))]
            ],
        }

    def test_the_opening_s_findings(self, cov, kelly) -> None:
        scaled = growth_rate(proportional_cap(kelly, MAX_LEVERAGE), MEANS, cov)
        corner = best_allocation_at_cap(MEANS, cov).growth
        threshold = corner_threshold(MEANS, cov)
        self._has(
            f"the answer changes once the cap passes {threshold:.2f}.*",
            f"Both leverages shrunk to the cap grow at {_six(scaled)} a year. "
            f"The whole cap on strategy 2 grows at {corner:.3f} a year.",
            f"The exact growth rate with everything on strategy 2 is {corner:.3f}, halfway "
            f"between {corner - 0.005:.2f} and {corner + 0.005:.2f}",
        )

    def test_the_inputs(self) -> None:
        (m1, m2), (s1, s2) = MEANS, VOLS
        loss, gain = kelly_allocation.EX81_PNLS
        self._has(
            f"annual mean excess returns of {100 * m1:.0f} and {100 * m2:.0f} percent",
            f"annual volatilities of {100 * s1:.0f} and {100 * s2:.0f} percent",
            f"Their returns are uncorrelated, the risk-free rate is "
            f"{kelly_allocation.RISK_FREE:g} and the broker allows a leverage of "
            f"{MAX_LEVERAGE:g}",
            f"Example 8.1 holds a leverage of {EX81_LEVERAGE:g} on {_dollars(EX81_EQUITY)} of "
            f"equity, a {_dollars(EX81_LEVERAGE * EX81_EQUITY)} position, through a "
            f"{_dollars(loss)} loss and then a {_dollars(gain)} gain.",
        )
        assert CORRELATION == 0.0 and loss < 0 < gain

    def test_the_kelly_leverages_and_their_growth_rate(self, cov, kelly) -> None:
        total = float(np.abs(kelly).sum())
        sharpes = [m / s for m, s in zip(MEANS, VOLS, strict=True)]
        ret, drag = growth_terms(kelly, MEANS, cov)
        self._has(
            f"Strategy 1 gets {_six(kelly[0])} and strategy 2 gets {_six(kelly[1])}, for a gross "
            f"total of {_six(total)}. Chan prints {_book(kelly[0], 1)}, {_book(kelly[1], 1)} "
            f"and {_book(total, 1)}.",
            f"The Sharpe ratios are {_six(sharpes[0])} and {_six(sharpes[1])}, so the uncapped "
            f"Kelly leverages grow at {_six(growth_rate(kelly, MEANS, cov))} a year. Their return "
            f"is {_six(ret)} and their drag is {_six(drag)}, exactly half the return",
        )
        assert drag == pytest.approx(ret / 2, abs=1e-12)

    def test_the_positions_example_8_1_s_trades_leave(self) -> None:
        loss, gain = constant_leverage_chain()
        self._has(
            f"Beside the two positions Example 8.1’s trades leave, {_dollars(loss.target)} and "
            f"{_dollars(gain.target)}, these are all the figures",
            f"A {_dollars(loss.pnl)} loss leaves {_dollars(loss.equity_after)} of equity and a "
            f"{_dollars(loss.position_after_move)} position, so getting back to "
            f"{EX81_LEVERAGE:g} means selling {_dollars(loss.trade)}, which leaves a "
            f"{_dollars(loss.target)} position. A {_dollars(gain.pnl)} gain the next day leaves "
            f"{_dollars(gain.equity_after)} of equity and a {_dollars(gain.position_after_move)} "
            f"position, and getting back to {EX81_LEVERAGE:g} means buying "
            f"{_dollars(gain.trade)}, which leaves a {_dollars(gain.target)} position.",
        )
        assert loss.trade < 0 < gain.trade

    def test_lesson_2_s_proportional_split(self, cov, kelly) -> None:
        capped = proportional_cap(kelly, MAX_LEVERAGE)
        factor = MAX_LEVERAGE / float(np.abs(kelly).sum())
        self._has(
            f"Here that factor is {_six(factor)}, and the scaled leverages are "
            f"{_six(capped[0])} and {_six(capped[1])}, the book’s {_book(capped[0], 2)} and "
            f"{_book(capped[1], 2)}.",
            f"It grows at {_six(growth_rate(capped, MEANS, cov))}.",
            f"sets F1 = {MAX_LEVERAGE:g} − F2 and draws the growth rate as F2 runs from 0 to "
            f"{MAX_LEVERAGE:g}.",
        )

    def test_lesson_2_s_slope_and_its_parts(self, cov) -> None:
        """The slope along the line is a line in F2, so two points give it."""
        m1, m2 = MEANS
        c11, c22 = cov[0, 0], cov[1, 1]
        at_zero = m2 - m1 + c11 * MAX_LEVERAGE
        per_unit = c11 + c22
        at_cap = at_zero - per_unit * MAX_LEVERAGE
        corner = best_allocation_at_cap(MEANS, cov).leverages
        self._has(
            f"\\frac{{dg}}{{dF_2}} = {at_zero:.4f} - {per_unit:.4f}\\,F_2",
            f"At F2 = 0, with everything on strategy 1, the slope is {at_zero:.4f}.",
            f"because strategy 2’s mean is {m2 - m1:.2f} higher, and because moving leverage "
            f"off strategy 1 sheds drag at {c11 * MAX_LEVERAGE:.4f}, strategy 1’s variance of "
            f"{c11:.4f} times its leverage of {MAX_LEVERAGE:g}. Each unit of leverage moved "
            f"lowers the slope by {per_unit:.4f}, the two variances, {c11:.4f} and {c22:.4f}, "
            f"added together. At F2 = {MAX_LEVERAGE:g} the slope is still {at_cap:.4f}, above "
            "zero,",
            f"It peaks at F2 = {corner[1]:g} with F1 = {corner[0]:g}, everything on strategy 2.",
        )
        assert at_cap > 0

    def test_the_chart_s_alt_text(self, cov, kelly) -> None:
        capped = proportional_cap(kelly, MAX_LEVERAGE)
        corner = best_allocation_at_cap(MEANS, cov).growth
        peak = unbounded_allocation_at_cap(MEANS, cov, MAX_LEVERAGE)
        strategy_1 = growth_rate((MAX_LEVERAGE, 0.0), MEANS, cov)
        self._has(
            f"A solid curve rises from {_short(strategy_1)} at F2 = 0, with everything on "
            f"strategy 1, to {corner:.3f} at F2 = {MAX_LEVERAGE:g}, with everything on "
            "strategy 2.",
            f"at the proportional split, F2 = {_six(capped[1])} and g = "
            f"{_six(growth_rate(capped, MEANS, cov))}, and a filled green marker at the corner, "
            f"F2 = {MAX_LEVERAGE:g} and g = {corner:.3f}.",
            f"at the unbounded peak, F2 = {_six(peak.leverages[1])} and g = {_six(peak.growth)}, "
            f"labelled as not allowed, and falls slightly toward F2 = {BEYOND_CAP:g}.",
        )

    def test_why_the_corner_wins(self, cov, kelly) -> None:
        capped = proportional_cap(kelly, MAX_LEVERAGE)
        corner = best_allocation_at_cap(MEANS, cov)
        split_ret, split_drag = growth_terms(capped, MEANS, cov)
        corner_ret, corner_drag = growth_terms(corner.leverages, MEANS, cov)
        scaled = growth_rate(capped, MEANS, cov)
        self._has(
            f"The corner beats the proportional split by {_six(corner.growth - scaled)}, and "
            f"grows {_six(corner.growth / scaled)} times as fast.",
            f"**The proportional split** earns a return of {_six(split_ret)} and pays a drag of "
            f"{_six(split_drag)}.",
            f"**The corner** earns a return of {_short(corner_ret)} and pays a drag of "
            f"{_short(corner_drag)}.",
            f"So the proportional split saves {_six(corner_drag - split_drag)} of drag by giving "
            f"up {_six(corner_ret - split_ret)} of return.",
            "each unit of the cap earns its own strategy’s mean, twice as high on strategy 2.",
        )
        assert MEANS[1] == 2 * MEANS[0]

    def test_the_curve_s_other_end_and_the_share_of_kelly(self, cov, kelly) -> None:
        at_kelly = growth_rate(kelly, MEANS, cov)
        scaled = growth_rate(proportional_cap(kelly, MAX_LEVERAGE), MEANS, cov)
        corner = best_allocation_at_cap(MEANS, cov).growth
        strategy_1 = growth_rate((MAX_LEVERAGE, 0.0), MEANS, cov)
        self._has(
            f"At the curve’s other end, everything on strategy 1 grows at {_short(strategy_1)}, "
            f"less than half the corner’s rate. Against the {_six(at_kelly)} the uncapped Kelly "
            f"leverages would earn, the proportional split keeps {_six(scaled / at_kelly)} of "
            f"that rate and the corner {_six(corner / at_kelly)} of it. Both fall far short, "
            f"because the cap allows {MAX_LEVERAGE:g} of the {_six(float(np.abs(kelly).sum()))} "
            "Kelly asks for.",
        )
        assert strategy_1 < corner / 2

    def test_lesson_3_s_tie_and_the_three_rounding_rules(self, cov) -> None:
        corner = best_allocation_at_cap(MEANS, cov).growth
        exact = 2 * Fraction(60, 100) - 4 * Fraction(35, 100) ** 2 / 2
        tie, cent = Decimal(f"{corner:.3f}"), Decimal("0.01")
        self._has(
            f"The growth rate at the corner is exactly {exact.numerator}/{exact.denominator}, "
            f"which is {tie}. Chan prints 0.96.",
            f"**Round half up**, the rule taught in school, gives "
            f"{tie.quantize(cent, rounding=ROUND_HALF_UP)}.",
            f"which sends a tie to the even last digit, gives "
            f"{tie.quantize(cent, rounding=ROUND_HALF_EVEN)}.",
            f"**Round half down** gives {tie.quantize(cent, rounding=ROUND_HALF_DOWN)}.",
            f"both see a number below halfway and print {corner:.2f}. A report that formats the "
            f"corner the obvious way puts {round(corner, 2)} beside the book’s 0.96",
        )
        assert float(exact) == corner

    def test_lesson_4_s_unbounded_peak(self, cov) -> None:
        peak = unbounded_allocation_at_cap(MEANS, cov, MAX_LEVERAGE)
        corner = best_allocation_at_cap(MEANS, cov).growth
        self._has(
            f"finds it at F2 = {_six(peak.leverages[1])} and F1 = {_six(peak.leverages[0])}, "
            f"growing at {_six(peak.growth)}. That is higher than the corner’s {corner:.3f}",
            f"so the gross leverage, the short plus the long, is {_six(peak.gross)}, over the "
            f"cap of {MAX_LEVERAGE:g}.",
            f"because {_six(peak.growth)} rounds to the same {_book(peak.growth, 2)} the book "
            "prints for the corner.",
        )
        assert peak.growth > corner and peak.gross > MAX_LEVERAGE

    def test_lesson_5_s_threshold_and_long_only_shares(self, cov, kelly) -> None:
        threshold = corner_threshold(MEANS, cov)
        total = float(np.abs(kelly).sum())
        sharpes = [m / s for m, s in zip(MEANS, VOLS, strict=True)]

        def share(cap: float) -> float:
            return best_allocation_at_cap(MEANS, cov, cap).leverages[1] / cap

        self._has(
            f"## Lesson 5: everything on one strategy stays best only below a cap of "
            f"{threshold:.2f}\n",
            f"Its mean excess return is {100 * MEANS[1]:.0f} percent against {100 * MEANS[0]:.0f}.",
            f"strategy 2’s Sharpe ratio is {_six(sharpes[1])} against {_six(sharpes[0])}. With "
            f"the whole cap of {MAX_LEVERAGE:g} on it alone, it grows at "
            f"{best_allocation_at_cap(MEANS, cov).growth:.3f} against strategy 1’s "
            f"{_short(growth_rate((MAX_LEVERAGE, 0.0), MEANS, cov))}.",
            f"c12 is the covariance, which is {cov[0, 1]:g} here. That cap is {_six(threshold)}.",
            f"At a cap equal to the total Kelly leverage of {_six(total)}, the best allocation "
            f"is the Kelly pair itself, {_six(kelly[0])} and {_six(kelly[1])}.",
            f"the best one gives strategy 2 the whole cap at {_six(threshold)}, "
            f"{share(3.0):.3f} of it at a cap of 3, {share(4.0):.3f} at 4 and "
            f"{share(total):.3f} at the total of {_six(total)}.",
            f"is best only while the cap is below {_six(threshold / total)} of the total, "
            "about a quarter.",
        )
        assert share(threshold) == 1.0
        assert round(4 * threshold / total) == 1

    def test_lesson_6_s_long_only_corner_and_correlated_case(self, cov) -> None:
        case = TestTheLongOnlyLimit()
        (m1, m2), cap = case.MEANS, case.CAP
        vol = math.sqrt(case.COV[1, 1])
        correlation = case.COV[0, 1] / (math.sqrt(case.COV[0, 0]) * vol)
        alone = m2 / case.COV[1, 1]
        whole = best_allocation_at_cap(case.MEANS, case.COV, cap)
        hedge = case._hedge()
        hedge_ret, hedge_drag = growth_terms(hedge, case.MEANS, case.COV)
        _, f1, f2 = _gross_boundary_grid(MEANS, covariance(VOLS, 1.0), MAX_LEVERAGE, points=4_001)
        assert f1 >= 0.0 and f2 >= 0.0
        whole_ret, whole_drag = growth_terms(whole.leverages, case.MEANS, case.COV)
        self._has(
            f"finds the same corner at {best_allocation_at_cap(MEANS, cov).growth:.3f}.",
            f"On Chan’s means and volatilities at a cap of {MAX_LEVERAGE:g}, no correlation lets "
            "a short beat the best long-only split, even a correlation of 1.",
            f"Take two strategies with mean excess returns of {m1:.2f} and {m2:.2f}, a "
            f"volatility of {vol:.2f} each, a correlation of {correlation:.2f}, and a cap of "
            f"{cap:g}.",
            f"at its own Kelly leverage, {m2:.2f} / {vol:.2f}², which is {_six(alone)}. That "
            f"sits inside the cap and grows at exactly "
            f"{_short(growth_rate((0.0, alone), case.MEANS, case.COV))}. Spending the whole "
            f"cap of {cap:g} on strategy 2 grows at only {_short(whole.growth)}.",
            f"holds {_six(-hedge[0])} of strategy 1 short against {_six(hedge[1])} of strategy "
            f"2 long, a gross of {abs(hedge[0]) + abs(hedge[1]):g}, and grows at "
            f"{_six(growth_rate(hedge, case.MEANS, case.COV))}.",
            f"which earns a return of {_short(whole_ret)} and pays a drag of "
            f"{_short(whole_drag)}. The hedge earns {_six(hedge_ret)} and pays "
            f"{_six(hedge_drag)}. It gives up {_six(whole_ret - hedge_ret)} of return",
            f"loses strategy 1’s mean on {_six(-hedge[0])} of leverage, {_six(-hedge[0] * m1)}.",
            f"**The displaced long** loses {_six((cap - hedge[1]) * m2)}, strategy 2’s mean on "
            f"the {_six(-hedge[0])} of the gross cap that the short now uses.",
            f"the drag falls by {_six(whole_drag - hedge_drag)}.",
            f"under a cap below {corner_threshold(MEANS, cov):.2f}.",
        )
        assert alone < cap

    def test_what_this_replication_cannot_say(self, cov, kelly) -> None:
        self._has(
            f"so the {_six(growth_rate(kelly, MEANS, cov))} growth rate at the uncapped Kelly "
            "leverages has no published figure to compare with."
        )
