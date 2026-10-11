"""The pins for long GLD and short gold futures, *Algorithmic Trading*'s locations 2718 and 2730.

This file is the single authority for every number a prose surface quotes
about this experiment and the rows beside it. ``docs/replication-log.md``
Entry 38 carries the verdicts and points here row by row. The rows are the ones
[issue 355](https://github.com/l3a0/quantitative-trading/issues/355) declared
under "The specification, declared before any figure".

Every pin on the committed files reads the same two vintages and one
specification unless it names another vintage, so they are stated once here
and carried in each figure's failure message as :data:`SPEC`. B1's pins
carry :data:`B1_SPEC` the same way.

- **GC.** ``inputdata_gc_1600_20100802/gc.csv``, chan-mat, raw, saved
  2012-05-07, 761 rows from 2007-08-03 to 2010-08-02, read as
  ``load_panel("inputData_GC_1600_20100802.mat")["GC"]``.
- **GLD.** ``inputdata_etf/gld.csv``, chan-mat, adjusted, saved 2012-04-10,
  read as ``load_panel("inputData_ETF.mat")["GLD"]``.
- **The third vintage.** ``inputdataohlcdaily_20120507/gc.csv``, chan-mat,
  adjusted, saved 2012-05-09, read only by ``TestTheSeriesIdentity``.
- **B1's vintage.** FRED's TB3MS, ``rate``, downloaded 2026-09-30, read only
  by ``TestTheFinancingCost``.
- **Specification S.** ``GLD_GC.m`` as shipped: the two calendars
  intersected, ``ret`` GLD's return minus GC's on the kept rows with NaN set
  to 0, and the script's five printed figures, with ``rf = 0.02 / 252`` in
  the Sharpe ratio and book two's divide-by-n ``smartstd``.

Each computed figure is held at six decimals, so a change cannot move it inside
the book's rounding unnoticed, and each printed figure at the precision the
book printed, through ``matches`` and ``gap``. ``TestTheArithmetic`` holds
every step of S on synthetic legs whose figures are computed here by hand, so a
flipped sign, an n − 1 deviation, a dropped first row or a 251 each fails.

``blog/gld-gc-lessons.md`` quotes most of these figures, so a change to any of
them moves that post too. ``TestWhatThePostMeasured`` holds the numbers the
post added, all measured after the run, and ``TestThePostsHelpers`` holds the
three helpers they come through on synthetic legs.
``tests/test_gld_gc_figures.py`` holds what the post's figure draws.

Exploratory. The window is the book's own. It first ran here on 2026-10-10.
"""

from __future__ import annotations

import dataclasses
import io
import math
import statistics
from contextlib import redirect_stdout

import numpy as np
import pandas as pd
import pytest

from chan import bill_rates, paths
from chan import gld_gc as module
from chan.gld_gc import (
    BOOK_APR,
    BOOK_AVERAGE_ANNUAL_RETURN,
    BOOK_MAX_DRAWDOWN,
    BOOK_MAX_DRAWDOWN_DAYS,
    BOOK_SHARPE,
    BOOK_TEXT_MAX_DRAWDOWN_PERCENT,
    BOOK_TEXT_RETURN_PERCENT,
    FINANCING_MONTHS,
    GC_ONLY_HOLIDAYS,
    GC_SOURCE_FILE,
    GLD_SOURCE_FILE,
    OHLC_SOURCE_FILE,
    RISK_FREE_RATE,
    STEP,
    WINDOW_END,
    WINDOW_START,
    Financing,
    GldGc,
    Identity,
    Sources,
    bill_accrual,
    by_year,
    common_days,
    daily_returns,
    figures,
    financing,
    gld_gc,
    identity,
    log_ratio_changes,
    main,
    ratio_steps,
    read_ohlc_gc,
    read_sources,
    run,
)
from chan.khandani_lo_book_two import gap, matches
from chan.matlab_helpers import drawdown_path
from chan.series import WindowCrossesScaleBreak, load_panel, scale_breaks
from tests.support.committed_vintages import LIFTED_SOURCES

SPEC = (
    "inputdata_gc_1600_20100802/gc.csv chan-mat raw saved 2012-05-07 against "
    "inputdata_etf/gld.csv chan-mat adjusted saved 2012-04-10, GLD_GC.m as shipped: "
    "intersected calendars, GLD's return minus GC's with NaN set to 0, rf = 0.02/252"
)
B1_SPEC = (
    "FRED TB3MS basis rate downloaded 2026-09-30, the monthly three-month bill rate "
    "averaged over 2007-08 to 2010-08, both months included"
)
#: The vintage the bill curve and the split by year read, each month's rate over 252 a day.
BILLS_SPEC = (
    "FRED TB3MS basis rate downloaded 2026-09-30, each kept day earning its month's rate "
    "over 252, the first row 0"
)
AFTER_THE_RUN = "measured by the write-up after the run, so exploratory like the rest"


@pytest.fixture(scope="module")
def sources() -> Sources:
    return read_sources()


@pytest.fixture(scope="module")
def result(sources) -> GldGc:
    return gld_gc(sources)


@pytest.fixture(scope="module")
def b1(result) -> Financing:
    return financing(result)


@pytest.fixture(scope="module")
def found(sources, result) -> Identity:
    return identity(sources, result)


@pytest.fixture
def no_arguments(monkeypatch):
    """``main`` parses ``sys.argv``, which under pytest holds pytest's own arguments."""
    monkeypatch.setattr("sys.argv", ["chan.gld_gc"])


def closes(values: list[float], days: list[str]) -> pd.Series:
    return pd.Series(values, index=pd.DatetimeIndex(days), dtype=float)


class TestTheArithmetic:
    """Every step of S on synthetic legs, against figures computed here by hand."""

    GLD = [100.0, 102.0, 101.0, 103.02]
    GC = [1000.0, 1010.0, 1015.05, 1005.0]

    def by_hand(self) -> list[float]:
        """GLD's simple return minus GC's, row by row, with the first row 0."""
        ret = [0.0]
        for t in range(1, 4):
            ret.append((self.GLD[t] / self.GLD[t - 1] - 1) - (self.GC[t] / self.GC[t - 1] - 1))
        return ret

    def test_the_return_is_long_gld_and_short_gc(self) -> None:
        ret = daily_returns(self.GLD, self.GC)
        np.testing.assert_allclose(ret, self.by_hand(), rtol=0, atol=1e-15)
        assert ret[1] == pytest.approx(0.02 - 0.01, abs=1e-15)

    def test_the_first_row_is_zero_and_kept(self) -> None:
        """The script zeroes the first row's NaN rather than dropping it, so n is 4, not 3."""
        ret = daily_returns(self.GLD, self.GC)
        assert len(ret) == 4
        assert ret[0] == 0.0

    def test_every_nan_is_zero_not_only_the_first(self) -> None:
        """``ret(isnan(ret))=0`` reaches a missing close too, and the row after it."""
        ret = daily_returns([100.0, np.nan, 101.0, 102.0], [10.0, 10.0, 10.0, 10.0])
        assert ret.tolist() == [0.0, 0.0, 0.0, pytest.approx(102 / 101 - 1, abs=1e-15)]

    def test_a_lag_padded_with_zeros_gives_the_same_returns(self, monkeypatch) -> None:
        """LeSage's ``lag`` pads with 0, so row 1 is infinity minus infinity, NaN, then 0."""
        padded_with_nan = daily_returns(self.GLD, self.GC)
        seen = []

        def padded_with_zeros(x):
            values = np.asarray(x, dtype=float)
            seen.append(values)
            return np.concatenate(([0.0], values[:-1]))

        monkeypatch.setattr(module, "lag1", padded_with_zeros)
        found = daily_returns(self.GLD, self.GC)
        assert len(seen) == 2
        assert found.tolist() == padded_with_nan.tolist()
        assert found[0] == 0.0

    def test_mismatched_legs_are_refused(self) -> None:
        with pytest.raises(ValueError, match="one shape"):
            daily_returns([1.0, 2.0], [1.0, 2.0, 3.0])

    def test_the_five_figures(self) -> None:
        ret = self.by_hand()
        excess = [r - 0.02 / 252 for r in ret]
        found = figures(daily_returns(self.GLD, self.GC))
        assert RISK_FREE_RATE == 0.02 / 252
        assert found.average_annual_return == pytest.approx(252 * statistics.fmean(ret), rel=1e-12)
        assert found.sharpe == pytest.approx(
            math.sqrt(252) * statistics.fmean(excess) / statistics.pstdev(excess), rel=1e-12
        )
        assert found.apr == pytest.approx(math.prod(1 + r for r in ret) ** (252 / 4) - 1, rel=1e-12)

    def test_the_sharpe_ratio_differs_from_an_n_minus_1_one(self) -> None:
        """So the divide-by-n ``smartstd`` is what the test above holds, not a near miss."""
        excess = [r - 0.02 / 252 for r in self.by_hand()]
        sample = math.sqrt(252) * statistics.fmean(excess) / statistics.stdev(excess)
        assert figures(self.by_hand()).sharpe != pytest.approx(sample, rel=1e-3)

    def test_the_drawdown_and_its_duration(self) -> None:
        """A high on day 1, two days below it at worst −2 percent, then a new high."""
        found = figures([0.0, 0.01, -0.02, 0.005, 0.03])
        assert found.max_drawdown == pytest.approx(-0.02, abs=1e-15)
        assert found.max_drawdown_days == 2

    def test_the_calendars_meet_on_common_days_and_returns_span_the_gaps(self) -> None:
        """Each leg's missing day drops the row from both, and the return spans the gap."""
        gc = closes(
            [10.0, 11.0, 12.0, 13.0], ["2020-01-02", "2020-01-03", "2020-01-06", "2020-01-07"]
        )
        gld = closes(
            [20.0, 21.0, 23.0, 24.0], ["2020-01-02", "2020-01-06", "2020-01-07", "2020-01-08"]
        )
        sources = Sources(gc_entry=None, gc=gc, gld_entry=None, gld=gld)  # type: ignore[arg-type]
        found = gld_gc(sources)
        assert [str(d.date()) for d in found.days] == ["2020-01-02", "2020-01-06", "2020-01-07"]
        assert found.daily.tolist() == pytest.approx(
            [0.0, (21 / 20 - 1) - (12 / 10 - 1), (23 / 21 - 1) - (13 / 12 - 1)], abs=1e-15
        )

    def test_the_common_days_come_back_sorted(self) -> None:
        gc = closes([1.0, 2.0, 3.0], ["2020-01-07", "2020-01-02", "2020-01-06"])
        gld = closes([1.0, 2.0, 3.0], ["2020-01-06", "2020-01-07", "2020-01-02"])
        assert [str(d.date()) for d in common_days(gc, gld)] == [
            "2020-01-02",
            "2020-01-06",
            "2020-01-07",
        ]

    def test_the_ratio_steps(self) -> None:
        """log(GC / GLD) moves by ln 1.03 on day 2 and 0 on day 3, so one step past 2 percent."""
        days = ["2020-01-02", "2020-01-03", "2020-01-06"]
        found = ratio_steps(
            closes([10.0, 10.3, 10.3], days), closes([1.0, 1.0, 1.0], days), pd.DatetimeIndex(days)
        )
        assert STEP == 0.02
        assert found.days == 3
        assert found.largest == pytest.approx(math.log(1.03), abs=1e-15)
        assert found.spread == pytest.approx(math.log(1.03) / 2, abs=1e-15)
        assert found.steps == 1

    def test_the_largest_move_is_measured_in_size(self) -> None:
        """A fall of ln(10.3 / 9.5) outweighs a rise of ln 1.03, so the largest move is the fall."""
        days = ["2020-01-02", "2020-01-03", "2020-01-06"]
        found = ratio_steps(
            closes([10.0, 10.3, 9.5], days), closes([1.0, 1.0, 1.0], days), pd.DatetimeIndex(days)
        )
        assert found.largest == pytest.approx(math.log(10.3 / 9.5), abs=1e-15)
        assert found.steps == 2

    def test_a_move_of_exactly_the_step_is_not_past_it(self, monkeypatch) -> None:
        """Past 2 percent means larger than it, so a move landing on the threshold is not counted.

        No float close makes log(GC / GLD) move by exactly 0.02, so the threshold
        is set to the move the synthetic legs make, through the same arithmetic
        :func:`ratio_steps` uses.
        """
        days = ["2020-01-02", "2020-01-03"]
        gc, gld = closes([10.0, 10.3], days), closes([1.0, 1.0], days)
        move = float(np.diff(np.log(gc.to_numpy() / gld.to_numpy()))[0])
        monkeypatch.setattr(module, "STEP", move)
        assert ratio_steps(gc, gld, pd.DatetimeIndex(days)).steps == 0
        monkeypatch.setattr(module, "STEP", np.nextafter(move, 0.0))
        assert ratio_steps(gc, gld, pd.DatetimeIndex(days)).steps == 1


class TestTheVintages:
    def test_gc_is_its_pinned_source(self, sources) -> None:
        vendor, basis, saved, folder, count = LIFTED_SOURCES[GC_SOURCE_FILE]
        assert GC_SOURCE_FILE == "inputData_GC_1600_20100802.mat"
        assert (vendor, basis, saved, folder, count) == (
            "chan-mat",
            "raw",
            "2012-05-07",
            "inputdata_gc_1600_20100802",
            1,
        )
        entry = sources.gc_entry
        assert entry.path == "inputdata_gc_1600_20100802/gc.csv"
        assert (entry.vendor, entry.price_basis, entry.obtained) == (vendor, basis, saved)

    def test_gld_is_its_pinned_source(self, sources) -> None:
        vendor, basis, saved, folder, _ = LIFTED_SOURCES[GLD_SOURCE_FILE]
        assert GLD_SOURCE_FILE == "inputData_ETF.mat"
        assert (vendor, basis, saved, folder) == (
            "chan-mat",
            "adjusted",
            "2012-04-10",
            "inputdata_etf",
        )
        entry = sources.gld_entry
        assert entry.path == "inputdata_etf/gld.csv"
        assert (entry.vendor, entry.price_basis, entry.obtained) == (vendor, basis, saved)

    def test_gc_holds_761_rows_over_the_book_s_window(self, sources) -> None:
        assert len(sources.gc) == 761
        assert (sources.gc.index[0], sources.gc.index[-1]) == (WINDOW_START, WINDOW_END)
        assert (WINDOW_START, WINDOW_END) == (
            pd.Timestamp("2007-08-03"),
            pd.Timestamp("2010-08-02"),
        )
        assert not sources.gc.isna().any()

    def test_gld_holds_755_rows_in_the_window_and_no_nan(self, sources) -> None:
        window = sources.gld.loc[WINDOW_START:WINDOW_END]
        assert len(window) == 755
        assert not window.isna().any()

    def test_s_runs_on_752_days(self, result) -> None:
        assert len(result.days) == 752
        assert (result.days[0], result.days[-1]) == (WINDOW_START, WINDOW_END)
        assert result.days.is_monotonic_increasing


class TestTheBooksFigures:
    """S against the script's five printed figures and the text's two."""

    def test_the_printed_figures(self) -> None:
        assert (BOOK_AVERAGE_ANNUAL_RETURN, BOOK_SHARPE, BOOK_APR, BOOK_MAX_DRAWDOWN) == (
            "0.0190",
            "-0.07",
            "0.0191",
            "-0.008247",
        )
        assert BOOK_MAX_DRAWDOWN_DAYS == 91
        assert (BOOK_TEXT_RETURN_PERCENT, BOOK_TEXT_MAX_DRAWDOWN_PERCENT) == ("1.9", "0.8")

    def test_row_1_the_average_annual_return_reproduces(self, result) -> None:
        found = result.figures.average_annual_return
        assert found == pytest.approx(0.019014, abs=5e-7), SPEC
        assert matches(found, BOOK_AVERAGE_ANNUAL_RETURN)
        assert gap(found, BOOK_AVERAGE_ANNUAL_RETURN) == 0.0

    def test_row_2_the_sharpe_ratio_reproduces(self, result) -> None:
        found = result.figures.sharpe
        assert found == pytest.approx(-0.066564, abs=5e-7), SPEC
        assert matches(found, BOOK_SHARPE)
        assert gap(found, BOOK_SHARPE) == 0.0

    def test_row_3_the_apr_reproduces(self, result) -> None:
        found = result.figures.apr
        assert found == pytest.approx(0.019084, abs=5e-7), SPEC
        assert matches(found, BOOK_APR)
        assert gap(found, BOOK_APR) == 0.0

    def test_row_4_the_maximum_drawdown_reproduces(self, result) -> None:
        found = result.figures.max_drawdown
        assert found == pytest.approx(-0.0082465, abs=5e-8), SPEC
        assert matches(found, BOOK_MAX_DRAWDOWN)
        assert gap(found, BOOK_MAX_DRAWDOWN) == 0.0

    def test_row_5_the_drawdown_lasts_91_days(self, result) -> None:
        assert result.figures.max_drawdown_days == BOOK_MAX_DRAWDOWN_DAYS == 91, SPEC

    def test_row_6_the_text_s_1_9_percent_reproduces_on_both_returns(self, result) -> None:
        """The text says "annualized return" and the script prints two, so both are checked."""
        found = result.figures
        assert 100 * found.average_annual_return == pytest.approx(1.901433, abs=5e-7), SPEC
        assert 100 * found.apr == pytest.approx(1.908382, abs=5e-7), SPEC
        assert matches(100 * found.average_annual_return, BOOK_TEXT_RETURN_PERCENT)
        assert matches(100 * found.apr, BOOK_TEXT_RETURN_PERCENT)

    def test_row_7_the_text_s_0_8_percent_reproduces(self, result) -> None:
        found = -100 * result.figures.max_drawdown
        assert found == pytest.approx(0.824652, abs=5e-7), SPEC
        assert matches(found, BOOK_TEXT_MAX_DRAWDOWN_PERCENT)
        assert gap(found, BOOK_TEXT_MAX_DRAWDOWN_PERCENT) == 0.0

    def test_the_sharpe_ratio_rounds_to_the_book_only_with_the_risk_free_rate(self, result) -> None:
        """Without ``rf`` it is positive, so the book's −0.07 holds the subtraction."""
        assert figures(result.daily, risk_free=0.0).sharpe > 0

    def test_a_miss_is_reported_as_one(self) -> None:
        assert module._verdict(-0.0666, "-0.07") == "reproduced"
        assert module._verdict(-0.0566, "-0.07") == "did not reproduce, gap +0.01"
        assert module._days_verdict(91, 91) == "reproduced"
        assert module._days_verdict(93, 91) == "did not reproduce, gap +2"


class TestTheFinancingCost:
    """B1, declared beside S and carrying no verdict."""

    def test_the_bills_are_the_september_download(self) -> None:
        entry = bill_rates.bill_vintage()
        assert (entry.vendor, entry.symbol, entry.price_basis) == ("fred", "TB3MS", "rate")
        assert entry.obtained == "2026-09-30"

    def test_the_bill_rate_over_the_window(self, b1) -> None:
        assert FINANCING_MONTHS == ("2007-08", "2010-08")
        assert b1.months == 37, B1_SPEC
        assert b1.bill_rate == pytest.approx(0.010141, abs=5e-7), B1_SPEC

    def test_what_is_left_above_it(self, b1, result) -> None:
        assert b1.average_annual_return == result.figures.average_annual_return
        assert b1.excess == pytest.approx(0.008874, abs=5e-7), f"{SPEC}, less {B1_SPEC}"


class TestTheSeriesIdentity:
    """What says the GC file is read at GLD's close rather than at the 1:30 p.m. settlement."""

    def test_gc_holds_9_us_exchange_holidays_gld_lacks(self, found) -> None:
        assert [str(day.date()) for day in found.gc_only] == list(GC_ONLY_HOLIDAYS)
        assert len(GC_ONLY_HOLIDAYS) == 9

    def test_each_holiday_carries_its_own_name(self) -> None:
        """The weekday test below cannot tell one Monday holiday from another."""
        assert GC_ONLY_HOLIDAYS == {
            "2007-11-22": "Thanksgiving",
            "2008-01-21": "Martin Luther King Jr. Day",
            "2008-02-18": "Presidents' Day",
            "2008-05-26": "Memorial Day",
            "2008-07-04": "Independence Day",
            "2008-09-01": "Labor Day",
            "2008-11-27": "Thanksgiving",
            "2009-01-19": "Martin Luther King Jr. Day",
            "2009-02-16": "Presidents' Day",
        }

    def test_the_holidays_are_named_for_the_day_they_fall_on(self) -> None:
        """Each one falls on the weekday its holiday's rule puts it on."""
        weekdays = {day: pd.Timestamp(day).day_name() for day in GC_ONLY_HOLIDAYS}
        for day, name in GC_ONLY_HOLIDAYS.items():
            if name == "Thanksgiving":
                assert weekdays[day] == "Thursday"
            elif name == "Independence Day":
                assert day.endswith("-07-04")
            else:
                assert weekdays[day] == "Monday"

    def test_gld_holds_3_days_gc_lacks(self, found) -> None:
        assert [str(day.date()) for day in found.gld_only] == [
            "2007-09-19",
            "2007-12-24",
            "2009-12-24",
        ]

    def test_752_is_761_less_the_9_holidays(self, sources, result, found) -> None:
        assert len(sources.gc) - len(found.gc_only) == len(result.days) == 752

    def test_the_ohlc_save_s_gc_never_equals_it(self, found) -> None:
        assert OHLC_SOURCE_FILE == "inputDataOHLCDaily_20120507.mat"
        entry = found.ohlc_entry
        assert entry.path == "inputdataohlcdaily_20120507/gc.csv"
        assert (entry.vendor, entry.price_basis, entry.obtained) == (
            "chan-mat",
            "adjusted",
            "2012-05-09",
        )
        assert found.shared_with_ohlc == 752
        assert found.equal_to_ohlc == 0
        assert found.smallest_difference == pytest.approx(9.30, abs=5e-3)

    def test_their_daily_returns_correlate_at_0_82(self, found) -> None:
        assert found.return_correlation == pytest.approx(0.824035, abs=5e-7)

    def test_their_difference_reverses_the_next_day(self, found) -> None:
        """A gap in timing makes the daily change reverse, and a step at a roll does not."""
        assert found.difference_reversal == pytest.approx(-0.559953, abs=5e-7)

    def test_the_ratio_s_first_and_last_values(self, found) -> None:
        """The issue's disclosure printed these before the criterion was written."""
        assert found.first_ratio == pytest.approx(10.822, abs=5e-4)
        assert found.last_ratio == pytest.approx(10.235, abs=5e-4)

    def test_the_log_ratio_moves_little_on_the_16_00_series(self, found) -> None:
        steps = found.sampled_at_1600
        assert steps.days == 752
        assert steps.spread == pytest.approx(0.000933, abs=5e-7)
        assert steps.largest == pytest.approx(0.007082, abs=5e-7)
        assert steps.steps == 0

    def test_the_log_ratio_moves_ten_times_as_much_on_the_ohlc_save(self, found) -> None:
        steps = found.ohlc
        assert steps.days == 752
        assert steps.spread == pytest.approx(0.009243, abs=5e-7)
        assert steps.largest == pytest.approx(0.097332, abs=5e-7)
        assert steps.steps == 20

    def test_a_gap_between_the_closes_carries_at_most_0_18_percent_of_gld_s_variance(
        self, found
    ) -> None:
        """Half the squared ratio of the log ratio's spread to GLD's own daily spread."""
        assert found.gld_spread == pytest.approx(0.015660, abs=5e-7)
        assert found.gap_share == pytest.approx(0.001775, abs=5e-7)
        assert found.gap_share == pytest.approx(
            (found.sampled_at_1600.spread / found.gld_spread) ** 2 / 2, rel=1e-12
        )


@pytest.fixture(scope="module")
def cumret(result) -> np.ndarray:
    """S's ``cumprod(1 + ret) − 1``, the series ``calculateMaxDD`` reads."""
    return np.cumprod(1 + result.daily) - 1


@pytest.fixture(scope="module")
def ohlc_gc() -> pd.Series:
    return read_ohlc_gc()[1]


def _on(days: pd.DatetimeIndex, row: int) -> str:
    return str(days[row].date())


class TestWhatThePostMeasured:
    """Numbers ``blog/gld-gc-lessons.md`` quotes that no row of Entry 38 declared.

    The write-up measured every one of them after the run, on the same
    vintages and specification as the rows above, so each is exploratory and
    none carries a verdict. The split by calendar year in particular was
    chosen after seeing the run.
    """

    def test_the_sharpe_ratio_at_no_rate_and_at_the_window_s_bill_rate(self, result, b1) -> None:
        """The script's 2 percent is a constant, so the sign of its Sharpe ratio is arithmetic."""
        assert f"{figures(result.daily, risk_free=0.0).sharpe:.6f}" == "1.284060", (
            f"{SPEC}, rf = 0; {AFTER_THE_RUN}"
        )
        at_bills = figures(result.daily, risk_free=b1.bill_rate / 252).sharpe
        assert f"{at_bills:.6f}" == "0.599257", f"{SPEC}, rf = B1 / 252; {AFTER_THE_RUN}"

    def test_any_rate_above_the_return_turns_the_sharpe_ratio_negative(self, result) -> None:
        """The break-even rate is the mean return itself, 1.9014 percent a year."""
        mean = result.figures.average_annual_return
        assert f"{100 * mean:.4f}" == "1.9014", SPEC
        assert figures(result.daily, risk_free=mean / 252).sharpe == pytest.approx(0, abs=1e-12)
        assert figures(result.daily, risk_free=(mean + 1e-4) / 252).sharpe < 0
        assert figures(result.daily, risk_free=(mean - 1e-4) / 252).sharpe > 0

    def test_the_script_s_2_percent_is_105_18_percent_of_the_return(self, result) -> None:
        share = 100 * RISK_FREE_RATE * 252 / result.figures.average_annual_return
        assert f"{share:.2f}" == "105.18", f"{SPEC}; {AFTER_THE_RUN}"

    def test_the_bill_rate_takes_0_533311_of_the_return(self, b1) -> None:
        share = b1.bill_rate / b1.average_annual_return
        assert f"{share:.6f}" == "0.533311", f"{SPEC}, against {B1_SPEC}; {AFTER_THE_RUN}"

    def test_the_return_fell_with_the_bill_rate_year_by_year(self, result) -> None:
        """Each year's rows, less the zeroed first row, against the months they span."""
        table = [
            (y.year, y.rows, f"{y.average_annual_return:.6f}", f"{y.bill_rate:.6f}")
            for y in by_year(result)
        ]
        assert table == [
            (2007, 101, "0.052235", "0.036520"),
            (2008, 253, "0.027315", "0.013650"),
            (2009, 251, "0.005822", "0.001500"),
            (2010, 146, "0.004458", "0.001350"),
        ], f"{SPEC}, against {B1_SPEC} by calendar year; {AFTER_THE_RUN}"
        assert sum(row for _, row, _, _ in table) == len(result.days) - 1

    def test_the_excess_shrinks_from_1_57_points_to_0_31(self, result) -> None:
        excess = [f"{100 * y.excess:.2f}" for y in by_year(result)]
        assert (excess[0], excess[-1]) == ("1.57", "0.31"), f"{SPEC}; {AFTER_THE_RUN}"

    def test_the_bill_rate_sat_below_half_a_percent_in_22_of_37_months(self) -> None:
        first, last = FINANCING_MONTHS
        assert bill_rates.months_below(0.005, first, last) == 22, B1_SPEC
        below = [
            month
            for month, rate in bill_rates.monthly_rates()
            if first <= month <= last and rate < 0.005
        ]
        assert (below[0], below[-1], len(below)) == ("2008-11", "2010-08", 22), B1_SPEC

    def test_the_deepest_drawdown_is_mostly_one_day(self, result, cumret) -> None:
        """A high on 2007-10-12, the trough on 2007-11-12 and a new high on 2007-11-14."""
        _, drawdown, _ = drawdown_path(cumret)
        trough = int(np.argmin(drawdown))
        high = int(np.argmax(cumret[: trough + 1]))
        recovered = trough + int(np.argmax(drawdown[trough:] == 0))
        assert (_on(result.days, high), _on(result.days, trough), _on(result.days, recovered)) == (
            "2007-10-12",
            "2007-11-12",
            "2007-11-14",
        ), f"{SPEC}; {AFTER_THE_RUN}"
        assert drawdown[trough] == result.figures.max_drawdown

    def test_on_the_trough_day_gld_fell_further_than_gc(self, result) -> None:
        row = result.days.get_loc(pd.Timestamp("2007-11-12"))
        gld = result.gld[row] / result.gld[row - 1] - 1
        gc = result.gc[row] / result.gc[row - 1] - 1
        assert (f"{100 * result.daily[row]:.4f}", f"{100 * gld:.4f}", f"{100 * gc:.4f}") == (
            "-0.6771",
            "-4.7213",
            "-4.0442",
        ), f"{SPEC}; {AFTER_THE_RUN}"

    def test_the_91_days_are_another_drawdown_and_a_shallower_one(self, result, cumret) -> None:
        """The longest stretch below a high runs 2009-08-28 to 2010-01-08 and reaches −0.40907%."""
        _, drawdown, duration = drawdown_path(cumret)
        last = int(np.argmax(duration))
        first = last - int(duration[last]) + 1
        assert (_on(result.days, first), _on(result.days, last), int(duration[last])) == (
            "2009-08-28",
            "2010-01-08",
            91,
        ), f"{SPEC}; {AFTER_THE_RUN}"
        assert f"{100 * drawdown[first : last + 1].min():.5f}" == "-0.40907", (
            f"{SPEC}; {AFTER_THE_RUN}"
        )

    def test_the_16_00_series_moves_most_on_the_trough_day(self, sources, result) -> None:
        change = log_ratio_changes(sources.gc, sources.gld, result.days)
        assert str(change.abs().idxmax().date()) == "2007-11-12", f"{SPEC}; {AFTER_THE_RUN}"
        assert f"{change.max():.6f}" == "0.007082", SPEC
        assert f"{change.min():.6f}" == "-0.006626", f"{SPEC}; {AFTER_THE_RUN}"

    def test_the_16_00_series_daily_change_still_reverses(self, sources, result) -> None:
        change = log_ratio_changes(sources.gc, sources.gld, result.days).to_numpy()
        reversal = np.corrcoef(change[:-1], change[1:])[0, 1]
        assert f"{reversal:.6f}" == "-0.437059", f"{SPEC}; {AFTER_THE_RUN}"

    def test_the_ohlc_save_s_moves_past_2_percent(self, sources, result, ohlc_gc) -> None:
        """Its largest rise is on 2008-09-18 and its largest fall the day after.

        Of its 20 moves past 0.02, 8 rise and 12 fall.
        """
        change = log_ratio_changes(ohlc_gc, sources.gld, result.days)
        assert len(change) == 751
        assert str(change.abs().idxmax().date()) == "2008-09-18", f"{SPEC}; {AFTER_THE_RUN}"
        assert f"{change.min():.6f}" == "-0.075146", f"{SPEC}; {AFTER_THE_RUN}"
        assert str(change.idxmin().date()) == "2008-09-19", f"{SPEC}; {AFTER_THE_RUN}"
        assert (int((change > STEP).sum()), int((change < -STEP).sum())) == (8, 12), (
            f"{SPEC}; {AFTER_THE_RUN}"
        )

    def test_the_three_curves_end_where_the_post_says(self, result, cumret) -> None:
        """S, bills accrued day by day, and the script's 2 percent, each 0 on 2007-08-03."""
        bills = np.cumprod(1 + bill_accrual(result.days).to_numpy()) - 1
        two_percent = (1 + RISK_FREE_RATE) ** np.arange(len(result.days)) - 1
        assert (cumret[0], bills[0], two_percent[0]) == (0.0, 0.0, 0.0)
        assert (f"{cumret[-1]:.6f}", f"{bills[-1]:.6f}", f"{two_percent[-1]:.6f}") == (
            "0.058033",
            "0.031057",
            "0.061413",
        ), f"{SPEC}; {BILLS_SPEC}; {AFTER_THE_RUN}"
        on = result.days.get_loc(pd.Timestamp("2008-12-31"))
        assert (f"{cumret[on]:.6f}", f"{bills[on]:.6f}") == ("0.049260", "0.028733"), (
            f"{SPEC}; {BILLS_SPEC}; {AFTER_THE_RUN}"
        )

    def test_s_peaks_on_2010_07_27_and_last_tops_2_percent_on_2010_05_21(
        self, result, cumret
    ) -> None:
        peak = int(np.argmax(cumret))
        assert (_on(result.days, peak), f"{cumret[peak]:.6f}") == ("2010-07-27", "0.058415"), (
            f"{SPEC}; {AFTER_THE_RUN}"
        )
        two_percent = (1 + RISK_FREE_RATE) ** np.arange(len(result.days)) - 1
        above = np.flatnonzero(cumret > two_percent)
        assert _on(result.days, int(above[-1])) == "2010-05-21", f"{SPEC}; {AFTER_THE_RUN}"


class TestThePostsHelpers:
    """The three helpers the post added, on synthetic legs whose answers are worked here."""

    DAYS = pd.DatetimeIndex(["2008-12-30", "2008-12-31", "2009-01-02", "2009-01-05"])

    def test_the_log_ratio_change_is_dated_on_the_later_day(self) -> None:
        gc = closes([10.0, 10.3, 10.3, 9.5], list(self.DAYS.strftime("%Y-%m-%d")))
        gld = closes([1.0, 1.0, 1.1, 1.0], list(self.DAYS.strftime("%Y-%m-%d")))
        change = log_ratio_changes(gc, gld, self.DAYS)
        assert change.index.equals(self.DAYS[1:])
        np.testing.assert_allclose(
            change.to_numpy(),
            [math.log(1.03), math.log(1 / 1.1), math.log((9.5 / 1.0) / (10.3 / 1.1))],
            rtol=0,
            atol=1e-15,
        )

    def test_it_reads_only_the_days_it_is_handed(self) -> None:
        """A day one leg holds and ``days`` leaves out moves nothing."""
        gc = closes([10.0, 99.0, 10.3], ["2020-01-02", "2020-01-03", "2020-01-06"])
        gld = closes([1.0, 1.0, 1.0], ["2020-01-02", "2020-01-03", "2020-01-06"])
        days = pd.DatetimeIndex(["2020-01-02", "2020-01-06"])
        assert log_ratio_changes(gc, gld, days).tolist() == [pytest.approx(math.log(1.03))]

    def test_ratio_steps_summarises_the_same_changes(self, monkeypatch) -> None:
        seen = []
        unpatched = module.log_ratio_changes

        def record(gc, gld, days):
            seen.append(len(days))
            return unpatched(gc, gld, days)

        monkeypatch.setattr(module, "log_ratio_changes", record)
        days = ["2020-01-02", "2020-01-03", "2020-01-06"]
        gc, gld = closes([10.0, 10.3, 9.5], days), closes([1.0] * 3, days)
        ratio_steps(gc, gld, pd.DatetimeIndex(days))
        assert seen == [3]

    def test_the_bills_earn_each_month_s_rate_over_252_from_the_second_row(self) -> None:
        rates = dict(bill_rates.monthly_rates())
        accrual = bill_accrual(self.DAYS)
        assert accrual.index.equals(self.DAYS)
        assert accrual.tolist() == [
            0.0,
            rates["2008-12"] / 252,
            rates["2009-01"] / 252,
            rates["2009-01"] / 252,
        ]

    def test_a_month_the_series_lacks_is_refused(self) -> None:
        with pytest.raises(ValueError, match="holds none for 2199-01"):
            bill_accrual(pd.DatetimeIndex(["2008-12-31", "2199-01-02"]))

    def test_by_year_leaves_out_the_first_row_and_reads_each_year_s_months(self) -> None:
        daily = np.array([0.0, 0.01, -0.002, 0.004])
        result = GldGc(days=self.DAYS, gc=np.ones(4), gld=np.ones(4), daily=daily)
        first, second = by_year(result)
        assert (first.year, first.rows, second.year, second.rows) == (2008, 1, 2009, 2)
        assert first.average_annual_return == pytest.approx(252 * 0.01, rel=1e-12)
        assert second.average_annual_return == pytest.approx(252 * 0.001, rel=1e-12)
        assert first.bill_rate == bill_rates.average("2008-12", "2008-12")
        assert second.bill_rate == bill_rates.average("2009-01", "2009-01")
        assert first.excess == first.average_annual_return - first.bill_rate

    def test_a_year_s_bill_rate_averages_every_month_its_days_span(self) -> None:
        days = pd.DatetimeIndex(["2008-01-02", "2008-01-03", "2008-03-31"])
        result = GldGc(days=days, gc=np.ones(3), gld=np.ones(3), daily=np.array([0.0, 0.1, 0.2]))
        (year,) = by_year(result)
        assert year.bill_rate == bill_rates.average("2008-01", "2008-03")
        assert year.rows == 2


class TestTheGuardAndTheReads:
    """Each leg and the OHLC save's GC are guarded over the window on their own calendars."""

    def test_no_series_carries_a_flagged_day_in_the_window(self, sources) -> None:
        assert scale_breaks(sources.gc) == []
        assert scale_breaks(sources.gld.loc[WINDOW_START:WINDOW_END]) == []
        ohlc_gc = load_panel(OHLC_SOURCE_FILE)[1]["GC"].dropna()
        assert scale_breaks(ohlc_gc.loc[WINDOW_START:WINDOW_END]) == []

    def test_every_read_is_guarded_over_the_window(self, monkeypatch) -> None:
        seen = []

        def record(legs, *, start, end):
            ((entry, _),) = legs
            seen.append((entry.path, start, end))

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", record)
        with redirect_stdout(io.StringIO()):
            run()
        assert seen == [
            ("inputdata_gc_1600_20100802/gc.csv", WINDOW_START, WINDOW_END),
            ("inputdata_etf/gld.csv", WINDOW_START, WINDOW_END),
            ("inputdataohlcdaily_20120507/gc.csv", WINDOW_START, WINDOW_END),
        ]

    @pytest.mark.parametrize(
        ("source_file", "symbol"), [(GC_SOURCE_FILE, "GC"), (GLD_SOURCE_FILE, "GLD")]
    )
    def test_a_leg_changing_scale_inside_the_window_is_refused(
        self, source_file, symbol, monkeypatch
    ) -> None:
        members, panel = load_panel(source_file)
        broken = panel.copy()
        broken.loc[pd.Timestamp("2009-01-02") :, symbol] *= 10

        def fake(name, **kwargs):
            return (members, broken) if name == source_file else load_panel(name, **kwargs)

        monkeypatch.setattr(module, "load_panel", fake)
        with pytest.raises(WindowCrossesScaleBreak, match=f"{symbol.lower()}.csv"):
            read_sources()

    def test_main_turns_a_guard_refusal_into_one_line(self, monkeypatch, no_arguments) -> None:
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("inputdata_gc_1600_20100802/gc.csv changes scale")

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(SystemExit, match="gc.csv changes scale"):
            main()

    def test_main_turns_a_missing_vintage_into_one_line(
        self, monkeypatch, tmp_path, no_arguments
    ) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit, match="inputData_GC_1600_20100802.mat"):
            main()

    def test_main_lets_any_other_error_through_as_itself(self, monkeypatch, no_arguments) -> None:
        def fail(*_a, **_k):
            raise ValueError("a bug, not a refusal")

        monkeypatch.setattr(module, "load_panel", fail)
        with pytest.raises(ValueError, match="a bug, not a refusal"):
            main()


@pytest.fixture(scope="module")
def printed() -> str:
    """What ``run`` prints, captured once for the tests that read it."""
    out = io.StringIO()
    with redirect_stdout(out):
        run()
    return out.getvalue()


class TestTheReport:
    def test_it_prints_each_figure_with_its_verdict(self, printed) -> None:
        for label, cells in (
            ("Average annual return", ["0.019014", "0.0190", "reproduced"]),
            ("Sharpe ratio", ["-0.066564", "-0.07", "reproduced"]),
            ("APR", ["0.019084", "0.0191", "reproduced"]),
            ("Maximum drawdown ", ["-0.008247", "-0.008247", "reproduced"]),
            ("Text return percent, average", ["1.901433", "1.9", "reproduced"]),
            ("Text return percent, APR", ["1.908382", "1.9", "reproduced"]),
            ("Text maximum drawdown percent", ["0.824652", "0.8", "reproduced"]),
            ("Maximum drawdown days", ["91", "91", "reproduced"]),
        ):
            row = next(r for r in printed.splitlines() if r.strip().startswith(label))
            assert all(cell in row.split() for cell in cells), row
        assert "did not reproduce" not in printed

    def test_it_names_every_vintage_and_the_label(self, printed) -> None:
        assert "inputdata_gc_1600_20100802/gc.csv" in printed
        assert "inputdata_etf/gld.csv" in printed
        assert "inputdataohlcdaily_20120507/gc.csv" in printed
        assert "2007-08-03 to 2010-08-02, 752 days both legs hold, of GC's 761" in printed
        assert "GLD_GC.m as shipped, long GLD and short GC every day" in printed
        assert "Exploratory." in printed
        assert "Entry 38" in printed

    def test_it_prints_b1_and_the_identity(self, printed) -> None:
        assert "37 months, 0.010141" in printed
        assert "+0.008874" in printed
        assert "GC rows GLD lacks, 9: 2007-11-22" in printed
        assert "GLD rows in the window GC lacks, 3:" in printed
        assert "on 0 of 752 shared days" in printed
        assert "correlation 0.824035" in printed
        assert "10.822 and 10.235" in printed
        assert "standard deviation 0.000933" in printed
        assert "standard deviation 0.009243" in printed
        assert "largest 0.007082, 0 moves past 0.02" in printed
        assert "largest 0.097332, 20 moves past 0.02" in printed
        assert "the nearest 9.30 apart" in printed
        assert "3: 2007-09-19, 2007-12-24, 2009-12-24" in printed
        assert "over 2007-08 to 2010-08, 37 months" in printed
        assert "lag-1 autocorrelation -0.559953" in printed
        assert "standard deviation 0.015660" in printed
        assert "at most 0.001775 of its daily variance" in printed

    def test_a_missed_duration_prints_its_own_value_and_gap(self, monkeypatch) -> None:
        """A run lasting 93 days shows 93 and its gap, not the book's 91."""
        unpatched = module.figures

        def longer(daily, risk_free=RISK_FREE_RATE):
            return dataclasses.replace(unpatched(daily, risk_free), max_drawdown_days=93)

        monkeypatch.setattr(module, "figures", longer)
        out = io.StringIO()
        with redirect_stdout(out):
            run()
        row = next(r for r in out.getvalue().splitlines() if "Maximum drawdown days" in r)
        assert row.split()[3:5] == ["93", "91"], row
        assert row.endswith("did not reproduce, gap +2"), row
