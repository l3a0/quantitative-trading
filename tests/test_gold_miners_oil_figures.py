"""The pins for the figure in the post on GLD, GDX and USO around July 2008.

``tests/test_gold_miners_oil.py`` holds what the run computes. This file holds
that the figure draws those numbers, so a generator that plotted the wrong
series, moved the split or mislabelled a panel fails even when the arithmetic
is right. Some numbers repeat here on purpose, because a figure's labels are
prose and the suite is the authority for every number prose quotes. No test
compares bytes, for the reason ``tests/test_regime_figure.py`` gives.

The figure reads the vintage and the specification
``tests/test_gold_miners_oil.py`` states in its module docstring: Chan's
``inputData_ETF.mat``, saved 2012-04-10, cut to GDX's first price, and
``johansen(·, 0, 1)`` on the first window, 2006-05-23 to 2008-07-14.

Exploratory, like everything location 1922 computes here.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from matplotlib.dates import date2num

from chan import gold_miners_oil_figures
from chan.gold_miners_oil import gold_miners_oil, read_sources
from chan.gold_miners_oil_figures import (
    BREAK_FIGURE,
    COLOURS,
    first_window_portfolio,
    main,
    make_break_figure,
    signed,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import GOOD, LOST
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable

SPLIT = pd.Timestamp("2008-07-14")


@pytest.fixture(scope="module")
def closes():
    return read_sources()[1]


@pytest.fixture(scope="module")
def portfolio(closes):
    return first_window_portfolio(closes, gold_miners_oil(closes))


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("gold_miners_oil_figure") / BREAK_FIGURE


@pytest.fixture(scope="module")
def figure(out, closes):
    return make_break_figure(out=out, closes=closes)


@pytest.fixture(scope="module")
def axes(figure):
    prices, z = figure.axes
    return {"prices": prices, "z": z}


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _title(ax) -> str:
    return ax.get_title(loc="left")


class TestThePanels:
    def test_there_are_two_sharing_the_date_axis_over_the_1481_days(
        self, figure, axes, closes
    ) -> None:
        assert len(figure.axes) == 2
        assert len(closes) == 1481
        limits = {ax.get_xlim() for ax in axes.values()}
        assert limits == {(date2num(closes.index[0]), date2num(closes.index[-1]))}
        assert axes["prices"].get_shared_x_axes().joined(axes["prices"], axes["z"])

    def test_both_mark_the_split_on_the_last_day_of_the_first_window(self, axes) -> None:
        for ax in axes.values():
            split = _by_gid(ax.lines)["split"]
            assert list(split.get_xdata()) == [SPLIT] * 2
            assert split.get_linestyle() == "--"

    def test_the_title_carries_the_label_and_the_note_names_the_file(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Exploratory: GLD and GDX either side of July 14, 2008, on Chan's own closes"
        )
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Algorithmic Trading, location 1922, 2006-05-23 to 2012-04-09, the 1,481 days "
            "GDX is priced.\nPrices from inputData_ETF.mat, saved 2012-04-10. The split date "
            "was chosen after the break was seen,\nso a test that splits there is favoured "
            "by construction."
        ]

    def test_drawing_with_no_closes_reads_the_committed_file(self, tmp_path, portfolio) -> None:
        """``main`` and the committed PNG take this path, so it is drawn here too."""
        drawn = make_break_figure(out=tmp_path / BREAK_FIGURE)
        after = _by_gid(drawn.axes[1].lines)["after"]
        np.testing.assert_array_equal(after.get_ydata(), portfolio.z.loc["2008-07-15":])


class TestTheCloses:
    def test_each_line_is_its_etfs_close(self, axes, closes) -> None:
        lines = _by_gid(axes["prices"].lines)
        for symbol in ("GLD", "GDX", "USO"):
            np.testing.assert_array_equal(lines[symbol].get_ydata(), closes[symbol])
        legend = [t.get_text() for t in axes["prices"].get_legend().get_texts()]
        assert legend == ["GLD", "GDX", "USO"]

    def test_each_line_and_its_legend_entry_share_one_colour(self, axes) -> None:
        """The legend is the only key to which line is which ETF."""
        lines = _by_gid(axes["prices"].lines)
        handles = axes["prices"].get_legend().legend_handles
        for symbol, handle in zip(("GLD", "GDX", "USO"), handles, strict=True):
            assert lines[symbol].get_color() == COLOURS[symbol]
            assert handle.get_color() == COLOURS[symbol]
        assert len(set(COLOURS.values())) == 3

    def test_the_peak_marker_is_usos_colour(self, axes) -> None:
        lines = _by_gid(axes["prices"].lines)
        assert lines["peak"].get_color() == lines["USO"].get_color()

    def test_usos_highest_close_is_the_split_day(self, axes, closes) -> None:
        """The fact Chan's oil story starts from, on his own file."""
        assert closes["USO"].idxmax() == SPLIT
        assert closes["USO"].max() == pytest.approx(117.48, abs=1e-9)
        peak = _by_gid(axes["prices"].lines)["peak"]
        assert list(peak.get_xdata()) == [SPLIT]
        assert list(peak.get_ydata()) == [closes["USO"].max()]

    def test_the_heading_names_the_peak(self, axes) -> None:
        assert _title(axes["prices"]) == (
            "The three closes on Chan's file. USO's highest, 117.48, is on 2008-07-14,\n"
            "the last day of Chan's first window, marked dashed."
        )


class TestTheFirstWindowPortfolio:
    def test_the_weights_are_the_first_windows_first_eigenvector(self, closes, portfolio):
        result = gold_miners_oil(closes)
        np.testing.assert_array_equal(portfolio.weights, result.before.eigenvectors[:, 0])
        assert portfolio.weights == pytest.approx((0.191134, -0.513914), abs=1e-6)

    def test_the_value_is_gld_and_gdx_in_those_shares(self, closes, portfolio) -> None:
        w_gld, w_gdx = portfolio.weights
        expected = w_gld * closes["GLD"] + w_gdx * closes["GDX"]
        np.testing.assert_allclose(portfolio.value, expected, atol=1e-12)

    def test_z_is_scaled_by_the_first_window_alone(self, portfolio) -> None:
        first = portfolio.z.loc[:"2008-07-14"]
        assert len(first) == 539
        assert first.mean() == pytest.approx(0, abs=1e-12)
        assert first.std() == pytest.approx(1, abs=1e-12)

    def test_the_ranges_either_side_of_the_split(self, portfolio) -> None:
        before, after = portfolio.z.loc[:"2008-07-14"], portfolio.z.loc["2008-07-15":]
        assert (len(before), len(after)) == (539, 942)
        assert (before.min(), before.max()) == pytest.approx((-3.236791, 2.557621), abs=1e-6)
        assert (after.min(), after.max()) == pytest.approx((0.472953, 13.521362), abs=1e-6)

    def test_before_the_split_it_crosses_its_mean_again_and_again(self, portfolio) -> None:
        """The post says it keeps crossing its average. It changes sign 61 times."""
        before = portfolio.z.loc[:"2008-07-14"].to_numpy()
        assert int((np.diff(np.sign(before)) != 0).sum()) == 61

    def test_after_the_split_it_never_comes_back_to_the_first_windows_mean(self, portfolio):
        assert (portfolio.z.loc["2008-07-15":] > 0).all()


class TestThePortfolioPanel:
    def test_the_two_lines_split_the_z_score_at_the_break(self, axes, portfolio) -> None:
        lines = _by_gid(axes["z"].lines)
        np.testing.assert_array_equal(lines["before"].get_ydata(), portfolio.z.loc[:"2008-07-14"])
        np.testing.assert_array_equal(lines["after"].get_ydata(), portfolio.z.loc["2008-07-15":])
        assert list(lines["zero"].get_ydata()) == [0, 0]

    def test_before_is_green_and_after_is_red(self, axes) -> None:
        """No legend tells the two apart, so the colour is the claim."""
        lines = _by_gid(axes["z"].lines)
        assert (lines["before"].get_color(), lines["after"].get_color()) == (GOOD, LOST)

    def test_the_heading_sets_the_weights_and_both_ranges(self, axes) -> None:
        assert _title(axes["z"]) == (
            "GLD and GDX in the first window's Johansen weights, 0.191 and −0.514 shares.\n"
            "From −3.24 to 2.56 in the 539 days before the split. From 0.47 to 13.52 in the "
            "942 after it,\nwhere it never comes back to the first window's mean."
        )

    def test_signed_prints_a_true_minus_sign(self) -> None:
        assert signed(-3.236791) == "−3.24"
        assert signed(0.472953) == "0.47"
        assert signed(-0.513914, 3) == "−0.514"


class TestTheFile:
    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.exists() and out.stat().st_size > 0

    def test_the_committed_figure_exists(self) -> None:
        assert (FIGURES_DIR / BREAK_FIGURE).is_file()

    def test_main_lets_any_other_error_through_as_itself(self, monkeypatch) -> None:
        def fail(*_a, **_k):
            raise ValueError("a bug, not a refusal")

        monkeypatch.setattr(gold_miners_oil_figures, "make_break_figure", fail)
        with pytest.raises(ValueError, match="a bug, not a refusal"):
            main()

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage is lifted from inputData_ETF.mat"),
            WindowCrossesScaleBreak("inputdata_etf/gdx.csv changes scale on 2008-01-02"),
        ],
    )
    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(gold_miners_oil_figures, "make_break_figure", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)
