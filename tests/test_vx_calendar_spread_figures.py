"""The pins for the figure in the post on VIX futures calendar spreads, location 2502.

``tests/test_vx_calendar_spread.py`` holds what the run computes. This file
holds that the figure draws those numbers, so a generator that plotted the
wrong row, moved the book's end date or swapped the bars before and after
October 2008 fails even when the arithmetic is right. Some numbers repeat here
on purpose, because a figure's labels are prose and the suite is the authority
for every number prose quotes. No test compares bytes, for the reason
``tests/test_regime_figure.py`` gives.

The figure reads the vintage and the rows that
``tests/test_vx_calendar_spread.py`` states in its module docstring:
``data/inputdatadaily_vx_20120507/``, vendor chan-mat, basis raw, saved
2012-05-08, and S and B1 to B3 from 2008-10-27 to 2012-05-07.

Exploratory, like everything Entry 35 computes here, and B3 was picked out
after the run among five rows.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from matplotlib.dates import date2num

from chan import vx_calendar_spread_figures as module
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, INK, MUTED
from chan.roll_returns import load_strip
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable
from chan.vx_calendar_spread import ROWS_BEFORE, vx_calendar_spread
from chan.vx_calendar_spread_figures import (
    CURVES,
    VX_CALENDAR_SPREAD_FIGURE,
    cumulative_return,
    main,
    make_vx_calendar_spread_figure,
    signed,
)
from tests.test_regime_figure import png_size

SPEC = (
    "inputdatadaily_vx_20120507/ chan-mat raw saved 2012-05-08; S and B1 to B3 as "
    "tests/test_vx_calendar_spread.py states them, from 2008-10-27 to 2012-05-07"
)


@pytest.fixture(scope="module")
def strip():
    return load_strip("VX")


@pytest.fixture(scope="module")
def result(strip):
    return vx_calendar_spread(strip.contracts)


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("vx_calendar_spread_figure") / VX_CALENDAR_SPREAD_FIGURE


@pytest.fixture(scope="module")
def figure(out, strip):
    return make_vx_calendar_spread_figure(out=out, strip=strip)


@pytest.fixture(scope="module")
def axes(figure):
    returns, before = figure.axes
    return {"returns": returns, "before": before}


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _title(ax) -> str:
    return ax.get_title(loc="left")


def _rects(ax, gid: str) -> list:
    return [patch for patch in ax.patches if patch.get_gid() == gid]


def _bars(ax, gid: str) -> list[float]:
    return [bar.get_height() for bar in _rects(ax, gid)]


class TestTheFigure:
    def test_there_are_two_panels(self, figure) -> None:
        assert len(figure.axes) == 2

    def test_the_title_carries_the_label_and_the_note_names_the_save(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Exploratory: VIX futures calendar spreads on the ratio of back to front"
        )
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Algorithmic Trading, location 2502. Contracts from inputDataDaily_VX_20120507.mat, "
            "saved 2012-05-08.\nB3 was picked out after the run among five rows, and no cost "
            "is charged."
        ]

    def test_drawing_with_no_strip_reads_the_committed_vintage(self, tmp_path, result) -> None:
        """``main`` and the committed PNG take this path, so it is drawn here too."""
        drawn = make_vx_calendar_spread_figure(out=tmp_path / VX_CALENDAR_SPREAD_FIGURE)
        line = _by_gid(drawn.axes[0].lines)["B3"]
        np.testing.assert_array_equal(
            line.get_ydata(), cumulative_return(result.rows["B3"].returns)
        )


class TestTheCumulativeReturns:
    """Figure 5.8, ``cumprod(1+ret)-1`` for S and B1 to B3 over the 889 rows from 2008-10-27."""

    def test_it_draws_s_and_b1_to_b3_and_not_b4(self, axes) -> None:
        drawn = [line.get_gid() for line in axes["returns"].lines if line.get_gid() in CURVES]
        assert drawn == ["B3", "S", "B1", "B2"]
        assert "B4" not in _by_gid(axes["returns"].lines)

    @pytest.mark.parametrize("key", CURVES)
    def test_each_line_is_its_rows_compounded_return(self, axes, result, key) -> None:
        line = _by_gid(axes["returns"].lines)[key]
        days = pd.DatetimeIndex(line.get_xdata())
        assert (len(days), str(days[0].date()), str(days[-1].date())) == (
            889,
            "2008-10-27",
            "2012-05-07",
        ), SPEC
        assert days.equals(result.rows[key].returns.index)
        np.testing.assert_allclose(
            line.get_ydata(),
            np.cumprod(1 + result.rows[key].returns.to_numpy()) - 1,
            rtol=1e-12,
        )

    def test_each_curve_ends_where_the_post_says(self, axes) -> None:
        ends = {key: f"{_by_gid(axes['returns'].lines)[key].get_ydata()[-1]:.6f}" for key in CURVES}
        assert ends == {
            "B3": "0.758213",
            "S": "-0.135565",
            "B1": "0.123003",
            "B2": "-0.345330",
        }, SPEC

    def test_b3_stands_at_0_765276_on_the_books_end_date(self, axes, result) -> None:
        """The same figure B3 compounds to on the book's own window, measured after the run."""
        line = _by_gid(axes["returns"].lines)["B3"]
        on_end = pd.Series(line.get_ydata(), index=pd.DatetimeIndex(line.get_xdata()))
        assert f"{on_end.loc['2012-04-23']:.6f}" == "0.765276", SPEC
        book = np.prod(1 + result.b3_book_window.returns.to_numpy()) - 1
        assert f"{book:.6f}" == "0.765276", SPEC

    def test_b3_is_drawn_in_ink_and_s_in_the_accent(self, axes) -> None:
        lines = _by_gid(axes["returns"].lines)
        assert (lines["B3"].get_color(), lines["B3"].get_linestyle()) == (INK, "-")
        assert (lines["S"].get_color(), lines["S"].get_linestyle()) == (ACCENT, "-")
        assert {lines[key].get_color() for key in ("B1", "B2")} == {MUTED}
        assert lines["B3"].get_zorder() > max(lines[key].get_zorder() for key in ("S", "B1", "B2"))

    def test_the_books_end_date_is_marked(self, axes) -> None:
        marker = _by_gid(axes["returns"].lines)["book-end"]
        assert list(marker.get_xdata()) == [pd.Timestamp("2012-04-23")] * 2
        label = _by_gid(axes["returns"].texts)["book-end-label"]
        assert label.get_text() == "the book's end, 2012-04-23"

    def test_the_axis_spans_the_window_and_reads_a_percentage(self, axes) -> None:
        assert axes["returns"].get_xlim() == (
            date2num(pd.Timestamp("2008-10-27")),
            date2num(pd.Timestamp("2012-05-07")),
        )
        assert axes["returns"].yaxis.get_major_formatter()(0.2) == "20%"

    def test_the_legend_names_each_row_and_its_end(self, axes) -> None:
        legend = [t.get_text() for t in axes["returns"].get_legend().get_texts()]
        assert legend == [
            "B3, the held pair's ratio, each pair held in turn, ending at 75.82 percent",
            "S, the specification, the front pair's ratio, ending at −13.56 percent",
            "B1, the held pair's ratio, ending at 12.30 percent",
            "B2, the front pair's ratio, each pair held in turn, ending at −34.53 percent",
        ], SPEC

    def test_the_heading_sets_b3_on_the_books_window_beside_the_book(self, axes) -> None:
        assert _title(axes["returns"]) == (
            "Figure 5.8: each row's cumulative return, 2008-10-27 to 2012-05-07. On the book's "
            "window to 2012-04-23,\nB3's APR is 0.176952 and its Sharpe ratio 1.475658, where "
            "the book prints 17.7 percent and 1.5."
        ), SPEC


class TestTheRowsBeforeOctober2008:
    """Each row's APR before October 2008 beside its APR from 2008-10-27."""

    def test_the_bars_are_s_and_b1_to_b3_in_order(self, axes) -> None:
        ticks = [t.get_text() for t in axes["before"].get_xticklabels()]
        assert ticks == list(ROWS_BEFORE) == ["S", "B1", "B2", "B3"]

    def test_the_bars_before_are_each_rows_apr_to_2008_10_24(self, axes) -> None:
        assert [f"{h:.6f}" for h in _bars(axes["before"], "before")] == [
            "-0.027638",
            "0.204377",
            "-0.018707",
            "-0.074173",
        ], SPEC

    def test_the_bars_after_are_each_rows_apr_from_2008_10_27(self, axes) -> None:
        assert [f"{h:.6f}" for h in _bars(axes["before"], "after")] == [
            "-0.040454",
            "0.033430",
            "-0.113153",
            "0.173462",
        ], SPEC

    def test_only_b3s_bar_falls_before_october_2008(self, axes) -> None:
        before = _bars(axes["before"], "before")
        after = _bars(axes["before"], "after")
        worse = [key for key, b, a in zip(ROWS_BEFORE, before, after, strict=True) if b < a]
        assert worse == ["B3"], SPEC

    def test_the_bars_before_sit_left_of_the_bars_after(self, axes) -> None:
        before = [bar.get_x() for bar in _rects(axes["before"], "before")]
        after = [bar.get_x() for bar in _rects(axes["before"], "after")]
        assert all(b < a for b, a in zip(before, after, strict=True))
        colors = {
            gid: {bar.get_facecolor() for bar in _rects(axes["before"], gid)}
            for gid in ("before", "after")
        }
        assert colors["before"] != colors["after"]

    def test_each_bar_is_labelled_with_its_apr_in_percent(self, axes) -> None:
        labels = [t.get_text() for t in axes["before"].texts]
        assert labels == ["−2.8", "20.4", "−1.9", "−7.4", "−4.0", "3.3", "−11.3", "17.3"], SPEC

    def test_the_heading_names_the_windows_and_the_claim(self, axes) -> None:
        assert _title(axes["before"]) == (
            "Each row's APR before October 2008, from its first held row (2006-11-10 at the "
            "earliest) to 2008-10-24,\nbeside its APR from 2008-10-27. Only B3 does worse "
            "before, as the book says of its rule."
        ), SPEC

    def test_signed_prints_a_true_minus_sign(self) -> None:
        assert signed(-13.5565) == "−13.56"
        assert signed(20.4377, 1) == "20.4"


class TestTheFile:
    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.exists() and out.stat().st_size > 0

    def test_the_committed_figure_exists(self) -> None:
        assert (FIGURES_DIR / VX_CALENDAR_SPREAD_FIGURE).is_file()

    def test_a_fresh_draw_has_the_committed_image_dimensions(self, figure, out) -> None:
        assert png_size(out) == png_size(FIGURES_DIR / VX_CALENDAR_SPREAD_FIGURE)

    def test_drawing_to_out_leaves_the_committed_figure_alone(self, tmp_path, strip) -> None:
        committed = FIGURES_DIR / VX_CALENDAR_SPREAD_FIGURE
        before = committed.read_bytes()
        touched = committed.stat().st_mtime_ns
        make_vx_calendar_spread_figure(out=tmp_path / VX_CALENDAR_SPREAD_FIGURE, strip=strip)
        assert committed.read_bytes() == before
        # A redraw is deterministic, so a stray write would leave the bytes
        # the same. Only the modification time shows it.
        assert committed.stat().st_mtime_ns == touched

    def test_main_lets_any_other_error_through_as_itself(self, monkeypatch) -> None:
        def fail(*_a, **_k):
            raise ValueError("a bug, not a refusal")

        monkeypatch.setattr(module, "make_vx_calendar_spread_figure", fail)
        with pytest.raises(ValueError, match="a bug, not a refusal"):
            main()

    def test_a_missing_vintage_reaches_the_operator_as_one_line(
        self, monkeypatch, tmp_path
    ) -> None:
        """No mock: the real read, pointed at an empty directory, refuses the strip."""
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
            VintageUnavailable("no committed vintage is lifted from inputDataDaily_VX_20120507"),
            WindowCrossesScaleBreak("inputdatadaily_vx_20120507/vx-2012k.csv changes scale"),
        ],
    )
    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(module, "make_vx_calendar_spread_figure", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)

    def test_main_reports_the_file_it_wrote(self, monkeypatch, capsys) -> None:
        monkeypatch.setattr(module, "make_vx_calendar_spread_figure", lambda: None)
        main()
        assert capsys.readouterr().out == f"wrote {FIGURES_DIR / VX_CALENDAR_SPREAD_FIGURE}\n"
