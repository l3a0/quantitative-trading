"""The pins for the figure in the post on the Kalman filter hedge ratio on EWA and EWC.

``tests/test_kalman_hedge.py`` holds what the run computes. This file holds
that the figure draws those numbers, so a generator that plotted the wrong
series, started the forecast error on the wrong row, put a year's step at the
wrong mean or marked the wrong day fails even when the arithmetic is right.
Some numbers repeat here on purpose, because a figure's labels are prose and
the suite is the authority for every number prose quotes. No test compares
bytes, for the reason ``tests/test_regime_figure.py`` gives.

The figure reads the vintage and the specification
``tests/test_kalman_hedge.py`` names as its ``SPEC``, which every failure
message here carries too.

One number is pinned here and nowhere else: where each cumulative line ends,
2.999998 for the script and 2.970231 with no signal on rows 1 and 2. Each is
tied to its run's APR, which ``tests/test_kalman_hedge.py`` pins, by the
compounding the APR undoes.

Exploratory, like everything ``KF_beta_EWA_EWC.m`` computes here.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from matplotlib.dates import DateFormatter, YearLocator, date2num

from chan import kalman_hedge as experiment
from chan import kalman_hedge_figures as figures
from chan import paths
from chan.kalman_hedge import kalman_hedge, read_sources
from chan.kalman_hedge_figures import (
    KALMAN_FIGURE,
    cumulative_return,
    main,
    make_kalman_figure,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable
from tests.test_kalman_hedge import SPEC

#: Each calendar year's mean intercept, as ``TestTheInterceptFinding`` pins them.
YEARLY = {
    2006: 0.1440,
    2007: 0.6336,
    2008: 2.5795,
    2009: 5.6350,
    2010: 6.0380,
    2011: 6.5851,
    2012: 6.7748,
}


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def result(sources):
    return kalman_hedge(sources[1])


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("kalman_hedge_figure") / KALMAN_FIGURE


@pytest.fixture(scope="module")
def figure(out, sources):
    return make_kalman_figure(out=out, sources=sources)


@pytest.fixture(scope="module")
def axes(figure):
    slope, intercept, error, returns = figure.axes
    return {"slope": slope, "intercept": intercept, "error": error, "returns": returns}


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _title(ax) -> str:
    return ax.get_title(loc="left")


def _legend(ax) -> list[str]:
    return [t.get_text() for t in ax.get_legend().get_texts()]


class TestThePanels:
    def test_there_are_four_in_the_order_the_post_reads_them(self, figure, axes) -> None:
        assert len(figure.axes) == 4
        for name, figure_number in (
            ("slope", "3.5"),
            ("intercept", "3.6"),
            ("error", "3.7"),
            ("returns", "3.8"),
        ):
            assert _title(axes[name]).startswith(f"Figure {figure_number}: "), name

    def test_all_four_share_the_files_1500_days(self, axes, result) -> None:
        days = result.filter.days
        assert len(days) == 1500, SPEC
        assert {ax.get_xlim() for ax in axes.values()} == {
            (date2num(days[0]), date2num(days[-1]))
        }, SPEC
        first = axes["slope"]
        assert all(first.get_shared_x_axes().joined(first, ax) for ax in axes.values())

    def test_the_date_ticks_read_as_years(self, axes) -> None:
        axis = axes["returns"].xaxis
        assert isinstance(axis.get_major_locator(), YearLocator)
        assert isinstance(axis.get_major_formatter(), DateFormatter)
        assert axis.get_major_formatter().fmt == "%Y"

    def test_the_title_carries_the_exploratory_label(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Exploratory: the Kalman filter hedge on Chan's own EWA and EWC closes"
        )

    def test_the_note_names_the_file_the_constants_and_the_look_ahead(self, figure) -> None:
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Algorithmic Trading, locations 1633 to 1726, 2006-04-26 to 2012-04-09, 1,500 "
            "trading days, as KF_beta_EWA_EWC.m runs them.\nPrices from inputData_ETF.mat, "
            "saved 2012-04-10. delta 0.0001 and Ve 0.001 are Chan's, and every figure is "
            "in-sample."
        ], SPEC

    def test_no_label_is_parsed_as_math(self, figure) -> None:
        for ax in figure.axes:
            for text in [*ax.texts, ax.title, ax._left_title]:
                assert text.get_parse_math() is False
        for text in figure.texts:
            assert text.get_parse_math() is False


class TestTheSlope:
    """Figure 3.5, the slope after each day's update."""

    def test_the_line_is_the_slope_on_all_1500_rows(self, axes, result) -> None:
        line = _by_gid(axes["slope"].lines)["slope"]
        assert list(line.get_xdata()) == list(result.filter.days), SPEC
        np.testing.assert_array_equal(line.get_ydata(), result.filter.slope)

    def test_a_dashed_line_marks_1(self, axes) -> None:
        one = _by_gid(axes["slope"].lines)["one"]
        assert list(one.get_ydata()) == [1, 1]
        assert one.get_linestyle() == "--"

    def test_the_zero_start_is_marked_on_the_files_first_day(self, axes, result) -> None:
        start = _by_gid(axes["slope"].lines)["start"]
        assert list(start.get_xdata()) == [result.filter.days[0]]
        assert list(start.get_ydata()) == [0.0], SPEC
        label = _by_gid(axes["slope"].texts)["start-label"]
        assert label.get_text() == "0 on 2006-04-26, where the filter starts", SPEC
        assert date2num(label.xy[0]) == date2num(result.filter.days[0])
        assert label.xy[1] == 0.0

    def test_the_line_is_ink_and_the_start_is_red(self, axes) -> None:
        """No legend names them, so the colour is the claim."""
        lines = _by_gid(axes["slope"].lines)
        assert (lines["slope"].get_color(), lines["start"].get_color()) == (INK, LOST)
        assert _by_gid(axes["slope"].texts)["start-label"].get_color() == LOST

    def test_the_heading_quotes_the_median_the_mean_and_the_days_above_1(self, axes) -> None:
        assert _title(axes["slope"]) == (
            "Figure 3.5: the slope, shares of EWA held against one share of EWC, after each "
            "day's update.\nMedian 1.047367, mean 1.089693, above the dashed line at 1 on "
            "894 of 1,500 days."
        ), SPEC


class TestTheIntercept:
    """Figure 3.6, the intercept after each day's update, and its yearly means."""

    def test_the_line_is_the_intercept_on_all_1500_rows(self, axes, result) -> None:
        line = _by_gid(axes["intercept"].lines)["intercept"]
        assert list(line.get_xdata()) == list(result.filter.days), SPEC
        np.testing.assert_array_equal(line.get_ydata(), result.filter.intercept)

    def test_each_years_step_sits_at_its_mean_across_its_days(self, axes, result) -> None:
        lines = _by_gid(axes["intercept"].lines)
        days = result.filter.days
        assert sorted(g for g in lines if g.startswith("year-")) == [
            f"year-{year}" for year in YEARLY
        ]
        for year, mean in YEARLY.items():
            step = lines[f"year-{year}"]
            inside = days[days.year == year]
            assert list(step.get_xdata()) == [inside[0], inside[-1]], year
            y = step.get_ydata()
            assert y[0] == y[1] == pytest.approx(mean, abs=5e-5), (year, SPEC)

    def test_the_peak_is_marked_on_2011_09_08(self, axes) -> None:
        peak = _by_gid(axes["intercept"].lines)["peak"]
        assert list(peak.get_xdata()) == [pd.Timestamp("2011-09-08")], SPEC
        assert peak.get_ydata()[0] == pytest.approx(6.803488, abs=5e-7), SPEC
        label = _by_gid(axes["intercept"].texts)["peak-label"]
        assert label.get_text() == "highest, 6.803488 on 2011-09-08", SPEC
        assert date2num(label.xy[0]) == date2num(pd.Timestamp("2011-09-08"))

    def test_the_steps_are_brass_apart_from_the_ink_line_and_the_peak_is_red(self, axes):
        """No legend tells the steps from the line, so the colour is the claim."""
        lines = _by_gid(axes["intercept"].lines)
        assert lines["intercept"].get_color() == INK
        assert {lines[f"year-{year}"].get_color() for year in YEARLY} == {ACCENT}
        assert lines["peak"].get_color() == LOST

    def test_the_axis_holds_the_line_and_the_label(self, axes, result) -> None:
        low, high = axes["intercept"].get_ylim()
        assert low < result.filter.intercept.min() and high > result.filter.intercept.max()

    def test_the_heading_counts_the_falls_at_two_grains(self, axes) -> None:
        assert _title(axes["intercept"]) == (
            "Figure 3.6: the intercept after each day's update, and each year's mean drawn "
            "flat over its year.\nThe yearly mean falls on 0 of 6 steps. Day to day, the "
            "intercept falls on 513 of 1,499 steps."
        ), SPEC


class TestTheForecastError:
    """Figure 3.7, the forecast error and the band, from row 3."""

    def test_the_error_starts_on_row_3_as_the_script_plots_it(self, axes, result) -> None:
        line = _by_gid(axes["error"].lines)["error"]
        f = result.filter
        assert list(line.get_xdata()) == list(f.days[2:]), SPEC
        np.testing.assert_array_equal(line.get_ydata(), f.error[2:])
        assert str(f.days[2].date()) == "2006-04-28"

    def test_the_band_is_plus_and_minus_sqrt_q_from_row_3(self, axes, result) -> None:
        lines = _by_gid(axes["error"].lines)
        band = np.sqrt(result.filter.variance[2:])
        for gid, sign in (("upper", 1), ("lower", -1)):
            assert list(lines[gid].get_xdata()) == list(result.filter.days[2:]), gid
            np.testing.assert_array_equal(lines[gid].get_ydata(), sign * band)

    def test_the_note_names_rows_1_and_2_off_the_axis(self, axes, sources, result) -> None:
        note = _by_gid(axes["error"].texts)["off-axis"]
        assert note.get_text() == (
            "Off this axis: 2006-04-26 at 22.95, EWC's whole close,\n"
            "and 2006-04-27 at 22.78. The script trades on both."
        ), SPEC
        assert result.filter.error[0] == sources[1]["EWC"].iloc[0], SPEC
        low, high = axes["error"].get_ylim()
        assert high < result.filter.error[1] < result.filter.error[0]
        shown = result.filter.error[2:]
        assert low < shown.min() and high > shown.max()

    def test_the_legend_names_the_error_and_the_band_in_their_colours(self, axes) -> None:
        lines = _by_gid(axes["error"].lines)
        assert _legend(axes["error"]) == [
            "forecast error",
            "plus and minus one forecast standard deviation",
        ]
        handles = axes["error"].get_legend().legend_handles
        assert [h.get_color() for h in handles] == [INK, ACCENT]
        assert (lines["error"].get_color(), lines["upper"].get_color()) == (INK, ACCENT)
        assert lines["lower"].get_color() == ACCENT
        assert _by_gid(axes["error"].texts)["off-axis"].get_color() == LOST

    def test_the_heading_names_where_the_rule_enters_and_exits(self, axes) -> None:
        assert _title(axes["error"]) == (
            "Figure 3.7: the forecast error and the band, from row 3, as the script plots "
            "them.\nA short enters above the upper band and a long below the lower, and each "
            "exits back across its own band."
        )


class TestTheReturn:
    """Figure 3.8, the compounded cumulative return of both runs."""

    def test_each_line_is_its_runs_compounded_return(self, axes, result) -> None:
        lines = _by_gid(axes["returns"].lines)
        for gid, run in (("script", result.trade), ("quiet-start", result.quiet_start)):
            expected = np.cumprod(1 + run.daily) - 1
            assert list(lines[gid].get_xdata()) == list(result.filter.days), gid
            np.testing.assert_array_equal(lines[gid].get_ydata(), expected)
            np.testing.assert_array_equal(cumulative_return(run), expected)

    def test_each_line_ends_where_its_apr_says(self, axes, result) -> None:
        """The APR carried back over 1,500 of 252 days ties each line to its pin."""
        lines = _by_gid(axes["returns"].lines)
        for gid, run, end in (
            ("script", result.trade, 2.999998),
            ("quiet-start", result.quiet_start, 2.970231),
        ):
            last = lines[gid].get_ydata()[-1]
            assert last == pytest.approx((1 + run.apr) ** (1500 / 252) - 1, abs=1e-12), gid
            assert last == pytest.approx(end, abs=5e-7), (gid, SPEC)

    def test_the_quiet_start_is_dashed_green_and_the_script_solid_ink(self, axes) -> None:
        lines = _by_gid(axes["returns"].lines)
        assert (lines["script"].get_linestyle(), lines["script"].get_color()) == ("-", INK)
        assert (lines["quiet-start"].get_linestyle(), lines["quiet-start"].get_color()) == (
            "--",
            GOOD,
        )
        handles = axes["returns"].get_legend().legend_handles
        assert [h.get_color() for h in handles] == [INK, GOOD]
        assert [h.get_linestyle() for h in handles] == ["-", "--"]

    def test_the_legend_sets_each_runs_figures(self, axes) -> None:
        assert _legend(axes["returns"]) == [
            "the script, APR 0.262252, Sharpe ratio 2.361162",
            "no signal on rows 1 and 2, APR 0.260669, Sharpe ratio 2.349460",
        ], SPEC

    def test_the_heading_sets_the_books_figures(self, axes) -> None:
        assert _title(axes["returns"]) == (
            "Figure 3.8: the cumulative return, unlevered and before costs.\n"
            "The book prints 26.2 percent and 2.4, the script's figures rounded."
        )

    def test_the_axis_reads_in_percent_and_marks_zero(self, axes) -> None:
        assert axes["returns"].yaxis.get_major_formatter()(0.5) == "50%"
        assert list(_by_gid(axes["returns"].lines)["zero"].get_ydata()) == [0, 0]


class TestTheReadPath:
    def test_drawing_with_no_sources_reads_the_runs_path(self, monkeypatch, tmp_path, sources):
        asked = []

        def read():
            asked.append(True)
            return sources

        monkeypatch.setattr(figures, "read_sources", read)
        drawn = make_kalman_figure(out=tmp_path / KALMAN_FIGURE)
        assert asked == [True]
        slope = _by_gid(drawn.axes[0].lines)["slope"].get_ydata()
        np.testing.assert_array_equal(slope, kalman_hedge(sources[1]).filter.slope)

    def test_sources_handed_in_are_the_sources_drawn(self, tmp_path, sources) -> None:
        """EWC doubled, so a figure that ignored the argument and read the file would fail."""
        members, closes = sources
        doubled = closes.assign(EWC=closes["EWC"] * 2)
        drawn = make_kalman_figure(out=tmp_path / KALMAN_FIGURE, sources=(members, doubled))
        error = _by_gid(drawn.axes[2].lines)["error"].get_ydata()
        np.testing.assert_array_equal(error, kalman_hedge(doubled).filter.error[2:])

    def test_the_guard_runs_on_the_default_path(self, monkeypatch, tmp_path) -> None:
        """The figure reads through ``read_sources``, so a flagged day stops it too."""

        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("inputdata_etf/ewc.csv changes scale on 2009-01-02")

        monkeypatch.setattr(experiment, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(WindowCrossesScaleBreak, match="ewc.csv changes scale"):
            make_kalman_figure(out=tmp_path / KALMAN_FIGURE)

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
            WindowCrossesScaleBreak("inputdata_etf/ewa.csv changes scale on 2008-01-02"),
        ],
    )
    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(figures, "make_kalman_figure", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)

    def test_any_other_error_keeps_its_traceback(self, monkeypatch) -> None:
        def broken(*_a, **_k):
            raise KeyError("Close")

        monkeypatch.setattr(figures, "make_kalman_figure", broken)
        with pytest.raises(KeyError, match="Close"):
            main()

    def test_the_command_writes_the_committed_path(self, monkeypatch, capsys) -> None:
        drawn = []
        monkeypatch.setattr(figures, "make_kalman_figure", lambda **kw: drawn.append(kw))
        main()
        assert drawn == [{}]
        assert f"wrote {FIGURES_DIR / KALMAN_FIGURE}" in capsys.readouterr().out

    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.is_file() and out.stat().st_size > 0


def test_the_committed_figure_exists() -> None:
    assert (FIGURES_DIR / KALMAN_FIGURE).is_file()
