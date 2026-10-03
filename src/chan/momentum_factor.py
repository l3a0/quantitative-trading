"""The market and momentum factors on Chan's S&P 500 file, and whether their returns have momentum.

A factor model is usable for trading only if this period's factor return says
something about the next. Chan makes that claim at Kindle location 4014 of the
revised edition: "often factor returns are more stable than individual stock
returns—they exhibit stronger serial autocorrelations than individual stock's
returns. In other words, they have momentum." Two of the factors his section
names can be built from prices alone. The market factor, defined at location
3978, is the index's return over the bill rate. WML, winners minus losers,
defined at location 4004, longs the stocks "that previously had positive
returns" and shorts those "that previously had negative returns".
[Issue 22](https://github.com/l3a0/quantitative-trading/issues/22) carries the
plan, and every rule below was fixed there before any return was computed.

**The construction.**

1. The month-ends are the panel's rows whose next row falls in another month,
   :func:`chan.series.row_month_ends`, which is Chan's own rule. That gives 96,
   from 1999-11-30 to 2007-10-31. The partial November of 2007 is dropped.
2. At month-end t, a stock's past return is its close at t − 1 over its close
   at t − 12, less 1. That is eleven months ending a month before formation.
   Skipping the latest month is the convention of French's momentum factor.
   Chan names no lookback.
3. A positive past return makes a stock a winner and a negative one a loser,
   Chan's split by sign. A past return of exactly 0 is in neither leg, and no
   quantile cut is applied, because location 4004 names none.
4. A stock is eligible at t only with a finite close at every one of the 14
   month-ends from t − 12 to t + 1.
5. WML for the month from t to t + 1 is the equal-weighted mean of the
   winners' returns less that of the losers'. No costs are charged.
6. MKT is SPY's month-end to month-end return over the same month, less that
   holding month's TB3MS divided by 12.
7. The formations run from 2000-11-30 to 2007-09-28, so the holding months run
   from December 2000 to October 2007. That is 83 months.
8. An empty leg in any month refuses the run, as :class:`EmptyLeg`, and names
   the month rather than reporting a WML for it.

**The statistic** is the lag-1 autocorrelation of 83 monthly returns,
``pandas.Series.autocorr(lag=1)``, the Pearson correlation of the 82 pairs of
one month's return with the month before. The same call computes it for MKT,
for WML and for each of the stocks with a finite return in all 83 holding
months. Their median stands for "individual stock's returns".

**The criterion**, applied to each factor on its own. The claim holds for a
factor when its autocorrelation is above 0 and above the median stock's, both
compared unrounded. Chan wrote "often", so one factor of the two holding is a
result to report as it stands, and no combined verdict is formed. The owner
ruled that way on 2026-10-03, before any autocorrelation was computed.

Beside the verdicts, deciding nothing, the report prints the ±1.96/√83 band a
series with no autocorrelation leaves about 5 percent of the time, each
factor's percentile among the stocks, the stocks' quartiles, each factor's
mean monthly return times 12 with its plain t-statistic, and the legs' sizes.

**Every figure that touches the stocks is about survivors.** ``spx_20071123/``
is the S&P 500 as it stood on 2007-11-23, carried backwards. The loser leg
lacks the losers that fell out of the index, which pushes WML down, and the
winner leg lacks the winners that later collapsed out of it, which pushes WML
up. Which dominates is not measured here, and
[issue 198](https://github.com/l3a0/quantitative-trading/issues/198) is where a
panel that could measure it is waited on. MKT reads SPY, which held the index
as it stood each day, so only WML and the stocks carry the bias.

The scale-break guard is not called. A momentum ranking is meant to see a real
collapse, and refusing a window across one would drop the losers the factor
exists to short. The comment above ``FLAGGED_IN_CHANS_MAT_FILES`` in
``tests/test_scale_breaks.py`` records the decision.

Every result here is exploratory. Testing a claim someone else chose spends
the 2000 to 2007 sample on it, so the run says whether the claim holds on this
file and nothing about factor momentum today.

``tests/test_momentum_factor.py`` is the single authority for every number any
prose surface quotes about this experiment.

Usage:
    python -m chan.momentum_factor
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from chan.bill_rates import bill_vintage, monthly_rates
from chan.series import load_panel, load_vintage, panel_line, row_month_ends, vintage_line
from chan.vintage import VintageEntry, VintageUnavailable

#: Chan's S&P 500 file, the cross-section WML and the comparison set come from.
SOURCE_FILE = "SPX_20071123.mat"

#: The market, read from Chan's ``example6_2.xls`` column.
MARKET = "SPY"

#: The past return runs from the close ``LOOKBACK`` month-ends before formation
#: to the close ``SKIP`` month-ends before it.
LOOKBACK = 12
SKIP = 1

#: The first and last formation month-ends, fixed on the issue before any
#: return was computed.
FIRST_FORMATION = pd.Timestamp("2000-11-30")
LAST_FORMATION = pd.Timestamp("2007-09-28")

#: The two-sided 5 percent point of the normal, for the band reported beside
#: the verdicts.
CRITICAL = 1.96

#: Months a year, which annualises a mean monthly return and turns a yearly
#: bill rate into a monthly one.
MONTHS = 12

#: The Kindle locations of the revised edition the report cites: the market
#: factor, WML, and the claim.
MARKET_LOCATION = 3978
WML_LOCATION = 4004
CLAIM_LOCATION = 4014

#: Chan's word for how reliably factors behave this way, quoted beside each
#: verdict.
OFTEN = "often"


class EmptyLeg(Exception):
    """A formation left the winner or the loser leg empty, so WML has no value that month."""


@dataclass(frozen=True)
class Factors:
    """The 83 holding months of MKT and WML, and what each formation held.

    Every tuple runs in formation order. ``formed`` is month-end t,
    ``held_to`` is t + 1, and ``lookback_start`` and ``lookback_end`` are the
    two closes a past return is read between, t − 12 and t − 1.
    """

    month_ends: pd.DatetimeIndex
    formed: tuple[pd.Timestamp, ...]
    held_to: tuple[pd.Timestamp, ...]
    lookback_start: tuple[pd.Timestamp, ...]
    lookback_end: tuple[pd.Timestamp, ...]
    #: Indexed by ``held_to``.
    mkt: pd.Series
    wml: pd.Series
    winners: tuple[int, ...]
    losers: tuple[int, ...]
    eligible: tuple[int, ...]
    #: Each stock's return over each holding month, indexed by ``held_to``.
    stock_returns: pd.DataFrame


@dataclass(frozen=True)
class Comparison:
    """The lag-1 autocorrelations of both factors and of the comparison set."""

    mkt: float
    wml: float
    #: One per stock with a finite return in every holding month.
    stocks: pd.Series
    months: int

    @property
    def median(self) -> float:
        return float(self.stocks.median())

    @property
    def lower_quartile(self) -> float:
        return float(self.stocks.quantile(0.25))

    @property
    def upper_quartile(self) -> float:
        return float(self.stocks.quantile(0.75))

    @property
    def band(self) -> float:
        """±1.96/√n, where a series with no autocorrelation lands 95 percent of the time."""
        return CRITICAL / math.sqrt(self.months)

    def percentile(self, value: float) -> float:
        """The percent of the comparison set whose autocorrelation is strictly below ``value``."""
        return float((self.stocks < value).mean() * 100)

    def outside_band(self, value: float) -> bool:
        return abs(value) > self.band


@dataclass(frozen=True)
class Verdict:
    """The criterion applied to one factor: both halves, and whether the claim holds."""

    factor: str
    autocorrelation: float
    median: float

    @property
    def above_zero(self) -> bool:
        return self.autocorrelation > 0

    @property
    def above_median(self) -> bool:
        return self.autocorrelation > self.median

    @property
    def holds(self) -> bool:
        return self.above_zero and self.above_median

    def line(self) -> str:
        if self.holds:
            return "HOLDS. Above 0 and above the median stock"
        if self.above_zero:
            return "DOES NOT HOLD. Above 0, but not above the median stock"
        if self.above_median:
            return "DOES NOT HOLD. Above the median stock, but not above 0"
        return "DOES NOT HOLD. Neither above 0 nor above the median stock"


def build_factors(closes: pd.DataFrame, spy: pd.Series, bills: dict[str, float]) -> Factors:
    """MKT and WML over the window, from the panel's closes, SPY's closes and the bill rates.

    ``bills`` maps ``YYYY-MM`` to that month's average three-month rate as a
    decimal a year, which is what :func:`chan.bill_rates.monthly_rates` returns.
    """
    ends = closes.index[row_month_ends(closes.index)]
    at_ends = closes.loc[ends].to_numpy()
    missing = [day.date().isoformat() for day in ends if day not in spy.index]
    if missing:
        raise VintageUnavailable(
            f"{MARKET} has no close on {len(missing)} of the panel's month-ends, the first "
            f"{missing[0]}, so the market factor cannot be read on the panel's calendar"
        )
    market = spy.loc[ends].to_numpy()

    first = ends.get_loc(FIRST_FORMATION)
    last = ends.get_loc(LAST_FORMATION)
    formed, held_to, starts, stops = [], [], [], []
    mkt, wml, winners, losers, eligible, held = [], [], [], [], [], []
    for t in range(first, last + 1):
        window = at_ends[t - LOOKBACK : t + 2]
        ok = np.isfinite(window).all(axis=0)
        past = at_ends[t - SKIP] / at_ends[t - LOOKBACK] - 1
        ahead = at_ends[t + 1] / at_ends[t] - 1
        win = ok & (past > 0)
        lose = ok & (past < 0)
        month = ends[t + 1].strftime("%Y-%m")
        if not win.any() or not lose.any():
            leg = "winner" if not win.any() else "loser"
            raise EmptyLeg(
                f"the {leg} leg is empty for the month ending {ends[t + 1].date()}, formed "
                f"{ends[t].date()}, so WML has no return that month"
            )
        formed.append(ends[t])
        held_to.append(ends[t + 1])
        starts.append(ends[t - LOOKBACK])
        stops.append(ends[t - SKIP])
        wml.append(float(ahead[win].mean() - ahead[lose].mean()))
        mkt.append(float(market[t + 1] / market[t] - 1 - bills[month] / MONTHS))
        winners.append(int(win.sum()))
        losers.append(int(lose.sum()))
        eligible.append(int(ok.sum()))
        held.append(ahead)

    index = pd.DatetimeIndex(held_to)
    return Factors(
        month_ends=ends,
        formed=tuple(formed),
        held_to=tuple(held_to),
        lookback_start=tuple(starts),
        lookback_end=tuple(stops),
        mkt=pd.Series(mkt, index=index, name="MKT"),
        wml=pd.Series(wml, index=index, name="WML"),
        winners=tuple(winners),
        losers=tuple(losers),
        eligible=tuple(eligible),
        stock_returns=pd.DataFrame(np.vstack(held), index=index, columns=closes.columns),
    )


def autocorrelations(factors: Factors) -> Comparison:
    """Each factor's lag-1 autocorrelation, and every fully priced stock's."""
    returns = factors.stock_returns
    complete = returns.loc[:, np.isfinite(returns.to_numpy()).all(axis=0)]
    return Comparison(
        mkt=float(factors.mkt.autocorr(lag=1)),
        wml=float(factors.wml.autocorr(lag=1)),
        stocks=complete.apply(lambda stock: stock.autocorr(lag=1)),
        months=len(returns),
    )


def verdicts(comparison: Comparison) -> tuple[Verdict, Verdict]:
    """The criterion applied to MKT and to WML, separately."""
    return (
        Verdict("MKT", comparison.mkt, comparison.median),
        Verdict("WML", comparison.wml, comparison.median),
    )


def annual_mean(returns: pd.Series) -> float:
    return float(returns.mean() * MONTHS)


def t_statistic(returns: pd.Series) -> float:
    """The mean over its plain standard error, with no correction for autocorrelation."""
    return float(returns.mean() / (returns.std(ddof=1) / math.sqrt(len(returns))))


def read_sources(
    data_dir: Path | None = None,
) -> tuple[
    list[VintageEntry], pd.DataFrame, VintageEntry, pd.Series, VintageEntry, dict[str, float]
]:
    """The panel, SPY and the bills, each with the entry the report names it by."""
    members, closes = load_panel(SOURCE_FILE, data_dir=data_dir)
    spy_entry, spy = load_vintage(MARKET, chan=True, data_dir=data_dir)
    bill_entry = bill_vintage(data_dir=data_dir)
    bills = dict(monthly_rates(data_dir=data_dir))
    return members, closes, spy_entry, spy, bill_entry, bills


def report(
    members: list[VintageEntry],
    spy_entry: VintageEntry,
    bill_entry: VintageEntry,
    factors: Factors,
    comparison: Comparison,
) -> None:
    """Print the vintages, the window, every figure, both verdicts and both labels."""
    print("The market and momentum factors on Chan's S&P 500 file, and whether they have momentum")
    print(f"  stocks   {panel_line(members)}")
    print(f"  market   {vintage_line(spy_entry)}")
    print(f"  bills    {vintage_line(bill_entry)}")
    print(
        f"  window   formed {factors.formed[0].date()} to {factors.formed[-1].date()}, held to "
        f"{factors.held_to[0].date()} to {factors.held_to[-1].date()}, {len(factors.mkt)} months"
    )
    print(f"  MKT      {MARKET} month-end return less TB3MS / {MONTHS}, location {MARKET_LOCATION}")
    print(
        f"  WML      winners minus losers by the sign of the return from t-{LOOKBACK} to "
        f"t-{SKIP}, equal-weighted, held one month, location {WML_LOCATION}"
    )
    print(
        f"  eligible {min(factors.eligible)} to {max(factors.eligible)} stocks per formation, "
        f"so {len(members) - max(factors.eligible)} to {len(members) - min(factors.eligible)} "
        "excluded for a missing close"
    )
    print(
        f"  legs     winners {min(factors.winners)} to {max(factors.winners)}, "
        f"losers {min(factors.losers)} to {max(factors.losers)}"
    )
    print()
    print(f"  Lag-1 autocorrelation of {comparison.months} monthly returns, Series.autocorr(lag=1)")
    print(f"  {'Series':<34} {'Autocorr':>9} {'Pctile':>7} {'Mean x 12':>10} {'t':>7}")
    for name, series, value in (
        ("MKT", factors.mkt, comparison.mkt),
        ("WML", factors.wml, comparison.wml),
    ):
        print(
            f"  {name:<34} {value:>9.4f} {comparison.percentile(value):>7.2f} "
            f"{annual_mean(series):>10.4f} {t_statistic(series):>7.4f}"
        )
    count = len(comparison.stocks)
    for label, value in (
        (f"Stocks, lower quartile of {count}", comparison.lower_quartile),
        (f"Stocks, median of {count}", comparison.median),
        (f"Stocks, upper quartile of {count}", comparison.upper_quartile),
    ):
        print(f"  {label:<34} {value:>9.4f}")
    print()
    for verdict in verdicts(comparison):
        print(
            f'  Claim for {verdict.factor}, location {CLAIM_LOCATION}, factor returns "{OFTEN}" '
            f"have stronger serial autocorrelation than stocks: {verdict.line()}."
        )
    print(
        "  Each factor is judged on its own: above 0 and above the median stock, unrounded, "
        "declared before any autocorrelation was computed."
    )
    print()
    outside = [
        name
        for name, value in (("MKT", comparison.mkt), ("WML", comparison.wml))
        if comparison.outside_band(value)
    ]
    print(
        f"  Band +/-{CRITICAL}/sqrt({comparison.months}) = {comparison.band:.4f}, where a series "
        "with no autocorrelation leaves its estimate 95 percent of the time. Decides nothing."
    )
    print(f"  Outside it: {', '.join(outside) or 'neither factor'}.")
    print(
        "  The panel holds only the stocks still in the index on 2007-11-23, so WML and every "
        "stock figure above are about survivors. MKT reads SPY and is not."
    )
    print(
        "  Exploratory. Testing a claim someone else chose spends the 2000 to 2007 sample on it, "
        "so this says whether"
    )
    print(
        "  the claim holds on this file and nothing about factor momentum today. "
        "docs/replication-log.md Entry 13 carries the verdicts."
    )


def run(data_dir: Path | None = None) -> tuple[Factors, Comparison]:
    """Read the three vintages, build both factors, and print the report."""
    members, closes, spy_entry, spy, bill_entry, bills = read_sources(data_dir)
    factors = build_factors(closes, spy, bills)
    comparison = autocorrelations(factors)
    report(members, spy_entry, bill_entry, factors, comparison)
    return factors, comparison


def main() -> None:
    argparse.ArgumentParser(
        description="The market and momentum factors on Chan's S&P 500 file, and whether "
        "their returns have momentum"
    ).parse_args()
    try:
        run()
    except (VintageUnavailable, EmptyLeg) as refused:
        # A refusal that names the source or the month is worth nothing at the
        # bottom of a traceback, so it reaches the reader as one line, the way
        # chan.khandani_lo.main does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
