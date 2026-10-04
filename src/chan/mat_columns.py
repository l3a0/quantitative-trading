"""Record one of Ernest Chan's MATLAB or CSV files as one vintage per column.

Chan's examples read five price files of this shape. Three come from his
first-edition code: the S&P 500 as it stood on 2007-11-23, and the S&P 600 in
two saves named for 2008-01-14 and 2008-01-31. Two come from his second book's
code: the S&P 500 as he held it on 2012-04-24, which his Examples 7.2, 6.2 and
4.1 read, and ``inputData_ETF.mat``, 67 ETFs saved on 2012-04-10, which most
of the book's ETF experiments not yet run here read. Each holds date-by-symbol
arrays of closes, highs, lows, opens and volumes, and
[issue 88](https://github.com/l3a0/quantitative-trading/issues/88) decided that
such a file is recorded as one ordinary vintage per stock rather than as one
file of a new shape. The ETF file is recorded the same way, one vintage per
ETF, and names its list of symbols ``syms`` where the others say ``stocks``.

Example 7.2 also reads a sixth file, ``earnannFile.mat``, which holds no
prices. It is a date-by-stock array of 0 and 1 marking the days a stock
announced earnings between the previous close and the open.
[Issue 250](https://github.com/l3a0/quantitative-trading/issues/250) decided it
is recorded the same way, one vintage per stock, under the ``event`` basis and
the one field :data:`chan.vintage.EVENT_FIELDS` names. :func:`record_flag_file`
records it and :func:`flag_round_trip_differs` checks it.

Chan's second book also reads eight futures strips, each a date-by-contract
array of settlements named ``inputDataDaily_<root>_<date>.mat``, and one gold
series sampled at 16:00, ``inputData_GC_1600_20100802.mat``.
[Issue 300](https://github.com/l3a0/quantitative-trading/issues/300) decided
that each contract is one vintage holding the close alone, because the file
holds nothing else, under a symbol joining the file's root and the contract,
such as ``CL-2007F``. The root is needed because six strips share a saved date,
so a bare ``2007Z`` would name six vintages no reader argument could separate.
Chan's spot column, ``0000$``, becomes ``<root>-SPOT``. The gold file holds no
contract names, so it is read as a strip of one column named for its root.
:func:`record_strip_file` records either and :func:`strip_round_trip_differs`
checks it.

Its futures examples also read four saves of a continuous futures file,
``inputDataOHLCDaily_2012*.mat``, where each symbol is one series rolled from
contract to contract and shifted at each roll.
[Issue 313](https://github.com/l3a0/quantitative-trading/issues/313) records
each symbol as one vintage with all five fields, as a stock is. Its ``tday``
is a date-by-symbol array, so every symbol keeps its own calendar.
:func:`read_continuous` reads one, :func:`record_continuous_file` records it,
and :func:`continuous_round_trip_differs` checks it member by member, because
the union of the members' days is not this file's layout. Two of those
examples also read ``VIX.csv``, which :func:`record_csv_file` records under
:data:`CSV_VENDOR` and :func:`csv_round_trip_differs` checks.

This module is the half that needs scipy, though its CSV route does not. It
reads the ``.mat`` bytes, turns
each column into rows, and hands them to
:func:`chan.vintage.record_lifted_columns`, which owns the write order, the
refusals and the rollback and stays on the standard library.

Three choices are settled here for the stock files rather than left to whoever
runs it.

1. **Every field is kept.** The owner decided on 2026-10-02 to record all five
   arrays rather than the closes alone. The closes are what Chan's printed
   figures read, and the other four exist only in the public mirror the files
   came from, which this repo does not control, so a vintage holding only the
   close would leave them to that mirror. Each stock's file holds all five, which
   keeps a stock one vintage. An open series recorded as a vintage of its own
   would share every identity field with the close.
2. **A missing cell is a missing row.** Chan marks a day a stock has no price
   with NaN in every field at once, and a vintage refuses one. Dropping those
   rows loses nothing, because no day in any of the five lacks a close in
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

The price basis is the caller's to state for a stock file, because nothing in
the file says it, and it names the four prices. ``data/README.md`` records what
was measured for each file and why it is recorded as ``adjusted``. A strip
takes ``raw`` and nothing else, because a contract's settlement is the price it
traded at and nothing adjusts it. A flag file takes ``event`` and nothing else.
A continuous futures save takes a price basis the way a stock file does, and
its saves are recorded as ``adjusted`` because each is back-adjusted at every
roll. ``VIX.csv`` is recorded as ``raw``, because an index level as published
has nothing to adjust.

Run it as ``python -m chan.mat_columns <file.mat> --price-basis adjusted``,
``--price-basis raw`` for a strip, or ``--price-basis event`` for a flag file.
A ``.csv`` also takes ``--saved-date YYYY-MM-DD``, because it carries no header
recording one. The command picks a ``.mat`` file's reader by the variables it
carries rather than by the basis, and :func:`shape_of` says how. A ``.csv`` is
picked by its suffix. The files are not committed, so a
run needs a local copy taken from the source and commit ``data/README.md``
names for that file.
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

#: The vendor a series lifted from one of Chan's own CSV files is recorded under.
#:
#: A third spelling beside ``chan-xls`` and :data:`VENDOR`, naming the kind of
#: file he shipped. ``VIX.csv`` is the one so far. It is not ``chan-py``, which
#: [issue 301](https://github.com/l3a0/quantitative-trading/issues/301) gives
#: the members of his 2018 Python port, because the mirror's ``VIX.csv`` is its
#: own source and the port contributes only its date.
CSV_VENDOR = "chan-csv"

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

#: The names Chan's files give their list of symbols. His stock files say
#: ``stocks``, and his book-two ETF file, ``inputData_ETF.mat``, says ``syms``.
#: A file holds exactly one of them.
SYMBOL_NAMES = ("stocks", "syms")


#: Maps a source's sha256 to its unnamed columns, each given by its position,
#: counting from one, and the symbol it is recorded under.
#:
#: The 2012-05-07 save of Chan's continuous futures holds 53 columns and the
#: sixth has an empty name. Its closes equal the 2012-05-11 save's ``C`` on
#: every day the two share, while the same save's own ``C`` is a different
#: series. The owner decided on 2026-10-04, on
#: [issue 313](https://github.com/l3a0/quantitative-trading/issues/313), to keep
#: it under a name built from its position rather than drop it, because that
#: name claims nothing the file does not say. It is keyed by the hash rather
#: than the file name, because the ruling was about those bytes, and any other
#: empty name is refused.
UNNAMED_COLUMNS = {
    "3cc01a9623031df25aa45abfc2201869d7a1288c018d8a46e62f7cad1fe72892": {6: "COLUMN-6"},
}


def symbols_of(held: dict[str, np.ndarray], *, unnamed: dict[int, str] | None = None) -> list[str]:
    """The symbols in a loaded file, read from whichever of :data:`SYMBOL_NAMES` it holds.

    ``held`` is what ``scipy.io.loadmat`` returned when asked for every name in
    :data:`SYMBOL_NAMES`, so any reader of Chan's files can take its symbols
    from here whatever shape its other arrays have. A file holding both names or
    neither is refused, because guessing would put one list's names on the
    other's columns, and so is a file naming a symbol twice.

    A column with an empty or blank name is refused by its position, counting
    from one, unless ``unnamed`` gives that position a name. A reader passes
    the ruling :data:`UNNAMED_COLUMNS` holds for its file's bytes, so a ruling
    reaches only the column it was made for, and only while that column is
    empty.
    """
    spellings = [name for name in SYMBOL_NAMES if name in held]
    if len(spellings) != 1:
        held_or_not = "both" if spellings else "neither"
        raise ValueError(
            f"the file carries {held_or_not} of {' and '.join(SYMBOL_NAMES)}, so it names "
            f"no single list of symbols"
        )
    named = unnamed or {}
    symbols = []
    for position, cell in enumerate(np.asarray(held[spellings[0]]).ravel(), start=1):
        if np.asarray(cell).size == 0 and position in named:
            symbols.append(named[position])
            continue
        if np.asarray(cell).size == 0 or not _symbol(cell):
            raise ValueError(f"column {position} has no name, and no ruling names it for this file")
        symbols.append(_symbol(cell))
    repeated = sorted({symbol for symbol in symbols if symbols.count(symbol) > 1})
    if repeated:
        raise ValueError(f"the file names a symbol more than once: {', '.join(repeated)}")
    return symbols


def _days_and_symbols(
    payload: bytes, names: list[str]
) -> tuple[dict[str, np.ndarray], list[str], list[str]]:
    """The file's arrays named ``names``, its trading days as ISO dates, and its symbols.

    Both readers here come through this, so a price file and a flag file cannot
    come to disagree on where a file keeps its symbols or on what makes a day
    list or a symbol list unreadable. It reads ``tday`` as one column of days.
    """
    wanted = ["tday", *names]
    held = scipy.io.loadmat(io.BytesIO(payload), variable_names=[*wanted, *SYMBOL_NAMES])
    missing = [name for name in wanted if name not in held]
    if missing:
        raise ValueError(f"the file carries no {', '.join(missing)}")
    symbols = symbols_of(held)

    days = [_iso_day(day) for day in np.asarray(held["tday"]).ravel()]
    if days != sorted(set(days)):
        raise ValueError("the file's trading days are not strictly increasing")
    return held, days, symbols


def read_arrays(payload: bytes) -> tuple[list[str], list[str], dict[str, np.ndarray]]:
    """The file's trading days as ISO dates, its symbols, and each field's array.

    The arrays are checked against the days and the symbols before anything is
    returned, because a mismatch here would put one stock's prices under
    another's name with every hash verifying.
    """
    held, days, symbols = _days_and_symbols(payload, list(ARRAYS.values()))
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
    that, measured on issue 88, and so do his later S&P 600 save, measured on
    issue 225, his book-two S&P 500 file, measured on issue 250, and his
    book-two ETF file, measured on issue 299. A file that does not is refused
    naming the first stock and day that break it.
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
    """Record every member of ``path`` as its own vintage, under :data:`VENDOR`.

    A file holding a day with no close in any column is refused before
    anything is written, for the reason :func:`_refuse_unpriced_days` gives.
    """
    payload = Path(path).read_bytes()
    days, symbols, arrays = read_arrays(payload)
    _refuse_unpriced_days(Path(path).name, days, arrays["Close"])
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
    although its bytes were right. Chan's book-two S&P 500 file was one, at 170
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
    held, days, symbols = _days_and_symbols(payload, ["earnann"])
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


#: The name Chan's strips give the spot column, which ``SYMBOL_PATTERN`` refuses.
SPOT_COLUMN = "0000$"

#: What the spot column is recorded as, after the root and a hyphen.
SPOT_SYMBOL = "SPOT"

#: A contract column's name, a delivery year and CME's letter for the month.
_CONTRACT = re.compile(r"^\d{4}[FGHJKMNQUVXZ]$")

#: A strip's root, the symbol between the file name's first two underscores.
_ROOT = re.compile(r"^inputData[A-Za-z]*_([A-Z][A-Z0-9]*)_")


def root_of(name: str) -> str:
    """The futures root a strip's file name carries, such as ``HO2``, or a refusal.

    Read off the name because the file holds no root of its own. Its contract
    columns name delivery months alone, and the gold file names nothing.
    """
    found = _ROOT.match(Path(name).stem)
    if found is None:
        raise ValueError(
            f"{name}: the name carries no root between its first two underscores, the way "
            f"inputDataDaily_CL_20120813.mat carries CL"
        )
    return found.group(1)


def read_strip(payload: bytes, root: str) -> tuple[list[str], list[str], np.ndarray]:
    """A strip's days as ISO dates, its symbols, and its date-by-symbol closes.

    Each contract column is named ``<root>-<contract>`` and the spot column
    ``<root>-SPOT``. A file with no ``contracts`` must hold one column, which
    is named ``<root>``. Any other column name is refused, because nothing
    says what an unrecognised column holds.
    """
    held = scipy.io.loadmat(io.BytesIO(payload), variable_names=["tday", "contracts", "cl"])
    missing = [name for name in ("tday", "cl") if name not in held]
    if missing:
        raise ValueError(f"the file carries no {', '.join(missing)}")

    days = [_iso_day(day) for day in np.asarray(held["tday"]).ravel()]
    if days != sorted(set(days)):
        raise ValueError("the file's trading days are not strictly increasing")
    closes = np.asarray(held["cl"], dtype=float)
    if "contracts" in held:
        symbols = []
        for name in (_symbol(cell) for cell in np.asarray(held["contracts"]).ravel()):
            if name == SPOT_COLUMN:
                symbols.append(f"{root}-{SPOT_SYMBOL}")
            elif _CONTRACT.match(name):
                symbols.append(f"{root}-{name}")
            else:
                raise ValueError(
                    f"the file names a column {name!r}, which is neither a contract such as "
                    f"2007F nor the spot column {SPOT_COLUMN}"
                )
        repeated = sorted({symbol for symbol in symbols if symbols.count(symbol) > 1})
        if repeated:
            raise ValueError(f"the file names a contract more than once: {', '.join(repeated)}")
    elif closes.ndim == 2 and closes.shape[1] == 1:
        symbols = [root]
    else:
        raise ValueError(
            f"the file names no contracts and its cl has {closes.shape[1]} columns, so "
            f"nothing says which series each one is"
        )
    if closes.shape != (len(days), len(symbols)):
        raise ValueError(
            f"cl is {closes.shape[0]} by {closes.shape[1]} and the file carries "
            f"{len(days)} days and {len(symbols)} columns"
        )
    return days, symbols, closes


def record_strip_file(
    path: Path, *, price_basis: str, data_dir: Path | None = None
) -> list[VintageEntry]:
    """Record every column of a strip as its own close-only vintage, under :data:`VENDOR`.

    A day a contract was not settled is a missing row, as it is for a stock.
    Some contracts stop and restart, and Chan's scripts read those holes when
    they find a contract's last day, so :func:`strip_round_trip_differs` is
    what says the panel gives them back.
    """
    payload = Path(path).read_bytes()
    days, symbols, closes = read_strip(payload, root_of(Path(path).name))
    _refuse_unpriced_days(Path(path).name, days, closes)
    columns = {
        symbol: [(days[day], float(closes[day, index])) for day in np.flatnonzero(priced)]
        for index, symbol in enumerate(symbols)
        for priced in [np.isfinite(closes[:, index])]
    }
    return record_lifted_columns(
        columns,
        vendor=VENDOR,
        price_basis=price_basis,
        saved_date=saved_date_of(payload),
        source_file=Path(path).name,
        data_dir=data_dir,
    )


def strip_round_trip_differs(path: Path, *, data_dir: Path | None = None) -> str | None:
    """Why the recorded strip is not the file's ``cl`` array, or ``None`` when it is.

    :func:`round_trip_differs` asks for five fields, and a strip's members
    carry the close alone, which :func:`chan.series.load_panel` refuses to
    read as anything else. So this rebuilds the one array and compares it
    exactly, days, column order and every NaN included.
    """
    from chan.series import load_panel

    payload = Path(path).read_bytes()
    days, symbols, closes = read_strip(payload, root_of(Path(path).name))
    _, panel = load_panel(Path(path).name, data_dir=data_dir)
    if [str(day.date()) for day in panel.index] != days:
        return "the panel's days are not the file's trading days"
    if list(panel.columns) != sorted(symbols):
        return "the panel's symbols are not the file's"
    order = [symbols.index(symbol) for symbol in panel.columns]
    if not np.array_equal(panel.to_numpy(dtype=float), closes[:, order], equal_nan=True):
        return "the panel's closes are not the file's cl array"
    return None


def read_continuous(payload: bytes) -> tuple[list[str], list[list[str]], dict[str, np.ndarray]]:
    """A continuous futures save's symbols, each symbol's own days, and each field's array.

    Chan's ``inputDataOHLCDaily_2012*.mat`` saves differ from a stock file in
    two ways.

    1. The symbol list is ``syms`` rather than ``stocks``, which Chan's ETF
       file shares.
    2. ``tday`` is a date-by-symbol array, so each column of a field is priced
       on its own calendar. Row 100 of CL and row 100 of FSTX are different
       days.

    A member's days are the rows its close is priced on. Three things are held
    before anything is returned, because each would put a price on the wrong
    day with every hash verifying.

    1. ``tday`` holds a date on exactly the rows the close is priced, so every
       priced row has a day and no day goes without its price.
    2. The unpriced rows are leading. Chan's scripts step through a column by
       row, so a gap in the middle would make the row before a price something
       other than the day before it, and dropping the gap would hide that.
    3. Each column's days strictly increase.

    How far apart two adjacent days are is not checked. ZB, ZF and ZN step
    from 1998-03-10 to 2008-04 between adjacent rows in three of the four
    saves, and ``data/README.md`` says so where it describes them.

    The symbols come through :func:`symbols_of`, so a column with an empty name
    is recorded under :data:`UNNAMED_COLUMNS` when the owner has named it for
    these bytes, and refused otherwise.
    """
    wanted = ["tday", *ARRAYS.values()]
    held = scipy.io.loadmat(io.BytesIO(payload), variable_names=[*wanted, *SYMBOL_NAMES])
    missing = [name for name in wanted if name not in held]
    if missing:
        raise ValueError(f"the file carries no {', '.join(missing)}")
    symbols = symbols_of(held, unnamed=UNNAMED_COLUMNS.get(hashlib.sha256(payload).hexdigest()))

    tday = np.asarray(held["tday"], dtype=float)
    arrays = {}
    for field, name in {"Day": "tday", **ARRAYS}.items():
        array = tday if field == "Day" else np.asarray(held[name], dtype=float)
        if array.ndim != 2 or array.shape[1] != len(symbols):
            raise ValueError(
                f"{name} is {' by '.join(map(str, array.shape))} and the file carries "
                f"{len(symbols)} symbols"
            )
        if array.shape != tday.shape:
            raise ValueError(f"{name} is not the shape of tday, {tday.shape[0]} by {len(symbols)}")
        if field != "Day":
            arrays[field] = array

    days = []
    for index, symbol in enumerate(symbols):
        priced = np.isfinite(arrays["Close"][:, index])
        dated = np.isfinite(tday[:, index])
        if not np.array_equal(dated, priced):
            row = int(np.flatnonzero(dated != priced)[0])
            raise ValueError(
                f"{symbol}'s tday and close disagree on whether row {row + 1} was priced"
            )
        rows = np.flatnonzero(priced)
        if rows.size and rows[-1] - rows[0] + 1 != rows.size:
            raise ValueError(
                f"{symbol} is unpriced on a row after its first price, so dropping that row "
                f"would move the rows after it"
            )
        if rows.size and rows[-1] != len(priced) - 1:
            raise ValueError(
                f"{symbol} is unpriced on the file's last row, and only leading rows are dropped"
            )
        column = [_iso_day(day) for day in tday[rows, index]]
        if column != sorted(set(column)):
            raise ValueError(f"{symbol}'s trading days are not strictly increasing")
        days.append(column)
    return symbols, days, arrays


def continuous_columns_of(
    symbols: list[str], days: list[list[str]], arrays: dict[str, np.ndarray]
) -> dict[str, list[tuple]]:
    """Each symbol's rows on its own days, carrying every field.

    The same rule :func:`columns_of` holds a stock to, every field priced on
    exactly the days the close is, applied one column at a time, since no two
    columns here share a calendar.
    """
    columns = {}
    for index, symbol in enumerate(symbols):
        rows = np.flatnonzero(np.isfinite(arrays["Close"][:, index]))
        single = {field: arrays[field][rows][:, [index]] for field in LIFTED_FIELDS}
        columns.update(columns_of(days[index], [symbol], single))
    return columns


def record_continuous_file(
    path: Path, *, price_basis: str, data_dir: Path | None = None
) -> list[VintageEntry]:
    """Record every symbol in a continuous futures save as its own vintage, under :data:`VENDOR`."""
    payload = Path(path).read_bytes()
    symbols, days, arrays = read_continuous(payload)
    return record_lifted_columns(
        continuous_columns_of(symbols, days, arrays),
        vendor=VENDOR,
        price_basis=price_basis,
        saved_date=saved_date_of(payload),
        source_file=Path(path).name,
        fields=LIFTED_FIELDS,
        data_dir=data_dir,
    )


def continuous_round_trip_differs(path: Path, *, data_dir: Path | None = None) -> str | None:
    """Why the recorded members are not the file's columns, or ``None`` when they are.

    Compared member by member rather than as one frame.
    :func:`chan.series.load_panel` rebuilds a source on the union of its
    members' dates, which is the file's layout for a stock file and not for
    this one. So each member's own rows, ``load_panel(source)[symbol].dropna()``,
    are held to its column's priced rows: the days, then every field, exactly.
    """
    from chan.series import load_panel

    payload = Path(path).read_bytes()
    symbols, days, arrays = read_continuous(payload)
    spelled = [symbol.upper() for symbol in symbols]
    for field in LIFTED_FIELDS:
        _, panel = load_panel(Path(path).name, field=field, data_dir=data_dir)
        if sorted(panel.columns) != sorted(spelled):
            return "the panel's symbols are not the file's"
        for index, symbol in enumerate(spelled):
            member = panel[symbol].dropna()
            if [str(day.date()) for day in member.index] != days[index]:
                return f"{symbol}'s days are not its tday column's priced rows"
            column = arrays[field][:, index]
            if not np.array_equal(member.to_numpy(dtype=float), column[np.isfinite(column)]):
                return f"{symbol}'s {field} is not the file's {ARRAYS[field]} column"
    return None


#: A number as Chan's CSV files write one. ``float`` alone would also take
#: ``1_0``, padding, ``nan`` and ``inf``, none of which a vendor's file means.
_DECIMAL = re.compile(r"^-?\d+(\.\d+)?$")

#: The header Chan's ``VIX.csv`` opens with, which is Yahoo's daily download.
CSV_HEADER = ["Date", "Open", "High", "Low", "Close", "Volume", "Adj Close"]


def read_csv_rows(payload: bytes) -> list[tuple]:
    """The rows of one of Chan's daily CSV files, in :data:`LIFTED_FIELDS` order.

    The header must be :data:`CSV_HEADER`. Its ``Adj Close`` is not written,
    so it must equal ``Close`` on every row, and a file where it does not is
    refused, because dropping it would then lose a series. Every date must be
    ISO and strictly increasing.
    """
    lines = payload.decode("ascii").splitlines()
    if not lines:
        raise ValueError("the file is empty")
    header, body = lines[0].split(","), lines[1:]
    if header != CSV_HEADER:
        raise ValueError(f"the header is {','.join(header)} rather than {','.join(CSV_HEADER)}")
    rows = []
    for number, line in enumerate(body, start=2):
        cells = line.split(",")
        if len(cells) != len(CSV_HEADER):
            raise ValueError(f"line {number} holds {len(cells)} cells, not {len(CSV_HEADER)}")
        day, opened, high, low, close, volume, adjusted = cells
        unreadable = [cell for cell in cells[1:] if not _DECIMAL.match(cell)]
        if unreadable:
            raise ValueError(f"line {number} holds {unreadable[0]!r}, which is not a plain decimal")
        if float(adjusted) != float(close):
            raise ValueError(
                f"the Adj Close on {day} is {adjusted} and the Close {close}, so leaving the "
                f"Adj Close out would lose a series"
            )
        rows.append((day, float(close), float(high), float(low), float(opened), float(volume)))
    days = [row[0] for row in rows]
    if days != sorted(set(days)):
        raise ValueError("the file's dates are not strictly increasing")
    return rows


def record_csv_file(
    path: Path, *, price_basis: str, saved_date: str, data_dir: Path | None = None
) -> list[VintageEntry]:
    """Record one of Chan's CSV files as one vintage, under :data:`CSV_VENDOR`.

    The symbol is the file's stem in capitals, so ``VIX.csv`` is ``VIX``. The
    saved date is the caller's to state, because a CSV carries no header that
    records one, and reading a filesystem's time would record whenever the
    local copy was made.
    """
    payload = Path(path).read_bytes()
    return record_lifted_columns(
        {Path(path).stem.upper(): read_csv_rows(payload)},
        vendor=CSV_VENDOR,
        price_basis=price_basis,
        saved_date=saved_date,
        source_file=Path(path).name,
        fields=LIFTED_FIELDS,
        data_dir=data_dir,
    )


def csv_round_trip_differs(path: Path, *, data_dir: Path | None = None) -> str | None:
    """Why the recorded vintage is not the CSV's rows, or ``None`` when it is."""
    from chan.series import load_panel

    rows = read_csv_rows(Path(path).read_bytes())
    symbol = Path(path).stem.upper()
    for position, field in enumerate(LIFTED_FIELDS, start=1):
        _, panel = load_panel(Path(path).name, field=field, data_dir=data_dir)
        if list(panel.columns) != [symbol]:
            return f"the panel holds {', '.join(panel.columns)} rather than {symbol}"
        if [str(day.date()) for day in panel.index] != [row[0] for row in rows]:
            return "the vintage's days are not the file's"
        if not np.array_equal(panel[symbol].to_numpy(dtype=float), [row[position] for row in rows]):
            return f"the vintage's {field} is not the file's"
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m chan.mat_columns",
        description="Record one of Chan's .mat or .csv files as one vintage per column.",
    )
    parser.add_argument("path", type=Path, help="a local copy of the .mat or .csv file")
    # Every basis but ``return``, which no writer records.
    choices = [basis for basis in PRICE_BASES if basis != "return"]
    parser.add_argument("--price-basis", required=True, choices=choices)
    parser.add_argument(
        "--saved-date",
        help="when Chan saved a .csv, which carries no header recording it. Refused for a .mat.",
    )
    arguments = parser.parse_args(argv)

    payload = arguments.path.read_bytes()
    sha256 = hashlib.sha256(payload).hexdigest()
    basis = arguments.price_basis
    try:
        csv = arguments.path.suffix.lower() == ".csv"
        if csv != (arguments.saved_date is not None):
            raise ValueError(
                "a .csv carries no saved date, so it needs --saved-date"
                if csv
                else "the MAT header records the saved date, so --saved-date is not taken"
            )
        shape = "csv" if csv else shape_of(payload)
        if shape == "flags":
            if basis != "event":
                raise ValueError(
                    f"the file carries earnann, which is recorded under the event basis "
                    f"rather than {basis}"
                )
            entries = record_flag_file(arguments.path)
        elif basis == "event":
            raise ValueError("the file carries no earnann")
        elif shape == "stocks":
            entries = record_mat_file(arguments.path, price_basis=basis)
        elif shape == "continuous":
            entries = record_continuous_file(arguments.path, price_basis=basis)
        elif shape == "csv":
            entries = record_csv_file(
                arguments.path, price_basis=basis, saved_date=arguments.saved_date
            )
        elif basis != "raw":
            raise ValueError(
                f"the file is a futures strip, whose settlements are recorded under the raw "
                f"basis rather than {basis}"
            )
        else:
            entries = record_strip_file(arguments.path, price_basis=basis)
    except (VintageRefused, ValueError) as refused:
        print(f"{arguments.path.name}: not recorded. {refused}", file=sys.stderr)
        return 1

    rows = sum(entry.row_count for entry in entries)
    fields = {
        "flags": EVENT_FIELDS,
        "stocks": LIFTED_FIELDS,
        "strip": ("Close",),
        "continuous": LIFTED_FIELDS,
        "csv": LIFTED_FIELDS,
    }[shape]
    print(f"{arguments.path.name}   sha256 {sha256}")
    print(
        f"recorded {len(entries)} vintages, {rows} rows of {', '.join(fields)}, under "
        f"{entries[0].path.split('/')[0]}/, saved {entries[0].saved_date}"
    )
    check = {
        "flags": flag_round_trip_differs,
        "stocks": round_trip_differs,
        "strip": strip_round_trip_differs,
        "continuous": continuous_round_trip_differs,
        "csv": csv_round_trip_differs,
    }[shape]
    differs = check(arguments.path)
    if differs is not None:
        print(
            f"round trip failed: {differs}. The vintages are recorded, so review them before "
            f"committing, or take them back out with `git checkout -- data/` and by removing "
            f"{entries[0].path.split('/')[0]}/.",
            file=sys.stderr,
        )
        return 1
    if shape == "flags":
        print("round trip: every flag read back is the file's array, day for day")
    elif shape == "strip":
        print("round trip: every close read back is the file's cl array, NaN for NaN")
    elif shape == "continuous":
        print("round trip: every member read back is its column's priced rows, every field")
    elif shape == "csv":
        print("round trip: every field read back is the file's, row for row")
    else:
        print("round trip: every field read back is the file's array, NaN for NaN")
    return 0


def shape_of(payload: bytes) -> str:
    """Which reader a ``.mat`` needs, ``flags``, ``stocks``, ``strip`` or ``continuous``.

    Read off the variables rather than off the basis the caller states,
    because a strip and a stock file both take a price basis, and before the
    strips arrived a strip handed to the command reached the stock reader and
    was refused for carrying no ``stocks``.

    A strip is a file carrying ``contracts``, or a file naming no columns and
    holding no price array but ``cl``, which is the gold file's shape. Anything
    else takes the stock path, so a stock file with its symbol list misspelled
    is refused for carrying neither ``stocks`` nor ``syms`` rather than read as
    one series. A file naming its columns ``syms`` takes the stock path too, and
    :func:`read_arrays` reads it. Chan's ETF file is one, and
    [issue 299](https://github.com/l3a0/quantitative-trading/issues/299) is
    what taught the stock reader that spelling.

    A file whose ``tday`` has more than one row and more than one column is a
    continuous futures save, where every symbol keeps its own calendar, and
    :func:`read_continuous` reads it.
    [Issue 313](https://github.com/l3a0/quantitative-trading/issues/313) added
    that case.
    """
    shapes = {name: shape for name, shape, _ in scipy.io.whosmat(io.BytesIO(payload))}
    if "earnann" in shapes:
        return "flags"
    if "contracts" in shapes:
        return "strip"
    if "tday" in shapes and len(shapes["tday"]) == 2 and min(shapes["tday"]) > 1:
        return "continuous"
    if not set(shapes) & ({"stocks", "syms", *ARRAYS.values()} - {ARRAYS["Close"]}):
        return "strip"
    return "stocks"


def _refuse_unpriced_days(name: str, days: list[str], closes: np.ndarray) -> None:
    """Refuse a file holding a day on which no column has a close.

    The panel rebuilds a file's days from the union of its members' dates, so
    such a day would vanish from it, and a round trip would only say so once
    every member had been recorded.
    """
    unpriced = [day for day, row in zip(days, closes, strict=True) if not np.isfinite(row).any()]
    if unpriced:
        raise ValueError(
            f"{name} prices no column on {', '.join(unpriced)}, so the per-column "
            f"files could not give that day back"
        )


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
