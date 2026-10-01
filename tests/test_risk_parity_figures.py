"""The pins for the risk parity post's three figures.

``tests/test_risk_parity.py`` holds what the risk parity run computes. This
file holds that the figures draw those numbers, so a generator that stacked the
wrong shares, swapped a portfolio's capital for its risk, or pointed an arrow
the wrong way fails even when the arithmetic is right. Some numbers repeat
here on purpose, because a figure's title and labels are prose, and the suite
is the authority for every number prose quotes. No test compares bytes, for
the reason ``tests/test_regime_figure.py`` gives.
"""

from __future__ import annotations

import re

import pytest
from matplotlib.colors import to_rgba

from chan.paths import FIGURES_DIR
from chan.risk_parity import (
    BOOK_LEVERAGE,
    BOOK_WEIGHTS,
    RISK_FREE,
    bond_sharpe_hurdle,
    leg_sharpes,
)
from chan.risk_parity_figures import (
    ACCENT,
    BILL_AVERAGE,
    CLAIM_FIGURE,
    GOOD,
    HURDLE_FIGURE,
    HURDLE_XLIM,
    INK,
    INSIDE_LABEL_MIN,
    MIN_ARROW,
    MUTED,
    QIAN_BOND_VOL,
    QIAN_CORRELATION,
    QIAN_SHARPE_BENCHMARK,
    QIAN_SHARPE_BOND,
    QIAN_SHARPE_PARITY,
    QIAN_SHARPE_STOCK,
    QIAN_STOCK_VOL,
    SPLIT_FIGURE,
    SURFACE,
    full_span,
    full_span_ranking,
    hurdle_rows,
    make_claim_figure,
    make_hurdle_figure,
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


# The claim figure, which draws Lesson 1.


@pytest.fixture(scope="module")
def claim_figure(tmp_path_factory: pytest.TempPathFactory, result):
    out = tmp_path_factory.mktemp("risk_parity_claim") / CLAIM_FIGURE
    fig = make_claim_figure(out=out, result=result)
    fig.written_to = out
    return fig


def _dots(ax) -> list:
    """The marker lines an axes carries, leaving out reference lines."""
    return [line for line in ax.lines if line.get_marker() == "o"]


def _filled(line) -> bool:
    return line.get_markerfacecolor() != "none"


def _arrows(ax) -> list:
    return [text for text in ax.texts if getattr(text, "arrow_patch", None) is not None]


def _plain_texts(ax) -> list[str]:
    return [text.get_text() for text in ax.texts if text.get_text()]


class TestWhatTheClaimFigureCompares:
    def test_qians_figures_are_the_ones_his_paper_prints(self) -> None:
        """Table 2 of the committed paper prints 0.67 for 60/40 and 0.87 for
        levered risk parity, and the weight and leverage are the book's."""
        assert (QIAN_SHARPE_BENCHMARK, QIAN_SHARPE_PARITY) == (0.67, 0.87)
        assert (BOOK_WEIGHTS[0], BOOK_LEVERAGE) == (0.23, 1.8)

    def test_the_bill_average_is_the_one_the_post_quotes(self) -> None:
        """This holds that the code and the post quote the same rate, not that
        the rate is right. It was read off the St. Louis Fed's TB3MS series and
        is not stored here, which README's third group of unpinned figures and
        the figure's own note both say."""
        assert BILL_AVERAGE == 0.0174

    def test_this_runs_weight_and_leverage(self, claim_figure) -> None:
        drawn = claim_figure.claim
        assert drawn.stock_weight == pytest.approx(0.217821, abs=5e-7)
        assert drawn.leverage == pytest.approx(1.981188, abs=5e-7)
        assert (drawn.start, drawn.end) == ("2003-09-30", "2026-09-17")

    def test_the_three_sharpe_pairs(self, claim_figure) -> None:
        """Qian's pair as printed, then this run's at the bill average and at 4%.

        The 4% pair is the one ``tests/test_risk_parity.py`` pins on the full
        span. The bill-average pair is what the post's Lesson 4 quotes as a gap
        of about 0.02 with a t-statistic of −0.21.
        """
        pairs = claim_figure.claim.pairs
        assert [(p.benchmark, p.parity) for p in pairs] == [
            pytest.approx((0.67, 0.87), abs=1e-12),
            pytest.approx((0.610815, 0.589809), abs=5e-7),
            pytest.approx((0.411135, 0.194204), abs=5e-7),
        ]
        assert pairs[0].t is None
        assert [p.t for p in pairs[1:]] == [
            pytest.approx(-0.210392, abs=5e-7),
            pytest.approx(-2.172682, abs=5e-7),
        ]

    def test_the_drawn_pairs_are_the_rankings_at_each_rate(self, claim_figure) -> None:
        for pair, rate in zip(claim_figure.claim.pairs[1:], (BILL_AVERAGE, RISK_FREE), strict=True):
            ranking = full_span_ranking(rate)
            assert (pair.benchmark, pair.parity, pair.t) == (
                ranking.sharpe_benchmark,
                ranking.sharpe_parity,
                ranking.t_newey_west,
            )

    def test_the_lead_reverses_as_the_title_says(self, claim_figure) -> None:
        """The title says the Sharpe lead does not land close. Qian's risk
        parity leads, and this run's trails at both rates."""
        gaps = [pair.gap for pair in claim_figure.claim.pairs]
        assert gaps[0] > 0
        assert all(gap < 0 for gap in gaps[1:])


class TestTheWeightAndLeveragePanels:
    def test_each_dot_sits_at_its_value_on_its_row(self, claim_figure) -> None:
        weight_ax, leverage_ax = claim_figure.axes[0], claim_figure.axes[1]
        drawn = claim_figure.claim
        for ax, values in (
            (weight_ax, (BOOK_WEIGHTS[0], drawn.stock_weight)),
            (leverage_ax, (BOOK_LEVERAGE, drawn.leverage)),
        ):
            rows = _row_of(ax)
            dots = _dots(ax)
            assert [(d.get_xdata()[0], d.get_ydata()[0]) for d in dots] == [
                pytest.approx((values[0], rows["Qian"]), abs=1e-12),
                pytest.approx((values[1], rows["SPY and AGG"]), abs=1e-12),
            ]
            assert rows["Qian"] > rows["SPY and AGG"]
            assert all(_filled(d) and _rgb(d.get_color()) == _rgb(ACCENT) for d in dots)

    def test_each_dot_carries_its_value(self, claim_figure) -> None:
        assert _plain_texts(claim_figure.axes[0]) == ["23%", "21.8%", "60/40 holds 60%"]
        assert _plain_texts(claim_figure.axes[1]) == ["1.8", "1.98", "60/40 is unlevered"]

    def test_each_value_label_sits_beside_its_dot(self, claim_figure) -> None:
        for ax in claim_figure.axes[:2]:
            dots = _dots(ax)
            labels = [text for text in ax.texts if text.get_text()][:2]
            for dot, label in zip(dots, labels, strict=True):
                assert label.xy == pytest.approx((dot.get_xdata()[0], dot.get_ydata()[0]))
                assert label.get_ha() == "left"
                assert label.xyann[0] > 0

    def test_the_reference_lines_mark_60_40(self, claim_figure) -> None:
        for ax, x in ((claim_figure.axes[0], 0.6), (claim_figure.axes[1], 1.0)):
            references = [line for line in ax.lines if line.get_marker() != "o"]
            assert len(references) == 1
            assert list(references[0].get_xdata()) == [x, x]
            label = [text for text in ax.texts if text.get_text().startswith("60/40")][0]
            assert label.xy[0] == x

    def test_the_axes_start_at_zero_and_mark_60_40(self, claim_figure) -> None:
        """A zero baseline alone would make any two values look close. The
        60/40 line on each panel is what gives the gap between the dots a
        scale, 1.2 points of weight against 37 to 60/40's 60%."""
        weight_ax, leverage_ax = claim_figure.axes[0], claim_figure.axes[1]
        assert weight_ax.get_xlim() == (0.0, 1.0)
        assert leverage_ax.get_xlim() == (0.0, 2.5)
        claim_figure.canvas.draw()
        assert [t.get_text() for t in weight_ax.get_xticklabels()] == [
            "0%",
            "25%",
            "50%",
            "75%",
            "100%",
        ]
        assert [t.get_text() for t in leverage_ax.get_xticklabels()] == [
            "0×",
            "0.5×",
            "1×",
            "1.5×",
            "2×",
            "2.5×",
        ]


class TestTheSharpePanel:
    def test_each_row_draws_60_40_hollow_and_risk_parity_filled(self, claim_figure) -> None:
        ax = claim_figure.axes[2]
        dots = _dots(ax)
        pairs = claim_figure.claim.pairs
        assert len(dots) == 2 * len(pairs)
        for i, pair in enumerate(pairs):
            parity, bench = dots[2 * i], dots[2 * i + 1]
            assert _filled(parity) and _rgb(parity.get_color()) == _rgb(ACCENT)
            assert not _filled(bench) and _rgb(bench.get_markeredgecolor()) == _rgb(INK)
            assert parity.get_xdata()[0] == pair.parity
            assert bench.get_xdata()[0] == pair.benchmark
            assert parity.get_ydata()[0] == bench.get_ydata()[0]

    def test_the_rows_run_top_to_bottom_under_their_labels(self, claim_figure) -> None:
        ax = claim_figure.axes[2]
        pairs = claim_figure.claim.pairs
        dots = _dots(ax)
        rows = [dots[2 * i].get_ydata()[0] for i in range(len(pairs))]
        assert rows == sorted(rows, reverse=True)
        for pair, y in zip(pairs, rows, strict=True):
            label = [t for t in ax.texts if t.get_text() == pair.label][0]
            assert 0 < label.get_position()[1] - y < 0.5

    def test_the_row_labels(self, claim_figure) -> None:
        assert [pair.label for pair in claim_figure.claim.pairs] == [
            "Qian, 1983 to 2004, cash at each month's bill rate",
            "SPY and AGG, 2003 to 2026, cash at the 1.74% bill average",
            "SPY and AGG, 2003 to 2026, cash at an assumed 4%",
        ]

    def test_each_row_states_its_leader_gap_and_t(self, claim_figure) -> None:
        ax = claim_figure.axes[2]
        gaps = [t for t in ax.texts if "ahead by" in t.get_text()]
        assert [t.get_text() for t in gaps] == [
            "risk parity ahead by 0.20",
            "60/40 ahead by 0.02, t = −0.21",
            "60/40 ahead by 0.22, t = −2.17",
        ]
        dots = _dots(ax)
        for i, text in enumerate(gaps):
            assert 0 < dots[2 * i].get_ydata()[0] - text.get_position()[1] < 0.5
            assert _rgb(text.get_color()) == _rgb(MUTED)

    def test_each_value_label_sits_on_the_outer_side_of_its_dot(self, claim_figure) -> None:
        ax = claim_figure.axes[2]
        values = [t for t in ax.texts if re.fullmatch(r"\d\.\d\d", t.get_text())]
        pairs = claim_figure.claim.pairs
        assert [t.get_text() for t in values] == [
            text for p in pairs for text in (f"{p.parity:.2f}", f"{p.benchmark:.2f}")
        ]
        assert [t.get_text() for t in values] == ["0.87", "0.67", "0.59", "0.61", "0.19", "0.41"]
        for i, pair in enumerate(pairs):
            parity_label, bench_label = values[2 * i], values[2 * i + 1]
            assert parity_label.xy[0] == pair.parity
            assert bench_label.xy[0] == pair.benchmark
            right = pair.parity > pair.benchmark
            assert parity_label.get_ha() == ("left" if right else "right")
            assert bench_label.get_ha() == ("right" if right else "left")
            for label in (parity_label, bench_label):
                assert (label.xyann[0] > 0) == (label.get_ha() == "left")
                assert label.xyann[0] != 0

    def test_arrows_run_from_60_40_to_risk_parity_where_there_is_room(self, claim_figure) -> None:
        """The 1.74% row's dots touch, so it draws no arrow, and the other two
        point the way the lead runs."""
        ax = claim_figure.axes[2]
        arrows = _arrows(ax)
        pairs = [p for p in claim_figure.claim.pairs if abs(p.gap) >= MIN_ARROW]
        assert len(pairs) == 2
        assert abs(claim_figure.claim.pairs[1].gap) < MIN_ARROW
        dots = _dots(ax)
        rows = {p.label: dots[2 * i].get_ydata()[0] for i, p in enumerate(claim_figure.claim.pairs)}
        assert [(a.xy, a.xyann) for a in arrows] == [
            ((p.parity, rows[p.label]), (p.benchmark, rows[p.label])) for p in pairs
        ]
        # The head sits at xy, the risk parity end, so the arrow reads from 60/40.
        assert all(a.arrowprops["arrowstyle"] == "-|>" for a in arrows)

    def test_the_axis_runs_from_zero_to_one(self, claim_figure) -> None:
        ax = claim_figure.axes[2]
        assert ax.get_xlim() == (0.0, 1.0)
        assert ax.get_yticks().size == 0
        claim_figure.canvas.draw()
        assert [t.get_text() for t in ax.get_xticklabels()] == [
            "0.0",
            "0.2",
            "0.4",
            "0.6",
            "0.8",
            "1.0",
        ]

    def test_the_legend_names_both_portfolios_in_their_markers(self, claim_figure) -> None:
        legend = claim_figure.axes[2].get_legend()
        assert [t.get_text() for t in legend.get_texts()] == ["60/40", "risk parity"]
        bench, parity = legend.legend_handles
        assert not _filled(bench) and _rgb(bench.get_markeredgecolor()) == _rgb(INK)
        assert _filled(parity) and _rgb(parity.get_color()) == _rgb(ACCENT)


class TestTheClaimFiguresText:
    def test_the_title_states_the_finding(self, claim_figure) -> None:
        assert claim_figure._suptitle.get_text() == (
            "Risk parity's weight and leverage land close to Qian's, "
            "and its Sharpe ratio lead is gone"
        )

    def test_the_panel_titles(self, claim_figure) -> None:
        assert [ax.get_title(loc="left") for ax in claim_figure.axes] == [
            "Risk parity's stock weight",
            "Leverage to match 60/40's volatility",
            "Sharpe ratio, from 60/40 to levered risk parity",
        ]

    def test_the_note_names_both_sources_and_the_unstored_rate(self, claim_figure) -> None:
        lines = claim_figure.texts[-1].get_text().split("\n")
        assert lines == [
            "Qian (2005), Table 2: Russell 1000 and Lehman Aggregate, monthly, 1983 to 2004.",
            "SPY and AGG: 2003-09-30 to 2026-09-17, daily, 2026 downloads. 1.74% is the "
            "St. Louis Fed's average three-month bill rate",
            "(TB3MS) from October 2003 to August 2026, read off the Fed's site and "
            "not stored here.",
            "4% is the cash rate Chan assumes elsewhere in the book, above what bills "
            "paid on average.",
            "t is the t-statistic of risk parity minus 60/40, corrected for day-to-day dependence "
            "(Newey-West).",
            "Beyond ±2, a gap that size arises by chance less than 5% of the time.",
        ]

    def test_every_text_fits_inside_the_figure(self, claim_figure) -> None:
        """The note ran off the right edge on an early draw."""
        from matplotlib.backends.backend_agg import FigureCanvasAgg

        canvas = FigureCanvasAgg(claim_figure)
        canvas.draw()
        renderer = canvas.get_renderer()
        texts = [*claim_figure.texts, claim_figure._suptitle]
        texts += [t for ax in claim_figure.axes for t in ax.texts if t.get_text()]
        right = max(t.get_window_extent(renderer).x1 for t in texts)
        assert right <= claim_figure.bbox.x1

    def test_no_two_pieces_of_text_overlap(self, claim_figure) -> None:
        """Mutation review squeezed the note onto the tick labels, and the
        panels onto each other, with every other test still passing."""
        from matplotlib.backends.backend_agg import FigureCanvasAgg

        canvas = FigureCanvasAgg(claim_figure)
        canvas.draw()
        renderer = canvas.get_renderer()
        pieces = [("suptitle", claim_figure._suptitle), ("note", claim_figure.texts[-1])]
        for i, ax in enumerate(claim_figure.axes):
            pieces.append((f"title {i}", ax.title))
            pieces += [(f"text {i} {t.get_text()}", t) for t in ax.texts if t.get_text()]
            ticks = [*ax.get_xticklabels(), *ax.get_yticklabels()]
            pieces += [(f"tick {i} {t.get_text()}", t) for t in ticks if t.get_text()]
        boxes = [(name, artist.get_window_extent(renderer)) for name, artist in pieces]
        legend = claim_figure.axes[2].get_legend()
        boxes.append(("legend", legend.get_window_extent(renderer)))
        clashes = [
            (a, b)
            for i, (a, box_a) in enumerate(boxes)
            for b, box_b in boxes[i + 1 :]
            if box_a.overlaps(box_b)
        ]
        assert clashes == []

    def test_no_label_is_parsed_as_math(self, claim_figure) -> None:
        for text in [*claim_figure.texts, *(t for ax in claim_figure.axes for t in ax.texts)]:
            assert text.get_parse_math() is False


class TestTheClaimFiguresDefaultDraw:
    def test_the_default_draw_reads_the_full_span(self, tmp_path, claim_figure) -> None:
        fig = make_claim_figure(out=tmp_path / CLAIM_FIGURE)
        assert fig.claim == claim_figure.claim

    def test_the_figure_is_written_where_it_is_asked_to_be(self, claim_figure) -> None:
        assert claim_figure.written_to.is_file()
        assert claim_figure.written_to.stat().st_size > 0


def test_the_committed_claim_figure_exists() -> None:
    assert (FIGURES_DIR / CLAIM_FIGURE).is_file()


# The hurdle figure, which draws Lesson 2.


@pytest.fixture(scope="module")
def hurdle_figure(tmp_path_factory: pytest.TempPathFactory, result):
    out = tmp_path_factory.mktemp("risk_parity_hurdle") / HURDLE_FIGURE
    fig = make_hurdle_figure(out=out, result=result)
    fig.written_to = out
    return fig


def _hurdle_ticks(ax) -> list:
    """The short vertical bars that mark each row's hurdle."""
    return [
        line
        for line in ax.lines
        if line.get_marker() != "o"
        and len(line.get_xdata()) == 2
        and line.get_xdata()[0] == line.get_xdata()[1]
        and line.get_ydata()[0] != line.get_ydata()[1]
        and line.get_transform() == ax.transData
    ]


class TestWhatTheHurdleFigureCompares:
    def test_qians_legs_are_the_ones_his_paper_prints(self) -> None:
        """Volatilities and correlation from the text beside Table 1, Sharpe
        ratios from Table 2's index columns."""
        assert (QIAN_STOCK_VOL, QIAN_BOND_VOL, QIAN_CORRELATION) == (0.151, 0.046, 0.2)
        assert (QIAN_SHARPE_STOCK, QIAN_SHARPE_BOND) == (0.55, 0.80)

    def test_the_three_rows(self, hurdle_figure) -> None:
        """Qian's hurdle is about two-thirds and this run's about 0.53. His
        bonds earned about 1.45 times stocks' Sharpe ratio, and AGG about 0.46
        times at the bill average and about −0.39 times at 4%."""
        rows = hurdle_figure.rows
        assert [row.label for row in rows] == [
            "Qian, 1983 to 2004, cash at each month's bill rate",
            "SPY and AGG, 2003 to 2026, cash at the 1.74% bill average",
            "SPY and AGG, 2003 to 2026, cash at an assumed 4%",
        ]
        assert [row.hurdle for row in rows] == [
            pytest.approx(0.657479, abs=5e-7),
            pytest.approx(0.526178, abs=5e-7),
            pytest.approx(0.526178, abs=5e-7),
        ]
        assert [row.ratio for row in rows] == [
            pytest.approx(0.80 / 0.55, abs=1e-12),
            pytest.approx(0.456266, abs=5e-7),
            pytest.approx(-0.390912, abs=5e-7),
        ]
        assert [row.clears for row in rows] == [True, False, False]

    def test_this_runs_rows_come_from_the_run(self, hurdle_figure, result) -> None:
        legs = result.legs
        hurdle = bond_sharpe_hurdle(legs.stock_vol, legs.bond_vol, legs.correlation)
        for row, rate in zip(hurdle_figure.rows[1:], (BILL_AVERAGE, RISK_FREE), strict=True):
            assert (row.stock_sharpe, row.bond_sharpe) == leg_sharpes(legs, risk_free=rate)
            assert row.hurdle == hurdle

    def test_clearing_the_hurdle_is_leading_the_comparison(self, hurdle_figure) -> None:
        """Each of this run's rows agrees with the ranking the claim figure
        draws at the same rate, and Qian's agrees with his printed pair."""
        rows = hurdle_figure.rows
        assert rows[0].clears == (QIAN_SHARPE_PARITY > QIAN_SHARPE_BENCHMARK)
        for row, rate in zip(rows[1:], (BILL_AVERAGE, RISK_FREE), strict=True):
            assert row.clears == (full_span_ranking(rate).sharpe_difference > 0)

    def test_the_title_matches_which_rows_clear(self, hurdle_figure) -> None:
        assert hurdle_figure._suptitle.get_text() == (
            "Qian's bonds cleared the hurdle risk parity needs, and AGG's did not"
        )
        assert [row.clears for row in hurdle_figure.rows] == [True, False, False]


class TestTheHurdlePanel:
    def test_each_row_draws_its_hurdle_its_dot_and_its_zone(self, hurdle_figure) -> None:
        ax = hurdle_figure.axes[0]
        rows = hurdle_figure.rows
        dots = _dots(ax)
        ticks = _hurdle_ticks(ax)
        zones = [p for p in ax.patches]
        assert len(dots) == len(ticks) == len(zones) == len(rows)
        ys = [dot.get_ydata()[0] for dot in dots]
        assert ys == sorted(ys, reverse=True)
        for row, y, dot, tick, zone in zip(rows, ys, dots, ticks, zones, strict=True):
            assert dot.get_xdata()[0] == pytest.approx(row.ratio, abs=1e-12)
            assert _filled(dot) and _rgb(dot.get_color()) == _rgb(ACCENT)
            assert list(tick.get_xdata()) == pytest.approx([row.hurdle, row.hurdle], abs=1e-12)
            low, high = tick.get_ydata()
            assert low < y < high
            assert zone.get_x() == pytest.approx(row.hurdle, abs=1e-12)
            assert zone.get_x() + zone.get_width() == pytest.approx(HURDLE_XLIM[1], abs=1e-12)
            assert zone.get_y() < y < zone.get_y() + zone.get_height()
            assert _rgb(zone.get_facecolor()) == _rgb(GOOD)

    def test_each_dot_and_hurdle_carries_its_value(self, hurdle_figure) -> None:
        ax = hurdle_figure.axes[0]
        texts = _plain_texts(ax)
        assert [t for t in texts if t.startswith("hurdle")] == [
            "hurdle 0.66",
            "hurdle 0.53",
            "hurdle 0.53",
        ]
        # Below its tick, so it stays clear of the row's title and detail lines.
        hurdle_labels = [t for t in ax.texts if t.get_text().startswith("hurdle")]
        ys = [dot.get_ydata()[0] for dot in _dots(ax)]
        for row, y, label in zip(hurdle_figure.rows, ys, hurdle_labels, strict=True):
            assert label.xy == pytest.approx((row.hurdle, y - 0.24), abs=1e-12)
            assert label.get_va() == "top" and label.xyann[1] < 0
        values = [t for t in ax.texts if re.fullmatch(r"−?\d\.\d\d", t.get_text())]
        assert [t.get_text() for t in values] == ["1.45", "0.46", "−0.39"]
        for row, label in zip(hurdle_figure.rows, values, strict=True):
            assert label.xy[0] == pytest.approx(row.ratio, abs=1e-12)
            outward = row.ratio >= row.hurdle
            assert label.get_ha() == ("left" if outward else "right")
            assert (label.xyann[0] > 0) == outward

    def test_each_row_names_its_data_and_both_sharpe_ratios(self, hurdle_figure) -> None:
        ax = hurdle_figure.axes[0]
        rows = hurdle_figure.rows
        details = [t for t in ax.texts if t.get_text().startswith("bonds ")]
        assert [t.get_text() for t in details] == [
            "bonds 0.80, stocks 0.55",
            "bonds 0.26, stocks 0.57",
            "bonds −0.18, stocks 0.45",
        ]
        ys = [dot.get_ydata()[0] for dot in _dots(ax)]
        for row, y, detail in zip(rows, ys, details, strict=True):
            label = [t for t in ax.texts if t.get_text() == row.label][0]
            assert y < detail.get_position()[1] < label.get_position()[1] < y + 0.5

    def test_the_equal_sharpe_line_and_the_axis(self, hurdle_figure) -> None:
        ax = hurdle_figure.axes[0]
        dashed = [line for line in ax.lines if line.get_linestyle() == "--"]
        assert len(dashed) == 1 and list(dashed[0].get_xdata()) == [1.0, 1.0]
        assert "equal Sharpe ratios" in _plain_texts(ax)
        assert ax.get_xlim() == HURDLE_XLIM
        assert ax.get_yticks().size == 0
        assert ax.get_xlabel() == "bonds' Sharpe ratio as a multiple of stocks'"
        hurdle_figure.canvas.draw()
        assert [t.get_text() for t in ax.get_xticklabels()] == ["−0.5", "0.0", "0.5", "1.0", "1.5"]

    def test_the_legend_names_each_mark(self, hurdle_figure) -> None:
        legend = hurdle_figure.axes[0].get_legend()
        assert [t.get_text() for t in legend.get_texts()] == [
            "where bonds landed",
            "hurdle",
            "risk parity leads",
        ]


class TestTheHurdleFiguresText:
    def test_the_note(self, hurdle_figure) -> None:
        note = hurdle_figure.texts[-1].get_text()
        assert note.split("\n") == [
            "The hurdle is the multiple of stocks' Sharpe ratio at which levered risk parity "
            "and 60/40 earn the same",
            "Sharpe ratio at the same volatility. It depends on the two volatilities and their "
            "correlation, not on the cash rate.",
            "Qian (2005): stocks 15.1%, bonds 4.6%, correlation 0.2. SPY and AGG: 18.55% and "
            "5.17%, correlation −0.0002,",
            "2003-09-30 to 2026-09-17, 2026 downloads. 1.74% is the St. Louis Fed's average "
            "three-month bill rate, not stored here.",
            "4% is the cash rate Chan assumes elsewhere in the book.",
        ]

    def test_text_fits_and_nothing_overlaps(self, hurdle_figure) -> None:
        from matplotlib.backends.backend_agg import FigureCanvasAgg

        canvas = FigureCanvasAgg(hurdle_figure)
        canvas.draw()
        renderer = canvas.get_renderer()
        ax = hurdle_figure.axes[0]
        pieces = [hurdle_figure._suptitle, hurdle_figure.texts[-1], ax.xaxis.label]
        pieces += [t for t in ax.texts if t.get_text()]
        pieces += [t for t in [*ax.get_xticklabels()] if t.get_text()]
        boxes = [(p.get_text(), p.get_window_extent(renderer)) for p in pieces]
        boxes.append(("legend", ax.get_legend().get_window_extent(renderer)))
        assert max(box.x1 for _, box in boxes) <= hurdle_figure.bbox.x1
        clashes = [
            (a, b)
            for i, (a, box_a) in enumerate(boxes)
            for b, box_b in boxes[i + 1 :]
            if box_a.overlaps(box_b)
        ]
        assert clashes == []

    def test_no_label_is_parsed_as_math(self, hurdle_figure) -> None:
        for text in [*hurdle_figure.texts, *hurdle_figure.axes[0].texts]:
            assert text.get_parse_math() is False


class TestTheHurdleFiguresDefaultDraw:
    def test_the_default_draw_reads_the_full_span(self, tmp_path, hurdle_figure) -> None:
        fig = make_hurdle_figure(out=tmp_path / HURDLE_FIGURE)
        assert fig.rows == hurdle_figure.rows == hurdle_rows()

    def test_the_figure_is_written_where_it_is_asked_to_be(self, hurdle_figure) -> None:
        assert hurdle_figure.written_to.is_file()
        assert hurdle_figure.written_to.stat().st_size > 0


def test_the_committed_hurdle_figure_exists() -> None:
    assert (FIGURES_DIR / HURDLE_FIGURE).is_file()
