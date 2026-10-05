"""EWA, EWC and IGE, *Algorithmic Trading*'s Examples 2.6 to 2.8.

Chan asks whether the Australian and Canadian country ETFs, EWA and EWC, are
cointegrated, since both economies run on commodities. Example 2.6 answers
with the CADF test, which regresses one on the other and tests the residual.
Example 2.7 asks the same of the Johansen test, then adds IGE, a fund of
natural resource stocks, and builds a portfolio from the triplet's first
eigenvector. Example 2.8 trades that portfolio with a linear mean-reversion
rule. At Kindle location 1292 he reports a CADF statistic of "about –3.64",
at 1337 that both Johansen statistics find three relations at 95 percent, at
1347 a half-life of 23 days, and at 1368 "APR = 12.6 percent with a Sharpe
ratio of 1.4".

**The transcription.** One script, ``cointegrationTests.m``, runs all three
examples on the same three columns. It was read in the mirror
[ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) at
``e4bc46f``, under ``public/img/book2/``, git blob ``3eabdf2``, and landed
here for [issue 339](https://github.com/l3a0/quantitative-trading/issues/339).
``x`` is EWA, ``y`` is EWC and ``z`` is IGE.

1. ``ols(y, [x ones])`` gives the hedge ratio, EWC on EWA with an intercept.
   The script prints nothing from it. It feeds Figure 2.6 only.
2. ``cadf(y, x, 0, 1)`` is :func:`chan.pair_cointegration.lesage_cadf` with
   EWC as ``y`` and one lag.
3. ``johansen([y, x], 0, 1)`` and ``johansen([y, x, z], 0, 1)`` are
   :func:`chan.johansen.johansen`. The columns run EWC, EWA, IGE, which is the
   order the eigenvector rows follow.
4. ``yport`` sums each price times its weight in the first eigenvector, and
   its half-life is ``−log(2) / β`` from ``Δyport`` regressed on the lagged
   level with an intercept, which is
   :func:`ithildincore.timeseries.ou_half_life`.
5. The lookback is the half-life under MATLAB's ``round``. ``numUnits`` is
   minus the portfolio's distance from its moving average over that lookback,
   in moving standard deviations. Each ETF's position in dollars is
   ``numUnits`` times its weight times its price. The day's return is
   yesterday's positions times today's simple returns, summed, over
   yesterday's gross, and a day that is not a number is 0.
6. The APR is ``prod(1 + r)^(252 / n) − 1`` and the Sharpe ratio is
   ``√252 · mean / std`` over all 1,500 rows, with MATLAB's n − 1 ``std``,
   which are :func:`chan.khandani_lo_book_two.compounded_apr` and
   :func:`chan.khandani_lo.plain_sharpe`.

**What changed on the way over.** Four things, and none moves a figure.

1. The three ETFs are read as committed vintages through
   :func:`chan.series.load_panel` rather than from the ``.mat``.
2. The six ``plot``, ``scatter`` and ``figure`` lines are not carried. The run
   prints and draws nothing.
3. LeSage's ``lag`` pads its first row with zero where
   :func:`chan.matlab_helpers.backshift` pads with NaN. The first row's return
   is not a number either way, since a zero price divides by zero, so it
   becomes 0 under the script's own last line. The tests hold that.
4. The run calls the scale-break guard, which the script has no counterpart
   for. It passes on these three ETFs over the whole file.

**The eigenvector's sign is statsmodels'.** Every vector comes back as Chan
printed it with the sign flipped, for the reason :mod:`chan.johansen` gives.
Negating a portfolio flips ``numUnits`` and the weights together, so the
positions, the half-life, the APR and the Sharpe ratio are unchanged.

**Two readings the entry has to make.** Location 1337 says both statistics
find three relations for the triplet. The script's own printout shows the
eigen statistic for r ≤ 0 at 16.897, short of even its 90 percent bar, so the
eigen test finds none and the claim holds for the trace test alone. Location
1324 reads two relations between two series as two hedge ratios. Under the
Johansen test a full rank says each series is stationary by itself around a
constant, so the run also takes a plain ADF test of each ETF, the evidence
that reading depends on.

Every result here is exploratory. Reproducing Chan's figures spends the 2006
to 2012 sample on a portfolio he chose, and the eigenvector is fitted on the
same 1,500 days the strategy trades, so the APR is in-sample by construction.
Location 1350 calls the strategy free of data-snooping because the lookback
comes from the series. The weights come from the series as well, from all of
it.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from ithildincore.timeseries import ADF_CRIT_CONST, adf_tstat, ols, ou_half_life
from numpy.typing import NDArray

from chan.johansen import Johansen, johansen
from chan.khandani_lo import TRADING_DAYS, plain_sharpe
from chan.khandani_lo_book_two import compounded_apr, gap, matches
from chan.matlab_helpers import backshift, moving_avg, moving_std, round_half_away
from chan.pair_cointegration import lesage_cadf
from chan.series import load_panel, panel_line, refuse_window_crossing_a_break
from chan.vintage import VintageEntry, VintageUnavailable

SOURCE_FILE = "inputData_ETF.mat"

#: The script's ``x``, ``y`` and ``z``.
X, Y, Z = "EWA", "EWC", "IGE"
#: ``y2 = [y, x]`` and ``y3 = [y2, z]``, the column order every eigenvector follows.
PAIR = (Y, X)
TRIPLET = (Y, X, Z)

#: ``cadf(y, x, 0, 1)`` and ``johansen(·, 0, 1)``.
CADF_LAGS = 1
JOHANSEN_P = 0
JOHANSEN_K = 1

#: Example 2.6's printout, script lines 36 and 39, and location 1292.
SCRIPT_CADF_T = "-3.64346635"
SCRIPT_CADF_AR1 = "-0.020411"
#: jplv7's own table at 1, 5 and 10 percent, quoted. Nothing here computes it.
SCRIPT_CADF_CRITICAL = ("-3.880", "-3.359", "-3.038")
BOOK_CADF_T = "-3.64"

#: Example 2.7's printouts, one row per null r ≤ i, critical values at 90, 95, 99.
SCRIPT_PAIR_TRACE = ("19.983", "3.983")
SCRIPT_PAIR_TRACE_CRITICAL = (("13.429", "15.494", "19.935"), ("2.705", "3.841", "6.635"))
SCRIPT_PAIR_EIGEN = ("16.000", "3.983")
SCRIPT_PAIR_EIGEN_CRITICAL = (("12.297", "14.264", "18.520"), ("2.705", "3.841", "6.635"))
SCRIPT_TRIPLET_TRACE = ("34.429", "17.532", "4.471")
SCRIPT_TRIPLET_TRACE_CRITICAL = (
    ("27.067", "29.796", "35.463"),
    ("13.429", "15.494", "19.935"),
    ("2.705", "3.841", "6.635"),
)
SCRIPT_TRIPLET_EIGEN = ("16.897", "13.061", "4.471")
SCRIPT_TRIPLET_EIGEN_CRITICAL = (
    ("18.893", "21.131", "25.865"),
    ("12.297", "14.264", "18.520"),
    ("2.705", "3.841", "6.635"),
)
SCRIPT_EIGENVALUES = ("0.0112", "0.0087", "0.0030")
#: ``results.evec``, rows EWC, EWA, IGE and one eigenvector per column.
SCRIPT_EIGENVECTORS = (
    ("-1.0460", "-0.5797", "-0.2647"),
    ("0.7600", "-0.1120", "-0.0790"),
    ("0.2233", "0.5316", "0.0952"),
)
SCRIPT_HALF_LIFE = "22.662578"
BOOK_HALF_LIFE_DAYS = "23"

#: Example 2.8's printout, script line 125, and location 1368.
SCRIPT_APR = "0.125739"
SCRIPT_SHARPE = "1.391310"
BOOK_APR_PERCENT = "12.6"
BOOK_SHARPE = "1.4"


def portfolio_value(
    prices: NDArray[np.float64], weights: NDArray[np.float64]
) -> NDArray[np.float64]:
    """``sum(repmat(w', [T 1]) .* y3, 2)``: each day's price of one unit of the portfolio."""
    return (prices * weights[None, :]).sum(axis=1)


def linear_mean_reversion(
    prices: NDArray[np.float64], weights: NDArray[np.float64], lookback: int
) -> NDArray[np.float64]:
    """Example 2.8's daily returns, lines 115 to 119 of the script.

    The portfolio holds ``numUnits`` units, minus its z-score over
    ``lookback`` rows, so each ETF's position in dollars is ``numUnits`` times
    its weight times its price. Each day earns yesterday's positions times
    today's simple returns, summed, over yesterday's gross. The sums are
    MATLAB's ``sum``, which a NaN turns to NaN, and a NaN day is then 0, which
    covers the first ``lookback`` rows.
    """
    value = portfolio_value(prices, weights)
    with np.errstate(invalid="ignore", divide="ignore"):
        units = -(value - moving_avg(value, lookback)) / moving_std(value, lookback)
        positions = units[:, None] * weights[None, :] * prices
        held = backshift(1, positions)
        before = backshift(1, prices)
        pnl = np.sum(held * (prices - before) / before, axis=1)
        daily = pnl / np.sum(np.abs(held), axis=1)
    return np.where(np.isnan(daily), 0.0, daily)


@dataclass(frozen=True)
class Strategy:
    """Example 2.8 on one portfolio: its weights, lookback and daily returns."""

    weights: NDArray[np.float64]
    half_life: float
    lookback: int
    daily: NDArray[np.float64]

    @property
    def apr(self) -> float:
        return compounded_apr(self.daily)

    @property
    def sharpe(self) -> float:
        return plain_sharpe(self.daily)


def strategy(prices: NDArray[np.float64], weights: NDArray[np.float64]) -> Strategy:
    """Lines 98 to 124: the portfolio, its half-life, the lookback, and the returns."""
    half_life = ou_half_life(portfolio_value(prices, weights))
    lookback = int(round_half_away(half_life))
    return Strategy(
        weights=weights,
        half_life=half_life,
        lookback=lookback,
        daily=linear_mean_reversion(prices, weights, lookback),
    )


@dataclass(frozen=True)
class Cadf:
    """``cadf(y, x, 0, lags)``'s t-statistic, AR(1) estimate and observation count."""

    t: float
    ar1: float
    nobs: int


@dataclass(frozen=True)
class EtfCointegration:
    """All three examples on the three ETFs, and the rows beside them.

    ``reversed_cadf`` swaps the legs, EWA on EWC. ``reordered_triplet`` runs
    the triplet's Johansen test with the columns as EWA, EWC, IGE. ``adf``
    holds a plain ADF t-statistic with a constant and one lag for each ETF on
    its own.
    """

    days: pd.DatetimeIndex
    hedge_ratio: float
    cadf: Cadf
    reversed_cadf: Cadf
    pair: Johansen
    triplet: Johansen
    reordered_triplet: Johansen
    eigenvector_half_lives: tuple[float, ...]
    strategy: Strategy
    adf: dict[str, float]


def etf_cointegration(closes: pd.DataFrame) -> EtfCointegration:
    """Run the script and the rows beside it on a frame holding EWA, EWC and IGE."""
    x, y, z = (closes[s].to_numpy(dtype=float) for s in (X, Y, Z))
    pair = np.column_stack([y, x])
    triplet = np.column_stack([y, x, z])
    tested = johansen(triplet, JOHANSEN_P, JOHANSEN_K)
    return EtfCointegration(
        days=closes.index,
        hedge_ratio=float(ols(y, np.column_stack([x, np.ones(len(x))])).beta[0]),
        cadf=Cadf(*lesage_cadf(y, x, CADF_LAGS)),
        reversed_cadf=Cadf(*lesage_cadf(x, y, CADF_LAGS)),
        pair=johansen(pair, JOHANSEN_P, JOHANSEN_K),
        triplet=tested,
        reordered_triplet=johansen(np.column_stack([x, y, z]), JOHANSEN_P, JOHANSEN_K),
        eigenvector_half_lives=tuple(
            ou_half_life(portfolio_value(triplet, tested.eigenvectors[:, i])) for i in range(3)
        ),
        strategy=strategy(triplet, tested.eigenvectors[:, 0]),
        adf={
            s: adf_tstat(closes[s].to_numpy(dtype=float), lags=1, constant=True)[0]
            for s in (X, Y, Z)
        },
    )


def read_sources(data_dir: Path | None = None) -> tuple[list[VintageEntry], pd.DataFrame]:
    """The three ETFs' closes, refused if any spans a scale break over the file."""
    members, closes = load_panel(SOURCE_FILE, data_dir=data_dir)
    read = [m for m in members if m.symbol in TRIPLET]
    frame = closes[[X, Y, Z]]
    refuse_window_crossing_a_break(
        [(m, frame[m.symbol]) for m in read], start=frame.index[0], end=frame.index[-1]
    )
    return read, frame


def _verdict(value: float, printed: str) -> str:
    return (
        "reproduced"
        if matches(value, printed)
        else f"did not reproduce, gap {gap(value, printed):+g}"
    )


def _relations(test: Johansen, statistic: str) -> str:
    return ", ".join(f"{test.relations(statistic, level)} at {level}%" for level in (90, 95, 99))


def report(members: list[VintageEntry], result: EtfCointegration) -> None:
    """Print the vintage, each printed figure beside the computed one, and the rows beside them."""
    s = result.strategy
    print("EWA, EWC and IGE, Algorithmic Trading's Examples 2.6 to 2.8")
    print(f"  vintage  {panel_line(members)}: {', '.join(m.symbol for m in members)}")
    print(
        f"  window   {result.days[0].date()} to {result.days[-1].date()}, "
        f"{len(result.days)} trading days"
    )
    print(f"  tests    cadf(EWC, EWA, 0, {CADF_LAGS}), johansen(., {JOHANSEN_P}, {JOHANSEN_K})")
    print()
    rows = [
        ("2.6 CADF t-statistic, EWC on EWA", result.cadf.t, SCRIPT_CADF_T),
        ("2.6 CADF AR(1) estimate", result.cadf.ar1, SCRIPT_CADF_AR1),
        *(
            (f"2.7 pair trace, r <= {i}", result.pair.trace[i], printed)
            for i, printed in enumerate(SCRIPT_PAIR_TRACE)
        ),
        *(
            (f"2.7 pair eigen, r <= {i}", result.pair.eigen[i], printed)
            for i, printed in enumerate(SCRIPT_PAIR_EIGEN)
        ),
        *(
            (f"2.7 triplet trace, r <= {i}", result.triplet.trace[i], printed)
            for i, printed in enumerate(SCRIPT_TRIPLET_TRACE)
        ),
        *(
            (f"2.7 triplet eigen, r <= {i}", result.triplet.eigen[i], printed)
            for i, printed in enumerate(SCRIPT_TRIPLET_EIGEN)
        ),
        *(
            (f"2.7 triplet eigenvalue {i + 1}", result.triplet.eigenvalues[i], printed)
            for i, printed in enumerate(SCRIPT_EIGENVALUES)
        ),
        ("2.7 half-life, days", s.half_life, SCRIPT_HALF_LIFE),
        ("2.8 APR", s.apr, SCRIPT_APR),
        ("2.8 Sharpe", s.sharpe, SCRIPT_SHARPE),
    ]
    print(f"  {'Figure':<36} {'Computed':>12}  {'Chan':>12}  Verdict")
    for label, value, printed in rows:
        print(f"  {label:<36} {value:>12.6f}  {printed:>12}  {_verdict(value, printed)}")
    print()
    print("  The first eigenvector, rows EWC, EWA, IGE, against Chan's with its sign flipped")
    for row, printed in zip(result.triplet.eigenvectors[:, 0], SCRIPT_EIGENVECTORS, strict=True):
        print(f"    {row:>9.4f}  {-float(printed[0]):>9.4f}")
    print()
    print("  Relations found, counting rejected nulls up to the first that is not")
    print(f"    pair trace     {_relations(result.pair, 'trace')}")
    print(f"    pair eigen     {_relations(result.pair, 'eigen')}")
    print(f"    triplet trace  {_relations(result.triplet, 'trace')}")
    print(f"    triplet eigen  {_relations(result.triplet, 'eigen')}")
    print()
    print("Beside the replication. No book prints these, so none carries a verdict.")
    print(f"  hedge ratio, EWC on EWA with an intercept   {result.hedge_ratio:.4f}")
    print(f"  CADF t-statistic with the legs reversed      {result.reversed_cadf.t:.4f}")
    print(
        "  triplet trace with columns EWA, EWC, IGE     "
        + ", ".join(f"{v:.3f}" for v in result.reordered_triplet.trace)
    )
    print(
        "  half-life of each eigenvector, days          "
        + ", ".join(f"{h:.2f}" for h in result.eigenvector_half_lives)
    )
    print(
        "  ADF with a constant and one lag, each alone  "
        + ", ".join(f"{sym} {t:.2f}" for sym, t in result.adf.items())
        + f", against {ADF_CRIT_CONST['10%']} at 90%"
    )
    first = int(np.flatnonzero(s.daily)[0])
    print(
        f"  lookback {s.lookback} days, first return on {result.days[first].date()}, "
        f"{np.count_nonzero(s.daily)} days with a return"
    )
    print()
    print(
        f"  Annualised over {TRADING_DAYS} days with no cost. The eigenvector is fitted "
        "on the days it trades, so the APR is in-sample."
    )
    print("  Exploratory. docs/replication-log.md carries the verdicts.")


def run(data_dir: Path | None = None) -> EtfCointegration:
    """Read the three ETFs, guard them, run the script, and print the report."""
    members, closes = read_sources(data_dir)
    result = etf_cointegration(closes)
    report(members, result)
    return result


def main() -> None:
    argparse.ArgumentParser(
        description="EWA, EWC and IGE, Algorithmic Trading's Examples 2.6 to 2.8"
    ).parse_args()
    try:
        run()
    except VintageUnavailable as unavailable:
        # A refusal that names the source reaches the reader as one line, the
        # way chan.khandani_lo_book_two.main does it.
        raise SystemExit(str(unavailable)) from unavailable


if __name__ == "__main__":
    main()
