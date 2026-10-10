"""The pins for AUD.USD against CAD.USD, *Algorithmic Trading*'s Example 5.1.

This file is the single authority for every number a prose surface quotes
about this example and the rows beside it. The one exception is
``blog/aud-cad-johansen-lessons.md``: ``tests/test_aud_cad_johansen_figures.py``
holds the numbers its figure draws, and README lists what it says that nothing
asserts. ``docs/replication-log.md`` Entry 25 carries the
verdicts and points here row by row.

Every pin on the committed files reads one vintage and one specification, so
both are stated once here.

- **Vintage.** ``pythoncodesanddata/inputData_AUDUSD_20120426.csv`` and
  ``pythoncodesanddata/inputData_USDCAD_20120426.csv``, chan-py, raw, saved
  2018-12-12, 862 days from 2009-01-02 to 2012-04-26, read through
  ``chan.series.load_port_close``. Row 5 also reads
  ``pythoncodesanddata/AUDCAD_unequal_ret.csv``, chan-py, return, saved
  2018-12-26, through ``chan.series.load_returns``. All three come from
  ``PythonCodesAndData.zip`` at EpchanPreview ``e4bc46f``, and their identity
  is their rows of ``PYTHON_PORT`` in ``tests/support/committed_vintages.py``.
- **Specification.** ``AUDCAD_unequal.m`` at EpchanPreview ``e4bc46f``, git
  blob ``5b8fbc2``, as :mod:`chan.aud_cad_johansen` transcribes it. AUD.USD and
  the inverse of USD.CAD, a Johansen test with ``p = 0`` and ``k = 1`` on the
  250 rows before each day, its first eigenvector as that day's hedge, a 20-row
  z-score including the day, units of minus that z-score, and the return as
  profit over the previous day's gross position. The figures are taken over the
  612 test rows, annualised over 252 days, with no risk-free rate and no cost.

Each published figure is held twice: at the computed value's own precision,
which is what lets the log quote it, and at the precision Chan printed,
through ``matches``.

Exploratory. Reproducing Chan's figures spends the 2009 to 2012 sample on a
rule he chose, with a training length he says was chosen in hindsight. The
example first ran on 2026-10-05.
"""

from __future__ import annotations

import dataclasses

import numpy as np
import pandas as pd
import pytest
from scipy import stats

from chan import aud_cad_johansen as module
from chan import paths
from chan.aud_cad_johansen import (
    AGREEMENT,
    BOOK_APR_PERCENT,
    BOOK_FIRST_DAY,
    BOOK_LAST_DAY,
    BOOK_SHARPE,
    DAILY_SAVED,
    JOHANSEN_K,
    JOHANSEN_P,
    LEGS,
    SCRIPT_APR,
    SCRIPT_KELLY,
    SCRIPT_LOOKBACK,
    SCRIPT_SHARPE,
    SCRIPT_TRAINING_DAYS,
    AudCad,
    agreement,
    aud_cad,
    cross_rates,
    daily_returns,
    figures,
    main,
    read_sources,
    run,
    units_on,
)
from chan.johansen import johansen
from chan.khandani_lo_book_two import matches
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import PYTHON_PORT, RETURN_CALENDAR


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def frame(sources) -> pd.DataFrame:
    return cross_rates(sources.audusd[1], sources.usdcad[1])


@pytest.fixture(scope="module")
def result(frame) -> AudCad:
    return aud_cad(frame)


@pytest.fixture(scope="module")
def saved(sources) -> np.ndarray:
    return sources.saved[1]


@pytest.fixture
def no_arguments(monkeypatch):
    """``main`` parses ``sys.argv``, which under pytest holds pytest's own arguments."""
    monkeypatch.setattr("sys.argv", ["chan.aud_cad_johansen"])


def _synthetic(rows: int = 80, seed: int = 7) -> pd.DataFrame:
    """Two random walks near AUD.USD and CAD.USD, with a shared component so they co-move."""
    rng = np.random.default_rng(seed)
    common = np.cumsum(rng.normal(scale=0.004, size=rows))
    aud = 0.90 + common + np.cumsum(rng.normal(scale=0.002, size=rows))
    cad = 0.95 + 0.8 * common + np.cumsum(rng.normal(scale=0.002, size=rows))
    return pd.DataFrame(
        {LEGS[0]: aud, LEGS[1]: cad}, index=pd.bdate_range("2020-01-01", periods=rows)
    )


def _returns_from(prices: np.ndarray, hedge: np.ndarray, start: int, lookback: int) -> np.ndarray:
    """Lines 36 to 54 again from a given hedge, so a case can change one day's vector."""
    units = np.full(len(prices), np.nan)
    for t in range(start, len(prices)):
        units[t] = units_on(prices, hedge[t], t, lookback)
    return daily_returns(units[:, None] * hedge * prices, prices)


class TestTheSpecification:
    def test_the_script_trains_on_250_days_and_scores_over_20(self) -> None:
        assert (SCRIPT_TRAINING_DAYS, SCRIPT_LOOKBACK) == (250, 20)
        assert (JOHANSEN_P, JOHANSEN_K) == (0, 1)

    def test_the_legs_are_aud_then_the_inverse_of_usdcad(self, sources, frame) -> None:
        """``y = [aud cad]``, so every hedge vector's first weight is AUD.USD's."""
        assert LEGS == ("AUDUSD", "CADUSD")
        assert list(frame.columns) == list(LEGS)
        np.testing.assert_array_equal(frame["AUDUSD"].to_numpy(), sources.audusd[1].to_numpy())
        np.testing.assert_array_equal(
            frame["CADUSD"].to_numpy(), 1.0 / sources.usdcad[1].to_numpy()
        )


class TestTheVintages:
    def test_each_read_is_its_pinned_entry(self, sources) -> None:
        for entry in sources.entries:
            vendor, symbol, basis, saved_date, _, _ = PYTHON_PORT[entry.path]
            assert (entry.vendor, entry.symbol, entry.price_basis, entry.saved_date) == (
                vendor,
                symbol,
                basis,
                saved_date,
            )
        assert [entry.path for entry in sources.entries] == [
            "pythoncodesanddata/inputData_AUDUSD_20120426.csv",
            "pythoncodesanddata/inputData_USDCAD_20120426.csv",
            "pythoncodesanddata/AUDCAD_unequal_ret.csv",
        ]
        assert DAILY_SAVED == "2018-12-12"

    def test_the_two_daily_files_hold_862_positive_closes_on_the_same_dates(self, sources) -> None:
        aud, cad = sources.audusd[1], sources.usdcad[1]
        assert aud.index.equals(cad.index)
        assert len(aud) == 862
        assert (str(aud.index[0].date()), str(aud.index[-1].date())) == (
            "2009-01-02",
            "2012-04-26",
        )
        for closes in (aud, cad):
            assert np.isfinite(closes.to_numpy()).all()
            assert (closes > 0).all()


class TestRow1TheTestWindow:
    def test_612_returns_from_the_books_first_day_to_its_last(self, result) -> None:
        days = result.test_days
        assert len(result.test) == len(days) == 612
        assert (str(days[0].date()), str(days[-1].date())) == (BOOK_FIRST_DAY, BOOK_LAST_DAY)
        assert (BOOK_FIRST_DAY, BOOK_LAST_DAY) == ("2009-12-18", "2012-04-26")

    def test_the_test_days_are_the_rows_the_return_calendar_names(self, sources, result):
        """``RETURN_CALENDAR`` is what the manifest check dates Chan's file by."""
        calendar, trained = RETURN_CALENDAR
        assert calendar == sources.audusd[0].path
        assert trained == SCRIPT_TRAINING_DAYS
        assert result.test_days.equals(sources.audusd[1].index[trained:])


class TestRows2To4TheFigures:
    def test_row_2_the_apr(self, result) -> None:
        apr = result.figures.apr
        assert apr == pytest.approx(0.1124100634, abs=1e-10)
        assert matches(apr, SCRIPT_APR)
        assert matches(100 * apr, BOOK_APR_PERCENT)

    def test_row_3_the_sharpe_ratio(self, result) -> None:
        sharpe = result.figures.sharpe
        assert sharpe == pytest.approx(1.6108902337, abs=1e-10)
        assert matches(sharpe, SCRIPT_SHARPE)
        assert matches(sharpe, BOOK_SHARPE)

    def test_row_4_the_kelly_leverage(self, result) -> None:
        kelly = result.figures.kelly
        assert kelly == pytest.approx(23.8453277641, abs=1e-10)
        assert matches(kelly, SCRIPT_KELLY)

    def test_the_kelly_leverage_is_mean_over_the_sample_variance(self, result) -> None:
        """Line 65's ``std`` divides by n − 1. The population form gives 23.884354."""
        test = result.test
        assert result.figures.kelly == pytest.approx(test.mean() / test.var(ddof=1), rel=1e-12)
        assert test.mean() / test.var(ddof=0) == pytest.approx(23.884354, abs=1e-6)

    def test_the_figures_are_wrong_on_the_wrong_rows(self, result) -> None:
        """Over all 862 rows the 250 zeros of training dilute every figure."""
        whole = figures(result.daily)
        assert not matches(whole.apr, SCRIPT_APR)
        assert not matches(whole.sharpe, SCRIPT_SHARPE)


class TestRow5TheReturnsAreChans:
    """Row 5. No source prints it, so it carries no verdict. Rows 2 to 4 cite it."""

    def test_every_row_agrees_within_the_declared_criterion(self, result, saved) -> None:
        found = agreement(result.test, saved, result.test_days)
        assert AGREEMENT == 1e-9
        assert found.holds
        assert found.rows_over == 0
        assert found.first_over is None
        assert 0 < found.largest <= AGREEMENT
        assert found.largest == np.abs(result.test - saved).max()

    def test_chans_saved_returns_give_all_three_printed_figures(self, saved) -> None:
        """Measurement 1 on issue 345, which is what makes row 5 decide rows 2 to 4."""
        his = figures(saved)
        assert matches(his.apr, SCRIPT_APR)
        assert matches(his.sharpe, SCRIPT_SHARPE)
        assert matches(his.kelly, SCRIPT_KELLY)

    def test_a_moved_row_is_reported_by_its_date(self, result, saved) -> None:
        moved = saved.copy()
        moved[100] += 1e-6
        found = agreement(result.test, moved, result.test_days)
        assert not found.holds
        assert found.rows_over == 1
        assert found.first_over == result.test_days[100]
        assert found.largest == pytest.approx(1e-6, rel=1e-6)

    def test_a_row_that_is_not_a_number_does_not_agree(self, result, saved) -> None:
        """``nan > 1e-9`` is False, so a plain comparison would call this row a match."""
        missing = saved.copy()
        missing[7] = np.nan
        found = agreement(result.test, missing, result.test_days)
        assert not found.holds
        assert found.rows_over == 1
        assert found.first_over == result.test_days[7]

    def test_a_constant_scale_on_either_leg_still_matches(self, frame, saved) -> None:
        """So row 5 says the inputs agree with Chan's up to a scale per leg, and no more."""
        again = aud_cad(frame * [2.0, 0.37])
        assert agreement(again.test, saved, again.test_days).holds

    def test_one_digit_on_a_test_window_close_breaks_the_match(self, frame, saved) -> None:
        """The files quote six decimals, so 1e-6 is one unit in the last digit.

        A close in the test window enters that day's or the next day's simple
        return, and the match fails. A close in the first training row reaches
        the returns only through the hedge, and the same change passes.
        """
        for row, breaks in ((SCRIPT_TRAINING_DAYS + 150, True), (0, False)):
            moved = frame.copy()
            moved.iloc[row, 0] += 1e-6
            again = aud_cad(moved)
            assert (not agreement(again.test, saved, again.test_days).holds) is breaks

    def test_series_of_different_lengths_are_refused(self, result, saved) -> None:
        with pytest.raises(ValueError, match="cannot be compared row by row"):
            agreement(result.test[1:], saved, result.test_days)

    def test_a_calendar_of_another_length_is_refused(self, result, saved) -> None:
        with pytest.raises(ValueError, match="cannot be compared row by row"):
            agreement(result.test, saved, result.test_days[1:])

    def test_a_difference_of_exactly_the_criterion_agrees(self) -> None:
        """The criterion is "at most 1e-9", so the boundary row agrees."""
        days = pd.bdate_range("2020-01-01", periods=2)
        assert agreement(np.array([0.0, 0.0]), np.array([0.0, AGREEMENT]), days).holds
        assert not agreement(np.array([0.0, 0.0]), np.array([0.0, 2 * AGREEMENT]), days).holds


class TestBesideTheReplication:
    """No book prints these, so none carries a verdict."""

    def test_the_trace_test_finds_a_relation_in_26_of_612_windows(self, result) -> None:
        """Nineteen find two, which the test reads as each series stationary on its own."""
        assert len(result.trace_relations) == 612
        assert np.bincount(result.trace_relations, minlength=3).tolist() == [586, 7, 19]

    def test_the_eigen_test_finds_one_in_11(self, result) -> None:
        assert np.bincount(result.eigen_relations, minlength=3).tolist() == [601, 11, 0]

    def test_the_relation_counts_are_the_windows_own_tests(self, frame, result) -> None:
        prices = frame.to_numpy()
        t = SCRIPT_TRAINING_DAYS + 300
        tested = johansen(prices[t - SCRIPT_TRAINING_DAYS : t], 0, 1)
        assert result.trace_relations[300] == tested.relations("trace", 95)
        assert result.eigen_relations[300] == tested.relations("eigen", 95)

    def test_the_last_days_hedge_holds_0_7797_of_cad_per_aud_short(self, result) -> None:
        """In units. At that day's quotes the dollars split 1 to −0.7622, long AUD."""
        np.testing.assert_allclose(result.last_hedge, [1.0, -0.7796733233], rtol=0, atol=1e-10)
        np.testing.assert_allclose(
            result.positions[-1] / result.positions[-1, 0], [1.0, -0.7622442800], rtol=0, atol=1e-10
        )
        assert result.units[-1] > 0

    def test_the_trace_tests_26_windows_fall_in_three_stretches(self, result) -> None:
        """Every two-relation window sits in the first or the third, and the eigen test's 11
        run from the second's first day to a day past its last."""
        days = result.test_days
        stretches = [
            ("2010-02-09", "2010-04-08", [1, 14]),
            ("2011-01-19", "2011-02-09", [6, 0]),
            ("2011-08-08", "2011-08-15", [0, 5]),
        ]
        for first, last, (one, two) in stretches:
            inside = (days >= first) & (days <= last)
            found = result.trace_relations[inside]
            assert [np.count_nonzero(found == 1), np.count_nonzero(found == 2)] == [one, two]
            assert days[inside & (result.trace_relations > 0)][[0, -1]].strftime(
                "%Y-%m-%d"
            ).tolist() == [first, last]
        eigen = days[result.eigen_relations > 0]
        assert len(eigen) == 11
        assert (str(eigen[0].date()), str(eigen[-1].date())) == ("2011-01-19", "2011-02-10")

    def test_the_hedge_held_both_currencies_the_same_way_on_90_days(self, result) -> None:
        """Eighty-five of them fall from 2010-06-01 to 2010-10-05, the longest run 65 days.

        A positive dollar split is a hedge long both legs or short both, so on
        those days the portfolio bet on the US dollar rather than on the spread.
        """
        split = result.dollar_split
        days = result.test_days
        same = split > 0
        assert len(split) == 612
        assert np.count_nonzero(same) == 90
        in_2010 = (days >= "2010-06-01") & (days <= "2010-10-05")
        assert np.count_nonzero(same & in_2010) == 85
        assert (str(days[same][0].date()), str(days[same & in_2010][-1].date())) == (
            "2010-06-01",
            "2010-10-05",
        )
        assert np.count_nonzero(same & ~in_2010) == 5
        # None of the 90 falls in a window the trace test backed.
        assert np.count_nonzero(same & (result.trace_relations > 0)) == 0
        edges = np.diff(np.concatenate(([0], same.astype(int), [0])))
        starts, ends = np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)
        longest = int(np.argmax(ends - starts))
        assert ends[longest] - starts[longest] == 65
        assert (str(days[starts[longest]].date()), str(days[ends[longest] - 1].date())) == (
            "2010-07-07",
            "2010-10-05",
        )

    def test_the_dollar_split_is_the_last_days_positions(self, result) -> None:
        """The last day's share is −0.4325, which is 1 to −0.7622 in dollars."""
        share = result.dollar_split[-1]
        assert share == pytest.approx(-0.4325417813, abs=1e-10)
        assert share / (1 - abs(share)) == pytest.approx(-0.7622442800, abs=1e-10)
        dollars = result.positions[-1]
        assert share == pytest.approx(dollars[1] / np.abs(dollars).sum(), abs=1e-12)

    def test_the_split_ignores_the_eigenvectors_sign(self, result) -> None:
        """The eigenvector's sign moves no return, so it must not move the split either.

        AUD.USD's weight is positive on every test day here, which hides a split
        that skipped holding AUD.USD long, so every other row's hedge is negated.
        """
        flip = np.where(np.arange(len(result.hedge)) % 2, -1.0, 1.0)[:, None]
        flipped = dataclasses.replace(result, hedge=result.hedge * flip)
        np.testing.assert_array_equal(flipped.dollar_split, result.dollar_split)
        assert (flipped.hedge[result.training :, 0] < 0).any()

    def test_the_90_days_compound_to_0_1074_and_the_other_522_to_0_1696(self, result):
        """Together they make the run's 0.2953, so 15 percent of the days carried about two
        fifths of the growth."""
        same = result.dollar_split > 0
        test = result.test
        those, rest = np.prod(1 + test[same]) - 1, np.prod(1 + test[~same]) - 1
        assert those == pytest.approx(0.1073962686, abs=1e-10)
        assert rest == pytest.approx(0.1696463785, abs=1e-10)
        assert (1 + those) * (1 + rest) - 1 == pytest.approx(0.2952620351, abs=1e-10)
        assert np.log1p(those) / np.log1p(0.2952620351) == pytest.approx(0.394, abs=5e-4)

    def test_the_curve_climbed_from_0_0214_to_0_1170_across_the_2010_stretch(self, result):
        """The compounded return on the last day before the first same-way day, and on the
        last day of the 65-day run."""
        curve = pd.Series(np.cumprod(1 + result.test) - 1, index=result.test_days)
        assert str(curve.index[curve.index.get_loc(pd.Timestamp("2010-06-01")) - 1].date()) == (
            "2010-05-31"
        )
        assert curve["2010-05-31"] == pytest.approx(0.0213815186, abs=1e-10)
        assert curve["2010-10-05"] == pytest.approx(0.1170443008, abs=1e-10)

    def test_the_90_days_swung_twice_as_wide_and_a_welch_t_of_1_09_cannot_rule_out_chance(
        self, result
    ):
        """The standard deviations are 0.0073 and 0.0035, and the means differ with p of 0.28."""
        same = result.dollar_split > 0
        test = result.test
        assert test[same].std(ddof=1) == pytest.approx(0.0072797972, abs=1e-10)
        assert test[~same].std(ddof=1) == pytest.approx(0.0034753836, abs=1e-10)
        assert test[same].mean() == pytest.approx(0.0011602616, abs=1e-10)
        assert test[~same].mean() == pytest.approx(0.0003062562, abs=1e-10)
        welch = stats.ttest_ind(test[same], test[~same], equal_var=False)
        assert welch.statistic == pytest.approx(1.0916745496, abs=1e-9)
        assert welch.pvalue == pytest.approx(0.2777053748, abs=1e-9)


class TestTheRule:
    """The five rule cases on series built by hand, and two on the committed files."""

    def test_negating_or_scaling_one_days_hedge_moves_no_return(self) -> None:
        frame = _synthetic()
        found = aud_cad(frame, training=30, lookback=5)
        prices = frame.to_numpy()
        for factor in (-1.0, 3.0, -0.25):
            hedge = found.hedge.copy()
            hedge[45] *= factor
            np.testing.assert_allclose(
                _returns_from(prices, hedge, 30, 5), found.daily, rtol=1e-12, atol=1e-15
            )
            assert not np.allclose(hedge[45], found.hedge[45])

    def test_the_first_test_row_returns_zero_and_nothing_is_held_before_it(self) -> None:
        found = aud_cad(_synthetic(), training=30, lookback=5)
        assert np.isnan(found.positions[:30]).all()
        assert np.isfinite(found.positions[30:]).all()
        assert found.daily[30] == 0
        assert found.daily[31] != 0
        assert (found.daily[:30] == 0).all()

    def test_the_first_committed_test_return_is_zero_as_chans_is(self, result, saved) -> None:
        assert result.test[0] == 0 == saved[0]
        assert np.count_nonzero(result.test) == 611

    def test_the_units_read_day_t_and_the_hedge_stops_the_day_before(self) -> None:
        frame = _synthetic()
        prices = frame.to_numpy()
        found = aud_cad(frame, training=30, lookback=5)
        t = 50
        moved = prices.copy()
        moved[t, 0] *= 1.01
        again = aud_cad(pd.DataFrame(moved, columns=LEGS), training=30, lookback=5)
        np.testing.assert_array_equal(again.hedge[t], found.hedge[t])
        assert again.units[t] != found.units[t]
        assert not np.array_equal(again.hedge[t + 1], found.hedge[t + 1])
        # Row t − 30 is the oldest the hedge reads and row t − 31 is out of it.
        for row, reaches in ((t - 30, True), (t - 31, False)):
            shifted = prices.copy()
            shifted[row, 1] *= 1.01
            other = aud_cad(pd.DataFrame(shifted, columns=LEGS), training=30, lookback=5)
            assert (not np.array_equal(other.hedge[t], found.hedge[t])) is reaches

    def test_ending_both_windows_a_day_earlier_breaks_row_5(self, frame, result, saved):
        """Issue 301 records that the Python port's Example 5.1 does this.

        The shifted run's Sharpe ratio is 1.359568, not the 1.362926 issue 301
        records the port printing, so the port differs in more than this and
        nothing here reproduces its printout.
        """
        prices = frame.to_numpy()
        hedge = np.full(prices.shape, np.nan)
        units = np.full(len(prices), np.nan)
        for t in range(SCRIPT_TRAINING_DAYS + 1, len(prices)):
            hedge[t] = johansen(prices[t - SCRIPT_TRAINING_DAYS - 1 : t - 1], 0, 1).eigenvectors[
                :, 0
            ]
            units[t] = units_on(prices, hedge[t], t - 1, SCRIPT_LOOKBACK)
        shifted = daily_returns(units[:, None] * hedge * prices, prices)[SCRIPT_TRAINING_DAYS:]
        found = agreement(shifted, saved, result.test_days)
        assert not found.holds
        assert found.rows_over == 611
        assert found.first_over == result.test_days[1]
        assert figures(shifted).sharpe == pytest.approx(1.359568, abs=1e-6)

    def test_two_calendars_of_one_length_are_refused_too(self) -> None:
        """Equal lengths are not equal dates, and the script would take AUD.USD's."""
        days = pd.bdate_range("2020-01-01", periods=5)
        aud = pd.Series([0.9, 0.91, 0.92, 0.91, 0.9], index=days)
        cad = pd.Series(
            [1.3, 1.31, 1.32, 1.31, 1.3], index=days[:4].append(days[4:] + pd.Timedelta(days=3))
        )
        with pytest.raises(ValueError, match="1 are AUD.USD's alone and 1 USD.CAD's alone"):
            cross_rates(aud, cad)

    def test_two_series_on_different_dates_are_refused_by_name(self) -> None:
        days = pd.bdate_range("2020-01-01", periods=5)
        aud = pd.Series([0.9, 0.91, 0.92, 0.91, 0.9], index=days)
        cad = pd.Series([1.3, 1.31, 1.32, 1.31], index=days.delete(2))
        with pytest.raises(ValueError, match="same dates.*1 are AUD.USD's alone and 0"):
            cross_rates(aud, cad)

    def test_the_units_are_minus_the_z_score_with_the_n_minus_1_deviation(self) -> None:
        """The deviation's divisor cancels out of every return, so only this sees it."""
        prices = _synthetic(rows=30).to_numpy()
        hedge = np.array([1.0, -0.8])
        value = prices[11:21] @ hedge
        expected = -(value[-1] - value.mean()) / value.std(ddof=1)
        population = -(value[-1] - value.mean()) / value.std(ddof=0)
        assert units_on(prices, hedge, 20, 10) == pytest.approx(expected, rel=1e-12)
        assert units_on(prices, hedge, 20, 10) != pytest.approx(population, rel=1e-6)

    def test_a_missing_price_makes_its_day_zero_as_matlabs_sum_does(self) -> None:
        """``np.nansum`` would skip the missing leg and earn on the other."""
        prices = _synthetic(rows=10).to_numpy(copy=True)
        positions = np.ones_like(prices) * [[1.0, -0.8]]
        prices[6, 1] = np.nan
        daily = daily_returns(positions, prices)
        assert daily[6] == 0
        assert daily[7] == 0
        assert daily[5] != 0 and daily[8] != 0


class TestTheGuardAndTheReads:
    def test_read_sources_runs_the_guard_on_both_legs_over_the_whole_files(
        self, monkeypatch
    ) -> None:
        seen = []

        def record(legs, *, start, end):
            seen.append(([entry.symbol for entry, _ in legs], start, end))

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", record)
        read_sources()
        assert seen == [
            (["AUDUSD", "USDCAD"], pd.Timestamp("2009-01-02"), pd.Timestamp("2012-04-26"))
        ]

    def test_the_guard_passes_the_committed_files(self) -> None:
        """No flagged day sits in either file, so the unpatched read refuses nothing."""
        read_sources()

    def test_a_refusal_from_the_guard_reaches_the_caller(self, monkeypatch) -> None:
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("flagged")

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(WindowCrossesScaleBreak, match="flagged"):
            run()

    def test_main_turns_a_guard_refusal_into_one_line(self, monkeypatch, no_arguments):
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("inputData_AUDUSD_20120426.csv changes scale")

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(SystemExit, match="AUDUSD_20120426.csv changes scale"):
            main()

    def test_run_reads_the_directory_it_is_given(self, tmp_path) -> None:
        with pytest.raises(VintageUnavailable):
            run(tmp_path)

    def test_main_turns_a_missing_vintage_into_one_line(
        self, monkeypatch, tmp_path, no_arguments
    ) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit):
            main()

    def test_a_miss_is_reported_as_one(self) -> None:
        assert module._verdict(0.0, "1.6") == "did not reproduce, gap -1.6"
        assert module._verdict(1.61, "1.6") == "reproduced"

    def test_the_report_marks_every_printed_figure_reproduced(self, capsys, no_arguments):
        main()
        out = capsys.readouterr().out
        verdicts = [line for line in out.splitlines() if line.rstrip().endswith("reproduced")]
        assert len(verdicts) == 5
        assert "did not reproduce" not in out
        assert "rows over           0" in out
        assert "they agree" in out
        assert "trace finds a relation in 26, one in 7 and two in 19" in out
        assert "CADUSD -0.7622" in out
        assert "Exploratory." in out
