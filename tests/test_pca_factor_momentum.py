"""The pins for whether Example 7.4's own factor returns have momentum.

This file is the single authority for every number any prose surface quotes
about [issue 286](https://github.com/l3a0/quantitative-trading/issues/286).
``docs/replication-log.md`` Entry 40 carries the verdicts and points here.

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
report's test prints from it rather than computing again.

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
    Pairs,
    Result,
    Results,
    Verdict,
    _figures,
    benjamini_hochberg,
    compute,
    compute_both,
    factor_pairs,
    main,
    one_sided_p,
    report,
    run,
    stock_statistics,
    uncentred,
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
            "docs/replication-log.md Entry 40 carries the verdicts.",
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
