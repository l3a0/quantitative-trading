"""Which manifest entries no recorder wrote, and what their identity is.

That covers two sets. :data:`HAND_WRITTEN` is the lines typed by hand, and
:data:`LIFTED_SOURCES` is the sources whose columns ``record_lifted_columns``
wrote, one vintage per column. Several test modules need the same answer to one
question, so it is written once here. ``tests/test_vintage.py`` holds the
hand-written entries to their pinned identity, and ``tests/test_series.py``
counts the reader's map against the same set. Spelling it twice would let a new
vintage satisfy one file and not the other, and nothing would say which
spelling was right.

Hand-written means no code wrote the manifest line. That is the whole reason
the set needs naming. A hand-written line has no generator to check it against,
while a recorded one does, and the two therefore need different assertions
rather than one applied to both.

The set was called ``BACKFILLED`` until
[issue 124](https://github.com/l3a0/quantitative-trading/issues/124), when
``spy_chan.csv`` joined it. Backfilled meant committed before
:mod:`chan.vintage` existed, which was true of all eight then and is false of
the ninth. Nothing else about the set moved, because the two are the same
question for everything that predates the recorder, and they part only on a
line typed after it. :func:`chan.vintage.record_vintage` takes a download date
and builds a name out of it, so a single column lifted from one of Chan's
workbooks, which carries a saved date and no download date, cannot be recorded
and still arrives by hand. A whole source of them is written by
``record_lifted_columns`` instead and pinned in :data:`LIFTED_SOURCES`.

Seven fields are pinned, keyed by the path that names the file. Five are the
identity, meaning what a reader is looking at, and four of those are
confirmable from nothing at all: a hash says the bytes did not move and says
nothing about which vendor sent them, on what day, or which price they carry.
The symbol is the exception, and only for this set, because each of its files
carries the ``Ticker,`` header row.

That header is a property of the members rather than of the key, and the two
are worth telling apart. "Backfilled" entailed it, because every file that
predates the recorder carries yfinance's frame. "Hand-written" does not, so a
hand-placed file written as a bare ``Date,Close`` would join this set and reach
``the_hand_written_entries_name_their_series`` with no header row to read. What
stops that today is convention rather than a check: every file here is written
in the three-row shape, which ``data/README.md``'s ``## Header shape`` states,
and the next one is expected to be.

The sixth is ``source_workbook``, which says where the bytes came from rather
than what they are. It is pinned with the identity because it is hand-typed on
both surfaces that state it, so the two agreeing says nothing about either
being right.

The seventh is ``vendor_column``, which says which column of the vendor's
response the bytes are. It is pinned for the same reason, and because for
``gld_20yr_prices.csv`` and ``gdx_20yr_prices.csv`` it was typed from a
measurement rather than from a call anyone wrote down, which
``TestWhichColumnTheHandPlacedAdjustedVintagesHold`` in
``tests/test_scale_breaks.py`` is what backs. Every other entry here pins ``None``,
so the field turning up on a workbook column fails here too.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from chan.paths import DATA_DIR
from chan.vintage import MANIFEST_NAME, VintageEntry

#: Path to ``(vendor, symbol, price_basis, download_date, saved_date,
#: source_workbook, vendor_column)``.
#:
#: The ``*_chan.csv`` entries carry a saved date and no download date,
#: because they are columns lifted from Ernest Chan's workbooks and nothing
#: was fetched on that day. They carry the workbook for the same reason, and
#: it is pinned here rather than left to the table alone because both surfaces
#: stating it are hand-typed. A hand edit that moves the manifest and
#: ``data/README.md`` together agrees with itself, so the check comparing the
#: two passes and only a pin fails it.
HAND_WRITTEN = {
    "gld_20yr_prices.csv": (
        "yfinance",
        "GLD",
        "adjusted",
        "2026-06-16",
        None,
        None,
        "Close, auto_adjust=True",
    ),
    "gld_20yr_prices_unadjusted.csv": ("yfinance", "GLD", "raw", "2026-08-27", None, None, None),
    "gdx_20yr_prices.csv": (
        "yfinance",
        "GDX",
        "adjusted",
        "2026-08-27",
        None,
        None,
        "Close, auto_adjust=True",
    ),
    "gdx_20yr_prices_unadjusted.csv": ("yfinance", "GDX", "raw", "2026-08-27", None, None, None),
    "gld_chan.csv": ("chan-xls", "GLD", "adjusted", None, "2007-12-02", "GLD.xls", None),
    "gdx_chan.csv": ("chan-xls", "GDX", "adjusted", None, "2007-12-02", "GDX.xls", None),
    "ko_chan.csv": ("chan-xls", "KO", "adjusted", None, "2008-01-23", "KO.xls", None),
    "pep_chan.csv": ("chan-xls", "PEP", "adjusted", None, "2008-01-23", "PEP.xls", None),
    "spy_chan.csv": ("chan-xls", "SPY", "adjusted", None, "2008-01-29", "example6_2.xls", None),
    "spy_unadjusted_chan.csv": (
        "chan-xls",
        "SPY",
        "raw",
        None,
        "2008-01-29",
        "example6_2.xls",
        None,
    ),
}


#: Each source lifted as one vintage per column, to what every one of its members carries.
#:
#: Source file to ``(vendor, price_basis, saved_date, directory, members)``.
#: [Issue 88](https://github.com/l3a0/quantitative-trading/issues/88) recorded
#: Chan's two ``.mat`` files this way, 1,100 columns between them, and pinning
#: each column by path would be 1,100 hand-typed tuples saying the same four
#: things. [Issue 250](https://github.com/l3a0/quantitative-trading/issues/250)
#: added Chan's two book-two files, his 2012 S&P 500 prices and the earnings
#: flags for the same 497 stocks under the ``event`` basis.
#: [Issue 225](https://github.com/l3a0/quantitative-trading/issues/225) added
#: ``IJR_20080131.mat``, a later save of the S&P 600 file holding the same 600
#: symbols. [Issue 299](https://github.com/l3a0/quantitative-trading/issues/299)
#: added ``inputData_ETF.mat``, Chan's book-two file of 67 ETFs, which names its
#: symbol list ``syms`` rather than ``stocks``. One source was saved once, so
#: its members share a vendor, a basis and a date, and the pin says each once.
#: The member count is what notices a column dropped from the manifest along
#: with its file.
#:
#: The symbol is not pinned, for the reason the ``Ticker,`` paragraph above
#: gives: each member's own bytes carry it, and a member's path is its
#: directory and its symbol lowercased.
#:
#: It sits beside :data:`HAND_WRITTEN` rather than inside it. That map is
#: keyed by path, and ``tests/test_series.py`` compares its keys against the
#: manifest's paths.
LIFTED_SOURCES = {
    "SPX_20071123.mat": ("chan-mat", "adjusted", "2007-11-24", "spx_20071123", 500),
    "IJR_20080114.mat": ("chan-mat", "adjusted", "2008-01-15", "ijr_20080114", 600),
    "IJR_20080131.mat": ("chan-mat", "adjusted", "2008-02-02", "ijr_20080131", 600),
    "inputDataOHLCDaily_stocks_20120424.mat": (
        "chan-mat",
        "adjusted",
        "2012-04-25",
        "inputdataohlcdaily_stocks_20120424",
        497,
    ),
    "earnannFile.mat": ("chan-mat", "event", "2012-05-15", "earnannfile", 497),
    "inputData_ETF.mat": ("chan-mat", "adjusted", "2012-04-10", "inputdata_etf", 67),
}


def in_a_lifted_source(path: str) -> bool:
    """Whether ``path`` sits in the directory of a source :data:`LIFTED_SOURCES` pins.

    Read off the path rather than off ``source_workbook``, because two of the
    checks that use it hold that field and the date fields to the path, and a
    predicate reading the field under test would agree with any edit to it.
    """
    directory, _, name = path.rpartition("/")
    return bool(name) and directory in {pin[3] for pin in LIFTED_SOURCES.values()}


def identity_of(
    entry: VintageEntry,
) -> tuple[str, str, str, str | None, str | None, str | None, str | None]:
    """The seven fields :data:`HAND_WRITTEN` pins, read off an entry.

    Written here rather than at each call site so the tuple's order is decided
    once. A pin compared against a tuple assembled in a different order fails
    on fields that agree.

    Five of the seven say what a reader is looking at. ``source_workbook`` and
    ``vendor_column`` say where the bytes came from instead, and they are
    pinned beside them because nothing else in the tree fails a hand edit to
    either. Most of the ``.xls``
    names here happen to be their columns' symbols, which is what
    [issue 152](https://github.com/l3a0/quantitative-trading/issues/152) stopped
    deriving. Reading them off a list rather than joining them is the point, and
    ``spy_chan.csv`` is why: its column comes from ``example6_2.xls``, while a
    real ``SPY.xls`` in the same mirror holds a different series.
    """
    return (
        entry.vendor,
        entry.symbol,
        entry.price_basis,
        entry.download_date,
        entry.saved_date,
        entry.source_workbook,
        entry.vendor_column,
    )


def rewrite_entry(directory: Path, named: str, **changes) -> None:
    """Hand-edit one manifest line, which is the act these assertions exist to catch.

    Written through JSON rather than a string replacement, so an edit changes
    the field it names and leaves the line's shape alone. A hand edit that also
    broke a line's shape is caught by a different assertion answering a
    different question, the one that reads each committed line back through
    :meth:`VintageEntry.as_json`.

    The line is selected by ``named`` rather than by a parameter called
    ``path``, so ``path`` stays available as a field to change. A caller
    repointing an entry at another file is one of the states these assertions
    have to be driven through, and the obvious spelling collided.

    An edit that matches no line raises rather than passing. Every negative
    case here asserts that some check fails afterwards, so a mistyped name
    would report that nothing raised instead of that nothing was edited.
    """
    manifest = directory / MANIFEST_NAME
    lines, edited = [], False
    for line in manifest.read_text(encoding="utf-8").splitlines():
        fields = json.loads(line)
        if fields["path"] == named:
            fields.update(changes)
            edited = True
        lines.append(json.dumps(fields, sort_keys=True))
    assert edited, named
    manifest.write_text("".join(line + "\n" for line in lines), encoding="utf-8")


def committed_copy(tmp_path: Path) -> Path:
    """The committed vintages, copied, so a case may record into them or break one.

    Both test modules need this and both wrote it out, down to the directory
    name. One copy of it here for the same reason :data:`HAND_WRITTEN` is here:
    a helper spelled twice is a helper that can come to differ.
    """
    directory = tmp_path / "committed"
    shutil.copytree(DATA_DIR, directory)
    return directory
