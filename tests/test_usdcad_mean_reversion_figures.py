"""The pins for the figures in the post on mean reversion on USD.CAD, Examples 2.1 to 2.5.

``tests/test_usdcad_mean_reversion.py`` holds what the run computes. This file
holds that the figure draws those numbers, so a generator that plotted the
wrong series, used another lookback, shifted the curve or shaded the wrong
fall fails even when the arithmetic is right. The classes from ``TestTheFall`` on
hold the second figure, Lesson 4's three panels over the fall, which a figure
that drew the wrong days, marked the wrong close or wrote a number into a
label rather than reading it from the run would fail. Some numbers repeat
here on purpose, because a figure's labels are prose and the suite is the authority
for every number prose quotes. No test compares bytes, for the reason
``tests/test_regime_figure.py`` gives.

The figure reads the vintage and the specification
``tests/test_usdcad_mean_reversion.py`` names as its ``SPEC``, which every
failure message here carries too: ``pythoncodesanddata/inputData_USDCAD.csv``,
vendor ``chan-py``, basis ``raw``, saved 2018-10-13, its 16:59 bar of each day,
and Example 2.5's position over the half-life rounded, 115 days.

Exploratory, like everything Examples 2.1 to 2.5 compute here.
"""

from __future__ import annotations

import shutil

import numpy as np
import pandas as pd
import pytest
from matplotlib.colors import same_color
from matplotlib.dates import DateFormatter, MonthLocator, YearLocator, date2num, num2date

from chan import paths, usdcad_mean_reversion
from chan import usdcad_mean_reversion_figures as figures
from chan.matlab_helpers import moving_avg, moving_std
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.series import WindowCrossesScaleBreak
from chan.usdcad_mean_reversion import market_value, read_sources, stationarity_tests
from chan.usdcad_mean_reversion_figures import (
    FALL_MARGIN,
    USDCAD_FALL_FIGURE,
    USDCAD_FIGURE,
    cumulative_pnl,
    fall_days,
    main,
    make_usdcad_fall_figure,
    make_usdcad_figure,
    moving_average,
    moving_deviation,
    position,
    rung_count,
    signed,
)
from chan.vintage import VintageUnavailable
from tests.test_usdcad_mean_reversion import SPEC

FIRST, LAST = pd.Timestamp("2007-07-23"), pd.Timestamp("2012-03-28")
AVERAGE_STARTS = pd.Timestamp("2007-12-31")
FIRST_POSITION = pd.Timestamp("2008-01-02")
PEAK, TROUGH = pd.Timestamp("2008-07-22"), pd.Timestamp("2008-10-27")
DEEPEST = pd.Timestamp("2008-10-10")
#: The integer part of the fall's largest z-score, 4.1198560837 on 2008-10-10.
RUNGS = 4


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def result(sources):
    return stationarity_tests(*sources)


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("usdcad_figure") / USDCAD_FIGURE


@pytest.fixture(scope="module")
def figure(out, sources):
    return make_usdcad_figure(out=out, sources=sources)


@pytest.fixture(scope="module")
def axes(figure):
    closes, pnl = figure.axes
    return {"closes": closes, "pnl": pnl}


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _title(ax) -> str:
    return ax.get_title(loc="left")


def _days(line) -> list[pd.Timestamp]:
    return [pd.Timestamp(d) for d in line.get_xdata()]


class TestThePanels:
    def test_there_are_two_in_the_order_the_post_reads_them(self, figure, axes) -> None:
        assert len(figure.axes) == 2
        assert _title(axes["closes"]).startswith("The 1,216 closes of USD.CAD")
        assert _title(axes["pnl"]).startswith("The cumulative P&L")

    def test_they_share_the_date_axis_over_the_1216_closes(self, axes, result) -> None:
        days = result.closes.index
        assert len(days) == 1216, SPEC
        assert (days[0], days[-1]) == (FIRST, LAST), SPEC
        limits = {ax.get_xlim() for ax in axes.values()}
        assert limits == {(date2num(FIRST), date2num(LAST))}, SPEC
        assert axes["closes"].get_shared_x_axes().joined(axes["closes"], axes["pnl"])

    def test_a_tick_falls_on_every_year_from_2008_to_2012(self, axes) -> None:
        axis = axes["pnl"].xaxis
        assert isinstance(axis.get_major_locator(), YearLocator)
        assert isinstance(axis.get_major_formatter(), DateFormatter)
        assert axis.get_major_formatter().fmt == "%Y"
        low, high = axes["pnl"].get_xlim()
        shown = [t for t in axis.get_major_locator()() if low <= t <= high]
        assert [num2date(t).year for t in shown] == list(range(2008, 2013)), SPEC
        assert all((num2date(t).month, num2date(t).day) == (1, 1) for t in shown)

    def test_the_title_carries_the_exploratory_label(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Exploratory: linear mean reversion redrawn on Chan's own USD.CAD closes"
        )

    def test_the_note_names_the_file_the_window_and_the_look_ahead(self, figure) -> None:
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Examples 2.1 to 2.5 of Algorithmic Trading, 2007-07-23 to 2012-03-28, the 16:59 "
            "bar of each day.\nCloses from pythoncodesanddata/inputData_USDCAD.csv, saved "
            "2018-10-13.\nThe 115-day lookback comes from the half-life of the same closes "
            "the rule trades, so every figure is in-sample."
        ], SPEC

    def test_no_label_names_a_figure_number_from_the_book(self, figure) -> None:
        """The post's caption cites the book's Figure 2.3, so the image itself cites none."""
        words = [t.get_text() for t in figure.texts]
        for ax in figure.axes:
            words += [ax.get_title(loc="left"), ax.get_title(), *ax.get_legend_handles_labels()[1]]
        assert len(words) == 8
        assert not any("Figure" in w or "figure 2." in w for w in words)

    def test_no_label_is_parsed_as_math(self, figure) -> None:
        """The P&L heading prints an ampersand and the note a path, and neither is a formula."""
        for ax in figure.axes:
            for text in [*ax.texts, ax.title, ax._left_title]:
                assert text.get_parse_math() is False
        for text in figure.texts:
            assert text.get_parse_math() is False


class TestTheCloses:
    def test_the_line_is_the_1216_closes_the_run_read(self, axes, result) -> None:
        line = _by_gid(axes["closes"].lines)["closes"]
        assert _days(line) == list(result.closes.index), SPEC
        assert len(line.get_ydata()) == 1216, SPEC
        np.testing.assert_array_equal(line.get_ydata(), result.closes.to_numpy())

    def test_the_average_is_movingavg_over_the_runs_115_day_lookback(self, axes, result):
        assert result.lookback == 115, SPEC
        line = _by_gid(axes["closes"].lines)["moving-average"]
        assert _days(line) == list(result.closes.index), SPEC
        expected = moving_avg(result.closes.to_numpy(dtype=float), 115)
        np.testing.assert_array_equal(line.get_ydata(), expected)
        np.testing.assert_array_equal(moving_average(result).to_numpy(), expected)

    def test_the_average_is_nan_until_its_window_fills_on_2007_12_31(self, axes, result):
        """Row 114 is the 115th close, the first whose trailing window is full."""
        y = np.asarray(_by_gid(axes["closes"].lines)["moving-average"].get_ydata())
        assert np.isnan(y[:114]).all(), SPEC
        assert np.isfinite(y[114:]).all(), SPEC
        assert result.closes.index[114] == AVERAGE_STARTS, SPEC
        assert y[114] == pytest.approx(1.0087995652, abs=5e-11), SPEC

    def test_the_closes_are_ink_and_the_average_brass(self, axes) -> None:
        lines = _by_gid(axes["closes"].lines)
        assert same_color(lines["closes"].get_color(), INK)
        assert same_color(lines["moving-average"].get_color(), ACCENT)

    def test_the_legend_names_both_lines(self, axes) -> None:
        legend = [t.get_text() for t in axes["closes"].get_legend().get_texts()]
        assert legend == ["close at 16:59", "115-day moving average"]

    def test_the_heading_names_the_lookback_the_rule_and_the_start(self, axes) -> None:
        assert _title(axes["closes"]) == (
            "The 1,216 closes of USD.CAD and their 115-day moving average, the half-life of "
            "115.2 days rounded.\nThe rule sells when the close is above the average and buys "
            "when it is below, sized by the distance in deviations.\nThe average starts on "
            "2007-12-31, once its window has filled."
        ), SPEC


class TestThePnl:
    def test_the_line_is_cumsum_of_the_runs_pnl(self, axes, result) -> None:
        line = _by_gid(axes["pnl"].lines)["pnl"]
        assert _days(line) == list(result.closes.index), SPEC
        expected = result.pnl.cumsum().to_numpy()
        np.testing.assert_array_equal(line.get_ydata(), expected)
        np.testing.assert_array_equal(cumulative_pnl(result).to_numpy(), expected)

    def test_it_is_zero_until_2008_01_02(self, axes, result) -> None:
        line = _by_gid(axes["pnl"].lines)["pnl"]
        days, y = _days(line), np.asarray(line.get_ydata())
        first = days.index(FIRST_POSITION)
        assert (y[:first] == 0).all(), SPEC
        assert y[first] != 0, SPEC
        assert result.first_position == FIRST_POSITION, SPEC

    def test_it_ends_at_0_1141168588(self, axes, result) -> None:
        last = _by_gid(axes["pnl"].lines)["pnl"].get_ydata()[-1]
        assert last == pytest.approx(0.1141168588, abs=5e-11), SPEC
        assert last == pytest.approx(result.total_pnl, abs=1e-12)

    def test_a_line_marks_zero(self, axes) -> None:
        assert list(_by_gid(axes["pnl"].lines)["zero"].get_ydata()) == [0, 0]

    def test_the_shaded_span_runs_from_the_peak_to_the_trough(self, axes, result) -> None:
        band = _by_gid(axes["pnl"].patches)["drawdown"]
        low, high = band.get_x(), band.get_x() + band.get_width()
        assert (low, high) == (date2num(PEAK), date2num(TROUGH)), SPEC
        assert (result.drawdown.peak, result.drawdown.trough) == (PEAK, TROUGH), SPEC
        assert same_color(band.get_facecolor()[:3], LOST)

    def test_the_peak_and_trough_are_marked_on_the_line(self, axes) -> None:
        marks = _by_gid(axes["pnl"].lines)
        for gid, day, value in (
            ("peak", PEAK, 0.1320839920),
            ("trough", TROUGH, -0.5104474067),
        ):
            assert _days(marks[gid]) == [day], (gid, SPEC)
            assert marks[gid].get_ydata()[0] == pytest.approx(value, abs=5e-11), (gid, SPEC)

    def test_the_marks_are_the_lines_highest_and_lowest_points(self, axes) -> None:
        """The deepest fall here starts at the curve's highest point and ends at its lowest,
        which is not true of every drawdown, so it is pinned rather than assumed."""
        lines = _by_gid(axes["pnl"].lines)
        y = np.asarray(lines["pnl"].get_ydata())
        assert lines["peak"].get_ydata()[0] == y.max(), SPEC
        assert lines["trough"].get_ydata()[0] == y.min(), SPEC

    def test_the_shaded_fall_is_the_runs_drawdown(self, axes, result) -> None:
        lines = _by_gid(axes["pnl"].lines)
        fall = lines["peak"].get_ydata()[0] - lines["trough"].get_ydata()[0]
        assert fall == pytest.approx(result.drawdown.depth, abs=1e-12)
        assert fall == pytest.approx(0.6425313986, abs=5e-11), SPEC

    def test_the_curve_is_green(self, axes) -> None:
        assert same_color(_by_gid(axes["pnl"].lines)["pnl"].get_color(), GOOD)

    def test_the_heading_sets_the_start_the_total_and_the_fall(self, axes) -> None:
        assert _title(axes["pnl"]) == (
            "The cumulative P&L, flat until 2008-01-02 and ending at 0.114. Unlevered and "
            "before costs.\nThe shaded fall runs from 0.132 on 2008-07-22 to −0.510 on "
            "2008-10-27, 0.643 deep."
        ), SPEC
        assert axes["pnl"].get_ylabel() == "cumulative P&L, summed"

    def test_signed_prints_a_true_minus_sign(self) -> None:
        assert signed(-0.5104474067) == "−0.510"
        assert signed(0.1141168588) == "0.114"
        assert signed(-0.5104474067, 2) == "−0.51"


class TestTheReadPath:
    def test_drawing_with_no_sources_reads_the_runs_path(self, monkeypatch, tmp_path, sources):
        asked = []

        def read():
            asked.append(True)
            return sources

        monkeypatch.setattr(figures, "read_sources", read)
        drawn = make_usdcad_figure(out=tmp_path / USDCAD_FIGURE)
        assert asked == [True]
        line = _by_gid(drawn.axes[0].lines)["closes"]
        np.testing.assert_array_equal(line.get_ydata(), sources[1].to_numpy())

    def test_sources_handed_in_are_the_sources_drawn(self, tmp_path, sources, result) -> None:
        """The closes raised by 0.1, so a figure that ignored the argument and read the file
        would fail. Doubling them would not do, because the position is in deviations and
        the P&L in returns, and both cancel a scale."""
        entry, closes = sources
        shifted = closes + 0.1
        drawn = make_usdcad_figure(out=tmp_path / USDCAD_FIGURE, sources=(entry, shifted))
        line = _by_gid(drawn.axes[1].lines)["pnl"]
        expected = stationarity_tests(entry, shifted).pnl.cumsum().to_numpy()
        np.testing.assert_array_equal(line.get_ydata(), expected)
        assert not np.array_equal(expected, result.pnl.cumsum().to_numpy())

    def test_the_average_follows_the_runs_lookback_rather_than_115(self, tmp_path, sources) -> None:
        """The first 800 closes have a half-life that rounds to 100 days, so a figure that
        drew a 115-day average, or wrote 115 into its legend, would fail here."""
        entry, closes = sources
        shorter = closes.iloc[:800]
        run = stationarity_tests(entry, shorter)
        assert run.lookback == 100
        drawn = make_usdcad_figure(out=tmp_path / USDCAD_FIGURE, sources=(entry, shorter))
        line = _by_gid(drawn.axes[0].lines)["moving-average"]
        expected = moving_avg(shorter.to_numpy(dtype=float), run.lookback)
        np.testing.assert_array_equal(line.get_ydata(), expected)
        assert int(np.flatnonzero(np.isfinite(line.get_ydata()))[0]) == run.lookback - 1
        assert line.get_label() == "100-day moving average"

    def test_the_guard_runs_on_the_default_path(self, monkeypatch, tmp_path) -> None:
        """The figure reads through ``stationarity_tests``, so a flagged day stops it too."""

        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("inputData_USDCAD.csv changes scale on 2009-01-02")

        monkeypatch.setattr(usdcad_mean_reversion, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(WindowCrossesScaleBreak, match="changes scale on 2009-01-02"):
            make_usdcad_figure(out=tmp_path / USDCAD_FIGURE)

    def test_a_missing_vintage_reaches_the_operator_as_one_line(
        self, monkeypatch, tmp_path
    ) -> None:
        """The manifest is copied and the minute file is not, so the refusal is the one a
        checkout without the file meets, and it names the file."""
        shutil.copy(paths.DATA_DIR / "vintages.jsonl", tmp_path)
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit) as stopped:
            main()
        message = str(stopped.value)
        assert message.startswith("pythoncodesanddata/inputData_USDCAD.csv: ")
        assert "no file is at" in message
        assert "\n" not in message

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage of USDCAD saved 2018-10-13"),
            WindowCrossesScaleBreak("inputData_USDCAD.csv changes scale on 2008-01-02"),
        ],
    )
    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(figures, "make_usdcad_figure", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)

    def test_any_other_error_keeps_its_traceback(self, monkeypatch) -> None:
        def broken(*_a, **_k):
            raise KeyError("Close")

        monkeypatch.setattr(figures, "make_usdcad_figure", broken)
        with pytest.raises(KeyError, match="Close"):
            main()

    def test_the_command_writes_both_committed_paths(self, monkeypatch, capsys) -> None:
        drawn = []
        monkeypatch.setattr(figures, "make_usdcad_figure", lambda **kw: drawn.append(("all", kw)))
        monkeypatch.setattr(
            figures, "make_usdcad_fall_figure", lambda **kw: drawn.append(("fall", kw))
        )
        main()
        assert drawn == [("all", {}), ("fall", {})]
        printed = capsys.readouterr().out
        assert f"wrote {FIGURES_DIR / USDCAD_FIGURE}" in printed
        assert f"wrote {FIGURES_DIR / USDCAD_FALL_FIGURE}" in printed

    def test_a_refusal_in_the_fall_figure_reaches_the_operator_as_one_line(
        self, monkeypatch
    ) -> None:
        refusal = WindowCrossesScaleBreak("inputData_USDCAD.csv changes scale on 2008-10-01")

        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(figures, "make_usdcad_figure", lambda **kw: None)
        monkeypatch.setattr(figures, "make_usdcad_fall_figure", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)

    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.is_file() and out.stat().st_size > 0


def test_the_committed_figure_exists() -> None:
    assert (FIGURES_DIR / USDCAD_FIGURE).is_file()


@pytest.fixture(scope="module")
def fall_out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("usdcad_fall_figure") / USDCAD_FALL_FIGURE


@pytest.fixture(scope="module")
def fall_figure(fall_out, sources):
    return make_usdcad_fall_figure(out=fall_out, sources=sources)


@pytest.fixture(scope="module")
def fall_axes(fall_figure):
    closes, held, pnl = fall_figure.axes
    return {"closes": closes, "position": held, "pnl": pnl}


def _text(ax, gid: str) -> str:
    return _by_gid(ax.texts)[gid].get_text()


def _point(ax, gid: str) -> tuple[pd.Timestamp, float]:
    line = _by_gid(ax.lines)[gid]
    (day,), (value,) = line.get_xdata(), line.get_ydata()
    return pd.Timestamp(day), float(value)


def _anchor(ax, gid: str) -> tuple[pd.Timestamp, float]:
    day, value = _by_gid(ax.texts)[gid].xy
    return pd.Timestamp(day), float(value)


class TestTheFall:
    """Lesson 4's figure, three panels on the 70 closes from the peak to the trough."""

    def test_there_are_three_panels_in_the_order_the_post_reads_them(self, fall_axes) -> None:
        assert list(fall_axes) == ["closes", "position", "pnl"]
        assert _title(fall_axes["closes"]).startswith("USD.CAD rose from 1.00835")
        assert _title(fall_axes["position"]).startswith("The position held at each close")
        assert _title(fall_axes["pnl"]).startswith("The cumulative P&L falls")

    def test_the_days_run_from_the_peak_to_the_trough(self, fall_axes, result) -> None:
        days = fall_days(result)
        assert (days[0], days[-1], len(days)) == (PEAK, TROUGH, 70), SPEC
        for ax, gid in (
            (fall_axes["closes"], "closes"),
            (fall_axes["closes"], "moving-average"),
            (fall_axes["position"], "position"),
            (fall_axes["pnl"], "pnl"),
        ):
            assert _days(_by_gid(ax.lines)[gid]) == list(days), (gid, SPEC)

    def test_the_axis_adds_three_days_either_side_and_is_shared(self, fall_axes) -> None:
        assert FALL_MARGIN == pd.Timedelta(days=3)
        expected = (date2num(PEAK - FALL_MARGIN), date2num(TROUGH + FALL_MARGIN))
        assert {ax.get_xlim() for ax in fall_axes.values()} == {expected}, SPEC
        first = fall_axes["closes"]
        assert all(first.get_shared_x_axes().joined(first, ax) for ax in fall_axes.values())

    def test_a_tick_falls_on_the_first_of_each_month(self, fall_axes) -> None:
        axis = fall_axes["pnl"].xaxis
        assert isinstance(axis.get_major_locator(), MonthLocator)
        assert axis.get_major_formatter().fmt == "%Y-%m-%d"
        low, high = fall_axes["pnl"].get_xlim()
        shown = [num2date(t).date() for t in axis.get_major_locator()() if low <= t <= high]
        assert [str(d) for d in shown] == ["2008-08-01", "2008-09-01", "2008-10-01"], SPEC

    def test_the_guide_crosses_all_three_panels_on_the_day_of_the_largest_short(
        self, fall_axes
    ) -> None:
        for name, ax in fall_axes.items():
            guide = _by_gid(ax.lines)["guide"]
            assert [pd.Timestamp(d) for d in guide.get_xdata()] == [DEEPEST, DEEPEST], name
            assert list(guide.get_ydata()) == [0, 1], name

    def test_the_title_carries_the_exploratory_label(self, fall_figure) -> None:
        assert fall_figure._suptitle.get_text() == (
            "Exploratory: the position the linear rule held through its deepest fall"
        )

    def test_the_note_names_the_file_the_window_and_the_look_ahead(self, fall_figure) -> None:
        notes = [t.get_text() for t in fall_figure.texts if t is not fall_figure._suptitle]
        assert notes == [
            "Example 2.5 of Algorithmic Trading on Chan's own USD.CAD closes, 2008-07-22 to "
            "2008-10-27, the 16:59 bar of each day.\nCloses from "
            "pythoncodesanddata/inputData_USDCAD.csv, saved 2018-10-13.\nThe 115-day lookback "
            "comes from the half-life of the same closes the rule trades, so every figure is "
            "in-sample."
        ], SPEC

    def test_no_label_is_parsed_as_math(self, fall_figure) -> None:
        for ax in fall_figure.axes:
            for text in [*ax.texts, ax.title, ax._left_title]:
                assert text.get_parse_math() is False
        for text in fall_figure.texts:
            assert text.get_parse_math() is False

    def test_it_is_as_wide_as_the_first_figure(self, figure, fall_figure) -> None:
        assert fall_figure.get_figwidth() == figure.get_figwidth() == 10
        assert fall_figure.dpi == figure.dpi == 130

    def test_drawing_writes_the_file_it_is_given(self, fall_figure, fall_out) -> None:
        assert fall_out.is_file() and fall_out.stat().st_size > 0

    def test_the_committed_figure_exists(self) -> None:
        assert (FIGURES_DIR / USDCAD_FALL_FIGURE).is_file()


class TestTheFallCloses:
    def test_the_lines_are_the_runs_closes_and_average_over_the_fall(
        self, fall_axes, result
    ) -> None:
        days = fall_days(result)
        lines = _by_gid(fall_axes["closes"].lines)
        np.testing.assert_array_equal(lines["closes"].get_ydata(), result.closes[days].to_numpy())
        np.testing.assert_array_equal(
            lines["moving-average"].get_ydata(), moving_average(result)[days].to_numpy()
        )
        assert same_color(lines["closes"].get_color(), INK)
        assert same_color(lines["moving-average"].get_color(), ACCENT)

    def test_the_heading_names_the_rise_the_close_on_the_dashed_day_and_the_rungs(
        self, fall_axes
    ) -> None:
        assert _title(fall_axes["closes"]) == (
            "USD.CAD rose from 1.00835 on 2008-07-22 to 1.29485 on 2008-10-27, 28.4 percent.\n"
            "It closed at 1.17325 on 2008-10-10, the vertical line, and rose another 10.4 "
            "percent after it.\nThe dashed rungs sit 1 to 4 moving deviations above the "
            "average, and spread apart as the deviation grows.\nOn 2008-10-10 the close stood "
            "just above the fourth rung. On 2008-10-27 it was higher in price but below that "
            "rung."
        ), SPEC

    def test_the_legend_names_both_lines_and_the_rungs(self, fall_axes) -> None:
        legend = [t.get_text() for t in fall_axes["closes"].get_legend().get_texts()]
        assert legend == [
            "close at 16:59",
            "115-day moving average",
            "average + 1 to 4 moving deviations",
        ]

    def test_the_largest_short_is_not_on_the_day_of_the_widest_gap_in_price(
        self, fall_axes
    ) -> None:
        """What the middle panel's heading says, so the heading cannot silently go false.

        The gap in price is widest on the trough day, 0.2409000000 against
        0.1392452174 on the day of the largest short, and the short there is
        still smaller."""
        lines = _by_gid(fall_axes["closes"].lines)
        days = _days(lines["closes"])
        gap = pd.Series(
            np.asarray(lines["closes"].get_ydata())
            - np.asarray(lines["moving-average"].get_ydata()),
            index=days,
        )
        held = pd.Series(_by_gid(fall_axes["position"].lines)["position"].get_ydata(), index=days)
        assert gap.idxmax() == TROUGH, SPEC
        assert held.idxmin() == DEEPEST, SPEC
        assert gap.idxmax() != held.idxmin(), SPEC
        assert gap[TROUGH] == pytest.approx(0.2409000000, abs=5e-11), SPEC
        assert gap[DEEPEST] == pytest.approx(0.1392452174, abs=5e-11), SPEC


def _rungs(ax) -> dict[int, pd.Series]:
    """Each rung's value on each day it covers, keyed by how many deviations it adds."""
    return {
        int(gid.split("-")[1]): pd.Series(line.get_ydata(), index=_days(line))
        for gid, line in _by_gid(ax.lines).items()
        if gid.startswith("rung-")
    }


def _closes(ax) -> pd.Series:
    line = _by_gid(ax.lines)["closes"]
    return pd.Series(line.get_ydata(), index=_days(line))


class TestTheFallLadder:
    """The ladder of rungs above the average in the top panel.

    The position counts the close's distance from the average in moving
    deviations, and the rungs let the eye count it. On the trough day the
    close stands higher in price than on the day of the largest short and
    still below the fourth rung, because the deviation widened. The average
    and the deviation are ``movingAvg`` and ``movingStd`` over the run's
    115-day lookback on the vintage and specification ``SPEC`` names.
    """

    def test_rung_k_is_movingavg_plus_k_movingstd_on_every_day_of_the_fall(
        self, fall_axes, result
    ) -> None:
        days = fall_days(result)
        y = result.closes.to_numpy(dtype=float)
        average = pd.Series(moving_avg(y, 115), index=result.closes.index)[days]
        deviation = pd.Series(moving_std(y, 115), index=result.closes.index)[days]
        rungs = _rungs(fall_axes["closes"])
        assert sorted(rungs) == list(range(1, RUNGS + 1)), SPEC
        for k, rung in rungs.items():
            assert list(rung.index) == list(days), (k, SPEC)
            np.testing.assert_allclose(rung, average + k * deviation, rtol=0, atol=1e-12)
        np.testing.assert_array_equal(moving_deviation(result)[days].to_numpy(), deviation)

    def test_the_rungs_stand_one_moving_deviation_apart_on_the_two_marked_days(
        self, fall_axes
    ) -> None:
        """The step from the average to the first rung, and from each rung to the next,
        is the moving deviation, the unit the position counts in."""
        ax = fall_axes["closes"]
        line = _by_gid(ax.lines)["moving-average"]
        average = pd.Series(line.get_ydata(), index=_days(line))
        rungs = _rungs(ax)
        for day, deviation in ((DEEPEST, 0.0337985635), (TROUGH, 0.0628484665)):
            levels = [average[day]] + [rungs[k][day] for k in range(1, RUNGS + 1)]
            for k, step in enumerate(np.diff(levels), start=1):
                assert step == pytest.approx(deviation, abs=5e-11), (day, k, SPEC)

    def test_the_deviation_is_wider_on_the_trough_day_than_on_the_day_of_the_largest_short(
        self, fall_axes
    ) -> None:
        """Why the rungs spread apart, as the heading says."""
        first = _rungs(fall_axes["closes"])[1]
        second = _rungs(fall_axes["closes"])[2]
        assert second[TROUGH] - first[TROUGH] > second[DEEPEST] - first[DEEPEST], SPEC

    def test_there_are_as_many_rungs_as_the_integer_part_of_the_largest_z_score(
        self, fall_axes, result
    ) -> None:
        days = fall_days(result)
        z = (result.closes[days] - moving_average(result)[days]) / moving_deviation(result)[days]
        assert z.max() == pytest.approx(4.1198560837, abs=5e-11), SPEC
        assert int(z.max()) == RUNGS == 4, SPEC
        assert rung_count(position(result)[days]) == RUNGS, SPEC
        assert len(_rungs(fall_axes["closes"])) == RUNGS, SPEC

    def test_the_fourth_rung_on_the_two_marked_days(self, fall_axes) -> None:
        fourth = _rungs(fall_axes["closes"])[4]
        assert fourth[DEEPEST] == pytest.approx(1.1691990365, abs=5e-11), SPEC
        assert fourth[TROUGH] == pytest.approx(1.3053438659, abs=5e-11), SPEC

    def test_the_close_clears_the_fourth_rung_on_the_day_of_the_largest_short_alone(
        self, fall_axes
    ) -> None:
        """What the heading's last line says, so it cannot silently go false.

        The close of 1.29485 on 2008-10-27 is higher than the 1.17325 of
        2008-10-10, and still below the fourth rung the earlier close cleared."""
        closes = _closes(fall_axes["closes"])
        fourth = _rungs(fall_axes["closes"])[4]
        assert closes[DEEPEST] > fourth[DEEPEST], SPEC
        assert closes[TROUGH] < fourth[TROUGH], SPEC
        assert closes[TROUGH] > closes[DEEPEST], SPEC
        assert list(closes.index[closes > fourth]) == [DEEPEST], SPEC

    def test_each_rung_is_labelled_at_its_right_end(self, fall_axes) -> None:
        ax = fall_axes["closes"]
        for k, rung in _rungs(ax).items():
            assert _text(ax, f"rung-{k}-label") == f"+{k}"
            assert _anchor(ax, f"rung-{k}-label") == (TROUGH, rung[TROUGH])

    def test_the_rungs_are_thin_muted_dashes_under_the_close(self, fall_axes) -> None:
        lines = _by_gid(fall_axes["closes"].lines)
        for k in range(1, RUNGS + 1):
            rung = lines[f"rung-{k}"]
            assert same_color(rung.get_color(), MUTED)
            assert rung.get_linestyle() == "--"
            assert rung.get_linewidth() < lines["closes"].get_linewidth()
            assert rung.get_zorder() < lines["closes"].get_zorder()


class TestTheFallPosition:
    def test_the_line_is_market_value_on_each_day_of_the_fall(self, fall_axes, result) -> None:
        days = fall_days(result)
        y = market_value(result.closes.to_numpy(dtype=float), 115)
        expected = pd.Series(y, index=result.closes.index)[days].to_numpy()
        line = _by_gid(fall_axes["position"].lines)["position"]
        np.testing.assert_array_equal(line.get_ydata(), expected)
        np.testing.assert_array_equal(position(result)[days].to_numpy(), expected)

    def test_it_is_short_at_every_close_of_the_fall(self, fall_axes) -> None:
        y = np.asarray(_by_gid(fall_axes["position"].lines)["position"].get_ydata())
        assert (y < 0).all(), SPEC

    def test_the_largest_short_is_marked_where_it_is_lowest(self, fall_axes, result) -> None:
        """The lowest point inside the fall is also the run's largest short of all, so the
        label can call it the largest short without saying "inside the fall"."""
        ax = fall_axes["position"]
        assert position(result).idxmin() == DEEPEST, SPEC
        line = _by_gid(ax.lines)["position"]
        y = np.asarray(line.get_ydata())
        day, value = _point(ax, "deepest")
        assert (day, value) == (_days(line)[int(np.argmin(y))], y.min())
        assert day == DEEPEST, SPEC
        assert value == pytest.approx(-4.1198560837, abs=5e-11), SPEC
        assert _anchor(ax, "deepest-label") == (DEEPEST, value)
        assert _text(ax, "deepest-label") == "largest short −4.12, 2008-10-10"

    def test_the_trough_days_position_is_marked(self, fall_axes) -> None:
        ax = fall_axes["position"]
        day, value = _point(ax, "trough-position")
        assert day == TROUGH, SPEC
        assert value == pytest.approx(-3.8330290865, abs=5e-11), SPEC
        assert _anchor(ax, "trough-position-label") == (TROUGH, value)
        assert _text(ax, "trough-position-label") == "−3.83, 2008-10-27"

    def test_a_line_marks_zero(self, fall_axes) -> None:
        assert list(_by_gid(fall_axes["position"].lines)["zero"].get_ydata()) == [0, 0]

    def test_the_heading_says_what_the_position_is(self, fall_axes) -> None:
        assert _title(fall_axes["position"]) == (
            "The position held at each close, minus the close's distance from its average in "
            "moving deviations.\nIt is largest when the close stands furthest above the "
            "average in deviations, not in price.\nFrom 2008-10-10 to 2008-10-27 the gap in "
            "price grew 73 percent and the moving deviation 86 percent."
        ), SPEC
        assert fall_axes["position"].get_ylabel() == "position, minus the z-score"


class TestTheFallPnl:
    def test_the_line_is_cumsum_of_the_runs_pnl_over_the_fall(self, fall_axes, result) -> None:
        days = fall_days(result)
        line = _by_gid(fall_axes["pnl"].lines)["pnl"]
        np.testing.assert_array_equal(line.get_ydata(), result.pnl.cumsum()[days].to_numpy())
        assert same_color(line.get_color(), GOOD)

    def test_the_peak_and_trough_are_marked_and_labelled(self, fall_axes) -> None:
        ax = fall_axes["pnl"]
        for gid, day, value, label in (
            ("peak", PEAK, 0.1320839920, "high 0.1321, 2008-07-22"),
            ("trough", TROUGH, -0.5104474067, "low −0.5104\n2008-10-27"),
        ):
            drawn_day, drawn = _point(ax, gid)
            assert drawn_day == day, (gid, SPEC)
            assert drawn == pytest.approx(value, abs=5e-11), (gid, SPEC)
            assert _anchor(ax, f"{gid}-label") == (day, drawn), gid
            assert _text(ax, f"{gid}-label") == label, gid
        assert same_color(_by_gid(ax.lines)["trough"].get_color(), LOST)

    def test_the_marks_are_the_lines_first_and_last_points(self, fall_axes) -> None:
        ax = fall_axes["pnl"]
        y = _by_gid(ax.lines)["pnl"].get_ydata()
        assert _point(ax, "peak")[1] == y[0] == y.max()
        assert _point(ax, "trough")[1] == y[-1] == y.min()

    def test_the_heading_names_the_depth(self, fall_axes) -> None:
        assert _title(fall_axes["pnl"]) == (
            "The cumulative P&L falls 0.6425 over the same days. Unlevered and before costs.\n"
            "Each day earns the previous close's position times the day's return."
        ), SPEC


@pytest.fixture(scope="module")
def altered(sources):
    """The closes with 2008-10-15 raised by 4 percent."""
    entry, closes = sources
    raised = closes.copy()
    raised[pd.Timestamp("2008-10-15")] *= 1.04
    return entry, raised


@pytest.fixture(scope="module")
def drawn(tmp_path_factory, altered):
    out = tmp_path_factory.mktemp("usdcad_fall_altered") / USDCAD_FALL_FIGURE
    closes, held, pnl = make_usdcad_fall_figure(out=out, sources=altered).axes
    return {"closes": closes, "position": held, "pnl": pnl}


class TestTheFallFollowsTheRun:
    """A run on other closes moves every date and value the figure prints.

    Raising the close of 2008-10-15 by 4 percent moves the half-life to 106
    days, the largest short to that day and every number on the marks, while
    the fall still runs from 2008-07-22 to 2008-10-27. So a figure that wrote
    any of them in, or found the largest short anywhere but in the run, fails.
    """

    def test_the_labels_and_marks_follow_the_altered_run(self, drawn, altered) -> None:
        run = stationarity_tests(*altered)
        days = fall_days(run)
        held = position(run)[days]
        cumulative = run.pnl.cumsum()[days]
        deepest = held.idxmin()
        assert run.lookback == 106
        assert (days[0], days[-1], deepest) == (PEAK, TROUGH, pd.Timestamp("2008-10-15"))

        assert _point(drawn["position"], "deepest") == (deepest, held[deepest])
        assert _point(drawn["position"], "trough-position") == (TROUGH, held[TROUGH])
        assert _text(drawn["position"], "deepest-label") == (
            f"largest short {signed(held[deepest], 2)}, 2008-10-15"
        )
        assert _text(drawn["position"], "trough-position-label") == (
            f"{signed(held[TROUGH], 2)}, 2008-10-27"
        )
        assert _text(drawn["pnl"], "peak-label") == (
            f"high {signed(cumulative[PEAK], 4)}, 2008-07-22"
        )
        assert _text(drawn["pnl"], "trough-label") == (
            f"low {signed(cumulative[TROUGH], 4)}\n2008-10-27"
        )
        for ax in drawn.values():
            guide = _by_gid(ax.lines)["guide"]
            assert [pd.Timestamp(d) for d in guide.get_xdata()] == [deepest, deepest]
        assert "on 2008-10-15, the vertical line" in _title(drawn["closes"])
        assert _by_gid(drawn["closes"].lines)["moving-average"].get_label() == (
            "106-day moving average"
        )
        assert "From 2008-10-15 to 2008-10-27 the gap in price grew" in _title(drawn["position"])

    def test_the_rungs_follow_the_altered_runs_lookback(self, drawn, altered) -> None:
        """The largest z-score moves to 4.7210946 on 2008-10-15, so there are still four
        rungs, now over 106 days. The close stands 0.72 of a deviation past the top one,
        so the heading drops "just"."""
        run = stationarity_tests(*altered)
        days = fall_days(run)
        y = run.closes.to_numpy(dtype=float)
        average = pd.Series(moving_avg(y, 106), index=run.closes.index)[days]
        deviation = pd.Series(moving_std(y, 106), index=run.closes.index)[days]
        rungs = _rungs(drawn["closes"])
        assert sorted(rungs) == [1, 2, 3, 4]
        for k, rung in rungs.items():
            np.testing.assert_allclose(rung, average + k * deviation, rtol=0, atol=1e-12)
        assert -position(run)[days].min() == pytest.approx(4.7210945936, abs=5e-11)
        assert _title(drawn["closes"]).endswith(
            "\nOn 2008-10-15 the close stood above the fourth rung. On 2008-10-27 it was higher "
            "in price but below that rung."
        )

    def test_the_rung_count_follows_the_largest_z_score(self, tmp_path, sources) -> None:
        """Raising 2008-10-15 by 6 percent lifts its z-score to 5.1844936810 and ends the
        fall there, so the ladder has five rungs and no later close to compare."""
        entry, closes = sources
        raised = closes.copy()
        raised[pd.Timestamp("2008-10-15")] *= 1.06
        run = stationarity_tests(entry, raised)
        days = fall_days(run)
        assert (run.lookback, days[-1]) == (98, pd.Timestamp("2008-10-15"))
        assert -position(run)[days].min() == pytest.approx(5.1844936810, abs=5e-11)
        drawn = make_usdcad_fall_figure(
            out=tmp_path / USDCAD_FALL_FIGURE, sources=(entry, raised)
        ).axes[0]
        assert sorted(_rungs(drawn)) == [1, 2, 3, 4, 5]
        assert drawn.get_legend().get_texts()[2].get_text() == (
            "average + 1 to 5 moving deviations"
        )
        assert _title(drawn).endswith(
            "The dashed rungs sit 1 to 5 moving deviations above the average, and spread apart "
            "as the deviation grows.\nOn 2008-10-15 the close stood just above the fifth rung."
        )

    def test_none_of_them_is_the_committed_runs(self, drawn) -> None:
        printed = " ".join(
            [
                _text(drawn["position"], "deepest-label"),
                _text(drawn["position"], "trough-position-label"),
                _text(drawn["pnl"], "peak-label"),
                _text(drawn["pnl"], "trough-label"),
                _title(drawn["closes"]),
                _title(drawn["position"]),
                _title(drawn["pnl"]),
            ]
        )
        for committed in (
            "−4.12",
            "−3.83",
            "0.1321",
            "−0.5104",
            "0.6425",
            "2008-10-10",
            "73 percent",
            "86 percent",
        ):
            assert committed not in printed, committed

    def test_the_window_follows_the_runs_peak(self, tmp_path, sources) -> None:
        """The first 800 closes peak a day later, on 2008-07-23."""
        entry, closes = sources
        shorter = closes.iloc[:800]
        assert stationarity_tests(entry, shorter).drawdown.peak == pd.Timestamp("2008-07-23")
        drawn = make_usdcad_fall_figure(out=tmp_path / USDCAD_FALL_FIGURE, sources=(entry, shorter))
        pnl = drawn.axes[2]
        assert _days(_by_gid(pnl.lines)["pnl"])[0] == pd.Timestamp("2008-07-23")
        assert pnl.get_xlim()[0] == date2num(pd.Timestamp("2008-07-23") - FALL_MARGIN)
        assert _text(pnl, "peak-label").endswith(", 2008-07-23")
