"""The pins for the figure in the post on Example 7.2 rerun on EDGAR's calendar.

``tests/test_pead_rerun.py`` holds what the runs compute. This file holds that
the figure draws those numbers, so a generator that split A's stocks into the
wrong groups, drew a curve of equal return through the wrong run or pointed an
arrow the wrong way fails even when the arithmetic is right. Some numbers
repeat here on purpose, because a figure's labels are prose and the suite is
the authority for every number prose quotes. No test compares bytes, for the
reason ``tests/test_regime_figure.py`` gives.

The figure reads the vintages and the specification that
``tests/test_pead_rerun.py`` states in its module docstring, and only the
committed ones: Chan's ``inputdataohlcdaily_stocks_20120424/`` and
``earnannfile/``, and the ticker table and Item 2.02 index under
``research/filings/earnings/`` as written on 2026-10-10. The runs on the
owner archive's prices are left out of it on purpose, so every test here runs
in CI.

Exploratory, like everything Entry 46 computes. The split of A's return into
three groups and the day it marks were measured after the runs, and decide
nothing.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from matplotlib.dates import num2date

from chan import pead_rerun_figures as module
from chan.paths import FIGURES_DIR
from chan.pead import DENOMINATOR, TRADING_DAYS
from chan.pead_rerun import committed_runs, per_trade, read_committed
from chan.pead_rerun_figures import (
    ARROWS,
    CURVES,
    GROUPS,
    MARKED_DAY,
    POINTS,
    RERUN_FIGURE,
    contributions,
    equal_return,
    group_stocks,
    main,
    make_rerun_figure,
    signed,
)
from chan.regime_figure import ACCENT, INK, LOST
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable
from tests.test_pead_rerun import FIGURES, PER_TRADE
from tests.test_regime_figure import png_size

SPEC = (
    "chan.pead.pead on the flag file's 330 days, 90-day lookback, entry at 0.5 moving std, "
    "each day's return over 30; universes from research/filings/earnings/tickers.csv and "
    "calendars from its index.jsonl as written 2026-10-10; committed runs only"
)


@pytest.fixture(scope="module")
def sources():
    return read_committed()


@pytest.fixture(scope="module")
def runs(sources):
    return committed_runs(sources)


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("pead_rerun_figure") / RERUN_FIGURE


@pytest.fixture(scope="module")
def figure(out, sources):
    return make_rerun_figure(out=out, sources=sources)


@pytest.fixture(scope="module")
def axes(figure):
    contribution, per_trade_ax = figure.axes
    return {"contribution": contribution, "per_trade": per_trade_ax}


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _line(axes, gid: str):
    return _by_gid(axes["contribution"].lines)[gid]


class TestTheFigure:
    def test_there_are_two_panels(self, figure) -> None:
        assert len(figure.axes) == 2

    def test_the_title_carries_the_exploratory_label(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Exploratory: post-earnings drift on EDGAR's calendar, the runs on committed files"
        )

    def test_the_note_names_each_vintage_and_the_runs_left_out(self, figure) -> None:
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Algorithmic Trading, Example 7.2, 2011-01-03 to 2012-04-24, on "
            "inputDataOHLCDaily_stocks_20120424.mat and earnannFile.mat,\nand Item 2.02 8-Ks as "
            "research/filings/earnings/ recorded them from EDGAR on 2026-10-10. No cost is "
            "charged.\nC, D, E1 and E5 read the owner's archive of Alpha Vantage prices, so no "
            "reader can rerun them, and they are left out."
        ]

    def test_no_label_is_parsed_as_math(self, figure) -> None:
        for text in [*figure.axes[0].texts, *figure.axes[1].texts, *figure.texts]:
            assert text.get_parse_math() is False


class TestWhereTheUniverseEffectComesFrom:
    """Run A's return over the 330 days, split among U, CAL without a series, and the rest."""

    def test_the_groups_hold_441_47_and_9_stocks(self, sources) -> None:
        groups = group_stocks(sources)
        assert [len(groups[g]) for g in GROUPS] == [441, 47, 9]
        assert groups["U"] == sources.universe("U")
        assert sorted(groups["no checked CIK"]) == [
            "AKS", "CPWR", "CVC", "DD", "LUK", "MWW", "NYX", "TLAB", "WFR",
        ]  # fmt: skip

    def test_it_draws_the_three_lines_in_order(self, axes) -> None:
        drawn = [line.get_gid() for line in axes["contribution"].lines if line.get_gid() in GROUPS]
        assert drawn == list(GROUPS)

    def test_each_line_spans_the_330_days(self, axes, runs) -> None:
        for group in GROUPS:
            assert pd.DatetimeIndex(_line(axes, group).get_xdata()).equals(runs["A"].days)

    def test_each_line_ends_where_the_post_says(self, axes) -> None:
        ends = [round(float(_line(axes, g).get_ydata()[-1]), 6) for g in GROUPS]
        assert ends == [0.043678, 0.010803, 0.012261], SPEC

    def test_the_three_ends_sum_to_a(self, axes, runs) -> None:
        total = sum(float(_line(axes, g).get_ydata()[-1]) for g in GROUPS)
        assert total == pytest.approx(runs["A"].arithmetic_annual, rel=1e-12)

    def test_the_u_line_is_run_a_u(self, axes, runs) -> None:
        """Each stock trades on its own gap and deviation, so dropping the rest changes nothing."""
        a_u = runs["A_U"]
        # A run's daily return is already its summed trades over 30.
        scale = TRADING_DAYS / len(a_u.days)
        np.testing.assert_allclose(
            _line(axes, "U").get_ydata(), np.cumsum(a_u.daily) * scale, rtol=1e-12, atol=1e-15
        )

    def test_the_other_two_end_on_the_universe_effect(self, axes, runs) -> None:
        outside = sum(float(_line(axes, g).get_ydata()[-1]) for g in GROUPS[1:])
        effect = runs["A"].arithmetic_annual - runs["A_U"].arithmetic_annual
        assert outside == pytest.approx(effect, rel=1e-12)
        assert round(outside, 6) == 0.023065, SPEC

    def test_the_marked_day_is_where_the_stocks_outside_u_add_most(self, axes) -> None:
        outside = sum(
            pd.Series(_line(axes, g).get_ydata(), index=_line(axes, g).get_xdata())
            for g in GROUPS[1:]
        )
        steps = outside.diff()
        assert steps.idxmax() == MARKED_DAY == pd.Timestamp("2011-08-04")
        assert round(float(steps.max()), 6) == 0.010702, SPEC

    def test_the_marked_day_is_drawn_and_labelled(self, axes) -> None:
        line = _line(axes, "marked-day")
        assert [pd.Timestamp(x) for x in line.get_xdata()] == [MARKED_DAY, MARKED_DAY]
        label = _by_gid(axes["contribution"].texts)["marked-day-label"]
        assert label.get_text() == "2011-08-04: the stocks outside U\nadd 0.010702 on one day"
        assert label.get_color() == LOST

    def test_the_legend_names_each_group_its_size_and_its_end(self, axes) -> None:
        labels = [t.get_text() for t in axes["contribution"].get_legend().get_texts()]
        assert labels == [
            "the 441 stocks of U, with a checked CIK and a checked series, ending at 0.043678",
            "the 47 with a checked CIK and no checked series, ending at 0.010803",
            "the 9 with no checked CIK, ending at 0.012261",
        ]

    def test_the_colours(self, axes) -> None:
        colours = [_line(axes, g).get_color() for g in GROUPS]
        assert colours == [INK, ACCENT, LOST]

    def test_the_heading(self, axes) -> None:
        assert axes["contribution"].get_title(loc="left") == (
            "Run A's arithmetic annual return, 0.066743, built up over its 330 days from three "
            "groups of its 497 stocks.\nThe 56 stocks outside U add 0.023065, and the U line is "
            "run A_U exactly."
        )

    def test_the_x_axis_is_dates(self, axes, runs) -> None:
        start, end = axes["contribution"].get_xlim()
        assert num2date(start).date() == runs["A"].days[0].date()
        assert num2date(end).date() == runs["A"].days[-1].date()


class TestTradesTimesTheirMean:
    """Each committed run's trades against its mean return per trade."""

    def test_it_draws_the_six_committed_runs(self) -> None:
        assert POINTS == ("A", "A_CAL", "A_PX", "A_U", "B1", "B5")

    @pytest.mark.parametrize("name", ("A", "A_CAL", "A_PX", "A_U", "B1", "B5"))
    def test_each_point_sits_on_the_runs_pins(self, axes, name) -> None:
        point = _by_gid(axes["per_trade"].lines)[f"point-{name}"]
        assert int(point.get_xdata()[0]) == FIGURES[name][5], SPEC
        assert round(float(point.get_ydata()[0]), 6) == PER_TRADE[name], SPEC
        label = _by_gid(axes["per_trade"].texts)[f"point-{name}-label"]
        assert label.get_text() == f"{name}, {FIGURES[name][0]:.6f}"

    @pytest.mark.parametrize("name", CURVES)
    def test_each_curve_holds_its_runs_return(self, axes, runs, name) -> None:
        """The return is the trades times their mean times 252, over 30 and over the days."""
        curve = _by_gid(axes["per_trade"].lines)[f"equal-{name}"]
        trades, mean = np.asarray(curve.get_xdata()), np.asarray(curve.get_ydata())
        annual = trades * mean * TRADING_DAYS / (DENOMINATOR * len(runs[name].days))
        np.testing.assert_allclose(annual, runs[name].arithmetic_annual, rtol=1e-12)
        assert curve.get_linestyle() == "--"

    @pytest.mark.parametrize("name", CURVES)
    def test_each_curve_passes_through_its_run(self, runs, name) -> None:
        drift = runs[name]
        through = equal_return(drift.arithmetic_annual, [drift.trades], len(drift.days))
        assert through[0] == pytest.approx(per_trade(drift), rel=1e-12)

    def test_the_curves_are_labelled_with_their_runs(self, axes) -> None:
        texts = _by_gid(axes["per_trade"].texts)
        assert texts["equal-A-label"].get_text() == "A's return, held fixed"
        assert texts["equal-A_CAL-label"].get_text() == "A_CAL's return, held fixed"

    def test_the_arrows_run_from_each_reference_to_its_run(self, axes, runs) -> None:
        assert ARROWS == (
            ("A", "A_U", "the universe"),
            ("A_CAL", "B1", "R1"),
            ("A_CAL", "B5", "R5"),
        )
        texts = _by_gid(axes["per_trade"].texts)
        for start, end, label in ARROWS:
            arrow = texts[f"arrow-{start}-{end}"]
            a, b = runs[start], runs[end]
            assert arrow.xyann == (a.trades, per_trade(a))
            assert arrow.xy == (b.trades, per_trade(b))
            assert texts[f"arrow-{start}-{end}-label"].get_text() == label

    def test_the_heading(self, axes) -> None:
        assert axes["per_trade"].get_title(loc="left") == (
            "Each committed run's trades against its mean return per trade, labelled with its "
            "arithmetic annual return.\nEach day is divided by a fixed 30, so along a dashed "
            "curve more trades at a lower mean earn the same."
        )

    def test_every_point_and_arrow_end_is_inside_the_axes(self, axes, runs) -> None:
        left, right = axes["per_trade"].get_xlim()
        bottom, top = axes["per_trade"].get_ylim()
        for name in POINTS:
            assert left < runs[name].trades < right
            assert bottom < per_trade(runs[name]) < top


class TestTheHelpers:
    def test_equal_return_solves_the_identity_for_the_mean(self) -> None:
        """At 252 days of one trade each a day, a mean of 30 percent earns 0.3 × 252 / 30 a year."""
        assert equal_return(2.52, [252.0], 252)[0] == pytest.approx(0.3)
        assert equal_return(2.52, [504.0], 252)[0] == pytest.approx(0.15)

    def test_the_contributions_add_up_to_a_s_running_return(self, sources, runs) -> None:
        lines = contributions(sources, runs["A"])
        assert list(lines) == list(GROUPS)
        total = sum(lines[g] for g in GROUPS)
        scale = TRADING_DAYS / len(runs["A"].days)
        np.testing.assert_allclose(total, np.cumsum(runs["A"].daily) * scale, atol=1e-15)

    def test_signed_prints_a_true_minus_sign(self) -> None:
        assert signed(-0.023065) == "−0.023065"
        assert signed(0.0107021) == "0.010702"


class TestTheFile:
    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.exists() and out.stat().st_size > 0

    def test_the_committed_figure_exists(self) -> None:
        assert (FIGURES_DIR / RERUN_FIGURE).is_file()

    def test_a_fresh_draw_has_the_committed_image_dimensions(self, figure, out) -> None:
        assert png_size(out) == png_size(FIGURES_DIR / RERUN_FIGURE)

    def test_drawing_to_out_leaves_the_committed_figure_alone(self, tmp_path, sources) -> None:
        committed = FIGURES_DIR / RERUN_FIGURE
        before = committed.read_bytes()
        touched = committed.stat().st_mtime_ns
        make_rerun_figure(out=tmp_path / RERUN_FIGURE, sources=sources)
        assert committed.read_bytes() == before
        # A redraw is deterministic, so a stray write would leave the bytes
        # the same. Only the modification time shows it.
        assert committed.stat().st_mtime_ns == touched

    def test_with_no_sources_it_reads_the_committed_files(self, monkeypatch, tmp_path, sources):
        """``main`` and the committed PNG take this path, so it is drawn here too."""
        read = []
        monkeypatch.setattr(module, "read_committed", lambda: read.append(1) or sources)
        make_rerun_figure(out=tmp_path / RERUN_FIGURE)
        assert read == [1]

    def test_the_committed_runs_call_the_scale_break_guard(self, monkeypatch, tmp_path, sources):
        from chan import pead_rerun

        def refuse(*args, **kwargs):
            raise WindowCrossesScaleBreak("a stock changes scale inside the window")

        monkeypatch.setattr(pead_rerun, "refuse_scale_breaks", refuse)
        with pytest.raises(WindowCrossesScaleBreak, match="changes scale"):
            make_rerun_figure(out=tmp_path / RERUN_FIGURE, sources=sources)

    def test_the_command_writes_the_committed_path(self, monkeypatch, capsys) -> None:
        drawn = []
        monkeypatch.setattr(module, "make_rerun_figure", lambda **kw: drawn.append(kw))
        main()
        assert drawn == [{}]
        assert capsys.readouterr().out == f"wrote {FIGURES_DIR / RERUN_FIGURE}\n"

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage is lifted from earnannFile.mat"),
            WindowCrossesScaleBreak("a stock changes scale inside the window"),
        ],
    )
    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(module, "make_rerun_figure", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)

    def test_main_lets_any_other_error_through_as_itself(self, monkeypatch) -> None:
        def fail(*_a, **_k):
            raise ValueError("a bug, not a refusal")

        monkeypatch.setattr(module, "make_rerun_figure", fail)
        with pytest.raises(ValueError, match="a bug, not a refusal"):
            main()
