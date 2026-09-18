"""Which manifest entries predate the recorder, and what their identity is.

Two test modules need the same answer to one question, so it is written once
here. ``tests/test_vintage.py`` holds the eight backfilled entries to their
pinned identity, and ``tests/test_series.py`` counts the reader's map against
the same eight. Spelling the set twice would let a ninth vintage satisfy one
file and not the other, and nothing would say which spelling was right.

The eight are backfilled in the sense that they were committed before
:mod:`chan.vintage` existed, so no code wrote them and their manifest lines
were typed by hand. That is the whole reason they need naming. A hand-written
line has no generator to check it against, while a recorded one does, and the
two therefore need different assertions rather than one applied to both.

The identity here is the five fields that say what a reader is looking at,
keyed by the path that names the file. Four of them are confirmable from
nothing at all: a hash says the bytes did not move and says nothing about
which vendor sent them, on what day, or which price they carry. The symbol is
the exception, and only for these eight, because each carries yfinance's
``Ticker,`` header row.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from chan.paths import DATA_DIR
from chan.vintage import MANIFEST_NAME, VintageEntry

#: Path to ``(vendor, symbol, price_basis, download_date, saved_date)``.
#:
#: The four ``*_chan.csv`` entries carry a saved date and no download date,
#: because they are columns lifted from Ernest Chan's workbooks and nothing
#: was fetched on that day.
BACKFILLED = {
    "gld_20yr_prices.csv": ("yfinance", "GLD", "adjusted", "2026-06-16", None),
    "gld_20yr_prices_unadjusted.csv": ("yfinance", "GLD", "raw", "2026-08-27", None),
    "gdx_20yr_prices.csv": ("yfinance", "GDX", "adjusted", "2026-08-27", None),
    "gdx_20yr_prices_unadjusted.csv": ("yfinance", "GDX", "raw", "2026-08-27", None),
    "gld_chan.csv": ("chan-xls", "GLD", "adjusted", None, "2007-12-02"),
    "gdx_chan.csv": ("chan-xls", "GDX", "adjusted", None, "2007-12-02"),
    "ko_chan.csv": ("chan-xls", "KO", "adjusted", None, "2008-01-23"),
    "pep_chan.csv": ("chan-xls", "PEP", "adjusted", None, "2008-01-23"),
}


def identity_of(entry: VintageEntry) -> tuple[str, str, str, str | None, str | None]:
    """The five fields :data:`BACKFILLED` pins, read off an entry.

    Written here rather than at each call site so the tuple's order is decided
    once. A pin compared against a tuple assembled in a different order fails
    on fields that agree.
    """
    return (
        entry.vendor,
        entry.symbol,
        entry.price_basis,
        entry.download_date,
        entry.saved_date,
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
    name. One copy of it here for the same reason :data:`BACKFILLED` is here:
    a helper spelled twice is a helper that can come to differ.
    """
    directory = tmp_path / "committed"
    shutil.copytree(DATA_DIR, directory)
    return directory
