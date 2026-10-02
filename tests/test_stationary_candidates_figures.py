"""The pins for the stationary-candidates post's figure.

``tests/test_stationary_candidates.py`` holds what both candidates compute. This
file holds that the figure draws those numbers against the right bars, so a
generator that put a statistic on the wrong line or a bar at the wrong value
fails even when the arithmetic is right. Some numbers repeat here on purpose,
because a figure's labels are prose and the suite is the authority for every
number prose quotes. No test compares bytes, for the reason
``tests/test_regime_figure.py`` gives.

The vintages and specifications are the ones that file states at its head:
``CADAUD=X`` on the log from 2007-08-06, and TLT against IEF on raw closes over
their shared history, all downloaded 2026-10-02.
"""

from __future__ import annotations

import dataclasses

import pytest
from ithildincore.timeseries import ADF_CRIT_CONST, EG_CRIT_N2
from matplotlib.colors import to_rgba

from chan.paths import FIGURES_DIR
from chan.stationary_candidates import cross_rate, fixed_income
from chan.stationary_candidates_figures import (
    BARS_FIGURE,
    GOOD,
    LEVELS,
    LOST,
    MUTED,
    ONE_SERIES_Y,
    PAIR_Y,
    X_RANGE,
    make_bars_figure,
    marks,
)
from chan.vintage import VintageUnavailable


@pytest.fixture(scope="module")
def measured():
    return cross_rate(), fixed_income()[1]


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("stationary_figures") / BARS_FIGURE


@pytest.fixture(scope="module")
def figure(out, measured):
    rate, orientations = measured
    return make_bars_figure(out=out, rate=rate, orientations=orientations)


def _by_gid(figure) -> dict:
    ax = figure.axes[0]
    return {a.get_gid(): a for a in [*ax.lines, *ax.collections] if a.get_gid()}


def _rgb(colour) -> tuple[float, float, float]:
    return tuple(to_rgba(colour)[:3])


class TestTheBars:
    """Each table on its own line, at the values the run reads it against."""

    @pytest.mark.parametrize(
        ("name", "y", "table"), [("adf", ONE_SERIES_Y, ADF_CRIT_CONST), ("eg", PAIR_Y, EG_CRIT_N2)]
    )
    def test_each_bar_sits_at_its_constant_on_its_own_line(self, figure, name, y, table) -> None:
        artists = _by_gid(figure)
        for level in LEVELS:
            bar = artists[f"bar-{name}-{level}"]
            assert set(bar.get_xdata()) == {table[level]}
            assert min(bar.get_ydata()) < y < max(bar.get_ydata())

    def test_the_bars_are_the_two_tables_the_post_quotes(self) -> None:
        """The post's Lesson 2 quotes all six, so they are held here by value
        and not only by name."""
        assert [ADF_CRIT_CONST[level] for level in LEVELS] == [-3.43, -2.86, -2.57]
        assert [EG_CRIT_N2[level] for level in LEVELS] == [-3.9, -3.34, -3.04]

    def test_each_bar_is_labelled_with_its_level_and_value(self, figure) -> None:
        labels = [t.get_text() for t in figure.axes[0].texts[:6]]
        assert labels == [
            "1%\n−3.43",
            "5%\n−2.86",
            "10%\n−2.57",
            "1%\n−3.90",
            "5%\n−3.34",
            "10%\n−3.04",
        ]

    @pytest.mark.parametrize(("name", "y"), [("adf", ONE_SERIES_Y), ("eg", PAIR_Y)])
    def test_each_line_and_its_shading_sit_at_its_own_height(self, figure, name, y) -> None:
        artists = _by_gid(figure)
        rule = artists[f"axis-{name}"]
        assert tuple(rule.get_xdata()) == X_RANGE
        assert tuple(rule.get_ydata()) == (y, y)
        ys = artists[f"shade-{name}"].get_paths()[0].vertices[:, 1]
        assert ys.min() < y < ys.max()
        assert _rgb(artists[f"shade-{name}"].get_facecolor()[0]) == _rgb(GOOD)

    def test_the_bars_wear_the_muted_ink_and_their_labels_sit_above_them(self, figure) -> None:
        artists = _by_gid(figure)
        anchors = [t.xy for t in figure.axes[0].texts[:6]]
        expected = []
        for name, y, table in (("adf", ONE_SERIES_Y, ADF_CRIT_CONST), ("eg", PAIR_Y, EG_CRIT_N2)):
            for level in LEVELS:
                assert _rgb(artists[f"bar-{name}-{level}"].get_color()) == _rgb(MUTED)
                expected.append((table[level], y + 0.16))
        assert anchors == [pytest.approx(xy) for xy in expected]

    @pytest.mark.parametrize(("name", "table"), [("adf", ADF_CRIT_CONST), ("eg", EG_CRIT_N2)])
    def test_the_shading_runs_from_the_left_edge_to_the_five_percent_bar(
        self, figure, name, table
    ) -> None:
        path = _by_gid(figure)[f"shade-{name}"].get_paths()[0]
        xs = path.vertices[:, 0]
        assert xs.min() == pytest.approx(X_RANGE[0])
        assert xs.max() == pytest.approx(table["5%"])


class TestTheMarks:
    """Each statistic on the line whose bars it is read against."""

    def test_the_rate_sits_on_the_one_series_line_at_both_statistics(
        self, figure, measured
    ) -> None:
        rate, _ = measured
        artists = _by_gid(figure)
        for gid, stat in (
            ("mark-cadaud-1", rate.adf_stat),
            ("mark-cadaud-passing", rate.passing.adf_stat),
        ):
            assert (artists[gid].get_xdata()[0], artists[gid].get_ydata()[0]) == (
                stat,
                ONE_SERIES_Y,
            )

    def test_the_pair_sits_on_the_pair_line_in_both_orientations(self, figure, measured) -> None:
        _, orientations = measured
        by = {o.dependent: o for o in orientations}
        artists = _by_gid(figure)
        for gid, leg in (("mark-tlt-on-ief", "TLT"), ("mark-ief-on-tlt", "IEF")):
            assert (artists[gid].get_xdata()[0], artists[gid].get_ydata()[0]) == (
                by[leg].fit.adf_stat,
                PAIR_Y,
            )

    def test_the_rate_is_drawn_again_hollow_on_the_pair_line(self, figure, measured) -> None:
        """Lesson 2 in the picture: the same two statistics, read against the
        pair's bars, fall short of its 5% bar."""
        rate, _ = measured
        artists = _by_gid(figure)
        for gid, stat in (
            ("mark-cadaud-1-as-pair", rate.adf_stat),
            ("mark-cadaud-passing-as-pair", rate.passing.adf_stat),
        ):
            mark = artists[gid]
            assert (mark.get_xdata()[0], mark.get_ydata()[0]) == (stat, PAIR_Y)
            assert mark.get_markerfacecolor() == "none"
            assert _rgb(mark.get_markeredgecolor()) == _rgb(GOOD)
            assert EG_CRIT_N2["5%"] < stat < ADF_CRIT_CONST["5%"]

    def test_the_filled_marks_wear_the_verdict_colours(self, figure) -> None:
        artists = _by_gid(figure)
        for gid in ("mark-cadaud-1", "mark-cadaud-passing"):
            assert _rgb(artists[gid].get_markerfacecolor()) == _rgb(GOOD)
        for gid in ("mark-tlt-on-ief", "mark-ief-on-tlt"):
            assert _rgb(artists[gid].get_markerfacecolor()) == _rgb(LOST)

    def test_each_mark_is_labelled_with_its_own_numbers(self, figure) -> None:
        assert [t.get_text() for t in figure.axes[0].texts[6:]] == [
            "CAD/AUD, 1 lag\n−3.2136",
            "CAD/AUD, 10 lags\n−2.9946",
            "TLT on IEF\n−2.3887",
            "IEF on TLT\n−2.3168",
            "CAD/AUD's two, read\nagainst these bars",
        ]

    def test_each_label_is_anchored_at_its_own_mark(self, figure) -> None:
        labelled = [m for m in figure.marks if m.label]
        assert len(figure.marks) == 6
        assert [t.xy for t in figure.axes[0].texts[6:]] == [(m.x, m.y) for m in labelled]

    def test_the_passing_label_reads_the_lag_count_the_run_found(self, measured) -> None:
        """The real search stops at 10, so a label hard-coding 10 would pass
        on the real data. A result whose search stopped elsewhere holds it."""
        rate, orientations = measured
        moved = dataclasses.replace(rate, passing=dataclasses.replace(rate.passing, lags=7))
        labels = [m.label for m in marks(moved, orientations)]
        assert "CAD/AUD, 7 lags\n−2.9946" in labels

    def test_every_mark_is_inside_the_axis(self, figure) -> None:
        """The post's alt text quotes the range, so the constant is held by
        value as well as by what it has to contain."""
        assert X_RANGE == (-4.1, -2.0)
        assert figure.axes[0].get_xlim() == X_RANGE
        for mark in figure.marks:
            assert X_RANGE[0] < mark.x < X_RANGE[1]


class TestTheText:
    def test_the_title_states_the_finding(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "CAD/AUD clears the one-series bar at 5%, "
            "and the same statistics fall short of the pair's"
        )

    def test_the_note_names_the_vintages_and_what_the_marks_mean(self, figure) -> None:
        note = figure.texts[-1].get_text()
        assert "CADAUD=X, log of the rate, 2007-08-06 to 2026-09-30." in note
        assert "TLT and IEF raw closes, 2002-07-30 to 2026-10-01." in note
        assert "All downloaded 2026-10-02." in note
        assert "Shaded: past the 5% bar." in note
        assert note.endswith(
            "Hollow: CAD/AUD's two statistics read against the pair's bars, "
            "which pay for a fitted hedge ratio."
        )

    def test_the_axes_show_both_lines_every_bar_and_their_names(self, figure) -> None:
        ax = figure.axes[0]
        low, high = ax.get_ylim()
        assert low < PAIR_Y < ONE_SERIES_Y < high
        left, right = ax.get_xlim()
        for table in (ADF_CRIT_CONST, EG_CRIT_N2):
            assert all(left < table[level] < right for level in LEVELS)
        ticks = dict(
            zip(ax.get_yticks(), (t.get_text() for t in ax.get_yticklabels()), strict=True)
        )
        assert ticks == {
            ONE_SERIES_Y: "one series,\nADF with a constant",
            PAIR_Y: "a fitted pair,\nEngle-Granger",
        }
        assert ax.get_xlabel() == (
            "t-statistic, where further left is stronger evidence of a stationary series or spread"
        )

    def test_no_label_is_parsed_as_math(self, figure) -> None:
        """The bar labels carry percent signs, so math parsing stays off the
        way it does for the other figures."""
        for text in [*figure.axes[0].texts, *figure.texts]:
            assert text.get_parse_math() is False


def test_drawing_writes_the_file_it_is_given(figure, out) -> None:
    assert out.is_file()


def test_a_missing_vintage_reaches_the_operator_as_a_line(monkeypatch) -> None:
    """The command reads the same vintages as the candidates' own, so a
    missing download ends in the refusal's own sentence, not a traceback."""
    import chan.stationary_candidates_figures as figures

    def refuse(*_, **__):
        raise VintageUnavailable("no CADAUD=X vintage recorded")

    monkeypatch.setattr(figures, "cross_rate", refuse)
    with pytest.raises(SystemExit, match="no CADAUD=X vintage recorded"):
        figures.main()


def test_the_committed_figure_exists() -> None:
    assert (FIGURES_DIR / BARS_FIGURE).is_file()
