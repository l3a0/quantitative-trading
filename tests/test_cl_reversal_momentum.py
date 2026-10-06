"""The pins for crude oil reversal joined to momentum, *Algorithmic Trading* location 2701.

This file is the single authority for every number a prose surface quotes
about this replication and the rows beside it. ``docs/replication-log.md``
Entry 31 carries the verdicts and points here row by row.

Every pin names one of three vintages and one specification, so they are
stated once here.

- **Vintages.** Three saves of Chan's continuous futures, chan-mat, adjusted,
  each read for CL's closes through ``chan.series.load_panel`` and cut to
  ``["CL"].dropna()``. A save is named by the date in its file name, and each
  one's identity is its row of ``LIFTED_SOURCES`` in
  ``tests/support/committed_vintages.py``.

  1. ``inputdataohlcdaily_20120504/``, from ``inputDataOHLCDaily_20120504.mat``,
     downloaded 2012-05-07. CL holds 1,000 rows, 2008-05-19 to 2012-05-04, the
     book's window. Every row marked as the specification reads this save.
  2. ``inputdataohlcdaily_20120511/``, downloaded 2012-05-12, read over the
     same 1,000 days for one row.
  3. ``inputdataohlcdaily_20120507/``, downloaded 2012-05-09. CL runs 2,000
     rows from 2004-05-24 to 2012-05-08. Its 998 rows from 2004-05-24 to
     2008-05-16 are the segment before the book's window.

- **The specification.** ``CL_rev.m``, git blob ``420d501`` at EpchanPreview
  ``e4bc46f``. Long where the close is below ``backshift(30, cl)`` and above
  ``backshift(40, cl)``, short on the mirror, flat otherwise. Each day earns
  ``backshift(1, positions) * (cl − backshift(1, cl)) / backshift(1, cl)``
  with NaN set to 0. The APR is ``prod(1 + r)^(252 / n) − 1`` and the Sharpe
  ratio ``√252 · mean / std`` with n − 1, both over every row, flat rows
  included, with no risk-free rate and no cost. "Momentum only", "reversal
  only" and "ComboOR" are the script's other three rules, named in
  ``chan.cl_reversal_momentum``'s docstring.

Each figure is held at six decimals, the precision the script prints, and the
book's two at the precision Chan printed, through ``matches``.

Exploratory. Reproducing Chan's figures spends the 2008 to 2012 sample on a
rule he chose, and the earlier segment was not registered before it was read.
The run first ran on 2026-10-06.
"""

from __future__ import annotations

import io
from contextlib import redirect_stdout

import numpy as np
import pandas as pd
import pytest

from chan import cl_reversal_momentum as module
from chan import paths
from chan.cl_reversal_momentum import (
    BOOK_APR_PERCENT,
    BOOK_END,
    BOOK_SHARPE,
    BOOK_START,
    CL,
    EARLIER_SOURCE_FILE,
    LATER_SOURCE_FILE,
    MOMENTUM_LOOKBACK,
    REVERSAL_LOOKBACK,
    SCRIPT_APR,
    SCRIPT_SHARPE,
    SOURCE_FILE,
    FourRules,
    Trades,
    combination_positions,
    either_positions,
    four_rules,
    main,
    momentum_positions,
    read_cl,
    reversal_positions,
    run,
    trade,
)
from chan.khandani_lo_book_two import compounded_apr, matches
from chan.matlab_helpers import backshift
from chan.series import WindowCrossesScaleBreak, load_panel, scale_breaks
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import LIFTED_SOURCES

SAVES = (SOURCE_FILE, EARLIER_SOURCE_FILE, LATER_SOURCE_FILE)
BEFORE_END = pd.Timestamp("2008-05-16")


@pytest.fixture(scope="module")
def cl() -> pd.Series:
    return read_cl()[1]


@pytest.fixture(scope="module")
def book(cl) -> FourRules:
    return four_rules(cl)


@pytest.fixture(scope="module")
def later_cl() -> pd.Series:
    return read_cl(LATER_SOURCE_FILE, start=BOOK_START, end=BOOK_END)[1]


@pytest.fixture(scope="module")
def before_cl() -> pd.Series:
    return read_cl(EARLIER_SOURCE_FILE, end=BEFORE_END)[1]


@pytest.fixture(scope="module")
def before(before_cl) -> FourRules:
    return four_rules(before_cl)


@pytest.fixture
def no_arguments(monkeypatch):
    """``main`` parses ``sys.argv``, which under pytest holds pytest's own arguments."""
    monkeypatch.setattr("sys.argv", ["chan.cl_reversal_momentum"])


def _six(traded: Trades) -> tuple[float, float]:
    return round(traded.apr, 6), round(traded.sharpe, 6)


class TestTheVintages:
    @pytest.mark.parametrize("source", SAVES)
    def test_each_save_is_its_pinned_source(self, source) -> None:
        member, _ = read_cl(source)
        vendor, basis, saved, folder, _ = LIFTED_SOURCES[source]
        assert (member.vendor, member.price_basis, member.obtained) == (vendor, basis, saved)
        assert member.path == f"{folder}/cl.csv"

    def test_the_specification_reads_the_save_the_script_loads(self) -> None:
        assert SOURCE_FILE == "inputDataOHLCDaily_20120504.mat"
        assert LIFTED_SOURCES[SOURCE_FILE][2] == "2012-05-07"

    def test_the_book_s_window_is_the_whole_of_cl_in_that_save(self, cl) -> None:
        assert len(cl) == 1000
        assert (cl.index[0], cl.index[-1]) == (BOOK_START, BOOK_END)

    def test_the_earlier_save_runs_back_to_2004(self) -> None:
        _, whole = read_cl(EARLIER_SOURCE_FILE)
        assert len(whole) == 2000
        assert (whole.index[0], whole.index[-1]) == (
            pd.Timestamp("2004-05-24"),
            pd.Timestamp("2012-05-08"),
        )

    def test_the_earlier_save_s_closes_equal_the_specification_s(self, cl) -> None:
        """Every one of the 1,000 days, so its earlier rows extend the same series."""
        _, same = read_cl(EARLIER_SOURCE_FILE, start=BOOK_START, end=BOOK_END)
        assert same.index.equals(cl.index)
        assert (same.to_numpy() == cl.to_numpy()).all()

    def test_the_earlier_save_therefore_gives_the_specification_s_figures(self, cl) -> None:
        _, same = read_cl(EARLIER_SOURCE_FILE, start=BOOK_START, end=BOOK_END)
        assert _six(trade(same, combination_positions(same))) == (0.117600, 1.100368)

    def test_the_later_save_sits_0_27_higher_on_every_day(self, cl, later_cl) -> None:
        assert later_cl.index.equals(cl.index)
        assert np.allclose(later_cl.to_numpy() - cl.to_numpy(), 0.27)

    def test_the_first_close_in_each_segment(self, cl, before_cl) -> None:
        assert round(cl.iloc[0], 2) == 175.48
        assert round(before_cl.iloc[0], 2) == 119.12


class TestTheSpecification:
    """The combination on the 2012-05-04 save over its 1,000 rows."""

    def test_the_apr_reproduces_the_script_s_comment(self, book) -> None:
        assert f"{book.combination.apr:.6f}" == SCRIPT_APR == "0.117600"

    def test_the_sharpe_ratio_reproduces_the_script_s_comment(self, book) -> None:
        assert f"{book.combination.sharpe:.6f}" == SCRIPT_SHARPE == "1.100368"

    def test_both_reproduce_the_book_s_figures(self, book) -> None:
        assert (BOOK_APR_PERCENT, BOOK_SHARPE) == ("12", "1.1")
        assert matches(100 * book.combination.apr, BOOK_APR_PERCENT)
        assert matches(book.combination.sharpe, BOOK_SHARPE)

    def test_it_measures_every_row(self, book) -> None:
        assert len(book.combination.daily) == 1000
        assert np.isfinite(book.combination.daily).all()

    def test_the_position_is_flat_on_most_days(self, book) -> None:
        positions = book.combination.positions
        assert (int((positions > 0).sum()), int((positions < 0).sum())) == (98, 59)
        assert int((positions == 0).sum()) == 843
        assert int((positions != 0).sum()) == 157
        assert book.combination.changes == 124

    def test_the_first_position_is_taken_on_2008_07_18(self, book) -> None:
        positions = book.combination.positions
        assert book.combination.days[np.flatnonzero(positions)[0]] == pd.Timestamp("2008-07-18")

    def test_the_first_40_rows_cannot_signal(self, book) -> None:
        assert not book.combination.positions[:MOMENTUM_LOOKBACK].any()


class TestTheRowsBeside:
    """The script's other three rules and a later save, none of them a verdict."""

    def test_momentum_alone(self, book) -> None:
        assert _six(book.momentum) == (0.090228, 0.439049)

    def test_reversal_alone(self, book) -> None:
        assert _six(book.reversal) == (0.068326, 0.370289)

    def test_the_combination_beats_each_rule_alone(self, book) -> None:
        """The book's sentence, measured on its own window."""
        for alone in (book.momentum, book.reversal):
            assert book.combination.apr > alone.apr
            assert book.combination.sharpe > alone.sharpe

    def test_combo_or(self, book) -> None:
        assert _six(book.either) == (0.125917, 1.123042)

    def test_combo_or_differs_on_10_warm_up_rows_only(self, book) -> None:
        differ = book.combination.days[book.combination.positions != book.either.positions]
        assert len(differ) == 10
        assert (differ[0], differ[-1]) == (pd.Timestamp("2008-07-01"), pd.Timestamp("2008-07-15"))

    def test_there_combo_or_trades_the_reversal_rule(self, book) -> None:
        rows = book.combination.positions != book.either.positions
        assert (book.either.positions[rows] == book.reversal.positions[rows]).all()
        assert np.isnan(backshift(MOMENTUM_LOOKBACK, np.ones(1000)))[rows].all()

    def test_no_close_ties_either_lag(self, cl) -> None:
        close = cl.to_numpy()
        for lookback in (REVERSAL_LOOKBACK, MOMENTUM_LOOKBACK):
            assert not (close == backshift(lookback, close)).any()

    def test_the_later_save(self, later_cl) -> None:
        assert _six(trade(later_cl, combination_positions(later_cl))) == (0.117226, 1.100045)

    def test_the_later_save_still_prints_as_the_book_s_figures(self, later_cl) -> None:
        traded = trade(later_cl, combination_positions(later_cl))
        assert matches(100 * traded.apr, BOOK_APR_PERCENT)
        assert matches(traded.sharpe, BOOK_SHARPE)
        assert not matches(traded.apr, SCRIPT_APR)


class TestBeforeTheBookSWindow:
    """The 2012-05-07 save's 998 rows from 2004-05-24 to 2008-05-16."""

    def test_the_span(self, before_cl) -> None:
        assert len(before_cl) == 998
        assert (before_cl.index[0], before_cl.index[-1]) == (
            pd.Timestamp("2004-05-24"),
            BEFORE_END,
        )

    def test_the_combination(self, before) -> None:
        assert _six(before.combination) == (0.021324, 0.369864)

    def test_momentum_alone(self, before) -> None:
        assert _six(before.momentum) == (0.094589, 0.660514)

    def test_reversal_alone(self, before) -> None:
        assert _six(before.reversal) == (-0.065694, -0.359464)

    def test_momentum_alone_beats_the_combination_there(self, before) -> None:
        assert before.momentum.apr > before.combination.apr
        assert before.momentum.sharpe > before.combination.sharpe


class TestTheMutations:
    """Five changes to the specification, each of which a pin above has to notice."""

    def test_swapping_the_lookbacks_negates_the_rule(self, cl, book) -> None:
        swapped = combination_positions(cl, reversal=MOMENTUM_LOOKBACK, momentum=REVERSAL_LOOKBACK)
        assert (swapped == -book.combination.positions).all()
        assert _six(trade(cl, swapped)) == (-0.115294, -1.100368)

    def test_trading_on_the_same_day_s_position(self, cl, book) -> None:
        close = cl.to_numpy()
        daily = book.combination.positions * (close - backshift(1, close)) / backshift(1, close)
        daily[np.isnan(daily)] = 0
        same_day = Trades(days=cl.index, positions=book.combination.positions, daily=daily)
        assert _six(same_day) == (0.008903, 0.139324)

    def test_measuring_from_the_first_row_both_lags_exist(self, cl, book) -> None:
        late = Trades(
            days=cl.index[MOMENTUM_LOOKBACK:],
            positions=book.combination.positions[MOMENTUM_LOOKBACK:],
            daily=book.combination.daily[MOMENTUM_LOOKBACK:],
        )
        assert len(late.daily) == 960
        assert _six(late) == (0.122789, 1.123147)

    def test_dividing_the_sharpe_ratio_by_n(self, book) -> None:
        daily = book.combination.daily
        assert round(np.sqrt(252) * daily.mean() / daily.std(ddof=0), 6) == 1.100919

    def test_reading_the_later_save_misses_the_script_s_digits(self, later_cl) -> None:
        traded = trade(later_cl, combination_positions(later_cl))
        assert f"{traded.apr:.6f}" != SCRIPT_APR
        assert f"{traded.sharpe:.6f}" != SCRIPT_SHARPE


class TestTheRules:
    """Each rule on a series built so its answer is known."""

    @staticmethod
    def _series(values) -> pd.Series:
        return pd.Series(
            np.asarray(values, dtype=float),
            index=pd.date_range("2020-01-01", periods=len(values)),
        )

    def test_the_combination_longs_below_the_short_lag_and_above_the_long_one(self) -> None:
        closes = self._series([10, 30, 20])
        assert combination_positions(closes, reversal=1, momentum=2).tolist() == [0, 0, 1]
        assert combination_positions(
            self._series([30, 10, 20]), reversal=1, momentum=2
        ).tolist() == [
            0,
            0,
            -1,
        ]

    def test_the_combination_is_flat_where_only_one_condition_holds(self) -> None:
        # Below both lags: the reversal rule is long, the momentum rule short.
        closes = self._series([30, 20, 10])
        assert combination_positions(closes, reversal=1, momentum=2).tolist() == [0, 0, 0]

    def test_momentum_and_reversal_are_mirrors_on_one_lookback(self) -> None:
        closes = self._series([10, 20, 15, 25])
        mom = momentum_positions(closes, lookback=1)
        assert mom.tolist() == [0, 1, -1, 1]
        assert (reversal_positions(closes, lookback=1) == -mom).all()

    def test_combo_or_sums_a_long_and_a_short_to_flat(self) -> None:
        # Row 1 has no 2-day lag, so OR trades the reversal rule alone there.
        # Row 2 sits below both lags, a reversal long and a momentum short.
        closes = self._series([30, 20, 10])
        assert either_positions(closes, reversal=1, momentum=2).tolist() == [0, 1, 0]
        # Row 2 is below the 1-day lag and above the 2-day one, so both say long.
        assert either_positions(self._series([10, 30, 20]), reversal=1, momentum=2).tolist() == [
            0,
            -1,
            1,
        ]

    def test_a_tie_with_a_lag_signals_nothing(self) -> None:
        closes = self._series([10, 10])
        assert momentum_positions(closes, lookback=1).tolist() == [0, 0]
        assert reversal_positions(closes, lookback=1).tolist() == [0, 0]

    def test_trade_earns_yesterday_s_position_on_today_s_move(self) -> None:
        closes = self._series([100, 110, 99])
        traded = trade(closes, np.array([1.0, -1.0, 0.0]))
        assert np.allclose(traded.daily, [0, 0.10, 0.10])

    def test_compounded_apr_is_the_script_s(self, book) -> None:
        daily = book.combination.daily
        assert book.combination.apr == compounded_apr(daily)
        assert np.isclose(book.combination.apr, np.prod(1 + daily) ** (252 / 1000) - 1)


class TestTheGuardAndTheReads:
    @pytest.mark.parametrize("source", SAVES)
    def test_cl_carries_no_flagged_day(self, source) -> None:
        """``tests/test_scale_breaks.py`` names ZB and ZF as the only flagged series here."""
        assert scale_breaks(load_panel(source)[1][CL].dropna()) == []

    def test_run_guards_each_span_it_reads(self, monkeypatch) -> None:
        seen = []

        def record(legs, *, start, end):
            seen.append(([entry.path for entry, _ in legs], start.date(), end.date()))

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", record)
        with redirect_stdout(io.StringIO()):
            run()
        day = pd.Timestamp
        assert seen == [
            (["inputdataohlcdaily_20120504/cl.csv"], BOOK_START.date(), BOOK_END.date()),
            (["inputdataohlcdaily_20120511/cl.csv"], BOOK_START.date(), BOOK_END.date()),
            (
                ["inputdataohlcdaily_20120507/cl.csv"],
                day("2004-05-24").date(),
                BEFORE_END.date(),
            ),
        ]

    @pytest.mark.parametrize("row", [1, 500, 999])
    def test_a_scale_change_anywhere_in_the_window_is_refused(self, row, monkeypatch) -> None:
        members, closes = load_panel(SOURCE_FILE)
        broken = closes.copy()
        days = broken[CL].dropna().index
        broken.loc[days[row:], CL] *= 10
        monkeypatch.setattr(module, "load_panel", lambda *_a, **_k: (members, broken))
        with pytest.raises(WindowCrossesScaleBreak, match="cl.csv"):
            read_cl()

    def test_a_scale_change_outside_the_cut_is_not_read(self, monkeypatch) -> None:
        members, closes = load_panel(EARLIER_SOURCE_FILE)
        broken = closes.copy()
        broken.loc[broken.index > BOOK_END, CL] *= 10
        monkeypatch.setattr(module, "load_panel", lambda *_a, **_k: (members, broken))
        read_cl(EARLIER_SOURCE_FILE, end=BEFORE_END)

    def test_a_refusal_from_the_guard_reaches_the_caller(self, monkeypatch) -> None:
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("flagged")

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(WindowCrossesScaleBreak, match="flagged"):
            run()

    def test_main_turns_a_guard_refusal_into_one_line(self, monkeypatch, no_arguments) -> None:
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("inputdataohlcdaily_20120504/cl.csv changes scale")

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(SystemExit, match="cl.csv changes scale"):
            main()

    def test_run_reads_the_directory_it_is_given(self, tmp_path) -> None:
        with pytest.raises(VintageUnavailable, match="inputDataOHLCDaily_20120504.mat"):
            run(tmp_path)

    def test_main_turns_a_missing_vintage_into_one_line(
        self, monkeypatch, tmp_path, no_arguments
    ) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit, match="inputDataOHLCDaily_20120504.mat"):
            main()

    def test_a_miss_is_reported_as_one(self) -> None:
        assert module._verdict(0.117600, SCRIPT_APR) == "reproduced"
        assert module._verdict(0.117226, SCRIPT_APR) == "gap -0.000374"
        assert module._verdict(1.100045, BOOK_SHARPE) == "reproduced"


@pytest.fixture(scope="module")
def printed() -> str:
    """What ``run`` prints, captured once for the tests that read it."""
    out = io.StringIO()
    with redirect_stdout(out):
        run()
    return out.getvalue()


def _row(out: str, label: str) -> list[str]:
    return next(r for r in out.splitlines() if r.strip().startswith(label)).split()


class TestTheReport:
    def test_it_prints_each_figure_beside_the_script_s_and_the_book_s(self, printed) -> None:
        assert _row(printed, "APR")[-5:] == [
            "0.117600",
            "0.117600",
            "reproduced",
            "12",
            "reproduced",
        ]
        assert _row(printed, "Sharpe ratio")[-5:] == [
            "1.100368",
            "1.100368",
            "reproduced",
            "1.1",
            "reproduced",
        ]
        assert "inputdataohlcdaily_20120504/cl.csv" in printed
        assert "window    2008-05-19 to 2012-05-04, 1000 rows" in printed
        assert "long 98 rows, short 59, flat 843, 124 changes, first position 2008-07-18" in printed
        assert "Exploratory." in printed

    def test_it_prints_each_row_beside(self, printed) -> None:
        lines = printed.split("Before the book's window")
        for label, figures in (
            ("Momentum only", ["0.090228", "0.439049"]),
            ("Reversal only", ["0.068326", "0.370289"]),
            ("ComboOR", ["0.125917", "1.123042"]),
            ("The combination, the 2012-05-11 save", ["0.117226", "1.100045"]),
        ):
            assert _row(lines[0], label)[-2:] == figures

    def test_it_prints_the_segment_before_the_book_s_window(self, printed) -> None:
        before = printed.split("Before the book's window")[1]
        assert before.startswith(", 2004-05-24 to 2008-05-16, 998 rows")
        assert "inputdataohlcdaily_20120507/cl.csv" in before
        for label, figures in (
            ("The combination", ["0.021324", "0.369864"]),
            ("Momentum only", ["0.094589", "0.660514"]),
            ("Reversal only", ["-0.065694", "-0.359464"]),
        ):
            assert _row(before, label)[-2:] == figures
