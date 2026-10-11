"""The pins for XLE against USO signed by crude oil's contango, *Algorithmic Trading* location 2734.

This file is the single authority for every number a prose surface quotes
about this replication. ``docs/replication-log.md`` Entry 38 carries the
verdicts and points here row by row.

Every pin reads two vintages and one specification, so they are stated once
here.

- **Vintages.** Two of Chan's book-two files, both chan-mat. Each one's
  identity is its row of ``LIFTED_SOURCES`` in
  ``tests/support/committed_vintages.py``.

  1. ``inputdata_etf/``, from ``inputData_ETF.mat``, basis ``adjusted``, saved
     2012-04-10. USO and XLE hold 1,500 rows each from 2006-04-26 to
     2012-04-09 with no missing close. The file subtracts each dividend in
     dollars from every earlier close, which ``data/README.md`` records.
  2. ``inputdatadaily_cl_20120502/``, from ``inputDataDaily_CL_20120502.mat``,
     basis ``raw``, saved 2012-05-03. 89 CL contracts from CL-2007F to
     CL-2014K over 2,867 days from 2000-11-20 to 2012-05-02, with no spot,
     read through ``chan.roll_returns.load_strip``.

- **The specification.** ``XLE_CL_rollReturn.m``, git blob ``e9b8981`` at
  EpchanPreview ``e4bc46f``. The ratio is the back contract over the front,
  with each contract the front from 40 to 10 rows before its last priced row
  and starting no earlier than the row after the previous front ended, NaN on
  every other row. On the days both calendars hold, a ratio above 1 is short
  USO and long XLE, below 1 long USO and short XLE, and anything else flat.
  Each day earns ``smartsum(backshift(1, positions) .* pctchange, 2) / 2`` with
  NaN set to 0. The figures are ``chan.tu_momentum.figures``: 252 times the
  mean, ``√252 · mean / std`` with the std dividing by n,
  ``prod(1 + r)^(252 / n) − 1`` and ``calculateMaxDD``, with no risk-free rate
  and no cost.

Each figure is held at full precision under a tight tolerance, against the
script's comment at the decimals it prints and against the book's two at the
precision Chan printed, through ``matches``.

Exploratory. Reproducing Chan's figures spends his 2006 to 2012 sample on a
rule he chose. The run first ran here on 2026-10-10.
"""

from __future__ import annotations

import io
import math
from contextlib import redirect_stdout

import numpy as np
import pandas as pd
import pytest

from chan import paths, roll_returns
from chan import xle_uso_roll_return as module
from chan.calendar_spread_reversion import calendar_schedule
from chan.khandani_lo_book_two import matches
from chan.series import WindowCrossesScaleBreak, load_panel, scale_breaks
from chan.vintage import VintageUnavailable
from chan.vx_calendar_spread import held_pair_ratio
from chan.xle_uso_roll_return import (
    BACKWARDATION,
    BOOK_APR_PERCENT,
    BOOK_SHARPE,
    CONTANGO,
    ETF_FILE,
    FRONT_END,
    FRONT_START,
    LEGS,
    SCRIPT_APR,
    SCRIPT_AVERAGE_ANNUAL_RETURN,
    SCRIPT_MAX_DRAWDOWN,
    SCRIPT_MAX_DRAWDOWN_DAYS,
    SCRIPT_SHARPE,
    STRIP_FILE,
    USO,
    WINDOW_END,
    WINDOW_START,
    XLE,
    Arbitrage,
    arbitrage,
    daily_returns,
    front_ratio,
    main,
    positions,
    read_sources,
    run,
)
from tests.support.committed_vintages import LIFTED_SOURCES

TIGHT = 1e-12

day = pd.Timestamp


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def closes(sources) -> pd.DataFrame:
    return sources[1]


@pytest.fixture(scope="module")
def contracts(sources) -> pd.DataFrame:
    return sources[2].contracts


@pytest.fixture(scope="module")
def ratio(contracts) -> pd.Series:
    return front_ratio(contracts)


@pytest.fixture(scope="module")
def result(closes, ratio) -> Arbitrage:
    return arbitrage(closes, ratio)


@pytest.fixture(scope="module")
def schedule(contracts) -> pd.DataFrame:
    """The calendar spread's schedule with one month between the pair and no minimum hold."""
    return calendar_schedule(contracts, spread_month=1, holddays=0)


@pytest.fixture(scope="module")
def printed() -> str:
    """What ``run`` prints, captured once for the tests that read it."""
    out = io.StringIO()
    with redirect_stdout(out):
        run()
    return out.getvalue()


@pytest.fixture
def no_arguments(monkeypatch):
    """``main`` parses ``sys.argv``, which under pytest holds pytest's own arguments."""
    monkeypatch.setattr("sys.argv", ["chan.xle_uso_roll_return"])


class TestTheVintages:
    def test_the_etf_legs_are_their_pinned_source(self, sources) -> None:
        etf, _, _ = sources
        vendor, basis, saved, folder, _ = LIFTED_SOURCES[ETF_FILE]
        assert (vendor, basis, saved, folder) == (
            "chan-mat",
            "adjusted",
            "2012-04-10",
            "inputdata_etf",
        )
        assert [m.symbol for m in etf] == list(LEGS) == [USO, XLE]
        assert {(m.vendor, m.price_basis, m.obtained) for m in etf} == {(vendor, basis, saved)}
        assert [m.path for m in etf] == ["inputdata_etf/uso.csv", "inputdata_etf/xle.csv"]

    def test_the_strip_is_its_pinned_source(self, sources) -> None:
        strip = sources[2]
        vendor, basis, saved, folder, count = LIFTED_SOURCES[STRIP_FILE]
        assert (vendor, basis, saved, folder, count) == (
            "chan-mat",
            "raw",
            "2012-05-03",
            "inputdatadaily_cl_20120502",
            89,
        )
        assert {(m.vendor, m.price_basis, m.obtained) for m in strip.members} == {
            (vendor, basis, saved)
        }
        assert {m.path.split("/")[0] for m in strip.members} == {folder}

    def test_both_legs_hold_1500_closes_with_none_missing(self, closes) -> None:
        assert list(closes.columns) == [USO, XLE]
        assert len(closes) == 1500
        assert (closes.index[0], closes.index[-1]) == (WINDOW_START, WINDOW_END)
        assert closes.notna().all().all()

    def test_the_strip_holds_89_contracts_and_no_spot(self, sources, contracts) -> None:
        assert sources[2].spot is None
        assert contracts.shape == (2867, 89)
        assert (contracts.columns[0], contracts.columns[-1]) == ("CL-2007F", "CL-2014K")
        assert (contracts.index[0], contracts.index[-1]) == (day("2000-11-20"), day("2012-05-02"))

    def test_the_strip_s_columns_are_in_delivery_order(self, contracts) -> None:
        assert list(contracts.columns) == sorted(contracts.columns)


class TestTheSpecification:
    """The script's rule on both vintages, over the 1,498 days both calendars hold."""

    def test_the_average_annual_return(self, result) -> None:
        f = result.figures
        assert f.average_annual_return == pytest.approx(0.15923063046565827, abs=TIGHT)
        assert matches(f.average_annual_return, SCRIPT_AVERAGE_ANNUAL_RETURN)
        assert SCRIPT_AVERAGE_ANNUAL_RETURN == "0.1592"

    def test_the_sharpe_ratio(self, result) -> None:
        f = result.figures
        assert f.sharpe == pytest.approx(1.0465964113818127, abs=TIGHT)
        assert matches(f.sharpe, SCRIPT_SHARPE)
        assert SCRIPT_SHARPE == "1.05"

    def test_the_apr(self, result) -> None:
        f = result.figures
        assert f.apr == pytest.approx(0.15910241442582507, abs=TIGHT)
        assert matches(f.apr, SCRIPT_APR)
        assert SCRIPT_APR == "0.1591"

    def test_the_maximum_drawdown(self, result) -> None:
        f = result.figures
        assert f.max_drawdown == pytest.approx(-0.19232087483339455, abs=TIGHT)
        assert matches(f.max_drawdown, SCRIPT_MAX_DRAWDOWN)
        assert SCRIPT_MAX_DRAWDOWN == "-0.192321"

    def test_the_longest_drawdown(self, result) -> None:
        assert result.figures.max_drawdown_days == 487
        assert matches(result.figures.max_drawdown_days, SCRIPT_MAX_DRAWDOWN_DAYS)
        assert SCRIPT_MAX_DRAWDOWN_DAYS == "487"

    def test_both_reproduce_the_book_s_figures(self, result) -> None:
        """Location 2734's "16 percent" and "about 1", checked at no decimals."""
        assert (BOOK_APR_PERCENT, BOOK_SHARPE) == ("16", "1")
        assert matches(100 * result.figures.apr, BOOK_APR_PERCENT)
        assert matches(result.figures.sharpe, BOOK_SHARPE)

    def test_the_two_calendars_share_1498_days(self, closes, ratio, result) -> None:
        assert len(result.days) == 1498
        assert (result.days[0], result.days[-1]) == (WINDOW_START, WINDOW_END)
        assert list(closes.index.difference(ratio.index)) == [
            day("2006-07-03"),
            day("2006-11-24"),
        ]

    def test_it_measures_every_shared_day(self, result) -> None:
        assert len(result.daily) == 1498
        assert np.isfinite(result.daily).all()

    def test_the_first_front_ratio_is_on_2006_10_20(self, ratio, result) -> None:
        assert ratio.first_valid_index() == day("2006-10-20")
        assert result.days[np.flatnonzero(np.isfinite(result.ratio))[0]] == day("2006-10-20")

    def test_the_window_s_first_123_days_carry_no_ratio_and_no_other_day_does(self, result) -> None:
        unset = np.flatnonzero(np.isnan(result.ratio))
        assert len(unset) == 123
        assert (unset == np.arange(123)).all()
        assert result.days[122] == day("2006-10-19")
        assert not result.positions[:123].any()

    def test_the_position_on_each_day(self, result) -> None:
        held = result.positions
        assert int((held == CONTANGO).all(axis=1).sum()) == 1129
        assert int((held == BACKWARDATION).all(axis=1).sum()) == 244
        assert result.flat == 125
        assert list(result.days[result.ratio == 1]) == [day("2008-02-07"), day("2008-08-07")]

    def test_cl_2007f_is_the_front_for_31_rows(self, ratio) -> None:
        first = ratio.loc[: day("2006-12-05")].dropna()
        assert (first.index[0], first.index[-1], len(first)) == (
            day("2006-10-20"),
            day("2006-12-05"),
            31,
        )


class TestTheQuirks:
    """The two quirks of the script's loop the module docstring names, on this strip."""

    def test_every_contract_marks_exactly_one_expiry(self, contracts) -> None:
        priced = contracts.notna().to_numpy()
        marks = priced & ~np.vstack([priced[1:], np.zeros((1, priced.shape[1]), bool)])
        assert (marks.sum(axis=0) == 1).all()

    def test_24_contracts_are_priced_on_the_file_s_last_day(self, contracts) -> None:
        last = contracts.iloc[-1].dropna()
        assert len(last) == 24
        assert last.index[0] == "CL-2012M"

    def test_the_last_10_rows_get_no_ratio_and_all_fall_after_the_window(self, ratio) -> None:
        assert ratio.last_valid_index() == day("2012-04-18")
        assert ratio.iloc[-10:].isna().all()
        assert ratio.index[-10] > WINDOW_END

    def test_the_front_on_the_window_s_last_day_starts_after_cl_2012k_ends(
        self, contracts, ratio
    ) -> None:
        """CL-2012M reads as expiring on 2012-05-02, and its own 40-row start does not bind."""
        days = contracts.index
        assert ratio.loc[WINDOW_END] == pytest.approx(
            contracts.loc[WINDOW_END, "CL-2012N"] / contracts.loc[WINDOW_END, "CL-2012M"]
        )
        k_expiry = days.get_loc(contracts["CL-2012K"].last_valid_index())
        k_end = k_expiry - FRONT_END
        assert days[k_end + 1] == WINDOW_END
        assert days[len(days) - 1 - FRONT_START] < WINDOW_END


class TestTheScheduleNotReused:
    """``calendar_schedule`` with ``holddays=0`` and ``held_pair_ratio``, on the same strip."""

    def test_it_gives_the_same_ratio_on_every_row_both_define(
        self, contracts, ratio, schedule
    ) -> None:
        held = (schedule.to_numpy() == -1).any(axis=1)
        theirs = held_pair_ratio(contracts, schedule).to_numpy()
        both = held & ratio.notna().to_numpy()
        assert int(both.sum()) == 1351
        assert (theirs[both] == ratio.to_numpy()[both]).all()
        assert not (held & ratio.isna().to_numpy()).any()

    def test_it_leaves_cl_2007f_s_31_front_rows_unheld(self, ratio, schedule) -> None:
        held = (schedule.to_numpy() == -1).any(axis=1)
        only_here = ratio.index[ratio.notna().to_numpy() & ~held]
        assert (only_here[0], only_here[-1], len(only_here)) == (
            day("2006-10-20"),
            day("2006-12-05"),
            31,
        )


class TestTheRules:
    """Each step on a frame built so its answer is known."""

    @staticmethod
    def _strip(*last_rows: int, rows: int = 120) -> pd.DataFrame:
        """Contracts priced from row 0 through each last row, contract k at (k + 1)!.

        So the first front's ratio is 2, the second's 3 and the third's 4,
        and a row's ratio names the contract that was the front on it.
        """
        frame = {}
        for k, last in enumerate(last_rows):
            column = np.full(rows, np.nan)
            column[: last + 1] = float(math.factorial(k + 1))
            frame[f"CL-20{10 + k}F"] = column
        return pd.DataFrame(frame, index=pd.date_range("2020-01-01", periods=rows))

    def test_the_first_contract_starts_40_rows_before_its_expiry(self) -> None:
        r = front_ratio(self._strip(50, 80, 100)).to_numpy()
        assert np.isnan(r[: 50 - FRONT_START]).all()
        assert (r[50 - FRONT_START : 50 - FRONT_END + 1] == 2).all()

    def test_a_later_contract_starts_the_row_after_the_previous_one_ends(self) -> None:
        # The second contract's own 40-row start, row 20, falls inside the
        # first contract's window, so it waits for row 41.
        r = front_ratio(self._strip(50, 60, 100)).to_numpy()
        assert (r[10:41] == 2).all()
        assert (r[41:51] == 3).all()
        assert np.isnan(r[51:]).all()

    def test_each_front_is_the_back_over_the_front(self) -> None:
        r = front_ratio(self._strip(50, 80, 100, 110)).to_numpy()
        assert (r[41:71] == 3).all()
        assert (r[71:91] == 4).all()
        assert np.isnan(r[91:]).all()

    def test_the_ratio_is_nan_off_every_front_window_and_never_filled(self) -> None:
        # The second contract expires at row 100, so its window opens at row
        # 60 and rows 41 to 59 belong to no front.
        r = front_ratio(self._strip(50, 100, 110)).to_numpy()
        assert (r[10:41] == 2).all()
        assert np.isnan(r[41:60]).all()
        assert (r[60:91] == 3).all()

    def test_the_last_contract_is_never_the_front(self) -> None:
        r = front_ratio(self._strip(50, 80)).to_numpy()
        assert np.isfinite(r).sum() == FRONT_START - FRONT_END + 1

    def test_a_window_whose_start_passes_its_end_assigns_nothing(self) -> None:
        # The third contract expires on the second's row, so its start, row
        # 71, passes its end, row 70.
        r = front_ratio(self._strip(50, 80, 80, 110)).to_numpy()
        assert (r[41:71] == 3).all()
        assert np.isnan(r[71:]).all()

    def test_a_contract_with_no_priced_row_is_refused(self) -> None:
        strip = self._strip(50, 80, 100)
        strip["CL-2011F"] = np.nan
        with pytest.raises(ValueError, match="CL-2011F marks 0 expiries"):
            front_ratio(strip)

    def test_a_contract_whose_prices_stop_and_restart_is_refused(self) -> None:
        strip = self._strip(50, 80, 100)
        strip.iloc[30, 1] = np.nan
        with pytest.raises(ValueError, match="CL-2011F marks 2 expiries"):
            front_ratio(strip)

    @pytest.mark.parametrize("last", [35, 39])
    def test_a_first_window_before_the_first_row_is_refused(self, last) -> None:
        """MATLAB refuses an index below 1, where a Python slice would count from the end."""
        with pytest.raises(
            ValueError, match=f"CL-2010F's front window would start before .* at row {last - 40}$"
        ):
            front_ratio(self._strip(last, 80, 100))

    def test_a_first_window_starting_on_the_first_row_is_read(self) -> None:
        r = front_ratio(self._strip(40, 80, 100)).to_numpy()
        assert r[0] == 2

    def test_the_last_contract_s_expiry_is_never_read(self) -> None:
        """The loop stops before the last column, so a last contract never priced is not refused."""
        strip = self._strip(50, 80, 100, 110)
        strip["CL-2013F"] = np.nan
        r = front_ratio(strip).to_numpy()
        assert (r[41:71] == 3).all()
        # The third contract is the front from row 71, and its back is never priced.
        assert np.isnan(r[71:]).all()

    def test_contango_is_short_uso_and_long_xle(self) -> None:
        assert (USO, XLE) == LEGS
        assert positions(np.array([1.1, 0.9])).tolist() == [[-1, 1], [1, -1]]

    def test_a_ratio_of_exactly_1_or_nan_holds_nothing(self) -> None:
        assert positions(np.array([1.0, np.nan])).tolist() == [[0, 0], [0, 0]]

    @staticmethod
    def _closes(uso, xle) -> pd.DataFrame:
        return pd.DataFrame(
            {USO: uso, XLE: xle}, index=pd.date_range("2020-01-01", periods=len(uso))
        )

    def test_each_day_earns_yesterday_s_position(self) -> None:
        closes = self._closes([100.0, 110.0, 99.0], [50.0, 50.0, 55.0])
        held = np.array([[-1.0, 1.0], [1.0, -1.0], [0.0, 0.0]])
        # Row 1: short USO on +10 percent. Row 2: long USO on −10 percent and
        # short XLE on +10 percent. Each sum is halved.
        assert np.allclose(daily_returns(closes, held), [0.0, -0.05, -0.1])

    def test_each_leg_carries_half_the_capital_even_when_one_has_no_move(self) -> None:
        closes = self._closes([100.0, np.nan, 99.0], [50.0, 55.0, 55.0])
        held = np.array([[1.0, -1.0], [1.0, -1.0], [0.0, 0.0]])
        assert np.allclose(daily_returns(closes, held), [0.0, -0.05, 0.0])

    def test_the_legs_are_read_by_name_not_by_column_order(self) -> None:
        closes = self._closes([100.0, 110.0], [50.0, 50.0])
        held = np.array([[-1.0, 1.0], [0.0, 0.0]])
        swapped = closes[[XLE, USO]]
        assert daily_returns(swapped, held).tolist() == daily_returns(closes, held).tolist()
        assert daily_returns(closes, held)[1] == pytest.approx(-0.05)

    def test_only_the_days_both_calendars_hold_are_traded(self) -> None:
        closes = self._closes([100.0, 110.0, 121.0, 133.1], [50.0, 50.0, 50.0, 50.0])
        ratio = pd.Series(
            [2.0, 2.0, 2.0],
            index=pd.DatetimeIndex(["2020-01-02", "2020-01-03", "2020-01-05"]),
        )
        traded = arbitrage(closes, ratio)
        assert list(traded.days) == [day("2020-01-02"), day("2020-01-03")]
        assert np.allclose(traded.daily, [0.0, -0.05])


class TestTheGuardAndTheReads:
    @pytest.mark.parametrize("symbol", [USO, XLE])
    def test_neither_etf_leg_carries_a_flagged_day(self, symbol) -> None:
        assert scale_breaks(load_panel(ETF_FILE)[1][symbol]) == []

    def test_run_guards_both_etf_legs_over_the_file_s_span(self, monkeypatch) -> None:
        seen = []

        def record(legs, *, start, end):
            seen.append(([entry.path for entry, _ in legs], start, end))

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", record)
        read_sources()
        assert seen == [
            (["inputdata_etf/uso.csv", "inputdata_etf/xle.csv"], WINDOW_START, WINDOW_END)
        ]

    def test_the_strip_is_read_through_load_strip_from_the_named_save(self, monkeypatch) -> None:
        seen = []
        real = module.load_strip

        def record(root, data_dir=None, *, source_file=None):
            seen.append((root, data_dir, source_file))
            return real(root, data_dir, source_file=source_file)

        monkeypatch.setattr(module, "load_strip", record)
        read_sources(paths.DATA_DIR)
        assert seen == [("CL", paths.DATA_DIR, "inputDataDaily_CL_20120502.mat")]

    @pytest.mark.parametrize(("symbol", "row"), [(USO, 1), (XLE, 750), (USO, 1499)])
    def test_a_scale_change_in_either_leg_is_refused(self, symbol, row, monkeypatch) -> None:
        members, closes = load_panel(ETF_FILE)
        broken = closes.copy()
        broken.loc[broken.index[row] :, symbol] *= 10
        monkeypatch.setattr(module, "load_panel", lambda *_a, **_k: (members, broken))
        with pytest.raises(WindowCrossesScaleBreak, match=f"{symbol.lower()}.csv"):
            read_sources()

    def test_a_scale_change_in_a_contract_is_refused(self, monkeypatch) -> None:
        members, closes = load_panel(STRIP_FILE)
        broken = closes.copy()
        own = broken["CL-2009F"].dropna().index
        broken.loc[own[len(own) // 2] :, "CL-2009F"] *= 10
        monkeypatch.setattr(roll_returns, "load_panel", lambda *_a, **_k: (members, broken))
        with pytest.raises(WindowCrossesScaleBreak, match="cl-2009f.csv changes scale"):
            read_sources()

    def test_run_reads_the_directory_it_is_given(self, tmp_path) -> None:
        with pytest.raises(VintageUnavailable, match="inputData_ETF.mat"):
            run(tmp_path)

    def test_run_returns_the_specification(self) -> None:
        with redirect_stdout(io.StringIO()):
            found = run()
        assert found.figures.apr == pytest.approx(0.15910241442582507, abs=TIGHT)


class TestTheReport:
    @staticmethod
    def _row(out: str, label: str) -> list[str]:
        return next(r for r in out.splitlines() if r.strip().startswith(label)).split()

    def test_it_prints_each_figure_beside_the_script_s_and_the_book_s(self, printed) -> None:
        assert self._row(printed, "Average annual return")[-3:] == [
            "0.159231",
            "0.1592",
            "reproduced",
        ]
        assert self._row(printed, "Sharpe ratio")[-5:] == [
            "1.046596",
            "1.05",
            "reproduced",
            "1",
            "reproduced",
        ]
        assert self._row(printed, "APR")[-5:] == [
            "0.159102",
            "0.1591",
            "reproduced",
            "16",
            "reproduced",
        ]
        assert self._row(printed, "Maximum drawdown")[-3:] == [
            "-0.192321",
            "-0.192321",
            "reproduced",
        ]
        assert self._row(printed, "Longest drawdown, days")[-3:] == ["487", "487", "reproduced"]

    def test_it_prints_the_vintages_the_window_and_the_counts(self, printed) -> None:
        assert printed.startswith(
            "XLE against USO signed by crude oil's contango, Algorithmic Trading location 2734"
        )
        assert "inputdata_etf/uso.csv" in printed
        assert "inputdata_etf/xle.csv" in printed
        assert "inputdatadaily_cl_20120502/" in printed
        assert "window    2006-04-26 to 2012-04-09, 1498 days both calendars hold" in printed
        assert (
            "contango on 1129 days, backwardation on 244, no ratio on 123, "
            "a ratio of exactly 1 on 2"
        ) in printed
        assert "first front ratio 2006-10-20" in printed
        assert "Exploratory." in printed

    def test_a_miss_is_reported_as_one(self) -> None:
        assert module._verdict(0.159231, SCRIPT_AVERAGE_ANNUAL_RETURN) == "reproduced"
        assert module._verdict(0.1594, SCRIPT_AVERAGE_ANNUAL_RETURN) == "gap +0.0002"
        assert module._verdict(1.6, BOOK_SHARPE) == "gap +1"

    def test_main_turns_a_guard_refusal_into_one_line(self, monkeypatch, no_arguments) -> None:
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("inputdata_etf/xle.csv changes scale")

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(SystemExit, match="xle.csv changes scale") as stopped:
            main()
        assert str(stopped.value) == "inputdata_etf/xle.csv changes scale"

    def test_main_turns_a_missing_vintage_into_one_line(
        self, monkeypatch, tmp_path, no_arguments
    ) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit, match="inputData_ETF.mat"):
            main()

    def test_main_lets_any_other_error_through(self, monkeypatch, no_arguments) -> None:
        def broken(*_a, **_k):
            raise ValueError("a programming error keeps its traceback")

        monkeypatch.setattr(module, "run", broken)
        with pytest.raises(ValueError, match="keeps its traceback"):
            main()

    def test_main_refuses_an_argument(self, monkeypatch) -> None:
        monkeypatch.setattr("sys.argv", ["chan.xle_uso_roll_return", "--bogus"])
        with pytest.raises(SystemExit) as refused:
            main()
        assert refused.value.code == 2
