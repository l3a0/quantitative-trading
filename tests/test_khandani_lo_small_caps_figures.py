"""The pins for the figure in the post on the reversal on Chan's S&P 600 file, location 2137.

``tests/test_khandani_lo_small_caps.py`` holds what the run computes. This file
holds that the figure draws those numbers, so a generator that swapped the two
universes, drew the uncharged cost series or headed a panel with the other
price's gap fails even when the arithmetic is right. Some numbers repeat here
on purpose, because a figure's labels are prose and the suite is the authority
for every number prose quotes. No test compares bytes, for the reason
``tests/test_regime_figure.py`` gives.

The figure reads the vintages and the specification that
``tests/test_khandani_lo_small_caps.py`` states in its module docstring:
``ijr_20080114/``, the 600 stocks of Chan's ``IJR_20080114.mat``, chan-mat,
adjusted, saved 2008-01-15, and ``spx_20071123/``, the 500 stocks of his
``SPX_20071123.mat``, chan-mat, adjusted, saved 2007-11-24, each read for the
close and the open, under rule B over 2006-01-03 to 2006-12-29 at 5 basis
points a side. Each line is a running total over that book's own mean gross
position for the year, and the cost lines charge the first day, so they are
the specification Entry 44 lists third rather than Chan's uncharged one.

Exploratory, like everything Entry 44 computes. The running totals were
measured by the write-up after the run. The gaps, standard errors and z values
in the headings are Entry 44's rows 7 and 8, declared before any figure.
"""

from __future__ import annotations

import re

import numpy as np
import pandas as pd
import pytest
from matplotlib.dates import date2num

from chan import khandani_lo_small_caps_figures as module
from chan.khandani_lo import daily_book
from chan.khandani_lo_small_caps import LARGE_CAP_FILE, SOURCE_FILE, compare
from chan.khandani_lo_small_caps_figures import (
    KHANDANI_LO_SMALL_CAPS_FIGURE,
    LINES,
    PRICES,
    main,
    make_khandani_lo_small_caps_figure,
    percent,
    running_totals,
    saved,
    signed,
)
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.regime_figure import ACCENT, INK, MUTED
from chan.vintage import VintageUnavailable
from tests.test_regime_figure import png_size

SPEC = (
    "ijr_20080114/ chan-mat adjusted saved 2008-01-15 against spx_20071123/ chan-mat adjusted "
    "saved 2007-11-24, rule B, 2006-01-03 to 2006-12-29, 5 bp a side with the first day "
    "charged, each day's profit over its own book's mean gross position; measured after the run"
)


@pytest.fixture(scope="module")
def result():
    return compare()


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("khandani_lo_small_caps_figure") / KHANDANI_LO_SMALL_CAPS_FIGURE


@pytest.fixture(scope="module")
def figure(out, result):
    return make_khandani_lo_small_caps_figure(out=out, result=result)


@pytest.fixture(scope="module")
def axes(figure):
    closes, opens = figure.axes
    return {"closes": closes, "opens": opens}


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _title(ax) -> str:
    return ax.get_title(loc="left")


class TestTheFigure:
    def test_there_are_two_panels_closes_above_opens(self, figure, axes) -> None:
        assert len(figure.axes) == 2
        assert PRICES == ("closes", "opens")
        assert _title(axes["closes"]).startswith("On the closes")
        assert _title(axes["opens"]).startswith("On the opens")

    def test_the_title_carries_the_label_and_the_note_names_each_vintage(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Exploratory: Khandani and Lo's reversal on Chan's S&P 600 and S&P 500 files"
        )
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Quantitative Trading, locations 2137 and 2236, over 2006-01-03 to 2006-12-29. The "
            "S&P 600 from IJR_20080114.mat,\nsaved 2008-01-15, and the S&P 500 from "
            "SPX_20071123.mat, saved 2007-11-24. Each line sums the day's profit over\nits own "
            "book's mean gross position for the year. The cost lines charge the first day too, "
            "which Chan's code does not.\nBoth files hold only survivors, and nothing here "
            "measures how many S&P 600 members were microcaps."
        ]

    def test_the_saved_dates_come_from_the_manifest(self) -> None:
        assert (saved(SOURCE_FILE), saved(LARGE_CAP_FILE)) == ("2008-01-15", "2007-11-24")

    def test_a_file_the_manifest_does_not_hold_is_refused(self) -> None:
        with pytest.raises(VintageUnavailable, match="no_such_file.mat has 0 saved dates"):
            saved("no_such_file.mat")

    def test_drawing_with_no_result_reads_the_committed_vintages(self, tmp_path, result) -> None:
        """``main`` and the committed PNG take this path, so it is drawn here too."""
        drawn = make_khandani_lo_small_caps_figure(out=tmp_path / KHANDANI_LO_SMALL_CAPS_FIGURE)
        line = _by_gid(drawn.axes[0].lines)["small-before"]
        r = result.small_closes
        np.testing.assert_array_equal(line.get_ydata(), np.cumsum(r.pnl) / daily_book(r).book)

    def test_both_panels_share_one_scale(self, axes) -> None:
        """The open's lift reads against the close only on one vertical scale."""
        assert axes["closes"].get_ylim() == axes["opens"].get_ylim()


class TestTheRunningTotals:
    """Four running totals in each panel, each over its own book's mean position."""

    @pytest.mark.parametrize("price", PRICES)
    def test_each_panel_draws_the_four_lines_in_order(self, axes, price) -> None:
        drawn = [line.get_gid() for line in axes[price].lines if line.get_gid() in LINES]
        assert drawn == ["small-before", "small-after", "large-before", "large-after"]

    @pytest.mark.parametrize("price", PRICES)
    def test_each_line_spans_the_251_days(self, axes, result, price) -> None:
        days = getattr(result, f"small_{price}").days
        for key in LINES:
            line = _by_gid(axes[price].lines)[key]
            assert pd.DatetimeIndex(line.get_xdata()).equals(days), SPEC
            assert len(days) == 251

    @pytest.mark.parametrize("price", PRICES)
    def test_each_line_is_the_runs_profit_over_its_own_mean_book(self, axes, result, price) -> None:
        """Before costs sums ``pnl``, after costs sums ``pnl_charged``, each over its own book."""
        for universe in ("small", "large"):
            r = getattr(result, f"{universe}_{price}")
            book = daily_book(r).book
            lines = _by_gid(axes[price].lines)
            np.testing.assert_allclose(
                lines[f"{universe}-before"].get_ydata(), np.cumsum(r.pnl) / book, rtol=1e-12
            )
            np.testing.assert_allclose(
                lines[f"{universe}-after"].get_ydata(), np.cumsum(r.pnl_charged) / book, rtol=1e-12
            )

    def test_running_totals_keys_each_line_by_its_gid(self, result) -> None:
        assert list(running_totals(result, "closes")) == list(LINES)

    def test_where_each_line_ends(self, axes) -> None:
        ends = {
            price: {key: f"{_by_gid(axes[price].lines)[key].get_ydata()[-1]:.6f}" for key in LINES}
            for price in PRICES
        }
        assert ends == {
            "closes": {
                "small-before": "0.168664",
                "small-after": "-0.015933",
                "large-before": "0.013244",
                "large-after": "-0.168795",
            },
            "opens": {
                "small-before": "0.297608",
                "small-after": "0.112761",
                "large-before": "0.225436",
                "large-after": "0.041749",
            },
        }, SPEC
        # The S&P 500's closes are the published post's figure, which
        # tests/test_survivorship_and_costs_figures.py pins at the same values.

    def test_where_the_s_and_p_600_closes_after_costs_bottom_out(self, axes) -> None:
        """The low of the closes' dashed S&P 600 line, which the post's alt text quotes."""
        line = _by_gid(axes["closes"].lines)["small-after"]
        totals, days = line.get_ydata(), pd.DatetimeIndex(line.get_xdata())
        low = int(np.argmin(totals))
        assert str(days[low].date()) == "2006-06-30", SPEC
        assert percent(totals[low]) == "−6.3%", SPEC

    @pytest.mark.parametrize(
        ("price", "legend"),
        [
            (
                "closes",
                [
                    "S&P 600, before costs, ending at +16.9%",
                    "S&P 600, after 5 bp a side, ending at −1.6%",
                    "S&P 500, before costs, ending at +1.3%",
                    "S&P 500, after 5 bp a side, ending at −16.9%",
                ],
            ),
            (
                "opens",
                [
                    "S&P 600, before costs, ending at +29.8%",
                    "S&P 600, after 5 bp a side, ending at +11.3%",
                    "S&P 500, before costs, ending at +22.5%",
                    "S&P 500, after 5 bp a side, ending at +4.2%",
                ],
            ),
        ],
    )
    def test_the_legend_names_each_line_and_its_end(self, axes, price, legend) -> None:
        assert [t.get_text() for t in axes[price].get_legend().get_texts()] == legend, SPEC

    @pytest.mark.parametrize("price", PRICES)
    def test_colour_names_the_universe_and_dashes_name_the_cost(self, axes, price) -> None:
        lines = _by_gid(axes[price].lines)
        assert {k: lines[k].get_color() for k in LINES} == {
            "small-before": ACCENT,
            "small-after": ACCENT,
            "large-before": INK,
            "large-after": INK,
        }
        assert {k: lines[k].get_linestyle() for k in LINES} == {
            "small-before": "-",
            "small-after": "--",
            "large-before": "-",
            "large-after": "--",
        }

    @pytest.mark.parametrize("price", PRICES)
    def test_each_panel_draws_a_zero_line(self, axes, price) -> None:
        zero = _by_gid(axes[price].lines)["zero"]
        assert list(zero.get_ydata()) == [0, 0]
        assert zero.get_color() == MUTED

    @pytest.mark.parametrize("price", PRICES)
    def test_the_axis_spans_the_window_and_reads_a_percentage(self, axes, price) -> None:
        assert axes[price].get_xlim() == (
            date2num(pd.Timestamp("2006-01-03")),
            date2num(pd.Timestamp("2006-12-29")),
        )
        assert axes[price].yaxis.get_major_formatter()(0.1) == "10%"


class TestTheHeadings:
    """Each heading carries its price's gap, standard error and z, Entry 44's rows 7 and 8."""

    def test_the_closes_heading(self, axes) -> None:
        assert _title(axes["closes"]) == (
            "On the closes, the S&P 600's Sharpe ratio before costs is 3.4086 against the "
            "S&P 500's 0.2510.\nThe gap is +3.1576, its standard error 0.9872, so z is "
            "+3.1987, beyond the line of 2 standard errors."
        )

    def test_the_opens_heading(self, axes) -> None:
        assert _title(axes["opens"]) == (
            "On the opens, the S&P 600's Sharpe ratio before costs is 5.3052 against the "
            "S&P 500's 4.4202.\nThe gap is +0.8850, its standard error 1.1640, so z is "
            "+0.7603, within the line of 2 standard errors."
        )

    def test_a_heading_reads_its_own_prices_gap(self, result) -> None:
        """Handing the closes' gap to the opens' heading would change every figure in it."""
        assert module.heading("opens", result.closes_gap) != module.heading(
            "opens", result.opens_gap
        )
        assert "within" in module.heading("opens", result.opens_gap)
        assert "beyond" in module.heading("closes", result.closes_gap)


class TestTheHelpers:
    def test_signed_always_shows_the_sign_with_a_true_minus(self) -> None:
        assert signed(3.15762) == "+3.1576"
        assert signed(-0.37021) == "−0.3702"
        assert signed(0.76031, 2) == "+0.76"

    def test_percent_prints_one_decimal_with_a_true_minus(self) -> None:
        assert percent(0.168664) == "+16.9%"
        assert percent(-0.015933) == "−1.6%"


class TestTheFile:
    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.exists() and out.stat().st_size > 0

    def test_the_committed_figure_exists(self) -> None:
        assert (FIGURES_DIR / KHANDANI_LO_SMALL_CAPS_FIGURE).is_file()

    def test_a_fresh_draw_has_the_committed_image_dimensions(self, figure, out) -> None:
        assert png_size(out) == png_size(FIGURES_DIR / KHANDANI_LO_SMALL_CAPS_FIGURE)

    def test_drawing_to_out_leaves_the_committed_figure_alone(self, tmp_path, result) -> None:
        committed = FIGURES_DIR / KHANDANI_LO_SMALL_CAPS_FIGURE
        before = committed.read_bytes()
        touched = committed.stat().st_mtime_ns
        make_khandani_lo_small_caps_figure(
            out=tmp_path / KHANDANI_LO_SMALL_CAPS_FIGURE, result=result
        )
        assert committed.read_bytes() == before
        # A redraw is deterministic, so a stray write would leave the bytes
        # the same. Only the modification time shows it.
        assert committed.stat().st_mtime_ns == touched

    def test_a_result_handed_in_is_drawn_without_a_second_read(
        self, monkeypatch, tmp_path, result
    ) -> None:
        def refuse(*_a, **_k):
            raise AssertionError("compare ran although a result was handed in")

        monkeypatch.setattr(module, "compare", refuse)
        make_khandani_lo_small_caps_figure(
            out=tmp_path / KHANDANI_LO_SMALL_CAPS_FIGURE, result=result
        )

    def test_main_lets_any_other_error_through_as_itself(self, monkeypatch) -> None:
        def fail(*_a, **_k):
            raise ValueError("a bug, not a refusal")

        monkeypatch.setattr(module, "make_khandani_lo_small_caps_figure", fail)
        with pytest.raises(ValueError, match="a bug, not a refusal"):
            main()

    def test_a_missing_vintage_reaches_the_operator_as_one_line(
        self, monkeypatch, tmp_path
    ) -> None:
        """No mock: the real read, pointed at an empty directory, refuses the S&P 600 file."""
        from chan import paths

        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert isinstance(stopped.value.__cause__, VintageUnavailable)
        assert "IJR_20080114.mat" in str(stopped.value)
        assert "\n" not in str(stopped.value)

    def test_main_reports_the_file_it_wrote(self, monkeypatch, capsys) -> None:
        monkeypatch.setattr(module, "make_khandani_lo_small_caps_figure", lambda: None)
        main()
        assert capsys.readouterr().out == f"wrote {FIGURES_DIR / KHANDANI_LO_SMALL_CAPS_FIGURE}\n"


POST = REPO_ROOT / "blog" / "khandani-lo-small-caps-lessons.md"


@pytest.fixture(scope="module")
def alt() -> str:
    post = POST.read_text(encoding="utf-8")
    found = re.findall(
        r"!\[([^\]]*)\]\(\.\./docs/figures/" + re.escape(KHANDANI_LO_SMALL_CAPS_FIGURE) + r"\)",
        post,
    )
    assert len(found) == 1
    return found[0]


class TestTheAltText:
    """The post's alt text quotes the figure's numbers, so it is held against what the figure draws.

    The alt text reads each line's end, and the low of the closes' dashed
    S&P 600 line, as signed percentages in the order below, and each heading's
    five figures. Its words about a line's shape, such as wandering around zero
    or dipping below it in the middle of the year, are read off the chart and
    not asserted.
    """

    def test_the_percentages_in_the_order_the_alt_text_reads_them(self, alt, axes) -> None:
        def ydata(price: str, key: str) -> np.ndarray:
            return _by_gid(axes[price].lines)[key].get_ydata()

        expected = [
            percent(ydata("closes", "small-before")[-1]),
            percent(ydata("closes", "small-after").min()),
            percent(ydata("closes", "small-after")[-1]),
            percent(ydata("closes", "large-before")[-1]),
            percent(ydata("closes", "large-after")[-1]),
            percent(ydata("opens", "small-before")[-1]),
            percent(ydata("opens", "large-before")[-1]),
            percent(ydata("opens", "small-after")[-1]),
            percent(ydata("opens", "large-after")[-1]),
        ]
        assert re.findall(r"[+−]\d+\.\d%", alt) == expected, SPEC

    def test_each_headings_figures(self, alt, result) -> None:
        for price in PRICES:
            g = getattr(result, f"{price}_gap")
            word = "beyond" if g.beyond_noise else "within"
            assert (
                f"Sharpe ratios of {g.a_sharpe:.4f} and {g.b_sharpe:.4f}, "
                f"a gap of {signed(g.gap)}, a standard error of {g.standard_error:.4f} "
                f"and a z of {signed(g.z)}, {word}"
            ) in alt, price
