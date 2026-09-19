"""Pins for Qian's risk parity against 60/40, on SPY and AGG.

This file is the single authority for every number any prose surface quotes
about this experiment. ``docs/replication-log.md`` Entry 4 states those numbers
and derives none of them, and ``src/chan/risk_parity.py`` carries the
reasoning.

**The allocation lands near Qian's and the ranking goes the other way.** On the
full common span the risk-parity weights are 21.78 to 78.22, about a
percentage point off his 23-77, and the leverage that matches 60/40's
volatility is 1.98 against his 1.8. Both are close. The Sharpe ranking is not:
60/40 beats the levered risk-parity portfolio by 0.2169 on the full span, and
the robust t on that difference is −2.17, which the window resolves.

Three kinds of assertion live here and they are not interchangeable.

1. **Vintage pins**, which state what these two committed series give under the
   specification. Each names its window, because the volatility ratio runs from
   2.76 to 3.87 across the three declared ones.
2. **Specification pins**, which hold a choice rather than a number. The
   annualisation, the dispersion form, the daily rebalance and the simple
   division of the risk-free rate are each moved and each costs something
   visible.
3. **Structure pins**, which hold a property no vintage can move. The
   correlation cancelling out of the two-leg risk-parity equation, the Sharpe
   difference being invariant to leverage, and the matched-volatility identity
   are all of that kind, and they are what make the ranking's error bar mean
   anything.

**The ranking is pinned as a difference and a t, never as a boolean.** An
assertion that one Sharpe exceeds another survives any mutation that leaves the
sign alone, which includes getting the magnitude wrong by any amount. Issue 10
recorded exactly that survivor in the ported suite, so the pins below hold the
measured difference, its annualised mean and its robust t.

**A red assertion here can be the data, this code, or the dependency**, which
is why ``tests/test_ithildincore_contract.py`` gained its `stats` cases in the
same change. Every robust t below runs through
``ithildincore.stats.newey_west_summary``, and those cases are what say a moved
t came from the pin in ``pyproject.toml`` rather than from either vintage.
"""

from __future__ import annotations

import contextlib
import io
import math

import numpy as np
import pandas as pd
import pytest

from chan.risk_parity import (
    BENCHMARK_WEIGHTS,
    BOND,
    BOOK_LEVERAGE,
    BOOK_RATIO_BAND,
    BOOK_REF,
    BOOK_VOL_RATIO,
    BOOK_WEIGHTS,
    MIN_TRADING_DAYS,
    RISK_FREE,
    STOCK,
    TIGHTENING_START,
    TRADING_DAYS,
    WINDOWS,
    Ranking,
    WindowTooShort,
    annualised_covariance,
    clip,
    correlation_from_leverage,
    decompose,
    leverage_from_correlation,
    main,
    matching_leverage,
    measure_legs,
    measure_window,
    portfolio_excess_returns,
    rank_at_matched_volatility,
    rank_the_windows,
    report,
    risk_parity_weights,
    risk_shares,
    run,
    simple_returns,
)
from chan.series import aligned_closes, load_close
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import committed_copy

# The download date both legs carry. They were taken on one day, which is not
# something the reader can assume: the default GLD/GDX pair's two legs are 72
# days apart.
VINTAGE_DATE = "2026-09-18"


@pytest.fixture(scope="module")
def joined():
    """Both committed vintages, inner-joined on their common trading days."""
    return aligned_closes(STOCK, BOND)


@pytest.fixture(scope="module")
def measured(joined):
    """The three declared windows, each a ``(WindowResult, returns)`` pair."""
    return {label: measure_window(label, joined, start, end) for label, start, end in WINDOWS}


@pytest.fixture(scope="module")
def rankings(measured):
    """The three rankings, with the rising-rates one carrying earlier weights."""
    return rank_the_windows(measured)


# ============================================================
# The two vintages, which every number below is a function of
# ============================================================


class TestTheVintages:
    """What this run read, and that both resolve without a date being named."""

    def test_the_two_entries_are_the_downloads_this_module_names(self, joined) -> None:
        """Five identity fields each, so a re-download cannot answer to these pins."""
        stock_entry, bond_entry = joined.attrs["vintages"]
        assert (stock_entry.vendor, stock_entry.symbol) == ("yfinance", "SPY")
        assert stock_entry.price_basis == "adjusted"
        assert stock_entry.download_date == VINTAGE_DATE
        assert (stock_entry.first_date, stock_entry.last_date) == ("1993-01-29", "2026-09-18")
        assert stock_entry.row_count == 8467

        assert (bond_entry.vendor, bond_entry.symbol) == ("yfinance", "AGG")
        assert bond_entry.price_basis == "adjusted"
        assert bond_entry.download_date == VINTAGE_DATE
        assert (bond_entry.first_date, bond_entry.last_date) == ("2003-09-29", "2026-09-17")
        assert bond_entry.row_count == 5779

    def test_the_bond_leg_is_what_bounds_the_common_span(self, joined) -> None:
        """AGG's first bar is the join's, and SPY reaches back ten years further.

        This is why the window is about two decades rather than the three SPY
        alone would give, and it is a fact about the download rather than
        something issue 15 asserted.
        """
        assert str(joined.index[0].date()) == "2003-09-29"
        assert str(joined.index[-1].date()) == "2026-09-17"
        assert len(joined) == 5779

    def test_the_join_drops_no_day_either_leg_holds_in_the_span(self, joined) -> None:
        """Both legs trade the same calendar here, so the inner join loses nothing.

        An inner join drops days one leg has and the other does not with
        nothing said, which is why the report prints this count. Holding it at
        zero is what would fail if a later vintage arrived on a different
        calendar, and the failure would name the leg.
        """
        first, last = joined.index[0], joined.index[-1]
        for symbol in (STOCK, BOND):
            own = load_close(symbol)
            inside = int(((own.index >= first) & (own.index <= last)).sum())
            assert inside == len(joined), symbol

    def test_the_last_common_day_is_the_bond_legs_and_not_the_stock_legs(self, joined) -> None:
        """SPY's vintage runs one day longer, and that day is not in the join.

        The AGG download returned a non-finite close for 2026-09-18, which
        `_validated_rows` refuses, so the row was dropped before the vintage
        was recorded and the span ends a day early. That is the mechanism
        `chan.vintage`'s refusal exists for, visible here as a date.
        """
        stock_entry, bond_entry = joined.attrs["vintages"]
        assert stock_entry.last_date == "2026-09-18"
        assert bond_entry.last_date == "2026-09-17"
        assert str(joined.index[-1].date()) == bond_entry.last_date


# ============================================================
# Structure, which no vintage can move
# ============================================================


class TestTheTwoLegAlgebra:
    """Properties of the method rather than of the data, checked numerically.

    The module docstring argues each of these on paper. Arguing is not
    checking, and a mutation to the arithmetic would leave the prose intact.
    """

    @pytest.mark.parametrize("correlation", [-0.5, 0.0, 0.5])
    @pytest.mark.parametrize("vols", [(0.18, 0.06), (0.18, 0.14)])
    def test_inverse_volatility_weights_equalise_the_risk_contributions(
        self, correlation, vols
    ) -> None:
        """The correlation cancels out of the two-leg equal-contribution equation.

        So inverse-volatility weighting and equal risk contribution are the
        same allocation on two legs, which is what lets one specification be
        named for both. They part company on three legs, which is why the
        module names the specification anyway.
        """
        stock_vol, bond_vol = vols
        covariance = np.array(
            [
                [stock_vol**2, correlation * stock_vol * bond_vol],
                [correlation * stock_vol * bond_vol, bond_vol**2],
            ]
        )
        stock = (1.0 / stock_vol) / (1.0 / stock_vol + 1.0 / bond_vol)
        shares = risk_shares((stock, 1.0 - stock), covariance)
        assert shares[0] == pytest.approx(0.5, abs=1e-12)
        assert shares[1] == pytest.approx(0.5, abs=1e-12)

    def test_the_risk_shares_sum_to_one_and_60_40_is_nowhere_near_balanced(self) -> None:
        """Qian's whole argument, on the illustrative volatilities the issue names.

        At 18 percent and 6 percent with no correlation the equity leg carries
        95.29 percent of a 60/40 portfolio's risk, and at 18 and 14 it carries
        78.81. Both say 60/40 is unbalanced and only the first says it is
        nearly all-equity risk, which is why the bond proxy decides how loud
        the book's point is. Neither pair is a measurement, so both are
        illustrations and neither reaches a prose surface as a result.
        """
        for vols, expected in (((0.18, 0.06), 0.952941), ((0.18, 0.14), 0.788108)):
            covariance = np.diag([vols[0] ** 2, vols[1] ** 2])
            shares = risk_shares(BENCHMARK_WEIGHTS, covariance)
            assert sum(shares) == pytest.approx(1.0, abs=1e-12)
            assert shares[0] == pytest.approx(expected, abs=5e-7)

    def test_qians_printed_weights_are_a_statement_about_volatilities(self) -> None:
        """23-77 implies an equity leg 3.3 times as volatile, and the band is his rounding.

        Weights that round to 23 and 77 put the ratio between 3.26 and 3.44, so
        a third digit read off the printed pair would be invented.
        """
        assert BOOK_VOL_RATIO == pytest.approx(0.77 / 0.23, abs=1e-12)
        assert round(BOOK_VOL_RATIO, 1) == 3.3
        low, high = BOOK_RATIO_BAND
        assert (round(low, 2), round(high, 2)) == (3.26, 3.44)
        assert low < BOOK_VOL_RATIO < high

    @pytest.mark.parametrize(
        ("correlation", "leverage"),
        [(-0.2, 2.02), (0.0, 1.88), (0.2, 1.78), (0.4, 1.71)],
    )
    def test_on_qians_weights_the_leverage_reads_the_correlation_and_nothing_else(
        self, correlation, leverage
    ) -> None:
        """Issue 15's declared map, to the two decimals it prints.

        The leg volatilities cancel once the weights fix their ratio, so this
        function takes no volatility at all. That is what makes 1.8 a statement
        about the stock-bond correlation rather than about either leg.
        """
        assert round(leverage_from_correlation(correlation), 2) == leverage

    def test_his_1_point_8_solves_to_a_correlation_near_0_16(self) -> None:
        """And the report says so without claiming to have recovered his correlation.

        1.8 carries two significant figures and so do the weights, and issue 15
        records that allowing for both puts the band at roughly 0.0 to 0.3. So
        the number below is what his printed pair implies and not what he
        measured.
        """
        implied = correlation_from_leverage(BOOK_LEVERAGE)
        assert implied == pytest.approx(0.1579, abs=5e-5)
        # A twentieth either side of his 1.8, which is well inside the rounding
        # his two significant figures leave. The map is steep, so the band on
        # the correlation is wide, which is why the report does not claim to
        # have recovered the one he measured.
        assert correlation_from_leverage(1.75) == pytest.approx(0.2783, abs=5e-5)
        assert correlation_from_leverage(1.85) == pytest.approx(0.0557, abs=5e-5)

    @pytest.mark.parametrize("correlation", [-0.6, -0.2, 0.0, 0.3, 0.7])
    def test_the_leverage_map_inverts(self, correlation) -> None:
        """Forwards then backwards returns the correlation it started from."""
        leverage = leverage_from_correlation(correlation)
        assert correlation_from_leverage(leverage) == pytest.approx(correlation, abs=1e-12)

    def test_a_leverage_no_correlation_reaches_comes_back_as_nothing(self) -> None:
        """A number outside ``[-1, 1]`` is not a correlation, so it is refused.

        On Qian's weights the map is bounded below and unbounded above. A
        correlation of +1 gives 1.5641, which is the least leverage any
        correlation reaches, and the leverage runs away as the correlation
        approaches −1, because the risk-parity portfolio's variance goes to
        zero there. So a leverage under 1.5641 solves to a number no
        correlation is, while a high one solves to a perfectly ordinary
        negative correlation. Reporting 1.4 as a correlation is worse than
        reporting none, which is why the report prints a refusal instead.
        """
        assert leverage_from_correlation(1.0) == pytest.approx(1.564088, abs=5e-7)
        assert correlation_from_leverage(1.5) is None
        assert correlation_from_leverage(1.2) is None
        assert correlation_from_leverage(4.0) == pytest.approx(-0.850977, abs=5e-7)
        assert correlation_from_leverage(BOOK_LEVERAGE) is not None


class TestTheRankingIsBuiltSoLeverageCannotMoveIt:
    """Why measuring the leverage inside the window it ranks is not look-ahead.

    A Sharpe ratio does not move with leverage under costless financing on
    excess returns. So the quantity the ranking reports is invariant to the
    leverage, and the only thing carried in from outside a window is the
    weights. That claim is load-bearing and it is checked rather than asserted.
    """

    def test_the_sharpe_difference_does_not_move_with_the_leverage(self, measured) -> None:
        """Rank the same window at three leverages and get one answer.

        Only the matching leverage makes the mean-difference identity below
        hold, so the two cases are separate: this one holds the ranking and
        that one holds the identity.
        """
        _, returns = measured["full span"]
        weights = (0.25, 0.75)
        base = rank_at_matched_volatility("x", returns, weights, weight_source="x", in_sample=True)
        for multiple in (0.5, 2.0, 3.0):
            levered = _rank_at_leverage(returns, weights, base.leverage * multiple)
            assert levered == pytest.approx(base.sharpe_difference, abs=1e-12)

    def test_at_matched_volatility_the_ranking_is_one_series_mean(self, rankings) -> None:
        """The identity that turns a comparison of two ratios into a measurable mean.

        With both portfolios at the same volatility their Sharpe difference is
        exactly the mean of the daily excess-return difference divided by that
        common volatility. Without it there is nothing for a standard error to
        be attached to, so this is what the whole error bar rests on.
        """
        for ranking in rankings.values():
            assert ranking.sharpe_difference == pytest.approx(
                ranking.mean_difference_annual / ranking.matched_volatility, abs=1e-12
            )

    def test_the_leverage_matches_the_two_volatilities_and_is_not_a_free_parameter(
        self, measured, rankings
    ) -> None:
        """Levering the parity portfolio by it lands exactly on 60/40's volatility."""
        for label, (_, returns) in measured.items():
            ranking = rankings[label]
            weights = _weights_used(measured, ranking)
            parity = portfolio_excess_returns(returns, weights)
            levered_vol = float((ranking.leverage * parity).std(ddof=1)) * math.sqrt(TRADING_DAYS)
            assert levered_vol == pytest.approx(ranking.matched_volatility, abs=1e-12)

    def test_the_assumed_rate_is_not_neutral_and_the_direction_is_exact(self, measured) -> None:
        """Raising the rate lowers the Sharpe difference, by 1/vol(60/40) less 1/vol(parity).

        The report states this rather than scanning the rate, because the rate
        was declared with the windows and a run that moves it is off the
        reproduction. The derivative is exact, so it is pinned rather than
        sampled, and it is negative on every window because the unlevered
        risk-parity portfolio is the quieter of the two.
        """
        _, returns = measured["full span"]
        legs = measure_legs(returns)
        weights = risk_parity_weights(legs)
        bench_vol = decompose("b", returns, BENCHMARK_WEIGHTS).volatility
        parity_vol = decompose("p", returns, weights).volatility
        expected = 1.0 / bench_vol - 1.0 / parity_vol
        assert expected < 0.0

        step = 1e-6
        low = _sharpe_difference(returns, weights, RISK_FREE)
        high = _sharpe_difference(returns, weights, RISK_FREE + step)
        assert (high - low) / step == pytest.approx(expected, rel=1e-6)


class TestTheWeightsDoNotSeeTheWindowTheyAreJudgedOn:
    """The one thing separating a ranking from a fitted allocation's ranking."""

    def test_the_rising_window_is_ranked_on_the_falling_windows_weights(
        self, measured, rankings
    ) -> None:
        """Strictly earlier data, available at the boundary, and it is not its own.

        Refitting inside the window would compare a fixed allocation against
        one that had seen every day it is judged on, and risk parity would win
        some of that comparison for a reason the book is not claiming.
        """
        rising = rankings["rising rates"]
        assert rising.in_sample is False
        assert rising.weight_source == "falling rates"

        carried = measured["falling rates"][0].parity
        own = measured["rising rates"][0].parity
        assert carried.stock_weight != pytest.approx(own.stock_weight, abs=1e-6)

        _, returns = measured["rising rates"]
        refitted = rank_at_matched_volatility(
            "rising rates",
            returns,
            (own.stock_weight, own.bond_weight),
            weight_source="rising rates",
            in_sample=True,
        )
        # Refitting moves the ranking, which is why it is not done. It moves it
        # in risk parity's favour here, which is the direction that would have
        # flattered the claim under test.
        assert refitted.sharpe_difference > rising.sharpe_difference

    def test_the_other_two_windows_say_in_sample_because_nothing_precedes_them(
        self, rankings
    ) -> None:
        """A label rather than a defect. Neither window has earlier data to borrow."""
        for label in ("full span", "falling rates"):
            assert rankings[label].in_sample is True
            assert rankings[label].weight_source == label

    def test_the_benchmark_never_sees_the_data_at_all(self, measured) -> None:
        """60/40 is fixed by definition, on every window, which is half the comparison."""
        for result, _ in measured.values():
            assert (result.benchmark.stock_weight, result.benchmark.bond_weight) == (0.6, 0.4)


# ============================================================
# The specification, which is what the near misses hold
# ============================================================


class TestTheSpecificationRatherThanTheNumber:
    """Five choices decide the figures below and each is moved here once."""

    def test_the_annualisation_is_252_and_the_near_counts_miss(self, measured) -> None:
        """251 and 260 are the plausible wrong answers and neither is close.

        Nothing in ``src/chan`` annualised anything before
        ``chan.kelly_leverage``, so this experiment inherits its convention
        rather than picking one, and the assertion is what stops the next
        experiment picking 260.
        """
        _, returns = measured["full span"]
        legs = measure_legs(returns)
        assert legs.stock_vol == pytest.approx(0.1854724463, abs=5e-10)
        daily_sd = float(returns.iloc[:, 0].std(ddof=1))
        for periods in (251, 260):
            assert abs(daily_sd * math.sqrt(periods) - legs.stock_vol) > 3e-4

    def test_the_dispersion_is_the_sample_form_dividing_by_n_minus_one(self, measured) -> None:
        """Which is what MATLAB's ``cov`` does and what ``chan.kelly_leverage`` reads.

        On 5,778 returns the two forms are 1.6e-5 apart on the volatility,
        which no figure this entry quotes could separate. It is pinned because
        the covariance matrix carries the same choice into the risk shares and
        the leverage, and a suite that never states it leaves a reader to guess.
        """
        _, returns = measured["full span"]
        sample = annualised_covariance(returns)
        population = returns.cov(ddof=0).to_numpy() * TRADING_DAYS
        assert math.sqrt(sample[0, 0]) - math.sqrt(population[0, 0]) == pytest.approx(
            1.605e-5, abs=5e-9
        )

    def test_the_risk_free_rate_comes_down_by_simple_division(self, measured) -> None:
        """``r / 252`` rather than ``(1 + r) ** (1 / 252) - 1``, and the two differ.

        By about 2 percent of the rate, which is small and is still a choice.
        Compounding it would move the 60/40 Sharpe ratio by 0.0069, so the pin
        names which division produced every ratio below.
        """
        _, returns = measured["full span"]
        simple = RISK_FREE / TRADING_DAYS
        compounded = (1.0 + RISK_FREE) ** (1.0 / TRADING_DAYS) - 1.0
        assert simple / compounded == pytest.approx(1.0198, abs=5e-5)

        at_simple = decompose("b", returns, BENCHMARK_WEIGHTS).sharpe
        raw = returns @ np.asarray(BENCHMARK_WEIGHTS)
        at_compounded = (
            float((raw - compounded).mean())
            * TRADING_DAYS
            / (float(raw.std(ddof=1)) * math.sqrt(TRADING_DAYS))
        )
        assert at_compounded - at_simple == pytest.approx(0.006858, abs=5e-7)

    def test_the_weights_are_constant_and_rebalanced_every_trading_day(
        self, joined, measured
    ) -> None:
        """A rebalancing rule rather than a holding, and buy and hold is a different thing.

        Held to two numbers rather than to a difference, because "they differ"
        is the assertion a mutation to the rebalancing survives. Buy and hold
        drifts toward whichever leg grew, which on this span is SPY at 11.47
        times against AGG at 1.97, so it ends the window far from 60/40 and
        turns a dollar into 7.67 against the rebalanced 6.28.
        """
        window = clip(joined, None, None)
        _, returns = measured["full span"]
        rebalanced = float((1.0 + returns @ np.asarray(BENCHMARK_WEIGHTS)).prod())
        growth = window.iloc[-1] / window.iloc[0]
        held = float(np.asarray(BENCHMARK_WEIGHTS) @ growth.to_numpy())
        assert rebalanced == pytest.approx(6.2779, abs=5e-5)
        assert held == pytest.approx(7.6672, abs=5e-5)
        assert float(growth.loc[STOCK]) == pytest.approx(11.4659, abs=5e-5)
        assert float(growth.loc[BOND]) == pytest.approx(1.9693, abs=5e-5)

    def test_a_non_finite_close_drops_its_return_rather_than_poisoning_the_moments(
        self,
    ) -> None:
        """A zero close divides to an infinity, which annualises to a mean that prints.

        The same rule ``chan.kelly_leverage.simple_returns`` applies to one
        leg, applied to two. The row goes when either leg is non-finite,
        because a portfolio return needs both, and the day that goes is the one
        dividing by the zero rather than the day falling to it. A loss of 100
        percent is a finite number and stays.
        """
        index = pd.bdate_range("2020-01-01", periods=5)
        frame = pd.DataFrame(
            {"SPY": [100.0, 101.0, 0.0, 103.0, 104.0], "AGG": [50.0, 50.5, 50.2, 50.9, 51.0]},
            index=index,
        )
        returns = simple_returns(frame)
        assert len(returns) == 3
        assert bool(np.isfinite(returns.to_numpy()).all())
        assert index[3] not in returns.index
        assert float(returns.loc[index[2], STOCK]) == pytest.approx(-1.0, abs=1e-12)


# ============================================================
# What these two vintages give, window by window
# ============================================================


class TestTheFullSpan:
    """The span the three published figures are compared against."""

    def test_the_leg_moments(self, measured) -> None:
        """Both legs' annualised volatility and mean, and their correlation.

        The mean returns are here because the ranking turns on them. AGG
        returns 3.09 percent a year against Chan's assumed 4 percent risk-free
        rate, so the bond leg's excess return over this span is negative and a
        78 percent bond weight is carrying it.
        """
        result, _ = measured["full span"]
        legs = result.legs
        assert (legs.start, legs.end, legs.days) == ("2003-09-30", "2026-09-17", 5778)
        assert legs.stock_vol == pytest.approx(0.185472, abs=5e-7)
        assert legs.bond_vol == pytest.approx(0.051650, abs=5e-7)
        assert legs.stock_mean == pytest.approx(0.123623, abs=5e-7)
        assert legs.bond_mean == pytest.approx(0.030897, abs=5e-7)
        assert legs.correlation == pytest.approx(-0.000215, abs=5e-7)

    def test_60_40_is_nearly_all_equity_risk(self, measured) -> None:
        """Qian's premise, measured. 60 percent of the capital carries 96.67 percent
        of the risk, which is the imbalance the whole argument is about."""
        result, _ = measured["full span"]
        bench = result.benchmark
        assert bench.stock_risk_share == pytest.approx(0.966717, abs=5e-7)
        assert bench.bond_risk_share == pytest.approx(0.033283, abs=5e-7)
        assert bench.volatility == pytest.approx(0.113181, abs=5e-7)
        assert bench.sharpe == pytest.approx(0.411135, abs=5e-7)

    def test_the_risk_parity_weights_land_about_a_point_off_qians(self, measured) -> None:
        """21.78 to 78.22 against his 23-77, and the ratio misses his band.

        The measured ratio is 3.5909 and weights rounding to 23 and 77 admit
        3.26 to 3.44, so the weights land close and the quantity they are a
        statement about does not. Both are reported, because a reader
        comparing only the weights would call this a match.
        """
        result, _ = measured["full span"]
        parity, legs = result.parity, result.legs
        assert parity.stock_weight == pytest.approx(0.217821, abs=5e-7)
        assert parity.bond_weight == pytest.approx(0.782179, abs=5e-7)
        assert parity.stock_risk_share == pytest.approx(0.5, abs=1e-12)
        assert legs.vol_ratio == pytest.approx(3.590935, abs=5e-7)
        assert legs.ratio_inside_the_band is False
        # The gap a prose surface quotes, at the whole percentage point Qian's
        # own two significant figures support, rounded from the full value.
        assert round((parity.stock_weight - BOOK_WEIGHTS[0]) * 100) == -1

    def test_the_leverage_and_what_it_implies(self, rankings) -> None:
        """1.9812 against the book's 1.8, which reads back to a correlation of −0.151.

        His 1.8 implies +0.158 on his own printed weights, so the two leverages
        are compared in one unit. The measured correlation is −0.0002 and is a
        different number, because this run's weights are not his: the two agree
        only when the measured weights are the printed ones.
        """
        ranking = rankings["full span"]
        assert ranking.leverage == pytest.approx(1.981188, abs=5e-7)
        assert ranking.implied_correlation == pytest.approx(-0.150793, abs=5e-7)
        assert round(ranking.leverage - BOOK_LEVERAGE, 1) == 0.2

    def test_the_ranking_goes_against_the_book_and_the_window_resolves_it(self, rankings) -> None:
        """60/40 beats levered risk parity by 0.2169 of Sharpe, robust t −2.17.

        Pinned as the measured difference and its robust t rather than as the
        comparison's result, because a boolean assertion survives any mutation
        that leaves the sign alone.
        """
        ranking = rankings["full span"]
        assert ranking.sharpe_benchmark == pytest.approx(0.411135, abs=5e-7)
        assert ranking.sharpe_parity == pytest.approx(0.194204, abs=5e-7)
        assert ranking.sharpe_difference == pytest.approx(-0.216931, abs=5e-7)
        assert ranking.mean_difference_annual == pytest.approx(-0.024552, abs=5e-7)
        assert (ranking.t_newey_west, ranking.lag, ranking.days) == pytest.approx(
            (-2.172682, 9, 5778), abs=5e-7
        )
        assert ranking.t_naive == pytest.approx(-1.752008, abs=5e-7)
        assert ranking.resolved is True


class TestTheTwoSubWindows:
    """Neither carries a published figure, because the book works no window.

    They are what turns the numbers into a verdict rather than a verdict
    themselves. The boundary is the Federal Reserve's first increase of the
    2022 tightening cycle, declared on issue 15 before any number existed.
    """

    def test_the_boundary_is_the_dated_external_event_the_issue_declared(self) -> None:
        """Moving it means editing the issue, so the constant is held to the date."""
        assert TIGHTENING_START == "2022-03-16"
        assert WINDOWS == (
            ("full span", None, None),
            ("falling rates", None, "2022-03-15"),
            ("rising rates", "2022-03-16", None),
        )

    def test_the_two_windows_partition_the_span_with_no_day_counted_twice(
        self, joined, measured
    ) -> None:
        """4,647 plus 1,130 daily returns against the full span's 5,778.

        One short, which is the return on the first day after the boundary.
        Splitting a price series into two windows loses the return that
        straddles the cut, and saying which day it is beats leaving a reader to
        wonder why the counts miss by one.
        """
        full = measured["full span"][0].legs.days
        falling = measured["falling rates"][0].legs.days
        rising = measured["rising rates"][0].legs.days
        assert (full, falling, rising) == (5778, 4647, 1130)
        assert falling + rising == full - 1
        assert measured["falling rates"][0].legs.end == "2022-03-15"
        assert measured["rising rates"][0].legs.start == "2022-03-17"

    def test_the_falling_rates_window(self, measured, rankings) -> None:
        """The quiet-bond regime, where the volatility ratio is furthest from Qian's."""
        result, _ = measured["falling rates"]
        legs, parity = result.legs, result.parity
        assert legs.stock_vol == pytest.approx(0.188748, abs=5e-7)
        assert legs.bond_vol == pytest.approx(0.048772, abs=5e-7)
        assert legs.vol_ratio == pytest.approx(3.869974, abs=5e-7)
        assert legs.correlation == pytest.approx(-0.068846, abs=5e-7)
        assert parity.stock_weight == pytest.approx(0.205340, abs=5e-7)
        assert result.benchmark.stock_risk_share == pytest.approx(0.982290, abs=5e-7)

        ranking = rankings["falling rates"]
        assert ranking.leverage == pytest.approx(2.147542, abs=5e-7)
        assert ranking.sharpe_difference == pytest.approx(-0.156507, abs=5e-7)
        assert ranking.t_newey_west == pytest.approx(-1.345475, abs=5e-7)
        assert ranking.lag == 9
        assert ranking.resolved is False

    def test_the_rising_rates_window(self, measured, rankings) -> None:
        """The loud-bond regime, ranked on weights that did not see it.

        The bond leg's volatility rises to 6.21 percent and the equity leg's
        falls, so the ratio drops to 2.76 and the in-window risk-parity weights
        move toward stocks, to 26.63 percent. They do not pass 60, so risk
        parity still holds less equity than 60/40 here and the book's
        correction still points the same way.
        """
        result, _ = measured["rising rates"]
        legs, parity = result.legs, result.parity
        assert legs.stock_vol == pytest.approx(0.171193, abs=5e-7)
        assert legs.bond_vol == pytest.approx(0.062127, abs=5e-7)
        assert legs.vol_ratio == pytest.approx(2.755525, abs=5e-7)
        assert legs.correlation == pytest.approx(0.244222, abs=5e-7)
        assert legs.bond_mean == pytest.approx(0.011596, abs=5e-7)
        assert parity.stock_weight == pytest.approx(0.266274, abs=5e-7)
        assert result.parity_tilts_toward_stocks is False
        assert result.benchmark.stock_risk_share == pytest.approx(0.900043, abs=5e-7)

        ranking = rankings["rising rates"]
        assert ranking.leverage == pytest.approx(1.657157, abs=5e-7)
        assert ranking.sharpe_benchmark == pytest.approx(0.507062, abs=5e-7)
        assert ranking.sharpe_parity == pytest.approx(0.009696, abs=5e-7)
        assert ranking.sharpe_difference == pytest.approx(-0.497366, abs=5e-7)
        assert ranking.mean_difference_annual == pytest.approx(-0.055417, abs=5e-7)
        assert ranking.t_newey_west == pytest.approx(-2.195624, abs=5e-7)
        assert ranking.lag == 6
        assert ranking.resolved is True

    def test_the_ratio_misses_qians_band_on_every_window_and_from_both_sides(
        self, measured
    ) -> None:
        """3.87, 3.59 and 2.76 against a band of 3.26 to 3.44.

        The two sub-windows straddle it, which is the finding that stops the
        full span's miss reading as a property of the proxy alone. A ratio that
        runs from below the band to above it inside one pair says the quantity
        Qian printed is a regime measurement rather than a constant.
        """
        ratios = {label: result.legs.vol_ratio for label, (result, _) in measured.items()}
        low, high = BOOK_RATIO_BAND
        assert ratios["falling rates"] > high
        assert ratios["rising rates"] < low
        assert not any(result.legs.ratio_inside_the_band for result, _ in measured.values())


# ============================================================
# The refusals, each naming which state it found
# ============================================================


class TestTheRefusals:
    """A run that cannot compute stops with a line rather than a traceback."""

    def test_a_window_too_short_for_a_volatility_names_itself(self, joined) -> None:
        """Under 30 common trading days, the floor the other two replications use."""
        with pytest.raises(WindowTooShort) as refused:
            measure_window("a thin slice", joined, "2020-01-02", "2020-01-10")
        assert "a thin slice" in str(refused.value)
        assert str(MIN_TRADING_DAYS) in str(refused.value)

    def test_the_floor_is_where_it_says_it_is(self, joined) -> None:
        """One day under refuses and one day over does not, so the bound is the bound."""
        window = clip(joined, "2020-01-02", None).index
        just_short = str(window[MIN_TRADING_DAYS - 2].date())
        just_enough = str(window[MIN_TRADING_DAYS - 1].date())
        with pytest.raises(WindowTooShort):
            measure_window("short", joined, "2020-01-02", just_short)
        measure_window("enough", joined, "2020-01-02", just_enough)

    def test_a_missing_vintage_reaches_the_operator_as_a_line(self, tmp_path, monkeypatch) -> None:
        """`main` turns the refusal into ``SystemExit``, the way the chapter does.

        The bond leg's entry is dropped from a copy of the committed record
        rather than the whole directory being emptied, so the line names AGG.
        An empty directory refuses earlier, on the manifest itself, and would
        pass an assertion that never reached the lookup this run depends on.
        """
        directory = committed_copy(tmp_path)
        manifest = directory / "vintages.jsonl"
        kept = [
            line
            for line in manifest.read_text(encoding="utf-8").splitlines()
            if '"symbol": "AGG"' not in line
        ]
        manifest.write_text("".join(f"{line}\n" for line in kept), encoding="utf-8")
        monkeypatch.setattr("sys.argv", ["chan.risk_parity"])
        monkeypatch.setattr("chan.paths.DATA_DIR", directory)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert "AGG" in str(stopped.value)

    def test_the_two_refusals_are_different_exceptions(self) -> None:
        """A run that could not read a vintage and one whose window was thin.

        Different facts with different fixes, which is the rule
        ``tests/test_series.py`` states for the refusals already here.
        """
        assert not issubclass(WindowTooShort, VintageUnavailable)
        assert not issubclass(VintageUnavailable, WindowTooShort)


# ============================================================
# The report, which is the surface a reader actually meets
# ============================================================


class TestTheReport:
    """What the run prints, held to the things a number is worthless without."""

    def test_the_report_names_both_vintages_and_the_specification(self, printed) -> None:
        """A figure separable from the vintage that produced it is not a result."""
        assert "yfinance_spy_adjusted_1993-01-29_2026-09-18_dl2026-09-18.csv" in printed
        assert "yfinance_agg_adjusted_2003-09-29_2026-09-17_dl2026-09-18.csv" in printed
        assert "downloaded 2026-09-18" in printed
        assert "adjusted closes on both legs" in printed
        assert "constant weights rebalanced every" in printed
        assert "no transaction costs and no financing spread" in printed
        assert BOOK_REF in printed

    def test_all_three_declared_windows_print_together(self, printed) -> None:
        """A window cannot be reported alone, which is what the declaration buys."""
        for label, _, _ in WINDOWS:
            assert f"--- {label}:" in printed
        assert TIGHTENING_START in printed
        assert "declared on issue 15 before any number existed" in printed

    def test_the_out_of_sample_window_says_so_and_the_others_say_in_sample(self, printed) -> None:
        """The label is the whole difference between two experiments."""
        assert "falling rates (out of sample)" in printed
        assert "full span (in sample)" in printed
        assert "falling rates (in sample)" in printed

    def test_a_window_that_does_not_resolve_the_ranking_says_so(self, printed) -> None:
        """A line a reader sees rather than an exception, because nothing has failed."""
        assert "does NOT resolve the ranking" in printed
        assert "resolves the ranking: the robust t clears 2" in printed

    def test_the_report_carries_the_exploratory_label_and_the_cost_omission(self, printed) -> None:
        """A replication is exploratory by construction, and charging no costs is not
        neutral. Both are on the page rather than only in the log."""
        assert "exploratory by construction" in printed
        assert "favours the levered portfolio the book argues for" in printed
        assert "docs/replication-log.md Entry 4" in printed

    def test_an_extra_window_is_reported_as_off_the_reproduction(self, joined) -> None:
        """Any window but the three declared ones carries no published counterpart."""
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            report(
                joined,
                {STOCK: load_close(STOCK), BOND: load_close(BOND)},
                extra=("the window you asked for", "2010-01-01", "2019-12-31"),
            )
        text = buffer.getvalue()
        assert "off the" in text and "reproduction" in text
        assert "--- the window you asked for:" in text
        # The three declared windows still print, so the extra one is an
        # addition rather than a replacement.
        for label, _, _ in WINDOWS:
            assert f"--- {label}:" in text

    def test_run_prints_the_same_report_the_module_entry_point_does(self) -> None:
        """``run`` is what ``main`` calls, so the pins above hold the shipped path."""
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            run()
        assert "--- full span:" in buffer.getvalue()


@pytest.fixture(scope="module")
def printed(joined):
    """The default report, captured once."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        report(joined, {STOCK: load_close(STOCK), BOND: load_close(BOND)})
    return buffer.getvalue()


def _rank_at_leverage(returns, weights, leverage: float) -> float:
    """The Sharpe difference at an arbitrary leverage, which should not move.

    Written here rather than as a module argument, because a leverage the run
    can be handed is a parameter somebody would eventually fit. The invariance
    is the claim, so the test supplies the leverage and the module does not.
    """
    parity = portfolio_excess_returns(returns, weights)
    bench = portfolio_excess_returns(returns, BENCHMARK_WEIGHTS)
    levered = leverage * parity
    sharpe_parity = float(levered.mean()) / float(levered.std(ddof=1)) * math.sqrt(TRADING_DAYS)
    sharpe_bench = float(bench.mean()) / float(bench.std(ddof=1)) * math.sqrt(TRADING_DAYS)
    return sharpe_parity - sharpe_bench


def _sharpe_difference(returns, weights, risk_free: float) -> float:
    parity = decompose("p", returns, weights, risk_free=risk_free)
    bench = decompose("b", returns, BENCHMARK_WEIGHTS, risk_free=risk_free)
    return parity.sharpe - bench.sharpe


def _weights_used(measured, ranking: Ranking) -> tuple[float, float]:
    """The weights a ranking actually ran on, read off the window it named."""
    parity = measured[ranking.weight_source][0].parity
    return parity.stock_weight, parity.bond_weight


def test_matching_leverage_agrees_with_the_one_the_ranking_reports(measured, rankings) -> None:
    """Two spellings of one quantity, so neither can drift from the other.

    ``matching_leverage`` is the public one and ``rank_at_matched_volatility``
    computes its own, because it already holds both series. Writing the
    arithmetic twice is how the two would come to disagree about one window.
    """
    for label, (_, returns) in measured.items():
        ranking = rankings[label]
        weights = _weights_used(measured, ranking)
        assert matching_leverage(returns, weights) == pytest.approx(ranking.leverage, abs=1e-12)
