"""The pins for Chan's equity seasonals, Examples 7.6 and 7.7, in every printout.

This file is the single authority for every number any prose surface quotes
about either example. ``docs/replication-log.md`` Entry 7 carries the verdicts
and points here row by row.

Three vintages, each read whole through :func:`chan.series.load_panel`.

- **Example 7.6** reads ``data/ijr_20080131/``, 600 members lifted from Chan's
  ``IJR_20080131.mat``, vendor ``chan-mat``, recorded as split-adjusted, saved
  2008-02-02, spanning 2004-01-15 to 2008-02-01. The file comes from the
  revised edition's code as reposted at
  pinhaocheng/epchan-quant_trading_MATLAB_codes ``7430b84``.
- **The earlier S&P 600 save**, ``data/ijr_20080114/``, lifted from
  ``IJR_20080114.mat`` with the same vendor and basis, saved 2008-01-15,
  spanning 2004-01-15 to 2008-01-14. It is read only to say whether the first
  two Januaries move between the saves.
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

A fourth read is not one of Chan's files. ``TestTheSurvivorPins`` runs
Example 7.6 on IJR's 603 members at 2025-12-31 from January 2009, on Alpha
Vantage closes kept in the owner's archive, and its own docstring names that
vintage. It is survivor-only and exploratory, read in one direction only, and
its mechanics run in CI on synthetic closes.

A fifth read is the S&P 600 as it stood at each year-end.
``TestThePointInTimePins`` runs Example 7.6 on IJR's members at every
year-end from 2008 to 2025, from ``research/filings/ijr/members.csv`` at the
sha256 :data:`PIT_MEMBERS_SHA256` holds, on the 1,487 ``sp600`` lines it maps
to, all downloaded 2026-10-05. Its own docstring names that vintage. It is
registered, and its rules, its bound and the flags it reads from the committed
files run in CI.

The 2002 split is exploratory and carries no verdict. First run on 2026-10-02.
P. 180's five-year claim carries one, under a criterion written on issue 254
before any five-year figure was computed, and ``TestTheMostRecentFiveYears``
holds it. First run on 2026-10-04.
"""

from __future__ import annotations

import json
import math
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import chan.equity_seasonals as seasonals
from chan.archive import ArchiveRefused, ArchiveUnavailable
from chan.equity_seasonals import (
    FIRST_EDITION_MATLAB,
    JANUARY_RULES,
    MATLAB_JANUARY,
    PYTHON_HESTON_SADKA,
    PYTHON_JANUARY,
    R_HESTON_SADKA,
    R_JANUARY,
    REVISED_MATLAB,
    TAIL_MONTHS,
    FiveYearCheck,
    HestonSadka,
    Mask,
    Statistic,
    Winners,
    five_year_check,
    heston_sadka,
    january_effect,
    monthly_returns,
    most_recent_five_years,
    split_at,
    summarize,
)
from chan.matlab_helpers import round_half_away, smartstd_book_two
from chan.series import departures, load_panel, panel_line, row_month_ends, vintage_overlap
from chan.vintage import VintageUnavailable

#: The earlier save of Chan's S&P 600 file, which the mirror holds and his script does not load.
EARLIER_SMALL_CAPS = "IJR_20080114.mat"


@pytest.fixture(scope="module")
def small_caps():
    """Loaded once, because ``load_panel`` hashes and parses all 600 members."""
    return load_panel(seasonals.SMALL_CAPS)


@pytest.fixture(scope="module")
def earlier_small_caps():
    """The earlier save, read only to say whether the first two Januaries move."""
    return load_panel(EARLIER_SMALL_CAPS)


@pytest.fixture(scope="module")
def large_caps():
    """Loaded once, because ``load_panel`` hashes and parses all 500 members."""
    return load_panel(seasonals.LARGE_CAPS)


@pytest.fixture(scope="module")
def ijr(small_caps) -> pd.DataFrame:
    return small_caps[1]


@pytest.fixture(scope="module")
def earlier_ijr(earlier_small_caps) -> pd.DataFrame:
    return earlier_small_caps[1]


@pytest.fixture(scope="module")
def spx(large_caps) -> pd.DataFrame:
    return large_caps[1]


def assert_reproduces(value: float, full: float, printed: str, spec: str) -> None:
    """The full value at 1e-9, and the figure as its source prints it."""
    assert value == pytest.approx(full, abs=1e-9)
    assert format(value, spec) == printed


def returns_of(effect) -> list[float]:
    return [trade.ret for trade in effect.trades]


def year_ends_and_januaries(closes: pd.DataFrame) -> tuple[list[str], list[str]]:
    """The December and January month-ends ``example7_6.m`` finds, by row."""
    days = closes.index[row_month_ends(closes.index)]
    return (
        [str(day.date()) for day in days if day.month == 12],
        [str(day.date()) for day in days if day.month == 1],
    )


class TestThePanels:
    def test_the_small_cap_panel(self, small_caps) -> None:
        members, closes = small_caps
        assert seasonals.SMALL_CAPS == "IJR_20080131.mat"
        assert len(members) == 600
        assert closes.index[0] == pd.Timestamp("2004-01-15")
        assert closes.index[-1] == pd.Timestamp("2008-02-01")
        assert panel_line(members) == (
            "ijr_20080131/   chan-mat adjusted, saved 2008-02-02, 600 members lifted from "
            "IJR_20080131.mat"
        )

    def test_the_earlier_small_cap_panel(self, earlier_small_caps) -> None:
        members, closes = earlier_small_caps
        assert len(members) == 600
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

    def test_the_three_januaries_reproduce(self, ijr) -> None:
        trades = january_effect(ijr, MATLAB_JANUARY).trades
        assert [(t.entered, t.exited) for t in trades] == [
            (pd.Timestamp("2005-12-30"), pd.Timestamp("2006-01-31")),
            (pd.Timestamp("2006-12-29"), pd.Timestamp("2007-01-31")),
            (pd.Timestamp("2007-12-31"), pd.Timestamp("2008-01-31")),
        ]
        assert_reproduces(trades[0].ret, -0.024368881797563913, "-0.0244", ".4f")
        assert_reproduces(trades[1].ret, -0.006796429884419337, "-0.0068", ".4f")
        assert_reproduces(trades[2].ret, 0.08807964565655355, "0.0881", ".4f")

    def test_the_script_as_written_pairs_its_dates_on_its_own_file(self, ijr) -> None:
        """Four year-ends and five January month-ends, and the script drops the first January.

        That leaves four Januaries against four Decembers, each in the year
        after its December, so the script's check passes on the file it loads.
        """
        decembers, januaries = year_ends_and_januaries(ijr)
        assert decembers == ["2004-12-31", "2005-12-30", "2006-12-29", "2007-12-31"]
        assert januaries == ["2004-01-30", "2005-01-31", "2006-01-31", "2007-01-31", "2008-01-31"]
        kept = januaries[1:]
        assert [int(jan[:4]) - int(dec[:4]) for dec, jan in zip(decembers, kept, strict=True)] == [
            1,
            1,
            1,
            1,
        ]

    def test_the_script_as_written_cannot_pair_its_dates_on_the_earlier_save(
        self, earlier_ijr
    ) -> None:
        """Four year-ends and four January month-ends, and the script drops the first January.

        That leaves three Januaries against four Decembers, so its check that
        each January follows its December fails before anything prints.
        """
        decembers, januaries = year_ends_and_januaries(earlier_ijr)
        assert decembers == ["2004-12-31", "2005-12-30", "2006-12-29", "2007-12-31"]
        assert januaries == ["2004-01-30", "2005-01-31", "2006-01-31", "2007-01-31"]
        assert len(januaries[1:]) != len(decembers)

    def test_the_decile_is_rounded_half_away_from_zero(self, ijr) -> None:
        trades = january_effect(ijr, MATLAB_JANUARY).trades
        assert [(t.ranked, t.longs, t.shorts) for t in trades] == [
            (578, 58, 58),
            (592, 59, 59),
            (594, 59, 59),
        ]

    def test_rounding_the_decile_down_moves_january_2006(self, ijr) -> None:
        floored = january_effect(ijr, replace(MATLAB_JANUARY, decile_size=np.floor))
        assert returns_of(floored)[0] == pytest.approx(-0.02335614494703974, abs=1e-9)
        assert format(returns_of(floored)[0], ".4f") == "-0.0234"

    @pytest.mark.parametrize("rules", JANUARY_RULES, ids=lambda rules: rules.source)
    def test_the_third_january_needs_the_row_after_it(self, ijr, rules) -> None:
        """The file is named for 2008-01-31 and its last row is 2008-02-01.

        Every printout finds a month's end by looking at the day after it, so
        cut at 2008-01-31 the file has no January 2008 to close the holding in.
        """
        cut = january_effect(ijr.loc[:"2008-01-31"], rules)
        assert cut.unreached == (pd.Timestamp("2007-12-31"),)
        assert len(cut.trades) == 2

    def test_each_trade_pays_two_one_way_costs_of_five_basis_points(self, ijr, monkeypatch) -> None:
        assert seasonals.ONE_WAY_COST == 0.0005
        costed = returns_of(january_effect(ijr, MATLAB_JANUARY))
        monkeypatch.setattr(seasonals, "ONE_WAY_COST", 0.0)
        free = returns_of(january_effect(ijr, MATLAB_JANUARY))
        assert [f - c for f, c in zip(free, costed, strict=True)] == pytest.approx(
            [0.001, 0.001, 0.001], abs=1e-15
        )


class TestJanuaryPython:
    """Example 7.6 under the revised ``example7_6.py``."""

    def test_the_three_januaries_reproduce(self, ijr) -> None:
        effect = january_effect(ijr, PYTHON_JANUARY)
        assert [t.exited for t in effect.trades] == [
            pd.Timestamp("2006-01-31"),
            pd.Timestamp("2007-01-31"),
            pd.Timestamp("2008-01-31"),
        ]
        assert_reproduces(effect.trades[0].ret, -0.023853172610774076, "-0.023853", ".6f")
        assert_reproduces(effect.trades[1].ret, -0.00364117175573088, "-0.003641", ".6f")
        assert_reproduces(effect.trades[2].ret, 0.08848639560403175, "0.088486", ".6f")
        assert effect.unreached == ()

    def test_the_winners_slice_holds_two_fewer_than_the_decile(self, ijr) -> None:
        trades = january_effect(ijr, PYTHON_JANUARY).trades
        assert [(t.ranked, t.longs, t.shorts) for t in trades] == [
            (579, 58, 56),
            (593, 59, 57),
            (595, 60, 58),
        ]

    def test_the_forward_fill_ranks_one_more_stock_and_moves_january_2008(self, ijr) -> None:
        """PMC has no close in 2005 or 2006, and pandas before 3.0 ranks it on a padded close.

        Without the fill the script ranks 578, 592 and 594, the MATLAB counts.
        That moves neither of the first two returns, because a tenth of 578 or
        579 and of 592 or 593 rounds to the same size. A tenth of 595 is 59.5,
        which rounds to 60, and a tenth of 594 rounds to 59, so in January
        2008 the fill adds a stock to each side and moves the printed figure.
        """
        unpadded = january_effect(ijr, replace(PYTHON_JANUARY, pads_year_ends=False))
        padded = january_effect(ijr, PYTHON_JANUARY)
        assert [(t.ranked, t.longs) for t in unpadded.trades] == [(578, 58), (592, 59), (594, 59)]
        assert returns_of(unpadded)[:2] == pytest.approx(returns_of(padded)[:2], abs=1e-15)
        assert unpadded.trades[2].ret == pytest.approx(0.0909075804839564, abs=1e-9)
        assert format(unpadded.trades[2].ret, ".6f") == "0.090908"

    def test_the_fill_reads_pmcs_gap_as_a_2007_gain(self, ijr) -> None:
        """PMC's last close before its 851-day gap stands in for its 2005 and 2006 year-ends."""
        filled = ijr.resample("YE").last().iloc[:-1].ffill()
        assert filled["PMC"].tolist() == [6.02, 6.02, 6.02, 13.88]
        gain = (filled.iloc[-1] - filled.iloc[-2]) / filled.iloc[-2]
        assert gain["PMC"] == pytest.approx(1.3056478405315617, abs=1e-12)
        assert int((gain.dropna() > gain["PMC"]).sum()) + 1 == 4
        assert int(gain.notna().sum()) == 595

    def test_the_full_decile_gives_the_first_editions_figures_until_2008(self, ijr) -> None:
        """In 2006 and 2007 the two editions' printouts differ by the winners' slice alone.

        In 2008 they differ by the forward fill too, so the full decile alone
        gives 0.085757, and dropping the fill as well gives MATLAB's 0.0881.
        """
        full = january_effect(ijr, replace(PYTHON_JANUARY, winners=Winners.DECILE))
        matlab = january_effect(ijr, MATLAB_JANUARY)
        assert returns_of(full)[:2] == pytest.approx(returns_of(matlab)[:2], abs=1e-15)
        assert full.trades[2].ret == pytest.approx(0.08575740297161999, abs=1e-9)
        assert format(full.trades[2].ret, ".6f") == "0.085757"
        both = january_effect(
            ijr, replace(PYTHON_JANUARY, winners=Winners.DECILE, pads_year_ends=False)
        )
        assert returns_of(both) == pytest.approx(returns_of(matlab), abs=1e-15)


class TestJanuaryR:
    """Example 7.6 in the revised edition's R, which prints MATLAB's three figures."""

    def test_the_three_januaries_reproduce(self, ijr) -> None:
        trades = january_effect(ijr, R_JANUARY).trades
        assert_reproduces(trades[0].ret, -0.024368881797563913, "-0.0244", ".4f")
        assert_reproduces(trades[1].ret, -0.006796429884419337, "-0.0068", ".4f")
        assert_reproduces(trades[2].ret, 0.08807964565655355, "0.0881", ".4f")

    def test_no_decile_on_this_file_lands_on_a_half(self, ijr) -> None:
        """No decile lands on a half, so R's rounding and MATLAB's pick the same stocks."""
        trades = january_effect(ijr, R_JANUARY).trades
        assert len(trades) == 3
        for trade in trades:
            assert (trade.ranked / 10) % 1 != 0.5


class TestTheTwoSmallCapSaves:
    """Whether the first two Januaries move between Chan's 2008-01-14 and 2008-01-31 saves.

    A vendor can restate history between two saves, and these were saved 18
    days apart, on 2008-01-15 and 2008-02-02. ``chan.series.vintage_overlap``
    sets each stock's two vintages side by side on the days both hold, and
    ``chan.series.departures`` keeps the days they disagree.
    """

    @pytest.mark.parametrize("rules", JANUARY_RULES, ids=lambda rules: rules.source)
    def test_the_first_two_januaries_do_not_move(self, ijr, earlier_ijr, rules) -> None:
        earlier = january_effect(earlier_ijr, rules)
        later = january_effect(ijr, rules)
        assert earlier.trades == later.trades[:2]
        assert earlier.unreached == (pd.Timestamp("2007-12-31"),)
        assert earlier.file_end == pd.Timestamp("2008-01-14")

    def test_the_saves_disagree_only_in_the_earlier_ones_last_six_days(
        self, small_caps, earlier_small_caps
    ) -> None:
        """198 closes in 42 stocks, every one between 2008-01-07 and 2008-01-14.

        The first two Januaries read no close after 2007-01-31, which is why
        they do not move. The tolerance is zero because both saves are one
        vendor's binary floats. A half cent finds the same 198, so no
        departure is a rounding.
        """
        later = {entry.symbol: entry for entry in small_caps[0]}
        shared, found, half_cent = 0, {}, 0
        for entry in earlier_small_caps[0]:
            overlap = vintage_overlap(
                (entry, earlier_small_caps[1][entry.symbol].dropna()),
                (later[entry.symbol], small_caps[1][entry.symbol].dropna()),
            )
            shared += len(overlap)
            moved = departures(overlap, tolerance=0.0)
            if len(moved):
                found[entry.symbol] = moved
            half_cent += len(departures(overlap, tolerance=0.005))
        disagree = pd.concat(found.values())

        assert shared == 589_660
        assert len(disagree) == 198 == half_cent
        assert len(found) == 42
        assert sorted({str(day.date()) for day in disagree.index}) == [
            "2008-01-07",
            "2008-01-08",
            "2008-01-09",
            "2008-01-10",
            "2008-01-11",
            "2008-01-14",
        ]

    def test_insp_is_rescaled_on_two_days(self, small_caps, earlier_small_caps) -> None:
        """The later save scales two of INSP's closes by 0.4969 and leaves the days before alone."""
        insp = vintage_overlap(
            *(
                (next(e for e in members if e.symbol == "INSP"), closes["INSP"].dropna())
                for members, closes in (earlier_small_caps, small_caps)
            )
        )
        moved = departures(insp, tolerance=0.0)
        assert [str(day.date()) for day in moved.index] == ["2008-01-07", "2008-01-08"]
        assert moved["ratio"].round(4).tolist() == [0.4969, 0.4969]


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
        ends = spx.index[row_month_ends(spx.index)]
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
            ends = spx.iloc[row_month_ends(spx.index)]
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
        ends = row_month_ends(spx.index)
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


class TestTheMostRecentFiveYears:
    """P. 180's claim that the most recent five years give even worse average returns.

    The owner ruled on 2026-10-04 that the check runs under the revised MATLAB's
    rules, with the revised Python's reported beside them. The criterion was
    written on [issue 254](https://github.com/l3a0/quantitative-trading/issues/254)
    before any five-year figure was computed, and these were first run on
    2026-10-04 after it.

    Reading 1 reruns the program unchanged on the rows of ``SPX_20071123`` dated
    after 2002-11-23, and its annual return carries the verdict: reproduced if it
    is below the whole period's at full precision. Reading 2 averages the full
    run's last 60 kept months and carries no verdict, and neither does any Sharpe
    ratio. The rerun's annual return has a standard error of 0.0281 a year, about
    eight times its gap from the whole period's, so the verdict says whether
    Chan's comparison holds on his file of survivors, not whether the effect
    weakened.
    """

    def test_the_rerun_reads_the_rows_after_2002_11_23(self, spx) -> None:
        assert seasonals.five_year_cutoff(spx) == pd.Timestamp("2002-11-23")
        cut = most_recent_five_years(spx)
        assert cut.index[0] == pd.Timestamp("2002-11-25")
        assert cut.index[-1] == pd.Timestamp("2007-11-23")

    @pytest.mark.parametrize(
        "rules", [REVISED_MATLAB, PYTHON_HESTON_SADKA], ids=["matlab", "python"]
    )
    def test_the_rerun_keeps_the_full_runs_last_47_months(self, spx, rules) -> None:
        """Cutting the input changes which months are kept and none of their values."""
        check = five_year_check(spx, rules)
        assert len(check.rerun_kept) == 47
        assert check.rerun_kept.index[0] == pd.Timestamp("2003-12-31")
        assert check.rerun_kept.index[-1] == pd.Timestamp("2007-10-31")
        assert check.rerun_kept.notna().all()
        whole = check.whole.returns.iloc[rules.dropped :].iloc[-47:]
        pd.testing.assert_series_equal(check.rerun_kept, whole)

    @pytest.mark.parametrize(
        ("rules", "first"),
        [(REVISED_MATLAB, "2002-11-29"), (PYTHON_HESTON_SADKA, "2002-11-30")],
        ids=["matlab", "python"],
    )
    def test_the_tail_starts_in_november_2002(self, spx, rules, first) -> None:
        """The MATLAB finds a month-end by row and the Python by calendar."""
        kept = five_year_check(spx, rules).whole.returns.iloc[rules.dropped :]
        assert kept.iloc[-TAIL_MONTHS:].index[0] == pd.Timestamp(first)
        assert kept.index[-1] == pd.Timestamp("2007-10-31")

    def test_a_row_on_the_cutoff_is_left_out(self) -> None:
        """Rows after the cutoff, not from it. No row of the committed file sits on it."""
        days = pd.DatetimeIndex(["2002-11-22", "2002-11-23", "2002-11-25", "2007-11-23"])
        closes = pd.DataFrame({"X": [1.0, 2.0, 3.0, 4.0]}, index=days)
        assert list(most_recent_five_years(closes).index) == list(days[2:])

    def test_the_claim_is_pinned_as_chans_words(self) -> None:
        assert seasonals.FIVE_YEAR_PAGE == 180
        assert seasonals.FIVE_YEAR_CLAIM == (
            "the most recent five years instead of the entire data period"
        )

    @pytest.mark.parametrize(
        ("rerun", "whole", "worse"),
        [
            (-0.02, -0.01, True),
            (-0.01001, -0.01, True),
            (-0.01, -0.01, False),
            (0.0, -0.01, False),
        ],
        ids=["below", "below-at-full-precision", "equal", "above"],
    )
    def test_the_verdict_reads_only_the_reruns_annual_return(self, rerun, whole, worse) -> None:
        """Strictly below, on the annual return, whatever the Sharpe ratios and the tail say.

        Every other figure the check computes is also worse than the whole period
        on this file, so the real data cannot tell the declared rule from a swap.
        """
        empty = pd.Series(dtype=float)
        check = FiveYearCheck(
            whole=HestonSadka(returns=empty, annual_return=whole, sharpe=-9.0),
            rerun=HestonSadka(returns=empty, annual_return=rerun, sharpe=9.0),
            rerun_kept=empty,
            tail=(60, 9.0, 9.0),
        )
        assert check.worse is worse

    def test_the_23_months_the_rerun_leaves_out_of_the_split_made_money(self, kept) -> None:
        """Exploratory, with no verdict, like the split.

        The revised Python's 70 months from 2002 return 0.011967 a year and its
        last 47 return -0.016431. The 23 between them, January 2002 to
        November 2003, are what turn one into the other.
        """
        between = kept[(kept.index >= "2002-01-01") & (kept.index < "2003-12-01")]
        assert len(between) == 23
        assert between.index[0] == pd.Timestamp("2002-01-31")
        assert between.index[-1] == pd.Timestamp("2003-11-30")
        annual, _ = summarize(between, replace(PYTHON_HESTON_SADKA, dropped=0))
        assert_reproduces(annual, 0.06999696732165601, "0.069997", ".6f")

    def test_the_revised_matlab_reproduces_the_claim(self, spx) -> None:
        check = five_year_check(spx, REVISED_MATLAB)
        assert_reproduces(check.whole.annual_return, -0.012922703586771995, "-0.0129", ".4f")
        assert_reproduces(check.rerun.annual_return, -0.016502156222333787, "-0.0165", ".4f")
        assert check.worse

    def test_the_gap_is_far_inside_the_noise_of_47_months(self, spx) -> None:
        """The standard error of the rerun's annual return, on book two's ``smartstd``."""
        check = five_year_check(spx, REVISED_MATLAB)
        kept = check.rerun_kept.to_numpy()
        monthly = smartstd_book_two(kept)
        error = 12 * monthly / math.sqrt(len(kept))
        gap = check.rerun.annual_return - check.whole.annual_return
        assert monthly == pytest.approx(0.01607494842406708, abs=1e-9)
        assert_reproduces(error, 0.028137266582467655, "0.0281", ".4f")
        assert_reproduces(gap, -0.0035794526355617928, "-0.0036", ".4f")
        assert format(error / abs(gap), ".1f") == "7.9"

    def test_the_revised_matlab_figures_with_no_verdict(self, spx) -> None:
        check = five_year_check(spx, REVISED_MATLAB)
        assert_reproduces(check.rerun.sharpe, -0.296346964414183, "-0.2963", ".4f")
        months, annual, sharpe = check.tail
        assert months == 60
        assert_reproduces(annual, -0.017065622236990454, "-0.0171", ".4f")
        assert_reproduces(sharpe, -0.2608812443118037, "-0.2609", ".4f")

    def test_the_revised_python_beside_it_with_no_verdict(self, spx) -> None:
        check = five_year_check(spx, PYTHON_HESTON_SADKA)
        assert_reproduces(check.whole.annual_return, -0.012679138708036275, "-0.012679", ".6f")
        assert_reproduces(check.rerun.annual_return, -0.01643109580760715, "-0.016431", ".6f")
        assert_reproduces(check.rerun.sharpe, -0.2949518936016059, "-0.294952", ".6f")
        months, annual, sharpe = check.tail
        assert months == 60
        assert_reproduces(annual, -0.017010774055752898, "-0.017011", ".6f")
        assert_reproduces(sharpe, -0.25998538649554387, "-0.259985", ".6f")
        assert check.worse


class TestTheReport:
    def test_every_figure_prints_beside_its_panel(self, capsys) -> None:
        seasonals.run()
        out = capsys.readouterr().out
        assert "ijr_20080131/   chan-mat adjusted, saved 2008-02-02" in out
        assert "spx_20071123/   chan-mat adjusted, saved 2007-11-24" in out
        for figure in (
            "entered 2005-12-30 exited 2006-01-31: -0.0244",
            "entered 2006-12-29 exited 2007-01-31: -0.0068",
            "entered 2007-12-31 exited 2008-01-31: 0.0881",
            "-0.023853",
            "-0.003641",
            "entered 2007-12-31 exited 2008-01-31: 0.088486",
            "average annual return -0.9167, Sharpe ratio -0.1055",
            "average annual return -0.0129, Sharpe ratio -0.1243",
            "average annual return -0.012679, Sharpe ratio -0.122247",
            "average annual return -0.01139674, Sharpe ratio -0.1095098",
            "-0.145387 a year, Sharpe ratio -0.859993",
            "0.011967 a year, Sharpe ratio 0.141777",
            "rows after 2002-11-23",
            "revised edition, reproduced: rerun on 47 months -0.0165 a year against the "
            "whole period's -0.0129. Its Sharpe ratio -0.2963, no verdict.",
            "The last 60 months -0.0171 a year, Sharpe ratio -0.2609, no verdict",
            "example7_7.py, revised edition, no verdict: rerun on 47 months -0.016431 a "
            "year against the whole period's -0.012679. Its Sharpe ratio -0.294952, no "
            "verdict. The last 60 months -0.017011 a year, Sharpe ratio -0.259985, no verdict",
        ):
            assert figure in out
        assert out.count("exited 2008-01-31: 0.0881 ") == 2
        assert out.count("rerun on ") == 2
        assert "not computable" not in out
        assert "Exploratory, no verdict" in out

    def test_a_claim_that_fails_prints_as_not_reproduced(
        self, large_caps, monkeypatch, capsys
    ) -> None:
        """The committed file reproduces the claim, so the other branch is driven by hand."""
        monkeypatch.setattr(FiveYearCheck, "worse", property(lambda self: False))
        seasonals.report_heston_sadka(*large_caps)
        out = capsys.readouterr().out
        assert "Example 7.7 in MATLAB, revised edition, not reproduced: rerun on 47" in out
        assert "example7_7.py, revised edition, no verdict: rerun on 47" in out

    def test_each_holding_prints_with_its_positions(self, capsys) -> None:
        seasonals.run()
        out = capsys.readouterr().out
        assert "exited 2008-01-31: 0.088486   (60 long and 58 short of 595 ranked)" in out
        assert out.count("exited 2008-01-31: 0.0881   (59 long and 59 short of 594 ranked)") == 2

    def test_a_january_the_file_ends_before_prints_as_not_computable(
        self, small_caps, capsys
    ) -> None:
        """The committed file reaches every January, so the line is driven on a cut panel."""
        members, closes = small_caps
        seasonals.report_january(members, closes.loc[:"2008-01-31"])
        out = capsys.readouterr().out
        assert (
            out.count(
                "entered 2007-12-31: not computable, the file ends 2008-01-31 before the "
                "January it holds through"
            )
            == 3
        )

    def test_a_missing_vintage_reaches_the_operator_as_one_line(self, monkeypatch) -> None:
        def refuse(*_args, **_kwargs):
            raise VintageUnavailable("no committed vintage is lifted from IJR_20080131.mat")

        monkeypatch.setattr(seasonals, "load_panel", refuse)
        with pytest.raises(
            SystemExit, match="no committed vintage is lifted from IJR_20080131.mat"
        ):
            seasonals.main()


# --------------------------------------------------------------------------
# Example 7.6 on IJR's members at 2025-12-31, survivor-only
# --------------------------------------------------------------------------


def synthetic_closes(start: str = "2005-06-01", end: str = "2026-02-27", members: int = 30):
    """Positive random walks on every weekday, with that same calendar beside them."""
    calendar = pd.bdate_range(start, end)
    rng = np.random.default_rng(333)
    walks = np.exp(np.cumsum(rng.normal(0.0, 0.02, (len(calendar), members)), axis=0))
    columns = [f"S{number:02d}" for number in range(members)]
    return pd.DataFrame(20.0 * walks, index=calendar, columns=columns), calendar


class TestTheSurvivorMembers:
    """IJR's members at 2025-12-31, as ``research/filings/ijr/2025-12-31.csv`` records them.

    That file is read from the Form N-PORT at accession ``0000940400-26-007526``
    through ``chan.fund_holdings``' member rule, which drops OmniAb's two
    earnout rows. It is committed, so these run everywhere.
    """

    def test_there_are_603_and_each_maps_to_its_own_symbol(self) -> None:
        pairs = seasonals.survivor_members()
        assert len(pairs) == 603
        assert len({symbol for _, symbol in pairs}) == 603
        assert seasonals.survivor_filing().accession == "0000940400-26-007526"

    def test_every_map_entry_names_a_member(self) -> None:
        tickers = {ticker for ticker, _ in seasonals.survivor_members()}
        assert set(seasonals.ALPHAVANTAGE_SYMBOLS) <= tickers
        assert len(seasonals.ALPHAVANTAGE_SYMBOLS) == 11

    def test_only_the_two_share_classes_carry_a_slash(self) -> None:
        """A ticker with a slash is not a symbol Alpha Vantage files, so each needs an entry."""
        slashed = sorted(t for t, _ in seasonals.survivor_members() if not t.isalpha())
        assert slashed == ["CWEN/A", "MOG/A"]
        assert seasonals.ALPHAVANTAGE_SYMBOLS["CWEN/A"] == "CWEN-A"
        assert seasonals.ALPHAVANTAGE_SYMBOLS["MOG/A"] == "MOG-A"

    def test_every_symbol_is_one_the_fetch_accepts(self) -> None:
        from chan.vintage import SYMBOL_PATTERN

        assert all(SYMBOL_PATTERN.fullmatch(s) for _, s in seasonals.survivor_members())

    def test_a_member_with_no_ticker_is_refused(self, tmp_path) -> None:
        from chan.fund_holdings import FILINGS_DIR

        source = FILINGS_DIR / "ijr" / "2025-12-31.csv"
        (tmp_path / "ijr").mkdir()
        lines = source.read_text(encoding="utf-8").splitlines()
        lines[5] = lines[5].rsplit(",", 1)[0] + ","
        (tmp_path / "ijr" / "2025-12-31.csv").write_text("\n".join(lines) + "\n", "utf-8")
        with pytest.raises(ValueError, match="1 members carry no ticker"):
            seasonals.survivor_members(tmp_path)

    def test_a_member_with_no_line_is_named_by_ticker_and_symbol(self) -> None:
        pairs = [("STRA", "STRA"), ("AXL", "DCH"), ("GES", "GES")]
        assert seasonals.missing_members(pairs, {"GES"}) == ("STRA", "AXL as DCH")
        assert seasonals.missing_members(pairs, {"STRA", "DCH", "GES"}) == ()

    def test_two_members_on_one_symbol_are_refused(self, monkeypatch) -> None:
        monkeypatch.setitem(seasonals.ALPHAVANTAGE_SYMBOLS, "AXL", "STRA")
        with pytest.raises(ValueError, match="two members map to STRA"):
            seasonals.survivor_members()


class TestTheOneSidedTest:
    def test_it_agrees_with_scipys_one_sample_test(self) -> None:
        from scipy import stats

        returns = [0.03, -0.01, 0.05, 0.02, -0.04, 0.06, 0.01]
        test = seasonals.one_sided_t(returns)
        reference = stats.ttest_1samp(returns, 0.0, alternative="greater")
        assert test.t == pytest.approx(reference.statistic, abs=1e-12)
        assert test.p == pytest.approx(reference.pvalue, abs=1e-12)
        assert test.std == pytest.approx(np.std(returns, ddof=1), abs=1e-15)
        assert test.n == 7

    @pytest.mark.parametrize(("p", "rejects"), [(0.0499, True), (0.05, False), (0.2, False)])
    def test_it_rejects_strictly_below_five_percent(self, p, rejects) -> None:
        assert seasonals.OneSided(n=18, mean=0.01, std=0.05, t=1.0, p=p).rejects is rejects

    def test_x_is_3_70_percent_at_6_05_percent_and_18_januaries(self) -> None:
        """The power the issue states before the run, on Chan's three printed Januaries."""
        x = seasonals.detectable_mean(0.0605, 18)
        assert x == pytest.approx(0.036958390706667864, abs=1e-12)
        assert format(x, ".2%") == "3.70%"

    def test_x_is_where_the_noncentral_t_rejects_with_80_percent(self) -> None:
        from scipy import stats

        x = seasonals.detectable_mean(0.0605, 18)
        critical = stats.t.isf(0.05, 17)
        assert stats.nct.sf(critical, 17, x * math.sqrt(18) / 0.0605) == pytest.approx(0.8)

    @pytest.mark.parametrize(("significance", "power"), [(0.05, 0.9), (0.01, 0.8), (0.1, 0.5)])
    def test_x_follows_the_size_and_power_it_is_given(self, significance, power) -> None:
        from scipy import stats

        x = seasonals.detectable_mean(0.0605, 18, significance=significance, power=power)
        critical = stats.t.isf(significance, 17)
        assert stats.nct.sf(critical, 17, x * math.sqrt(18) / 0.0605) == pytest.approx(power)

    def test_the_normal_approximation_gives_3_55_percent(self) -> None:
        """The figure the issue quoted first, smaller because it treats the deviation as known."""
        from scipy import stats

        shift = stats.norm.isf(0.05) + stats.norm.isf(0.2)
        assert format(shift * 0.0605 / math.sqrt(18), ".2%") == "3.55%"


class TestTheSurvivorRun:
    """The run's rules on synthetic closes, so they hold in CI with no archive."""

    def test_a_slice_from_december_2007_yields_18_januaries(self) -> None:
        closes, calendar = synthetic_closes()
        effect = seasonals.survivor_effect(closes, calendar)
        assert len(effect.trades) == 18
        assert effect.trades[0].entered == pd.Timestamp("2008-12-31")
        assert effect.trades[0].exited == pd.Timestamp("2009-01-30")
        assert effect.trades[-1].entered == pd.Timestamp("2025-12-31")
        assert effect.trades[-1].exited == pd.Timestamp("2026-01-30")

    def test_the_calendar_is_the_committed_raw_spy_download(self) -> None:
        entry, _ = seasonals.survivor_calendar()
        assert entry.path == "yfinance_spy_raw_1993-01-29_2026-10-02_dl2026-10-03.csv"

    def test_the_counts_read_the_slice_and_not_the_years_before_it(self) -> None:
        """Closes from 2005 would give two more Januaries and more year-ends unsliced."""
        closes, _ = synthetic_closes()
        closes.loc[:"2007-06-30", "S09"] = np.nan
        assert len(seasonals.ranked_without_exit(closes)) == 18
        assert "S09" not in seasonals.year_ends_missed(closes)

    def test_the_slice_drops_rows_before_december_2007(self) -> None:
        closes, _ = synthetic_closes()
        assert seasonals.survivor_slice(closes).index[0] == pd.Timestamp("2007-12-03")

    def test_closes_starting_in_2008_are_refused_for_one_january_short(self) -> None:
        closes, calendar = synthetic_closes(start="2008-01-02")
        with pytest.raises(seasonals.SurvivorRunRefused, match="yields 17 Januaries, not 18"):
            seasonals.survivor_effect(closes, calendar)

    def test_closes_ending_on_the_last_january_day_are_refused(self) -> None:
        """2026-01-30 is the last row, so it ends no month and 2025-12-31 has no exit."""
        closes, calendar = synthetic_closes(end="2026-01-30")
        with pytest.raises(
            seasonals.SurvivorRunRefused,
            match="end 2026-01-30, before the January after 2025-12-31",
        ):
            seasonals.survivor_effect(closes, calendar)

    def test_a_row_the_calendar_lacks_is_refused_by_symbol_and_date(self) -> None:
        closes, calendar = synthetic_closes()
        saturday = pd.Timestamp("2015-12-26")
        closes.loc[saturday] = np.nan
        closes.loc[saturday, "S07"] = 10.0
        closes = closes.sort_index()
        with pytest.raises(seasonals.SurvivorRunRefused, match="S07 has a row on 2015-12-26"):
            seasonals.survivor_effect(closes, calendar)

    def test_a_row_the_calendar_lacks_would_otherwise_become_a_year_end(self) -> None:
        """Why the refusal exists: a stray Saturday after the last December day ends the year.

        2016-12-30 is the last weekday of 2016. One series with a row on the
        Saturday after it makes that row the year-end, on which only that
        series has a close, so one stock is ranked and the January is NaN.
        """
        closes, _ = synthetic_closes()
        saturday = pd.Timestamp("2016-12-31")
        closes.loc[saturday] = np.nan
        closes.loc[saturday, "S07"] = 10.0
        closes = closes.sort_index()
        effect = january_effect(seasonals.survivor_slice(closes), MATLAB_JANUARY)
        (stray,) = [trade for trade in effect.trades if trade.entered.year == 2016]
        assert stray.entered == saturday
        assert stray.ranked == 1
        assert math.isnan(stray.ret)

    def test_an_exit_off_the_calendars_last_january_day_is_refused(self) -> None:
        closes, calendar = synthetic_closes()
        closes = closes.drop(pd.Timestamp("2016-01-29"))
        with pytest.raises(
            seasonals.SurvivorRunRefused, match="entered 2015-12-31 and exited 2016-01-28"
        ):
            seasonals.survivor_effect(closes, calendar)

    def test_the_earliest_off_calendar_day_is_named_with_the_count(self) -> None:
        closes, calendar = synthetic_closes()
        for day, symbol in (("2019-06-15", "S02"), ("2012-03-10", "S08")):
            closes.loc[pd.Timestamp(day)] = np.nan
            closes.loc[pd.Timestamp(day), symbol] = 10.0
        closes = closes.sort_index()
        with pytest.raises(
            seasonals.SurvivorRunRefused,
            match="S08 has a row on 2012-03-10, which the SPY calendar does not hold, and 2 such",
        ):
            seasonals.survivor_effect(closes, calendar)

    def test_the_earliest_nonpositive_close_is_named(self) -> None:
        closes, calendar = synthetic_closes()
        closes.loc["2020-05-01", "S01"] = 0.0
        closes.loc["2011-02-01", "S06"] = -2.0
        with pytest.raises(seasonals.SurvivorRunRefused, match="S06 closes at -2.0 on 2011-02-01"):
            seasonals.survivor_effect(closes, calendar)

    def test_a_trade_off_the_calendars_last_december_day_is_refused(self) -> None:
        """A calendar day no member trades on moves the year-end, and the run says so."""
        closes, calendar = synthetic_closes()
        closes = closes.drop(pd.Timestamp("2015-12-31"))
        with pytest.raises(
            seasonals.SurvivorRunRefused, match="entered 2015-12-30 and exited 2016-01-29"
        ):
            seasonals.survivor_effect(closes, calendar)

    @pytest.mark.parametrize("close", [0.0, -1.0])
    def test_a_close_of_zero_or_below_is_refused_by_symbol_and_date(self, close) -> None:
        closes, calendar = synthetic_closes()
        closes.loc["2012-01-31", "S03"] = close
        with pytest.raises(
            seasonals.SurvivorRunRefused, match=f"S03 closes at {close} on 2012-01-31"
        ):
            seasonals.survivor_effect(closes, calendar)

    def test_a_zero_exit_close_would_otherwise_be_averaged_in_as_a_total_loss(self) -> None:
        closes, _ = synthetic_closes()
        sliced = seasonals.survivor_slice(closes)
        before = january_effect(sliced, MATLAB_JANUARY).trades[3].ret
        zeroed = sliced.copy()
        zeroed.loc["2012-01-31", :] = 0.0
        after = january_effect(zeroed, MATLAB_JANUARY).trades[3].ret
        assert after != pytest.approx(before)
        assert after == pytest.approx(-2 * seasonals.ONE_WAY_COST)

    def test_a_missing_close_is_not_refused(self) -> None:
        closes, calendar = synthetic_closes()
        closes.loc["2012-01-31", "S03"] = np.nan
        assert len(seasonals.survivor_effect(closes, calendar).trades) == 18

    def test_returns_before_costs_add_back_two_one_way_costs(self) -> None:
        closes, calendar = synthetic_closes()
        effect = seasonals.survivor_effect(closes, calendar)
        before = seasonals.before_costs(effect)
        assert [b - t.ret for b, t in zip(before, effect.trades, strict=True)] == pytest.approx(
            [0.001] * 18, abs=1e-15
        )

    def test_a_member_with_no_exit_close_is_counted(self) -> None:
        closes, _ = synthetic_closes()
        closes.loc["2026-01-23":, "S05"] = np.nan
        counts = seasonals.ranked_without_exit(closes)
        assert len(counts) == 18
        assert counts[-1] == 1
        assert sum(counts[:-1]) == 0

    def test_a_member_unranked_that_year_is_not_counted_for_a_missing_exit(self) -> None:
        """No close at the year-end before means no rank, so its missing exit counts for nothing."""
        closes, _ = synthetic_closes()
        closes.loc["2014-12-31", "S05"] = np.nan
        closes.loc["2016-01-29", "S05"] = np.nan
        counts = seasonals.ranked_without_exit(closes)
        assert counts[7] == 0
        assert sum(counts) == 0

    def test_a_member_that_lists_late_misses_its_early_year_ends(self) -> None:
        closes, _ = synthetic_closes()
        closes.loc[:"2010-06-30", "S09"] = np.nan
        missed = seasonals.year_ends_missed(closes)
        assert list(missed) == ["S09"]
        assert [day.year for day in missed["S09"]] == [2007, 2008, 2009]

    def test_a_member_with_no_close_on_the_filings_date_is_named(self) -> None:
        closes, _ = synthetic_closes()
        closes.loc[:"2026-01-01", "S04"] = np.nan
        closes.loc["2025-12-31", "S11"] = np.nan
        assert seasonals.no_close_at_filing(closes) == ("S04", "S11")

    def test_a_calendar_refusal_on_an_empty_row_names_no_symbol(self) -> None:
        closes, calendar = synthetic_closes()
        closes.loc[pd.Timestamp("2015-12-26")] = np.nan
        closes = closes.sort_index()
        with pytest.raises(seasonals.SurvivorRunRefused, match="a row with no close on 2015-12-26"):
            seasonals.survivor_effect(closes, calendar)

    def test_a_member_ranks_only_from_its_second_year_end(self) -> None:
        closes, calendar = synthetic_closes()
        closes.loc[:"2010-06-30", "S09"] = np.nan
        ranked = [t.ranked for t in seasonals.survivor_effect(closes, calendar).trades]
        assert ranked[:4] == [29, 29, 29, 30]


class TestTheSurvivorReading:
    def test_failing_to_reject_gives_the_owners_wording(self) -> None:
        test = seasonals.OneSided(n=18, mean=0.004, std=0.06, t=0.28, p=0.39)
        assert seasonals.survivor_reading(test, 0.0366) == (
            "no January effect detectable above about 3.7% a January, on members that "
            "favour the effect"
        )

    def test_rejecting_gives_no_verdict(self) -> None:
        test = seasonals.OneSided(n=18, mean=0.04, std=0.06, t=2.83, p=0.006)
        reading = seasonals.survivor_reading(test, 0.0366)
        assert reading.startswith("above zero on survivors, no verdict: a mean of 0.0400")
        assert "t 2.83, p 0.006, over 18 Januaries" in reading
        assert "survivor bias alone could produce it" in reading
        assert "disappeared" not in reading


class TestTheSurvivorRefusalsReachTheOperator:
    @pytest.mark.parametrize(
        "refusal",
        [
            ArchiveUnavailable("no data archive is configured on this machine"),
            ArchiveRefused("sp600/daily_STRA.csv hashes to 00, not ff"),
            seasonals.SurvivorRunRefused("S07 has a row on 2015-12-26"),
        ],
        ids=lambda refusal: type(refusal).__name__,
    )
    def test_each_refusal_is_one_line(self, refusal, monkeypatch, capsys) -> None:
        def refuse(**_kwargs):
            raise refusal

        monkeypatch.setattr(seasonals, "run_survivors", refuse)
        with pytest.raises(SystemExit) as stopped:
            seasonals.main(["--survivors"])
        assert stopped.value.code == str(refusal)
        assert "\n" not in str(stopped.value.code)

    def test_a_machine_with_no_archive_gets_the_readers_line(self, monkeypatch) -> None:
        import chan.archive as archive

        monkeypatch.delenv(archive.ARCHIVE_DIR_ENV, raising=False)
        monkeypatch.setattr(archive, "ARCHIVE_DIR_CONFIG", Path("/nonexistent/archive_dir"))
        with pytest.raises(SystemExit, match="no data archive is configured"):
            seasonals.main(["--survivors"])

    def test_a_bug_is_not_turned_into_a_line(self, monkeypatch) -> None:
        def broken(**_kwargs):
            raise ValueError("a bug")

        monkeypatch.setattr(seasonals, "run_survivors", broken)
        with pytest.raises(ValueError, match="a bug"):
            seasonals.main(["--survivors"])


#: The sha256 of the 603 ``sp600`` lines the survivor run reads, one per member,
#: joined in file order with a newline after each. A change to any of them is a
#: change to which bytes the pins below rest on, so it fails here first, in CI.
#: Lines the cross-section gains for other symbols, such as the past members
#: issue 332 adds, are left out, so they do not move it.
SURVIVOR_LINES_SHA256 = "6fbf738e08fb74ebc51f04af7bf9a285636b366e5691d1530f09e7a563eb8985"

#: Each January's return before costs, entered at the 2008-12-31 year-end to the 2025-12-31 one.
SURVIVOR_BEFORE_COSTS = [
    0.0109878352639423,
    0.03959431018322435,
    0.0437343887556381,
    0.07993112553055388,
    -0.006311308645010345,
    -0.0047755181428521705,
    -0.03448782709144869,
    -0.025391911944576386,
    0.015670478679503344,
    -0.012831740397399177,
    0.06256583296485677,
    -0.04280677611733347,
    -0.02849998631720376,
    0.018737208384723536,
    0.09659059125843618,
    -0.020807370559363342,
    0.001279482522117216,
    0.001457459899829136,
]

#: Ranked, long and short counts for each January, in the same order.
SURVIVOR_COUNTS = [
    (362, 36, 36),
    (370, 37, 37),
    (378, 38, 38),
    (389, 39, 39),
    (400, 40, 40),
    (412, 41, 41),
    (433, 43, 43),
    (459, 46, 46),
    (486, 49, 49),
    (502, 50, 50),
    (522, 52, 52),
    (541, 54, 54),
    (549, 55, 55),
    (559, 56, 56),
    (581, 58, 58),
    (584, 58, 58),
    (592, 59, 59),
    (598, 60, 60),
]


class TestTheSurvivorLines:
    """The members' lines in the ``sp600`` cross-section, committed, so these run everywhere."""

    def test_the_lines_are_the_ones_the_pins_rest_on(self) -> None:
        import hashlib

        from chan.paths import DATA_DIR

        symbols = {symbol for _, symbol in seasonals.survivor_members()}
        text = (DATA_DIR / "archive_vintages.jsonl").read_text(encoding="utf-8")
        lines = [
            line
            for line in text.splitlines()
            if line.strip()
            and json.loads(line).get("cross_section") == "sp600"
            and json.loads(line)["symbol"] in symbols
        ]
        assert len(lines) == 603
        digest = hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()
        assert digest == SURVIVOR_LINES_SHA256

    def test_the_figures_data_readme_quotes_for_the_lines(self) -> None:
        """Rows, span, the 24 that end early and the bytes, from the committed lines."""
        from chan.archive import read_archive_manifest
        from chan.paths import DATA_DIR

        symbols = {symbol for _, symbol in seasonals.survivor_members()}
        lines = [
            e for e in read_archive_manifest() if e.cross_section == "sp600" and e.symbol in symbols
        ]
        assert sum(e.row_count for e in lines) == 2_993_012
        assert min(e.first_date for e in lines) == "1999-11-01"
        assert max(e.last_date for e in lines) == "2026-10-02"
        early = [e.last_date for e in lines if e.last_date < "2026-10-02"]
        assert (len(early), min(early)) == (24, "2026-01-22")
        text = (DATA_DIR / "archive_vintages.jsonl").read_text(encoding="utf-8")
        size = sum(
            len(line.encode("utf-8")) + 1
            for line in text.splitlines()
            if line.strip()
            and json.loads(line).get("cross_section") == "sp600"
            and json.loads(line)["symbol"] in symbols
        )
        assert size == 233_992

    def test_every_member_has_a_line_downloaded_on_2026_10_05(self) -> None:
        from chan.archive import read_archive_manifest

        symbols = {symbol for _, symbol in seasonals.survivor_members()}
        lines = {e.symbol: e for e in read_archive_manifest() if e.cross_section == "sp600"}
        assert symbols <= set(lines)
        assert {lines[symbol].download_date for symbol in symbols} == {"2026-10-05"}


@pytest.fixture(scope="module")
def survivors() -> seasonals.SurvivorRun:
    """One run on the owner's archive, about ten seconds, or a skip naming what is missing."""
    try:
        return seasonals.run_survivors()
    except ArchiveUnavailable as absent:
        pytest.skip(str(absent))


class TestTheSurvivorPins:
    """Example 7.6 on IJR's 603 members at 2025-12-31, survivor-only and exploratory.

    The vintage is three things.

    1. The members, from IJR's Form N-PORT for 2025-12-31, accession
       ``0000940400-26-007526``, through ``chan.fund_holdings``' member rule
       and :data:`chan.equity_seasonals.ALPHAVANTAGE_SYMBOLS`.
    2. Their closes, Alpha Vantage's ``adjusted_close`` from
       ``TIME_SERIES_DAILY_ADJUSTED``, the 603 ``sp600`` lines in
       ``data/archive_vintages.jsonl``, all downloaded 2026-10-05, whose bytes
       :data:`SURVIVOR_LINES_SHA256` holds.
    3. The calendar, ``yfinance_spy_raw_1993-01-29_2026-10-02_dl2026-10-03.csv``.

    The specification is :data:`chan.equity_seasonals.MATLAB_JANUARY`
    unchanged, on rows from 2007-12-01 to 2026-10-02, in one call: January 2009
    to January 2026, 18 Januaries. Returns are read before costs. The test is
    one-sided at 5%, and X is the mean it detects with 80% probability at the
    measured standard deviation. All of it was declared on issue 333 before any
    return was computed. First run on 2026-10-05.

    The figures need the archive, so they skip with the reader's own message
    where none is configured, as ``tests/test_cpo.py``'s do. They take about
    ten seconds, so ``QT_ARCHIVE_RUN`` does not gate them.
    """

    def test_every_member_has_a_series(self, survivors) -> None:
        assert len(survivors.members) == 603
        assert len(survivors.entries) == 603
        assert survivors.missing == ()

    def test_the_calendar_is_the_committed_raw_spy_vintage(self, survivors) -> None:
        assert survivors.calendar.path == "yfinance_spy_raw_1993-01-29_2026-10-02_dl2026-10-03.csv"

    def test_two_members_have_no_close_on_the_filings_own_date(self, survivors) -> None:
        """Alpha Vantage's NVRI and GTES hold nothing before 2026, so neither is ever ranked."""
        assert survivors.no_close == ("GTES", "NVRI")
        assert all(len(survivors.missed[symbol]) == 19 for symbol in survivors.no_close)
        ranked = max(trade.ranked for trade in survivors.effect.trades)
        assert ranked == 598 < 603 - len(survivors.no_close)

    def test_241_members_miss_2139_year_ends(self, survivors) -> None:
        assert len(survivors.missed) == 241
        assert sum(len(days) for days in survivors.missed.values()) == 2139

    def test_the_18_entry_and_exit_days(self, survivors) -> None:
        assert [(str(t.entered.date()), str(t.exited.date())) for t in survivors.effect.trades] == [
            ("2008-12-31", "2009-01-30"),
            ("2009-12-31", "2010-01-29"),
            ("2010-12-31", "2011-01-31"),
            ("2011-12-30", "2012-01-31"),
            ("2012-12-31", "2013-01-31"),
            ("2013-12-31", "2014-01-31"),
            ("2014-12-31", "2015-01-30"),
            ("2015-12-31", "2016-01-29"),
            ("2016-12-30", "2017-01-31"),
            ("2017-12-29", "2018-01-31"),
            ("2018-12-31", "2019-01-31"),
            ("2019-12-31", "2020-01-31"),
            ("2020-12-31", "2021-01-29"),
            ("2021-12-31", "2022-01-31"),
            ("2022-12-30", "2023-01-31"),
            ("2023-12-29", "2024-01-31"),
            ("2024-12-31", "2025-01-31"),
            ("2025-12-31", "2026-01-30"),
        ]

    def test_the_ranked_long_and_short_counts(self, survivors) -> None:
        counts = [(t.ranked, t.longs, t.shorts) for t in survivors.effect.trades]
        assert counts == SURVIVOR_COUNTS

    def test_the_18_returns_before_costs(self, survivors) -> None:
        assert list(survivors.before) == pytest.approx(SURVIVOR_BEFORE_COSTS, abs=1e-9)

    def test_two_ranked_members_have_no_exit_close(self, survivors) -> None:
        """INDV has no row on 2019-01-31, and GES was delisted on 2026-01-22."""
        expected = [0] * 18
        expected[10] = 1
        expected[17] = 1
        assert list(survivors.no_exit) == expected

    def test_the_mean_is_not_detectably_above_zero(self, survivors) -> None:
        test = survivors.test
        assert test.n == 18
        assert_reproduces(test.mean, 0.010813126345979859, "0.0108", ".4f")
        assert_reproduces(test.std, 0.03975601910659598, "0.0398", ".4f")
        assert_reproduces(test.t, 1.153943750439647, "1.15", ".2f")
        assert_reproduces(test.p, 0.13224437054261162, "0.132", ".3f")
        assert not test.rejects

    def test_x_is_2_4_percent_a_january(self, survivors) -> None:
        assert_reproduces(survivors.detectable, 0.02428625598484838, "0.0243", ".4f")
        assert format(survivors.detectable, ".1%") == "2.4%"

    def test_the_mean_after_costs(self, survivors) -> None:
        assert_reproduces(survivors.after_mean, 0.009813126345979858, "0.0098", ".4f")

    def test_the_reading(self, survivors) -> None:
        assert survivors.reading == (
            "no January effect detectable above about 2.4% a January, on members that "
            "favour the effect"
        )

    def test_the_report_prints_the_reading_beside_the_one_way_rule(self, survivors, capsys):
        seasonals.report_survivors(survivors)
        out = capsys.readouterr().out
        assert "survivor-only and exploratory" in out
        assert "accession 0000940400-26-007526" in out
        assert "downloaded 2026-10-05" in out
        assert "members with no series: 0" in out
        assert "no close on 2025-12-31, the filing's own date: 2" in out
        assert "NVRI: its series runs 2026-05-27 to 2026-10-02" in out
        assert (
            "entered 2025-12-31 exited 2026-01-30: 0.0015   (60 long and 60 short of 598 "
            "ranked, 1 ranked with no exit close)"
        ) in out
        assert "mean 0.0108, standard deviation 0.0398, t 1.15, one-sided p 0.132" in out
        assert "closes: 603 series from the sp600 cross-section" in out
        assert "calendar: yfinance_spy_raw_1993-01-29_2026-10-02_dl2026-10-03.csv" in out
        assert "members missing a year-end close: 241" in out
        assert "    GTES: 2007 to 2025" in out
        assert "detectable with 80% probability at 5%: 0.0243 a January" in out
        assert "after costs: mean 0.0098" in out

    def test_the_report_names_a_missing_member_and_counts_series_not_members(
        self, survivors, capsys
    ) -> None:
        """Nothing is missing on the real run, so a copy of it with one member gone is printed."""
        gone = replace(
            survivors,
            entries=tuple(e for e in survivors.entries if e.symbol != "DCH"),
            missing=("AXL as DCH",),
        )
        seasonals.report_survivors(gone)
        out = capsys.readouterr().out
        assert "closes: 602 series" in out
        assert "members with no series: 1\n    AXL as DCH\n" in out
        assert "reading: no January effect detectable above about 2.4% a January" in out
        assert "Read one way only" in out


# --------------------------------------------------------------------------
# Example 7.6 on the S&P 600 as it stood at each year-end, registered
# --------------------------------------------------------------------------


class TestTheUniverseKeyword:
    """The tenth of the whole index, which the point-in-time run passes and every printout omits."""

    def test_the_default_is_the_ranked_count(self, ijr) -> None:
        assert january_effect(ijr, MATLAB_JANUARY, universe=None) == january_effect(
            ijr, MATLAB_JANUARY
        )

    def test_a_larger_universe_takes_a_tenth_of_it(self, ijr) -> None:
        trades = january_effect(ijr, MATLAB_JANUARY, universe=600).trades
        assert [(t.ranked, t.longs, t.shorts) for t in trades] == [
            (578, 60, 60),
            (592, 60, 60),
            (594, 60, 60),
        ]

    def test_the_ranked_count_itself_changes_nothing(self, ijr) -> None:
        """578 is the first January's ranked count, so that January is the printed one."""
        trade = january_effect(ijr.loc[:"2006-02-28"], MATLAB_JANUARY, universe=578).trades[-1]
        assert_reproduces(trade.ret, -0.024368881797563913, "-0.0244", ".4f")

    def test_a_universe_below_the_ranked_count_is_refused_naming_both(self, ijr) -> None:
        with pytest.raises(ValueError, match="a universe of 500 is smaller than the 578 stocks"):
            january_effect(ijr, MATLAB_JANUARY, universe=500)


#: Ten stocks ranked on their annual return, each with a January return.
ANNUAL = np.array([-0.5, -0.4, -0.3, -0.2, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
JANUARY = np.array([0.10, 0.06, 0.03, 0.01, 0.0, -0.01, -0.02, -0.03, -0.05, -0.08])


class TestTheBound:
    """:func:`chan.equity_seasonals.bounded_january` on ten stocks and a tenth of two."""

    def _percentiles(self) -> tuple[float, float]:
        worst, best = np.percentile(JANUARY, [1, 99])
        return float(worst), float(best)

    def test_with_nothing_to_insert_both_are_the_covered_return_before_costs(self) -> None:
        low, high = seasonals.bounded_january(ANNUAL, JANUARY, 2)
        _, _, _, after = seasonals._rank_and_trade(ANNUAL, JANUARY, MATLAB_JANUARY, 20)
        assert low == high == pytest.approx(((0.10 + 0.06) / 2 - (-0.05 - 0.08) / 2) / 2)
        assert low == pytest.approx(after + 2 * seasonals.ONE_WAY_COST, abs=1e-15)

    def test_a_loser_displaces_the_least_extreme_and_takes_each_percentile(self) -> None:
        """The stock ranked second is displaced, and the worst-ranked one stays."""
        worst, best = self._percentiles()
        low, high = seasonals.bounded_january(ANNUAL, JANUARY, 2, long=1)
        winners = (-0.05 - 0.08) / 2
        assert low == pytest.approx(((0.10 + worst) / 2 - winners) / 2)
        assert high == pytest.approx(((0.10 + best) / 2 - winners) / 2)

    def test_a_winner_takes_the_99th_in_the_low_series_because_it_is_held_short(self) -> None:
        worst, best = self._percentiles()
        low, high = seasonals.bounded_january(ANNUAL, JANUARY, 2, short=1)
        losers = (0.10 + 0.06) / 2
        assert low == pytest.approx((losers - (-0.08 + best) / 2) / 2)
        assert high == pytest.approx((losers - (-0.08 + worst) / 2) / 2)

    def test_more_threats_than_places_fill_the_tenth(self) -> None:
        worst, best = self._percentiles()
        low, high = seasonals.bounded_january(ANNUAL, JANUARY, 2, long=5, short=3)
        assert low == pytest.approx((worst - best) / 2)
        assert high == pytest.approx((best - worst) / 2)

    def test_an_unplaced_member_goes_where_it_does_most_harm_to_each_bound(self) -> None:
        worst, best = self._percentiles()
        as_loser = seasonals.bounded_january(ANNUAL, JANUARY, 2, long=1)
        as_winner = seasonals.bounded_january(ANNUAL, JANUARY, 2, short=1)
        low, high = seasonals.bounded_january(ANNUAL, JANUARY, 2, unplaced=1)
        assert low == min(as_loser[0], as_winner[0])
        assert high == max(as_loser[1], as_winner[1])
        assert as_loser[0] != as_winner[0]

    def test_a_january_with_no_exit_close_is_skipped_and_kept_out_of_the_percentiles(self) -> None:
        january = JANUARY.copy()
        january[9] = np.nan
        low, high = seasonals.bounded_january(ANNUAL, january, 2)
        assert low == high == pytest.approx(((0.10 + 0.06) / 2 - (-0.05)) / 2)
        worst, _ = np.percentile(january[:9], [1, 99])
        low, _ = seasonals.bounded_january(ANNUAL, january, 2, long=1)
        assert low == pytest.approx(((0.10 + worst) / 2 - (-0.05)) / 2)


PIT_DATE = "2015-12-31"


def synthetic_year(missing_returns: dict[int, object] | None = None):
    """Twenty covered members and two missing ones at 2015-12-31, on synthetic closes.

    Row 21 is placed far below every covered member, so it threatens the
    losers, and row 22 cannot be placed.
    """
    from decimal import Decimal

    from chan.fund_panel import Coverage, MemberRow

    closes, calendar = synthetic_closes(members=20)
    rows = [
        MemberRow(PIT_DATE, row, f"S{row - 1:02d}", "filing", check="pass", exit="close")
        for row in range(1, 21)
    ] + [MemberRow(PIT_DATE, row, "", "none", check="unmapped") for row in (21, 22)]
    missing = ((PIT_DATE, 21), (PIT_DATE, 22))
    year = Coverage(PIT_DATE, 22, 20, {"unmapped": 2}, 0, missing)
    returns = {(PIT_DATE, row): Decimal(row) for row in range(1, 21)}
    returns.update(
        {(PIT_DATE, 21): Decimal(-100), (PIT_DATE, 22): None}
        if missing_returns is None
        else missing_returns
    )
    return rows, year, closes, calendar, returns


class TestThePointInTimeYear:
    """One year-end of the run on synthetic closes, so its rules hold in CI with no archive."""

    def _run(self, monkeypatch, rows, year, closes, calendar, returns):
        monkeypatch.setattr(seasonals, "year_end_returns", lambda *args: returns)
        return seasonals.point_in_time_year(rows, year, closes, calendar)

    def test_the_tenth_counts_the_missing_members(self, monkeypatch) -> None:
        rows, year, closes, calendar, returns = synthetic_year()
        result = self._run(monkeypatch, rows, year, closes, calendar, returns)
        assert (result.trade.ranked, result.universe) == (20, 22)
        assert (result.trade.longs, result.trade.shorts) == (2, 2)
        assert result.sides == {(PIT_DATE, 21): "long", (PIT_DATE, 22): "unplaced"}
        assert (result.threatening("long"), result.threatening("unplaced")) == (1, 1)
        assert not result.exact
        assert result.low < result.trade.ret + 2 * seasonals.ONE_WAY_COST < result.high

    def test_the_trade_is_the_one_january_of_the_slice(self, monkeypatch) -> None:
        rows, year, closes, calendar, returns = synthetic_year()
        result = self._run(monkeypatch, rows, year, closes, calendar, returns)
        assert result.trade.entered == pd.Timestamp("2015-12-31")
        assert result.trade.exited == pd.Timestamp("2016-01-29")
        sliced = seasonals.year_end_slice(closes, calendar, PIT_DATE)
        assert (sliced.index[0], sliced.index[-1]) == (
            pd.Timestamp("2014-12-01"),
            pd.Timestamp("2016-02-01"),
        )

    def test_a_year_end_with_no_threat_is_exact(self, monkeypatch) -> None:
        from decimal import Decimal

        rows, year, closes, calendar, returns = synthetic_year(
            {(PIT_DATE, 21): Decimal("10.5"), (PIT_DATE, 22): Decimal("11.5")}
        )
        result = self._run(monkeypatch, rows, year, closes, calendar, returns)
        assert result.exact
        assert result.low == result.high
        assert result.low == pytest.approx(result.trade.ret + 2 * seasonals.ONE_WAY_COST)

    def test_only_the_covered_members_are_ranked(self, monkeypatch) -> None:
        """A column the year-end does not cover is in the closes and stays out of the ranking."""
        rows, year, closes, calendar, returns = synthetic_year()
        closes["OUTSIDER"] = closes["S00"] * 2
        result = self._run(monkeypatch, rows, year, closes, calendar, returns)
        assert result.trade.ranked == 20

    def test_a_covered_member_with_no_series_is_refused(self, monkeypatch) -> None:
        rows, year, closes, calendar, returns = synthetic_year()
        with pytest.raises(seasonals.PointInTimeRefused, match="the first S05"):
            self._run(monkeypatch, rows, year, closes.drop(columns="S05"), calendar, returns)

    def test_an_entry_off_the_filings_price_date_is_refused_naming_both(self, monkeypatch) -> None:
        rows, year, closes, calendar, returns = synthetic_year()
        closes = closes.drop(index=pd.Timestamp("2015-12-31"))
        with pytest.raises(
            seasonals.PointInTimeRefused,
            match="2015-12-31: the slice enters 2015-12-30 and exits 2016-01-29, where the "
            "filing's price date is 2015-12-31",
        ):
            self._run(monkeypatch, rows, year, closes, calendar, returns)

    def test_a_stray_row_is_refused(self, monkeypatch) -> None:
        rows, year, closes, calendar, returns = synthetic_year()
        closes.loc[pd.Timestamp("2015-12-26"), "S03"] = 20.0
        closes = closes.sort_index()
        with pytest.raises(seasonals.SurvivorRunRefused, match="S03 has a row on 2015-12-26"):
            self._run(monkeypatch, rows, year, closes, calendar, returns)

    def test_a_rank_row_off_the_last_december_day_is_refused(self, monkeypatch) -> None:
        """No member has a close on 2014-12-31, so the slice would rank against the day before."""
        rows, year, closes, calendar, returns = synthetic_year()
        closes = closes.drop(index=pd.Timestamp("2014-12-31"))
        with pytest.raises(
            seasonals.PointInTimeRefused,
            match="ranks against 2014-12-30, where the calendar's last trading day of "
            "December 2014 is 2014-12-31",
        ):
            self._run(monkeypatch, rows, year, closes, calendar, returns)

    def test_a_slice_yielding_two_trades_is_refused(self, monkeypatch) -> None:
        rows, year, closes, calendar, returns = synthetic_year()
        real = seasonals.january_effect

        def doubled(*args, **kwargs):
            effect = real(*args, **kwargs)
            return replace(effect, trades=effect.trades * 2)

        monkeypatch.setattr(seasonals, "january_effect", doubled)
        with pytest.raises(seasonals.PointInTimeRefused, match="yields 2 trades, not one"):
            self._run(monkeypatch, rows, year, closes, calendar, returns)

    def test_the_bound_disagreeing_with_january_effect_is_refused(self, monkeypatch) -> None:
        """The bound recomputes the returns outside january_effect, so the two are compared."""
        rows, year, closes, calendar, returns = synthetic_year()
        real = seasonals._rank_and_trade

        def shifted(*args):
            ranked, longs, shorts, ret = real(*args)
            return ranked, longs, shorts, ret + 0.01

        monkeypatch.setattr(seasonals, "_rank_and_trade", shifted)
        with pytest.raises(seasonals.PointInTimeRefused, match="where january_effect gives"):
            self._run(monkeypatch, rows, year, closes, calendar, returns)

    def test_a_calendar_short_of_february_is_refused(self, monkeypatch) -> None:
        rows, year, closes, calendar, returns = synthetic_year()
        short = calendar[calendar < pd.Timestamp("2016-02-01")]
        with pytest.raises(seasonals.PointInTimeRefused, match="to February 2016"):
            self._run(monkeypatch, rows, year, closes, short, returns)


def _test(mean: float, t: float, p: float) -> seasonals.OneSided:
    return seasonals.OneSided(n=18, mean=mean, std=0.05, t=t, p=p)


class TestTheVerdict:
    """The three forms issue 329 worded before any return was computed."""

    def test_neither_rejecting_quotes_the_larger_x(self) -> None:
        verdict = seasonals.point_in_time_verdict(
            _test(0.01, 0.8, 0.2), _test(0.02, 1.5, 0.07), 0.031, 0.044
        )
        assert verdict == "no January effect detectable above about 4.4% a January"

    def test_both_rejecting_names_the_effect_with_both_series(self) -> None:
        verdict = seasonals.point_in_time_verdict(
            _test(0.03, 2.5, 0.011), _test(0.05, 3.1, 0.003), 0.03, 0.04
        )
        assert verdict == (
            "a January effect above zero: a mean of 0.0300 to 0.0500 a January, t 2.50 to "
            "3.10, p 0.011 to 0.003, over 18 Januaries"
        )

    def test_equal_series_print_one_figure(self) -> None:
        test = _test(0.03, 2.5, 0.011)
        verdict = seasonals.point_in_time_verdict(test, test, 0.03, 0.03)
        assert "a mean of 0.0300 a January, t 2.50, p 0.011" in verdict

    def test_series_that_disagree_cannot_decide_it(self) -> None:
        verdict = seasonals.point_in_time_verdict(
            _test(-0.1, -5.0, 1.0), _test(0.09, 3.7, 0.001), 0.055, 0.062
        )
        assert verdict.startswith("the free sources cannot decide it")
        assert "next step is buying prices" in verdict


#: The ranked covered members at each year-end, from the archive run below,
#: which :class:`TestThePointInTimePins` holds. Covered less ranked is the
#: members new to a filing whose series has no close at the year-end before.
PIT_RANKED = (
    433,
    425,
    425,
    479,
    456,
    441,
    501,
    534,
    547,
    554,
    554,
    560,
    571,
    582,
    585,
    588,
    588,
    598,
)

#: Per year-end: missing members, then those threatening the losers, the
#: winners, and those that cannot be placed, with the tenth sized on
#: :data:`PIT_RANKED` plus the missing members.
PIT_THREATS = (
    ("2008-12-31", 161, 45, 24, 20),
    ("2009-12-31", 174, 37, 39, 13),
    ("2010-12-31", 175, 38, 43, 16),
    ("2011-12-31", 119, 26, 28, 13),
    ("2012-12-31", 144, 32, 29, 15),
    ("2013-12-31", 158, 37, 35, 15),
    ("2014-12-31", 95, 26, 17, 6),
    ("2015-12-31", 60, 14, 11, 9),
    ("2016-12-31", 50, 15, 8, 7),
    ("2017-12-31", 46, 15, 7, 8),
    ("2018-12-31", 44, 14, 7, 7),
    ("2019-12-31", 40, 8, 6, 8),
    ("2020-12-31", 28, 6, 7, 1),
    ("2021-12-31", 14, 4, 4, 1),
    ("2022-12-30", 11, 4, 2, 1),
    ("2023-12-31", 9, 4, 1, 2),
    ("2024-12-31", 8, 1, 2, 2),
    ("2025-12-31", 2, 0, 1, 0),
)

#: The members file the point-in-time pins were measured on, by sha256, the
#: same file ``tests/test_sp600_panel.py`` pins.
PIT_MEMBERS_SHA256 = "c92cc2512ded3a054c861b48e17572c9ff708a4dcfb548e9e226901c14adda9b"


class TestThePointInTimeFlags:
    """Which missing members threaten a tenth, from committed files alone, so these run in CI."""

    def test_the_members_file_is_the_one_measured(self) -> None:
        import hashlib

        from chan import sp600_panel

        digest = hashlib.sha256(sp600_panel.MEMBERS_PATH.read_bytes()).hexdigest()
        assert digest == PIT_MEMBERS_SHA256

    def test_each_year_ends_flags_by_side(self) -> None:
        from chan import sp600_panel
        from chan.fund_holdings import IJR
        from chan.fund_panel import coverage, threat_sides, year_end_returns

        found = []
        for year, ranked in zip(coverage(IJR, sp600_panel.load()), PIT_RANKED, strict=True):
            returns = year_end_returns(IJR, year.report_date)
            sides = threat_sides(returns, year.missing, ranked + len(year.missing))
            counts = [list(sides.values()).count(side) for side in ("long", "short", "unplaced")]
            found.append((year.report_date, len(year.missing), *counts))
        assert tuple(found) == PIT_THREATS

    def test_no_year_end_is_exact(self) -> None:
        assert all(sum(pin[2:]) > 0 for pin in PIT_THREATS)

    def test_741_member_years_threaten_89_of_them_at_2008(self) -> None:
        """The totals the log quotes, sized on this run's universe rather than on every member."""
        assert sum(sum(pin[2:]) for pin in PIT_THREATS) == 741
        assert PIT_THREATS[0][:2] == ("2008-12-31", 161)
        assert sum(PIT_THREATS[0][2:]) == 89

    def test_1487_of_the_1590_mapped_tickers_have_a_line(self) -> None:
        """The rest have no series at Alpha Vantage, so the run reads 1,487 files."""
        from chan import sp600_panel
        from chan.archive import read_archive_manifest

        mapped = sp600_panel.tickers(sp600_panel.load())
        recorded = {e.symbol for e in read_archive_manifest() if e.cross_section == "sp600"}
        assert len(mapped) == 1590
        assert len(set(mapped) & recorded) == 1487


class TestThePointInTimeCommand:
    @pytest.mark.parametrize(
        "refusal",
        [
            seasonals.PointInTimeRefused("2015-12-31: the slice enters 2015-12-30"),
            seasonals.PanelRefused("the members file names 1 rows the filings do not hold"),
            ArchiveUnavailable("no data archive is configured on this machine"),
        ],
        ids=lambda refusal: type(refusal).__name__,
    )
    def test_each_refusal_is_one_line(self, refusal, monkeypatch) -> None:
        def refuse(**_kwargs):
            raise refusal

        monkeypatch.setattr(seasonals, "run_point_in_time", refuse)
        with pytest.raises(SystemExit) as stopped:
            seasonals.main(["--point-in-time"])
        assert stopped.value.code == str(refusal)

    def test_the_two_archive_runs_are_one_or_the_other(self) -> None:
        with pytest.raises(SystemExit) as stopped:
            seasonals.main(["--survivors", "--point-in-time"])
        assert stopped.value.code == 2


@pytest.fixture(scope="module")
def point_in_time() -> seasonals.PointInTimeRun:
    """One run on the owner's archive, about ten seconds, or a skip naming what is missing."""
    try:
        return seasonals.run_point_in_time()
    except ArchiveUnavailable as absent:
        pytest.skip(str(absent))


#: Each January before costs, the low series then the high.
PIT_LOW = [
    -0.3102916684682715, -0.19839476507411702, -0.192227314302099, -0.10870572849484236,
    -0.15467069691120883, -0.1653363299933961, -0.13112900962243856, -0.09597216550984841,
    -0.08469806698164244, -0.08838588652403147, -0.009638637680710993, -0.12694805604135495,
    -0.18706825793047532, -0.007092727187004211, 0.051120529038608704, -0.049378548477207414,
    -0.024022313935317015, -0.0023087433400641386,
]  # fmt: skip
PIT_HIGH = [
    0.31512341488232387, 0.24494937260065897, 0.1889766558224868, 0.14492043392989745,
    0.1457086223041022, 0.1597979963136514, 0.0686157912693974, 0.06014433261299512,
    0.044717957152853684, 0.06835439802701994, 0.1306503085694603, -0.004070341602840345,
    -0.09002848776268077, 0.03353559694544943, 0.08356653439121693, -0.019616922654241906,
    0.0037277705788413724, 0.0026855572271426084,
]  # fmt: skip


class TestThePointInTimePins:
    """Example 7.6 on the S&P 600 as it stood at each year-end, registered.

    The vintage is three things.

    1. The members, ``research/filings/ijr/members.csv``, whose sha256
       :data:`PIT_MEMBERS_SHA256` holds, read from IJR's year-end filings from
       2007 to 2025.
    2. Their closes, Alpha Vantage's ``adjusted_close`` from
       ``TIME_SERIES_DAILY_ADJUSTED``, the 1,487 ``sp600`` lines in
       ``data/archive_vintages.jsonl`` the members file maps to, all downloaded
       2026-10-05, with the bytes in the owner's archive.
    3. The calendar, ``yfinance_spy_raw_1993-01-29_2026-10-02_dl2026-10-03.csv``.

    The specification is :data:`chan.equity_seasonals.MATLAB_JANUARY`
    unchanged, one year-end at a time on its covered members, with the tenth
    taken of the ranked covered members plus every missing member. January
    2009 to January 2026, 18 Januaries, read before costs. Every year-end has
    a missing member that could change a tenth, so every January is bounded by
    the owner's ruling of 2026-10-04, with the percentiles set per leg as the
    audit on issue 329 wrote before any return was computed. Each series is
    tested one-sided at 5%, and X is the mean it detects with 80% probability.
    Labelled registered: the criterion was written on issue 329 before any
    return was seen. First run on 2026-10-05.

    The read takes about ten seconds, so ``QT_ARCHIVE_RUN`` does not gate
    these, and they skip with the reader's own message where no archive is.
    """

    def test_it_reads_one_download_of_every_mapped_ticker(self, point_in_time) -> None:
        assert len(point_in_time.entries) == 1487
        assert {entry.download_date for entry in point_in_time.entries} == {"2026-10-05"}
        assert point_in_time.calendar.path == (
            "yfinance_spy_raw_1993-01-29_2026-10-02_dl2026-10-03.csv"
        )

    def test_the_18_entry_and_exit_days_are_the_survivor_runs(
        self, point_in_time, survivors
    ) -> None:
        assert [(y.trade.entered, y.trade.exited) for y in point_in_time.year_ends] == [
            (t.entered, t.exited) for t in survivors.effect.trades
        ]

    def test_the_ranked_counts_are_the_ones_the_flags_were_sized_on(self, point_in_time) -> None:
        assert tuple(y.trade.ranked for y in point_in_time.year_ends) == PIT_RANKED

    def test_the_tenths_and_the_threats(self, point_in_time) -> None:
        assert [
            (y.report_date, y.missing, y.threatening("long"), y.threatening("short"),
             y.threatening("unplaced"))
            for y in point_in_time.year_ends
        ] == list(PIT_THREATS)  # fmt: skip
        assert [(y.universe, y.trade.longs, y.trade.shorts) for y in point_in_time.year_ends] == [
            (594, 59, 59), (599, 60, 60), (600, 60, 60), (598, 60, 60), (600, 60, 60),
            (599, 60, 60), (596, 60, 60), (594, 59, 59), (597, 60, 60), (600, 60, 60),
            (598, 60, 60), (600, 60, 60), (599, 60, 60), (596, 60, 60), (596, 60, 60),
            (597, 60, 60), (596, 60, 60), (600, 60, 60),
        ]  # fmt: skip

    def test_every_january_is_bounded(self, point_in_time) -> None:
        assert not any(year.exact for year in point_in_time.year_ends)

    def test_ranked_members_with_no_exit_close(self, point_in_time) -> None:
        assert [year.no_exit for year in point_in_time.year_ends] == [
            0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 2, 4, 1, 1, 0, 3, 2, 1,
        ]  # fmt: skip

    def test_the_18_returns_of_each_series(self, point_in_time) -> None:
        assert [y.low for y in point_in_time.year_ends] == pytest.approx(PIT_LOW, abs=1e-9)
        assert [y.high for y in point_in_time.year_ends] == pytest.approx(PIT_HIGH, abs=1e-9)

    def test_the_low_series_is_not_above_zero(self, point_in_time) -> None:
        test = point_in_time.low
        assert test.n == 18
        assert_reproduces(test.mean, -0.1047304659686345, "-0.1047", ".4f")
        assert_reproduces(test.std, 0.0896119544094856, "0.0896", ".4f")
        assert_reproduces(test.t, -4.958420324916569, "-4.96", ".2f")
        assert_reproduces(test.p, 0.9999402254003401, "1.000", ".3f")
        assert not test.rejects

    def test_the_high_series_is_above_zero(self, point_in_time) -> None:
        test = point_in_time.high
        assert test.n == 18
        assert_reproduces(test.mean, 0.08787549947820747, "0.0879", ".4f")
        assert_reproduces(test.std, 0.10072917438308693, "0.1007", ".4f")
        assert_reproduces(test.t, 3.701253105374127, "3.70", ".2f")
        assert_reproduces(test.p, 0.0008865014467510794, "0.001", ".3f")
        assert test.rejects

    def test_x_for_each_series(self, point_in_time) -> None:
        assert_reproduces(point_in_time.x_low, 0.05474237393477483, "0.0547", ".4f")
        assert_reproduces(point_in_time.x_high, 0.06153368896545796, "0.0615", ".4f")

    def test_the_means_after_costs(self, point_in_time) -> None:
        low, high = point_in_time.after_costs
        assert_reproduces(low, -0.1057304659686345, "-0.1057", ".4f")
        assert_reproduces(high, 0.08687549947820747, "0.0869", ".4f")

    def test_the_verdict_is_that_the_free_sources_cannot_decide_it(self, point_in_time) -> None:
        assert point_in_time.verdict == (
            "the free sources cannot decide it: the low series gives p 1.000 and the high "
            "series p 0.001, so the next step is buying prices for the members that "
            "threaten a tenth"
        )

    def test_the_survivor_run_less_this_one(self, point_in_time, survivors) -> None:
        """Issue 333's rows against these, described rather than tested."""
        per, means = seasonals.survivorship_gap(point_in_time, survivors)
        assert [low for low, _ in per] == pytest.approx(
            [b - y for b, y in zip(SURVIVOR_BEFORE_COSTS, PIT_LOW, strict=True)], abs=1e-9
        )
        assert [high for _, high in per] == pytest.approx(
            [b - y for b, y in zip(SURVIVOR_BEFORE_COSTS, PIT_HIGH, strict=True)], abs=1e-9
        )
        assert_reproduces(means[0], 0.11554359231461436, "0.1155", ".4f")
        assert_reproduces(means[1], -0.07706237313222761, "-0.0771", ".4f")

    def test_the_gap_refuses_runs_on_different_januaries(self, point_in_time, survivors) -> None:
        shifted = replace(point_in_time, year_ends=point_in_time.year_ends[1:])
        with pytest.raises(seasonals.PointInTimeRefused, match="not this run's"):
            seasonals.survivorship_gap(shifted, survivors)

    def test_the_report(self, point_in_time, survivors, capsys) -> None:
        seasonals.report_point_in_time(point_in_time, survivors)
        out = capsys.readouterr().out
        assert "at each year-end, registered" in out
        assert "members: research/filings/ijr/members.csv" in out
        assert "closes: 1487 series from the sp600 cross-section" in out
        assert "downloaded 2026-10-05" in out
        assert (
            "    2008-12-31: entered 2008-12-31 exited 2009-01-30: -0.3103 to 0.3151   "
            "(bounded; 59 long and 59 short of 433 ranked, a tenth of 594; 161 of 600 members "
            "missing, 45 threatening the losers, 24 the winners, 20 unplaced; 0 ranked with no "
            "exit close)"
        ) in out
        assert "the low series: mean -0.1047, standard deviation 0.0896, t -4.96" in out
        assert "the high series: mean 0.0879, standard deviation 0.1007, t 3.70" in out
        assert "verdict: the free sources cannot decide it" in out
        assert "    2009 January: 0.3213 and -0.3041" in out
        assert "    the mean: 0.1155 and -0.0771" in out
