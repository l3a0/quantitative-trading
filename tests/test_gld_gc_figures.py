"""The pins for the figure in the post on long GLD and short gold futures, locations 2718 and 2730.

``tests/test_gld_gc.py`` holds what the run computes. This file holds that the
figure draws those numbers, so a generator that plotted the wrong GC series,
shaded the wrong drawdown or swapped the two financing curves fails even when
the arithmetic is right. Some numbers repeat here on purpose, because a
figure's labels are prose and the suite is the authority for every number
prose quotes. No test compares bytes, for the reason
``tests/test_regime_figure.py`` gives.

The figure reads the vintages and the specification that
``tests/test_gld_gc.py`` states in its module docstring: GC from
``inputdata_gc_1600_20100802/gc.csv``, chan-mat, raw, saved 2012-05-07, GLD
from ``inputdata_etf/gld.csv``, chan-mat, adjusted, saved 2012-04-10, the OHLC
save's GC from ``inputdataohlcdaily_20120507/gc.csv``, chan-mat, adjusted,
saved 2012-05-09, FRED's TB3MS downloaded 2026-09-30, and S, ``GLD_GC.m`` as
shipped, over the 752 days from 2007-08-03 to 2010-08-02.

Exploratory, like everything Entry 38 computes here. The first panel's
curves were measured after the run. The second panel's spreads, largest moves
and counts past 0.02 are Entry 38's row 11, declared before any figure.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from matplotlib.dates import date2num, num2date

from chan import gld_gc as gld_gc_module
from chan import gld_gc_figures as module
from chan.gld_gc import RISK_FREE_RATE, bill_accrual, gld_gc, read_ohlc_gc, read_sources
from chan.gld_gc_figures import (
    CURVES,
    GLD_GC_FIGURE,
    cumulative_return,
    deepest_trough,
    financing_curves,
    longest_stretch,
    main,
    make_gld_gc_figure,
    signed,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, INK, LOST, MUTED
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable
from tests.test_regime_figure import png_size

SPEC = (
    "inputdata_gc_1600_20100802/gc.csv chan-mat raw saved 2012-05-07 against "
    "inputdata_etf/gld.csv chan-mat adjusted saved 2012-04-10, GLD_GC.m as shipped, "
    "752 days from 2007-08-03 to 2010-08-02; bills from FRED TB3MS downloaded 2026-09-30"
)


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def result(sources):
    return gld_gc(sources)


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("gld_gc_figure") / GLD_GC_FIGURE


@pytest.fixture(scope="module")
def figure(out, sources):
    return make_gld_gc_figure(out=out, sources=sources)


@pytest.fixture(scope="module")
def axes(figure):
    financing, ratio = figure.axes
    return {"financing": financing, "ratio": ratio}


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _title(ax) -> str:
    return ax.get_title(loc="left")


def _days(line) -> pd.DatetimeIndex:
    return pd.DatetimeIndex(line.get_xdata())


class TestTheFigure:
    def test_there_are_two_panels(self, figure) -> None:
        assert len(figure.axes) == 2

    def test_the_title_carries_the_label_and_the_note_names_each_vintage(self, figure) -> None:
        assert figure._suptitle.get_text() == "Exploratory: long GLD and short gold futures"
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Algorithmic Trading, locations 2718 and 2730. GC from "
            "inputData_GC_1600_20100802.mat, saved 2012-05-07,\nGLD from inputData_ETF.mat, "
            "saved 2012-04-10, and FRED's TB3MS, downloaded 2026-09-30.\nThe top panel was "
            "measured after the run, on the book's window, and no cost is charged."
        ]

    def test_drawing_with_no_sources_reads_the_committed_vintages(self, tmp_path, result) -> None:
        """``main`` and the committed PNG take this path, so it is drawn here too."""
        drawn = make_gld_gc_figure(out=tmp_path / GLD_GC_FIGURE)
        line = _by_gid(drawn.axes[0].lines)["S"]
        np.testing.assert_array_equal(line.get_ydata(), np.cumprod(1 + result.daily) - 1)


class TestTheReturnBesideItsFinancing:
    """S, bills and the script's 2 percent, each compounded from 0 on 2007-08-03."""

    def test_it_draws_the_three_curves_in_order(self, axes) -> None:
        drawn = [line.get_gid() for line in axes["financing"].lines if line.get_gid() in CURVES]
        assert drawn == ["S", "bills", "2 percent"]

    def test_each_curve_spans_the_752_days_from_0(self, axes, result) -> None:
        for key in CURVES:
            line = _by_gid(axes["financing"].lines)[key]
            assert _days(line).equals(result.days), SPEC
            assert line.get_ydata()[0] == 0.0

    def test_s_is_its_compounded_return(self, axes, result) -> None:
        line = _by_gid(axes["financing"].lines)["S"]
        np.testing.assert_allclose(line.get_ydata(), np.cumprod(1 + result.daily) - 1, rtol=1e-12)

    def test_the_bills_compound_each_month_s_rate_over_252(self, axes, result) -> None:
        line = _by_gid(axes["financing"].lines)["bills"]
        accrual = bill_accrual(result.days).to_numpy()
        np.testing.assert_allclose(line.get_ydata(), np.cumprod(1 + accrual) - 1, rtol=1e-12)

    def test_the_2_percent_line_compounds_the_script_s_rate(self, axes, result) -> None:
        line = _by_gid(axes["financing"].lines)["2 percent"]
        expected = (1 + RISK_FREE_RATE) ** np.arange(len(result.days)) - 1
        np.testing.assert_allclose(line.get_ydata(), expected, rtol=1e-12, atol=1e-15)

    def test_each_curve_ends_where_the_post_says(self, axes) -> None:
        ends = {
            key: f"{_by_gid(axes['financing'].lines)[key].get_ydata()[-1]:.6f}" for key in CURVES
        }
        assert ends == {"S": "0.058033", "bills": "0.031057", "2 percent": "0.061413"}, SPEC

    def test_s_and_the_bills_on_2008_12_31(self, axes) -> None:
        lines = _by_gid(axes["financing"].lines)
        on = {
            key: pd.Series(lines[key].get_ydata(), index=_days(lines[key])).loc["2008-12-31"]
            for key in ("S", "bills")
        }
        assert {key: f"{value:.6f}" for key, value in on.items()} == {
            "S": "0.049260",
            "bills": "0.028733",
        }, SPEC

    def test_the_legend_names_each_curve_and_its_end(self, axes) -> None:
        legend = [t.get_text() for t in axes["financing"].get_legend().get_texts()]
        assert legend == [
            "S, long GLD and short GC, ending at 5.80 percent",
            "three-month bills, each month's TB3MS over 252 a day, ending at 3.11 percent",
            "the script's 2 percent a year, compounded, ending at 6.14 percent",
        ], SPEC

    def test_s_is_drawn_in_ink_over_the_rest(self, axes) -> None:
        lines = _by_gid(axes["financing"].lines)
        assert (lines["S"].get_color(), lines["S"].get_linestyle()) == (INK, "-")
        assert lines["bills"].get_color() == ACCENT
        assert (lines["2 percent"].get_color(), lines["2 percent"].get_linestyle()) == (
            MUTED,
            "--",
        )
        assert lines["S"].get_zorder() > max(lines[k].get_zorder() for k in ("bills", "2 percent"))

    def test_the_91_days_are_shaded(self, axes) -> None:
        (span,) = [p for p in axes["financing"].patches if p.get_gid() == "longest-stretch"]
        left, right = span.get_x(), span.get_x() + span.get_width()
        assert (num2date(left).date().isoformat(), num2date(right).date().isoformat()) == (
            "2009-08-28",
            "2010-01-08",
        ), SPEC
        label = _by_gid(axes["financing"].texts)["longest-stretch-label"]
        assert label.get_text() == (
            "91 days below a high,\n2009-08-28 to 2010-01-08,\nat worst −0.41 percent"
        ), SPEC

    def test_the_trough_is_marked_on_s(self, axes, result) -> None:
        marker = _by_gid(axes["financing"].lines)["trough"]
        assert list(marker.get_xdata()) == [pd.Timestamp("2007-11-12")], SPEC
        on = result.days.get_loc(pd.Timestamp("2007-11-12"))
        assert marker.get_ydata()[0] == (np.cumprod(1 + result.daily) - 1)[on]
        assert marker.get_color() == LOST
        label = _by_gid(axes["financing"].texts)["trough-label"]
        assert label.xy == (pd.Timestamp("2007-11-12"), marker.get_ydata()[0])
        assert label.get_text() == "the deepest drawdown, −0.82 percent, on 2007-11-12", SPEC

    def test_the_axis_spans_the_window_and_reads_a_percentage(self, axes) -> None:
        assert axes["financing"].get_xlim() == (
            date2num(pd.Timestamp("2007-08-03")),
            date2num(pd.Timestamp("2010-08-02")),
        )
        assert axes["financing"].yaxis.get_major_formatter()(0.02) == "2%"

    def test_the_panel_draws_a_zero_line(self, axes) -> None:
        assert list(_by_gid(axes["financing"].lines)["zero"].get_ydata()) == [0, 0]

    def test_the_heading_names_the_window_and_the_last_day_above_2_percent(self, axes) -> None:
        assert _title(axes["financing"]) == (
            "S's cumulative return beside two rates of financing, 2007-08-03 to 2010-08-02.\n"
            "S last stands above the script's 2 percent a year on 2010-05-21, and ends above "
            "the bills."
        ), SPEC


class TestTheDailyChangeInTheRatio:
    """The daily change in log(GC / GLD) on the 16:00 series and on the OHLC save's GC."""

    def test_the_16_00_series_is_drawn_in_ink_over_the_ohlc_save(self, axes) -> None:
        lines = _by_gid(axes["ratio"].lines)
        assert lines["1600"].get_color() == INK
        assert lines["ohlc"].get_color() == MUTED
        assert lines["1600"].get_zorder() > lines["ohlc"].get_zorder()

    def test_each_line_is_751_changes_dated_on_the_later_day(self, axes, sources, result) -> None:
        _, ohlc = read_ohlc_gc()
        for gid, gc in (("1600", sources.gc), ("ohlc", ohlc)):
            line = _by_gid(axes["ratio"].lines)[gid]
            assert _days(line).equals(result.days[1:]), SPEC
            ratio = gc.loc[result.days].to_numpy() / result.gld
            np.testing.assert_allclose(line.get_ydata(), np.diff(np.log(ratio)), rtol=1e-12)

    def test_what_each_line_reaches(self, axes) -> None:
        lines = _by_gid(axes["ratio"].lines)
        reached = {
            gid: (
                f"{np.std(lines[gid].get_ydata()):.6f}",
                f"{lines[gid].get_ydata().max():.6f}",
                f"{lines[gid].get_ydata().min():.6f}",
            )
            for gid in ("1600", "ohlc")
        }
        assert reached == {
            "1600": ("0.000933", "0.007082", "-0.006626"),
            "ohlc": ("0.009243", "0.097332", "-0.075146"),
        }, SPEC

    def test_the_dashed_lines_sit_at_plus_and_minus_0_02(self, axes) -> None:
        lines = _by_gid(axes["ratio"].lines)
        assert list(lines["step-up"].get_ydata()) == [0.02, 0.02]
        assert list(lines["step-down"].get_ydata()) == [-0.02, -0.02]
        assert {lines[g].get_linestyle() for g in ("step-up", "step-down")} == {"--"}

    def test_the_legend_counts_each_series_moves_past_0_02(self, axes) -> None:
        legend = [t.get_text() for t in axes["ratio"].get_legend().get_texts()]
        assert legend == [
            "the OHLC series, shifted at each roll, 20 moves past ±0.02",
            "the 16:00 series the script reads, 0 moves past ±0.02",
        ], SPEC

    def test_the_largest_16_00_move_is_labelled_on_the_trough_day(self, axes) -> None:
        label = _by_gid(axes["ratio"].texts)["largest-label"]
        assert label.xy[0] == pd.Timestamp("2007-11-12")
        assert f"{label.xy[1]:.6f}" == "0.007082", SPEC
        assert label.get_text() == ("the 16:00 series' largest move, 0.007082, on 2007-11-12"), SPEC

    def test_the_heading_names_both_spreads_and_the_ohlc_save_s_largest_move(self, axes) -> None:
        assert _title(axes["ratio"]) == (
            "The daily change in log(GC / GLD) over 751 days on each GC series. Its standard "
            "deviation is 0.000933\non the 16:00 series and 0.009243 on the OHLC series, "
            "whose largest move, 0.097332, falls on 2008-09-18."
        ), SPEC

    def test_the_axis_spans_the_window(self, axes) -> None:
        assert axes["ratio"].get_xlim() == (
            date2num(pd.Timestamp("2007-08-03")),
            date2num(pd.Timestamp("2010-08-02")),
        )


class TestTheHelpers:
    """The figure module's own rules, on series whose answers are worked here."""

    DAYS = pd.bdate_range("2020-01-01", periods=6)

    def test_the_cumulative_return_compounds(self) -> None:
        found = cumulative_return(pd.Series([0.0, 0.1, -0.1], index=self.DAYS[:3]))
        assert found.tolist() == pytest.approx([0.0, 0.1, 1.1 * 0.9 - 1], abs=1e-15)
        assert found.index.equals(self.DAYS[:3])

    def test_the_longest_stretch_and_the_deepest_trough_can_differ(self) -> None:
        """A one-day fall of 5 percent, then a three-day stretch no deeper than 1 percent."""
        cumret = pd.Series([0.0, 0.1, 0.045, 0.1, 0.099, 0.089, 0.095], dtype=float)
        cumret.index = pd.bdate_range("2020-01-01", periods=7)
        first, last = longest_stretch(cumret)
        trough, depth = deepest_trough(cumret)
        assert (first, last) == (cumret.index[4], cumret.index[6])
        assert trough == cumret.index[2]
        assert depth == pytest.approx(1.045 / 1.1 - 1, abs=1e-15)

    def test_the_financing_curves_start_together_at_0(self, result) -> None:
        curves = financing_curves(result)
        assert list(curves) == list(CURVES)
        assert {key: curve.iloc[0] for key, curve in curves.items()} == {
            "S": 0.0,
            "bills": 0.0,
            "2 percent": 0.0,
        }

    def test_signed_prints_a_true_minus_sign(self) -> None:
        assert signed(-0.8246) == "−0.82"
        assert signed(5.8033, 1) == "5.8"


class TestTheFile:
    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.exists() and out.stat().st_size > 0

    def test_the_committed_figure_exists(self) -> None:
        assert (FIGURES_DIR / GLD_GC_FIGURE).is_file()

    def test_a_fresh_draw_has_the_committed_image_dimensions(self, figure, out) -> None:
        assert png_size(out) == png_size(FIGURES_DIR / GLD_GC_FIGURE)

    def test_drawing_to_out_leaves_the_committed_figure_alone(self, tmp_path, sources) -> None:
        committed = FIGURES_DIR / GLD_GC_FIGURE
        before = committed.read_bytes()
        touched = committed.stat().st_mtime_ns
        make_gld_gc_figure(out=tmp_path / GLD_GC_FIGURE, sources=sources)
        assert committed.read_bytes() == before
        # A redraw is deterministic, so a stray write would leave the bytes
        # the same. Only the modification time shows it.
        assert committed.stat().st_mtime_ns == touched

    def test_every_read_goes_through_the_scale_break_guard_once(self, monkeypatch, tmp_path):
        """GC, GLD and the OHLC series, each guarded over the window and read once."""
        seen = []

        def record(legs, *, start, end):
            ((entry, _),) = legs
            seen.append((entry.path, str(start.date()), str(end.date())))

        monkeypatch.setattr(gld_gc_module, "refuse_window_crossing_a_break", record)
        make_gld_gc_figure(out=tmp_path / GLD_GC_FIGURE)
        assert seen == [
            ("inputdata_gc_1600_20100802/gc.csv", "2007-08-03", "2010-08-02"),
            ("inputdata_etf/gld.csv", "2007-08-03", "2010-08-02"),
            ("inputdataohlcdaily_20120507/gc.csv", "2007-08-03", "2010-08-02"),
        ]

    def test_a_flagged_day_stops_the_figure(self, monkeypatch, tmp_path) -> None:
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("inputdataohlcdaily_20120507/gc.csv changes scale")

        monkeypatch.setattr(gld_gc_module, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(WindowCrossesScaleBreak, match="changes scale"):
            make_gld_gc_figure(out=tmp_path / GLD_GC_FIGURE)

    def test_main_lets_any_other_error_through_as_itself(self, monkeypatch) -> None:
        def fail(*_a, **_k):
            raise ValueError("a bug, not a refusal")

        monkeypatch.setattr(module, "make_gld_gc_figure", fail)
        with pytest.raises(ValueError, match="a bug, not a refusal"):
            main()

    def test_a_missing_vintage_reaches_the_operator_as_one_line(
        self, monkeypatch, tmp_path
    ) -> None:
        """No mock: the real read, pointed at an empty directory, refuses the GC file."""
        from chan import paths

        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert isinstance(stopped.value.__cause__, VintageUnavailable)
        assert "inputData_GC_1600_20100802.mat" in str(stopped.value)
        assert "\n" not in str(stopped.value)

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage is lifted from inputData_GC_1600_20100802"),
            WindowCrossesScaleBreak("inputdata_gc_1600_20100802/gc.csv changes scale"),
        ],
    )
    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(module, "make_gld_gc_figure", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)

    def test_main_reports_the_file_it_wrote(self, monkeypatch, capsys) -> None:
        monkeypatch.setattr(module, "make_gld_gc_figure", lambda: None)
        main()
        assert capsys.readouterr().out == f"wrote {FIGURES_DIR / GLD_GC_FIGURE}\n"
