"""Example 7.1, Conditional Parameter Optimization, against the readings declared on issue 23.

Two kinds of test live here.

1. **The mechanics**, on synthetic data, run everywhere. Each vectorised step is
   held against a literal loop that reads like the book's rule, so a fast
   implementation that drifts from the rule fails here.
2. **The pins**, on the owner's archive of Alpha Vantage minute bars. A public
   clone has no archive, and the full run takes minutes, so these skip unless
   an archive is configured and ``QT_ARCHIVE_RUN=1`` asks for them. The skip
   reason says which of the two is missing. ``.claude/settings.json`` sets the
   flag for every Claude Code session here.

Every pinned figure names its vintages, the two archive files by their sha256
in ``data/archive_vintages.jsonl``, and its specification, the readings
declared on issue 23 before any number was computed.

``blog/conditional-parameter-optimization-lessons.md`` quotes these pins, and
two classes at the end of this file read the post itself, one copy of each
figure: ``TestThePostQuotesWhatEveryCloneComputes`` for what needs no bars, and
``TestThePostQuotesTheRun`` for the run's figures. The chart's own labels are
held by ``tests/test_cpo_figures.py``, and the two sketches' by
``tests/test_cpo_whiteboard.py``. What the post says that nothing here
asserts is listed in README's ``## The write-up``.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy.stats import spearmanr

from chan import cpo
from chan.archive import read_archive_manifest
from chan.cpo import (
    EXIT_FRACTION,
    Cell,
    cells,
    claim_holds,
    conditional_choices,
    costed,
    day_bounds,
    design_rows,
    ema_var,
    metrics,
    minute_grid,
    positions,
    regular_session,
    round_trips,
    train_days,
    unconditional_cell,
    zscore,
)
from tests.conftest import archive_skip_reason

#: The seeds the model was refit with after the result was seen, the ones the
#: claim holds for, and the range of the re-chosen Sharpe ratio across them.
#: ``test_the_claim_holds_for_2_of_10_seeds`` pins them, and the post quotes them.
SEEDS_TRIED = 10
SEEDS_THE_CLAIM_HOLDS_FOR = (2, 7)
SEED_SHARPE_RANGE = (5.166, 6.353)
#: How many of the ten seeds make re-choosing beat holding on each metric.
SEED_WINS = {"cumulative": 2, "annual": 2, "sharpe": 3, "calmar": 6}

# --- literal readings of the rules, the references the fast code is held to ---


def literal_ema_var(spread):
    """The endnote, one line per equation."""
    alpha = 2.0 / LOOKBACK
    ema = [spread[0]]
    var = [math.nan]
    for t in range(1, len(spread)):
        ema.append(alpha * spread[t] + (1 - alpha) * ema[t - 1])
        if t == 1:
            var.append((spread[1] - spread[0]) ** 2)
        else:
            var.append(alpha * (spread[t] - ema[t]) ** 2 + (1 - alpha) * var[t - 1])
    return np.array(ema), np.array(var)


LOOKBACK = 30


def literal_positions(z, entry, first):
    """Rules a to d, exits before entries, flat at each day's start, NaN fires nothing."""
    exit_threshold = EXIT_FRACTION * entry
    state = 0
    out = []
    for t, value in enumerate(z):
        if first[t]:
            state = 0
        if not math.isnan(value):
            if state == 1 and value > exit_threshold:
                state = 0
            if state == -1 and value < -exit_threshold:
                state = 0
            if value < -entry:
                state = 1
            elif value > entry:
                state = -1
        out.append(state)
    return np.array(out, dtype=np.int8)


def literal_round_trips(held, price, first, last, n_days, codes):
    """Walk each day, opening a trip on a change to a side and closing it on the next change."""
    total = np.zeros(n_days)
    count = np.zeros(n_days, dtype=np.int64)
    side = 0
    entry_price = math.nan
    for t in range(len(held)):
        if first[t]:
            side = 0
        if side != 0 and held[t] != side:
            total[codes[t]] += side * (price[t] / entry_price - 1)
            count[codes[t]] += 1
            side = 0
        if side == 0 and held[t] != 0 and not last[t]:
            side = int(held[t])
            entry_price = price[t]
        if last[t] and side != 0:
            total[codes[t]] += side * (price[t] / entry_price - 1)
            count[codes[t]] += 1
            side = 0
    return total, count


def random_days(rng, n_days=40, per_day=60):
    first = np.zeros(n_days * per_day, dtype=bool)
    first[::per_day] = True
    last = np.zeros_like(first)
    last[per_day - 1 :: per_day] = True
    codes = np.repeat(np.arange(n_days), per_day)
    return first, last, codes


# --- the grid ---


class TestTheGrid:
    def test_four_hundred_cells_in_the_declared_tie_order(self):
        grid = cells()
        assert len(grid) == 400
        assert grid[0] == Cell(2.0, 0.2, 30)
        assert grid[1] == Cell(2.0, 0.2, 60)
        assert grid[8] == Cell(2.0, 0.3, 30)
        assert grid[-1] == Cell(4.0, 2.5, 720)

    def test_the_entry_grid_reads_the_printed_2_2_5_as_2_and_2_5(self):
        assert cpo.ENTRY_THRESHOLDS[-2:] == (2.0, 2.5)
        assert len(set(cpo.ENTRY_THRESHOLDS)) == 10

    def test_a_cell_spells_itself_as_chan_s_output_does(self):
        """p. 145 prints `2.5_30_0.2`: weight, lookback, entry."""
        assert Cell(2.5, 0.2, 30).label == "2.5_30_0.2"


# --- the bars ---


class TestTheBars:
    def test_the_regular_session_is_0930_to_1559_by_opening_minute(self):
        index = pd.to_datetime(
            ["2006-06-01 09:29", "2006-06-01 09:30", "2006-06-01 15:59", "2006-06-01 16:00"]
        )
        bars = pd.DataFrame({"close": [1.0, 2.0, 3.0, 4.0]}, index=index)
        assert list(regular_session(bars)["close"]) == [2.0, 3.0]

    def test_an_early_close_ends_the_session_at_1259(self):
        """2019-11-29 closed at 13:00.

        Its 13:00 bar holds the closing auction's print, and the bars after it are
        extended hours.
        """
        index = pd.to_datetime(
            ["2019-11-29 12:59", "2019-11-29 13:00", "2019-11-29 14:57", "2019-12-02 15:59"]
        )
        bars = pd.DataFrame({"close": [1.0, 2.0, 3.0, 4.0]}, index=index)
        assert list(regular_session(bars)["close"]) == [1.0, 4.0]

    def test_the_early_closes_are_thirty_four_days_at_one_a_year_or_more(self):
        assert len(cpo.EARLY_CLOSES) == 34
        assert {day[:4] for day in cpo.EARLY_CLOSES} == {str(y) for y in range(2006, 2021)}

    def test_the_span_ends_on_2020_12_31(self):
        index = pd.to_datetime(["2020-12-31 15:59", "2021-01-04 09:30"])
        bars = pd.DataFrame({"close": [1.0, 2.0]}, index=index)
        assert len(regular_session(bars)) == 1

    def test_a_close_carries_forward_within_a_day_and_never_across_a_night(self):
        gld = pd.Series(
            [100.0, 101.0, 102.0],
            index=pd.to_datetime(["2006-06-01 09:30", "2006-06-01 09:32", "2006-06-02 09:31"]),
        )
        gdx = pd.Series(
            [30.0, 31.0],
            index=pd.to_datetime(["2006-06-01 09:31", "2006-06-02 09:30"]),
        )
        grid = minute_grid(gld, gdx)
        # Day one: 09:30 has no GDX yet, so it is dropped. 09:31 carries GLD's
        # 100 forward, and 09:32 carries GDX's 30 forward.
        # Day two: 09:30 has no GLD yet, so it is dropped rather than taking
        # day one's last GLD close.
        assert grid.index.strftime("%m-%d %H:%M").tolist() == [
            "06-01 09:31",
            "06-01 09:32",
            "06-02 09:31",
        ]
        assert grid["gld"].tolist() == [100.0, 101.0, 102.0]
        assert grid["gdx"].tolist() == [30.0, 30.0, 31.0]

    def test_a_day_only_one_symbol_traded_is_left_out(self):
        gld = pd.Series(
            [100.0, 101.0], index=pd.to_datetime(["2006-06-01 09:30", "2006-06-02 09:30"])
        )
        gdx = pd.Series([30.0], index=pd.to_datetime(["2006-06-02 09:30"]))
        assert minute_grid(gld, gdx).index.normalize().unique().strftime("%m-%d").tolist() == [
            "06-02"
        ]

    def test_day_bounds_mark_each_day_s_first_and_last_minute(self):
        index = pd.to_datetime(["2006-06-01 09:30", "2006-06-01 09:31", "2006-06-02 09:30"])
        first, last, codes, days = day_bounds(index)
        assert first.tolist() == [True, False, True]
        assert last.tolist() == [False, True, True]
        assert codes.tolist() == [0, 0, 1]
        assert len(days) == 2


# --- the strategy ---


class TestTheRecursions:
    def test_ema_and_var_follow_the_endnote_line_for_line(self):
        spread = np.random.default_rng(1).normal(0, 1, 500).cumsum()
        ema, var = ema_var(spread, LOOKBACK)
        expected_ema, expected_var = literal_ema_var(spread)
        np.testing.assert_allclose(ema, expected_ema, rtol=1e-12, atol=1e-12)
        assert math.isnan(var[0])
        np.testing.assert_allclose(var[1:], expected_var[1:], rtol=1e-10)

    def test_the_first_variance_is_the_squared_first_step(self):
        _, var = ema_var(np.array([1.0, 3.0, 2.0]), LOOKBACK)
        assert var[1] == 4.0

    def test_a_zero_variance_leaves_the_z_score_undefined(self):
        z = zscore(np.ones(10), LOOKBACK)
        assert np.isnan(z).all()


class TestTheRules:
    @pytest.mark.parametrize("entry", cpo.ENTRY_THRESHOLDS)
    def test_the_fast_rules_match_a_literal_loop(self, entry):
        rng = np.random.default_rng(int(entry * 100))
        first, _, _ = random_days(rng)
        z = rng.normal(0, 1.4, len(first))
        z[rng.random(len(z)) < 0.03] = np.nan
        np.testing.assert_array_equal(
            positions(z, entry, first), literal_positions(z, entry, first)
        )

    def test_a_long_flips_short_on_one_close(self):
        """Exits before entries: the long exits and the short entry fires on the same minute."""
        first = np.array([True, False, False])
        assert positions(np.array([-1.5, -0.8, 1.5]), 1.0, first).tolist() == [1, 1, -1]

    def test_each_band_does_what_the_rules_say(self):
        entry = 1.0
        first = np.zeros(7, dtype=bool)
        first[0] = True
        # long, held in the short-exit band, flat in the long-exit band, held
        # flat, short, held in the long-exit band, flat in the middle
        z = np.array([-1.2, -0.7, 0.7, -0.7, 1.2, 0.7, 0.1])
        assert positions(z, entry, first).tolist() == [1, 1, 0, 0, -1, -1, 0]

    def test_every_day_starts_flat(self):
        first = np.array([True, False, True, False])
        assert positions(np.array([-2.0, -2.0, -0.7, -0.7]), 1.0, first).tolist() == [1, 1, 0, 0]

    def test_a_nan_fires_no_rule(self):
        first = np.array([True, False, False])
        assert positions(np.array([-2.0, np.nan, np.nan]), 1.0, first).tolist() == [1, 1, 1]


class TestTheRoundTrips:
    def test_the_fast_trips_match_a_literal_walk(self):
        rng = np.random.default_rng(7)
        first, last, codes = random_days(rng)
        price = 100 * np.exp(rng.normal(0, 0.001, len(first)).cumsum())
        held = positions(rng.normal(0, 1.4, len(first)), 0.7, first)
        total, count = round_trips(held, price, first, last, codes, codes.max() + 1)
        expected_total, expected_count = literal_round_trips(
            held, price, first, last, codes.max() + 1, codes
        )
        np.testing.assert_allclose(total, expected_total, rtol=1e-12, atol=1e-15)
        np.testing.assert_array_equal(count, expected_count)

    def test_a_trip_runs_from_its_first_close_to_the_close_after_its_last(self):
        first = np.array([True, False, False, False])
        last = np.array([False, False, False, True])
        held = np.array([1, 1, 0, 0], dtype=np.int8)
        price = np.array([100.0, 101.0, 103.0, 99.0])
        total, count = round_trips(held, price, first, last, np.zeros(4, dtype=np.intp), 1)
        assert count.tolist() == [1]
        assert total[0] == pytest.approx(103.0 / 100.0 - 1)

    def test_a_trip_open_at_the_close_is_liquidated_at_the_last_close(self):
        first = np.array([True, False, False])
        last = np.array([False, False, True])
        held = np.array([0, -1, -1], dtype=np.int8)
        price = np.array([100.0, 100.0, 95.0])
        total, _ = round_trips(held, price, first, last, np.zeros(3, dtype=np.intp), 1)
        assert total[0] == pytest.approx(-(95.0 / 100.0 - 1))

    def test_a_position_taken_at_the_last_close_earns_nothing_and_is_not_a_trip(self):
        first = np.array([True, False])
        last = np.array([False, True])
        held = np.array([0, 1], dtype=np.int8)
        total, count = round_trips(
            held, np.array([100.0, 105.0]), first, last, np.zeros(2, dtype=np.intp), 1
        )
        assert total.tolist() == [0.0]
        assert count.tolist() == [0]


# --- selection, split, metrics ---


class TestSelectionAndMetrics:
    def test_the_train_set_is_the_first_eighty_percent_of_days(self):
        assert train_days(3680) == 2944

    def test_the_unconditional_cell_compounds_rather_than_sums(self):
        """Summed, column 0 wins at 0.10 against 0.08. Compounded, its loss drags it to -0.10."""
        returns = np.array([[0.5, 0.04], [-0.4, 0.04]])
        assert returns.sum(axis=0).argmax() == 0
        assert unconditional_cell(returns) == 1

    def test_a_tie_goes_to_the_first_cell(self):
        assert unconditional_cell(np.array([[0.1, 0.1, 0.05]])) == 0

    def test_the_metrics_are_pyfolio_s_definitions(self):
        r = np.array([0.01, -0.02, 0.015, 0.005])
        m = metrics(r)
        wealth = np.cumprod(1 + r)
        assert m["cumulative"] == pytest.approx(wealth[-1] - 1)
        assert m["annual"] == pytest.approx(wealth[-1] ** (252 / 4) - 1)
        assert m["sharpe"] == pytest.approx(np.sqrt(252) * r.mean() / r.std(ddof=1))
        drawdown = wealth[1] / wealth[0] - 1
        assert m["max_drawdown"] == pytest.approx(drawdown)
        assert m["calmar"] == pytest.approx(m["annual"] / abs(drawdown))
        assert m["arithmetic_annual"] == pytest.approx(252 * r.mean())

    def test_chan_s_annual_returns_do_not_compound_to_his_cumulative_ones(self):
        """The book's own table disagrees with itself, which Entry 16 states."""
        assert (1 + cpo.BOOK_UNCONDITIONAL["annual"]) ** 3 - 1 == pytest.approx(0.614, abs=5e-4)
        assert (1 + cpo.BOOK_CONDITIONAL["annual"]) ** 3 - 1 == pytest.approx(0.718, abs=5e-4)

    def test_chan_s_annual_returns_read_as_arithmetic_cannot_reach_them_either(self):
        """An arithmetic annual return caps what three years can compound to.

        Since ln(1 + r) <= r for every daily return, three years of daily
        returns averaging ``a / 252`` compound to at most ``exp(3a) - 1``. That
        bound sits below Chan's printed cumulative return for both arms, so his
        table disagrees with itself under either definition, whatever the
        daily returns were. Added for the post's Lesson 2.
        """
        unconditional = math.exp(3 * cpo.BOOK_UNCONDITIONAL["annual"]) - 1
        conditional = math.exp(3 * cpo.BOOK_CONDITIONAL["annual"]) - 1
        assert unconditional == pytest.approx(0.680, abs=5e-4)
        assert conditional == pytest.approx(0.810, abs=5e-4)
        assert unconditional < cpo.BOOK_UNCONDITIONAL["cumulative"]
        assert conditional < cpo.BOOK_CONDITIONAL["cumulative"]

    def test_the_costed_returns_charge_one_basis_point_a_trip(self):
        assert costed(np.array([0.01]), np.array([3])).tolist() == pytest.approx([0.0097])

    def test_the_claim_needs_all_four_metrics(self):
        base = {"cumulative": 1.0, "annual": 1.0, "sharpe": 1.0, "calmar": 1.0}
        assert claim_holds(base, {k: 2.0 for k in base})
        assert not claim_holds(base, {**{k: 2.0 for k in base}, "calmar": 1.0})


# --- the model's rows and the daily choice ---


class TestTheConditionalChoice:
    def test_a_design_row_is_three_parameters_then_the_day_s_features(self):
        features = np.arange(6, dtype=np.float32).reshape(3, 2)
        rows = design_rows(features, np.array([2]))
        assert rows.shape == (400, 5)
        assert rows[0].tolist() == [2.0, pytest.approx(0.2), 30.0, 4.0, 5.0]
        assert rows[-1].tolist() == [4.0, 2.5, 720.0, 4.0, 5.0]

    def test_each_test_day_is_chosen_from_the_previous_close(self):
        """A model that reads the row it is given: a day's own row cannot move its choice."""

        class ReadsTheFeature:
            def predict(self, x):
                # Score each cell by its lookback times the day's one feature,
                # so the sign of the feature decides between 30 and 720.
                return x[:, 2] * x[:, 3]

        features = np.array([[1.0], [1.0], [-1.0], [1.0]], dtype=np.float32)
        chosen = conditional_choices(ReadsTheFeature(), features, n_train=2, n_days=4)
        # Day 2 reads day 1's +1, so the longest lookback wins. Day 3 reads day
        # 2's −1, so the shortest wins, and day 2's own −1 never reaches day 2.
        assert [cells()[i].lookback for i in chosen] == [720, 30]

    def test_the_fit_reads_only_train_pairs(self, monkeypatch):
        seen = {}

        class Recorder:
            def __init__(self, **_):
                pass

            def fit(self, x, y):
                seen["rows"] = len(x)
                seen["y"] = y
                return self

        import sklearn.ensemble

        monkeypatch.setattr(sklearn.ensemble, "HistGradientBoostingRegressor", Recorder)
        returns = np.arange(5 * 400, dtype=np.float64).reshape(5, 400)
        cpo.fit_model(np.zeros((5, 1), dtype=np.float32), returns, n_train=3)
        # Train days are 0, 1 and 2. The pairs are (0, 1) and (1, 2), so the
        # labels are days 1 and 2, and day 3, the first test day, is never read.
        assert seen["rows"] == 800
        assert seen["y"].min() == returns[1].min()
        assert seen["y"].max() == returns[2].max()


# --- the pins, on the owner's archive ---------------------------------------


class TestWhenThePinsRun:
    """The skip in ``tests/conftest.py``, which no archive pin can check from inside."""

    def test_they_run_with_an_archive_and_the_flag(self, tmp_path):
        environ = {"QT_ARCHIVE_DIR": str(tmp_path), "QT_ARCHIVE_RUN": "1"}
        assert archive_skip_reason(environ, config=tmp_path / "absent") is None

    def test_they_skip_without_the_flag(self, tmp_path):
        environ = {"QT_ARCHIVE_DIR": str(tmp_path)}
        assert "QT_ARCHIVE_RUN=1" in archive_skip_reason(environ, config=tmp_path / "absent")

    def test_they_skip_without_an_archive(self, tmp_path):
        reason = archive_skip_reason({"QT_ARCHIVE_RUN": "1"}, config=tmp_path / "absent")
        assert reason.startswith("no data archive is configured")


@pytest.fixture(scope="module")
def result(cpo_result) -> cpo.Result:
    """One full run of Example 7.1, or a skip naming what is missing.

    ``tests/conftest.py`` holds the run and its skip, so this file and
    ``tests/test_cpo_figures.py`` read one run rather than paying for two.
    """
    return cpo_result


class TestExample71OnTheArchive:
    """Rows 1 to 11 of Entry 16, all from one run, and the pins its post added.

    The vintages are the archive's `gld_intraday_1min.csv.gz`, sha256
    `3611a8f7…0de7a`, downloaded 2026-07-17, and `gdx_intraday_1min.csv.gz`,
    sha256 `c47f5890…711c`, downloaded 2026-10-03, both Alpha Vantage at
    `adjusted=false`. The specification is the 19 readings declared on issue 23
    before any return was computed, with scikit-learn 1.9.1 and `ta` 0.11.0 as
    `uv.lock` fixes them. A lock update that moves either can move rows 5 to 10.

    The first run kept the extended-hours bars after 12:59 on NYSE's 34 early
    closes, which broke reading 2, and the review of the pull request found it.
    These pins are from the corrected run. Entry 16 sets the first run's figures
    beside them.
    """

    def test_row_11_the_span_and_the_split(self, result):
        assert result.days[0] == pd.Timestamp("2006-05-22")
        assert result.days[-1] == pd.Timestamp("2020-12-31")
        assert len(result.days) == 3680
        assert result.n_train == 2944
        assert result.test_days[0] == pd.Timestamp("2018-01-31")
        assert len(result.test_days) == 736

    def test_the_unconditional_cell_is_the_smallest_weight_lookback_and_entry(self, result):
        assert result.unconditional == Cell(2.0, 0.2, 30)

    def test_rows_1_to_4_the_unconditional_figures_and_their_gaps(self, result):
        got = metrics(result.unconditional_returns)
        assert got["cumulative"] == pytest.approx(3.403600927621887, abs=1e-9)
        assert got["annual"] == pytest.approx(0.6612471362977341, abs=1e-9)
        assert got["sharpe"] == pytest.approx(5.699728423851837, abs=1e-9)
        assert got["calmar"] == pytest.approx(15.249331720373785, abs=1e-8)
        # At Chan's printed precision, every gap is positive and large.
        assert round(got["cumulative"], 2) - 0.73 == pytest.approx(2.67)
        assert round(got["annual"], 4) - 0.1729 == pytest.approx(0.4883)
        assert round(got["sharpe"], 3) - 1.947 == pytest.approx(3.753)
        assert round(got["calmar"], 3) - 0.984 == pytest.approx(14.265)

    def test_row_5_chan_s_claim_does_not_hold(self, result):
        """Conditional wins on Calmar alone and loses on Sharpe and both returns."""
        unconditional = metrics(result.unconditional_returns)
        conditional = metrics(result.conditional_returns)
        better = {name for name in cpo.METRICS if conditional[name] > unconditional[name]}
        assert better == {"calmar"}
        assert not claim_holds(unconditional, conditional)

    def test_row_6_the_conditional_figures_beside_chan_s(self, result):
        got = metrics(result.conditional_returns)
        assert got["cumulative"] == pytest.approx(3.116680929400907, abs=1e-9)
        assert got["annual"] == pytest.approx(0.6233629131053431, abs=1e-9)
        assert got["sharpe"] == pytest.approx(5.274377985680034, abs=1e-9)
        assert got["calmar"] == pytest.approx(18.63739123362268, abs=1e-8)

    def test_row_6_how_often_the_conditional_arm_keeps_the_unconditional_cell(self, result):
        """Added after the result was seen, and not among reading 16's rows. It decides nothing."""
        chosen = result.conditional_cells
        unconditional = cells().index(result.unconditional)
        assert int((chosen == unconditional).sum()) == 557
        assert len(set(chosen.tolist())) == 44
        assert int((np.diff(chosen) != 0).sum()) == 254

    def test_row_7_the_arithmetic_annual_returns(self, result):
        assert metrics(result.unconditional_returns)["arithmetic_annual"] == pytest.approx(
            0.5120905561032464, abs=1e-9
        )
        assert metrics(result.conditional_returns)["arithmetic_annual"] == pytest.approx(
            0.4892191781531026, abs=1e-9
        )

    def test_row_8_one_basis_point_a_round_trip_turns_both_arms_to_losses(self, result):
        unconditional = metrics(costed(result.unconditional_returns, result.unconditional_trips))
        conditional = metrics(costed(result.conditional_returns, result.conditional_trips))
        assert unconditional["sharpe"] == pytest.approx(-7.614270686532979, abs=1e-9)
        assert unconditional["cumulative"] == pytest.approx(-0.8583878331403573, abs=1e-9)
        assert conditional["sharpe"] == pytest.approx(-6.122139215884792, abs=1e-9)
        assert conditional["cumulative"] == pytest.approx(-0.8139195761710087, abs=1e-9)

    def test_row_9_round_trips_a_day(self, result):
        assert result.unconditional_trips.mean() == pytest.approx(46.692934782608695, abs=1e-9)
        assert result.conditional_trips.mean() == pytest.approx(42.06385869565217, abs=1e-9)

    def test_row_10_where_chan_s_sharpe_sits_among_the_400_cells(self, result):
        """Added after the result was seen. It locates the gap and decides nothing."""
        sharpes = result.cell_sharpes
        assert sharpes.min() == pytest.approx(0.8067846216494515, abs=1e-9)
        assert float(np.median(sharpes)) == pytest.approx(3.5063034976327305, abs=1e-9)
        assert sharpes.max() == pytest.approx(5.8911003445458965, abs=1e-9)
        assert cells()[int(np.argmax(sharpes))].label == "2.5_30_0.2"
        assert int((sharpes < 1.947).sum()) == 39
        nearest = int(np.argmin(np.abs(sharpes - 1.947)))
        assert cells()[nearest].label == "3_60_2.5"
        assert sharpes[nearest] == pytest.approx(1.9311, abs=5e-5)
        assert result.cell_trips[nearest] == pytest.approx(1.19, abs=0.005)

    # The five pins below were added for the post on this example,
    # blog/conditional-parameter-optimization-lessons.md, so that every figure
    # it quotes from the corrected run traces to an assertion rather than to
    # prose. Entry 16 names them.

    def test_rows_1_to_4_as_multiples_of_chan_s_figures(self, result):
        """Each computed figure over Chan's, which Entry 16 states and the post quotes.

        Only the unconditional arm enters, so the model cannot move these.
        """
        got = metrics(result.unconditional_returns)
        multiples = {name: got[name] / cpo.BOOK_UNCONDITIONAL[name] for name in cpo.METRICS}
        assert multiples["cumulative"] == pytest.approx(4.662467024139571, abs=1e-9)
        assert multiples["annual"] == pytest.approx(3.8244484459093937, abs=1e-9)
        assert multiples["sharpe"] == pytest.approx(2.927441409271616, abs=1e-9)
        assert multiples["calmar"] == pytest.approx(15.497288333713197, abs=1e-8)
        assert {name: round(value, 1) for name, value in multiples.items()} == {
            "cumulative": 4.7,
            "annual": 3.8,
            "sharpe": 2.9,
            "calmar": 15.5,
        }

    def test_each_arm_earns_less_a_round_trip_than_a_round_trip_costs(self, result):
        """Added after the result was seen. It explains row 8 and decides nothing.

        The edge is the sum of an arm's test-day returns over the sum of its
        round trips, in basis points. The re-chosen arm's rests on the model, so
        a lock update can move it, as it can rows 5 to 10.
        """
        unconditional = result.unconditional_returns.sum() / result.unconditional_trips.sum()
        conditional = result.conditional_returns.sum() / result.conditional_trips.sum()
        assert unconditional * 1e4 == pytest.approx(0.43520618072586204, abs=1e-9)
        assert conditional * 1e4 == pytest.approx(0.461523503846464, abs=1e-9)
        assert round(unconditional * 1e4, 3) == 0.435
        assert round(conditional * 1e4, 3) == 0.462
        assert max(unconditional, conditional) < cpo.COST_PER_ROUND_TRIP

    def test_the_chosen_cell_is_the_second_busiest_of_the_400(self, result):
        """Added after the result was seen. Only ``2.5_30_0.2`` trades more, and it decides nothing.

        Only the unconditional arm enters, so the model cannot move this.
        """
        chosen = cells().index(result.unconditional)
        busier = np.flatnonzero(result.cell_trips > result.cell_trips[chosen])
        assert [cells()[i].label for i in busier] == ["2.5_30_0.2"]

    def test_the_claim_holds_for_2_of_10_seeds(self, result):
        """Added after the result was seen. How far row 5 rests on reading 14's seed.

        With over 10,000 rows the model's early stopping is on, so its seed
        picks the tenth of the train rows held out to judge it, and the sample
        its bins are cut from. Reading 14 declared seed 0, which row 5 pins.
        Seeds 2 and 7 make re-choosing beat holding on all four metrics. This
        decides nothing. Like rows 5 to 10, it rests on the model, so a lock update
        can move it.
        """
        from sklearn.ensemble import HistGradientBoostingRegressor

        features, returns, n_train = result.features, result.label_returns, result.n_train
        n_days = len(result.days)
        decided = np.arange(n_train - 1)
        x = design_rows(features, decided)
        y = returns[decided + 1].reshape(-1).astype(np.float64)
        unconditional = metrics(result.unconditional_returns)
        rows = np.arange(n_train, n_days)
        held, sharpes = [], []
        wins = dict.fromkeys(cpo.METRICS, 0)
        for seed in range(SEEDS_TRIED):
            model = HistGradientBoostingRegressor(random_state=seed).fit(x, y)
            chosen = conditional_choices(model, features, n_train, n_days)
            conditional = metrics(returns[rows, chosen])
            sharpes.append(conditional["sharpe"])
            for name in cpo.METRICS:
                wins[name] += conditional[name] > unconditional[name]
            if claim_holds(unconditional, conditional):
                held.append(seed)
        assert tuple(held) == SEEDS_THE_CLAIM_HOLDS_FOR
        assert sharpes[0] == pytest.approx(5.274377985680034, abs=1e-9)
        assert (round(min(sharpes), 3), round(max(sharpes), 3)) == SEED_SHARPE_RANGE
        assert wins == SEED_WINS

    def test_turnover_and_sharpe_ratio_rise_together_across_the_400_cells(self, result):
        """Added after the result was seen. Spearman's rank correlation, deciding nothing."""
        rho = spearmanr(result.cell_trips, result.cell_sharpes).statistic
        assert rho == pytest.approx(0.9485368645941135, abs=1e-9)
        assert round(rho, 2) == 0.95


# --- what the mutation lens of PR 285's review found unheld ------------------
#
# Each test below kills mutants that survived the default suite: a feature read
# a day late, the strategy traded on GDX, the unconditional cell chosen on every
# day including the test days, a threshold boundary, a trip that returns
# nothing, an unseeded model. Most of them only the archive pins would have
# noticed, and the selection leak probably not even those.


class TestTheBoundariesAndConstants:
    @pytest.mark.parametrize("entry", [1.0, 0.7, 1.25])
    @pytest.mark.parametrize("start", [-9.0, 9.0, 0.0])
    @pytest.mark.parametrize("which", ["-entry", "entry", "-inner", "inner"])
    def test_the_rules_match_the_literal_loop_exactly_on_each_threshold(self, entry, start, which):
        """A random z-score never lands on a threshold, so these place it there."""
        edge = {
            "-entry": -entry,
            "entry": entry,
            "-inner": EXIT_FRACTION * entry,
            "inner": -EXIT_FRACTION * entry,
        }[which]
        z = np.array([start, edge, edge])
        first = np.array([True, False, False])
        np.testing.assert_array_equal(
            positions(z, entry, first), literal_positions(z, entry, first)
        )

    def test_the_exit_fraction_is_the_book_s_minus_0_6(self):
        """pp. 140 to 141. A short exits at 0.55 under −0.6 and would hold under −0.5."""
        assert positions(np.array([1.2, 0.55]), 1.0, np.array([True, False])).tolist() == [-1, 0]

    def test_the_grids_are_the_printed_ones(self):
        assert cpo.GDX_WEIGHTS == (2.0, 2.5, 3.0, 3.5, 4.0)
        assert cpo.LOOKBACKS == (30, 60, 90, 120, 180, 240, 360, 720)
        assert cpo.ENTRY_THRESHOLDS == (0.2, 0.3, 0.4, 0.5, 0.7, 1.0, 1.25, 1.5, 2.0, 2.5)
        assert cpo.FEATURE_LOOKBACKS == (50, 100, 200, 400, 800, 1600, 3200)

    def test_the_z_score_divides_by_the_root_of_the_variance(self):
        spread = np.random.default_rng(3).normal(0, 1, 200).cumsum()
        ema, var = ema_var(spread, 30)
        np.testing.assert_allclose(zscore(spread, 30)[1:], ((spread - ema) / np.sqrt(var))[1:])

    def test_a_trip_that_returns_nothing_still_counts(self):
        """Minute bars move in whole cents, so an exit at the entry price is common."""
        first = np.array([True, False, False, False])
        last = np.array([False, False, False, True])
        held = np.array([1, 1, 0, 0], dtype=np.int8)
        price = np.array([100.0, 101.0, 100.0, 99.0])
        total, count = round_trips(held, price, first, last, np.zeros(4, dtype=np.intp), 1)
        assert total.tolist() == [0.0]
        assert count.tolist() == [1]

    def test_the_train_set_floors_a_fractional_day(self):
        assert train_days(3681) == 2944
        assert train_days(9) == 7

    def test_a_loss_on_the_first_day_is_a_drawdown_from_the_starting_wealth(self):
        assert metrics(np.array([-0.1, 0.05, 0.02]))["max_drawdown"] == pytest.approx(-0.1)

    def test_a_series_with_no_drawdown_has_an_infinite_calmar(self):
        assert metrics(np.array([0.01, 0.02, 0.01]))["calmar"] == float("inf")


class TestTheWiring:
    def test_the_model_is_seeded(self, monkeypatch):
        seen = {}

        class Recorder:
            def __init__(self, **kwargs):
                seen.update(kwargs)

            def fit(self, x, y):
                return self

        import sklearn.ensemble

        monkeypatch.setattr(sklearn.ensemble, "HistGradientBoostingRegressor", Recorder)
        cpo.fit_model(np.zeros((5, 1), dtype=np.float32), np.zeros((5, 400)), n_train=3)
        assert seen == {"random_state": 0}

    def test_a_day_s_features_are_its_last_regular_session_bar(self, monkeypatch):
        index = pd.to_datetime(
            [
                "2006-06-01 09:30",
                "2006-06-01 15:59",
                "2006-06-01 16:05",
                "2006-06-02 09:30",
                "2006-06-02 15:59",
                "2006-06-02 16:05",
            ]
        )
        bars = pd.DataFrame({"close": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]}, index=index)
        monkeypatch.setattr(
            cpo, "indicators", lambda b, n: pd.DataFrame({"x": b["close"] * n}, index=b.index)
        )
        features = cpo.daily_features(bars, "gld", pd.DatetimeIndex(["2006-06-01", "2006-06-02"]))
        # The 15:59 bar, never the 16:05 one, and each day its own, never the next.
        assert features["gld_x_50"].tolist() == [100.0, 250.0]
        assert features.shape[1] == len(cpo.FEATURE_LOOKBACKS)

    def test_an_early_close_s_features_are_its_1259_bar(self, monkeypatch):
        index = pd.to_datetime(["2019-11-29 12:59", "2019-11-29 14:57"])
        bars = pd.DataFrame({"close": [7.0, 8.0]}, index=index)
        monkeypatch.setattr(
            cpo, "indicators", lambda b, n: pd.DataFrame({"x": b["close"] * n}, index=b.index)
        )
        features = cpo.daily_features(bars, "gld", pd.DatetimeIndex(["2019-11-29"]))
        assert features["gld_x_50"].tolist() == [350.0]

    def test_each_label_column_is_its_cell_run_on_gld(self):
        rng = np.random.default_rng(5)
        index = pd.DatetimeIndex([])
        for day in pd.date_range("2006-06-01", periods=30, freq="D"):
            index = index.append(
                pd.date_range(day + pd.Timedelta("9h30min"), periods=60, freq="min")
            )
        n = len(index)
        grid = pd.DataFrame(
            {
                "gld": 100 * np.exp(rng.normal(0, 1e-3, n).cumsum()),
                "gdx": 30 * np.exp(rng.normal(0, 1e-3, n).cumsum()),
            },
            index=index,
        )
        labels = cpo.strategy_labels(grid)
        first, last, codes, days = day_bounds(grid.index)
        gld, gdx = grid["gld"].to_numpy(), grid["gdx"].to_numpy()
        for i, cell in enumerate(cells()):
            held = positions(zscore(gld - cell.weight * gdx, cell.lookback), cell.entry, first)
            total, count = round_trips(held, gld, first, last, codes, len(days))
            np.testing.assert_array_equal(labels.returns[:, i], total)
            np.testing.assert_array_equal(labels.trips[:, i], count)

    def test_the_indicators_use_their_declared_windows(self):
        from ta.momentum import AwesomeOscillatorIndicator

        rng = np.random.default_rng(9)
        close = pd.Series(100 * np.exp(rng.normal(0, 1e-3, 600).cumsum()))
        bars = pd.DataFrame(
            {"high": close + 0.05, "low": close - 0.05, "close": close, "volume": 1000}
        )
        got = cpo.indicators(bars, 50)
        mean = close.rolling(50).mean()
        spread = close.rolling(50).std(ddof=0)
        pd.testing.assert_series_equal(got["bbz"], (close - mean) / spread, check_names=False)
        slow = AwesomeOscillatorIndicator(bars["high"], bars["low"], 50, 340).awesome_oscillator()
        pd.testing.assert_series_equal(got["ao"], slow, check_names=False)

    def test_atr_and_adx_read_0_rather_than_nothing_before_their_windows_fill(self):
        """``ta`` 0.11.0 fills the unfilled rows with 0, which reading 12 leaves alone.

        The post's first limit and Entry 16 state it. At a lookback of 50 the ATR
        reads 0 on its first 49 rows and the ADX on its first 99, while the other
        five indicators leave those rows missing.
        """
        rng = np.random.default_rng(9)
        close = pd.Series(100 * np.exp(rng.normal(0, 1e-3, 600).cumsum()))
        bars = pd.DataFrame(
            {"high": close + 0.05, "low": close - 0.05, "close": close, "volume": 1000}
        )
        got = cpo.indicators(bars, 50)
        assert got["atr"].notna().all() and got["adx"].notna().all()
        assert (got["atr"].iloc[:49] == 0).all() and (got["atr"].iloc[49:] != 0).all()
        assert (got["adx"].iloc[:99] == 0).all() and (got["adx"].iloc[99:] != 0).all()
        assert got[["bbz", "mfi", "donchian"]].iloc[:49].isna().all().all()

    def test_the_model_reads_101_features_a_row(self):
        """Reading 12: three parameters, then seven indicators on each fund at seven lookbacks.

        The post's item on the model and README quote 101 against the book's 115.
        This builds the design rows the way :func:`chan.cpo.run` does, so an
        indicator dropped or added anywhere on that path changes the width.
        """
        # ``ta``'s ADX needs twice its window of bars, so 17 days of 390 cover 3,200.
        days = pd.date_range("2006-06-01", periods=17, freq="B")
        index = pd.DatetimeIndex([])
        for day in days:
            index = index.append(
                pd.date_range(day + pd.Timedelta("9h30min"), periods=390, freq="min")
            )
        close = pd.Series(
            100 * np.exp(np.random.default_rng(4).normal(0, 1e-3, len(index)).cumsum()),
            index=index,
        )
        bars = pd.DataFrame(
            {"high": close + 0.05, "low": close - 0.05, "close": close, "volume": 1000},
            index=index,
        )
        features = pd.concat(
            [cpo.daily_features(bars, "gld", days), cpo.daily_features(bars, "gdx", days)],
            axis=1,
        ).to_numpy(dtype=np.float32)
        assert design_rows(features, np.arange(2)).shape == (800, 101)

    def test_run_selects_on_train_days_and_reports_test_days(self, monkeypatch):
        """Column 0 wins on the train days, column 1 over all days, and the model picks 2."""
        n_days = 15
        days = pd.date_range("2006-06-01", periods=n_days, freq="D")
        returns = np.random.default_rng(0).normal(0, 1e-6, (n_days, 400))
        returns[:12, 0] = 0.01
        returns[12:, 1] = 0.5 + np.array([0.0, 0.001, 0.002])
        returns[:, 2] = np.arange(n_days) / 1000.0
        trips = np.tile(np.arange(n_days)[:, None], (1, 400))
        trips[14] = 50
        bars = pd.DataFrame({"close": [1.0]}, index=pd.to_datetime(["2006-06-01 09:30"]))
        bars.attrs["vintage"] = None
        monkeypatch.setattr(cpo.archive, "minute_bars", lambda *a, **k: bars)
        monkeypatch.setattr(cpo, "minute_grid", lambda a, b: None)
        monkeypatch.setattr(cpo, "strategy_labels", lambda g: cpo.Labels(days, returns, trips))
        monkeypatch.setattr(
            cpo, "daily_features", lambda b, p, d: pd.DataFrame({p: np.zeros(len(d))}, index=d)
        )
        monkeypatch.setattr(cpo, "fit_model", lambda f, r, n: None)
        monkeypatch.setattr(cpo, "conditional_choices", lambda m, f, n, d: np.full(d - n, 2))
        result = cpo.run()
        assert result.n_train == 12
        assert result.unconditional == cells()[0]
        assert result.unconditional_returns.tolist() == returns[12:, 0].tolist()
        assert result.conditional_returns.tolist() == [0.012, 0.013, 0.014]
        assert result.conditional_trips.tolist() == [12, 13, 50]
        assert result.cell_trips.tolist() == [25.0] * 400


# --- the post, read against the code and the run ------------------------------

POST = (
    Path(__file__).resolve().parents[1] / "blog" / "conditional-parameter-optimization-lessons.md"
)

#: The counts the post spells out in words.
WORDS = {2: "two", 3: "three", 5: "five", 6: "six", 7: "seven", 8: "eight", 10: "ten"}
ORDINALS = {1: "first", 2: "second", 3: "third"}

_METRIC_ROWS = {
    "cumulative": "Cumulative return",
    "annual": "Annual return",
    "sharpe": "Sharpe ratio",
    "calmar": "Calmar ratio",
}


def _percent(fraction: float, places: int) -> str:
    return f"{100 * fraction:.{places}f}%"


def _signed(text: str) -> str:
    """The post writes a minus sign, not a hyphen."""
    return text.replace("-", "\N{MINUS SIGN}")


def _quotes(text: str, phrase: str) -> None:
    """Fail naming the phrase, so a reworded sentence reads as one rather than as a number."""
    assert phrase in text, f"the post no longer says: {phrase}"


def _table(text: str, head: str) -> dict[str, list[str]]:
    """The first math table whose head row starts with ``head``, as cells by metric."""
    for block in text.split("```math")[1:]:
        table = block.split("```", 1)[0]
        lines = table.strip().splitlines()
        if lines[1].startswith(f"\\text{{{head}}}"):
            rows = {}
            for line in lines[2:]:
                if line.startswith("\\text{"):
                    cells_ = [cell.strip().rstrip("\\").strip() for cell in line.split("&")]
                    rows[cells_[0][len("\\text{") : -1]] = [
                        cell.replace("\\%", "%") for cell in cells_[1:]
                    ]
            return rows
    raise AssertionError(f"the post has no table headed {head}")


def _figure(metric: str, value: float, places: int) -> str:
    """A table cell: a return as a percent, a ratio as a number."""
    if metric in ("cumulative", "annual"):
        return _percent(value, places - 2)
    return f"{value:.{places}f}"


class TestThePostQuotesWhatEveryCloneComputes:
    """The post's figures a clone can hold without the run, one copy of each, read from the post.

    Each test reads the sentence or table cell it names: the book columns of
    Lesson 1's tables, held to ``chan.cpo``'s ``BOOK_*`` constants rather than
    to the page; Chan's arithmetic in Lesson 2; the early closes and the 12:59
    fix in Lesson 3; the grid, the rules, the split, the trading year and the
    cost; the feature count; and the two download dates, held to the archive's
    manifest. The seeds sentences are held to this file's ``SEED*`` constants,
    which ``test_the_claim_holds_for_2_of_10_seeds`` derives on the archive. A
    second copy of a figure elsewhere in the post is not read. The run's own
    figures need the archive, so ``TestThePostQuotesTheRun`` reads those.
    """

    text = POST.read_text("utf-8")

    def test_the_book_columns_of_the_lesson_1_tables(self) -> None:
        """Chan's eight printed figures, at his precision, are the module's constants."""
        for head, book in (
            ("Fixed arm", cpo.BOOK_UNCONDITIONAL),
            ("Re-chosen arm", cpo.BOOK_CONDITIONAL),
        ):
            rows = _table(self.text, head)
            for metric, name in _METRIC_ROWS.items():
                assert rows[name][1] == _figure(metric, book[metric], cpo.BOOK_DECIMALS[metric])

    def test_lesson_2_compounds_chan_s_annual_returns(self) -> None:
        fixed, rechosen = cpo.BOOK_UNCONDITIONAL, cpo.BOOK_CONDITIONAL
        _quotes(
            self.text,
            f"{_percent(fixed['annual'], 2)} a year compounds to "
            f"{_percent((1 + fixed['annual']) ** 3 - 1, 1)} over three years, "
            f"not the printed {_percent(fixed['cumulative'], 0)}",
        )
        _quotes(
            self.text,
            f"{_percent(rechosen['annual'], 2)} a year compounds to "
            f"{_percent((1 + rechosen['annual']) ** 3 - 1, 1)}, "
            f"not the printed {_percent(rechosen['cumulative'], 0)}",
        )

    def test_lesson_2_caps_them_read_as_arithmetic(self) -> None:
        fixed, rechosen = cpo.BOOK_UNCONDITIONAL, cpo.BOOK_CONDITIONAL
        _quotes(
            self.text,
            f"At an arithmetic {_percent(fixed['annual'], 2)} a year, the daily returns average "
            f"{fixed['annual']:g} ÷ {cpo.TRADING_DAYS}, so three years of them sum to "
            f"3 × {fixed['annual']:g}, and the cap is a cumulative return of "
            f"{_percent(math.exp(3 * fixed['annual']) - 1, 1)}, "
            f"still short of {_percent(fixed['cumulative'], 0)}",
        )
        _quotes(
            self.text,
            f"{_percent(rechosen['annual'], 2)} caps at "
            f"{_percent(math.exp(3 * rechosen['annual']) - 1, 1)}, "
            f"short of {_percent(rechosen['cumulative'], 0)}",
        )

    def test_lesson_3_the_early_closes_and_their_last_minute(self) -> None:
        years = sorted(day[:4] for day in cpo.EARLY_CLOSES)
        _quotes(
            self.text, f"From {years[0]} to {years[-1]} there were {len(cpo.EARLY_CLOSES)} of them."
        )
        _quotes(self.text, f"It ended those days at {cpo.EARLY_CLOSE_LAST}")

    def test_the_grid(self) -> None:
        def span(values) -> str:
            return f"from {min(values):g} to {max(values):g}"

        weights, lookbacks, entries = cpo.GDX_WEIGHTS, cpo.LOOKBACKS, cpo.ENTRY_THRESHOLDS
        _quotes(
            self.text,
            f"The book’s grid has {WORDS[len(weights)]} weights {span(weights)}, "
            f"{WORDS[len(lookbacks)]} lookbacks {span(lookbacks)} minutes, and "
            f"{WORDS[len(entries)]} entry thresholds {span(entries)}, so "
            f"{len(weights)} × {len(lookbacks)} × {len(entries)} = {len(cells())} combinations",
        )

    def test_the_rules_the_split_and_the_cost(self) -> None:
        inner = -EXIT_FRACTION
        _quotes(
            self.text,
            f"Exit a long when the z-score rises back above {_signed(f'{EXIT_FRACTION:g}')} "
            f"times the entry threshold, and exit a short when it falls back below "
            f"{inner:g} times the threshold",
        )
        _quotes(self.text, f"regular session, {cpo.SESSION_FIRST} to {cpo.SESSION_LAST}")
        _quotes(self.text, f"the first {cpo.TRAIN_FRACTION:.0%} of the days")
        _quotes(self.text, f"a year of {cpo.TRADING_DAYS} trading days")
        _quotes(
            self.text,
            f"At a cost of {cpo.COST_PER_ROUND_TRIP * 1e4:g} basis point a round trip",
        )

    def test_the_feature_count(self) -> None:
        """Three parameters, then each indicator of each fund at each window."""
        rng = np.random.default_rng(9)
        close = pd.Series(100 * np.exp(rng.normal(0, 1e-3, 60).cumsum()))
        bars = pd.DataFrame(
            {"high": close + 0.05, "low": close - 0.05, "close": close, "volume": 1000}
        )
        named = cpo.indicators(bars, 10).shape[1]
        windows = len(cpo.FEATURE_LOOKBACKS)
        _quotes(
            self.text,
            f"{WORDS[named]} named technical indicators for each fund, each computed over "
            f"{WORDS[windows]} windows",
        )
        _quotes(
            self.text,
            f"That makes 3 + {named} × 2 × {windows} = {3 + 2 * named * windows} features.",
        )

    def test_the_seeds_sentence_quotes_the_seed_pin(self) -> None:
        """The figures ``test_the_claim_holds_for_2_of_10_seeds`` holds on the archive.

        Without the archive it checks only that the post quotes these constants, and
        that pin is what ties them to the refit.
        """
        low, high = SEED_SHARPE_RANGE
        held = len(SEEDS_THE_CLAIM_HOLDS_FOR)
        _quotes(
            self.text,
            f"refit the model with each of seeds 0 to {SEEDS_TRIED - 1}.",
        )
        _quotes(
            self.text,
            f"With {WORDS[held]} of those {WORDS[SEEDS_TRIED]} seeds, re-choosing wins on all "
            f"four metrics. The re-chosen arm’s Sharpe ratio runs from {low:.3f} to {high:.3f} "
            f"across all {WORDS[SEEDS_TRIED]} seeds",
        )
        _quotes(
            self.text,
            f"Refit with each of {WORDS[SEEDS_TRIED]} seeds after the result was seen, the model "
            f"makes re-choosing win on all four for {WORDS[held]} of them",
        )

    def test_the_seeds_wins_per_metric(self) -> None:
        """How many of the ten seeds win on each metric, from ``SEED_WINS``."""
        w = {name: WORDS[count] for name, count in SEED_WINS.items()}
        assert SEED_WINS["cumulative"] == SEED_WINS["annual"]
        _quotes(
            self.text,
            f"Across the ten, re-choosing beats the fixed arm on the Calmar ratio for "
            f"{w['calmar']} seeds, on the Sharpe ratio for {w['sharpe']} and on each return "
            f"for {w['cumulative']}.",
        )

    def test_the_download_dates(self) -> None:
        """The two vintages' download dates, held to the archive's manifest."""
        by_path = {entry.path: entry for entry in read_archive_manifest()}
        gld = by_path["gld_intraday_1min.csv.gz"].download_date
        gdx = by_path["gdx_intraday_1min.csv.gz"].download_date
        _quotes(self.text, f"GLD was downloaded on {gld} and GDX on {gdx}.")


class TestThePostQuotesTheRun:
    """The post's figures from the run, one copy of each, read from the post itself.

    Each test reads the sentence or table cell it names and holds it to the
    shared run that ``TestExample71OnTheArchive`` pins, at the precision the
    post prints. A second copy of a figure elsewhere in the post, such as the
    5.700 in the opening list or the corrected columns of Lesson 3's tables,
    is not read. These run only where the archive is, like the pins.
    """

    text = POST.read_text("utf-8")

    def test_the_computed_columns_of_the_lesson_1_tables(self, result):
        for head, returns in (
            ("Fixed arm", result.unconditional_returns),
            ("Re-chosen arm", result.conditional_returns),
        ):
            got = metrics(returns)
            rows = _table(self.text, head)
            for metric, name in _METRIC_ROWS.items():
                assert rows[name][0] == _figure(metric, got[metric], cpo.BOOK_DECIMALS[metric])

    def test_which_metric_re_choosing_wins(self, result):
        """The verdict's words: the one metric re-choosing wins with the seed fixed in advance."""
        fixed = metrics(result.unconditional_returns)
        rechosen = metrics(result.conditional_returns)
        (won,) = [name for name in cpo.METRICS if rechosen[name] > fixed[name]]
        name = {"sharpe": "Sharpe ratio", "calmar": "Calmar ratio"}[won]
        _quotes(
            self.text,
            f"Re-choosing beats holding on the {name}, {rechosen[won]:.3f} against "
            f"{fixed[won]:.3f}.",
        )
        _quotes(self.text, f"In the corrected run it wins on the {name} alone.")

    def test_the_gaps_and_the_multiples(self, result):
        got = metrics(result.unconditional_returns)
        book = cpo.BOOK_UNCONDITIONAL
        rounded = {m: round(got[m], cpo.BOOK_DECIMALS[m]) for m in _METRIC_ROWS}
        gaps = {m: rounded[m] - book[m] for m in _METRIC_ROWS}
        _quotes(
            self.text,
            f"The gaps between computed and printed figures are +{100 * gaps['cumulative']:.0f} "
            f"and +{100 * gaps['annual']:.2f} percentage points on the two returns, and "
            f"+{gaps['sharpe']:.3f} and +{gaps['calmar']:.3f} on the two ratios.",
        )
        times = {m: got[m] / book[m] for m in _METRIC_ROWS}
        _quotes(
            self.text,
            f"about {times['cumulative']:.1f} times on cumulative return, "
            f"{times['annual']:.1f} times on annual return, {times['sharpe']:.1f} times on "
            f"the Sharpe ratio and {times['calmar']:.1f} times on the Calmar ratio",
        )

    def test_how_often_the_model_kept_the_fixed_cell(self, result):
        chosen = result.conditional_cells
        kept = int((chosen == cells().index(result.unconditional)).sum())
        _quotes(
            self.text,
            f"on {kept} of the {len(result.test_days)} test days the model picked the same cell",
        )
        _quotes(
            self.text,
            f"it used {len(set(chosen.tolist()))} different cells and switched "
            f"{int((np.diff(chosen) != 0).sum())} times",
        )

    def test_the_span_and_the_split(self, result):
        _quotes(
            self.text,
            f"GDX did not trade until {result.days[0]:%Y-%m-%d}. From then to "
            f"{result.days[-1]:%Y-%m-%d} there are {len(result.days):,} days",
        )
        _quotes(
            self.text,
            f"The test is the last {len(result.test_days)} of those days, from "
            f"{result.test_days[0]:%Y-%m-%d} to {result.test_days[-1]:%Y-%m-%d}.",
        )

    def test_the_arithmetic_annual_returns(self, result):
        fixed = metrics(result.unconditional_returns)["arithmetic_annual"]
        rechosen = metrics(result.conditional_returns)["arithmetic_annual"]
        _quotes(
            self.text,
            f"its annual return is {_percent(fixed, 2)} for the fixed arm and "
            f"{_percent(rechosen, 2)} for the re-chosen one",
        )

    def test_one_basis_point_a_round_trip(self, result):
        fixed = metrics(costed(result.unconditional_returns, result.unconditional_trips))
        rechosen = metrics(costed(result.conditional_returns, result.conditional_trips))
        _quotes(
            self.text,
            f"the fixed arm’s Sharpe ratio becomes {_signed(f'{fixed["sharpe"]:.3f}')} and its "
            f"cumulative return {_signed(_percent(fixed['cumulative'], 1))}. The re-chosen arm’s "
            f"become {_signed(f'{rechosen["sharpe"]:.3f}')} and "
            f"{_signed(_percent(rechosen['cumulative'], 1))}.",
        )

    def test_the_chosen_cell_and_its_round_trips(self, result):
        _quotes(
            self.text,
            f"picks `{result.unconditional.label}`: the smallest weight, the shortest lookback "
            f"and the lowest entry threshold on the grid. On the test days it trades "
            f"{result.unconditional_trips.mean():.1f} round trips a day",
        )
        _quotes(
            self.text,
            f"The re-chosen arm trades {result.conditional_trips.mean():.1f}, and its figures "
            "in this lesson come from the seed fixed in advance.",
        )
        chosen = cells().index(result.unconditional)
        rank = 1 + int((result.cell_trips > result.cell_trips[chosen]).sum())
        _quotes(self.text, f"the {ORDINALS[rank]} most of the {len(cells())} cells")

    def test_the_edge_a_round_trip(self, result):
        fixed = result.unconditional_returns.sum() / result.unconditional_trips.sum()
        rechosen = result.conditional_returns.sum() / result.conditional_trips.sum()
        _quotes(self.text, f"the fixed arm earns {fixed * 1e4:.3f} basis points a round trip")
        _quotes(self.text, f"The re-chosen arm earns {rechosen * 1e4:.3f}.")

    def test_the_400_cells(self, result):
        sharpes = result.cell_sharpes
        book = cpo.BOOK_UNCONDITIONAL["sharpe"]
        nearest = int(np.argmin(np.abs(sharpes - book)))
        _quotes(
            self.text,
            f"Across the {len(cells())} cells, the test Sharpe ratios run from "
            f"{sharpes.min():.3f} to {sharpes.max():.3f}, with a median of "
            f"{float(np.median(sharpes)):.3f}. Only {int((sharpes < book).sum())} cells sit "
            f"below {book}. The nearest is `{cells()[nearest].label}`, at "
            f"{sharpes[nearest]:.3f}, and it trades {result.cell_trips[nearest]:.2f} round trips",
        )

    def test_turnover_and_sharpe_ratio_rise_together(self, result):
        rho = spearmanr(result.cell_trips, result.cell_sharpes).statistic
        _quotes(self.text, f"is {rho:.2f}. These figures were added after the result was seen")

    def test_the_overshoot_against_the_third_party(self, result):
        times = metrics(result.unconditional_returns)["sharpe"] / cpo.BOOK_UNCONDITIONAL["sharpe"]
        _quotes(self.text, f"both overshoot Chan’s 1.947, by {times:.1f} times here")
