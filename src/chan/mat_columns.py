"""Record one of Ernest Chan's MATLAB files as one vintage per stock, every field kept.

Chan's cross-sectional examples read four price files. Three come from his
first-edition code: the S&P 500 as it stood on 2007-11-23, and the S&P 600 in
two saves named for 2008-01-14 and 2008-01-31. The fourth comes from his second
book's code: the S&P 500 as he held it on 2012-04-24, which his Examples 7.2
and 6.2 read. Each holds
date-by-stock arrays of closes, highs, lows, opens and volumes, and
[issue 88](https://github.com/l3a0/quantitative-trading/issues/88) decided that
such a file is recorded as one ordinary vintage per stock rather than as one
file of a new shape.

Example 7.2 also reads a fifth file, ``earnannFile.mat``, which holds no
prices. It is a date-by-stock array of 0 and 1 marking the days a stock
announced earnings between the previous close and the open.
[Issue 250](https://github.com/l3a0/quantitative-trading/issues/250) decided it
is recorded the same way, one vintage per stock, under the ``event`` basis and
the one field :data:`chan.vintage.EVENT_FIELDS` names. :func:`record_flag_file`
records it and :func:`flag_round_trip_differs` checks it.

This module is the half that needs scipy. It reads the ``.mat`` bytes, turns
each stock into rows, and hands them to
:func:`chan.vintage.record_lifted_columns`, which owns the write order, the
refusals and the rollback and stays on the standard library.

Three choices are settled here rather than left to whoever runs it.

1. **Every field is kept.** The owner decided on 2026-10-02 to record all five
   arrays rather than the closes alone. The closes are what Chan's printed
   figures read, and the other four exist only in the public mirror the files
   came from, which this repo does not control, so a vintage holding only the
   close would leave them to that mirror. Each stock's file holds all five, which
   keeps a stock one vintage. An open series recorded as a vintage of its own
   would share every identity field with the close.
2. **A missing cell is a missing row.** Chan marks a day a stock has no price
   with NaN in every field at once, and a vintage refuses one. Dropping those
   rows loses nothing, because no day in any of the four lacks a close in
   every column, so the union of the members' dates is the file's own day list and
   :func:`chan.series.load_panel` rebuilds every NaN by reindexing onto it.
   :func:`round_trip_differs` is the check that says so, field by field, for
   the file at hand. A flag file is the exception, and keeps every day of its
   calendar with a 0 where nothing happened, because Example 7.2 cuts its
   prices to the flag file's own days. A flag file whose rows began at its
   first announcement would start that calendar late.
3. **The saved date is the header's.** A MAT file's 116-byte text header
   records when it was created, and that is the date the vintage carries. For
   the first three files recorded it is a day after the date in the file's
   name, because the name carries the last trading day and the header carries
   the save. ``IJR_20080131.mat`` is the exception: its name says 2008-01-31,
   its last row is 2008-02-01 and its header says 2008-02-02.

The price basis is the caller's to state, because nothing in the file says
it, and it names the four prices. ``data/README.md`` records what was measured
for each file and why it is recorded as ``adjusted``. A basis of ``event``
records a flag file instead.

Run it as ``python -m chan.mat_columns <file.mat> --price-basis adjusted``, or
``--price-basis event`` for a flag file. The files are not committed, so a run
needs a local copy taken from the source and commit ``data/README.md`` names
for that file.
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
    EVENT_FIELDS,
    LIFTED_FIELDS,
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


#: Each field a lifted file carries, to the array in Chan's file that holds it.
ARRAYS = {"Close": "cl", "High": "hi", "Low": "lo", "Open": "op", "Volume": "vol"}


def read_arrays(payload: bytes) -> tuple[list[str], list[str], dict[str, np.ndarray]]:
    """The file's trading days as ISO dates, its symbols, and each field's array.

    The arrays are checked against the days and the symbols before anything is
    returned, because a mismatch here would put one stock's prices under
    another's name with every hash verifying.
    """
    wanted = ["tday", "stocks", *ARRAYS.values()]
    held = scipy.io.loadmat(io.BytesIO(payload), variable_names=wanted)
    missing = [name for name in wanted if name not in held]
    if missing:
        raise ValueError(f"the file carries no {', '.join(missing)}")

    days = [_iso_day(day) for day in np.asarray(held["tday"]).ravel()]
    if days != sorted(set(days)):
        raise ValueError("the file's trading days are not strictly increasing")
    symbols = [_symbol(cell) for cell in np.asarray(held["stocks"]).ravel()]
    repeated = sorted({symbol for symbol in symbols if symbols.count(symbol) > 1})
    if repeated:
        raise ValueError(f"the file names a symbol more than once: {', '.join(repeated)}")

    arrays = {}
    for field, name in ARRAYS.items():
        array = np.asarray(held[name], dtype=float)
        if array.shape != (len(days), len(symbols)):
            raise ValueError(
                f"{name} is {array.shape[0]} by {array.shape[1]} and the file carries "
                f"{len(days)} days and {len(symbols)} symbols"
            )
        arrays[field] = array
    return days, symbols, arrays


def columns_of(
    days: list[str], symbols: list[str], arrays: dict[str, np.ndarray]
) -> dict[str, list[tuple]]:
    """Each symbol's rows, one per day the file prices it, carrying every field.

    A day is priced when its close is. Every other field must be present on
    exactly those days, because a row cannot hold a missing open and a day
    with an open and no close has nowhere to go. Chan's first two files hold
    that, measured on issue 88, and so does his book-two file, measured on
    issue 250. A file that does not is refused naming the
    first stock and day that break it.
    """
    closes = arrays["Close"]
    columns = {}
    for index, symbol in enumerate(symbols):
        priced = np.isfinite(closes[:, index])
        for field in LIFTED_FIELDS[1:]:
            held = np.isfinite(arrays[field][:, index])
            if not np.array_equal(held, priced):
                day = days[int(np.flatnonzero(held != priced)[0])]
                raise ValueError(
                    f"{symbol}'s {field} and close disagree on whether {day} was priced, so "
                    f"no row can hold that day"
                )
        columns[symbol] = [
            (days[day], *(float(arrays[field][day, index]) for field in LIFTED_FIELDS))
            for day in np.flatnonzero(priced)
        ]
    return columns


def record_mat_file(
    path: Path, *, price_basis: str, data_dir: Path | None = None
) -> list[VintageEntry]:
    """Record every stock in ``path`` as its own vintage, under :data:`VENDOR`.

    A file holding a day with no close in any column is refused before
    anything is written. The panel rebuilds a file's days from the union of
    its members' dates, so such a day would vanish from it, and
    :func:`round_trip_differs` would only say so once every member had been
    recorded.
    """
    payload = Path(path).read_bytes()
    days, symbols, arrays = read_arrays(payload)
    unpriced = [
        day for day, row in zip(days, arrays["Close"], strict=True) if not np.isfinite(row).any()
    ]
    if unpriced:
        raise ValueError(
            f"{Path(path).name} prices no column on {', '.join(unpriced)}, so the per-stock "
            f"files could not give that day back"
        )
    return record_lifted_columns(
        columns_of(days, symbols, arrays),
        vendor=VENDOR,
        price_basis=price_basis,
        saved_date=saved_date_of(payload),
        source_file=Path(path).name,
        fields=LIFTED_FIELDS,
        data_dir=data_dir,
    )


def round_trip_differs(path: Path, *, data_dir: Path | None = None) -> str | None:
    """Why the recorded panels are not the file's arrays, or ``None`` when they are.

    Each field's panel is rebuilt by :func:`chan.series.load_panel` from the
    committed bytes alone, so this is the check that dropping the NaN rows lost
    nothing. It needs the ``.mat``, which is not committed, so it runs where the
    file was recorded, the way the TLT and IEF column check ran at download
    time.

    The comparison is exact, and so is the parse it compares. ``_parse_close``
    once landed a long value one unit in its last digit away from the one
    written, which
    [issue 211](https://github.com/l3a0/quantitative-trading/issues/211)
    fixed. Before that a file of full-precision prices was reported as differing
    although its bytes were right. Chan's book-two price file was one, at 170
    closes and 173 opens, measured on
    [issue 20](https://github.com/l3a0/quantitative-trading/issues/20).
    """
    from chan.series import load_panel

    payload = Path(path).read_bytes()
    days, symbols, arrays = read_arrays(payload)
    spelled = [symbol.upper() for symbol in symbols]
    for field in LIFTED_FIELDS:
        _, panel = load_panel(Path(path).name, field=field, data_dir=data_dir)
        if [str(day.date()) for day in panel.index] != days:
            return "the panel's days are not the file's trading days"
        if list(panel.columns) != sorted(spelled):
            return "the panel's symbols are not the file's"
        order = [spelled.index(symbol) for symbol in panel.columns]
        if not np.array_equal(panel.to_numpy(dtype=float), arrays[field][:, order], equal_nan=True):
            return f"the panel's {field} is not the file's {ARRAYS[field]} array"
    return None


def read_flags(payload: bytes) -> tuple[list[str], list[str], np.ndarray]:
    """A flag file's days as ISO dates, its symbols, and its 0 and 1 array.

    Checked the way :func:`read_arrays` checks a price file, and every cell must
    be 0 or 1, because a flag file with anything else in it is not one.
    """
    wanted = ["tday", "stocks", "earnann"]
    held = scipy.io.loadmat(io.BytesIO(payload), variable_names=wanted)
    missing = [name for name in wanted if name not in held]
    if missing:
        raise ValueError(f"the file carries no {', '.join(missing)}")

    days = [_iso_day(day) for day in np.asarray(held["tday"]).ravel()]
    if days != sorted(set(days)):
        raise ValueError("the file's trading days are not strictly increasing")
    symbols = [_symbol(cell) for cell in np.asarray(held["stocks"]).ravel()]
    repeated = sorted({symbol for symbol in symbols if symbols.count(symbol) > 1})
    if repeated:
        raise ValueError(f"the file names a symbol more than once: {', '.join(repeated)}")

    flags = np.asarray(held["earnann"])
    if flags.shape != (len(days), len(symbols)):
        raise ValueError(
            f"earnann is {flags.shape[0]} by {flags.shape[1]} and the file carries "
            f"{len(days)} days and {len(symbols)} symbols"
        )
    if not np.isin(flags, (0, 1)).all():
        raise ValueError("earnann holds a value other than 0 and 1")
    return days, symbols, flags.astype(int)


def record_flag_file(path: Path, *, data_dir: Path | None = None) -> list[VintageEntry]:
    """Record every stock in a flag file as its own ``event`` vintage, under :data:`VENDOR`.

    Each stock keeps every day of the file's calendar, a 0 included, so the
    vintage's span is the calendar's rather than its first announcement's.
    """
    payload = Path(path).read_bytes()
    days, symbols, flags = read_flags(payload)
    columns = {
        symbol: [(day, int(flag)) for day, flag in zip(days, flags[:, index], strict=True)]
        for index, symbol in enumerate(symbols)
    }
    return record_lifted_columns(
        columns,
        vendor=VENDOR,
        price_basis="event",
        saved_date=saved_date_of(payload),
        source_file=Path(path).name,
        fields=EVENT_FIELDS,
        data_dir=data_dir,
    )


def flag_round_trip_differs(path: Path, *, data_dir: Path | None = None) -> str | None:
    """Why the recorded flags are not the file's array, or ``None`` when they are.

    :func:`round_trip_differs` cannot read a flag file, because
    :func:`read_arrays` asks for five price arrays it does not carry. This
    rebuilds the array from the committed bytes through
    :func:`chan.series.load_panel` and compares it cell for cell, days and
    symbol order included.
    """
    from chan.series import load_panel

    payload = Path(path).read_bytes()
    days, symbols, flags = read_flags(payload)
    spelled = [symbol.upper() for symbol in symbols]
    _, panel = load_panel(Path(path).name, field=EVENT_FIELDS[0], data_dir=data_dir)
    if [str(day.date()) for day in panel.index] != days:
        return "the panel's days are not the file's trading days"
    if list(panel.columns) != sorted(spelled):
        return "the panel's symbols are not the file's"
    order = [spelled.index(symbol) for symbol in panel.columns]
    if not np.array_equal(panel.to_numpy(dtype=float), flags[:, order].astype(float)):
        return "the panel's flags are not the file's earnann array"
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m chan.mat_columns",
        description="Record one of Chan's .mat files as one vintage per stock.",
    )
    parser.add_argument("path", type=Path, help="a local copy of the .mat file")
    parser.add_argument("--price-basis", required=True, choices=PRICE_BASES)
    arguments = parser.parse_args(argv)

    sha256 = hashlib.sha256(arguments.path.read_bytes()).hexdigest()
    flags = arguments.price_basis == "event"
    try:
        if flags:
            entries = record_flag_file(arguments.path)
        else:
            entries = record_mat_file(arguments.path, price_basis=arguments.price_basis)
    except (VintageRefused, ValueError) as refused:
        print(f"{arguments.path.name}: not recorded. {refused}", file=sys.stderr)
        return 1

    rows = sum(entry.row_count for entry in entries)
    fields = EVENT_FIELDS if flags else LIFTED_FIELDS
    print(f"{arguments.path.name}   sha256 {sha256}")
    print(
        f"recorded {len(entries)} vintages, {rows} rows of {', '.join(fields)}, under "
        f"{entries[0].path.split('/')[0]}/, saved {entries[0].saved_date}"
    )
    differs = (flag_round_trip_differs if flags else round_trip_differs)(arguments.path)
    if differs is not None:
        print(
            f"round trip failed: {differs}. The vintages are recorded, so review them before "
            f"committing, or take them back out with `git checkout -- data/` and by removing "
            f"{entries[0].path.split('/')[0]}/.",
            file=sys.stderr,
        )
        return 1
    if flags:
        print("round trip: every flag read back is the file's array, day for day")
    else:
        print("round trip: every field read back is the file's array, NaN for NaN")
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
