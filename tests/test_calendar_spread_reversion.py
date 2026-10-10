"""The pins for mean reversion on a 12-month CL spread, *Algorithmic Trading*'s Example 5.4.

This file is the single authority for every number a prose surface quotes
about this example and the rows beside it. ``docs/replication-log.md`` Entry 34
carries the verdicts and points here row by row. The rows are the ones
[issue 348](https://github.com/l3a0/quantitative-trading/issues/348) declared
before the build.

Every pin on the committed strip reads one vintage and one specification, so
both are stated once here and carried in every figure's failure message as
:data:`SPEC`, with the row's own change where it has one.

- **Vintage.** ``inputdatadaily_cl_20120813/``, chan-mat, raw, saved
  2012-08-14, lifted from ``inputDataDaily_CL_20120813.mat``. It holds 89
  contracts, CL-2007F to CL-2014K, one vintage each, and one for ``CL-SPOT``,
  over 6,467 days from 1986-11-03 to 2012-08-13, read through
  ``chan.roll_returns.load_strip``. Its identity is its row of
  ``LIFTED_SOURCES`` in ``tests/support/committed_vintages.py``, which
  ``TestTheVintage`` holds the members to.
- **Specification.** ``calendarSpdsMeanReversion.m`` at EpchanPreview
  ``e4bc46f``, git blob ``277d84d``, as :mod:`chan.calendar_spread_reversion`
  transcribes it. γ is ``chan.roll_returns.roll_returns`` forward-filled. The
  ADF test and the half-life read the filled γ's finite rows, and the z-score's
  lookback is the half-life rounded. Pair c is short contract c and long c + 12,
  the first held from 73 rows before its expiry, each later one from the day
  after the last held pair's end, and each to 10 rows before its own expiry,
  skipping a pair with fewer than 63 rows. The spread is reversed where the
  z-score is above 0 and flat where it is NaN. The return is the summed leg
  returns over 2, measured from 2008-01-02 to 2012-08-13, annualised over 252
  days with no risk-free rate and no cost.

S is the specification. R1 starts one row later, at 2008-01-03, and R2 holds
61 rows rather than 63. Each computed figure is held at six decimals, so a
change cannot move it inside the published rounding unnoticed, and each
published figure at the precision Chan printed, through ``matches``.

Exploratory. Reproducing Chan's figures spends the 2008 to 2012 sample on a
rule he chose, and R1 was found by a scan after S missed two of the comment's
figures. The example first ran on 2026-10-10.
"""

from __future__ import annotations

import io
import math
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from ithildincore.timeseries import ou_half_life

from chan import calendar_spread_reversion as module
from chan import paths
from chan.calendar_spread_reversion import (
    BOOK_APR_PERCENT,
    BOOK_HALFLIFE,
    BOOK_HOLDDAYS,
    BOOK_SHARPE,
    COMMENT_START,
    HOLDDAYS,
    NUM_DAYS_END,
    SCRIPT_APR,
    SCRIPT_HALFLIFE,
    SCRIPT_MAX_DD,
    SCRIPT_MAX_DD_DAYS,
    SCRIPT_SHARPE,
    SPREAD_MONTH,
    START,
    CalendarSpreadRun,
    calendar_schedule,
    flip_on_zscore,
    main,
    run,
    run_spread,
    spread_returns,
)
from chan.khandani_lo import plain_sharpe
from chan.khandani_lo_book_two import compounded_apr, gap, matches
from chan.roll_returns import contract_month, roll_returns
from chan.series import WindowCrossesScaleBreak
from chan.stationarity_tests import jplv7_adf
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import LIFTED_SOURCES

SOURCE_FILE = "inputDataDaily_CL_20120813.mat"

SPEC = (
    "inputdatadaily_cl_20120813/ chan-mat raw strip saved 2012-08-14, "
    "calendarSpdsMeanReversion.m at e4bc46f: gamma filled, lookback the rounded half-life, "
    "pairs c and c + 12 held 63 rows to 10 before expiry, reversed above z 0, "
    "return over 2 from 2008-01-02"
)

#: Each run's figures at six decimals: APR, Sharpe ratio, maximum drawdown,
#: its duration, and the window's rows.
FIGURES = {
    "S": ("0.082671", "1.278216", "-0.053222", 206, 1164),
    "R1": ("0.083406", "1.288661", "-0.053222", 206, 1163),
    "R2": ("0.067315", "1.044327", "-0.098047", 208, 1164),
}


@pytest.fixture(scope="module")
def ran():
    """What ``run`` reads, returns and prints, captured once for every test that needs it."""
    out = io.StringIO()
    with redirect_stdout(out):
        strip, runs = run()
    return strip, runs, out.getvalue()


@pytest.fixture(scope="module")
def strip(ran):
    return ran[0]


@pytest.fixture(scope="module")
def runs(ran) -> dict[str, CalendarSpreadRun]:
    return ran[1]


@pytest.fixture(scope="module")
def printed(ran) -> str:
    return ran[2]


@pytest.fixture(scope="module")
def gamma(strip) -> pd.Series:
    return roll_returns(strip.contracts)


@pytest.fixture
def no_arguments(monkeypatch):
    """``main`` parses ``sys.argv``, which under pytest holds pytest's own arguments."""
    monkeypatch.setattr("sys.argv", ["chan.calendar_spread_reversion"])


def _six(value: float) -> str:
    return f"{value:.6f}"


class TestTheSpecification:
    def test_the_scripts_constants(self) -> None:
        assert (SPREAD_MONTH, HOLDDAYS, NUM_DAYS_END, BOOK_HOLDDAYS) == (12, 63, 10, 61)
        assert (START, COMMENT_START) == (pd.Timestamp("2008-01-02"), pd.Timestamp("2008-01-03"))

    def test_the_scripts_printed_figures(self) -> None:
        assert (SCRIPT_HALFLIFE, SCRIPT_APR, SCRIPT_SHARPE, SCRIPT_MAX_DD, SCRIPT_MAX_DD_DAYS) == (
            "36.394034",
            "0.083406",
            "1.288661",
            "-0.053222",
            "206",
        )

    def test_the_books_printed_figures(self) -> None:
        assert (BOOK_APR_PERCENT, BOOK_SHARPE, BOOK_HALFLIFE) == ("8.3", "1.3", "36")


class TestTheVintage:
    def test_the_strip_run_reads_is_its_pinned_source(self, strip) -> None:
        vendor, basis, saved, folder, count = LIFTED_SOURCES[SOURCE_FILE]
        assert {(m.vendor, m.price_basis, m.obtained) for m in strip.members} == {
            (vendor, basis, saved)
        }
        assert (vendor, basis, saved) == ("chan-mat", "raw", "2012-08-14")
        assert len(strip.members) == count == 90
        assert {m.path.split("/")[0] for m in strip.members} == {folder}

    def test_its_contracts_run_from_cl_2007f_to_cl_2014k(self, strip) -> None:
        columns = list(strip.contracts.columns)
        assert (len(columns), columns[0], columns[-1]) == (89, "CL-2007F", "CL-2014K")
        assert strip.spot.name == "CL-SPOT"
        months = [contract_month(symbol) for symbol in columns]
        assert set(np.diff(months)) == {1}, "each contract is a month after the last"
        days = strip.contracts.index
        assert (len(days), str(days[0].date()), str(days[-1].date())) == (
            6467,
            "1986-11-03",
            "2012-08-13",
        )

    def test_run_passes_its_data_directory_to_load_strip(self, monkeypatch) -> None:
        seen = []

        class Stop(Exception):
            pass

        def record(root, data_dir=None):
            seen.append((root, data_dir))
            raise Stop

        monkeypatch.setattr(module, "load_strip", record)
        with pytest.raises(Stop):
            run(data_dir=Path("elsewhere"))
        assert seen == [("CL", Path("elsewhere"))]

    def test_main_on_an_empty_data_directory_exits_naming_the_file(
        self, monkeypatch, tmp_path, no_arguments
    ) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit, match=SOURCE_FILE) as stopped:
            main()
        assert "\n" not in str(stopped.value)

    def test_main_refuses_an_argument(self, monkeypatch) -> None:
        monkeypatch.setattr("sys.argv", ["chan.calendar_spread_reversion", "--bogus"])
        with pytest.raises(SystemExit) as refused:
            main()
        assert refused.value.code == 2


class TestTheFigures:
    @pytest.mark.parametrize("row", ["S", "R1", "R2"])
    def test_each_run_at_six_decimals(self, runs, row) -> None:
        found = runs[row]
        apr, sharpe, max_dd, days, rows = FIGURES[row]
        assert (
            _six(found.apr),
            _six(found.sharpe),
            _six(found.max_dd),
            found.max_dd_days,
            len(found.returns),
        ) == (apr, sharpe, max_dd, days, rows), f"{row}: {SPEC}"
        assert _six(found.half_life) == "36.394034"
        assert found.lookback == 36

    def test_each_window_starts_where_its_row_says_and_ends_on_the_strips_last_day(
        self, runs
    ) -> None:
        for row, first in (("S", START), ("R1", COMMENT_START), ("R2", START)):
            assert runs[row].returns.index[0] == first
            assert str(runs[row].returns.index[-1].date()) == "2012-08-13"

    def test_the_last_held_days(self, runs) -> None:
        assert str(runs["S"].last_held.date()) == "2012-05-08"
        assert str(runs["R1"].last_held.date()) == "2012-05-08"
        assert str(runs["R2"].last_held.date()) == "2012-07-06"

    def test_the_first_row_holding_anything_is_2006_09_05(self, runs) -> None:
        positions = runs["S"].positions
        held = positions.index[(positions.to_numpy() != 0).any(axis=1)]
        assert str(held[0].date()) == "2006-09-05"
        assert str(held[-1].date()) == "2012-05-08"

    def test_the_windows_last_66_rows_and_no_other_return_exactly_zero(self, runs) -> None:
        flat = runs["S"].returns.to_numpy() == 0
        assert int(flat.sum()) == 66
        assert flat[-66:].all()

    def test_the_first_days_return_and_what_zeroing_it_gives(self, runs) -> None:
        daily = runs["S"].returns.to_numpy()
        assert f"{daily[0]:.7f}" == "-0.0028127"
        zeroed = daily.copy()
        zeroed[0] = 0
        assert (_six(compounded_apr(zeroed)), _six(plain_sharpe(zeroed))) == (
            "0.083331",
            "1.288104",
        )

    def test_r1_matches_every_figure_the_comment_prints(self, runs) -> None:
        r1 = runs["R1"]
        for value, printed in (
            (r1.half_life, SCRIPT_HALFLIFE),
            (r1.apr, SCRIPT_APR),
            (r1.sharpe, SCRIPT_SHARPE),
            (r1.max_dd, SCRIPT_MAX_DD),
            (r1.max_dd_days, SCRIPT_MAX_DD_DAYS),
        ):
            assert matches(value, printed), (value, printed)

    def test_s_reproduces_six_of_the_eight_and_misses_the_comments_apr_and_sharpe(
        self, runs
    ) -> None:
        s = runs["S"]
        assert matches(s.half_life, SCRIPT_HALFLIFE)
        assert matches(s.max_dd, SCRIPT_MAX_DD)
        assert matches(s.max_dd_days, SCRIPT_MAX_DD_DAYS)
        assert not matches(s.apr, SCRIPT_APR)
        assert not matches(s.sharpe, SCRIPT_SHARPE)
        assert (gap(s.apr, SCRIPT_APR), gap(s.sharpe, SCRIPT_SHARPE)) == (-0.000735, -0.010445)

    @pytest.mark.parametrize("row", ["S", "R1"])
    def test_s_and_r1_round_to_the_books_figures(self, runs, row) -> None:
        found = runs[row]
        assert matches(100 * found.apr, BOOK_APR_PERCENT)
        assert matches(found.sharpe, BOOK_SHARPE)
        assert matches(found.half_life, BOOK_HALFLIFE)


class TestTheAdfTest:
    def test_the_statistic_clears_the_1_percent_critical_value(self, runs) -> None:
        adf = runs["S"].adf
        assert _six(adf.statistic) == "-4.727778"
        assert f"{adf.critical[0]:.4f}" == "-3.4583"
        assert _six(adf.critical[0] - adf.statistic) == "1.269478"

    def test_it_reads_the_filled_gammas_finite_rows(self, runs, gamma) -> None:
        finite = gamma.ffill().dropna().to_numpy()
        assert len(finite) == 1941
        assert str(gamma.first_valid_index().date()) == "2004-11-22"
        assert runs["S"].adf == jplv7_adf(finite, 0, 1)
        assert runs["S"].half_life == ou_half_life(finite)


# --- the rule on synthetic frames ------------------------------------------------


def _contracts(last_rows: list[int], rows: int = 120) -> pd.DataFrame:
    """Rising prices on contracts each priced from the first row to its own last row."""
    days = pd.bdate_range("2020-01-01", periods=rows)
    found = {}
    for i, last in enumerate(last_rows):
        prices = 50.0 + i + 0.01 * np.arange(rows) + 0.002 * np.arange(rows) ** 1.5 * (i + 1)
        prices[last + 1 :] = np.nan
        found[f"X-{i}"] = prices
    return pd.DataFrame(found, index=days)


def _held(schedule: pd.DataFrame, column: int, sign: int) -> list[int]:
    return list(np.flatnonzero(schedule.iloc[:, column].to_numpy() == sign))


def _reverting(seed: int, rows: int = 400) -> np.ndarray:
    """An AR(1) path with coefficient 0.88 from 0, seeded."""
    rng = np.random.default_rng(seed)
    path = np.zeros(rows)
    for t in range(1, rows):
        path[t] = 0.88 * path[t - 1] + rng.standard_normal()
    return path


class TestTheSchedule:
    def test_the_first_pair_starts_holddays_plus_10_rows_before_its_expiry(self) -> None:
        schedule = calendar_schedule(_contracts([40, 60]), spread_month=1, holddays=5)
        assert _held(schedule, 0, -1) == list(range(25, 31))
        assert _held(schedule, 1, 1) == list(range(25, 31))
        assert np.count_nonzero(schedule.to_numpy()) == 12

    def test_a_short_window_is_skipped_and_keeps_the_previous_end(self) -> None:
        schedule = calendar_schedule(_contracts([40, 44, 70, 90]), spread_month=1, holddays=5)
        assert _held(schedule, 0, -1) == list(range(25, 31))
        assert _held(schedule, 1, -1) == []
        assert _held(schedule, 2, -1) == list(range(31, 61))
        assert _held(schedule, 3, 1) == list(range(31, 61))

    def test_a_contract_priced_on_the_last_row_expires_there(self) -> None:
        schedule = calendar_schedule(_contracts([49, 49], rows=50), spread_month=1, holddays=5)
        assert _held(schedule, 0, -1) == list(range(34, 40))

    def test_the_schedule_sits_on_the_contracts_index_and_columns(self) -> None:
        contracts = _contracts([40, 60])
        schedule = calendar_schedule(contracts, spread_month=1, holddays=5)
        assert schedule.index.equals(contracts.index)
        assert list(schedule.columns) == list(contracts.columns)

    def test_case_1_a_one_row_first_window_is_not_held(self) -> None:
        """Line 98's comparison is strict, and no CL pin reaches a window of one row."""
        schedule = calendar_schedule(_contracts([30, 50]), spread_month=1, holddays=0)
        assert np.count_nonzero(schedule.to_numpy()) == 0

    def test_case_2_a_gap_in_the_near_contract_is_not_its_expiry(self) -> None:
        """Line 83 takes the last mark, so the row before a gap does not end the contract."""
        contracts = _contracts([40, 60])
        contracts.iloc[21:25, 0] = np.nan
        schedule = calendar_schedule(contracts, spread_month=1, holddays=5)
        assert _held(schedule, 0, -1) == list(range(25, 31))


class TestTheFlip:
    def test_nan_is_flat_positive_reverses_and_negative_keeps(self) -> None:
        days = pd.bdate_range("2020-01-01", periods=4)
        schedule = pd.DataFrame({"a": [-1.0] * 4, "b": [1.0] * 4}, index=days)
        z = pd.Series([np.nan, -1.0, 0.5, 2.0], index=days)
        flipped = flip_on_zscore(schedule, z)
        assert flipped.to_numpy().tolist() == [[0, 0], [-1, 1], [1, -1], [1, -1]]

    def test_case_3_a_z_score_of_exactly_zero_keeps_the_schedules_sign(self) -> None:
        """Line 107's comparison is strict, and no CL row has a z-score of exactly 0."""
        days = pd.bdate_range("2020-01-01", periods=1)
        schedule = pd.DataFrame({"a": [-1.0], "b": [1.0]}, index=days)
        flipped = flip_on_zscore(schedule, pd.Series([0.0], index=days))
        assert flipped.to_numpy().tolist() == [[-1, 1]]


class TestTheReturn:
    def test_it_halves_skips_a_nan_leg_and_zeroes_a_row_with_none(self) -> None:
        days = pd.bdate_range("2020-01-01", periods=4)
        positions = pd.DataFrame({"a": [-1.0] * 4, "b": [1.0] * 4}, index=days)
        prices = pd.DataFrame(
            {"a": [100.0, 110.0, 121.0, np.nan], "b": [50.0, 60.0, np.nan, np.nan]}, index=days
        )
        found = spread_returns(positions, prices)
        assert found.index.equals(days)
        assert np.allclose(found.to_numpy(), [0.0, 0.05, -0.05, 0.0], rtol=0, atol=1e-15)

    def test_it_earns_yesterdays_position(self) -> None:
        days = pd.bdate_range("2020-01-01", periods=3)
        positions = pd.DataFrame({"a": [0.0, -1.0, 0.0], "b": [0.0, 1.0, 0.0]}, index=days)
        prices = pd.DataFrame({"a": [100.0, 110.0, 99.0], "b": [50.0, 60.0, 66.0]}, index=days)
        found = spread_returns(positions, prices).to_numpy()
        assert np.allclose(found, [0.0, 0.0, (0.1 + 0.1) / 2], rtol=0, atol=1e-15)


class TestRunSpread:
    def test_a_signal_with_gaps_is_filled_before_the_half_life_and_the_adf(self) -> None:
        """γ on CL has no NaN after its first finite row, so no CL pin can hold the fill."""
        contracts = _contracts([200, 399], rows=400)
        values = _reverting(0)
        values[:10] = np.nan
        values[[50, 51, 120]] = np.nan
        signal = pd.Series(values, index=contracts.index)
        found = run_spread(contracts, signal, start=contracts.index[0], spread_month=1)
        filled = signal.ffill().dropna().to_numpy()
        assert found.half_life == ou_half_life(filled)
        assert found.adf == jplv7_adf(filled, 0, 1)
        assert found.half_life != ou_half_life(signal.dropna().to_numpy())

    def test_case_4_the_lookback_rounds_a_half_life_up(self) -> None:
        """A half-life of 36.39 rounds down either way, so no CL pin tells round from truncate."""
        contracts = _contracts([200, 399], rows=400)
        signal = pd.Series(_reverting(5), index=contracts.index)
        found = run_spread(contracts, signal, start=contracts.index[0], spread_month=1)
        assert found.half_life % 1 >= 0.5
        assert f"{found.half_life:.6f}" == "6.563390"
        assert found.lookback == math.ceil(found.half_life) == 7

    def test_a_signal_on_a_shifted_index_is_refused(self) -> None:
        contracts = _contracts([200, 399], rows=400)
        signal = pd.Series(_reverting(0), index=contracts.index + pd.Timedelta(days=1))
        with pytest.raises(ValueError, match="contracts' own index"):
            run_spread(contracts, signal, start=contracts.index[0], spread_month=1)

    def test_a_signal_on_an_equal_index_built_separately_runs(self) -> None:
        contracts = _contracts([200, 399], rows=400)
        signal = pd.Series(_reverting(0), index=contracts.index.copy())
        found = run_spread(contracts, signal, start=contracts.index[0], spread_month=1)
        assert len(found.returns) == 400


class TestTheArgumentsNoClRowPasses:
    """Case 5. S, R1 and R2 pass neither ``lookback`` nor ``end``, and issue 349 passes both."""

    def test_a_passed_lookback_of_36_gives_s_and_15_does_not(self, strip, gamma, runs) -> None:
        s = runs["S"]
        same = run_spread(strip.contracts, gamma, start=START, lookback=36)
        assert (same.apr, same.sharpe) == (s.apr, s.sharpe)
        shorter = run_spread(strip.contracts, gamma, start=START, lookback=15)
        assert shorter.lookback == 15
        assert (_six(shorter.apr), _six(shorter.sharpe)) == ("0.074327", "1.156156")

    def test_an_end_cuts_the_returns(self, strip, gamma, runs) -> None:
        cut = run_spread(strip.contracts, gamma, start=START, end=pd.Timestamp("2010-12-31"))
        assert len(cut.returns) == 757
        pd.testing.assert_series_equal(cut.returns, runs["S"].returns.loc[:"2010-12-31"])
        assert str(cut.last_held.date()) == "2010-12-31"

    def test_an_end_inside_the_flat_tail_leaves_the_last_held_day(self, strip, gamma) -> None:
        cut = run_spread(strip.contracts, gamma, start=START, end=pd.Timestamp("2012-06-29"))
        assert str(cut.returns.index[-1].date()) == "2012-06-29"
        assert str(cut.last_held.date()) == "2012-05-08"


class TestMain:
    def test_main_lets_any_other_error_through_as_itself(self, monkeypatch, no_arguments) -> None:
        def fail(*_a, **_k):
            raise ValueError("a bug, not a refusal")

        monkeypatch.setattr(module, "load_strip", fail)
        with pytest.raises(ValueError, match="a bug, not a refusal"):
            main()

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage is lifted from inputDataDaily_CL_20120813"),
            WindowCrossesScaleBreak("inputdatadaily_cl_20120813/cl-2008f.csv changes scale"),
        ],
    )
    def test_main_prints_a_refusal_as_one_line(self, monkeypatch, no_arguments, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(module, "load_strip", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)


class TestTheReport:
    def _row(self, printed: str, label: str) -> str:
        return next(r for r in printed.splitlines() if r.strip().startswith(label))

    def test_each_of_s_eight_figures_carries_a_verdict(self, printed) -> None:
        for label, figures in (
            ("Half-life, days ", ["36.394034", "36.394034", "reproduced"]),
            ("Half-life, days, book", ["36.394034", "36", "reproduced"]),
            ("APR ", ["0.082671", "0.083406", "did", "reproduce,", "-0.000735"]),
            ("APR percent, book", ["8.267103", "8.3", "reproduced"]),
            ("Sharpe ratio ", ["1.278216", "1.288661", "did", "reproduce,", "-0.010445"]),
            ("Sharpe ratio, book", ["1.278216", "1.3", "reproduced"]),
            ("Maximum drawdown", ["-0.053222", "-0.053222", "reproduced"]),
            ("Longest drawdown, days", ["206", "206", "reproduced"]),
        ):
            row = self._row(printed, label)
            assert all(f in row.split() for f in figures), row

    def test_the_adf_row_carries_a_verdict_and_its_criterion(self, printed) -> None:
        row = self._row(printed, "ADF statistic")
        assert all(f in row.split() for f in ["-4.727778", "-3.4583", "reproduced,"]), row
        assert "below the 1 percent critical value" in row

    def test_the_rows_beside_carry_no_verdict(self, printed) -> None:
        r1 = self._row(printed, "R1,")
        r2 = self._row(printed, "R2,")
        assert r1.split()[-5:] == ["1163", "0.083406", "1.288661", "-0.053222", "206"]
        assert r2.split()[-5:] == ["1164", "0.067315", "1.044327", "-0.098047", "208"]
        assert self._row(printed, "last held day, S").split()[-1] == "2012-05-08"
        assert self._row(printed, "last held day, R2").split()[-1] == "2012-07-06"
        beside = printed.split("Beside the replication.")[1]
        assert "reproduce" not in beside

    def test_it_prints_the_vintage_the_window_and_the_label(self, printed) -> None:
        assert "inputdatadaily_cl_20120813/   chan-mat raw, saved 2012-08-14, 90 members" in printed
        assert "2008-01-02 to 2012-08-13, 1164 days" in printed
        assert "Exploratory. docs/replication-log.md carries the verdicts." in printed
