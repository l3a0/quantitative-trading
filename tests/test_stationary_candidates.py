"""The pins for Chan's stationary candidates: TLT/IEF, CAD/AUD, and calendar spreads.

This file is the single authority for every number any prose surface quotes
about the three candidates. ``docs/replication-log.md`` Entry 5 carries the
fixed-income finding, Entry 6 the cross-rate verdict and Entry 15 the
calendar-spread verdicts, and each points here row by row.
``blog/usdcad-stationarity-lessons.md`` quotes the cross rate's half-life of
141.6 days, so a change to that pin moves that post too. The fixed-income
classes come first, then the cross-rate classes, then the calendar-spread
classes, each under a statement of its vintage and specification.

The fixed-income pins read one vintage pair and one specification, so both are
stated once here rather than in every docstring.

- **Vintage.** ``yfinance_tlt_raw_2002-07-30_2026-10-01_dl2026-10-02.csv`` and
  ``yfinance_ief_raw_2002-07-30_2026-10-01_dl2026-10-02.csv``, yfinance's
  ``Close`` under ``auto_adjust=False``, both downloaded 2026-10-02. The price
  basis is raw on both legs, meaning split-adjusted and not dividend-adjusted.
  A re-download moves these pins, which is the behaviour that makes them worth
  having.
- **Specification.** The with-intercept Engle-Granger regression in both
  orientations, levels, one ADF lag, the full common span of 6,083 days, and a
  rolling scan of 252-day windows stepped by 21. The residual check reads ten
  autocorrelations against the ``±1.96/√n`` band and a Breusch-Godfrey test
  over the same ten lags at the 10% cut.

Six classes.

1. ``TestTheSpan``, the joined history and the two vintages it reads.
2. ``TestBothOrientations``, the hedge, the statistic and the half-life each
   way round. Neither rejects.
3. ``TestTheResidualCheck``, which asks whether the one-lag fit earned its
   critical values. It did not, and the first fit that does is further from
   rejecting.
4. ``TestTheRollingScan``, the 278 windows each way round.
5. ``TestTheReport``, which holds the lines saying which vintage produced the
   rest, and the words the finding is not allowed to use.
6. ``TestTheRefusals``, which holds that both refusals the join can raise reach
   an operator as a line.

Exploratory, and not a replication. Chan printed no number, so nothing here is
compared against one. First run on 2026-10-02.

The cross-rate pins read one vintage and one specification too.

- **Vintage.** ``yfinance_cadaud=x_raw_2005-07-04_2026-09-30_dl2026-10-02.csv``,
  yfinance's ``Close`` under ``auto_adjust=False``, downloaded 2026-10-02, less
  the two rows dated on or after the day before that. Raw basis, which for a
  rate means the vendor's close untouched.
- **Specification.** The ADF with a constant and no trend, on the log of the
  rate, one lag, over the test window from 2007-08-06 to 2026-09-30, 4,984
  days. The residual check fits the same constant. The rolling scan is
  252-day windows stepped by 21. Tests that change one part of it, such as
  the quoting direction or the deterministic term, say which in their names.

Eleven classes and one test.

1. ``TestTheCrossRateVintage``, the file, the window it is read over, and the
   vendor's gap the window starts after.
2. ``TestTheCrossRateStatistic``, the lag-1 statistic, its half-life, that
   the quoting direction does not move it, and what dropping the constant or
   adding a trend would have done.
3. ``TestTheCrossRateResidualCheck``, which asks whether the lag-1 fit earned
   its critical values. It did not, and the first fit that does still rejects.
4. ``TestTheCrossRateVerdict``, the rule issue 135 declared and the verdict it
   gives, reproduced, and that the pair's bars would have refused it.
5. ``TestTheCrossRateScan``, the 226 windows, and how many half-lives one holds.
6. ``TestTheCrossRateReport``, which holds the vintage line, the bars, the null
   the report names, and the verdict line.
7. ``TestTheCrossRateRefusals``, which holds that a missing download reaches
   an operator as a line, and what the command runs with and without an
   argument.
8. ``TestTheUnitRootLine``, the null the report names and the level, held at
   each bar.
9. ``TestTheCheckFitsTheTermItIsGiven``, the ``regression`` keyword on
   ``residual_check``, held on a synthetic series.
10. ``TestTheWindowPower``, the simulation issue 212 declared before it ran:
    how often a series that truly reverts at the rate's half-life rejects in
    the rate's scan.
11. ``TestTheKnownMeanRule``, what a known-mean version of Chan's linear rule
    earns on the rate's half-life, set beside a 36-day half-life.

``test_measuring_reads_from_the_test_start`` holds that measuring a series
that begins before the window drops those days.

A replication under the claim route, which is still exploratory: the sample
was spent on a claim Chan stated about one named rate. First run on
2026-10-02, after the criterion was fixed on issue 135.

The calendar-spread pins read eight vintages and one specification.

- **Vintages.** EIA's NYMEX settlements for the nearest four contracts,
  ``eia_rngc1`` to ``eia_rngc4`` for natural gas and ``eia_eer-epmrr-pe1`` to
  ``pe4`` for RBOB gasoline, all downloaded 2026-10-02 on the raw basis.
  :data:`SPREAD_FILES` names each file.
- **Specification.** Every adjacent pair of delivery months whose window lies
  inside all four of a commodity's files. A pair reads every trading day both
  contracts sit in the nearest four, less a six-day guard band, and drops any
  day a file lacks. Engle-Granger on levels at one lag, near on far and far on
  near, and a pair rejects when both clear the 10% bar of -3.04. A commodity's
  share is judged against the 975th of 1,000 null shares from seed 20261003,
  and the power row reverts at a 36-day half-life from seed 20261004. Each was
  declared on issue 137 before any statistic. The null's walks were then
  corrected, after the result and on the owner's ruling, to correlate as the
  files' two legs do, and the declared null's figures are pinned beside it.

Ten classes. Most read the module fixture ``spreads``, which runs both batches
once.

1. ``TestTheCalendarSpreadVintages``, the eight files, and the three days the
   calendar used to count closed on which every file settled.
2. ``TestTheContractNumber``, which file holds a contract, read by delivery
   year rather than by the day's year.
3. ``TestTheExpiryMapAgainstTheFiles``, how often the files hand over on the
   day each rule says and on a day either side.
4. ``TestThePairs``, the declared set, the days each pair reads, and that a
   rule one day wrong reads the same prices on every day both keep.
5. ``TestTheBatchedStatistic``, the simulations' closed form held to the
   engine on simulated paths and on every real pair.
6. ``TestTheCalendarSpreadVerdicts``, the criterion, the correction, and the
   verdicts under both nulls.
7. ``TestTheCalendarSpreadNull``, how the null draws and reads its walks.
8. ``TestTheCalendarSpreadDescriptions``, each orientation alone, the residual
   check and the power row, which decide nothing.
9. ``TestTheCalendarSpreadReport``, the vintage lines and the verdict lines.
10. ``TestTheCalendarSpreadCommandLine``, what the command runs and refuses.

A replication under the claim route, so exploratory. The batch takes about
seven seconds. First run on 2026-10-03, after the criterion was fixed on
issue 137.
"""

from __future__ import annotations

import contextlib
import dataclasses
import io
import math
import re
from datetime import date
from decimal import Decimal

import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm
from ithildincore.timeseries import ADF_CRIT_CONST, EG_CRIT_N2, adf_tstat, ou_half_life
from statsmodels.tsa.stattools import adfuller

from chan.commodity_seasonals import june_contract_number
from chan.futures import (
    NATURAL_GAS_CONTRACTS,
    RBOB_CONTRACTS,
    UNSCHEDULED_CLOSURES,
    Product,
    contract_number,
    handover_fit,
    is_trading_day,
    last_business_day,
    month_step,
    next_trading_day,
    ng_last_trade,
    rbob_last_trade,
    settlements,
    shifted,
    trading_days,
)
from chan.pair_cointegration import ResidualCheck, engle_granger, residual_check
from chan.series import WindowCrossesScaleBreak, aligned_closes, load_vintage
from chan.stationary_candidates import (
    CROSS_RATE,
    GAP,
    INTERMEDIATE,
    LAGS,
    LONG,
    NULL_RANK,
    NULL_SEED,
    NULL_SETS,
    ORIENTATIONS,
    POWER_PATHS,
    POWER_SEED,
    RESIDUAL_PASS_P,
    SPREAD_LEVEL,
    SPREAD_POWER_HALF_LIFE,
    SPREAD_POWER_SEED,
    SPREAD_PRODUCTS,
    TEST_START,
    TRADING_DAYS,
    WINDOW,
    CalendarSpread,
    CrossRate,
    Orientation,
    _orientation,
    batched_engle_granger,
    calendar_spread,
    cross_rate,
    first_passing,
    fixed_income,
    guard_band,
    known_mean_rule,
    leg_correlation,
    main,
    measure_cross_rate,
    null_shares,
    report_calendar_spread,
    report_cross_rate,
    residuals_pass,
    rolling_adf,
    run,
    run_cross_rate,
    schwert_ceiling,
    simulated_paths,
    spread_pair,
    spread_window,
    unit_root_line,
    window_power,
)
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import committed_copy

TLT_FILE = "yfinance_tlt_raw_2002-07-30_2026-10-01_dl2026-10-02.csv"
IEF_FILE = "yfinance_ief_raw_2002-07-30_2026-10-01_dl2026-10-02.csv"


@pytest.fixture(scope="module")
def measured() -> tuple[pd.DataFrame, dict[str, Orientation]]:
    closes, orientations = fixed_income()
    return closes, {o.dependent: o for o in orientations}


class TestTheSpan:
    def test_the_join_keeps_every_day_of_both_legs(
        self, measured: tuple[pd.DataFrame, dict[str, Orientation]]
    ) -> None:
        """The vendor's history of both begins on one day and carries the same
        trading days after it, so the inner join drops nothing and the span is
        the full history the download returned."""
        closes, _ = measured
        assert len(closes) == 6083
        assert str(closes.index[0].date()) == "2002-07-30"
        assert str(closes.index[-1].date()) == "2026-10-01"
        assert list(closes.columns) == [LONG, INTERMEDIATE]

    def test_it_reads_the_two_raw_vintages(
        self, measured: tuple[pd.DataFrame, dict[str, Orientation]]
    ) -> None:
        closes, _ = measured
        entries = closes.attrs["vintages"]
        assert [e.path for e in entries] == [TLT_FILE, IEF_FILE]
        assert {e.price_basis for e in entries} == {"raw"}
        assert {e.download_date for e in entries} == {"2026-10-02"}

    def test_both_orientations_run_and_in_order(self) -> None:
        assert ORIENTATIONS == (("TLT", "IEF"), ("IEF", "TLT"))


class TestBothOrientations:
    """The full-span test each way round, at one lag."""

    #: Per dependent leg: hedge, intercept, ADF statistic, observations, half-life.
    PINNED = {
        "TLT": (1.8632, -74.8326, -2.3887, 6081, 333.2),
        "IEF": (0.4771, 46.6023, -2.3168, 6081, 376.4),
    }

    @pytest.mark.parametrize("dependent", sorted(PINNED))
    def test_the_fit(
        self, measured: tuple[pd.DataFrame, dict[str, Orientation]], dependent: str
    ) -> None:
        hedge, intercept, stat, nobs, half_life = self.PINNED[dependent]
        fit = measured[1][dependent].fit
        assert fit.hedge_ratio == pytest.approx(hedge, abs=5e-5)
        assert fit.intercept == pytest.approx(intercept, abs=5e-5)
        assert fit.adf_stat == pytest.approx(stat, abs=5e-5)
        assert fit.nobs == nobs
        assert fit.half_life == pytest.approx(half_life, abs=5e-2)

    @pytest.mark.parametrize("dependent", sorted(PINNED))
    def test_neither_orientation_rejects_even_at_ten_percent(
        self, measured: tuple[pd.DataFrame, dict[str, Orientation]], dependent: str
    ) -> None:
        """The finding. The statistics sit 0.65 and 0.72 short of the 10% bar, so
        the orientation the test would otherwise have chosen decides nothing
        here."""
        short = measured[1][dependent].fit.adf_stat - EG_CRIT_N2["10%"]
        assert short == pytest.approx({"TLT": 0.6513, "IEF": 0.7232}[dependent], abs=5e-5)

    def test_the_two_orientations_differ_by_less_than_a_tenth(
        self, measured: tuple[pd.DataFrame, dict[str, Orientation]]
    ) -> None:
        """The two orientations sit 0.0719 apart, so this pair is not a case
        where the choice of dependent leg could have turned the finding. Entry 5
        of the replication log quotes the GLD/GDX comparison, measured on issue
        136 and pinned nowhere, since pinning the engine's asymmetry is issue
        127's."""
        gap = measured[1]["TLT"].fit.adf_stat - measured[1]["IEF"].fit.adf_stat
        assert gap == pytest.approx(-0.0719, abs=5e-5)


class TestTheResidualCheck:
    """Whether the one-lag fit earned its critical values, each way round."""

    def test_the_ceiling(self) -> None:
        """Schwert's rule, rounded up. 33 at GLD/GDX's 5,099 days, which is the
        figure issue 136 measured before this pair was downloaded, and 34 here."""
        assert schwert_ceiling(5099) == 33
        assert schwert_ceiling(6083) == 34

    #: Per dependent leg: the Breusch-Godfrey p at one lag and the residual lags
    #: outside the band.
    AT_ONE_LAG = {
        "TLT": (0.0000, [2, 3, 4, 5, 6, 7, 8, 9, 10]),
        "IEF": (0.0000, [2, 3, 4, 5, 7, 8, 9, 10]),
    }

    @pytest.mark.parametrize("dependent", sorted(AT_ONE_LAG))
    def test_the_one_lag_fit_fails_it(
        self, measured: tuple[pd.DataFrame, dict[str, Orientation]], dependent: str
    ) -> None:
        bg_p, outside = self.AT_ONE_LAG[dependent]
        check = measured[1][dependent].at_lag
        assert check.lags == LAGS
        assert check.breusch_godfrey_p == pytest.approx(bg_p, abs=5e-5)
        assert check.outside == outside
        assert not residuals_pass(check)

    #: Per dependent leg: the first passing lag count, its ADF statistic and its
    #: Breusch-Godfrey p.
    FIRST_PASSING = {
        "TLT": (31, -1.5677, 0.1352),
        "IEF": (31, -1.5387, 0.3223),
    }

    @pytest.mark.parametrize("dependent", sorted(FIRST_PASSING))
    def test_the_first_fit_that_passes_is_further_from_rejecting(
        self, measured: tuple[pd.DataFrame, dict[str, Orientation]], dependent: str
    ) -> None:
        lags, stat, bg_p = self.FIRST_PASSING[dependent]
        o = measured[1][dependent]
        assert o.ceiling == 34
        assert o.passing is not None
        assert o.passing.lags == lags
        assert o.passing.adf_stat == pytest.approx(stat, abs=5e-5)
        assert o.passing.breusch_godfrey_p == pytest.approx(bg_p, abs=5e-5)
        assert o.passing.outside == []
        assert o.passing.adf_stat > o.fit.adf_stat

    def test_a_search_that_finds_nothing_says_none(self) -> None:
        """The ceiling is a stop, not a suggestion. On GLD/GDX's full raw
        history the first passing count is 21 for GLD on GDX, so a ceiling of
        20 finds nothing and the search returns ``None`` rather than reaching
        past it."""
        df = aligned_closes("GLD", "GDX", unadjusted=True)
        spread = engle_granger(df["GLD"].to_numpy(float), df["GDX"].to_numpy(float)).spread
        assert first_passing(spread, 20) is None
        found = first_passing(spread, 21)
        assert found is not None
        assert found.lags == 21

    #: Per dependent leg: the first lag count whose ten autocorrelations all sit
    #: inside the band.
    BAND_CLEARS = {"TLT": 9, "IEF": 10}

    @pytest.mark.parametrize("dependent", sorted(BAND_CLEARS))
    def test_the_breusch_godfrey_half_is_what_holds_the_count_at_31(
        self, measured: tuple[pd.DataFrame, dict[str, Orientation]], dependent: str
    ) -> None:
        """On GLD/GDX the band was the half that decided. Here every bar is
        inside it from 9 or 10 lags on, and every fit from there to 30 still
        fails the Breusch-Godfrey test. A pass that read the band alone would
        stop 22 and 21 lag counts early, at a statistic nearer rejection."""
        o = measured[1][dependent]
        checks = [residual_check(o.fit.spread, k) for k in range(o.passing.lags)]
        clean = [c.lags for c in checks if not c.outside]
        first_clean = self.BAND_CLEARS[dependent]
        assert clean == list(range(first_clean, o.passing.lags))
        assert all(checks[k].breusch_godfrey_p <= 0.10 for k in clean)
        assert not any(residuals_pass(c) for c in checks)
        assert o.passing.lags - first_clean == {"TLT": 22, "IEF": 21}[dependent]
        assert checks[first_clean].adf_stat < o.passing.adf_stat

    def test_a_clean_breusch_godfrey_p_does_not_pass_with_a_bar_outside_the_band(self) -> None:
        """No fit on either pair has a Breusch-Godfrey p above the cut while a
        bar sits outside the band, so the real data cannot hold the band half
        of the predicate. These two checks do. Dropping either half lets one of
        them through."""
        quiet = np.zeros(10)
        one_out = quiet.copy()
        one_out[5] = 0.5  # the band at 400 observations is 1.96 / 20, or 0.098
        assert ResidualCheck(1, -2.0, 400, one_out, 0.50).outside == [6]
        assert not residuals_pass(ResidualCheck(1, -2.0, 400, one_out, 0.50))
        assert not residuals_pass(ResidualCheck(1, -2.0, 400, quiet, 0.05))
        assert residuals_pass(ResidualCheck(1, -2.0, 400, quiet, 0.50))

    def test_the_cut_is_ten_percent_and_a_p_on_it_fails(self) -> None:
        """The cut Entry 1 uses. TLT's passing p is 0.1352, so a cut moved
        anywhere below that leaves every pin above green, and only this holds
        it."""
        quiet = np.zeros(10)
        assert RESIDUAL_PASS_P == 0.10
        assert not residuals_pass(ResidualCheck(1, -2.0, 400, quiet, 0.10))
        assert residuals_pass(ResidualCheck(1, -2.0, 400, quiet, 0.1001))

    def test_the_search_starts_at_zero_lags(self) -> None:
        """Zero lags never passes on either pair, so the real data cannot hold
        the start of the range. Seeded white noise passes there."""
        found = first_passing(np.random.default_rng(0).standard_normal(2000), 5)
        assert found is not None
        assert found.lags == 0

    def test_the_search_reaches_the_ceiling_it_reports(
        self, measured: tuple[pd.DataFrame, dict[str, Orientation]], monkeypatch
    ) -> None:
        """The first pass at 31 sits below the ceiling of 34, so the real data
        cannot tell a search stopping at 33 from one reaching 34. A check that
        never passes makes the search run to its end, and the last lag it tries
        has to be the ceiling the report prints."""
        import chan.stationary_candidates as candidates

        tried: list[int] = []

        def never_passes(spread, lags, **_):
            tried.append(lags)
            return ResidualCheck(lags, 0.0, 400, np.zeros(10), 0.0)

        monkeypatch.setattr(candidates, "residual_check", never_passes)
        o = candidates.measure_orientation(measured[0], LONG, INTERMEDIATE)
        assert o.passing is None
        assert max(tried) == o.ceiling == 34


class TestTheRollingScan:
    """The 278 one-year windows each way round. They describe the span, and no
    window in them is a finding on its own."""

    #: Per dependent leg: windows clearing 10%, windows clearing 5%, windows
    #: whose spread does not mean-revert.
    PINNED = {
        "TLT": (56, 33, 2),
        "IEF": (51, 29, 2),
    }

    @pytest.mark.parametrize("dependent", sorted(PINNED))
    def test_the_counts(
        self, measured: tuple[pd.DataFrame, dict[str, Orientation]], dependent: str
    ) -> None:
        clear10, clear5, never = self.PINNED[dependent]
        scan = measured[1][dependent].scan
        assert len(scan.adf_stat) == 278 == math.floor((6083 - 252) / 21) + 1
        assert int((scan.adf_stat < EG_CRIT_N2["10%"]).sum()) == clear10
        assert int((scan.adf_stat < EG_CRIT_N2["5%"]).sum()) == clear5
        assert int(np.isinf(scan.half_life).sum()) == never

    def test_the_windows_span_the_history(
        self, measured: tuple[pd.DataFrame, dict[str, Orientation]]
    ) -> None:
        closes, by = measured
        ends = closes.index[by["TLT"].scan.end_idx]
        assert str(ends[0].date()) == "2003-07-29"
        assert str(ends[-1].date()) == "2026-09-11"

    @pytest.mark.parametrize("dependent", sorted(PINNED))
    def test_rejections_cluster_in_two_stretches(
        self, measured: tuple[pd.DataFrame, dict[str, Orientation]], dependent: str
    ) -> None:
        """Just over half of the windows that clear 10% end in 2003-04 or
        2020-21, four of the twenty-four calendar years the scan covers. The
        rest are scattered across the other years, none with more than six."""
        closes, by = measured
        scan = by[dependent].scan
        years = closes.index[scan.end_idx[scan.adf_stat < EG_CRIT_N2["10%"]]].year
        stretches = [2003, 2004, 2020, 2021]
        clustered = int(np.isin(years, stretches).sum())
        assert clustered == {"TLT": 30, "IEF": 29}[dependent]
        assert 2 * clustered > len(years)
        elsewhere = years[~np.isin(years, stretches)]
        assert max(np.unique(elsewhere, return_counts=True)[1]) <= 6


class TestTheReport:
    @staticmethod
    @pytest.fixture(scope="class")
    def out() -> str:
        import contextlib
        import io

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            run()
        return buffer.getvalue()

    def test_it_names_the_basis_and_each_leg_s_file_and_date(self, out: str) -> None:
        first = f"TLT vintage: {TLT_FILE}   yfinance raw, downloaded 2026-10-02"
        second = f"IEF vintage: {IEF_FILE}   yfinance raw, downloaded 2026-10-02"
        assert "Price basis: raw closes, adjusted for splits and not for dividends" in out
        assert first in out
        assert second in out
        assert out.index(first) < out.index(second)

    def test_it_prints_both_orientations_in_order(self, out: str) -> None:
        tlt = out.index("TLT on IEF:")
        ief = out.index("IEF on TLT:")
        assert tlt < ief
        assert "t = -2.3887" in out[tlt:ief]
        assert "t = -2.3168" in out[ief:]

    def test_it_prints_the_residual_check_and_the_scan(self, out: str) -> None:
        assert "first lag count from 0 to 34 whose residuals pass: 31, where t = -1.5677" in out
        assert "56 of 278 clear the 10% bar, 33 clear 5%" in out
        assert "51 of 278 clear the 10% bar, 29 clear 5%" in out

    def test_the_header_and_the_lines_that_print_constants(self, out: str) -> None:
        assert "MacKinnon crit (N=2, const, asymptotic):  1% -3.9   5% -3.34   10% -3.04" in out
        assert "(N = 6083 trading days)" in out
        assert "half-life = 333.2 trading days" in out
        assert "half-life = 376.4 trading days" in out
        assert "residual check at 1 lag:  Breusch-Godfrey p = 0.0000" in out

    def test_each_statistic_carries_its_own_reading(self, out: str) -> None:
        """Four statistics print, the one-lag fit and the first passing fit each
        way round, and each is read against the table under it."""
        readings = [
            line.strip()
            for line in out.splitlines()
            if "cointegration" in line and ("REJECTS" in line or "fails to reject" in line)
        ]
        assert readings == ["fails to reject -- no evidence of cointegration"] * 4

    def test_a_spread_that_never_reverts_and_a_search_that_finds_nothing_say_so(
        self, measured: tuple[pd.DataFrame, dict[str, Orientation]], capsys
    ) -> None:
        """Neither branch is reached on this pair, so each is driven with the
        real fit and one field replaced."""
        import dataclasses

        o = measured[1]["TLT"]
        fit = dataclasses.replace(o.fit, half_life=math.inf)
        _orientation(dataclasses.replace(o, fit=fit, passing=None))
        printed = capsys.readouterr().out
        assert (
            "spread does not mean-revert (non-negative OU slope) -- half-life undefined" in printed
        )
        assert "no lag count from 0 to 34 leaves residuals that pass" in printed
        assert "half-life =" not in printed
        assert "whose residuals pass:" not in printed

    def test_it_says_exploratory(self, out: str) -> None:
        assert "This is exploratory." in out

    def test_it_never_calls_the_result_a_verdict_or_a_replication(self, out: str) -> None:
        """Issue 16 rules both words out for a claim with no published number.
        The log's file name is a path rather than a word, so it is struck
        before the sweep."""
        prose = re.sub(r"\S*replication-log\.md", "", out).lower()
        assert "verdict" not in prose
        assert "replication" not in prose


class TestTheRefusals:
    def test_a_missing_vintage_reaches_the_operator_as_a_line(self, tmp_path, monkeypatch) -> None:
        """The IEF entry is dropped from a copy of the committed record, so the
        line names IEF. An empty directory would refuse earlier, on the
        manifest itself, and never reach the lookup this run depends on."""
        directory = committed_copy(tmp_path)
        manifest = directory / "vintages.jsonl"
        kept = [
            line
            for line in manifest.read_text(encoding="utf-8").splitlines()
            if '"symbol": "IEF"' not in line
        ]
        manifest.write_text("".join(f"{line}\n" for line in kept), encoding="utf-8")
        monkeypatch.setattr("sys.argv", ["chan.stationary_candidates"])
        monkeypatch.setattr("chan.paths.DATA_DIR", directory)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert "IEF" in str(stopped.value)

    def test_a_window_spanning_a_scale_break_also_reaches_it_as_a_line(self, monkeypatch) -> None:
        """Raised inside the join rather than here, which is how a module reading
        a pair lets it through as a traceback when it names only the first."""

        def raise_it(*args, **kwargs):
            raise WindowCrossesScaleBreak("yfinance_tlt_raw changes scale on 2010-01-04")

        monkeypatch.setattr("sys.argv", ["chan.stationary_candidates"])
        monkeypatch.setattr("chan.stationary_candidates.aligned_closes", raise_it)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert "changes scale on 2010-01-04" in str(stopped.value)

    def test_the_command_line_takes_no_window(self, monkeypatch) -> None:
        """A window option is the knob that would let a reader pick one that
        rejects, so none is offered."""
        monkeypatch.setattr("sys.argv", ["chan.stationary_candidates", "--start", "2020-01-02"])
        with pytest.raises(SystemExit) as stopped:
            main()
        assert stopped.value.code == 2


# ---- the CAD/AUD cross rate ----

CADAUD_FILE = "yfinance_cadaud=x_raw_2005-07-04_2026-09-30_dl2026-10-02.csv"


@pytest.fixture(scope="module")
def rate() -> CrossRate:
    return cross_rate()


class TestTheCrossRateVintage:
    def test_it_reads_the_raw_download_of_2026_10_02(self, rate: CrossRate) -> None:
        entry = rate.entry
        assert entry.path == CADAUD_FILE
        assert (entry.vendor, entry.symbol, entry.price_basis) == ("yfinance", CROSS_RATE, "raw")
        assert (entry.first_date, entry.last_date) == ("2005-07-04", "2026-09-30")
        assert entry.row_count == 5438
        assert entry.download_date == "2026-10-02"

    def test_the_window_starts_after_the_gap_and_runs_to_the_last_row(
        self, rate: CrossRate
    ) -> None:
        days = rate.log_rate.index
        assert str(days[0].date()) == TEST_START == "2007-08-06"
        assert str(days[-1].date()) == "2026-09-30"
        assert len(days) == 4984

    def test_the_gap_the_start_rests_on_is_in_the_vintage(self) -> None:
        """The window starts where it does because the vendor returned nothing
        for 90 weekdays. A download that filled the gap would leave the
        constant standing on nothing, so this fails first."""
        _, close = load_vintage(CROSS_RATE, unadjusted=True)
        dates = {str(day.date()) for day in close.index}
        inside = [d for d in dates if GAP[0] <= d <= GAP[1]]
        assert inside == []
        assert "2007-03-30" in dates
        assert TEST_START in dates
        weekdays = pd.bdate_range(GAP[0], GAP[1])
        assert len(weekdays) == 90

    def test_the_default_flags_refuse_it(self) -> None:
        """The rate is recorded raw, and the default flags ask for adjusted."""
        with pytest.raises(VintageUnavailable, match="CADAUD=X adjusted"):
            load_vintage(CROSS_RATE)


class TestTheCrossRateStatistic:
    def test_the_lag_one_statistic(self, rate: CrossRate) -> None:
        assert rate.adf_stat == pytest.approx(-3.2136, abs=5e-5)
        assert rate.nobs == 4982
        assert unit_root_line(rate.adf_stat) == "REJECTS the unit-root null at the 5% level"

    def test_it_is_the_statistic_the_residual_check_fits(self, rate: CrossRate) -> None:
        """The check audits the same regression the test runs, constant and
        all. With no constant it checks a different regression, with a
        different statistic, read against a different table, so the keyword is
        what makes the check about this test at all."""
        assert rate.at_lag.adf_stat == pytest.approx(rate.adf_stat, abs=1e-12)
        values = rate.log_rate.to_numpy()
        without = residual_check(values, LAGS).adf_stat
        assert without == pytest.approx(-2.5159, abs=5e-5)

    def test_the_half_life(self, rate: CrossRate) -> None:
        assert rate.half_life == pytest.approx(141.6, abs=0.05)

    def test_the_quoting_direction_does_not_move_it(self, rate: CrossRate) -> None:
        """Chan writes CAD/AUD and the vendor quotes AUD per CAD. On the log the
        two are one series negated, and the test gives one answer. On the level
        they part, though both still reject at 5% here."""
        values = rate.log_rate.to_numpy()
        assert adf_tstat(-values, LAGS)[0] == pytest.approx(rate.adf_stat, abs=1e-9)
        assert ou_half_life(-values) == pytest.approx(rate.half_life, abs=1e-9)
        level = adf_tstat(np.exp(values), LAGS)[0]
        inverse = adf_tstat(np.exp(-values), LAGS)[0]
        assert level == pytest.approx(-3.2944, abs=5e-5)
        assert inverse == pytest.approx(-3.1552, abs=5e-5)

    def test_on_the_level_both_statistics_the_verdict_reads_still_reject(
        self, rate: CrossRate
    ) -> None:
        """The scale is claimed not to decide the verdict, which reads two
        statistics, so both are held on the level in both directions."""
        values = rate.log_rate.to_numpy()
        for series, stat in ((np.exp(values), -3.0241), (np.exp(-values), -2.9734)):
            passing = first_passing(series, rate.ceiling, regression="c")
            assert passing is not None
            assert passing.lags == 10
            assert passing.adf_stat == pytest.approx(stat, abs=5e-5)

    def test_without_the_constant_the_answer_rests_on_where_the_rate_sits(
        self, rate: CrossRate
    ) -> None:
        """Added after the verdict, to show what the declared constant does.
        Without it the regression assumes the log reverts to zero, a rate of
        exactly 1.00. The rate stayed close to 1.00, between 0.9301 and 1.3239,
        so the test still rejects. Quoted per 100 Canadian dollars, the log sits 4.6 higher,
        the test with a constant gives the same answer, and the test without
        one finds nothing."""
        values = rate.log_rate.to_numpy()
        rates = np.exp(values)
        assert (rates.min(), rates.max()) == pytest.approx((0.9301, 1.3239), abs=5e-5)
        crit = adfuller(values, maxlag=LAGS, regression="n", autolag=None, result_object=False)[4]
        assert (round(crit["5%"], 2), round(crit["10%"], 2)) == (-1.94, -1.62)
        without = adf_tstat(values, LAGS, constant=False)[0]
        assert without == pytest.approx(-2.5159, abs=5e-5)
        assert without < crit["5%"]
        per_hundred = values + math.log(100)
        assert adf_tstat(per_hundred, LAGS)[0] == pytest.approx(rate.adf_stat, abs=1e-9)
        shifted = adf_tstat(per_hundred, LAGS, constant=False)[0]
        assert shifted == pytest.approx(-0.2982, abs=5e-5)
        assert shifted > crit["10%"]

    def test_a_trend_term_would_have_turned_the_verdict(self, rate: CrossRate) -> None:
        """Added after the verdict, to measure how much the declared term
        mattered. Issue 135 fixed a constant and no trend before any statistic,
        because Chan's claim is that the level is stationary. With a trend the
        one-lag statistic clears the 10% bar and not the 5% bar."""
        values = rate.log_rate.to_numpy()
        stat, _, _, nobs, crit = adfuller(
            values, maxlag=LAGS, regression="ct", autolag=None, result_object=False
        )[:5]
        assert stat == pytest.approx(-3.2947, abs=5e-5)
        assert nobs == rate.nobs
        assert (round(crit["1%"], 2), round(crit["5%"], 2), round(crit["10%"], 2)) == (
            -3.96,
            -3.41,
            -3.13,
        )
        assert crit["5%"] < stat < crit["10%"]
        same = adfuller(values, maxlag=LAGS, regression="c", autolag=None, result_object=False)[0]
        assert same == pytest.approx(rate.adf_stat, abs=1e-9)

    def test_every_lag_up_to_the_ceiling_rejects_at_five_percent(self, rate: CrossRate) -> None:
        """The headline is lag 1 by rule, and the rule does not decide the
        verdict here. Every count from 0 to the ceiling of 32 rejects, and the
        closest is 6, at -2.8739."""
        values = rate.log_rate.to_numpy()
        sweep = [adf_tstat(values, lags)[0] for lags in range(rate.ceiling + 1)]
        assert max(sweep) == pytest.approx(-2.8739, abs=5e-5)
        assert int(np.argmax(sweep)) == 6
        assert all(stat < ADF_CRIT_CONST["5%"] for stat in sweep)


class TestTheCrossRateResidualCheck:
    def test_the_ceiling(self, rate: CrossRate) -> None:
        assert rate.ceiling == schwert_ceiling(4984) == 32

    def test_the_lag_one_fit_fails_it(self, rate: CrossRate) -> None:
        assert rate.at_lag.breusch_godfrey_p == pytest.approx(0.000186, abs=5e-7)
        assert rate.at_lag.outside == [2, 6, 7, 10]
        assert not residuals_pass(rate.at_lag)

    def test_the_first_fit_that_passes_still_rejects(self, rate: CrossRate) -> None:
        passing = rate.passing
        assert passing is not None
        assert passing.lags == 10
        assert passing.adf_stat == pytest.approx(-2.9946, abs=5e-5)
        assert passing.breusch_godfrey_p == pytest.approx(0.6487, abs=5e-5)
        assert passing.outside == []
        assert unit_root_line(passing.adf_stat) == "REJECTS the unit-root null at the 5% level"

    def test_no_count_below_ten_passes(self, rate: CrossRate) -> None:
        values = rate.log_rate.to_numpy()
        for lags in range(10):
            assert not residuals_pass(residual_check(values, lags, regression="c")), lags

    def test_the_search_fits_a_constant(self, rate: CrossRate) -> None:
        """Searched without one, the first passing fit is a different
        regression with a different statistic."""
        values = rate.log_rate.to_numpy()
        plain = first_passing(values, rate.ceiling)
        assert plain is None or plain.adf_stat != pytest.approx(rate.passing.adf_stat, abs=1e-6)


def _measured(stat_one: float, stat_passing: float | None) -> CrossRate:
    """A cross-rate result with only the two statistics the verdict reads set."""

    def check(stat: float, lags: int) -> ResidualCheck:
        return ResidualCheck(
            lags=lags,
            adf_stat=stat,
            nobs=500,
            autocorrelation=np.zeros(10),
            breusch_godfrey_p=0.5,
        )

    return CrossRate(
        entry=None,  # type: ignore[arg-type]
        log_rate=pd.Series(dtype=float),
        adf_stat=stat_one,
        nobs=500,
        at_lag=check(stat_one, 1),
        ceiling=32,
        passing=None if stat_passing is None else check(stat_passing, 4),
        half_life=10.0,
        scan=rolling_adf(np.zeros(10)),
    )


class TestTheCrossRateVerdict:
    def test_it_is_reproduced(self, rate: CrossRate) -> None:
        assert rate.reproduced

    @pytest.mark.parametrize(
        ("stat_one", "stat_passing", "reproduced"),
        [
            (-3.0, -3.0, True),
            (-2.85, -3.0, False),
            (-3.0, -2.85, False),
            (-3.0, None, False),
            (-2.86, -2.86, False),
            (-2.86, -3.0, False),
            (-3.0, -2.86, False),
            (-2.8601, -2.8601, True),
        ],
    )
    def test_the_rule_reads_both_statistics_at_five_percent(
        self, stat_one: float, stat_passing: float | None, reproduced: bool
    ) -> None:
        """Both must be strictly below -2.86, and a search that found no clean
        fit is not reproduced however far the lag-1 statistic sits."""
        assert _measured(stat_one, stat_passing).reproduced is reproduced

    def test_the_pair_bar_would_refuse_both_statistics(self, rate: CrossRate) -> None:
        """The rate is one series with nothing fitted, so it is read against
        the ADF's bars. Read against Engle-Granger's, which pay for a fitted
        hedge ratio, both statistics the verdict reads miss at 5%, so the table
        decides the verdict. The blog post's Lesson 2 and its figure quote it.
        At 10% the two part: the lag-1 statistic clears the pair's -3.04 and
        the residual-clean one does not."""
        both = (rate.adf_stat, rate.passing.adf_stat)
        assert all(EG_CRIT_N2["5%"] < s < ADF_CRIT_CONST["5%"] for s in both)
        assert rate.adf_stat < EG_CRIT_N2["10%"] < rate.passing.adf_stat


class TestTheCrossRateScan:
    def test_the_counts(self, rate: CrossRate) -> None:
        stats = rate.scan.adf_stat
        assert len(stats) == 226
        assert int((stats < ADF_CRIT_CONST["10%"]).sum()) == 23
        assert int((stats < ADF_CRIT_CONST["5%"]).sum()) == 5
        assert int(np.isinf(rate.scan.half_life).sum()) == 3

    def test_a_window_holds_under_two_half_lives(self, rate: CrossRate) -> None:
        """The blog post offers this as a hypothesis for why so few windows
        reject, and nothing here measures whether it is the reason. A window of
        252 days against a half-life of 141.6 is about 1.78 half-lives."""
        assert WINDOW == 252
        assert WINDOW < 2 * rate.half_life
        assert WINDOW / rate.half_life == pytest.approx(1.78, abs=5e-3)

    def test_the_windows_span_the_test_window(self, rate: CrossRate) -> None:
        days = rate.log_rate.index
        assert str(days[rate.scan.end_idx[0]].date()) == "2008-07-30"
        assert str(days[rate.scan.end_idx[-1]].date()) == "2026-09-21"

    def test_each_window_is_the_test_on_its_slice(self, rate: CrossRate) -> None:
        values = rate.log_rate.to_numpy()
        end = int(rate.scan.end_idx[10])
        piece = values[end - 251 : end + 1]
        assert rate.scan.adf_stat[10] == pytest.approx(adf_tstat(piece, LAGS)[0], abs=1e-12)

    def test_a_series_shorter_than_a_window_has_no_windows(self) -> None:
        assert len(rolling_adf(np.zeros(251)).adf_stat) == 0

    def test_a_series_exactly_one_window_long_has_one_ending_on_its_last_row(self) -> None:
        """The real window's length leaves 7 days past the last full step, so
        it cannot tell whether the final row is reachable. This can."""
        rng = np.random.default_rng(5)
        scan = rolling_adf(np.cumsum(rng.normal(size=252)))
        assert list(scan.end_idx) == [251]


class TestTheUnitRootLine:
    """The line names the most demanding level the statistic is strictly below."""

    def test_a_statistic_on_a_bar_does_not_reject_at_that_bar(self) -> None:
        assert unit_root_line(ADF_CRIT_CONST["5%"]) == (
            "REJECTS the unit-root null at the 10% level"
        )
        assert unit_root_line(ADF_CRIT_CONST["10%"]) == (
            "fails to reject the unit-root null at 10%"
        )

    def test_just_past_a_bar_rejects_there(self) -> None:
        assert unit_root_line(ADF_CRIT_CONST["1%"] - 1e-9) == (
            "REJECTS the unit-root null at the 1% level"
        )


class TestTheCrossRateReport:
    @staticmethod
    @pytest.fixture(scope="class")
    def out() -> str:
        import contextlib
        import io

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            run_cross_rate()
        return buffer.getvalue()

    def test_it_names_the_basis_and_the_file_and_date(self, out: str) -> None:
        assert "Price basis: raw, the vendor's close, which no adjustment touches" in out
        assert f"CADAUD=X vintage: {CADAUD_FILE}   yfinance raw, downloaded 2026-10-02" in out
        assert "Test window: 2007-08-06 .. 2026-09-30   (N = 4984 days" in out

    def test_it_names_the_unit_root_null_and_never_cointegration(self, out: str) -> None:
        assert "t = -3.2136" in out
        assert "REJECTS the unit-root null at the 5% level" in out
        assert "cointegration" not in out.lower()

    def test_it_prints_the_residual_check_and_the_scan(self, out: str) -> None:
        assert "lags outside the band: 2, 6, 7, 10" in out
        assert "first lag count from 0 to 32 whose residuals pass: 10, where t = -2.9946" in out
        assert "23 of 226 clear the 10% bar, 5 clear 5%" in out

    def test_it_prints_the_one_series_bars(self, out: str) -> None:
        """The table the verdict is read against. The blog post quotes all
        three, and the 10% and 1% values are held nowhere else in this file."""
        assert "ADF crit (constant, no trend):  1% -3.43   5% -2.86   10% -2.57" in out

    def test_the_verdict_line_names_the_criterion_and_both_statistics(self, out: str) -> None:
        assert "Verdict: REPRODUCED." in out
        assert "both below the 5% bar of -2.86" in out
        assert "Here they are t = -3.2136 and t = -2.9946." in out

    def test_it_says_exploratory(self, out: str) -> None:
        assert "A replication against data is exploratory by construction." in out

    def test_a_search_that_finds_nothing_says_so_and_is_not_reproduced(self, capsys) -> None:
        """The branch the real rate never reaches, built from a result whose
        search found no residual-clean fit."""
        m = dataclasses.replace(
            _measured(-3.0, None),
            entry=cross_rate().entry,
            log_rate=pd.Series([0.0], index=pd.DatetimeIndex(["2007-08-06"])),
            half_life=math.inf,
        )
        report_cross_rate(m)
        out = capsys.readouterr().out
        assert "no lag count from 0 to 32 leaves residuals that pass" in out
        assert "Here they are t = -3.0000 and none passes." in out
        assert "Verdict: DID NOT REPRODUCE." in out
        assert "half-life undefined" in out


class TestTheCrossRateRefusals:
    def test_a_download_nobody_recorded_reaches_the_operator_as_a_line(self, monkeypatch) -> None:
        monkeypatch.setattr(
            "sys.argv", ["chan.stationary_candidates", "cross-rate", "--dated", "2026-10-03"]
        )
        with pytest.raises(SystemExit) as stopped:
            main()
        assert "CADAUD=X raw dated 2026-10-03" in str(stopped.value)

    def test_no_argument_runs_every_candidate_fixed_income_first(
        self, monkeypatch, capsys, spreads
    ) -> None:
        monkeypatch.setattr(
            "chan.stationary_candidates.calendar_spread",
            lambda product, data_dir=None: spreads[product.name],
        )
        monkeypatch.setattr("sys.argv", ["chan.stationary_candidates"])
        main()
        out = capsys.readouterr().out
        assert out.index("TLT on IEF") < out.index("Chan's CAD/AUD cross rate")
        assert "Entry 5 carries the finding.\n\nChan's CAD/AUD cross rate" in out
        assert "Verdict: REPRODUCED." in out

    def test_dated_is_refused_for_the_fixed_income_candidate(self, monkeypatch) -> None:
        """It names a CADAUD=X download, so accepting it there would read nothing."""
        monkeypatch.setattr(
            "sys.argv", ["chan.stationary_candidates", "fixed-income", "--dated", "2026-10-02"]
        )
        with pytest.raises(SystemExit) as stopped:
            main()
        assert stopped.value.code == 2

    def test_each_candidate_runs_alone(self, monkeypatch, capsys) -> None:
        monkeypatch.setattr("sys.argv", ["chan.stationary_candidates", "cross-rate"])
        main()
        out = capsys.readouterr().out
        assert "CAD/AUD" in out
        assert "TLT on IEF" not in out


class TestTheCheckFitsTheTermItIsGiven:
    """``residual_check``'s new keyword, held on a series with a mean far from zero."""

    def test_the_default_is_no_term(self) -> None:
        rng = np.random.default_rng(3)
        series = 5.0 + np.cumsum(rng.normal(size=400)) * 0.01
        assert (
            residual_check(series, 1).adf_stat == residual_check(series, 1, regression="n").adf_stat
        )

    def test_a_constant_matches_the_test_with_one(self) -> None:
        rng = np.random.default_rng(3)
        series = 5.0 + np.cumsum(rng.normal(size=400)) * 0.01
        with_constant = residual_check(series, 1, regression="c").adf_stat
        assert with_constant == pytest.approx(adf_tstat(series, 1, constant=True)[0], abs=1e-12)
        assert with_constant != pytest.approx(residual_check(series, 1).adf_stat, abs=1e-3)


def test_measuring_reads_from_the_test_start(rate: CrossRate) -> None:
    """Measuring a series that begins before the window drops those days."""
    _, close = load_vintage(CROSS_RATE, unadjusted=True)
    again = measure_cross_rate(rate.entry, close)
    assert len(again.log_rate) == 4984
    assert math.isclose(again.adf_stat, rate.adf_stat)


@pytest.fixture(scope="module")
def power(rate: CrossRate):
    return window_power(rate.half_life, len(rate.log_rate))


class TestTheWindowPower:
    """How often a series that truly reverts rejects in the rate's scan.

    The specification was declared on issue 212 before any number was
    computed: a Gaussian AR(1) reverting at the half-life the rate's own
    estimate gives, 1,000 paths as long as its test window from seed
    20261002, scanned as the rate is. It answers the hypothesis Lesson 4 of
    the blog post offered for why so few of the rate's windows reject. It does
    not show that slow reversion is the reason, because the model has neither
    the rate's fat tails nor its changing volatility. Exploratory. Takes about
    half a minute.
    """

    def test_the_declared_specification(self, power, rate: CrossRate) -> None:
        assert (POWER_SEED, POWER_PATHS) == (20261002, 1000)
        assert power.half_life == rate.half_life
        assert power.phi == pytest.approx(1 - math.log(2) / rate.half_life, abs=1e-15)
        assert power.length == 4984
        assert power.windows == 226 == len(rate.scan.adf_stat)
        assert len(power.clear10) == len(power.clear5) == len(power.whole_rejects5) == 1000

    def test_the_scan_is_the_rate_s_scan(self, rate: CrossRate) -> None:
        """The simulation computes only the statistic, for speed, so it is held
        to the scan the rate runs on the first simulated path."""
        path = simulated_paths(rate.half_life, len(rate.log_rate), 1, POWER_SEED)[0]
        stats = rolling_adf(path).adf_stat
        one = window_power(rate.half_life, len(rate.log_rate), paths=1)
        assert one.clear10[0] == int((stats < ADF_CRIT_CONST["10%"]).sum())
        assert one.clear5[0] == int((stats < ADF_CRIT_CONST["5%"]).sum())
        assert one.whole_rejects5[0] == (adf_tstat(path, LAGS)[0] < ADF_CRIT_CONST["5%"])

    def test_a_long_path_reverts_at_the_rate_s_half_life(self, rate: CrossRate) -> None:
        """Measured the way the rate's is, two million simulated days give the
        half-life back. A path as short as the test window reads it short as
        well as loosely, which is why Entry 6 says the rate's true reversion
        may be slower than its estimate."""
        long = simulated_paths(rate.half_life, 2_000_000, 1, POWER_SEED)[0]
        assert ou_half_life(long) == pytest.approx(141.5863, abs=5e-5)
        assert ou_half_life(long) == pytest.approx(rate.half_life, rel=1e-3)

    def test_each_path_starts_from_the_stationary_distribution(self, rate: CrossRate) -> None:
        phi = 1 - math.log(2) / rate.half_life
        first = simulated_paths(rate.half_life, 2, 1000, POWER_SEED)[:, 0]
        assert first.var() == pytest.approx(1 / (1 - phi**2), rel=0.1)

    def test_a_stationary_series_rejects_in_about_one_window_in_eight(self, power) -> None:
        """At 10% the mean is 27.042 windows of 226, 12.0%, against the
        rate's 23. At 5% it is 14.003, 6.2%, against the rate's 5."""
        assert power.clear10.mean() == pytest.approx(27.042, abs=5e-4)
        assert power.share_of_windows("10%") == pytest.approx(0.1197, abs=5e-5)
        assert power.clear5.mean() == pytest.approx(14.003, abs=5e-4)
        assert power.share_of_windows("5%") == pytest.approx(0.0620, abs=5e-5)
        with pytest.raises(KeyError):
            power.share_of_windows("1%")

    def test_where_the_rate_s_counts_fall_among_the_paths(self, power, rate: CrossRate) -> None:
        """388 of the 1,000 paths have 23 or fewer windows past 10%, so the
        rate's count sits near the middle. The 73 with 5 or fewer past 5% was
        not in the declared specification. It was added after the results
        were seen, and every surface that quotes it says so."""
        stats = rate.scan.adf_stat
        observed10 = int((stats < ADF_CRIT_CONST["10%"]).sum())
        observed5 = int((stats < ADF_CRIT_CONST["5%"]).sum())
        assert (observed10, observed5) == (23, 5)
        assert int((power.clear10 <= observed10).sum()) == 388
        assert int((power.clear5 <= observed5).sum()) == 73

    def test_the_whole_window_test_almost_always_rejects(self, power) -> None:
        """968 of 1,000 paths reject at 5% over all 4,984 days, so the whole
        test period has the power one year lacks."""
        assert int(power.whole_rejects5.sum()) == 968


class TestTheKnownMeanRule:
    """What a known-mean version of Chan's linear rule earns on the rate's half-life.

    The rule holds minus the distance from the mean. On a Gaussian series that
    truly reverts at a half-life, with the mean and the speed known and no
    costs, its Sharpe ratio has a closed form. The rate's is about half of
    what a 36-day half-life gives. The 36 days is Chan's crude oil calendar
    spread in *Algorithmic Trading* Example 5.4, the half-life
    ``TestTheCalendarSpreadDescriptions`` already reads for its power row. The
    figures are long-run averages, not bounds. Added on 2026-10-04 after every
    other cross-rate number was known, to say why the blog post calls the
    half-life a sizing problem. It tests no trade on the rate. Exploratory.
    """

    def test_the_rate_s_figures(self, rate: CrossRate) -> None:
        """A Sharpe ratio of 0.7845 before costs, daily scaled by the square
        root of 252, and a typical day 10.12 times a day's noise from the mean."""
        c = known_mean_rule(rate.half_life)
        assert c.phi == pytest.approx(1 - math.log(2) / rate.half_life, abs=1e-15)
        assert c.sharpe == pytest.approx(0.7845, abs=5e-5)
        assert c.spread_to_daily == pytest.approx(10.12, abs=5e-3)

    def test_a_36_day_half_life_s_figures(self) -> None:
        """1.5501 and 5.12, so the rate earns about half as much per unit of
        daily risk while holding a position about twice as large."""
        c = known_mean_rule(SPREAD_POWER_HALF_LIFE)
        assert SPREAD_POWER_HALF_LIFE == 36.0
        assert c.sharpe == pytest.approx(1.5501, abs=5e-5)
        assert c.spread_to_daily == pytest.approx(5.12, abs=5e-3)

    def test_the_sharpe_ratio_falls_with_the_square_root_of_the_half_life(
        self, rate: CrossRate
    ) -> None:
        """The ratio is 1.976 against a square root of 1.983, so the rule of
        thumb holds to within half a percent at these speeds."""
        slow, fast = known_mean_rule(rate.half_life), known_mean_rule(SPREAD_POWER_HALF_LIFE)
        assert fast.sharpe / slow.sharpe == pytest.approx(1.976, abs=5e-4)
        assert math.sqrt(rate.half_life / 36.0) == pytest.approx(1.983, abs=5e-4)

    def test_the_test_window_holds_about_35_half_lives(self, rate: CrossRate) -> None:
        """4,984 days over a 141.6-day half-life gives 35.2 stretches long
        enough for a gap to close halfway. Successive days are far from
        independent, so this counts swings rather than independent bets."""
        assert len(rate.log_rate) / rate.half_life == pytest.approx(35.2, abs=0.05)

    def test_one_standard_error_on_the_speed_spans_110_to_198_days(self, rate: CrossRate) -> None:
        """The slope the half-life is read from, with the constant the test
        fits, has a standard error of 29% of itself. One standard error either
        side gives half-lives of 110.1 and 198.2 days. That is the regression's
        usual standard error, which assumes well-behaved noise, so the true
        uncertainty is wider, and Lesson 4's short bias comes on top."""
        y = rate.log_rate.to_numpy(dtype=float)
        fit = sm.OLS(np.diff(y), sm.add_constant(y[:-1])).fit()
        slope, se = float(fit.params[1]), float(fit.bse[1])
        assert -math.log(2) / slope == pytest.approx(rate.half_life, rel=1e-12)
        assert se / -slope == pytest.approx(0.286, abs=5e-4)
        assert -math.log(2) / (slope - se) == pytest.approx(110.1, abs=0.05)
        assert -math.log(2) / (slope + se) == pytest.approx(198.2, abs=0.05)

    def test_the_kelly_leverage_tracks_the_speed(self, rate: CrossRate) -> None:
        """A 36-day half-life reverts 3.93 times as fast as the rate and earns
        a Kelly leverage 3.88 times as large, so the leverage moves almost one
        for one with the speed."""
        slow, fast = known_mean_rule(rate.half_life), known_mean_rule(SPREAD_POWER_HALF_LIFE)
        assert rate.half_life / SPREAD_POWER_HALF_LIFE == pytest.approx(3.93, abs=5e-3)
        assert fast.kelly / slow.kelly == pytest.approx(3.88, abs=5e-3)

    @pytest.mark.parametrize("half_life", ["rate", SPREAD_POWER_HALF_LIFE, 3.0])
    def test_a_simulated_trade_earns_the_closed_forms(self, rate: CrossRate, half_life) -> None:
        """The closed forms are checked by running the trade they describe on
        400 simulated paths as long as the test window, seed 20261005. At 141.6
        and 36 days each closed form sits within the simulation's noise of its
        first-order approximation, so the 3-day case is what tells them apart:
        there the first-order Sharpe ratio is 5.40 against 5.11, and the
        first-order Kelly leverage 0.231 against 0.183."""
        h = rate.half_life if half_life == "rate" else half_life
        c = known_mean_rule(h)
        z = simulated_paths(h, len(rate.log_rate), 400, 20261005)
        pnl = -z[:, :-1] * np.diff(z, axis=1)
        assert pnl.mean() / pnl.std() * math.sqrt(TRADING_DAYS) == pytest.approx(c.sharpe, rel=0.01)
        assert z.std() == pytest.approx(c.spread_to_daily, rel=0.01)
        assert pnl.mean() / pnl.var() == pytest.approx(c.kelly, rel=0.02)

    def test_on_whole_years_the_slow_reversion_earns_less_than_a_third(
        self, rate: CrossRate
    ) -> None:
        """Summed over 19 whole years per path, a day's loss on a widening gap
        is won back as it closes, so the yearly Sharpe ratio runs higher than
        the daily one scaled up: 1.24 against 0.78 at the rate's half-life, and
        4.29 against 1.55 at 36 days. The slower reversion's yearly ratio is
        0.29 of the faster one's, so on this measure the half-life costs more
        than on the daily one."""
        yearly = {}
        for h in (rate.half_life, SPREAD_POWER_HALF_LIFE):
            z = simulated_paths(h, len(rate.log_rate), 400, 20261005)
            pnl = -z[:, :-1] * np.diff(z, axis=1)
            years = pnl[:, : TRADING_DAYS * 19].reshape(400, 19, TRADING_DAYS).sum(axis=2)
            yearly[h] = float(years.mean() / years.std())
            assert yearly[h] > known_mean_rule(h).sharpe
        assert yearly[rate.half_life] == pytest.approx(1.236, abs=5e-4)
        assert yearly[SPREAD_POWER_HALF_LIFE] == pytest.approx(4.291, abs=5e-4)
        assert yearly[rate.half_life] / yearly[SPREAD_POWER_HALF_LIFE] == pytest.approx(
            0.288, abs=5e-4
        )


# ---- calendar spreads ----

NG, RBOB = NATURAL_GAS_CONTRACTS.name, RBOB_CONTRACTS.name

#: The eight vintages every calendar-spread pin reads, contract 1 to 4 of each.
SPREAD_FILES = {
    NG: [f"eia_rngc{n}_raw_{span}_dl2026-10-02.csv" for n, span in (
        (1, "1994-01-13_2024-04-05"),
        (2, "1994-01-12_2024-04-05"),
        (3, "1994-01-19_2024-04-05"),
        (4, "1993-12-20_2024-04-05"),
    )],
    RBOB: [
        f"eia_eer-epmrr-pe{n}-y35ny-dpg_raw_2005-10-03_2024-04-05_dl2026-10-02.csv"
        for n in (1, 2, 3, 4)
    ],
}  # fmt: skip


@pytest.fixture(scope="module")
def spreads() -> dict[str, CalendarSpread]:
    return {product.name: calendar_spread(product) for product in SPREAD_PRODUCTS}


def count(share: float, n: int) -> int:
    """A share of ``n`` pairs as the whole number of pairs it is."""
    whole = round(share * n)
    assert share == pytest.approx(whole / n, abs=1e-12)
    return whole


class TestTheCalendarSpreadVintages:
    @pytest.mark.parametrize("product", SPREAD_PRODUCTS, ids=lambda p: p.name)
    def test_it_reads_the_eight_downloads_of_2026_10_02(self, product: Product) -> None:
        entries = [settlements(symbol)[0] for symbol in product.symbols]
        assert [e.path for e in entries] == SPREAD_FILES[product.name]
        assert {(e.vendor, e.price_basis, e.obtained) for e in entries} == {
            ("eia", "raw", "2026-10-02")
        }

    def test_a_file_with_another_header_is_refused(self, monkeypatch, tmp_path) -> None:
        """A settlement is read only from the two columns EIA's files carry."""
        entry = settlements(RBOB_CONTRACTS.symbols[0])[0]
        monkeypatch.setattr("chan.futures.resolve_vintage", lambda **_: entry)
        monkeypatch.setattr(
            "chan.futures.read_vintage", lambda *_, **__: b"Day,Settle\n2020-01-02,1.0\n"
        )
        with pytest.raises(ValueError, match="the header reads"):
            settlements(RBOB_CONTRACTS.symbols[0], data_dir=tmp_path)

    @pytest.mark.parametrize("day", [date(2012, 10, 29), date(2012, 10, 30), date(2018, 12, 5)])
    def test_the_three_former_closures_settled_in_every_file(self, day: date) -> None:
        """Every file holds the day, and at least seven of the eight differ from
        the day before, which a holiday row repeating a settlement does not."""
        moved = 0
        for product in SPREAD_PRODUCTS:
            for rows in product.files():
                assert day in rows
                moved += rows[day] != rows[max(d for d in rows if d < day)]
        assert moved >= 7
        assert is_trading_day(day)

    def test_counted_open_the_sandy_days_put_november_2012_where_the_files_hand_over(
        self,
    ) -> None:
        """Counted closed, the rule gave 2012-10-25, where the handover does not fit."""
        assert ng_last_trade(2012, 11) == date(2012, 10, 29)
        sandy = {date(2012, 10, 29), date(2012, 10, 30), date(2018, 12, 5)}
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr("chan.futures.UNSCHEDULED_CLOSURES", UNSCHEDULED_CLOSURES | sandy)
            assert ng_last_trade(2012, 11) == date(2012, 10, 25)
        assert handover_fit(NATURAL_GAS_CONTRACTS, date(2012, 10, 29)) == Decimal("-0.315")
        assert handover_fit(NATURAL_GAS_CONTRACTS, date(2012, 10, 25)) == Decimal("0.289")


class TestTheContractNumber:
    def test_a_january_contract_read_in_december(self) -> None:
        """The count reads the delivery year, not the day's, which June's did."""
        assert contract_number(date(2017, 12, 1), 2018, 1, ng_last_trade) == 1
        assert contract_number(date(2017, 12, 1), 2018, 2, ng_last_trade) == 2

    def test_june_s_number_is_a_call_of_it(self) -> None:
        for day in trading_days(date(2018, 2, 1), date(2018, 5, 25)):
            assert june_contract_number(day) == contract_number(day, 2018, 6, ng_last_trade)

    def test_a_contract_counts_as_trading_on_its_own_last_day(self) -> None:
        last = ng_last_trade(2018, 3)
        assert contract_number(last, 2018, 3, ng_last_trade) == 1
        assert contract_number(last, 2018, 4, ng_last_trade) == 2
        assert contract_number(next_trading_day(last), 2018, 4, ng_last_trade) == 1

    def test_an_expired_contract_has_no_number(self) -> None:
        with pytest.raises(ValueError, match="stopped trading"):
            contract_number(date(2018, 2, 27), 2018, 3, ng_last_trade)

    @pytest.mark.parametrize("day", [date(2010, 12, 31), date(2021, 12, 31)])
    def test_new_year_on_a_saturday_leaves_the_friday_open(self, day: date) -> None:
        """The exchange does not move New Year's Day back into the old year.
        Every file settled on both Fridays, each the January RBOB expiry."""
        assert is_trading_day(day)
        assert rbob_last_trade(day.year + 1, 1) == day
        for product in SPREAD_PRODUCTS:
            assert all(day in rows for rows in product.files())

    def test_rbob_stops_on_the_last_business_day_before_delivery(self) -> None:
        """2024-03-29 was Good Friday, and 2005-12-30 the first RBOB expiry a pair reads."""
        assert rbob_last_trade(2024, 4) == date(2024, 3, 28)
        assert rbob_last_trade(2006, 1) == date(2005, 12, 30)
        assert rbob_last_trade(2006, 1) == last_business_day(2005, 12)


class TestTheExpiryMapAgainstTheFiles:
    """Whether the files hand over on the day each rule says, over every expiry.

    A negative :func:`handover_fit` says the handover fits. At the rule's day
    about 94% of readable handovers fit, and a day either side between 4% and
    12%, so a rule moved by a day turns these red. Measured on issue 137 before any
    statistic, and reproduced here unchanged.
    """

    @staticmethod
    def survey(product: Product, first: tuple[int, int], shift: int) -> tuple[int, int, int]:
        rule = shifted(product, shift) if shift else product
        expiries, fits, readable, month = 0, 0, 0, first
        while month <= (2024, 4):
            expiries += 1
            fit = handover_fit(product, rule.last_trade(*month))
            if fit is not None:
                readable += 1
                fits += fit < 0
            month = month_step(*month, 1)
        return expiries, fits, readable

    @pytest.mark.parametrize(
        ("product", "first", "shift", "expected"),
        [
            (NATURAL_GAS_CONTRACTS, (1994, 2), 0, (363, 298, 316)),
            (NATURAL_GAS_CONTRACTS, (1994, 2), -1, (363, 38, 324)),
            (NATURAL_GAS_CONTRACTS, (1994, 2), 1, (363, 16, 324)),
            (RBOB_CONTRACTS, (2006, 1), 0, (220, 202, 213)),
            (RBOB_CONTRACTS, (2006, 1), -1, (220, 15, 210)),
            (RBOB_CONTRACTS, (2006, 1), 1, (220, 9, 213)),
        ],
        ids=["ng", "ng-earlier", "ng-later", "rbob", "rbob-earlier", "rbob-later"],
    )
    def test_the_handover_counts(self, product, first, shift, expected) -> None:
        assert self.survey(product, first, shift) == expected

    def test_a_comparison_with_a_hole_in_it_is_none(self) -> None:
        """1994-06-14 is a trading day RNGC3 alone holds no row for."""
        files = NATURAL_GAS_CONTRACTS.files()
        assert is_trading_day(date(1994, 6, 14))
        assert [date(1994, 6, 14) in rows for rows in files] == [True, True, False, True]
        assert handover_fit(NATURAL_GAS_CONTRACTS, date(1994, 6, 14)) is None


class TestThePairs:
    """The declared set: every adjacent pair whose whole window lies in the files."""

    @pytest.mark.parametrize(
        ("name", "pairs", "first", "last"),
        [(NG, 360, (1994, 5), (2024, 4)), (RBOB, 220, (2006, 1), (2024, 4))],
    )
    def test_the_counts_and_the_ends(self, spreads, name, pairs, first, last) -> None:
        """April 1994's window starts before RNGC1 does, and December 2005's
        before the RBOB files do. May 2024's ends after 2024-04-05."""
        tests = spreads[name].tests
        assert len(tests) == pairs
        assert (tests[0].pair.near, tests[-1].pair.near) == (first, last)
        assert [t.pair.far for t in tests[:-1]] == [t.pair.near for t in tests[1:]]

    @pytest.mark.parametrize(
        ("name", "shortest", "longest", "median", "lacked"),
        [(NG, 39, 59, 56, 705), (RBOB, 40, 59, 57, 183)],
    )
    def test_the_days_each_pair_reads(
        self, spreads, name, shortest, longest, median, lacked
    ) -> None:
        """Every window loses its six guard days, and ``lacked`` more pair-days
        go because a file holds no row, which is dropped rather than filled."""
        pairs = [t.pair for t in spreads[name].tests]
        lengths = [len(p.kept) for p in pairs]
        assert (min(lengths), max(lengths), float(np.median(lengths))) == (
            shortest,
            longest,
            median,
        )
        assert sum(len(p.window) - 6 - len(p.kept) for p in pairs) == lacked

    def test_the_window_runs_from_the_contract_three_back_expiring_to_the_near_one(self) -> None:
        window = spread_window(NATURAL_GAS_CONTRACTS, (2018, 6))
        assert window[0] == next_trading_day(ng_last_trade(2018, 3)) == date(2018, 2, 27)
        assert window[-1] == ng_last_trade(2018, 6) == date(2018, 5, 29)

    def test_the_guard_band(self) -> None:
        band = guard_band(NATURAL_GAS_CONTRACTS, (2018, 6))
        assert sorted(band) == [
            date(2018, 2, 27),
            date(2018, 3, 27),
            date(2018, 3, 28),
            date(2018, 4, 26),
            date(2018, 4, 27),
            date(2018, 5, 29),
        ]
        pair = spread_pair(NATURAL_GAS_CONTRACTS, (2018, 6))
        assert not band & set(pair.kept)

    @pytest.mark.parametrize(
        ("name", "first", "last"),
        [
            (NG, ("1994-01-26", "2.119", "2.087"), ("1994-04-20", "2.139", "2.169")),
            (RBOB, ("2005-10-04", "1.817", "1.942"), ("2005-12-29", "1.682", "1.707")),
        ],
    )
    def test_the_first_pair_s_ends(self, spreads, name, first, last) -> None:
        """The near leg starts in contract 3 and ends in contract 1, the far leg one up."""
        pair = spreads[name].tests[0].pair
        files = dict(zip((NG, RBOB), SPREAD_PRODUCTS, strict=True))[name].files()
        for i, (day, near, far) in ((0, first), (-1, last)):
            assert pair.kept[i] == date.fromisoformat(day)
            assert (pair.near_prices[i], pair.far_prices[i]) == (float(near), float(far))
        assert files[2][pair.kept[0]] == Decimal(first[1])
        assert files[0][pair.kept[-1]] == Decimal(last[1])

    @pytest.mark.parametrize("product", SPREAD_PRODUCTS, ids=lambda p: p.name)
    @pytest.mark.parametrize("shift", [-1, 1])
    def test_a_rule_one_day_wrong_reads_the_same_files_on_every_kept_day(
        self, spreads, product: Product, shift: int
    ) -> None:
        """The guard band's job, held directly: on every day a pair keeps under
        the rule, a rule one day wrong puts both legs in the same files."""
        moved = shifted(product, shift).last_trade
        for t in spreads[product.name].tests:
            for day in t.pair.kept:
                assert contract_number(day, *t.pair.near, moved) == contract_number(
                    day, *t.pair.near, product.last_trade
                ), (t.pair.near, day)

    @pytest.mark.parametrize("product", SPREAD_PRODUCTS, ids=lambda p: p.name)
    @pytest.mark.parametrize("shift", [-1, 1])
    def test_a_rule_one_day_wrong_reads_the_same_prices(
        self, spreads, product: Product, shift: int
    ) -> None:
        """On every day a pair keeps under both the rule and the rule moved a
        day, the two read the same two prices."""
        compared = 0
        for t in spreads[product.name].tests:
            moved = spread_pair(shifted(product, shift), t.pair.near)
            here = dict(
                zip(
                    t.pair.kept,
                    zip(t.pair.near_prices, t.pair.far_prices, strict=True),
                    strict=True,
                )
            )
            there = dict(
                zip(moved.kept, zip(moved.near_prices, moved.far_prices, strict=True), strict=True)
            )
            for day in here.keys() & there.keys():
                assert here[day] == there[day], (t.pair.near, day)
                compared += 1
        assert compared > 50 * len(spreads[product.name].tests)


class TestTheBatchedStatistic:
    def test_it_matches_the_engine_on_simulated_paths(self) -> None:
        rng = np.random.default_rng(1)
        a = np.cumsum(rng.standard_normal((50, 56)), axis=1)
        b = np.cumsum(rng.standard_normal((50, 56)), axis=1)
        want = [engle_granger(x, y).adf_stat for x, y in zip(a, b, strict=True)]
        assert batched_engle_granger(a, b) == pytest.approx(want, abs=1e-9)

    @pytest.mark.parametrize("name", [NG, RBOB])
    def test_it_matches_the_engine_on_every_real_pair(self, spreads, name) -> None:
        for t in spreads[name].tests:
            p = t.pair
            near, far = p.near_prices[None, :], p.far_prices[None, :]
            assert batched_engle_granger(near, far)[0] == pytest.approx(
                t.near_on_far.adf_stat, abs=1e-9
            )
            assert batched_engle_granger(far, near)[0] == pytest.approx(
                t.far_on_near.adf_stat, abs=1e-9
            )


class TestTheCalendarSpreadVerdicts:
    """The criterion issue 137 declared, the correction to its null, and what each gives.

    A commodity reproduces when the share of its pairs rejecting in both
    orientations at 10% is strictly above the 975th of 1,000 null shares,
    seed 20261003. The null issue 137 declared made every contract an
    independent walk. The owner ruled on 2026-10-03, after the result was
    seen, to re-judge against walks that correlate as the files' two legs do,
    and to report the declared verdict beside it. Shares are pinned as whole
    pairs.
    """

    def test_the_declared_specification(self, spreads) -> None:
        assert (NULL_SEED, NULL_SETS, NULL_RANK) == (20261003, 1000, 975)
        assert (SPREAD_LEVEL, EG_CRIT_N2[SPREAD_LEVEL], LAGS) == ("10%", -3.04, 1)
        assert all(
            len(r.null) == len(r.declared_null) == len(r.power) == 1000 for r in spreads.values()
        )

    def test_the_correlation_the_correction_reads(self, spreads) -> None:
        """The median over pairs of the correlation of the two legs' daily changes."""
        assert spreads[NG].correlation == pytest.approx(0.9942, abs=5e-5)
        assert spreads[RBOB].correlation == pytest.approx(0.9951, abs=5e-5)
        pairs = tuple(t.pair for t in spreads[RBOB].tests)
        assert leg_correlation(pairs) == spreads[RBOB].correlation

    def test_natural_gas_reproduces(self, spreads) -> None:
        """57 of 360 against a corrected 975th null share of 47, with a median of 35."""
        r = spreads[NG]
        assert count(r.share, 360) == 57
        assert (count(r.cut, 360), count(r.null_median, 360)) == (47, 35)
        assert r.reproduced

    def test_rbob_does_not_reproduce(self, spreads) -> None:
        """14 of 220 against a corrected 975th null share of 31, with a median of 21.5."""
        r = spreads[RBOB]
        assert count(r.share, 220) == 14
        assert count(r.cut, 220) == 31
        assert r.null_median * 220 == pytest.approx(21.5, abs=1e-9)
        assert not r.reproduced

    def test_under_the_declared_null(self, spreads) -> None:
        """Bars of 19 and 13, medians of 12 and 7, and both commodities passed."""
        ng, rbob = spreads[NG], spreads[RBOB]
        assert (count(ng.declared_cut, 360), count(ng.declared_null_median, 360)) == (19, 12)
        assert (count(rbob.declared_cut, 220), count(rbob.declared_null_median, 220)) == (13, 7)
        assert ng.reproduced_as_declared and rbob.reproduced_as_declared

    def test_the_declared_null_is_the_correlated_one_at_zero(self, spreads) -> None:
        pairs = tuple(t.pair for t in spreads[RBOB].tests)
        assert np.array_equal(null_shares(pairs, correlation=0.0), spreads[RBOB].declared_null)

    def test_how_many_null_sets_reach_each_share(self, spreads) -> None:
        """Added after the verdicts were seen, and decides nothing. Under the
        corrected null none reaches natural gas's 57 and 973 reach RBOB's 14.
        Under the declared null, none and 22."""
        assert (spreads[NG].null_reaching, spreads[RBOB].null_reaching) == (0, 973)
        assert (spreads[NG].declared_null_reaching, spreads[RBOB].declared_null_reaching) == (
            0,
            22,
        )

    def test_a_pair_rejects_only_when_both_orientations_clear(self, spreads) -> None:
        t = spreads[NG].tests[0]
        clear = dataclasses.replace(t.near_on_far, adf_stat=-3.05)
        short = dataclasses.replace(t.near_on_far, adf_stat=-3.04)
        both = dataclasses.replace(t, near_on_far=clear, far_on_near=clear)
        assert both.rejects
        assert not dataclasses.replace(both, far_on_near=short).rejects
        assert not dataclasses.replace(both, near_on_far=short).rejects

    def test_a_share_on_the_cut_does_not_reproduce(self, spreads) -> None:
        r = spreads[RBOB]
        null = np.full(1000, r.share)
        assert not dataclasses.replace(r, null=null).reproduced
        assert dataclasses.replace(r, null=null - 1e-9).reproduced

    def test_the_cut_is_the_975th_share_and_not_an_interpolation(self, spreads) -> None:
        null = np.arange(1000) / 1000
        assert dataclasses.replace(spreads[NG], null=null[::-1]).cut == 0.974

    def test_the_null_changes_with_its_seed(self, spreads) -> None:
        pairs = tuple(t.pair for t in spreads[RBOB].tests)
        again = null_shares(pairs, sets=50)
        assert np.array_equal(null_shares(pairs, sets=50), again)
        assert not np.array_equal(null_shares(pairs, sets=50, seed=NULL_SEED + 1), again)


class TestTheCalendarSpreadNull:
    def test_one_pair_reads_its_walks_on_its_kept_days(self) -> None:
        """For a lone pair each leg's run is the window, drawn near leg first, so
        a dropped day spans two steps of the walk."""
        pair = spread_pair(NATURAL_GAS_CONTRACTS, (1997, 6))
        assert len(pair.kept) < len(pair.window) - 6
        rng = np.random.default_rng(NULL_SEED)
        n = len(pair.window)
        near = np.cumsum(rng.standard_normal((200, n)), axis=1)[:, pair.kept_index]
        far = np.cumsum(rng.standard_normal((200, n)), axis=1)[:, pair.kept_index]
        bar = EG_CRIT_N2[SPREAD_LEVEL]
        want = (batched_engle_granger(near, far) < bar) & (batched_engle_granger(far, near) < bar)
        assert np.array_equal(null_shares((pair,), sets=200), want.astype(float))

    def test_a_correlated_null_draws_the_shared_walk_first(self) -> None:
        """For a lone pair the shared walk covers the window, and each leg is
        the square root of rho times it plus the rest times its own walk."""
        pair = spread_pair(RBOB_CONTRACTS, (2012, 3))
        rho, n = 0.9, len(pair.window)
        rng = np.random.default_rng(NULL_SEED)
        shared = np.cumsum(rng.standard_normal((200, n)), axis=1)
        near = np.cumsum(rng.standard_normal((200, n)), axis=1)
        far = np.cumsum(rng.standard_normal((200, n)), axis=1)

        def leg(own):
            return (math.sqrt(rho) * shared + math.sqrt(1 - rho) * own)[:, pair.kept_index]

        bar = EG_CRIT_N2[SPREAD_LEVEL]
        a, b = leg(near), leg(far)
        want = (batched_engle_granger(a, b) < bar) & (batched_engle_granger(b, a) < bar)
        got = null_shares((pair,), sets=200, correlation=rho)
        assert np.array_equal(got, want.astype(float))

    def test_the_correlation_raises_how_often_both_orientations_reject(self, spreads) -> None:
        """The reason for the correction, on RBOB's own days: the null's median
        rises from 7 pairs to 21.5 when the walks correlate as the files do."""
        r = spreads[RBOB]
        assert r.declared_null_median * 220 < 8 < 21 < r.null_median * 220

    def test_pairs_out_of_delivery_order_are_refused(self) -> None:
        first, second = (spread_pair(RBOB_CONTRACTS, m) for m in ((2010, 1), (2010, 2)))
        with pytest.raises(ValueError, match="delivery order"):
            null_shares((second, first), sets=10)

    def test_a_contract_shared_by_two_pairs_carries_one_walk(self) -> None:
        """The second pair's near leg is the first pair's far leg, so its run
        covers both windows and one draw serves both."""
        first, second = (spread_pair(RBOB_CONTRACTS, m) for m in ((2010, 1), (2010, 2)))
        run = sorted(set(first.window) | set(second.window))
        rng = np.random.default_rng(NULL_SEED)
        a = np.cumsum(rng.standard_normal((100, len(first.window))), axis=1)
        b = np.cumsum(rng.standard_normal((100, len(run))), axis=1)
        c = np.cumsum(rng.standard_normal((100, len(second.window))), axis=1)
        at = {day: i for i, day in enumerate(run)}
        bar = EG_CRIT_N2[SPREAD_LEVEL]

        def both(x, y):
            return (batched_engle_granger(x, y) < bar) & (batched_engle_granger(y, x) < bar)

        b_first = b[:, [at[d] for d in first.kept]]
        b_second = b[:, [at[d] for d in second.kept]]
        want = both(a[:, first.kept_index], b_first) + 0.0
        want += both(b_second, c[:, second.kept_index])
        assert np.array_equal(null_shares((first, second), sets=100), want / 2)


class TestTheCalendarSpreadDescriptions:
    """Rows that describe each batch and decide nothing, on the same vintages."""

    @pytest.mark.parametrize(
        ("name", "n", "near_on_far", "far_on_near"), [(NG, 360, 62, 62), (RBOB, 220, 17, 16)]
    )
    def test_each_orientation_alone(self, spreads, name, n, near_on_far, far_on_near) -> None:
        r = spreads[name]
        assert (count(r.near_on_far_share, n), count(r.far_on_near_share, n)) == (
            near_on_far,
            far_on_near,
        )

    @pytest.mark.parametrize(
        ("name", "n", "near_on_far", "far_on_near"), [(NG, 360, 250, 255), (RBOB, 220, 168, 166)]
    )
    def test_the_residual_check_at_one_lag(
        self, spreads, name, n, near_on_far, far_on_near
    ) -> None:
        r = spreads[name]
        assert (
            count(r.near_on_far_residuals_pass, n),
            count(r.far_on_near_residuals_pass, n),
        ) == (near_on_far, far_on_near)

    def test_the_power_row(self, spreads) -> None:
        """Every pair reverting at Chan's 36-day half-life, seed 20261004. The
        mean share is 0.0609 for natural gas and 0.0614 for RBOB, so a window
        this short sees reversion that slow in about one pair in sixteen."""
        assert (SPREAD_POWER_SEED, SPREAD_POWER_HALF_LIFE) == (20261004, 36.0)
        assert float(spreads[NG].power.mean()) == pytest.approx(0.0609, abs=5e-5)
        assert float(spreads[RBOB].power.mean()) == pytest.approx(0.0614, abs=5e-5)
        assert float(spreads[NG].power.mean()) * 360 == pytest.approx(21.9, abs=0.05)
        assert float(spreads[RBOB].power.mean()) * 220 == pytest.approx(13.5, abs=0.05)


@pytest.fixture(scope="module")
def spread_report(spreads) -> str:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        report_calendar_spread(tuple(spreads.values()))
    return buffer.getvalue()


class TestTheCalendarSpreadReport:
    @pytest.fixture
    def out(self, spread_report: str) -> str:
        return spread_report

    def test_it_names_all_eight_vintages(self, out: str) -> None:
        for files in SPREAD_FILES.values():
            for name in files:
                assert f"    {name}   eia raw, downloaded 2026-10-02" in out

    def test_the_verdict_lines(self, out: str) -> None:
        assert "rejecting in both orientations: 57 of 360, a share of 0.1583" in out
        assert "Verdict: REPRODUCED. 0.1583 is above 0.1306." in out
        assert "rejecting in both orientations: 14 of 220, a share of 0.0636" in out
        assert "Verdict: DID NOT REPRODUCE. 0.0636 is not above 0.1409." in out

    def test_every_line_that_prints_a_number(self, out: str) -> None:
        """Each line the entry quotes, so a wrong number in any of them fails."""
        for line in (
            "natural gas: 360 pairs, near months 1994-05 .. 2024-04",
            "RBOB gasoline: 220 pairs, near months 2006-01 .. 2024-04",
            "days a pair reads: 39 to 59, median 56",
            "days a pair reads: 40 to 59, median 57",
            "each orientation alone at 10%: near on far 0.1722, far on near 0.1722",
            "each orientation alone at 10%: near on far 0.0773, far on near 0.0727",
            "residual check passing at 1 lag: near on far 0.6944, far on near 0.7083",
            "residual check passing at 1 lag: near on far 0.7636, far on near 0.7545",
            "correlation of the two legs' daily changes, median of pairs: 0.9942",
            "correlation of the two legs' daily changes, median of pairs: 0.9951",
            "null shares: median 0.0972, 975th of 1,000 0.1306",
            "null shares: median 0.0977, 975th of 1,000 0.1409",
            "declared null, contracts independent: median 0.0333, 975th 0.0528, reproduced",
            "declared null, contracts independent: median 0.0318, 975th 0.0591, reproduced",
            "null sets reaching 0.1583: 0 of 1,000, and 0 under the declared null",
            "null sets reaching 0.0636: 973 of 1,000, and 22 under the declared null",
            "(seed 20261004): mean share 0.0609",
            "(seed 20261004): mean share 0.0614",
            "A pair rejects when both clear the 10% bar of -3.04.",
            "Null: 1,000 sets of Gaussian random walks on the same days, seed 20261003,",
            "A commodity reproduces when its share is above the 975th null share.",
        ):
            assert line in out, line

    def test_the_description_added_late_says_so(self, out: str) -> None:
        assert out.count("a description added after the verdicts were seen") == 2
        assert "This null was corrected after the result was seen" in out

    def test_it_says_exploratory_and_names_the_entry(self, out: str) -> None:
        assert "exploratory by construction" in out
        assert "Entry 15 carries the verdicts." in out
        assert "there is no combined one" in out


class TestTheCalendarSpreadCommandLine:
    @pytest.fixture
    def quick(self, monkeypatch, spreads) -> None:
        """The command recomputes both batches. These tests ask only what it runs."""
        monkeypatch.setattr(
            "chan.stationary_candidates.calendar_spread",
            lambda product, data_dir=None: spreads[product.name],
        )

    def test_dated_is_refused_for_the_calendar_spread_candidate(self, monkeypatch) -> None:
        """The twin of the fixed-income refusal, for the same reason."""
        monkeypatch.setattr(
            "sys.argv", ["chan.stationary_candidates", "calendar-spread", "--dated", "2026-10-02"]
        )
        with pytest.raises(SystemExit) as stopped:
            main()
        assert stopped.value.code == 2

    @pytest.mark.parametrize("other", ["fixed-income", "cross-rate"])
    def test_the_other_candidates_run_without_it(self, monkeypatch, capsys, other) -> None:
        def refuse(product, data_dir=None):
            raise AssertionError("the calendar spreads ran")

        monkeypatch.setattr("chan.stationary_candidates.calendar_spread", refuse)
        monkeypatch.setattr("sys.argv", ["chan.stationary_candidates", other])
        main()
        assert "Chan's calendar spreads" not in capsys.readouterr().out

    def test_it_runs_alone(self, monkeypatch, capsys, quick) -> None:
        monkeypatch.setattr("sys.argv", ["chan.stationary_candidates", "calendar-spread"])
        main()
        out = capsys.readouterr().out
        assert "Chan's calendar spreads" in out
        assert "TLT on IEF" not in out and "CAD/AUD" not in out

    def test_no_argument_runs_it_third(self, monkeypatch, capsys, quick) -> None:
        monkeypatch.setattr("sys.argv", ["chan.stationary_candidates"])
        main()
        out = capsys.readouterr().out
        assert out.index("Chan's CAD/AUD cross rate") < out.index("Chan's calendar spreads")
        assert "Entry 6 carries the verdict.\n\nChan's calendar spreads" in out

    def test_a_missing_vintage_reaches_the_operator_as_a_line(self, monkeypatch) -> None:
        def refuse(product, data_dir=None):
            raise VintageUnavailable("no eia RNGC1 raw vintage is recorded")

        monkeypatch.setattr("chan.stationary_candidates.calendar_spread", refuse)
        monkeypatch.setattr("sys.argv", ["chan.stationary_candidates", "calendar-spread"])
        with pytest.raises(SystemExit) as stopped:
            main()
        assert "no eia RNGC1 raw vintage is recorded" in str(stopped.value)
