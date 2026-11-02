"""The pins for TU momentum traded on the lagged roll return, *Algorithmic Trading*'s location 2690.

This file is the single authority for every number a prose surface quotes
about this experiment and the rows beside it, with three exceptions.
``blog/roll-momentum-lessons.md`` also quotes its figure's numbers, which
``tests/test_roll_momentum_figures.py`` holds, its sketches' dates, price
changes and twelve-second hold, which ``tests/test_roll_momentum_whiteboard.py``
holds, and Example 6.1's figures on the 2012-05-11 save, which
``TestTheWindow::test_its_figures`` in ``tests/test_tu_momentum.py`` holds. It
also quotes claims no test asserts, which README lists. ``docs/replication-log.md``
Entry 36 carries the verdicts and points here row by row. The rows are the ones
[issue 353](https://github.com/l3a0/quantitative-trading/issues/353) declared
under "The pins".

Every pin on the committed files reads one vintage and one specification
unless it names the second vintage, so both are stated once here and carried
in each figure's failure message as :data:`SPEC`.

- **Vintage.** ``inputdatadaily_tu_20120813/``, chan-mat, raw, saved
  2012-08-14, 93 contracts over 5,565 days from 1990-06-22 to 2012-08-13 and
  ``TU-SPOT`` from 1995-08-10, read through ``chan.roll_returns.load_strip``. Its identity is
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
from chan.matlab_helpers import backshift
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
from chan.roll_returns import MONTHS_PER_YEAR, NEAREST, Strip, load_strip
from chan.series import WindowCrossesScaleBreak
from chan.tu_momentum import (
    HOLD_DAYS,
    LOOKBACK,
    TRADING_DAYS,
    positions,
    read_sources,
    signals,
    strategy_returns,
)
from tests.support.committed_vintages import LIFTED_SOURCES
from tests.support.post_tables import either_way, not_found_once, tables

POST = paths.REPO_ROOT / "blog" / "roll-momentum-lessons.md"

SPEC = (
    "inputdatadaily_tu_20120813/ chan-mat raw saved 2012-08-14, gamma in column units, long "
    "above 0.03 and short below -0.03, backshift(1, pos) times the front contract rolled 7 "
    "rows before its last price, computed on 5,565 rows and cut to 2009-01-02..2012-08-13"
)

#: The thresholds either side of 0.03 at which the APR margin turns negative.
APR_SIGN_THRESHOLDS = (0.029, 0.032)
#: The threshold one step below 0.03 at which all three margins turn negative.
ALL_THREE_THRESHOLD = 0.028
#: γ on the window's first days, when all five fitted prices are equal, is
#: zero to within ten to this power.
ZERO_EXPONENT = -13


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


def far_three_share_one_price(strip: Strip) -> np.ndarray:
    """Each row on which the 3rd, 4th and 5th of the five fitted contracts carry one price."""
    prices = strip.contracts.to_numpy(dtype=float)
    one = np.zeros(len(prices), dtype=bool)
    for t, row in enumerate(prices):
        nearest = roll_returns._nearest_adjacent(row)
        if nearest is not None:
            third, fourth, fifth = row[nearest[2:]]
            one[t] = third == fourth == fifth
    return one


def roll_rows_matching_neither(strip: Strip, result: RollMomentum, save) -> tuple[int, int, int]:
    """The save's rolls on row L − 7, how many match neither contract's own change, and how
    many match only the new contract's."""
    closes = save[1]
    contracts = strip.contracts
    prices = contracts.to_numpy(dtype=float)
    span = np.asarray(result.days.isin(closes.index))
    rows = np.flatnonzero(span)[1:]
    change = dict(zip(rows, np.diff(closes.to_numpy(dtype=float)), strict=True))
    held = module._held_columns(contracts, ROLL_ROWS)
    last = module._last_priced_rows(contracts)
    jump = [t for t in rows if held[t] >= 0 and last[held[t]] - t == ROLL_ROWS]

    def matches(t: int, c: int) -> bool:
        return abs(change[t] - (prices[t, c] - prices[t - 1, c])) <= SAVE_ROUNDING

    neither = sum(not matches(t, held[t]) and not matches(t, held[t] + 1) for t in jump)
    new_only = sum(matches(t, held[t] + 1) and not matches(t, held[t]) for t in jump)
    return len(jump), neither, new_only


def at_threshold(result: RollMomentum, threshold: float):
    """The declared rule's window figures with ``threshold`` in place of 0.03."""
    position = roll_position(*roll_signals(result.gamma, threshold))
    return tu_momentum.figures(rule_returns(position, result.market)[result.window])


def leading_equal_price_days(strip: Strip, result: RollMomentum) -> int:
    """How many window days, from the first, all five fitted contracts close at one price."""
    prices = strip.contracts.to_numpy(dtype=float)
    count = 0
    for t in np.flatnonzero(result.window):
        row = prices[t]
        if len(set(row[roll_returns._nearest_adjacent(row)])) != 1:
            break
        count += 1
    return count


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

    def test_it_holds_5565_days_from_1990_06_22(self, strip, result) -> None:
        """The contracts start on 1990-06-22 and the spot only on 1995-08-10."""
        assert len(result.days) == 5565
        assert str(result.days[0].date()) == "1990-06-22"
        assert str(result.days[-1].date()) == "2012-08-13"
        assert str(strip.spot.first_valid_index().date()) == "1995-08-10"

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

    def test_the_save_does_not_say_which_contract_earns_row_l_minus_7(
        self, strip, result, save
    ) -> None:
        """On 29 of the 32 rolls the save's change on row L − 7 matches neither contract's own.

        So the save fixes rows L − 8 and L − 6 and leaves row L − 7 open. Giving
        that row to the new contract, a roll 8 rows before the last price, moves
        the declared rule to 1.366491 percent and 1.789044.
        """
        assert roll_rows_matching_neither(strip, result, save) == (32, 29, 1)
        eight = roll_momentum(strip, roll_rows=8)
        assert 100 * eight.figures.apr == pytest.approx(1.366491, abs=5e-7), SPEC
        assert eight.figures.sharpe == pytest.approx(1.789044, abs=5e-7), SPEC

    def test_the_roll_row_reaches_both_series_the_rules_earn_on(self, strip, result) -> None:
        """The declared rule earns ``market`` and Example 6.1's signal reads ``level``.

        In this window Example 6.1 is long on every row whichever roll row its
        level uses, so its figures cannot show a level that ignored the roll row.
        """
        contracts = strip.contracts
        eight = roll_momentum(strip, roll_rows=8)
        np.testing.assert_array_equal(eight.market, held_returns(contracts, 8).to_numpy())
        np.testing.assert_array_equal(eight.level, adjusted_level(contracts, 8).to_numpy())
        assert not np.array_equal(eight.level, result.level)

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

    def test_the_apr_margin_turns_negative_at_2_9_and_3_2_percent(self, result) -> None:
        """Only the APR margin's sign is at stake, so a threshold either side of 0.03 is enough."""
        assert APR_SIGN_THRESHOLDS == (0.029, 0.032)
        for threshold in APR_SIGN_THRESHOLDS:
            assert at_threshold(result, threshold).apr < result.example_figures.apr, threshold

    def test_all_three_margins_turn_negative_at_2_8_percent(self, result) -> None:
        """One step below the book's 0.03, the declared rule loses all three claims."""
        assert ALL_THREE_THRESHOLD == 0.028
        moved = at_threshold(result, ALL_THREE_THRESHOLD)
        example = result.example_figures
        assert moved.apr - example.apr == pytest.approx(-0.003693, abs=5e-7), SPEC
        assert moved.sharpe - example.sharpe == pytest.approx(-0.060471, abs=5e-7), SPEC
        assert abs(example.max_drawdown) - abs(moved.max_drawdown) == pytest.approx(
            -0.000859, abs=5e-7
        ), SPEC

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


class TestWhatTheMarginsAreMadeOf:
    """Example 6.1 holds TU all through the window, and the declared rule is that, less 341 rows."""

    def test_example_6_1_holds_all_25_tranches_long_on_every_window_row(self, result) -> None:
        """Its returns are then the rebuild's own, which is buying and holding TU."""
        held = backshift(1, result.example_positions)[result.window]
        assert len(held) == 913
        assert (held == 25).all(), SPEC
        market = np.nan_to_num(result.market[result.window])
        np.testing.assert_allclose(result.example_daily[result.window], market, rtol=1e-15)

    def test_the_rows_the_declared_rule_steps_aside_compound_to_about_nothing(self, result) -> None:
        """341 flat rows at −0.001244, and 572 long rows carrying all of its 0.050629."""
        held = result.held_position
        market = np.nan_to_num(result.market[result.window])
        flat, long = held == 0, held > 0
        assert int(flat.sum()) == 341
        assert np.prod(1 + market[flat]) - 1 == pytest.approx(-0.001244, abs=5e-7), SPEC
        assert np.prod(1 + market[long]) - 1 == pytest.approx(0.050629, abs=5e-7), SPEC
        whole = np.prod(1 + result.daily[result.window]) - 1
        assert whole == pytest.approx(np.prod(1 + market[long]) - 1, rel=1e-12)

    def test_the_flat_rows_set_on_shared_prices_swing_more(self, strip, result) -> None:
        """TU's annual volatility on the 169 flat rows set on a shared-price γ is 0.016727."""
        one = far_three_share_one_price(strip)
        set_on = one[np.flatnonzero(result.window) - 1]
        rows = set_on & (result.held_position == 0)
        assert int(rows.sum()) == 169
        market = np.nan_to_num(result.market[result.window])
        swing = tu_momentum.figures(market[rows]).annual_volatility
        assert swing == pytest.approx(0.016727, abs=5e-7), SPEC
        assert swing > result.example_figures.annual_volatility

    def test_from_2009_10_01_no_position_rests_on_shared_prices(self, strip, result) -> None:
        """The last shared-price row is 2009-09-29, and its position earns 2009-09-30."""
        one = far_three_share_one_price(strip)
        assert str(result.days[one][-1].date()) == "2009-09-29"
        after = np.asarray(result.window_days >= pd.Timestamp("2009-10-01"))
        revised = tu_momentum.figures(result.daily[result.window][after])
        example = tu_momentum.figures(result.example_daily[result.window][after])
        assert revised.sharpe == pytest.approx(1.845682, abs=5e-7), SPEC
        assert example.sharpe == pytest.approx(1.428115, abs=5e-7), SPEC

    def test_the_two_rules_volatilities_and_average_returns(self, result) -> None:
        """Average annual returns of 0.013661 and 0.013351 over 0.007575 and 0.011156."""
        revised, example = result.figures, result.example_figures
        assert revised.annual_volatility == pytest.approx(0.007575, abs=5e-7), SPEC
        assert example.annual_volatility == pytest.approx(0.011156, abs=5e-7), SPEC
        assert revised.average_annual_return == pytest.approx(0.013661, abs=5e-7), SPEC
        assert example.average_annual_return == pytest.approx(0.013351, abs=5e-7), SPEC


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

    def test_the_64_uncovered_days_cannot_carry_the_gap(self, result, check) -> None:
        """They would need about 4.2 percent to reach the book's 2.5, and add 0.03 percent."""
        uncovered = result.window_days > pd.Timestamp("2012-05-11")
        assert int(uncovered.sum()) == 64
        need = (1.025 ** (913 / 252)) / (1 + check.revised_on_save.apr) ** (849 / 252) - 1
        assert round(100 * need, 1) == 4.2
        added = np.prod(1 + result.daily[result.window][np.asarray(uncovered)]) - 1
        assert round(100 * added, 2) == 0.03

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

    def test_the_window_starts_flat(self, strip, result) -> None:
        """γ is below 0.03 on 2008-12-31, and all five contracts share one price on three days.

        The fourth window day, 2009-01-07, is the first whose five prices differ.
        """
        gamma = pd.Series(result.gamma, index=result.days)
        assert gamma.loc["2008-12-31"] == pytest.approx(0.0161092, abs=5e-8), SPEC
        contracts = strip.contracts
        for day in ("2009-01-02", "2009-01-05", "2009-01-06", "2009-01-07"):
            row = contracts.loc[day].to_numpy(dtype=float)
            five = row[roll_returns._nearest_adjacent(row)]
            assert (len(set(five)) == 1) == (day != "2009-01-07"), day
        for day in ("2009-01-02", "2009-01-05", "2009-01-06"):
            assert abs(gamma.loc[day]) < 10.0**ZERO_EXPONENT
        assert result.held_position[0] == 0

    def test_the_far_three_contracts_share_one_price_on_185_days(self, strip, result) -> None:
        """The 3rd, 4th and 5th fitted contracts carry one price on 185 window days.

        They run from 2009-01-02 to 2009-09-29, and the pattern began before the
        window. 169 of the 341 flat rows take their position, set the row before,
        from a γ fitted on a row where those three share one price. All but one of
        those rows are window rows, and the one is 2008-12-31, the row before it.
        The shared price changes on 180 of the 184 steps from one of those days to
        the next.
        """
        one = far_three_share_one_price(strip)
        window = result.window
        assert int(one[window].sum()) == 185
        days = result.days[window & one]
        assert (str(days[0].date()), str(days[-1].date())) == ("2009-01-02", "2009-09-29")
        set_on = one[np.flatnonzero(window) - 1]
        assert int((set_on & (result.held_position == 0)).sum()) == 169
        set_days = result.days[np.flatnonzero(window) - 1][set_on & (result.held_position == 0)]
        assert str(set_days[0].date()) == "2008-12-31"
        assert (set_days[1:] >= WINDOW_START).all()
        prices = strip.contracts.to_numpy(dtype=float)
        shared = [
            prices[t][roll_returns._nearest_adjacent(prices[t])[2]]
            for t in np.flatnonzero(window & one)
        ]
        assert int((np.diff(shared) != 0).sum()) == 180, "changes from day to day"

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


def signed(value: float, decimals: int) -> str:
    """A figure as the post prints it, with a true minus sign."""
    return f"{value:.{decimals}f}".replace("-", "−")


#: The counts the post spells out in words.
WORDS = {2: "two", 3: "three", 5: "five", 6: "six", 7: "seven", 8: "eight"}
#: The positions the post spells out in words.
ORDINALS = {6: "sixth", 7: "seventh"}


def power_of_ten(exponent: int) -> str:
    """``10`` to ``exponent`` as the post prints it, with a superscript exponent."""
    return "10" + str(exponent).translate(str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹"))


class TestWhatThePostQuotes:
    """At least one copy of each run figure ``blog/roll-momentum-lessons.md`` quotes.

    The classes above pin each figure once, and the post copies it by hand.
    Here each figure is built from the run at the precision the post prints
    it, and looked for in a short fragment holding the number and the few
    words that name one place in the post. Each fragment must occur exactly
    once, so it cannot match a second copy. A typo in a copy that is read, or
    a re-pin that leaves the post behind, fails here, while rewording the
    prose between two figures does not. Where a word states a fact the run
    decides, such as "never short" or "negative", the run is asserted to bear
    it out. The post's two tables are each read whole, as the grid of its
    cells with its row labels and column heads, so a cell changed, added,
    dropped or moved fails, while the same table turned on its side still
    passes. A number's unit is not read, so a table's percent signs could be
    dropped and pass.

    The fragments read the summary's copies, the first copy in the lesson that
    states each figure, and the alt text's exact figures, end values and γ's
    rounded peak. The run's rule facts are read the same way, built from the
    module constants the run uses, so the post's threshold, roll row,
    lookback, hold, number of fitted contracts and days a year cannot drift
    from the code. A count the post spells out, such as "seven trading days",
    is built from its constant through :data:`WORDS`. Where a figure repeats
    in a later lesson or a habit, that later copy is left unread. Example
    6.1's figures on the 2012-05-11 save are read against
    ``tests/test_tu_momentum.py``'s pin through
    ``test_example_6_1_on_the_save_is_entry_33_s_pin``. The copies left unread
    are the title's and the subtitle's words, the later repeats, the book's
    figures where the prose restates them, the sketches' alt texts, which
    ``tests/test_roll_momentum_whiteboard.py`` reads, the references, the alt
    text's readings of the lines along the way, such as "about 3.9 percent by
    late 2010", and the rounded readings ``README.md`` lists. Nothing checks
    Chan's words against their source or the page numbers.
    """

    @pytest.fixture(scope="class")
    @classmethod
    def text(cls) -> str:
        return POST.read_text(encoding="utf-8")

    def test_the_post_holds_two_tables(self, text) -> None:
        assert len(tables(text)) == 2

    def test_lesson_1_s_table(self, result, text) -> None:
        found = result.figures
        apr, sharpe, drawdown = 100 * found.apr, found.sharpe, -100 * found.max_drawdown
        expected = [
            ["", "APR", "Sharpe", "Drawdown"],
            ["Computed", f"{apr:.4f}", f"{sharpe:.6f}", f"{drawdown:.4f}"],
            ["Book", BOOK_APR_PERCENT, BOOK_SHARPE, BOOK_MAX_DRAWDOWN_PERCENT],
            [
                "Gap",
                str(gap(apr, BOOK_APR_PERCENT)),
                str(gap(sharpe, BOOK_SHARPE)),
                str(gap(drawdown, BOOK_MAX_DRAWDOWN_PERCENT)),
            ],
        ]
        assert tables(text)[0] in either_way(expected)

    def test_lesson_2_s_table(self, result, text) -> None:
        revised, example = result.figures, result.example_figures
        apr, sharpe, drawdown = margins(result)
        expected = [
            ["", "APR", "Sharpe", "Drawdown"],
            [
                "Declared",
                f"{revised.apr:.6f}",
                f"{revised.sharpe:.6f}",
                f"{revised.max_drawdown:.6f}",
            ],
            ["6.1", f"{example.apr:.6f}", f"{example.sharpe:.6f}", f"{example.max_drawdown:.6f}"],
            ["Margin", f"{apr:.6f}", f"{sharpe:.6f}", f"{drawdown:.6f}"],
        ]
        assert tables(text)[1] in either_way(expected)

    def test_the_summary(self, result, text) -> None:
        example = result.example_figures
        low, high = APR_SIGN_THRESHOLDS
        for threshold in APR_SIGN_THRESHOLDS:
            assert at_threshold(result, threshold).apr < example.apr, "turns it negative"
        lower = at_threshold(result, ALL_THREE_THRESHOLD)
        assert lower.apr < example.apr and lower.sharpe < example.sharpe, "loses on all three"
        assert abs(lower.max_drawdown) > abs(example.max_drawdown), "loses on all three"
        fragments = [
            f"a threshold of {100 * low:.1f} or {100 * high:.1f} percent instead of the book’s "
            f"{100 * THRESHOLD:.0f} turns it negative.",
            f"At {100 * ALL_THREE_THRESHOLD:.1f} percent the rule here loses on all three.",
        ]
        assert not_found_once(text, fragments) == []

    def test_the_rule_and_the_files(self, strip, result, text) -> None:
        defined = np.isfinite(result.gamma)
        peak = np.nanmax(result.gamma_in_months[result.window])
        contracts = strip.contracts
        window = int(result.window.sum())
        longs, shorts = signals(result.level[result.window])
        (saved,) = {member.obtained for member in strip.members}
        assert peak < THRESHOLD, "never reaches 3 percent"
        assert (result.month_position == 0).all(), "never trades"
        fragments = [
            f"the log prices of the {WORDS[NEAREST]} nearest contracts against their place in "
            f"line, 1 to {NEAREST}. Then γ is {signed(-MONTHS_PER_YEAR, 0)} times the slope",
            f"The {signed(-MONTHS_PER_YEAR, 0)} assumes adjacent contracts are a month apart",
            f"On all {int(defined.sum()):,} days where γ is defined, γ in column units is exactly "
            "three times γ measured in months",
            f"But γ in months peaks at {100 * peak:.3f} percent inside the test window and never "
            f"reaches {100 * THRESHOLD:.0f} percent, so a rule on it never trades.",
            f"Example 6.1 trades in {HOLD_DAYS} tranches. A tranche is one twenty-fifth of the "
            f"capital, opened on one day and held for {HOLD_DAYS}.",
            f"its level {LOOKBACK} trading days back",
            f"Long where γ is strictly above {THRESHOLD:.2f} and short where it is strictly below "
            f"{signed(-THRESHOLD, 2)}.",
            f"trimmed to {WINDOW_START.date()} to {WINDOW_END.date()}, the {window} trading days "
            "of the window Chan names on p. 206.",
            f"no value for the window’s first {LOOKBACK} trading days. Its signal would then "
            f"exist on only {int((longs | shorts).sum())} of the {window}, and its APR, written "
            f"as a fraction, would fall from {result.example_figures.apr:.6f} to "
            f"{result.example_cut_first_figures.apr:.6f}.",
            f"with {TRADING_DAYS} trading days a year, no risk-free rate and no cost.",
            f"This strip holds {contracts.shape[1]} TU contracts over {len(contracts):,} days, "
            f"from {contracts.index[0].date()} to {contracts.index[-1].date()}, and TU’s spot "
            f"price from {strip.spot.first_valid_index().date()}.",
            f"It was saved on {saved} and is the only TU file",
        ]
        assert not_found_once(text, fragments) == []

    def test_lesson_1(self, strip, result, check, save, text) -> None:
        entry, closes = save
        on_save, on_rebuild = check.revised_on_save, check.revised_on_rebuild
        assert str((closes.index[-1] + pd.Timedelta(days=1)).date()) == entry.obtained
        held = result.held_position
        one = far_three_share_one_price(strip)
        days = result.days[result.window & one]
        set_on = one[np.flatnonzero(result.window) - 1]
        gamma = pd.Series(result.gamma, index=result.days)
        assert int((held < 0).sum()) == 0, "never short"
        before_window = result.days[np.flatnonzero(result.window)[0] - 1]
        assert one[np.flatnonzero(result.window)[0] - 1], "the first was set before the window"
        window, shared = int(result.window.sum()), check.shared_window_rows
        need = (1 + float(BOOK_APR_PERCENT) / 100) ** (window / TRADING_DAYS) / (
            1 + on_save.apr
        ) ** (shared / TRADING_DAYS) - 1
        uncovered = np.asarray(result.window_days > closes.index[-1])
        added = np.prod(1 + result.daily[result.window][uncovered]) - 1
        found = result.figures
        assert 100 * found.apr < float(BOOK_APR_PERCENT), "land below the book"
        assert found.sharpe < float(BOOK_SHARPE), "land below the book"
        assert -100 * found.max_drawdown < float(BOOK_MAX_DRAWDOWN_PERCENT), "shallower"
        equal = leading_equal_price_days(strip, result)
        first = np.flatnonzero(result.window)[:equal]
        assert np.abs(result.gamma[first]).max() < 10.0**ZERO_EXPONENT
        fragments = [
            "The APR and the Sharpe ratio land below the book, and the drawdown is shallower "
            "than the book’s.",
            f"On the window’s first {WORDS[equal]} days, the {WORDS[NEAREST]} nearest contracts "
            "close at the same price, so the fit’s slope and γ are zero to within "
            f"{power_of_ten(ZERO_EXPONENT)}.",
            f"Those {WORDS[equal]} days fall inside a longer pattern",
            f"It ends on {closes.index[-1].date()}, was saved the next day, and covers "
            f"{shared} of the window’s {window} trading days.",
            f"gives an APR of {100 * on_save.apr:.4f} percent, a Sharpe ratio of "
            f"{on_save.sharpe:.6f} and a drawdown of {-100 * on_save.max_drawdown:.4f} percent.",
            f"The rebuilt series gives {100 * on_rebuild.apr:.4f} percent, {on_rebuild.sharpe:.6f} "
            f"and {-100 * on_rebuild.max_drawdown:.4f} percent on the same days.",
            f"The {window - shared} window days that close does not cover",
            f"In this window the rule is long on {int((held > 0).sum())} of the {window} days, "
            f"{100 * (held > 0).mean():.2f} percent, and flat on the other "
            f"{int((held == 0).sum())}.",
            "Because γ never falls below −3 percent, the rule is never short.",
            f"It changes position {int((np.diff(held) != 0).sum())} times.",
            f"set by γ on 2008-12-31, which is {100 * gamma.loc['2008-12-31']:.2f} percent, under "
            "the threshold.",
            f"On {len(days)} of the window’s days, from {days[0].date()} to {days[-1].date()},",
            f"The position on {int((set_on & (held == 0)).sum())} of the {int((held == 0).sum())} "
            "flat days",
            f"The first of those days was {before_window.date()}, the day before the window.",
            f"would have to add about {round(100 * need, 1)} percent to reach the book’s "
            f"{BOOK_APR_PERCENT} percent. On the rebuild they add {100 * added:.2f} percent.",
        ]
        assert not_found_once(text, fragments) == []

    def test_lesson_2(self, strip, result, check, text) -> None:
        on_save, example_on_save = check.revised_on_save, check.example_on_save
        revised, example = result.figures, result.example_figures
        apr, sharpe, _ = margins(result)
        held = result.held_position
        market = np.nan_to_num(result.market[result.window])
        flat = np.prod(1 + market[held == 0]) - 1
        long = np.prod(1 + market[held > 0]) - 1
        low, high = APR_SIGN_THRESHOLDS
        for threshold in APR_SIGN_THRESHOLDS:
            assert at_threshold(result, threshold).apr < example.apr, "negative"
        lower = at_threshold(result, ALL_THREE_THRESHOLD)
        assert lower.sharpe < example.sharpe, "even that"
        assert lower.apr < example.apr, "loses all three"
        assert abs(lower.max_drawdown) > abs(example.max_drawdown), "loses all three"
        window = np.flatnonzero(result.window)
        long_before = signals(result.level)[0][window[0] - HOLD_DAYS : window[-1] + 1]
        assert long_before.all(), "always stood above its level 250 trading days earlier"
        tranches = backshift(1, result.example_positions)[result.window]
        assert (tranches == HOLD_DAYS).all(), "all 25 are long on all 913 days"
        one = far_three_share_one_price(strip)
        rows = one[np.flatnonzero(result.window) - 1] & (held == 0)
        swing = tu_momentum.figures(market[rows]).annual_volatility
        after = np.asarray(result.window_days >= pd.Timestamp("2009-10-01"))
        after_revised = tu_momentum.figures(result.daily[result.window][after]).sharpe
        after_example = tu_momentum.figures(result.example_daily[result.window][after]).sharpe
        fragments = [
            f"There the declared rule gives an APR of {100 * on_save.apr:.4f} percent against "
            f"Example 6.1’s {100 * example_on_save.apr:.4f} percent, a Sharpe ratio of "
            f"{on_save.sharpe:.6f} against {example_on_save.sharpe:.6f}, and a drawdown of "
            f"{-100 * on_save.max_drawdown:.4f} percent against "
            f"{-100 * example_on_save.max_drawdown:.4f} percent.",
            f"The APR margin of {apr:.6f} is small.",
            f"the APR margin is {on_save.apr - example_on_save.apr:.6f} on that close and "
            f"{check.revised_on_rebuild.apr - check.example_on_rebuild.apr:.6f} on the rebuild.",
            f"since a threshold of {100 * low:.1f} or {100 * high:.1f} percent turns it negative.",
            f"The Sharpe ratio’s margin of {sharpe:.6f} carries the comparison at the book’s "
            "threshold.",
            f"At {100 * ALL_THREE_THRESHOLD:.1f} percent even that margin turns negative, and the "
            "declared rule loses all three claims.",
            f"From {HOLD_DAYS} trading days before the window to its end, TU always stood above "
            f"its level {LOOKBACK} trading days earlier.",
            f"and all {HOLD_DAYS} are long on all {len(window)} days.",
            f"the mean daily return times {TRADING_DAYS} without compounding",
            f"with an annual volatility of {swing:.6f} against {example.annual_volatility:.6f}.",
            f"From 2009-10-01, once no position rests on those prices, the declared rule’s Sharpe "
            f"ratio is {after_revised:.2f} against Example 6.1’s {after_example:.2f}, so a smaller "
            "margin remains.",
            f"TU’s return compounds to {signed(flat, 6)}, close to nothing.",
            f"it compounds to {long:.6f}, which is the declared rule’s whole return.",
            f"are {revised.average_annual_return:.6f} for the declared rule and "
            f"{example.average_annual_return:.6f} for Example 6.1’s rule.",
            f"the declared rule’s is {revised.annual_volatility:.6f} against "
            f"{example.annual_volatility:.6f} for holding TU.",
            f"the Sharpe ratios of "
            f"{revised.average_annual_return / revised.annual_volatility:.2f} and "
            f"{example.average_annual_return / example.annual_volatility:.2f} follow.",
            f"out of the market on {int((held == 0).sum())} of the {len(held)} days",
        ]
        assert not_found_once(text, fragments) == []

    def test_lesson_3(self, strip, result, check, save, text) -> None:
        contracts = strip.contracts
        held = held_contracts(contracts)
        rolls, neither, new_only = roll_rows_matching_neither(strip, result, save)
        eight = roll_momentum(strip, roll_rows=ROLL_ROWS + 1).figures
        last = contracts["TU-2012H"].last_valid_index()
        through = held.index[held == "TU-2012H"][-1]
        after = held.index[held == "TU-2012M"][0]
        assert contracts.index.get_loc(last) - contracts.index.get_loc(through) == ROLL_ROWS
        # The save matches the rebuild off row L − 7, so it follows the old
        # contract through row L − 8 and the new one from row L − 6.
        assert check.beyond_rounding == check.beyond_rounding_on_jump_row
        span = held.loc[save[1].index].to_numpy()
        assert int((span[1:] != span[:-1]).sum()) == rolls
        fragments = [
            f"still has at least {WORDS[ROLL_ROWS]} trading days left before its last price. So "
            f"the old contract earns through the {ORDINALS[ROLL_ROWS]} trading day before its "
            f"last price and the new one from the {ORDINALS[ROLL_ROWS - 1]}.",
            f"The March 2012 contract’s last price in the strip is on {last.date()}. It earns "
            f"through {through.date()}, and the June contract earns from {after.date()}.",
            f"It follows the old contract until {WORDS[ROLL_ROWS + 1]} trading days before its "
            f"last price and the new one from {WORDS[ROLL_ROWS - 1]},",
            f"On {neither} of the {rolls} rolls in its span,",
            f"and on {'one' if new_only == 1 else new_only} it matches the new contract’s.",
            f"a roll {WORDS[ROLL_ROWS + 1]} days before the last price, the declared rule gives "
            f"an APR of {100 * eight.apr:.4f} percent and a Sharpe ratio of "
            f"{eight.sharpe:.6f}, against {100 * result.figures.apr:.4f} percent and "
            f"{result.figures.sharpe:.6f}.",
            f"covers the {check.changes:,} daily changes the two series share.",
            f"They correlate at {check.correlation:.6f}.",
            f"{check.beyond_rounding} changes differ by more than the files’ rounding. All "
            f"{check.beyond_rounding_on_jump_row} fall on the {ORDINALS[ROLL_ROWS]} trading day "
            "before a contract’s last price,",
            f"The close’s span holds {rolls} rolls, and on the other "
            f"{WORDS[rolls - check.beyond_rounding_on_jump_row]} its change lands within rounding",
            f"sits {check.revised_on_rebuild.apr - check.revised_on_save.apr:.6f} above its APR on "
            "that close.",
        ]
        assert not_found_once(text, fragments) == []

    def test_lesson_4(self, result, text) -> None:
        fifth = result.fifth_figures
        assert matches(100 * fifth.apr, BOOK_APR_PERCENT), "match"
        assert matches(fifth.sharpe, BOOK_SHARPE), "match"
        assert not matches(-100 * fifth.max_drawdown, BOOK_MAX_DRAWDOWN_PERCENT), "misses"
        fragments = [
            f"That gives an APR of {100 * fifth.apr:.4f} percent, a Sharpe ratio of "
            f"{fifth.sharpe:.6f} and a drawdown of {-100 * fifth.max_drawdown:.4f} percent.",
            f"The first two match the book’s {BOOK_APR_PERCENT} percent and {BOOK_SHARPE} at the "
            f"book’s precision. The drawdown misses {BOOK_MAX_DRAWDOWN_PERCENT} percent.",
            f"It gives a Sharpe ratio of {result.fifth_on_both_days_figures.sharpe:.6f}, short of "
            f"the book’s {BOOK_SHARPE}.",
        ]
        assert not_found_once(text, fragments) == []

    def test_the_alt_text(self, strip, result, text) -> None:
        revised, example = result.figures, result.example_figures
        held = result.held_position
        gamma = pd.Series(result.gamma, index=result.days)[result.window]
        example_end = np.prod(1 + result.example_daily[result.window]) - 1
        revised_end = np.prod(1 + result.daily[result.window]) - 1
        assert revised_end > example_end, "just above it"
        (saved,) = {member.obtained for member in strip.members}
        fragments = [
            f"ends at {100 * example_end:.1f} percent. The green line",
            f"It ends just above it, at {100 * revised_end:.1f} percent.",
            f"a step-like line between about 0 and {100 * gamma.max():.1f} percent, with dashed "
            f"lines at {100 * THRESHOLD:.0f} and {signed(-100 * THRESHOLD, 0)} percent.",
            f"Chan’s TU strip, saved {saved},",
            f"sets the declared rule’s APR of {revised.apr:.6f} and Sharpe ratio of "
            f"{revised.sharpe:.6f} beside the book’s",
            f"gives Example 6.1’s rule {example.apr:.6f} and {example.sharpe:.6f},",
            f"γ peaks at {gamma.max():.6f} on {gamma.idxmax().date()}",
            f"the rule is long on {int((held > 0).sum())} trading days, short on none and flat on "
            f"the {int((held == 0).sum())} shaded ones.",
        ]
        assert not_found_once(text, fragments) == []


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
        assert "Entry 36" in printed

    def test_it_prints_the_rows_beside(self, printed) -> None:
        assert "return correlation 0.998359, 30 changes" in printed
        assert "long on 572 of 913 rows, 62.65 percent, short on 0, 21 changes" in printed
        assert "Sharpe ratio 2.144165" in printed
        assert "flat on 913 of 913 rows" in printed
        assert "APR 0.008435" in printed
