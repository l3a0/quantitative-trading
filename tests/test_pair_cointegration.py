"""The pins for the GLD/GDX and KO/PEP replications.

This file is the single authority for every number the repo's own prose quotes
about these two pairs. A doc that recomputed one of them would be a second
implementation of the calculation, and the two would drift without either
looking wrong. The two blog posts about these pairs are the exceptions, and
README.md lists the figures in each that nothing here asserts.

There is no dataset gate. All four vintages are committed to git, so every
layer runs everywhere the suite runs. The primitives underneath have their own
mechanics tests in ``ithildincore``; this file tests the
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
   cannot be trusted for this. Against MATLAB the disagreement is a lag
   setting, apart from a detail of ``cadf``'s regression worth 0.0035 at one
   lag, and this pins it on the 2026 closes. ``TestChansPythonRun`` reproduces
   his Python and MATLAB printouts on his own files, and
   ``TestChansRRunIsACovariateAugmentedDickeyFuller`` reproduces his R
   printout and shows that run was a different test on a longer window.
7. ``TestResidualCheck``, which asks which of those settings the test is
   entitled to, by checking what each lag count leaves in the residuals.
   Exploratory, and ``docs/figures/adf_residual_autocorrelation.png`` is the
   picture of it. ``TestResidualCheckOnChansFiles`` repeats it on Chan's own
   files, and ``TestResidualCheckChapter7`` asks the same of the longer window,
   on the yfinance closes and on Chan's own files.
8. ``TestAdjustedCloseMovesWithTheDownloadDate``, the part of the vintage
   premise one download date can show: GDX's adjusted 2006 closes sit below
   its raw ones, and GLD's do not move at all.
9. ``TestReportNamesItsBasis``, which holds the lines of the report that say
   which vintage produced the numbers above them. The basis line names which
   kind of series and the vintage lines name which file, which vendor and which
   date, read off the manifest entry the reader resolved.

1.6766 is a cited book target throughout, never asserted as a computed result,
because no surviving file reproduces it.

**Where this came from.** ``tests/test_pair_cointegration.py`` in the sibling
``trading-strategies`` repo, at commit ``b27222b``, landed here in ``ce3f757``.
That repo retired its Chan material in ``cc1ec3a`` and this file is gone from
its tip, so the path alone no longer finds it and the commit is what does.
No test method and no class was removed, and all sixteen sibling test methods
survived. The copy changed five things.

1. Imports repointed to ``chan``, with ``math``, ``warnings``,
   ``statsmodels.tsa.stattools.adfuller``, ``run`` and ``adf_tstat`` added.
2. Seven cached fixture helpers became static methods and dropped ``self``.
3. Two classes added, ``TestLagSettingDetour`` and ``TestReportNamesItsBasis``.
4. Six test methods added.
5. Several pins tightened from a bound to an exact figure, ``kopep.half_life``
   from greater than 100 to 618.8 among them, and the return correlation
   gained a t-statistic pin beside its r.

Those five describe the file at ``ce3f757``, where the repointed imports named
``chan.timeseries``, which went to ``ithildincore`` in ``aec40f3`` and cannot
be imported today. They cover the code. The comments and the docstrings were
rewritten to this repo's writing rules, which ``CLAUDE.md`` says no port carries
across, and the sibling's ``pyright`` pragma went with them. Diff ``b27222b``
against ``ce3f757`` to read the port and against ``HEAD`` to read everything
since, with docstrings stripped from both sides, because they are most of it.
"""

from __future__ import annotations

import math
import warnings

import numpy as np
import pandas as pd
import pytest
from ithildincore.timeseries import EG_CRIT_N2, adf_tstat, ols
from statsmodels.tsa.adfvalues import mackinnoncrit
from statsmodels.tsa.stattools import adfuller, coint

from chan.pair_cointegration import (
    BOOK_END,
    BOOK_START,
    BOOK_TRAIN_END,
    RESIDUAL_LAGS,
    CointResult,
    RollingCoint,
    engle_granger,
    lesage_cadf,
    main,
    residual_check,
    return_correlation,
    rolling_cointegration,
    run,
    selftest,
)
from chan.series import aligned_closes, load_close

# ============================================================
# Layer 1 -- the two-step test on synthetic pairs (engle_granger)
# ============================================================


class TestEngleGranger:
    """The pair-specific two-step test on synthetic pairs with known answers.

    The underlying OLS / ADF / OU primitives are tested in
    ithildincore's own suite. Here the assertions are the verdict
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
    ten weeks earlier than the other three. data/vintages.jsonl carries the
    dates per file, because they are not one date.

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

    def test_the_plain_adf_table_would_have_passed_it(self, kopep: CointResult) -> None:
        """Read against the plain ADF table, the same statistic rejects at 5%.

        The plain table is for a series nobody fitted. The Engle-Granger table
        is stricter because step one already picked the most stationary-looking
        combination of the two prices. KO/PEP sits between the two: it clears
        the plain 5% value and misses every Engle-Granger value, so the table is
        what decides the verdict. ``blog/price-spread-mean-reversion.md`` quotes
        the plain values at two decimals.

        Specification: statsmodels' MacKinnon (2010) large-sample critical
        values for one series with no deterministic term, which is the
        ``regression='n'`` ADF this file runs on every residual spread. First
        pinned on 2026-09-29.
        """
        one_pct, five_pct, ten_pct = (float(v) for v in mackinnoncrit(N=1, regression="n"))
        assert (one_pct, five_pct, ten_pct) == pytest.approx((-2.5657, -1.9410, -1.6168), abs=5e-5)
        assert (round(one_pct, 2), round(five_pct, 2), round(ten_pct, 2)) == (-2.57, -1.94, -1.62)
        assert one_pct < kopep.adf_stat < five_pct
        assert kopep.adf_stat > max(EG_CRIT_N2.values())

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

    def test_the_mean_price_ratio_approximates_the_through_origin_slope(
        self, arch: CointResult
    ) -> None:
        """The ratio of the mean prices lands 0.0021 from the through-origin
        slope and more than 0.25 from the with-intercept one.

        The through-origin slope is the sum of the price products over the sum
        of GDX's squared prices. When prices move only a little against their
        level, that is close to the ratio of the means, which is why the ratio
        works as a quick check on Chan's printed hedge and not on the slope the
        test uses. ``blog/price-spread-mean-reversion.md`` quotes all three at
        four decimals, the form the rest of the repo writes the hedges in.

        Vintage: ``gld_chan.csv`` and ``gdx_chan.csv``, the adjusted-close
        columns of Chan's companion .xls. Specification: the full intersection,
        2006-05-23 to 2007-11-30, 385 rows. First pinned on 2026-09-29.
        """
        df = aligned_closes("GLD", "GDX", chan=True)
        assert len(df) == 385
        ratio = float(df["GLD"].mean() / df["GDX"].mean())
        assert arch.origin_hedge is not None
        assert ratio == pytest.approx(1.6416, abs=5e-5)
        assert ratio - arch.origin_hedge == pytest.approx(0.0021, abs=5e-5)
        assert abs(ratio - arch.hedge_ratio) > 0.25
        assert (round(ratio, 4), round(arch.origin_hedge, 4), round(arch.hedge_ratio, 4)) == (
            1.6416,
            1.6395,
            1.3865,
        )

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

    def test_the_half_life_slope_is_not_the_adf_slope(self, arch: CointResult) -> None:
        """Both regressions put the daily change on the lagged level, so under
        the half-life's own AR(1) model their slopes estimate the same
        reversion speed. They are still two numbers, and read as half-lives
        they give 10.3 and 10.6 days.

        The half-life regression carries a constant and no lagged difference.
        The ADF regression at Chan's one lag carries a lagged difference and no
        constant, and it loses one more row to that lag. Stepping from one fit
        to the other one change at a time splits the gap of 0.0018:

        1. Dropping the constant moves the slope by less than 1e-5. The spread
           is a residual from a fit with an intercept, so its mean is already
           zero and a constant has nothing to absorb.
        2. Dropping the first row moves it by about a tenth of the gap.
        3. Adding the lagged difference moves it by the rest, about nine
           tenths.

        Specification: the with-intercept residual spread over 2006-05-23 to
        2007-11-30, 385 observations, which leaves 384 rows in the half-life
        fit and 383 in the ADF fit. The half-life slope is the one
        ``ou_half_life`` fits. The ADF slope is ``adfuller`` at ``maxlag=1``,
        ``autolag=None`` and ``regression='n'``, the fit behind
        ``arch.adf_stat``. First pinned on 2026-09-28.
        """
        z = arch.spread
        dz = np.diff(z)

        def slope(y: np.ndarray, *cols: np.ndarray) -> float:
            return float(ols(y, np.column_stack(cols)).beta[0])

        lam = slope(dz, z[:-1], np.ones(len(dz)))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            fit = adfuller(z, maxlag=1, autolag=None, regression="n", regresults=True)
        gamma = float(fit[-1].resols.params[0])

        assert lam == pytest.approx(-0.0672, abs=5e-5)
        assert gamma == pytest.approx(-0.0654, abs=5e-5)
        assert gamma - lam == pytest.approx(0.0018, abs=5e-5)
        assert math.log(2) / -lam == pytest.approx(arch.half_life, abs=1e-9)
        assert math.log(2) / -lam == pytest.approx(10.3, abs=0.05)
        assert math.log(2) / -gamma == pytest.approx(10.6, abs=0.05)
        assert float(fit[0]) == pytest.approx(arch.adf_stat, abs=1e-9)
        assert slope(dz[1:], z[1:-1], dz[:-1]) == pytest.approx(gamma, abs=1e-12)

        no_constant = slope(dz, z[:-1])
        no_first_row = slope(dz[1:], z[1:-1])
        gap = gamma - lam
        assert abs(no_constant - lam) < 1e-5
        assert (no_first_row - no_constant) / gap == pytest.approx(0.088, abs=0.005)
        assert (gamma - no_first_row) / gap == pytest.approx(0.909, abs=0.005)


# ============================================================
# Layer 6 -- the lag setting behind Chan's Python-vs-MATLAB detour
# ============================================================


class TestLagSettingDetour:
    """Pin the third GLD/GDX result, which is a claim about tooling.

    Chan reports that his Python run disagreed with his MATLAB and R runs on
    whether GLD/GDX cointegrate, and concludes that Python's statistics and
    econometrics packages are not to be trusted. The packages are fine. Python
    and MATLAB ran the same test with different lag settings, up to a detail of
    how ``cadf`` forms its regression, and R ran a
    different test, which ``TestChansRRunIsACovariateAugmentedDickeyFuller``
    holds.

    ``statsmodels`` defaults to ``autolag='aic'``, which reads the lag count
    off the data. On the Chapter 3 window it picks six, where Chan's MATLAB
    call passes one. Six carries the statistic back across the 10% line, which
    is the disagreement between those two. A detail of ``cadf``'s own
    regression moves the one-lag statistic by a further 0.0035 on Chan's files,
    which ``TestChansPythonRun`` pins, and changes no verdict.

    On the 2026 yfinance closes this class reads, the statistic does not drift
    steadily toward zero as lags are added. It rises and falls: weaker at three
    lags than at four, and back near the line at thirteen. What the lag setting
    decides is the verdict, which clears 10% at zero and one lag and misses it
    at every count from two to sixteen.
    ``test_the_statistic_is_not_monotone_in_the_lag`` pins that shape.

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
        """At the fixed lag Chan's MATLAB call passes, the pair rejects at
        10%, which is the verdict the book reports for that run."""
        stat, _nobs = adf_tstat(spread, lags=1, constant=False)
        assert stat == pytest.approx(-3.0875, abs=5e-4)
        assert stat < EG_CRIT_N2["10%"]

    def test_cadfs_own_regression_leaves_the_verdict_alone(self, spread: np.ndarray) -> None:
        """Row 4 under the regression ``cadf`` itself runs, which row 12
        reproduces on Chan's files. It gives -3.0908 on these closes, 0.0032
        more negative than row 4's figure and still past both 10% values, and
        widens the margin against MATLAB's printed -3.082 from 0.0055 to
        0.0088."""
        df = aligned_closes("GLD", "GDX", start=BOOK_START, end=BOOK_TRAIN_END, unadjusted=True)
        stat, _ar1, nobs = lesage_cadf(df["GLD"].to_numpy(float), df["GDX"].to_numpy(float))
        port, _nobs = adf_tstat(spread, lags=1, constant=False)
        assert nobs == 250
        assert stat == pytest.approx(-3.0908, abs=5e-5)
        assert round(stat - port, 4) == -0.0032
        assert stat < TestChansPythonRun.MATLAB_10PCT < EG_CRIT_N2["10%"]
        assert round(port - TestChansPythonRun.MATLAB_10PCT, 4) == -0.0055
        assert round(stat - TestChansPythonRun.MATLAB_10PCT, 4) == -0.0088

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

    def test_each_automatic_rule_and_the_ceiling_it_searches_to(self, spread: np.ndarray) -> None:
        """AIC and the t-stat rule pick six lags and BIC picks none, each
        searching up to sixteen.

        Schwert's rule, ``12 * (n / 100) ** 0.25``, gives 15.12 at 252 days.
        Schwert rounds it down to 15, and statsmodels rounds it up to 16 when no
        ``maxlag`` is passed. The ceiling is read off the stored result, so it
        is what statsmodels searched rather than what the formula says it
        should. BIC charges more per extra term, which is why it stops at zero
        where the other two stop at six. ``blog/price-spread-mean-reversion.md``
        quotes all of this.

        Vintage and specification are the sweep's below: the Chapter 3
        with-intercept residual spread on the 2026-08-27 yfinance raw closes,
        tested by ``adfuller`` with ``regression='n'`` and each ``autolag``
        rule at its default ceiling. First pinned on 2026-09-29.
        """
        schwert = 12 * (len(spread) / 100) ** 0.25
        assert len(spread) == 252
        assert schwert == pytest.approx(15.12, abs=5e-3)
        assert (math.floor(schwert), math.ceil(schwert)) == (15, 16)

        picks = {}
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            for rule in ("aic", "bic", "t-stat"):
                result = adfuller(spread, autolag=rule, regression="n", store=True)
                assert result[-1].maxlag == 16
                picks[rule] = (int(result[-1].usedlag), float(result[0]))
        assert {rule: lag for rule, (lag, _) in picks.items()} == {"aic": 6, "bic": 0, "t-stat": 6}
        assert picks["aic"][1] == pytest.approx(-2.2979, abs=5e-4)
        assert picks["t-stat"][1] == pytest.approx(-2.2979, abs=5e-4)
        assert picks["bic"][1] == pytest.approx(-3.2018, abs=5e-4)

    def test_the_statistic_is_not_monotone_in_the_lag(self, spread: np.ndarray) -> None:
        """Adding lags moves the statistic both ways, while the verdict holds
        from two lags up.

        Vintage: ``gld_20yr_prices_unadjusted.csv`` and
        ``gdx_20yr_prices_unadjusted.csv``, yfinance raw closes, both downloaded
        2026-08-27. Specification: the with-intercept residual spread over
        2006-05-23 to 2007-05-23, 252 observations, tested by ``adfuller`` with
        ``maxlag=k``, ``autolag=None`` and ``regression='n'``, so each lag count
        is a fixed lag rather than a selection. The spread and the window are
        row 4 of ``docs/replication-log.md``. The sweep was first run on
        2026-09-26.
        """

        def stat_at(k: int) -> float:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", FutureWarning)
                return float(adfuller(spread, maxlag=k, autolag=None, regression="n")[0])

        sweep = [stat_at(k) for k in range(17)]
        pinned = [
            -3.2018, -3.0875, -2.6402, -2.4067, -2.6394, -2.1853,
            -2.2979, -2.1132, -2.1111, -2.2259, -2.5294, -2.6072,
            -2.6604, -2.9872, -2.2640, -1.9045, -1.9737,
        ]  # fmt: skip
        assert sweep == pytest.approx(pinned, abs=5e-4)

        # The statistic is more negative at four lags than at three, and more
        # negative at thirteen than at any other count from two to sixteen. A
        # steady pull toward zero would forbid both.
        assert sweep[4] < sweep[3]
        assert sweep[13] == min(sweep[2:])

        # The verdict is what the lag decides: zero and one lag clear the 10%
        # line, and every count from two to sixteen misses it.
        assert all(sweep[k] < EG_CRIT_N2["10%"] for k in (0, 1))
        assert all(sweep[k] > EG_CRIT_N2["10%"] for k in range(2, 17))


class TestChansPythonRun:
    """Chan's Python run, reproduced on his own files at every figure he printed.

    The book's Python code, at pp. 149 to 150 of the revised edition, calls
    ``coint(df['Adj Close_GLD'], df['Adj Close_GDX'])`` on the first 252 rows
    of ``GLD.xls`` and ``GDX.xls`` merged on date, with no lag argument. So it is
    the Engle-Granger test at ``statsmodels``' defaults, which choose the lag by
    ``autolag='aic'``. His prose at Kindle location 3755 rounds the printed t to
    -2.4. The owner read the code and the printout on 2026-10-02, and
    issue 168 records the reading, since the book notes hold the prose only.

    It is the test Chan's MATLAB call runs in row 4 of
    ``docs/replication-log.md``, on the same window with a different lag count,
    as ``example3_6_1.m`` and the book's code read, apart from one detail of
    ``cadf``'s regression. ``test_cadfs_own_regression_lands_matlabs_printout``
    reproduces MATLAB's -3.18156477 on these files, and
    ``test_the_port_misses_cadf_by_one_detail_of_its_regression`` says what the
    detail is. ``TestLagSettingDetour`` holds the lag difference on the 2026
    closes.

    Vintage: ``gld_chan.csv`` and ``gdx_chan.csv``, the adjusted-close columns
    of Chan's companion ``GLD.xls`` and ``GDX.xls``, last saved 2007-12-02.
    Specification: 2006-05-23 to 2007-05-23, 252 rows, ``coint`` at its
    defaults, which fits GLD on GDX with an intercept and runs ``adfuller`` on
    the residuals with ``regression='n'``. First pinned on 2026-10-02.
    """

    #: The t-statistic, p-value and through-origin hedge the book's Python
    #: output prints at pp. 149 to 150, and the -2.4 its prose quotes at
    #: location 3755. Cited, never computed.
    BOOK_T = -2.3591268376687244
    BOOK_P = 0.3444494880427884
    BOOK_HEDGE = 1.631009
    BOOK_PROSE_T = -2.4

    @staticmethod
    @pytest.fixture(scope="class")
    def closes() -> pd.DataFrame:
        return aligned_closes("GLD", "GDX", chan=True, start=BOOK_START, end=BOOK_TRAIN_END)

    def test_coint_at_its_defaults_lands_the_printout(self, closes: pd.DataFrame) -> None:
        """The t and the p land within a billionth of the printout, and the
        statistic fails to reject at 10%, which is the verdict Chan reports.
        A second call returns the same value."""
        assert len(closes) == 252
        stat, pvalue, _crit = coint(closes["GLD"], closes["GDX"])
        assert stat == pytest.approx(self.BOOK_T, abs=1e-9)
        assert pvalue == pytest.approx(self.BOOK_P, abs=1e-9)
        assert round(stat, 1) == self.BOOK_PROSE_T
        assert pvalue > 0.10
        assert coint(closes["GLD"], closes["GDX"])[0] == stat

    def test_the_default_picks_six_lags(self, closes: pd.DataFrame) -> None:
        """``coint``'s statistic is ``adfuller`` at ``autolag='aic'`` on the
        with-intercept residual spread, which picks six lags and keeps 245 of
        the 252 rows."""
        a = closes["GLD"].to_numpy(dtype=float)
        b = closes["GDX"].to_numpy(dtype=float)
        spread = engle_granger(a, b, lags=1, origin=True).spread
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            result = adfuller(spread, autolag="aic", regression="n")
        assert (int(result[2]), int(result[3])) == (6, 245)
        assert float(result[0]) == pytest.approx(coint(closes["GLD"], closes["GDX"])[0], abs=1e-12)

    def test_the_through_origin_hedge_lands_the_printout(self, closes: pd.DataFrame) -> None:
        """The printed 1.631009 is the through-origin slope at six decimals."""
        a = closes["GLD"].to_numpy(dtype=float)
        b = closes["GDX"].to_numpy(dtype=float)
        hedge = engle_granger(a, b, lags=1, origin=True).origin_hedge
        assert hedge is not None
        assert hedge == pytest.approx(1.63100895, abs=5e-9)
        assert round(hedge, 6) == self.BOOK_HEDGE

    def test_the_code_comment_quotes_the_full_window(self) -> None:
        """The code's comment says the p-value is "only 1.8%" while its output
        prints 0.344. ``coint`` at its defaults over all 385 days gives 0.0184,
        so the comment comes from a run on the whole file."""
        closes = aligned_closes("GLD", "GDX", chan=True)
        assert len(closes) == 385
        _stat, pvalue, _crit = coint(closes["GLD"], closes["GDX"])
        assert pvalue == pytest.approx(0.0184, abs=5e-5)

    def test_the_fixed_lags_that_matched_the_2026_closes_miss_on_chans(
        self, closes: pd.DataFrame
    ) -> None:
        """The null result behind the old reading of -2.4 and -3.2.

        On the 2026 closes, zero fixed lags give -3.2018 and three give
        -2.4067, which read as Chan's two figures. On his own files the same
        counts give -3.2975 and -2.4857, so those matches were a coincidence of
        vintage. One fixed lag gives -3.1780, which rounds to R's -3.2 and is
        a different test from the one R ran, which the next class holds.
        Specification: ``adfuller`` with ``maxlag=k``, ``autolag=None`` and
        ``regression='n'`` on the same spread as above.
        """
        a = closes["GLD"].to_numpy(dtype=float)
        b = closes["GDX"].to_numpy(dtype=float)
        spread = engle_granger(a, b, lags=1, origin=True).spread

        def stat_at(k: int) -> float:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", FutureWarning)
                return float(adfuller(spread, maxlag=k, autolag=None, regression="n")[0])

        assert [stat_at(k) for k in (0, 1, 3)] == pytest.approx(
            [-3.2975, -3.1780, -2.4857], abs=5e-4
        )
        assert [round(stat_at(k), 1) for k in (0, 1, 3)] == [-3.3, -3.2, -2.5]

    #: What Chan's MATLAB ``cadf`` printed for this window at Kindle location
    #: 3718: the t-statistic, the AR(1) estimate beside it, and the 10% critical
    #: value. Cited, never computed. The 5% value is
    #: ``TestResidualCheckChapter7.MATLAB_5PCT``.
    MATLAB_T = -3.18156477
    MATLAB_AR1 = -0.070038
    MATLAB_10PCT = -3.082

    def test_cadfs_own_regression_lands_matlabs_printout(self, closes: pd.DataFrame) -> None:
        """Row 12 of Entry 1: MATLAB's run, reproduced on Chan's own files.

        :func:`~chan.pair_cointegration.lesage_cadf` at one lag returns the
        printed t-statistic at all eight decimals and the printed AR(1)
        estimate at all six, and the statistic lands the band Chan reports,
        past the 10% value and short of the 5% one under both tables.

        Specification: ``cadf(GLD, GDX, 0, 1)`` as ``example3_6_1.m`` calls
        it, over 2006-05-23 to 2007-05-23, 250 ADF observations. Vintage as
        the class. First pinned on 2026-10-03.
        """
        a = closes["GLD"].to_numpy(dtype=float)
        b = closes["GDX"].to_numpy(dtype=float)
        stat, ar1, nobs = lesage_cadf(a, b, lags=1)

        assert nobs == 250
        assert stat == pytest.approx(self.MATLAB_T, abs=5e-9)
        assert round(ar1, 6) == self.MATLAB_AR1
        assert EG_CRIT_N2["5%"] < stat < EG_CRIT_N2["10%"]
        assert TestResidualCheckChapter7.MATLAB_5PCT < stat < self.MATLAB_10PCT
        assert round(stat - EG_CRIT_N2["10%"], 4) == -0.1416
        assert round(stat - self.MATLAB_10PCT, 4) == -0.0996

    def test_the_port_misses_cadf_by_one_detail_of_its_regression(
        self, closes: pd.DataFrame
    ) -> None:
        """What separates the port's one-lag statistic from MATLAB's.

        ``adfuller`` with ``regression='n'``, which is what
        :func:`~chan.pair_cointegration.engle_granger` and ``coint`` run,
        gives -3.1780 on the same spread, +0.0035 from the printout. With
        ``regression='c'`` the coefficient matches ``cadf``'s at every digit
        printed and the statistic is -3.1749, so what is left is how ``cadf``
        forms the standard error. Computing its covariance from the demeaned
        regressors, the one step a textbook ADF does differently, gives -3.18133078
        and misses the printout. The through-origin spread is not the input:
        it gives -3.8851.

        The gap is +0.0035 from the engine's value and +0.0036 from the
        four-decimal one, which is the rounding the replication log's
        precision rule forbids. Issue 232 quoted the second.
        """
        a = closes["GLD"].to_numpy(dtype=float)
        b = closes["GDX"].to_numpy(dtype=float)
        fit = engle_granger(a, b, lags=1, origin=True)
        assert fit.origin_hedge is not None

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            port = adfuller(fit.spread, maxlag=1, autolag=None, regression="n", regresults=True)
            constant = adfuller(fit.spread, maxlag=1, autolag=None, regression="c", regresults=True)
            through_origin = float(
                adfuller(a - fit.origin_hedge * b, maxlag=1, autolag=None, regression="n")[0]
            )
        stat = float(port[0])

        assert int(port[-1].resols.nobs) == 250
        assert stat == pytest.approx(-3.1780, abs=5e-5)
        assert round(stat - self.MATLAB_T, 4) == 0.0035
        assert round(round(stat, 4) - self.MATLAB_T, 4) == 0.0036

        assert float(constant[0]) == pytest.approx(-3.1749, abs=5e-5)
        assert round(float(constant[-1].resols.params[0]), 6) == self.MATLAB_AR1

        # cadf with its covariance taken from the demeaned regressors instead.
        dep = np.diff(fit.spread)[1:]
        z = np.column_stack([fit.spread[1:-1], np.diff(fit.spread)[:-1]])
        z_centred = z - z.mean(axis=0)
        beta = np.linalg.lstsq(z_centred, dep - dep.mean(), rcond=None)[0]
        res = dep - dep.mean() - z_centred @ beta
        cov = float(res @ res) / (len(dep) - 2) * np.linalg.inv(z_centred.T @ z_centred)
        assert beta[0] / math.sqrt(cov[0, 0]) == pytest.approx(-3.18133078, abs=5e-9)

        assert through_origin == pytest.approx(-3.8851, abs=5e-5)

        # Lagged differences line up as cadf.m's lag and trimr leave them: at
        # every lag count cadf's coefficient is the textbook ADF-with-constant
        # one, so only the standard error differs.
        for lags in (2, 3, 6):
            _stat, coefficient, nobs = lesage_cadf(a, b, lags=lags)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", FutureWarning)
                textbook = adfuller(
                    fit.spread, maxlag=lags, autolag=None, regression="c", regresults=True
                )[-1].resols
            assert nobs == int(textbook.nobs)
            assert coefficient == pytest.approx(float(textbook.params[0]), abs=1e-12)


class TestChansRRunIsACovariateAugmentedDickeyFuller:
    """Chan's R run, which calls Hansen's covariate-augmented Dickey-Fuller test
    rather than the Engle-Granger test his prose names, and feeds it an input
    it was not built for.

    The book's R code, at p. 151 of the revised edition, calls
    ``CADFtest(model=GLD~GDX, data=mydata, type="drift", max.lag.X=1,
    subset=trainset)`` on the adjusted closes of ``GLD.txt`` and ``GDX.txt``,
    intersected on date and forward-filled with ``zoo::na.locf``. Hansen's test
    (Econometric Theory, 1995) asks whether GLD alone has a unit root, and
    gains power from a covariate that is itself stationary. The printout names
    the regression: the daily change in GLD on a constant, GLD's lagged level,
    one lagged change of GLD, and GDX today and yesterday. The statistic is the
    t on the lagged level. Chan's prose at location 3806 rounds it to -3.2. The
    owner read the code and the printout on 2026-10-02, and issue 168 records
    the reading.

    Four things follow, and the tests below hold the first three.

    1. ``subset=trainset`` did not reach the regression. The printout's 378
       residual degrees of freedom are five coefficients on 383 rows, which is
       all 385 days, not the 252 the Python run uses.
    2. The forward-fill changes nothing on these files, because the two share
       every one of GDX's trading days.
    3. The covariate went in as GDX's price, which is not stationary. Since
       b0 * x(t) + b1 * x(t-1) equals b0 * dx(t) + (b0 + b1) * x(t-1), the
       regression is an error-correction cointegration test in disguise. It
       carries GDX's lagged price beside GLD's and implies a long-run hedge of
       -(b0 + b1) / delta. Given GDX's daily change, the stationary input
       Hansen's test expects, the same regression returns a positive t.
    4. The printed p-value of 0.004975 comes from Hansen's distribution, which
       depends on the printed rho-squared of 0.2604 and assumes the stationary
       covariate this run did not have. ``EG_CRIT_N2`` belongs to the two-step
       test. So neither says whether -3.24 rejects. Nothing here computes that
       p-value, and ``docs/design.md``'s considered-and-rejected register says
       why.

    Vintage: ``gld_chan.csv`` and ``gdx_chan.csv``, the adjusted-close columns
    of Chan's companion ``GLD.xls`` and ``GDX.xls``, last saved 2007-12-02.
    Specification: the regression above by OLS over 2006-05-23 to 2007-11-30.
    First pinned on 2026-10-02.
    """

    #: The t-statistic the book's R output prints at p. 151, the five
    #: coefficients in the order of the regression above, and the -3.2 its
    #: prose quotes at location 3806. Cited, never computed.
    BOOK_T = -3.240868894
    BOOK_COEFS = (-0.07570, -0.03817, 0.08542, 0.75428, -0.68942)
    BOOK_DF = 378
    BOOK_PROSE_T = -3.2

    @staticmethod
    def r_frame() -> pd.DataFrame:
        """GLD and GDX as the R code builds them: intersected, then filled."""
        both = pd.concat(
            [load_close("GLD", chan=True), load_close("GDX", chan=True)], axis=1, join="inner"
        )
        both.columns = ["GLD", "GDX"]
        return both.ffill()

    @staticmethod
    def cadf(frame: pd.DataFrame) -> tuple[float, np.ndarray, int, int]:
        """The t on the lagged level, the coefficients, the rows and the
        residual degrees of freedom of Hansen's regression with one lag of the
        tested series' change and the covariate at lags 0 and 1."""
        y = frame["GLD"].to_numpy(dtype=float)
        x = frame["GDX"].to_numpy(dtype=float)
        dy = np.diff(y)
        target = dy[1:]
        regressors = np.column_stack([np.ones(len(target)), y[1:-1], dy[:-1], x[2:], x[1:-1]])
        fit = ols(target, regressors)
        rows, k = regressors.shape
        return float(fit.beta[1] / fit.se[1]), fit.beta, rows, rows - k

    def test_the_regression_lands_the_printout(self) -> None:
        """All 385 days land the printed t within a billionth and every
        printed coefficient at its five decimals."""
        frame = self.r_frame()
        assert len(frame) == 385
        stat, beta, rows, dof = self.cadf(frame)
        assert stat == pytest.approx(self.BOOK_T, abs=1e-9)
        assert round(stat, 1) == self.BOOK_PROSE_T
        assert (rows, dof) == (383, self.BOOK_DF)
        assert tuple(round(float(b), 5) for b in beta) == self.BOOK_COEFS
        assert beta == pytest.approx(
            [-0.0757014636, -0.0381733407, 0.0854194365, 0.7542804034, -0.6894163853], abs=1e-9
        )

    def test_the_covariate_went_in_as_a_price(self) -> None:
        """GDX's price fails to reject a unit root, so it is not the stationary
        covariate Hansen's test assumes. Written in error-correction form, the
        regression gives the same t and implies a hedge of 1.6992. Given GDX's
        daily change instead, it gives +0.3554, which no left-tailed test
        rejects.

        Specification for the unit-root check: ``adfuller`` on GDX's 385 closes
        with ``regression='c'`` and ``autolag='aic'``, which picks one lag.
        """
        frame = self.r_frame()
        x = frame["GDX"].to_numpy(dtype=float)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            level = adfuller(x, regression="c", autolag="aic")
            change = adfuller(np.diff(x), regression="c", autolag="aic")
        assert (float(level[0]), int(level[2])) == pytest.approx((-1.9258, 1), abs=5e-5)
        assert float(level[1]) == pytest.approx(0.3200, abs=5e-5)
        assert float(change[1]) < 0.01

        stat, beta, _rows, _dof = self.cadf(frame)
        y = frame["GLD"].to_numpy(dtype=float)
        dy = np.diff(y)
        dx = np.diff(x)
        target = dy[1:]
        ecm = np.column_stack([np.ones(len(target)), y[1:-1], dy[:-1], dx[1:], x[1:-1]])
        ecm_fit = ols(target, ecm)
        assert float(ecm_fit.beta[1] / ecm_fit.se[1]) == pytest.approx(stat, abs=1e-9)
        hedge = -float(beta[3] + beta[4]) / float(beta[1])
        assert hedge == pytest.approx(1.6992, abs=5e-5)
        assert hedge == pytest.approx(-float(ecm_fit.beta[4] / ecm_fit.beta[1]), abs=1e-9)

        stationary = np.column_stack(
            [np.ones(len(target) - 1), y[2:-1], dy[1:-1], dx[2:], dx[1:-1]]
        )
        fit = ols(target[1:], stationary)
        assert float(fit.beta[1] / fit.se[1]) == pytest.approx(0.3554, abs=5e-5)

    def test_the_training_subset_was_not_applied(self) -> None:
        """On the 252 days the Python run uses, the same regression gives
        -3.2032 on 245 degrees of freedom, which misses the printout."""
        stat, _beta, rows, dof = self.cadf(self.r_frame().loc[:BOOK_TRAIN_END])
        assert (rows, dof) == (250, 245)
        assert stat == pytest.approx(-3.2032228155, abs=1e-9)
        assert abs(stat - self.BOOK_T) > 0.03

    def test_the_forward_fill_changes_nothing_on_these_files(self) -> None:
        """The intersection has no gap to fill, and even an outer join filled
        forward returns the same 385 rows."""
        gld = load_close("GLD", chan=True)
        gdx = load_close("GDX", chan=True)
        inner = pd.concat([gld, gdx], axis=1, join="inner")
        outer = pd.concat([gld, gdx], axis=1, join="outer").ffill().dropna()
        assert not inner.isna().to_numpy().any()
        assert len(gld) > len(inner) == len(gdx) == 385
        pd.testing.assert_frame_equal(outer, inner, check_freq=False)
        pd.testing.assert_frame_equal(self.r_frame(), inner.set_axis(["GLD", "GDX"], axis=1))


class TestResidualCheck:
    """Which lag count the test is entitled to, read off the residuals.

    ``TestLagSettingDetour`` shows the lag count decides the verdict. The ADF
    critical values assume the fit leaves residuals with no autocorrelation,
    so this checks each fixed-lag fit's residuals at lags 1 to 10, two ways: a
    pointwise white-noise band of ``±1.96/√n``, and a Breusch-Godfrey test over
    the same ten lags. Passing means both.

    Exploratory. The sample was spent looking, after the sweep had been seen.

    Vintage: ``gld_20yr_prices_unadjusted.csv`` and
    ``gdx_20yr_prices_unadjusted.csv``, yfinance raw closes, both downloaded
    2026-08-27. Specification: the with-intercept residual spread over
    2006-05-23 to 2007-05-23, row 4 of ``docs/replication-log.md``, tested by
    ``adfuller`` at a fixed lag count with ``regression='n'``. First run on
    2026-09-26. ``tests/test_lag_residual_figure.py`` holds that the figure
    draws these numbers, and repeats some of them on purpose, for the reason
    ``tests/test_regime_figure.py`` gives.
    """

    #: Per lag count: observations, ADF statistic, Breusch-Godfrey p, and the
    #: residual lags that fall outside the band.
    PINNED = {
        0: (251, -3.2018, 0.1193, [6]),
        1: (250, -3.0875, 0.0421, [6]),
        2: (249, -2.6402, 0.0714, [3, 6]),
        3: (248, -2.4067, 0.0043, [6]),
        4: (247, -2.6394, 0.0066, [6]),
        5: (246, -2.1853, 0.0634, [6]),
        6: (245, -2.2979, 0.8395, []),
    }

    @staticmethod
    @pytest.fixture(scope="class")
    def spread() -> np.ndarray:
        df = aligned_closes("GLD", "GDX", start=BOOK_START, end=BOOK_TRAIN_END, unadjusted=True)
        return engle_granger(df["GLD"].to_numpy(float), df["GDX"].to_numpy(float)).spread

    @pytest.mark.parametrize("lags", sorted(PINNED))
    def test_the_fit_and_its_residuals(self, spread: np.ndarray, lags: int) -> None:
        nobs, stat, bg_p, outside = self.PINNED[lags]
        check = residual_check(spread, lags)

        assert check.nobs == nobs
        assert check.adf_stat == pytest.approx(stat, abs=5e-5)
        assert check.breusch_godfrey_p == pytest.approx(bg_p, abs=5e-5)
        assert check.outside == outside
        assert len(check.autocorrelation) == RESIDUAL_LAGS

    @pytest.mark.parametrize("lags", sorted(PINNED))
    def test_the_statistic_is_the_one_the_replication_computes(
        self, spread: np.ndarray, lags: int
    ) -> None:
        """The check reaches the ADF through ``statsmodels`` because it needs
        the fitted regression, and the replication reaches it through
        ``ithildincore``. They have to be the same test, or the check reads
        the residuals of a fit nobody reported."""
        stat, _nobs = adf_tstat(spread, lags=lags, constant=False)
        assert residual_check(spread, lags).adf_stat == pytest.approx(stat, abs=1e-10)

    def test_the_band_at_the_books_lag_count(self, spread: np.ndarray) -> None:
        assert residual_check(spread, 1).band == pytest.approx(0.1240, abs=5e-5)

    def test_the_lag_six_autocorrelation_survives_until_six_lags(self, spread: np.ndarray) -> None:
        at_six = [float(residual_check(spread, k).autocorrelation[5]) for k in range(7)]
        assert at_six == pytest.approx(
            [0.1631, 0.1668, 0.1764, 0.1546, 0.1551, 0.1477, 0.0100], abs=5e-5
        )

    def test_two_lags_also_leave_one_at_lag_three(self, spread: np.ndarray) -> None:
        assert residual_check(spread, 2).autocorrelation[2] == pytest.approx(-0.1331, abs=5e-5)

    def test_the_books_lag_count_fails_the_residual_check(self, spread: np.ndarray) -> None:
        """One lag is the count behind Chan's better-than-90% verdict. The ADF
        rejects there and the residuals fail Breusch-Godfrey at 10%."""
        check = residual_check(spread, 1)
        assert check.adf_stat < EG_CRIT_N2["10%"]
        assert check.breusch_godfrey_p < 0.10

    def test_which_horizons_the_breusch_godfrey_verdict_survives(self, spread: np.ndarray) -> None:
        """The ten-lag horizon is a choice, so this asks what every horizon from
        one to ten says at the 10% cut. The one-lag fit fails at every horizon
        from two up, six lags pass at all ten, and zero lags is the fit whose
        verdict turns on the choice, failing only at six and seven."""

        def fails(k: int) -> list[int]:
            return [
                h
                for h in range(1, RESIDUAL_LAGS + 1)
                if residual_check(spread, k, horizon=h).breusch_godfrey_p < 0.10
            ]

        assert fails(1) == list(range(2, 11))
        assert fails(6) == []
        assert fails(0) == [6, 7]
        assert residual_check(spread, 1, horizon=1).breusch_godfrey_p == pytest.approx(
            0.1369, abs=5e-5
        )

    def test_at_five_percent_breusch_godfrey_alone_passes_more_fits(
        self, spread: np.ndarray
    ) -> None:
        """The cut is a choice too. At 5% the test alone lets through zero, two
        and five lags, still fails one, and leaves the band as what keeps the
        first three out."""
        passing = [k for k in range(7) if residual_check(spread, k).breusch_godfrey_p > 0.05]
        assert passing == [0, 2, 5, 6]
        assert all(residual_check(spread, k).outside == [6] for k in (0, 5))

    def test_six_is_the_first_lag_count_whose_residuals_pass(self, spread: np.ndarray) -> None:
        """Zero lags clears Breusch-Godfrey and not the band, which is why both
        are asked. At six lags the test no longer rejects."""

        def passes(k: int) -> bool:
            check = residual_check(spread, k)
            return check.breusch_godfrey_p > 0.10 and not check.outside

        assert [passes(k) for k in range(7)] == [False] * 6 + [True]
        assert residual_check(spread, 6).adf_stat > EG_CRIT_N2["10%"]


class TestResidualCheckOnChansFiles:
    """The Chapter 3 residual check again, on the files Chan's figures land on.

    ``TestResidualCheck`` runs on the 2026 closes, where the one-lag fit's
    lag-6 autocorrelation sits outside the band by little enough that a
    different vintage could move it inside. Chan's own files are the vintage
    that matters, because ``TestChansPythonRun`` reproduces his Python printout
    on them. The shape holds there. The one-lag fit fails both halves of the
    check, six lags is the first count that passes, and the test does not
    reject at six. The six-lag fit is also the one ``coint`` runs at its
    defaults, so the statistic Chan distrusted is the one whose residuals pass.

    Exploratory, for the reason ``TestResidualCheck`` gives, and run after it
    had been seen.

    Vintage: ``gld_chan.csv`` and ``gdx_chan.csv``, the adjusted-close columns
    of Chan's companion ``GLD.xls`` and ``GDX.xls``, last saved 2007-12-02.
    Specification: the with-intercept residual spread over 2006-05-23 to
    2007-05-23, 252 rows, tested by ``adfuller`` at a fixed lag count with
    ``regression='n'``, with the band and the Breusch-Godfrey horizon at
    :data:`~chan.pair_cointegration.RESIDUAL_LAGS`. First pinned on 2026-10-02.
    """

    #: Per lag count: observations, ADF statistic, Breusch-Godfrey p, and the
    #: residual lags that fall outside the band.
    PINNED = {
        0: (251, -3.2975, 0.1263, [6]),
        1: (250, -3.1780, 0.0460, [6]),
        2: (249, -2.7187, 0.0731, [3, 6]),
        3: (248, -2.4857, 0.0047, [6]),
        4: (247, -2.7241, 0.0072, [6]),
        5: (246, -2.2571, 0.0621, [6]),
        6: (245, -2.3591, 0.8284, []),
    }

    @staticmethod
    @pytest.fixture(scope="class")
    def closes() -> pd.DataFrame:
        return aligned_closes("GLD", "GDX", chan=True, start=BOOK_START, end=BOOK_TRAIN_END)

    def test_every_lag_count_up_to_the_first_pass_is_pinned(self) -> None:
        assert sorted(self.PINNED) == list(range(7))

    @staticmethod
    @pytest.fixture(scope="class")
    def spread(closes: pd.DataFrame) -> np.ndarray:
        return engle_granger(closes["GLD"].to_numpy(float), closes["GDX"].to_numpy(float)).spread

    @pytest.mark.parametrize("lags", sorted(PINNED))
    def test_the_fit_and_its_residuals(self, spread: np.ndarray, lags: int) -> None:
        nobs, stat, bg_p, outside = self.PINNED[lags]
        check = residual_check(spread, lags)

        assert check.nobs == nobs
        assert check.adf_stat == pytest.approx(stat, abs=5e-5)
        assert check.breusch_godfrey_p == pytest.approx(bg_p, abs=5e-5)
        assert check.outside == outside
        assert len(check.autocorrelation) == RESIDUAL_LAGS

    def test_the_lag_six_bar_stays_outside_at_the_books_lag_count(self, spread: np.ndarray) -> None:
        """The bar the caveat in ``TestResidualCheck``'s vintage was about. On
        Chan's files it stays outside the same band, at 0.1659 against the 2026
        closes' 0.1668, so the other vintage moves it slightly and not inside."""
        check = residual_check(spread, 1)
        assert check.band == pytest.approx(0.1240, abs=5e-5)
        assert float(check.autocorrelation[5]) == pytest.approx(0.1659, abs=5e-5)

    def test_the_books_lag_count_fails_at_every_horizon_from_two(self, spread: np.ndarray) -> None:
        def fails(k: int) -> list[int]:
            return [
                h
                for h in range(1, RESIDUAL_LAGS + 1)
                if residual_check(spread, k, horizon=h).breusch_godfrey_p < 0.10
            ]

        assert fails(1) == list(range(2, 11))
        assert fails(6) == []
        assert residual_check(spread, 1, horizon=1).breusch_godfrey_p == pytest.approx(
            0.1423, abs=5e-5
        )

    def test_six_is_the_first_lag_count_whose_residuals_pass(self, spread: np.ndarray) -> None:
        """The band alone would give this list, because every fit from zero to
        five leaves lag 6 outside it. So the Breusch-Godfrey half is pinned on
        its own: at 10% it fails one to five lags and passes zero and six."""

        def passes(k: int) -> bool:
            check = residual_check(spread, k)
            return check.breusch_godfrey_p > 0.10 and not check.outside

        assert [passes(k) for k in range(7)] == [False] * 6 + [True]
        assert [residual_check(spread, k).breusch_godfrey_p > 0.10 for k in range(7)] == [
            True,
            False,
            False,
            False,
            False,
            False,
            True,
        ]
        assert residual_check(spread, 1).adf_stat < EG_CRIT_N2["10%"]
        assert residual_check(spread, 6).adf_stat > EG_CRIT_N2["10%"]

    def test_the_passing_fit_is_the_one_coint_runs(
        self, closes: pd.DataFrame, spread: np.ndarray
    ) -> None:
        """Chan's Python run picks six lags by AIC, so its printed statistic is
        the six-lag fit's, to the last digit."""
        stat = coint(closes["GLD"], closes["GDX"])[0]
        assert residual_check(spread, 6).adf_stat == pytest.approx(stat, abs=1e-12)
        assert stat == pytest.approx(TestChansPythonRun.BOOK_T, abs=1e-9)


class TestResidualCheckChapter7:
    """The same residual check on the longer Chapter 7 window, on two vintages.

    Row 3 of ``docs/replication-log.md`` is this window on the yfinance raw
    closes, and ``TestGldGdxChanArchive`` is the same window on Chan's own
    files. Both reject at one lag. This asks what each lag count leaves in the
    residuals, and what the test says at the first one that passes.

    The answer differs from the Chapter 3 window. Every fit from zero lags to
    nine leaves an autocorrelation at residual lag 10 outside the band, and the
    one-lag fit also fails Breusch-Godfrey, as do six other counts from zero to
    nine. With the band reading ten bars, ten lags is the first count that
    passes, and the test still rejects there. Which count passes first moves
    with how many bars the band reads, because the decisive bar is its last
    one. At every setting tried, the first fit that passes rejects at 10% or
    better on both vintages. So the check leaves the rejection standing, at
    better than 90% rather than the better than 95% Chan reports.

    Exploratory. The sample was spent looking, after the Chapter 3 check had
    been seen.

    Vintages: ``gld_chan.csv`` and ``gdx_chan.csv``, the adjusted-close columns
    of Chan's companion ``GLD.xls`` and ``GDX.xls``, last saved 2007-12-02; and
    ``gld_20yr_prices_unadjusted.csv`` and ``gdx_20yr_prices_unadjusted.csv``,
    yfinance raw closes, both downloaded 2026-08-27. Specification: the
    with-intercept residual spread over 2006-05-23 to 2007-11-30, 385
    observations, tested by ``adfuller`` at a fixed lag count with
    ``regression='n'``. First run on 2026-09-28.
    """

    #: The 5% critical value Chan's MATLAB printed, quoted at Kindle location
    #: 3718 and kept in row 3 of the replication log's verdicts. It survives
    #: only as highlight text, so nothing else in the tree carries it.
    MATLAB_5PCT = -3.380

    #: Per vintage and lag count: observations, ADF statistic, Breusch-Godfrey
    #: p, the residual lags that fall outside the band, and the autocorrelation
    #: at residual lag 10.
    PINNED = {
        "chan": {
            0: (384, -3.6981, 0.1068, [10], 0.1463),
            1: (383, -3.5171, 0.0337, [10], 0.1435),
            2: (382, -3.4232, 0.0819, [10], 0.1444),
            3: (381, -3.0458, 0.0153, [10], 0.1342),
            4: (380, -3.1378, 0.0116, [10], 0.1410),
            5: (379, -2.8030, 0.0511, [10], 0.1239),
            6: (378, -2.8562, 0.3035, [10], 0.1161),
            7: (377, -2.7189, 0.1082, [10], 0.1111),
            8: (376, -2.8054, 0.0216, [10], 0.1155),
            9: (375, -2.7999, 0.0043, [10], 0.1180),
            10: (374, -3.3580, 0.3896, [], -0.0037),
            11: (373, -3.2667, 0.2923, [], -0.0030),
            12: (372, -3.2419, 0.0348, [], -0.0047),
        },
        "raw": {
            0: (384, -3.6314, 0.1064, [10], 0.1472),
            1: (383, -3.4544, 0.0325, [10], 0.1443),
            2: (382, -3.3654, 0.0809, [10], 0.1453),
            3: (381, -2.9911, 0.0149, [10], 0.1352),
            4: (380, -3.0794, 0.0115, [10], 0.1417),
            5: (379, -2.7533, 0.0526, [10], 0.1244),
            6: (378, -2.8141, 0.3104, [10], 0.1167),
            7: (377, -2.6809, 0.1125, [10], 0.1117),
            8: (376, -2.7568, 0.0182, [10], 0.1158),
            9: (375, -2.7465, 0.0039, [10], 0.1181),
            10: (374, -3.2965, 0.3861, [], -0.0040),
            11: (373, -3.2061, 0.2917, [], -0.0033),
            12: (372, -3.1752, 0.0353, [], -0.0050),
        },
    }

    @staticmethod
    @pytest.fixture(scope="class")
    def spreads() -> dict[str, np.ndarray]:
        def spread(**basis: bool) -> np.ndarray:
            df = aligned_closes("GLD", "GDX", start=BOOK_START, end=BOOK_END, **basis)
            return engle_granger(df["GLD"].to_numpy(float), df["GDX"].to_numpy(float)).spread

        return {"chan": spread(chan=True), "raw": spread(unadjusted=True)}

    @staticmethod
    def passes(spread: np.ndarray, lags: int) -> bool:
        check = residual_check(spread, lags)
        return check.breusch_godfrey_p > 0.10 and not check.outside

    @pytest.mark.parametrize(
        ("vintage", "lags"),
        [(v, k) for v in ("chan", "raw") for k in range(13)],
    )
    def test_the_fit_and_its_residuals(
        self, spreads: dict[str, np.ndarray], vintage: str, lags: int
    ) -> None:
        nobs, stat, bg_p, outside, at_ten = self.PINNED[vintage][lags]
        check = residual_check(spreads[vintage], lags)

        assert check.lags == lags
        assert check.nobs == nobs
        assert check.adf_stat == pytest.approx(stat, abs=5e-5)
        assert check.breusch_godfrey_p == pytest.approx(bg_p, abs=5e-5)
        assert check.outside == outside
        assert check.autocorrelation[9] == pytest.approx(at_ten, abs=5e-5)

    def test_the_band_at_the_books_lag_count(self, spreads: dict[str, np.ndarray]) -> None:
        for spread in spreads.values():
            assert residual_check(spread, 1).band == pytest.approx(0.1002, abs=5e-5)
            assert residual_check(spread, 10).band == pytest.approx(0.1013, abs=5e-5)

    @pytest.mark.parametrize("vintage", ["chan", "raw"])
    def test_the_books_lag_count_fails_the_residual_check(
        self, spreads: dict[str, np.ndarray], vintage: str
    ) -> None:
        """At one lag the ADF rejects at 5% and the residuals fail both halves
        of the check, as they do on the Chapter 3 window."""
        check = residual_check(spreads[vintage], 1)
        assert check.adf_stat < EG_CRIT_N2["5%"]
        assert check.breusch_godfrey_p < 0.10
        assert check.outside == [10]

    @pytest.mark.parametrize("vintage", ["chan", "raw"])
    def test_ten_is_the_first_lag_count_whose_residuals_pass(
        self, spreads: dict[str, np.ndarray], vintage: str
    ) -> None:
        """With the band reading ten bars, ten lags absorbs the lag-10
        autocorrelation the way six lags absorbs the lag-6 one on Chapter 3,
        and there the test still rejects at 10%.

        The band decides every fit from zero to nine, so the Breusch-Godfrey
        half of the rule is first tested at twelve lags, which it fails. No lag
        count here has a p between 0.05 and 0.10 that the band lets through, so
        this data cannot tell a 10% cut from a 5% one."""
        spread = spreads[vintage]
        assert [self.passes(spread, k) for k in range(13)] == [False] * 10 + [True, True, False]
        assert residual_check(spread, 10).adf_stat < EG_CRIT_N2["10%"]

    @pytest.mark.parametrize(
        ("bars", "first", "chan_stat", "raw_stat"),
        [
            (9, 0, -3.6981, -3.6314),
            (10, 10, -3.3580, -3.2965),
            (15, 10, -3.3580, -3.2965),
            (16, 16, -3.1865, -3.1234),
            (20, 16, -3.1865, -3.1234),
        ],
    )
    def test_the_first_passing_fit_moves_with_the_bars_and_still_rejects(
        self,
        spreads: dict[str, np.ndarray],
        bars: int,
        first: int,
        chan_stat: float,
        raw_stat: float,
    ) -> None:
        """How many autocorrelations the band reads is a choice, like the
        Breusch-Godfrey horizon. Nine bars stop short of the lag-10 bar and let
        zero lags through. Sixteen reach a lag-16 bar that ten and eleven lags
        leave behind. Whichever fit passes first, it rejects at 10% on both
        vintages. The Breusch-Godfrey horizon stays at ten throughout."""

        def first_pass(spread: np.ndarray) -> int:
            for k in range(21):
                check = residual_check(spread, k, bars=bars)
                if check.breusch_godfrey_p > 0.10 and not check.outside:
                    return k
            raise AssertionError("no lag count up to 20 passes")

        for vintage, stat in (("chan", chan_stat), ("raw", raw_stat)):
            spread = spreads[vintage]
            k = first_pass(spread)
            assert k == first
            check = residual_check(spread, k, bars=bars)
            assert check.adf_stat == pytest.approx(stat, abs=5e-5)
            assert check.adf_stat < EG_CRIT_N2["10%"]

    def test_the_level_at_ten_lags_depends_on_the_table(
        self, spreads: dict[str, np.ndarray]
    ) -> None:
        """At ten lags the yfinance closes miss 5% under both tables. Chan's
        files clear ``EG_CRIT_N2``'s -3.34 by 0.018 and miss the -3.380 his
        MATLAB printed by 0.022, so the 5% level rests on the table. What
        both vintages clear under both tables is 10%."""
        chan = residual_check(spreads["chan"], 10).adf_stat
        raw = residual_check(spreads["raw"], 10).adf_stat
        assert chan < EG_CRIT_N2["5%"]
        assert chan == pytest.approx(EG_CRIT_N2["5%"] - 0.018, abs=5e-4)
        assert chan > self.MATLAB_5PCT
        assert chan == pytest.approx(self.MATLAB_5PCT + 0.022, abs=5e-4)
        assert raw > EG_CRIT_N2["5%"]
        assert max(chan, raw) < EG_CRIT_N2["10%"]

    @pytest.mark.parametrize("vintage", ["chan", "raw"])
    def test_zero_lags_fails_only_on_the_lag_ten_bar(
        self, spreads: dict[str, np.ndarray], vintage: str
    ) -> None:
        """Zero lags is what ``autolag='aic'`` and ``autolag='bic'`` pick here.
        It clears Breusch-Godfrey and rejects at 5%, and one bar at lag 10 keeps
        it out. That bar stays outside even a band widened for reading ten bars
        at once, 2.807/√n."""
        check = residual_check(spreads[vintage], 0)
        assert check.breusch_godfrey_p > 0.10
        assert check.outside == [10]
        assert check.adf_stat < EG_CRIT_N2["5%"]
        assert abs(check.autocorrelation[9]) > 2.807 / np.sqrt(check.nobs)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            picks = [
                int(adfuller(spreads[vintage], autolag=rule, regression="n")[2])
                for rule in ("aic", "bic")
            ]
        assert picks == [0, 0]


# ============================================================
# Layer 7 -- the vintage premise, as far as one download date shows
# ============================================================


class TestAdjustedCloseMovesWithTheDownloadDate:
    """The adjusted half of the vintage premise.

    An adjusted close folds every later dividend back into the history, so the
    same 2006 trading day reads lower in the adjusted series than in the raw
    one. The second case below sets two adjusted vintages taken nineteen years
    apart against each other, Chan's 2007 file and a 2026 download, and shows
    the series moving under itself. The raw half, that two downloads of a
    symbol that has not split return the same as-traded close, is
    ``TestRawCloseAcrossTwoDownloads`` in ``tests/test_vintage_overlap.py``.
    Together they are the premise test
    [issue 4](https://github.com/l3a0/quantitative-trading/issues/4) asked for.

    Four prose surfaces quote the gap as about 15%, so a re-pin here moves all
    four. ``src/chan/series.py`` says it against raw, which the first test
    below measures. ``docs/design.md``, ``blog/gld-gdx-cointegration-lessons.md``
    and ``docs/gld-gdx-cointegration-lessons.html`` say it against the number
    Chan saw, which the second measures on his own file. The prose rounds both
    to a whole percent.
    """

    def test_gdx_2006_adjusted_sits_about_fifteen_percent_below_raw(self) -> None:
        """Vintages: ``gdx_20yr_prices.csv`` against
        ``gdx_20yr_prices_unadjusted.csv``, both downloaded from yfinance on
        2026-08-27. Specification: the mean of adjusted over raw, less one, on
        the 155 rows they share in 2006, 2006-05-22 to 2006-12-29."""
        raw = load_close("GDX", unadjusted=True)
        adjusted = load_close("GDX")
        shared = raw.index.intersection(adjusted.index)
        gap = (adjusted.loc[shared] / raw.loc[shared] - 1.0).loc["2006-01-01":"2006-12-31"]

        assert len(gap) == 155
        assert float(gap.mean()) == pytest.approx(-0.1513, abs=5e-5)

    def test_gdx_adjusted_sits_about_fifteen_percent_below_chans_own_file(self) -> None:
        """The design doc and the post compare today's adjusted price with the
        one Chan saw rather than with raw, so this measures that comparison
        directly.

        Vintages: ``gdx_20yr_prices.csv``, downloaded from yfinance on
        2026-08-27, against ``gdx_chan.csv``, the adjusted-close column of
        Chan's companion .xls, last saved 2007-12-02. Specification: adjusted
        over Chan's file, less one, on every row they share, 2006-05-23 to
        2007-11-30. The gap is flat across that span, so its mean is the gap
        on any 2006 day the prose could mean. First pinned on 2026-10-02.
        """
        adjusted = load_close("GDX")
        chan = load_close("GDX", chan=True)
        shared = adjusted.index.intersection(chan.index)
        gap = adjusted.loc[shared] / chan.loc[shared] - 1.0

        assert float(gap.mean()) == pytest.approx(-0.1489, abs=5e-5)
        assert float(gap.max() - gap.min()) < 3e-4

    def test_chans_gdx_file_holds_one_dividend_step_off_raw(self) -> None:
        """Chan's file is what the prose means by an adjusted close near raw.
        It sits a little below raw until 2006-12-20 and on raw from 2006-12-21,
        the day yfinance's adjusted series takes its first dividend step. So
        his file folds in that one distribution and nothing later, and the rest
        of the 15% is distributions that went ex after he saved it.

        Six surfaces state the near-raw claim in words rather than a number,
        so a re-pin here is checked against them.

        1. ``src/chan/series.py``, its module docstring.
        2. ``src/chan/pair_cointegration.py``, its module docstring.
        3. ``src/chan/pair_cointegration.py``, the comment above ``BOOK_START``.
        4. ``src/chan/kelly_leverage.py``, its module docstring.
        5. ``docs/design.md``, under "The first time the fallback clause fires".
        6. ``blog/gld-gdx-cointegration-lessons.md`` and its HTML copy.

        Vintages: ``gdx_20yr_prices_unadjusted.csv`` and ``gdx_20yr_prices.csv``,
        downloaded from yfinance on 2026-08-27, against ``gdx_chan.csv``, last
        saved 2007-12-02. Specification: raw over Chan's file, less one, on
        every row they share, split at 2006-12-21. The step is the first day
        adjusted over raw moves by more than 1e-4. First pinned on 2026-10-02.
        """
        raw = load_close("GDX", unadjusted=True)
        adjusted = load_close("GDX")
        chan = load_close("GDX", chan=True)
        both = raw.index.intersection(adjusted.index)
        steps = (adjusted.loc[both] / raw.loc[both]).diff().abs()
        shared = raw.index.intersection(chan.index)
        above = raw.loc[shared] / chan.loc[shared] - 1.0
        before = above.loc[:"2006-12-20"]
        after = above.loc["2006-12-21":]

        assert str(steps[steps > 1e-4].index[0].date()) == "2006-12-21"
        assert len(before) == 148
        assert float(before.min()) > 0.0
        assert float(before.max()) == pytest.approx(0.0030, abs=5e-5)
        assert float(after.abs().max()) < 1e-6

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

    def test_the_default_run_names_a_file_and_a_date_for_each_leg(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """The basis line says which kind of series and this says which file.

        `src/chan/__init__.py` promises that every run names the vintage it read,
        and until the reader resolved one there was nothing to name. The two legs
        of the default run were downloaded 72 days apart, a gap invisible from
        `--ch7` and `--ch3`, which read the raw pair and share a date.
        """
        run("GLD", "GDX", 1)
        out = capsys.readouterr().out

        first = "GLD vintage: gld_20yr_prices.csv   yfinance adjusted, downloaded 2026-06-16"
        second = "GDX vintage: gdx_20yr_prices.csv   yfinance adjusted, downloaded 2026-08-27"

        assert first in out
        assert second in out
        # Leg order, which carries no different words and so needs its own
        # assertion. A report that prints B above A contradicts the "A = ...
        # B = ..." line three rows above it.
        assert out.index(first) < out.index(second)

    def test_a_workbook_column_is_named_as_saved_rather_than_downloaded(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Nothing was fetched on 2008-01-23. Printing that date under the word
        "downloaded" would state a wrong fact about where the series came from."""
        run("KO", "PEP", 1, origin=True, show_correlation=True, chan=True)
        out = capsys.readouterr().out

        assert "KO vintage: ko_chan.csv   chan-xls adjusted, saved 2008-01-23" in out
        assert "PEP vintage: pep_chan.csv   chan-xls adjusted, saved 2008-01-23" in out
        assert "downloaded" not in out

    def test_asking_for_chan_s_as_traded_ko_stops_with_the_reader_s_line(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """``--ko-pep --unadjusted`` asks for a column this repo does not hold.

        Before [issue 192](https://github.com/l3a0/quantitative-trading/issues/192)
        the flag was ignored under ``--ko-pep``, so the run read KO's adjusted
        column and printed the adjusted basis line beside it. Chan's SPY
        workbook now gives an as-traded column, so ``close_identity`` asks for
        ``(chan-xls, raw)`` and the reader refuses KO, which has none. The run
        exits with the reader's own sentence rather than a traceback, and prints
        no report.
        """
        monkeypatch.setattr("sys.argv", ["chan.pair_cointegration", "--ko-pep", "--unadjusted"])

        with pytest.raises(
            SystemExit, match="no committed vintage is recorded for chan-xls KO raw"
        ):
            main()
        assert "Price basis" not in capsys.readouterr().out
