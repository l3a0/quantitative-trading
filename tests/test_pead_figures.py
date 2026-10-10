"""The pins for the post-earnings drift post's one figure.

``tests/test_pead.py`` holds what the run computes. This file holds that the
figure draws those numbers, so a generator that plotted the wrong series or
shaded the wrong days fails even when the arithmetic is right. Some numbers
repeat here on purpose, because a figure's labels are prose and the suite is
the authority for every number prose quotes. No test compares bytes, for the
reason ``tests/test_regime_figure.py`` gives.

The figure reads the vintages and the specification ``tests/test_pead.py``
names as its ``SPEC``, which every failure message here carries too.

Three things are pinned here and nowhere else.

1. The dates of the longest spell below the high.
2. The high it falls from.
3. That the deepest drawdown sits inside it.

``calculateMaxDD`` returns the deepest drawdown and the longest
duration separately, and the two need not share a spell, so the figure
finding them together is a fact about this run rather than about the helper.

Exploratory, like everything Example 7.2 computes here.
"""

from __future__ import annotations

import numpy as np
import pytest
from matplotlib.colors import same_color
from matplotlib.dates import date2num, num2date

from chan import pead
from chan.paths import FIGURES_DIR
from chan.pead import LOOKBACK, SCRIPT_MAX_DD, SCRIPT_MAX_DDD, guarded_drift
from chan.pead_figures import (
    CUMULATIVE_FIGURE,
    LOST,
    RULE,
    cumulative_return,
    longest_spell,
    main,
    make_cumulative_figure,
)
from chan.vintage import VintageUnavailable
from tests.test_pead import SPEC


@pytest.fixture(scope="module")
def drift():
    return guarded_drift()[2]


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("pead_figure") / CUMULATIVE_FIGURE


@pytest.fixture(scope="module")
def figure(out, drift):
    return make_cumulative_figure(out=out, drift=drift)


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _span_rows(span, days) -> list[int]:
    """The rows of ``days`` whose date lies inside a shaded band."""
    low, high = span.get_x(), span.get_x() + span.get_width()
    return [i for i, day in enumerate(date2num(days)) if low <= day <= high]


def _day(drift, row: int) -> str:
    return str(drift.days[row].date())


class TestTheLine:
    """The line is ``pead.m``'s ``cumprod(1 + ret) − 1`` over the 330 days."""

    def test_it_runs_over_the_flag_files_days(self, figure, drift) -> None:
        line = _by_gid(figure.axes[0].lines)["cumulative"]
        assert list(line.get_xdata()) == list(drift.days), SPEC
        assert len(drift.days) == 330, SPEC

    def test_its_values_are_the_cumulative_return(self, figure, drift) -> None:
        line = _by_gid(figure.axes[0].lines)["cumulative"]
        expected = np.cumprod(1 + drift.daily) - 1
        assert list(line.get_ydata()) == pytest.approx(list(expected), abs=1e-12), SPEC
        assert cumulative_return(drift) == pytest.approx(expected, abs=1e-12), SPEC

    def test_it_ends_where_the_compounded_apr_says(self, figure, drift) -> None:
        """The last value is the compounded APR carried back over 330 of 252 days,
        which ties the line to the pinned 0.067952."""
        last = _by_gid(figure.axes[0].lines)["cumulative"].get_ydata()[-1]
        assert drift.compounded_apr == pytest.approx(0.067952, abs=5e-7), SPEC
        assert last == pytest.approx((1 + drift.compounded_apr) ** (330 / 252) - 1, abs=1e-12)

    def test_the_axes_hold_every_point_and_read_in_percent(self, figure) -> None:
        ax, cumret = figure.axes[0], figure.cumret
        low, high = ax.get_ylim()
        assert low < cumret.min() and high > cumret.max()
        assert ax.yaxis.get_major_formatter().xmax == 1.0


class TestTheSpell:
    """The longest spell below the high, which ``calculateMaxDD`` measures as 109 days."""

    def test_it_runs_109_rows_from_2011_08_05_to_2012_01_10(self, drift) -> None:
        spell = longest_spell(cumulative_return(drift))
        assert spell.rows == SCRIPT_MAX_DDD == drift.max_drawdown_days == 109, SPEC
        assert (_day(drift, spell.first), _day(drift, spell.last)) == (
            "2011-08-05",
            "2012-01-10",
        ), SPEC

    def test_it_falls_from_the_high_of_2011_08_04(self, drift) -> None:
        cumret = cumulative_return(drift)
        spell = longest_spell(cumret)
        assert spell.high == spell.first - 1
        assert _day(drift, spell.high) == "2011-08-04", SPEC
        assert cumret[spell.high] == cumret[: spell.first].max(), SPEC

    def test_the_deepest_drawdown_sits_inside_it_on_2011_11_02(self, drift) -> None:
        spell = longest_spell(cumulative_return(drift))
        assert spell.first <= spell.trough <= spell.last
        assert _day(drift, spell.trough) == "2011-11-02", SPEC
        assert spell.depth == pytest.approx(drift.max_drawdown, abs=1e-12), SPEC

    def test_the_shaded_spell_covers_its_rows(self, figure, drift) -> None:
        spell = figure.spell
        band = _by_gid(figure.axes[0].patches)["spell"]
        assert _span_rows(band, drift.days) == list(range(spell.first, spell.last + 1)), SPEC

    def test_the_high_and_the_trough_are_marked_on_the_line(self, figure, drift) -> None:
        marks = _by_gid(figure.axes[0].lines)
        cumret, spell = figure.cumret, figure.spell
        for gid, row in (("high", spell.high), ("trough", spell.trough)):
            assert list(marks[gid].get_xdata()) == [drift.days[row]]
            assert list(marks[gid].get_ydata()) == [cumret[row]]

    def test_the_labels_name_the_spell_the_high_and_the_drawdown(self, figure) -> None:
        texts = {t.get_gid(): t.get_text() for t in figure.axes[0].texts}
        assert texts["spell-label"] == "109 days below the high,\n2011-08-05 to 2012-01-10"
        assert texts["high-label"] == "high, 2011-08-04"
        assert texts["trough-label"] == (
            f"deepest drawdown {SCRIPT_MAX_DD.replace('-', '−')},\n2011-11-02"
        )

    def test_the_spell_is_shaded_in_lost(self, figure) -> None:
        """The post's caption calls it the red band, against the idle start's grey."""
        band = _by_gid(figure.axes[0].patches)["spell"]
        assert same_color(band.get_facecolor()[:3], LOST)

    def test_the_trough_and_the_spell_labels_wear_the_spells_colour(self, figure) -> None:
        """The red point and its label belong to the spell, and the high belongs to the line."""
        ax = figure.axes[0]
        marks, texts = _by_gid(ax.lines), _by_gid(ax.texts)
        for artist in (marks["trough"], texts["trough-label"], texts["spell-label"]):
            assert same_color(artist.get_color(), LOST)
        assert same_color(marks["high"].get_color(), marks["cumulative"].get_color())
        assert same_color(texts["high-label"].get_color(), marks["cumulative"].get_color())
        assert not same_color(marks["high"].get_color(), marks["trough"].get_color())

    def test_a_tie_takes_the_first_spell(self) -> None:
        """Two dips of two rows each, so the first is the one drawn."""
        cumret = np.array([0.0, 0.1, 0.05, 0.06, 0.2, 0.15, 0.1, 0.3])
        spell = longest_spell(cumret)
        assert (spell.high, spell.first, spell.last, spell.rows) == (1, 2, 3, 2)
        assert spell.trough == 2


class TestTheIdleStart:
    """The first 89 rows, which ``test_no_stock_trades_before_its_window_fills`` holds empty."""

    def test_the_band_covers_exactly_the_rows_with_no_position(self, figure, drift) -> None:
        band = _by_gid(figure.axes[0].patches)["unfilled"]
        rows = _span_rows(band, drift.days)
        assert rows == list(range(LOOKBACK - 1)), SPEC
        assert not drift.positions[rows].any(), SPEC
        assert drift.positions[LOOKBACK - 1 :].any(), SPEC

    def test_it_is_shaded_in_rule_apart_from_the_spell(self, figure) -> None:
        """The post's caption calls it the grey band, and the red one is the spell."""
        bands = _by_gid(figure.axes[0].patches)
        assert same_color(bands["unfilled"].get_facecolor()[:3], RULE)
        assert not same_color(bands["unfilled"].get_facecolor()[:3], LOST)

    def test_its_label_is_not_the_spells_colour(self, figure) -> None:
        """Red text in the grey band would read as part of the spell."""
        label = _by_gid(figure.axes[0].texts)["unfilled-label"]
        assert not same_color(label.get_color(), LOST)

    def test_its_label_names_the_89_days(self, figure) -> None:
        text = {t.get_gid(): t.get_text() for t in figure.axes[0].texts}["unfilled-label"]
        assert text == "no position in the first 89 days,\nbefore the 90-day deviation fills"


class TestTheWords:
    def test_the_title_carries_the_exploratory_label(self, figure) -> None:
        title = figure._suptitle.get_text()
        assert title.startswith("Exploratory:")
        assert "redrawn" in title

    def test_the_note_names_both_vintages_and_the_survivors(self, figure) -> None:
        note = figure.texts[-1].get_text()
        assert "2011-01-03 to 2012-04-24" in note
        assert "over 30, unlevered and before costs" in note
        assert "inputDataOHLCDaily_stocks_20120424.mat" in note
        assert "earnannFile.mat" in note
        assert "every stock is a survivor" in note

    def test_no_label_is_parsed_as_math(self, figure) -> None:
        for text in [*figure.axes[0].texts, *figure.texts]:
            assert text.get_parse_math() is False


class TestTheReadPath:
    def test_the_default_path_runs_the_scale_break_guard(
        self, monkeypatch, tmp_path, drift
    ) -> None:
        """The figure reads through ``guarded_drift``, so it cannot skip the guard
        Example 7.2's run calls."""
        sources = pead.read_sources()
        asked = []
        monkeypatch.setattr(pead, "read_sources", lambda data_dir=None: sources)
        monkeypatch.setattr(pead, "refuse_scale_breaks", lambda *args: asked.append(args[3]))
        drawn = make_cumulative_figure(out=tmp_path / CUMULATIVE_FIGURE)
        (days,) = asked
        assert days.equals(sources[4].index)
        assert list(drawn.cumret) == pytest.approx(list(cumulative_return(drift)), abs=1e-15)

    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.is_file()

    def test_a_missing_vintage_reaches_the_operator_as_one_line(self, monkeypatch) -> None:
        import chan.pead_figures as figures

        def refuse(data_dir=None):
            raise VintageUnavailable("no committed vintage is lifted from earnannFile.mat")

        monkeypatch.setattr(figures, "guarded_drift", refuse)
        with pytest.raises(SystemExit, match="no committed vintage is lifted from earnannFile"):
            main()

    def test_the_command_writes_the_committed_path(self, monkeypatch, capsys) -> None:
        import chan.pead_figures as figures

        drawn = []
        monkeypatch.setattr(figures, "make_cumulative_figure", lambda **kw: drawn.append(kw))
        main()
        assert drawn == [{}]
        assert f"wrote {FIGURES_DIR / CUMULATIVE_FIGURE}" in capsys.readouterr().out


def test_the_committed_figure_exists() -> None:
    assert (FIGURES_DIR / CUMULATIVE_FIGURE).is_file()


def test_the_x_axis_is_dates(figure, drift) -> None:
    """A figure drawn against row numbers would still pass the value checks."""
    start, end = figure.axes[0].get_xlim()
    assert num2date(start).date() == drift.days[0].date()
    assert num2date(end).date() == drift.days[-1].date()
