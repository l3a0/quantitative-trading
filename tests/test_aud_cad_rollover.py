"""The pins for AUD.CAD with rollover interest, *Algorithmic Trading*'s Example 5.2.

This file is the single authority for every number a prose surface quotes
about this example and the rows beside it, with one exception, in
``blog/aud-cad-rollover-lessons.md``. The post's figure has its own pins in
``tests/test_aud_cad_rollover_figures.py``. README lists what the post says
that nothing pins. ``docs/replication-log.md`` Entry 30 carries the verdicts
and points here row by row.

Every pin on the committed files reads one vintage and one specification, so
both are stated once here.

- **Vintage.** ``pythoncodesanddata/inputData_AUDCAD_20120426.csv``, chan-py,
  raw, saved 2018-12-13, 1,237 days from 2007-07-23 to 2012-04-26, read
  through ``chan.series.load_port_close``. ``pythoncodesanddata/AUD_interestRate.csv``
  and ``pythoncodesanddata/CAD_interestRate.csv``, chan-py, rate, saved
  2018-12-13, read through ``chan.series.load_rates``. All three come from
  ``PythonCodesAndData.zip`` at EpchanPreview ``e4bc46f``, and their identity
  is their rows of ``PYTHON_PORT`` in ``tests/support/committed_vintages.py``.
- **Specification.** ``AUDCAD_daily.m`` at EpchanPreview ``e4bc46f``, git blob
  ``823983a``, as :mod:`chan.aud_cad_rollover` transcribes it. A 20-row
  z-score including the day, a position of minus its sign held from the next
  day, each month's rate with zero for a missing month, divided by 365 and by
  100, AUD tripled on Wednesdays and CAD on Thursdays, log returns compounded
  as simple ones over all 1,237 rows, 252-day annualisation, no risk-free rate
  and no cost.

Each published figure is held twice: at the computed value's own precision,
which is what lets the log quote it, and at the precision Chan printed,
through ``matches``.

Exploratory. Reproducing Chan's figures spends the 2007 to 2012 sample on a
rule he chose. The example first ran on 2026-10-05.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from chan import aud_cad_rollover as module
from chan import paths
from chan.aud_cad_rollover import (
    AUD_TRIPLE_WEEKDAY,
    BOOK_APR_PERCENT,
    BOOK_APR_WITHOUT_PERCENT,
    BOOK_SHARPE,
    BOOK_SHARPE_WITHOUT,
    CAD_TRIPLE_WEEKDAY,
    ROLLOVER_CEILING,
    ROLLOVER_FLOOR,
    SCRIPT_APR,
    SCRIPT_LOOKBACK,
    SCRIPT_SHARPE,
    Rollover,
    annualised_rollover,
    aud_cad_rollover,
    daily_rates,
    linear_returns,
    main,
    read_sources,
    run,
    zscore,
)
from chan.khandani_lo_book_two import matches
from chan.matlab_helpers import lag1
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import PYTHON_PORT, committed_copy


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def result(sources) -> Rollover:
    return aud_cad_rollover(sources.closes[1], sources.aud[1], sources.cad[1])


@pytest.fixture
def no_arguments(monkeypatch):
    """``main`` parses ``sys.argv``, which under pytest holds pytest's own arguments."""
    monkeypatch.setattr("sys.argv", ["chan.aud_cad_rollover"])


def _monthly(rates: dict[str, float]) -> pd.Series:
    """A rate file as ``load_rates`` returns it, keyed by ``YYYY-MM``."""
    return pd.Series(
        list(rates.values()), index=pd.DatetimeIndex([f"{month}-01" for month in rates])
    )


def _closes(rows: int = 60, seed: int = 3) -> np.ndarray:
    """A random walk near AUD.CAD's level, long enough to fill the 20-row window."""
    rng = np.random.default_rng(seed)
    return 1.0 + np.cumsum(rng.normal(scale=0.005, size=rows))


class TestTheSpecification:
    def test_the_script_scores_over_20_rows(self) -> None:
        assert SCRIPT_LOOKBACK == 20

    def test_aud_triples_on_wednesday_and_cad_on_thursday(self) -> None:
        """MATLAB's ``weekday`` 4 and 5 count from Sunday as 1, pandas' 2 and 3 from Monday as 0."""
        assert (AUD_TRIPLE_WEEKDAY, CAD_TRIPLE_WEEKDAY) == (2, 3)
        assert pd.Timestamp("2012-04-25").day_name() == "Wednesday"
        assert pd.Timestamp("2012-04-25").weekday() == AUD_TRIPLE_WEEKDAY

    def test_row_5s_criterion_is_the_one_declared_on_issue_346(self) -> None:
        assert (ROLLOVER_FLOOR, ROLLOVER_CEILING) == (0.045, 0.050)


class TestTheVintages:
    def test_each_read_is_its_pinned_entry(self, sources) -> None:
        for entry in sources.entries:
            vendor, symbol, basis, saved_date, _, _ = PYTHON_PORT[entry.path]
            assert (entry.vendor, entry.symbol, entry.price_basis, entry.saved_date) == (
                vendor,
                symbol,
                basis,
                saved_date,
            )
        assert [entry.path for entry in sources.entries] == [
            "pythoncodesanddata/inputData_AUDCAD_20120426.csv",
            "pythoncodesanddata/AUD_interestRate.csv",
            "pythoncodesanddata/CAD_interestRate.csv",
        ]

    def test_the_daily_file_holds_1237_positive_closes(self, sources) -> None:
        closes = sources.closes[1]
        assert len(closes) == 1237
        assert (str(closes.index[0].date()), str(closes.index[-1].date())) == (
            "2007-07-23",
            "2012-04-26",
        )
        assert np.isfinite(closes.to_numpy()).all()
        assert (closes > 0).all()
        assert closes.index.is_monotonic_increasing and closes.index.is_unique

    def test_seven_weekdays_are_absent_and_none_is_a_weekend(self, sources) -> None:
        """Measurement 1 on issue 346: the holidays, and the early close of 2011-12-23."""
        days = sources.closes[1].index
        absent = pd.bdate_range(days[0], days[-1]).difference(days)
        assert [str(day.date()) for day in absent] == [
            "2007-12-25",
            "2008-01-01",
            "2008-12-25",
            "2009-01-01",
            "2009-12-25",
            "2010-01-01",
            "2011-12-23",
        ]
        assert (days.weekday < 5).all()

    def test_the_rate_files_stop_before_the_trading_does(self, sources) -> None:
        aud, cad = sources.aud[1], sources.cad[1]
        assert (len(aud), str(aud.index[-1].date())) == (147, "2012-03-01")
        assert (len(cad), str(cad.index[-1].date())) == (144, "2011-12-01")

    def test_the_rates_average_4_908_and_1_592_percent_from_july_2007(self, sources) -> None:
        """Measurement 6 on issue 346, which row 5's criterion was written knowing."""
        aud, cad = (rates[rates.index >= "2007-07-01"] for _, rates in (sources.aud, sources.cad))
        assert aud.mean() == pytest.approx(4.908, abs=5e-4)
        assert cad.mean() == pytest.approx(1.592, abs=5e-4)

    def test_84_days_carry_no_cad_rate_and_19_no_aud_rate(self, result) -> None:
        """Measurement 2 on issue 346. All of 2012 for CAD, and April 2012 for AUD."""
        no_cad = result.days[result.cad == 0]
        no_aud = result.days[result.aud == 0]
        assert len(no_cad) == 84
        assert set(no_cad.year) == {2012}
        assert len(no_aud) == 19
        assert set(no_aud.strftime("%Y-%m")) == {"2012-04"}


class TestRows1And2WithRollover:
    def test_row_1_the_apr(self, result) -> None:
        apr = result.with_rollover.apr
        assert apr == pytest.approx(0.0615638271, abs=1e-10)
        assert matches(apr, SCRIPT_APR)
        assert matches(100 * apr, BOOK_APR_PERCENT)

    def test_row_2_the_sharpe_ratio(self, result) -> None:
        sharpe = result.with_rollover.sharpe
        assert sharpe == pytest.approx(0.5418018005, abs=1e-10)
        assert matches(sharpe, SCRIPT_SHARPE)
        assert matches(sharpe, BOOK_SHARPE)

    def test_the_figures_run_over_all_1237_rows_with_the_zeros(self, result) -> None:
        """Dropping rows 1 to 20 moves the APR off the script's six decimals."""
        assert len(result.returns) == 1237
        assert not matches(module.figures(result.returns[SCRIPT_LOOKBACK:]).apr, SCRIPT_APR)


class TestRows3And4WithoutRollover:
    def test_row_3_the_apr(self, result) -> None:
        apr = result.without_rollover.apr
        assert apr == pytest.approx(0.0671408367, abs=1e-10)
        assert matches(100 * apr, BOOK_APR_WITHOUT_PERCENT)

    def test_row_4_the_sharpe_ratio(self, result) -> None:
        sharpe = result.without_rollover.sharpe
        assert sharpe == pytest.approx(0.5845063318, abs=1e-10)
        assert matches(sharpe, BOOK_SHARPE_WITHOUT)


class TestRow5TheAnnualisedRollover:
    def test_row_5_misses_the_criterion(self, result) -> None:
        assert result.rollover == pytest.approx(0.0326416903, abs=1e-10)
        assert not result.rollover_holds
        assert result.rollover < ROLLOVER_FLOOR

    def test_row_5_is_the_term_line_43_adds_to_a_long_position(self, result) -> None:
        term = lag1(np.log(1 + result.aud) - np.log(1 + result.cad))
        term[0] = 0.0
        assert result.rollover == 252 * term.mean()

    def test_the_criterion_admits_its_floor_and_refuses_its_ceiling(self, result) -> None:
        for value, holds in ((0.045, True), (0.0499, True), (0.050, False), (0.0449, False)):
            moved = Rollover(**{**result.__dict__, "rollover": value})
            assert moved.rollover_holds is holds


class TestBesideTheReplication:
    """No source prints these, so none carries a gap or a verdict."""

    def test_the_rule_holds_short_on_707_days_and_long_on_510(self, result) -> None:
        """The positions behind rows 21 to 1,237. Short pays the differential and long earns it."""
        held = lag1(result.position)[SCRIPT_LOOKBACK:]
        assert len(held) == 1217
        assert (np.count_nonzero(held < 0), np.count_nonzero(held > 0)) == (707, 510)
        assert np.count_nonzero(held == 0) == 0

    def test_row_5_on_the_aud_rate_alone_lands_inside_the_criterion(self, result) -> None:
        assert result.aud_alone == pytest.approx(0.0466475912, abs=1e-10)
        assert ROLLOVER_FLOOR <= result.aud_alone < ROLLOVER_CEILING

    def test_row_5_annualised_over_365_days_lands_inside_the_criterion_too(self, result) -> None:
        """Row 8. The script divides each rate by 365, so this is a second reading of the book."""
        assert result.over_365_days == pytest.approx(0.0472786388, abs=1e-10)
        assert ROLLOVER_FLOOR <= result.over_365_days < ROLLOVER_CEILING
        assert result.over_365_days == annualised_rollover(result.aud, result.cad, days_a_year=365)

    def test_the_rollover_the_strategy_earned_is_a_cost_of_0_005221(self, result) -> None:
        """252 times the mean of line 43 less line 44, which the long and short counts explain."""
        assert result.rollover_drag == pytest.approx(-0.0052212787, abs=1e-10)

    def test_the_two_aprs_differ_by_more_than_the_rollover_the_strategy_earned(self, result):
        """Row 3 less row 1, which is not the rollover the strategy earned.

        The APR compounds the returns over 1,237 rows, while the rollover the
        strategy earned is 252 times their mean, so the two differ in size.
        """
        difference = result.without_rollover.apr - result.with_rollover.apr
        assert difference == pytest.approx(0.0055770095, abs=1e-10)
        assert abs(difference) > abs(result.rollover_drag) + 1e-4
        assert abs(result.rollover_drag) == pytest.approx(0.0052212787, abs=1e-10)

    def test_the_net_share_of_held_days_times_row_5_is_near_what_the_strategy_earned(
        self, result
    ) -> None:
        """(510 − 707) / 1,217 times row 5, beside the rollover the strategy earned.

        A long day earns the rate difference and a short day pays it, so the
        net share of days held long scales row 5 to the strategy's positions.
        """
        held = lag1(result.position)[SCRIPT_LOOKBACK:]
        net = (np.count_nonzero(held > 0) - np.count_nonzero(held < 0)) / len(held)
        assert net == pytest.approx((510 - 707) / 1217, abs=1e-15)
        assert net == pytest.approx(-0.161873, abs=5e-7)
        assert net * result.rollover == pytest.approx(-0.0052838233, abs=1e-10)
        assert result.rollover_drag == pytest.approx(-0.0052212787, abs=1e-10)

    def test_the_rate_difference_annualised_over_the_days_held_each_way(self, result) -> None:
        """252 times the mean of row 5's term over the days held long, then held short.

        The term is ``lag1(log(1 + aud) − log(1 + cad))``, over rows 21 onward.
        Long days and short days see nearly the same difference, which is why
        the net share of days alone explains the rollover the strategy earned.
        """
        held = lag1(result.position)[SCRIPT_LOOKBACK:]
        term = lag1(np.log(1 + result.aud) - np.log(1 + result.cad))[SCRIPT_LOOKBACK:]
        # The term rebuilt here is the one the run's returns carry, lags included.
        added = (result.returns - result.without)[SCRIPT_LOOKBACK:] / held
        np.testing.assert_allclose(added, term, rtol=0, atol=1e-15)
        assert 252 * term[held > 0].mean() == pytest.approx(0.0328995788, abs=1e-10)
        assert 252 * term[held < 0].mean() == pytest.approx(0.0328677609, abs=1e-10)

    def test_rows_1_and_2_with_each_missing_month_carried_forward(self, result) -> None:
        assert result.carried.apr == pytest.approx(0.0620850756, abs=1e-10)
        assert result.carried.sharpe == pytest.approx(0.5457420240, abs=1e-10)
        assert not matches(result.carried.apr, SCRIPT_APR)
        assert matches(100 * result.carried.apr, BOOK_APR_PERCENT)
        assert not matches(result.carried.sharpe, BOOK_SHARPE)
        assert matches(result.carried.sharpe, "0.55")


class TestTheRule:
    def test_a_month_the_file_lacks_gets_zero_rather_than_the_month_before(self) -> None:
        days = pd.DatetimeIndex(["2012-01-30", "2012-01-31", "2012-02-01", "2012-02-02"])
        rates = daily_rates(_monthly({"2012-01": 3.65}), days, triple_weekday=6)
        np.testing.assert_array_equal(rates, [3.65 / 365 / 100, 3.65 / 365 / 100, 0.0, 0.0])

    def test_months_out_of_order_carry_forward_the_latest_before_the_day(self) -> None:
        days = pd.DatetimeIndex(["2012-01-02", "2012-02-01", "2012-03-01", "2012-04-02"])
        monthly = _monthly({"2012-03": 1.0, "2012-01": 3.0})
        rates = daily_rates(monthly, days, triple_weekday=6, carry_forward=True)
        np.testing.assert_array_equal(rates, np.array([3.0, 3.0, 1.0, 1.0]) / 365 / 100)

    def test_carrying_forward_gives_a_missing_month_the_last_month_held(self) -> None:
        days = pd.DatetimeIndex(["2011-12-30", "2012-01-02", "2012-03-01"])
        rates = daily_rates(_monthly({"2012-01": 3.65}), days, triple_weekday=6, carry_forward=True)
        np.testing.assert_array_equal(rates, [0.0, 3.65 / 365 / 100, 3.65 / 365 / 100])

    def test_aud_triples_on_wednesday_only_and_cad_on_thursday_only(self) -> None:
        """2012-02-13 is a Monday, and the two weeks hold every weekday."""
        days = pd.bdate_range("2012-02-13", periods=10)
        monthly = _monthly({"2012-02": 3.65})
        base = 3.65 / 365 / 100
        for weekday in (AUD_TRIPLE_WEEKDAY, CAD_TRIPLE_WEEKDAY):
            rates = daily_rates(monthly, days, weekday)
            expected = np.where(days.weekday == weekday, 3 * base, base)
            np.testing.assert_array_equal(rates, expected)

    def test_a_weekday_holiday_multiplies_nothing(self) -> None:
        """Without Christmas Day 2008, a Thursday, its neighbours keep their own multiples."""
        days = pd.bdate_range("2008-12-22", "2008-12-31").drop(pd.Timestamp("2008-12-25"))
        base = 3.65 / 365 / 100
        cad = daily_rates(_monthly({"2008-12": 3.65}), days, CAD_TRIPLE_WEEKDAY)
        aud = daily_rates(_monthly({"2008-12": 3.65}), days, AUD_TRIPLE_WEEKDAY)
        assert list(cad / base) == pytest.approx([1, 1, 1, 1, 1, 1, 1])
        assert list(aud / base) == pytest.approx([1, 1, 3, 1, 1, 1, 3])

    def test_the_rate_is_divided_by_365_then_by_100(self) -> None:
        days = pd.DatetimeIndex(["2012-02-13"])
        rate = 5.476190476190476
        assert daily_rates(_monthly({"2012-02": rate}), days, 6)[0] == rate / 365 / 100

    def test_day_t_carries_day_t_minus_1s_position_and_rates(self) -> None:
        closes = _closes()
        position = -np.sign(zscore(closes, SCRIPT_LOOKBACK))
        aud = np.full(len(closes), 0.0002)
        cad = np.full(len(closes), 0.0001)
        base = linear_returns(closes, position, aud, cad)
        t = 40
        for moved in (
            linear_returns(closes, position, np.where(np.arange(60) == t, 0.01, aud), cad),
            linear_returns(closes, position, aud, np.where(np.arange(60) == t, 0.01, cad)),
            linear_returns(closes, np.where(np.arange(60) == t, -position, position), aud, cad),
        ):
            assert moved[t] == base[t]
            assert moved[t + 1] != base[t + 1]

    def test_the_position_is_the_sign_so_doubling_every_distance_moves_no_return(self) -> None:
        closes = _closes()
        z = zscore(closes, SCRIPT_LOOKBACK)
        zero = np.zeros(len(closes))
        once = linear_returns(closes, -np.sign(z), zero, zero)
        twice = linear_returns(closes, -np.sign(2 * z), zero, zero)
        linear = linear_returns(closes, -z, zero, zero)
        np.testing.assert_array_equal(once, twice)
        assert not np.array_equal(once, linear)

    def test_a_constant_scale_on_every_close_moves_no_figure(self, sources, result) -> None:
        """Log moves and the sign of z cannot see it, so rows 1 to 4 are no evidence about scale."""
        scaled = aud_cad_rollover(1.7 * sources.closes[1], sources.aud[1], sources.cad[1])
        for moved, held in (
            (scaled.with_rollover, result.with_rollover),
            (scaled.without_rollover, result.without_rollover),
        ):
            assert moved.apr == pytest.approx(held.apr, abs=1e-12)
            assert moved.sharpe == pytest.approx(held.sharpe, abs=1e-12)

    def test_rows_1_to_20_return_zero(self, result) -> None:
        assert (result.returns[:SCRIPT_LOOKBACK] == 0).all()
        assert (result.without[:SCRIPT_LOOKBACK] == 0).all()
        assert result.returns[SCRIPT_LOOKBACK] != 0

    def test_the_returns_are_line_43_bit_for_bit(self, result, sources) -> None:
        """``log(1 + x)`` rather than ``log1p``, and the line's own order of additions."""
        cl = sources.closes[1].to_numpy()
        aud, cad = result.aud, result.cad
        line_43 = lag1(-np.sign(zscore(cl, SCRIPT_LOOKBACK))) * (
            np.log(cl) + lag1(-np.log(cl) + np.log(1 + aud) - np.log(1 + cad))
        )
        line_43 = np.where(np.isnan(line_43), 0.0, line_43)
        np.testing.assert_array_equal(result.returns, line_43)

    def test_zscore_is_the_distance_in_moving_deviations(self) -> None:
        closes = np.array([1.0, 2.0, 3.0, 5.0])
        z = zscore(closes, 3)
        assert np.isnan(z[:2]).all()
        assert z[2] == (3.0 - 2.0) / 1.0
        assert z[3] == pytest.approx((5.0 - 10.0 / 3.0) / np.std([2.0, 3.0, 5.0], ddof=1))

    def test_zero_rates_give_line_44_bit_for_bit(self, result, sources) -> None:
        cl = sources.closes[1].to_numpy()
        line_44 = lag1(-np.sign(zscore(cl, SCRIPT_LOOKBACK))) * (np.log(cl) + lag1(-np.log(cl)))
        line_44 = np.where(np.isnan(line_44), 0.0, line_44)
        np.testing.assert_array_equal(result.without, line_44)

    def test_the_aud_rate_alone_is_row_5_with_cad_at_zero(self, result) -> None:
        assert result.aud_alone == annualised_rollover(result.aud, np.zeros_like(result.cad))


class TestTheGuardAndTheReads:
    def test_read_sources_runs_the_guard_on_the_closes_over_the_whole_file(
        self, monkeypatch
    ) -> None:
        seen = []

        def record(legs, *, start, end):
            seen.append(([entry.symbol for entry, _ in legs], start, end))

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", record)
        read_sources()
        assert seen == [(["AUDCAD"], pd.Timestamp("2007-07-23"), pd.Timestamp("2012-04-26"))]

    def test_the_guard_passes_the_committed_file(self) -> None:
        """No flagged day sits in the file, so the unpatched read refuses nothing."""
        read_sources()

    def test_main_turns_a_guard_refusal_into_one_line(self, monkeypatch, no_arguments):
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("inputData_AUDCAD_20120426.csv changes scale")

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(SystemExit, match="AUDCAD_20120426.csv changes scale"):
            main()

    def test_run_reads_the_directory_it_is_given(self, tmp_path) -> None:
        with pytest.raises(VintageUnavailable):
            run(tmp_path)

    def test_all_three_reads_come_from_the_directory_given(self, tmp_path, monkeypatch) -> None:
        """The default directory is emptied, so a read that ignored ``data_dir`` would fail."""
        directory = committed_copy(tmp_path)
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path / "empty")
        found = read_sources(directory)
        assert [entry.symbol for entry in found.entries] == ["AUDCAD", "AUDRATE", "CADRATE"]

    def test_main_leaves_any_other_error_its_traceback(self, monkeypatch, no_arguments) -> None:
        def broken(*args):
            raise ValueError("a bug in the run")

        monkeypatch.setattr(module, "aud_cad_rollover", broken)
        with pytest.raises(ValueError, match="a bug in the run"):
            main()

    def test_a_miss_is_reported_as_one(self) -> None:
        assert module._verdict(0.07, SCRIPT_APR) == "did not reproduce, gap +0.008436"
        assert module._verdict(0.0615638, SCRIPT_APR) == "reproduced"

    def test_main_turns_a_missing_vintage_into_one_line(
        self, monkeypatch, tmp_path, no_arguments
    ) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit):
            main()

    def test_the_report_gives_each_row_its_verdict(self, capsys, no_arguments) -> None:
        main()
        out = capsys.readouterr().out
        reproduced = [line for line in out.splitlines() if line.rstrip().endswith("reproduced")]
        assert len(reproduced) == 6
        assert "5 annualised rollover" in out
        assert out.count("  vintage  ") == 3
        for name in ("inputData_AUDCAD_20120426", "AUD_interestRate", "CAD_interestRate"):
            assert f"pythoncodesanddata/{name}.csv" in out
        assert "window   2007-07-23 to 2012-04-26, 1237 days" in out
        printed = {
            "1 APR with rollover, script": "0.061564",
            "1 APR percent, book": "6.2",
            "2 Sharpe with rollover, script": "0.541802",
            "2 Sharpe, book": "0.54",
            "3 APR percent without, book": "6.7",
            "4 Sharpe without, book": "0.58",
        }
        for label, chan in printed.items():
            (line,) = [line for line in out.splitlines() if label in line]
            assert line.split()[-2:] == [chan, "reproduced"]
        assert "0.032642  almost 5 percent  did not reproduce" in out
        assert "19 days carry no AUD rate and 84 no CAD rate" in out
        assert "row 5 on the AUD rate alone      0.046648" in out
        assert "row 5 annualised over 365 days   0.047279" in out
        assert "rollover the strategy earned     -0.005221 a year" in out
        assert "APR 0.062085, Sharpe 0.545742" in out
        assert "Exploratory." in out
