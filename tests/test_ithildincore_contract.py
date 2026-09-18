"""What this repo requires of the estimators it does not own.

The estimators come from [ithildincore](https://github.com/l3a0/ithildin-core), so a
number here can move for two different reasons: the vintage changed, or the
dependency changed. `tests/test_pair_cointegration.py` fails on either and
cannot say which, because every one of its assertions reads a committed CSV.

These cases read no vintage. Their answers are known in closed form, so they
fail only when the estimator's behaviour moves. A run where these pass and the
pair tests fail points at the data. A run where these fail points at the pin
in `pyproject.toml`.

That is the whole job. These are not a second copy of ithildincore's own tests,
which are broader and live where the code does. This file holds the three
properties this repo's replications actually rest on, and it is the reason the
package is pinned to a tag rather than a range.
"""

from __future__ import annotations

import math

import numpy as np
import pytest
from ithildincore.timeseries import ADF_CRIT_CONST, EG_CRIT_N2, adf_tstat, ols, ou_half_life


class TestTheEstimatorsStillBehaveAsTheReplicationsAssume:
    def test_least_squares_recovers_a_line_it_was_given(self) -> None:
        """No implicit intercept. The design carries the ones column or it does not."""
        x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
        fit = ols(2.0 * x + 1.0, np.column_stack([x, np.ones(5)]))
        assert fit.beta[0] == pytest.approx(2.0, abs=1e-9)
        assert fit.beta[1] == pytest.approx(1.0, abs=1e-9)

    def test_least_squares_without_a_ones_column_fits_through_the_origin(self) -> None:
        """The two GLD/GDX hedge specifications differ by exactly this column."""
        x = np.array([1.0, 2.0, 3.0, 4.0])
        through_origin = ols(2.0 * x + 5.0, x.reshape(-1, 1))
        assert through_origin.beta.shape == (1,)
        assert through_origin.beta[0] != pytest.approx(2.0, abs=1e-3)

    def test_the_half_life_of_a_known_decay(self) -> None:
        """A z_{t+1} = 0.5 z_t decay has slope -0.5, so the half-life is ln(2)/0.5."""
        z = 0.5 ** np.arange(200, dtype=float)
        assert ou_half_life(z) == pytest.approx(math.log(2.0) / 0.5, abs=1e-4)

    def test_the_lag_stays_where_it_was_asked_to_stay(self) -> None:
        """The pinned verdicts assume a fixed lag of one, not a lag read off the data."""
        rng = np.random.default_rng(1)
        walk = np.cumsum(rng.standard_normal(2000))
        assert adf_tstat(walk, lags=1, constant=True)[1] == 1998
        assert adf_tstat(walk, lags=6, constant=True)[1] == 1993

    def test_the_critical_values_are_the_ones_the_verdicts_were_read_against(self) -> None:
        """docs/replication-log.md reads its verdicts against these exact numbers."""
        assert ADF_CRIT_CONST == {"1%": -3.43, "5%": -2.86, "10%": -2.57}
        assert EG_CRIT_N2 == {"1%": -3.90, "5%": -3.34, "10%": -3.04}
