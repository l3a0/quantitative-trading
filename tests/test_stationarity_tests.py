"""The rules of the three toolbox tests in :mod:`chan.stationarity_tests`, on synthetic series.

What vouches for ``adf`` and ``vratiotest`` against Chan's own output is
``tests/test_usdcad_mean_reversion.py``, where each lands the digits
``stationarityTests.m`` printed. ``genhurst`` lands none of the book's figures,
0.49 on USD.CAD and 0.44 on TU, so no figure of Chan's vouches for it.
``TestGenhurst`` here holds its rules. That file and
``tests/test_tu_momentum.py`` pin its output on USD.CAD and TU, which catches a
change but does not show it is right.
This file holds what those digits cannot separate: the row jplv7's ``adf``
drops against ``adfuller``, the bins of ``ztcrit``, ``genhurst``'s invariances,
and the period trim and closed forms of ``vratiotest``. Each class asserts the
nearby wrong answer beside the right one, so a transcription swapped for the
obvious library call fails here rather than agreeing on easy inputs.
"""

from __future__ import annotations

import math
import warnings

import numpy as np
import pytest
from statsmodels.tsa.stattools import adfuller

from chan.stationarity_tests import (
    ZTCRIT_CONSTANT,
    genhurst,
    jplv7_adf,
    vratiotest,
    ztcrit,
)


def _walk(n: int, seed: int) -> np.ndarray:
    return np.cumsum(np.random.default_rng(seed).standard_normal(n)) + 100.0


def _ar1(n: int, phi: float, seed: int) -> np.ndarray:
    shocks = np.random.default_rng(seed).standard_normal(n)
    out = np.empty(n)
    out[0] = 0.0
    for t in range(1, n):
        out[t] = phi * out[t - 1] + shocks[t]
    return out + 100.0


def _adfuller(x: np.ndarray, lags: int) -> tuple[float, int, float]:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        r = adfuller(x, maxlag=lags, regression="c", autolag=None, regresults=True)
    return float(r[0]), int(r[3].nobs), float(r[3].resols.params[0]) + 1


class TestJplv7Adf:
    @pytest.mark.parametrize("lags", [1, 2, 3])
    def test_it_is_adfuller_on_the_series_less_its_first_row(self, lags: int) -> None:
        """jplv7 trims the lagged level once more than ``adfuller`` does, and nothing else."""
        x = _walk(400, seed=lags)
        ours = jplv7_adf(x, 0, lags)
        theirs, nobs, ar1 = _adfuller(x[1:], lags)
        assert ours.statistic == pytest.approx(theirs, abs=1e-9)
        assert ours.ar1 == pytest.approx(ar1, abs=1e-12)
        assert ours.nobs == nobs == len(x) - lags - 2

    def test_the_whole_series_gives_adfullers_other_answer(self) -> None:
        x = _walk(400, seed=7)
        whole, nobs, _ = _adfuller(x, 1)
        assert nobs == jplv7_adf(x).nobs + 1
        assert abs(jplv7_adf(x).statistic - whole) > 1e-4

    def test_the_statistic_is_the_ar1_estimate_less_one_over_its_error(self) -> None:
        """A stationary series has an AR(1) estimate well below 1 and a very negative statistic."""
        reverting = jplv7_adf(_ar1(500, 0.5, seed=3))
        assert reverting.ar1 < 0.7
        assert reverting.statistic < reverting.critical[0]
        walking = jplv7_adf(_walk(500, seed=3))
        assert walking.ar1 > 0.95
        assert walking.statistic > walking.critical[2]

    def test_the_critical_values_are_ztcrits_for_the_whole_series(self) -> None:
        """``ztcrit`` reads ``rows(x)``, the series' length, not the rows the regression fit."""
        assert jplv7_adf(_walk(424, seed=1)).critical == ZTCRIT_CONSTANT[8]
        assert jplv7_adf(_walk(425, seed=1)).critical == ZTCRIT_CONSTANT[9]

    def test_another_trend_order_is_refused_by_name(self) -> None:
        with pytest.raises(ValueError, match="only trend order 0.*not 1"):
            jplv7_adf(_walk(100, seed=1), 1, 1)

    def test_zero_lags_is_refused_as_adf_m_refuses_it(self) -> None:
        with pytest.raises(ValueError, match="at least 1 lag, not 0"):
            jplv7_adf(_walk(100, seed=1), 0, 0)

    def test_a_missing_value_is_refused(self) -> None:
        x = _walk(100, seed=1)
        x[50] = math.nan
        with pytest.raises(ValueError, match="no missing value"):
            jplv7_adf(x)

    @pytest.mark.parametrize("lags", [13, 14, 16])
    def test_a_fit_with_no_more_rows_than_regressors_is_refused(self, lags: int) -> None:
        """30 points at 13 lags fit 15 rows on 15 regressors, which ``adf.m``'s own guard passes."""
        assert 30 - 2 * 13 + 1 >= 1
        with pytest.raises(ValueError, match="no degrees of freedom"):
            jplv7_adf(_walk(30, seed=1), 0, lags)

    def test_the_most_lags_that_leave_a_degree_of_freedom_run(self) -> None:
        """30 points at 12 lags fit 16 rows on 14 regressors."""
        assert jplv7_adf(_walk(30, seed=1), 0, 12).nobs == 16


class TestZtcrit:
    @pytest.mark.parametrize(
        ("nobs", "row"),
        [(25, 1), (49, 1), (50, 2), (74, 2), (75, 3), (124, 3), (125, 4), (424, 9), (425, 10)],
    )
    def test_the_bin_is_round_nobs_over_50_plus_1(self, nobs: int, row: int) -> None:
        assert ztcrit(nobs) == ZTCRIT_CONSTANT[row - 1]

    def test_a_half_rounds_away_from_zero_where_numpy_rounds_to_even(self) -> None:
        """125 / 50 is 2.5. MATLAB's round gives bin 4, numpy's would give bin 3."""
        assert round(125 / 50) + 1 == 3
        assert ztcrit(125) == ZTCRIT_CONSTANT[3]

    def test_the_rows_are_ztcrits_constant_rows_as_typed_from_it(self) -> None:
        """Rows 2, 9, 16, ... 65 of ``ztcrit.m``'s table, retyped so a slip in either copy fails."""
        assert ZTCRIT_CONSTANT == (
            (-3.63993, -2.94935, -2.61560),
            (-3.56634, -2.93701, -2.61518),
            (-3.43911, -2.91515, -2.58414),
            (-3.46419, -2.91242, -2.58837),
            (-3.49260, -2.87595, -2.56885),
            (-3.44558, -2.84182, -2.57313),
            (-3.44036, -2.86974, -2.58294),
            (-3.42692, -2.86280, -2.57220),
            (-3.38577, -2.86443, -2.57318),
            (-3.45830, -2.87104, -2.59369),
        )

    def test_every_long_series_reads_the_last_row(self) -> None:
        assert ztcrit(1216) == ztcrit(100_000) == (-3.45830, -2.87104, -2.59369)

    def test_the_rows_are_ordered_one_five_ten_percent(self) -> None:
        for one, five, ten in ZTCRIT_CONSTANT:
            assert one < five < ten < 0

    def test_a_series_too_short_for_any_bin_is_refused(self) -> None:
        with pytest.raises(ValueError, match="no bin for 24 observations"):
            ztcrit(24)


class TestGenhurst:
    def test_a_random_walk_is_near_a_half(self) -> None:
        assert genhurst(_walk(5000, seed=11), 2) == pytest.approx(0.5, abs=0.03)

    def test_a_reverting_series_is_well_below_a_walk_on_the_same_shocks(self) -> None:
        reverting = genhurst(_ar1(5000, 0.8, seed=11), 2)
        walking = genhurst(_ar1(5000, 1.0, seed=11), 2)
        assert reverting < 0.4 < walking

    def test_it_ignores_the_level_and_the_scale(self) -> None:
        """The changes and the levels are both detrended, and the moments are a ratio.

        Leaving the intercept on the levels would break the first, and
        dividing one moment by a different power the second.
        """
        s = _walk(800, seed=5)
        h = genhurst(s, 2)
        assert genhurst(s + 1000.0, 2) == pytest.approx(h, abs=1e-9)
        assert genhurst(7.0 * s, 2) == pytest.approx(h, abs=1e-12)

    def test_q_divides_the_mean_slope(self) -> None:
        """H(q) estimates qH and divides by q, so q = 1 and q = 2 agree on a walk only roughly."""
        s = _walk(5000, seed=13)
        assert genhurst(s, 1) == pytest.approx(genhurst(s, 2), abs=0.05)
        assert genhurst(s, 1) != genhurst(s, 2)

    def test_the_window_lengths_matter(self) -> None:
        s = _walk(800, seed=5)
        assert genhurst(s, 2, max_t=10) != genhurst(s, 2)

    def test_a_matrix_is_refused(self) -> None:
        with pytest.raises(ValueError, match="one series"):
            genhurst(np.ones((10, 2)))


class TestVratiotest:
    def test_the_returns_are_trimmed_to_a_whole_number_of_periods(self) -> None:
        """With an odd count of returns at period 2, the last one is never read."""
        y_odd = _walk(202, seed=2)
        moved = y_odd.copy()
        moved[-1] += 50.0
        assert vratiotest(moved) == vratiotest(y_odd)
        assert vratiotest(y_odd).nobs == 200

    def test_the_iid_variance_is_its_closed_form(self) -> None:
        y = _walk(301, seed=4)
        r = vratiotest(y, iid=True)
        expected = math.sqrt(300) * (r.ratio - 1) / math.sqrt(2 * 3 * 1 / 6)
        assert r.statistic == pytest.approx(expected, abs=1e-12)

    def test_the_robust_variance_differs_from_the_iid_one_under_changing_volatility(self) -> None:
        rng = np.random.default_rng(9)
        scale = np.where(np.arange(600) < 300, 0.2, 3.0)
        y = np.cumsum(rng.standard_normal(600) * scale)
        robust, iid = vratiotest(y), vratiotest(y, iid=True)
        assert robust.ratio == iid.ratio
        assert abs(robust.statistic) < abs(iid.statistic)

    def test_an_alternating_series_rejects_with_a_ratio_below_one(self) -> None:
        y = np.cumsum(np.tile([1.0, -1.0], 200) + np.random.default_rng(1).normal(0, 0.1, 400))
        r = vratiotest(y)
        assert r.ratio < 0.5
        assert r.rejects and r.p_value < 1e-6

    def test_the_p_value_is_two_sided(self) -> None:
        y = _walk(500, seed=8)
        r = vratiotest(y)
        assert r.p_value == pytest.approx(math.erfc(abs(r.statistic) / math.sqrt(2)), abs=1e-14)
        assert r.rejects == (r.p_value <= 0.05)

    def test_a_missing_value_is_refused_rather_than_deleted(self) -> None:
        y = _walk(100, seed=1)
        y[10] = math.nan
        with pytest.raises(ValueError, match="no missing value"):
            vratiotest(y)

    def test_a_series_shorter_than_twice_the_period_is_refused(self) -> None:
        with pytest.raises(ValueError, match="more than twice the period"):
            vratiotest([1.0, 2.0, 3.0, 4.0], period=2)

    def test_a_period_below_two_is_refused(self) -> None:
        with pytest.raises(ValueError, match="at least 2, not 1"):
            vratiotest(_walk(50, seed=1), period=1)
