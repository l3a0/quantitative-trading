"""Every committed figure is what the code that makes it draws today.

A committed figure is a generated artifact, and ``docs/design.md``'s register
row "The regime-map figure and its generator, cut then reversed" rests on it
being regenerable: an image nothing regenerates is an artifact nobody can
check. The figure tests check the code, by reading the artists each ``make_*``
function returns. Until issue 581 nothing checked that the file on disk was
what that code draws. Two committed figures had drifted that way without a
test noticing, ``risk_parity_cash_rate.png`` by 569 pixels and
``reproduction_regime_map.png`` by 19, and this change redrew both.

So each figure here is drawn fresh into ``tmp_path`` and compared with its
committed file, pixel for pixel, through :mod:`tests.support.figure_pixels`.
The comparison is exact. A failure names how many pixels differ and by how
much, and the fix is to redraw the figure, as ``CLAUDE.md`` asks under
"Regenerating is the second half of an edit".

Every ``make_*`` function writes to ``docs/figures`` when ``out`` is None, so
each draw here passes a path under ``tmp_path``. Drawing without one would
overwrite the file being checked.

Three cases need more than a call with ``out``.

1. Two makers take an input their module's ``main()`` computes, and the draws
   below compute it the way ``main()`` does.
2. ``low_beta_holdout.png`` reads the owner's archive of minute bars, so its
   comparison skips where ``archive_skip_reason()`` in ``tests/conftest.py``
   gives a reason, as its other archive pins do.
3. ``cpo_cells.png`` needs a full run of Example 7.1 on the archive. Its
   comparison sits in ``tests/test_cpo_figures.py``, which already reads the
   ``cpo_result`` fixture, because a third test file reading it would build
   that run once more in its own worker.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import numpy as np
import pytest
from PIL import Image
from PIL.PngImagePlugin import PngInfo

from chan import (
    aud_cad_johansen_figures,
    aud_cad_rollover_figures,
    bollinger_figures,
    buy_on_gap_figures,
    calendar_spread_figures,
    calendar_spread_reversion_figures,
    cl_reversal_momentum_figures,
    coin_flip_figures,
    commodity_seasonals_figures,
    cross_sectional_momentum_figures,
    equity_seasonals_figures,
    etf_cointegration_figures,
    gld_gc_figures,
    gold_miners_oil_figures,
    index_arbitrage_figures,
    kalman_hedge_figures,
    kelly_allocation_figures,
    kelly_figures,
    khandani_lo_book_two_figures,
    khandani_lo_small_caps_figures,
    lag_residual_figure,
    low_beta_capped_figures,
    low_beta_holdout_figures,
    low_beta_leverage_figures,
    momentum_factor_figures,
    monte_carlo_leverage_figures,
    opening_gap_figures,
    pca_factor_momentum_figures,
    pead_figures,
    pead_rerun_figures,
    price_spread_figures,
    regime_figure,
    risk_parity_figures,
    roll_momentum_figures,
    roll_returns_figures,
    stationary_candidates_figures,
    survivorship_and_costs_figures,
    tu_hypothesis_tests_figures,
    tu_momentum_figures,
    usdcad_mean_reversion_figures,
    vix_filter_figures,
    vx_calendar_spread_figures,
    vx_es_figures,
    vx_es_roll_return_figures,
    xle_uso_roll_return_figures,
)
from chan.cpo_figures import CELLS_FIGURE
from chan.momentum_factor import autocorrelations, build_factors, read_sources
from chan.paths import FIGURES_DIR
from chan.pca_factor import SMALL_CAPS
from chan.pca_factor_momentum import (
    compute_both,
    daily_components,
    file_returns,
    weight_statistics,
)
from chan.series import load_panel
from tests import test_cpo_figures as cpo_figure_tests
from tests.conftest import archive_skip_reason
from tests.support.figure_pixels import assert_same_pixels, pixel_difference


def _factor_momentum(out: Path) -> object:
    """``chan.momentum_factor_figures.main`` without the write to the repo."""
    _, closes, _, spy, _, bills = read_sources()
    comparison = autocorrelations(build_factors(closes, spy, bills))
    return momentum_factor_figures.make_autocorrelation_figure(comparison, out=out)


def _pca_factor_momentum(out: Path) -> object:
    """``chan.pca_factor_momentum_figures.main`` without the write to the repo."""
    _, closes = load_panel(SMALL_CAPS, field="Close")
    returns = file_returns(closes)
    results = compute_both(closes)
    weights = weight_statistics(returns, daily_components(returns))
    return pca_factor_momentum_figures.make_pca_factor_momentum_figure(results, weights, out=out)


rp = risk_parity_figures
coin = coin_flip_figures
candidates = stationary_candidates_figures
survivorship = survivorship_and_costs_figures

#: Each committed figure this file draws, keyed by its file name in
#: ``docs/figures``, with the call that draws it to a given path.
DRAWS: dict[str, Callable[[Path], object]] = {
    "adf_residual_autocorrelation.png": lambda out: lag_residual_figure.make_lag_residual_figure(
        out=out
    ),
    "aud_cad_johansen.png": lambda out: aud_cad_johansen_figures.make_aud_cad_figure(out=out),
    "aud_cad_rollover.png": lambda out: aud_cad_rollover_figures.make_rollover_figure(out=out),
    "bollinger_band.png": lambda out: bollinger_figures.make_bollinger_figure(out=out),
    "buy_on_gap_cumulative_returns.png": lambda out: buy_on_gap_figures.make_cumulative_figure(
        out=out
    ),
    "calendar_spread_nulls.png": lambda out: calendar_spread_figures.make_nulls_figure(out=out),
    "calendar_spread_reversion.png": lambda out: (
        calendar_spread_reversion_figures.make_calendar_spread_reversion_figure(out=out)
    ),
    "cl_reversal_momentum.png": lambda out: cl_reversal_momentum_figures.make_join_figure(out=out),
    "coin_flip_capital_paths.png": lambda out: coin.make_paths_figure(out=out),
    "coin_flip_ensemble_estimators.png": lambda out: coin.make_estimator_figure(out=out),
    "coin_flip_final_balances.png": lambda out: coin.make_distribution_figure(out=out),
    "coin_flip_growth_by_stake.png": lambda out: coin.make_stake_figure(out=out),
    "coin_flip_sign_by_run_size.png": lambda out: coin.make_sign_figure(out=out),
    "commodity_seasonals_years.png": lambda out: commodity_seasonals_figures.make_years_figure(
        out=out
    ),
    "cross_sectional_momentum_cumulative_returns.png": lambda out: (
        cross_sectional_momentum_figures.make_cumulative_figure(out=out)
    ),
    "equity_seasonals_split.png": lambda out: equity_seasonals_figures.make_split_figure(out=out),
    "etf_cointegration.png": lambda out: etf_cointegration_figures.make_cointegration_figure(
        out=out
    ),
    "factor_momentum_autocorrelations.png": _factor_momentum,
    "gld_gc.png": lambda out: gld_gc_figures.make_gld_gc_figure(out=out),
    "gold_miners_oil_break.png": lambda out: gold_miners_oil_figures.make_break_figure(out=out),
    "index_arbitrage.png": lambda out: index_arbitrage_figures.make_index_arbitrage_figure(out=out),
    "kalman_hedge.png": lambda out: kalman_hedge_figures.make_kalman_figure(out=out),
    "kelly_allocation.png": lambda out: kelly_allocation_figures.make_allocation_figure(out=out),
    "kelly_growth_by_leverage.png": lambda out: kelly_figures.make_growth_figure(out=out),
    "khandani_lo_book_two.png": lambda out: khandani_lo_book_two_figures.make_reversal_figure(
        out=out
    ),
    "khandani_lo_cumulative_profit.png": lambda out: survivorship.make_cumulative_figure(out=out),
    "khandani_lo_small_caps.png": lambda out: (
        khandani_lo_small_caps_figures.make_khandani_lo_small_caps_figure(out=out)
    ),
    "low_beta_capped.png": lambda out: low_beta_capped_figures.make_low_beta_capped_figure(out=out),
    "low_beta_holdout.png": lambda out: low_beta_holdout_figures.make_low_beta_holdout_figure(
        out=out
    ),
    "low_beta_leverage.png": lambda out: low_beta_leverage_figures.make_low_beta_leverage_figure(
        out=out
    ),
    "monte_carlo_leverage.png": lambda out: (
        monte_carlo_leverage_figures.make_monte_carlo_leverage_figure(out=out)
    ),
    "opening_gap.png": lambda out: opening_gap_figures.make_opening_gap_figure(out=out),
    "pca_factor_momentum.png": _pca_factor_momentum,
    "pead_cumulative_return.png": lambda out: pead_figures.make_cumulative_figure(out=out),
    "pead_edgar_rerun.png": lambda out: pead_rerun_figures.make_rerun_figure(out=out),
    "price_spread_signals.png": lambda out: price_spread_figures.make_signals_figure(out=out),
    "reproduction_regime_map.png": lambda out: regime_figure.make_regime_figure(out=out),
    "risk_parity_against_qian.png": lambda out: rp.make_claim_figure(out=out),
    "risk_parity_bond_hurdle.png": lambda out: rp.make_hurdle_figure(out=out),
    "risk_parity_by_window.png": lambda out: rp.make_window_figure(out=out),
    "risk_parity_capital_and_risk.png": lambda out: rp.make_risk_split_figure(out=out),
    "risk_parity_cash_rate.png": lambda out: rp.make_rate_figure(out=out),
    "risk_parity_hurdle_by_correlation.png": lambda out: rp.make_correlation_figure(out=out),
    "risk_parity_ratio_and_correlation.png": lambda out: rp.make_decode_figure(out=out),
    "roll_momentum.png": lambda out: roll_momentum_figures.make_roll_momentum_figure(out=out),
    "roll_returns.png": lambda out: roll_returns_figures.make_roll_returns_figure(out=out),
    "stationary_candidates_bars.png": lambda out: candidates.make_bars_figure(out=out),
    "stationary_candidates_lags.png": lambda out: candidates.make_lags_figure(out=out),
    "stationary_candidates_windows.png": lambda out: candidates.make_windows_figure(out=out),
    "survivorship_toy_returns.png": lambda out: survivorship.make_toy_figure(out=out),
    "tu_hypothesis_tests.png": lambda out: (
        tu_hypothesis_tests_figures.make_tu_hypothesis_tests_figure(out=out)
    ),
    "tu_momentum.png": lambda out: tu_momentum_figures.make_tu_figure(out=out),
    "usdcad_mean_reversion.png": lambda out: usdcad_mean_reversion_figures.make_usdcad_figure(
        out=out
    ),
    "vix_filter.png": lambda out: vix_filter_figures.make_vix_filter_figure(out=out),
    "vx_calendar_spread.png": lambda out: vx_calendar_spread_figures.make_vx_calendar_spread_figure(
        out=out
    ),
    "vx_es.png": lambda out: vx_es_figures.make_vx_es_figure(out=out),
    "vx_es_roll_return.png": lambda out: vx_es_roll_return_figures.make_vx_es_roll_return_figure(
        out=out
    ),
    "xle_uso_roll_return.png": lambda out: (
        xle_uso_roll_return_figures.make_xle_uso_roll_return_figure(out=out)
    ),
}

#: The figures whose draw reads the owner's archive, so their comparison skips
#: where the archive pins skip.
ON_THE_ARCHIVE = {"low_beta_holdout.png"}

#: The figure compared in another file, with the test there that compares it.
COMPARED_ELSEWHERE = {
    CELLS_FIGURE: cpo_figure_tests.TestOnTheArchive.test_the_committed_figure_is_what_the_run_draws,
}


def _png(path: Path, pixels: np.ndarray, software: str = "Matplotlib version3.11.2") -> Path:
    """Write ``pixels`` as a PNG carrying the text chunk matplotlib writes."""
    info = PngInfo()
    info.add_text("Software", software)
    Image.fromarray(pixels, "RGBA").save(path, pnginfo=info)
    return path


class TestThePixelComparison:
    """The comparison every draw below relies on, on PNGs built by hand."""

    PIXELS = np.full((2, 3, 4), 200, dtype=np.uint8)

    def test_a_different_software_tag_alone_compares_equal(self, tmp_path: Path) -> None:
        """The case the register row declined a byte comparison over."""
        drawn = _png(tmp_path / "drawn.png", self.PIXELS)
        committed = _png(tmp_path / "committed.png", self.PIXELS, "Matplotlib version3.11.1")

        assert drawn.read_bytes() != committed.read_bytes()
        assert pixel_difference(drawn, committed) is None

    def test_one_level_in_one_channel_is_reported_with_its_size(self, tmp_path: Path) -> None:
        moved = self.PIXELS.copy()
        moved[1, 2, 0] = 199
        drawn = _png(tmp_path / "drawn.png", self.PIXELS)
        committed = _png(tmp_path / "committed.png", moved)

        assert pixel_difference(drawn, committed) == (
            "committed.png: 1 of 6 pixels differ from a fresh draw, by at most 1 of 255"
        )

    def test_a_pixel_counts_once_however_many_channels_moved(self, tmp_path: Path) -> None:
        moved = self.PIXELS.copy()
        moved[0, 0] = (190, 205, 200, 255)
        drawn = _png(tmp_path / "drawn.png", self.PIXELS)
        committed = _png(tmp_path / "committed.png", moved)

        assert pixel_difference(drawn, committed) == (
            "committed.png: 1 of 6 pixels differ from a fresh draw, by at most 55 of 255"
        )

    def test_a_different_size_is_reported_rather_than_compared(self, tmp_path: Path) -> None:
        drawn = _png(tmp_path / "drawn.png", self.PIXELS)
        committed = _png(tmp_path / "committed.png", np.full((3, 3, 4), 200, dtype=np.uint8))

        assert pixel_difference(drawn, committed) == (
            "committed.png: a fresh draw is 3 by 2 pixels and the committed file is 3 by 3"
        )


class TestEveryCommittedFigureIsCompared:
    def test_each_file_in_docs_figures_has_a_draw(self) -> None:
        """A figure committed without an entry here would go unchecked, which
        is how the two stale ones went unnoticed."""
        committed = {path.name for path in FIGURES_DIR.iterdir()}

        assert committed == set(DRAWS) | set(COMPARED_ELSEWHERE)

    def test_no_figure_is_drawn_in_two_places(self) -> None:
        assert not set(DRAWS) & set(COMPARED_ELSEWHERE)

    def test_the_archive_figures_are_ones_this_file_draws(self) -> None:
        assert ON_THE_ARCHIVE <= set(DRAWS)


@pytest.mark.parametrize("name", sorted(DRAWS))
def test_a_fresh_draw_has_the_committed_pixels(name: str, tmp_path: Path) -> None:
    if name in ON_THE_ARCHIVE and (reason := archive_skip_reason()) is not None:
        pytest.skip(reason)
    out = tmp_path / name

    DRAWS[name](out)

    assert_same_pixels(out, FIGURES_DIR / name)
