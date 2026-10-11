"""The pins for the figure in the post on three hypothesis tests on TU momentum, Example 1.1.

``tests/test_tu_hypothesis_tests.py`` holds what the run computes. This file
holds that the figure draws those numbers, so a generator that drew the wrong
row, binned one panel differently, centred the Gaussian null on the observed
mean or gave it another spread fails even when the arithmetic is right. Some
numbers repeat here on purpose, because a figure's labels are prose and the
suite is the authority for every number prose quotes. No test compares bytes,
for the reason ``tests/test_regime_figure.py`` gives.

The figure reads the vintage and the specification
``tests/test_tu_hypothesis_tests.py`` names in its docstring, which ``SPEC``
below repeats for every failure message here:
``inputdataohlcdaily_20120511/tu.csv``, vendor ``chan-mat``, basis
``adjusted``, saved 2012-05-12, 2,000 days from 2004-06-01 to 2012-05-11, a
lookback of 250 and a hold of 25, seed 20261010 for the simulated returns and
seed 20261011 for the shuffled entry days. The run is ``tu_hypothesis_run`` in
``tests/conftest.py``, shared with that file.

Exploratory, like everything Example 1.1 computes here. Two of the four
histograms are checks added after a trial run on other seeds had seen
results.
"""

from __future__ import annotations

import dataclasses
import math

import numpy as np
import pytest
from matplotlib.colors import same_color
from matplotlib.ticker import FuncFormatter, MultipleLocator
from scipy.stats import norm

from chan import paths, tu_momentum
from chan import tu_hypothesis_tests_figures as figures
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST
from chan.series import WindowCrossesScaleBreak
from chan.tu_hypothesis_tests_figures import (
    BINS,
    TU_HYPOTHESIS_TESTS_FIGURE,
    axis_limits,
    bin_edges,
    gaussian_spread,
    main,
    make_tu_hypothesis_tests_figure,
    panel_series,
)
from chan.tu_momentum import read_sources
from chan.vintage import VintageUnavailable

SPEC = (
    "inputdataohlcdaily_20120511/tu.csv, chan-mat, adjusted, saved 2012-05-12, "
    "TU_mom_hypothesisTest.m with a lookback of 250 and a hold of 25, seeds 20261010 "
    "and 20261011"
)
OBSERVED = 6.626644e-05
SPREAD = 2.259145e-05


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def result(tu_hypothesis_run):
    return tu_hypothesis_run[0]


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("tu_hypothesis_tests_figure") / TU_HYPOTHESIS_TESTS_FIGURE


@pytest.fixture(scope="module")
def figure(out, result, sources):
    return make_tu_hypothesis_tests_figure(out=out, result=result, sources=sources)


@pytest.fixture(scope="module")
def axes(figure):
    gaussian, returns, trades = figure.axes
    return {"gaussian": gaussian, "returns": returns, "trades": trades}


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _stairs(ax) -> dict:
    return _by_gid(ax.patches)


def _legend(ax) -> list[str]:
    return [t.get_text() for t in ax.get_legend().get_texts()]


def _title(ax) -> str:
    return ax.get_title(loc="left")


class TestThePanels:
    def test_there_are_three_in_the_book_s_order(self, figure, axes) -> None:
        assert len(figure.axes) == 3
        assert _title(axes["gaussian"]).startswith("The first test:")
        assert _title(axes["returns"]).startswith("The second test:")
        assert _title(axes["trades"]).startswith("The third test, corrected:")

    def test_they_share_one_axis_of_mean_daily_return(self, axes, result) -> None:
        limits = {ax.get_xlim() for ax in axes.values()}
        assert limits == {axis_limits(result)}, SPEC
        joined = axes["trades"].get_shared_x_axes()
        assert joined.joined(axes["gaussian"], axes["returns"])
        assert joined.joined(axes["returns"], axes["trades"])
        assert axes["trades"].get_xlabel() == "mean daily strategy return"

    def test_the_axis_reaches_four_spreads_and_every_draw(self, result) -> None:
        low, high = axis_limits(result)
        assert low < -4 * SPREAD and high > 4 * SPREAD, SPEC
        for name, values in panel_series(result).items():
            assert low < values.min() and values.max() < high, (name, SPEC)
        assert low < OBSERVED < high

    def test_the_observed_mean_is_the_same_line_on_each(self, axes, result) -> None:
        assert result.observed_mean == pytest.approx(OBSERVED, rel=5e-7), SPEC
        for name, ax in axes.items():
            line = _by_gid(ax.lines)["observed"]
            assert list(line.get_xdata()) == [result.observed_mean] * 2, name
            assert same_color(line.get_color(), INK), name
            assert _legend(ax)[-1] == "observed mean", name

    def test_the_ticks_fall_every_5e_5_in_the_post_s_notation(self, axes) -> None:
        axis = axes["trades"].xaxis
        assert isinstance(axis.get_major_locator(), MultipleLocator)
        assert isinstance(axis.get_major_formatter(), FuncFormatter)
        low, high = axes["trades"].get_xlim()
        shown = [t for t in axis.get_major_locator()() if low <= t <= high]
        labels = [axis.get_major_formatter()(t) for t in shown]
        assert labels == ["−5e-5", "0", "5e-5", "1e-4"], SPEC

    def test_the_y_axis_carries_no_ticks_and_leaves_the_legend_room(self, axes) -> None:
        """A density of a daily return runs to tens of thousands, a number nobody reads.

        The legend sits at the upper left, and the top of each panel sits at
        least 1.55 times its tallest value above zero, so the legend covers no
        data. The 1.55 is written here rather than read from the module, so a
        module that dropped the headroom fails.
        """
        for name, ax in axes.items():
            assert list(ax.get_yticks()) == [], name
            assert ax.get_ylabel() == "share of draws, as a density"
            heights = [s.get_data().values.max() for s in _stairs(ax).values()]
            heights += [line.get_ydata().max() for line in ax.lines if line.get_gid() == "gaussian"]
            bottom, top = ax.get_ylim()
            assert bottom == 0, name
            assert top >= 1.55 * max(heights), name
            assert ax.get_legend()._loc == 2, name  # matplotlib's code for "upper left"

    def test_the_title_carries_the_exploratory_label(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Exploratory: three hypothesis tests on TU momentum, rerun on Chan's own file"
        )

    def test_the_note_names_the_file_the_seeds_the_trial_run_and_the_selection(
        self, figure
    ) -> None:
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Example 1.1 of Algorithmic Trading. TU from inputdataohlcdaily_20120511/tu.csv, "
            "saved 2012-05-12, 2004-06-01 to 2012-05-11.\nSeed 20261010 draws the simulated "
            "returns and seed 20261011 the shuffles.\nThe checks marked as added came after a "
            "trial run on other seeds.\nThe 250-day lookback and 25-day hold were picked from "
            "49 pairs on the same closes, and no p-value here is corrected for that."
        ], SPEC

    def test_no_label_is_parsed_as_math(self, figure) -> None:
        for ax in figure.axes:
            for text in [*ax.texts, ax.title, ax._left_title]:
                assert text.get_parse_math() is False
        for text in figure.texts:
            assert text.get_parse_math() is False


class TestTheHistograms:
    def test_each_draws_its_row_s_means(self, axes, result) -> None:
        """10,000 means for each row on seed 20261010 and 100,000 on seed 20261011."""
        series = panel_series(result)
        assert {name: len(values) for name, values in series.items()} == {
            "mean-zero": 10_000,
            "declared": 10_000,
            "normal": 10_000,
            "shuffled": 100_000,
        }, SPEC
        np.testing.assert_array_equal(series["mean-zero"], result.returns.mean_zero)
        np.testing.assert_array_equal(series["declared"], result.returns.declared)
        np.testing.assert_array_equal(series["normal"], result.returns.normal)
        np.testing.assert_array_equal(series["shuffled"], result.trades)

    def test_each_panel_holds_the_rows_it_names(self, axes) -> None:
        assert set(_stairs(axes["gaussian"])) == {"mean-zero"}
        assert set(_stairs(axes["returns"])) == {"declared", "normal"}
        assert set(_stairs(axes["trades"])) == {"shuffled"}

    def test_every_histogram_shares_one_set_of_edges(self, axes, result) -> None:
        edges = bin_edges(result)
        assert len(edges) == BINS + 1
        assert (edges[0], edges[-1]) == axis_limits(result)
        for ax in axes.values():
            for gid, stairs in _stairs(ax).items():
                np.testing.assert_array_equal(stairs.get_data().edges, edges, err_msg=gid)

    def test_each_is_its_row_s_density_with_every_draw_inside(self, axes, result) -> None:
        edges = bin_edges(result)
        series = panel_series(result)
        width = edges[1] - edges[0]
        for ax in axes.values():
            for gid, stairs in _stairs(ax).items():
                values = stairs.get_data().values
                expected, _ = np.histogram(series[gid], bins=edges, density=True)
                np.testing.assert_array_equal(values, expected, err_msg=gid)
                counts, _ = np.histogram(series[gid], bins=edges)
                assert counts.sum() == len(series[gid]), gid
                assert values.sum() * width == pytest.approx(1, rel=1e-9), gid

    def test_the_shuffled_means_are_the_narrowest(self, result) -> None:
        """3.788199e-06 against 2.819219e-05, the spreads the post quotes."""
        spreads = {name: values.std(ddof=1) for name, values in panel_series(result).items()}
        assert spreads["shuffled"] == pytest.approx(3.788199e-06, rel=5e-7), SPEC
        assert spreads["declared"] == pytest.approx(2.819219e-05, rel=5e-7), SPEC
        assert min(spreads, key=spreads.get) == "shuffled"

    def test_the_book_s_tests_are_filled_brass_and_the_added_checks_are_outlines(
        self, axes
    ) -> None:
        for gid, filled, colour in (
            ("declared", True, ACCENT),
            ("shuffled", True, ACCENT),
            ("normal", False, GOOD),
            ("mean-zero", False, LOST),
        ):
            stairs = next(s for ax in axes.values() for g, s in _stairs(ax).items() if g == gid)
            assert stairs.get_fill() is filled, gid
            paint = stairs.get_facecolor() if filled else stairs.get_edgecolor()
            assert same_color(paint[:3], colour), gid


class TestTheGaussianNull:
    def test_the_dashed_curve_is_centred_on_zero_with_the_null_s_spread(self, axes, result) -> None:
        line = _by_gid(axes["gaussian"].lines)["gaussian"]
        assert line.get_linestyle() == "--"
        assert same_color(line.get_color(), ACCENT)
        x, y = np.asarray(line.get_xdata()), np.asarray(line.get_ydata())
        assert gaussian_spread(result) == pytest.approx(SPREAD, rel=5e-7), SPEC
        np.testing.assert_allclose(y, norm.pdf(x, loc=0.0, scale=SPREAD), rtol=5e-7)
        assert x[np.argmax(y)] == pytest.approx(0, abs=(x[1] - x[0]))
        assert y.max() == pytest.approx(1 / (SPREAD * math.sqrt(2 * math.pi)), rel=1e-3)

    def test_it_spans_the_shared_axis(self, axes, result) -> None:
        x = _by_gid(axes["gaussian"].lines)["gaussian"].get_xdata()
        assert (x[0], x[-1]) == axis_limits(result)
        assert len(x) == figures.CURVE_POINTS


class TestTheLabels:
    def test_the_first_panel_gives_the_tail_and_the_count_of_19(self, axes) -> None:
        assert _legend(axes["gaussian"]) == [
            "Gaussian null of the mean, one-sided tail 0.001677",
            "type IV with the mean set to zero, added after a trial run: 19 of 10,000 at or above",
            "observed mean",
        ], SPEC

    def test_the_second_panel_gives_1221_and_1165(self, axes) -> None:
        assert _legend(axes["returns"]) == [
            "type IV with TU's four moments: 1,221 of 10,000 at or above",
            "normal with TU's mean and std, added after a trial run: 1,165 of 10,000 at or above",
            "observed mean",
        ], SPEC

    def test_the_third_panel_gives_0_of_100000(self, axes) -> None:
        assert _legend(axes["trades"]) == [
            "shuffled entry days, corrected: 0 of 100,000 at or above",
            "observed mean",
        ], SPEC

    def test_only_the_two_added_checks_say_they_were_added(self, axes) -> None:
        added = [
            label
            for ax in axes.values()
            for label in _legend(ax)
            if "added after a trial run" in label
        ]
        assert len(added) == 2
        assert added[0].startswith("type IV with the mean set to zero")
        assert added[1].startswith("normal with TU's mean and std")

    def test_the_headings(self, axes) -> None:
        assert _title(axes["gaussian"]) == (
            "The first test: the mean of 2,000 normal days with a mean of zero and the "
            "strategy's std,\nwhich spreads by 2.26e-5. Removing TU's drift from the type IV "
            "draws gives nearly the same null."
        ), SPEC
        assert _title(axes["returns"]) == (
            "The second test: the rule rerun on simulated returns. Type IV and a normal draw "
            "share TU's mean\nand spread, and their means sit almost on top of each other, "
            "shifted right of the first panel's."
        )
        assert _title(axes["trades"]) == (
            "The third test, corrected: the long and short entry days shuffled on TU's own "
            "returns.\nThe means sit in a narrow band, and none reaches the observed mean."
        )

    def test_the_counts_follow_the_result_rather_than_the_text(
        self, tmp_path, result, sources
    ) -> None:
        """Three shuffled means moved above the observed mean must show as 3 of 100,000."""
        trades = result.trades.copy()
        trades[:3] = 2 * result.observed_mean
        moved = dataclasses.replace(result, trades=trades)
        drawn = make_tu_hypothesis_tests_figure(
            out=tmp_path / TU_HYPOTHESIS_TESTS_FIGURE, result=moved, sources=sources
        )
        assert _legend(drawn.axes[2])[0] == (
            "shuffled entry days, corrected: 3 of 100,000 at or above"
        )


class TestTheReadPath:
    def test_drawing_with_no_result_runs_the_tests_on_the_closes_read(
        self, monkeypatch, tmp_path, sources, result
    ) -> None:
        read, ran = [], []

        def reading():
            read.append(True)
            return sources

        def running(closes):
            ran.append(closes)
            return result

        monkeypatch.setattr(figures, "read_sources", reading)
        monkeypatch.setattr(figures, "hypothesis_tests", running)
        make_tu_hypothesis_tests_figure(out=tmp_path / TU_HYPOTHESIS_TESTS_FIGURE)
        assert read == [True]
        assert len(ran) == 1
        np.testing.assert_array_equal(ran[0], sources[1].to_numpy(dtype=float))

    def test_a_result_handed_in_is_the_result_drawn(self, tmp_path, result, sources) -> None:
        shifted = dataclasses.replace(result, trades=result.trades + 1e-5)
        drawn = make_tu_hypothesis_tests_figure(
            out=tmp_path / TU_HYPOTHESIS_TESTS_FIGURE, result=shifted, sources=sources
        )
        values = _stairs(drawn.axes[2])["shuffled"].get_data().values
        expected, _ = np.histogram(shifted.trades, bins=bin_edges(shifted), density=True)
        np.testing.assert_array_equal(values, expected)
        original, _ = np.histogram(result.trades, bins=bin_edges(shifted), density=True)
        assert not np.array_equal(values, original)

    def test_the_guard_runs_even_when_a_result_is_handed_in(
        self, monkeypatch, tmp_path, result
    ) -> None:
        """The note names the vintage, so the closes are read, and a flagged day stops it."""

        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("inputdataohlcdaily_20120511/tu.csv changes scale")

        monkeypatch.setattr(tu_momentum, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(WindowCrossesScaleBreak, match="tu.csv changes scale"):
            make_tu_hypothesis_tests_figure(
                out=tmp_path / TU_HYPOTHESIS_TESTS_FIGURE, result=result
            )

    def test_a_missing_vintage_reaches_the_operator_as_one_line(
        self, monkeypatch, tmp_path
    ) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit) as stopped:
            main()
        message = str(stopped.value)
        assert "inputDataOHLCDaily_20120511.mat" in message
        assert "\n" not in message

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage of TU saved 2012-05-12"),
            WindowCrossesScaleBreak("inputdataohlcdaily_20120511/tu.csv changes scale"),
        ],
    )
    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(figures, "make_tu_hypothesis_tests_figure", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)

    def test_any_other_error_keeps_its_traceback(self, monkeypatch) -> None:
        def broken(*_a, **_k):
            raise KeyError("TU")

        monkeypatch.setattr(figures, "make_tu_hypothesis_tests_figure", broken)
        with pytest.raises(KeyError, match="TU"):
            main()

    def test_the_command_writes_the_committed_path(self, monkeypatch, capsys) -> None:
        drawn = []
        monkeypatch.setattr(
            figures, "make_tu_hypothesis_tests_figure", lambda **kw: drawn.append(kw)
        )
        main()
        assert drawn == [{}]
        assert f"wrote {FIGURES_DIR / TU_HYPOTHESIS_TESTS_FIGURE}" in capsys.readouterr().out

    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.is_file() and out.stat().st_size > 0


def test_the_committed_figure_exists() -> None:
    assert (FIGURES_DIR / TU_HYPOTHESIS_TESTS_FIGURE).is_file()
