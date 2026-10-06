"""The pins for the factor models post's one figure.

``tests/test_momentum_factor.py`` holds what Entry 14 computes. This file holds
that the figure draws those numbers, so a generator that drew the curve from
the wrong stocks, put a factor's line at the other factor's value or shaded a
band of the wrong width fails even when the arithmetic is right. Some numbers
repeat here on purpose, because a figure's labels are prose and the suite is
the authority for every number prose quotes. No test compares bytes, for the
reason ``tests/test_regime_figure.py`` gives.

The vintages are the three ``tests/test_momentum_factor.py`` names.

1. ``spx_20071123/``, the 500 S&P 500 members lifted from Chan's
   ``SPX_20071123.mat``, saved 2007-11-24.
2. ``spy_chan.csv``, from Chan's ``example6_2.xls``, saved 2008-01-29.
3. FRED's TB3MS, downloaded 2026-09-30.

The specification is :mod:`chan.momentum_factor` as
[issue 22](https://github.com/l3a0/quantitative-trading/issues/22) fixed it.
Like the test it draws, the figure is exploratory.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from matplotlib.colors import same_color, to_rgba

import chan.momentum_factor_figures as figures
from chan.momentum_factor import Comparison, EmptyLeg, autocorrelations, build_factors, read_sources
from chan.momentum_factor_figures import AUTOCORRELATION_FIGURE, make_autocorrelation_figure
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST
from chan.vintage import VintageUnavailable


@pytest.fixture(scope="module")
def comparison() -> Comparison:
    """Read once, because ``read_sources`` hashes and parses all 500 members."""
    _, closes, _, spy, _, bills = read_sources()
    return autocorrelations(build_factors(closes, spy, bills))


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("momentum_factor_figures") / AUTOCORRELATION_FIGURE


@pytest.fixture(scope="module")
def figure(comparison, out):
    return make_autocorrelation_figure(comparison, out=out)


def _by_gid(figure) -> dict:
    ax = figure.axes[0]
    return {
        a.get_gid(): a for a in [*ax.lines, *ax.texts, *ax.patches, *ax.collections] if a.get_gid()
    }


def _height_at(figure, x: float) -> float:
    """The drawn curve's height at ``x``, read off the step's own vertices."""
    step = _by_gid(figure)["stocks"]
    xs, ys = np.asarray(step.get_xdata()), np.asarray(step.get_ydata())
    below = np.flatnonzero(xs <= x)
    return 0.0 if not len(below) else float(ys[below[-1]])


class TestTheCurve:
    def test_its_steps_are_the_446_stocks_sorted(self, figure, comparison) -> None:
        step = _by_gid(figure)["stocks"]
        assert len(step.get_xdata()) == 446
        assert list(step.get_xdata()) == sorted(comparison.stocks)

    def test_its_heights_run_from_one_446th_to_1(self, figure) -> None:
        heights = np.asarray(_by_gid(figure)["stocks"].get_ydata())
        assert heights == pytest.approx(np.arange(1, 447) / 446, abs=1e-15)

    def test_it_steps_at_each_stock_not_between_them(self, figure) -> None:
        """A step drawn the other way puts each stock's height on the one before."""
        assert _by_gid(figure)["stocks"].get_drawstyle() == "steps-post"

    def test_the_y_axis_names_the_share_at_or_below(self, figure) -> None:
        assert figure.axes[0].get_ylabel() == "share of the 446 stocks at or below"
        assert figure.axes[0].get_xlabel() == "lag-1 autocorrelation of 83 monthly returns"


class TestTheFactors:
    @pytest.mark.parametrize(("tag", "field"), [("mkt", "mkt"), ("wml", "wml")])
    def test_each_line_sits_at_its_factors_value(self, figure, comparison, tag, field) -> None:
        assert set(_by_gid(figure)[tag].get_xdata()) == {getattr(comparison, field)}

    def test_no_stock_ties_either_factor(self, comparison) -> None:
        """What lets the share at or below stand for the percentile, which counts strictly below."""
        assert not (comparison.stocks == comparison.mkt).any()
        assert not (comparison.stocks == comparison.wml).any()

    @pytest.mark.parametrize(("tag", "field"), [("mkt", "mkt"), ("wml", "wml")])
    def test_each_line_meets_the_curve_at_its_percentile(
        self, figure, comparison, tag, field
    ) -> None:
        value = getattr(comparison, field)
        share = comparison.percentile(value) / 100
        assert _height_at(figure, value) == pytest.approx(share, abs=1e-15)
        meets = _by_gid(figure)[f"{tag}-meets"]
        assert (meets.get_xdata()[0], meets.get_ydata()[0]) == pytest.approx((value, share))

    def test_the_median_line_sits_at_the_median_stock(self, figure, comparison) -> None:
        assert set(_by_gid(figure)["median"].get_xdata()) == {comparison.median}

    def test_the_zero_line_sits_at_zero(self, figure) -> None:
        assert set(_by_gid(figure)["zero"].get_xdata()) == {0}

    def test_the_two_factors_are_drawn_apart(self, figure) -> None:
        """The labels name the factors, and the lines must not need them to."""
        mkt, wml = _by_gid(figure)["mkt"], _by_gid(figure)["wml"]
        assert to_rgba(mkt.get_color()) != to_rgba(wml.get_color())
        assert mkt.get_linestyle() != wml.get_linestyle()

    @pytest.mark.parametrize(("tag", "colour", "style"), [("mkt", ACCENT, "-"), ("wml", INK, "--")])
    def test_each_factor_wears_its_own_colour_and_dash(self, figure, tag, colour, style) -> None:
        """The post's alt text tells the factors apart by dash, solid MKT and dashed WML."""
        line = _by_gid(figure)[tag]
        assert same_color(line.get_color(), colour)
        assert line.get_linestyle() == style

    @pytest.mark.parametrize("tag", ["mkt", "wml"])
    def test_each_meeting_point_wears_its_factors_colour(self, figure, tag) -> None:
        """The dot is where the factor's line meets the curve, so it reads as that line's."""
        drawn = _by_gid(figure)
        assert same_color(drawn[f"{tag}-meets"].get_color(), drawn[tag].get_color())

    def test_the_median_line_is_dotted(self, figure) -> None:
        """The post's alt text names it the dotted line, apart from both factors' dashes."""
        assert _by_gid(figure)["median"].get_linestyle() == ":"

    def test_the_axes_show_the_whole_curve(self, figure) -> None:
        """A share runs from 0 to 1, so nothing the curve or a label sits on is clipped."""
        low, high = figure.axes[0].get_ylim()
        assert low == 0 and high >= 1


def _band_edges(figure) -> tuple[float, float]:
    """The shaded band's left and right edges, in autocorrelation units."""
    band = _by_gid(figure)["band"]
    return band.get_x(), band.get_x() + band.get_width()


class TestTheBand:
    def test_its_edges_are_the_comparisons_band(self, figure, comparison) -> None:
        assert _band_edges(figure) == pytest.approx((-comparison.band, comparison.band), abs=1e-15)

    def test_it_spans_the_whole_height(self, figure) -> None:
        band = _by_gid(figure)["band"]
        assert (band.get_y(), band.get_height()) == (0, 1)

    def test_the_band_is_0_2151(self, figure) -> None:
        assert round(_band_edges(figure)[1], 4) == 0.2151
        assert round(_band_edges(figure)[0], 4) == -0.2151

    def test_both_factors_and_the_median_sit_inside_it(self, figure, comparison) -> None:
        """What the post's caption says, so the caption has a pin."""
        for value in (comparison.mkt, comparison.wml, comparison.median):
            assert -comparison.band < value < comparison.band


class TestTheWords:
    def test_the_labels_read_the_figures_the_post_quotes(self, figure) -> None:
        labels = _by_gid(figure)
        assert labels["label-mkt"].get_text() == "MKT 0.0675\n80.7175th percentile"
        assert labels["label-wml"].get_text() == "WML −0.1099\n27.8027th percentile"
        assert labels["label-median"].get_text() == "median stock −0.0392"
        assert labels["label-band"].get_text() == (
            "±0.2151, where a series with no\nautocorrelation lands 95 percent of the time"
        )

    def test_each_factor_label_hangs_off_its_own_point(self, figure, comparison) -> None:
        labels = _by_gid(figure)
        for tag, value in (("mkt", comparison.mkt), ("wml", comparison.wml)):
            assert labels[f"label-{tag}"].xy == pytest.approx(
                (value, comparison.percentile(value) / 100)
            )

    def test_the_median_and_band_labels_sit_on_their_own_lines(self, figure, comparison) -> None:
        labels = _by_gid(figure)
        assert labels["label-median"].xy[0] == comparison.median
        assert labels["label-band"].xy[0] == comparison.band

    def test_the_title_carries_the_exploratory_label(self, figure) -> None:
        title = figure._suptitle.get_text()
        assert title == "Factor momentum on Chan's S&P 500 file, an exploratory test"

    def test_the_note_names_the_survivors_and_spy(self, figure) -> None:
        note = figure.texts[-1].get_text().replace("\n", " ")
        assert note.startswith(
            "The 446 stocks are every stock in spx_20071123/ priced in all 83 holding months."
        )
        assert "in the S&P 500 on 2007-11-23, so WML and every stock here are survivors." in note
        assert "MKT reads SPY, which held the index as it stood each day, so it is not." in note

    def test_no_label_is_parsed_as_math(self, figure) -> None:
        """The title carries an ampersand and the labels minus signs, so math
        parsing stays off the way it does for the other figures."""
        ax = figure.axes[0]
        for text in [
            *ax.texts,
            *figure.texts,
            ax.xaxis.label,
            ax.yaxis.label,
            *ax.get_xticklabels(),
            *ax.get_yticklabels(),
        ]:
            assert text.get_parse_math() is False

    def test_nothing_wears_a_verdict_colour(self, figure) -> None:
        """Neither verdict can be told from noise, so nothing is green or red."""
        ax = figure.axes[0]
        verdicts = {to_rgba(GOOD)[:3], to_rgba(LOST)[:3]}
        assert to_rgba(figure.patch.get_facecolor())[:3] not in verdicts
        for patch in ax.patches:
            assert to_rgba(patch.get_facecolor())[:3] not in verdicts
            assert to_rgba(patch.get_edgecolor())[:3] not in verdicts
        for line in ax.lines:
            assert to_rgba(line.get_color())[:3] not in verdicts
            assert to_rgba(line.get_markerfacecolor())[:3] not in verdicts
        for text in [
            *ax.texts,
            *figure.texts,
            ax.xaxis.label,
            ax.yaxis.label,
            *ax.get_xticklabels(),
            *ax.get_yticklabels(),
        ]:
            assert to_rgba(text.get_color())[:3] not in verdicts


def test_drawing_writes_the_file_it_is_given(figure, out) -> None:
    assert out.is_file()


def test_drawing_reads_only_the_comparison_it_is_given(monkeypatch, tmp_path) -> None:
    """A hand-built comparison draws its own four stocks, and nothing reads a vintage."""

    def refuse(*_args, **_kwargs):
        raise AssertionError("the figure read a vintage instead of the comparison it was given")

    for name in ("read_sources", "build_factors", "autocorrelations"):
        monkeypatch.setattr(figures, name, refuse)
    small = Comparison(mkt=0.15, wml=-0.25, stocks=pd.Series([0.3, -0.1, 0.1, -0.3]), months=83)
    drawn = make_autocorrelation_figure(small, out=tmp_path / AUTOCORRELATION_FIGURE)
    assert list(_by_gid(drawn)["stocks"].get_xdata()) == [-0.3, -0.1, 0.1, 0.3]
    assert _height_at(drawn, small.mkt) == 0.75
    assert _height_at(drawn, small.wml) == 0.25


def test_the_committed_figure_exists() -> None:
    assert (FIGURES_DIR / AUTOCORRELATION_FIGURE).is_file()


def test_the_command_reads_the_vintages_once_and_draws(monkeypatch, capsys) -> None:
    reads, built, drawn = [], [], []
    sources = ("members", "closes", "spy entry", "spy", "bill entry", "bills")
    monkeypatch.setattr(figures, "read_sources", lambda: reads.append(1) or sources)
    monkeypatch.setattr(figures, "build_factors", lambda *args: built.append(args) or "factors")
    monkeypatch.setattr(figures, "autocorrelations", lambda f: f"comparison of {f}")
    monkeypatch.setattr(figures, "make_autocorrelation_figure", lambda c: drawn.append(c))
    figures.main()
    assert reads == [1]
    assert built == [("closes", "spy", "bills")]
    assert drawn == ["comparison of factors"]
    assert AUTOCORRELATION_FIGURE in capsys.readouterr().out


def test_a_missing_vintage_reaches_the_operator_as_one_line(monkeypatch) -> None:
    def refuse(*_args, **_kwargs):
        raise VintageUnavailable("no committed vintage is lifted from SPX_20071123.mat")

    monkeypatch.setattr(figures, "read_sources", refuse)
    with pytest.raises(SystemExit, match="no committed vintage is lifted from SPX_20071123.mat"):
        figures.main()


def test_an_empty_leg_reaches_the_operator_as_one_line(monkeypatch) -> None:
    def refuse(*_args, **_kwargs):
        raise EmptyLeg("the loser leg is empty for the month ending 2000-12-29")

    monkeypatch.setattr(figures, "read_sources", lambda: (None,) * 6)
    monkeypatch.setattr(figures, "build_factors", refuse)
    with pytest.raises(SystemExit, match="loser leg is empty for the month ending 2000-12-29"):
        figures.main()


def test_any_other_failure_still_ends_in_a_traceback(monkeypatch) -> None:
    """Only a refusal becomes one line, so a real bug is not hidden."""

    def broken(*_args, **_kwargs):
        raise ValueError("a bug, not a refusal")

    monkeypatch.setattr(figures, "read_sources", broken)
    with pytest.raises(ValueError, match="a bug, not a refusal"):
        figures.main()
