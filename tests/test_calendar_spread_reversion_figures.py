"""The pins for the figure in the post on crude oil's calendar spread, Example 5.4.

``tests/test_calendar_spread_reversion.py`` holds what the run computes. This
file holds that the figure draws those numbers, so a generator that plotted
the wrong series, moved the shaded rows or mislabelled a panel fails even when
the arithmetic is right. Some numbers repeat here on purpose, because a
figure's labels are prose and the suite is the authority for every number
prose quotes. No test compares bytes, for the reason
``tests/test_regime_figure.py`` gives.

The figure reads the vintage and specification S that
``tests/test_calendar_spread_reversion.py`` states in its module docstring:
``data/inputdatadaily_cl_20120813/``, vendor chan-mat, basis raw, saved
2012-08-14, and ``calendarSpdsMeanReversion.m`` at EpchanPreview ``e4bc46f``
measured from 2008-01-02 to 2012-08-13.

Exploratory, like everything Example 5.4 computes here.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from matplotlib.dates import date2num

from chan import calendar_spread_reversion_figures as module
from chan.calendar_spread_reversion import START, run_spread
from chan.calendar_spread_reversion_figures import (
    CALENDAR_SPREAD_REVERSION_FIGURE,
    cumulative_return,
    flat_tail,
    held_rows,
    main,
    make_calendar_spread_reversion_figure,
    signed,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import INK, MUTED
from chan.roll_returns import load_strip, roll_returns
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable
from tests.test_regime_figure import png_size

SPEC = (
    "inputdatadaily_cl_20120813/ chan-mat raw saved 2012-08-14; S: calendarSpdsMeanReversion.m "
    "from 2008-01-02 to 2012-08-13"
)


@pytest.fixture(scope="module")
def strip():
    return load_strip("CL")


@pytest.fixture(scope="module")
def gamma(strip) -> pd.Series:
    return roll_returns(strip.contracts)


@pytest.fixture(scope="module")
def s(strip, gamma):
    return run_spread(strip.contracts, gamma, start=START)


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("calendar_spread_reversion_figure") / (
        CALENDAR_SPREAD_REVERSION_FIGURE
    )


@pytest.fixture(scope="module")
def figure(out, strip):
    return make_calendar_spread_reversion_figure(out=out, strip=strip)


@pytest.fixture(scope="module")
def axes(figure):
    returns, scatter = figure.axes
    return {"returns": returns, "scatter": scatter}


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _title(ax) -> str:
    return ax.get_title(loc="left")


class TestTheFigure:
    def test_there_are_two_panels(self, figure) -> None:
        assert len(figure.axes) == 2

    def test_the_title_carries_the_label_and_the_note_names_the_save(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Exploratory: Example 5.4's calendar spread on crude oil, and the direction it trades"
        )
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Algorithmic Trading, locations 2461 and 2471. Contracts from "
            "inputDataDaily_CL_20120813.mat, saved 2012-08-14.\nThe 2008 to 2012 window is the "
            "one Chan chose, and no cost is charged."
        ]

    def test_drawing_with_no_strip_reads_the_committed_vintage(self, tmp_path, s) -> None:
        """``main`` and the committed PNG take this path, so it is drawn here too."""
        drawn = make_calendar_spread_reversion_figure(
            out=tmp_path / CALENDAR_SPREAD_REVERSION_FIGURE
        )
        line = _by_gid(drawn.axes[0].lines)["cumulative"]
        np.testing.assert_array_equal(line.get_ydata(), cumulative_return(s.returns))


class TestTheCumulativeReturn:
    """Figure 5.7, ``cumprod(1+ret)-1`` over S's 1,164 rows."""

    def test_the_line_is_ss_compounded_return(self, axes, s) -> None:
        line = _by_gid(axes["returns"].lines)["cumulative"]
        days = pd.DatetimeIndex(line.get_xdata())
        assert (len(days), str(days[0].date()), str(days[-1].date())) == (
            1164,
            "2008-01-02",
            "2012-08-13",
        ), SPEC
        assert days.equals(s.returns.index)
        np.testing.assert_allclose(
            line.get_ydata(), np.cumprod(1 + s.returns.to_numpy()) - 1, rtol=1e-12
        )
        assert line.get_color() == INK and line.get_linestyle() == "-"
        assert axes["returns"].get_xlim() == (date2num(days[0]), date2num(days[-1]))

    def test_it_starts_at_ss_first_return_and_ends_at_0_443248(self, axes) -> None:
        ydata = _by_gid(axes["returns"].lines)["cumulative"].get_ydata()
        assert f"{ydata[0]:.7f}" == "-0.0028127", SPEC
        assert f"{ydata[-1]:.6f}" == "0.443248", SPEC

    def test_the_dashed_curve_compounds_the_negated_returns(self, axes, s) -> None:
        line = _by_gid(axes["returns"].lines)["reversed"]
        assert list(line.get_xdata()) == list(s.returns.index)
        np.testing.assert_allclose(
            line.get_ydata(), np.cumprod(1 - s.returns.to_numpy()) - 1, rtol=1e-12
        )
        assert f"{line.get_ydata()[-1]:.6f}" == "-0.320073", f"{SPEC}, every position reversed"
        assert line.get_linestyle() == "--" and line.get_color() == MUTED

    def test_the_shade_covers_the_last_66_rows(self, axes, s) -> None:
        flat = flat_tail(s.returns)
        assert len(flat) == 66, SPEC
        assert (str(flat[0].date()), str(flat[-1].date())) == ("2012-05-10", "2012-08-13"), SPEC
        assert flat.equals(s.returns.index[-66:])
        shade = _by_gid(axes["returns"].patches)["flat"]
        assert shade.get_x() == pytest.approx(date2num(flat[0]))
        assert shade.get_x() + shade.get_width() == pytest.approx(date2num(flat[-1]))

    def test_flat_tail_stops_at_the_last_nonzero_return(self) -> None:
        days = pd.bdate_range("2012-05-07", periods=5)
        assert flat_tail(pd.Series([0.0, 0.1, 0.0, 0.0, 0.0], index=days)).equals(days[2:])
        assert flat_tail(pd.Series([0.1, 0.1], index=days[:2])).empty
        assert flat_tail(pd.Series([0.0, 0.0], index=days[:2])).equals(days[:2])

    def test_the_last_held_day_is_marked(self, axes, s) -> None:
        marker = _by_gid(axes["returns"].lines)["last-held"]
        assert list(marker.get_xdata()) == [pd.Timestamp("2012-05-08")] * 2, SPEC
        assert s.last_held == pd.Timestamp("2012-05-08")
        label = _by_gid(axes["returns"].texts)["last-held-label"]
        assert label.get_text() == "last pair held on 2012-05-08"

    def test_the_axis_reads_the_return_as_a_percentage(self, axes) -> None:
        assert axes["returns"].yaxis.get_major_formatter()(0.2) == "20%"

    def test_the_legend_names_both_curves_and_their_ends(self, axes) -> None:
        legend = [t.get_text() for t in axes["returns"].get_legend().get_texts()]
        assert legend == [
            "S, the script's rule, ending at 44.32 percent",
            "every position reversed, ending at −32.01 percent",
        ], SPEC

    def test_the_heading_sets_the_figures_beside_the_book_s(self, axes) -> None:
        assert _title(axes["returns"]) == (
            "Figure 5.7: S's cumulative return, 2008-01-02 to 2012-08-13. APR 0.082671 and "
            "Sharpe ratio 1.278216,\nwhere the book prints 8.3 percent and 1.3. Shaded: the last "
            "66 rows, 2012-05-10 to 2012-08-13, which hold nothing."
        ), SPEC


class TestTheScatter:
    """The held pair's log spread against filled γ on S's held rows from 2008-01-02."""

    def test_it_plots_the_1097_held_rows(self, axes, strip, gamma) -> None:
        held = held_rows(strip.contracts, gamma, START)
        points = _by_gid(axes["scatter"].collections)["held"].get_offsets()
        assert len(points) == len(held.spread) == 1097, SPEC
        assert (str(held.spread.index[0].date()), str(held.spread.index[-1].date())) == (
            "2008-01-02",
            "2012-05-08",
        ), SPEC
        np.testing.assert_array_equal(
            points, np.column_stack([held.gamma.to_numpy(), held.spread.to_numpy()])
        )

    def test_the_spread_correlates_with_gamma_at_minus_0_883910(self, axes) -> None:
        points = _by_gid(axes["scatter"].collections)["held"].get_offsets()
        found = np.corrcoef(points[:, 0], points[:, 1])[0, 1]
        assert f"{found:.6f}" == "-0.883910", SPEC

    def test_the_heading_names_the_rows_and_the_correlation(self, axes) -> None:
        assert _title(axes["scatter"]) == (
            "The held pair's log spread against γ on the 1,097 held rows from 2008-01-02, "
            "correlation −0.883910.\nThe spread falls as γ rises, so the script's short where "
            "z(γ) is above 0 sells the spread when it is low."
        ), SPEC

    def test_held_rows_read_filled_gamma_from_the_start(self, monkeypatch) -> None:
        """γ on CL has no NaN after its first finite row, so only a synthetic signal holds
        the fill. Row 0 is before the start, row 2 holds no pair, and row 3's γ is carried
        forward from row 1."""
        days = pd.bdate_range("2008-01-01", periods=4)
        contracts = pd.DataFrame({"near": [100.0] * 4, "far": [90.0] * 4}, index=days)
        schedule = pd.DataFrame(
            {"near": [-1.0, -1.0, 0.0, -1.0], "far": [1.0, 1.0, 0.0, 1.0]}, index=days
        )
        monkeypatch.setattr(module, "calendar_schedule", lambda _contracts: schedule)
        gamma = pd.Series([0.1, 0.2, np.nan, np.nan], index=days)
        held = held_rows(contracts, gamma, days[1])
        assert held.spread.index.equals(days[[1, 3]])
        assert held.gamma.tolist() == [0.2, 0.2]
        assert held.spread.tolist() == [pytest.approx(np.log(0.9))] * 2

    def test_signed_prints_a_true_minus_sign(self) -> None:
        assert signed(-0.8839099, 6) == "−0.883910"
        assert signed(44.3248) == "44.32"


class TestTheFile:
    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.exists() and out.stat().st_size > 0

    def test_the_committed_figure_exists(self) -> None:
        assert (FIGURES_DIR / CALENDAR_SPREAD_REVERSION_FIGURE).is_file()

    def test_a_fresh_draw_has_the_committed_image_dimensions(self, figure, out) -> None:
        assert png_size(out) == png_size(FIGURES_DIR / CALENDAR_SPREAD_REVERSION_FIGURE)

    def test_drawing_to_out_leaves_the_committed_figure_alone(self, tmp_path, strip) -> None:
        committed = FIGURES_DIR / CALENDAR_SPREAD_REVERSION_FIGURE
        before = committed.read_bytes()
        touched = committed.stat().st_mtime_ns
        make_calendar_spread_reversion_figure(
            out=tmp_path / CALENDAR_SPREAD_REVERSION_FIGURE, strip=strip
        )
        assert committed.read_bytes() == before
        # A redraw is deterministic, so a stray write would leave the bytes
        # the same. Only the modification time shows it.
        assert committed.stat().st_mtime_ns == touched

    def test_main_lets_any_other_error_through_as_itself(self, monkeypatch) -> None:
        def fail(*_a, **_k):
            raise ValueError("a bug, not a refusal")

        monkeypatch.setattr(module, "make_calendar_spread_reversion_figure", fail)
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
        assert "inputDataDaily_CL_20120813.mat" in str(stopped.value)
        assert "\n" not in str(stopped.value)

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage is lifted from inputDataDaily_CL_20120813"),
            WindowCrossesScaleBreak("inputdatadaily_cl_20120813/cl-spot.csv changes scale"),
        ],
    )
    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(module, "make_calendar_spread_reversion_figure", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)

    def test_main_reports_the_file_it_wrote(self, monkeypatch, capsys) -> None:
        monkeypatch.setattr(module, "make_calendar_spread_reversion_figure", lambda: None)
        main()
        assert capsys.readouterr().out == (
            f"wrote {FIGURES_DIR / CALENDAR_SPREAD_REVERSION_FIGURE}\n"
        )
