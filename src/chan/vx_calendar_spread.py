"""VIX futures calendar spreads on the ratio of back to front, *Algorithmic Trading*.

The VX future, a futures contract on the VIX volatility index, does not revert
to a mean, and Chan reports that the spread between two of its contracts does.
At Kindle location 2502 he says that no model of the forward curve he tried
explains why, so the evidence is empirical alone. He makes three claims.

1. An ADF test on "the ratio back/front of VX" finds it "stationary with a 99
   percent probability".
2. "our usual linear mean-reverting strategy using ratio as the signal (and
   with a 15-day look-back ...)" yields "an APR of 17.7 percent and a Sharpe
   ratio of 1.5 from October 27, 2008, to April 23, 2012".
3. It "performed much more poorly prior to October 2008".

**No script ships under its own name, and Example 5.4's is the evidence.**
``calendarSpdsMeanReversion.m``, read under ``public/img/book2/`` in the mirror
[ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) at
``e4bc46f``, opens with a commented-out load of this strip above its live CL
line::

    % load('inputDataDaily_VX_20120507', 'tday', 'contracts', 'cl');

So Chan ran Example 5.4's script on VX, and the book's text names what he
changed. :mod:`chan.calendar_spread_reversion` transcribes that script, and
every row here calls its :func:`~chan.calendar_spread_reversion.run_spread`.

**The specification S, declared before any figure.** The declaration was
written on [issue 349](https://github.com/l3a0/quantitative-trading/issues/349)
on 2026-10-05 at ``f107b1f``, before any APR, Sharpe ratio or ADF statistic on
VX was computed. S is the script with five edits and no others.

1. The VX load line in place of the CL one. VX's file holds no spot column,
   so the spot lines remove nothing, and :func:`chan.roll_returns.load_strip`
   reads it with its spot set to ``None``.
2. ``spreadMonth=1``. The strip lists 2 to 10 contracts a day, so the shipped
   12 pairs contracts that are rarely priced together, and on most held days
   the script would hold the front contract alone.
3. The signal is :func:`nearest_two_ratio`, the second-nearest priced
   contract over the nearest, NaN where the two are not adjacent columns, and
   then ``fillMissingData`` as the script does for γ.
4. ``lookback=15`` in place of ``round(halflife)``. The half-life is still
   printed.
5. ``idx=find(tday==20081027)``, measured to the file's last row, 2012-05-07,
   as the script measures to its own last row.

Everything else is the script as shipped, including ``holddays=3*21``, the
sign-of-z flip and the return divided by 2.

**Four rows beside S, declared with it.**

1. B1 trades :func:`held_pair_ratio`, the far contract over the near one for
   the pair the schedule holds that day, which the script's own comment calls
   the back and the front.
2. B2 sets ``holddays=0``, so each pair is held from the day after the
   previous pair's last day to 10 rows before its own expiry. The first pair
   is never held, and a pair whose near contract still trades on the file's
   last row is skipped once an earlier such pair has taken the rows to the
   end, so VX holds 64 of its 71 pairs.
3. B3 is B1 and B2 together.
4. B4 is S measured to 2012-04-23, the book's end date.

A row beside S that lands while S misses is reported and not promoted to the
specification, because choosing among five rows after seeing them is a search.

**What the run found.** S passes the first claim and misses the second with
the wrong sign. B3 lands, and that was found after the run. Two measurements
were then taken after seeing the rows, so they carry no verdict either: B3 on
the book's own window to 2012-04-23, and each row before October 2008, from
the first row its flipped positions hold anything to 2008-10-24.
``tests/test_vx_calendar_spread.py`` pins every figure.

The post on these lessons found a third thing, which :func:`near_leg_rank`
measures. S holds each pair from 73 rows before its near contract's expiry, so
on most of its held rows the pair it trades is not the front pair its signal
reads. :mod:`chan.vx_calendar_spread_figures` draws the post's figure, since
the run prints its figures and draws nothing.

Every result here is exploratory. Reproducing Chan's figures spends his 2006 to
2012 strip on a rule he chose, S is this repo's reading of the book's text
rather than a script, and B3 was picked out after the run among five rows.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from chan.calendar_spread_reversion import (
    HOLDDAYS,
    CalendarSpreadRun,
    calendar_schedule,
    run_spread,
)
from chan.khandani_lo import TRADING_DAYS
from chan.khandani_lo_book_two import gap, matches
from chan.roll_returns import Strip, load_strip
from chan.series import WindowCrossesScaleBreak, panel_line
from chan.vintage import VintageUnavailable

ROOT = "VX"
#: ``idx=find(tday==20081027)``, the first day of the book's window.
START = pd.Timestamp("2008-10-27")
#: The last day of the book's window, "October 27, 2008, to April 23, 2012".
BOOK_END = pd.Timestamp("2012-04-23")
#: The last trading day before October 27, 2008, where "prior to October 2008" ends.
BEFORE_END = pd.Timestamp("2008-10-24")
#: "a 15-day look-back for the moving average and standard deviations".
LOOKBACK = 15
#: One column apart, which on this strip is one month.
SPREAD_MONTH = 1
#: B2's and B3's holding period. Each pair is then held in turn, apart from the
#: strip's first pair and the pairs whose near contract still trades on the
#: file's last row. Neither changes what is held from 2008-10-27, which is
#: each pair from VX-2008X's to VX-2012K's in order.
EACH_IN_TURN = 0

#: Location 2502. The APR is compared against 100 times the computed one.
BOOK_APR_PERCENT = "17.7"
BOOK_SHARPE = "1.5"

#: The rows declared on issue 349, each a signal, a holding period and an end.
ROWS = ("S", "B1", "B2", "B3", "B4")
#: The rows measured before October 2008. B4 differs from S only after it.
ROWS_BEFORE = ("S", "B1", "B2", "B3")


@dataclass(frozen=True)
class VxCalendarSpread:
    """S and the four rows beside it, then the two measurements taken after them.

    ``rows`` holds S and B1 to B4 from :data:`START`. ``b3_book_window`` is B3
    from :data:`START` to :data:`BOOK_END`. ``before`` holds S and B1 to B3
    from the first row each one's flipped positions hold anything to
    :data:`BEFORE_END`.
    """

    rows: dict[str, CalendarSpreadRun]
    b3_book_window: CalendarSpreadRun
    before: dict[str, CalendarSpreadRun]


def nearest_two_ratio(contracts: pd.DataFrame) -> pd.Series:
    """S's signal: the second-nearest priced contract over the nearest, on every row.

    The nearest two are the first two priced columns in column order. A row
    where they are not adjacent columns, or where fewer than two are priced, is
    NaN, the adjacency test the script's γ loop applies.
    """
    prices = contracts.to_numpy(dtype=float)
    ratio = np.full(len(prices), np.nan)
    for t, row in enumerate(prices):
        priced = np.flatnonzero(np.isfinite(row))
        if len(priced) >= 2 and priced[1] - priced[0] == 1:
            ratio[t] = row[priced[1]] / row[priced[0]]
    return pd.Series(ratio, index=contracts.index, name="nearest_two_ratio")


def held_pair_ratio(contracts: pd.DataFrame, schedule: pd.DataFrame) -> pd.Series:
    """B1's and B3's signal: the far contract over the near one for the pair held that day.

    ``schedule`` is the unflipped frame
    :func:`chan.calendar_spread_reversion.calendar_schedule` returns, −1 on the
    near contract and +1 on the far one, and it holds at most one pair a row.
    The ratio is filled forward across the rows where nothing is held, so it is
    NaN only before the first held row.

    The check below refuses a schedule built on other days or columns. It
    cannot catch the flipped positions
    :attr:`~chan.calendar_spread_reversion.CalendarSpreadRun.positions` carries
    passed in place of the unflipped schedule, because those share the
    schedule's days and columns. On every row the flip reverses, the result
    would then be the near contract over the far one.
    """
    if not (schedule.index.equals(contracts.index) and schedule.columns.equals(contracts.columns)):
        raise ValueError(
            "held_pair_ratio takes the schedule built on these contracts, on their own "
            "days and columns"
        )
    held = schedule.to_numpy(dtype=float)
    prices = contracts.to_numpy(dtype=float)
    rows = np.flatnonzero((held == -1).any(axis=1))
    ratio = np.full(len(prices), np.nan)
    near = (held[rows] == -1).argmax(axis=1)
    far = (held[rows] == 1).argmax(axis=1)
    ratio[rows] = prices[rows, far] / prices[rows, near]
    return pd.Series(ratio, index=contracts.index, name="held_pair_ratio").ffill()


def near_leg_rank(contracts: pd.DataFrame, schedule: pd.DataFrame) -> pd.Series:
    """The held pair's near leg's place among each row's priced contracts, 1 for the front.

    ``schedule`` is the unflipped frame
    :func:`chan.calendar_spread_reversion.calendar_schedule` returns. On a row
    it holds a pair, the result counts the priced contracts in column order up
    to and including the near leg, so 1 means the near leg is the front
    contract. A row holding nothing is NaN. The check refuses a schedule built
    on other days or columns, for the reason :func:`held_pair_ratio` gives.
    """
    if not (schedule.index.equals(contracts.index) and schedule.columns.equals(contracts.columns)):
        raise ValueError(
            "near_leg_rank takes the schedule built on these contracts, on their own "
            "days and columns"
        )
    held = schedule.to_numpy(dtype=float)
    priced = np.isfinite(contracts.to_numpy(dtype=float))
    rows = np.flatnonzero((held == -1).any(axis=1))
    near = (held[rows] == -1).argmax(axis=1)
    rank = np.full(len(held), np.nan)
    rank[rows] = [priced[row, : col + 1].sum() for row, col in zip(rows, near, strict=True)]
    return pd.Series(rank, index=contracts.index, name="near_leg_rank")


def first_held(positions: pd.DataFrame) -> pd.Timestamp:
    """The first row of the flipped positions that holds anything."""
    return positions.index[(positions != 0).any(axis=1).to_numpy()][0]


def vx_calendar_spread(contracts: pd.DataFrame) -> VxCalendarSpread:
    """Run S, B1 to B4, B3 on the book's window and each row before October 2008."""
    nearest = nearest_two_ratio(contracts)
    plans = {
        "S": (nearest, HOLDDAYS, None),
        "B1": (
            held_pair_ratio(contracts, calendar_schedule(contracts, spread_month=SPREAD_MONTH)),
            HOLDDAYS,
            None,
        ),
        "B2": (nearest, EACH_IN_TURN, None),
        "B3": (
            held_pair_ratio(
                contracts,
                calendar_schedule(contracts, spread_month=SPREAD_MONTH, holddays=EACH_IN_TURN),
            ),
            EACH_IN_TURN,
            None,
        ),
        "B4": (nearest, HOLDDAYS, BOOK_END),
    }

    def spread(key: str, start: pd.Timestamp, end: pd.Timestamp | None) -> CalendarSpreadRun:
        signal, holddays, _ = plans[key]
        return run_spread(
            contracts,
            signal,
            start=start,
            end=end,
            spread_month=SPREAD_MONTH,
            holddays=holddays,
            lookback=LOOKBACK,
        )

    rows = {key: spread(key, START, plans[key][2]) for key in ROWS}
    return VxCalendarSpread(
        rows=rows,
        b3_book_window=spread("B3", START, BOOK_END),
        before={
            key: spread(key, first_held(rows[key].positions), BEFORE_END) for key in ROWS_BEFORE
        },
    )


def _verdict(value: float, printed: str) -> str:
    return (
        "reproduced"
        if matches(value, printed)
        else f"did not reproduce, gap {gap(value, printed):+g}"
    )


def _days(found: CalendarSpreadRun) -> str:
    days = found.returns.index
    return f"{days[0].date()} to {days[-1].date()}, {len(days)} days"


def report(strip: Strip, result: VxCalendarSpread) -> None:
    """Print the vintage, S against the book's three claims, then the rows beside it."""
    s = result.rows["S"]
    print("VX calendar spreads on the ratio of back to front, Algorithmic Trading at location 2502")
    print(f"  vintage  {panel_line(strip.members)}, no spot")
    print(f"  window   {_days(s)}")
    print(
        f"  rule     z-score of the ratio over {LOOKBACK} rows, contract c against c + "
        f"{SPREAD_MONTH} held {HOLDDAYS} days, reversed when z > 0"
    )
    print()
    one_percent = s.adf.critical[0]
    print(f"  {'Claim, specification S':<30} {'Computed':>12}  {'Book':>10}  Verdict")
    print(
        f"  {'ADF statistic of the ratio':<30} {s.adf.statistic:>12.6f}  {'99 percent':>10}  "
        f"{'reproduced' if s.adf.statistic < one_percent else 'did not reproduce'}, "
        f"criterion below the 1 percent critical value {one_percent}"
    )
    for label, value, printed in (
        ("APR percent", 100 * s.apr, BOOK_APR_PERCENT),
        ("Sharpe ratio", s.sharpe, BOOK_SHARPE),
    ):
        print(f"  {label:<30} {value:>12.6f}  {printed:>10}  {_verdict(value, printed)}")
    print()
    print(
        "Beside S, declared with it on issue 349. None carries a verdict, and B3 landing was "
        "found after the run."
    )
    print(
        f"  {'Row':<4} {'ADF':>10} {'Half-life':>10} {'APR':>10} {'Sharpe':>10} "
        f"{'Max DD':>10} {'Days':>5} {'Last held':>11}  Window"
    )
    for key in ROWS:
        found = result.rows[key]
        print(
            f"  {key:<4} {found.adf.statistic:>10.6f} {found.half_life:>10.6f} "
            f"{found.apr:>10.6f} {found.sharpe:>10.6f} {found.max_dd:>10.6f} "
            f"{found.max_dd_days:>5} {str(found.last_held.date()):>11}  {_days(found)}"
        )
    print()
    print("Measured after seeing the rows above, so neither carries a verdict.")
    b3 = result.b3_book_window
    print(
        f"  B3 on the book's window, {_days(b3)}: APR {b3.apr:.6f}, Sharpe {b3.sharpe:.6f}, "
        f"last held {b3.last_held.date()}"
    )
    print("  Before October 2008, from each row's first held day to 2008-10-24:")
    for key in ROWS_BEFORE:
        found = result.before[key]
        print(f"    {key:<4} {_days(found)}: APR {found.apr:.6f}, Sharpe {found.sharpe:.6f}")
    print()
    print(
        f"  Annualised over {TRADING_DAYS} days by compounding simple returns, with a Sharpe "
        "ratio on std's n - 1, no risk-free rate and no cost."
    )
    print("  Exploratory. docs/replication-log.md carries the verdicts.")


def run(data_dir: Path | None = None) -> tuple[Strip, VxCalendarSpread]:
    """Read the VX strip, run every row on it, and print the report."""
    strip = load_strip(ROOT, data_dir)
    result = vx_calendar_spread(strip.contracts)
    report(strip, result)
    return strip, result


def main() -> None:
    argparse.ArgumentParser(
        description="VX calendar spreads on the ratio of back to front, Algorithmic Trading "
        "at location 2502"
    ).parse_args()
    try:
        run()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day reaches the reader
        # as one line, the way chan.calendar_spread_reversion.main does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
