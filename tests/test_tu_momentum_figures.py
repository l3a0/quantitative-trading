"""The pins for the figure in the post on time-series momentum on TU, Example 6.1.

``tests/test_tu_momentum.py`` holds what the run computes. This file holds that
the figure draws those numbers, so a generator that plotted the wrong series,
summed the returns rather than compounding them, marked the wrong day or shaded
the wrong fall fails even when the arithmetic is right. Some numbers repeat here
on purpose, because a figure's labels are prose and the suite is the authority
for every number prose quotes. No test compares bytes, for the reason
``tests/test_regime_figure.py`` gives.

Every pin reads one vintage and one specification, which every failure message
here carries as ``SPEC``.

- **Vintage.** ``inputdataohlcdaily_20120511/tu.csv``, chan-mat, adjusted,
  saved 2012-05-12, TU's column of ``inputDataOHLCDaily_20120511.mat``. It
  holds 2,000 closes from 2004-06-01 to 2012-05-11.
- **Specification.** ``TU_mom.m`` at EpchanPreview ``e4bc46f`` with
  ``idx = 1``, as :mod:`chan.tu_momentum` transcribes it: long where the close
  is above the close 250 rows back and short where below, each day's signal
  held 25 days, and the return yesterday's position times today's return over
  25. The curve is ``cumprod(1+ret)-1`` over all 2,000 returns, and the
  drawdown is ``calculateMaxDD``'s.

Exploratory, like everything Example 6.1 computes here.
"""

from __future__ import annotations

import shutil

import numpy as np
import pandas as pd
import pytest
from matplotlib.colors import same_color
from matplotlib.dates import DateFormatter, YearLocator, date2num, num2date

from chan import coin_flip_figures, paths, tu_momentum
from chan import tu_momentum_figures as figures
from chan.matlab_helpers import calculate_max_dd
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST
from chan.series import WindowCrossesScaleBreak, load_panel
from chan.tu_momentum import (
    ACTIVE_LINE_START,
    SOURCE_FILE,
    SYMBOL,
    read_sources,
)
from chan.tu_momentum import figures as run_figures
from chan.tu_momentum_figures import (
    TU_FIGURE,
    cumulative_return,
    daily_returns,
    main,
    make_tu_figure,
)
from chan.vintage import VintageUnavailable

SPEC = (
    "vintage inputdataohlcdaily_20120511/tu.csv, chan-mat, adjusted, saved 2012-05-12; "
    "TU_mom.m at e4bc46f with idx = 1"
)

FIRST, LAST = pd.Timestamp("2004-06-01"), pd.Timestamp("2012-05-11")
FIRST_RETURN = pd.Timestamp("2005-06-02")
ACTIVE = pd.Timestamp("2009-01-02")
HIGH, LOW = pd.Timestamp("2008-03-17"), pd.Timestamp("2008-06-13")
TOP = pd.Timestamp("2011-09-19")


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def run(sources):
    return tu_momentum.tu_momentum(sources[1])


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("tu_figure") / TU_FIGURE


@pytest.fixture(scope="module")
def figure(out, sources):
    return make_tu_figure(out=out, sources=sources)


@pytest.fixture(scope="module")
def axes(figure):
    closes, cumulative = figure.axes
    return {"closes": closes, "cumulative": cumulative}


@pytest.fixture(scope="module")
def curve(axes):
    line = _by_gid(axes["cumulative"].lines)["cumulative"]
    return pd.Series(np.asarray(line.get_ydata()), index=pd.DatetimeIndex(line.get_xdata()))


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _title(ax) -> str:
    return ax.get_title(loc="left")


def _days(line) -> list[pd.Timestamp]:
    return [pd.Timestamp(d) for d in line.get_xdata()]


def _legend(ax) -> list[str]:
    return [t.get_text() for t in ax.get_legend().get_texts()]


class TestThePanels:
    def test_there_are_two_in_the_order_the_post_reads_them(self, figure, axes) -> None:
        assert len(figure.axes) == 2
        assert _title(axes["closes"]).startswith("The 2,000 closes of TU")
        assert _title(axes["cumulative"]).startswith("The cumulative return")

    def test_they_share_the_date_axis_over_the_2000_closes(self, axes, sources) -> None:
        days = sources[1].index
        assert len(days) == 2000, SPEC
        assert (days[0], days[-1]) == (FIRST, LAST), SPEC
        limits = {ax.get_xlim() for ax in axes.values()}
        assert limits == {(date2num(FIRST), date2num(LAST))}, SPEC
        assert axes["closes"].get_shared_x_axes().joined(axes["closes"], axes["cumulative"])

    def test_a_tick_falls_on_every_year_from_2005_to_2012(self, axes) -> None:
        axis = axes["cumulative"].xaxis
        assert isinstance(axis.get_major_locator(), YearLocator)
        assert isinstance(axis.get_major_formatter(), DateFormatter)
        assert axis.get_major_formatter().fmt == "%Y"
        low, high = axes["cumulative"].get_xlim()
        shown = [t for t in axis.get_major_locator()() if low <= t <= high]
        assert [num2date(t).year for t in shown] == list(range(2005, 2013)), SPEC

    def test_the_title_carries_the_exploratory_label(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Exploratory: time-series momentum redrawn on Chan's own TU closes"
        )

    def test_the_note_names_the_file_the_window_and_the_choice(self, figure) -> None:
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Example 6.1 of Algorithmic Trading, 2004-06-01 to 2012-05-11, TU_mom.m with "
            "idx = 1.\nCloses from inputdataohlcdaily_20120511/tu.csv, saved 2012-05-12.\n"
            "The 250-day lookback and 25-day hold were chosen from a table of the same "
            "closes, so every figure is in-sample."
        ], SPEC

    def test_no_label_names_a_figure_number_from_the_book(self, figure) -> None:
        """The post's caption cites the book's Figure 6.2, so the image itself cites none."""
        words = [t.get_text() for t in figure.texts]
        for ax in figure.axes:
            words += [ax.get_title(loc="left"), ax.get_title(), *_legend(ax)]
        assert len(words) == 12
        assert not any("Figure" in w or "figure 6." in w for w in words)

    def test_no_label_is_parsed_as_math(self, figure) -> None:
        for ax in figure.axes:
            for text in [*ax.texts, ax.title, ax._left_title]:
                assert text.get_parse_math() is False
        for text in figure.texts:
            assert text.get_parse_math() is False


class TestTheCloses:
    def test_the_line_is_the_2000_closes_the_run_read(self, axes, sources) -> None:
        line = _by_gid(axes["closes"].lines)["closes"]
        assert _days(line) == list(sources[1].index), SPEC
        np.testing.assert_array_equal(line.get_ydata(), sources[1].to_numpy())

    def test_it_runs_from_97_9219_to_110_2734(self, axes) -> None:
        line = _by_gid(axes["closes"].lines)["closes"]
        days, y = _days(line), line.get_ydata()
        assert len(y) == 2000, SPEC
        assert (days[0], y[0]) == (FIRST, pytest.approx(97.9219, abs=5e-5)), SPEC
        assert (days[-1], y[-1]) == (LAST, pytest.approx(110.2734, abs=5e-5)), SPEC

    def test_the_highest_close_is_marked_at_110_3125_on_2011_09_19(self, axes) -> None:
        lines = _by_gid(axes["closes"].lines)
        mark = lines["close-high"]
        assert _days(mark) == [TOP], SPEC
        assert mark.get_ydata()[0] == pytest.approx(110.3125, abs=5e-5), SPEC
        assert mark.get_ydata()[0] == np.max(lines["closes"].get_ydata())

    def test_the_closes_are_ink_and_the_mark_brass(self, axes) -> None:
        lines = _by_gid(axes["closes"].lines)
        assert same_color(lines["closes"].get_color(), INK)
        assert same_color(lines["close-high"].get_color(), ACCENT)

    def test_the_legend_names_the_line_and_the_mark(self, axes) -> None:
        assert _legend(axes["closes"]) == [
            "TU's daily close",
            "highest close, 110.3125 on 2011-09-19",
        ], SPEC

    def test_the_heading_names_the_span_and_the_rule(self, axes) -> None:
        assert _title(axes["closes"]) == (
            "The 2,000 closes of TU, the two-year Treasury note future, from 97.9219 to "
            "110.2734.\nThe rule is long when the close is above the close 250 days back and "
            "short when it is below.\nEach day's call is held 25 days with 1/25 of the capital."
        ), SPEC
        assert axes["closes"].get_ylabel() == "close, back-adjusted"


class TestTheCumulativeReturn:
    def test_the_line_is_cumprod_of_the_runs_returns(self, curve, run, sources) -> None:
        assert list(curve.index) == list(sources[1].index), SPEC
        expected = np.cumprod(1 + run.daily) - 1
        np.testing.assert_array_equal(curve.to_numpy(), expected)
        np.testing.assert_array_equal(daily_returns(sources[1]), run.daily)
        np.testing.assert_array_equal(cumulative_return(run.daily), expected)

    def test_it_is_zero_until_2005_06_02(self, curve) -> None:
        """The first 250 rows have no signal and the next 25 hold no tranche yet, so the
        first return that is not zero falls on 2005-06-02."""
        nonzero = curve.to_numpy() != 0
        assert curve.index[int(np.argmax(nonzero))] == FIRST_RETURN, SPEC
        assert (curve[curve.index < FIRST_RETURN] == 0).all(), SPEC
        assert curve[FIRST_RETURN] != 0, SPEC

    def test_it_stands_at_0_085439_on_2009_01_02(self, curve) -> None:
        assert ACTIVE_LINE_START == ACTIVE
        assert round(curve[ACTIVE], 6) == 0.085439, SPEC

    def test_it_ends_at_0_140547_the_apr_compounded_over_2000_days(self, curve, run) -> None:
        last = curve.iloc[-1]
        assert round(last, 6) == 0.140547, SPEC
        apr = run_figures(run.daily).apr
        assert last == pytest.approx((1 + apr) ** (2000 / 252) - 1, abs=1e-12), SPEC

    def test_a_line_marks_zero(self, axes) -> None:
        assert list(_by_gid(axes["cumulative"].lines)["zero"].get_ydata()) == [0, 0]

    def test_a_vertical_line_marks_where_the_active_line_starts(self, axes) -> None:
        line = _by_gid(axes["cumulative"].lines)["active-line"]
        assert _days(line) == [ACTIVE, ACTIVE], SPEC
        assert line.get_linestyle() == "--"

    def test_the_shaded_span_runs_from_the_high_to_the_low(self, axes) -> None:
        band = _by_gid(axes["cumulative"].patches)["drawdown"]
        low, high = band.get_x(), band.get_x() + band.get_width()
        assert (low, high) == (date2num(HIGH), date2num(LOW)), SPEC
        assert same_color(band.get_facecolor()[:3], LOST)

    def test_the_shaded_fall_is_calculate_max_dds_drawdown(self, curve) -> None:
        """The fall is measured against the account's value at the high, as
        ``calculateMaxDD`` measures it, so it is −0.024847 and not the curve's own drop."""
        fall = (1 + curve[LOW]) / (1 + curve[HIGH]) - 1
        depth, _ = calculate_max_dd(curve.to_numpy())
        assert fall == pytest.approx(depth, abs=1e-15), SPEC
        assert round(fall, 6) == -0.024847, SPEC
        assert curve[HIGH] == curve[:LOW].max(), SPEC

    def test_the_highest_point_is_marked_at_0_140951_on_2011_09_19(self, axes, curve) -> None:
        mark = _by_gid(axes["cumulative"].lines)["high"]
        assert _days(mark) == [TOP], SPEC
        assert round(mark.get_ydata()[0], 6) == 0.140951, SPEC
        assert mark.get_ydata()[0] == curve.max()

    def test_the_curves_high_and_the_closes_high_fall_on_one_day(self, axes) -> None:
        closes_mark = _by_gid(axes["closes"].lines)["close-high"]
        curve_mark = _by_gid(axes["cumulative"].lines)["high"]
        assert _days(closes_mark) == _days(curve_mark) == [TOP], SPEC

    def test_the_curve_is_green(self, axes) -> None:
        assert same_color(_by_gid(axes["cumulative"].lines)["cumulative"].get_color(), GOOD)

    def test_the_legend_names_every_mark(self, axes) -> None:
        assert _legend(axes["cumulative"]) == [
            "deepest drawdown, −0.024847",
            "2009-01-02, where the script's active line starts",
            "the rule's cumulative return",
            "highest point, 0.140951 on 2011-09-19",
        ], SPEC

    def test_the_heading_sets_the_start_the_end_the_active_line_and_the_fall(self, axes):
        assert _title(axes["cumulative"]) == (
            "The cumulative return, flat until 2005-06-02 and ending at 0.140547. Unlevered "
            "and before costs.\nIt stands at 0.085439 on 2009-01-02. The shaded drawdown runs "
            "from the high on 2008-03-17\nto the low on 2008-06-13, −0.024847 against the "
            "account's value at the high."
        ), SPEC
        assert axes["cumulative"].get_ylabel() == "cumulative return, compounded"


class TestTheReadPath:
    def test_drawing_with_no_sources_reads_the_runs_path(self, monkeypatch, tmp_path, sources):
        asked = []

        def read():
            asked.append(True)
            return sources

        monkeypatch.setattr(figures, "read_sources", read)
        drawn = make_tu_figure(out=tmp_path / TU_FIGURE)
        assert asked == [True]
        line = _by_gid(drawn.axes[0].lines)["closes"]
        np.testing.assert_array_equal(line.get_ydata(), sources[1].to_numpy())

    def test_sources_handed_in_are_the_sources_drawn(self, tmp_path, sources, run) -> None:
        """The closes raised by 10, so a figure that ignored the argument and read the file
        would fail. Doubling them would not do, because the signals compare closes and the
        returns are ratios, and both cancel a scale."""
        entry, closes = sources
        shifted = closes + 10
        drawn = make_tu_figure(out=tmp_path / TU_FIGURE, sources=(entry, shifted))
        line = _by_gid(drawn.axes[1].lines)["cumulative"]
        expected = np.cumprod(1 + tu_momentum.tu_momentum(shifted).daily) - 1
        np.testing.assert_array_equal(line.get_ydata(), expected)
        assert not np.array_equal(expected, np.cumprod(1 + run.daily) - 1)

    def test_a_scale_break_in_tu_is_refused_through_main(self, monkeypatch, tmp_path) -> None:
        """The figure reads through ``read_sources``, so the real guard runs on its path.
        TU's closes are multiplied by 10 from row 1000, a break the guard must flag. The
        default directory is pointed at ``tmp_path``, so a figure that drew past the guard
        cannot overwrite the committed one."""
        members, panel = load_panel(SOURCE_FILE)
        broken = panel.copy()
        tu = broken[SYMBOL].dropna()
        broken.loc[tu.index[1000:], SYMBOL] *= 10
        monkeypatch.setattr(tu_momentum, "load_panel", lambda *_a, **_k: (members, broken))
        monkeypatch.setattr(coin_flip_figures, "FIGURES_DIR", tmp_path)
        with pytest.raises(WindowCrossesScaleBreak, match="tu.csv"):
            make_tu_figure(out=tmp_path / TU_FIGURE)
        with pytest.raises(SystemExit) as stopped:
            main()
        message = str(stopped.value)
        assert "tu.csv" in message
        assert "\n" not in message

    def test_a_missing_vintage_reaches_the_operator_as_one_line(
        self, monkeypatch, tmp_path
    ) -> None:
        """The manifest is copied and the closes are not, so the refusal is the one a
        checkout without the files meets."""
        shutil.copy(paths.DATA_DIR / "vintages.jsonl", tmp_path)
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit) as stopped:
            main()
        message = str(stopped.value)
        assert message.startswith("inputdataohlcdaily_20120511/")
        assert "no file is at" in message
        assert "\n" not in message

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage of TU saved 2012-05-12"),
            WindowCrossesScaleBreak("inputdataohlcdaily_20120511/tu.csv changes scale"),
        ],
    )
    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(figures, "make_tu_figure", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)

    def test_any_other_error_keeps_its_traceback(self, monkeypatch) -> None:
        def broken(*_a, **_k):
            raise KeyError("Close")

        monkeypatch.setattr(figures, "make_tu_figure", broken)
        with pytest.raises(KeyError, match="Close"):
            main()

    def test_the_command_writes_the_committed_path(self, monkeypatch, capsys) -> None:
        drawn = []
        monkeypatch.setattr(figures, "make_tu_figure", lambda **kw: drawn.append(kw))
        main()
        assert drawn == [{}]
        assert f"wrote {FIGURES_DIR / TU_FIGURE}" in capsys.readouterr().out

    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.is_file() and out.stat().st_size > 0


def test_the_committed_figure_exists() -> None:
    assert (FIGURES_DIR / TU_FIGURE).is_file()
