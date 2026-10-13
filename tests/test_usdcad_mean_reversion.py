"""The pins for the stationarity tests and linear mean reversion on USD.CAD.

They are *Algorithmic Trading*'s Examples 2.1 to 2.5.

This file is the single authority for every number any prose surface quotes
about Examples 2.1 to 2.5, with one exception, in
``blog/usdcad-stationarity-lessons.md``. That post also quotes numbers held
elsewhere: H at a ``maxT`` of 24 in ``tests/test_tu_momentum.py``, CAD/AUD's
half-life of 141.6 days in ``tests/test_stationary_candidates.py``, the book's
23-day half-life in ``tests/test_etf_cointegration.py``, and its figure's
labels in ``tests/test_usdcad_mean_reversion_figures.py``. README lists what
the post says that nothing asserts. ``blog/tu-momentum-lessons.md`` quotes
USD.CAD's H at a ``maxT`` of 19, which this file pins, so a change to that pin
moves that post too. ``docs/replication-log.md`` Entry 22 carries the verdicts
and points here row by row.

Every pin on the committed closes reads one vintage and one specification, so
both are stated once here and carried in every figure's failure message as
:data:`SPEC`.

- **Vintage.** ``pythoncodesanddata/inputData_USDCAD.csv``, vendor ``chan-py``,
  symbol ``USDCAD``, basis ``raw``, saved 2018-10-13, the minute file of
  Chan's 2018 Python port. Its identity is the row of ``PYTHON_PORT`` in
  ``tests/support/committed_vintages.py``. The 16:59 bar of each day gives
  1,216 closes from 2007-07-23 to 2012-03-28.
- **Specification.** ``stationarityTests.m`` at the mirror commit
  :mod:`chan.usdcad_mean_reversion` names. jplv7's ``adf`` at trend order 0
  and 1 lag, with ``ztcrit``'s critical values. ``genhurst`` at q = 2 and its
  default ``maxT`` of 19 on the log closes. ``vratiotest`` at its defaults,
  period 2, heteroskedasticity-consistent and two-sided, on the log closes. The
  half-life from the change regressed on the previous close and a constant.
  Example 2.5's position is minus the close's distance from its moving average
  in moving standard deviations, both over the half-life rounded, and its claim
  is the one issue 338 declared before any P&L was computed: the sum of the
  daily P&L over all 1,216 rows is greater than 0.

``TestExample22HowFarHMovesByChance`` reads the same vintage under a second
specification, :data:`NOISE_SPEC`. It sets the observed H beside each
estimator's values on 40,000 Gaussian random walks of 1,216 log prices drawn
from ``numpy.random.default_rng(20261011)``, and beside both estimators and
the script's three landed figures with the first 0 to 10 closes dropped.
:mod:`chan.usdcad_hurst_noise` computes both. The class docstring says what
precision 40,000 walks support.
That measurement was designed after the miss was seen, so it is exploratory
in the same sense, a reading of the miss rather than a test registered before
it.

Each figure Chan printed is pinned twice, at the precision he printed it and
at the precision that is real, so a change cannot move it inside his rounding
unnoticed. H is pinned against the book's 0.49 as a miss.

Exploratory. Reproducing Chan's figures spends the 2007 to 2012 sample on
tests he chose. It first ran here on 2026-10-05.
"""

from __future__ import annotations

import dataclasses

import numpy as np
import pandas as pd
import pytest
from ithildincore.timeseries import adf_tstat

from chan import usdcad_hurst_noise, usdcad_mean_reversion
from chan.matlab_helpers import moving_avg, moving_std
from chan.series import WindowCrossesScaleBreak, scale_breaks
from chan.stationarity_tests import ZTCRIT_CONSTANT, genhurst, vratiotest
from chan.usdcad_hurst_noise import (
    PATHS,
    SEED,
    START_OFFSETS,
    HurstNoise,
    genhurst_rows,
    in_standard_deviations,
    measure,
    percentile,
    python_port_hurst_rows,
    random_walk_hurst,
    random_walks,
    report,
)
from chan.usdcad_mean_reversion import (
    ADF_LAGS,
    ADF_ORDER,
    BOOK_ADF,
    BOOK_HALF_LIFE_DAYS,
    BOOK_HURST,
    HURST_Q,
    MINUTES_DATED,
    SCRIPT_ADF,
    SCRIPT_AR1,
    SCRIPT_CRITICAL,
    SCRIPT_HALF_LIFE,
    SCRIPT_VRATIO_H,
    SCRIPT_VRATIO_P,
    SYMBOL,
    StationarityRun,
    linear_mean_reversion,
    main,
    market_value,
    pnl_drawdown,
    python_port_hurst,
    read_sources,
    run,
    stationarity_tests,
)
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import PYTHON_PORT

SPEC = (
    "inputData_USDCAD.csv saved 2018-10-13, 16:59 closes, jplv7 adf(y, 0, 1), "
    "genhurst(log(y), 2), vratiotest(log(y)), half-life from ols(dy, [ylag 1]), "
    "Example 2.5 over the rounded half-life"
)
NOISE_SPEC = (
    "inputData_USDCAD.csv saved 2018-10-13, 16:59 closes, genhurst(z, 2) at maxT 19 and the "
    "Python port's estimator, on the log closes from start offsets 0 to 10 and on 40,000 "
    "Gaussian random walks of 1,216 log prices from default_rng(20261011); at each offset "
    "also jplv7 adf(y, 0, 1), vratiotest(log(y)) at period 2, and the half-life from "
    "ols(dy, [ylag 1])"
)
MINUTE_FILE = "pythoncodesanddata/inputData_USDCAD.csv"


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def result(sources) -> StationarityRun:
    return stationarity_tests(*sources)


class TestTheSpecification:
    def test_the_calls_are_the_scripts(self) -> None:
        assert (ADF_ORDER, ADF_LAGS, HURST_Q) == (0, 1, 2)

    def test_the_printed_figures_are_transcribed_as_printed(self) -> None:
        assert SCRIPT_ADF == -1.840744
        assert SCRIPT_AR1 == 0.994120
        assert SCRIPT_CRITICAL == (-3.458, -2.871, -2.594)
        assert (SCRIPT_VRATIO_H, SCRIPT_VRATIO_P) == (0, 0.367281)
        assert SCRIPT_HALF_LIFE == 115.209794
        assert (BOOK_ADF, BOOK_HURST, BOOK_HALF_LIFE_DAYS) == (-1.84, 0.49, 115)


class TestTheVintage:
    def test_the_closes_are_the_pinned_minute_file(self, sources) -> None:
        entry, _ = sources
        vendor, symbol, basis, saved, workbook, shape = PYTHON_PORT[MINUTE_FILE]
        assert (entry.path, entry.vendor, entry.symbol, entry.price_basis) == (
            MINUTE_FILE,
            vendor,
            symbol,
            basis,
        )
        assert entry.saved_date == saved == MINUTES_DATED
        assert (entry.source_workbook, shape, entry.symbol) == (
            "PythonCodesAndData.zip",
            "minute",
            SYMBOL,
        )

    def test_the_1659_bar_gives_1216_closes(self, sources) -> None:
        _, closes = sources
        assert len(closes) == 1216, SPEC
        assert (str(closes.index[0].date()), str(closes.index[-1].date())) == (
            "2007-07-23",
            "2012-03-28",
        )
        assert closes.index.is_monotonic_increasing and closes.index.is_unique

    def test_the_scale_break_guard_flags_nothing(self, sources) -> None:
        """The run calls the guard, so a vintage that broke would refuse it. This one does not."""
        _, closes = sources
        assert scale_breaks(closes) == []

    def test_the_run_calls_the_guard(self, sources, monkeypatch) -> None:
        """Removing the call moves no figure here, so only a guard that refuses can show it runs."""

        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak(f"a break inside {start.date()} to {end.date()}")

        monkeypatch.setattr(usdcad_mean_reversion, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(WindowCrossesScaleBreak, match="2007-07-23 to 2012-03-28"):
            stationarity_tests(*sources)


class TestExample21TheAdfTest:
    def test_the_statistic_is_chans_minus_1_840744(self, result: StationarityRun) -> None:
        assert result.adf.statistic == pytest.approx(SCRIPT_ADF, abs=5e-7), SPEC
        # Nine decimals rather than ten. macOS gives -1.8407440890839797 and some
        # Linux CI runners -1.840744089202234, a 1.2e-10 gap in the last bits of
        # the regression, so the tenth decimal is not a figure the platforms
        # share. Issue 400 measured it.
        assert result.adf.statistic == pytest.approx(-1.840744089, abs=5e-10), SPEC
        assert round(result.adf.statistic, 2) == BOOK_ADF

    def test_the_ar1_estimate_is_chans_0_994120(self, result: StationarityRun) -> None:
        assert result.adf.ar1 == pytest.approx(SCRIPT_AR1, abs=5e-7), SPEC
        assert result.adf.ar1 == pytest.approx(0.9941196429, abs=5e-11), SPEC

    def test_the_critical_values_are_chans(self, result: StationarityRun) -> None:
        assert result.adf.critical == ZTCRIT_CONSTANT[9] == (-3.45830, -2.87104, -2.59369)
        assert tuple(round(c, 3) for c in result.adf.critical) == SCRIPT_CRITICAL

    def test_the_regression_fits_1213_rows_at_1_lag(self, result: StationarityRun) -> None:
        assert result.adf.nobs == 1213

    def test_the_unit_root_is_not_rejected_at_90_percent_and_lambda_is_negative(
        self, result: StationarityRun
    ) -> None:
        """Location 1114's two readings: above −2.594, and the slope on the level below 0."""
        assert result.adf.statistic > result.adf.critical[2]
        assert result.adf.ar1 - 1 < 0

    def test_adfuller_at_the_same_lag_misses_by_the_one_row_it_keeps(
        self, result: StationarityRun
    ) -> None:
        """``ithildincore``'s ``adf_tstat`` and Chan's Python port both run ``adfuller``.

        Neither prints −1.840744, so the script's figure needs jplv7's regression.
        """
        assert result.adfuller_statistic == pytest.approx(-1.8430182830, abs=5e-11)
        assert result.adfuller_ar1 == pytest.approx(0.9941138113, abs=5e-11)
        assert round(result.adfuller_statistic, 6) != SCRIPT_ADF
        assert adf_tstat(result.closes.to_numpy(), 1)[1] == 1214


class TestExample22TheHurstExponent:
    def test_h_misses_the_books_0_49(self, result: StationarityRun) -> None:
        assert result.hurst == pytest.approx(0.4732326652, abs=5e-11), SPEC
        assert round(result.hurst, 2) == 0.47 != BOOK_HURST

    def test_h_is_still_below_a_half(self, result: StationarityRun) -> None:
        """Location 1119's reading, weakly mean reverting, survives the miss as a side of 0.5.

        Below 0.5 is not evidence of reversion here, because a random walk of
        the same length gives a lower ``genhurst`` about one time in six, which
        ``TestExample22HowFarHMovesByChance`` measures.
        """
        assert result.hurst < 0.5

    def test_the_python_ports_own_genhurst_misses_too(self, result: StationarityRun) -> None:
        assert result.python_port_hurst == pytest.approx(0.4758441244, abs=5e-11)
        assert round(result.python_port_hurst, 2) == 0.48 != BOOK_HURST


@pytest.fixture(scope="module")
def noise(sources) -> HurstNoise:
    """About 11 seconds serially, nearly all of it the 40,000 walks."""
    _, closes = sources
    return measure(closes)


def mean_se(values: np.ndarray) -> float:
    """The standard error of a sample mean, the SD over the square root of the count."""
    return float(values.std(ddof=1) / np.sqrt(len(values)))


def sd_se(values: np.ndarray) -> float:
    """The large-sample standard error of a normal sample's SD, the SD over √(2(n − 1))."""
    return float(values.std(ddof=1) / np.sqrt(2 * (len(values) - 1)))


def percentile_se(percent: float, count: int) -> float:
    """The standard error of a share below a value, in percentage points."""
    return float(np.sqrt(percent * (100 - percent) / count))


def ratio_se(values: np.ndarray, distance: float, distance_se: float) -> float:
    """The delta-method standard error of ``distance`` divided by the sample SD."""
    sd = values.std(ddof=1)
    return float(np.hypot(distance_se / sd, distance * sd_se(values) / sd**2))


def holds_at(value: float, se: float, quoted: float, decimals: int) -> bool:
    """``quoted`` is what ``value`` prints as, with two standard errors to spare.

    Holds when the value and two standard errors either side all round to
    ``quoted`` at ``decimals`` places, so a different seed would very likely
    print the same digits.
    """
    return abs(value - quoted) + 2 * se <= 0.5 * 10**-decimals


class TestExample22HowFarHMovesByChance:
    """How far H moves on a random walk of the same length, and with the sample's start day.

    The exact pins are what seed 20261011 gives. They catch a change to the
    walks or to the estimators, and they say nothing about precision. What
    40,000 walks support is stated by the standard errors below, which
    :func:`test_the_standard_errors_of_40_000_walks` pins, and every figure
    prose quotes is checked with :func:`holds_at`: the quoted digits hold with
    two standard errors to spare. On that rule the walks support these, and
    nothing finer.

    - ``genhurst``'s random-walk mean as 0.496 and its SD as 0.023.
    - The port's random-walk mean as between 0.47 and 0.48, and its SD as 0.06.
    - 16 percent of walks below ``genhurst``'s 0.4732, and about half below the
      port's 0.4758, meaning within 5 points of 50.
    - ``genhurst``'s 0.4732 as 1.0 SD below its random-walk mean, and the port's
      0.4758 as within a tenth of an SD of its own.
    - The book's 0.49 as 0.7 and 0.2 SDs above the two observed values.

    The distance from 0.5 in SDs is pinned for the report and quoted nowhere.
    0.5 is the theoretical H of a random walk, which the port's estimator does
    not reach at 1,216 points, and ``genhurst``'s distance from it, 1.156, sits
    within two standard errors of the 1.15 rounding boundary.
    """

    def test_the_walks_are_the_stated_number_and_length(self, noise: HurstNoise) -> None:
        assert (PATHS, SEED, START_OFFSETS) == (40_000, 20261011, tuple(range(11)))
        assert len(noise.walks.genhurst) == len(noise.walks.port) == 40_000
        assert (noise.walks.length, noise.walks.seed) == (1216, 20261011)

    def test_the_observed_h_is_the_runs(self, noise: HurstNoise, result) -> None:
        assert noise.observed_genhurst == result.hurst
        assert noise.observed_port == result.python_port_hurst

    def test_the_rows_match_the_scalar_estimators(self) -> None:
        """The batched arithmetic is the scalar functions', to the last few bits."""
        walks = random_walks(12, 1216, np.random.default_rng(5))
        for walk, gen, port in zip(
            walks, genhurst_rows(walks), python_port_hurst_rows(walks), strict=True
        ):
            assert gen == pytest.approx(genhurst(walk, 2), abs=1e-13)
            assert port == pytest.approx(python_port_hurst(walk), abs=1e-13)

    def test_the_rows_match_on_a_short_series_too(self) -> None:
        """At 60 points the step and window lengths cut the series differently."""
        walks = random_walks(4, 60, np.random.default_rng(6))
        for walk, gen, port in zip(
            walks, genhurst_rows(walks), python_port_hurst_rows(walks), strict=True
        ):
            assert gen == pytest.approx(genhurst(walk, 2), abs=1e-13)
            assert port == pytest.approx(python_port_hurst(walk), abs=1e-13)

    def test_drawing_in_blocks_changes_no_walk(self) -> None:
        """The walks match bit for bit. A row's H can move in its last bit with the block shape."""
        whole = random_walks(5, 1216, np.random.default_rng(SEED))
        rng = np.random.default_rng(SEED)
        blocks = np.vstack([random_walks(k, 1216, rng) for k in (2, 2, 1)])
        np.testing.assert_array_equal(whole, blocks)
        one, many = random_walk_hurst(1216, paths=5, chunk=5), random_walk_hurst(1216, 5, chunk=2)
        np.testing.assert_allclose(one.genhurst, many.genhurst, rtol=0, atol=1e-14)
        np.testing.assert_allclose(one.port, many.port, rtol=0, atol=1e-14)

    def test_neither_estimator_reads_scale_or_drift(self) -> None:
        """Why standard normal steps can stand in for USD.CAD's own mean and SD."""
        (z,) = random_walks(1, 1216, np.random.default_rng(3))
        moved = 0.006 * z + 2e-4 * np.arange(1216) + 0.1
        assert genhurst(moved, 2) == pytest.approx(genhurst(z, 2), abs=1e-9)
        assert python_port_hurst(moved) == pytest.approx(python_port_hurst(z), abs=1e-9)

    def test_the_walks_are_seeded(self) -> None:
        first, again = random_walk_hurst(1216, paths=3), random_walk_hurst(1216, paths=3)
        np.testing.assert_array_equal(first.genhurst, again.genhurst)
        other = random_walk_hurst(1216, paths=3, seed=SEED + 1)
        assert not np.array_equal(first.genhurst, other.genhurst)

    def test_the_standard_errors_of_40_000_walks(self, noise: HurstNoise) -> None:
        """Pinned so prose can quote them. Each is a property of the count, not of the seed."""
        g, p = noise.walks.genhurst, noise.walks.port
        assert (round(mean_se(g), 5), round(mean_se(p), 5)) == (0.00012, 0.00029)
        assert (round(sd_se(g), 5), round(sd_se(p), 5)) == (0.00008, 0.00020)
        below_g = percentile(g, noise.observed_genhurst)
        below_p = percentile(p, noise.observed_port)
        assert round(percentile_se(below_g, len(g)), 2) == 0.18
        assert round(percentile_se(below_p, len(p)), 2) == 0.25

    def test_genhurst_on_a_random_walk_averages_0_496_with_an_sd_of_0_023(
        self, noise: HurstNoise
    ) -> None:
        g = noise.walks.genhurst
        assert g.mean() == pytest.approx(0.49622344, abs=5e-9), NOISE_SPEC
        assert g.std(ddof=1) == pytest.approx(0.02314563, abs=5e-9), NOISE_SPEC
        assert holds_at(g.mean(), mean_se(g), 0.496, 3)
        assert holds_at(g.std(ddof=1), sd_se(g), 0.023, 3)

    def test_the_port_estimator_on_a_random_walk_runs_low_between_0_47_and_0_48(
        self, noise: HurstNoise
    ) -> None:
        """0.5 is a random walk's theoretical H, which this estimator misses at 1,216 points."""
        p = noise.walks.port
        assert p.mean() == pytest.approx(0.47534832, abs=5e-9), NOISE_SPEC
        assert p.std(ddof=1) == pytest.approx(0.05767276, abs=5e-9), NOISE_SPEC
        assert 0.47 <= p.mean() - 2 * mean_se(p) and p.mean() + 2 * mean_se(p) <= 0.48
        assert holds_at(p.std(ddof=1), sd_se(p), 0.06, 2)
        assert p.std(ddof=1) > 2 * noise.walks.genhurst.std(ddof=1)

    def test_where_each_observed_h_falls_among_the_walks(self, noise: HurstNoise) -> None:
        """6,434 of 40,000 walks give ``genhurst`` below 0.4732, 19,575 a port H below 0.4758."""
        w = noise.walks
        assert (int((w.genhurst < noise.observed_genhurst).sum()), len(w.genhurst)) == (
            6434,
            40_000,
        ), NOISE_SPEC
        assert int((w.port < noise.observed_port).sum()) == 19_575, NOISE_SPEC
        below_g = percentile(w.genhurst, noise.observed_genhurst)
        below_p = percentile(w.port, noise.observed_port)
        assert holds_at(below_g, percentile_se(below_g, 40_000), 16, 0)
        assert abs(below_p - 50) + 2 * percentile_se(below_p, 40_000) <= 5

    def test_each_estimate_against_its_own_estimators_random_walks(self, noise: HurstNoise) -> None:
        """``genhurst`` is 1.0 SD below its random-walk mean, the port within 0.1 SD of its own."""
        g, p = noise.walks.genhurst, noise.walks.port
        gap_g = g.mean() - noise.observed_genhurst
        gap_p = p.mean() - noise.observed_port
        from_mean_g = in_standard_deviations(g, gap_g)
        from_mean_p = in_standard_deviations(p, gap_p)
        assert from_mean_g == pytest.approx(0.99330928, abs=5e-7), NOISE_SPEC
        assert from_mean_p == pytest.approx(-0.00859691, abs=5e-7), NOISE_SPEC
        assert holds_at(from_mean_g, ratio_se(g, gap_g, mean_se(g)), 1.0, 1)
        assert abs(from_mean_p) + 2 * ratio_se(p, gap_p, mean_se(p)) < 0.1

    def test_the_gap_to_the_books_0_49_is_under_one_sd(self, noise: HurstNoise) -> None:
        g, p = noise.walks.genhurst, noise.walks.port
        to_book_g = in_standard_deviations(g, BOOK_HURST - noise.observed_genhurst)
        to_book_p = in_standard_deviations(p, BOOK_HURST - noise.observed_port)
        assert to_book_g == pytest.approx(0.72442763, abs=5e-7), NOISE_SPEC
        assert to_book_p == pytest.approx(0.24545167, abs=5e-7), NOISE_SPEC
        assert holds_at(to_book_g, ratio_se(g, BOOK_HURST - noise.observed_genhurst, 0), 0.7, 1)
        assert holds_at(to_book_p, ratio_se(p, BOOK_HURST - noise.observed_port, 0), 0.2, 1)

    def test_the_gap_to_a_half_is_pinned_and_not_quoted(self, noise: HurstNoise) -> None:
        """``genhurst``'s 1.156 is within two standard errors of 1.15, so no one decimal holds."""
        g, p = noise.walks.genhurst, noise.walks.port
        to_half_g = in_standard_deviations(g, 0.5 - noise.observed_genhurst)
        to_half_p = in_standard_deviations(p, 0.5 - noise.observed_port)
        assert to_half_g == pytest.approx(1.15647460, abs=5e-7), NOISE_SPEC
        assert to_half_p == pytest.approx(0.41884374, abs=5e-7), NOISE_SPEC
        se = ratio_se(g, 0.5 - noise.observed_genhurst, 0)
        assert not holds_at(to_half_g, se, 1.2, 1) and not holds_at(to_half_g, se, 1.1, 1)

    def test_genhurst_moves_to_0_49_when_the_first_close_is_dropped(
        self, noise: HurstNoise
    ) -> None:
        first, second = noise.offsets[0], noise.offsets[1]
        assert (first.offset, str(first.first_day.date())) == (0, "2007-07-23")
        assert (second.offset, str(second.first_day.date())) == (1, "2007-07-24")
        assert first.genhurst == pytest.approx(0.4732326652, abs=5e-11), NOISE_SPEC
        assert second.genhurst == pytest.approx(0.4890716563, abs=5e-11), NOISE_SPEC
        assert (first.prints_as_book, second.prints_as_book) == (False, True)
        last = noise.offsets[-1]
        assert (last.offset, str(last.first_day.date())) == (10, "2007-08-06")

    def test_six_of_eleven_start_days_print_as_0_49(self, noise: HurstNoise) -> None:
        """Offsets 1, 3, 4, 6, 8 and 9. Offset 7 gives 0.48488, which prints as 0.48."""
        landed = [row.offset for row in noise.offsets if row.prints_as_book]
        assert landed == [1, 3, 4, 6, 8, 9], NOISE_SPEC
        assert noise.offsets[7].genhurst == pytest.approx(0.4848758154, abs=5e-11), NOISE_SPEC

    def test_the_first_close_gives_the_lowest_genhurst_and_one_start_day_tops_a_half(
        self, noise: HurstNoise
    ) -> None:
        values = [row.genhurst for row in noise.offsets]
        assert min(values) == noise.offsets[0].genhurst
        assert max(values) == noise.offsets[5].genhurst
        assert noise.offsets[5].genhurst == pytest.approx(0.5061926171, abs=5e-11), NOISE_SPEC

    def test_the_port_estimator_barely_moves_with_the_start_day(self, noise: HurstNoise) -> None:
        values = [row.port for row in noise.offsets]
        assert noise.offsets[0].port == pytest.approx(0.4758441244, abs=5e-11), NOISE_SPEC
        assert max(values) == noise.offsets[0].port
        assert min(values) == pytest.approx(0.4741152609, abs=5e-11), NOISE_SPEC
        assert max(values) - min(values) < 0.002

    def test_only_the_first_close_lands_the_scripts_other_figures(self, noise: HurstNoise) -> None:
        """A start a day later gives 0.49 only on a run other than the one the comments record."""
        assert [row.lands_the_script for row in noise.offsets] == [True] + [False] * 10
        second = noise.offsets[1]
        assert second.adf_statistic == pytest.approx(-1.8361499805, abs=5e-9), NOISE_SPEC
        assert round(second.adf_statistic, 6) != SCRIPT_ADF

    def test_the_report_prints_every_row(self, noise: HurstNoise, capsys) -> None:
        """Each row is read back and set against the arithmetic done here, column by column."""
        report(noise)
        lines = capsys.readouterr().out.splitlines()
        assert "  40,000 Gaussian random walks of 1,216 log prices, seed 20261011" in lines
        g, p = noise.walks.genhurst, noise.walks.port
        og, op = noise.observed_genhurst, noise.observed_port
        expected = {
            "observed H, from the first close": (og, op),
            "random-walk mean": (g.mean(), p.mean()),
            "random-walk SD": (g.std(ddof=1), p.std(ddof=1)),
            "random-walk mean minus observed, in SDs": (
                (g.mean() - og) / g.std(ddof=1),
                (p.mean() - op) / p.std(ddof=1),
            ),
            "percentile of the observed H": (100 * (g < og).mean(), 100 * (p < op).mean()),
            "0.49 minus observed, in SDs": (
                (0.49 - og) / g.std(ddof=1),
                (0.49 - op) / p.std(ddof=1),
            ),
            "0.5 minus observed, in SDs": ((0.5 - og) / g.std(ddof=1), (0.5 - op) / p.std(ddof=1)),
        }
        for label, (gen, port) in expected.items():
            (row,) = [each for each in lines if each[2:42].rstrip() == label]
            assert row.split()[-2:] == [f"{gen:.6f}", f"{port:.6f}"], row
        offset_rows = [each.split() for each in lines if each[:5].strip().isdigit()]
        assert len(offset_rows) == 11
        for cells, row in zip(offset_rows, noise.offsets, strict=True):
            assert cells == [
                str(row.offset),
                str(row.first_day.date()),
                f"{row.genhurst:.6f}",
                f"{row.port:.6f}",
                f"{row.adf_statistic:.6f}",
                "yes" if row.offset == 0 else "no",
            ]
        assert "  6 of 11 start days give a genhurst that prints as 0.49." in lines
        assert any("Exploratory." in each for each in lines)

    def test_main_prints_a_refusal_as_one_line(self, monkeypatch) -> None:
        def refuse(data_dir=None):
            raise VintageUnavailable(f"no committed vintage of {SYMBOL} saved {MINUTES_DATED}")

        monkeypatch.setattr(usdcad_hurst_noise, "run", refuse)
        monkeypatch.setattr("sys.argv", ["usdcad_hurst_noise"])
        with pytest.raises(SystemExit, match="no committed vintage of USDCAD saved 2018-10-13"):
            usdcad_hurst_noise.main()


class TestExample23TheVarianceRatio:
    def test_the_decision_and_p_value_are_chans(self, result: StationarityRun) -> None:
        assert int(result.vratio.rejects) == SCRIPT_VRATIO_H, SPEC
        assert result.vratio.p_value == pytest.approx(SCRIPT_VRATIO_P, abs=5e-7), SPEC
        assert result.vratio.p_value == pytest.approx(0.3672813756, abs=5e-11), SPEC

    def test_the_statistic_and_ratio(self, result: StationarityRun) -> None:
        assert result.vratio.statistic == pytest.approx(-0.9015774476, abs=5e-11)
        assert result.vratio.ratio == pytest.approx(0.9647450127, abs=5e-11)
        assert result.vratio.nobs == 1214

    def test_the_last_of_1215_returns_is_never_read(self, sources, result) -> None:
        """1,215 returns is odd, so MATLAB's trim to whole periods drops the last one."""
        _, closes = sources
        assert vratiotest(np.log(closes.to_numpy()[:-1])) == result.vratio


class TestExample24TheHalfLife:
    def test_the_half_life_is_chans_115_209794(self, result: StationarityRun) -> None:
        assert result.half_life == pytest.approx(SCRIPT_HALF_LIFE, abs=5e-7), SPEC
        assert result.half_life == pytest.approx(115.2097944852, abs=5e-10), SPEC
        assert round(result.half_life) == BOOK_HALF_LIFE_DAYS


class TestExample25LinearMeanReversion:
    def test_the_lookback_is_the_half_life_rounded(self, result: StationarityRun) -> None:
        assert result.lookback == 115

    def test_the_cumulative_pnl_is_positive_as_location_1225_says(
        self, result: StationarityRun
    ) -> None:
        """The claim issue 338 declared before any P&L was computed."""
        assert result.total_pnl > 0, SPEC
        assert result.total_pnl == pytest.approx(0.1141168588, abs=5e-11), SPEC

    def test_the_drawdown_reported_beside_it(self, result: StationarityRun) -> None:
        """It decides nothing. It is more than five times what the run ends with."""
        d = result.drawdown
        assert d.depth == pytest.approx(0.6425313986, abs=5e-11)
        assert (str(d.peak.date()), str(d.trough.date())) == ("2008-07-22", "2008-10-27")
        cumulative = result.pnl.cumsum()
        assert cumulative.max() == pytest.approx(0.1320839920, abs=5e-11)
        assert cumulative.idxmax() == d.peak
        assert cumulative.min() == pytest.approx(-0.5104474067, abs=5e-11)
        assert cumulative.idxmin() == d.trough
        assert 5 * result.total_pnl < d.depth < 6 * result.total_pnl

    def test_the_first_position_is_the_day_after_the_window_fills(
        self, result: StationarityRun
    ) -> None:
        assert str(result.first_position.date()) == "2008-01-02"
        assert result.pnl.index.get_loc(result.first_position) == result.lookback
        assert (result.pnl.iloc[: result.lookback] == 0).all()

    def test_each_days_pnl_is_yesterdays_position_times_todays_return(
        self, sources, result: StationarityRun
    ) -> None:
        """Recomputed by plain pandas, so a shifted position or a lost minus sign fails."""
        _, closes = sources
        y = closes.astype(float)
        position = -(y - y.rolling(115).mean()) / y.rolling(115).std(ddof=1)
        expected = (position.shift(1) * y.pct_change()).fillna(0.0)
        np.testing.assert_allclose(result.pnl.to_numpy(), expected.to_numpy(), atol=1e-12)

    def test_the_sharpe_ratio_against_any_fixed_account_is_0_12(
        self, result: StationarityRun
    ) -> None:
        """No figure Chan printed. The P&L has a Sharpe ratio whatever account it is divided by.

        The specification is ``√252 · mean / std`` with ``ddof=1`` and no
        risk-free rate, over the 1,101 days whose previous-day position is not
        NaN, from the first position on 2008-01-02 to the last close. Those
        days keep the three whose zero return earns nothing, and leave out the
        115 zeros the script fills in before any position exists. The P&L
        carries no rollover interest.

        Dividing each day's P&L by one account size is the return on that
        account. The run's own figure on three such accounts is pinned to the
        same value, which is the claim the blog post makes.
        """
        spec = SPEC + ", Sharpe sqrt(252) mean/std ddof=1, no risk-free rate, 1,101 held days"
        held = result.pnl.iloc[result.lookback :]
        assert len(held) == 1101 and held.index[0] == result.first_position, spec
        assert int((held == 0).sum()) == 3, spec
        assert result.sharpe == pytest.approx(0.1188463477, abs=5e-11), spec
        assert round(result.sharpe, 2) == 0.12
        expected = np.sqrt(252) * held.mean() / held.std(ddof=1)
        assert result.sharpe == pytest.approx(expected, abs=1e-12), spec
        for account in (0.5, 7.0, 1_000_000.0):
            on_account = dataclasses.replace(result, pnl=result.pnl / account)
            assert on_account.sharpe == pytest.approx(result.sharpe, abs=1e-12), spec


def held_position(result: StationarityRun) -> pd.Series:
    """The run's ``mktVal`` on each day, over the run's own lookback."""
    y = result.closes.to_numpy(dtype=float)
    return pd.Series(market_value(y, result.lookback), index=result.closes.index)


class TestBesideTheClaim:
    """Numbers the blog post on Examples 2.1 to 2.5 quotes about the trade, none a published figure.

    None of these is a replication. Each reads the run's closes and P&L on the
    vintage and specification in :data:`SPEC`, so they are as exploratory as
    the rest.
    """

    def test_the_dollar_rose_28_percent_on_the_canadian_dollar_across_the_fall(
        self, result: StationarityRun
    ) -> None:
        d = result.drawdown
        at_peak, at_trough = result.closes[d.peak], result.closes[d.trough]
        assert (at_peak, at_trough) == (1.00835, 1.29485), SPEC
        assert at_trough / at_peak - 1 == pytest.approx(0.2841275351, abs=5e-11), SPEC

    def test_the_largest_short_is_held_inside_the_fall(self, result: StationarityRun) -> None:
        """The largest short, 4.12 moving deviations, falls inside the drawdown."""
        position = held_position(result)
        assert position.min() == pytest.approx(-4.1198560837, abs=5e-11), SPEC
        assert str(position.idxmin().date()) == "2008-10-10"
        assert result.drawdown.peak < position.idxmin() < result.drawdown.trough
        assert position.max() == pytest.approx(3.0442241430, abs=5e-11), SPEC
        assert str(position.idxmax().date()) == "2009-05-29"

    def test_the_short_eases_while_the_close_keeps_rising(self, result: StationarityRun) -> None:
        """The deviation widens with the close, so the trough holds a smaller short."""
        position = held_position(result)
        trough = result.drawdown.trough
        assert result.closes[position.idxmin()] == 1.17325, SPEC
        rise = result.closes[trough] / result.closes[position.idxmin()] - 1
        assert rise == pytest.approx(0.1036437247, abs=5e-11), SPEC
        assert position[trough] == pytest.approx(-3.8330290865, abs=5e-11), SPEC

    def test_the_rule_is_short_on_all_69_days_of_the_fall(self, result: StationarityRun) -> None:
        """Each day after the peak through the trough earns on yesterday's position."""
        d = result.drawdown
        held = held_position(result).shift(1)[d.peak : d.trough].iloc[1:]
        assert len(held) == 69
        assert (held < 0).all(), SPEC

    def test_the_run_ends_below_its_high_after_climbing_back(self, result: StationarityRun) -> None:
        cumulative = result.pnl.cumsum()
        assert cumulative.max() - result.total_pnl == pytest.approx(0.0179671332, abs=5e-11)
        assert result.total_pnl - cumulative.min() == pytest.approx(0.6245642655, abs=5e-11)

    def test_the_rule_holds_short_on_488_days_and_long_on_613(
        self, result: StationarityRun
    ) -> None:
        """Counted on the day the P&L is earned, so on yesterday's position.

        The P&L each held day earns has the sign of that position times the
        day's return, which ties the count to the rule rather than to a copy.
        """
        held = held_position(result).shift(1).dropna()
        returns = result.closes.pct_change().loc[held.index]
        earned = result.pnl.loc[held.index]
        np.testing.assert_allclose(earned.to_numpy(), (held * returns).to_numpy(), atol=1e-12)
        assert len(held) == 1101 == len(result.closes) - result.lookback
        assert ((held < 0).sum(), (held > 0).sum()) == (488, 613), SPEC

    def test_2008_ends_at_minus_0_2552_and_the_rest_adds_0_3693(
        self, result: StationarityRun
    ) -> None:
        cumulative = result.pnl.cumsum()
        end_of_2008 = cumulative[:"2008-12-31"].iloc[-1]
        assert end_of_2008 == pytest.approx(-0.2552305412, abs=5e-11), SPEC
        assert result.total_pnl - end_of_2008 == pytest.approx(0.3693474000, abs=5e-11), SPEC

    def test_the_closes_span_10_6_half_lives(self, result: StationarityRun) -> None:
        assert len(result.closes) / result.half_life == pytest.approx(10.5546581819, abs=5e-11)
        assert round(len(result.closes) / result.half_life, 1) == 10.6


class TestTheRun:
    def test_it_prints_each_figure_beside_chans(self, sources, monkeypatch, capsys) -> None:
        monkeypatch.setattr(usdcad_mean_reversion, "read_sources", lambda data_dir=None: sources)
        run()
        out = capsys.readouterr().out
        assert "1216 closes, 2007-07-23 to 2012-03-28" in out
        for line, figures in (
            ("2.1 ADF statistic", ["-1.840744", "-1.840744", "-1.84"]),
            ("2.1 AR(1) estimate", ["0.994120", "0.994120"]),
            ("2.1 critical values", ["-3.458/-2.871/-2.594", "-2.594"]),
            ("2.2 Hurst exponent", ["0.473233", "0.49"]),
            ("2.3 variance ratio p-value", ["0.367281", "0.367281"]),
            ("2.4 half-life", ["115.209794", "115"]),
        ):
            (row,) = [each for each in out.splitlines() if line in each]
            assert all(figure in row.split() for figure in figures), row
        (h_row,) = [each for each in out.splitlines() if "2.3 variance ratio h" in each]
        assert h_row.split()[-3:] == ["0", "0", "none"], h_row
        assert "2.5 lookback 115 days, the half-life rounded. First position on 2008-01-02." in out
        assert "cumulative P&L 0.114117. The claim declared on issue 338, positive, holds." in out
        assert "deepest drawdown 0.642531, from 2008-07-22 to 2008-10-27" in out
        assert "statistic -1.843018, AR(1) 0.994114" in out
        assert "own genhurst: 0.475844" in out
        assert "Exploratory." in out


class TestTheRule:
    def test_the_rows_before_the_window_fills_earn_nothing(self) -> None:
        pnl = linear_mean_reversion(np.array([1.0, 2.0, 3.0, 2.0, 1.0, 2.0]), 3)
        np.testing.assert_array_equal(pnl[:3], [0.0, 0.0, 0.0])

    def test_a_close_above_its_average_is_sold_and_earns_on_a_fall(self) -> None:
        """Closes 1, 2, 3: the average is 2 and the deviation 1, so the position is −1.

        The next close of 1.5 is a return of −0.5, and −1 times −0.5 is +0.5.
        """
        y = np.array([1.0, 2.0, 3.0, 1.5])
        assert moving_avg(y, 3)[2] == 2.0 and moving_std(y, 3)[2] == 1.0
        assert linear_mean_reversion(y, 3)[3] == pytest.approx(0.5, abs=1e-15)

    def test_a_zero_deviation_leaves_the_day_at_zero_rather_than_nan(self) -> None:
        """A flat window divides by a zero deviation, which is NaN for 0/0 and set to 0."""
        y = np.array([2.0, 2.0, 2.0, 3.0])
        assert linear_mean_reversion(y, 3)[3] == 0.0

    def test_the_drawdown_finds_the_deepest_fall_and_its_dates(self) -> None:
        days = pd.date_range("2020-01-01", periods=6)
        pnl = pd.Series([0.0, 1.0, 1.0, -3.0, 1.0, 2.5], index=days)
        d = pnl_drawdown(pnl)
        assert d.depth == 3.0
        assert (d.peak, d.trough) == (days[2], days[3])

    def test_the_peak_is_the_last_day_at_the_high_before_the_trough(self) -> None:
        days = pd.date_range("2020-01-01", periods=4)
        d = pnl_drawdown(pd.Series([0.0, 1.0, 0.0, -3.0], index=days))
        assert (d.depth, d.peak, d.trough) == (3.0, days[2], days[3])

    def test_the_running_high_starts_at_the_first_day_rather_than_at_zero(self) -> None:
        days = pd.date_range("2020-01-01", periods=3)
        d = pnl_drawdown(pd.Series([-1.0, -1.0, 0.5], index=days))
        assert (d.depth, d.peak, d.trough) == (1.0, days[0], days[1])

    def test_the_lookback_rounds_a_half_away_from_zero_as_matlab_does(
        self, sources, monkeypatch
    ) -> None:
        """Python's ``round`` sends 114.5 to the even 114, and MATLAB's sends it to 115."""
        monkeypatch.setattr(usdcad_mean_reversion, "ou_half_life", lambda y: 114.5)
        assert round(114.5) == 114
        assert stationarity_tests(*sources).lookback == 115

    def test_the_deepest_fall_need_not_end_at_the_lowest_point(self) -> None:
        """Cumulative 0, 1, −0.5, 5, 4.5, −0.2: the fall from 5 is deepest, and −0.5 is lower."""
        days = pd.date_range("2020-01-01", periods=6)
        pnl = pd.Series(np.diff([0.0, 0.0, 1.0, -0.5, 5.0, 4.5, -0.2]), index=days)
        d = pnl_drawdown(pnl)
        assert d.depth == pytest.approx(5.2)
        assert (d.peak, d.trough) == (days[3], days[5])

    def test_a_run_that_never_falls_has_a_zero_drawdown(self) -> None:
        days = pd.date_range("2020-01-01", periods=3)
        d = pnl_drawdown(pd.Series([0.0, 1.0, 2.0], index=days))
        assert d.depth == 0.0 and d.trough == days[0]

    def test_a_series_that_does_not_revert_is_refused(self, sources) -> None:
        entry, closes = sources
        trending = pd.Series(np.exp(np.arange(len(closes)) * 1e-3), index=closes.index)
        with pytest.raises(ValueError, match="do not revert"):
            stationarity_tests(entry, trending)


class TestTheRefusals:
    def test_main_prints_a_refusal_as_one_line(self, monkeypatch) -> None:
        def refuse(data_dir=None):
            raise VintageUnavailable(f"no committed vintage of {SYMBOL} saved {MINUTES_DATED}")

        monkeypatch.setattr(usdcad_mean_reversion, "run", refuse)
        monkeypatch.setattr("sys.argv", ["usdcad_mean_reversion"])
        with pytest.raises(SystemExit, match="no committed vintage of USDCAD saved 2018-10-13"):
            main()

    def test_a_missing_vintage_reaches_the_reader(self, tmp_path) -> None:
        with pytest.raises(VintageUnavailable):
            read_sources(tmp_path)
