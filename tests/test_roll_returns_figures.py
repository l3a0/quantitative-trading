"""The pins for the figure in the post on spot and roll returns, Example 5.3.

``tests/test_roll_returns.py`` holds what the run computes. This file holds that
the figure draws those numbers, so a generator that plotted the wrong strip,
swapped the two roll returns, dropped the absolute value or shaded the wrong
side of zero fails even when the arithmetic is right. Some numbers repeat here
on purpose, because a figure's labels are prose and the suite is the authority
for every number prose quotes. No test compares bytes, for the reason
``tests/test_regime_figure.py`` gives.

The figure reads the vintage and the specification
``tests/test_roll_returns.py`` names as its ``SPEC``, which every failure
message here carries too: the five strips ``inputdatadaily_*_20120813/``,
vendor ``chan-mat``, basis ``raw``, saved 2012-08-14, with α the slope of the
log spot on the row number and γ the slope of the five nearest contracts' log
prices on their columns or on their months.

Exploratory, like everything Example 5.3 computes here.
"""

from __future__ import annotations

import dataclasses
import shutil

import numpy as np
import pandas as pd
import pytest
from matplotlib.colors import same_color
from matplotlib.dates import DateFormatter, YearLocator, date2num, num2date

from chan import paths, roll_returns
from chan import roll_returns_figures as figures
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.roll_returns import ROOTS
from chan.roll_returns_figures import (
    ROLL_RETURNS_FIGURE,
    bar_heights,
    book_label,
    main,
    make_roll_returns_figure,
    read_results,
    signed,
)
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable
from tests.test_roll_returns import COMPUTED, COMPUTED_IN_MONTHS, SPEC

FIRST, LAST = pd.Timestamp("2004-11-22"), pd.Timestamp("2012-08-13")


@pytest.fixture(scope="module")
def results():
    return read_results()


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("roll_returns_figure") / ROLL_RETURNS_FIGURE


@pytest.fixture(scope="module")
def figure(out, results):
    return make_roll_returns_figure(out=out, results=results)


@pytest.fixture(scope="module")
def axes(figure):
    bars, gamma = figure.axes
    return {"bars": bars, "gamma": gamma}


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _bars(ax, gid: str) -> list:
    return [p for p in ax.patches if p.get_gid() == gid]


def _title(ax) -> str:
    return ax.get_title(loc="left")


class TestThePanels:
    def test_there_are_two_in_the_order_the_post_reads_them(self, figure, axes) -> None:
        assert len(figure.axes) == 2
        assert _title(axes["bars"]).startswith("Table 5.1's spot and roll returns")
        assert _title(axes["gamma"]).startswith("Figure 5.5 redrawn")

    def test_the_title_carries_the_exploratory_label(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Exploratory: spot and roll returns redrawn on Chan's own futures strips"
        )

    def test_the_note_names_the_save_the_two_fits_and_the_sample(self, figure) -> None:
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Example 5.3 of Algorithmic Trading. Five strips saved 2012-08-14, one file per "
            "commodity holding its spot and every contract.\nα is 252 times the slope of the "
            "log spot on the day number. γ is −12 times the slope of the five nearest "
            "contracts'\nlog prices on their columns, or on their months. Every figure is "
            "in-sample on 1986 to 2012."
        ], SPEC

    def test_no_label_is_parsed_as_math(self, figure) -> None:
        """The bar legend prints |α| and |γ|, and the vertical bars are not a formula."""
        for ax in figure.axes:
            for text in [*ax.texts, ax.title, ax._left_title]:
                assert text.get_parse_math() is False
        for text in figure.texts:
            assert text.get_parse_math() is False


class TestTheBars:
    @pytest.mark.parametrize(
        ("gid", "column"),
        [("alpha", 0), ("gamma-columns", 1)],
    )
    def test_the_spot_and_script_bars_are_table_5_1s_figures(self, axes, gid, column) -> None:
        heights = [p.get_height() for p in _bars(axes["bars"], gid)]
        expected = [100 * abs(float(COMPUTED[root][column])) for root in ROOTS]
        np.testing.assert_allclose(heights, expected, rtol=0, atol=5e-5, err_msg=SPEC)

    def test_the_month_bars_are_the_month_spaced_gamma(self, axes) -> None:
        heights = [p.get_height() for p in _bars(axes["bars"], "gamma-months")]
        expected = [100 * abs(float(COMPUTED_IN_MONTHS[root])) for root in ROOTS]
        np.testing.assert_allclose(heights, expected, rtol=0, atol=5e-5, err_msg=SPEC)

    def test_every_bar_is_a_magnitude(self, results) -> None:
        """C's and CL's γ and BR's α are negative, and the claims compare sizes."""
        for gid, values in bar_heights(results).items():
            assert all(v >= 0 for v in values), gid
        assert results["C2"].mean_gamma < 0 and results["BR"].alpha < 0

    def test_the_groups_run_in_table_5_1s_order(self, axes) -> None:
        labels = [t.get_text() for t in axes["bars"].get_xticklabels()]
        assert labels == ["BR", "C", "CL", "HG", "TU"]
        for gid, offset in (("alpha", -1), ("gamma-columns", 0), ("gamma-months", 1)):
            centres = [p.get_x() + p.get_width() / 2 for p in _bars(axes["bars"], gid)]
            np.testing.assert_allclose(centres, np.arange(5) + offset * figures.BAR_WIDTH)

    def test_each_kind_of_bar_has_its_colour(self, axes) -> None:
        for gid, colour in (("alpha", MUTED), ("gamma-columns", ACCENT), ("gamma-months", GOOD)):
            assert all(same_color(p.get_facecolor()[:3], colour) for p in _bars(axes["bars"], gid))

    def test_twice_the_spot_return_is_marked_over_br_c_and_tu_alone(self, axes, results):
        marks = {gid: line for gid, line in _by_gid(axes["bars"].lines).items()}
        assert set(marks) == {"twice-alpha-BR", "twice-alpha-C", "twice-alpha-TU"}
        for root in ("BR", "C2", "TU"):
            line = marks[f"twice-alpha-{book_label(root)}"]
            assert list(line.get_ydata()) == [200 * abs(results[root].alpha)] * 2, SPEC
            assert same_color(line.get_color(), LOST)

    def test_cs_month_bar_falls_under_its_mark_and_hgs_under_its_spot_bar(self, axes) -> None:
        """What the heading says, read off the drawn bars rather than the data."""
        months = [p.get_height() for p in _bars(axes["bars"], "gamma-months")]
        spot = [p.get_height() for p in _bars(axes["bars"], "alpha")]
        c, hg = ROOTS.index("C2"), ROOTS.index("HG")
        mark = _by_gid(axes["bars"].lines)["twice-alpha-C"].get_ydata()[0]
        assert months[c] < mark, SPEC
        assert months[hg] < spot[hg], SPEC

    def test_the_legend_names_the_three_bars_and_the_mark(self, axes) -> None:
        legend = [t.get_text() for t in axes["bars"].get_legend().get_texts()]
        assert legend == [
            "twice the spot return",
            "spot return |α|",
            "roll return |γ|, the script's, on contract columns",
            "roll return |γ| on months, as the text describes",
        ]

    def test_the_heading_quotes_hg_and_c_on_months(self, axes) -> None:
        assert _title(axes["bars"]) == (
            "Table 5.1's spot and roll returns, and the roll return with maturity in months.\n"
            "On months HG's roll return of 3.86% falls below its spot return of 5.06%,\n"
            "and C's is 1.89 times its spot return, short of twice."
        ), SPEC
        assert axes["bars"].get_ylabel() == "annualized, percent"


class TestFigure55:
    def test_the_line_is_cls_gamma_on_its_1941_days(self, axes, results) -> None:
        line = _by_gid(axes["gamma"].lines)["gamma"]
        days = [pd.Timestamp(d) for d in line.get_xdata()]
        expected = results["CL"].gamma.dropna()
        assert len(days) == 1941, SPEC
        assert (days[0], days[-1]) == (FIRST, LAST), SPEC
        assert days == list(expected.index), SPEC
        np.testing.assert_array_equal(line.get_ydata(), expected.to_numpy())
        assert same_color(line.get_color(), INK)

    def test_the_axis_spans_figure_5_5s_window(self, axes) -> None:
        assert axes["gamma"].get_xlim() == (date2num(FIRST), date2num(LAST)), SPEC

    def test_a_tick_falls_on_every_year_from_2005_to_2012(self, axes) -> None:
        axis = axes["gamma"].xaxis
        assert isinstance(axis.get_major_locator(), YearLocator)
        assert isinstance(axis.get_major_formatter(), DateFormatter)
        assert axis.get_major_formatter().fmt == "%Y"
        low, high = axes["gamma"].get_xlim()
        shown = [t for t in axis.get_major_locator()() if low <= t <= high]
        assert [num2date(t).year for t in shown] == list(range(2005, 2013)), SPEC

    def test_the_mean_line_is_table_5_1s_cl_gamma(self, axes) -> None:
        line = _by_gid(axes["gamma"].lines)["mean"]
        assert f"{line.get_ydata()[0]:.6f}" == COMPUTED["CL"][1], SPEC
        assert line.get_label() == "mean −0.070592, Table 5.1's −7.1%"
        assert same_color(line.get_color(), ACCENT)

    def test_a_line_marks_zero(self, axes) -> None:
        assert list(_by_gid(axes["gamma"].lines)["zero"].get_ydata()) == [0, 0]

    @pytest.mark.parametrize(
        ("gid", "colour", "above"),
        [("backwardation", GOOD, True), ("contango", LOST, False)],
    )
    def test_each_side_of_zero_is_shaded_in_its_colour(self, axes, gid, colour, above) -> None:
        """Location 2399: "Positive values indicate backwardation and negative values
        indicate contango"."""
        shade = _by_gid(axes["gamma"].collections)[gid]
        assert same_color(shade.get_facecolor()[0][:3], colour)
        ys = np.concatenate([path.vertices[:, 1] for path in shade.get_paths()])
        assert (ys >= 0).all() if above else (ys <= 0).all(), SPEC
        assert np.abs(ys).max() > 0.2, SPEC

    def test_the_heading_counts_the_days_on_each_side(self, axes) -> None:
        assert _title(axes["gamma"]) == (
            "Figure 5.5 redrawn: CL's roll return on its 1,941 days from 2004-11-22 to "
            "2012-08-13.\nBelow zero, contango, on 1,389 days and above zero, backwardation, "
            "on 552."
        ), SPEC
        assert axes["gamma"].get_ylabel() == "roll return γ, annualized"

    def test_signed_prints_a_true_minus_sign(self) -> None:
        assert signed(-0.070592024) == "−0.070592"
        assert signed(0.258871, 2) == "0.26"


class TestTheReadPath:
    def test_drawing_with_no_results_reads_the_runs_path(self, monkeypatch, tmp_path, results):
        asked = []

        def read():
            asked.append(True)
            return results

        monkeypatch.setattr(figures, "read_results", read)
        drawn = make_roll_returns_figure(out=tmp_path / ROLL_RETURNS_FIGURE)
        assert asked == [True]
        assert len(drawn.axes) == 2

    def test_the_default_reads_each_strip_through_load_strip(self, monkeypatch, results) -> None:
        read = []

        def load(root, data_dir=None):
            read.append(root)
            return results[root].strip

        monkeypatch.setattr(figures, "load_strip", load)
        found = read_results()
        assert read == list(ROOTS)
        assert {root: found[root].alpha for root in ROOTS} == {
            root: results[root].alpha for root in ROOTS
        }

    def test_results_handed_in_are_the_results_drawn(self, tmp_path, results) -> None:
        """HG's α doubled, so a figure that read the files instead would fail."""
        changed = dict(results)
        changed["HG"] = dataclasses.replace(results["HG"], alpha=2 * results["HG"].alpha)
        drawn = make_roll_returns_figure(out=tmp_path / ROLL_RETURNS_FIGURE, results=changed)
        heights = [p.get_height() for p in _bars(drawn.axes[0], "alpha")]
        assert heights[ROOTS.index("HG")] == pytest.approx(200 * abs(results["HG"].alpha))

    def test_the_guard_runs_on_the_default_path(self, monkeypatch, tmp_path) -> None:
        """The figure reads through ``load_strip``, so a flagged day stops it too."""

        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("inputDataDaily_BR_20120813.mat changes scale")

        monkeypatch.setattr(roll_returns, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(WindowCrossesScaleBreak, match="changes scale"):
            make_roll_returns_figure(out=tmp_path / ROLL_RETURNS_FIGURE)

    def test_a_missing_vintage_reaches_the_operator_as_one_line(
        self, monkeypatch, tmp_path
    ) -> None:
        """The manifest is copied and the strips are not, so the refusal is the one a
        checkout without the files meets, and it names the first strip."""
        shutil.copy(paths.DATA_DIR / "vintages.jsonl", tmp_path)
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit) as stopped:
            main()
        message = str(stopped.value)
        assert "inputdatadaily_br_20120813" in message
        assert "\n" not in message

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage of CL saved 2012-08-14"),
            WindowCrossesScaleBreak("inputDataDaily_CL_20120813.mat changes scale"),
        ],
    )
    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(figures, "make_roll_returns_figure", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)

    def test_any_other_error_keeps_its_traceback(self, monkeypatch) -> None:
        def broken(*_a, **_k):
            raise KeyError("CL-SPOT")

        monkeypatch.setattr(figures, "make_roll_returns_figure", broken)
        with pytest.raises(KeyError, match="CL-SPOT"):
            main()

    def test_the_command_writes_the_committed_path(self, monkeypatch, capsys) -> None:
        drawn = []
        monkeypatch.setattr(figures, "make_roll_returns_figure", lambda **kw: drawn.append(kw))
        main()
        assert drawn == [{}]
        assert f"wrote {FIGURES_DIR / ROLL_RETURNS_FIGURE}" in capsys.readouterr().out

    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.is_file() and out.stat().st_size > 0


def test_the_committed_figure_exists() -> None:
    assert (FIGURES_DIR / ROLL_RETURNS_FIGURE).is_file()
