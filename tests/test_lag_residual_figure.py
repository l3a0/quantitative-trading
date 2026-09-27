"""The pins for the ADF residual figure.

``TestResidualCheck`` in ``tests/test_pair_cointegration.py`` holds what the
residual check computes, and it names the vintage and the specification. This
file holds that the figure draws those numbers, so a generator that quietly
plotted the wrong fit fails even when the check is right. Some numbers repeat
here on purpose, for the reason ``tests/test_regime_figure.py`` gives. Neither
file compares bytes, because a PNG carries the matplotlib version that
rendered it.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from chan.lag_residual_figure import (
    FIGURE_NAME,
    LAG_COUNTS,
    LOST,
    _signed,
    make_lag_residual_figure,
)
from chan.pair_cointegration import BOOK_START, BOOK_TRAIN_END, engle_granger, residual_check
from chan.paths import FIGURES_DIR
from chan.series import aligned_closes
from tests.test_regime_figure import png_size

COMMITTED = FIGURES_DIR / FIGURE_NAME

#: The residual lags outside the band in each panel, repeated from
#: ``TestResidualCheck`` so this file says what the picture shows.
OUTSIDE = {0: [6], 1: [6], 2: [3, 6], 3: [6], 6: []}


@pytest.fixture(scope="module")
def spread() -> np.ndarray:
    df = aligned_closes("GLD", "GDX", start=BOOK_START, end=BOOK_TRAIN_END, unadjusted=True)
    return engle_granger(df["GLD"].to_numpy(float), df["GDX"].to_numpy(float)).spread


@pytest.fixture(scope="module")
def drawn(tmp_path_factory: pytest.TempPathFactory) -> tuple[object, Path]:
    """Run the real drawing code, writing somewhere that is not the repo."""
    out = tmp_path_factory.mktemp("figure") / FIGURE_NAME
    return make_lag_residual_figure(out=out), out


def red_lags(ax) -> list[int]:
    from matplotlib.colors import to_rgba

    return [
        lag for lag, bar in enumerate(ax.containers[0], 1) if bar.get_facecolor() == to_rgba(LOST)
    ]


class TestTheFigureDrawsTheCheck:
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

    def test_every_bar_fits_inside_its_panel(self, drawn) -> None:
        """A y-range that clips the lag-6 bar hides the one thing the figure
        is for, and every other assertion here reads the artists rather than
        the pixels, so none of them would notice."""
        fig, _ = drawn
        for ax in fig.axes:
            low, high = ax.get_ylim()
            assert all(low < bar.get_height() < high for bar in ax.containers[0])

    def test_the_bars_outside_the_band_and_only_those_are_red(self, drawn) -> None:
        """The footer says red bars fall outside the band, so a red bar inside
        it, or a bar outside it drawn in grey, makes the picture say something
        the numbers do not."""
        fig, _ = drawn
        for ax, lags in zip(fig.axes, LAG_COUNTS, strict=True):
            assert red_lags(ax) == OUTSIDE[lags]

    def test_each_red_bar_carries_its_own_value(self, drawn) -> None:
        fig, _ = drawn
        for ax, check in zip(fig.axes, fig.checks, strict=True):
            printed = [text.get_text() for text in ax.texts]
            expected = [_signed(check.autocorrelation[lag - 1], 2) for lag in check.outside]
            assert printed == expected
        assert [t.get_text() for t in fig.axes[2].texts] == ["−0.13", "+0.18"]

    def test_the_band_is_the_one_the_check_uses(self, drawn) -> None:
        fig, _ = drawn
        for ax, check in zip(fig.axes, fig.checks, strict=True):
            band = ax.patches[0]
            assert band.get_y() == pytest.approx(-check.band)
            assert band.get_height() == pytest.approx(2 * check.band)

    def test_each_title_carries_its_lag_count_statistic_and_p_value(self, drawn) -> None:
        fig, _ = drawn
        titles = [ax.get_title(loc="left") for ax in fig.axes]

        assert titles[1].startswith("1 lag\n")
        assert titles[4].startswith("6 lags\n")
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

    def test_the_command_names_its_vintages_and_where_it_wrote(
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
        assert f"wrote {tmp_path / FIGURE_NAME}" in out
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
