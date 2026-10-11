"""The pins for location 4709's claim that a levered low-beta portfolio out-compounds high beta.

This file is the single authority for every number any prose surface quotes
about [issue 275](https://github.com/l3a0/quantitative-trading/issues/275).
``docs/replication-log.md`` Entry 40 carries the verdict and points here row by
row.

Every pin on the committed files reads three vintages under one specification,
so both are stated once here and carried in every figure's failure message as
:data:`SPEC`.

- **Vintages.** ``spx_20071123/``, the 500 stocks lifted from Chan's
  ``SPX_20071123.mat``, saved 2007-11-24, read through ``load_panel``.
  ``spy_chan.csv``, the adjusted-close column of Chan's ``example6_2.xls``,
  saved 2008-01-29. FRED's TB3MS, downloaded 2026-09-30. The stock file is the
  S&P 500 as it stood on 2007-11-23, so every figure here is about survivors.
- **Specification.** :mod:`chan.low_beta_leverage` as the issue registered it
  on 2026-10-11, with the amendment of the same day. The panel cut to the days
  it shares with SPY. Betas from 252 daily excess returns with an intercept,
  at least 200 finite. The lowest and highest fifth by beta, ties by symbol,
  equal-weighted, held one month. The low fifth levered to the high fifth's
  mean beta, borrowing at the bill rate. Holding months December 2000 to
  October 2007.

The result is registered. The plan, its criterion and its first three
outcomes' wording were written on the issue before any number was computed.
The fourth outcome, ruin, is the amendment of 2026-10-11, which the owner ruled
after the build stopped on the first ruined month. So the ruin case was
settled after its first instance was visible, and the amendment names what
had been seen by then.

The figures are pinned at four decimals, which is what the log quotes. The
verdict and the ruin threshold compare unrounded values, so their tests read
the unrounded ones. It first ran here on 2026-10-11.
"""

from __future__ import annotations

import dataclasses
import math
import re

import numpy as np
import pandas as pd
import pytest
from ithildincore.stats import NeweyWestSummary

from chan import low_beta_leverage
from chan.low_beta_leverage import (
    BETA_DAYS,
    CAVEAT_LOCATION,
    CRITICAL,
    DAYS_A_YEAR,
    GROUPS,
    MIN_DAYS,
    MONTHS,
    POWER,
    PREMISE_LOCATION,
    RUIN,
    RULE_LOCATION,
    SOURCE_FILE,
    EmptyPortfolio,
    NonPositiveBeta,
    Portfolios,
    Verdict,
    build_portfolios,
    daily_excess,
    differences,
    fit_beta,
    flagged_days,
    flagged_stock_months,
    growth,
    kelly,
    main,
    read_sources,
    realised_beta,
    report,
    ruined_months,
    sharpe,
    verdict,
)
from chan.series import row_month_ends
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import LIFTED_SOURCES

SPEC = (
    "spx_20071123/ against spy_chan.csv and TB3MS dl 2026-09-30, cut to SPY's days, "
    "252-day excess-return betas with an intercept and 200 finite, lowest and highest fifth "
    "ties by symbol, equal-weighted, low levered to the high fifth's mean beta at the bill, "
    "December 2000 to October 2007, registered 2026-10-11 with that day's ruin amendment"
)

# --- the committed files -------------------------------------------------------


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def portfolios(sources) -> Portfolios:
    _, closes, _, spy, _, bills = sources
    return build_portfolios(closes, spy, bills)


@pytest.fixture(scope="module")
def result(portfolios: Portfolios) -> Verdict:
    return verdict(portfolios)


@pytest.fixture(scope="module")
def flags(sources) -> dict[str, list[pd.Timestamp]]:
    _, closes, *_ = sources
    return flagged_days(closes)


class TestTheSpecification:
    def test_the_beta_window_and_its_floor(self) -> None:
        assert (BETA_DAYS, MIN_DAYS, DAYS_A_YEAR) == (252, 200, 252)

    def test_fifths_and_months(self) -> None:
        assert (GROUPS, MONTHS) == (5, 12)

    def test_the_threshold_the_power_and_the_ruin(self) -> None:
        assert CRITICAL == 1.645
        assert POWER == 0.8416
        assert RUIN == -1.0

    def test_the_locations_are_the_revised_editions(self) -> None:
        assert (PREMISE_LOCATION, CAVEAT_LOCATION, RULE_LOCATION) == (4684, 4700, 4709)


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
    def test_the_cut_drops_13_of_2024_rows(self, sources) -> None:
        _, closes, _, spy, *_ = sources
        shared = closes.index.isin(spy.index)
        assert (len(closes), int(shared.sum()), int((~shared).sum())) == (2024, 2011, 13), SPEC
        assert pd.Timestamp("2001-09-11") in closes.index[~shared]

    def test_96_month_ends_on_the_cut_calendar(self, portfolios: Portfolios) -> None:
        ends = portfolios.month_ends
        assert len(ends) == 96, SPEC
        assert str(ends[0].date()) == "1999-11-30"
        assert str(ends[-1].date()) == "2007-10-31"

    def test_83_formations_from_2000_11_30(self, portfolios: Portfolios) -> None:
        assert len(portfolios.formed) == len(portfolios.levered) == 83, SPEC
        assert str(portfolios.formed[0].date()) == "2000-11-30"
        assert str(portfolios.formed[-1].date()) == "2007-09-28"
        assert str(portfolios.held_to[0].date()) == "2000-12-29"
        assert str(portfolios.held_to[-1].date()) == "2007-10-31"

    def test_the_first_beta_window_opens_on_1999_12_03(self, portfolios: Portfolios) -> None:
        """252 returns end at 2000-11-30, and the earliest of them lands on 1999-12-03."""
        assert str(portfolios.window_start[0].date()) == "1999-12-03", SPEC


class TestTheFigures:
    """Each figure the report prints and the log quotes, at four decimals."""

    def test_444_to_495_stocks_are_eligible(self, portfolios: Portfolios) -> None:
        assert (min(portfolios.eligible), max(portfolios.eligible)) == (444, 495), SPEC
        assert portfolios.eligible[0] == 453

    def test_each_portfolio_holds_88_to_99(self, portfolios: Portfolios) -> None:
        sizes = [len(held) for held in portfolios.low_members]
        assert sizes == [len(held) for held in portfolios.high_members]
        assert sizes == [n // 5 for n in portfolios.eligible]
        assert (min(sizes), max(sizes), sum(sizes)) == (88, 99, 7908), SPEC

    def test_the_leverage_path(self, portfolios: Portfolios) -> None:
        k = portfolios.leverage
        assert round(float(k.mean()), 4) == 7.8414, SPEC
        assert round(float(k.min()), 4) == 2.1826, SPEC
        assert round(float(k.max()), 4) == 69.0762, SPEC
        assert portfolios.formed[int(np.argmax(k.to_numpy()))] == pd.Timestamp("2001-04-30")

    def test_the_groups_mean_betas(self, portfolios: Portfolios) -> None:
        assert round(float(portfolios.low_beta.min()), 4) == 0.0280, SPEC
        assert round(float(portfolios.low_beta.max()), 4) == 0.6745, SPEC
        assert round(float(portfolios.high_beta.min()), 4) == 1.4625, SPEC
        assert round(float(portfolios.high_beta.max()), 4) == 1.9532, SPEC

    def test_each_series_realised_growth(self, portfolios: Portfolios) -> None:
        assert round(growth(portfolios.low), 4) == 0.1254, SPEC
        assert round(growth(portfolios.high), 4) == 0.1183, SPEC
        assert round(growth(portfolios.spy), 4) == 0.0379, SPEC

    def test_the_low_and_high_sharpe_ratios(self, portfolios: Portfolios) -> None:
        assert round(sharpe(portfolios.low, portfolios.rf), 4) == 1.0132, SPEC
        assert round(sharpe(portfolios.high, portfolios.rf), 4) == 0.4457, SPEC

    def test_the_realised_betas(self, portfolios: Portfolios) -> None:
        assert round(realised_beta(portfolios.low, portfolios), 4) == 0.4292, SPEC
        assert round(realised_beta(portfolios.high, portfolios), 4) == 2.0671, SPEC
        assert realised_beta(portfolios.spy, portfolios) == pytest.approx(1.0)

    def test_the_kelly_reading(self, portfolios: Portfolios) -> None:
        reading = kelly(portfolios)
        assert round(reading.leverage, 4) == 9.9884, SPEC
        assert round(reading.bill, 4) == 0.0283, SPEC
        assert round(reading.moments.levered_growth, 4) == 0.5132, SPEC
        assert round(reading.growth, 4) == 0.5415, SPEC


class TestTheVerdicts:
    def test_the_claim_is_contradicted_by_ruin(self, result: Verdict) -> None:
        assert result.by_ruin
        assert result.contradicted
        assert not result.holds
        assert result.outcome == "Contradicted by ruin"
        assert result.log_verdict == "did not reproduce"
        assert result.months == 83

    def test_two_months_are_ruined(self, result: Verdict) -> None:
        found = [
            (str(r.held_to.date()), str(r.formed.date()), round(r.leverage, 4), round(r.levered, 4))
            for r in result.ruined
        ]
        assert found == [
            ("2001-06-29", "2001-05-31", 58.0262, -2.5053),
            ("2001-09-28", "2001-08-31", 31.5098, -1.1278),
        ], SPEC

    def test_june_2001s_low_fifth_returned_minus_0_0403(self, portfolios: Portfolios) -> None:
        """An ordinary month for the unlevered low fifth, levered 58.0262 times."""
        assert round(float(portfolios.low.loc["2001-06-29"]), 4) == -0.0403, SPEC

    def test_the_wording_names_the_first_ruined_month(self, result: Verdict) -> None:
        assert result.line() == (
            "Levered to the high-beta portfolio's beta, the low-beta portfolio lost more than its "
            "capital in the month ending 2001-06-29, at a leverage of 58.0262, so its compounded "
            "growth is unbounded below and the unlevered high-beta portfolio out-compounded it."
        )

    def test_neither_t_nor_y_is_computed(self, portfolios: Portfolios, result: Verdict) -> None:
        assert result.summary is None
        with pytest.raises(ValueError, match="Newey-West statistic is not computed"):
            _ = result.t
        with pytest.raises(ValueError, match="Newey-West statistic is not computed"):
            _ = result.detectable
        with pytest.raises(ValueError, match="d is undefined"):
            differences(portfolios)


class TestTheScaleBreakDecision:
    """No window is refused, and the flagged stock-months are counted rather than dropped."""

    def test_43_flagged_days_in_34_stocks(self, flags) -> None:
        assert (sum(map(len, flags.values())), len(flags)) == (43, 34), SPEC

    def test_36_low_and_186_high_stock_months_carry_a_flag(
        self, portfolios: Portfolios, flags
    ) -> None:
        assert flagged_stock_months(portfolios, flags) == (36, 186), SPEC

    @pytest.mark.parametrize(("symbol", "restart"), [("WYN", "2006-08-01"), ("DFS", "2007-07-02")])
    def test_no_return_reaches_across_a_restart(self, sources, symbol: str, restart: str) -> None:
        """The two symbols holding two companies give no return on the day the second starts."""
        _, closes, _, spy, _, bills = sources
        cut = closes.loc[closes.index.isin(spy.index), [symbol]]
        excess = daily_excess(cut, bills)[symbol]
        assert np.isnan(excess.loc[restart])
        assert np.isnan(cut[symbol].shift(1).loc[restart])


class TestTheRun:
    def test_it_prints_the_verdict_the_side_figures_and_every_label(
        self, sources, portfolios: Portfolios, flags, capsys
    ) -> None:
        members, _, spy_entry, _, bill_entry, _ = sources
        report(members, spy_entry, bill_entry, portfolios, flagged_stock_months(portfolios, flags))
        out = capsys.readouterr().out
        assert "spx_20071123/" in out and "spy_chan.csv" in out and "tb3ms" in out
        assert "formed 2000-11-30 to 2007-09-28" in out and "83 months" in out
        assert "444 to 495 stocks per formation, each portfolio 88 to 99" in out
        assert "mean 7.8414, min 2.1826, max 69.0762" in out
        assert "CONTRADICTED BY RUIN." in out
        assert "in the month ending 2001-06-29, at a leverage of 58.0262" in out
        assert "2001-06-29     2001-05-31    58.0262   -2.5053" in out
        assert "2001-09-28     2001-08-31    31.5098   -1.1278" in out
        assert "Newey-West t and Y are not computed" in out
        assert "levered low        ruin" in out
        assert "low              0.1254   1.0132   0.4292" in out
        assert "high             0.1183   0.4457   2.0671" in out
        assert "SPY              0.0379" in out
        assert "9.9884" in out and "0.0283 + 0.5132 = 0.5415" in out
        assert "36 low and 186 high stock-months of 15816" in out
        assert "quite wary of using too much leverage" in out
        assert "about survivors" in out
        assert "amendment of 2026-10-11" in out
        assert "It is not a holdout" in out


# --- the rule, on frames built by hand -----------------------------------------

DAYS = pd.bdate_range("2000-01-03", "2001-12-31")
MONTH_KEYS = [day.strftime("%Y-%m") for day in DAYS]


def rates(rate: float = 0.0, months: dict[str, float] | None = None) -> dict[str, float]:
    """A bill rate for every month of :data:`DAYS`, with any month in ``months`` overridden."""
    return {key: rate for key in MONTH_KEYS} | (months or {})


def market_returns() -> np.ndarray:
    """A daily market return that moves, so a slope on it is defined."""
    i = np.arange(len(DAYS))
    return 0.0005 + 0.01 * (i % 3 - 1) + 0.003 * (i % 7 - 3)


def closes(returns: np.ndarray) -> pd.Series:
    """Closes from 100 whose return on each day after the first is ``returns`` on that day."""
    steps = np.concatenate([[1.0], 1 + returns[1:]])
    return pd.Series(100 * np.cumprod(steps), index=DAYS)


def spy() -> pd.Series:
    return closes(market_returns())


def stock(beta: float, bills: dict[str, float], alpha: float = 0.0) -> pd.Series:
    """Closes whose daily excess return is exactly ``alpha + beta`` times the market's."""
    rf = np.array([bills[key] for key in MONTH_KEYS]) / DAYS_A_YEAR
    return closes(rf + alpha + beta * (market_returns() - rf))


def panel(bills: dict[str, float], **betas: float) -> pd.DataFrame:
    return pd.DataFrame({symbol: stock(beta, bills) for symbol, beta in betas.items()})


def month_return(prices: pd.Series, formed: pd.Timestamp, held_to: pd.Timestamp) -> float:
    return float(prices.loc[held_to] / prices.loc[formed] - 1)


def summary(mean: float, t: float) -> NeweyWestSummary:
    return NeweyWestSummary(n=83, mean=mean, var=0.0, t_naive=0.0, t_newey_west=t, lag=3)


class TestTheRule:
    def test_the_first_formation_is_the_first_month_end_with_252_returns(self) -> None:
        bills = rates()
        p = build_portfolios(panel(bills, A=0.5, B=1.0, C=1.5, D=2.0, E=2.5), spy(), bills)
        rows = row_month_ends(DAYS)
        first = next(r for r in rows if r >= BETA_DAYS)
        assert p.formed[0] == DAYS[first] == pd.Timestamp("2000-12-29")
        assert p.window_start[0] == DAYS[first - BETA_DAYS + 1]
        assert p.held_to[-1] == DAYS[rows[-1]]

    def test_beta_is_the_slope_with_an_intercept(self) -> None:
        x = market_returns()[:BETA_DAYS]
        assert fit_beta(0.002 + 1.5 * x, x) == pytest.approx(1.5, abs=1e-12)

    def test_200_finite_days_fit_and_199_do_not(self) -> None:
        x = market_returns()[:BETA_DAYS]
        y = 0.8 * x
        y[: BETA_DAYS - MIN_DAYS] = np.nan
        assert fit_beta(y, x) == pytest.approx(0.8, abs=1e-12)
        y[BETA_DAYS - MIN_DAYS] = np.nan
        assert math.isnan(fit_beta(y, x))

    def test_a_missing_market_day_counts_against_the_200(self) -> None:
        x = market_returns()[:BETA_DAYS].copy()
        y = 0.8 * x
        y[: BETA_DAYS - MIN_DAYS] = np.nan
        x[-1] = np.nan
        assert math.isnan(fit_beta(y, x))

    def test_a_stock_short_of_200_returns_is_not_eligible(self) -> None:
        bills = rates()
        frame = panel(bills, A=0.5, B=1.0, C=1.5, D=2.0, E=2.5, F=3.0)
        p0 = build_portfolios(frame, spy(), bills)
        late = frame.copy()
        late.loc[late.index < p0.formed[0] - pd.Timedelta(days=200), "F"] = np.nan
        p = build_portfolios(late, spy(), bills)
        assert p0.eligible[0] == 6 and p.eligible[0] == 5
        assert math.isnan(p.betas.loc[p.formed[0], "F"])

    def test_a_stock_with_no_close_at_t_plus_1_is_not_eligible(self) -> None:
        bills = rates()
        frame = panel(bills, A=0.5, B=1.0, C=1.5, D=2.0, E=2.5, F=3.0)
        p0 = build_portfolios(frame, spy(), bills)
        frame.loc[p0.held_to[0], "F"] = np.nan
        p = build_portfolios(frame, spy(), bills)
        assert p.eligible[0] == 5
        assert p.high_members[0] == ("E",)

    def test_the_fifths_take_the_floor(self) -> None:
        bills = rates()
        betas = {f"S{n:02d}": 0.2 + 0.1 * n for n in range(14)}
        p = build_portfolios(panel(bills, **betas), spy(), bills)
        assert p.low_members[0] == ("S00", "S01")
        assert p.high_members[0] == ("S12", "S13")

    def test_ties_are_broken_by_symbol(self) -> None:
        """Columns out of order, so a sort that ignored the symbol would keep B and Y."""
        bills = rates()
        frame = panel(bills, Z=2.0, B=0.5, C=1.0, D=1.5, Y=2.0, A=0.5)
        p = build_portfolios(frame, spy(), bills)
        assert p.low_members[0] == ("A",)
        assert p.high_members[0] == ("Z",)

    def test_k_is_the_high_mean_beta_over_the_low(self) -> None:
        bills = rates(0.06)
        betas = {f"S{n:02d}": 0.2 + 0.1 * n for n in range(10)}
        p = build_portfolios(panel(bills, **betas), spy(), bills)
        assert p.low_beta.iloc[0] == pytest.approx((0.2 + 0.3) / 2)
        assert p.high_beta.iloc[0] == pytest.approx((1.0 + 1.1) / 2)
        assert p.leverage.iloc[0] == pytest.approx(1.05 / 0.25)

    def test_the_levered_month_borrows_at_the_holding_months_bill(self) -> None:
        bills = rates(0.06, {"2001-01": 0.12})
        frame = panel(bills, A=0.25, B=0.5, C=1.0, D=1.5, E=1.75)
        p = build_portfolios(frame, spy(), bills)
        formed, held_to = p.formed[0], p.held_to[0]
        assert held_to.strftime("%Y-%m") == "2001-01"
        r_low = month_return(frame["A"], formed, held_to)
        k = 1.75 / 0.25
        assert p.rf.iloc[0] == pytest.approx(0.01)
        assert p.low.iloc[0] == pytest.approx(r_low)
        assert p.leverage.iloc[0] == pytest.approx(k)
        assert p.levered.iloc[0] == pytest.approx(0.01 + k * (r_low - 0.01))
        assert p.high.iloc[0] == pytest.approx(month_return(frame["E"], formed, held_to))
        assert p.rf.iloc[1] == pytest.approx(0.005)

    def test_each_portfolio_is_equal_weighted(self) -> None:
        bills = rates()
        betas = {f"S{n:02d}": 0.2 + 0.1 * n for n in range(10)}
        frame = panel(bills, **betas)
        p = build_portfolios(frame, spy(), bills)
        formed, held_to = p.formed[0], p.held_to[0]
        expected = np.mean([month_return(frame[s], formed, held_to) for s in ("S00", "S01")])
        assert p.low.iloc[0] == pytest.approx(expected)

    def test_a_day_subtracts_its_months_bill_over_252(self) -> None:
        bills = rates(0.0, {"2000-02": 0.0504})
        prices = pd.DataFrame({"A": closes(market_returns())})
        excess = daily_excess(prices, bills)["A"]
        raw = prices["A"].pct_change()
        feb = excess.index.strftime("%Y-%m") == "2000-02"
        assert excess[feb].to_numpy() == pytest.approx(raw[feb].to_numpy() - 0.0504 / 252)
        assert excess[~feb].iloc[1:].to_numpy() == pytest.approx(raw[~feb].iloc[1:].to_numpy())

    def test_no_close_is_carried_forward(self) -> None:
        prices = pd.DataFrame({"A": closes(market_returns())})
        prices.iloc[10, 0] = np.nan
        excess = daily_excess(prices, rates())["A"]
        assert np.isnan(excess.iloc[10]) and np.isnan(excess.iloc[11])

    def test_a_non_positive_low_beta_raises(self) -> None:
        bills = rates()
        frame = panel(bills, A=-0.5, B=0.5, C=1.0, D=1.5, E=2.0)
        with pytest.raises(NonPositiveBeta, match="mean beta of -0.5000"):
            build_portfolios(frame, spy(), bills)

    def test_a_low_beta_of_exactly_zero_raises(self) -> None:
        bills = rates()
        frame = panel(bills, A=0.0, B=0.5, C=1.0, D=1.5, E=2.0)
        with pytest.raises(NonPositiveBeta, match="no leverage brings it"):
            build_portfolios(frame, spy(), bills)

    def test_fewer_than_five_eligible_refuses(self) -> None:
        bills = rates()
        with pytest.raises(EmptyPortfolio, match="only 4 stocks are eligible"):
            build_portfolios(panel(bills, A=0.5, B=1.0, C=1.5, D=2.0), spy(), bills)

    def test_spy_missing_a_shared_close_is_refused(self) -> None:
        bills = rates()
        market = spy()
        market.iloc[300] = np.nan
        with pytest.raises(VintageUnavailable, match="missing close"):
            build_portfolios(panel(bills, A=0.5, B=1.0, C=1.5, D=2.0, E=2.5), market, bills)

    def test_the_panel_is_cut_to_spys_days(self) -> None:
        bills = rates()
        frame = panel(bills, A=0.5, B=1.0, C=1.5, D=2.0, E=2.5)
        # A Saturday that closes September, so an uncut panel would move a month-end.
        extra = pd.DataFrame(np.nan, index=[pd.Timestamp("2000-09-30")], columns=frame.columns)
        extra.loc[:, "A"] = 1.0
        widened = pd.concat([frame, extra]).sort_index()
        assert build_portfolios(widened, spy(), bills).levered.equals(
            build_portfolios(frame, spy(), bills).levered
        )


def with_levered(p: Portfolios, values: list[float]) -> Portfolios:
    levered = pd.Series(values, index=p.levered.index)
    return dataclasses.replace(p, levered=levered, high=pd.Series(0.0, index=p.levered.index))


@pytest.fixture(scope="module")
def small() -> Portfolios:
    bills = rates()
    return build_portfolios(panel(bills, A=0.5, B=1.0, C=1.5, D=2.0, E=2.5), spy(), bills)


class TestTheCriterion:
    def test_d_is_the_log_gap(self, small: Portfolios) -> None:
        d = differences(small)
        assert d.to_numpy() == pytest.approx(
            np.log(1 + small.levered.to_numpy()) - np.log(1 + small.high.to_numpy())
        )

    def test_a_levered_return_of_exactly_minus_1_is_ruin(self, small: Portfolios) -> None:
        values = [0.01] * len(small.levered)
        values[3] = -1.0
        ruined = ruined_months(with_levered(small, values))
        assert [r.held_to for r in ruined] == [small.held_to[3]]
        result = verdict(with_levered(small, values))
        assert result.outcome == "Contradicted by ruin"
        assert f"in the month ending {small.held_to[3].date()}" in result.line()

    def test_just_above_minus_1_is_not_ruin(self, small: Portfolios) -> None:
        values = [0.01] * len(small.levered)
        values[3] = -0.9999
        result = verdict(with_levered(small, values))
        assert not result.by_ruin
        assert result.summary is not None

    def test_the_first_ruined_month_is_named(self, small: Portfolios) -> None:
        values = [0.01] * len(small.levered)
        values[2], values[5] = -1.5, -3.0
        result = verdict(with_levered(small, values))
        assert len(result.ruined) == 2
        assert str(small.held_to[2].date()) in result.line()
        assert f"{small.leverage.iloc[2]:.4f}" in result.line()

    def test_t_at_the_threshold_holds(self) -> None:
        result = Verdict(months=83, summary=summary(0.001, 1.645))
        assert result.holds and result.outcome == "Holds"
        assert result.log_verdict == "reproduced"
        assert result.line() == (
            "Levered to the high-beta portfolio's beta, the low-beta portfolio out-compounded "
            "the unlevered high-beta portfolio by 0.0120 a year, Newey-West t = 1.6450 over "
            "83 months."
        )

    def test_t_just_below_the_threshold_is_not_decided(self) -> None:
        result = Verdict(months=83, summary=summary(0.001, 1.6449))
        assert not result.holds and not result.contradicted
        assert result.outcome == "Not decided"
        assert result.log_verdict == "did not reproduce"

    def test_minus_the_threshold_contradicts(self) -> None:
        result = Verdict(months=83, summary=summary(-0.002, -1.645))
        assert result.contradicted and not result.by_ruin
        assert result.outcome == "Contradicted"
        assert result.log_verdict == "did not reproduce"
        assert result.line() == (
            "The unlevered high-beta portfolio out-compounded the levered low-beta portfolio "
            "by 0.0240 a year, Newey-West t = -1.6450 over 83 months."
        )

    def test_a_positive_mean_with_a_negative_t_is_not_decided(self) -> None:
        assert Verdict(months=83, summary=summary(0.001, -2.0)).outcome == "Not decided"

    def test_y_is_the_power_gap_times_the_standard_error_times_12(self) -> None:
        result = Verdict(months=83, summary=summary(0.001, 0.5))
        assert result.standard_error == pytest.approx(0.002)
        assert result.detectable == pytest.approx((1.645 + 0.8416) * 0.002 * 12)
        assert result.line() == (
            "No gap in compounded growth detectable above about 0.0597 a year over 83 months, "
            "where the point estimate is 0.0120."
        )

    def test_a_t_of_zero_has_no_standard_error(self) -> None:
        with pytest.raises(ValueError, match="t is 0"):
            _ = Verdict(months=83, summary=summary(0.0, 0.0)).detectable


class TestTheSideFigures:
    def test_growth_is_12_times_the_mean_log_return(self) -> None:
        assert growth(pd.Series([0.1, -0.1])) == pytest.approx(6 * (math.log(1.1) + math.log(0.9)))

    def test_sharpe_reads_the_excess_return(self) -> None:
        returns = pd.Series([0.02, 0.0, 0.03, -0.01])
        rf = pd.Series([0.01, 0.0, 0.005, 0.0])
        excess = returns - rf
        assert sharpe(returns, rf) == pytest.approx(excess.mean() / excess.std() * math.sqrt(12))

    def test_realised_beta_is_the_slope_on_spys_excess_return(self, small: Portfolios) -> None:
        series = small.rf + 0.003 + 2.0 * (small.spy - small.rf)
        assert realised_beta(series, small) == pytest.approx(2.0)

    def test_kelly_growth_is_the_bill_plus_half_the_sharpe_squared(self, small: Portfolios) -> None:
        reading = kelly(small)
        excess = small.low - small.rf
        m, s = excess.mean() * 12, excess.std() * math.sqrt(12)
        assert reading.leverage == pytest.approx(m / s**2)
        assert reading.growth == pytest.approx(small.rf.mean() * 12 + (m / s) ** 2 / 2)

    def test_a_flag_counts_from_the_window_start_to_the_holding_month_end(
        self, small: Portfolios
    ) -> None:
        start, end = small.window_start[0], small.held_to[0]
        low, high = small.low_members[0][0], small.high_members[0][0]
        before = start - pd.offsets.BDay(1)
        after = end + pd.offsets.BDay(1)
        assert flagged_stock_months(small, {low: [start]}) == (1, 0)
        assert flagged_stock_months(small, {high: [end]})[1] >= 1
        assert flagged_stock_months(small, {low: [before], high: [after]})[0] == 0
        assert flagged_stock_months(small, {"C": [start]}) == (0, 0)


class TestTheRefusals:
    @pytest.mark.parametrize(
        "refusal",
        [
            NonPositiveBeta("the low group formed 2001-05-31 has a mean beta of -0.1000"),
            EmptyPortfolio("only 4 stocks are eligible at 2000-11-30"),
            VintageUnavailable("no committed vintage is lifted from SPX_20071123.mat"),
        ],
    )
    def test_main_prints_a_refusal_as_one_line(self, monkeypatch, refusal: Exception) -> None:
        def refuse(data_dir=None):
            raise refusal

        monkeypatch.setattr(low_beta_leverage, "run", refuse)
        monkeypatch.setattr("sys.argv", ["low_beta_leverage"])
        with pytest.raises(SystemExit, match=re.escape(str(refusal))):
            main()
