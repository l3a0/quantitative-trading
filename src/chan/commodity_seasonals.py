"""Chan's two commodity seasonal trades, gasoline in April and natural gas in spring.

Chan argues that seasonal trades in commodity futures still pay where the
equity ones have died, because the demand behind them is physical: drivers
before summer for gasoline, power generators before air conditioning season
for natural gas. Entry 7 reproduced the equity seasonals and found them dead
as he said. This module checks the two he says are alive.

The rules are the revised edition's sidebars.

1. **Gasoline**, at Kindle location 4536. Buy one May contract at the close of
   April 13, or the following trading day if that is a holiday, and sell it at
   the close of April 25, or the previous trading day.
2. **Natural gas**, at location 4590. Buy one June contract at the close of
   February 25, or the following trading day, and sell it at the close of
   April 15, or the previous trading day.

What decides each remaining choice was written on
[issue 19](https://github.com/l3a0/quantitative-trading/issues/19) before any
trade was computed, and the issue is the authority for it. In short, a year is
profitable when the exit settlement is strictly above the entry settlement on
one contract with no costs, and a year whose trade date has no row in its file
is reported as missing rather than moved.

**The data is EIA's contract-numbered settlements, not one file per contract.**
Contract 1 is whichever contract expires next, so the module has to say which
numbered file holds the May or June contract on a given day. The May gasoline
contract is contract 1 on both gasoline dates, because it trades until the last
business day of April. The June natural gas contract is contract 4 or 3 at the
entry, depending on whether the March contract has expired, and contract 2 at
the exit. :func:`ng_last_trade` gives each expiry.
``tests/test_commodity_seasonals.py`` checks it against the exchange's own last
trading days for the years the Massive futures API covers, and against the
files, which keep an expiring contract in contract 1 on its last day.

**The gasoline contract changes in 2006.** RBOB futures began trading in
October 2005, so the run reads New York Harbor regular gasoline through 2005
and RBOB from 2006. :func:`gasoline_trade` takes the other contract for 2006
when asked, which the run prints as a side row.

**The calendar is computed rather than read from the files.** The natural gas
files carry exchange holidays as rows repeating the day before's settlement, so
a row's presence does not say the exchange was open. :func:`is_trading_day`
uses NYMEX's holiday rules instead. Of those holidays only Good Friday can land
on a date this module reads.

Every result here is **exploratory**. Chan chose both trades after looking at
the same history the run reads, so the run says whether his counts reproduce
and nothing about whether either trade pays today.

The parse uses the standard library's ``csv`` and ``decimal``, as
:mod:`chan.bill_rates` does. A settlement is compared exactly as its file spells
it, so a zero change reads as zero rather than as a float's rounding.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from functools import cache
from pathlib import Path

from chan.series import vintage_line
from chan.vintage import VintageEntry, read_vintage, resolve_vintage

BOOK_REF = (
    "Chan, Quantitative Trading, revised edition, Kindle locations 4529 to 4632 "
    "and the two sidebars at 4536 and 4590"
)

VENDOR = "eia"
PRICE_BASIS = "raw"

#: New York Harbor regular gasoline, the contract RBOB replaced, contract 1.
HARBOR_GASOLINE = "EER-EPMR-PE1-Y35NY-DPG"
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

#: Days NYMEX closed outside its holiday rules. None falls between February 20
#: and April 30, so none can move a date this module reads, and they are listed
#: so the calendar is the exchange's rather than one tuned to these trades.
UNSCHEDULED_CLOSURES = frozenset(
    date.fromisoformat(day)
    for day in (
        "2001-09-11",
        "2001-09-12",
        "2001-09-13",
        "2001-09-14",
        "2004-06-11",
        "2007-01-02",
        "2012-10-29",
        "2012-10-30",
        "2018-12-05",
    )
)


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


def easter(year: int) -> date:
    """Western Easter Sunday, by the anonymous Gregorian algorithm."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    m = (32 + 2 * e + 2 * i - h - k) % 7
    n = (a + 11 * h + 22 * m) // 451
    month, day = divmod(h + m - 7 * n + 114, 31)
    return date(year, month, day + 1)


def good_friday(year: int) -> date:
    return easter(year) - timedelta(days=2)


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    """The ``n``th ``weekday`` of the month, Monday being 0, or the last when ``n`` is -1."""
    if n == -1:
        last = date(year, month + 1, 1) - timedelta(days=1) if month < 12 else date(year, 12, 31)
        return last - timedelta(days=(last.weekday() - weekday) % 7)
    first = date(year, month, 1)
    return first + timedelta(days=(weekday - first.weekday()) % 7 + 7 * (n - 1))


def _observed(day: date) -> date | None:
    """The weekday a fixed-date holiday is observed on, or ``None`` for New Year on a Saturday.

    A Saturday holiday moves to the Friday before and a Sunday one to the
    Monday after, except New Year's Day on a Saturday, which the exchange does
    not move back into the old year.
    """
    if day.weekday() == 5:
        return None if (day.month, day.day) == (1, 1) else day - timedelta(days=1)
    if day.weekday() == 6:
        return day + timedelta(days=1)
    return day


@cache
def nymex_holidays(year: int) -> frozenset[date]:
    """NYMEX's full-day holidays in ``year``, on the weekdays the exchange observed them."""
    fixed = [_observed(date(year, month, day)) for month, day in ((1, 1), (7, 4), (12, 25))]
    floating = [
        _nth_weekday(year, 2, 0, 3),  # Presidents' Day
        good_friday(year),
        _nth_weekday(year, 5, 0, -1),  # Memorial Day
        _nth_weekday(year, 9, 0, 1),  # Labor Day
        _nth_weekday(year, 11, 3, 4),  # Thanksgiving
    ]
    if year >= 1998:
        floating.append(_nth_weekday(year, 1, 0, 3))  # Martin Luther King Jr. Day
    return frozenset(day for day in fixed + floating if day is not None)


def is_trading_day(day: date) -> bool:
    return (
        day.weekday() < 5
        and day not in nymex_holidays(day.year)
        and day not in UNSCHEDULED_CLOSURES
    )


def on_or_after(day: date) -> date:
    """The day itself if the exchange was open, else the next day it was."""
    while not is_trading_day(day):
        day += timedelta(days=1)
    return day


def on_or_before(day: date) -> date:
    """The day itself if the exchange was open, else the last day before it that was."""
    while not is_trading_day(day):
        day -= timedelta(days=1)
    return day


def ng_last_trade(year: int, delivery_month: int) -> date:
    """A natural gas contract's last trading day, three business days before delivery starts."""
    day = date(year, delivery_month, 1)
    counted = 0
    while counted < 3:
        day -= timedelta(days=1)
        if is_trading_day(day):
            counted += 1
    return day


def last_business_day(year: int, month: int) -> date:
    """The last trading day of a month, when a gasoline contract for the next month expires."""
    following = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    return on_or_before(following - timedelta(days=1))


def june_contract_number(day: date) -> int:
    """Which numbered natural gas file holds the June contract on ``day``, in February to May.

    Contract 1 is the earliest contract still trading, and a contract still
    trades on its own last day, so June's number is one more than the count of
    the March, April and May contracts that have not yet expired.
    """
    earlier = sum(1 for month in (3, 4, 5) if day <= ng_last_trade(day.year, month))
    return 1 + earlier


@cache
def settlements(
    symbol: str, *, data_dir: Path | None = None
) -> tuple[VintageEntry, dict[date, Decimal]]:
    """A committed EIA vintage's entry and its settlements by day, read only after they verify."""
    entry = resolve_vintage(
        vendor=VENDOR, symbol=symbol, price_basis=PRICE_BASIS, data_dir=data_dir
    )
    reader = csv.reader(io.StringIO(read_vintage(entry, data_dir=data_dir).decode("utf-8")))
    header = next(reader, None)
    if header != ["Date", "Close"]:
        raise ValueError(f"{entry.path}: the header reads {header!r}, not ['Date', 'Close']")
    return entry, {date.fromisoformat(day): Decimal(value) for day, value in reader}


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
        f"  counted from {NG_YEARS[0]}, the files' first year, the same two runs are "
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
