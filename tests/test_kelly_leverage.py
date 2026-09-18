"""Pins for Chan's Kelly leverage on SPY, Example 6.2.

This file is the single authority for every number any prose surface quotes
about this experiment. ``docs/replication-log.md`` Entry 3 states those numbers
and derives none of them, and ``src/chan/kelly_leverage.py`` carries the
reasoning.

**Nothing here reproduces a published figure, and that is the result.** Chan
read SPY through 2007-12-28 on a 2008-vintage adjusted series. This reads a
2026 download of the same symbol over the same dates, so every gap below
measures eighteen years of restatement rather than a method. Reading his own
workbook is issue 138.

Two kinds of assertion live here and they are not interchangeable.

1. **Vintage pins**, which state what this committed series gives under the
   specification. They name their window, because ``f*`` runs from −2.82 to
   +4.90 inside this one vintage.
2. **Specification pins**, which hold a choice rather than a number. The
   dispersion form is the sharp one: the sample and population forms differ by
   5.7e-5 on the Sharpe ratio and by 6.8e-4 on the leverage, so an assertion at
   the leverage's printed precision passes on either and only the Sharpe ratio
   decides.

**One choice is not pinned here and saying so is the point.** The adjusted
close against the as-traded close moves the leverage by a quarter on Chan's own
workbook, which is the measurement that reverses his risk conclusion, and no
committed SPY vintage carries an as-traded column to check it against. The
module docstring cites it as his figure rather than as one this suite holds.
Issue 133 says a ``raw`` yfinance vintage is not the as-traded close anyway, so
recording one would not close it.

**A red assertion here means the data or this code, never the dependency.**
Every figure below is a mean, a standard deviation or a minimum computed in
numpy and pandas, and the reader path imports nothing from ``ithildincore``. So
the distinction ``tests/test_ithildincore_contract.py`` restores for the pair
replication is free here, and no contract case is owed.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from chan.kelly_leverage import (
    BLACK_MONDAY_DATE,
    BLACK_MONDAY_LOSS,
    BLOCK_DAYS,
    BOOK_END,
    BOOK_LEVERAGE,
    BOOK_REF,
    BOOK_START,
    DRAWDOWN_TOLERANCE,
    EQUITY,
    MIN_TRADING_DAYS,
    RISK_FREE,
    SAMPLING_RULES,
    TRADING_DAYS,
    VINTAGE_DATE,
    annualised_moments,
    main,
    rebalance,
    report,
    resample_close,
    run,
    sampling_scan,
    simple_returns,
    stress_test,
)
from chan.series import load_vintage
from chan.vintage import VintageUnavailable

# The windows this file pins, each named where it is used. Chan's own span is
# the only one with published figures beside it.
BEAR = ("2000-01-01", "2002-12-31")
BULL = ("2003-01-01", "2007-12-28")


@pytest.fixture(scope="module")
def spy():
    """The committed SPY vintage, resolved by the date it was downloaded.

    ``dated`` rather than symbol and basis alone, because issue 15 records a
    second SPY adjusted vintage and two of them make the bare lookup refuse and
    name the candidates. Written this way from the outset, that issue landing
    moves nothing here.
    """
    return load_vintage("SPY", dated=VINTAGE_DATE)


@pytest.fixture(scope="module")
def chan_window(spy):
    """Chan's own span on this vintage, which is the run the module defaults to."""
    _, close = spy
    return close[(close.index >= BOOK_START) & (close.index <= BOOK_END)]


def window(close, start, end):
    return close[(close.index >= start) & (close.index <= end)]


# ============================================================
# The vintage, which every number below is a function of
# ============================================================


class TestTheVintage:
    """What this run read, and that it is resolvable without guessing."""

    def test_the_entry_is_the_spy_download_this_module_names(self, spy) -> None:
        """Five identity fields, so a re-download cannot answer to the same pins."""
        entry, _ = spy
        assert entry.vendor == "yfinance"
        assert entry.symbol == "SPY"
        assert entry.price_basis == "adjusted"
        assert entry.download_date == VINTAGE_DATE
        assert entry.first_date == "1993-01-29"
        assert entry.last_date == "2026-09-18"
        assert entry.row_count == 8467

    def test_the_series_holds_every_row_the_entry_counts(self, spy) -> None:
        """The parse is what the moments run on, so its length is part of the pin."""
        entry, close = spy
        assert len(close) == entry.row_count
        assert close.index.is_monotonic_increasing
        assert bool(np.isfinite(close.to_numpy()).all())

    def test_chans_window_selects_the_days_his_workbook_holds(self, chan_window) -> None:
        """His ``example6_2.xls`` carries 3,758 bars over these dates and so does this.

        A match on the count is not a match on the closes. It says the two
        series agree on which days the exchange was open, which is what makes
        the gaps below a price difference rather than a calendar one.
        """
        assert len(chan_window) == 3758
        assert str(chan_window.index[0].date()) == BOOK_START
        assert str(chan_window.index[-1].date()) == BOOK_END


# ============================================================
# The specification, which is what the near misses hold
# ============================================================


class TestTheSpecificationRatherThanTheNumber:
    """Five choices decide the figures and three are invisible on the page.

    Each case below moves one of them and shows what it costs, because an
    assertion on the right number alone holds a number rather than a choice.
    """

    def test_the_sharpe_ratio_is_the_only_pin_that_separates_the_two_dispersions(
        self, chan_window
    ) -> None:
        """The sample form against the population form, at the book's own precision.

        This is the reason the Sharpe assertion below is tighter than the rule
        in ``docs/design.md`` would ask for. The book prints the leverage to
        three decimals and both forms round to the same three, so a suite
        pinning the leverage passes on the wrong specification and everything
        downstream inherits it quietly.
        """
        returns = simple_returns(chan_window)
        sample = annualised_moments(returns)
        population_sd = float(returns.std(ddof=0)) * math.sqrt(TRADING_DAYS)
        excess = sample.excess_annual
        population_sharpe = excess / population_sd
        population_leverage = excess / population_sd**2

        assert round(sample.sharpe, 4) != round(population_sharpe, 4)
        assert round(sample.leverage, 3) == round(population_leverage, 3)
        assert abs(sample.sharpe - population_sharpe) == pytest.approx(5.74e-5, abs=5e-7)

    def test_the_annualisation_is_252_and_the_near_counts_miss(self, chan_window) -> None:
        """251 and 250 are the plausible wrong answers and neither is close."""
        returns = simple_returns(chan_window)
        at_252 = annualised_moments(returns).mean_annual
        assert at_252 == pytest.approx(0.1129482956, abs=5e-10)
        for periods in (250, 251):
            other = annualised_moments(returns, periods_per_year=periods).mean_annual
            assert abs(other - at_252) > 4e-4

    def test_m_is_the_excess_return_and_not_the_total(self, chan_window) -> None:
        """Location 2869's prose says one thing and its arithmetic says another.

        Reading ``m`` as the total return puts the unlevered growth rate four
        points out, which reads as a gap in the data rather than a misread
        symbol. The difference is exactly the risk-free rate, so the wrong
        reading is not a small error anywhere.
        """
        moments = annualised_moments(simple_returns(chan_window))
        by_the_gloss = RISK_FREE + moments.mean_annual - moments.sd_annual**2 / 2.0
        assert moments.unlevered_growth == pytest.approx(0.0986480243, abs=5e-10)
        assert by_the_gloss - moments.unlevered_growth == pytest.approx(RISK_FREE, abs=5e-12)

    def test_the_returns_are_simple_and_not_logarithmic(self, chan_window) -> None:
        """Location 2777 fixes them as simple, and ``example6_3.m`` computes them.

        Log returns are the other obvious reading and they move the leverage,
        so the choice is a pin rather than a convention.
        """
        simple = annualised_moments(simple_returns(chan_window))
        logged = annualised_moments(np.log(chan_window).diff().dropna())
        assert abs(logged.leverage - simple.leverage) > 0.09

    def test_the_risk_free_rate_is_subtracted_per_period(self, chan_window) -> None:
        """Chan's ``excessRet=ret-repmat(0.04/252, size(ret))``.

        For an annualised mean this is algebraically the same as subtracting
        the annual rate once, so no printed figure moves. It is held because
        the time-scale check needs a per-period rate to be well-posed, and a
        refactor to the annual form would break that without moving a number
        anyone is looking at.
        """
        moments = annualised_moments(simple_returns(chan_window))
        assert moments.excess_annual == pytest.approx(moments.mean_annual - RISK_FREE, abs=5e-14)

    def test_a_non_finite_return_is_dropped_before_anything_is_computed(self) -> None:
        """``example6_3.m`` drops them and so does this.

        A zero close divides to an infinity rather than raising, so a series
        carrying one would annualise to an infinite mean and report a leverage
        of zero with nothing failing.
        """
        import pandas as pd

        closes = pd.Series(
            [10.0, 0.0, 12.0, 12.5, 13.0],
            index=pd.to_datetime(
                ["2026-01-02", "2026-01-05", "2026-01-06", "2026-01-07", "2026-01-08"]
            ),
        )
        returns = simple_returns(closes)
        assert len(returns) == 3
        assert bool(np.isfinite(returns.to_numpy()).all())

    def test_two_returns_are_the_fewest_a_sample_dispersion_can_carry(self) -> None:
        """One return has no ``n - 1`` denominator, so the refusal names why."""
        import pandas as pd

        one = pd.Series([0.01], index=pd.to_datetime(["2026-01-05"]))
        with pytest.raises(ValueError, match="at least two"):
            annualised_moments(one)


# ============================================================
# What this vintage computes, window by window
# ============================================================


class TestChansWindowOnAModernDownload:
    """The pinned run: Chan's dates, this vintage, his specification.

    Every figure here has a published counterpart and none of them reproduces
    it, which is the entry's result rather than its failure.
    """

    @pytest.fixture(scope="class")
    @staticmethod
    def moments(chan_window):
        return annualised_moments(simple_returns(chan_window))

    def test_the_moments(self, moments) -> None:
        """Mean and dispersion, at ten decimals because nothing rounds them."""
        assert moments.returns == 3757
        assert moments.mean_annual == pytest.approx(0.1129482956, abs=5e-10)
        assert moments.sd_annual == pytest.approx(0.1691169493, abs=5e-10)
        assert moments.excess_annual == pytest.approx(0.0729482956, abs=5e-10)

    def test_the_sharpe_ratio_at_a_tolerance_that_holds_the_specification(self, moments) -> None:
        """Tighter than the 5.7e-5 that separates the two dispersion forms.

        ``docs/design.md`` says an experiment pins a figure at the precision the
        book prints it, and four decimals would admit both forms. Entry 1's row
        4 is the precedent for going tighter where a choice turns on the
        margin. A figure computed from a committed vintage is derived rather
        than invented, which is what that rule was guarding against.
        """
        assert moments.sharpe == pytest.approx(0.4313482233, abs=5e-6)

    def test_the_kelly_leverage_and_the_growth_rates(self, moments) -> None:
        """``f* = m / s^2``, then ``g = r + S^2 / 2`` and ``g = r + m - s^2 / 2``."""
        assert moments.leverage == pytest.approx(2.5505913225, abs=5e-8)
        assert moments.half_kelly == pytest.approx(1.2752956613, abs=5e-8)
        assert moments.levered_growth == pytest.approx(0.1330306449, abs=5e-10)
        assert moments.unlevered_growth == pytest.approx(0.0986480243, abs=5e-10)

    def test_the_levered_growth_rate_is_chans_matrix_formula_in_the_scalar_case(
        self, moments
    ) -> None:
        """Location 2849 renders the formula as an image the highlights missed.

        It is recovered from ``example6_3.m``'s ``g=0.04+F'*C*F/2`` rather than
        reconstructed, and in one asset that is ``r + f*m/2``, which is the same
        as ``r + S^2/2``. Holding both spellings is what says the recovery was
        right.
        """
        assert moments.levered_growth == pytest.approx(
            RISK_FREE + moments.leverage * moments.excess_annual / 2.0, abs=5e-14
        )

    def test_no_published_figure_reproduces_and_every_gap_points_one_way(self, moments) -> None:
        """The whole entry, in one assertion.

        Chan prints 11.23, 16.91, 7.231, 0.4275, 2.528, 13.14 and 9.8. Every
        computed figure lands above its published one, which is what a
        dividend-adjusted series eighteen years further on does to a mean. The
        standard deviation is the exception and it moves by 0.0017 of a
        percentage point, which rounds to the book's own two decimals.
        """
        assert moments.mean_annual * 100 - 11.23 == pytest.approx(0.0648, abs=5e-5)
        assert moments.sd_annual * 100 - 16.91 == pytest.approx(0.0017, abs=5e-5)
        assert moments.excess_annual * 100 - 7.231 == pytest.approx(0.0638, abs=5e-5)
        assert moments.sharpe - 0.4275 == pytest.approx(0.0038, abs=5e-5)
        assert moments.leverage - 2.528 == pytest.approx(0.0226, abs=5e-5)
        assert moments.levered_growth * 100 - 13.14 == pytest.approx(0.1631, abs=5e-5)
        assert moments.unlevered_growth * 100 - 9.8 == pytest.approx(0.0648, abs=5e-5)
        assert round(moments.sd_annual * 100, 2) == 16.91


class TestTheWindowMovesItFurtherThanTheVintageDoes:
    """Why the window is an argument rather than a constant.

    Inside one vintage, on one specification, the leverage runs from a short of
    2.82 times equity to a long of 4.90. Any gap against the book is smaller
    than that by an order of magnitude, so a single number with no window named
    mixes vendor drift and sample choice and neither is recoverable.
    """

    def test_the_full_modern_span_has_no_published_counterpart(self, spy) -> None:
        """What SPY looks like today, which the book cannot speak to.

        This is the shape Entry 1's row 10 has: not a replication, and the row
        that makes the shelf life visible.
        """
        _, close = spy
        moments = annualised_moments(simple_returns(close))
        assert moments.returns == 8466
        assert moments.mean_annual == pytest.approx(0.1199817061, abs=5e-10)
        assert moments.sd_annual == pytest.approx(0.1853492595, abs=5e-10)
        assert moments.sharpe == pytest.approx(0.4315188865, abs=5e-6)
        assert moments.leverage == pytest.approx(2.3281392528, abs=5e-8)
        assert moments.levered_growth == pytest.approx(0.1331042747, abs=5e-10)
        assert moments.unlevered_growth == pytest.approx(0.1028045321, abs=5e-10)

    def test_the_bear_window_recommends_a_short(self, spy) -> None:
        """Requirement 10 is not hypothetical, and this is the window that shows it."""
        _, close = spy
        moments = annualised_moments(simple_returns(window(close, *BEAR)))
        assert moments.returns == 751
        assert moments.mean_annual == pytest.approx(-0.1254117226, abs=5e-10)
        assert moments.sd_annual == pytest.approx(0.2420323939, abs=5e-10)
        assert moments.leverage == pytest.approx(-2.8237047966, abs=5e-8)
        assert moments.half_kelly < 0.0

    def test_the_bull_window_nearly_doubles_it(self, spy) -> None:
        """The other end of the range, from the five years Chan's own span ends on."""
        _, close = spy
        moments = annualised_moments(simple_returns(window(close, *BULL)))
        assert moments.returns == 1256
        assert moments.mean_annual == pytest.approx(0.1228666934, abs=5e-10)
        assert moments.sd_annual == pytest.approx(0.1300811724, abs=5e-10)
        assert moments.leverage == pytest.approx(4.8972370287, abs=5e-8)

    def test_the_window_spread_dwarfs_the_gap_against_the_book(self, spy, chan_window) -> None:
        """The measurement the window argument exists for, stated as a comparison."""
        _, close = spy
        bear = annualised_moments(simple_returns(window(close, *BEAR))).leverage
        bull = annualised_moments(simple_returns(window(close, *BULL))).leverage
        chan = annualised_moments(simple_returns(chan_window)).leverage
        assert bull - bear > 7.7
        assert abs(chan - BOOK_LEVERAGE) < 0.03


# ============================================================
# The worked example and the rebalancing chain
# ============================================================


class TestTheWorkedExample:
    """Locations 2869 and 3021, which are arithmetic on a rounded leverage."""

    def test_the_books_own_chain_reproduces_to_the_cent(self) -> None:
        """All four printed figures, once 2.528 is taken as given.

        This is the one part of the example that does reproduce, and it does so
        because none of it reads a series. It is the book's rounded leverage
        multiplied out.
        """
        chain = rebalance(BOOK_LEVERAGE)
        assert chain.portfolio == pytest.approx(252_800.0, abs=5e-7)
        assert chain.debt == pytest.approx(152_800.0, abs=5e-7)
        assert chain.shocked_portfolio == pytest.approx(227_520.0, abs=5e-7)
        assert chain.shocked_equity == pytest.approx(74_720.0, abs=5e-7)
        assert round(chain.resized) == 188_892

    def test_the_printed_portfolio_comes_from_a_rounded_leverage(self) -> None:
        """$252,800 is the one printed figure with no exact counterpart.

        Chan rounded the leverage to three decimals before multiplying, so the
        published portfolio is derived from a rounded input. Anything under
        $12.50 of rounding in the leverage would land on the same $252,800, and
        the gap this shows is the reason the chain above is pinned on 2.528
        rather than on a computed number.
        """
        assert rebalance(2.5278).portfolio == pytest.approx(252_780.0, abs=5e-7)
        assert round(rebalance(2.5278).portfolio, -2) == 252_800.0

    def test_this_vintages_chain_is_a_different_account(self, chan_window) -> None:
        """What the same $100,000 buys on the leverage this run computed."""
        moments = annualised_moments(simple_returns(chan_window))
        chain = rebalance(moments.leverage)
        assert chain.portfolio == pytest.approx(255_059.1323, abs=5e-5)
        assert chain.debt == pytest.approx(155_059.1323, abs=5e-5)
        assert chain.shocked_portfolio == pytest.approx(229_553.2190, abs=5e-5)
        assert chain.shocked_equity == pytest.approx(74_494.0868, abs=5e-5)
        assert chain.resized == pytest.approx(190_003.9713, abs=5e-5)

    def test_the_chain_is_leverage_preserving_by_construction(self) -> None:
        """Resizing restores the leverage, which is what makes it a rebalance.

        Held for a second leverage and a second shock, because one set of
        numbers cannot tell the identity apart from four constants.
        """
        for leverage in (BOOK_LEVERAGE, 1.5, 4.0):
            for shock in (0.10, 0.20):
                chain = rebalance(leverage, shock=shock)
                assert chain.resized / chain.shocked_equity == pytest.approx(leverage, abs=5e-12)
                assert chain.portfolio - chain.debt == pytest.approx(EQUITY, abs=5e-9)

    def test_equity_is_exactly_gone_when_the_leverage_times_the_shock_reaches_one(self) -> None:
        """The wipeout the half-Kelly convention exists to avoid, as arithmetic.

        Four times equity into a 25 percent loss leaves nothing, and the resize
        has nothing to size. At the leverage this vintage gives, Chan's own
        20.47 percent constant is already most of the way there, which is what
        the stress test's full-Kelly figure says in percent.
        """
        wiped = rebalance(4.0, shock=0.25)
        assert wiped.shocked_equity == pytest.approx(0.0, abs=5e-9)
        assert wiped.resized == pytest.approx(0.0, abs=5e-9)

    def test_the_equity_moves_by_the_leverage_times_the_shock(self) -> None:
        """Why leverage is the thing the stress test measures.

        A 10 percent loss on a 2.528-times position costs 25.28 percent of
        equity. That identity is what turns a 20.47 percent day into a wipeout
        at full Kelly, and it holds for any leverage and any shock.
        """
        for leverage in (BOOK_LEVERAGE, 1.0, 3.7):
            chain = rebalance(leverage, shock=0.10)
            lost = (EQUITY - chain.shocked_equity) / EQUITY
            assert lost == pytest.approx(leverage * 0.10, abs=5e-12)


# ============================================================
# The stress test, which replicates a verdict rather than a figure
# ============================================================


class TestTheStressTest:
    """Location 3083, where the book states a conclusion rather than a number."""

    @pytest.fixture(scope="class")
    @staticmethod
    def stress(chan_window):
        returns = simple_returns(chan_window)
        return stress_test(annualised_moments(returns), returns)

    def test_the_tolerance_allows_about_one_times_equity(self, stress) -> None:
        """The book's "about 1" is 0.20 / 0.2047, and both inputs are its own."""
        assert stress.allowed_leverage == pytest.approx(0.9770395701, abs=5e-10)
        assert stress.allowed_leverage == pytest.approx(
            DRAWDOWN_TOLERANCE / BLACK_MONDAY_LOSS, abs=5e-15
        )

    def test_the_conclusion_has_a_threshold_and_this_run_clears_it(self, stress) -> None:
        """Chan's conclusion holds exactly while ``f*`` is above 1.954079.

        The margin is thinner than 2.55 against 1.95 sounds. On his own
        workbook the as-traded close gives 1.9341, which is below the threshold
        and reverses the conclusion, so the price basis alone spends it.
        """
        assert stress.threshold == pytest.approx(1.9540791402, abs=5e-10)
        assert stress.half_kelly == pytest.approx(1.2752956613, abs=5e-8)
        assert stress.survives is True
        assert 1.9341 < stress.threshold

    def test_the_verdict_turns_over_at_the_threshold_and_not_before(self, chan_window) -> None:
        """A boundary held on both sides, because a one-sided pin passes on a
        comparison that always returns true."""
        returns = simple_returns(chan_window)
        moments = annualised_moments(returns)
        threshold = stress_test(moments, returns).threshold
        for leverage, expected in (
            (threshold * 1.001, True),
            (threshold, False),
            (threshold * 0.999, False),
        ):
            faked = type(moments)(**{**moments.__dict__, "leverage": leverage})
            assert stress_test(faked, returns).survives is expected

    def test_black_monday_is_a_book_constant_and_not_a_vintage_figure(self, stress) -> None:
        """SPY's first bar is 1993-01-29, six years after 1987-10-19.

        The two losses are separate fields on purpose. Reporting the book's
        20.47 percent as something the series holds would be a wrong fact about
        where the number came from, and no SPY vintage of any span can check it.
        """
        assert stress.book_loss == BLACK_MONDAY_LOSS == 0.2047
        assert stress.book_day == BLACK_MONDAY_DATE == "1987-10-19"
        assert stress.worst_day == "1997-10-27"
        assert stress.worst_loss == pytest.approx(-0.0724732862, abs=5e-10)
        assert abs(stress.worst_loss) < stress.book_loss

    def test_the_full_kelly_cost_of_that_day_is_reported_and_not_published(self, stress) -> None:
        """2.5506 times 20.47 percent is 52.21 percent of equity gone in a day.

        The book does not print this. It prints the comparison against
        half-Kelly instead, and this is the thing that comparison is protecting
        against.
        """
        assert stress.full_kelly_equity_loss == pytest.approx(0.5221060437, abs=5e-10)
        assert stress.full_kelly_equity_loss > 0.5

    def test_the_worst_day_is_the_windows_own(self, spy) -> None:
        """A different window has a different worst day, so the field is read
        from the returns rather than carried as a constant."""
        _, close = spy
        returns = simple_returns(close)
        full = stress_test(annualised_moments(returns), returns)
        assert full.worst_day == "2020-03-16"
        assert full.worst_loss == pytest.approx(-0.1094237801, abs=5e-10)


# ============================================================
# Time-scale independence, which is two claims
# ============================================================


class TestTimeScaleIndependence:
    """Chan's claim is exactly true in one reading and 43 to 47 percent wrong
    in the other, and the run has to say which it is showing."""

    def test_the_annualisation_factor_cancels_exactly(self, chan_window) -> None:
        """The identity, which is why testing it proves nothing about the data.

        ``f*`` from the annualised moments is ``f*`` from the per-period ones,
        because the factor divides out between the mean and the variance. The
        agreement is to floating-point noise rather than bit-for-bit, since the
        annualised path squares a square root.
        """
        moments = annualised_moments(simple_returns(chan_window))
        assert moments.leverage == pytest.approx(moments.period_leverage, rel=1e-12)

    def test_resampling_is_what_actually_moves_it(self, chan_window) -> None:
        """Every monthly rule lands 40-odd percent above the daily figure.

        The driver is the variance ratio rather than the mean: annualised
        monthly variance is well under the daily one, and dividing a similar
        mean by a smaller variance is what lifts the leverage.
        """
        scan = sampling_scan(chan_window)
        daily = scan["daily"]
        assert daily.leverage == pytest.approx(2.5505913225, abs=5e-8)
        assert scan["month-end"].returns == 179
        assert scan["month-end"].leverage == pytest.approx(3.7174520000, abs=5e-6)
        assert scan["month-end-complete"].returns == 178
        assert scan["month-end-complete"].leverage == pytest.approx(3.7460430000, abs=5e-6)
        assert scan["block-21"].returns == 178
        assert scan["block-21"].leverage == pytest.approx(3.6438410000, abs=5e-6)
        for rule in ("month-end", "month-end-complete", "block-21"):
            lift = scan[rule].leverage / daily.leverage - 1.0
            assert 0.42 < lift < 0.48

    def test_the_conclusion_does_not_depend_on_which_monthly_rule_is_picked(
        self, chan_window
    ) -> None:
        """Three plausible readings of "monthly", within 0.11 of each other.

        That spread is what makes naming the rule enough. The pin has to be
        reproducible and the finding does not turn on the choice.
        """
        scan = sampling_scan(chan_window)
        monthly = [scan[rule].leverage for rule in SAMPLING_RULES if rule != "daily"]
        assert max(monthly) - min(monthly) < 0.11

    def test_the_monthly_rules_annualise_by_twelve(self, chan_window) -> None:
        """A rule that kept 12 periods a year and annualised by 252 would report
        a leverage twenty-one times too small, and nothing else would look wrong."""
        for rule in SAMPLING_RULES:
            sampled, periods = resample_close(chan_window, rule)
            assert periods == (float(TRADING_DAYS) if rule == "daily" else 12.0)
        assert TRADING_DAYS / BLOCK_DAYS == 12.0

    def test_the_month_end_rules_differ_by_exactly_the_partial_final_month(
        self, chan_window
    ) -> None:
        """Chan's span stops on 2007-12-28, three days before its month does."""
        plain, _ = resample_close(chan_window, "month-end")
        complete, _ = resample_close(chan_window, "month-end-complete")
        assert len(plain) - len(complete) == 1
        assert str(plain.index[-1].date()) == BOOK_END
        assert str(complete.index[-1].date()) == "2007-11-30"

    def test_a_complete_final_month_is_kept(self, spy) -> None:
        """The rule drops a partial month rather than always dropping the last one.

        Checked on a window ending on the last trading day of November 2007,
        where the two rules have to agree.
        """
        _, close = spy
        ends_on_a_month = window(close, BOOK_START, "2007-11-30")
        plain, _ = resample_close(ends_on_a_month, "month-end")
        complete, _ = resample_close(ends_on_a_month, "month-end-complete")
        assert len(plain) == len(complete)

    def test_an_unknown_rule_is_refused_by_name(self) -> None:
        """The rule is part of the pin, so a typo has to stop rather than
        silently fall through to the daily case."""
        with pytest.raises(ValueError, match="sampling rule"):
            resample_close(None, "weekly")

    def test_a_window_too_short_for_a_rule_yields_nothing_rather_than_raising(self, spy) -> None:
        """A 40-day window has two monthly closes at most, so a rule that cannot
        carry a sample dispersion comes back as ``None`` and the report says so."""
        _, close = spy
        scan = sampling_scan(window(close, "2007-11-01", BOOK_END))
        assert scan["daily"] is not None
        assert scan["block-21"] is None


# ============================================================
# The report, which is four of the twelve requirements
# ============================================================


class TestTheReportSaysWhatItComputed:
    """Nothing else in this file executes ``report``, ``run`` or ``main``.

    The repo already learned this twice. ``TestReportNamesItsBasis`` in
    ``tests/test_pair_cointegration.py`` exists because a ported report
    announced the wrong price basis while reading a different file, and nothing
    noticed. A report that names the wrong quantity is worse than one that
    names none.
    """

    def test_the_report_prints_the_figures_it_labels(self, spy, chan_window, capsys) -> None:
        """Every labelled figure carries the value its label claims."""
        entry, _ = spy
        moments = annualised_moments(simple_returns(chan_window))
        report(entry, chan_window)
        out = capsys.readouterr().out
        assert f"{moments.mean_annual * 100:.4f}%" in out
        assert f"{moments.sd_annual * 100:.4f}%" in out
        assert f"{moments.sharpe:.4f}" in out
        assert f"{moments.leverage:.4f}" in out
        assert f"{moments.levered_growth * 100:.4f}%" in out
        assert f"{moments.unlevered_growth * 100:.4f}%" in out
        assert f"{moments.half_kelly:.4f}" in out

    def test_the_report_names_the_vintage_and_the_specification(
        self, spy, chan_window, capsys
    ) -> None:
        """Requirement 8. A figure separable from the vintage that produced it is
        a figure nobody can check."""
        entry, _ = spy
        report(entry, chan_window)
        out = capsys.readouterr().out
        assert entry.path in out
        assert f"downloaded {VINTAGE_DATE}" in out
        assert "yfinance adjusted" in out
        assert "adjusted close, simple daily returns" in out
        assert "sample sd (n-1)" in out
        assert "m is the excess return" in out

    def test_the_report_states_the_gap_only_against_chans_own_window(
        self, spy, chan_window, capsys
    ) -> None:
        """A gap against a published figure needs the window the figure came from.

        On any other span there is no published counterpart, so the column is
        dropped and the report says why rather than printing a comparison a
        reader would take for one.
        """
        entry, close = spy
        report(entry, chan_window)
        on_chans_window = capsys.readouterr().out
        assert "the book   gap" in on_chans_window
        assert "11.2948%     11.23%   +0.06" in on_chans_window

        report(entry, window(close, *BEAR))
        elsewhere = capsys.readouterr().out
        assert "no figure below has a published counterpart" in elsewhere
        assert f"The book's own span is {BOOK_START} .. {BOOK_END}." in elsewhere
        assert "the book   gap" not in elsewhere
        # The published values appear once more, in BOOK_REF on the second line,
        # which quotes what the book prints rather than comparing anything. The
        # assertion is on the table's own row so it separates the two.
        assert "11.23%   +" not in elsewhere

    def test_a_negative_leverage_arrives_as_a_line_and_not_an_exception(self, spy, capsys) -> None:
        """Requirement 10. Nothing has failed, so nothing raises, and the only
        thing between a reader and a wrong-signed recommendation is this line."""
        entry, close = spy
        report(entry, window(close, *BEAR))
        out = capsys.readouterr().out
        assert "The leverage is negative" in out
        assert "recommends a short" in out
        assert "half of a negative leverage is a smaller" in out
        assert "the comparison is not made" in out

    def test_a_positive_leverage_prints_no_negative_note(self, spy, chan_window, capsys) -> None:
        """The other half of the branch, which a one-sided case would leave
        passing on a report that printed the note unconditionally."""
        entry, _ = spy
        report(entry, chan_window)
        out = capsys.readouterr().out
        assert "The leverage is negative" not in out
        assert "SURVIVES" in out

    def test_the_report_carries_the_epistemic_label(self, spy, chan_window, capsys) -> None:
        """Requirement 11. This is the first result here whose output is a
        leverage rather than a statistic, so it is the first a reader could
        mistake for advice."""
        entry, _ = spy
        report(entry, chan_window)
        out = " ".join(capsys.readouterr().out.split())
        assert "exploratory by construction" in out
        assert "reference point rather than a recommendation" in out
        assert "his constant applied to whatever window was read" in out

    def test_the_report_keeps_the_book_constant_apart_from_the_vintages_worst_day(
        self, spy, chan_window, capsys
    ) -> None:
        """Two losses on two lines, because one of them is not in any SPY series."""
        entry, _ = spy
        report(entry, chan_window)
        out = " ".join(capsys.readouterr().out.split())
        assert f"20.47% on {BLACK_MONDAY_DATE} <- a book constant, outside SPY" in out
        assert "worst one-day loss in this window 7.25% on 1997-10-27" in out

    def test_the_report_says_which_time_scale_reading_it_is_showing(
        self, spy, chan_window, capsys
    ) -> None:
        """Both readings in one block, because the identity and the measurement
        answer different questions and a report showing one reads as the other."""
        entry, _ = spy
        report(entry, chan_window)
        out = " ".join(capsys.readouterr().out.split())
        assert "as an identity it holds exactly" in out
        assert "the factor cancels between the mean and the variance" in out
        assert "Resampling is what moves it" in out
        for rule in SAMPLING_RULES:
            assert rule in out

    def test_the_book_reference_quotes_what_the_book_prints(self) -> None:
        """``BOOK_REF`` is the report's second line and it restates eight published
        figures, so a change to any of them has to move it too."""
        for printed in ("11.23%", "16.91%", "7.231%", "0.4275", "2.528", "13.14%", "9.8%", "1.26"):
            assert printed in BOOK_REF
        assert "locations 2858, 2869 and 3083" in BOOK_REF


class TestTheRunAndTheCli:
    """Requirement 12: a refusal is a line a reader sees, not a traceback."""

    def test_the_default_run_is_chans_own_window(self, capsys) -> None:
        """The default holds the window fixed so the vintage is the only
        difference from the book."""
        run()
        out = capsys.readouterr().out
        assert f"{BOOK_START} .. {BOOK_END}" in out
        assert "3,758 closes, 3,757 daily returns" in out

    def test_the_cli_passes_every_argument_through(self, monkeypatch, capsys) -> None:
        """A dropped argument leaves the report describing a run nobody asked for."""
        monkeypatch.setattr(
            "sys.argv",
            ["chan.kelly_leverage", "--start", BEAR[0], "--end", BEAR[1], "--risk-free", "0.0"],
        )
        main()
        out = capsys.readouterr().out
        assert "2000-01-03 .. 2002-12-31" in out
        assert "751 daily returns" in out
        assert "risk-free 0% subtracted" in out

    def test_a_window_with_too_few_days_exits_with_a_line(self, monkeypatch) -> None:
        """Not a pandas traceback. The message names the window and the span the
        vintage actually holds, which is the two things a reader needs to fix it."""
        monkeypatch.setattr(
            "sys.argv", ["chan.kelly_leverage", "--start", "2007-12-01", "--end", BOOK_END]
        )
        with pytest.raises(SystemExit) as exited:
            main()
        message = str(exited.value)
        assert f"need >= {MIN_TRADING_DAYS}" in message
        assert "1993-01-29..2026-09-18" in message

    def test_an_unavailable_vintage_exits_with_the_readers_own_message(self, monkeypatch) -> None:
        """``chan.pair_cointegration.main`` catches the same refusal the same way.

        A refusal naming which vintage and which state is worth nothing under a
        twenty-line traceback, and the reader already wrote the sentence.
        """
        monkeypatch.setattr("sys.argv", ["chan.kelly_leverage", "--dated", "1999-01-01"])
        with pytest.raises(SystemExit) as exited:
            main()
        assert "1999-01-01" in str(exited.value)

    def test_the_reader_refuses_that_date_on_its_own(self) -> None:
        """The message the case above relays comes from the reader rather than
        from this module, so the catch is a relay and not a second sentence."""
        with pytest.raises(VintageUnavailable, match="1999-01-01"):
            load_vintage("SPY", dated="1999-01-01")
