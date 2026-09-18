"""The pins for the GLD/GDX and KO/PEP replications.

This file is the single authority for every number the repo's own prose quotes
about these two pairs. A doc that recomputed one of them would be a second
implementation of the calculation, and the two would drift without either
looking wrong. The essay copied in from the sibling repo is the exception, and
README.md lists the six figures in it that nothing here asserts.

There is no dataset gate. All four vintages are committed to git, so every
layer runs everywhere the suite runs. The primitives underneath have their own
mechanics tests in ``quantcore``; this file tests the
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
6. ``TestLagSettingDetour``, the third GLD/GDX result in the book. Chan reports
   that Python disagreed with MATLAB and R on the verdict and concludes Python
   cannot be trusted for this. The disagreement is a setting, and this pins it.
7. ``TestAdjustedCloseMovesWithTheDownloadDate``, the part of the vintage
   premise one download date can show: GDX's adjusted 2006 closes sit below
   its raw ones, and GLD's do not move at all.
8. ``TestReportNamesItsBasis``, which holds the report's price-basis line. It
   is the one line that says which vintage produced the numbers above it.

1.6766 is a cited book target throughout, never asserted as a computed result,
because no surviving file reproduces it.
"""

from __future__ import annotations

import math
import warnings

import numpy as np
import pandas as pd
import pytest
from quantcore.timeseries import EG_CRIT_N2, adf_tstat
from statsmodels.tsa.stattools import adfuller

from chan.pair_cointegration import (
    BOOK_END,
    BOOK_START,
    BOOK_TRAIN_END,
    CointResult,
    RollingCoint,
    aligned_closes,
    engle_granger,
    load_close,
    return_correlation,
    rolling_cointegration,
    run,
    selftest,
)

# ============================================================
# Layer 1 -- the two-step test on synthetic pairs (engle_granger)
# ============================================================


class TestEngleGranger:
    """The pair-specific two-step test on synthetic pairs with known answers.

    The underlying OLS / ADF / OU primitives are tested in
    quantcore's own suite. Here the assertions are the verdict
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

    Vintage: GLD and GDX from yfinance. The two book windows read the raw
    as-traded close, downloaded 2026-08-27. The full-history run reads Yahoo's
    dividend-adjusted close, and GLD's adjusted file was downloaded 2026-06-16,
    ten weeks earlier than the other three. data/README.md carries the dates
    per file, because they are not one date.

    Values are pinned at the 4-decimal CLI precision, rounded from the true
    value. Chan's printed 1.6766 is not asserted, because it is a book target
    the replication cannot hit from any modern download.
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
        assert ch7.intercept == pytest.approx(9.9361, abs=5e-4)
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
        # The half-life is the other half of the story the blog post tells:
        # ten days on Chan's window, over eight hundred on the full span.
        assert full_span.half_life == pytest.approx(833.5, abs=0.1)


# ============================================================
# Layer 3 -- the rolling-window regime scan behind the write-up's figure
# ============================================================


class TestRollingRegime:
    """Freeze the rolling-window scan over the full as-traded history.

    A one-year window, 252 trading days, stepped monthly by 21 days, with
    ``origin=True`` so Chan's through-origin hedge rides along. A re-download
    that shifts the vintage moves these pins.

    These are the numbers section 6 of
    ``blog/gld-gdx-cointegration-lessons.md`` quotes, and
    ``docs/figures/reproduction_regime_map.png`` is the picture of them, drawn
    by :mod:`chan.regime_figure`. A vintage shift moves the prose, the figure
    and these pins together, and ``tests/test_regime_figure.py`` is what holds
    the figure to what this class computes.
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
        assert math.isfinite(kopep.half_life)
        assert kopep.half_life == pytest.approx(618.8, abs=0.1)

    def test_a_weak_correlation_is_judged_two_sided(self) -> None:
        """The p-value is two-sided, and on KO/PEP that cannot be checked,
        because the true p underflows to zero and any tail convention clears
        0.05. A borderline synthetic pair separates them: two-sided it is 0.091
        and fails at the 5% level, one-sided it would be 0.045 and pass."""
        rng = np.random.default_rng(47)
        a = 100 * np.cumprod(1 + rng.standard_normal(31) * 0.01)
        b = 100 * np.cumprod(1 + rng.standard_normal(31) * 0.01)
        _r, _t, p_value = return_correlation(a, b)
        assert p_value == pytest.approx(0.0905, abs=5e-4)
        assert p_value > 0.05

    def test_returns_are_correlated(self, corr: tuple[float, float, float]) -> None:
        """The other half of the counter-example. Daily returns ARE
        significantly correlated, at Chan's r = 0.4849, even though the prices
        do not cointegrate."""
        r, t, p = corr
        # Tighter than Chan's printed 4 decimals, on purpose. These pin the two
        # definitional choices the function makes, which a 4-decimal tolerance
        # is too loose to hold: returns divide by the earlier price, and the
        # t-statistic carries n-2 degrees of freedom.
        assert r == pytest.approx(0.48492, abs=5e-5)
        assert t == pytest.approx(49.0707, abs=5e-4)
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


# ============================================================
# Layer 6 -- the lag setting behind Chan's Python-vs-MATLAB detour
# ============================================================


class TestLagSettingDetour:
    """Pin the third GLD/GDX result, which is a claim about tooling.

    Chan reports that his Python run disagreed with his MATLAB and R runs on
    whether GLD/GDX cointegrate, and concludes that Python's statistics and
    econometrics packages are not to be trusted. The packages are fine. All
    three ran the same test under different defaults.

    ``statsmodels`` defaults to ``autolag='aic'``, which reads the lag count
    off the data. On the Chapter 3 window it picks six, and each added lag
    pulls the statistic toward zero. Six is enough to carry it back across the
    10% line, which is the whole disagreement. MATLAB and R fix the lag at one.

    Without this pin the claim lives only in a module docstring, and a docstring
    is not an authority for a number.
    """

    @staticmethod
    @pytest.fixture(scope="class")
    def spread() -> np.ndarray:
        """The Chapter 3 residual spread, which is what both runs test."""
        df = aligned_closes("GLD", "GDX", start=BOOK_START, end=BOOK_TRAIN_END, unadjusted=True)
        a = df["GLD"].to_numpy(dtype=float)
        b = df["GDX"].to_numpy(dtype=float)
        return engle_granger(a, b, lags=1, origin=True).spread

    def test_fixed_lag_reproduces_the_book(self, spread: np.ndarray) -> None:
        """At the fixed lag MATLAB and R use, the pair rejects at 10%, which is
        the verdict the book reports."""
        stat, _nobs = adf_tstat(spread, lags=1, constant=False)
        assert stat == pytest.approx(-3.0875, abs=5e-4)
        assert stat < EG_CRIT_N2["10%"]

    def test_the_default_lag_choice_flips_the_verdict(self, spread: np.ndarray) -> None:
        """Letting statsmodels pick the lag reverses the conclusion on the same
        data, with the same library, through one setting."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            result = adfuller(spread, autolag="aic", regression="n")
        stat, used_lag = float(result[0]), int(result[2])
        assert used_lag == 6
        assert stat == pytest.approx(-2.2979, abs=5e-4)
        assert stat > EG_CRIT_N2["10%"]


# ============================================================
# Layer 7 -- the vintage premise, as far as one download date shows
# ============================================================


class TestAdjustedCloseMovesWithTheDownloadDate:
    """The vintage premise, as far as one download date can show it.

    An adjusted close folds every later dividend back into the history, so the
    same 2006 trading day reads lower in the adjusted series than in the raw
    one. Two vintages taken at different dates would show the series moving
    under itself, which is issue 4's remaining half and needs the recorder.
    This is the weaker claim that the committed files already support, and
    ``blog/gld-gdx-cointegration-lessons.md`` quotes the gap it measures.
    """

    def test_gdx_2006_adjusted_sits_about_fifteen_percent_below_raw(self) -> None:
        raw = load_close("GDX", unadjusted=True)
        adjusted = load_close("GDX")
        shared = raw.index.intersection(adjusted.index)
        gap = (adjusted.loc[shared] / raw.loc[shared] - 1.0).loc["2006-01-01":"2006-12-31"]

        assert len(gap) > 0
        assert float(gap.mean()) == pytest.approx(-0.1513, abs=5e-4)

    def test_gld_pays_nothing_so_its_two_series_do_not_part(self) -> None:
        """GLD is the control. It pays no distribution, so the adjustment has
        nothing to fold in and the two series stay on top of each other. That
        is why the essay names GDX rather than GLD as the symbol that drifts."""
        raw = load_close("GLD", unadjusted=True)
        adjusted = load_close("GLD")
        shared = raw.index.intersection(adjusted.index)
        gap = (adjusted.loc[shared] / raw.loc[shared] - 1.0).abs()

        assert float(gap.max()) < 1e-3


# ============================================================
# Layer 8 -- the report's price-basis line
# ============================================================


class TestReportNamesItsBasis:
    """Hold the line of the report that says which vintage produced the rest.

    This repo exists because a number without its vintage cannot be checked, so
    a report that names the wrong source is worse than one that names none. The
    ported code did exactly that: it announced Yahoo's adjusted close while
    reading Chan's companion files, and nothing noticed, because nothing covered
    the report at all.
    """

    def test_chan_companion_data_is_named_as_such(self, capsys: pytest.CaptureFixture[str]) -> None:
        run("KO", "PEP", 1, origin=True, show_correlation=True, chan=True)
        assert "Price basis: Chan's companion-file adjusted closes" in capsys.readouterr().out

    def test_raw_closes_are_named_as_such(self, capsys: pytest.CaptureFixture[str]) -> None:
        run("GLD", "GDX", 1, start=BOOK_START, end=BOOK_END, unadjusted=True, origin=True)
        assert "Price basis: raw / unadjusted closes" in capsys.readouterr().out

    def test_the_yahoo_adjusted_default_is_named_as_such(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        run("GLD", "GDX", 1, start=BOOK_START, end=BOOK_END)
        assert "Price basis: Yahoo dividend-adjusted closes" in capsys.readouterr().out
