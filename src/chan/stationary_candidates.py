"""Chan's other stationary candidates, tested on committed vintages.

Having worked GLD against GDX, Chan names three more places stationarity
should live, at Kindle location 3951. He names them rather than working them,
so there is no published figure to match.
[Issue 16](https://github.com/l3a0/quantitative-trading/issues/16) carries the
rules every candidate obeys, and each candidate's own issue carries its scope.
All three run here, and they produce different kinds of result.

**The CAD/AUD cross rate is a replication.** Chan names the series itself and
says it "is quite stationary", which is a definite claim about one named rate.
The owner ruled on 2026-10-02 that it takes the claim route, so it carries a
verdict against a criterion
[issue 135](https://github.com/l3a0/quantitative-trading/issues/135) declared
before any statistic was computed. Its section below says what that criterion
is and why each specification choice was made.

**The calendar spreads are a replication too.** Chan calls them "the simplest
examples of cointegrating futures pairs", and a June and July natural gas pair
is a member of that class rather than a stand-in for it. The owner ruled on
2026-10-03 that each commodity carries a verdict, against a criterion
[issue 137](https://github.com/l3a0/quantitative-trading/issues/137) declared
before any statistic. Its section below says what that criterion is.

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

The command line takes no window for any candidate. A window option is the
knob that would let a reader pick one that rejects, and each candidate's issue
declared exactly one: the full common span here, :data:`TEST_START` to the
last row for the cross rate, and each pair's days in the nearest four for the
calendar spreads.

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
   :func:`schwert_ceiling` the pair uses, so the fixed-income pair and the
   cross rate read one rule. The check fits a constant here, because the test does.
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

**The calendar spreads** are every adjacent pair of delivery months, contract m
against m+1, of natural gas and of RBOB gasoline on EIA's nearest four
contracts. :mod:`chan.futures` says which numbered file holds each contract on
each day. No pair overlaps long enough to test alone, so each commodity is one
batch, and no pair's result is a finding about that pair.

1. **The days.** A pair reads every trading day both contracts sit in the
   nearest four, less a six-day :func:`guard_band` around the window's ends
   and its two interior expiries, so an expiry rule one day wrong misreads
   only days the band drops. A day either file lacks is dropped, not filled.
2. **The test** is the fixed-income pair's: Engle-Granger on levels at one
   lag, in both orientations. A pair rejects only when both clear the 10% bar.
3. **The verdict.** A commodity's statistic is the share of its pairs that
   reject. Short windows and pairs sharing a contract make 10% the wrong
   reference for that share, so :func:`null_shares` simulates 1,000 sets of
   random walks on the same days. The claim reproduces for a commodity when
   its share is strictly above the 975th of those shares, a family-wise 5%
   split across the two commodities.
4. **The correction.** The null issue 137 declared made every contract an
   independent walk. Real neighbouring contracts move almost together, and
   then requiring both orientations is barely stricter than one, so the
   declared null set the bar too low. The owner ruled on 2026-10-03 to
   re-judge against walks that correlate as the files' legs do,
   :func:`leg_correlation`, and to report the declared verdict beside it.

:func:`power_shares` runs the same pipeline on pairs that truly cointegrate at
a 36-day half-life, and with each orientation's share and the residual check it
describes the batch and decides nothing. ``docs/replication-log.md`` Entry 15
carries the verdicts.

All three results are exploratory, and ``tests/test_stationary_candidates.py``
is the single authority for every number any prose surface quotes about them.

Usage:
    python -m chan.stationary_candidates                # all three candidates
    python -m chan.stationary_candidates fixed-income
    python -m chan.stationary_candidates cross-rate
    python -m chan.stationary_candidates calendar-spread
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from ithildincore.timeseries import ADF_CRIT_CONST, EG_CRIT_N2, adf_tstat, ou_half_life
from numpy.typing import NDArray

from chan.futures import (
    NATURAL_GAS_CONTRACTS,
    RBOB_CONTRACTS,
    Product,
    contract_number,
    month_step,
    next_trading_day,
    settlements,
    trading_days,
)
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
    return _ar1(rng.standard_normal((paths, length)), phi)


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


# ---- calendar spreads ----

CALENDAR_REF = (
    "Kindle location 3951: the simplest cointegrating futures pairs are calendar spreads, "
    "one commodity at two expiration months"
)

#: The two commodities, each judged on its own. New York Harbor gasoline is out:
#: its four files each lack different days, so an adjacent pair keeps a median
#: of 42 days, which issue 137 measured before any statistic.
SPREAD_PRODUCTS = (NATURAL_GAS_CONTRACTS, RBOB_CONTRACTS)

#: A pair rejects only when both orientations clear this bar of ``EG_CRIT_N2``.
SPREAD_LEVEL = "10%"

#: The null, declared on issue 137 before any statistic: 1,000 simulated sets,
#: and a commodity reproduces when its share is strictly above the 975th of
#: them sorted from smallest. The 975th rather than the 950th splits a
#: family-wise 5% across the two commodities. The walks were corrected after
#: the result to correlate as the files do, which :func:`null_shares` says.
NULL_SEED = 20261003
NULL_SETS = 1000
NULL_RANK = 975

#: The power row, declared with the null. 36 trading days is the half-life Chan
#: reports for the 12-month crude oil calendar spread in *Algorithmic Trading*
#: Example 5.4.
SPREAD_POWER_SEED = 20261004
SPREAD_POWER_HALF_LIFE = 36.0

#: A delivery month as ``(year, month)``.
Month = tuple[int, int]


def spread_window(product: Product, near: Month) -> tuple[date, ...]:
    """Every trading day both contracts of the pair at ``near`` sit in the nearest four.

    The far contract enters contract 4 the day after the contract three months
    before the near one expires, and the window runs through the near
    contract's own last day, when it is contract 1 and the far one contract 2.
    """
    start = next_trading_day(product.last_trade(*month_step(*near, -3)))
    return trading_days(start, product.last_trade(*near))


def guard_band(product: Product, near: Month) -> frozenset[date]:
    """The six days of a window a one-day error in the expiry rule could misread.

    The window's first and last days, and each of the two expiries inside it
    with the day after. An expiry rule off by one day in either direction then
    reads a neighbouring contract only on days this drops.
    """
    window = spread_window(product, near)
    inside = [product.last_trade(*month_step(*near, k)) for k in (-2, -1)]
    return frozenset({window[0], window[-1], *inside, *(next_trading_day(d) for d in inside)})


@dataclass(frozen=True)
class SpreadPair:
    """One adjacent pair's window, the days it keeps, and both legs on those days.

    ``window`` is every trading day the calendar gives. ``kept`` drops the guard
    band and any day either file lacks, which is dropped rather than filled.
    """

    product: str
    near: Month
    window: tuple[date, ...]
    kept: tuple[date, ...]
    near_prices: NDArray[np.float64]
    far_prices: NDArray[np.float64]

    @property
    def far(self) -> Month:
        return month_step(*self.near, 1)

    @property
    def kept_index(self) -> NDArray[np.int64]:
        """Where each kept day sits in the window."""
        position = {day: i for i, day in enumerate(self.window)}
        return np.array([position[day] for day in self.kept], dtype=np.int64)


def spread_pair(product: Product, near: Month, *, data_dir: Path | None = None) -> SpreadPair:
    """Read both legs of the pair at ``near`` from whichever numbered file holds each."""
    files = product.files(data_dir=data_dir)
    window = spread_window(product, near)
    band = guard_band(product, near)
    kept: list[date] = []
    near_prices: list[float] = []
    far_prices: list[float] = []
    for day in window:
        if day in band:
            continue
        n = contract_number(day, *near, product.last_trade)
        a, b = files[n - 1].get(day), files[n].get(day)
        if a is None or b is None:
            continue
        kept.append(day)
        near_prices.append(float(a))
        far_prices.append(float(b))
    return SpreadPair(
        product=product.name,
        near=near,
        window=window,
        kept=tuple(kept),
        near_prices=np.array(near_prices),
        far_prices=np.array(far_prices),
    )


def declared_pairs(product: Product, *, data_dir: Path | None = None) -> tuple[SpreadPair, ...]:
    """Every adjacent pair whose whole window lies inside all four of the product's files."""
    spans = [sorted(f) for f in product.files(data_dir=data_dir)]
    first, last = max(s[0] for s in spans), min(s[-1] for s in spans)
    pairs, near = [], (first.year - 1, 1)
    while near <= (last.year + 1, 12):
        window = spread_window(product, near)
        if first <= window[0] and window[-1] <= last:
            pairs.append(spread_pair(product, near, data_dir=data_dir))
        near = month_step(*near, 1)
    return tuple(pairs)


def batched_engle_granger(a: NDArray[np.float64], b: NDArray[np.float64]) -> NDArray[np.float64]:
    """Engle-Granger's statistic at one lag for each row of ``a`` on the same row of ``b``.

    The with-intercept regression of ``a`` on ``b``, then the ADF regression
    of the residual's change on its lagged level and one lagged change, with no
    deterministic term, as :func:`chan.pair_cointegration.engle_granger` runs it
    through ``adfuller``. Solved in closed form across rows, because the null
    and the power row are each about 1.16 million fits and one call of the
    engine takes about a third of a millisecond.
    ``tests/test_stationary_candidates.py`` holds that the two agree.
    """
    am = a - a.mean(axis=1, keepdims=True)
    bm = b - b.mean(axis=1, keepdims=True)
    beta = (am * bm).sum(axis=1) / (bm * bm).sum(axis=1)
    z = am - beta[:, None] * bm
    dz = np.diff(z, axis=1)
    y, level, change = dz[:, 1:], z[:, 1:-1], dz[:, :-1]
    s11 = (level * level).sum(axis=1)
    s22 = (change * change).sum(axis=1)
    s12 = (level * change).sum(axis=1)
    s1y = (level * y).sum(axis=1)
    s2y = (change * y).sum(axis=1)
    det = s11 * s22 - s12 * s12
    coef_level = (s22 * s1y - s12 * s2y) / det
    coef_change = (s11 * s2y - s12 * s1y) / det
    resid = y - coef_level[:, None] * level - coef_change[:, None] * change
    variance = (resid * resid).sum(axis=1) / (y.shape[1] - 2)
    return coef_level / np.sqrt(variance * s22 / det)


def _both_reject(near: NDArray[np.float64], far: NDArray[np.float64]) -> NDArray[np.bool_]:
    bar = EG_CRIT_N2[SPREAD_LEVEL]
    return (batched_engle_granger(near, far) < bar) & (batched_engle_granger(far, near) < bar)


def leg_correlation(pairs: tuple[SpreadPair, ...]) -> float:
    """The median, over ``pairs``, of the correlation of the two legs' daily changes.

    Read on the days each pair keeps, so a dropped day contributes a two-day
    change, as it does to the test. It is the one input of the corrected null.
    """
    return float(
        np.median([np.corrcoef(np.diff(p.near_prices), np.diff(p.far_prices))[0, 1] for p in pairs])
    )


def null_shares(
    pairs: tuple[SpreadPair, ...],
    *,
    sets: int = NULL_SETS,
    seed: int = NULL_SEED,
    correlation: float = 0.0,
) -> NDArray[np.float64]:
    """The share of pairs rejecting in both orientations, in each of ``sets`` simulated sets.

    Every contract walks with unit Gaussian innovations on every trading day of
    its run, which is every day of each window it appears in. A contract shared
    by two pairs carries one walk through both. Each pair reads its walks on
    the days the real pair keeps, so a dropped day spans two steps as it does
    in the files.

    At ``correlation`` 0, the null issue 137 declared, every contract's walk is
    independent, drawn contract by contract in delivery order. Otherwise each
    walk is the square root of ``correlation`` times one walk shared by the
    whole commodity, drawn first over every day any run covers, plus the square
    root of one minus it times the contract's own. Any two contracts' daily
    changes then correlate at ``correlation``. That is the corrected null the
    owner ruled for on 2026-10-03, after the declared one was seen to leave out
    how closely neighbouring contracts move together.
    """
    for first, second in zip(pairs, pairs[1:], strict=False):
        if second.near != first.far:
            raise ValueError("the pairs must be adjacent and in delivery order")
    run: dict[Month, list[date]] = {}
    for pair in pairs:
        for month in (pair.near, pair.far):
            run.setdefault(month, [])
            run[month].extend(day for day in pair.window if day not in run[month])
    rng = np.random.default_rng(seed)
    shared: NDArray[np.float64] | None = None
    every: dict[date, int] = {}
    if correlation:
        every = {day: i for i, day in enumerate(sorted({d for days in run.values() for d in days}))}
        shared = np.cumsum(rng.standard_normal((sets, len(every))), axis=1)
    walks: dict[Month, tuple[dict[date, int], NDArray[np.float64]]] = {}
    count = np.zeros(sets)
    for pair in pairs:
        for month in (pair.near, pair.far):
            if month not in walks:
                days = sorted(run[month])
                walk = np.cumsum(rng.standard_normal((sets, len(days))), axis=1)
                if shared is not None:
                    common = shared[:, [every[day] for day in days]]
                    walk = math.sqrt(correlation) * common + math.sqrt(1 - correlation) * walk
                walks[month] = ({day: i for i, day in enumerate(days)}, walk)

        def legs(month: Month, pair: SpreadPair = pair) -> NDArray[np.float64]:
            position, walk = walks[month]
            return walk[:, [position[day] for day in pair.kept]]

        count += _both_reject(legs(pair.near), legs(pair.far))
        del walks[pair.near]
    return count / len(pairs)


def _ar1(shocks: NDArray[np.float64], phi: float) -> NDArray[np.float64]:
    """AR(1) paths, one per row, each starting from the stationary distribution."""
    z = np.empty_like(shocks)
    z[:, 0] = shocks[:, 0] / math.sqrt(1.0 - phi**2)
    for t in range(1, shocks.shape[1]):
        z[:, t] = phi * z[:, t - 1] + shocks[:, t]
    return z


def power_shares(
    pairs: tuple[SpreadPair, ...],
    *,
    sets: int = NULL_SETS,
    seed: int = SPREAD_POWER_SEED,
    half_life: float = SPREAD_POWER_HALF_LIFE,
) -> NDArray[np.float64]:
    """The share rejecting in both orientations when every pair truly cointegrates.

    Each pair is simulated on its own over its window: the far leg a Gaussian
    random walk, and the near leg the far leg plus a Gaussian AR(1) spread
    reverting at ``half_life``, unit innovations on both. Each pair draws its
    far leg's steps and then its spread's, in delivery order, and is read on
    the days the real pair keeps.
    """
    phi = 1.0 - math.log(2.0) / half_life
    rng = np.random.default_rng(seed)
    count = np.zeros(sets)
    for pair in pairs:
        n = len(pair.window)
        far = np.cumsum(rng.standard_normal((sets, n)), axis=1)
        near = far + _ar1(rng.standard_normal((sets, n)), phi)
        idx = pair.kept_index
        count += _both_reject(near[:, idx], far[:, idx])
    return count / len(pairs)


@dataclass(frozen=True)
class PairTest:
    """Both orientations of one pair, and the residual check of each at one lag."""

    pair: SpreadPair
    near_on_far: CointResult
    far_on_near: CointResult
    near_on_far_check: ResidualCheck
    far_on_near_check: ResidualCheck

    @property
    def rejects(self) -> bool:
        bar = EG_CRIT_N2[SPREAD_LEVEL]
        return self.near_on_far.adf_stat < bar and self.far_on_near.adf_stat < bar


def measure_pair(pair: SpreadPair) -> PairTest:
    """Engle-Granger at one lag on levels, near on far and far on near."""
    near_on_far = engle_granger(pair.near_prices, pair.far_prices, lags=LAGS)
    far_on_near = engle_granger(pair.far_prices, pair.near_prices, lags=LAGS)
    return PairTest(
        pair=pair,
        near_on_far=near_on_far,
        far_on_near=far_on_near,
        near_on_far_check=residual_check(near_on_far.spread, LAGS),
        far_on_near_check=residual_check(far_on_near.spread, LAGS),
    )


@dataclass(frozen=True)
class CalendarSpread:
    """One commodity's batch, both nulls, its power row, and the verdict they give.

    ``null`` is the corrected null, at the files' own correlation, and the
    verdict reads it. ``declared_null`` is the one issue 137 declared before any
    statistic, every contract independent, kept beside it because it was the
    registered criterion.
    """

    product: Product
    tests: tuple[PairTest, ...]
    correlation: float
    null: NDArray[np.float64]
    declared_null: NDArray[np.float64]
    power: NDArray[np.float64]

    def _share(self, hits: list[bool]) -> float:
        return sum(hits) / len(self.tests)

    @property
    def share(self) -> float:
        """The share of declared pairs rejecting in both orientations, the statistic judged."""
        return self._share([t.rejects for t in self.tests])

    @property
    def near_on_far_share(self) -> float:
        bar = EG_CRIT_N2[SPREAD_LEVEL]
        return self._share([t.near_on_far.adf_stat < bar for t in self.tests])

    @property
    def far_on_near_share(self) -> float:
        bar = EG_CRIT_N2[SPREAD_LEVEL]
        return self._share([t.far_on_near.adf_stat < bar for t in self.tests])

    @property
    def near_on_far_residuals_pass(self) -> float:
        return self._share([residuals_pass(t.near_on_far_check) for t in self.tests])

    @property
    def far_on_near_residuals_pass(self) -> float:
        return self._share([residuals_pass(t.far_on_near_check) for t in self.tests])

    @staticmethod
    def _cut(null: NDArray[np.float64]) -> float:
        return float(np.sort(null)[NULL_RANK - 1])

    @property
    def cut(self) -> float:
        """The 975th of the corrected null's shares sorted from smallest."""
        return self._cut(self.null)

    @property
    def declared_cut(self) -> float:
        """The 975th of the declared null's shares sorted from smallest."""
        return self._cut(self.declared_null)

    @property
    def null_median(self) -> float:
        return float(np.median(self.null))

    @property
    def declared_null_median(self) -> float:
        return float(np.median(self.declared_null))

    @property
    def null_reaching(self) -> int:
        """How many corrected null sets reach the real share. Added after the verdicts were seen.

        It decides nothing. It says how close the verdict sat to the cut, which
        the cut alone does not.
        """
        return int((self.null >= self.share).sum())

    @property
    def declared_null_reaching(self) -> int:
        """The same count under the declared null, added after the verdicts were seen."""
        return int((self.declared_null >= self.share).sum())

    @property
    def reproduced(self) -> bool:
        """Whether Chan's claim holds for this commodity against the corrected null."""
        return self.share > self.cut

    @property
    def reproduced_as_declared(self) -> bool:
        """Whether it holds against the declared null, which the corrected one replaced."""
        return self.share > self.declared_cut


def calendar_spread(product: Product, *, data_dir: Path | None = None) -> CalendarSpread:
    """Test every declared pair of one commodity and judge the batch against both nulls."""
    pairs = declared_pairs(product, data_dir=data_dir)
    correlation = leg_correlation(pairs)
    return CalendarSpread(
        product=product,
        tests=tuple(measure_pair(pair) for pair in pairs),
        correlation=correlation,
        null=null_shares(pairs, correlation=correlation),
        declared_null=null_shares(pairs),
        power=power_shares(pairs),
    )


def _month(month: Month) -> str:
    return f"{month[0]}-{month[1]:02d}"


def report_calendar_spread(results: tuple[CalendarSpread, ...]) -> None:
    """Print each commodity's verdict with the vintages, specification and nulls behind it."""
    bar = EG_CRIT_N2[SPREAD_LEVEL]
    print(
        "Chan's calendar spreads -- daily NYMEX settlements   "
        "(replication; see tests/test_stationary_candidates.py)"
    )
    print(f"  Claim: {CALENDAR_REF}")
    print("  Pairs: every adjacent pair of delivery months, contract m against m+1, read over")
    print("    the days both sit in EIA's nearest four, less the window's first and last days")
    print("    and each interior expiry with the day after")
    print("  Price basis: raw, EIA's settlement as the exchange printed it")
    print("  vintages:")
    for result in results:
        for symbol in result.product.symbols:
            print(f"    {vintage_line(settlements(symbol)[0])}")
    print(
        f"  Test: Engle-Granger on levels at {LAGS} lag, near on far and far on near. A pair "
        f"rejects when both clear the {SPREAD_LEVEL} bar of {bar}."
    )
    print(
        f"  Null: {NULL_SETS:,} sets of Gaussian random walks on the same days, seed "
        f"{NULL_SEED}, whose daily changes correlate as closely as the files' two legs do. "
        f"A commodity reproduces when its share is above the {NULL_RANK}th null share."
    )
    print("    This null was corrected after the result was seen, on the owner's ruling.")
    print("    The declared one made every contract independent, and is reported beside it.")
    print()
    for r in results:
        lengths = [len(t.pair.kept) for t in r.tests]
        n = len(r.tests)
        print(
            f"{r.product.name}: {n} pairs, near months "
            f"{_month(r.tests[0].pair.near)} .. {_month(r.tests[-1].pair.near)}"
        )
        print(
            f"  days a pair reads: {min(lengths)} to {max(lengths)}, "
            f"median {float(np.median(lengths)):g}"
        )
        print(
            f"  rejecting in both orientations: {round(r.share * n)} of {n}, "
            f"a share of {r.share:.4f}"
        )
        print(
            f"  each orientation alone at {SPREAD_LEVEL}: near on far {r.near_on_far_share:.4f}, "
            f"far on near {r.far_on_near_share:.4f}"
        )
        print(
            f"  residual check passing at {LAGS} lag: near on far "
            f"{r.near_on_far_residuals_pass:.4f}, far on near {r.far_on_near_residuals_pass:.4f}"
        )
        print(f"  correlation of the two legs' daily changes, median of pairs: {r.correlation:.4f}")
        print(
            f"  null shares: median {r.null_median:.4f}, {NULL_RANK}th of {NULL_SETS:,} {r.cut:.4f}"
        )
        print(
            f"  declared null, contracts independent: median {r.declared_null_median:.4f}, "
            f"{NULL_RANK}th {r.declared_cut:.4f}, "
            f"{'reproduced' if r.reproduced_as_declared else 'did not reproduce'}"
        )
        print(
            f"  null sets reaching {r.share:.4f}: {r.null_reaching} of {NULL_SETS:,}, and "
            f"{r.declared_null_reaching} under the declared null, a description added after "
            "the verdicts were seen"
        )
        print(
            f"  power, every pair reverting at a {SPREAD_POWER_HALF_LIFE:g}-day half-life "
            f"(seed {SPREAD_POWER_SEED}): mean share {float(r.power.mean()):.4f}"
        )
        print(
            f"  Verdict: {'REPRODUCED' if r.reproduced else 'DID NOT REPRODUCE'}. "
            f"{r.share:.4f} {'is' if r.reproduced else 'is not'} above {r.cut:.4f}."
        )
        print()
    print("Each commodity carries its own verdict, and there is no combined one. No pair's")
    print("result is a finding about that pair. The declared null, the orientation shares,")
    print("the residual check and the power row describe the batch and decide nothing.")
    print()
    print("A replication against data is exploratory by construction. A pass earns a")
    print("registration, not a headline.")
    print("docs/replication-log.md Entry 15 carries the verdicts.")


def run_calendar_spread(*, data_dir: Path | None = None) -> None:
    """Test both commodities and print the report."""
    report_calendar_spread(
        tuple(calendar_spread(product, data_dir=data_dir) for product in SPREAD_PRODUCTS)
    )


CANDIDATES = ("fixed-income", "cross-rate", "calendar-spread")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Chan's stationary candidates at Kindle location 3951, on committed "
        "vintages. None takes a window, because each declared exactly one."
    )
    parser.add_argument(
        "candidate",
        nargs="?",
        choices=CANDIDATES,
        help="which candidate to run (default: all three)",
    )
    parser.add_argument(
        "--dated",
        default=None,
        help=f"which {CROSS_RATE} download to read, by its date (default: {CROSS_RATE_DATED})",
    )
    args = parser.parse_args()
    if args.dated is not None and args.candidate in ("fixed-income", "calendar-spread"):
        # Accepting it and reading nothing would let a reader believe a date
        # moved the other candidates' numbers.
        parser.error("--dated names a CADAUD=X download and applies only to cross-rate")
    dated = CROSS_RATE_DATED if args.dated is None else args.dated
    try:
        if args.candidate in (None, "fixed-income"):
            run()
        if args.candidate is None:
            print()
        if args.candidate in (None, "cross-rate"):
            run_cross_rate(dated=dated)
        if args.candidate is None:
            print()
        if args.candidate in (None, "calendar-spread"):
            run_calendar_spread()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refusal:
        # Both are raised while reading, and a refusal naming which vintage or
        # which dates is worth nothing at the bottom of a pandas traceback.
        # `chan.risk_parity.main` records what happened when a module reading
        # a pair named only the first.
        raise SystemExit(str(refusal)) from refusal


if __name__ == "__main__":
    main()
