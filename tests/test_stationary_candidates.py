"""The pins for Chan's fixed-income stationary candidate, TLT against IEF.

This file is the single authority for every number any prose surface quotes
about the candidate. ``docs/replication-log.md`` Entry 5 carries the finding
and points here row by row.

Every pin below reads one vintage pair and one specification, so both are
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
"""

from __future__ import annotations

import math
import re

import numpy as np
import pandas as pd
import pytest
from ithildincore.timeseries import EG_CRIT_N2

from chan.pair_cointegration import engle_granger, residual_check
from chan.series import WindowCrossesScaleBreak, aligned_closes
from chan.stationary_candidates import (
    INTERMEDIATE,
    LAGS,
    LONG,
    ORIENTATIONS,
    Orientation,
    first_passing,
    fixed_income,
    main,
    residuals_pass,
    run,
    schwert_ceiling,
)
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
        """Both funds list on one exchange and began on one day, so the inner
        join drops nothing and the span is the full history the download
        returned."""
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
        """The finding. Both statistics sit about two thirds of a unit short of
        the 10% bar, so the orientation the test would otherwise have chosen
        decides nothing here."""
        assert measured[1][dependent].fit.adf_stat > EG_CRIT_N2["10%"]

    def test_the_two_orientations_differ_by_less_than_a_tenth(
        self, measured: tuple[pd.DataFrame, dict[str, Orientation]]
    ) -> None:
        """On GLD/GDX the two orientations sit about 0.5 apart. Here they sit
        0.0719 apart, so this pair is not a case where the choice of dependent
        leg could have turned the finding."""
        gap = measured[1]["TLT"].fit.adf_stat - measured[1]["IEF"].fit.adf_stat
        assert gap == pytest.approx(-0.0719, abs=5e-5)

    def test_the_through_origin_hedges_ride_along(
        self, measured: tuple[pd.DataFrame, dict[str, Orientation]]
    ) -> None:
        """Display-only, as on GLD/GDX. They are pinned because the rolling scan
        reports them window by window."""
        assert measured[1]["TLT"].fit.origin_hedge == pytest.approx(1.1100, abs=5e-5)
        assert measured[1]["IEF"].fit.origin_hedge == pytest.approx(0.8925, abs=5e-5)


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
        stop two dozen lag counts early, at a statistic nearer rejection."""
        o = measured[1][dependent]
        checks = [residual_check(o.fit.spread, k) for k in range(o.passing.lags)]
        clean = [c.lags for c in checks if not c.outside]
        assert clean == list(range(self.BAND_CLEARS[dependent], o.passing.lags))
        assert all(checks[k].breusch_godfrey_p <= 0.10 for k in clean)
        assert not any(residuals_pass(c) for c in checks)


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
        clustered = int(np.isin(years, [2003, 2004, 2020, 2021]).sum())
        assert clustered == {"TLT": 30, "IEF": 29}[dependent]


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
