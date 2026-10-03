"""Chan's other stationary candidates, tested on committed vintages.

Having worked GLD against GDX, Chan names three more places stationarity
should live, at Kindle location 3951. He names them rather than working them,
so there is no published figure to match.
[Issue 16](https://github.com/l3a0/quantitative-trading/issues/16) carries the
rules every candidate obeys, and each candidate's own issue carries its scope.
Two candidates run here today, and they produce different kinds of result.

**The CAD/AUD cross rate is a replication.** Chan names the series itself and
says it "is quite stationary", which is a definite claim about one named rate.
The owner ruled on 2026-10-02 that it takes the claim route, so it carries a
verdict against a criterion
[issue 135](https://github.com/l3a0/quantitative-trading/issues/135) declared
before any statistic was computed. Its section below says what that criterion
is and why each specification choice was made.

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

The command line takes no window for either candidate. A window option is the
knob that would let a reader pick one that rejects, and each candidate's issue
declared exactly one: the full common span here, and :data:`TEST_START` to the
last row for the cross rate.

The fixed-income result is exploratory. The sample was spent on a claim Chan
stated and on stand-ins this repo chose, so it can say whether these two funds
cointegrate over this span and nothing about bonds in general. It is not a
replication, because Chan printed no number and named no instrument, and the
word for its conclusion is a finding. ``docs/replication-log.md`` Entry 5
carries it.

**The cross rate** is ``CADAUD=X``, yfinance's quote of the rate Chan names,
tested as one series with nothing estimated from it. So it is an augmented
Dickey-Fuller test against ``ADF_CRIT_CONST``, whose 5% bar is -2.86, and not
the pair engine, whose residual-based bar pays for a hedge ratio this test
never fits. Three specification choices are fixed here.

1. **The scale is the log.** ``CADAUD=X`` quotes Australian dollars per
   Canadian dollar and Chan writes CAD/AUD without saying which way round. The
   test on the log gives one answer in either direction, and the test on the
   level does not.
2. **The lag is 1**, with the residual check beside it and the same search to
   :func:`schwert_ceiling` the pair uses, so both candidates in this module read
   one rule. The check fits a constant here, because the test does.
3. **The deterministic term is a constant and no trend**, because Chan's claim
   is that the level is stationary.

The test reads from :data:`TEST_START`, the first row after a 90-weekday gap in
the vendor's history, so no lagged regression treats four months as one day.
The vintage keeps the rows before the gap. The verdict is "reproduced" when the
statistic at lag 1 and the statistic at the first lag count whose residuals
pass are both below the 5% bar, and "did not reproduce" otherwise, including
when no count up to the ceiling passes. The rolling scan and the half-life are
reported beside it and decide nothing. :func:`window_power` measures what the
scan can see: it runs the same scan over simulated series that truly revert at
the rate's half-life, on a specification declared on issue 212 before it ran.
``docs/replication-log.md`` Entry 6 carries the verdict.

Both results are exploratory, and ``tests/test_stationary_candidates.py`` is
the single authority for every number any prose surface quotes about either.

Usage:
    python -m chan.stationary_candidates                # both candidates
    python -m chan.stationary_candidates fixed-income
    python -m chan.stationary_candidates cross-rate
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from ithildincore.timeseries import ADF_CRIT_CONST, EG_CRIT_N2, adf_tstat, ou_half_life
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
from chan.series import WindowCrossesScaleBreak, aligned_closes, load_vintage, vintage_line
from chan.vintage import VintageEntry, VintageUnavailable

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

#: The fixed-income candidate's claim. The cross rate's is :data:`CROSS_RATE_REF`.
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


def first_passing(
    spread: NDArray[np.float64], ceiling: int, *, regression: str = "n"
) -> ResidualCheck | None:
    """The fit at the smallest lag count up to ``ceiling`` whose residuals pass.

    ``None`` when none does, which is a result rather than a reason to search
    further. ``regression`` is passed to
    :func:`chan.pair_cointegration.residual_check`, so a series tested with a
    constant is searched with one.
    """
    for lags in range(ceiling + 1):
        check = residual_check(spread, lags, regression=regression)
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


# ---- the CAD/AUD cross rate ----

#: yfinance's quote of the rate Chan names, Australian dollars per Canadian dollar.
CROSS_RATE = "CADAUD=X"

#: The download the pins were computed from. A second download of the rate
#: would otherwise make the run refuse and name both, which is right for a
#: caller who did not say which, and wrong for the run whose numbers the suite
#: pins. ``chan.kelly_leverage`` names its SPY vintage the same way.
CROSS_RATE_DATED = "2026-10-02"

#: The first row after the 90 weekdays the vendor returned nothing for. A
#: constant rather than a search for the gap, so a later download that fills
#: the gap cannot move the window with nothing in the diff to say so.
TEST_START = "2007-08-06"

#: The gap :data:`TEST_START` steps over, inclusive. The suite holds the
#: vintage to it, because the reason for the start is a fact about the rows.
GAP = ("2007-04-02", "2007-08-03")

#: The level the verdict is read at, fixed in issue 135 before any statistic.
VERDICT_LEVEL = "5%"

CROSS_RATE_REF = "Kindle location 3951: the CAD/AUD cross-currency rate is quite stationary"


@dataclass(frozen=True)
class RollingADF:
    """The ADF statistic and OU half-life on each window of one series."""

    end_idx: NDArray[np.int64]
    adf_stat: NDArray[np.float64]
    half_life: NDArray[np.float64]


def rolling_adf(
    series: NDArray[np.float64], *, window: int = WINDOW, step: int = STEP, lags: int = LAGS
) -> RollingADF:
    """Slide a fixed window across one series and run the ADF with a constant in each.

    The univariate counterpart of
    :func:`chan.pair_cointegration.rolling_cointegration`, on the same window
    and step so the scans are comparable. A series shorter than ``window``
    yields no windows and raises nothing, which is why the command line takes
    no window of its own.
    """
    ends: list[int] = []
    stats: list[float] = []
    halves: list[float] = []
    for e in range(window, len(series) + 1, step):
        piece = series[e - window : e]
        ends.append(e - 1)
        stats.append(adf_tstat(piece, lags, constant=True)[0])
        halves.append(ou_half_life(piece))
    return RollingADF(
        end_idx=np.array(ends, dtype=np.int64),
        adf_stat=np.array(stats, dtype=np.float64),
        half_life=np.array(halves, dtype=np.float64),
    )


@dataclass(frozen=True)
class CrossRate:
    """Every number the cross-rate test produces, with the vintage behind it."""

    entry: VintageEntry
    log_rate: pd.Series
    adf_stat: float
    nobs: int
    at_lag: ResidualCheck
    ceiling: int
    passing: ResidualCheck | None
    half_life: float
    scan: RollingADF

    @property
    def reproduced(self) -> bool:
        """Whether Chan's claim holds under the criterion issue 135 declared."""
        bar = ADF_CRIT_CONST[VERDICT_LEVEL]
        return self.adf_stat < bar and self.passing is not None and self.passing.adf_stat < bar


def measure_cross_rate(entry: VintageEntry, close: pd.Series) -> CrossRate:
    """Clip a rate to the test window, take its log, and run every test on it."""
    window = close.loc[close.index >= pd.Timestamp(TEST_START)]
    log_rate = np.log(window)
    values = log_rate.to_numpy(dtype=float)
    stat, nobs = adf_tstat(values, LAGS, constant=True)
    ceiling = schwert_ceiling(len(values))
    return CrossRate(
        entry=entry,
        log_rate=log_rate,
        adf_stat=stat,
        nobs=nobs,
        at_lag=residual_check(values, LAGS, regression="c"),
        ceiling=ceiling,
        passing=first_passing(values, ceiling, regression="c"),
        half_life=ou_half_life(values),
        scan=rolling_adf(values),
    )


def cross_rate(*, dated: str = CROSS_RATE_DATED, data_dir: Path | None = None) -> CrossRate:
    """Read the raw CADAUD=X vintage and measure it.

    ``unadjusted=True`` is what names the ``raw`` basis the rate is recorded
    under. The default flags ask for an adjusted series this repo does not hold
    for the rate, and refuse.
    """
    entry, close = load_vintage(CROSS_RATE, unadjusted=True, dated=dated, data_dir=data_dir)
    return measure_cross_rate(entry, close)


#: The seed and path count of the window-power simulation, declared on issue 212
#: before any number was computed.
POWER_SEED = 20261002
POWER_PATHS = 1000


@dataclass(frozen=True)
class WindowPower:
    """How often a series that truly reverts rejects in the rate's scan.

    Each path is a Gaussian AR(1) with mean zero and ``phi = 1 - ln 2 / h``,
    which is the reversion speed :func:`ou_half_life` reads as a half-life of
    ``h``. It starts from the stationary distribution, runs as long as the
    rate's test window, and is scanned the way the rate is. The arrays hold one
    entry per path.
    """

    half_life: float
    phi: float
    length: int
    windows: int
    clear10: NDArray[np.int64]
    clear5: NDArray[np.int64]
    whole_rejects5: NDArray[np.bool_]

    def share_of_windows(self, level: str) -> float:
        counts = {"10%": self.clear10, "5%": self.clear5}[level]
        return float(counts.mean() / self.windows)


def simulated_paths(half_life: float, length: int, paths: int, seed: int) -> NDArray[np.float64]:
    """``paths`` AR(1) series of ``length`` days, one per row.

    The innovation scale is 1 because the ADF statistic does not depend on it.
    The first value is drawn from the stationary distribution, so no burn-in is
    needed and every day of a path is a day of a stationary series.
    """
    phi = 1.0 - math.log(2.0) / half_life
    rng = np.random.default_rng(seed)
    shocks = rng.standard_normal((paths, length))
    z = np.empty((paths, length))
    z[:, 0] = shocks[:, 0] / math.sqrt(1.0 - phi**2)
    for t in range(1, length):
        z[:, t] = phi * z[:, t - 1] + shocks[:, t]
    return z


def window_power(
    half_life: float, length: int, *, paths: int = POWER_PATHS, seed: int = POWER_SEED
) -> WindowPower:
    """Scan simulated stationary series the way the rate's scan runs.

    The windows are :func:`rolling_adf`'s, 252 days stepped by 21 at one lag
    with a constant, and so is the statistic. Only the statistic is computed,
    because the half-life ``rolling_adf`` also fits in each window would double
    the run time and the simulation reports nothing about it.
    ``tests/test_stationary_candidates.py`` holds that the two agree.
    """
    z = simulated_paths(half_life, length, paths, seed)
    ends = range(WINDOW, length + 1, STEP)
    clear10 = np.empty(paths, dtype=np.int64)
    clear5 = np.empty(paths, dtype=np.int64)
    whole = np.empty(paths, dtype=bool)
    for i, path in enumerate(z):
        stats = np.array([adf_tstat(path[e - WINDOW : e], LAGS, constant=True)[0] for e in ends])
        clear10[i] = int((stats < ADF_CRIT_CONST["10%"]).sum())
        clear5[i] = int((stats < ADF_CRIT_CONST["5%"]).sum())
        whole[i] = adf_tstat(path, LAGS, constant=True)[0] < ADF_CRIT_CONST["5%"]
    return WindowPower(
        half_life=half_life,
        phi=1.0 - math.log(2.0) / half_life,
        length=length,
        windows=len(ends),
        clear10=clear10,
        clear5=clear5,
        whole_rejects5=whole,
    )


def unit_root_line(stat: float) -> str:
    """The most demanding level at which ``stat`` rejects a unit root.

    Written for this test rather than borrowed from
    :func:`chan.pair_cointegration._verdict`, which names the no-cointegration
    null. This test fits no hedge ratio, so there is no cointegration in it.
    """
    for level in ("1%", "5%", "10%"):
        if stat < ADF_CRIT_CONST[level]:
            return f"REJECTS the unit-root null at the {level} level"
    return "fails to reject the unit-root null at 10%"


def report_cross_rate(m: CrossRate) -> None:
    """Print the cross-rate verdict with the vintage, window and criterion behind it."""
    days = m.log_rate.index
    crit = ADF_CRIT_CONST
    bar = crit[VERDICT_LEVEL]
    print(
        "Chan's CAD/AUD cross rate -- daily closes   "
        "(replication; see tests/test_stationary_candidates.py)"
    )
    print(f"  Claim: {CROSS_RATE_REF}")
    print(f"  Series: {CROSS_RATE}, Australian dollars per Canadian dollar, on the log scale")
    print("  Price basis: raw, the vendor's close, which no adjustment touches")
    print(f"  {CROSS_RATE} vintage: {vintage_line(m.entry)}")
    print(
        f"  Test window: {days[0].date()} .. {days[-1].date()}   (N = {len(days)} days, "
        f"starting after the vendor's gap from {GAP[0]} to {GAP[1]})"
    )
    print(
        f"  ADF crit (constant, no trend):  1% {crit['1%']}   5% {crit['5%']}   10% {crit['10%']}"
    )
    print()
    print(f"  ADF on log(rate), {LAGS} lag, constant:  t = {m.adf_stat:.4f}   (nobs = {m.nobs})")
    print(f"  {unit_root_line(m.adf_stat)}")
    if math.isinf(m.half_life):
        print("  rate does not mean-revert (non-negative OU slope) -- half-life undefined")
    else:
        print(f"  half-life = {m.half_life:.1f} trading days")
    outside = ", ".join(str(lag) for lag in m.at_lag.outside) or "none"
    print(
        f"  residual check at {LAGS} lag:  Breusch-Godfrey p = {m.at_lag.breusch_godfrey_p:.4f}, "
        f"lags outside the band: {outside}"
    )
    if m.passing is None:
        print(f"  no lag count from 0 to {m.ceiling} leaves residuals that pass")
    else:
        print(
            f"  first lag count from 0 to {m.ceiling} whose residuals pass: {m.passing.lags}, "
            f"where t = {m.passing.adf_stat:.4f}"
        )
        print(f"    {unit_root_line(m.passing.adf_stat)}")
    stats = m.scan.adf_stat
    print(
        f"  rolling scan, {WINDOW}-day windows stepped by {STEP}:  "
        f"{int((stats < crit['10%']).sum())} of {len(stats)} clear the 10% bar, "
        f"{int((stats < crit['5%']).sum())} clear 5%"
    )
    print()
    passing = "none passes" if m.passing is None else f"t = {m.passing.adf_stat:.4f}"
    print(
        f"Verdict: {'REPRODUCED' if m.reproduced else 'DID NOT REPRODUCE'}. The criterion, "
        f"declared before any statistic, is that the lag-{LAGS} statistic and the statistic at"
    )
    print(
        f"the first residual-clean lag count are both below the {VERDICT_LEVEL} bar of {bar}. "
        f"Here they are t = {m.adf_stat:.4f} and {passing}."
    )
    print("The rolling scan and the half-life describe the window and decide nothing.")
    print()
    print("A replication against data is exploratory by construction. The sample was spent")
    print("on a claim Chan stated about one named rate, so this says whether that rate was")
    print("stationary over this window and nothing about whether trading it would pay.")
    print("docs/replication-log.md Entry 6 carries the verdict.")


def run_cross_rate(*, dated: str = CROSS_RATE_DATED, data_dir: Path | None = None) -> None:
    """Measure the cross rate and print the report."""
    report_cross_rate(cross_rate(dated=dated, data_dir=data_dir))


CANDIDATES = ("fixed-income", "cross-rate")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Chan's stationary candidates at Kindle location 3951, on committed "
        "vintages. Neither takes a window, because each declared exactly one."
    )
    parser.add_argument(
        "candidate",
        nargs="?",
        choices=CANDIDATES,
        help="which candidate to run (default: both)",
    )
    parser.add_argument(
        "--dated",
        default=None,
        help=f"which {CROSS_RATE} download to read, by its date (default: {CROSS_RATE_DATED})",
    )
    args = parser.parse_args()
    if args.dated is not None and args.candidate == "fixed-income":
        # Accepting it and reading nothing would let a reader believe a date
        # moved the fixed-income numbers.
        parser.error("--dated names a CADAUD=X download and applies only to cross-rate")
    dated = CROSS_RATE_DATED if args.dated is None else args.dated
    try:
        if args.candidate in (None, "fixed-income"):
            run()
        if args.candidate is None:
            print()
        if args.candidate in (None, "cross-rate"):
            run_cross_rate(dated=dated)
    except (VintageUnavailable, WindowCrossesScaleBreak) as refusal:
        # Both are raised while reading, and a refusal naming which vintage or
        # which dates is worth nothing at the bottom of a pandas traceback.
        # `chan.risk_parity.main` records what happened when a module reading
        # a pair named only the first.
        raise SystemExit(str(refusal)) from refusal


if __name__ == "__main__":
    main()
