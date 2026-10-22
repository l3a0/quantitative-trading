"""The pins for Khandani and Lo's reversal on Chan's S&P 600 file, beside his S&P 500 file.

This file is the single authority for every number a prose surface quotes
about the comparison. ``docs/replication-log.md`` Entry 44 reports it and
points here row by row. The S&P 500 figures it reads against are pinned in
``tests/test_khandani_lo.py``, and ``TestTheLargeCapSide`` holds that this
module's runs land on those same pins rather than retyping them as new ones.

Every pin on the committed files reads two vintages and one specification, so
all three are stated once here.

- **The S&P 600 vintage.** ``ijr_20080114/``, the 600 stocks lifted from
  Chan's ``IJR_20080114.mat``, saved 2008-01-15, read for the close and the
  open through ``chan.series.load_panel``. Its identity is that file's row of
  ``LIFTED_SOURCES`` in ``tests/support/committed_vintages.py``. The stocks are
  the S&P 600 as it stood on 2008-01-14, so every figure is about survivors.
- **The S&P 500 vintage.** ``spx_20071123/``, the 500 stocks of Chan's
  ``SPX_20071123.mat``, the index as it stood on 2007-11-23.
- **The specification.** Rule B, ``chan.khandani_lo.reversal`` unchanged,
  which is Example 3.7's ``example3_7.m`` on the closes and Example 3.8's rule
  B on the opens. The run computes returns, weights and profit on the whole
  file and cuts them to 2006-01-03 to 2006-12-29, 251 trading days in both
  files. The cost is 5 basis points on each side of a change in weight, and the Sharpe ratio
  is ``√252 · mean / std`` with no risk-free rate.

Each run gives the three figures ``chan.khandani_lo.Reversal`` carries.

1. **Before costs**, Chan's ``sharpe``.
2. **After costs with both quirks kept**, Chan's ``sharpeminustcost``, the
   first day uncharged and its NaN counted as 0 in the deviation.
3. **After costs with the first day charged**, so nothing is NaN.

Every figure is pinned at four decimals, at ``abs=5e-5``, which is what lets
the log quote it at four. A gap is the S&P 600's figure less the S&P 500's,
rounded from the full values. The standard errors and correlations are
Memmel's (2003) test on the two before-cost daily series, as
``chan.khandani_lo_small_caps.sharpe_gap`` computes it, and they rest on its
assumption that the daily profits are independent and normal.

The reading was declared on issue 249 before any S&P 600 figure was computed,
and the two flagged days were classified there before the run. Khandani and
Lo's 4.47 is printed by the report and judged against nothing, so it is cited
here as unpinned.

EXPLORATORY. The run varies a published rule on data Chan left as an
exercise, so it says which way the gap points and how it compares with one
year's noise, and no figure carries a verdict. It first ran on 2026-10-10.
"""

from __future__ import annotations

import math
import re
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from chan import khandani_lo, paths
from chan.khandani_lo import (
    BOOK_KHANDANI_LO,
    ONE_WAY_COST,
    TRADING_DAYS,
    chan_sharpe,
    daily_book,
    daily_returns,
    plain_sharpe,
    reversal_weights,
)
from chan.khandani_lo_small_caps import (
    KEPT_FLAGGED_DAYS,
    LARGE_CAP_FILE,
    MIXED,
    NOISE_MULTIPLE,
    POINTING_AGAINST,
    POINTING_CHANS_WAY,
    SOURCE_FILE,
    SPLICED_SYMBOL,
    Comparison,
    SharpeGap,
    compare,
    comparison,
    direction,
    main,
    memmel_variance,
    points_chans_way,
    report,
    run,
    same_days,
    sharpe_gap,
)
from chan.series import (
    SCALE_BREAK_BOUND,
    WindowCrossesScaleBreak,
    load_panel,
    refuse_window_crossing_a_break,
    scale_breaks,
)
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import LIFTED_SOURCES
from tests.test_scale_breaks import FLAGGED_IN_CHANS_MAT_FILES

START, END = pd.Timestamp("2006-01-03"), pd.Timestamp("2006-12-29")

# --- the committed files -------------------------------------------------------


@pytest.fixture(scope="module")
def small_closes():
    return load_panel(SOURCE_FILE)


@pytest.fixture(scope="module")
def small_opens():
    return load_panel(SOURCE_FILE, field="Open")


@pytest.fixture(scope="module")
def large_closes():
    return load_panel(LARGE_CAP_FILE)


@pytest.fixture(scope="module")
def large_opens():
    return load_panel(LARGE_CAP_FILE, field="Open")


@pytest.fixture(scope="module")
def result(small_closes, small_opens, large_closes, large_opens) -> Comparison:
    return comparison(small_closes[1], small_opens[1], large_closes[1], large_opens[1])


@pytest.fixture
def no_arguments(monkeypatch):
    """``main`` parses ``sys.argv``, which under pytest holds pytest's own arguments."""
    monkeypatch.setattr("sys.argv", ["chan.khandani_lo_small_caps"])


class TestTheVintage:
    def test_the_members_are_the_pinned_source(self, small_closes) -> None:
        members, frame = small_closes
        vendor, basis, saved, folder, count = LIFTED_SOURCES[SOURCE_FILE]
        assert {(m.vendor, m.price_basis, m.obtained) for m in members} == {(vendor, basis, saved)}
        assert {m.path.split("/")[0] for m in members} == {folder} == {"ijr_20080114"}
        assert len(members) == count == frame.shape[1] == 600

    def test_the_large_cap_file_is_example_37s(self) -> None:
        assert LARGE_CAP_FILE == khandani_lo.SOURCE_FILE == "SPX_20071123.mat"

    def test_the_two_files_share_no_symbol(self, small_closes, large_closes) -> None:
        assert set(small_closes[1].columns).isdisjoint(large_closes[1].columns)

    def test_how_many_stocks_are_priced_at_each_end(self, small_closes) -> None:
        """592 on the first day and 594 on the last, because the file is survivors."""
        _, frame = small_closes
        assert frame.loc[START].notna().sum() == 592
        assert frame.loc[END].notna().sum() == 594


class TestTheCalendars:
    """The gap pairs the two files' daily profits by day, so their windows must match."""

    def test_both_windows_hold_the_same_251_days(self, result: Comparison) -> None:
        for small, large in (
            (result.small_closes, result.large_closes),
            (result.small_opens, result.large_opens),
        ):
            assert small.days.equals(large.days)
            assert len(small.days) == 251
            assert (small.days[0], small.days[-1]) == (START, END)

    def test_the_closes_and_opens_hold_the_same_days(self, result: Comparison) -> None:
        assert result.small_closes.days.equals(result.small_opens.days)

    @pytest.mark.parametrize("price", ["closes", "opens"])
    def test_a_window_missing_one_day_is_refused(
        self, small_closes, small_opens, large_closes, large_opens, price
    ) -> None:
        """One 2006 day dropped from the S&P 600 frame of either price stops the pairing."""
        frames = {
            "small_closes": small_closes[1],
            "small_opens": small_opens[1],
            "large_closes": large_closes[1],
            "large_opens": large_opens[1],
        }
        key = f"small_{price}"
        frames[key] = frames[key].drop(index=pd.Timestamp("2006-06-01"))
        with pytest.raises(ValueError, match="250 against 251"):
            comparison(**frames)

    def test_the_same_count_of_different_days_is_refused(
        self, small_closes, small_opens, large_closes, large_opens
    ) -> None:
        """Each side drops a different day, so both hold 250 days and the first to differ is named.

        The S&P 600 drops 2006-06-01 and the S&P 500 drops 2006-06-02, so at
        that position the S&P 600 holds 2006-06-02 and the S&P 500 holds
        2006-06-01.
        """
        with pytest.raises(ValueError, match="first differing at 2006-06-02 against 2006-06-01"):
            comparison(
                small_closes[1].drop(index=pd.Timestamp("2006-06-01")),
                small_opens[1],
                large_closes[1].drop(index=pd.Timestamp("2006-06-02")),
                large_opens[1],
            )

    def test_same_days_passes_two_runs_on_one_calendar(self, result: Comparison) -> None:
        same_days(result.small_closes, result.large_closes)
        same_days(result.small_opens, result.large_opens)


class TestCompareReadsTheCommittedFiles:
    def test_it_gives_the_figures_comparison_gives(self, result: Comparison) -> None:
        again = compare()
        for name in ("small_closes", "small_opens", "large_closes", "large_opens"):
            for field in ("before_costs", "after_costs", "after_costs_charged"):
                assert getattr(getattr(again, name), field) == getattr(getattr(result, name), field)
        assert (again.closes_gap, again.opens_gap) == (result.closes_gap, result.opens_gap)

    def test_it_reads_the_directory_it_is_given(self, tmp_path) -> None:
        with pytest.raises(VintageUnavailable, match="IJR_20080114.mat cannot be"):
            compare(tmp_path)


class TestTheSmallCapFigures:
    """Rule B on ``IJR_20080114.mat``, 2006-01-03 to 2006-12-29, 5 bp a side."""

    def test_closes(self, result: Comparison) -> None:
        r = result.small_closes
        assert r.before_costs == pytest.approx(3.4086, abs=5e-5)
        assert r.after_costs == pytest.approx(-0.3702, abs=5e-5)
        assert r.after_costs_charged == pytest.approx(-0.3255, abs=5e-5)

    def test_opens(self, result: Comparison) -> None:
        r = result.small_opens
        assert r.before_costs == pytest.approx(5.3052, abs=5e-5)
        assert r.after_costs == pytest.approx(2.0147, abs=5e-5)
        assert r.after_costs_charged == pytest.approx(2.0257, abs=5e-5)

    def test_no_day_of_profit_before_costs_is_nan(self, result: Comparison) -> None:
        for r in (result.small_closes, result.small_opens):
            assert np.isfinite(r.pnl).all()


class TestTheLargeCapSide:
    """This module's S&P 500 runs land on the pins ``tests/test_khandani_lo.py`` holds."""

    def test_closes_are_entry_8s(self, result: Comparison) -> None:
        r = result.large_closes
        assert r.before_costs == pytest.approx(0.2510, abs=5e-5)
        assert r.after_costs == pytest.approx(-3.1884, abs=5e-5)
        assert r.after_costs_charged == pytest.approx(-3.2337, abs=5e-5)

    def test_opens_are_entry_10s_rule_b(self, result: Comparison) -> None:
        r = result.large_opens
        assert r.before_costs == pytest.approx(4.4202, abs=5e-5)
        assert r.after_costs == pytest.approx(0.7834, abs=5e-5)
        assert r.after_costs_charged == pytest.approx(0.8293, abs=5e-5)


class TestTheSixGaps:
    """The S&P 600's figure less the S&P 500's, same price, same specification."""

    @pytest.mark.parametrize(
        ("price", "field", "gap"),
        [
            ("closes", "before_costs", 3.1576),
            ("closes", "after_costs", 2.8181),
            ("closes", "after_costs_charged", 2.9081),
            ("opens", "before_costs", 0.8850),
            ("opens", "after_costs", 1.2313),
            ("opens", "after_costs_charged", 1.1964),
        ],
    )
    def test_the_gap(self, result: Comparison, price, field, gap) -> None:
        small = getattr(result, f"small_{price}")
        large = getattr(result, f"large_{price}")
        assert getattr(small, field) - getattr(large, field) == pytest.approx(gap, abs=5e-5)

    def test_the_sharpe_gaps_carry_the_before_cost_gaps(self, result: Comparison) -> None:
        assert result.closes_gap.gap == pytest.approx(3.1576, abs=5e-5)
        assert result.opens_gap.gap == pytest.approx(0.8850, abs=5e-5)


class TestTheSizeReading:
    """Memmel's standard error on each before-cost pair, both 251-day series."""

    def test_closes(self, result: Comparison) -> None:
        g = result.closes_gap
        assert g.days == 251
        assert g.standard_error == pytest.approx(0.9872, abs=5e-5)
        assert g.correlation == pytest.approx(0.5258, abs=5e-5)
        assert g.z == pytest.approx(3.1987, abs=5e-5)
        assert g.beyond_noise

    def test_opens(self, result: Comparison) -> None:
        g = result.opens_gap
        assert g.days == 251
        assert g.standard_error == pytest.approx(1.1640, abs=5e-5)
        assert g.correlation == pytest.approx(0.3663, abs=5e-5)
        assert g.z == pytest.approx(0.7603, abs=5e-5)
        assert not g.beyond_noise

    def test_the_gaps_ratios_are_the_runs_own_figures_exactly(self, result: Comparison) -> None:
        """``chan_sharpe`` and ``plain_sharpe`` agree to the bit on a series with no NaN.

        So the ratios the size reading compares are exactly the before-cost
        figures pinned above, rather than a second computation near them.
        """
        for gap, small, large in (
            (result.closes_gap, result.small_closes, result.large_closes),
            (result.opens_gap, result.small_opens, result.large_opens),
        ):
            assert gap.a_sharpe == small.before_costs == chan_sharpe(small.pnl)
            assert gap.b_sharpe == large.before_costs == chan_sharpe(large.pnl)
            assert chan_sharpe(small.pnl) == plain_sharpe(small.pnl)

    def test_the_gap_runs_small_caps_less_large_caps(self, result: Comparison) -> None:
        g = result.closes_gap
        assert g.gap == g.a_sharpe - g.b_sharpe > 0
        assert g.a_sharpe == result.small_closes.before_costs


class TestTheReading:
    def test_it_points_the_way_chan_says(self, result: Comparison) -> None:
        """The S&P 600 is higher before costs at both prices, declared before any figure."""
        assert result.reading == POINTING_CHANS_WAY == "pointing the way Chan says"

    def test_the_declarations_three_words(self) -> None:
        assert (POINTING_CHANS_WAY, MIXED, POINTING_AGAINST) == (
            "pointing the way Chan says",
            "mixed",
            "pointing against it",
        )

    def test_khandani_and_los_figure_is_cited_and_not_computed(self) -> None:
        assert BOOK_KHANDANI_LO == 4.47


# --- the two flagged days, PMC and the guard ----------------------------------------


class TestTheFlaggedDaysAreKept:
    """BCSI's 2006-02-06 and SCUR's 2006-07-12 were classified as real moves, so both stay in."""

    def test_the_kept_days(self) -> None:
        assert KEPT_FLAGGED_DAYS == {"BCSI": "2006-02-06", "SCUR": "2006-07-12"}

    @pytest.mark.parametrize(
        ("symbol", "day", "before", "after", "ratio"),
        [
            ("BCSI", "2006-02-06", 20.165, 12.37, 0.6134),
            ("SCUR", "2006-07-12", 8.07, 4.99, 0.6183),
        ],
    )
    def test_each_close_return_is_finite_and_weighted_into_the_next_day(
        self, small_closes, symbol, day, before, after, ratio
    ) -> None:
        _, frame = small_closes
        prices = frame.to_numpy(dtype=float)
        column = frame.columns.get_loc(symbol)
        row = frame.index.get_loc(pd.Timestamp(day))
        assert (prices[row - 1, column], prices[row, column]) == (before, after)
        assert after / before == pytest.approx(ratio, abs=5e-5)
        ret = daily_returns(prices)[row, column]
        assert np.isfinite(ret)
        assert ret == pytest.approx(after / before - 1)
        weight = reversal_weights(prices)[row, column]
        assert np.isfinite(weight) and weight > 0
        # The day's weight earns the next day's return, which is finite too.
        assert np.isfinite(daily_returns(prices)[row + 1, column])


class TestTheMissingPrices:
    def test_eight_stocks_miss_a_price_in_2006(self, small_closes) -> None:
        _, frame = small_closes
        window = frame.loc[START:END]
        assert sorted(window.columns[window.isna().any()]) == [
            "CENTA",
            "CROX",
            "FOR",
            "GFG",
            "PCX",
            "PMC",
            "TRX.B",
            "ZEP",
        ]
        assert sorted(window.columns[window.isna().all()]) == [
            "CENTA",
            "FOR",
            "GFG",
            "PCX",
            "PMC",
            "ZEP",
        ]

    def test_two_start_trading_during_the_year_and_have_no_later_gap(self, small_closes) -> None:
        _, frame = small_closes
        window = frame.loc[START:END]
        assert window["CROX"].first_valid_index() == pd.Timestamp("2006-02-08")
        assert window["TRX.B"].first_valid_index() == pd.Timestamp("2006-03-31")
        for symbol in ("CROX", "TRX.B"):
            assert window[symbol].loc[window[symbol].first_valid_index() :].notna().all()

    def test_pmc_carries_zero_weight_on_every_day_of_2006(self, small_closes) -> None:
        _, frame = small_closes
        assert SPLICED_SYMBOL == "PMC"
        prices = frame.to_numpy(dtype=float)
        inside = (frame.index >= START) & (frame.index <= END)
        column = frame.columns.get_loc(SPLICED_SYMBOL)
        assert (reversal_weights(prices)[inside, column] == 0.0).all()
        assert frame.loc[START:END, SPLICED_SYMBOL].isna().all()


class TestTheScaleBreakDecision:
    """Why the module does not call the guard, run rather than asserted.

    Over each member's own closes the guard refuses the window on exactly the
    two days the classification kept, and over each member's own opens it
    passes. Handed the panel's columns it also refuses on the eight stocks with
    a missing price in 2006, which rule B weights at 0. The comment block above
    ``FLAGGED_IN_CHANS_MAT_FILES`` in ``tests/test_scale_breaks.py`` records the
    decision.
    """

    def test_over_each_members_own_closes_it_refuses_on_bcsi_and_scur(self, small_closes) -> None:
        members, frame = small_closes
        legs = [(m, frame[m.symbol].dropna()) for m in members]
        with pytest.raises(WindowCrossesScaleBreak) as refused:
            refuse_window_crossing_a_break(legs, start=START, end=END)
        said = str(refused.value)
        assert said.count("changes scale") == 2
        assert "ijr_20080114/bcsi.csv changes scale on 2006-02-06" in said
        assert "ijr_20080114/scur.csv changes scale on 2006-07-12" in said
        assert "has no readable" not in said

    def test_the_two_days_are_the_pinned_flags_inside_the_window(self, small_closes) -> None:
        members, frame = small_closes
        legs = [(m, frame[m.symbol].dropna()) for m in members]
        with pytest.raises(WindowCrossesScaleBreak) as refused:
            refuse_window_crossing_a_break(legs, start=START, end=END)
        named = set(re.findall(r"ijr_20080114/[a-z.]+\.csv", str(refused.value)))
        pinned = {
            path
            for path, days in FLAGGED_IN_CHANS_MAT_FILES.items()
            if path.startswith("ijr_20080114/") and any(day.startswith("2006") for day in days)
        }
        assert named == pinned
        assert {
            s.upper() for s in re.findall(r"ijr_20080114/([a-z.]+)\.csv", str(refused.value))
        } == set(KEPT_FLAGGED_DAYS)

    def test_over_each_members_own_opens_it_passes(self, small_opens) -> None:
        members, frame = small_opens
        refuse_window_crossing_a_break(
            [(m, frame[m.symbol].dropna()) for m in members], start=START, end=END
        )

    def test_scale_breaks_flags_only_the_kept_days_on_the_closes(self, small_closes) -> None:
        _, frame = small_closes
        cut = frame.loc[START:END]
        flagged = {s: [str(d.date()) for d in scale_breaks(cut[s].dropna())] for s in cut.columns}
        assert {s: days[0] for s, days in flagged.items() if days} == KEPT_FLAGGED_DAYS

    @pytest.mark.parametrize("field", ["Close", "Open"])
    def test_handed_the_panels_columns_it_cannot_read_eight_stocks(
        self, small_closes, small_opens, field
    ) -> None:
        members, frame = small_closes if field == "Close" else small_opens
        with pytest.raises(WindowCrossesScaleBreak) as refused:
            refuse_window_crossing_a_break(
                [(m, frame[m.symbol]) for m in members], start=START, end=END
            )
        assert str(refused.value).count("has no readable day-over-day move") == 8


# --- Memmel's test, worked by hand -----------------------------------------------------
#
# a = 0, 2, 0, 2 and b = 1, 1, 1, 3, four days.
#
#   a: mean 1, deviations −1, 1, −1, 1, variance 4/3 over n − 1, sd 2/√3, s_a = √3/2
#   b: mean 1.5, deviations −½, −½, −½, 3/2, variance 1, sd 1, s_b = 3/2
#   covariance (½ − ½ + ½ + 3/2) / 3 = 2/3, so ρ = (2/3) / (2/√3) = 1/√3, ρ² = 1/3
#   2 s_a s_b ρ² = 2 · (3√3/4) · (1/3) = √3/2
#   Var = (1/4) · [2(1 − 1/√3) + ½(3/4 + 9/4 − √3/2)]
#       = (1/4) · [2 − 2/√3 + 3/2 − √3/4] ≈ 0.478072
#   annualised: gap = √252 · (√3/2 − 3/2) ≈ −10.0640, SE = √(252 · Var) ≈ 10.9761

HAND_A = np.array([0.0, 2.0, 0.0, 2.0])
HAND_B = np.array([1.0, 1.0, 1.0, 3.0])
ROOT3 = math.sqrt(3)
HAND_VARIANCE = (2 - 2 / ROOT3 + 1.5 - ROOT3 / 4) / 4


class TestSharpeGapByHand:
    def test_the_worked_example(self) -> None:
        g = sharpe_gap(HAND_A, HAND_B)
        assert g.days == 4
        assert g.correlation == pytest.approx(1 / ROOT3, rel=1e-12)
        assert g.a_sharpe == pytest.approx(math.sqrt(252) * ROOT3 / 2, rel=1e-12)
        assert g.b_sharpe == pytest.approx(math.sqrt(252) * 1.5, rel=1e-12)
        assert g.gap == pytest.approx(math.sqrt(252) * (ROOT3 / 2 - 1.5), rel=1e-12)
        assert g.standard_error == pytest.approx(math.sqrt(252 * HAND_VARIANCE), rel=1e-12)
        assert HAND_VARIANCE == pytest.approx(0.478072, abs=5e-7)
        assert g.gap == pytest.approx(-10.0640, abs=5e-5)
        assert g.standard_error == pytest.approx(10.9761, abs=5e-5)
        assert g.z == pytest.approx(g.gap / g.standard_error)
        assert not g.beyond_noise

    def test_memmel_variance_is_the_worked_example(self) -> None:
        """The formula on its own, at the hand example's daily ratios and correlation."""
        assert memmel_variance(ROOT3 / 2, 1.5, 1 / ROOT3, 4) == pytest.approx(
            HAND_VARIANCE, rel=1e-12
        )
        assert memmel_variance(0.0, 0.0, 0.0, 4) == 2 / 4
        assert memmel_variance(0.3, 0.3, 1.0, 10) == pytest.approx(0.0, abs=1e-15)

    def test_swapping_the_series_flips_the_gap_and_keeps_the_error(self) -> None:
        ab, ba = sharpe_gap(HAND_A, HAND_B), sharpe_gap(HAND_B, HAND_A)
        assert ba.gap == pytest.approx(-ab.gap, rel=1e-12)
        assert ba.standard_error == pytest.approx(ab.standard_error, rel=1e-12)
        assert ba.correlation == pytest.approx(ab.correlation, rel=1e-12)
        assert (ba.a_sharpe, ba.b_sharpe) == (ab.b_sharpe, ab.a_sharpe)

    def test_one_series_against_itself_has_no_gap_and_no_error(self) -> None:
        g = sharpe_gap(HAND_B, HAND_B.copy())
        assert g.gap == 0.0
        assert g.standard_error == pytest.approx(0.0, abs=1e-6)
        assert g.correlation == pytest.approx(1.0)
        assert not g.beyond_noise

    def test_scaling_a_book_moves_nothing(self) -> None:
        """A Sharpe ratio is unchanged by scaling, so the books need no matching."""
        plain, scaled = sharpe_gap(HAND_A, HAND_B), sharpe_gap(HAND_A * 7.5, HAND_B / 3)
        assert scaled.gap == pytest.approx(plain.gap, rel=1e-12)
        assert scaled.standard_error == pytest.approx(plain.standard_error, rel=1e-12)

    def test_uncorrelated_series_of_zero_mean_give_the_textbook_two_over_t(self) -> None:
        """With s_a = s_b = 0 and ρ = 0 the variance is 2 / T."""
        a = np.array([1.0, -1.0, 1.0, -1.0])
        b = np.array([1.0, 1.0, -1.0, -1.0])
        g = sharpe_gap(a, b)
        assert g.correlation == pytest.approx(0.0, abs=1e-15)
        assert g.standard_error == pytest.approx(math.sqrt(252 * 2 / 4), rel=1e-12)

    @pytest.mark.parametrize(
        ("a", "b", "said"),
        [
            (
                np.array([1.0, np.nan, 2.0, 3.0]),
                HAND_B,
                "sharpe_gap takes two series with every day finite",
            ),
            (
                HAND_A,
                np.array([1.0, 2.0, np.inf, 3.0]),
                "sharpe_gap takes two series with every day finite",
            ),
            (HAND_A, HAND_B[:3], "pairs two series day by day"),
            (HAND_A.reshape(2, 2), HAND_B.reshape(2, 2), "pairs two series day by day"),
            (HAND_A[:2], HAND_B[:2], "at least 3 days"),
            (np.zeros(4), HAND_B, "two series that vary"),
            (HAND_A, np.full(4, 0.01), "two series that vary"),
        ],
    )
    def test_it_refuses_what_it_cannot_pair(self, a, b, said) -> None:
        with pytest.raises(ValueError, match=said):
            sharpe_gap(a, b)

    def test_a_constant_series_is_refused_rather_than_read_as_beyond_noise(self) -> None:
        """Before the refusal, rounding gave this pair a standard error near 1.9e16.

        ``np.full(10, 0.01)`` has a deviation of about 1.8e-18 from rounding
        alone and a range of exactly 0, so the range is what the refusal reads.
        """
        constant = np.full(10, 0.01)
        assert np.ptp(constant) == 0
        with pytest.raises(ValueError, match="two series that vary"):
            sharpe_gap(constant, np.random.default_rng(0).standard_normal(10))

    def test_three_days_are_enough(self) -> None:
        g = sharpe_gap(HAND_A[1:], HAND_B[1:])
        assert g.days == 3
        assert np.isfinite(g.standard_error)

    def test_a_negative_correlation_keeps_its_sign(self) -> None:
        a, b = np.array([1.0, 2.0, 3.0, 4.0]), np.array([4.0, 3.5, 2.0, 1.0])
        g = sharpe_gap(a, b)
        assert g.correlation < 0
        assert g.correlation == pytest.approx(np.corrcoef(a, b)[0, 1], rel=1e-12)


class TestTheNoiseLine:
    """More than twice the standard error, strictly, in either direction."""

    @staticmethod
    def gap(value: float, error: float = 1.0) -> SharpeGap:
        return SharpeGap(
            a_sharpe=value, b_sharpe=0.0, gap=value, correlation=0.0, standard_error=error, days=4
        )

    def test_the_multiple_is_the_declarations(self) -> None:
        assert NOISE_MULTIPLE == 2.0

    @pytest.mark.parametrize(
        ("value", "beyond"),
        [(2.0, False), (2.001, True), (-2.001, True), (-1.999, False), (0.0, False)],
    )
    def test_where_the_line_sits(self, value, beyond) -> None:
        assert self.gap(value).beyond_noise is beyond

    def test_z_is_the_gap_in_standard_errors(self) -> None:
        assert self.gap(3.0, 1.5).z == 2.0
        assert math.isnan(self.gap(0.0, 0.0).z)
        assert self.gap(1.0, 0.0).z == math.inf
        assert self.gap(-1.0, 0.0).z == -math.inf


class TestTheOrderReading:
    @pytest.mark.parametrize(
        ("figures", "holds"),
        [
            ((0.25, 3.41), True),
            ((3.41, 0.25), False),
            ((1.0, 1.0), False),
            ((0.25, 1.0, 3.41), True),
            ((0.25, 3.41, 1.0), False),
            ((1.0, 0.25, 3.41), False),
            ((0.25, 1.0, 1.0), False),
        ],
    )
    def test_figures_must_rise_strictly_as_capitalisation_falls(self, figures, holds) -> None:
        assert points_chans_way(figures) is holds

    def test_one_universe_is_not_an_order(self) -> None:
        with pytest.raises(ValueError, match="at least two universes"):
            points_chans_way([1.0])

    @pytest.mark.parametrize(
        "figures", [(math.nan, 1.0), (0.25, math.nan), (0.25, math.inf, 3.41), (-math.inf, 1.0)]
    )
    def test_a_figure_that_is_not_finite_is_refused(self, figures) -> None:
        """A NaN fails every comparison, so it would read as an order that fails."""
        with pytest.raises(ValueError, match="reads finite figures"):
            points_chans_way(figures)

    @pytest.mark.parametrize(
        ("closes", "opens", "word"),
        [
            ((0.25, 3.41), (4.42, 5.31), POINTING_CHANS_WAY),
            ((0.25, 3.41), (5.31, 4.42), MIXED),
            ((3.41, 0.25), (4.42, 5.31), MIXED),
            ((3.41, 0.25), (5.31, 4.42), POINTING_AGAINST),
        ],
    )
    def test_both_prices_read_together(self, closes, opens, word) -> None:
        assert direction(closes, opens) == word

    @pytest.mark.parametrize(
        ("closes", "opens", "price"),
        [
            ((0.25, 4.0, 3.41), (4.42, 5.5, 5.31), "closes"),
            ((0.25, 3.41), (4.42, 5.0, 5.31), "opens"),
            ((0.25,), (4.42, 5.31), "closes"),
        ],
    )
    def test_anything_but_two_universes_a_price_is_refused(self, closes, opens, price) -> None:
        """The declaration defined its words for two universes, and issue 303 declares its own.

        The first row is the review's case. With closes of 0.25, 4.0 and 3.41
        and opens of 4.42, 5.5 and 5.31, the S&P 600 is above the S&P 500 at
        both prices, and reading three universes as an order called it against.
        """
        with pytest.raises(ValueError, match=f"two universes at each price, and the {price}"):
            direction(closes, opens)


class TestTheComparisonsReading:
    """``Comparison.reading`` reads both prices, before costs only, on stand-in runs."""

    @staticmethod
    def comparison_of(small_closes, large_closes, small_opens, large_opens) -> Comparison:
        """Each argument is one run's figure before costs and its figure after costs."""

        def stand_in(figures):
            before, after = figures
            return SimpleNamespace(
                before_costs=before, after_costs=after, after_costs_charged=after
            )

        return Comparison(
            small_closes=stand_in(small_closes),
            small_opens=stand_in(small_opens),
            large_closes=stand_in(large_closes),
            large_opens=stand_in(large_opens),
            closes_gap=None,
            opens_gap=None,
        )

    def test_it_reads_before_costs_where_after_costs_disagree(self) -> None:
        ahead_before_behind_after = self.comparison_of(
            (2.0, -1.0), (1.0, 0.0), (2.0, -1.0), (1.0, 0.0)
        )
        assert ahead_before_behind_after.reading == POINTING_CHANS_WAY
        behind_before_ahead_after = self.comparison_of(
            (1.0, 2.0), (2.0, 1.0), (1.0, 2.0), (2.0, 1.0)
        )
        assert behind_before_ahead_after.reading == POINTING_AGAINST

    @pytest.mark.parametrize(
        ("closes_ahead", "opens_ahead", "word"),
        [(True, False, MIXED), (False, True, MIXED), (True, True, POINTING_CHANS_WAY)],
    )
    def test_it_reads_each_price_from_its_own_runs(self, closes_ahead, opens_ahead, word) -> None:
        def pair(ahead):
            return ((2.0, 0.0), (1.0, 0.0)) if ahead else ((1.0, 0.0), (2.0, 0.0))

        small_closes, large_closes = pair(closes_ahead)
        small_opens, large_opens = pair(opens_ahead)
        c = self.comparison_of(small_closes, large_closes, small_opens, large_opens)
        assert c.reading == word


# --- the report -------------------------------------------------------------------------


class TestTheReport:
    def test_it_prints_the_six_pairs_the_errors_and_the_reading(self, capsys, no_arguments) -> None:
        main()
        out = capsys.readouterr().out
        assert "600 members lifted from IJR_20080114.mat" in out
        assert "500 members lifted from SPX_20071123.mat" in out
        assert "2006-01-03 to 2006-12-29, 251 trading days" in out
        for line, figures in (
            ("Closes, before costs", ["3.4086", "0.2510", "+3.1576"]),
            ("Closes, after 5 bp a side, first day uncharged", ["-0.3702", "-3.1884", "+2.8181"]),
            ("Closes, after 5 bp a side, first day charged", ["-0.3255", "-3.2337", "+2.9081"]),
            ("Opens, before costs", ["5.3052", "4.4202", "+0.8850"]),
            ("Opens, after 5 bp a side, first day uncharged", ["2.0147", "0.7834", "+1.2313"]),
            ("Opens, after 5 bp a side, first day charged", ["2.0257", "0.8293", "+1.1964"]),
        ):
            (row,) = [each for each in out.splitlines() if line in each]
            assert row.split()[-3:] == figures, row
        assert (
            "Closes  gap +3.1576, standard error 0.9872, correlation 0.5258, z +3.1987, "
            "beyond one year's noise" in out
        )
        assert (
            "Opens   gap +0.8850, standard error 1.1640, correlation 0.3663, z +0.7603, "
            "within one year's noise" in out
        )
        assert "Reading, declared before any figure: pointing the way Chan says." in out
        assert "Khandani and Lo report 4.47 for 2006" in out
        assert "judged against nothing" in out
        assert "survivors" in out
        assert "EXPLORATORY." in out

    @pytest.fixture
    def printed(self, capsys, small_closes, large_closes, result) -> list[str]:
        report(small_closes[0], large_closes[0], result)
        return capsys.readouterr().out.splitlines()

    def test_each_vintage_line_starts_with_its_own_label(self, printed) -> None:
        (small,) = [line for line in printed if line.startswith("  S&P 600  ")]
        (large,) = [line for line in printed if line.startswith("  S&P 500  ")]
        assert "ijr_20080114/" in small and small.endswith("lifted from IJR_20080114.mat")
        assert "spx_20071123/" in large and large.endswith("lifted from SPX_20071123.mat")

    def test_the_header_runs_small_caps_large_caps_gap(self, printed) -> None:
        (header,) = [line for line in printed if "Price and specification" in line]
        assert header.split()[-5:] == ["S&P", "600", "S&P", "500", "Gap"]

    def test_the_specification_lines(self, printed) -> None:
        assert "  rule     rule B, Example 3.7's MATLAB, on the closes and on the opens" in printed
        assert "  Sharpe   sqrt(252) * mean / std, no risk-free rate" in printed

    def test_the_lines_that_explain_the_reading(self, printed) -> None:
        assert (
            "    The S&P 600 higher before costs at both prices is pointing the way Chan says, "
            "at one is mixed, at neither is pointing against it."
        ) in printed
        assert "    A gap beyond noise is more than 2 standard errors from 0." in printed

    def test_the_caveats(self, printed) -> None:
        assert (
            "  Both files hold only survivors, the S&P 600 as of 2008-01-14 and the S&P 500 "
            "as of 2007-11-23."
        ) in printed
        assert (
            "  Both files pay the same 5 bp a side, while small caps cost more to trade, "
            "so the after-cost figures flatter the S&P 600."
        ) in printed
        assert (
            "  Chan's sentence names microcaps beside small caps. The file holds no market "
            "values, so it cannot say how many S&P 600 members were microcaps, and no figure "
            "speaks for them."
        ) in printed

    def test_the_reading_line_prints_the_comparisons_reading(
        self, capsys, monkeypatch, small_closes, large_closes, result
    ) -> None:
        monkeypatch.setattr(Comparison, "reading", property(lambda self: MIXED))
        report(small_closes[0], large_closes[0], result)
        assert "  Reading, declared before any figure: mixed." in capsys.readouterr().out

    def test_a_missing_vintage_reaches_the_reader_as_one_line(
        self, monkeypatch, tmp_path, no_arguments
    ) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert "IJR_20080114.mat cannot be" in str(stopped.value)

    def test_run_reads_the_directory_it_is_given(self, tmp_path) -> None:
        with pytest.raises(VintageUnavailable, match="IJR_20080114.mat cannot be"):
            run(tmp_path)

    def test_run_hands_its_directory_to_every_read(self, monkeypatch, tmp_path) -> None:
        asked = []

        def recording(source, *, field="Close", data_dir=None):
            asked.append((source, field, data_dir))
            return [], pd.DataFrame()

        monkeypatch.setattr("chan.khandani_lo_small_caps.load_panel", recording)
        monkeypatch.setattr("chan.khandani_lo_small_caps.comparison", lambda *_: None)
        monkeypatch.setattr("chan.khandani_lo_small_caps.report", lambda *_: None)
        run(tmp_path)
        assert asked == [
            (SOURCE_FILE, "Close", tmp_path),
            (SOURCE_FILE, "Open", tmp_path),
            (LARGE_CAP_FILE, "Close", tmp_path),
            (LARGE_CAP_FILE, "Open", tmp_path),
        ]

    def test_any_other_failure_keeps_its_traceback(self, monkeypatch, no_arguments) -> None:
        def broken(*_args, **_kwargs):
            raise RuntimeError("a bug, not a refusal")

        monkeypatch.setattr("chan.khandani_lo_small_caps.load_panel", broken)
        with pytest.raises(RuntimeError, match="a bug, not a refusal"):
            main()


# --- what the write-up measured --------------------------------------------------------


class TestWhatThePostMeasured:
    """Numbers ``blog/khandani-lo-small-caps-lessons.md`` quotes that no row of Entry 44 declared.

    The write-up measured every one of them after the run, on the same two
    vintages, window and specification as the rows above, so each is
    exploratory and none carries a verdict. The average day is the charged
    specification's, ``chan.khandani_lo.daily_book``, each figure a daily mean
    over that book's own mean gross position. The S&P 500's closes are the
    exception, because ``TestWhatAnAverageDayCosts`` in
    ``tests/test_khandani_lo.py`` already pins 0.5276, 7.2525, 1.4505 and
    13.7453, and this class does not pin them twice.
    """

    @pytest.mark.parametrize(
        ("book", "profit", "cost", "turnover", "multiple"),
        [
            ("small_closes", 6.7197, 7.3545, 1.4709, 1.0945),
            ("small_opens", 11.8569, 7.3644, 1.4729, 0.6211),
            ("large_opens", 8.9815, 7.3182, 1.4636, 0.8148),
        ],
    )
    def test_the_average_day(self, result, book, profit, cost, turnover, multiple) -> None:
        """Profit and cost in basis points of the position a day, turnover in books a day."""
        day = daily_book(getattr(result, book))
        assert day.profit * 1e4 == pytest.approx(profit, abs=5e-5), book
        assert day.cost * 1e4 == pytest.approx(cost, abs=5e-5), book
        assert day.turnover == pytest.approx(turnover, abs=5e-5), book
        assert day.cost_per_profit == pytest.approx(multiple, abs=5e-5), book

    def test_every_book_trades_about_the_same_and_pays_about_the_same(self, result) -> None:
        """Turnover sits within 1.4505 to 1.4729 books a day, so the profit is what differs."""
        days = [daily_book(getattr(result, b)) for b in ("small_closes", "small_opens")]
        days += [daily_book(getattr(result, b)) for b in ("large_closes", "large_opens")]
        turnovers = [d.turnover for d in days]
        assert max(turnovers) - min(turnovers) < 0.025
        for d in days:
            assert d.cost == pytest.approx(d.turnover * ONE_WAY_COST, abs=1e-15)

    @pytest.mark.parametrize(
        ("book", "break_even"),
        [
            ("small_closes", "4.57"),
            ("small_opens", "8.05"),
            ("large_closes", "0.36"),
            ("large_opens", "6.14"),
        ],
    )
    def test_the_cost_a_side_at_which_each_book_breaks_even(self, result, book, break_even) -> None:
        """The average day's profit over its turnover, in basis points of each unit traded.

        At that cost a side the charged specification's mean daily profit is
        0, so its Sharpe ratio is 0. The profit and the turnover share one
        divisor, so the mean book cancels.
        """
        r = getattr(result, book)
        day = daily_book(r)
        found = day.profit / day.turnover
        assert f"{found * 1e4:.2f}" == break_even, book
        assert (r.pnl - r.traded * found).mean() == pytest.approx(0.0, abs=1e-15)

    def test_the_open_lifts_the_s_and_p_500_far_more(self, result) -> None:
        large = result.large_opens.before_costs - result.large_closes.before_costs
        small = result.small_opens.before_costs - result.small_closes.before_costs
        assert f"{large:.4f}" == "4.1693"
        assert f"{small:.4f}" == "1.8966"

    @staticmethod
    def _daily(pnl: np.ndarray) -> float:
        return float(pnl.mean() / pnl.std(ddof=1))

    def test_without_the_correlation_the_closes_standard_error_would_be_1_4252(
        self, result
    ) -> None:
        """Memmel's formula at a correlation of 0, against the measured 0.5258."""
        a, b = result.small_closes.pnl, result.large_closes.pnl
        variance = memmel_variance(self._daily(a), self._daily(b), 0, result.closes_gap.days)
        unrelated = math.sqrt(TRADING_DAYS * variance)
        assert f"{unrelated:.4f}" == "1.4252"
        assert f"{result.closes_gap.gap / unrelated:.4f}" == "2.2155"
        assert result.closes_gap.standard_error < unrelated

    def test_the_correlation_term_carries_almost_all_of_the_variance(self, result) -> None:
        """2(1 − ρ) against the whole bracket, because daily Sharpe ratios are small."""
        shares = {}
        for price, gap in (("closes", result.closes_gap), ("opens", result.opens_gap)):
            small = getattr(result, f"small_{price}").pnl
            large = getattr(result, f"large_{price}").pnl
            bracket = gap.days * memmel_variance(
                self._daily(small), self._daily(large), gap.correlation, gap.days
            )
            shares[price] = f"{2 * (1 - gap.correlation) / bracket:.2f}"
        assert shares == {"closes": "0.98", "opens": "0.94"}


# --- what the post quotes --------------------------------------------------------------

POST = paths.REPO_ROOT / "blog" / "khandani-lo-small-caps-lessons.md"


@pytest.fixture(scope="module")
def post() -> str:
    return POST.read_text(encoding="utf-8")


def _latex_row(label: str, *cells: str) -> str:
    """One row of a post's ``array``, with ``S&P`` written the way the post's LaTeX writes it."""
    escaped = label.replace("S&P", "S}\\&\\text{P")
    return " & ".join([f"\\text{{{escaped}}}", *cells])


def _latex_rows(*rows: str) -> str:
    """A table's rows in order, down to the line that ends its ``array``."""
    return " \\\\\n".join(rows) + "\n\\end{array}"


def _latex_head(*heads: str) -> str:
    """A table's line of column heads and the rule under it, so a swapped head fails too."""
    cells = [h.replace("S&P", "S}\\&\\text{P") for h in heads]
    return " & ".join(f"\\text{{{c}}}" for c in cells) + " \\\\ \\hline\n"


class TestThePostQuotesTheRun:
    """One copy of each figure ``blog/khandani-lo-small-caps-lessons.md`` quotes from this run.

    Each fragment is built from the value the run computes, at the precision
    the post prints, so a typo in the post fails here and a re-pin moves the
    post in the same change. It reads one copy of each figure: the tables of
    Lessons 1, 2 and 4 whole, and the first prose copy of the rest. The italic
    summary, the prose that repeats a table and the figure's caption are not
    read. The S&P 400 figures Lesson 6 quotes are held by
    ``TestThePostQuotesTheLadder`` in ``tests/test_khandani_lo_mid_caps.py``,
    the figure's alt text by ``TestTheAltText`` in
    ``tests/test_khandani_lo_small_caps_figures.py``, and the two sketches'
    alt text by ``TestThePost`` in
    ``tests/test_khandani_lo_small_caps_whiteboard.py``.
    """

    def test_the_files_and_the_window(self, post, small_closes, result) -> None:
        _, frame = small_closes
        window = frame.loc[START:END]
        days = result.small_closes.days
        words = {8: "Eight", 6: "Six", 2: "two"}
        missing = int(window.isna().any().sum())
        none_all_year = int(window.isna().all().sum())
        fragments = [
            f"window of {len(days)} trading days, {days[0].date()} to {days[-1].date()}.",
            f"On the window’s first day {frame.loc[START].notna().sum()} of them have a price, "
            f"and on its last day {frame.loc[END].notna().sum()}.",
            f"{words[missing]} of the {frame.shape[1]} stocks miss a price somewhere in 2006. "
            f"{words[none_all_year]} have none all year, and {words[missing - none_all_year]} "
            "start trading during it.",
        ]
        assert [f for f in fragments if f not in post] == []

    def test_lesson_1s_table(self, post, result) -> None:
        g = result.closes_gap
        assert (
            _latex_head("On the closes, before costs", "Figure")
            + _latex_rows(
                _latex_row("S&P 600, Sharpe ratio", f"{g.a_sharpe:.4f}"),
                _latex_row("S&P 500, Sharpe ratio", f"{g.b_sharpe:.4f}"),
                _latex_row("Gap", f"{g.gap:+.4f}"),
                _latex_row("Correlation of daily profits", f"{g.correlation:.4f}"),
                _latex_row("Standard error of the gap", f"{g.standard_error:.4f}"),
                _latex_row("Gap in standard errors, z", f"{g.z:+.4f}"),
            )
            in post
        )

    def test_lesson_2s_table(self, post, result) -> None:
        """Both prices' Sharpe ratios, gaps, correlations, standard errors and z values."""
        c, o = result.closes_gap, result.opens_gap
        assert (
            _latex_head("Before costs", "Closes", "Opens")
            + _latex_rows(
                _latex_row("S&P 600, Sharpe ratio", f"{c.a_sharpe:.4f}", f"{o.a_sharpe:.4f}"),
                _latex_row("S&P 500, Sharpe ratio", f"{c.b_sharpe:.4f}", f"{o.b_sharpe:.4f}"),
                _latex_row("Gap", f"{c.gap:+.4f}", f"{o.gap:+.4f}"),
                _latex_row("Correlation", f"{c.correlation:.4f}", f"{o.correlation:.4f}"),
                _latex_row(
                    "Standard error of the gap",
                    f"{c.standard_error:.4f}",
                    f"{o.standard_error:.4f}",
                ),
                _latex_row("Gap in standard errors, z", f"{c.z:+.4f}", f"{o.z:+.4f}"),
            )
            in post
        )

    def test_the_opens_lift(self, post, result) -> None:
        lc, lo = result.large_closes.before_costs, result.large_opens.before_costs
        sc, so = result.small_closes.before_costs, result.small_opens.before_costs
        assert (
            f"The S&P 500 rises by {lo - lc:.4f}, from {lc:.4f} to {lo:.4f}, "
            f"and the S&P 600 by {so - sc:.4f}, from {sc:.4f} to {so:.4f}."
        ) in post

    def test_lesson_3s_figures(self, post, result) -> None:
        """The correlation term's share of the bracket, and the closes with the correlation at 0."""
        daily = TestWhatThePostMeasured._daily
        shares = []
        for price in ("closes", "opens"):
            gap = getattr(result, f"{price}_gap")
            small = getattr(result, f"small_{price}").pnl
            large = getattr(result, f"large_{price}").pnl
            bracket = gap.days * memmel_variance(
                daily(small), daily(large), gap.correlation, gap.days
            )
            shares.append(round(100 * 2 * (1 - gap.correlation) / bracket))
        g = result.closes_gap
        unrelated = math.sqrt(
            TRADING_DAYS
            * memmel_variance(
                daily(result.small_closes.pnl), daily(result.large_closes.pnl), 0, g.days
            )
        )
        fragments = [
            f"carries {shares[0]} percent of the bracket on the closes and {shares[1]} percent "
            "on the opens",
            f"the standard error would be {unrelated:.4f}, and the gap of {g.gap:+.4f} would sit "
            f"{g.gap / unrelated:.4f} standard errors out",
        ]
        assert [f for f in fragments if f not in post] == []

    def test_lesson_4s_after_cost_table(self, post, result) -> None:
        """Each price's heading row, then Chan's uncharged row and the charged one."""
        blocks = []
        for price in ("closes", "opens"):
            small, large = getattr(result, f"small_{price}"), getattr(result, f"large_{price}")
            rows = [f"\\text{{{price.capitalize()}}} & & &"]
            for field, words in (("after_costs", "uncharged"), ("after_costs_charged", "charged")):
                a, b = getattr(small, field), getattr(large, field)
                rows.append(f"\\quad\\text{{{words}}} & {a:.4f} & {b:.4f} & {a - b:+.4f}")
            blocks.append(" \\\\\n".join(rows))
        head = _latex_head("After costs", "S&P 600", "S&P 500", "Gap")
        assert head + " \\\\ \\hline\n".join(blocks) + "\n\\end{array}" in post

    def test_lesson_4s_average_day_tables(self, post, result) -> None:
        """Profit, cost and turnover in one table, cost over profit and break-even in the next."""
        books = {
            "S&P 600, closes": daily_book(result.small_closes),
            "S&P 600, opens": daily_book(result.small_opens),
            "S&P 500, opens": daily_book(result.large_opens),
            "S&P 500, closes": daily_book(result.large_closes),
        }
        first = [
            _latex_row(label, f"{d.profit * 1e4:.4f}", f"{d.cost * 1e4:.4f}", f"{d.turnover:.4f}")
            for label, d in books.items()
        ]
        second = [
            _latex_row(label, f"{d.cost_per_profit:.4f}", f"{d.profit / d.turnover * 1e4:.2f}")
            for label, d in books.items()
        ]
        tables = (
            _latex_head("Book", "Profit", "Cost", "Turnover") + _latex_rows(*first),
            _latex_head("Book", "Cost over profit", "Break-even") + _latex_rows(*second),
        )
        assert [t for t in tables if t not in post] == []

    def test_lesson_4s_ranges(self, post, result) -> None:
        days = [
            daily_book(getattr(result, b))
            for b in ("small_closes", "small_opens", "large_closes", "large_opens")
        ]
        turnovers = [d.turnover for d in days]
        costs = [d.cost * 1e4 for d in days]
        assert (
            f"Every book trades between {min(turnovers):.4f} and {max(turnovers):.4f} times its "
            f"average gross position a day, so every book pays between {min(costs):.4f} and "
            f"{max(costs):.4f} basis points a day."
        ) in post

    def test_lesson_5s_bound_and_two_days(self, post, small_closes) -> None:
        _, frame = small_closes
        factor = math.exp(SCALE_BREAK_BOUND)
        fragments = [
            f"moves by more than a factor of {factor:.1f} from the day before, which means a "
            f"close below 1/{factor:.1f}, or {1 / factor:.3f}, of the previous one",
        ]
        for symbol, day, tail in (
            ("BCSI", "2006-02-06", " the day before"),
            ("SCUR", "2006-07-12", ""),
        ):
            row = frame.index.get_loc(pd.Timestamp(day))
            before, after = frame[symbol].iloc[row - 1], frame[symbol].iloc[row]
            fragments.append(
                f"**{symbol} on {day}** closes at {after:g} against {before:g}{tail}, "
                f"a ratio of {after / before:.4f}."
            )
        assert [f for f in fragments if f not in post] == []
