"""AUD.CAD with rollover interest, *Algorithmic Trading*'s Example 5.2.

A currency position held past 5 p.m. New York time earns or pays the
difference between the two currencies' interest rates, and Chan uses this
example to show how that rollover interest enters a currency strategy's excess
return. At Kindle location 2303 he trades the AUD.CAD cross rate with a linear
mean-reverting rule and reports "an APR of 6.2 percent, with a Sharpe ratio of
0.54", and 6.7 percent and 0.58 without the rollover, "even though the
annualized average rollover interest would amount to almost 5 percent".

**The transcription.** ``AUDCAD_daily.m`` was read in the mirror
[ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) at
``e4bc46f``, under ``public/img/book2/``, git blob ``823983a``, and landed here
for [issue 346](https://github.com/l3a0/quantitative-trading/issues/346). Line
numbers count from the script's first line, ``clear;``.

1. Lines 3 to 8 set ``lookback = 20`` and keep the 16:59 bar of each day of a
   minute ``.mat`` that neither mirror holds. The run reads the Python port's
   daily file instead, through :func:`chan.series.load_port_close`, and filters
   nothing.
2. Lines 11 to 21 and 26 to 33 give each trading day the rate of its own
   calendar month, and 0 where the file holds no such month. Nothing is
   carried forward. Then the rate is divided by 365 and by 100, in that order,
   so the bits match MATLAB's. :func:`daily_rates` is those lines.
3. Lines 22 to 24 and 34 to 36 triple AUD's daily rate on every Wednesday,
   MATLAB's ``weekday == 4``, and CAD's on every Thursday, ``weekday == 5``.
   In pandas those are weekdays 2 and 3. No holiday multiplies anything.
4. Lines 38 to 40 take ``z = (cl − movingAvg(cl, 20)) / movingStd(cl, 20)``,
   which are :func:`chan.matlab_helpers.moving_avg` and
   :func:`chan.matlab_helpers.moving_std`. :func:`zscore` is those lines.
5. Line 43 is the return, ``lag(−sign(z), 1) .* (log(cl) + lag(−log(cl) +
   log(1 + aud) − log(1 + cad), 1))``. The position is minus the sign of
   yesterday's z rather than minus z, and the rollover term carries
   yesterday's rates. ``lag`` is :func:`chan.matlab_helpers.lag1`. Chan's
   ``lag`` pads with NaN and jplv7's with zeros, and every row is the same
   under either, because rows 1 to 20 come out 0 both ways. The run takes
   ``np.log(1 + x)`` rather than ``np.log1p`` and keeps the line's order of
   additions, so the arithmetic is MATLAB's. Line 45 sets every NaN to 0.
   :func:`linear_returns` is lines 43 and 45.
6. Line 44, commented out, is the return without rollover. It equals line 43
   with both rate arrays at zero, bit for bit, since adding ``log(1)`` adds an
   exact zero, so the run calls :func:`linear_returns` twice rather than
   writing a second formula.
7. Line 49 prints ``prod(1 + ret)^(252 / 1237) − 1`` over all 1,237 rows, the
   20 zeros included, and ``√252 · mean / std`` with n − 1 and no risk-free
   rate. They are :func:`chan.khandani_lo_book_two.compounded_apr` and
   :func:`chan.khandani_lo.plain_sharpe`. The script compounds a log return as
   if it were simple, and the run does the same. Line 50 is its printout,
   ``APR=0.061564 Sharpe=0.541802``.

**What changed on the way over.** Four things, and none moves a figure.

1. The closes and rates are read as committed vintages, through
   :func:`chan.series.load_port_close` and :func:`chan.series.load_rates`,
   rather than from the ``.mat`` files.
2. The ``plot`` on line 47 is not carried. The run draws nothing.
3. The run calls the scale-break guard, which the script has no counterpart
   for.
4. Rows the script does not print are computed beside it: the two figures
   without rollover, the annualised rollover, and the rows beside the
   replication below.

**The settlement rule the script applies is not the one the book states.**
Location 2273 says a cross triples its rollover when day T + 3 is a weekend,
which is Wednesday for both currencies, and names T + 1 settlement as the
exception for USD.CAD. The script triples CAD on Thursday, which is the USD.CAD
rule applied to one leg of a cross. The run transcribes the script, because the
script is what printed the figures.

**Row 5's criterion was written before the row was computed.** Location 2273
defines the rollover on a long B.Q position as the differential iB − iQ. So the
annualised rollover is 252 times the mean, over all 1,237 rows, of the term
line 43 adds to a long position, ``lag(log(1 + aud) − log(1 + cad), 1)`` with
its first row set to 0. Issue 346 wrote on 2026-10-05 that "almost 5 percent"
holds when that value is at least 0.045 and below 0.050, knowing only that the
monthly rates average 4.908 percent for AUD and 1.592 for CAD from July 2007.
The AUD rate alone, annualised the same way, is reported beside it, because
those two means predicted that the book's figure might describe it rather than
the differential. So is the differential annualised over 365 days, the
script's own rate divisor, which the review found lands inside the criterion
too.

**The scale-break guard is called and refuses nothing.** The run calls
:func:`chan.series.refuse_window_crossing_a_break` on the AUD.CAD closes over
the file's whole span, 2007-07-23 to 2012-04-26, as
:mod:`chan.usdcad_mean_reversion` does. The guard reads prices, so the rate
files are not passed to it.

Every result here is exploratory. Reproducing Chan's figures spends the 2007
to 2012 sample on a rule he chose, so the run says whether his numbers
reproduce on his files and nothing about whether the cross rate reverts today.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from chan.khandani_lo import TRADING_DAYS, plain_sharpe
from chan.khandani_lo_book_two import compounded_apr, gap, matches
from chan.matlab_helpers import lag1, moving_avg, moving_std
from chan.series import (
    WindowCrossesScaleBreak,
    load_port_close,
    load_rates,
    refuse_window_crossing_a_break,
    vintage_line,
)
from chan.vintage import VintageEntry, VintageUnavailable

SYMBOL = "AUDCAD"
#: The manifest's symbols for the two monthly rate files.
AUD_RATE, CAD_RATE = "AUDRATE", "CADRATE"

#: ``lookback``, script line 3.
SCRIPT_LOOKBACK = 20
#: The divisors of lines 21 and 33: days in a year, then percent.
DAYS_IN_YEAR = 365
PERCENT = 100
#: Lines 23 and 35 in pandas' numbering, where Monday is 0.
AUD_TRIPLE_WEEKDAY = 2
CAD_TRIPLE_WEEKDAY = 3
#: How many days a tripled rollover covers.
TRIPLE = 3

#: Script line 50.
SCRIPT_APR = "0.061564"
SCRIPT_SHARPE = "0.541802"
#: Location 2303, with and without rollover.
BOOK_APR_PERCENT = "6.2"
BOOK_SHARPE = "0.54"
BOOK_APR_WITHOUT_PERCENT = "6.7"
BOOK_SHARPE_WITHOUT = "0.58"
BOOK_ROLLOVER = "almost 5 percent"

#: Row 5's criterion, declared on issue 346 before the row was computed.
#:
#: At least the floor and below the ceiling, because "almost 5 percent" says
#: below 5 and close enough to round to it.
ROLLOVER_FLOOR = 0.045
ROLLOVER_CEILING = 0.050


def daily_rates(
    monthly: pd.Series,
    days: pd.DatetimeIndex,
    triple_weekday: int,
    *,
    carry_forward: bool = False,
) -> NDArray[np.float64]:
    """Lines 11 to 24, or 12 and 26 to 36: each day's rate as a fraction, tripled on one weekday.

    ``monthly`` is a rate file as :func:`chan.series.load_rates` returns it,
    in percent a year and indexed by the first of each month. Each day takes
    its own month's rate, and 0 where ``monthly`` holds no such month, which
    is the script's zero fill. ``carry_forward`` instead gives such a day the
    rate of the last month before it that ``monthly`` holds, which is the row
    beside the replication that measures what the zero fill moved. The
    months are sorted first, because the carried rate is found by position.
    """
    monthly = monthly.sort_index()
    month_of_day = days.to_period("M")
    held = monthly.index.to_period("M")
    if carry_forward:
        position = held.searchsorted(month_of_day, side="right") - 1
        known = position >= 0
        rates = np.where(known, monthly.to_numpy()[np.maximum(position, 0)], 0.0)
    else:
        lookup = dict(zip(held, monthly.to_numpy(), strict=True))
        rates = np.array([lookup.get(month, 0.0) for month in month_of_day], dtype=float)
    rates = rates / DAYS_IN_YEAR / PERCENT
    tripled = days.weekday == triple_weekday
    rates[tripled] = TRIPLE * rates[tripled]
    return rates


def zscore(closes: NDArray[np.float64], lookback: int) -> NDArray[np.float64]:
    """Lines 38 to 40: the close's distance from its moving average in moving deviations."""
    return (closes - moving_avg(closes, lookback)) / moving_std(closes, lookback)


def linear_returns(
    closes: NDArray[np.float64],
    position: NDArray[np.float64],
    aud: NDArray[np.float64],
    cad: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Lines 43 and 45: yesterday's position times the log move plus yesterday's rollover.

    ``position`` is ``−sign(z)``. The rollover term ``log(1 + aud) − log(1 +
    cad)`` sits inside the second ``lag``, so day t's return carries day
    t − 1's rates as well as its position. A row that is not a number is 0.
    """
    log_closes = np.log(closes)
    returns = lag1(position) * (log_closes + lag1(-log_closes + np.log(1 + aud) - np.log(1 + cad)))
    return np.where(np.isnan(returns), 0.0, returns)


def annualised_rollover(
    aud: NDArray[np.float64], cad: NDArray[np.float64], *, days_a_year: int = TRADING_DAYS
) -> float:
    """Row 5: 252 times the mean of the rollover a long position earns, over every row.

    The term is the one line 43 adds to a long position, lagged as line 43
    lags it, with its first row set to 0 as line 45 would. ``days_a_year`` is
    365 for row 8, the reading that annualises with the script's rate divisor.
    """
    term = lag1(np.log(1 + aud) - np.log(1 + cad))
    term[0] = 0.0
    return float(days_a_year * term.mean())


@dataclass(frozen=True)
class Figures:
    """Line 49's two figures over one series of returns."""

    apr: float
    sharpe: float


def figures(returns: NDArray[np.float64]) -> Figures:
    return Figures(apr=compounded_apr(returns), sharpe=plain_sharpe(returns))


@dataclass(frozen=True)
class Rollover:
    """The script on the cross rate, the five rows, and the two rows beside them.

    ``aud`` and ``cad`` are the daily rates line 43 reads. ``returns`` is line
    43's series and ``without`` line 44's. ``carried`` is line 43 again with
    each missing month carried forward, ``aud_alone`` is row 5's arithmetic
    on the AUD rate alone, and ``over_365_days`` is row 5 annualised over 365
    days.
    """

    days: pd.DatetimeIndex
    aud: NDArray[np.float64]
    cad: NDArray[np.float64]
    position: NDArray[np.float64]
    returns: NDArray[np.float64]
    without: NDArray[np.float64]
    rollover: float
    aud_alone: float
    over_365_days: float
    carried: Figures

    @property
    def with_rollover(self) -> Figures:
        """Rows 1 and 2."""
        return figures(self.returns)

    @property
    def without_rollover(self) -> Figures:
        """Rows 3 and 4."""
        return figures(self.without)

    @property
    def rollover_drag(self) -> float:
        """What rollover added to the strategy a year: 252 times the mean of line 43 less 44."""
        return float(TRADING_DAYS * np.mean(self.returns - self.without))

    @property
    def rollover_holds(self) -> bool:
        """Whether row 5 meets the criterion declared on issue 346."""
        return ROLLOVER_FLOOR <= self.rollover < ROLLOVER_CEILING


def aud_cad_rollover(closes: pd.Series, aud_monthly: pd.Series, cad_monthly: pd.Series) -> Rollover:
    """Run ``AUDCAD_daily.m`` on ``closes``, and the rows beside it."""
    days = pd.DatetimeIndex(closes.index)
    cl = closes.to_numpy(dtype=float)
    aud = daily_rates(aud_monthly, days, AUD_TRIPLE_WEEKDAY)
    cad = daily_rates(cad_monthly, days, CAD_TRIPLE_WEEKDAY)
    position = -np.sign(zscore(cl, SCRIPT_LOOKBACK))
    zero = np.zeros_like(cl)
    carried = linear_returns(
        cl,
        position,
        daily_rates(aud_monthly, days, AUD_TRIPLE_WEEKDAY, carry_forward=True),
        daily_rates(cad_monthly, days, CAD_TRIPLE_WEEKDAY, carry_forward=True),
    )
    return Rollover(
        days=days,
        aud=aud,
        cad=cad,
        position=position,
        returns=linear_returns(cl, position, aud, cad),
        without=linear_returns(cl, position, zero, zero),
        rollover=annualised_rollover(aud, cad),
        aud_alone=annualised_rollover(aud, zero),
        over_365_days=annualised_rollover(aud, cad, days_a_year=DAYS_IN_YEAR),
        carried=figures(carried),
    )


@dataclass(frozen=True)
class Sources:
    """The cross rate's closes and the two rate files, each with the entry it was read from."""

    closes: tuple[VintageEntry, pd.Series]
    aud: tuple[VintageEntry, pd.Series]
    cad: tuple[VintageEntry, pd.Series]

    @property
    def entries(self) -> list[VintageEntry]:
        return [self.closes[0], self.aud[0], self.cad[0]]


def read_sources(data_dir: Path | None = None) -> Sources:
    """The AUD.CAD closes, refused if they span a scale break, and the two rate files."""
    closes = load_port_close(SYMBOL, data_dir=data_dir)
    days = closes[1].index
    refuse_window_crossing_a_break([closes], start=days[0], end=days[-1])
    return Sources(
        closes=closes,
        aud=load_rates(AUD_RATE, data_dir=data_dir),
        cad=load_rates(CAD_RATE, data_dir=data_dir),
    )


def _verdict(value: float, printed: str) -> str:
    return (
        "reproduced"
        if matches(value, printed)
        else f"did not reproduce, gap {gap(value, printed):+g}"
    )


def report(sources: Sources, result: Rollover) -> None:
    """Print the vintages, each published figure beside the computed one, and the rows beside."""
    print("AUD.CAD with rollover interest, Algorithmic Trading's Example 5.2")
    for entry in sources.entries:
        print(f"  vintage  {vintage_line(entry)}")
    days = result.days
    print(f"  window   {days[0].date()} to {days[-1].date()}, {len(days)} days")
    print(
        f"  rule     minus the sign of a {SCRIPT_LOOKBACK}-row z-score, held from the next day, "
        "AUD tripled on Wednesdays and CAD on Thursdays"
    )
    print(
        f"  zero     {int(np.count_nonzero(result.aud == 0))} days carry no AUD rate and "
        f"{int(np.count_nonzero(result.cad == 0))} no CAD rate"
    )
    print()
    have, lack = result.with_rollover, result.without_rollover
    rows = [
        ("1 APR with rollover, script", have.apr, SCRIPT_APR),
        ("1 APR percent, book", 100 * have.apr, BOOK_APR_PERCENT),
        ("2 Sharpe with rollover, script", have.sharpe, SCRIPT_SHARPE),
        ("2 Sharpe, book", have.sharpe, BOOK_SHARPE),
        ("3 APR percent without, book", 100 * lack.apr, BOOK_APR_WITHOUT_PERCENT),
        ("4 Sharpe without, book", lack.sharpe, BOOK_SHARPE_WITHOUT),
    ]
    print(f"  {'Row':<30} {'Computed':>12}  {'Chan':>12}  Verdict")
    for label, value, printed in rows:
        print(f"  {label:<30} {value:>12.6f}  {printed:>12}  {_verdict(value, printed)}")
    print(
        f"  {'5 annualised rollover':<30} {result.rollover:>12.6f}  {BOOK_ROLLOVER:>12}  "
        f"{'reproduced' if result.rollover_holds else 'did not reproduce'}, criterion at least "
        f"{ROLLOVER_FLOOR} and below {ROLLOVER_CEILING}"
    )
    print()
    print("Beside the replication. No book prints these, so none carries a verdict.")
    print(f"  row 5 on the AUD rate alone      {result.aud_alone:.6f}")
    print(f"  row 5 annualised over 365 days   {result.over_365_days:.6f}")
    print(f"  rollover the strategy earned     {result.rollover_drag:.6f} a year")
    print(
        f"  rows 1 and 2, months carried     APR {result.carried.apr:.6f}, "
        f"Sharpe {result.carried.sharpe:.6f}"
    )
    print()
    print(
        f"  Annualised over {TRADING_DAYS} days, log returns compounded as simple ones, with no "
        "risk-free rate and no cost."
    )
    print("  Exploratory. docs/replication-log.md carries the verdicts.")


def run(data_dir: Path | None = None) -> Rollover:
    """Read the vintages, guard the closes, run the script, and print the report."""
    sources = read_sources(data_dir)
    result = aud_cad_rollover(sources.closes[1], sources.aud[1], sources.cad[1])
    report(sources, result)
    return result


def main() -> None:
    argparse.ArgumentParser(
        description="AUD.CAD with rollover interest, Algorithmic Trading's Example 5.2"
    ).parse_args()
    try:
        run()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day reaches the reader
        # as one line, the way chan.pead.main does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
