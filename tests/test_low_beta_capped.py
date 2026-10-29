"""The pins for location 4709's low-beta rule at leverage a broker would lend. Exploratory.

This file is the single authority for every number any prose surface quotes
about [issue 516](https://github.com/l3a0/quantitative-trading/issues/516),
apart from the Entry 45 figures it reads unchanged, which
``tests/test_low_beta_leverage.py`` pins.
``docs/replication-log.md`` Entry 48 carries the result and points here row by
row.

Every pin on the committed files reads three vintages under one specification
and one ceiling, so the vintages and the specification are stated once here
and carried, with the ceiling, in every figure's failure message through
:func:`spec`.

- **Vintages.** ``spx_20071123/``, the 500 stocks lifted from Chan's
  ``SPX_20071123.mat``, chan-mat adjusted, saved 2007-11-24, read through
  ``load_panel``. ``spy_chan.csv``, the adjusted-close column of Chan's
  ``example6_2.xls``, chan-xls adjusted, saved 2008-01-29. FRED's TB3MS,
  downloaded 2026-09-30. The stock file is the S&P 500 as it stood on
  2007-11-23, carried backwards, so every figure here is about survivors,
  apart from the earlier company's prices WYN, DFS and SE also carry.
- **Specification.** :mod:`chan.low_beta_capped` as the issue's plan fixed it
  on 2026-10-11 before any capped number. Entry 45's portfolios unchanged,
  the low fifth levered by min(k, C) at the bill rate, d against the unlevered
  high fifth from December 2000 to October 2007, Newey-West at the default
  lag, and Benjamini-Hochberg at 0.05 across the two ceilings in each
  direction.

**Every result here is exploratory.** Entry 45's calendar, its leverage path,
the ruin at the beta match, eight months of both groups' returns and its side
figures were seen before either ceiling was chosen. The side figures are both
Sharpe ratios, the growths, the realised betas and the full-sample Kelly
leverage of 9.9884. So no figure here confirms anything. Entry 45's own figures are
read from :mod:`chan.low_beta_leverage` rather than pinned again here, because
``tests/test_low_beta_leverage.py`` already pins them.

The figures are pinned at four decimals, which is what the log quotes. The
outcomes compare unrounded values, so their tests read the unrounded ones. It
first ran here on 2026-10-11.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from ithildincore.stats import NeweyWestSummary, newey_west_summary

from chan import low_beta_capped
from chan.low_beta_capped import (
    CEILINGS,
    FALSE_DISCOVERY,
    MARGIN_LOCATION,
    MAX_HALVINGS,
    MAX_SPREAD,
    RETAIL_LOCATION,
    RUINED_P,
    Capped,
    NoBreakEven,
    Outcome,
    assess,
    break_even_spread,
    cap,
    capped,
    charged_gap,
    decide,
    five_percent_line,
    main,
    report,
    yearly_standard_error,
)
from chan.low_beta_leverage import (
    CRITICAL,
    POWER,
    EmptyPortfolio,
    NonPositiveBeta,
    Portfolios,
    UnreadableStandardError,
    build_portfolios,
    growth,
    kelly,
    read_sources,
    realised_beta,
    ruined_months,
    ruinous_leverage,
)
from chan.pca_factor_momentum import one_sided_p
from chan.vintage import VintageUnavailable

POST = Path(__file__).resolve().parents[1] / "blog" / "capped-low-beta-lessons.md"

SPEC = (
    "spx_20071123/ chan-mat adjusted saved 2007-11-24 against spy_chan.csv chan-xls adjusted "
    "saved 2008-01-29 and TB3MS dl 2026-09-30, Entry 45's portfolios unchanged, low fifth "
    "levered by min(k, C) at the bill, d against the unlevered high fifth December 2000 to "
    "October 2007, Newey-West default lag, Benjamini-Hochberg 0.05 across ceilings 2 and 5 in "
    "each direction, planned 2026-10-11 before any capped number, exploratory, survivors only, "
    "not a holdout"
)


AFTER_THE_RUN = "measured by the write-up after the run, so exploratory, and it decides nothing"


def spec(ceiling: float) -> str:
    """:data:`SPEC` with the ceiling a pin reads."""
    return f"{SPEC}, ceiling {ceiling:g}"


# --- the committed files -------------------------------------------------------


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def portfolios(sources) -> Portfolios:
    _, closes, _, spy, _, bills = sources
    return build_portfolios(closes, spy, bills)


@pytest.fixture(scope="module")
def outcomes(portfolios: Portfolios) -> dict[float, Outcome]:
    return {o.capped.ceiling: o for o in assess(portfolios)}


class TestTheSpecification:
    def test_the_two_ceilings(self) -> None:
        assert CEILINGS == (2.0, 5.0)

    def test_the_false_discovery_rate_and_the_ruined_p(self) -> None:
        assert FALSE_DISCOVERY == 0.05
        assert RUINED_P == 1.0

    def test_the_locations_are_the_revised_editions(self) -> None:
        assert (MARGIN_LOCATION, RETAIL_LOCATION) == (814, 2836)


class TestTheCommittedFiles:
    """Each figure the report prints and the log quotes, at four decimals."""

    @pytest.mark.parametrize("ceiling", CEILINGS)
    def test_no_month_is_ruined_at_either_ceiling(self, outcomes, ceiling: float) -> None:
        assert outcomes[ceiling].capped.ruined == (), spec(ceiling)

    @pytest.mark.parametrize("ceiling", CEILINGS)
    def test_both_ceilings_are_not_decided(self, outcomes, ceiling: float) -> None:
        o = outcomes[ceiling]
        assert o.outcome == "Not decided", spec(ceiling)
        assert (o.claim_rejected, o.contrary_rejected) == (False, False), spec(ceiling)

    @pytest.mark.parametrize(
        ("ceiling", "figures"),
        [
            (2.0, (0.0934, 1.0715, 0.1420, 0.8580, 0.2168)),
            (5.0, (0.1659, 1.2111, 0.1129, 0.8871, 0.3407)),
        ],
    )
    def test_the_gap_t_both_p_values_and_y(self, outcomes, ceiling: float, figures) -> None:
        c = outcomes[ceiling].capped
        got = (c.gap, c.t, c.p_claim, c.p_contrary, c.detectable)
        assert tuple(round(x, 4) for x in got) == figures, spec(ceiling)
        assert (c.lag, c.months) == (3, 83), spec(ceiling)

    @pytest.mark.parametrize(
        ("ceiling", "line"),
        [
            (
                2.0,
                "At a ceiling of 2, no gap in compounded growth detectable above about 0.2168 a "
                "year over 83 months, where the point estimate is 0.0934.",
            ),
            (
                5.0,
                "At a ceiling of 5, no gap in compounded growth detectable above about 0.3407 a "
                "year over 83 months, where the point estimate is 0.1659.",
            ),
        ],
    )
    def test_each_outcome_line(self, outcomes, ceiling: float, line: str) -> None:
        assert outcomes[ceiling].line() == line, spec(ceiling)

    @pytest.mark.parametrize(
        ("ceiling", "figures"),
        [(2.0, (0.2118, 2.0, 83, 0.8584)), (5.0, (0.2843, 3.5134, 20, 1.5831))],
    )
    def test_growth_mean_leverage_binding_months_and_beta(
        self, outcomes, ceiling: float, figures
    ) -> None:
        c = outcomes[ceiling].capped
        got = (
            round(c.realised_growth, 4),
            round(c.mean_leverage, 4),
            c.binds,
            round(c.realised_beta, 4),
        )
        assert got == figures, spec(ceiling)

    @pytest.mark.parametrize(
        ("ceiling", "worst"),
        [
            (2.0, ("2002-07-31", "2002-06-28", 2.0, -0.1479)),
            (5.0, ("2002-07-31", "2002-06-28", 5.0, -0.3719)),
        ],
    )
    def test_the_worst_month(self, outcomes, ceiling: float, worst) -> None:
        w = outcomes[ceiling].capped.worst()
        got = (
            str(w.held_to.date()),
            str(w.formed.date()),
            round(w.leverage, 4),
            round(w.capped, 4),
        )
        assert got == worst, spec(ceiling)

    @pytest.mark.parametrize(("ceiling", "spread"), [(2.0, 0.0946), (5.0, 0.0661)])
    def test_the_break_even_spread(self, outcomes, ceiling: float, spread: float) -> None:
        c = outcomes[ceiling].capped
        found = break_even_spread(c.portfolios)
        assert round(found, 4) == spread, spec(ceiling)
        assert charged_gap(c.portfolios, found) == pytest.approx(0.0, abs=1e-9)

    def test_ceiling_2_is_a_constant_leverage_of_2(self, outcomes) -> None:
        """k never falls below 2 on this panel, which the plan said before any capped number."""
        leverage = outcomes[2.0].capped.portfolios.leverage
        assert (leverage == 2.0).all(), spec(2.0)

    def test_the_beta_match_sets_the_leverage_in_63_months_at_ceiling_5(self, outcomes) -> None:
        """k is at or below 5 in 63 of the 83 months, so there L is k rather than the ceiling."""
        c = outcomes[5.0].capped
        assert int((c.k <= 5.0).sum()) == 63, spec(5.0)
        assert c.portfolios.leverage[c.k <= 5.0].equals(c.k[c.k <= 5.0]), spec(5.0)

    def test_the_capped_series_are_entry_45s_with_two_fields_replaced(
        self, portfolios: Portfolios, outcomes
    ) -> None:
        for ceiling, o in outcomes.items():
            p = o.capped.portfolios
            assert p.low is portfolios.low and p.high is portfolios.high, spec(ceiling)
            assert p.leverage.equals(portfolios.leverage.clip(upper=ceiling)), spec(ceiling)


class TestTheRun:
    def test_it_prints_every_outcome_side_figure_and_label(
        self, sources, portfolios: Portfolios, capsys
    ) -> None:
        members, _, spy_entry, _, bill_entry, _ = sources
        report(members, spy_entry, bill_entry, portfolios)
        out = capsys.readouterr().out
        assert out.startswith("EXPLORATORY.")
        assert "spx_20071123/" in out and "spy_chan.csv" in out and "tb3ms" in out
        assert "formed 2000-11-30 to 2007-09-28" in out and "83 months" in out
        assert "Ceiling 2: NOT DECIDED, exploratory." in out
        assert "Ceiling 5: NOT DECIDED, exploratory." in out
        assert "where the point estimate is 0.0934." in out
        assert "where the point estimate is 0.1659." in out
        assert "mean x 12 0.0934, Newey-West t 1.0715 at lag 3" in out
        assert "mean x 12 0.1659, Newey-West t 1.2111 at lag 3" in out
        assert "claim 0.1420, rejected no. Contrary 0.8580, rejected no." in out
        assert "claim 0.1129, rejected no. Contrary 0.8871, rejected no." in out
        assert (
            "  2          0.2118   2.0000     83   0.8584   0.0946   2002-07-31, formed "
            "2002-06-28, L 2.0000, return -0.1479"
        ) in out
        assert (
            "  5          0.2843   3.5134     20   1.5831   0.0661   2002-07-31, formed "
            "2002-06-28, L 5.0000, return -0.3719"
        ) in out
        assert (
            f"Entry 45, unlevered: low growth {growth(portfolios.low):.4f}, high growth "
            f"{growth(portfolios.high):.4f}, high beta "
            f"{realised_beta(portfolios.high, portfolios):.4f}"
        ) in out
        assert "quite wary of using too much leverage on normally low-beta stocks" in out
        for label in ("Exploratory.", "Survivor-only.", "Not a holdout.", "bill rate flatters"):
            assert label in out
        assert (
            "1. Exploratory. Entry 45's calendar, its leverage path, the ruin, eight months of "
            "both groups' returns and its side figures,"
        ) in out
        assert (
            "both Sharpe ratios, the growths, the realised betas and the full-sample Kelly "
            "leverage, were seen before either ceiling was chosen."
        ) in out
        assert (
            "5. No margin call inside a month is modelled. Under FINRA Rule 4210's 25 percent "
            "maintenance margin, a position levered 2"
        ) in out
        assert (
            "gets a call after a fall of a third within the month, and month-end closes cannot "
            "see that."
        ) in out
        assert "Entry 48" in out
        # The report lines that print figures, each read whole.
        assert (
            "  window   formed 2000-11-30 to 2007-09-28, held to 2000-12-29 to 2007-10-31, "
            "83 months\n"
        ) in out
        assert "k the beta match of location 4684, C each ceiling of location 814: 2, 5\n" in out
        assert "  Claim, location 4709, " in out
        assert "  Location 4700: " in out
        assert "  Ceilings from locations 814 and 2836. " in out
        assert "return over all 83 months, each freshly funded." in out
        assert "Benjamini-Hochberg at q = 0.05 across the 2 ceilings, run" in out
        for y in ("0.2168", "0.3407"):
            assert (
                f"  Y = (1.645 + 0.8416) x the Newey-West standard error x 12 = {y}, per ceiling"
            ) in out


class TestWhatThePostMeasured:
    """Numbers ``blog/capped-low-beta-lessons.md`` quotes that no row of Entry 48 declared.

    The write-up measured every one of them after the run, on the vintages and
    the specification in :data:`SPEC`, so each is exploratory and none carries
    an outcome. :func:`chan.low_beta_capped.yearly_standard_error` and
    :func:`chan.low_beta_capped.five_percent_line` were added for them, and
    :mod:`chan.low_beta_capped_figures` draws them.
    """

    @pytest.mark.parametrize(
        ("ceiling", "figures"), [(2.0, (0.0872, 0.1434)), (5.0, (0.1370, 0.2254))]
    )
    def test_the_yearly_standard_error_and_the_5_percent_line(
        self, outcomes, ceiling: float, figures
    ) -> None:
        c = outcomes[ceiling].capped
        se, line = yearly_standard_error(c), five_percent_line(c)
        assert (round(se, 4), round(line, 4)) == figures, f"{spec(ceiling)}; {AFTER_THE_RUN}"
        assert se == pytest.approx(abs(c.summary.mean / c.t) * 12, rel=1e-12)
        assert line == pytest.approx(CRITICAL * se, rel=1e-12)
        assert c.detectable == pytest.approx((CRITICAL + POWER) * se, rel=1e-12)

    @pytest.mark.parametrize("ceiling", CEILINGS)
    def test_each_point_estimate_falls_short_of_its_line(self, outcomes, ceiling: float) -> None:
        """The t is under 1.645 exactly when the gap is under the line, which is what it draws."""
        c = outcomes[ceiling].capped
        assert 0 < c.gap < five_percent_line(c) < c.detectable, f"{spec(ceiling)}; {AFTER_THE_RUN}"
        assert c.t < CRITICAL
        # Each point estimate is under half of its own Y, as the post says.
        assert 2 * c.gap < c.detectable, f"{spec(ceiling)}; {AFTER_THE_RUN}"

    @pytest.mark.parametrize(("ceiling", "june"), [(2.0, -0.0835), (5.0, -0.2132)])
    def test_june_2001_at_each_ceiling(self, outcomes, ceiling: float, june: float) -> None:
        """The month the beta match ruined, at a leverage of 2 and 5 rather than 58.0262."""
        c = outcomes[ceiling].capped
        held_to = pd.Timestamp("2001-06-29")
        assert c.portfolios.leverage.loc[held_to] == ceiling, spec(ceiling)
        assert round(float(c.portfolios.levered.loc[held_to]), 4) == june, (
            f"{spec(ceiling)}; {AFTER_THE_RUN}"
        )

    def test_the_smallest_leverage_that_ruins_any_month(self, portfolios: Portfolios) -> None:
        """No leverage below 13.4118 ruins any of the 83 months, so neither ceiling can.

        Each month's ruinous leverage is (1 + rf) / (rf − r_low), Entry 45's
        :func:`chan.low_beta_leverage.ruinous_leverage`. The smallest of them
        belongs to July 2002, the worst month at both ceilings.
        """
        needed = ruinous_leverage(portfolios.low, portfolios.rf)
        assert (round(float(needed.min()), 4), str(needed.idxmin().date())) == (
            13.4118,
            "2002-07-31",
        ), f"{SPEC}; {AFTER_THE_RUN}"
        assert max(CEILINGS) < needed.min()

    def test_wyn_dfs_and_se_carry_an_earlier_company_into_36_holding_months(
        self, sources, portfolios: Portfolios
    ) -> None:
        """Each symbol holds two companies, split by more than a year with no close.

        ``data/README.md`` names WYN and DFS. SE's closes stop on 2005-11-09
        and start again on 2007-01-03, the day Spectra Energy began
        regular-way trading after Duke Energy spun it off, so the closes before
        the gap are another company's. A holding month counts when any of the
        three sits in either fifth before its gap. None of them sits in a fifth
        after its restart. October 2001 holds both SE and WYN, and 2002-08 and
        2002-09 hold both WYN and DFS.
        """
        _, closes, _, _, _, _ = sources
        for symbol, (end, restart) in EARLIER_COMPANIES.items():
            held = closes[symbol].dropna().index
            longest = int((held[1:] - held[:-1]).argmax())
            assert (held[longest], held[longest + 1]) == (end, restart), symbol
        later = {
            held_to
            for held_to, low, high in zip(
                portfolios.held_to, portfolios.low_members, portfolios.high_members, strict=True
            )
            for symbol, (_, restart) in EARLIER_COMPANIES.items()
            if held_to >= restart and (symbol in low or symbol in high)
        }
        assert later == set()
        both = {
            held_to
            for held_to, low, high in zip(
                portfolios.held_to, portfolios.low_members, portfolios.high_members, strict=True
            )
            if sum(s in low or s in high for s in EARLIER_COMPANIES) > 1
        }
        assert both == {pd.Timestamp(d) for d in ("2001-10-31", "2002-08-30", "2002-09-30")}
        months = earlier_company_months(portfolios)
        assert (len(months), len(portfolios.held_to)) == (36, 83), f"{SPEC}; {AFTER_THE_RUN}"


class TestThePostQuotesTheRun:
    """The figures ``blog/capped-low-beta-lessons.md`` takes from the run, read from the post.

    The tests above derive these numbers and the post states them, so before
    this class a typo in the post passed every test. In round 1 of the post's
    review, a mutation run changed every figure in the post, and no test
    failed. Each assertion formats the run's own value at the post's precision,
    so a re-pin that leaves the post behind fails here too.

    The first four tests read one copy of each figure in the place it sits,
    so they also catch a figure moved to another figure's place. The fourth
    reads the dates: the file's last day and first month, the years its
    earlier companies' prices end, Entry 45's two ruined months, and the first
    and last of the eight sorts whose returns Entry 45 had shown. The last
    reads every figure in the post written with a decimal point, every copy,
    and holds that each is one the run computes or one of the constants listed
    below. That covers the subtitle, the lessons' list, the trader's habits
    and both alt texts, and it catches a copy that gains or drops a digit. It
    does not hold where a figure from the run sits, and it does not read a
    figure written as a whole number or in words, such as the 20 capped months
    in the chart's alt text.

    Chan's quotations and Kindle pages and the plan's date are not figures from
    the run. The last test also accepts these decimal figures from outside the
    run. It accepts 0.8416 and 1.645 anywhere. It accepts each of the others
    only in the phrases where the post uses it, and fails when one of those
    phrases is missing or the constant appears anywhere else.

    - 0.8416 and 1.645, which :data:`chan.low_beta_leverage.POWER` and
      :data:`chan.low_beta_leverage.CRITICAL` name.
    - 0.05, which :data:`chan.low_beta_capped.FALSE_DISCOVERY` names, with
      half of it, 0.025, and 1 minus it, 0.95. The post also uses 0.05 as an
      example of a month's return.
    - 0.0975, which is 1 − 0.95², in both its copies.
    - 0.20, the margin whose leverage is the higher ceiling, 5.
    - 0.04, Lesson 4's example p-value.
    - −0.4 and 0.8, the chart's outer tick labels, where the alt text gives
      its axis.
    """

    text = POST.read_text("utf-8")

    def test_the_two_tables(self, outcomes) -> None:
        two, five = outcomes[2.0].capped, outcomes[5.0].capped
        june = pd.Timestamp("2001-06-29")

        def row(label: str, a: float, b: float, digits: int = 4) -> str:
            return f"{label} & {a:.{digits}f} & {b:.{digits}f}"

        rows = [
            row(r"\text{Mean leverage}", two.mean_leverage, five.mean_leverage),
            row(r"\text{Months capped}", two.binds, five.binds, 0),
            row(
                r"\text{June 2001}",
                float(two.portfolios.levered.loc[june]),
                float(five.portfolios.levered.loc[june]),
            ),
            row(r"\text{July 2002, the worst month}", two.worst().capped, five.worst().capped),
            row(r"\text{Growth a year}", two.realised_growth, five.realised_growth),
            row(r"\text{Gap a year}", two.gap, five.gap),
            row(r"\text{Newey-West } t", two.t, five.t),
            row(r"\text{One-sided } p", two.p_claim, five.p_claim),
            row("Y", two.detectable, five.detectable),
        ]
        assert [r for r in rows if r not in self.text] == [], SPEC

    def test_the_prose_figures(self, outcomes, portfolios: Portfolios) -> None:
        two, five = outcomes[2.0].capped, outcomes[5.0].capped
        assert all(
            0 < c.gap < five_percent_line(c) and 2 * c.gap < c.detectable for c in (two, five)
        ), SPEC
        worst = two.worst()
        se_two, se_five = yearly_standard_error(two), yearly_standard_error(five)
        words = ("no", "one", "two", "three", "four", "five", "six")
        fragments = [
            f"which gives {two.months} holding months from {portfolios.held_to[0]:%B %Y} to "
            f"{portfolios.held_to[-1]:%B %Y}.",
            f"correlated with the d of the {words[two.lag]} months before it",
            f"The match never fell below {two.k.min():.4f}",
            f"realised betas were {two.realised_beta:.4f} at a ceiling of 2 and "
            f"{five.realised_beta:.4f} at 5",
            f"whose portfolios were formed on {worst.formed.date()}",
            f"{five.binds} of the {five.months} months at 5, so the beta match set the leverage "
            f"in the other {int((five.k <= 5.0).sum())}",
            f"The Newey-West standard error of the yearly gap is {se_two:.4f} at a ceiling of 2 "
            f"and {se_five:.4f} at 5",
            f"puts the 5 percent line at {five_percent_line(two):.4f} at a ceiling of 2 and "
            f"{five_percent_line(five):.4f} at 5",
            "Both point estimates fall short of their line.",
            "Each point estimate is under half of its own Y.",
            "each point estimate was under half of its Y",
            outcomes[2.0].line(),
            f"the gap rose from {two.gap:.4f} to {five.gap:.4f}, about "
            f"{five.gap / two.gap:.2f} times",
            f"Its standard error rose from {se_two:.4f} to {se_five:.4f}, about "
            f"{se_five / se_two:.2f} times",
            f"Against the claim they are {two.p_contrary:.4f} and {five.p_contrary:.4f}",
            f"At a ceiling of 2 it is {break_even_spread(two.portfolios):.4f} a year, and at a "
            f"ceiling of 5 it is {break_even_spread(five.portfolios):.4f}",
            f"The lead at 5 is about {five.gap / two.gap:.2f} times the lead at 2, but the "
            f"portfolio at 5 borrows about "
            f"{(five.mean_leverage - 1) / (two.mean_leverage - 1):.2f} times as much",
            f"It borrows a mean of {five.mean_leverage - 1:.4f} for each unit of capital, one "
            f"less than its mean leverage of {five.mean_leverage:.4f}",
            f"Those earlier prices sit in one of the two fifths in "
            f"{len(earlier_company_months(portfolios))} of the {len(portfolios.held_to)} months "
            f"the portfolios were held.",
        ]
        assert [f for f in fragments if f not in self.text] == [], SPEC

    def test_entry_45s_figures(self, portfolios: Portfolios) -> None:
        june = pd.Timestamp("2001-06-29")
        needed = ruinous_leverage(portfolios.low, portfolios.rf)
        fragments = [
            f"so the [match asked for leverages up to {portfolios.leverage.max():.4f}]",
            f"At a leverage of {portfolios.leverage.loc[june]:.4f}, the [levered portfolio",
            f"the low fifth compounded at {growth(portfolios.low):.4f} a year against the high "
            f"fifth’s {growth(portfolios.high):.4f}",
            f"was {kelly(portfolios).leverage:.4f}.",
            f"against the high fifth’s {realised_beta(portfolios.high, portfolios):.4f}",
            f"June 2001 returned {minus(float(portfolios.levered.loc[june]))} at a leverage of "
            f"{portfolios.leverage.loc[june]:.4f}",
            f"Across all {len(needed)} months the smallest is {needed.min():.4f}, for "
            f"{needed.idxmin():%B %Y}, "
            f"when the low fifth returned {minus(float(portfolios.low.min()))}, its worst month",
        ]
        assert [f for f in fragments if f not in self.text] == [], SPEC

    def test_the_dates(self, sources, portfolios: Portfolios) -> None:
        """The dates the post takes from the file and from Entry 45's run."""
        _, closes, _, _, _, _ = sources
        ruins = ruined_months(portfolios)
        assert len(ruins) == 2, SPEC
        assert EARLIER_COMPANIES["DFS"][0].year == EARLIER_COMPANIES["SE"][0].year
        fragments = [
            f"in the S&P 500 on {closes.index[-1].date()}, with their prices back to "
            f"{closes.index[0]:%B %Y}",
            f"up to {EARLIER_COMPANIES['WYN'][0].year} for WYN and "
            f"{EARLIER_COMPANIES['DFS'][0].year} for the other two",
            f"lost more than its capital in {ruins[0].held_to:%B %Y}](",
            f"for [{ruins[0].held_to:%B} and {ruins[1].held_to:%B %Y}](",
            f"for the eight months held after the sorts from {portfolios.formed[0].date()} to "
            f"{portfolios.formed[7].date()}",
        ]
        assert [f for f in fragments if f not in self.text] == [], SPEC

    def test_every_decimal_figure_is_one_the_run_computes(
        self, outcomes, portfolios: Portfolios
    ) -> None:
        june = pd.Timestamp("2001-06-29")
        values = [POWER]
        for c in (o.capped for o in outcomes.values()):
            values += [
                c.gap,
                c.t,
                c.p_claim,
                c.p_contrary,
                c.detectable,
                c.realised_growth,
                c.mean_leverage,
                c.mean_leverage - 1,
                c.realised_beta,
                c.worst().capped,
                float(c.portfolios.levered.loc[june]),
                yearly_standard_error(c),
                five_percent_line(c),
                break_even_spread(c.portfolios),
            ]
        values += [
            portfolios.leverage.max(),
            portfolios.leverage.loc[june],
            float(portfolios.levered.loc[june]),
            growth(portfolios.low),
            growth(portfolios.high),
            kelly(portfolios).leverage,
            realised_beta(portfolios.high, portfolios),
            ruinous_leverage(portfolios.low, portfolios.rf).min(),
            float(portfolios.low.min()),
            outcomes[2.0].capped.k.min(),
        ]
        two, five = outcomes[2.0].capped, outcomes[5.0].capped
        computed = {f"{abs(v):.4f}" for v in values} | {
            f"{five.gap / two.gap:.2f}",
            f"{yearly_standard_error(five) / yearly_standard_error(two):.2f}",
            f"{(five.mean_leverage - 1) / (two.mean_leverage - 1):.2f}",
            f"{CRITICAL}",
        }
        # The constants from outside the run, each accepted only where the post uses it.
        rate, half, ceiling = FALSE_DISCOVERY, FALSE_DISCOVERY / 2, max(CEILINGS)
        constants = [
            "a month returning 0.05 gained 5 percent",
            f"a leverage of 1 / {1 / ceiling:.2f}, or {ceiling:.0f}.",
            f"the chance is 1 − {1 - rate}², or {1 - (1 - rate) ** 2:.4f}.",
            f"their chance sits below {1 - (1 - rate) ** 2:.4f}.",
            f"at most i/m × {rate}.",
            f"both pass when both p-values are at most {rate}.",
            f"only if it is at most {half}.",
            f"Both are above {rate}, and the smaller is above {half},",
            f"Both p-values are above {rate}, so",
            "come in at a p-value of 0.04 beside",
            f"If the other ceiling’s p-value is above {rate},",
            f"must then be at most {half}.",
            "running from −0.4 to 0.8.",
        ]
        rest = self.text
        for fragment in constants:
            assert fragment in rest, fragment
            rest = rest.replace(fragment, " ")
        quoted = re.findall(r"(?<![\d.])\d+\.\d+(?!\d)", rest)
        assert quoted, POST
        assert [q for q in quoted if q not in computed] == [], SPEC


def minus(x: float) -> str:
    """A negative figure as the post prints it, with a typographic minus sign."""
    return f"{x:.4f}".replace("-", "\u2212")


#: The symbols in Chan's file that carry an earlier company's closes before a
#: gap of more than a year, with the last close before the gap and the restart.
EARLIER_COMPANIES = {
    "WYN": (pd.Timestamp("2002-10-18"), pd.Timestamp("2006-08-01")),
    "DFS": (pd.Timestamp("2005-11-25"), pd.Timestamp("2007-07-02")),
    "SE": (pd.Timestamp("2005-11-09"), pd.Timestamp("2007-01-03")),
}


def earlier_company_months(portfolios: Portfolios) -> set[pd.Timestamp]:
    """The holding months with an earlier company's closes in either fifth."""
    return {
        held_to
        for held_to, low, high in zip(
            portfolios.held_to, portfolios.low_members, portfolios.high_members, strict=True
        )
        for symbol, (end, _) in EARLIER_COMPANIES.items()
        if held_to <= end and (symbol in low or symbol in high)
    }


# --- the rules, on portfolios built by hand ------------------------------------


def made(
    low: list[float],
    high: list[float],
    k: list[float],
    rf: float | list[float] = 0.0,
    spy: list[float] | None = None,
) -> Portfolios:
    """A :class:`Portfolios` holding the given months, with nothing else in it that matters."""
    n = len(low)
    ends = pd.date_range("2001-01-31", periods=n + 1, freq="ME")
    index = pd.DatetimeIndex(ends[1:])
    rates = rf if isinstance(rf, list) else [rf] * n
    market = spy if spy is not None else [0.01 * ((i % 3) - 1) + 0.002 * i for i in range(n)]
    rate = pd.Series(rates, index=index)
    low_series = pd.Series(low, index=index)
    leverage = pd.Series(k, index=index)
    return Portfolios(
        month_ends=ends,
        formed=tuple(ends[:-1]),
        held_to=tuple(index),
        window_start=tuple(ends[:-1]),
        low=low_series,
        high=pd.Series(high, index=index),
        levered=rate + leverage * (low_series - rate),
        rf=rate,
        spy=pd.Series(market, index=index),
        low_beta=pd.Series(1.0, index=index),
        high_beta=leverage.copy(),
        leverage=leverage,
        eligible=(5,) * n,
        low_members=(("A",),) * n,
        high_members=(("E",),) * n,
        betas=pd.DataFrame(index=pd.DatetimeIndex(ends[:-1])),
    )


def summary(mean: float, t: float, n: int = 83) -> NeweyWestSummary:
    return NeweyWestSummary(n=n, mean=mean, var=0.0, t_naive=0.0, t_newey_west=t, lag=3)


def with_statistic(ceiling: float, mean: float, t: float, months: int = 83) -> Capped:
    """A ceiling carrying a hand-set statistic, for the control and the wordings."""
    p = made([0.01] * months, [0.0] * months, [3.0] * months)
    return Capped(ceiling=ceiling, portfolios=p, k=p.leverage, ruined=(), summary=summary(mean, t))


def ruined_at(ceiling: float) -> Capped:
    """A ceiling whose second month loses more than the capital."""
    p = cap(made([0.01, -0.3, 0.01], [0.0, 0.0, 0.0], [10.0, 10.0, 10.0]), ceiling)
    return Capped(
        ceiling=ceiling, portfolios=p, k=p.leverage, ruined=ruined_months(p), summary=None
    )


def t_for(p: float) -> float:
    """The t whose one-sided p-value in the claim's direction is ``p``."""
    low, high = -10.0, 10.0
    for _ in range(200):
        middle = (low + high) / 2
        if one_sided_p(middle) > p:
            low = middle
        else:
            high = middle
    return (low + high) / 2


class TestTheCap:
    def test_l_is_the_beta_match_capped_at_the_ceiling(self) -> None:
        p = cap(made([0.01, 0.02, 0.03], [0.0] * 3, [1.5, 3.0, 7.0]), 5.0)
        assert list(p.leverage) == [1.5, 3.0, 5.0]

    def test_a_ceiling_equal_to_k_leaves_k(self) -> None:
        assert list(cap(made([0.01], [0.0], [2.0]), 2.0).leverage) == [2.0]

    def test_the_capped_month_borrows_at_the_holding_months_bill(self) -> None:
        p = cap(made([0.02, -0.01], [0.0, 0.0], [8.0, 3.0], rf=[0.004, 0.001]), 5.0)
        assert p.levered.iloc[0] == pytest.approx(0.004 + 5.0 * (0.02 - 0.004))
        assert p.levered.iloc[1] == pytest.approx(0.001 + 3.0 * (-0.01 - 0.001))

    def test_a_ruin_names_the_capped_leverage_not_k(self) -> None:
        """Replacing ``levered`` alone would leave ``leverage`` at k, and the ruin would say 10."""
        ruined = ruined_at(5.0).ruined
        assert [(r.leverage, round(r.levered, 4)) for r in ruined] == [(5.0, -1.5)]

    def test_only_levered_and_leverage_change(self) -> None:
        p = made([0.01, 0.02], [0.03, 0.04], [9.0, 1.0], rf=0.002)
        q = cap(p, 2.0)
        assert q.low is p.low and q.high is p.high and q.rf is p.rf and q.spy is p.spy
        assert q.formed == p.formed and q.held_to == p.held_to
        assert not q.levered.equals(p.levered)

    @pytest.mark.parametrize("ceiling", [1.0, 0.5, 0.0, -2.0, math.nan])
    def test_a_ceiling_at_or_below_1_refuses(self, ceiling: float) -> None:
        """At a ceiling of 1 nothing is borrowed, and below it the spread logic turns over."""
        p = made([0.01, 0.02], [0.0, 0.0], [3.0, 4.0])
        for build in (cap, capped):
            with pytest.raises(ValueError, match="nothing is borrowed and no leverage is tested"):
                build(p, ceiling)
        with pytest.raises(ValueError, match="nothing is borrowed and no leverage is tested"):
            assess(p, [2.0, ceiling])

    def test_a_ceiling_just_above_1_is_accepted(self) -> None:
        p = made([0.01, 0.02], [0.0, 0.0], [3.0, 4.0])
        assert list(cap(p, 1.5).leverage) == [1.5, 1.5]

    def test_k_is_kept_beside_the_capped_leverage(self) -> None:
        p = made([0.01, 0.02], [0.0, 0.0], [9.0, 1.0])
        result = capped(p, 2.0)
        assert list(result.k) == [9.0, 1.0]
        assert list(result.portfolios.leverage) == [2.0, 1.0]


class TestTheStatistic:
    def test_d_is_the_log_gap_on_the_capped_return(self) -> None:
        low = [0.01, -0.02, 0.03, 0.005, -0.01, 0.02]
        high = [0.02, -0.03, 0.01, 0.0, 0.01, -0.01]
        p = made(low, high, [4.0, 1.0, 6.0, 2.0, 3.0, 7.0], rf=0.001)
        result = capped(p, 3.0)
        expected = np.log1p(result.portfolios.levered) - np.log1p(p.high)
        assert result.summary == newey_west_summary(expected.to_numpy())
        assert result.gap == pytest.approx(12 * expected.mean())

    def test_a_ruined_ceiling_computes_no_t(self) -> None:
        result = ruined_at(5.0)
        with pytest.raises(ValueError, match="Newey-West statistic is not computed"):
            _ = result.t
        with pytest.raises(ValueError, match="Newey-West statistic is not computed"):
            _ = result.detectable

    def test_a_ceiling_low_enough_avoids_the_ruin(self) -> None:
        p = made([0.01, -0.3, 0.01], [0.0, 0.0, 0.0], [10.0, 10.0, 10.0])
        assert capped(p, 5.0).by_ruin
        assert not capped(p, 2.0).by_ruin


class TestTheControl:
    def test_the_two_directions_read_t_and_minus_t(self) -> None:
        c = with_statistic(2.0, 0.001, 1.3)
        assert c.p_claim == one_sided_p(1.3)
        assert c.p_contrary == one_sided_p(-1.3)

    def test_a_ruined_ceiling_enters_both_families_at_1(self) -> None:
        c = ruined_at(5.0)
        assert (c.p_claim, c.p_contrary) == (1.0, 1.0)

    def test_both_at_most_0_05_are_both_rejected(self) -> None:
        a, b = with_statistic(2.0, 0.001, t_for(0.04)), with_statistic(5.0, 0.001, t_for(0.0499))
        outcomes = decide([a, b])
        assert [o.claim_rejected for o in outcomes] == [True, True]
        assert [o.outcome for o in outcomes] == ["Holds", "Holds"]

    def test_otherwise_only_one_at_most_0_025_is_rejected(self) -> None:
        a, b = with_statistic(2.0, 0.001, t_for(0.0249)), with_statistic(5.0, 0.001, t_for(0.06))
        outcomes = decide([a, b])
        assert [o.claim_rejected for o in outcomes] == [True, False]
        assert [o.outcome for o in outcomes] == ["Holds", "Not decided"]

    def test_one_at_0_03_alone_is_not_rejected(self) -> None:
        a, b = with_statistic(2.0, 0.001, t_for(0.03)), with_statistic(5.0, 0.001, t_for(0.2))
        assert [o.claim_rejected for o in decide([a, b])] == [False, False]

    def test_a_ruined_ceiling_cannot_help_the_other_pass(self) -> None:
        """Alone, 0.03 would pass at 0.05. Beside a ruin at 1 its threshold is 0.025."""
        ok = with_statistic(2.0, 0.001, t_for(0.03))
        outcomes = decide([ok, ruined_at(5.0)])
        assert [o.outcome for o in outcomes] == ["Not decided", "Contradicted by ruin"]
        assert [o.claim_rejected for o in outcomes] == [False, False]
        assert [o.contrary_rejected for o in outcomes] == [False, False]
        assert decide([ok])[0].claim_rejected

    def test_the_contrary_family_rejects_negative_t(self) -> None:
        a, b = with_statistic(2.0, -0.002, -t_for(0.01)), with_statistic(5.0, -0.001, -t_for(0.5))
        outcomes = decide([a, b])
        assert [o.contrary_rejected for o in outcomes] == [True, False]
        assert [o.claim_rejected for o in outcomes] == [False, False]
        assert [o.outcome for o in outcomes] == ["Contradicted", "Not decided"]

    def test_the_contrary_family_runs_at_the_same_q(self) -> None:
        a = with_statistic(2.0, -0.001, -t_for(0.04))
        b = with_statistic(5.0, -0.001, -t_for(0.0499))
        assert [o.contrary_rejected for o in decide([a, b])] == [True, True]

    def test_assess_uses_the_ceilings_it_is_given(self) -> None:
        p = made([0.01, 0.02, -0.01, 0.03], [0.0, 0.01, 0.0, 0.005], [4.0, 1.0, 6.0, 2.0])
        assert [o.capped.ceiling for o in assess(p, (3.0,))] == [3.0]

    def test_a_rejection_against_the_means_sign_is_not_decided(self) -> None:
        """A positive mean with a rejecting contrary family decides nothing, and the reverse."""
        up = Outcome(
            capped=with_statistic(2.0, 0.001, 3.0), claim_rejected=False, contrary_rejected=True
        )
        down = Outcome(
            capped=with_statistic(5.0, -0.001, -3.0), claim_rejected=True, contrary_rejected=False
        )
        assert (up.outcome, down.outcome) == ("Not decided", "Not decided")


class TestTheWordings:
    def test_contradicted_by_ruin(self) -> None:
        o = decide([ruined_at(5.0), with_statistic(2.0, 0.001, 0.5)])[0]
        assert o.outcome == "Contradicted by ruin"
        assert o.line() == (
            "Levered by the beta match capped at 5, the low-beta portfolio lost more than its "
            "capital in the month ending 2001-03-31, at a leverage of 5.0000, so its compounded "
            "growth is unbounded below and the unlevered high-beta portfolio out-compounded it."
        )

    def test_the_ruin_line_names_the_first_ruin_at_its_capped_leverage(self) -> None:
        # Months 2 and 3 ruin, at L = 4 and L = 5, so the first ruin sits below the cap.
        p = cap(made([0.01, -0.4, -0.3], [0.0] * 3, [10.0, 4.0, 10.0]), 5.0)
        c = Capped(ceiling=5.0, portfolios=p, k=p.leverage, ruined=ruined_months(p), summary=None)
        o = Outcome(capped=c, claim_rejected=False, contrary_rejected=False)
        assert [r.leverage for r in c.ruined] == [4.0, 5.0]
        assert "in the month ending 2001-03-31, at a leverage of 4.0000, so" in o.line()

    def test_holds(self) -> None:
        o = Outcome(
            capped=with_statistic(2.0, 0.001, 2.5), claim_rejected=True, contrary_rejected=False
        )
        assert o.line() == (
            "Levered by the beta match capped at 2, the low-beta portfolio out-compounded the "
            "unlevered high-beta portfolio by 0.0120 a year, Newey-West t = 2.5000 over 83 "
            "months, a discovery under Benjamini-Hochberg at 5 percent across the two ceilings."
        )

    def test_contradicted(self) -> None:
        o = Outcome(
            capped=with_statistic(5.0, -0.002, -2.5), claim_rejected=False, contrary_rejected=True
        )
        assert o.line() == (
            "The unlevered high-beta portfolio out-compounded the low-beta portfolio levered by "
            "the beta match capped at 5 by 0.0240 a year, Newey-West t = -2.5000 over 83 months, "
            "a discovery under Benjamini-Hochberg at 5 percent across the two ceilings."
        )

    def test_not_decided_quotes_y_from_entry_45s_formula(self) -> None:
        o = Outcome(
            capped=with_statistic(2.0, 0.001, 0.5, months=60),
            claim_rejected=False,
            contrary_rejected=False,
        )
        assert o.capped.detectable == pytest.approx((1.645 + 0.8416) * 0.002 * 12)
        assert o.line() == (
            "At a ceiling of 2, no gap in compounded growth detectable above about 0.0597 a year "
            "over 60 months, where the point estimate is 0.0120."
        )

    def test_a_degenerate_d_refuses_before_anything_is_printed(self) -> None:
        with pytest.raises(UnreadableStandardError, match="mean of exactly 0"):
            decide([with_statistic(2.0, 0.0, 0.0), with_statistic(5.0, 0.001, 0.5)])


class TestTheSideFigures:
    def test_binds_counts_the_months_k_is_above_the_ceiling(self) -> None:
        p = made([0.01] * 4, [0.0] * 4, [1.0, 2.0, 2.5, 6.0])
        assert capped(p, 2.0).binds == 2
        assert capped(p, 2.0).mean_leverage == pytest.approx((1.0 + 2.0 + 2.0 + 2.0) / 4)

    def test_the_worst_month_carries_its_formation_and_leverage(self) -> None:
        p = made([0.01, -0.05, -0.04], [0.0] * 3, [1.0, 1.0, 9.0])
        worst = capped(p, 3.0).worst()
        assert worst.held_to == p.held_to[2] and worst.formed == p.formed[2]
        assert (worst.leverage, worst.capped) == (3.0, pytest.approx(-0.12))

    def test_growth_is_ruin_once_a_month_is_ruined(self) -> None:
        assert ruined_at(5.0).realised_growth is None
        p = made([0.01, 0.02], [0.0, 0.0], [2.0, 2.0])
        assert capped(p, 5.0).realised_growth == pytest.approx(
            6 * (math.log(1.02) + math.log(1.04))
        )

    def test_realised_beta_reads_the_capped_series(self) -> None:
        spy = [0.01, -0.02, 0.03, 0.0, -0.01, 0.02]
        p = made(spy, [0.0] * 6, [4.0] * 6, spy=spy)
        assert capped(p, 2.0).realised_beta == pytest.approx(2.0)


class TestThePostsHelpers:
    """The two helpers the write-up added, on a hand-set statistic whose answers are worked here."""

    def test_the_yearly_standard_error_is_12_times_the_mean_over_t(self) -> None:
        """A monthly mean of 0.001 at a t of 0.5 is a monthly standard error of 0.002."""
        c = with_statistic(2.0, 0.001, 0.5)
        assert yearly_standard_error(c) == pytest.approx(0.024, abs=1e-15)
        assert yearly_standard_error(with_statistic(5.0, -0.001, -0.5)) == pytest.approx(0.024)

    def test_the_line_is_1_645_standard_errors(self) -> None:
        c = with_statistic(2.0, 0.001, 0.5)
        assert five_percent_line(c) == pytest.approx(1.645 * 0.024, abs=1e-15)
        assert c.detectable - five_percent_line(c) == pytest.approx(0.8416 * 0.024)

    def test_a_ruined_ceiling_has_neither(self) -> None:
        for helper in (yearly_standard_error, five_percent_line):
            with pytest.raises(ValueError, match="Newey-West statistic is not computed"):
                helper(ruined_at(5.0))

    def test_a_t_of_0_refuses_and_names_the_months(self) -> None:
        """A t of 0 hides the standard error, and the refusal counts the ceiling's own months."""
        for helper in (yearly_standard_error, five_percent_line):
            with pytest.raises(UnreadableStandardError, match="t of d is 0 over 7 months"):
                helper(with_statistic(2.0, 0.0, 0.0, months=7))


class TestTheBreakEvenSpread:
    def test_at_a_leverage_of_2_it_is_12_times_the_monthly_gap(self) -> None:
        """2 × 0.01 − s / 12 equals 0.005 at s = 0.18."""
        p = cap(made([0.01] * 4, [0.005] * 4, [3.0] * 4), 2.0)
        assert break_even_spread(p) == pytest.approx(0.18, abs=1e-9)

    def test_the_charge_is_on_the_borrowed_l_minus_1(self) -> None:
        """At a leverage of 3 the charge is 2 × s / 12, so 0.03 − s / 6 = 0.005 at s = 0.15."""
        p = cap(made([0.01] * 4, [0.005] * 4, [3.0] * 4), 5.0)
        assert break_even_spread(p) == pytest.approx(0.15, abs=1e-9)
        assert charged_gap(p, 0.06) == pytest.approx(12 * (math.log(1.02) - math.log(1.005)))

    def test_the_gap_falls_as_the_spread_rises(self) -> None:
        p = cap(made([0.01, 0.03, -0.005], [0.005, 0.0, 0.01], [3.0, 2.0, 4.0]), 5.0)
        spread = break_even_spread(p)
        assert charged_gap(p, spread / 2) > 0 > charged_gap(p, spread * 2)

    def test_none_when_the_gap_is_0_or_below_without_a_spread(self) -> None:
        behind = cap(made([0.002] * 3, [0.01] * 3, [3.0] * 3), 2.0)
        even = cap(made([0.005] * 3, [0.01] * 3, [3.0] * 3), 2.0)
        assert charged_gap(even, 0.0) == pytest.approx(0.0)
        assert break_even_spread(behind) is None
        assert break_even_spread(even) is None

    def test_none_for_a_ruined_ceiling(self) -> None:
        assert break_even_spread(ruined_at(5.0).portfolios) is None

    def test_a_charged_month_at_minus_1_is_a_gap_unbounded_below(self) -> None:
        p = cap(made([0.01] * 2, [0.0] * 2, [3.0] * 2), 2.0)
        assert charged_gap(p, 12 * 1.02) == -math.inf

    def test_a_break_even_past_8192_ends_within_the_halving_cap(self, monkeypatch) -> None:
        """Past about 8192 neighbouring floats lie further apart than the bisection's tolerance.

        At a leverage of 1 + 1e-7 each month borrows almost nothing, so the
        break-even spread is near 12 × 0.0005 / 1e-7, about 60,000. Counting
        the calls to the gap turns a bisection that would never end into a
        failure rather than a hang.
        """
        n = 4
        p = made([0.001] * n, [0.0005] * n, [1 + 1e-7] * n)
        assert p.levered.equals(p.rf + p.leverage * (p.low - p.rf))
        doublings = math.ceil(math.log2(MAX_SPREAD)) + 1
        limit = 1 + doublings + MAX_HALVINGS
        calls = 0
        gap = low_beta_capped.charged_gap

        def counted(portfolios: Portfolios, spread: float) -> float:
            nonlocal calls
            calls += 1
            if calls > limit:
                raise AssertionError(f"the bisection called the gap more than {limit} times")
            return gap(portfolios, spread)

        monkeypatch.setattr(low_beta_capped, "charged_gap", counted)
        found = break_even_spread(p)
        assert found > 8192
        assert found == pytest.approx(12 * (0.001 - 0.0005) / 1e-7, rel=1e-3)
        assert gap(p, found) == pytest.approx(0.0, abs=1e-9)

    def test_no_bracket_refuses(self) -> None:
        """At a leverage of 1 nothing is borrowed, so no spread moves the gap."""
        p = cap(made([0.01] * 3, [0.0] * 3, [1.0] * 3), 2.0)
        with pytest.raises(NoBreakEven, match=re.escape(f"spread of {MAX_SPREAD:g}")):
            break_even_spread(p)


class TestTheRefusals:
    @pytest.mark.parametrize(
        "refusal",
        [
            NonPositiveBeta("the low group formed 2001-05-31 has a mean beta of -0.1000"),
            EmptyPortfolio("only 4 stocks are eligible at 2000-11-30"),
            UnreadableStandardError("the Newey-West t of d is 0 over 83 months"),
            NoBreakEven("the gap stays above 0 at a yearly spread of 1e+06"),
            VintageUnavailable("no committed vintage is lifted from SPX_20071123.mat"),
        ],
    )
    def test_main_prints_a_refusal_as_one_line(self, monkeypatch, refusal: Exception) -> None:
        def refuse(data_dir=None):
            raise refusal

        monkeypatch.setattr(low_beta_capped, "run", refuse)
        monkeypatch.setattr("sys.argv", ["low_beta_capped"])
        with pytest.raises(SystemExit, match=re.escape(str(refusal))) as exited:
            main()
        assert exited.value.code == str(refusal)


class TestTheRuinedReport:
    """The report's branch for a ruined ceiling, on portfolios built by hand."""

    def test_it_prints_the_ruined_month_and_no_statistic(
        self, sources, capsys, monkeypatch
    ) -> None:
        members, _, spy_entry, _, bill_entry, _ = sources
        months = 12
        low = [0.01, -0.03, 0.02, 0.015, -0.005, 0.01, 0.02, -0.01, 0.005, 0.03, -0.02, 0.01]
        high = [0.0, -0.02, 0.03, 0.0, 0.01, -0.01, 0.02, 0.0, -0.005, 0.01, 0.0, 0.02]
        k = [3.0] * months
        k[1] = 40.0
        p = made(low, high, k, rf=0.001)
        monkeypatch.setattr(low_beta_capped, "CEILINGS", (2.0, 50.0))
        outcomes = report(members, spy_entry, bill_entry, p)
        out = capsys.readouterr().out
        assert [o.outcome for o in outcomes][1] == "Contradicted by ruin"
        assert "Ceiling 50: CONTRADICTED BY RUIN, exploratory." in out
        ruin = outcomes[1].capped.ruined[0]
        assert (
            f"  {str(ruin.held_to.date()):<14} {str(ruin.formed.date()):<12} "
            f"{40.0:>8.4f} {ruin.levered:>9.4f}"
        ) in out
        assert "neither t nor Y is computed, and the ceiling enters both families at p = 1." in out
        assert re.search(r"\n  50 +ruin ", out)
        assert "none   2001-03-31" in out

    def test_every_ruin_row_prints_its_capped_leverage(self, sources, capsys, monkeypatch) -> None:
        members, _, spy_entry, _, bill_entry, _ = sources
        low = [0.01, -0.3, 0.02, 0.015, -0.4, 0.01, 0.02, -0.01, 0.005, 0.03, -0.02, 0.01]
        high = [0.0, -0.02, 0.03, 0.0, 0.01, -0.01, 0.02, 0.0, -0.005, 0.01, 0.0, 0.02]
        k = [3.0] * 12
        k[1], k[4] = 10.0, 4.0
        monkeypatch.setattr(low_beta_capped, "CEILINGS", (2.0, 5.0))
        outcomes = report(members, spy_entry, bill_entry, made(low, high, k, rf=0.001))
        out = capsys.readouterr().out
        ruined = outcomes[1].capped.ruined
        assert [(str(r.held_to.date()), r.leverage) for r in ruined] == [
            ("2001-03-31", 5.0),
            ("2001-06-30", 4.0),
        ]
        for r in ruined:
            assert (
                f"  {str(r.held_to.date()):<14} {str(r.formed.date()):<12} "
                f"{r.leverage:>8.4f} {r.levered:>9.4f}"
            ) in out

    def test_the_report_prints_each_familys_decision(self, sources, capsys, monkeypatch) -> None:
        members, _, spy_entry, _, bill_entry, _ = sources
        low = [0.02, 0.03, 0.025, 0.01, 0.04, 0.02, 0.03, 0.015, 0.02, 0.035, 0.01, 0.025]
        p = made(low, [0.0] * 12, [3.0] * 12, rf=0.001)
        outcomes = report(members, spy_entry, bill_entry, p)
        out = capsys.readouterr().out
        assert [o.outcome for o in outcomes] == ["Holds", "Holds"]
        assert len(re.findall(r"rejected yes\. Contrary \d\.\d{4}, rejected no\.", out)) == 2
