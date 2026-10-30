"""The VIX filter on buy on gap and the FSTX gap rule, *Algorithmic Trading*'s location 3509.

A risk indicator is worth reading only if it says something about the next
day's return of the strategy it guards, and Chapter 8 of *Algorithmic
Trading* argues that no one indicator does that for every strategy. Location
3509, in ``research/book-notes/algorithmic-trading.md``, makes the case on two
rules the book already ran. It keeps only the days after the VIX closed above
35, "a common threshold for highly risky periods", and reports what each rule
earned on them.

1. **Buy on gap**, Example 4.1, which :mod:`chan.buy_on_gap` runs. The
   sentence gives its unfiltered figures as "an annualized average return of
   around 8.7 percent and a Sharpe ratio of 1.5", and its filtered ones as
   "17.2 percent with a Sharpe ratio of 1.4".
2. **The opening gap rule on FSTX**, the STOXX Europe 50 index future on
   Eurex, Example 7.1, which :mod:`chan.opening_gap` runs. Its unfiltered
   figures are "around 13 percent and a Sharpe ratio of 1.4", and its
   filtered ones "2.6 percent and the Sharpe ratio to 0.16".

**No script ships for location 3509, and the FSTX alignment was found by
search.** None of the three public copies of Chan's code this repository has
read, ivanliu1989/algorithmic_trading, ericnberwick/EpchanPreview and
burakbayramli/books, holds a file that applies the filter, so the
specification below is inferred from the four printed figures rather than
read from code. The plan on
[issue 359](https://github.com/l3a0/quantitative-trading/issues/359) tried six
ways of aligning VIX with FSTX's calendar and two ways of averaging before
choosing one. All six alignments and both averages are pinned in
``tests/test_vix_filter.py``, so a reader can see what each gives, and only
the join below lands 2.6 percent. Buy on gap's figures do not depend on which
previous close is read, because every one of its 1,500 days is a VIX day and
VIX has no day between its first and last that the panel lacks. So an
alignment that reads the previous day can change only the close read on the
first day, 2006-05-11, which no reading keeps. Every result here is
exploratory.

**The specification.** Three steps, each mapped to the function that runs it.

1. **The calendar**, :func:`common_days`. Each rule's calendar is joined to
   VIX's on the days both trade, which is MATLAB's ``intersect`` on two date
   vectors. Buy on gap keeps all 1,500 of its days. FSTX keeps 1,945 of its
   2,000. It loses the 7 days after VIX's last close on 2012-05-08, and 48
   days on which Eurex traded and the CBOE did not.
2. **The filter**, :func:`qualifies`. A day qualifies when the VIX close on
   the previous joined day is strictly above :data:`THRESHOLD`, which is
   ``backshift(1, vix) > 35`` on the joined calendar. A NaN qualifies nothing,
   so the first joined day never does.
3. **The figures**, :class:`Filtered`. Each rule runs on its own full
   calendar, unchanged, and its daily returns are then taken on the joined
   days. The "annualized average return" is 252 times the mean over the
   qualifying days alone, and the Sharpe ratio is
   :func:`chan.khandani_lo.plain_sharpe` on those same days, with MATLAB's
   n − 1 deviation, no risk-free rate and no cost. For FSTX, the qualifying
   days' returns are the same whether the rule runs before or after the join,
   which the tests hold.

**The phrase "annualized average return" names two formulas in two
consecutive sentences.** Entry 18 of ``docs/replication-log.md`` found that
the unfiltered 8.7 percent is buy on gap's compounded APR, which the
arithmetic figure misses. The filtered 17.2 percent is the arithmetic
figure, and the compounded APR over the same 190 days prints as 17.9
percent.

**Zeroing the other days and averaging over the whole sample** misses. It
gives buy on gap a figure of 2.2 percent, nowhere near 17.2, so the average
is taken over the qualifying days alone.

**The five alignments set aside**, each pinned with the reason. The first
three read the day before, as the sentence asks, and the last two read the
same day.

1. **The latest VIX close strictly before each FSTX day**, with no calendar
   join, keeps 188 days. The three it adds are US holidays on which Eurex
   traded, and each reads the close before it. Its Sharpe ratio prints as
   0.16, and its return prints as 2.5 percent rather than 2.6.
2. **VIX forward-filled onto FSTX's calendar and moved one row** keeps the
   same 188 days as the latest close, so it gives the same figures. The two
   do not always read the same close. After a day the CBOE traded and Eurex
   did not, the latest close is that day's, while the forward fill reads
   FSTX's previous day. No such day moves a close across 35.
3. **A one-row shift on FSTX's own calendar**, with NaN where VIX has no
   close, keeps 185 days and lands neither figure. It keeps those three
   holidays and drops the day after each, which reads the holiday's NaN.
4. **The same day's VIX close on FSTX's own calendar**, with NaN on days
   the US exchanges were shut, keeps 185 days.
5. **The same day's VIX close forward-filled onto FSTX's calendar** keeps
   188, the three holidays included.

The last two look ahead. The gap rule holds FSTX from the open to the close,
and VIX closes at 16:15 New York time, hours after FSTX opens on the same
date. So the sentence's "preceding day's VIX" rules them out before any figure
is read, and both give a negative return and Sharpe ratio besides.

**The seven FSTX days after VIX ends.** The join drops them, because VIX has
no close on any of them. Under the latest-close reading they would read
2012-05-08's close of 19.05, which is below 35, so none of them could qualify
either way.

**The vintages.** Three committed files, each read through
:func:`chan.series.load_panel`, which hashes every member against its manifest
entry before parsing it.

1. **VIX** from ``VIX.csv``, ``vix/vix.csv``, vendor chan-csv, basis ``raw``,
   saved 2012-05-09, 5,635 rows from 1990-01-02 to 2012-05-08.
2. **The stocks** from ``inputdataohlcdaily_stocks_20120424/``, the 497
   stocks of Chan's ``inputDataOHLCDaily_stocks_20120424.mat``, chan-mat,
   adjusted, saved 2012-04-25, read by
   :func:`chan.buy_on_gap.read_sources` over 1,500 days from 2006-05-11 to
   2012-04-24. Every figure on it is about survivors.
3. **FSTX** from ``inputdataohlcdaily_20120517/fstx.csv``, chan-mat,
   adjusted, saved 2012-05-18, read by :func:`chan.opening_gap.read_sources`
   over 2,000 days from 2004-07-16 to 2012-05-17.

**The scale-break guard.** :func:`chan.series.scale_breaks` flags a day whose
close is more than 1.6 times the close before it, or less than that close
divided by 1.6. VIX flags one day, 2007-02-27, a real move from 11.15 to 18.31
that ``tests/test_scale_breaks.py`` pins, and it falls inside both windows. So
a guard over either whole window would refuse. :func:`read_sources` guards VIX
over two spans in each window instead, from the window's first joined day to
:data:`BEFORE_FLAG` and from :data:`FLAGGED_DAY` to its last joined day.
Together they leave out only the ratio from 2007-02-26 to 2007-02-27, so every
day-over-day move the run reads from the window's first joined day on is
guarded except the one real move.
:mod:`chan.vx_es_roll_return` met the same day and guarded VIX only from an
anchor after it. That is a different case, because no figure there reads VIX
before the anchor, while here every close before the flag feeds the filter.

A rescale smaller than 1.6 times is invisible to the guard on any span. VIX's
largest close from FSTX's first joined day to 2007-02-26 is 23.81, on
2006-06-13, and a rescale of 1.47 times would carry it past 35, inside that
blind band. So the guard rules out a large rescale on every span the run
reads, and nothing here rules out a small one. VIX's first close above 35
inside either window is on 2008-09-17. FSTX is guarded over its whole span
inside :func:`chan.opening_gap.read_sources`, which flags nothing. The stocks
are not guarded, for the reason :mod:`chan.buy_on_gap` gives: the guard flags
30 closes in 17 of them, all inside the window, and
[issue 295](https://github.com/l3a0/quantitative-trading/issues/295) decided
that reproducing Chan's script on the prices as they stand comes first.

**Whether the kept days differ from the rest.** No source prints a test, so
:attr:`Filtered.welch` runs one beside the replication. Welch's t on mean
daily return, the kept days against the other joined days, is 0.705402 for
buy on gap, with p of 0.481405, and −0.684181 for FSTX under the script's
sign, with p of 0.494679. The momentum sign gives the same t negated. The test
treats each day as independent, and neither difference is distinguishable from
noise, so neither rule's mean return says which way the filter points.

Every result here is exploratory. Reproducing Chan's figures spends the 2006
to 2012 and 2004 to 2012 samples on two rules and a threshold he chose, and
the FSTX alignment was chosen after its figures were seen. So the run says
whether his numbers reproduce on his files and nothing about whether VIX
above 35 guards either rule today.

:func:`runs` and :attr:`Filtered.summed` were added by the write-up,
``blog/vix-filter-lessons.md``, after the run. They describe how the kept days
bunch and what each rule earned on them, and decide nothing.
:mod:`chan.vix_filter_figures` draws that post's figure.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray
from scipy import stats

from chan import buy_on_gap, opening_gap
from chan.khandani_lo import TRADING_DAYS, plain_sharpe
from chan.khandani_lo_book_two import compounded_apr, gap, matches
from chan.matlab_helpers import backshift
from chan.series import (
    WindowCrossesScaleBreak,
    load_panel,
    panel_line,
    refuse_window_crossing_a_break,
    vintage_line,
)
from chan.vintage import VintageEntry, VintageUnavailable

#: The index file location 3509 filters on.
VIX_FILE = "VIX.csv"
VIX = "VIX"

#: "if the preceding day's VIX is over 35".
THRESHOLD = 35.0
#: VIX's one flagged day, the real move from 11.15 to 18.31, where the second guarded span starts.
FLAGGED_DAY = pd.Timestamp("2007-02-27")
#: VIX's close before :data:`FLAGGED_DAY`, where the first guarded span ends.
BEFORE_FLAG = pd.Timestamp("2007-02-26")

#: Location 3509's filtered figures for buy on gap, "17.2 percent with a Sharpe ratio of 1.4".
BOOK_BUY_ON_GAP_PERCENT = "17.2"
BOOK_BUY_ON_GAP_SHARPE = "1.4"
#: Location 3509's filtered figures for FSTX, "2.6 percent and the Sharpe ratio to 0.16".
BOOK_FSTX_PERCENT = "2.6"
BOOK_FSTX_SHARPE = "0.16"


def common_days(days: pd.DatetimeIndex, vix: pd.Series) -> pd.DatetimeIndex:
    """The days both trade, sorted ascending, which is what MATLAB's ``intersect`` returns."""
    return days.intersection(vix.index).sort_values()


def qualifies(vix_closes: ArrayLike) -> NDArray[np.bool_]:
    """``backshift(1, vix) > 35``: whether the previous row's close is strictly above 35.

    A NaN on the previous row qualifies nothing, as a comparison with NaN is
    false in MATLAB, so the first row never qualifies.
    """
    closes = np.asarray(vix_closes, dtype=float)
    with np.errstate(invalid="ignore"):
        return backshift(1, closes) > THRESHOLD


def runs(flags: ArrayLike) -> list[tuple[int, int]]:
    """The first and last row of each run of consecutive true rows, in order.

    ``blog/vix-filter-lessons.md`` added it after the run, to count how the
    kept days bunch, so it decides nothing.
    """
    marked = np.asarray(flags, dtype=bool).astype(int)
    steps = np.diff(np.concatenate(([0], marked, [0])))
    starts = np.flatnonzero(steps == 1)
    ends = np.flatnonzero(steps == -1) - 1
    return [(int(a), int(b)) for a, b in zip(starts, ends, strict=True)]


def latest_close_before(days: pd.DatetimeIndex, vix: pd.Series) -> NDArray[np.float64]:
    """The latest VIX close strictly before each day, NaN before VIX's first.

    This is the first alignment set aside. It joins no calendars, so a day
    after a US holiday reads the close before the holiday, and a day after
    VIX's last close reads that close.
    """
    rows = vix.index.searchsorted(days, side="left") - 1
    closes = vix.to_numpy(dtype=float)
    return np.where(rows >= 0, closes[np.clip(rows, 0, None)], np.nan)


@dataclass(frozen=True)
class Reading:
    """What one reading of the sentence gives: the days it keeps and its two figures."""

    kept: int
    average_annual_return: float
    sharpe: float


def reading(daily: ArrayLike, keep: ArrayLike) -> Reading:
    """252 times the mean and the Sharpe ratio over the days ``keep`` marks."""
    kept = np.asarray(daily, dtype=float)[np.asarray(keep, dtype=bool)]
    return Reading(
        kept=len(kept),
        average_annual_return=float(TRADING_DAYS * kept.mean()),
        sharpe=plain_sharpe(kept),
    )


def as_of_reading(days: pd.DatetimeIndex, daily: ArrayLike, vix: pd.Series) -> Reading:
    """The first alignment set aside: each day kept when the latest close before it is above 35."""
    with np.errstate(invalid="ignore"):
        keep = latest_close_before(days, vix) > THRESHOLD
    return reading(daily, keep)


def own_calendar_reading(days: pd.DatetimeIndex, daily: ArrayLike, vix: pd.Series) -> Reading:
    """The third alignment set aside: one row back on the rule's own calendar.

    VIX is placed on the rule's days with NaN where it has no close, and
    :func:`qualifies` shifts it one row, so a day after a US holiday reads the
    holiday's NaN and qualifies nothing.
    """
    return reading(daily, qualifies(vix.reindex(days).to_numpy(dtype=float)))


def forward_filled_reading(days: pd.DatetimeIndex, daily: ArrayLike, vix: pd.Series) -> Reading:
    """The second alignment set aside: VIX forward-filled onto the rule's calendar, one row back.

    A day after a US holiday reads the close before the holiday, as
    :func:`as_of_reading` does. A day after one the CBOE traded and the rule
    did not reads the rule's previous day, where :func:`as_of_reading` reads
    the later close.
    """
    return reading(daily, qualifies(vix.reindex(days, method="ffill").to_numpy(dtype=float)))


def same_day_reading(
    days: pd.DatetimeIndex, daily: ArrayLike, vix: pd.Series, *, forward_fill: bool
) -> Reading:
    """The fourth and fifth alignments set aside: VIX above 35 on the same date.

    Both look ahead. VIX closes at 16:15 New York time, after FSTX's open on the same date, so
    a position taken at the open could not have read it. ``forward_fill``
    gives a day the US exchanges were shut the close before it rather than NaN.
    """
    closes = vix.reindex(days, method="ffill" if forward_fill else None)
    with np.errstate(invalid="ignore"):
        return reading(daily, closes.to_numpy(dtype=float) > THRESHOLD)


@dataclass(frozen=True)
class Filtered:
    """One rule's returns on the joined calendar, and the days the filter keeps.

    ``daily`` is the rule's own return on each joined day, computed on its
    full calendar first. ``held`` says whether it held a position that day,
    and ``calendar_days`` is the length of the full calendar.
    """

    name: str
    days: pd.DatetimeIndex
    daily: NDArray[np.float64]
    held: NDArray[np.bool_]
    qualifies: NDArray[np.bool_]
    calendar_days: int

    @property
    def kept(self) -> int:
        return int(self.qualifies.sum())

    @property
    def kept_days(self) -> pd.DatetimeIndex:
        return self.days[self.qualifies]

    @property
    def filtered(self) -> NDArray[np.float64]:
        return self.daily[self.qualifies]

    @property
    def average_annual_return(self) -> float:
        """Location 3509's "annualized average return": 252 times the mean over the kept days."""
        return float(TRADING_DAYS * self.filtered.mean())

    @property
    def sharpe(self) -> float:
        return plain_sharpe(self.filtered)

    @property
    def apr(self) -> float:
        """The compounded APR over the kept days, the first reading that misses for buy on gap."""
        return compounded_apr(self.filtered)

    @property
    def held_days(self) -> int:
        """How many kept days the rule held a position on."""
        return int(self.held[self.qualifies].sum())

    @property
    def unfiltered(self) -> Reading:
        """Both figures over every joined day."""
        return reading(self.daily, np.ones(len(self.daily), dtype=bool))

    @property
    def zeroed(self) -> Reading:
        """The other days set to 0 and every joined day averaged, a reading that misses."""
        zeroed = np.where(self.qualifies, self.daily, 0.0)
        return reading(zeroed, np.ones(len(zeroed), dtype=bool))

    @property
    def summed(self) -> NDArray[np.float64]:
        """The daily returns summed over the kept days so far, one value per joined day.

        Every other day adds nothing. The last value is the kept days' sum,
        which is :attr:`average_annual_return` times ``kept / 252``, because
        that figure is an arithmetic mean. Added after the run by the
        write-up, like :func:`runs`.
        """
        return np.cumsum(np.where(self.qualifies, self.daily, 0.0))

    @property
    def welch(self) -> tuple[float, float]:
        """Welch's t and its two-sided p for the kept days' mean daily return against the rest.

        The rest are the other joined days. The test treats each day as
        independent of the others, which daily returns need not be, so it is
        a rough check on whether the kept days differ rather than a verdict.
        """
        test = stats.ttest_ind(self.filtered, self.daily[~self.qualifies], equal_var=False)
        return float(test.statistic), float(test.pvalue)


def vix_filter(
    name: str,
    days: pd.DatetimeIndex,
    daily: ArrayLike,
    held: ArrayLike,
    vix: pd.Series,
) -> Filtered:
    """Join a rule's calendar to VIX's and mark the days after a close above 35.

    ``daily`` and ``held`` run over ``days``, the rule's full calendar, and are
    taken on the joined days afterwards, so the rule itself is never rerun.
    """
    joined = common_days(days, vix)
    rows = days.get_indexer(joined)
    return Filtered(
        name=name,
        days=joined,
        daily=np.asarray(daily, dtype=float)[rows],
        held=np.asarray(held, dtype=bool)[rows],
        qualifies=qualifies(vix.reindex(joined).to_numpy(dtype=float)),
        calendar_days=len(days),
    )


@dataclass(frozen=True)
class Sources:
    """VIX, the stock panel's four fields and FSTX's, each with its vintage."""

    vix_member: VintageEntry
    vix: pd.Series
    stock_members: list[VintageEntry]
    stocks: dict[str, pd.DataFrame]
    fstx_member: VintageEntry
    fstx: pd.DataFrame


def guarded_spans(
    days: pd.DatetimeIndex, vix: pd.Series
) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    """The two spans of a window VIX is guarded over, either side of :data:`FLAGGED_DAY`.

    The first runs from the window's first joined day to :data:`BEFORE_FLAG`
    and the second from :data:`FLAGGED_DAY` to its last joined day, so the
    only day-over-day ratio neither reads is the flagged one.
    """
    joined = common_days(days, vix)
    return [(joined[0], BEFORE_FLAG), (FLAGGED_DAY, joined[-1])]


def read_sources(data_dir: Path | None = None) -> Sources:
    """VIX, the stocks and FSTX, with VIX guarded over :func:`guarded_spans` of each window.

    FSTX is guarded inside :func:`chan.opening_gap.read_sources`. The stocks
    are not guarded, as :mod:`chan.buy_on_gap` decides.
    """
    vix_members, vix_panel = load_panel(VIX_FILE, data_dir=data_dir)
    vix_member = next(m for m in vix_members if m.symbol == VIX)
    vix = vix_panel[VIX]
    stock_members, stocks = buy_on_gap.read_sources(data_dir)
    fstx_member, fstx = opening_gap.read_sources(data_dir)
    for days in (stocks["Close"].index, fstx.index):
        for start, end in guarded_spans(days, vix):
            refuse_window_crossing_a_break([(vix_member, vix)], start=start, end=end)
    return Sources(
        vix_member=vix_member,
        vix=vix,
        stock_members=stock_members,
        stocks=stocks,
        fstx_member=fstx_member,
        fstx=fstx,
    )


@dataclass(frozen=True)
class VixFilter:
    """Both rules filtered, FSTX under both readings of its return line, and the misses.

    ``as_of``, ``forward_filled``, ``own_calendar``, ``same_day`` and
    ``same_day_filled`` are FSTX's literal reading under the five alignments
    set aside, in the module docstring's order. ``fstx_full`` is Example
    7.1's literal figures on FSTX's full calendar, which location 3509 quotes
    unfiltered.
    """

    buy_on_gap: Filtered
    literal: Filtered
    momentum: Filtered
    as_of: Reading
    forward_filled: Reading
    own_calendar: Reading
    same_day: Reading
    same_day_filled: Reading
    fstx_full: opening_gap.Figures


def vix_filters(sources: Sources) -> VixFilter:
    """Run both rules unchanged on their own calendars, then filter each on VIX."""
    stocks = sources.stocks
    long = buy_on_gap.buy_on_gap(stocks["Open"], stocks["Low"], stocks["Close"])
    rule = opening_gap.opening_gap(sources.fstx)
    held_long = np.count_nonzero(long.positions, axis=1) > 0
    held_gap = rule.positions != 0
    vix = sources.vix
    return VixFilter(
        buy_on_gap=vix_filter("Buy on gap", long.days, long.daily, held_long, vix),
        literal=vix_filter("FSTX, literal", rule.days, rule.literal, held_gap, vix),
        momentum=vix_filter("FSTX, momentum", rule.days, rule.momentum, held_gap, vix),
        as_of=as_of_reading(rule.days, rule.literal, vix),
        forward_filled=forward_filled_reading(rule.days, rule.literal, vix),
        own_calendar=own_calendar_reading(rule.days, rule.literal, vix),
        same_day=same_day_reading(rule.days, rule.literal, vix, forward_fill=False),
        same_day_filled=same_day_reading(rule.days, rule.literal, vix, forward_fill=True),
        fstx_full=rule.literal_figures,
    )


def _verdict(value: float, printed: str) -> str:
    return "reproduced" if matches(value, printed) else f"gap {gap(value, printed):+g}"


def _row(label: str, kept: int, value: float, percent: str, sharpe: float, book: str) -> str:
    return (
        f"  {label:<44} {kept:>4}  {value:>10.6f} {percent:>5}  "
        f"{_verdict(100 * value, percent):<11} {sharpe:>10.6f} {book:>5}  {_verdict(sharpe, book)}"
    )


def report(sources: Sources, result: VixFilter) -> None:
    """Print the vintages, the join, both rules beside the book, the misses and the counts."""
    long, literal, momentum = result.buy_on_gap, result.literal, result.momentum
    print(
        "The VIX filter on buy on gap and the STOXX Europe 50 gap rule, "
        "Algorithmic Trading location 3509"
    )
    print(f"  vintage   {vintage_line(sources.vix_member)}")
    print(f"  prices    {panel_line(sources.stock_members)}")
    print(f"  vintage   {vintage_line(sources.fstx_member)}")
    for filtered in (long, literal):
        print(
            f"  join      {filtered.name.split(',')[0]} keeps {len(filtered.days)} of its "
            f"{filtered.calendar_days} days, {filtered.days[0].date()} to "
            f"{filtered.days[-1].date()}"
        )
    print(
        f"  rule      a day is kept when VIX closed above {THRESHOLD:g} on the previous joined day"
    )
    print(
        f"  guard     VIX over each window but its flagged move, {BEFORE_FLAG.date()} to "
        f"{FLAGGED_DAY.date()}"
    )
    print()
    print(
        f"  {'Figure, on the kept days':<44} {'Days':>4}  {'252 x mean':>10} {'Book':>5}  "
        f"{'Verdict':<11} {'Sharpe':>10} {'Book':>5}  Verdict"
    )
    for filtered, percent, book in (
        (long, BOOK_BUY_ON_GAP_PERCENT, BOOK_BUY_ON_GAP_SHARPE),
        (literal, BOOK_FSTX_PERCENT, BOOK_FSTX_SHARPE),
        (momentum, BOOK_FSTX_PERCENT, BOOK_FSTX_SHARPE),
    ):
        print(
            _row(
                filtered.name,
                filtered.kept,
                filtered.average_annual_return,
                percent,
                filtered.sharpe,
                book,
            )
        )
    print()
    print("Readings that miss, each beside the book's figure")
    print(
        f"  {'Buy on gap, compounded APR on the kept days':<44} {long.kept:>4}  "
        f"{long.apr:>10.6f} {BOOK_BUY_ON_GAP_PERCENT:>5}  "
        f"{_verdict(100 * long.apr, BOOK_BUY_ON_GAP_PERCENT)}"
    )
    for label, figures, percent, book in (
        (
            "Buy on gap, other days zeroed",
            long.zeroed,
            BOOK_BUY_ON_GAP_PERCENT,
            BOOK_BUY_ON_GAP_SHARPE,
        ),
        ("FSTX, literal, other days zeroed", literal.zeroed, BOOK_FSTX_PERCENT, BOOK_FSTX_SHARPE),
        (
            "FSTX, literal, latest VIX close before",
            result.as_of,
            BOOK_FSTX_PERCENT,
            BOOK_FSTX_SHARPE,
        ),
        (
            "FSTX, literal, forward-filled, one row back",
            result.forward_filled,
            BOOK_FSTX_PERCENT,
            BOOK_FSTX_SHARPE,
        ),
        (
            "FSTX, literal, one row back on its calendar",
            result.own_calendar,
            BOOK_FSTX_PERCENT,
            BOOK_FSTX_SHARPE,
        ),
        (
            "FSTX, literal, same-day VIX, NaN on holidays",
            result.same_day,
            BOOK_FSTX_PERCENT,
            BOOK_FSTX_SHARPE,
        ),
        (
            "FSTX, literal, same-day VIX, forward-filled",
            result.same_day_filled,
            BOOK_FSTX_PERCENT,
            BOOK_FSTX_SHARPE,
        ),
    ):
        print(
            _row(
                label,
                figures.kept,
                figures.average_annual_return,
                percent,
                figures.sharpe,
                book,
            )
        )
    print("  The same-day rows look ahead. VIX closes at 16:15 New York time, after FSTX's open.")
    print()
    print("Beside the replication. No source prints these, so none carries a verdict.")
    print(
        f"  kept days      {long.kept_days[0].date()} to {long.kept_days[-1].date()} for buy on "
        f"gap, {literal.kept_days[0].date()} to {literal.kept_days[-1].date()} for FSTX"
    )
    print(
        f"  held           buy on gap on {long.held_days} of its {long.kept} kept days, "
        f"FSTX on {literal.held_days} of its {literal.kept}"
    )
    for filtered in (long, literal):
        f = filtered.unfiltered
        print(
            f"  unfiltered     {filtered.name}, all {f.kept} joined days: 252 x mean "
            f"{f.average_annual_return:.6f}, Sharpe ratio {f.sharpe:.6f}"
        )
    print(
        f"  unfiltered     FSTX, literal, all {literal.calendar_days} days of Example 7.1: "
        f"252 x mean {result.fstx_full.average_annual_return:.6f}, "
        f"Sharpe ratio {result.fstx_full.sharpe:.6f}"
    )
    for filtered in (long, literal):
        t, p = filtered.welch
        print(
            f"  Welch's t      {filtered.name}, kept days against the other joined days: "
            f"t {t:.6f}, p {p:.6f}, treating days as independent"
        )
    print()
    print(
        f"  Annualised over {TRADING_DAYS} days with no risk-free rate and no cost. "
        "The stock prices hold only survivors."
    )
    print(
        "  No script ships for location 3509. The FSTX alignment was chosen after six were "
        "tried, and the five set aside are above."
    )
    print("  Exploratory. docs/replication-log.md Entry 47 carries the verdicts.")


def run(data_dir: Path | None = None) -> VixFilter:
    """Read the three vintages, run both rules, filter them and print the report."""
    sources = read_sources(data_dir)
    result = vix_filters(sources)
    report(sources, result)
    return result


def main() -> None:
    argparse.ArgumentParser(
        description="The VIX filter on buy on gap and the STOXX Europe 50 gap rule, "
        "location 3509 of Algorithmic Trading"
    ).parse_args()
    try:
        run()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day reaches the reader
        # as one line, the way chan.opening_gap.main does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
