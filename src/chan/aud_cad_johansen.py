"""AUD.USD against CAD.USD with a rolling Johansen hedge, *Algorithmic Trading*'s Example 5.1.

Chan uses this example to show two things about currencies. A pair is quoted so
that each unit of it is worth the same amount in one currency, which is why
USD.CAD is inverted before the test. And a currency portfolio's return is its
profit over the capital it held the day before, in that one currency. At Kindle
locations 2186 to 2237 he reports "the APR is 11 percent and the Sharpe ratio
is 1.6, for the period December 18, 2009, to April 26, 2012", after leaving out
the first 250 days of training data.

**The transcription.** ``AUDCAD_unequal.m`` was read in the mirror
[ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) at
``e4bc46f``, under ``public/img/book2/``, git blob ``5b8fbc2``, and landed here
for [issue 345](https://github.com/l3a0/quantitative-trading/issues/345). Line
numbers are the script's.

1. Lines 3 to 18 load two minute ``.mat`` files and keep the 16:59 bar of each
   day after 2009-01-01. The run reads the port's two daily files instead,
   which hold one close a day already, so it filters nothing. Line 18 takes
   AUD.USD's dates for both series, so the run refuses two series whose dates
   differ rather than aligning them, because an inner join would silently
   change which rows train.
2. Lines 22 and 25 build ``y`` from AUD.USD and ``1 ./ usdcad``, in that order.
3. Lines 31 to 33 take, for each row ``t`` from 251 on, counted from one,
   ``johansen(y(t − 250 : t − 1, :), 0, 1)`` on the 250 rows before ``t``, and
   keep the eigenvector of the largest eigenvalue as that day's hedge. That is
   :func:`chan.johansen.johansen`. The hedge is taken whether or not the test
   finds a relation in that window.
4. Lines 36 to 42 value the portfolio over rows ``t − 19`` to ``t`` at day
   ``t``'s hedge, so the 20-row window includes day ``t`` while the hedge's
   window ends the day before. The units are minus that value's z-score, with
   MATLAB's n − 1 ``std``.
5. Lines 49 to 54 take each leg's position in dollars as the units times its
   hedge weight times its price. The day's return is yesterday's positions
   times today's simple returns, summed, over yesterday's gross, and a day that
   is not a number is 0. The sums are MATLAB's ``sum``, so one missing leg
   makes a missing day. Row 251's lagged positions are row 250's, which do not
   exist yet, so row 251's return is 0. That is the first value of Chan's saved
   returns.
6. Lines 59 and 65 take, over the 612 rows from 251 on, the compounded APR, the
   Sharpe ratio ``√252 · mean / std`` with no risk-free rate, and the Kelly
   leverage ``mean / std²``. Those are
   :func:`chan.khandani_lo_book_two.compounded_apr`,
   :func:`chan.khandani_lo.plain_sharpe` and the ``period_leverage`` of
   :func:`chan.kelly_leverage.annualised_moments`.
7. Line 69 saves the 612 returns. That output is committed as
   ``AUDCAD_unequal_ret.csv``, so the run writes no file.

**What changed on the way over.** Three things, and none moves a figure.

1. The two series are read as committed vintages through
   :func:`chan.series.load_port_close` rather than from the ``.mat`` files.
2. The ``plot`` on line 57 is not carried. The run draws nothing.
3. The run calls the scale-break guard, which the script has no counterpart
   for, and compares its returns with Chan's saved ones.

**Whether the inputs are the ones the MATLAB read.** The committed daily files
are the Python port's copies, and the ``.mat`` files the script loaded are in
neither mirror.
[Issue 301](https://github.com/l3a0/quantitative-trading/issues/301) assigned
the question here, because Chan's saved returns are the one output of the
MATLAB that can be compared. The criterion, fixed on issue 345 before any
return was computed, is that the 612 returns agree with his to within 1e-9 on
every row. A match says the inputs agree up to a constant scale on each leg,
because a simple return ignores the scale and the eigenvector rescales to
cancel it.

**The hedge's sign and scale move no return.** Multiplying day ``t``'s vector
by any ``c ≠ 0`` multiplies that day's portfolio value by ``c``, so its z-score
by the sign of ``c``, so the units by the sign of ``c``, so the positions by
``|c|``. The return divides profit by the gross position, so ``|c|`` cancels.
statsmodels' eigenvector sign can be the opposite of MATLAB's, which
:mod:`chan.etf_cointegration` measured on Chan's ETFs, and here it reaches no
return.

**The scale-break guard is called and refuses nothing.** The run calls
:func:`chan.series.refuse_window_crossing_a_break` on both closes over the
files' whole span, 2009-01-02 to 2012-04-26, as :mod:`chan.pead` does.
Neither file carries a flagged day, so a refusal today would mean a corrupted
copy.

Every result here is exploratory. Reproducing Chan's figures spends the 2009 to
2012 sample on a rule he chose, and location 2237 says the 250-day training
length was chosen in hindsight. The run says whether his numbers reproduce on
his files and nothing about whether the pair trades today.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from chan.johansen import johansen
from chan.kelly_leverage import annualised_moments
from chan.khandani_lo import TRADING_DAYS, plain_sharpe
from chan.khandani_lo_book_two import compounded_apr, gap, matches
from chan.matlab_helpers import lag1
from chan.series import (
    WindowCrossesScaleBreak,
    load_port_close,
    load_returns,
    refuse_window_crossing_a_break,
    vintage_line,
)
from chan.vintage import VintageEntry, VintageUnavailable

#: The port's two daily files share this saved date. USD.CAD's minute file does not.
DAILY_SAVED = "2018-12-12"
AUDUSD, USDCAD = "AUDUSD", "USDCAD"
#: ``y = [aud cad]``, the order every hedge vector follows.
LEGS = ("AUDUSD", "CADUSD")
#: The manifest's symbol for ``AUDCAD_unequal_ret.csv``, the script's saved returns.
SAVED_RETURNS = "AUDCAD-UNEQUAL"

#: ``trainlen`` and ``lookback``, script lines 26 and 27.
SCRIPT_TRAINING_DAYS = 250
SCRIPT_LOOKBACK = 20
#: ``johansen(·, 0, 1)``, a constant and one lagged difference.
JOHANSEN_P = 0
JOHANSEN_K = 1

#: Script lines 60 and 66.
SCRIPT_APR = "0.112410"
SCRIPT_SHARPE = "1.610890"
SCRIPT_KELLY = "23.845328"
#: Location 2237.
BOOK_APR_PERCENT = "11"
BOOK_SHARPE = "1.6"
BOOK_FIRST_DAY = "2009-12-18"
BOOK_LAST_DAY = "2012-04-26"

#: Row 5's criterion, declared on issue 345 before any return was computed.
#:
#: The returns are of order 1e-3, so a different input close moves the rows it
#: reaches by far more than this, while the same arithmetic in MATLAB and numpy
#: differs by rounding.
AGREEMENT = 1e-9

#: The level the two relation counts beside the replication read.
RELATION_LEVEL = 95


def cross_rates(audusd: pd.Series, usdcad: pd.Series) -> pd.DataFrame:
    """Lines 18 to 25: AUD.USD and the inverse of USD.CAD, on dates the two must share.

    The script takes AUD.USD's dates for both, which is right only when the two
    carry the same ones, so two different calendars are refused rather than
    joined.
    """
    if not audusd.index.equals(usdcad.index):
        only_aud = audusd.index.difference(usdcad.index)
        only_cad = usdcad.index.difference(audusd.index)
        raise ValueError(
            f"AUD.USD and USD.CAD must carry the same dates, because the script takes "
            f"AUD.USD's for both. {len(only_aud)} are AUD.USD's alone and {len(only_cad)} "
            f"USD.CAD's alone"
        )
    return pd.DataFrame(
        {LEGS[0]: audusd.to_numpy(dtype=float), LEGS[1]: 1.0 / usdcad.to_numpy(dtype=float)},
        index=audusd.index,
    )


def units_on(
    prices: NDArray[np.float64], hedge: NDArray[np.float64], t: int, lookback: int
) -> float:
    """Lines 36 to 42: minus the z-score of the portfolio over rows ``t − lookback + 1`` to ``t``.

    The window includes day ``t`` and every row in it is valued at day ``t``'s
    hedge.
    """
    value = prices[t - lookback + 1 : t + 1] @ hedge
    return float(-(value[-1] - value.mean()) / value.std(ddof=1))


def daily_returns(
    positions: NDArray[np.float64], prices: NDArray[np.float64]
) -> NDArray[np.float64]:
    """Lines 52 to 54: yesterday's positions times today's simple returns, over yesterday's gross.

    Both sums are MATLAB's ``sum``, which a NaN turns to NaN, and a NaN day is
    then 0. ``np.nansum`` would skip a missing leg and earn on the other.
    """
    held = lag1(positions)
    before = lag1(prices)
    with np.errstate(invalid="ignore", divide="ignore"):
        pnl = np.sum(held * (prices - before) / before, axis=1)
        daily = pnl / np.sum(np.abs(held), axis=1)
    return np.where(np.isnan(daily), 0.0, daily)


@dataclass(frozen=True)
class Figures:
    """Lines 59 and 65 over the test rows: the APR, the Sharpe ratio and the Kelly leverage."""

    apr: float
    sharpe: float
    kelly: float


def figures(test: NDArray[np.float64]) -> Figures:
    """The three printed figures, each through the helper that already computes it here."""
    return Figures(
        apr=compounded_apr(test),
        sharpe=plain_sharpe(test),
        kelly=annualised_moments(pd.Series(test), risk_free=0.0).period_leverage,
    )


@dataclass(frozen=True)
class AudCad:
    """The script on the two series, and the two relation counts beside it.

    ``hedge``, ``units`` and ``positions`` hold a row for every day and are NaN
    before row 251. ``daily`` holds every day's return and ``test`` the 612
    from row 251 on. ``trace_relations`` and ``eigen_relations`` count, per
    test row, the relations each statistic finds at
    :data:`RELATION_LEVEL` percent in that row's training window.
    """

    days: pd.DatetimeIndex
    prices: NDArray[np.float64]
    hedge: NDArray[np.float64]
    units: NDArray[np.float64]
    positions: NDArray[np.float64]
    daily: NDArray[np.float64]
    trace_relations: NDArray[np.int_]
    eigen_relations: NDArray[np.int_]
    training: int

    @property
    def test(self) -> NDArray[np.float64]:
        return self.daily[self.training :]

    @property
    def test_days(self) -> pd.DatetimeIndex:
        return self.days[self.training :]

    @property
    def figures(self) -> Figures:
        return figures(self.test)

    @property
    def last_hedge(self) -> NDArray[np.float64]:
        """The last day's hedge with AUD.USD's weight scaled to 1.

        The weights count units of each currency, so the split in dollars is
        each weight times its quote, which is the last row of ``positions``.
        """
        return self.hedge[-1] / self.hedge[-1, 0]


def aud_cad(
    frame: pd.DataFrame, training: int = SCRIPT_TRAINING_DAYS, lookback: int = SCRIPT_LOOKBACK
) -> AudCad:
    """Run lines 25 to 54 on a frame from :func:`cross_rates`."""
    prices = frame[list(LEGS)].to_numpy(dtype=float)
    rows = len(prices)
    hedge = np.full(prices.shape, np.nan)
    units = np.full(rows, np.nan)
    trace, eigen = [], []
    for t in range(training, rows):
        tested = johansen(prices[t - training : t], JOHANSEN_P, JOHANSEN_K)
        hedge[t] = tested.eigenvectors[:, 0]
        units[t] = units_on(prices, hedge[t], t, lookback)
        trace.append(tested.relations("trace", RELATION_LEVEL))
        eigen.append(tested.relations("eigen", RELATION_LEVEL))
    positions = units[:, None] * hedge * prices
    return AudCad(
        days=frame.index,
        prices=prices,
        hedge=hedge,
        units=units,
        positions=positions,
        daily=daily_returns(positions, prices),
        trace_relations=np.array(trace, dtype=int),
        eigen_relations=np.array(eigen, dtype=int),
        training=training,
    )


@dataclass(frozen=True)
class Agreement:
    """Row 5: the computed test returns against Chan's saved ones, row by row."""

    largest: float
    rows_over: int
    first_over: pd.Timestamp | None

    @property
    def holds(self) -> bool:
        return self.rows_over == 0


def agreement(
    computed: NDArray[np.float64], saved: NDArray[np.float64], days: pd.DatetimeIndex
) -> Agreement:
    """How far apart the two series are, and where they first part by more than 1e-9.

    A row that is not a number on either side counts as over the criterion.

    ``days`` is the calendar the computed returns fall on. Chan's file carries
    none, so it takes this one.
    """
    if not len(computed) == len(saved) == len(days):
        raise ValueError(
            f"the computed returns hold {len(computed)} rows and Chan's {len(saved)}, "
            f"on {len(days)} days, so they cannot be compared row by row"
        )
    difference = np.abs(computed - saved)
    # A row that is not a number on either side has not agreed, and a plain
    # ``>`` would read it as agreeing.
    over = np.flatnonzero(~(difference <= AGREEMENT))
    return Agreement(
        largest=float(difference.max()),
        rows_over=len(over),
        first_over=days[over[0]] if len(over) else None,
    )


@dataclass(frozen=True)
class Sources:
    """The two daily series and Chan's saved returns, each with the entry it was read from."""

    audusd: tuple[VintageEntry, pd.Series]
    usdcad: tuple[VintageEntry, pd.Series]
    saved: tuple[VintageEntry, NDArray[np.float64]]

    @property
    def entries(self) -> list[VintageEntry]:
        return [self.audusd[0], self.usdcad[0], self.saved[0]]


def read_sources(data_dir: Path | None = None) -> Sources:
    """The two daily files, refused if either spans a scale break, and Chan's saved returns."""
    audusd = load_port_close(AUDUSD, dated=DAILY_SAVED, data_dir=data_dir)
    usdcad = load_port_close(USDCAD, dated=DAILY_SAVED, data_dir=data_dir)
    days = audusd[1].index
    refuse_window_crossing_a_break([audusd, usdcad], start=days[0], end=days[-1])
    return Sources(
        audusd=audusd, usdcad=usdcad, saved=load_returns(SAVED_RETURNS, data_dir=data_dir)
    )


def _verdict(value: float, printed: str) -> str:
    return (
        "reproduced"
        if matches(value, printed)
        else f"did not reproduce, gap {gap(value, printed):+g}"
    )


def report(sources: Sources, result: AudCad, row5: Agreement) -> None:
    """Print the vintages, each printed figure beside the computed one, and the rows beside them."""
    found = result.figures
    print(
        "AUD.USD against CAD.USD with a rolling Johansen hedge, Algorithmic Trading's Example 5.1"
    )
    for entry in sources.entries:
        print(f"  vintage  {vintage_line(entry)}")
    days = result.test_days
    print(
        f"  window   {days[0].date()} to {days[-1].date()}, {len(days)} test returns after "
        f"{result.training} training days"
    )
    print(
        f"  rule     johansen(., {JOHANSEN_P}, {JOHANSEN_K}) on the {result.training} rows before "
        f"each day, units of minus a {SCRIPT_LOOKBACK}-row z-score"
    )
    print()
    rows = [
        ("APR", found.apr, SCRIPT_APR),
        ("Sharpe ratio", found.sharpe, SCRIPT_SHARPE),
        ("Kelly leverage, mean / std^2", found.kelly, SCRIPT_KELLY),
    ]
    print(f"  {'Figure':<30} {'Computed':>12}  {'Chan':>12}  Verdict")
    for label, value, printed in rows:
        print(f"  {label:<30} {value:>12.6f}  {printed:>12}  {_verdict(value, printed)}")
    print(
        f"  {'Book, APR percent':<30} {100 * found.apr:>12.6f}  {BOOK_APR_PERCENT:>12}  "
        f"{_verdict(100 * found.apr, BOOK_APR_PERCENT)}"
    )
    print(
        f"  {'Book, Sharpe ratio':<30} {found.sharpe:>12.6f}  {BOOK_SHARPE:>12}  "
        f"{_verdict(found.sharpe, BOOK_SHARPE)}"
    )
    print()
    print(
        f"  The {len(days)} returns against Chan's saved ones, criterion {AGREEMENT:g} on every row"
    )
    print(f"    largest difference  {row5.largest:.3g}")
    print(f"    rows over           {row5.rows_over}")
    if row5.first_over is not None:
        print(f"    first row over      {row5.first_over.date()}")
    print(f"    {'they agree' if row5.holds else 'they do not agree'}")
    print()
    print("Beside the replication. No book prints these, so none carries a verdict.")
    print(f"  of the {len(result.trace_relations)} training windows, at {RELATION_LEVEL}%")
    for name, found in (("trace", result.trace_relations), ("eigen", result.eigen_relations)):
        one, two = (np.count_nonzero(found == n) for n in (1, 2))
        print(f"    {name} finds a relation in {one + two}, one in {one} and two in {two}")
    aud, cad = result.last_hedge
    dollars = result.positions[-1] / result.positions[-1, 0]
    print(f"  last day's hedge, AUD.USD to 1    {LEGS[0]} {aud:.4f}, {LEGS[1]} {cad:.4f}")
    print(
        f"  last day's positions in dollars   {LEGS[0]} {dollars[0]:.4f}, "
        f"{LEGS[1]} {dollars[1]:.4f}"
    )
    print()
    print(
        f"  Annualised over {TRADING_DAYS} days with no risk-free rate, no cost and no "
        "rollover interest."
    )
    print("  Exploratory. docs/replication-log.md carries the verdicts.")


def run(data_dir: Path | None = None) -> tuple[AudCad, Agreement]:
    """Read the vintages, guard them, run the script, compare with Chan's, and print the report."""
    sources = read_sources(data_dir)
    result = aud_cad(cross_rates(sources.audusd[1], sources.usdcad[1]))
    row5 = agreement(result.test, sources.saved[1], result.test_days)
    report(sources, result, row5)
    return result, row5


def main() -> None:
    argparse.ArgumentParser(
        description="AUD.USD against CAD.USD with a rolling Johansen hedge, Algorithmic "
        "Trading's Example 5.1"
    ).parse_args()
    try:
        run()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day reaches the reader
        # as one line, the way chan.pead.main does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
