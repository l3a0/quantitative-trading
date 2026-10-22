"""The pins for VX against ES, *Algorithmic Trading*'s hedge from August 2008.

This file is the single authority for every number a prose surface quotes
about this replication and the diagnostics beside it, with one exception, in
``blog/vx-es-lessons.md``. The post's figure has its own pins in
``tests/test_vx_es_figures.py``. README lists what the post says that nothing
pins. ``blog/crude-oil-reversal-momentum-lessons.md`` cites the APR on the
2012-05-07 save and on the 2012-05-17 save, falling by more than half, from
the pins here. ``docs/replication-log.md`` Entry 28 carries the verdicts and
points here row by row.

Every pin names one of three vintages and one of two specifications, so they
are stated once here.

- **Vintages.** Three saves of Chan's continuous futures, chan-mat, adjusted,
  read for VX's and ES's closes through ``chan.series.load_panel``, each leg
  cut to its own rows and then intersected. Each one's identity is its row of
  ``LIFTED_SOURCES`` in ``tests/support/committed_vintages.py``.

  1. ``inputdataohlcdaily_20120507/``, from ``inputDataOHLCDaily_20120507.mat``,
     saved 2012-05-09. VX runs 2,000 rows from 2004-06-01 and ES 2,000 rows
     from 2004-06-02, both to 2012-05-08, with 1,999 common days. Every row
     marked as the specification reads this save.
  2. ``inputdataohlcdaily_20120511/``, saved 2012-05-12, read for one row.
  3. ``inputdataohlcdaily_20120517/``, saved 2012-05-18, the save ``VX_ES.m``
     loads. VX runs from 2004-06-10 and ES from 2004-06-14, 2,000 rows each to
     2012-05-17, with 1,999 common days.

- **The specification.** ``ols(50·ES, [1000·VX, 1])`` on the first 500
  common days on or after 2008-08-04, which are 2008-08-04 to 2010-07-28. The
  hedge is minus the slope and the residual's deviation divides by n − 1. The
  z-score is the portfolio less the intercept over that deviation, from
  2008-08-04 on. ``chan.bollinger.band_units`` goes long below −1 and short
  above +1 and holds each until the opposite band. Returns are
  ``chan.price_spread.daily_returns`` on the dollar positions, measured on the
  449 rows from 2010-07-29 to 2012-05-08, annualised over 252 days with no
  risk-free rate and no cost.
- **The script as shipped.** ``VX_ES.m``, git blob ``ca480c4`` at
  EpchanPreview ``e4bc46f``: the same regression on every common day of the
  2012-05-17 save from 2008-08-01 to its end. It has no trade.

Each figure is held at the computed value's own precision, which is what lets
the log quote it, and the book's four at the precision Chan printed, through
``matches``.

Exploratory. Reproducing Chan's figures spends the 2008 to 2012 sample on a
rule he chose, and the save and the exit were chosen because they land the
printed figures. The run first ran on 2026-10-05.
"""

from __future__ import annotations

import io
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from chan import paths
from chan import vx_es as module
from chan.khandani_lo_book_two import gap, matches
from chan.series import WindowCrossesScaleBreak, load_panel, scale_breaks
from chan.vintage import VintageUnavailable
from chan.vx_es import (
    ANCHOR,
    BOOK_APR_PERCENT,
    BOOK_HEDGE,
    BOOK_RESIDUAL_STD,
    BOOK_SHARPE,
    BOOK_TEST_END,
    ES,
    MIDDLE_SOURCE_FILE,
    SCRIPT_SOURCE_FILE,
    SOURCE_FILE,
    TRAINING_DAYS,
    VX,
    VxEs,
    anchored,
    common_days,
    fit_hedge,
    main,
    mean_exit_units,
    opposite_band_units,
    portfolio_value,
    position_changes,
    read_legs,
    run,
    script_as_shipped,
    specification,
    trade,
    vx_es,
)
from tests.support.committed_vintages import LIFTED_SOURCES

SAVES = (SOURCE_FILE, MIDDLE_SOURCE_FILE, SCRIPT_SOURCE_FILE)


@pytest.fixture(scope="module")
def sources():
    return read_legs()


@pytest.fixture(scope="module")
def legs(sources) -> pd.DataFrame:
    return sources[1]


@pytest.fixture(scope="module")
def result(legs) -> VxEs:
    return vx_es(legs)


@pytest.fixture(scope="module")
def script_legs() -> pd.DataFrame:
    return read_legs(SCRIPT_SOURCE_FILE)[1]


@pytest.fixture
def no_arguments(monkeypatch):
    """``main`` parses ``sys.argv``, which under pytest holds pytest's own arguments."""
    monkeypatch.setattr("sys.argv", ["chan.vx_es"])


def _book(printed: str) -> str:
    """The book's figure as ``matches`` reads it, without its thousands comma."""
    return printed.replace(",", "")


class TestTheVintages:
    @pytest.mark.parametrize("source", SAVES)
    def test_each_save_is_its_pinned_source(self, source) -> None:
        members, _ = read_legs(source)
        vendor, basis, saved, folder, _ = LIFTED_SOURCES[source]
        assert {(m.vendor, m.price_basis, m.obtained) for m in members} == {(vendor, basis, saved)}
        assert sorted(m.path for m in members) == [f"{folder}/es.csv", f"{folder}/vx.csv"]

    def test_the_specification_reads_the_2012_05_07_save(self) -> None:
        assert SOURCE_FILE == "inputDataOHLCDaily_20120507.mat"
        assert LIFTED_SOURCES[SOURCE_FILE][2] == "2012-05-09"

    def test_the_script_reads_the_2012_05_17_save(self) -> None:
        assert SCRIPT_SOURCE_FILE == "inputDataOHLCDaily_20120517.mat"
        assert LIFTED_SOURCES[SCRIPT_SOURCE_FILE][2] == "2012-05-18"

    @pytest.mark.parametrize(
        ("source", "symbol", "first", "last"),
        [
            (SOURCE_FILE, VX, "2004-06-01", "2012-05-08"),
            (SOURCE_FILE, ES, "2004-06-02", "2012-05-08"),
            (SCRIPT_SOURCE_FILE, VX, "2004-06-10", "2012-05-17"),
            (SCRIPT_SOURCE_FILE, ES, "2004-06-14", "2012-05-17"),
        ],
    )
    def test_each_leg_keeps_its_own_calendar(self, source, symbol, first, last) -> None:
        leg = load_panel(source)[1][symbol].dropna()
        assert len(leg) == 2000
        assert str(leg.index[0].date()) == first
        assert str(leg.index[-1].date()) == last

    def test_the_common_calendar_is_1999_days(self, legs, script_legs) -> None:
        assert len(legs) == 1999
        assert str(legs.index[0].date()) == "2004-06-02"
        assert str(legs.index[-1].date()) == "2012-05-08"
        assert len(script_legs) == 1999
        assert np.isfinite(legs.to_numpy()).all()

    def test_the_saves_rewrite_the_history(self, legs, script_legs) -> None:
        """Issue 313's finding, on this window: the back-adjusted closes differ between saves."""
        shared = legs.index.intersection(script_legs.index)
        assert not np.allclose(legs.loc[shared, VX], script_legs.loc[shared, VX])


class TestTheSpans:
    def test_the_training_set_is_the_first_500_days_from_the_anchor(self, result) -> None:
        days = result.hedge.days
        assert ANCHOR == pd.Timestamp("2008-08-04")
        assert TRAINING_DAYS == 500
        assert len(days) == 500
        assert str(days[0].date()) == "2008-08-04"
        assert str(days[-1].date()) == "2010-07-28"

    def test_the_test_set_is_the_book_s(self, result) -> None:
        """ "The APR on the test set July 29, 2010, to May 8, 2012"."""
        days = result.trade.test_days
        assert len(days) == 449 == len(result.trade.daily)
        assert str(days[0].date()) == "2010-07-29"
        assert str(days[-1].date()) == "2012-05-08"
        assert BOOK_TEST_END == days[-1]

    def test_the_band_runs_from_the_anchor(self, result) -> None:
        assert len(result.trade.days) == 949
        assert result.trade.days[0] == ANCHOR


class TestTheSpecification:
    """The four printed figures, on the 2012-05-07 save, training rows 1 to 500."""

    def test_the_hedge(self, result) -> None:
        assert result.hedge.hedge == pytest.approx(0.390594, abs=5e-7)
        assert matches(result.hedge.hedge, BOOK_HEDGE)

    def test_the_residual_standard_deviation_misses_by_two_dollars(self, result) -> None:
        assert result.hedge.residual_std == pytest.approx(2044.91, abs=0.005)
        assert not matches(result.hedge.residual_std, _book(BOOK_RESIDUAL_STD))
        assert gap(result.hedge.residual_std, _book(BOOK_RESIDUAL_STD)) == -2
        assert 2047 - result.hedge.residual_std == pytest.approx(2.09, abs=0.005)

    def test_the_apr(self, result) -> None:
        assert result.trade.apr == pytest.approx(0.122811, abs=5e-7)
        assert matches(100 * result.trade.apr, BOOK_APR_PERCENT)

    def test_the_sharpe_ratio(self, result) -> None:
        assert result.trade.sharpe == pytest.approx(1.393201, abs=5e-7)
        assert matches(result.trade.sharpe, BOOK_SHARPE)

    def test_the_book_s_figures_as_printed(self) -> None:
        assert (BOOK_HEDGE, BOOK_RESIDUAL_STD, BOOK_APR_PERCENT, BOOK_SHARPE) == (
            "0.3906",
            "2,047",
            "12.3",
            "1.4",
        )


class TestTheTrade:
    """Item 7 of the plan: the result rests on four holding periods."""

    def test_the_portfolio_is_long_at_the_close_of_the_last_training_day(self, result) -> None:
        t = result.trade
        assert t.zscore[TRAINING_DAYS - 1] == pytest.approx(-1.041, abs=5e-4)
        assert t.units[TRAINING_DAYS - 1] == 1

    def test_it_changes_position_three_times_in_the_test(self, result) -> None:
        assert [(str(day.date()), units) for day, units in position_changes(result.trade)] == [
            ("2011-11-08", -1.0),
            ("2011-12-19", 1.0),
            ("2012-02-17", -1.0),
        ]

    def test_it_is_in_the_market_on_every_test_day(self, result) -> None:
        held = result.trade.units[TRAINING_DAYS - 1 : -1]
        assert len(held) == 449
        assert (held != 0).all()
        assert np.count_nonzero(result.trade.daily) == 449

    def test_more_test_days_sit_beyond_a_band_than_training_days(self, result) -> None:
        beyond = np.abs(result.trade.zscore) > 1
        assert beyond[TRAINING_DAYS:].sum() == 236
        assert beyond[:TRAINING_DAYS].sum() == 113

    def test_the_band_from_the_calendar_s_first_day_gives_the_same_figures(
        self, legs, result
    ) -> None:
        """Item 6: starting the band on 2004-06-02 rather than the anchor moves nothing."""
        rows = legs.loc[:BOOK_TEST_END]
        whole = trade(rows, result.hedge, test_from=len(rows) - 449)
        assert str(whole.days[0].date()) == "2004-06-02"
        assert whole.test_days.equals(result.trade.test_days)
        assert whole.apr == result.trade.apr
        assert whole.sharpe == result.trade.sharpe


@pytest.fixture(scope="module")
def cumulative(result) -> pd.Series:
    """The test set's compounded cumulative return, ``cumprod(1 + ret) − 1``."""
    return pd.Series(np.cumprod(1 + result.trade.daily) - 1, index=result.trade.test_days)


class TestTheDowngrade:
    """Location 2559: "particularly profitable starting around the time of the Standard and
    Poor's downgrade of the U.S. credit rating", announced after the close of 2011-08-05.

    ``blog/vx-es-lessons.md`` quotes each figure here. Each compounds the
    specification's own test-set returns.
    """

    DOWNGRADE = pd.Timestamp("2011-08-05")

    def test_the_test_set_ends_where_the_apr_says(self, result, cumulative) -> None:
        assert cumulative.iloc[-1] == pytest.approx(0.229231, abs=5e-7)
        assert cumulative.iloc[-1] == pytest.approx((1 + result.trade.apr) ** (449 / 252) - 1)

    def test_it_is_down_at_the_close_of_the_downgrade_day(self, cumulative) -> None:
        before = cumulative.loc[: self.DOWNGRADE]
        assert len(before) == 259
        assert before.iloc[-1] == pytest.approx(-0.045935, abs=5e-7)

    def test_the_whole_gain_and_more_comes_after_that_close(self, cumulative) -> None:
        """The share earned after the close is more than all of it, since it was a loss before."""
        at_close = cumulative.loc[self.DOWNGRADE]
        after = (1 + cumulative.iloc[-1]) / (1 + at_close) - 1
        assert len(cumulative.loc[self.DOWNGRADE :]) - 1 == 190
        assert after == pytest.approx(0.288414, abs=5e-7)
        assert after > cumulative.iloc[-1] > 0 > at_close

    def test_the_deepest_point_is_the_first_day_after_the_announcement(
        self, result, cumulative
    ) -> None:
        assert str(cumulative.idxmin().date()) == "2011-08-08"
        assert cumulative.min() == pytest.approx(-0.077553, abs=5e-7)
        low = int(np.argmin(result.trade.zscore))
        assert str(result.trade.days[low].date()) == "2011-08-08"
        assert result.trade.zscore[low] == pytest.approx(-3.886, abs=5e-4)
        assert result.trade.units[low] == 1

    def test_each_of_the_four_bets_earns(self, result) -> None:
        """What each holding period earned, compounded over the test days it was held.

        A position taken at a day's close earns from the next day, so the long
        carried in earns through 2011-11-08 and the short taken that evening
        earns from 2011-11-09.
        """
        held = result.trade.units[TRAINING_DAYS - 1 : -1]
        daily = pd.Series(result.trade.daily, index=result.trade.test_days)
        starts = [0, *(np.flatnonzero(np.diff(held)) + 1), len(held)]
        bets = [
            (
                str(daily.index[a].date()),
                str(daily.index[b - 1].date()),
                held[a],
                b - a,
                float(np.prod(1 + daily.iloc[a:b]) - 1),
            )
            for a, b in zip(starts, starts[1:], strict=False)
        ]
        assert [bet[:4] for bet in bets] == [
            ("2010-07-29", "2011-11-08", 1, 325),
            ("2011-11-09", "2011-12-19", -1, 28),
            ("2011-12-20", "2012-02-17", 1, 41),
            ("2012-02-21", "2012-05-08", -1, 55),
        ]
        assert [bet[4] for bet in bets] == pytest.approx(
            [0.058104, 0.056144, 0.056877, 0.040777], abs=5e-7
        )


class TestTheDiagnostics:
    """The rows of the plan's table other than the specification."""

    def test_dropping_the_first_training_row_reaches_both_printed_figures(self, result) -> None:
        dropped, traded = result.first_row_dropped
        assert str(dropped.days[0].date()) == "2008-08-05"
        assert len(dropped.days) == 499
        assert dropped.hedge == pytest.approx(0.390635, abs=5e-7)
        assert dropped.residual_std == pytest.approx(2046.93, abs=0.005)
        assert matches(dropped.hedge, BOOK_HEDGE)
        assert matches(dropped.residual_std, _book(BOOK_RESIDUAL_STD))
        assert traded.apr == pytest.approx(0.122804, abs=5e-7)
        assert traded.sharpe == pytest.approx(1.393228, abs=5e-7)

    def test_an_exit_at_the_mean_misses(self, result) -> None:
        t = result.exit_at_mean
        assert t.apr == pytest.approx(0.068463, abs=5e-7)
        assert t.sharpe == pytest.approx(0.870716, abs=5e-7)
        assert not matches(100 * t.apr, BOOK_APR_PERCENT)
        assert not matches(t.sharpe, BOOK_SHARPE)

    def test_starting_flat_on_the_first_test_day_misses(self, result) -> None:
        t = result.flat_at_test
        assert t.test_days.equals(result.trade.test_days)
        assert t.daily[0] == 0
        assert t.apr == pytest.approx(0.124916, abs=5e-7)
        assert t.sharpe == pytest.approx(1.415772, abs=5e-7)
        assert not matches(100 * t.apr, BOOK_APR_PERCENT)
        assert gap(100 * t.apr, BOOK_APR_PERCENT) == pytest.approx(0.2)
        # ``blog/vx-es-lessons.md`` says the flat start lands the Sharpe ratio and misses
        # only the APR.
        assert matches(t.sharpe, BOOK_SHARPE)

    def test_the_printed_constant_moves_nothing_that_prints(self, result) -> None:
        """Item 10: issue 357 takes 0.3906 as a constant, and this row says that is safe."""
        t = result.book_hedge
        assert t.apr == pytest.approx(0.122810, abs=5e-7)
        assert t.sharpe == pytest.approx(1.393205, abs=5e-7)
        assert matches(100 * t.apr, BOOK_APR_PERCENT)
        assert matches(t.sharpe, BOOK_SHARPE)

    def test_the_2012_05_17_save_misses(self, script_legs) -> None:
        fitted, traded = specification(script_legs)
        assert str(fitted.days[0].date()) == "2008-08-04"
        assert str(fitted.days[-1].date()) == "2010-07-28"
        assert str(traded.test_days[-1].date()) == "2012-05-08"
        assert len(traded.daily) == 449
        assert fitted.hedge == pytest.approx(0.376431, abs=5e-7)
        assert fitted.residual_std == pytest.approx(2291.00, abs=0.005)
        assert traded.apr == pytest.approx(0.056582, abs=5e-7)
        assert traded.sharpe == pytest.approx(0.673910, abs=5e-7)
        assert not matches(fitted.hedge, BOOK_HEDGE)
        assert not matches(fitted.residual_std, _book(BOOK_RESIDUAL_STD))
        assert not matches(100 * traded.apr, BOOK_APR_PERCENT)
        assert not matches(traded.sharpe, BOOK_SHARPE)

    def test_the_2012_05_11_save_agrees_with_the_2012_05_17_save(self, script_legs) -> None:
        middle_hedge, middle_trade = specification(read_legs(MIDDLE_SOURCE_FILE)[1])
        later_hedge, later_trade = specification(script_legs)
        assert middle_hedge.hedge == later_hedge.hedge
        assert middle_hedge.residual_std == later_hedge.residual_std
        assert middle_trade.apr == later_trade.apr
        assert middle_trade.sharpe == later_trade.sharpe

    def test_the_script_as_shipped(self, script_legs) -> None:
        fitted = script_as_shipped(script_legs)
        assert len(fitted.days) == 957
        assert str(fitted.days[0].date()) == "2008-08-01"
        assert str(fitted.days[-1].date()) == "2012-05-17"
        assert fitted.hedge == pytest.approx(0.350731, abs=5e-7)
        assert fitted.residual_std == pytest.approx(2373.59, abs=0.005)

    def test_the_script_s_fit_includes_the_whole_test_set(self, script_legs) -> None:
        fitted = script_as_shipped(script_legs)
        assert fitted.days[-1] > BOOK_TEST_END


class TestTheRule:
    def test_common_days_cuts_each_leg_before_intersecting(self) -> None:
        days = pd.to_datetime(["2010-01-04", "2010-01-05", "2010-01-06", "2010-01-07"])
        closes = pd.DataFrame(
            {ES: [1000.0, np.nan, 1010.0, 1020.0], VX: [np.nan, 20.0, 21.0, 22.0]}, index=days
        )
        out = common_days(closes)
        assert list(out.index) == list(days[2:])
        assert list(out.columns) == [VX, ES]

    def test_fit_hedge_recovers_a_known_relation(self) -> None:
        """``50·ES = 80,000 − 0.4·1000·VX`` plus noise gives a hedge of 0.4."""
        rng = np.random.default_rng(0)
        vx = 20 + rng.standard_normal(400)
        noise = rng.standard_normal(400)
        es = (80_000 - 0.4 * 1000 * vx + noise) / 50
        fitted = fit_hedge(pd.DataFrame({VX: vx, ES: es}))
        assert fitted.hedge == pytest.approx(0.4, abs=0.01)
        assert fitted.intercept == pytest.approx(80_000, abs=50)
        assert fitted.residual_std == pytest.approx(np.std(noise, ddof=1), rel=0.01)

    def test_a_position_is_held_until_the_opposite_band(self) -> None:
        z = np.array([0.0, -1.5, 0.5, 0.9, 1.5, 0.0, -0.5, -1.2, 2.0])
        assert opposite_band_units(z).tolist() == [0, 1, 1, 1, -1, -1, -1, 1, -1]

    def test_the_mean_exit_closes_at_zero(self) -> None:
        z = np.array([0.0, -1.5, -0.5, 0.5, 1.5, 0.5, -0.5])
        assert mean_exit_units(z).tolist() == [0, 1, 1, 0, -1, -1, 0]

    def test_the_band_is_one_deviation_and_strict(self) -> None:
        assert opposite_band_units(np.array([0.0, -1.0, 1.0])).tolist() == [0, 0, 0]
        assert opposite_band_units(np.array([0.0, -1.5, 1.0])).tolist() == [0, 1, 1]
        assert opposite_band_units(np.array([0.0, 1.5, -1.0])).tolist() == [0, -1, -1]

    def test_the_first_test_day_earns_the_position_carried_into_it(self, legs, result) -> None:
        rows = anchored(legs)
        vx = rows[VX].to_numpy()
        es = rows[ES].to_numpy()
        h = result.hedge.hedge
        i = TRAINING_DAYS
        held = np.array([h * 1000 * vx[i - 1], 50 * es[i - 1]])
        profit = held @ (np.array([vx[i], es[i]]) / np.array([vx[i - 1], es[i - 1]]) - 1)
        assert result.trade.daily[0] == pytest.approx(profit / np.abs(held).sum(), rel=1e-12)

    def test_the_rounded_hedge_keeps_the_fitted_intercept_and_deviation(self, legs, result) -> None:
        expected = (
            portfolio_value(anchored(legs), float(BOOK_HEDGE)) - result.hedge.intercept
        ) / result.hedge.residual_std
        np.testing.assert_allclose(result.book_hedge.zscore, expected, rtol=1e-12)

    def test_the_zscore_is_the_portfolio_less_the_intercept_over_the_deviation(
        self, legs, result
    ) -> None:
        expected = (
            portfolio_value(anchored(legs), result.hedge.hedge) - result.hedge.intercept
        ) / result.hedge.residual_std
        np.testing.assert_allclose(result.trade.zscore, expected, rtol=1e-12)

    def test_position_changes_reads_the_test_rows_only(self) -> None:
        """A change on the last training day is not reported, and one on the first test day is."""
        units = np.array([0.0, 1.0, -1.0, -1.0, 1.0])
        days = pd.date_range("2010-07-26", periods=5, freq="B")
        traded = module.Trade(
            days=days,
            zscore=np.zeros(5),
            units=units,
            test_days=days[2:],
            daily=np.zeros(3),
        )
        assert position_changes(traded) == [(days[2], -1.0), (days[4], 1.0)]


class TestTheGuardAndTheReads:
    @pytest.mark.parametrize("source", SAVES)
    def test_neither_leg_carries_a_flagged_day(self, source) -> None:
        """``tests/test_scale_breaks.py`` names ZB and ZF as the only flagged series here."""
        closes = load_panel(source)[1]
        assert scale_breaks(closes[VX].dropna()) == []
        assert scale_breaks(closes[ES].dropna()) == []

    @pytest.mark.parametrize("source", SAVES)
    def test_read_legs_guards_each_leg_over_its_own_span(self, source, monkeypatch) -> None:
        seen = []

        def record(legs, *, start, end):
            seen.append(([entry.symbol for entry, _ in legs], start, end))

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", record)
        read_legs(source)
        closes = load_panel(source)[1]
        assert seen == [
            ([symbol], closes[symbol].dropna().index[0], closes[symbol].dropna().index[-1])
            for symbol in (ES, VX)
        ]

    @pytest.mark.parametrize("symbol", [VX, ES])
    @pytest.mark.parametrize("row", [1, 1000, 1999])
    def test_either_leg_changing_scale_anywhere_is_refused(self, symbol, row, monkeypatch) -> None:
        members, closes = load_panel(SOURCE_FILE)
        broken = closes.copy()
        leg = broken[symbol].dropna()
        broken.loc[leg.index[row:], symbol] *= 10
        monkeypatch.setattr(module, "load_panel", lambda *_a, **_k: (members, broken))
        with pytest.raises(WindowCrossesScaleBreak, match=f"{symbol.lower()}.csv"):
            read_legs()

    def test_run_reads_the_two_saves(self, monkeypatch, capsys) -> None:
        seen = []
        real = module.read_legs

        def record(source_file=SOURCE_FILE, data_dir=None):
            seen.append((source_file, data_dir))
            return real(source_file, data_dir)

        monkeypatch.setattr(module, "read_legs", record)
        run(paths.DATA_DIR)
        assert seen == [(SOURCE_FILE, paths.DATA_DIR), (SCRIPT_SOURCE_FILE, paths.DATA_DIR)]

    def test_a_refusal_from_the_guard_reaches_the_caller(self, monkeypatch) -> None:
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("flagged")

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(WindowCrossesScaleBreak, match="flagged"):
            run()

    def test_main_turns_a_guard_refusal_into_one_line(self, monkeypatch, no_arguments) -> None:
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("inputdataohlcdaily_20120507/vx.csv changes scale")

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(SystemExit, match="vx.csv changes scale"):
            main()

    def test_run_reads_the_directory_it_is_given(self, tmp_path) -> None:
        with pytest.raises(VintageUnavailable, match="inputDataOHLCDaily_20120507.mat"):
            run(tmp_path)

    def test_main_turns_a_missing_vintage_into_one_line(
        self, monkeypatch, tmp_path, no_arguments
    ) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit, match="inputDataOHLCDaily_20120507.mat"):
            main()

    def test_a_miss_is_reported_as_one(self) -> None:
        assert module._verdict(2044.906966, "2,047") == "did not reproduce, gap -2"
        assert module._verdict(0.390594, "0.3906") == "reproduced"
        assert module._verdict(0.3916, "0.3906") == "did not reproduce, gap +0.001"


@pytest.fixture(scope="module")
def printed() -> str:
    """What ``run`` prints, captured once for the two tests that read it."""
    out = io.StringIO()
    with redirect_stdout(out):
        run()
    return out.getvalue()


class TestTheReport:
    def test_it_prints_each_figure_beside_the_book_s(self, printed) -> None:
        out = printed
        for label, figures in (
            ("Hedge, VX contracts per ES", ["0.390594", "0.3906", "reproduced"]),
            ("Residual standard deviation, $", ["2044.906966", "2,047", "did", "not"]),
            ("APR, percent", ["12.281057", "12.3", "reproduced"]),
            ("Sharpe ratio", ["1.393201", "1.4", "reproduced"]),
        ):
            row = next(r for r in out.splitlines() if r.strip().startswith(label))
            assert all(f in row.split() for f in figures), row
        assert "inputdataohlcdaily_20120507/" in out
        assert "training  2008-08-04 to 2010-07-28, 500 days" in out
        assert "test      2010-07-29 to 2012-05-08, 449 days" in out
        assert (
            "held at the close of 2010-07-28: +1, then "
            "short 2011-11-08, long 2011-12-19, short 2012-02-17"
        ) in out
        assert "Exploratory." in out

    def test_it_prints_each_diagnostic(self, printed) -> None:
        out = printed
        for label, figures in (
            ("Training rows 2 to 500", ["0.390635", "2046.93", "0.122804", "1.393228"]),
            ("Exit at the mean", ["0.390594", "2044.91", "0.068463", "0.870716"]),
            ("Flat on the first test day", ["0.390594", "2044.91", "0.124916", "1.415772"]),
            ("Trading the printed 0.3906", ["0.390600", "2044.91", "0.122810", "1.393205"]),
            ("The 2012-05-17 save", ["0.376431", "2291.00", "0.056582", "0.673910"]),
            ("VX_ES.m as shipped", ["0.350731", "2373.59", "none", "none"]),
        ):
            row = next(r for r in out.splitlines() if r.strip().startswith(label))
            assert row.split()[-4:] == figures, row


POST = Path(__file__).parents[1] / "blog" / "vx-es-lessons.md"


def _minus(x: float, places: int) -> str:
    """A number as the post prints it, with a true minus sign."""
    return f"{x:.{places}f}".replace("-", "−")


def _tex_dollars(x: float) -> str:
    """Dollars as the post's tables print them, ``\\$2{,}044.91``."""
    return f"\\${x:,.2f}".replace(",", "{,}")


def _lands(traded) -> str:
    """Lesson 3's last column: which of the book's APR and Sharpe ratio a rule lands."""
    apr = matches(100 * traded.apr, BOOK_APR_PERCENT)
    sharpe = matches(traded.sharpe, BOOK_SHARPE)
    return {(True, True): "both", (False, False): "neither"}.get(
        (apr, sharpe), "APR" if apr else "Sharpe"
    )


def _bets(traded) -> list[tuple[str, str, float, int, float, float]]:
    """Each holding period's first and last test day earned, units, days, return and worst."""
    held = traded.units[TRAINING_DAYS - 1 : -1]
    daily = pd.Series(traded.daily, index=traded.test_days)
    starts = [0, *(np.flatnonzero(np.diff(held)) + 1), len(held)]
    return [
        (
            str(daily.index[a].date()),
            str(daily.index[b - 1].date()),
            held[a],
            b - a,
            float(np.prod(1 + daily.iloc[a:b]) - 1),
            float(np.min(np.cumprod(1 + daily.iloc[a:b])) - 1),
        )
        for a, b in zip(starts, starts[1:], strict=False)
    ]


def post_fragments(legs, script_legs, result) -> list[str]:
    """The sentences and table rows of ``blog/vx-es-lessons.md`` that quote the run."""
    h, t = result.hedge, result.trade
    dropped, _ = result.first_row_dropped
    later_hedge, later_trade = specification(script_legs)
    shipped = script_as_shipped(script_legs)
    mean, flat, printed = result.exit_at_mean, result.flat_at_test, result.book_hedge
    cumulative = pd.Series(np.cumprod(1 + t.daily) - 1, index=t.test_days)
    downgrade = pd.Timestamp("2011-08-05")
    at_close = cumulative.loc[downgrade]
    after = (1 + cumulative.iloc[-1]) / (1 + at_close) - 1
    beyond = np.abs(t.zscore) > 1
    held = t.units[TRAINING_DAYS - 1 : -1]
    changes = [str(day.date()) for day, _ in position_changes(t)]
    bets = _bets(t)
    n = len(t.test_days)

    def verdict(value: float, book: str) -> str:
        plain = _book(book)
        return (
            "\\text{lands}"
            if matches(value, plain)
            else f"\\text{{misses by }}\\${abs(value - float(plain)):.2f}"
        )

    fragments = [
        f"VX and ES share {len(legs):,} trading days, from {legs.index[0].date()}"
        f" to {legs.index[-1].date()}",
        f"It also holds {len(script_legs):,} common days, ending {script_legs.index[-1].date()}",
        f"over the {len(h.days)} common days from {h.days[0].date()} to {h.days[-1].date()}",
        f"The {n} days from {t.test_days[0].date()} to {t.test_days[-1].date()}",
        # Lesson 1's table, each figure beside the book's and the verdict between them.
        f"\\text{{Hedge}} & {h.hedge:.6f} & {BOOK_HEDGE} & {verdict(h.hedge, BOOK_HEDGE)}",
        f"\\text{{Deviation}} & {_tex_dollars(h.residual_std)}"
        f" & \\${BOOK_RESIDUAL_STD.replace(',', '{,}')}"
        f" & {verdict(h.residual_std, BOOK_RESIDUAL_STD)}",
        f"\\text{{APR}} & {t.apr:.6f} & {BOOK_APR_PERCENT}\\%"
        f" & {verdict(100 * t.apr, BOOK_APR_PERCENT)}",
        f"\\text{{Sharpe}} & {t.sharpe:.6f} & {BOOK_SHARPE} & {verdict(t.sharpe, BOOK_SHARPE)}",
        f"so {t.apr:.6f} is {100 * t.apr:.2f} percent",
        f"from {dropped.days[0].date()}, lands both, at {dropped.hedge:.6f}"
        f" and \\${dropped.residual_std:,.2f}",
        f"gives an APR of {printed.apr:.6f} and a Sharpe ratio of {printed.sharpe:.6f}",
        # Lesson 2's table, the 2012-05-07 save beside the later saves and the script.
        f"\\text{{Hedge}} & {h.hedge:.6f} & {later_hedge.hedge:.6f} & {shipped.hedge:.6f}",
        f"\\text{{Deviation}} & {_tex_dollars(h.residual_std)}"
        f" & {_tex_dollars(later_hedge.residual_std)} & {_tex_dollars(shipped.residual_std)}",
        f"\\text{{APR}} & {t.apr:.6f} & {later_trade.apr:.6f} & \\text{{no trade}}",
        f"\\text{{Sharpe}} & {t.sharpe:.6f} & {later_trade.sharpe:.6f} & \\text{{no trade}}",
        f"every day from {shipped.days[0].date()} to the end of the file",
        f"That fit runs over {len(shipped.days)} days, through {shipped.days[-1].date()}",
        # Lesson 3's table and the sentences after it.
        f"\\text{{Opposite band}} & {t.apr:.6f} & {t.sharpe:.6f} & \\text{{{_lands(t)}}}",
        f"\\text{{Mean}} & {mean.apr:.6f} & {mean.sharpe:.6f} & \\text{{{_lands(mean)}}}",
        f"\\text{{Flat start}} & {flat.apr:.6f} & {flat.sharpe:.6f} & \\text{{{_lands(flat)}}}",
        f"this trade earns {100 * mean.apr:.1f} percent a year rather than {BOOK_APR_PERCENT}",
        f"the z-score is {_minus(t.zscore[TRAINING_DAYS - 1], 3)}",
        f"misses the APR, at {100 * flat.apr:.1f} percent",
        # Lesson 4: the four bets, the downgrade and the band.
        f"changes position at the close of {', '.join(changes[:-1])} and {changes[-1]}",
        f"the last one earns through {bets[-1][1]}",
        f"in the market on all {np.count_nonzero(held)} test days",
        f"make the test set’s {100 * cumulative.iloc[-1]:.2f} percent",
        f"after {len(cumulative.loc[:downgrade])} of the {n} test days, the trade was down"
        f" {-100 * at_close:.2f} percent",
        f"On Monday {cumulative.idxmin().date()} it reached its lowest point,"
        f" down {-100 * cumulative.min():.2f} percent, and the z-score reached"
        f" {_minus(t.zscore.min(), 2)}",
        f"grew {100 * after:.2f} percent in {len(cumulative.loc[downgrade:]) - 1} days",
        f"spent its {bets[0][3]} test days earning {100 * bets[0][4]:.2f} percent,"
        f" and was down {-100 * bets[0][5]:.2f} percent at its worst",
        f"on {beyond[TRAINING_DAYS:].sum()} of the {n} test days, against"
        f" {beyond[:TRAINING_DAYS].sum()} of the {TRAINING_DAYS} training days",
        f"Each unit also holds {h.hedge:.2f} of a VX contract",
    ]
    fragments += [
        f"\\text{{{'Long' if units > 0 else 'Short'}}} & \\text{{{first}}} & {days} & {earned:.6f}"
        for first, _, units, days, earned, _ in bets
    ]
    return fragments


class TestThePostQuotesTheRun:
    """``blog/vx-es-lessons.md`` prints what the run computes, read here from the run.

    The pins above hold the run's numbers. This class holds that the post
    prints them, so a figure edited in the post alone fails here. It reads
    every row of the four tables with its verdict, and one copy of each figure
    the run computes that the prose writes in numerals. README says what it
    does not read.
    """

    def test_the_post_prints_each_figure_the_run_computes(self, legs, script_legs, result) -> None:
        text = POST.read_text(encoding="utf-8")
        assert [f for f in post_fragments(legs, script_legs, result) if f not in text] == []
