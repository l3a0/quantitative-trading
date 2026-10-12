"""How far USD.CAD's Hurst exponent moves by chance and by the day its sample starts.

Example 2.2 of *Algorithmic Trading* reports an H of 0.49 for USD.CAD, and on
the 1,216 closes :mod:`chan.usdcad_mean_reversion` reads, ``genhurst`` gives
0.4732 and Chan's 2018 Python port's estimator gives 0.4758. Both miss. This
module asks how large that miss is beside the variation H shows on a series
with no reversion at all, so a reader can tell a miss that means something
from one chance alone would produce.

It measures two things.

1. **Each estimator on random walks of the same length.**
   :func:`random_walk_hurst` draws ``paths`` Gaussian random walks of 1,216
   log prices from one seeded generator and computes both estimators on each.
   The spread of those values is how far H moves when nothing but chance
   moves it. Both estimators ignore a series' scale and its drift, so the
   walks take standard normal steps rather than USD.CAD's own mean and
   standard deviation, and ``tests/test_usdcad_mean_reversion.py`` checks that
   indifference rather than assuming it.
2. **``genhurst`` across start days.** ``genhurst`` samples every ``tt``-th
   point counting from the first observation, so which day the sample starts
   on changes which points it reads. :func:`start_offset_hurst` drops the
   first ``k`` closes for each ``k`` in :data:`START_OFFSETS` and computes both
   estimators and the three figures the script's comments print, so it also
   says on which start day those comments still land. The port's estimator
   uses every overlapping change and barely moves.

What it does not measure. A Gaussian random walk is the null hypothesis
rather than a model of USD.CAD, so the spread says how H behaves when there is
nothing to find and says nothing about the distribution of H on a series that
does revert. No block bootstrap of USD.CAD's own returns is carried. Resampling
returns keeps their short-range structure and breaks any reversion longer than
a block, so it answers a different question, and the issue that asked for this
measurement made it optional.

Exploratory. The measurement was designed after the miss was seen, to answer
how significant the miss is, so it is a reading of the miss rather than a
test registered before it. Nothing here chooses a start day or a bar time for
the headline H, which stays the script's: the 16:59 bar, from the first close.

Run it with::

    uv run python -m chan.usdcad_hurst_noise
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from ithildincore.timeseries import ou_half_life

from chan.stationarity_tests import genhurst, jplv7_adf, vratiotest
from chan.usdcad_mean_reversion import (
    ADF_LAGS,
    ADF_ORDER,
    BOOK_HURST,
    HURST_Q,
    SCRIPT_ADF,
    SCRIPT_HALF_LIFE,
    SCRIPT_VRATIO_P,
    python_port_hurst,
    read_sources,
)
from chan.vintage import VintageUnavailable

#: The generator's seed, the date the measurement was first run.
SEED = 20261011
#: Random walks drawn. The tests say what precision this many supports.
PATHS = 1000
#: Closes dropped from the start of the sample, 0 being the script's own start.
START_OFFSETS = tuple(range(11))


@dataclass(frozen=True)
class RandomWalkHurst:
    """Both estimators of H on the same seeded random walks, one value per walk."""

    genhurst: np.ndarray
    port: np.ndarray
    length: int
    seed: int


@dataclass(frozen=True)
class StartOffset:
    """H and the script's three landed figures on the closes after dropping the first ``offset``."""

    offset: int
    first_day: pd.Timestamp
    genhurst: float
    port: float
    adf_statistic: float
    vratio_p_value: float
    half_life: float

    @property
    def prints_as_book(self) -> bool:
        """``genhurst`` at the two decimals the book prints is its 0.49."""
        return round(self.genhurst, 2) == BOOK_HURST

    @property
    def lands_the_script(self) -> bool:
        """The ADF statistic, the variance ratio's p-value and the half-life all land six decimals.

        These are the three calculations whose figures the script's comments
        print and the committed closes reproduce from the first close.
        """
        return (
            round(self.adf_statistic, 6) == SCRIPT_ADF
            and round(self.vratio_p_value, 6) == SCRIPT_VRATIO_P
            and round(self.half_life, 6) == SCRIPT_HALF_LIFE
        )


def random_walk(length: int, rng: np.random.Generator) -> np.ndarray:
    """``length`` log prices of a Gaussian random walk from 0, with standard normal steps."""
    return np.concatenate([[0.0], np.cumsum(rng.standard_normal(length - 1))])


def random_walk_hurst(length: int, paths: int = PATHS, seed: int = SEED) -> RandomWalkHurst:
    """``genhurst(z, 2)`` and :func:`python_port_hurst` on ``paths`` seeded random walks.

    Every walk comes from one ``numpy.random.default_rng(seed)`` in order, and
    both estimators read the same walk, so the two arrays pair up by position.
    """
    rng = np.random.default_rng(seed)
    gen = np.empty(paths)
    port = np.empty(paths)
    for i in range(paths):
        z = random_walk(length, rng)
        gen[i] = genhurst(z, HURST_Q)
        port[i] = python_port_hurst(z)
    return RandomWalkHurst(genhurst=gen, port=port, length=length, seed=seed)


def start_offset_hurst(
    closes: pd.Series, offsets: tuple[int, ...] = START_OFFSETS
) -> list[StartOffset]:
    """Both estimators and the script's three landed figures after dropping the first closes."""
    rows = []
    for offset in offsets:
        kept = closes.iloc[offset:]
        y = kept.to_numpy(dtype=float)
        z = np.log(y)
        rows.append(
            StartOffset(
                offset=offset,
                first_day=kept.index[0],
                genhurst=genhurst(z, HURST_Q),
                port=python_port_hurst(z),
                adf_statistic=jplv7_adf(y, ADF_ORDER, ADF_LAGS).statistic,
                vratio_p_value=vratiotest(z).p_value,
                half_life=ou_half_life(y),
            )
        )
    return rows


def percentile(null: np.ndarray, value: float) -> float:
    """The percent of ``null`` strictly below ``value``."""
    return float((null < value).mean() * 100)


def in_standard_deviations(null: np.ndarray, distance: float) -> float:
    """``distance`` divided by the sample standard deviation of ``null``."""
    return float(distance / null.std(ddof=1))


@dataclass(frozen=True)
class HurstNoise:
    """The observed H of each estimator beside its random-walk values and its start-day sweep."""

    observed_genhurst: float
    observed_port: float
    walks: RandomWalkHurst
    offsets: list[StartOffset]


def measure(closes: pd.Series, paths: int = PATHS, seed: int = SEED) -> HurstNoise:
    """Both estimators on ``closes`` from its first close, on random walks, and by start day."""
    z = np.log(closes.to_numpy(dtype=float))
    return HurstNoise(
        observed_genhurst=genhurst(z, HURST_Q),
        observed_port=python_port_hurst(z),
        walks=random_walk_hurst(len(z), paths=paths, seed=seed),
        offsets=start_offset_hurst(closes),
    )


def report(noise: HurstNoise) -> None:
    """Print each estimator against its random walks, then the start-day sweep."""
    w = noise.walks
    print("How far USD.CAD's Hurst exponent moves by chance and by its start day, Example 2.2")
    print(f"  {len(w.genhurst):,} Gaussian random walks of {w.length:,} log prices, seed {w.seed}")
    print()
    print(f"  {'':<34} {'genhurst':>10} {'port':>10}")
    for label, gen, port in (
        ("observed H, from the first close", noise.observed_genhurst, noise.observed_port),
        ("random-walk mean", w.genhurst.mean(), w.port.mean()),
        ("random-walk SD", w.genhurst.std(ddof=1), w.port.std(ddof=1)),
        (
            "percentile of the observed H",
            percentile(w.genhurst, noise.observed_genhurst),
            percentile(w.port, noise.observed_port),
        ),
        (
            "0.49 minus observed, in SDs",
            in_standard_deviations(w.genhurst, BOOK_HURST - noise.observed_genhurst),
            in_standard_deviations(w.port, BOOK_HURST - noise.observed_port),
        ),
        (
            "0.5 minus observed, in SDs",
            in_standard_deviations(w.genhurst, 0.5 - noise.observed_genhurst),
            in_standard_deviations(w.port, 0.5 - noise.observed_port),
        ),
    ):
        print(f"  {label:<34} {gen:>10.4f} {port:>10.4f}")
    print()
    print("  Start day, closes dropped from the first")
    print(f"  {'k':>3} {'first day':>12} {'genhurst':>10} {'port':>10} {'ADF':>10} {'lands':>6}")
    for row in noise.offsets:
        print(
            f"  {row.offset:>3} {str(row.first_day.date()):>12} {row.genhurst:>10.4f} "
            f"{row.port:>10.4f} {row.adf_statistic:>10.6f} "
            f"{'yes' if row.lands_the_script else 'no':>6}"
        )
    hits = sum(row.prints_as_book for row in noise.offsets)
    print(f"  {hits} of {len(noise.offsets)} start days give a genhurst that prints as 0.49.")
    print()
    print(
        "  Exploratory. The measurement was designed after the miss was seen, and the headline H "
        "stays the script's, from the first close."
    )


def run(data_dir: Path | None = None, paths: int = PATHS, seed: int = SEED) -> HurstNoise:
    """Read the closes, measure, and print the report."""
    _, closes = read_sources(data_dir)
    noise = measure(closes, paths=paths, seed=seed)
    report(noise)
    return noise


def main() -> None:
    argparse.ArgumentParser(
        description="How far USD.CAD's H moves by chance and by the day its sample starts"
    ).parse_args()
    try:
        run()
    except VintageUnavailable as refused:
        # A refusal that names the source is worth nothing at the bottom of a
        # traceback, so it reaches the reader as one line, the way
        # chan.usdcad_mean_reversion.main does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
