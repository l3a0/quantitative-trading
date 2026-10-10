"""Mean reversion on crude oil's 12-month calendar spread, *Algorithmic Trading*'s Example 5.4.

A calendar spread is long one futures contract and short another on the same
underlying with a different expiry. Under the constant-returns model of
Example 5.3, the log value of a spread long the far contract and short the
near one is γ(T1 − T2), where T1 is the near expiry and T2 the later far one.
That is minus γ times the gap between their expiries, so its signal depends on
the roll return γ alone and not on the spot price. At Kindle location 2461
Chan runs the ADF test on CL's 12-month log calendar spread and finds it
"stationary with 99 percent probability, and a half-life of 36 days". He then
trades it with linear mean reversion and reports "an APR of 8.3 percent and a
Sharpe ratio of 1.3 from January 2, 2008, to August 13, 2012". Location 2471
is Example 5.4, which describes the backtest.

**The transcription.** Every step is Chan's ``calendarSpdsMeanReversion.m``,
read under ``public/img/book2/`` in the mirror
[ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) at
``e4bc46f``, git blob ``277d84d``, and landed here for
[issue 348](https://github.com/l3a0/quantitative-trading/issues/348). Line
numbers count from the script's first line, ``clear;``.

1. Lines 11 to 41 remove the spot and fit γ on every row, which is
   :func:`chan.roll_returns.load_strip` and :func:`chan.roll_returns.roll_returns`.
   A scratch run on issue 348 found that γ equals the script's loop bit for
   bit on every row of the CL strip.
2. Line 42 runs ``fillMissingData``, which carries the last finite value
   forward. On one column holding no ±Inf, as γ holds none, that is
   :meth:`pandas.Series.ffill`, as :mod:`chan.pca_factor` uses it.
3. Lines 51 and 52 are ``adf(gamma(isGoodData), 0, 1)`` on the filled
   signal's finite rows, which is :func:`chan.stationarity_tests.jplv7_adf`.
   Lines 55 to 60 regress the change on the lagged level over the same rows,
   which is :func:`ithildincore.timeseries.ou_half_life`. Both read the whole
   filled signal, not the traded window.
4. Lines 66 to 69 set the lookback to ``round(halflife)``, MATLAB's half away
   from zero, which is :func:`chan.matlab_helpers.round_half_away`, and take
   the z-score with :func:`chan.price_spread.zscore`.
5. Lines 72 to 102 are :func:`calendar_schedule`. Line 75 marks a contract
   expired on a row where it is priced and the next row is not, through
   :func:`chan.matlab_helpers.fwdshift`, and line 83 takes the last such row.
6. Lines 106 and 107 are :func:`flip_on_zscore`, and lines 110 and 111 are
   :func:`spread_returns`.
7. Line 113 starts the window on 2008-01-02, and line 119 prints
   ``prod(1 + ret)^(252 / n) − 1`` and ``√252 · mean / std`` with MATLAB's
   n − 1 ``std``. They are :func:`chan.khandani_lo_book_two.compounded_apr`
   and :func:`chan.khandani_lo.plain_sharpe`. Line 121's ``calculateMaxDD``
   on ``cumprod(1 + ret) − 1`` is :func:`chan.matlab_helpers.calculate_max_dd`.

Line 110's ``lag`` is LeSage's, since neither mirror ships a ``lag.m``, and it
pads with zeros where :func:`chan.matlab_helpers.backshift` pads with NaN. The
pad moves nothing. It touches only the first row, which line 111 zeroes either
way and which falls outside the window.

**Two places where Python cannot follow MATLAB to the letter.** Neither moves a
figure on CL.

1. Lines 59 and 60 give a negative half-life when the signal does not revert,
   where :func:`ithildincore.timeseries.ou_half_life` returns infinity. Either
   way the run stops. MATLAB rounds the negative half-life to a negative
   lookback, and ``movingAvg.m``'s ``assert(T>0)`` refuses it. Python's
   ``int(round_half_away(inf))`` raises ``OverflowError``.
2. Line 85's ``max(1, ...)`` is one-based, so the zero-based row is
   ``max(0, ...)``. A first contract expiring within 10 rows of the file's
   first row gives a negative end row, which MATLAB refuses and a Python slice
   wraps. CL's first expiry is 5,044 rows after the file's first row, on
   2006-12-19.

**What the script's spread month counts.** ``spread_month`` counts columns,
as line 81's loop does, although line 80's comment says months, in the way
:mod:`chan.roll_returns` says the script measures maturity in columns. On the
CL and VX strips each column is a month after the last, so the two agree. On
TU, which line 5 names, contract c + 12 is 36 months on, and a run there would
print a wrong spread with nothing to say so.

**The two figures the script's comment prints and the specification does
not.** The script's line 113 starts on 2008-01-02, which gives an APR of
0.082671 and a Sharpe ratio of 1.278216. Its comment prints 0.083406 and
1.288661, which the window from 2008-01-03 lands to every digit. Nothing
committed says whether Chan's own copy of the file labelled its rows a day
earlier or the comment came from a run with another ``idx``, so the
specification keeps the window the script states and the later start runs
beside it with no verdict. ``tests/test_calendar_spread_reversion.py`` pins
every figure.

**What issue 349 imports.** :data:`SPREAD_MONTH`, :data:`HOLDDAYS`,
:func:`calendar_schedule`, :func:`run_spread` and :class:`CalendarSpreadRun`
are the contract that
[issue 349](https://github.com/l3a0/quantitative-trading/issues/349), the VX
calendar spread, builds against.

1. :func:`run_spread` forward-fills the signal before the half-life and the
   ADF read it, as line 42 does. On a signal with NaN after its first finite
   row the filled and unfilled half-lives differ.
2. It refuses a signal whose index does not equal ``contracts.index`` under
   :meth:`pandas.Index.equals`, because a signal built in another module on a
   shifted index of the same length would otherwise misalign silently.
3. :attr:`CalendarSpreadRun.positions` holds the flipped positions, while
   :attr:`CalendarSpreadRun.last_held` reads the unflipped schedule.
4. ``holddays=0`` holds each pair from the day after the previous pair's
   last day to 10 rows before its own expiry, with two exceptions. The first
   pair is never held, because its window is one row and line 98's comparison
   is strict. A pair whose near contract still trades on the file's last row
   is skipped once an earlier such pair has taken the rows up to the end.

**What changed on the way over.** Four things, and none moves a figure.

1. The strip is read as committed vintages through
   :func:`chan.roll_returns.load_strip` rather than loaded from the ``.mat``.
   That module names the vintage and runs the scale-break guard on each
   member's own rows.
2. The plots are not carried. Figure 5.7 belongs to the write-up.
3. The signal, the spread month, the holding period and the lookback are
   arguments, so issue 349 runs the same steps on another strip.
4. Rows the script does not print are computed beside it: the window from
   2008-01-03, a holding period of 61 days, which is what the book's text
   says where the script sets ``3*21``, and the last day a pair is held.

Every result here is exploratory. Reproducing Chan's figures spends the 2008
to 2012 sample on a rule he chose, and the later start was found by a scan
after the script's window missed two of the comment's figures. The half-life,
and so the lookback, is measured on all of γ, including the window it trades.
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

ROOT = "CL"
#: ``spreadMonth``, line 80. It counts columns, as the module docstring says.
SPREAD_MONTH = 12
#: ``holddays=3*21``, line 77.
HOLDDAYS = 3 * 21
#: ``numDaysEnd``, line 79: a pair is let go this many rows before its near contract expires.
NUM_DAYS_END = 10
#: Line 78 adds this to ``holddays`` for the first pair's start.
FIRST_PAIR_EXTRA_DAYS = 10
#: The holding period the book's text gives, "3 months (61 trading days)".
BOOK_HOLDDAYS = 61

#: ``idx=find(tday==20080102)``, line 113.
START = pd.Timestamp("2008-01-02")
#: The start that lands the script's comment to every printed digit.
COMMENT_START = pd.Timestamp("2008-01-03")

#: Lines 63, 123 and 124, the script's comments.
SCRIPT_HALFLIFE = "36.394034"
SCRIPT_APR = "0.083406"
SCRIPT_SHARPE = "1.288661"
SCRIPT_MAX_DD = "-0.053222"
SCRIPT_MAX_DD_DAYS = "206"
#: Locations 2461 and 2471. The APR is compared against 100 times the computed one.
BOOK_APR_PERCENT = "8.3"
BOOK_SHARPE = "1.3"
BOOK_HALFLIFE = "36"


@dataclass(frozen=True)
class CalendarSpreadRun:
    """The script on one strip and one signal, measured over one window.

    ``positions`` holds the flipped positions on every row and ``returns`` the
    window's days. ``last_held`` is the last row of the unflipped schedule
    holding a position on or before the window's end.
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

    Pair c is contract c against contract c + ``spread_month``, by column
    position. The first pair starts ``holddays + 10`` rows before its near
    contract's last expiry and every pair ends :data:`NUM_DAYS_END` rows
    before it. A later pair starts the row after the previous pair's end, and
    is skipped when that leaves fewer than ``holddays`` rows, in which case the
    previous end stands. A pair is held only when its end is after its start,
    rows inclusive.
    """
    cl = contracts.to_numpy(dtype=float)
    is_expire_date = np.isfinite(cl) & ~np.isfinite(fwdshift(1, cl))
    positions = np.zeros_like(cl)
    num_days_start = holddays + FIRST_PAIR_EXTRA_DAYS
    start_idx: int | None = None
    end_idx = 0
    for c in range(cl.shape[1] - spread_month):
        # Line 83: the last mark, since a column may have a gap earlier on.
        expire_idx = int(np.flatnonzero(is_expire_date[:, c])[-1])
        if c == 0:
            start_idx = max(0, expire_idx - num_days_start)
            end_idx = expire_idx - NUM_DAYS_END
        else:
            my_start_idx = end_idx + 1
            my_end_idx = expire_idx - NUM_DAYS_END
            if my_end_idx - my_start_idx >= holddays:
                start_idx, end_idx = my_start_idx, my_end_idx
            else:
                # Line 94 sets startIdx to NaN, and every comparison with NaN is false.
                start_idx = None
        if start_idx is not None and end_idx > start_idx:
            positions[start_idx : end_idx + 1, c] = -1
            positions[start_idx : end_idx + 1, c + spread_month] = 1
    return pd.DataFrame(positions, index=contracts.index, columns=contracts.columns)


def flip_on_zscore(schedule: pd.DataFrame, z: pd.Series) -> pd.DataFrame:
    """Lines 106 and 107: flat where z is NaN, and the spread reversed where z is above 0.

    Where z is exactly 0 the schedule's sign stands, because line 107's
    comparison is strict.
    """
    positions = schedule.to_numpy(dtype=float).copy()
    score = z.to_numpy(dtype=float)
    positions[np.isnan(score), :] = 0
    above = score > 0
    positions[above, :] = -positions[above, :]
    return pd.DataFrame(positions, index=schedule.index, columns=schedule.columns)


def spread_returns(positions: pd.DataFrame, contracts: pd.DataFrame) -> pd.Series:
    """Lines 110 and 111: yesterday's positions times each leg's return, summed and halved.

    ``smartsum`` skips a leg whose return is not a number, and a row with no
    such leg at all is set to 0.
    """
    held = backshift(1, positions.to_numpy(dtype=float))
    cl = contracts.to_numpy(dtype=float)
    before = backshift(1, cl)
    with np.errstate(invalid="ignore", divide="ignore"):
        legs = held * (cl - before) / before
    daily = smartsum(legs, axis=1) / 2
    return pd.Series(np.where(np.isnan(daily), 0.0, daily), index=contracts.index)


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
    """Lines 42 to 122 on ``signal``, measured from ``start`` to ``end``, both included.

    The signal is forward-filled first. The half-life and the ADF read every
    finite row of the filled signal, and the lookback is the half-life rounded
    half away from zero unless one is passed. ``end`` of ``None`` runs to the
    file's last row.
    """
    if not signal.index.equals(contracts.index):
        raise ValueError(
            "run_spread takes a signal on the contracts' own index, so that each row's "
            "z-score sits on the same day as its positions"
        )
    filled = signal.astype(float).ffill()
    good = filled.to_numpy()[np.isfinite(filled.to_numpy())]
    adf = jplv7_adf(good, 0, 1)
    half_life = ou_half_life(good)
    if lookback is None:
        lookback = int(round_half_away(half_life))
    z = pd.Series(zscore(filled.to_numpy(), lookback), index=contracts.index)
    schedule = calendar_schedule(contracts, spread_month=spread_month, holddays=holddays)
    positions = flip_on_zscore(schedule, z)
    returns = spread_returns(positions, contracts).loc[start:end]
    daily = returns.to_numpy()
    max_dd, max_dd_days = calculate_max_dd(np.cumprod(1 + daily) - 1)
    held = schedule.loc[: returns.index[-1]]
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
        last_held=held.index[(held != 0).any(axis=1).to_numpy()][-1],
    )


def _verdict(value: float, printed: str) -> str:
    return (
        "reproduced"
        if matches(value, printed)
        else f"did not reproduce, gap {gap(value, printed):+g}"
    )


def report(strip: Strip, runs: dict[str, CalendarSpreadRun]) -> None:
    """Print the vintage, each printed figure beside S's, the ADF row, and the rows beside."""
    s = runs["S"]
    days = s.returns.index
    print("Mean reversion on CL's 12-month calendar spread, Algorithmic Trading's Example 5.4")
    print(f"  vintage  {panel_line(strip.members)}")
    print(f"  window   {days[0].date()} to {days[-1].date()}, {len(days)} days")
    print(
        f"  rule     z-score of the forward-filled roll return over {s.lookback} rows, "
        f"contract c against c + {SPREAD_MONTH} held {HOLDDAYS} days, reversed when z > 0"
    )
    print()
    rows = [
        ("Half-life, script", s.half_life, SCRIPT_HALFLIFE),
        ("Half-life, book", s.half_life, BOOK_HALFLIFE),
        ("APR, script", s.apr, SCRIPT_APR),
        ("APR percent, book", 100 * s.apr, BOOK_APR_PERCENT),
        ("Sharpe ratio, script", s.sharpe, SCRIPT_SHARPE),
        ("Sharpe ratio, book", s.sharpe, BOOK_SHARPE),
        ("Maximum drawdown, script", s.max_dd, SCRIPT_MAX_DD),
    ]
    print(f"  {'Figure':<30} {'Computed':>12}  {'Chan':>10}  Verdict")
    for label, value, printed in rows:
        print(f"  {label:<30} {value:>12.6f}  {printed:>10}  {_verdict(value, printed)}")
    print(
        f"  {'Longest drawdown, script':<30} {s.max_dd_days:>12}  {SCRIPT_MAX_DD_DAYS:>10}  "
        f"{_verdict(s.max_dd_days, SCRIPT_MAX_DD_DAYS)}"
    )
    one_percent = s.adf.critical[0]
    print(
        f"  {'ADF statistic, book':<30} {s.adf.statistic:>12.6f}  {'99 percent':>10}  "
        f"{'reproduced' if s.adf.statistic < one_percent else 'did not reproduce'}, "
        f"criterion below the 1 percent critical value {one_percent}"
    )
    print()
    print("Beside the replication. No book prints these, so none carries a verdict.")
    for key, label in (
        ("R1", f"R1, from {COMMENT_START.date()}"),
        ("R2", f"R2, holddays={BOOK_HOLDDAYS} from {START.date()}"),
    ):
        run_ = runs[key]
        print(
            f"  {label:<33} {len(run_.returns)} days, APR {run_.apr:.6f}, Sharpe "
            f"{run_.sharpe:.6f}, max drawdown {run_.max_dd:.6f} over {run_.max_dd_days} days, "
            f"last held {run_.last_held.date()}"
        )
    print(f"  {'S, last day a pair is held':<33} {s.last_held.date()}")
    print()
    print(
        f"  Annualised over {TRADING_DAYS} days by compounding simple returns, with a Sharpe "
        "ratio on std's n - 1, no risk-free rate and no cost."
    )
    print("  Exploratory. docs/replication-log.md carries the verdicts.")


def run(data_dir: Path | None = None) -> tuple[Strip, dict[str, CalendarSpreadRun]]:
    """Read the CL strip, run S, R1 and R2 on its roll return, and print the report."""
    strip = load_strip(ROOT, data_dir)
    gamma = roll_returns(strip.contracts)
    runs = {
        "S": run_spread(strip.contracts, gamma, start=START),
        "R1": run_spread(strip.contracts, gamma, start=COMMENT_START),
        "R2": run_spread(strip.contracts, gamma, start=START, holddays=BOOK_HOLDDAYS),
    }
    report(strip, runs)
    return strip, runs


def main() -> None:
    argparse.ArgumentParser(
        description="Mean reversion on CL's 12-month calendar spread, Example 5.4 of "
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
