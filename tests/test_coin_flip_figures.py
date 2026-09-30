"""The pins for the five coin-flip figures.

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
    ACCENT,
    DISTRIBUTION_FIGURE,
    ESTIMATOR_FIGURE,
    ESTIMATOR_RUN,
    FAN_PATHS,
    GOOD,
    HEADS_SHOWN,
    LOST,
    MAX_STAKE,
    MUTED,
    PATHS_FIGURE,
    PER_TOSS_BAND,
    ROUNDS,
    RUN_SIZES,
    SIGN_FIGURE,
    SIGN_SEEDS,
    STAKE_FIGURE,
    _dollars,
    _signed_rate,
    ensemble_estimates,
    final_balances,
    make_distribution_figure,
    make_estimator_figure,
    make_paths_figure,
    make_sign_figure,
    make_stake_figure,
    stake_curve,
)
from chan.coin_flip_growth import BOOK_SEED, _flip_log_returns, gamble_moments, simulate
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


@pytest.fixture(scope="module")
def sign(out_dir: Path):
    return make_sign_figure(out=out_dir / SIGN_FIGURE)


@pytest.fixture(scope="module")
def estimator(out_dir: Path):
    return make_estimator_figure(out=out_dir / ESTIMATOR_FIGURE)


def _texts(ax) -> list[str]:
    return [text.get_text() for text in ax.texts]


def _rgb(colour) -> tuple[float, float, float]:
    return tuple(to_rgba(colour)[:3])


def _thick(ax) -> list:
    """The lines a reader is meant to follow, as opposed to the fan or a rule."""
    return [line for line in ax.lines if line.get_linewidth() > 2 and len(line.get_xdata()) > 2]


class TestTheStakeFigure:
    """Lesson 4: growth against the stake, with three stakes marked."""

    def test_the_curve_is_the_exact_growth_rate(self, stake) -> None:
        curve = stake.curve
        for f, g in zip(curve.stakes[1::40], curve.growth[1::40], strict=True):
            assert g == pytest.approx(gamble_moments(capital=100.0 / f).growth_exact, rel=1e-12)
        assert curve.growth[0] == 0.0
        drawn = max(stake.axes[0].lines, key=lambda line: len(line.get_xdata()))
        assert list(drawn.get_ydata()) == pytest.approx(list(curve.growth), abs=1e-15)
        assert list(drawn.get_xdata()) == pytest.approx(list(curve.stakes), abs=1e-15)

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

    def test_the_title_states_the_finding(self, stake) -> None:
        assert stake._suptitle.get_text() == (
            "Chan’s stake of 1/10 shrinks capital, and a stake of 1/22 grows it fastest"
        )

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

    def test_the_marks_and_fills_wear_the_colours_the_note_names(self, stake) -> None:
        """The note says green where capital grows and red where it shrinks,
        so a swapped fill or a swapped mark says the opposite."""
        ax = stake.axes[0]
        marks = [line for line in ax.lines if len(line.get_xdata()) == 1]
        assert [_rgb(line.get_color()) for line in marks] == [_rgb(GOOD), _rgb(MUTED), _rgb(LOST)]
        fills = ax.collections
        assert [_rgb(fill.get_facecolor()[0]) for fill in fills] == [_rgb(GOOD), _rgb(LOST)]
        grows = fills[0].get_paths()[0].vertices
        shrinks = fills[1].get_paths()[0].vertices
        assert grows[:, 1].min() >= -1e-12 and grows[:, 0].max() <= 1 / 11 + 1e-3
        assert shrinks[:, 1].max() <= 1e-12 and shrinks[:, 0].min() >= 1 / 11 - 1e-3

    def test_the_axes_show_the_whole_curve_and_the_zero_line(self, stake) -> None:
        ax = stake.axes[0]
        assert ax.get_xlim() == pytest.approx((0.0, MAX_STAKE))
        low, high = ax.get_ylim()
        assert low < stake.curve.growth.min() and stake.curve.growth.max() < high
        (zero,) = [line for line in ax.lines if list(line.get_ydata()) == [0, 0]]
        assert zero is not None

    def test_the_tick_labels_use_a_typographic_minus_and_a_bare_zero(self) -> None:
        assert _signed_rate(-0.0005) == "−0.0005"
        assert _signed_rate(0.001) == "+0.0010"
        assert _signed_rate(0.0) == "0"
        assert [_dollars(v) for v in (146_576, 1.0, 0.5, 0.002)] == [
            "$146,576",
            "$1",
            "$0.50",
            "$2e-03",
        ]


class TestThePathsFigure:
    """Lesson 2: a seeded fan, the ensemble mean and the median path."""

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
        assert _texts(paths.axes[0]) == [
            "ensemble mean, all possible traders\n$146,576",
            "median trader\n$606",
        ]

    def test_the_title_names_the_mean_and_the_median(self, paths) -> None:
        """Lesson 1 says the mean describes the crowd rather than any trader,
        so the title names the ensemble mean rather than an average trader."""
        assert paths._suptitle.get_text() == (
            "The ensemble mean climbs while the median trader loses"
        )

    def test_the_drawn_paths_average_well_short_of_the_ensemble_mean(self, paths) -> None:
        """The gold line is the mean over every possible trader, and the 200
        drawn fall far short of it, which is Lesson 6's point. The note says
        so, because a reader would otherwise take the gold line for the
        average of the grey ones."""
        assert paths.sample_mean == pytest.approx(21_664, abs=0.5)
        assert paths.sample_mean == pytest.approx(paths.paths[:, -1].mean(), rel=1e-12)
        assert np.mean(paths.paths[:, -1] > paths.mean[-1]) == pytest.approx(0.035)
        (note,) = [t.get_text() for t in paths.texts if t is not paths._suptitle]
        assert "average $21,664 at round 1,000" in note

    def test_the_note_names_the_seed_and_the_draw_method(self, paths) -> None:
        (note,) = [t.get_text() for t in paths.texts if t is not paths._suptitle]
        assert f"seed {BOOK_SEED}" in note
        assert "rng.integers" in note
        assert f"{FAN_PATHS} simulated traders" in note

    def test_the_gold_and_red_lines_are_the_two_rates_compounded(self, paths) -> None:
        """Only the attributes were held before, so a figure drawing the mean
        in red, or the median from the approximation, passed."""
        moments = gamble_moments()
        rounds = np.arange(ROUNDS + 1)
        gold, red = _thick(paths.axes[0])
        assert _rgb(gold.get_color()) == _rgb(ACCENT)
        assert _rgb(red.get_color()) == _rgb(LOST)
        assert list(gold.get_ydata()) == pytest.approx(
            list(1000.0 * np.exp(moments.ensemble_log_growth * rounds)), rel=1e-12
        )
        assert list(red.get_ydata()) == pytest.approx(
            list(1000.0 * np.exp(moments.growth_exact * rounds)), rel=1e-12
        )

    def test_a_different_seed_draws_different_paths_and_says_so(self, tmp_path: Path) -> None:
        other = make_paths_figure(out=tmp_path / "seed7.png", seed=7)
        logs = _flip_log_returns(ROUNDS, FAN_PATHS, 7, 110.0, 100.0, 1000.0)
        assert other.paths[:, -1] == pytest.approx(1000.0 * np.exp(logs.sum(axis=1)), rel=1e-9)
        (note,) = [t.get_text() for t in other.texts if t is not other._suptitle]
        assert "seed 7" in note

    def test_the_axes_are_log_scaled_and_show_every_round(self, paths) -> None:
        ax = paths.axes[0]
        assert ax.get_yscale() == "log"
        assert ax.get_xlim() == pytest.approx((0, ROUNDS))
        low, high = ax.get_ylim()
        assert low < paths.paths.min() and paths.paths.max() < high
        dashed = [line for line in ax.lines if list(line.get_ydata()) == [1000.0, 1000.0]]
        assert len(dashed) == 1


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
        assert inset.get_title(loc="left") == "zoomed near $600: no balance at $599"

    def test_the_note_names_the_range_the_bars_cover(self, distribution) -> None:
        low, high = HEADS_SHOWN
        (note,) = [t.get_text() for t in distribution.texts if t is not distribution._suptitle]
        assert f"One bar per head count from {low} to {high}" in note
        assert (low, high) == (440, 560)

    def test_no_label_is_parsed_as_math(self, stake, paths, distribution, sign, estimator) -> None:
        """Two dollar signs in one matplotlib string turn the text between
        them into an italic formula, which the inset title did on its first
        draw. Every text artist here is drawn with math parsing off."""
        for fig in (stake, paths, distribution, sign, estimator):
            texts = [*fig.texts]
            for ax in fig.axes:
                texts += [*ax.texts, ax.title, ax._left_title]
            assert all(not text.get_parse_math() for text in texts)

    def test_each_bar_is_centred_on_its_own_balance(self, distribution) -> None:
        """Heights and colours alone pass with every bar shifted one slot, so
        the geometric centre of each bar on the log axis is held too."""
        b = distribution.balances
        low, _ = HEADS_SHOWN
        for h, bar in enumerate(distribution.axes[0].containers[0], low):
            left, right = bar.get_x(), bar.get_x() + bar.get_width()
            assert np.sqrt(left * right) == pytest.approx(b.balance[h], rel=1e-9)
            assert left < b.balance[h] < right

    def test_the_lines_and_stems_wear_their_colours_and_the_axes_their_scales(
        self, distribution
    ) -> None:
        ax = distribution.axes[0]
        assert ax.get_xscale() == "log"
        assert [_rgb(line.get_color()) for line in ax.lines] == [
            _rgb(LOST),
            _rgb(MUTED),
            _rgb(ACCENT),
        ]
        low, high = ax.get_ylim()
        assert low == 0 and distribution.balances.probability.max() < high
        inset = distribution.inset
        assert [_rgb(c.get_color()[0]) for c in inset.collections] == [_rgb(LOST), _rgb(LOST)]
        tops = [c.get_segments()[0][1][1] for c in inset.collections]
        assert all(t < inset.get_ylim()[1] for t in tops)


class TestTheSignFigure:
    """Lesson 6, first problem: a small run gets the sign wrong a quarter of the time."""

    def test_each_run_is_the_simulation_at_its_size(self, sign) -> None:
        assert [(r.rounds, r.traders) for r in sign.runs] == list(RUN_SIZES)
        for run in sign.runs:
            assert len(run.estimates) == SIGN_SEEDS
            for seed in (0, 42, 199):
                assert (
                    run.estimates[seed]
                    == simulate(run.rounds, run.traders, seed).time_average_growth
                )

    def test_the_wrong_sign_counts_and_standard_errors(self, sign) -> None:
        """56 and 0 are what ``tests/test_coin_flip_growth.py`` pins for these
        two sizes, and the note prints the two standard errors."""
        small, large = sign.runs
        assert (small.wrong_sign, large.wrong_sign) == (56, 0)
        # The alt text in the post describes the small run's spread by these.
        assert small.estimates.min() == pytest.approx(-0.0024, abs=5e-5)
        assert small.estimates.max() == pytest.approx(0.0015, abs=5e-5)
        assert small.standard_error == pytest.approx(7.4148e-4, abs=5e-8)
        assert large.standard_error == pytest.approx(1.0486e-4, abs=5e-8)
        (note,) = [t.get_text() for t in sign.texts if t is not sign._suptitle]
        assert note == (
            "Each bar counts seeds whose estimate falls in a 1e-4-wide range. Red bars sit "
            "right of zero, where the losing bet looks like a winner.\n"
            "Standard error 7.41e-4 for the small run and 1.05e-4 for the large one, "
            "against a true growth of −0.0005."
        )

    def test_the_bars_count_every_seed_and_zero_is_a_bin_edge(self, sign) -> None:
        """A bar straddling zero would mix right and wrong signs under one
        colour, so zero has to be an edge."""
        assert np.isclose(sign.edges, 0.0, atol=1e-15).any()
        for ax, run in zip(sign.axes, sign.runs, strict=True):
            bars = ax.containers[0]
            heights = [bar.get_height() for bar in bars]
            expected, _ = np.histogram(run.estimates, bins=sign.edges)
            assert heights == list(expected)
            assert sum(heights) == SIGN_SEEDS
            centres = [bar.get_x() + bar.get_width() / 2 for bar in bars]
            assert centres == pytest.approx(list((sign.edges[:-1] + sign.edges[1:]) / 2))

    def test_red_bars_are_exactly_the_wrong_signs(self, sign) -> None:
        for ax, run in zip(sign.axes, sign.runs, strict=True):
            red = 0
            for bar in ax.containers[0]:
                centre = bar.get_x() + bar.get_width() / 2
                expected = LOST if centre > 0 else MUTED
                assert _rgb(bar.get_facecolor()) == _rgb(expected)
                red += bar.get_height() if centre > 0 else 0
            assert red == run.wrong_sign

    def test_each_panel_marks_zero_and_the_true_growth(self, sign) -> None:
        truth = gamble_moments().growth_exact
        for ax in sign.axes:
            lines = [(line.get_xdata()[0], _rgb(line.get_color())) for line in ax.lines]
            assert lines == [(0, _rgb("#23201A")), (pytest.approx(truth), _rgb(ACCENT))]
        assert sign.axes[0].get_xlim() == sign.axes[1].get_xlim()

    def test_the_titles_state_the_counts(self, sign) -> None:
        assert (
            sign._suptitle.get_text()
            == "A small simulation gets the sign wrong more than a quarter of the time"
        )
        small, _ = sign.runs
        assert small.wrong_sign / SIGN_SEEDS > 0.25
        assert [ax.get_title(loc="left") for ax in sign.axes] == [
            "100 rounds × 200 traders: 56 of 200 seeds get the sign wrong",
            "1,000 rounds × 1,000 traders: 0 of 200 seeds get the sign wrong",
        ]
        assert _texts(sign.axes[0]) == ["true growth, −0.0005", "zero"]


class TestTheEstimatorFigure:
    """Lesson 6, second problem: averaging final wealth reads low."""

    def test_both_estimators_come_from_the_same_draws(self) -> None:
        rounds, traders, seeds = ESTIMATOR_RUN
        assert (rounds, traders, seeds) == (5000, 1000, 20)
        e = ensemble_estimates()
        logs = _flip_log_returns(rounds, traders, 3, 110.0, 100.0, 1000.0)
        assert e.wealth_average[3] == pytest.approx(
            np.log(np.exp(logs.sum(axis=1)).mean()) / rounds, rel=1e-12
        )
        assert e.per_toss[3] == pytest.approx(np.log1p(np.expm1(logs).mean()), rel=1e-12)
        assert e.per_toss[3] == pytest.approx(
            simulate(rounds, traders, 3).ensemble_log_growth, rel=1e-12
        )

    def test_the_wealth_average_reads_low_and_the_per_toss_one_does_not(self, estimator) -> None:
        """The same bounds ``tests/test_coin_flip_growth.py`` holds, which the
        title and the post quote."""
        e = estimator.estimates
        assert e.truth == pytest.approx(0.0049875, abs=5e-8)
        assert np.all(e.wealth_average < 0.0038)
        # The alt text in the post describes the wealth average's spread by these.
        assert e.wealth_average.min() == pytest.approx(0.0023, abs=5e-5)
        assert e.wealth_average.max() == pytest.approx(0.0037, abs=5e-5)
        assert np.all(np.abs(e.per_toss - e.truth) < PER_TOSS_BAND)
        assert PER_TOSS_BAND == 1e-4

    def test_the_dots_are_the_estimates_in_their_rows(self, estimator) -> None:
        e = estimator.estimates
        ax = estimator.axes[0]
        dots = [line for line in ax.lines if line.get_marker() == "o"]
        assert [_rgb(d.get_color()) for d in dots] == [_rgb(LOST), _rgb(MUTED)]
        assert list(dots[0].get_xdata()) == pytest.approx(list(e.wealth_average))
        assert list(dots[1].get_xdata()) == pytest.approx(list(e.per_toss))
        assert set(dots[0].get_ydata()) == {1.0} and set(dots[1].get_ydata()) == {0.0}
        low, high = ax.get_xlim()
        assert low < e.wealth_average.min() and max(e.per_toss.max(), e.truth) < high

    def test_the_true_value_is_marked_and_labelled(self, estimator) -> None:
        ax = estimator.axes[0]
        (truth,) = [line for line in ax.lines if line.get_marker() != "o"]
        assert truth.get_xdata()[0] == pytest.approx(estimator.estimates.truth)
        assert _rgb(truth.get_color()) == _rgb(ACCENT)
        assert _texts(ax) == [
            "true ensemble growth\nln(1.005) = 0.0049875",
            "all 20 dots, within 1e-4 of the true value",
        ]
        assert estimator._suptitle.get_text() == "Averaging final wealth reads low on all 20 seeds"
        (note,) = [t.get_text() for t in estimator.texts if t is not estimator._suptitle]
        assert note == (
            "1,000 simulated traders playing 5,000 rounds, one dot per seed. "
            "The wealth average misses the rare lucky paths that carry the mean.\n"
            "Averaging each toss’s return needs no rare paths and lands within 1e-4 of "
            "the true value every time."
        )


class TestTheCommittedImagesAreThoseFigures:
    @pytest.mark.parametrize(
        "name",
        [STAKE_FIGURE, PATHS_FIGURE, DISTRIBUTION_FIGURE, SIGN_FIGURE, ESTIMATOR_FIGURE],
    )
    def test_a_fresh_draw_has_the_committed_image_dimensions(
        self, name: str, out_dir: Path, stake, paths, distribution, sign, estimator
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
        make_sign_figure(out=tmp_path / "d.png")
        make_estimator_figure(out=tmp_path / "e.png")
        assert list(default.iterdir()) == []

    def test_the_command_writes_all_five_and_says_where(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(figures, "FIGURES_DIR", tmp_path)
        figures.main()
        out = capsys.readouterr().out
        for name in (
            STAKE_FIGURE,
            PATHS_FIGURE,
            DISTRIBUTION_FIGURE,
            SIGN_FIGURE,
            ESTIMATOR_FIGURE,
        ):
            assert f"wrote {tmp_path / name}" in out
            assert (tmp_path / name).is_file()
