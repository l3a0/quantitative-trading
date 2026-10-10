"""The pins for the stationarity tests and linear mean reversion on USD.CAD.

They are *Algorithmic Trading*'s Examples 2.1 to 2.5.

This file is the single authority for every number any prose surface quotes
about Examples 2.1 to 2.5, with one exception, in
``blog/usdcad-stationarity-lessons.md``. That post also quotes numbers held
elsewhere: H at a ``maxT`` of 24 in ``tests/test_tu_momentum.py``, CAD/AUD's
half-life of 141.6 days in ``tests/test_stationary_candidates.py``, the book's
23-day half-life in ``tests/test_etf_cointegration.py``, and its figure's
labels in ``tests/test_usdcad_mean_reversion_figures.py``. README lists what
the post says that nothing asserts. ``docs/replication-log.md`` Entry 22
carries the verdicts and points here row by row.

Every pin on the committed closes reads one vintage and one specification, so
both are stated once here and carried in every figure's failure message as
:data:`SPEC`.

- **Vintage.** ``pythoncodesanddata/inputData_USDCAD.csv``, vendor ``chan-py``,
  symbol ``USDCAD``, basis ``raw``, saved 2018-10-13, the minute file of
  Chan's 2018 Python port. Its identity is the row of ``PYTHON_PORT`` in
  ``tests/support/committed_vintages.py``. The 16:59 bar of each day gives
  1,216 closes from 2007-07-23 to 2012-03-28.
- **Specification.** ``stationarityTests.m`` at the mirror commit
  :mod:`chan.usdcad_mean_reversion` names. jplv7's ``adf`` at trend order 0
  and 1 lag, with ``ztcrit``'s critical values. ``genhurst`` at q = 2 and its
  default ``maxT`` of 19 on the log closes. ``vratiotest`` at its defaults,
  period 2, heteroskedasticity-consistent and two-sided, on the log closes. The
  half-life from the change regressed on the previous close and a constant.
  Example 2.5's position is minus the close's distance from its moving average
  in moving standard deviations, both over the half-life rounded, and its claim
  is the one issue 338 declared before any P&L was computed: the sum of the
  daily P&L over all 1,216 rows is greater than 0.

Each figure Chan printed is pinned twice, at the precision he printed it and
at the precision that is real, so a change cannot move it inside his rounding
unnoticed. H is pinned against the book's 0.49 as a miss.

Exploratory. Reproducing Chan's figures spends the 2007 to 2012 sample on
tests he chose. It first ran here on 2026-10-05.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from ithildincore.timeseries import adf_tstat

from chan import usdcad_mean_reversion
from chan.matlab_helpers import moving_avg, moving_std
from chan.series import WindowCrossesScaleBreak, scale_breaks
from chan.stationarity_tests import ZTCRIT_CONSTANT, vratiotest
from chan.usdcad_mean_reversion import (
    ADF_LAGS,
    ADF_ORDER,
    BOOK_ADF,
    BOOK_HALF_LIFE_DAYS,
    BOOK_HURST,
    HURST_Q,
    MINUTES_DATED,
    SCRIPT_ADF,
    SCRIPT_AR1,
    SCRIPT_CRITICAL,
    SCRIPT_HALF_LIFE,
    SCRIPT_VRATIO_H,
    SCRIPT_VRATIO_P,
    SYMBOL,
    StationarityRun,
    linear_mean_reversion,
    main,
    market_value,
    pnl_drawdown,
    read_sources,
    run,
    stationarity_tests,
)
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import PYTHON_PORT

SPEC = (
    "inputData_USDCAD.csv saved 2018-10-13, 16:59 closes, jplv7 adf(y, 0, 1), "
    "genhurst(log(y), 2), vratiotest(log(y)), half-life from ols(dy, [ylag 1]), "
    "Example 2.5 over the rounded half-life"
)
MINUTE_FILE = "pythoncodesanddata/inputData_USDCAD.csv"


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def result(sources) -> StationarityRun:
    return stationarity_tests(*sources)


class TestTheSpecification:
    def test_the_calls_are_the_scripts(self) -> None:
        assert (ADF_ORDER, ADF_LAGS, HURST_Q) == (0, 1, 2)

    def test_the_printed_figures_are_transcribed_as_printed(self) -> None:
        assert SCRIPT_ADF == -1.840744
        assert SCRIPT_AR1 == 0.994120
        assert SCRIPT_CRITICAL == (-3.458, -2.871, -2.594)
        assert (SCRIPT_VRATIO_H, SCRIPT_VRATIO_P) == (0, 0.367281)
        assert SCRIPT_HALF_LIFE == 115.209794
        assert (BOOK_ADF, BOOK_HURST, BOOK_HALF_LIFE_DAYS) == (-1.84, 0.49, 115)


class TestTheVintage:
    def test_the_closes_are_the_pinned_minute_file(self, sources) -> None:
        entry, _ = sources
        vendor, symbol, basis, saved, workbook, shape = PYTHON_PORT[MINUTE_FILE]
        assert (entry.path, entry.vendor, entry.symbol, entry.price_basis) == (
            MINUTE_FILE,
            vendor,
            symbol,
            basis,
        )
        assert entry.saved_date == saved == MINUTES_DATED
        assert (entry.source_workbook, shape, entry.symbol) == (
            "PythonCodesAndData.zip",
            "minute",
            SYMBOL,
        )

    def test_the_1659_bar_gives_1216_closes(self, sources) -> None:
        _, closes = sources
        assert len(closes) == 1216, SPEC
        assert (str(closes.index[0].date()), str(closes.index[-1].date())) == (
            "2007-07-23",
            "2012-03-28",
        )
        assert closes.index.is_monotonic_increasing and closes.index.is_unique

    def test_the_scale_break_guard_flags_nothing(self, sources) -> None:
        """The run calls the guard, so a vintage that broke would refuse it. This one does not."""
        _, closes = sources
        assert scale_breaks(closes) == []

    def test_the_run_calls_the_guard(self, sources, monkeypatch) -> None:
        """Removing the call moves no figure here, so only a guard that refuses can show it runs."""

        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak(f"a break inside {start.date()} to {end.date()}")

        monkeypatch.setattr(usdcad_mean_reversion, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(WindowCrossesScaleBreak, match="2007-07-23 to 2012-03-28"):
            stationarity_tests(*sources)


class TestExample21TheAdfTest:
    def test_the_statistic_is_chans_minus_1_840744(self, result: StationarityRun) -> None:
        assert result.adf.statistic == pytest.approx(SCRIPT_ADF, abs=5e-7), SPEC
        # Nine decimals rather than ten. macOS gives -1.8407440890839797 and some
        # Linux CI runners -1.840744089202234, a 1.2e-10 gap in the last bits of
        # the regression, so the tenth decimal is not a figure the platforms
        # share. Issue 400 measured it.
        assert result.adf.statistic == pytest.approx(-1.840744089, abs=5e-10), SPEC
        assert round(result.adf.statistic, 2) == BOOK_ADF

    def test_the_ar1_estimate_is_chans_0_994120(self, result: StationarityRun) -> None:
        assert result.adf.ar1 == pytest.approx(SCRIPT_AR1, abs=5e-7), SPEC
        assert result.adf.ar1 == pytest.approx(0.9941196429, abs=5e-11), SPEC

    def test_the_critical_values_are_chans(self, result: StationarityRun) -> None:
        assert result.adf.critical == ZTCRIT_CONSTANT[9] == (-3.45830, -2.87104, -2.59369)
        assert tuple(round(c, 3) for c in result.adf.critical) == SCRIPT_CRITICAL

    def test_the_regression_fits_1213_rows_at_1_lag(self, result: StationarityRun) -> None:
        assert result.adf.nobs == 1213

    def test_the_unit_root_is_not_rejected_at_90_percent_and_lambda_is_negative(
        self, result: StationarityRun
    ) -> None:
        """Location 1114's two readings: above −2.594, and the slope on the level below 0."""
        assert result.adf.statistic > result.adf.critical[2]
        assert result.adf.ar1 - 1 < 0

    def test_adfuller_at_the_same_lag_misses_by_the_one_row_it_keeps(
        self, result: StationarityRun
    ) -> None:
        """``ithildincore``'s ``adf_tstat`` and Chan's Python port both run ``adfuller``.

        Neither prints −1.840744, so the script's figure needs jplv7's regression.
        """
        assert result.adfuller_statistic == pytest.approx(-1.8430182830, abs=5e-11)
        assert result.adfuller_ar1 == pytest.approx(0.9941138113, abs=5e-11)
        assert round(result.adfuller_statistic, 6) != SCRIPT_ADF
        assert adf_tstat(result.closes.to_numpy(), 1)[1] == 1214


class TestExample22TheHurstExponent:
    def test_h_misses_the_books_0_49(self, result: StationarityRun) -> None:
        assert result.hurst == pytest.approx(0.4732326652, abs=5e-11), SPEC
        assert round(result.hurst, 2) == 0.47 != BOOK_HURST

    def test_h_is_still_below_a_half(self, result: StationarityRun) -> None:
        """Location 1119's reading, weakly mean reverting, survives the miss."""
        assert result.hurst < 0.5

    def test_the_python_ports_own_genhurst_misses_too(self, result: StationarityRun) -> None:
        assert result.python_port_hurst == pytest.approx(0.4758441244, abs=5e-11)
        assert round(result.python_port_hurst, 2) == 0.48 != BOOK_HURST


class TestExample23TheVarianceRatio:
    def test_the_decision_and_p_value_are_chans(self, result: StationarityRun) -> None:
        assert int(result.vratio.rejects) == SCRIPT_VRATIO_H, SPEC
        assert result.vratio.p_value == pytest.approx(SCRIPT_VRATIO_P, abs=5e-7), SPEC
        assert result.vratio.p_value == pytest.approx(0.3672813756, abs=5e-11), SPEC

    def test_the_statistic_and_ratio(self, result: StationarityRun) -> None:
        assert result.vratio.statistic == pytest.approx(-0.9015774476, abs=5e-11)
        assert result.vratio.ratio == pytest.approx(0.9647450127, abs=5e-11)
        assert result.vratio.nobs == 1214

    def test_the_last_of_1215_returns_is_never_read(self, sources, result) -> None:
        """1,215 returns is odd, so MATLAB's trim to whole periods drops the last one."""
        _, closes = sources
        assert vratiotest(np.log(closes.to_numpy()[:-1])) == result.vratio


class TestExample24TheHalfLife:
    def test_the_half_life_is_chans_115_209794(self, result: StationarityRun) -> None:
        assert result.half_life == pytest.approx(SCRIPT_HALF_LIFE, abs=5e-7), SPEC
        assert result.half_life == pytest.approx(115.2097944852, abs=5e-10), SPEC
        assert round(result.half_life) == BOOK_HALF_LIFE_DAYS


class TestExample25LinearMeanReversion:
    def test_the_lookback_is_the_half_life_rounded(self, result: StationarityRun) -> None:
        assert result.lookback == 115

    def test_the_cumulative_pnl_is_positive_as_location_1225_says(
        self, result: StationarityRun
    ) -> None:
        """The claim issue 338 declared before any P&L was computed."""
        assert result.total_pnl > 0, SPEC
        assert result.total_pnl == pytest.approx(0.1141168588, abs=5e-11), SPEC

    def test_the_drawdown_reported_beside_it(self, result: StationarityRun) -> None:
        """It decides nothing. It is more than five times what the run ends with."""
        d = result.drawdown
        assert d.depth == pytest.approx(0.6425313986, abs=5e-11)
        assert (str(d.peak.date()), str(d.trough.date())) == ("2008-07-22", "2008-10-27")
        cumulative = result.pnl.cumsum()
        assert cumulative.max() == pytest.approx(0.1320839920, abs=5e-11)
        assert cumulative.idxmax() == d.peak
        assert cumulative.min() == pytest.approx(-0.5104474067, abs=5e-11)
        assert cumulative.idxmin() == d.trough
        assert 5 * result.total_pnl < d.depth < 6 * result.total_pnl

    def test_the_first_position_is_the_day_after_the_window_fills(
        self, result: StationarityRun
    ) -> None:
        assert str(result.first_position.date()) == "2008-01-02"
        assert result.pnl.index.get_loc(result.first_position) == result.lookback
        assert (result.pnl.iloc[: result.lookback] == 0).all()

    def test_each_days_pnl_is_yesterdays_position_times_todays_return(
        self, sources, result: StationarityRun
    ) -> None:
        """Recomputed by plain pandas, so a shifted position or a lost minus sign fails."""
        _, closes = sources
        y = closes.astype(float)
        position = -(y - y.rolling(115).mean()) / y.rolling(115).std(ddof=1)
        expected = (position.shift(1) * y.pct_change()).fillna(0.0)
        np.testing.assert_allclose(result.pnl.to_numpy(), expected.to_numpy(), atol=1e-12)


def held_position(result: StationarityRun) -> pd.Series:
    """The run's ``mktVal`` on each day, over the run's own lookback."""
    y = result.closes.to_numpy(dtype=float)
    return pd.Series(market_value(y, result.lookback), index=result.closes.index)


class TestBesideTheClaim:
    """Numbers the blog post on Examples 2.1 to 2.5 quotes about the trade, none a published figure.

    None of these is a replication. Each reads the run's closes and P&L on the
    vintage and specification in :data:`SPEC`, so they are as exploratory as
    the rest.
    """

    def test_the_dollar_rose_28_percent_on_the_canadian_dollar_across_the_fall(
        self, result: StationarityRun
    ) -> None:
        d = result.drawdown
        at_peak, at_trough = result.closes[d.peak], result.closes[d.trough]
        assert (at_peak, at_trough) == (1.00835, 1.29485), SPEC
        assert at_trough / at_peak - 1 == pytest.approx(0.2841275351, abs=5e-11), SPEC

    def test_the_largest_short_is_held_inside_the_fall(self, result: StationarityRun) -> None:
        """The largest short, 4.12 moving deviations, falls inside the drawdown."""
        position = held_position(result)
        assert position.min() == pytest.approx(-4.1198560837, abs=5e-11), SPEC
        assert str(position.idxmin().date()) == "2008-10-10"
        assert result.drawdown.peak < position.idxmin() < result.drawdown.trough
        assert position.max() == pytest.approx(3.0442241430, abs=5e-11), SPEC
        assert str(position.idxmax().date()) == "2009-05-29"

    def test_the_short_eases_while_the_close_keeps_rising(self, result: StationarityRun) -> None:
        """The deviation widens with the close, so the trough holds a smaller short."""
        position = held_position(result)
        trough = result.drawdown.trough
        assert result.closes[position.idxmin()] == 1.17325, SPEC
        rise = result.closes[trough] / result.closes[position.idxmin()] - 1
        assert rise == pytest.approx(0.1036437247, abs=5e-11), SPEC
        assert position[trough] == pytest.approx(-3.8330290865, abs=5e-11), SPEC

    def test_the_rule_is_short_on_all_69_days_of_the_fall(self, result: StationarityRun) -> None:
        """Each day after the peak through the trough earns on yesterday's position."""
        d = result.drawdown
        held = held_position(result).shift(1)[d.peak : d.trough].iloc[1:]
        assert len(held) == 69
        assert (held < 0).all(), SPEC

    def test_the_run_ends_below_its_high_after_climbing_back(self, result: StationarityRun) -> None:
        cumulative = result.pnl.cumsum()
        assert cumulative.max() - result.total_pnl == pytest.approx(0.0179671332, abs=5e-11)
        assert result.total_pnl - cumulative.min() == pytest.approx(0.6245642655, abs=5e-11)

    def test_the_rule_holds_short_on_488_days_and_long_on_613(
        self, result: StationarityRun
    ) -> None:
        """Counted on the day the P&L is earned, so on yesterday's position.

        The P&L each held day earns has the sign of that position times the
        day's return, which ties the count to the rule rather than to a copy.
        """
        held = held_position(result).shift(1).dropna()
        returns = result.closes.pct_change().loc[held.index]
        earned = result.pnl.loc[held.index]
        np.testing.assert_allclose(earned.to_numpy(), (held * returns).to_numpy(), atol=1e-12)
        assert len(held) == 1101 == len(result.closes) - result.lookback
        assert ((held < 0).sum(), (held > 0).sum()) == (488, 613), SPEC

    def test_2008_ends_at_minus_0_2552_and_the_rest_adds_0_3693(
        self, result: StationarityRun
    ) -> None:
        cumulative = result.pnl.cumsum()
        end_of_2008 = cumulative[:"2008-12-31"].iloc[-1]
        assert end_of_2008 == pytest.approx(-0.2552305412, abs=5e-11), SPEC
        assert result.total_pnl - end_of_2008 == pytest.approx(0.3693474000, abs=5e-11), SPEC

    def test_the_closes_span_10_6_half_lives(self, result: StationarityRun) -> None:
        assert len(result.closes) / result.half_life == pytest.approx(10.5546581819, abs=5e-11)
        assert round(len(result.closes) / result.half_life, 1) == 10.6


class TestTheRun:
    def test_it_prints_each_figure_beside_chans(self, sources, monkeypatch, capsys) -> None:
        monkeypatch.setattr(usdcad_mean_reversion, "read_sources", lambda data_dir=None: sources)
        run()
        out = capsys.readouterr().out
        assert "1216 closes, 2007-07-23 to 2012-03-28" in out
        for line, figures in (
            ("2.1 ADF statistic", ["-1.840744", "-1.840744", "-1.84"]),
            ("2.1 AR(1) estimate", ["0.994120", "0.994120"]),
            ("2.1 critical values", ["-3.458/-2.871/-2.594", "-2.594"]),
            ("2.2 Hurst exponent", ["0.473233", "0.49"]),
            ("2.3 variance ratio p-value", ["0.367281", "0.367281"]),
            ("2.4 half-life", ["115.209794", "115"]),
        ):
            (row,) = [each for each in out.splitlines() if line in each]
            assert all(figure in row.split() for figure in figures), row
        (h_row,) = [each for each in out.splitlines() if "2.3 variance ratio h" in each]
        assert h_row.split()[-3:] == ["0", "0", "none"], h_row
        assert "2.5 lookback 115 days, the half-life rounded. First position on 2008-01-02." in out
        assert "cumulative P&L 0.114117. The claim declared on issue 338, positive, holds." in out
        assert "deepest drawdown 0.642531, from 2008-07-22 to 2008-10-27" in out
        assert "statistic -1.843018, AR(1) 0.994114" in out
        assert "own genhurst: 0.475844" in out
        assert "Exploratory." in out


class TestTheRule:
    def test_the_rows_before_the_window_fills_earn_nothing(self) -> None:
        pnl = linear_mean_reversion(np.array([1.0, 2.0, 3.0, 2.0, 1.0, 2.0]), 3)
        np.testing.assert_array_equal(pnl[:3], [0.0, 0.0, 0.0])

    def test_a_close_above_its_average_is_sold_and_earns_on_a_fall(self) -> None:
        """Closes 1, 2, 3: the average is 2 and the deviation 1, so the position is −1.

        The next close of 1.5 is a return of −0.5, and −1 times −0.5 is +0.5.
        """
        y = np.array([1.0, 2.0, 3.0, 1.5])
        assert moving_avg(y, 3)[2] == 2.0 and moving_std(y, 3)[2] == 1.0
        assert linear_mean_reversion(y, 3)[3] == pytest.approx(0.5, abs=1e-15)

    def test_a_zero_deviation_leaves_the_day_at_zero_rather_than_nan(self) -> None:
        """A flat window divides by a zero deviation, which is NaN for 0/0 and set to 0."""
        y = np.array([2.0, 2.0, 2.0, 3.0])
        assert linear_mean_reversion(y, 3)[3] == 0.0

    def test_the_drawdown_finds_the_deepest_fall_and_its_dates(self) -> None:
        days = pd.date_range("2020-01-01", periods=6)
        pnl = pd.Series([0.0, 1.0, 1.0, -3.0, 1.0, 2.5], index=days)
        d = pnl_drawdown(pnl)
        assert d.depth == 3.0
        assert (d.peak, d.trough) == (days[2], days[3])

    def test_the_peak_is_the_last_day_at_the_high_before_the_trough(self) -> None:
        days = pd.date_range("2020-01-01", periods=4)
        d = pnl_drawdown(pd.Series([0.0, 1.0, 0.0, -3.0], index=days))
        assert (d.depth, d.peak, d.trough) == (3.0, days[2], days[3])

    def test_the_running_high_starts_at_the_first_day_rather_than_at_zero(self) -> None:
        days = pd.date_range("2020-01-01", periods=3)
        d = pnl_drawdown(pd.Series([-1.0, -1.0, 0.5], index=days))
        assert (d.depth, d.peak, d.trough) == (1.0, days[0], days[1])

    def test_the_lookback_rounds_a_half_away_from_zero_as_matlab_does(
        self, sources, monkeypatch
    ) -> None:
        """Python's ``round`` sends 114.5 to the even 114, and MATLAB's sends it to 115."""
        monkeypatch.setattr(usdcad_mean_reversion, "ou_half_life", lambda y: 114.5)
        assert round(114.5) == 114
        assert stationarity_tests(*sources).lookback == 115

    def test_a_run_that_never_falls_has_a_zero_drawdown(self) -> None:
        days = pd.date_range("2020-01-01", periods=3)
        d = pnl_drawdown(pd.Series([0.0, 1.0, 2.0], index=days))
        assert d.depth == 0.0 and d.trough == days[0]

    def test_a_series_that_does_not_revert_is_refused(self, sources) -> None:
        entry, closes = sources
        trending = pd.Series(np.exp(np.arange(len(closes)) * 1e-3), index=closes.index)
        with pytest.raises(ValueError, match="do not revert"):
            stationarity_tests(entry, trending)


class TestTheRefusals:
    def test_main_prints_a_refusal_as_one_line(self, monkeypatch) -> None:
        def refuse(data_dir=None):
            raise VintageUnavailable(f"no committed vintage of {SYMBOL} saved {MINUTES_DATED}")

        monkeypatch.setattr(usdcad_mean_reversion, "run", refuse)
        monkeypatch.setattr("sys.argv", ["usdcad_mean_reversion"])
        with pytest.raises(SystemExit, match="no committed vintage of USDCAD saved 2018-10-13"):
            main()

    def test_a_missing_vintage_reaches_the_reader(self, tmp_path) -> None:
        with pytest.raises(VintageUnavailable):
            read_sources(tmp_path)
