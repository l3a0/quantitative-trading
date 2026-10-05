"""Example 7.1, Conditional Parameter Optimization, against the readings declared on issue 23.

Two kinds of test live here.

1. **The mechanics**, on synthetic data, run everywhere. Each vectorised step is
   held against a literal loop that reads like the book's rule, so a fast
   implementation that drifts from the rule fails here.
2. **The pins**, on the owner's archive of Alpha Vantage minute bars. A public
   clone has no archive, and the full run takes minutes, so these skip unless
   an archive is configured and ``QT_ARCHIVE_RUN=1`` asks for them. The skip
   reason says which of the two is missing.

Every pinned figure names its vintages, the two archive files by their sha256
in ``data/archive_vintages.jsonl``, and its specification, the readings
declared on issue 23 before any number was computed.

``blog/conditional-parameter-optimization-lessons.md`` quotes these pins, and
its figure's own labels are held by ``tests/test_cpo_figures.py``. What the
post says that nothing here asserts is listed in README's ``## The write-up``.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest
from scipy.stats import spearmanr

from chan import cpo
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
from tests.conftest import CPO_GROUP, archive_skip_reason

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
        """2019-11-29 closed at 13:00, so its 13:00 to 15:59 bars are extended hours."""
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


class TestTheRunIsSharedAcrossWorkers:
    """The hook in ``tests/conftest.py`` that keeps one run of Example 7.1 per suite.

    Without it, each xdist worker drawing a pin builds the run again. The pins
    skip on every machine without the archive, so nothing else here would
    notice a run built ten times over.
    """

    def test_every_test_reading_the_run_is_in_its_group(self, request):
        """Inside a worker it also checks the node ids, because xdist groups by
        a suffix it writes onto each one from the marks it finds when its own
        collection hook runs. Measured on 16 readers, the hook without
        ``tryfirst`` left all 16 marked and none suffixed, so checking the marks
        alone passed while every reader still ran wherever it landed.

        One test rather than a second that skips outside a worker, so a serial
        run and a parallel one report the same passed and skipped counts.
        """
        readers = [item for item in request.session.items if "cpo_result" in item.fixturenames]
        if not readers:
            pytest.skip("this selection collected no test that reads cpo_result")
        groups = [[mark.args for mark in item.iter_markers("xdist_group")] for item in readers]
        assert groups == [[(CPO_GROUP,)]] * len(readers)
        if hasattr(request.config, "workerinput"):
            suffix = f"@{CPO_GROUP}"
            assert [item.nodeid for item in readers if not item.nodeid.endswith(suffix)] == []

    def test_the_suite_runs_groups_on_one_worker(self, request):
        """A group mark does nothing unless the run distributes by group."""
        addopts = request.config.getini("addopts")
        assert ["--dist", "loadgroup"] in [addopts[i : i + 2] for i in range(len(addopts))]


@pytest.fixture(scope="module")
def result(cpo_result) -> cpo.Result:
    """One full run of Example 7.1, or a skip naming what is missing.

    ``tests/conftest.py`` holds the run and its skip, so this file and
    ``tests/test_cpo_figures.py`` read one run rather than paying for two.
    """
    return cpo_result


class TestExample71OnTheArchive:
    """Rows 1 to 11 of Entry 16, all from one run, and three figures its post quotes.

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

    # The four pins below were added for the post on this example,
    # blog/conditional-parameter-optimization-lessons.md, so that every figure
    # it quotes traces to an assertion rather than to prose. Entry 16 names them.

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
        """p. 140. A short exits at 0.55 under −0.6 and would hold under −0.5."""
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
