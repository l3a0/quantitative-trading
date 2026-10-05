"""The pins for the figure in the post on Example 3.1's price spread, log price spread and ratio.

``tests/test_price_spread.py`` holds what the run computes. This file holds that
the figure draws those numbers, so a generator that plotted the wrong series,
swapped a panel or mislabelled a run fails even when the arithmetic is right.
Some numbers repeat here on purpose, because a figure's labels are prose and
the suite is the authority for every number prose quotes. No test compares
bytes, for the reason ``tests/test_regime_figure.py`` gives.

The figure reads the vintage and the specification ``tests/test_price_spread.py``
names as its ``SPEC``, which every failure message here carries too.

Exploratory, like everything Example 3.1 computes here.
"""

from __future__ import annotations

import numpy as np
import pytest
from matplotlib.dates import date2num

from chan import price_spread_figures
from chan.paths import FIGURES_DIR
from chan.price_spread import example_three_one, read_sources
from chan.price_spread_figures import (
    RUNS,
    SIGNALS_FIGURE,
    cumulative_return,
    legend_label,
    main,
    make_signals_figure,
)
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable
from tests.test_price_spread import SPEC


@pytest.fixture(scope="module")
def result():
    return example_three_one(read_sources()[1])


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("price_spread_figure") / SIGNALS_FIGURE


@pytest.fixture(scope="module")
def figure(out, result):
    return make_signals_figure(out=out, result=result)


@pytest.fixture(scope="module")
def axes(figure):
    hedge, spread, ratio, returns = figure.axes
    return {"hedge": hedge, "spread": spread, "ratio": ratio, "returns": returns}


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _title(ax) -> str:
    return ax.get_title(loc="left")


class TestThePanels:
    def test_there_are_four_in_the_order_the_post_reads_them(self, figure, axes) -> None:
        assert len(figure.axes) == 4
        assert _title(axes["hedge"]).startswith("The hedge ratio h")
        assert _title(axes["spread"]) == "Figure 3.1: the price spread USO − h·GLD."
        assert _title(axes["ratio"]) == "Figure 3.2: the ratio USO/GLD."
        assert _title(axes["returns"]).startswith("Each run's compounded return")

    def test_they_share_the_date_axis_over_the_traded_days(self, axes, result) -> None:
        days = result.price_spread.signal.days
        limits = {ax.get_xlim() for ax in axes.values()}
        assert limits == {(date2num(days[0]), date2num(days[-1]))}, SPEC
        assert axes["hedge"].get_shared_x_axes().joined(axes["hedge"], axes["returns"])

    def test_the_title_carries_the_label_and_the_note_names_the_file(self, figure) -> None:
        assert figure._suptitle.get_text().startswith("Exploratory:")
        note = " ".join(t.get_text() for t in figure.texts)
        assert "2006-05-24 to 2012-04-09, the 1,480 days" in note, SPEC
        assert "inputData_ETF.mat, saved 2012-04-10" in note
        assert "chosen with hindsight" in note


class TestTheSignals:
    def test_the_hedge_panel_draws_the_hedge_ratio_and_its_zero(self, axes, result) -> None:
        hedge = _by_gid(axes["hedge"].lines)
        signal = result.price_spread.signal
        assert list(hedge["hedge"].get_xdata()) == list(signal.days), SPEC
        np.testing.assert_array_equal(hedge["hedge"].get_ydata(), signal.hedge)
        assert list(hedge["zero"].get_ydata()) == [0, 0]

    def test_the_hedge_heading_counts_the_negative_days(self, axes) -> None:
        assert _title(axes["hedge"]) == (
            "The hedge ratio h, refitted on the last 20 days.\n"
            "Below zero on 334 of 1,480 days, when one unit holds both ETFs long."
        ), SPEC

    def test_the_shading_fills_only_the_days_below_zero(self, axes, result) -> None:
        shaded = _by_gid(axes["hedge"].collections)["negative"]
        vertices = np.concatenate([path.vertices for path in shaded.get_paths()])
        assert (vertices[:, 1] <= 0).all()
        assert vertices[:, 1].min() == pytest.approx(result.price_spread.signal.hedge.min())

    def test_the_spread_panel_draws_figure_3_1(self, axes, result) -> None:
        line = _by_gid(axes["spread"].lines)["spread"]
        np.testing.assert_array_equal(line.get_ydata(), result.price_spread.signal.value)

    def test_the_ratio_panel_draws_figure_3_2_as_uso_over_gld(self, axes, result) -> None:
        line = _by_gid(axes["ratio"].lines)["ratio"]
        np.testing.assert_array_equal(line.get_ydata(), result.ratio.signal.value)
        assert result.ratio.signal.name == "ratio"


class TestTheReturns:
    def test_there_is_one_line_per_run(self, axes) -> None:
        lines = _by_gid(axes["returns"].lines)
        assert [attribute for attribute, *_ in RUNS] == [
            "price_spread",
            "log_price_spread",
            "ratio",
            "swapped_ratio",
        ]
        assert set(lines) >= {attribute for attribute, *_ in RUNS}

    def test_each_line_is_its_runs_cumulative_return(self, axes, result) -> None:
        lines = _by_gid(axes["returns"].lines)
        for attribute, *_ in RUNS:
            run = getattr(result, attribute)
            expected = np.cumprod(1 + run.daily) - 1
            assert lines[attribute].get_ydata() == pytest.approx(expected, abs=1e-12), SPEC
            np.testing.assert_array_equal(cumulative_return(run), expected)

    def test_each_line_ends_where_its_apr_says(self, axes, result) -> None:
        """The last value is the APR carried back over 1,480 of 252 days."""
        lines = _by_gid(axes["returns"].lines)
        for attribute, *_ in RUNS:
            apr = getattr(result, attribute).apr
            last = lines[attribute].get_ydata()[-1]
            assert last == pytest.approx((1 + apr) ** (1480 / 252) - 1, abs=1e-9), SPEC

    def test_only_the_swapped_ratio_is_dashed(self, axes) -> None:
        lines = _by_gid(axes["returns"].lines)
        dashed = {gid for gid, line in lines.items() if line.get_linestyle() == "--"}
        assert dashed == {"swapped_ratio"}

    def test_the_legend_sets_each_runs_two_figures(self, axes) -> None:
        legend = [t.get_text() for t in axes["returns"].get_legend().get_texts()]
        assert legend == [
            "price spread: APR 0.108335, Sharpe ratio 0.589651",
            "log price spread: APR 0.088863, Sharpe ratio 0.504153",
            "ratio, as Ratio.m publishes it: APR -0.134608, Sharpe ratio -0.702522",
            "ratio, GLD and USO swapped, tried after the miss: APR -0.141522, "
            "Sharpe ratio -0.746663",
        ], SPEC

    def test_the_legend_label_reads_the_run_it_is_given(self, result) -> None:
        assert legend_label(result.ratio, "x") == "x: APR -0.134608, Sharpe ratio -0.702522"

    def test_the_legend_sits_above_every_line(self, axes) -> None:
        lines = _by_gid(axes["returns"].lines)
        highest = max(lines[attribute].get_ydata().max() for attribute, *_ in RUNS)
        assert axes["returns"].get_ylim()[1] > highest * 1.3


class TestTheFile:
    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.exists() and out.stat().st_size > 0

    def test_the_committed_figure_exists(self) -> None:
        assert (FIGURES_DIR / SIGNALS_FIGURE).is_file()

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage is lifted from inputData_ETF.mat"),
            WindowCrossesScaleBreak("inputdata_etf/uso.csv changes scale on 2009-01-02"),
        ],
    )
    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(price_spread_figures, "make_signals_figure", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)
