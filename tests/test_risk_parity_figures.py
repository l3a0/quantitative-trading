"""The pins for the risk parity post's five figures.

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
    BOOK_RATIO_BAND,
    BOOK_WEIGHTS,
    RISK_FREE,
    bond_sharpe_hurdle,
    book_correlation_band,
    correlation_from_leverage,
    leg_sharpes,
    leverage_from_correlation,
)
from chan.risk_parity_figures import (
    ACCENT,
    BILL_AVERAGE,
    CLAIM_FIGURE,
    CURVE_STEPS,
    DECODE_CORRELATIONS,
    DECODE_FIGURE,
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
    RATE_FIGURE,
    RATE_MARGIN,
    RATE_RANGE,
    RATE_STEPS,
    SPLIT_FIGURE,
    SURFACE,
    T_BAR,
    decoding,
    full_span,
    full_span_ranking,
    hurdle_rows,
    make_claim_figure,
    make_decode_figure,
    make_hurdle_figure,
    make_rate_figure,
    make_risk_split_figure,
    qian_ratio_span,
    rate_line,
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
            "not stored with the replication's data.",
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
        """Volatilities and correlation from page 1, with the volatilities
        again in Table 2's standard deviation row, and Sharpe ratios from
        Table 2's index columns."""
        assert (QIAN_STOCK_VOL, QIAN_BOND_VOL, QIAN_CORRELATION) == (0.151, 0.046, 0.2)
        assert (QIAN_SHARPE_STOCK, QIAN_SHARPE_BOND) == (0.55, 0.80)

    def test_the_three_rows(self, hurdle_figure) -> None:
        """Qian's hurdle is about two-thirds and this run's about 0.53. His
        bonds earned about 1.45 times stocks' Sharpe ratio, and AGG about 0.46
        times at the bill average and about −0.39 times at 4%. Only Qian's row
        rests on a source's rounded inputs."""
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
        assert [row.approximate for row in rows] == [True, False, False]

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

    def test_the_title_matches_which_rows_clear_and_by_how_much(self, hurdle_figure) -> None:
        """AGG misses by under a tenth of stocks' Sharpe ratio at the bill
        average, which is what narrowly means here, and by more than 0.9 at 4%."""
        assert hurdle_figure._suptitle.get_text() == (
            "Qian's bonds cleared the hurdle, and AGG's fell short, narrowly at the bill average"
        )
        rows = hurdle_figure.rows
        assert [row.clears for row in rows] == [True, False, False]
        assert 0 < rows[1].hurdle - rows[1].ratio < 0.1
        assert rows[2].hurdle - rows[2].ratio > 0.9


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
            assert zone.get_height() < 0.4
            assert _rgb(zone.get_facecolor()) == _rgb(GOOD)
            assert zone.get_alpha() < 0.5
            assert _rgb(tick.get_color()) == _rgb(INK)

    def test_each_dot_and_hurdle_carries_its_value(self, hurdle_figure) -> None:
        ax = hurdle_figure.axes[0]
        texts = _plain_texts(ax)
        assert [t for t in texts if t.startswith("hurdle")] == [
            "hurdle about 2/3",
            "hurdle 0.53",
            "hurdle 0.53",
        ]
        # Below its tick, so it stays clear of the row's title and detail lines.
        hurdle_labels = [t for t in ax.texts if t.get_text().startswith("hurdle")]
        ys = [dot.get_ydata()[0] for dot in _dots(ax)]
        for row, y, label in zip(hurdle_figure.rows, ys, hurdle_labels, strict=True):
            assert label.xy == pytest.approx((row.hurdle, y - 0.24), abs=1e-12)
            assert label.get_va() == "top" and label.xyann[1] < 0
        values = [t for t in ax.texts if re.fullmatch(r"(about )?−?\d\.\d\d", t.get_text())]
        assert [t.get_text() for t in values] == ["about 1.45", "0.46", "−0.39"]
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
        dot, tick, zone = legend.legend_handles
        assert _rgb(dot.get_color()) == _rgb(ACCENT)
        assert _rgb(tick.get_color()) == _rgb(INK)
        assert _rgb(zone.get_facecolor()) == _rgb(GOOD)


class TestTheHurdleFiguresText:
    def test_the_note(self, hurdle_figure) -> None:
        note = hurdle_figure.texts[-1].get_text()
        assert note.split("\n") == [
            "The hurdle is the multiple of stocks' Sharpe ratio at which levered risk parity "
            "and 60/40 earn the same",
            "Sharpe ratio at the same volatility. It depends on the two volatilities and their "
            "correlation, not on the cash rate.",
            "Qian's is computed here from his rounded inputs: stocks 15.1%, bonds 4.6%, "
            "correlation 0.2 (Qian, 2005).",
            "SPY and AGG: 18.55% and 5.17%, correlation −0.0002, 2003-09-30 to 2026-09-17, "
            "2026 downloads. Each multiple",
            "divides unrounded Sharpe ratios. AGG's multiple meets the hurdle with cash at "
            "1.50%, the rate where the two Sharpe ratios tie.",
            "1.74% is the St. Louis Fed's average three-month bill rate, not stored with the "
            "replication's data. 4% is the rate Chan assumes.",
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


def test_the_command_writes_all_five_and_says_where(
    tmp_path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """``main`` is the redraw command README names, so it has to write every
    committed figure. The save helper lives in ``chan.coin_flip_figures``, so
    both modules' figure directory is redirected."""
    import chan.coin_flip_figures as shared
    import chan.risk_parity_figures as figures

    monkeypatch.setattr(figures, "FIGURES_DIR", tmp_path)
    monkeypatch.setattr(shared, "FIGURES_DIR", tmp_path)
    figures.main()
    out = capsys.readouterr().out
    for name in (SPLIT_FIGURE, CLAIM_FIGURE, HURDLE_FIGURE, DECODE_FIGURE, RATE_FIGURE):
        assert f"wrote {tmp_path / name}" in out
        assert (tmp_path / name).is_file()


# The decode figure, which draws Lesson 3.


@pytest.fixture(scope="module")
def decode_figure(tmp_path_factory: pytest.TempPathFactory, result):
    out = tmp_path_factory.mktemp("risk_parity_decode") / DECODE_FIGURE
    fig = make_decode_figure(out=out, result=result)
    fig.written_to = out
    return fig


class TestWhatTheDecodeFigureDraws:
    def test_the_ratio_band_and_the_four_ratios(self, decode_figure) -> None:
        """Weights rounding to 23-77 allow 3.26 to 3.44. Qian's rounded
        volatilities allow 3.24 to 3.33, which overlaps that band without
        sitting inside it. SPY and AGG give 3.59 over the whole period, 3.87 up
        to March 2022 and 2.76 after, and all three miss both ranges."""
        drawn = decode_figure.decoding
        assert drawn.ratio_band == BOOK_RATIO_BAND
        assert [(m.label, m.span is not None) for m in drawn.ratios] == [
            ("Qian, 1983 to 2004", True),
            ("SPY and AGG, 2003 to 2026", False),
            ("SPY and AGG, to March 2022", False),
            ("SPY and AGG, from March 2022", False),
        ]
        assert [m.ratio for m in drawn.ratios] == [
            pytest.approx(0.151 / 0.046, abs=1e-12),
            pytest.approx(3.590935, abs=5e-7),
            pytest.approx(3.869974, abs=5e-7),
            pytest.approx(2.755525, abs=5e-7),
        ]
        low, high = drawn.ratio_band
        span_low, span_high = drawn.ratios[0].span
        assert (span_low, span_high) == qian_ratio_span()
        assert (span_low, span_high) == pytest.approx((0.1505 / 0.0465, 0.1515 / 0.0455))
        assert span_low < low < span_high < high
        for mark in drawn.ratios[1:]:
            assert not (min(low, span_low) <= mark.ratio <= max(high, span_high))
        # The two sides of 2022 sit on opposite sides of the band, which Lesson 6 takes up.
        assert drawn.ratios[2].ratio > high and drawn.ratios[3].ratio < low

    def test_the_ratios_are_the_runs(self, decode_figure, result) -> None:
        assert decode_figure.decoding.ratios[1].ratio == result.legs.vol_ratio

    def test_the_two_leverage_points(self, decode_figure) -> None:
        """Qian's 1.8 reads as a correlation of 0.16 on his weights, and SPY and
        AGG sit at 1.98 and −0.0002 on theirs."""
        drawn = decode_figure.decoding
        assert (drawn.qian.stock_weight, drawn.qian.leverage) == (BOOK_WEIGHTS[0], BOOK_LEVERAGE)
        assert drawn.qian.correlation == correlation_from_leverage(BOOK_LEVERAGE)
        assert drawn.qian.correlation == pytest.approx(0.157879, abs=5e-7)
        assert drawn.run.stock_weight == pytest.approx(0.217821, abs=5e-7)
        assert drawn.run.correlation == pytest.approx(-0.000215, abs=5e-7)
        assert drawn.run.leverage == pytest.approx(1.981188, abs=5e-7)
        assert drawn.qian_printed_correlation == 0.2

    def test_each_point_sits_on_its_own_curve(self, decode_figure) -> None:
        """The leverage that matches 60/40 on SPY and AGG's own weights, read
        off the map at their measured correlation, is the leverage the run
        measured, so the map and the measurement agree."""
        drawn = decode_figure.decoding
        for point in (drawn.qian, drawn.run):
            weights = (point.stock_weight, 1.0 - point.stock_weight)
            assert leverage_from_correlation(point.correlation, weights=weights) == pytest.approx(
                point.leverage, abs=1e-9
            )

    def test_the_correlation_band(self, decode_figure) -> None:
        band = decode_figure.decoding.correlation_band
        assert band == book_correlation_band()
        assert band == pytest.approx((-0.012650, 0.371407), abs=5e-6)
        assert band[0] < decode_figure.decoding.qian.correlation < band[1]
        assert band[0] < decode_figure.decoding.qian_printed_correlation < band[1]


class TestTheRatioPanel:
    def test_each_ratio_sits_on_its_row_as_a_dot_or_a_bar(self, decode_figure) -> None:
        """Measured ratios are dots. Qian's, from rounded figures, is a bar
        across the ratios his rounding allows."""
        ax = decode_figure.axes[0]
        rows = _row_of(ax)
        marks = decode_figure.decoding.ratios
        dots = _dots(ax)
        assert [(d.get_xdata()[0], d.get_ydata()[0]) for d in dots] == [
            pytest.approx((m.ratio, rows[m.label]), abs=1e-12) for m in marks[1:]
        ]
        assert all(_filled(d) and _rgb(d.get_color()) == _rgb(ACCENT) for d in dots)
        (bar,) = [line for line in ax.lines if line.get_marker() != "o"]
        assert list(bar.get_xdata()) == pytest.approx(list(marks[0].span), abs=1e-12)
        assert list(bar.get_ydata()) == [rows[marks[0].label]] * 2
        assert _rgb(bar.get_color()) == _rgb(ACCENT) and bar.get_linewidth() >= 5
        ys = [rows[m.label] for m in marks]
        assert ys == sorted(ys, reverse=True)

    def test_each_dot_carries_its_value_beside_it(self, decode_figure) -> None:
        ax = decode_figure.axes[0]
        values = [t for t in ax.texts if re.fullmatch(r"(about )?\d\.\d\d?", t.get_text())]
        assert [t.get_text() for t in values] == ["about 3.3", "3.59", "3.87", "2.76"]
        for mark, label in zip(decode_figure.decoding.ratios, values, strict=True):
            end = mark.span[1] if mark.span is not None else mark.ratio
            assert label.xy[0] == end
            assert label.get_ha() == "left" and label.xyann[0] > 0

    def test_the_band_is_the_rounding_band(self, decode_figure) -> None:
        ax = decode_figure.axes[0]
        (band,) = ax.patches
        low, high = BOOK_RATIO_BAND
        assert (band.get_x(), band.get_x() + band.get_width()) == pytest.approx(
            (low, high), abs=1e-12
        )
        assert _rgb(band.get_facecolor()) == _rgb(GOOD)
        assert 0 < band.get_alpha() < 0.5
        assert "what 23-77 allows" in _plain_texts(ax)

    def test_the_axis(self, decode_figure) -> None:
        ax = decode_figure.axes[0]
        assert ax.get_xlim() == (2.5, 4.25)
        decode_figure.canvas.draw()
        assert [t.get_text() for t in ax.get_xticklabels()] == ["2.5×", "3×", "3.5×", "4×"]


class TestTheLeveragePanel:
    def test_each_curve_is_the_map_on_its_weights(self, decode_figure) -> None:
        ax = decode_figure.axes[1]
        drawn = decode_figure.decoding
        curves = [line for line in ax.lines if len(line.get_xdata()) > 2][2:]
        assert len(curves) == 2
        for curve, point, style in zip(curves, (drawn.qian, drawn.run), ("-", "--"), strict=True):
            xs, ys = curve.get_xdata(), curve.get_ydata()
            assert (xs[0], xs[-1]) == DECODE_CORRELATIONS
            assert len(xs) == CURVE_STEPS + 1 and CURVE_STEPS >= 200
            weights = (point.stock_weight, 1.0 - point.stock_weight)
            assert list(ys) == pytest.approx(
                [leverage_from_correlation(x, weights=weights) for x in xs], abs=1e-12
            )
            assert curve.get_linestyle() == style
        assert _rgb(curves[0].get_color()) == _rgb(INK)
        assert _rgb(curves[1].get_color()) == _rgb(MUTED)

    def test_the_band_edges_are_where_the_rounding_curves_cross_the_rounded_leverage(
        self, decode_figure
    ) -> None:
        """The band is not read off the solid curve. Its low edge is where the
        curve for a 23.5% stock weight meets 1.85, and its high edge where the
        curve for 22.5% meets 1.75, so both rounding curves are drawn."""
        ax = decode_figure.axes[1]
        drawn = decode_figure.decoding
        assert drawn.rounding_weights == pytest.approx((0.225, 0.235), abs=1e-12)
        assert drawn.rounding_leverages == pytest.approx((1.75, 1.85), abs=1e-12)
        faint = [line for line in ax.lines if len(line.get_xdata()) > 2][:2]
        for line, weight in zip(faint, drawn.rounding_weights, strict=True):
            weights = (weight, 1.0 - weight)
            assert list(line.get_ydata()) == pytest.approx(
                [leverage_from_correlation(x, weights=weights) for x in line.get_xdata()],
                abs=1e-12,
            )
            assert _rgb(line.get_color()) == _rgb(INK) and line.get_alpha() < 0.5
        low, high = drawn.correlation_band
        w_low, w_high = drawn.rounding_weights
        l_low, l_high = drawn.rounding_leverages
        assert leverage_from_correlation(low, weights=(w_high, 1 - w_high)) == pytest.approx(l_high)
        assert leverage_from_correlation(high, weights=(w_low, 1 - w_low)) == pytest.approx(l_low)
        spans = [p for p in ax.patches if p.get_width() > 0.9]
        assert len(spans) == 1
        assert (spans[0].get_y(), spans[0].get_y() + spans[0].get_height()) == pytest.approx(
            (l_low, l_high), abs=1e-12
        )
        assert "1.8's rounding" in _plain_texts(ax)

    def test_each_point_is_drawn_and_labelled(self, decode_figure) -> None:
        ax = decode_figure.axes[1]
        drawn = decode_figure.decoding
        dots = _dots(ax)
        assert [(d.get_xdata()[0], d.get_ydata()[0]) for d in dots] == [
            pytest.approx((p.correlation, p.leverage), abs=1e-12) for p in (drawn.qian, drawn.run)
        ]
        assert all(_filled(d) and _rgb(d.get_color()) == _rgb(ACCENT) for d in dots)
        labels = [t for t in ax.texts if " at " in t.get_text()]
        assert [t.get_text() for t in labels] == ["1.8 at 0.16", "1.98 at −0.0002"]
        for dot, label in zip(dots, labels, strict=True):
            assert label.xy == pytest.approx((dot.get_xdata()[0], dot.get_ydata()[0]))
        # Qian's sits below and left of its dot, clear of the curves above it.
        assert labels[0].xyann[0] < 0 and labels[0].xyann[1] < 0
        assert labels[1].xyann[0] > 0 and labels[1].xyann[1] > 0

    def test_the_band_and_the_printed_correlation(self, decode_figure) -> None:
        ax = decode_figure.axes[1]
        (band,) = [p for p in ax.patches if p.get_width() < 0.9]
        low, high = decode_figure.decoding.correlation_band
        assert (band.get_x(), band.get_x() + band.get_width()) == pytest.approx(
            (low, high), abs=1e-12
        )
        assert _rgb(band.get_facecolor()) == _rgb(GOOD)
        assert 0 < band.get_alpha() < 0.5
        dotted = [line for line in ax.lines if line.get_linestyle() == ":"]
        assert len(dotted) == 1 and list(dotted[0].get_xdata()) == [0.2, 0.2]
        texts = _plain_texts(ax)
        assert "what 23-77 and 1.8 allow" in texts
        assert "his paper prints 0.2" in texts

    def test_the_legend_names_both_curves(self, decode_figure) -> None:
        legend = decode_figure.axes[1].get_legend()
        assert [t.get_text() for t in legend.get_texts()] == [
            "ends of 23-77's rounding",
            "Qian's 23-77 weights",
            "SPY and AGG's 21.8% weights",
        ]
        faint, solid, dashed = legend.get_lines()
        assert faint.get_alpha() < 0.5
        assert solid.get_linestyle() == "-" and dashed.get_linestyle() == "--"

    def test_the_axes(self, decode_figure) -> None:
        ax = decode_figure.axes[1]
        assert ax.get_xlim() == DECODE_CORRELATIONS
        assert ax.get_ylim() == (1.5, 2.4)
        assert ax.get_xlabel() == "stock-bond correlation"


class TestTheDecodeFiguresText:
    def test_the_titles(self, decode_figure) -> None:
        assert decode_figure._suptitle.get_text() == (
            "Qian's weights stand for a volatility ratio, and his leverage for a correlation"
        )
        assert [ax.get_title(loc="left") for ax in decode_figure.axes] == [
            "Weights: stocks' volatility over bonds'",
            "Leverage to match 60/40, by correlation",
        ]

    def test_the_note(self, decode_figure) -> None:
        assert decode_figure.texts[-1].get_text().split("\n") == [
            "Risk parity sets each weight times its volatility equal, so 23-77 says stocks were "
            "77/23 times as volatile as bonds.",
            "Weights that round to 23 and 77 allow 3.26 to 3.44. Qian's (2005) 15.1% and 4.6% "
            "allow 3.24 to 3.33 once rounded.",
            "Given the weights, the leverage that matches 60/40 depends only on the correlation. "
            "The band's edges, −0.01 and +0.37,",
            "are where the faint curves cross the ends of 1.8's rounding. The split is the "
            "Federal Reserve's first rate rise of 2022, on 16 March.",
            "SPY and AGG: 2003-09-30 to 2026-09-17, 2026 downloads.",
        ]

    def test_text_fits_and_nothing_overlaps(self, decode_figure) -> None:
        from matplotlib.backends.backend_agg import FigureCanvasAgg

        canvas = FigureCanvasAgg(decode_figure)
        canvas.draw()
        renderer = canvas.get_renderer()
        pieces = [decode_figure._suptitle, decode_figure.texts[-1]]
        for ax in decode_figure.axes:
            pieces += [ax.title, ax.xaxis.label]
            pieces += [t for t in ax.texts if t.get_text()]
            pieces += [t for t in [*ax.get_xticklabels(), *ax.get_yticklabels()] if t.get_text()]
        boxes = [(p.get_text(), p.get_window_extent(renderer)) for p in pieces]
        boxes.append(("legend", decode_figure.axes[1].get_legend().get_window_extent(renderer)))
        assert min(box.x0 for _, box in boxes) >= 0
        assert max(box.x1 for _, box in boxes) <= decode_figure.bbox.x1
        clashes = [
            (a, b)
            for i, (a, box_a) in enumerate(boxes)
            for b, box_b in boxes[i + 1 :]
            if box_a.overlaps(box_b) and a and b
        ]
        assert clashes == []

    def test_no_label_is_parsed_as_math(self, decode_figure) -> None:
        for text in [*decode_figure.texts, *(t for ax in decode_figure.axes for t in ax.texts)]:
            assert text.get_parse_math() is False


def test_the_decode_figures_default_draw_reads_the_full_span(tmp_path, decode_figure) -> None:
    fig = make_decode_figure(out=tmp_path / DECODE_FIGURE)
    assert fig.decoding == decode_figure.decoding == decoding()


def test_the_committed_decode_figure_exists() -> None:
    assert (FIGURES_DIR / DECODE_FIGURE).is_file()


# The rate figure, which draws Lesson 4.


@pytest.fixture(scope="module")
def rate_figure(tmp_path_factory: pytest.TempPathFactory, result):
    out = tmp_path_factory.mktemp("risk_parity_rate") / RATE_FIGURE
    fig = make_rate_figure(out=out, result=result)
    fig.written_to = out
    return fig


class TestWhatTheRateFigureDraws:
    def test_the_tie_and_where_the_data_settles_it(self, rate_figure) -> None:
        """The same 1.50% and 3.80% ``tests/test_risk_parity.py`` pins in
        closed form, reached here through the drawn line."""
        drawn = rate_figure.rate_line
        assert drawn.tie == pytest.approx(0.014977, abs=5e-7)
        assert drawn.resolves_below == pytest.approx(0.038011, abs=5e-7)

    def test_the_three_marked_rates(self, rate_figure) -> None:
        """At a zero rate risk parity leads by 0.13 with a t of +1.30. At the
        bill average 60/40 leads by 0.02, and at 4% by 0.22 with a t of −2.17."""
        marks = rate_figure.rate_line.marks
        assert [m.rate for m in marks] == [0.0, BILL_AVERAGE, RISK_FREE]
        assert [(m.gap, m.t) for m in marks] == [
            pytest.approx((0.129838, 1.300398), abs=5e-7),
            pytest.approx((-0.021007, -0.210392), abs=5e-7),
            pytest.approx((-0.216931, -2.172682), abs=5e-7),
        ]

    def test_the_line_is_the_ranking_at_every_rate_it_draws(self, rate_figure) -> None:
        line = rate_figure.rate_line.line
        low, high = RATE_RANGE
        assert len(line) == RATE_STEPS + 1
        assert (line[0].rate, line[-1].rate) == (low, high)
        for point in line[:: RATE_STEPS // 5]:
            ranking = full_span_ranking(point.rate)
            assert (point.gap, point.t) == (ranking.sharpe_difference, ranking.t_newey_west)

    def test_the_gap_and_the_t_move_in_a_straight_line(self, rate_figure) -> None:
        """The note says so, and the tie and the 3.80% are roots of lines, so
        every drawn point has to sit on the line through the two ends."""
        line = rate_figure.rate_line.line
        first, last = line[0], line[-1]
        for point in line:
            share = (point.rate - first.rate) / (last.rate - first.rate)
            assert point.gap == pytest.approx(first.gap + share * (last.gap - first.gap), abs=1e-9)
            assert point.t == pytest.approx(first.t + share * (last.t - first.t), abs=1e-9)

    def test_only_the_shaded_rates_settle_it(self, rate_figure) -> None:
        """The title says only rates above 3.80% settle the comparison. No
        drawn rate gives risk parity a t past +2, and every rate whose t is
        past −2 is inside the shading."""
        drawn = rate_figure.rate_line
        assert max(p.t for p in drawn.line) < T_BAR
        for point in drawn.line:
            assert (point.t < -T_BAR) == (point.rate > drawn.resolves_below)


class TestTheRatePanel:
    def test_the_line_and_the_zero_line(self, rate_figure) -> None:
        ax = rate_figure.axes[0]
        drawn = rate_figure.rate_line
        (curve,) = [line for line in ax.lines if len(line.get_xdata()) > 2]
        assert list(curve.get_xdata()) == [p.rate for p in drawn.line]
        assert list(curve.get_ydata()) == [p.gap for p in drawn.line]
        assert _rgb(curve.get_color()) == _rgb(ACCENT)
        zero = [line for line in ax.lines if list(line.get_ydata()) == [0, 0]]
        assert len(zero) == 1 and _rgb(zero[0].get_color()) == _rgb(INK)

    def test_the_marks_and_the_tie(self, rate_figure) -> None:
        ax = rate_figure.axes[0]
        drawn = rate_figure.rate_line
        dots = _dots(ax)
        tie, *marks = dots
        assert (tie.get_xdata()[0], tie.get_ydata()[0]) == (drawn.tie, 0.0)
        assert _rgb(tie.get_markerfacecolor()) == _rgb(SURFACE)
        assert _rgb(tie.get_markeredgecolor()) == _rgb(INK)
        assert [(d.get_xdata()[0], d.get_ydata()[0]) for d in marks] == [
            (m.rate, m.gap) for m in drawn.marks
        ]
        assert all(_filled(d) and _rgb(d.get_color()) == _rgb(ACCENT) for d in marks)

    def test_each_mark_states_its_leader_gap_and_t(self, rate_figure) -> None:
        ax = rate_figure.axes[0]
        labels = [t for t in ax.texts if "ahead by" in t.get_text()]
        assert [t.get_text() for t in labels] == [
            "cash at 0%\nrisk parity ahead by 0.13, t = +1.30",
            "1.74% bill average\n60/40 ahead by 0.02, t = −0.21",
            "cash at 4%\n60/40 ahead by 0.22, t = −2.17",
        ]
        for mark, label in zip(rate_figure.rate_line.marks, labels, strict=True):
            assert label.xy == (mark.rate, mark.gap)
        # The first sits above and right of its dot, and the other two below
        # and left, where the falling line leaves room.
        assert labels[0].xyann[0] > 0 and labels[0].xyann[1] > 0
        assert all(label.xyann[0] < 0 and label.xyann[1] < 0 for label in labels[1:])
        tie = [t for t in ax.texts if t.get_text() == "tie at 1.50%"]
        assert len(tie) == 1 and tie[0].xyann[0] > 0 and tie[0].xyann[1] > 0

    def test_the_shading_runs_from_the_settling_rate_to_the_edge(self, rate_figure) -> None:
        ax = rate_figure.axes[0]
        drawn = rate_figure.rate_line
        (shade,) = ax.patches
        assert shade.get_x() == pytest.approx(drawn.resolves_below, abs=1e-12)
        assert shade.get_x() + shade.get_width() == pytest.approx(RATE_RANGE[1], abs=1e-12)
        assert 0 < shade.get_alpha() < 0.5
        texts = _plain_texts(ax)
        assert "the data names 60/40\nabove 3.80%" in texts
        assert "risk parity leads" in texts and "60/40 leads" in texts

    def test_the_axes(self, rate_figure) -> None:
        ax = rate_figure.axes[0]
        assert ax.get_xlim() == (RATE_RANGE[0] - RATE_MARGIN, RATE_RANGE[1])
        assert ax.get_ylim() == (-0.33, 0.2)
        assert ax.get_xlabel() == "assumed cash rate"
        assert ax.get_ylabel() == "risk parity's Sharpe ratio minus 60/40's"
        rate_figure.canvas.draw()
        assert [t.get_text() for t in ax.get_xticklabels()] == [
            "0%",
            "1%",
            "2%",
            "3%",
            "4%",
            "5%",
        ]


class TestTheRateFiguresText:
    def test_the_title_and_note(self, rate_figure) -> None:
        assert rate_figure._suptitle.get_text() == (
            "The cash rate decides which portfolio leads, and only rates above 3.80% settle it"
        )
        assert rate_figure.texts[-1].get_text().split("\n") == [
            "SPY and AGG, 2003-09-30 to 2026-09-17, 2026 downloads, both portfolios at the same "
            "volatility. The gap and its t-statistic",
            "move in a straight line with the rate. The shading is where the t-statistic, "
            "corrected for day-to-day dependence, is beyond −2.",
            "1.74% is the St. Louis Fed's average three-month bill rate, not stored with the "
            "replication's data. 4% is the rate Chan assumes.",
        ]

    def test_text_fits_and_nothing_overlaps(self, rate_figure) -> None:
        from matplotlib.backends.backend_agg import FigureCanvasAgg

        canvas = FigureCanvasAgg(rate_figure)
        canvas.draw()
        renderer = canvas.get_renderer()
        ax = rate_figure.axes[0]
        pieces = [rate_figure._suptitle, rate_figure.texts[-1], ax.xaxis.label, ax.yaxis.label]
        pieces += [t for t in ax.texts if t.get_text()]
        pieces += [t for t in [*ax.get_xticklabels(), *ax.get_yticklabels()] if t.get_text()]
        boxes = [(p.get_text(), p.get_window_extent(renderer)) for p in pieces]
        assert min(box.x0 for _, box in boxes) >= 0
        assert max(box.x1 for _, box in boxes) <= rate_figure.bbox.x1
        clashes = [
            (a, b)
            for i, (a, box_a) in enumerate(boxes)
            for b, box_b in boxes[i + 1 :]
            if box_a.overlaps(box_b)
        ]
        assert clashes == []

    def test_no_label_runs_through_the_line(self, rate_figure) -> None:
        """An early draw ran the line straight through the bill average's label."""
        from matplotlib.backends.backend_agg import FigureCanvasAgg

        canvas = FigureCanvasAgg(rate_figure)
        canvas.draw()
        renderer = canvas.get_renderer()
        ax = rate_figure.axes[0]
        (curve,) = [line for line in ax.lines if len(line.get_xdata()) > 2]
        path = curve.get_transform().transform_path(curve.get_path())
        for text in ax.texts:
            if text.get_text():
                box = text.get_window_extent(renderer)
                assert not path.intersects_bbox(box, filled=False), text.get_text()

    def test_no_label_is_parsed_as_math(self, rate_figure) -> None:
        for text in [*rate_figure.texts, *rate_figure.axes[0].texts]:
            assert text.get_parse_math() is False


def test_the_rate_figures_default_draw_reads_the_full_span(tmp_path, rate_figure) -> None:
    fig = make_rate_figure(out=tmp_path / RATE_FIGURE)
    assert fig.rate_line == rate_figure.rate_line == rate_line()


def test_the_committed_rate_figure_exists() -> None:
    assert (FIGURES_DIR / RATE_FIGURE).is_file()
