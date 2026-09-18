"""The GLD/GDX and KO/PEP cointegration replications from Chan's book.

Reproduces the pair-trading examples in Ernest Chan, *Quantitative Trading*
(rev. ed.): a hedge-ratio regression, an Engle-Granger / CADF unit-root test on
the residual spread, and an Ornstein-Uhlenbeck half-life. Every number this
module computes is frozen by ``tests/test_pair_cointegration.py``, which is the
single authority for any figure the prose quotes.

These are replications, which means they are exploratory by construction.
Reproducing a published figure spends the sample on a hypothesis someone else
chose, so it says whether the number reproduces and nothing more.

``docs/design.md`` carries the reasoning: why the hedge ratio drifted while the
verdict held, why Chan's own archived files are committed beside the yfinance
ones, and what the KO/PEP counter-example answers. The notes below stay
operational, naming which run each constant belongs to.

Three steps, all backed by ``ithildincore.timeseries``:

1. Hedge ratio. OLS of A's close on B's close with an intercept, which is the
   cointegrating regression the CADF test uses. The residual
   ``z = A - beta*B - alpha`` is the candidate stationary spread.
   ``origin=True`` additionally reports a separate through-origin slope, which
   is the one Chan quotes as 1.6766. It is display-only and does not enter the
   test.
2. Engle-Granger / CADF test. An Augmented Dickey-Fuller unit-root test on that
   residual spread, compared to MacKinnon critical values for the
   residual-based test with N=2 series. More negative than the critical value
   rejects the no-cointegration null.
3. Ornstein-Uhlenbeck half-life. OLS of the daily change in the spread on the
   lagged spread level gives the mean-reversion speed theta, and the half-life
   ``ln(2)/theta`` is the expected holding period.

**The trap this module exists to make visible.** Chan prints a hedge ratio and
a test statistic near each other, and they are not one result. His
``cadf(GLD, GDX, 0, 1)`` runs the with-intercept test and reports the t-stat
and half-life. His ``ols(GLD, GDX)`` quotes a through-origin hedge of 1.6766.
The two also come from two windows of the GLD-GDX intersection: the full
2006-05-23 to 2007-11-30 span (``--ch7``, reported t=-3.357, better than 95%)
and the first 252 trading days (``--ch3``, reported t=-3.18, better than 90%).
Reading them as one result produces the wrong number twice over.

The ``ch7`` and ``ch3`` names are first-edition shorthand, after that
edition's Chapter 7 and its Chapter 3 example on page 63 with
``example3_6_1.m``. The 2021 revised edition puts both printouts in one
Chapter 7 example, and says at Kindle location 1862 that Chapter 3 defers the
training-set analysis rather than performing it. The names are kept because
the windows they stand for are unambiguous, and ``docs/design.md`` carries the
reasoning. What does not depend on the edition is the specification split
above: it comes from ``cadf`` and ``ols`` being different functions, not from
the book's chapter numbering.

**The vintage.** This module matches the t-stat and half-life closely, at
t=-3.45 on the full window and -3.09 on the training set, and lands the
through-origin hedge near 1.6379. The exact 1.6766 is a lost data vintage.
Yahoo rescales adjusted close by every later dividend, so no modern download
reaches it, and independent reproductions converge near 1.6379 too. Raw close
is the closest modern proxy to Chan's 2007-era adjusted series, since GDX had
barely any dividends stripped out by then, so ``--ch7`` and ``--ch3`` read raw.

**The counter-example.** Chan's KO vs PEP run (``--ko-pep``, Example 7.3) is
the mirror image. ``return_correlation`` and the CADF run together to show a
pair that is significantly correlated in daily returns (r = 0.4849) yet does
not cointegrate (CADF t = -2.14, fails to reject). Correlation is the
short-term co-movement of returns. Cointegration is the long-term tethering of
price levels. A pair can have one without the other. Unlike GLD/GDX, KO/PEP
reproduces Chan's printed figures exactly, because it runs on his own committed
companion data rather than on a modern download.

Usage:
    python -m chan.pair_cointegration                   # GLD vs GDX, full history
    python -m chan.pair_cointegration --ch7             # Chan's Ch.7 full-window run
    python -m chan.pair_cointegration --ch3             # Chan's Ch.3 (p.63) run
    python -m chan.pair_cointegration --ko-pep          # Chan's KO/PEP counter-example
    python -m chan.pair_cointegration --a SPY --b IVV --origin
    python -m chan.pair_cointegration --selftest        # verify the math
"""

from __future__ import annotations

import argparse
import math
import warnings
from dataclasses import dataclass

import numpy as np
import pandas as pd
from ithildincore.timeseries import (
    ADF_CRIT_CONST,
    EG_CRIT_N2,
    adf_tstat,
    ols,
    ou_half_life,
)
from numpy.typing import NDArray
from scipy import stats

from chan.paths import data_path


@dataclass(frozen=True)
class CointResult:
    """Everything the CLI needs to report one pair's cointegration test.

    ``hedge_ratio``, ``intercept`` and ``spread`` come from the with-intercept
    cointegrating regression that drives the CADF test. ``origin_hedge`` is the
    separate through-origin slope Chan quotes as 1.6766, filled only when
    asked. It does not enter the test.
    """

    hedge_ratio: float
    intercept: float
    spread: NDArray[np.float64]
    adf_stat: float
    nobs: int
    half_life: float
    origin_hedge: float | None = None


@dataclass(frozen=True)
class RollingCoint:
    """A rolling-window CADF scan of one pair, as parallel arrays.

    One entry per window, indexed by the window's end position in the aligned
    series. A single full-history verdict hides regime changes: a pair can
    cointegrate for a stretch and then detach, and the whole-span statistic
    averages the two away. This turns the CADF t-statistic into a time series,
    so when the relationship held becomes visible. ``origin_hedge`` carries
    Chan's through-origin hedge in each window, and its drift is the signal
    that the relationship moved.
    """

    end_idx: NDArray[np.int64]
    adf_stat: NDArray[np.float64]
    origin_hedge: NDArray[np.float64]
    half_life: NDArray[np.float64]


def engle_granger(
    a: NDArray[np.float64],
    b: NDArray[np.float64],
    lags: int = 1,
    *,
    origin: bool = False,
) -> CointResult:
    """Two-step Engle-Granger cointegration test.

    The test always uses the statistically standard with-intercept form: fit
    ``a = alpha + beta*b + z``, run the ADF on the mean-zero residual ``z``
    with no deterministic term, compared to the with-constant N=2 critical
    values, and measure the OU half-life. This is what Chan's
    ``cadf(GLD, GDX, 0, 1)`` computes, and its t-stat and half-life match the
    book.

    ``origin=True`` additionally reports a through-origin hedge ratio from a
    separate no-constant OLS, which is Chan's ``ols(GLD, GDX)`` and the source
    of his 1.6766. It is display-only and does not change the test.
    """
    design = np.column_stack([b, np.ones(len(b))])
    fit = ols(a, design)
    hedge_ratio = float(fit.beta[0])
    intercept = float(fit.beta[1])
    spread = fit.resid
    adf_stat, nobs = adf_tstat(spread, lags=lags, constant=False)
    origin_hedge = float(ols(a, b.reshape(-1, 1)).beta[0]) if origin else None
    return CointResult(
        hedge_ratio=hedge_ratio,
        intercept=intercept,
        spread=spread,
        adf_stat=adf_stat,
        nobs=nobs,
        half_life=ou_half_life(spread),
        origin_hedge=origin_hedge,
    )


def return_correlation(
    a: NDArray[np.float64], b: NDArray[np.float64]
) -> tuple[float, float, float]:
    """Pearson correlation of the two legs' daily returns, with a significance
    test. This is Chan's ``corrcoef(dailyReturns)`` in ``example7_3.m``.

    It is the other half of the KO/PEP counter-example, and the reason
    correlation and cointegration are not the same thing. Correlation measures
    the short-term co-movement of returns: do the two move together day to day?
    Cointegration, in ``engle_granger`` above, measures the long-term tethering
    of price levels: does a fixed combination of the two stay range-bound? A
    pair can have either without the other. KO and PEP are significantly
    correlated at r near 0.48 yet do not cointegrate.

    Returns ``(r, t, p)``: the correlation, its t-statistic
    ``r*sqrt((n-2)/(1-r^2))``, and the two-sided p-value under ``t_{n-2}``.
    """
    ra = np.diff(a) / a[:-1]
    rb = np.diff(b) / b[:-1]
    r = float(np.corrcoef(ra, rb)[0, 1])
    n = len(ra)
    t = r * math.sqrt((n - 2) / (1.0 - r * r))
    p = float(2.0 * stats.t.sf(abs(t), df=n - 2))
    return r, t, p


def rolling_cointegration(
    a: NDArray[np.float64],
    b: NDArray[np.float64],
    *,
    window: int = 252,
    step: int = 21,
    lags: int = 1,
) -> RollingCoint:
    """Slide a fixed window across a pair and run the CADF test in each.

    Re-runs ``engle_granger`` on every ``window``-day slice, about one trading
    year by default, stepped by ``step`` days, about a month, so the CADF
    t-statistic and the through-origin hedge become time series. Each window's
    entry is stamped with the index of its last day in ``end_idx``, which the
    caller maps back to a date through the aligned frame. This is what makes
    "cointegration is a property of a window" checkable rather than a caveat:
    over the full GLD/GDX history only 31 of 231 windows clear even the 10%
    bar, and they cluster before 2015.
    """
    ends: list[int] = []
    adf: list[float] = []
    hedge: list[float] = []
    half: list[float] = []
    n = len(a)
    for e in range(window, n + 1, step):
        r = engle_granger(a[e - window : e], b[e - window : e], lags=lags, origin=True)
        oh = r.origin_hedge  # origin=True always fills it; narrow for the checker
        ends.append(e - 1)
        adf.append(r.adf_stat)
        hedge.append(oh if oh is not None else float("nan"))
        half.append(r.half_life)
    return RollingCoint(
        end_idx=np.array(ends, dtype=np.int64),
        adf_stat=np.array(adf, dtype=np.float64),
        origin_hedge=np.array(hedge, dtype=np.float64),
        half_life=np.array(half, dtype=np.float64),
    )


def load_close(ticker: str, *, unadjusted: bool = False, chan: bool = False) -> pd.Series:
    """Load a ticker's daily close from a committed vintage, date-indexed.

    Two sources, told apart by filename:

    - The yfinance set, the default: ``data/{ticker}_20yr_prices.csv`` carries
      Yahoo's dividend-adjusted close, and ``..._20yr_prices_unadjusted.csv``
      carries the raw close when ``unadjusted=True``.
    - Chan's book-companion set, with ``chan=True``: ``data/{ticker}_chan.csv``
      is the adjusted-close column of Chan's own ``.xls`` for that ticker.
      There is no unadjusted twin, so ``unadjusted`` is ignored here.

    All are written with a three-row header (Price/Close, Ticker/SYM,
    Date/blank). Rather than hard-code the skip count, every leading row whose
    first field is not a parseable date is dropped, so either header shape
    loads.

    The basis decides the levels. GLD pays no distributions, so its adjusted
    close already equals its raw close, while GDX's dividends put today's
    adjusted history about 15% below raw. Chan's 2007-vintage adjusted close
    was near raw, since GDX had paid little by then, so raw is the closest
    modern proxy for reproducing the book. That is why ``--ch7``, ``--ch3`` and
    ``--unadjusted`` read it.
    """
    # Provenance lives in data/vintages.jsonl, which names each file's vendor,
    # symbol, price basis, span, date, row count and sha256. data/README.md says
    # the same in prose. The four yfinance files were not all taken on one day,
    # so the date is per file rather than per directory. All of them are frozen
    # on purpose. Nothing regenerates these eight, and the pinned tests freeze
    # these exact bytes against each source's drifting vintage, so a re-download
    # would fail the replication rather than pass it quietly.
    if chan:
        path = data_path(f"{ticker.lower()}_chan.csv")
    else:
        suffix = "_20yr_prices_unadjusted.csv" if unadjusted else "_20yr_prices.csv"
        path = data_path(f"{ticker.lower()}{suffix}")
    raw = pd.read_csv(path, header=None, names=["date", "close"], usecols=[0, 1])
    with warnings.catch_warnings():
        # The header rows ("Date", "Ticker") do not parse as dates, and coerce
        # drops them to NaT. pandas warns about the mixed formats, expected here.
        warnings.simplefilter("ignore", UserWarning)
        dates = pd.to_datetime(raw["date"], errors="coerce")
    mask = dates.notna()
    series = pd.Series(
        pd.to_numeric(raw["close"][mask], errors="coerce").to_numpy(dtype=float),
        index=pd.DatetimeIndex(dates[mask]),
        name=ticker.upper(),
    )
    return series.sort_index()


def aligned_closes(
    a: str,
    b: str,
    *,
    start: str | None = None,
    end: str | None = None,
    unadjusted: bool = False,
    chan: bool = False,
) -> pd.DataFrame:
    """Inner-join two tickers' closes on their common trading days.

    Optionally clipped to the inclusive window ``[start, end]``, both
    ``YYYY-MM-DD``. ``chan=True`` loads both legs from Chan's committed
    companion data.
    """
    joined = pd.concat(
        [
            load_close(a, unadjusted=unadjusted, chan=chan),
            load_close(b, unadjusted=unadjusted, chan=chan),
        ],
        axis=1,
        join="inner",
    ).dropna()
    joined.columns = [a.upper(), b.upper()]
    if start is not None:
        joined = joined.loc[joined.index >= pd.Timestamp(start)]
    if end is not None:
        joined = joined.loc[joined.index <= pd.Timestamp(end)]
    return joined


def _verdict(stat: float, crit: dict[str, float]) -> str:
    """The most demanding level, meaning the lowest percentage, at which the
    statistic rejects."""
    for level in ("1%", "5%", "10%"):
        if stat < crit[level]:
            return f"REJECTS the no-cointegration null at the {level} level"
    return "fails to reject -- no evidence of cointegration"


def run(
    a: str,
    b: str,
    lags: int,
    *,
    start: str | None = None,
    end: str | None = None,
    unadjusted: bool = False,
    origin: bool = False,
    reference: str | None = None,
    show_correlation: bool = False,
    chan: bool = False,
) -> None:
    """Load the pair, run the test, and print a book-style report."""
    closes = aligned_closes(a, b, start=start, end=end, unadjusted=unadjusted, chan=chan)
    if len(closes) < 30:
        raise SystemExit(
            f"only {len(closes)} common trading days in the window -- need >= 30 "
            f"(check --start/--end and that both price files exist)"
        )
    av = closes[a.upper()].to_numpy(dtype=float)
    bv = closes[b.upper()].to_numpy(dtype=float)
    result = engle_granger(av, bv, lags=lags, origin=origin)

    span_start = closes.index[0].date()
    span_end = closes.index[-1].date()
    au, bu = a.upper(), b.upper()
    # Name the source, not just the adjustment. Chan's companion files carry an
    # adjusted close too, and reporting it as Yahoo's would put the wrong
    # vintage next to the number.
    if chan:
        basis = "Chan's companion-file adjusted closes"
    elif unadjusted:
        basis = "raw / unadjusted closes"
    else:
        basis = "Yahoo dividend-adjusted closes"

    print(
        "Pair cointegration -- daily closes   "
        "(pinned replication; see tests/test_pair_cointegration.py)"
    )
    print(f"  A = {au}   B = {bu}")
    print(f"  Span: {span_start} .. {span_end}   (N = {len(closes)} trading days)")
    print(f"  Price basis: {basis} (both legs)")
    if reference is not None:
        print(f"  Book reference: {reference}")
    print()
    print(f"Cointegrating regression (OLS with intercept):  {au} = alpha + beta*{bu} + z")
    print(
        f"  hedge ratio beta = {result.hedge_ratio:.4f}    intercept alpha = {result.intercept:.4f}"
    )
    print(f"  => spread z = {au} - {result.hedge_ratio:.4f}*{bu} {-result.intercept:+.4f}")
    if result.origin_hedge is not None:
        note = "   <- Chan quotes this (his ols convention)" if reference is not None else ""
        print(
            f"  through-origin hedge (no intercept, ols({au},{bu})) = "
            f"{result.origin_hedge:.4f}{note}"
        )
    print()
    print(f"Engle-Granger / CADF test (ADF on residual spread, {lags} lag, no const):")
    print(f"  ADF t-statistic = {result.adf_stat:.4f}   (nobs = {result.nobs})")
    crit = EG_CRIT_N2
    print(
        f"  MacKinnon crit (N=2, const, asymptotic):  "
        f"1% {crit['1%']}   5% {crit['5%']}   10% {crit['10%']}"
    )
    print(f"  Verdict: {_verdict(result.adf_stat, crit)}")
    print()
    print("Ornstein-Uhlenbeck half-life:")
    if math.isinf(result.half_life):
        print("  spread does not mean-revert (non-negative OU slope) -- half-life undefined")
    else:
        print(f"  half-life = {result.half_life:.1f} trading days")
    print()
    if show_correlation:
        r, t, p = return_correlation(av, bv)
        sig = "significant" if p < 0.05 else "not significant"
        print("Daily-return correlation (Chan's corrcoef check):")
        print(f"  r = {r:.4f}   (t = {t:.1f}, p = {p:.2e} -> {sig})")
        print("  Correlated returns do not imply cointegrated prices: the pair")
        print("  can co-move day to day yet drift apart in the long run.")
        print()
    print("Caveats: asymptotic critical values (a fitted hedge ratio biases the")
    print("stat toward rejection) and a single fixed hedge ratio over the whole")
    print("span. Cointegration is window-dependent, so a borderline verdict")
    print("deserves scrutiny across other windows.")


def selftest() -> None:
    """Verify the ADF and cointegration arithmetic on synthetic series with
    known answers. Deterministic and seeded; prints OK or raises."""
    rng = np.random.default_rng(0)
    n = 2000

    # 1. Pure random walk -> unit root -> ADF should NOT reject.
    walk = np.cumsum(rng.standard_normal(n))
    rw_stat, _ = adf_tstat(walk, lags=1, constant=True)
    assert rw_stat > ADF_CRIT_CONST["10%"], f"random walk wrongly rejected: {rw_stat:.3f}"

    # 2. Stationary AR(1), phi=0.2 -> strong mean reversion -> ADF REJECTS.
    ar = np.zeros(n)
    for t in range(1, n):
        ar[t] = 0.2 * ar[t - 1] + rng.standard_normal()
    ar_stat, _ = adf_tstat(ar, lags=1, constant=True)
    assert ar_stat < ADF_CRIT_CONST["1%"], f"stationary AR(1) not rejected: {ar_stat:.3f}"

    # 3. Cointegrated pair: shared random-walk factor + small noise -> REJECTS.
    factor = np.cumsum(rng.standard_normal(n))
    a = factor + rng.standard_normal(n) * 0.5
    b = 0.5 * factor + rng.standard_normal(n) * 0.5
    coint = engle_granger(a, b, lags=1)
    assert coint.adf_stat < EG_CRIT_N2["1%"], (
        f"cointegrated pair not detected: {coint.adf_stat:.3f}"
    )
    assert 0 < coint.half_life < 50, f"implausible half-life: {coint.half_life:.2f}"

    # 4. Independent random walks: NOT cointegrated -> fails to reject.
    ind_a = np.cumsum(rng.standard_normal(n))
    ind_b = np.cumsum(rng.standard_normal(n))
    ind = engle_granger(ind_a, ind_b, lags=1)
    assert ind.adf_stat > EG_CRIT_N2["10%"], (
        f"independent walks wrongly cointegrated: {ind.adf_stat:.3f}"
    )

    print("selftest OK")
    print(f"  random walk ADF        = {rw_stat:+.3f}  (not < {ADF_CRIT_CONST['10%']}, correct)")
    print(f"  AR(1) phi=0.2 ADF      = {ar_stat:+.3f}  (< {ADF_CRIT_CONST['1%']}, correct)")
    print(
        f"  cointegrated pair ADF  = {coint.adf_stat:+.3f}  "
        f"(< {EG_CRIT_N2['1%']}, correct); half-life {coint.half_life:.1f}d"
    )
    print(f"  independent walks ADF  = {ind.adf_stat:+.3f}  (not < {EG_CRIT_N2['10%']}, correct)")


# Chan's GLD/GDX cadf example, reconstructed from his own MATLAB source
# (example7_2.m, example3_6_1.m) and companion GLD.xls/GDX.xls. There are two
# runs on two windows, both through-origin, since his ols/cadf add no intercept:
#   Ch.7 (example7_2.m): the FULL GLD-GDX intersection 2006-05-23..2007-11-30.
#     Reported hedge 1.6766, cadf t=-3.357, "better than 95%".
#   Ch.3 (example3_6_1.m, book p.63): drops the last 60 days, then runs cadf on
#     the first 252 days = 2006-05-23..~2007-05-23. Reported t=-3.18, "better
#     than 90%", the numbers cited on page 63.
# Chan used the ADJUSTED close, but the exact 1.6766 is a lost data vintage.
# Yahoo rescales adjusted close by every later dividend, so his 2007-era series
# differs from any modern download. Independent reproductions converge on a
# hedge near 1.6379. Raw close is the closest modern proxy to his 2007-vintage
# adjusted series, since GDX had barely any dividends stripped out back then,
# so --ch7 uses raw plus origin over the full window.
BOOK_START = "2006-05-23"
BOOK_END = "2007-11-30"
BOOK_TRAIN_END = "2007-05-23"  # first ~252 trading days -> the Ch.3 / p.63 run
BOOK_REF_FULL = "example7_2.m (Ch.7): hedge 1.6766, cadf t=-3.357, ~95%"
BOOK_REF_TRAIN = "example3_6_1.m (Ch.3, p.63): cadf t=-3.18, ~90%"

# Chan's KO/PEP counter-example (example7_3.m, Ch.7): correlated but NOT
# cointegrated, the demonstration that correlation and cointegration differ.
# Unlike GLD/GDX this runs on Chan's OWN committed companion data.
# data/ko_chan.csv and pep_chan.csv are the adjusted-close columns of his
# KO.xls/PEP.xls, so the replication hits his printed figures exactly:
#   the full KO-PEP intersection 1977-01-03..2008-01-18 (7833 obs after 1 lag),
#   through-origin hedge 1.0114, cadf t=-2.14 (above the 10% crit, so it fails
#   to reject), daily-return correlation 0.4849 (significant).
# Provenance: KO.xls/PEP.xls last saved by Ernest Chan 2008-01-23, from the
# public book-code mirror github.com/egorpe/EPChan-QuantitativeTrading
#   KO.xls  sha256 33c09f771c141793bf6c4fa355299f7aec4fe51b330b692064760d2efa3e87bc
#   PEP.xls sha256 fdc0deefb3beeaec4dacf729f63be3457bed59df7589a312b93badb58ced7053
# A frozen vintage with no regeneration script, like the GLD/GDX CSVs. yfinance
# would drift off 1.0114 and 0.4849 the way it drifts off GLD/GDX's 1.6766.
KOPEP_REF = "example7_3.m (Ch.7): hedge 1.0114, cadf t=-2.14, corr 0.4849 -- NOT cointegrated"

# Chan's GLD/GDX companion data is ALSO committed, as the lost-vintage receipt:
# data/gld_chan.csv and gdx_chan.csv, the adjusted close of his GLD.xls/GDX.xls
# from the same egorpe mirror, last saved by Ernest Chan 2007-12-02. Loaded via
# aligned_closes(..., chan=True) and pinned by TestGldGdxChanArchive, they give
# an origin hedge of 1.6395 and cadf t=-3.52 over 2006-05-23..2007-11-30, which
# is NOT the book's 1.6766 / -3.357. Even Chan's own saved files miss his
# printed number: the 2007 book-run adjusted-close vintage is gone. There is no
# CLI mode for this, and the yfinance --ch7 path stays the interactive GLD/GDX
# replication.
#   GLD.xls sha256 3b866a8a43bf52f915ed73209ab542434c85ef033e5b9f01d57ff508820f4563
#   GDX.xls sha256 757aa109b0617bbe1d6983456c4c397ffdc946e417ce3ac98e3ef255d740df34


def main() -> None:
    ch7_window = f"{BOOK_START}..{BOOK_END}"
    ch3_window = f"{BOOK_START}..{BOOK_TRAIN_END}"
    parser = argparse.ArgumentParser(description="Daily cointegration test for a pair of tickers")
    parser.add_argument("--a", default="GLD", help="dependent-leg ticker (default: GLD)")
    parser.add_argument("--b", default="GDX", help="independent-leg ticker (default: GDX)")
    parser.add_argument(
        "--lags", type=int, default=1, help="ADF augmenting lags (default: 1, as in the book)"
    )
    parser.add_argument(
        "--start", default=None, help="window start YYYY-MM-DD (default: full history)"
    )
    parser.add_argument("--end", default=None, help="window end YYYY-MM-DD (default: full history)")
    parser.add_argument(
        "--unadjusted",
        action="store_true",
        help="use raw closes instead of dividend-adjusted (the closest modern proxy to the book)",
    )
    parser.add_argument(
        "--origin",
        action="store_true",
        help="also report the through-origin hedge (Chan's ols convention; the test "
        "stays with-intercept)",
    )
    parser.add_argument(
        "--ch7",
        action="store_true",
        help=f"reproduce Chan's Chapter 7 full-window run ({ch7_window}, raw, origin)",
    )
    parser.add_argument(
        "--ch3",
        action="store_true",
        help=f"reproduce Chan's Chapter 3 (p.63) run ({ch3_window}, raw, origin)",
    )
    parser.add_argument(
        "--ko-pep",
        dest="ko_pep",
        action="store_true",
        help="reproduce Chan's KO/PEP counter-example (example7_3.m): correlated but "
        "NOT cointegrated",
    )
    parser.add_argument(
        "--correlation",
        action="store_true",
        help="also report the daily-return correlation (Chan's corrcoef check)",
    )
    parser.add_argument(
        "--selftest", action="store_true", help="verify the ADF/coint math on synthetic data"
    )
    args = parser.parse_args()

    if args.selftest:
        selftest()
        return

    a_tick, b_tick = args.a, args.b
    start, end, unadjusted, origin, reference = (
        args.start,
        args.end,
        args.unadjusted,
        args.origin,
        None,
    )
    show_correlation = args.correlation
    chan = False
    if args.ch7:
        start, end, unadjusted, origin, reference = (
            BOOK_START,
            BOOK_END,
            True,
            True,
            BOOK_REF_FULL,
        )
    elif args.ch3:
        start, end, unadjusted, origin, reference = (
            BOOK_START,
            BOOK_TRAIN_END,
            True,
            True,
            BOOK_REF_TRAIN,
        )
    elif args.ko_pep:
        # KO/PEP runs on Chan's committed adjusted-close data over the full
        # intersection, with the correlation check alongside the CADF.
        a_tick, b_tick = "KO", "PEP"
        origin, show_correlation, reference, chan = True, True, KOPEP_REF, True
    run(
        a_tick,
        b_tick,
        args.lags,
        start=start,
        end=end,
        unadjusted=unadjusted,
        origin=origin,
        reference=reference,
        show_correlation=show_correlation,
        chan=chan,
    )


if __name__ == "__main__":
    main()
