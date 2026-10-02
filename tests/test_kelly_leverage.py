"""Pins for Chan's Kelly leverage on SPY, Example 6.2.

This file is the single authority for every number any prose surface quotes
about this experiment. ``docs/replication-log.md`` Entry 3 states those numbers
and derives none of them, and ``src/chan/kelly_leverage.py`` carries the
reasoning.

**Two vintages are read here, and they are not interchangeable.**

1. **A 2026 download**, which most of this file pins. Chan read SPY through
   2007-12-28 on a 2008-vintage adjusted series, so every level a modern
   download gives over the same dates lands high, and the gaps measure how two
   downloads eighteen years apart differ rather than a method. The standard
   deviation is the exception, at the two decimals the book prints.
2. **Chan's own ``example6_2.xls``**, committed as ``data/spy_chan.csv`` and
   pinned in the section headed for it near the end. Every figure he printed
   from a series reproduces from it at the precision he printed it, and the
   two-vintage comparison there is what says why the modern download misses:
   the whole gap in the mean sits on about ten days on or beside SPY's
   quarterly ex-dividend dates, mostly raising the 2026 mean. That moves a
   mean and barely touches a standard deviation. That one download folds in
   all or part of a payout the other does not, on those days, is measured on
   issue 138 rather than pinned here.

Two kinds of assertion live here and they are not interchangeable.

1. **Vintage pins**, which state what this committed series gives under the
   specification. They name their window, because ``f*`` runs from −2.82 to
   +4.90 inside this one vintage.
2. **Specification pins**, which hold a choice rather than a number. The
   dispersion form is the sharp one: the sample and population forms differ by
   5.74e-5 on the Sharpe ratio and by 6.79e-4 on the leverage, so an assertion at
   the leverage's printed precision passes on either and only the Sharpe ratio
   decides.

**One choice is not pinned here and saying so is the point.** The adjusted
close against the as-traded close moves the leverage by a quarter on Chan's own
workbook, which is the measurement that reverses his risk conclusion, and no
committed SPY vintage carries an as-traded column to check it against. The
module docstring cites it as his figure rather than as one this suite holds.
Issue 133 says a ``raw`` yfinance vintage is not the as-traded close anyway, so
recording one would not close it. Issue 192 commits the workbook's own
as-traded column and pins the figure against it.

**A red assertion here means the data or this code, never the dependency.**
Every figure below is a mean, a standard deviation or a minimum computed in
numpy and pandas, and the reader path imports nothing from ``ithildincore``. So
the distinction ``tests/test_ithildincore_contract.py`` restores for the pair
replication is free here, and no contract case is owed.
"""

from __future__ import annotations

import contextlib
import inspect
import io
import math
import re

import numpy as np
import pandas as pd
import pytest

from chan.kelly_leverage import (
    _PUBLISHED,
    BLACK_MONDAY_DATE,
    BLACK_MONDAY_LOSS,
    BLOCK_DAYS,
    BOOK_END,
    BOOK_LEVERAGE,
    BOOK_REF,
    BOOK_START,
    DIVIDEND_MONTHS,
    DRAWDOWN_TOLERANCE,
    EQUITY,
    LARGEST_DAYS,
    MIN_TRADING_DAYS,
    RISK_FREE,
    SAMPLING_RULES,
    TRADING_DAYS,
    VINTAGE_DATE,
    _worked_example,
    annualised_moments,
    compare_vintages,
    main,
    rebalance,
    report,
    resample_close,
    run,
    sampling_scan,
    simple_returns,
    stress_test,
)
from chan.series import load_close, load_vintage
from chan.vintage import VintageUnavailable

# The windows this file pins, each named where it is used. Chan's own span is
# the only one with published figures beside it.
BEAR = ("2000-01-01", "2002-12-31")
BULL = ("2003-01-01", "2007-12-28")


@pytest.fixture(scope="module")
def spy():
    """The committed SPY vintage, resolved by the date it was downloaded.

    ``dated`` rather than symbol and basis alone, against a second yfinance SPY
    download arriving, because two of those make the bare lookup refuse and
    name the candidates. Issue 15 was expected to be that and was not: it reads
    this file as its equity leg rather than downloading the symbol again.
    Written this way from the outset, neither that issue landing nor the next
    SPY download moves anything here.
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
        # Both separations are quoted in prose, so both are held here. Without
        # this line the leverage's is covered only by the three-decimal
        # equality above, which admits anything up to about 0.001.
        assert population_leverage - sample.leverage == pytest.approx(6.79e-4, abs=5e-6)

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

        A zero close divides to an infinity rather than raising. A series
        carrying one annualises to an infinite mean and, because the dispersion
        subtracts that mean, to a standard deviation of ``nan``. The leverage
        is then ``nan``, which prints and compares without failing anywhere.
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

    Every figure here has a published counterpart and only the dispersion
    reproduces it, which is the 2026 download's result rather than its failure.
    His own workbook reproduces all of them, near the end of this file.
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

    def test_every_level_moved_and_only_the_dispersion_reproduces(self, moments) -> None:
        """The whole entry, in one assertion.

        Chan prints 11.23, 16.91, 7.231, 0.4275, 2.528, 13.14 and 9.8. Every
        computed figure lands above its published one, because the two downloads
        differ on about ten quarterly dividends inside the window. The
        standard deviation is the exception. It moves by 0.0017 of a percentage
        point and rounds to the book's own two decimals, so the last assertion
        here is the one row of Entry 3 that reproduces from the 2026 download.
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
        """All four printed figures and the debt, once 2.528 is taken as given.

        This is the one part of the example that does reproduce, and it does so
        because none of it reads a series. It is the book's rounded leverage
        multiplied out. The resized position is held to the cent at
        $188,892.16, which the book prints rounded to the dollar, and the
        rounding is asserted separately.
        """
        chain = rebalance(BOOK_LEVERAGE)
        assert chain.portfolio == pytest.approx(252_800.0, abs=5e-7)
        assert chain.debt == pytest.approx(152_800.0, abs=5e-7)
        assert chain.shocked_portfolio == pytest.approx(227_520.0, abs=5e-7)
        assert chain.shocked_equity == pytest.approx(74_720.0, abs=5e-7)
        assert chain.resized == pytest.approx(188_892.16, abs=5e-3)
        assert round(chain.resized) == 188_892

    def test_the_printed_portfolio_comes_from_a_rounded_leverage(self) -> None:
        """$252,800 is the one printed figure with no exact counterpart.

        Chan rounded the leverage to three decimals before multiplying, so the
        published portfolio is derived from a rounded input rather than from
        the leverage his workbook computed. His four-decimal 2.5278 buys
        $252,780, twenty dollars under what he printed, and the rounded 2.528
        buys $252,800 exactly. That is why the chain above is pinned on 2.528
        rather than on any computed number.
        """
        assert rebalance(2.5278).portfolio == pytest.approx(252_780.0, abs=5e-7)
        assert rebalance(BOOK_LEVERAGE).portfolio - rebalance(2.5278).portfolio == pytest.approx(
            20.0, abs=5e-7
        )

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
        """SPY's first bar is 1993-01-29, five years after 1987-10-19.

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
    """The cases that execute ``report`` on the 2026 download.

    ``TestTheReportOnHisWorkbook`` does the same for Chan's own workbook, and
    the CLI classes below drive ``run`` and ``main``.

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
        # The rate's treatment, for the rows it applies to. The spec line at
        # the top names the daily one only, and three of the four rows below
        # are monthly, so without this the report's one statement about the
        # rate is accurate for a quarter of what it prints.
        assert "subtracts the rate over its own period, 0.04/252 a day and 0.04/12 a month" in out
        assert "a daily f* needs a daily r" in out
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
        """A dropped argument leaves the report describing a run nobody asked for.

        ``--dated`` is driven here too, and the header's vintage line is what
        shows it arrived. Without that line the date is an argument the report
        never mentions, and dropping it is invisible on the one SPY download
        committed today. ``--chan`` has its own case below, because it reads a
        different file and the header has to name that one.
        """
        monkeypatch.setattr(
            "sys.argv",
            [
                "chan.kelly_leverage",
                "--start",
                BEAR[0],
                "--end",
                BEAR[1],
                "--dated",
                VINTAGE_DATE,
                "--risk-free",
                "0.0",
            ],
        )
        main()
        out = capsys.readouterr().out
        assert "2000-01-03 .. 2002-12-31" in out
        assert "751 daily returns" in out
        assert "risk-free 0% subtracted" in out
        assert f"vintage: yfinance_spy_adjusted_1993-01-29_{VINTAGE_DATE}" in out
        assert f"downloaded {VINTAGE_DATE}" in out

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


# ============================================================
# The report's labels, which a substring assertion does not hold
# ============================================================


def cell(out: str, label: str) -> str:
    """What the line labelled ``label`` prints after it.

    A report is a table of labels and values, and an assertion that a value
    appears *somewhere* in the output holds neither. A mutation pass over this
    module moved nine values onto the wrong labels and the suite stayed green
    every time, including one that printed the unlevered growth rate under the
    levered label, which is the comparison Example 6.2 exists to make.

    The label has to be followed by at least two spaces, so ``month-end`` does
    not match ``month-end-complete``.
    """
    for line in out.splitlines():
        found = re.match(rf"\s*{re.escape(label)}\s\s+(.*?)\s*$", line)
        if found:
            return found.group(1)
    raise AssertionError(f"no line labelled {label!r} in:\n{out}")


class TestEveryLabelCarriesItsOwnValue:
    """The mutation class that survived everything, closed one table at a time.

    Each case reads the value off the line its label owns rather than off the
    whole report. ``tests/test_pair_cointegration.py``'s ``TestReportNamesItsBasis``
    is the precedent, and this is what extending it to four tables looks like.
    """

    @pytest.fixture(scope="class")
    @staticmethod
    def printed(spy, chan_window):
        entry, _ = spy
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            report(entry, chan_window)
        return buffer.getvalue()

    def test_the_published_table_binds_all_three_columns(self, printed, chan_window) -> None:
        """Computed, published and gap, on the row that claims them.

        The gap is asserted too, because the published string and the number
        the gap is computed from are separate fields of ``_PUBLISHED`` and
        nothing else makes them agree.
        """
        moments = annualised_moments(simple_returns(chan_window))
        for label, field, as_percent, printed_figure, value, decimals in _PUBLISHED:
            computed = getattr(moments, field) * (100.0 if as_percent else 1.0)
            shown = f"{computed:.4f}%" if as_percent else f"{computed:.4f}"
            gap = round(computed - value, decimals) + 0.0
            assert (
                cell(printed, label)
                == (f"{shown:>12}   {printed_figure:>8}   {gap:+.{decimals}f}").strip()
            )

    def test_the_table_is_the_specification_and_so_is_pinned_as_one(self) -> None:
        """``_PUBLISHED`` decides which figure wears which label, so no case
        that reads its expectation out of it can hold that.

        Swapping the levered and unlevered rows' fields and labels together
        passes every other assertion in this class, because they all walk this
        tuple. The report then tells a reader the unlevered growth rate is
        13.3031 percent and the levered rate 9.8648, which is the comparison
        Example 6.2 exists to make, printed backwards. The literal is what
        stands between that and a green suite.
        """
        assert _PUBLISHED == (
            ("mean annual return", "mean_annual", True, "11.23%", 11.23, 2),
            ("annualised standard deviation", "sd_annual", True, "16.91%", 16.91, 2),
            ("mean excess return", "excess_annual", True, "7.231%", 7.231, 3),
            ("Sharpe ratio", "sharpe", False, "0.4275", 0.4275, 4),
            ("optimal Kelly leverage f*", "leverage", False, "2.528", 2.528, 3),
            ("levered growth rate", "levered_growth", True, "13.14%", 13.14, 2),
            ("unlevered growth rate", "unlevered_growth", True, "9.8%", 9.8, 1),
            ("half-Kelly leverage", "half_kelly", False, "1.26", 1.26, 2),
        )

    def test_the_published_table_prints_every_row_it_holds_and_no_other(self, printed) -> None:
        """A deleted row is invisible to an assertion that reads rows by name.

        The excess return is the row this catches: it is the one quantity the
        report's other assertions do not reach, and choice 4 of the module
        docstring calls it the specification's sharp edge.
        """
        labels = [row[0] for row in _PUBLISHED]
        assert [line.strip().split("  ")[0] for line in published_rows(printed)] == labels

    def test_the_worked_example_puts_this_vintage_left_and_the_book_right(
        self, printed, chan_window
    ) -> None:
        """Two columns of dollars, and swapping them reads as a reproduction."""
        mine = rebalance(annualised_moments(simple_returns(chan_window)).leverage)
        book = rebalance(BOOK_LEVERAGE)
        for label, field in (
            ("portfolio", "portfolio"),
            ("borrowed", "debt"),
            ("after SPY falls 10%", "shocked_portfolio"),
            ("equity left", "shocked_equity"),
            ("resized at the same leverage", "resized"),
        ):
            left = f"${getattr(mine, field):,.2f}"
            right = f"${getattr(book, field):,.2f}"
            assert cell(printed, label) == f"{left:>16}   {right:>16}".strip()

    def test_the_worked_examples_header_names_the_leverage_each_column_used(
        self, printed, chan_window
    ) -> None:
        """A header that stops naming its own leverage is a column nobody can check."""
        leverage = annualised_moments(simple_returns(chan_window)).leverage
        assert f"at f* = {leverage:.4f}" in printed
        assert f"at {BOOK_LEVERAGE}" in printed

    def test_the_equity_the_report_is_given_reaches_the_worked_example(
        self, spy, chan_window, capsys
    ) -> None:
        """``report`` takes an equity and nothing called it with another one.

        The book's $100,000 is the only value any other case uses, so passing
        the module constant straight through instead of the argument was
        invisible. A knob nobody turns is a knob nobody holds.
        """
        entry, _ = spy
        report(entry, chan_window, equity=250_000.0)
        out = capsys.readouterr().out
        leverage = annualised_moments(simple_returns(chan_window)).leverage
        assert "on $250,000 of equity" in out
        assert cell(out, "portfolio").startswith(f"${leverage * 250_000.0:,.2f}")
        assert f"${EQUITY:,.2f}" not in out

    def test_the_stress_block_binds_its_four_figures(self, printed, chan_window) -> None:
        """The half-Kelly line is the sharp one. Printing the full leverage there
        leaves the sentence below comparing a number the reader never saw."""
        returns = simple_returns(chan_window)
        moments = annualised_moments(returns)
        stress = stress_test(moments, returns)
        assert cell(printed, "worst one-day S&P 500 loss").startswith(f"{stress.book_loss:.2%}")
        assert cell(printed, "worst one-day loss in this window").startswith(
            f"{abs(stress.worst_loss):.2%}"
        )
        assert cell(printed, f"a {stress.tolerance:.0%} one-day tolerance allows").startswith(
            f"{stress.allowed_leverage:.6f}"
        )
        assert cell(printed, "half-Kelly here") == f"{stress.half_kelly:.6f}"
        assert (
            f"f* is above {stress.threshold:.6f}, and f* is {moments.leverage:.6f} here" in printed
        )

    def test_the_scan_binds_each_rule_to_its_own_moments(self, printed, chan_window) -> None:
        """Four rows of four numbers. Swapping the mean and the standard
        deviation columns, or their headers, was green."""
        scan = sampling_scan(chan_window)
        daily = scan["daily"]
        for rule, moments in scan.items():
            lift = "" if rule == "daily" else f"{moments.leverage / daily.leverage - 1.0:+.1%}"
            assert (
                cell(printed, rule)
                == (
                    f"{moments.returns:>8,} {moments.mean_annual:>10.4f} "
                    f"{moments.sd_annual:>10.4f} {moments.leverage:>10.4f} {lift:>10}"
                ).strip()
            )
        assert (
            cell(printed, "rule")
            == (f"{'returns':>8} {'mean':>10} {'sd':>10} {'f*':>10} {'vs daily':>10}").strip()
        )

    def test_the_identity_line_prints_the_two_leverages_it_compares(
        self, printed, chan_window
    ) -> None:
        """One of them is the per-period ratio. Printing the Sharpe ratio there
        was green, under a sentence saying the two are the same quantity."""
        moments = annualised_moments(simple_returns(chan_window))
        assert f"annualised moments is {moments.leverage:.10f}" in printed
        assert f"before annualising it is {moments.period_leverage:.10f}" in printed

    def test_a_window_that_is_not_chans_keeps_its_labels(self, spy, capsys) -> None:
        """The no-published-column branch formats its own rows, so it needs its
        own case. Dropping the label from it was green."""
        entry, close = spy
        report(entry, window(close, *BEAR))
        out = capsys.readouterr().out
        moments = annualised_moments(simple_returns(window(close, *BEAR)))
        assert cell(out, "optimal Kelly leverage f*") == f"{moments.leverage:.4f}"
        assert cell(out, "mean annual return") == f"{moments.mean_annual * 100:.4f}%"


def published_rows(out: str) -> list[str]:
    """The lines of the published table, taken as the block under its header.

    Matching rows by shape rather than by position picks up the time-scale
    scan as well, which has the same shape and a different job. The table is
    the run of non-empty lines after the header row and nothing else, so a
    deleted row shortens it and a reordered one moves inside it.
    """
    lines = out.splitlines()
    header = next(i for i, line in enumerate(lines) if line.strip().startswith("quantity"))
    rows = []
    for line in lines[header + 1 :]:
        if not line.strip():
            break
        rows.append(line)
    return rows


class TestTheReportCarriesEveryCaveatItOwes:
    """Four sentences the report is required to print, each deletable and green.

    A number is held by an assertion on the number. A caveat is held by nothing
    unless somebody writes this class, and every one of these was removable
    with the suite green.
    """

    def test_the_gap_column_says_it_is_a_drift_measurement(self, spy, chan_window, capsys) -> None:
        """Without it the gap column reads as a reproduction, which the module
        docstring's own first claim says it is not."""
        entry, _ = spy
        report(entry, chan_window)
        out = " ".join(capsys.readouterr().out.split())
        assert "the gap column is a vendor-drift measurement and not a reproduction" in out
        assert "Chan's own workbook is the --chan run" in out
        assert "so the gap column is a reproduction" not in out

    def test_the_full_kelly_cost_is_flagged_as_unpublished(self, spy, chan_window, capsys) -> None:
        """It is the one figure in the stress block the book does not print."""
        entry, _ = spy
        report(entry, chan_window)
        assert "not a figure the book prints: at full Kelly" in capsys.readouterr().out

    def test_the_report_points_at_the_entry_that_carries_the_verdict(
        self, spy, chan_window, capsys
    ) -> None:
        """The report states figures and the log states verdicts, so a reader
        who stops at the report needs the pointer."""
        entry, _ = spy
        report(entry, chan_window)
        assert "docs/replication-log.md Entry 3 carries the verdict." in capsys.readouterr().out

    def test_a_rule_too_short_for_the_window_says_so_rather_than_vanishing(
        self, spy, capsys
    ) -> None:
        """``sampling_scan`` returns None so the report can say this. Deleting
        the line drops the row without comment, which is what the None exists
        to prevent."""
        entry, close = spy
        report(entry, window(close, "2007-11-01", BOOK_END))
        out = capsys.readouterr().out
        assert "too few returns in this window" in out
        assert cell(out, "daily").startswith("39 ")


class TestThePublishedConstantsAgreeWithThemselves:
    """``_PUBLISHED`` holds each book figure twice, as a string and as a number.

    The string is shown in the book column and the number computes the gap, and
    nothing made them agree. Setting the Sharpe row's number to 0.4276 while
    its string stayed 0.4275 was green, so the row printed a book figure and a
    gap that cannot both be right.
    """

    def test_each_row_prints_the_number_it_subtracts(self) -> None:
        for label, _field, as_percent, printed_figure, value, decimals in _PUBLISHED:
            expected = f"{value}%" if as_percent else f"{value}"
            assert printed_figure == expected, label
            assert len(printed_figure.rstrip("%").split(".")[1]) == decimals, label

    def test_every_published_figure_is_one_the_book_reference_quotes(self) -> None:
        """``BOOK_REF`` is the report's second line and the table is below it, so
        a figure in one and not the other is two answers to one question."""
        for row in _PUBLISHED:
            assert row[3] in BOOK_REF

    def test_the_worked_examples_closing_sentence_quotes_the_chain_it_ran(self) -> None:
        """Four dollar figures in prose beside a column that computes them.
        Changing one to $188,829 was green."""
        chain = rebalance(BOOK_LEVERAGE)
        source = inspect.getsource(_worked_example)
        for value in (chain.portfolio, chain.shocked_portfolio, chain.shocked_equity):
            assert f"${value:,.0f}" in source
        assert f"${chain.resized:,.0f}".rsplit(".", 1)[0] in source


# ============================================================
# The guards, which one-sided cases leave open
# ============================================================


class TestTheWindowGuardIsHeldOnBothSides:
    """``MIN_TRADING_DAYS`` could move by a factor of 23 with the suite green.

    The refusal case quoted the constant back at itself and its window held 19
    days, so the floor was pinned only to the open range between 20 and about
    752.
    """

    def test_the_floor_is_the_value_it_is_documented_as(self) -> None:
        """Quoted in the module docstring's sibling comment and in the refusal,
        so it is a number the prose carries."""
        assert MIN_TRADING_DAYS == 30

    def test_exactly_the_floor_runs_and_one_fewer_refuses(self, spy, capsys) -> None:
        """The boundary from both sides. The refusal case alone passes on a
        floor anywhere below the window it happens to use."""
        _, close = spy
        after = close[close.index >= pd.Timestamp(BOOK_START)]
        at_the_floor = str(after.index[MIN_TRADING_DAYS - 1].date())
        one_short = str(after.index[MIN_TRADING_DAYS - 2].date())
        run(start=BOOK_START, end=at_the_floor)
        assert f"{MIN_TRADING_DAYS:,} closes" in capsys.readouterr().out
        with pytest.raises(SystemExit) as exited:
            run(start=BOOK_START, end=one_short)
        assert f"only {MIN_TRADING_DAYS - 1} trading days" in str(exited.value)

    def test_the_refusal_names_the_window_in_the_order_it_was_asked_for(self, spy) -> None:
        """Reversing the two was green, which turns a message meant to help a
        reader fix the argument into one that describes a window nobody asked
        for."""
        with pytest.raises(SystemExit) as exited:
            run(start="2007-12-01", end=BOOK_END)
        assert f"in 2007-12-01..{BOOK_END}" in str(exited.value)

    def test_two_returns_are_enough_for_a_sampling_rule(self, spy) -> None:
        """The None branch was only exercised at one return, so the floor was
        unpinned from above and could rise to twenty with nothing failing."""
        _, close = spy
        after = close[close.index >= pd.Timestamp(BOOK_START)]
        three_bars = after.iloc[: 2 * BLOCK_DAYS + 1]
        scan = sampling_scan(three_bars)
        assert scan["block-21"] is not None
        assert scan["block-21"].returns == 2
        assert sampling_scan(after.iloc[: BLOCK_DAYS + 1])["block-21"] is None


class TestTheBookColumnNeedsBothEndpoints:
    """Sharing one endpoint with Chan's window is not sharing his window.

    Testing either half alone was green, because the two windows the other
    cases use differ at both ends. The bull window ends on ``BOOK_END``, so the
    half that matters would have printed gaps against his published figures for
    a run over 2003 to 2007.
    """

    def test_a_window_sharing_only_the_end_prints_no_gap(self, spy, capsys) -> None:
        entry, close = spy
        report(entry, window(close, *BULL))
        out = capsys.readouterr().out
        assert "no figure below has a published counterpart" in out
        assert "the book   gap" not in out

    def test_a_window_sharing_only_the_start_prints_no_gap(self, spy, capsys) -> None:
        entry, close = spy
        report(entry, window(close, BOOK_START, "2006-12-29"))
        out = capsys.readouterr().out
        assert "no figure below has a published counterpart" in out
        assert "the book   gap" not in out


class TestTheCliDefaultsAreTheirOwnPins:
    """``run()``'s defaults and argparse's are two sets of constants.

    Every earlier case called ``run()`` directly or passed arguments, so all
    of argparse's defaults could move with the suite green, including
    ``--risk-free`` to 0.40. ``--chan`` and ``--dated`` are held by the case
    with no arguments, which reads the 2026 download, and by
    ``TestTheChanFlag``, which shows the date default does not follow it there.
    """

    def test_main_with_no_arguments_runs_chans_window_at_the_books_rate(
        self, monkeypatch, capsys
    ) -> None:
        monkeypatch.setattr("sys.argv", ["chan.kelly_leverage"])
        main()
        out = capsys.readouterr().out
        assert f"{BOOK_START} .. {BOOK_END}" in out
        assert "3,758 closes, 3,757 daily returns" in out
        assert f"risk-free {RISK_FREE:.0%} subtracted" in out
        assert cell(out, "optimal Kelly leverage f*").startswith("2.5506")

    def test_the_rate_reaches_the_arithmetic_and_not_only_the_label(
        self, monkeypatch, capsys
    ) -> None:
        """The label and the figures came from different places. Dropping
        ``risk_free=`` inside ``report`` printed "risk-free 0%" over figures
        computed at four percent, and the argument-passing case passed on it
        because it asserts the label.
        """
        monkeypatch.setattr("sys.argv", ["chan.kelly_leverage", "--risk-free", "0.0"])
        main()
        out = capsys.readouterr().out
        moments = annualised_moments(
            simple_returns(load_close("SPY", dated=VINTAGE_DATE)[BOOK_START:BOOK_END]),
            risk_free=0.0,
        )
        assert (
            cell(out, "optimal Kelly leverage f*")
            == (
                f"{moments.leverage:>12.4f}   {'2.528':>8}   {moments.leverage - 2.528:+.3f}"
            ).strip()
        )
        # At a zero rate the excess return is the total return, so the two rows
        # print the same computed figure under different book figures. That is
        # the cheapest statement of "the rate reached the arithmetic" that does
        # not restate a number.
        assert (
            cell(out, "mean excess return").split()[0]
            == (cell(out, "mean annual return").split()[0])
        )
        assert "0.0/252 a day and 0.0/12 a month" in out

    def test_the_rate_reaches_every_sampling_rule(self, chan_window) -> None:
        """``sampling_scan`` takes the rate and three of its four rules are
        monthly, so dropping it there moves three rows and no label."""
        at_zero = sampling_scan(chan_window, risk_free=0.0)
        at_the_book = sampling_scan(chan_window)
        for rule in SAMPLING_RULES:
            assert at_zero[rule].leverage != at_the_book[rule].leverage
            assert at_zero[rule].excess_annual == pytest.approx(
                at_the_book[rule].excess_annual + RISK_FREE, abs=5e-12
            )


class TestTheMonthEndCalendar:
    """``_final_month_is_partial`` was covered by two shapes and needed four.

    Both survivors are off-by-one on the range it scans, and each one drops a
    month of returns from a rule that names itself complete.
    """

    @staticmethod
    def series(days: list[str]) -> pd.Series:
        return pd.Series(
            range(1, len(days) + 1), index=pd.DatetimeIndex(pd.to_datetime(days)), dtype=float
        )

    def test_a_month_whose_last_weekday_is_the_last_bar_is_complete(self) -> None:
        """May 2026 ends on a Sunday, so a Friday 29th bar closes it. Widening
        the weekday test to include Saturday called this partial."""
        closes = self.series(["2026-04-30", "2026-05-29"])
        assert len(resample_close(closes, "month-end-complete")[0]) == 2

    def test_the_last_bar_does_not_count_as_a_day_still_to_come(self) -> None:
        """Scanning from ``last`` rather than the day after it makes every
        weekday bar partial unless it is the month's final calendar day."""
        closes = self.series(["2026-05-29", "2026-06-30"])
        assert len(resample_close(closes, "month-end-complete")[0]) == 2

    def test_a_month_with_weekdays_left_in_it_is_partial(self) -> None:
        """The case Chan's own span is: 2007-12-28 with the 31st still to trade."""
        closes = self.series(["2007-11-30", "2007-12-28"])
        assert len(resample_close(closes, "month-end-complete")[0]) == 1


# ============================================================
# Chan's own workbook, which reproduces what he printed
# ============================================================


@pytest.fixture(scope="module")
def chans():
    """Chan's ``example6_2.xls`` column, resolved with no date.

    One ``chan-xls`` SPY entry exists, so the flags select it on their own.
    That is the property ``run`` relies on when ``--chan`` arrives without
    ``--dated``.
    """
    return load_vintage("SPY", chan=True)


@pytest.fixture(scope="module")
def his_moments(chans):
    _, close = chans
    return annualised_moments(simple_returns(close))


class TestChansOwnWorkbook:
    """What the ``--chan`` run reads, and that it is exactly his window."""

    def test_the_entry_is_his_workbook_column(self, chans) -> None:
        """A saved date rather than a download date, and the workbook named,
        because ``SPY.xls`` in the same mirror is a different series."""
        entry, close = chans
        assert entry.vendor == "chan-xls"
        assert entry.symbol == "SPY"
        assert entry.price_basis == "adjusted"
        assert entry.saved_date == "2008-01-29"
        assert entry.download_date is None
        assert entry.source_workbook == "example6_2.xls"
        assert entry.path == "spy_chan.csv"
        assert len(close) == entry.row_count == 3758

    def test_his_series_spans_exactly_the_window_the_module_defaults_to(self, chans) -> None:
        """``BOOK_START`` and ``BOOK_END`` were read off this file, so the
        default window selects every row of it and nothing is clipped."""
        _, close = chans
        assert str(close.index[0].date()) == BOOK_START
        assert str(close.index[-1].date()) == BOOK_END


class TestEveryFigureHePrintedReproducesFromHisData:
    """Entry 3's rows 18 to 25. The verdict on each is ``reproduced``.

    That verdict says his arithmetic is right on his data. It says nothing
    about whether 2.528 is a leverage anyone should carry, which the report
    prints above the table rather than leaving to this docstring.
    """

    def test_the_moments(self, his_moments) -> None:
        assert his_moments.returns == 3757
        assert his_moments.mean_annual == pytest.approx(0.1123074733, abs=5e-10)
        assert his_moments.sd_annual == pytest.approx(0.1691312229, abs=5e-10)
        assert his_moments.excess_annual == pytest.approx(0.0723074733, abs=5e-10)

    def test_the_sharpe_ratio_and_the_dispersion_form_it_decides(self, chans, his_moments) -> None:
        """Only the sample form prints as the 0.4275 he published.

        On his own data the population form gives 0.427580, which prints as
        0.4276, while both forms round to his 2.528. This is the demonstration
        the modern vintage can only make by analogy, and it is why the Sharpe
        ratio is pinned tighter than the precision rule asks.
        """
        _, close = chans
        returns = simple_returns(close)
        population_sd = float(returns.std(ddof=0)) * math.sqrt(TRADING_DAYS)
        population_sharpe = his_moments.excess_annual / population_sd
        population_leverage = his_moments.excess_annual / population_sd**2
        assert his_moments.sharpe == pytest.approx(0.4275229141, abs=5e-7)
        assert population_sharpe == pytest.approx(0.4275798223, abs=5e-7)
        assert round(his_moments.sharpe, 4) == 0.4275
        assert round(population_sharpe, 4) == 0.4276
        assert round(population_leverage, 3) == round(his_moments.leverage, 3) == 2.528

    def test_the_kelly_leverage_and_the_growth_rates(self, his_moments) -> None:
        assert his_moments.leverage == pytest.approx(2.5277586649, abs=5e-8)
        assert his_moments.half_kelly == pytest.approx(1.2638793324, abs=5e-8)
        assert his_moments.levered_growth == pytest.approx(0.1313879210, abs=5e-10)
        assert his_moments.unlevered_growth == pytest.approx(0.0980047880, abs=5e-10)

    def test_every_published_figure_reproduces_at_the_precision_he_printed(
        self, his_moments
    ) -> None:
        """The whole of rows 18 to 25 in one assertion, row by row.

        Rounding the computed figure to the book's own decimals gives the
        book's own figure, on every row of ``_PUBLISHED``. Three of them, the
        excess return, the leverage and the levered growth rate, land below his
        figure before rounding, which is why the report rounds a gap before
        signing it.
        """
        below = [
            row[0]
            for row in _PUBLISHED
            if getattr(his_moments, row[1]) * (100.0 if row[2] else 1.0) < row[4]
        ]
        assert below == ["mean excess return", "optimal Kelly leverage f*", "levered growth rate"]
        for label, field, as_percent, _printed, value, decimals in _PUBLISHED:
            computed = getattr(his_moments, field) * (100.0 if as_percent else 1.0)
            assert round(computed, decimals) == value, label


class TestThePrintedPortfolioOnHisExactLeverage:
    """Row 26. The one printed figure his own data does not reach."""

    def test_his_exact_leverage_buys_less_than_he_printed(self, his_moments) -> None:
        """$252,775.87 against $252,800, and the rest of the chain with it.

        The gaps are taken against the four figures the book prints, which are
        whole dollars, so they are quoted in whole dollars. The last is against
        his printed $188,892 rather than the $188,892.16 his chain computes to.
        """
        chain = rebalance(his_moments.leverage)
        assert chain.portfolio == pytest.approx(252_775.8665, abs=5e-5)
        assert chain.shocked_portfolio == pytest.approx(227_498.2798, abs=5e-5)
        assert chain.shocked_equity == pytest.approx(74_722.4134, abs=5e-5)
        assert chain.resized == pytest.approx(188_880.2278, abs=5e-5)
        printed = (252_800, 227_520, 74_720, 188_892)
        computed = (chain.portfolio, chain.shocked_portfolio, chain.shocked_equity, chain.resized)
        assert [round(c - p) for c, p in zip(computed, printed, strict=True)] == [-24, -22, 2, -12]

    def test_rounding_the_leverage_is_the_whole_cause(self, his_moments) -> None:
        """His leverage rounded to the three decimals he printed buys what he
        printed, the first three figures to the cent and the fourth to the dollar
        he printed it at, so nothing in the data is left to explain."""
        rounded = rebalance(round(his_moments.leverage, 3))
        assert rounded.portfolio == pytest.approx(252_800.0, abs=5e-7)
        assert rounded.shocked_portfolio == pytest.approx(227_520.0, abs=5e-7)
        assert rounded.shocked_equity == pytest.approx(74_720.0, abs=5e-7)
        assert rounded.resized == pytest.approx(188_892.16, abs=5e-3)


class TestHisOwnDataOnTheRestOfTheEntry:
    """Rows 27 and 28, and the window figures the module docstring quotes."""

    def test_the_black_monday_conclusion_survives_on_his_data(self, chans, his_moments) -> None:
        """Row 27. Half-Kelly is 1.2639 against the 0.977040 a 20 percent day
        allows, and his leverage clears the threshold by 0.57."""
        _, close = chans
        stress = stress_test(his_moments, simple_returns(close))
        assert stress.survives is True
        assert stress.half_kelly == pytest.approx(1.2638793324, abs=5e-8)
        assert his_moments.leverage - stress.threshold == pytest.approx(0.5737, abs=5e-5)
        assert stress.worst_day == "1997-10-27"
        assert stress.worst_loss == pytest.approx(-0.0724744678, abs=5e-10)
        assert stress.full_kelly_equity_loss == pytest.approx(0.5174321987, abs=5e-10)

    def test_the_time_scale_claim_fails_on_his_own_series(self, chans, his_moments) -> None:
        """Row 28. Every monthly rule lands 43 to 47 percent above his daily
        figure, so the vintage explanation is spent and the verdict on the
        claim does not depend on which vintage was read."""
        _, close = chans
        scan = sampling_scan(close)
        assert scan["month-end"].leverage == pytest.approx(3.6907806516, abs=5e-8)
        assert scan["month-end-complete"].leverage == pytest.approx(3.7195468280, abs=5e-8)
        assert scan["block-21"].leverage == pytest.approx(3.6163471560, abs=5e-8)
        lifts = {
            rule: scan[rule].leverage / his_moments.leverage - 1.0
            for rule in ("month-end", "month-end-complete", "block-21")
        }
        assert lifts["month-end"] == pytest.approx(0.4601, abs=5e-5)
        assert lifts["month-end-complete"] == pytest.approx(0.4715, abs=5e-5)
        assert lifts["block-21"] == pytest.approx(0.4307, abs=5e-5)
        assert all(0.43 <= round(lift, 2) <= 0.47 for lift in lifts.values())

    def test_the_window_moves_his_leverage_from_a_short_to_nearly_double(self, chans) -> None:
        """The module docstring's −2.85 and +4.83, which are his data's."""
        _, close = chans
        bear = annualised_moments(simple_returns(window(close, *BEAR)))
        bull = annualised_moments(simple_returns(window(close, *BULL)))
        assert bear.returns == 751
        assert bear.leverage == pytest.approx(-2.8454514767, abs=5e-8)
        assert bull.returns == 1256
        assert bull.leverage == pytest.approx(4.8292559665, abs=5e-8)


class TestTheTwoVintagesOverChansWindow:
    """Rows 29 and 30, which carry no published figure and no verdict.

    The join is pinned before the difference, because a vendor restates which
    days a series holds as well as what they are worth. Over this window the
    two vintages agree on every day, which is what makes the rest a difference
    in prices rather than a difference in calendars.
    """

    @pytest.fixture(scope="class")
    @staticmethod
    def comparison(chans, chan_window):
        _, close = chans
        return compare_vintages(close, chan_window)

    def test_the_join_drops_nothing_from_either_side(self, comparison) -> None:
        assert comparison.older_days == comparison.newer_days == 3758
        assert comparison.joined_days == 3758
        assert comparison.older_dropped == comparison.newer_dropped == 0
        assert (comparison.joined_start, comparison.joined_end) == (BOOK_START, BOOK_END)

    def test_the_gap_in_the_mean_and_the_dispersion_that_does_not_move(self, comparison) -> None:
        """0.0641 of a percentage point on the mean, and 0.0014 on the
        dispersion, which is why only the second reproduces at two decimals."""
        assert comparison.mean_gap == pytest.approx(0.0006408223, abs=5e-10)
        assert comparison.older.sd_annual == pytest.approx(0.1691312229, abs=5e-10)
        assert comparison.newer.sd_annual == pytest.approx(0.1691169493, abs=5e-10)

    def test_ten_days_carry_the_whole_gap_and_dividend_months_carry_it_too(
        self, comparison
    ) -> None:
        """The ten largest daily differences sum to 108 percent of the total,
        eight raising the 2026 mean and two lowering it, so the other 3,747
        days pull the other way by about a twelfth. Days in SPY's dividend
        months carry 100.4 percent."""
        assert LARGEST_DAYS == 10
        assert DIVIDEND_MONTHS == (3, 6, 9, 12)
        assert comparison.largest_share == pytest.approx(1.0847689666, abs=5e-10)
        assert comparison.largest_raising == 8
        assert comparison.dividend_month_share == pytest.approx(1.0039062657, abs=5e-10)

    def test_the_mean_gap_is_the_mean_of_the_daily_differences(self, chans, chan_window) -> None:
        """The two shares divide up the summed difference, so the gap they are
        shares of has to be that sum annualised rather than a difference of
        two rounded means."""
        _, close = chans
        differences = simple_returns(chan_window) - simple_returns(close)
        comparison = compare_vintages(close, chan_window)
        assert comparison.mean_gap == pytest.approx(
            float(differences.mean()) * TRADING_DAYS, abs=5e-15
        )

    def test_the_ten_days_are_all_quarterly_ex_dividend_days(self, comparison) -> None:
        """Each falls on the third Friday of a quarter-end month, when SPY goes
        ex, or on the trading day after one. 1994-09-19 is the only Monday.

        The share in dividend months says where the gap sits in aggregate. This
        says it of every one of the ten, which is the claim the prose makes.
        """
        assert comparison.largest_days == (
            "1994-09-19",
            "2006-12-15",
            "1996-09-20",
            "2001-12-21",
            "1993-03-19",
            "1994-12-16",
            "1995-12-15",
            "1993-12-17",
            "1993-06-18",
            "1996-12-20",
        )
        for day in map(pd.Timestamp, comparison.largest_days):
            fridays = pd.date_range(day.replace(day=1), periods=5, freq="W-FRI")
            third_friday = fridays[fridays.month == day.month][2]
            assert day.month in DIVIDEND_MONTHS
            assert day in (third_friday, third_friday + pd.offsets.BDay(1)), day

    def test_days_one_side_lacks_are_counted_rather_than_hidden(self) -> None:
        """A synthetic pair where the older side lacks one day and the newer
        lacks two. A silent inner join would report both as 0, and a swap of the
        two counts would report 2 and 1."""
        days = pd.bdate_range("2026-01-05", periods=7)
        closes = [10.0, 10.1, 10.2, 10.0, 10.3, 10.4, 10.2]
        older = pd.Series(closes, index=days).drop(days[1])
        newer = pd.Series(closes, index=days).drop([days[4], days[5]])
        newer.loc[days[3]] = 10.05
        comparison = compare_vintages(older, newer)
        assert (comparison.older_days, comparison.newer_days) == (6, 5)
        assert comparison.joined_days == 4
        assert (comparison.older_dropped, comparison.newer_dropped) == (2, 1)

    def test_a_missing_close_on_one_side_drops_that_day_from_both(self) -> None:
        """Both sides' moments come from the same days, so the gap stays the
        annualised mean of the daily differences. Before, a NaN close on one side
        dropped its return there and nowhere else, and the shares divided by a
        sum the gap was not."""
        days = pd.bdate_range("2026-01-05", periods=8)
        older = pd.Series([10.0, 10.1, 10.3, 10.2, 10.4, 10.5, 10.3, 10.6], index=days)
        newer = older * 1.01
        newer.iloc[5] = 10.62
        newer.iloc[3] = float("nan")
        comparison = compare_vintages(older, newer)
        assert comparison.older.returns == comparison.newer.returns
        common = simple_returns(older).index.intersection(simple_returns(newer).index)
        differences = simple_returns(newer).loc[common] - simple_returns(older).loc[common]
        assert comparison.mean_gap == pytest.approx(
            float(differences.mean()) * TRADING_DAYS, abs=5e-12
        )

    def test_differences_summing_to_zero_leave_no_share_to_state(self) -> None:
        """Identical series differ by nothing, so both shares are nan rather
        than a division by zero."""
        days = pd.bdate_range("2026-01-05", periods=5)
        close = pd.Series([10.0, 10.1, 10.2, 10.0, 10.3], index=days)
        comparison = compare_vintages(close, close.copy())
        assert comparison.mean_gap == 0.0
        assert math.isnan(comparison.largest_share)
        assert math.isnan(comparison.dividend_month_share)

    def test_a_repeated_date_is_refused_by_name(self) -> None:
        days = pd.to_datetime(["2026-01-05", "2026-01-06", "2026-01-06", "2026-01-07"])
        repeated = pd.Series([10.0, 10.1, 10.1, 10.2], index=days)
        clean = repeated[~repeated.index.duplicated()]
        with pytest.raises(ValueError, match="newer vintage repeats a date"):
            compare_vintages(clean, repeated)
        with pytest.raises(ValueError, match="older vintage repeats a date"):
            compare_vintages(repeated, clean)

    def test_a_join_too_short_for_a_dispersion_is_refused_by_name(self) -> None:
        days = pd.to_datetime(["2026-01-05", "2026-01-06", "2026-01-07"])
        older = pd.Series([10.0, 10.1, 10.2], index=days)
        newer = pd.Series([10.0, 10.1], index=days[1:].shift(1, freq="D"))
        with pytest.raises(ValueError, match="share 0 days with a return on both sides"):
            compare_vintages(older, newer)


class TestTheReportOnHisWorkbook:
    """The caveat, the gap column and the comparison, on the run that reads him."""

    @pytest.fixture(scope="class")
    @staticmethod
    def printed():
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            run(chan=True)
        return buffer.getvalue()

    def test_the_header_names_his_workbook_and_its_saved_date(self, printed) -> None:
        assert "vintage: spy_chan.csv   chan-xls adjusted, saved 2008-01-29" in printed
        assert "downloaded" not in printed

    def test_the_gap_column_says_it_is_a_reproduction_and_what_that_does_not_mean(
        self, printed
    ) -> None:
        """Issue 138 asks for the label in the same breath as the figure,
        because a match invites belief where a gap invites doubt."""
        out = " ".join(printed.split())
        assert "read on his own workbook, so the gap column is a reproduction" in out
        assert "his arithmetic is right on his data" in out
        assert "nothing about whether a leverage of 2.528 is one anyone should carry" in out
        assert "vendor-drift measurement" not in out

    def test_every_gap_prints_as_zero_and_none_as_negative_zero(self, printed) -> None:
        """A gap that rounds to nothing from below would print as -0.000 under
        plain formatting, which reads as a miss."""
        for label, _field, _as_percent, _printed, _value, decimals in _PUBLISHED:
            assert cell(printed, label).endswith(f"+{0.0:.{decimals}f}"), label
        assert "-0.0" not in printed

    def test_the_comparison_names_each_vintage_and_its_recorded_span(self, printed) -> None:
        """Requirement 4 asks for each vintage's recorded span beside the joined
        one, so a day the window excluded reads differently from a day the
        vendor's series does not hold."""
        assert cell(printed, "this vintage") == "spy_chan.csv, recorded 1993-01-29 .. 2007-12-28"
        assert cell(printed, "the 2026 download") == (
            "yfinance_spy_adjusted_1993-01-29_2026-09-18_dl2026-09-18.csv, "
            "recorded 1993-01-29 .. 2026-09-18"
        )

    def test_the_comparison_binds_its_figures_to_its_labels(self, printed) -> None:
        assert cell(printed, "days in the window, this vintage") == "3,758"
        assert cell(printed, "days in the window, 2026 download") == "3,758"
        assert cell(printed, "days both hold") == f"3,758   {BOOK_START} .. {BOOK_END}"
        assert cell(printed, "dropped from each by the join") == "0 and 0"
        assert cell(printed, "mean annual return").startswith("11.2307%")
        assert "11.2307% against 11.2948%, +0.0641 points" in printed
        assert "16.9131% against 16.9117%" in printed
        assert cell(printed, "largest 10 daily differences carry").startswith("108.5%")
        assert cell(printed, "quarterly dividend months carry") == "100.4% of it"

    def test_the_comparison_says_it_is_not_a_replication(self, printed) -> None:
        out = " ".join(printed.split())
        assert "carries neither a gap nor a verdict" in out

    def test_the_modern_run_prints_no_comparison(self, capsys) -> None:
        """It belongs to the run that reads his workbook. The default run has
        nothing of his to compare against."""
        run()
        assert "Against the 2026 download" not in capsys.readouterr().out


class TestTheChanFlag:
    """``--chan`` reads a file whose date is a saved date, not a download date."""

    def test_the_flag_alone_reads_his_workbook(self, monkeypatch, capsys) -> None:
        """The trap the audit of issue 138 measured. With ``--dated`` defaulting
        to the download date, this refused with the reader's own message."""
        monkeypatch.setattr("sys.argv", ["chan.kelly_leverage", "--chan"])
        main()
        out = capsys.readouterr().out
        assert "vintage: spy_chan.csv" in out
        assert cell(out, "optimal Kelly leverage f*").startswith("2.5278")

    def test_the_flag_and_his_saved_date_together(self, monkeypatch, capsys) -> None:
        monkeypatch.setattr(
            "sys.argv",
            ["chan.kelly_leverage", "--chan", "--dated", "2008-01-29", "--start", BULL[0]],
        )
        main()
        out = capsys.readouterr().out
        assert "saved 2008-01-29" in out
        assert f"{BULL[0][:4]}-01-02 .. {BOOK_END}" in out
        assert "no figure below has a published counterpart" in out
        assert cell(out, "days both hold").startswith("1,257")

    def test_a_window_past_his_last_day_drops_nothing_from_the_download(self, capsys) -> None:
        """The download is clipped to the days his series spans, not to the
        window asked for. Clipped to the window, the 126 days after 2007-12-28
        read as days the join dropped, which is a span and not a restatement."""
        run(chan=True, start="2007-11-01", end="2008-06-30")
        out = capsys.readouterr().out
        assert cell(out, "days in the window, 2026 download") == "40"
        assert cell(out, "dropped from each by the join") == "0 and 0"

    def test_a_rate_that_is_not_his_is_not_called_a_reproduction(self, capsys) -> None:
        """At a zero rate the leverage gap is +1.398, under a caveat that used to
        say a zero in that column meant his arithmetic was right."""
        run(chan=True, risk_free=0.0)
        out = " ".join(capsys.readouterr().out.split())
        assert "at a risk-free rate of 0.00% rather than his 4%" in out
        assert "neither a reproduction nor a vendor-drift measurement" in out
        assert "so the gap column is a reproduction" not in out

    def test_the_same_holds_for_the_2026_download(self, capsys) -> None:
        """The caveat it had there, a vendor-drift measurement, was as wrong
        at another rate, so the rule reads the rate before the vintage."""
        run(risk_free=0.0)
        out = " ".join(capsys.readouterr().out.split())
        assert "neither a reproduction nor a vendor-drift measurement" in out
        assert "the gap column is a vendor-drift measurement and not" not in out

    def test_a_download_date_under_the_flag_is_refused_by_the_reader(self, monkeypatch) -> None:
        """The date names a vintage, and no workbook column carries that one."""
        monkeypatch.setattr("sys.argv", ["chan.kelly_leverage", "--chan", "--dated", VINTAGE_DATE])
        with pytest.raises(SystemExit) as exited:
            main()
        assert f"chan-xls SPY adjusted dated {VINTAGE_DATE}" in str(exited.value)
