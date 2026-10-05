"""The pins for the price spread, log price spread and ratio, *Algorithmic Trading*'s Example 3.1.

This file is the single authority for every number any prose surface quotes
about Example 3.1. ``docs/replication-log.md`` Entry 21 carries the verdicts
and points here row by row.

Every pin on the committed file reads one vintage and one specification, so
both are stated once here and carried in every figure's failure message as
:data:`SPEC`.

- **Vintage.** ``inputdata_etf/gld.csv`` and ``inputdata_etf/uso.csv``, two of
  the 67 ETFs lifted from Chan's ``inputData_ETF.mat``, chan-mat, adjusted,
  saved 2012-04-10, 1,500 days from 2006-04-26 to 2012-04-09. Its identity is
  the row of ``LIFTED_SOURCES`` in ``tests/support/committed_vintages.py``,
  which ``TestTheVintages`` holds the members to.
- **Specification.** ``PriceSpread.m``, ``LogPriceSpread.m`` and ``Ratio.m``
  at the mirror commit :mod:`chan.price_spread` names. A 20-row rolling hedge
  ratio from ``ols(y, [x ones])``, the first 20 rows dropped, ``numUnits`` the
  negative 20-row z-score from ``movingAvg`` and ``movingStd``, the return as
  profit over gross dollars with a NaN day set to 0, the APR compounded over
  252 days a year and the Sharpe ratio with MATLAB's n − 1 ``std``, over 1,480
  rows.

Each figure is pinned twice. Once at the six decimals the script's ``%f``
prints, against its closing comment, and once at eight, so a later change
cannot move it inside the printed digits unnoticed. The book's own rounding at
location 1505 is pinned beside them.

``TestTheRatio`` holds the miss and its cause. ``Ratio.m`` as published does
not land its comment's figures, and the same script with GLD and USO swapped
lands both. The swap was the third reading tried after the miss, and
[issue 340](https://github.com/l3a0/quantitative-trading/issues/340) names
the other two.

Exploratory. Reproducing Chan's figures spends the 2006 to 2012 sample on a
rule he chose. It first ran here on 2026-10-05.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from chan import price_spread as module
from chan.matlab_helpers import smart_moving_avg, smart_moving_std
from chan.price_spread import (
    BOOK_LOG_PRICE_SPREAD,
    BOOK_PRICE_SPREAD,
    LOOKBACK,
    SCRIPT_LOG_PRICE_SPREAD,
    SCRIPT_PRICE_SPREAD,
    SCRIPT_RATIO,
    SOURCE_FILE,
    X_SYMBOL,
    Y_SYMBOL,
    ExampleThreeOne,
    Run,
    daily_returns,
    example_three_one,
    linear_mean_reversion,
    linear_units,
    log_price_spread,
    main,
    price_spread,
    ratio,
    read_sources,
    rolling_hedge_ratio,
    run,
    zscore,
)
from chan.series import WindowCrossesScaleBreak, scale_breaks
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import LIFTED_SOURCES

SPEC = (
    "inputdata_etf/ GLD and USO closes over 1,500 days, 20-row rolling hedge ratio, "
    "first 20 rows dropped, numUnits minus the 20-row z-score with movingAvg and "
    "movingStd, profit over gross dollars, compounded APR, n - 1 Sharpe ratio, 1,480 rows"
)

# --- the committed file --------------------------------------------------------


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def result(sources) -> ExampleThreeOne:
    return example_three_one(sources[1])


def _zero_padded_lag(x: np.ndarray) -> np.ndarray:
    """A ``lag`` that pads its first row with 0 rather than NaN."""
    values = np.asarray(x, dtype=float)
    shifted = np.zeros_like(values)
    shifted[1:] = values[:-1]
    return shifted


def _runs(result: ExampleThreeOne) -> list[Run]:
    return [result.price_spread, result.log_price_spread, result.ratio, result.swapped_ratio]


class TestTheSpecification:
    def test_the_rule_is_the_three_scripts(self) -> None:
        assert (X_SYMBOL, Y_SYMBOL, LOOKBACK) == ("GLD", "USO", 20)

    def test_the_source_is_the_file_the_scripts_load(self) -> None:
        """Each script runs ``load('inputData_ETF', 'tday', 'syms', 'cl')``."""
        assert SOURCE_FILE == "inputData_ETF.mat"


class TestTheVintages:
    def test_the_members_are_the_pinned_source(self, sources) -> None:
        members, closes = sources
        vendor, basis, saved, folder, _ = LIFTED_SOURCES[SOURCE_FILE]
        assert {(m.vendor, m.price_basis, m.obtained) for m in members} == {(vendor, basis, saved)}
        assert [m.path for m in members] == [f"{folder}/gld.csv", f"{folder}/uso.csv"]
        assert list(closes.columns) == [X_SYMBOL, Y_SYMBOL]

    def test_both_legs_are_priced_on_all_1500_days(self, sources) -> None:
        _, closes = sources
        assert closes.shape == (1500, 2)
        assert not closes.isna().any().any()
        assert (str(closes.index[0].date()), str(closes.index[-1].date())) == (
            "2006-04-26",
            "2012-04-09",
        )

    def test_the_runs_keep_1480_rows_from_2006_05_24(self, result: ExampleThreeOne) -> None:
        for each in _runs(result):
            days = each.signal.days
            assert len(days) == len(each.daily) == 1480, each.signal.name
            assert str(days[0].date()) == "2006-05-24", each.signal.name
            assert str(days[-1].date()) == "2012-04-09", each.signal.name


class TestTheFigures:
    """The price spread and the log price spread, beside each script's comment and the book."""

    def test_the_price_spread_apr_is_chans_0_108335(self, result: ExampleThreeOne) -> None:
        apr = result.price_spread.apr
        assert apr == pytest.approx(0.10833467, abs=5e-9), SPEC
        assert f"{apr:f}" == SCRIPT_PRICE_SPREAD[0] == "0.108335", SPEC

    def test_the_books_about_10_9_percent_is_not_its_scripts_figure_rounded(
        self, result: ExampleThreeOne
    ) -> None:
        """Location 1505 prints "about 10.9 percent". The script's own 0.108335 rounds
        to 10.8, so the book's figure does not follow from what its script printed, and the
        run lands the script."""
        apr = result.price_spread.apr
        assert round(100 * apr, 1) == 10.8, SPEC
        assert round(100 * float(SCRIPT_PRICE_SPREAD[0]), 1) == 10.8
        assert BOOK_PRICE_SPREAD[0] == 10.9

    def test_the_price_spread_sharpe_ratio_is_chans_0_589651(self, result: ExampleThreeOne) -> None:
        sharpe = result.price_spread.sharpe
        assert sharpe == pytest.approx(0.58965098, abs=5e-9), SPEC
        assert f"{sharpe:f}" == SCRIPT_PRICE_SPREAD[1] == "0.589651", SPEC
        assert round(sharpe, 2) == BOOK_PRICE_SPREAD[1] == 0.59, SPEC

    def test_the_log_price_spread_apr_is_chans_0_088863(self, result: ExampleThreeOne) -> None:
        apr = result.log_price_spread.apr
        assert apr == pytest.approx(0.08886345, abs=5e-9), SPEC
        assert f"{apr:f}" == SCRIPT_LOG_PRICE_SPREAD[0] == "0.088863", SPEC
        assert round(100 * apr) == BOOK_LOG_PRICE_SPREAD[0] == 9, SPEC

    def test_the_log_price_spread_sharpe_ratio_is_chans_0_504153(
        self, result: ExampleThreeOne
    ) -> None:
        sharpe = result.log_price_spread.sharpe
        assert sharpe == pytest.approx(0.50415292, abs=5e-9), SPEC
        assert f"{sharpe:f}" == SCRIPT_LOG_PRICE_SPREAD[1] == "0.504153", SPEC
        assert round(sharpe, 1) == BOOK_LOG_PRICE_SPREAD[1] == 0.5, SPEC

    def test_the_first_position_is_held_into_2006_06_22(self, result: ExampleThreeOne) -> None:
        """``movingStd`` first fills on the 20th kept row, 2006-06-21, and its position
        earns from the next close. Every row before returns the script's zero-filled 0."""
        for each in _runs(result):
            first_units = np.flatnonzero(np.isfinite(each.units))[0]
            first_return = np.flatnonzero(each.daily)[0]
            assert first_units == LOOKBACK - 1, each.signal.name
            assert str(each.signal.days[first_units].date()) == "2006-06-21", each.signal.name
            assert str(each.signal.days[first_return].date()) == "2006-06-22", each.signal.name


class TestTheRatio:
    """``Ratio.m`` as published misses its comment, and the swapped legs land it."""

    def test_the_published_script_misses_both_figures(self, result: ExampleThreeOne) -> None:
        apr, sharpe = result.ratio.apr, result.ratio.sharpe
        assert apr == pytest.approx(-0.13460781, abs=5e-9), SPEC
        assert sharpe == pytest.approx(-0.70252227, abs=5e-9), SPEC
        assert (f"{apr:f}", f"{sharpe:f}") == ("-0.134608", "-0.702522"), SPEC
        assert (f"{apr:f}", f"{sharpe:f}") != SCRIPT_RATIO, SPEC

    def test_the_script_with_gld_and_uso_swapped_lands_both(self, result: ExampleThreeOne) -> None:
        apr, sharpe = result.swapped_ratio.apr, result.swapped_ratio.sharpe
        assert apr == pytest.approx(-0.14152186, abs=5e-9), SPEC
        assert sharpe == pytest.approx(-0.74666317, abs=5e-9), SPEC
        assert (f"{apr:f}", f"{sharpe:f}") == SCRIPT_RATIO == ("-0.141522", "-0.746663"), SPEC

    def test_the_swap_trades_gld_over_uso_and_buys_gld_on_a_positive_unit(
        self, sources, result: ExampleThreeOne
    ) -> None:
        _, closes = sources
        swapped = result.swapped_ratio.signal
        np.testing.assert_array_equal(
            swapped.value, (closes[X_SYMBOL] / closes[Y_SYMBOL]).to_numpy()[LOOKBACK:]
        )
        np.testing.assert_array_equal(
            swapped.prices, closes[[Y_SYMBOL, X_SYMBOL]].to_numpy()[LOOKBACK:]
        )
        assert (swapped.unit_dollars == [-1.0, 1.0]).all()


class TestTheClaims:
    """Location 1505's two claims, with the criteria issue 340 wrote after the first
    transcription ran. Each is the sentence's own word, so no threshold was left to choose."""

    def test_the_ratio_loses_13_5_or_14_2_percent_a_year(self, result: ExampleThreeOne) -> None:
        """Entry 21's conclusion quotes both APRs at one decimal of a percent."""
        assert round(100 * result.ratio.apr, 1) == -13.5, SPEC
        assert round(100 * result.swapped_ratio.apr, 1) == -14.2, SPEC

    def test_the_ratio_loses_money(self, result: ExampleThreeOne) -> None:
        """Location 1505: "perform poorly, with a negative APR". It holds on the script as published
        and on the swapped legs both."""
        assert result.ratio.apr < 0, SPEC
        assert result.swapped_ratio.apr < 0, SPEC

    def test_the_log_price_spread_is_below_the_price_spread_on_both_figures(
        self, result: ExampleThreeOne
    ) -> None:
        """Location 1505: "The APR of 9 percent and Sharpe ratio of 0.5 are actually lower"."""
        assert result.log_price_spread.apr < result.price_spread.apr, SPEC
        assert result.log_price_spread.sharpe < result.price_spread.sharpe, SPEC


class TestWhatMovesNothing:
    """Two choices a port could get wrong that no Example 3.1 figure can see.

    Each is held here so a reader does not mistake these figures for evidence
    about them. ``tests/test_matlab_helpers.py`` holds each helper on its own.
    """

    def test_lag_padding_with_0_or_nan_gives_the_same_returns(self, sources) -> None:
        """Neither mirror holds ``lag.m``. Each script's first held position is NaN,
        so its first row comes out NaN and is set to 0 whichever padding runs."""
        _, closes = sources
        nan_padded = example_three_one(closes)
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(module, "lag1", _zero_padded_lag)
            zero_padded = example_three_one(closes)
        for nan_run, zero_run in zip(_runs(nan_padded), _runs(zero_padded), strict=True):
            np.testing.assert_array_equal(nan_run.daily, zero_run.daily)

    def test_the_standard_deviations_divisor_cancels_out_of_the_return(self, sources) -> None:
        """The return is profit over gross dollars, so scaling every unit by one factor
        leaves it where it was. Book two's ``smartMovingStd``, which divides by n, gives
        the same figures as ``movingStd``. Example 3.2's thresholds do not cancel."""
        _, closes = sources
        plain = example_three_one(closes)
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(module, "moving_std", smart_moving_std)
            patch.setattr(module, "moving_avg", smart_moving_avg)
            smart = example_three_one(closes)
        for plain_run, smart_run in zip(_runs(plain), _runs(smart), strict=True):
            assert not np.allclose(plain_run.units[LOOKBACK:], smart_run.units[LOOKBACK:])
            np.testing.assert_allclose(plain_run.daily, smart_run.daily, rtol=0, atol=1e-12)


class TestTheScaleBreakDecision:
    def test_neither_leg_carries_a_flagged_day(self, sources) -> None:
        """``tests/test_scale_breaks.py`` pins 58 days in eight other ETFs of this file."""
        _, closes = sources
        assert scale_breaks(closes[X_SYMBOL]) == []
        assert scale_breaks(closes[Y_SYMBOL]) == []

    def test_a_leg_that_changed_scale_is_refused(self, sources, monkeypatch) -> None:
        members, closes = sources
        broken = closes.copy()
        broken.loc[broken.index[700:], Y_SYMBOL] *= 10
        monkeypatch.setattr(module, "load_panel", lambda *_a, **_k: (members, broken))
        with pytest.raises(WindowCrossesScaleBreak, match="uso"):
            read_sources()


class TestTheRun:
    def test_it_prints_each_figure_beside_chans(self, sources, monkeypatch, capsys) -> None:
        monkeypatch.setattr(module, "read_sources", lambda *_a, **_k: sources)
        run()
        out = capsys.readouterr().out
        for line, figures in (
            ("Price spread, APR", ("0.108335", "0.108335", "10.9%")),
            ("Price spread, Sharpe ratio", ("0.589651", "0.589651", "0.59")),
            ("Log price spread, APR", ("0.088863", "0.088863", "9%")),
            ("Log price spread, Sharpe ratio", ("0.504153", "0.504153", "0.5")),
            ("Ratio, USO/GLD, APR", ("-0.134608", "-0.141522", "negative")),
            ("Ratio, USO/GLD, Sharpe ratio", ("-0.702522", "-0.746663", "none")),
            ("Ratio, legs swapped, APR", ("-0.141522", "none", "none")),
            ("Ratio, legs swapped, Sharpe ratio", ("-0.746663", "none", "none")),
        ):
            row = next(r for r in out.splitlines() if r.strip().startswith(line + " "))
            assert row.split()[-3:] == list(figures), row
        assert "inputdata_etf/gld.csv" in out and "inputdata_etf/uso.csv" in out
        assert "2006-05-24 to 2012-04-09, 1480 trading days" in out
        assert "Exploratory" in out and "Entry 21" in out


# --- the rule on synthetic arrays ------------------------------------------------


DAYS = pd.bdate_range("2020-01-01", periods=8)


class TestTheRule:
    def test_the_hedge_ratio_recovers_a_planted_slope_and_is_nan_before_the_window(self) -> None:
        x = np.array([1.0, 3.0, 2.0, 5.0, 4.0, 7.0])
        hedge = rolling_hedge_ratio(2.5 * x + 3.0, x, 3)
        assert np.isnan(hedge[:2]).all()
        np.testing.assert_allclose(hedge[2:], 2.5, rtol=0, atol=1e-12)

    def test_the_hedge_ratio_fits_an_intercept(self) -> None:
        """Through the origin, ``y = x + 10`` would give a slope far from 1."""
        x = np.array([1.0, 2.0, 3.0, 4.0])
        assert rolling_hedge_ratio(x + 10.0, x, 4)[3] == pytest.approx(1.0, abs=1e-12)

    def test_the_hedge_ratios_window_ends_on_its_own_row(self) -> None:
        """Row 2 of a window of 3 reads rows 0 to 2. A shock on row 3 moves rows 3 on only."""
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y = 2.0 * x
        shocked = y.copy()
        shocked[3] += 5.0
        before, after = rolling_hedge_ratio(y, x, 3), rolling_hedge_ratio(shocked, x, 3)
        assert after[2] == pytest.approx(before[2], abs=1e-12)
        assert after[3] != pytest.approx(before[3], abs=1e-6)

    def test_series_of_two_shapes_are_refused(self) -> None:
        with pytest.raises(ValueError, match="two series of one shape"):
            rolling_hedge_ratio(np.ones(5), np.ones(4), 3)

    def test_a_window_too_short_to_fit_a_slope_and_an_intercept_is_refused(self) -> None:
        """Two rows fit both exactly, and one leaves the slope undetermined."""
        with pytest.raises(ValueError, match="at least 3 rows, not 2"):
            rolling_hedge_ratio(np.arange(5.0), np.arange(5.0), 2)

    def test_a_window_holding_a_nan_gives_a_nan_slope_and_the_rest_still_fit(self) -> None:
        """Chan's ``ols`` returns NaN on such a window rather than stopping the run."""
        x = np.array([1.0, 3.0, 2.0, np.nan, 4.0, 7.0, 5.0, 6.0])
        hedge = rolling_hedge_ratio(2.0 * x + 1.0, x, 3)
        assert np.isnan(hedge[[0, 1, 3, 4, 5]]).all()
        np.testing.assert_allclose(hedge[[2, 6, 7]], 2.0, rtol=0, atol=1e-12)

    def test_days_of_another_length_are_refused(self) -> None:
        x = np.arange(1.0, 9.0)
        for build in (price_spread, log_price_spread, ratio):
            with pytest.raises(ValueError, match="one length, not 7, 8 and 8"):
                build(DAYS[:7], x, x + 1.0, 3)

    def test_each_signal_drops_the_first_lookback_rows(self) -> None:
        x = np.arange(1.0, 9.0)
        y = 3.0 * x + np.array([0.1, -0.2, 0.3, 0.0, -0.1, 0.2, -0.3, 0.1])
        for signal in (
            price_spread(DAYS, x, y, 3),
            log_price_spread(DAYS, x, y, 3),
            ratio(DAYS, x, y, 3),
        ):
            assert list(signal.days) == list(DAYS[3:]), signal.name
            np.testing.assert_array_equal(signal.prices, np.column_stack([x, y])[3:])

    def test_the_price_spread_holds_minus_h_dollars_of_x_per_dollar_of_y_per_share(self) -> None:
        x = np.arange(1.0, 9.0)
        y = 3.0 * x + np.array([0.1, -0.2, 0.3, 0.0, -0.1, 0.2, -0.3, 0.1])
        signal = price_spread(DAYS, x, y, 3)
        hedge = rolling_hedge_ratio(y, x, 3)[3:]
        np.testing.assert_array_equal(signal.hedge, hedge)
        np.testing.assert_array_equal(signal.value, y[3:] - hedge * x[3:])
        np.testing.assert_array_equal(signal.unit_dollars, np.column_stack([-hedge * x[3:], y[3:]]))

    def test_the_log_price_spread_fits_and_trades_on_log_prices_in_dollars(self) -> None:
        x = np.arange(1.0, 9.0)
        y = 3.0 * x + np.array([0.1, -0.2, 0.3, 0.0, -0.1, 0.2, -0.3, 0.1])
        signal = log_price_spread(DAYS, x, y, 3)
        hedge = rolling_hedge_ratio(np.log(y), np.log(x), 3)[3:]
        np.testing.assert_array_equal(signal.hedge, hedge)
        np.testing.assert_array_equal(signal.value, np.log(y[3:]) - hedge * np.log(x[3:]))
        np.testing.assert_array_equal(signal.unit_dollars, np.column_stack([-hedge, np.ones(5)]))

    def test_the_ratio_is_y_over_x_with_a_dollar_short_x_and_long_y(self) -> None:
        x, y = np.arange(1.0, 9.0), np.arange(2.0, 10.0)
        signal = ratio(DAYS, x, y, 3)
        assert signal.hedge is None
        np.testing.assert_array_equal(signal.value, y[3:] / x[3:])
        assert (signal.unit_dollars == [-1.0, 1.0]).all()

    def test_the_units_are_minus_the_z_score(self) -> None:
        """A value above its moving average is sold, in proportion to the distance."""
        value = np.array([1.0, 2.0, 3.0, 10.0])
        z = zscore(value, 3)
        assert np.isnan(z[:2]).all()
        assert z[3] == pytest.approx((10.0 - 5.0) / np.std([2.0, 3.0, 10.0], ddof=1), abs=1e-12)
        np.testing.assert_array_equal(linear_units(value, 3), -z)
        assert linear_units(value, 3)[3] < 0

    def test_the_return_is_yesterdays_dollars_times_todays_move_over_gross_dollars(self) -> None:
        positions = np.array([[np.nan, np.nan], [-2.0, 1.0], [1.0, 3.0]])
        prices = np.array([[10.0, 20.0], [10.0, 20.0], [11.0, 19.0]])
        daily = daily_returns(positions, prices)
        assert daily[0] == 0.0 and daily[1] == 0.0
        assert daily[2] == pytest.approx((-2.0 * 0.1 + 1.0 * -0.05) / 3.0, abs=1e-15)

    def test_a_nan_in_either_leg_spoils_the_day_and_sets_it_to_0(self) -> None:
        """MATLAB's ``sum`` does not skip a NaN, so one leg's NaN takes the day with it."""
        positions = np.array([[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]])
        prices = np.array([[10.0, 20.0], [11.0, np.nan], [12.0, 20.0]])
        assert list(daily_returns(positions, prices)) == [0.0, 0.0, 0.0]

    def test_doubling_every_unit_moves_no_return(self) -> None:
        signal = price_spread(
            DAYS, np.arange(1.0, 9.0), np.array([3, 7, 8, 12, 16, 17, 22, 25.0]), 3
        )
        once = linear_mean_reversion(signal, 3)
        positions = 2.0 * once.positions
        np.testing.assert_allclose(daily_returns(positions, signal.prices), once.daily, atol=1e-15)


class TestTheRefusals:
    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage is lifted from inputData_ETF.mat"),
            WindowCrossesScaleBreak("inputdata_etf/uso.csv changes scale on 2009-01-02"),
        ],
    )
    def test_main_prints_a_refusal_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(module, "read_sources", refuse)
        monkeypatch.setattr("sys.argv", ["price_spread"])
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)
