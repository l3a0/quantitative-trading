"""The cases that separate each of Chan's MATLAB helpers from the numpy default.

Each helper in :mod:`chan.matlab_helpers` exists because the default it
replaces moves a printed figure. So every class here holds at least one input
on which the two disagree, and asserts the default's answer beside the
helper's, so a helper quietly swapped for the default fails rather than
agreeing on easy inputs. The figure each one moves is pinned in
``tests/test_equity_seasonals.py``.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from chan.matlab_helpers import (
    backshift,
    fwdshift,
    lag1,
    matlab_sort,
    round_half_away,
    smartmean,
    smartstd,
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


class TestSmartstd:
    def test_it_counts_a_nan_as_zero_where_nanstd_skips_it(self) -> None:
        """``std([1, 0, 3])`` over n - 1, against numpy's 1.0 over the two finite entries."""
        x = [1.0, NAN, 3.0]
        assert smartstd(x) == pytest.approx(math.sqrt(7 / 3), abs=1e-15)
        assert np.nanstd(x) == 1.0

    def test_it_divides_by_n_minus_one(self) -> None:
        assert smartstd([1.0, 3.0]) == pytest.approx(math.sqrt(2), abs=1e-15)

    def test_a_column_with_nothing_finite_is_nan(self) -> None:
        assert math.isnan(smartstd([NAN, NAN, NAN]))


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
        [(0.5, 1.0, 0.0), (2.5, 3.0, 2.0), (57.8, 58.0, 58.0), (-2.5, -3.0, -2.0)],
    )
    def test_a_half_goes_away_from_zero_where_numpy_goes_to_even(
        self, value: float, matlab: float, numpy: float
    ) -> None:
        assert round_half_away(value) == matlab
        assert np.round(value) == numpy
