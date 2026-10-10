"""The pins for the figure in the post on the Khandani-Lo reversal on Chan's 2012 panel.

``tests/test_khandani_lo_book_two.py`` holds what the run computes. This file
holds that the figure draws those numbers, so a generator that plotted the
wrong example, summed where the script compounds, shaded the wrong year or
labelled a year with another's APR fails even when the arithmetic is right.
Some numbers repeat here on purpose, because a figure's labels are prose and
the suite is the authority for every number prose quotes. No test compares
bytes, for the reason ``tests/test_regime_figure.py`` gives.

The figure reads the vintage and the specification
``tests/test_khandani_lo_book_two.py`` names in its docstring.

One number is pinned here and nowhere else: where each cumulative line ends,
0.898341 for Example 4.3 and 14.566046 for Example 4.4. Each is tied to its
example's APR by the compounding the APR undoes, over 1,260 days of 252, which
is five years.

Exploratory, like everything ``andrewlo_2007_2012.m`` computes here.
"""

from __future__ import annotations

import dataclasses

import numpy as np
import pytest
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.colors import to_hex
from matplotlib.dates import DateFormatter, YearLocator, date2num

from chan import khandani_lo_book_two_figures as figures
from chan import paths
from chan.khandani_lo_book_two import WINDOW_END, WINDOW_START, close_to_close, open_to_close
from chan.khandani_lo_book_two_figures import (
    NAMED_YEARS,
    REVERSAL_FIGURE,
    cumulative_return,
    main,
    make_reversal_figure,
    read_sources,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, INK, MUTED
from chan.vintage import VintageUnavailable
from tests.test_khandani_lo_book_two import YEARLY_APR_PERCENT as YEARS


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def runs(sources):
    _, opens, closes = sources
    return {
        "close-to-close": close_to_close(closes, start=WINDOW_START, end=WINDOW_END),
        "open-to-close": open_to_close(opens, closes, start=WINDOW_START, end=WINDOW_END),
    }


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("khandani_lo_book_two_figure") / REVERSAL_FIGURE


@pytest.fixture(scope="module")
def figure(out, sources):
    return make_reversal_figure(out=out, sources=sources)


@pytest.fixture(scope="module")
def axes(figure):
    held, intraday = figure.axes
    return {"close-to-close": held, "open-to-close": intraday}


@pytest.fixture(scope="module")
def renderer(figure):
    """The figure drawn on the Agg canvas, so tick labels are laid out."""
    canvas = FigureCanvasAgg(figure)
    canvas.draw()
    return canvas.get_renderer()


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _title(ax) -> str:
    return ax.get_title(loc="left")


def _legend(ax) -> list[str]:
    return [t.get_text() for t in ax.get_legend().get_texts()]


class TestThePanels:
    def test_there_are_two_and_the_first_is_figure_4_4(self, figure, axes) -> None:
        assert len(figure.axes) == 2
        assert _title(axes["close-to-close"]).startswith("Figure 4.4: Example 4.3, ")
        assert _title(axes["open-to-close"]).startswith("Example 4.4, ")

    def test_both_share_the_windows_1260_days(self, axes, runs) -> None:
        days = runs["close-to-close"].days
        assert len(days) == 1260
        assert list(runs["open-to-close"].days) == list(days)
        assert {ax.get_xlim() for ax in axes.values()} == {(date2num(days[0]), date2num(days[-1]))}
        first = axes["close-to-close"]
        assert all(first.get_shared_x_axes().joined(first, ax) for ax in axes.values())

    def test_the_date_ticks_read_as_years(self, axes) -> None:
        axis = axes["open-to-close"].xaxis
        assert isinstance(axis.get_major_locator(), YearLocator)
        assert isinstance(axis.get_major_formatter(), DateFormatter)
        assert axis.get_major_formatter().fmt == "%Y"

    def test_both_panels_show_the_years_under_them(self, axes, renderer) -> None:
        """A shared axis hides the top panel's tick labels unless told not to."""
        for name, ax in axes.items():
            shown = {t.get_text() for t in ax.get_xticklabels() if t.get_visible()}
            assert {str(year) for year in range(2008, 2012)} <= shown, name

    def test_each_panel_names_its_units_and_reads_in_percent(self, axes) -> None:
        for ax in axes.values():
            assert ax.get_ylabel() == "cumulative return, compounded"
            assert ax.yaxis.get_major_formatter()(0.5) == "50%"
            assert list(_by_gid(ax.lines)["zero"].get_ydata()) == [0, 0]

    def test_the_title_carries_both_labels(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Exploratory: Khandani and Lo's reversal on Chan's 2012 panel of survivors"
        )

    def test_the_note_names_the_window_the_file_and_the_cost(self, figure) -> None:
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Algorithmic Trading, Examples 4.3 and 4.4, 2007-01-03 to 2011-12-30, 1,260 "
            "trading days, as andrewlo_2007_2012.m runs them.\n"
            "Prices from inputDataOHLCDaily_stocks_20120424.mat, saved 2012-04-25, for the "
            "497 stocks Chan held as the S&P 500 on 2012-04-24.\n"
            "Their prices are carried back, so every figure is about survivors. No cost is "
            "charged."
        ]

    def test_the_note_names_every_save_date_once_in_order(self, tmp_path, sources) -> None:
        """Every member was saved on 2012-04-25, so only a second date shows the rule."""
        members, opens, closes = sources
        later = dataclasses.replace(members[1], saved_date="2013-01-02")
        drawn = make_reversal_figure(
            out=tmp_path / REVERSAL_FIGURE, sources=([later, *members], opens, closes)
        )
        [note] = [t.get_text() for t in drawn.texts if t is not drawn._suptitle]
        assert "saved 2012-04-25, 2013-01-02, for the 498 stocks" in note

    def test_no_label_is_parsed_as_math(self, figure) -> None:
        for ax in figure.axes:
            for text in [*ax.texts, ax.title, ax._left_title]:
                assert text.get_parse_math() is False
        for text in figure.texts:
            assert text.get_parse_math() is False


class TestTheCurves:
    @pytest.mark.parametrize("gid", ["close-to-close", "open-to-close"])
    def test_each_line_is_its_examples_compounded_return(self, axes, runs, gid) -> None:
        line = _by_gid(axes[gid].lines)[gid]
        expected = np.cumprod(1 + runs[gid].daily) - 1
        assert list(line.get_xdata()) == list(runs[gid].days)
        np.testing.assert_array_equal(line.get_ydata(), expected)
        np.testing.assert_array_equal(cumulative_return(runs[gid]), expected)
        assert line.get_color() == INK

    @pytest.mark.parametrize(
        ("gid", "end"), [("close-to-close", 0.898341), ("open-to-close", 14.566046)]
    )
    def test_each_line_ends_where_its_apr_says(self, axes, runs, gid, end) -> None:
        """The APR carried back over 1,260 of 252 days ties each line to its pin."""
        last = _by_gid(axes[gid].lines)[gid].get_ydata()[-1]
        assert last == pytest.approx((1 + runs[gid].apr) ** 5 - 1, abs=1e-12)
        assert last == pytest.approx(end, abs=5e-7)

    def test_each_legend_sets_its_examples_figures(self, axes) -> None:
        assert _legend(axes["close-to-close"]) == ["APR 0.136776, Sharpe ratio 1.259478"]
        assert _legend(axes["open-to-close"]) == ["APR 0.731553, Sharpe ratio 4.713284"]

    def test_each_heading_sets_the_books_figures(self, axes) -> None:
        assert _title(axes["close-to-close"]) == (
            "Figure 4.4: Example 4.3, each day's weights held from one close to the next.\n"
            "The book prints 13.7 percent and 1.3, and 30 percent in 2008 and 11 percent in "
            "2011, the two years shaded."
        )
        assert _title(axes["open-to-close"]) == (
            "Example 4.4, weighted on the overnight move, entered at the open and closed at "
            "the same day's close.\n"
            "The book prints 73 percent and 4.7 and draws no figure, so this one has its "
            "own axis."
        )

    def test_the_axis_holds_the_curve_and_room_for_the_year_labels(self, axes, runs) -> None:
        for gid, ax in axes.items():
            curve = cumulative_return(runs[gid])
            low, high = ax.get_ylim()
            assert low < min(curve.min(), 0.0)
            assert high > curve.max() + 0.25 * (curve.max() - min(curve.min(), 0.0)), gid


class TestTheYears:
    """Each calendar year's APR above its span, and the two years location 2110 names."""

    def test_the_named_years_are_the_books(self) -> None:
        assert NAMED_YEARS == (2008, 2011)

    @pytest.mark.parametrize(
        ("gid", "example"), [("close-to-close", "4.3"), ("open-to-close", "4.4")]
    )
    def test_each_label_carries_its_years_pinned_apr(self, axes, runs, gid, example) -> None:
        texts = _by_gid(axes[gid].texts)
        assert sorted(texts) == [f"year-{year}" for year in range(2007, 2012)]
        for year, percent in YEARS[example].items():
            label = texts[f"year-{year}"].get_text()
            assert label == f"{year}\n{percent:.2f}%".replace("-", "\N{MINUS SIGN}"), label

    def test_a_loss_is_written_with_a_minus_sign(self, axes) -> None:
        label = _by_gid(axes["close-to-close"].texts)["year-2007"].get_text()
        assert label == "2007\n\N{MINUS SIGN}3.05%"

    @pytest.mark.parametrize("gid", ["close-to-close", "open-to-close"])
    def test_each_label_sits_over_the_middle_of_its_year(self, axes, runs, gid) -> None:
        days = runs[gid].days
        for year in range(2007, 2012):
            inside = days[days.year == year]
            text = _by_gid(axes[gid].texts)[f"year-{year}"]
            x, y = text.get_position()
            assert x == inside[0] + (inside[-1] - inside[0]) / 2
            assert y == 0.97

    def test_only_the_first_panel_shades_and_sets_apart_the_named_years(self, axes, runs) -> None:
        held = axes["close-to-close"]
        shades = {p.get_gid(): p for p in held.patches if (p.get_gid() or "").startswith("shade")}
        assert sorted(shades) == ["shade-2008", "shade-2011"]
        days = runs["close-to-close"].days
        for year in NAMED_YEARS:
            inside = days[days.year == year]
            shade = shades[f"shade-{year}"]
            assert (shade.get_x(), shade.get_x() + shade.get_width()) == pytest.approx(
                (date2num(inside[0]), date2num(inside[-1])), abs=1e-9
            )
            assert to_hex(shades[f"shade-{year}"].get_facecolor()) == ACCENT.lower()
        assert not [p for p in axes["open-to-close"].patches if p.get_gid()]
        for gid, ax in axes.items():
            for year in range(2007, 2012):
                text = _by_gid(ax.texts)[f"year-{year}"]
                named = gid == "close-to-close" and year in NAMED_YEARS
                assert text.get_color() == (ACCENT if named else MUTED), (gid, year)
                assert text.get_fontweight() == ("bold" if named else "normal"), (gid, year)


class TestTheReadPath:
    def test_drawing_with_no_sources_reads_the_runs_path(self, monkeypatch, tmp_path, sources):
        asked = []

        def read():
            asked.append(True)
            return sources

        monkeypatch.setattr(figures, "read_sources", read)
        drawn = make_reversal_figure(out=tmp_path / REVERSAL_FIGURE)
        assert asked == [True]
        line = _by_gid(drawn.axes[0].lines)["close-to-close"].get_ydata()
        expected = close_to_close(sources[2], start=WINDOW_START, end=WINDOW_END)
        np.testing.assert_array_equal(line, cumulative_return(expected))

    def test_read_sources_reads_the_panels_closes_and_opens(self, monkeypatch) -> None:
        asked = []

        def recording(source, *, field="Close", data_dir=None):
            asked.append((source, field))
            return [field], field

        monkeypatch.setattr(figures, "load_panel", recording)
        assert read_sources() == (["Close"], "Open", "Close")
        assert asked == [
            ("inputDataOHLCDaily_stocks_20120424.mat", "Close"),
            ("inputDataOHLCDaily_stocks_20120424.mat", "Open"),
        ]

    def test_sources_handed_in_are_the_sources_drawn(self, tmp_path, sources) -> None:
        """Opens and closes swapped, so a figure that ignored the argument would fail."""
        members, opens, closes = sources
        drawn = make_reversal_figure(
            out=tmp_path / REVERSAL_FIGURE, sources=(members, closes, opens)
        )
        line = _by_gid(drawn.axes[1].lines)["open-to-close"].get_ydata()
        swapped = open_to_close(closes, opens, start=WINDOW_START, end=WINDOW_END)
        np.testing.assert_array_equal(line, cumulative_return(swapped))
        held = _by_gid(drawn.axes[0].lines)["close-to-close"].get_ydata()
        np.testing.assert_array_equal(
            held, cumulative_return(close_to_close(opens, start=WINDOW_START, end=WINDOW_END))
        )

    def test_a_missing_vintage_reaches_the_operator_as_one_line(
        self, monkeypatch, tmp_path
    ) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert "inputDataOHLCDaily_stocks_20120424.mat" in str(stopped.value)
        assert "\n" not in str(stopped.value)

    def test_any_other_error_keeps_its_traceback(self, monkeypatch) -> None:
        def broken(*_a, **_k):
            raise KeyError("Close")

        monkeypatch.setattr(figures, "make_reversal_figure", broken)
        with pytest.raises(KeyError, match="Close"):
            main()

    def test_a_refusal_is_turned_into_its_own_text(self, monkeypatch) -> None:
        refusal = VintageUnavailable("no committed vintage is lifted from the panel")

        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(figures, "make_reversal_figure", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)

    def test_the_command_writes_the_committed_path(self, monkeypatch, capsys) -> None:
        drawn = []
        monkeypatch.setattr(figures, "make_reversal_figure", lambda **kw: drawn.append(kw))
        main()
        assert drawn == [{}]
        assert f"wrote {FIGURES_DIR / REVERSAL_FIGURE}" in capsys.readouterr().out

    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.is_file() and out.stat().st_size > 0


def test_the_committed_figure_exists() -> None:
    assert (FIGURES_DIR / REVERSAL_FIGURE).is_file()
