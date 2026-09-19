"""Which manifest entries were typed by hand, and what their identity is.

Two test modules need the same answer to one question, so it is written once
here. ``tests/test_vintage.py`` holds the hand-written entries to their pinned
identity, and ``tests/test_series.py`` counts the reader's map against the same
set. Spelling it twice would let a new vintage satisfy one file and not the
other, and nothing would say which spelling was right.

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
and builds a name out of it, so a column lifted from one of Chan's workbooks,
which carries a saved date and no download date, cannot be recorded at all and
still arrives by hand.

Six fields are pinned, keyed by the path that names the file. Five are the
identity, meaning what a reader is looking at, and four of those are
confirmable from nothing at all: a hash says the bytes did not move and says
nothing about which vendor sent them, on what day, or which price they carry.
The symbol is the exception, and only for this set, because each of its files
carries the ``Ticker,`` header row.

The sixth is ``source_workbook``, which says where the bytes came from rather
than what they are. It is pinned with the identity because it is hand-typed on
both surfaces that state it, so the two agreeing says nothing about either
being right.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from chan.paths import DATA_DIR
from chan.vintage import MANIFEST_NAME, VintageEntry

#: Path to ``(vendor, symbol, price_basis, download_date, saved_date,
#: source_workbook)``.
#:
#: The five ``*_chan.csv`` entries carry a saved date and no download date,
#: because they are columns lifted from Ernest Chan's workbooks and nothing
#: was fetched on that day. They carry the workbook for the same reason, and
#: it is pinned here rather than left to the table alone because both surfaces
#: stating it are hand-typed. A hand edit that moves the manifest and
#: ``data/README.md`` together agrees with itself, so the check comparing the
#: two passes and only a pin fails it.
HAND_WRITTEN = {
    "gld_20yr_prices.csv": ("yfinance", "GLD", "adjusted", "2026-06-16", None, None),
    "gld_20yr_prices_unadjusted.csv": ("yfinance", "GLD", "raw", "2026-08-27", None, None),
    "gdx_20yr_prices.csv": ("yfinance", "GDX", "adjusted", "2026-08-27", None, None),
    "gdx_20yr_prices_unadjusted.csv": ("yfinance", "GDX", "raw", "2026-08-27", None, None),
    "gld_chan.csv": ("chan-xls", "GLD", "adjusted", None, "2007-12-02", "GLD.xls"),
    "gdx_chan.csv": ("chan-xls", "GDX", "adjusted", None, "2007-12-02", "GDX.xls"),
    "ko_chan.csv": ("chan-xls", "KO", "adjusted", None, "2008-01-23", "KO.xls"),
    "pep_chan.csv": ("chan-xls", "PEP", "adjusted", None, "2008-01-23", "PEP.xls"),
    "spy_chan.csv": ("chan-xls", "SPY", "adjusted", None, "2008-01-29", "example6_2.xls"),
}


def identity_of(
    entry: VintageEntry,
) -> tuple[str, str, str, str | None, str | None, str | None]:
    """The six fields :data:`HAND_WRITTEN` pins, read off an entry.

    Written here rather than at each call site so the tuple's order is decided
    once. A pin compared against a tuple assembled in a different order fails
    on fields that agree.

    Five of the six say what a reader is looking at. ``source_workbook`` says
    where the bytes came from instead, and it is pinned beside them because
    nothing else in the tree fails a hand edit to it. Four of the five ``.xls``
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
