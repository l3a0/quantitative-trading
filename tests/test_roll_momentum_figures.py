"""The pins for the figure in the post on TU momentum traded on the lagged roll return.

``tests/test_roll_momentum.py`` holds what the run computes. This file holds
that the figure draws those numbers, so a generator that plotted the wrong
series, shaded the wrong rows or moved a threshold fails even when the
arithmetic is right. Some numbers repeat here on purpose, because a figure's
labels are prose and the suite is the authority for every number prose quotes.
No test compares bytes, for the reason ``tests/test_regime_figure.py`` gives.

- **Vintage.** ``inputdatadaily_tu_20120813/``, chan-mat, raw, saved
  2012-08-14, 93 contracts and ``TU-SPOT`` over 5,565 days from 1990-06-22 to
  2012-08-13, read through ``chan.roll_returns.load_strip``. The figure reads
  no second vintage.
- **Specification.** The declared rule in :mod:`chan.roll_momentum`'s
  docstring, as ``tests/test_roll_momentum.py`` states it. γ is
  ``roll_returns`` in column units. Long where γ > 0.03 and short where
  γ < −0.03, both strict. The return is ``backshift(1, pos)`` times the
  rebuilt front-contract return, which rolls 7 rows before the held contract's
  last priced row. Every series runs on the full 5,565-row index and is cut to
  2009-01-02 to 2012-08-13, 913 rows, last. Example 6.1's rule is
  ``chan.tu_momentum``'s ``signals`` on the rebuilt level, then
  ``positions``, then ``strategy_returns`` on the rebuilt return. The
  cumulative return is ``cumprod(1 + ret) − 1`` over the window, with no cost.

Exploratory. The rule was declared after about 90 scratch readings, as the
run's module docstring discloses.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from matplotlib.dates import date2num

from chan import roll_momentum_figures
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD
from chan.roll_momentum import roll_momentum
from chan.roll_momentum_figures import FIGURE, flat_spans, main, make_roll_momentum_figure
from chan.roll_returns import load_strip
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable

WINDOW_ROWS = 913
FLAT_ROWS = 341
LONG_ROWS = 572
GAMMA_PEAK = 0.073403
GAMMA_PEAK_DAY = pd.Timestamp("2009-10-12")


@pytest.fixture(scope="module")
def strip():
    return load_strip("TU")


@pytest.fixture(scope="module")
def result(strip):
    return roll_momentum(strip)


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("roll_momentum_figure") / FIGURE


@pytest.fixture(scope="module")
def figure(out, strip):
    return make_roll_momentum_figure(out=out, strip=strip)


@pytest.fixture(scope="module")
def axes(figure):
    curve, gamma = figure.axes
    return {"curve": curve, "gamma": gamma}


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _title(ax) -> str:
    return ax.get_title(loc="left")


def _shaded(ax, days: pd.DatetimeIndex) -> np.ndarray:
    """The window rows whose date falls inside a span drawn with the gid ``flat``."""
    x = date2num(days)
    shaded = np.zeros(len(x), dtype=bool)
    for span in ax.patches:
        if span.get_gid() == "flat":
            left = span.get_x()
            shaded |= (x >= left) & (x <= left + span.get_width())
    return shaded


class TestTheCurves:
    @pytest.mark.parametrize("gid", ["declared", "example"])
    def test_each_is_dated_over_the_913_window_rows(self, axes, result, gid) -> None:
        line = _by_gid(axes["curve"].lines)[gid]
        days = pd.DatetimeIndex(line.get_xdata())
        assert days.equals(result.window_days)
        assert len(days) == WINDOW_ROWS
        assert (str(days[0].date()), str(days[-1].date())) == ("2009-01-02", "2012-08-13")
        assert axes["curve"].get_xlim() == (date2num(days[0]), date2num(days[-1]))

    def test_the_declared_rule_is_its_compounded_window_return(self, axes, result) -> None:
        y = _by_gid(axes["curve"].lines)["declared"].get_ydata()
        np.testing.assert_array_equal(y, np.cumprod(1 + result.daily[result.window]) - 1)

    def test_example_6_1_is_its_compounded_window_return(self, axes, result) -> None:
        y = _by_gid(axes["curve"].lines)["example"].get_ydata()
        np.testing.assert_array_equal(y, np.cumprod(1 + result.example_daily[result.window]) - 1)

    def test_the_declared_rule_ends_at_its_apr_compounded_over_913_rows(self, axes, result) -> None:
        y = _by_gid(axes["curve"].lines)["declared"].get_ydata()
        assert y[-1] == pytest.approx(0.050629, abs=1e-6)
        assert y[-1] == pytest.approx((1 + result.figures.apr) ** (913 / 252) - 1, abs=1e-12)

    def test_example_6_1_ends_at_its_apr_compounded_over_913_rows(self, axes, result) -> None:
        y = _by_gid(axes["curve"].lines)["example"].get_ydata()
        assert y[-1] == pytest.approx(0.049322, abs=1e-6)
        assert y[-1] == pytest.approx(
            (1 + result.example_figures.apr) ** (913 / 252) - 1, abs=1e-12
        )

    def test_example_6_1_holds_all_25_tranches_long_so_its_line_is_holding_tu(
        self, axes, result
    ) -> None:
        """What the heading says, held here so the heading cannot outlive it."""
        assert (result.example_positions[result.window] == 25).all()
        y = _by_gid(axes["curve"].lines)["example"].get_ydata()
        market = np.nan_to_num(result.market[result.window])
        np.testing.assert_allclose(y, np.cumprod(1 + market) - 1, atol=1e-12)

    def test_the_colours_and_the_legend(self, axes) -> None:
        lines = _by_gid(axes["curve"].lines)
        assert (lines["declared"].get_color(), lines["example"].get_color()) == (GOOD, ACCENT)
        assert list(lines["zero"].get_ydata()) == [0, 0]
        labels = [t.get_text() for t in axes["curve"].get_legend().get_texts()]
        assert labels == [
            "Example 6.1's rule, on the 250-day return",
            "the declared rule, on the lagged roll return",
        ]

    def test_the_heading_sets_the_figures_beside_the_books(self, axes) -> None:
        assert _title(axes["curve"]) == (
            "The compounded cumulative return over the 913 window rows, shaded where the "
            "declared rule is flat.\nThe declared rule: APR 0.013725 and Sharpe ratio 1.803348, "
            "which the book prints as 2.5 percent and 2.1.\nExample 6.1's rule: APR 0.013377 and "
            "Sharpe ratio 1.196742. It holds all 25 tranches long on every\nwindow row, so its "
            "line is holding TU. They end at 0.050629 and 0.049322, before costs."
        )


class TestTheShading:
    @pytest.mark.parametrize("panel", ["curve", "gamma"])
    def test_it_covers_exactly_the_341_flat_rows(self, axes, result, panel) -> None:
        shaded = _shaded(axes[panel], result.window_days)
        assert shaded.sum() == FLAT_ROWS
        np.testing.assert_array_equal(shaded, result.held_position == 0)

    def test_the_rule_is_long_on_every_other_row(self, result) -> None:
        held = result.held_position
        assert ((held > 0).sum(), (held < 0).sum(), (held == 0).sum()) == (LONG_ROWS, 0, FLAT_ROWS)

    def test_the_declared_curve_does_not_move_on_a_flat_row(self, axes, result) -> None:
        y = np.asarray(_by_gid(axes["curve"].lines)["declared"].get_ydata())
        flat = result.held_position == 0
        assert flat[0]
        assert y[0] == 0
        assert (np.diff(y)[flat[1:]] == 0).all()

    def test_a_run_of_one_row_still_gets_a_width(self) -> None:
        days = pd.DatetimeIndex(["2009-01-02", "2009-01-05", "2009-01-06", "2009-01-07"])
        ((left, right),) = flat_spans(days, np.array([False, True, False, False]))
        x = date2num(days)
        assert x[0] < left < x[1] < right < x[2]

    def test_a_run_at_either_end_stops_at_the_axis(self) -> None:
        days = pd.DatetimeIndex(["2009-01-02", "2009-01-05", "2009-01-06", "2009-01-07"])
        x = date2num(days)
        first, last = flat_spans(days, np.array([True, False, False, True]))
        assert first[0] == x[0] and last[1] == x[-1]


class TestTheRollReturnPanel:
    def test_gamma_is_drawn_in_column_units_over_the_window(self, axes, result) -> None:
        line = _by_gid(axes["gamma"].lines)["gamma"]
        assert pd.DatetimeIndex(line.get_xdata()).equals(result.window_days)
        np.testing.assert_array_equal(line.get_ydata(), result.gamma[result.window])

    def test_gamma_peaks_at_0_073403_on_2009_10_12(self, axes, result) -> None:
        line = _by_gid(axes["gamma"].lines)["gamma"]
        y = np.asarray(line.get_ydata())
        assert y.max() == pytest.approx(GAMMA_PEAK, abs=1e-6)
        assert result.window_days[int(np.argmax(y))] == GAMMA_PEAK_DAY

    def test_gamma_never_falls_below_minus_1_5e_14(self, axes) -> None:
        """Zero to rounding, so it never comes near the short threshold."""
        y = np.asarray(_by_gid(axes["gamma"].lines)["gamma"].get_ydata())
        assert not np.isnan(y).any()
        assert y.min() >= -1.5e-14
        assert y.min() < 0

    def test_the_thresholds_are_dashed_at_plus_and_minus_3_percent(self, axes) -> None:
        lines = _by_gid(axes["gamma"].lines)
        assert list(lines["long above"].get_ydata()) == [pytest.approx(0.03)] * 2
        assert list(lines["short below"].get_ydata()) == [pytest.approx(-0.03)] * 2
        assert lines["long above"].get_linestyle() == lines["short below"].get_linestyle() == "--"

    def test_both_thresholds_are_inside_the_drawn_range(self, axes) -> None:
        bottom, top = axes["gamma"].get_ylim()
        assert bottom < -0.03 and top > GAMMA_PEAK

    def test_the_heading_says_what_the_thresholds_do(self, axes) -> None:
        assert _title(axes["gamma"]) == (
            "The rule goes long when γ is above 3 percent and short below −3 percent, on the "
            "next row.\nγ peaks at 0.073403 on 2009-10-12 and never falls below −3 percent in "
            "the window,\nso the rule is long on 572 rows, short on none and flat on the 341 "
            "shaded rows."
        )


class TestTheFigure:
    def test_there_are_two_panels_sharing_the_dates(self, figure, axes) -> None:
        assert len(figure.axes) == 2
        assert axes["curve"].get_xlim() == axes["gamma"].get_xlim()

    def test_the_title_is_exploratory_and_the_note_names_the_vintage(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Exploratory: TU momentum traded on the lagged roll return, against Example 6.1"
        )
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Algorithmic Trading, location 2690. TU contracts from inputdatadaily_tu_20120813/, "
            "saved 2012-08-14.\nThe series is the front contract rebuilt from the strip, rolling "
            "7 rows before its last price.\nThe rule was declared after about 90 scratch "
            "readings, so this is no registered test, and no cost is taken."
        ]

    def test_drawing_with_no_strip_reads_the_committed_files(self, tmp_path, result) -> None:
        """``main`` and the committed PNG take this path, so it is drawn here too."""
        drawn = make_roll_momentum_figure(out=tmp_path / FIGURE)
        line = _by_gid(drawn.axes[0].lines)["declared"]
        np.testing.assert_array_equal(
            line.get_ydata(), np.cumprod(1 + result.daily[result.window]) - 1
        )

    def test_a_strip_passed_in_is_drawn_without_reading_again(
        self, monkeypatch, tmp_path, strip
    ) -> None:
        monkeypatch.setattr(
            roll_momentum_figures, "load_strip", lambda *_a: pytest.fail("read again")
        )
        make_roll_momentum_figure(out=tmp_path / FIGURE, strip=strip)


class TestTheFile:
    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.exists() and out.stat().st_size > 0

    def test_the_committed_figure_exists(self) -> None:
        assert (FIGURES_DIR / FIGURE).is_file()

    def test_main_names_the_file_it_wrote(self, monkeypatch, capsys) -> None:
        monkeypatch.setattr(roll_momentum_figures, "make_roll_momentum_figure", lambda: None)
        main()
        assert capsys.readouterr().out == f"wrote {FIGURES_DIR / FIGURE}\n"

    def test_main_lets_any_other_error_through_as_itself(self, monkeypatch) -> None:
        def fail(*_a, **_k):
            raise ValueError("a bug, not a refusal")

        monkeypatch.setattr(roll_momentum_figures, "make_roll_momentum_figure", fail)
        with pytest.raises(ValueError, match="a bug, not a refusal"):
            main()

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable(
                "no committed vintage is lifted from inputDataDaily_TU_20120813.mat"
            ),
            WindowCrossesScaleBreak("inputdatadaily_tu_20120813/tu-2009h.csv changes scale"),
        ],
    )
    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(roll_momentum_figures, "make_roll_momentum_figure", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)
