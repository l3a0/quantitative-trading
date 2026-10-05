"""The pins for EWA, EWC and IGE, *Algorithmic Trading*'s Examples 2.6 to 2.8.

This file is the single authority for every number a prose surface quotes
about these three examples and the rows beside them. ``docs/replication-log.md``
Entry 21 carries the verdicts and points here row by row.

Every pin on the committed file reads one vintage and one specification, so
both are stated once here.

- **Vintage.** ``inputdata_etf/ewa.csv``, ``ewc.csv`` and ``ige.csv``, lifted
  from Chan's ``inputData_ETF.mat``, chan-mat, adjusted by subtracting each
  dividend in dollars, saved 2012-04-10, 1,500 trading days from 2006-04-26 to
  2012-04-09, read for the close through ``chan.series.load_panel``. Its
  identity is that file's row of ``LIFTED_SOURCES`` in
  ``tests/support/committed_vintages.py``.
- **Specification.** ``cointegrationTests.m`` at EpchanPreview ``e4bc46f``,
  as :mod:`chan.etf_cointegration` transcribes it. ``cadf(EWC, EWA, 0, 1)``,
  which is ``lesage_cadf`` with one lag. ``johansen(·, 0, 1)``, a constant and
  one lagged difference, on columns EWC, EWA and then IGE. The portfolio is
  the triplet's first eigenvector, its half-life comes from a regression with
  an intercept, and the strategy's lookback is that half-life rounded half
  away from zero. Returns are annualised over 252 days with no risk-free rate
  and no cost, and the deviation divides by n − 1.

Each published figure is held twice: at the computed value's own precision,
which is what lets the log quote it, and at the precision Chan printed,
through ``matches``.

Exploratory. Reproducing Chan's figures spends the 2006 to 2012 sample on a
portfolio he chose, fitted on the days it trades. All three examples first ran
on 2026-10-05.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from ithildincore.timeseries import EG_CRIT_N2

from chan import etf_cointegration as module
from chan import paths
from chan.etf_cointegration import (
    BOOK_APR_PERCENT,
    BOOK_CADF_T,
    BOOK_HALF_LIFE_DAYS,
    BOOK_SHARPE,
    PAIR,
    SCRIPT_APR,
    SCRIPT_CADF_AR1,
    SCRIPT_CADF_CRITICAL,
    SCRIPT_CADF_T,
    SCRIPT_EIGENVALUES,
    SCRIPT_EIGENVECTORS,
    SCRIPT_HALF_LIFE,
    SCRIPT_PAIR_EIGEN,
    SCRIPT_PAIR_EIGEN_CRITICAL,
    SCRIPT_PAIR_TRACE,
    SCRIPT_PAIR_TRACE_CRITICAL,
    SCRIPT_SHARPE,
    SCRIPT_TRIPLET_EIGEN,
    SCRIPT_TRIPLET_EIGEN_CRITICAL,
    SCRIPT_TRIPLET_TRACE,
    SCRIPT_TRIPLET_TRACE_CRITICAL,
    SOURCE_FILE,
    TRIPLET,
    EtfCointegration,
    etf_cointegration,
    linear_mean_reversion,
    main,
    portfolio_value,
    read_sources,
    run,
    strategy,
)
from chan.johansen import johansen
from chan.khandani_lo_book_two import matches
from chan.matlab_helpers import moving_avg, moving_std
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import LIFTED_SOURCES


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def result(sources) -> EtfCointegration:
    return etf_cointegration(sources[1])


@pytest.fixture(scope="module")
def triplet(sources) -> np.ndarray:
    return sources[1][list(TRIPLET)].to_numpy(dtype=float)


@pytest.fixture
def no_arguments(monkeypatch):
    """``main`` parses ``sys.argv``, which under pytest holds pytest's own arguments."""
    monkeypatch.setattr("sys.argv", ["chan.etf_cointegration"])


def _printed(rows) -> np.ndarray:
    return np.array([[float(cell) for cell in row] for row in rows])


class TestTheVintage:
    def test_the_three_members_are_the_pinned_source(self, sources) -> None:
        members, closes = sources
        vendor, basis, saved, folder, _ = LIFTED_SOURCES[SOURCE_FILE]
        assert {(m.vendor, m.price_basis, m.obtained) for m in members} == {(vendor, basis, saved)}
        assert sorted(m.path for m in members) == [
            f"{folder}/ewa.csv",
            f"{folder}/ewc.csv",
            f"{folder}/ige.csv",
        ]
        assert list(closes.columns) == ["EWA", "EWC", "IGE"]

    def test_the_window_is_the_whole_file_with_no_price_missing(self, sources) -> None:
        closes = sources[1]
        assert len(closes) == 1500
        assert str(closes.index[0].date()) == "2006-04-26"
        assert str(closes.index[-1].date()) == "2012-04-09"
        assert np.isfinite(closes.to_numpy()).all()

    def test_the_script_orders_the_columns_ewc_ewa_ige(self) -> None:
        """``y2 = [y, x]``, so every eigenvector row follows this order, not the title's."""
        assert PAIR == ("EWC", "EWA")
        assert TRIPLET == ("EWC", "EWA", "IGE")


class TestExample26TheCadfTest:
    """Rows 1 to 3: ``cadf(EWC, EWA, 0, 1)`` and the claim location 1292 makes."""

    def test_row_1_the_t_statistic(self, result) -> None:
        assert result.cadf.t == pytest.approx(-3.6434663489, abs=1e-10)
        assert matches(result.cadf.t, SCRIPT_CADF_T)
        assert matches(result.cadf.t, BOOK_CADF_T)

    def test_row_2_the_ar1_estimate_and_the_observations(self, result) -> None:
        assert result.cadf.ar1 == pytest.approx(-0.0204108120, abs=1e-10)
        assert matches(result.cadf.ar1, SCRIPT_CADF_AR1)
        assert result.cadf.nobs == 1498

    def test_row_3_the_pair_cointegrates_at_95_percent(self, result) -> None:
        """Past jplv7's −3.359, which is quoted, and not past its −3.880 at 99."""
        one, five, ten = (float(v) for v in SCRIPT_CADF_CRITICAL)
        assert (one, five, ten) == (-3.880, -3.359, -3.038)
        assert one < result.cadf.t < five
        assert result.cadf.t < EG_CRIT_N2["5%"] == -3.34


class TestExample27TheJohansenTest:
    """Rows 4 to 11, with each critical value the script prints."""

    def test_row_4_the_pair_trace_statistics(self, result) -> None:
        np.testing.assert_allclose(result.pair.trace, [19.983219, 3.982761], atol=1e-6)
        assert all(map(matches, result.pair.trace, SCRIPT_PAIR_TRACE))

    def test_row_5_the_pair_eigen_statistics(self, result) -> None:
        np.testing.assert_allclose(result.pair.eigen, [16.000457, 3.982761], atol=1e-6)
        assert all(map(matches, result.pair.eigen, SCRIPT_PAIR_EIGEN))

    def test_row_7_the_triplet_trace_statistics(self, result) -> None:
        np.testing.assert_allclose(
            result.triplet.trace, [34.428620, 17.531719, 4.471021], atol=1e-6
        )
        assert all(map(matches, result.triplet.trace, SCRIPT_TRIPLET_TRACE))

    def test_row_8_the_triplet_eigen_statistics(self, result) -> None:
        np.testing.assert_allclose(
            result.triplet.eigen, [16.896901, 13.060698, 4.471021], atol=1e-6
        )
        assert all(map(matches, result.triplet.eigen, SCRIPT_TRIPLET_EIGEN))

    @pytest.mark.parametrize(
        ("which", "statistic", "printed"),
        [
            ("pair", "trace", SCRIPT_PAIR_TRACE_CRITICAL),
            ("pair", "eigen", SCRIPT_PAIR_EIGEN_CRITICAL),
            ("triplet", "trace", SCRIPT_TRIPLET_TRACE_CRITICAL),
            ("triplet", "eigen", SCRIPT_TRIPLET_EIGEN_CRITICAL),
        ],
    )
    def test_every_critical_value_is_the_one_printed(self, result, which, statistic, printed):
        computed = getattr(getattr(result, which), f"{statistic}_critical")
        assert computed.shape == (len(printed), 3)
        # LeSage's tables hold four decimals, such as 2.7055, and prt printed
        # three. Formatting reproduces the printout. round() on a numpy float
        # scales and rounds half to even, which gives 2.706 instead.
        for row, row_printed in zip(computed, printed, strict=True):
            assert [f"{value:.3f}" for value in row] == list(row_printed)

    def test_row_10_the_triplet_eigenvalues(self, result) -> None:
        np.testing.assert_allclose(
            result.triplet.eigenvalues, [0.01121626, 0.00868086, 0.00298021], atol=1e-8
        )
        assert all(map(matches, result.triplet.eigenvalues, SCRIPT_EIGENVALUES))

    def test_row_11_the_eigenvectors_are_chans_with_every_sign_flipped(self, result) -> None:
        """statsmodels makes the top-left element positive, and MATLAB gave −1.0460 there."""
        printed = _printed(SCRIPT_EIGENVECTORS)
        np.testing.assert_allclose(result.triplet.eigenvectors, -printed, atol=5e-5)
        assert not np.allclose(result.triplet.eigenvectors, printed, atol=5e-5)
        assert result.triplet.eigenvectors[0, 0] == pytest.approx(1.04602749, abs=1e-8)

    def test_row_12_the_half_life(self, result) -> None:
        assert result.strategy.half_life == pytest.approx(22.6625778505, abs=1e-9)
        assert matches(result.strategy.half_life, SCRIPT_HALF_LIFE)
        assert matches(result.strategy.half_life, BOOK_HALF_LIFE_DAYS)


class TestTheClaims:
    """Rows 3, 6 and 9 read each test's relations through its critical values."""

    def test_row_6_both_tests_find_two_relations_for_the_pair_at_95(self, result) -> None:
        assert result.pair.relations("trace", 95) == 2
        assert result.pair.relations("eigen", 95) == 2

    def test_row_6_the_trace_rejects_r_le_0_at_99_and_the_eigen_does_not(self, result) -> None:
        """Location 1324 says the trace's r = 0 falls at 99 and the eigen's at 95."""
        assert result.pair.trace[0] > result.pair.trace_critical[0, 2]
        assert result.pair.eigen[0] < result.pair.eigen_critical[0, 2]
        assert result.pair.relations("trace", 99) == 1

    def test_row_6_the_pairs_second_relation_clears_its_bar_by_0_141(self, result) -> None:
        margin = result.pair.trace[1] - result.pair.trace_critical[1, 1]
        assert margin == pytest.approx(0.141261, abs=1e-6)

    def test_row_9_the_trace_test_finds_three_relations_at_95(self, result) -> None:
        assert result.triplet.relations("trace", 95) == 3

    def test_row_9_the_eigen_test_finds_none_even_at_90(self, result) -> None:
        """16.897 is short of 18.893, so location 1337's "Both" does not survive."""
        assert result.triplet.eigen[0] < result.triplet.eigen_critical[0, 0]
        assert [result.triplet.relations("eigen", level) for level in (90, 95, 99)] == [0, 0, 0]


class TestExample28TheStrategy:
    """Rows 13 and 14, and how the strategy gets there."""

    def test_row_13_the_apr(self, result) -> None:
        assert result.strategy.apr == pytest.approx(0.1257386810, abs=1e-10)
        assert matches(result.strategy.apr, SCRIPT_APR)
        assert matches(100 * result.strategy.apr, BOOK_APR_PERCENT)

    def test_row_14_the_sharpe_ratio(self, result) -> None:
        assert result.strategy.sharpe == pytest.approx(1.3913100883, abs=1e-10)
        assert matches(result.strategy.sharpe, SCRIPT_SHARPE)
        assert matches(result.strategy.sharpe, BOOK_SHARPE)

    def test_the_lookback_is_the_half_life_rounded(self, result) -> None:
        assert result.strategy.lookback == 23

    def test_the_weights_are_the_first_eigenvector(self, result) -> None:
        np.testing.assert_array_equal(result.strategy.weights, result.triplet.eigenvectors[:, 0])

    def test_the_first_return_is_on_row_23_and_every_later_day_has_one(self, result) -> None:
        """The moving deviation fills on row 22 and positions earn from the next row."""
        nonzero = np.flatnonzero(result.strategy.daily)
        assert nonzero[0] == 23
        assert str(result.days[23].date()) == "2006-05-30"
        assert len(nonzero) == 1477 == 1500 - 23
        assert len(result.strategy.daily) == 1500

    def test_negating_the_eigenvector_moves_nothing(self, triplet, result) -> None:
        """Chan's sign gives the same half-life, lookback and every day's return."""
        flipped = strategy(triplet, -result.strategy.weights)
        assert flipped.half_life == pytest.approx(result.strategy.half_life, abs=1e-9)
        assert flipped.lookback == result.strategy.lookback
        np.testing.assert_allclose(flipped.daily, result.strategy.daily, atol=1e-15)

    def test_zero_padding_the_lag_as_lesage_does_gives_the_same_series(self, triplet, result):
        """The first row divides by a zero price, so it is not a number and becomes 0."""
        weights = result.strategy.weights
        value = portfolio_value(triplet, weights)
        lookback = result.strategy.lookback
        with np.errstate(invalid="ignore", divide="ignore"):
            units = -(value - moving_avg(value, lookback)) / moving_std(value, lookback)
            positions = units[:, None] * weights[None, :] * triplet
            held = np.vstack([np.zeros((1, 3)), positions[:-1]])
            before = np.vstack([np.zeros((1, 3)), triplet[:-1]])
            pnl = np.sum(held * (triplet - before) / before, axis=1)
            daily = pnl / np.sum(np.abs(held), axis=1)
        assert np.isnan(daily[0])
        np.testing.assert_array_equal(np.where(np.isnan(daily), 0.0, daily), result.strategy.daily)


class TestTheRule:
    """The strategy's lines on series built by hand."""

    def test_a_portfolio_is_each_price_times_its_weight_summed(self) -> None:
        prices = np.array([[10.0, 20.0], [11.0, 19.0]])
        np.testing.assert_array_equal(portfolio_value(prices, np.array([1.0, -0.5])), [0.0, 1.5])

    def test_the_rows_before_the_window_fills_earn_nothing(self) -> None:
        prices = np.column_stack([np.linspace(10, 20, 12), np.linspace(20, 10, 12) + [0, 1] * 6])
        daily = linear_mean_reversion(prices, np.array([1.0, 1.0]), 4)
        assert (daily[:4] == 0).all()
        assert (daily[4:] != 0).any()

    def test_a_portfolio_above_its_average_is_sold(self) -> None:
        """The last price jumps, so the units go negative and the next rise loses."""
        one = np.r_[np.full(5, 10.0) + [0, 0.1, -0.1, 0.1, -0.1], 12.0, 13.0]
        prices = np.column_stack([one, np.full(7, 5.0)])
        daily = linear_mean_reversion(prices, np.array([1.0, 0.0]), 3)
        assert daily[6] < 0

    def test_a_portfolio_that_does_not_revert_is_refused_by_name(self) -> None:
        """``ou_half_life`` gives infinity here, which ``int`` would refuse with no reason."""
        trend = np.column_stack([np.exp(np.linspace(0, 1, 50)), np.ones(50)])
        with pytest.raises(ValueError, match="does not revert"):
            strategy(trend, np.array([1.0, 0.0]))

    def test_a_day_with_no_gross_is_zero_rather_than_nan(self) -> None:
        """A weight of 0 everywhere leaves the gross at 0 and 0 / 0 at NaN, set to 0."""
        prices = np.column_stack([np.linspace(1, 2, 8), np.linspace(2, 3, 8)])
        assert (linear_mean_reversion(prices, np.zeros(2), 3) == 0).all()


class TestBesideTheReplication:
    """No book prints these, so none carries a verdict."""

    def test_the_hedge_ratio_feeds_only_the_figure(self, result) -> None:
        assert result.hedge_ratio == pytest.approx(0.9624293987, abs=1e-10)

    def test_reversing_the_legs_moves_the_statistic_and_not_the_verdict(self, result) -> None:
        """Location 1282 says the result differs. It does, by 0.0029, past −3.359 both ways."""
        assert result.reversed_cadf.t == pytest.approx(-3.6405421403, abs=1e-10)
        assert result.reversed_cadf.t - result.cadf.t == pytest.approx(0.002924, abs=1e-6)
        assert result.reversed_cadf.t < float(SCRIPT_CADF_CRITICAL[1])

    def test_reordering_the_columns_leaves_every_statistic(self, result) -> None:
        """Location 1324 says the Johansen test does not depend on the order."""
        for statistic in ("trace", "eigen", "eigenvalues"):
            np.testing.assert_allclose(
                getattr(result.reordered_triplet, statistic),
                getattr(result.triplet, statistic),
                atol=1e-11,
            )

    def test_reordering_permutes_the_vectors_rows_up_to_sign(self, result) -> None:
        reordered = result.reordered_triplet.eigenvectors[[1, 0, 2]]
        signs = np.sign(reordered[0] / result.triplet.eigenvectors[0])
        np.testing.assert_allclose(reordered * signs, result.triplet.eigenvectors, atol=1e-10)
        assert list(signs) == [-1, -1, 1]

    def test_the_first_eigenvector_reverts_fastest(self, result) -> None:
        """Location 1340 expects the half-lives to rise as the eigenvalues fall."""
        np.testing.assert_allclose(
            result.eigenvector_half_lives, [22.662578, 43.731678, 151.546826], atol=1e-6
        )
        assert list(result.eigenvector_half_lives) == sorted(result.eigenvector_half_lives)

    def test_no_etf_alone_rejects_a_unit_root_even_at_90(self, result) -> None:
        """A plain ADF with a constant and one lag, against MacKinnon's −2.57.

        The pair's Johansen rank of 2 says each series is stationary around a
        constant. These three say none is, which is what makes row 6's reading
        fragile rather than wrong.
        """
        assert result.adf == pytest.approx(
            {"EWA": -1.863334, "EWC": -1.901877, "IGE": -2.078705}, abs=1e-6
        )
        assert all(t > -2.57 for t in result.adf.values())

    def test_the_pair_is_tested_as_ewc_then_ewa(self, sources, result) -> None:
        """The statistics do not depend on the order, so the eigenvector rows are what show it."""
        closes = sources[1]
        script_order = johansen(closes[["EWC", "EWA"]].to_numpy(dtype=float))
        np.testing.assert_allclose(script_order.eigenvectors, result.pair.eigenvectors, atol=1e-10)
        swapped = johansen(closes[["EWA", "EWC"]].to_numpy(dtype=float))
        assert not np.allclose(np.abs(swapped.eigenvectors), np.abs(result.pair.eigenvectors))


class TestTheGuardAndTheReads:
    def test_read_sources_runs_the_guard_on_the_three_over_the_whole_file(
        self, monkeypatch
    ) -> None:
        seen = []

        def record(legs, *, start, end):
            seen.append(([entry.symbol for entry, _ in legs], start, end))

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", record)
        read_sources()
        assert seen == [
            (["EWA", "EWC", "IGE"], pd.Timestamp("2006-04-26"), pd.Timestamp("2012-04-09"))
        ]

    def test_a_refusal_from_the_guard_reaches_the_caller(self, monkeypatch) -> None:
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("flagged")

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(WindowCrossesScaleBreak, match="flagged"):
            run()

    def test_main_turns_a_guard_refusal_into_one_line(self, monkeypatch, no_arguments):
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("inputdata_etf/ewa.csv changes scale on 2008-01-02")

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(SystemExit, match="ewa.csv changes scale on 2008-01-02"):
            main()

    def test_run_reads_the_directory_it_is_given(self, tmp_path) -> None:
        with pytest.raises(VintageUnavailable, match="inputData_ETF.mat"):
            run(tmp_path)

    def test_main_turns_a_missing_vintage_into_one_line(
        self, monkeypatch, tmp_path, no_arguments
    ) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit, match="inputData_ETF.mat"):
            main()

    def test_the_report_marks_every_printed_figure_reproduced(self, capsys, no_arguments):
        main()
        out = capsys.readouterr().out
        figures = [line for line in out.splitlines() if line.startswith("  2.")]
        assert len(figures) == 18
        assert all(line.endswith("reproduced") for line in figures)
        assert "did not reproduce" not in out
        assert "triplet eigen  0 at 90%, 0 at 95%, 0 at 99%" in out
        assert "Exploratory." in out
