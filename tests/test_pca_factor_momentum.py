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


def _flips_by_cause(components: list[Decomposition], closes: pd.DataFrame):
    """Each factor's flips between consecutive days, once every sign is fixed by rule.

    Returns four things. The flips, the ones where the stock holding the
    largest weight changed, and the ones where it moved to a stock the earlier
    day weighed below zero, each counted by factor. Then every other flip as
    its factor, its earlier day, and whether two or more factors swap rank
    that day.
    """
    fixed = [with_largest_weight_positive(d) for d in components]
    flips, moved, opposite, others = (
        np.zeros(FACTORS, int),
        np.zeros(FACTORS, int),
        np.zeros(FACTORS, int),
        [],
    )
    for earlier, later in zip(fixed[:-1], fixed[1:], strict=True):
        swapped = bool((match(earlier, later)[0] != np.arange(FACTORS)).any())
        for k in np.flatnonzero(np.diag(overlaps(earlier, later)) < 0):
            flips[k] += 1
            before = earlier.stocks[np.abs(earlier.vectors[:, k]).argmax()]
            after = later.stocks[np.abs(later.vectors[:, k]).argmax()]
            held = np.flatnonzero(earlier.stocks == after)
            moved[k] += before != after
            if before != after and held.size and earlier.vectors[held[0], k] < 0:
                opposite[k] += 1
            else:
                others.append((NAMES[k], str(closes.index[earlier.end].date()), swapped))
    return flips, moved, opposite, others


class TestWhatThePostMeasured:
    """Numbers measured after the run that no row of Entry 42 declared.

    ``blog/pca-factor-momentum-lessons.md`` quotes most of them. The rest, such
    as the 753 decompositions, the control row's other four factors and each
    gap between a factor and its nearest stock, back sentences the post writes
    in words rather than figures.

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

    def test_two_or_more_factors_swap_rank_on_15_of_752_days(self, components) -> None:
        assert swap_days(components) == 15, f"{SPEC}; {AFTER_THE_RUN}"

    def test_every_flip_but_five_moves_the_largest_weight_to_a_stock_weighed_below_zero(
        self, panel, components
    ) -> None:
        """All but five flips move the largest weight to a stock the earlier day weighed below zero.

        Of the 1, 14, 6, 22 and 24 flips, the stock holding the largest weight
        changed between the two days on 1, 14, 6, 20 and 23, and the earlier
        day had weighed the new one below zero on 1, 14, 5, 19 and 23. Each of
        the five left falls on a day two or more factors swap rank, named by
        its earlier day.
        """
        _, closes = panel
        flips, moved, opposite, others = _flips_by_cause(components, closes)
        assert flips.tolist() == [1, 14, 6, 22, 24], SPEC
        assert moved.tolist() == [1, 14, 6, 20, 23], f"{SPEC}; {AFTER_THE_RUN}"
        assert opposite.tolist() == [1, 14, 5, 19, 23], f"{SPEC}; {AFTER_THE_RUN}"
        assert others == [
            ("PC3", "2005-06-15", True),
            ("PC4", "2005-06-15", True),
            ("PC4", "2007-06-29", True),
            ("PC4", "2007-08-01", True),
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

        On every day PMC carries PC1, 2007-08-02 to 2007-08-10, the factor in
        PC2's place with PMC is the one in PC1's place without it, to an overlap
        of 0.98 or more in size on the stocks both runs keep. The post says so
        for the two large days, and the rank shift sketch draws it for all seven.
        """
        pairs = results.unspliced.pairs
        share, days = share_of_largest(pairs.today[:, 0] * pairs.tomorrow[:, 0], 2)
        assert round(share, 4) == 0.9461, f"{SPEC}, without PMC; {AFTER_THE_RUN}"
        assert [str(pairs.days[i].date()) for i in days] == ["2007-08-09", "2007-08-10"]
        _, closes = panel
        without = closes.drop(columns=[SPLICED])
        returns_without = file_returns(without)
        for day in (
            "2007-08-02",
            "2007-08-03",
            "2007-08-06",
            "2007-08-07",
            "2007-08-08",
            "2007-08-09",
            "2007-08-10",
        ):
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


# --- what the post quotes -----------------------------------------------------------

POST = paths.REPO_ROOT / "blog" / "pca-factor-momentum-lessons.md"

#: The one fraction the post spells out, a fifth of the false-discovery rate.
ORDINALS = {5: "fifth"}


def _listed(items: list[str]) -> str:
    """Items as the post lists them, "PC1, PC2, PC4 and PC5"."""
    return items[0] if len(items) == 1 else f"{', '.join(items[:-1])} and {items[-1]}"


def _table(spec: str, header: list[str], rows: list[list[str]], last: list[str] | None = None):
    """One of the post's ``math`` tables, from ``\\small`` to its end, with an optional last row.

    The last row sits below a second rule, as Lesson 5's median stock does.
    """
    cells = [" & ".join(row) for row in [header, *rows]]
    table = f"\\small\n\\begin{{array}}{{{spec}}}\n{cells[0]} \\\\ \\hline\n"
    table += " \\\\\n".join(cells[1:])
    if last is not None:
        table += f" \\\\ \\hline\n{' & '.join(last)}"
    return f"{table}\n\\end{{array}}"


def _gap(closes: pd.DataFrame) -> tuple[int, int]:
    """The rows either side of PMC's longest run of missing closes, both priced."""
    missing = np.r_[0, closes[SPLICED].isna().to_numpy().astype(int), 0]
    starts = np.flatnonzero(np.diff(missing) == 1)
    ends = np.flatnonzero(np.diff(missing) == -1)
    longest = int(np.argmax(ends - starts))
    return int(starts[longest]) - 1, int(ends[longest])


def _text(name: str) -> str:
    return f"\\text{{{name}}}"


class TestWhatThePostQuotes:
    """Each figure ``blog/pca-factor-momentum-lessons.md`` quotes, read against the run.

    The classes above pin each figure once, and the post copies it by hand.
    Here each figure is built from the run, the file or a module constant at
    the precision the post prints it, and looked for in one copy: a short
    fragment holding the number and the few words that name one place in the
    post. A typo in a copy that is read, or a re-pin that leaves the post
    behind, fails here. The tables in Lessons 1, 4 and 5 are rebuilt whole, so
    a digit added to a cell fails as well as a digit changed. Every factor a
    sentence names, and each count it spells out, comes from the run too, so a
    sentence that names the wrong factor fails as well. PMC's 1.8654 and its
    851 days are pinned on the file by ``TestTheSplice`` in
    ``tests/test_pca_factor.py``, and this class rebuilds them from the file
    only to read the post's copy.

    The copies read are these.

    - The section on how the test works: the file, the decomposition, the
      first day and the pair count, the criterion, and the comparison set.
    - Lesson 1's counts of flips and swaps, the 251-day window in the list
      before its table, the table, and the two paragraphs after it.
    - Lesson 2's two worked series, PC2's two days and their share, and the
      same-sign shares.
    - Lesson 3's count of checked days and its intercept figures.
    - Lesson 4's table, its quartiles, its verdicts and its three points.
    - Lesson 5's splice, its weights on PMC, the two sentences before its table,
      the table and the paragraph after it.

    Other copies are not read, so a typo in one of them passes. Among them
    are the repeats of 600, 252, 251, 579, 752 and the dates elsewhere, such
    as the 752 days t in Lesson 3 and the two dates in Lesson 4's second
    point, the "four of" five in the title, the subtitle and Lesson 4's
    heading, Chan's 2 percent, the figure's alt text and caption, the closing
    habits, the page numbers and the references.
    ``tests/test_pca_factor_momentum_figures.py`` holds what the figure draws.
    """

    @pytest.fixture(scope="class")
    @classmethod
    def text(cls) -> str:
        return POST.read_text(encoding="utf-8")

    @staticmethod
    def missing(text: str, fragments: list[str]) -> list[str]:
        return [fragment for fragment in fragments if fragment not in text]

    def test_how_the_test_works(self, panel, results: Results, text) -> None:
        members, closes = panel
        (saved,) = {m.obtained for m in members}
        c = results.spliced.comparison
        days = results.spliced.pairs.days
        assert days[-1] == closes.index[-2], "the second-to-last row"
        fragments = [
            f"holds the {closes.shape[1]} members of the S&P 600 as he saved them on {saved}, "
            f"with {len(closes):,} trading days of closes from {closes.index[0].date()} to "
            f"{closes.index[-1].date()}.",
            f"It takes the {LOOKBACK} daily returns ending the day before",
            f"finds the window’s {WORDS[FACTORS]} largest principal components.",
            f"These {WORDS[FACTORS]} components are the strategy’s {WORDS[FACTORS]} statistical "
            f"factors, {NAMES[0]} to {NAMES[-1]},",
            f"The first day with a full window is {days[0].date()}. Every day from then to the "
            f"second-to-last row has a next day, which gives {c.pairs} days t.",
            "when its statistic is above 0 and above the median stock’s.",
            f"The comparison set is the {len(c.stocks)} stocks priced on every day the pairs read",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_1s_flips_and_swaps(self, panel, components, text) -> None:
        _, closes = panel
        flips, _, opposite, others = _flips_by_cause(components, closes)
        assert all(swapped for _, _, swapped in others), f"{SPEC}; {AFTER_THE_RUN}"
        assert len(others) == flips.sum() - opposite.sum()
        days = len(components) - 1
        each = [f"{name}’s on {n}" for name, n in zip(NAMES[1:], flips[1:], strict=True)]
        fragments = [
            f"{NAMES[0]}’s vector points the other way on {flips[0]} of the {days} days, "
            f"{_listed(each)}, {flips.sum()} flips in all.",
            f"On {opposite.sum()} of them, the largest weight moves to a stock the earlier day "
            f"weighed below zero. The other {WORDS[len(others)]} all fall on days two",
            f"On {swap_days(components)} of the {days} days, two or more factors trade places.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_1s_table_and_the_two_paragraphs_after_it(
        self, weights, results: Results, text
    ) -> None:
        paired = results.spliced.comparison.factors
        columns = (weights.own, weights.matched, weights.left_out, paired)
        low = int(np.argmin(weights.own))
        near = int(np.argmin(np.abs(weights.own)))
        assert weights.own[low] < min(0.0, results.spliced.comparison.median), "fails outright"
        matched_gap = np.abs(weights.matched - paired)
        left_out_gap = np.abs(weights.left_out - paired)
        matched, left_out = int(matched_gap.argmax()), int(left_out_gap.argmax())
        left_out_column = next(j for j, c in enumerate(columns) if c is weights.left_out) + 1
        # The control reads like whichever of the first three columns it sits nearest.
        like = 1 + min(range(3), key=lambda j: np.abs(weights.shortened - columns[j]).max())
        fragments = [
            f"Weights fitted on the {LOOKBACK - 1} days before today, a window that leaves "
            "today’s return out, then matched.",
            _table(
                "l|r|r|r|r",
                [_text("Factor"), *(_text(str(n)) for n in range(1, len(columns) + 1))],
                [
                    [_text(name), *(f"{column[k]:.4f}" for column in columns)]
                    for k, name in enumerate(NAMES)
                ],
            ),
            f"On tomorrow’s own weights, {NAMES[low]} reads {_minus(weights.own[low], 4)} and "
            f"would fail outright, and {NAMES[near]} reads {weights.own[near]:.4f}.",
            f"and {NAMES[low]} still reads {_minus(weights.matched[low], 4)}. The largest gap "
            f"left between a matched figure and the test’s own is {NAMES[matched]}’s, "
            f"{matched_gap[matched]:.4f}.",
            f"leaves today’s return out, as in column {left_out_column}, the five figures land "
            "close to the test’s.",
            f"The largest gap left is {NAMES[left_out]}’s, {left_out_gap[left_out]:.4f}.",
            f"That window is also one day shorter, {LOOKBACK - 1} days rather than {LOOKBACK}, "
            "so a control",
            f"It fits tomorrow’s weights on the {LOOKBACK - 1} days ending today, "
            f"t − {LOOKBACK - 2} to t, which still hold today’s return, and matches them. Its "
            f"figures read like column {like} instead, with {NAMES[low]} at "
            f"{_minus(weights.shortened[low], 4)}.",
            f"holds today’s return pushes {NAMES[matched]} so far.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_2s_worked_series(self, text) -> None:
        first, second = [1, 2, 3], [2, 0, 1]
        products = int(np.dot(first, second))
        squares = int(np.dot(first, first)), int(np.dot(second, second))
        statistic = float(uncentred(np.array(first, float), np.array(second, float)))
        assert statistic == pytest.approx(products / math.sqrt(squares[0] * squares[1]))
        assert statistic > 0, "positive"
        steady = [1, 1.2, 0.9, 1.1, 1.0]
        series = np.array(steady)
        fragments = [
            f"Two series, ({', '.join(map(str, first))}) and ({', '.join(map(str, second))}), "
            f"show the difference. Their products sum to {products}, and their squares to "
            f"{squares[0]} and {squares[1]}, so the statistic is "
            f"{products}/√{squares[0] * squares[1]}, which is positive. Their ordinary "
            f"correlation is {_minus(np.corrcoef(first, second)[0, 1], 1)}.",
            f"The series ({', '.join(map(str, steady))}), read one day apart, shows it. Its "
            f"uncentred statistic is {float(uncentred(series[:-1], series[1:])):.4f}, close to "
            "perfect persistence, while its ordinary correlation is "
            f"{_minus(np.corrcoef(series[:-1], series[1:])[0, 1], 1)}, because each wiggle "
            "reverses.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_2s_two_days_and_same_sign_shares(self, results: Results, text) -> None:
        s = results.spliced
        (k,) = np.flatnonzero(np.abs(s.comparison.factors) > s.comparison.band)
        products = s.pairs.today[:, k] * s.pairs.tomorrow[:, k]
        share, days = share_of_largest(products, 2)
        first, second = (s.pairs.days[i].date() for i in days)
        reversed_, kept = sorted(days, key=lambda i: products[i])
        assert products[reversed_] < 0 < products[kept], SPEC
        assert products[kept] > -products[reversed_], SPEC
        shares = [f"{v:.4f} for {name}" for name, v in zip(NAMES, s.same_sign, strict=True)]
        fragments = [
            f"quiet ones. {NAMES[k]} shows how far that goes.",
            f"Two days, {first} and {second}, hold {100 * share:.2f} percent of the sum of "
            f"{NAMES[k]}’s squared products.",
            f"On {s.pairs.days[reversed_].date()} {NAMES[k]}’s return reversed the next day, and "
            f"on {s.pairs.days[kept].date()} it kept its sign, with the larger product.",
            f"It is {_listed(shares)}, all close to a coin toss.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_3s_check_and_the_intercept(self, results: Results, text) -> None:
        slope = TestOnRealDays.test_each_factor_return_is_s_times_the_programs_slope
        _, checked = slope.pytestmark[0].args
        s = results.spliced
        fragments = [
            f"A check on {WORDS[len(checked)]} of the file’s days confirms",
            f"Its own figures are {_minus(s.intercept_uncentred, 4)} uncentred and "
            f"{_minus(s.intercept_pearson, 4)} as an ordinary correlation.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_4s_table_quartiles_and_verdicts(self, results: Results, text) -> None:
        s = results.spliced
        c = s.comparison
        verdicts = s.verdicts()
        held = [v.factor for v in verdicts if v.holds]
        (missed,) = [v for v in verdicts if not v.holds]
        assert c.median < 0, "the median stock's statistic is negative"
        fragments = [
            _table(
                "l|r|r|r|r",
                [_text("Factor"), _text("Statistic"), _text("Percentile"), "t", "p"],
                [
                    [
                        _text(name),
                        f"{c.factors[k]:.4f}",
                        f"{c.percentile(c.factors[k]):.4f}",
                        f"{s.t_newey_west[k]:.4f}",
                        f"{s.p_values[k]:.4f}",
                    ]
                    for k, name in enumerate(NAMES)
                ],
            ),
            f"Among the {len(c.stocks)} stocks, the lower quartile’s statistic is "
            f"{_minus(c.lower_quartile, 4)}, the median’s is {_minus(c.median, 4)} and the "
            f"upper quartile’s is {_minus(c.upper_quartile, 4)}.",
            f"The claim holds for {_listed(held)}, which are above 0 and above the median "
            f"stock. It does not hold for {missed.factor}, which is "
            f"{_side(missed.above_median)} the median stock and {_side(missed.above_zero)} 0.",
            "so on this file any factor above 0 clears the median too.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_4s_three_points(self, results: Results, text) -> None:
        s, u = results.spliced, results.unspliced
        c = s.comparison
        (out,) = np.flatnonzero(np.abs(c.factors) > c.band)
        inside = [k for k in range(FACTORS) if k != out]
        edge = max(inside, key=lambda k: abs(c.factors[k]))
        two = share_of_largest(s.pairs.today[:, out] * s.pairs.tomorrow[:, out], 2)[1]
        shares = [
            share_of_largest(u.pairs.today[:, k] * u.pairs.tomorrow[:, k], 2)
            for k in range(FACTORS)
        ]
        carried = max(range(FACTORS), key=lambda k: shares[k][0])
        assert shares[carried][1].tolist() == two.tolist(), "the same two days"
        assert not s.survives.any(), SPEC
        smallest = int(np.argmin(s.p_values))
        assert s.p_values[smallest] >= FALSE_DISCOVERY, SPEC
        percent = f"{100 * FALSE_DISCOVERY:.0f}"
        fragments = [
            f"Over {c.pairs} pairs it lands inside ±{CRITICAL}/√{c.pairs} = ±{c.band:.4f} about "
            f"{100 * math.erf(CRITICAL / math.sqrt(2)):.0f} percent of the time",
            f"{NAMES[out]}’s {c.factors[out]:.4f} is outside it. {NAMES[edge]}’s "
            f"{c.factors[edge]:.4f} is just inside, and the other {WORDS[len(inside) - 1]} well "
            "inside.",
            f"The band and the t disagree about {NAMES[out]}.",
            f"and {NAMES[out]}’s statistic rests on two days",
            f"So {NAMES[out]} clears the band and its t is only {s.t_newey_west[out]:.4f}.",
            f"They land on {NAMES[out]} because of {SPLICED},",
            f"Run without {SPLICED}, the same two days fall on {NAMES[carried]} and hold "
            f"{100 * shares[carried][0]:.2f} percent of its squared products.",
            f"{SPLICED} takes the {NAMES[carried]} slot on both days and pushes the factor that "
            f"would be {NAMES[carried]} without {SPLICED} into {NAMES[out]}’s place.",
            f"to {percent} percent. Run across the {WORDS[FACTORS]} p-values, it declares none. "
            f"The smallest p-value is {NAMES[smallest]}’s {s.p_values[smallest]:.4f}, so none "
            f"would pass at {percent} percent even tested alone.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_5s_splice(self, panel, text) -> None:
        _, closes = panel
        before, after = _gap(closes)
        filled = closes[SPLICED].ffill()
        jump = float(filled.iloc[after] / filled.iloc[after - 1] - 1)
        fragments = [
            f"It closes on {closes.index[before].date()}, has no close for {after - before - 1} "
            f"trading days, and resumes on {closes.index[after].date()} as a different price "
            "history under the same ticker.",
            f"one day’s return of {jump:.4f}, a rise of {100 * jump:.2f} percent, on "
            f"{closes.index[after].date()}.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_5s_weights_on_pmc(self, panel, components, results: Results, text) -> None:
        _, closes = panel
        _, row = _gap(closes)
        column = closes.columns.get_loc(SPLICED)
        holding = windows_holding(components, row)
        assert holding[-1] is components[-1], "to the end of the file"
        paired = windows_holding(components[:-1], row)
        largest = [largest_loading(d, column) for d in paired]
        days = [closes.index[d.end].date() for d in paired]
        carried = np.bincount([k for _, k in largest], minlength=FACTORS)
        order = [k for k in np.argsort(-carried, kind="stable") if carried[k]]
        lead = largest[0][1]
        streak = next(i for i, (_, k) in enumerate(largest) if k != lead)
        sizes = [size for size, _ in largest[:streak]]
        s = results.spliced
        (out,) = np.flatnonzero(np.abs(s.comparison.factors) > s.comparison.band)
        two = share_of_largest(s.pairs.today[:, out] * s.pairs.tomorrow[:, out], 2)[1]
        first, second = (s.pairs.days[i].date() for i in two)
        assert {first, second} <= set(days[:streak]), "both days fall while PMC holds PC1"
        fragments = [
            f"Every day from {days[0]} to the end of the file fits its components on a window "
            f"that holds it. That is {len(holding)} days, and {len(paired)} of them have a next "
            f"day to pair with, the last being {days[-1]}.",
            f"On each of those {len(paired)} days, one of the top {WORDS[FACTORS]} factors puts "
            f"a weight of at least {min(size for size, _ in largest):.4f} on {SPLICED} alone,",
            f"{NAMES[order[0]]} carries it on {carried[order[0]]} of the days, "
            f"{_listed([f'{NAMES[k]} on {carried[k]}' for k in order[1:]])}.",
            f"From {days[0]} to {days[streak - 1]}, {NAMES[lead]} carries {SPLICED}, with a weight "
            f"between {min(sizes):.4f} and {max(sizes):.4f}.",
            f"So on {first} and {second} the factor that would be {NAMES[lead]} without "
            f"{SPLICED} sits in {NAMES[out]}’s place.",
            f"Those are the two days that put {NAMES[out]} outside the band.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_5s_table_and_what_moves(
        self, panel, components, results: Results, text
    ) -> None:
        before, after = results.spliced, results.unspliced
        _, closes = panel
        column = closes.columns.get_loc(SPLICED)
        # A window keeps a stock when its own returns are finite throughout, so
        # dropping one column moves no other stock. A window that holds PMC
        # therefore keeps exactly one stock fewer without it.
        assert all(column in d.stocks for d in components[:-1]), SPEC
        was = {v.factor: v for v in before.verdicts()}
        now = {v.factor: v for v in after.verdicts()}
        (fell,) = [n for n in NAMES if was[n].above_zero and not now[n].above_zero]
        (rose,) = [n for n in NAMES if not was[n].above_zero and now[n].above_zero]
        (missed,) = [n for n in NAMES if not was[n].holds]
        (new_miss,) = [n for n in NAMES if not now[n].holds]
        assert new_miss == fell, SPEC
        band = after.comparison.band
        outside = [n for n in NAMES if abs(now[n].statistic) > band]
        (back,) = [
            n
            for n in NAMES
            if abs(was[n].statistic) > before.comparison.band and abs(now[n].statistic) <= band
        ]
        assert not after.survives.any(), SPEC
        smallest = int(np.argmin(after.p_values))
        held_to = FALSE_DISCOVERY / FACTORS
        assert after.p_values[smallest] > held_to, SPEC
        rest = np.delete(after.p_values, smallest)
        assert (rest > FALSE_DISCOVERY).all(), SPEC
        fragments = [
            _table(
                "l|r|r",
                [
                    _text("Factor"),
                    _text(f"With {SPLICED}"),
                    _text(f"Without {SPLICED}"),
                ],
                [[_text(n), f"{was[n].statistic:.4f}", f"{now[n].statistic:.4f}"] for n in NAMES],
                [
                    _text("Median stock"),
                    f"{before.comparison.median:.4f}",
                    f"{after.comparison.median:.4f}",
                ],
            ),
            f"Dropping {SPLICED} and running everything again moves every factor. Each day’s "
            f"window keeps one stock fewer, and the comparison set holds "
            f"{len(after.comparison.stocks)} stocks rather than {len(before.comparison.stocks)}.",
            f"Without {SPLICED}, {fell} falls below 0 and {rose} rises above it, so the "
            f"criterion would miss {fell} instead of {missed}. {_listed(outside)} move outside "
            f"the band, and {back} moves back inside it. Benjamini-Hochberg still declares none. "
            f"It holds the smallest of {WORDS[FACTORS]} p-values to a {ORDINALS[FACTORS]} of "
            f"{100 * FALSE_DISCOVERY:.0f} percent, the second smallest to two "
            f"{ORDINALS[FACTORS]}s, and so on up to {100 * FALSE_DISCOVERY:.0f} percent for the "
            f"largest. The smallest is {NAMES[smallest]}’s {after.p_values[smallest]:.4f}, over "
            f"its {held_to:g}, and the other {WORDS[FACTORS - 1]} are all above "
            f"{100 * FALSE_DISCOVERY:.0f} percent, so none clears its step.",
        ]
        assert self.missing(text, fragments) == []


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

    def test_each_weight_vector_sums_to_zero(self, window) -> None:
        """Each day's average across the stocks comes off first, so no vector leans one way.

        Every vector with a nonzero singular value lies at right angles to
        equal weights on every stock, so even PC1 holds some stocks long and
        others short. Lesson 3 of the post says each vector sums to zero.
        """
        vectors, _ = revised_matlab_components(window)
        np.testing.assert_allclose(vectors.sum(axis=0), 0, atol=1e-14)

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
