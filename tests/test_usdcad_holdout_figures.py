"""The pins for the figure in the post on Example 2.5 on USD/CAD after 2012.

``tests/test_usdcad_holdout.py`` holds what the run computes. This file holds
that the figure draws those numbers, so a generator that plotted the wrong
series, started the P&L on a warm-up day, used another lookback or shaded the
wrong fall fails even when the arithmetic is right. Some numbers repeat here
on purpose, because a figure's labels are prose and the suite is the authority
for every number prose quotes. No test compares bytes, for the reason
``tests/test_regime_figure.py`` gives, and ``tests/test_figures_match_code.py``
compares the committed file with a fresh draw.

The figure reads the vintage and the specification
``tests/test_usdcad_holdout.py`` names as its ``SPEC``, which every failure
message here carries too. The final P&L's sign is the registered claim, and
everything else the figure draws is exploratory.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from matplotlib.colors import same_color
from matplotlib.dates import DateFormatter, YearLocator, date2num, num2date

from chan import usdcad_holdout_figures as figures
from chan.matlab_helpers import moving_avg
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST
from chan.series import WindowCrossesScaleBreak
from chan.usdcad_holdout import HoldoutRefused, compute, read_closes, read_holdout
from chan.usdcad_holdout_figures import (
    USDCAD_HOLDOUT_FIGURE,
    cumulative_pnl,
    main,
    make_usdcad_holdout_figure,
    moving_average,
    signed,
)
from chan.vintage import VintageUnavailable
from tests.test_usdcad_holdout import SPEC

FIRST, LAST = pd.Timestamp("2011-10-20"), pd.Timestamp("2026-10-12")
LAST_WARM_UP, FIRST_TRADED = pd.Timestamp("2012-03-28"), pd.Timestamp("2012-03-29")
PEAK, TROUGH = pd.Timestamp("2013-11-20"), pd.Timestamp("2016-01-19")


@pytest.fixture(scope="module")
def holdout():
    return read_holdout()


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("usdcad_holdout_figure") / USDCAD_HOLDOUT_FIGURE


@pytest.fixture(scope="module")
def figure(out, holdout):
    return make_usdcad_holdout_figure(out=out, holdout=holdout)


@pytest.fixture(scope="module")
def axes(figure):
    closes, pnl = figure.axes
    return {"closes": closes, "pnl": pnl}


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _title(ax) -> str:
    return ax.get_title(loc="left")


def _days(line) -> list[pd.Timestamp]:
    return [pd.Timestamp(d) for d in line.get_xdata()]


class TestThePanels:
    def test_there_are_two_in_the_order_the_post_reads_them(self, figure, axes) -> None:
        assert len(figure.axes) == 2
        assert _title(axes["closes"]).startswith("The closes of USD.CAD")
        assert _title(axes["pnl"]).startswith("The cumulative P&L")

    def test_they_share_the_date_axis_over_the_warm_up_and_the_traded_days(
        self, axes, holdout
    ) -> None:
        days = holdout.closes.index
        assert len(days) == 115 + 3791, SPEC
        assert (days[0], days[-1]) == (FIRST, LAST), SPEC
        limits = {ax.get_xlim() for ax in axes.values()}
        assert limits == {(date2num(FIRST), date2num(LAST))}, SPEC
        assert axes["closes"].get_shared_x_axes().joined(axes["closes"], axes["pnl"])

    def test_a_tick_falls_on_every_second_year_from_2012_to_2026(self, axes) -> None:
        axis = axes["pnl"].xaxis
        assert isinstance(axis.get_major_locator(), YearLocator)
        assert axis.get_major_formatter().fmt == "%Y"
        assert isinstance(axis.get_major_formatter(), DateFormatter)
        low, high = axes["pnl"].get_xlim()
        shown = [t for t in axis.get_major_locator()() if low <= t <= high]
        assert [num2date(t).year for t in shown] == list(range(2012, 2027, 2)), SPEC

    def test_a_dashed_line_marks_the_first_traded_day_in_both(self, axes) -> None:
        for ax in axes.values():
            line = _by_gid(ax.lines)["first-traded-day"]
            assert set(line.get_xdata()) == {FIRST_TRADED}, SPEC
            assert line.get_linestyle() == "--"

    def test_the_title_carries_the_registered_label(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Registered: Example 2.5's linear rule on USD.CAD after Chan's sample"
        )

    def test_the_note_names_the_file_and_what_is_exploratory(self, figure) -> None:
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Alpha Vantage FX_DAILY closes, 2011-10-20 to 2026-10-12, from "
            "alphavantage_usdcad_raw_2007-08-10_2026-10-12_dl2026-10-13.csv.\nThe registered "
            "claim is the sign of the final P&L, predicted before any of these closes was "
            "read.\nThe curve, the fall and the half-life are exploratory."
        ], SPEC

    def test_no_label_is_parsed_as_math(self, figure) -> None:
        """The P&L heading prints an ampersand, and an ampersand is not a formula."""
        for ax in figure.axes:
            for text in [*ax.texts, ax.title, ax._left_title]:
                assert text.get_parse_math() is False
        for text in figure.texts:
            assert text.get_parse_math() is False


class TestTheCloses:
    def test_the_line_is_every_close_the_run_read(self, axes, holdout) -> None:
        line = _by_gid(axes["closes"].lines)["closes"]
        assert _days(line) == list(holdout.closes.index), SPEC
        np.testing.assert_array_equal(line.get_ydata(), holdout.closes.to_numpy())

    def test_the_average_is_movingavg_over_the_frozen_115(self, axes, holdout) -> None:
        assert holdout.lookback == 115, SPEC
        line = _by_gid(axes["closes"].lines)["moving-average"]
        expected = moving_avg(holdout.closes.to_numpy(dtype=float), 115)
        np.testing.assert_array_equal(line.get_ydata(), expected)
        np.testing.assert_array_equal(moving_average(holdout).to_numpy(), expected)

    def test_the_average_fills_on_the_last_warm_up_close(self, axes, holdout) -> None:
        """Row 114 is the 115th close, so the average covers every traded day."""
        y = np.asarray(_by_gid(axes["closes"].lines)["moving-average"].get_ydata())
        assert np.isnan(y[:114]).all(), SPEC
        assert np.isfinite(y[114:]).all(), SPEC
        assert holdout.closes.index[114] == LAST_WARM_UP, SPEC
        assert y[114] == pytest.approx(1.0102365217, abs=5e-11), SPEC

    def test_the_closes_are_ink_and_the_average_brass(self, axes) -> None:
        lines = _by_gid(axes["closes"].lines)
        assert same_color(lines["closes"].get_color(), INK)
        assert same_color(lines["moving-average"].get_color(), ACCENT)

    def test_the_legend_names_both_lines(self, axes) -> None:
        legend = [t.get_text() for t in axes["closes"].get_legend().get_texts()]
        assert legend == ["daily close", "115-day moving average"]

    def test_the_heading_names_the_lookback_the_first_day_and_the_half_life(self, axes) -> None:
        assert _title(axes["closes"]) == (
            "The closes of USD.CAD and their 115-day moving average, the lookback frozen from "
            "Chan's 2007 to 2012 closes.\nThe dashed line is the first traded day, 2012-03-29. "
            "The 115 closes before it only fill the window.\nThe half-life of the traded "
            "days' closes is 457.8 days."
        ), SPEC


class TestThePnl:
    def test_the_line_is_cumsum_of_the_traded_days_alone(self, axes, holdout) -> None:
        line = _by_gid(axes["pnl"].lines)["pnl"]
        assert _days(line) == list(holdout.traded.index), SPEC
        assert len(line.get_xdata()) == 3791, SPEC
        assert _days(line)[0] == FIRST_TRADED, SPEC
        expected = holdout.traded.cumsum().to_numpy()
        np.testing.assert_array_equal(line.get_ydata(), expected)
        np.testing.assert_array_equal(cumulative_pnl(holdout).to_numpy(), expected)

    def test_it_ends_at_h1s_sum(self, axes, holdout) -> None:
        last = _by_gid(axes["pnl"].lines)["pnl"].get_ydata()[-1]
        assert last == pytest.approx(0.1131618949, abs=5e-11), SPEC
        assert last == pytest.approx(holdout.total_pnl, abs=1e-12)

    def test_a_line_marks_zero(self, axes) -> None:
        assert list(_by_gid(axes["pnl"].lines)["zero"].get_ydata()) == [0, 0]

    def test_the_shaded_span_runs_from_the_peak_to_the_trough(self, axes, holdout) -> None:
        band = _by_gid(axes["pnl"].patches)["drawdown"]
        low, high = band.get_x(), band.get_x() + band.get_width()
        assert (low, high) == (date2num(PEAK), date2num(TROUGH)), SPEC
        assert (holdout.drawdown.peak, holdout.drawdown.trough) == (PEAK, TROUGH), SPEC
        assert same_color(band.get_facecolor()[:3], LOST)

    def test_the_peak_and_trough_are_marked_on_the_line(self, axes) -> None:
        marks = _by_gid(axes["pnl"].lines)
        for gid, day, value in (
            ("peak", PEAK, 0.1035025300),
            ("trough", TROUGH, -0.3997903912),
        ):
            assert _days(marks[gid]) == [day], (gid, SPEC)
            assert marks[gid].get_ydata()[0] == pytest.approx(value, abs=5e-11), (gid, SPEC)

    def test_the_trough_is_the_lowest_point_and_the_peak_is_not_the_highest(self, axes) -> None:
        """The curve climbs past its 2013 high after the fall, so the shaded fall's
        peak is not the curve's highest point, unlike the fall on Chan's closes."""
        lines = _by_gid(axes["pnl"].lines)
        y = np.asarray(lines["pnl"].get_ydata())
        assert lines["trough"].get_ydata()[0] == y.min(), SPEC
        assert lines["peak"].get_ydata()[0] < y.max(), SPEC

    def test_the_shaded_fall_is_the_runs_drawdown(self, axes, holdout) -> None:
        lines = _by_gid(axes["pnl"].lines)
        fall = lines["peak"].get_ydata()[0] - lines["trough"].get_ydata()[0]
        assert fall == pytest.approx(holdout.drawdown.depth, abs=1e-12)
        assert fall == pytest.approx(0.5032929212, abs=5e-11), SPEC

    def test_the_curve_is_green(self, axes) -> None:
        assert same_color(_by_gid(axes["pnl"].lines)["pnl"].get_color(), GOOD)

    def test_the_heading_sets_the_days_the_total_and_the_fall(self, axes) -> None:
        assert _title(axes["pnl"]) == (
            "The cumulative P&L over 3,791 traded days, ending at 0.1132. Unlevered and "
            "before costs.\nThe shaded fall runs from 0.1035 on 2013-11-20 to −0.3998 on "
            "2016-01-19, 0.5033 deep."
        ), SPEC
        assert axes["pnl"].get_ylabel() == "cumulative P&L, summed"

    def test_signed_prints_a_true_minus_sign(self) -> None:
        assert signed(-0.3997903912) == "−0.3998"
        assert signed(0.1131618949) == "0.1132"
        assert signed(-0.3997903912, 2) == "−0.40"


class TestTheReadPath:
    def test_drawing_with_no_holdout_reads_the_runs_path(self, monkeypatch, tmp_path, holdout):
        asked = []

        def read():
            asked.append(True)
            return holdout

        monkeypatch.setattr(figures, "read_holdout", read)
        drawn = make_usdcad_holdout_figure(out=tmp_path / USDCAD_HOLDOUT_FIGURE)
        assert asked == [True]
        line = _by_gid(drawn.axes[0].lines)["closes"]
        np.testing.assert_array_equal(line.get_ydata(), holdout.closes.to_numpy())

    def test_a_holdout_handed_in_is_the_holdout_drawn(self, tmp_path, holdout) -> None:
        """A run with a 20-day lookback ending in mid-2012, so a figure that read the
        file instead, or wrote 115 into a label, would fail."""
        entry, closes = read_closes()
        short = compute(entry, closes, start="2012-04-02", end="2012-06-29", lookback=20)
        drawn = make_usdcad_holdout_figure(out=tmp_path / USDCAD_HOLDOUT_FIGURE, holdout=short)
        lines = _by_gid(drawn.axes[1].lines)
        np.testing.assert_array_equal(lines["pnl"].get_ydata(), short.traded.cumsum().to_numpy())
        assert _days(lines["pnl"])[0] == pd.Timestamp("2012-04-02")
        average = _by_gid(drawn.axes[0].lines)["moving-average"]
        assert int(np.flatnonzero(np.isfinite(average.get_ydata()))[0]) == 19
        assert average.get_label() == "20-day moving average"

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage of USDCAD downloaded 2026-10-13"),
            HoldoutRefused("fewer than 115 warm-up closes before 2012-03-29"),
            WindowCrossesScaleBreak("USDCAD changes scale on 2015-01-02"),
        ],
    )
    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(figures, "make_usdcad_holdout_figure", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)

    def test_any_other_error_keeps_its_traceback(self, monkeypatch) -> None:
        def broken(*_a, **_k):
            raise KeyError("Close")

        monkeypatch.setattr(figures, "make_usdcad_holdout_figure", broken)
        with pytest.raises(KeyError, match="Close"):
            main()

    def test_the_command_writes_the_committed_path(self, monkeypatch, capsys) -> None:
        drawn = []
        monkeypatch.setattr(figures, "make_usdcad_holdout_figure", lambda **kw: drawn.append(kw))
        main()
        assert drawn == [{}]
        assert f"wrote {FIGURES_DIR / USDCAD_HOLDOUT_FIGURE}" in capsys.readouterr().out

    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.is_file() and out.stat().st_size > 0


def test_the_committed_figure_exists() -> None:
    assert (FIGURES_DIR / USDCAD_HOLDOUT_FIGURE).is_file()
