"""Chan's two commodity seasonal trades, gasoline in April and natural gas in spring.

Chan argues that seasonal trades in commodity futures still pay where much of
the equity seasonality has weakened or disappeared, because the demand behind
them is physical: drivers before summer for gasoline, power generators before
air conditioning season for natural gas. Entry 7 tested two equity seasonals.
This module checks the two commodity trades he says are alive.

The rules are the revised edition's sidebars.

1. **Gasoline**, at Kindle location 4536. Buy one May contract at the close of
   April 13, or the following trading day if that is a holiday, and sell it at
   the close of April 25, or the previous trading day.
2. **Natural gas**, at location 4590. Buy one June contract at the close of
   February 25, or the following trading day, and sell it on April 15, or the
   previous trading day. The sidebar names no time of day for the exit, so the
   run sells at the close.

What decides each remaining choice was written on
[issue 19](https://github.com/l3a0/quantitative-trading/issues/19) before any
trade was computed, and the issue is the authority for it. In short, a year is
profitable when the exit settlement is strictly above the entry settlement on
one contract with no costs, and a year whose trade date has no row in its file
is reported as missing rather than moved.

**The data is EIA's contract-numbered settlements, not one file per contract.**
Contract 1 is whichever contract expires next, so the module has to say which
numbered file holds the May or June contract on a given day. The May gasoline
contract is contract 1 on both gasoline dates. The April contract stops trading
on the last trading day of March, and the May contract trades until the last
trading day of April. The June natural gas contract is contract 4 or 3 at the
entry, depending on whether the March contract has expired, and contract 2 at
the exit. :func:`chan.futures.ng_last_trade` gives each expiry. Today a
contract stops three trading days before delivery, and before mid-1997 it
stopped five or six days before, which :data:`chan.futures.NG_LEAD_DAYS`
records.
``tests/test_commodity_seasonals.py`` checks it against the last trading days
the Massive futures API recorded for every year from 2017, where its records
begin, to 2026, and against the files, which
keep an expiring contract in contract 1 on its last day.

**The gasoline contract changes in 2006.** RBOB futures began trading in
October 2005, so the run reads New York Harbor regular gasoline through 2005
and RBOB from 2006. :func:`gasoline_trade` takes the other contract for 2006
when asked, which the run prints as a side row.

**The calendar is computed rather than read from the files.** The natural gas
files hold a row repeating the previous trading day's settlement on every
exchange holiday from January 2018 to November 2019, and on almost none in
other years, so a row's presence does not say the exchange was open.
:func:`chan.futures.is_trading_day` uses NYMEX's holiday rules instead. Of
those holidays only Good Friday can land on a date this module reads. The
calendar and the expiry rules live in :mod:`chan.futures`, because the
calendar-spread test reads them too.

**A missing gasoline price stays missing, and the run measures why.**
Three gasoline years have no contract-1 row on a trade date, though the
exchange traded and the contract-2 file holds a row. :func:`gap_fills` asks
whether filling each missing price could decide its year. It fills each gap
two ways, by drawing a straight line between the rows on either side, and by
moving May's price on the last day before the gap, counting only days both
files hold, by June's change since that day, since June sits in contract 2. It
measures each way's error by hiding April days whose price the file holds,
in the same pattern of days as the gap, and filling them. Each year's
estimated move is smaller than its fill's typical miss. Fill 2's misses also
average above zero, guessing May low, so :class:`GapFill` corrects fill 2's
guess by its average miss and measures the spread of the misses around that
average. Even corrected, no year's chance of a profit reaches 95%.

Every result here is **exploratory**. Chan chose both trades after looking at
years before his book, which the run also reads, so on those years the run says
whether his counts reproduce. Nobody wrote down a test for the years after the
book before the run computed them, so the run says nothing about whether either
trade pays today.

A settlement is a ``Decimal`` as its file spells it, which
:func:`chan.futures.settlements` reads, so a zero change reads as zero rather
than as a float's rounding.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

# The calendar and the expiry rules moved to chan.futures. The three names
# aliased to themselves are imported only so Entry 11's tests, which import them
# from here, did not have to move.
from scipy import stats

from chan.futures import (
    contract_number,
    last_business_day,
    ng_last_trade,
    on_or_after,
    on_or_before,
    settlements,
)
from chan.futures import easter as easter
from chan.futures import is_trading_day as is_trading_day
from chan.futures import ng_lead_days as ng_lead_days
from chan.series import vintage_line

BOOK_REF = (
    "Chan, Quantitative Trading, revised edition, Kindle locations 4529 to 4632 "
    "and the two sidebars at 4536 and 4590"
)

#: New York Harbor regular gasoline, the contract RBOB replaced, contract 1.
HARBOR_GASOLINE = "EER-EPMR-PE1-Y35NY-DPG"
#: New York Harbor regular gasoline, contract 2, which holds June when May is
#: contract 1. Its file starts on 1994-01-20.
HARBOR_GASOLINE_2 = "EER-EPMR-PE2-Y35NY-DPG"
#: RBOB gasoline, contract 1.
RBOB_GASOLINE = "EER-EPMRR-PE1-Y35NY-DPG"
#: Henry Hub natural gas, by contract number.
NATURAL_GAS = {number: f"RNGC{number}" for number in (1, 2, 3, 4)}

#: The first year the run reads RBOB rather than the harbor contract.
FIRST_RBOB_YEAR = 2006

GASOLINE_ENTRY = (4, 13)
GASOLINE_EXIT = (4, 25)
NG_ENTRY = (2, 25)
NG_EXIT = (4, 15)


@dataclass(frozen=True)
class Trade:
    """One year's trade: when, in which file, at what prices, and whether it paid.

    ``entry_price`` and ``exit_price`` are ``None`` when the file holds no row
    on that day, and ``profitable`` is then ``None`` too, because a missing
    year counts neither way.
    """

    year: int
    entry_day: date
    exit_day: date
    entry_symbol: str
    exit_symbol: str
    entry_price: Decimal | None
    exit_price: Decimal | None

    @property
    def change(self) -> Decimal | None:
        if self.entry_price is None or self.exit_price is None:
            return None
        return self.exit_price - self.entry_price

    @property
    def profitable(self) -> bool | None:
        change = self.change
        return None if change is None else change > 0

    @property
    def relative_change(self) -> float | None:
        """The change over the entry price, the year's return on one contract's value."""
        change = self.change
        return None if change is None else float(change / self.entry_price)


def june_contract_number(day: date) -> int:
    """Which numbered natural gas file holds the June contract on ``day``, in February to May.

    :func:`chan.futures.contract_number` counts the earlier contracts still
    trading, and a contract still trades on its own last day.
    """
    return contract_number(day, day.year, 6, ng_last_trade)


def _price(symbol: str, day: date, data_dir: Path | None) -> Decimal | None:
    return settlements(symbol, data_dir=data_dir)[1].get(day)


def gasoline_symbol(year: int) -> str:
    return HARBOR_GASOLINE if year < FIRST_RBOB_YEAR else RBOB_GASOLINE


def gasoline_trade(year: int, *, symbol: str | None = None, data_dir: Path | None = None) -> Trade:
    """The May gasoline contract from the close of April 13 to the close of April 25."""
    entry_day = on_or_after(date(year, *GASOLINE_ENTRY))
    exit_day = on_or_before(date(year, *GASOLINE_EXIT))
    if exit_day >= last_business_day(year, 4):
        raise ValueError(f"{year}: the exit {exit_day} is not before the May contract expires")
    symbol = gasoline_symbol(year) if symbol is None else symbol
    return Trade(
        year=year,
        entry_day=entry_day,
        exit_day=exit_day,
        entry_symbol=symbol,
        exit_symbol=symbol,
        entry_price=_price(symbol, entry_day, data_dir),
        exit_price=_price(symbol, exit_day, data_dir),
    )


def natural_gas_trade(year: int, *, data_dir: Path | None = None) -> Trade:
    """The June natural gas contract from the close of February 25 to the close of April 15."""
    entry_day = on_or_after(date(year, *NG_ENTRY))
    exit_day = on_or_before(date(year, *NG_EXIT))
    entry_symbol = NATURAL_GAS[june_contract_number(entry_day)]
    exit_symbol = NATURAL_GAS[june_contract_number(exit_day)]
    return Trade(
        year=year,
        entry_day=entry_day,
        exit_day=exit_day,
        entry_symbol=entry_symbol,
        exit_symbol=exit_symbol,
        entry_price=_price(entry_symbol, entry_day, data_dir),
        exit_price=_price(exit_symbol, exit_day, data_dir),
    )


def profitable_count(trades: list[Trade]) -> int:
    return sum(1 for trade in trades if trade.profitable)


def runs_ending(trades: list[Trade]) -> dict[int, int]:
    """For each year, how many consecutive profitable years end in it.

    A loss resets the count to zero. A missing year also resets it, because a
    run nobody can read through is not a run the data shows.
    """
    runs, current = {}, 0
    for trade in sorted(trades, key=lambda trade: trade.year):
        current = current + 1 if trade.profitable else 0
        runs[trade.year] = current
    return runs


def daily_marks(trade: Trade, *, data_dir: Path | None = None) -> list[Decimal]:
    """The contract's settlement on each trading day from entry to exit.

    A natural gas trade's June contract moves between files as earlier
    contracts expire, so each day reads the file that holds it then. A day with
    no row is skipped.
    """
    marks, day = [], trade.entry_day
    while day <= trade.exit_day:
        if is_trading_day(day):
            symbol = (
                NATURAL_GAS[june_contract_number(day)]
                if trade.entry_symbol in NATURAL_GAS.values()
                else trade.entry_symbol
            )
            price = _price(symbol, day, data_dir)
            if price is not None:
                marks.append(price)
        day += timedelta(days=1)
    return marks


def _readable(trades: list[Trade]) -> list[Trade]:
    return [trade for trade in trades if trade.change is not None]


def mean_return(trades: list[Trade]) -> float:
    """The average yearly return, over the years with both prices."""
    return statistics.mean(trade.relative_change for trade in _readable(trades))


def sharpe_ratio(trades: list[Trade]) -> float:
    """The average yearly return divided by its standard deviation.

    Each trade is one year's return, so the ratio is already a yearly one. A
    futures position ties up no cash beyond margin, so its return is already a
    return above cash and nothing is subtracted.
    """
    returns = [trade.relative_change for trade in _readable(trades)]
    return statistics.mean(returns) / statistics.stdev(returns)


def sharpe_standard_error(trades: list[Trade]) -> float:
    """How far a Sharpe ratio from this few yearly results typically strays from the true one.

    Lo (2002) gives ``sqrt((1 + SR**2 / 2) / n)`` for ``n`` independent
    returns. One trade a year leaves ``n`` at 8 to 18 here, so the error is
    about a third of a Sharpe ratio of 1.
    """
    ratio = sharpe_ratio(trades)
    return math.sqrt((1 + ratio**2 / 2) / len(_readable(trades)))


def mean_interval(trades: list[Trade], level: float = 0.95) -> tuple[float, float]:
    """The range that holds the true mean yearly return at ``level``, from Student's t."""
    returns = [trade.relative_change for trade in _readable(trades)]
    n, mean = len(returns), statistics.mean(returns)
    half = stats.t.ppf((1 + level) / 2, n - 1) * statistics.stdev(returns) / math.sqrt(n)
    return mean - half, mean + half


def change_p_value(before: list[Trade], after: list[Trade]) -> float:
    """Welch's two-sided p-value for the mean yearly return differing between two periods.

    Welch's test lets each period keep its own spread, which matters here
    because natural gas swung far more after 2008 than before.
    """
    one = [trade.relative_change for trade in _readable(before)]
    two = [trade.relative_change for trade in _readable(after)]
    return float(stats.ttest_ind(one, two, equal_var=False).pvalue)


def rank_p_value(before: list[Trade], after: list[Trade]) -> float:
    """The Mann-Whitney two-sided p-value for one period's years sitting lower than the other's.

    It ranks every year from worst to best and ignores how far apart they are,
    so it asks whether the typical year changed. One extreme year moves it
    by one rank, where it can move :func:`change_p_value` a long way.

    The p-value is exact, counted over every way the years could split
    between the periods. scipy's default switches to a normal approximation
    once both periods hold more than eight years, which gives natural gas's
    15 against 15 a chance of 0.79% where the exact count gives 0.66%, while
    gasoline's 8 later years would stay exact. So the method is named rather
    than left to the sample sizes. The years hold no ties, so the exact count
    needs no correction for them.
    """
    one = [trade.relative_change for trade in _readable(before)]
    two = [trade.relative_change for trade in _readable(after)]
    return float(stats.mannwhitneyu(one, two, alternative="two-sided", method="exact").pvalue)


def pairs_won(before: list[Trade], after: list[Trade]) -> tuple[float, int]:
    """How many pairings of an earlier year with a later year the earlier year won, of how many.

    This is the count :func:`rank_p_value` tests, Mann-Whitney's U for the
    earlier period, so a tie counts as half a win. With nothing changed, the
    earlier year wins about half the pairs.
    """
    one = [trade.relative_change for trade in _readable(before)]
    two = [trade.relative_change for trade in _readable(after)]
    return float(stats.mannwhitneyu(one, two).statistic), len(one) * len(two)


def max_drawdown(trades: list[Trade], *, data_dir: Path | None = None) -> float:
    """The largest fall from a peak in the summed returns, marked every trading day.

    Each year stakes one contract's value at entry, so the years' returns add
    rather than compound, and the fall is a fraction of one stake. Marking
    every day catches a fall inside a trade that ended the year with a profit.
    """
    total = peak = drawdown = 0.0
    for trade in _readable(trades):
        for price in daily_marks(trade, data_dir=data_dir):
            value = total + float((price - trade.entry_price) / trade.entry_price)
            peak = max(peak, value)
            drawdown = max(drawdown, peak - value)
        total += trade.relative_change
    return drawdown


def gasoline_trades(first: int, last: int, *, data_dir: Path | None = None) -> list[Trade]:
    return [gasoline_trade(year, data_dir=data_dir) for year in range(first, last + 1)]


def natural_gas_trades(first: int, last: int, *, data_dir: Path | None = None) -> list[Trade]:
    return [natural_gas_trade(year, data_dir=data_dir) for year in range(first, last + 1)]


#: The years each file can serve. EIA's RBOB and natural gas files end on
#: 2024-04-05, before either trade's 2024 exit, so 2023 is the last whole year.
GASOLINE_YEARS = (1995, 2023)
NG_YEARS = (1994, 2023)

#: The year the book's natural gas runs are counted from, as issue 19 pins it.
#: The gasoline sidebar's "every year since 1995" names the same start. EIA's
#: files reach back to 1994, so the run printed beside it counts from there.
RUN_START = 1995


# --- What a fill of a missing gasoline price could say ------------------------

#: The years whose April days test each fill: from the first April the
#: contract-2 file holds to the last the run reads the harbor contract in.
FILL_TEST_YEARS = (1994, FIRST_RBOB_YEAR - 1)


@dataclass(frozen=True)
class GapFill:
    """One missing gasoline price, its two fills, and how far each can be trusted.

    ``before`` and ``after`` are the nearest days around ``day`` that hold a
    contract-1 row. ``base`` is the last day before ``day`` that both files
    hold, where the June fill starts. It is ``before`` unless the contract-2
    file misses that day too. ``steps`` counts the trading days from
    ``before`` to ``day``, from ``day`` to ``after``, and from ``base`` to
    ``day``. ``other`` is the trade's price on its other date. The ``*_error``
    fields are each fill's root mean square error on ``tested`` April days
    whose rows sit the same numbers of trading days away, the typical size of
    a miss. ``june_bias`` is fill 2's average miss on those days, the true
    price minus the guess, and ``june_spread`` the sample standard deviation
    of its misses around that average.
    """

    year: int
    leg: str
    day: date
    before: date
    after: date
    base: date
    steps: tuple[int, int, int]
    other: Decimal
    linear: float
    june: float
    linear_error: float
    june_error: float
    june_bias: float
    june_spread: float
    tested: int

    def move(self, fill: float) -> float:
        """The year's change in dollars a gallon with ``fill`` in the gap."""
        return float(self.other) - fill if self.leg == "entry" else fill - float(self.other)

    @property
    def linear_margin(self) -> float:
        """The linear fill's move in units of that fill's typical error."""
        return self.move(self.linear) / self.linear_error

    @property
    def june_corrected(self) -> float:
        """Fill 2's guess moved by its average miss."""
        return self.june + self.june_bias

    @property
    def june_margin(self) -> float:
        """The year's move with the corrected guess, in units of the spread."""
        return self.move(self.june_corrected) / self.june_spread

    @property
    def june_chance(self) -> float:
        """The chance the year was a profit, if fill 2's misses are normal
        around their average."""
        return 0.5 * (1 + math.erf(self.june_margin / math.sqrt(2)))


def _step(day: date, steps: int) -> date:
    """The trading day ``steps`` trading days after ``day``, or before it when negative."""
    sign = 1 if steps > 0 else -1
    for _ in range(abs(steps)):
        day += timedelta(days=sign)
        while not is_trading_day(day):
            day += timedelta(days=sign)
    return day


def _trading_days_between(earlier: date, later: date) -> int:
    """How many trading days after ``earlier`` it takes to reach ``later``."""
    steps, day = 0, earlier
    while day < later:
        day, steps = _step(day, 1), steps + 1
    return steps


def _fills(day: date, around: tuple[date, date, date], steps: tuple[int, int, int], one, two):
    """The linear fill and the June fill of contract 1 on ``day``.

    ``around`` is the row before, the row after and the June fill's base. The
    linear fill weights the two rows by how many trading days away each sits.
    The June fill adds June's change since the base to May's price there.
    """
    before, after, base = around
    weight = Decimal(steps[0]) / Decimal(steps[0] + steps[1])
    linear = float(one[before] + (one[after] - one[before]) * weight)
    june = float(one[base] + two[day] - two[base])
    return linear, june


def _test_day_stage(day: date, steps: tuple[int, int, int], last: date, one, two) -> int:
    """How far ``day`` gets through the checks that make it a test day.

    0 means its pattern reaches outside April, 1 that it fits but May's file
    misses a price it needs, 2 that May's prices are all there but June's file
    misses one, and 3 that it is a test day. The pattern is the row before,
    the row after and fill 2's base, the same numbers of trading days away as
    the gap's, and all of it must lie in April, when May is contract 1, so no
    fill reaches across a roll.
    """
    around = (_step(day, -steps[0]), _step(day, steps[1]), _step(day, -steps[2]))
    before, after, base = around
    if min(before, base).month != 4 or after > last:
        return 0
    if not all(d in one for d in (*around, day)):
        return 1
    if not all(d in two for d in (base, day)):
        return 2
    return 3


def _april_days():
    """Every April trading day of :data:`FILL_TEST_YEARS`, with its month's last."""
    for year in range(FILL_TEST_YEARS[0], FILL_TEST_YEARS[1] + 1):
        last = last_business_day(year, 4)
        day = on_or_after(date(year, 4, 1))
        while day <= last:
            yield day, last
            day = _step(day, 1)


def _test_days(steps: tuple[int, int, int], one, two) -> list[tuple[date, tuple[date, date, date]]]:
    """Every April day whose fills can be tested in a gap's pattern of steps,
    with its row before, row after and base."""
    return [
        (day, (_step(day, -steps[0]), _step(day, steps[1]), _step(day, -steps[2])))
        for day, last in _april_days()
        if _test_day_stage(day, steps, last, one, two) == 3
    ]


def count_test_days(fill: GapFill, *, data_dir: Path | None = None) -> tuple[int, int, int, int]:
    """How the April trading days narrow to ``fill``'s test days: all of them,
    those whose pattern fits inside April, those with every May price the fills
    need, and those that also have both of fill 2's June prices. The last is
    ``fill.tested``."""
    one = settlements(HARBOR_GASOLINE, data_dir=data_dir)[1]
    two = settlements(HARBOR_GASOLINE_2, data_dir=data_dir)[1]
    stages = [_test_day_stage(day, fill.steps, last, one, two) for day, last in _april_days()]
    return (
        len(stages),
        sum(stage >= 1 for stage in stages),
        sum(stage >= 2 for stage in stages),
        sum(stage == 3 for stage in stages),
    )


def _fill_errors(steps: tuple[int, int, int], one, two) -> tuple[float, float, float, float, int]:
    """Each fill's root mean square error on the test days, and fill 2's average
    miss and the spread of its misses around it."""
    linear, june = [], []
    for day, around in _test_days(steps, one, two):
        fill_linear, fill_june = _fills(day, around, steps, one, two)
        linear.append(float(one[day]) - fill_linear)
        june.append(float(one[day]) - fill_june)

    def rms(errors: list[float]) -> float:
        return math.sqrt(statistics.fmean(e * e for e in errors))

    return rms(linear), rms(june), statistics.fmean(june), statistics.stdev(june), len(linear)


def fill_two_misses(
    fill: GapFill, *, data_dir: Path | None = None
) -> list[tuple[date, date, float]]:
    """Fill 2's miss on every test day of ``fill``'s pattern, the true price
    minus the guess in dollars a gallon, with the day and the base the guess
    starts from. Their average is ``fill.june_bias`` and their spread
    ``fill.june_spread``."""
    one = settlements(HARBOR_GASOLINE, data_dir=data_dir)[1]
    two = settlements(HARBOR_GASOLINE_2, data_dir=data_dir)[1]
    return [
        (day, around[2], float(one[day]) - _fills(day, around, fill.steps, one, two)[1])
        for day, around in _test_days(fill.steps, one, two)
    ]


def gap_fills(*, data_dir: Path | None = None) -> list[GapFill]:
    """Every missing gasoline price in the harbor years from 1995, filled two ways."""
    one = settlements(HARBOR_GASOLINE, data_dir=data_dir)[1]
    two = settlements(HARBOR_GASOLINE_2, data_dir=data_dir)[1]
    found = []
    for trade in gasoline_trades(RUN_START, FIRST_RBOB_YEAR - 1, data_dir=data_dir):
        for leg, day, price, other in (
            ("entry", trade.entry_day, trade.entry_price, trade.exit_price),
            ("exit", trade.exit_day, trade.exit_price, trade.entry_price),
        ):
            if price is not None or other is None:
                continue
            around = (
                max(d for d in one if d < day),
                min(d for d in one if d > day),
                max(d for d in one if d < day and d in two),
            )
            steps = (
                _trading_days_between(around[0], day),
                _trading_days_between(day, around[1]),
                _trading_days_between(around[2], day),
            )
            linear, june = _fills(day, around, steps, one, two)
            linear_error, june_error, june_bias, june_spread, tested = _fill_errors(steps, one, two)
            found.append(
                GapFill(
                    year=trade.year,
                    leg=leg,
                    day=day,
                    before=around[0],
                    after=around[1],
                    base=around[2],
                    steps=steps,
                    other=other,
                    linear=linear,
                    june=june,
                    linear_error=linear_error,
                    june_error=june_error,
                    june_bias=june_bias,
                    june_spread=june_spread,
                    tested=tested,
                )
            )
    return found


def _row(trade: Trade) -> str:
    if trade.profitable is None:
        result = "missing"
    else:
        result = f"{trade.change:+.3f}  {'profit' if trade.profitable else 'loss'}"
    symbols = (
        trade.entry_symbol
        if trade.entry_symbol == trade.exit_symbol
        else f"{trade.entry_symbol} -> {trade.exit_symbol}"
    )
    return (
        f"  {trade.year}  {trade.entry_day} {trade.entry_price!s:>6} -> "
        f"{trade.exit_day} {trade.exit_price!s:>6}  {result:<16} {symbols}"
    )


def main() -> None:
    """Print every year's trade and the counts the book prints beside its own."""
    gasoline = gasoline_trades(*GASOLINE_YEARS)
    gas = natural_gas_trades(*NG_YEARS)
    print("Chan's commodity seasonal trades (revised edition)")
    print(f"  {BOOK_REF}")
    print("  vintages:")
    for symbol in (HARBOR_GASOLINE, RBOB_GASOLINE, *(NATURAL_GAS[n] for n in (2, 3, 4))):
        print(f"    {vintage_line(settlements(symbol)[0])}")
    print()
    print("Gasoline, the May contract, close of April 13 to close of April 25:")
    for trade in gasoline:
        print(_row(trade))
    in_book = [trade for trade in gasoline if 1995 <= trade.year <= 2015]
    later = [trade for trade in gasoline if 2007 <= trade.year <= 2015]
    first_edition = [trade for trade in gasoline if trade.year <= 2008]
    print(
        f"  1995 to 2015: {profitable_count(in_book)} of {len(in_book)} profitable   "
        "(the book prints 19 of 21)"
    )
    print(
        f"  2007 to 2015, the years the book calls out of sample: "
        f"{profitable_count(later)} of {len(later)}"
    )
    print(
        f"  1995 to 2008: {profitable_count(first_edition)} of {len(first_edition)}   "
        "(the sidebar says a profit every year since 1995)"
    )
    side = gasoline_trade(2006, symbol=HARBOR_GASOLINE)
    print(f"  2006 on the harbor contract instead of RBOB, a side row:\n{_row(side)}")
    print()
    print("Natural gas, the June contract, close of February 25 to close of April 15:")
    for trade in gas:
        print(_row(trade))
    runs = runs_ending([trade for trade in gas if trade.year >= RUN_START])
    print(
        f"  counted from {RUN_START}, the run ending in 2007: {runs[2007]}   "
        "(the main text prints 13)"
    )
    print(
        f"  counted from {RUN_START}, the run ending in 2008: {runs[2008]}   "
        "(the sidebar prints 14)"
    )
    long_runs = {year: run for year, run in runs.items() if run >= 13}
    print(
        f"  every run of 13 or more from {RUN_START}, by the year it reaches that length: "
        f"{long_runs or 'none'}"
    )
    from_data = runs_ending(gas)
    print(
        f"  counted from {NG_YEARS[0]}, the first year the files hold a whole trade, "
        f"the same two runs are "
        f"{from_data[2007]} and {from_data[2008]}"
    )
    through = [trade for trade in gas if trade.year <= 2008]
    after = [trade for trade in gas if trade.year >= 2009]
    print(f"  1994 to 2008: {profitable_count(through)} of {len(through)} profitable")
    print(f"  2009 to 2023: {profitable_count(after)} of {len(after)} profitable")
    print()
    print("Every result here is exploratory. docs/replication-log.md Entry 11 carries")
    print("the verdicts.")


if __name__ == "__main__":
    main()
