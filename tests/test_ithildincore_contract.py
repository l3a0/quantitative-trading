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
which are broader and live where the code does. This file holds the properties
this repo's replications actually rest on, and it is the reason the package is
pinned to a commit rather than a range.

Two estimators are read here and they answer different questions. The
`timeseries` cases below hold what the pair replication rests on. The `stats`
cases hold `newey_west_summary`, which `src/chan/risk_parity.py` pins a Sharpe
ranking on, and they arrived with it: that replication reports a measured
difference and a robust t rather than a boolean, so a t-statistic that moved
inside the dependency would re-pin a verdict with nothing in this repo's diff
to explain it.
"""

from __future__ import annotations

import math

import numpy as np
import pytest
from ithildincore.stats import newey_west_lag, newey_west_summary
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


class TestTheSignificanceBlockTheRankingRestsOn:
    """`newey_west_summary`, held to answers worked out by hand rather than run.

    Four values on four points are enough to pin the whole estimator, because
    every part of it is exercised: the sample variance, the Bartlett weight,
    the lag rule and the sign of the correction. Both four-point series below
    have a mean of 2 and a sample variance of 4/3, so the naive t-statistic is
    identical on the two and only the autocorrelation separates them.
    """

    def test_a_negatively_autocorrelated_series_raises_the_robust_t(self) -> None:
        """[1, 3, 1, 3] has lag-1 autocovariance -1, which shrinks the standard error.

        By hand: the lag rule gives L = 1 and the Bartlett weight is
        1 - 1/2 = 1/2, so Var(mean) = (4/3 + 2 * (1/2) * (-1)) / 4 = 1/12 and
        the robust t is 2 / sqrt(1/12) = 4 * sqrt(3). The naive one is
        2 / sqrt((4/3) / 4) = 2 * sqrt(3), exactly half of it.
        """
        summary = newey_west_summary([1.0, 3.0, 1.0, 3.0])
        assert summary.n == 4
        assert summary.lag == 1
        assert summary.mean == pytest.approx(2.0, abs=1e-12)
        assert summary.var == pytest.approx(4.0 / 3.0, abs=1e-12)
        assert summary.t_naive == pytest.approx(2.0 * math.sqrt(3.0), abs=1e-12)
        assert summary.t_newey_west == pytest.approx(4.0 * math.sqrt(3.0), abs=1e-12)

    def test_a_positively_autocorrelated_series_lowers_the_robust_t(self) -> None:
        """[1, 1, 3, 3] has lag-1 autocovariance +1/3, which is the case that matters.

        By hand: Var(mean) = (4/3 + 2 * (1/2) * (1/3)) / 4 = 5/12, so the
        robust t is 2 / sqrt(5/12). Daily portfolio returns carry positive
        autocorrelation, so this is the direction that keeps a ranking from
        reading as significant when the sample does not support it. The naive
        t is unchanged from the case above, which is the whole point of
        reporting both.
        """
        summary = newey_west_summary([1.0, 1.0, 3.0, 3.0])
        assert summary.t_naive == pytest.approx(2.0 * math.sqrt(3.0), abs=1e-12)
        assert summary.t_newey_west == pytest.approx(2.0 / math.sqrt(5.0 / 12.0), abs=1e-12)
        assert summary.t_newey_west < summary.t_naive

    def test_the_lag_rule_steps_where_it_has_always_stepped(self) -> None:
        """``L = int(4 * (n / 100) ** (2 / 9))``, held at its own boundaries.

        A pin in the middle of a plateau holds almost nothing: this rule
        returns 9 for every sample from 3,845 to 6,176, so three sizes drawn
        from one replication's windows would survive a formula that moved by a
        long way. The boundaries are where the rule is actually decidable, and
        they are properties of the dependency with no vintage in them, which is
        what this file is for. Each pair is the last sample at one lag and the
        first at the next.
        """
        for last, first in ((99, 100), (272, 273), (620, 621), (1240, 1241), (3844, 3845)):
            assert newey_west_lag(first) == newey_west_lag(last) + 1
        assert [newey_west_lag(n) for n in (99, 100, 620, 621, 3844, 3845)] == [3, 4, 5, 6, 8, 9]

    def test_a_sample_too_short_to_carry_a_variance_returns_zeros(self) -> None:
        """The guard `chan.risk_parity` relies on rather than checking for itself.

        A one-element sample has no sample variance, and the summary reports
        zeros rather than raising. `measure_window` refuses a window under 30
        trading days long before this could fire, so what this case holds is
        that the refusal is the only path to a short window and not a race with
        an exception from inside the dependency.
        """
        assert newey_west_summary([7.0]) == (1, 7.0, 0.0, 0.0, 0.0, 0)
        assert newey_west_summary([]) == (0, 0.0, 0.0, 0.0, 0.0, 0)
