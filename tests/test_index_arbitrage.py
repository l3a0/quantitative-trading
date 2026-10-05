"""The pins for SPY against the S&P 500 stocks, *Algorithmic Trading*'s Example 4.2.

This file is the single authority for every number a prose surface quotes
about this example and the rows beside it. ``docs/replication-log.md`` Entry 24
carries the verdicts and points here row by row.

Every pin on the committed files reads one vintage and one specification, so
both are stated once here.

- **Vintage.** ``inputdataohlcdaily_stocks_20120424/``, 497 members lifted
  from Chan's ``inputDataOHLCDaily_stocks_20120424.mat``, chan-mat, adjusted,
  saved 2012-04-25, closes only. ``inputdata_etf/spy.csv``, lifted from
  ``inputData_ETF.mat``, chan-mat, adjusted by subtracting each dividend in
  dollars, saved 2012-04-10. Both are read for the close through
  ``chan.series.load_panel``, and their 1,489 common days run from 2006-05-11
  to 2012-04-09. Each file's identity is its row of ``LIFTED_SOURCES`` in
  ``tests/support/committed_vintages.py``.
- **Specification.** ``indexArb.m``, git blob ``dcb079a``, at EpchanPreview
  ``e4bc46f``, as :mod:`chan.index_arbitrage` transcribes it. A screen in
  prices over 2007 with ``johansen(·, 0, 1)``, more than 250 rows and the
  trace statistic for r ≤ 0 above its 90 percent value. A basket in log prices
  tested the same way, its first eigenvector, a lookback of 5 with
  ``movingAvg`` and an n − 1 ``movingStd``, positions in dollars and log
  returns. Returns are annualised over 252 days with a compounded APR, no
  risk-free rate and no cost.

Each published figure is held twice: at the computed value's own precision,
which is what lets the log quote it, and at the precision Chan printed,
through ``matches``.

Exploratory, survivor-only, and in-sample on the lookback. Reproducing Chan's
figures spends the 2007 to 2012 sample on a rule he chose, the panel holds only
stocks that survived to 2012, and location 2035 says the lookback of 5 was
chosen with hindsight. The example first ran on 2026-10-05.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from chan import index_arbitrage as module
from chan import paths
from chan.index_arbitrage import (
    BOOK_APR_PERCENT,
    BOOK_SHARPE,
    BOOK_TEST_END,
    BOOK_TEST_START,
    ETF_FILE,
    FEWEST_ROWS,
    INDEX,
    LOOKBACK,
    SCRIPT_APR,
    SCRIPT_EIGEN,
    SCRIPT_EIGEN_CRITICAL,
    SCRIPT_EIGENVECTORS,
    SCRIPT_PASSED,
    SCRIPT_SHARPE,
    SCRIPT_TRACE,
    SCRIPT_TRACE_CRITICAL,
    STOCK_FILE,
    IndexArbitrage,
    basket_value,
    common_days,
    index_arbitrage,
    index_arbitrage_returns,
    instrument_weights,
    main,
    read_sources,
    run,
    screen,
    windows,
)
from chan.johansen import johansen
from chan.khandani_lo_book_two import matches
from chan.matlab_helpers import moving_avg, moving_std, smartsum
from chan.series import WindowCrossesScaleBreak, refuse_window_crossing_a_break, scale_breaks
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import LIFTED_SOURCES

SPEC = "indexArb.m at blob dcb079a on the 2012 S&P 500 file and the ETF file's SPY"

#: The 17 stocks line 26 skips, with the 2007 rows each keeps.
SKIPPED = {
    "CFN": 0,
    "COV": 139,
    "DFS": 139,
    "DPS": 0,
    "LO": 0,
    "MJN": 0,
    "MMI": 0,
    "MPC": 0,
    "PCS": 178,
    "PM": 0,
    "QEP": 0,
    "SNI": 0,
    "TDC": 64,
    "TEL": 139,
    "TWC": 246,
    "V": 0,
    "XYL": 0,
}


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def result(sources) -> IndexArbitrage:
    return index_arbitrage(sources[2], sources[3])


@pytest.fixture(scope="module")
def held(sources, result) -> np.ndarray:
    """Line 66's ``yNplus``: the basket's test closes, then SPY's."""
    stocks, index = sources[2], sources[3]
    test = stocks.index.isin(result.test_days)
    return np.column_stack(
        [stocks.loc[test, list(result.screen.passed)].to_numpy(), index.loc[test].to_numpy()]
    )


@pytest.fixture
def no_arguments(monkeypatch):
    """``main`` parses ``sys.argv``, which under pytest holds pytest's own arguments."""
    monkeypatch.setattr("sys.argv", ["chan.index_arbitrage"])


def _printed(rows) -> np.ndarray:
    return np.array([[float(cell) for cell in row] for row in rows])


class TestTheVintage:
    def test_the_stocks_are_the_pinned_source(self, sources) -> None:
        stock_members = sources[0]
        vendor, basis, saved, folder, count = LIFTED_SOURCES[STOCK_FILE]
        assert {(m.vendor, m.price_basis, m.obtained) for m in stock_members} == {
            (vendor, basis, saved)
        }
        assert len(stock_members) == count == 497
        assert all(m.path.startswith(f"{folder}/") for m in stock_members)

    def test_spy_is_the_etf_files_spy(self, sources) -> None:
        spy = sources[1]
        vendor, basis, saved, folder, _ = LIFTED_SOURCES[ETF_FILE]
        assert (spy.vendor, spy.price_basis, spy.obtained) == (vendor, basis, saved)
        assert spy.path == f"{folder}/spy.csv"

    def test_the_common_days_are_1489_from_2006_05_11_to_2012_04_09(self, sources) -> None:
        stocks, index = sources[2], sources[3]
        assert len(stocks) == len(index) == 1489
        assert (str(stocks.index[0].date()), str(stocks.index[-1].date())) == (
            "2006-05-11",
            "2012-04-09",
        )
        assert stocks.index.equals(index.index)
        assert stocks.index.is_monotonic_increasing

    def test_the_two_calendars_agree_on_every_day_of_their_overlap(self) -> None:
        """Neither file holds a day inside the overlap that the other lacks."""
        stocks = module.load_panel(STOCK_FILE)[1].index
        etf = module.load_panel(ETF_FILE)[1].index
        lo, hi = max(stocks[0], etf[0]), min(stocks[-1], etf[-1])
        inside = lambda days: days[(days >= lo) & (days <= hi)]  # noqa: E731
        assert inside(stocks).equals(inside(etf))
        assert len(stocks) == len(etf) == 1500

    def test_spy_and_every_tested_stock_are_priced_on_every_day_they_are_read(
        self, sources, result
    ) -> None:
        stocks, index = sources[2], sources[3]
        assert np.isfinite(index.to_numpy()).all()
        read = stocks.index >= result.train_days[0]
        assert np.isfinite(stocks.loc[read, list(result.screen.tested)].to_numpy()).all()


class TestRow1TheWindows:
    def test_row_1_the_test_window_is_the_books(self, result) -> None:
        assert (result.test_days[0], result.test_days[-1]) == (BOOK_TEST_START, BOOK_TEST_END)
        assert len(result.test_days) == 1076

    def test_training_is_the_251_days_of_2007(self, result) -> None:
        assert str(result.train_days[0].date()) == "2007-01-03"
        assert str(result.train_days[-1].date()) == "2007-12-31"
        assert len(result.train_days) == 251


class TestRow2TheScreen:
    def test_row_2_98_stocks_pass(self, result) -> None:
        assert len(result.screen.passed) == SCRIPT_PASSED == 98, SPEC

    def test_480_are_tested(self, result) -> None:
        """Each at a per-test 90 percent bar, which ``TestBesideTheReplication`` sizes."""
        assert len(result.screen.tested) == 480
        assert set(result.screen.passed) <= set(result.screen.tested)

    def test_the_17_skipped_are_the_11_with_no_2007_close_and_6_listed_during_it(
        self, result
    ) -> None:
        assert result.screen.skipped == SKIPPED
        assert sum(rows == 0 for rows in SKIPPED.values()) == 11
        assert len(result.screen.tested) + len(SKIPPED) == 497

    def test_the_six_partial_stocks_list_during_2007_and_never_miss_a_close_after(
        self, sources, result
    ) -> None:
        """Each holds one unbroken run of closes from its first 2007 day onward."""
        stocks = sources[2]
        partial = sorted(s for s, rows in SKIPPED.items() if rows)
        assert partial == ["COV", "DFS", "PCS", "TDC", "TEL", "TWC"]
        for symbol in partial:
            closes = stocks[symbol]
            first = closes.first_valid_index()
            assert result.train_days[0] < first <= result.train_days[-1], symbol
            assert closes.loc[first:].notna().all(), symbol
            assert closes.loc[first : result.train_days[-1]].count() == SKIPPED[symbol]

    def test_the_rule_admits_exactly_the_stocks_priced_on_all_251_days(self, result) -> None:
        assert max(result.screen.skipped.values()) == 246 < FEWEST_ROWS


class TestTheBasketTest:
    """Rows 3, 4 and 7, with each critical value the script prints."""

    def test_row_3_the_trace_statistics(self, result) -> None:
        np.testing.assert_allclose(result.basket.trace, [15.868648, 6.197357], atol=1e-6)
        assert all(map(matches, result.basket.trace, SCRIPT_TRACE))

    def test_row_4_the_eigen_statistics(self, result) -> None:
        np.testing.assert_allclose(result.basket.eigen, [9.671291, 6.197357], atol=1e-6)
        assert all(map(matches, result.basket.eigen, SCRIPT_EIGEN))

    @pytest.mark.parametrize(
        ("statistic", "printed"),
        [("trace", SCRIPT_TRACE_CRITICAL), ("eigen", SCRIPT_EIGEN_CRITICAL)],
    )
    def test_every_critical_value_is_the_one_printed(self, result, statistic, printed) -> None:
        computed = getattr(result.basket, f"{statistic}_critical")
        assert computed.shape == (2, 3)
        # LeSage's tables hold four decimals, such as 2.7055, and prt printed
        # three. Formatting reproduces the printout, where matches would round
        # to 2.706.
        for row, row_printed in zip(computed, printed, strict=True):
            assert [f"{value:.3f}" for value in row] == list(row_printed)

    def test_row_7_the_eigenvectors_are_chans_with_his_signs(self, result) -> None:
        """statsmodels makes the top-left element positive, and Chan's 1.0939 already is."""
        printed = _printed(SCRIPT_EIGENVECTORS)
        np.testing.assert_allclose(result.basket.eigenvectors, printed, atol=5e-5)
        np.testing.assert_allclose(
            result.basket.eigenvectors,
            [[1.09386171, -0.27989806], [-105.55999232, 56.09328286]],
            atol=1e-8,
        )
        for row, row_printed in zip(result.basket.eigenvectors, SCRIPT_EIGENVECTORS, strict=True):
            assert all(map(matches, row, row_printed))

    def test_the_eigenvalues(self, result) -> None:
        np.testing.assert_allclose(result.basket.eigenvalues, [0.03809590, 0.02458181], atol=1e-8)


class TestTheClaims:
    """Rows 5 and 6, each read for the trace and the eigen test separately."""

    def test_row_5_the_trace_rejects_r_le_0_at_95(self, result) -> None:
        """15.869 is past 15.494, by 0.374."""
        assert result.basket.trace[0] > result.basket.trace_critical[0, 1]
        margin = result.basket.trace[0] - result.basket.trace_critical[0, 1]
        assert margin == pytest.approx(0.374348, abs=1e-6)

    def test_row_5_the_eigen_does_not_reject_r_le_0_even_at_90(self, result) -> None:
        """9.671 is short of 12.297, so only the trace half of "better than 95" holds."""
        assert result.basket.eigen[0] < result.basket.eigen_critical[0, 0]

    def test_row_6_the_trace_counts_two_relations_at_95(self, result) -> None:
        assert [result.basket.relations("trace", level) for level in (90, 95, 99)] == [2, 2, 0]

    def test_row_6_the_eigen_counts_none_at_any_level(self, result) -> None:
        assert [result.basket.relations("eigen", level) for level in (90, 95, 99)] == [0, 0, 0]


class TestTheStrategy:
    """Rows 8 and 9, and how the strategy gets there."""

    def test_row_8_the_apr(self, result) -> None:
        assert result.apr == pytest.approx(0.0449298745, abs=1e-10)
        assert matches(result.apr, SCRIPT_APR)
        assert matches(100 * result.apr, BOOK_APR_PERCENT)

    def test_row_9_the_sharpe_ratio(self, result) -> None:
        assert result.sharpe == pytest.approx(1.3193972970, abs=1e-10)
        assert matches(result.sharpe, SCRIPT_SHARPE)
        assert matches(result.sharpe, BOOK_SHARPE)

    def test_every_stock_carries_the_baskets_weight_and_spy_its_own(self, result) -> None:
        weights = result.weights
        assert len(weights) == 99
        assert (weights[:-1] == result.basket.eigenvectors[0, 0]).all()
        assert weights[-1] == result.basket.eigenvectors[1, 0]

    def test_the_first_return_is_on_the_sixth_test_row_and_every_later_day_has_one(
        self, result
    ) -> None:
        """The moving deviation fills on row 4 and positions earn from the next row."""
        nonzero = np.flatnonzero(result.daily)
        assert nonzero[0] == LOOKBACK == 5
        assert str(result.test_days[5].date()) == "2008-01-09"
        assert len(nonzero) == 1071 == 1076 - 5
        assert len(result.daily) == 1076

    def test_zero_padding_the_lag_as_lesage_does_gives_the_same_series(self, held, result) -> None:
        """Row 0 is 0 over 0 under a zero pad, and rows 1 to 4 read NaN positions."""
        weights = result.weights
        logs = np.log(held)

        def lag(x):
            return np.vstack([np.zeros((1, x.shape[1])), x[:-1]])

        value = smartsum(weights[None, :] * logs, axis=1)
        with np.errstate(invalid="ignore", divide="ignore"):
            units = -(value - moving_avg(value, 5)) / moving_std(value, 5)
            positions = units[:, None] * weights[None, :]
            pnl = smartsum(lag(positions) * (logs - lag(logs)), axis=1)
            daily = pnl / smartsum(np.abs(lag(positions)), axis=1)
        assert np.isnan(daily[:5]).all()
        zero_padded = np.where(np.isnan(daily), 0.0, daily)
        np.testing.assert_array_equal(zero_padded == 0, result.daily == 0)
        # The row sums can part in their last bit, about 1e-17 on returns near
        # 1e-3, because numpy does not promise one summation order.
        np.testing.assert_allclose(zero_padded, result.daily, rtol=0, atol=1e-15)


class TestTheRule:
    """The script's steps on frames built by hand."""

    @staticmethod
    def _walks(days: int, symbols: list[str], seed: int = 3) -> tuple[pd.DataFrame, pd.Series]:
        rng = np.random.default_rng(seed)
        index = pd.date_range("2007-01-01", periods=days, freq="B")
        spy = pd.Series(100 + np.cumsum(rng.normal(size=days)), index=index)
        stocks = pd.DataFrame(
            {s: spy.to_numpy() / 2 + rng.normal(size=days) for s in symbols}, index=index
        )
        return stocks, spy

    def test_251_rows_are_tested_and_250_are_not(self) -> None:
        """Line 26 asks for more than 250, strictly."""
        stocks, spy = self._walks(251, ["FULL", "SHORT"])
        stocks.iloc[100, 1] = np.nan
        found = screen(stocks, spy)
        assert found.tested == ("FULL",)
        assert found.skipped == {"SHORT": 250}

    def test_a_row_holding_a_nan_is_removed_before_the_test(self) -> None:
        """``johansen`` refuses a NaN by name, so a test that reached one would raise."""
        stocks, spy = self._walks(253, ["GAP"])
        stocks.iloc[10, 0] = np.nan
        spy.iloc[20] = np.nan
        found = screen(stocks, spy)
        assert found.tested == ("GAP",)
        assert found.passed == ("GAP",)

    def test_a_nan_in_the_index_removes_that_row_for_every_stock(self) -> None:
        stocks, spy = self._walks(251, ["ONE", "TWO"])
        spy.iloc[0] = np.nan
        assert screen(stocks, spy).skipped == {"ONE": 250, "TWO": 250}

    def test_a_stock_with_no_close_in_the_window_is_skipped(self) -> None:
        stocks, spy = self._walks(260, ["LATE"])
        stocks["LATE"] = np.nan
        assert screen(stocks, spy).skipped == {"LATE": 0}

    def test_a_stock_tracking_the_index_passes_and_an_unrelated_walk_does_not(self) -> None:
        stocks, spy = self._walks(300, ["TRACKS"])
        rng = np.random.default_rng(11)
        stocks["WANDERS"] = 50 + np.cumsum(rng.normal(size=300))
        found = screen(stocks, spy)
        assert found.tested == ("TRACKS", "WANDERS")
        assert found.passed == ("TRACKS",)

    def test_the_basket_is_the_plain_sum_of_log_prices(self) -> None:
        prices = np.array([[1.0, np.e], [np.e, np.nan]])
        np.testing.assert_array_equal(basket_value(prices), [1.0, np.nan])

    def test_the_weights_repeat_the_baskets_element_for_every_stock(self) -> None:
        np.testing.assert_array_equal(instrument_weights(np.array([2.0, -3.0]), 3), [2, 2, 2, -3])

    def test_the_common_days_drop_a_day_either_file_lacks(self) -> None:
        stocks = pd.DataFrame(
            {"A": [1.0, 2.0, 3.0]}, index=pd.to_datetime(["2007-01-03", "2007-01-04", "2007-01-05"])
        )
        spy = pd.Series([4.0, 5.0], index=pd.to_datetime(["2007-01-05", "2007-01-03"]))
        cut, index = common_days(stocks, spy)
        assert list(cut["A"]) == [1.0, 3.0]
        assert list(index) == [5.0, 4.0]

    def test_the_last_day_of_2007_trains_and_the_first_of_2008_tests(self) -> None:
        days = pd.to_datetime(["2006-12-29", "2007-01-02", "2007-12-31", "2008-01-02"])
        train, test = windows(pd.DatetimeIndex(days))
        assert list(train) == [False, True, True, False]
        assert list(test) == [False, False, False, True]

    def test_a_portfolio_above_its_average_is_sold(self) -> None:
        """The last price jumps, so the units go negative and the next rise loses."""
        one = np.exp(np.r_[np.full(6, 1.0) + [0, 0.01, -0.01, 0.01, -0.01, 0], 1.2, 1.3])
        prices = np.column_stack([one, np.full(8, 5.0)])
        daily = index_arbitrage_returns(prices, np.array([1.0, 0.0]), 3)
        assert daily[7] < 0

    def test_a_missing_price_is_skipped_rather_than_zeroing_the_day(self) -> None:
        """``smartsum`` earns on the legs it can read, where Example 2.8's ``sum`` gives 0."""
        rng = np.random.default_rng(5)
        prices = np.exp(np.cumsum(rng.normal(scale=0.01, size=(30, 2)), axis=0))
        prices[20, 1] = np.nan
        daily = index_arbitrage_returns(prices, np.array([1.0, -1.0]), 5)
        assert daily[20] != 0
        assert np.isfinite(daily).all()

    def test_a_day_with_no_gross_is_zero_rather_than_nan(self) -> None:
        prices = np.exp(np.column_stack([np.linspace(0, 1, 8), np.linspace(1, 0, 8)]))
        assert (index_arbitrage_returns(prices, np.zeros(2), 3) == 0).all()


class TestBesideTheReplication:
    """No book prints these, so none carries a verdict."""

    def test_neither_2007_log_series_rejects_a_unit_root_even_at_90(self, result) -> None:
        """A plain ADF with a constant and one lag, against MacKinnon's −2.57.

        Row 6's two relations between two series say each is stationary around
        a constant over 2007. Neither rejects a unit root here, which is weak
        evidence against that reading rather than proof, on a test with little
        power over 251 days.
        """
        assert result.adf == pytest.approx({"basket": -2.461086, INDEX: -2.381322}, abs=1e-6)
        assert all(t > -2.57 for t in result.adf.values())

    def test_the_screen_passes_561_of_2000_walks_unrelated_to_spy(self, sources, result):
        """The 90 percent bar passes far more than 10 percent of stocks unrelated to SPY.

        2,000 Gaussian random walks with unit steps and no drift, seeded with
        343, each screened against SPY's 2007 closes exactly as the stocks are.
        561 pass, 28 percent, which is about 135 of 480 stocks. The 98 the
        screen passes is fewer than that, so 48, the nominal 10 percent of 480,
        is not what chance alone gives.
        """
        spy = sources[3].loc[result.train_days]
        rng = np.random.default_rng(343)
        walks = pd.DataFrame(
            100 + np.cumsum(rng.normal(size=(len(spy), 2000)), axis=0),
            index=spy.index,
            columns=[f"W{i}" for i in range(2000)],
        )
        found = screen(walks, spy)
        assert len(found.tested) == 2000
        assert len(found.passed) == 561
        assert 480 * len(found.passed) / 2000 == pytest.approx(134.64)
        assert len(result.screen.passed) < 480 * len(found.passed) / 2000

    def test_the_trace_test_rejects_two_to_three_times_its_nominal_rate_on_unrelated_walks(self):
        """Two independent walks of 251 days, 2,000 pairs seeded with 345.

        ``johansen(·, 0, 1)``'s trace test rejects r ≤ 0 on 410 pairs at its 90
        percent value and on 242 at its 95, about 20 and 12 percent where 10
        and 5 are nominal. So a pass at either bar, the screen's or row 5's, is
        weaker evidence than its label.
        """
        rng = np.random.default_rng(345)
        at = {90: 0, 95: 0}
        for _ in range(2000):
            pair = 100 + np.cumsum(rng.normal(size=(251, 2)), axis=0)
            tested = johansen(pair, 0, 1)
            for level in at:
                at[level] += tested.relations("trace", level) >= 1
        assert at == {90: 410, 95: 242}


class TestTheScaleBreakDecision:
    """Issue 343 decided the guard runs on SPY and not on the stocks."""

    @staticmethod
    def _tested_legs(sources, result):
        members = {m.symbol: m for m in sources[0]}
        stocks = sources[2]
        return [(members[s], stocks[s]) for s in result.screen.tested]

    def test_the_guard_refuses_the_480_over_the_days_the_run_reads(self, sources, result):
        legs = self._tested_legs(sources, result)
        with pytest.raises(WindowCrossesScaleBreak) as refused:
            refuse_window_crossing_a_break(
                legs, start=result.train_days[0], end=result.test_days[-1]
            )
        message = str(refused.value)
        assert message.count(" changes scale on ") == 17
        assert "inputdataohlcdaily_stocks_20120424/etfc.csv changes scale on 2007-11-12" in message
        assert "no readable day-over-day move" not in message

    def test_the_30_flags_fall_one_in_training_and_29_in_the_test(self, sources, result):
        flagged = [
            day
            for _, closes in self._tested_legs(sources, result)
            for day in scale_breaks(closes.dropna())
        ]
        assert len(flagged) == 30
        assert all(result.train_days[0] <= day <= result.test_days[-1] for day in flagged)
        assert sum(day <= result.train_days[-1] for day in flagged) == 1
        assert sum(result.test_days[0] <= day <= result.test_days[-1] for day in flagged) == 29

    def test_four_of_the_baskets_stocks_carry_a_flag_all_in_the_test(self, sources, result):
        stocks = sources[2]
        flags = {s: scale_breaks(stocks[s].dropna()) for s in result.screen.passed}
        carrying = sorted(s for s, days in flags.items() if days)
        assert carrying == ["CVH", "MOS", "PNC", "STT"], SPEC
        assert all(
            result.test_days[0] <= day <= result.test_days[-1] for s in carrying for day in flags[s]
        )

    def test_spy_carries_no_flag_over_the_common_days(self, sources) -> None:
        assert scale_breaks(sources[3]) == []


class TestTheGuardAndTheReads:
    def test_read_sources_runs_the_guard_on_spy_alone_over_the_common_days(
        self, monkeypatch
    ) -> None:
        seen = []

        def record(legs, *, start, end):
            seen.append(([entry.symbol for entry, _ in legs], start, end))

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", record)
        read_sources()
        assert seen == [([INDEX], pd.Timestamp("2006-05-11"), pd.Timestamp("2012-04-09"))]

    def test_a_refusal_from_the_guard_reaches_the_caller(self, monkeypatch) -> None:
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("flagged")

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(WindowCrossesScaleBreak, match="flagged"):
            run()

    def test_main_turns_a_guard_refusal_into_one_line(self, monkeypatch, no_arguments) -> None:
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("inputdata_etf/spy.csv changes scale on 2008-01-02")

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(SystemExit, match="spy.csv changes scale on 2008-01-02"):
            main()

    def test_run_reads_the_directory_it_is_given(self, tmp_path) -> None:
        with pytest.raises(VintageUnavailable, match=STOCK_FILE):
            run(tmp_path)

    def test_main_turns_a_missing_vintage_into_one_line(
        self, monkeypatch, tmp_path, no_arguments
    ) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit, match=STOCK_FILE):
            main()

    def test_a_miss_is_reported_as_one(self) -> None:
        assert module._verdict(0.0, "1.0") == "did not reproduce, gap -1"
        assert module._verdict(1.04, "1.0") == "reproduced"

    def test_the_report_marks_every_printed_figure_reproduced(
        self, monkeypatch, capsys, sources, no_arguments
    ) -> None:
        monkeypatch.setattr(module, "read_sources", lambda data_dir=None: sources)
        main()
        out = capsys.readouterr().out
        figures = out.split("Verdict\n")[1].split("\n\n")[0].splitlines()
        assert len(figures) == 11
        assert all(line.endswith("reproduced") for line in figures)
        assert "did not reproduce" not in out
        assert "basket eigen  0 at 90%, 0 at 95%, 0 at 99%" in out
        assert "480 stocks tested at a per-test 90% bar, with no false-discovery" in out
        assert "pass it about 28% of the time" in out
        assert "first return on 2008-01-09" in out
        assert "Exploratory and survivor-only." in out
