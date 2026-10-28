"""The pins for the figure in the post on Chan's low-beta rule at leverage a broker would lend.

``tests/test_low_beta_capped.py`` holds what the run computes and what the
write-up measured after it. This file holds that the figure draws those
numbers, so a generator that centred the second curve on the point estimate
rather than on Y, drew the line at Y, or shaded the wrong side of the line
fails even when the arithmetic is right. Some numbers repeat here on purpose,
because a figure's labels are prose and the suite is the authority for every
number prose quotes. No test compares bytes, for the reason
``tests/test_regime_figure.py`` gives.

The figure reads the vintages and the specification that
``tests/test_low_beta_capped.py`` states in its module docstring and carries
through its ``spec``. Every figure drawn is exploratory. The ceilings were
chosen after Entry 45's figures had been seen, and the standard error and the
5 percent line were measured after the run, so they decide nothing.
"""

from __future__ import annotations

from statistics import NormalDist

import numpy as np
import pytest
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.colors import to_rgba
from matplotlib.text import Text

from chan import low_beta_capped_figures as module
from chan.low_beta_capped import assess, five_percent_line, yearly_standard_error
from chan.low_beta_capped_figures import (
    GAP_LIMITS,
    LOW_BETA_CAPPED_FIGURE,
    SHADED,
    main,
    make_low_beta_capped_figure,
    normal_density,
    signed,
)
from chan.low_beta_leverage import build_portfolios, read_sources
from chan.paths import FIGURES_DIR
from chan.regime_figure import GOOD, INK, LOST, MUTED
from chan.vintage import VintageUnavailable
from tests.test_low_beta_capped import AFTER_THE_RUN, spec
from tests.test_regime_figure import png_size

CEILINGS = (2.0, 5.0)


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def portfolios(sources):
    _, closes, _, spy, _, bills = sources
    return build_portfolios(closes, spy, bills)


@pytest.fixture(scope="module")
def results(portfolios) -> dict:
    return {o.capped.ceiling: o.capped for o in assess(portfolios)}


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("low_beta_capped_figure") / LOW_BETA_CAPPED_FIGURE


@pytest.fixture(scope="module")
def figure(out, sources, portfolios):
    return make_low_beta_capped_figure(out=out, portfolios=portfolios, sources=sources)


@pytest.fixture(scope="module")
def renderer(figure):
    """The figure drawn once more on a canvas that can measure text and lay out tick labels."""
    FigureCanvasAgg(figure)
    figure.canvas.draw()
    return figure.canvas.get_renderer()


@pytest.fixture(scope="module")
def axes(figure) -> dict:
    two, five = figure.axes
    return {2.0: two, 5.0: five}


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _title(ax) -> str:
    return ax.get_title(loc="left")


def _shaded(ax):
    (shaded,) = [c for c in ax.collections if c.get_gid() == "shaded"]
    return shaded


def _area(polygon: np.ndarray) -> float:
    """The area a closed polygon encloses, by the shoelace formula."""
    x, y = polygon[:, 0], polygon[:, 1]
    return abs(float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))) / 2


class TestTheFigure:
    def test_there_is_one_panel_per_ceiling(self, figure) -> None:
        assert len(figure.axes) == 2

    def test_the_title_says_exploratory_and_the_note_names_each_vintage(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Exploratory: neither capped gap reaches the line a 5 percent test draws"
        )
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Quantitative Trading, Kindle edition, p. 191, ceilings from pp. 16 and 112. Stocks "
            "from SPX_20071123.mat, saved 2007-11-24, survivors only.\nSPY from spy_chan.csv, "
            "saved 2008-01-29, and FRED's TB3MS, downloaded 2026-09-30. Not a holdout.\nThe "
            "ceilings were chosen after Entry 45's figures were seen, and the standard error "
            "and the 5 percent line were drawn\nafter the run, so nothing here decides anything."
        ], spec(2.0)

    def test_both_panels_share_one_gap_axis(self, axes) -> None:
        """One axis, so the line visibly moves right as the leverage rises."""
        two, five = axes[2.0], axes[5.0]
        assert two.get_shared_x_axes().joined(two, five)
        for ax in (two, five):
            assert ax.get_xlim() == pytest.approx(GAP_LIMITS)

    def test_both_panels_label_their_gap_ticks(self, axes, renderer) -> None:
        for ax in axes.values():
            low, high = ax.get_xlim()
            ticks = [t for t in ax.get_xticklabels() if low <= t.get_position()[0] <= high]
            labels = [t.get_text() for t in ticks if t.get_visible()]
            shown = [x for x in ax.get_xticks() if low <= x <= high]
            assert shown == pytest.approx([round(-0.4 + 0.1 * n, 1) for n in range(13)])
            assert labels[:5] == ["−0.4", "−0.3", "−0.2", "−0.1", "0"]
            assert labels[-1] == "0.8"

    def test_each_panel_names_its_axes(self, axes) -> None:
        assert [ax.get_ylabel() for ax in axes.values()] == ["density", "density"]
        assert axes[2.0].get_xlabel() == ""
        assert axes[5.0].get_xlabel() == (
            "gap in compounded growth a year, capped low fifth less unlevered high fifth"
        )

    def test_density_carries_no_ticks(self, axes) -> None:
        """The height of a density means nothing to the reader, so no tick names one."""
        for ax in axes.values():
            assert list(ax.get_yticks()) == []

    def test_every_series_lies_inside_its_panel(self, axes) -> None:
        drawn = {}
        for ceiling, ax in axes.items():
            (x0, x1), (y0, y1) = ax.get_xlim(), ax.get_ylim()
            for line in ax.lines:
                if line.get_gid() in ("line", "zero"):
                    continue
                x = np.asarray(line.get_xdata(), dtype=float)
                y = np.asarray(line.get_ydata(), dtype=float)
                assert ((x0 <= x) & (x <= x1)).all(), (ceiling, line.get_gid())
                assert ((y0 <= y) & (y <= y1)).all(), (ceiling, line.get_gid())
                drawn.setdefault(ceiling, set()).add(line.get_gid())
        assert drawn == {c: {"null", "alternative", "estimate"} for c in CEILINGS}

    def test_both_curves_fall_near_zero_at_the_axis_ends(self, axes) -> None:
        """Three standard errors either side of 0 and of Y fit, so no curve is cut off."""
        for ceiling, ax in axes.items():
            for gid in ("null", "alternative"):
                line = _by_gid(ax.lines)[gid]
                y = np.asarray(line.get_ydata())
                assert max(y[0], y[-1]) < 0.01 * y.max(), (ceiling, gid)

    def test_drawing_with_nothing_handed_in_reads_and_builds(
        self, monkeypatch, tmp_path, sources, portfolios
    ) -> None:
        """``main`` and the committed PNG take this path, so its wiring is checked here."""
        calls = []

        def read():
            calls.append("read")
            return sources

        def build(closes, spy, bills):
            calls.append("build")
            assert (closes, spy, bills) == (sources[1], sources[3], sources[5])
            return portfolios

        monkeypatch.setattr(module, "read_sources", read)
        monkeypatch.setattr(module, "build_portfolios", build)
        drawn = make_low_beta_capped_figure(out=tmp_path / LOW_BETA_CAPPED_FIGURE)
        assert calls == ["read", "build"]
        marker = _by_gid(drawn.axes[0].lines)["estimate"]
        assert f"{marker.get_xdata()[0]:.4f}" == "0.0934"

    def test_what_is_handed_in_is_drawn_without_reading_or_building(
        self, monkeypatch, tmp_path, sources, portfolios
    ) -> None:
        """A draw handed both inputs uses them rather than reading the vintages again."""

        def refuse(*_a, **_k):
            raise AssertionError("read or built although both were handed in")

        monkeypatch.setattr(module, "read_sources", refuse)
        monkeypatch.setattr(module, "build_portfolios", refuse)
        drawn = make_low_beta_capped_figure(
            out=tmp_path / LOW_BETA_CAPPED_FIGURE, portfolios=portfolios, sources=sources
        )
        assert len(drawn.axes) == 2


def _heading_box(ax, renderer):
    """The left-aligned heading in display pixels. ``ax.title`` is the empty centred one."""
    heading = ax._left_title
    assert heading.get_text() == _title(ax)
    return heading.get_window_extent(renderer)


class TestTheLayout:
    """Each heading and axis label sits wholly below the text above it and above the text below.

    The order is checked rather than only the overlap, because text pushed
    past its neighbour or off the figure overlaps nothing and is still lost.
    """

    def test_the_first_heading_sits_below_the_title(self, figure, axes, renderer) -> None:
        title = figure._suptitle.get_window_extent(renderer)
        assert _heading_box(axes[2.0], renderer).y1 < title.y0

    def test_the_second_heading_sits_below_the_first_panels_tick_labels(
        self, axes, renderer
    ) -> None:
        ticks = axes[2.0].xaxis.get_tightbbox(renderer)
        assert _heading_box(axes[5.0], renderer).y1 < ticks.y0

    def test_the_gap_axis_label_sits_above_the_note(self, figure, axes, renderer) -> None:
        (note,) = [t for t in figure.texts if t is not figure._suptitle]
        label = axes[5.0].xaxis.label.get_window_extent(renderer)
        assert label.y0 > note.get_window_extent(renderer).y1


@pytest.mark.parametrize(
    ("ceiling", "figures"),
    [
        (2.0, {"se": "0.0872", "line": "0.1434", "y": "0.2168", "gap": "0.0934", "t": "1.0715"}),
        (5.0, {"se": "0.1370", "line": "0.2254", "y": "0.3407", "gap": "0.1659", "t": "1.2111"}),
    ],
)
class TestEachPanel:
    """One ceiling's sampling curves, its 5 percent line and its point estimate."""

    def test_the_curve_at_zero_has_the_yearly_standard_error(
        self, axes, results, ceiling, figures
    ) -> None:
        null = _by_gid(axes[ceiling].lines)["null"]
        se = yearly_standard_error(results[ceiling])
        assert f"{se:.4f}" == figures["se"], f"{spec(ceiling)}; {AFTER_THE_RUN}"
        np.testing.assert_allclose(
            null.get_ydata(), normal_density(null.get_xdata(), 0.0, se), rtol=1e-12
        )
        assert null.get_color() == MUTED

    def test_the_second_curve_is_the_same_normal_centred_on_y(
        self, axes, results, ceiling, figures
    ) -> None:
        c = results[ceiling]
        alternative = _by_gid(axes[ceiling].lines)["alternative"]
        x, y = np.asarray(alternative.get_xdata()), np.asarray(alternative.get_ydata())
        assert f"{x[np.argmax(y)]:.2f}" == f"{float(figures['y']):.2f}", spec(ceiling)
        np.testing.assert_allclose(
            y, normal_density(x, c.detectable, yearly_standard_error(c)), rtol=1e-12
        )
        assert alternative.get_color() == INK

    def test_the_line_sits_at_1_645_standard_errors(self, axes, results, ceiling, figures) -> None:
        line = _by_gid(axes[ceiling].lines)["line"]
        at = five_percent_line(results[ceiling])
        assert list(line.get_xdata()) == [at, at]
        assert f"{at:.4f}" == figures["line"], f"{spec(ceiling)}; {AFTER_THE_RUN}"
        assert (line.get_color(), line.get_linestyle()) == (LOST, "--")
        label = _by_gid(axes[ceiling].texts)["line-label"]
        assert label.get_text() == f"5 percent line, {figures['line']}", spec(ceiling)

    def test_four_fifths_of_the_second_curve_is_shaded_past_the_line(
        self, axes, results, ceiling, figures
    ) -> None:
        shaded = _shaded(axes[ceiling])
        (polygon,) = [p.vertices for p in shaded.get_paths()]
        at = five_percent_line(results[ceiling])
        assert polygon[:, 0].min() == pytest.approx(at, abs=1e-12)
        assert polygon[:, 0].max() == pytest.approx(GAP_LIMITS[1])
        assert round(_area(polygon), 3) == SHADED == 0.80, spec(ceiling)
        assert shaded.get_facecolor()[0][:3] == pytest.approx(
            tuple(int(GOOD[i : i + 2], 16) / 255 for i in (1, 3, 5))
        )

    def test_the_baseline_is_the_floor_of_the_panel(self, axes, ceiling, figures) -> None:
        """Both curves and the estimate stand on 0, so 0 is where the panel starts."""
        ax = axes[ceiling]
        assert ax.get_ylim()[0] == 0
        zero = _by_gid(ax.lines)["zero"]
        assert list(zero.get_ydata()) == [0, 0]
        assert zero.get_color() == MUTED

    def test_the_point_estimate_is_marked_on_the_baseline(
        self, axes, results, ceiling, figures
    ) -> None:
        """A marker on the floor would be cut in half by the frame, so it is drawn unclipped."""
        marker = _by_gid(axes[ceiling].lines)["estimate"]
        assert list(marker.get_ydata()) == [0]
        assert marker.get_xdata()[0] == results[ceiling].gap
        assert f"{marker.get_xdata()[0]:.4f}" == figures["gap"], spec(ceiling)
        assert marker.get_color() == LOST
        assert (marker.get_marker(), marker.get_markersize()) == ("D", 8)
        assert marker.get_clip_on() is False
        label = _by_gid(axes[ceiling].texts)["estimate-label"]
        assert label.get_text() == (
            f"point estimate {figures['gap']},\nNewey-West t {figures['t']}"
        ), spec(ceiling)

    def test_y_is_labelled_at_the_second_curves_peak(self, axes, results, ceiling, figures) -> None:
        label = _by_gid(axes[ceiling].texts)["y-label"]
        assert label.xy[0] == results[ceiling].detectable
        assert label.get_text() == (
            f"Y, {figures['y']}, the gap a\n5 percent test finds\nfour times in five"
        ), spec(ceiling)

    def test_the_point_estimate_falls_short_of_the_line(self, results, ceiling, figures) -> None:
        c = results[ceiling]
        assert 0 < c.gap < five_percent_line(c) < c.detectable, spec(ceiling)

    def test_the_legend_names_both_curves_and_the_shading(self, axes, ceiling, figures) -> None:
        legend = [t.get_text() for t in axes[ceiling].get_legend().get_texts()]
        assert legend == [
            "80 percent of that curve, past the line",
            "if the true gap were 0",
            "if the true gap were Y",
        ]


class TestTheHeadings:
    def test_ceiling_2_names_its_constant_leverage(self, axes) -> None:
        assert _title(axes[2.0]) == (
            "Ceiling 2, a constant leverage of 2. Standard error 0.0872 a year.\n"
            "The point estimate, 0.0934, falls short of the 5 percent line at 0.1434."
        ), f"{spec(2.0)}; {AFTER_THE_RUN}"

    def test_ceiling_5_names_its_mean_leverage_and_the_months_it_binds(self, axes) -> None:
        assert _title(axes[5.0]) == (
            "Ceiling 5, a mean leverage of 3.5134, capped in 20 of 83 months. Standard error "
            "0.1370 a year.\nThe point estimate, 0.1659, falls short of the 5 percent line at "
            "0.2254."
        ), f"{spec(5.0)}; {AFTER_THE_RUN}"

    def test_the_line_moves_right_as_the_leverage_rises(self, axes) -> None:
        lines = [_by_gid(axes[c].lines)["line"].get_xdata()[0] for c in CEILINGS]
        assert lines[0] < lines[1]


def _text_boxes(ax, renderer) -> dict:
    """Each label's text alone, in display pixels, without the rule joining it to its point."""
    return {t.get_gid(): Text.get_window_extent(t, renderer) for t in ax.texts}


def _points(line) -> np.ndarray:
    """A line's points in display pixels, with 50 more along each segment between them."""
    path = line.get_transform().transform(line.get_xydata())
    steps = np.linspace(0, 1, 50)[:, None]
    segments = [a + steps * (b - a) for a, b in zip(path[:-1], path[1:], strict=True)]
    return np.concatenate([path, *segments])


class TestTheLabels:
    """Where each label's rule points, and where its text sits."""

    GIDS = {"line-label", "y-label", "estimate-label"}

    def test_every_label_is_listed(self, axes) -> None:
        for ax in axes.values():
            assert {t.get_gid() for t in ax.texts} == self.GIDS

    def test_each_rule_points_at_its_marked_point(self, axes, results) -> None:
        for ceiling, ax in axes.items():
            c = results[ceiling]
            texts = _by_gid(ax.texts)
            alternative = _by_gid(ax.lines)["alternative"]
            assert texts["estimate-label"].xy == (c.gap, 0)
            assert texts["y-label"].xy == (c.detectable, max(alternative.get_ydata()))
            assert texts["line-label"].xy[0] == five_percent_line(c)

    def test_each_label_takes_the_colour_of_what_it_names(self, axes) -> None:
        """The line and the estimate are drawn in LOST, the curve centred on Y in INK."""
        for ceiling, ax in axes.items():
            texts = _by_gid(ax.texts)
            colours = {gid: t.get_color() for gid, t in texts.items()}
            assert colours == {"line-label": LOST, "y-label": INK, "estimate-label": LOST}, ceiling
            rules = {
                gid: texts[gid].arrow_patch.get_edgecolor() for gid in ("y-label", "estimate-label")
            }
            assert rules["y-label"] == pytest.approx(to_rgba(INK)), ceiling
            assert rules["estimate-label"] == pytest.approx(to_rgba(LOST)), ceiling

    def test_the_line_label_sits_just_right_of_its_line(self, axes, results, renderer) -> None:
        for ceiling, ax in axes.items():
            box = _text_boxes(ax, renderer)["line-label"]
            x = ax.transData.transform((five_percent_line(results[ceiling]), 0))[0]
            assert 0 < box.x0 - x < 20, ceiling

    def test_every_label_sits_inside_its_panel(self, axes, renderer) -> None:
        for ceiling, ax in axes.items():
            (x0, x1), (y0, y1) = ax.get_xlim(), ax.get_ylim()
            frame = ax.get_window_extent(renderer)
            for gid, box in _text_boxes(ax, renderer).items():
                x, y = _by_gid(ax.texts)[gid].xyann
                assert x0 <= x <= x1 and y0 <= y <= y1, (ceiling, gid)
                assert frame.x0 <= box.x0 and box.x1 <= frame.x1, (ceiling, gid)
                assert frame.y0 <= box.y0 and box.y1 <= frame.y1, (ceiling, gid)

    def test_no_two_labels_in_a_panel_overlap(self, axes, renderer) -> None:
        for ceiling, ax in axes.items():
            anchors = [t.xyann for t in ax.texts]
            assert len(set(anchors)) == len(anchors), ceiling
            boxes = list(_text_boxes(ax, renderer).items())
            for n, (gid, box) in enumerate(boxes):
                for other, second in boxes[n + 1 :]:
                    assert not box.overlaps(second), (ceiling, gid, other)

    def test_no_label_overlaps_the_legend(self, axes, renderer) -> None:
        for ceiling, ax in axes.items():
            legend = ax.get_legend().get_window_extent(renderer)
            for gid, box in _text_boxes(ax, renderer).items():
                assert not box.overlaps(legend), (ceiling, gid)

    def test_no_label_crosses_a_line(self, axes, renderer) -> None:
        """The label offsets were placed by eye so that no label's text crosses a drawn line."""
        for ceiling, ax in axes.items():
            for gid, box in _text_boxes(ax, renderer).items():
                for line in ax.lines:
                    xy = _points(line)
                    inside = (
                        (box.x0 <= xy[:, 0])
                        & (xy[:, 0] <= box.x1)
                        & (box.y0 <= xy[:, 1])
                        & (xy[:, 1] <= box.y1)
                    )
                    assert not inside.any(), (ceiling, gid, line.get_gid())


class TestTheHelpers:
    def test_signed_prints_a_true_minus_sign(self) -> None:
        assert signed(-0.4, 1) == "−0.4"
        assert signed(0.1659) == "0.1659"

    def test_the_density_is_the_normals(self) -> None:
        x = np.array([-0.3, 0.0, 0.1434, 0.5])
        expected = [NormalDist(0.2168, 0.0872).pdf(v) for v in x]
        np.testing.assert_allclose(normal_density(x, 0.2168, 0.0872), expected, rtol=1e-12)

    def test_y_puts_four_fifths_past_the_line_for_any_standard_error(self) -> None:
        """Y is 1.645 + 0.8416 standard errors, the line 1.645, so the share is the same."""
        for se in (0.01, 0.0872, 0.137, 1.0):
            share = 1 - NormalDist((1.645 + 0.8416) * se, se).cdf(1.645 * se)
            assert round(share, 4) == 0.8


class TestTheFile:
    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.exists() and out.stat().st_size > 0

    def test_the_committed_figure_exists(self) -> None:
        assert (FIGURES_DIR / LOW_BETA_CAPPED_FIGURE).is_file()

    def test_a_fresh_draw_has_the_committed_image_dimensions(self, figure, out) -> None:
        assert png_size(out) == png_size(FIGURES_DIR / LOW_BETA_CAPPED_FIGURE)

    def test_drawing_to_out_leaves_the_committed_figure_alone(
        self, tmp_path, sources, portfolios
    ) -> None:
        committed = FIGURES_DIR / LOW_BETA_CAPPED_FIGURE
        before = committed.read_bytes()
        touched = committed.stat().st_mtime_ns
        make_low_beta_capped_figure(
            out=tmp_path / LOW_BETA_CAPPED_FIGURE, portfolios=portfolios, sources=sources
        )
        assert committed.read_bytes() == before
        # A redraw is deterministic, so a stray write would leave the bytes
        # the same. Only the modification time shows it.
        assert committed.stat().st_mtime_ns == touched

    def test_main_lets_any_other_error_through_as_itself(self, monkeypatch) -> None:
        def fail(*_a, **_k):
            raise ValueError("a bug, not a refusal")

        monkeypatch.setattr(module, "make_low_beta_capped_figure", fail)
        with pytest.raises(ValueError, match="a bug, not a refusal"):
            main()

    def test_a_missing_vintage_reaches_the_operator_as_one_line(
        self, monkeypatch, tmp_path
    ) -> None:
        """No mock: the real read, pointed at an empty directory, refuses the stock file."""
        from chan import paths

        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert isinstance(stopped.value.__cause__, VintageUnavailable)
        assert "SPX_20071123.mat" in str(stopped.value)
        assert "\n" not in str(stopped.value)

    def test_main_reports_the_file_it_wrote(self, monkeypatch, capsys) -> None:
        monkeypatch.setattr(module, "make_low_beta_capped_figure", lambda: None)
        main()
        assert capsys.readouterr().out == f"wrote {FIGURES_DIR / LOW_BETA_CAPPED_FIGURE}\n"
