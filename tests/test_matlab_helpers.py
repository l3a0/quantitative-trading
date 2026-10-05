"""The cases that separate each of Chan's MATLAB helpers from the numpy default.

Every class here holds at least one input on which a helper and the numpy
default disagree, and asserts the default's answer beside the helper's. So a
helper quietly swapped for the default fails rather than agreeing on easy
inputs. Where a helper moves a figure Chan prints, that figure is pinned in
``tests/test_equity_seasonals.py``, ``tests/test_pead.py``,
``tests/test_pca_factor.py``, ``tests/test_buy_on_gap.py`` or
``tests/test_usdcad_mean_reversion.py``, and the module docstring of
:mod:`chan.matlab_helpers` says which helpers those are.

Book two's plain ``movingAvg`` and ``movingStd`` are held against their
``smart`` namesakes as well as against numpy, because the two pairs differ by
one word and give different answers on a window holding a NaN.

The two books' ``smartstd`` files are held against each other as well as
against numpy, on one input where all three disagree, because swapping one
for the other is the mistake their shared MATLAB name invites.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from chan.matlab_helpers import (
    backshift,
    calculate_max_dd,
    calculate_returns,
    fwdshift,
    lag1,
    matlab_sort,
    moving_avg,
    moving_std,
    round_half_away,
    smart_moving_avg,
    smart_moving_std,
    smartmean,
    smartstd_book_two,
    smartstd_first_edition,
    smartsum,
)

NAN = math.nan


class TestSmartmean:
    def test_it_skips_a_nan_where_the_plain_mean_does_not(self) -> None:
        x = [1.0, NAN, 3.0]
        assert smartmean(x) == 2.0
        assert math.isnan(np.mean(x))

    def test_it_skips_an_infinity_too(self) -> None:
        assert smartmean([1.0, math.inf, 3.0]) == 2.0

    def test_a_column_with_nothing_finite_is_nan(self) -> None:
        assert math.isnan(smartmean([NAN, NAN]))

    def test_it_reduces_down_each_column_by_default(self) -> None:
        x = np.array([[1.0, NAN], [3.0, 4.0]])
        np.testing.assert_array_equal(smartmean(x), [2.0, 4.0])
        np.testing.assert_array_equal(smartmean(x, axis=1), [1.0, 3.5])


class TestSmartsum:
    def test_a_row_with_nothing_finite_is_nan_where_nansum_gives_zero(self) -> None:
        assert math.isnan(smartsum([NAN, NAN]))
        assert np.nansum([NAN, NAN]) == 0.0

    def test_it_skips_a_nan(self) -> None:
        np.testing.assert_array_equal(
            smartsum(np.array([[1.0, NAN], [2.0, NAN]]), axis=1), [1.0, 2.0]
        )


class TestSmartstdFirstEdition:
    def test_it_counts_a_nan_as_zero_where_nanstd_skips_it(self) -> None:
        """``std([1, 0, 3])`` over n - 1, against numpy's 1.0 over the two finite entries."""
        x = [1.0, NAN, 3.0]
        assert smartstd_first_edition(x) == pytest.approx(math.sqrt(7 / 3), abs=1e-15)
        assert np.nanstd(x) == 1.0

    def test_it_divides_by_n_minus_one(self) -> None:
        assert smartstd_first_edition([1.0, 3.0]) == pytest.approx(math.sqrt(2), abs=1e-15)

    def test_a_column_with_nothing_finite_is_nan(self) -> None:
        assert math.isnan(smartstd_first_edition([NAN, NAN, NAN]))

    def test_one_value_has_a_spread_of_zero_as_in_matlab(self) -> None:
        assert smartstd_first_edition([5.0]) == 0.0
        np.testing.assert_array_equal(
            smartstd_first_edition(np.array([[5.0, NAN]]), axis=0), [0.0, NAN]
        )


class TestSmartstdBookTwo:
    def test_it_divides_by_n_where_the_sample_std_divides_by_n_minus_one(self) -> None:
        assert smartstd_book_two([1.0, 3.0]) == 1.0
        assert np.std([1.0, 3.0], ddof=1) == pytest.approx(math.sqrt(2), abs=1e-15)

    def test_it_skips_a_nan_and_an_infinity(self) -> None:
        assert smartstd_book_two([1.0, NAN, 3.0, math.inf]) == 1.0

    def test_a_column_with_nothing_finite_is_nan(self) -> None:
        assert math.isnan(smartstd_book_two([NAN, math.inf]))

    def test_one_finite_value_has_a_spread_of_zero(self) -> None:
        np.testing.assert_array_equal(
            smartstd_book_two(np.array([[5.0, NAN], [NAN, NAN]]), axis=0), [0.0, NAN]
        )

    def test_it_reduces_down_each_column_by_default(self) -> None:
        x = np.array([[1.0, 2.0], [3.0, 2.0]])
        np.testing.assert_array_equal(smartstd_book_two(x), [1.0, 0.0])
        np.testing.assert_array_equal(smartstd_book_two(x, axis=1), [0.5, 0.5])


class TestTheTwoBooksSmartstd:
    def test_one_input_separates_the_two_books_and_numpy(self) -> None:
        """``[1, 2, NaN, 4]`` gives three answers to one question.

        The first edition zero-fills to ``[1, 2, 0, 4]`` and divides 8.75 by 3.
        Book two keeps ``[1, 2, 4]`` and divides 42/9 by 3. numpy's ``nanstd``
        happens to agree with book two, because it also skips and divides by n,
        and its sample form divides by n - 1 over the three finite entries.
        """
        x = [1.0, 2.0, NAN, 4.0]
        assert smartstd_first_edition(x) == pytest.approx(math.sqrt(8.75 / 3), abs=1e-15)
        assert smartstd_book_two(x) == pytest.approx(math.sqrt(14 / 9), abs=1e-15)
        assert np.nanstd(x, ddof=1) == pytest.approx(math.sqrt(7 / 3), abs=1e-15)


class TestSmartMovingStd:
    def test_the_rows_before_the_window_fills_are_nan(self) -> None:
        spread = smart_moving_std(np.arange(5.0)[:, None], 3)
        assert np.isnan(spread[:2]).all()
        assert np.isfinite(spread[2:]).all()

    def test_each_row_is_book_twos_spread_over_the_trailing_window(self) -> None:
        x = np.array([[1.0, 4.0], [3.0, NAN], [NAN, 6.0], [7.0, 6.0]])
        spread = smart_moving_std(x, 2)
        np.testing.assert_array_equal(spread[1], [1.0, 0.0])
        np.testing.assert_array_equal(spread[2], [0.0, 0.0])
        np.testing.assert_array_equal(spread[3], [0.0, 0.0])

    def test_it_takes_book_twos_helper_rather_than_the_first_editions(self) -> None:
        x = np.array([1.0, 2.0, NAN, 4.0])
        assert smart_moving_std(x, 4)[3] == smartstd_book_two(x)
        assert smart_moving_std(x, 4)[3] != smartstd_first_edition(x)

    def test_the_window_trails_rather_than_leads(self) -> None:
        """Row 2 of a window of 2 reads rows 1 and 2, never row 3."""
        spread = smart_moving_std([0.0, 0.0, 0.0, 10.0], 2)
        assert spread[2] == 0.0
        assert spread[3] == 5.0

    def test_a_one_row_window_is_refused(self) -> None:
        with pytest.raises(ValueError, match="at least 2 rows, not 1"):
            smart_moving_std([1.0, 2.0], 1)


class TestSmartMovingAvg:
    def test_the_rows_before_the_window_fills_are_nan_even_when_finite(self) -> None:
        """A rolling mean with no minimum count would give row 0 a mean of itself."""
        avg = smart_moving_avg(np.arange(1.0, 6.0)[:, None], 3)
        assert np.isnan(avg[:2]).all()
        np.testing.assert_array_equal(avg[2:, 0], [2.0, 3.0, 4.0])

    def test_a_missing_entry_is_skipped_rather_than_spoiling_the_window(self) -> None:
        """The plain mean of a window holding a NaN is NaN."""
        x = np.array([[1.0], [NAN], [4.0], [6.0]])
        avg = smart_moving_avg(x, 3)
        assert avg[2, 0] == 2.5
        assert avg[3, 0] == 5.0
        assert np.isnan(np.mean(x[0:3]))

    def test_a_zero_counts_and_an_infinity_does_not(self) -> None:
        """A zero is a value, and an infinity is skipped the way a NaN is."""
        assert smart_moving_avg([[0.0], [2.0]], 2)[1, 0] == 1.0
        assert smart_moving_avg([[math.inf], [2.0]], 2)[1, 0] == 2.0

    def test_a_window_holding_nothing_finite_is_nan(self) -> None:
        x = np.array([[1.0, NAN], [NAN, NAN], [NAN, NAN], [4.0, 5.0]])
        avg = smart_moving_avg(x, 2)
        np.testing.assert_array_equal(avg[1], [1.0, NAN])
        assert np.isnan(avg[2]).all()
        np.testing.assert_array_equal(avg[3], [4.0, 5.0])

    def test_it_adds_the_current_row_first_as_the_m_file_does(self) -> None:
        """Added newest first, 1 is lost against 1e16 before the two large values cancel.

        ``np.mean`` adds oldest first and keeps it, so the two orders give 0 and 1/3.
        """
        x = [-1e16, 1e16, 1.0]
        assert smart_moving_avg(x, 3)[2] == 0.0
        assert np.mean(x) == pytest.approx(1 / 3, abs=1e-15)

    def test_a_window_below_one_row_is_refused(self) -> None:
        with pytest.raises(ValueError, match="at least 1 row, not 0"):
            smart_moving_avg([1.0, 2.0], 0)


class TestMovingAvg:
    def test_the_rows_before_the_window_fills_are_nan(self) -> None:
        avg = moving_avg(np.arange(1.0, 6.0), 3)
        assert np.isnan(avg[:2]).all()
        np.testing.assert_array_equal(avg[2:], [2.0, 3.0, 4.0])

    def test_a_missing_value_spoils_the_window_where_the_smart_one_skips_it(self) -> None:
        x = [1.0, NAN, 4.0, 6.0, 8.0]
        avg = moving_avg(x, 3)
        assert np.isnan(avg[2]) and np.isnan(avg[3])
        assert avg[4] == 6.0
        assert smart_moving_avg(x, 3)[2] == 2.5

    def test_it_adds_the_oldest_row_first_as_the_m_file_does(self) -> None:
        """Added oldest first, 1 is lost against 1e16 before the two large values cancel.

        ``smartMovingAvg`` adds newest first and keeps it, so the two orders give 0 and 1/3.
        """
        x = [1.0, 1e16, -1e16]
        assert moving_avg(x, 3)[2] == 0.0
        assert smart_moving_avg(x, 3)[2] == pytest.approx(1 / 3, abs=1e-15)

    def test_it_averages_down_each_column(self) -> None:
        avg = moving_avg(np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]), 2)
        assert np.isnan(avg[0]).all()
        np.testing.assert_array_equal(avg[1:], [[2.0, 3.0], [4.0, 5.0]])

    def test_a_series_shorter_than_the_window_is_all_nan(self) -> None:
        avg = moving_avg([1.0, 2.0], 3)
        assert avg.shape == (2,) and np.isnan(avg).all()

    def test_a_window_below_one_row_is_refused(self) -> None:
        with pytest.raises(ValueError, match="at least 1 row, not 0"):
            moving_avg([1.0, 2.0], 0)


class TestMovingStd:
    def test_it_divides_by_n_minus_one_where_numpy_divides_by_n(self) -> None:
        sd = moving_std([1.0, 2.0, 4.0, 8.0], 3)
        assert np.isnan(sd[:2]).all()
        assert sd[2] == pytest.approx(math.sqrt(7 / 3), abs=1e-15)
        assert np.std([1.0, 2.0, 4.0]) == pytest.approx(math.sqrt(14 / 9), abs=1e-15)

    def test_it_is_not_book_twos_smart_spread(self) -> None:
        """``smartMovingStd`` divides by n and skips a NaN, and this does neither."""
        x = [1.0, NAN, 4.0, 2.0]
        assert np.isnan(moving_std(x, 3)[2])
        assert smart_moving_std(np.array(x)[:, None], 3)[2, 0] == 1.5
        assert (
            moving_std([1.0, 2.0, 4.0], 3)[2]
            != smart_moving_std(np.array([[1.0], [2.0], [4.0]]), 3)[2, 0]
        )

    def test_the_window_trails_rather_than_leads(self) -> None:
        sd = moving_std([0.0, 0.0, 0.0, 6.0], 2)
        np.testing.assert_array_equal(sd[1:3], [0.0, 0.0])
        assert sd[3] == pytest.approx(math.sqrt(18), abs=1e-12)

    def test_a_one_row_window_is_refused(self) -> None:
        with pytest.raises(ValueError, match="at least 2 rows, not 1"):
            moving_std([1.0, 2.0], 1)


class TestCalculateReturns:
    def test_each_row_is_its_simple_return_and_the_first_lag_rows_are_nan(self) -> None:
        """``np.diff`` would drop the first row rather than keep the shape."""
        r = calculate_returns([100.0, 110.0, 99.0], 1)
        assert np.isnan(r[0])
        assert r[1] == pytest.approx(0.1, abs=1e-15)
        assert r[2] == pytest.approx(-0.1, abs=1e-15)
        assert len(np.diff([100.0, 110.0, 99.0])) == 2

    def test_no_return_reaches_across_a_missing_price(self) -> None:
        """A forward fill would read 100 to 120 as one row's return of 0.2."""
        r = calculate_returns([100.0, NAN, 120.0], 1)
        assert np.isnan(r).all()

    def test_the_lag_counts_rows(self) -> None:
        r = calculate_returns([100.0, 50.0, 150.0], 2)
        assert np.isnan(r[:2]).all()
        assert r[2] == pytest.approx(0.5, abs=1e-15)


class TestCalculateMaxDD:
    def test_the_deepest_drawdown_and_the_longest_stretch_below_a_high(self) -> None:
        """Two days below 0.1 after it, then a new high, then one day below that."""
        cumret = [0.0, 0.1, 0.05, 0.02, 0.12, 0.11]
        max_dd, max_ddd = calculate_max_dd(cumret)
        assert max_dd == pytest.approx(1.02 / 1.1 - 1, abs=1e-15)
        assert max_ddd == 2

    def test_the_high_starts_at_zero_rather_than_at_the_first_day(self) -> None:
        """Starting the high at -0.1 would give a drawdown of 0.8 / 0.9 - 1."""
        max_dd, max_ddd = calculate_max_dd([-0.1, -0.2])
        assert max_dd == pytest.approx(-0.2, abs=1e-15)
        assert max_ddd == 1

    def test_the_first_day_is_never_in_a_drawdown(self) -> None:
        """A loop starting on the first row would give -0.5 and a day below the high."""
        assert calculate_max_dd([-0.5, 0.0]) == (0.0, 0)

    def test_a_day_back_at_the_high_ends_the_stretch(self) -> None:
        assert calculate_max_dd([0.0, 0.1, 0.0, 0.1, 0.0])[1] == 1

    def test_any_drawdown_however_small_counts_as_a_day_below(self) -> None:
        """``drawdown == 0`` is an exact test, so a shortfall of 1e-12 is a day below."""
        assert calculate_max_dd([0.0, 0.1, 0.1 - 1e-12])[1] == 1

    def test_a_nan_day_is_skipped_by_the_minimum_as_matlab_skips_it(self) -> None:
        """numpy's ``min`` would return NaN, where MATLAB's gives the deepest finite day."""
        max_dd, max_ddd = calculate_max_dd([0.0, 0.1, math.nan, 0.05])
        assert max_dd == pytest.approx(1.05 / 1.1 - 1, abs=1e-15)
        assert max_ddd == 2


class TestShifts:
    def test_backshift_moves_rows_later_and_pads_with_nan(self) -> None:
        np.testing.assert_array_equal(backshift(2, [1.0, 2.0, 3.0, 4.0]), [NAN, NAN, 1.0, 2.0])

    def test_lag1_is_a_backshift_of_one(self) -> None:
        x = np.array([[1.0, 2.0], [3.0, 4.0]])
        np.testing.assert_array_equal(lag1(x), [[NAN, NAN], [1.0, 2.0]])

    def test_fwdshift_moves_rows_earlier(self) -> None:
        np.testing.assert_array_equal(fwdshift(1, [1.0, 2.0, 3.0]), [2.0, 3.0, NAN])

    def test_a_shift_of_zero_returns_the_rows_unmoved(self) -> None:
        np.testing.assert_array_equal(backshift(0, [1.0, 2.0]), [1.0, 2.0])
        np.testing.assert_array_equal(fwdshift(0, [1.0, 2.0]), [1.0, 2.0])

    @pytest.mark.parametrize("shift", [backshift, fwdshift])
    def test_a_shift_longer_than_the_rows_is_refused(self, shift) -> None:
        with pytest.raises(ValueError, match="longer than the 3 given"):
            shift(5, [1.0, 2.0, 3.0])

    @pytest.mark.parametrize("shift", [backshift, fwdshift])
    def test_a_negative_shift_is_refused_by_name(self, shift) -> None:
        with pytest.raises(ValueError, match="must be at least 0"):
            shift(-1, [1.0])


class TestMatlabSort:
    def test_nan_sorts_last_and_ties_keep_column_order(self) -> None:
        """Columns 0 and 3 tie at 2, and MATLAB keeps 0 ahead of 3."""
        assert matlab_sort([2.0, NAN, 1.0, 2.0]).tolist() == [2, 0, 3, 1]

    def test_ties_hold_their_order_past_the_size_quicksort_reorders(self) -> None:
        """Sixty equal values, so an unstable sort has room to move them."""
        x = np.r_[np.full(60, 5.0), 1.0]
        assert matlab_sort(x).tolist() == [60, *range(60)]


class TestRoundHalfAway:
    @pytest.mark.parametrize(
        ("value", "matlab", "numpy"),
        [
            (0.5, 1.0, 0.0),
            (2.5, 3.0, 2.0),
            (57.8, 58.0, 58.0),
            (-2.5, -3.0, -2.0),
            (0.49999999999999994, 0.0, 0.0),
            (2.0**52 + 1, 2.0**52 + 1, 2.0**52 + 1),
        ],
    )
    def test_a_half_goes_away_from_zero_where_numpy_goes_to_even(
        self, value: float, matlab: float, numpy: float
    ) -> None:
        assert round_half_away(value) == matlab
        assert np.round(value) == numpy
