"""NYMEX's trading calendar, the expiry rules, and EIA's contract-numbered files.

Two experiments read EIA's futures settlements, and both need the same three
things: which days the exchange was open, which day each contract stopped
trading, and so which numbered file holds a given contract on a given day.
Entry 11's seasonal trades, in :mod:`chan.commodity_seasonals`, were the first
consumer. The calendar-spread test in :mod:`chan.stationary_candidates` is the
second, and it would otherwise import a chapter's replication to read a file,
which :mod:`chan.series` already decided against for the price readers. So
the rules live here and the seasonal module imports them back.
[Issue 137](https://github.com/l3a0/quantitative-trading/issues/137) moved
them, and the reasoning for every rule below is unchanged from
[issue 19](https://github.com/l3a0/quantitative-trading/issues/19) except
where a comment says otherwise.

**EIA numbers contracts by expiry, not by delivery month.** Contract 1 is the
earliest contract still trading, and a contract still trades on its own last
day, so it stays contract 1 through that day and its successor becomes
contract 1 on the next trading day. :func:`contract_number` turns a delivery
month into a file number on one day. :data:`NATURAL_GAS_CONTRACTS` and
:data:`RBOB_CONTRACTS` name each product's four files and its expiry rule.

**The calendar is computed rather than read from the files.** The natural gas
files carry exchange holidays as rows repeating the day before's settlement, so
a row's presence does not say the exchange was open. :func:`is_trading_day`
uses NYMEX's holiday rules instead.

**The expiry rules were checked two ways.** Against the last trading days the
Massive futures API recorded for 16 natural gas contracts, which
``tests/test_commodity_seasonals.py`` pins. And against the files themselves,
through :func:`handover_fit`, which asks whether the files' prices hand over
from one contract to the next on the day the rule says. Read over every expiry
both products' files cover, the rule's day fits about nine times in ten and a
day either side about one in ten. ``tests/test_stationary_candidates.py`` pins
those counts.

The parse uses the standard library's ``csv`` and ``decimal``, as
:mod:`chan.bill_rates` does. A settlement is compared exactly as its file spells
it, so a zero change reads as zero rather than as a float's rounding.
"""

from __future__ import annotations

import csv
import io
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from functools import cache
from pathlib import Path

from chan.vintage import VintageEntry, read_vintage, resolve_vintage

VENDOR = "eia"
PRICE_BASIS = "raw"

#: Days NYMEX closed outside its holiday rules. The only one between February
#: 20 and April 30 is 1994-04-27, Richard Nixon's funeral, which moves the May
#: 1994 natural gas expiry and no trade date. They are listed so the calendar is
#: the exchange's rather than one tuned to these trades.
#:
#: Three days this list used to carry are gone: 2012-10-29 and 2012-10-30, when
#: Hurricane Sandy closed the trading floor, and 2018-12-05. All eight natural
#: gas and RBOB files hold a settlement on each, and on each day most of them
#: differ from the day before, which a holiday row repeating a settlement does
#: not. Counted as closed, the Sandy days put the November 2012 natural gas
#: expiry on 2012-10-25, two trading days before the files hand over.
#: ``tests/test_stationary_candidates.py`` pins that every file settled on all
#: three.
UNSCHEDULED_CLOSURES = frozenset(
    date.fromisoformat(day)
    for day in (
        "1994-04-27",
        "2001-09-11",
        "2001-09-12",
        "2001-09-13",
        "2001-09-14",
        "2004-06-11",
        "2007-01-02",
    )
)


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


def next_trading_day(day: date) -> date:
    return on_or_after(day + timedelta(days=1))


def previous_trading_day(day: date) -> date:
    return on_or_before(day - timedelta(days=1))


def trading_days(first: date, last: date) -> tuple[date, ...]:
    """Every trading day from ``first`` to ``last``, both included when the exchange was open."""
    days, day = [], on_or_after(first)
    while day <= last:
        days.append(day)
        day = next_trading_day(day)
    return tuple(days)


#: How many trading days before delivery a natural gas contract stopped
#: trading, by the first delivery month each count applies to. Three is the
#: rule today and the one issue 19 first pinned. The files show the March 1996
#: and March 1997 contracts stopping earlier: on 1996-02-26 each numbered file
#: continues the next one's settlement from 1996-02-23, the handover a five-day
#: rule predicts and a three-day rule does not. The boundaries are measured from
#: the files' handovers, where the curve is steep enough to show one, and the
#: review that found them recorded the measurement on the pull request.
NG_LEAD_DAYS = ((date(1990, 1, 1), 6), (date(1996, 2, 1), 5), (date(1997, 6, 1), 3))


def ng_lead_days(year: int, delivery_month: int) -> int:
    """How many trading days before delivery the contract's trading stopped."""
    first = date(year, delivery_month, 1)
    return [days for start, days in NG_LEAD_DAYS if start <= first][-1]


def ng_last_trade(year: int, delivery_month: int) -> date:
    """A natural gas contract's last trading day, ``ng_lead_days`` before delivery starts."""
    day = date(year, delivery_month, 1)
    counted, lead = 0, ng_lead_days(year, delivery_month)
    while counted < lead:
        day -= timedelta(days=1)
        if is_trading_day(day):
            counted += 1
    return day


def last_business_day(year: int, month: int) -> date:
    """The last trading day of a month, when a gasoline contract for the next month expires."""
    following = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    return on_or_before(following - timedelta(days=1))


def month_step(year: int, month: int, step: int) -> tuple[int, int]:
    """The delivery month ``step`` months after ``year``-``month``, or before when negative."""
    index = year * 12 + (month - 1) + step
    return index // 12, index % 12 + 1


def rbob_last_trade(year: int, delivery_month: int) -> date:
    """An RBOB contract's last trading day, the last business day of the month before delivery."""
    return last_business_day(*month_step(year, delivery_month, -1))


#: A contract's last trading day from its delivery year and month.
LastTrade = Callable[[int, int], date]


def contract_number(day: date, year: int, month: int, last_trade: LastTrade) -> int:
    """Which numbered file holds the contract for delivery in ``year``-``month`` on ``day``.

    One more than the count of earlier contracts still trading, counting a
    contract as trading on its own last day. It takes the delivery as a year
    and a month rather than reading the year off ``day``, because a January
    contract is read in December of the year before.
    """
    if day > last_trade(year, month):
        raise ValueError(f"the {year}-{month:02d} contract stopped trading before {day}")
    number, earlier = 1, month_step(year, month, -1)
    while day <= last_trade(*earlier):
        number += 1
        earlier = month_step(*earlier, -1)
    return number


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


@dataclass(frozen=True)
class Product:
    """One commodity's four contract-numbered EIA files and its expiry rule."""

    name: str
    symbols: tuple[str, str, str, str]
    last_trade: LastTrade

    def files(self, *, data_dir: Path | None = None) -> tuple[dict[date, Decimal], ...]:
        """Contracts 1 to 4's settlements by day, in that order."""
        return tuple(settlements(symbol, data_dir=data_dir)[1] for symbol in self.symbols)


NATURAL_GAS_CONTRACTS = Product(
    name="natural gas",
    symbols=("RNGC1", "RNGC2", "RNGC3", "RNGC4"),
    last_trade=ng_last_trade,
)

RBOB_CONTRACTS = Product(
    name="RBOB gasoline",
    symbols=(
        "EER-EPMRR-PE1-Y35NY-DPG",
        "EER-EPMRR-PE2-Y35NY-DPG",
        "EER-EPMRR-PE3-Y35NY-DPG",
        "EER-EPMRR-PE4-Y35NY-DPG",
    ),
    last_trade=rbob_last_trade,
)


def shifted(product: Product, days: int) -> Product:
    """The same product with every expiry moved ``days`` trading days, later when positive.

    Nothing reads a shifted product as the exchange's rule. It exists so the
    suite can ask what a rule one day wrong would change.
    """

    def last_trade(year: int, month: int) -> date:
        day = product.last_trade(year, month)
        for _ in range(abs(days)):
            day = next_trading_day(day) if days > 0 else previous_trading_day(day)
        return day

    return Product(
        name=f"{product.name}, expiries moved {days:+d}",
        symbols=product.symbols,
        last_trade=last_trade,
    )


def handover_fit(product: Product, last: date, *, data_dir: Path | None = None) -> Decimal | None:
    """How much better a handover after ``last`` fits the files than no handover.

    The spreads between neighbouring files on the next trading day are set
    against the spreads one file further up on ``last``, which a handover
    predicts, and against the same files' spreads, which no handover
    predicts. A negative value says the handover fits better. ``None`` when a
    file the comparison reads has no row on either day, because a comparison
    with a hole in it is not one.
    """
    files = product.files(data_dir=data_dir)
    nxt = next_trading_day(last)
    if any(last not in f for f in files) or any(nxt not in f for f in files[:3]):
        return None

    def spread(day: date, n: int) -> Decimal:
        return files[n - 1][day] - files[n][day]

    moved = sum(abs(spread(nxt, n) - spread(last, n + 1)) for n in (1, 2))
    stayed = sum(abs(spread(nxt, n) - spread(last, n)) for n in (1, 2))
    return moved - stayed
