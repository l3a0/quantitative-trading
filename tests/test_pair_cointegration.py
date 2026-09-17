"""The pins for the GLD/GDX and KO/PEP replications.

This file is the single authority for every number the prose quotes about
these two pairs. A doc that recomputed one of them would be a second
implementation of the calculation, and the two would drift without either
looking wrong.

There is no dataset gate. All four vintages are committed to git, so every
layer runs everywhere the suite runs. The primitives underneath have their own
mechanics tests in ``tests/test_timeseries.py``; this file tests the
pair-specific two-step ``engle_granger``, the return correlation, and the
replications themselves.

1. ``TestEngleGranger``, the two-step test on synthetic pairs with known
   answers, plus the module's own ``selftest``.
2. ``TestGldGdxReproduction``, the reproduced GLD/GDX numbers, each pinned
   against its own window and its own regression specification. This is what
   freezes the yfinance vintage: a re-download that shifts the adjusted-close
   basis moves these numbers and fails CI rather than passing quietly.
3. ``TestRollingRegime``, the rolling-window scan that makes "cointegration is
   a property of the window" checkable.
4. ``TestKoPepNonCointegration``, Chan's counter-example: correlated in returns
   yet not cointegrated in levels. It runs on Chan's OWN committed companion
   data, so it reproduces his printed figures to the digit.
5. ``TestGldGdxChanArchive``, Chan's own committed GLD/GDX files. They give
   1.6395 and -3.52, NOT his printed 1.6766, which is the receipt for the lost
   vintage. The verdict survives; only the hedge drifted.

1.6766 is a cited book target throughout, never asserted as a computed result,
because no surviving file reproduces it.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from chan.pair_cointegration import (
    BOOK_END,
    BOOK_START,
    BOOK_TRAIN_END,
    CointResult,
    RollingCoint,
    aligned_closes,
    engle_granger,
    return_correlation,
    rolling_cointegration,
    selftest,
)
from chan.timeseries import EG_CRIT_N2

# ============================================================
# Layer 1 -- the two-step test on synthetic pairs (engle_granger)
# ============================================================


class TestEngleGranger:
    """The pair-specific two-step test on synthetic pairs with known answers.

    The underlying OLS / ADF / OU primitives are tested in
    tests/test_timeseries.py. Here the assertions are the verdict
    ``engle_granger`` reaches.
    """

    def test_cointegrated_pair_detected(self) -> None:
        """A shared-factor pair rejects the no-cointegration null with a short
        half-life."""
        rng = np.random.default_rng(3)
        factor = np.cumsum(rng.standard_normal(2000))
        a = factor + rng.standard_normal(2000) * 0.5
        b = 0.5 * factor + rng.standard_normal(2000) * 0.5
        res = engle_granger(a, b, lags=1)
        assert res.adf_stat < EG_CRIT_N2["1%"]
        assert 0 < res.half_life < 50

    def test_independent_walks_not_cointegrated(self) -> None:
        """Two unrelated random walks fail to reject, so no spurious pair."""
        rng = np.random.default_rng(4)
        a = np.cumsum(rng.standard_normal(2000))
        b = np.cumsum(rng.standard_normal(2000))
        res = engle_granger(a, b, lags=1)
        assert res.adf_stat > EG_CRIT_N2["10%"]

    def test_selftest_runs_clean(self) -> None:
        """The module's own selftest, all four synthetic checks, must not raise."""
        selftest()


# ============================================================
# Layer 2 -- the pinned GLD/GDX replication (committed vintages)
# ============================================================


class TestGldGdxReproduction:
    """Freeze the reproduced Chan GLD/GDX numbers.

    Vintage: GLD and GDX from yfinance, downloaded 2026-08-27, raw as-traded
    close for the two book windows and Yahoo's dividend-adjusted close for the
    full-history run. Values are pinned at the 4-decimal CLI precision, rounded
    from the true value. Chan's printed 1.6766 is not asserted, because it is a
    book target the replication cannot hit from any modern download.
    """

    @staticmethod
    @pytest.fixture(scope="class")
    def ch7() -> CointResult:
        """Chapter 7: the full 2006-05-23 .. 2007-11-30 window, raw closes."""
        df = aligned_closes("GLD", "GDX", start=BOOK_START, end=BOOK_END, unadjusted=True)
        a = df["GLD"].to_numpy(dtype=float)
        b = df["GDX"].to_numpy(dtype=float)
        return engle_granger(a, b, lags=1, origin=True)

    @staticmethod
    @pytest.fixture(scope="class")
    def ch3() -> CointResult:
        """Chapter 3, page 63: the first ~252-day training set, raw closes."""
        df = aligned_closes("GLD", "GDX", start=BOOK_START, end=BOOK_TRAIN_END, unadjusted=True)
        a = df["GLD"].to_numpy(dtype=float)
        b = df["GDX"].to_numpy(dtype=float)
        return engle_granger(a, b, lags=1, origin=True)

    @staticmethod
    @pytest.fixture(scope="class")
    def full_span() -> CointResult:
        """The whole dividend-adjusted history, where the relationship has gone."""
        df = aligned_closes("GLD", "GDX")
        a = df["GLD"].to_numpy(dtype=float)
        b = df["GDX"].to_numpy(dtype=float)
        return engle_granger(a, b, lags=1)

    def test_ch7_hedge_and_stat(self, ch7: CointResult) -> None:
        """Chapter 7 window, raw closes. The through-origin slope is Chan's
        1.6766 specification and the with-intercept slope is the test's own, so
        a later re-pin can say which of the two moved."""
        assert ch7.nobs == 383
        assert ch7.origin_hedge == pytest.approx(1.6379, abs=5e-4)
        assert ch7.hedge_ratio == pytest.approx(1.3905, abs=5e-4)
        assert ch7.adf_stat == pytest.approx(-3.45, abs=1e-2)
        assert ch7.half_life == pytest.approx(10.6, abs=0.1)
        # Rejects the no-cointegration null at the 5% level on this window.
        assert ch7.adf_stat < EG_CRIT_N2["5%"]

    def test_ch3_hedge_and_stat(self, ch3: CointResult) -> None:
        """Chapter 3 training set, raw closes, same two specifications."""
        assert ch3.nobs == 250
        assert ch3.origin_hedge == pytest.approx(1.6283, abs=5e-4)
        assert ch3.hedge_ratio == pytest.approx(1.1911, abs=5e-4)
        assert ch3.adf_stat == pytest.approx(-3.09, abs=1e-2)
        # Rejects at the 10% level on the shorter training set.
        assert ch3.adf_stat < EG_CRIT_N2["10%"]

    def test_full_span_fails_to_reject(self, full_span: CointResult) -> None:
        """Over the full history the pair no longer looks cointegrated. The
        relationship the book documented had a shelf life."""
        assert full_span.nobs == 5028
        assert full_span.adf_stat == pytest.approx(-1.45, abs=1e-2)
        assert full_span.adf_stat > EG_CRIT_N2["10%"]


# ============================================================
# Layer 3 -- the rolling-window regime scan
# ============================================================


class TestRollingRegime:
    """Freeze the rolling-window scan over the full as-traded history.

    A one-year window, 252 trading days, stepped monthly by 21 days, with
    ``origin=True`` so Chan's through-origin hedge rides along. A re-download
    that shifts the vintage moves these pins.
    """

    @staticmethod
    @pytest.fixture(scope="class")
    def scan() -> tuple[RollingCoint, pd.DatetimeIndex]:
        df = aligned_closes("GLD", "GDX", unadjusted=True)
        a = df["GLD"].to_numpy(dtype=float)
        b = df["GDX"].to_numpy(dtype=float)
        return rolling_cointegration(a, b, window=252, step=21, lags=1), df.index

    def test_cointegration_is_episodic(self, scan: tuple[RollingCoint, pd.DatetimeIndex]) -> None:
        """Only about one window in eight clears even the 10% bar."""
        roll, _ = scan
        adf = roll.adf_stat
        assert len(adf) == 231
        assert int((adf < EG_CRIT_N2["10%"]).sum()) == 31
        assert int((adf < EG_CRIT_N2["5%"]).sum()) == 14

    def test_first_window_reproduces_chans_era(
        self, scan: tuple[RollingCoint, pd.DatetimeIndex]
    ) -> None:
        """The first rolling window is close to Chan's Ch.3 training set. It
        rejects, with a through-origin hedge near his 1.64."""
        roll, _ = scan
        assert roll.adf_stat[0] == pytest.approx(-3.18, abs=1e-2)
        assert roll.origin_hedge[0] == pytest.approx(1.6286, abs=5e-4)
        assert roll.adf_stat[0] < EG_CRIT_N2["10%"]

    def test_hedge_drifts_far_past_the_book(
        self, scan: tuple[RollingCoint, pd.DatetimeIndex]
    ) -> None:
        """Chan's hedge does not hold: the through-origin ratio peaks past 6,
        so there was never one ratio a fixed pair trade could have held."""
        roll, _ = scan
        assert roll.origin_hedge.max() == pytest.approx(6.6152, abs=5e-4)

    def test_cointegration_fades_after_the_early_years(
        self, scan: tuple[RollingCoint, pd.DatetimeIndex]
    ) -> None:
        """The early cluster is the whole story. In the decade from 2015 only
        10 of 139 windows reject."""
        roll, idx = scan
        years = idx[roll.end_idx].year.to_numpy()
        post = years >= 2015
        assert int(post.sum()) == 139
        assert int((roll.adf_stat[post] < EG_CRIT_N2["10%"]).sum()) == 10


# ============================================================
# Layer 4 -- Chan's KO/PEP counter-example (his committed data)
# ============================================================


class TestKoPepNonCointegration:
    """Freeze Chan's KO/PEP counter-example, Example 7.3.

    The pair is significantly correlated in daily returns yet does not
    cointegrate, which is the demonstration that correlation and cointegration
    are different things.

    Vintage: the adjusted-close columns of Chan's own KO.xls and PEP.xls, last
    saved 2008-01-23, committed as data/ko_chan.csv and data/pep_chan.csv.
    Running his exact companion data is why this one reproduces his printed
    figures to the digit, which is the counterpoint to the lost 1.6766.
    """

    @staticmethod
    @pytest.fixture(scope="class")
    def kopep() -> CointResult:
        """Full KO/PEP intersection, adjusted close, Chan's example7_3.m run."""
        df = aligned_closes("KO", "PEP", chan=True)
        a = df["KO"].to_numpy(dtype=float)
        b = df["PEP"].to_numpy(dtype=float)
        return engle_granger(a, b, lags=1, origin=True)

    @staticmethod
    @pytest.fixture(scope="class")
    def corr() -> tuple[float, float, float]:
        df = aligned_closes("KO", "PEP", chan=True)
        a = df["KO"].to_numpy(dtype=float)
        b = df["PEP"].to_numpy(dtype=float)
        return return_correlation(a, b)

    def test_hedge_matches_chan_exactly(self, kopep: CointResult) -> None:
        """Chan's through-origin hedge 1.0114 reproduces to the digit, on his
        .xls data rather than a modern download. The with-intercept hedge from
        the test's own specification is 0.9209."""
        assert kopep.nobs == 7833
        assert kopep.origin_hedge == pytest.approx(1.0114, abs=5e-4)
        assert kopep.hedge_ratio == pytest.approx(0.9209, abs=5e-4)

    def test_fails_to_cointegrate(self, kopep: CointResult) -> None:
        """CADF t = -2.14, against Chan's -2.14258438, well above the 10%
        critical value, so the pair fails to reject the no-cointegration null.
        The OU half-life past 600 days confirms the spread barely reverts."""
        assert kopep.adf_stat == pytest.approx(-2.14, abs=1e-2)
        assert kopep.adf_stat > EG_CRIT_N2["10%"]
        assert kopep.half_life > 100

    def test_returns_are_correlated(self, corr: tuple[float, float, float]) -> None:
        """The other half of the counter-example. Daily returns ARE
        significantly correlated, at Chan's r = 0.4849, even though the prices
        do not cointegrate."""
        r, _t, p = corr
        assert r == pytest.approx(0.4849, abs=5e-4)
        assert p < 0.05


# ============================================================
# Layer 5 -- Chan's own GLD/GDX archive, the lost-vintage receipt
# ============================================================


class TestGldGdxChanArchive:
    """Freeze what Chan's own archived GLD.xls and GDX.xls produce, and pin
    that they do NOT reproduce his printed 1.6766.

    Vintage: the adjusted-close columns of Chan's companion .xls, last saved
    2007-12-02, committed as data/gld_chan.csv and data/gdx_chan.csv. The
    design doc calls 1.6766 a lost data vintage. This is the receipt. Even
    Chan's own saved files, re-run, land at 1.6395, which is essentially the
    yfinance 1.6379 rather than the book. The 2007 book-run vintage is a
    still-earlier state that no surviving file carries.
    """

    @staticmethod
    @pytest.fixture(scope="class")
    def arch() -> CointResult:
        """Full GLD/GDX intersection from Chan's committed .xls, adjusted close."""
        df = aligned_closes("GLD", "GDX", chan=True)
        a = df["GLD"].to_numpy(dtype=float)
        b = df["GDX"].to_numpy(dtype=float)
        return engle_granger(a, b, lags=1, origin=True)

    def test_reproduces_chans_archive(self, arch: CointResult) -> None:
        """Chan's own data gives 1.6395 and -3.52 over 2006-05-23..2007-11-30."""
        assert arch.nobs == 383
        assert arch.origin_hedge == pytest.approx(1.6395, abs=5e-4)
        assert arch.hedge_ratio == pytest.approx(1.3865, abs=5e-4)
        assert arch.adf_stat == pytest.approx(-3.52, abs=1e-2)
        assert arch.half_life == pytest.approx(10.3, abs=0.1)

    def test_hedge_is_not_the_lost_book_vintage(self, arch: CointResult) -> None:
        """The whole point of committing this archive. Even Chan's own saved
        files miss his printed 1.6766, so the 2007 book-run vintage is gone."""
        assert arch.origin_hedge is not None
        assert abs(arch.origin_hedge - 1.6766) > 0.03

    def test_verdict_survives_the_drift(self, arch: CointResult) -> None:
        """The vintage moved the hedge but not the conclusion. The pair still
        cointegrates at the 5% level, the same verdict --ch7 reaches on
        yfinance data."""
        assert arch.adf_stat < EG_CRIT_N2["5%"]
