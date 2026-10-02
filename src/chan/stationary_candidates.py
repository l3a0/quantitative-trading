"""Chan's other stationary candidates, tested on committed vintages.

Having worked GLD against GDX, Chan names three more places a stationary
spread should live, at Kindle location 3951. He names them rather than working
them, so there is no published figure to match, and what this module produces
is a finding on whether his claim holds for the stand-ins this repo chose.
[Issue 16](https://github.com/l3a0/quantitative-trading/issues/16) carries the
rules every candidate obeys, and each candidate's own issue carries its scope.
One candidate runs here today.

**The fixed-income pair.** Chan's sentence is that one can "long and short
bonds by the same issuer but of different maturities". TLT holds Treasuries
maturing in twenty years or more and IEF holds Treasuries maturing in seven to
ten, so the two are one issuer at two maturities.
[Issue 136](https://github.com/l3a0/quantitative-trading/issues/136) named
both in writing before anything was downloaded, and the owner confirmed them
on 2026-09-18. Each fund is a rolling basket rather than a bond, which is the
step between the stand-ins and the claim.

Both legs are read on the raw basis, meaning split-adjusted and not
dividend-adjusted. Most of a bond fund's return is its distributions, so an
adjusted pair would drift apart by the difference in what the two maturities
pay rather than by anything about whether their prices are tied.

Four specification choices are fixed here rather than defaulted, because each
one can move a borderline statistic across a critical value.

1. **The lag is 1.** It is Chan's ``cadf(..., 0, 1)``, the default of
   :func:`chan.pair_cointegration.engle_granger`, and the lag
   :func:`chan.pair_cointegration.rolling_cointegration` runs, so the full span
   and the scan read one specification. A lag that leaves autocorrelation in
   the test's own residuals reads its statistic against critical values that do
   not apply, so each fit also gets
   :func:`chan.pair_cointegration.residual_check`, and the search for the first
   lag count whose residuals pass stops at :func:`schwert_ceiling`.
2. **The scale is levels**, as in every other run in this repo.
3. **Both legs take a turn as the dependent one.** The test regresses one leg
   on the other and is not symmetric, and Chan names no dependent leg, so
   choosing the orientation that rejects would be a search.
   :data:`ORIENTATIONS` holds both and every number is reported for each.
4. **The rolling window is 252 days stepped by 21**, matching the GLD/GDX scan
   so the two are comparable. The scan describes the whole span. No window that
   happens to reject is a finding on its own.

The command line takes no window. A window option is the knob that would let a
reader pick one that rejects, and the full span is the only one declared.

The result is exploratory. The sample was spent on a claim Chan stated and on
stand-ins this repo chose, so it can say whether these two funds cointegrate
over this span and nothing about bonds in general. It is not a replication,
because Chan printed no number, and the word for its conclusion is a finding.
``docs/replication-log.md`` Entry 5 carries it, and
``tests/test_stationary_candidates.py`` is the single authority for every
number any prose surface quotes about it.

Usage:
    python -m chan.stationary_candidates
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from ithildincore.timeseries import EG_CRIT_N2
from numpy.typing import NDArray

from chan.pair_cointegration import (
    CointResult,
    ResidualCheck,
    RollingCoint,
    _verdict,
    engle_granger,
    residual_check,
    rolling_cointegration,
)
from chan.series import WindowCrossesScaleBreak, aligned_closes, vintage_line
from chan.vintage import VintageUnavailable

#: The two stand-ins, long maturity first. Neither is the dependent leg until
#: :data:`ORIENTATIONS` says so.
LONG, INTERMEDIATE = "TLT", "IEF"

#: Every run reports both, in this order.
ORIENTATIONS = ((LONG, INTERMEDIATE), (INTERMEDIATE, LONG))

LAGS = 1
WINDOW = 252
STEP = 21

#: The Breusch-Godfrey cut a residual check passes at, the one Entry 1 of the
#: replication log uses. Passing also needs every autocorrelation inside the
#: white-noise band.
RESIDUAL_PASS_P = 0.10

BOOK_REF = "Kindle location 3951: fixed-income instruments can be found to be cointegrating"


def schwert_ceiling(n: int) -> int:
    """The largest lag count the residual search tries, for ``n`` observations.

    Schwert's rule, ``12 * (n / 100) ** 0.25``, rounded up the way
    ``statsmodels`` rounds it when ``adfuller`` is given no ``maxlag``.
    ``TestLagSettingDetour`` pins that rounding on the Chapter 3 window. A long
    span pushes the first passing count far past the Chapter windows' 6 and 10,
    and a search with no ceiling is a search, so the ceiling is fixed before
    any statistic is read.
    """
    return math.ceil(12 * (n / 100) ** 0.25)


def residuals_pass(check: ResidualCheck) -> bool:
    """Whether a fit's residuals pass both halves of the check."""
    return check.breusch_godfrey_p > RESIDUAL_PASS_P and not check.outside


def first_passing(spread: NDArray[np.float64], ceiling: int) -> ResidualCheck | None:
    """The fit at the smallest lag count up to ``ceiling`` whose residuals pass.

    ``None`` when none does, which is a result rather than a reason to search
    further.
    """
    for lags in range(ceiling + 1):
        check = residual_check(spread, lags)
        if residuals_pass(check):
            return check
    return None


@dataclass(frozen=True)
class Orientation:
    """Every number one orientation of the pair produces."""

    dependent: str
    independent: str
    fit: CointResult
    at_lag: ResidualCheck
    ceiling: int
    passing: ResidualCheck | None
    scan: RollingCoint


def measure_orientation(closes: pd.DataFrame, dependent: str, independent: str) -> Orientation:
    """Fit, check and scan one orientation of an aligned pair."""
    a = closes[dependent].to_numpy(dtype=float)
    b = closes[independent].to_numpy(dtype=float)
    fit = engle_granger(a, b, lags=LAGS)
    ceiling = schwert_ceiling(len(closes))
    return Orientation(
        dependent=dependent,
        independent=independent,
        fit=fit,
        at_lag=residual_check(fit.spread, LAGS),
        ceiling=ceiling,
        passing=first_passing(fit.spread, ceiling),
        scan=rolling_cointegration(a, b, window=WINDOW, step=STEP, lags=LAGS),
    )


def fixed_income(*, data_dir: Path | None = None) -> tuple[pd.DataFrame, tuple[Orientation, ...]]:
    """Read both raw vintages, join them, and measure both orientations."""
    closes = aligned_closes(LONG, INTERMEDIATE, unadjusted=True, data_dir=data_dir)
    return closes, tuple(measure_orientation(closes, a, b) for a, b in ORIENTATIONS)


def _orientation(o: Orientation) -> None:
    fit = o.fit
    print(f"{o.dependent} on {o.independent}:  {o.dependent} = alpha + beta*{o.independent} + z")
    print(f"  hedge ratio beta = {fit.hedge_ratio:.4f}    intercept alpha = {fit.intercept:.4f}")
    print(
        f"  Engle-Granger / CADF (ADF on the residual spread, {LAGS} lag, no const):  "
        f"t = {fit.adf_stat:.4f}   "
        f"(nobs = {fit.nobs})"
    )
    print(f"  {_verdict(fit.adf_stat, EG_CRIT_N2)}")
    if math.isinf(fit.half_life):
        print("  spread does not mean-revert (non-negative OU slope) -- half-life undefined")
    else:
        print(f"  half-life = {fit.half_life:.1f} trading days")
    outside = ", ".join(str(lag) for lag in o.at_lag.outside) or "none"
    print(
        f"  residual check at {LAGS} lag:  Breusch-Godfrey p = {o.at_lag.breusch_godfrey_p:.4f}, "
        f"lags outside the band: {outside}"
    )
    if o.passing is None:
        print(f"  no lag count from 0 to {o.ceiling} leaves residuals that pass")
    else:
        print(
            f"  first lag count from 0 to {o.ceiling} whose residuals pass: {o.passing.lags}, "
            f"where t = {o.passing.adf_stat:.4f}"
        )
        print(f"    {_verdict(o.passing.adf_stat, EG_CRIT_N2)}")
    stats = o.scan.adf_stat
    print(
        f"  rolling scan, {WINDOW}-day windows stepped by {STEP}:  "
        f"{int((stats < EG_CRIT_N2['10%']).sum())} of {len(stats)} clear the 10% bar, "
        f"{int((stats < EG_CRIT_N2['5%']).sum())} clear 5%"
    )
    print()


def report(closes: pd.DataFrame, orientations: tuple[Orientation, ...]) -> None:
    """Print the finding for both orientations, with the vintage behind it."""
    print(
        "Chan's fixed-income candidate -- daily closes   "
        "(exploratory finding; see tests/test_stationary_candidates.py)"
    )
    print(f"  Claim: {BOOK_REF}")
    print(f"  Stand-ins: {LONG} (20+ year Treasuries) and {INTERMEDIATE} (7-10 year Treasuries)")
    print(
        f"  Span: {closes.index[0].date()} .. {closes.index[-1].date()}   "
        f"(N = {len(closes)} trading days)"
    )
    print("  Price basis: raw closes, adjusted for splits and not for dividends (both legs)")
    # Read off the manifest entries the join resolved, so these lines are the
    # record rather than a restatement of it.
    for entry in closes.attrs["vintages"]:
        print(f"  {entry.symbol} vintage: {vintage_line(entry)}")
    crit = EG_CRIT_N2
    print(
        f"  MacKinnon crit (N=2, const, asymptotic):  "
        f"1% {crit['1%']}   5% {crit['5%']}   10% {crit['10%']}"
    )
    print()
    for o in orientations:
        _orientation(o)
    print("Both orientations print because the test is not symmetric and Chan names no")
    print("dependent leg, so reporting one would be a choice made after the fact. The")
    print("rolling scan describes the span, and no window in it is a finding on its own.")
    print()
    print("This is exploratory. The sample was spent on a claim Chan stated and on two")
    print("stand-ins chosen for it, so it says whether these two funds cointegrate over")
    print("this span and nothing about bonds in general. Chan printed no number, so")
    print("nothing here is compared against one.")
    print("docs/replication-log.md Entry 5 carries the finding.")


def run(*, data_dir: Path | None = None) -> None:
    """Measure the pair and print the report."""
    closes, orientations = fixed_income(data_dir=data_dir)
    report(closes, orientations)


def main() -> None:
    argparse.ArgumentParser(
        description="Chan's fixed-income stationary candidate, TLT against IEF, on committed "
        "raw vintages. It takes no window, because the full span is the only one declared."
    ).parse_args()
    try:
        run()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refusal:
        # Both are raised inside the join, and a refusal naming which vintage
        # or which dates is worth nothing at the bottom of a pandas traceback.
        # `chan.risk_parity.main` records what happened when a module reading
        # a pair named only the first.
        raise SystemExit(str(refusal)) from refusal


if __name__ == "__main__":
    main()
