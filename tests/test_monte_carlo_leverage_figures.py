"""The pins for the figure in the post on Chapter 8's leverage, Boxes 8.1 to 8.6.

``tests/test_monte_carlo_leverage.py`` holds what the run computes. This file
holds that the figure draws those numbers, so a generator that plotted the
wrong series, marked the wrong optimum or ran the wrong CPPI form fails even
when the arithmetic is right. Some numbers repeat here on purpose, because a
figure's labels are prose and the suite is the authority for every number
prose quotes. No test compares bytes, for the reason
``tests/test_regime_figure.py`` gives.

The figure reads the vintage and the specification that
``tests/test_monte_carlo_leverage.py`` states in its module docstring:
``pythoncodesanddata/AUDCAD_unequal_ret.csv``, vendor chan-py, symbol
AUDCAD-UNEQUAL, basis return, saved 2018-12-26, 612 returns, and
``monteCarloOptimLeverage.m`` as :mod:`chan.monte_carlo_leverage` transcribes
it. It draws the declared seed 20261012 only, and no further seed. Days are
counted from 1 at the first draw. A growth rate is pinned by its seven
printed digits, ``f"{g:.6e}"``, because ``rel=5e-7`` lets the seventh digit
move by two either way. A drawdown or a leverage is pinned at six decimals, as
in that file.

Exploratory, like everything Entry 43 computes here. Every value this file
pins that the run's tests did not already hold was measured by the write-up
after the run.
"""

from __future__ import annotations

import numpy as np
import pytest
from matplotlib.colors import to_rgba

from chan import monte_carlo_leverage_figures as module
from chan.aud_cad_johansen import SCRIPT_KELLY
from chan.khandani_lo_book_two import matches
from chan.monte_carlo_leverage import (
    CAP,
    SEED,
    D,
    account_drawdowns,
    cppi_as_described,
    cppi_as_scripted,
    draws,
    growth,
    implied_kelly_band,
    max_drawdown,
    pearson_fit,
    read_returns,
    ruin_leverage,
    simulate,
)
from chan.monte_carlo_leverage_figures import (
    BLOCK,
    CURVE_POINTS,
    FIGURE,
    FLOOR,
    LEVERAGE_MAX,
    block_minima,
    days_below,
    deepest_day,
    first_below,
    growth_curve,
    main,
    make_monte_carlo_leverage_figure,
    signed,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.vintage import VintageUnavailable
from tests.test_regime_figure import png_size

SPEC = (
    "pythoncodesanddata/AUDCAD_unequal_ret.csv chan-py AUDCAD-UNEQUAL return saved "
    "2018-12-26, 612 returns; monteCarloOptimLeverage.m as chan.monte_carlo_leverage "
    "transcribes it, on the declared seed 20261012"
)


@pytest.fixture(scope="module")
def saved():
    return read_returns()


@pytest.fixture(scope="module")
def returns(saved):
    return saved[1]


@pytest.fixture(scope="module")
def sim(returns):
    return draws(pearson_fit(returns)[1], SEED)


@pytest.fixture(scope="module")
def declared(returns):
    """The run's own pass over the declared seed, which the figure must agree with."""
    return simulate(pearson_fit(returns)[1], SEED)


@pytest.fixture(scope="module")
def accounts(sim, declared):
    """Each account's drawdown on every day, at the declared seed's capped optimum."""
    f = declared.optimum
    return {
        "scripted": account_drawdowns(cppi_as_scripted(sim, f)),
        "described": account_drawdowns(cppi_as_described(sim, f)),
        "full": account_drawdowns(f * D * sim),
    }


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("monte_carlo_leverage_figure") / FIGURE


@pytest.fixture(scope="module")
def figure(out, saved):
    return make_monte_carlo_leverage_figure(out=out, saved=saved)


@pytest.fixture(scope="module")
def axes(figure):
    growth_ax, cppi_ax = figure.axes
    return {"growth": growth_ax, "cppi": cppi_ax}


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _point(ax, gid: str) -> tuple[float, float]:
    marker = _by_gid(ax.lines)[gid]
    (x,), (y,) = marker.get_xdata(), marker.get_ydata()
    return float(x), float(y)


def _stairs(ax, gid: str):
    return _by_gid(ax.patches)[gid]


def _steps(ax, gid: str) -> tuple[np.ndarray, np.ndarray]:
    """A step line's values and its edges."""
    data = _stairs(ax, gid).get_data()
    return data.values, data.edges


def _legend(ax) -> list[str]:
    return [t.get_text() for t in ax.get_legend().get_texts()]


class TestTheFigure:
    def test_there_are_two_panels(self, figure) -> None:
        assert len(figure.axes) == 2

    def test_the_title_carries_the_label_and_the_note_names_the_vintage_and_seed(
        self, figure
    ) -> None:
        assert figure._suptitle.get_text() == (
            "Exploratory: Chapter 8's leverage on Example 5.1's returns, one declared seed"
        )
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Algorithmic Trading, Kindle edition, Figure 8.2 and pp. 258 to 265. Returns from "
            "pythoncodesanddata/AUDCAD_unequal_ret.csv, saved 2018-12-26.\nDraws: 100,000 "
            "from the Pearson type IV with the returns' four moments, on seed 20261012. No "
            "further seed is drawn here."
        ]

    def test_drawing_with_nothing_handed_in_reads_the_committed_vintage(
        self, tmp_path, sim
    ) -> None:
        """``main`` and the committed PNG take this path, so it is drawn here too."""
        drawn = make_monte_carlo_leverage_figure(out=tmp_path / FIGURE)
        line = _by_gid(drawn.axes[0].lines)["draws"]
        np.testing.assert_array_equal(line.get_ydata(), growth_curve(sim, ruin_leverage(sim))[1])

    def test_drawing_uses_the_returns_it_is_handed(self, tmp_path, saved) -> None:
        """Halved returns are not the committed vintage, so a draw that re-read it fails here."""
        entry, returns = saved
        halved = returns * 0.5
        drawn = make_monte_carlo_leverage_figure(out=tmp_path / FIGURE, saved=(entry, halved))
        line = _by_gid(drawn.axes[0].lines)["saved"]
        np.testing.assert_array_equal(line.get_ydata(), growth_curve(halved, LEVERAGE_MAX)[1])


class TestTheGrowthPanel:
    """Figure 8.2 redrawn, on the declared seed's draws and on the 612 saved returns."""

    def test_the_draws_curve_is_their_growth_rate_up_to_their_ruin_leverage(
        self, axes, sim, declared
    ) -> None:
        line = _by_gid(axes["growth"].lines)["draws"]
        x, y = line.get_xdata(), line.get_ydata()
        assert len(x) == CURVE_POINTS == 541
        assert x[0] == 0.0 and x[-1] < declared.ruin
        assert x[-1] == pytest.approx(declared.ruin * (1 - 1 / CURVE_POINTS), rel=1e-12)
        np.testing.assert_allclose(y, [np.mean(np.log1p(f * sim)) for f in x], rtol=1e-12)

    def test_the_curve_stops_at_the_ruin_leverage_and_a_line_marks_it(self, axes, declared) -> None:
        ruin = _by_gid(axes["growth"].lines)["ruin"]
        assert list(ruin.get_xdata()) == [declared.ruin] * 2
        assert declared.ruin == pytest.approx(23.217362, abs=5e-7), SPEC
        assert ruin.get_linestyle() == ":"

    def test_the_saved_returns_curve_runs_to_27(self, axes, returns) -> None:
        line = _by_gid(axes["growth"].lines)["saved"]
        x, y = line.get_xdata(), line.get_ydata()
        assert (len(x), x[0]) == (CURVE_POINTS, 0.0)
        assert x[-1] == pytest.approx(LEVERAGE_MAX * (1 - 1 / CURVE_POINTS), rel=1e-12)
        np.testing.assert_allclose(y, [np.mean(np.log1p(f * returns)) for f in x], rtol=1e-12)
        assert axes["growth"].get_xlim() == (0.0, LEVERAGE_MAX)

    def test_the_draws_are_ink_and_the_saved_returns_muted(self, axes) -> None:
        lines = _by_gid(axes["growth"].lines)
        assert lines["draws"].get_color() == INK and lines["saved"].get_color() == MUTED
        assert lines["draws"].get_zorder() > lines["saved"].get_zorder()

    def test_the_draws_uncapped_optimum(self, axes, declared) -> None:
        f, g = _point(axes["growth"], "uncapped")
        assert f == declared.uncapped
        assert f == pytest.approx(22.295382, abs=1e-6), SPEC
        assert f"{g:.6e}" == "4.801065e-03", SPEC

    def test_the_script_s_answer_sits_on_the_cap(self, axes, declared, sim) -> None:
        f, g = _point(axes["growth"], "capped")
        assert f == declared.optimum
        assert f == pytest.approx(CAP, abs=1e-6)
        assert f"{g:.6e}" == "4.735998e-03", SPEC
        assert g == pytest.approx(growth(CAP, sim), rel=1e-8)
        cap = _by_gid(axes["growth"].lines)["cap"]
        assert list(cap.get_xdata()) == [CAP] * 2 and cap.get_linestyle() == "--"

    def test_the_saved_returns_optimum_and_kelly(self, axes, returns) -> None:
        f, g = _point(axes["growth"], "historical")
        assert f == pytest.approx(23.721773, abs=1e-6), SPEC
        assert f"{g:.6e}" == "5.197618e-03", SPEC
        kelly, at_kelly = _point(axes["growth"], "kelly")
        assert kelly == pytest.approx(23.845328, abs=5e-7), SPEC
        assert matches(kelly, SCRIPT_KELLY)
        assert f"{at_kelly:.6e}" == "5.197464e-03", SPEC
        assert 0 < g - at_kelly < 2e-7

    def test_the_markers_are_accent_on_the_draws_and_muted_on_the_saved_returns(self, axes) -> None:
        lines = _by_gid(axes["growth"].lines)
        assert {g: lines[g].get_color() for g in ("uncapped", "capped", "historical", "kelly")} == {
            "uncapped": ACCENT,
            "capped": ACCENT,
            "historical": MUTED,
            "kelly": MUTED,
        }

    def test_the_shaded_span_is_the_implied_kelly_band(self, axes) -> None:
        (span,) = [p for p in axes["growth"].patches if p.get_gid() == "kelly-band"]
        low, high = implied_kelly_band()
        assert span.get_x() == low
        assert span.get_x() + span.get_width() == pytest.approx(high, rel=1e-14)
        assert (low, high) == pytest.approx((21.558894, 26.757652), abs=5e-7)
        assert span.get_facecolor() == to_rgba(*module.KELLY_BAND_SHADE)

    def test_the_kelly_band_is_a_faint_accent(self, axes) -> None:
        """The shade is pinned as a literal, so a change to the constant fails here."""
        (span,) = [p for p in axes["growth"].patches if p.get_gid() == "kelly-band"]
        assert span.get_facecolor() == to_rgba(ACCENT, 0.14)

    def test_the_book_s_figures_stand_on_the_axis(self, axes) -> None:
        lines = _by_gid(axes["growth"].lines)
        assert {
            g: lines[g].get_xdata()[0] for g in ("book-kelly", "book-fminbnd", "book-optimum")
        } == {
            "book-kelly": 18.4,
            "book-fminbnd": 19.0,
            "book-optimum": 19.2,
        }
        assert all(
            lines[g].get_color() == LOST for g in ("book-kelly", "book-fminbnd", "book-optimum")
        )
        texts = _by_gid(axes["growth"].texts)
        assert texts["book-kelly-label"].get_text() == (
            "18.4, the book's Kelly\nand historical optimum"
        )
        assert texts["book-optimum-label"].get_text() == (
            "19 and 19.2,\nthe book's simulated optimum"
        )

    def test_the_book_s_ticks_reach_0_16_of_the_panel_height(self, axes) -> None:
        """Heights are in axes coordinates, a share of the panel's height."""
        lines = _by_gid(axes["growth"].lines)
        for gid in ("book-kelly", "book-fminbnd", "book-optimum"):
            assert list(lines[gid].get_ydata()) == [0.0, 0.16], gid

    def test_the_cap_and_ruin_lines_stop_below_the_legend(self, axes) -> None:
        """Heights are in axes coordinates, a share of the panel's height."""
        lines = _by_gid(axes["growth"].lines)
        for gid in ("cap", "ruin"):
            assert list(lines[gid].get_ydata()) == [0.0, 0.8], gid

    def test_the_legend_names_each_series_and_mark(self, axes) -> None:
        assert _legend(axes["growth"]) == [
            "the Kelly range Example 5.1's printed figures allow, 21.558894 to 26.757652",
            "Chan's 612 saved returns",
            "100,000 draws on seed 20261012, ending at their ruin leverage of 23.217362",
            "the script's cap, fminbnd(minusGsim, 0, 20)",
            "the script's answer on the draws, 20.000000, growth 0.004736",
            "the draws' optimum without the cap, 22.295382, growth 0.004801",
            "the saved returns' optimum, 23.721773, growth 0.005198",
            "the saved returns' Kelly, 23.845328, growth 0.005197",
        ], SPEC

    def test_both_curves_fit_inside_the_panel(self, axes) -> None:
        low, high = axes["growth"].get_ylim()
        for gid in ("draws", "saved"):
            y = _by_gid(axes["growth"].lines)[gid].get_ydata()
            assert low <= y.min() and y.max() <= high

    def test_the_heading(self, axes) -> None:
        assert axes["growth"].get_title(loc="left") == (
            "Figure 8.2 redrawn: the growth rate g(f), the mean of log(1 + f·R), against the "
            "leverage f.\nThe book prints 18.4 for the Kelly and for the historical optimum. "
            "The saved returns give neither."
        )

    def test_growth_curve_leaves_out_its_upper_end(self) -> None:
        x, y = growth_curve(np.array([0.1, -0.05] * 5), 20.0)
        assert x[-1] < 20.0 and len(x) == CURVE_POINTS
        assert y[0] == 0.0


class TestTheCppiPanel:
    """Box 8.6's loop, location 3426's scheme and the full account at f·D, on the same draws."""

    @pytest.mark.parametrize("gid", ["scripted", "described", "full"])
    def test_each_step_is_the_deepest_drawdown_in_its_1000_days(self, axes, accounts, gid) -> None:
        values, edges = _steps(axes["cppi"], gid)
        np.testing.assert_array_equal(edges, np.arange(0, 100_001, BLOCK))
        np.testing.assert_array_equal(values, accounts[gid].reshape(-1, BLOCK).min(axis=1))

    @pytest.mark.parametrize(
        ("gid", "name"),
        [
            ("scripted", "cppi_drawdown"),
            ("described", "described_drawdown"),
            ("full", "full_drawdown"),
        ],
    )
    def test_each_deepest_step_is_the_run_s_drawdown(self, axes, declared, gid, name) -> None:
        values, _ = _steps(axes["cppi"], gid)
        assert values.min() == getattr(declared, name)

    def test_the_loop_s_deepest_drawdown_and_its_days_below_the_floor(self, axes, accounts) -> None:
        day, value = _point(axes["cppi"], "scripted-deepest")
        assert (day, f"{value:.6f}") == (37_071, "-0.848088"), SPEC
        assert first_below(accounts["scripted"]) == 303
        assert days_below(accounts["scripted"]) == 5_681

    def test_the_scheme_s_deepest_drawdown_and_it_never_falls_below(self, axes, accounts) -> None:
        day, value = _point(axes["cppi"], "described-deepest")
        assert (day, f"{value:.6f}") == (33_785, "-0.495638"), SPEC
        assert first_below(accounts["described"]) is None
        assert accounts["described"].min() > FLOOR

    def test_the_full_account_s_deepest_drawdown_and_its_days_below_the_floor(
        self, axes, accounts
    ) -> None:
        day, value = _point(axes["cppi"], "full-deepest")
        assert (day, f"{value:.6f}") == (37_071, "-0.871216"), SPEC
        assert first_below(accounts["full"]) == 303
        assert days_below(accounts["full"]) == 6_034

    @pytest.mark.parametrize("gid", ["scripted", "described", "full"])
    def test_each_deepest_marker_sits_on_its_step(self, axes, gid) -> None:
        day, value = _point(axes["cppi"], f"{gid}-deepest")
        values, edges = _steps(axes["cppi"], gid)
        step = int(np.searchsorted(edges, day - 1, side="right")) - 1
        assert values[step] == value

    def test_the_legend_names_each_form_s_deepest_day_and_days_below(self, axes) -> None:
        assert _legend(axes["cppi"]) == [
            "the full account at f·D = 10.000000: deepest −0.871216 on day 37,071, below "
            "−0.5 on 6,034 days from day 303",
            "Box 8.6's loop: deepest −0.848088 on day 37,071, below −0.5 on 5,681 days from "
            "day 303",
            "the scheme on p. 263: deepest −0.495638 on day 33,785, never below −0.5",
        ], SPEC

    def test_the_loop_is_red_the_scheme_green_and_the_full_account_muted(self, axes) -> None:
        colors = {
            g: _stairs(axes["cppi"], g).get_edgecolor() for g in ("scripted", "described", "full")
        }
        assert colors == {
            "scripted": to_rgba(LOST),
            "described": to_rgba(GOOD),
            "full": to_rgba(MUTED),
        }

    def test_a_dashed_line_marks_the_floor(self, axes) -> None:
        floor = _by_gid(axes["cppi"].lines)["floor"]
        assert list(floor.get_ydata()) == [-0.5, -0.5] and floor.get_linestyle() == "--"

    def test_the_panel_spans_every_draw(self, axes) -> None:
        assert axes["cppi"].get_xlim() == (0.0, 100_000.0)

    def test_every_step_fits_inside_the_panel(self, axes) -> None:
        low, high = axes["cppi"].get_ylim()
        for gid in ("scripted", "described", "full"):
            values, _ = _steps(axes["cppi"], gid)
            assert low <= values.min() and values.max() <= high

    def test_the_heading(self, axes) -> None:
        assert axes["cppi"].get_title(loc="left") == (
            "Two CPPI forms on the same draws, at the script's f of 20.000000 and D = 0.5.\n"
            "Chan says on p. 264 that CPPI's drawdown is less than 0.5 by design. The dashed line "
            "is "
            "−0.5."
        )

    def test_the_helpers_on_a_path_worked_by_hand(self) -> None:
        drawdowns = np.array([0.0, -0.1, -0.6, -0.2, -0.7, -0.7])
        assert first_below(drawdowns) == 3
        assert deepest_day(drawdowns) == 5
        assert first_below(np.array([0.0, -0.4])) is None
        assert days_below(drawdowns) == 3
        assert days_below(np.array([0.0, -0.5, -0.5])) == 0
        assert first_below(np.array([0.0, -0.5, -0.51])) == 3
        np.testing.assert_array_equal(block_minima(drawdowns, 2), [-0.1, -0.6, -0.7])

    def test_the_account_drawdowns_reach_max_drawdown(self, accounts, sim, declared) -> None:
        f = declared.optimum
        assert accounts["scripted"].min() == max_drawdown(cppi_as_scripted(sim, f))

    def test_signed_prints_a_true_minus_sign(self) -> None:
        assert signed(-0.848088) == "−0.848088"
        assert signed(-0.5, 1) == "−0.5"


class TestTheFile:
    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.exists() and out.stat().st_size > 0

    def test_the_committed_figure_exists(self) -> None:
        assert (FIGURES_DIR / FIGURE).is_file()

    def test_a_fresh_draw_has_the_committed_image_dimensions(self, figure, out) -> None:
        assert png_size(out) == png_size(FIGURES_DIR / FIGURE)

    def test_drawing_to_out_leaves_the_committed_figure_alone(self, tmp_path, saved) -> None:
        committed = FIGURES_DIR / FIGURE
        before = committed.read_bytes()
        touched = committed.stat().st_mtime_ns
        make_monte_carlo_leverage_figure(out=tmp_path / FIGURE, saved=saved)
        assert committed.read_bytes() == before
        # A redraw is deterministic, so a stray write would leave the bytes
        # the same. Only the modification time shows it.
        assert committed.stat().st_mtime_ns == touched

    def test_main_lets_any_other_error_through_as_itself(self, monkeypatch) -> None:
        def fail(*_a, **_k):
            raise ValueError("a bug, not a refusal")

        monkeypatch.setattr(module, "make_monte_carlo_leverage_figure", fail)
        with pytest.raises(ValueError, match="a bug, not a refusal"):
            main()

    def test_a_missing_vintage_reaches_the_operator_as_one_line(
        self, monkeypatch, tmp_path
    ) -> None:
        """No mock: the real read, pointed at an empty directory, refuses the saved returns."""
        from chan import paths

        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert isinstance(stopped.value.__cause__, VintageUnavailable)
        assert "\n" not in str(stopped.value)

    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch) -> None:
        refusal = VintageUnavailable("no committed vintage holds AUDCAD-UNEQUAL")

        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(module, "make_monte_carlo_leverage_figure", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)

    def test_main_reports_the_file_it_wrote(self, monkeypatch, capsys) -> None:
        monkeypatch.setattr(module, "make_monte_carlo_leverage_figure", lambda: None)
        main()
        assert capsys.readouterr().out == f"wrote {FIGURES_DIR / FIGURE}\n"
