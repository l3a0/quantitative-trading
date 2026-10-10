"""What :func:`chan.johansen.johansen` adds to statsmodels' test, held on synthetic series.

Where Chan prints a Johansen figure, the test file of the replication that
reproduces it pins the wrapper's figure, as ``tests/test_etf_cointegration.py``
does for his ETFs. Matching those printouts is what shows the wrapper is
LeSage's ``johansen.m``. This file holds the parts no printout reaches: that a
known cointegrating vector comes back, how the relations are counted, the sign
rule, and each refusal.
"""

from __future__ import annotations

import warnings

import numpy as np
import pytest
from statsmodels.tsa.vector_ar.vecm import coint_johansen

from chan.johansen import LEVELS, Johansen, johansen


def raw(prices: np.ndarray, p: int = 0):
    """statsmodels' own result, with the warning the wrapper exists to remove silenced."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return coint_johansen(prices, p, 1)


@pytest.fixture(scope="module")
def tethered() -> np.ndarray:
    """Two random walks and a third that sits 2 × the first minus the second, plus noise.

    So exactly one combination, (−2, 1, 1) up to scale, is stationary.
    """
    rng = np.random.default_rng(339)
    walks = np.cumsum(rng.normal(size=(2000, 2)), axis=0)
    third = 2 * walks[:, 0] - walks[:, 1] + rng.normal(size=2000)
    return np.column_stack([walks, third])


class TestAKnownSystem:
    def test_it_finds_one_relation_in_a_system_built_with_one(self, tethered) -> None:
        test = johansen(tethered)
        assert test.relations("trace", 95) == 1
        assert test.relations("eigen", 95) == 1

    def test_the_first_eigenvector_is_the_built_combination(self, tethered) -> None:
        vector = johansen(tethered).eigenvectors[:, 0]
        np.testing.assert_allclose(vector / vector[2], [-2.0, 1.0, 1.0], atol=0.01)

    def test_independent_walks_hold_no_relation(self) -> None:
        walks = np.cumsum(np.random.default_rng(1).normal(size=(2000, 3)), axis=0)
        assert johansen(walks).relations("trace", 95) == 0


class TestTheFiguresComeBackReal:
    def test_statsmodels_hands_back_complex_arrays_from_numpy_2_5(self, tethered) -> None:
        """What the wrapper exists to remove, held so a numpy or statsmodels change is noticed.

        numpy 2.4 and earlier return real eigenvalues here, and the wrapper's
        real branch covers that, so the expectation follows the installed numpy.
        """
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            raw = coint_johansen(tethered, 0, 1)
        complex_from = tuple(int(part) for part in np.__version__.split(".")[:2]) >= (2, 5)
        assert np.iscomplexobj(raw.eig) is complex_from
        assert np.iscomplexobj(raw.evec) is complex_from
        warned = any(issubclass(w.category, np.exceptions.ComplexWarning) for w in caught)
        assert warned is complex_from

    def test_the_wrapper_hands_back_reals_without_a_warning(self, tethered) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            test = johansen(tethered)
        for array in (test.eigenvalues, test.eigenvectors, test.trace, test.eigen):
            assert array.dtype == np.float64

    def test_a_complex_eigenvalue_is_refused(self, monkeypatch, tethered) -> None:
        result = raw(tethered)

        class Rotated:
            lr1, lr2, cvt, cvm, evec = result.lr1, result.lr2, result.cvt, result.cvm, result.evec
            eig = result.eig + np.array([0, 1e-3j, -1e-3j])

        monkeypatch.setattr("chan.johansen.coint_johansen", lambda *_: Rotated)
        with pytest.raises(ValueError, match="eigenvalues came back complex"):
            johansen(tethered)

    def test_a_complex_eigenvector_is_refused(self, monkeypatch, tethered) -> None:
        result = raw(tethered)

        class Rotated:
            lr1, lr2, cvt, cvm, eig = result.lr1, result.lr2, result.cvt, result.cvm, result.eig
            evec = result.evec + 1e-3j

        monkeypatch.setattr("chan.johansen.coint_johansen", lambda *_: Rotated)
        with pytest.raises(ValueError, match="eigenvectors came back complex"):
            johansen(tethered)


class TestTheSignRule:
    def test_the_top_left_element_is_always_positive(self, tethered) -> None:
        """statsmodels flips the whole matrix, so negating the input changes nothing."""
        for prices in (tethered, -tethered, tethered[:, ::-1]):
            assert johansen(prices).eigenvectors[0, 0] > 0

    def test_the_wrapper_keeps_statsmodels_signs_rather_than_its_own(self, tethered) -> None:
        """No column is re-signed, so a column whose first element is negative stays so."""
        vectors = johansen(tethered).eigenvectors
        np.testing.assert_array_equal(vectors, raw(tethered).evec.real)


class TestCountingRelations:
    @staticmethod
    def made(trace, eigen) -> Johansen:
        bars = np.array([[10.0, 20.0, 30.0], [1.0, 2.0, 3.0]])
        return Johansen(
            trace=np.array(trace),
            trace_critical=bars,
            eigen=np.array(eigen),
            eigen_critical=bars,
            eigenvalues=np.zeros(2),
            eigenvectors=np.eye(2),
        )

    def test_a_null_rejected_after_one_that_is_not_adds_nothing(self) -> None:
        test = self.made(trace=[15.0, 5.0], eigen=[25.0, 5.0])
        assert [test.relations("trace", level) for level in LEVELS] == [2, 0, 0]
        assert [test.relations("eigen", level) for level in LEVELS] == [2, 2, 0]

    def test_each_statistic_reads_its_own_bars(self) -> None:
        test = Johansen(
            trace=np.array([15.0, 5.0]),
            trace_critical=np.array([[10.0, 20.0, 30.0], [1.0, 2.0, 3.0]]),
            eigen=np.array([15.0, 5.0]),
            eigen_critical=np.array([[12.0, 13.0, 14.0], [1.0, 2.0, 3.0]]),
            eigenvalues=np.zeros(2),
            eigenvectors=np.eye(2),
        )
        assert test.relations("eigen", 95) == 2
        assert test.relations("trace", 95) == 0

    def test_a_statistic_equal_to_its_bar_does_not_reject(self) -> None:
        assert self.made(trace=[20.0, 5.0], eigen=[0.0, 0.0]).relations("trace", 95) == 0

    def test_an_unknown_statistic_or_level_is_refused(self) -> None:
        test = self.made(trace=[0.0, 0.0], eigen=[0.0, 0.0])
        with pytest.raises(ValueError, match="'trace' or 'eigen'"):
            test.relations("max", 95)
        with pytest.raises(ValueError, match=r"one of \(90, 95, 99\), not 97"):
            test.relations("trace", 97)


class TestTheRefusals:
    def test_a_nan_is_refused_by_column_and_row(self, tethered) -> None:
        """statsmodels' own answer is an SVD that did not converge."""
        prices = tethered.copy()
        prices[17, 1] = np.nan
        with pytest.raises(np.linalg.LinAlgError, match="SVD did not converge"):
            coint_johansen(prices, 0, 1)
        with pytest.raises(ValueError, match="column 1 is nan on row 17"):
            johansen(prices)

    def test_the_refusal_names_the_first_bad_row(self, tethered) -> None:
        prices = tethered.copy()
        prices[5, 1] = np.nan
        prices[9, 0] = np.nan
        with pytest.raises(ValueError, match="column 1 is nan on row 5"):
            johansen(prices)

    def test_an_infinity_is_refused_too(self, tethered) -> None:
        prices = tethered.copy()
        prices[3, 0] = np.inf
        with pytest.raises(ValueError, match="column 0 is inf on row 3"):
            johansen(prices)

    def test_a_p_with_no_critical_values_is_refused(self, tethered) -> None:
        """statsmodels warns and hands back NaN bars, which fail every comparison."""
        assert np.isnan(raw(tethered, p=2).cvt).all()
        with pytest.raises(ValueError, match="p is -1, 0 or 1"):
            johansen(tethered, p=2)

    def test_twelve_series_are_accepted(self) -> None:
        walks = np.cumsum(np.random.default_rng(3).normal(size=(400, 12)), axis=0)
        assert johansen(walks).trace.shape == (12,)

    def test_more_than_twelve_series_is_refused(self) -> None:
        walks = np.cumsum(np.random.default_rng(2).normal(size=(400, 13)), axis=0)
        with pytest.raises(ValueError, match="stop at 12 series, and this matrix holds 13"):
            johansen(walks)

    def test_a_single_series_or_a_vector_is_refused(self, tethered) -> None:
        for shape in (tethered[:, :1], tethered[:, 0]):
            with pytest.raises(ValueError, match="at least two series"):
                johansen(shape)

    def test_a_negative_k_is_refused(self, tethered) -> None:
        with pytest.raises(ValueError, match="cannot be -1"):
            johansen(tethered, k=-1)
