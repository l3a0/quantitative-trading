"""The pins for the buy-on-gap post's one figure.

``tests/test_buy_on_gap.py`` holds what the run computes. This file holds that
the figure draws those numbers, so a generator that plotted the wrong series,
swapped the panels or shaded the wrong days fails even when the arithmetic is
right. Some numbers repeat here on purpose, because a figure's labels are
prose and the suite is the authority for every number prose quotes. No test
compares bytes, for the reason ``tests/test_regime_figure.py`` gives.

The figure reads the vintage and the specification ``tests/test_buy_on_gap.py``
names as its ``SPEC``, which every failure message here carries too.

Three things are pinned here and nowhere else, for each side.

1. The dates of the longest spell below the high.
2. The high it falls from.
3. That the deepest drawdown sits inside it, and on which day.

``calculateMaxDD`` returns the deepest drawdown and the longest duration
separately, and the two need not share a spell, so the figure finding them
together on both sides is a fact about this run rather than about the helper.

Exploratory, like everything Example 4.1 computes here. The bottom panel is
the mirror issue 295 declared, not a rule Chan published.
"""

from __future__ import annotations

import numpy as np
import pytest
from matplotlib.dates import date2num, num2date

from chan import buy_on_gap
from chan.buy_on_gap import SPREAD_LOOKBACK, both_sides
from chan.buy_on_gap_figures import CUMULATIVE_FIGURE, main, make_cumulative_figure, panel_heading
from chan.paths import FIGURES_DIR
from chan.pead_figures import cumulative_return, longest_spell
from chan.vintage import VintageUnavailable
from tests.test_buy_on_gap import SPEC

#: Each side's longest spell as the figure draws it: the high, the spell's
#: first and last days, the trough, the depth, and the spell's length in days.
SPELLS = {
    "buy on gap": ("2008-08-29", "2008-09-02", "2009-04-20", "2008-12-09", -0.052459, 159),
    "short on gap": ("2008-11-21", "2008-11-24", "2010-05-05", "2009-02-03", -0.064928, 363),
}


@pytest.fixture(scope="module")
def sides():
    return both_sides()[1:]


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("buy_on_gap_figure") / CUMULATIVE_FIGURE


@pytest.fixture(scope="module")
def figure(out, sides):
    return make_cumulative_figure(out=out, sides=sides)


@pytest.fixture(scope="module")
def panels(figure, sides):
    """Each axes beside the side it should draw, top then bottom."""
    return list(zip(figure.axes, sides, strict=True))


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _texts(ax) -> dict:
    return {t.get_gid(): t.get_text() for t in ax.texts if t.get_gid()}


def _span_rows(span, days) -> list[int]:
    """The rows of ``days`` whose date lies inside a shaded band."""
    low, high = span.get_x(), span.get_x() + span.get_width()
    return [i for i, day in enumerate(date2num(days)) if low <= day <= high]


def _day(side, row: int) -> str:
    return str(side.days[row].date())


class TestThePanels:
    def test_there_are_two_and_buy_on_gap_is_on_top(self, figure, sides) -> None:
        long, short = sides
        assert len(figure.axes) == 2
        assert (long.name, short.name) == ("buy on gap", "short on gap")
        top, bottom = figure.axes
        assert top.get_title(loc="left").startswith("Figure 4.1: buy on gap")
        assert bottom.get_title(loc="left").startswith("Where Figure 4.2 stands: short on gap")

    def test_they_share_both_axes(self, figure) -> None:
        """So the mirror's drawdown and its return read on the buy side's scale."""
        top, bottom = figure.axes
        assert top.get_ylim() == bottom.get_ylim()
        assert top.get_xlim() == bottom.get_xlim()
        assert top.get_shared_y_axes().joined(top, bottom)

    def test_each_heading_sets_both_figures_beside_the_books(self, figure) -> None:
        top, bottom = (ax.get_title(loc="left") for ax in figure.axes)
        assert top == (
            "Figure 4.1: buy on gap, as bog.m runs it.\n"
            "APR 0.087385 and Sharpe ratio 1.5371, where the book prints 8.7 percent and 1.5."
        ), SPEC
        assert bottom == (
            "Where Figure 4.2 stands: short on gap, the mirror as declared here.\n"
            "APR 0.122030 and Sharpe ratio 1.7853, where the book prints 46 percent and 1.27."
        ), SPEC

    def test_the_heading_reads_the_side_it_is_given(self, sides) -> None:
        long, _ = sides
        assert "APR 0.087385" in panel_heading(long, mirror=False)
        assert "46 percent" in panel_heading(long, mirror=True)


class TestTheLines:
    """Each line is ``cumprod(1 + ret) − 1`` over the 1,500 days."""

    def test_each_runs_over_the_files_days(self, panels) -> None:
        for ax, side in panels:
            line = _by_gid(ax.lines)["cumulative"]
            assert list(line.get_xdata()) == list(side.days), SPEC
            assert len(side.days) == 1500, SPEC

    def test_each_values_are_the_cumulative_return(self, panels) -> None:
        for ax, side in panels:
            line = _by_gid(ax.lines)["cumulative"]
            expected = np.cumprod(1 + side.daily) - 1
            assert list(line.get_ydata()) == pytest.approx(list(expected), abs=1e-12), SPEC

    def test_each_ends_where_its_apr_says(self, panels) -> None:
        """The last value is the APR carried back over 1,500 of 252 days, which
        ties each line to its pinned APR."""
        for (ax, side), apr in zip(panels, (0.087385, 0.122030), strict=True):
            last = _by_gid(ax.lines)["cumulative"].get_ydata()[-1]
            assert side.apr == pytest.approx(apr, abs=5e-7), SPEC
            assert last == pytest.approx((1 + side.apr) ** (1500 / 252) - 1, abs=1e-12), SPEC

    def test_the_axes_hold_every_point_and_read_in_percent(self, figure, panels) -> None:
        low, high = figure.axes[0].get_ylim()
        for ax, _ in panels:
            assert low < ax.cumret.min() and high > ax.cumret.max()
            assert ax.yaxis.get_major_formatter().xmax == 1.0


class TestTheSpells:
    """The longest spell below the high on each side, 159 days and 363."""

    @pytest.mark.parametrize("which", [0, 1])
    def test_each_runs_where_the_figure_says(self, sides, which: int) -> None:
        side = sides[which]
        high, first, last, trough, depth, rows = SPELLS[side.name]
        spell = longest_spell(cumulative_return(side))
        assert spell.rows == side.max_drawdown_days == rows, SPEC
        assert (_day(side, spell.high), _day(side, spell.first), _day(side, spell.last)) == (
            high,
            first,
            last,
        ), SPEC
        assert spell.high == spell.first - 1

    @pytest.mark.parametrize("which", [0, 1])
    def test_each_deepest_drawdown_sits_inside_its_spell(self, sides, which: int) -> None:
        side = sides[which]
        *_, trough, depth, _ = SPELLS[side.name]
        spell = longest_spell(cumulative_return(side))
        assert spell.first <= spell.trough <= spell.last, SPEC
        assert _day(side, spell.trough) == trough, SPEC
        assert spell.depth == pytest.approx(side.max_drawdown, abs=1e-12), SPEC
        assert spell.depth == pytest.approx(depth, abs=5e-7), SPEC

    def test_the_mirrors_spell_is_the_longer_and_the_deeper(self, sides) -> None:
        long, short = (longest_spell(cumulative_return(side)) for side in sides)
        assert short.rows > long.rows and short.depth < long.depth, SPEC

    def test_each_shaded_spell_covers_its_rows(self, panels) -> None:
        for ax, side in panels:
            band = _by_gid(ax.patches)["spell"]
            spell = ax.spell
            assert _span_rows(band, side.days) == list(range(spell.first, spell.last + 1)), SPEC

    def test_the_high_and_the_trough_are_marked_on_each_line(self, panels) -> None:
        for ax, side in panels:
            marks = _by_gid(ax.lines)
            for gid, row in (("high", ax.spell.high), ("trough", ax.spell.trough)):
                assert list(marks[gid].get_xdata()) == [side.days[row]]
                assert list(marks[gid].get_ydata()) == [ax.cumret[row]]

    def test_the_labels_name_each_spell_its_high_and_its_drawdown(self, figure) -> None:
        top, bottom = (_texts(ax) for ax in figure.axes)
        assert top["spell-label"] == "159 days below the high,\n2008-09-02 to 2009-04-20"
        assert top["high-label"] == "high, 2008-08-29"
        assert top["trough-label"] == "deepest drawdown −0.052459,\n2008-12-09"
        assert bottom["spell-label"] == "363 days below the high,\n2008-11-24 to 2010-05-05"
        assert bottom["high-label"] == "high, 2008-11-21"
        assert bottom["trough-label"] == "deepest drawdown −0.064928,\n2009-02-03"


class TestTheIdleStart:
    """The first 90 rows, which ``test_nothing_is_held_before_the_spread_exists`` holds empty."""

    def test_each_band_covers_exactly_the_rows_before_the_spread(self, panels) -> None:
        for ax, side in panels:
            rows = _span_rows(_by_gid(ax.patches)["unfilled"], side.days)
            assert rows == list(range(SPREAD_LOOKBACK)), SPEC
            assert not side.positions[rows].any(), SPEC
            assert _day(side, SPREAD_LOOKBACK) == "2006-09-19", SPEC

    def test_its_label_names_the_90_days_once(self, figure) -> None:
        top, bottom = (_texts(ax) for ax in figure.axes)
        assert top["unfilled-label"] == (
            "no position in the first 90 days,\nbefore the 90-day spread exists"
        )
        assert "unfilled-label" not in bottom


class TestTheWords:
    def test_the_title_carries_the_exploratory_label(self, figure) -> None:
        title = figure._suptitle.get_text()
        assert title.startswith("Exploratory:")
        assert "redrawn" in title
        assert "declared mirror" in title

    def test_the_note_names_the_file_and_the_survivors(self, figure) -> None:
        note = figure.texts[-1].get_text()
        assert "2006-05-11 to 2012-04-24" in note
        assert "over 10, unlevered and before costs" in note
        assert "inputDataOHLCDaily_stocks_20120424.mat" in note
        assert "bog.m loads as inputDataOHLCDaily_20120424" in note
        assert "every stock is a survivor" in note

    def test_no_label_is_parsed_as_math(self, figure) -> None:
        for text in [*figure.axes[0].texts, *figure.axes[1].texts, *figure.texts]:
            assert text.get_parse_math() is False


class TestTheReadPath:
    def test_the_default_path_reads_the_runs_own_sides(self, monkeypatch, tmp_path, sides) -> None:
        """With no sides handed in, the figure reads ``both_sides``, the run's path."""
        import chan.buy_on_gap_figures as figures

        asked = []

        def read():
            asked.append(True)
            return [], *sides

        monkeypatch.setattr(figures, "both_sides", read)
        drawn = make_cumulative_figure(out=tmp_path / CUMULATIVE_FIGURE)
        assert asked == [True]
        assert list(drawn.axes[1].cumret) == list(cumulative_return(sides[1]))

    def test_both_sides_is_the_runs_read(self, monkeypatch, sides) -> None:
        """``run`` and the figure both go through ``both_sides``, so they cannot diverge."""
        monkeypatch.setattr(buy_on_gap, "both_sides", lambda data_dir=None: ([], *sides))
        monkeypatch.setattr(buy_on_gap, "report", lambda *args: None)
        assert buy_on_gap.run() == tuple(sides)

    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.is_file()

    def test_a_missing_vintage_reaches_the_operator_as_one_line(self, monkeypatch) -> None:
        import chan.buy_on_gap_figures as figures

        def refuse(data_dir=None):
            raise VintageUnavailable("no committed vintage is lifted from inputDataOHLCDaily")

        monkeypatch.setattr(figures, "both_sides", refuse)
        with pytest.raises(SystemExit, match="no committed vintage is lifted from inputData"):
            main()

    def test_the_command_writes_the_committed_path(self, monkeypatch, capsys) -> None:
        import chan.buy_on_gap_figures as figures

        drawn = []
        monkeypatch.setattr(figures, "make_cumulative_figure", lambda **kw: drawn.append(kw))
        main()
        assert drawn == [{}]
        assert f"wrote {FIGURES_DIR / CUMULATIVE_FIGURE}" in capsys.readouterr().out


def test_the_committed_figure_exists() -> None:
    assert (FIGURES_DIR / CUMULATIVE_FIGURE).is_file()


def test_the_x_axis_is_dates(figure, sides) -> None:
    """A figure drawn against row numbers would still pass the value checks."""
    start, end = figure.axes[1].get_xlim()
    assert num2date(start).date() == sides[0].days[0].date()
    assert num2date(end).date() == sides[0].days[-1].date()
