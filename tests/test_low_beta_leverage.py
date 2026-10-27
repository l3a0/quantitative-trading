"""The pins for location 4709's claim that a levered low-beta portfolio out-compounds high beta.

This file is the single authority for every number any prose surface quotes
about [issue 275](https://github.com/l3a0/quantitative-trading/issues/275).
``docs/replication-log.md`` Entry 45 carries the verdict and points here row by
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
after the build found two ruined months and stopped. So the ruin case was
settled after its first instance was visible, and the amendment names what
had been seen by then.

Registration does not make the span a holdout. Chan wrote the claim in 2008
from "empirical studies", and the low-beta literature's own samples cover 1999
to 2007. Every figure beside the verdict is a point estimate nothing tests, so
it is exploratory and decides nothing.

The figures are pinned at four decimals, which is what the log quotes. The
verdict and the ruin threshold compare unrounded values, so their tests read
the unrounded ones. It first ran here on 2026-10-11.
"""

from __future__ import annotations

import dataclasses
import math
import re
from statistics import NormalDist

import numpy as np
import pandas as pd
import pytest
from ithildincore.stats import NeweyWestSummary, newey_west_summary

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
    UnreadableStandardError,
    Verdict,
    build_portfolios,
    daily_excess,
    differences,
    fit_beta,
    flagged_days,
    flagged_stock_months,
    formation_table,
    growth,
    kelly,
    levered_wealth,
    main,
    read_sources,
    realised_beta,
    report,
    ruin_line,
    ruined_months,
    ruinous_leverage,
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
    "December 2000 to October 2007, registered 2026-10-11 with that day's ruin amendment, "
    "survivors only, not a holdout"
)

AFTER_THE_RUN = "measured by the write-up after the run, so exploratory, and it decides nothing"

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

    def test_every_formations_eligible_count(self, portfolios: Portfolios) -> None:
        table = formation_table(portfolios)
        assert tuple(table["eligible"]) == (
            453,
            453,
            444,
            444,
            456,
            456,
            456,
            457,
            461,
            462,
            463,
            464,
            463,
            464,
            465,
            465,
            468,
            473,
            474,
            474,
            474,
            475,
            474,
            475,
            476,
            476,
            476,
            476,
            476,
            477,
            477,
            477,
            477,
            477,
            478,
            479,
            479,
            479,
            479,
            480,
            480,
            480,
            480,
            481,
            481,
            481,
            480,
            481,
            483,
            484,
            484,
            485,
            487,
            487,
            487,
            488,
            488,
            488,
            488,
            486,
            487,
            487,
            487,
            487,
            487,
            487,
            488,
            488,
            489,
            489,
            490,
            491,
            491,
            492,
            492,
            492,
            493,
            493,
            494,
            494,
            495,
            495,
            495,
        ), SPEC
        assert list(table["per group"]) == [n // 5 for n in table["eligible"]]

    @pytest.mark.parametrize(
        ("formed", "row"),
        [
            ("2000-11-30", (453, 90, 0.1582, 1.5537, 9.8220)),
            ("2001-04-30", (456, 91, 0.0280, 1.9349, 69.0762)),
            ("2001-05-31", (456, 91, 0.0337, 1.9532, 58.0262)),
            ("2001-08-31", (462, 92, 0.0616, 1.9422, 31.5098)),
            ("2007-09-28", (495, 99, 0.6462, 1.4847, 2.2977)),
        ],
    )
    def test_formation_table_rows(self, portfolios: Portfolios, formed: str, row: tuple) -> None:
        got = formation_table(portfolios).loc[formed]
        assert (int(got["eligible"]), int(got["per group"])) == row[:2], SPEC
        assert tuple(round(float(got[c]), 4) for c in ("low beta", "high beta", "k")) == row[2:], (
            SPEC
        )

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

    def test_the_levered_lows_beta_and_sharpe_over_all_83_months(
        self, portfolios: Portfolios
    ) -> None:
        """Each levered month read as if freshly funded, which is how the series is defined.

        The beta shows the match overshot after the fact, against the high
        fifth's 2.0671.
        """
        assert len(portfolios.levered) == 83
        assert round(realised_beta(portfolios.levered, portfolios), 4) == 3.4596, SPEC
        assert round(sharpe(portfolios.levered, portfolios.rf), 4) == 0.2836, SPEC

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
        """The sixth-worst of the unlevered low fifth's 83 months, levered 58.0262 times."""
        assert round(float(portfolios.low.loc["2001-06-29"]), 4) == -0.0403, SPEC
        worst = list(portfolios.low.sort_values().index)
        assert worst.index(pd.Timestamp("2001-06-29")) + 1 == 6, SPEC

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


def by_formation(portfolios: Portfolios, series: pd.Series) -> pd.Series:
    """A series indexed by holding month, re-keyed by the formation that set it."""
    return pd.Series(series.to_numpy(), index=pd.DatetimeIndex(portfolios.formed))


def dates(index: pd.Index) -> list[str]:
    return [str(day.date()) for day in index]


class TestWhatThePostMeasured:
    """Numbers ``blog/levered-low-beta-lessons.md`` quotes that no row of Entry 45 declared.

    The write-up measured every one of them after the run, on the vintages and
    the specification in :data:`SPEC`, so each is exploratory and none carries
    a verdict. The ruin line, the ruinous leverage and the levered wealth were
    defined after the ruined months had been seen. A beta or a leverage is named
    by its formation date, and a return or a ruin line by its holding month.
    """

    def test_the_low_fifths_beta_near_zero_in_spring_2001(self, portfolios: Portfolios) -> None:
        """Both 2000 formations sit near 0.15, and only four of 2001's fall below 0.05."""
        low = by_formation(portfolios, portfolios.low_beta)
        assert round(float(low.loc["2000-12-29"]), 4) == 0.1443, f"{SPEC}; {AFTER_THE_RUN}"
        below_5 = low[low < 0.05]
        assert {
            d: round(float(v), 4) for d, v in zip(dates(below_5.index), below_5, strict=True)
        } == {
            "2001-03-30": 0.0375,
            "2001-04-30": 0.0280,
            "2001-05-31": 0.0337,
            "2001-06-29": 0.0448,
        }, f"{SPEC}; {AFTER_THE_RUN}"
        below_10 = dates(low[low < 0.10].index)
        assert (len(below_10), below_10[0], below_10[-1]) == (9, "2001-01-31", "2001-09-28"), (
            f"{SPEC}; {AFTER_THE_RUN}"
        )
        assert below_10 == dates(low.loc["2001-01-31":"2001-09-28"].index), (
            f"{SPEC}; {AFTER_THE_RUN}"
        )

    def test_k_above_20_and_above_the_look_ahead_kelly(self, portfolios: Portfolios) -> None:
        k = by_formation(portfolios, portfolios.leverage)
        above_20 = dates(k[k > 20].index)
        assert (len(above_20), above_20[0], above_20[-1]) == (8, "2001-02-28", "2001-09-28"), (
            f"{SPEC}; {AFTER_THE_RUN}"
        )
        reading = kelly(portfolios)
        assert round(reading.leverage, 4) == 9.9884, SPEC
        above_kelly = dates(k[k > reading.leverage].index)
        assert (len(above_kelly), above_kelly[0], above_kelly[-1]) == (
            13,
            "2000-12-29",
            "2001-12-31",
        ), f"{SPEC}; {AFTER_THE_RUN}"
        assert above_kelly == dates(k.loc["2000-12-29":"2001-12-31"].index), (
            f"{SPEC}; {AFTER_THE_RUN}"
        )

    def test_the_levered_wealth_through_may_2001(self, portfolios: Portfolios) -> None:
        """1 grew to 4.8089 by the end of May 2001, through levered losses in January and March."""
        wealth = levered_wealth(portfolios.levered)
        assert round(float(wealth.loc["2001-05-31"]), 4) == 4.8089, f"{SPEC}; {AFTER_THE_RUN}"
        assert round(float(portfolios.levered.loc["2001-01-31"]), 4) == -0.5456, (
            f"{SPEC}; {AFTER_THE_RUN}"
        )
        assert round(float(portfolios.levered.loc["2001-03-30"]), 4) == -0.4516, (
            f"{SPEC}; {AFTER_THE_RUN}"
        )
        assert portfolios.held_to[0] == pd.Timestamp("2000-12-29")
        assert wealth.loc["2001-07-31":].isna().all()

    def test_may_2001s_levered_month_at_the_highest_k(self, portfolios: Portfolios) -> None:
        """Formed 2001-04-30 at k 69.0762, held to 2001-05-31, and not ruined."""
        may = pd.Timestamp("2001-05-31")
        assert round(float(portfolios.leverage.loc[may]), 4) == 69.0762, SPEC
        assert round(float(portfolios.levered.loc[may]), 4) == 1.7253, f"{SPEC}; {AFTER_THE_RUN}"
        assert round(float(portfolios.low.loc[may]), 4) == 0.0279, f"{SPEC}; {AFTER_THE_RUN}"

    def test_the_ruin_line(self, portfolios: Portfolios) -> None:
        line = ruin_line(portfolios.rf, portfolios.leverage)
        assert round(float(portfolios.rf.loc["2001-06-29"]), 4) == 0.0029, SPEC
        assert round(float(line.loc["2001-06-29"]), 4) == -0.0144, f"{SPEC}; {AFTER_THE_RUN}"
        assert round(float(line.loc["2001-09-28"]), 4) == -0.0296, f"{SPEC}; {AFTER_THE_RUN}"
        assert round(float(line.max()), 4) == -0.0115, f"{SPEC}; {AFTER_THE_RUN}"
        assert str(line.idxmax().date()) == "2001-05-31", f"{SPEC}; {AFTER_THE_RUN}"
        below = line < -0.10
        assert str(line.index[below.to_numpy()][0].date()) == "2002-02-28", (
            f"{SPEC}; {AFTER_THE_RUN}"
        )
        assert below.loc["2002-02-28":].all() and not below.loc[:"2002-01-31"].any(), (
            f"{SPEC}; {AFTER_THE_RUN}"
        )
        low = portfolios.low
        assert (round(float(low.min()), 4), str(low.idxmin().date())) == (-0.0733, "2002-07-31"), (
            f"{SPEC}; {AFTER_THE_RUN}"
        )
        assert line.loc["2002-02-28":].max() < low.min(), f"{SPEC}; {AFTER_THE_RUN}"

    def test_the_line_finds_the_same_two_ruined_months(self, portfolios: Portfolios) -> None:
        line = ruin_line(portfolios.rf, portfolios.leverage)
        found = portfolios.low.index[(portfolios.low <= line).to_numpy()]
        assert list(found) == [r.held_to for r in ruined_months(portfolios)]

    def test_september_2001s_low_fifth_was_the_eighth_worst(self, portfolios: Portfolios) -> None:
        sep = pd.Timestamp("2001-09-28")
        assert round(float(portfolios.low.loc[sep]), 4) == -0.0337, f"{SPEC}; {AFTER_THE_RUN}"
        worst = list(portfolios.low.sort_values().index)
        assert worst.index(sep) + 1 == 8, f"{SPEC}; {AFTER_THE_RUN}"

    def test_13_of_83_months_reach_junes_line(self, portfolios: Portfolios) -> None:
        """Holding June's k of 58.0262 in every month ruins the same 13."""
        june = pd.Timestamp("2001-06-29")
        line = ruin_line(portfolios.rf, portfolios.leverage).loc[june]
        reached = portfolios.low <= line
        assert (int(reached.sum()), len(reached)) == (13, 83), f"{SPEC}; {AFTER_THE_RUN}"
        k = portfolios.leverage.loc[june]
        constant = portfolios.rf + k * (portfolios.low - portfolios.rf)
        assert (constant <= RUIN).equals(reached), f"{SPEC}; {AFTER_THE_RUN}"

    def test_the_leverage_that_ruins_june_and_september(self, portfolios: Portfolios) -> None:
        needed = ruinous_leverage(portfolios.low, portfolios.rf)
        june = float(needed.loc["2001-06-29"])
        assert round(june, 4) == 23.2017, f"{SPEC}; {AFTER_THE_RUN}"
        assert 23.2017 < june < 23.2018, f"{SPEC}; {AFTER_THE_RUN}"
        asked = float(portfolios.leverage.loc["2001-06-29"])
        assert round(asked / june, 2) == 2.50, f"{SPEC}; {AFTER_THE_RUN}"
        assert round(float(needed.loc["2001-09-28"]), 4) == 27.9461, f"{SPEC}; {AFTER_THE_RUN}"

    def test_a_normal_month_as_bad_as_junes_line(self, portfolios: Portfolios) -> None:
        """The low fifth's own mean and standard deviation, ddof 1, give 0.1931."""
        mean, sd = float(portfolios.low.mean()), float(portfolios.low.std(ddof=1))
        assert (round(mean, 4), round(sd, 4)) == (0.0109, 0.0292), f"{SPEC}; {AFTER_THE_RUN}"
        line = ruin_line(portfolios.rf, portfolios.leverage).loc["2001-06-29"]
        chance = NormalDist(mean, sd).cdf(float(line))
        assert round(chance, 4) == 0.1931, f"{SPEC}; {AFTER_THE_RUN}"


class TestThePostsHelpers:
    """The three helpers the write-up added, on months whose answers are worked here."""

    MONTHS = pd.DatetimeIndex(["2001-01-31", "2001-02-28", "2001-03-30", "2001-04-30"])

    def series(self, *values: float) -> pd.Series:
        return pd.Series(values, index=self.MONTHS[: len(values)])

    def test_the_ruin_line_is_rf_less_one_plus_rf_over_k(self) -> None:
        line = ruin_line(self.series(0.01, 0.0), self.series(10.0, 4.0))
        assert line.tolist() == pytest.approx([0.01 - 1.01 / 10, -0.25], abs=1e-15)
        assert line.index.equals(self.MONTHS[:2])

    def test_a_low_return_on_the_line_levers_to_exactly_minus_1(self) -> None:
        rf, k = self.series(0.003, 0.02), self.series(58.0, 2.5)
        r = ruin_line(rf, k)
        assert (rf + k * (r - rf)).tolist() == pytest.approx([RUIN, RUIN], abs=1e-12)

    def test_the_ruinous_leverage_is_one_plus_rf_over_the_shortfall(self) -> None:
        needed = ruinous_leverage(self.series(-0.04, 0.0), self.series(0.01, 0.0))
        assert needed.iloc[0] == pytest.approx(1.01 / 0.05, abs=1e-12)
        assert needed.iloc[1] == math.inf

    def test_levering_at_the_ruinous_leverage_lands_on_minus_1(self) -> None:
        low, rf = self.series(-0.0403, -0.002), self.series(0.0029, 0.001)
        k = ruinous_leverage(low, rf)
        assert (rf + k * (low - rf)).tolist() == pytest.approx([RUIN, RUIN], abs=1e-12)

    def test_a_month_at_or_above_the_bill_cannot_be_ruined(self) -> None:
        needed = ruinous_leverage(self.series(0.01, 0.05), self.series(0.01, 0.01))
        assert needed.tolist() == [math.inf, math.inf]

    def test_wealth_compounds_with_no_ruin(self) -> None:
        wealth = levered_wealth(self.series(0.1, -0.5, 0.2))
        assert wealth.tolist() == pytest.approx([1.1, 0.55, 0.66], abs=1e-15)
        assert wealth.index.equals(self.MONTHS[:3])

    def test_wealth_stops_after_the_first_ruin(self) -> None:
        """The ruined month ends below zero, and nothing is left to lever after it."""
        wealth = levered_wealth(self.series(0.1, -0.5, -1.2, 0.3))
        assert wealth.iloc[:3].tolist() == pytest.approx([1.1, 0.55, 0.55 * -0.2], abs=1e-15)
        assert math.isnan(wealth.iloc[3])

    def test_a_month_at_exactly_minus_1_is_the_first_ruin(self) -> None:
        wealth = levered_wealth(self.series(0.5, -1.0, 0.4, -2.0))
        assert wealth.iloc[:2].tolist() == [1.5, 0.0]
        assert wealth.iloc[2:].isna().all()


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
        assert "levered low        ruin   0.2836   3.4596" in out
        assert "each month as if freshly funded" in out
        assert "low              0.1254   1.0132   0.4292" in out
        assert "high             0.1183   0.4457   2.0671" in out
        assert f"{'SPY':<14} {0.0379:>8.4f} {'':>8} {1.0:>8.4f}" in out
        assert "held to 2000-12-29 to 2007-10-31" in out
        assert "against the high portfolio's realised 0.1183." in out
        assert "9.9884, Gaussian growth there r + S^2/2 = 0.0283 + 0.5132 = 0.5415" in out
        assert "2000-11-30        453    90    0.1582     1.5537   9.8220" in out
        assert "2001-04-30        456    91    0.0280     1.9349  69.0762" in out
        assert "2007-09-28        495    99    0.6462     1.4847   2.2977" in out
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
        assert math.isnan(p.betas.loc[p.formed[0], "F"])

    @pytest.mark.parametrize("behind", [BETA_DAYS, BETA_DAYS - 1])
    def test_the_first_formation_needs_exactly_252_returns(self, behind: int) -> None:
        """A month-end with 252 returns behind it forms, and one with 251 does not."""
        bills = rates()
        frame = panel(bills, A=0.5, B=1.0, C=1.5, D=2.0, E=2.5)
        rows = row_month_ends(DAYS)
        first = next(r for r in rows if r >= BETA_DAYS)
        p = build_portfolios(frame.iloc[first - behind :], spy().iloc[first - behind :], bills)
        later = DAYS[next(r for r in rows if r > first)]
        assert p.formed[0] == (DAYS[first] if behind == BETA_DAYS else later)

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

    def test_not_decided_quotes_a_negative_estimate_and_its_months(self) -> None:
        result = Verdict(months=60, summary=summary(-0.001, -0.5))
        assert result.line() == (
            "No gap in compounded growth detectable above about 0.0597 a year over 60 months, "
            "where the point estimate is -0.0120."
        )

    def test_holds_quotes_its_months(self) -> None:
        assert "over 60 months." in Verdict(months=60, summary=summary(0.001, 2.0)).line()

    def test_a_mean_of_zero_has_no_standard_error(self) -> None:
        with pytest.raises(UnreadableStandardError, match="t of d is 0 over 83 months"):
            _ = Verdict(months=83, summary=summary(0.0, 0.0)).detectable

    def test_a_gap_that_never_varies_refuses_rather_than_crashing(self) -> None:
        result = Verdict(months=83, summary=newey_west_summary(np.full(83, 0.01)))
        assert result.t == 0
        with pytest.raises(UnreadableStandardError, match="a gap that never varies"):
            result.line()

    def test_the_run_refuses_a_gap_of_exactly_zero(self, small: Portfolios) -> None:
        """Equal returns every month make d exactly 0, so the summary's t is 0."""
        flat = dataclasses.replace(
            small,
            levered=pd.Series(0.01, index=small.levered.index),
            high=pd.Series(0.01, index=small.levered.index),
        )
        with pytest.raises(UnreadableStandardError, match="mean of exactly 0"):
            verdict(flat)


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
            UnreadableStandardError("the Newey-West t of d is 0 over 83 months"),
            VintageUnavailable("no committed vintage is lifted from SPX_20071123.mat"),
        ],
    )
    def test_main_prints_a_refusal_as_one_line(self, monkeypatch, refusal: Exception) -> None:
        def refuse(data_dir=None):
            raise refusal

        monkeypatch.setattr(low_beta_leverage, "run", refuse)
        monkeypatch.setattr("sys.argv", ["low_beta_leverage"])
        with pytest.raises(SystemExit, match=re.escape(str(refusal))) as exited:
            main()
        assert exited.value.code == str(refusal)


class TestTheUnruinedReport:
    """The report's branch for a run with no ruined month, on a synthetic panel."""

    def test_it_prints_d_t_lag_y_and_every_levered_figure(
        self, sources, small: Portfolios, capsys
    ) -> None:
        members, _, spy_entry, _, bill_entry, _ = sources
        result = verdict(small)
        assert not result.by_ruin
        report(members, spy_entry, bill_entry, small, (0, 0))
        out = capsys.readouterr().out
        assert (
            f"mean x 12 {result.gap:.4f}, Newey-West t {result.t:.4f} at lag {result.lag}, "
            f"Y {result.detectable:.4f}"
        ) in out
        assert (
            f"{'levered low':<14} {growth(small.levered):>8.4f} "
            f"{sharpe(small.levered, small.rf):>8.4f} {realised_beta(small.levered, small):>8.4f}\n"
        ) in out
        assert "registered before any number" in out
        assert "not computed" not in out
