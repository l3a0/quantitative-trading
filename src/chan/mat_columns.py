"""Record the closes in one of Ernest Chan's MATLAB files as one vintage per stock.

Chan's cross-sectional examples read two files from his first-edition code: the
S&P 500 as it stood on 2007-11-23 and the S&P 600 as it stood on 2008-01-14.
Each holds a date-by-stock array of closes, and
[issue 88](https://github.com/l3a0/quantitative-trading/issues/88) decided that
such a file is recorded as one ordinary vintage per stock rather than as one
file of a new shape.

This module is the half that needs scipy. It reads the ``.mat`` bytes, turns
each column into rows, and hands them to
:func:`chan.vintage.record_lifted_columns`, which owns the write order, the
refusals and the rollback and stays on the standard library.

Three choices are settled here rather than left to whoever runs it.

1. **Closes only.** Each file carries ``op``, ``hi``, ``lo`` and ``vol`` beside
   ``cl``, and every figure Chan's code prints from these two files reads
   ``cl`` alone. An open series per stock would share every identity field
   with that stock's closes, so the owner decided on 2026-10-02 to record
   closes and nothing else.
   [Issue 206](https://github.com/l3a0/quantitative-trading/issues/206) holds
   the one step that would need opens.
2. **A missing cell is a missing row.** Chan marks a day a stock has no price
   with NaN, and a vintage refuses one. Dropping those cells loses nothing,
   because no day in either file lacks a close in every column, so the union
   of the members' dates is the file's own day list and
   :func:`chan.series.load_panel` rebuilds every NaN by reindexing onto it.
   :func:`round_trip_differs` is the check that says so for the file at hand.
3. **The saved date is the header's.** A MAT file's 116-byte text header
   records when it was created, and that is the date the vintage carries. It
   is a day after the date in each file's name, because the name carries the
   last trading day and the header carries the save.

The price basis is the caller's to state, because nothing in the file says
it. ``data/README.md`` records what was measured for each file and why it is
recorded as ``adjusted``.

Run it as ``python -m chan.mat_columns <file.mat> --price-basis adjusted``. The
files are not committed, so a run needs a local copy taken from the mirror at
the commit ``data/README.md`` names.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import re
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import scipy.io

from chan.vintage import (
    PRICE_BASES,
    VintageEntry,
    VintageRefused,
    record_lifted_columns,
)

#: The vendor every column lifted from one of Chan's MATLAB files is recorded under.
#:
#: Not ``chan-xls``, which his workbook columns carry. KO and PEP are in the S&P
#: 500 file and already committed from his workbooks, so one vendor for both
#: would make ``load_vintage("KO", chan=True)`` match two entries and stop the
#: KO/PEP replication.
VENDOR = "chan-mat"

_CREATED = re.compile(rb"Created on: +([A-Z][a-z]{2} [A-Z][a-z]{2} +\d{1,2} [\d:]{8} \d{4})")


def saved_date_of(payload: bytes) -> str:
    """The ISO date a MAT file's header says it was created, or a refusal saying why not.

    Read from the text header rather than from a filesystem timestamp, which a
    copy or an unzip rewrites. The header is part of the bytes, so the date is
    as fixed as the file.
    """
    header = payload[:116]
    if not header.startswith(b"MATLAB 5.0 MAT-file"):
        raise ValueError(
            "the file does not open with a MATLAB 5.0 header, so it is not the format "
            "scipy.io.loadmat reads and carries no creation date to record"
        )
    found = _CREATED.search(header)
    if found is None:
        raise ValueError(f"the MAT header carries no creation date: {header!r}")
    created = " ".join(found.group(1).decode("ascii").split())
    return datetime.strptime(created, "%a %b %d %H:%M:%S %Y").date().isoformat()


def read_closes(payload: bytes) -> tuple[list[str], list[str], np.ndarray]:
    """The file's trading days as ISO dates, its symbols, and its date-by-symbol closes.

    The three arrays are checked against each other before anything is
    returned, because a mismatch here would put one stock's closes under
    another's name with every hash verifying.
    """
    held = scipy.io.loadmat(io.BytesIO(payload), variable_names=["tday", "stocks", "cl"])
    missing = sorted({"tday", "stocks", "cl"} - held.keys())
    if missing:
        raise ValueError(f"the file carries no {', '.join(missing)}")

    days = [_iso_day(day) for day in np.asarray(held["tday"]).ravel()]
    if days != sorted(set(days)):
        raise ValueError("the file's trading days are not strictly increasing")
    symbols = [_symbol(cell) for cell in np.asarray(held["stocks"]).ravel()]
    repeated = sorted({symbol for symbol in symbols if symbols.count(symbol) > 1})
    if repeated:
        raise ValueError(f"the file names a symbol more than once: {', '.join(repeated)}")

    closes = np.asarray(held["cl"], dtype=float)
    if closes.shape != (len(days), len(symbols)):
        raise ValueError(
            f"cl is {closes.shape[0]} by {closes.shape[1]} and the file carries "
            f"{len(days)} days and {len(symbols)} symbols"
        )
    return days, symbols, closes


def columns_of(
    days: list[str], symbols: list[str], closes: np.ndarray
) -> dict[str, list[tuple[str, float]]]:
    """Each symbol's rows, holding only the days the file prices it on."""
    columns = {}
    for index, symbol in enumerate(symbols):
        priced = np.isfinite(closes[:, index])
        columns[symbol] = [(days[day], float(closes[day, index])) for day in np.flatnonzero(priced)]
    return columns


def record_mat_closes(
    path: Path, *, price_basis: str, data_dir: Path | None = None
) -> list[VintageEntry]:
    """Record every close column in ``path`` as its own vintage, under :data:`VENDOR`."""
    payload = Path(path).read_bytes()
    days, symbols, closes = read_closes(payload)
    return record_lifted_columns(
        columns_of(days, symbols, closes),
        vendor=VENDOR,
        price_basis=price_basis,
        saved_date=saved_date_of(payload),
        source_file=Path(path).name,
        data_dir=data_dir,
    )


def round_trip_differs(path: Path, *, data_dir: Path | None = None) -> str | None:
    """Why the recorded panel is not the file's ``cl`` array, or ``None`` when it is.

    The panel is rebuilt by :func:`chan.series.load_panel` from the committed
    bytes alone, so this is the check that dropping the NaN cells lost nothing.
    It needs the ``.mat``, which is not committed, so it runs where the file was
    recorded, the way the TLT and IEF column check ran at download time.
    """
    from chan.series import load_panel

    payload = Path(path).read_bytes()
    days, symbols, closes = read_closes(payload)
    _, panel = load_panel(Path(path).name, data_dir=data_dir)

    if [str(day.date()) for day in panel.index] != days:
        return "the panel's days are not the file's trading days"
    if list(panel.columns) != sorted(symbols):
        return "the panel's symbols are not the file's"
    order = [symbols.index(symbol) for symbol in panel.columns]
    if not np.array_equal(panel.to_numpy(dtype=float), closes[:, order], equal_nan=True):
        return "the panel's closes are not the file's cl array"
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m chan.mat_columns",
        description="Record the closes in one of Chan's .mat files as one vintage per stock.",
    )
    parser.add_argument("path", type=Path, help="a local copy of the .mat file")
    parser.add_argument("--price-basis", required=True, choices=PRICE_BASES)
    arguments = parser.parse_args(argv)

    sha256 = hashlib.sha256(arguments.path.read_bytes()).hexdigest()
    try:
        entries = record_mat_closes(arguments.path, price_basis=arguments.price_basis)
    except (VintageRefused, ValueError) as refused:
        print(f"{arguments.path.name}: not recorded. {refused}", file=sys.stderr)
        return 1

    rows = sum(entry.row_count for entry in entries)
    print(f"{arguments.path.name}   sha256 {sha256}")
    print(
        f"recorded {len(entries)} vintages, {rows} closes, under "
        f"{entries[0].path.split('/')[0]}/, saved {entries[0].saved_date}"
    )
    differs = round_trip_differs(arguments.path)
    if differs is not None:
        print(f"round trip failed: {differs}", file=sys.stderr)
        return 1
    print("round trip: the panel read back is the file's cl array, NaN for NaN")
    return 0


def _iso_day(day: object) -> str:
    """A ``yyyymmdd`` integer as an ISO date, refusing anything that is not one."""
    text = str(int(day))
    return datetime.strptime(text, "%Y%m%d").date().isoformat()


def _symbol(cell: object) -> str:
    """One entry of MATLAB's cell array of strings, as the string it holds."""
    held = np.asarray(cell).ravel()
    if held.size != 1:
        raise ValueError(f"a symbol cell holds {held.size} values rather than one")
    return str(held[0]).strip()


if __name__ == "__main__":
    sys.exit(main())
