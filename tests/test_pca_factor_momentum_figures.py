"""The pins for the PCA factor momentum post's one figure.

``tests/test_pca_factor_momentum.py`` holds what Entry 42 computes and what
the write-up measured after the run. This file holds that the figure draws
those numbers, so a generator that drew the curve from the wrong stocks, put a
factor's dot at another factor's value, or swapped two of the second panel's
statistics fails even when the arithmetic is right. Some numbers repeat here
on purpose, because a figure's labels are prose and the suite is the
authority for every number prose quotes. No test compares bytes, for the
reason ``tests/test_regime_figure.py`` gives.

The vintage is ``ijr_20080114/``, the 600 S&P 600 members lifted from Chan's
``IJR_20080114.mat``, saved 2008-01-15, read for the Close column. The
specification is :mod:`chan.pca_factor_momentum` as
[issue 286](https://github.com/l3a0/quantitative-trading/issues/286) fixed it.
The second panel's statistics were measured after the run and decide nothing.
Like the test it draws, the figure is exploratory.
"""

from __future__ import annotations

import numpy as np
import pytest
from matplotlib.colors import same_color, to_rgba

import chan.pca_factor_momentum_figures as figures
from chan.paths import FIGURES_DIR
from chan.pca_factor import SMALL_CAPS
from chan.pca_factor_momentum import (
    NAMES,
    Results,
    WeightStatistics,
    compute_both,
    daily_components,
    file_returns,
    weight_statistics,
)
from chan.pca_factor_momentum_figures import (
    LABEL_SPOTS,
    PCA_FACTOR_MOMENTUM_FIGURE,
    WAYS,
    factor_label,
    make_pca_factor_momentum_figure,
)
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED, SURFACE
from chan.series import load_panel
from chan.vintage import VintageUnavailable


@pytest.fixture(scope="module")
def drawn_from() -> tuple[Results, WeightStatistics]:
    """Computed once, because each takes hundreds of decompositions."""
    _, closes = load_panel(SMALL_CAPS, field="Close")
    returns = file_returns(closes)
    return compute_both(closes), weight_statistics(returns, daily_components(returns))


@pytest.fixture(scope="module")
def results(drawn_from) -> Results:
    return drawn_from[0]


@pytest.fixture(scope="module")
def weights(drawn_from) -> WeightStatistics:
    return drawn_from[1]


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("pca_factor_momentum_figures") / PCA_FACTOR_MOMENTUM_FIGURE


@pytest.fixture(scope="module")
def figure(results, weights, out):
    return make_pca_factor_momentum_figure(results, weights, out=out)


def _by_gid(figure, panel: int) -> dict:
    ax = figure.axes[panel]
    return {
        a.get_gid(): a for a in [*ax.lines, *ax.texts, *ax.patches, *ax.collections] if a.get_gid()
    }


def _height_at(figure, x: float) -> float:
    """The drawn curve's height at ``x``, read off the step's own vertices."""
    step = _by_gid(figure, 0)["stocks"]
    xs, ys = np.asarray(step.get_xdata()), np.asarray(step.get_ydata())
    below = np.flatnonzero(xs <= x)
    return 0.0 if not len(below) else float(ys[below[-1]])


def _point(line) -> tuple[float, float]:
    return float(line.get_xdata()[0]), float(line.get_ydata()[0])


class TestTheCurve:
    def test_its_steps_are_the_579_stocks_sorted(self, figure, results) -> None:
        step = _by_gid(figure, 0)["stocks"]
        assert len(step.get_xdata()) == 579
        assert list(step.get_xdata()) == sorted(results.spliced.comparison.stocks)

    def test_its_heights_run_from_one_579th_to_1(self, figure) -> None:
        heights = np.asarray(_by_gid(figure, 0)["stocks"].get_ydata())
        assert heights == pytest.approx(np.arange(1, 580) / 579, abs=1e-15)

    def test_it_steps_at_each_stock_not_between_them(self, figure) -> None:
        assert _by_gid(figure, 0)["stocks"].get_drawstyle() == "steps-post"

    def test_the_axes_name_what_they_measure(self, figure) -> None:
        ax = figure.axes[0]
        assert ax.get_ylabel() == "share of the 579 stocks at or below"
        assert ax.get_xlabel() == (
            "uncentred correlation of 752 pairs of one day's return and the next"
        )

    def test_the_axes_show_every_stock(self, figure, results) -> None:
        low, high = figure.axes[0].get_xlim()
        stocks = results.spliced.comparison.stocks
        assert low < stocks.min() and stocks.max() < high
        assert figure.axes[0].get_ylim() == (0, 1.02)


class TestTheFactors:
    @pytest.mark.parametrize("k", range(5))
    def test_each_filled_dot_sits_on_the_curve_at_its_percentile(self, figure, results, k) -> None:
        c = results.spliced.comparison
        value, share = c.factors[k], c.percentile(c.factors[k]) / 100
        assert _point(_by_gid(figure, 0)[NAMES[k].lower()]) == pytest.approx((value, share))
        assert _height_at(figure, value) == pytest.approx(share, abs=1e-15)

    @pytest.mark.parametrize("k", range(5))
    def test_each_hollow_dot_sits_at_its_percentile_among_the_578(self, figure, results, k) -> None:
        u = results.unspliced.comparison
        drawn = _by_gid(figure, 0)[f"{NAMES[k].lower()}-without"]
        assert _point(drawn) == pytest.approx((u.factors[k], u.percentile(u.factors[k]) / 100))
        assert same_color(drawn.get_markerfacecolor(), figures.SURFACE)

    @pytest.mark.parametrize("k", range(5))
    def test_a_line_joins_each_factors_two_dots(self, figure, results, k) -> None:
        tag = NAMES[k].lower()
        drawn = _by_gid(figure, 0)
        moves = drawn[f"{tag}-moves"]
        assert list(zip(moves.get_xdata(), moves.get_ydata(), strict=True)) == [
            _point(drawn[tag]),
            _point(drawn[f"{tag}-without"]),
        ]

    def test_the_filled_dots_are_filled(self, figure) -> None:
        for name in NAMES:
            dot = _by_gid(figure, 0)[name.lower()]
            assert same_color(dot.get_markerfacecolor(), ACCENT)

    def test_the_median_line_sits_at_the_median_stock(self, figure, results) -> None:
        drawn = _by_gid(figure, 0)["median"]
        assert set(drawn.get_xdata()) == {results.spliced.comparison.median}
        assert drawn.get_linestyle() == ":"

    def test_the_zero_line_sits_at_zero(self, figure) -> None:
        assert set(_by_gid(figure, 0)["zero"].get_xdata()) == {0}


class TestTheBand:
    @pytest.mark.parametrize("panel", [0, 1])
    def test_both_panels_shade_plus_and_minus_0_0715(self, figure, results, panel) -> None:
        band = _by_gid(figure, panel)["band"]
        if panel == 0:
            edges = (band.get_x(), band.get_x() + band.get_width())
        else:
            edges = (band.get_y(), band.get_y() + band.get_height())
        width = results.spliced.comparison.band
        assert edges == pytest.approx((-width, width), abs=1e-15)
        assert round(edges[1], 4) == 0.0715

    def test_it_wears_no_factors_colour(self, figure) -> None:
        band = to_rgba(_by_gid(figure, 0)["band"].get_facecolor())[:3]
        assert not same_color(band, ACCENT)
        assert not same_color(band, INK)


class TestTheWords:
    def test_each_label_reads_the_figures_the_post_quotes(self, figure) -> None:
        labels = {name: _by_gid(figure, 0)[f"label-{name.lower()}"].get_text() for name in NAMES}
        assert labels == {
            "PC1": "PC1 0.0316 → 0.0740",
            "PC2": "PC2 0.0778 → −0.0152",
            "PC3": "PC3 −0.0189 → 0.0139",
            "PC4": "PC4 0.0305 → 0.0975",
            "PC5": "PC5 0.0710 → 0.0536",
        }

    def test_the_label_writes_with_pmc_then_without(self) -> None:
        assert factor_label("PCX", 0.1, -0.2) == "PCX 0.1000 → −0.2000"

    def test_each_label_points_at_its_filled_dot(self, figure) -> None:
        drawn = _by_gid(figure, 0)
        for name in NAMES:
            assert drawn[f"label-{name.lower()}"].xy == pytest.approx(_point(drawn[name.lower()]))

    def test_the_labels_run_down_in_the_order_of_their_dots(self, figure) -> None:
        """So no two leader lines cross on the way from the column to the curve."""
        drawn = _by_gid(figure, 0)
        by_dot = sorted(NAMES, key=lambda name: -_point(drawn[name.lower()])[1])
        by_label = sorted(NAMES, key=lambda name: -LABEL_SPOTS[name][1])
        assert by_dot == by_label == ["PC2", "PC5", "PC1", "PC4", "PC3"]

    def test_the_labels_sit_below_the_curve_and_right_of_their_dots(self, figure) -> None:
        """The curve climbs to the right, so the space below it there is empty."""
        drawn = _by_gid(figure, 0)
        for name in NAMES:
            x, y = LABEL_SPOTS[name]
            dot_x, dot_y = _point(drawn[name.lower()])
            assert x > dot_x and y < dot_y
            assert y < _height_at(figure, x)

    def test_the_median_and_band_labels(self, figure, results) -> None:
        drawn = _by_gid(figure, 0)
        assert drawn["label-median"].get_text() == "median stock −0.0283"
        assert drawn["label-median"].xy[0] == results.spliced.comparison.median
        assert drawn["label-band"].get_text() == (
            "±0.0715, where a series\nwith no persistence lands\n95 percent of the time"
        )
        assert drawn["label-band"].xy[0] == results.spliced.comparison.band

    def test_the_panel_titles(self, figure) -> None:
        assert figure.axes[0].get_title(loc="left") == (
            "The verdicts: each factor with PMC, filled, → without it, hollow"
        )
        assert figure.axes[1].get_title(loc="left") == (
            "Why each pair reads one day's weights, measured after the run"
        )

    def test_the_title_carries_the_exploratory_label(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Example 7.4's own factors on Chan's S&P 600 file, an exploratory test"
        )

    def test_the_note_names_the_survivors_and_what_decides_nothing(self, figure) -> None:
        note = figure.texts[-1].get_text().replace("\n", " ")
        assert note.startswith(
            "The 579 stocks are every stock in ijr_20080114/ priced on every day the pairs read."
        )
        assert "in the S&P 600 on 2008-01-14, so every figure here is about survivors." in note
        assert "A hollow dot sits at its percentile among the 578 stocks left without PMC." in note
        assert "The shaded band is the same in both panels." in note
        assert "Panel 2 was measured after the verdicts and decides nothing." in note

    def test_no_label_is_parsed_as_math(self, figure) -> None:
        for ax in figure.axes:
            for text in [
                *ax.texts,
                ax.xaxis.label,
                ax.yaxis.label,
                *ax.get_xticklabels(),
                *ax.get_yticklabels(),
            ]:
                assert text.get_parse_math() is False
        for text in figure.texts:
            assert text.get_parse_math() is False

    def test_nothing_wears_a_verdict_colour(self, figure) -> None:
        """No factor clears the noise, so nothing is green or red."""
        verdicts = {to_rgba(GOOD)[:3], to_rgba(LOST)[:3]}
        assert to_rgba(figure.patch.get_facecolor())[:3] not in verdicts
        for ax in figure.axes:
            for patch in ax.patches:
                assert to_rgba(patch.get_facecolor())[:3] not in verdicts
            for line in ax.lines:
                for colour in (
                    line.get_color(),
                    line.get_markerfacecolor(),
                    line.get_markeredgecolor(),
                ):
                    assert to_rgba(colour)[:3] not in verdicts
            for text in [*ax.texts, ax.xaxis.label, ax.yaxis.label]:
                assert to_rgba(text.get_color())[:3] not in verdicts


class TestTheWaysPanel:
    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            ("own", (0.0326, -0.1105, -0.0283, -0.0315, 0.0025)),
            ("matched", (0.0246, -0.0161, -0.0318, -0.0285, 0.0768)),
            ("left_out", (0.0315, 0.0776, -0.0228, 0.0338, 0.0713)),
            ("paired", (0.0316, 0.0778, -0.0189, 0.0305, 0.0710)),
        ],
    )
    def test_each_way_draws_its_statistics(self, figure, results, weights, field, expected) -> None:
        drawn = np.asarray(_by_gid(figure, 1)[field].get_ydata())
        source = (
            results.spliced.comparison.factors if field == "paired" else getattr(weights, field)
        )
        np.testing.assert_array_equal(drawn, source)
        assert drawn == pytest.approx(expected, abs=5e-5)

    def test_each_factors_four_sit_around_its_tick_in_the_legends_order(self, figure) -> None:
        ax = figure.axes[1]
        assert [t.get_text() for t in ax.get_xticklabels()] == list(NAMES)
        xs = np.array([_by_gid(figure, 1)[field].get_xdata() for field, *_ in WAYS])
        assert (np.diff(xs, axis=0) > 0).all(), "left to right in the order WAYS lists"
        np.testing.assert_allclose(xs.mean(axis=0), np.arange(5), atol=1e-12)
        assert (np.abs(xs - np.arange(5)) < 0.5).all(), "each sits nearer its own tick"

    def test_the_legend_names_each_way(self, figure) -> None:
        legend = figure.axes[1].get_legend()
        assert [t.get_text() for t in legend.get_texts()] == [
            "each day's own weights, largest weight positive",
            "sign and rank matched",
            "tomorrow's weights on 251 days without today",
            "both days on today's weights, as tested",
        ]
        assert legend.get_title().get_text() == "tomorrow's factor return read on"

    def test_each_way_carries_its_own_legend_entry(self, figure) -> None:
        """Read by series rather than in the legend's order, so a label on another series fails."""
        drawn = _by_gid(figure, 1)
        assert {field: drawn[field].get_label() for field, *_ in WAYS} == {
            "own": "each day's own weights, largest weight positive",
            "matched": "sign and rank matched",
            "left_out": "tomorrow's weights on 251 days without today",
            "paired": "both days on today's weights, as tested",
        }

    def test_the_four_are_drawn_apart(self, figure) -> None:
        drawn = _by_gid(figure, 1)
        looks = {
            (field, drawn[field].get_marker(), to_rgba(drawn[field].get_markerfacecolor()))
            for field, *_ in WAYS
        }
        assert len({look[1:] for look in looks}) == 4

    def test_the_test_s_own_statistic_is_the_ink_dot(self, figure) -> None:
        paired = _by_gid(figure, 1)["paired"]
        assert paired.get_marker() == "o"
        assert same_color(paired.get_markerfacecolor(), INK)

    @pytest.mark.parametrize(
        ("field", "marker", "edge", "face"),
        [
            ("own", "o", MUTED, SURFACE),
            ("matched", "s", MUTED, MUTED),
            ("left_out", "D", ACCENT, ACCENT),
            ("paired", "o", INK, INK),
        ],
    )
    def test_each_way_wears_the_marker_the_alt_text_names(
        self, figure, field, marker, edge, face
    ) -> None:
        """A hollow circle, a grey square, a brass diamond and a black dot, as the post says.

        Written out rather than read from ``WAYS``, so a change there fails here.
        """
        drawn = _by_gid(figure, 1)[field]
        assert drawn.get_marker() == marker
        assert same_color(drawn.get_markeredgecolor(), edge)
        assert same_color(drawn.get_markerfacecolor(), face)

    def test_the_axis_names_what_it_measures(self, figure) -> None:
        assert figure.axes[1].get_ylabel() == "uncentred correlation"

    def test_the_zero_line(self, figure) -> None:
        assert set(_by_gid(figure, 1)["zero"].get_ydata()) == {0}


def test_drawing_writes_the_file_it_is_given(figure, out) -> None:
    assert out.is_file()


def test_drawing_reads_only_what_it_is_given(monkeypatch, tmp_path, results, weights) -> None:
    def refuse(*_args, **_kwargs):
        raise AssertionError("the figure read the vintage instead of what it was given")

    for name in ("load_panel", "compute_both", "daily_components", "weight_statistics"):
        monkeypatch.setattr(figures, name, refuse)
    make_pca_factor_momentum_figure(results, weights, out=tmp_path / PCA_FACTOR_MOMENTUM_FIGURE)


def test_the_committed_figure_exists() -> None:
    assert (FIGURES_DIR / PCA_FACTOR_MOMENTUM_FIGURE).is_file()


def test_the_command_reads_the_vintage_once_and_draws(monkeypatch, capsys) -> None:
    calls = []
    monkeypatch.setattr(
        figures, "load_panel", lambda name, field: calls.append(("read", name, field)) or ("m", "c")
    )
    monkeypatch.setattr(figures, "file_returns", lambda closes: f"returns of {closes}")
    monkeypatch.setattr(figures, "compute_both", lambda closes: f"results of {closes}")
    monkeypatch.setattr(figures, "daily_components", lambda r: f"components of {r}")
    monkeypatch.setattr(figures, "weight_statistics", lambda r, d: f"weights of {r}, {d}")
    monkeypatch.setattr(
        figures, "make_pca_factor_momentum_figure", lambda r, w: calls.append(("draw", r, w))
    )
    figures.main()
    assert calls == [
        ("read", SMALL_CAPS, "Close"),
        ("draw", "results of c", "weights of returns of c, components of returns of c"),
    ]
    assert PCA_FACTOR_MOMENTUM_FIGURE in capsys.readouterr().out


def test_a_missing_vintage_reaches_the_operator_as_one_line(monkeypatch) -> None:
    def refuse(*_args, **_kwargs):
        raise VintageUnavailable("no committed vintage is lifted from IJR_20080114.mat")

    monkeypatch.setattr(figures, "load_panel", refuse)
    with pytest.raises(SystemExit, match="no committed vintage is lifted from IJR_20080114.mat"):
        figures.main()


def test_any_other_failure_still_ends_in_a_traceback(monkeypatch) -> None:
    """Only a refusal becomes one line, so a real bug is not hidden."""

    def broken(*_args, **_kwargs):
        raise ValueError("a bug, not a refusal")

    monkeypatch.setattr(figures, "load_panel", broken)
    with pytest.raises(ValueError, match="a bug, not a refusal"):
        figures.main()
