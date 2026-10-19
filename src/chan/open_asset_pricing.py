"""Read the Open Source Asset Pricing project's long-short returns for five signals.

Andrew Chen and Tom Zimmermann rebuild published stock-return predictors from
CRSP and publish the monthly returns of portfolios sorted on each one. Their
paper is "Open Source Cross-Sectional Asset Pricing", *Critical Finance
Review*, 2022, and the project asks anyone using the data to cite it. Five of
its signals match strategies this repo reproduced from Chan's books, and
[issue 660](https://github.com/l3a0/quantitative-trading/issues/660) committed
their long-short returns so the comparisons that read them read bytes somebody
kept. The project ships a new release most years, and a later release can
restate an earlier month, which is why the release is part of the vendor.

Each signal is one ``return`` vintage, holding the long-short rows of the
release's ``PredictorPortsFull.csv`` byte for byte under that file's own
header. [data/README.md](../../data/README.md) names the download, the source
file's sha256 and each signal's construction. In short, ``ret`` is the
long-short portfolio's return in percent a month, dated the last trading day of
the month, and ``Nlong`` and ``Nshort`` count the stocks on each side.

The returns come back in percent a month, as the file writes them, because
dividing by 100 here would move the last digit of every value away from the
text a reader can check against the file. Turning them into decimals belongs
to the caller, where the arithmetic is the strategy's.

The bytes are read only once they hash to the manifest's line, which
:func:`chan.vintage.read_vintage` decides. Every row is then checked to be the
asked signal's long-short row, because a file holding another signal's rows
under the right hash is a manifest line written against the wrong file, and a
comparison computed from it would read as the right one.
"""

from __future__ import annotations

import csv
import io
import math
import re
from pathlib import Path

import pandas as pd

from chan.vintage import VintageEntry, VintageUnavailable, read_vintage, resolve_vintage

#: The release, as the ``openassetpricing`` package names it in ``OpenAP(202510)``.
RELEASE = "202510"

#: The vendor field of every line, carrying the release so a later one is a different vintage.
VENDOR = f"openassetpricing-{RELEASE}"
PRICE_BASIS = "return"

#: The signals committed, in the order the issue lists them.
SIGNALS = ("MomSeasonShort", "Mom12m", "STreversal", "BetaFP", "AnnouncementReturn")

#: The header of ``PredictorPortsFull.csv``, which every committed file keeps.
HEADER = ("signalname", "port", "date", "ret", "signallag", "Nlong", "Nshort")

#: The ``port`` value of the long-short row, as the project writes it.
LONG_SHORT = "LS"

_ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def long_short_symbol(signal: str) -> str:
    """The manifest's symbol for a signal's long-short series, such as ``MOMSEASONSHORT-LS``.

    Upper case because the manifest refuses any other spelling of a symbol, and
    suffixed so a later file of the same signal's deciles is a different series.
    """
    if signal not in SIGNALS:
        raise ValueError(
            f"{signal!r} is not a committed signal. The committed ones are {', '.join(SIGNALS)}, "
            f"spelled as the project spells them"
        )
    return f"{signal.upper()}-{LONG_SHORT}"


def long_short_vintage(signal: str, *, data_dir: Path | None = None) -> VintageEntry:
    """The manifest entry holding ``signal``'s long-short returns from release :data:`RELEASE`."""
    return resolve_vintage(
        vendor=VENDOR,
        symbol=long_short_symbol(signal),
        price_basis=PRICE_BASIS,
        data_dir=data_dir,
    )


def long_short_returns(
    signal: str, *, data_dir: Path | None = None
) -> tuple[VintageEntry, pd.Series]:
    """``signal``'s monthly long-short returns, in percent a month, indexed by date.

    The index is each row's date as the file writes it, the last trading day of
    the month. A file whose header is not the source's, or holding a row that is
    not this signal's long-short row, or holding dates out of order or a return
    that is not a finite number, stops the read and names its path and line.
    """
    entry = long_short_vintage(signal, data_dir=data_dir)
    reader = csv.reader(io.StringIO(read_vintage(entry, data_dir=data_dir).decode("utf-8")))
    header = tuple(next(reader, ()))
    if header != HEADER:
        raise VintageUnavailable(
            f"{entry.path}: the header reads {','.join(header)!r} where the release's "
            f"PredictorPortsFull.csv writes {','.join(HEADER)!r}, so its columns cannot be "
            f"trusted to be what the names say"
        )

    days: list[str] = []
    returns: list[float] = []
    for line, row in enumerate(reader, start=2):
        if len(row) != len(HEADER):
            raise VintageUnavailable(
                f"{entry.path}: line {line} holds {len(row)} cells where the header names "
                f"{len(HEADER)}"
            )
        name, port, day, percent = row[0], row[1], row[2], row[3]
        if (name, port) != (signal, LONG_SHORT):
            raise VintageUnavailable(
                f"{entry.path}: line {line} is the {port!r} row of {name!r}, and the file is "
                f"recorded as the {LONG_SHORT!r} rows of {signal!r}"
            )
        if not _ISO_DATE.fullmatch(day) or (days and day <= days[-1]):
            raise VintageUnavailable(
                f"{entry.path}: line {line} is dated {day!r}, and each row is one month dated "
                f"YYYY-MM-DD, later than the row before it"
            )
        value = _finite(percent)
        if value is None:
            raise VintageUnavailable(
                f"{entry.path}: line {line} holds the return {percent!r}, which is not a "
                f"finite number"
            )
        days.append(day)
        returns.append(value)

    if not days:
        raise VintageUnavailable(f"{entry.path}: the file holds a header and no rows")
    series = pd.Series(
        returns,
        index=pd.DatetimeIndex(days, name="date"),
        name=f"{signal} long-short, percent a month",
    )
    return entry, series


def _finite(text: str) -> float | None:
    """The float ``text`` spells, or ``None`` when it is not a finite number."""
    try:
        value = float(text)
    except ValueError:
        return None
    return value if math.isfinite(value) else None
