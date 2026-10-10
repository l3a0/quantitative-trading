"""Mean reversion on crude oil's 12-month calendar spread, *Algorithmic Trading*'s Example 5.4.

A calendar spread is long one contract of a future and short another of the
same future a fixed number of months away. Its log value moves with the roll
return γ and not with the spot price, because the spot cancels between the
two legs. So a γ that mean-reverts gives a spread that mean-reverts. Chan's
Example 5.4, at Kindle locations 2461 and 2471, finds the 12-month log
calendar spread of CL "stationary with 99 percent probability, and a
half-life of 36 days". Trading it with linear mean reversion gives "an APR of
8.3 percent and a Sharpe ratio of 1.3 from January 2, 2008, to August 13,
2012."

**The transcription.** Every step is Chan's ``calendarSpdsMeanReversion.m``,
read under ``public/img/book2/`` in the mirror
[ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) at
``e4bc46f``, git blob ``277d84d``. Its line numbers here count from the
script's first line, ``clear;``.

1. **γ**, lines 28 to 42, is :func:`chan.roll_returns.roll_returns` on the
   strip's contracts, forward-filled as ``fillMissingData`` does. That
   function is the same loop, and it equals the script's own bit for bit on
   all 6,467 rows of CL.
2. **The test**, lines 51 to 60. :func:`chan.stationarity_tests.jplv7_adf`
   at order 0 and one lag, and :func:`ithildincore.timeseries.ou_half_life`,
   both on the filled γ's finite rows.
3. **The z-score**, lines 66 to 69, is :func:`chan.price_spread.zscore` over
   a lookback of the half-life rounded half away from zero, as MATLAB's
   ``round`` does.
4. **The schedule**, lines 72 to 102, is :func:`calendar_schedule`. Line 75
   marks a contract expired on each priced row whose next row is not priced,
   and line 83 takes the last such mark. Pair ``c`` is short contract ``c``
   and long contract ``c + spread_month``. The first pair is held from
   ``holddays + 10`` rows before its expiry, and every later pair from the
   day after the previous pair's last day. Each pair stops 10 rows before its
   own expiry. A later pair whose window is shorter than ``holddays`` rows is
   skipped, and the next pair starts after the last pair that was held,
   because line 94 sets the start to NaN and leaves the end alone. Line 98
   then holds a pair only when its end is strictly after its start.
5. **The flip**, lines 106 and 107, is :func:`flip_on_zscore`. It zeroes
   every row whose z-score is NaN and reverses the spread on every row whose
   z-score is above 0.
6. **The return**, lines 110 and 111, is :func:`spread_returns`. It sums
   yesterday's positions times each leg's return with
   :func:`chan.matlab_helpers.smartsum`, divides by 2, and sets a NaN row
   to 0.
7. **The figures**, lines 113 to 122, read the rows from 2008-01-02. The APR
   is :func:`chan.khandani_lo_book_two.compounded_apr`, the Sharpe ratio
   :func:`chan.khandani_lo.plain_sharpe`, and the drawdown
   :func:`chan.matlab_helpers.calculate_max_dd` on ``cumprod(1 + r) − 1``.

Neither mirror holds ``lag.m``, so line 110's ``lag`` is LeSage's, which pads
its first row with 0. That pad moves nothing here. A zero pad divides by a
price of 0, so the first row is NaN either way, line 111 sets it to 0, and the
row falls before the window. :func:`chan.matlab_helpers.backshift` pads with
NaN, as :mod:`chan.price_spread` says of the same line.

**``spread_month`` counts columns.** Line 81's loop pairs contract ``c`` with
contract ``c + spreadMonth`` by position, though line 80's comment calls it a
number of months, the way :mod:`chan.roll_returns` says the script measures
maturity in columns. On CL and VX each column is one month after the last, so
the two readings agree. On TU, whose contracts are quarterly, contract
``c + 12`` is 36 months on, and nothing here refuses such a strip.

**The comment's figures land one row later.** The script's closing comment
prints an APR of 0.083406 and a Sharpe ratio of 1.288661. The script as
written, from 2008-01-02, gives 0.082671 and 1.278216, which round to the
book's 8.3 percent and 1.3 and miss the comment. Starting at 2008-01-03 lands
the comment to every printed digit. A scan on
[issue 348](https://github.com/l3a0/quantitative-trading/issues/348) found that
window the only one within 1e-6 on both figures, and the suite does not run
the scan. So
the specification keeps the window the script states, and :func:`run` carries
the later start beside it with no verdict. The script's ``holddays=3*21`` is
63 rows, where the book says "3 months (61 trading days)", so :func:`run`
carries a 61-row hold beside it too.

**The vintage and the guard** are :func:`chan.roll_returns.load_strip`'s.
It reads ``inputDataDaily_CL_20120813.mat``'s committed strip, the file the
script's load line names, and runs the scale-break guard on every member over
its own rows. That module's docstring says why.

**What issue 349 imports.** :func:`calendar_schedule`, :func:`run_spread` and
:class:`CalendarSpreadRun` are the contract that
[issue 349](https://github.com/l3a0/quantitative-trading/issues/349) builds
against, running this script on VX with signals of its own.

1. :func:`run_spread` forward-fills the signal before the half-life and the
   ADF read it, as line 42 fills γ, and takes both on every finite row of the
   filled signal rather than on the window, as lines 51 to 60 do.
2. It refuses a signal whose index does not equal ``contracts.index``,
   because a signal built in another module on a shifted index of the same
   length would align silently.
3. ``positions`` is the flipped frame on every row, and ``last_held`` reads
   the unflipped schedule, because issue 349's tables were measured that way.

:func:`flip_on_zscore` and :func:`spread_returns` are public so the tests can
hold each step on a frame small enough to read.

**What changed on the way over.** Three things, and none moves a figure.

1. The strip is read as a committed vintage through
   :func:`chan.roll_returns.load_strip` rather than loaded from the ``.mat``,
   and the guard runs on it, which the script has no counterpart for.
2. The plot of the cumulative return is not carried. The run draws nothing.
3. The later start and the 61-row hold run beside the script as written,
   each changing one thing.

Every result here is exploratory. Reproducing Chan's figures spends the 2008
to 2012 sample on a rule he chose, and the later start was found by a scan
after the script as written missed two of the comment's figures. So the run
says whether his numbers reproduce on his file and nothing about whether the
spread reverts today.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from ithildincore.timeseries import ou_half_life

from chan.khandani_lo import TRADING_DAYS, plain_sharpe
from chan.khandani_lo_book_two import compounded_apr, gap, matches
from chan.matlab_helpers import (
    backshift,
    calculate_max_dd,
    fwdshift,
    round_half_away,
    smartsum,
)
from chan.price_spread import zscore
from chan.roll_returns import Strip, load_strip, roll_returns
from chan.series import WindowCrossesScaleBreak, panel_line
from chan.stationarity_tests import Jplv7Adf, jplv7_adf
from chan.vintage import VintageUnavailable

#: The strip line 4 loads.
ROOT = "CL"
#: ``spreadMonth=12``, counted in columns as line 81's loop counts it.
SPREAD_MONTH = 12
#: ``holddays=3*21``, line 77.
HOLDDAYS = 3 * 21
#: The book's "3 months (61 trading days)", run beside the script with no verdict.
BOOK_HOLDDAYS = 61
#: ``numDaysEnd=10``, line 79. ``numDaysStart`` is ``holddays`` plus this.
NUM_DAYS_END = 10

#: ``idx=find(tday==20080102)``, line 113.
START = pd.Timestamp("2008-01-02")
#: The start that lands the comment's figures, one row after the script's.
COMMENT_START = pd.Timestamp("2008-01-03")

#: What the script's comments print, lines 63, 123 and 124.
SCRIPT_HALFLIFE = "36.394034"
SCRIPT_APR = "0.083406"
SCRIPT_SHARPE = "1.288661"
SCRIPT_MAX_DD = "-0.053222"
SCRIPT_MAX_DD_DAYS = "206"
#: What locations 2461 and 2471 print. The APR is compared against 100 times the APR.
BOOK_APR_PERCENT = "8.3"
BOOK_SHARPE = "1.3"
BOOK_HALFLIFE = "36"


@dataclass(frozen=True)
class CalendarSpreadRun:
    """One run of the script on one signal, from its ADF test to its last held day.

    ``positions`` is the flipped schedule on every row of the strip, and
    ``returns`` holds the window's rows only. ``last_held`` is the last row of
    the unflipped schedule holding a position on or before the window's last
    row.
    """

    adf: Jplv7Adf
    half_life: float
    lookback: int
    positions: pd.DataFrame
    returns: pd.Series
    apr: float
    sharpe: float
    max_dd: float
    max_dd_days: int
    last_held: pd.Timestamp


def calendar_schedule(
    contracts: pd.DataFrame,
    *,
    spread_month: int = SPREAD_MONTH,
    holddays: int = HOLDDAYS,
) -> pd.DataFrame:
    """Lines 72 to 102: −1 on each held pair's near contract and +1 on its far one.

    The rows run from each pair's start to its end, both included, on
    ``contracts``' index and columns. The module docstring states the rule.
    """
    prices = contracts.to_numpy(dtype=float)
    expired = np.isfinite(prices) & ~np.isfinite(fwdshift(1, prices))
    positions = np.zeros_like(prices)
    num_days_start = holddays + NUM_DAYS_END
    start: int | None = None
    end = 0
    for c in range(prices.shape[1] - spread_month):
        expiry = int(np.flatnonzero(expired[:, c])[-1])
        if c == 0:
            start = max(0, expiry - num_days_start)
            end = expiry - NUM_DAYS_END
        else:
            my_start = end + 1
            my_end = expiry - NUM_DAYS_END
            if my_end - my_start >= holddays:
                start, end = my_start, my_end
            else:
                # Line 94 sets the start to NaN, and line 98's comparison
                # against NaN is false, so the pair is skipped.
                start = None
        if start is not None and end > start:
            positions[start : end + 1, c] = -1
            positions[start : end + 1, c + spread_month] = 1
    return pd.DataFrame(positions, index=contracts.index, columns=contracts.columns)


def flip_on_zscore(schedule: pd.DataFrame, z: pd.Series) -> pd.DataFrame:
    """Lines 106 and 107: flat where z is NaN, the spread reversed where z is above 0."""
    values = z.to_numpy(dtype=float)
    positions = schedule.to_numpy(dtype=float).copy()
    positions[np.isnan(values), :] = 0
    above = values > 0
    positions[above, :] = -positions[above, :]
    return pd.DataFrame(positions, index=schedule.index, columns=schedule.columns)


def spread_returns(positions: pd.DataFrame, contracts: pd.DataFrame) -> pd.Series:
    """Lines 110 and 111: yesterday's positions times each leg's return, summed, over 2.

    The sum skips a NaN leg, and a row with no finite leg is NaN and then 0.
    """
    held = backshift(1, positions.to_numpy(dtype=float))
    prices = contracts.to_numpy(dtype=float)
    before = backshift(1, prices)
    with np.errstate(invalid="ignore", divide="ignore"):
        legs = held * (prices - before) / before
    daily = np.asarray(smartsum(legs, axis=1), dtype=float) / 2
    daily[np.isnan(daily)] = 0
    return pd.Series(daily, index=contracts.index, name="returns")


def run_spread(
    contracts: pd.DataFrame,
    signal: pd.Series,
    *,
    start: pd.Timestamp,
    end: pd.Timestamp | None = None,
    spread_month: int = SPREAD_MONTH,
    holddays: int = HOLDDAYS,
    lookback: int | None = None,
) -> CalendarSpreadRun:
    """The script on ``signal``, measured over ``start`` to ``end``, both included.

    The signal is forward-filled first, and the half-life and the ADF test
    read every finite row of the filled signal. ``lookback`` defaults to the
    half-life rounded half away from zero, and ``end`` to the strip's last row.
    """
    if not signal.index.equals(contracts.index):
        raise ValueError(
            "run_spread takes a signal on the contracts' own index, and this one differs, "
            "so its rows would not line up with the prices"
        )
    filled = signal.astype(float).ffill()
    finite = filled.to_numpy()[np.isfinite(filled.to_numpy())]
    adf = jplv7_adf(finite, 0, 1)
    half_life = ou_half_life(finite)
    if lookback is None:
        lookback = int(round_half_away(half_life))
    schedule = calendar_schedule(contracts, spread_month=spread_month, holddays=holddays)
    z = pd.Series(zscore(filled.to_numpy(), lookback), index=contracts.index)
    positions = flip_on_zscore(schedule, z)
    returns = spread_returns(positions, contracts).loc[start:end]
    daily = returns.to_numpy()
    max_dd, max_dd_days = calculate_max_dd(np.cumprod(1 + daily) - 1)
    held = schedule.index[(schedule.to_numpy() != 0).any(axis=1)]
    return CalendarSpreadRun(
        adf=adf,
        half_life=half_life,
        lookback=lookback,
        positions=positions,
        returns=returns,
        apr=compounded_apr(daily),
        sharpe=plain_sharpe(daily),
        max_dd=max_dd,
        max_dd_days=max_dd_days,
        last_held=held[held <= returns.index[-1]][-1],
    )


def _verdict(value: float, printed: str) -> str:
    return (
        "reproduced"
        if matches(value, printed)
        else f"did not reproduce, gap {gap(value, printed):+g}"
    )


def _span(days: pd.DatetimeIndex) -> str:
    return f"{days[0].date()} to {days[-1].date()}, {len(days)} days"


def report(strip: Strip, runs: dict[str, CalendarSpreadRun]) -> None:
    """Print the vintage, each printed figure beside S's, the ADF claim, and the rows beside."""
    s = runs["S"]
    print(
        "Mean reversion on crude oil's 12-month calendar spread, Algorithmic Trading's Example 5.4"
    )
    print(f"  vintage  {panel_line(strip.members)}")
    print(f"  window   {_span(s.returns.index)}, calendarSpdsMeanReversion.m as written")
    print(
        f"  rule     short contract c and long c + {SPREAD_MONTH}, rolled {NUM_DAYS_END} days "
        f"before expiry, reversed when the {s.lookback}-day z-score of gamma is above 0"
    )
    print()
    rows = [
        ("Half-life, days", s.half_life, SCRIPT_HALFLIFE),
        ("Half-life, days, book", s.half_life, BOOK_HALFLIFE),
        ("APR", s.apr, SCRIPT_APR),
        ("APR percent, book", 100 * s.apr, BOOK_APR_PERCENT),
        ("Sharpe ratio", s.sharpe, SCRIPT_SHARPE),
        ("Sharpe ratio, book", s.sharpe, BOOK_SHARPE),
        ("Maximum drawdown", s.max_dd, SCRIPT_MAX_DD),
    ]
    print(f"  {'Figure':<32} {'Computed':>12}  {'Chan':>10}  Verdict")
    for label, value, printed in rows:
        print(f"  {label:<32} {value:>12.6f}  {printed:>10}  {_verdict(value, printed)}")
    print(
        f"  {'Longest drawdown, days':<32} {s.max_dd_days:>12}  {SCRIPT_MAX_DD_DAYS:>10}  "
        f"{_verdict(s.max_dd_days, SCRIPT_MAX_DD_DAYS)}"
    )
    critical = s.adf.critical[0]
    holds = s.adf.statistic < critical
    print(
        f"  {'ADF statistic, 99 percent, book':<32} {s.adf.statistic:>12.6f}  {critical:>10.4f}  "
        f"{'reproduced' if holds else 'did not reproduce'}, criterion below the 1 percent "
        "critical value"
    )
    print()
    print("Beside the replication. No book prints these, so none carries a verdict.")
    print(f"  {'Row':<38} {'Days':>5} {'APR':>9} {'Sharpe':>9} {'Max DD':>10} {'Dur':>4}")
    for label, row in (
        (f"R1, from {COMMENT_START.date()}", runs["R1"]),
        (f"R2, holddays {BOOK_HOLDDAYS} from {START.date()}", runs["R2"]),
    ):
        print(
            f"  {label:<38} {len(row.returns):>5} {row.apr:>9.6f} {row.sharpe:>9.6f} "
            f"{row.max_dd:>10.6f} {row.max_dd_days:>4}"
        )
    print(f"  last held day, S                       {s.last_held.date()}")
    print(f"  last held day, R2                      {runs['R2'].last_held.date()}")
    print()
    print(
        f"  Annualised over {TRADING_DAYS} days, simple returns compounded, a Sharpe ratio on "
        "std with n - 1, no risk-free rate and no cost."
    )
    print("  Exploratory. docs/replication-log.md carries the verdicts.")


def run(data_dir: Path | None = None) -> tuple[Strip, dict[str, CalendarSpreadRun]]:
    """Read the CL strip, run the script and the two rows beside it, and print the report."""
    strip = load_strip(ROOT, data_dir)
    contracts = strip.contracts
    gamma = roll_returns(contracts)
    runs = {
        "S": run_spread(contracts, gamma, start=START),
        "R1": run_spread(contracts, gamma, start=COMMENT_START),
        "R2": run_spread(contracts, gamma, start=START, holddays=BOOK_HOLDDAYS),
    }
    report(strip, runs)
    return strip, runs


def main() -> None:
    argparse.ArgumentParser(
        description="Mean reversion on crude oil's 12-month calendar spread, Example 5.4 of "
        "Algorithmic Trading"
    ).parse_args()
    try:
        run()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day reaches the reader
        # as one line, the way chan.roll_returns.main does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
