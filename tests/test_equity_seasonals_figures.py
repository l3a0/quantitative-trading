"""The pins for the equity-seasonals post's one figure.

``tests/test_equity_seasonals.py`` holds what Example 7.7 computes. This file
holds that the figure draws those numbers, so a generator that summed the wrong
months, put the split on the wrong date or labelled a half with the other's
figures fails even when the arithmetic is right. Some numbers repeat here on
purpose, because a figure's labels are prose and the suite is the authority for
every number prose quotes. No test compares bytes, for the reason
``tests/test_regime_figure.py`` gives.

The vintage is ``data/spx_20071123/``, the 500 S&P 500 members lifted from
Chan's ``SPX_20071123.mat``, split-adjusted, saved 2007-11-24, spanning
1999-11-24 to 2007-11-23. The specification is the revised edition's Python,
``PYTHON_HESTON_SADKA``. Like the split it draws, the figure is exploratory and
carries no verdict.
"""

from __future__ import annotations

import pandas as pd
import pytest
from matplotlib.colors import to_rgba

import chan.equity_seasonals_figures as figures
from chan.equity_seasonals import (
    LARGE_CAPS,
    PYTHON_HESTON_SADKA,
    SPLIT,
    heston_sadka,
    split_at,
)
from chan.equity_seasonals_figures import SPLIT_FIGURE, make_split_figure
from chan.paths import FIGURES_DIR
from chan.regime_figure import GOOD, LOST
from chan.series import load_panel
from chan.vintage import VintageUnavailable


@pytest.fixture(scope="module")
def panel():
    """Loaded once, because ``load_panel`` hashes and parses all 500 members."""
    return load_panel(LARGE_CAPS)


@pytest.fixture(scope="module")
def kept(panel) -> pd.Series:
    rules = PYTHON_HESTON_SADKA
    return heston_sadka(panel[1], rules).returns.iloc[rules.dropped :]


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("equity_seasonals_figures") / SPLIT_FIGURE


@pytest.fixture(scope="module")
def figure(panel, out):
    return make_split_figure(panel, out=out)


def _by_gid(figure) -> dict:
    ax = figure.axes[0]
    return {a.get_gid(): a for a in [*ax.lines, *ax.texts] if a.get_gid()}


class TestTheLine:
    def test_it_draws_the_83_month_ends_from_december_2000(self, figure) -> None:
        dates = pd.DatetimeIndex(_by_gid(figure)["running-sum"].get_xdata())
        assert len(dates) == 83
        assert dates[0] == pd.Timestamp("2000-12-31")
        assert dates[-1] == pd.Timestamp("2007-10-31")
        assert (dates == dates + pd.offsets.MonthEnd(0)).all()

    def test_it_is_the_running_sum_of_the_kept_months(self, figure, kept) -> None:
        drawn = _by_gid(figure)["running-sum"].get_ydata()
        assert list(drawn) == pytest.approx(list(kept.cumsum()), abs=1e-12)

    def test_its_end_is_83_twelfths_of_the_pinned_annual_return(self, figure, panel) -> None:
        """Ties the line to the −0.012679 ``TestHestonSadkaPython`` pins."""
        end = _by_gid(figure)["running-sum"].get_ydata()[-1]
        annual = heston_sadka(panel[1], PYTHON_HESTON_SADKA).annual_return
        assert end == pytest.approx(83 / 12 * annual, abs=1e-12)
        assert end == pytest.approx(83 / 12 * -0.012679138708036275, abs=1e-9)

    def test_it_draws_the_zero_line_and_shows_the_running_sum(self, figure) -> None:
        drawn = _by_gid(figure)
        assert set(drawn["zero"].get_ydata()) == {0}
        assert drawn["running-sum"].get_visible()

    def test_nothing_wears_a_verdict_colour(self, figure) -> None:
        """No shading at all, and no line, label, axis title or tick in green or red."""
        ax = figure.axes[0]
        assert not ax.patches
        assert not ax.collections
        verdicts = {to_rgba(GOOD), to_rgba(LOST)}
        for line in ax.lines:
            for colour in (
                line.get_color(),
                line.get_markerfacecolor(),
                line.get_markeredgecolor(),
            ):
                assert to_rgba(colour) not in verdicts
        for text in [
            *ax.texts,
            *figure.texts,
            ax.xaxis.label,
            ax.yaxis.label,
            *ax.get_xticklabels(),
            *ax.get_yticklabels(),
        ]:
            assert to_rgba(text.get_color()) not in verdicts


class TestTheSplit:
    def test_the_split_line_sits_at_split(self, figure) -> None:
        xs = set(_by_gid(figure)["split"].get_xdata())
        assert xs == {SPLIT}
        assert SPLIT == pd.Timestamp("2002-01-01")

    def test_each_half_is_labelled_with_split_at_s_figures(self, figure, panel) -> None:
        before, after = split_at(heston_sadka(panel[1], PYTHON_HESTON_SADKA), PYTHON_HESTON_SADKA)
        labels = _by_gid(figure)
        for gid, when, (months, annual, sharpe) in (
            ("label-before", "before", before),
            ("label-after", "from", after),
        ):
            assert labels[gid].get_text() == (
                f"{months} months {when} 2002\n"
                f"{format(annual, '.6f').replace('-', '−')} a year\n"
                f"Sharpe ratio {format(sharpe, '.6f').replace('-', '−')}"
            )

    def test_the_labels_read_the_figures_the_post_quotes(self, figure) -> None:
        labels = _by_gid(figure)
        assert labels["label-before"].get_text() == (
            "13 months before 2002\n−0.145387 a year\nSharpe ratio −0.859993"
        )
        assert labels["label-after"].get_text() == (
            "70 months from 2002\n0.011967 a year\nSharpe ratio 0.141777"
        )

    def test_each_label_sits_on_its_own_side_of_the_split(self, figure) -> None:
        labels = _by_gid(figure)
        assert labels["label-before"].get_ha() == "right"
        assert labels["label-before"].xyann[0] < 0
        assert labels["label-after"].get_ha() == "left"
        assert labels["label-after"].xyann[0] > 0
        for gid in ("label-before", "label-after"):
            assert labels[gid].xy == (SPLIT, 1.0)
            assert labels[gid].get_va() == "top"

    def test_the_labels_sit_above_the_line(self, figure) -> None:
        """The y-axis leaves room at the top, so the labels hang into empty space."""
        ax = figure.axes[0]
        top = max(_by_gid(figure)["running-sum"].get_ydata())
        assert ax.get_ylim()[1] > top + 0.2 * (top - ax.get_ylim()[0])


class TestTheWords:
    def test_the_title_carries_the_exploratory_label(self, figure) -> None:
        title = figure._suptitle.get_text()
        assert title == "Example 7.7 split at 2002, an exploratory cut with no verdict"

    def test_the_y_axis_names_fractions_of_capital(self, figure) -> None:
        """Not the first edition's units of summed positions."""
        assert figure.axes[0].get_ylabel() == (
            "running sum of monthly returns,\nas a fraction of capital"
        )

    def test_the_note_names_the_vintage_and_the_survivors(self, figure) -> None:
        note = figure.texts[-1].get_text().replace("\n", " ")
        assert note.startswith(
            "spx_20071123/ chan-mat adjusted, saved 2007-11-24, 500 members lifted from "
            "SPX_20071123.mat, which holds only the companies in the S&P 500 the day Chan "
            "saved it."
        )
        assert "The revised edition's Python rules, 83 months from 2000-12-31 to 2007-10-31," in (
            note
        )
        assert note.endswith(
            "A running sum through 83 months shows how far a single year moves it."
        )

    def test_no_label_is_parsed_as_math(self, figure) -> None:
        """The note carries an ampersand and the labels minus signs, so math
        parsing stays off the way it does for the other figures."""
        for text in [*figure.axes[0].texts, *figure.texts]:
            assert text.get_parse_math() is False


def test_drawing_writes_the_file_it_is_given(figure, out) -> None:
    assert out.is_file()


def test_drawing_reads_only_the_panel_it_is_given(panel, monkeypatch, tmp_path) -> None:
    """A short panel draws a short line, and nothing reads the vintage again."""

    def refuse(*_args, **_kwargs):
        raise AssertionError("the figure read the vintage instead of the panel it was given")

    monkeypatch.setattr(figures, "load_panel", refuse)
    members, closes = panel
    short = make_split_figure((members, closes.loc[:"2005-12-31"]), out=tmp_path / SPLIT_FIGURE)
    dates = pd.DatetimeIndex(_by_gid(short)["running-sum"].get_xdata())
    assert dates[-1] < pd.Timestamp("2005-12-31")


def test_the_committed_figure_exists() -> None:
    assert (FIGURES_DIR / SPLIT_FIGURE).is_file()


def test_the_command_reads_the_vintage_once_and_draws(monkeypatch, capsys) -> None:
    panel, drawn, reads = object(), [], []
    monkeypatch.setattr(figures, "load_panel", lambda name: reads.append(name) or (name, panel))
    monkeypatch.setattr(figures, "make_split_figure", lambda p: drawn.append(p))
    figures.main()
    assert reads == [LARGE_CAPS]
    assert drawn == [(LARGE_CAPS, panel)]
    assert SPLIT_FIGURE in capsys.readouterr().out


def test_a_missing_vintage_reaches_the_operator_as_one_line(monkeypatch) -> None:
    def refuse(*_args, **_kwargs):
        raise VintageUnavailable("no committed vintage is lifted from SPX_20071123.mat")

    monkeypatch.setattr(figures, "load_panel", refuse)
    with pytest.raises(SystemExit, match="no committed vintage is lifted from SPX_20071123.mat"):
        figures.main()


def test_any_other_failure_still_ends_in_a_traceback(monkeypatch) -> None:
    """Only a refused vintage becomes one line, so a real bug is not hidden."""

    def broken(*_args, **_kwargs):
        raise ValueError("a bug, not a refusal")

    monkeypatch.setattr(figures, "load_panel", broken)
    with pytest.raises(ValueError, match="a bug, not a refusal"):
        figures.main()
