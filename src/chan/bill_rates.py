"""Read the committed three-month Treasury-bill series and summarise a window of it.

The risk parity post quotes what cash paid over its run: an average bill rate
for the whole span, one for each side of the March 2022 rate rise, and a count
of the months the rate sat near zero. Those figures were first read off the St.
Louis Fed's website, and nothing in this repo could recheck them, which is the
state the premise in [docs/design.md](../../docs/design.md) exists to prevent.
This module computes them from a committed vintage instead, so
``tests/test_bill_rates.py`` can pin them and a reader can rerun them.

The vintage is FRED's series TB3MS, recorded under the ``rate`` basis.
[data/README.md](../../data/README.md) says what it holds and why it is not a
price. In short, each row is one calendar month, dated the first of that month,
and holds the month's average three-month bill rate in percent a year.

Every rate this module returns is a decimal a year, so 1.744% comes back as
0.01744. A threshold passed in is a decimal too. The file's percent text is
divided by 100 in exact decimal arithmetic before it becomes a float, so a rate
written ``0.25`` compares equal to a threshold written ``0.0025``. Dividing the
float instead lands one unit in the last place away for 249 of the 1,112 rows.

A window is named by two months written ``YYYY-MM``, and both ends are
included. October 2003 to August 2026 is the 275 months from the first to the
last. Both months must be ones the series holds, and the first must not come
after the last. Either mistake stops the call with a message rather than
returning an average over months nobody asked for.

The parse uses the standard library's ``csv`` rather than pandas, because a
series of 1,112 numbers needs no frame.
"""

from __future__ import annotations

import csv
import io
import re
from decimal import Decimal
from pathlib import Path

from chan.vintage import VintageEntry, read_vintage, resolve_vintage

#: The identity fields that name the series in ``data/vintages.jsonl``.
VENDOR = "fred"
SYMBOL = "TB3MS"
PRICE_BASIS = "rate"

#: The one header a recorded vintage carries. In a ``rate`` vintage the
#: ``Close`` column holds the rate, because the recorder writes one header for
#: every series.
HEADER = ["Date", "Close"]

_FIRST_OF_MONTH = re.compile(r"\d{4}-\d{2}-01")


def bill_vintage(*, data_dir: Path | None = None) -> VintageEntry:
    """The manifest entry for the committed bill series.

    Resolved by identity rather than by filename, so a second download of
    TB3MS makes this refuse and name both rather than pick one.
    """
    return resolve_vintage(vendor=VENDOR, symbol=SYMBOL, price_basis=PRICE_BASIS, data_dir=data_dir)


def monthly_rates(*, data_dir: Path | None = None) -> list[tuple[str, float]]:
    """Every month the series holds, as ``(YYYY-MM, decimal rate a year)`` pairs, oldest first.

    The bytes are read only after they hash to what the manifest records. The
    header must be ``Date,Close``, every date must be the first of a month, and
    each month must follow the one before it. A gap would shrink a window's
    month count without any message, so it stops the read instead.
    """
    entry = bill_vintage(data_dir=data_dir)
    text = read_vintage(entry, data_dir=data_dir).decode("utf-8")
    reader = csv.reader(io.StringIO(text))
    header = next(reader, None)
    if header != HEADER:
        raise ValueError(
            f"{entry.path}: the header reads {header!r} and a recorded vintage carries "
            f"{HEADER!r}, so the columns cannot be trusted to be a date and a rate"
        )

    rates: list[tuple[str, float]] = []
    for line, (day, percent) in enumerate(reader, start=2):
        if not _FIRST_OF_MONTH.fullmatch(day):
            raise ValueError(
                f"{entry.path}: line {line} is dated {day!r}, and each row of a monthly series "
                f"is dated the first of its month"
            )
        month = day[:7]
        if rates and month != _next_month(rates[-1][0]):
            raise ValueError(
                f"{entry.path}: line {line} holds {month} straight after {rates[-1][0]}, and "
                f"the series is read as one row for every calendar month"
            )
        rates.append((month, float(Decimal(percent) / 100)))
    return rates


def average(first_month: str, last_month: str, *, data_dir: Path | None = None) -> float:
    """The mean monthly rate over the window, both ends included, as a decimal a year.

    Each month counts once, whatever its number of trading days, because each
    row is already that month's average.
    """
    window = _window(first_month, last_month, data_dir)
    return sum(window) / len(window)


def months_in(first_month: str, last_month: str, *, data_dir: Path | None = None) -> int:
    """How many months the window holds, both ends included."""
    return len(_window(first_month, last_month, data_dir))


def months_below(
    threshold: float, first_month: str, last_month: str, *, data_dir: Path | None = None
) -> int:
    """How many months in the window had a rate strictly below ``threshold``, a decimal a year.

    Strictly, so a month at exactly the threshold is not counted. TB3MS prints
    at most two decimal places of a percent, so a threshold of 0.0025 counts
    months at 0.24% and below.
    """
    return sum(1 for rate in _window(first_month, last_month, data_dir) if rate < threshold)


def _window(first_month: str, last_month: str, data_dir: Path | None) -> list[float]:
    """The rates from ``first_month`` to ``last_month``, both included, or a refusal."""
    rates = monthly_rates(data_dir=data_dir)
    held = {month for month, _ in rates}
    for label, month in (("first", first_month), ("last", last_month)):
        if month not in held:
            raise ValueError(
                f"the {label} month {month!r} is not one the bill series holds. It runs from "
                f"{rates[0][0]} to {rates[-1][0]}, one YYYY-MM per month"
            )
    if last_month < first_month:
        raise ValueError(
            f"the window runs backwards, from {first_month} to {last_month}. Name the earlier "
            f"month first"
        )
    return [rate for month, rate in rates if first_month <= month <= last_month]


def _next_month(month: str) -> str:
    """The ``YYYY-MM`` after ``month``."""
    year, number = int(month[:4]), int(month[5:])
    return f"{year + 1:04d}-01" if number == 12 else f"{year:04d}-{number + 1:02d}"
