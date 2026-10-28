"""The pins for the figure in the post on Chan's levered low-beta rule, location 4709.

``tests/test_low_beta_leverage.py`` holds what the run computes. This file
holds that the figure draws those numbers, so a generator that plotted the
leverage by formation date rather than by holding month, drew the high fifth's
return against the ruin line or marked the wrong month fails even when the
arithmetic is right. Some numbers repeat here on purpose, because a figure's
labels are prose and the suite is the authority for every number prose
quotes. No test compares bytes, for the reason ``tests/test_regime_figure.py``
gives.

The figure reads the vintages and the specification that
``tests/test_low_beta_leverage.py`` states in its module docstring and carries
as its ``SPEC``. The ruined months carry Entry 45's verdict, registered under
an amendment the owner made after June 2001 was seen. Every path drawn is
exploratory, and the ruin line and the Kelly line were added after the run.
"""

from __future__ import annotations

import dataclasses

import numpy as np
import pandas as pd
import pytest
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.dates import date2num
from matplotlib.text import Text

from chan import low_beta_leverage_figures as module
from chan.low_beta_leverage import (
    build_portfolios,
    kelly,
    read_sources,
    ruin_line,
)
from chan.low_beta_leverage_figures import (
    LOW_BETA_LEVERAGE_FIGURE,
    RETURN_LIMITS,
    main,
    make_low_beta_leverage_figure,
    signed,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import INK, LOST, MUTED
from chan.vintage import VintageUnavailable
from tests.test_low_beta_leverage import SPEC
from tests.test_regime_figure import png_size


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def portfolios(sources):
    _, closes, _, spy, _, bills = sources
    return build_portfolios(closes, spy, bills)


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("low_beta_leverage_figure") / LOW_BETA_LEVERAGE_FIGURE


@pytest.fixture(scope="module")
def figure(out, sources, portfolios):
    return make_low_beta_leverage_figure(out=out, portfolios=portfolios, sources=sources)


@pytest.fixture(scope="module")
def renderer(figure):
    """The figure drawn once more on a canvas that can measure text and lay out tick labels."""
    FigureCanvasAgg(figure)
    figure.canvas.draw()
    return figure.canvas.get_renderer()


@pytest.fixture(scope="module")
def axes(figure):
    beta, leverage, ruin = figure.axes
    return {"beta": beta, "leverage": leverage, "ruin": ruin}


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _title(ax) -> str:
    return ax.get_title(loc="left")


def _months(line) -> pd.DatetimeIndex:
    return pd.DatetimeIndex(line.get_xdata())


def _span(ax) -> tuple:
    return ax.get_xlim()


HOLDING_MONTHS = (date2num(pd.Timestamp("2000-12-29")), date2num(pd.Timestamp("2007-10-31")))


class TestTheFigure:
    def test_there_are_three_panels(self, figure) -> None:
        assert len(figure.axes) == 3

    def test_the_title_carries_both_labels_and_the_note_names_each_vintage(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Registered verdict, exploratory path: Chan's low-beta fifth levered to the high "
            "fifth's beta"
        )
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Quantitative Trading, Kindle edition, pp. 189 and 191. Stocks from SPX_20071123.mat, "
            "saved "
            "2007-11-24, survivors only.\nSPY from spy_chan.csv, saved 2008-01-29, and FRED's "
            "TB3MS, downloaded 2026-09-30. Not a holdout.\nThe ruined months carry the "
            "verdict, registered under an amendment made after June 2001 was seen.\nThe paths "
            "are exploratory, and the ruin and Kelly lines were added after the run."
        ], SPEC

    def test_every_panel_spans_the_83_holding_months(self, axes) -> None:
        for ax in axes.values():
            assert _span(ax) == HOLDING_MONTHS, SPEC

    def test_every_series_but_the_ruin_line_lies_inside_its_panel(self, axes) -> None:
        """A y-limit too tight hides a point the post quotes, such as k's peak of 69.0762.

        The ruin line is meant to leave its panel, so it is the one series
        left out. ``get_yticks`` lists every fixed tick whatever the limits,
        so only the data can show a limit that cuts it off.
        """
        drawn = {}
        for panel, ax in axes.items():
            low, high = ax.get_ylim()
            for line in ax.lines:
                if line.get_gid() == "ruin-line":
                    continue
                y = np.asarray(line.get_ydata(), dtype=float)
                assert ((low <= y) & (y <= high)).all(), (panel, line.get_gid(), y.min(), y.max())
                drawn.setdefault(panel, set()).add(line.get_gid())
        assert drawn == {
            "beta": {"high", "low", "lowest"},
            "leverage": {"kelly", "k", "ruined"},
            "ruin": {"zero", "low", "below"},
        }

    def test_each_panel_names_its_y_axis(self, axes) -> None:
        assert [ax.get_ylabel() for ax in axes.values()] == [
            "mean beta at formation",
            "leverage, log scale",
            "monthly return",
        ]

    def test_drawing_with_nothing_handed_in_reads_and_builds(
        self, monkeypatch, tmp_path, sources, portfolios
    ) -> None:
        """``main`` and the committed PNG take this path, so its wiring is checked here.

        The real read and build take minutes, so both are replaced by the
        module's fixtures, and the test holds that each runs once and that
        the build is handed the read's closes, SPY and bills.
        """
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
        drawn = make_low_beta_leverage_figure(out=tmp_path / LOW_BETA_LEVERAGE_FIGURE)
        assert calls == ["read", "build"]
        line = _by_gid(drawn.axes[1].lines)["k"]
        np.testing.assert_array_equal(line.get_ydata(), portfolios.leverage.to_numpy())


class TestTheBetas:
    """Each fifth's mean beta at formation, drawn at the month it was held."""

    def test_the_low_fifth_is_ink_over_the_high_fifth_muted(self, axes) -> None:
        lines = _by_gid(axes["beta"].lines)
        assert lines["low"].get_color() == INK
        assert lines["high"].get_color() == MUTED
        assert lines["low"].get_zorder() > lines["high"].get_zorder()

    def test_each_line_is_the_groups_mean_beta_by_holding_month(self, axes, portfolios) -> None:
        lines = _by_gid(axes["beta"].lines)
        for gid, series in (("low", portfolios.low_beta), ("high", portfolios.high_beta)):
            assert _months(lines[gid]).equals(pd.DatetimeIndex(portfolios.held_to)), SPEC
            np.testing.assert_array_equal(lines[gid].get_ydata(), series.to_numpy())

    def test_the_lowest_beta_is_marked_at_may_2001(self, axes) -> None:
        """Formed 2001-04-30 and held to 2001-05-31, so it sits at May."""
        marker = _by_gid(axes["beta"].lines)["lowest"]
        assert list(marker.get_xdata()) == [pd.Timestamp("2001-05-31")], SPEC
        assert f"{marker.get_ydata()[0]:.4f}" == "0.0280", SPEC
        assert marker.get_color() == LOST
        label = _by_gid(axes["beta"].texts)["lowest-label"]
        assert label.get_text() == "0.0280, formed 2001-04-30", SPEC

    def test_the_legend_names_both_fifths(self, axes) -> None:
        legend = [t.get_text() for t in axes["beta"].get_legend().get_texts()]
        assert legend == ["highest fifth", "lowest fifth"]

    def test_the_heading_names_both_ranges(self, axes) -> None:
        assert _title(axes["beta"]) == (
            "Each fifth's mean beta at formation, at the month it was held. The low fifth's fell "
            "to 0.0280,\nwhile the high fifth's stayed between 1.4625 and 1.9532."
        ), SPEC


class TestTheLeverage:
    """k by holding month on a log axis, the ruined months and the look-ahead Kelly line."""

    def test_k_is_drawn_by_holding_month_on_a_log_axis(self, axes, portfolios) -> None:
        line = _by_gid(axes["leverage"].lines)["k"]
        assert _months(line).equals(pd.DatetimeIndex(portfolios.held_to)), SPEC
        np.testing.assert_array_equal(line.get_ydata(), portfolios.leverage.to_numpy())
        assert line.get_color() == INK
        assert axes["leverage"].get_yscale() == "log"
        assert list(axes["leverage"].get_yticks()) == [2, 5, 10, 20, 50, 100]

    def test_the_log_axis_labels_its_ticks_as_plain_numbers(self, axes, renderer) -> None:
        """A log axis labels a tick of 10 as a power of ten unless a plain formatter is set."""
        labels = [t.get_text() for t in axes["leverage"].get_yticklabels()]
        assert labels == ["2", "5", "10", "20", "50", "100"]

    def test_the_highest_k_is_labelled_at_may_2001(self, axes) -> None:
        label = _by_gid(axes["leverage"].texts)["highest-label"]
        assert label.xy[0] == pd.Timestamp("2001-05-31"), SPEC
        assert label.get_text() == "highest, 69.0762", SPEC

    def test_the_two_ruined_months_are_marked_with_k_and_the_levered_return(self, axes) -> None:
        marker = _by_gid(axes["leverage"].lines)["ruined"]
        assert list(marker.get_xdata()) == [
            pd.Timestamp("2001-06-29"),
            pd.Timestamp("2001-09-28"),
        ], SPEC
        assert [f"{k:.4f}" for k in marker.get_ydata()] == ["58.0262", "31.5098"], SPEC
        assert marker.get_color() == LOST
        texts = _by_gid(axes["leverage"].texts)
        assert [texts[f"ruined-label-{n}"].get_text() for n in (0, 1)] == [
            "ruined 2001-06-29: k 58.0262,\nlevered return −2.5053",
            "ruined 2001-09-28: k 31.5098,\nlevered return −1.1278",
        ], SPEC

    def test_the_kelly_line_is_dashed_muted_and_labelled_look_ahead(self, axes, portfolios) -> None:
        line = _by_gid(axes["leverage"].lines)["kelly"]
        assert list(line.get_ydata()) == [kelly(portfolios).leverage] * 2
        assert (line.get_color(), line.get_linestyle()) == (MUTED, "--")
        legend = [t.get_text() for t in axes["leverage"].get_legend().get_texts()]
        assert legend == [
            "full-sample Kelly, look-ahead, 9.9884",
            "k, high beta over low",
        ], SPEC

    def test_the_heading_names_the_mean_and_says_the_kelly_line_decides_nothing(self, axes) -> None:
        assert _title(axes["leverage"]) == (
            "k, the leverage that matches the high fifth's beta, mean 7.8414. 2 months lost more\n"
            "than the capital, and the Kelly line, added after the run, looks ahead and decides "
            "nothing."
        ), SPEC


class TestTheRuinLine:
    """The low fifth's monthly return against rf − (1 + rf) / k."""

    def test_the_low_fifths_return_is_drawn_in_ink(self, axes, portfolios) -> None:
        line = _by_gid(axes["ruin"].lines)["low"]
        assert _months(line).equals(pd.DatetimeIndex(portfolios.held_to)), SPEC
        np.testing.assert_array_equal(line.get_ydata(), portfolios.low.to_numpy())
        assert line.get_color() == INK

    def test_the_ruin_line_is_rf_less_one_plus_rf_over_k(self, axes, portfolios) -> None:
        line = _by_gid(axes["ruin"].lines)["ruin-line"]
        rf, k = portfolios.rf.to_numpy(), portfolios.leverage.to_numpy()
        np.testing.assert_allclose(line.get_ydata(), rf - (1 + rf) / k, rtol=1e-12)
        assert (line.get_color(), line.get_linestyle()) == (LOST, "--")

    def test_the_axis_runs_from_minus_0_10_to_0_12(self, axes, portfolios) -> None:
        assert RETURN_LIMITS == (-0.10, 0.12)
        assert RETURN_LIMITS[0] < portfolios.low.min(), SPEC
        assert portfolios.low.max() < RETURN_LIMITS[1], SPEC
        assert axes["ruin"].get_ylim() == pytest.approx(RETURN_LIMITS)
        assert axes["ruin"].yaxis.get_major_formatter()(-0.05, 0) == "−0.05"

    def test_the_two_months_below_the_line_are_marked(self, axes) -> None:
        marker = _by_gid(axes["ruin"].lines)["below"]
        assert list(marker.get_xdata()) == [
            pd.Timestamp("2001-06-29"),
            pd.Timestamp("2001-09-28"),
        ], SPEC
        assert [f"{r:.4f}" for r in marker.get_ydata()] == ["-0.0403", "-0.0337"], SPEC
        assert marker.get_color() == LOST
        texts = _by_gid(axes["ruin"].texts)
        assert [texts[f"below-label-{n}"].get_text() for n in (0, 1)] == [
            "2001-06-29: −0.0403\nagainst a line at −0.0144",
            "2001-09-28: −0.0337\nagainst a line at −0.0296",
        ], SPEC

    def test_a_month_exactly_on_the_line_is_marked(self, sources, portfolios, tmp_path) -> None:
        """At or below, as the heading says, so a return equal to its line is marked.

        No month on the committed vintages sits exactly on the line, so June
        2001's return is moved onto it here.
        """
        june = pd.Timestamp("2001-06-29")
        line = ruin_line(portfolios.rf, portfolios.leverage)
        low = portfolios.low.copy()
        low.loc[june] = line.loc[june]
        drawn = make_low_beta_leverage_figure(
            out=tmp_path / LOW_BETA_LEVERAGE_FIGURE,
            portfolios=dataclasses.replace(portfolios, low=low),
            sources=sources,
        )
        marker = _by_gid(drawn.axes[2].lines)["below"]
        assert list(marker.get_xdata()) == [june, pd.Timestamp("2001-09-28")]

    def test_zero_is_marked_by_a_muted_line(self, axes) -> None:
        zero = _by_gid(axes["ruin"].lines)["zero"]
        assert list(zero.get_ydata()) == [0, 0]
        assert zero.get_color() == MUTED

    def test_the_axis_is_ticked_every_0_04(self, axes) -> None:
        low, high = axes["ruin"].get_ylim()
        shown = [t for t in axes["ruin"].get_yticks() if low <= t <= high]
        assert shown == pytest.approx([-0.08, -0.04, 0.0, 0.04, 0.08, 0.12])

    def test_the_legend_names_the_line_and_the_return(self, axes) -> None:
        legend = [t.get_text() for t in axes["ruin"].get_legend().get_texts()]
        assert legend == ["ruin line, rf − (1 + rf) / k", "low fifth's monthly return"]

    def test_the_heading_names_where_the_line_leaves_the_panel(self, axes) -> None:
        assert _title(axes["ruin"]) == (
            "The low fifth's monthly return against the return that would ruin the levered "
            "month. The line\nleaves the panel from 2002-02-28 on, and 2 months fall at or "
            "below it."
        ), SPEC


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
    """Where each label's rule points, and where its text sits.

    The panels' own classes pin each label's text. These pin the geometry,
    so a label that names the right number while its rule points at the
    formation month, or two labels stacked on one spot, fails.
    """

    #: Each label's point, as its holding month, its value as printed, and
    #: the series that holds that value.
    POINTS = {
        ("beta", "lowest-label"): ("2001-05-31", "0.0280", "low_beta"),
        ("leverage", "highest-label"): ("2001-05-31", "69.0762", "leverage"),
        ("leverage", "ruined-label-0"): ("2001-06-29", "58.0262", "leverage"),
        ("leverage", "ruined-label-1"): ("2001-09-28", "31.5098", "leverage"),
        ("ruin", "below-label-0"): ("2001-06-29", "-0.0403", "low"),
        ("ruin", "below-label-1"): ("2001-09-28", "-0.0337", "low"),
    }

    def test_every_label_is_listed(self, axes) -> None:
        drawn = {(panel, t.get_gid()) for panel, ax in axes.items() for t in ax.texts}
        assert drawn == set(self.POINTS)

    @pytest.mark.parametrize(("panel", "gid"), list(POINTS))
    def test_each_rule_points_at_its_marked_point(self, axes, portfolios, panel, gid) -> None:
        month, value, series = self.POINTS[(panel, gid)]
        label = _by_gid(axes[panel].texts)[gid]
        assert label.xy[0] == pd.Timestamp(month), SPEC
        assert f"{label.xy[1]:.4f}" == value, SPEC
        assert label.xy[1] == getattr(portfolios, series).loc[month]

    def test_every_label_sits_inside_its_panel(self, axes, renderer) -> None:
        for panel, ax in axes.items():
            (x0, x1), (y0, y1) = ax.get_xlim(), ax.get_ylim()
            frame = ax.get_window_extent(renderer)
            for gid, box in _text_boxes(ax, renderer).items():
                x, y = _by_gid(ax.texts)[gid].xyann
                assert x0 <= date2num(x) <= x1 and y0 <= y <= y1, (panel, gid)
                assert frame.x0 <= box.x0 and box.x1 <= frame.x1, (panel, gid)
                assert frame.y0 <= box.y0 and box.y1 <= frame.y1, (panel, gid)

    def test_no_two_labels_in_a_panel_overlap(self, axes, renderer) -> None:
        for panel, ax in axes.items():
            anchors = [t.xyann for t in ax.texts]
            assert len(set(anchors)) == len(anchors), panel
            boxes = list(_text_boxes(ax, renderer).items())
            for n, (gid, box) in enumerate(boxes):
                for other, second in boxes[n + 1 :]:
                    assert not box.overlaps(second), (panel, gid, other)

    def test_no_label_crosses_a_line(self, axes, renderer) -> None:
        """``LABEL_AT`` was placed by eye so that no label's text crosses a drawn line."""
        for panel, ax in axes.items():
            for gid, box in _text_boxes(ax, renderer).items():
                for line in ax.lines:
                    xy = _points(line)
                    inside = (
                        (box.x0 <= xy[:, 0])
                        & (xy[:, 0] <= box.x1)
                        & (box.y0 <= xy[:, 1])
                        & (xy[:, 1] <= box.y1)
                    )
                    assert not inside.any(), (panel, gid, line.get_gid())


class TestTheHelpers:
    def test_signed_prints_a_true_minus_sign(self) -> None:
        assert signed(-2.50531) == "−2.5053"
        assert signed(-0.05, 2) == "−0.05"
        assert signed(0.12, 2) == "0.12"


class TestTheFile:
    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.exists() and out.stat().st_size > 0

    def test_the_committed_figure_exists(self) -> None:
        assert (FIGURES_DIR / LOW_BETA_LEVERAGE_FIGURE).is_file()

    def test_a_fresh_draw_has_the_committed_image_dimensions(self, figure, out) -> None:
        assert png_size(out) == png_size(FIGURES_DIR / LOW_BETA_LEVERAGE_FIGURE)

    def test_drawing_to_out_leaves_the_committed_figure_alone(
        self, tmp_path, sources, portfolios
    ) -> None:
        committed = FIGURES_DIR / LOW_BETA_LEVERAGE_FIGURE
        before = committed.read_bytes()
        touched = committed.stat().st_mtime_ns
        make_low_beta_leverage_figure(
            out=tmp_path / LOW_BETA_LEVERAGE_FIGURE, portfolios=portfolios, sources=sources
        )
        assert committed.read_bytes() == before
        # A redraw is deterministic, so a stray write would leave the bytes
        # the same. Only the modification time shows it.
        assert committed.stat().st_mtime_ns == touched

    def test_main_lets_any_other_error_through_as_itself(self, monkeypatch) -> None:
        def fail(*_a, **_k):
            raise ValueError("a bug, not a refusal")

        monkeypatch.setattr(module, "make_low_beta_leverage_figure", fail)
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
        monkeypatch.setattr(module, "make_low_beta_leverage_figure", lambda: None)
        main()
        assert capsys.readouterr().out == f"wrote {FIGURES_DIR / LOW_BETA_LEVERAGE_FIGURE}\n"
