"""The pins for the figure in the post on Bollinger bands on GLD and USO, Example 3.2.

``tests/test_bollinger.py`` holds what the run computes. This file holds that
the figure draws those numbers, so a generator that plotted the wrong series,
swapped a panel, mislabelled a run or dropped a band line fails even when the
arithmetic is right. Some numbers repeat here on purpose, because a figure's
labels are prose and the suite is the authority for every number prose quotes.
No test compares bytes, for the reason ``tests/test_regime_figure.py`` gives.

The figure reads the vintage and the specification ``tests/test_bollinger.py``
names as its ``SPEC``, which every failure message here carries too. The
dashed line is the run with ``movingStd`` swapped for ``smartMovingStd``, and
it is held here against that file's ``by_n`` fixture, built the same way.

Exploratory, like everything Example 3.2 computes here.
"""

from __future__ import annotations

import numpy as np
import pytest
from matplotlib.dates import DateFormatter, YearLocator, date2num

from chan import bollinger_figures as figures
from chan import paths, price_spread
from chan.bollinger import example_three_two
from chan.bollinger_figures import (
    BOLLINGER_FIGURE,
    RUNS,
    cumulative_return,
    divided_by_n,
    legend_label,
    main,
    make_bollinger_figure,
)
from chan.matlab_helpers import smart_moving_std
from chan.paths import FIGURES_DIR
from chan.price_spread import read_sources
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable
from tests.test_bollinger import SPEC


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def result(sources):
    return example_three_two(sources[1])


@pytest.fixture(scope="module")
def by_n(sources):
    """The run with ``smartMovingStd`` in place of ``movingStd``, as ``tests/test_bollinger.py``
    builds it, so the figure's own helper is checked against the patched run path."""
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(price_spread, "moving_std", smart_moving_std)
        return example_three_two(sources[1])


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("bollinger_figure") / BOLLINGER_FIGURE


@pytest.fixture(scope="module")
def figure(out, sources):
    return make_bollinger_figure(out=out, sources=sources)


@pytest.fixture(scope="module")
def axes(figure):
    z, units, returns = figure.axes
    return {"zscore": z, "units": units, "returns": returns}


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _title(ax) -> str:
    return ax.get_title(loc="left")


class TestThePanels:
    def test_there_are_three_in_the_order_the_post_reads_them(self, figure, axes) -> None:
        assert len(figure.axes) == 3
        assert _title(axes["zscore"]).startswith("The 20-day z-score of the price spread")
        assert _title(axes["units"]).startswith("The units held")
        assert _title(axes["returns"]).startswith("Figure 3.3: the band's compounded return")

    def test_they_share_the_date_axis_over_the_1480_traded_days(self, axes, result) -> None:
        days = result.bollinger.signal.days
        assert len(days) == 1480, SPEC
        limits = {ax.get_xlim() for ax in axes.values()}
        assert limits == {(date2num(days[0]), date2num(days[-1]))}, SPEC
        shared = axes["zscore"].get_shared_x_axes()
        assert shared.joined(axes["zscore"], axes["units"])
        assert shared.joined(axes["zscore"], axes["returns"])

    def test_the_date_ticks_read_as_years(self, axes) -> None:
        axis = axes["returns"].xaxis
        assert isinstance(axis.get_major_locator(), YearLocator)
        assert isinstance(axis.get_major_formatter(), DateFormatter)
        assert axis.get_major_formatter().fmt == "%Y"

    def test_the_title_carries_the_exploratory_label(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Exploratory: Example 3.2 redrawn on Chan's own GLD and USO closes"
        )

    def test_the_note_names_the_file_the_window_and_the_hindsight(self, figure) -> None:
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Example 3.2 of Algorithmic Trading, 2006-05-24 to 2012-04-09, the 1,480 days left "
            "once the first 20 are dropped.\nPrices from inputData_ETF.mat, saved 2012-04-10. "
            "Chan's 20-day lookback was chosen with hindsight, so every figure is in-sample."
        ], SPEC

    def test_no_label_is_parsed_as_math(self, figure) -> None:
        for ax in figure.axes:
            for text in [*ax.texts, ax.title, ax._left_title]:
                assert text.get_parse_math() is False
        for text in figure.texts:
            assert text.get_parse_math() is False


class TestTheZScore:
    def test_the_line_is_the_z_score_the_band_traded_on(self, axes, result) -> None:
        line = _by_gid(axes["zscore"].lines)["zscore"]
        assert list(line.get_xdata()) == list(result.bollinger.signal.days), SPEC
        np.testing.assert_array_equal(line.get_ydata(), result.zscore)

    def test_the_band_lines_sit_at_minus_1_0_and_1(self, axes) -> None:
        lines = _by_gid(axes["zscore"].lines)
        levels = {
            gid: list(lines[gid].get_ydata()) for gid in ("long-entry", "exit", "short-entry")
        }
        assert levels == {"long-entry": [-1, -1], "exit": [0, 0], "short-entry": [1, 1]}

    def test_the_entries_are_dashed_and_the_exit_is_solid(self, axes) -> None:
        lines = _by_gid(axes["zscore"].lines)
        styles = {gid: lines[gid].get_linestyle() for gid in ("long-entry", "exit", "short-entry")}
        assert styles == {"long-entry": "--", "exit": "-", "short-entry": "--"}

    def test_the_axis_holds_every_z_score(self, axes, result) -> None:
        bottom, top = axes["zscore"].get_ylim()
        assert bottom < np.nanmin(result.zscore) and np.nanmax(result.zscore) < top
        assert bottom == -top

    def test_the_heading_names_the_rule(self, axes) -> None:
        assert _title(axes["zscore"]) == (
            "The 20-day z-score of the price spread USO − h·GLD.\n"
            "A long enters below −1 and a short above 1, and each exits when the z-score "
            "crosses 0."
        )


class TestTheUnits:
    def test_the_line_is_the_units_held(self, axes, result) -> None:
        line = _by_gid(axes["units"].lines)["units"]
        assert list(line.get_xdata()) == list(result.bollinger.signal.days), SPEC
        np.testing.assert_array_equal(line.get_ydata(), result.bollinger.units)

    def test_the_units_take_only_minus_1_0_and_1(self, axes) -> None:
        line = _by_gid(axes["units"].lines)["units"]
        assert set(np.unique(line.get_ydata()).tolist()) == {-1.0, 0.0, 1.0}, SPEC

    def test_each_day_holds_until_the_next_change(self, axes) -> None:
        """A unit is held from one close to the next, so the line steps rather than slopes."""
        assert _by_gid(axes["units"].lines)["units"].get_drawstyle() == "steps-post"

    def test_the_ticks_name_each_position(self, axes) -> None:
        ticks = axes["units"].get_yticks()
        labels = [t.get_text() for t in axes["units"].get_yticklabels()]
        assert list(ticks) == [-1, 0, 1]
        assert labels == ["short −1", "flat 0", "long 1"]

    def test_the_heading_counts_the_days_and_the_changes(self, axes) -> None:
        assert _title(axes["units"]) == (
            "The units held: short on 547 days, flat on 334 and long on 599.\n"
            "They change on 162 days, where the linear rule's change on 1,460."
        ), SPEC


class TestTheReturns:
    def test_there_is_one_line_per_run(self, axes) -> None:
        assert [gid for gid, *_ in RUNS] == ["bollinger", "linear", "by_n"]
        assert set(_by_gid(axes["returns"].lines)) >= {"bollinger", "linear", "by_n", "zero"}

    def test_each_line_is_its_runs_cumulative_return(self, axes, result, by_n) -> None:
        lines = _by_gid(axes["returns"].lines)
        for gid, run in (
            ("bollinger", result.bollinger),
            ("linear", result.linear),
            ("by_n", by_n.bollinger),
        ):
            expected = np.cumprod(1 + run.daily) - 1
            assert list(lines[gid].get_xdata()) == list(run.signal.days), gid
            np.testing.assert_array_equal(lines[gid].get_ydata(), expected, err_msg=gid)
            np.testing.assert_array_equal(cumulative_return(run), expected)

    def test_each_line_ends_where_its_apr_says(self, axes, result, by_n) -> None:
        """The last value is the APR carried back over 1,480 of 252 days."""
        lines = _by_gid(axes["returns"].lines)
        for gid, run in (
            ("bollinger", result.bollinger),
            ("linear", result.linear),
            ("by_n", by_n.bollinger),
        ):
            last = lines[gid].get_ydata()[-1]
            assert last == pytest.approx((1 + run.apr) ** (1480 / 252) - 1, abs=1e-9), SPEC

    def test_the_diagnostic_is_the_band_with_the_deviation_divided_by_n(self, result, by_n) -> None:
        diagnostic = divided_by_n(result.bollinger)
        np.testing.assert_array_equal(diagnostic.units, by_n.bollinger.units)
        np.testing.assert_array_equal(diagnostic.daily, by_n.bollinger.daily)

    def test_only_the_diagnostic_is_dashed(self, axes) -> None:
        lines = _by_gid(axes["returns"].lines)
        styles = {gid: lines[gid].get_linestyle() for gid, *_ in RUNS}
        assert styles == {"bollinger": "-", "linear": "-", "by_n": "--"}

    def test_the_legend_sets_each_runs_two_figures(self, axes) -> None:
        legend = [t.get_text() for t in axes["returns"].get_legend().get_texts()]
        assert legend == [
            "the band, bollinger.m: APR 0.178249, Sharpe ratio 0.964673",
            "the linear rule, Example 3.1: APR 0.108335, Sharpe ratio 0.589651",
            "the band, deviation divided by n, a diagnostic: APR 0.183306, Sharpe ratio 0.984872",
        ], SPEC

    def test_the_legend_label_reads_the_run_it_is_given(self, result) -> None:
        assert legend_label(result.linear, "x") == "x: APR 0.108335, Sharpe ratio 0.589651"

    def test_the_heading_and_axis_read_as_compounded_percent(self, axes) -> None:
        returns = axes["returns"]
        assert _title(returns) == (
            "Figure 3.3: the band's compounded return, beside the linear rule's on the same "
            "spread.\nUnlevered and before costs. The dashed line is a diagnostic, not Chan's run."
        )
        assert returns.yaxis.get_major_formatter()(0.5) == "50%"
        assert returns.get_ylabel() == "cumulative return, compounded"

    def test_a_line_marks_zero(self, axes) -> None:
        assert list(_by_gid(axes["returns"].lines)["zero"].get_ydata()) == [0, 0]

    def test_the_legend_sits_above_every_line(self, axes) -> None:
        """The top leaves 40 percent of the lines' range clear for the legend, and the
        bottom clears the lowest line."""
        lines = _by_gid(axes["returns"].lines)
        ys = [lines[gid].get_ydata() for gid, *_ in RUNS]
        low, high = min(y.min() for y in ys), max(y.max() for y in ys)
        bottom, top = axes["returns"].get_ylim()
        assert top == pytest.approx(high + 0.4 * (high - low))
        assert bottom == pytest.approx(low - 0.08 * (high - low))


class TestTheReadPath:
    def test_drawing_with_no_sources_reads_the_runs_path(self, monkeypatch, tmp_path, sources):
        asked = []

        def read():
            asked.append(True)
            return sources

        monkeypatch.setattr(figures, "read_sources", read)
        drawn = make_bollinger_figure(out=tmp_path / BOLLINGER_FIGURE)
        assert asked == [True]
        line = _by_gid(drawn.axes[0].lines)["zscore"]
        np.testing.assert_array_equal(line.get_ydata(), example_three_two(sources[1]).zscore)

    def test_sources_handed_in_are_the_sources_drawn(self, tmp_path, sources, result) -> None:
        """USO raised by 10 dollars, so a figure that ignored the argument and read the file
        would fail. Doubling USO would not do, because it doubles the spread and both legs'
        dollars, and the z-score and the return each cancel that."""
        members, closes = sources
        shifted = closes.assign(USO=closes["USO"] + 10)
        drawn = make_bollinger_figure(out=tmp_path / BOLLINGER_FIGURE, sources=(members, shifted))
        line = _by_gid(drawn.axes[2].lines)["bollinger"]
        expected = cumulative_return(example_three_two(shifted).bollinger)
        np.testing.assert_array_equal(line.get_ydata(), expected)
        assert not np.array_equal(expected, cumulative_return(result.bollinger))

    def test_the_guard_runs_on_the_default_path(self, monkeypatch, tmp_path) -> None:
        """The figure reads through ``read_sources``, so a flagged day stops it too."""

        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("inputdata_etf/uso.csv changes scale on 2009-01-02")

        monkeypatch.setattr(price_spread, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(WindowCrossesScaleBreak, match="uso.csv changes scale"):
            make_bollinger_figure(out=tmp_path / BOLLINGER_FIGURE)

    def test_a_missing_vintage_reaches_the_operator_as_one_line(
        self, monkeypatch, tmp_path
    ) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert "inputData_ETF.mat" in str(stopped.value)
        assert "\n" not in str(stopped.value)

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage is lifted from inputData_ETF.mat"),
            WindowCrossesScaleBreak("inputdata_etf/gld.csv changes scale on 2008-01-02"),
        ],
    )
    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(figures, "make_bollinger_figure", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)

    def test_any_other_error_keeps_its_traceback(self, monkeypatch) -> None:
        def broken(*_a, **_k):
            raise KeyError("Close")

        monkeypatch.setattr(figures, "make_bollinger_figure", broken)
        with pytest.raises(KeyError, match="Close"):
            main()

    def test_the_command_writes_the_committed_path(self, monkeypatch, capsys) -> None:
        drawn = []
        monkeypatch.setattr(figures, "make_bollinger_figure", lambda **kw: drawn.append(kw))
        main()
        assert drawn == [{}]
        assert f"wrote {FIGURES_DIR / BOLLINGER_FIGURE}" in capsys.readouterr().out

    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.is_file() and out.stat().st_size > 0


def test_the_committed_figure_exists() -> None:
    assert (FIGURES_DIR / BOLLINGER_FIGURE).is_file()
