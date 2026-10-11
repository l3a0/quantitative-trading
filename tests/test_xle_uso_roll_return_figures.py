"""The pins for the figure in the post on XLE against USO, location 2734.

``tests/test_xle_uso_roll_return.py`` holds what the run computes. This file
holds that the figure draws those numbers, so a generator that plotted the
wrong series, shaded the wrong view or marked the wrong drawdown fails even
when the arithmetic is right. Some numbers repeat here on purpose, because a
figure's labels are prose and the suite is the authority for every number
prose quotes. No test compares bytes, for the reason
``tests/test_regime_figure.py`` gives.

The figure reads the vintages and the specification that
``tests/test_xle_uso_roll_return.py`` states in its module docstring:
``data/inputdata_etf/`` USO and XLE, vendor chan-mat, basis adjusted, saved
2012-04-10, and ``data/inputdatadaily_cl_20120502/``, vendor chan-mat, basis
raw, saved 2012-05-03, over the 1,498 days from 2006-04-26 to 2012-04-09.

Exploratory, like everything Entry 39 computes here.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from matplotlib.dates import date2num

from chan import xle_uso_roll_return_figures as module
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, INK, MUTED
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable
from chan.xle_uso_roll_return import (
    BACKWARDATION,
    arbitrage,
    fixed_view,
    front_ratio,
    read_sources,
)
from chan.xle_uso_roll_return_figures import (
    FIGURE,
    cumulative_return,
    held_runs,
    main,
    make_xle_uso_roll_return_figure,
    signed,
)
from tests.test_regime_figure import png_size

SPEC = (
    "inputdata_etf/ uso.csv and xle.csv chan-mat adjusted saved 2012-04-10, and "
    "inputdatadaily_cl_20120502/ chan-mat raw saved 2012-05-03; the script's rule as "
    "tests/test_xle_uso_roll_return.py states it, from 2006-04-26 to 2012-04-09"
)

day = pd.Timestamp


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def result(sources):
    _, closes, strip = sources
    return arbitrage(closes, front_ratio(strip.contracts))


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("xle_uso_roll_return_figure") / FIGURE


@pytest.fixture(scope="module")
def figure(out, sources):
    return make_xle_uso_roll_return_figure(out=out, sources=sources)


@pytest.fixture(scope="module")
def axes(figure):
    curve, ratio = figure.axes
    return {"curve": curve, "ratio": ratio}


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _title(ax) -> str:
    return ax.get_title(loc="left")


def _covered(ax, gid: str, days: pd.DatetimeIndex) -> np.ndarray:
    """The days whose date falls inside a span drawn with ``gid``."""
    x = date2num(days)
    covered = np.zeros(len(x), dtype=bool)
    for span in ax.patches:
        if span.get_gid() == gid:
            left = span.get_x()
            covered |= (x >= left) & (x <= left + span.get_width())
    return covered


def _point(ax, gid: str) -> tuple[pd.Timestamp, float]:
    marker = _by_gid(ax.lines)[gid]
    (x,), (y,) = marker.get_xdata(), marker.get_ydata()
    return pd.Timestamp(x), float(y)


class TestTheFigure:
    def test_there_are_two_panels_on_one_date_axis(self, axes) -> None:
        assert axes["curve"].get_shared_x_axes().joined(axes["curve"], axes["ratio"])
        assert axes["curve"].get_xlim() == (
            date2num(day("2006-04-26")),
            date2num(day("2012-04-09")),
        )

    def test_the_title_carries_the_label_and_the_note_names_both_saves(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Exploratory: XLE against USO signed by crude oil's contango"
        )
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Algorithmic Trading, location 2734. USO and XLE from inputData_ETF.mat, saved "
            "2012-04-10, which subtracts dividends in dollars.\nContracts from "
            "inputDataDaily_CL_20120502.mat, saved 2012-05-03. No cost is charged."
        ]

    def test_drawing_with_no_sources_reads_the_committed_vintages(self, tmp_path, result) -> None:
        """``main`` and the committed PNG take this path, so it is drawn here too."""
        drawn = make_xle_uso_roll_return_figure(out=tmp_path / FIGURE)
        line = _by_gid(drawn.axes[0].lines)["trade"]
        np.testing.assert_array_equal(line.get_ydata(), cumulative_return(result.daily))


class TestTheCumulativeReturns:
    """Figure 6.3, ``cumprod(1+ret)-1`` over the 1,498 days, and the fixed view beside it."""

    @pytest.mark.parametrize("gid", ["trade", "fixed"])
    def test_each_line_is_dated_over_the_1498_days(self, axes, result, gid) -> None:
        days = pd.DatetimeIndex(_by_gid(axes["curve"].lines)[gid].get_xdata())
        assert (len(days), str(days[0].date()), str(days[-1].date())) == (
            1498,
            "2006-04-26",
            "2012-04-09",
        ), SPEC
        assert days.equals(result.days)

    def test_the_trade_is_its_compounded_return(self, axes, result) -> None:
        line = _by_gid(axes["curve"].lines)["trade"]
        np.testing.assert_allclose(line.get_ydata(), np.cumprod(1 + result.daily) - 1, rtol=1e-12)

    def test_the_fixed_view_is_its_compounded_return(self, axes, sources, result) -> None:
        line = _by_gid(axes["curve"].lines)["fixed"]
        np.testing.assert_allclose(
            line.get_ydata(), np.cumprod(1 + fixed_view(sources[1], result)) - 1, rtol=1e-12
        )

    def test_each_curve_ends_where_the_post_says(self, axes) -> None:
        ends = {
            g: f"{_by_gid(axes['curve'].lines)[g].get_ydata()[-1]:.6f}" for g in ("trade", "fixed")
        }
        assert ends == {"trade": "1.405296", "fixed": "0.298702"}, SPEC

    def test_the_trade_is_in_ink_and_the_fixed_view_muted_and_dashed(self, axes) -> None:
        lines = _by_gid(axes["curve"].lines)
        assert (lines["trade"].get_color(), lines["trade"].get_linestyle()) == (INK, "-")
        assert (lines["fixed"].get_color(), lines["fixed"].get_linestyle()) == (MUTED, "--")
        assert lines["trade"].get_zorder() > lines["fixed"].get_zorder()

    def test_the_drawdown_s_high_and_trough_are_marked(self, axes) -> None:
        high, trough = (
            _point(axes["curve"], "drawdown-high"),
            _point(axes["curve"], "drawdown-trough"),
        )
        assert (high[0], f"{high[1]:.6f}") == (day("2009-02-18"), "1.272665"), SPEC
        assert (trough[0], f"{trough[1]:.6f}") == (day("2009-06-29"), "0.835584"), SPEC
        assert (1 + trough[1]) / (1 + high[1]) - 1 == pytest.approx(-0.19232087483339455)
        labels = _by_gid(axes["curve"].texts)
        assert labels["drawdown-high-label"].get_text() == "high, 1.272665 on 2009-02-18"
        assert labels["drawdown-trough-label"].get_text() == "trough, 0.835584 on 2009-06-29"

    def test_the_longest_run_below_a_high_is_marked_at_that_high(self, axes) -> None:
        line = _by_gid(axes["curve"].lines)["longest-drawdown"]
        assert [pd.Timestamp(x) for x in line.get_xdata()] == [
            day("2009-02-19"),
            day("2011-01-24"),
        ], SPEC
        assert [f"{y:.6f}" for y in line.get_ydata()] == ["1.272665"] * 2
        label = _by_gid(axes["curve"].texts)["longest-drawdown-label"]
        assert label.get_text() == "487 days below this high, to 2011-01-24"

    def test_the_legend_names_each_line_and_its_end(self, axes) -> None:
        legend = [t.get_text() for t in axes["curve"].get_legend().get_texts()]
        assert legend == [
            "held long USO and short XLE, backwardation",
            "no ratio, nothing held",
            "contango's position on every held day, ending at 29.87 percent",
            "the trade, ending at 140.53 percent",
        ], SPEC

    def test_the_axis_reads_a_percentage_and_draws_a_zero_line(self, axes) -> None:
        assert axes["curve"].yaxis.get_major_formatter()(0.25) == "25%"
        assert list(_by_gid(axes["curve"].lines)["zero"].get_ydata()) == [0, 0]

    def test_the_heading_sets_the_figures_beside_the_book(self, axes) -> None:
        assert _title(axes["curve"]) == (
            "Figure 6.3: the trade's cumulative return, 2006-04-26 to 2012-04-09. APR 0.159102 "
            "and Sharpe ratio 1.046596,\nwhere the book prints 16 percent and about 1. The "
            "deepest drawdown is −0.192321."
        ), SPEC


class TestTheShading:
    @pytest.mark.parametrize("panel", ["curve", "ratio"])
    def test_it_covers_exactly_the_244_days_held_in_backwardation(
        self, axes, result, panel
    ) -> None:
        covered = _covered(axes[panel], "backwardation", result.days)
        held = (result.positions == BACKWARDATION).all(axis=1)
        assert int(covered.sum()) == 244
        np.testing.assert_array_equal(covered, held)

    @pytest.mark.parametrize("panel", ["curve", "ratio"])
    def test_the_first_123_days_are_marked_as_holding_nothing(self, axes, result, panel) -> None:
        covered = _covered(axes[panel], "no-ratio", result.days)
        assert int(covered.sum()) == 123
        assert covered[:123].all()
        assert not result.positions[:123].any()

    def test_nine_backwardation_spans_the_longest_in_2007_and_the_last_in_2011(
        self, axes, result
    ) -> None:
        held = (result.positions == BACKWARDATION).all(axis=1)
        runs = held_runs(result.days, held)
        assert len(runs) == 9
        assert len([p for p in axes["curve"].patches if p.get_gid() == "backwardation"]) == 9
        assert max(runs, key=lambda r: r[2]) == (day("2007-07-13"), day("2007-12-13"), 108), SPEC
        assert runs[-1] == (day("2011-10-24"), day("2011-11-18"), 20), SPEC

    def test_held_runs_reads_each_run_with_its_ends_and_length(self) -> None:
        days = pd.date_range("2020-01-01", periods=6)
        runs = held_runs(days, np.array([True, False, True, True, False, True]))
        assert runs == [
            (days[0], days[0], 1),
            (days[2], days[3], 2),
            (days[5], days[5], 1),
        ]

    def test_held_runs_finds_none_where_nothing_is_held(self) -> None:
        assert held_runs(pd.date_range("2020-01-01", periods=3), np.zeros(3, bool)) == []


class TestTheRatioPanel:
    def test_the_ratio_is_drawn_on_its_1375_days(self, axes, result) -> None:
        line = _by_gid(axes["ratio"].lines)["ratio"]
        days = pd.DatetimeIndex(line.get_xdata())
        assert (len(days), days[0], days[-1]) == (1375, day("2006-10-20"), day("2012-04-09"))
        defined = np.isfinite(result.ratio)
        np.testing.assert_array_equal(line.get_ydata(), result.ratio[defined])

    def test_its_low_and_high_are_marked(self, axes) -> None:
        low, high = _point(axes["ratio"], "ratio-low"), _point(axes["ratio"], "ratio-high")
        assert (low[0], f"{low[1]:.6f}") == (day("2007-09-26"), "0.982067"), SPEC
        assert (high[0], f"{high[1]:.6f}") == (day("2009-02-05"), "1.111489"), SPEC
        labels = _by_gid(axes["ratio"].texts)
        assert labels["ratio-low-label"].get_text() == "low, 0.982067 on 2007-09-26"
        assert labels["ratio-high-label"].get_text() == "high, 1.111489 on 2009-02-05"

    def test_a_line_marks_1_where_the_view_changes(self, axes) -> None:
        assert list(_by_gid(axes["ratio"].lines)["one"].get_ydata()) == [1, 1]

    def test_the_heading_states_the_window_and_the_rule(self, axes) -> None:
        assert _title(axes["ratio"]) == (
            "The signal: the back contract over the front, each contract the front from 40 to "
            "10 rows before its last price.\nAbove 1 is contango, short USO and long XLE. Below "
            "1 is backwardation, long USO and short XLE."
        )

    def test_the_markers_are_drawn_in_the_accent(self, axes) -> None:
        for panel, gid in (
            ("curve", "drawdown-high"),
            ("curve", "drawdown-trough"),
            ("ratio", "ratio-low"),
            ("ratio", "ratio-high"),
        ):
            assert _by_gid(axes[panel].lines)[gid].get_color() == ACCENT

    def test_signed_prints_a_true_minus_sign(self) -> None:
        assert signed(-0.192321, 6) == "−0.192321"
        assert signed(140.5296) == "140.53"


class TestTheFile:
    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.exists() and out.stat().st_size > 0

    def test_the_committed_figure_exists(self) -> None:
        assert (FIGURES_DIR / FIGURE).is_file()

    def test_a_fresh_draw_has_the_committed_image_dimensions(self, figure, out) -> None:
        assert png_size(out) == png_size(FIGURES_DIR / FIGURE)

    def test_drawing_to_out_leaves_the_committed_figure_alone(self, tmp_path, sources) -> None:
        committed = FIGURES_DIR / FIGURE
        before = committed.read_bytes()
        touched = committed.stat().st_mtime_ns
        make_xle_uso_roll_return_figure(out=tmp_path / FIGURE, sources=sources)
        assert committed.read_bytes() == before
        # A redraw is deterministic, so a stray write would leave the bytes
        # the same. Only the modification time shows it.
        assert committed.stat().st_mtime_ns == touched

    def test_main_lets_any_other_error_through_as_itself(self, monkeypatch) -> None:
        def fail(*_a, **_k):
            raise ValueError("a bug, not a refusal")

        monkeypatch.setattr(module, "make_xle_uso_roll_return_figure", fail)
        with pytest.raises(ValueError, match="a bug, not a refusal"):
            main()

    def test_a_missing_vintage_reaches_the_operator_as_one_line(
        self, monkeypatch, tmp_path
    ) -> None:
        """No mock: the real read, pointed at an empty directory, refuses the ETF file."""
        from chan import paths

        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert isinstance(stopped.value.__cause__, VintageUnavailable)
        assert "inputData_ETF.mat" in str(stopped.value)
        assert "\n" not in str(stopped.value)

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage is lifted from inputData_ETF.mat"),
            WindowCrossesScaleBreak("inputdata_etf/xle.csv changes scale"),
        ],
    )
    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(module, "make_xle_uso_roll_return_figure", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)

    def test_main_reports_the_file_it_wrote(self, monkeypatch, capsys) -> None:
        monkeypatch.setattr(module, "make_xle_uso_roll_return_figure", lambda: None)
        main()
        assert capsys.readouterr().out == f"wrote {FIGURES_DIR / FIGURE}\n"
