"""The pins for the figure in the post on VX against ES on VX's roll return, location 2754.

``tests/test_vx_es_roll_return.py`` holds what the run computes. This file
holds that the figure draws those numbers, so a generator that plotted the
wrong rule, shaded the wrong side or marked the wrong drawdown fails even when
the arithmetic is right. Some numbers repeat here on purpose, because a
figure's labels are prose and the suite is the authority for every number
prose quotes. No test compares bytes, for the reason
``tests/test_regime_figure.py`` gives.

The figure draws three of the four vintages that
``tests/test_vx_es_roll_return.py`` states in its module docstring:
``data/inputdatadaily_vx_20120507/``, vendor chan-mat, basis raw, saved
2012-05-08, ``data/vix/vix.csv``, vendor chan-csv, basis raw, saved
2012-05-09, and ``data/inputdataohlcdaily_20120507/es.csv``, vendor chan-mat,
basis adjusted, saved 2012-05-09. Loading ES also checks the fourth,
``data/inputdataohlcdaily_20120507/vx.csv``, against its checksum, since it
belongs to the same save, and the figure draws nothing from it. Its
specifications are that file's H, the hedge 0.3906, and U, the hedge [1, 1],
over the 448 test days from 2010-07-29 to 2012-05-07.

The curve's ends, the drawdown's marks and the signal's extremes were
measured after the run, for the post, and pinning them here is what keeps the
post's quotes of them honest. Exploratory, like everything Entry 41 computes
here.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from matplotlib.colors import to_rgba
from matplotlib.dates import date2num

from chan import vx_es as vx_es_module
from chan import vx_es_roll_return as run_module
from chan import vx_es_roll_return_figures as module
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, GROUND, INK, MUTED
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable
from chan.vx_es_roll_return import (
    HEDGE,
    SHIPPED_HEDGE,
    front_roll,
    read_sources,
    roll_return_trade,
)
from chan.vx_es_roll_return_figures import (
    FIGURE,
    cumulative_return,
    held_runs,
    main,
    make_vx_es_roll_return_figure,
    signed,
)
from tests.test_regime_figure import png_size

SPEC = (
    "inputdatadaily_vx_20120507/ chan-mat raw saved 2012-05-08, vix/vix.csv chan-csv raw "
    "saved 2012-05-09, inputdataohlcdaily_20120507/es.csv chan-mat adjusted saved 2012-05-09; "
    "H and U as tests/test_vx_es_roll_return.py states them, from 2010-07-29 to 2012-05-07"
)

day = pd.Timestamp


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def hedged(sources):
    return roll_return_trade(sources, HEDGE)


@pytest.fixture(scope="module")
def shipped(sources):
    return roll_return_trade(sources, SHIPPED_HEDGE)


@pytest.fixture(scope="module")
def roll(sources, hedged) -> pd.Series:
    contracts = sources.strip.contracts.loc[hedged.days]
    return front_roll(contracts, sources.vix.loc[hedged.days]).iloc[hedged.test]


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("vx_es_roll_return_figure") / FIGURE


@pytest.fixture(scope="module")
def figure(out, sources):
    return make_vx_es_roll_return_figure(out=out, sources=sources)


@pytest.fixture(scope="module")
def axes(figure):
    curve, signal = figure.axes
    return {"curve": curve, "roll": signal}


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


def _drawn_spans(ax, gid: str, days: pd.DatetimeIndex) -> list[tuple]:
    """Each span drawn with ``gid`` as the first and last day it covers and how many."""
    x = date2num(days)
    found = []
    for span in ax.patches:
        if span.get_gid() == gid:
            left = span.get_x()
            inside = days[(x >= left) & (x <= left + span.get_width())]
            found.append((inside[0], inside[-1], len(inside)))
    return found


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
        assert axes["curve"].get_shared_x_axes().joined(axes["curve"], axes["roll"])
        assert axes["curve"].get_xlim() == (
            date2num(day("2010-07-29")),
            date2num(day("2012-05-07")),
        )

    def test_the_title_carries_the_label_and_the_note_names_the_three_vintages(
        self, figure
    ) -> None:
        assert figure._suptitle.get_text() == "Exploratory: VX against ES on VX's roll return"
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Algorithmic Trading, Kindle edition, pp. 211 to 213. VX contracts from "
            "inputDataDaily_VX_20120507.mat, saved 2012-05-08.\nVIX from VIX.csv, saved "
            "2012-05-09. ES from inputDataOHLCDaily_20120507.mat, saved 2012-05-09.\nOne basis "
            "point of each day's change in market value is charged, and nothing on an entry "
            "from flat."
        ]

    def test_drawing_with_no_sources_reads_the_committed_vintages(self, tmp_path, hedged) -> None:
        """``main`` and the committed PNG take this path, so it is drawn here too."""
        drawn = make_vx_es_roll_return_figure(out=tmp_path / FIGURE)
        line = _by_gid(drawn.axes[0].lines)["hedged"]
        np.testing.assert_array_equal(line.get_ydata(), cumulative_return(hedged.test_daily))

    def test_it_reads_the_sources_once_and_never_computes_the_fitted_hedge(
        self, tmp_path, monkeypatch
    ) -> None:
        """Only the fitted hedge uses VX's continuous close as data, and the figure omits it.

        Loading ES still checks that file against its checksum, as a member of
        the same save, so what this holds is that no route reaches the fit.
        Each name is patched where it is defined and where it is imported, so
        a call through ``chan.vx_es`` fails as well as one through the run.
        """
        calls = []
        real = module.read_sources

        def record(*args, **kwargs):
            calls.append(args)
            return real(*args, **kwargs)

        def refuse(*_a, **_k):
            raise AssertionError("the figure reached the fitted hedge")

        monkeypatch.setattr(module, "read_sources", record)
        for owner in (vx_es_module, run_module, module):
            for name in ("read_legs", "fit_hedge", "fitted_hedge"):
                if hasattr(owner, name):
                    monkeypatch.setattr(owner, name, refuse)
        make_vx_es_roll_return_figure(out=tmp_path / FIGURE)
        assert calls == [()]


class TestTheCumulativeReturns:
    """Figure 6.4, ``cumprod(1+r)-1`` over the 448 test days, under both rules."""

    @pytest.mark.parametrize("gid", ["hedged", "shipped"])
    def test_each_line_is_dated_over_the_448_test_days(self, axes, hedged, gid) -> None:
        days = pd.DatetimeIndex(_by_gid(axes["curve"].lines)[gid].get_xdata())
        assert (len(days), str(days[0].date()), str(days[-1].date())) == (
            448,
            "2010-07-29",
            "2012-05-07",
        ), SPEC
        assert days.equals(hedged.test_days)

    def test_the_book_s_rule_is_its_compounded_return(self, axes, hedged) -> None:
        line = _by_gid(axes["curve"].lines)["hedged"]
        np.testing.assert_allclose(
            line.get_ydata(), np.cumprod(1 + hedged.test_daily) - 1, rtol=1e-12
        )

    def test_the_live_lines_are_their_compounded_return(self, axes, shipped) -> None:
        line = _by_gid(axes["curve"].lines)["shipped"]
        np.testing.assert_allclose(
            line.get_ydata(), np.cumprod(1 + shipped.test_daily) - 1, rtol=1e-12
        )

    def test_each_curve_ends_where_the_post_says(self, axes) -> None:
        ends = {
            g: f"{_by_gid(axes['curve'].lines)[g].get_ydata()[-1]:.6f}"
            for g in ("hedged", "shipped")
        }
        assert ends == {"hedged": "0.126063", "shipped": "0.581024"}, SPEC

    @pytest.mark.parametrize("gid", ["hedged", "shipped"])
    def test_each_curve_reaches_its_end_on_2012_04_24_and_stays_for_9_rows(self, axes, gid) -> None:
        line = _by_gid(axes["curve"].lines)[gid]
        days, y = pd.DatetimeIndex(line.get_xdata()), line.get_ydata()
        assert days[-10] == day("2012-04-24")
        assert (y[-9:] == y[-10]).all()
        assert y[-11] != y[-10]

    def test_the_book_s_rule_peaks_on_2011_12_19(self, axes) -> None:
        line = _by_gid(axes["curve"].lines)["hedged"]
        y = line.get_ydata()
        peak = int(np.argmax(y))
        assert (pd.Timestamp(line.get_xdata()[peak]), f"{y[peak]:.6f}") == (
            day("2011-12-19"),
            "0.129142",
        ), SPEC

    def test_the_book_s_rule_is_in_ink_and_the_live_lines_muted_and_dashed(self, axes) -> None:
        lines = _by_gid(axes["curve"].lines)
        assert (lines["hedged"].get_color(), lines["hedged"].get_linestyle()) == (INK, "-")
        assert (lines["shipped"].get_color(), lines["shipped"].get_linestyle()) == (MUTED, "--")
        assert lines["hedged"].get_zorder() > lines["shipped"].get_zorder()

    def test_the_drawdown_s_high_and_trough_are_marked(self, axes) -> None:
        high, trough = (
            _point(axes["curve"], "drawdown-high"),
            _point(axes["curve"], "drawdown-trough"),
        )
        assert (high[0], f"{high[1]:.6f}") == (day("2010-08-31"), "0.049547"), SPEC
        assert (trough[0], f"{trough[1]:.6f}") == (day("2011-08-08"), "-0.029886"), SPEC
        assert (1 + trough[1]) / (1 + high[1]) - 1 == pytest.approx(-0.07568284958529414)
        labels = _by_gid(axes["curve"].texts)
        assert labels["drawdown-high-label"].get_text() == "high, 0.049547 on 2010-08-31"
        assert labels["drawdown-trough-label"].get_text() == "trough, −0.029886 on 2011-08-08"

    def test_both_curves_fit_inside_the_panel(self, axes) -> None:
        low, high = axes["curve"].get_ylim()
        for gid in ("hedged", "shipped"):
            y = _by_gid(axes["curve"].lines)[gid].get_ydata()
            assert low <= y.min() and y.max() <= high

    @pytest.mark.parametrize("gid", ["drawdown-high", "drawdown-trough"])
    def test_each_drawdown_label_points_at_its_marker(self, axes, gid) -> None:
        assert _labelled_at(axes["curve"], gid) == _point(axes["curve"], gid)

    def test_the_longest_run_label_sits_over_the_middle_of_its_line(self, axes) -> None:
        line = _by_gid(axes["curve"].lines)["longest-drawdown"]
        first, last = (pd.Timestamp(x) for x in line.get_xdata())
        assert _labelled_at(axes["curve"], "longest-drawdown") == (
            first + (last - first) / 2,
            float(line.get_ydata()[0]),
        )

    def test_the_longest_run_is_the_deepest_drawdown_s_episode(self, axes) -> None:
        """259 days from the day after the 2010-08-31 high, at that high's level."""
        line = _by_gid(axes["curve"].lines)["longest-drawdown"]
        assert [pd.Timestamp(x) for x in line.get_xdata()] == [
            day("2010-09-01"),
            day("2011-09-09"),
        ], SPEC
        assert [f"{y:.6f}" for y in line.get_ydata()] == ["0.049547"] * 2
        label = _by_gid(axes["curve"].texts)["longest-drawdown-label"]
        assert label.get_text() == "259 days below this high, to 2011-09-09"

    def test_the_curve_makes_a_new_high_on_2011_09_12(self, axes) -> None:
        line = _by_gid(axes["curve"].lines)["hedged"]
        days, y = pd.DatetimeIndex(line.get_xdata()), line.get_ydata()
        high = y[days.get_loc(day("2010-08-31"))]
        above = days[(y > high) & (days > day("2010-08-31"))]
        assert above[0] == day("2011-09-12")

    def test_the_legend_names_each_shade_and_each_line_with_its_end(self, axes) -> None:
        legend = [t.get_text() for t in axes["curve"].get_legend().get_texts()]
        assert legend == [
            "held short VX and short ES",
            "held long VX and long ES",
            "1 VX contract per ES contract, the script's live lines, ending at 58.10 percent",
            "0.3906 VX contracts per ES contract, the book's rule, ending at 12.61 percent",
        ], SPEC

    def test_the_axis_reads_a_percentage_and_draws_a_zero_line(self, axes) -> None:
        assert axes["curve"].yaxis.get_major_formatter()(0.25) == "25%"
        assert list(_by_gid(axes["curve"].lines)["zero"].get_ydata()) == [0, 0]

    def test_the_heading_sets_the_figures_beside_the_book(self, axes) -> None:
        assert _title(axes["curve"]) == (
            "Figure 6.4: cumulative return over the test, 2010-07-29 to 2012-05-07.\nUnder "
            "0.3906, APR 0.069065 and Sharpe ratio 1.002020, where the book prints 6.9 percent "
            "and 1.\nThe deepest drawdown is −0.075683."
        ), SPEC


class TestTheShading:
    @pytest.mark.parametrize("panel", ["curve", "roll"])
    @pytest.mark.parametrize(("gid", "sign", "count"), [("short", -1, 196), ("long", 1, 28)])
    def test_it_covers_exactly_the_days_held_on_each_side(
        self, axes, hedged, panel, gid, sign, count
    ) -> None:
        covered = _covered(axes[panel], gid, hedged.test_days)
        held = hedged.es_leg[hedged.test] == sign
        assert int(covered.sum()) == count
        np.testing.assert_array_equal(covered, held)

    @pytest.mark.parametrize("panel", ["curve", "roll"])
    def test_the_spans_count_25_short_and_7_long(self, axes, hedged, panel) -> None:
        """Read off the drawn patches, and ``held_runs`` agrees with them."""
        short = _drawn_spans(axes[panel], "short", hedged.test_days)
        long = _drawn_spans(axes[panel], "long", hedged.test_days)
        assert (len(short), len(long)) == (25, 7)
        assert max(short, key=lambda r: r[2]) == (day("2010-07-29"), day("2010-09-20"), 37), SPEC
        assert max(long, key=lambda r: r[2]) == (day("2011-07-27"), day("2011-08-22"), 19), SPEC
        leg = hedged.es_leg[hedged.test]
        assert held_runs(hedged.test_days, leg < 0) == short
        assert held_runs(hedged.test_days, leg > 0) == long

    @pytest.mark.parametrize("panel", ["curve", "roll"])
    @pytest.mark.parametrize(("gid", "shade"), [("short", (ACCENT, 0.16)), ("long", (GOOD, 0.22))])
    def test_each_side_has_its_own_tint(self, axes, panel, gid, shade) -> None:
        assert {"short": module.SHORT_SHADE, "long": module.LONG_SHADE}[gid] == shade
        spans = [p for p in axes[panel].patches if p.get_gid() == gid]
        assert spans and all(p.get_facecolor() == to_rgba(*shade) for p in spans)

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


class TestTheSignalPanel:
    def test_the_roll_is_drawn_on_the_448_days_and_defined_on_438(self, axes, roll) -> None:
        line = _by_gid(axes["roll"].lines)["roll"]
        days = pd.DatetimeIndex(line.get_xdata())
        y = np.asarray(line.get_ydata(), dtype=float)
        assert (len(days), days[0], days[-1]) == (448, day("2010-07-29"), day("2012-05-07"))
        np.testing.assert_array_equal(y, roll.to_numpy())
        assert int(np.isfinite(y).sum()) == 438, SPEC
        assert np.isnan(y[-10:]).all()
        assert days[-11] == day("2012-04-23")

    def test_196_rows_sit_above_the_line_28_below_and_214_between(self, axes) -> None:
        y = np.asarray(_by_gid(axes["roll"].lines)["roll"].get_ydata(), dtype=float)
        y = y[np.isfinite(y)]
        assert (int((y > 0.1).sum()), int((y < -0.1).sum())) == (196, 28)
        assert int((np.abs(y) <= 0.1).sum()) == 214, SPEC

    def test_the_roll_is_drawn_in_ink(self, axes) -> None:
        assert _by_gid(axes["roll"].lines)["roll"].get_color() == INK

    @pytest.mark.parametrize("gid", ["roll-low", "roll-high"])
    def test_each_roll_label_points_at_its_marker(self, axes, gid) -> None:
        assert _labelled_at(axes["roll"], gid) == _point(axes["roll"], gid)

    def test_its_low_and_high_are_marked(self, axes) -> None:
        low, high = _point(axes["roll"], "roll-low"), _point(axes["roll"], "roll-high")
        assert (low[0], f"{low[1]:.6f}") == (day("2011-08-08"), "-0.574194"), SPEC
        assert (high[0], f"{high[1]:.6f}") == (day("2012-03-16"), "0.311739"), SPEC
        labels = _by_gid(axes["roll"].texts)
        assert labels["roll-low-label"].get_text() == "low, −0.574194 on 2011-08-08"
        assert labels["roll-high-label"].get_text() == "high, 0.311739 on 2012-03-16"

    def test_dashed_lines_mark_both_thresholds(self, axes) -> None:
        lines = _by_gid(axes["roll"].lines)
        assert list(lines["short-line"].get_ydata()) == [0.1, 0.1]
        assert list(lines["long-line"].get_ydata()) == [-0.1, -0.1]
        assert lines["short-line"].get_linestyle() == lines["long-line"].get_linestyle() == "--"
        assert list(lines["zero"].get_ydata()) == [0, 0]

    def test_the_heading_states_the_window_and_the_rule(self, axes) -> None:
        assert _title(axes["roll"]) == (
            "The signal: the front VX contract less VIX, over the trading days to settlement, "
            "each contract the front\nfrom 40 to 10 rows before its last price. Above 0.1 the "
            "rule is short both legs, below −0.1 long both.\nThe last 10 days have no front, and "
            "the rule holds nothing on them."
        )

    def test_the_markers_are_drawn_in_the_accent(self, axes) -> None:
        for panel, gid in (
            ("curve", "drawdown-high"),
            ("curve", "drawdown-trough"),
            ("roll", "roll-low"),
            ("roll", "roll-high"),
        ):
            assert _by_gid(axes[panel].lines)[gid].get_color() == ACCENT

    def test_signed_prints_a_true_minus_sign(self) -> None:
        assert signed(-0.574194, 6) == "−0.574194"
        assert signed(58.1024) == "58.10"


class TestTheLabels:
    """A review found the live lines' curve running through the high's label and the
    signal's December 2011 spike striking the 0.311739 in the signal's own."""

    @pytest.mark.parametrize(
        "panel, curves", [("curve", ("hedged", "shipped")), ("roll", ("roll",))]
    )
    def test_no_curve_runs_through_a_label(self, figure, axes, panel, curves) -> None:
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        from matplotlib.text import Text

        canvas = FigureCanvasAgg(figure)
        canvas.draw()
        renderer = canvas.get_renderer()
        lines = _by_gid(axes[panel].lines)
        labels = [text for text in axes[panel].texts if text.get_text()]
        assert len(labels) == {"curve": 3, "roll": 2}[panel]
        for gid in curves:
            line = lines[gid]
            path = line.get_transform().transform_path(line.get_path())
            for text in labels:
                # The text's own extent, without the leader line back to its marker.
                box = Text.get_window_extent(text, renderer)
                assert not path.intersects_bbox(box, filled=False), (gid, text.get_text())

    @pytest.mark.parametrize("panel", ["curve", "roll"])
    def test_every_label_sits_on_the_ground(self, axes, panel) -> None:
        for text in axes[panel].texts:
            patch = text.get_bbox_patch()
            assert patch is not None, text.get_text()
            assert patch.get_facecolor() == to_rgba(GROUND), text.get_text()


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
        make_vx_es_roll_return_figure(out=tmp_path / FIGURE, sources=sources)
        assert committed.read_bytes() == before
        # A redraw is deterministic, so a stray write would leave the bytes
        # the same. Only the modification time shows it.
        assert committed.stat().st_mtime_ns == touched

    def test_main_lets_any_other_error_through_as_itself(self, monkeypatch) -> None:
        def fail(*_a, **_k):
            raise ValueError("a bug, not a refusal")

        monkeypatch.setattr(module, "make_vx_es_roll_return_figure", fail)
        with pytest.raises(ValueError, match="a bug, not a refusal"):
            main()

    def test_a_missing_vintage_reaches_the_operator_as_one_line(
        self, monkeypatch, tmp_path
    ) -> None:
        """No mock: the real read, pointed at an empty directory, refuses the VX strip."""
        from chan import paths

        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert isinstance(stopped.value.__cause__, VintageUnavailable)
        assert "inputDataDaily_VX_20120507.mat" in str(stopped.value)
        assert "\n" not in str(stopped.value)

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage is lifted from VIX.csv"),
            WindowCrossesScaleBreak("vix/vix.csv changes scale"),
        ],
    )
    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(module, "make_vx_es_roll_return_figure", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)

    def test_main_reports_the_file_it_wrote(self, monkeypatch, capsys) -> None:
        monkeypatch.setattr(module, "make_vx_es_roll_return_figure", lambda: None)
        main()
        assert capsys.readouterr().out == f"wrote {FIGURES_DIR / FIGURE}\n"
