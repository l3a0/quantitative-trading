"""The pins for the Kelly post's figure.

``tests/test_kelly_leverage.py`` holds what the Kelly run computes. This file
holds that the figure draws those numbers, so a generator that plotted the
wrong curve or marked the wrong leverage fails even when the arithmetic is
right. Some numbers repeat here on purpose, because a figure's title and labels
are prose, and the suite is the authority for every number prose quotes. No
test compares bytes, for the reason ``tests/test_regime_figure.py`` gives.
"""

from __future__ import annotations

import numpy as np
import pytest
from matplotlib.colors import to_rgba

from chan.kelly_figures import (
    ACCENT,
    GOOD,
    GROWTH_FIGURE,
    LOST,
    MAX_LEVERAGE,
    MUTED,
    chan_window_moments,
    growth,
    growth_curve,
    make_growth_figure,
)
from chan.paths import FIGURES_DIR


@pytest.fixture(scope="module")
def moments():
    return chan_window_moments()


@pytest.fixture(scope="module")
def figure(tmp_path_factory: pytest.TempPathFactory, moments):
    out = tmp_path_factory.mktemp("kelly_figures") / GROWTH_FIGURE
    return make_growth_figure(out=out, moments=moments)


def _rgb(colour) -> tuple[float, float, float]:
    return tuple(to_rgba(colour)[:3])


def _marks(ax) -> list:
    return [line for line in ax.lines if len(line.get_xdata()) == 1]


class TestTheCurve:
    """The formula the post derives, on the moments the Kelly run computes."""

    def test_the_formula_reproduces_both_growth_rates_the_run_pins(self, moments) -> None:
        """g(1) is the unlevered rate and g(f*) the Kelly rate, so the one
        formula and the two the run computes separately agree."""
        assert growth(moments, 1.0) == pytest.approx(moments.unlevered_growth, abs=1e-15)
        assert growth(moments, moments.leverage) == pytest.approx(moments.levered_growth, abs=1e-15)

    def test_half_kelly_keeps_three_quarters_and_twice_kelly_keeps_none(self, moments) -> None:
        r, kelly = moments.risk_free, moments.leverage
        top = growth(moments, kelly) - r
        assert growth(moments, kelly / 2) - r == pytest.approx(0.75 * top, abs=1e-15)
        assert growth(moments, 2 * kelly) == pytest.approx(r, abs=1e-15)
        assert growth(moments, kelly / 2) == pytest.approx(0.1097729837, abs=5e-10)
        assert 2 * kelly == pytest.approx(5.1011826450, abs=5e-10)

    def test_the_drawn_curve_is_the_formula_and_peaks_at_kelly(self, figure, moments) -> None:
        curve = figure.curve
        assert curve.leverages[0] == 0.0
        assert curve.leverages[-1] == MAX_LEVERAGE
        assert list(curve.growth) == pytest.approx(
            list(growth(moments, curve.leverages)), abs=1e-15
        )
        step = curve.leverages[1] - curve.leverages[0]
        assert curve.leverages[np.argmax(curve.growth)] == pytest.approx(moments.leverage, abs=step)
        drawn = max(figure.axes[0].lines, key=lambda line: len(line.get_xdata()))
        assert list(drawn.get_ydata()) == pytest.approx(list(curve.growth), abs=1e-15)

    def test_the_range_leaves_room_past_twice_kelly(self, moments) -> None:
        """The alt text quotes the range, so the constant is pinned as well as
        its relation to the last mark."""
        assert MAX_LEVERAGE == 5.6
        curve = growth_curve(moments)
        assert curve.leverages[-1] > 2 * moments.leverage


class TestTheMarks:
    def test_the_four_marks_sit_on_the_curve_at_the_four_leverages(self, figure, moments) -> None:
        kelly = moments.leverage
        points = [(line.get_xdata()[0], line.get_ydata()[0]) for line in _marks(figure.axes[0])]
        expected = [1.0, kelly / 2, kelly, 2 * kelly]
        assert points == [pytest.approx((x, growth(moments, x)), abs=1e-12) for x in expected]

    def test_each_mark_is_labelled_with_its_own_numbers(self, figure) -> None:
        assert [text.get_text() for text in figure.axes[0].texts] == [
            "unlevered SPY, 1\n9.86% a year",
            "half-Kelly, 1.28\n10.98% a year",
            "Kelly, 2.551\n13.30% a year",
            "twice Kelly, 5.10\n4%, the cash rate",
        ]

    def test_the_marks_wear_distinct_colours(self, figure) -> None:
        colours = [_rgb(line.get_color()) for line in _marks(figure.axes[0])]
        assert colours == [_rgb(MUTED), _rgb(ACCENT), _rgb(GOOD), _rgb(LOST)]

    def test_the_dashed_line_is_the_risk_free_rate(self, figure, moments) -> None:
        dashed = [line for line in figure.axes[0].lines if line.get_linestyle() == "--"]
        assert len(dashed) == 1
        assert set(dashed[0].get_ydata()) == {moments.risk_free}


class TestTheText:
    def test_the_title_states_the_finding(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Growth on SPY peaks at the Kelly leverage and falls back to cash at twice it"
        )

    def test_the_note_names_the_window_the_formula_and_its_inputs(self, figure) -> None:
        note = figure.texts[-1].get_text()
        assert "SPY, 1993-01-29 to 2007-12-28, 2026 download." in note
        assert "g(f) = r + f·m − f²s²/2" in note
        assert "m = 0.07295, s = 0.1691 and r = 0.04" in note
        assert "three-quarters" in note

    def test_no_label_is_parsed_as_math(self, figure) -> None:
        """The labels carry percent signs and the note carries a formula, so
        math parsing stays off the way it does for the coin-flip figures."""
        for text in [*figure.axes[0].texts, *figure.texts]:
            assert text.get_parse_math() is False


def test_the_committed_figure_exists() -> None:
    assert (FIGURES_DIR / GROWTH_FIGURE).is_file()
