"""Pins for Chan's Examples 8.1 and 8.2, constant leverage and capped Kelly allocation.

This file is the single authority for every number any prose surface quotes
about these examples. ``docs/replication-log.md`` Entry 17 states those numbers
and derives none of them, and ``src/chan/kelly_allocation.py`` carries the
reasoning.

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
    kelly_leverages,
    main,
    proportional_cap,
    report,
    segment_stationary_point,
)


@pytest.fixture(scope="module")
def cov():
    return covariance(VOLS, CORRELATION)


@pytest.fixture(scope="module")
def kelly(cov):
    return kelly_leverages(MEANS, cov)


def _book(value: float, places: int) -> str:
    """Round half up from the true value. Only row 10 sits on a tie, and there
    half to even gives the same digit, so the choice of rule moves nothing."""
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

    def test_the_slope_along_the_line_is_positive_up_to_the_cap(self, cov) -> None:
        """Along ``F1 = 2 - F2`` the growth rate is a parabola, so its slope is a
        line in F2: 0.4352 at F2 = 0, falling by 0.1901 per unit. It is still
        positive at F2 = 2, which is why the peak is the corner."""

        def slope(f2: float, h: float = 1e-6) -> float:
            up = growth_rate((MAX_LEVERAGE - f2 - h, f2 + h), MEANS, cov)
            down = growth_rate((MAX_LEVERAGE - f2 + h, f2 - h), MEANS, cov)
            return (up - down) / (2 * h)

        assert slope(0.0) == pytest.approx(0.4352, abs=1e-8)
        assert slope(1.0) - slope(0.0) == pytest.approx(-0.1901, abs=1e-8)
        assert slope(MAX_LEVERAGE) == pytest.approx(0.0550, abs=1e-8)

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
        """Chan's claim, which is what row 8's verdict rests on."""
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

    def test_reading_location_3319_literally_gives_0_676(self, kelly) -> None:
        """The recovered text reads ``f2m2/2``. With the mean in place of the
        volatility, the proportional allocation grows at 0.676, which matches
        nothing the book prints, so the variance is what belongs there."""
        capped = proportional_cap(kelly, MAX_LEVERAGE)
        literal = sum(f * m - f**2 * m**2 / 2 for f, m in zip(capped, MEANS, strict=True))
        assert literal == pytest.approx(0.675932, abs=5e-7)


class TestWhereTheCornerStopsWinning:
    """Chan's "when Fmax is much smaller than" the total Kelly leverage, measured."""

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
    """The capped search is long-only, and here is a case where that binds.

    Two strategies with means of 0.05 and 0.30, a volatility of 0.30 each and a
    correlation of 0.95, under a cap of 4. The best long-only allocation puts
    everything on strategy 2. A short hedge in strategy 1 inside the same gross
    cap grows faster, so the docstring's restriction is a limit and not a theorem.
    """

    MEANS = (0.05, 0.30)
    COV = covariance((0.30, 0.30), 0.95)
    CAP = 4.0

    def test_the_long_only_answer(self) -> None:
        best = best_allocation_at_cap(self.MEANS, self.COV, self.CAP)
        assert best.leverages == (0.0, self.CAP)
        assert best.growth == pytest.approx(0.48, abs=1e-12)

    def test_a_short_hedge_inside_the_cap_beats_it(self) -> None:
        g, f1, f2 = _gross_boundary_grid(self.MEANS, self.COV, self.CAP)
        assert f1 == pytest.approx(-1.002849, abs=1e-3)
        assert f2 == pytest.approx(2.997151, abs=1e-3)
        assert g == pytest.approx(0.656501, abs=1e-6)
        assert abs(f1) + abs(f2) == pytest.approx(self.CAP, abs=1e-9)


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
        """With the means swapped the formula gives -2.448980, a cap nothing can be."""
        with pytest.raises(ValueError, match="not above"):
            corner_threshold((0.60, 0.30), covariance(VOLS))

    def test_a_cap_below_zero_is_refused(self) -> None:
        with pytest.raises(ValueError, match="below zero"):
            best_allocation_at_cap(MEANS, covariance(VOLS), -1.0)
        with pytest.raises(ValueError, match="below zero"):
            proportional_cap((4.4, 4.9), -1.0)

    def test_an_allocation_reports_its_gross_leverage(self) -> None:
        assert Allocation((-1.5, 0.5), 0.0).gross == 2.0


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
        assert "0.955" in line
        assert line.rstrip().endswith("0.96")

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
