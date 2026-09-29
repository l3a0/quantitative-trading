"""The pins for the three coin-flip figures.

``tests/test_coin_flip_growth.py`` holds what the gamble computes. This file
holds that each figure draws those numbers, so a generator that plotted the
wrong rate or marked the wrong stake fails even when the arithmetic is right.
Some numbers repeat here on purpose, because a figure's own title and labels
are prose, and the suite is the authority for every number prose quotes. No
test compares bytes, for the reason ``tests/test_regime_figure.py`` gives.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from matplotlib.colors import to_rgba

from chan import coin_flip_figures as figures
from chan.coin_flip_figures import (
    DISTRIBUTION_FIGURE,
    FAN_PATHS,
    GOOD,
    HEADS_SHOWN,
    LOST,
    PATHS_FIGURE,
    ROUNDS,
    STAKE_FIGURE,
    final_balances,
    make_distribution_figure,
    make_paths_figure,
    make_stake_figure,
    stake_curve,
)
from chan.coin_flip_growth import BOOK_SEED, _flip_log_returns, gamble_moments
from chan.paths import FIGURES_DIR
from tests.test_regime_figure import png_size


@pytest.fixture(scope="module")
def out_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return tmp_path_factory.mktemp("coin_flip_figures")


@pytest.fixture(scope="module")
def stake(out_dir: Path):
    return make_stake_figure(out=out_dir / STAKE_FIGURE)


@pytest.fixture(scope="module")
def paths(out_dir: Path):
    return make_paths_figure(out=out_dir / PATHS_FIGURE)


@pytest.fixture(scope="module")
def distribution(out_dir: Path):
    return make_distribution_figure(out=out_dir / DISTRIBUTION_FIGURE)


def _texts(ax) -> list[str]:
    return [text.get_text() for text in ax.texts]


class TestTheStakeFigure:
    """Lesson 4: growth against the stake, with three stakes marked."""

    def test_the_curve_is_the_exact_growth_rate(self, stake) -> None:
        curve = stake.curve
        for f, g in zip(curve.stakes[1::40], curve.growth[1::40], strict=True):
            assert g == pytest.approx(gamble_moments(capital=100.0 / f).growth_exact, rel=1e-12)
        assert curve.growth[0] == 0.0
        drawn = max(stake.axes[0].lines, key=lambda line: len(line.get_xdata()))
        assert list(drawn.get_ydata()) == pytest.approx(list(curve.growth), abs=1e-15)

    def test_the_curve_peaks_at_a_twenty_second_and_crosses_zero_at_an_eleventh(self) -> None:
        curve = stake_curve()
        step = curve.stakes[1] - curve.stakes[0]
        assert curve.stakes[np.argmax(curve.growth)] == pytest.approx(1 / 22, abs=step)
        crossing = np.where((curve.growth[:-1] > 0) & (curve.growth[1:] <= 0))[0]
        assert len(crossing) == 1
        assert curve.stakes[crossing[0]] <= 1 / 11 <= curve.stakes[crossing[0] + 1]

    def test_the_curve_gives_both_sides_of_zero_room(self) -> None:
        """The range stops where the loss roughly mirrors the peak, which is
        what keeps the peak from being flattened by a deep tail."""
        curve = stake_curve()
        assert curve.growth.max() == pytest.approx(0.0011351, abs=5e-8)
        assert curve.growth.min() == pytest.approx(-0.0011563, abs=5e-8)

    def test_the_three_marks_sit_on_the_three_stakes(self, stake) -> None:
        marks = [line for line in stake.axes[0].lines if len(line.get_xdata()) == 1]
        points = [(line.get_xdata()[0], line.get_ydata()[0]) for line in marks]
        assert points == [
            pytest.approx((1 / 22, 0.0011351), abs=5e-8),
            pytest.approx((1 / 11, 0.0), abs=5e-12),
            pytest.approx((0.1, -0.00050025), abs=5e-9),
        ]

    def test_each_mark_is_labelled_with_its_own_numbers(self, stake) -> None:
        labels = _texts(stake.axes[0])
        assert labels == [
            "best stake, 1/22\n+0.0011351 per round",
            "break-even, 1/11\ngrowth zero",
            "Chan’s stake, 1/10\n−0.00050025 per round",
        ]
        best = gamble_moments(capital=2200.0).growth_exact
        chan = gamble_moments().growth_exact
        assert f"{best:+.7f}" in labels[0]
        assert f"{chan:+.8f}".replace("-", "−") in labels[2]


class TestThePathsFigure:
    """Lessons 1 and 2: a seeded fan, the ensemble mean and the median path."""

    def test_the_fan_is_the_module_s_own_draws(self, paths) -> None:
        """The figure names its seed and its draw method, so the paths it draws
        have to be the ones those two produce."""
        assert paths.paths.shape == (FAN_PATHS, ROUNDS + 1)
        assert np.all(paths.paths[:, 0] == 1000.0)
        logs = _flip_log_returns(ROUNDS, FAN_PATHS, BOOK_SEED, 110.0, 100.0, 1000.0)
        assert paths.paths[:, -1] == pytest.approx(1000.0 * np.exp(logs.sum(axis=1)), rel=1e-9)
        thin = [line for line in paths.axes[0].lines if line.get_linewidth() == 0.5]
        assert len(thin) == FAN_PATHS

    def test_the_two_lines_end_where_the_post_says(self, paths) -> None:
        assert paths.mean[-1] == pytest.approx(146_576, abs=0.5)
        assert paths.median[-1] == pytest.approx(606, abs=0.5)
        assert paths.median[-1] == pytest.approx(1000.0 * (1.11 * 0.90) ** 500, rel=1e-12)

    def test_the_labels_carry_those_two_balances(self, paths) -> None:
        assert _texts(paths.axes[0]) == ["ensemble mean\n$146,576", "median trader\n$606"]

    def test_the_note_names_the_seed_and_the_draw_method(self, paths) -> None:
        (note,) = [t.get_text() for t in paths.texts if t is not paths._suptitle]
        assert f"seed {BOOK_SEED}" in note
        assert "rng.integers" in note
        assert f"{FAN_PATHS} simulated traders" in note


class TestTheDistributionFigure:
    """Lessons 1 and 5: every reachable balance and its probability."""

    def test_every_head_count_is_a_balance_and_the_probabilities_sum_to_one(self) -> None:
        b = final_balances()
        assert len(b.balance) == ROUNDS + 1
        assert b.probability.sum() == pytest.approx(1.0, abs=1e-12)
        assert b.balance[500] == pytest.approx(606.3789, abs=5e-5)
        assert b.balance[499] == pytest.approx(491.6586, abs=5e-5)

    def test_the_two_shares_in_the_title(self, distribution) -> None:
        """56.3% end below the starting capital and 4.7% reach the ensemble
        mean. The first is every head count up to 502, the second every
        head count from 527."""
        b = distribution.balances
        assert b.share_below_start == pytest.approx(0.5628, abs=5e-5)
        assert b.share_at_or_above_mean == pytest.approx(0.0468, abs=5e-5)
        assert b.balance[502] < 1000.0 < b.balance[503]
        assert b.balance[526] < b.mean <= b.balance[527]
        assert distribution._suptitle.get_text() == (
            "56.3% of traders end below $1,000, and 4.7% reach the ensemble mean"
        )

    def test_the_bars_are_the_probabilities_of_the_head_counts_shown(self, distribution) -> None:
        b = distribution.balances
        low, high = HEADS_SHOWN
        bars = distribution.axes[0].containers[0]
        assert len(bars) == high - low + 1
        heights = [bar.get_height() for bar in bars]
        assert heights == pytest.approx(list(b.probability[low : high + 1]), abs=1e-15)

    def test_nothing_visible_falls_outside_the_range_shown(self) -> None:
        b = final_balances()
        low, high = HEADS_SHOWN
        outside = b.probability[:low].sum() + b.probability[high + 1 :].sum()
        assert outside == pytest.approx(1.3e-4, abs=5e-6)

    def test_red_bars_are_exactly_the_balances_below_the_start(self, distribution) -> None:
        """The note says red bars end below the starting capital, so a red bar
        above it, or a green one below, makes the picture say something the
        numbers do not."""
        b = distribution.balances
        low, _ = HEADS_SHOWN
        bars = distribution.axes[0].containers[0]
        for h, bar in enumerate(bars, low):
            expected = LOST if b.balance[h] < 1000.0 else GOOD
            assert bar.get_facecolor()[:3] == pytest.approx(to_rgba(expected)[:3])

    def test_the_three_lines_are_the_median_the_start_and_the_mean(self, distribution) -> None:
        b = distribution.balances
        verticals = [line.get_xdata()[0] for line in distribution.axes[0].lines]
        assert verticals == pytest.approx([b.median, 1000.0, b.mean], rel=1e-12)
        assert _texts(distribution.axes[0]) == [
            "median trader\n$606",
            "starting capital\n$1,000",
            "ensemble mean\n$146,576",
        ]

    def test_the_inset_shows_the_approximation_between_two_balances(self, distribution) -> None:
        """Lesson 5's claim, drawn: the approximation compounds to a balance
        between the 499-head and 500-head bars, where no head count lands."""
        b = distribution.balances
        inset = distribution.inset
        stems = [collection.get_segments()[0][0][0] for collection in inset.collections]
        assert stems == pytest.approx([491.6586, 606.3789], abs=5e-5)
        dotted = inset.lines[0].get_xdata()[0]
        assert dotted == pytest.approx(b.approximated, rel=1e-12)
        assert b.approximated == pytest.approx(598.9962, abs=5e-5)
        assert stems[0] < dotted < stems[1]
        assert inset.get_xlim()[0] < stems[0] and stems[1] < inset.get_xlim()[1]
        assert _texts(inset) == ["499 heads\n$492", "500 heads\n$606", "$599, the\napproximation"]


class TestTheCommittedImagesAreThoseFigures:
    @pytest.mark.parametrize("name", [STAKE_FIGURE, PATHS_FIGURE, DISTRIBUTION_FIGURE])
    def test_a_fresh_draw_has_the_committed_image_dimensions(
        self, name: str, out_dir: Path, stake, paths, distribution
    ) -> None:
        assert png_size(out_dir / name) == png_size(FIGURES_DIR / name)

    def test_drawing_elsewhere_writes_nothing_where_the_committed_files_live(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Moving the default directory catches a generator that ignores
        ``out``, for the reason ``tests/test_lag_residual_figure.py`` gives."""
        default = tmp_path / "default"
        default.mkdir()
        monkeypatch.setattr(figures, "FIGURES_DIR", default)
        make_stake_figure(out=tmp_path / "a.png")
        make_paths_figure(out=tmp_path / "b.png")
        make_distribution_figure(out=tmp_path / "c.png")
        assert list(default.iterdir()) == []

    def test_the_command_writes_all_three_and_says_where(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(figures, "FIGURES_DIR", tmp_path)
        figures.main()
        out = capsys.readouterr().out
        for name in (STAKE_FIGURE, PATHS_FIGURE, DISTRIBUTION_FIGURE):
            assert f"wrote {tmp_path / name}" in out
            assert (tmp_path / name).is_file()
