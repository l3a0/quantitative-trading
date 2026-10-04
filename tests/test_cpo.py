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
"""

from __future__ import annotations

import math
import os

import numpy as np
import pandas as pd
import pytest

from chan import cpo
from chan.archive import ArchiveUnavailable, archive_dir
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

#: Set to 1 to run the pins below. The full run takes minutes, and every
#: session here runs the suite, so they do not run by default.
RUN_ENV = "QT_ARCHIVE_RUN"


@pytest.fixture(scope="module")
def result() -> cpo.Result:
    """One full run of Example 7.1, or a skip naming what is missing."""
    try:
        archive_dir()
    except ArchiveUnavailable as absent:
        pytest.skip(str(absent))
    if os.environ.get(RUN_ENV) != "1":
        pytest.skip(f"the archive pins take minutes, so they run only with {RUN_ENV}=1")
    return cpo.run()


class TestExample71OnTheArchive:
    """Rows 1 to 11 of Entry 16, all from one run.

    The vintages are the archive's `gld_intraday_1min.csv.gz`, sha256
    `3611a8f7…0de7a`, downloaded 2026-07-17, and `gdx_intraday_1min.csv.gz`,
    sha256 `c47f5890…711c`, downloaded 2026-10-03, both Alpha Vantage at
    `adjusted=false`. The specification is the 19 readings declared on issue 23
    before any return was computed, with scikit-learn 1.9.1 and `ta` 0.11.0 as
    `uv.lock` fixes them. A lock update that moves either can move rows 5 to 10.
    """

    def test_row_11_the_span_and_the_split(self, result):
        assert result.days[0] == pd.Timestamp("2006-05-22")
        assert result.days[-1] == pd.Timestamp("2020-12-31")
        assert len(result.days) == 3680
        assert result.n_train == 2944
        assert result.test_days[0] == pd.Timestamp("2018-01-31")
        assert len(result.test_days) == 736

    def test_the_unconditional_cell_is_the_busiest_corner_of_the_grid(self, result):
        """The smallest weight, the shortest lookback and the lowest entry threshold."""
        assert result.unconditional == Cell(2.0, 0.2, 30)

    def test_rows_1_to_4_the_unconditional_figures_and_their_gaps(self, result):
        got = metrics(result.unconditional_returns)
        assert got["cumulative"] == pytest.approx(3.5483992546508443, abs=1e-9)
        assert got["annual"] == pytest.approx(0.6797515757890611, abs=1e-9)
        assert got["sharpe"] == pytest.approx(5.790924881105733, abs=1e-9)
        assert got["calmar"] == pytest.approx(15.676071316831976, abs=1e-8)
        # At Chan's printed precision, every gap is positive and large.
        assert round(got["cumulative"], 2) - 0.73 == pytest.approx(2.82)
        assert round(got["annual"], 4) - 0.1729 == pytest.approx(0.5069)
        assert round(got["sharpe"], 3) - 1.947 == pytest.approx(3.844)
        assert round(got["calmar"], 3) - 0.984 == pytest.approx(14.692)

    def test_row_5_chan_s_claim_does_not_hold(self, result):
        """Conditional wins on Sharpe and Calmar and loses on both returns."""
        unconditional = metrics(result.unconditional_returns)
        conditional = metrics(result.conditional_returns)
        better = {name for name in cpo.METRICS if conditional[name] > unconditional[name]}
        assert better == {"sharpe", "calmar"}
        assert not claim_holds(unconditional, conditional)

    def test_row_6_the_conditional_figures_beside_chan_s(self, result):
        got = metrics(result.conditional_returns)
        assert got["cumulative"] == pytest.approx(3.47958438490497, abs=1e-9)
        assert got["annual"] == pytest.approx(0.6710064763877099, abs=1e-9)
        assert got["sharpe"] == pytest.approx(5.915820233948008, abs=1e-9)
        assert got["calmar"] == pytest.approx(16.604331193405503, abs=1e-8)

    def test_row_6_the_conditional_arm_mostly_keeps_the_unconditional_cell(self, result):
        chosen = result.conditional_cells
        unconditional = cells().index(result.unconditional)
        assert int((chosen == unconditional).sum()) == 489
        assert len(set(chosen.tolist())) == 47
        assert int((np.diff(chosen) != 0).sum()) == 362

    def test_row_7_the_arithmetic_annual_returns(self, result):
        assert metrics(result.unconditional_returns)["arithmetic_annual"] == pytest.approx(
            0.5232361584088379, abs=1e-9
        )
        assert metrics(result.conditional_returns)["arithmetic_annual"] == pytest.approx(
            0.5177468750046424, abs=1e-9
        )

    def test_row_8_one_basis_point_a_round_trip_turns_both_arms_to_losses(self, result):
        unconditional = metrics(costed(result.unconditional_returns, result.unconditional_trips))
        conditional = metrics(costed(result.conditional_returns, result.conditional_trips))
        assert unconditional["sharpe"] == pytest.approx(-7.468491852898375, abs=1e-9)
        assert unconditional["cumulative"] == pytest.approx(-0.8549535316680085, abs=1e-9)
        assert conditional["sharpe"] == pytest.approx(-5.657835189746311, abs=1e-9)
        assert conditional["cumulative"] == pytest.approx(-0.7730746556456858, abs=1e-9)

    def test_row_9_round_trips_a_day(self, result):
        assert result.unconditional_trips.mean() == pytest.approx(46.80842391304348, abs=1e-9)
        assert result.conditional_trips.mean() == pytest.approx(40.52038043478261, abs=1e-9)

    def test_row_10_where_chan_s_sharpe_sits_among_the_400_cells(self, result):
        """Added after the result was seen. It locates the gap and decides nothing."""
        sharpes = result.cell_sharpes
        assert sharpes.min() == pytest.approx(0.8123231655061941, abs=1e-9)
        assert float(np.median(sharpes)) == pytest.approx(3.5161777010537194, abs=1e-9)
        assert sharpes.max() == pytest.approx(5.963635026095906, abs=1e-9)
        assert int((sharpes < 1.947).sum()) == 38
        nearest = int(np.argmin(np.abs(sharpes - 1.947)))
        assert cells()[nearest].label == "3_60_2.5"
        assert result.cell_trips[nearest] == pytest.approx(1.2, abs=0.05)
