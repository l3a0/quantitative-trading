"""The pins for VX against ES on VX's roll return, *Algorithmic Trading* locations 2747 to 2754.

This file is the single authority for every number a prose surface quotes
about this replication. ``docs/replication-log.md`` Entry 41 carries the
verdicts and points here row by row.

Every pin reads three vintages and one of two specifications, so they are
stated once here.

- **Vintages.** Three of Chan's book-two files. Each one's identity is its
  row of ``LIFTED_SOURCES`` in ``tests/support/committed_vintages.py``.

  1. ``inputdatadaily_vx_20120507/``, from ``inputDataDaily_VX_20120507.mat``,
     chan-mat, basis ``raw``, saved 2012-05-08. 72 VX contracts from VX-2007F
     to VX-2012Z over 1,543 days from 2006-03-23 to 2012-05-07, with no spot,
     read through ``chan.roll_returns.load_strip``.
  2. ``vix/vix.csv``, from ``VIX.csv``, chan-csv, basis ``raw``, saved
     2012-05-09. 5,635 rows from 1990-01-02 to 2012-05-08.
  3. ``inputdataohlcdaily_20120507/es.csv``, from
     ``inputDataOHLCDaily_20120507.mat``, chan-mat, basis ``adjusted``, saved
     2012-05-09. ES holds 2,000 rows from 2004-06-02 to 2012-05-08.

- **The specifications.** ``VX_ES_rollreturn.m``, git blob ``849e0ac`` at
  EpchanPreview ``e4bc46f``, with one of two hedges. On the days all three
  hold, each contract is the front from 40 to 10 rows before its last priced
  row, starting no earlier than the row after the previous front ended. On a
  front row, ``(VX − VIX) / (expiry − row + 1)`` above 0.1 is short ``hedge``
  front VX contracts and one ES contract, below −0.1 long both, and anything
  else flat. Each day earns yesterday's dollar profit on
  ``y = [1000·VX, 50·ES]`` over yesterday's gross market value, less one
  basis point of the day's change in market value over the same gross, with
  NaN set to 0. The figures are taken over the 448 rows after the first 500
  from 2008-08-04: ``prod(1 + r)^(252 / n) − 1``, ``√252 · mean / std`` with
  the std dividing by n − 1, and ``calculateMaxDD``, with no risk-free rate.

  1. **H**, the hedge 0.3906 of the script's commented lines 47 and 55,
     whose figures its lines 81 to 82 print and the book's come from.
  2. **U**, the hedge [1, 1] of its live lines 48 to 49 and 56 to 57, whose
     figures its lines 86 to 88 print.

Each figure is held at full precision under a tight tolerance, against the
script's comment at the decimals it prints and against the book's two at the
precision Chan printed, through ``matches``.

Exploratory. Reproducing Chan's figures spends his 2008 to 2012 sample on a
rule and a hedge he chose. A scratch run landed every figure before the
criterion was written on the issue. The run first ran here on 2026-10-10.
"""

from __future__ import annotations

import io
import math
from contextlib import redirect_stdout
from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from chan import paths, roll_returns
from chan import vx_es_roll_return as module
from chan.khandani_lo_book_two import gap, matches
from chan.series import WindowCrossesScaleBreak, refuse_window_crossing_a_break, scale_breaks
from chan.vintage import VintageUnavailable
from chan.vx_es import ANCHOR, SOURCE_FILE, TRAINING_DAYS
from chan.vx_es_roll_return import (
    BOOK_APR_PERCENT,
    BOOK_SHARPE,
    ENTRY_THRESHOLD,
    HEDGE,
    HEDGED_COMMENT,
    ONE_WAY_COST,
    SHIPPED_COMMENT,
    SHIPPED_HEDGE,
    VIX_FILE,
    RollReturnTrade,
    common_days,
    daily_returns,
    fitted_hedge,
    main,
    market_values,
    positions,
    read_sources,
    roll_return_trade,
    run,
)
from chan.xle_uso_roll_return import front_windows
from tests.support.committed_vintages import LIFTED_SOURCES

TIGHT = 1e-12

day = pd.Timestamp

#: The book's test, "July 29, 2010, to May 7, 2012".
TEST_START = day("2010-07-29")
TEST_END = day("2012-05-07")


@pytest.fixture(scope="module")
def sources() -> module.Sources:
    return read_sources()


@pytest.fixture(scope="module")
def hedged(sources) -> RollReturnTrade:
    return roll_return_trade(sources, HEDGE)


@pytest.fixture(scope="module")
def shipped(sources) -> RollReturnTrade:
    return roll_return_trade(sources, SHIPPED_HEDGE)


@pytest.fixture(scope="module")
def fitted(sources) -> RollReturnTrade:
    return roll_return_trade(sources, fitted_hedge())


@pytest.fixture(scope="module")
def windows(sources) -> list:
    return front_windows(sources.strip.contracts)


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
    monkeypatch.setattr("sys.argv", ["chan.vx_es_roll_return"])


class TestTheVintages:
    def test_the_strip_is_its_pinned_source(self, sources) -> None:
        vendor, basis, saved, folder, count = LIFTED_SOURCES["inputDataDaily_VX_20120507.mat"]
        assert (vendor, basis, saved, folder, count) == (
            "chan-mat",
            "raw",
            "2012-05-08",
            "inputdatadaily_vx_20120507",
            72,
        )
        strip = sources.strip
        assert {(m.vendor, m.price_basis, m.obtained) for m in strip.members} == {
            (vendor, basis, saved)
        }
        assert {m.path.split("/")[0] for m in strip.members} == {folder}

    def test_vix_is_its_pinned_source(self, sources) -> None:
        vendor, basis, saved, folder, _ = LIFTED_SOURCES[VIX_FILE]
        assert (vendor, basis, saved, folder) == ("chan-csv", "raw", "2012-05-09", "vix")
        member = sources.vix_member
        assert (member.vendor, member.price_basis, member.obtained) == (vendor, basis, saved)
        assert member.path == "vix/vix.csv"

    def test_es_is_its_pinned_source(self, sources) -> None:
        vendor, basis, saved, folder, _ = LIFTED_SOURCES[SOURCE_FILE]
        assert (vendor, basis, saved, folder) == (
            "chan-mat",
            "adjusted",
            "2012-05-09",
            "inputdataohlcdaily_20120507",
        )
        member = sources.es_member
        assert (member.vendor, member.price_basis, member.obtained) == (vendor, basis, saved)
        assert member.path == "inputdataohlcdaily_20120507/es.csv"

    def test_the_strip_holds_72_contracts_in_delivery_order_and_no_spot(self, sources) -> None:
        contracts = sources.strip.contracts
        assert sources.strip.spot is None
        assert contracts.shape == (1543, 72)
        assert (contracts.columns[0], contracts.columns[-1]) == ("VX-2007F", "VX-2012Z")
        assert list(contracts.columns) == sorted(contracts.columns)
        assert (contracts.index[0], contracts.index[-1]) == (day("2006-03-23"), TEST_END)

    def test_vix_holds_5635_rows_and_es_2000(self, sources) -> None:
        assert len(sources.vix) == 5635
        assert sources.vix.notna().all()
        assert (sources.vix.index[0], sources.vix.index[-1]) == (
            day("1990-01-02"),
            day("2012-05-08"),
        )
        assert len(sources.es) == 2000
        assert (sources.es.index[0], sources.es.index[-1]) == (
            day("2004-06-02"),
            day("2012-05-08"),
        )


class TestTheHedgedSpecification:
    """H, the hedge 0.3906, against lines 81 to 82 and location 2754."""

    def test_the_apr(self, hedged) -> None:
        assert hedged.apr == pytest.approx(0.06906463533351137, abs=TIGHT)
        assert matches(hedged.apr, HEDGED_COMMENT.apr)
        assert HEDGED_COMMENT.apr == "0.069065"

    def test_the_sharpe_ratio(self, hedged) -> None:
        assert hedged.sharpe == pytest.approx(1.002020489339432, abs=TIGHT)
        assert matches(hedged.sharpe, HEDGED_COMMENT.sharpe)
        assert HEDGED_COMMENT.sharpe == "1.002020"

    def test_the_maximum_drawdown(self, hedged) -> None:
        assert hedged.max_drawdown == pytest.approx(-0.07568284958529414, abs=TIGHT)
        assert matches(hedged.max_drawdown, HEDGED_COMMENT.max_drawdown)
        assert HEDGED_COMMENT.max_drawdown == "-0.075683"

    def test_the_longest_drawdown(self, hedged) -> None:
        assert hedged.max_drawdown_days == 259
        assert matches(hedged.max_drawdown_days, HEDGED_COMMENT.max_drawdown_days)
        assert HEDGED_COMMENT.max_drawdown_days == "259"

    def test_both_reproduce_the_book_s_figures(self, hedged) -> None:
        """Location 2754's "6.9 percent" and "a Sharpe ratio of 1", at the precision printed."""
        assert (BOOK_APR_PERCENT, BOOK_SHARPE) == ("6.9", "1")
        assert matches(100 * hedged.apr, BOOK_APR_PERCENT)
        assert matches(hedged.sharpe, BOOK_SHARPE)

    def test_the_hedge_is_the_printed_constant(self) -> None:
        assert HEDGE == 0.3906


class TestTheShippedSpecification:
    """U, the hedge [1, 1] of the live lines, against lines 86 to 88."""

    def test_the_apr(self, shipped) -> None:
        assert shipped.apr == pytest.approx(0.29390641242002613, abs=TIGHT)
        assert matches(shipped.apr, SHIPPED_COMMENT.apr)
        assert SHIPPED_COMMENT.apr == "0.293906"

    def test_the_sharpe_ratio(self, shipped) -> None:
        assert shipped.sharpe == pytest.approx(3.263951598374718, abs=TIGHT)
        assert matches(shipped.sharpe, SHIPPED_COMMENT.sharpe)
        assert SHIPPED_COMMENT.sharpe == "3.263952"

    def test_the_maximum_drawdown(self, shipped) -> None:
        assert shipped.max_drawdown == pytest.approx(-0.03579807048938177, abs=TIGHT)
        assert matches(shipped.max_drawdown, SHIPPED_COMMENT.max_drawdown)
        assert SHIPPED_COMMENT.max_drawdown == "-0.035798"

    def test_the_longest_drawdown(self, shipped) -> None:
        assert shipped.max_drawdown_days == 59
        assert matches(shipped.max_drawdown_days, SHIPPED_COMMENT.max_drawdown_days)
        assert SHIPPED_COMMENT.max_drawdown_days == "59"


class TestTheVerdicts:
    def test_every_gap_is_zero_with_the_sign_the_log_prints(self, hedged, shipped) -> None:
        """The replication log's verdict table, computed minus printed at the printed precision."""
        gaps = [
            gap(hedged.apr, HEDGED_COMMENT.apr),
            gap(hedged.sharpe, HEDGED_COMMENT.sharpe),
            gap(hedged.max_drawdown, HEDGED_COMMENT.max_drawdown),
            gap(hedged.max_drawdown_days, HEDGED_COMMENT.max_drawdown_days),
            gap(shipped.apr, SHIPPED_COMMENT.apr),
            gap(shipped.sharpe, SHIPPED_COMMENT.sharpe),
            gap(shipped.max_drawdown, SHIPPED_COMMENT.max_drawdown),
            gap(shipped.max_drawdown_days, SHIPPED_COMMENT.max_drawdown_days),
            gap(100 * hedged.apr, BOOK_APR_PERCENT),
            gap(hedged.sharpe, BOOK_SHARPE),
        ]
        assert gaps == [0.0] * 10
        assert [math.copysign(1, g) for g in gaps] == [-1, 1, 1, 1, 1, -1, -1, 1, 1, 1]

    def test_neither_rule_lands_the_other_s_figures(self, hedged, shipped) -> None:
        """Each specification misses the other's printed APR and Sharpe ratio by the same size."""
        assert gap(shipped.apr, HEDGED_COMMENT.apr) == 0.224841
        assert gap(shipped.sharpe, HEDGED_COMMENT.sharpe) == 2.261932
        assert gap(hedged.apr, SHIPPED_COMMENT.apr) == -0.224841
        assert gap(hedged.sharpe, SHIPPED_COMMENT.sharpe) == -2.261932

    def test_the_two_rules_hold_the_same_days_with_the_same_signs(self, hedged, shipped) -> None:
        """The hedge scales the VX column and nothing else."""
        assert (hedged.es_leg == shipped.es_leg).all()
        assert np.array_equal(hedged.positions[:, :-1], HEDGE * shipped.positions[:, :-1])


class TestTheFittedHedge:
    """The row beside the replication, with no verdict: chan.vx_es's fitted hedge traded instead."""

    def test_the_fitted_hedge_is_chan_vx_es_s(self, fitted) -> None:
        assert fitted.hedge == pytest.approx(0.3905939904665755, abs=TIGHT)
        assert matches(fitted.hedge, "0.3906")

    def test_it_misses_the_script_s_sixth_decimal_on_both(self, fitted) -> None:
        assert fitted.apr == pytest.approx(0.06906215847032793, abs=TIGHT)
        assert fitted.sharpe == pytest.approx(1.0019778657128104, abs=TIGHT)
        assert not matches(fitted.apr, HEDGED_COMMENT.apr)
        assert not matches(fitted.sharpe, HEDGED_COMMENT.sharpe)
        assert gap(fitted.apr, HEDGED_COMMENT.apr) == -0.000003
        assert gap(fitted.sharpe, HEDGED_COMMENT.sharpe) == -0.000042


class TestTheCounts:
    def test_all_three_calendars_share_the_strip_s_1543_days(self, sources, hedged) -> None:
        assert len(hedged.days) == 1543
        assert hedged.days.equals(sources.strip.contracts.index)

    def test_948_days_from_the_anchor_and_448_in_the_test(self, hedged) -> None:
        assert int((hedged.days >= ANCHOR).sum()) == 948
        assert hedged.days[hedged.days >= ANCHOR][0] == ANCHOR
        assert len(hedged.test) == 948 - TRAINING_DAYS == 448
        assert (hedged.test_days[0], hedged.test_days[-1]) == (TEST_START, TEST_END)

    def test_the_test_holds_224_days_196_short_and_28_long(self, hedged) -> None:
        leg = hedged.es_leg[hedged.test]
        assert int((leg != 0).sum()) == 224
        assert int((leg < 0).sum()) == 196
        assert int((leg > 0).sum()) == 28

    def test_the_test_holds_32_entries_from_flat(self, hedged) -> None:
        assert int(hedged.entries_from_flat[hedged.test].sum()) == 32

    def test_each_entry_from_flat_earns_0(self, hedged) -> None:
        entries = np.flatnonzero(hedged.entries_from_flat)
        assert len(entries) == 104
        assert (hedged.daily[entries] == 0).all()

    def test_every_day_is_measured(self, hedged) -> None:
        assert len(hedged.daily) == 1543
        assert np.isfinite(hedged.daily).all()

    def test_65_of_the_71_windows_hold_a_row(self, sources, windows) -> None:
        contracts = sources.strip.contracts
        assert len(windows) == 71
        held = [w for w in windows if len(w.rows)]
        assert len(held) == 65
        first = held[0]
        assert contracts.columns[first.column] == "VX-2007F"
        assert (contracts.index[first.first], contracts.index[first.last]) == (
            day("2006-11-14"),
            day("2006-12-28"),
        )
        assert len(first.rows) == 31


class TestTheQuirks:
    """The two quirks the module docstring names, on these files."""

    def test_every_contract_the_loop_reads_marks_exactly_one_expiry(self, sources) -> None:
        priced = sources.strip.contracts.notna().to_numpy()[:, :-1]
        marks = priced & ~np.vstack([priced[1:], np.zeros((1, priced.shape[1]), bool)])
        assert (marks.sum(axis=0) == 1).all()

    def test_eight_contracts_are_priced_on_the_file_s_last_day(self, sources) -> None:
        last = sources.strip.contracts.iloc[-1].dropna()
        assert len(last) == 8
        assert last.index[0] == "VX-2012K"

    def test_vx_2012k_reads_as_expiring_on_the_last_day(self, sources, windows) -> None:
        contracts = sources.strip.contracts
        k = next(w for w in windows if contracts.columns[w.column] == "VX-2012K")
        assert contracts.index[k.expiry] == TEST_END
        assert contracts.index[k.last] == day("2012-04-23")
        after = [w for w in windows if w.column > k.column]
        assert len(after) == 6
        assert all(len(w.rows) == 0 for w in after)

    def test_the_test_s_last_10_rows_hold_nothing(self, hedged) -> None:
        held = np.flatnonzero((hedged.positions != 0).any(axis=1))
        assert hedged.days[held[-1]] <= day("2012-04-23")
        assert not hedged.positions[-10:].any()
        assert hedged.days[-11] == day("2012-04-23")

    def test_an_entry_from_flat_pays_no_cost(self, sources, hedged) -> None:
        """With the cost charged on the entry's own gross, the APR would be lower."""
        contracts = sources.strip.contracts
        values = market_values(contracts, sources.es.loc[hedged.days].to_numpy(dtype=float))
        today = np.nansum(np.abs(hedged.positions * values), axis=1)
        entries = hedged.entries_from_flat
        charged = hedged.daily.copy()
        charged[entries] = -ONE_WAY_COST
        assert (today[entries] > 0).all()
        assert (charged[hedged.test] <= hedged.test_daily).all()
        assert (charged[hedged.test] < hedged.test_daily).sum() == 32


class TestTheRules:
    """Each step on frames built so the answer is known."""

    EXPIRY = 50

    @classmethod
    def _strip(cls, rows: int = 120) -> pd.DataFrame:
        """Three contracts at 0, the first expiring on row 50, so its window runs rows 10 to 40.

        A price of 0 keeps ``VX − VIX`` exact, so a roll can sit on the threshold.
        """
        frame = {}
        for k, last in enumerate((cls.EXPIRY, 100, 110)):
            column = np.full(rows, np.nan)
            column[: last + 1] = 0.0
            frame[f"VX-20{10 + k}F"] = column
        return pd.DataFrame(frame, index=pd.date_range("2020-01-01", periods=rows))

    def _held(self, row: int, above: float, hedge: float = 1.0) -> np.ndarray:
        """The positions with the front ``above`` VIX on ``row`` and level with it elsewhere."""
        strip = self._strip()
        vix = np.zeros(len(strip))
        vix[row] = -above
        return positions(strip, vix, hedge)

    def test_the_days_to_settlement_count_one_past_expiry_on_the_first_row(self) -> None:
        """Row 10 is 40 rows before expiry, so it divides by 41: 4.05 / 41 sits below 0.1."""
        assert not self._held(10, 4.05).any()
        assert self._held(10, 4.15)[10, -1] == -1

    def test_the_days_to_settlement_count_one_past_expiry_on_the_last_row(self) -> None:
        """Row 40 is 10 rows before expiry, so it divides by 11: 1.05 / 11 sits below 0.1."""
        assert not self._held(40, 1.05).any()
        assert self._held(40, 1.15)[40, -1] == -1

    @pytest.mark.parametrize("sign", [1, -1])
    def test_the_threshold_is_strict(self, sign) -> None:
        """Row 35 divides by 16, so 1.6 over it is exactly the threshold and holds nothing."""
        assert 1.6 / (self.EXPIRY - 35 + 1) == ENTRY_THRESHOLD
        assert not self._held(35, sign * 1.6).any()
        assert self._held(35, sign * 1.65)[35, -1] == -sign

    def test_above_is_short_both_legs_and_below_long_both(self) -> None:
        short = self._held(20, 5.0, hedge=0.5)
        long = self._held(20, -5.0, hedge=0.5)
        assert short[20].tolist() == [-0.5, 0, 0, -1]
        assert long[20].tolist() == [0.5, 0, 0, 1]
        assert np.count_nonzero(short) == np.count_nonzero(long) == 2

    def test_a_row_off_every_front_window_holds_nothing(self) -> None:
        assert not self._held(5, 5.0).any()
        assert not self._held(45, 5.0).any()

    def test_a_nan_vix_holds_nothing(self) -> None:
        assert not self._held(20, np.nan).any()

    @staticmethod
    def _returns(held, vx, es) -> np.ndarray:
        values = np.column_stack([1000 * np.asarray(vx, float), 50 * np.asarray(es, float)])
        return daily_returns(np.asarray(held, float), values)

    def test_each_day_earns_yesterday_s_position_over_yesterday_s_gross(self) -> None:
        # Row 0 holds short 0.5 VX at 20 and short 1 ES at 1,000, a gross of
        # 10,000 + 50,000. VX rises 1 and ES falls 20, so the day makes
        # −500 + 1,000 = 500, and the held position's value moves by
        # 500 + 1,000, which pays one basis point.
        ret = self._returns([[-0.5, -1], [-0.5, -1]], [20, 21], [1000, 980])
        assert ret[0] == 0
        assert ret[1] == pytest.approx(500 / 60000 - ONE_WAY_COST * 1500 / 60000, abs=1e-15)

    def test_today_s_position_earns_nothing_today(self) -> None:
        ret = self._returns([[0, 0], [-0.5, -1], [0, 0]], [20, 21, 21], [1000, 980, 980])
        assert ret[1] == 0

    def test_an_entry_from_flat_earns_0_and_pays_nothing(self) -> None:
        ret = self._returns([[0, 0], [-0.5, -1], [-0.5, -1]], [20, 20, 20], [1000, 1000, 1000])
        assert ret.tolist() == [0.0, 0.0, 0.0]

    def test_an_exit_pays_one_basis_point_of_yesterday_s_gross(self) -> None:
        ret = self._returns([[-0.5, -1], [0, 0]], [20, 20], [1000, 1000])
        assert ret[1] == pytest.approx(-ONE_WAY_COST, abs=1e-18)

    def test_a_contract_s_unpriced_rows_are_skipped(self) -> None:
        """``smartsum`` skips a NaN, so a contract nobody holds adds nothing even when unpriced."""
        held = np.array([[-0.5, 0, -1], [-0.5, 0, -1]])
        values = np.array([[20000, np.nan, 50000], [21000, np.nan, 49000]])
        assert daily_returns(held, values)[1] == pytest.approx(
            500 / 60000 - ONE_WAY_COST * 1500 / 60000, abs=1e-15
        )

    def test_the_calendars_intersect_in_the_script_s_order(self) -> None:
        index = pd.date_range("2020-01-01", periods=5)
        contracts = pd.DataFrame({"VX-2010F": range(5)}, index=index)
        vix = pd.Series(1.0, index=index[1:])
        es = pd.Series(1.0, index=index[:4])
        assert list(common_days(contracts, vix, es)) == list(index[1:4])


class TestTheGuardAndTheReads:
    def test_the_strip_is_read_through_load_strip(self, monkeypatch) -> None:
        seen = []
        real = module.load_strip

        def record(root, data_dir=None, *, source_file=None):
            seen.append((root, data_dir, source_file))
            return real(root, data_dir, source_file=source_file)

        monkeypatch.setattr(module, "load_strip", record)
        read_sources(paths.DATA_DIR)
        assert seen == [("VX", paths.DATA_DIR, None)]

    def test_es_is_guarded_over_its_span_and_vix_from_the_anchor(self, monkeypatch) -> None:
        seen = []

        def record(legs, *, start, end):
            seen.append(([entry.path for entry, _ in legs], start, end))

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", record)
        read_sources()
        assert seen == [
            (["inputdataohlcdaily_20120507/es.csv"], day("2004-06-02"), day("2012-05-08")),
            (["vix/vix.csv"], ANCHOR, TEST_END),
        ]

    def test_neither_guarded_span_carries_a_flagged_day(self, sources) -> None:
        assert scale_breaks(sources.es) == []
        assert scale_breaks(sources.vix.loc[ANCHOR:TEST_END]) == []

    def test_a_guard_over_the_whole_common_span_refuses_on_2007_02_27(
        self, sources, hedged
    ) -> None:
        assert scale_breaks(sources.vix) == [day("2007-02-27")]
        with pytest.raises(
            WindowCrossesScaleBreak, match="vix/vix.csv changes scale on 2007-02-27"
        ):
            refuse_window_crossing_a_break(
                [(sources.vix_member, sources.vix)], start=hedged.days[0], end=hedged.days[-1]
            )

    def test_the_flagged_day_sets_a_long_position(self, sources, hedged) -> None:
        assert (sources.vix.loc[day("2007-02-26")], sources.vix.loc[day("2007-02-27")]) == (
            11.15,
            18.31,
        )
        assert hedged.es_leg[hedged.days.get_loc(day("2007-02-27"))] == 1

    def test_no_figure_reads_vix_before_the_test_s_first_held_close(self, sources, hedged) -> None:
        """A position reads its own day's VIX, and the first test return earns 2010-07-28's."""
        before = sources.vix.index <= day("2010-07-27")
        moved = sources.vix.where(~before, sources.vix * 10)
        changed = roll_return_trade(replace(sources, vix=moved), HEDGE)
        assert (changed.test_daily == hedged.test_daily).all()
        assert not (changed.positions == hedged.positions).all()

    @pytest.mark.parametrize(
        ("source", "symbol", "when"),
        [(VIX_FILE, "VIX", "2010-01-04"), (SOURCE_FILE, "ES", "2009-06-01")],
    )
    def test_a_scale_change_in_vix_or_es_is_refused(
        self, source, symbol, when, monkeypatch
    ) -> None:
        real = module.load_panel

        def broken(name, **kwargs):
            members, frame = real(name, **kwargs)
            if name == source:
                frame = frame.copy()
                frame.loc[day(when) :, symbol] *= 10
            return members, frame

        monkeypatch.setattr(module, "load_panel", broken)
        with pytest.raises(WindowCrossesScaleBreak, match=f"{symbol.lower()}.csv changes scale"):
            read_sources()

    def test_a_scale_change_in_a_contract_is_refused(self, monkeypatch) -> None:
        real = roll_returns.load_panel

        def broken(name, **kwargs):
            members, frame = real(name, **kwargs)
            frame = frame.copy()
            own = frame["VX-2010F"].dropna().index
            frame.loc[own[len(own) // 2] :, "VX-2010F"] *= 10
            return members, frame

        monkeypatch.setattr(roll_returns, "load_panel", broken)
        with pytest.raises(WindowCrossesScaleBreak, match="vx-2010f.csv changes scale"):
            read_sources()

    def test_run_reads_the_directory_it_is_given(self, tmp_path) -> None:
        with pytest.raises(VintageUnavailable, match="inputDataDaily_VX_20120507.mat"):
            run(tmp_path)

    def test_run_returns_both_specifications(self) -> None:
        with redirect_stdout(io.StringIO()):
            found, as_shipped = run()
        assert found.apr == pytest.approx(0.06906463533351137, abs=TIGHT)
        assert as_shipped.apr == pytest.approx(0.29390641242002613, abs=TIGHT)


class TestTheReport:
    @staticmethod
    def _rows(out: str, label: str) -> list[list[str]]:
        return [r.split() for r in out.splitlines() if r.strip().startswith(label)]

    def test_it_prints_each_figure_beside_the_script_s(self, printed) -> None:
        apr = self._rows(printed, "APR ")
        sharpe = self._rows(printed, "Sharpe ratio")
        drawdown = self._rows(printed, "Maximum drawdown")
        longest = self._rows(printed, "Longest drawdown, rows")
        assert apr[0][-3:] == ["0.069065", "0.069065", "reproduced"]
        assert apr[1][-3:] == ["0.293906", "0.293906", "reproduced"]
        assert sharpe[0][-3:] == ["1.002020", "1.002020", "reproduced"]
        assert sharpe[1][-3:] == ["3.263952", "3.263952", "reproduced"]
        assert drawdown[0][-3:] == ["-0.075683", "-0.075683", "reproduced"]
        assert drawdown[1][-3:] == ["-0.035798", "-0.035798", "reproduced"]
        assert longest[0][-3:] == ["259", "259", "reproduced"]
        assert longest[1][-3:] == ["59", "59", "reproduced"]

    def test_it_prints_the_book_s_two(self, printed) -> None:
        assert self._rows(printed, "APR, percent")[0][-3:] == ["6.906464", "6.9", "reproduced"]
        assert self._rows(printed, "Sharpe ratio")[2][-3:] == ["1.002020", "1", "reproduced"]

    def test_it_prints_the_fitted_hedge_with_no_verdict(self, printed) -> None:
        line = next(r for r in printed.splitlines() if "The fitted hedge" in r)
        assert line.split() == [
            "The",
            "fitted",
            "hedge",
            "0.390594:",
            "APR",
            "0.069062",
            "against",
            "0.069065,",
            "Sharpe",
            "ratio",
            "1.001978",
            "against",
            "1.002020",
        ]

    def test_it_prints_the_vintages_the_window_and_the_counts(self, printed) -> None:
        assert printed.startswith(
            "VX against ES on VX's roll return, Algorithmic Trading location 2754"
        )
        assert "inputdatadaily_vx_20120507/" in printed
        assert "vix/vix.csv" in printed
        assert "inputdataohlcdaily_20120507/es.csv" in printed
        assert "calendar  2006-03-23 to 2012-05-07, 1543 days all three hold" in printed
        assert "test      2010-07-29 to 2012-05-07, 448 days" in printed
        assert (
            "held on 224 days, short on 196, long on 28, 32 entries from flat, each free"
        ) in printed
        assert "Exploratory." in printed

    def test_a_miss_is_reported_as_one(self) -> None:
        assert module._verdict(0.069065, HEDGED_COMMENT.apr) == "reproduced"
        assert module._verdict(0.069062, HEDGED_COMMENT.apr) == "gap -3e-06"
        assert module._verdict(3.26, BOOK_SHARPE) == "gap +2"

    def test_main_turns_a_guard_refusal_into_one_line(self, monkeypatch, no_arguments) -> None:
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("vix/vix.csv changes scale")

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(SystemExit, match="vix.csv changes scale") as stopped:
            main()
        assert str(stopped.value) == "vix/vix.csv changes scale"

    def test_main_turns_a_missing_vintage_into_one_line(
        self, monkeypatch, tmp_path, no_arguments
    ) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit, match="inputDataDaily_VX_20120507.mat"):
            main()

    def test_main_lets_any_other_error_through(self, monkeypatch, no_arguments) -> None:
        def broken(*_a, **_k):
            raise ValueError("a programming error keeps its traceback")

        monkeypatch.setattr(module, "run", broken)
        with pytest.raises(ValueError, match="keeps its traceback"):
            main()

    def test_main_refuses_an_argument(self, monkeypatch) -> None:
        monkeypatch.setattr("sys.argv", ["chan.vx_es_roll_return", "--bogus"])
        with pytest.raises(SystemExit) as refused:
            main()
        assert refused.value.code == 2
