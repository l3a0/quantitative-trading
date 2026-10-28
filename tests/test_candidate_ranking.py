"""Pins for the figures ``docs/candidate-ranking.md`` derives rather than quotes.

The ranking quotes most of its numbers from the test that already pins each
one, and names that test beside it. What it adds is arithmetic on those
numbers: the variant count N, the hurdle t* that Bonferroni sets at that N, a
t converted from a Sharpe ratio and its span, and the product of a Sharpe
ratio and the root of a span's length that decides whether a holdout test
could reach t*. This file is the authority for those. The method they follow
was posted on issue 774 before any row was filled in.

Each input below is copied from the assertion that pins it, and the comment
beside it names that assertion. The price of copying is that a re-pin there
does not fail here. The ranking is a dated document read at ``6da0ee38``, so
a re-pin upstream means re-deriving the ranking rather than editing a cell.

Only one input is read from data. Entry 52's seasonal-momentum series is
measured over 1965 to 2024, the span Entry 52 already read, and the months
from 1927 to 1964 are dropped before any statistic is taken, because that
span is one the ranking names as never loaded by a search.
"""

from __future__ import annotations

import math
from datetime import date
from statistics import NormalDist

import pytest

from chan.open_asset_pricing import long_short_returns

NORMAL = NormalDist()

#: The one-sided tail beyond t = 2, which Bonferroni divides by N.
TAIL_AT_TWO = 1 - NORMAL.cdf(2)

#: Variants per entry of ``docs/replication-log.md``, at ``6da0ee38``, under the
#: four counting rules of the method comment on issue 774. Entries that measure
#: no strategy return count 0 and are left out. Entries 44 and 50 count only the
#: cells they add, since each reruns cells an earlier entry already counted.
REPO_VARIANTS = {
    3: 6,
    4: 13,
    7: 32,
    8: 1,
    9: 5,
    10: 13,
    11: 2,
    12: 2,
    13: 11,
    14: 2,
    16: 803,
    17: 16,
    18: 4,
    19: 6,
    21: 7,
    22: 1,
    23: 1,
    24: 1,
    25: 2,
    26: 2,
    28: 7,
    30: 3,
    31: 11,
    32: 3,
    33: 52,
    34: 7 + 172_056 + 48_048,
    35: 10,
    36: 100,
    37: 1,
    38: 5,
    39: 5,
    40: 10,
    41: 3,
    44: 2,
    45: 3,
    46: 16,
    47: 11,
    48: 2,
    49: 3,
    50: 6,
    51: 1,
    52: 7,
}

#: Entry 34's two scans for the window and the parameters behind the book's
#: printed figures. The window scan's count is the log's. The grid's is the
#: product of the ranges the log states, an upper bound, since the log gives
#: no count of the cells that ran.
ENTRY_34_SCANS = 172_056 + 48_048

#: ``trading-strategies`` at ``7a26498``: 6,951 return-measuring variants with
#: every walk-forward grid counted once per training window, plus 21
#: conditioning splits. Placebo and jitter draws are null runs, left out.
SIBLING_VARIANTS = 6_951 + 21

#: The sibling's count with each walk-forward grid counted once per instrument
#: and span, the narrowest reading of its searches.
SIBLING_NARROW = 1_104

#: The last day a vendor could supply for a span that runs to the present.
SPAN_END = date(2026, 9, 30)


def hurdle(n: int) -> float:
    """The t whose one-sided normal tail is the tail at t = 2 divided by ``n``."""
    return NORMAL.inv_cdf(1 - TAIL_AT_TWO / n)


def years(start: date, end: date) -> float:
    return (end - start).days / 365.25


def t_from_sharpe(sharpe: float, days: int) -> float:
    """An annualized Sharpe ratio over ``days`` trading days, as a t on the daily mean."""
    return sharpe * math.sqrt(days / 252)


N = sum(REPO_VARIANTS.values()) + SIBLING_VARIANTS
N_NARROW = sum(REPO_VARIANTS.values()) - ENTRY_34_SCANS + SIBLING_NARROW


class TestTheVariantCount:
    def test_n_across_both_repositories(self) -> None:
        assert sum(REPO_VARIANTS.values()) == 221_302
        assert N == 228_274

    def test_entry_34s_scans_are_most_of_n(self) -> None:
        """The two scans chased the book's printed figures rather than an edge, and
        the counting rules count them anyway. Without them and with the sibling's
        narrow count, N falls by two orders of magnitude."""
        assert N_NARROW == 2_302

    def test_the_hurdle_at_each_count(self) -> None:
        assert TAIL_AT_TWO == pytest.approx(0.02275, abs=5e-6)
        assert hurdle(N) == pytest.approx(5.2000, abs=5e-5)
        assert hurdle(N_NARROW) == pytest.approx(4.2675, abs=5e-5)

    def test_the_hurdle_grows_with_n(self) -> None:
        """A check on ``hurdle`` itself: one look needs t = 2 and more looks need more."""
        assert hurdle(1) == pytest.approx(2.0, abs=1e-9)
        assert hurdle(10) < hurdle(100) < hurdle(N_NARROW) < hurdle(N)


#: Rows with an after-cost Sharpe ratio pinned at 5 bp a side, as ``(Sharpe,
#: trading days)``. Each is the figure with the first day's rebalance charged
#: where the entry pins one, and Entry 10's rule A is the notebook's own after-cost
#: figure. Every one is 2006 except Entry 19's, which is 2007 to 2011.
AFTER_COST_ROWS = {
    # tests/test_khandani_lo_small_caps.py, TestTheSmallCapFigures::test_opens
    "44b S&P 600 opens": (2.0257, 251),
    # tests/test_khandani_lo_mid_caps.py, TestTheControl
    "50d S&P 600 control opens": (1.6903, 251),
    # tests/test_khandani_lo.py, TestRuleAOnTheOpens::test_the_figures
    "10 rule A S&P 500 opens": (1.3997, 251),
    # tests/test_khandani_lo.py, TestRuleBOnTheOpens::test_after_costs_with_both_quirks_removed
    "10 rule B S&P 500 opens": (0.8293, 251),
    # tests/test_khandani_lo_mid_caps.py, TestTheMidCapFigures::test_opens
    "50b S&P 400 opens": (0.4884, 251),
    # tests/test_khandani_lo_book_two.py, TestBesideTheFirstBook::
    # test_the_first_books_rule_on_this_panel_and_window
    "19 row 10 S&P 500 closes": (0.3797, 1260),
    # tests/test_khandani_lo_mid_caps.py, TestTheControl
    "50c S&P 600 control closes": (0.0575, 251),
    # tests/test_khandani_lo_small_caps.py, TestTheSmallCapFigures::test_closes
    "44a S&P 600 closes": (-0.3255, 251),
    # tests/test_khandani_lo_mid_caps.py, TestTheMidCapFigures::test_closes
    "50a S&P 400 closes": (-1.4524, 251),
    # tests/test_khandani_lo.py, test_after_costs_with_both_quirks_removed
    "8 S&P 500 closes": (-3.2337, 251),
}


class TestTheAfterCostRows:
    @pytest.mark.parametrize(
        ("row", "expected"),
        [
            ("44b S&P 600 opens", 2.0217),
            ("50d S&P 600 control opens", 1.6869),
            ("10 rule A S&P 500 opens", 1.3969),
            ("10 rule B S&P 500 opens", 0.8277),
            ("50b S&P 400 opens", 0.4874),
            ("19 row 10 S&P 500 closes", 0.8490),
            ("50c S&P 600 control closes", 0.0574),
            ("44a S&P 600 closes", -0.3249),
            ("50a S&P 400 closes", -1.4495),
            ("8 S&P 500 closes", -3.2273),
        ],
    )
    def test_each_sharpe_as_a_t(self, row: str, expected: float) -> None:
        sharpe, days = AFTER_COST_ROWS[row]
        assert t_from_sharpe(sharpe, days) == pytest.approx(expected, abs=5e-5)

    def test_none_reaches_the_hurdle_even_unadjusted_but_one(self) -> None:
        """Only Entry 44's S&P 600 opens reach t = 2, on one year a search loaded."""
        reaching = [r for r, (s, d) in AFTER_COST_ROWS.items() if t_from_sharpe(s, d) >= 2]
        assert reaching == ["44b S&P 600 opens"]
        assert all(t_from_sharpe(s, d) < hurdle(N_NARROW) for s, d in AFTER_COST_ROWS.values())

    @pytest.mark.parametrize(
        ("row", "expected"),
        [
            ("44b S&P 600 opens", 6.6),
            ("50d S&P 600 control opens", 9.5),
            ("19 row 10 S&P 500 closes", 187.6),
        ],
    )
    def test_the_years_of_forward_data_each_would_need(self, row: str, expected: float) -> None:
        """If the in-sample Sharpe ratio held exactly, the years before t reaches t*."""
        sharpe, _ = AFTER_COST_ROWS[row]
        assert (hurdle(N) / sharpe) ** 2 == pytest.approx(expected, abs=0.05)


#: The screen: a row's Sharpe ratio, the span no search loaded, and whether the
#: Sharpe ratio is after costs at 5 bp a side or before any cost. A product
#: below t* fails whatever the cost. A gross product above it decides nothing
#: until the row has an after-cost figure.
SCREEN = {
    # Entry 32, tests/test_kalman_hedge.py; EWA and EWC after Chan's file ends
    "32 Kalman EWA/EWC": (2.36116164, date(2012, 4, 10), SPAN_END),
    # Entry 23, tests/test_etf_cointegration.py; EWA, EWC and IGE after the file
    "23 Johansen EWA/EWC/IGE": (1.3913100883, date(2012, 4, 10), SPAN_END),
    # Entry 36, tests/test_roll_momentum.py; TU after the strip ends
    "36 TU on lagged roll": (1.803348, date(2012, 8, 14), SPAN_END),
    # Entry 35, tests/test_vx_calendar_spread.py, B3; VX after the strip ends
    "35 VX calendar B3": (1.457009, date(2012, 5, 8), SPAN_END),
    # Entry 28, tests/test_vx_es.py; VX and ES after the files end
    "28 VX against ES": (1.393201, date(2012, 5, 9), SPAN_END),
    # Entry 40, tests/test_opening_gap.py; FSTX after the file ends
    "40 FSTX opening gap": (1.441620, date(2012, 5, 18), SPAN_END),
    # Entry 25, tests/test_aud_cad_johansen.py; AUD and CAD before any search's first day
    "25 AUD.USD and CAD.USD": (1.6108902337, date(1971, 1, 4), date(2007, 7, 20)),
    # Entry 19, tests/test_khandani_lo_book_two.py, 4.4; S&P 500 opens before Khandani and Lo's 1995
    "19 Example 4.4 opens": (4.713284, date(1992, 7, 1), date(1994, 12, 30)),
    # Entry 34, tests/test_calendar_spread_reversion.py; CL after the strip ends
    "34 CL calendar spread": (1.278216, date(2012, 8, 14), SPAN_END),
    # Entry 31, tests/test_cl_reversal_momentum.py; CL after the file ends
    "31 CL reversal and momentum": (1.100368, date(2012, 5, 5), SPAN_END),
    # Entry 33, tests/test_tu_momentum.py; TU after the strip ends
    "33 TU momentum": (1.041462, date(2012, 8, 14), SPAN_END),
    # Entry 10, rule A, after costs, tests/test_khandani_lo.py; S&P 500 opens before 1995
    "10 rule A opens": (1.3997, date(1992, 7, 1), date(1994, 12, 30)),
    # Entry 19, Example 4.3; S&P 500 closes between the two published samples
    "19 Example 4.3 closes": (1.259478, date(1988, 1, 4), date(1994, 12, 30)),
    # Entry 41, tests/test_vx_es.py, with no cost at all; VX and ES after the files end
    "41 VX against ES on roll": (1.030894, date(2012, 5, 8), SPAN_END),
    # trading-strategies data/gen_ledger.jsonl:62, at a 1 bp hedge; SPY chains before 2010
    "sibling generative 0.05 delta call": (0.688, date(1996, 1, 4), date(2010, 11, 30)),
    # Entry 18, the mirror, tests/test_buy_on_gap.py; S&P 500 opens before 1995
    "18 short on gap": (1.7853, date(1992, 7, 1), date(1994, 12, 30)),
    # Entry 46, run B1, tests/test_pead_rerun.py; the same span
    "46 post-earnings drift B1": (1.7045, date(1992, 7, 1), date(1994, 12, 30)),
    # Entry 30, tests/test_aud_cad_rollover.py; AUD and CAD before any search's first day
    "30 AUD.CAD with rollover": (0.5418018005, date(1971, 1, 4), date(2007, 7, 20)),
    # Entry 11, natural gas 1994 to 2008, one ratio per yearly trade,
    # tests/test_commodity_seasonals.py
    "11 natural gas seasonal": (1.0008, date(1990, 4, 2), date(1993, 12, 31)),
    # Entry 13, tests/test_pca_factor.py; S&P 600 before Chan's file
    "13 PCA factor model": (0.5787, date(1994, 10, 3), date(2004, 1, 14)),
    # Entry 7, Example 7.6 on IJR survivors, its t of 1.15 over 18 Januaries as a yearly ratio
    "7 January effect on survivors": (1.15 / math.sqrt(18), date(1994, 10, 3), date(2004, 1, 14)),
    # Entry 44, after costs; S&P 600 from launch to Chan's file, the reading the ranking rejects
    "44b on 1994 to 2004": (2.0257, date(1994, 10, 3), date(2004, 1, 14)),
    # Entry 50, after costs; the same span
    "50d on 1994 to 2004": (1.6903, date(1994, 10, 3), date(2004, 1, 14)),
}


class TestTheScreen:
    @pytest.mark.parametrize(
        ("row", "span_years", "product"),
        [
            ("32 Kalman EWA/EWC", 14.47, 8.98),
            ("23 Johansen EWA/EWC/IGE", 14.47, 5.29),
            ("36 TU on lagged roll", 14.13, 6.78),
            ("35 VX calendar B3", 14.40, 5.53),
            ("28 VX against ES", 14.39, 5.29),
            ("40 FSTX opening gap", 14.37, 5.46),
            ("25 AUD.USD and CAD.USD", 36.54, 9.74),
            ("19 Example 4.4 opens", 2.50, 7.45),
            ("34 CL calendar spread", 14.13, 4.80),
            ("31 CL reversal and momentum", 14.40, 4.18),
            ("33 TU momentum", 14.13, 3.91),
            ("10 rule A opens", 2.50, 2.21),
            ("19 Example 4.3 closes", 6.99, 3.33),
            ("41 VX against ES on roll", 14.40, 3.91),
            ("sibling generative 0.05 delta call", 14.90, 2.66),
            ("18 short on gap", 2.50, 2.82),
            ("46 post-earnings drift B1", 2.50, 2.69),
            ("30 AUD.CAD with rollover", 36.54, 3.28),
            ("11 natural gas seasonal", 3.75, 1.94),
            ("13 PCA factor model", 9.28, 1.76),
            ("7 January effect on survivors", 9.28, 0.83),
            ("44b on 1994 to 2004", 9.28, 6.17),
            ("50d on 1994 to 2004", 9.28, 5.15),
        ],
    )
    def test_each_rows_span_and_product(self, row: str, span_years: float, product: float) -> None:
        sharpe, start, end = SCREEN[row]
        assert years(start, end) == pytest.approx(span_years, abs=0.005)
        assert sharpe * math.sqrt(years(start, end)) == pytest.approx(product, abs=0.005)

    def test_which_gross_products_clear_the_hurdle(self) -> None:
        """The eight rows a measurement at 5 bp a side could make registrable."""
        gross = {k: v for k, v in SCREEN.items() if not k.startswith(("44b on", "50d on"))}
        clearing = sorted(
            k for k, (s, a, b) in gross.items() if s * math.sqrt(years(a, b)) >= hurdle(N)
        )
        assert clearing == sorted(
            [
                "32 Kalman EWA/EWC",
                "23 Johansen EWA/EWC/IGE",
                "36 TU on lagged roll",
                "35 VX calendar B3",
                "28 VX against ES",
                "40 FSTX opening gap",
                "25 AUD.USD and CAD.USD",
                "19 Example 4.4 opens",
            ]
        )

    def test_the_s_and_p_600_row_turns_on_the_span_alone(self) -> None:
        """Were 1994 to 2004 counted as unloaded, Chan's file would clear and the
        control rebuilt from Alpha Vantage would not."""
        for row, clears in (("44b on 1994 to 2004", True), ("50d on 1994 to 2004", False)):
            sharpe, start, end = SCREEN[row]
            assert (sharpe * math.sqrt(years(start, end)) >= hurdle(N)) is clears


class TestTheSeasonalMomentumRow:
    def test_its_gross_sharpe_over_the_span_entry_52_read(self) -> None:
        _, series = long_short_returns("MomSeasonShort")
        loaded = series[series.index >= "1965-01-01"] / 100
        assert len(loaded) == 720
        sharpe = loaded.mean() / loaded.std() * math.sqrt(12)
        assert sharpe == pytest.approx(0.8096, abs=5e-5)

    def test_even_before_costs_1927_to_1964_cannot_reach_the_hurdle(self) -> None:
        span = years(date(1927, 1, 1), date(1964, 12, 31))
        assert span == pytest.approx(38.00, abs=0.005)
        assert 0.8096 * math.sqrt(span) == pytest.approx(4.99, abs=0.005)
        assert 0.8096 * math.sqrt(span) < hurdle(N)
