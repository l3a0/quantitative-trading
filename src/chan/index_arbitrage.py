"""SPY against the S&P 500 stocks that pass a Johansen screen, *Algorithmic Trading*'s Example 4.2.

Chan tests each stock in his 2012 S&P 500 file against SPY over 2007 and keeps
the ones that pass. He holds those stocks with equal capital, checks that the
basket cointegrates with SPY, and trades the basket against SPY with a linear
mean-reversion rule from 2008. At Kindle location 2035 he reports "98 stocks
that cointegrate (each separately) with SPY", a basket that cointegrates with
SPY "with better than 95 percent probability", and, over January 2, 2008, to
April 9, 2012, "The APR of this strategy is 4.5 percent, and the Sharpe ratio
is 1.3".

**The transcription.** One script, ``indexArb.m``, git blob ``dcb079a``. It
was read in the mirror
[ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) at
``e4bc46f``, under ``public/img/book2/``, and the same blob sits in
[ivanliu1989/algorithmic_trading](https://github.com/ivanliu1989/algorithmic_trading)
at ``4567024``, under ``archived/matlab/``. It landed here for
[issue 343](https://github.com/l3a0/quantitative-trading/issues/343). Line
numbers are that blob's.

1. **Lines 4 to 14.** The stock closes and SPY's close, cut to the days both
   files hold, which is MATLAB's ``intersect`` and :func:`common_days`.
2. **Lines 16 and 17.** Training is every day from 20070101 to 20071231 and
   the test is every day after 20071231, which is :func:`windows`.
3. **Lines 19 to 32, the screen.** For each stock, the training rows of
   ``[stock close, SPY close]``, in prices rather than logs, with every row
   holding a NaN removed. A stock is tested only when more than 250 rows
   remain. It passes when ``lr1(1) > cvt(1, 1)``, the trace statistic for
   r ≤ 0 above its 90 percent value, which is
   ``Johansen.relations("trace", 90) >= 1``. That is :func:`screen`.
4. **Lines 39 to 44.** ``sum(log(yN), 2)`` over the stocks that passed, then
   ``johansen([basket, log(SPY)], 0, 1)``, in log prices. MATLAB's plain
   ``sum`` is :func:`basket_value`.
5. **Lines 66 to 68.** Column 1 of ``evec`` gives one weight to every stock's
   log price and another to SPY's, which is :func:`instrument_weights`.
6. **Lines 70 to 77, the strategy on the test window.** The log market value
   is ``smartsum`` of each weight times its log price. ``numUnits`` is minus
   its distance from its 5-day moving average, in 5-day moving standard
   deviations. Each instrument's position in dollars is ``numUnits`` times its
   weight, with no price in it. The day's profit is yesterday's dollars times
   today's change in log price, summed, and the day's return is that over
   yesterday's gross. A NaN day is 0. That is :func:`index_arbitrage_returns`.
7. **Line 82.** The APR is ``prod(1 + r)^(252 / n) − 1`` and the Sharpe ratio
   ``√252 · mean / std`` over all test rows, with MATLAB's n − 1 ``std``,
   which are :func:`chan.khandani_lo_book_two.compounded_apr` and
   :func:`chan.khandani_lo.plain_sharpe`.

Example 2.8's :func:`chan.etf_cointegration.linear_mean_reversion` is not
reused. It holds units times price and earns simple returns. This script holds
dollars and earns log returns, so the formula differs.

**What changed on the way over.** Five things, and none moves a figure.

1. Both files are read as committed vintages through
   :func:`chan.series.load_panel` rather than from the ``.mat``.
2. The stock file is named ``inputDataOHLCDaily_stocks_20120424.mat``, where
   line 4 loads ``inputDataOHLCDaily_20120424`` with no ``_stocks``.
   ``data/README.md`` records that the two names are one blob with one
   sha256.
3. The two plot lines, 79 and 80, are not carried. The run prints and draws
   nothing, and :mod:`chan.index_arbitrage_figures` draws Figure 4.3 for the
   post.
4. :func:`chan.matlab_helpers.backshift` stands in for LeSage's ``lag``,
   which pads its first row with zero where ``backshift`` pads with NaN.
   Neither mirror holds a ``lag.m``, and the script already calls LeSage's
   ``johansen``, so his toolbox's ``lag`` is the one that ran. Either pad
   leaves the first five test rows not a number. The first row is 0 over a
   gross of 0 under a zero pad and the pad itself under ``backshift``. The
   next four read positions that are NaN, because the moving average needs
   five rows. Each becomes 0 under line 77, and the tests hold that.
5. The run calls the scale-break guard on SPY, which the script has no
   counterpart for, and not on the stocks, for the reason below.

**The screen is a search, and the count is reported as one.** Lines 26 to 28
test 480 stocks against one bar each, at 90 percent. The bar's nominal 10
percent would put about 48 passes down to chance, but the test does not hold
its nominal rate. Random walks unrelated to SPY pass it 28 percent of the
time against SPY's 2007 closes, which is about 135 of 480 and more than the 98
that pass. ``tests/test_index_arbitrage.py`` measures that on seeded walks. So
the count is stocks passing a per-test 90 percent bar among 480 tested, never
stocks that cointegrate with SPY. The run varies nothing, since ``indexArb.m``
fixed the panel, the window, the bar and the test before any number here was
seen, so no false-discovery control is computed. ``coint_johansen`` returns no
p-values for one to read.

**SPY is guarded and the stocks are not.** SPY carries no flagged day over the
two files' common days. The stocks carry all 30 of the panel's flagged days
inside the window this run reads, ETFC's 2007-11-12 in training and 29 more in
the test, and the guard would refuse the run on them. ``indexArb.m`` ran on
these prices as they stand, so this run does too, following
[issue 295](https://github.com/l3a0/quantitative-trading/issues/295).
``TestTheScaleBreakDecision`` in ``tests/test_index_arbitrage.py`` holds both.

**A screen that passes no stock is not refused by name.** The basket would sum
no columns and the second test would read a column of zeros, which statsmodels
refuses with a linear-algebra error. Chan's file cannot reach that path, so it
has run zero times, and the repo's ranking rule defers it.

Every result here is exploratory, survivor-only, and in-sample on its
lookback. Reproducing Chan's figures spends the 2007 to 2012 sample on a rule
he chose. The panel is the index as Chan held it on 2012-04-24, carried
backwards, so the 2007 screen picks only from stocks that survived to 2012.
The stocks and weights are fitted on 2007 and traded from 2008, but location
2035 says the lookback of 5 was fixed with the benefit of hindsight, so the
APR and Sharpe ratio are not out-of-sample figures.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from ithildincore.timeseries import ADF_CRIT_CONST, adf_tstat
from numpy.typing import NDArray

from chan.johansen import Johansen, johansen
from chan.khandani_lo import TRADING_DAYS, plain_sharpe
from chan.khandani_lo_book_two import compounded_apr, gap, matches
from chan.matlab_helpers import backshift, moving_avg, moving_std, smartsum
from chan.series import (
    WindowCrossesScaleBreak,
    load_panel,
    panel_line,
    refuse_window_crossing_a_break,
    vintage_line,
)
from chan.vintage import VintageEntry, VintageUnavailable

STOCK_FILE = "inputDataOHLCDaily_stocks_20120424.mat"
ETF_FILE = "inputData_ETF.mat"
INDEX = "SPY"

#: Lines 16 and 17: training is 20070101 to 20071231, and the test every day after.
TRAIN_START = pd.Timestamp("2007-01-01")
TRAIN_END = pd.Timestamp("2007-12-31")

#: Line 26 tests a stock only when more than this many rows remain.
FEWEST_ROWS = 250
#: Line 28's ``cvt(1, 1)``, the 90 percent column.
SCREEN_LEVEL = 90
#: ``johansen(·, 0, 1)``.
JOHANSEN_P = 0
JOHANSEN_K = 1
#: Line 72.
LOOKBACK = 5

#: Line 35 and location 2035.
SCRIPT_PASSED = 98
#: Lines 50 to 55, one row per null r ≤ i, critical values at 90, 95 and 99.
SCRIPT_TRACE = ("15.869", "6.197")
SCRIPT_TRACE_CRITICAL = (("13.429", "15.494", "19.935"), ("2.705", "3.841", "6.635"))
SCRIPT_EIGEN = ("9.671", "6.197")
SCRIPT_EIGEN_CRITICAL = (("12.297", "14.264", "18.520"), ("2.705", "3.841", "6.635"))
#: ``results.evec``, lines 61 and 62, rows basket and SPY and one vector per column.
SCRIPT_EIGENVECTORS = (("1.0939", "-0.2799"), ("-105.5600", "56.0933"))
#: Line 83 and location 2035.
SCRIPT_APR = "0.044930"
SCRIPT_SHARPE = "1.319397"
BOOK_APR_PERCENT = "4.5"
BOOK_SHARPE = "1.3"
#: Location 2035's test window.
BOOK_TEST_START = pd.Timestamp("2008-01-02")
BOOK_TEST_END = pd.Timestamp("2012-04-09")


def common_days(stocks: pd.DataFrame, index: pd.Series) -> tuple[pd.DataFrame, pd.Series]:
    """Lines 8 to 10: both files cut to the days both hold, in date order."""
    days = stocks.index.intersection(index.index).sort_values()
    return stocks.loc[days], index.loc[days]


def windows(days: pd.DatetimeIndex) -> tuple[NDArray[np.bool_], NDArray[np.bool_]]:
    """Lines 16 and 17: which rows are training and which are the test."""
    train = (days >= TRAIN_START) & (days <= TRAIN_END)
    test = days > TRAIN_END
    return np.asarray(train), np.asarray(test)


@dataclass(frozen=True)
class Screen:
    """Lines 19 to 32. ``skipped`` maps each untested stock to the rows it kept."""

    tested: tuple[str, ...]
    skipped: dict[str, int]
    passed: tuple[str, ...]


def screen(stocks: pd.DataFrame, index: pd.Series) -> Screen:
    """Test each stock's training closes against the index's, in the frame's column order."""
    tested, skipped, passed = [], {}, []
    leg = index.to_numpy(dtype=float)
    for symbol in stocks.columns:
        y2 = np.column_stack([stocks[symbol].to_numpy(dtype=float), leg])
        y2 = y2[~np.isnan(y2).any(axis=1)]
        if not len(y2) > FEWEST_ROWS:
            skipped[symbol] = len(y2)
            continue
        tested.append(symbol)
        if johansen(y2, JOHANSEN_P, JOHANSEN_K).relations("trace", SCREEN_LEVEL) >= 1:
            passed.append(symbol)
    return Screen(tested=tuple(tested), skipped=skipped, passed=tuple(passed))


def walks_unrelated_to(index: pd.Series, count: int, seed: int) -> pd.DataFrame:
    """``count`` Gaussian random walks on ``index``'s days, unit steps, no drift, from 100.

    They share nothing with the index, so :func:`screen` run on them measures
    how often the screen passes a series by chance.
    """
    rng = np.random.default_rng(seed)
    return pd.DataFrame(
        100 + np.cumsum(rng.normal(size=(len(index), count)), axis=0),
        index=index.index,
        columns=[f"W{i}" for i in range(count)],
    )


def basket_value(prices: NDArray[np.float64]) -> NDArray[np.float64]:
    """Line 40's ``sum(log(yN), 2)``, which a NaN turns to NaN, as MATLAB's ``sum`` does."""
    return np.log(prices).sum(axis=1)


def instrument_weights(eigenvector: NDArray[np.float64], stocks: int) -> NDArray[np.float64]:
    """Lines 67 and 68: the basket's weight on each of ``stocks`` columns, then SPY's."""
    return np.r_[np.full(stocks, eigenvector[0]), eigenvector[1]]


def index_arbitrage_returns(
    prices: NDArray[np.float64], weights: NDArray[np.float64], lookback: int
) -> NDArray[np.float64]:
    """Lines 70 to 77: the daily returns of holding minus the z-score in dollars.

    ``prices`` holds one column per instrument, the basket's stocks then SPY.
    Every sum is ``smartsum``, which skips a NaN and is NaN only where nothing
    is finite, and a day that is not a number is then 0.
    """
    logs = np.log(prices)
    value = smartsum(weights[None, :] * logs, axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        units = -(value - moving_avg(value, lookback)) / moving_std(value, lookback)
        held = backshift(1, units[:, None] * weights[None, :])
        pnl = smartsum(held * (logs - backshift(1, logs)), axis=1)
        daily = pnl / smartsum(np.abs(held), axis=1)
    return np.where(np.isnan(daily), 0.0, daily)


@dataclass(frozen=True)
class IndexArbitrage:
    """The whole script on both files, and the rows beside it.

    ``adf`` holds a plain ADF t-statistic with a constant and one lag on each
    2007 log series, the basket and SPY.
    """

    train_days: pd.DatetimeIndex
    test_days: pd.DatetimeIndex
    screen: Screen
    basket: Johansen
    weights: NDArray[np.float64]
    daily: NDArray[np.float64]
    adf: dict[str, float]

    @property
    def apr(self) -> float:
        return compounded_apr(self.daily)

    @property
    def sharpe(self) -> float:
        return plain_sharpe(self.daily)


def index_arbitrage(stocks: pd.DataFrame, index: pd.Series) -> IndexArbitrage:
    """Run the script on the stock closes and the index's, already on their common days."""
    train, test = windows(stocks.index)
    found = screen(stocks.loc[train], index.loc[train])
    basket = basket_value(stocks.loc[train, list(found.passed)].to_numpy(dtype=float))
    logged_index = np.log(index.loc[train].to_numpy(dtype=float))
    tested = johansen(np.column_stack([basket, logged_index]), JOHANSEN_P, JOHANSEN_K)
    weights = instrument_weights(tested.eigenvectors[:, 0], len(found.passed))
    held = np.column_stack(
        [stocks.loc[test, list(found.passed)].to_numpy(dtype=float), index.loc[test].to_numpy()]
    )
    return IndexArbitrage(
        train_days=stocks.index[train],
        test_days=stocks.index[test],
        screen=found,
        basket=tested,
        weights=weights,
        daily=index_arbitrage_returns(held, weights, LOOKBACK),
        adf={
            "basket": adf_tstat(basket, lags=1, constant=True)[0],
            INDEX: adf_tstat(logged_index, lags=1, constant=True)[0],
        },
    )


def read_sources(
    data_dir: Path | None = None,
) -> tuple[list[VintageEntry], VintageEntry, pd.DataFrame, pd.Series]:
    """Both files on their common days, refused if SPY spans a scale break over them."""
    stock_members, stocks = load_panel(STOCK_FILE, data_dir=data_dir)
    etf_members, etfs = load_panel(ETF_FILE, data_dir=data_dir)
    (spy_member,) = [m for m in etf_members if m.symbol == INDEX]
    stocks, index = common_days(stocks, etfs[INDEX])
    refuse_window_crossing_a_break([(spy_member, index)], start=index.index[0], end=index.index[-1])
    return stock_members, spy_member, stocks, index


def _verdict(value: float, printed: str) -> str:
    return (
        "reproduced"
        if matches(value, printed)
        else f"did not reproduce, gap {gap(value, printed):+g}"
    )


def _relations(test: Johansen, statistic: str) -> str:
    return ", ".join(f"{test.relations(statistic, level)} at {level}%" for level in (90, 95, 99))


def report(
    stock_members: list[VintageEntry], spy_member: VintageEntry, result: IndexArbitrage
) -> None:
    """Print the vintages, each printed figure beside the computed one, and the rows beside them."""
    found, basket = result.screen, result.basket
    train, test = result.train_days, result.test_days
    print("SPY against the S&P 500 stocks that pass a screen, Algorithmic Trading's Example 4.2")
    print(f"  stocks   {panel_line(stock_members)}")
    print(f"  index    {vintage_line(spy_member)}")
    print(f"  training {train[0].date()} to {train[-1].date()}, {len(train)} trading days")
    print(f"  test     {test[0].date()} to {test[-1].date()}, {len(test)} trading days")
    print(
        f"  tests    johansen(., {JOHANSEN_P}, {JOHANSEN_K}), the screen's trace at "
        f"{SCREEN_LEVEL}% on prices, the basket's on log prices, lookback {LOOKBACK}"
    )
    print()
    rows = [
        *(
            (f"basket trace, r <= {i}", basket.trace[i], printed)
            for i, printed in enumerate(SCRIPT_TRACE)
        ),
        *(
            (f"basket eigen, r <= {i}", basket.eigen[i], printed)
            for i, printed in enumerate(SCRIPT_EIGEN)
        ),
        *(
            (f"eigenvector {j + 1}, {name} row", basket.eigenvectors[i, j], row[j])
            for i, (name, row) in enumerate(
                zip(("basket", INDEX), SCRIPT_EIGENVECTORS, strict=True)
            )
            for j in range(2)
        ),
        ("APR", result.apr, SCRIPT_APR),
        ("Sharpe", result.sharpe, SCRIPT_SHARPE),
    ]
    passed = len(found.passed)
    counted = (
        "reproduced"
        if passed == SCRIPT_PASSED
        else f"did not reproduce, gap {passed - SCRIPT_PASSED:+d}"
    )
    print(f"  {'Figure':<28} {'Computed':>12}  {'Chan':>12}  Verdict")
    print(f"  {'stocks passing the screen':<28} {passed:>12d}  {SCRIPT_PASSED:>12d}  {counted}")
    for label, value, printed in rows:
        print(f"  {label:<28} {value:>12.6f}  {printed:>12}  {_verdict(value, printed)}")
    print()
    print("  Relations found, counting rejected nulls up to the first that is not")
    print(f"    basket trace  {_relations(basket, 'trace')}")
    print(f"    basket eigen  {_relations(basket, 'eigen')}")
    print()
    print("Beside the replication. No book prints these, so none carries a verdict.")
    print(
        f"  {len(found.tested)} stocks tested at a per-test {SCREEN_LEVEL}% bar, with no "
        "false-discovery control. Walks unrelated to SPY pass it about 28% of the time."
    )
    print(
        f"  {len(found.skipped)} skipped: "
        + ", ".join(f"{symbol} {rows}" for symbol, rows in found.skipped.items())
    )
    print(
        "  ADF with a constant and one lag on 2007 log prices  "
        + ", ".join(f"{name} {t:.2f}" for name, t in result.adf.items())
        + f", against {ADF_CRIT_CONST['10%']} at 90%"
    )
    first = int(np.flatnonzero(result.daily)[0])
    print(
        f"  first return on {test[first].date()}, row {first} of the test, "
        f"{np.count_nonzero(result.daily)} days with a return"
    )
    print()
    print(
        f"  Annualised over {TRADING_DAYS} days with no cost. The lookback was chosen "
        "with hindsight, so the APR is in-sample."
    )
    print("  Exploratory and survivor-only. docs/replication-log.md carries the verdicts.")


def run(data_dir: Path | None = None) -> IndexArbitrage:
    """Read both files, guard SPY, run the script, and print the report."""
    stock_members, spy_member, stocks, index = read_sources(data_dir)
    result = index_arbitrage(stocks, index)
    report(stock_members, spy_member, result)
    return result


def main() -> None:
    argparse.ArgumentParser(
        description="SPY against the S&P 500 stocks that pass a screen, "
        "Algorithmic Trading's Example 4.2"
    ).parse_args()
    try:
        run()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day reaches the reader
        # as one line, the way chan.pead.main does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
