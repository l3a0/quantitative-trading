"""The pins for Chan's stationary candidates: TLT against IEF, and the CAD/AUD rate.

This file is the single authority for every number any prose surface quotes
about either candidate. ``docs/replication-log.md`` Entry 5 carries the
fixed-income finding and Entry 6 the cross-rate verdict, and each points here
row by row. The fixed-income classes come first and the cross-rate classes
follow under their own heading, each stating its vintage and specification.

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
  252-day windows stepped by 21.

Ten classes and one test.

1. ``TestTheCrossRateVintage``, the file, the window it is read over, and the
   vendor's gap the window starts after.
2. ``TestTheCrossRateStatistic``, the lag-1 statistic, its half-life, and that
   the quoting direction does not move it.
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

``test_measuring_reads_from_the_test_start`` holds that measuring a series
that begins before the window drops those days.

A replication under the claim route, which is still exploratory: the sample
was spent on a claim Chan stated about one named rate. First run on
2026-10-02, after the criterion was fixed on issue 135.
"""

from __future__ import annotations

import dataclasses
import math
import re

import numpy as np
import pandas as pd
import pytest
from ithildincore.timeseries import ADF_CRIT_CONST, EG_CRIT_N2, adf_tstat, ou_half_life

from chan.pair_cointegration import ResidualCheck, engle_granger, residual_check
from chan.series import WindowCrossesScaleBreak, aligned_closes, load_vintage
from chan.stationary_candidates import (
    CROSS_RATE,
    GAP,
    INTERMEDIATE,
    LAGS,
    LONG,
    ORIENTATIONS,
    POWER_PATHS,
    POWER_SEED,
    RESIDUAL_PASS_P,
    TEST_START,
    WINDOW,
    CrossRate,
    Orientation,
    _orientation,
    cross_rate,
    first_passing,
    fixed_income,
    main,
    measure_cross_rate,
    report_cross_rate,
    residuals_pass,
    rolling_adf,
    run,
    run_cross_rate,
    schwert_ceiling,
    simulated_paths,
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

    def test_no_argument_runs_both_fixed_income_first(self, monkeypatch, capsys) -> None:
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
