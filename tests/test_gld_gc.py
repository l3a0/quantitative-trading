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

Exploratory. The window is the book's own. It first ran here on 2026-10-10.
"""

from __future__ import annotations

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
    common_days,
    daily_returns,
    figures,
    financing,
    gld_gc,
    identity,
    main,
    ratio_steps,
    read_sources,
    run,
)
from chan.khandani_lo_book_two import gap, matches
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
        assert "752 days both legs hold, of GC's 761" in printed
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
        assert "lag-1 autocorrelation -0.559953" in printed
        assert "standard deviation 0.015660" in printed
        assert "at most 0.001775 of its daily variance" in printed
