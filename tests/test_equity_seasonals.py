"""The pins for Chan's equity seasonals, Examples 7.6 and 7.7, in every printout.

This file is the single authority for every number any prose surface quotes
about either example. ``docs/replication-log.md`` Entry 7 carries the verdicts
and points here row by row.

Two vintages, both read whole through :func:`chan.series.load_panel`.

- **Example 7.6** reads ``data/ijr_20080114/``, 600 members lifted from Chan's
  ``IJR_20080114.mat``, vendor ``chan-mat``, recorded as split-adjusted, saved
  2008-01-15, spanning 2004-01-15 to 2008-01-14.
- **Example 7.7** reads ``data/spx_20071123/``, 500 members lifted from Chan's
  ``SPX_20071123.mat``, the same vendor and basis, saved 2007-11-24, spanning
  1999-11-24 to 2007-11-23.

The specification is one printout's rules, and each class names the one it
pins. :data:`chan.equity_seasonals.JANUARY_RULES` and
:data:`chan.equity_seasonals.HESTON_SADKA_RULES` hold them, and their sources
are these.

1. The first edition's MATLAB, ``example7_6.m`` and ``example7_7.m`` at
   ``1a71950`` in egorpe/EPChan-QuantitativeTrading.
2. The revised edition's Python, ``example7_6.py`` and ``example7_7.py`` at
   ``653cf92`` in liujiantong/epchan_books.
3. The revised edition's MATLAB and R, printed on pp. 179 and 181 of the
   revised Kindle edition, which the owner read on 2026-10-02 and 2026-10-03.
   [Issue 226](https://github.com/l3a0/quantitative-trading/issues/226) quotes
   the expressions that decide each rule. The R needs no repair. The MATLAB
   needs one repair to run, which :data:`chan.equity_seasonals.REVISED_MATLAB`
   names. The revised code as reposted at
   pinhaocheng/epchan-quant_trading_MATLAB_codes ``7430b84`` carries the same repair and book two's
   ``smartstd``.

Every reproduced figure is asserted twice. Its full value is held at
``abs=1e-9``, and its rounding is held at the precision its source prints. Two
margins are thin, which is why the second assertion is not
``abs=5e-5`` on the printed figure. The first edition's 7.7 return sits 0.000014
from the rounding boundary at -0.91665, and its Sharpe ratio sits 0.000016 from
-0.10545.

Each rule that makes a printed figure land has a test asserting the figure the
changed rule gives instead. A builder who corrects Chan's code fails one of
those rather than quietly moving a pin.

The 2002 split is exploratory and carries no verdict. First run on 2026-10-02.
"""

from __future__ import annotations

import math
from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

import chan.equity_seasonals as seasonals
from chan.equity_seasonals import (
    FIRST_EDITION_MATLAB,
    MATLAB_JANUARY,
    PYTHON_HESTON_SADKA,
    PYTHON_JANUARY,
    R_HESTON_SADKA,
    R_JANUARY,
    REVISED_MATLAB,
    Mask,
    Statistic,
    Winners,
    heston_sadka,
    january_effect,
    monthly_returns,
    split_at,
    summarize,
)
from chan.matlab_helpers import round_half_away
from chan.series import load_panel, panel_line
from chan.vintage import VintageUnavailable


@pytest.fixture(scope="module")
def small_caps():
    """Loaded once, because ``load_panel`` hashes and parses all 600 members."""
    return load_panel(seasonals.SMALL_CAPS)


@pytest.fixture(scope="module")
def large_caps():
    """Loaded once, because ``load_panel`` hashes and parses all 500 members."""
    return load_panel(seasonals.LARGE_CAPS)


@pytest.fixture(scope="module")
def ijr(small_caps) -> pd.DataFrame:
    return small_caps[1]


@pytest.fixture(scope="module")
def spx(large_caps) -> pd.DataFrame:
    return large_caps[1]


def assert_reproduces(value: float, full: float, printed: str, spec: str) -> None:
    """The full value at 1e-9, and the figure as its source prints it."""
    assert value == pytest.approx(full, abs=1e-9)
    assert format(value, spec) == printed


def returns_of(effect) -> list[float]:
    return [trade.ret for trade in effect.trades]


class TestThePanels:
    def test_the_small_cap_panel(self, small_caps) -> None:
        members, closes = small_caps
        assert len(members) == 600
        assert closes.index[0] == pd.Timestamp("2004-01-15")
        assert closes.index[-1] == pd.Timestamp("2008-01-14")
        assert panel_line(members) == (
            "ijr_20080114/   chan-mat adjusted, saved 2008-01-15, 600 members lifted from "
            "IJR_20080114.mat"
        )

    def test_the_large_cap_panel(self, large_caps) -> None:
        members, closes = large_caps
        assert len(members) == 500
        assert closes.index[0] == pd.Timestamp("1999-11-24")
        assert closes.index[-1] == pd.Timestamp("2007-11-23")


class TestJanuaryMatlab:
    """Example 7.6 under ``example7_6.m``, which both editions' MATLAB print the same."""

    def test_the_two_reachable_januaries_reproduce(self, ijr) -> None:
        trades = january_effect(ijr, MATLAB_JANUARY).trades
        assert [(t.entered, t.exited) for t in trades] == [
            (pd.Timestamp("2005-12-30"), pd.Timestamp("2006-01-31")),
            (pd.Timestamp("2006-12-29"), pd.Timestamp("2007-01-31")),
        ]
        assert_reproduces(trades[0].ret, -0.024368881797563913, "-0.0244", ".4f")
        assert_reproduces(trades[1].ret, -0.006796429884419337, "-0.0068", ".4f")

    def test_the_script_as_written_cannot_pair_its_dates_on_this_file(self, ijr) -> None:
        """Four year-ends and four January month-ends, and the script drops the first January.

        That leaves three Januaries against four Decembers, so its check that
        each January follows its December fails before anything prints.
        """
        ends = seasonals._row_month_ends(ijr.index)
        decembers = [ijr.index[row] for row in ends if ijr.index[row].month == 12]
        januaries = [ijr.index[row] for row in ends if ijr.index[row].month == 1]
        assert [day.date().isoformat() for day in decembers] == [
            "2004-12-31",
            "2005-12-30",
            "2006-12-29",
            "2007-12-31",
        ]
        assert [day.date().isoformat() for day in januaries] == [
            "2004-01-30",
            "2005-01-31",
            "2006-01-31",
            "2007-01-31",
        ]
        assert len(januaries[1:]) != len(decembers)

    def test_the_decile_is_rounded_half_away_from_zero(self, ijr) -> None:
        trades = january_effect(ijr, MATLAB_JANUARY).trades
        assert [(t.ranked, t.longs, t.shorts) for t in trades] == [(578, 58, 58), (592, 59, 59)]

    def test_rounding_the_decile_down_moves_january_2006(self, ijr) -> None:
        floored = january_effect(ijr, replace(MATLAB_JANUARY, decile_size=np.floor))
        assert returns_of(floored)[0] == pytest.approx(-0.02335614494703974, abs=1e-9)
        assert format(returns_of(floored)[0], ".4f") == "-0.0234"

    def test_the_third_january_is_not_reached(self, ijr) -> None:
        """Chan prints 0.0881 for it. Issue 225 carries reaching it."""
        effect = january_effect(ijr, MATLAB_JANUARY)
        assert effect.unreached == (pd.Timestamp("2007-12-31"),)
        assert effect.file_end == pd.Timestamp("2008-01-14")

    def test_each_trade_pays_two_one_way_costs_of_five_basis_points(self, ijr, monkeypatch) -> None:
        assert seasonals.ONE_WAY_COST == 0.0005
        costed = returns_of(january_effect(ijr, MATLAB_JANUARY))
        monkeypatch.setattr(seasonals, "ONE_WAY_COST", 0.0)
        free = returns_of(january_effect(ijr, MATLAB_JANUARY))
        assert [f - c for f, c in zip(free, costed, strict=True)] == pytest.approx(
            [0.001, 0.001], abs=1e-15
        )


class TestJanuaryPython:
    """Example 7.6 under the revised ``example7_6.py``."""

    def test_the_two_reachable_januaries_reproduce(self, ijr) -> None:
        effect = january_effect(ijr, PYTHON_JANUARY)
        assert [t.exited for t in effect.trades] == [
            pd.Timestamp("2006-01-31"),
            pd.Timestamp("2007-01-31"),
        ]
        assert_reproduces(effect.trades[0].ret, -0.023853172610774076, "-0.023853", ".6f")
        assert_reproduces(effect.trades[1].ret, -0.00364117175573088, "-0.003641", ".6f")
        assert effect.unreached == (pd.Timestamp("2007-12-31"),)

    def test_the_winners_slice_holds_two_fewer_than_the_decile(self, ijr) -> None:
        trades = january_effect(ijr, PYTHON_JANUARY).trades
        assert [(t.ranked, t.longs, t.shorts) for t in trades] == [(579, 58, 56), (593, 59, 57)]

    def test_the_forward_fill_ranks_one_more_stock_and_moves_no_return(self, ijr) -> None:
        """PMC has no close in 2005 or 2006, and pandas before 3.0 ranks it on a return of 0.

        Without the fill the script ranks 578 and 592, the MATLAB counts, and the
        decile sizes and both returns are unchanged.
        """
        unpadded = january_effect(ijr, replace(PYTHON_JANUARY, pads_year_ends=False))
        assert [t.ranked for t in unpadded.trades] == [578, 592]
        assert returns_of(unpadded) == pytest.approx(
            returns_of(january_effect(ijr, PYTHON_JANUARY)), abs=1e-15
        )

    def test_the_full_decile_gives_the_first_editions_figures(self, ijr) -> None:
        """On this file the two editions' printouts differ by the winners' slice alone."""
        full = january_effect(ijr, replace(PYTHON_JANUARY, winners=Winners.DECILE))
        matlab = january_effect(ijr, MATLAB_JANUARY)
        assert returns_of(full) == pytest.approx(returns_of(matlab), abs=1e-15)


class TestJanuaryR:
    """Example 7.6 in the revised edition's R, which prints MATLAB's three figures."""

    def test_the_two_reachable_januaries_reproduce(self, ijr) -> None:
        trades = january_effect(ijr, R_JANUARY).trades
        assert_reproduces(trades[0].ret, -0.024368881797563913, "-0.0244", ".4f")
        assert_reproduces(trades[1].ret, -0.006796429884419337, "-0.0068", ".4f")

    def test_no_decile_on_this_file_lands_on_a_half(self, ijr) -> None:
        """No decile lands on a half, so R's rounding and MATLAB's pick the same stocks."""
        for trade in january_effect(ijr, R_JANUARY).trades:
            assert (trade.ranked / 10) % 1 != 0.5


class TestHestonSadkaFirstEdition:
    """Example 7.7 under the first edition's ``example7_7.m``."""

    def test_both_figures_reproduce(self, spx) -> None:
        result = heston_sadka(spx, FIRST_EDITION_MATLAB)
        assert_reproduces(result.annual_return, -0.9166642443863228, "-0.9167", ".4f")
        assert_reproduces(result.sharpe, -0.10546582130286845, "-0.1055", ".4f")

    def test_the_months_are_found_by_row(self, spx) -> None:
        returns = monthly_returns(spx, FIRST_EDITION_MATLAB)
        assert len(returns) == 96
        assert returns.index[0] == pd.Timestamp("1999-11-30")
        assert returns.index[-1] == pd.Timestamp("2007-10-31")

    def test_the_mean_counts_twelve_empty_months_as_zero(self, spx) -> None:
        returns = monthly_returns(spx, FIRST_EDITION_MATLAB).to_numpy()
        assert math.isnan(returns[0])
        assert int((returns[1:] == 0).sum()) == 12

    def test_masking_each_stock_by_its_own_close_moves_both_figures(self, spx) -> None:
        own = heston_sadka(spx, replace(FIRST_EDITION_MATLAB, mask=Mask.OWN_CLOSE))
        assert own.annual_return == pytest.approx(-1.0822171415504576, abs=1e-9)
        assert own.sharpe == pytest.approx(-0.12087260820688678, abs=1e-9)

    def test_averaging_over_the_months_with_positions_moves_both(self, spx) -> None:
        held = heston_sadka(spx, replace(FIRST_EDITION_MATLAB, dropped=13))
        assert held.annual_return == pytest.approx(-1.0491940146590437, abs=1e-9)
        assert held.sharpe == pytest.approx(-0.11215885700724335, abs=1e-9)

    def test_skipping_the_nan_month_in_the_deviation_moves_the_sharpe_ratio(self, spx) -> None:
        returns = monthly_returns(spx, FIRST_EDITION_MATLAB)
        annual, sharpe = summarize(returns, replace(FIRST_EDITION_MATLAB, statistic=Statistic.R))
        assert annual == pytest.approx(-0.9166642443863228, abs=1e-9)
        assert sharpe == pytest.approx(-0.1049097760233146, abs=1e-9)

    def test_dividing_by_the_positions_puts_the_return_in_units_of_capital(self, spx) -> None:
        """-0.0120 a year, a figure this repo derived and Chan did not print."""
        per = heston_sadka(
            spx,
            replace(FIRST_EDITION_MATLAB, per_position=True, empty_month_is_nan=True, dropped=13),
        )
        assert per.annual_return == pytest.approx(-0.011980550862626747, abs=1e-9)


class TestTheShapesTheScaleBreakCommentNames:
    """What the comment above ``FLAGGED_IN_CHANS_MAT_FILES`` says about Example 7.7."""

    def test_aapls_flagged_day_is_a_month_end(self, spx) -> None:
        ends = spx.index[seasonals._row_month_ends(spx.index)]
        assert pd.Timestamp("2000-09-29") in ends

    @pytest.mark.parametrize("rules", [FIRST_EDITION_MATLAB, PYTHON_HESTON_SADKA])
    @pytest.mark.parametrize("symbol", ["WYN", "DFS"])
    def test_no_monthly_return_spans_a_shared_symbols_gap(self, spx, rules, symbol) -> None:
        """The gap is hundreds of NaN days, and no finite monthly return reaches across it.

        A single missing day inside a month is ordinary and is not the gap, so
        the test looks for the long run rather than for any NaN.
        """
        if rules.per_stock_period_ends:
            ends = spx.resample("ME").last().iloc[:-1]
        else:
            ends = spx.iloc[seasonals._row_month_ends(spx.index)]
        returned = ends[symbol].pct_change(fill_method=None)
        missing = spx[symbol].isna().to_numpy()
        runs, run = [], 0
        for gone in missing:
            run = run + 1 if gone else 0
            runs.append(run)
        longest = pd.Series(runs, index=spx.index)
        assert longest.max() >= 300
        for when in returned.index[np.isfinite(returned.to_numpy())]:
            start = ends.index[ends.index.get_loc(when) - 1]
            inside = longest[(longest.index > start) & (longest.index <= when)]
            assert inside.max() < 20, f"{symbol} {when.date()} spans the gap"


class TestHestonSadkaRevisedMatlab:
    """Example 7.7 in the revised edition's MATLAB, as printed on p. 179 with one repair.

    The listing cuts ``cl`` to its month-end rows and then masks on
    ``cl(monthEnds(m-1), :)``, which cannot run. The repair reads ``cl(m-1, :)``.
    Pp. 179 to 181 do not print ``smartstd``, so these tests also hold which of
    Chan's two prints his digits. The revised code's repost ships book two's,
    which is the one that does.
    """

    def test_both_figures_reproduce(self, spx) -> None:
        result = heston_sadka(spx, REVISED_MATLAB)
        assert_reproduces(result.annual_return, -0.012922703586771995, "-0.0129", ".4f")
        assert_reproduces(result.sharpe, -0.12434081928195095, "-0.1243", ".4f")

    def test_the_printed_index_is_out_of_range_on_the_first_pass(self, spx) -> None:
        """``monthEnds(12)`` is a daily row, and the cut ``cl`` holds 96 rows."""
        ends = seasonals._row_month_ends(spx.index)
        assert len(ends) == 96
        assert ends[11] + 1 == 237

    def test_it_drops_thirteen_months_as_printed(self, spx) -> None:
        """``ret(1:13)=[]`` leaves 83 months, from the end of December 2000."""
        kept = monthly_returns(spx, REVISED_MATLAB).iloc[REVISED_MATLAB.dropped :]
        assert len(kept) == 83
        assert kept.index[0] == pd.Timestamp("2000-12-29")
        assert kept.index[-1] == pd.Timestamp("2007-10-31")

    def test_every_month_the_drop_removes_holds_no_position(self, spx) -> None:
        """So book two's ``smartstd`` skips them all, and the drop count moves no figure.

        Only the count of kept months above holds the 13.
        """
        returns = monthly_returns(spx, REVISED_MATLAB).to_numpy()
        assert np.isnan(returns[:13]).all()
        assert np.isfinite(returns[13:]).all()
        for dropped in (0, 12):
            other = heston_sadka(spx, replace(REVISED_MATLAB, dropped=dropped))
            assert other.sharpe == pytest.approx(-0.12434081928195095, abs=1e-15)

    def test_the_first_editions_smartstd_does_not_print(self, spx) -> None:
        """It prints -0.1236, so the revised code's ``smartstd`` is book two's.

        R's ``sd`` gives the same figure here, because no NaN month is left
        after the drop and both divide by n - 1.
        """
        for statistic in (Statistic.SMART, Statistic.R):
            other = heston_sadka(spx, replace(REVISED_MATLAB, statistic=statistic))
            assert other.sharpe == pytest.approx(-0.12358950835964105, abs=1e-9)
            assert format(other.sharpe, ".4f") == "-0.1236"

    @pytest.mark.parametrize(
        ("dropped", "full", "printed"),
        [
            (0, -0.133014381355165, "-0.1330"),
            (12, -0.12433986572716507, "-0.1243"),
            (13, -0.12358950835964105, "-0.1236"),
        ],
    )
    def test_the_first_editions_smartstd_reads_every_month_it_is_given(
        self, spx, dropped, full, printed
    ) -> None:
        """It counts each month with no position as zero, so the drop count moves its figure.

        Dropping 12 also prints -0.1243. That was the reading pinned before the
        printed code was read, and it lands by counting the one empty month it
        keeps as zero, which ``ret(1:13)=[]`` never gives it.
        """
        other = heston_sadka(
            spx, replace(REVISED_MATLAB, dropped=dropped, statistic=Statistic.SMART)
        )
        assert other.annual_return == pytest.approx(-0.012922703586771993, abs=1e-9)
        assert_reproduces(other.sharpe, full, printed, ".4f")

    def test_the_minimal_repair_keeping_the_first_editions_mask_does_not_print(self, spx) -> None:
        repaired = heston_sadka(spx, replace(REVISED_MATLAB, mask=Mask.SORTED_AGAINST_COLUMNS))
        assert repaired.annual_return == pytest.approx(-0.011980550862626747, abs=1e-9)
        assert repaired.sharpe == pytest.approx(-0.11333516462421217, abs=1e-9)
        assert format(repaired.annual_return, ".4f") != "-0.0129"

    def test_masking_on_each_stocks_own_return_also_prints(self, spx) -> None:
        """So four decimals do not identify the mask, and the printed code does."""
        own_return = heston_sadka(spx, replace(REVISED_MATLAB, mask=Mask.OWN_RETURN))
        assert own_return.annual_return == pytest.approx(-0.012917299005454961, abs=1e-9)
        assert own_return.sharpe == pytest.approx(-0.12426107174773211, abs=1e-9)
        assert format(own_return.annual_return, ".4f") == "-0.0129"
        assert format(own_return.sharpe, ".4f") == "-0.1243"


class TestHestonSadkaPython:
    """Example 7.7 under the revised ``example7_7.py``."""

    def test_both_figures_reproduce(self, spx) -> None:
        result = heston_sadka(spx, PYTHON_HESTON_SADKA)
        assert_reproduces(result.annual_return, -0.012679138708036275, "-0.012679", ".6f")
        assert_reproduces(result.sharpe, -0.12224679235381582, "-0.122247", ".6f")

    def test_it_keeps_83_months_from_december_2000(self, spx) -> None:
        kept = monthly_returns(spx, PYTHON_HESTON_SADKA).iloc[PYTHON_HESTON_SADKA.dropped :]
        assert len(kept) == 83
        assert kept.index[0] == pd.Timestamp("2000-12-31")
        assert kept.index[-1] == pd.Timestamp("2007-10-31")

    def test_one_shared_row_per_month_moves_both_figures(self, spx) -> None:
        rows = heston_sadka(spx, replace(PYTHON_HESTON_SADKA, per_stock_period_ends=False))
        assert rows.annual_return == pytest.approx(-0.012917299005454961, abs=1e-9)
        assert rows.sharpe == pytest.approx(-0.12426107174773211, abs=1e-9)

    def test_dividing_by_n_minus_one_moves_the_sharpe_ratio(self, spx) -> None:
        sample = heston_sadka(spx, replace(PYTHON_HESTON_SADKA, statistic=Statistic.R))
        assert sample.sharpe == pytest.approx(-0.12150813427802731, abs=1e-9)


class TestHestonSadkaR:
    """Example 7.7 in the revised edition's R, as printed on p. 181."""

    def test_both_figures_reproduce(self, spx) -> None:
        result = heston_sadka(spx, R_HESTON_SADKA)
        assert_reproduces(result.annual_return, -0.011396742529215827, "-0.01139674", ".7g")
        assert_reproduces(result.sharpe, -0.10950975118870672, "-0.1095098", ".7g")

    def test_a_month_with_no_position_is_nan_as_rs_0_over_0_gives(self, spx) -> None:
        """Every such month is dropped, so this holds the rule and moves no figure."""
        returns = monthly_returns(spx, R_HESTON_SADKA).to_numpy()
        assert np.isnan(returns[: R_HESTON_SADKA.dropped]).all()
        assert np.isfinite(returns[R_HESTON_SADKA.dropped :]).all()

    def test_rounding_half_away_from_zero_does_not_print(self, spx) -> None:
        away = heston_sadka(spx, replace(R_HESTON_SADKA, decile_size=round_half_away))
        assert away.annual_return == pytest.approx(-0.0118031107972294, abs=1e-9)

    def test_the_floor_gives_the_revised_matlab_return(self, spx) -> None:
        floored = heston_sadka(spx, replace(R_HESTON_SADKA, decile_size=np.floor))
        assert floored.annual_return == pytest.approx(
            heston_sadka(spx, REVISED_MATLAB).annual_return, abs=1e-15
        )

    def test_dividing_by_n_does_not_print(self, spx) -> None:
        population = heston_sadka(spx, replace(R_HESTON_SADKA, statistic=Statistic.NUMPY))
        assert population.sharpe == pytest.approx(-0.11017547009364882, abs=1e-9)

    def test_masking_on_each_stocks_own_return_does_not_print(self, spx) -> None:
        own_return = heston_sadka(spx, replace(R_HESTON_SADKA, mask=Mask.OWN_RETURN))
        assert own_return.annual_return == pytest.approx(-0.01171463869446247, abs=1e-9)


class TestTheSplitAt2002:
    """Exploratory, with no verdict.

    The revised Python's 83 months, split on the date location 4425 gives.
    """

    def test_the_two_halves(self, spx) -> None:
        before, after = split_at(heston_sadka(spx, PYTHON_HESTON_SADKA), PYTHON_HESTON_SADKA)
        assert before[0] == 13
        assert after[0] == 70
        assert before[1] == pytest.approx(-0.14538748140058178, abs=1e-9)
        assert before[2] == pytest.approx(-0.8599925306287449, abs=1e-9)
        assert after[1] == pytest.approx(0.011966696363436455, abs=1e-9)
        assert after[2] == pytest.approx(0.14177713632213693, abs=1e-9)
        assert [format(v, ".6f") for v in (before[1], before[2], after[1], after[2])] == [
            "-0.145387",
            "-0.859993",
            "0.011967",
            "0.141777",
        ]


@pytest.fixture(scope="module")
def kept(spx) -> pd.Series:
    """The revised Python's 83 kept months, the series the split and the figure read."""
    return monthly_returns(spx, PYTHON_HESTON_SADKA).iloc[PYTHON_HESTON_SADKA.dropped :]


class TestTheYearsInsideTheSplit:
    """Exploratory, with no verdict, like the split they sit inside.

    The calendar-year sums of the revised Python's kept months, which the post's
    Lesson 3 quotes beside its figure of the running sum. A year's sum is twelve
    times its mean, so it is in the same units as each half's annual return.
    First run on 2026-10-03.
    """

    def test_it_reads_the_83_kept_months(self, kept) -> None:
        assert len(kept) == 83
        assert kept.index[0] == pd.Timestamp("2000-12-31")
        assert kept.index[-1] == pd.Timestamp("2007-10-31")

    def test_2002_and_2006(self, kept) -> None:
        years = kept.groupby(kept.index.year).sum()
        assert years[2002] == pytest.approx(0.22273245297832958, abs=1e-9)
        assert years[2006] == pytest.approx(-0.13191102457761186, abs=1e-9)
        assert [format(years[y], ".4f") for y in (2002, 2006)] == ["0.2227", "-0.1319"]

    def test_the_years_swing_wider_than_the_halves_differ(self, spx, kept) -> None:
        years = kept.groupby(kept.index.year).sum()
        before, after = split_at(heston_sadka(spx, PYTHON_HESTON_SADKA), PYTHON_HESTON_SADKA)
        assert years[2002] - years[2006] == pytest.approx(0.35464347755594144, abs=1e-9)
        assert after[1] - before[1] == pytest.approx(0.15735417776401822, abs=1e-9)
        assert years[2002] - years[2006] > after[1] - before[1]

    def test_the_running_sum_peaks_in_january_2006(self, kept) -> None:
        assert kept.cumsum().idxmax() == pd.Timestamp("2006-01-31")


class TestTheReport:
    def test_every_figure_prints_beside_its_panel(self, capsys) -> None:
        seasonals.run()
        out = capsys.readouterr().out
        assert "ijr_20080114/   chan-mat adjusted, saved 2008-01-15" in out
        assert "spx_20071123/   chan-mat adjusted, saved 2007-11-24" in out
        for figure in (
            "-0.0244",
            "-0.0068",
            "-0.023853",
            "-0.003641",
            "average annual return -0.9167, Sharpe ratio -0.1055",
            "average annual return -0.0129, Sharpe ratio -0.1243",
            "average annual return -0.012679, Sharpe ratio -0.122247",
            "average annual return -0.01139674, Sharpe ratio -0.1095098",
            "-0.145387 a year, Sharpe ratio -0.859993",
            "0.011967 a year, Sharpe ratio 0.141777",
        ):
            assert figure in out
        assert out.count("entered 2007-12-31: not computable, the file ends 2008-01-14") == 3
        assert "Exploratory, no verdict" in out

    def test_a_missing_vintage_reaches_the_operator_as_one_line(self, monkeypatch) -> None:
        def refuse(*_args, **_kwargs):
            raise VintageUnavailable("no committed vintage is lifted from IJR_20080114.mat")

        monkeypatch.setattr(seasonals, "load_panel", refuse)
        with pytest.raises(
            SystemExit, match="no committed vintage is lifted from IJR_20080114.mat"
        ):
            seasonals.main()
