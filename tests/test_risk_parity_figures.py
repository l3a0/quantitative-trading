"""The pins for the risk parity post's figure.

``tests/test_risk_parity.py`` holds what the risk parity run computes. This
file holds that the figure draws those numbers, so a generator that stacked the
wrong shares or swapped a portfolio's capital for its risk fails even when the
arithmetic is right. Some numbers repeat here on purpose, because a figure's
title and labels are prose, and the suite is the authority for every number
prose quotes. No test compares bytes, for the reason
``tests/test_regime_figure.py`` gives.
"""

from __future__ import annotations

import pytest
from matplotlib.colors import to_rgba

from chan.paths import FIGURES_DIR
from chan.risk_parity_figures import (
    ACCENT,
    GOOD,
    INK,
    INSIDE_LABEL_MIN,
    SPLIT_FIGURE,
    SURFACE,
    full_span,
    make_risk_split_figure,
    split_bars,
)


@pytest.fixture(scope="module")
def result():
    return full_span()


@pytest.fixture(scope="module")
def figure(tmp_path_factory: pytest.TempPathFactory, result):
    out = tmp_path_factory.mktemp("risk_parity_figures") / SPLIT_FIGURE
    fig = make_risk_split_figure(out=out, result=result)
    fig.written_to = out
    return fig


def _row_of(ax) -> dict[str, float]:
    """Each tick label's y position, so a mark can be tied to its label."""
    return {
        label.get_text(): y for y, label in zip(ax.get_yticks(), ax.get_yticklabels(), strict=True)
    }


def _rgb(colour) -> tuple[float, float, float]:
    return tuple(to_rgba(colour)[:3])


def _segments(ax) -> list:
    return list(ax.patches)


class TestTheBars:
    def test_the_bars_carry_the_shares_the_run_measures(self, result) -> None:
        bench, parity = result.benchmark, result.parity
        assert [(bar.label, bar.stock, bar.bond) for bar in split_bars(result)] == [
            ("60/40, capital", 0.6, 0.4),
            ("60/40, risk", bench.stock_risk_share, bench.bond_risk_share),
            ("risk parity, capital", parity.stock_weight, parity.bond_weight),
            ("risk parity, risk", parity.stock_risk_share, parity.bond_risk_share),
        ]

    def test_the_shares_are_the_ones_the_post_quotes(self, figure) -> None:
        """The post and the labels quote these at one decimal."""
        shares = [(bar.stock, bar.bond) for bar in figure.bars]
        assert shares == [
            pytest.approx((0.6, 0.4), abs=1e-12),
            pytest.approx((0.966717, 0.033283), abs=5e-7),
            pytest.approx((0.217821, 0.782179), abs=5e-7),
            pytest.approx((0.5, 0.5), abs=1e-12),
        ]

    def test_each_segment_is_drawn_at_its_share_and_wears_its_legs_colour(self, figure) -> None:
        drawn = [
            (seg.get_x(), seg.get_width(), _rgb(seg.get_facecolor()))
            for seg in _segments(figure.axes[0])
        ]
        expected = []
        for bar in figure.bars:
            expected.append((0.0, bar.stock, _rgb(ACCENT)))
            expected.append((bar.stock, bar.bond, _rgb(GOOD)))
        flat = [v for x, w, _ in drawn for v in (x, w)]
        assert flat == pytest.approx([v for x, w, _ in expected for v in (x, w)], abs=1e-12)
        assert [c for _, _, c in drawn] == [c for _, _, c in expected]

    def test_the_portfolios_are_labelled_top_to_bottom(self, figure) -> None:
        ax = figure.axes[0]
        ticks = sorted(zip(ax.get_yticks(), ax.get_yticklabels(), strict=True), key=lambda t: -t[0])
        assert [label.get_text() for _, label in ticks] == [
            "60/40, capital",
            "60/40, risk",
            "risk parity, capital",
            "risk parity, risk",
        ]


class TestTheText:
    def test_each_segment_is_labelled_with_its_leg_and_share(self, figure) -> None:
        assert [text.get_text() for text in figure.axes[0].texts] == [
            "SPY 60%",
            "AGG 40%",
            "SPY 96.7%",
            "AGG 3.3%",
            "SPY 21.8%",
            "AGG 78.2%",
            "SPY 50%",
            "AGG 50%",
        ]

    def test_only_the_segment_too_narrow_for_its_label_carries_it_outside(self, figure) -> None:
        narrow = [
            width
            for bar in figure.bars
            for width in (bar.stock, bar.bond)
            if width < INSIDE_LABEL_MIN
        ]
        assert narrow == [pytest.approx(0.033283, abs=5e-7)]
        outside = [text for text in figure.axes[0].texts if text.get_text() == "AGG 3.3%"]
        assert outside[0].get_ha() == "left"

    def test_the_title_states_the_premise(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "60/40 puts 60% of the capital and 96.7% of the risk in stocks"
        )

    def test_the_note_names_the_window_and_both_volatilities(self, figure) -> None:
        note = figure.texts[-1].get_text()
        assert "SPY and AGG, 2003-09-30 to 2026-09-17, 2026 downloads." in note
        assert "18.55% for SPY and 5.17% for AGG" in note
        assert "share of the portfolio's variance" in note

    def test_the_legend_names_both_legs(self, figure) -> None:
        legend = figure.axes[0].get_legend()
        assert [text.get_text() for text in legend.get_texts()] == [
            "stocks, SPY",
            "bonds, AGG",
        ]

    def test_no_label_is_parsed_as_math(self, figure) -> None:
        """The labels carry percent signs, so math parsing stays off the way
        it does for the other post figures."""
        for text in [*figure.axes[0].texts, *figure.texts]:
            assert text.get_parse_math() is False


class TestWhereEachMarkSits:
    """Mutation review found every bar and label could move to another
    portfolio's row with the suite still green, so the positions are held."""

    def test_each_segment_sits_on_the_row_of_its_own_label(self, figure) -> None:
        ax = figure.axes[0]
        rows = _row_of(ax)
        centres = [seg.get_y() + seg.get_height() / 2 for seg in _segments(ax)]
        expected = [rows[bar.label] for bar in figure.bars for _ in (0, 1)]
        assert centres == pytest.approx(expected, abs=1e-12)

    def test_each_label_sits_on_its_segment(self, figure) -> None:
        ax = figure.axes[0]
        rows = _row_of(ax)
        expected = []
        for bar in figure.bars:
            for left, width in ((0.0, bar.stock), (bar.stock, bar.bond)):
                inside = width >= INSIDE_LABEL_MIN
                x = left + width / 2 if inside else left + width
                expected.append((x, rows[bar.label], SURFACE if inside else INK))
        drawn = []
        for text in ax.texts:
            x, y = text.xy if hasattr(text, "xy") else text.get_position()
            drawn.append((x, y, text.get_color()))
        assert [(x, y) for x, y, _ in drawn] == [
            pytest.approx((x, y), abs=1e-12) for x, y, _ in expected
        ]
        assert [_rgb(c) for _, _, c in drawn] == [_rgb(c) for _, _, c in expected]

    def test_the_legend_swatches_wear_the_segment_colours(self, figure) -> None:
        legend = figure.axes[0].get_legend()
        swatches = [_rgb(handle.get_facecolor()) for handle in legend.legend_handles]
        assert swatches == [_rgb(ACCENT), _rgb(GOOD)]

    def test_the_axis_shows_every_bar_whole_in_percent(self, figure) -> None:
        ax = figure.axes[0]
        assert ax.get_xlim()[0] == 0.0
        assert ax.get_xlim()[1] >= 1.0
        figure.canvas.draw()
        assert [tick.get_text() for tick in ax.get_xticklabels()] == [
            "0%",
            "25%",
            "50%",
            "75%",
            "100%",
        ]


class TestTheDefaultDraw:
    """The path ``main`` takes to redraw the committed PNG passes no result."""

    def test_the_default_draw_reads_the_full_span(self, tmp_path, result) -> None:
        fig = make_risk_split_figure(out=tmp_path / SPLIT_FIGURE)
        assert fig.bars == split_bars(result)
        assert "2003-09-30 to 2026-09-17" in fig.texts[-1].get_text()

    def test_the_figure_is_written_where_it_is_asked_to_be(self, figure) -> None:
        assert figure.written_to.is_file()
        assert figure.written_to.stat().st_size > 0


def test_the_committed_figure_exists() -> None:
    assert (FIGURES_DIR / SPLIT_FIGURE).is_file()
