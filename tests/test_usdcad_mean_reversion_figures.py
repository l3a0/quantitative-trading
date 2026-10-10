"""The pins for the figure in the post on mean reversion on USD.CAD, Examples 2.1 to 2.5.

``tests/test_usdcad_mean_reversion.py`` holds what the run computes. This file
holds that the figure draws those numbers, so a generator that plotted the
wrong series, used another lookback, shifted the curve or shaded the wrong
fall fails even when the arithmetic is right. Some numbers repeat here on
purpose, because a figure's labels are prose and the suite is the authority
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
from matplotlib.dates import DateFormatter, YearLocator, date2num, num2date

from chan import paths, usdcad_mean_reversion
from chan import usdcad_mean_reversion_figures as figures
from chan.matlab_helpers import moving_avg
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST
from chan.series import WindowCrossesScaleBreak
from chan.usdcad_mean_reversion import read_sources, stationarity_tests
from chan.usdcad_mean_reversion_figures import (
    USDCAD_FIGURE,
    cumulative_pnl,
    main,
    make_usdcad_figure,
    moving_average,
    signed,
)
from chan.vintage import VintageUnavailable
from tests.test_usdcad_mean_reversion import SPEC

FIRST, LAST = pd.Timestamp("2007-07-23"), pd.Timestamp("2012-03-28")
AVERAGE_STARTS = pd.Timestamp("2007-12-31")
FIRST_POSITION = pd.Timestamp("2008-01-02")
PEAK, TROUGH = pd.Timestamp("2008-07-22"), pd.Timestamp("2008-10-27")


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

    def test_the_command_writes_the_committed_path(self, monkeypatch, capsys) -> None:
        drawn = []
        monkeypatch.setattr(figures, "make_usdcad_figure", lambda **kw: drawn.append(kw))
        main()
        assert drawn == [{}]
        assert f"wrote {FIGURES_DIR / USDCAD_FIGURE}" in capsys.readouterr().out

    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.is_file() and out.stat().st_size > 0


def test_the_committed_figure_exists() -> None:
    assert (FIGURES_DIR / USDCAD_FIGURE).is_file()
