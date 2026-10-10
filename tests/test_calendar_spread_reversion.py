"""The pins for mean reversion on CL's calendar spread, *Algorithmic Trading*'s Example 5.4.

This file is the single authority for every number a prose surface quotes
about this example and the rows beside it. ``docs/replication-log.md`` Entry 34
carries the verdicts and points here row by row. The rows are the ones
[issue 348](https://github.com/l3a0/quantitative-trading/issues/348) declared
before the build.

Every pin on the committed file reads one strip and one of three
specifications, so they are stated once here and carried in every figure's
failure message.

- **Vintage.** ``data/inputdatadaily_cl_20120813/``, vendor chan-mat, basis
  raw, saved 2012-08-14, lifted from ``inputDataDaily_CL_20120813.mat``. It is
  one vintage per contract, 89 of them from CL-2007F to CL-2014K, and one for
  ``CL-SPOT``, read through ``chan.roll_returns.load_strip``. The strip's
  identity is its row of ``LIFTED_SOURCES`` in
  ``tests/support/committed_vintages.py``, which ``TestTheVintage`` holds the
  members to.
- **S, the specification.** ``calendarSpdsMeanReversion.m`` at EpchanPreview
  ``e4bc46f``, git blob ``277d84d``, as :mod:`chan.calendar_spread_reversion`
  transcribes it. γ is ``chan.roll_returns.roll_returns`` on the contracts,
  forward-filled. The half-life and the ADF read every finite row of it, and
  the z-score's lookback is the half-life rounded half away from zero, 36.
  Contract c is held short against contract c + 12 long for 63 days, the first
  pair from 73 rows before its expiry, each pair let go 10 rows before its
  near contract's last priced row, and the spread is reversed where z is above
  0 and flat where z is NaN. The return is yesterday's positions times each
  leg's return, summed over the priced legs and halved, measured on the 1,164
  rows from 2008-01-02 to 2012-08-13 and annualised over 252 days with no
  risk-free rate and no cost.
- **R1.** S measured from 2008-01-03, 1,163 rows.
- **R2.** S with ``holddays=61``, the book's "61 trading days", from
  2008-01-02.

Each computed figure is held at six decimals, so a change cannot move it
inside the published rounding unnoticed, and each published figure at the
precision Chan printed, through ``matches``.

Exploratory. Reproducing Chan's figures spends the 2008 to 2012 sample on a
rule he chose, and R1 was found by a scan after S missed two of the comment's
figures. The example first ran here on 2026-10-10.
"""

from __future__ import annotations

import io
from contextlib import redirect_stdout

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
    held_log_spread,
    main,
    report,
    run,
    run_spread,
    spread_returns,
)
from chan.khandani_lo import plain_sharpe
from chan.khandani_lo_book_two import compounded_apr, gap, matches
from chan.price_spread import zscore
from chan.roll_returns import SOURCE_FILES, Strip, load_strip, roll_returns
from chan.series import WindowCrossesScaleBreak
from chan.stationarity_tests import jplv7_adf
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import LIFTED_SOURCES

VINTAGE = (
    "inputdatadaily_cl_20120813/ chan-mat raw saved 2012-08-14, one vintage per contract "
    "CL-2007F to CL-2014K and one for CL-SPOT"
)
S_SPEC = (
    f"{VINTAGE}; S: calendarSpdsMeanReversion.m, forward-filled gamma, lookback round(half-life), "
    "c against c + 12 held 63 days, from 2008-01-02 to 2012-08-13"
)
R1_SPEC = f"{VINTAGE}; R1: S from 2008-01-03"
R2_SPEC = f"{VINTAGE}; R2: S with holddays=61 from 2008-01-02"

# --- the committed strip -------------------------------------------------------


@pytest.fixture(scope="module")
def strip() -> Strip:
    return load_strip("CL")


@pytest.fixture(scope="module")
def gamma(strip) -> pd.Series:
    return roll_returns(strip.contracts)


@pytest.fixture(scope="module")
def runs(strip, gamma) -> dict[str, CalendarSpreadRun]:
    return {
        "S": run_spread(strip.contracts, gamma, start=START),
        "R1": run_spread(strip.contracts, gamma, start=COMMENT_START),
        "R2": run_spread(strip.contracts, gamma, start=START, holddays=BOOK_HOLDDAYS),
    }


class TestTheSpecification:
    def test_the_scripts_constants(self) -> None:
        """Lines 77 to 80 and 113, and the book's 61 days."""
        assert (SPREAD_MONTH, HOLDDAYS, NUM_DAYS_END, BOOK_HOLDDAYS) == (12, 63, 10, 61)
        assert (START, COMMENT_START) == (pd.Timestamp("2008-01-02"), pd.Timestamp("2008-01-03"))

    def test_the_printed_figures_are_ascii_strings_float_can_read(self) -> None:
        printed = (
            SCRIPT_HALFLIFE,
            SCRIPT_APR,
            SCRIPT_SHARPE,
            SCRIPT_MAX_DD,
            SCRIPT_MAX_DD_DAYS,
            BOOK_APR_PERCENT,
            BOOK_SHARPE,
            BOOK_HALFLIFE,
        )
        assert printed == (
            "36.394034",
            "0.083406",
            "1.288661",
            "-0.053222",
            "206",
            "8.3",
            "1.3",
            "36",
        )
        assert all(text.isascii() for text in printed)
        assert [float(text) for text in printed]

    def test_the_strip_holds_89_contracts_a_month_apart(self, strip) -> None:
        """So all 77 pairs of c and c + 12 are a year apart, the book's third rule."""
        columns = list(strip.contracts.columns)
        assert (len(columns), columns[0], columns[-1]) == (89, "CL-2007F", "CL-2014K"), VINTAGE
        assert len(columns) - SPREAD_MONTH == 77

    def test_cls_first_expiry_is_5044_rows_after_the_files_first_row(self, strip) -> None:
        """The module docstring quotes it, as why a Python slice cannot wrap on CL."""
        first = strip.contracts.iloc[:, 0]
        expiry = first.last_valid_index()
        assert (strip.contracts.index.get_loc(expiry), str(expiry.date())) == (
            5044,
            "2006-12-19",
        ), VINTAGE


class TestTheFigures:
    """Test 1 of the plan on issue 348: S, R1 and R2 at six decimals."""

    @pytest.mark.parametrize(
        ("key", "rows", "apr", "sharpe", "max_dd", "days", "spec"),
        [
            ("S", 1164, "0.082671", "1.278216", "-0.053222", 206, S_SPEC),
            ("R1", 1163, "0.083406", "1.288661", "-0.053222", 206, R1_SPEC),
            ("R2", 1164, "0.067315", "1.044327", "-0.098047", 208, R2_SPEC),
        ],
    )
    def test_each_runs_figures(self, runs, key, rows, apr, sharpe, max_dd, days, spec) -> None:
        found = runs[key]
        assert len(found.returns) == rows, spec
        assert f"{found.half_life:.6f}" == "36.394034", spec
        assert (f"{found.apr:.6f}", f"{found.sharpe:.6f}") == (apr, sharpe), spec
        assert (f"{found.max_dd:.6f}", found.max_dd_days) == (max_dd, days), spec

    def test_each_window_runs_to_the_files_last_day(self, runs) -> None:
        for key, first, spec in (
            ("S", "2008-01-02", S_SPEC),
            ("R1", "2008-01-03", R1_SPEC),
            ("R2", "2008-01-02", R2_SPEC),
        ):
            index = runs[key].returns.index
            assert (str(index[0].date()), str(index[-1].date())) == (first, "2012-08-13"), spec

    def test_ss_lookback_is_36(self, runs) -> None:
        assert runs["S"].lookback == 36, S_SPEC

    def test_the_last_held_day_of_s_and_of_r2(self, runs) -> None:
        """Contracts still trading on 2012-08-13 expire on the file's last row, so S's last
        pairs are skipped. R2's 61 days let a later pair through."""
        assert str(runs["S"].last_held.date()) == "2012-05-08", S_SPEC
        assert str(runs["R2"].last_held.date()) == "2012-07-06", R2_SPEC

    def test_the_first_row_holding_anything_is_2006_09_05(self, runs) -> None:
        positions = runs["S"].positions
        holding = positions.index[(positions != 0).any(axis=1).to_numpy()]
        assert str(holding[0].date()) == "2006-09-05", S_SPEC

    def test_ss_window_returns_exactly_zero_on_its_last_66_rows_and_no_other(self, runs) -> None:
        returns = runs["S"].returns.to_numpy()
        zero = np.flatnonzero(returns == 0)
        assert zero.tolist() == list(range(len(returns) - 66, len(returns))), S_SPEC

    def test_dropping_the_first_day_is_what_r1_does(self, runs) -> None:
        """S's 2008-01-02 return set to zero misses the comment, so the printed run left the
        row out rather than holding it flat."""
        returns = runs["S"].returns.to_numpy().copy()
        assert f"{returns[0]:.7f}" == "-0.0028127", S_SPEC
        returns[0] = 0.0
        assert (f"{compounded_apr(returns):.6f}", f"{plain_sharpe(returns):.6f}") == (
            "0.083331",
            "1.288104",
        ), S_SPEC

    def test_r1_matches_every_figure_the_scripts_comment_prints(self, runs) -> None:
        r1 = runs["R1"]
        assert matches(r1.half_life, SCRIPT_HALFLIFE), R1_SPEC
        assert matches(r1.apr, SCRIPT_APR), R1_SPEC
        assert matches(r1.sharpe, SCRIPT_SHARPE), R1_SPEC
        assert matches(r1.max_dd, SCRIPT_MAX_DD), R1_SPEC
        assert matches(r1.max_dd_days, SCRIPT_MAX_DD_DAYS), R1_SPEC

    def test_s_misses_the_comments_apr_and_sharpe_ratio(self, runs) -> None:
        s = runs["S"]
        assert not matches(s.apr, SCRIPT_APR) and not matches(s.sharpe, SCRIPT_SHARPE), S_SPEC
        assert (gap(s.apr, SCRIPT_APR), gap(s.sharpe, SCRIPT_SHARPE)) == (
            -0.000735,
            -0.010445,
        ), S_SPEC

    def test_s_reproduces_the_comments_half_life_and_drawdown(self, runs) -> None:
        s = runs["S"]
        assert matches(s.half_life, SCRIPT_HALFLIFE), S_SPEC
        assert matches(s.max_dd, SCRIPT_MAX_DD), S_SPEC
        assert matches(s.max_dd_days, SCRIPT_MAX_DD_DAYS), S_SPEC

    @pytest.mark.parametrize(("key", "spec"), [("S", S_SPEC), ("R1", R1_SPEC)])
    def test_s_and_r1_both_match_the_books_figures(self, runs, key, spec) -> None:
        found = runs[key]
        assert matches(100 * found.apr, BOOK_APR_PERCENT), spec
        assert matches(found.sharpe, BOOK_SHARPE), spec
        assert matches(found.half_life, BOOK_HALFLIFE), spec

    def test_s_measured_to_its_last_nonzero_return(self, runs) -> None:
        """The pair held on 2012-05-08 earns its last return on 2012-05-09, so the window
        cut there drops only the 66 rows that hold nothing."""
        returns = runs["S"].returns
        last = returns.index[(returns != 0).to_numpy()][-1]
        spec = f"{S_SPEC}, cut at S's last nonzero return"
        assert str(last.date()) == "2012-05-09", spec
        cut = returns.loc[:last].to_numpy()
        assert len(cut) == 1098, spec
        assert (f"{compounded_apr(cut):.6f}", f"{plain_sharpe(cut):.6f}") == (
            "0.087853",
            "1.316295",
        ), spec

    def test_s_compounds_to_0_443248_by_its_last_day(self, runs) -> None:
        """Figure 5.7's curve, ``cumprod(1 + ret) − 1``, at 2012-08-13."""
        returns = runs["S"].returns
        cumulative = np.cumprod(1 + returns.to_numpy()) - 1
        assert str(returns.index[-1].date()) == "2012-08-13", S_SPEC
        assert f"{cumulative[-1]:.6f}" == "0.443248", S_SPEC


class TestTheTest:
    """Test 2: the book's "stationary with 99 percent probability"."""

    def test_the_adf_statistic_clears_the_1_percent_critical_value(self, runs) -> None:
        adf = runs["S"].adf
        assert f"{adf.statistic:.6f}" == "-4.727778", S_SPEC
        assert adf.critical[0] == -3.4583, S_SPEC
        assert f"{adf.critical[0] - adf.statistic:.6f}" == "1.269478", S_SPEC

    def test_the_half_life_and_adf_read_the_whole_filled_gamma(self, runs, gamma) -> None:
        """Lines 51 to 60 read every finite row, not the window, so the three runs agree."""
        filled_series = gamma.ffill().dropna()
        assert (len(filled_series), str(filled_series.index[0].date())) == (
            1941,
            "2004-11-22",
        ), S_SPEC
        filled = filled_series.to_numpy()
        assert runs["S"].adf == jplv7_adf(filled, 0, 1) == runs["R1"].adf == runs["R2"].adf, S_SPEC
        assert runs["S"].half_life == ou_half_life(filled), S_SPEC

    def test_1164_of_gammas_1941_rows_lie_in_ss_window(self, runs, gamma) -> None:
        """So 60 percent of what the half-life, and so the lookback, read is the traded window."""
        filled = gamma.ffill().dropna()
        inside = filled.loc[runs["S"].returns.index[0] :]
        assert (len(inside), len(filled)) == (1164, 1941), S_SPEC
        assert inside.index.equals(runs["S"].returns.index), S_SPEC
        assert round(100 * len(inside) / len(filled)) == 60, S_SPEC


@pytest.fixture(scope="module")
def held_window(strip, gamma) -> pd.DataFrame:
    """S's held rows from 2008-01-02: the log spread, filled γ and its z-score on each.

    A held row is one where the unflipped schedule holds a pair and filled γ is
    finite, as it is on every such row of CL.
    """
    schedule = calendar_schedule(strip.contracts)
    filled = gamma.ffill()
    frame = pd.DataFrame(
        {
            "spread": held_log_spread(strip.contracts, schedule),
            "gamma": filled,
            "z": zscore(filled.to_numpy(), 36),
        }
    )
    held = frame["spread"].notna() & frame["gamma"].notna()
    return frame.loc[held.to_numpy() & (frame.index >= START)]


class TestTheTradesDirection:
    """The spread moves against γ, and line 107 sells it where z(γ) is above 0.

    So the script shorts the spread when the spread sits below its average,
    which bets that it moves further away, the opposite of the reversion
    location 2461 describes. The spread is :func:`held_log_spread` on the
    unflipped schedule, and z is ``zscore`` of filled γ over S's 36 rows.
    """

    def test_the_held_spread_moves_against_gamma_on_ss_window(self, held_window) -> None:
        spec = f"{S_SPEC}, held rows from 2008-01-02"
        assert len(held_window) == 1097, spec
        assert (str(held_window.index[0].date()), str(held_window.index[-1].date())) == (
            "2008-01-02",
            "2012-05-08",
        ), spec
        found = np.corrcoef(held_window["spread"], held_window["gamma"])[0, 1]
        assert f"{found:.6f}" == "-0.883910", spec

    def test_the_held_spread_moves_against_gamma_on_every_held_row(self, strip, gamma) -> None:
        spread = held_log_spread(strip.contracts, calendar_schedule(strip.contracts))
        filled = gamma.ffill()
        held = spread.notna() & filled.notna()
        spec = f"{S_SPEC}, every held row of the file"
        assert int(held.sum()) == 1429, spec
        found = np.corrcoef(spread[held], filled[held])[0, 1]
        assert f"{found:.6f}" == "-0.893686", spec

    def test_the_far_leg_is_short_wherever_z_is_above_0(self, runs, strip, held_window) -> None:
        """554 rows with z above 0 hold the far leg short and 543 below hold it long.

        No held row of the window has z at 0 or NaN, so the two sets are all 1,097.
        """
        schedule = calendar_schedule(strip.contracts).loc[held_window.index]
        flipped = runs["S"].positions.loc[held_window.index]
        far = (flipped.to_numpy() * (schedule.to_numpy() == 1)).sum(axis=1)
        z = held_window["z"].to_numpy()
        spec = f"{S_SPEC}, held rows from 2008-01-02"
        assert (int((z > 0).sum()), int((z < 0).sum())) == (554, 543), spec
        assert set(far[z > 0]) == {-1.0}, spec
        assert set(far[z < 0]) == {1.0}, spec

    def test_reversing_every_position_negates_ss_returns(self, runs, strip) -> None:
        """The return is linear in the positions, so the book's direction earns minus S's."""
        s = runs["S"]
        reversed_ = spread_returns(-s.positions, strip.contracts).loc[s.returns.index]
        np.testing.assert_allclose(reversed_, -s.returns, rtol=0, atol=1e-15, err_msg=S_SPEC)

    def test_the_reversed_rule_loses_what_s_earns(self, runs) -> None:
        daily = -runs["S"].returns.to_numpy()
        spec = f"{S_SPEC}, every position reversed"
        assert len(daily) == 1164, spec
        assert (f"{compounded_apr(daily):.6f}", f"{plain_sharpe(daily):.6f}") == (
            "-0.080125",
            "-1.278216",
        ), spec


class TestTheArgumentsOnCl:
    """Test 3 case 5: ``lookback`` and ``end`` on CL, which no CL row passes and issue 349's do.

    Without these a ``run_spread`` that ignored either argument would pass
    every pin above.
    """

    def test_a_passed_lookback_of_36_gives_s_exactly(self, strip, gamma, runs) -> None:
        found = run_spread(strip.contracts, gamma, start=START, lookback=36)
        s = runs["S"]
        assert found.lookback == 36, S_SPEC
        assert found.returns.equals(s.returns), S_SPEC
        assert (found.apr, found.sharpe, found.last_held) == (s.apr, s.sharpe, s.last_held), S_SPEC

    def test_a_passed_lookback_of_15_is_used(self, strip, gamma) -> None:
        found = run_spread(strip.contracts, gamma, start=START, lookback=15)
        spec = f"{S_SPEC}, with the lookback passed as 15"
        assert found.lookback == 15, spec
        assert (f"{found.apr:.6f}", f"{found.sharpe:.6f}") == ("0.074327", "1.156156"), spec

    def test_an_end_cuts_the_returns_and_bounds_the_last_held_day(self, strip, gamma, runs) -> None:
        end = pd.Timestamp("2010-12-31")
        found = run_spread(strip.contracts, gamma, start=START, end=end)
        spec = f"{S_SPEC}, cut at 2010-12-31"
        assert found.returns.equals(runs["S"].returns.loc[:end]), spec
        assert len(found.returns) == 757, spec
        assert str(found.last_held.date()) == "2010-12-31", spec

    def test_an_end_inside_the_flat_tail_keeps_the_schedules_last_held_day(
        self, strip, gamma
    ) -> None:
        """No pair is held after 2012-05-08, so an end of 2012-06-29 is not a held day."""
        found = run_spread(strip.contracts, gamma, start=START, end=pd.Timestamp("2012-06-29"))
        assert str(found.last_held.date()) == "2012-05-08", f"{S_SPEC}, cut at 2012-06-29"


# --- the rules on synthetic frames ---------------------------------------------

ROWS = 120
DAYS = pd.bdate_range("2020-01-01", periods=ROWS)


def _contracts(expiries: list[int], gaps: dict[int, slice] | None = None) -> pd.DataFrame:
    """A strip whose contract c is priced from row 0 to row ``expiries[c]``, both included.

    ``gaps`` blanks rows of a contract before its expiry. Prices drift up so
    every leg's return is defined and not zero.
    """
    prices = np.full((ROWS, len(expiries)), np.nan)
    for c, last in enumerate(expiries):
        prices[: last + 1, c] = 50.0 + c + 0.1 * np.arange(last + 1)
    for c, rows in (gaps or {}).items():
        prices[rows, c] = np.nan
    return pd.DataFrame(prices, index=DAYS, columns=[f"X{c}" for c in range(len(expiries))])


def _held(schedule: pd.DataFrame, column: int, sign: int) -> list[int]:
    return np.flatnonzero(schedule.iloc[:, column].to_numpy() == sign).tolist()


class TestTheSchedule:
    def test_the_first_pair_starts_holddays_plus_10_rows_before_its_expiry(self) -> None:
        schedule = calendar_schedule(_contracts([40, 70, 100]), spread_month=1, holddays=5)
        assert _held(schedule, 0, -1) == list(range(25, 31))
        assert _held(schedule, 1, 1) == list(range(25, 31))

    def test_a_later_pair_starts_the_row_after_the_last_ends(self) -> None:
        schedule = calendar_schedule(_contracts([40, 70, 100]), spread_month=1, holddays=5)
        assert _held(schedule, 1, -1) == list(range(31, 61))
        assert _held(schedule, 2, 1) == list(range(31, 61))

    def test_a_first_expiry_inside_holddays_plus_10_rows_starts_on_the_files_first_row(
        self,
    ) -> None:
        """Line 85's ``max(1, ...)``, worked by hand in the script's one-based rows.

        Contract 0 is priced on rows 1 to 16, so ``expireIdx`` is 16 and
        ``numDaysStart`` is 20. ``startIdx`` is ``max(1, -4)``, row 1, and
        ``endIdx`` is 6, so rows 1 to 6 are held, which are rows 0 to 5 here.
        """
        schedule = calendar_schedule(_contracts([15, 70, 100]), spread_month=1, holddays=10)
        assert _held(schedule, 0, -1) == list(range(0, 6))
        assert _held(schedule, 1, 1) == list(range(0, 6))

    def test_a_window_of_exactly_holddays_is_held(self) -> None:
        """Line 90's ``>=``: pair 1 runs from row 31 to row 36, and 36 minus 31 is 5."""
        schedule = calendar_schedule(_contracts([40, 46, 70, 100]), spread_month=1, holddays=5)
        assert _held(schedule, 1, -1) == list(range(31, 37))
        assert _held(schedule, 2, -1) == list(range(37, 61))

    def test_a_window_one_short_of_holddays_is_skipped(self) -> None:
        """Pair 1 would run from row 31 to row 35, and 35 minus 31 is 4, below 5."""
        schedule = calendar_schedule(_contracts([40, 45, 70, 100]), spread_month=1, holddays=5)
        assert _held(schedule, 1, -1) == []
        assert _held(schedule, 2, -1) == list(range(31, 61))

    def test_a_short_window_is_skipped_and_keeps_the_previous_end(self) -> None:
        """Pair 1 would run rows 31 to 33, fewer than 5, so pair 2 starts on row 31."""
        schedule = calendar_schedule(_contracts([40, 43, 70, 100]), spread_month=1, holddays=5)
        assert _held(schedule, 1, -1) == []
        assert _held(schedule, 2, -1) == list(range(31, 61))

    def test_a_contract_priced_on_the_last_row_expires_there(self) -> None:
        schedule = calendar_schedule(
            _contracts([40, ROWS - 1, ROWS - 1]), spread_month=1, holddays=5
        )
        assert _held(schedule, 1, -1) == list(range(31, ROWS - 1 - NUM_DAYS_END + 1))

    def test_the_schedule_is_on_the_contracts_index_and_columns(self) -> None:
        contracts = _contracts([40, 70, 100])
        schedule = calendar_schedule(contracts, spread_month=1, holddays=5)
        assert schedule.index.equals(contracts.index)
        assert schedule.columns.equals(contracts.columns)

    def test_holddays_0_never_holds_the_first_pairs_one_row_window(self) -> None:
        """Line 98's comparison is strict, so a window whose start is its end holds nothing."""
        schedule = calendar_schedule(_contracts([40, 70]), spread_month=1, holddays=0)
        assert not schedule.to_numpy().any()

    def test_holddays_0_holds_the_next_pair_from_the_row_after(self) -> None:
        schedule = calendar_schedule(_contracts([40, 70, 100]), spread_month=1, holddays=0)
        assert _held(schedule, 0, -1) == []
        assert _held(schedule, 1, -1) == list(range(31, 61))

    def test_a_near_contract_with_a_gap_expires_on_its_last_priced_row(self) -> None:
        """Line 75 marks row 30 and row 50, and line 83 takes the last."""
        contracts = _contracts([50, 80, 110], gaps={0: slice(31, 36)})
        schedule = calendar_schedule(contracts, spread_month=1, holddays=5)
        assert _held(schedule, 0, -1) == list(range(35, 41))


class TestTheHeldSpread:
    def test_it_is_log_far_minus_log_near(self) -> None:
        contracts = pd.DataFrame({"near": [100.0], "far": [80.0]}, index=DAYS[:1])
        schedule = pd.DataFrame({"near": [-1.0], "far": [1.0]}, index=DAYS[:1])
        found = held_log_spread(contracts, schedule)
        assert found.index.equals(DAYS[:1])
        assert found.tolist() == [pytest.approx(np.log(80.0) - np.log(100.0))]
        assert found.iloc[0] < 0

    def test_it_reads_the_sign_of_the_schedule_and_not_the_column_order(self) -> None:
        contracts = pd.DataFrame({"a": [100.0, 100.0], "b": [80.0, 80.0]}, index=DAYS[:2])
        schedule = pd.DataFrame({"a": [-1.0, 1.0], "b": [1.0, -1.0]}, index=DAYS[:2])
        found = held_log_spread(contracts, schedule)
        assert found.tolist() == [
            pytest.approx(np.log(0.8)),
            pytest.approx(-np.log(0.8)),
        ]

    def test_a_row_without_exactly_one_pair_or_with_an_unpriced_leg_is_nan(self) -> None:
        """Row 0 holds nothing, row 1 two near contracts, and row 2 an unpriced far leg."""
        contracts = pd.DataFrame(
            {"x": [100.0, 100.0, 100.0], "y": [90.0, 90.0, 90.0], "z": [80.0, 80.0, np.nan]},
            index=DAYS[:3],
        )
        schedule = pd.DataFrame(
            {"x": [0.0, -1.0, -1.0], "y": [0.0, -1.0, 0.0], "z": [0.0, 1.0, 1.0]},
            index=DAYS[:3],
        )
        assert held_log_spread(contracts, schedule).isna().tolist() == [True, True, True]


class TestTheFlip:
    def test_nan_is_flat_positive_reverses_and_zero_and_negative_keep_the_sign(self) -> None:
        schedule = pd.DataFrame({"near": [-1.0] * 4, "far": [1.0] * 4}, index=DAYS[:4])
        z = pd.Series([np.nan, 1.0, 0.0, -1.0], index=DAYS[:4])
        flipped = flip_on_zscore(schedule, z)
        assert flipped["near"].tolist() == [0.0, 1.0, -1.0, -1.0]
        assert flipped["far"].tolist() == [0.0, -1.0, 1.0, 1.0]

    def test_z_exactly_0_keeps_the_schedules_sign(self) -> None:
        """Line 107's comparison is strict."""
        schedule = pd.DataFrame({"near": [-1.0], "far": [1.0]}, index=DAYS[:1])
        flipped = flip_on_zscore(schedule, pd.Series([0.0], index=DAYS[:1]))
        assert flipped.to_numpy().tolist() == [[-1.0, 1.0]]

    def test_the_schedule_is_not_changed(self) -> None:
        schedule = pd.DataFrame({"near": [-1.0, -1.0]}, index=DAYS[:2])
        flip_on_zscore(schedule, pd.Series([1.0, np.nan], index=DAYS[:2]))
        assert schedule["near"].tolist() == [-1.0, -1.0]


class TestTheReturn:
    def test_it_halves_yesterdays_positions_times_each_legs_return(self) -> None:
        contracts = pd.DataFrame({"near": [100.0, 110.0], "far": [50.0, 45.0]}, index=DAYS[:2])
        positions = pd.DataFrame({"near": [-1.0, 0.0], "far": [1.0, 0.0]}, index=DAYS[:2])
        returns = spread_returns(positions, contracts)
        assert returns.index.equals(DAYS[:2])
        assert returns.tolist() == [0.0, pytest.approx((-0.1 - 0.1) / 2)]

    def test_a_leg_with_no_return_is_skipped(self) -> None:
        contracts = pd.DataFrame({"near": [100.0, np.nan], "far": [50.0, 55.0]}, index=DAYS[:2])
        positions = pd.DataFrame({"near": [-1.0, 0.0], "far": [1.0, 0.0]}, index=DAYS[:2])
        assert spread_returns(positions, contracts).tolist() == [0.0, pytest.approx(0.05)]

    def test_a_leg_whose_return_is_infinite_is_skipped(self) -> None:
        """A price of 0 the day before makes the near leg's return infinite, and
        ``smartsum`` sums only the finite legs, so the far leg's 0.1 is halved alone."""
        contracts = pd.DataFrame({"near": [0.0, 1.0], "far": [50.0, 55.0]}, index=DAYS[:2])
        positions = pd.DataFrame({"near": [-1.0, 0.0], "far": [1.0, 0.0]}, index=DAYS[:2])
        assert spread_returns(positions, contracts).tolist() == [0.0, pytest.approx(0.05)]

    def test_a_row_with_no_leg_is_zero(self) -> None:
        contracts = pd.DataFrame({"near": [100.0, np.nan], "far": [np.nan, 55.0]}, index=DAYS[:2])
        positions = pd.DataFrame({"near": [-1.0, 0.0], "far": [1.0, 0.0]}, index=DAYS[:2])
        assert spread_returns(positions, contracts).tolist() == [0.0, 0.0]


def _ar1(seed: int, rows: int = ROWS, phi: float = 0.9) -> np.ndarray:
    rng = np.random.default_rng(seed)
    shocks = rng.standard_normal(rows)
    x = np.zeros(rows)
    for t in range(1, rows):
        x[t] = phi * x[t - 1] + shocks[t]
    return x


def _wiggling_contracts(seed: int) -> pd.DataFrame:
    """Three contracts a pair apart, with prices that move both ways so a Sharpe ratio exists."""
    rng = np.random.default_rng(seed)
    contracts = _contracts([40, 70, 110])
    return contracts * np.exp(0.01 * rng.standard_normal(contracts.shape).cumsum(axis=0))


class TestTheRun:
    def test_the_half_life_and_adf_read_the_forward_filled_signal(self) -> None:
        """Line 42 runs before line 51. γ on CL has no NaN after its first finite row, so
        only a synthetic signal holds the order."""
        values = _ar1(1)
        values[:3] = np.nan
        values[40:45] = np.nan
        values[80:90] = np.nan
        signal = pd.Series(values, index=DAYS)
        found = run_spread(
            _wiggling_contracts(1), signal, start=DAYS[0], spread_month=1, holddays=5
        )
        filled = signal.ffill().dropna().to_numpy()
        dropped = signal.dropna().to_numpy()
        assert found.half_life == ou_half_life(filled)
        assert found.adf == jplv7_adf(filled, 0, 1)
        assert ou_half_life(dropped) != pytest.approx(found.half_life, rel=1e-3)

    def test_the_z_score_reads_the_forward_filled_signal(self) -> None:
        """Line 42 fills γ before lines 67 to 69 read it, so a gap in the signal
        inside a held pair does not leave the pair flat."""
        values = _ar1(2)
        values[30:36] = np.nan
        signal = pd.Series(values, index=DAYS)
        contracts = _wiggling_contracts(2)
        found = run_spread(
            contracts, signal, start=DAYS[0], spread_month=1, holddays=5, lookback=10
        )
        z = pd.Series(zscore(signal.ffill().to_numpy(), 10), index=DAYS)
        expected = flip_on_zscore(calendar_schedule(contracts, spread_month=1, holddays=5), z)
        assert found.positions.equals(expected)

    def test_a_half_life_of_exactly_a_half_rounds_away_from_zero(self, monkeypatch) -> None:
        """MATLAB's ``round`` takes 36.5 to 37, where Python's ``round`` gives 36."""
        monkeypatch.setattr(module, "ou_half_life", lambda _x: 36.5)
        signal = pd.Series(_ar1(0), index=DAYS)
        found = run_spread(
            _wiggling_contracts(0), signal, start=DAYS[0], spread_month=1, holddays=5
        )
        assert (found.half_life, found.lookback) == (36.5, 37)

    def test_a_half_life_with_a_fraction_above_a_half_rounds_up(self) -> None:
        signal = pd.Series(_ar1(0, phi=0.9), index=DAYS)
        half_life = ou_half_life(signal.to_numpy())
        assert half_life % 1 > 0.5, "the seed no longer gives a half-life that rounds up"
        found = run_spread(
            _wiggling_contracts(0), signal, start=DAYS[0], spread_month=1, holddays=5
        )
        assert found.lookback == int(np.ceil(half_life))

    def test_a_lookback_passed_in_is_used(self) -> None:
        signal = pd.Series(_ar1(0), index=DAYS)
        found = run_spread(
            _wiggling_contracts(0), signal, start=DAYS[0], spread_month=1, holddays=5, lookback=15
        )
        assert found.lookback == 15

    def test_the_window_runs_from_start_to_end_both_included(self) -> None:
        signal = pd.Series(_ar1(0), index=DAYS)
        found = run_spread(
            _wiggling_contracts(0), signal, start=DAYS[10], end=DAYS[50], spread_month=1, holddays=5
        )
        assert found.returns.index.equals(DAYS[10:51])
        assert found.last_held == DAYS[50]

    # Every return in this window is 0, so the Sharpe ratio divides 0 by 0.
    @pytest.mark.filterwarnings("ignore:invalid value encountered:RuntimeWarning")
    def test_last_held_reads_the_unflipped_schedule(self) -> None:
        """A signal that starts late leaves z NaN, so the positions are flat where the
        schedule holds a pair, and the last held day is still the schedule's."""
        values = _ar1(0)
        values[:36] = np.nan
        signal = pd.Series(values, index=DAYS)
        found = run_spread(
            _wiggling_contracts(0), signal, start=DAYS[0], end=DAYS[33], spread_month=1, holddays=5
        )
        assert not found.positions.loc[: DAYS[33]].to_numpy().any()
        assert found.last_held == DAYS[33]


class TestTheRefusal:
    """Test 4: a signal on another index is refused, and an equal copy runs."""

    def test_a_signal_on_a_shifted_index_is_refused(self) -> None:
        signal = pd.Series(_ar1(0), index=DAYS.shift(1, freq="B"))
        with pytest.raises(ValueError, match="the contracts' own index"):
            run_spread(_wiggling_contracts(0), signal, start=DAYS[0], spread_month=1, holddays=5)

    def test_a_signal_on_an_equal_index_built_separately_runs(self) -> None:
        contracts = _wiggling_contracts(0)
        signal = pd.Series(_ar1(0), index=contracts.index.copy())
        found = run_spread(contracts, signal, start=DAYS[0], spread_month=1, holddays=5)
        assert len(found.returns) == ROWS


# --- the vintage, main and the report ----------------------------------------------


class TestTheVintage:
    """Test 6: the strip ``run`` reads, and that it reads it from the directory it is given."""

    def test_run_reads_the_cl_strip_the_script_loads(self) -> None:
        assert (module.ROOT, SOURCE_FILES[module.ROOT]) == ("CL", "inputDataDaily_CL_20120813.mat")

    def test_the_strip_is_its_pinned_source(self, strip) -> None:
        vendor, basis, saved, folder, count = LIFTED_SOURCES["inputDataDaily_CL_20120813.mat"]
        assert {(m.vendor, m.price_basis, m.obtained) for m in strip.members} == {
            (vendor, basis, saved)
        }, VINTAGE
        assert len(strip.members) == count == 90, VINTAGE
        assert {m.path.split("/")[0] for m in strip.members} == {folder}, VINTAGE
        columns = strip.contracts.columns
        assert (columns[0], columns[-1]) == ("CL-2007F", "CL-2014K"), VINTAGE

    def test_run_passes_its_directory_to_load_strip(self, strip, monkeypatch, tmp_path) -> None:
        """``TestMain`` patches ``load_strip``, so it would pass a ``run`` that dropped it."""
        asked = []

        def fake_load_strip(root, data_dir=None):
            asked.append((root, data_dir))
            return strip

        monkeypatch.setattr(module, "load_strip", fake_load_strip)
        with redirect_stdout(io.StringIO()):
            run(tmp_path)
        assert asked == [("CL", tmp_path)]

    def test_main_turns_a_missing_vintage_into_one_line(
        self, monkeypatch, tmp_path, no_arguments
    ) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit, match="inputDataDaily_CL_20120813.mat") as stopped:
            main()
        assert "\n" not in str(stopped.value)

    def test_main_refuses_an_argument(self, monkeypatch) -> None:
        monkeypatch.setattr("sys.argv", ["chan.calendar_spread_reversion", "--bogus"])
        with pytest.raises(SystemExit) as refused:
            main()
        assert refused.value.code == 2


@pytest.fixture
def no_arguments(monkeypatch) -> None:
    monkeypatch.setattr("sys.argv", ["calendar_spread_reversion"])


class TestMain:
    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage is lifted from inputDataDaily_CL_20120813"),
            WindowCrossesScaleBreak("inputdatadaily_cl_20120813/cl-spot.csv changes scale"),
        ],
    )
    def test_main_prints_a_refusal_as_one_line(self, monkeypatch, no_arguments, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(module, "load_strip", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)

    def test_main_lets_any_other_error_through_as_itself(self, monkeypatch, no_arguments) -> None:
        def fail(*_a, **_k):
            raise ValueError("a bug, not a refusal")

        monkeypatch.setattr(module, "load_strip", fail)
        with pytest.raises(ValueError, match="a bug, not a refusal"):
            main()

    def test_run_calls_run_spread_with_each_rows_start_and_holding_period(
        self, strip, monkeypatch
    ) -> None:
        """S from the script's start, R1 from the comment's, and R2 on the book's 61 days."""
        calls = []

        def record(contracts, signal, **kwargs):
            calls.append((contracts is strip.contracts, kwargs))
            return len(calls)

        monkeypatch.setattr(module, "load_strip", lambda *_a, **_k: strip)
        monkeypatch.setattr(module, "run_spread", record)
        monkeypatch.setattr(module, "report", lambda *_a: None)
        _, runs_ = run()
        assert calls == [
            (True, {"start": START}),
            (True, {"start": COMMENT_START}),
            (True, {"start": START, "holddays": BOOK_HOLDDAYS}),
        ]
        assert runs_ == {"S": 1, "R1": 2, "R2": 3}

    def test_run_reads_cl_and_returns_the_strip_and_three_runs(
        self, strip, monkeypatch, capsys
    ) -> None:
        asked = []

        def fake_load_strip(root, data_dir=None):
            asked.append((root, data_dir))
            return strip

        monkeypatch.setattr(module, "load_strip", fake_load_strip)
        found, runs_ = run()
        assert asked == [("CL", None)]
        assert found is strip
        assert list(runs_) == ["S", "R1", "R2"]
        assert "Exploratory." in capsys.readouterr().out


@pytest.fixture(scope="module")
def printed(strip, runs) -> str:
    out = io.StringIO()
    with redirect_stdout(out):
        report(strip, runs)
    return out.getvalue()


def _row(printed: str, label: str) -> str:
    return next(r for r in printed.splitlines() if r.strip().startswith(label))


class TestTheReport:
    @pytest.mark.parametrize(
        ("label", "figures", "verdict"),
        [
            ("Half-life, script", ["36.394034", "36.394034"], "reproduced"),
            ("Half-life, book", ["36.394034", "36"], "reproduced"),
            ("APR, script", ["0.082671", "0.083406"], "did not reproduce, gap -0.000735"),
            ("APR percent, book", ["8.267103", "8.3"], "reproduced"),
            ("Sharpe ratio, script", ["1.278216", "1.288661"], "did not reproduce, gap -0.010445"),
            ("Sharpe ratio, book", ["1.278216", "1.3"], "reproduced"),
            ("Maximum drawdown, script", ["-0.053222", "-0.053222"], "reproduced"),
            ("Longest drawdown, script", ["206", "206"], "reproduced"),
        ],
    )
    def test_each_of_ss_eight_rows_carries_a_verdict(
        self, printed, label, figures, verdict
    ) -> None:
        row = _row(printed, label)
        assert all(figure in row.split() for figure in figures), f"{S_SPEC}: {row}"
        assert row.rstrip().endswith(verdict), f"{S_SPEC}: {row}"

    def test_a_miss_prints_its_gap_with_its_sign(self) -> None:
        assert module._verdict(1.1, "1.0") == "did not reproduce, gap +0.1"
        assert module._verdict(0.9, "1.0") == "did not reproduce, gap -0.1"

    def test_the_longest_drawdown_row_reports_a_miss(self, strip, runs, monkeypatch) -> None:
        """The row is printed apart from the others, so its verdict is held on its own."""
        monkeypatch.setattr(module, "SCRIPT_MAX_DD_DAYS", "999")
        out = io.StringIO()
        with redirect_stdout(out):
            report(strip, runs)
        row = _row(out.getvalue(), "Longest drawdown, script")
        assert row.rstrip().endswith("did not reproduce, gap -793"), f"{S_SPEC}: {row}"

    def test_the_adf_row_carries_its_verdict_and_criterion(self, printed) -> None:
        row = _row(printed, "ADF statistic, book")
        assert "-4.727778" in row.split() and "99 percent" in row, f"{S_SPEC}: {row}"
        assert "reproduced, criterion below the 1 percent critical value -3.4583" in row, (
            f"{S_SPEC}: {row}"
        )

    def test_the_rows_beside_carry_no_verdict(self, printed) -> None:
        beside = printed.split("Beside the replication.")[1]
        r1 = _row(beside, "R1, from 2008-01-03")
        assert "1163 days, APR 0.083406, Sharpe 1.288661" in r1, f"{R1_SPEC}: {r1}"
        r2 = _row(beside, "R2, holddays=61 from 2008-01-02")
        assert "APR 0.067315, Sharpe 1.044327" in r2, f"{R2_SPEC}: {r2}"
        assert "last held 2012-07-06" in r2, f"{R2_SPEC}: {r2}"
        last = _row(beside, "S, last day a pair is held")
        assert last.split()[-1] == "2012-05-08", f"{S_SPEC}: {last}"
        assert "reproduce" not in beside

    def test_it_prints_the_vintage_the_window_and_the_label(self, printed) -> None:
        assert "inputdatadaily_cl_20120813/" in _row(printed, "vintage"), VINTAGE
        assert _row(printed, "window").split()[1:] == [
            "2008-01-02",
            "to",
            "2012-08-13,",
            "1164",
            "days",
        ], S_SPEC
        assert "Exploratory. docs/replication-log.md carries the verdicts." in printed
