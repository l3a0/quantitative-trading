"""The pins for SPY against the S&P 500 stocks, *Algorithmic Trading*'s Example 4.2.

This file is the single authority for every number a prose surface quotes
about this example and the rows beside it, with one exception.
``blog/index-arbitrage-lessons.md`` also quotes its figure's numbers, which
``tests/test_index_arbitrage_figures.py`` holds, and claims no test asserts,
which README lists. ``docs/replication-log.md`` Entry 24
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
stocks that were in the S&P 500 in late 2011, and location 2035 says the lookback of 5 was
chosen with hindsight. The example first ran on 2026-10-05.
"""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import pandas as pd
import pytest
from ithildincore.timeseries import ADF_CRIT_CONST

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
    SCREEN_LEVEL,
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
    Screen,
    basket_value,
    common_days,
    index_arbitrage,
    index_arbitrage_returns,
    instrument_weights,
    main,
    read_sources,
    report,
    run,
    screen,
    walks_unrelated_to,
    windows,
)
from chan.johansen import johansen
from chan.khandani_lo_book_two import matches
from chan.matlab_helpers import moving_avg, moving_std, smartsum
from chan.series import WindowCrossesScaleBreak, refuse_window_crossing_a_break, scale_breaks
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import LIFTED_SOURCES

POST = paths.REPO_ROOT / "blog" / "index-arbitrage-lessons.md"
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


#: Lesson 2's two measurements: 2,000 walks screened against SPY from one seed,
#: and 2,000 pairs of independent walks of 251 days from another.
WALKS = 2000
WALK_SEED = 343
PAIR_SEED = 345
PAIR_DAYS = 251


@pytest.fixture(scope="module")
def walks_screened(sources, result) -> Screen:
    """The screen run on walks unrelated to SPY, against SPY's 2007 closes."""
    spy = sources[3].loc[result.train_days]
    return screen(walks_unrelated_to(spy, WALKS, WALK_SEED), spy)


@pytest.fixture(scope="module")
def pair_rejections() -> dict[int, int]:
    """How many pairs of independent walks the trace test rejects r ≤ 0 on, at 90 and 95."""
    rng = np.random.default_rng(PAIR_SEED)
    at = {90: 0, 95: 0}
    for _ in range(WALKS):
        pair = 100 + np.cumsum(rng.normal(size=(PAIR_DAYS, 2)), axis=0)
        tested = johansen(pair, 0, 1)
        for level in at:
            at[level] += tested.relations("trace", level) >= 1
    return at


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

    def test_the_trace_for_r_le_0_is_the_sum_of_the_two_eigen_statistics(self, result) -> None:
        """The post's Lesson 1 reads the second relation's evidence into the trace pass."""
        trace, eigen = result.basket.trace, result.basket.eigen
        assert trace[0] == pytest.approx(eigen[0] + eigen[1], abs=1e-12)
        assert trace[1] == pytest.approx(eigen[1], abs=1e-12)
        assert eigen[0] < result.basket.trace_critical[0][1] < trace[0]

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

    def test_the_98_stocks_together_carry_107_198_against_spys_105_560(self, result) -> None:
        """One unit is long about as many dollars of stocks as it is short of SPY."""
        stocks, spy = result.weights[:-1].sum(), result.weights[-1]
        assert stocks == pytest.approx(107.198448, abs=1e-6)
        assert spy == pytest.approx(-105.559992, abs=1e-6)
        assert stocks + spy == pytest.approx(1.638456, abs=1e-6)

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

    def test_the_common_days_come_back_in_date_order(self) -> None:
        stocks = pd.DataFrame(
            {"A": [3.0, 1.0, 2.0]}, index=pd.to_datetime(["2007-01-05", "2007-01-03", "2007-01-04"])
        )
        spy = pd.Series([1.0, 2.0, 3.0], index=stocks.index)
        cut, index = common_days(stocks, spy)
        assert cut.index.is_monotonic_increasing
        assert list(cut["A"]) == [1.0, 2.0, 3.0]
        assert index.index.equals(cut.index)

    def test_the_common_days_drop_a_day_either_file_lacks(self) -> None:
        stocks = pd.DataFrame(
            {"A": [1.0, 2.0, 3.0]}, index=pd.to_datetime(["2007-01-03", "2007-01-04", "2007-01-05"])
        )
        spy = pd.Series([4.0, 5.0], index=pd.to_datetime(["2007-01-05", "2007-01-03"]))
        cut, index = common_days(stocks, spy)
        assert list(cut["A"]) == [1.0, 3.0]
        assert list(index) == [5.0, 4.0]

    def test_the_last_day_of_2007_trains_and_the_first_of_2008_tests(self) -> None:
        days = pd.to_datetime(
            ["2006-12-29", "2007-01-01", "2007-01-02", "2007-12-31", "2008-01-01", "2008-01-02"]
        )
        train, test = windows(pd.DatetimeIndex(days))
        assert list(train) == [False, True, True, True, False, False]
        assert list(test) == [False, False, False, False, True, True]

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
        # The log market value skips the missing leg too, so the moving window
        # over day 20 stays finite and the next five days still earn.
        assert (daily[21:26] != 0).all()
        assert np.isfinite(daily).all()

    def test_a_day_with_no_price_at_all_earns_nothing_for_a_window(self) -> None:
        """``smartsum`` of nothing finite is NaN, where ``np.nansum`` would give 0.

        A value of 0 among log prices near 0.1 would be a z-score far from the
        rest, and the days after it would trade on that.
        """
        rng = np.random.default_rng(5)
        prices = np.exp(0.1 + np.cumsum(rng.normal(scale=0.01, size=(30, 2)), axis=0))
        prices[20, :] = np.nan
        daily = index_arbitrage_returns(prices, np.array([1.0, -1.0]), 5)
        assert (daily[20:26] == 0).all()
        assert daily[26] != 0

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

    def test_the_screen_passes_561_of_2000_walks_unrelated_to_spy(self, walks_screened, result):
        """The 90 percent bar passes far more than 10 percent of stocks unrelated to SPY.

        2,000 Gaussian random walks with unit steps and no drift, seeded with
        343, each screened against SPY's 2007 closes exactly as the stocks are.
        561 pass, 28.1 percent, which is about 135 of 480 stocks. The 98 the
        screen passes is fewer than that, so 48, the nominal 10 percent of 480,
        is not what chance alone gives.
        """
        assert len(walks_screened.tested) == WALKS == 2000
        assert len(walks_screened.passed) == 561
        assert 480 * len(walks_screened.passed) / 2000 == pytest.approx(134.64)
        assert len(result.screen.passed) < 480 * len(walks_screened.passed) / 2000

    def test_the_trace_test_rejects_two_to_three_times_its_nominal_rate_on_unrelated_walks(
        self, pair_rejections
    ):
        """Two independent walks of 251 days, 2,000 pairs seeded with 345.

        ``johansen(·, 0, 1)``'s trace test rejects r ≤ 0 on 410 pairs at its 90
        percent value and on 242 at its 95, 20.5 and 12.1 percent where 10
        and 5 are nominal. So a pass at either bar, the screen's or row 5's, is
        weaker evidence than its label.
        """
        assert (WALKS, PAIR_DAYS) == (2000, 251)
        assert pair_rejections == {90: 410, 95: 242}


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
        assert "basket trace  2 at 90%, 2 at 95%, 0 at 99%" in out
        assert "basket eigen  0 at 90%, 0 at 95%, 0 at 99%" in out
        assert "training 2007-01-03 to 2007-12-31, 251 trading days" in out
        assert "test     2008-01-02 to 2012-04-09, 1076 trading days" in out
        assert "17 skipped: CFN 0, COV 139, DFS 139, DPS 0" in out
        assert "basket -2.46, SPY -2.38, against -2.57 at 90%" in out
        assert "row 5 of the test, 1071 days with a return" in out
        assert "480 stocks tested at a per-test 90% bar, with no false-discovery" in out
        assert "pass it about 28% of the time" in out
        assert "first return on 2008-01-09" in out
        assert "Exploratory and survivor-only." in out

    def test_a_count_that_misses_98_is_reported_as_a_miss(self, capsys, sources, result):
        """The count's verdict is its own branch, so a run passing 97 must say so."""
        short = Screen(
            tested=result.screen.tested,
            skipped=result.screen.skipped,
            passed=result.screen.passed[:-1],
        )
        report(sources[0], sources[1], replace(result, screen=short))
        (line,) = [s for s in capsys.readouterr().out.splitlines() if "passing the screen" in s]
        assert line.endswith("did not reproduce, gap -1")


def _schedule_names(report_date: str) -> list[str]:
    """The lower-cased company names in one quarter's committed IVV holdings schedule."""
    path = paths.REPO_ROOT / "research" / "filings" / "ivv" / f"{report_date}.csv"
    return [str(name).lower() for name in pd.read_csv(path)["name"]]


class TestTheBasketsStocksAndTheIndex:
    """Fourteen of the 98 stocks the screen picks were out of the S&P 500 at some point.

    The stock file holds companies that were in the index in late 2011, which
    ``TestTheListDatesFromLate2011`` in ``tests/test_buy_on_gap.py`` holds for
    the same file. The screen then runs on 2007, so it can pick a company that
    joined the index after 2007, or one that left and came back. Two committed
    sources show both. ``data/spx_20071123/`` is Chan's list of the index as it
    stood on 2007-11-23, by ticker. The IVV schedules under
    ``research/filings/ivv/`` name companies rather than tickers at each
    quarter-end from 2008-12-31, so those checks match a distinctive word of
    the name. The schedules hold nothing between 2007-11-23 and 2008-12-31, so
    a stock that left and returned inside that gap is not seen here.
    """

    #: The basket's tickers missing from Chan's 2007-11-23 list. MSI is not one
    #: of the 12 companies: Motorola traded as MOT until 2011, and MOT is on it.
    NOT_ON_THE_2007_LIST = {
        "AKS",
        "CERN",
        "HCP",
        "MOS",
        "MSI",
        "NFX",
        "NRG",
        "OKE",
        "PBCT",
        "PWR",
        "PXD",
        "RHT",
        "WPO",
    }
    #: Two members of 2007 the IVV schedules omit at every quarter-end from the
    #: first to the last named here, and the first quarter-end each is back.
    OUT_AND_BACK = {
        "ACE": ("ace ltd", ("2008-12-31", "2010-06-30"), "2010-09-30"),
        "CBE": ("cooper industries", ("2009-09-30", "2011-09-30"), "2011-12-31"),
    }

    def test_12_of_the_98_were_not_on_the_index_list_of_2007_11_23(self, result) -> None:
        listed = {path.stem.upper() for path in (paths.DATA_DIR / "spx_20071123").glob("*.csv")}
        assert len(listed) == 500
        assert set(result.screen.passed) - listed == self.NOT_ON_THE_2007_LIST
        assert "MOT" in listed
        assert len(self.NOT_ON_THE_2007_LIST - {"MSI"}) == 12

    def test_ace_and_cooper_industries_left_the_index_during_the_test_and_came_back(
        self, result
    ) -> None:
        schedules = sorted(
            p.stem for p in (paths.REPO_ROOT / "research" / "filings" / "ivv").glob("*.csv")
        )
        for ticker, (name, (first, last), back) in self.OUT_AND_BACK.items():
            assert ticker in result.screen.passed
            assert ticker not in self.NOT_ON_THE_2007_LIST
            missing = [q for q in schedules if first <= q <= last]
            assert len(missing) >= 7
            for quarter in missing:
                assert not any(name in n for n in _schedule_names(quarter)), (ticker, quarter)
            assert any(name in n for n in _schedule_names(back)), ticker

    def test_ak_steel_is_in_the_basket_after_it_left_the_index(self, result) -> None:
        assert "AKS" in result.screen.passed
        assert any("ak steel" in n for n in _schedule_names("2011-09-30"))
        for quarter in ("2011-12-31", "2012-03-31"):
            assert not any("ak steel" in n for n in _schedule_names(quarter))
        assert result.test_days[-1] == pd.Timestamp("2012-04-09")

    def test_the_post_counts_the_basket_stocks_outside_the_index(self) -> None:
        text = POST.read_text(encoding="utf-8")
        assert "12 of the 98 it picks were not in the index on 2007-11-23" in text
        assert "Twelve of the 98 are missing from Chan’s list of the S&P 500" in text
        assert "All 14 stay in the basket on every test day." in text


#: Small counts and ordinals as the post spells them out, indexed by the number.
SPELLED = {2: "two", 6: "six", 11: "Eleven"}
ORDINAL = {5: "fifth", 6: "sixth"}


def _minus(x: float, places: int) -> str:
    """A negative figure in prose, with the post's typographic minus sign."""
    return f"{x:.{places}f}".replace("-", "−")


def _array(head: str, rows: list[list[str]]) -> str:
    """One of the post's ``array`` tables, from its header row to its last row."""
    body = " \\\\\n".join(" & ".join(row) for row in rows)
    return f"{head} \\\\ \\hline\n{body}\n\\end{{array}}"


class TestWhatThePostQuotes:
    """Each run figure the post quotes outside its sketch, read against the run.

    The classes above pin each figure once, and the post copies it by hand.
    Here each figure the run computes is built from the run's value at the
    precision the post prints it, and looked for in at least one copy: a short
    fragment holding the number and the few words that name one place in the
    post. A typo in a copy that is read, or a re-pin that leaves the post
    behind, fails here. Lesson 1's four tables are rebuilt whole, each
    computed cell from the run and each cell in a column of the script's
    figures from its printout as :mod:`chan.index_arbitrage` records it, so a digit added to a
    cell fails as well as a digit changed. The two random-walk measurements
    come from the same fixtures the pins of 561, 410 and 242 read, so they run
    once for the module.

    The post states several figures more than once, and only one copy of each
    is read. The copies read are the ones in the section on the files, the
    paragraphs on one unit, Lesson 1's tables and the two paragraphs after
    them, Lesson 2's measurements, Lesson 3's ADF statistics, and, in the
    figure's alt text, the APR, the Sharpe ratio, the first return's date and
    the last day's cumulative return. Other copies are not read, among them
    the 98 and 480 in the opening and the alt text, the 12.1 percent in
    Lesson 3, the 497 in Lesson 4 and the 99 positions in the closing list, so
    a typo in one of them passes. The alt text's 98 of 480 and 561 of 2,000
    are drawn by the figure, and ``tests/test_index_arbitrage_figures.py``
    holds those. The sketch's caption and alt text are read in
    ``tests/test_index_arbitrage_whiteboard.py`` instead, and the counts of
    the basket's stocks outside the index in
    ``TestTheBasketsStocksAndTheIndex``. The Kindle locations, the facts
    outside the data and the references are checked by nothing, and README
    lists them.
    """

    @pytest.fixture(scope="class")
    @classmethod
    def text(cls) -> str:
        return POST.read_text(encoding="utf-8")

    @staticmethod
    def missing(text: str, fragments: list[str]) -> list[str]:
        return [fragment for fragment in fragments if fragment not in text]

    def test_the_files_and_the_windows(self, sources, result, text) -> None:
        stock_members, spy_member, stocks, _ = sources
        whole = module.load_panel(STOCK_FILE)[1].index
        spy_closes = module.load_panel(ETF_FILE)[1][INDEX]
        (saved,) = {m.obtained for m in stock_members}
        train, test = result.train_days, result.test_days
        found = result.screen
        none = sum(rows == 0 for rows in found.skipped.values())
        fragments = [
            f"The stock file holds {len(stock_members)} stocks that were in the S&P 500 in "
            f"late 2011, with prices from {whole[0].date()} to {whole[-1].date()}, and was "
            f"saved on {saved}.",
            f"whose closes end on {spy_closes.last_valid_index().date()} and which was saved "
            f"on {spy_member.obtained}.",
            f"The two share {len(stocks):,} trading days from {stocks.index[0].date()} to "
            f"{stocks.index[-1].date()}. Training is the {len(train)} days of 2007, from "
            f"{train[0].date()} to {train[-1].date()}, and the test period is the "
            f"{len(test):,} days from {test[0].date()} to {test[-1].date()}",
            f"The screen needs more than {FEWEST_ROWS} days of closes, so it skips "
            f"{len(found.skipped)} stocks. {SPELLED[none]} have no 2007 close at all, and "
            f"{SPELLED[len(found.skipped) - none]} began trading during 2007. It tests the "
            f"other {len(found.tested)}.",
            f"A stock passes when the trace statistic clears its {SCREEN_LEVEL} percent bar "
            "for r ≤ 0",
            f"both taken over the last {LOOKBACK} days. Those {LOOKBACK} days are the rule’s "
            "lookback.",
        ]
        assert self.missing(text, fragments) == []

    def test_one_unit_and_its_first_return(self, result, text) -> None:
        (basket, spy), passed = result.basket.eigenvectors[:, 0], len(result.screen.passed)
        stocks = result.weights[:-1].sum()
        earning = np.flatnonzero(result.daily)
        first = int(earning[0])
        fragments = [
            f"gives two weights, {basket:.4f} on the basket and {_minus(spy, 4)} on SPY. The "
            f"basket’s weight goes on each of its {passed} stocks, so the script holds "
            f"{len(result.weights)} positions, {basket:.4f} on each stock and "
            f"{_minus(spy, 4)} on SPY.",
            f"is long ${basket:.5f} of each stock, ${stocks:.3f} of stocks in all, and short "
            f"${-spy:.3f} of SPY. The two sides differ by ${stocks + spy:.3f},",
            f"first exists on the {ORDINAL[LOOKBACK]} test day, so the strategy’s first return "
            f"falls on {result.test_days[first].date()}, the {ORDINAL[first + 1]} "
            f"test day. From there the strategy earns a return on every one of the "
            f"{len(earning):,} remaining days.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_1s_three_tables(self, result, text) -> None:
        tested, passed = result.basket, len(result.screen.passed)
        statistics = [
            [f"\\text{{{name}, }} r \\le {i}", f"{values[i]:.6f}", printed[i]]
            for name, values, printed in (
                ("Trace", tested.trace, SCRIPT_TRACE),
                ("Eigen", tested.eigen, SCRIPT_EIGEN),
            )
            for i in range(2)
        ]
        vectors = [
            [f"\\text{{{which}, {leg}}}", f"{tested.eigenvectors[i, j]:.8f}", row[j]]
            for j, which in enumerate(("First", "Second"))
            for i, (leg, row) in enumerate(zip(("basket", "SPY"), SCRIPT_EIGENVECTORS, strict=True))
        ]
        fragments = [
            _array(
                "\\begin{array}{l|r|r}\n\\text{Figure} & \\text{Computed} & \\text{Script}",
                [["\\text{Stocks passing}", str(passed), str(SCRIPT_PASSED)], *statistics],
            ),
            _array(
                "\\small\\begin{array}{l|r|r}\n"
                "\\text{Eigenvector} & \\text{Computed} & \\text{Script}",
                vectors,
            ),
            _array(
                "\\begin{array}{l|r|r|r}\n"
                "\\text{Figure} & \\text{Computed} & \\text{Script} & \\text{Book}",
                [
                    ["\\text{APR}", f"{result.apr:.10f}", SCRIPT_APR, f"{BOOK_APR_PERCENT}\\%"],
                    ["\\text{Sharpe}", f"{result.sharpe:.10f}", SCRIPT_SHARPE, BOOK_SHARPE],
                ],
            ),
            f"The book’s {100 * result.apr:.1f} percent and {result.sharpe:.1f} are the "
            "script’s figures rounded.",
        ]
        assert self.missing(text, fragments) == []

    def test_what_the_second_test_supports(self, result, text) -> None:
        tested = result.basket
        trace_bar, eigen_bar = tested.trace_critical, tested.eigen_critical
        levels = (90, 95)
        fragments = [
            _array(
                "\\begin{array}{l|r|r}\nr \\le 0 & \\text{Trace} & \\text{Eigen}",
                [
                    ["\\text{Value}", f"{tested.trace[0]:.3f}", f"{tested.eigen[0]:.3f}"],
                    *(
                        [
                            f"\\text{{{level} percent bar}}",
                            f"{trace_bar[0, k]:.3f}",
                            f"{eigen_bar[0, k]:.3f}",
                        ]
                        for k, level in enumerate(levels)
                    ),
                ],
            ),
            f"The trace statistic clears its {levels[1]} percent bar by "
            f"{tested.trace[0] - trace_bar[0, 1]:.3f}.",
            f"the sum of the two eigen statistics, {tested.eigen[0]:.6f} and "
            f"{tested.eigen[1]:.6f},",
            f"the trace test counts {SPELLED[tested.relations('trace', levels[1])]} relations "
            f"at both {levels[0]} and {levels[1]} percent, because its r ≤ 1 statistic, "
            f"{tested.trace[1]:.3f}, also clears that row’s bars, which the script prints as "
            f"{trace_bar[1, 0]:.3f} and {trace_bar[1, 1]:.3f}.",
        ]
        assert tested.relations("trace", levels[0]) == tested.relations("trace", levels[1])
        assert self.missing(text, fragments) == []

    def test_the_figures_alt_text(self, result, text) -> None:
        cumulative = np.cumprod(1 + result.daily) - 1
        first = result.test_days[int(np.flatnonzero(result.daily)[0])]
        fragments = [
            f"to end at about {100 * cumulative[-1]:.1f} percent.",
            f"Its heading sets the APR of {result.apr:.6f} and the Sharpe ratio of "
            f"{result.sharpe:.6f} beside the book’s {BOOK_APR_PERCENT} percent and "
            f"{BOOK_SHARPE}, and says the curve is zero until the first return on "
            f"{first.date()} and {cumulative[-1]:.6f} on the last day.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_2s_walks(self, result, walks_screened, pair_rejections, text) -> None:
        tested, passed = len(result.screen.tested), len(result.screen.passed)
        walked = len(walks_screened.passed)
        nominal = 100 - SCREEN_LEVEL
        pairs = {level: 100 * count / WALKS for level, count in pair_rejections.items()}
        fragments = [
            f"chance alone would pass about {nominal} percent of the {tested}, which is "
            f"{tested * nominal // 100}.",
            f"On {WALKS:,} pairs of random walks of {PAIR_DAYS} days,",
            f"rejects the hypothesis of no relation on {pair_rejections[90]} pairs at its 90 "
            f"percent bar and on {pair_rejections[95]} at its 95. That is {pairs[90]:.1f} and "
            f"{pairs[95]:.1f} percent, where the bars allow 10 and 5.",
            f"the screen passes {walked} of {len(walks_screened.tested):,} random walks "
            f"unrelated to SPY against SPY’s own 2007 closes. That is "
            f"{100 * walked / WALKS:.1f} percent, or about {round(tested * walked / WALKS)} of "
            f"{tested}. It is higher than the {pairs[90]:.1f} percent of the first measurement.",
            f"The stocks pass at {100 * passed / tested:.1f} percent, {passed} of {tested}. The "
            f"random walks unrelated to SPY pass at {100 * walked / WALKS:.1f} percent.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_3s_adf_statistics(self, result, text) -> None:
        bar = ADF_CRIT_CONST["10%"]
        assert all(t > bar for t in result.adf.values()), SPEC
        fragments = [
            f"it gives {_minus(result.adf['basket'], 6)} for the basket’s 2007 sum of log "
            f"prices and {_minus(result.adf[INDEX], 6)} for SPY’s 2007 log price. Neither "
            f"falls below {_minus(bar, 2)}, the bar at 90 percent",
        ]
        assert self.missing(text, fragments) == []
