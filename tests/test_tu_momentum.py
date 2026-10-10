"""The pins for time-series momentum on TU, *Algorithmic Trading*'s Example 6.1.

This file is the single authority for every number a prose surface quotes
about this example and the rows beside it. ``docs/replication-log.md`` Entry 32
carries the verdicts and points here row by row.

Every pin on the committed files reads one of two vintages and one
specification, so they are stated once here.

- **Vintage.** ``inputdataohlcdaily_20120511/tu.csv``, chan-mat, adjusted,
  saved 2012-05-12, lifted from ``inputDataOHLCDaily_20120511.mat``. TU's own
  column holds 2,000 days from 2004-06-01 to 2012-05-11, read through
  ``chan.series.load_panel`` as ``closes["TU"].dropna()``. Its identity is its
  row of ``LIFTED_SOURCES`` in ``tests/support/committed_vintages.py``. Every
  pin reads it unless it names the second.
- **The second vintage.** ``inputdataohlcdaily_20120517/tu.csv``, chan-mat,
  adjusted, saved 2012-05-18, the save ``correlationTest.m`` loads, 2,000 days
  from 2004-06-07 to 2012-05-17. ``TestTheSave`` alone reads it.
- **Specification.** ``TU_mom.m`` at EpchanPreview ``e4bc46f``, git blob
  ``f7935c7``, with ``idx = 1``, as :mod:`chan.tu_momentum` transcribes it.
  The correlation table takes past and future returns for every pair of 1, 5,
  10, 25, 60, 120 and 250 days, deletes the rows where either is NaN, keeps
  every ``min(lookback, hold)``-th row and correlates them. H is
  ``genhurst(log(cl), 2)`` at ``maxT`` 19 and the variance ratio test is
  ``vratiotest(log(cl))`` at period 2. The rule is long where the close is
  above the close 250 rows back and short where below, each day's signal held
  25 days, and the return is yesterday's position times today's return over
  25. The figures read all 2,000 returns, annualised over 252 days with no
  risk-free rate and no cost.

Each computed figure is held at six decimals, so a change cannot move it inside
the published rounding unnoticed, and each published figure at the precision
Chan printed, through ``matches``.

Exploratory. Reproducing Chan's figures spends the 2004 to 2012 sample on a
lookback and a hold chosen from the same table. The example first ran on
2026-10-06.
"""

from __future__ import annotations

import io
from contextlib import redirect_stdout

import numpy as np
import pandas as pd
import pytest

from chan import paths
from chan import tu_momentum as module
from chan.khandani_lo_book_two import gap, matches
from chan.matlab_helpers import backshift
from chan.series import WindowCrossesScaleBreak, load_panel, scale_breaks
from chan.tu_momentum import (
    ACTIVE_LINE_START,
    BOOK_APR_PERCENT,
    BOOK_CORRELATION,
    BOOK_FIRST_DAY,
    BOOK_HURST,
    BOOK_LAST_DAY,
    BOOK_MAX_DRAWDOWN_PERCENT,
    BOOK_P_VALUE,
    BOOK_SHARPE,
    COMPROMISES,
    HOLD_DAYS,
    HURST_DIAGNOSTIC_MAX_T,
    LATER_SOURCE_FILE,
    LOOKBACK,
    PERIODS,
    SCRIPT_APR,
    SCRIPT_AVERAGE_ANNUAL_RETURN,
    SCRIPT_GAUSSIAN_STATISTIC,
    SCRIPT_KELLY,
    SCRIPT_MAX_DRAWDOWN,
    SCRIPT_MAX_DRAWDOWN_DAYS,
    SCRIPT_SHARPE,
    SOURCE_FILE,
    SYMBOL,
    TuMomentum,
    correlation,
    figures,
    gaussian_statistic,
    hurst_at,
    main,
    market_returns,
    positions,
    read_later_save,
    read_sources,
    run,
    signals,
    strategy_returns,
    tu_momentum,
)
from chan.usdcad_mean_reversion import read_sources as read_usdcad
from tests.support.committed_vintages import LIFTED_SOURCES

#: The 49 cells on the 2012-05-11 save at four decimals, ``(lookback, hold): (r, p)``.
TABLE = {
    (1, 1): (-0.0576, 0.0100),
    (1, 5): (-0.0755, 0.0007),
    (1, 10): (-0.0288, 0.1998),
    (1, 25): (-0.0152, 0.5010),
    (1, 60): (0.0293, 0.1973),
    (1, 120): (0.0185, 0.4237),
    (1, 250): (0.0377, 0.1149),
    (5, 1): (-0.0756, 0.0007),
    (5, 5): (-0.1271, 0.0111),
    (5, 10): (-0.0474, 0.3459),
    (5, 25): (0.0304, 0.5471),
    (5, 60): (0.0784, 0.1235),
    (5, 120): (0.0511, 0.3241),
    (5, 250): (0.1022, 0.0566),
    (10, 1): (-0.0280, 0.2118),
    (10, 5): (-0.0485, 0.3348),
    (10, 10): (0.0366, 0.6087),
    (10, 25): (0.1124, 0.1159),
    (10, 60): (0.1675, 0.0199),
    (10, 120): (0.0848, 0.2485),
    (10, 250): (0.1686, 0.0262),
    (25, 1): (-0.0140, 0.5353),
    (25, 5): (0.0319, 0.5276),
    (25, 10): (0.1219, 0.0880),
    (25, 25): (0.1955, 0.0863),
    (25, 60): (0.2333, 0.0411),
    (25, 120): (0.1482, 0.2045),
    (25, 250): (0.2620, 0.0297),
    (60, 1): (0.0313, 0.1686),
    (60, 5): (0.0799, 0.1168),
    (60, 10): (0.1718, 0.0169),
    (60, 25): (0.2592, 0.0228),
    (60, 60): (0.2162, 0.2346),
    (60, 120): (-0.0331, 0.8598),
    (60, 250): (0.3137, 0.0974),
    (120, 1): (0.0222, 0.3355),
    (120, 5): (0.0565, 0.2750),
    (120, 10): (0.0955, 0.1934),
    (120, 25): (0.1456, 0.2126),
    (120, 60): (-0.0192, 0.9182),
    (120, 120): (0.2081, 0.4567),
    (120, 250): (0.4072, 0.1484),
    (250, 1): (0.0411, 0.0857),
    (250, 5): (0.1068, 0.0462),
    (250, 10): (0.1784, 0.0185),
    (250, 25): (0.2719, 0.0238),
    (250, 60): (0.4245, 0.0217),
    (250, 120): (0.5112, 0.0617),
    (250, 250): (0.4873, 0.3269),
}


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def closes(sources) -> pd.Series:
    return sources[1]


@pytest.fixture(scope="module")
def result(closes) -> TuMomentum:
    return tu_momentum(closes)


@pytest.fixture(scope="module")
def later() -> TuMomentum:
    return tu_momentum(read_later_save()[1])


@pytest.fixture
def no_arguments(monkeypatch):
    """``main`` parses ``sys.argv``, which under pytest holds pytest's own arguments."""
    monkeypatch.setattr("sys.argv", ["chan.tu_momentum"])


class TestTheSpecification:
    def test_the_rule_is_250_days_back_and_25_held(self) -> None:
        assert (LOOKBACK, HOLD_DAYS) == (250, 25)
        assert PERIODS == (1, 5, 10, 25, 60, 120, 250)

    def test_the_script_s_printed_figures(self) -> None:
        assert (
            SCRIPT_AVERAGE_ANNUAL_RETURN,
            SCRIPT_SHARPE,
            SCRIPT_APR,
            SCRIPT_MAX_DRAWDOWN,
            SCRIPT_MAX_DRAWDOWN_DAYS,
            SCRIPT_KELLY,
        ) == ("0.0167", "1.04", "0.0167", "-0.024847", 343, "64.919535")

    def test_the_book_s_printed_figures(self) -> None:
        assert (
            BOOK_CORRELATION,
            BOOK_P_VALUE,
            BOOK_HURST,
            BOOK_SHARPE,
            BOOK_APR_PERCENT,
            BOOK_MAX_DRAWDOWN_PERCENT,
        ) == ("0.27", "0.02", "0.44", "1", "1.7", "2.5")

    def test_the_specification_reads_every_row(self, result) -> None:
        """``idx = 1``: the figures read all 2,000 returns, from the book's first day."""
        assert len(result.daily) == 2000
        assert result.days[0] == BOOK_FIRST_DAY
        assert result.days[-1] == BOOK_LAST_DAY


class TestTheVintage:
    def test_tu_is_its_pinned_source(self, sources) -> None:
        entry, _ = sources
        vendor, basis, saved, folder, _ = LIFTED_SOURCES[SOURCE_FILE]
        assert SOURCE_FILE == "inputDataOHLCDaily_20120511.mat"
        assert (entry.vendor, entry.price_basis, entry.obtained) == (vendor, basis, saved)
        assert saved == "2012-05-12"
        assert entry.path == f"{folder}/tu.csv" == "inputdataohlcdaily_20120511/tu.csv"
        assert entry.symbol == SYMBOL == "TU"

    def test_tu_s_own_column_is_2000_days_from_the_book_s_first(self, closes) -> None:
        assert len(closes) == 2000
        assert str(closes.index[0].date()) == "2004-06-01"
        assert str(closes.index[-1].date()) == "2012-05-11"
        assert np.isfinite(closes.to_numpy()).all()

    def test_read_sources_is_load_panel_s_column_without_its_nan(self, closes) -> None:
        panel = load_panel(SOURCE_FILE)[1]
        pd.testing.assert_series_equal(closes, panel[SYMBOL].dropna())
        assert panel[SYMBOL].isna().any()


class TestTheCorrelationTable:
    def test_the_traded_cell_lands_the_book(self, result) -> None:
        cell = result.traded
        assert cell.coefficient == pytest.approx(0.271855, abs=5e-7)
        assert cell.p_value == pytest.approx(0.023841, abs=5e-7)
        assert round(cell.coefficient, 4) == 0.2719
        assert round(cell.p_value, 4) == 0.0238
        assert matches(cell.coefficient, BOOK_CORRELATION)
        assert matches(cell.p_value, BOOK_P_VALUE)

    def test_the_traded_cell_correlates_69_rows(self, result) -> None:
        """2,000 rows less 250 back and 25 ahead leave 1,725, and every 25th of those is 69."""
        assert result.traded.rows == 69

    @pytest.mark.parametrize(("pair", "expected"), sorted(TABLE.items()))
    def test_every_cell(self, result, pair, expected) -> None:
        cell = result.correlations[pair]
        assert (round(cell.coefficient, 4), round(cell.p_value, 4)) == expected

    def test_the_six_compromises(self, result) -> None:
        assert {pair: TABLE[pair] for pair in COMPROMISES} == {
            (60, 10): (0.1718, 0.0169),
            (60, 25): (0.2592, 0.0228),
            (250, 10): (0.1784, 0.0185),
            (250, 25): (0.2719, 0.0238),
            (250, 60): (0.4245, 0.0217),
            (250, 120): (0.5112, 0.0617),
        }
        assert all(result.correlations[pair].coefficient > 0 for pair in COMPROMISES)

    def test_the_sample_keeps_every_min_lookback_hold_th_row(self) -> None:
        """A lookback of 5 and a hold of 10 keep every 5th row, so 21 of the 105 left."""
        closes = 100 + np.cumsum(np.random.default_rng(3).standard_normal(120))
        assert correlation(closes, 5, 10).rows == 21
        assert correlation(closes, 10, 5).rows == 21

    def test_the_p_value_is_corrcoef_s_t_test(self) -> None:
        """``corrcoef``'s p-value is the two-sided t-test on n − 2 degrees of freedom."""
        from scipy.stats import t

        closes = 100 + np.cumsum(np.random.default_rng(4).standard_normal(300))
        cell = correlation(closes, 1, 1)
        r, n = cell.coefficient, cell.rows
        statistic = r * np.sqrt((n - 2) / (1 - r**2))
        assert cell.p_value == pytest.approx(2 * t.sf(abs(statistic), n - 2), rel=1e-9)


class TestTheTwoTests:
    def test_h_misses_the_book_s_0_44(self, result) -> None:
        assert result.hurst == pytest.approx(0.433357, abs=5e-7)
        assert not matches(result.hurst, BOOK_HURST)
        assert gap(result.hurst, BOOK_HURST) == -0.01
        assert result.hurst < 0.5

    def test_no_single_max_t_lands_both_books_figures(self, closes) -> None:
        """Raising ``maxT`` to 24 lands TU's 0.44 and moves USD.CAD further from its 0.49."""
        usdcad = read_usdcad()[1].to_numpy(dtype=float)
        assert HURST_DIAGNOSTIC_MAX_T == 24
        assert hurst_at(closes) == pytest.approx(0.440450, abs=5e-7)
        assert round(hurst_at(closes), 4) == 0.4404
        assert matches(hurst_at(closes), BOOK_HURST)
        at_default = hurst_at(usdcad, 19)
        at_24 = hurst_at(usdcad)
        assert at_default == pytest.approx(0.473233, abs=5e-7)
        assert at_24 == pytest.approx(0.471426, abs=5e-7)
        assert abs(at_24 - 0.49) > abs(at_default - 0.49)

    def test_the_variance_ratio_test_does_not_reject(self, result) -> None:
        vr = result.variance_ratio
        assert vr.rejects is False
        assert vr.p_value == pytest.approx(0.126860, abs=5e-7)
        assert vr.nobs == 1998


class TestTheFigures:
    def test_the_average_annual_return(self, result) -> None:
        found = result.figures.average_annual_return
        assert found == pytest.approx(0.016699, abs=5e-7)
        assert matches(found, SCRIPT_AVERAGE_ANNUAL_RETURN)

    def test_the_sharpe_ratio(self, result) -> None:
        found = result.figures.sharpe
        assert found == pytest.approx(1.041462, abs=5e-7)
        assert matches(found, SCRIPT_SHARPE)
        assert matches(found, BOOK_SHARPE)

    def test_the_sharpe_ratio_divides_by_n(self, result) -> None:
        """``plain_sharpe``'s n − 1 gives 1.041201, which prints as 1.04 too."""
        n_minus_one = np.sqrt(252) * result.daily.mean() / result.daily.std(ddof=1)
        assert n_minus_one == pytest.approx(1.041201, abs=5e-7)
        assert result.figures.sharpe != pytest.approx(n_minus_one, abs=5e-7)

    def test_the_apr(self, result) -> None:
        found = result.figures.apr
        assert found == pytest.approx(0.016708, abs=5e-7)
        assert matches(found, SCRIPT_APR)
        assert matches(100 * found, BOOK_APR_PERCENT)

    def test_the_maximum_drawdown(self, result) -> None:
        found = result.figures.max_drawdown
        assert found == pytest.approx(-0.024847, abs=5e-7)
        assert matches(found, SCRIPT_MAX_DRAWDOWN)
        assert matches(-100 * found, BOOK_MAX_DRAWDOWN_PERCENT)

    def test_the_longest_drawdown(self, result) -> None:
        assert result.figures.max_drawdown_days == SCRIPT_MAX_DRAWDOWN_DAYS == 343

    def test_the_kelly_f(self, result) -> None:
        found = result.figures.kelly
        assert found == pytest.approx(64.919535, abs=5e-7)
        assert matches(found, SCRIPT_KELLY)

    def test_the_annual_volatility_the_comment_leaves_out(self, result) -> None:
        assert result.figures.annual_volatility == pytest.approx(0.016034, abs=5e-7)


class TestTheWindow:
    """The script's active line, ``idx = find(tday == 20090102)``, which no figure lands on."""

    def test_the_active_line_reads_849_days(self, result) -> None:
        days = result.active_line_days
        assert ACTIVE_LINE_START == pd.Timestamp("2009-01-02")
        assert len(days) == 849
        assert days[0] == ACTIVE_LINE_START
        assert days[-1] == BOOK_LAST_DAY

    def test_its_figures(self, result) -> None:
        found = result.active_line_figures
        assert found.average_annual_return == pytest.approx(0.014042, abs=5e-7)
        assert found.sharpe == pytest.approx(1.187438, abs=5e-7)
        assert found.apr == pytest.approx(0.014069, abs=5e-7)
        assert found.max_drawdown == pytest.approx(-0.009851, abs=5e-7)
        assert found.max_drawdown_days == 164
        assert found.kelly == pytest.approx(100.298107, abs=5e-7)

    def test_none_of_them_lands_the_comment(self, result) -> None:
        found = result.active_line_figures
        assert not matches(found.average_annual_return, SCRIPT_AVERAGE_ANNUAL_RETURN)
        assert not matches(found.sharpe, SCRIPT_SHARPE)
        assert not matches(found.apr, SCRIPT_APR)
        assert not matches(found.max_drawdown, SCRIPT_MAX_DRAWDOWN)
        assert found.max_drawdown_days != SCRIPT_MAX_DRAWDOWN_DAYS
        assert not matches(found.kelly, SCRIPT_KELLY)


class TestTheSave:
    """The 2012-05-17 save ``correlationTest.m`` loads, which tells the two saves apart."""

    def test_it_is_its_pinned_source(self) -> None:
        entry, tu = read_later_save()
        vendor, basis, saved, folder, _ = LIFTED_SOURCES[LATER_SOURCE_FILE]
        assert (entry.vendor, entry.price_basis, entry.obtained) == (vendor, basis, saved)
        assert saved == "2012-05-18"
        assert entry.path == f"{folder}/tu.csv"
        assert len(tu) == 2000
        assert str(tu.index[0].date()) == "2004-06-07"
        assert str(tu.index[-1].date()) == "2012-05-17"

    def test_the_two_saves_agree_on_every_shared_day(self, closes) -> None:
        """Issue 313's finding: TU's close never moves between saves, so only the window does."""
        tu = read_later_save()[1]
        shared = closes.index.intersection(tu.index)
        assert len(shared) == 1996
        assert closes.loc[shared].equals(tu.loc[shared])

    def test_its_traded_cell_and_kelly_f_miss(self, later) -> None:
        assert later.traded.coefficient == pytest.approx(0.287046, abs=5e-7)
        assert round(later.traded.coefficient, 4) == 0.2870
        assert later.traded.p_value == pytest.approx(0.016785, abs=5e-7)
        assert later.figures.kelly == pytest.approx(64.930941, abs=5e-7)
        assert not matches(later.traded.coefficient, BOOK_CORRELATION)
        assert not matches(later.figures.kelly, SCRIPT_KELLY)

    def test_its_two_tests(self, later) -> None:
        assert later.hurst == pytest.approx(0.446556, abs=5e-7)
        assert not matches(later.hurst, BOOK_HURST)
        assert later.variance_ratio.rejects is False
        assert later.variance_ratio.p_value == pytest.approx(0.132819, abs=5e-7)


class TestTheGaussianStatistic:
    """What issue 352 relies on: the returns built from the five exports are this module's."""

    def test_the_exports_give_tu_mom_hypothesis_test_s_2_93(self, closes, result) -> None:
        cl = closes.to_numpy()
        daily = strategy_returns(positions(*signals(cl)), market_returns(cl))
        np.testing.assert_array_equal(daily, result.daily)
        statistic = gaussian_statistic(daily)
        assert statistic == pytest.approx(2.933253, abs=5e-7)
        assert round(statistic, 4) == 2.9333
        assert matches(statistic, SCRIPT_GAUSSIAN_STATISTIC)

    def test_zeroing_the_market_returns_first_moves_nothing(self, closes, result) -> None:
        """``TU_mom.m`` leaves the first market return NaN, and the hypothesis test sets it to 0."""
        cl = closes.to_numpy()
        before = backshift(1, cl)
        unzeroed = (cl - before) / before
        assert np.isnan(unzeroed[0])
        zeroed = market_returns(cl)
        assert zeroed[0] == 0
        np.testing.assert_array_equal(zeroed[1:], unzeroed[1:])
        np.testing.assert_array_equal(
            strategy_returns(result.positions, unzeroed),
            strategy_returns(result.positions, zeroed),
        )

    def test_the_script_s_own_line_gives_the_same_returns(self, closes, result) -> None:
        """``backshift(1, pos).*(cl − backshift(1, cl))./backshift(1, cl)/holddays``."""
        cl = closes.to_numpy()
        before = backshift(1, cl)
        script = backshift(1, result.positions) * (cl - before) / before / HOLD_DAYS
        script[np.isnan(script)] = 0
        np.testing.assert_allclose(result.daily, script, rtol=1e-14, atol=0)


class TestTheRule:
    def test_the_first_lookback_rows_carry_no_signal(self) -> None:
        longs, shorts = signals([1.0, 2.0, 3.0, 2.0, 1.0, 1.0], lookback=2)
        assert longs.tolist() == [False, False, True, False, False, False]
        assert shorts.tolist() == [False, False, False, False, True, True]

    def test_an_unchanged_close_is_neither(self) -> None:
        longs, shorts = signals([5.0, 5.0, 5.0], lookback=1)
        assert not longs.any()
        assert not shorts.any()

    def test_each_signal_is_held_hold_days_rows(self) -> None:
        longs = np.array([False, True, False, False, False, False])
        shorts = np.array([False, False, False, True, False, False])
        assert positions(longs, shorts, hold_days=2).tolist() == [0, 1, 1, -1, -1, 0]
        assert positions(longs, shorts, hold_days=3).tolist() == [0, 1, 1, 0, -1, -1]

    def test_the_position_runs_from_minus_to_plus_hold_days(self, result) -> None:
        assert result.positions.max() == HOLD_DAYS
        assert result.positions.min() == -HOLD_DAYS
        assert str(result.days[np.flatnonzero(result.positions)[0]].date()) == "2005-06-01"

    def test_the_return_is_yesterday_s_position_over_hold_days(self) -> None:
        held = np.array([0.0, 2.0, -1.0, 3.0])
        market = np.array([0.0, 0.01, 0.02, -0.03])
        np.testing.assert_allclose(
            strategy_returns(held, market, hold_days=4), [0.0, 0.0, 0.01, 0.0075], rtol=1e-15
        )

    def test_the_divisor_is_hold_days_and_not_the_gross_position(self) -> None:
        """Chan's 2018 Python port divides by the gross position, which would give 0.01 here."""
        out = strategy_returns(np.array([1.0, 1.0]), np.array([0.0, 0.01]), hold_days=25)
        assert out.tolist() == [0.0, 0.01 / 25]

    def test_a_position_larger_than_hold_days_is_refused(self) -> None:
        held = positions(np.ones(30, dtype=bool), np.zeros(30, dtype=bool), hold_days=25)
        assert held.max() == 25
        with pytest.raises(ValueError, match="same hold_days"):
            strategy_returns(held, np.zeros(30), hold_days=20)
        strategy_returns(held, np.zeros(30), hold_days=25)

    def test_mismatched_inputs_are_refused(self) -> None:
        with pytest.raises(ValueError, match="one length"):
            positions(np.ones(3, dtype=bool), np.ones(4, dtype=bool))
        with pytest.raises(ValueError, match="at least 1 day"):
            positions(np.ones(3, dtype=bool), np.ones(3, dtype=bool), hold_days=0)
        with pytest.raises(ValueError, match="one shape"):
            strategy_returns(np.zeros(3), np.zeros(4))

    def test_the_market_return_s_first_row_is_zero(self) -> None:
        np.testing.assert_allclose(market_returns([100.0, 101.0, 99.99]), [0.0, 0.01, -0.01])

    def test_figures_on_a_known_series(self) -> None:
        daily = np.array([0.0, 0.01, -0.02, 0.01])
        found = figures(daily)
        assert found.average_annual_return == pytest.approx(252 * daily.mean())
        assert found.sharpe == pytest.approx(np.sqrt(252) * daily.mean() / daily.std(ddof=0))
        assert found.kelly == pytest.approx(daily.mean() / daily.var(ddof=1))
        assert found.max_drawdown == pytest.approx(0.98 * 1.01 / 1.01 - 1)


class TestTheGuardAndTheReads:
    def test_tu_carries_no_flagged_day(self, closes) -> None:
        """``tests/test_scale_breaks.py`` names ZB and ZF as the only flagged series here."""
        assert scale_breaks(closes) == []
        assert scale_breaks(read_later_save()[1]) == []

    def test_read_sources_guards_tu_over_its_whole_span(self, closes, monkeypatch) -> None:
        seen = []

        def record(legs, *, start, end):
            seen.append(([entry.symbol for entry, _ in legs], start, end))

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", record)
        read_sources()
        assert seen == [([SYMBOL], closes.index[0], closes.index[-1])]

    @pytest.mark.parametrize("row", [1, 1000, 1999])
    def test_tu_changing_scale_anywhere_is_refused(self, row, monkeypatch) -> None:
        members, panel = load_panel(SOURCE_FILE)
        broken = panel.copy()
        tu = broken[SYMBOL].dropna()
        broken.loc[tu.index[row:], SYMBOL] *= 10
        monkeypatch.setattr(module, "load_panel", lambda *_a, **_k: (members, broken))
        with pytest.raises(WindowCrossesScaleBreak, match="tu.csv"):
            read_sources()

    def test_main_turns_a_guard_refusal_into_one_line(self, monkeypatch, no_arguments) -> None:
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("inputdataohlcdaily_20120511/tu.csv changes scale")

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(SystemExit, match="tu.csv changes scale"):
            main()

    def test_main_turns_a_missing_vintage_into_one_line(
        self, monkeypatch, tmp_path, no_arguments
    ) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit, match="inputDataOHLCDaily_20120511.mat"):
            main()

    def test_a_miss_is_reported_as_one(self) -> None:
        assert module._verdict(0.433357, "0.44") == "did not reproduce, gap -0.01"
        assert module._verdict(0.271855, "0.27") == "reproduced"


@pytest.fixture(scope="module")
def printed() -> str:
    """What ``run`` prints, captured once for the tests that read it."""
    out = io.StringIO()
    with redirect_stdout(out):
        run()
    return out.getvalue()


class TestTheReport:
    def test_it_prints_each_figure_beside_chan_s(self, printed) -> None:
        for label, figures_ in (
            ("250/25 correlation", ["0.271855", "0.27", "reproduced"]),
            ("250/25 p-value", ["0.023841", "0.02", "reproduced"]),
            ("Hurst exponent", ["0.433357", "0.44", "did", "not"]),
            ("Average annual return", ["0.016699", "0.0167", "reproduced"]),
            ("Kelly f", ["64.919535", "64.919535", "reproduced"]),
            ("Longest drawdown, days", ["343", "343", "reproduced"]),
        ):
            row = next(r for r in printed.splitlines() if r.strip().startswith(label))
            assert all(f in row.split() for f in figures_), row
        assert "inputdataohlcdaily_20120511/tu.csv" in printed
        assert "inputdataohlcdaily_20120517/tu.csv" in printed
        assert "Exploratory." in printed
        assert "Entry 32" in printed

    def test_it_prints_the_table_and_the_rows_beside(self, printed) -> None:
        assert "0.2719 (0.0238)" in printed
        assert "2.9333" in printed
        assert "2009-01-02 to 2012-05-11, 849 days" in printed
        assert "250/25 correlation 0.2870, p 0.0168" in printed
