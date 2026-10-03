"""The pins for the market and momentum factors, and for location 4014's claim about them.

This file is the single authority for every number any prose surface quotes
about [issue 22](https://github.com/l3a0/quantitative-trading/issues/22).
``docs/replication-log.md`` Entry 13 carries the verdicts and points here row
by row.

Every pin on the committed files reads three vintages under one specification,
so both are stated once here and carried in every figure's failure message as
:data:`SPEC`.

- **Vintages.** ``spx_20071123/``, the 500 stocks lifted from Chan's
  ``SPX_20071123.mat``, saved 2007-11-24, read through ``load_panel``.
  ``spy_chan.csv``, the adjusted-close column of Chan's ``example6_2.xls``,
  saved 2008-01-29. FRED's TB3MS, downloaded 2026-09-30. The stock file is the
  S&P 500 as it stood on 2007-11-23, so every figure touching the stocks, WML
  among them, is a figure about survivors.
- **Specification.** :mod:`chan.momentum_factor` as the issue fixed it. Month-
  ends by Chan's row rule. A past return from the close at t − 12 to the close
  at t − 1. Winners and losers by its sign. Eligibility on a finite close at all
  14 month-ends from t − 12 to t + 1. Equal weights, one month held, no costs.
  MKT is SPY's month return less TB3MS over 12. Holding months December 2000 to
  October 2007. The statistic is ``Series.autocorr(lag=1)``, and the comparison
  set is every stock with a finite return in all 83 holding months.

The figures are pinned at four decimals, which is what the log quotes. The two
verdicts compare unrounded values, so their tests read the unrounded ones.

Exploratory. Testing a claim someone else chose spends the 2000 to 2007 sample
on it. It first ran here on 2026-10-03.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from chan import momentum_factor
from chan.momentum_factor import (
    CLAIM_LOCATION,
    CRITICAL,
    FIRST_FORMATION,
    LAST_FORMATION,
    LOOKBACK,
    MARKET_LOCATION,
    SKIP,
    SOURCE_FILE,
    WML_LOCATION,
    Comparison,
    EmptyLeg,
    Factors,
    Verdict,
    annual_mean,
    autocorrelations,
    build_factors,
    main,
    read_sources,
    report,
    t_statistic,
    verdicts,
)
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import LIFTED_SOURCES

SPEC = (
    "spx_20071123/ against spy_chan.csv and TB3MS dl 2026-09-30, sign split on t-12 to t-1, "
    "14 closes for eligibility, equal-weighted, held one month, December 2000 to October 2007, "
    "Series.autocorr(lag=1)"
)

# --- the committed files -------------------------------------------------------


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def factors(sources) -> Factors:
    _, closes, _, spy, _, bills = sources
    return build_factors(closes, spy, bills)


@pytest.fixture(scope="module")
def comparison(factors) -> Comparison:
    return autocorrelations(factors)


class TestTheSpecification:
    def test_the_lookback_skips_the_latest_month(self) -> None:
        assert (LOOKBACK, SKIP) == (12, 1)

    def test_the_window_and_the_band_are_the_issues(self) -> None:
        assert FIRST_FORMATION == pd.Timestamp("2000-11-30")
        assert LAST_FORMATION == pd.Timestamp("2007-09-28")
        assert CRITICAL == 1.96

    def test_the_locations_are_the_revised_editions(self) -> None:
        assert (MARKET_LOCATION, WML_LOCATION, CLAIM_LOCATION) == (3978, 4004, 4014)


class TestTheVintages:
    def test_the_stocks_are_chans_sp500_file(self, sources) -> None:
        members, closes, *_ = sources
        vendor, basis, saved, folder, count = LIFTED_SOURCES[SOURCE_FILE]
        assert {(m.vendor, m.price_basis, m.obtained) for m in members} == {(vendor, basis, saved)}
        assert {m.path.split("/")[0] for m in members} == {folder}
        assert len(members) == closes.shape[1] == count == 500

    def test_the_market_is_chans_spy_column(self, sources) -> None:
        _, _, spy_entry, *_ = sources
        assert spy_entry.path == "spy_chan.csv"
        assert (spy_entry.vendor, spy_entry.price_basis) == ("chan-xls", "adjusted")
        assert spy_entry.obtained == "2008-01-29"

    def test_the_bills_are_the_september_download(self, sources) -> None:
        *_, bill_entry, _ = sources
        assert (bill_entry.vendor, bill_entry.symbol) == ("fred", "TB3MS")
        assert bill_entry.obtained == "2026-09-30"


class TestTheCalendar:
    def test_96_month_ends_by_chans_row_rule(self, factors: Factors) -> None:
        ends = factors.month_ends
        assert len(ends) == 96, SPEC
        assert str(ends[0].date()) == "1999-11-30"
        assert str(ends[-1].date()) == "2007-10-31"

    def test_83_formations_held_from_december_2000_to_october_2007(self, factors: Factors) -> None:
        assert len(factors.formed) == len(factors.mkt) == len(factors.wml) == 83, SPEC
        assert str(factors.held_to[0].date()) == "2000-12-29"
        assert str(factors.held_to[-1].date()) == "2007-10-31"

    def test_the_formations_last_close_is_the_month_before(self, factors: Factors) -> None:
        """The skip. A lookback ending at t rather than t − 1 moves WML."""
        ends = list(factors.month_ends)
        for formed, start, stop, held in zip(
            factors.formed,
            factors.lookback_start,
            factors.lookback_end,
            factors.held_to,
            strict=True,
        ):
            t = ends.index(formed)
            assert stop == ends[t - 1]
            assert start == ends[t - 12]
            assert held == ends[t + 1]


class TestTheLegs:
    def test_442_to_494_stocks_are_eligible(self, factors: Factors) -> None:
        assert (min(factors.eligible), max(factors.eligible)) == (442, 494), SPEC

    def test_the_winner_and_loser_legs_sizes(self, factors: Factors) -> None:
        assert (min(factors.winners), max(factors.winners)) == (79, 468), SPEC
        assert (min(factors.losers), max(factors.losers)) == (11, 397), SPEC

    def test_446_stocks_are_priced_in_every_holding_month(self, comparison: Comparison) -> None:
        assert len(comparison.stocks) == 446, SPEC
        assert comparison.months == 83


class TestTheFigures:
    """Each figure the report prints and the log quotes, at four decimals."""

    def test_mkts_autocorrelation(self, comparison: Comparison) -> None:
        assert round(comparison.mkt, 4) == 0.0675, SPEC

    def test_wmls_autocorrelation(self, comparison: Comparison) -> None:
        assert round(comparison.wml, 4) == -0.1099, SPEC

    def test_the_stocks_quartiles(self, comparison: Comparison) -> None:
        assert round(comparison.lower_quartile, 4) == -0.1198, SPEC
        assert round(comparison.median, 4) == -0.0392, SPEC
        assert round(comparison.upper_quartile, 4) == 0.0402, SPEC

    def test_the_median_is_not_the_mean(self, comparison: Comparison) -> None:
        """The criterion reads the median, and the mean of the 446 rounds elsewhere."""
        assert round(float(comparison.stocks.mean()), 4) == -0.0382
        assert round(comparison.median, 4) != round(float(comparison.stocks.mean()), 4)

    def test_each_factors_percentile_among_the_stocks(self, comparison: Comparison) -> None:
        assert int((comparison.stocks < comparison.mkt).sum()) == 360
        assert int((comparison.stocks < comparison.wml).sum()) == 124
        assert round(comparison.percentile(comparison.mkt), 4) == 80.7175, SPEC
        assert round(comparison.percentile(comparison.wml), 4) == 27.8027, SPEC

    def test_each_factors_annual_mean_and_t_statistic(self, factors: Factors) -> None:
        assert round(annual_mean(factors.mkt), 4) == 0.0185, SPEC
        assert round(t_statistic(factors.mkt), 4) == 0.3660, SPEC
        assert round(annual_mean(factors.wml), 4) == 0.0241, SPEC
        assert round(t_statistic(factors.wml), 4) == 0.4505, SPEC


class TestTheVerdicts:
    """One test per factor, named for its outcome, stating which half held."""

    def test_mkt_holds_above_zero_and_above_the_median_stock(self, comparison: Comparison) -> None:
        mkt, _ = verdicts(comparison)
        assert mkt.factor == "MKT"
        assert mkt.above_zero
        assert mkt.above_median
        assert mkt.holds

    def test_wml_does_not_hold_on_either_half(self, comparison: Comparison) -> None:
        _, wml = verdicts(comparison)
        assert wml.factor == "WML"
        assert not wml.above_zero
        assert not wml.above_median
        assert not wml.holds

    def test_both_are_judged_against_the_median(self, comparison: Comparison) -> None:
        for verdict in verdicts(comparison):
            assert verdict.median == comparison.median


class TestTheBand:
    def test_the_band_is_1_96_over_root_83(self, comparison: Comparison) -> None:
        assert round(comparison.band, 4) == 0.2151
        assert comparison.band == CRITICAL / math.sqrt(83)

    def test_neither_factor_falls_outside_it(self, comparison: Comparison) -> None:
        assert not comparison.outside_band(comparison.mkt)
        assert not comparison.outside_band(comparison.wml)


class TestTheScaleBreakDecision:
    """WYN and DFS each hold two companies across a gap, and no formation reads across it.

    These read the committed closes against the 14-close rule.
    ``TestTheRule::test_a_missing_close_inside_the_14_excludes_the_stock`` is
    what holds the module to that rule.
    """

    @pytest.mark.parametrize(("symbol", "restart"), [("WYN", "2006-08-01"), ("DFS", "2007-07-02")])
    def test_no_eligible_window_spans_the_restart(
        self, sources, factors: Factors, symbol: str, restart: str
    ) -> None:
        _, closes, *_ = sources
        at_ends = closes[symbol].loc[factors.month_ends]
        ends = list(factors.month_ends)
        spanning = 0
        for formed in factors.formed:
            t = ends.index(formed)
            window = at_ends.iloc[t - LOOKBACK : t + 2]
            if window.notna().all():
                assert (window.index >= restart).all() or (window.index < restart).all()
            elif window.index[0] < pd.Timestamp(restart) <= window.index[-1]:
                spanning += 1
        assert spanning > 0


class TestTheRun:
    def test_it_prints_every_figure_both_verdicts_and_both_labels(
        self, sources, factors: Factors, comparison: Comparison, capsys
    ) -> None:
        members, _, spy_entry, _, bill_entry, _ = sources
        report(members, spy_entry, bill_entry, factors, comparison)
        out = capsys.readouterr().out
        assert "spx_20071123/" in out and "spy_chan.csv" in out and "tb3ms" in out
        assert "442 to 494 stocks per formation" in out
        assert "winners 79 to 468, losers 11 to 397" in out
        for figure in ("0.0675", "-0.1099", "-0.1198", "-0.0392", "0.0402", "80.72", "27.80"):
            assert figure in out
        assert "Claim for MKT, location 4014" in out
        assert "HOLDS. Above 0 and above the median stock" in out
        assert (
            'Claim for WML, location 4014, factor returns "often" have stronger serial '
            "autocorrelation than stocks: DOES NOT HOLD. Neither above 0 nor above the median stock"
        ) in out
        assert "= 0.2151" in out and "Outside it: neither factor." in out
        assert "about survivors" in out
        assert "Exploratory." in out


# --- the rule, on frames built by hand -----------------------------------------

DAYS = pd.bdate_range("1999-11-01", "2007-11-23")
MONTHS = DAYS.to_period("M")


def by_month(values: dict[str, float], default: float) -> pd.Series:
    """A daily series holding one value through each calendar month."""
    return pd.Series([values.get(str(m), default) for m in MONTHS], index=DAYS)


def path(rate: float) -> pd.Series:
    """Closes compounding at ``rate`` a month, constant within each month."""
    periods = sorted(set(MONTHS))
    return pd.Series([(1 + rate) ** periods.index(m) for m in MONTHS], index=DAYS, dtype=float)


def wobble(rate: float) -> pd.Series:
    """Closes whose monthly return cycles about ``rate``, so its autocorrelation is defined."""
    periods = sorted(set(MONTHS))
    steps = np.cumprod([1.0] + [1 + rate + 0.01 * (i % 3 - 1) for i in range(len(periods) - 1)])
    return pd.Series([steps[periods.index(m)] for m in MONTHS], index=DAYS)


def bills(rate: float = 0.06) -> dict[str, float]:
    return {str(m): rate for m in sorted(set(MONTHS))}


def frame(**stocks: pd.Series) -> pd.DataFrame:
    return pd.DataFrame(stocks)


class TestTheRule:
    def test_the_hand_built_calendar_is_the_panels(self) -> None:
        f = build_factors(frame(UP=path(0.01), DN=path(-0.01)), path(0.01), bills())
        assert len(f.month_ends) == 96
        assert len(f.formed) == 83

    def test_wml_is_the_winners_mean_less_the_losers(self) -> None:
        f = build_factors(frame(A=path(0.02), B=path(0.01), C=path(-0.01)), path(0.0), bills())
        assert f.winners[0] == 2 and f.losers[0] == 1
        assert f.wml.iloc[0] == pytest.approx((0.02 + 0.01) / 2 - (-0.01))

    def test_mkt_is_spys_month_less_a_twelfth_of_the_bill(self) -> None:
        f = build_factors(frame(A=path(0.02), C=path(-0.01)), path(0.01), bills(0.06))
        assert f.mkt.to_numpy() == pytest.approx(np.full(83, 0.01 - 0.06 / 12))

    def test_the_bill_is_the_holding_months(self) -> None:
        rates = bills(0.0)
        rates["2000-12"] = 0.12
        f = build_factors(frame(A=path(0.02), C=path(-0.01)), path(0.0), rates)
        assert f.mkt.iloc[0] == pytest.approx(-0.01)
        assert f.mkt.iloc[1] == pytest.approx(0.0)

    def test_the_month_before_formation_does_not_rank(self) -> None:
        """A stock up for eleven months and crashing in the twelfth is still a winner."""
        crash = path(0.05).copy()
        crash[MONTHS >= pd.Period("2000-11", "M")] *= 0.1
        f = build_factors(frame(A=crash, B=path(0.02), C=path(-0.01)), path(0.0), bills())
        assert (f.winners[0], f.losers[0]) == (2, 1)

    def test_a_past_return_of_zero_is_in_neither_leg(self) -> None:
        f = build_factors(frame(A=path(0.02), FLAT=path(0.0), C=path(-0.01)), path(0.0), bills())
        assert (f.winners[0], f.losers[0], f.eligible[0]) == (1, 1, 3)

    def test_a_missing_close_inside_the_14_excludes_the_stock(self) -> None:
        """A gap mid-lookback counts, not only one at the four closes the returns read."""
        gap = path(0.03).copy()
        gap[MONTHS == pd.Period("2000-05", "M")] = np.nan
        f = build_factors(frame(A=path(0.02), GAP=gap, C=path(-0.01)), path(0.0), bills())
        assert f.eligible[:8] == (2, 2, 2, 2, 2, 2, 2, 3)

    def test_an_empty_leg_refuses_and_names_the_month(self) -> None:
        with pytest.raises(EmptyLeg, match="loser leg is empty for the month ending 2000-12-29"):
            build_factors(frame(A=path(0.02), B=path(0.01)), path(0.0), bills())

    def test_spy_missing_a_month_end_is_refused(self) -> None:
        spy = path(0.01).drop(pd.Timestamp("2003-06-30"))
        with pytest.raises(VintageUnavailable, match="first 2003-06-30"):
            build_factors(frame(A=path(0.02), C=path(-0.01)), spy, bills())

    def test_the_comparison_set_drops_a_stock_missing_any_holding_month(self) -> None:
        gap = wobble(0.03).copy()
        gap[MONTHS == pd.Period("2005-03", "M")] = np.nan
        f = build_factors(frame(A=wobble(0.02), GAP=gap, C=wobble(-0.01)), wobble(0.0), bills())
        stocks = autocorrelations(f).stocks
        assert list(stocks.index) == ["A", "C"]
        assert np.isfinite(stocks).all()

    def test_the_statistic_is_the_lag_1_autocorrelation(self) -> None:
        series = pd.Series([1.0, -1.0] * 10 + [1.0, 2.0])
        assert series.autocorr(lag=1) == pytest.approx(
            np.corrcoef(series.to_numpy()[1:], series.to_numpy()[:-1])[0, 1]
        )


class TestTheCriterion:
    def test_above_both_holds(self) -> None:
        assert Verdict("X", 0.1, 0.0).holds

    def test_above_zero_alone_does_not(self) -> None:
        verdict = Verdict("X", 0.1, 0.2)
        assert not verdict.holds
        assert verdict.line() == "DOES NOT HOLD. Above 0, but not above the median stock"

    def test_above_the_median_alone_does_not(self) -> None:
        verdict = Verdict("X", -0.1, -0.2)
        assert not verdict.holds
        assert verdict.line() == "DOES NOT HOLD. Above the median stock, but not above 0"

    def test_equal_to_the_median_is_not_above_it(self) -> None:
        assert not Verdict("X", 0.1, 0.1).holds

    def test_zero_is_not_above_zero(self) -> None:
        assert not Verdict("X", 0.0, -0.1).holds

    def test_the_percentile_counts_strictly_below(self) -> None:
        comparison = Comparison(
            mkt=0.0, wml=0.0, stocks=pd.Series([-1.0, 0.0, 1.0, 2.0]), months=83
        )
        assert comparison.percentile(0.0) == 25.0
        assert comparison.median == 0.5


class TestTheRefusals:
    def test_main_prints_an_empty_leg_as_one_line(self, monkeypatch) -> None:
        def refuse(data_dir=None):
            raise EmptyLeg("the loser leg is empty for the month ending 2000-12-29")

        monkeypatch.setattr(momentum_factor, "run", refuse)
        monkeypatch.setattr("sys.argv", ["momentum_factor"])
        with pytest.raises(SystemExit, match="loser leg is empty for the month ending 2000-12-29"):
            main()

    def test_main_prints_a_missing_vintage_as_one_line(self, monkeypatch) -> None:
        def refuse(data_dir=None):
            raise VintageUnavailable("no committed vintage is lifted from SPX_20071123.mat")

        monkeypatch.setattr(momentum_factor, "run", refuse)
        monkeypatch.setattr("sys.argv", ["momentum_factor"])
        with pytest.raises(SystemExit, match="no committed vintage is lifted from SPX_20071123"):
            main()
