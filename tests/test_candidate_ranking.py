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

import numpy as np
import pandas as pd
import pytest

from chan import cross_sectional_momentum
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

#: ``trading-strategies`` at ``7a26498``, one count per search, each walk-forward
#: grid counted once per instrument and span. Ledger cells are deduplicated on
#: (template, parameters, ticker), which leaves the edge ledger's 63 cells all
#: inside the idea ledger's 82. Placebo and jitter draws are null runs, left out.
SIBLING_SEARCHES = {
    "proxy covered call": 36,
    "real-chain covered call": 152,
    "structure campaign and LLM proposer": 82,
    "generative search": 56,
    "factor panel": 63,
    "volatility premium": 20,
    "registered put credit spread": 142,
    "Gap E, Gap G and call-spread exits": 16,
    "random-entry replication": 3,
    "covered call in R-multiples and the NVDA and GLD coda": 42,
    "QQQ one-day wheel": 30,
    "support and resistance catalog": 384,
    "cup-and-handle scan": 12,
    "intraday breakout continuation": 46,
    "volume-profile reversal": 20,
}

#: Counting each walk-forward grid once per training window instead: the
#: covered call's 141 grid cells become 2,952 evaluations and the put credit
#: spread's 138 become 3,174.
PER_WINDOW_EXTRA = (2_952 - 141) + (3_174 - 138)

#: Conditioning splits, which tag cycles inside one fixed baseline.
CONDITIONING_SPLITS = 21

SIBLING_NARROW = sum(SIBLING_SEARCHES.values())
SIBLING_VARIANTS = SIBLING_NARROW + PER_WINDOW_EXTRA + CONDITIONING_SPLITS

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
        assert SIBLING_NARROW == 1_104
        assert SIBLING_VARIANTS == 6_972
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


#: Rows with an after-cost Sharpe ratio pinned at 5 bp a side, as ``(Sharpe
#: before costs, Sharpe after, trading days)``. Each after-cost figure is the
#: one with the first day's rebalance charged where the entry pins one, and
#: Entry 10's rule A is the notebook's own. Every row is 2006 except Entry 19's,
#: which is 2007 to 2011.
AFTER_COST_ROWS = {
    # tests/test_khandani_lo_small_caps.py, TestTheSmallCapFigures::test_opens
    "44b S&P 600 opens": (5.3052, 2.0257, 251),
    # tests/test_khandani_lo_mid_caps.py, TestTheControl
    "50d S&P 600 control opens": (4.5808, 1.6903, 251),
    # tests/test_khandani_lo.py, TestRuleAOnTheOpens::test_the_figures
    "10 rule A S&P 500 opens": (2.3818, 1.3997, 251),
    # tests/test_khandani_lo.py, TestRuleBOnTheOpens
    "10 rule B S&P 500 opens": (4.4202, 0.8293, 251),
    # tests/test_khandani_lo_mid_caps.py, TestTheMidCapFigures::test_opens
    "50b S&P 400 opens": (3.4533, 0.4884, 251),
    # tests/test_khandani_lo_book_two.py, TestBesideTheFirstBook::
    # test_the_first_books_rule_on_this_panel_and_window
    "19 row 10 S&P 500 closes": (1.2219, 0.3797, 1260),
    # tests/test_khandani_lo_mid_caps.py, TestTheControl
    "50c S&P 600 control closes": (3.5194, 0.0575, 251),
    # tests/test_khandani_lo_small_caps.py, TestTheSmallCapFigures::test_closes
    "44a S&P 600 closes": (3.4086, -0.3255, 251),
    # tests/test_khandani_lo_mid_caps.py, TestTheMidCapFigures::test_closes
    "50a S&P 400 closes": (2.0338, -1.4524, 251),
    # tests/test_khandani_lo.py, test_after_costs_with_both_quirks_removed
    "8 S&P 500 closes": (0.2510, -3.2337, 251),
}


class TestTheAfterCostRows:
    @pytest.mark.parametrize(
        ("row", "before", "after"),
        [
            ("44b S&P 600 opens", 5.2947, 2.0217),
            ("50d S&P 600 control opens", 4.5717, 1.6869),
            ("10 rule A S&P 500 opens", 2.3771, 1.3969),
            ("10 rule B S&P 500 opens", 4.4114, 0.8277),
            ("50b S&P 400 opens", 3.4464, 0.4874),
            ("19 row 10 S&P 500 closes", 2.7323, 0.8490),
            ("50c S&P 600 control closes", 3.5124, 0.0574),
            ("44a S&P 600 closes", 3.4018, -0.3249),
            ("50a S&P 400 closes", 2.0298, -1.4495),
            ("8 S&P 500 closes", 0.2505, -3.2273),
        ],
    )
    def test_each_sharpe_as_a_t(self, row: str, before: float, after: float) -> None:
        gross, net, days = AFTER_COST_ROWS[row]
        assert t_from_sharpe(gross, days) == pytest.approx(before, abs=5e-5)
        assert t_from_sharpe(net, days) == pytest.approx(after, abs=5e-5)

    def test_none_reaches_the_hurdle_and_one_reaches_two(self) -> None:
        """Only Entry 44's S&P 600 opens reach t = 2 after costs, on one year a search loaded."""
        reaching = [r for r, (_, s, d) in AFTER_COST_ROWS.items() if t_from_sharpe(s, d) >= 2]
        assert reaching == ["44b S&P 600 opens"]
        assert all(t_from_sharpe(s, d) < hurdle(N_NARROW) for _, s, d in AFTER_COST_ROWS.values())

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
        _, sharpe, _ = AFTER_COST_ROWS[row]
        assert (hurdle(N) / sharpe) ** 2 == pytest.approx(expected, abs=0.05)


def available(spans: tuple[tuple[date, date], ...]) -> float:
    """The years of every span no search loaded, joined into one holdout."""
    return sum(years(start, end) for start, end in spans)


def needed(sharpe: float, n: int = N) -> float:
    """The years over which ``sharpe`` held exactly would reach the hurdle at ``n``."""
    return (hurdle(n) / sharpe) ** 2


#: Spans no search in either repository loaded, per instrument or universe.
#: Each starts the day after the last day a search read, or on the day the
#: instrument began trading, and ends on the day before a search's first day.
#: Spans before a file starts have to be bought.
EWA_EWC = ((date(1996, 3, 18), date(2006, 4, 25)), (date(2012, 4, 10), SPAN_END))
EWA_EWC_IGE = ((date(2001, 10, 22), date(2006, 4, 25)), (date(2012, 4, 10), SPAN_END))
TU = ((date(2012, 8, 14), SPAN_END),)
VX = ((date(2012, 5, 9), SPAN_END),)
FSTX = ((date(1998, 6, 22), date(2004, 7, 6)), (date(2012, 5, 18), SPAN_END))
CL = ((date(1983, 3, 30), date(1986, 11, 2)), (date(2012, 8, 14), SPAN_END))
AUD_CAD = ((date(1983, 12, 12), date(2007, 7, 20)),)
#: Point-in-time S&P 500 members before Chan's file. Norgate's membership is
#: reported to reach 1967. How far back opening prices reach is not established.
SP500 = ((date(1967, 1, 3), date(1999, 11, 23)),)
#: The S&P 600 from its launch to Chan's file. 1999-11 on is in the Alpha
#: Vantage cross-section, survivors only. The years before have to be bought.
SP600 = ((date(1994, 10, 28), date(2004, 1, 14)),)
#: The S&P 400 from its launch, either side of Entry 50's year, and before the
#: sibling's intraday archive starts in 2016.
SP400 = ((date(1991, 6, 19), date(2005, 11, 30)), (date(2007, 1, 1), date(2015, 12, 31)))
MOM_SEASON = ((date(1927, 1, 1), date(1964, 12, 31)),)
NATURAL_GAS = ((date(1990, 4, 3), date(1993, 12, 31)),)
SPY_CHAINS = ((date(1996, 1, 4), date(2010, 5, 16)),)

#: ``(Sharpe ratio, whether it is after costs at 5 bp a side, spans)``. A gross
#: Sharpe ratio is an upper bound on the after-cost one, so a gross row whose
#: years available fall short of the years needed fails whatever its cost.
SCREEN = {
    # Entry 32, tests/test_kalman_hedge.py
    "32 Kalman EWA/EWC": (2.36116164, False, EWA_EWC),
    # Entry 25, tests/test_aud_cad_johansen.py, AUD floating from 1983-12-12
    "25 AUD.USD and CAD.USD": (1.6108902337, False, AUD_CAD),
    # Entry 36, tests/test_roll_momentum.py
    "36 TU on lagged roll": (1.803348, False, TU),
    # Entry 40, tests/test_opening_gap.py
    "40 FSTX opening gap": (1.441620, False, FSTX),
    # Entry 23, tests/test_etf_cointegration.py
    "23 Johansen EWA/EWC/IGE": (1.3913100883, False, EWA_EWC_IGE),
    # Entry 35, tests/test_vx_calendar_spread.py, B3
    "35 VX calendar B3": (1.457009, False, VX),
    # Entry 28, tests/test_vx_es.py
    "28 VX against ES": (1.393201, False, VX),
    # Entry 34, tests/test_calendar_spread_reversion.py
    "34 CL calendar spread": (1.278216, False, CL),
    # Entry 19, tests/test_khandani_lo_book_two.py, Examples 4.4 and 4.3
    "19 Example 4.4 opens": (4.713284, False, SP500),
    "19 Example 4.3 closes": (1.259478, False, SP500),
    # Entry 18, tests/test_buy_on_gap.py
    "18 buy on gap": (1.5371, False, SP500),
    "18 short on gap": (1.7853, False, SP500),
    # Entry 47, tests/test_vix_filter.py
    "47 buy on gap under the VIX filter": (1.417425, False, SP500),
    # Entry 46, tests/test_pead_rerun.py, its lowest and highest runs, and Entry 12
    "46 drift run A_U": (1.2815, False, SP500),
    "46 drift run B1": (1.7045, False, SP500),
    "12 drift": (1.4909, False, SP500),
    # Entry 31, tests/test_cl_reversal_momentum.py
    "31 CL reversal and momentum": (1.100368, False, CL),
    # Entry 33, tests/test_tu_momentum.py
    "33 TU momentum": (1.041462, False, TU),
    # Entry 41, tests/test_vx_es.py, with no cost at all
    "41 VX against ES on roll": (1.030894, False, VX),
    # Entry 52, measured below from the committed vintage
    "52 MomSeasonShort": (0.8096, False, MOM_SEASON),
    # Entry 11, natural gas 1994 to 2008, one ratio per yearly trade,
    # tests/test_commodity_seasonals.py
    "11 natural gas seasonal": (1.0008, False, NATURAL_GAS),
    # Entry 13, tests/test_pca_factor.py
    "13 PCA factor model": (0.5787, False, SP600),
    # Entry 30, tests/test_aud_cad_rollover.py
    "30 AUD.CAD with rollover": (0.5418018005, False, AUD_CAD),
    # trading-strategies data/gen_ledger.jsonl:62, at a 1 bp hedge
    "sibling generative 0.05 delta call": (0.688, False, SPY_CHAINS),
    # After costs, from AFTER_COST_ROWS, and Entry 10's unfilled rule A,
    # tests/test_khandani_lo.py, TestRuleAOnTheOpens::test_without_the_forward_fill
    "44b S&P 600 opens": (2.0257, True, SP600),
    "50d S&P 600 control opens": (1.6903, True, SP600),
    "10 rule A S&P 500 opens": (1.3997, True, SP500),
    "10 rule A without the fill": (1.0335, True, SP500),
    "10 rule B S&P 500 opens": (0.8293, True, SP500),
    "19 row 10 S&P 500 closes": (0.3797, True, SP500),
    "50b S&P 400 opens": (0.4884, True, SP400),
    "50c S&P 600 control closes": (0.0575, True, SP600),
}


def reaching(n: int, after_costs: bool) -> list[str]:
    """The rows whose years available reach the years needed at ``n``."""
    return sorted(
        row
        for row, (sharpe, net, spans) in SCREEN.items()
        if net is after_costs and sharpe > 0 and available(spans) >= needed(sharpe, n)
    )


class TestTheScreen:
    @pytest.mark.parametrize(
        ("row", "years_available", "years_needed"),
        [
            ("32 Kalman EWA/EWC", 24.57, 4.85),
            ("25 AUD.USD and CAD.USD", 23.60, 10.42),
            ("36 TU on lagged roll", 14.13, 8.31),
            ("40 FSTX opening gap", 20.41, 13.01),
            ("23 Johansen EWA/EWC/IGE", 18.98, 13.97),
            ("35 VX calendar B3", 14.39, 12.74),
            ("28 VX against ES", 14.39, 13.93),
            ("34 CL calendar spread", 17.72, 16.55),
            ("19 Example 4.4 opens", 32.89, 1.22),
            ("19 Example 4.3 closes", 32.89, 17.05),
            ("18 buy on gap", 32.89, 11.44),
            ("18 short on gap", 32.89, 8.48),
            ("47 buy on gap under the VIX filter", 32.89, 13.46),
            ("46 drift run A_U", 32.89, 16.47),
            ("46 drift run B1", 32.89, 9.31),
            ("12 drift", 32.89, 12.16),
            ("31 CL reversal and momentum", 17.72, 22.33),
            ("33 TU momentum", 14.13, 24.93),
            ("41 VX against ES on roll", 14.39, 25.44),
            ("52 MomSeasonShort", 38.00, 41.25),
            ("11 natural gas seasonal", 3.75, 27.00),
            ("13 PCA factor model", 9.21, 80.74),
            ("30 AUD.CAD with rollover", 23.60, 92.11),
            ("sibling generative 0.05 delta call", 14.36, 57.12),
            ("44b S&P 600 opens", 9.21, 6.59),
            ("50d S&P 600 control opens", 9.21, 9.46),
            ("10 rule A S&P 500 opens", 32.89, 13.80),
            ("10 rule A without the fill", 32.89, 25.32),
            ("10 rule B S&P 500 opens", 32.89, 39.32),
            ("19 row 10 S&P 500 closes", 32.89, 187.55),
            ("50b S&P 400 opens", 23.45, 113.36),
            ("50c S&P 600 control closes", 9.21, 8178.35),
        ],
    )
    def test_each_rows_years_available_and_needed(
        self, row: str, years_available: float, years_needed: float
    ) -> None:
        sharpe, _, spans = SCREEN[row]
        assert available(spans) == pytest.approx(years_available, abs=0.005)
        assert needed(sharpe) == pytest.approx(years_needed, abs=0.005)

    def test_the_rows_a_measurement_at_5_bp_could_make_registrable(self) -> None:
        assert reaching(N, after_costs=False) == sorted(
            [
                "32 Kalman EWA/EWC",
                "25 AUD.USD and CAD.USD",
                "36 TU on lagged roll",
                "40 FSTX opening gap",
                "23 Johansen EWA/EWC/IGE",
                "35 VX calendar B3",
                "28 VX against ES",
                "34 CL calendar spread",
                "19 Example 4.4 opens",
                "19 Example 4.3 closes",
                "18 buy on gap",
                "18 short on gap",
                "47 buy on gap under the VIX filter",
                "46 drift run A_U",
                "46 drift run B1",
                "12 drift",
            ]
        )

    def test_the_rows_that_wait_only_on_whether_the_data_can_be_bought(self) -> None:
        assert reaching(N, after_costs=True) == sorted(
            ["44b S&P 600 opens", "10 rule A S&P 500 opens", "10 rule A without the fill"]
        )

    def test_the_narrow_hurdle_adds_four_rows(self) -> None:
        added = set(reaching(N_NARROW, after_costs=False)) - set(reaching(N, after_costs=False))
        assert added == {"31 CL reversal and momentum", "52 MomSeasonShort"}
        added = set(reaching(N_NARROW, after_costs=True)) - set(reaching(N, after_costs=True))
        assert added == {"50d S&P 600 control opens", "10 rule B S&P 500 opens"}


class TestTheCrossSectionalMomentumRow:
    def test_its_sharpe_over_every_day_the_script_trades_is_negative(self) -> None:
        """Entry 17 pins three windows. Over all their days, 2007-05-15 to
        2012-04-24, the script's own reading loses, so no span can rescue it."""
        values = cross_sectional_momentum.read_closes()[1]
        days = pd.DatetimeIndex(values.index)
        daily = cross_sectional_momentum.script_as_printed(values.to_numpy(dtype=float))
        inside = (days >= pd.Timestamp("2007-05-15")) & (days <= pd.Timestamp("2012-04-24"))
        r = daily[inside]
        assert len(r) == 1247
        sharpe = np.sqrt(252) * cross_sectional_momentum.smartmean(r)
        sharpe /= cross_sectional_momentum.smartstd_book_two(r)
        assert sharpe == pytest.approx(-0.4800, abs=5e-5)


class TestTheSeasonalMomentumRow:
    def test_its_gross_sharpe_over_the_span_entry_52_read(self) -> None:
        _, series = long_short_returns("MomSeasonShort")
        loaded = series[series.index >= "1965-01-01"] / 100
        assert len(loaded) == 720
        sharpe = loaded.mean() / loaded.std() * math.sqrt(12)
        assert sharpe == pytest.approx(0.8096, abs=5e-5)

    def test_even_before_costs_1927_to_1964_falls_short(self) -> None:
        """The screen's row uses this figure, so this pins the link between them."""
        assert SCREEN["52 MomSeasonShort"][0] == 0.8096
        assert available(MOM_SEASON) < needed(0.8096)
