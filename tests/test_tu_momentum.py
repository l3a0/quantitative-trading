"""The pins for time-series momentum on TU, *Algorithmic Trading*'s Example 6.1.

This file is the single authority for every number a prose surface quotes
about this example and the rows beside it. ``docs/replication-log.md`` Entry 33
carries the verdicts and points here row by row.
``blog/usdcad-stationarity-lessons.md`` quotes USD.CAD's H at a ``maxT`` of 24,
which ``TestTheTwoTests`` pins here, so a change to that pin moves that post
too. ``blog/tu-hypothesis-tests-lessons.md`` quotes the 49 pairs of lookback
and hold the rule was picked from, which ``PERIODS`` and
``TestTheCorrelationTable`` hold here. ``blog/tu-momentum-lessons.md`` teaches
this example and quotes most of these pins, with the numbers it adds in
``TestBesideThePost``, its figure's in ``tests/test_tu_momentum_figures.py``,
and its two sketches' in ``tests/test_tu_momentum_whiteboard.py``, which also
pins the 225 days two kept pasts share and the four trading days between the
two saves' first days. ``TestWhatThePostQuotes`` reads at least one copy of
each run figure the post quotes, outside the sketches' alt text, against the
run. README lists what the post says that nothing asserts.

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
  from 2004-06-07 to 2012-05-17. ``TestTheSave`` pins it, and every
  other test that reads it names it where it does.
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
        assert result.correlations[(250, 120)].rows == 14

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

    def test_max_t_24_lands_tu_and_moves_usdcad_further(self, closes) -> None:
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

    def test_no_max_t_from_5_to_40_lands_both(self, closes) -> None:
        """Every ``maxT`` that lands TU's 0.44 moves USD.CAD further from its 0.49.

        No ``maxT`` from 5 to 40 lands USD.CAD's 0.49 either.

        24 is not the only ``maxT`` that lands TU, and not the first. Below 5 the
        function has too few gaps to fit and gives no H.
        """
        usdcad = read_usdcad()[1].to_numpy(dtype=float)
        at_default = hurst_at(usdcad, 19)
        landing = []
        for max_t in range(5, 41):
            if matches(hurst_at(closes, max_t), BOOK_HURST):
                landing.append(max_t)
                assert abs(hurst_at(usdcad, max_t) - 0.49) > abs(at_default - 0.49)
            assert not matches(hurst_at(usdcad, max_t), "0.49")
        assert landing == [6, 7, 21, 22, 23, 24, 25, 26, 27]

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
        assert -100 * found == pytest.approx(2.484746, abs=5e-7)
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
    """The script's active line, ``idx=find(tday==20090102);``, which no figure lands on."""

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

    def test_the_two_saves_keep_none_of_the_same_69_days(self, closes) -> None:
        """The later save starts four trading days later, so every kept day at 250/25 moves."""
        tu = read_later_save()[1]

        def kept(series: pd.Series) -> pd.DatetimeIndex:
            rows = np.arange(LOOKBACK, len(series) - HOLD_DAYS)[:: min(LOOKBACK, HOLD_DAYS)]
            assert len(rows) == correlation(series, LOOKBACK, HOLD_DAYS).rows
            return series.index[rows]

        earlier, later_days = kept(closes), kept(tu)
        assert len(earlier) == len(later_days) == 69
        assert closes.index.get_loc(tu.index[0]) == 4
        assert str(earlier[0].date()) == "2005-06-01"
        assert str(later_days[0].date()) == "2005-06-07"
        assert earlier.intersection(later_days).empty

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


class TestBesideThePost:
    """Numbers ``blog/tu-momentum-lessons.md`` quotes about the table and the trade.

    None is a published figure, so none is a replication. Each reads the run on
    the vintage and specification stated at the top of this file, so they are as
    exploratory as the rest.
    """

    def test_14_of_the_49_cells_are_significant_and_the_negative_four_are_the_shortest(
        self, result
    ) -> None:
        """Ten positive and four negative, against the 2.45 that 49 independent tests would give."""
        significant = {
            pair: cell for pair, cell in result.correlations.items() if cell.p_value < 0.05
        }
        assert len(result.correlations) == 49
        assert len(significant) == 14
        assert sum(cell.coefficient > 0 for cell in significant.values()) == 10
        assert {pair for pair, cell in significant.items() if cell.coefficient < 0} == {
            (1, 1),
            (1, 5),
            (5, 1),
            (5, 5),
        }
        assert len(result.correlations) * 0.05 == pytest.approx(2.45)

    def test_the_position_is_fully_long_on_1176_of_the_2000_days(self, result) -> None:
        """+25 on 1,176 days, −25 on 397 and 0 on 251, of which 250 precede the first signal."""
        held = result.positions
        assert len(held) == 2000
        assert int((held == HOLD_DAYS).sum()) == 1176
        assert int((held == -HOLD_DAYS).sum()) == 397
        assert int((held == 0).sum()) == 251
        assert np.flatnonzero(held)[0] == 250

    def test_the_other_176_days_hold_a_partial_position(self, result) -> None:
        """Between −25 and +25, neither flat nor full, on the days the three counts leave out."""
        held = result.positions
        assert int(((np.abs(held) < HOLD_DAYS) & (held != 0)).sum()) == 176
        assert 1176 + 397 + 251 + 176 == len(held)

    def test_tu_s_close_rose_from_the_first_day_to_the_last(self, result) -> None:
        assert result.closes[0] == 97.9219
        assert result.closes[-1] == 110.2734

    def test_2008_alone_against_every_other_year(self, result) -> None:
        """Calendar 2008 against every other year of the run, each compounded on its own."""
        growth = (1 + pd.Series(result.daily, index=result.days)).groupby(result.days.year).prod()
        in_2008 = growth[2008] - 1
        the_rest = growth.drop(2008).prod() - 1
        assert in_2008 == pytest.approx(0.060565, abs=5e-7)
        assert the_rest == pytest.approx(0.075414, abs=5e-7)


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

    def test_the_refusal_reads_short_positions_and_its_boundary(self) -> None:
        """A short position counts by its size, and one tranche past the divisor is refused."""
        short = positions(np.zeros(30, dtype=bool), np.ones(30, dtype=bool), hold_days=25)
        assert short.min() == -25
        with pytest.raises(ValueError, match="same hold_days"):
            strategy_returns(short, np.zeros(30), hold_days=20)
        held = positions(np.ones(30, dtype=bool), np.zeros(30, dtype=bool), hold_days=21)
        with pytest.raises(ValueError, match="same hold_days"):
            strategy_returns(held, np.zeros(30), hold_days=20)
        strategy_returns(held, np.zeros(30), hold_days=21)

    def test_a_mismatch_inside_the_bound_is_not_refused(self) -> None:
        """The refusal reads the largest position, so cancelling tranches slip past it.

        Built with 26 tranches, one long and one short alternating never pass 1,
        so dividing by 25 goes through and the return is 26/25 of the right one.
        """
        longs = np.tile([True, False], 20)
        held = positions(longs, ~longs, hold_days=26)
        assert np.abs(held).max() == 1
        market = np.linspace(0.0, 0.01, 40)
        np.testing.assert_allclose(
            strategy_returns(held, market, hold_days=25),
            strategy_returns(held, market, hold_days=26) * 26 / 25,
            rtol=1e-12,
        )

    def test_a_nan_signal_reads_as_false(self) -> None:
        """The script's NaN comparison is false, and a bool cast would make it true."""
        held = positions(np.array([np.nan, 0.0, 0.0]), np.zeros(3), hold_days=2)
        assert held.tolist() == [0.0, 0.0, 0.0]
        held = positions(np.array([1.0, np.nan, 0.0]), np.array([np.nan, 0.0, 0.0]), hold_days=2)
        assert held.tolist() == [1.0, 1.0, 0.0]

    def test_mismatched_inputs_are_refused(self) -> None:
        with pytest.raises(ValueError, match="one length"):
            positions(np.ones(3, dtype=bool), np.ones(4, dtype=bool))
        with pytest.raises(ValueError, match="at least 1 day"):
            positions(np.ones(3, dtype=bool), np.ones(3, dtype=bool), hold_days=0)
        with pytest.raises(ValueError, match="one shape"):
            strategy_returns(np.zeros(3), np.zeros(4))

    def test_the_market_return_s_first_row_is_zero(self) -> None:
        np.testing.assert_allclose(market_returns([100.0, 101.0, 99.99]), [0.0, 0.01, -0.01])

    def test_an_infinite_market_return_is_zero(self) -> None:
        """A zero close makes the next return infinite, and the script's line sets it to 0."""
        assert market_returns([0.0, 1.0, 2.0]).tolist() == [0.0, 0.0, 1.0]

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
        assert "Entry 33" in printed

    def test_it_prints_the_table_and_the_rows_beside(self, printed) -> None:
        assert "0.2719 (0.0238)" in printed
        assert "2.9333" in printed
        assert "2009-01-02 to 2012-05-11, 849 days" in printed
        assert "250/25 correlation 0.2870, p 0.0168" in printed, "the 2012-05-17 save"


POST = paths.REPO_ROOT / "blog" / "tu-momentum-lessons.md"

#: Counts the post spells out in words rather than printing as digits.
SPELLED = {4: "four", 5: "five", 6: "six", 7: "seven", 10: "ten", 14: "fourteen"}

#: The six figures in the script's closing comment, each beside the field of
#: :class:`Figures` that gives it.
SCRIPT_FIGURES = (
    ("average_annual_return", SCRIPT_AVERAGE_ANNUAL_RETURN),
    ("sharpe", SCRIPT_SHARPE),
    ("apr", SCRIPT_APR),
    ("max_drawdown", SCRIPT_MAX_DRAWDOWN),
    ("max_drawdown_days", str(SCRIPT_MAX_DRAWDOWN_DAYS)),
    ("kelly", SCRIPT_KELLY),
)


def _minus(x: float, places: int) -> str:
    """``x`` at ``places`` decimals with a true minus sign, as the post's prose prints it."""
    return f"{x:.{places}f}".replace("-", "−")


def _landed(found) -> int:
    """How many of the closing comment's six figures ``found`` lands, every printed digit."""
    return sum(matches(getattr(found, name), printed) for name, printed in SCRIPT_FIGURES)


def _array(columns: str, header: list[str], rows: list[str]) -> str:
    """One of the post's ``\\small`` tables, rebuilt whole from its header and rows."""
    return (
        f"\\small\\begin{{array}}{{{columns}}}\n"
        + " & "
        + " & ".join(header)
        + " \\\\ \\hline\n"
        + " \\\\\n".join(rows)
        + "\n\\end{array}"
    )


def _cell(cell) -> str:
    """One cell of Lesson 3's tables, bold where its p-value is below 0.05."""
    value = f"{cell.coefficient:.4f}"
    return f"\\mathbf{{{value}}}" if cell.p_value < 0.05 else value


def _kept(series: pd.Series) -> pd.DatetimeIndex:
    """The days the 250/25 cell keeps on one save, every 25th from the first with both returns."""
    rows = np.arange(LOOKBACK, len(series) - HOLD_DAYS)[:: min(LOOKBACK, HOLD_DAYS)]
    assert len(rows) == correlation(series, LOOKBACK, HOLD_DAYS).rows
    return series.index[rows]


class TestWhatThePostQuotes:
    """Each run figure ``blog/tu-momentum-lessons.md`` quotes, read in the post against the run.

    The classes above pin each figure once, and the post copies it by hand.
    Here each figure is built from the run at the precision the post prints
    it, and looked for in the post inside a fragment holding the number and
    the words that place it. A typo in that copy, or a re-pin that leaves the
    post behind, fails here. Each of the four ``\\small`` tables is rebuilt
    whole, so a cell changed there fails too, bold included in Lesson 3's.

    These comparisons the post's words draw are asserted on the run, except
    two. The traded pair's place among Chan's compromises is checked against
    the module's transcription of location 2646, and the kept past returns
    still overlapping on the module's lookback and hold. One copy of the
    words for each is read.

    - TU's column spans the window the book names, the full window lands all
      six of the comment's figures and the active line none, and the traded
      pair is one of Chan's compromises while several pairs, read as more
      than two, correlate more strongly.
    - The position runs from −25 to 25.
    - The full window's maximum drawdown rounds to the book's 2.5 percent,
      and the active line's daily standard deviation shrinks by more than
      its mean, so its Sharpe ratio and Kelly f are higher.
    - More than half of the gain is in by 2009-01-02, the maximum drawdown is
      over by then, and the active line sees a smaller gain and a shallower
      fall.
    - The two saves agree on every shared day, the later one starts and ends
      four trading days later, the days the traded cell keeps start four
      trading days later too, each gives the traded cell 69 days and no day
      appears in both, and the shift alone moves the correlation in its
      second decimal, off the book's 0.27, and the Kelly f off the comment's
      digits.
    - At the scripts' settings H lands neither the book's 0.44 on TU nor its
      0.49 on USD.CAD, TU's H misses low and the later save's on the other
      side, a ``maxT`` of 24 lands TU and moves USD.CAD further from its
      0.49, and every H the post gives sits below 0.5 with the book's.
    - The traded cell lands the book's 0.27 and 0.02, the past returns its
      kept days look back on still overlap, and the four negative cells are
      exactly the shortest pairs. Every pair of two periods of 60 days or
      more keeps fewer days than any other pair, and one of them correlates
      more strongly than the traded cell with a p-value of 0.05 or more. All
      six compromises correlate positively, all but one with a p-value below
      0.05. The variance ratio test keeps a whole number of two-day periods
      and does not reject.
    - The rule is fully long on most days of a rising price, the return
      leans on 2008, which holds the maximum drawdown, and 2008 earned about
      four-fifths as much as the other years, read as between 0.75 and 0.85.

    No other comparison is asserted here, so a flipped word elsewhere in the
    post passes unless it sits inside a fragment read here. The sampling step
    and the rule's direction are two such comparisons, which
    ``TestTheCorrelationTable`` and ``TestTheRule`` assert on the code
    without reading the post.

    What it leaves unread is listed in README. Every copy of a figure or of an
    asserted comparison but the one read here can carry a typo that passes,
    and the post states several figures more than once, in its opening, a
    lesson, a table, the closing list or the figure's alt text. Of that alt
    text it reads only the two figures that appear nowhere else, the highest
    close and the curve's high, each with its day. The two sketches' alt texts are
    read by ``tests/test_tu_momentum_whiteboard.py``, not here. Chan's words,
    the Kindle locations, the mirror's commit, the facts about the script and the contract
    that README's second group lists, such as the ``q`` of 2 and the default
    ``maxT`` of 19, the book's chapter, example,
    figure and table numbers, the replication log's entry number, the post's
    counts of its own groups, lessons, tables and lists and its pointers to
    its lessons and tables, its counts of what other surfaces hold, the one
    setting the replication tried, a random walk's 0.5 and its two-day
    variance of twice its one-day, the 1 the cumulative return's definition
    subtracts and the references stay unread.
    """

    @pytest.fixture(scope="class")
    @classmethod
    def text(cls) -> str:
        return POST.read_text(encoding="utf-8")

    @pytest.fixture(scope="class")
    @classmethod
    def later_closes(cls) -> pd.Series:
        return read_later_save()[1]

    @pytest.fixture(scope="class")
    @classmethod
    def curve(cls, closes) -> pd.Series:
        from chan.tu_momentum_figures import cumulative_return, daily_returns

        return pd.Series(cumulative_return(daily_returns(closes)), index=closes.index)

    @staticmethod
    def missing(text: str, fragments: list[str]) -> list[str]:
        return [fragment for fragment in fragments if fragment not in text]

    def test_the_opening_and_the_file(self, sources, result, text) -> None:
        entry, closes = sources
        cell = result.traded
        six = len(SCRIPT_FIGURES)
        assert _landed(result.figures) == six
        assert _landed(result.active_line_figures) == 0
        assert (closes.index[0], closes.index[-1]) == (BOOK_FIRST_DAY, BOOK_LAST_DAY)
        assert (LOOKBACK, HOLD_DAYS) in COMPROMISES
        stronger = sum(
            other.coefficient > cell.coefficient for other in result.correlations.values()
        )
        assert stronger > 2, "several pairs correlate more strongly"
        fragments = [
            f"the correlation that picked the rule’s periods rests on {cell.rows} days.",
            f"The comment at the end of the script lists {SPELLED[six]} figures.",
            f"The one it runs starts in {ACTIVE_LINE_START.year} and lands none of the "
            f"{SPELLED[six]}. The one below it starts in {closes.index[0].year} and reads "
            "every day",
            f"That line lands all {SPELLED[_landed(result.figures)]}.",
            f"The book prints {BOOK_HURST}, and the transcription gives {result.hurst:.6f}.",
            f"looking back {LOOKBACK} days and holding for {HOLD_DAYS}.",
            "he names it among the best compromises between a strong correlation and a small "
            "p-value, though several pairs correlate more strongly.",
            f"The pair correlates at {cell.coefficient:.2f} with a p-value of "
            f"{cell.p_value:.2f}. The correlation rests on {cell.rows} days, and the pair is "
            f"one of {len(result.correlations)} tried on the same closes.",
            f"a table computed on the {closes.index[0].year} to {closes.index[-1].year} closes "
            "the rule then trades",
            f"Chan’s own MATLAB file `{SOURCE_FILE}`, saved on {entry.obtained} and converted "
            f"here to one file per future. TU’s column holds {len(closes):,} daily closes of the "
            "continuous future, from "
            f"{closes.index[0].date()} to {closes.index[-1].date()}, the window the book names.",
        ]
        assert self.missing(text, fragments) == []

    def test_the_table_and_the_rule(self, result, text) -> None:
        days = result.days
        first_position = days[int(np.flatnonzero(result.positions)[0])].date()
        first_return = days[int(np.flatnonzero(result.daily)[0])].date()
        periods = ", ".join(map(str, PERIODS[:-1])) + f" and {PERIODS[-1]}"
        step = min(LOOKBACK, HOLD_DAYS)
        shared = set(range(1, HOLD_DAYS + 1)) & set(range(2, HOLD_DAYS + 2))
        assert (result.positions.min(), result.positions.max()) == (-HOLD_DAYS, HOLD_DAYS)
        fragments = [
            f"The table starts from one cell, a lookback of {LOOKBACK} days and a hold of "
            f"{HOLD_DAYS}. On each day the past return is the percentage change in TU’s close "
            f"over the previous {LOOKBACK} days, and the future return is the percentage change "
            f"over the next {HOLD_DAYS}.",
            f"Two consecutive future returns overlap on {len(shared)} of their {HOLD_DAYS} days",
            f"For {LOOKBACK} and {HOLD_DAYS} it keeps every {step}th day, and "
            f"{result.traded.rows} days survive.",
            f"every pairing of {periods} days, {SPELLED[len(PERIODS)]} lookbacks against "
            f"{SPELLED[len(PERIODS)]} holds, which makes {len(result.correlations)} cells. In "
            f"what follows, {LOOKBACK}/{HOLD_DAYS} means a lookback of {LOOKBACK} days and a "
            f"hold of {HOLD_DAYS}.",
            f"Chan picks {LOOKBACK}/{HOLD_DAYS} from the table and then looks for a rule to "
            "trade it.",
            f"sets the rule’s year at {LOOKBACK} trading days and its month at {HOLD_DAYS}",
            f"Each tranche is held for {HOLD_DAYS} days, so up to {HOLD_DAYS} are open at once. "
            f"Counted in tranches, the position runs from −{HOLD_DAYS}, all short, to "
            f"{HOLD_DAYS}, all long. A day’s return is yesterday’s position times today’s "
            f"percentage change in the close, divided by {HOLD_DAYS}. The first {LOOKBACK} days "
            f"have no {LOOKBACK}-day return, so the rule holds nothing until {first_position} "
            f"and earns its first return on {first_return}.",
            f"the mean daily return times {module.TRADING_DAYS}, the number of trading days a "
            "year the script uses to annualize",
            f"times √{module.TRADING_DAYS}.",
            f"annualizes it over {module.TRADING_DAYS} days a year",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_1s_tables(self, result, text) -> None:
        full, active = result.figures, result.active_line_figures
        days = result.active_line_days
        assert matches(-100 * full.max_drawdown, BOOK_MAX_DRAWDOWN_PERCENT)
        start = result.days.get_loc(ACTIVE_LINE_START)
        whole, tail = result.daily, result.daily[start:]
        assert tail.mean() < whole.mean() and tail.std() < whole.std()
        assert tail.std() / whole.std() < tail.mean() / whole.mean(), (
            "standard deviation shrinks more"
        )
        assert active.sharpe > full.sharpe and active.kelly > full.kelly
        returns = _array(
            "l|r|r|r",
            ["\\text{Return}", "\\text{Sharpe}", "\\text{APR}"],
            [
                *(
                    f"\\text{{{label}}} & {f.average_annual_return:.6f} & {f.sharpe:.6f} & "
                    f"{f.apr:.6f}"
                    for label, f in (("Full window", full), ("Active line", active))
                ),
                f"\\text{{Comment}} & {SCRIPT_AVERAGE_ANNUAL_RETURN} & {SCRIPT_SHARPE} & "
                f"{SCRIPT_APR}",
                f"\\text{{Book}} & \\text{{none}} & {BOOK_SHARPE} & "
                f"{BOOK_APR_PERCENT}\\text{{ percent}}",
            ],
        )
        drawdowns = _array(
            "l|r|r|r",
            ["\\text{Drawdown}", "\\text{Days}", "\\text{Kelly f}"],
            [
                *(
                    f"\\text{{{label}}} & {f.max_drawdown:.6f} & {f.max_drawdown_days} & "
                    f"{f.kelly:.6f}"
                    for label, f in (("Full window", full), ("Active line", active))
                ),
                f"\\text{{Comment}} & {SCRIPT_MAX_DRAWDOWN} & {SCRIPT_MAX_DRAWDOWN_DAYS} & "
                f"{SCRIPT_KELLY}",
                f"\\text{{Book}} & {BOOK_MAX_DRAWDOWN_PERCENT}\\text{{ percent}} & "
                "\\text{none} & \\text{none}",
            ],
        )
        fragments = [
            f"The full window is all {len(result.days):,} days. The active line, the one the "
            f"script runs, reads the {len(days)} days from {days[0].date()}.",
            returns,
            drawdowns,
            f"The maximum drawdown of {_minus(full.max_drawdown, 6)} is a fall of "
            f"{-100 * full.max_drawdown:.6f} percent, which rounds to the book’s "
            f"{BOOK_MAX_DRAWDOWN_PERCENT} percent.",
            "The standard deviation of its daily returns shrinks by more than their mean does, "
            "so its Sharpe ratio and Kelly f come out higher.",
        ]
        assert self.missing(text, fragments) == []

    def test_the_curve_and_the_alt_text(self, curve, closes, result, text) -> None:
        from chan.cross_sectional_momentum_figures import deepest_drawdown

        drawdown = deepest_drawdown(curve.to_numpy())
        at_start, last = curve[ACTIVE_LINE_START], curve.iloc[-1]
        high, low = curve.index[drawdown.high], curve.index[drawdown.trough]
        assert at_start / last > 0.5, "more than half of the gain"
        assert low < ACTIVE_LINE_START, "the active line starts after the maximum drawdown"
        start = result.days.get_loc(ACTIVE_LINE_START)
        assert np.prod(1 + result.daily[start:]) - 1 < last, "a smaller gain"
        assert result.active_line_figures.max_drawdown > result.figures.max_drawdown, (
            "a shallower fall"
        )
        fragments = [
            f"The curve stands at {at_start:.6f} on {ACTIVE_LINE_START.date()} and ends at "
            f"{last:.6f}, so the active line starts after more than half of the gain was "
            "already in. The active line also starts after the maximum drawdown, which runs "
            f"from {high.date()} to {low.date()}. The active line sees a smaller gain and a "
            "shallower fall, and every figure moves.",
            f"keep rising to a high of {closes.max():.4f} on {closes.idxmax().date()}",
            f"to its highest point, {curve.max():.6f} on {curve.idxmax().date()}",
        ]
        assert self.missing(text, fragments) == []

    def test_the_later_file(self, closes, later_closes, result, later, text) -> None:
        shared = closes.index.intersection(later_closes.index)
        assert closes.loc[shared].equals(later_closes.loc[shared])
        shift = closes.index.get_loc(later_closes.index[0])
        earlier_kept, later_kept = _kept(closes), _kept(later_closes)
        assert len(earlier_kept) == len(later_kept)
        assert earlier_kept.intersection(later_kept).empty
        assert closes.index.get_loc(later_kept[0]) - closes.index.get_loc(earlier_kept[0]) == shift
        assert round(later.traded.coefficient, 2) != round(result.traded.coefficient, 2)
        assert not matches(later.traded.coefficient, BOOK_CORRELATION)
        assert not matches(later.figures.kelly, SCRIPT_KELLY)
        assert len(later_closes) - len(shared) == shift, "it also ends that many days later"
        on_shared = correlation(later_closes.loc[shared], LOOKBACK, HOLD_DAYS).coefficient
        assert on_shared == pytest.approx(later.traded.coefficient, abs=1e-12), "shift alone"
        fragments = [
            f"whose closes run to {later_closes.index[-1].date()}. TU’s close is the same on all "
            f"{len(shared):,} days the two files share. The later file’s "
            f"{len(later_closes):,} days start on {later_closes.index[0].date()}, "
            f"{SPELLED[shift]} trading days later, so the days the {LOOKBACK}/{HOLD_DAYS} cell "
            f"keeps, every {HOLD_DAYS}th one, start {SPELLED[shift]} trading days later too, on "
            f"{later_kept[0].date()} rather than {earlier_kept[0].date()}. Each file gives the "
            f"cell {len(earlier_kept)} days, and no day appears in both sets.",
            f"The {SPELLED[shift]}-day shift alone moves the {LOOKBACK}/{HOLD_DAYS} correlation "
            f"to {later.traded.coefficient:.6f}, which rounds to "
            f"{later.traded.coefficient:.2f} rather than the book’s {BOOK_CORRELATION}. Run "
            f"over the whole later file, which also ends {SPELLED[shift]} trading days later, "
            f"`TU_mom.m` gives a Kelly f of {later.figures.kelly:.6f}, off the comment’s "
            "digits.",
            "So the book’s figures come "
            f"from the file whose closes end on {closes.index[-1].date()}. "
            f"{SPELLED[shift].capitalize()} days at the start move the correlation in its "
            "second decimal",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_2(self, result, later, later_closes, closes, text) -> None:
        usdcad = read_usdcad()[1].to_numpy(dtype=float)
        at_default, at_24 = hurst_at(usdcad, 19), hurst_at(usdcad)
        book = float(BOOK_HURST)
        assert result.hurst < book < later.hurst, "misses on the other side"
        assert not matches(result.hurst, BOOK_HURST) and not matches(at_default, "0.49"), (
            "lands neither H at the scripts' settings"
        )
        assert matches(hurst_at(closes), BOOK_HURST)
        assert abs(at_24 - 0.49) > abs(at_default - 0.49), "further from its printed 0.49"
        assert max(result.hurst, hurst_at(closes), later.hurst, book) < 0.5, "below 0.5"
        fragments = [
            f"On TU’s log closes the transcription gives {result.hurst:.6f}. That prints as "
            f"{result.hurst:.2f}, so it misses the book’s {BOOK_HURST} with a gap of "
            f"{_minus(gap(result.hurst, BOOK_HURST), 2)}, computed minus published.",
            f"Chan’s later file, whose closes run to {later_closes.index[-1].date()}, gives "
            f"{later.hurst:.6f}, which prints as {later.hurst:.2f} and misses on the other side.",
            f"Raising `maxT` to {HURST_DIAGNOSTIC_MAX_T} lands TU at {hurst_at(closes):.6f}. The "
            "same change moves USD.CAD, the other series the book prints an H for, from "
            f"{at_default:.6f} to {at_24:.6f}, further from its printed 0.49. No value of "
            "`maxT` from 5 to 40 lands both.",
            f"Every H here, {result.hurst:.6f}, {hurst_at(closes):.6f} and the later file’s "
            f"{later.hurst:.6f}, sits below 0.5, on the same side as the book’s {BOOK_HURST}.",
            "At the settings Chan’s scripts use, the Python copy of `genhurst` lands neither H "
            "the book prints, so no figure of Chan’s confirms the copy.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_3s_tables(self, result, text) -> None:
        first, second = PERIODS[:4], PERIODS[4:]

        def table(holds: tuple[int, ...]) -> str:
            return _array(
                "r|" + "r" * len(holds),
                [str(hold) for hold in holds],
                [
                    f"{lookback} & "
                    + " & ".join(_cell(result.correlations[(lookback, hold)]) for hold in holds)
                    for lookback in PERIODS
                ],
            )

        fragments = [
            f"Here are all {len(result.correlations)} correlations of the table in two parts, "
            f"holds of {first[0]} to {first[-1]} days and then holds of {second[0]} to "
            f"{second[-1]} days.",
            table(first),
            table(second),
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_3(self, result, closes, text) -> None:
        cell = result.traded
        cells = len(result.correlations)
        significant = {p: c for p, c in result.correlations.items() if c.p_value < 0.05}
        positive = sum(c.coefficient > 0 for c in significant.values())
        negative = sorted(p for p, c in significant.items() if c.coefficient < 0)
        assert negative == [(lb, h) for lb in PERIODS[:2] for h in PERIODS[:2]], "the shortest"
        chance = cells * 0.05
        step = min(LOOKBACK, HOLD_DAYS)
        assert LOOKBACK - step > 0, "the past returns still overlap"
        long_pairs = {p: c for p, c in result.correlations.items() if min(p) >= 60}
        others = [c.rows for p, c in result.correlations.items() if p not in long_pairs]
        assert max(c.rows for c in long_pairs.values()) < min(others), "keeps few days"
        assert any(
            c.coefficient > cell.coefficient and c.p_value >= 0.05 for c in long_pairs.values()
        ), "a strong correlation there can still have a large p-value"
        compromises = [f"{lb}/{h}" for lb, h in COMPROMISES]
        assert all(result.correlations[p].coefficient > 0 for p in COMPROMISES)
        below = sum(result.correlations[p].p_value < 0.05 for p in COMPROMISES)
        (exception,) = [p for p in COMPROMISES if result.correlations[p].p_value >= 0.05]
        vr = result.variance_ratio
        assert vr.rejects is False and vr.nobs % 2 == 0
        assert matches(cell.coefficient, BOOK_CORRELATION)
        assert matches(cell.p_value, BOOK_P_VALUE)
        fragments = [
            f"The traded cell, {LOOKBACK}/{HOLD_DAYS}, is {cell.coefficient:.6f} with a p-value "
            f"of {cell.p_value:.6f}, and both land the book’s {BOOK_CORRELATION} and "
            f"{BOOK_P_VALUE}.",
            f"**It rests on {cell.rows} days.**",
            f"The past returns still overlap, since each kept one shares {LOOKBACK - step} of its "
            f"{LOOKBACK} days with the next.",
            f"{SPELLED[len(significant)].capitalize()} of the {cells} cells have a p-value below "
            f"0.05. {SPELLED[positive].capitalize()} of them are positive. The "
            f"{SPELLED[len(negative)]} negative ones are exactly the shortest pairs, "
            + ", ".join(f"{lb}/{h}" for lb, h in negative[:-1])
            + f" and {negative[-1][0]}/{negative[-1][1]},",
            f"If the cells were {cells} independent tests of returns with no pattern at all, "
            f"chance alone would put {chance:.2f} of them below 0.05 on average.",
            f"Every cell reads the same {len(closes):,} closes",
            "and neighbouring cells share a lookback or a hold, so their returns overlap. So "
            f"comparing {len(significant)} with {chance:.2f} is not a valid test.",
            "A pair of two long periods keeps few days, so a strong correlation there can still "
            "have a large p-value.",
            "Chan weighs a strong correlation against a small p-value, and calls "
            f"{SPELLED[len(COMPROMISES)]} pairs",
            f": {', '.join(compromises[:-1])} and {compromises[-1]}. All "
            f"{SPELLED[len(COMPROMISES)]} correlate positively and {SPELLED[below]} have a "
            "p-value below 0.05. The exception is "
            f"{exception[0]}/{exception[1]}, whose p-value is "
            f"{result.correlations[exception].p_value:.4f} on "
            f"{result.correlations[exception].rows} days.",
            f"It uses {vr.nobs:,} of the {len(closes) - 1:,} daily changes in TU’s log close, "
            "because it keeps a whole number of two-day periods. Its p-value is "
            f"{vr.p_value:.6f}, so it cannot tell TU from a random walk.",
        ]
        assert self.missing(text, fragments) == []

    def test_the_drift_and_the_one_year(self, result, curve, text) -> None:
        from chan.cross_sectional_momentum_figures import deepest_drawdown

        held = result.positions
        long, short = int((held == HOLD_DAYS).sum()), int((held == -HOLD_DAYS).sum())
        flat = int((held == 0).sum())
        partial = int(((np.abs(held) < HOLD_DAYS) & (held != 0)).sum())
        assert long + short + flat + partial == len(held)
        assert 2 * long > len(held) and result.closes[-1] > result.closes[0], (
            "fully long on most days of a rising price"
        )
        before = int(np.flatnonzero(held)[0])
        growth = (1 + pd.Series(result.daily, index=result.days)).groupby(result.days.year).prod()
        assert growth.idxmax() == 2008, "the return leans on one year"
        in_2008, the_rest = growth[2008] - 1, growth.drop(2008).prod() - 1
        assert 0.75 < in_2008 / the_rest < 0.85, "about four-fifths"
        drawdown = deepest_drawdown(curve.to_numpy())
        assert {curve.index[drawdown.high].year, curve.index[drawdown.trough].year} == {2008}
        first, last = result.days[before], result.days[-1]
        fragments = [
            f"TU’s close rose from {result.closes[0]:.4f} on the first day to "
            f"{result.closes[-1]:.4f} on the last. The position was +{HOLD_DAYS}, fully long, on "
            f"{long:,} of the {len(held):,} days and −{HOLD_DAYS} on {short}. It was between "
            f"−{HOLD_DAYS} and +{HOLD_DAYS} but not 0 on {partial} days, and 0 on the other "
            f"{flat}, of which {before} came before the first signal. A rule that is fully long "
            "on most days of a rising price earns",
            "The return also leans on one year. Calendar 2008 alone compounds to "
            f"{in_2008:.6f}, and the other years together, from the first trade in "
            f"{first:%B %Y} to {last:%B %Y}, compound to "
            f"{the_rest:.6f}. So 2008, the year of the financial crisis, earned about "
            "four-fifths as much as the rest of the run combined, and it holds the maximum "
            "drawdown too.",
        ]
        assert self.missing(text, fragments) == []

    def test_what_this_replication_cannot_say(self, result, closes, text) -> None:
        cells = len(result.correlations)
        fragments = [
            f"The pair was picked from a table of {cells} computed on the "
            f"{closes.index[0].year} to {closes.index[-1].year} closes it then trades, so its "
            f"p-value is not corrected for the other {cells - 1}.",
        ]
        assert self.missing(text, fragments) == []
