"""The pins for the cross-sectional momentum post's one figure.

``tests/test_cross_sectional_momentum.py`` holds what the run computes. This
file holds that the figure draws those numbers, so a generator that plotted the
wrong series, sliced a window differently or marked the wrong trough fails even
when the arithmetic is right. Some numbers repeat here on purpose, because a
figure's labels are prose and the suite is the authority for every number prose
quotes. No test compares bytes, for the reason ``tests/test_regime_figure.py``
gives.

The figure reads the vintage and the specification
``tests/test_cross_sectional_momentum.py`` names as its ``SPEC``, which every
failure message here carries too.

Four things are pinned here and nowhere else.

1. Each window's deepest drawdown, the high it fell from and the trough.
2. That the 2008 and 2009 spell below the high runs from 2008-07-15 to the
   window's last day, so it was still running when the window ended.
3. That in 2007 and in 2010 to 2012 the deepest drawdown falls outside the
   longest spell, which is why the figure marks the drawdown.
4. Each panel's last value, the compounded figure carried back over its days.

Exploratory, like everything Example 6.2 computes here.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from matplotlib.colors import same_color
from matplotlib.dates import DateFormatter, MonthLocator, YearLocator, date2num, num2date

from chan import cross_sectional_momentum
from chan.cross_sectional_momentum import WINDOWS, read_closes, script_as_printed, window_figures
from chan.cross_sectional_momentum_figures import (
    CUMULATIVE_FIGURE,
    Drawdown,
    deepest_drawdown,
    main,
    make_cumulative_figure,
    panel_heading,
    panels,
)
from chan.matlab_helpers import calculate_max_dd
from chan.paths import FIGURES_DIR
from chan.pead_figures import longest_spell
from chan.regime_figure import LOST
from chan.vintage import VintageUnavailable
from tests.test_cross_sectional_momentum import SPEC

#: Each window's deepest drawdown: the high, the trough and the depth.
DEEPEST = {
    "2007": ("2007-11-07", "2007-11-13", -0.033870),
    "2008-2009": ("2008-07-14", "2009-09-22", -0.606634),
    "2010-2012": ("2011-09-22", "2012-02-06", -0.095556),
}

#: Each window's last cumulative value, at six decimals.
ENDS = {"2007": 0.222714, "2008-2009": -0.508995, "2010-2012": 0.030382}

#: Each window's longest spell below the high, where it is not the deepest
#: drawdown's: its first and last days, its length and its trough's depth.
SPELLS_ELSEWHERE = {
    "2007": ("2007-07-20", "2007-08-21", 23, -0.021110),
    "2010-2012": ("2010-12-02", "2011-09-01", 190, -0.066993),
}


@pytest.fixture(scope="module")
def closes() -> pd.DataFrame:
    return read_closes()[1]


@pytest.fixture(scope="module")
def drawn(closes):
    return panels(closes)


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("cross_sectional_momentum_figure") / CUMULATIVE_FIGURE


@pytest.fixture(scope="module")
def figure(out, closes):
    return make_cumulative_figure(out=out, closes=closes)


@pytest.fixture(scope="module")
def pairs(figure, drawn):
    """Each axes beside the panel it should draw, left to right."""
    return list(zip(figure.axes, drawn, strict=True))


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _texts(ax) -> dict:
    return {t.get_gid(): t.get_text() for t in ax.texts if t.get_gid()}


def _day(days, row: int) -> str:
    return str(days[row].date())


class TestThePanels:
    def test_there_are_three_in_the_scripts_order(self, figure, drawn) -> None:
        assert len(figure.axes) == 3
        assert [p.window for p in drawn] == list(WINDOWS) == ["2007", "2008-2009", "2010-2012"]

    def test_they_share_the_y_axis(self, figure) -> None:
        """So the 2008 and 2009 loss reads on the 2007 gain's scale."""
        first, *rest = figure.axes
        for ax in rest:
            assert ax.get_ylim() == first.get_ylim()
            assert first.get_shared_y_axes().joined(first, ax)

    def test_their_widths_follow_their_days(self, figure) -> None:
        """160, 505 and 582 days, so a day is the same width in every panel."""
        widths = [ax.get_position().width for ax in figure.axes]
        for width, days in zip(widths, (160, 505, 582), strict=True):
            assert width / widths[0] == pytest.approx(days / 160, rel=1e-6)

    def test_each_heading_names_its_window_figures_and_book(self, figure) -> None:
        headings = [ax.get_title(loc="left") for ax in figure.axes]
        assert headings == [
            "2007-05-15 to\n2007-12-31\ncompounded 0.372577\narithmetic 0.319989\n"
            "Sharpe ratio 4.0657\nThe book prints\n37 percent and 4.1.",
            "2008-01-02 to\n2009-12-31\ncompounded −0.298789\narithmetic −0.323195\n"
            "Sharpe ratio −1.2930\nThe book prints\n−30 percent.",
            "2010-01-04 to\n2012-04-24\ncompounded 0.013043\narithmetic 0.016244\n"
            'Sharpe ratio 0.2004\nThe book says it\n"did stabilize".',
        ], SPEC

    def test_the_heading_reads_the_panel_it_is_given(self, drawn) -> None:
        assert "compounded −0.298789" in panel_heading(drawn[1])
        assert panel_heading(drawn[0]).startswith("2007-05-15 to")


class TestTheLines:
    """Each line is ``cumprod(1 + ret) − 1`` over its own window, from zero."""

    def test_each_runs_over_its_windows_days(self, closes, pairs) -> None:
        daily = script_as_printed(closes.to_numpy())
        for ax, panel in pairs:
            line = _by_gid(ax.lines)["cumulative"]
            expected = window_figures(daily, pd.DatetimeIndex(closes.index), panel.window).days
            assert list(line.get_xdata()) == list(expected), SPEC

    def test_each_values_are_the_cumulative_return(self, closes, pairs) -> None:
        daily = script_as_printed(closes.to_numpy())
        days = pd.DatetimeIndex(closes.index)
        for ax, panel in pairs:
            start, end = (pd.Timestamp(each) for each in WINDOWS[panel.window])
            r = daily[(days >= start) & (days <= end)]
            line = _by_gid(ax.lines)["cumulative"]
            expected = np.cumprod(1 + r) - 1
            assert list(line.get_ydata()) == pytest.approx(list(expected), abs=1e-12), SPEC

    def test_each_ends_where_its_compounded_figure_says(self, pairs) -> None:
        """The last value is the compounded figure carried back over the window's
        days, which ties each panel to a pinned figure."""
        for ax, panel in pairs:
            last = _by_gid(ax.lines)["cumulative"].get_ydata()[-1]
            n = len(panel.days)
            assert last == pytest.approx(
                (1 + panel.figures.compounded_apr) ** (n / 252) - 1, abs=1e-12
            ), SPEC
            assert last == pytest.approx(ENDS[panel.window], abs=5e-7), SPEC

    def test_the_axes_hold_every_point_and_read_in_percent(self, figure, pairs) -> None:
        low, high = figure.axes[0].get_ylim()
        for _, panel in pairs:
            assert low < panel.cumret.min() and high > panel.cumret.max()
        assert figure.axes[0].yaxis.get_major_formatter().xmax == 1.0

    def test_the_limits_leave_room_for_the_labels(self, figure, drawn) -> None:
        """22 percent of the joint span on each side, where the high and trough labels sit."""
        low = min(p.cumret.min() for p in drawn)
        high = max(p.cumret.max() for p in drawn)
        span = high - low
        assert figure.axes[0].get_ylim() == pytest.approx(
            (low - 0.22 * span, high + 0.22 * span), abs=1e-12
        )

    def test_each_x_axis_is_its_windows_dates(self, pairs) -> None:
        """A panel drawn against row numbers would still pass the value checks."""
        for ax, panel in pairs:
            start, end = ax.get_xlim()
            assert num2date(start).date() == panel.days[0].date()
            assert num2date(end).date() == panel.days[-1].date()

    def test_the_ticks_read_as_months_then_years(self, figure) -> None:
        first, *rest = (ax.xaxis for ax in figure.axes)
        assert isinstance(first.get_major_locator(), MonthLocator)
        assert first.get_major_formatter().fmt == "%b"
        for axis in rest:
            assert isinstance(axis.get_major_locator(), YearLocator)
            assert isinstance(axis.get_major_formatter(), DateFormatter)
            assert axis.get_major_formatter().fmt == "%Y"


class TestTheDeepestDrawdowns:
    """Each window's deepest drawdown, marked where ``calculateMaxDD`` finds it."""

    @pytest.mark.parametrize("window", list(WINDOWS))
    def test_each_falls_where_the_figure_says(self, drawn, window: str) -> None:
        (panel,) = [p for p in drawn if p.window == window]
        high, trough, depth = DEEPEST[window]
        deepest = deepest_drawdown(panel.cumret)
        assert (_day(panel.days, deepest.high), _day(panel.days, deepest.trough)) == (
            high,
            trough,
        ), SPEC
        assert deepest.depth == pytest.approx(panel.figures.max_drawdown, abs=1e-12), SPEC
        assert deepest.depth == pytest.approx(depth, abs=5e-7), SPEC

    def test_the_high_and_the_trough_are_marked_on_each_line(self, pairs) -> None:
        for ax, panel in pairs:
            marks = _by_gid(ax.lines)
            for gid, row in (("high", ax.deepest.high), ("trough", ax.deepest.trough)):
                assert list(marks[gid].get_xdata()) == [panel.days[row]]
                assert list(marks[gid].get_ydata()) == [panel.cumret[row]]

    def test_the_labels_name_each_high_and_drawdown(self, figure) -> None:
        labels = [_texts(ax) for ax in figure.axes]
        for texts, (high, trough, depth) in zip(labels, DEEPEST.values(), strict=True):
            assert texts["high-label"] == f"high,\n{high}"
            assert texts["trough-label"] == (
                f"deepest drawdown\n{depth:f}".replace("-", "−") + f",\n{trough}"
            )

    def test_each_label_points_at_the_row_it_names(self, pairs) -> None:
        """The text alone would pass with the arrow anchored at the wrong day."""
        for ax, panel in pairs:
            notes = {a.get_gid(): a for a in ax.texts if a.get_gid()}
            for gid, row in (("high-label", ax.deepest.high), ("trough-label", ax.deepest.trough)):
                x, y = notes[gid].xy
                assert date2num(x) == date2num(panel.days[row]), gid
                assert y == panel.cumret[row], gid

    def test_the_trough_is_marked_in_lost_and_the_high_in_the_line_s_colour(self, figure) -> None:
        """Colour ties each point to its label, and only the fall wears the loss colour."""
        for ax in figure.axes:
            marks, notes = _by_gid(ax.lines), _by_gid(ax.texts)
            line = marks["cumulative"].get_color()
            for gid, colour in (("high", line), ("trough", LOST)):
                assert same_color(marks[gid].get_markerfacecolor(), colour), gid
                assert same_color(notes[f"{gid}-label"].get_color(), colour), gid
            assert not same_color(marks["high"].get_markerfacecolor(), LOST)


class TestTheSpell:
    """The 2008 and 2009 spell below the high, the one duration the post quotes."""

    def test_it_runs_371_days_to_the_windows_last_day(self, drawn) -> None:
        panel = drawn[1]
        spell = longest_spell(panel.cumret)
        assert spell.rows == panel.figures.max_drawdown_days == 371, SPEC
        assert (_day(panel.days, spell.first), _day(panel.days, spell.last)) == (
            "2008-07-15",
            "2009-12-31",
        ), SPEC
        assert spell.last == len(panel.days) - 1, SPEC
        assert spell.first <= deepest_drawdown(panel.cumret).trough <= spell.last, SPEC

    def test_it_is_still_below_the_high_on_the_last_day(self, drawn) -> None:
        panel = drawn[1]
        high = panel.cumret[longest_spell(panel.cumret).high]
        assert panel.cumret[-1] < high, SPEC

    def test_it_is_shaded_on_that_panel_alone(self, pairs) -> None:
        for ax, panel in pairs:
            band = _by_gid(ax.patches).get("spell")
            if panel.window != "2008-2009":
                assert band is None
                continue
            low, high = band.get_x(), band.get_x() + band.get_width()
            rows = [i for i, day in enumerate(date2num(panel.days)) if low <= day <= high]
            assert rows == list(range(ax.spell.first, ax.spell.last + 1)), SPEC

    def test_its_label_says_it_was_still_running(self, figure) -> None:
        texts = [_texts(ax) for ax in figure.axes]
        assert texts[1]["spell-label"] == (
            "371 days below the high,\n2008-07-15 to 2009-12-31,\n"
            "still running when the window ends"
        )
        assert "spell-label" not in texts[0] and "spell-label" not in texts[2]

    def test_the_band_and_its_label_wear_lost(self, figure) -> None:
        """The colour is what ties the label to the shaded days below the high."""
        ax = figure.axes[1]
        band = _by_gid(ax.patches)["spell"]
        assert same_color(band.get_facecolor()[:3], LOST)
        assert band.get_alpha() < 1, "the line must show through the band"
        assert same_color(_by_gid(ax.texts)["spell-label"].get_color(), LOST)

    @pytest.mark.parametrize("window", list(SPELLS_ELSEWHERE))
    def test_elsewhere_the_deepest_drawdown_falls_outside_the_longest_spell(
        self, drawn, window: str
    ) -> None:
        """What the figure's choice to mark the drawdown rests on."""
        (panel,) = [p for p in drawn if p.window == window]
        first, last, rows, depth = SPELLS_ELSEWHERE[window]
        spell = longest_spell(panel.cumret)
        deepest = deepest_drawdown(panel.cumret)
        assert (_day(panel.days, spell.first), _day(panel.days, spell.last)) == (first, last)
        assert spell.rows == panel.figures.max_drawdown_days == rows, SPEC
        assert spell.depth == pytest.approx(depth, abs=5e-7), SPEC
        assert not spell.first <= deepest.trough <= spell.last, SPEC
        assert deepest.depth < spell.depth


class TestDeepestDrawdown:
    """The helper on series small enough to read."""

    def test_it_finds_the_trough_and_the_high_before_it(self) -> None:
        cumret = np.array([0.0, 0.1, 0.05, 0.2, 0.1, -0.1, 0.0, 0.3])
        found = deepest_drawdown(cumret)
        assert found == Drawdown(high=3, trough=5, depth=pytest.approx(0.9 / 1.2 - 1))
        assert found.depth == pytest.approx(calculate_max_dd(cumret)[0])

    def test_a_high_held_on_equal_value_is_the_later_row(self) -> None:
        """A day back at the high has a drawdown of 0 and resets the duration."""
        cumret = np.array([0.0, 0.1, 0.1, 0.0])
        assert deepest_drawdown(cumret).high == 2

    def test_the_first_of_two_equal_troughs_is_taken(self) -> None:
        cumret = np.array([0.0, 0.1, 0.0, 0.1, 0.0])
        assert deepest_drawdown(cumret) == Drawdown(
            high=1, trough=2, depth=pytest.approx(1 / 1.1 - 1)
        )

    def test_a_fall_from_the_start_counts_from_row_0(self) -> None:
        """``calculateMaxDD``'s high starts at 0, so a window opening on a fall falls from row 0."""
        cumret = np.array([0.0, -0.1, -0.2, -0.1])
        assert deepest_drawdown(cumret) == Drawdown(high=0, trough=2, depth=pytest.approx(-0.2))

    def test_a_window_opening_below_zero_still_falls_from_row_0(self) -> None:
        """Row 0's drawdown is forced to 0, so a later row above row 0 but below
        zero is not a new high. Reading the high as the largest value before the
        trough would put it on row 1 here."""
        cumret = np.array([-0.05, -0.01, -0.2])
        assert deepest_drawdown(cumret).high == 0


class TestTheWords:
    def test_the_title_carries_the_exploratory_label(self, figure) -> None:
        title = figure._suptitle.get_text()
        assert title.startswith("Exploratory:")
        assert "kentdaniel.m" in title and "one run per window" in title

    def test_the_note_names_the_file_the_restart_and_the_survivors(self, figure) -> None:
        note = figure.texts[-1].get_text()
        assert "inputDataOHLCDaily_stocks_20120424.mat" in note
        assert "50 highest and 50 lowest 252-day returns" in note
        assert "held 25 days, unlevered and before costs" in note
        assert "restarts at zero on its window's first day" in note
        assert "every stock is a survivor" in note

    def test_no_label_is_parsed_as_math(self, figure) -> None:
        for text in [*(t for ax in figure.axes for t in ax.texts), *figure.texts]:
            assert text.get_parse_math() is False


class TestTheReadPath:
    def test_the_default_path_reads_the_runs_closes(self, monkeypatch, tmp_path, closes) -> None:
        """With no closes handed in, the figure reads ``read_closes``, the run's path."""
        import chan.cross_sectional_momentum_figures as figures

        asked = []

        def read(data_dir=None):
            asked.append(True)
            return [], closes

        monkeypatch.setattr(figures, "read_closes", read)
        drawn = make_cumulative_figure(out=tmp_path / CUMULATIVE_FIGURE)
        assert asked == [True]
        assert list(drawn.axes[2].cumret) == list(panels(closes)[2].cumret)

    def test_closes_handed_in_are_the_closes_drawn(self, tmp_path, closes) -> None:
        """Half the stocks jump by half in 2009, so a figure that ignored the
        argument and read the file would fail."""
        changed = closes.copy()
        changed.iloc[700:, ::2] *= 1.5
        drawn = make_cumulative_figure(out=tmp_path / CUMULATIVE_FIGURE, closes=changed)
        assert list(drawn.axes[1].cumret) == list(panels(changed)[1].cumret)
        assert list(drawn.axes[1].cumret) != list(panels(closes)[1].cumret)

    def test_the_figure_and_the_run_slice_each_window_by_one_rule(
        self, monkeypatch, tmp_path, closes
    ) -> None:
        """Both go through ``window_returns``, so they cannot disagree on a window's days."""
        import chan.cross_sectional_momentum_figures as figures

        asked = []
        real = cross_sectional_momentum.window_returns

        def spy(daily, days, window):
            asked.append(window)
            return real(daily, days, window)

        monkeypatch.setattr(figures, "window_returns", spy)
        monkeypatch.setattr(cross_sectional_momentum, "window_returns", spy)
        make_cumulative_figure(out=tmp_path / CUMULATIVE_FIGURE, closes=closes)
        assert asked.count("2007") == asked.count("2008-2009") == asked.count("2010-2012") == 2

    def test_any_other_error_keeps_its_traceback(self, monkeypatch) -> None:
        """Only a missing vintage becomes one line. A bug must surface as itself."""
        import chan.cross_sectional_momentum_figures as figures

        def broken(data_dir=None):
            raise KeyError("Close")

        monkeypatch.setattr(figures, "read_closes", broken)
        with pytest.raises(KeyError, match="Close"):
            main()

    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.is_file()

    def test_a_missing_vintage_reaches_the_operator_as_one_line(self, monkeypatch) -> None:
        import chan.cross_sectional_momentum_figures as figures

        def refuse(data_dir=None):
            raise VintageUnavailable("no committed vintage is lifted from inputDataOHLCDaily")

        monkeypatch.setattr(figures, "read_closes", refuse)
        with pytest.raises(SystemExit, match="no committed vintage is lifted from inputData"):
            main()

    def test_the_command_writes_the_committed_path(self, monkeypatch, capsys) -> None:
        import chan.cross_sectional_momentum_figures as figures

        drawn = []
        monkeypatch.setattr(figures, "make_cumulative_figure", lambda **kw: drawn.append(kw))
        main()
        assert drawn == [{}]
        assert f"wrote {FIGURES_DIR / CUMULATIVE_FIGURE}" in capsys.readouterr().out


def test_the_committed_figure_exists() -> None:
    assert (FIGURES_DIR / CUMULATIVE_FIGURE).is_file()
