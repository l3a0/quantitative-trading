"""The pins for the PCA factor model, Chan's Example 7.4.

This file is the single authority for every number any prose surface quotes
about Example 7.4. ``docs/replication-log.md`` Entry 13 carries the verdicts and
points here row by row.

Every pin on the committed file reads one vintage and one specification, so
both are stated once here and carried in failure messages as :data:`SPEC`.

- **Vintage.** ``ijr_20080114/``, the 600 S&P 600 members lifted from Chan's
  ``IJR_20080114.mat``, adjusted, saved 2008-01-15, spanning 2004-01-15 to
  2008-01-14, read for the Close column. Its identity is the
  ``LIFTED_SOURCES`` row in ``tests/support/committed_vintages.py``. The file
  holds the companies in the index on 2008-01-14, so every figure is a figure
  about survivors.
- **Specification.** A lookback of 252 days, five factors, 50 stocks shorted,
  no cost, and each printout's own rule as :mod:`chan.pca_factor` transcribes
  it: the first edition's ``example7_4.m``, the revised edition's MATLAB and
  Python, and a reading of its R.

Each printed figure is pinned twice. Once as the printout formats it, which is
the pin ``docs/design.md``'s ``### What an experiment pins`` asks for, and once
at its full computed value as a regression pin. The variants that separate the
printouts, and the runs without PMC, are pinned at four decimals, the
precision the log quotes.

Every full run happens once, in the ``results`` fixture, because one run of
the first edition takes about 18 seconds. Every pin reads that fixture, and
the report's test prints from it rather than computing again.

Exploratory. Reproducing Chan's figures spends the 2004 to 2008 sample on a
rule he chose. It first ran here on 2026-10-03.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from chan import pca_factor
from chan.matlab_helpers import smartmean, smartstd_first_edition
from chan.pca_factor import (
    BOOK_MATLAB_PERCENT,
    BOOK_PYTHON_R_PERCENT,
    DIGITS_17,
    FACTORS,
    FIRST_EDITION_PRINTS,
    LOOKBACK,
    MATLAB_LONGS,
    PYTHON_LONGS,
    PYTHON_PRINTS,
    R_LONGS,
    R_PRINTS,
    REVISED_MATLAB_PRINTS,
    SMALL_CAPS,
    SPLICED,
    TOP_N,
    TRADING_DAYS,
    Results,
    agreement,
    compute,
    first_edition_expected,
    main,
    matlab_sharpe,
    prints_as,
    python_expected,
    report,
    revised_matlab_expected,
    run,
    summed_returns,
    within,
)
from chan.series import load_panel
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import LIFTED_SOURCES

SPEC = "ijr_20080114/ Close, lookback 252, 5 factors, 50 a side, no cost"


# --- the committed file ----------------------------------------------------------


@pytest.fixture(scope="module")
def panel():
    return load_panel(SMALL_CAPS, field="Close")


@pytest.fixture(scope="module")
def results(panel) -> Results:
    _, closes = panel
    return compute(closes)


def _first_book(positions: np.ndarray, closes: pd.DataFrame) -> str:
    rows = np.flatnonzero(np.abs(positions).sum(axis=1) > 0)
    return str(closes.index[rows[0]].date())


class TestTheSpecification:
    def test_every_printout_shares_one_rule(self) -> None:
        assert (LOOKBACK, FACTORS, TOP_N, TRADING_DAYS) == (252, 5, 50, 252)

    def test_the_source_is_chans_s_and_p_600_file(self) -> None:
        assert SMALL_CAPS == "IJR_20080114.mat"

    def test_the_r_block_prints_the_pythons_figures(self) -> None:
        """Pp. 165 to 167: the R ends on the same three lines the Python does."""
        assert R_PRINTS == PYTHON_PRINTS

    def test_the_books_figures(self) -> None:
        """Location 4051: "only 2% (MATLAB) to 4% (Python and R)"."""
        assert (BOOK_MATLAB_PERCENT, BOOK_PYTHON_R_PERCENT) == (2, 4)


class TestTheVintage:
    def test_the_members_are_the_pinned_source(self, panel) -> None:
        members, closes = panel
        vendor, basis, saved, folder, count = LIFTED_SOURCES[SMALL_CAPS]
        assert {(m.vendor, m.price_basis, m.obtained) for m in members} == {(vendor, basis, saved)}
        assert {m.path.split("/")[0] for m in members} == {folder}
        assert len(members) == count == closes.shape[1] == 600

    def test_the_file_spans_chans_four_years(self, panel) -> None:
        _, closes = panel
        assert len(closes) == 1006
        assert str(closes.index[0].date()) == "2004-01-15"
        assert str(closes.index[-1].date()) == "2008-01-14"
        assert int(closes.isna().sum().sum()) == 13940

    def test_no_close_is_at_or_below_zero(self, panel) -> None:
        """What lets the R reading treat every missing return as NA rather than a 0/0."""
        _, closes = panel
        assert closes.min().min() > 0


class TestThePrintouts:
    """Each printout's figures beside what Chan printed, at its precision and in full."""

    def test_the_first_edition_prints_minus_1_8099(self, results: Results) -> None:
        assert prints_as(results.first.annual, FIRST_EDITION_PRINTS), SPEC
        assert results.first.annual == pytest.approx(-1.8098646256272817, abs=1e-9), SPEC

    def test_the_revised_matlab_prints_its_two_figures(self, results: Results) -> None:
        assert prints_as(results.matlab.annual, REVISED_MATLAB_PRINTS[0]), SPEC
        assert prints_as(results.matlab.sharpe, REVISED_MATLAB_PRINTS[1]), SPEC
        assert results.matlab.annual == pytest.approx(0.020205047899499503, abs=1e-9), SPEC
        assert results.matlab.sharpe == pytest.approx(0.21112030750148036, abs=1e-9), SPEC

    def test_the_revised_python_lands_its_17_digits(self, results: Results) -> None:
        figures = (results.python.annual, results.python.stdev, results.python.sharpe)
        assert within(figures, PYTHON_PRINTS), (figures, SPEC)

    def test_neither_r_reading_lands_the_printed_figures(self, results: Results) -> None:
        for reading, figures in (
            (results.r_unfilled, (0.0401, 0.0797, 0.5038)),
            (results.r_filled, (0.0426, 0.0802, 0.5319)),
        ):
            computed = (reading.annual, reading.stdev, reading.sharpe)
            assert computed == pytest.approx(figures, abs=5e-5), (reading.name, SPEC)
            assert not within(computed, R_PRINTS), reading.name

    def test_the_first_editions_figure_is_a_sum_over_positions(self, results: Results) -> None:
        """Every book holds 100 positions of ±1 and nothing divides by capital."""
        held = np.abs(results.first.positions).sum(axis=1)
        assert set(held[held > 0]) == {100}
        assert np.nanmax(np.abs(results.first.daily)) > 1


class TestTheBooks:
    """When each program starts trading and how many names each side holds."""

    @pytest.mark.parametrize(
        ("name", "first_book", "longs"),
        [
            ("first", "2005-01-14", 50),
            ("matlab", "2005-01-18", 50),
            ("python", "2005-01-19", 49),
            ("r_unfilled", "2005-01-18", 52),
            ("r_filled", "2005-01-18", 52),
        ],
    )
    def test_each_program_s_first_book_and_long_count(
        self, results: Results, panel, name: str, first_book: str, longs: int
    ) -> None:
        _, closes = panel
        positions = getattr(results, name).positions
        rows = np.flatnonzero(np.abs(positions).sum(axis=1) > 0)
        assert _first_book(positions, closes) == first_book
        assert set((positions[rows] > 0).sum(axis=1)) == {longs}
        assert set((positions[rows] < 0).sum(axis=1)) == {TOP_N}

    def test_the_python_clears_its_own_first_book(self, results: Results, panel) -> None:
        """Its loop sets a book on 2005-01-18, which ``positionsTable[capital==0,]=0`` clears."""
        _, closes = panel
        first_loop_row = LOOKBACK + 1
        assert str(closes.index[first_loop_row].date()) == "2005-01-18"
        assert not results.python.positions[first_loop_row].any()
        assert results.python.positions[first_loop_row + 1].any()

    def test_the_traded_days(self, results: Results) -> None:
        assert int(results.first.traded.sum()) == 753
        assert int(results.matlab.traded.sum()) == 752
        assert int(results.python.traded.sum()) == 751
        assert int(np.isfinite(results.first.daily).sum()) == 1005
        assert int(np.isfinite(results.matlab.daily).sum()) == 752


class TestWhatSeparatesTwoFromFour:
    """The four differences a test can tell apart, each against the printout it moves."""

    def test_the_pythons_pca_changes_no_position(self, results: Results) -> None:
        assert np.array_equal(results.python.positions, results.momentum.positions)

    def test_the_revised_books_are_never_identical(self, results: Results) -> None:
        together = agreement(results.matlab, results.python)
        assert (together.days, together.identical) == (752, 0)
        assert round(together.share, 4) == 0.1383

    def test_fifty_longs_move_the_pythons_figures(self, results: Results) -> None:
        assert results.python_fifty.annual == pytest.approx(0.0414, abs=5e-5)
        assert results.python_fifty.sharpe == pytest.approx(0.5908, abs=5e-5)
        assert not within(
            (results.python_fifty.annual, results.python_fifty.stdev, results.python_fifty.sharpe),
            PYTHON_PRINTS,
        )

    def test_averaging_over_trading_days_moves_both_programs(self, results: Results) -> None:
        assert results.python_traded.annual == pytest.approx(0.0543, abs=5e-5)
        assert results.python_traded.sharpe == pytest.approx(0.6699, abs=5e-5)
        first = float(smartmean(results.first.daily[results.first.traded])) * TRADING_DAYS
        assert first == pytest.approx(-2.4156, abs=5e-5)

    def test_the_first_editions_smartstd_moves_the_revised_sharpe(self, results: Results) -> None:
        swapped = matlab_sharpe(results.matlab.daily, smartstd_first_edition)
        assert swapped == pytest.approx(0.2441, abs=5e-5)
        assert not prints_as(swapped, REVISED_MATLAB_PRINTS[1])

    def test_round_off_does_not_explain_the_spread(self, results: Results) -> None:
        """Chan's "essentially round off errors" needs the books to agree on every day."""
        together = agreement(results.matlab, results.python)
        assert together.identical < together.days


class TestTheSplice:
    def test_pmc_forward_fills_into_one_days_return(self, panel) -> None:
        _, closes = panel
        filled = closes[SPLICED].ffill()
        day = pd.Timestamp("2007-08-01")
        assert filled[day] / filled.shift()[day] - 1 == pytest.approx(1.8654, abs=5e-5)
        gap = closes[SPLICED].loc["2004-03-15":"2007-07-31"]
        assert gap.isna().all() and len(gap) == 851

    def test_each_printout_without_pmc(self, results: Results) -> None:
        assert results.first_unspliced.annual == pytest.approx(-1.8014, abs=5e-5)
        assert results.matlab_unspliced.annual == pytest.approx(0.0180, abs=5e-5)
        assert results.matlab_unspliced.sharpe == pytest.approx(0.1869, abs=5e-5)
        assert results.python_unspliced.annual == pytest.approx(0.0408, abs=5e-5)
        assert results.python_unspliced.sharpe == pytest.approx(0.5851, abs=5e-5)


class TestTheReport:
    def test_it_prints_each_figure_and_verdict(self, results: Results, panel, capsys) -> None:
        members, closes = panel
        report(members, closes, results)
        out = capsys.readouterr().out
        assert "2004-01-15 to 2008-01-14, 1006 days, 600 stocks" in out
        for printed in (FIRST_EDITION_PRINTS, *REVISED_MATLAB_PRINTS, *PYTHON_PRINTS):
            assert printed in out
        for line in (
            "first-edition MATLAB   reproduced",
            "revised MATLAB         reproduced",
            "revised Python         reproduced",
            "revised R              did not reproduce",
            "'round off errors'     does not hold",
            "identical on 0 of 752 days",
            "identical on every day",
            "13.83%",
            "Without PMC",
            "about survivors",
            "Exploratory.",
        ):
            assert line in out, line

    def test_run_reads_the_file_once_and_reports(
        self, results: Results, monkeypatch, capsys
    ) -> None:
        monkeypatch.setattr(pca_factor, "compute", lambda closes: results)
        assert run() is results
        assert "Verdicts" in capsys.readouterr().out

    def test_an_empty_data_directory_is_refused_before_any_program_runs(
        self, tmp_path, monkeypatch
    ) -> None:
        def never(closes):
            raise AssertionError("a program ran")

        monkeypatch.setattr(pca_factor, "compute", never)
        with pytest.raises(VintageUnavailable):
            run(data_dir=tmp_path)

    def test_main_prints_a_refusal_as_one_line(self, monkeypatch) -> None:
        def refuse(data_dir=None):
            raise VintageUnavailable("no committed vintage is lifted from IJR_20080114.mat")

        monkeypatch.setattr(pca_factor, "run", refuse)
        monkeypatch.setattr("sys.argv", ["pca_factor"])
        with pytest.raises(SystemExit, match="no committed vintage is lifted from IJR_20080114"):
            main()


# --- the rules, on windows small enough to read ------------------------------------


@pytest.fixture()
def window() -> np.ndarray:
    """Twelve stocks over thirty days of returns, with enough spread for five factors."""
    return np.random.default_rng(7).normal(0, 0.02, size=(12, 30))


class TestTheRules:
    def test_a_regression_with_an_intercept_sums_to_the_summed_returns(self, window) -> None:
        np.testing.assert_allclose(python_expected(window), summed_returns(window), atol=1e-14)

    def test_the_first_edition_projects_todays_return_on_the_top_five(self, window) -> None:
        centred = window - window.mean(axis=1, keepdims=True)
        top, _, _ = np.linalg.svd(centred, full_matrices=False)
        exposures = top[:, :FACTORS]
        expected = window.mean(axis=1) + exposures @ (exposures.T @ centred[:, -1])
        np.testing.assert_allclose(first_edition_expected(window), expected, atol=1e-14)

    def test_the_revised_matlab_fits_today_with_an_intercept(self, window) -> None:
        today = np.random.default_rng(8).normal(0, 0.02, size=len(window))
        fitted = revised_matlab_expected(window, today)
        assert fitted.mean() == pytest.approx(today.mean(), abs=1e-15)
        assert not np.allclose(fitted, today)

    def test_the_revised_matlab_ignores_a_flipped_score(self, window, monkeypatch) -> None:
        """A score's sign is arbitrary, and the fitted values depend only on the span.

        So MATLAB's ``pca`` and this SVD may disagree on signs without moving a
        position, which is why no test separates them.
        """
        today = np.random.default_rng(9).normal(0, 0.02, size=len(window))
        fitted = revised_matlab_expected(window, today)
        svd = np.linalg.svd

        def flipped(matrix, full_matrices=True):
            left, singular, right = svd(matrix, full_matrices=full_matrices)
            left = left.copy()
            left[:, :2] *= -1
            return left, singular, right

        monkeypatch.setattr(pca_factor.np.linalg, "svd", flipped)
        np.testing.assert_allclose(revised_matlab_expected(window, today), fitted, atol=1e-15)

    def test_each_printouts_long_side(self) -> None:
        order = np.arange(100)
        assert list(order[MATLAB_LONGS]) == list(range(50, 100))
        assert list(order[PYTHON_LONGS]) == list(range(50, 99))
        assert list(order[R_LONGS]) == list(range(48, 100))

    def test_prints_as_reads_the_decimals_off_the_printed_figure(self) -> None:
        assert prints_as(-1.80986, "-1.8099")
        assert not prints_as(-1.80984, "-1.8099")
        assert prints_as(0.2111203, "0.211120")

    def test_within_holds_a_figure_to_17_digits(self) -> None:
        assert DIGITS_17 == 1e-12
        assert within((0.1 + 3e-13,), ("0.1",))
        assert not within((0.1 + 3e-12,), ("0.1",))
