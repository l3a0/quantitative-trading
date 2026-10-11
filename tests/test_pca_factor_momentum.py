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
in ``TestWhatThePostMeasured`` read two more module fixtures for the same
reason, ``components`` for the 753 fitting days' decompositions and
``weights`` for the 752 more that leave each pair day's return out.

Exploratory. Testing a claim someone else chose spends the 2004 to 2008 sample
on it. It first ran here on 2026-10-10.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from chan import pca_factor_momentum
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
    compute_both,
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
def results(panel) -> Results:
    _, closes = panel
    return compute_both(closes)


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
def components(returns) -> list[Decomposition]:
    """All 753 fitting days' decompositions, computed once for every pin below."""
    return daily_components(returns)


@pytest.fixture(scope="module")
def weights(returns, components) -> WeightStatistics:
    """752 more decompositions, on the 251 days before each pair day, so computed once."""
    return weight_statistics(returns, components)


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

    def test_each_factors_vector_flips_sign_on_about_half_the_days(self, components) -> None:
        """Day t's vector against day t + 1's, on the stocks both keep, over 752 pair days."""
        assert sign_flips(components).tolist() == [391, 376, 414, 387, 355], (
            f"{SPEC}; {AFTER_THE_RUN}"
        )

    def test_two_factors_swap_rank_on_15_of_752_days(self, components) -> None:
        assert swap_days(components) == 15, f"{SPEC}; {AFTER_THE_RUN}"

    def test_on_each_days_own_weights(self, weights) -> None:
        """A series rebuilt from each day's decomposition, flips and swaps and all."""
        expected = (0.0624, -0.1643, -0.0369, -0.0577, 0.0593)
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

    def test_dropping_the_intercept_moves_no_ranking_on_any_pair_day(
        self, returns, components
    ) -> None:
        agree = rankings_agree(returns, components)
        assert len(agree) == 752 and agree.all(), f"{SPEC}; {AFTER_THE_RUN}"

    def test_no_stock_ties_any_factor(self, results: Results) -> None:
        """What lets the figure's curve meet each factor at its percentile, which counts below."""
        assert f"{smallest_gap(results.spliced.comparison):.2e}" == "1.06e-04", SPEC
        assert f"{smallest_gap(results.unspliced.comparison):.2e}" == "3.85e-05", SPEC

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
            "  Band +/-1.96/sqrt(752) = 0.0715, where a series with no persistence stays inside "
            "95 percent of the time. Decides nothing."
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
        """A series that keeps one sign reads as persistent, which a centred statistic misses."""
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

    def test_the_three_statistics_by_hand(self, closes) -> None:
        returns = file_returns(closes)
        components = daily_components(returns)
        today, own, matched, left_out = [], [], [], []
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
        stats = weight_statistics(returns, components)
        np.testing.assert_allclose(stats.own, uncentred(np.array(today), np.array(own)))
        np.testing.assert_allclose(stats.matched, uncentred(np.array(today), np.array(matched)))
        np.testing.assert_allclose(
            stats.left_out, uncentred(np.array(today), np.array(left_out)), atol=1e-14
        )

    def test_a_flip_tomorrow_moves_the_own_statistic_and_not_the_matched_one(self, closes) -> None:
        returns = file_returns(closes)
        components = daily_components(returns)
        before = weight_statistics(returns, components)
        last = components[-1]
        flipped = last.vectors.copy()
        flipped[:, 0] *= -1
        components[-1] = Decomposition(last.end, last.stocks, flipped, last.singular)
        after = weight_statistics(returns, components)
        assert after.own[0] != pytest.approx(before.own[0])
        np.testing.assert_allclose(after.matched, before.matched, atol=1e-15)
        np.testing.assert_array_equal(after.left_out, before.left_out)

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
