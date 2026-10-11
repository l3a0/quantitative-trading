"""The pins for location 4709's low-beta rule at leverage a broker would lend. Exploratory.

This file is the single authority for every number any prose surface quotes
about [issue 516](https://github.com/l3a0/quantitative-trading/issues/516).
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
  2007-11-23, so every figure here is about survivors.
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
    main,
    report,
)
from chan.low_beta_leverage import (
    EmptyPortfolio,
    NonPositiveBeta,
    Portfolios,
    UnreadableStandardError,
    build_portfolios,
    growth,
    read_sources,
    realised_beta,
    ruined_months,
)
from chan.pca_factor_momentum import one_sided_p
from chan.vintage import VintageUnavailable

SPEC = (
    "spx_20071123/ chan-mat adjusted saved 2007-11-24 against spy_chan.csv chan-xls adjusted "
    "saved 2008-01-29 and TB3MS dl 2026-09-30, Entry 45's portfolios unchanged, low fifth "
    "levered by min(k, C) at the bill, d against the unlevered high fifth December 2000 to "
    "October 2007, Newey-West default lag, Benjamini-Hochberg 0.05 across ceilings 2 and 5 in "
    "each direction, planned 2026-10-11 before any capped number, exploratory, survivors only, "
    "not a holdout"
)


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
            "5. No margin call inside a month is modelled. Under Regulation T's 25 percent "
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
