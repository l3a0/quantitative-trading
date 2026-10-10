"""The pins for TU momentum traded on the lagged roll return, *Algorithmic Trading*'s location 2690.

This file is the single authority for every number a prose surface quotes
about this experiment and the rows beside it. ``docs/replication-log.md``
Entry 35 carries the verdicts and points here row by row. The rows are the ones
[issue 353](https://github.com/l3a0/quantitative-trading/issues/353) declared
under "The pins".

Every pin on the committed files reads one vintage and one specification
unless it names the second vintage, so both are stated once here and carried
in each figure's failure message as :data:`SPEC`.

- **Vintage.** ``inputdatadaily_tu_20120813/``, chan-mat, raw, saved
  2012-08-14, 93 contracts and ``TU-SPOT`` over 5,565 days from 1990-06-22 to
  2012-08-13, read through ``chan.roll_returns.load_strip``. Its identity is
  its row of ``LIFTED_SOURCES`` in ``tests/support/committed_vintages.py``.
- **The second vintage.** ``inputdataohlcdaily_20120511/tu.csv``, chan-mat,
  adjusted, saved 2012-05-12, 2,000 days from 2004-06-01 to 2012-05-11, read
  through ``chan.tu_momentum.read_sources``. ``TestTheRebuildAgainstTheSave``
  and the save's rows in ``TestTheRowsBeside`` read it.
- **Specification.** The declared rule in :mod:`chan.roll_momentum`'s
  docstring. γ is ``roll_returns`` in column units. Long where γ > 0.03 and
  short where γ < −0.03, both strict. The return is ``backshift(1, pos)``
  times the rebuilt front-contract return, which rolls 7 rows before the held
  contract's last priced row. Every series runs on the full 5,565-row index
  and is cut to 2009-01-02 to 2012-08-13, 913 rows, last. The figures are
  ``chan.tu_momentum.figures``, annualised over 252 days with no risk-free
  rate and no cost. Example 6.1's rule, for rows 4 to 6, is
  ``chan.tu_momentum``'s ``signals`` on the rebuilt level, then
  ``positions``, then ``strategy_returns`` on the rebuilt return.

Each computed figure is held at six decimals, so a change cannot move it inside
the book's rounding unnoticed, and each of rows 1 to 3 at the precision the
book printed, through ``matches`` and ``gap``. The book's figures are module
constants, and there are no ``SCRIPT_*`` constants because no script ships.

Exploratory. The rule was declared after about 90 scratch readings, as the
module docstring discloses. It first ran here on 2026-10-10.
"""

from __future__ import annotations

import io
from contextlib import redirect_stdout

import numpy as np
import pandas as pd
import pytest

from chan import paths, roll_returns, tu_momentum
from chan import roll_momentum as module
from chan.khandani_lo_book_two import gap, matches
from chan.roll_momentum import (
    BOOK_APR_PERCENT,
    BOOK_MAX_DRAWDOWN_PERCENT,
    BOOK_SHARPE,
    EXAMPLE_6_1_BOOK_APR_PERCENT,
    EXAMPLE_6_1_BOOK_MAX_DRAWDOWN_PERCENT,
    EXAMPLE_6_1_BOOK_SHARPE,
    ROLL_ROWS,
    SAVE_ROUNDING,
    SOURCE_FILE,
    THRESHOLD,
    WINDOW_END,
    WINDOW_START,
    RollMomentum,
    SaveCheck,
    adjusted_level,
    check_against_save,
    fifth_contract_returns,
    held_contracts,
    held_returns,
    main,
    margins,
    roll_momentum,
    roll_position,
    roll_signals,
    rule_returns,
    run,
)
from chan.roll_returns import Strip, load_strip
from chan.series import WindowCrossesScaleBreak
from chan.tu_momentum import positions, read_sources, signals, strategy_returns
from tests.support.committed_vintages import LIFTED_SOURCES

SPEC = (
    "inputdatadaily_tu_20120813/ chan-mat raw saved 2012-08-14, gamma in column units, long "
    "above 0.03 and short below -0.03, backshift(1, pos) times the front contract rolled 7 "
    "rows before its last price, computed on 5,565 rows and cut to 2009-01-02..2012-08-13"
)


@pytest.fixture(scope="module")
def strip() -> Strip:
    return load_strip("TU")


@pytest.fixture(scope="module")
def result(strip) -> RollMomentum:
    return roll_momentum(strip)


@pytest.fixture(scope="module")
def save():
    return read_sources()


@pytest.fixture(scope="module")
def check(strip, result, save) -> SaveCheck:
    return check_against_save(strip, result, save[1])


@pytest.fixture
def no_arguments(monkeypatch):
    """``main`` parses ``sys.argv``, which under pytest holds pytest's own arguments."""
    monkeypatch.setattr("sys.argv", ["chan.roll_momentum"])


def frame(columns: dict[str, list[float]], days: int | None = None) -> pd.DataFrame:
    """A synthetic strip of contracts in delivery order on consecutive business days."""
    length = days or len(next(iter(columns.values())))
    index = pd.bdate_range("2020-01-01", periods=length)
    return pd.DataFrame(columns, index=index, dtype=float)


class TestTheDeclaredRule:
    """Items 2 and 3 of the declared rule on synthetic arrays."""

    def test_the_threshold_is_three_percent_and_both_sides_are_strict(self) -> None:
        assert THRESHOLD == 0.03
        longs, shorts = roll_signals([0.031, 0.03, 0.0, -0.03, -0.031])
        assert longs.tolist() == [True, False, False, False, False]
        assert shorts.tolist() == [False, False, False, False, True]

    def test_a_nan_gamma_opens_neither(self) -> None:
        longs, shorts = roll_signals([np.nan, 0.05, np.nan, -0.05])
        assert longs.tolist() == [False, True, False, False]
        assert shorts.tolist() == [False, False, False, True]

    def test_the_threshold_is_a_parameter(self) -> None:
        longs, shorts = roll_signals([0.02, -0.02], threshold=0.01)
        assert (longs.tolist(), shorts.tolist()) == ([True, False], [False, True])

    def test_the_position_is_longs_less_shorts(self) -> None:
        position = roll_position(*roll_signals([0.05, 0.0, -0.05, np.nan]))
        assert position.tolist() == [1.0, 0.0, -1.0, 0.0]

    def test_a_position_earns_the_next_row(self) -> None:
        """Today's γ sets the position, and tomorrow's return pays it. Same-day would look ahead."""
        position = np.array([1.0, 0.0, -1.0, 1.0])
        market = np.array([0.5, 0.01, 0.02, -0.03])
        assert rule_returns(position, market).tolist() == [0.0, 0.01, 0.0, 0.03]

    def test_a_nan_return_is_zero(self) -> None:
        position = np.ones(3)
        assert rule_returns(position, np.array([np.nan, np.nan, 0.01])).tolist() == [0, 0, 0.01]

    def test_mismatched_inputs_are_refused(self) -> None:
        with pytest.raises(ValueError, match="one shape"):
            rule_returns(np.zeros(3), np.zeros(4))


class TestTheRoll:
    """Item 3's roll, which earns the old contract through L − 7 and the new from L − 6."""

    def test_the_roll_comes_seven_rows_before_the_last_price(self) -> None:
        """A first contract priced on rows 0 to 10, so L = 10, and a second on every row."""
        near = [100.0 + t for t in range(11)] + [np.nan] * 5
        far = [200.0 + 2 * t for t in range(16)]
        contracts = frame({"TU-2020H": near, "TU-2020M": far})
        held = held_contracts(contracts)
        assert ROLL_ROWS == 7
        assert held.iloc[0] is None
        assert held.iloc[1:4].tolist() == ["TU-2020H"] * 3
        assert held.iloc[4:].tolist() == ["TU-2020M"] * 12
        returns = held_returns(contracts)
        assert np.isnan(returns.iloc[0])
        assert returns.iloc[3] == pytest.approx(103 / 102 - 1, rel=1e-15)
        assert returns.iloc[4] == pytest.approx(208 / 206 - 1, rel=1e-15)

    def test_the_roll_row_is_a_parameter(self) -> None:
        near = [100.0 + t for t in range(11)] + [np.nan] * 5
        far = [200.0 + 2 * t for t in range(16)]
        contracts = frame({"TU-2020H": near, "TU-2020M": far})
        held = held_contracts(contracts, roll_rows=0)
        assert held.iloc[1:11].tolist() == ["TU-2020H"] * 10
        assert held.iloc[11:].tolist() == ["TU-2020M"] * 5
        with pytest.raises(ValueError, match="at least 0 rows"):
            held_contracts(contracts, roll_rows=-1)

    def test_the_contract_trading_on_the_file_s_last_row_never_rolls(self) -> None:
        """Its last priced row is the file's last row, which says nothing about its expiry."""
        contracts = frame({"TU-2020H": [100.0, 101.0, 102.0], "TU-2020M": [200.0, 201.0, 202.0]})
        assert held_contracts(contracts).iloc[1:].tolist() == ["TU-2020H", "TU-2020H"]

    def test_a_contract_unpriced_the_row_before_is_passed_over(self) -> None:
        """The held contract must be priced at t − 1, so a later listing is not held on day one."""
        contracts = frame({"TU-2020H": [np.nan, 101.0, 102.0], "TU-2020M": [200.0, 201.0, 202.0]})
        assert held_contracts(contracts).iloc[1:].tolist() == ["TU-2020M", "TU-2020H"]

    def test_a_row_no_contract_qualifies_for_holds_nothing(self) -> None:
        """One contract priced on rows 0 to 10, so L = 10, qualifies only through row 3."""
        contracts = frame({"TU-2020H": [100.0 + t for t in range(11)] + [np.nan] * 5})
        held = held_contracts(contracts)
        assert held.iloc[1:4].tolist() == ["TU-2020H"] * 3
        assert all(name is None for name in held.iloc[4:])
        assert held_returns(contracts).iloc[4:].isna().all()

    def test_a_contract_ending_one_row_before_the_file_still_rolls(self) -> None:
        """Only a contract priced on the file's very last row is read as never expiring."""
        near = [100.0 + t for t in range(15)] + [np.nan]
        far = [200.0 + 2 * t for t in range(16)]
        held = held_contracts(frame({"TU-2020H": near, "TU-2020M": far}))
        assert held.iloc[1:8].tolist() == ["TU-2020H"] * 7
        assert held.iloc[8:].tolist() == ["TU-2020M"] * 8

    def test_the_level_adds_the_held_contract_s_own_changes(self) -> None:
        """No roll jump enters: the level moves by each row's change within one contract."""
        near = [100.0 + t for t in range(11)] + [np.nan] * 5
        far = [200.0 + 2 * t for t in range(16)]
        level = adjusted_level(frame({"TU-2020H": near, "TU-2020M": far}))
        assert level.tolist() == [0.0, 1.0, 2.0, 3.0] + [3.0 + 2 * k for k in range(1, 13)]

    def test_the_march_2012_roll(self, strip) -> None:
        """``TU-2012H``'s last row is 03-30, so it earns through 03-21 and ``TU-2012M`` from 03-22.

        03-21 is row L − 7.
        """
        held = held_contracts(strip.contracts)
        assert str(strip.contracts["TU-2012H"].last_valid_index().date()) == "2012-03-30"
        assert held.loc["2012-03-20":"2012-03-21"].tolist() == ["TU-2012H"] * 2
        assert held.loc["2012-03-22":"2012-03-23"].tolist() == ["TU-2012M"] * 2
        rows = strip.contracts.index
        last = rows.get_loc(pd.Timestamp("2012-03-30"))
        assert rows[last - ROLL_ROWS] == pd.Timestamp("2012-03-21")

    def test_the_fifth_contract_is_counted_among_those_priced_the_day_before(self) -> None:
        columns = {f"TU-202{k}H": [10.0 * (k + 1), 10.0 * (k + 1) + 1] for k in range(6)}
        columns["TU-2020H"] = [10.0, np.nan]
        contracts = frame(columns)
        assert fifth_contract_returns(contracts).iloc[1] == pytest.approx(51 / 50 - 1)
        assert fifth_contract_returns(contracts, on_both_days=True).iloc[1] == pytest.approx(
            61 / 60 - 1
        )
        assert np.isnan(fifth_contract_returns(contracts).iloc[0])

    def test_a_contract_first_priced_today_is_not_counted_on_both_days(self) -> None:
        """A nearest contract that lists at t is priced at t but not at t − 1, so it is skipped."""
        columns = {"TU-2019Z": [np.nan, 5.0]}
        columns.update({f"TU-202{k}H": [100.0, 100.0 + k] for k in range(1, 7)})
        contracts = frame(columns)
        assert fifth_contract_returns(contracts, on_both_days=True).iloc[1] == pytest.approx(
            0.05, rel=1e-12
        )

    def test_fewer_than_five_priced_leaves_the_fifth_return_nan(self) -> None:
        contracts = frame({f"TU-202{k}H": [1.0, 2.0] for k in range(4)})
        assert fifth_contract_returns(contracts).isna().all()


class TestTheVintage:
    def test_the_strip_is_its_pinned_source(self, strip) -> None:
        vendor, basis, saved, folder, count = LIFTED_SOURCES[SOURCE_FILE]
        assert SOURCE_FILE == "inputDataDaily_TU_20120813.mat"
        assert {(m.vendor, m.price_basis, m.obtained) for m in strip.members} == {
            (vendor, basis, saved)
        }
        assert (vendor, basis, saved, folder) == (
            "chan-mat",
            "raw",
            "2012-08-14",
            "inputdatadaily_tu_20120813",
        )
        assert len(strip.members) == count == 94
        assert strip.contracts.shape[1] == 93
        assert strip.spot.name == "TU-SPOT"

    def test_it_holds_5565_days_from_1990_06_22(self, result) -> None:
        assert len(result.days) == 5565
        assert str(result.days[0].date()) == "1990-06-22"
        assert str(result.days[-1].date()) == "2012-08-13"

    def test_the_window_is_913_rows_to_the_file_s_last(self, result) -> None:
        days = result.window_days
        assert (WINDOW_START, WINDOW_END) == (
            pd.Timestamp("2009-01-02"),
            pd.Timestamp("2012-08-13"),
        )
        assert len(days) == 913
        assert days[0] == WINDOW_START and days[-1] == WINDOW_END == result.days[-1]

    def test_the_save_is_tu_momentum_s(self, save) -> None:
        entry, closes = save
        assert entry.path == "inputdataohlcdaily_20120511/tu.csv"
        assert (entry.vendor, entry.price_basis, entry.obtained) == (
            "chan-mat",
            "adjusted",
            "2012-05-12",
        )
        assert len(closes) == 2000
        assert str(closes.index[-1].date()) == "2012-05-11"


class TestTheRebuildAgainstTheSave:
    """The rebuild over the 1,999 changes it shares with the 2012-05-11 save."""

    def test_the_two_agree_on_every_day_but_the_jump_row(self, check) -> None:
        assert check.changes == 1999
        assert check.correlation == pytest.approx(0.998359, abs=5e-7), SPEC
        assert SAVE_ROUNDING == 1.5e-4
        assert check.beyond_rounding == 30
        assert check.beyond_rounding_on_jump_row == 30

    def test_the_rounding_threshold_sits_between_rounding_and_the_jumps(self, result, save) -> None:
        """Off the roll row the changes agree within 1e-4, and every jump beyond is 0.0078 or more.

        Both files print four decimals, so that is what rounding alone allows,
        and any threshold between the two counts the same 30 changes.
        """
        closes = save[1]
        span = np.asarray(result.days.isin(closes.index))
        difference = np.abs(np.diff(closes.to_numpy(dtype=float)) - np.diff(result.level[span]))
        within = difference[difference <= SAVE_ROUNDING]
        beyond = difference[difference > SAVE_ROUNDING]
        assert within.max() == pytest.approx(1e-4, abs=1e-9), SPEC
        assert beyond.min() == pytest.approx(0.0078, abs=1e-9), SPEC
        assert len(beyond) == 30

    def test_a_planted_change_past_rounding_is_counted_off_the_roll_row(
        self, strip, result, save
    ) -> None:
        """A close moved mid-contract adds two changes beyond rounding and none on row L − 7.

        Moving it by 1.6e-4 is just past the threshold and by 1e-3 is far past it,
        so the count holds the comparison to 1.5e-4 rather than to anything the
        jumps alone would allow.
        """
        closes = save[1]
        span = np.asarray(result.days.isin(closes.index))
        difference = np.abs(np.diff(closes.to_numpy(dtype=float)) - np.diff(result.level[span]))
        rows = np.flatnonzero(span)
        held = held_contracts(strip.contracts).to_numpy()
        last = {
            name: strip.contracts.index.get_loc(strip.contracts[name].last_valid_index())
            for name in strip.contracts.columns
        }
        k = next(
            k
            for k in range(1000, len(closes) - 1)
            if difference[k - 1] < 1e-9
            and difference[k] < 1e-9
            and all(last[held[rows[j]]] - rows[j] > 20 for j in (k, k + 1))
        )
        for planted in (1.6e-4, 1e-3):
            moved = closes.copy()
            moved.iloc[k] += planted
            found = check_against_save(strip, result, moved)
            assert found.beyond_rounding == 32
            assert found.beyond_rounding_on_jump_row == 30

    def test_the_save_s_span_holds_32_rolls(self, strip, save) -> None:
        """The held contract changes 32 times, so 30 of the 32 jump rows differ beyond rounding.

        On the other two, the save's change on that row lands within rounding of the rebuild's.
        """
        closes = save[1]
        held = held_contracts(strip.contracts).loc[closes.index]
        rolls = int((held.iloc[1:].to_numpy() != held.iloc[:-1].to_numpy()).sum())
        assert rolls == 32

    def test_the_rebuild_follows_the_save_s_days(self, result, save) -> None:
        closes = save[1]
        assert result.days[result.days.isin(closes.index)].equals(closes.index)

    def test_a_save_holding_a_day_the_strip_lacks_is_refused(self, strip, result, save) -> None:
        closes = save[1].copy()
        closes.index = closes.index + pd.Timedelta(hours=1)
        with pytest.raises(ValueError, match="cannot be paired"):
            check_against_save(strip, result, closes)


class TestTheSixRows:
    """Rows 1 to 3 miss the book under the declared rule, and rows 4 to 6 hold."""

    def test_the_book_s_printed_figures(self) -> None:
        assert (BOOK_APR_PERCENT, BOOK_SHARPE, BOOK_MAX_DRAWDOWN_PERCENT) == ("2.5", "2.1", "1.1")

    def test_row_1_the_apr_misses(self, result) -> None:
        found = result.figures.apr
        assert found == pytest.approx(0.013725, abs=5e-7), SPEC
        assert not matches(100 * found, BOOK_APR_PERCENT)
        assert gap(100 * found, BOOK_APR_PERCENT) == -1.1

    def test_row_2_the_sharpe_ratio_misses(self, result) -> None:
        found = result.figures.sharpe
        assert found == pytest.approx(1.803348, abs=5e-7), SPEC
        assert not matches(found, BOOK_SHARPE)
        assert gap(found, BOOK_SHARPE) == -0.3

    def test_row_3_the_maximum_drawdown_misses(self, result) -> None:
        found = result.figures.max_drawdown
        assert found == pytest.approx(-0.007299, abs=5e-7), SPEC
        assert not matches(-100 * found, BOOK_MAX_DRAWDOWN_PERCENT)
        assert gap(-100 * found, BOOK_MAX_DRAWDOWN_PERCENT) == -0.4

    def test_rows_4_to_6_hold(self, result) -> None:
        assert all(margin > 0 for margin in margins(result))

    def test_a_miss_is_reported_as_one(self) -> None:
        assert module._verdict(1.803348, "2.1") == "did not reproduce, gap -0.3"
        assert module._verdict(2.144165, "2.1") == "reproduced"
        assert module._claim(0.000348) == "reproduced"
        assert module._claim(-0.000348) == "did not reproduce"


class TestTheComparisonMargins:
    """Rows 4 to 6: the declared rule against Example 6.1's on one series, rows and arithmetic."""

    def test_example_6_1_on_the_rebuild(self, result) -> None:
        found = result.example_figures
        assert found.apr == pytest.approx(0.013377, abs=5e-7), SPEC
        assert found.sharpe == pytest.approx(1.196742, abs=5e-7), SPEC
        assert found.max_drawdown == pytest.approx(-0.009167, abs=5e-7), SPEC

    def test_a_claim_with_no_margin_does_not_hold(self) -> None:
        """ "Higher" and "reduced" need the revised figure strictly better."""
        assert module._claim(1e-12) == "reproduced"
        assert module._claim(0.0) == "did not reproduce"

    def test_example_6_1_s_rule_is_tu_momentum_s_own(self, result) -> None:
        """One copy of the rule: the three functions of ``chan.tu_momentum`` on the rebuild."""
        held = positions(*signals(result.level))
        np.testing.assert_array_equal(held, result.example_positions)
        np.testing.assert_array_equal(strategy_returns(held, result.market), result.example_daily)

    def test_each_margin(self, result) -> None:
        apr, sharpe, drawdown = margins(result)
        assert apr == pytest.approx(0.000348, abs=5e-7), SPEC
        assert sharpe == pytest.approx(0.606606, abs=5e-7), SPEC
        assert drawdown == pytest.approx(0.001868, abs=5e-7), SPEC

    def test_row_4_s_margin_is_about_the_rebuild_s_own_error(self, check) -> None:
        """0.035 points of APR, against the 0.031 the rebuild and the save part by over 849 rows."""
        apr_error = check.revised_on_rebuild.apr - check.revised_on_save.apr
        assert apr_error == pytest.approx(0.000309, abs=5e-7)

    def test_the_claims_hold_on_the_save_too(self, check) -> None:
        revised, example = check.revised_on_save, check.example_on_save
        assert revised.apr > example.apr
        assert revised.sharpe > example.sharpe
        assert abs(revised.max_drawdown) < abs(example.max_drawdown)

    def test_cutting_the_window_first_moves_example_6_1(self, result) -> None:
        """The 250-day signal then starts 250 rows into the window, on 663 of its 913 rows."""
        found = result.example_cut_first_figures.apr
        assert found == pytest.approx(0.008435, abs=5e-7), SPEC
        level = result.level[result.window]
        longs, shorts = signals(level)
        assert int((longs | shorts).sum()) == 663


class TestTheRowsBeside:
    def test_the_book_s_own_comparison(self) -> None:
        """Rows 1 to 3 against Example 6.1's printed figures, on 2004-06-01 to 2012-05-11."""
        assert (
            EXAMPLE_6_1_BOOK_APR_PERCENT,
            EXAMPLE_6_1_BOOK_SHARPE,
            EXAMPLE_6_1_BOOK_MAX_DRAWDOWN_PERCENT,
        ) == ("1.7", "1", "2.5")
        assert float(BOOK_APR_PERCENT) > float(EXAMPLE_6_1_BOOK_APR_PERCENT)
        assert float(BOOK_SHARPE) > float(EXAMPLE_6_1_BOOK_SHARPE)
        assert float(BOOK_MAX_DRAWDOWN_PERCENT) < float(EXAMPLE_6_1_BOOK_MAX_DRAWDOWN_PERCENT)

    def test_the_revised_rule_on_the_save_s_own_close(self, check) -> None:
        """The second vintage, over the 849 window rows it covers."""
        found = check.revised_on_save
        assert check.shared_window_rows == 849
        assert 100 * found.apr == pytest.approx(1.437321, abs=5e-7), SPEC
        assert found.sharpe == pytest.approx(1.791969, abs=5e-7), SPEC
        assert 100 * found.max_drawdown == pytest.approx(-0.807695, abs=5e-7), SPEC

    def test_example_6_1_on_the_save_is_entry_33_s_pin(self, check, save) -> None:
        """``TestTheWindow::test_its_figures`` in ``tests/test_tu_momentum.py`` pins its digits."""
        assert check.example_on_save == tu_momentum.tu_momentum(save[1]).active_line_figures

    def test_both_rules_on_the_rebuild_over_the_same_rows(self, check) -> None:
        revised, example = check.revised_on_rebuild, check.example_on_rebuild
        assert 100 * revised.apr == pytest.approx(1.468184, abs=5e-7), SPEC
        assert revised.sharpe == pytest.approx(1.870808, abs=5e-7), SPEC
        assert 100 * revised.max_drawdown == pytest.approx(-0.729860, abs=5e-7), SPEC
        assert 100 * example.apr == pytest.approx(1.445672, abs=5e-7), SPEC
        assert example.sharpe == pytest.approx(1.250783, abs=5e-7), SPEC
        assert 100 * example.max_drawdown == pytest.approx(-0.916666, abs=5e-7), SPEC

    def test_the_rule_is_long_or_flat_and_never_short(self, result) -> None:
        held = result.held_position
        assert int((held > 0).sum()) == 572
        assert round(100 * (held > 0).mean(), 2) == 62.65
        assert int((held < 0).sum()) == 0
        assert int((np.diff(held) != 0).sum()) == 21

    def test_the_window_starts_flat(self, result) -> None:
        """γ is below 0.03 on 2008-12-31, and all five contracts share one price on three days."""
        gamma = pd.Series(result.gamma, index=result.days)
        assert gamma.loc["2008-12-31"] == pytest.approx(0.0161092, abs=5e-8), SPEC
        for day in ("2009-01-02", "2009-01-05", "2009-01-06"):
            assert abs(gamma.loc[day]) < 1e-13
        assert result.held_position[0] == 0

    def test_gamma_has_no_nan_in_the_window(self, result) -> None:
        """So the NaN-as-false comparison never decides a window row."""
        assert not np.isnan(result.gamma[result.window]).any()
        assert np.nanmean(result.gamma[result.window]) == pytest.approx(0.035943, abs=5e-7), SPEC

    def test_the_month_unit_gamma_never_trades(self, result) -> None:
        """It is a third of the column-unit γ on every row and peaks below the threshold.

        The three equal-price days carry round-off of order 1e-15 in both, so the
        comparison allows that much absolutely.
        """
        window = result.window
        np.testing.assert_allclose(
            result.gamma_in_months[window], result.gamma[window] / 3, rtol=1e-9, atol=1e-13
        )
        assert np.nanmax(result.gamma_in_months[window]) == pytest.approx(0.02447, abs=5e-6)
        assert (result.month_position == 0).all()

    def test_the_month_unit_gamma_is_a_third_on_every_defined_row(self, result) -> None:
        """Every TU contract is a quarter from the next, so the ratio holds on the full index."""
        defined = np.isfinite(result.gamma)
        assert defined.sum() == 1087
        np.testing.assert_array_equal(np.isfinite(result.gamma_in_months), defined)
        np.testing.assert_allclose(
            result.gamma_in_months[defined], result.gamma[defined] / 3, rtol=1e-9, atol=1e-13
        )

    def test_the_fifth_contract_reading(self, result) -> None:
        found = result.fifth_figures
        assert found.apr == pytest.approx(0.024712, abs=5e-7), SPEC
        assert found.sharpe == pytest.approx(2.144165, abs=5e-7), SPEC
        assert found.max_drawdown == pytest.approx(-0.011583, abs=5e-7), SPEC
        assert result.fifth_on_both_days_figures.sharpe == pytest.approx(1.957852, abs=5e-7)

    def test_the_fifth_contract_reading_lands_two_of_the_book_s_three(self, result) -> None:
        """Why it is set aside rather than ignored: it lands nearer the book than the rule does."""
        found = result.fifth_figures
        assert matches(100 * found.apr, BOOK_APR_PERCENT)
        assert matches(found.sharpe, BOOK_SHARPE)
        assert not matches(-100 * found.max_drawdown, BOOK_MAX_DRAWDOWN_PERCENT)


class TestTheGuardDecision:
    """``load_strip`` guards each member's own rows, and no window-level call is added."""

    def test_every_guard_call_reads_one_member_over_its_own_rows(self, monkeypatch) -> None:
        seen = []

        def record(legs, *, start, end):
            ((entry, series),) = legs
            seen.append((entry.path, start == series.index[0], end == series.index[-1]))

        monkeypatch.setattr(roll_returns, "refuse_window_crossing_a_break", record)
        monkeypatch.setattr(tu_momentum, "refuse_window_crossing_a_break", record)
        with redirect_stdout(io.StringIO()):
            run()
        assert len(seen) == 95
        assert all(own_start and own_end for _, own_start, own_end in seen)
        assert sum(path.startswith("inputdatadaily_tu_20120813/") for path, _, _ in seen) == 94
        assert ("inputdataohlcdaily_20120511/tu.csv", True, True) in seen

    def test_every_row_earns_within_one_contract_priced_on_both_days(self, strip) -> None:
        """So the level has no gap over the full index, ``TU-1998M``'s restart included."""
        held = held_contracts(strip.contracts)
        prices = strip.contracts
        for t in range(1, len(prices)):
            symbol = held.iloc[t]
            assert np.isfinite(prices[symbol].iloc[t - 1]) and np.isfinite(prices[symbol].iloc[t])
        assert np.isfinite(held_returns(strip.contracts).iloc[1:]).all()

    def test_tu_1998m_restarts_and_is_still_read_across(self, strip) -> None:
        column = strip.contracts["TU-1998M"]
        held = np.flatnonzero(column.notna().to_numpy())
        assert held[-1] - held[0] + 1 != len(held)

    def test_main_turns_a_guard_refusal_into_one_line(self, monkeypatch, no_arguments) -> None:
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("inputdatadaily_tu_20120813/tu-2012m.csv changes scale")

        monkeypatch.setattr(roll_returns, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(SystemExit, match="tu-2012m.csv changes scale"):
            main()

    def test_main_turns_a_missing_vintage_into_one_line(
        self, monkeypatch, tmp_path, no_arguments
    ) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit, match="inputDataDaily_TU_20120813.mat"):
            main()

    def test_main_lets_any_other_error_through_as_itself(self, monkeypatch, no_arguments) -> None:
        def fail(*_a, **_k):
            raise ValueError("a bug, not a refusal")

        monkeypatch.setattr(module, "load_strip", fail)
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
    def test_it_prints_the_six_rows_with_their_verdicts(self, printed) -> None:
        for label, cells in (
            ("APR percent", ["1.372525", "2.5", "-1.1"]),
            ("Sharpe ratio", ["1.803348", "2.1", "-0.3"]),
            ("Maximum drawdown percent", ["0.729860", "1.1", "-0.4"]),
            ("Higher APR", ["0.013725", "0.013377", "+0.000348", "reproduced"]),
            ("Higher Sharpe ratio", ["1.803348", "1.196742", "+0.606606", "reproduced"]),
            ("Reduced maximum drawdown", ["-0.007299", "-0.009167", "+0.001868", "reproduced"]),
        ):
            row = next(r for r in printed.splitlines() if r.strip().startswith(label))
            assert all(cell in row.split() for cell in cells), row
        assert printed.count("did not reproduce") == 3

    def test_it_names_both_vintages_and_the_label(self, printed) -> None:
        assert "inputdatadaily_tu_20120813/" in printed
        assert "inputdataohlcdaily_20120511/tu.csv" in printed
        assert "Exploratory." in printed
        assert "Entry 35" in printed

    def test_it_prints_the_rows_beside(self, printed) -> None:
        assert "return correlation 0.998359, 30 changes" in printed
        assert "long on 572 of 913 rows, 62.65 percent, short on 0, 21 changes" in printed
        assert "Sharpe ratio 2.144165" in printed
        assert "flat on 913 of 913 rows" in printed
        assert "APR 0.008435" in printed
