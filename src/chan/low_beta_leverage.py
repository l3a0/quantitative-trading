"""Whether a levered low-beta portfolio out-compounds an unlevered high-beta one, on Chan's S&P 500.

Chan's Fama-French argument at Kindle location 4684 of the revised edition ends
on a claim that needs only prices. Levered up to a high-beta portfolio's beta,
a low-beta portfolio earns the same average return under the model, so the
choice comes down to risk, and "Empirical studies have found that a portfolio
that consists of low-beta stocks generally has lower risk and thus a higher
Sharpe ratio." His chapter summary at location 4709 states the rule: "Holding
a highly leveraged portfolio of low-beta stocks should generate higher
long-term compounded growth than holding an unleveraged portfolio of high-beta
stocks." Location 4700 adds the caveat that fat tails make one "quite wary of
using too much leverage on normally low-beta stocks".
[Issue 275](https://github.com/l3a0/quantitative-trading/issues/275) carries
the plan, registered on 2026-10-11 before any beta or return was computed, and
every rule below is that plan's.

**The construction.**

1. The panel is cut to the 2,011 days it shares with SPY, which drops the 13
   rows on days the exchange was closed. The month-ends are
   :func:`chan.series.row_month_ends` on that cut calendar, 96 of them, from
   1999-11-30 to 2007-10-31.
2. A day's excess return is its simple return on the cut calendar less the
   TB3MS rate of that day's month divided by 252, for each stock and for SPY.
3. At month-end t a stock's beta is the OLS slope, with an intercept, of its
   daily excess return on SPY's over the 252 daily returns ending at t. It
   needs at least 200 of those 252 days with both returns finite, and the fit
   reads only those days. :func:`ithildincore.timeseries.ols` with a column of
   ones is the estimator.
4. A stock is eligible at t when it has a beta and a close at both t and t + 1.
   The eligible stocks are sorted by beta, ties broken by symbol, and the
   lowest and the highest fifth form the two portfolios, each holding the floor
   of a fifth of the eligible count.
5. Each portfolio is equal-weighted, held one month from t to t + 1, and
   re-formed every month-end. The first formation is the first month-end with
   252 returns behind it, 2000-11-30, so the holding months run from December
   2000 to October 2007, 83 of them.
6. The low portfolio is levered by k, the high group's mean beta over the low
   group's, both from point 3, so k is known before the month it applies to.
   The levered month returns rf + k × (r_low − rf), where rf is the holding
   month's TB3MS divided by 12. Borrowing costs the bill rate, and no trading
   cost is charged. A low group whose mean beta is not positive refuses the run
   as :class:`NonPositiveBeta` rather than levering it.

**The statistic** is the Newey-West t of d, the 83 monthly differences
ln(1 + r_levered) − ln(1 + r_high), from
:func:`ithildincore.stats.newey_west_summary`. Twelve times the mean of d is the
gap in realised compounded growth a year.

**The criterion**, one-sided at 5 percent against 1.645, with four outcomes.
The first three were worded on the issue before any number:

1. **Holds** when the mean of d is above 0 and t is at least 1.645.
2. **Contradicted** when the mean is below 0 and t is at most −1.645.
3. **Not decided** otherwise, with Y, the gap a one-sided 5 percent test finds
   four times in five, as (1.645 + 0.8416) times the Newey-West standard error
   of the mean of d, times 12.
4. **Contradicted by ruin** when any holding month's levered return is −1 or
   below. The levered portfolio has then lost more than its capital, its
   compounded growth is unbounded below, and d does not exist for that month,
   so neither t nor Y is computed. Every ruined month is reported with its
   formation date, its k and its levered return.

The fourth outcome is the issue's amendment of 2026-10-11, which the owner
ruled after the leverage path was seen. The registered rules left a month
below −1 undefined. The build found two such months, June and September 2001,
and stopped before anything the criterion reads had been computed. So the ruin
case was settled after its first instance was visible, and the amendment names
everything that had been seen.

Beside the verdict the report prints the side figures the plan declared. Each
is a point estimate that nothing tests, so each is exploratory and decides
nothing.

1. The Sharpe ratio of the levered low, the low and the high.
2. The realised compounded growth of the low, the high and SPY. The levered
   low's is reported as ruin rather than as a number.
3. k's mean, minimum and maximum.
4. The realised beta of the levered low, the low, the high and SPY.
5. A table of every formation: its eligible count, the size of each group,
   each group's mean beta, and k.
6. Location 4709's Kelly reading.

The levered low's Sharpe ratio and realised beta read all 83 months of
``Portfolios.levered``, which holds rf + k × (r_low − rf) for each month as if
the portfolio were freshly funded at its start. That is how the plan defines
the series, and it is not what an investor ruined in June 2001 would have
held. The Kelly reading is look-ahead, because the Kelly leverage it reads is
computed from the whole sample, and at the in-sample Kelly leverage any
portfolio's growth is at least its own unlevered growth by construction. Its
growth is the Gaussian growth r + S² / 2, a formula on the sample's moments
rather than a growth any portfolio realised.

**Every figure drawn from the stocks is about survivors.** ``spx_20071123/``
is the S&P 500 as it stood on 2007-11-23, carried backwards, so a stock that
left the index before then is in neither portfolio. Which side that flatters
is not measured here. Leaving out high-beta stocks that fell out of the index
would flatter the high side and work against the claim, and that is a
hypothesis rather than a finding.

The scale-break guard is not called, as in :mod:`chan.momentum_factor`. The
run instead reports how many stock-months in either portfolio have a flagged
day inside the beta window or the holding month. The comment above
``FLAGGED_IN_CHANS_MAT_FILES`` in ``tests/test_scale_breaks.py`` records the
decision.

The result is **registered**, under the amendment of 2026-10-11. The
hypothesis, the specification and the first three outcomes' wording were
committed on the issue before any number was seen, and the amendment covers
only the case those rules left undefined. Registration rules out a
specification tuned on this panel by this repo. It does not make 2000 to 2007
a holdout, because Chan's premise comes from "empirical studies" of past
prices, and those years were past prices by the time the book printed the
claim.
[Issue 526](https://github.com/l3a0/quantitative-trading/issues/526) runs
issue 275's registered specification on IVV's S&P 500 from 2008 to 2026, with
the changes that panel forces and under both amendments of 2026-10-11, the
ruin amendment and its own skip amendment. That run is a holdout, and
[issue 516](https://github.com/l3a0/quantitative-trading/issues/516) tests the
rule on this file at leverage a broker would lend, as an exploratory run,
because the ruin had been seen.

``tests/test_low_beta_leverage.py`` is the single authority for every number
any prose surface quotes about this experiment. It first ran here on
2026-10-11.

:func:`ruin_line`, :func:`ruinous_leverage` and :func:`levered_wealth` were
added by the write-up, ``blog/levered-low-beta-lessons.md``, after the run.
They measure how far each month stood from ruin and decide nothing.
:mod:`chan.low_beta_leverage_figures` draws that post's figure.

Usage:
    python -m chan.low_beta_leverage
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from ithildincore.stats import NeweyWestSummary, newey_west_summary
from ithildincore.timeseries import ols

from chan.bill_rates import bill_vintage, monthly_rates
from chan.kelly_leverage import Moments, annualised_moments
from chan.series import (
    load_panel,
    load_vintage,
    panel_line,
    row_month_ends,
    scale_breaks,
    vintage_line,
)
from chan.vintage import VintageEntry, VintageUnavailable

#: Chan's S&P 500 file, the stocks both portfolios are drawn from.
SOURCE_FILE = "SPX_20071123.mat"

#: The market, read from Chan's ``example6_2.xls`` column.
MARKET = "SPY"

#: The daily returns a beta is fitted over, and the fewest of them with both
#: returns finite that a stock needs.
BETA_DAYS = 252
MIN_DAYS = 200

#: Trading days a year, which turns a yearly bill rate into a daily one.
DAYS_A_YEAR = 252

#: Months a year, which annualises a monthly mean and turns a yearly bill rate
#: into a monthly one.
MONTHS = 12

#: The beta groups. The lowest and the highest of them are the two portfolios.
GROUPS = 5

#: The one-sided 5 percent point of the normal, against which t is read.
CRITICAL = 1.645

#: The normal's 80th percentile. Added to :data:`CRITICAL`, it gives the gap a
#: one-sided 5 percent test finds four times in five.
POWER = 0.8416

#: The Kindle locations of the revised edition the report cites: the premise
#: and the beta match, the fat-tail caveat, and the rule.
PREMISE_LOCATION = 4684
CAVEAT_LOCATION = 4700
RULE_LOCATION = 4709


#: A levered month returning this or less has lost all its capital, which the
#: issue's amendment of 2026-10-11 reads as the claim contradicted.
RUIN = -1.0


class NonPositiveBeta(Exception):
    """A formation's low group has a mean beta of zero or below, so no leverage matches it."""


class EmptyPortfolio(Exception):
    """A formation has fewer than five eligible stocks, so a fifth of them holds none."""


class UnreadableStandardError(Exception):
    """The Newey-West t of d is 0, so the standard error behind Y cannot be recovered.

    :func:`ithildincore.stats.newey_west_summary` returns a t of 0 in two cases.
    One is a mean of exactly 0. The other is a standard error of 0, which d
    has when every month's gap is the same. The summary carries the mean and t
    but not the standard error, so neither case lets Y be computed, and
    recomputing the variance here would be a second copy of the estimator.
    """


@dataclass(frozen=True)
class Portfolios:
    """The holding months of the three portfolios, 83 on Chan's file, and what each formation held.

    Every tuple runs in formation order, and every series is indexed by
    ``held_to``, month-end t + 1. ``rf`` is that holding month's TB3MS over 12.
    ``low_beta`` and ``high_beta`` are each group's mean beta at formation, and
    ``leverage`` is their ratio. ``levered`` holds rf + k × (r_low − rf) for
    every month, those after a ruin included, so a ruin is read from the plan's
    arithmetic rather than from a series cut short.
    """

    month_ends: pd.DatetimeIndex
    formed: tuple[pd.Timestamp, ...]
    held_to: tuple[pd.Timestamp, ...]
    #: The first day whose return is inside each formation's beta window.
    window_start: tuple[pd.Timestamp, ...]
    low: pd.Series
    high: pd.Series
    levered: pd.Series
    rf: pd.Series
    spy: pd.Series
    low_beta: pd.Series
    high_beta: pd.Series
    leverage: pd.Series
    eligible: tuple[int, ...]
    low_members: tuple[tuple[str, ...], ...]
    high_members: tuple[tuple[str, ...], ...]
    #: Each eligible stock's beta at each formation, NaN where it has none.
    betas: pd.DataFrame
    #: Formations left out under ``skip_non_positive``, in none of the per-formation
    #: fields above. ``month_ends`` still lists every month-end.
    skipped: tuple[Skipped, ...] = ()


@dataclass(frozen=True)
class Skipped:
    """A formation whose low group's mean beta is zero or below, so no leverage matches it."""

    formed: pd.Timestamp
    held_to: pd.Timestamp
    low_beta: float
    high_beta: float


@dataclass(frozen=True)
class Ruin:
    """One holding month in which the levered portfolio lost more than its capital."""

    formed: pd.Timestamp
    held_to: pd.Timestamp
    leverage: float
    levered: float


@dataclass(frozen=True)
class Verdict:
    """The criterion applied to d, or the ruin that leaves d undefined.

    ``summary`` is ``None`` exactly when ``ruined`` is not empty, because the
    amendment computes neither t nor Y once a month is ruined.
    """

    months: int
    summary: NeweyWestSummary | None = None
    ruined: tuple[Ruin, ...] = ()

    @property
    def by_ruin(self) -> bool:
        return bool(self.ruined)

    def _tested(self) -> NeweyWestSummary:
        if self.summary is None:
            raise ValueError(
                "a levered month lost more than its capital, so d is undefined and the "
                "Newey-West statistic is not computed"
            )
        return self.summary

    @property
    def gap(self) -> float:
        """Twelve times the mean of d, the gap in realised compounded growth a year."""
        return self._tested().mean * MONTHS

    @property
    def t(self) -> float:
        return self._tested().t_newey_west

    @property
    def lag(self) -> int:
        return self._tested().lag

    @property
    def standard_error(self) -> float:
        """The Newey-West standard error of the mean of d, a month.

        Read back from the summary's mean and t rather than recomputed, so the
        variance exists once, in :mod:`ithildincore.stats`, whose arithmetic is
        pinned there. The summary returns a t of 0 for a mean of exactly 0 and
        for a standard error of 0, and either refuses as
        :class:`UnreadableStandardError`.
        """
        if self.t == 0:
            raise UnreadableStandardError(
                f"the Newey-West t of d is 0 over {self.months} months, which the summary "
                "returns for a mean of exactly 0 or a gap that never varies, so the standard "
                "error behind Y cannot be recovered"
            )
        return abs(self._tested().mean / self.t)

    @property
    def detectable(self) -> float:
        """Y, the yearly gap a one-sided 5 percent test finds four times in five."""
        return (CRITICAL + POWER) * self.standard_error * MONTHS

    @property
    def holds(self) -> bool:
        return not self.by_ruin and self._tested().mean > 0 and self.t >= CRITICAL

    @property
    def contradicted(self) -> bool:
        return self.by_ruin or (self._tested().mean < 0 and self.t <= -CRITICAL)

    @property
    def outcome(self) -> str:
        if self.by_ruin:
            return "Contradicted by ruin"
        if self.holds:
            return "Holds"
        if self.contradicted:
            return "Contradicted"
        return "Not decided"

    @property
    def log_verdict(self) -> str:
        """The value the log's verdict column takes, as the issue maps each outcome."""
        return "reproduced" if self.holds else "did not reproduce"

    def line(self) -> str:
        """The outcome in the wording the issue fixed."""
        if self.by_ruin:
            first = self.ruined[0]
            return (
                "Levered to the high-beta portfolio's beta, the low-beta portfolio lost more "
                f"than its capital in the month ending {first.held_to.date()}, at a leverage of "
                f"{first.leverage:.4f}, so its compounded growth is unbounded below and the "
                "unlevered high-beta portfolio out-compounded it."
            )
        if self.holds:
            return (
                "Levered to the high-beta portfolio's beta, the low-beta portfolio "
                f"out-compounded the unlevered high-beta portfolio by {self.gap:.4f} a year, "
                f"Newey-West t = {self.t:.4f} over {self.months} months."
            )
        if self.contradicted:
            # The issue's sentence names the high-beta side as the winner, so the
            # gap it quotes is the size of the high side's lead, a positive number.
            return (
                "The unlevered high-beta portfolio out-compounded the levered low-beta "
                f"portfolio by {-self.gap:.4f} a year, Newey-West t = {self.t:.4f} over "
                f"{self.months} months."
            )
        return (
            f"No gap in compounded growth detectable above about {self.detectable:.4f} a year "
            f"over {self.months} months, where the point estimate is {self.gap:.4f}."
        )


@dataclass(frozen=True)
class Kelly:
    """Location 4709's Kelly reading, which looks ahead and decides nothing.

    ``moments`` are the low portfolio's on its monthly excess return, with no
    rate subtracted again and 12 periods a year, so ``moments.leverage`` is the
    full-sample m / s² and ``moments.levered_growth`` is S² / 2, the growth
    above the bill rate. ``bill`` is the mean holding-month bill rate a year,
    the r that growth sits on.
    """

    moments: Moments
    bill: float

    @property
    def leverage(self) -> float:
        return self.moments.leverage

    @property
    def growth(self) -> float:
        """The Gaussian growth r + S² / 2 at the low portfolio's full-sample Kelly leverage.

        A formula on the sample's mean and variance, not a growth any portfolio
        realised at that leverage.
        """
        return self.bill + self.moments.levered_growth


def daily_excess(prices: pd.DataFrame, bills: dict[str, float]) -> pd.DataFrame:
    """Each column's simple daily return less that day's month's bill rate over 252.

    No price is carried forward, so a return touching a missing close is NaN.
    """
    returns = prices.pct_change(fill_method=None)
    rate = np.array([bills[day.strftime("%Y-%m")] for day in prices.index]) / DAYS_A_YEAR
    return returns.sub(rate, axis=0)


def fit_beta(stock: np.ndarray, market: np.ndarray) -> float:
    """The OLS slope of ``stock`` on ``market`` with an intercept, over the days both are finite.

    NaN when fewer than :data:`MIN_DAYS` days qualify.
    """
    ok = np.isfinite(stock) & np.isfinite(market)
    if ok.sum() < MIN_DAYS:
        return math.nan
    x = np.column_stack([np.ones(int(ok.sum())), market[ok]])
    return float(ols(stock[ok], x).beta[1])


def flagged_days(closes: pd.DataFrame) -> dict[str, list[pd.Timestamp]]:
    """Every stock's scale-break days, read on its own rows, for the stocks that have any."""
    flags = {}
    for symbol in closes.columns:
        days = scale_breaks(closes[symbol].dropna())
        if days:
            flags[symbol] = days
    return flags


def build_portfolios(
    closes: pd.DataFrame,
    spy: pd.Series,
    bills: dict[str, float],
    *,
    members: pd.DataFrame | None = None,
    skip_non_positive: bool = False,
) -> Portfolios:
    """The low, high and levered portfolios over the window, from the panel, SPY and the bills.

    ``bills`` maps ``YYYY-MM`` to that month's average three-month rate as a
    decimal a year, which is what :func:`chan.bill_rates.monthly_rates` returns.

    ``members`` is for a panel whose stocks come and go, which
    [issue 526](https://github.com/l3a0/quantitative-trading/issues/526) runs.
    It is a boolean frame indexed by month-end days, one column per stock, and
    a stock is eligible at a formation only where its row there is true. Its
    index replaces :func:`chan.series.row_month_ends` as the month-ends, so the
    last holding month can end on the frame's last row, and a day the cut
    calendar lacks is refused. The close at t + 1 is still asked for, so a
    caller wanting a stopped stock to earn its return to its last close
    carries that close to the next month-end first, as
    :func:`chan.equity_seasonals.stopped_closes` does. Left out, every stock is
    a candidate at every month-end, as on Chan's file.

    ``skip_non_positive`` is issue 526's amendment of 2026-10-11. A formation
    whose low group's mean beta is not positive then leaves its holding month
    out of every series and is listed in ``skipped``, rather than refusing the
    run as :class:`NonPositiveBeta`.
    """
    cut = closes.loc[closes.index.isin(spy.index)]
    market = spy.loc[cut.index]
    if not np.isfinite(market.to_numpy()).all():
        raise VintageUnavailable(
            f"{MARKET} has a missing close on a day the panel shares with it, so its daily "
            "return cannot be read on the panel's calendar"
        )
    stock_excess = daily_excess(cut, bills).to_numpy()
    market_excess = daily_excess(market.to_frame(), bills).to_numpy()[:, 0]
    at = cut.to_numpy()
    rows = row_month_ends(cut.index)
    symbols = np.array(cut.columns)
    allowed = np.ones((len(rows), len(symbols)), dtype=bool)
    if members is not None:
        outside = members.index.difference(cut.index)
        if len(outside):
            raise VintageUnavailable(
                f"{len(outside)} month-ends in the members frame are not on the panel's "
                f"calendar, the first {outside[0].date()}"
            )
        if not members.index.is_monotonic_increasing or not members.index.is_unique:
            raise ValueError("the members frame's month-ends are not in increasing date order")
        rows = cut.index.get_indexer(members.index)
        allowed = members.reindex(columns=cut.columns, fill_value=False).to_numpy(dtype=bool)
    ends = cut.index[rows]

    formed, held_to, starts = [], [], []
    low, high, levered, rf, spy_month = [], [], [], [], []
    low_beta, high_beta, leverage, eligible = [], [], [], []
    low_members, high_members, beta_rows = [], [], []
    skipped = []
    for t in range(len(ends) - 1):
        row, next_row = rows[t], rows[t + 1]
        if row < BETA_DAYS:
            continue
        window = slice(row - BETA_DAYS + 1, row + 1)
        y = stock_excess[window]
        x = market_excess[window]
        beta = np.array(
            [fit_beta(y[:, j], x) if allowed[t, j] else math.nan for j in range(len(symbols))]
        )
        ok = np.isfinite(beta) & np.isfinite(at[row]) & np.isfinite(at[next_row])
        count = int(ok.sum())
        size = count // GROUPS
        if size == 0:
            raise EmptyPortfolio(
                f"only {count} stocks are eligible at {ends[t].date()}, so a fifth of them "
                "holds none"
            )
        # One ordering by beta, then by symbol, read from both ends.
        chosen = np.flatnonzero(ok)
        order = chosen[np.lexsort((symbols[chosen], beta[chosen]))]
        lows, highs = order[:size], order[-size:]
        mean_low = float(beta[lows].mean())
        mean_high = float(beta[highs].mean())
        if not mean_low > 0 and skip_non_positive:
            skipped.append(Skipped(ends[t], ends[t + 1], mean_low, mean_high))
            continue
        if not mean_low > 0:
            raise NonPositiveBeta(
                f"the low group formed {ends[t].date()} has a mean beta of {mean_low:.4f}, so "
                "no leverage brings it to the high group's beta"
            )
        k = mean_high / mean_low
        ahead = at[next_row] / at[row] - 1
        rate = bills[ends[t + 1].strftime("%Y-%m")] / MONTHS
        r_low = float(ahead[lows].mean())

        formed.append(ends[t])
        held_to.append(ends[t + 1])
        starts.append(cut.index[window.start])
        low.append(r_low)
        high.append(float(ahead[highs].mean()))
        levered.append(rate + k * (r_low - rate))
        rf.append(rate)
        spy_month.append(float(market.iloc[next_row] / market.iloc[row] - 1))
        low_beta.append(mean_low)
        high_beta.append(mean_high)
        leverage.append(k)
        eligible.append(count)
        low_members.append(tuple(symbols[lows]))
        high_members.append(tuple(symbols[highs]))
        beta_rows.append(np.where(ok, beta, np.nan))

    index = pd.DatetimeIndex(held_to)
    return Portfolios(
        month_ends=ends,
        formed=tuple(formed),
        held_to=tuple(held_to),
        window_start=tuple(starts),
        low=pd.Series(low, index=index, name="low"),
        high=pd.Series(high, index=index, name="high"),
        levered=pd.Series(levered, index=index, name="levered low"),
        rf=pd.Series(rf, index=index, name="rf"),
        spy=pd.Series(spy_month, index=index, name=MARKET),
        low_beta=pd.Series(low_beta, index=index, name="low beta"),
        high_beta=pd.Series(high_beta, index=index, name="high beta"),
        leverage=pd.Series(leverage, index=index, name="k"),
        eligible=tuple(eligible),
        low_members=tuple(low_members),
        high_members=tuple(high_members),
        betas=pd.DataFrame(np.vstack(beta_rows), index=pd.DatetimeIndex(formed), columns=symbols),
        skipped=tuple(skipped),
    )


def ruined_months(portfolios: Portfolios) -> tuple[Ruin, ...]:
    """Every holding month whose levered return is :data:`RUIN` or below, in date order."""
    return tuple(
        Ruin(formed=formed, held_to=held_to, leverage=float(k), levered=float(r))
        for formed, held_to, k, r in zip(
            portfolios.formed,
            portfolios.held_to,
            portfolios.leverage,
            portfolios.levered,
            strict=True,
        )
        if r <= RUIN
    )


def ruin_line(rf: pd.Series, leverage: pd.Series) -> pd.Series:
    """The low fifth's monthly return at or below which the levered month is ruined.

    rf + k × (r − rf) is −1 or below exactly when r is rf − (1 + rf) / k or
    below, for a positive k. ``blog/levered-low-beta-lessons.md`` added it
    after the run, so it decides nothing.
    """
    return rf - (1 + rf) / leverage


def ruinous_leverage(low: pd.Series, rf: pd.Series) -> pd.Series:
    """The smallest leverage that would have ruined each month, (1 + rf) / (rf − r).

    A month whose low return is at or above the bill rate loses nothing more
    as the leverage grows, so no leverage ruins it and its value is infinite.
    Added after the run by the write-up, like :func:`ruin_line`.
    """
    shortfall = rf - low
    with np.errstate(divide="ignore"):
        ratio = (1 + rf) / shortfall
    return ratio.where(shortfall > 0, math.inf)


def levered_wealth(levered: pd.Series) -> pd.Series:
    """What 1 in the levered portfolio grew to at each month's end, through its first ruin.

    Wealth compounds as the product of 1 + r. The month that ruins it ends at
    or below zero, and every month after it is NaN, because a portfolio that
    has lost its capital holds nothing to lever. Added after the run by the
    write-up, like :func:`ruin_line`.
    """
    wealth = (1 + levered).cumprod()
    ruined = (levered <= RUIN).to_numpy()
    if ruined.any():
        first = int(np.argmax(ruined))
        wealth.iloc[first + 1 :] = np.nan
    return wealth


def differences(portfolios: Portfolios) -> pd.Series:
    """d, ln(1 + r_levered) − ln(1 + r_high), one per holding month.

    Refused once any month is ruined, because the log of a wealth ratio of zero
    or below does not exist and numpy would hand back NaN or −inf in its place.
    """
    if ruined_months(portfolios):
        raise ValueError("a levered month lost more than its capital, so d is undefined")
    return np.log1p(portfolios.levered) - np.log1p(portfolios.high)


def verdict(portfolios: Portfolios) -> Verdict:
    """The criterion applied to d, or the amendment's outcome when a month is ruined."""
    months = len(portfolios.levered)
    ruined = ruined_months(portfolios)
    if ruined:
        return Verdict(months=months, ruined=ruined)
    result = Verdict(months=months, summary=newey_west_summary(differences(portfolios).to_numpy()))
    # Read Y once here, so a degenerate d refuses before anything is printed.
    _ = result.standard_error
    return result


def growth(returns: pd.Series) -> float:
    """Realised compounded growth a year, twelve times the mean monthly log return."""
    return float(np.log1p(returns).mean() * MONTHS)


def excess_moments(returns: pd.Series, rf: pd.Series) -> Moments:
    """Entry 3's annualised moments of the monthly excess return.

    The bill rate moves month by month, so it is subtracted here, month by
    month, and :func:`chan.kelly_leverage.annualised_moments` is handed the
    excess return with a rate of 0, which it would otherwise subtract as one
    constant.
    """
    return annualised_moments(returns - rf, risk_free=0.0, periods_per_year=MONTHS)


def sharpe(returns: pd.Series, rf: pd.Series) -> float:
    """The Sharpe ratio of the monthly excess return, annualised by the square root of 12."""
    return excess_moments(returns, rf).sharpe


def realised_beta(returns: pd.Series, portfolios: Portfolios) -> float:
    """The OLS slope, with an intercept, of a series' monthly excess return on SPY's."""
    market = (portfolios.spy - portfolios.rf).to_numpy()
    x = np.column_stack([np.ones(len(market)), market])
    return float(ols((returns - portfolios.rf).to_numpy(), x).beta[1])


def kelly(portfolios: Portfolios) -> Kelly:
    """The low portfolio's full-sample Kelly leverage and the Gaussian growth there. Look-ahead."""
    return Kelly(
        moments=excess_moments(portfolios.low, portfolios.rf),
        bill=float(portfolios.rf.mean() * MONTHS),
    )


def formation_table(portfolios: Portfolios) -> pd.DataFrame:
    """One row per formation: the eligible count, each group's size, both mean betas and k."""
    return pd.DataFrame(
        {
            "eligible": portfolios.eligible,
            "per group": [len(held) for held in portfolios.low_members],
            "low beta": portfolios.low_beta.to_numpy(),
            "high beta": portfolios.high_beta.to_numpy(),
            "k": portfolios.leverage.to_numpy(),
        },
        index=pd.DatetimeIndex(portfolios.formed, name="formed"),
    )


def flagged_stock_months(
    portfolios: Portfolios, flags: dict[str, list[pd.Timestamp]]
) -> tuple[int, int]:
    """How many low and high stock-months have a flagged day in the beta window or holding month.

    The span read runs from the first day whose return is in the beta window
    to the close the holding month ends on, both included.
    """
    counts = []
    for members in (portfolios.low_members, portfolios.high_members):
        count = 0
        for start, end, held in zip(
            portfolios.window_start, portfolios.held_to, members, strict=True
        ):
            count += sum(
                any(start <= day <= end for day in flags.get(symbol, ())) for symbol in held
            )
        counts.append(count)
    return counts[0], counts[1]


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
    portfolios: Portfolios,
    flagged: tuple[int, int],
) -> None:
    """Print the vintages, the window, the verdict, every side figure and both labels."""
    p = portfolios
    result = verdict(p)
    print("A levered low-beta portfolio against an unlevered high-beta one, on Chan's S&P 500 file")
    print(f"  stocks   {panel_line(members)}")
    print(f"  market   {vintage_line(spy_entry)}")
    print(f"  bills    {vintage_line(bill_entry)}")
    print(
        f"  window   formed {p.formed[0].date()} to {p.formed[-1].date()}, held to "
        f"{p.held_to[0].date()} to {p.held_to[-1].date()}, {len(p.low)} months"
    )
    print(
        f"  beta     OLS slope with an intercept on {MARKET}'s daily excess return, "
        f"{BETA_DAYS} days ending at formation, at least {MIN_DAYS} finite"
    )
    print(
        "  groups   lowest and highest fifth by beta, ties by symbol, equal-weighted, "
        f"held one month, location {PREMISE_LOCATION}"
    )
    sizes = [len(held) for held in p.low_members]
    print(
        f"  eligible {min(p.eligible)} to {max(p.eligible)} stocks per formation, each "
        f"portfolio {min(sizes)} to {max(sizes)}"
    )
    print(
        f"  leverage k = high group's mean beta / low group's, mean {p.leverage.mean():.4f}, "
        f"min {p.leverage.min():.4f}, max {p.leverage.max():.4f}"
    )
    print()
    print(
        f'  Claim, location {RULE_LOCATION}, "Holding a highly leveraged portfolio of low-beta '
        "stocks should generate higher"
    )
    print(
        "  long-term compounded growth than holding an unleveraged portfolio of high-beta "
        f'stocks": {result.outcome.upper()}.'
    )
    print(f"  {result.line()}")
    if result.by_ruin:
        print(f"  {'Ruined month':<14} {'Formed':<12} {'k':>8} {'Levered':>9}")
        for ruin in result.ruined:
            print(
                f"  {str(ruin.held_to.date()):<14} {str(ruin.formed.date()):<12} "
                f"{ruin.leverage:>8.4f} {ruin.levered:>9.4f}"
            )
        print(
            f"  A levered return of {RUIN:.0f} or below leaves d undefined, so the Newey-West t "
            "and Y are not computed."
        )
        print(
            "  The issue's amendment of 2026-10-11 settled this case after its first instance "
            "was visible."
        )
    else:
        print(
            f"  d = ln(1 + levered low) - ln(1 + high), {result.months} months, mean x 12 "
            f"{result.gap:.4f}, Newey-West t {result.t:.4f} at lag {result.lag}, "
            f"Y {result.detectable:.4f}"
        )
        print(
            f"  One-sided at 5 percent against {CRITICAL}, Y = ({CRITICAL} + {POWER}) x the "
            "standard error x 12, registered before any number."
        )
    print()
    print("  Beside the verdict, deciding nothing")
    print(f"  {'Series':<14} {'Growth':>8} {'Sharpe':>8} {'Beta':>8}")
    levered_growth = "ruin" if result.by_ruin else f"{growth(p.levered):.4f}"
    for name, series, grew in (
        ("levered low", p.levered, levered_growth),
        ("low", p.low, f"{growth(p.low):.4f}"),
        ("high", p.high, f"{growth(p.high):.4f}"),
    ):
        print(
            f"  {name:<14} {grew:>8} {sharpe(series, p.rf):>8.4f} {realised_beta(series, p):>8.4f}"
        )
    print(f"  {MARKET:<14} {growth(p.spy):>8.4f} {'':>8} {realised_beta(p.spy, p):>8.4f}")
    print(
        "  Growth is 12 x the mean monthly log return. Sharpe is the monthly excess return's, "
        "x sqrt(12). Beta is on SPY's monthly excess return."
    )
    print(
        "  The levered low's Sharpe and beta read all 83 months of rf + k x (r_low - rf), each "
        "month as if freshly funded,"
    )
    print("  which is how the plan defines the series. They decide nothing.")
    reading = kelly(p)
    print(
        f"  Kelly, location {RULE_LOCATION}, look-ahead: the low portfolio's full-sample m / s^2 "
        f"{reading.leverage:.4f}, Gaussian growth there r + S^2/2 = {reading.bill:.4f} + "
        f"{reading.moments.levered_growth:.4f} = {reading.growth:.4f}, against the high "
        f"portfolio's realised {growth(p.high):.4f}."
    )
    low_flags, high_flags = flagged
    print(
        f"  Scale-break flags inside the beta window or the holding month: {low_flags} low and "
        f"{high_flags} high stock-months of {2 * sum(sizes)}. None is refused."
    )
    print()
    print("  Every formation, deciding nothing")
    print(
        f"  {'Formed':<12} {'Eligible':>8} {'Each':>5} {'Low beta':>9} {'High beta':>10} {'k':>8}"
    )
    for formed, row in formation_table(p).iterrows():
        print(
            f"  {str(formed.date()):<12} {row['eligible']:>8.0f} {row['per group']:>5.0f} "
            f"{row['low beta']:>9.4f} {row['high beta']:>10.4f} {row['k']:>8.4f}"
        )
    print()
    print(
        f'  Location {CAVEAT_LOCATION}: "one should be quite wary of using too much leverage on '
        'normally low-beta stocks", because returns have fat tails.'
    )
    print(
        "  The panel holds only the stocks still in the index on 2007-11-23, so every figure "
        "above drawn from the stocks is about survivors."
    )
    print(
        "  Registered on the issue before any number, under its amendment of 2026-10-11. That "
        "rules out a specification"
    )
    print(
        "  tuned here. It is not a holdout: 2000 to 2007 were past prices by the time the "
        "book printed the claim. docs/replication-log.md Entry 45 carries the verdict."
    )


def run(data_dir: Path | None = None) -> tuple[Portfolios, Verdict]:
    """Read the three vintages, build the portfolios, and print the report."""
    members, closes, spy_entry, spy, bill_entry, bills = read_sources(data_dir)
    portfolios = build_portfolios(closes, spy, bills)
    flagged = flagged_stock_months(portfolios, flagged_days(closes))
    report(members, spy_entry, bill_entry, portfolios, flagged)
    return portfolios, verdict(portfolios)


def main() -> None:
    argparse.ArgumentParser(
        description="Whether a levered low-beta portfolio out-compounds an unlevered high-beta "
        "one on Chan's S&P 500 file"
    ).parse_args()
    try:
        run()
    except (
        VintageUnavailable,
        NonPositiveBeta,
        EmptyPortfolio,
        UnreadableStandardError,
    ) as refused:
        # A refusal that names the source or the month is worth nothing at the
        # bottom of a traceback, so it reaches the reader as one line, the way
        # chan.momentum_factor.main does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
