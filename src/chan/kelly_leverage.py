"""Chan's Kelly leverage on SPY, Example 6.2, against a modern download.

Example 6.1 argues that a positive expected return can still shrink capital.
This one puts a number on the other side of that argument. Given a return
series, the continuous Kelly formula gives the leverage that maximises
long-term compounded growth, ``f* = m / s^2``, where ``m`` is the annualised
mean **excess** return and ``s`` the annualised standard deviation. Chan works
it on SPY, gets 2.528, and then asks whether that leverage would have survived
the worst day the index has had.

**One figure the book prints reproduces here and it is the dispersion.** Chan
read SPY through 2007-12-28. This reads a 2026 download of the same symbol,
which is a different sample, so every level it computes lands high. The
standard deviation does not, because restatement moves where a series sits and
not how much it moves. Reading his own workbook is
[issue 138](https://github.com/l3a0/quantitative-trading/issues/138), and the
``reproduced`` verdict on the rest belongs there.
``docs/replication-log.md`` Entry 3 carries this run's verdicts row by row, and
``tests/test_kelly_leverage.py`` is the single authority for every number any
prose surface quotes about it.

Five choices decide the numbers and three of them are invisible on the page.
Each is read off Chan's own ``example6_3.m``, which implements the multi-asset
Kelly for the next example, rather than guessed from the printed figures.

1. **Simple daily returns**, which location 2777 fixes as "one-period, simple
   (uncompounded), unlevered returns" and which his ``ret=(adjcls-lag1(adjcls))
   ./lag1(adjcls)`` computes.
2. **Annualised by 252 on the mean and by the square root of 252 on the
   standard deviation**, from his ``M=252*mean(excessRet)`` and
   ``C=252*cov(excessRet)``. 251 and 250 are the plausible wrong answers and
   :func:`annualised_moments` is held against both, on this vintage's own
   moments rather than on his.
3. **The sample standard deviation, dividing by n - 1**, which is what MATLAB's
   ``cov`` does. This is the one choice the book's own precision can separate,
   and :func:`annualised_moments` is where it lives. See
   ``## The Sharpe ratio is what holds the specification`` below.
4. **``m`` in ``g = r + m - s^2 / 2`` is the excess return, not the total
   return.** Location 2777 says the returns "should be net of all financing
   costs; that is, they should be excess returns", and the arithmetic printed
   at location 2869 substitutes ``r + m = 0.1123``. The prose beside it glosses
   the same symbol as "the annualized mean return", and following the gloss
   gives 13.80 percent against the book's 9.8.
5. **The adjusted close, not the as-traded close.** Chan's own line is
   ``adjcls1=num1(:, end)``, commented "the adjusted close prices", and the
   choice moves the answer by a quarter. On his workbook's ``Close`` column the
   leverage falls to 1.9341 from 2.5278, which crosses the threshold below and
   reverses his own risk conclusion.

**The price basis runs against this repo's own default, and that is
deliberate.** ``docs/design.md`` says to prefer a series that cannot be
restated, falling back on a committed vintage when only an adjusted series
will do, and its ``### The first time the fallback clause fires`` is why this
is the deliverable where the second half applies. The short version is that
GDX had paid almost nothing by 2007 and SPY had been paying for fifteen years,
worth 1.68 percentage points of annual mean return on his own data. The
reasoning lives there rather than here, because it outlives this experiment.

## The Sharpe ratio is what holds the specification

The obvious pin does not work. The book prints the leverage to three decimals
and the Sharpe ratio to four, and the sample and population dispersion forms
separate at one of those precisions and not the other. On Chan's own data the
sample form gives a Sharpe of 0.427523 and the population form 0.427580, which
print as 0.4275 and 0.4276, while both give a leverage of 2.528. So a suite
pinning the leverage at the precision the book prints passes on the wrong
dispersion form and everything downstream inherits the error quietly.

``src/chan/coin_flip_growth.py`` made the opposite choice on purpose, over two
outcomes where the population form is the right one, so a reader carrying that
reasoning across this module gets this one wrong.

## Black Monday is outside SPY, so it enters as a book constant

SPY's first bar is 1993-01-29, five years after 1987-10-19. Location 3083 says
"In the S&P 500 index example", and 20.47 percent on that day is an S&P 500
index figure. No SPY vintage of any span can check it, so it is named as a
constant the book supplies and the worst loss the window actually holds is
reported beside it.

The test Chan runs is a comparison rather than a simulated drawdown. He
divides a tolerable one-day loss by the worst historical one, gets about 1, and
sets it against half-Kelly. So his conclusion holds exactly while ``f*`` is
above ``2 * 0.20 / 0.2047``, which is 1.954079, and :func:`stress_test`
reports whether it survived rather than leaving a reader to compare two
numbers.

## The window is an argument because it moves the answer further than the data

Within Chan's own series, on his own specification, ``f*`` runs from −2.85 over
2000 to 2002 to +4.83 over 2003 to 2007 against +2.53 over the whole span. So a
single number with no window named mixes vendor drift and sample choice, and
neither is recoverable. The default is Chan's own span, which holds the window
fixed and leaves the vintage as the only difference.

## Time-scale independence is an identity in one reading and false in the other

Chan notes that ``f*`` is independent of time scale, unlike the Sharpe ratio.
Under the annualisation in use that is exactly true and testing it proves
nothing: the factor cancels between ``m`` and ``s^2``, so the annualised ratio
is the per-period ratio. What moves the answer is resampling the returns, and
:data:`SAMPLING_RULES` names three ways of doing it monthly because "monthly
moments" hides the choice. All three land 40-odd percent above the daily
figure and within 0.11 of each other, so the conclusion does not depend on
which is picked, and the run reports which reading it is showing.

Usage::

    python -m chan.kelly_leverage                      # Chan's span, the pinned run
    python -m chan.kelly_leverage --start 2000-01-01 --end 2002-12-31
"""

from __future__ import annotations

import argparse
import calendar
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from chan.series import load_vintage, vintage_line
from chan.vintage import VintageUnavailable

# Chan's own window, which is the span of his ``example6_2.xls``. The default
# run holds it fixed so the vintage is the only thing that differs from his.
BOOK_START = "1993-01-29"
BOOK_END = "2007-12-28"

# The SPY vintage this experiment reads, named by the date it was downloaded.
# Issue 15 records a SPY adjusted vintage too, and two of them make
# ``load_close("SPY")`` refuse and name the candidates, which is the reader
# doing its job. Resolving with a date from the outset means that issue landing
# does not break this run's pins.
#
# Provenance: recorded through :func:`chan.vintage.record_vintage` from a
# yfinance download of the both-adjustments close, splits and dividends folded
# in. ``data/README.md`` names the exact call, and it is named there rather
# than here because yfinance returns two different series under the word
# adjusted, which is
# [issue 125](https://github.com/l3a0/quantitative-trading/issues/125), and one
# home for that fact is one fewer place for it to drift.
VINTAGE_DATE = "2026-09-18"

# The book's constants. None of the four is computed from a series, here or in
# Chan's workbook, so each is quoted rather than derived.
RISK_FREE = 0.04
TRADING_DAYS = 252
EQUITY = 100_000.0
# Location 3083's S&P 500 figure, from a day six years before SPY existed.
BLACK_MONDAY_LOSS = 0.2047
BLACK_MONDAY_DATE = "1987-10-19"
# The one-day loss location 3083 treats as tolerable.
DRAWDOWN_TOLERANCE = 0.20
# The leverage the book prints, rounded to three decimals. The worked example
# and the rebalancing chain at location 3021 are arithmetic on this rounded
# figure rather than on the exact one, which is why $252,800 reproduces and
# the exact leverage times $100,000 does not.
BOOK_LEVERAGE = 2.528
# The 10 percent SPY loss location 3021 rebalances after.
BOOK_SHOCK = 0.10

BOOK_REF = (
    "Example 6.2 (rev. ed., locations 2858, 2869 and 3083): mean 11.23%, sd 16.91%, "
    "risk-free 4%, excess 7.231%, Sharpe 0.4275, Kelly leverage 2.528, levered growth "
    "13.14%, unlevered growth 9.8%, half-Kelly 1.26"
)

# A window shorter than this stops the run. The same floor as
# ``chan.pair_cointegration.run``, for the same reason: a moment estimated from
# a handful of days is a number the report would print without a caveat.
MIN_TRADING_DAYS = 30

# How the returns are sampled before their moments are taken. Named rather than
# implied, because "monthly" hides a choice that moves ``f*`` by 0.1 between
# these three and by 40-odd percent against the daily run.
SAMPLING_RULES = ("daily", "month-end", "month-end-complete", "block-21")

# The trading days in one block of the ``block-21`` rule, chosen as the usual
# count of trading days in a month so the three monthly rules are comparable.
BLOCK_DAYS = 21


@dataclass(frozen=True)
class Moments:
    """One return series' annualised moments and everything Kelly reads off them.

    ``mean_annual`` is the total return and ``excess_annual`` is that less the
    risk-free rate. Both are here because the book prints both and because the
    symbol ``m`` means the second one in every formula Chan writes, while his
    prose at location 2869 glosses it as the first.

    ``period_leverage`` is the same quantity as ``leverage`` computed before
    any annualisation, ``mean excess / variance`` per period. It exists so the
    time-scale claim can be shown as the identity it is: the factor cancels
    between the mean and the variance, so the two agree to floating-point
    noise for any factor at all.
    """

    periods_per_year: float
    returns: int
    risk_free: float
    mean_annual: float
    sd_annual: float
    excess_annual: float
    sharpe: float
    leverage: float
    period_leverage: float
    levered_growth: float
    unlevered_growth: float

    @property
    def half_kelly(self) -> float:
        """The leverage halved, which is the convention location 2836 states."""
        return self.leverage / 2.0


@dataclass(frozen=True)
class StressTest:
    """Chan's Black Monday comparison at location 3083, and whether it survived.

    ``allowed_leverage`` is the tolerable one-day loss divided by the worst
    historical one, the "about 1" the book prints. ``survives`` is true when
    half-Kelly exceeds it, which is Chan's conclusion that even half-Kelly
    would not have survived that day.

    ``threshold`` is the leverage at which that conclusion turns over, twice
    ``allowed_leverage``. It is reported because the margin is thinner than it
    looks: on Chan's own workbook the as-traded close gives 1.9341 and flips
    the conclusion, so a vintage landing below the threshold flips it the same
    way.

    ``worst_loss`` and ``worst_day`` come from the window the run read.
    ``book_loss`` does not, and the two are kept apart because no SPY vintage
    holds 1987.
    """

    book_loss: float
    book_day: str
    tolerance: float
    allowed_leverage: float
    half_kelly: float
    threshold: float
    survives: bool
    worst_loss: float
    worst_day: str
    full_kelly_equity_loss: float


@dataclass(frozen=True)
class Rebalance:
    """The worked example at locations 2869 and 3021, for one leverage.

    Chan buys ``leverage`` times equity, takes a ``shock`` loss on the
    position, and resizes at the same leverage against whatever equity is left.
    The book's own chain runs on its rounded 2.528 rather than on the exact
    figure, so passing :data:`BOOK_LEVERAGE` reproduces all four of its printed
    numbers and passing a computed leverage says what this vintage implies
    instead.
    """

    leverage: float
    equity: float
    portfolio: float
    debt: float
    shock: float
    shocked_portfolio: float
    shocked_equity: float
    resized: float


def simple_returns(close: pd.Series) -> pd.Series:
    """One-period simple returns, with every non-finite value dropped.

    ``example6_3.m`` drops days carrying a non-finite return before computing
    anything, and so does this. A zero close divides to an infinity rather than
    raising, so a series carrying one would otherwise annualise to a mean of
    ``inf`` and a standard deviation of ``nan``, since the dispersion
    subtracts that mean from it. The reported leverage is then ``nan``, which
    prints and compares without raising anywhere.
    """
    returns = close.pct_change().dropna()
    return returns[np.isfinite(returns)]


def annualised_moments(
    returns: pd.Series,
    *,
    risk_free: float = RISK_FREE,
    periods_per_year: float = TRADING_DAYS,
) -> Moments:
    """Chan's five lines of ``example6_3.m``, in the scalar case.

    The risk-free rate is subtracted per period, ``risk_free /
    periods_per_year`` from each return, which is his
    ``excessRet=ret-repmat(0.04/252, size(ret))``. For the mean that is
    algebraically the same as subtracting the annual rate from the annualised
    mean, and for the standard deviation a constant shift changes nothing, so
    no figure moves. It is written his way because the time-scale check needs a
    per-period rate to be well-posed at all.

    The dispersion is the sample form, dividing by ``n - 1``, which is what
    MATLAB's ``cov`` does. The population form moves the Sharpe ratio by 5.7e-5
    and the leverage by 0.0007, so only an assertion on the first of those can
    tell the two apart at the precision the book prints.
    """
    if len(returns) < 2:
        raise ValueError(
            f"{len(returns)} returns cannot carry a sample standard deviation, which needs at "
            f"least two"
        )
    excess = returns - risk_free / periods_per_year
    period_mean = float(excess.mean())
    period_variance = float(returns.var(ddof=1))
    mean_annual = float(returns.mean()) * periods_per_year
    sd_annual = float(returns.std(ddof=1)) * math.sqrt(periods_per_year)
    excess_annual = period_mean * periods_per_year
    sharpe = excess_annual / sd_annual
    return Moments(
        periods_per_year=periods_per_year,
        returns=len(returns),
        risk_free=risk_free,
        mean_annual=mean_annual,
        sd_annual=sd_annual,
        excess_annual=excess_annual,
        sharpe=sharpe,
        leverage=excess_annual / sd_annual**2,
        period_leverage=period_mean / period_variance,
        # g = r + S^2 / 2, the scalar case of example6_3.m's
        # g=0.04+F'*C*F/2, which is the levered rate location 2849 renders as
        # an image the committed highlights did not capture.
        levered_growth=risk_free + sharpe**2 / 2.0,
        # g = r + m - s^2 / 2 with m excess, which location 2869 prints inline.
        unlevered_growth=risk_free + excess_annual - sd_annual**2 / 2.0,
    )


def resample_close(close: pd.Series, rule: str) -> tuple[pd.Series, float]:
    """The closes one sampling rule keeps, and the periods per year they carry.

    Four rules, because Chan's time-scale claim is about a frequency and the
    word "monthly" names three different series.

    - ``daily`` keeps every bar, 252 periods a year.
    - ``month-end`` keeps the last close of each calendar month, 12 a year.
    - ``month-end-complete`` is the same with a partial final month dropped. A
      month is partial when a weekday falls after the last bar and inside it,
      so a series ending on a Friday that closes its month is kept. A market
      holiday in that tail would be read as partial, which is a limit of
      deciding this from a calendar rather than from an exchange schedule.
    - ``block-21`` keeps every twenty-first bar, which is a month of trading
      days and so also 12 a year.
    """
    if rule not in SAMPLING_RULES:
        raise ValueError(f"sampling rule {rule!r} is not one of {SAMPLING_RULES}")
    if rule == "daily":
        return close, float(TRADING_DAYS)
    if rule == "block-21":
        return close.iloc[::BLOCK_DAYS], TRADING_DAYS / BLOCK_DAYS
    months = close.groupby([close.index.year, close.index.month]).tail(1)
    if rule == "month-end-complete" and _final_month_is_partial(close):
        months = months.iloc[:-1]
    return months, 12.0


def _final_month_is_partial(close: pd.Series) -> bool:
    """Whether a weekday falls after the last bar and inside its own month."""
    last = close.index[-1]
    days_in_month = calendar.monthrange(last.year, last.month)[1]
    if last.day == days_in_month:
        return False
    tail = pd.date_range(
        last + pd.Timedelta(days=1), pd.Timestamp(last.year, last.month, days_in_month)
    )
    return any(day.weekday() < 5 for day in tail)


def stress_test(moments: Moments, returns: pd.Series) -> StressTest:
    """Location 3083's comparison, and whether the conclusion it reaches held.

    ``full_kelly_equity_loss`` is the leverage times the book's one-day loss,
    which is the share of equity a full-Kelly account gives up on such a day.
    The book does not print it. It is reported because it is the thing the
    half-Kelly convention is protecting against, and it is flagged as not a
    published figure rather than left to read as one.
    """
    allowed = DRAWDOWN_TOLERANCE / BLACK_MONDAY_LOSS
    worst = returns.idxmin()
    return StressTest(
        book_loss=BLACK_MONDAY_LOSS,
        book_day=BLACK_MONDAY_DATE,
        tolerance=DRAWDOWN_TOLERANCE,
        allowed_leverage=allowed,
        half_kelly=moments.half_kelly,
        threshold=2.0 * allowed,
        survives=moments.half_kelly > allowed,
        worst_loss=float(returns.min()),
        worst_day=str(pd.Timestamp(worst).date()),
        full_kelly_equity_loss=moments.leverage * BLACK_MONDAY_LOSS,
    )


def rebalance(leverage: float, *, equity: float = EQUITY, shock: float = BOOK_SHOCK) -> Rebalance:
    """Buy at ``leverage``, take a ``shock`` loss, and resize at the same leverage."""
    portfolio = leverage * equity
    shocked_portfolio = portfolio * (1.0 - shock)
    debt = portfolio - equity
    shocked_equity = shocked_portfolio - debt
    return Rebalance(
        leverage=leverage,
        equity=equity,
        portfolio=portfolio,
        debt=debt,
        shock=shock,
        shocked_portfolio=shocked_portfolio,
        shocked_equity=shocked_equity,
        resized=leverage * shocked_equity,
    )


def sampling_scan(close: pd.Series, *, risk_free: float = RISK_FREE) -> dict[str, Moments | None]:
    """Every rule in :data:`SAMPLING_RULES`, or ``None`` where the window is too short.

    A rule that cannot produce two returns has no sample standard deviation, so
    it yields ``None`` and the report says the window is too short for it
    rather than dropping the row without comment.
    """
    scan: dict[str, Moments | None] = {}
    for rule in SAMPLING_RULES:
        sampled, periods = resample_close(close, rule)
        returns = simple_returns(sampled)
        scan[rule] = (
            annualised_moments(returns, risk_free=risk_free, periods_per_year=periods)
            if len(returns) >= 2
            else None
        )
    return scan


# What the book prints beside each computed figure, and at what precision. The
# published values are quoted from locations 2858, 2869 and 3083 and are
# computed nowhere. The decimals are the book's own, which is what decides how
# a gap is stated: a gap is quoted at the coarser of the two precisions.
_PUBLISHED = (
    ("mean annual return", "mean_annual", True, "11.23%", 11.23, 2),
    ("annualised standard deviation", "sd_annual", True, "16.91%", 16.91, 2),
    ("mean excess return", "excess_annual", True, "7.231%", 7.231, 3),
    ("Sharpe ratio", "sharpe", False, "0.4275", 0.4275, 4),
    ("optimal Kelly leverage f*", "leverage", False, "2.528", 2.528, 3),
    ("levered growth rate", "levered_growth", True, "13.14%", 13.14, 2),
    ("unlevered growth rate", "unlevered_growth", True, "9.8%", 9.8, 1),
    ("half-Kelly leverage", "half_kelly", False, "1.26", 1.26, 2),
)


def _published_row(moments: Moments, row: tuple, against_the_book: bool) -> str:
    label, field, as_percent, printed, value, decimals = row
    computed = getattr(moments, field)
    scaled = computed * 100.0 if as_percent else computed
    shown = f"{scaled:.4f}%" if as_percent else f"{scaled:.4f}"
    if not against_the_book:
        return f"  {label:<31} {shown:>12}"
    return f"  {label:<31} {shown:>12}   {printed:>8}   {scaled - value:+.{decimals}f}"


def report(
    entry,
    close: pd.Series,
    *,
    risk_free: float = RISK_FREE,
    equity: float = EQUITY,
) -> None:
    """Print the moments, the worked example, the stress test and the time-scale scan.

    ``entry`` is the manifest entry the reader already resolved, so the vintage
    line is the record rather than a fourth surface restating it.
    """
    returns = simple_returns(close)
    moments = annualised_moments(returns, risk_free=risk_free)
    start, end = close.index[0].date(), close.index[-1].date()
    against_the_book = (str(start), str(end)) == (BOOK_START, BOOK_END)

    print("Kelly leverage on SPY, Example 6.2 (revised edition, locations 2858, 2869 and 3083)")
    print(f"  {BOOK_REF}")
    print(f"  vintage: {vintage_line(entry)}")
    print(f"  window:  {start} .. {end}   ({len(close):,} closes, {len(returns):,} daily returns)")
    print(
        f"  spec:    adjusted close, simple daily returns, mean x {TRADING_DAYS}, "
        f"sample sd (n-1) x sqrt({TRADING_DAYS}),"
    )
    print(
        f"           risk-free {risk_free:.0%} subtracted as {risk_free}/{TRADING_DAYS} per day, "
        f"m is the excess return"
    )
    print()
    if against_the_book:
        print("This is Chan's own window read on a 2026 download, so the gap column is a")
        print("vendor-drift measurement and not a reproduction. He read a 2008-vintage")
        print("adjusted series, and the distributions since have rescaled the history")
        print("behind it. Chan's own workbook is issue 138, not this run.")
        print()
        print(f"  {'quantity':<31} {'this run':>12}   {'the book':>8}   gap")
    else:
        print("This window is not Chan's, so no figure below has a published counterpart")
        print(f"and none carries a gap. The book's own span is {BOOK_START} .. {BOOK_END}.")
        print()
        print(f"  {'quantity':<31} {'this run':>12}")
    for row in _PUBLISHED:
        print(_published_row(moments, row, against_the_book))
    print()

    if moments.leverage < 0.0:
        print(
            f"The leverage is negative. Kelly recommends a short of "
            f"{abs(moments.leverage):.4f} times"
        )
        print("equity, because the mean excess return over this window is negative.")
        print("Nothing has failed and nothing raised. What does not carry across that")
        print("sign change is everything below: half of a negative leverage is a smaller")
        print("short rather than a safer position, and the drawdown comparison measures a")
        print("long position's worst day. Read them as arithmetic rather than as advice,")
        print("and note that a window picked for its losses is a sample spent looking.")
        print()

    _worked_example(moments, equity)
    _stress(stress_test(moments, returns), moments)
    _time_scale(close, moments, risk_free)

    print("A replication against data is exploratory by construction. The sample was")
    print("spent on a hypothesis Chan chose, so this run says whether his figures")
    print("reproduce and nothing about whether leverage of this size is a good idea.")
    print(f"The {risk_free:.0%} is his constant applied to whatever window was read, not a")
    print("rate anyone paid, and a leverage computed from one sample's moments is a")
    print("reference point rather than a recommendation.")
    print("docs/replication-log.md Entry 3 carries the verdict.")


def _worked_example(moments: Moments, equity: float) -> None:
    """Locations 2869 and 3021, run twice: on this vintage and on the book's 2.528."""
    mine = rebalance(moments.leverage, equity=equity)
    book = rebalance(BOOK_LEVERAGE, equity=equity)
    print(f"The worked example at locations 2869 and 3021, on ${equity:,.0f} of equity:")
    # Both headers are built from the leverage the column was computed at, so
    # neither can drift into naming a number the column below it did not use.
    print(
        f"  {'':<28} {'at f* = ' + format(moments.leverage, '.4f'):>16}   "
        f"{'at ' + format(BOOK_LEVERAGE, 'g'):>16}"
    )
    for label, field in (
        ("portfolio", "portfolio"),
        ("borrowed", "debt"),
        (f"after SPY falls {book.shock:.0%}", "shocked_portfolio"),
        ("equity left", "shocked_equity"),
        ("resized at the same leverage", "resized"),
    ):
        left = f"${getattr(mine, field):,.2f}"
        right = f"${getattr(book, field):,.2f}"
        print(f"  {label:<28} {left:>16}   {right:>16}")
    print("  The book prints $252,800, $227,520, $74,720 and $188,892. All four are")
    print("  arithmetic on its own rounded 2.528, so the right column reproduces them")
    print("  exactly and the left says what this vintage implies instead.")
    print()


def _stress(stress: StressTest, moments: Moments) -> None:
    """Location 3083, with the book constant and the vintage's own worst day apart."""
    print("The stress test at location 3083:")
    print(
        f"  {'worst one-day S&P 500 loss':<36}{stress.book_loss:>9.2%} on {stress.book_day}"
        f"   <- a book constant, outside SPY"
    )
    print(
        f"  {'worst one-day loss in this window':<36}{abs(stress.worst_loss):>9.2%} "
        f"on {stress.worst_day}"
    )
    print(
        f"  {'a ' + format(stress.tolerance, '.0%') + ' one-day tolerance allows':<36}"
        f'{stress.allowed_leverage:>9.6f}   (the book\'s "about 1")'
    )
    print(f"  {'half-Kelly here':<36}{stress.half_kelly:>9.6f}")
    if moments.leverage < 0.0:
        print("  Chan's conclusion is about a levered long position and this window")
        print("  recommends a short, so the comparison is not made. See the note above.")
        print()
        return
    verdict = "SURVIVES" if stress.survives else "DOES NOT SURVIVE"
    print(f"  Chan's conclusion, that even half-Kelly would not have survived that day: {verdict}")
    print(
        f"    it holds exactly while f* is above {stress.threshold:.6f}, and f* is "
        f"{moments.leverage:.6f} here"
    )
    print(
        f"  not a figure the book prints: at full Kelly that day costs "
        f"{stress.full_kelly_equity_loss:.2%} of equity"
    )
    print()


def _time_scale(close: pd.Series, daily: Moments, risk_free: float) -> None:
    """The identity, then the resampling that actually moves the answer."""
    print("Time-scale independence, which is two claims rather than one:")
    print(
        f"  as an identity it holds exactly. f* from the annualised moments is "
        f"{daily.leverage:.10f}"
    )
    print(
        f"  and from the same moments before annualising it is "
        f"{daily.period_leverage:.10f}, because"
    )
    print("  the factor cancels between the mean and the variance. Testing that proves")
    print("  nothing about the data.")
    print()
    print('  Resampling is what moves it, and "monthly" names three different series.')
    print(
        f"  Each rule subtracts the rate over its own period, {risk_free}/252 a day and "
        f"{risk_free}/12 a month,"
    )
    print("  because a daily f* needs a daily r and the identity above breaks without it:")
    print(f"  {'rule':<20} {'returns':>8} {'mean':>10} {'sd':>10} {'f*':>10} {'vs daily':>10}")
    for rule, moments in sampling_scan(close, risk_free=risk_free).items():
        if moments is None:
            print(f"  {rule:<20} {'too few returns in this window':>50}")
            continue
        against = "" if rule == "daily" else f"{moments.leverage / daily.leverage - 1.0:+.1%}"
        print(
            f"  {rule:<20} {moments.returns:>8,} {moments.mean_annual:>10.4f} "
            f"{moments.sd_annual:>10.4f} {moments.leverage:>10.4f} {against:>10}".rstrip()
        )
    print("  So the claim is exactly true as an identity and wrong on the data, and")
    print("  the run says which of the two it is showing.")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Chan's Kelly leverage on SPY, Example 6.2, against a committed vintage"
    )
    parser.add_argument(
        "--start", default=BOOK_START, help=f"window start, inclusive (default: {BOOK_START})"
    )
    parser.add_argument(
        "--end", default=BOOK_END, help=f"window end, inclusive (default: {BOOK_END})"
    )
    parser.add_argument(
        "--dated",
        default=VINTAGE_DATE,
        help=f"which SPY download to read, by its date (default: {VINTAGE_DATE})",
    )
    parser.add_argument(
        "--risk-free",
        type=float,
        default=RISK_FREE,
        help=f"annual risk-free rate (default: {RISK_FREE}, the book's constant)",
    )
    args = parser.parse_args()
    try:
        run(start=args.start, end=args.end, dated=args.dated, risk_free=args.risk_free)
    except VintageUnavailable as unavailable:
        # A refusal that names which vintage and which state is worth nothing at
        # the bottom of a twenty-line pandas traceback. `run` already exits this
        # way for a window with too few trading days, so this follows it.
        raise SystemExit(str(unavailable)) from unavailable


def run(
    *,
    start: str = BOOK_START,
    end: str = BOOK_END,
    dated: str = VINTAGE_DATE,
    risk_free: float = RISK_FREE,
    data_dir: Path | None = None,
) -> None:
    """Read the vintage, clip it to the window, and print the report."""
    entry, close = load_vintage("SPY", dated=dated, data_dir=data_dir)
    clipped = close[(close.index >= pd.Timestamp(start)) & (close.index <= pd.Timestamp(end))]
    if len(clipped) < MIN_TRADING_DAYS:
        raise SystemExit(
            f"only {len(clipped)} trading days in {start}..{end} -- need >= {MIN_TRADING_DAYS} "
            f"(the vintage spans {entry.first_date}..{entry.last_date})"
        )
    report(entry, clipped, risk_free=risk_free)


if __name__ == "__main__":
    main()
