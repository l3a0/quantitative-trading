"""The pins for crude oil reversal joined to momentum, *Algorithmic Trading* location 2701.

This file is the single authority for every number a prose surface quotes
about this replication and the rows beside it. The one exception is
``blog/crude-oil-reversal-momentum-lessons.md``:
``tests/test_cl_reversal_momentum_figures.py`` holds the numbers its figure
draws, and README lists what it says that nothing asserts. The post also
quotes what ``TestTheJoinIsHalfOfEachRule`` pins for it: that half of each
rule gives the join's position, how often the two rules agree, and each
rule's average day and standard deviation. ``TestWhatThePostQuotes`` reads
one copy of each run figure the post quotes, and its three tables, against
the run, and asserts each comparison the post's words draw.
``docs/replication-log.md`` Entry 31 carries the verdicts and points here row
by row.

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

import calendar
import io
import re
from contextlib import redirect_stdout
from pathlib import Path

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
from chan.cl_reversal_momentum_figures import cumulative
from chan.khandani_lo import TRADING_DAYS
from chan.khandani_lo_book_two import compounded_apr, matches
from chan.matlab_helpers import backshift
from chan.roll_returns import MONTH_LETTERS, OTHER_SAVES, SOURCE_FILES, load_strip
from chan.series import WindowCrossesScaleBreak, load_panel, scale_breaks
from chan.vintage import VintageUnavailable
from chan.vx_es import SCRIPT_SOURCE_FILE as VX_SCRIPT_SOURCE_FILE
from chan.vx_es import SOURCE_FILE as VX_SOURCE_FILE
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

    def test_the_later_save_takes_the_same_positions(self, cl, later_cl) -> None:
        """A uniform shift moves no comparison, so only each return's divisor changes."""
        assert (combination_positions(later_cl) == combination_positions(cl)).all()

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


def _half_of_each(rules: FourRules) -> np.ndarray:
    return (rules.momentum.positions + rules.reversal.positions) / 2


def _both_lags(closes: pd.Series) -> np.ndarray:
    return ~np.isnan(backshift(MOMENTUM_LOOKBACK, closes.to_numpy()))


def _mean_and_deviation(traded: Trades) -> tuple[float, float]:
    return round(traded.daily.mean(), 6), round(traded.daily.std(ddof=1), 6)


class TestTheJoinIsHalfOfEachRule:
    """Half a position in each rule is the join, outside rows where a lag is missing or tied.

    Where the two rules agree, half of each is their shared position, and the
    join holds it. Where they disagree, half of each sums to flat, and so does
    the join. A close that equals its lag leaves that rule flat while the
    other holds a position, so half of each is half a position and the join
    is flat. Off those rows the join earns the average of the two rules'
    daily returns, which is what the post's Lessons 2 and 3 rest on.
    """

    def test_on_the_book_s_window_it_differs_on_the_10_warm_up_rows_only(self, book) -> None:
        differ = book.combination.days[_half_of_each(book) != book.combination.positions]
        assert len(differ) == 10
        assert (differ[0], differ[-1]) == (pd.Timestamp("2008-07-01"), pd.Timestamp("2008-07-15"))

    def test_so_the_join_earns_the_average_of_the_two_rules(self, book) -> None:
        average = (book.momentum.daily + book.reversal.daily) / 2
        differ = book.combination.days[~np.isclose(average, book.combination.daily, atol=1e-15)]
        assert len(differ) == 10
        assert (differ[0], differ[-1]) == (pd.Timestamp("2008-07-02"), pd.Timestamp("2008-07-16"))

    def test_the_warm_up_shorts_put_the_join_below_the_plain_average(self, book) -> None:
        """On the 10 warm-up rows reversal alone is short, and the shorts earn on the
        days after, so the join's average day sits below the plain average of the two."""
        rows = _half_of_each(book) != book.combination.positions
        assert (book.reversal.positions[rows] == -1).all()
        earned = backshift(1, rows.astype(float)) == 1
        gain = float(book.reversal.daily[earned].sum())
        assert round(gain, 6) == 0.031552
        plain = (book.momentum.daily.mean() + book.reversal.daily.mean()) / 2
        assert plain - book.combination.daily.mean() == pytest.approx(
            gain / 2 / len(book.combination.daily)
        )

    def test_the_two_rules_agree_on_157_of_the_960_rows_both_lags_exist(self, cl, book) -> None:
        both = _both_lags(cl)
        agree = both & (book.momentum.positions == book.reversal.positions)
        assert (int(both.sum()), int(agree.sum()), int((both & ~agree).sum())) == (960, 157, 803)

    def test_where_they_disagree_their_positions_are_opposite(self, cl, book) -> None:
        disagree = _both_lags(cl) & (book.momentum.positions != book.reversal.positions)
        assert (book.momentum.positions[disagree] == -book.reversal.positions[disagree]).all()
        assert not book.combination.positions[disagree].any()

    def test_the_join_s_average_day_and_its_spread(self, book) -> None:
        assert _mean_and_deviation(book.combination) == (0.000463, 0.006687)
        assert _mean_and_deviation(book.momentum) == (0.000519, 0.018748)
        assert _mean_and_deviation(book.reversal) == (0.000440, 0.018864)

    def test_momentum_alone_earns_more_per_day_and_swings_far_more(self, book) -> None:
        """Momentum alone earns more per day, and each rule alone swings over 2.5 times as much."""
        assert book.momentum.daily.mean() > book.combination.daily.mean()
        assert book.combination.daily.std() < book.momentum.daily.std() / 2.5
        assert book.combination.daily.std() < book.reversal.daily.std() / 2.5

    def test_before_it_differs_on_the_warm_up_and_on_two_ties(self, before_cl, before) -> None:
        differ = before.combination.days[_half_of_each(before) != before.combination.positions]
        assert len(differ) == 12
        close = before_cl.to_numpy()
        ties = before_cl.index[close == backshift(MOMENTUM_LOOKBACK, close)]
        assert list(ties) == [pd.Timestamp("2005-06-15"), pd.Timestamp("2007-04-17")]
        assert set(ties) <= set(differ)
        assert not before.combination.positions[before_cl.index.isin(ties)].any()
        assert not (close == backshift(REVERSAL_LOOKBACK, close)).any()

    def test_before_the_two_rules_agree_on_162_of_958_rows(self, before_cl, before) -> None:
        """Of the 796 that do not agree, 794 are opposite and 2 are the ties."""
        both = _both_lags(before_cl)
        agree = both & (before.momentum.positions == before.reversal.positions)
        assert (int(both.sum()), int(agree.sum()), int((both & ~agree).sum())) == (958, 162, 796)
        opposite = both & (before.momentum.positions == -before.reversal.positions)
        assert int(opposite.sum()) == 794

    def test_before_the_average_day_and_its_spread(self, before) -> None:
        assert _mean_and_deviation(before.combination) == (0.000091, 0.003922)
        assert _mean_and_deviation(before.momentum) == (0.000406, 0.009765)
        assert _mean_and_deviation(before.reversal) == (-0.000222, 0.009792)


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

    @pytest.mark.parametrize(
        "values",
        [
            # The close ties the reversal lag while the momentum long holds.
            [10, 20, 20],
            # The close ties the reversal lag while the momentum short holds.
            [30, 20, 20],
            # The close ties the momentum lag while the reversal long holds.
            [20, 30, 20],
            # The close ties the momentum lag while the reversal short holds.
            [20, 10, 20],
        ],
    )
    def test_a_tie_leaves_the_combination_flat(self, values) -> None:
        assert combination_positions(self._series(values), reversal=1, momentum=2)[-1] == 0

    @pytest.mark.parametrize(
        ("values", "position"),
        [
            # A tie with one lag counts as neither side of that condition, so
            # the other condition alone decides.
            ([10, 20, 20], 1),
            ([30, 20, 20], -1),
            ([20, 30, 20], 1),
            ([20, 10, 20], -1),
        ],
    )
    def test_a_tie_counts_for_neither_side_of_combo_or(self, values, position) -> None:
        assert either_positions(self._series(values), reversal=1, momentum=2)[-1] == position

    def test_a_tie_with_a_lag_signals_nothing(self) -> None:
        closes = self._series([10, 10])
        assert momentum_positions(closes, lookback=1).tolist() == [0, 0]
        assert reversal_positions(closes, lookback=1).tolist() == [0, 0]

    def test_trade_earns_yesterday_s_position_on_today_s_move(self) -> None:
        closes = self._series([100, 110, 99])
        traded = trade(closes, np.array([1.0, -1.0, 0.0]))
        assert traded.daily[0] == 0
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

    def test_run_reads_every_save_from_the_directory_it_is_given(self, monkeypatch) -> None:
        """Each of the three reads, so no row is read from a vintage the caller did not name."""
        seen = []
        real = module.read_cl

        def record(source_file=SOURCE_FILE, *, start=None, end=None, data_dir=None):
            seen.append((source_file, data_dir))
            return real(source_file, start=start, end=end, data_dir=data_dir)

        monkeypatch.setattr(module, "read_cl", record)
        with redirect_stdout(io.StringIO()):
            run(paths.DATA_DIR)
        assert seen == [
            (SOURCE_FILE, paths.DATA_DIR),
            (LATER_SOURCE_FILE, paths.DATA_DIR),
            (EARLIER_SOURCE_FILE, paths.DATA_DIR),
        ]

    def test_run_returns_the_specification_s_four_rules(self) -> None:
        with redirect_stdout(io.StringIO()):
            result = run()
        assert _six(result.combination) == (0.117600, 1.100368)
        assert _six(result.momentum) == (0.090228, 0.439049)

    def test_main_lets_any_other_error_through(self, monkeypatch, no_arguments) -> None:
        def broken(*_a, **_k):
            raise ValueError("a programming error keeps its traceback")

        monkeypatch.setattr(module, "run", broken)
        with pytest.raises(ValueError, match="keeps its traceback"):
            main()

    def test_main_refuses_an_argument(self, monkeypatch) -> None:
        monkeypatch.setattr("sys.argv", ["chan.cl_reversal_momentum", "--bogus"])
        with pytest.raises(SystemExit) as refused:
            main()
        assert refused.value.code == 2

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
        assert module._verdict(0.117700, SCRIPT_APR) == "gap +0.0001"


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
        assert printed.startswith(
            "Crude oil reversal joined to momentum, Algorithmic Trading location 2701"
        )
        assert "Rows beside it. None carries a verdict." in printed
        assert "Annualised over 252 days with no cost, flat rows included." in printed

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


POST = Path(__file__).parents[1] / "blog" / "crude-oil-reversal-momentum-lessons.md"
SPELLED = {2: "two", 10: "ten"}
#: A number cell in one of the post's ``math`` tables: a signed decimal, a date or an integer.
CELL = re.compile(r"-?\d+\.\d+|\d{4}-\d{2}-\d{2}|\d+")
#: Crude oil's 2008 peak as the post dates it, from the book through the gold miners post.
#: It is Chan's date and is not derived here, so the post's copy of it is not read.
CRUDE_PEAK = pd.Timestamp("2008-07-14")


def _saved(source_file: str) -> str:
    """The date a save is named by, from its file name, as the post writes it."""
    stamp = re.search(r"_(\d{8})\.mat$", source_file).group(1)
    return f"{stamp[:4]}-{stamp[4:6]}-{stamp[6:]}"


def _minus(x: float, places: int) -> str:
    """``x`` at ``places`` decimals with a true minus sign, as the post's prose prints it."""
    return f"{x:.{places}f}".replace("-", "−")


def _pct(x: float) -> str:
    """A cumulative return as the post's prose and alt text print it, one decimal, true minus."""
    return _minus(100 * x, 1)


def _about(x: float) -> str:
    """A cumulative return the alt text reads as "about", to the nearest whole percent."""
    return _minus(round(100 * x), 0)


def _day(stamp: pd.Timestamp) -> str:
    return f"{stamp:%B} {stamp.day}, {stamp.year}"


@pytest.fixture(scope="module")
def text() -> str:
    return POST.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def strips() -> list[pd.DataFrame]:
    """Chan's two CL strips, read through the one read path for single contracts."""
    return [
        load_strip("CL", source_file=f).contracts for f in (SOURCE_FILES["CL"], *OTHER_SAVES["CL"])
    ]


class TestWhatThePostQuotes:
    """One copy of each figure the post quotes, read against the run.

    The classes above pin each figure once, and
    ``blog/crude-oil-reversal-momentum-lessons.md`` copies it by hand. Here
    each figure is built from the run at the precision the post prints it and
    looked for in one copy: a short fragment holding the number and the few
    words that name one place in the post. A typo in that copy, or a re-pin
    that leaves the post behind, fails here. Each of the three tables
    is read as the multiset of its number cells, so a cell changed, added or
    dropped fails whichever way the table is laid out. Each comparison the
    post's words draw on the run, such as "a little over a third", "about 40
    percent", "under a quarter", "most of that gain" and "for most of the
    period", is asserted on the run, and one copy of its words is read.

    Three reads beside the run supply the rest.

    1. The figure's curves through
       :func:`chan.cl_reversal_momentum_figures.cumulative`, for the alt text
       and the paragraph after the chart.
       ``tests/test_cl_reversal_momentum_figures.py`` pins the same curves.
    2. Chan's two CL strips through :func:`chan.roll_returns.load_strip`, for
       the January 2007 contract both start with, and for the close of the
       contract nearest delivery on the window's first day.
       ``tests/test_roll_returns.py`` pins the same first contract.
    3. The file names of the two VX and ES saves in :mod:`chan.vx_es`, for
       "ten days apart". ``tests/test_vx_es.py`` pins the APR falling by more
       than half between them, and this class does not read that run.

    "Two months before" is asserted against crude oil's peak on July 14,
    2008, a date the post takes from the book and this class does not read.
    The post states several figures more than once, and the other copies are
    not read, so a typo in one of them passes. Chan's words, the Kindle
    locations, the book's year, the EIA's $41.51 and its year, the year in
    another post's link text, the mirror's commit and the references stay
    unpinned.
    """

    @staticmethod
    def missing(text: str, fragments: list[str]) -> list[str]:
        return [fragment for fragment in fragments if fragment not in text]

    @staticmethod
    def tables(text: str) -> list[list[str]]:
        """Each ``math`` block's number cells, sorted, in the order the blocks appear.

        ``\\small`` and each array's column spec are dropped first, so neither
        the font size nor the layout of a header can add a number.
        """
        blocks = re.findall(r"```math\n(.*?)```", text, flags=re.S)
        return [
            sorted(CELL.findall(re.sub(r"\\small|\\begin\{array\}\{[^}]*\}", "", block)))
            for block in blocks
        ]

    def test_the_post_holds_three_tables(self, text) -> None:
        assert len(self.tables(text)) == 3

    def test_the_opening_and_the_file(self, cl, book, later_cl, before_cl, strips, text) -> None:
        saved = pd.Timestamp(_saved(SOURCE_FILE))
        assert (pd.Timestamp(_saved(LATER_SOURCE_FILE)) - saved).days == 7, "a week later"
        assert round((BOOK_START - before_cl.index[0]).days / 365.25) == 4, "four years"
        assert round((CRUDE_PEAK - cl.index[0]).days / (365.25 / 12)) == 2, "two months before"
        # Each strip's contracts sit in delivery order, so the first with a close that day
        # is the one nearest delivery.
        nearest = {float(s.loc[cl.index[0]].dropna().iloc[0]) for s in strips}
        assert len(nearest) == 1, "both strips agree on the contract nearest delivery"
        (near,) = nearest
        assert near < cl.iloc[0], "well above the price that traded"
        fragments = [
            f"reports a {BOOK_APR_PERCENT} percent APR and a Sharpe ratio of {BOOK_SHARPE}. "
            "Both land.",
            f"It buys at the close when the price is below its close {REVERSAL_LOOKBACK} trading "
            f"days earlier and above its close {MOMENTUM_LOOKBACK} trading days earlier. It "
            f"shorts when the price is above its close {REVERSAL_LOOKBACK} trading days earlier "
            f"and below its close {MOMENTUM_LOOKBACK} trading days earlier",
            f"He reports “The APR is {BOOK_APR_PERCENT} percent, with a Sharpe ratio of "
            f"{BOOK_SHARPE}.”",
            f"names by the date in its file name, here {_saved(SOURCE_FILE)}.",
            f"The script runs the rule over the save’s {len(cl):,} trading days of CL, and a "
            f"comment under its print line records `APR={SCRIPT_APR} Sharpe={SCRIPT_SHARPE}`.",
            f"a save dated a week later still prints as {BOOK_APR_PERCENT} percent and "
            f"{BOOK_SHARPE}.",
            f"reruns the rule he chose, on the {BOOK_START.year} to {BOOK_END.year} data his "
            f"script reads",
            f"Nothing shows Chan fixed the {REVERSAL_LOOKBACK} and {MOMENTUM_LOOKBACK} days",
            f"The {REVERSAL_LOOKBACK}-day lag on a given day is the close {REVERSAL_LOOKBACK} "
            "trading days before it.",
            f"buys when the close is below its {REVERSAL_LOOKBACK}-day lag, because",
            f"buys when the close is above its {MOMENTUM_LOOKBACK}-day lag, because",
            f"The join buys when the close is below its {REVERSAL_LOOKBACK}-day lag and above "
            f"its {MOMENTUM_LOOKBACK}-day lag",
            f"scores a long on any day the close is below its {REVERSAL_LOOKBACK}-day lag or "
            f"above its {MOMENTUM_LOOKBACK}-day lag. It scores a short on any day the close is "
            f"above its {REVERSAL_LOOKBACK}-day lag or below its {MOMENTUM_LOOKBACK}-day lag.",
            f"`prod(1 + r)^({TRADING_DAYS}/n) − 1`",
            f"multiplying by √{TRADING_DAYS}.",
            f"The book’s window opens at {cl.iloc[0]:.2f} on {cl.index[0].date()}, a day the "
            f"contract nearest delivery closed at {near:.2f}. That is two months before",
            f"**The {_saved(SOURCE_FILE)} save**, the one `CL_rev.m` loads. CL holds "
            f"{len(cl):,} rows, from {BOOK_START.date()} to {BOOK_END.date()}.",
            f"**The {_saved(LATER_SOURCE_FILE)} save**, read over the same {len(later_cl):,} days.",
            f"**The {_saved(EARLIER_SOURCE_FILE)} save**, whose CL closes equal the first save’s "
            f"on all {len(cl):,} of the book’s days. Its {len(before_cl):,} earlier rows, from "
            f"{before_cl.index[0].date()} to {before_cl.index[-1].date()}, extend",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_1(self, cl, book, later_cl, text) -> None:
        spec = book.combination
        later = trade(later_cl, combination_positions(later_cl))
        _, same = read_cl(EARLIER_SOURCE_FILE, start=BOOK_START, end=BOOK_END)
        shift = round(float(np.mean(later_cl.to_numpy() - cl.to_numpy())), 2)
        assert np.allclose(later_cl.to_numpy() - cl.to_numpy(), shift), "on every one"
        assert _six(trade(same, combination_positions(same))) == _six(spec), "to six decimals"
        cells = [
            _saved(SOURCE_FILE),
            f"{spec.apr:.6f}",
            f"{spec.sharpe:.6f}",
            SCRIPT_APR,
            SCRIPT_SHARPE,
            BOOK_APR_PERCENT,
            BOOK_SHARPE,
            _saved(LATER_SOURCE_FILE),
            f"{later.apr:.6f}",
            f"{later.sharpe:.6f}",
        ]
        assert self.tables(text)[0] == sorted(cells)
        apart = (
            pd.Timestamp(_saved(VX_SCRIPT_SOURCE_FILE)) - pd.Timestamp(_saved(VX_SOURCE_FILE))
        ).days
        fragments = [
            f"Here is the join on the {_saved(SOURCE_FILE)} and {_saved(LATER_SOURCE_FILE)} saves",
            f"The {_saved(EARLIER_SOURCE_FILE)} save gives the same two figures to six decimals",
            f"Its closes sit {shift:.2f} higher on every one of the {len(cl):,} days.",
            f"the APR falls to {later.apr:.6f} and the Sharpe ratio to {later.sharpe:.6f}. "
            f"Both still round to {BOOK_APR_PERCENT} percent and {BOOK_SHARPE}",
            f"The script’s comment matches the {_saved(SOURCE_FILE)} save",
            f"between two of Chan’s saves whose names are {SPELLED[apart]} days apart.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_2_s_table_and_arithmetic(self, cl, book, text) -> None:
        j, m, r = book.combination, book.momentum, book.reversal
        cells = []
        for rule in (j, m, r):
            mean, deviation = _mean_and_deviation(rule)
            cells += [f"{mean:.6f}", f"{deviation:.6f}", f"{rule.apr:.6f}", f"{rule.sharpe:.6f}"]
        assert self.tables(text)[1] == sorted(cells)
        for alone in (m, r):
            assert j.apr > alone.apr and j.sharpe > alone.sharpe, "each rule alone scores below"
        assert m.daily.mean() > j.daily.mean(), "momentum alone earns more on an average day"

        early = book.combination.days[_half_of_each(book) != j.positions]
        rows = cl.index.isin(early)
        close = cl.to_numpy()
        assert not np.isnan(backshift(REVERSAL_LOOKBACK, close))[rows].any(), "the 30-day lag"
        assert np.isnan(backshift(MOMENTUM_LOOKBACK, close))[rows].all(), "no 40-day lag yet"
        assert (r.positions[rows] == -1).all(), "reversal alone held shorts on every one"
        follow = backshift(1, rows.astype(float)) == 1
        assert float(r.daily[follow].sum()) > 0, "that made money"
        average = (m.daily + r.daily) / 2
        assert (~np.isclose(average, j.daily, atol=1e-15) == follow).all(), "the ten that follow"

        both = _both_lags(cl)
        agree = int((both & (m.positions == r.positions)).sum())
        opposite = int((both & (m.positions == -r.positions)).sum())
        assert opposite > agree, "the two rules mostly disagree"
        held = int((j.positions != 0).sum())
        before_both = int((~both).sum())
        assert not both[:before_both].any() and both[before_both:].all(), "the first rows"
        assert len(j.positions) - held == opposite + before_both, "the 803 and the first 40"
        means = {name: rule.daily.mean() for name, rule in (("j", j), ("m", m), ("r", r))}
        deviations = {name: rule.daily.std(ddof=1) for name, rule in (("j", j), ("m", m), ("r", r))}
        assert means["r"] < means["j"] < means["m"], "sits between"
        assert means["j"] < (means["m"] + means["r"]) / 2, "slightly below the plain average"
        for alone in ("m", "r"):
            assert 1 / 3 < deviations["j"] / deviations[alone] < 0.4, "a little over a third"
        fragments = [
            f"So half of each rule gives the join’s position on every row but "
            f"{SPELLED[len(early)]}. Those {SPELLED[len(early)]}, from {early[0].date()} to "
            f"{early[-1].date()}, come early in the run, when the {REVERSAL_LOOKBACK}-day lag "
            f"exists and the {MOMENTUM_LOOKBACK}-day lag does not yet",
            f"So on every day except the day after each of those {SPELLED[int(follow.sum())]} rows",
            f"Of the {int(both.sum())} rows where both lags exist, they agree on {agree} and take "
            f"opposite sides on {opposite}. On the day after each of those {opposite} rows",
            f"The join holds a position on {held} of the {len(j.positions):,} rows, long on "
            f"{int((j.positions > 0).sum())} and short on {int((j.positions < 0).sum())}. "
            f"It is flat on the other {len(j.positions) - held}, which are the {opposite} rows "
            f"where the rules take opposite sides and the first {before_both} rows, before the "
            f"{MOMENTUM_LOOKBACK}-day lag exists.",
            f"The join’s average day, {means['j']:.6f}, sits between reversal’s "
            f"{means['r']:.6f} and momentum’s {means['m']:.6f}.",
            f"because on those {SPELLED[len(early)]} early days reversal alone held shorts that "
            "made money",
            f"Cancelling {opposite} days of opposite bets gives a standard deviation of "
            f"{deviations['j']:.6f}, a little over a third of either rule’s.",
        ]
        assert self.missing(text, fragments) == []

    def test_what_the_swings_cost(self, book, before, text) -> None:
        j = book.combination
        for alone in (book.momentum, book.reversal):
            assert j.apr > alone.apr and j.sharpe > alone.sharpe, "the highest of the three"
        move = 2
        down, up = 1 - move / 100, 1 + move / 100
        assert round(down * up, 4) < 1, "a small loss"
        fragments = [
            "Smaller swings give the join the highest APR of the three as well as the highest "
            "Sharpe ratio",
            f"A day that loses {move} percent followed by one that gains {move} percent leaves "
            f"{down:.2f} × {up:.2f} = {down * up:.4f} of the capital",
        ]
        assert self.missing(text, fragments) == []

    def test_the_chart_s_curves_and_alt_text(self, book, before, text) -> None:
        names = ("combination", "momentum", "reversal")
        up = {name: cumulative(getattr(book, name)) for name in names}
        down = {name: cumulative(getattr(before, name)) for name in names}
        peak, trough = up["momentum"], up["reversal"]
        assert peak.max() - peak.iloc[-1] > peak.max() / 2, "gave back most of that gain"
        assert up["combination"].iloc[-1] > max(peak.iloc[-1], trough.iloc[-1]), "ends highest"
        first_year = up["combination"][: str(BOOK_START.year)]
        assert first_year.abs().max() < 0.05, "within a few percent of zero through 2008"
        assert (down["combination"] < 0).mean() > 0.5, "below zero for most of the period"
        # "Until late 2007": through September, before momentum's climb begins in October.
        wander = down["momentum"][:"2007-09-30"]
        first, last = before.combination.days[[0, -1]]
        fragments = [
            f"The upper chart covers the book’s window, {BOOK_START:%B %Y} to {BOOK_END:%B %Y}.",
            f"Momentum alone climbs to {_pct(peak.max())} percent by {_day(peak.idxmax())}, then "
            f"drifts down to end at {_pct(peak.iloc[-1])} percent.",
            f"Reversal alone falls to {_pct(trough.min())} percent by {_day(trough.idxmin())}, "
            f"then climbs back to end at {_pct(trough.iloc[-1])} percent.",
            f"stays within a few percent of zero through {BOOK_START.year}, never falls below "
            f"{_pct(up['combination'].min())} percent, and ends highest of the three at "
            f"{_pct(up['combination'].iloc[-1])} percent.",
            f"The lower chart covers {first:%B %Y} to {last:%B %Y}.",
            f"Momentum alone wanders between about {_about(wander.min())} and "
            f"{_about(wander.max())} percent until late 2007, then climbs to end at "
            f"{_pct(down['momentum'].iloc[-1])} percent.",
            f"Reversal alone drifts down to about {_about(down['reversal'].min())} percent and "
            f"ends at {_pct(down['reversal'].iloc[-1])} percent.",
            f"as low as about {_about(down['combination'].min())} percent, and ends at "
            f"{_pct(down['combination'].iloc[-1])} percent.",
            f"Above, the book’s {len(book.combination.days):,} rows on the save the script loads. "
            f"Below, the {len(before.combination.days):,} rows before them on the "
            f"{_saved(EARLIER_SOURCE_FILE)} save.",
            f"Momentum alone rose {_pct(peak.max())} percent and then gave back most of that "
            f"gain, ending at {_pct(peak.iloc[-1])} percent. Reversal alone fell "
            f"{_pct(-trough.min())} percent before recovering to {_pct(trough.iloc[-1])} percent.",
            f"the join never lost more than {_pct(-up['combination'].min())} percent from its "
            f"start, and finished at {_pct(up['combination'].iloc[-1])} percent.",
        ]
        assert self.missing(text, fragments) == []

    def test_swapped_lags_and_combo_or(self, cl, book, text) -> None:
        swapped_positions = combination_positions(
            cl, reversal=MOMENTUM_LOOKBACK, momentum=REVERSAL_LOOKBACK
        )
        assert (swapped_positions == -book.combination.positions).all(), "every long a short"
        swapped = trade(cl, swapped_positions)
        assert round(swapped.sharpe, 6) == -round(book.combination.sharpe, 6), "flips exactly"
        assert round(swapped.apr, 6) != -round(book.combination.apr, 6), "not quite"
        close = cl.to_numpy()
        for lookback in (REVERSAL_LOOKBACK, MOMENTUM_LOOKBACK):
            assert not (close == backshift(lookback, close)).any(), "no close equals its lag"
        rows = book.combination.positions != book.either.positions
        assert (book.either.positions[rows] == book.reversal.positions[rows]).all()
        fragments = [
            f"With reversal on the {MOMENTUM_LOOKBACK}-day lag and momentum on the "
            f"{REVERSAL_LOOKBACK}-day lag, a buy needs the close below the {MOMENTUM_LOOKBACK}-day "
            f"lag and above the {REVERSAL_LOOKBACK}-day lag",
            f"The Sharpe ratio flips sign exactly, to {_minus(swapped.sharpe, 6)}, and the APR "
            f"becomes {_minus(swapped.apr, 6)}, not quite the negative of "
            f"{book.combination.apr:.6f}",
            f"On the book’s window no close equals its {REVERSAL_LOOKBACK}-day or "
            f"{MOMENTUM_LOOKBACK}-day lag exactly",
            f"So it matches the join everywhere except the same {SPELLED[int(rows.sum())]} early "
            "rows, where it trades reversal alone.",
            f"Its APR of {book.either.apr:.6f} and Sharpe ratio of {book.either.sharpe:.6f} "
            f"differ from the join’s only through those {SPELLED[int(rows.sum())]} rows.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_3(self, before_cl, before, text) -> None:
        j, m, r = before.combination, before.momentum, before.reversal
        cells = []
        for rule in (j, m, r):
            mean, deviation = _mean_and_deviation(rule)
            cells += [f"{mean:.6f}", f"{deviation:.6f}", f"{rule.apr:.6f}", f"{rule.sharpe:.6f}"]
        assert self.tables(text)[2] == sorted(cells)
        assert m.apr > j.apr and m.sharpe > j.sharpe, "momentum alone beats the join"
        assert r.apr < 0, "reversal alone loses money"

        differ = before.combination.days[_half_of_each(before) != j.positions]
        close = before_cl.to_numpy()
        ties = before_cl.index[close == backshift(MOMENTUM_LOOKBACK, close)]
        early = differ[~differ.isin(ties)]
        at_early = before_cl.index.isin(early)
        assert np.isnan(backshift(MOMENTUM_LOOKBACK, close))[at_early].all(), "only the 30-day"
        assert not np.isnan(backshift(REVERSAL_LOOKBACK, close))[at_early].any(), "lag exists"
        at_ties = before_cl.index.isin(ties)
        assert not m.positions[at_ties].any() and r.positions[at_ties].all(), "a tie"
        both = _both_lags(before_cl)
        agree = int((both & (m.positions == r.positions)).sum())
        opposite = int((both & (m.positions == -r.positions)).sum())
        assert int(both.sum()) - agree - opposite == len(ties), "the other two are the ties"
        plain = (m.daily.mean() + r.daily.mean()) / 2
        assert abs(j.daily.mean() - plain) < 0.02 * plain, "near the plain average"
        assert j.daily.mean() / m.daily.mean() < 1 / 4, "under a quarter"
        deviation_ratio = j.daily.std(ddof=1) / m.daily.std(ddof=1)
        fragments = [
            f"The {_saved(EARLIER_SOURCE_FILE)} save holds the same series back to "
            f"{before_cl.index[0].date()}. Its {len(before_cl):,} rows before the book’s window",
            f"Half of each rule gives the join’s position on all but {len(differ)} of these rows. "
            f"{SPELLED[len(early)].capitalize()} are again the early rows where only the "
            f"{REVERSAL_LOOKBACK}-day lag exists, here from {early[0].date()} to "
            f"{early[-1].date()}. The other {SPELLED[len(ties)]}, {ties[0].date()} and "
            f"{ties[1].date()}, are days when the close equals its {MOMENTUM_LOOKBACK}-day lag "
            "exactly",
            f"Of the {int(both.sum())} rows where both lags exist, the two rules agree on "
            f"{agree} and take opposite sides on {opposite}. The other "
            f"{SPELLED[len(ties)]} are those tie days.",
            f"Its average day is {j.daily.mean():.6f}, near the plain average of a rule that "
            f"earns {m.daily.mean():.6f} a day and one that loses {-r.daily.mean():.6f}.",
            f"Its standard deviation is about {round(100 * deviation_ratio, -1):.0f} percent of "
            "momentum’s, but its average day is under a quarter of momentum’s, and its Sharpe "
            f"ratio falls to {j.sharpe:.2f} against momentum’s {m.sharpe:.2f}.",
            f"The series closes at {before_cl.iloc[0]:.2f} on {before_cl.index[0].date()}",
        ]
        assert self.missing(text, fragments) == []

    def test_what_this_replication_cannot_say(self, book, before_cl, strips, text) -> None:
        firsts = {contracts.columns[0] for contracts in strips}
        assert len(firsts) == 1, "both strips start with the same contract"
        root, code = next(iter(firsts)).split("-")
        year, month = int(code[:4]), calendar.month_name[MONTH_LETTERS.index(code[4]) + 1]
        # The contract before it stops trading about a month before its own last day, so
        # the nearest contract is missing until then.
        last = strips[0][f"{root}-{code}"].last_valid_index()
        missing = before_cl.index < last - pd.DateOffset(months=1)
        assert missing.mean() > 0.5, "for most of those four years"
        fragments = [
            f"the book names {REVERSAL_LOOKBACK} and {MOMENTUM_LOOKBACK} days and says nothing",
            f"The join changes position {book.combination.changes} times in "
            f"{len(book.combination.daily):,} days, and nothing here measures what a cost on "
            f"each change would take from {BOOK_APR_PERCENT} percent.",
            f"start with the contract delivering in {month} {year}, so for most of those four "
            "years they lack the contract nearest delivery.",
        ]
        assert self.missing(text, fragments) == []
