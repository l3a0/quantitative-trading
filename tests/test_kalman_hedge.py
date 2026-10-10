"""The pins for *Algorithmic Trading*'s Kalman filter hedge ratio on EWA and EWC.

The script is ``KF_beta_EWA_EWC.m``, at Kindle locations 1633 to 1726.

This file is the single authority for every number a prose surface quotes
about this replication and the findings beside it, with one exception, in
``blog/kalman-hedge-lessons.md``. The post's figure has its own pins in
``tests/test_kalman_hedge_figures.py``. README lists what the post says that
nothing pins. ``docs/replication-log.md`` Entry 32 carries the verdicts and
points here row by row.

Every pin reads one vintage and one specification, so both are stated once
here and carried in every figure's failure message as :data:`SPEC`.

- **Vintage.** ``inputdata_etf/ewa.csv`` and ``inputdata_etf/ewc.csv``, two of
  the 67 ETFs lifted from Chan's ``inputData_ETF.mat``, git blob ``261718b``,
  chan-mat, adjusted, saved 2012-04-10, 1,500 days from 2006-04-26 to
  2012-04-09, read through ``chan.series.load_panel``.
- **Specification.** ``KF_beta_EWA_EWC.m``, git blob ``e2f8a62`` at
  EpchanPreview ``e4bc46f``, as ``chan.kalman_hedge`` transcribes it. EWC's
  close regressed on EWA's close and a column of ones by a Kalman filter with
  ``delta`` 0.0001 and ``Ve`` 0.001, its state and covariance starting at 0.
  One unit long while the forecast error is below ``−sqrt(Q)``, one unit
  short while it is above ``sqrt(Q)``, each exiting on its own entry band,
  carried forward by ``fillMissingData``. Positions are ``[−slope, 1]`` of
  EWA and EWC. The return is profit over gross dollars with a NaN day set to
  0, the APR is compounded over 252 days a year and the Sharpe ratio uses
  MATLAB's n − 1 ``std``, over all 1,500 rows.

Each figure is pinned twice. Once at the six decimals the script's comment
prints, and once at eight, so a later change cannot move it inside the printed
digits unnoticed. The book's rounding at location 1726 is pinned beside them.

Location 1726's two claims about the filter's state carry no verdict, by the
owner's ruling of 2026-10-06 on issue 342, because the only criteria available
for them were written after a run. ``TestTheSlopeFinding`` and
``TestTheInterceptFinding`` pin what can be read against them.

Exploratory. Reproducing Chan's figures spends the 2006 to 2012 sample on a
rule he chose. It first ran here on 2026-10-06.
"""

from __future__ import annotations

import io
from contextlib import redirect_stdout

import numpy as np
import pandas as pd
import pytest

from chan import kalman_hedge as module
from chan import paths
from chan.kalman_hedge import (
    BOOK_APR_PERCENT,
    BOOK_SHARPE,
    DELTA,
    SCRIPT_APR,
    SCRIPT_SHARPE,
    SOURCE_FILE,
    VE,
    KalmanHedge,
    X,
    Y,
    band_signals,
    intercept_findings,
    kalman_filter,
    kalman_hedge,
    main,
    read_sources,
    rolling_falls,
    run,
    slope_findings,
    trade,
)
from chan.khandani_lo import plain_sharpe
from chan.khandani_lo_book_two import compounded_apr, matches
from chan.series import WindowCrossesScaleBreak, load_panel
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import LIFTED_SOURCES

SPEC = (
    "inputdata_etf/ EWA and EWC closes over 1,500 days, KF_beta_EWA_EWC.m's Kalman filter "
    "with delta 0.0001 and Ve 0.001 from a zero start, one unit entered beyond +/- sqrt(Q) "
    "and exited on the same band, profit over gross dollars, compounded APR, n - 1 Sharpe "
    "ratio, 1,500 rows"
)


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def closes(sources) -> pd.DataFrame:
    return sources[1]


@pytest.fixture(scope="module")
def result(closes) -> KalmanHedge:
    return kalman_hedge(closes)


@pytest.fixture
def no_arguments(monkeypatch):
    """``main`` parses ``sys.argv``, which under pytest holds pytest's own arguments."""
    monkeypatch.setattr("sys.argv", ["chan.kalman_hedge"])


class TestTheVintage:
    def test_the_members_are_the_pinned_source(self, sources) -> None:
        members, _ = sources
        vendor, basis, saved, folder, _ = LIFTED_SOURCES[SOURCE_FILE]
        assert {(m.vendor, m.price_basis, m.obtained) for m in members} == {(vendor, basis, saved)}
        assert sorted(m.path for m in members) == [f"{folder}/ewa.csv", f"{folder}/ewc.csv"]
        assert (vendor, basis, saved) == ("chan-mat", "adjusted", "2012-04-10")

    def test_both_legs_are_priced_on_all_1500_rows(self, closes) -> None:
        assert list(closes.columns) == [X, Y] == ["EWA", "EWC"]
        assert len(closes) == 1500
        assert (str(closes.index[0].date()), str(closes.index[-1].date())) == (
            "2006-04-26",
            "2012-04-09",
        )
        assert not closes.isna().any().any()


class TestTheSpecification:
    def test_the_constants_are_the_scripts(self) -> None:
        """``delta=0.0001`` and ``Ve=0.001``."""
        assert (DELTA, VE) == (0.0001, 0.001)

    def test_the_band_is_plus_or_minus_sqrt_q_with_each_exit_on_its_entry(self) -> None:
        error = np.array([-2.0, -0.5, 0.5, 2.0, 1.0, -1.0])
        variance = np.ones(6)
        longs_entry, longs_exit, shorts_entry, shorts_exit = band_signals(error, variance)
        assert list(longs_entry) == [True, False, False, False, False, False]
        assert list(longs_exit) == [False, True, True, True, True, False]
        assert list(shorts_entry) == [False, False, False, True, False, False]
        assert list(shorts_exit) == [True, True, True, False, False, True]

    def test_a_quiet_start_silences_all_four_arrays(self) -> None:
        signals = band_signals(np.array([5.0, -5.0, 5.0]), np.ones(3), quiet_rows=2)
        assert all(not each[:2].any() for each in signals)
        assert signals[2][2]

    def test_the_positions_hold_minus_the_slope_of_ewa_against_one_ewc(self, closes) -> None:
        """``numUnits.*[-beta(1,:)' ones].*[EWA EWC]``, so a short on row 1 holds EWC alone."""
        prices = closes[[X, Y]].to_numpy(dtype=float)
        filtered = kalman_filter(closes.index, prices[:, 0], prices[:, 1])
        traded = trade(prices, filtered)
        units = traded.units
        held_rows = [t for t in range(1, len(units)) if units[t - 1] != 0]
        assert {units[t - 1] for t in held_rows} == {-1.0, 1.0}
        for t in held_rows:
            held = units[t - 1] * np.array([-filtered.slope[t - 1], 1.0]) * prices[t - 1]
            move = (prices[t] - prices[t - 1]) / prices[t - 1]
            expected = (held * move).sum() / np.abs(held).sum()
            assert traded.daily[t] == pytest.approx(expected, rel=1e-12, abs=1e-15)

    def test_no_row_is_dropped(self, result) -> None:
        assert len(result.trade.daily) == len(result.trade.units) == 1500, SPEC


class TestTheFirstRows:
    def test_row_1_has_a_zero_gain_and_q_equal_to_ve(self, result) -> None:
        f = result.filter
        assert (f.slope[0], f.intercept[0]) == (0.0, 0.0), SPEC
        assert f.variance[0] == VE, SPEC
        assert f.error[0] == pytest.approx(22.95, abs=5e-9), SPEC
        assert np.sqrt(f.variance[0]) == pytest.approx(0.031623, abs=5e-7), SPEC

    def test_row_2_equals_its_closed_form(self, closes, result) -> None:
        """``c*y*[x 1]'/(c*(x^2 + 1) + Ve)`` with ``c = delta/(1-delta)``."""
        x, y = closes[X].iloc[1], closes[Y].iloc[1]
        c = DELTA / (1 - DELTA)
        expected = c * y * np.array([x, 1.0]) / (c * (x**2 + 1) + VE)
        f = result.filter
        np.testing.assert_allclose([f.slope[1], f.intercept[1]], expected, rtol=0, atol=1e-12)
        assert f.slope[1] == pytest.approx(1.366666, abs=5e-7), SPEC
        assert f.error[1] == pytest.approx(22.78, abs=5e-9), SPEC
        assert np.sqrt(f.variance[1]) == pytest.approx(0.163213, abs=5e-7), SPEC

    def test_the_first_unit_is_a_short_held_while_the_slope_is_0(self, result) -> None:
        assert result.trade.units[0] == -1.0, SPEC
        assert str(result.filter.days[0].date()) == "2006-04-26"

    def test_the_first_nonzero_return_falls_on_2006_04_27(self, result) -> None:
        first = np.flatnonzero(result.trade.daily)[0]
        assert first == 1
        assert str(result.filter.days[first].date()) == "2006-04-27", SPEC

    def test_row_1s_forecast_error_is_ewcs_whole_close(self, closes, result) -> None:
        """The forecast is 0 on row 1, so the error is EWC's close of 22.95, exactly."""
        assert result.filter.error[0] == closes[Y].iloc[0], SPEC
        assert closes[Y].iloc[0] == 22.95, SPEC

    def test_the_short_on_ewc_alone_earns_0_0074074_on_2006_04_27(self, closes, result) -> None:
        """With the slope at 0 the EWA leg holds no dollars, so the return is EWC's fall
        from 22.95 to 22.78 as a share of 22.95, which is 0.74 percent in a day."""
        ewc = closes[Y].to_numpy()
        assert (ewc[0], ewc[1]) == (22.95, 22.78), SPEC
        assert result.trade.daily[1] == pytest.approx(-(ewc[1] - ewc[0]) / ewc[0], rel=1e-12)
        assert result.trade.daily[1] == pytest.approx(0.0074074, abs=5e-8), SPEC

    def test_the_two_runs_hold_the_same_units_from_row_3_on(self, result) -> None:
        """So the whole difference between them is the returns of 2006-04-27 and
        2006-04-28, which rows 1 and 2's units earn."""
        script, quiet = result.trade, result.quiet_start
        assert list(script.units[:2]) == [-1.0, -1.0], SPEC
        assert list(quiet.units[:2]) == [0.0, 0.0], SPEC
        np.testing.assert_array_equal(script.units[2:], quiet.units[2:])
        differ = np.flatnonzero(script.daily != quiet.daily)
        assert [str(result.filter.days[t].date()) for t in differ] == [
            "2006-04-27",
            "2006-04-28",
        ], SPEC


class TestTheFigures:
    """The APR and the Sharpe ratio, beside the script's comment and location 1726."""

    def test_the_apr_is_chans_0_262252(self, result) -> None:
        apr = result.trade.apr
        assert apr == pytest.approx(0.26225194, abs=5e-9), SPEC
        assert f"{apr:f}" == SCRIPT_APR == "0.262252", SPEC
        assert matches(100 * apr, BOOK_APR_PERCENT) and BOOK_APR_PERCENT == "26.2", SPEC

    def test_the_sharpe_ratio_is_chans_2_361162(self, result) -> None:
        sharpe = result.trade.sharpe
        assert sharpe == pytest.approx(2.36116164, abs=5e-9), SPEC
        assert f"{sharpe:f}" == SCRIPT_SHARPE == "2.361162", SPEC
        assert matches(sharpe, BOOK_SHARPE) and BOOK_SHARPE == "2.4", SPEC

    def test_no_signal_on_rows_1_and_2_over_all_1500_rows(self, result) -> None:
        """The four arrays false on rows 1 and 2, and every one of the 1,500 returns
        still annualised. The figures then round to 26.1 percent and 2.3, not the
        book's 26.2 and 2.4."""
        quiet = result.quiet_start
        assert len(quiet.daily) == 1500
        assert quiet.apr == pytest.approx(0.26066891, abs=5e-9), SPEC
        assert quiet.sharpe == pytest.approx(2.34946035, abs=5e-9), SPEC
        assert round(100 * quiet.apr, 1) == 26.1
        assert round(quiet.sharpe, 1) == 2.3
        assert not matches(100 * quiet.apr, BOOK_APR_PERCENT)
        assert not matches(quiet.sharpe, BOOK_SHARPE)
        assert (quiet.daily[:2] == 0).all()

    def test_dropping_rows_1_and_2_from_the_returns_is_a_different_reading(self, result) -> None:
        """The pin above annualises all 1,500 rows. Dropping rows 1 and 2 as well
        gives 0.261059 and 2.351062, so the two readings cannot be confused."""
        dropped = result.quiet_start.daily[2:]
        assert compounded_apr(dropped) == pytest.approx(0.26105886, abs=5e-9)
        assert plain_sharpe(dropped) == pytest.approx(2.35106158, abs=5e-9)


class TestTheHoldings:
    """How often the script holds a position and how often it changes its units,
    each a trade in both funds. Between those changes the EWA leg is resized to
    each day's slope, which is a trade too and is not counted here. The script
    charges for neither."""

    def test_it_is_long_on_358_short_on_350_and_flat_on_792_days(self, result) -> None:
        units = result.trade.units
        assert set(np.unique(units)) == {-1.0, 0.0, 1.0}
        counts = ((units > 0).sum(), (units < 0).sum(), (units == 0).sum())
        assert counts == (358, 350, 792), SPEC

    def test_its_units_change_from_one_day_to_the_next_875_times(self, result) -> None:
        """Counted over the 1,499 steps between rows, so the short entered on row 1
        from no position before the file is not among them."""
        units = result.trade.units
        assert int((np.diff(units) != 0).sum()) == 875, SPEC
        assert units[0] != 0


class TestTheSlopeFinding:
    """Location 1726's "oscillates around 1", carried with no verdict."""

    def test_the_median_rounds_to_1_0_and_the_mean_to_1_1(self, result) -> None:
        s = slope_findings(result.filter.slope)
        assert s.median == pytest.approx(1.04736740, abs=5e-9), SPEC
        assert s.mean == pytest.approx(1.08969304, abs=5e-9), SPEC
        assert (round(s.median, 1), round(s.mean, 1)) == (1.0, 1.1)
        assert 1.05 - s.median == pytest.approx(0.002633, abs=5e-7)

    def test_the_slope_sits_above_1_on_894_of_1500_rows(self, result) -> None:
        s = slope_findings(result.filter.slope)
        assert (s.rows_above_one, s.rows) == (894, 1500), SPEC
        assert round(100 * s.rows_above_one / s.rows, 1) == 59.6

    def test_the_slope_crosses_1_54_times(self, result) -> None:
        """One of the 54 is row 2, where the slope leaves its zero start."""
        slope = result.filter.slope
        assert slope_findings(slope).crossings == 54, SPEC
        assert slope[0] < 1 < slope[1]
        assert slope_findings(slope[1:]).crossings == 53, SPEC

    def test_a_crossing_is_a_change_of_side(self) -> None:
        assert slope_findings(np.array([0.0, 1.5, 1.2, 0.9, 0.8, 1.1])).crossings == 3

    def test_a_slope_of_exactly_1_is_not_above_1(self) -> None:
        assert slope_findings(np.array([0.0, 1.0, 1.5])).rows_above_one == 1


@pytest.fixture(scope="module")
def found(result):
    """The intercept findings, measured once for the class that reads them."""
    return intercept_findings(result.filter.days, result.filter.intercept)


class TestTheInterceptFinding:
    """Location 1726's "increases monotonically with time", carried with no verdict."""

    def test_every_yearly_mean_is_above_the_year_before(self, found) -> None:
        assert list(found.yearly.index) == list(range(2006, 2013))
        assert list(found.yearly.round(4)) == [
            0.1440,
            0.6336,
            2.5795,
            5.6350,
            6.0380,
            6.5851,
            6.7748,
        ], SPEC
        assert (found.by_year.falls, found.by_year.steps) == (0, 6), SPEC

    def test_it_falls_at_every_finer_grain(self, found) -> None:
        assert (found.by_quarter.falls, found.by_quarter.steps) == (3, 24), SPEC
        assert (found.by_month.falls, found.by_month.steps) == (9, 72), SPEC
        assert (found.by_day.falls, found.by_day.steps) == (513, 1499), SPEC

    def test_a_250_day_rolling_mean_falls_57_times_in_1250_steps(self, found) -> None:
        assert (found.rolling.falls, found.rolling.steps) == (57, 1250), SPEC

    def test_a_300_day_rolling_mean_falls_25_times_in_1200_steps(self, result) -> None:
        falls = rolling_falls(result.filter.intercept, 300)
        assert (falls.falls, falls.steps) == (25, 1200), SPEC

    def test_a_350_day_rolling_mean_never_falls_in_1150_steps(self, result) -> None:
        """Fifty days longer than the window above, and no step falls."""
        falls = rolling_falls(result.filter.intercept, 350)
        assert (falls.falls, falls.steps) == (0, 1150), SPEC

    def test_it_peaks_on_2011_09_08_above_its_last_value(self, found) -> None:
        assert str(found.peak_day.date()) == "2011-09-08", SPEC
        assert found.peak == pytest.approx(6.803488, abs=5e-7), SPEC
        assert found.last == pytest.approx(6.767360, abs=5e-7), SPEC

    def test_a_fall_is_a_step_down(self) -> None:
        days = pd.date_range("2006-01-02", periods=4, freq="D")
        found = intercept_findings(days, np.array([1.0, 0.5, 2.0, 1.5]))
        assert (found.by_day.falls, found.by_day.steps) == (2, 3)

    def test_a_flat_step_is_not_a_fall(self) -> None:
        days = pd.date_range("2006-01-02", periods=3, freq="D")
        found = intercept_findings(days, np.array([1.0, 1.0, 0.5]))
        assert (found.by_day.falls, found.by_day.steps) == (1, 2)

    def test_any_drop_however_small_is_a_fall(self) -> None:
        falls = rolling_falls(np.array([1.0, 1.0, 1.0 - 1e-14]), 1)
        assert (falls.falls, falls.steps) == (1, 2)


class TestTheGuardAndTheReads:
    def test_read_sources_guards_both_legs_over_the_whole_file(self, monkeypatch) -> None:
        """``tests/test_scale_breaks.py`` holds that neither ETF is flagged, so a test of
        that alone passes with the call deleted. The call is recorded instead."""
        seen = []

        def record(legs, *, start, end):
            seen.append(([entry.symbol for entry, _ in legs], start, end))

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", record)
        read_sources()
        assert seen == [([X, Y], pd.Timestamp("2006-04-26"), pd.Timestamp("2012-04-09"))]

    @pytest.mark.parametrize("symbol", [X, Y])
    @pytest.mark.parametrize("row", [1, 750, 1499])
    def test_either_leg_changing_scale_anywhere_is_refused(self, symbol, row, monkeypatch) -> None:
        members, closes = load_panel(SOURCE_FILE)
        broken = closes.copy()
        broken.loc[broken.index[row:], symbol] *= 10
        monkeypatch.setattr(module, "load_panel", lambda *_a, **_k: (members, broken))
        with pytest.raises(WindowCrossesScaleBreak, match=f"{symbol.lower()}.csv"):
            read_sources()

    def test_run_reads_the_directory_it_is_given(self, tmp_path) -> None:
        with pytest.raises(VintageUnavailable, match="inputData_ETF.mat"):
            run(tmp_path)

    def test_run_reads_the_default_directory(self, monkeypatch, capsys) -> None:
        seen = []
        real = module.read_sources

        def record(data_dir=None):
            seen.append(data_dir)
            return real(data_dir)

        monkeypatch.setattr(module, "read_sources", record)
        run(paths.DATA_DIR)
        assert seen == [paths.DATA_DIR]

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage is lifted from inputData_ETF.mat"),
            WindowCrossesScaleBreak("inputdata_etf/ewc.csv changes scale on 2009-01-02"),
        ],
    )
    def test_main_prints_a_refusal_as_one_line(self, monkeypatch, no_arguments, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(module, "read_sources", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)

    def test_main_turns_a_missing_vintage_into_one_line(
        self, monkeypatch, tmp_path, no_arguments
    ) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit, match="inputData_ETF.mat"):
            main()

    def test_main_lets_any_other_error_through_as_itself(self, monkeypatch, no_arguments) -> None:
        def fail(*_a, **_k):
            raise ValueError("a bug, not a refusal")

        monkeypatch.setattr(module, "read_sources", fail)
        with pytest.raises(ValueError, match="a bug, not a refusal"):
            main()

    def test_a_miss_is_reported_as_one(self) -> None:
        assert module._verdict(0.262252, "0.262252") == "reproduced"
        assert module._verdict(26.07, "26.2") == "did not reproduce, gap -0.1"
        assert module._verdict(26.33, "26.2") == "did not reproduce, gap +0.1"


@pytest.fixture(scope="module")
def printed() -> str:
    """What ``run`` prints, captured once for the tests that read it."""
    out = io.StringIO()
    with redirect_stdout(out):
        assert isinstance(run(), KalmanHedge)
    return out.getvalue()


class TestTheReport:
    def test_it_prints_each_figure_beside_the_script_s_and_the_book_s(self, printed) -> None:
        for label, figures in (
            ("APR", ["0.26225194", "0.262252", "26.2", "reproduced"]),
            ("Sharpe ratio", ["2.36116164", "2.361162", "2.4", "reproduced"]),
        ):
            row = next(r for r in printed.splitlines() if r.strip().startswith(label + " "))
            assert row.split()[-4:] == figures, row
        assert "inputdata_etf/" in printed
        assert "inputData_ETF.mat: EWA, EWC" in printed
        assert "2006-04-26 to 2012-04-09, 1500 days" in printed
        assert "delta 0.0001, Ve 0.001" in printed

    def test_a_book_figure_that_misses_is_printed_as_a_miss(self, monkeypatch, capsys) -> None:
        """Both precisions must match for the row to read reproduced."""
        monkeypatch.setattr(module, "BOOK_APR_PERCENT", "26.1")
        run()
        row = next(r for r in capsys.readouterr().out.splitlines() if r.strip().startswith("APR "))
        assert row.endswith("did not reproduce, gap +0.1, reproduced"), row

    def test_it_prints_the_first_rows_and_the_quiet_start(self, printed) -> None:
        assert "first units -1 on 2006-04-26 with the slope at 0" in printed
        assert "first return on 2006-04-27" in printed
        assert "all 1500 rows annualised: APR 0.26066891, Sharpe ratio 2.34946035" in printed

    def test_it_prints_the_findings_with_no_verdict(self, printed) -> None:
        assert "carried as findings with no verdict" in printed
        assert (
            "median 1.047367, mean 1.089693, above 1 on 894 of 1500 rows (59.6 percent)"
        ) in printed
        assert "54 crossings of 1" in printed
        assert "2006 0.1440" in printed and "2012 6.7748" in printed
        for line in (
            "yearly steps falling: 0 of 6",
            "quarterly steps falling: 3 of 24",
            "monthly steps falling: 9 of 72",
            "250-day rolling steps falling: 57 of 1250",
            "daily steps falling: 513 of 1499",
            "peak 6.803488 on 2011-09-08, last 6.767360",
        ):
            assert line in printed

    def test_it_says_the_run_is_exploratory(self, printed) -> None:
        assert "Exploratory." in printed
