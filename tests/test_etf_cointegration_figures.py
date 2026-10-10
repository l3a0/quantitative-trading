"""The pins for the figure in the post on EWA, EWC and IGE, Examples 2.6 to 2.8.

``tests/test_etf_cointegration.py`` holds what the run computes. This file
holds that the figure draws those numbers, so a generator that plotted the
wrong series, dropped the hedge ratio, swapped the trace and eigen bars or
marked the wrong day fails even when the arithmetic is right. Some numbers
repeat here on purpose, because a figure's labels are prose and the suite is
the authority for every number prose quotes. No test compares bytes, for the
reason ``tests/test_regime_figure.py`` gives.

The figure reads the vintage and the specification
``tests/test_etf_cointegration.py`` names as its ``SPEC``, which every failure
message here carries too.

One thing is pinned here and nowhere else: that the residual's mean, which
the panel draws, equals the intercept of the regression the hedge ratio comes
from, 6.4113. ``blog/johansen-etf-lessons.md`` draws it and
``blog/kalman-hedge-lessons.md`` quotes it, so a change to it moves both posts.
That the deepest drawdown's trough sits inside the longest spell below the
high is held here and in ``tests/test_etf_cointegration.py``.
``calculateMaxDD`` returns the two separately, so it is a fact about this run
rather than about the helper.

Exploratory, like everything Examples 2.6 to 2.8 compute here.
"""

from __future__ import annotations

import numpy as np
import pytest
from ithildincore.timeseries import ols
from matplotlib.colors import same_color, to_rgb
from matplotlib.dates import DateFormatter, YearLocator, date2num

from chan import etf_cointegration as experiment
from chan import etf_cointegration_figures as figures
from chan import paths
from chan.etf_cointegration import etf_cointegration, read_sources
from chan.etf_cointegration_figures import (
    COINTEGRATION_FIGURE,
    STATISTICS,
    cumulative_return,
    main,
    make_cointegration_figure,
    residual,
)
from chan.johansen import Johansen
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable
from tests.test_etf_cointegration import SPEC

#: The triplet's statistics as ``tests/test_etf_cointegration.py`` rows 7 and 8 pin them.
TRACE = [34.428620, 17.531719, 4.471021]
EIGEN = [16.896901, 13.060698, 4.471021]

#: The dash each critical value is drawn in, as the post's alt text reads them: dotted at
#: 90 percent, solid at 95 and dashed at 99. Written out rather than read from the
#: module's ``LEVELS``, so a swap there fails here instead of moving both sides at once.
DASHES = {90: ":", 95: "-", 99: "--"}


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def result(sources):
    return etf_cointegration(sources[1])


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("etf_cointegration_figure") / COINTEGRATION_FIGURE


@pytest.fixture(scope="module")
def figure(out, sources):
    return make_cointegration_figure(out=out, sources=sources)


@pytest.fixture(scope="module")
def axes(figure):
    closes, spread, statistics, returns = figure.axes
    return {"closes": closes, "residual": spread, "statistics": statistics, "returns": returns}


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _title(ax) -> str:
    return ax.get_title(loc="left")


def _legend(ax) -> list[str]:
    return [t.get_text() for t in ax.get_legend().get_texts()]


def _handles(ax) -> dict:
    """Each legend entry's handle, by the text beside it."""
    legend = ax.get_legend()
    return dict(zip(_legend(ax), legend.legend_handles, strict=True))


class TestThePanels:
    def test_there_are_four_in_the_order_the_post_reads_them(self, figure, axes) -> None:
        assert len(figure.axes) == 4
        assert (
            _title(axes["closes"]) == "Figure 2.4: the closes of EWA and EWC over the whole file."
        )
        assert _title(axes["residual"]).startswith("Figure 2.6: the residual EWC − 0.9624·EWA")
        assert _title(axes["statistics"]).startswith("The Johansen test on EWC, EWA and IGE")
        assert _title(axes["returns"]).startswith("Figure 2.7: the first eigenvector")

    def test_the_three_date_panels_share_the_files_days(self, axes, result) -> None:
        days = result.days
        dated = [axes[name] for name in ("closes", "residual", "returns")]
        assert {ax.get_xlim() for ax in dated} == {(date2num(days[0]), date2num(days[-1]))}, SPEC
        assert len(days) == 1500, SPEC
        assert axes["closes"].get_shared_x_axes().joined(axes["closes"], axes["returns"])
        assert not axes["closes"].get_shared_x_axes().joined(axes["closes"], axes["statistics"])

    def test_the_date_ticks_read_as_years(self, axes) -> None:
        for name in ("closes", "residual", "returns"):
            axis = axes[name].xaxis
            assert isinstance(axis.get_major_locator(), YearLocator), name
            assert isinstance(axis.get_major_formatter(), DateFormatter), name
            assert axis.get_major_formatter().fmt == "%Y", name

    def test_the_title_carries_the_exploratory_label(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Exploratory: Examples 2.6 to 2.8 redrawn on Chan's own EWA, EWC and IGE closes"
        )

    def test_the_note_names_the_file_the_window_and_the_look_ahead(self, figure) -> None:
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Examples 2.6 to 2.8 of Algorithmic Trading, 2006-04-26 to 2012-04-09, 1,500 "
            "trading days, as cointegrationTests.m runs them.\nPrices from inputData_ETF.mat, "
            "saved 2012-04-10. The eigenvector is fitted on the days the strategy trades, so "
            "every figure is in-sample."
        ], SPEC

    def test_no_label_is_parsed_as_math(self, figure) -> None:
        for ax in figure.axes:
            for text in [*ax.texts, ax.title, ax._left_title]:
                assert text.get_parse_math() is False
        for text in figure.texts:
            assert text.get_parse_math() is False


class TestTheCloses:
    """Figure 2.4, the two ETFs' closes."""

    def test_each_line_is_its_etfs_close_over_every_day(self, axes, sources) -> None:
        closes = sources[1]
        lines = _by_gid(axes["closes"].lines)
        assert set(lines) == {"EWA", "EWC"}
        for symbol in ("EWA", "EWC"):
            assert list(lines[symbol].get_xdata()) == list(closes.index), SPEC
            np.testing.assert_array_equal(lines[symbol].get_ydata(), closes[symbol].to_numpy())

    def test_the_legend_names_both(self, axes) -> None:
        assert _legend(axes["closes"]) == ["EWA", "EWC"]

    def test_each_close_wears_its_own_colour_and_its_legend_entry_matches(self, axes) -> None:
        """Colour is the only thing telling the two lines apart, and the legend its only key."""
        ax = axes["closes"]
        lines, handles = _by_gid(ax.lines), _handles(ax)
        for symbol, colour in (("EWA", ACCENT), ("EWC", INK)):
            assert same_color(lines[symbol].get_color(), colour), symbol
            assert same_color(handles[symbol].get_color(), lines[symbol].get_color()), symbol
        assert not same_color(lines["EWA"].get_color(), lines["EWC"].get_color())

    def test_the_axis_reads_in_dollars(self, axes) -> None:
        assert axes["closes"].get_ylabel() == "adjusted close, dollars"


class TestTheResidual:
    """Figure 2.6, ``y - hedgeRatio*x`` with the intercept left in."""

    def test_the_line_is_ewc_less_the_hedge_ratio_times_ewa(self, axes, sources, result) -> None:
        closes = sources[1]
        line = _by_gid(axes["residual"].lines)["residual"]
        assert result.hedge_ratio == pytest.approx(0.9624293987, abs=1e-10), SPEC
        expected = closes["EWC"].to_numpy() - 0.9624293987 * closes["EWA"].to_numpy()
        assert list(line.get_xdata()) == list(closes.index), SPEC
        np.testing.assert_allclose(line.get_ydata(), expected, rtol=0, atol=1e-8)
        np.testing.assert_array_equal(line.get_ydata(), residual(closes, result))

    def test_the_dashed_line_is_its_mean_and_the_regressions_intercept(
        self, axes, sources, result
    ) -> None:
        """Least squares with an intercept leaves the residual's mean equal to it."""
        closes = sources[1]
        x, y = closes["EWA"].to_numpy(dtype=float), closes["EWC"].to_numpy(dtype=float)
        intercept = ols(y, np.column_stack([x, np.ones(len(x))])).beta[1]
        mean = _by_gid(axes["residual"].lines)["mean"]
        assert intercept == pytest.approx(6.41133139, abs=1e-8), SPEC
        assert list(mean.get_ydata()) == pytest.approx([intercept] * 2, abs=1e-9), SPEC
        assert mean.get_linestyle() == "--"

    def test_the_legend_and_heading_name_both_lines(self, axes) -> None:
        assert _legend(axes["residual"]) == [
            "the residual",
            "its mean, 6.41, which is the regression's intercept",
        ], SPEC
        assert _title(axes["residual"]) == (
            "Figure 2.6: the residual EWC − 0.9624·EWA, the hedge ratio from EWC on EWA with "
            "an intercept.\nIts CADF statistic is −3.6435, past the 95 percent bar of −3.359."
        ), SPEC

    def test_each_legend_entry_wears_its_lines_colour_and_dash(self, axes) -> None:
        """The residual alone is plain ink, so only the key's match to its lines is pinned."""
        ax = axes["residual"]
        lines = _by_gid(ax.lines)
        handles = list(_handles(ax).values())
        for handle, gid in zip(handles, ("residual", "mean"), strict=True):
            assert same_color(handle.get_color(), lines[gid].get_color()), gid
            assert handle.get_linestyle() == lines[gid].get_linestyle(), gid

    def test_the_legend_sits_above_the_residuals_highest_point(self, axes, sources, result):
        values = residual(sources[1], result)
        span = values.max() - values.min()
        assert axes["residual"].get_ylim() == pytest.approx(
            (values.min() - 0.08 * span, values.max() + 0.32 * span), abs=1e-12
        )

    def test_the_axis_reads_in_dollars(self, axes) -> None:
        assert axes["residual"].get_ylabel() == "dollars"


class TestTheStatistics:
    """The triplet's trace and eigen statistics, each crossed by its three critical values."""

    def _bars(self, ax) -> dict:
        return _by_gid(ax.patches)

    def test_each_bar_is_its_statistic(self, axes, result) -> None:
        bars = self._bars(axes["statistics"])
        assert [name for name, *_ in STATISTICS] == ["trace", "eigen"]
        for name, pinned in (("trace", TRACE), ("eigen", EIGEN)):
            heights = [bars[f"{name}-{i}"].get_height() for i in range(3)]
            np.testing.assert_allclose(heights, pinned, rtol=0, atol=1e-6, err_msg=SPEC)
            assert heights == list(getattr(result.triplet, name))

    def test_each_bar_sits_in_its_nulls_group(self, axes) -> None:
        """Trace on the left of each null, eigen on the right, one group per null."""
        bars = self._bars(axes["statistics"])
        for i in range(3):
            trace, eigen = (bars[f"{name}-{i}"] for name in ("trace", "eigen"))
            centres = [bar.get_x() + bar.get_width() / 2 for bar in (trace, eigen)]
            assert sum(centres) / 2 == pytest.approx(i)
            assert trace.get_x() < eigen.get_x()

    def test_each_tick_sits_under_the_bar_its_label_names(self, axes) -> None:
        """The labels alone would pass with the trace label printed under the eigen bar."""
        ax = axes["statistics"]
        bars = self._bars(ax)
        named = [bars[f"{name}-{i}"] for i in range(3) for name in ("trace", "eigen")]
        labels = [t.get_text() for t in ax.get_xticklabels()]
        assert [label.split("\n")[0] for label in labels] == ["trace", "eigen"] * 3
        assert list(ax.get_xticks()) == pytest.approx(
            [bar.get_x() + bar.get_width() / 2 for bar in named]
        )
        assert [label.split("\n")[1] for label in labels] == [
            f"{bar.get_height():.3f}" for bar in named
        ]

    def test_every_bar_and_mark_lies_inside_the_axis(self, axes) -> None:
        """A narrower axis would clip the first or the last null's group."""
        ax = axes["statistics"]
        low, high = ax.get_xlim()
        bars = list(self._bars(ax).values())
        assert len(bars) == 6
        for bar in bars:
            assert low < bar.get_x() and bar.get_x() + bar.get_width() < high, bar.get_gid()
        for mark in ax.lines:
            left, right = mark.get_xdata()
            assert low < left and right < high, mark.get_gid()

    def test_the_two_statistics_are_filled_apart(self, axes) -> None:
        """One fill for both would leave the legend unable to tell them apart."""
        bars = self._bars(axes["statistics"])
        fills = {}
        for name, _, _ in STATISTICS:
            colours = {tuple(bars[f"{name}-{i}"].get_facecolor()) for i in range(3)}
            assert len(colours) == 1, name
            fills[name] = colours.pop()
        assert fills["trace"] != fills["eigen"]
        patches = axes["statistics"].get_legend().get_patches()
        assert [tuple(p.get_facecolor()) for p in patches] == [fills["trace"], fills["eigen"]]

    def test_the_trace_bars_are_accent_and_the_eigen_bars_good(self, axes) -> None:
        """A swap of the two fills in ``STATISTICS`` moves the legend with the bars, so
        only a pin on the constants notices it."""
        ax = axes["statistics"]
        bars, handles = self._bars(ax), _handles(ax)
        for name, colour in (("trace", ACCENT), ("eigen", GOOD)):
            for i in range(3):
                assert same_color(to_rgb(bars[f"{name}-{i}"].get_facecolor()), colour), name
            handle = handles[f"{name} statistic"]
            assert same_color(handle.get_facecolor(), bars[f"{name}-0"].get_facecolor()), name
        assert not same_color(bars["trace-0"].get_facecolor(), bars["eigen-0"].get_facecolor())

    def test_each_bar_is_crossed_by_its_own_critical_values(self, axes, result) -> None:
        lines = _by_gid(axes["statistics"].lines)
        bars = self._bars(axes["statistics"])
        for name, _, _ in STATISTICS:
            critical = getattr(result.triplet, f"{name}_critical")
            for i in range(3):
                bar = bars[f"{name}-{i}"]
                for column, (level, dash) in enumerate(DASHES.items()):
                    mark = lines[f"{name}-{i}-{level}"]
                    assert list(mark.get_ydata()) == [critical[i, column]] * 2
                    assert mark.get_linestyle() == dash
                    left, right = mark.get_xdata()
                    assert left < bar.get_x() and right > bar.get_x() + bar.get_width()

    def test_the_trace_bars_clear_95_and_the_first_eigen_bar_misses_90(self, axes) -> None:
        """What the panel exists to show, read from what it draws."""
        bars = self._bars(axes["statistics"])
        lines = _by_gid(axes["statistics"].lines)
        for i in range(3):
            assert bars[f"trace-{i}"].get_height() > lines[f"trace-{i}-95"].get_ydata()[0]
        assert bars["eigen-0"].get_height() < lines["eigen-0-90"].get_ydata()[0]
        assert lines["eigen-0-90"].get_ydata()[0] == pytest.approx(18.8928, abs=1e-4), SPEC
        assert lines["trace-0-95"].get_ydata()[0] == pytest.approx(29.7961, abs=1e-4), SPEC

    def test_the_tick_labels_print_each_statistic(self, axes) -> None:
        labels = [t.get_text() for t in axes["statistics"].get_xticklabels()]
        assert labels == [
            "trace\n34.429",
            "eigen\n16.897",
            "trace\n17.532",
            "eigen\n13.061",
            "trace\n4.471",
            "eigen\n4.471",
        ], SPEC
        nulls = _by_gid(axes["statistics"].texts)
        assert [nulls[f"null-{i}"].get_text() for i in range(3)] == [
            "null r ≤ 0",
            "null r ≤ 1",
            "null r ≤ 2",
        ]

    def test_the_note_points_at_the_first_eigen_bar(self, axes) -> None:
        note = _by_gid(axes["statistics"].texts)["eigen-short-label"]
        bar = self._bars(axes["statistics"])["eigen-0"]
        assert note.get_text() == "16.897, short of 18.893,\nits 90 percent bar", SPEC
        assert note.xy == pytest.approx((bar.get_x() + bar.get_width() / 2, bar.get_height()))

    def test_the_heading_counts_each_tests_relations(self, axes) -> None:
        assert _title(axes["statistics"]) == (
            "The Johansen test on EWC, EWA and IGE: each statistic beside its 90, 95 and 99 "
            "percent critical values.\nThe trace test finds 3 relations at 95 percent. "
            "The eigen test finds 0, even at 90."
        ), SPEC

    def test_the_heading_counts_at_the_levels_it_names(self, monkeypatch, tmp_path, sources):
        """On this file the counts read the same at 90 and 95, so the levels asked are pinned.

        The stand-in answers each question with its level, so a count asked at the
        wrong level prints a number the heading's own words contradict.
        """
        asked = []

        def relations(self, statistic: str, level: int) -> int:
            asked.append((statistic, level))
            return level

        monkeypatch.setattr(Johansen, "relations", relations)
        drawn = make_cointegration_figure(out=tmp_path / COINTEGRATION_FIGURE, sources=sources)
        assert asked == [("trace", 95), ("eigen", 90)]
        assert _title(drawn.axes[2]).endswith(
            "The trace test finds 95 relations at 95 percent. The eigen test finds 90, even at 90."
        )

    def test_the_legend_names_both_statistics_and_every_level(self, axes) -> None:
        assert _legend(axes["statistics"]) == [
            "trace statistic",
            "eigen statistic",
            "90 percent critical value",
            "95 percent critical value",
            "99 percent critical value",
        ]

    def test_each_legend_line_is_dashed_as_its_level_is_drawn(self, axes) -> None:
        """The labels alone would pass with every legend line solid."""
        ax = axes["statistics"]
        drawn = _by_gid(ax.lines)
        legend = ax.get_legend().get_lines()
        assert len(legend) == len(DASHES)
        for line, (level, dash) in zip(legend, DASHES.items(), strict=True):
            assert line.get_linestyle() == dash, level
            assert line.get_linestyle() == drawn[f"trace-0-{level}"].get_linestyle(), level

    def test_the_axis_holds_the_tallest_mark(self, axes, result) -> None:
        low, high = axes["statistics"].get_ylim()
        assert low == 0
        assert high > result.triplet.trace_critical.max() > result.triplet.trace.max()
        assert axes["statistics"].get_ylabel() == "statistic"


class TestTheReturn:
    """Figure 2.7, the linear rule on the first eigenvector, compounded."""

    def test_the_line_is_the_compounded_cumulative_return(self, axes, result) -> None:
        line = _by_gid(axes["returns"].lines)["cumulative"]
        expected = np.cumprod(1 + result.strategy.daily) - 1
        assert list(line.get_xdata()) == list(result.days), SPEC
        assert line.get_ydata() == pytest.approx(expected, abs=1e-12), SPEC
        np.testing.assert_array_equal(cumulative_return(result), expected)

    def test_it_ends_where_the_apr_says(self, axes, result) -> None:
        """The APR carried back over 1,500 of 252 days ties the line to row 13's pin."""
        last = _by_gid(axes["returns"].lines)["cumulative"].get_ydata()[-1]
        assert result.strategy.apr == pytest.approx(0.1257386810, abs=1e-10), SPEC
        assert last == pytest.approx((1 + result.strategy.apr) ** (1500 / 252) - 1, abs=1e-12)
        assert last == pytest.approx(1.0238397644, abs=1e-10), SPEC

    def test_the_deepest_drawdown_is_marked_on_its_trough(self, axes, result) -> None:
        trough = _by_gid(axes["returns"].lines)["trough"]
        cumret = cumulative_return(result)
        assert axes["returns"].trough == 1084, SPEC
        assert str(result.days[1084].date()) == "2010-08-16", SPEC
        assert list(trough.get_xdata()) == [result.days[1084]]
        assert list(trough.get_ydata()) == [cumret[1084]]
        assert cumret[1084] == pytest.approx(0.7149719171, abs=1e-10), SPEC

    def test_the_trough_sits_inside_the_longest_spell(self, axes) -> None:
        spell = axes["returns"].spell
        assert spell.first <= axes["returns"].trough <= spell.last
        assert spell.trough == axes["returns"].trough
        assert spell.depth == pytest.approx(-0.10124855881644923, abs=1e-10), SPEC

    def test_the_shaded_spell_covers_its_598_rows(self, axes, result) -> None:
        band = _by_gid(axes["returns"].patches)["spell"]
        low, high = band.get_x(), band.get_x() + band.get_width()
        rows = [i for i, day in enumerate(date2num(result.days)) if low <= day <= high]
        assert rows == list(range(739, 1337)), SPEC
        assert len(rows) == 598 == axes["returns"].spell.rows

    def test_the_high_is_marked_the_day_before_the_spell(self, axes, result) -> None:
        high = _by_gid(axes["returns"].lines)["high"]
        assert list(high.get_xdata()) == [result.days[738]]
        assert str(result.days[738].date()) == "2009-04-01", SPEC
        assert axes["returns"].spell.high == 738

    def test_the_labels_name_the_spell_the_high_and_the_drawdown(self, axes) -> None:
        texts = {t.get_gid(): t.get_text() for t in axes["returns"].texts if t.get_gid()}
        assert texts["spell-label"] == "598 days below the high,\n2009-04-02 to 2011-08-15", SPEC
        assert texts["high-label"] == "high, 2009-04-01", SPEC
        assert texts["trough-label"] == "deepest drawdown −0.101249,\n2010-08-16", SPEC

    def test_the_spell_and_the_trough_wear_lost_and_the_high_the_lines_colour(self, axes) -> None:
        """Swapped, the red mark would sit on the high and say the drawdown is there."""
        ax = axes["returns"]
        lines, notes = _by_gid(ax.lines), _by_gid(ax.texts)
        assert same_color(to_rgb(_by_gid(ax.patches)["spell"].get_facecolor()), LOST)
        assert same_color(notes["spell-label"].get_color(), LOST)
        line = lines["cumulative"].get_color()
        for gid, colour in (("high", line), ("trough", LOST)):
            assert same_color(lines[gid].get_markerfacecolor(), colour), gid
            assert same_color(notes[f"{gid}-label"].get_color(), colour), gid
        assert not same_color(lines["high"].get_markerfacecolor(), LOST)

    def test_each_label_points_at_the_row_it_names(self, axes, result) -> None:
        """The text alone would pass with the arrow anchored at the wrong day."""
        notes = _by_gid(axes["returns"].texts)
        cumret = cumulative_return(result)
        for gid, row in (("high-label", 738), ("trough-label", 1084)):
            x, y = notes[gid].xy
            assert date2num(x) == date2num(result.days[row]), gid
            assert y == cumret[row], gid
        middle = result.days[(739 + 1336) // 2]
        assert date2num(notes["spell-label"].get_position()[0]) == date2num(middle)

    def test_the_heading_sets_both_figures_beside_the_books(self, axes) -> None:
        assert _title(axes["returns"]) == (
            "Figure 2.7: the first eigenvector traded by the linear rule, over a 23-day "
            "lookback.\nAPR 0.125739 and Sharpe ratio 1.3913, where the book prints 12.6 "
            "percent and 1.4. Unlevered and before costs."
        ), SPEC

    def test_the_axis_holds_every_point_and_reads_in_percent(self, axes, result) -> None:
        cumret = cumulative_return(result)
        low, high = axes["returns"].get_ylim()
        assert low < cumret.min() and high > cumret.max()
        assert axes["returns"].yaxis.get_major_formatter()(0.5) == "50%"
        assert axes["returns"].get_ylabel() == "cumulative return, compounded"

    def test_a_line_marks_zero(self, axes) -> None:
        zero = _by_gid(axes["returns"].lines)["zero"]
        assert list(zero.get_ydata()) == [0, 0]


class TestTheReadPath:
    def test_drawing_with_no_sources_reads_the_runs_path(self, monkeypatch, tmp_path, sources):
        asked = []

        def read():
            asked.append(True)
            return sources

        monkeypatch.setattr(figures, "read_sources", read)
        drawn = make_cointegration_figure(out=tmp_path / COINTEGRATION_FIGURE)
        assert asked == [True]
        assert _by_gid(drawn.axes[1].lines)["residual"].get_ydata()[0] == pytest.approx(
            residual(sources[1], etf_cointegration(sources[1]))[0]
        )

    def test_sources_handed_in_are_the_sources_drawn(self, tmp_path, sources) -> None:
        """EWA doubled, so a figure that ignored the argument and read the file would fail."""
        members, closes = sources
        doubled = closes.assign(EWA=closes["EWA"] * 2)
        drawn = make_cointegration_figure(
            out=tmp_path / COINTEGRATION_FIGURE, sources=(members, doubled)
        )
        line = _by_gid(drawn.axes[0].lines)["EWA"]
        np.testing.assert_array_equal(line.get_ydata(), doubled["EWA"].to_numpy())

    def test_the_guard_runs_on_the_default_path(self, monkeypatch, tmp_path) -> None:
        """The figure reads through ``read_sources``, so a flagged day stops it too."""

        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("inputdata_etf/ige.csv changes scale on 2009-01-02")

        monkeypatch.setattr(experiment, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(WindowCrossesScaleBreak, match="ige.csv changes scale"):
            make_cointegration_figure(out=tmp_path / COINTEGRATION_FIGURE)

    def test_a_missing_vintage_reaches_the_operator_as_one_line(
        self, monkeypatch, tmp_path
    ) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert "inputData_ETF.mat" in str(stopped.value)
        assert "\n" not in str(stopped.value)

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage is lifted from inputData_ETF.mat"),
            WindowCrossesScaleBreak("inputdata_etf/ewa.csv changes scale on 2008-01-02"),
        ],
    )
    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(figures, "make_cointegration_figure", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)

    def test_any_other_error_keeps_its_traceback(self, monkeypatch) -> None:
        def broken(*_a, **_k):
            raise KeyError("Close")

        monkeypatch.setattr(figures, "make_cointegration_figure", broken)
        with pytest.raises(KeyError, match="Close"):
            main()

    def test_the_command_writes_the_committed_path(self, monkeypatch, capsys) -> None:
        drawn = []
        monkeypatch.setattr(figures, "make_cointegration_figure", lambda **kw: drawn.append(kw))
        main()
        assert drawn == [{}]
        assert f"wrote {FIGURES_DIR / COINTEGRATION_FIGURE}" in capsys.readouterr().out

    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.is_file() and out.stat().st_size > 0


def test_the_committed_figure_exists() -> None:
    assert (FIGURES_DIR / COINTEGRATION_FIGURE).is_file()
