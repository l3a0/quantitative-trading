"""The pins for the ADF residual figure.

Two layers, for the reason ``tests/test_regime_figure.py`` gives. The first
holds what :func:`chan.lag_residual_figure.residual_check` computes, which is
the finding. The second holds that the picture draws those numbers, so a
generator that quietly plotted the wrong series fails even when the engine is
right. Neither compares bytes, because a PNG carries the matplotlib version
that rendered it.

Vintage: ``gld_20yr_prices_unadjusted.csv`` and
``gdx_20yr_prices_unadjusted.csv``, yfinance raw closes, both downloaded
2026-08-27. Specification: the with-intercept residual spread over 2006-05-23
to 2007-05-23, which is row 4 of ``docs/replication-log.md``, tested by
``adfuller`` at a fixed lag count with ``regression='n'``. Each fit's residuals
are read at lags 1 to 10, against a white-noise band of ``±1.96/√n`` and by a
Breusch-Godfrey test over the same ten lags. First run on 2026-09-26.

The result is exploratory, and the docstring of the module under test says why.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from ithildincore.timeseries import EG_CRIT_N2, adf_tstat

from chan.lag_residual_figure import (
    FIGURE_NAME,
    LAG_COUNTS,
    LOST,
    RESIDUAL_LAGS,
    make_lag_residual_figure,
    residual_check,
)
from chan.pair_cointegration import BOOK_START, BOOK_TRAIN_END, engle_granger
from chan.paths import FIGURES_DIR
from chan.series import aligned_closes
from tests.test_regime_figure import png_size

COMMITTED = FIGURES_DIR / FIGURE_NAME

#: Per lag count: observations, ADF statistic, Breusch-Godfrey p, and the
#: residual lags that fall outside the band.
PINNED = {
    0: (251, -3.2018, 0.1193, [6]),
    1: (250, -3.0875, 0.0421, [6]),
    2: (249, -2.6402, 0.0714, [3, 6]),
    3: (248, -2.4067, 0.0043, [6]),
    6: (245, -2.2979, 0.8395, []),
}


@pytest.fixture(scope="module")
def spread() -> np.ndarray:
    df = aligned_closes("GLD", "GDX", start=BOOK_START, end=BOOK_TRAIN_END, unadjusted=True)
    return engle_granger(df["GLD"].to_numpy(float), df["GDX"].to_numpy(float)).spread


@pytest.fixture(scope="module")
def drawn(tmp_path_factory: pytest.TempPathFactory) -> tuple[object, Path]:
    """Run the real drawing code, writing somewhere that is not the repo."""
    out = tmp_path_factory.mktemp("figure") / FIGURE_NAME
    return make_lag_residual_figure(out=out), out


class TestWhatEachLagCountLeavesBehind:
    @pytest.mark.parametrize("lags", LAG_COUNTS)
    def test_the_fit_and_its_residuals(self, spread: np.ndarray, lags: int) -> None:
        nobs, stat, bg_p, outside = PINNED[lags]
        check = residual_check(spread, lags)

        assert check.nobs == nobs
        assert check.adf_stat == pytest.approx(stat, abs=5e-5)
        assert check.breusch_godfrey_p == pytest.approx(bg_p, abs=5e-5)
        assert check.outside == outside
        assert len(check.autocorrelation) == RESIDUAL_LAGS

    @pytest.mark.parametrize("lags", LAG_COUNTS)
    def test_the_statistic_is_the_one_the_replication_computes(
        self, spread: np.ndarray, lags: int
    ) -> None:
        """The figure reaches the ADF through ``statsmodels`` because it needs
        the fitted regression, and the replication reaches it through
        ``ithildincore``. They have to be the same test, or the figure checks
        the residuals of a fit nobody reported."""
        stat, _nobs = adf_tstat(spread, lags=lags, constant=False)
        assert residual_check(spread, lags).adf_stat == pytest.approx(stat, abs=1e-10)

    def test_the_spike_is_at_lag_six_until_six_lags_absorb_it(self, spread: np.ndarray) -> None:
        at_six = [float(residual_check(spread, k).autocorrelation[5]) for k in LAG_COUNTS]
        assert at_six == pytest.approx([0.1631, 0.1668, 0.1764, 0.1546, 0.0100], abs=5e-5)

    def test_two_lags_also_leave_a_spike_at_lag_three(self, spread: np.ndarray) -> None:
        assert residual_check(spread, 2).autocorrelation[2] == pytest.approx(-0.1331, abs=5e-5)

    def test_the_books_lag_count_fails_the_residual_check(self, spread: np.ndarray) -> None:
        """One lag is the count behind Chan's better-than-90% verdict, and its
        residuals fail Breusch-Godfrey at 10% while the ADF rejects."""
        check = residual_check(spread, 1)
        assert check.adf_stat < EG_CRIT_N2["10%"]
        assert check.breusch_godfrey_p < 0.10

    def test_six_is_the_first_lag_count_whose_residuals_pass(self, spread: np.ndarray) -> None:
        """Passing means both checks: Breusch-Godfrey clears 10% and no
        autocorrelation leaves the band. Zero lags clears the first and not the
        second, which is why both are asked. Four and five are not drawn, and
        this is what says the figure skipped nothing that passes."""

        def passes(k: int) -> bool:
            check = residual_check(spread, k)
            return check.breusch_godfrey_p > 0.10 and not check.outside

        assert [passes(k) for k in range(7)] == [False] * 6 + [True]
        assert residual_check(spread, 6).adf_stat > EG_CRIT_N2["10%"]


class TestTheFigureDrawsThoseChecks:
    def test_one_panel_per_lag_count(self, drawn) -> None:
        fig, _ = drawn
        assert len(fig.axes) == len(LAG_COUNTS)
        assert [check.lags for check in fig.checks] == list(LAG_COUNTS)

    def test_the_bars_are_the_residual_autocorrelations(self, drawn, spread: np.ndarray) -> None:
        fig, _ = drawn
        for ax, lags in zip(fig.axes, LAG_COUNTS, strict=True):
            heights = [bar.get_height() for bar in ax.containers[0]]
            expected = residual_check(spread, lags).autocorrelation
            assert heights == pytest.approx(list(expected), abs=1e-12)

    def test_the_bars_outside_the_band_and_only_those_are_red(self, drawn) -> None:
        """The footer says red bars fall outside the band, so a red bar inside
        it, or a bar outside it drawn grey, makes the picture say something the
        numbers do not."""
        from matplotlib.colors import to_rgba

        fig, _ = drawn
        for ax, lags in zip(fig.axes, LAG_COUNTS, strict=True):
            red = [
                lag
                for lag, bar in enumerate(ax.containers[0], 1)
                if bar.get_facecolor() == to_rgba(LOST)
            ]
            assert red == PINNED[lags][3]

    def test_the_band_is_the_one_the_checks_use(self, drawn) -> None:
        fig, _ = drawn
        for ax, check in zip(fig.axes, fig.checks, strict=True):
            band = ax.patches[0]
            assert band.get_y() == pytest.approx(-check.band)
            assert band.get_height() == pytest.approx(2 * check.band)

    def test_each_title_carries_its_statistic_and_p_value(self, drawn) -> None:
        fig, _ = drawn
        titles = [ax.get_title(loc="left") for ax in fig.axes]

        assert "ADF t −3.09, rejects at 10%" in titles[1]
        assert "Breusch-Godfrey p = 0.042" in titles[1]
        assert "ADF t −2.30, does not reject" in titles[4]
        assert "Breusch-Godfrey p = 0.840" in titles[4]


class TestTheFigureNamesWhatItDrewFrom:
    def test_the_figure_carries_the_two_entries_it_resolved(self, drawn) -> None:
        fig, _ = drawn
        assert [entry.path for entry in fig.vintages] == [
            "gld_20yr_prices_unadjusted.csv",
            "gdx_20yr_prices_unadjusted.csv",
        ]

    def test_the_command_prints_a_vintage_line_for_each_leg(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        from chan import lag_residual_figure

        monkeypatch.setattr(lag_residual_figure, "FIGURES_DIR", tmp_path)
        lag_residual_figure.main()
        out = capsys.readouterr().out

        assert (
            "GLD vintage: gld_20yr_prices_unadjusted.csv   yfinance raw, downloaded 2026-08-27"
            in out
        )
        assert (
            "GDX vintage: gdx_20yr_prices_unadjusted.csv   yfinance raw, downloaded 2026-08-27"
            in out
        )
        assert (tmp_path / FIGURE_NAME).is_file()


class TestTheCommittedImageIsThatFigure:
    def test_a_fresh_draw_has_the_committed_image_dimensions(self, drawn) -> None:
        _, out = drawn
        assert png_size(out) == png_size(COMMITTED)

    def test_drawing_elsewhere_writes_nothing_where_the_committed_file_lives(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Hashing the committed file around a draw cannot catch a generator
        that ignores ``out``, because the draw already happened in a fixture.
        Moving the default directory can: anything written there is a write
        that would have landed on the committed image."""
        from chan import lag_residual_figure

        default = tmp_path / "default"
        default.mkdir()
        monkeypatch.setattr(lag_residual_figure, "FIGURES_DIR", default)
        out = tmp_path / "elsewhere.png"
        make_lag_residual_figure(out=out)

        assert out.is_file()
        assert list(default.iterdir()) == []
