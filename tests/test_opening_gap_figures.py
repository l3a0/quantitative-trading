"""The pins for the figure in the post on the opening gap strategy, Example 7.1.

``tests/test_opening_gap.py`` holds what the run computes. This file holds
that the figure draws those numbers, so a generator that plotted the wrong
reading, kept the wrong side's days or marked the wrong drawdown fails even
when the arithmetic is right. Some numbers repeat here on purpose, because a
figure's labels are prose and the suite is the authority for every number
prose quotes. No test compares bytes, for the reason
``tests/test_regime_figure.py`` gives.

The figure reads the vintage and the specification that
``tests/test_opening_gap.py`` states in its module docstring:
``data/inputdataohlcdaily_20120517/fstx.csv``, vendor chan-mat, basis
adjusted, saved 2012-05-18, over the 2,000 days from 2004-07-16 to
2012-05-17, both readings of line 23 as ``chan.opening_gap`` transcribes
them.

Exploratory, like everything Entry 40 computes here.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from matplotlib.colors import to_rgba
from matplotlib.dates import YearLocator, date2num

from chan import opening_gap_figures as module
from chan.opening_gap import by_side, opening_gap, read_sources
from chan.opening_gap_figures import (
    FIGURE,
    cumulative_return,
    main,
    make_opening_gap_figure,
    signed,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, INK, LOST, MUTED, RULE
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable
from tests.test_regime_figure import png_size

SPEC = (
    "inputdataohlcdaily_20120517/fstx.csv chan-mat adjusted saved 2012-05-18; "
    "gapFutures_FSTX.m as tests/test_opening_gap.py states it, from 2004-07-16 to 2012-05-17"
)

day = pd.Timestamp


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def result(sources):
    return opening_gap(sources[1])


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("opening_gap_figure") / FIGURE


@pytest.fixture(scope="module")
def figure(out, sources):
    return make_opening_gap_figure(out=out, sources=sources)


@pytest.fixture(scope="module")
def axes(figure):
    readings, sides = figure.axes
    return {"readings": readings, "sides": sides}


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _title(ax) -> str:
    return ax.get_title(loc="left")


def _line(ax, gid: str) -> tuple[pd.DatetimeIndex, np.ndarray]:
    line = _by_gid(ax.lines)[gid]
    return pd.DatetimeIndex(line.get_xdata()), np.asarray(line.get_ydata(), dtype=float)


def _covered(ax, gid: str, days: pd.DatetimeIndex) -> np.ndarray:
    """The days whose date falls inside a span drawn with ``gid``."""
    x = date2num(days)
    covered = np.zeros(len(x), dtype=bool)
    for span in ax.patches:
        if span.get_gid() == gid:
            left = span.get_x()
            covered |= (x >= left) & (x <= left + span.get_width())
    return covered


def _labelled_at(ax, gid: str) -> tuple[pd.Timestamp, float]:
    """Where the annotation ``<gid>-label`` points."""
    x, y = _by_gid(ax.texts)[f"{gid}-label"].xy
    return pd.Timestamp(x), float(y)


def _point(ax, gid: str) -> tuple[pd.Timestamp, float]:
    marker = _by_gid(ax.lines)[gid]
    (x,), (y,) = marker.get_xdata(), marker.get_ydata()
    return pd.Timestamp(x), float(y)


class TestTheFigure:
    def test_there_are_two_panels_on_one_date_axis(self, axes) -> None:
        assert axes["readings"].get_shared_x_axes().joined(axes["readings"], axes["sides"])
        assert axes["readings"].get_xlim() == (
            date2num(day("2004-07-16")),
            date2num(day("2012-05-17")),
        )

    def test_the_title_carries_the_label_and_the_note_names_the_save(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Exploratory: the opening gap strategy on STOXX Europe 50 futures, both signs"
        )
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Algorithmic Trading, Kindle edition, Example 7.1 and p. 229. FSTX from "
            "inputDataOHLCDaily_20120517.mat, saved 2012-05-18.\n2,000 days from 2004-07-16 "
            "to 2012-05-17, each held from the open to the close, with no cost charged."
        ]

    def test_drawing_with_no_sources_reads_the_committed_vintage(self, tmp_path, result) -> None:
        """``main`` and the committed PNG take this path, so it is drawn here too."""
        drawn = make_opening_gap_figure(out=tmp_path / FIGURE)
        line = _by_gid(drawn.axes[0].lines)["literal"]
        np.testing.assert_array_equal(line.get_ydata(), cumulative_return(result.literal))


class TestTheReadings:
    """Figure 7.1, ``cumprod(1+ret)-1`` over the 2,000 days, under both signs of line 23."""

    @pytest.mark.parametrize("gid", ["literal", "momentum"])
    def test_each_line_is_dated_over_the_2000_days(self, axes, result, gid) -> None:
        days, _ = _line(axes["readings"], gid)
        assert (len(days), days[0], days[-1]) == (
            2000,
            day("2004-07-16"),
            day("2012-05-17"),
        ), SPEC
        assert days.equals(result.days)

    @pytest.mark.parametrize("gid", ["literal", "momentum"])
    def test_each_line_is_its_reading_s_compounded_return(self, axes, result, gid) -> None:
        _, y = _line(axes["readings"], gid)
        np.testing.assert_allclose(y, np.cumprod(1 + getattr(result, gid)) - 1, rtol=1e-12)

    def test_the_literal_curve_ends_at_its_highest_first_reached_on_2012_05_07(self, axes) -> None:
        days, y = _line(axes["readings"], "literal")
        assert f"{y[-1]:.6f}" == "1.688951", SPEC
        assert y[-1] == y.max()
        assert days[int(np.argmax(y))] == day("2012-05-07"), SPEC

    def test_the_momentum_curve_ends_at_its_lowest_first_reached_on_2012_05_07(self, axes) -> None:
        days, y = _line(axes["readings"], "momentum")
        assert f"{y[-1]:.6f}" == "-0.651056", SPEC
        assert y[-1] == y.min()
        assert days[int(np.argmin(y))] == day("2012-05-07"), SPEC

    def test_from_the_first_trade_each_curve_keeps_to_its_side_of_zero(self, axes) -> None:
        """From 2004-11-22, the first day holding a position."""
        days, literal = _line(axes["readings"], "literal")
        _, momentum = _line(axes["readings"], "momentum")
        on = days >= day("2004-11-22")
        assert int(on.sum()) == 1909
        assert f"{literal[on].min():.6f}" == "0.002878", SPEC
        assert f"{momentum[on].max():.6f}" == "-0.002878", SPEC
        assert (literal[~on] == 0).all() and (momentum[~on] == 0).all()

    def test_the_literal_line_is_in_ink_and_the_momentum_line_in_the_loss_colour(
        self, axes
    ) -> None:
        lines = _by_gid(axes["readings"].lines)
        assert (lines["literal"].get_color(), lines["literal"].get_linestyle()) == (INK, "-")
        assert (lines["momentum"].get_color(), lines["momentum"].get_linestyle()) == (LOST, "-")
        assert lines["literal"].get_zorder() > lines["momentum"].get_zorder()

    def test_the_drawdown_s_high_and_trough_are_marked(self, axes) -> None:
        high, trough = (
            _point(axes["readings"], "drawdown-high"),
            _point(axes["readings"], "drawdown-trough"),
        )
        assert (high[0], f"{high[1]:.6f}") == (day("2008-07-08"), "0.573901"), SPEC
        assert (trough[0], f"{trough[1]:.6f}") == (day("2008-10-13"), "0.274823"), SPEC
        assert f"{(1 + trough[1]) / (1 + high[1]) - 1:.6f}" == "-0.190023"
        labels = _by_gid(axes["readings"].texts)
        assert labels["drawdown-high-label"].get_text() == "high, 0.573901 on 2008-07-08"
        assert labels["drawdown-trough-label"].get_text() == "trough, 0.274823 on 2008-10-13"
        assert labels["drawdown-high-label"].get_ha() == "right"
        assert labels["drawdown-trough-label"].get_ha() == "left"

    @pytest.mark.parametrize("gid", ["drawdown-high", "drawdown-trough"])
    def test_each_drawdown_label_points_at_its_marker(self, axes, gid) -> None:
        assert _labelled_at(axes["readings"], gid) == _point(axes["readings"], gid)

    def test_the_longest_run_below_a_high_is_marked_at_that_high(self, axes) -> None:
        line = _by_gid(axes["readings"].lines)["longest-drawdown"]
        # The post's alt text says a dotted line marks it.
        assert (line.get_linestyle(), line.get_color()) == (":", ACCENT)
        assert [pd.Timestamp(x) for x in line.get_xdata()] == [
            day("2008-07-15"),
            day("2009-08-31"),
        ], SPEC
        days, literal = _line(axes["readings"], "literal")
        before = literal[days < day("2008-07-15")]
        assert list(line.get_ydata()) == [before[-1]] * 2
        assert before[-1] == literal[days <= day("2009-08-31")].max()
        label = _by_gid(axes["readings"].texts)["longest-drawdown-label"]
        assert label.get_text() == "287 days below this high,\nto 2009-08-31"

    def test_the_longest_run_label_sits_over_the_middle_of_its_line(self, axes) -> None:
        line = _by_gid(axes["readings"].lines)["longest-drawdown"]
        first, last = (pd.Timestamp(x) for x in line.get_xdata())
        assert _labelled_at(axes["readings"], "longest-drawdown") == (
            first + (last - first) / 2,
            float(line.get_ydata()[0]),
        )

    def test_the_legend_names_each_line_and_its_end(self, axes) -> None:
        legend = [t.get_text() for t in axes["readings"].get_legend().get_texts()]
        assert legend == [
            "the first 90 days, no standard deviation and nothing held",
            "the sign the text describes, ending at −65.11 percent",
            "the script as written, ending at 168.90 percent",
        ], SPEC

    def test_the_heading_sets_both_readings_beside_the_book(self, axes) -> None:
        assert _title(axes["readings"]) == (
            "Figure 7.1 redrawn: the script as written earns APR 0.132733 and Sharpe ratio "
            "1.441620,\nwhere the book prints 13 percent and 1.4. The sign the text describes "
            "earns −0.124236 and −1.441620."
        ), SPEC


class TestTheSides:
    """The literal reading's returns kept on one side's days, nothing on the other's."""

    @pytest.mark.parametrize("gid", ["long", "short"])
    def test_each_line_is_its_side_s_compounded_return(self, axes, result, gid) -> None:
        days, y = _line(axes["sides"], gid)
        assert days.equals(result.days)
        held = result.positions == (1 if gid == "long" else -1)
        kept = np.where(held, result.literal, 0.0)
        np.testing.assert_allclose(y, np.cumprod(1 + kept) - 1, rtol=1e-12)
        np.testing.assert_array_equal(by_side(result)[gid].daily, kept)

    def test_the_long_curve_ends_at_its_highest_first_reached_on_2012_05_02(self, axes) -> None:
        days, y = _line(axes["sides"], "long")
        assert f"{y[-1]:.6f}" == "1.084422", SPEC
        assert y[-1] == y.max()
        assert days[int(np.argmax(y))] == day("2012-05-02"), SPEC

    def test_the_short_curve_ends_at_its_highest_after_a_low_in_2009(self, axes) -> None:
        days, y = _line(axes["sides"], "short")
        assert f"{y[-1]:.6f}" == "0.290022", SPEC
        assert y[-1] == y.max()
        assert days[int(np.argmax(y))] == day("2012-05-07"), SPEC
        assert (days[int(np.argmin(y))], f"{y.min():.6f}") == (day("2009-02-20"), "-0.038153")

    def test_the_short_curve_s_high_before_its_low_is_in_july_2008(self, axes) -> None:
        """The post's alt text reads it as about 18 percent."""
        days, y = _line(axes["sides"], "short")
        before = days < day("2009-01-01")
        peak = int(np.argmax(y[before]))
        assert (days[peak], f"{y[peak]:.6f}") == (day("2008-07-08"), "0.176401")

    def test_the_short_curve_s_low_is_marked(self, axes) -> None:
        low = _point(axes["sides"], "short-low")
        assert (low[0], f"{low[1]:.6f}") == (day("2009-02-20"), "-0.038153"), SPEC
        assert _labelled_at(axes["sides"], "short-low") == low
        label = _by_gid(axes["sides"].texts)["short-low-label"]
        assert label.get_text() == "low, −0.038153 on 2009-02-20"

    def test_the_two_sides_multiply_to_the_whole_curve(self, axes) -> None:
        """They hold on different days, so one plus each, multiplied, is one plus the whole."""
        _, long = _line(axes["sides"], "long")
        _, short = _line(axes["sides"], "short")
        _, whole = _line(axes["readings"], "literal")
        np.testing.assert_allclose((1 + long) * (1 + short), 1 + whole, rtol=1e-12)

    def test_the_long_side_is_in_ink_and_the_short_side_muted_and_dashed(self, axes) -> None:
        lines = _by_gid(axes["sides"].lines)
        assert (lines["long"].get_color(), lines["long"].get_linestyle()) == (INK, "-")
        assert (lines["short"].get_color(), lines["short"].get_linestyle()) == (MUTED, "--")
        assert lines["long"].get_zorder() > lines["short"].get_zorder()

    def test_the_legend_names_each_side_its_days_and_its_end(self, axes) -> None:
        legend = [t.get_text() for t in axes["sides"].get_legend().get_texts()]
        assert legend == [
            "the first 90 days, no standard deviation and nothing held",
            "the 191 short days alone, ending at 29.00 percent",
            "the 278 long days alone, ending at 108.44 percent",
        ], SPEC

    def test_the_heading_says_what_each_side_earns(self, axes) -> None:
        assert _title(axes["sides"]) == (
            "The script as written, by side: each side's returns on its own days, and nothing "
            "on the others.\nIts long days earn a fall from the open after an upward jump, and "
            "its short days a rise after a downward one."
        )


class TestBothPanels:
    @pytest.mark.parametrize("panel", ["readings", "sides"])
    def test_the_shading_covers_exactly_the_first_90_days(self, axes, result, panel) -> None:
        covered = _covered(axes[panel], "no-spread", result.days)
        assert int(covered.sum()) == 90
        assert covered[:90].all()
        assert result.days[89] == day("2004-11-18")
        assert np.isnan(result.spread[:90]).all() and not result.positions[:90].any()

    @pytest.mark.parametrize("panel", ["readings", "sides"])
    def test_the_shading_is_the_light_rule_colour(self, axes, panel) -> None:
        color, alpha = module.NO_SPREAD_SHADE
        assert (color, alpha) == (RULE, 0.45)
        spans = [p for p in axes[panel].patches if p.get_gid() == "no-spread"]
        assert len(spans) == 1 and spans[0].get_facecolor() == to_rgba(color, alpha)

    @pytest.mark.parametrize(
        ("panel", "gids"), [("readings", ("literal", "momentum")), ("sides", ("long", "short"))]
    )
    def test_every_curve_fits_inside_its_panel(self, axes, panel, gids) -> None:
        low, high = axes[panel].get_ylim()
        for gid in gids:
            _, y = _line(axes[panel], gid)
            assert low <= y.min() and y.max() <= high

    @pytest.mark.parametrize("panel", ["readings", "sides"])
    def test_each_axis_reads_a_percentage_and_draws_a_zero_line(self, axes, panel) -> None:
        assert axes[panel].yaxis.get_major_formatter()(0.25) == "25%"
        assert list(_by_gid(axes[panel].lines)["zero"].get_ydata()) == [0, 0]
        assert _by_gid(axes[panel].lines)["zero"].get_color() == MUTED

    @pytest.mark.parametrize(
        ("panel", "limits"), [("readings", (-0.85, 1.95)), ("sides", (-0.25, 1.3))]
    )
    def test_each_panel_s_vertical_range_is_pinned(self, axes, panel, limits) -> None:
        assert (module.CURVE_LIMITS, module.SIDE_LIMITS) == ((-0.85, 1.95), (-0.25, 1.3))
        assert axes[panel].get_ylim() == pytest.approx(limits)

    @pytest.mark.parametrize("panel", ["readings", "sides"])
    def test_each_legend_sits_in_the_upper_left(self, axes, panel) -> None:
        # Matplotlib stores "upper left" as location code 2.
        assert axes[panel].get_legend()._loc == 2

    def test_the_date_axis_marks_each_year(self, axes) -> None:
        xaxis = axes["sides"].xaxis
        assert isinstance(xaxis.get_major_locator(), YearLocator)
        assert xaxis.get_major_formatter()(date2num(day("2008-06-30"))) == "2008"

    def test_the_first_panel_is_taller(self, figure) -> None:
        assert tuple(figure.axes[0].get_gridspec().get_height_ratios()) == (1.4, 1)

    def test_the_whole_curve_and_the_long_side_are_drawn_heavier(self, axes) -> None:
        readings, sides = _by_gid(axes["readings"].lines), _by_gid(axes["sides"].lines)
        assert readings["literal"].get_linewidth() == 1.7
        assert sides["long"].get_linewidth() == 1.7
        assert sides["long"].get_linewidth() > sides["short"].get_linewidth()
        assert readings["literal"].get_linewidth() > readings["momentum"].get_linewidth()

    def test_the_markers_are_drawn_in_the_accent(self, axes) -> None:
        for panel, gid in (
            ("readings", "drawdown-high"),
            ("readings", "drawdown-trough"),
            ("sides", "short-low"),
        ):
            assert _by_gid(axes[panel].lines)[gid].get_color() == ACCENT
            assert _by_gid(axes[panel].texts)[f"{gid}-label"].get_color() == ACCENT
        assert _by_gid(axes["readings"].texts)["longest-drawdown-label"].get_color() == ACCENT

    def test_signed_prints_a_true_minus_sign(self) -> None:
        assert signed(-0.038153, 6) == "−0.038153"
        assert signed(168.89507) == "168.90"


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
        make_opening_gap_figure(out=tmp_path / FIGURE, sources=sources)
        assert committed.read_bytes() == before
        # A redraw is deterministic, so a stray write would leave the bytes
        # the same. Only the modification time shows it.
        assert committed.stat().st_mtime_ns == touched

    def test_main_lets_any_other_error_through_as_itself(self, monkeypatch) -> None:
        def fail(*_a, **_k):
            raise ValueError("a bug, not a refusal")

        monkeypatch.setattr(module, "make_opening_gap_figure", fail)
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
        assert "inputDataOHLCDaily_20120517.mat" in str(stopped.value)
        assert "\n" not in str(stopped.value)

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable(
                "no committed vintage is lifted from inputDataOHLCDaily_20120517.mat"
            ),
            WindowCrossesScaleBreak("inputdataohlcdaily_20120517/fstx.csv changes scale"),
        ],
    )
    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(module, "make_opening_gap_figure", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)

    def test_main_reports_the_file_it_wrote(self, monkeypatch, capsys) -> None:
        monkeypatch.setattr(module, "make_opening_gap_figure", lambda: None)
        main()
        assert capsys.readouterr().out == f"wrote {FIGURES_DIR / FIGURE}\n"
