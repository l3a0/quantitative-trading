"""The pins for whether Example 7.4's own factor returns have momentum.

This file is the single authority for every number any prose surface quotes
about [issue 286](https://github.com/l3a0/quantitative-trading/issues/286).
``docs/replication-log.md`` Entry 42 carries the verdicts and points here.

Every pin on the committed file reads one vintage and one specification, so
both are stated once here and carried in every figure's failure message as
:data:`SPEC`.

- **Vintage.** ``ijr_20080114/``, the 600 S&P 600 members lifted from Chan's
  ``IJR_20080114.mat``, adjusted, saved 2008-01-15, spanning 2004-01-15 to
  2008-01-14, read for the Close column. Its identity is the
  ``LIFTED_SOURCES`` row in ``tests/support/committed_vintages.py``. The file
  holds the companies in the index on 2008-01-14, so every figure is a figure
  about survivors.
- **Specification.** :mod:`chan.pca_factor_momentum` as the issue fixed it.
  The revised MATLAB's components, a lookback of 252 and five factors, after
  its forward fill. Each pair is f_t[k] = u_k · r_t and f_{t+1}[k] = u_k ·
  r_{t+1} on day t's unit-length vectors and day t's stocks, for every
  fitting day with a next row. The statistic is the uncentred correlation of
  the pairs. The comparison set is every stock with a finite return on every
  row the pairs read, under the same statistic.

The figures are pinned at four decimals, which is what the log quotes. The
five verdicts compare unrounded values, so their tests read the unrounded
ones. Every figure is pinned twice, once on the file as the program reads it
and once without PMC.

Every run on the file happens once, in the ``results`` fixture, because each
set of columns takes 752 decompositions. Every pin reads that fixture, and the
report's test prints from it rather than computing again. The write-up's pins
in ``TestWhatThePostMeasured`` read two more fixtures for the same reason,
``components`` for the 753 fitting days' decompositions and ``weights`` for
the 1,504 more, on the 251 days before each day t and on the 251 days ending
it. All three come from ``pca_factor_momentum_run`` in ``tests/conftest.py``,
which ``tests/test_pca_factor_momentum_figures.py`` reads too, so a run of the
suite computes them once for both files.

Exploratory. Testing a claim someone else chose spends the 2004 to 2008 sample
on it. It first ran here on 2026-10-10.
"""

from __future__ import annotations

import dataclasses
import math

import numpy as np
import pandas as pd
import pytest

from chan import paths, pca_factor_momentum
from chan.pca_factor import (
    FACTORS,
    LOOKBACK,
    SMALL_CAPS,
    SPLICED,
    matlab_returns,
    revised_matlab_components,
    revised_matlab_expected,
)
from chan.pca_factor_momentum import (
    ASSUMPTION_LOCATION,
    CLAIM_LOCATION,
    CRITICAL,
    FALSE_DISCOVERY,
    NAMES,
    OFTEN,
    Comparison,
    Decomposition,
    Pairs,
    Result,
    Results,
    Verdict,
    WeightStatistics,
    _figures,
    benjamini_hochberg,
    compute,
    daily_components,
    decompose,
    factor_pairs,
    file_returns,
    largest_loading,
    main,
    match,
    one_sided_p,
    overlaps,
    rankings_agree,
    report,
    run,
    share_of_largest,
    sign_flips,
    smallest_gap,
    stock_statistics,
    swap_days,
    uncentred,
    weight_statistics,
    windows_holding,
    with_largest_weight_positive,
    without_the_intercept,
)
from chan.series import load_panel
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import LIFTED_SOURCES

SPEC = (
    "ijr_20080114/ Close, forward-filled, revised MATLAB components, lookback 252, 5 factors, "
    "f_t = u_k.r_t and f_t+1 = u_k.r_t+1 on day t's vectors, uncentred correlation"
)

#: The tolerance a figure pinned at four decimals is held to.
FOUR = 5e-5


# --- the committed file ----------------------------------------------------------


@pytest.fixture(scope="module")
def panel():
    return load_panel(SMALL_CAPS, field="Close")


@pytest.fixture(scope="module")
def results(pca_factor_momentum_run) -> Results:
    return pca_factor_momentum_run[0]


class TestTheSpecification:
    def test_the_rule_is_the_issues(self) -> None:
        assert (LOOKBACK, FACTORS) == (252, 5)
        assert NAMES == ("PC1", "PC2", "PC3", "PC4", "PC5")
        assert (CRITICAL, FALSE_DISCOVERY) == (1.96, 0.05)

    def test_the_locations_are_the_revised_editions(self) -> None:
        assert (CLAIM_LOCATION, ASSUMPTION_LOCATION) == (4014, 4051)
        assert OFTEN == "often"

    def test_the_members_are_the_pinned_source(self, panel) -> None:
        members, closes = panel
        vendor, basis, saved, folder, count = LIFTED_SOURCES[SMALL_CAPS]
        assert {(m.vendor, m.price_basis, m.obtained) for m in members} == {(vendor, basis, saved)}
        assert {m.path.split("/")[0] for m in members} == {folder}
        assert len(members) == count == closes.shape[1] == 600


class TestThePairs:
    def test_752_pairs_from_the_first_fitting_day(self, results: Results) -> None:
        days = results.spliced.pairs.days
        assert len(days) == results.spliced.comparison.pairs == 752, SPEC
        assert str(days[0].date()) == "2005-01-18"
        assert str(days[-1].date()) == "2008-01-11"
        assert results.unspliced.comparison.pairs == 752, SPEC

    def test_every_factor_return_is_finite(self, results: Results) -> None:
        """No stock in a day's cross-section lacks a return on day t or day t + 1."""
        for result in (results.spliced, results.unspliced):
            assert np.isfinite(result.pairs.today).all(), SPEC
            assert np.isfinite(result.pairs.tomorrow).all(), SPEC

    def test_579_stocks_are_priced_on_every_row_the_pairs_read(self, results: Results) -> None:
        assert len(results.spliced.comparison.stocks) == 579, SPEC
        assert len(results.unspliced.comparison.stocks) == 578, SPEC
        assert SPLICED in results.spliced.comparison.stocks.index


class TestTheFigures:
    """Each figure the report prints and the log quotes, at four decimals."""

    def test_each_factors_statistic(self, results: Results) -> None:
        expected = (0.0316, 0.0778, -0.0189, 0.0305, 0.0710)
        assert results.spliced.comparison.factors == pytest.approx(expected, abs=FOUR), SPEC

    def test_each_factors_same_sign_share(self, results: Results) -> None:
        expected = (0.5226, 0.5146, 0.5106, 0.5173, 0.5000)
        assert results.spliced.same_sign == pytest.approx(expected, abs=FOUR), SPEC

    def test_the_stocks_median_and_quartiles(self, results: Results) -> None:
        c = results.spliced.comparison
        assert c.lower_quartile == pytest.approx(-0.0729, abs=FOUR), SPEC
        assert c.median == pytest.approx(-0.0283, abs=FOUR), SPEC
        assert c.upper_quartile == pytest.approx(0.0137, abs=FOUR), SPEC

    def test_each_factors_percentile_among_the_stocks(self, results: Results) -> None:
        c = results.spliced.comparison
        expected = (83.9378, 95.6822, 55.0950, 83.4197, 94.3005)
        assert [c.percentile(v) for v in c.factors] == pytest.approx(expected, abs=FOUR), SPEC

    def test_the_band_is_1_96_over_root_752(self, results: Results) -> None:
        band = results.spliced.comparison.band
        assert band == pytest.approx(0.0715, abs=FOUR), SPEC
        assert band == CRITICAL / math.sqrt(752)

    def test_only_pc2_falls_outside_the_band(self, results: Results) -> None:
        """PC2's 0.0778 is past 0.0715, and PC5's 0.0710 is just inside it."""
        c = results.spliced.comparison
        outside = [name for name, v in zip(NAMES, c.factors, strict=True) if abs(v) > c.band]
        assert outside == ["PC2"], SPEC

    def test_each_factors_newey_west_t_and_p(self, results: Results) -> None:
        t = (0.9029, 0.8254, -0.4034, 0.8743, 1.2697)
        p = (0.1833, 0.2046, 0.6567, 0.1910, 0.1021)
        assert results.spliced.t_newey_west == pytest.approx(t, abs=FOUR), SPEC
        assert results.spliced.p_values == pytest.approx(p, abs=FOUR), SPEC

    def test_no_factor_survives_benjamini_hochberg(self, results: Results) -> None:
        assert not results.spliced.survives.any(), SPEC

    def test_the_intercepts_two_figures(self, results: Results) -> None:
        assert results.spliced.intercept_uncentred == pytest.approx(-0.0395, abs=FOUR), SPEC
        assert results.spliced.intercept_pearson == pytest.approx(-0.0401, abs=FOUR), SPEC


class TestTheVerdicts:
    """One test per factor, named for its outcome, stating which half held."""

    def _verdict(self, results: Results, name: str) -> Verdict:
        (verdict,) = [v for v in results.spliced.verdicts() if v.factor == name]
        return verdict

    @pytest.mark.parametrize("name", ["PC1", "PC2", "PC4", "PC5"])
    def test_pc1_pc2_pc4_and_pc5_hold_above_zero_and_above_the_median_stock(
        self, results: Results, name: str
    ) -> None:
        verdict = self._verdict(results, name)
        assert verdict.above_zero, SPEC
        assert verdict.above_median, SPEC
        assert verdict.holds, SPEC

    def test_pc3_misses_below_zero_though_above_the_median_stock(self, results: Results) -> None:
        verdict = self._verdict(results, "PC3")
        assert not verdict.above_zero, SPEC
        assert verdict.above_median, SPEC
        assert not verdict.holds, SPEC

    def test_each_is_judged_against_the_median(self, results: Results) -> None:
        verdicts = results.spliced.verdicts()
        assert [v.factor for v in verdicts] == list(NAMES)
        for verdict in verdicts:
            assert verdict.median == results.spliced.comparison.median


class TestWithoutPMC:
    """Every figure again without the column whose two histories forward-fill into one return."""

    def test_each_factors_statistic(self, results: Results) -> None:
        expected = (0.0740, -0.0152, 0.0139, 0.0975, 0.0536)
        assert results.unspliced.comparison.factors == pytest.approx(expected, abs=FOUR), SPEC

    def test_each_factors_same_sign_share(self, results: Results) -> None:
        expected = (0.5199, 0.5146, 0.5133, 0.5146, 0.5053)
        assert results.unspliced.same_sign == pytest.approx(expected, abs=FOUR), SPEC

    def test_the_stocks_median_and_quartiles(self, results: Results) -> None:
        c = results.unspliced.comparison
        assert c.lower_quartile == pytest.approx(-0.0732, abs=FOUR), SPEC
        assert c.median == pytest.approx(-0.0283, abs=FOUR), SPEC
        assert c.upper_quartile == pytest.approx(0.0137, abs=FOUR), SPEC

    def test_each_factors_percentile_among_the_stocks(self, results: Results) -> None:
        c = results.unspliced.comparison
        expected = (94.9827, 57.0934, 75.2595, 98.0969, 89.9654)
        assert [c.percentile(v) for v in c.factors] == pytest.approx(expected, abs=FOUR), SPEC

    def test_the_band(self, results: Results) -> None:
        assert results.unspliced.comparison.band == pytest.approx(0.0715, abs=FOUR), SPEC

    def test_pc1_and_pc4_fall_outside_the_band(self, results: Results) -> None:
        c = results.unspliced.comparison
        outside = [name for name, v in zip(NAMES, c.factors, strict=True) if abs(v) > c.band]
        assert outside == ["PC1", "PC4"], SPEC

    def test_the_criterion_would_miss_pc2_rather_than_pc3(self, results: Results) -> None:
        """Not a verdict, since the verdicts read the forward-filled file, but which factor misses.

        PC2 falls below 0 and PC3 rises above it, so the one factor the
        criterion misses moves when one spliced symbol is dropped.
        """
        holds = {v.factor: (v.above_zero, v.above_median) for v in results.unspliced.verdicts()}
        assert holds == {
            "PC1": (True, True),
            "PC2": (False, True),
            "PC3": (True, True),
            "PC4": (True, True),
            "PC5": (True, True),
        }, SPEC

    def test_each_factors_newey_west_t_and_p(self, results: Results) -> None:
        t = (0.9754, -0.3926, 0.4221, 1.8537, 1.1759)
        p = (0.1647, 0.6527, 0.3365, 0.0319, 0.1198)
        assert results.unspliced.t_newey_west == pytest.approx(t, abs=FOUR), SPEC
        assert results.unspliced.p_values == pytest.approx(p, abs=FOUR), SPEC

    def test_no_factor_survives_benjamini_hochberg(self, results: Results) -> None:
        assert not results.unspliced.survives.any(), SPEC

    def test_the_intercepts_two_figures(self, results: Results) -> None:
        assert results.unspliced.intercept_uncentred == pytest.approx(-0.0394, abs=FOUR), SPEC
        assert results.unspliced.intercept_pearson == pytest.approx(-0.0401, abs=FOUR), SPEC


class TestOnRealDays:
    """The rules, checked on a handful of the file's own days rather than a synthetic window."""

    @pytest.mark.parametrize("i", [0, 300, 751])
    def test_each_factor_return_is_s_times_the_programs_slope(
        self, panel, results: Results, i: int
    ) -> None:
        _, closes = panel
        returns = matlab_returns(closes.ffill().to_numpy(dtype=float))
        t = LOOKBACK + 1 + i
        assert closes.index[t] == results.spliced.pairs.days[i]
        window = returns[t - LOOKBACK : t].T
        has = np.flatnonzero(np.isfinite(window).all(axis=1))
        vectors, singular = revised_matlab_components(window[has])
        design = np.column_stack([np.ones(len(has)), vectors * singular])
        pairs = results.spliced.pairs
        for day, factors, intercept in (
            (t, pairs.today[i], pairs.intercept_today[i]),
            (t + 1, pairs.tomorrow[i], pairs.intercept_tomorrow[i]),
        ):
            coefficients = np.linalg.lstsq(design, returns[day, has], rcond=None)[0]
            np.testing.assert_allclose(
                design @ coefficients,
                revised_matlab_expected(window[has], returns[day, has]),
                atol=1e-15,
            )
            np.testing.assert_allclose(factors, coefficients[1:] * singular, atol=1e-14)
            assert intercept == pytest.approx(coefficients[0], abs=1e-15)


#: Carried beside :data:`SPEC` by every pin the write-up added after the run.
AFTER_THE_RUN = "measured by the write-up after the verdicts, and decides nothing"


@pytest.fixture(scope="module")
def returns(panel) -> np.ndarray:
    _, closes = panel
    return file_returns(closes)


@pytest.fixture(scope="module")
def components(pca_factor_momentum_run) -> list[Decomposition]:
    """All 753 fitting days' decompositions, computed once for every pin below."""
    return pca_factor_momentum_run[1]


@pytest.fixture(scope="module")
def weights(pca_factor_momentum_run) -> WeightStatistics:
    """1,504 more decompositions, on 251 days before and ending each day t, so computed once."""
    return pca_factor_momentum_run[2]


class TestWhatThePostMeasured:
    """Numbers ``blog/pca-factor-momentum-lessons.md`` quotes that no row of Entry 42 declared.

    Every number in this class was measured after the run, on the same vintage
    and specification as :data:`SPEC`, and decides nothing. None of them moves
    a verdict. They explain why each pair reads one day's vectors, how much one
    symbol weighs in the components, and what the figure can draw.
    """

    def test_753_decompositions_give_one_day_after_each_of_the_752_pairs(
        self, components, results: Results
    ) -> None:
        assert len(components) == 753, SPEC
        days = results.spliced.pairs.days
        assert [d.end for d in components[:-1]] == list(range(LOOKBACK + 1, LOOKBACK + 1 + 752))
        assert components[-1].end == components[-2].end + 1
        assert len(days) == len(components) - 1

    def test_with_each_sign_fixed_by_rule_a_vector_still_flips_on_a_few_days(
        self, components
    ) -> None:
        """Day t's vector against day t + 1's, on the stocks both keep, over 752 pair days.

        The library's own signs are not pinned, because they differ between
        machines. On the two that ran this suite they flipped on about half
        the days, and PC2's count differed by 2.
        """
        fixed = [with_largest_weight_positive(d) for d in components]
        assert sign_flips(fixed).tolist() == [1, 14, 6, 22, 24], f"{SPEC}; {AFTER_THE_RUN}"

    def test_two_factors_swap_rank_on_15_of_752_days(self, components) -> None:
        assert swap_days(components) == 15, f"{SPEC}; {AFTER_THE_RUN}"

    def test_every_remaining_flip_moves_the_largest_weight_or_swaps_rank(
        self, panel, components
    ) -> None:
        """A vector turns over when its largest weight moves to a stock it weighed the other way.

        Of the 1, 14, 6, 22 and 24 flips, the stock holding the largest weight
        changed between the two days on 1, 14, 6, 20 and 23. Each of the three
        left falls on a day two or more factors swap rank, named by its
        earlier day.
        """
        _, closes = panel
        fixed = [with_largest_weight_positive(d) for d in components]
        flips, moved, others = np.zeros(FACTORS, int), np.zeros(FACTORS, int), []
        for earlier, later in zip(fixed[:-1], fixed[1:], strict=True):
            swapped = bool((match(earlier, later)[0] != np.arange(FACTORS)).any())
            for k in np.flatnonzero(np.diag(overlaps(earlier, later)) < 0):
                flips[k] += 1
                before = earlier.stocks[np.abs(earlier.vectors[:, k]).argmax()]
                after = later.stocks[np.abs(later.vectors[:, k]).argmax()]
                if before != after:
                    moved[k] += 1
                else:
                    others.append((NAMES[k], str(closes.index[earlier.end].date()), swapped))
        assert flips.tolist() == [1, 14, 6, 22, 24], SPEC
        assert moved.tolist() == [1, 14, 6, 20, 23], f"{SPEC}; {AFTER_THE_RUN}"
        assert others == [
            ("PC4", "2005-06-15", True),
            ("PC4", "2007-06-29", True),
            ("PC5", "2007-08-01", True),
        ], f"{SPEC}; {AFTER_THE_RUN}"

    def test_on_each_days_own_weights(self, weights) -> None:
        """A series rebuilt from each day's decomposition, each sign fixed by rule."""
        expected = (0.0326, -0.1105, -0.0283, -0.0315, 0.0025)
        assert weights.own == pytest.approx(expected, abs=FOUR), f"{SPEC}; {AFTER_THE_RUN}"

    def test_with_sign_and_rank_matched(self, weights) -> None:
        expected = (0.0246, -0.0161, -0.0318, -0.0285, 0.0768)
        assert weights.matched == pytest.approx(expected, abs=FOUR), f"{SPEC}; {AFTER_THE_RUN}"

    def test_with_tomorrows_weights_fitted_on_251_days_that_leave_today_out(self, weights) -> None:
        expected = (0.0315, 0.0776, -0.0228, 0.0338, 0.0713)
        assert weights.left_out == pytest.approx(expected, abs=FOUR), f"{SPEC}; {AFTER_THE_RUN}"

    def test_leaving_today_out_closes_most_of_the_gap_matching_leaves(
        self, weights, results: Results
    ) -> None:
        """Matched, the farthest factor sits 0.0938 from its paired statistic. Left out, 0.0039."""
        paired = results.spliced.comparison.factors
        assert round(float(np.abs(weights.matched - paired).max()), 4) == 0.0938, SPEC
        assert int(np.abs(weights.matched - paired).argmax()) == 1, "PC2"
        assert round(float(np.abs(weights.left_out - paired).max()), 4) == 0.0039, SPEC
        assert int(np.abs(weights.left_out - paired).argmax()) == 2, "PC3"

    def test_a_251_day_window_that_holds_today_reads_like_the_matched_row(self, weights) -> None:
        """The control for leaving today out: the same length, ending today rather than before it.

        It lands beside the matched row rather than beside the test's, so the
        shorter window is not what closes the gap. Leaving today out is.
        """
        expected = (0.0252, -0.0158, -0.0307, -0.0350, 0.0810)
        assert weights.shortened == pytest.approx(expected, abs=FOUR), f"{SPEC}; {AFTER_THE_RUN}"

    def test_113_pair_days_hold_pmcs_one_days_return(self, panel, components) -> None:
        """Its window ends the day before, so 114 fitting days hold it and the last has no pair."""
        _, closes = panel
        row = closes.index.get_loc(pd.Timestamp("2007-08-01"))
        holding = windows_holding(components, row)
        assert len(holding) == 114, SPEC
        pairs = windows_holding(components[:-1], row)
        assert len(pairs) == 113, f"{SPEC}; {AFTER_THE_RUN}"
        assert str(closes.index[pairs[0].end].date()) == "2007-08-02"
        assert str(closes.index[pairs[-1].end].date()) == "2008-01-11"

    def test_a_top_five_factor_weighs_pmc_at_0_5939_or_more_on_each(
        self, panel, components
    ) -> None:
        """Mostly PC2, on 103 of the 113, then PC1 on 7 and PC3 on 3."""
        _, closes = panel
        row = closes.index.get_loc(pd.Timestamp("2007-08-01"))
        column = closes.columns.get_loc(SPLICED)
        largest = [largest_loading(d, column) for d in windows_holding(components[:-1], row)]
        assert round(min(size for size, _ in largest), 4) == 0.5939, f"{SPEC}; {AFTER_THE_RUN}"
        carried = np.bincount([k for _, k in largest], minlength=FACTORS)
        assert carried.tolist() == [7, 103, 3, 0, 0], f"{SPEC}; {AFTER_THE_RUN}"

    def test_pmc_takes_pc1_through_2007_08_10_and_pc2_from_2007_08_13(
        self, panel, components
    ) -> None:
        """Its first seven days with a next day, at a weight between 0.9144 and 0.9223.

        So on 2007-08-09 and 2007-08-10, the two days that carry PC2's
        statistic, PC1 is PMC and PC2 is the factor that would otherwise be
        PC1.
        """
        _, closes = panel
        row = closes.index.get_loc(pd.Timestamp("2007-08-01"))
        column = closes.columns.get_loc(SPLICED)
        holding = windows_holding(components[:-1], row)
        largest = [largest_loading(d, column) for d in holding]
        days = [str(closes.index[d.end].date()) for d in holding]
        on_pc1 = [day for day, (_, k) in zip(days, largest, strict=True) if k == 0]
        assert on_pc1 == days[:7], f"{SPEC}; {AFTER_THE_RUN}"
        assert days[:8] == [
            "2007-08-02",
            "2007-08-03",
            "2007-08-06",
            "2007-08-07",
            "2007-08-08",
            "2007-08-09",
            "2007-08-10",
            "2007-08-13",
        ]
        sizes = [size for size, _ in largest[:7]]
        assert (round(min(sizes), 4), round(max(sizes), 4)) == (0.9144, 0.9223), SPEC
        assert largest[7][1] == 1, "PC2 from 2007-08-13"

    def test_without_pmc_the_same_two_days_carry_pc1(
        self, panel, returns, results: Results
    ) -> None:
        """94.61 percent of PC1's squared products, on the days PC2 carries them with PMC.

        On both days, the factor in PC2's place with PMC is the one in PC1's
        place without it, to an overlap of 0.98 or more in size on the stocks
        both runs keep.
        """
        pairs = results.unspliced.pairs
        share, days = share_of_largest(pairs.today[:, 0] * pairs.tomorrow[:, 0], 2)
        assert round(share, 4) == 0.9461, f"{SPEC}, without PMC; {AFTER_THE_RUN}"
        assert [str(pairs.days[i].date()) for i in days] == ["2007-08-09", "2007-08-10"]
        _, closes = panel
        without = closes.drop(columns=[SPLICED])
        returns_without = file_returns(without)
        for day in ("2007-08-09", "2007-08-10"):
            t = closes.index.get_loc(pd.Timestamp(day))
            spliced = decompose(returns, t)
            unspliced = decompose(returns_without, t)
            _, mine, theirs = np.intersect1d(
                closes.columns[spliced.stocks],
                without.columns[unspliced.stocks],
                return_indices=True,
            )
            overlap = spliced.vectors[mine, 1] @ unspliced.vectors[theirs, 0]
            assert abs(overlap) >= 0.98, f"{SPEC}; {AFTER_THE_RUN}"

    def test_dropping_the_intercept_moves_no_ranking_on_any_pair_day(
        self, returns, components
    ) -> None:
        agree = rankings_agree(returns, components)
        assert len(agree) == 752 and agree.all(), f"{SPEC}; {AFTER_THE_RUN}"

    def test_no_stock_ties_any_factor(self, results: Results) -> None:
        """What lets the figure's curve meet each factor at its percentile, which counts below."""
        assert f"{smallest_gap(results.spliced.comparison):.2e}" == "1.06e-04", SPEC
        assert f"{smallest_gap(results.unspliced.comparison):.2e}" == "3.85e-05", SPEC

    def test_the_whiteboard_draws_this_runs_figures(
        self, panel, components, results: Results, weights
    ) -> None:
        """The two sketches ``tests/test_pca_factor_momentum_whiteboard.py`` pins
        draw its ``PINNED_WINDOW`` and ``PINNED_RANK_SHIFT``, so they run without
        the decompositions. This holds that the run gives them, each figure
        within 1e-12 of the one the sketches were drawn from."""
        from chan.pca_factor_momentum_whiteboard import RankShift, Window
        from tests.test_pca_factor_momentum_whiteboard import PINNED_RANK_SHIFT, PINNED_WINDOW

        _, closes = panel
        drawn = (
            Window.from_run(results, weights),
            RankShift.from_run(closes, components, results),
        )
        for found, pinned in zip(drawn, (PINNED_WINDOW, PINNED_RANK_SHIFT), strict=True):
            for field in dataclasses.fields(pinned):
                value, expected = getattr(found, field.name), getattr(pinned, field.name)
                if field.name in ("span", "days", "others"):
                    assert value == expected, field.name
                else:
                    assert value == pytest.approx(expected, abs=1e-12), field.name

    def test_two_days_carry_97_percent_of_pc2s_squared_products(self, results: Results) -> None:
        """2007-08-09 and 2007-08-10, which is how PC2 clears the band and not the t-test."""
        pairs = results.spliced.pairs
        share, days = share_of_largest(pairs.today[:, 1] * pairs.tomorrow[:, 1], 2)
        assert round(share, 4) == 0.9704, f"{SPEC}; {AFTER_THE_RUN}"
        assert [str(pairs.days[i].date()) for i in days] == ["2007-08-09", "2007-08-10"]


class TestTheReport:
    def test_it_prints_every_figure_and_verdict(self, results: Results, panel, capsys) -> None:
        members, closes = panel
        report(members, closes, results)
        out = capsys.readouterr().out
        lines = out.splitlines()
        assert lines[0] == (
            "Whether Example 7.4's own factor returns have momentum, on Chan's S&P 600 file"
        )
        assert lines[1] == (
            "  closes   ijr_20080114/   chan-mat adjusted, saved 2008-01-15, "
            "600 members lifted from IJR_20080114.mat"
        )
        assert lines[3] == (
            "  rule     the revised MATLAB's components, lookback 252, 5 factors, "
            "f_t = u_k . r_t and f_t+1 = u_k . r_t+1 on day t's vectors"
        )
        assert "2004-01-15 to 2008-01-14, 1006 days, 600 stocks" in out
        assert "day t from 2005-01-18 to 2008-01-11, 752 pairs" in out
        assert "location 4051" in out
        for figure in (
            # with PMC
            "0.0316   83.94    0.5226   0.9029  0.1833   no",
            "0.0778   95.68    0.5146   0.8254  0.2046   no",
            "-0.0189   55.09    0.5106  -0.4034  0.6567   no",
            "0.0305   83.42    0.5173   0.8743  0.1910   no",
            "0.0710   94.30    0.5000   1.2697  0.1021   no",
            "lower quartile of 579    -0.0729",
            "median of 579            -0.0283",
            "upper quartile of 579     0.0137",
            "uncentred -0.0395, ordinary correlation -0.0401",
            # without PMC
            "0.0740   94.98    0.5199   0.9754  0.1647   no",
            "-0.0152   57.09    0.5146  -0.3926  0.6527   no",
            "0.0139   75.26    0.5133   0.4221  0.3365   no",
            "0.0975   98.10    0.5146   1.8537  0.0319   no",
            "0.0536   89.97    0.5053   1.1759  0.1198   no",
            "lower quartile of 578    -0.0732",
            "median of 578            -0.0283",
            "upper quartile of 578     0.0137",
            "uncentred -0.0394, ordinary correlation -0.0401",
            "= 0.0715",
        ):
            assert figure in out, figure
        claim = 'location 4014, factor returns "often" have stronger serial autocorrelation'
        for name in ("PC1", "PC2", "PC4", "PC5"):
            assert (
                f"Claim for {name}, {claim} than stocks: HOLDS. Above 0 and above the median stock."
            ) in out, name
        assert (
            f"Claim for PC3, {claim} than stocks: DOES NOT HOLD. Above the median stock, "
            "but not above 0."
        ) in out
        assert out.count("Claim for") == 5
        band = (
            "  Band +/-1.96/sqrt(752) = 0.0715, where a series of independent returns centred on "
            "zero stays inside 95 percent of the time. Decides nothing."
        )
        assert lines.count(band) == 2, "once with PMC and once without"
        for line in (
            "  Uncentred correlation of each day's factor return with the next day's",
            "  Quartiles by linear interpolation. The percentile counts stocks strictly below. "
            "NW t is one-sided, BH at q = 0.05.",
            "  Each factor is judged on its own: above 0 and above the median stock, unrounded, "
            "declared before any factor return was computed.",
            "  Without PMC, whose two price histories forward-fill into one day's return",
            "  The verdicts read the file as the program does, which forward-fills.",
            "  The file holds only the companies in the index on 2008-01-14, "
            "so every figure above is about survivors.",
            "  Exploratory. Testing a claim someone else chose spends the 2004 to 2008 sample "
            "on it, so this says whether",
            "  the claim holds on this file and nothing about factor momentum today. "
            "docs/replication-log.md Entry 42 carries the verdicts.",
        ):
            assert line in lines, line

    def test_run_reads_the_file_once_and_reports(
        self, results: Results, panel, monkeypatch, capsys
    ) -> None:
        """The closes ``run`` hands on are the Close column the pins read, not another field."""
        handed = []

        def capture(closes):
            handed.append(closes)
            return results

        monkeypatch.setattr(pca_factor_momentum, "compute_both", capture)
        assert run() is results
        assert "Claim for PC1" in capsys.readouterr().out
        (closes,) = handed
        pd.testing.assert_frame_equal(closes, panel[1])

    def test_an_empty_data_directory_is_refused_before_any_decomposition(
        self, tmp_path, monkeypatch
    ) -> None:
        def never(closes):
            raise AssertionError("a decomposition ran")

        monkeypatch.setattr(pca_factor_momentum, "compute_both", never)
        with pytest.raises(VintageUnavailable):
            run(data_dir=tmp_path)

    def test_main_prints_a_refusal_as_one_line(self, monkeypatch) -> None:
        def refuse(data_dir=None):
            raise VintageUnavailable("no committed vintage is lifted from IJR_20080114.mat")

        monkeypatch.setattr(pca_factor_momentum, "run", refuse)
        monkeypatch.setattr("sys.argv", ["pca_factor_momentum"])
        with pytest.raises(SystemExit, match="no committed vintage is lifted from IJR_20080114"):
            main()


# --- what the factor-models post quotes --------------------------------------------

FACTOR_MODELS_POST = paths.REPO_ROOT / "blog" / "factor-models-lessons.md"

#: The counts the post spells out.
WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}


def _minus(x: float, places: int) -> str:
    """A figure in prose, with the post's typographic minus sign."""
    return f"{x:.{places}f}".replace("-", "−")


def _array(head: str, rows: list[list[str]]) -> str:
    """One of the post's ``array`` tables, from its header row to its last row."""
    body = " \\\\\n".join(" & ".join(row) for row in rows)
    return f"{head} \\\\ \\hline\n{body}\n\\end{{array}}"


def _side(above: bool) -> str:
    return "above" if above else "below"


class TestWhatTheFactorModelsPostQuotes:
    """Each figure ``blog/factor-models-lessons.md`` quotes on Example 7.4's own factors.

    The classes above pin each figure once, and the post copies it by hand.
    Here each figure is built from the run or a module constant at the
    precision the post prints it, and looked for in one copy: a short fragment
    holding the number and the few words that name one place in the post. A
    typo in a copy that is read, or a re-pin that leaves the post behind,
    fails here. Lesson 3's daily table is rebuilt whole, its claim column from
    :meth:`chan.pca_factor_momentum.Result.verdicts`, so a digit added to a
    cell fails as well as a digit changed. Every factor a sentence names, and
    each count it spells out, comes from the run too, so a sentence that
    names the wrong factor fails as well. ``blog/pca-factor-momentum-lessons.md``
    is a different post, and this class does not read it.

    The copies read are the paragraphs on how each day's weights make a pair,
    the daily table, the paragraph after it, the three points that follow, and
    Lesson 6's third point. Other copies are not read, so a typo in one of
    them passes. Among them are the 1.8654 and 186.54 percent in the third
    point, which ``tests/test_pca_factor.py`` reads in Lesson 6, the 752 in
    Lesson 5, which counts days rather than pairs, and the "four of Example
    7.4's five" in the headings, subtitle and closing habits.
    """

    @pytest.fixture(scope="class")
    @classmethod
    def text(cls) -> str:
        return FACTOR_MODELS_POST.read_text(encoding="utf-8")

    @staticmethod
    def missing(text: str, fragments: list[str]) -> list[str]:
        return [fragment for fragment in fragments if fragment not in text]

    def test_how_each_pair_is_built(self, results: Results, text) -> None:
        c = results.spliced.comparison
        fragments = [
            f"The {WORDS[FACTORS]} factors are {NAMES[0]} to {NAMES[-1]},",
            f"{NAMES[0]} carries the most of the year’s variation in returns, and each later "
            "one less.",
            f"Each day’s weights come from the {LOOKBACK} days of returns that end the day before.",
            f"the correlation of the {c.pairs} pairs computed without subtracting their means "
            "first.",
            f"The same statistic is computed for each of the {len(c.stocks)} stocks with a "
            "return on every day the pairs read.",
            f"its percentile is the share of the {len(c.stocks)} stocks whose statistic is "
            "below it.",
        ]
        assert self.missing(text, fragments) == []

    def test_the_daily_table_and_its_verdicts(self, results: Results, text) -> None:
        c = results.spliced.comparison
        verdicts = results.spliced.verdicts()
        claim = {True: "\\text{holds}", False: "\\text{does not hold}"}
        (missed,) = [v for v in verdicts if not v.holds]
        held = sum(v.holds for v in verdicts)
        fragments = [
            _array(
                "\\small\\begin{array}{l|r|r|l}\n"
                "\\text{Factor} & \\text{Correlation} & \\text{Percentile} & \\text{Claim}",
                [
                    [
                        f"\\text{{{v.factor}}}",
                        f"{v.statistic:.4f}",
                        f"{c.percentile(v.statistic):.4f}",
                        claim[v.holds],
                    ]
                    for v in verdicts
                ],
            ),
            f"The median stock’s statistic is {_minus(c.median, 4)}. The claim that factors "
            f"“{OFTEN}” autocorrelate more strongly holds for {WORDS[held]} of the "
            f"{WORDS[len(verdicts)]}, and does not hold for {missed.factor}, which sits "
            f"{_side(missed.above_median)} the median stock but {_side(missed.above_zero)} 0.",
        ]
        assert self.missing(text, fragments) == []

    def test_the_band_and_the_test_across_all_five(self, results: Results, text) -> None:
        c = results.spliced.comparison
        outside = [(n, v) for n, v in zip(NAMES, c.factors, strict=True) if abs(v) > c.band]
        ((name, value),) = outside
        assert not results.spliced.survives.any(), SPEC
        assert (results.spliced.p_values >= FALSE_DISCOVERY).all(), SPEC
        k = NAMES.index(name)
        first, second = np.argsort(-np.abs(results.spliced.pairs.today[:, k]))[:2]
        assert abs(int(first) - int(second)) == 1, SPEC
        products = results.spliced.pairs.today[:, k] * results.spliced.pairs.tomorrow[:, k]
        signs = np.sign(products[np.argsort(-np.abs(products))[:2]])
        assert sorted(signs.tolist()) == [-1.0, 1.0], SPEC
        fragments = [
            f"Over {c.pairs} pairs it lands inside ±{CRITICAL}/√{c.pairs} = ±{c.band:.4f}",
            f"{name}’s {value:.4f} is outside it and the other {WORDS[FACTORS - 1]} are inside.",
            f"So the Benjamini-Hochberg procedure runs across all {WORDS[FACTORS]}. Among the "
            "factors it declares significant, it holds the expected share of false findings "
            f"to {100 * FALSE_DISCOVERY:.0f} percent. None survives, {name} included, and no "
            f"factor’s p-value would pass at {100 * FALSE_DISCOVERY:.0f} percent even alone.",
            f"{name}’s largest returns fell on neighbouring days, so two of its {c.pairs} "
            "products, one positive and one negative, are far larger in size than all the "
            "others.",
            f"which is how {name} can sit outside the band and still fail the test.",
        ]
        assert self.missing(text, fragments) == []

    def test_what_dropping_pmc_moves(self, results: Results, text) -> None:
        before, after = results.spliced, results.unspliced
        was = {v.factor: v for v in before.verdicts()}
        now = {v.factor: v for v in after.verdicts()}
        (fell,) = [n for n in NAMES if was[n].above_zero and not now[n].above_zero]
        (rose,) = [n for n in NAMES if not was[n].above_zero and now[n].above_zero]
        (missed,) = [n for n in NAMES if not was[n].holds]
        (spliced_outside,) = [n for n in NAMES if abs(was[n].statistic) > before.comparison.band]
        first, second = [n for n in NAMES if abs(now[n].statistic) > after.comparison.band]
        (passing,) = [k for k, p in enumerate(after.p_values) if p < FALSE_DISCOVERY]
        assert not after.survives.any(), SPEC
        fragments = [
            f"Without {SPLICED}, {fell} falls to {_minus(now[fell].statistic, 4)} and {rose} "
            f"rises to {now[rose].statistic:.4f}, so the claim would miss {fell} rather than "
            f"{missed}.",
            f"{first} at {now[first].statistic:.4f} and {second} at "
            f"{now[second].statistic:.4f} would sit outside the band in place of "
            f"{spliced_outside}.",
            f"{NAMES[passing]}’s one-sided p-value of {after.p_values[passing]:.4f} would then "
            f"pass at {100 * FALSE_DISCOVERY:.0f} percent on its own, but no factor would "
            f"survive the test across all {WORDS[FACTORS]}.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_6s_median(self, results: Results, text) -> None:
        median = results.spliced.comparison.median
        fragment = f"on the S&P 600 file the median daily statistic is {_minus(median, 4)}."
        assert self.missing(text, [fragment]) == []


# --- the rules, on data small enough to read ---------------------------------------


@pytest.fixture()
def closes() -> pd.DataFrame:
    """Twelve stocks over LOOKBACK + 6 days, so the pairs run over four fitting days.

    One stock has no close on the first day, so its first return is missing and
    the first window leaves it out.
    """
    rng = np.random.default_rng(11)
    steps = 1 + rng.normal(0, 0.02, size=(LOOKBACK + 6, 12))
    frame = pd.DataFrame(
        100 * np.cumprod(steps, axis=0),
        index=pd.bdate_range("2004-01-15", periods=LOOKBACK + 6),
        columns=[f"S{i}" for i in range(12)],
    )
    frame.iloc[0, 3] = np.nan
    return frame


@pytest.fixture()
def window() -> np.ndarray:
    """Twelve stocks over thirty days of returns, with enough spread for five factors."""
    return np.random.default_rng(7).normal(0, 0.02, size=(12, 30))


class TestTheRules:
    def test_the_pairs_run_over_every_fitting_day_with_a_next_row(self, closes) -> None:
        pairs = factor_pairs(closes)
        assert list(pairs.days) == list(closes.index[LOOKBACK + 1 : -1])
        assert pairs.today.shape == pairs.tomorrow.shape == (4, FACTORS)

    def test_both_members_of_a_pair_read_day_ts_vectors(self, closes) -> None:
        pairs = factor_pairs(closes)
        returns = matlab_returns(closes.ffill().to_numpy(dtype=float))
        for i, day in enumerate(pairs.days):
            t = closes.index.get_loc(day)
            window = returns[t - LOOKBACK : t].T
            has = np.flatnonzero(np.isfinite(window).all(axis=1))
            vectors, _ = revised_matlab_components(window[has])
            np.testing.assert_allclose(pairs.today[i], vectors.T @ returns[t, has], atol=1e-15)
            np.testing.assert_allclose(
                pairs.tomorrow[i], vectors.T @ returns[t + 1, has], atol=1e-15
            )
            assert pairs.intercept_today[i] == pytest.approx(returns[t, has].mean(), abs=1e-17)
            assert pairs.intercept_tomorrow[i] == pytest.approx(
                returns[t + 1, has].mean(), abs=1e-17
            )
        first_window = returns[1 : LOOKBACK + 1].T
        assert int(np.isfinite(first_window).all(axis=1).sum()) == 11

    def test_a_flipped_vector_moves_no_product_and_no_statistic(self, closes, monkeypatch) -> None:
        """A singular vector's sign is arbitrary, so flipping one on one day changes nothing."""
        pairs = factor_pairs(closes)
        calls = {"n": 0}

        def flipped(window):
            vectors, singular = revised_matlab_components(window)
            calls["n"] += 1
            if calls["n"] == 3:
                vectors = vectors.copy()
                vectors[:, 1] *= -1
            return vectors, singular

        monkeypatch.setattr(pca_factor_momentum, "revised_matlab_components", flipped)
        moved = factor_pairs(closes)
        assert moved.today[2, 1] == -pairs.today[2, 1]
        np.testing.assert_array_equal(moved.today * moved.tomorrow, pairs.today * pairs.tomorrow)
        np.testing.assert_array_equal(
            uncentred(moved.today, moved.tomorrow), uncentred(pairs.today, pairs.tomorrow)
        )

    def test_a_factor_return_is_s_times_the_programs_slope(self, window) -> None:
        """f_t[k] = u_k · r_t, and the slope the program fits is that over s_k."""
        today = np.random.default_rng(8).normal(0, 0.02, size=len(window))
        vectors, singular = revised_matlab_components(window)
        design = np.column_stack([np.ones(len(window)), vectors * singular])
        coefficients = np.linalg.lstsq(design, today, rcond=None)[0]
        np.testing.assert_allclose(design @ coefficients, revised_matlab_expected(window, today))
        np.testing.assert_allclose(vectors.T @ today, coefficients[1:] * singular, atol=1e-15)
        assert not np.allclose(vectors.T @ today, coefficients[1:])

    def test_the_intercept_is_the_days_mean(self, window) -> None:
        today = np.random.default_rng(9).normal(0, 0.02, size=len(window))
        vectors, singular = revised_matlab_components(window)
        design = np.column_stack([np.ones(len(window)), vectors * singular])
        intercept = np.linalg.lstsq(design, today, rcond=None)[0][0]
        assert intercept == pytest.approx(today.mean(), abs=1e-17)

    def test_the_components_are_unit_length_and_ranked(self, window) -> None:
        vectors, singular = revised_matlab_components(window)
        assert vectors.shape == (len(window), FACTORS)
        np.testing.assert_allclose(vectors.T @ vectors, np.eye(FACTORS), atol=1e-14)
        assert (np.diff(singular) <= 0).all() and (singular > 0).all()

    def test_the_statistic_is_uncentred(self) -> None:
        """5 / √(14 · 5) by hand, where the centred correlation is −0.5."""
        first, second = np.array([1.0, 2.0, 3.0]), np.array([2.0, 0.0, 1.0])
        assert float(uncentred(first, second)) == pytest.approx(5 / math.sqrt(70), abs=1e-15)
        assert np.corrcoef(first, second)[0, 1] == pytest.approx(-0.5)

    def test_the_statistic_runs_down_each_column(self) -> None:
        first = np.array([[1.0, 1.0], [2.0, -1.0], [3.0, 1.0]])
        second = np.array([[2.0, 1.0], [0.0, -1.0], [1.0, 1.0]])
        assert uncentred(first, second) == pytest.approx([5 / math.sqrt(70), 1.0], abs=1e-15)

    def test_a_steady_mean_counts_as_persistence(self) -> None:
        """A series holding a steady value reads as persistent, which a centred statistic misses."""
        steady = np.array([1.0, 1.2, 0.9, 1.1, 1.0])
        assert float(uncentred(steady[:-1], steady[1:])) > 0.95
        assert np.corrcoef(steady[:-1], steady[1:])[0, 1] < 0

    def test_the_steady_series_reads_0_9798_uncentred_and_minus_0_8_centred(self) -> None:
        """The two figures the post quotes for the series above, at four decimals."""
        steady = np.array([1.0, 1.2, 0.9, 1.1, 1.0])
        assert round(float(uncentred(steady[:-1], steady[1:])), 4) == 0.9798
        assert round(float(np.corrcoef(steady[:-1], steady[1:])[0, 1]), 4) == -0.8

    def test_the_comparison_set_needs_every_row_the_pairs_read(self, closes) -> None:
        """A gap before the first fitting day leaves a stock in, and one after leaves it out."""
        frame = closes.copy()
        frame.iloc[: LOOKBACK + 1, 5] = np.nan  # no return until row LOOKBACK + 2
        frame.iloc[: LOOKBACK - 1, 7] = np.nan  # no return until row LOOKBACK
        stocks = stock_statistics(frame)
        assert "S5" not in stocks.index
        assert "S7" in stocks.index and "S3" in stocks.index
        returns = matlab_returns(frame.ffill().to_numpy(dtype=float))[LOOKBACK + 1 :, 7]
        assert stocks["S7"] == pytest.approx(float(uncentred(returns[:-1], returns[1:])))

    def test_the_same_sign_share_counts_only_strictly_positive_products(self, closes) -> None:
        """A day when every stock is flat makes two pairs' products exactly 0, and neither counts.

        Every return on that day is 0, so its factor returns are 0. The pair
        it is today in and the pair it is tomorrow in both multiply to 0,
        which shares no sign, so at most two of the four pairs can count.
        """
        frame = closes.copy()
        flat = LOOKBACK + 3
        frame.iloc[flat] = frame.iloc[flat - 1]
        result = compute(frame)
        products = result.pairs.today * result.pairs.tomorrow
        assert (products[1:3] == 0).all()
        np.testing.assert_array_equal(result.same_sign * 4, (products[[0, 3]] > 0).sum(axis=0))
        assert (result.same_sign <= 0.5).all()

    def test_the_comparison_reads_the_forward_filled_closes(self, closes) -> None:
        """A close missing after the first fitting day is filled, so its stock stays in."""
        frame = closes.copy()
        frame.iloc[LOOKBACK + 3, 9] = np.nan
        assert "S9" in stock_statistics(frame).index


def _decomposition(vectors: np.ndarray, stocks=None, end: int = 0) -> Decomposition:
    stocks = np.arange(len(vectors)) if stocks is None else np.asarray(stocks)
    return Decomposition(end=end, stocks=stocks, vectors=vectors, singular=np.ones(FACTORS))


@pytest.fixture()
def unit() -> np.ndarray:
    """Five orthonormal columns over eight stocks."""
    q, _ = np.linalg.qr(np.random.default_rng(3).normal(size=(8, FACTORS)))
    return q


class TestThePostsHelpers:
    """The write-up's helpers, each on data small enough to work by hand."""

    def test_a_decomposition_reads_the_lookback_rows_before_its_end(self, closes) -> None:
        returns = file_returns(closes)
        d = decompose(returns, LOOKBACK + 2)
        window = returns[2 : LOOKBACK + 2].T
        vectors, singular = revised_matlab_components(window)
        assert d.end == LOOKBACK + 2 and d.stocks.tolist() == list(range(12))
        # Selecting the kept stocks copies the window into another memory
        # layout, so the decomposition agrees to rounding rather than bit for bit.
        np.testing.assert_allclose(d.vectors, vectors, atol=1e-12)
        np.testing.assert_allclose(d.singular, singular, rtol=1e-12)

    def test_a_shorter_lookback_reads_fewer_rows_before_the_same_end(self, closes) -> None:
        returns = file_returns(closes)
        d = decompose(returns, LOOKBACK + 2, LOOKBACK - 1)
        vectors, _ = revised_matlab_components(returns[3 : LOOKBACK + 2].T)
        np.testing.assert_allclose(d.vectors, vectors, atol=1e-12)
        assert not np.allclose(decompose(returns, LOOKBACK + 2).vectors, vectors, atol=1e-6)

    def test_a_stock_missing_a_return_in_the_window_is_left_out(self, closes) -> None:
        d = decompose(file_returns(closes), LOOKBACK + 1)
        assert 3 not in d.stocks.tolist() and len(d.stocks) == 11

    def test_daily_components_run_over_every_fitting_day_including_the_last(self, closes) -> None:
        components = daily_components(file_returns(closes))
        assert [d.end for d in components] == list(range(LOOKBACK + 1, len(closes)))
        assert len(factor_pairs(closes).days) == len(components) - 1

    def test_overlaps_read_only_the_stocks_both_keep(self, unit) -> None:
        earlier = _decomposition(unit[:6], stocks=range(6))
        later = _decomposition(unit[2:], stocks=range(2, 8))
        np.testing.assert_allclose(overlaps(earlier, later), unit[2:6].T @ unit[2:6])

    def test_a_vector_pointed_the_other_way_counts_as_one_flip(self, unit) -> None:
        flipped = unit.copy()
        flipped[:, 3] *= -1
        days = [_decomposition(unit), _decomposition(flipped), _decomposition(flipped)]
        assert sign_flips(days).tolist() == [0, 0, 0, 1, 0]

    def test_any_negative_overlap_is_a_flip_however_far_the_vector_moved(self, unit) -> None:
        """Tomorrow's vector is rarely today's exactly reversed, so only the sign counts."""
        tilted = unit.copy()
        tilted[:, 2] = -0.6 * unit[:, 2] + 0.8 * unit[:, 4]
        tilted[:, 4] = 0.8 * unit[:, 2] + 0.6 * unit[:, 4]
        assert np.diag(overlaps(_decomposition(unit), _decomposition(tilted)))[2] == pytest.approx(
            -0.6
        )
        assert sign_flips([_decomposition(unit), _decomposition(tilted)]).tolist() == [
            0,
            0,
            1,
            0,
            0,
        ]

    def test_match_finds_a_swap_and_a_flip(self, unit) -> None:
        later = unit[:, [0, 2, 1, 3, 4]].copy()
        later[:, 0] *= -1
        order, signs = match(_decomposition(unit), _decomposition(later))
        assert order.tolist() == [0, 2, 1, 3, 4]
        assert signs.tolist() == [-1.0, 1.0, 1.0, 1.0, 1.0]

    def test_match_maximises_the_summed_overlap_rather_than_each_row_greedily(self) -> None:
        """Row 0 alone prefers column 0, but the pairing 0.8 + 0.7 beats 0.9 + 0.1."""
        later = np.eye(FACTORS)
        later[:2, :2] = [[0.9, 0.8], [0.7, 0.1]]
        order, signs = match(_decomposition(np.eye(FACTORS)), _decomposition(later))
        assert order.tolist() == [1, 0, 2, 3, 4]
        assert signs.tolist() == [1.0] * FACTORS

    def test_a_swap_day_is_any_day_whose_order_moves(self, unit) -> None:
        swapped = unit[:, [0, 1, 2, 4, 3]]
        flipped = -unit
        days = [_decomposition(m) for m in (unit, swapped, swapped, flipped)]
        assert swap_days(days) == 2

    def test_the_four_statistics_by_hand(self, closes) -> None:
        returns = file_returns(closes)
        components = []
        for d in daily_components(returns):
            columns = np.arange(FACTORS)
            signs = np.sign(d.vectors[np.abs(d.vectors).argmax(axis=0), columns])
            components.append(Decomposition(d.end, d.stocks, d.vectors * signs, d.singular))
        today, own, matched, left_out, shortened = [], [], [], [], []
        for d, after in zip(components[:-1], components[1:], strict=True):
            t = d.end
            today.append(d.vectors.T @ returns[t, d.stocks])
            tomorrow = after.vectors.T @ returns[t + 1, after.stocks]
            own.append(tomorrow)
            order, signs = match(d, after)
            matched.append(signs * tomorrow[order])
            window = returns[t - LOOKBACK + 1 : t].T
            assert window.shape[1] == LOOKBACK - 1
            vectors, _ = revised_matlab_components(window)  # every stock is priced from row 2
            order, signs = match(d, _decomposition(vectors))
            left_out.append(signs * (vectors.T @ returns[t + 1])[order])
            window = returns[t - LOOKBACK + 2 : t + 1].T
            assert window.shape[1] == LOOKBACK - 1
            vectors, _ = revised_matlab_components(window)  # rows t − 250 to t, holding r_t
            order, signs = match(d, _decomposition(vectors))
            shortened.append(signs * (vectors.T @ returns[t + 1])[order])
        stats = weight_statistics(returns, components)
        np.testing.assert_allclose(stats.own, uncentred(np.array(today), np.array(own)))
        np.testing.assert_allclose(stats.matched, uncentred(np.array(today), np.array(matched)))
        np.testing.assert_allclose(
            stats.left_out, uncentred(np.array(today), np.array(left_out)), atol=1e-14
        )
        np.testing.assert_allclose(
            stats.shortened, uncentred(np.array(today), np.array(shortened)), atol=1e-14
        )

    def test_no_statistic_depends_on_the_signs_the_library_returns(self, closes) -> None:
        """Flip any vectors on any days, and all four statistics come back the same."""
        returns = file_returns(closes)
        components = daily_components(returns)
        before = weight_statistics(returns, components)
        flipped = [
            Decomposition(d.end, d.stocks, d.vectors * signs, d.singular)
            for d, signs in zip(
                components,
                np.random.default_rng(5).choice([-1.0, 1.0], size=(len(components), FACTORS)),
                strict=True,
            )
        ]
        assert any((f.vectors != d.vectors).any() for f, d in zip(flipped, components, strict=True))
        after = weight_statistics(returns, flipped)
        np.testing.assert_array_equal(after.own, before.own)
        np.testing.assert_array_equal(after.matched, before.matched)
        np.testing.assert_array_equal(after.left_out, before.left_out)
        np.testing.assert_array_equal(after.shortened, before.shortened)

    def test_the_rule_makes_each_vectors_largest_weight_positive(self, unit) -> None:
        mixed = unit * np.array([1.0, -1.0, 1.0, -1.0, -1.0])
        fixed = with_largest_weight_positive(_decomposition(mixed)).vectors
        largest = np.abs(fixed).argmax(axis=0)
        assert (fixed[largest, np.arange(FACTORS)] > 0).all()
        np.testing.assert_array_equal(np.abs(fixed), np.abs(mixed))
        np.testing.assert_array_equal(
            with_largest_weight_positive(_decomposition(-mixed)).vectors, fixed
        )

    def test_the_rule_reads_the_largest_weight_by_size(self) -> None:
        """A vector flips when its largest weight is negative, though most of the others are not."""
        vectors = np.zeros((4, FACTORS))
        vectors[:, 0] = [0.3, 0.3, 0.3, -0.85]
        fixed = with_largest_weight_positive(_decomposition(vectors)).vectors
        assert fixed[:, 0].tolist() == [-0.3, -0.3, -0.3, 0.85]

    def test_a_window_holds_a_row_from_the_day_after_it_for_lookback_days(self, closes) -> None:
        components = daily_components(file_returns(closes))
        row = LOOKBACK + 2
        assert [d.end for d in windows_holding(components, row)] == [
            LOOKBACK + 3,
            LOOKBACK + 4,
            LOOKBACK + 5,
        ]
        assert [d.end for d in windows_holding(components, 1)] == [LOOKBACK + 1]
        assert windows_holding(components, 0) == []

    def test_the_largest_loading_is_by_size_and_names_its_factor(self) -> None:
        vectors = np.zeros((3, FACTORS))
        vectors[1] = [0.1, -0.7, 0.3, 0.0, 0.2]
        d = _decomposition(vectors, stocks=[4, 9, 11])
        assert largest_loading(d, 9) == (0.7, 1)

    def test_dropping_the_intercept_leaves_the_fitted_values_less_the_days_mean(
        self, window
    ) -> None:
        today = np.random.default_rng(10).normal(0, 0.02, size=len(window))
        np.testing.assert_allclose(
            without_the_intercept(window, today),
            revised_matlab_expected(window, today) - today.mean(),
            atol=1e-15,
        )

    def test_rankings_agree_on_every_synthetic_pair_day(self, closes) -> None:
        returns = file_returns(closes)
        agree = rankings_agree(returns, daily_components(returns))
        assert agree.tolist() == [True] * 4

    def test_rankings_read_each_pair_days_window_and_return(self, closes, monkeypatch) -> None:
        """Both rankings read the 252 rows before the day and that day's returns.

        Neither agreement pin can show this. Dropping the intercept leaves
        the fitted values less the day's mean for any window and any day, so the
        two rankings agree whichever rows they read. Recording the arguments is
        what fails when a ranking reads the next day or a window shifted by one.
        """
        returns = file_returns(closes)
        components = daily_components(returns)
        seen = {"revised_matlab_expected": [], "without_the_intercept": []}

        def recorder(name):
            def record(window, today):
                seen[name].append((window.copy(), today.copy()))
                return today

            return record

        for name in seen:
            monkeypatch.setattr(pca_factor_momentum, name, recorder(name))
        rankings_agree(returns, components)
        for calls in seen.values():
            assert len(calls) == len(components) - 1
            for (window, today), d in zip(calls, components[:-1], strict=True):
                np.testing.assert_array_equal(window, returns[d.end - LOOKBACK : d.end].T[d.stocks])
                np.testing.assert_array_equal(today, returns[d.end, d.stocks])

    def test_a_ranking_on_another_key_disagrees(self, closes, monkeypatch) -> None:
        """The check can fail: the fitted values reversed give the opposite order."""
        returns = file_returns(closes)
        monkeypatch.setattr(
            pca_factor_momentum,
            "without_the_intercept",
            lambda window, today: -revised_matlab_expected(window, today),
        )
        assert not rankings_agree(returns, daily_components(returns)).any()

    def test_the_smallest_gap_is_the_nearest_stock_to_any_factor(self) -> None:
        c = Comparison(np.array([0.1, 0.2, 0.3, 0.4, 0.5]), pd.Series([0.0, 0.33, 0.9]), pairs=752)
        assert smallest_gap(c) == pytest.approx(0.03, abs=1e-15)

    def test_the_share_of_the_largest_squares(self) -> None:
        share, positions = share_of_largest(np.array([3.0, 1.0, -4.0, 0.0]), 2)
        assert share == pytest.approx(25 / 26, abs=1e-15)
        assert positions.tolist() == [0, 2]


class TestTheCriterion:
    def test_above_both_holds(self) -> None:
        verdict = Verdict("X", 0.1, 0.0)
        assert verdict.holds
        assert verdict.line() == "HOLDS. Above 0 and above the median stock"

    def test_above_zero_alone_does_not(self) -> None:
        verdict = Verdict("X", 0.1, 0.2)
        assert not verdict.holds
        assert verdict.line() == "DOES NOT HOLD. Above 0, but not above the median stock"

    def test_above_the_median_alone_does_not(self) -> None:
        verdict = Verdict("X", -0.01, -0.03)
        assert not verdict.holds
        assert verdict.line() == "DOES NOT HOLD. Above the median stock, but not above 0"

    def test_below_both_does_not(self) -> None:
        verdict = Verdict("X", -0.1, 0.0)
        assert not verdict.holds
        assert verdict.line() == "DOES NOT HOLD. Neither above 0 nor above the median stock"

    def test_equal_to_the_median_is_not_above_it(self) -> None:
        assert not Verdict("X", 0.1, 0.1).holds

    def test_zero_is_not_above_zero(self) -> None:
        assert not Verdict("X", 0.0, -0.1).holds

    def test_the_quartiles_interpolate_linearly(self) -> None:
        c = Comparison(np.zeros(FACTORS), pd.Series([0.0, 1.0, 2.0, 3.0]), pairs=752)
        assert (c.lower_quartile, c.median, c.upper_quartile) == (0.75, 1.5, 2.25)

    def test_the_percentile_counts_strictly_below(self) -> None:
        c = Comparison(np.zeros(FACTORS), pd.Series([-1.0, 0.0, 1.0, 2.0]), pairs=752)
        assert c.percentile(0.0) == 25.0


class TestTheFiguresRow:
    def test_a_factor_that_survives_benjamini_hochberg_reads_yes(self, capsys) -> None:
        """The file has no survivor, so only a constructed result shows the column saying yes."""
        empty = np.zeros((0, FACTORS))
        result = Result(
            pairs=Pairs(pd.DatetimeIndex([]), empty, empty, np.zeros(0), np.zeros(0)),
            comparison=Comparison(np.full(FACTORS, 0.1), pd.Series([0.0, 0.2]), pairs=752),
            same_sign=np.full(FACTORS, 0.5),
            t_newey_west=np.full(FACTORS, 1.0),
            p_values=np.full(FACTORS, 0.2),
            survives=np.array([False, True, False, False, False]),
            intercept_uncentred=0.0,
            intercept_pearson=0.0,
        )
        _figures(result)
        rows = {
            line.split()[0]: line.split()[-1]
            for line in capsys.readouterr().out.splitlines()
            if line.split()[0] in NAMES
        }
        assert rows == {"PC1": "no", "PC2": "yes", "PC3": "no", "PC4": "no", "PC5": "no"}


class TestTheSignificance:
    def test_the_p_value_is_one_sided(self) -> None:
        assert one_sided_p(0.0) == 0.5
        assert one_sided_p(1.96) == pytest.approx(0.025, abs=1e-4)
        assert one_sided_p(-1.0) == pytest.approx(1 - one_sided_p(1.0), abs=1e-15)

    def test_benjamini_hochberg_rejects_the_first_three(self) -> None:
        p = np.array([0.01, 0.02, 0.03, 0.2, 0.5])
        assert benjamini_hochberg(p).tolist() == [True, True, True, False, False]
        assert benjamini_hochberg(p[::-1]).tolist() == [False, False, True, True, True]

    def test_the_ith_smallest_is_held_to_i_over_m(self) -> None:
        """0.04 is above 1 · 0.05 / 2 and below 2 · 0.05 / 2, so where i starts decides it."""
        assert benjamini_hochberg(np.array([0.04, 0.5])).tolist() == [False, False]
        assert benjamini_hochberg(np.array([0.025, 0.5])).tolist() == [True, False]

    def test_it_steps_up_past_a_smaller_p_that_failed(self) -> None:
        """0.03 fails 0.025, but 0.04 passes 0.05, so both are rejected."""
        assert benjamini_hochberg(np.array([0.04, 0.03])).tolist() == [True, True]

    def test_none_passing_rejects_none(self) -> None:
        assert not benjamini_hochberg(np.array([0.5, 0.6, 0.7])).any()
