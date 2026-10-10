"""The pins for the figure in the post on SPY against its component stocks.

``tests/test_index_arbitrage.py`` holds what the run computes. This file holds
that the figure draws those numbers, so a generator that plotted the wrong
series, mislabelled a bar or moved the nominal line fails even when the
arithmetic is right. Some numbers repeat here on purpose, because a figure's
labels are prose and the suite is the authority for every number prose quotes.
No test compares bytes, for the reason ``tests/test_regime_figure.py`` gives.

The figure reads the vintage and the specification
``tests/test_index_arbitrage.py`` states in its module docstring: Chan's 2012
S&P 500 stock file and the ETF file's SPY on their 1,489 common days, and
``indexArb.m`` at blob ``dcb079a``. The random walks are the 2,000 seeded with
343 that the same file screens.

Exploratory and survivor-only, like everything Example 4.2 computes here.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from matplotlib.colors import to_rgba
from matplotlib.dates import date2num

from chan import index_arbitrage_figures
from chan.index_arbitrage import index_arbitrage, read_sources
from chan.index_arbitrage_figures import (
    FIGURE,
    WALK_SEED,
    WALKS,
    ScreenRates,
    main,
    make_index_arbitrage_figure,
    screen_rates,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable

FIRST_RETURN = pd.Timestamp("2008-01-09")


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def result(sources):
    return index_arbitrage(sources[2], sources[3])


@pytest.fixture(scope="module")
def rates(sources, result) -> ScreenRates:
    return screen_rates(sources[3], result)


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("index_arbitrage_figure") / FIGURE


@pytest.fixture(scope="module")
def figure(out, sources, rates):
    return make_index_arbitrage_figure(out=out, sources=sources, rates=rates)


@pytest.fixture(scope="module")
def axes(figure):
    curve, rate = figure.axes
    return {"curve": curve, "rate": rate}


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _title(ax) -> str:
    return ax.get_title(loc="left")


class TestTheCurve:
    def test_it_is_dated_over_the_1076_test_days(self, axes, result) -> None:
        line = _by_gid(axes["curve"].lines)["cumulative"]
        days = pd.DatetimeIndex(line.get_xdata())
        assert days.equals(result.test_days)
        assert len(days) == 1076
        assert (str(days[0].date()), str(days[-1].date())) == ("2008-01-02", "2012-04-09")
        assert axes["curve"].get_xlim() == (date2num(days[0]), date2num(days[-1]))

    def test_it_is_the_compounded_cumulative_return(self, axes, result) -> None:
        line = _by_gid(axes["curve"].lines)["cumulative"]
        np.testing.assert_array_equal(line.get_ydata(), np.cumprod(1 + result.daily) - 1)

    def test_it_sits_at_zero_until_the_first_return(self, axes, result) -> None:
        line = _by_gid(axes["curve"].lines)["cumulative"]
        y = np.asarray(line.get_ydata())
        before = result.test_days < FIRST_RETURN
        assert before.sum() == 5
        assert (y[before] == 0).all()
        assert y[~before][0] != 0

    def test_it_ends_at_the_apr_compounded_over_1076_days(self, axes, result) -> None:
        y = _by_gid(axes["curve"].lines)["cumulative"].get_ydata()
        assert y[-1] == pytest.approx(0.2064215407, abs=1e-10)
        assert y[-1] == pytest.approx((1 + result.apr) ** (1076 / 252) - 1, abs=1e-12)

    def test_the_zero_line_and_the_curves_colour(self, axes) -> None:
        lines = _by_gid(axes["curve"].lines)
        assert list(lines["zero"].get_ydata()) == [0, 0]
        assert lines["cumulative"].get_color() == GOOD

    def test_the_heading_sets_the_figures_beside_the_books(self, axes) -> None:
        assert _title(axes["curve"]) == (
            "Figure 4.3 against the date: the compounded cumulative return over the 1,076 "
            "test days.\nAPR 0.044930 and Sharpe ratio 1.319397, which the book prints as "
            "4.5 percent and 1.3.\nZero until the first return on 2008-01-09, and 0.206422 on "
            "the last day, unlevered and before costs."
        )


class TestTheScreenPanel:
    def test_the_rates_are_the_runs_screen_and_the_pinned_walks(self, rates) -> None:
        """The walks are the ones ``tests/test_index_arbitrage.py`` pins at 561."""
        assert (WALKS, WALK_SEED) == (2000, 343)
        assert rates == ScreenRates(
            stocks_tested=480, stocks_passed=98, walks_tested=2000, walks_passed=561
        )

    def test_each_bar_is_its_share_passed(self, axes) -> None:
        stocks, walks = axes["rate"].patches
        assert (stocks.get_width(), walks.get_width()) == (98 / 480, 561 / 2000)
        assert stocks.get_y() > walks.get_y()

    def test_the_stocks_pass_at_20_4_percent_and_the_walks_at_28_1(self, axes) -> None:
        texts = [t.get_text() for t in axes["rate"].texts]
        assert "20.4%" in texts and "28.1%" in texts
        assert 98 / 480 == pytest.approx(0.204167, abs=1e-6)
        assert 561 / 2000 == 0.2805

    def test_each_bar_is_labelled_with_its_count(self, axes) -> None:
        labels = [t.get_text() for t in axes["rate"].texts if t.get_gid() == "label"]
        assert labels == [
            "98 of 480 stocks in Chan's file",
            "561 of 2,000 random walks unrelated to SPY",
        ]

    def test_the_two_bars_have_their_own_colours(self, axes) -> None:
        stocks, walks = axes["rate"].patches
        assert stocks.get_facecolor() != walks.get_facecolor()
        assert (stocks.get_facecolor(), walks.get_facecolor()) == (to_rgba(GOOD), to_rgba(ACCENT))

    def test_the_nominal_line_is_dashed_at_10_percent(self, axes) -> None:
        nominal = _by_gid(axes["rate"].lines)["nominal"]
        assert list(nominal.get_xdata()) == [pytest.approx(0.10)] * 2
        assert nominal.get_linestyle() == "--"
        texts = [t.get_text() for t in axes["rate"].texts]
        assert "nominal 10 percent at the 90 percent bar" in texts

    def test_the_heading_says_what_the_bars_mean(self, axes) -> None:
        assert _title(axes["rate"]) == (
            "The screen tests each series against SPY's 2007 closes at the trace test's "
            "90 percent\nbar. Random walks with no drift, which are not stocks, pass more often "
            "than the stocks\ndo, so the count of stocks passing is no evidence that any of them "
            "cointegrates with SPY."
        )


class TestTheFigure:
    def test_there_are_two_panels(self, figure) -> None:
        assert len(figure.axes) == 2

    def test_the_title_carries_both_labels_and_the_note_names_both_files(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Exploratory and survivor-only: SPY against the stocks that pass Chan's screen"
        )
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Algorithmic Trading, Example 4.2, location 2035. Stocks from "
            "inputDataOHLCDaily_stocks_20120424.mat, saved 2012-04-25,\nand SPY from "
            "inputData_ETF.mat, saved 2012-04-10. The stocks and the weights are fitted on "
            "2007 and traded from 2008,\nbut the lookback of 5 was chosen with hindsight, and "
            "every stock in the file survived to 2012."
        ]

    def test_drawing_with_no_sources_reads_the_committed_files(self, tmp_path, rates, result):
        """``main`` and the committed PNG take this path, so it is drawn here too."""
        drawn = make_index_arbitrage_figure(out=tmp_path / FIGURE, rates=rates)
        line = _by_gid(drawn.axes[0].lines)["cumulative"]
        np.testing.assert_array_equal(line.get_ydata(), np.cumprod(1 + result.daily) - 1)

    def test_drawing_with_no_rates_screens_the_walks(self, monkeypatch, tmp_path, sources) -> None:
        """Left out, the rates come from ``screen_rates`` on the run's own SPY."""
        seen = []

        def record(index, result):
            seen.append((index, result.test_days))
            return ScreenRates(480, 98, 2000, 561)

        monkeypatch.setattr(index_arbitrage_figures, "screen_rates", record)
        make_index_arbitrage_figure(out=tmp_path / FIGURE, sources=sources)
        ((index, test_days),) = seen
        assert index.equals(sources[3])
        assert len(test_days) == 1076


class TestTheFile:
    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.exists() and out.stat().st_size > 0

    def test_the_committed_figure_exists(self) -> None:
        assert (FIGURES_DIR / FIGURE).is_file()

    def test_main_lets_any_other_error_through_as_itself(self, monkeypatch) -> None:
        def fail(*_a, **_k):
            raise ValueError("a bug, not a refusal")

        monkeypatch.setattr(index_arbitrage_figures, "make_index_arbitrage_figure", fail)
        with pytest.raises(ValueError, match="a bug, not a refusal"):
            main()

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage is lifted from inputData_ETF.mat"),
            WindowCrossesScaleBreak("inputdata_etf/spy.csv changes scale on 2008-01-02"),
        ],
    )
    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(index_arbitrage_figures, "make_index_arbitrage_figure", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)
