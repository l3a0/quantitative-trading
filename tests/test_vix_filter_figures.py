"""The pins for the figure in the post on the VIX filter, location 3509.

``tests/test_vix_filter.py`` holds what the run computes. This file holds that
the figure draws those numbers, so a generator that plotted the wrong close,
shaded the wrong span or summed the wrong days fails even when the arithmetic
is right. Some numbers repeat here on purpose, because a figure's labels are
prose and the suite is the authority for every number prose quotes. No test
compares bytes, for the reason ``tests/test_regime_figure.py`` gives.

The figure reads the vintages and the specification that
``tests/test_vix_filter.py`` states in its module docstring: ``vix/vix.csv``,
chan-csv, raw, saved 2012-05-09, the 497 stocks saved 2012-04-25, and
``inputdataohlcdaily_20120517/fstx.csv``, chan-mat, adjusted, saved
2012-05-18, with a day kept when ``backshift(1, vix) > 35`` on each rule's
joined calendar.

Exploratory, like everything Entry 47 computes here.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from matplotlib.colors import to_rgba
from matplotlib.dates import YearLocator, date2num

from chan import vix_filter_figures as module
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, INK, LOST, MUTED, RULE
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable
from chan.vix_filter import read_sources, vix_filters
from chan.vix_filter_figures import FIGURE, main, make_vix_filter_figure, vix_window
from tests.test_regime_figure import png_size

SPEC = (
    "vix/vix.csv chan-csv raw saved 2012-05-09, the stock panel saved 2012-04-25, "
    "fstx.csv chan-mat adjusted saved 2012-05-18; backshift(1, vix) > 35 on each joined calendar"
)

day = pd.Timestamp

#: The figure's date axis, FSTX's first joined day to VIX's last close.
FIRST, LAST = day("2004-07-16"), day("2012-05-08")
#: The span that holds every kept day of both rules.
KEPT_FIRST, KEPT_LAST = day("2008-09-18"), day("2011-11-10")


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def result(sources):
    return vix_filters(sources)


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("vix_filter_figure") / FIGURE


@pytest.fixture(scope="module")
def figure(out, sources):
    return make_vix_filter_figure(out=out, sources=sources)


@pytest.fixture(scope="module")
def axes(figure):
    vix, earned = figure.axes
    return {"vix": vix, "earned": earned}


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _title(ax) -> str:
    return ax.get_title(loc="left")


def _line(ax, gid: str) -> tuple[pd.DatetimeIndex, np.ndarray]:
    line = _by_gid(ax.lines)[gid]
    return pd.DatetimeIndex(line.get_xdata()), np.asarray(line.get_ydata(), dtype=float)


def _point(ax, gid: str) -> tuple[pd.Timestamp, float]:
    marker = _by_gid(ax.lines)[gid]
    (x,), (y,) = marker.get_xdata(), marker.get_ydata()
    return pd.Timestamp(x), float(y)


def _labelled_at(ax, gid: str) -> tuple[pd.Timestamp, float]:
    """Where the annotation ``<gid>-label`` points."""
    x, y = _by_gid(ax.texts)[f"{gid}-label"].xy
    return pd.Timestamp(x), float(y)


def _covered(ax, gid: str, days: pd.DatetimeIndex) -> np.ndarray:
    """The days whose date falls inside a span drawn with ``gid``."""
    x = date2num(days)
    covered = np.zeros(len(x), dtype=bool)
    for span in ax.patches:
        if span.get_gid() == gid:
            left = span.get_x()
            covered |= (x >= left) & (x <= left + span.get_width())
    return covered


class TestTheFigure:
    def test_there_are_two_panels_on_one_date_axis(self, axes) -> None:
        assert axes["vix"].get_shared_x_axes().joined(axes["vix"], axes["earned"])
        assert axes["vix"].get_xlim() == (date2num(FIRST), date2num(LAST)), SPEC

    def test_the_title_carries_the_label_and_the_note_names_the_saves(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Exploratory: the VIX filter on buy on gap and on FSTX's opening gap rule"
        )
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Algorithmic Trading, location 3509. VIX saved 2012-05-09, the stocks saved "
            "2012-04-25, FSTX saved 2012-05-18. No cost charged.\nThe FSTX alignment was chosen "
            "after its figures were seen, and every kept day falls from 2008 to 2011."
        ]

    def test_drawing_with_no_sources_reads_the_committed_vintages(self, tmp_path, result) -> None:
        """``main`` and the committed PNG take this path, so it is drawn here too."""
        drawn = make_vix_filter_figure(out=tmp_path / FIGURE)
        line = _by_gid(drawn.axes[1].lines)["buy-on-gap"]
        np.testing.assert_array_equal(line.get_ydata(), result.buy_on_gap.summed)

    def test_the_date_axis_marks_each_year(self, axes) -> None:
        xaxis = axes["earned"].xaxis
        assert isinstance(xaxis.get_major_locator(), YearLocator)
        assert xaxis.get_major_formatter()(date2num(day("2008-06-30"))) == "2008"


class TestTheVixPanel:
    def test_the_line_is_vix_s_close_on_its_own_calendar_over_the_window(
        self, axes, sources
    ) -> None:
        days, y = _line(axes["vix"], "vix")
        assert (len(days), days[0], days[-1]) == (1969, FIRST, LAST), SPEC
        window = sources.vix.loc[FIRST:LAST]
        assert days.equals(window.index)
        np.testing.assert_array_equal(y, window.to_numpy())

    def test_vix_window_runs_from_fstx_s_first_joined_day_to_its_last(
        self, result, sources
    ) -> None:
        window = vix_window(result, sources.vix)
        assert (window.index[0], window.index[-1]) == (result.literal.days[0], LAST)

    def test_the_threshold_is_a_dashed_line_at_35_in_the_loss_colour(self, axes) -> None:
        line = _by_gid(axes["vix"].lines)["threshold"]
        assert list(line.get_ydata()) == [35, 35]
        assert (line.get_linestyle(), line.get_color()) == ("--", LOST)

    def test_every_close_above_35_is_marked_and_no_other(self, axes, sources) -> None:
        days, y = _line(axes["vix"], "above")
        window = sources.vix.loc[FIRST:LAST]
        above = window[window > 35]
        assert len(days) == 190, SPEC
        assert days.equals(above.index)
        np.testing.assert_array_equal(y, above.to_numpy())
        assert _by_gid(axes["vix"].lines)["above"].get_color() == ACCENT

    @pytest.mark.parametrize(
        ("gid", "when", "value", "text"),
        [
            (
                "first",
                "2008-09-17",
                36.22,
                "first above 35 inside the window, 36.22 on 2008-09-17",
            ),
            ("highest", "2008-11-20", 80.86, "highest, 80.86 on 2008-11-20"),
            ("last", "2011-11-09", 36.16, "last above 35, 36.16 on 2011-11-09"),
        ],
    )
    def test_each_labelled_close_is_marked_where_its_label_points(
        self, axes, gid, when, value, text
    ) -> None:
        ax = axes["vix"]
        assert _point(ax, gid) == (day(when), value), SPEC
        assert _labelled_at(ax, gid) == _point(ax, gid)
        label = _by_gid(ax.texts)[f"{gid}-label"]
        assert label.get_text() == text
        assert label.get_color() == ACCENT
        assert _by_gid(ax.lines)[gid].get_color() == ACCENT

    def test_the_labelled_closes_are_the_first_highest_and_last_above_35(
        self, axes, sources
    ) -> None:
        window = sources.vix.loc[FIRST:LAST]
        above = window[window > 35]
        ax = axes["vix"]
        assert _point(ax, "first") == (above.index[0], above.iloc[0])
        assert _point(ax, "highest") == (window.idxmax(), window.max())
        assert _point(ax, "last") == (above.index[-1], above.iloc[-1])

    def test_the_legend_counts_the_closes_above_35_and_their_runs(self, axes) -> None:
        legend = [t.get_text() for t in axes["vix"].get_legend().get_texts()]
        assert legend == [
            "every kept day falls from 2008-09-18 to 2011-11-10",
            "VIX's close",
            "the threshold, 35",
            "a close above 35, on 190 days in 15 runs",
        ], SPEC

    def test_the_heading_says_when_vix_closed_above_35(self, axes) -> None:
        assert _title(axes["vix"]) == (
            "Inside the window, VIX closed above 35 only from 2008 to 2011. A day is kept when "
            "the previous\njoined day closed above the dashed line, so the kept days follow the "
            "marked closes."
        ), SPEC


class TestTheEarnedPanel:
    @pytest.mark.parametrize("gid", ["buy-on-gap", "literal", "momentum"])
    def test_each_curve_is_its_rule_s_returns_summed_over_the_kept_days(
        self, axes, result, gid
    ) -> None:
        filtered = {
            "buy-on-gap": result.buy_on_gap,
            "literal": result.literal,
            "momentum": result.momentum,
        }[gid]
        days, y = _line(axes["earned"], gid)
        assert days.equals(filtered.days)
        kept = np.where(filtered.qualifies, filtered.daily, 0.0)
        np.testing.assert_allclose(y, np.cumsum(kept), rtol=0, atol=1e-15)

    @pytest.mark.parametrize(
        ("gid", "count", "end"),
        [
            ("buy-on-gap", 1500, "0.129625"),
            ("literal", 1945, "0.018889"),
            ("momentum", 1945, "-0.018889"),
        ],
    )
    def test_each_curve_runs_over_its_joined_days_and_ends_at_its_sum(
        self, axes, gid, count, end
    ) -> None:
        days, y = _line(axes["earned"], gid)
        assert len(days) == count, SPEC
        assert f"{y[-1]:.6f}" == end, SPEC

    def test_each_curve_is_flat_outside_the_kept_span(self, axes) -> None:
        for gid in ("buy-on-gap", "literal", "momentum"):
            days, y = _line(axes["earned"], gid)
            assert (y[days < KEPT_FIRST] == 0).all()
            assert (y[days >= KEPT_LAST] == y[-1]).all()

    def test_the_fstx_curves_mirror_each_other(self, axes) -> None:
        _, literal = _line(axes["earned"], "literal")
        _, momentum = _line(axes["earned"], "momentum")
        np.testing.assert_array_equal(momentum, -literal)

    def test_buy_on_gap_s_largest_kept_day_is_marked(self, axes, result) -> None:
        ax = axes["earned"]
        when, value = _point(ax, "best")
        assert when == day("2009-04-21"), SPEC
        long = result.buy_on_gap
        row = long.days.get_loc(when)
        assert value == long.summed[row]
        assert f"{long.summed[row] - long.summed[row - 1]:.6f}" == "0.093601", SPEC
        assert _labelled_at(ax, "best") == (when, value)
        label = _by_gid(ax.texts)["best-label"]
        assert label.get_text() == "2009-04-21 alone adds 0.093601"
        assert label.get_color() == ACCENT

    def test_the_lines_carry_their_colours_and_weights(self, axes) -> None:
        lines = _by_gid(axes["earned"].lines)
        assert (lines["buy-on-gap"].get_color(), lines["buy-on-gap"].get_linestyle()) == (INK, "-")
        assert (lines["literal"].get_color(), lines["literal"].get_linestyle()) == (MUTED, "--")
        assert (lines["momentum"].get_color(), lines["momentum"].get_linestyle()) == (LOST, "-")
        assert lines["buy-on-gap"].get_linewidth() > lines["literal"].get_linewidth()
        assert lines["buy-on-gap"].get_zorder() > lines["literal"].get_zorder()
        assert list(lines["zero"].get_ydata()) == [0, 0]
        assert lines["zero"].get_color() == MUTED

    def test_the_legend_names_each_curve_its_days_and_its_end(self, axes) -> None:
        legend = [t.get_text() for t in axes["earned"].get_legend().get_texts()]
        assert legend == [
            "every kept day falls from 2008-09-18 to 2011-11-10",
            "FSTX, the sign the text describes, 185 kept days, ending at −0.018889",
            "FSTX, the script as written, 185 kept days, ending at 0.018889",
            "buy on gap, 190 kept days, ending at 0.129625",
        ], SPEC

    def test_the_heading_sets_both_rules_beside_the_book(self, axes) -> None:
        assert _title(axes["earned"]) == (
            "What each rule earned on its kept days, summed, and nothing on the others. Buy on "
            "gap's 252 · mean\nis 0.171924 and its Sharpe ratio 1.417425, where the book prints "
            "17.2 percent and 1.4. FSTX's are 0.025730\nand 0.164869, where it prints 2.6 percent "
            "and 0.16. The other sign gives both negated."
        ), SPEC


class TestBothPanels:
    @pytest.mark.parametrize("panel", ["vix", "earned"])
    def test_the_shading_covers_every_kept_day_of_both_rules(self, axes, result, panel) -> None:
        for filtered in (result.buy_on_gap, result.literal):
            covered = _covered(axes[panel], "kept-span", filtered.days)
            assert covered[filtered.qualifies].all()
            inside = filtered.days[covered]
            assert (inside[0], inside[-1]) == (KEPT_FIRST, KEPT_LAST), SPEC

    @pytest.mark.parametrize("panel", ["vix", "earned"])
    def test_the_shading_is_the_light_rule_colour(self, axes, panel) -> None:
        color, alpha = module.KEPT_SHADE
        assert (color, alpha) == (RULE, 0.45)
        spans = [p for p in axes[panel].patches if p.get_gid() == "kept-span"]
        assert len(spans) == 1 and spans[0].get_facecolor() == to_rgba(color, alpha)

    @pytest.mark.parametrize(
        ("panel", "gids"),
        [("vix", ("vix", "above")), ("earned", ("buy-on-gap", "literal", "momentum"))],
    )
    def test_every_curve_fits_inside_its_panel(self, axes, panel, gids) -> None:
        low, high = axes[panel].get_ylim()
        for gid in gids:
            _, y = _line(axes[panel], gid)
            assert low <= y.min() and y.max() <= high

    @pytest.mark.parametrize(("panel", "limits"), [("vix", (0.0, 92.0)), ("earned", (-0.12, 0.3))])
    def test_each_panel_s_vertical_range_is_pinned(self, axes, panel, limits) -> None:
        assert (module.VIX_LIMITS, module.EARNED_LIMITS) == ((0.0, 92.0), (-0.12, 0.3))
        assert axes[panel].get_ylim() == pytest.approx(limits)

    @pytest.mark.parametrize("panel", ["vix", "earned"])
    def test_each_legend_sits_in_the_upper_left(self, axes, panel) -> None:
        # Matplotlib stores "upper left" as location code 2.
        assert axes[panel].get_legend()._loc == 2

    @pytest.mark.parametrize("panel", ["vix", "earned"])
    def test_each_panel_names_its_vertical_axis(self, axes, panel) -> None:
        expected = {"vix": "VIX close", "earned": "daily returns summed"}[panel]
        assert axes[panel].get_ylabel() == expected


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
        make_vix_filter_figure(out=tmp_path / FIGURE, sources=sources)
        assert committed.read_bytes() == before
        # A redraw is deterministic, so a stray write would leave the bytes
        # the same. Only the modification time shows it.
        assert committed.stat().st_mtime_ns == touched

    def test_main_lets_any_other_error_through_as_itself(self, monkeypatch) -> None:
        def fail(*_a, **_k):
            raise ValueError("a bug, not a refusal")

        monkeypatch.setattr(module, "make_vix_filter_figure", fail)
        with pytest.raises(ValueError, match="a bug, not a refusal"):
            main()

    def test_a_missing_vintage_reaches_the_operator_as_one_line(
        self, monkeypatch, tmp_path
    ) -> None:
        """No mock: the real read, pointed at an empty directory, refuses the save."""
        from chan import paths

        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert isinstance(stopped.value.__cause__, VintageUnavailable)
        assert "VIX.csv" in str(stopped.value)
        assert "\n" not in str(stopped.value)

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage is lifted from VIX.csv"),
            WindowCrossesScaleBreak("vix/vix.csv changes scale on 2007-02-27"),
        ],
    )
    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(module, "make_vix_filter_figure", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)

    def test_main_reports_the_file_it_wrote(self, monkeypatch, capsys) -> None:
        monkeypatch.setattr(module, "make_vix_filter_figure", lambda: None)
        main()
        assert capsys.readouterr().out == f"wrote {FIGURES_DIR / FIGURE}\n"
