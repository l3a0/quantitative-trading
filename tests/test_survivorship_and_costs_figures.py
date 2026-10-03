"""The pins for the survivorship and costs post's two figures.

``tests/test_khandani_lo.py`` and ``tests/test_survivorship_bias.py`` hold what
the two runs compute. This file holds that the figures draw those numbers, so a
generator that summed the wrong series or split the wrong bar fails even when
the arithmetic is right. Some numbers repeat here on purpose, because a
figure's labels are prose and the suite is the authority for every number prose
quotes. No test compares bytes, for the reason ``tests/test_regime_figure.py``
gives.

The cost figure reads ``spx_20071123/``, Chan's S&P 500 file, over 2006-01-03
to 2006-12-29 on the specifications ``tests/test_khandani_lo.py`` names. The
toy's figure reads no vintage, only the book's two printed tables.
"""

from __future__ import annotations

import numpy as np
import pytest
from matplotlib.colors import to_rgba
from matplotlib.dates import date2num

from chan.khandani_lo import daily_book
from chan.paths import FIGURES_DIR
from chan.survivorship_and_costs_figures import (
    ACCENT,
    CUMULATIVE_FIGURE,
    GOOD,
    LOST,
    TOY_FIGURE,
    chan_window_result,
    cumulative,
    make_cumulative_figure,
    make_toy_figure,
    toy_bars,
)
from chan.survivorship_bias import (
    SURVIVOR_PICKS,
    UNBIASED_PICKS,
    contributions,
    equal_capital_return,
    one_share_basis,
)
from chan.vintage import VintageUnavailable


@pytest.fixture(scope="module")
def result():
    return chan_window_result()


@pytest.fixture(scope="module")
def cumulative_out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("costs_figure") / CUMULATIVE_FIGURE


@pytest.fixture(scope="module")
def costs(cumulative_out, result):
    return make_cumulative_figure(out=cumulative_out, result=result)


@pytest.fixture(scope="module")
def toy_out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("toy_figure") / TOY_FIGURE


@pytest.fixture(scope="module")
def toy(toy_out):
    return make_toy_figure(out=toy_out)


def _rgb(colour) -> tuple[float, float, float]:
    return tuple(to_rgba(colour)[:3])


def _lines(ax) -> dict:
    return {line.get_gid(): line for line in ax.lines if line.get_gid()}


class TestTheRunningTotals:
    """What the cost figure sums, and where each line ends."""

    def test_each_line_is_the_days_profit_summed_over_the_mean_book(self, result) -> None:
        totals = cumulative(result)
        book = daily_book(result).book
        assert totals.before == pytest.approx(np.cumsum(result.pnl) / book, abs=1e-15)
        assert totals.after == pytest.approx(np.cumsum(result.pnl_charged) / book, abs=1e-15)

    def test_the_year_ends_up_1_3_percent_before_costs_and_down_16_9_after(self, result) -> None:
        totals = cumulative(result)
        assert totals.before[-1] == pytest.approx(0.013244, abs=5e-7)
        assert totals.after[-1] == pytest.approx(-0.168795, abs=5e-7)

    def test_the_drawn_lines_are_the_totals(self, costs) -> None:
        lines = _lines(costs.axes[0])
        totals = costs.totals
        assert list(lines["before"].get_ydata()) == pytest.approx(list(totals.before), abs=1e-15)
        assert list(lines["after"].get_ydata()) == pytest.approx(list(totals.after), abs=1e-15)
        assert len(lines["before"].get_xdata()) == 251

    def test_the_lines_wear_gain_and_loss(self, costs) -> None:
        lines = _lines(costs.axes[0])
        assert _rgb(lines["before"].get_color()) == _rgb(GOOD)
        assert _rgb(lines["after"].get_color()) == _rgb(LOST)

    def test_each_end_is_labelled_with_its_own_total(self, costs) -> None:
        assert [text.get_text() for text in costs.axes[0].texts] == [
            "before costs, +1.3%",
            "after 5 bp a side, −16.9%",
        ]

    def test_the_title_and_note_state_the_window_and_both_sharpe_ratios(self, costs) -> None:
        assert costs._suptitle.get_text() == (
            "Five basis points a side turn a +1.3% year into a −16.9% one"
        )
        note = costs.texts[-1].get_text()
        assert "Chan's S&P 500 file, 2006-01-03 to 2006-12-29" in note
        assert "over the year's mean gross position" in note
        assert "charges the first day's rebalance too" in note
        assert "Sharpe ratio 0.2510 before costs and −3.2337 after." in note


class TestWhereTheCostFigureDrawsIt:
    """The geometry, so a figure that drew the right numbers in the wrong
    place, on the wrong dates or behind a misread axis still fails."""

    def test_each_line_runs_forward_over_the_windows_own_days(self, costs, result) -> None:
        assert cumulative(result).days.equals(result.days)
        lines = _lines(costs.axes[0])
        for gid in ("before", "after"):
            assert list(lines[gid].get_xdata()) == list(result.days)

    def test_the_axes_hold_every_point_and_read_in_percent(self, costs) -> None:
        ax, totals = costs.axes[0], costs.totals
        low, high = ax.get_ylim()
        assert low < min(totals.after.min(), totals.before.min())
        assert high > max(totals.after.max(), totals.before.max())
        start, end = ax.get_xlim()
        assert start <= date2num(totals.days[0]) and end >= date2num(totals.days[-1])
        assert ax.yaxis.get_major_formatter().xmax == 1.0

    def test_each_end_mark_and_label_sits_on_its_lines_last_day(self, costs) -> None:
        ax, totals = costs.axes[0], costs.totals
        marks = [line for line in ax.lines if len(line.get_xdata()) == 1]
        last = totals.days[-1]
        assert [(m.get_xdata()[0], m.get_ydata()[0]) for m in marks] == [
            (last, totals.before[-1]),
            (last, totals.after[-1]),
        ]
        assert [_rgb(m.get_color()) for m in marks] == [_rgb(GOOD), _rgb(LOST)]
        assert [text.xy for text in ax.texts] == [
            (last, totals.before[-1]),
            (last, totals.after[-1]),
        ]


class TestWhereTheToyFigureDrawsIt:
    """Which row each bar and label sits on, read from the drawn figure."""

    def test_the_rows_carry_the_three_labels_top_to_bottom(self, toy) -> None:
        assert [bar.label for bar in toy.bars] == [
            "survivorship-free picks,\nwhat a trader got",
            "survivor-only picks,\nas the book prints them",
            "survivor-only picks,\nNEOF on one share basis",
        ]
        ax = toy.axes[0]
        ticks = sorted(
            zip(ax.get_yticks(), [t.get_text() for t in ax.get_yticklabels()], strict=True)
        )
        assert [label for _, label in reversed(ticks)] == [bar.label for bar in toy.bars]

    def test_each_bars_segments_share_the_row_its_label_names(self, toy) -> None:
        ax = toy.axes[0]
        rows = {
            label: y
            for y, label in zip(
                ax.get_yticks(), [t.get_text() for t in ax.get_yticklabels()], strict=True
            )
        }
        centre = {
            gid: [p.get_y() + p.get_height() / 2 for p in ax.patches if p.get_gid() == gid]
            for gid in ("loss", "others", "neof")
        }
        labels = [bar.label for bar in toy.bars]
        assert centre["loss"] == [pytest.approx(rows[labels[0]])]
        assert centre["others"] == pytest.approx([rows[labels[1]], rows[labels[2]]])
        assert centre["neof"] == pytest.approx([rows[labels[1]], rows[labels[2]]])

    def test_each_total_label_sits_at_its_own_bars_end(self, toy) -> None:
        ax = toy.axes[0]
        rows = sorted(ax.get_yticks(), reverse=True)
        totals = [t for t in ax.texts if t.get_text().endswith("%")]
        assert [t.xy for t in totals] == [
            pytest.approx((max(bar.total, 0.0), y)) for bar, y in zip(toy.bars, rows, strict=True)
        ]

    def test_the_other_nine_label_sits_in_the_middle_of_its_segment(self, toy) -> None:
        ax = toy.axes[0]
        rows = sorted(ax.get_yticks(), reverse=True)
        labels = [t for t in ax.texts if t.get_text() == "the other nine"]
        assert [t.xy for t in labels] == [
            pytest.approx((bar.others / 2, y))
            for bar, y in zip(toy.bars, rows, strict=True)
            if bar.neof
        ]

    def test_the_axis_holds_every_bar_and_reads_in_percent(self, toy) -> None:
        ax = toy.axes[0]
        low, high = ax.get_xlim()
        assert low < min(bar.total for bar in toy.bars)
        assert high > max(bar.total for bar in toy.bars)
        assert ax.xaxis.get_major_formatter().xmax == 1.0


class TestTheToyBars:
    """The two printed tables, and the second with NEOF on one share basis."""

    def test_the_bars_are_the_three_portfolios(self) -> None:
        bars = toy_bars()
        adjusted = one_share_basis(SURVIVOR_PICKS)
        assert [bar.total for bar in bars] == [
            equal_capital_return(UNBIASED_PICKS),
            equal_capital_return(SURVIVOR_PICKS),
            equal_capital_return(adjusted),
        ]
        assert [bar.neof for bar in bars] == [
            0.0,
            contributions(SURVIVOR_PICKS)["NEOF"],
            contributions(adjusted)["NEOF"],
        ]

    def test_the_other_nine_are_the_same_in_both_survivor_bars(self) -> None:
        """Only NEOF moves on one share basis, so the green segments match."""
        _, printed, adjusted = toy_bars()
        assert printed.others == pytest.approx(adjusted.others, abs=1e-12)

    def test_neofs_share_on_one_basis_is_21_89_points(self) -> None:
        assert toy_bars()[2].neof == pytest.approx(0.218857, abs=5e-7)

    def test_the_drawn_widths_are_the_bars(self, toy) -> None:
        patches = toy.axes[0].patches
        by_gid = {
            gid: [p for p in patches if p.get_gid() == gid] for gid in ("loss", "others", "neof")
        }
        _, printed, adjusted = toy.bars
        assert [p.get_width() for p in by_gid["loss"]] == [pytest.approx(toy.bars[0].total)]
        assert [p.get_width() for p in by_gid["others"]] == pytest.approx(
            [printed.others, adjusted.others]
        )
        assert [p.get_width() for p in by_gid["neof"]] == pytest.approx(
            [printed.neof, adjusted.neof]
        )
        assert [p.get_x() for p in by_gid["neof"]] == pytest.approx(
            [printed.others, adjusted.others]
        )

    def test_the_segments_wear_loss_gain_and_neofs_colour(self, toy) -> None:
        colours = {p.get_gid(): _rgb(p.get_facecolor()) for p in toy.axes[0].patches if p.get_gid()}
        assert colours == {"loss": _rgb(LOST), "others": _rgb(GOOD), "neof": _rgb(ACCENT)}

    def test_each_bar_is_labelled_with_its_own_numbers(self, toy) -> None:
        assert [text.get_text() for text in toy.axes[0].texts] == [
            "−41.72%",
            "the other nine",
            "NEOF 308.86 points",
            "+387.88%",
            "the other nine",
            "NEOF 21.89 points",
            "+100.91%",
        ]

    def test_the_title_and_note_state_the_tables_and_the_split(self, toy) -> None:
        assert toy._suptitle.get_text() == (
            "A database of survivors turns a 42% loss into a 388% gain, most of it from one row"
        )
        note = toy.texts[-1].get_text()
        assert "Example 3.3, revised edition" in note
        assert "1/2/2001 to 1/2/2002, from the book's two printed tables" in note
        assert "1-for-10 reverse split" in note
        assert "multiplies its start price by 10" in note


@pytest.mark.parametrize("name", ["costs", "toy"])
def test_no_label_is_parsed_as_math(request, name) -> None:
    """The labels carry percent signs, so math parsing stays off the way it
    does for the other figures."""
    figure = request.getfixturevalue(name)
    for text in [*figure.axes[0].texts, *figure.texts]:
        assert text.get_parse_math() is False


def test_drawing_writes_the_files_it_is_given(costs, cumulative_out, toy, toy_out) -> None:
    assert cumulative_out.is_file()
    assert toy_out.is_file()


def test_the_command_draws_the_toy_first_and_the_costs_from_one_read(monkeypatch, capsys) -> None:
    import chan.survivorship_and_costs_figures as figures

    result, drawn = object(), []
    monkeypatch.setattr(figures, "chan_window_result", lambda: result)
    monkeypatch.setattr(figures, "make_toy_figure", lambda **kw: drawn.append(("toy", kw)))
    monkeypatch.setattr(figures, "make_cumulative_figure", lambda **kw: drawn.append(("costs", kw)))
    figures.main()
    assert drawn == [("toy", {}), ("costs", {"result": result})]
    out = capsys.readouterr().out
    assert f"wrote {FIGURES_DIR / TOY_FIGURE}" in out
    assert f"wrote {FIGURES_DIR / CUMULATIVE_FIGURE}" in out


def test_a_missing_vintage_reaches_the_operator_as_a_line_after_the_toy(monkeypatch) -> None:
    """The toy's figure reads nothing, so it is drawn before the refusal."""
    import chan.survivorship_and_costs_figures as figures

    drawn = []

    def refuse(*_, **__):
        raise VintageUnavailable("SPX_20071123.mat cannot be read")

    monkeypatch.setattr(figures, "make_toy_figure", lambda **kw: drawn.append("toy"))
    monkeypatch.setattr(figures, "chan_window_result", refuse)
    with pytest.raises(SystemExit, match="SPX_20071123.mat cannot be read"):
        figures.main()
    assert drawn == ["toy"]


@pytest.mark.parametrize("name", [CUMULATIVE_FIGURE, TOY_FIGURE])
def test_the_committed_figure_exists(name) -> None:
    assert (FIGURES_DIR / name).is_file()
