"""The pins for the PCA factor model, Chan's Example 7.4.

This file is the single authority for every number any prose surface quotes
about Example 7.4's printouts. ``tests/test_pca_factor_momentum.py`` holds the
figures on whether its own factor returns have momentum.
``docs/replication-log.md`` Entry 13 carries the verdicts and points here row
by row.

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

from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from chan import paths, pca_factor
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
    Run,
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

    def test_the_revised_python_lands_its_printed_figures(self, results: Results) -> None:
        """Within 1e-15 of each figure the Python prints to 17 digits.

        The verdict's criterion is :data:`DIGITS_17`. This pin is tighter, so it
        holds the precision the log quotes the computed figures at.
        """
        figures = (results.python.annual, results.python.stdev, results.python.sharpe)
        assert within(figures, PYTHON_PRINTS), (figures, SPEC)
        for computed, printed in zip(figures, PYTHON_PRINTS, strict=True):
            assert computed == pytest.approx(float(printed), abs=1e-15), SPEC

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

    def test_the_revised_books_share_few_names(self, results: Results) -> None:
        """The printed Python buys 49 and the MATLAB 50, so this compares names, not books."""
        together = agreement(results.matlab, results.python)
        assert together.days == 752
        assert round(together.share, 4) == 0.1383

    def test_at_one_size_the_revised_books_are_never_identical(self, results: Results) -> None:
        """Given 50 longs, the Python's book is the MATLAB's size, and still never matches it."""
        sized = agreement(results.matlab, results.python_fifty)
        assert (sized.days, sized.identical) == (752, 0)
        assert sized.fewest_differing == 125
        assert round(sized.share, 4) == 0.1414

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
        """Chan's "essentially round off errors" needs books of one size to agree every day."""
        sized = agreement(results.matlab, results.python_fifty)
        assert sized.identical < sized.days

    def test_keeping_the_first_book_moves_the_pythons_figures(self, results: Results) -> None:
        kept = results.python_first_book
        assert kept.annual == pytest.approx(0.0417, abs=5e-5)
        assert kept.sharpe == pytest.approx(0.5945, abs=5e-5)
        assert kept.positions[LOOKBACK + 1].any()

    def test_each_bookkeeping_choice_lowers_the_pythons_figure(self, results: Results) -> None:
        """Changing any of the three raises it, so each moves it toward the MATLAB's."""
        for changed in (results.python_fifty, results.python_traded, results.python_first_book):
            assert changed.annual > results.python.annual > results.matlab.annual


class TestTheSplice:
    def test_pmc_forward_fills_into_one_days_return(self, panel) -> None:
        _, closes = panel
        filled = closes[SPLICED].ffill()
        day = pd.Timestamp("2007-08-01")
        assert filled[day] / filled.shift()[day] - 1 == pytest.approx(1.8654, abs=5e-5)
        gap = closes[SPLICED].loc["2004-03-15":"2007-07-31"]
        assert gap.isna().all() and len(gap) == 851
        # Both ends are priced, so 851 is the whole gap rather than part of it.
        before, after = closes.index.get_indexer(
            [pd.Timestamp("2004-03-12"), pd.Timestamp("2007-08-01")]
        )
        assert after - before == 852
        assert closes[SPLICED].iloc[[before, after]].notna().all()

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
            "differ in at least 125 positions",
            "identical on every day",
            "13.83%",
            "Without PMC",
            "about survivors",
            "Exploratory.",
        ):
            assert line in out, line
        for figure in (
            "-1.8014",
            "0.0180",
            "0.1869",
            "0.0408",
            "0.5851",
            "0.0414",
            "0.5908",
            "0.0543",
            "0.6699",
            "0.0417",
            "0.5945",
            "-2.4156",
            "0.2441",
            "14.14%",
        ):
            assert figure in out, figure

    def test_the_r_verdict_holds_if_either_reading_lands(
        self, results: Results, panel, capsys
    ) -> None:
        """The report says "under either reading", so one reading landing is enough."""
        members, closes = panel
        landed = replace(
            results.r_filled,
            annual=float(R_PRINTS[0]),
            stdev=float(R_PRINTS[1]),
            sharpe=float(R_PRINTS[2]),
        )
        report(members, closes, replace(results, r_filled=landed))
        assert "revised R              reproduced" in capsys.readouterr().out

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


# --- what the post quotes ----------------------------------------------------------

POST = paths.REPO_ROOT / "blog" / "factor-models-lessons.md"


def _minus(x: float, places: int) -> str:
    """A figure in prose, with the post's typographic minus sign."""
    return f"{x:.{places}f}".replace("-", "−")


def _array(head: str, rows: list[list[str]]) -> str:
    """One of the post's ``array`` tables, from its header row to its last row."""
    body = " \\\\\n".join(" & ".join(row) for row in rows)
    return f"{head} \\\\ \\hline\n{body}\n\\end{{array}}"


def _longs(program: Run) -> int:
    """The one number of stocks a program buys on every day it holds a book."""
    rows = np.flatnonzero(np.abs(program.positions).sum(axis=1) > 0)
    (longs,) = set((program.positions[rows] > 0).sum(axis=1))
    return int(longs)


class TestWhatThePostQuotes:
    """Each figure ``blog/factor-models-lessons.md`` quotes about Example 7.4, read against the run.

    The classes above pin each figure once, and the post copies it by hand.
    Here each figure is built from the run, the file or a module constant at
    the precision the post prints it, and looked for in one copy: a short
    fragment holding the number and the few words that name one place in the
    post. A typo in a copy that is read, or a re-pin that leaves the post
    behind, fails here. Lesson 1's two tables and Lesson 2's are rebuilt
    whole, so a digit added to a cell fails as well as a digit changed. Each
    printed figure in Lesson 1's tables comes from :mod:`chan.pca_factor`'s
    record of the printout and is held against the run, and Lesson 2's table
    and its labels come from the run.

    The copies read are the section on the file and the four steps, every copy
    of Chan's 2 and 4 percent, Lesson 1's tables and the paragraph and three
    points around them, Lesson 2's equation, its third and fourth points, the
    three choices listed after them and its table, and Lesson 6's first and
    fourth points. Other copies are not read, so a typo in one of them passes.
    Among them are the 10⁻¹⁵ the Python lands within, the "three of the four"
    printouts in the title and Lesson 1's heading, the 1.8654 and 186.54
    percent in Lesson 3's third point, the 0 identical days out of 752 in
    Lesson 5, and the repeats of 600, 50, 252 and "five" elsewhere.
    ``tests/test_pca_factor_momentum.py`` reads Lesson 3's figures on
    Example 7.4's own factors, and ``tests/test_momentum_factor.py`` those on
    MKT and WML.
    """

    @pytest.fixture(scope="class")
    @classmethod
    def text(cls) -> str:
        return POST.read_text(encoding="utf-8")

    @staticmethod
    def missing(text: str, fragments: list[str]) -> list[str]:
        return [fragment for fragment in fragments if fragment not in text]

    def test_the_file_and_the_steps(self, panel, text) -> None:
        members, closes = panel
        (saved,) = {m.obtained for m in members}
        assert saved == LIFTED_SOURCES[SMALL_CAPS][2]
        fragments = [
            f"`{SMALL_CAPS}`, the {closes.shape[1]} members of the S&P 600 as he saved them on "
            f"{saved}, spanning {closes.index[0].date()} to {closes.index[-1].date()}, "
            f"{len(closes):,} trading days of split-adjusted closes.",
            f"Take the last {LOOKBACK} trading days of returns on each stock.",
            f"Buy the {TOP_N} stocks predicted highest and short the {TOP_N} predicted lowest",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_1s_two_tables(self, results: Results, text) -> None:
        matlab = (results.first.annual, results.matlab.annual, results.matlab.sharpe)
        printed = (FIRST_EDITION_PRINTS, *REVISED_MATLAB_PRINTS)
        assert all(prints_as(v, p) for v, p in zip(matlab, printed, strict=True)), SPEC
        python_run = (results.python.annual, results.python.stdev, results.python.sharpe)
        assert within(python_run, PYTHON_PRINTS), SPEC
        labels = (
            "First edition, annual mean",
            "Revised, annual mean return",
            "Revised, Sharpe ratio",
        )
        python = ("Mean return", "Standard deviation", "Sharpe ratio")
        fragments = [
            _array(
                "\\begin{array}{l|r}\n\\text{MATLAB printout} & \\text{Printed}",
                [[f"\\text{{{label}}}", p] for label, p in zip(labels, printed, strict=True)],
            ),
            _array(
                "\\small\\begin{array}{l|r}\n\\text{Revised Python, annual} & \\text{Printed}",
                [[f"\\text{{{label}}}", p] for label, p in zip(python, PYTHON_PRINTS, strict=True)],
            ),
            f"so {REVISED_MATLAB_PRINTS[0]} is Chan’s {BOOK_MATLAB_PERCENT} percent and "
            f"{PYTHON_PRINTS[0]} his {BOOK_PYTHON_R_PERCENT} percent.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_1s_three_points(self, results: Results, text) -> None:
        held = np.abs(results.first.positions).sum(axis=1)
        (positions,) = set(held[held > 0])
        readings = [
            f"{r.annual:.4f}, {r.stdev:.4f} and {r.sharpe:.4f}"
            for r in (results.r_unfilled, results.r_filled)
        ]
        first_edition_sharpe = matlab_sharpe(results.matlab.daily, smartstd_first_edition)
        fragments = [
            f"Its daily figure sums {int(positions)} positions of ±1 and never divides by "
            f"capital. So {_minus(results.first.annual, 4)} is a sum over positions",
            f"It buys {_longs(results.r_unfilled)} stocks where the Python buys "
            f"{_longs(results.python)}, among other differences.",
            f"Leaving each missing price empty gives {readings[0]}. Filling it with the last "
            f"price gives {readings[1]}.",
            f"reproduces the printed {results.matlab.sharpe:.6f}",
            f"The one from this book’s first edition gives {first_edition_sharpe:.4f}.",
        ]
        assert _longs(results.r_filled) == _longs(results.r_unfilled)
        assert self.missing(text, fragments) == []

    def test_lesson_2s_overlap_and_bookkeeping(self, results: Results, panel, text) -> None:
        _, closes = panel
        names = agreement(results.matlab, results.python)
        sized = agreement(results.matlab, results.python_fifty)
        changed = (results.python_fifty, results.python_traded, results.python_first_book)
        for program in changed:
            assert program.annual > results.python.annual, program.name
            assert program.sharpe > results.python.sharpe, program.name
        python, matlab = _longs(results.python), _longs(results.matlab)
        fifty = _longs(results.python_fifty)
        assert fifty == matlab
        traded = int(results.python.traded.sum())
        held = int((np.abs(results.python.positions).sum(axis=1) > 0).sum())
        assert held == sized.days == traded + 1
        fragments = [
            f"r_{{i,t}} = a_i + \\sum_{{k=1}}^{{{FACTORS}}} b_{{ik}} f_{{k,t}} + e_{{i,t}}",
            f"The printed Python buys {python} stocks, because its index range skips the "
            f"top-ranked one, while the MATLAB buys {matlab}.",
            f"On an average day, {100 * names.share:.2f} percent of the MATLAB’s names sit on "
            f"the same side in the printed Python, and {100 * sized.share:.2f} percent once the "
            f"Python also buys {fifty}.",
            f"Even at {fifty} longs each, the two sets of positions are identical on "
            f"{sized.identical} of the {sized.days} days both hold positions, and on each of "
            f"those days at least {sized.fewest_differing} of the {closes.shape[1]} stocks "
            "hold a different position in the two.",
            f"The printed Python buys the {python} stocks ranked second to {TOP_N}th rather "
            f"than the top {TOP_N}.",
            f"It averages its daily returns over all {len(closes):,} trading days rather than "
            f"the {traded} on which its positions earn a return. It holds positions on {held} "
            "days, and the last is the file’s final day,",
            f"Undoing any one raises both, from the printed {PYTHON_PRINTS[0]} and "
            f"{PYTHON_PRINTS[2]}, and so moves the Python further from the revised MATLAB’s "
            f"{REVISED_MATLAB_PRINTS[0]} and {REVISED_MATLAB_PRINTS[1]}.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_2s_table(self, results: Results, panel, text) -> None:
        _, closes = panel
        traded = int(results.python.traded.sum())
        labels = (
            f"Top {_longs(results.python_fifty)}, not {_longs(results.python)}",
            f"{traded} days, not {len(closes):,}",
            "First day kept",
        )
        changed = (results.python_fifty, results.python_traded, results.python_first_book)
        table = _array(
            "\\begin{array}{l|r|r}\n\\text{Change} & \\text{Mean} & \\text{Sharpe}",
            [
                [f"\\text{{{label}}}", f"{program.annual:.4f}", f"{program.sharpe:.4f}"]
                for label, program in zip(labels, changed, strict=True)
            ],
        )
        assert self.missing(text, [table]) == []

    def test_chans_2_and_4_percent_wherever_the_post_repeats_them(self, text) -> None:
        two, four = BOOK_MATLAB_PERCENT, BOOK_PYTHON_R_PERCENT
        fragments = [
            f"*Chan’s {two} and {four} percent come from two methods, not round-off.",
            f"he reports {two} percent a year from the MATLAB program and {four} percent from "
            "the Python and R,",
            f"it cannot be set beside the revised edition’s {two} percent.",
            f"Chan’s explanation of {two} against {four} percent is round-off,",
            f"So the gap between {two} and {four} percent is method,",
            f"None of them says how much of the revised MATLAB’s {two} percent the factors’ "
            "momentum earns.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_6s_survivors_and_pmc(self, results: Results, panel, text) -> None:
        _, closes = panel
        priced = np.flatnonzero(closes[SPLICED].notna().to_numpy())
        gaps = np.diff(priced) - 1
        resume = closes.index[priced[gaps.argmax() + 1]]
        filled = closes[SPLICED].ffill()
        jump = filled[resume] / filled.shift()[resume] - 1
        first = results.first_unspliced
        matlab, python = results.matlab_unspliced, results.python_unspliced
        fragments = [
            f"Every printout ranks and trades only the {closes.shape[1]} stocks still in the "
            f"S&P 600 on {closes.index[-1].date()}.",
            f"{SPLICED} in the S&P 600 file closes, goes missing for {gaps.max()} trading "
            "days, and resumes",
            f"when the second history begins on {resume.date()} the file shows one day’s "
            f"return of {jump:.4f}, a rise of {100 * jump:.2f} percent.",
            f"Without {SPLICED}, the first edition gives {_minus(first.annual, 4)}, the revised "
            f"MATLAB {matlab.annual:.4f} at a Sharpe ratio of {matlab.sharpe:.4f}, and the "
            f"revised Python {python.annual:.4f} at {python.sharpe:.4f}.",
        ]
        assert self.missing(text, fragments) == []


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
        assert within((0.1 - 3e-13,), ("0.1",))
        assert not within((0.1 + 3e-12,), ("0.1",))
        assert not within((0.1 - 3e-12,), ("0.1",))

    def test_agreement_counts_only_days_both_hold_a_book(self) -> None:
        """Each run holds a book on a day the other does not, and those days are left out."""
        a = np.array([[1.0, -1.0, 0.0], [1.0, -1.0, 0.0], [0.0, 0.0, 0.0], [1.0, 0.0, -1.0]])
        b = np.array([[0.0, 0.0, 0.0], [1.0, -1.0, 0.0], [1.0, -1.0, 0.0], [1.0, -1.0, 0.0]])
        first = Run("a", a, np.zeros(4), 0.0, 0.0, 0.0)
        second = Run("b", b, np.zeros(4), 0.0, 0.0, 0.0)
        together = agreement(first, second)
        assert (together.days, together.identical) == (2, 1)
        assert together.share == pytest.approx(0.75)
        assert together.fewest_differing == 0
        assert agreement(second, first).days == 2
