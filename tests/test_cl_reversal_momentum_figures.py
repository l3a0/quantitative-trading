"""The pins for the figure in the post on the crude oil reversal joined to momentum.

``tests/test_cl_reversal_momentum.py`` holds what the run computes. This file
holds that the figure draws those numbers, so a generator that plotted the
wrong rule, the wrong save or the wrong segment, or mislabelled a panel, fails
even when the arithmetic is right. Some numbers repeat here on purpose,
because a figure's labels are prose and the suite is the authority for every
number prose quotes. No test compares bytes, for the reason
``tests/test_regime_figure.py`` gives.

The figure reads the vintages and the specification
``tests/test_cl_reversal_momentum.py`` states in its module docstring: CL on
the 2012-05-04 save over its 1,000 rows for the upper panel, and on the
2012-05-07 save over its 998 rows from 2004-05-24 to 2008-05-16 for the lower.

Every number here is exploratory, like everything computed for location 2701.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from matplotlib.dates import date2num

from chan import cl_reversal_momentum_figures
from chan.cl_reversal_momentum import EARLIER_SOURCE_FILE, four_rules, read_cl
from chan.cl_reversal_momentum_figures import (
    JOIN_FIGURE,
    RULES,
    cumulative,
    main,
    make_join_figure,
    percent,
)
from chan.paths import FIGURES_DIR
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable

BEFORE_END = pd.Timestamp("2008-05-16")
NAMES = ("combination", "momentum", "reversal")


@pytest.fixture(scope="module")
def book_closes() -> pd.Series:
    return read_cl()[1]


@pytest.fixture(scope="module")
def before_closes() -> pd.Series:
    return read_cl(EARLIER_SOURCE_FILE, end=BEFORE_END)[1]


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("cl_reversal_momentum_figure") / JOIN_FIGURE


@pytest.fixture(scope="module")
def figure(out, book_closes, before_closes):
    return make_join_figure(out=out, book_closes=book_closes, before_closes=before_closes)


@pytest.fixture(scope="module")
def axes(figure):
    book, before = figure.axes
    return {"book": book, "before": before}


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _title(ax) -> str:
    return ax.get_title(loc="left")


class TestThePanels:
    def test_there_are_two_each_over_its_own_segment(
        self, figure, axes, book_closes, before_closes
    ) -> None:
        assert len(figure.axes) == 2
        for name, closes in (("book", book_closes), ("before", before_closes)):
            assert axes[name].get_xlim() == (date2num(closes.index[0]), date2num(closes.index[-1]))
        assert not axes["book"].get_shared_x_axes().joined(axes["book"], axes["before"])

    def test_the_segments_are_the_book_s_window_and_the_998_rows_before(
        self, book_closes, before_closes
    ) -> None:
        assert len(book_closes) == 1000
        assert (book_closes.index[0], book_closes.index[-1]) == (
            pd.Timestamp("2008-05-19"),
            pd.Timestamp("2012-05-04"),
        )
        assert len(before_closes) == 998
        assert (before_closes.index[0], before_closes.index[-1]) == (
            pd.Timestamp("2004-05-24"),
            BEFORE_END,
        )

    def test_the_title_carries_the_label_and_the_note_names_both_saves(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Exploratory: Chan's crude oil join against each of the two rules it joins"
        )
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Algorithmic Trading, location 2701. CL_rev.m's rules compounded daily on Chan's "
            "back-adjusted CL, with no cost.\nThe book's window reads "
            "inputDataOHLCDaily_20120504.mat, the save the script loads, and the rows before "
            "it\nread inputDataOHLCDaily_20120507.mat. Those closes sit far above the traded "
            "price, so the lower panel is the rule\non Chan's series rather than a trader's "
            "return."
        ]

    def test_drawing_with_no_closes_reads_the_committed_saves(self, tmp_path, book_closes) -> None:
        """``main`` and the committed PNG take this path, so it is drawn here too."""
        drawn = make_join_figure(out=tmp_path / JOIN_FIGURE)
        book, before = (_by_gid(ax.lines) for ax in drawn.axes)
        np.testing.assert_array_equal(
            book["combination"].get_ydata(), cumulative(four_rules(book_closes).combination)
        )
        assert len(before["combination"].get_xdata()) == 998
        assert before["combination"].get_xdata()[-1] == BEFORE_END


class TestTheCurves:
    @pytest.mark.parametrize("panel", ["book", "before"])
    def test_each_line_is_its_rule_compounded(
        self, axes, panel, book_closes, before_closes
    ) -> None:
        closes = book_closes if panel == "book" else before_closes
        rules = four_rules(closes)
        lines = _by_gid(axes[panel].lines)
        for name in NAMES:
            traded = getattr(rules, name)
            np.testing.assert_array_equal(lines[name].get_xdata(), closes.index)
            np.testing.assert_allclose(
                lines[name].get_ydata(), np.cumprod(1 + traded.daily) - 1, rtol=0, atol=1e-15
            )
        assert list(lines["zero"].get_ydata()) == [0, 0]

    @pytest.mark.parametrize("panel", ["book", "before"])
    def test_each_line_ends_where_its_apr_says(
        self, axes, panel, book_closes, before_closes
    ) -> None:
        closes = book_closes if panel == "book" else before_closes
        rules = four_rules(closes)
        lines = _by_gid(axes[panel].lines)
        for name in NAMES:
            traded = getattr(rules, name)
            end = (1 + traded.apr) ** (len(closes) / 252) - 1
            assert lines[name].get_ydata()[-1] == pytest.approx(end, abs=1e-12)

    def test_comboor_is_left_out(self, axes) -> None:
        for ax in axes.values():
            assert "either" not in _by_gid(ax.lines)
            assert len([line for line in ax.lines if line.get_gid() in NAMES]) == 3

    def test_each_line_and_its_legend_entry_share_one_colour(self, axes) -> None:
        """The legend is the only key to which line is which rule."""
        assert len({colour for _, _, colour in RULES}) == 3
        for ax in axes.values():
            lines = _by_gid(ax.lines)
            legend = ax.get_legend()
            labels = [t.get_text() for t in legend.get_texts()]
            assert labels == ["the join", "momentum alone", "reversal alone"]
            for (name, _, colour), handle in zip(RULES, legend.legend_handles, strict=True):
                assert lines[name].get_color() == colour
                assert handle.get_color() == colour

    def test_the_join_is_drawn_heavier(self, axes) -> None:
        for ax in axes.values():
            lines = _by_gid(ax.lines)
            assert lines["combination"].get_linewidth() > lines["momentum"].get_linewidth()
            assert lines["momentum"].get_linewidth() == lines["reversal"].get_linewidth()


class TestTheBookSWindow:
    def test_the_ends_peak_and_trough(self, axes) -> None:
        lines = _by_gid(axes["book"].lines)
        ends = [round(float(lines[name].get_ydata()[-1]), 6) for name in NAMES]
        assert ends == [0.554578, 0.408892, 0.299884]
        momentum = pd.Series(lines["momentum"].get_ydata(), index=lines["momentum"].get_xdata())
        reversal = pd.Series(lines["reversal"].get_ydata(), index=lines["reversal"].get_xdata())
        assert (round(momentum.max(), 6), momentum.idxmax()) == (
            1.169842,
            pd.Timestamp("2009-06-11"),
        )
        assert (round(reversal.min(), 6), reversal.idxmin()) == (
            -0.587038,
            pd.Timestamp("2009-02-18"),
        )

    def test_the_join_never_falls_far(self, axes) -> None:
        join = _by_gid(axes["book"].lines)["combination"].get_ydata()
        assert round(float(join.min()), 6) == -0.039937

    def test_the_heading(self, axes) -> None:
        assert _title(axes["book"]) == (
            "The book's window, 2008-05-19 to 2012-05-04, 1,000 rows. The join ends at 55.5%.\n"
            "Momentum alone peaks at 117.0% on 2009-06-11 and ends at 40.9%. Reversal alone "
            "falls to −58.7%\non 2009-02-18 and ends at 30.0%."
        )


class TestTheRowsBefore:
    def test_the_ends(self, axes) -> None:
        lines = _by_gid(axes["before"].lines)
        ends = [round(float(lines[name].get_ydata()[-1]), 6) for name in NAMES]
        assert ends == [0.087153, 0.430362, -0.23594]

    def test_the_heading(self, axes) -> None:
        assert _title(axes["before"]) == (
            "The 998 rows before it, 2004-05-24 to 2008-05-16. The join ends at 8.7%,\n"
            "momentum alone at 43.0% and reversal alone at −23.6%."
        )

    def test_percent_prints_a_true_minus_sign(self) -> None:
        assert percent(-0.23594) == "−23.6%"
        assert percent(1.169842) == "117.0%"


class TestTheFile:
    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.exists() and out.stat().st_size > 0

    def test_the_committed_figure_exists(self) -> None:
        assert (FIGURES_DIR / JOIN_FIGURE).is_file()

    def test_main_lets_any_other_error_through_as_itself(self, monkeypatch) -> None:
        def fail(*_a, **_k):
            raise ValueError("a bug, not a refusal")

        monkeypatch.setattr(cl_reversal_momentum_figures, "make_join_figure", fail)
        with pytest.raises(ValueError, match="a bug, not a refusal"):
            main()

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage is lifted from inputDataOHLCDaily_20120504"),
            WindowCrossesScaleBreak("inputdataohlcdaily_20120504/cl.csv changes scale"),
        ],
    )
    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(cl_reversal_momentum_figures, "make_join_figure", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)

    def test_a_missing_save_reaches_the_operator_as_one_line(self, monkeypatch, tmp_path) -> None:
        """The real read path, not a stand-in, so the guard and the read are both exercised."""
        from chan import paths

        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit, match="inputDataOHLCDaily_20120504.mat"):
            main()
